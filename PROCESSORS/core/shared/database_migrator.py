"""
DatabaseMigrator for fundamental financial data migration and standardization.
Migrator cơ sở dữ liệu cho migration và chuẩn hóa dữ liệu tài chính cơ bản.
"""

import os
import pandas as pd
import duckdb
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

from data_validator import DataValidator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Database migrator for fundamental financial data.
    Migrator cơ sở dữ liệu cho dữ liệu tài chính cơ bản.
    """
    
    def __init__(self,
                 input_dir: str = None,
                 output_dir: str = None,
                 temp_db_path: str = "temp_fundamental_migration.db"):
        """Initialize DatabaseMigrator.
        Khởi tạo DatabaseMigrator.

        Args:
            input_dir: Input directory containing fundamental parquet files (default: canonical v4.0.0)
            output_dir: Output directory for standardized files (default: canonical v4.0.0)
            temp_db_path: Temporary DuckDB file path
        """
        # Use canonical v4.0.0 paths as defaults
        base_path = Path(__file__).resolve().parents[3]
        if input_dir is None:
            input_dir = base_path / 'DATA' / 'processed' / 'fundamental'
        if output_dir is None:
            output_dir = base_path / 'DATA' / 'processed' / 'fundamental_std'

        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.temp_db_path = temp_db_path

        # Create output directory structure
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "bank").mkdir(exist_ok=True)
        (self.output_dir / "company").mkdir(exist_ok=True)

        # Initialize validators
        self.bank_validator = DataValidator(data_type="bank")
        self.company_validator = DataValidator(data_type="company")
    
    def migrate_all_fundamental_data(self, 
                                   validate: bool = True,
                                   convert_units: bool = True,
                                   parallel: bool = True) -> Dict[str, Any]:
        """Migrate all fundamental data files.
        Migrate tất cả file dữ liệu cơ bản.
        
        Args:
            validate: Whether to validate data during migration
            convert_units: Whether to convert units from thousands to base unit
            parallel: Whether to process files in parallel
            
        Returns:
            Dictionary with migration results
        """
        logger.info("Starting fundamental data migration")
        
        results = {
            "bank": {"files_processed": 0, "total_records": 0, "errors": []},
            "company": {"files_processed": 0, "total_records": 0, "errors": []},
            "migration_time": None
        }
        
        start_time = datetime.now()
        
        try:
            # Process bank data
            bank_results = self._migrate_data_type("bank", validate, convert_units, parallel)
            results["bank"].update(bank_results)
            
            # Process company data
            company_results = self._migrate_data_type("company", validate, convert_units, parallel)
            results["company"].update(company_results)
            
            # Create unified database
            self._create_unified_database()
            
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            results["error"] = str(e)
        
        finally:
            results["migration_time"] = (datetime.now() - start_time).total_seconds()
            logger.info(f"Migration completed in {results['migration_time']:.2f} seconds")
        
        return results
    
    def _migrate_data_type(self, 
                          data_type: str,
                          validate: bool,
                          convert_units: bool,
                          parallel: bool) -> Dict[str, Any]:
        """Migrate data for specific type (bank or company).
        Migrate dữ liệu cho loại cụ thể (bank hoặc company).
        
        Args:
            data_type: Type of data to migrate
            validate: Whether to validate data
            convert_units: Whether to convert units
            parallel: Whether to process in parallel
            
        Returns:
            Dictionary with migration results
        """
        logger.info(f"Migrating {data_type} data")
        
        input_path = self.input_dir / data_type
        output_path = self.output_dir / data_type
        
        if not input_path.exists():
            logger.warning(f"Input directory not found: {input_path}")
            return {"files_processed": 0, "total_records": 0, "errors": ["Input directory not found"]}
        
        # Find parquet files
        parquet_files = list(input_path.glob("*.parquet"))
        
        if not parquet_files:
            logger.warning(f"No parquet files found in {input_path}")
            return {"files_processed": 0, "total_records": 0, "errors": ["No parquet files found"]}
        
        results = {
            "files_processed": 0,
            "total_records": 0,
            "errors": [],
            "file_results": []
        }
        
        if parallel and len(parquet_files) > 1:
            # Process files in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_file = {
                    executor.submit(
                        self._process_single_file,
                        file_path, output_path, data_type, validate, convert_units
                    ): file_path for file_path in parquet_files
                }
                
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        file_result = future.result()
                        results["file_results"].append(file_result)
                        results["files_processed"] += 1
                        results["total_records"] += file_result["records_output"]
                    except Exception as e:
                        error_msg = f"Error processing {file_path}: {e}"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
        else:
            # Process files sequentially
            for file_path in parquet_files:
                try:
                    file_result = self._process_single_file(
                        file_path, output_path, data_type, validate, convert_units
                    )
                    results["file_results"].append(file_result)
                    results["files_processed"] += 1
                    results["total_records"] += file_result["records_output"]
                except Exception as e:
                    error_msg = f"Error processing {file_path}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
        
        logger.info(f"Completed {data_type} migration: {results['files_processed']} files, {results['total_records']} records")
        return results
    
    def _process_single_file(self, 
                           file_path: Path,
                           output_path: Path,
                           data_type: str,
                           validate: bool,
                           convert_units: bool) -> Dict[str, Any]:
        """Process a single parquet file.
        Xử lý một file parquet đơn lẻ.
        
        Args:
            file_path: Input file path
            output_path: Output directory path
            data_type: Type of data (bank or company)
            validate: Whether to validate data
            convert_units: Whether to convert units
            
        Returns:
            Dictionary with file processing results
        """
        logger.info(f"Processing {file_path.name}")
        
        # Read data
        df = pd.read_parquet(file_path)
        logger.info(f"Loaded {len(df)} records from {file_path.name}")
        
        # Get appropriate validator
        validator = self.bank_validator if data_type == "bank" else self.company_validator
        
        # Validate data if requested
        validation_result = None
        if validate:
            validation_result = validator.get_validation_summary(df)
            if not validation_result["overall_valid"]:
                logger.warning(f"Data validation issues in {file_path.name}")
        
        # Clean and standardize data
        df_cleaned = validator.clean_and_standardize(df, convert_units=convert_units)
        
        # Generate output filename
        output_filename = f"{file_path.stem}_std.parquet"
        output_file_path = output_path / output_filename
        
        # Save standardized data
        df_cleaned.to_parquet(output_file_path, index=False)
        logger.info(f"Saved standardized data to {output_file_path}")
        
        return {
            "input_file": str(file_path),
            "output_file": str(output_file_path),
            "records_input": len(df),
            "records_output": len(df_cleaned),
            "validation_result": validation_result,
            "units_converted": convert_units
        }
    
    def _create_unified_database(self):
        """Create unified DuckDB database from standardized files.
        Tạo cơ sở dữ liệu DuckDB thống nhất từ các file đã chuẩn hóa.
        """
        logger.info("Creating unified database")
        
        # Connect to temporary DuckDB
        conn = duckdb.connect(self.temp_db_path)
        
        try:
            # Create bank table
            bank_files = list((self.output_dir / "bank").glob("*_std.parquet"))
            if bank_files:
                bank_file_paths = [str(f) for f in bank_files]
                create_bank_table_query = f"""
                CREATE OR REPLACE TABLE bank_financial_metrics AS
                SELECT * FROM read_parquet({bank_file_paths})
                """
                conn.execute(create_bank_table_query)
                
                # Add indexes
                conn.execute("CREATE INDEX IF NOT EXISTS idx_bank_symbol ON bank_financial_metrics (symbol)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_bank_date ON bank_financial_metrics (report_date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_bank_symbol_date ON bank_financial_metrics (symbol, report_date)")
                
                bank_count = conn.execute("SELECT COUNT(*) FROM bank_financial_metrics").fetchone()[0]
                logger.info(f"Created bank table with {bank_count} records")
            
            # Create company table
            company_files = list((self.output_dir / "company").glob("*_std.parquet"))
            if company_files:
                company_file_paths = [str(f) for f in company_files]
                create_company_table_query = f"""
                CREATE OR REPLACE TABLE company_financial_metrics AS
                SELECT * FROM read_parquet({company_file_paths})
                """
                conn.execute(create_company_table_query)
                
                # Add indexes
                conn.execute("CREATE INDEX IF NOT EXISTS idx_company_symbol ON company_financial_metrics (symbol)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_company_date ON company_financial_metrics (report_date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_company_symbol_date ON company_financial_metrics (symbol, report_date)")
                
                company_count = conn.execute("SELECT COUNT(*) FROM company_financial_metrics").fetchone()[0]
                logger.info(f"Created company table with {company_count} records")
            
            # Create unified view
            unified_view_query = """
            CREATE OR REPLACE VIEW unified_financial_metrics AS
            SELECT 
                'bank' as data_type,
                symbol,
                report_date,
                year,
                quarter,
                freq_code,
                nii as revenue_metric,
                npatmi as profit_metric,
                roea_ttm as roe_metric,
                roaa_ttm as roa_metric,
                eps_ttm as eps_metric,
                bvps as bvps_metric
            FROM bank_financial_metrics
            UNION ALL
            SELECT 
                'company' as data_type,
                symbol,
                report_date,
                year,
                quarter,
                freq_code,
                net_revenue as revenue_metric,
                npatmi as profit_metric,
                roe_ttm as roe_metric,
                roa_ttm as roa_metric,
                eps_ttm as eps_metric,
                NULL as bvps_metric
            FROM company_financial_metrics
            """
            conn.execute(unified_view_query)
            
            # Save database
            final_db_path = self.output_dir / "fundamental_metrics.db"
            conn.execute(f"EXPORT DATABASE '{final_db_path}' (FORMAT PARQUET)")
            
            logger.info(f"Unified database created: {final_db_path}")
            
        finally:
            conn.close()
            # Clean up temporary database
            if os.path.exists(self.temp_db_path):
                os.remove(self.temp_db_path)
    
    def validate_migration_results(self) -> Dict[str, Any]:
        """Validate migration results.
        Validate kết quả migration.
        
        Returns:
            Dictionary with validation results
        """
        logger.info("Validating migration results")
        
        results = {
            "bank": {"is_valid": False, "issues": []},
            "company": {"is_valid": False, "issues": []},
            "overall_valid": False
        }
        
        # Validate bank data
        bank_files = list((self.output_dir / "bank").glob("*_std.parquet"))
        if bank_files:
            try:
                df_bank = pd.read_parquet(bank_files[0])
                bank_validation = self.bank_validator.get_validation_summary(df_bank)
                results["bank"]["is_valid"] = bank_validation["overall_valid"]
                if not bank_validation["overall_valid"]:
                    results["bank"]["issues"] = bank_validation.get("issues", [])
            except Exception as e:
                results["bank"]["issues"].append(f"Error validating bank data: {e}")
        
        # Validate company data
        company_files = list((self.output_dir / "company").glob("*_std.parquet"))
        if company_files:
            try:
                df_company = pd.read_parquet(company_files[0])
                company_validation = self.company_validator.get_validation_summary(df_company)
                results["company"]["is_valid"] = company_validation["overall_valid"]
                if not company_validation["overall_valid"]:
                    results["company"]["issues"] = company_validation.get("issues", [])
            except Exception as e:
                results["company"]["issues"].append(f"Error validating company data: {e}")
        
        results["overall_valid"] = results["bank"]["is_valid"] and results["company"]["is_valid"]
        
        return results
    
    def get_migration_summary(self) -> Dict[str, Any]:
        """Get migration summary statistics.
        Lấy thống kê tóm tắt migration.
        
        Returns:
            Dictionary with migration summary
        """
        summary = {
            "input_directory": str(self.input_dir),
            "output_directory": str(self.output_dir),
            "bank_files": len(list((self.output_dir / "bank").glob("*_std.parquet"))),
            "company_files": len(list((self.output_dir / "company").glob("*_std.parquet"))),
            "database_created": (self.output_dir / "fundamental_metrics.db").exists()
        }
        
        # Count records in each type
        try:
            if summary["bank_files"] > 0:
                bank_files = list((self.output_dir / "bank").glob("*_std.parquet"))
                df_bank = pd.read_parquet(bank_files[0])
                summary["bank_records"] = len(df_bank)
            
            if summary["company_files"] > 0:
                company_files = list((self.output_dir / "company").glob("*_std.parquet"))
                df_company = pd.read_parquet(company_files[0])
                summary["company_records"] = len(df_company)
        except Exception as e:
            logger.warning(f"Error counting records: {e}")
        
        return summary
    
    def optimize_parquet_files(self, 
                             compression: str = "snappy",
                             row_group_size: int = 100000) -> Dict[str, Any]:
        """Optimize parquet files for better performance.
        Tối ưu hóa file parquet để có hiệu suất tốt hơn.
        
        Args:
            compression: Compression algorithm
            row_group_size: Row group size for parquet files
            
        Returns:
            Dictionary with optimization results
        """
        logger.info("Optimizing parquet files")
        
        results = {
            "bank_files_optimized": 0,
            "company_files_optimized": 0,
            "compression": compression,
            "row_group_size": row_group_size
        }
        
        # Optimize bank files
        bank_files = list((self.output_dir / "bank").glob("*_std.parquet"))
        for file_path in bank_files:
            try:
                df = pd.read_parquet(file_path)
                df.to_parquet(
                    file_path,
                    compression=compression,
                    index=False,
                    engine='pyarrow'
                )
                results["bank_files_optimized"] += 1
            except Exception as e:
                logger.error(f"Error optimizing {file_path}: {e}")
        
        # Optimize company files
        company_files = list((self.output_dir / "company").glob("*_std.parquet"))
        for file_path in company_files:
            try:
                df = pd.read_parquet(file_path)
                df.to_parquet(
                    file_path,
                    compression=compression,
                    index=False,
                    engine='pyarrow'
                )
                results["company_files_optimized"] += 1
            except Exception as e:
                logger.error(f"Error optimizing {file_path}: {e}")
        
        logger.info(f"Optimized {results['bank_files_optimized']} bank files and {results['company_files_optimized']} company files")
        
        return results
