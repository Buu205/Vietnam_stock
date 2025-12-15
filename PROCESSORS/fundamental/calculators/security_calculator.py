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
from PROCESSORS.fundamental.formulas.registry import formula_registry
import logging

logger = logging.getLogger(__name__)

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
            'components': self.calculate_basic_components, # Keeping original name for now, as instruction implies adding to existing.
            'profitability': self.calculate_profitability,
            'revenue_composition': self.calculate_revenue_composition,
            'efficiency': self.calculate_efficiency,
            'risk_metrics': self.calculate_risk_metrics,
            'capital_adequacy': self.calculate_capital_adequacy,
            'growth': self.calculate_growth_rates,
            'ttm': self.calculate_ttm_metrics
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

        # Basic components (convert to billions VND) - FIXED MAPPING
        result_df['net_profit'] = self.convert_to_billions(df.get('SIS_201', np.nan))  # NPATMI
        result_df['total_revenue'] = self.convert_to_billions(df.get('SIS_20', np.nan))  # Total Operating Revenue

        # Balance sheet components - FIXED MAPPING
        result_df['total_assets'] = self.convert_to_billions(df.get('SBS_270', np.nan))  # Total Assets
        result_df['equity'] = self.convert_to_billions(df.get('SBS_400', np.nan))  # Total Equity
        result_df['cash'] = self.convert_to_billions(df.get('SBS_111', np.nan))  # Cash
        result_df['liabilities'] = self.convert_to_billions(df.get('SBS_300', np.nan))  # Total Liabilities

        # Investment Portfolio components
        result_df['fvtpl'] = self.convert_to_billions(df.get('SBS_112', np.nan))
        result_df['htm'] = self.convert_to_billions(df.get('SBS_113', np.nan))
        result_df['afs'] = self.convert_to_billions(df.get('SBS_115', np.nan))
        result_df['total_investment'] = (
            result_df.get('fvtpl', 0) +
            result_df.get('htm', 0) +
            result_df.get('afs', 0)
        )

        # Loan Portfolio
        result_df['margin_loans'] = self.convert_to_billions(df.get('SBS_114', np.nan))

        # Debt
        result_df['st_debt'] = self.convert_to_billions(df.get('SBS_311', np.nan))
        result_df['lt_debt'] = self.convert_to_billions(df.get('SBS_341', np.nan))
        result_df['total_debt'] = result_df.get('st_debt', 0) + result_df.get('lt_debt', 0)

        # Income components
        result_df['income_fvtpl'] = self.convert_to_billions(df.get('SIS_1', np.nan))
        result_df['income_htm'] = self.convert_to_billions(df.get('SIS_2', np.nan))
        result_df['income_loans'] = self.convert_to_billions(df.get('SIS_3', np.nan))
        result_df['income_afs'] = self.convert_to_billions(df.get('SIS_4', np.nan))

        # Gross Profit
        result_df['gross_profit'] = self.convert_to_billions(df.get('SIS_50_1', np.nan))
        if result_df['gross_profit'].isna().all():
            # Calculate if not available: Revenue - Operating Expenses
            result_df['gross_profit'] = (
                result_df.get('total_revenue', 0) -
                self.convert_to_billions(df.get('SIS_40', 0))
            )

        return result_df
    
    def calculate_growth_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate growth rates for Security metrics.
        Tính toán tốc độ tăng trưởng cho Chứng khoán.
        """
        # Key metrics for Security
        growth_metrics = [
            'total_revenue', 'net_profit'
        ]
        
        # Calculate QoQ growth
        df = super().calculate_growth_rates(df, growth_metrics)
        
        # Calculate YoY growth
        df = super().calculate_yoy_growth_rates(df, growth_metrics)
        
        return df

    def calculate_ttm_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate TTM metrics for Security.
        Tính toán các chỉ số TTM cho Chứng khoán.
        """
        # Key metrics for TTM
        ttm_metrics = [
            'total_revenue', 'net_profit'
        ]
        
        # Calculate TTM
        df = super().calculate_ttm(df, ttm_metrics)
        
        return df
    
    def calculate_profitability(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate profitability ratios for SECURITY entities.

        Args:
            df: DataFrame with basic components

        Returns:
            DataFrame with profitability ratios calculated
        """
        result_df = df.copy()

        # Calculate 2Q averages for TTM ratios
        result_df = result_df.sort_values(['SECURITY_CODE', 'REPORT_DATE'])

        # Average Assets (2Q)
        result_df['assets_avg_2q'] = (
            result_df.groupby('SECURITY_CODE')['total_assets']
            .transform(lambda s: s.rolling(window=2, min_periods=1).mean())
        )

        # Average Equity (2Q)
        result_df['equity_avg_2q'] = (
            result_df.groupby('SECURITY_CODE')['equity']
            .transform(lambda s: s.rolling(window=2, min_periods=1).mean())
        )

        # TTM Net Profit
        result_df['net_profit_ttm'] = (
            result_df.groupby('SECURITY_CODE')['net_profit']
            .transform(lambda s: s.rolling(window=4, min_periods=1).sum())
        )

        # Get formulas
        calc_roe = formula_registry.get_formula('calculate_roe')
        calc_roa = formula_registry.get_formula('calculate_roa')

        # ROAE (TTM) = Net Profit TTM / Equity Avg 2Q
        if calc_roe:
            result_df['roae_ttm'] = df.apply(
                lambda row: calc_roe(row.get('net_profit_ttm', 0) * 1e9, row.get('equity_avg_2q', 1) * 1e9),
                axis=1
            )
        else:
            result_df['roae_ttm'] = self.safe_divide(
                numerator=result_df['net_profit_ttm'],
                denominator=result_df['equity_avg_2q'],
                result_nan=True
            ) * 100

        # ROAA (TTM) = Net Profit TTM / Assets Avg 2Q
        if calc_roa:
            result_df['roaa_ttm'] = df.apply(
                lambda row: calc_roa(row.get('net_profit_ttm', 0) * 1e9, row.get('assets_avg_2q', 1) * 1e9),
                axis=1
            )
        else:
            result_df['roaa_ttm'] = self.safe_divide(
                numerator=result_df['net_profit_ttm'],
                denominator=result_df['assets_avg_2q'],
                result_nan=True
            ) * 100

        # Profit Margin = Net Profit / Total Revenue
        result_df['profit_margin'] = self.safe_divide(
            numerator=result_df['net_profit'],
            denominator=result_df['total_revenue'],
            result_nan=True
        ) * 100

        # Gross Profit Margin = Gross Profit / Total Revenue
        result_df['gross_profit_margin'] = self.safe_divide(
            numerator=result_df.get('gross_profit', 0),
            denominator=result_df['total_revenue'],
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

        # Total Investment Income = FVTPL + HTM + AFS
        result_df['investment_revenue'] = (
            result_df.get('income_fvtpl', 0) +
            result_df.get('income_htm', 0) +
            result_df.get('income_afs', 0)
        )

        # Investment Income Ratio = Investment Income / Total Revenue
        result_df['investment_ratio'] = self.safe_divide(
            numerator=result_df['investment_revenue'],
            denominator=result_df['total_revenue'],
            result_nan=True
        ) * 100

        # Margin Lending Ratio = Lending Income / Total Revenue
        result_df['lending_ratio'] = self.safe_divide(
            numerator=result_df.get('income_loans', 0),
            denominator=result_df['total_revenue'],
            result_nan=True
        ) * 100

        # Brokerage Ratio = Brokerage Income / Total Revenue
        result_df['brokerage_ratio'] = self.safe_divide(
            numerator=self.convert_to_billions(df.get('SIS_6', 0)),
            denominator=result_df['total_revenue'],
            result_nan=True
        ) * 100

        # IB Revenue = Underwriting + Agency + Advisory
        ib_revenue = (
            self.convert_to_billions(df.get('SIS_7_1', 0)) +  # Underwriting
            self.convert_to_billions(df.get('SIS_7_2', 0)) +  # Agency
            self.convert_to_billions(df.get('SIS_8', 0)) +    # Investment advisory
            self.convert_to_billions(df.get('SIS_10', 0))     # Financial advisory
        )

        result_df['ib_ratio'] = self.safe_divide(
            numerator=ib_revenue,
            denominator=result_df['total_revenue'],
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

        # Operating Expenses
        operating_expenses = self.convert_to_billions(df.get('SIS_40', 0))

        # G&A Expenses
        ga_expenses = self.convert_to_billions(df.get('SIS_62', 0))

        # CIR = (Operating Expenses + G&A) / Total Revenue
        result_df['cir'] = self.safe_divide(
            numerator=abs(operating_expenses) + abs(ga_expenses),
            denominator=result_df['total_revenue'],
            result_nan=True
        ) * 100

        # Operating Expense Ratio = Operating Expenses / Total Revenue
        result_df['opex_ratio'] = self.safe_divide(
            numerator=abs(operating_expenses),
            denominator=result_df['total_revenue'],
            result_nan=True
        ) * 100

        # G&A Expense Ratio = G&A / Total Revenue
        result_df['ga_ratio'] = self.safe_divide(
            numerator=abs(ga_expenses),
            denominator=result_df['total_revenue'],
            result_nan=True
        ) * 100

        return result_df
    
    def calculate_risk_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate risk metrics for SECURITY entities.

        Args:
            df: DataFrame with basic components

        Returns:
            DataFrame with risk metrics calculated
        """
        result_df = df.copy()

        # Leverage Ratio = Total Assets / Equity (FIXED)
        result_df['leverage'] = self.safe_divide(
            numerator=result_df['total_assets'],
            denominator=result_df['equity'],
            result_nan=True
        )

        # Loans to Equity Ratio
        result_df['loans_to_equity'] = self.safe_divide(
            numerator=result_df.get('margin_loans', 0),
            denominator=result_df['equity'],
            result_nan=True
        )

        # Investment to Assets Ratio
        result_df['inv_to_assets'] = self.safe_divide(
            numerator=result_df.get('total_investment', 0),
            denominator=result_df['total_assets'],
            result_nan=True
        ) * 100

        # Loans to Assets Ratio
        result_df['loans_to_assets'] = self.safe_divide(
            numerator=result_df.get('margin_loans', 0),
            denominator=result_df['total_assets'],
            result_nan=True
        ) * 100

        # Liquidity Ratio = Cash / Current Liabilities
        result_df['liquidity_ratio'] = self.safe_divide(
            numerator=result_df['cash'],
            denominator=result_df.get('st_debt', 1),
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
            "net_profit", "total_revenue", "gross_profit",
            "total_assets", "equity", "cash", "liabilities",

            # Portfolio components
            "fvtpl", "htm", "afs", "total_investment", "margin_loans",
            "st_debt", "lt_debt", "total_debt",

            # Income components
            "income_fvtpl", "income_htm", "income_loans", "income_afs",

            # Profitability (TTM)
            "roae_ttm", "roaa_ttm", "profit_margin", "gross_profit_margin",
            "net_profit_ttm", "assets_avg_2q", "equity_avg_2q",

            # Revenue composition
            "investment_revenue", "investment_ratio", "lending_ratio",
            "brokerage_ratio", "ib_ratio",

            # Efficiency
            "cir", "opex_ratio", "ga_ratio",

            # Risk metrics
            "leverage", "loans_to_equity", "inv_to_assets",
            "loans_to_assets", "liquidity_ratio",

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