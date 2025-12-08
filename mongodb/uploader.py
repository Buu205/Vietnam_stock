"""Main upload script for financial metrics to MongoDB."""

import os
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from pymongo.collection import Collection
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne

from .config import get_database
from .utils import (
    parquet_to_dict_list,
    create_unique_index,
    validate_collection_name,
    add_metadata_to_record
)

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Collection mappings: collection_name -> parquet_file_path
COLLECTION_MAPPINGS = {
    'company_metrics': 'calculated_results/fundamental/company/company_financial_metrics.parquet',
    'bank_metrics': 'calculated_results/fundamental/bank/bank_financial_metrics.parquet',
    'insurance_metrics': 'calculated_results/fundamental/insurance/insurance_financial_metrics.parquet',
    'security_metrics': 'calculated_results/fundamental/security/security_financial_metrics.parquet',
    # Valuation collections
    'valuation_pe': 'calculated_results/valuation/pe/pe_historical_all_symbols_final.parquet',
    'valuation_pb': 'calculated_results/valuation/pb/pb_historical_all_symbols_final.parquet',
    'valuation_evebitda': 'calculated_results/valuation/ev_ebitda/ev_ebitda_historical_all_symbols_final.parquet',
    'vnindex_pe': 'calculated_results/valuation/vnindex_pe_historical_final.parquet',
    'sector_pe': 'calculated_results/valuation/sector_pe/sector_pe_historical_final.parquet',
}

# Unique index fields for each collection
UNIQUE_INDEX_FIELDS = {
    'company_metrics': ['symbol', 'report_date', 'year', 'quarter'],
    'bank_metrics': ['symbol', 'report_date', 'year', 'quarter'],
    'insurance_metrics': ['symbol', 'report_date', 'year', 'quarter'],
    'security_metrics': ['symbol', 'report_date', 'year', 'quarter'],
    'valuation_pe': ['symbol', 'date'],
    'valuation_pb': ['symbol', 'date'],
    'valuation_evebitda': ['symbol', 'date'],
    'vnindex_pe': ['date'],
    'sector_pe': ['sector', 'date'],
}


def upload_parquet_to_mongodb(
    parquet_path: str,
    collection_name: str,
    db_name: Optional[str] = None,
    batch_size: int = 1000,
    upsert: bool = True,
    create_index: bool = True
) -> Dict[str, Any]:
    """
    Upload parquet file to MongoDB collection.
    
    Args:
        parquet_path: Path to parquet file (relative to project root or absolute)
        collection_name: MongoDB collection name
        db_name: Database name (optional, uses default from config)
        batch_size: Batch size for bulk operations
        upsert: If True, update existing documents, else insert only
        create_index: If True, create unique index on (symbol, report_date, year, quarter)
        
    Returns:
        Dict with upload statistics: {
            'inserted': int,
            'updated': int,
            'errors': int,
            'total': int
        }
        
    Note:
        - Uses upsert logic: update if exists, insert if not
        - Creates unique index on (symbol, report_date, year, quarter)
        - Handles bulk write operations with error handling
    """
    # Validate collection name
    if not validate_collection_name(collection_name):
        raise ValueError(f"Invalid collection name: {collection_name}")
    
    # Resolve parquet path
    if not os.path.isabs(parquet_path):
        project_root = Path(__file__).parent.parent
        parquet_path = project_root / parquet_path
    
    if not os.path.exists(parquet_path):
        raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
    
    logger.info(f"Uploading {parquet_path} to collection '{collection_name}'")
    
    # Get database and collection
    db = get_database(db_name)
    collection = db[collection_name]
    
    # Convert parquet to dict list
    records = parquet_to_dict_list(str(parquet_path))
    
    if not records:
        logger.warning(f"No records found in {parquet_path}")
        return {
            'inserted': 0,
            'updated': 0,
            'errors': 0,
            'total': 0
        }
    
    # Add metadata
    for record in records:
        add_metadata_to_record(record)
    
    # Create unique index if requested
    if create_index and collection_name in UNIQUE_INDEX_FIELDS:
        index_fields = UNIQUE_INDEX_FIELDS[collection_name]
        create_unique_index(collection, index_fields)
    
    # Prepare bulk operations
    stats = {
        'inserted': 0,
        'updated': 0,
        'errors': 0,
        'total': len(records)
    }
    
    # Process in batches
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        
        try:
            if upsert:
                # Upsert operations
                operations = []
                for record in batch:
                    # Build filter for unique fields
                    filter_dict = {
                        'symbol': record.get('symbol'),
                        'report_date': record.get('report_date'),
                        'year': record.get('year'),
                        'quarter': record.get('quarter')
                    }

                    # Remove None values from filter
                    filter_dict = {k: v for k, v in filter_dict.items() if v is not None}

                    # Use UpdateOne operation for upsert
                    operations.append(
                        UpdateOne(
                            filter_dict,
                            {'$set': record},
                            upsert=True
                        )
                    )
                
                result = collection.bulk_write(operations, ordered=False)
                stats['inserted'] += result.upserted_count
                stats['updated'] += result.modified_count
                
            else:
                # Insert only
                result = collection.insert_many(batch, ordered=False)
                stats['inserted'] += len(result.inserted_ids)
                
            logger.info(
                f"Processed batch {i//batch_size + 1}: "
                f"inserted={stats['inserted']}, updated={stats['updated']}"
            )
            
        except BulkWriteError as e:
            # Handle partial success
            stats['errors'] += len(e.details.get('writeErrors', []))
            stats['inserted'] += e.details.get('nInserted', 0)
            stats['updated'] += e.details.get('nModified', 0)
            logger.warning(f"Bulk write errors: {len(e.details.get('writeErrors', []))}")
            
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            stats['errors'] += len(batch)
    
    logger.info(
        f"Upload complete: {stats['inserted']} inserted, "
        f"{stats['updated']} updated, {stats['errors']} errors, "
        f"{stats['total']} total"
    )
    
    return stats


