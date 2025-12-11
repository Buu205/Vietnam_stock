#!/usr/bin/env python3
"""
Security Financial Calculator - Bộ tính toán tài chính cho Chứng khoán
========================================================================

Phiên bản refactor sử dụng BaseFinancialCalculator để giảm trùng lặp code.
Thực hiện các tính toán đặc thù cho thực thể SECURITY.

Tính năng chính:
1. Kế thừa tất cả chức năng chung từ BaseFinancialCalculator
2. Thực hiện các tính toán đặc thù cho SECURITY
3. Sử dụng metric_registry.json để validation
4. Tích hợp với UnifiedTickerMapper

Tác giả: Claude Code
Ngày: 2025-12-07
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import os

# Use relative imports instead of sys.path manipulation
from PROCESSORS.fundamental.calculators.base_financial_calculator import BaseFinancialCalculator

class SecurityFinancialCalculator(BaseFinancialCalculator):
    """
    Bộ tính toán tài chính cho thực thể SECURITY.
    
    Kế thừa chức năng chung từ BaseFinancialCalculator và thực hiện
    các tính toán đặc thù cho SECURITY.
    Financial calculator for securities companies.
    Bộ tính toán tài chính cho công ty chứng khoán.
    
    Handles specific metrics for securities firms such as Brokerage revenue,
    Margin Lending, Proprietary Trading, and specialized risk metrics.
    Xử lý các chỉ số đặc thù cho công ty chứng khoán như Doanh thu môi giới,
    Cho vay ký quỹ (Margin), Tự doanh, và các chỉ số rủi ro chuyên biệt.
    """
    
    def get_entity_type(self) -> str:
        """Return entity type for this calculator."""
        return "SECURITY"
    
    def get_metric_prefixes(self) -> List[str]:
        """Return metric code prefixes for SECURITY entities."""
        return ['SIS_', 'SBS_']
    
    def get_entity_specific_calculations(self) -> Dict[str, callable]:
        """Return SECURITY-specific calculation methods."""
        return {
            'profitability': self.calculate_profitability,
            'revenue_composition': self.calculate_revenue_composition,
            'efficiency': self.calculate_efficiency,
            'risk_metrics': self.calculate_risk_metrics,
            'capital_adequacy': self.calculate_capital_adequacy,
            'components': self.calculate_basic_components,
        }
    
    # ==================== SECURITY-SPECIFIC CALCULATIONS ====================
    
    def calculate_basic_components(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate basic components for SECURITY entities.
        
        Args:
            df: Pivoted DataFrame with raw metrics
            
        Returns:
            DataFrame with component metrics calculated
        """
        result_df = df.copy()
        
        # Basic components (convert to billions VND)
        result_df['net_profit'] = self.convert_to_billions(df.get('SIS_37', np.nan))
        result_df['total_revenue'] = self.convert_to_billions(df.get('SIS_1', np.nan))
        
        # Balance sheet components
        result_df['total_assets'] = self.convert_to_billions(df.get('SBS_39', np.nan))
        result_df['equity'] = self.convert_to_billions(df.get('SBS_65', np.nan))
        result_df['cash'] = self.convert_to_billions(df.get('SBS_1', np.nan))
        result_df['liabilities'] = self.convert_to_billions(df.get('SBS_40', np.nan))
        
        return result_df
    
    def calculate_profitability(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate profitability ratios for SECURITY entities.
        
        Args:
            df: DataFrame with basic components
            
        Returns:
            DataFrame with profitability ratios calculated
        """
        result_df = df.copy()
        
        # ROE = Net Profit / Equity
        result_df['roe'] = self.safe_divide(
            numerator=df.get('SIS_37', 0),
            denominator=df.get('SBS_65', 1),
            result_nan=True
        ) * 100
        
        # ROA = Net Profit / Total Assets
        result_df['roa'] = self.safe_divide(
            numerator=df.get('SIS_37', 0),
            denominator=df.get('SBS_39', 1),
            result_nan=True
        ) * 100
        
        # Profit Margin = Net Profit / Total Revenue
        result_df['profit_margin'] = self.safe_divide(
            numerator=df.get('SIS_37', 0),
            denominator=df.get('SIS_1', 1),
            result_nan=True
        ) * 100
        
        return result_df
    
    def calculate_revenue_composition(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate revenue composition for SECURITY entities.
        
        Args:
            df: DataFrame with basic components
            
        Returns:
            DataFrame with revenue composition ratios calculated
        """
        result_df = df.copy()
        
        # Proprietary Trading Ratio = Trading Income / Total Revenue
        result_df['prop_trading_ratio'] = self.safe_divide(
            numerator=df.get('SIS_2', 0),
            denominator=df.get('SIS_1', 1),
            result_nan=True
        ) * 100
        
        # Brokerage Ratio = Brokerage Income / Total Revenue
        result_df['brokerage_ratio'] = self.safe_divide(
            numerator=df.get('SIS_10', 0),
            denominator=df.get('SIS_1', 1),
            result_nan=True
        ) * 100
        
        # Advisory Ratio = Advisory Income / Total Revenue
        result_df['advisory_ratio'] = self.safe_divide(
            numerator=df.get('SIS_13', 0),
            denominator=df.get('SIS_1', 1),
            result_nan=True
        ) * 100
        
        # Margin Lending Ratio = Lending Income / Total Revenue
        result_df['margin_lending_ratio'] = self.safe_divide(
            numerator=df.get('SIS_16', 0),
            denominator=df.get('SIS_1', 1),
            result_nan=True
        ) * 100
        
        return result_df
    
    def calculate_efficiency(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate efficiency ratios for SECURITY entities.
        
        Args:
            df: DataFrame with basic components
            
        Returns:
            DataFrame with efficiency ratios calculated
        """
        result_df = df.copy()
        
        # Cost to Income Ratio = Costs / Total Revenue
        result_df['cost_income'] = self.safe_divide(
            numerator=df.get('SIS_24', 0),
            denominator=df.get('SIS_1', 1),
            result_nan=True
        ) * 100
        
        # Operating Expense Ratio = Opex / Total Revenue
        result_df['opex_ratio'] = self.safe_divide(
            numerator=df.get('SIS_27', 0),
            denominator=df.get('SIS_1', 1),
            result_nan=True
        ) * 100
        
        return result_df
    
    def calculate_risk_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculator implementation for securities companies.
Bộ tính toán cho các công ty chứng khoán.
        
        Args:
            df: DataFrame with basic components
            
        Returns:
            DataFrame with risk metrics calculated
        """
        result_df = df.copy()
        
        # Leverage Ratio = Liabilities / Equity
        result_df['leverage_ratio'] = self.safe_divide(
            numerator=df.get('SBS_40', 0),
            denominator=df.get('SBS_65', 1),
            result_nan=True
        )
        
        # Liquidity Ratio = Cash / Liabilities
        result_df['liquid_ratio'] = self.safe_divide(
            numerator=df.get('SBS_1', 0),
            denominator=df.get('SBS_41', 1),
            result_nan=True
        )
        
        return result_df
    
    def calculate_capital_adequacy(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate capital adequacy ratios for SECURITY entities.
        
        Args:
            df: DataFrame with basic components
            
        Returns:
            DataFrame with capital adequacy ratios calculated
        """
        result_df = df.copy()
        
        # Capital Ratio = Equity / Total Assets
        result_df['capital_ratio'] = self.safe_divide(
            numerator=df.get('SBS_65', 0),
            denominator=df.get('SBS_39', 1),
            result_nan=True
        ) * 100
        
        return result_df
    
    # ==================== ENTITY-SPECIFIC HELPER METHODS ====================
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate data specific to SECURITY entities.
        
        Args:
            df: Pivoted DataFrame
            
        Returns:
            True if validation passes
        """
        # Call parent validation
        if not super().validate_data(df):
            return False
        
        # Check for SECURITY-specific metrics
        security_metrics = ['SIS_1', 'SBS_39', 'SBS_65']
        missing_metrics = [m for m in security_metrics if m not in df.columns]
        
        if missing_metrics:
            logger.warning(f"Missing SECURITY metrics: {missing_metrics}")
            # Don't fail validation, just warn
        
        return True
    
    def postprocess_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Post-process SECURITY-specific results.
        
        Args:
            df: DataFrame with calculated metrics
            
        Returns:
            Post-processed DataFrame
        """
        # Call parent postprocessing
        df = super().postprocess_results(df)
        
        # Select and rename columns for SECURITY output
        security_cols = [
            # ID columns
            "SECURITY_CODE", "REPORT_DATE", "YEAR", "QUARTER", "FREQ_CODE",
            
            # Basic components
            "net_profit", "total_revenue",
            "total_assets", "equity", "cash", "liabilities",
            
            # Profitability
            "roe", "roa", "profit_margin",
            
            # Revenue composition
            "prop_trading_ratio", "brokerage_ratio", "advisory_ratio", "margin_lending_ratio",
            
            # Efficiency
            "cost_income", "opex_ratio",
            
            # Risk metrics
            "leverage_ratio", "liquid_ratio",
            
            # Capital adequacy
            "capital_ratio"
        ]
        
        # Filter available columns
        available_cols = [col for col in security_cols if col in df.columns]
        result = df[available_cols].copy()
        
        # Rename columns to more readable names
        rename_dict = {
            "SECURITY_CODE": "symbol",
            "REPORT_DATE": "report_date",
            "YEAR": "year",
            "QUARTER": "quarter",
            "FREQ_CODE": "freq_code"
        }
        
        result = result.rename(columns=rename_dict)
        
        # Standardize date format
        if 'report_date' in result.columns:
            result['report_date'] = pd.to_datetime(result['report_date']).dt.strftime('%Y-%m-%d')
        
        return result