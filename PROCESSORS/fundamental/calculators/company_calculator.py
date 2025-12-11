#!/usr/bin/env python3
"""
Company Financial Calculator - Bộ tính toán tài chính cho Công ty
====================================================================

Phiên bản refactor sử dụng BaseFinancialCalculator để giảm trùng lặp code.
Thực hiện các tính toán đặc thù cho thực thể COMPANY.

Tính năng chính:
1. Kế thừa tất cả chức năng chung từ BaseFinancialCalculator
2. Thực hiện các tính toán đặc thù cho COMPANY
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
import logging

logger = logging.getLogger(__name__)
# Calculator implementation for standard companies (Manufacturing, Retail, etc.).
# Bộ tính toán cho các doanh nghiệp chuẩn (Sản xuất, Bán lẻ, v.v.).

class CompanyFinancialCalculator(BaseFinancialCalculator):
    """
    Bộ tính toán tài chính cho thực thể COMPANY.
    
    Kế thừa chức năng chung từ BaseFinancialCalculator và thực hiện
    các tính toán đặc thù cho COMPANY như báo cáo kết quả, biên lợi nhuận, tốc độ tăng trưởng, v.v.
    
    Financial calculator for standard companies.
    Bộ tính toán tài chính cho doanh nghiệp.
    
    Handles standard Income Statement, Balance Sheet, and Cash Flow
    metrics typical for non-financial institutions.
    Xử lý các chỉ số Báo cáo Kết quả Kinh doanh, Bảng Cân đối Kế toán
    và Lưu chuyển Tiền tệ điển hình cho các tổ chức phi tài chính.
    """
    
    def get_entity_type(self) -> str:
        """Return entity type for this calculator."""
        return "COMPANY"
    
    def get_metric_prefixes(self) -> List[str]:
        """Return metric code prefixes for COMPANY entities."""
        return ['CIS_', 'CBS_', 'CCFI_']
    
    def get_entity_specific_calculations(self) -> Dict[str, callable]:
        """Return COMPANY-specific calculation methods."""
        return {
            'income_statement': self.calculate_income_statement,
            'margins': self.calculate_margins,
            'growth_rates': self.calculate_growth_rates,
            'balance_sheet': self.calculate_balance_sheet,
            'cash_flow': self.calculate_cash_flow,
            'ratios': self.calculate_profitability_ratios,
            'ttm_metrics': self.calculate_ttm_metrics,
        }
    
    # ==================== COMPANY-SPECIFIC CALCULATIONS ====================
    
    def calculate_income_statement(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate income statement metrics for COMPANY entities.
        
        Args:
            df: Pivoted DataFrame with raw metrics
            
        Returns:
            DataFrame with income statement metrics calculated
        """
        result_df = df.copy()
        
        # Core Income Statement metrics (convert to billions VND)
        result_df['net_revenue'] = self.convert_to_billions(df.get('CIS_10', np.nan))
        result_df['cogs'] = self.convert_to_billions(df.get('CIS_11', np.nan))
        result_df['gross_profit'] = self.convert_to_billions(df.get('CIS_20', np.nan))
        
        # SG&A = CIS_25 + CIS_26 (selling + admin expenses)
        sga_sales = df.get('CIS_25', np.nan)
        sga_admin = df.get('CIS_26', np.nan)
        # Handle NaN values properly
        result_df['sga'] = self._safe_sum_expenses(sga_sales, sga_admin) / 1e9
        
        # EBIT = Gross Profit - SG&A
        result_df['ebit'] = result_df['gross_profit'] + result_df['sga']  # SGA is negative
        
        # Net Finance Income
        finance_income = df.get('CIS_21', 0)  # Revenue
        finance_cost = df.get('CIS_22', 0)     # Expense (typically negative)
        result_df['net_finance_income'] = (finance_income + finance_cost) / 1e9
        
        # EBT and NPATMI
        result_df['ebt'] = self.convert_to_billions(df.get('CIS_50', np.nan))
        result_df['npatmi'] = self.convert_to_billions(df.get('CIS_61', np.nan))
        
        # Depreciation & EBITDA
        result_df['depreciation'] = self.convert_to_billions(df.get('CCFI_2', np.nan))
        result_df['ebitda'] = result_df['ebit'] + result_df['depreciation']
        
        return result_df
    
    def calculate_margins(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate profitability margins for COMPANY entities.
        
        Args:
            df: DataFrame with income statement metrics
            
        Returns:
            DataFrame with margin metrics calculated
        """
        result_df = df.copy()
        
        # Avoid division by zero
        net_revenue = df['net_revenue'].replace(0, np.nan)
        
        # Calculate margins as percentages
        margin_calculations = {
            'gross_profit_margin': ('gross_profit', net_revenue),
            'ebit_margin': ('ebit', net_revenue),
            'ebitda_margin': ('ebitda', net_revenue),
            'net_margin': ('npatmi', net_revenue)
        }
        
        for margin_name, (numerator, denominator) in margin_calculations.items():
            result_df[margin_name] = self.safe_divide(
                numerator=df[numerator], 
                denominator=denominator, 
                result_nan=True
            ) * 100
        
        return result_df
    
    def calculate_growth_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate quarter-over-quarter growth rates for key metrics.
        
        Args:
            df: DataFrame with base metrics
            
        Returns:
            DataFrame with growth rate columns added
        """
        # Sort by ticker and date for correct growth calculation
        df = df.sort_values(['SECURITY_CODE', 'REPORT_DATE'])
        
        # Metrics to calculate growth for
        growth_metrics = [
            'net_revenue', 'gross_profit', 'ebit', 'ebitda', 'npatmi'
        ]
        
        # Calculate growth rates
        result_df = self.calculate_growth_rates(df, growth_metrics)
        
        return result_df
    
    def calculate_balance_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate balance sheet metrics for COMPANY entities.
        
        Args:
            df: Pivoted DataFrame with balance sheet codes
            
        Returns:
            DataFrame with balance sheet metrics calculated
        """
        result_df = df.copy()
        
        # Balance Sheet metrics (convert to billions VND)
        result_df['total_assets'] = self.convert_to_billions(df.get('CBS_270', np.nan))
        result_df['total_liabilities'] = self.convert_to_billions(df.get('CBS_300', np.nan))
        result_df['total_equity'] = self.convert_to_billions(df.get('CBS_400', np.nan))
        result_df['cash'] = self.convert_to_billions(df.get('CBS_110', np.nan))
        result_df['inventory'] = self.convert_to_billions(df.get('CBS_140', np.nan))
        result_df['account_receivable'] = self.convert_to_billions(df.get('CBS_130', np.nan))
        result_df['tangible_fixed_asset'] = self.convert_to_billions(df.get('CBS_221', np.nan))
        result_df['st_debt'] = self.convert_to_billions(df.get('CBS_320', np.nan))
        result_df['lt_debt'] = self.convert_to_billions(df.get('CBS_338', np.nan))
        result_df['common_shares'] = df.get('CBS_411A', np.nan)  # Not converted, used for EPS
        
        return result_df
    
    def calculate_cash_flow(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate cash flow metrics for COMPANY entities.
        
        Args:
            df: Pivoted DataFrame with cash flow codes
            
        Returns:
            DataFrame with cash flow metrics calculated
        """
        result_df = df.copy()
        
        # Cash Flow metrics (convert to billions VND)
        result_df['operating_cf'] = self.convert_to_billions(df.get('CCFI_20', np.nan))
        result_df['investment_cf'] = self.convert_to_billions(df.get('CCFI_30', np.nan))
        result_df['capex'] = self.convert_to_billions(df.get('CCFI_21', np.nan))
        result_df['financing_cf'] = self.convert_to_billions(df.get('CCFI_40', np.nan))
        result_df['fcf'] = self.convert_to_billions(df.get('CCFI_50', np.nan))
        
        return result_df
    
    def calculate_profitability_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate profitability ratios for COMPANY entities.
        
        Args:
            df: DataFrame with income statement and balance sheet metrics
            
        Returns:
            DataFrame with profitability ratios calculated
        """
        result_df = df.copy()
        
        # ROE = NPATMI / Total Equity
        result_df['roe'] = self.safe_divide(
            numerator=df['npatmi'] * 1e9,  # Convert back to VND
            denominator=df['total_equity'] * 1e9,
            result_nan=True
        ) * 100
        
        # ROA = NPATMI / Total Assets
        result_df['roa'] = self.safe_divide(
            numerator=df['npatmi'] * 1e9,  # Convert back to VND
            denominator=df['total_assets'] * 1e9,
            result_nan=True
        ) * 100
        
        # EPS = NPATMI (TTM) * 1e9 / (common_shares * 10,000)
        # First calculate TTM NPATMI if not already done
        if 'npatmi_ttm' not in df.columns:
            df = self.calculate_ttm(df, ['npatmi'])
        
        result_df['eps'] = self.safe_divide(
            numerator=df['npatmi_ttm'] * 1e9,
            denominator=df['common_shares'] * 10000,
            result_nan=True
        )
        
        return result_df
    
    def calculate_ttm_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate trailing twelve months (TTM) values for key metrics.
        
        Args:
            df: DataFrame with quarterly metrics
            
        Returns:
            DataFrame with TTM metrics calculated
        """
        # Metrics to calculate TTM for
        ttm_metrics = ['net_revenue', 'npatmi', 'operating_cf']
        
        # Calculate TTM
        result_df = self.calculate_ttm(df, ttm_metrics)
        
        return result_df
    
    # ==================== ENTITY-SPECIFIC HELPER METHODS ====================
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate data specific to COMPANY entities.
        
        Args:
            df: Pivoted DataFrame
            
        Returns:
            True if validation passes
        """
        # Call parent validation
        if not super().validate_data(df):
            return False
        
        # Check for COMPANY-specific metrics
        company_metrics = ['CIS_10', 'CBS_270', 'CBS_400']
        missing_metrics = [m for m in company_metrics if m not in df.columns]
        
        if missing_metrics:
            logger.warning(f"Missing COMPANY metrics: {missing_metrics}")
            # Don't fail validation, just warn
        
        return True
    
    def _safe_sum_expenses(self, expense1, expense2):
        """
        Safely sum two expense values, handling NaN values.
        
        Args:
            expense1: First expense value
            expense2: Second expense value
            
        Returns:
            Sum of expenses (negative values for expenses)
        """
        # Handle NaN values
        if pd.isna(expense1) and pd.isna(expense2):
            return np.nan
        if pd.isna(expense1):
            return expense2 if expense2 < 0 else -expense2  # Ensure expense is negative
        if pd.isna(expense2):
            return expense1 if expense1 < 0 else -expense1  # Ensure expense is negative
        
        # Ensure both are negative (expenses should be negative)
        exp1 = expense1 if expense1 < 0 else -expense1
        exp2 = expense2 if expense2 < 0 else -expense2
        
        return exp1 + exp2
    
    def postprocess_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Post-process COMPANY-specific results.
        
        Args:
            df: DataFrame with calculated metrics
            
        Returns:
            Post-processed DataFrame
        """
        # Call parent postprocessing
        df = super().postprocess_results(df)
        
        # Select and rename columns for COMPANY output
        company_cols = [
            # ID columns
            "SECURITY_CODE", "REPORT_DATE", "YEAR", "QUARTER", "FREQ_CODE",
            
            # Income Statement
            "net_revenue", "cogs", "gross_profit", "sga", "ebit",
            "net_finance_income", "ebt", "npatmi", "depreciation", "ebitda",
            
            # Margins
            "gross_profit_margin", "ebit_margin", "ebitda_margin", "net_margin",
            
            # Growth Rates
            "net_revenue_growth", "gross_profit_growth", "ebit_growth", 
            "ebitda_growth", "npatmi_growth",
            
            # Balance Sheet
            "total_assets", "total_liabilities", "total_equity", "cash",
            "inventory", "account_receivable", "tangible_fixed_asset",
            "st_debt", "lt_debt", "common_shares",
            
            # Cash Flow
            "operating_cf", "investment_cf", "capex", "financing_cf", "fcf",
            
            # TTM Metrics
            "net_revenue_ttm", "npatmi_ttm", "operating_cf_ttm",
            
            # Ratios
            "roe", "roa", "eps"
        ]
        
        # Filter available columns
        available_cols = [col for col in company_cols if col in df.columns]
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