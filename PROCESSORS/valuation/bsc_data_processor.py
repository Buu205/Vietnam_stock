#!/usr/bin/env python3
"""
BSC Data Processor - Xử lý dữ liệu BSC Forecast từ Excel sang CSV
Tự động hóa việc chuyển đổi từ Database Forecast BSC.xlsx → bsc_forecast_latest.csv

Usage:
    python3 bsc_data_processor.py [--force] [--validate-only]

Author: AI Assistant
Date: 2025-12-10
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Disable pandas type checking for this file
pd.set_option('mode.chained_assignment', None)

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

# Create logs directory if it doesn't exist
logs_dir = PROJECT_ROOT / 'logs'
logs_dir.mkdir(parents=True, exist_ok=True)

# Setup logging
# Create logs directory if it doesn't exist
logs_dir = PROJECT_ROOT / 'logs'
logs_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'bsc_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BSCDataProcessor:
    """Processor cho dữ liệu BSC Forecast từ Excel sang CSV"""
    
    def __init__(self):
        """Initialize BSC Data Processor"""
        # File paths
        self.excel_path = PROJECT_ROOT / "PROCESSORS/forecast/Database Forecast BSC.xlsx"
        self.output_dir = PROJECT_ROOT / "DATA/processed/forecast/bsc/"
        self.output_file = self.output_dir / "bsc_forecast_latest.csv"
        self.backup_dir = self.output_dir / "backup/"
        
        # Column mapping (Vietnamese → English)
        self.column_mapping = {
            'ticker': 'symbol',
            'Rating': 'rating', 
            'target_price': 'target_price',
            '2025_rev': 'rev_fy',
            '2026_rev': 'rev_fy_1',
            '2025_npat': 'npatmi_fy',
            '2026_npat': 'npatmi_fy_1',
            '2025_eps': 'eps_fy',
            '2026_eps': 'eps_fy_1',
            '2025_bv': 'bv_fy',
            '2026_bv': 'bv_fy_1',
            '2025_roe': 'roe_fy',
            '2026_roe': 'roe_fy_1',
            '2025_roa': 'roa_fy',
            '2026_roa': 'roa_fy_1'
        }
        
        # Validation requirements
        self.min_symbols = 85
        self.required_columns = ['symbol', 'rating', 'target_price', 'rev_fy']
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("📊 BSC Data Processor initialized")
        logger.info(f"📁 Excel file: {self.excel_path}")
        logger.info(f"📁 Output directory: {self.output_dir}")
        logger.info(f"📁 Output file: {self.output_file}")
    
    def process_excel_to_csv(self, force_update: bool = False) -> bool:
        """
        Process Excel file and create standardized CSV
        
        Args:
            force_update: Force update even if CSV exists and is newer
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("🔄 Starting BSC data processing...")
            
            # Check if output file exists and is newer than Excel
            if not force_update and self.output_file.exists():
                excel_mtime = self.excel_path.stat().st_mtime
                csv_mtime = self.output_file.stat().st_mtime
                if csv_mtime >= excel_mtime:
                    logger.info("📋 CSV file is up-to-date, skipping processing")
                    return True
            
            # Load Excel data
            logger.info("📖 Loading Excel file...")
            df = pd.read_excel(self.excel_path, sheet_name="Codedata")
            logger.info(f"   Loaded {len(df)} rows from Codedata sheet")
            
            # Validate data
            validation_result = self.validate_data(df)
            if not validation_result['valid']:
                logger.error(f"❌ Data validation failed: {validation_result['errors']}")
                return False
            
            # Process data
            logger.info("🔄 Processing data...")
            processed_df = self.process_data(df)
            
            # Save to CSV
            logger.info(f"💾 Saving to CSV: {self.output_file}")
            processed_df.to_csv(self.output_file, index=False)
            
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"bsc_forecast_{timestamp}.csv"
            processed_df.to_csv(backup_file, index=False)
            logger.info(f"💾 Backup created: {backup_file}")
            
            # Generate report
            self.generate_processing_report(df, processed_df, validation_result)
            
            logger.info("✅ BSC data processing completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing BSC data: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def validate_data(self, df: pd.DataFrame) -> Dict:
        """
        Validate BSC data completeness and quality
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Check minimum symbols
        if len(df) < self.min_symbols:
            errors.append(f"Insufficient symbols: {len(df)} < {self.min_symbols}")
        
        # Check required columns
        missing_cols = []
        for col in self.required_columns:
            if col not in df.columns:
                missing_cols.append(col)
        
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
        
        # Check for empty critical fields
        if df['symbol'].isnull().any():
            errors.append("Empty symbol values found")
        
        if df['target_price'].isnull().any():
            warnings.append("Some target_price values are empty")
        
        # Check data types
        if not pd.api.types.is_numeric_dtype(df['target_price']):
            warnings.append("target_price should be numeric")
        
        # Check for reasonable values
        if 'rev_fy' in df.columns:
            invalid_rev = df[df['rev_fy'] < 0].shape[0]
            if len(invalid_rev) > 0:
                warnings.append(f"Found {len(invalid_rev)} negative revenue values")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_symbols': len(df),
            'valid_symbols': len(df) - len(df[df['symbol'].isnull()])
        }
    
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process and standardize BSC data
        
        Args:
            df: Raw DataFrame from Excel
            
        Returns:
            Processed DataFrame with standardized columns
        """
        logger.info("🔄 Processing BSC data...")
        
        # Create processed DataFrame with mapped columns
        processed_df = pd.DataFrame()
        
        # Map columns using the mapping dictionary
        for old_col, new_col in self.column_mapping.items():
            if old_col in df.columns:
                processed_df[new_col] = df[old_col]
            else:
                logger.warning(f"⚠️ Column '{old_col}' not found in source data")
                processed_df[new_col] = None
        
        # Add processing timestamp
        processed_df['processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        processed_df['data_source'] = 'Database Forecast BSC.xlsx'
        
        # Data quality improvements
        if 'rating' in processed_df.columns:
            # Standardize rating values
            processed_df['rating'] = processed_df['rating'].str.upper().str.strip()
        
        if 'target_price' in processed_df.columns:
            # Clean and validate target prices
            processed_df['target_price'] = pd.to_numeric(processed_df['target_price'], errors='coerce')
            # Filter out unreasonable values
            processed_df = processed_df[
                (processed_df['target_price'] > 0) & 
                (processed_df['target_price'] < 1000000)  # Max 10M VND
            ]
        
        logger.info(f"📊 Processed {len(processed_df)} symbols with standardized columns")
        return processed_df
    
    def generate_processing_report(self, original_df: pd.DataFrame, processed_df: pd.DataFrame, validation_result: Dict):
        """Generate processing report"""
        logger.info("📋 Generating processing report...")
        
        report_lines = [
            "=== BSC DATA PROCESSING REPORT ===",
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Excel File: {self.excel_path}",
            f"Output File: {self.output_file}",
            "",
            "DATA SUMMARY:",
            f"  Original Records: {len(original_df)}",
            f"  Processed Records: {len(processed_df)}",
            f"  Validation: {'✅ PASS' if validation_result['valid'] else '❌ FAIL'}",
            "",
            "COLUMN MAPPING:",
        ]
        
        for old_col, new_col in self.column_mapping.items():
            if old_col in original_df.columns:
                report_lines.append(f"  {old_col} → {new_col}")
        
        if validation_result['warnings']:
            report_lines.extend(["", "WARNINGS:"])
            report_lines.extend([f"  - {warning}" for warning in validation_result['warnings']])
        
        if validation_result['errors']:
            report_lines.extend(["", "ERRORS:"])
            report_lines.extend([f"  - {error}" for error in validation_result['errors']])
        
        report_lines.extend([
            "",
            "SAMPLE PROCESSED DATA:",
            f"  First 5 rows:",
        ])
        
        if not processed_df.empty:
            sample_cols = ['symbol', 'rating', 'target_price', 'rev_fy']
            available_cols = [col for col in sample_cols if col in processed_df.columns]
            sample_data = processed_df[available_cols].head().to_string(index=False)
            report_lines.append(sample_data)
        
        # Write report to file
        report_file = self.output_dir / f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"📋 Report saved to: {report_file}")
    
    def get_latest_bsc_symbols(self) -> List[str]:
        """Get list of BSC symbols from latest CSV"""
        try:
            if self.output_file.exists():
                df = pd.read_csv(self.output_file)
                symbols = df['symbol'].dropna().unique().tolist()
                logger.info(f"📊 Loaded {len(symbols)} BSC symbols from CSV")
                return sorted(symbols)
            else:
                logger.warning("⚠️ BSC CSV file not found")
                return []
        except Exception as e:
            logger.error(f"❌ Error loading BSC symbols: {e}")
            return []

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='BSC Data Processor')
    parser.add_argument('--force', action='store_true', help='Force update even if CSV is newer')
    parser.add_argument('--validate-only', action='store_true', help='Only validate data, no processing')
    
    args = parser.parse_args()
    
    # Create processor
    processor = BSCDataProcessor()
    
    if args.validate_only:
        # Only validate existing CSV
        if processor.output_file.exists():
            df = pd.read_csv(processor.output_file)
            validation_result = processor.validate_data(df)
            
            print("=== BSC DATA VALIDATION ===")
            print(f"Status: {'✅ PASS' if validation_result['valid'] else '❌ FAIL'}")
            print(f"Total Symbols: {validation_result['total_symbols']}")
            print(f"Valid Symbols: {validation_result['valid_symbols']}")
            
            if validation_result['warnings']:
                print("Warnings:")
                for warning in validation_result['warnings']:
                    print(f"  - {warning}")
            
            if validation_result['errors']:
                print("Errors:")
                for error in validation_result['errors']:
                    print(f"  - {error}")
        else:
            print("❌ BSC CSV file not found")
    else:
        # Process Excel to CSV
        success = processor.process_excel_to_csv(force_update=args.force)
        if success:
            print("✅ BSC data processing completed successfully")
        else:
            print("❌ BSC data processing failed")

if __name__ == "__main__":
    main()
    