"""
Data Source Manager for managing multiple data sources.
Quản lý nguồn dữ liệu cho việc quản lý nhiều nguồn dữ liệu.
"""

import os
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Union
import logging
from pathlib import Path
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSourceManager:
    """Manager for handling multiple data sources.
    Quản lý xử lý nhiều nguồn dữ liệu.
    """
    
    def __init__(self,
                 data_warehouse_path: str = None,
                 config_path: str = "config/data_sources.json"):
        """Initialize DataSourceManager.
        Khởi tạo DataSourceManager.
        
        Args:
            data_warehouse_path: Path to data warehouse
            config_path: Path to data sources configuration
        """
        # Use canonical v4.0.0 path as default
        if data_warehouse_path is None:
            data_warehouse_path = Path(__file__).resolve().parents[3] / "DATA"

        self.data_warehouse_path = Path(data_warehouse_path)
        self.config_path = Path(config_path)
        self.data_sources = {}
        self.schemas = {}
        
        # Load configuration
        self._load_configuration()
        
        # Load schemas
        self._load_schemas()
    
    def _load_configuration(self):
        """Load data sources configuration.
        Tải cấu hình nguồn dữ liệu.
        """
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.data_sources = config.get('data_sources', {})
        else:
            # Default configuration
            self.data_sources = {
                "ohlcv": {
                    "raw_path": "raw/ohlcv",
                    "processed_path": "processed/ohlcv",
                    "schema_file": "schemas/ohlcv_schema.json",
                    "file_pattern": "*.parquet",
                    "description": "OHLCV price and volume data"
                },
                "fundamental": {
                    "raw_path": "raw/fundamental",
                    "processed_path": "processed/fundamental",
                    "schema_file": "schemas/fundamental_schema.json",
                    "file_pattern": "*.parquet",
                    "description": "Fundamental financial data"
                },
                "technical": {
                    "raw_path": "raw/technical",
                    "processed_path": "processed/technical",
                    "schema_file": "schemas/technical_schema.json",
                    "file_pattern": "*.parquet",
                    "description": "Technical indicators and signals"
                }
            }
    
    def _load_schemas(self):
        """Load data schemas.
        Tải schema dữ liệu.
        """
        schemas_dir = self.data_warehouse_path / "schemas"
        
        for schema_file in schemas_dir.glob("*.json"):
            try:
                with open(schema_file, 'r') as f:
                    schema_name = schema_file.stem
                    self.schemas[schema_name] = json.load(f)
                    logger.info(f"Loaded schema: {schema_name}")
            except Exception as e:
                logger.error(f"Error loading schema {schema_file}: {e}")
    
    def get_data_source_info(self, source_name: str) -> Dict[str, Any]:
        """Get information about a data source.
        Lấy thông tin về một nguồn dữ liệu.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Dictionary with data source information
        """
        if source_name not in self.data_sources:
            raise ValueError(f"Data source '{source_name}' not found")
        
        source_info = self.data_sources[source_name].copy()
        
        # Add file counts
        raw_path = self.data_warehouse_path / source_info["raw_path"]
        processed_path = self.data_warehouse_path / source_info["processed_path"]
        
        source_info["raw_files_count"] = len(list(raw_path.glob(source_info["file_pattern"]))) if raw_path.exists() else 0
        source_info["processed_files_count"] = len(list(processed_path.glob(source_info["file_pattern"]))) if processed_path.exists() else 0
        
        # Add schema info
        schema_name = source_info["schema_file"].replace("schemas/", "").replace(".json", "")
        if schema_name in self.schemas:
            source_info["schema"] = self.schemas[schema_name]
        
        return source_info
    
    def list_data_sources(self) -> List[str]:
        """List all available data sources.
        Liệt kê tất cả nguồn dữ liệu có sẵn.
        
        Returns:
            List of data source names
        """
        return list(self.data_sources.keys())
    
    def get_data_path(self, source_name: str, data_type: str = "processed") -> Path:
        """Get path for a data source.
        Lấy đường dẫn cho một nguồn dữ liệu.
        
        Args:
            source_name: Name of the data source
            data_type: Type of data ("raw" or "processed")
            
        Returns:
            Path to the data source
        """
        if source_name not in self.data_sources:
            raise ValueError(f"Data source '{source_name}' not found")
        
        path_key = f"{data_type}_path"
        if path_key not in self.data_sources[source_name]:
            raise ValueError(f"Data type '{data_type}' not found for source '{source_name}'")
        
        return self.data_warehouse_path / self.data_sources[source_name][path_key]
    
    def get_schema(self, source_name: str) -> Dict[str, Any]:
        """Get schema for a data source.
        Lấy schema cho một nguồn dữ liệu.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Schema dictionary
        """
        if source_name not in self.data_sources:
            raise ValueError(f"Data source '{source_name}' not found")
        
        schema_file = self.data_sources[source_name]["schema_file"]
        schema_name = schema_file.replace("schemas/", "").replace(".json", "")
        
        if schema_name not in self.schemas:
            raise ValueError(f"Schema for '{source_name}' not found")
        
        return self.schemas[schema_name]
    
    def validate_data_source(self, source_name: str) -> Dict[str, Any]:
        """Validate a data source.
        Validate một nguồn dữ liệu.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Dictionary with validation results
        """
        if source_name not in self.data_sources:
            return {"is_valid": False, "error": f"Data source '{source_name}' not found"}
        
        result = {
            "is_valid": True,
            "source_name": source_name,
            "issues": [],
            "file_counts": {}
        }
        
        try:
            # Check raw data path
            raw_path = self.get_data_path(source_name, "raw")
            if raw_path.exists():
                raw_files = list(raw_path.glob(self.data_sources[source_name]["file_pattern"]))
                result["file_counts"]["raw"] = len(raw_files)
                if len(raw_files) == 0:
                    result["issues"].append("No raw data files found")
            else:
                result["issues"].append("Raw data path does not exist")
                result["file_counts"]["raw"] = 0
            
            # Check processed data path
            processed_path = self.get_data_path(source_name, "processed")
            if processed_path.exists():
                processed_files = list(processed_path.glob(self.data_sources[source_name]["file_pattern"]))
                result["file_counts"]["processed"] = len(processed_files)
                if len(processed_files) == 0:
                    result["issues"].append("No processed data files found")
            else:
                result["issues"].append("Processed data path does not exist")
                result["file_counts"]["processed"] = 0
            
            # Check schema
            try:
                schema = self.get_schema(source_name)
                result["schema_loaded"] = True
            except Exception as e:
                result["issues"].append(f"Schema loading error: {e}")
                result["schema_loaded"] = False
            
            # Overall validation
            result["is_valid"] = len(result["issues"]) == 0
            
        except Exception as e:
            result["is_valid"] = False
            result["error"] = str(e)
        
        return result
    
    def get_data_summary(self, source_name: str) -> Dict[str, Any]:
        """Get summary statistics for a data source.
        Lấy thống kê tóm tắt cho một nguồn dữ liệu.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Dictionary with data summary
        """
        if source_name not in self.data_sources:
            raise ValueError(f"Data source '{source_name}' not found")
        
        summary = {
            "source_name": source_name,
            "description": self.data_sources[source_name]["description"],
            "file_counts": {},
            "data_ranges": {},
            "last_updated": None
        }
        
        try:
            # Get file counts
            raw_path = self.get_data_path(source_name, "raw")
            processed_path = self.get_data_path(source_name, "processed")
            
            if raw_path.exists():
                raw_files = list(raw_path.glob(self.data_sources[source_name]["file_pattern"]))
                summary["file_counts"]["raw"] = len(raw_files)
                
                # Get data range from first file
                if raw_files:
                    try:
                        df = pd.read_parquet(raw_files[0])
                        if 'date' in df.columns:
                            summary["data_ranges"]["raw"] = {
                                "min_date": df['date'].min(),
                                "max_date": df['date'].max(),
                                "total_records": len(df)
                            }
                    except Exception as e:
                        logger.warning(f"Error reading raw data for summary: {e}")
            
            if processed_path.exists():
                processed_files = list(processed_path.glob(self.data_sources[source_name]["file_pattern"]))
                summary["file_counts"]["processed"] = len(processed_files)
                
                # Get data range from first file
                if processed_files:
                    try:
                        df = pd.read_parquet(processed_files[0])
                        if 'date' in df.columns or 'report_date' in df.columns:
                            date_col = 'date' if 'date' in df.columns else 'report_date'
                            summary["data_ranges"]["processed"] = {
                                "min_date": df[date_col].min(),
                                "max_date": df[date_col].max(),
                                "total_records": len(df)
                            }
                    except Exception as e:
                        logger.warning(f"Error reading processed data for summary: {e}")
            
            # Get last updated time
            if processed_path.exists():
                processed_files = list(processed_path.glob(self.data_sources[source_name]["file_pattern"]))
                if processed_files:
                    latest_file = max(processed_files, key=os.path.getmtime)
                    summary["last_updated"] = datetime.fromtimestamp(os.path.getmtime(latest_file))
        
        except Exception as e:
            logger.error(f"Error getting data summary for {source_name}: {e}")
            summary["error"] = str(e)
        
        return summary
    
    def get_all_data_summaries(self) -> Dict[str, Any]:
        """Get summaries for all data sources.
        Lấy tóm tắt cho tất cả nguồn dữ liệu.
        
        Returns:
            Dictionary with all data summaries
        """
        summaries = {}
        
        for source_name in self.list_data_sources():
            try:
                summaries[source_name] = self.get_data_summary(source_name)
            except Exception as e:
                summaries[source_name] = {"error": str(e)}
        
        return summaries
    
    def create_data_source(self, 
                          source_name: str,
                          raw_path: str,
                          processed_path: str,
                          schema_file: str,
                          file_pattern: str = "*.parquet",
                          description: str = "") -> bool:
        """Create a new data source configuration.
        Tạo cấu hình nguồn dữ liệu mới.
        
        Args:
            source_name: Name of the data source
            raw_path: Path to raw data
            processed_path: Path to processed data
            schema_file: Path to schema file
            file_pattern: File pattern for data files
            description: Description of the data source
            
        Returns:
            True if successful
        """
        try:
            # Add to data sources
            self.data_sources[source_name] = {
                "raw_path": raw_path,
                "processed_path": processed_path,
                "schema_file": schema_file,
                "file_pattern": file_pattern,
                "description": description
            }
            
            # Create directories
            raw_dir = self.data_warehouse_path / raw_path
            processed_dir = self.data_warehouse_path / processed_path
            
            raw_dir.mkdir(parents=True, exist_ok=True)
            processed_dir.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            self._save_configuration()
            
            logger.info(f"Created data source: {source_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating data source {source_name}: {e}")
            return False
    
    def _save_configuration(self):
        """Save data sources configuration.
        Lưu cấu hình nguồn dữ liệu.
        """
        config = {
            "data_sources": self.data_sources,
            "last_updated": datetime.now().isoformat()
        }
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("Configuration saved")
