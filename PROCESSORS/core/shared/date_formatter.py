"""
Date Format Standardization Utility
===================================

Utility functions để chuẩn hóa định dạng date theo chuẩn YYYY-MM-DD
cho toàn bộ stock_dashboard library.

Author: AI Assistant
Date: 2025-01-27
"""

import pandas as pd
import numpy as np
import json
import os
import logging
from typing import Union, List, Optional
import re
from datetime import datetime, date

logger = logging.getLogger(__name__)

class DateFormatter:
    """Utility class để chuẩn hóa định dạng date theo config."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize DateFormatter với config.
        
        Args:
            config_path: Đường dẫn đến file config. Mặc định là config/data_sources.json
        """
        if config_path is None:
            # Use paths module to get project root
            try:
                from PROCESSORS.core.config.paths import PROJECT_ROOT
                config_path = os.path.join(str(PROJECT_ROOT), 'config', 'data_sources.json')
            except ImportError:
                # Fallback: Tìm config từ project root
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # Go up 4 levels from PROCESSORS/core/shared to project root
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
                config_path = os.path.join(project_root, 'config', 'data_sources.json')
            
            # Debug logging
            logger.info(f"Looking for config at: {config_path}")
        
        self.config_path = config_path
        self.config = self._load_config()
        self.date_standards = self.config.get('date_format_standards', {})
        
    def _load_config(self) -> dict:
        """Load configuration từ JSON file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load config from {self.config_path}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """Default configuration nếu không load được từ file."""
        return {
            'date_format_standards': {
                'target_format': 'YYYY-MM-DD',
                'target_dtype': 'object',
                'rules': {
                    'no_time_component': True,
                    'no_timezone': True,
                    'format_string': '%Y-%m-%d',
                    'pandas_format': 'object'
                },
                'conversion_settings': {
                    'from_datetime': {
                        'method': 'dt.date',
                        'then_convert_to_string': True
                    },
                    'validation': {
                        'regex_pattern': r'^\d{4}-\d{2}-\d{2}$',
                        'min_year': 2010,
                        'max_year': 2030
                    }
                },
                'applicable_columns': [
                    'report_date', 'date', 'trading_date', 
                    'announcement_date', 'effective_date'
                ]
            }
        }
    
    def standardize_date_column(self, 
                               df: pd.DataFrame, 
                               column_name: str,
                               inplace: bool = False) -> pd.DataFrame:
        """
        Chuẩn hóa một cột date thành định dạng YYYY-MM-DD.
        
        Args:
            df: DataFrame chứa dữ liệu
            column_name: Tên cột cần chuẩn hóa
            inplace: Có modify DataFrame gốc hay không
            
        Returns:
            DataFrame với cột date đã được chuẩn hóa
        """
        if not inplace:
            df = df.copy()
            
        if column_name not in df.columns:
            logger.warning(f"Column '{column_name}' not found in DataFrame")
            return df
            
        logger.info(f"Standardizing date format for column: {column_name}")
        
        # Backup original data type info
        original_dtype = df[column_name].dtype
        logger.info(f"Original dtype of {column_name}: {original_dtype}")
        
        try:
            # Convert to pandas datetime first if not already
            if not pd.api.types.is_datetime64_any_dtype(df[column_name]):
                df[column_name] = pd.to_datetime(df[column_name], errors='coerce')
            
            # Convert datetime to date (removes time component)
            df[column_name] = df[column_name].dt.date
            
            # Convert to string format YYYY-MM-DD
            df[column_name] = df[column_name].astype(str)
            
            # Validate format
            valid_pattern = self.date_standards.get('conversion_settings', {}).get('validation', {}).get('regex_pattern', r'^\d{4}-\d{2}-\d{2}$')
            invalid_mask = ~df[column_name].str.match(valid_pattern, na=False)
            
            if invalid_mask.any():
                invalid_count = invalid_mask.sum()
                logger.warning(f"Found {invalid_count} invalid date formats in {column_name}")
                # Set invalid dates to NaN
                df.loc[invalid_mask, column_name] = np.nan
                
            logger.info(f"Successfully standardized {column_name} to YYYY-MM-DD format")
            
        except Exception as e:
            logger.error(f"Error standardizing date column {column_name}: {e}")
            raise
            
        return df
    
    def standardize_all_date_columns(self, 
                                   df: pd.DataFrame,
                                   inplace: bool = False) -> pd.DataFrame:
        """
        Chuẩn hóa tất cả các cột date trong DataFrame.
        
        Args:
            df: DataFrame chứa dữ liệu
            inplace: Có modify DataFrame gốc hay không
            
        Returns:
            DataFrame với tất cả date columns đã được chuẩn hóa
        """
        if not inplace:
            df = df.copy()
            
        applicable_columns = self.date_standards.get('applicable_columns', [])
        
        for col in df.columns:
            # Check if column name matches any of the applicable patterns
            if any(pattern.lower() in col.lower() for pattern in applicable_columns):
                df = self.standardize_date_column(df, col, inplace=True)
                
        return df
    
    def validate_date_format(self, df: pd.DataFrame, column_name: str) -> dict:
        """
        Validate date format trong một cột.
        
        Args:
            df: DataFrame chứa dữ liệu
            column_name: Tên cột cần validate
            
        Returns:
            Dict chứa thông tin validation
        """
        if column_name not in df.columns:
            return {'valid': False, 'error': f"Column '{column_name}' not found"}
            
        valid_pattern = self.date_standards.get('conversion_settings', {}).get('validation', {}).get('regex_pattern', r'^\d{4}-\d{2}-\d{2}$')
        
        # Count valid vs invalid formats
        # Convert to string first if not already
        col_series = df[column_name].astype(str)
        valid_mask = col_series.str.match(valid_pattern, na=False) & (col_series != 'nan')
        total_count = len(df)
        valid_count = valid_mask.sum()
        null_count = df[column_name].isna().sum()
        invalid_count = total_count - valid_count - null_count
        
        return {
            'valid': True,
            'total_rows': total_count,
            'valid_dates': valid_count,
            'invalid_dates': invalid_count,
            'null_dates': null_count,
            'format_compliance': valid_count / total_count if total_count > 0 else 0,
            'sample_valid': col_series[valid_mask].head(3).tolist() if valid_count > 0 else [],
            'sample_invalid': col_series[~valid_mask & (col_series != 'nan')].head(3).tolist() if invalid_count > 0 else []
        }

def standardize_dataframe_dates(df: pd.DataFrame, 
                              config_path: str = None,
                              inplace: bool = False) -> pd.DataFrame:
    """
    Convenience function để chuẩn hóa tất cả date columns trong DataFrame.
    
    Args:
        df: DataFrame cần chuẩn hóa
        config_path: Đường dẫn config file (optional)
        inplace: Có modify DataFrame gốc hay không
        
    Returns:
        DataFrame với date columns đã được chuẩn hóa
    """
    formatter = DateFormatter(config_path)
    return formatter.standardize_all_date_columns(df, inplace=inplace)

def validate_dataframe_dates(df: pd.DataFrame, 
                           config_path: str = None) -> dict:
    """
    Convenience function để validate tất cả date columns trong DataFrame.
    
    Args:
        df: DataFrame cần validate
        config_path: Đường dẫn config file (optional)
        
    Returns:
        Dict chứa validation results cho tất cả date columns
    """
    formatter = DateFormatter(config_path)
    applicable_columns = formatter.date_standards.get('applicable_columns', [])
    
    results = {}
    for col in df.columns:
        if any(pattern.lower() in col.lower() for pattern in applicable_columns):
            results[col] = formatter.validate_date_format(df, col)
            
    return results
