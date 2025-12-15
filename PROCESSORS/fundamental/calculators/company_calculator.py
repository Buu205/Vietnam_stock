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
5. [Phase 3] Tích hợp Schema Validation (cập nhật 2025-12-11)

Tác giả: Claude Code
Ngày: 2025-12-07
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import os

# Use relative imports instead of sys.path manipulation
from PROCESSORS.fundamental.calculators.base_financial_calculator import BaseFinancialCalculator
from PROCESSORS.fundamental.calculators.base_financial_calculator import BaseFinancialCalculator
from PROCESSORS.fundamental.formulas.registry import formula_registry
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
            'balance_sheet': self.calculate_balance_sheet,
            'cash_flow': self.calculate_cash_flow,
            'profitability': self.calculate_profitability_ratios,
            'liquidity': self.calculate_liquidity_ratios,
            'solvency': self.calculate_solvency_ratios,
            'activity': self.calculate_activity_ratios,
            'margins': self.calculate_margins,
            'growth': self.calculate_growth_rates,
            'ttm': self.calculate_ttm_metrics,
            'valuation': self.calculate_valuation_ratios,
            'free_cash_flow': self.calculate_free_cash_flow
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

        # Core Income Statement metrics (stored in VND as per v4.0.0 standard)
        # Display layer will handle conversion to billions
        result_df['net_revenue'] = df.get('CIS_10', np.nan)
        result_df['cogs'] = df.get('CIS_11', np.nan)
        result_df['gross_profit'] = df.get('CIS_20', np.nan)

        # SG&A = CIS_25 + CIS_26 (selling + admin expenses)
        sga_sales = df.get('CIS_25', np.nan)
        sga_admin = df.get('CIS_26', np.nan)
        # Handle NaN values properly
        result_df['sga'] = self._safe_sum_expenses(sga_sales, sga_admin)
        
        # EBIT = Gross Profit - SG&A
        result_df['ebit'] = result_df['gross_profit'] + result_df['sga']  # SGA is negative
        
        # Net Finance Income (stored in VND)
        finance_income = df.get('CIS_21', 0)  # Revenue
        finance_cost = df.get('CIS_22', 0)     # Expense (typically negative)
        result_df['net_finance_income'] = (finance_income + finance_cost)
        
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
        
        # Get formulas from registry
        calc_gross_margin = formula_registry.get_formula('calculate_gross_margin')
        calc_net_margin = formula_registry.get_formula('calculate_net_margin')
        
        # Use formula functions
        if calc_gross_margin:
            result_df['gross_profit_margin'] = df.apply(
                lambda row: calc_gross_margin(row['gross_profit'], row['net_revenue']),
                axis=1
            )
            result_df['ebit_margin'] = df.apply(
                lambda row: calc_gross_margin(row['ebit'], row['net_revenue']),
                axis=1
            )
            result_df['ebitda_margin'] = df.apply(
                lambda row: calc_gross_margin(row['ebitda'], row['net_revenue']),
                axis=1
            )
        
        if calc_net_margin:
            result_df['net_margin'] = df.apply(
                lambda row: calc_net_margin(row['npatmi'], row['net_revenue']),
                axis=1
            )
        
        return result_df
    
    def calculate_growth_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate growth rates for key metrics.
        Tính toán tốc độ tăng trưởng cho các chỉ số chính.
        
        Args:
            df: Pivoted DataFrame
            
        Returns:
            DataFrame with growth rates
        """
        # Define key metrics for growth calculation
        # CIS_10: Net Revenue, CIS_20: Gross Profit, CIS_50: PBT, CIS_61: Net Profit
        growth_metrics = ['CIS_10', 'CIS_20', 'CIS_50', 'CIS_61']
        
        # Calculate QoQ growth
        df = super().calculate_growth_rates(df, growth_metrics)
        
        # Calculate YoY growth
        df = super().calculate_yoy_growth_rates(df, growth_metrics)
        
        return df

    def calculate_ttm_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate TTM metrics.
        Tính toán các chỉ số TTM.
        
        Args:
            df: Pivoted DataFrame
            
        Returns:
            DataFrame with TTM metrics
        """
        # Define key metrics for TTM
        ttm_metrics = ['CIS_10', 'CIS_20', 'CIS_50', 'CIS_61']
        
        # Calculate TTM
        df = super().calculate_ttm(df, ttm_metrics)
        
        return df
    
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
        
        # Liquidity components
        result_df['current_assets'] = self.convert_to_billions(df.get('CBS_100', np.nan))
        result_df['current_liabilities'] = self.convert_to_billions(df.get('CBS_310', np.nan))
        
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

        # Net Debt = (ST Debt + LT Debt) - Cash
        result_df['net_debt'] = (result_df.get('st_debt', 0) + result_df.get('lt_debt', 0)) - result_df.get('cash', 0)

        # Working Capital = Current Assets - Current Liabilities
        result_df['working_capital'] = result_df.get('current_assets', 0) - result_df.get('current_liabilities', 0)

        # Calculate delta Working Capital (for FCFE calculation)
        result_df = result_df.sort_values(['SECURITY_CODE', 'REPORT_DATE'])
        result_df['delta_working_capital'] = result_df.groupby('SECURITY_CODE')['working_capital'].diff()

        # Calculate delta Net Borrowing (for FCFE calculation)
        net_borrowing = (result_df.get('st_debt', 0) + result_df.get('lt_debt', 0)) - result_df.get('cash', 0)
        result_df['delta_net_borrowing'] = result_df.groupby('SECURITY_CODE')[net_borrowing.name if hasattr(net_borrowing, 'name') else 'net_debt'].transform(lambda x: x.diff())

        # FCFE = NPATMI + Depreciation - Capex - Delta Working Capital + Delta Net Borrowing
        result_df['fcfe'] = (
            result_df.get('npatmi', 0) +
            result_df.get('depreciation', 0) -
            result_df.get('capex', 0) -
            result_df.get('delta_working_capital', 0) +
            result_df.get('delta_net_borrowing', 0)
        )

        return result_df
    
    def calculate_liquidity_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate liquidity ratios for COMPANY entities.
        
        Args:
            df: DataFrame with balance sheet metrics
            
        Returns:
            DataFrame with liquidity ratios calculated
        """
        result_df = df.copy()
        
        # Current Ratio
        result_df['current_ratio'] = self.safe_divide(
            numerator=result_df['current_assets'],
            denominator=result_df['current_liabilities'],
            result_nan=True
        )
        
        # Quick Ratio = (Current Assets - Inventory) / Current Liabilities
        result_df['quick_ratio'] = self.safe_divide(
            numerator=result_df['current_assets'] - result_df['inventory'],
            denominator=result_df['current_liabilities'],
            result_nan=True
        )
        
        # Cash Ratio = Cash / Current Liabilities
        result_df['cash_ratio'] = self.safe_divide(
            numerator=result_df['cash'],
            denominator=result_df['current_liabilities'],
            result_nan=True
        )
        
        return result_df

    def calculate_activity_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate activity ratios for COMPANY entities.
        
        Args:
            df: DataFrame with component metrics
            
        Returns:
            DataFrame with activity ratios calculated
        """
        result_df = df.copy()
        
        # Asset Turnover = Net Revenue / Total Assets
        result_df['asset_turnover'] = self.safe_divide(
            numerator=result_df['net_revenue'],
            denominator=result_df['total_assets'],
            result_nan=True
        )
        
        # Inventory Turnover = COGS / Inventory
        result_df['inventory_turnover'] = self.safe_divide(
            numerator=result_df['cogs'],
            denominator=result_df['inventory'],
            result_nan=True
        )
        
        # Receivables Turnover = Net Revenue / Account Receivable
        result_df['receivables_turnover'] = self.safe_divide(
            numerator=result_df['net_revenue'],
            denominator=result_df['account_receivable'],
            result_nan=True
        )
        
        return result_df

    def calculate_valuation_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate valuation ratios for COMPANY entities.
        
        Args:
            df: DataFrame with component metrics
            
        Returns:
            DataFrame with valuation ratios calculated
        """
        result_df = df.copy()
        
        # Book Value Per Share = Total Equity / Common Shares
        result_df['bvps'] = self.safe_divide(
            numerator=result_df['total_equity'] * 1e9,
            denominator=result_df['common_shares'],
            result_nan=True
        )
        
        return result_df

    def calculate_free_cash_flow(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate free cash flow for COMPANY entities.
        
        Args:
            df: DataFrame with cash flow metrics
            
        Returns:
            DataFrame with FCF metrics calculated
        """
        return self.calculate_cash_flow(df)
    
    def calculate_solvency_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate solvency ratios for COMPANY entities.
        
        Args:
            df: DataFrame with balance sheet metrics
            
        Returns:
            DataFrame with solvency ratios calculated
        """
        result_df = df.copy()
        
        # Debt to Equity
        result_df['debt_to_equity'] = self.safe_divide(
            numerator=result_df['st_debt'] + result_df['lt_debt'],
            denominator=result_df['total_equity'],
            result_nan=True
        )
        
        # Debt to Assets
        result_df['debt_to_assets'] = self.safe_divide(
            numerator=result_df['st_debt'] + result_df['lt_debt'],
            denominator=result_df['total_assets'],
            result_nan=True
        )
        
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
        
        # Get formulas
        calc_roe = formula_registry.get_formula('calculate_roe')
        calc_roa = formula_registry.get_formula('calculate_roa')
        calc_eps = formula_registry.get_formula('calculate_eps')
        
        if calc_roe:
            result_df['roe'] = df.apply(
                lambda row: calc_roe(row['npatmi'] * 1e9, row['total_equity'] * 1e9),
                axis=1
            )
        
        if calc_roa:
            result_df['roa'] = df.apply(
                lambda row: calc_roa(row['npatmi'] * 1e9, row['total_assets'] * 1e9),
                axis=1
            )
        
        # EPS = NPATMI (TTM) * 1e9 / (common_shares * 10,000)
        # First calculate TTM NPATMI if not already done
        if 'npatmi_ttm' not in df.columns:
            df = self.calculate_ttm(df, ['npatmi'])
            result_df = df # Update result_df to include TTM columns
        
        if calc_eps:
             result_df['eps'] = df.apply(
                lambda row: calc_eps(row['npatmi_ttm'] * 1e9, row['common_shares'] * 10000),
                axis=1
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
            "current_assets", "current_liabilities",

            # Cash Flow & Complex Metrics
            "operating_cf", "investment_cf", "capex", "financing_cf", "fcf",
            "net_debt", "working_capital", "delta_working_capital",
            "delta_net_borrowing", "fcfe",

            # TTM Metrics
            "net_revenue_ttm", "npatmi_ttm", "operating_cf_ttm",

            # Liquidity Ratios
            "current_ratio", "quick_ratio", "cash_ratio",

            # Solvency Ratios
            "debt_to_equity", "debt_to_assets",

            # Activity Ratios
            "asset_turnover", "inventory_turnover", "receivables_turnover",

            # Profitability Ratios
            "roe", "roa", "eps",

            # Valuation
            "bvps"
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