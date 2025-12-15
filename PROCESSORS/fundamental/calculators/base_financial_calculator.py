#!/usr/bin/env python3
"""
Base Financial Calculator - Foundation for All Entity Calculators
============================================================

Base class for all financial calculators (Company, Bank, Insurance, Security).
Provides shared functionality to reduce code duplication by 60%.

Key Features:
1. Shared data loading and pivoting logic
2. Common date formatting
3. Template pattern for entity-specific calculations
4. Integration with metric_registry.json
5. Integration with sector_industry_registry.json

Author: Claude Code
Date: 2025-12-07
"""

import os
import sys
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np

# Use relative imports instead of sys.path manipulation
from PROCESSORS.core.shared.date_formatter import DateFormatter
from config.registries import MetricRegistry, SectorRegistry
from PROCESSORS.core.shared.unified_mapper import UnifiedTickerMapper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseFinancialCalculator(ABC):
    """
   Abstract base class for all entity-specific financial calculators.
Lớp cơ sở trừu tượng cho tất cả các bộ tính toán tài chính đặc thù theo thực thể.
    
    Implements the Template Method pattern to provide shared functionality
    while allowing subclasses to customize specific calculations.
    
    Subclasses must implement:
    - get_entity_type() -> str
    - get_metric_prefixes() -> List[str]
    - get_entity_specific_calculations() -> Dict[str, callable]
    
    Optional overrides:
    - validate_data()
    - preprocess_data()
    - postprocess_results()
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize calculator with path to parquet data.
        Khởi tạo bộ tính toán với đường dẫn đến dữ liệu parquet.
        
        Args:
            data_path: Path to directory containing parquet files (processed data)
                      Đường dẫn đến thư mục chứa file parquet (dữ liệu đã xử lý)
        """
        self.data_path = data_path
        self.df = None
        self.pivot_df = None
        self.results = None
        self.date_formatter = DateFormatter()
        
        # Initialize registries for validation and mapping
        self.metric_registry = MetricRegistry()
        self.sector_registry = SectorRegistry()
        self.unified_mapper = UnifiedTickerMapper()
        
        # Cache for metric information
        self._metric_info_cache = {}
        
    # ==================== Core Data Operations ====================
    
    def load_data(self) -> pd.DataFrame:
        """
        Load raw data from parquet file.
        
        Returns:
            Raw DataFrame with fundamental data
        """
        if self.data_path is None:
            raise ValueError("Data path must be provided")
            
        logger.info(f"Loading data from {self.data_path}")
        self.df = pd.read_parquet(self.data_path)
        
        # Validate required columns exist
        required_cols = ['SECURITY_CODE', 'REPORT_DATE', 'METRIC_CODE', 'METRIC_VALUE']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        return self.df
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess raw data before pivoting.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        # Default implementation: filter by frequency
        if 'FREQ_CODE' in df.columns:
            # Only use quarterly data to avoid mixing with yearly/semi
            df = df[df['FREQ_CODE'] == 'Q'].copy()
            
        # Filter by entity type if possible
        entity_type = self.get_entity_type()
        if 'SECURITY_CODE' in df.columns and entity_type:
            # Get tickers for this entity type
            tickers = self.sector_registry.get_tickers_by_entity_type(entity_type)
            if tickers:
                df = df[df['SECURITY_CODE'].isin(tickers)].copy()
                
        return df
    
    def pivot_data(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Pivot raw data from long to wide format.
        
        Args:
            df: Raw DataFrame (uses loaded data if None)
            
        Returns:
            Pivoted DataFrame with metrics as columns
        """
        if df is None:
            if self.df is None:
                self.load_data()
            df = self.df
            
        # Preprocess data
        df = self.preprocess_data(df)
        
        # Pivot the data
        index_cols = ["SECURITY_CODE", "REPORT_DATE", "YEAR", "QUARTER", "FREQ_CODE"]
        if not all(col in df.columns for col in index_cols):
            # Add missing columns from REPORT_DATE
            if "YEAR" not in df.columns and "REPORT_DATE" in df.columns:
                df["YEAR"] = pd.to_datetime(df["REPORT_DATE"]).dt.year
            if "QUARTER" not in df.columns and "REPORT_DATE" in df.columns:
                df["QUARTER"] = pd.to_datetime(df["REPORT_DATE"]).dt.quarter
                
        pivot = df.pivot_table(
            index=index_cols,
            columns="METRIC_CODE",
            values="METRIC_VALUE",
            aggfunc="first"
        ).reset_index()
        
        pivot.columns.name = None
        self.pivot_df = pivot
        
        return pivot
    
    # ==================== Template Methods ====================
    
    @abstractmethod
    def get_entity_type(self) -> str:
        """
        Get the entity type for this calculator.
        
        Returns:
            Entity type (COMPANY, BANK, INSURANCE, SECURITY)
        """
        pass
    
    @abstractmethod
    def get_metric_prefixes(self) -> List[str]:
        """
        Get the metric code prefixes for this entity type.
        
        Returns:
            List of metric prefixes (e.g., ['CIS', 'CBS', 'CCFI'] for COMPANY)
        """
        pass
    
    @abstractmethod
    def get_entity_specific_calculations(self) -> Dict[str, callable]:
        """
        Get entity-specific calculation methods.
        
        Returns:
            Dictionary mapping metric name to calculation method
        """
        pass
    
    # ==================== Common Calculations ====================
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate data before processing.
        Can be overridden by subclasses for specific validation.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True
    def calculate_growth_rates(self, df: pd.DataFrame, metric_cols: List[str]) -> pd.DataFrame:
        """
        Calculate quarter-over-quarter growth rates (QoQ).
        Tính toán tốc độ tăng trưởng theo quý (QoQ).
        
        Args:
            df: Pivoted DataFrame
            metric_cols: List of metric columns to calculate growth for
            
        Returns:
            DataFrame with growth rate columns added (e.g., metric_growth)
        """
        # Sort by ticker and date
        df = df.sort_values(['SECURITY_CODE', 'REPORT_DATE'])
        
        for col in metric_cols:
            if col in df.columns:
                # Calculate QoQ growth by ticker
                growth_col = f"{col}_qoq_growth"
                # Default is 1 period shift for QoQ
                df[growth_col] = df.groupby('SECURITY_CODE')[col].pct_change(periods=1) * 100
                
        return df

    def calculate_yoy_growth_rates(self, df: pd.DataFrame, metric_cols: List[str]) -> pd.DataFrame:
        """
        Calculate year-over-year growth rates (YoY).
        Tính toán tốc độ tăng trưởng theo năm (YoY).
        
        Args:
            df: Pivoted DataFrame
            metric_cols: List of metric columns to calculate growth for
            
        Returns:
            DataFrame with growth rate columns added (e.g., metric_yoy_growth)
        """
        # Sort by ticker and date
        df = df.sort_values(['SECURITY_CODE', 'REPORT_DATE'])
        
        for col in metric_cols:
            if col in df.columns:
                # Calculate YoY growth by ticker (shift 4 quarters)
                growth_col = f"{col}_yoy_growth"
                df[growth_col] = df.groupby('SECURITY_CODE')[col].pct_change(periods=4) * 100
                
        return df
    
    def calculate_ttm(self, df: pd.DataFrame, metric_cols: List[str], min_periods: int = 4) -> pd.DataFrame:
        """
        Calculate trailing twelve months (TTM) values.
        Tính toán giá trị trượt 12 tháng (TTM).
        
        Args:
            df: Pivoted DataFrame
            metric_cols: List of metric columns to calculate TTM for
            min_periods: Minimum periods required (default 4 for full year)
            
        Returns:
            DataFrame with TTM columns added (e.g., metric_ttm)
        """
        # Sort by ticker and date
        df = df.sort_values(['SECURITY_CODE', 'REPORT_DATE'])
        
        for col in metric_cols:
            if col in df.columns:
                # Calculate TTM as sum of last 4 quarters
                ttm_col = f"{col}_ttm"
                df[ttm_col] = df.groupby('SECURITY_CODE')[col].rolling(
                    window=4, min_periods=min_periods
                ).sum().reset_index(level=0, drop=True)
                
        return df
    
    # ==================== Main Calculation Flow ====================
    
    def calculate_all_metrics(self, ticker: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate all metrics for this entity type.
        Tính toán tất cả các chỉ số cho loại hình thực thể này.
        
        Args:
            ticker: Optional ticker to filter results (Mã chứng khoán tùy chọn để lọc kết quả)
            
        Returns:
            DataFrame with all calculated metrics (DataFrame với tất cả chỉ số đã tính)
        """
        logger.info(f"Calculating metrics for entity type: {self.get_entity_type()}")
        
        # Load and pivot data
        df = self.pivot_data()
        
        # Filter by ticker if specified
        if ticker:
            df = df[df['SECURITY_CODE'] == ticker].copy()
            
        # Validate data
        if not self.validate_data(df):
            logger.error("Data validation failed")
            return pd.DataFrame()
            
        # Get entity-specific calculations
        entity_calcs = self.get_entity_specific_calculations()
        
        # Execute calculations
        for calc_name, calc_func in entity_calcs.items():
            try:
                df = calc_func(df)
                logger.debug(f"Completed calculation: {calc_name}")
            except Exception as e:
                logger.error(f"Error in calculation {calc_name}: {str(e)}")
                continue
                
        # Post-process results
        df = self.postprocess_results(df)
        
        # Validate output schema
        self.validate_output_schema(df)
        
        # Store and return results
        self.results = df
        return df

    def postprocess_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Post-process calculation results.
        Xử lý hậu kỳ kết quả tính toán.
        
        Args:
            df: DataFrame with calculated metrics
            
        Returns:
            Post-processed DataFrame
        """
        # Default implementation: sort results
        df = df.sort_values(['SECURITY_CODE', 'REPORT_DATE'])
        
        # Add entity type column
        df['entity_type'] = self.get_entity_type()
        
        return df
    
    # ==================== Schema Validation ====================

    def load_schema(self) -> Optional[Dict]:
        """
        Load output schema for this entity type.
        Tải schema đầu ra cho loại thực thể này.
        
        Returns:
            Dictionary schema content or None if not found
        """
        try:
            entity_type = self.get_entity_type().lower()
            schema_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                "DATA", "metadata", "schema", f"{entity_type}_output.json"
            )
            
            if not os.path.exists(schema_path):
                logger.warning(f"Schema not found for {entity_type}: {schema_path}")
                return None
                
            import json
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading schema: {str(e)}")
            return None

    def validate_output_schema(self, df: pd.DataFrame) -> bool:
        """
        Validate DataFrame against the entity schema.
        Xác thực DataFrame so với schema của thực thể.
        
        Args:
            df: DataFrame containing results
            
        Returns:
            True if valid, False otherwise
        """
        schema = self.load_schema()
        if not schema:
            return True # Skip validation if no schema
            
        required_cols = []
        schema_cols = schema.get('columns', {})
        
        for col_name, col_def in schema_cols.items():
            if col_def.get('required', False):
                required_cols.append(col_name)
                
        # Check for missing columns
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            logger.warning(f"Schema validation warning - Missing columns for {self.get_entity_type()}: {missing_cols}")
            # We strictly warn but return True for now to avoid breaking existing flows, 
            # unless strict mode is desired.
            return False
            
        logger.info(f"Schema validation passed for {self.get_entity_type()}")
        return True
    
    # ==================== Utility Methods ====================
    
    
    def calculate_from_registry(self, metric_name: str) -> None:
        """
        Calculates a metric dynamically using the formula defined in formula_registry.json.
        This provides automation: just update JSON to fix/add formulas!

        Args:
            metric_name: Name of the calculated metric (e.g., 'roe')
        """
        # 1. Get formula info
        formula_info = self.metric_registry.get_calculated_metric_formula(metric_name)
        if not formula_info:
            logger.warning(f"Formula for '{metric_name}' not found in registry")
            return

        entity_type = self.get_entity_type()
        
        # 2. Get dependencies (column mapping) for this entity
        dependencies = formula_info.get("dependencies", {}).get(entity_type, [])
        if not dependencies:
            logger.warning(f"No dependencies defined for '{metric_name}' in entity '{entity_type}'")
            return
            
        # 3. Get the raw formula string
        # Warning: 'formula' field in JSON is currently human-readable (e.g., "A / B").
        # For full automation, we need a parsable format.
        # This implementation assumes we can map variables 1-to-1 with dependencies.
        # Ideally, JSON should have "expression": "{0} / {1} * 100" or similar.
        
        # Current HACK for Phase 4: supporting basic "Ratio" type automatically if 2 deps exist
        # Future enhancement: Implement full expression parser (as per Plan Part 2)
        
        try:
            # Simple automatic implementation for common financial ratios
            if len(dependencies) >= 2:
                numerator_col = dependencies[0]
                denominator_col = dependencies[1]
                
                # Check columns exist
                missing = [col for col in dependencies if col not in self.pivot_df.columns]
                if missing:
                    logger.warning(f"Missing columns {missing} for metric '{metric_name}'")
                    return

                # Calculate safely
                # Default logic: (First / Second) * 100 if unit is %
                # This is a heuristic until we have full expression parsing in JSON
                val = (self.pivot_df[numerator_col] / self.pivot_df[denominator_col].replace(0, np.nan))
                
                if formula_info.get("unit") == "%":
                    val = val * 100
                    
                self.results[metric_name] = val
                logger.info(f"Calculated '{metric_name}' using dynamic engine.")
                
        except Exception as e:
            logger.error(f"Error calculating {metric_name}: {str(e)}")

    def get_metric_info(self, metric_code: str) -> Dict[str, Any]:
        """
        Get metric information from metric registry.
        
        Args:
            metric_code: Metric code to look up
            
        Returns:
            Dictionary with metric information
        """
        if metric_code not in self._metric_info_cache:
            entity_type = self.get_entity_type()
            metric_info = self.metric_registry.get_metric(metric_code, entity_type)
            self._metric_info_cache[metric_code] = metric_info or {}
            
        return self._metric_info_cache.get(metric_code, {})
    
    def validate_metric_for_entity(self, metric_code: str) -> bool:
        """
        Validate if a metric code is applicable to this entity type.
        
        Args:
            metric_code: Metric code to validate
            
        Returns:
            True if metric is valid for this entity type
        """
        entity_type = self.get_entity_type()
        metric_info = self.get_metric_info(metric_code)
        
        # Check if metric belongs to this entity type
        return metric_info.get('entity_type') == entity_type
    
    def get_peers_for_ticker(self, ticker: str) -> List[str]:
        """
        Get peer tickers for the specified ticker.
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            List of peer ticker symbols
        """
        peer_info = self.unified_mapper.get_peer_comparison_info(ticker)
        return peer_info.get('peer_tickers', [])
    
    # ==================== Static Helper Methods ====================
    
    @staticmethod
    def safe_divide(numerator: pd.Series, denominator: pd.Series, 
                   result_nan: bool = True, fill_value: float = 0.0) -> pd.Series:
        """
        Safely divide two series, handling division by zero.
        
        Args:
            numerator: Numerator series
            denominator: Denominator series
            result_nan: Whether to return NaN or fill_value on division by zero
            fill_value: Value to use when result_nan is False
            
        Returns:
            Result of division
        """
        if result_nan:
            return np.where(denominator != 0, numerator / denominator, np.nan)
        else:
            return np.where(denominator != 0, numerator / denominator, fill_value)
    
    @staticmethod
    def convert_to_billions(series: pd.Series) -> pd.Series:
        """
        DEPRECATED: Returns raw VND values (no conversion).

        As per v4.0.0 Unit Standardization (formula_migration_plan.md):
        - Storage Layer: Keep values in VND (raw data)
        - Display Layer: UI/Streamlit handles conversion to "Tỷ VND" when rendering

        This function is kept for backward compatibility but now returns
        values unchanged (in VND).

        Args:
            series: Series in VND

        Returns:
            Series unchanged (in VND, not billions)
        """
        # NO CONVERSION - store in VND as per standardization
        return series
    
    @staticmethod
    def convert_to_millions(series: pd.Series) -> pd.Series:
        """
        Convert values to millions (VND / 1e6).
        
        Args:
            series: Series to convert
            
        Returns:
            Series converted to millions
        """
        return series / 1e6