def upload_all_collections(
    db_name: Optional[str] = None,
    batch_size: int = 1000,
    upsert: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Upload all collections defined in COLLECTION_MAPPINGS.
    
    Args:
        db_name: Database name (optional)
        batch_size: Batch size for bulk operations
        upsert: If True, update existing documents
        
    Returns:
        Dict mapping collection_name -> upload statistics
    """
    results = {}
    
    for collection_name, parquet_path in COLLECTION_MAPPINGS.items():
        try:
            logger.info(f"Uploading {collection_name}...")
            stats = upload_parquet_to_mongodb(
                parquet_path=parquet_path,
                collection_name=collection_name,
                db_name=db_name,
                batch_size=batch_size,
                upsert=upsert
            )
            results[collection_name] = stats
            
        except Exception as e:
            logger.error(f"Failed to upload {collection_name}: {e}")
            results[collection_name] = {
                'error': str(e),
                'inserted': 0,
                'updated': 0,
                'errors': 0,
                'total': 0
            }
    
    return results


if __name__ == '__main__':
    """Main entry point for uploading data."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload financial metrics to MongoDB')
    parser.add_argument(
        '--collection',
        type=str,
        help='Collection name to upload (if not specified, uploads all)'
    )
    parser.add_argument(
        '--parquet',
        type=str,
        help='Path to parquet file (required if --collection specified)'
    )
    parser.add_argument(
        '--db',
        type=str,
        help='Database name (optional)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Batch size for bulk operations (default: 1000)'
    )
    parser.add_argument(
        '--no-upsert',
        action='store_true',
        help='Disable upsert (insert only)'
    )
    
    args = parser.parse_args()
    
    if args.collection:
        if not args.parquet:
            parser.error("--parquet is required when --collection is specified")
        
        stats = upload_parquet_to_mongodb(
            parquet_path=args.parquet,
            collection_name=args.collection,
            db_name=args.db,
            batch_size=args.batch_size,
            upsert=not args.no_upsert
        )
        print(f"Upload statistics: {stats}")
    else:
        results = upload_all_collections(
            db_name=args.db,
            batch_size=args.batch_size,
            upsert=not args.no_upsert
        )
        print("Upload results:")
        for collection, stats in results.items():
            print(f"  {collection}: {stats}")

