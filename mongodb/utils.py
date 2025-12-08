"""Helper functions for MongoDB operations."""

import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pymongo.collection import Collection
from pymongo.errors import OperationFailure

logger = logging.getLogger(__name__)


def parquet_to_dict_list(
    parquet_path: str,
    symbol_col: str = 'symbol',
    report_date_col: str = 'report_date',
    year_col: str = 'year',
    quarter_col: str = 'quarter'
) -> List[Dict[str, Any]]:
    """
    Convert parquet file to list of dictionaries for MongoDB insertion.
    
    Args:
        parquet_path: Path to parquet file
        symbol_col: Column name for symbol (default: 'symbol')
        report_date_col: Column name for report_date (default: 'report_date')
        year_col: Column name for year (default: 'year')
        quarter_col: Column name for quarter (default: 'quarter')
        
    Returns:
        List of dictionaries ready for MongoDB insertion
        
    Note:
        - Converts pandas DataFrame to dict records
        - Handles NaN values (converts to None)
        - Normalizes symbol to uppercase and strips whitespace
        - Converts date columns to ISO format strings
    """
    try:
        df = pd.read_parquet(parquet_path)
        logger.info(f"Loaded {len(df)} records from {parquet_path}")
        
        # Normalize symbol column if exists
        if symbol_col in df.columns:
            df[symbol_col] = df[symbol_col].str.upper().str.strip()
        
        # Convert date columns to ISO format strings
        date_columns = [report_date_col] if report_date_col in df.columns else []
        for col in date_columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d')
            elif pd.api.types.is_object_dtype(df[col]):
                # Try to parse if string
                try:
                    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
                except:
                    pass
        
        # Convert to dict list
        records = df.replace({pd.NA: None, pd.NaT: None}).to_dict('records')
        
        # Convert NaN to None
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
        
        logger.info(f"Converted {len(records)} records to dict format")
        return records
        
    except Exception as e:
        logger.error(f"Error converting parquet to dict list: {e}")
        raise


def create_unique_index(
    collection: Collection,
    index_fields: List[str],
    index_name: Optional[str] = None
) -> str:
    """
    Create unique index on collection.
    
    Args:
        collection: MongoDB collection
        index_fields: List of field names for index
        index_name: Optional name for index. If None, auto-generated.
        
    Returns:
        str: Index name
        
    Note:
        Creates unique index to prevent duplicate documents
    """
    try:
        index_name = index_name or '_'.join(index_fields) + '_unique'
        
        # Create index specification
        index_spec = [(field, 1) for field in index_fields]
        
        # Create unique index
        collection.create_index(
            index_spec,
            unique=True,
            name=index_name,
            background=True
        )
        
        logger.info(f"Created unique index '{index_name}' on fields: {index_fields}")
        return index_name
        
    except OperationFailure as e:
        if 'already exists' in str(e).lower():
            logger.info(f"Index '{index_name}' already exists")
            return index_name
        else:
            logger.error(f"Error creating index: {e}")
            raise
    except Exception as e:
        logger.error(f"Unexpected error creating index: {e}")
        raise


def validate_collection_name(name: str) -> bool:
    """
    Validate MongoDB collection name.
    
    Args:
        name: Collection name to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Note:
        MongoDB collection names must:
        - Not be empty
        - Not contain $ or null character
        - Not start with 'system.'
        - Be <= 64 characters
    """
    if not name or len(name) == 0:
        return False
    
    if '$' in name or '\x00' in name:
        return False
    
    if name.startswith('system.'):
        return False
    
    if len(name) > 64:
        return False
    
    return True


def add_metadata_to_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add metadata to record (upload timestamp, etc.).
    
    Args:
        record: Record dictionary
        
    Returns:
        Dict with added metadata
    """
    record['_uploaded_at'] = datetime.utcnow().isoformat()
    return record

