"""
DataValidator for fundamental financial data validation and unit conversion.
Validator dữ liệu tài chính cơ bản để kiểm tra tính hợp lệ và chuyển đổi đơn vị.
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple, Union
import logging
from pathlib import Path
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """Data validator for fundamental financial data with unit conversion capabilities.
    Validator dữ liệu tài chính cơ bản với khả năng chuyển đổi đơn vị.
    """
    
    # Standard schemas for different data types
    BANK_SCHEMA = {
        'symbol': 'VARCHAR',
        'report_date': 'DATE',
        'year': 'INTEGER',
        'quarter': 'INTEGER',
        'freq_code': 'VARCHAR',
        'npl_amount': 'DOUBLE',
        'nii': 'DOUBLE',
        'toi': 'DOUBLE',
        'noii': 'DOUBLE',
        'opex': 'DOUBLE',
        'ppop': 'DOUBLE',
        'provision_expense': 'DOUBLE',
        'pbt': 'DOUBLE',
        'npatmi': 'DOUBLE',
        'interest_income': 'DOUBLE',
        'interest_expense': 'DOUBLE',
        'iea': 'DOUBLE',
        'ibl': 'DOUBLE',
        'avg_iea_2q': 'DOUBLE',
        'avg_ibl_2q': 'DOUBLE',
        'total_credit': 'DOUBLE',
        'customer_loan': 'DOUBLE',
        'customer_deposit': 'DOUBLE',
        'roea_ttm': 'DOUBLE',
        'roaa_ttm': 'DOUBLE',
        'asset_yield_q': 'DOUBLE',
        'funding_cost_q': 'DOUBLE',
        'nim_q': 'DOUBLE',
        'loan_yield_q': 'DOUBLE',
        'casa_ratio': 'DOUBLE',
        'cir': 'DOUBLE',
        'nii_toi': 'DOUBLE',
        'noii_toi': 'DOUBLE',
        'ldr_pure': 'DOUBLE',
        'ldr_regulated_estimated': 'DOUBLE',
        'debt_group2_ratio': 'DOUBLE',
        'npl_ratio': 'DOUBLE',
        'group2_to_total_ratio': 'DOUBLE',
        'llcr': 'DOUBLE',
        'bvps': 'DOUBLE',
        'eps_ttm': 'DOUBLE'
    }
    
    COMPANY_SCHEMA = {
        'symbol': 'VARCHAR',
        'report_date': 'DATE',
        'year': 'INTEGER',
        'quarter': 'INTEGER',
        'freq_code': 'VARCHAR',
        'net_revenue': 'DOUBLE',
        'cogs': 'DOUBLE',
        'gross_profit': 'DOUBLE',
        'sga': 'DOUBLE',
        'ebit': 'DOUBLE',
        'net_finance_income': 'DOUBLE',
        'ebt': 'DOUBLE',
        'npatmi': 'DOUBLE',
        'depreciation': 'DOUBLE',
        'ebitda': 'DOUBLE',
        'gross_margin': 'DOUBLE',
        'ebit_margin': 'DOUBLE',
        'ebitda_margin': 'DOUBLE',
        'net_margin': 'DOUBLE',
        'roe': 'DOUBLE',
        'roa': 'DOUBLE',
        'eps': 'DOUBLE',
        'net_revenue_ttm': 'DOUBLE',
        'gross_profit_ttm': 'DOUBLE',
        'ebit_ttm': 'DOUBLE',
        'ebitda_ttm': 'DOUBLE',
        'npatmi_ttm': 'DOUBLE',
        'gross_margin_ttm': 'DOUBLE',
        'ebit_margin_ttm': 'DOUBLE',
        'ebitda_margin_ttm': 'DOUBLE',
        'net_margin_ttm': 'DOUBLE',
        'roe_ttm': 'DOUBLE',
        'roa_ttm': 'DOUBLE',
        'eps_ttm': 'DOUBLE'
    }
    
    # Unit conversion factors (from thousands VND to VND)
    UNIT_CONVERSION = {
        'amount_columns': [
            'npl_amount', 'nii', 'toi', 'noii', 'opex', 'ppop', 'provision_expense',
            'pbt', 'npatmi', 'interest_income', 'interest_expense', 'iea', 'ibl',
            'avg_iea_2q', 'avg_ibl_2q', 'total_credit', 'customer_loan', 'customer_deposit',
            'net_revenue', 'cogs', 'gross_profit', 'sga', 'ebit', 'net_finance_income',
            'ebt', 'depreciation', 'ebitda', 'net_revenue_ttm', 'gross_profit_ttm',
            'ebit_ttm', 'ebitda_ttm', 'npatmi_ttm'
        ],
        'ratio_columns': [
            'roea_ttm', 'roaa_ttm', 'asset_yield_q', 'funding_cost_q', 'nim_q',
            'loan_yield_q', 'casa_ratio', 'cir', 'nii_toi', 'noii_toi', 'ldr_pure',
            'ldr_regulated_estimated', 'debt_group2_ratio', 'npl_ratio', 'group2_to_total_ratio',
            'llcr', 'gross_margin', 'ebit_margin', 'ebitda_margin', 'net_margin',
            'roe', 'roa', 'gross_margin_ttm', 'ebit_margin_ttm', 'ebitda_margin_ttm',
            'net_margin_ttm', 'roe_ttm', 'roa_ttm'
        ],
        'per_share_columns': ['bvps', 'eps', 'eps_ttm']
    }
    
    def __init__(self, 
                 data_type: str = "company",  # "bank" or "company"
                 unit_threshold: float = 1000.0,
                 ratio_threshold: float = 100.0):
        """Initialize DataValidator.
        Khởi tạo DataValidator.
        
        Args:
            data_type: Type of data ("bank" or "company")
            unit_threshold: Threshold for detecting unit conversion issues
            ratio_threshold: Threshold for detecting ratio anomalies
        """
        self.data_type = data_type
        self.unit_threshold = unit_threshold
        self.ratio_threshold = ratio_threshold
        
        # Set schema based on data type
        if data_type == "bank":
            self.schema = self.BANK_SCHEMA
        elif data_type == "company":
            self.schema = self.COMPANY_SCHEMA
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
    
    def validate_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate DataFrame schema against standard schema.
        Validate schema DataFrame với schema chuẩn.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            "is_valid": True,
            "missing_columns": [],
            "extra_columns": [],
            "type_mismatches": [],
            "warnings": []
        }
        
        # Check for missing columns
        required_columns = list(self.schema.keys())
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            result["missing_columns"] = missing_columns
            result["is_valid"] = False
        
        # Check for extra columns
        extra_columns = [col for col in df.columns if col not in required_columns]
        if extra_columns:
            result["extra_columns"] = extra_columns
            result["warnings"].append(f"Extra columns found: {extra_columns}")
        
        # Check data types
        for col, expected_type in self.schema.items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if not self._is_type_compatible(actual_type, expected_type):
                    result["type_mismatches"].append({
                        "column": col,
                        "expected": expected_type,
                        "actual": actual_type
                    })
                    result["warnings"].append(f"Type mismatch in {col}: expected {expected_type}, got {actual_type}")
        
        return result
    
    def _is_type_compatible(self, actual_type: str, expected_type: str) -> bool:
        """Check if actual type is compatible with expected type.
        Kiểm tra xem kiểu thực tế có tương thích với kiểu mong đợi không.
        """
        type_mapping = {
            'VARCHAR': ['object', 'string'],
            'INTEGER': ['int32', 'int64', 'int'],
            'DOUBLE': ['float64', 'float32', 'float'],
            'DATE': ['datetime64[ns]', 'datetime64', 'object']
        }
        
        expected_types = type_mapping.get(expected_type, [expected_type])
        return any(actual_type.startswith(t) for t in expected_types)
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data quality and detect anomalies.
        Validate chất lượng dữ liệu và phát hiện bất thường.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with quality validation results
        """
        result = {
            "is_valid": True,
            "anomalies": [],
            "warnings": [],
            "statistics": {}
        }
        
        # Check for missing values
        missing_stats = df.isnull().sum()
        high_missing = missing_stats[missing_stats > len(df) * 0.5]
        if not high_missing.empty:
            result["warnings"].append(f"High missing values in columns: {high_missing.to_dict()}")
        
        # Check for duplicate records
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            result["warnings"].append(f"Found {duplicates} duplicate records")
        
        # Check for negative values in amount columns
        amount_cols = [col for col in self.UNIT_CONVERSION['amount_columns'] if col in df.columns]
        for col in amount_cols:
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                result["anomalies"].append(f"Negative values in {col}: {negative_count} records")
        
        # Check for extreme values in ratio columns
        ratio_cols = [col for col in self.UNIT_CONVERSION['ratio_columns'] if col in df.columns]
        for col in ratio_cols:
            if col in df.columns:
                extreme_values = df[col].abs() > self.ratio_threshold
                extreme_count = extreme_values.sum()
                if extreme_count > 0:
                    result["anomalies"].append(f"Extreme values in {col}: {extreme_count} records")
        
        # Check date consistency
        if 'report_date' in df.columns and 'year' in df.columns:
            date_year_mismatch = df['report_date'].dt.year != df['year']
            mismatch_count = date_year_mismatch.sum()
            if mismatch_count > 0:
                result["anomalies"].append(f"Date-year mismatch: {mismatch_count} records")
        
        # Check quarter consistency
        if 'report_date' in df.columns and 'quarter' in df.columns:
            expected_quarters = ((df['report_date'].dt.month - 1) // 3) + 1
            quarter_mismatch = df['quarter'] != expected_quarters
            mismatch_count = quarter_mismatch.sum()
            if mismatch_count > 0:
                result["anomalies"].append(f"Date-quarter mismatch: {mismatch_count} records")
        
        # Calculate statistics
        result["statistics"] = {
            "total_records": len(df),
            "missing_values": missing_stats.to_dict(),
            "duplicates": duplicates,
            "date_range": {
                "min": df['report_date'].min() if 'report_date' in df.columns else None,
                "max": df['report_date'].max() if 'report_date' in df.columns else None
            }
        }
        
        return result
    
    def detect_unit_issues(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect potential unit conversion issues.
        Phát hiện các vấn đề chuyển đổi đơn vị tiềm ẩn.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with unit analysis results
        """
        result = {
            "suspicious_columns": [],
            "unit_analysis": {},
            "recommendations": []
        }
        
        amount_cols = [col for col in self.UNIT_CONVERSION['amount_columns'] if col in df.columns]
        
        for col in amount_cols:
            if col in df.columns:
                values = df[col].dropna()
                if len(values) > 0:
                    # Check if values seem too small (might be in thousands)
                    median_value = values.median()
                    max_value = values.max()
                    
                    # If median is less than threshold, might need unit conversion
                    if median_value < self.unit_threshold and max_value < self.unit_threshold * 100:
                        result["suspicious_columns"].append(col)
                        result["unit_analysis"][col] = {
                            "median": median_value,
                            "max": max_value,
                            "likely_in_thousands": True
                        }
                        result["recommendations"].append(f"Column {col} might be in thousands VND, consider converting to VND")
                    else:
                        result["unit_analysis"][col] = {
                            "median": median_value,
                            "max": max_value,
                            "likely_in_thousands": False
                        }
        
        return result
    
    def convert_units(self, df: pd.DataFrame, 
                     from_thousands: bool = True,
                     target_unit: str = "VND") -> pd.DataFrame:
        """Convert units in DataFrame.
        Chuyển đổi đơn vị trong DataFrame.
        
        Args:
            df: DataFrame to convert
            from_thousands: Whether to convert from thousands to base unit
            target_unit: Target unit (VND, USD, etc.)
            
        Returns:
            DataFrame with converted units
        """
        df_converted = df.copy()
        
        if from_thousands:
            # Convert from thousands VND to VND
            amount_cols = [col for col in self.UNIT_CONVERSION['amount_columns'] if col in df_converted.columns]
            
            for col in amount_cols:
                if col in df_converted.columns:
                    # Only convert if values seem to be in thousands
                    median_value = df_converted[col].dropna().median()
                    if median_value < self.unit_threshold:
                        df_converted[col] = df_converted[col] * 1000
                        logger.info(f"Converted {col} from thousands VND to VND")
        
        return df_converted
    
    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize DataFrame according to schema.
        Chuẩn hóa DataFrame theo schema.
        
        Args:
            df: DataFrame to standardize
            
        Returns:
            Standardized DataFrame
        """
        df_std = df.copy()
        
        # Ensure all required columns exist
        for col, dtype in self.schema.items():
            if col not in df_std.columns:
                if dtype == 'VARCHAR':
                    df_std[col] = ''
                elif dtype == 'INTEGER':
                    df_std[col] = 0
                elif dtype == 'DOUBLE':
                    df_std[col] = 0.0
                elif dtype == 'DATE':
                    df_std[col] = pd.NaT
        
        # Reorder columns according to schema
        df_std = df_std[list(self.schema.keys())]
        
        # Convert data types
        for col, dtype in self.schema.items():
            if col in df_std.columns:
                if dtype == 'VARCHAR':
                    df_std[col] = df_std[col].astype(str)
                elif dtype == 'INTEGER':
                    df_std[col] = pd.to_numeric(df_std[col], errors='coerce').astype('Int64')
                elif dtype == 'DOUBLE':
                    df_std[col] = pd.to_numeric(df_std[col], errors='coerce')
                elif dtype == 'DATE':
                    df_std[col] = pd.to_datetime(df_std[col], errors='coerce')
        
        # Clean symbol column
        if 'symbol' in df_std.columns:
            df_std['symbol'] = df_std['symbol'].astype(str).str.strip().str.upper()
        
        # Remove rows with invalid data
        df_std = df_std.dropna(subset=['symbol', 'report_date'])
        
        return df_std
    
    def validate_financial_relationships(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate financial statement relationships.
        Validate các mối quan hệ báo cáo tài chính.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with relationship validation results
        """
        result = {
            "is_valid": True,
            "violations": [],
            "warnings": []
        }
        
        if self.data_type == "bank":
            # Bank-specific validations
            if 'nii' in df.columns and 'toi' in df.columns:
                # NII should be part of TOI
                nii_greater_than_toi = df['nii'] > df['toi']
                if nii_greater_than_toi.any():
                    result["violations"].append("NII greater than TOI in some records")
            
            if 'pbt' in df.columns and 'npatmi' in df.columns:
                # PBT should be >= NPATMI (before tax >= after tax)
                pbt_less_than_npatmi = df['pbt'] < df['npatmi']
                if pbt_less_than_npatmi.any():
                    result["warnings"].append("PBT less than NPATMI in some records (unusual)")
        
        elif self.data_type == "company":
            # Company-specific validations
            if 'net_revenue' in df.columns and 'cogs' in df.columns and 'gross_profit' in df.columns:
                # Gross profit = Net revenue - COGS
                calculated_gross_profit = df['net_revenue'] - df['cogs']
                gross_profit_diff = abs(df['gross_profit'] - calculated_gross_profit)
                large_diffs = gross_profit_diff > 1000  # Allow for rounding differences
                if large_diffs.any():
                    result["violations"].append("Gross profit calculation mismatch in some records")
            
            if 'ebit' in df.columns and 'ebitda' in df.columns and 'depreciation' in df.columns:
                # EBITDA = EBIT + Depreciation
                calculated_ebitda = df['ebit'] + df['depreciation']
                ebitda_diff = abs(df['ebitda'] - calculated_ebitda)
                large_diffs = ebitda_diff > 1000
                if large_diffs.any():
                    result["violations"].append("EBITDA calculation mismatch in some records")
        
        return result
    
    def get_validation_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive validation summary.
        Lấy tóm tắt validation toàn diện.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with comprehensive validation results
        """
        schema_result = self.validate_schema(df)
        quality_result = self.validate_data_quality(df)
        unit_result = self.detect_unit_issues(df)
        relationship_result = self.validate_financial_relationships(df)
        
        return {
            "schema_validation": schema_result,
            "quality_validation": quality_result,
            "unit_analysis": unit_result,
            "relationship_validation": relationship_result,
            "overall_valid": all([
                schema_result["is_valid"],
                len(quality_result["anomalies"]) == 0,
                len(relationship_result["violations"]) == 0
            ])
        }
    
    def clean_and_standardize(self, df: pd.DataFrame, 
                            convert_units: bool = True) -> pd.DataFrame:
        """Clean and standardize DataFrame.
        Làm sạch và chuẩn hóa DataFrame.
        
        Args:
            df: DataFrame to clean and standardize
            convert_units: Whether to convert units
            
        Returns:
            Cleaned and standardized DataFrame
        """
        logger.info(f"Cleaning and standardizing {self.data_type} data: {len(df)} records")
        
        # Convert units if needed
        if convert_units:
            df = self.convert_units(df, from_thousands=True)
        
        # Standardize data
        df_std = self.standardize_data(df)
        
        # Remove duplicates
        df_std = df_std.drop_duplicates()
        
        logger.info(f"Cleaned data: {len(df_std)} records remaining")
        
        return df_std
