#!/usr/bin/env python3
"""
Insurance Financial Calculator - Bộ tính toán tài chính cho Bảo hiểm
======================================================================

Phiên bản refactor sử dụng BaseFinancialCalculator để giảm trùng lặp code.
Thực hiện các tính toán đặc thù cho thực thể INSURANCE.

Tính năng chính:
1. Kế thừa tất cả chức năng chung từ BaseFinancialCalculator
2. Thực hiện các tính toán đặc thù cho INSURANCE
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
from PROCESSORS.fundamental.formulas.registry import formula_registry
import logging

logger = logging.getLogger(__name__)

class InsuranceFinancialCalculator(BaseFinancialCalculator):
    """
    Financial calculator for insurance companies.
    Bộ tính toán tài chính cho công ty bảo hiểm.
    
    Handles specific metrics for insurance such as Combined Ratio,
    Loss Ratio, and investment performance from premiums.
    Xử lý các chỉ số đặc thù cho bảo hiểm như Tỷ lệ Kết hợp,
    Tỷ lệ Bồi thường, và hiệu quả đầu tư từ phí bảo hiểm.
    """
    
    def get_entity_type(self) -> str:
        """Return entity type for this calculator."""
        return "INSURANCE"
    
    def get_metric_prefixes(self) -> List[str]:
        """Return metric code prefixes for INSURANCE entities."""
        return ['IIS_', 'IBS_']
    
    def get_entity_specific_calculations(self) -> Dict[str, callable]:
        """Return INSURANCE-specific calculation methods."""
        return {
            'components': self.calculate_basic_components,
            'profitability': self.calculate_profitability,
            'underwriting': self.calculate_underwriting_ratios,
            'investment': self.calculate_investment_performance,
            'solvency': self.calculate_solvency_ratios,
            'growth': self.calculate_growth_rates,
            'ttm': self.calculate_ttm_metrics
        }
    
    def calculate_growth_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate growth rates for Insurance metrics.
        Tính toán tốc độ tăng trưởng cho Bảo hiểm.
        """
        # Key metrics for Insurance
        growth_metrics = [
            'net_profit', 'total_revenue', 'technical_reserves', 'investment_income'
        ]
        
        # Calculate QoQ growth
        df = super().calculate_growth_rates(df, growth_metrics)
        
        # Calculate YoY growth
        df = super().calculate_yoy_growth_rates(df, growth_metrics)
        
        return df

    def calculate_ttm_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate TTM metrics for Insurance.
        Tính toán các chỉ số TTM cho Bảo hiểm.
        """
        # Key metrics for TTM
        ttm_metrics = [
            'net_profit', 'total_revenue', 'investment_income'
        ]
        
        # Calculate TTM
        df = super().calculate_ttm(df, ttm_metrics)
        
        return df
    
    # ==================== INSURANCE-SPECIFIC CALCULATIONS ====================
    
    def calculate_basic_components(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate basic components for INSURANCE entities.
        
        Args:
            df: Pivoted DataFrame with raw metrics
            
        Returns:
            DataFrame with component metrics calculated
        """
        result_df = df.copy()
        
        # Basic components (convert to billions VND)
        result_df['net_profit'] = self.convert_to_billions(df.get('IIS_20', np.nan))
        result_df['total_revenue'] = self.convert_to_billions(df.get('IIS_1', np.nan))
        result_df['technical_reserves'] = self.convert_to_billions(df.get('IIS_3', np.nan))
        result_df['investment_income'] = self.convert_to_billions(df.get('IIS_6', np.nan))
        
        # Balance sheet components
        result_df['total_assets'] = self.convert_to_billions(df.get('IBS_18', np.nan))
        result_df['equity'] = self.convert_to_billions(df.get('IBS_36', np.nan))
        result_df['liabilities'] = self.convert_to_billions(df.get('IBS_19', np.nan))
        
        return result_df
    
    def calculate_profitability(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate profitability ratios for INSURANCE entities.
        
        Args:
            df: DataFrame with basic components
            
        Returns:
            DataFrame with profitability ratios calculated
        """
        result_df = df.copy()
        
        # Get formulas
        calc_roe = formula_registry.get_formula('calculate_roe')
        calc_roa = formula_registry.get_formula('calculate_roa')
        
        # ROE = Net Profit / Equity
        if calc_roe:
            result_df['roe'] = df.apply(
                lambda row: calc_roe(row.get('IIS_20', 0), row.get('IBS_36', 1)),
                axis=1
            )
        else:
            result_df['roe'] = self.safe_divide(
                numerator=df.get('IIS_20', 0),
                denominator=df.get('IBS_36', 1),
                result_nan=True
            ) * 100
        
        # ROA = Net Profit / Total Assets
        if calc_roa:
             result_df['roa'] = df.apply(
                lambda row: calc_roa(row.get('IIS_20', 0), row.get('IBS_18', 1)),
                axis=1
            )
        else:
            result_df['roa'] = self.safe_divide(
                numerator=df.get('IIS_20', 0),
                denominator=df.get('IBS_18', 1),
                result_nan=True
            ) * 100
        
        # Profit Margin = Net Profit / Total Revenue
        result_df['profit_margin'] = self.safe_divide(
            numerator=df.get('IIS_20', 0),
            denominator=df.get('IIS_1', 1),
            result_nan=True
        ) * 100
        
        return result_df
    
    def calculate_underwriting_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate underwriting ratios for INSURANCE entities.
        
        Args:
            df: DataFrame with basic components
            
        Returns:
            DataFrame with underwriting ratios calculated
        """
        result_df = df.copy()
        
        # Loss Ratio = Claims / Premiums
        loss_ratio = self.safe_divide(
            numerator=df.get('IIS_9', 0),
            denominator=df.get('IIS_1', 1),
            result_nan=True
        ) * 100
        
        # Expense Ratio = Expenses / Premiums
        expense_ratio = self.safe_divide(
            numerator=df.get('IIS_15', 0),
            denominator=df.get('IIS_1', 1),
            result_nan=True
        ) * 100
        
        # Combined Ratio = Loss Ratio + Expense Ratio
        result_df['combined_ratio'] = loss_ratio + expense_ratio
        result_df['loss_ratio'] = loss_ratio
        result_df['expense_ratio'] = expense_ratio
        
        # Retention Ratio = Technical Reserves / Premiums
        result_df['retention_ratio'] = self.safe_divide(
            numerator=df.get('IIS_3', 0),
            denominator=df.get('IIS_1', 1),
            result_nan=True
        ) * 100
        
        return result_df
    
    def calculate_investment_performance(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate investment performance for INSURANCE entities.
        
        Args:
            df: DataFrame with basic components
            
        Returns:
            DataFrame with investment performance metrics calculated
        """
        result_df = df.copy()
        
        # Investment Yield = Investment Income / Investments
        # Use IBS_8 for Investments if available
        result_df['investment_yield'] = self.safe_divide(
            numerator=df.get('IIS_6', 0),
            denominator=df.get('IBS_8', 1),
            result_nan=True
        ) * 100
        
        # Investment Ratio = Investment Income / Total Revenue
        total_revenue = df.get('IIS_1', 0) + df.get('IIS_6', 0)
        result_df['investment_ratio'] = self.safe_divide(
            numerator=df.get('IIS_6', 0),
            denominator=total_revenue,
            result_nan=True
        ) * 100
        
        return result_df
    
    def calculate_solvency_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate solvency and capital ratios for INSURANCE entities.
        
        Args:
            df: DataFrame with basic components
            
        Returns:
            DataFrame with solvency ratios calculated
        """
        result_df = df.copy()
        
        # Solvency Ratio = Equity / (Total Assets * 0.2)
        # Using 20% of total assets as minimum required capital
        result_df['solvency_ratio'] = self.safe_divide(
            numerator=df.get('IBS_36', 0),
            denominator=df.get('IBS_18', 1) * 0.2,
            result_nan=True
        ) * 100
        
        # Capital Adequacy = Equity / Total Assets
        result_df['capital_adequacy'] = self.safe_divide(
            numerator=df.get('IBS_36', 0),
            denominator=df.get('IBS_18', 1),
            result_nan=True
        ) * 100
        
        # Leverage Ratio = Liabilities / Equity
        result_df['leverage_ratio'] = self.safe_divide(
            numerator=df.get('IBS_19', 0),
            denominator=df.get('IBS_36', 1),
            result_nan=True
        )
        
        return result_df
    
    # ==================== ENTITY-SPECIFIC HELPER METHODS ====================
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate data specific to INSURANCE entities.
        
        Args:
            df: Pivoted DataFrame
            
        Returns:
            True if validation passes
        """
        # Call parent validation
        if not super().validate_data(df):
            return False
        
        # Check for INSURANCE-specific metrics
        insurance_metrics = ['IIS_1', 'IBS_18', 'IBS_36']
        missing_metrics = [m for m in insurance_metrics if m not in df.columns]
        
        if missing_metrics:
            logger.warning(f"Missing INSURANCE metrics: {missing_metrics}")
            # Don't fail validation, just warn
        
        return True
    
    def postprocess_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Post-process INSURANCE-specific results.
        
        Args:
            df: DataFrame with calculated metrics
            
        Returns:
            Post-processed DataFrame
        """
        # Call parent postprocessing
        df = super().postprocess_results(df)
        
        # Select and rename columns for INSURANCE output
        insurance_cols = [
            # ID columns
            "SECURITY_CODE", "REPORT_DATE", "YEAR", "QUARTER", "FREQ_CODE",
            
            # Basic components
            "net_profit", "total_revenue", "technical_reserves", "investment_income",
            "total_assets", "equity", "liabilities",
            
            # Profitability
            "roe", "roa", "profit_margin",
            
            # Underwriting
            "combined_ratio", "loss_ratio", "expense_ratio", "retention_ratio",
            
            # Investment
            "investment_yield", "investment_ratio",
            
            # Solvency
            "solvency_ratio", "capital_adequacy", "leverage_ratio"
        ]
        
        # Filter available columns
        available_cols = [col for col in insurance_cols if col in df.columns]
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