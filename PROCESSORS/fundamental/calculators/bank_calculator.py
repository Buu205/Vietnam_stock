#!/usr/bin/env python3
"""
Bank Financial Calculator - Bộ tính toán tài chính cho Ngân hàng
================================================================

Phiên bản refactor sử dụng BaseFinancialCalculator để giảm trùng lặp code.
Thực hiện các tính toán đặc thù cho thực thể BANK.

Tính năng chính:
1. Kế thừa tất cả chức năng chung từ BaseFinancialCalculator
2. Thực hiện các tính toán đặc thù cho BANK
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

class BankFinancialCalculator(BaseFinancialCalculator):
    """
    Financial calculator for banking institutions.
    Bộ tính toán tài chính cho ngân hàng.
    
    Handles specific metrics for banks such as NIM, CASA, LDR,
    NPL, and specialized balance sheet structure.
    Xử lý các chỉ số đặc thù cho ngân hàng như NIM, CASA, LDR,
    NPL, và cấu trúc bảng cân đối kế toán chuyên biệt.
    """
    
    def get_entity_type(self) -> str:
        """Return entity type for this calculator."""
        return "BANK"
    
    def get_metric_prefixes(self) -> List[str]:
        """Return metric code prefixes for BANK entities."""
        return ['BIS_', 'BBS_', 'BNOT_', 'CCFI_']
    
    def get_entity_specific_calculations(self) -> Dict[str, callable]:
        """Return BANK-specific calculation methods."""
        return {
            'components': self.calculate_components,
            'growth': self.calculate_growth,
            'profitability': self.calculate_profitability,
            'efficiency': self.calculate_efficiency,
            'liquidity_and_capital': self.calculate_liquidity_and_capital,
            'valuation': self.calculate_valuation,
        }
    
    # ==================== BANK-SPECIFIC CALCULATIONS ====================
    
    def calculate_components(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate basic components for BANK entities.
        
        Args:
            df: Pivoted DataFrame with raw metrics
            
        Returns:
            DataFrame with component metrics calculated
        """
        result_df = df.copy()
        
        # NPL amount
        npl_num = (
            df.get('BNOT_4_3', 0).fillna(0) +  # Substandard loans
            df.get('BNOT_4_4', 0).fillna(0) +  # Doubtful loans
            df.get('BNOT_4_5', 0).fillna(0)     # Loss loans
        )
        result_df['npl_amount'] = npl_num / 1e9
        
        # Net Interest Income (NII)
        result_df['nii'] = df.get('BIS_3', np.nan) / 1e9
        
        # Total Operating Income (TOI)
        result_df['toi'] = df.get('BIS_14A', np.nan) / 1e9
        
        # Non-Interest Income (NOII)
        result_df['noii'] = result_df['toi'] - result_df['nii']
        
        # Operating Expenses (OPEX)
        result_df['opex'] = df.get('BIS_14', np.nan) / 1e9
        
        # Provision Expense
        result_df['provision_expense'] = df.get('BIS_16', np.nan) / 1e9
        
        # Profit Before Tax (PBT)
        result_df['pbt'] = df.get('BIS_17', np.nan) / 1e9
        
        # NPATMI
        result_df['npatmi'] = df.get('BIS_22A', np.nan) / 1e9
        
        # Interest Income, Expense, and averages
        result_df['interest_income'] = df.get('BIS_1', np.nan) / 1e9
        result_df['interest_expense'] = df.get('BIS_2', np.nan) / 1e9
        result_df['iea'] = (df.get('BBS_120', 0) + df.get('BBS_130', 0)) / 1e9  # Interest earning assets
        result_df['ibl'] = df.get('BBS_321', np.nan) / 1e9  # Interest bearing liabilities
        
        # Calculate 2-quarter averages for averages
        result_df = self._calculate_2q_averages(result_df)
        
        return result_df
    
    def calculate_growth(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate growth metrics for BANK entities.
        
        Args:
            df: DataFrame with component metrics
            
        Returns:
            DataFrame with growth metrics calculated
        """
        result_df = df.copy()
        
        # Total Credit
        result_df['total_credit'] = (
            result_df.get("BBS_161", 0).fillna(0) +  # Customer loans
            result_df.get("BBS_180", 0).fillna(0) +  # Other credit
            result_df.get("BNOT_5_1_3", 0).fillna(0) +  # Other credit
            result_df.get("BNOT_13_1_1_3", 0).fillna(0) +  # Special credit
            result_df.get("BNOT_13_2_3", 0).fillna(0)    # Other credit
        ) / 1e9
        
        # Customer Loans
        result_df['customer_loan'] = df.get('BBS_161', 0) / 1e9
        
        # Customer Deposits
        result_df['customer_deposit'] = df.get('BBS_330', 0) / 1e9
        
        return result_df
    
    def calculate_profitability(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate profitability ratios for BANK entities.
        
        Args:
            df: DataFrame with component metrics
            
        Returns:
            DataFrame with profitability ratios calculated
        """
        result_df = df.copy()
        result_df = result_df.sort_values(["SECURITY_CODE", "REPORT_DATE"])
        
        # TTM for BIS_22A (NPATMI)
        result_df["bis22a_ttm"] = (
            result_df.groupby("SECURITY_CODE")["BIS_22A"]
            .transform(lambda s: s.rolling(window=4, min_periods=1).sum()) / 1e9
        )
        
        # ROEA (TTM) and ROAA (TTM) in percentage
        result_df["roea_ttm"] = self.safe_divide(
            numerator=result_df["bis22a_ttm"],
            denominator=result_df["equity_avg_2q"],
            result_nan=True
        ) * 100
        
        result_df["roaa_ttm"] = self.safe_divide(
            numerator=result_df["bis22a_ttm"],
            denominator=result_df["assets_avg_2q"],
            result_nan=True
        ) * 100
        
        # Asset Yield, Funding Cost, NIM (quarterly %)
        result_df["asset_yield_q"] = self.safe_divide(
            numerator=result_df["BIS_1"] / 1e9,
            denominator=result_df["avg_iea_2q"],
            result_nan=True
        ) * 100
        
        result_df["funding_cost_q"] = self.safe_divide(
            numerator=result_df["BIS_2"] / 1e9,
            denominator=result_df["avg_ibl_2q"],
            result_nan=True
        ) * 100
        
        result_df["nim_q"] = self.safe_divide(
            numerator=result_df["BIS_3"] / 1e9,
            denominator=result_df["avg_iea_2q"],
            result_nan=True
        ) * 100
        
        # Loan Yield
        result_df["loan_base"] = (result_df.get("BBS_160", 0) + result_df.get("BBS_180", 0)) / 1e9
        result_df = result_df.sort_values(["SECURITY_CODE", "REPORT_DATE"])
        result_df["loan_base_avg_2q"] = (
            result_df.groupby("SECURITY_CODE")["loan_base"]
            .transform(self._avg_two_quarters)
        )
        
        result_df["loan_yield_q"] = self.safe_divide(
            numerator=result_df.get("BNOT_31_1", 0) / 1e9,
            denominator=result_df["loan_base_avg_2q"],
            result_nan=True
        ) * 100
        
        return result_df
    
    def calculate_efficiency(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculator implementation for banking institutions.
        Bộ tính toán cho các tổ chức ngân hàng.
        
        Args:
            df: DataFrame with component metrics
            
        Returns:
            DataFrame with efficiency ratios calculated
        """
        result_df = df.copy()
        
        # CASA Ratio
        casa_num = (
            result_df.get("BNOT_26_1", 0) +  # Non-term deposits
            result_df.get("BNOT_26_5", 0) +  # Savings deposits
            result_df.get("BNOT_26_3", 0)     # Term deposits
        )
        casa_den = result_df.get("BNOT_26", 0)
        result_df["casa_ratio"] = self.safe_divide(
            numerator=casa_num,
            denominator=casa_den,
            result_nan=True
        ) * 100
        
        # Cost to Income Ratio (CIR)
        result_df["cir"] = self.safe_divide(
            numerator=result_df.get("BIS_14", 0),
            denominator=result_df.get("BIS_14A", 0),
            result_nan=True
        ) * 100
        
        # NII/TOI and NOII/TOI ratios
        result_df["nii_toi"] = self.safe_divide(
            numerator=result_df["nii"],
            denominator=result_df["toi"],
            result_nan=True
        ) * 100
        
        result_df["noii_toi"] = self.safe_divide(
            numerator=result_df["toi"] - result_df["nii"],
            denominator=result_df["toi"],
            result_nan=True
        ) * 100
        
        return result_df
    
    def calculate_liquidity_and_capital(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate liquidity and capital adequacy ratios for BANK entities.
        
        Args:
            df: DataFrame with component metrics
            
        Returns:
            DataFrame with liquidity and capital ratios calculated
        """
        result_df = df.copy()
        
        # LDR Pure
        result_df["ldr_pure"] = self.safe_divide(
            numerator=result_df.get("BBS_161", 0),
            denominator=result_df.get("BBS_330", 0) + result_df.get("BBS_370", 0),
            result_nan=True
        ) * 100
        
        # LDR Regulated (estimated)
        reg_den = (
            result_df.get("BBS_322", 0) + 
            result_df.get("BBS_330", 0) - 
            result_df.get("BNOT_26_5", 0) - 
            result_df.get("BNOT_26_3", 0) + 
            result_df.get("BBS_370", 0)
        )
        result_df["ldr_regulated_estimated"] = self.safe_divide(
            numerator=result_df.get("BBS_161", 0) - result_df.get("BNOT_7_5", 0),
            denominator=reg_den,
            result_nan=True
        ) * 100
        
        # Debt Group 2 Ratio
        result_df["debt_group2_ratio"] = self.safe_divide(
            numerator=result_df.get("BNOT_4_2", 0),
            denominator=result_df.get("BNOT_4", 0),
            result_nan=True
        ) * 100
        
        # NPL Ratio
        npl_num = (
            result_df.get("BNOT_4_3", 0) + 
            result_df.get("BNOT_4_4", 0) + 
            result_df.get("BNOT_4_5", 0)
        )
        result_df["npl_ratio"] = self.safe_divide(
            numerator=npl_num,
            denominator=result_df.get("BNOT_4", 0),
            result_nan=True
        ) * 100
        
        # Group 2 to Total Ratio
        grp_2_5 = (
            result_df.get("BNOT_4_2", 0) + 
            result_df.get("BNOT_4_3", 0) + 
            result_df.get("BNOT_4_4", 0) + 
            result_df.get("BNOT_4_5", 0)
        )
        result_df["group2_to_total_ratio"] = self.safe_divide(
            numerator=grp_2_5,
            denominator=result_df.get("BNOT_4", 0),
            result_nan=True
        ) * 100
        
        # Loan Loss Coverage Ratio (LLCR)
        result_df["llcr"] = self.safe_divide(
            numerator=result_df.get("BBS_169", 0),
            denominator=npl_num,
            result_nan=True
        ) * 100
        
        return result_df
    
    def calculate_valuation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate valuation metrics for BANK entities.
        
        Args:
            df: DataFrame with component metrics
            
        Returns:
            DataFrame with valuation metrics calculated
        """
        result_df = df.copy()
        result_df = result_df.sort_values(["SECURITY_CODE", "REPORT_DATE"])
        
        # BVPS
        equity = result_df.get("BBS_410", 0)  # Equity in VND
        minority_interest = result_df.get("BBS_7001", 0) if "BBS_7001" in result_df.columns else 0
        shares = result_df.get("BBS_411", 0) / 10000  # Shares count
        
        result_df["bvps"] = self.safe_divide(
            numerator=equity - minority_interest,
            denominator=shares,
            result_nan=True
        )
        
        # EPS (TTM)
        result_df["bis22a_ttm"] = (
            result_df.groupby("SECURITY_CODE")["BIS_22A"]
            .transform(lambda s: s.rolling(window=4, min_periods=1).sum()) / 1e9
        )
        
        result_df["eps_ttm"] = self.safe_divide(
            numerator=result_df["bis22a_ttm"] * 1e9,
            denominator=shares,
            result_nan=True
        )
        
        return result_df
    
    # ==================== ENTITY-SPECIFIC HELPER METHODS ====================
    
    def _calculate_2q_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate 2-quarter averages for key metrics.
        
        Args:
            df: DataFrame with base metrics
            
        Returns:
            DataFrame with 2Q average columns added
        """
        # Ensure proper sorting
        df = df.sort_values(["SECURITY_CODE", "REPORT_DATE"])
        
        # Fill forward equity for averaging
        df["BBS_500_ffill"] = df.groupby("SECURITY_CODE")["BBS_500"].ffill()
        
        # Calculate averages
        df["equity_avg_2q"] = (
            df.groupby("SECURITY_CODE")["BBS_500_ffill"]
            .transform(lambda s: s.rolling(window=2, min_periods=1).mean()) / 1e9
        )
        
        df["assets_avg_2q"] = (
            df.groupby("SECURITY_CODE")["BBS_100"]
            .transform(lambda s: s.rolling(window=2, min_periods=2).mean()) / 1e9
        )
        
        df["avg_iea_2q"] = (
            df.groupby("SECURITY_CODE")["iea"]
            .transform(self._avg_two_quarters)
        )
        
        df["avg_ibl_2q"] = (
            df.groupby("SECURITY_CODE")["ibl"]
            .transform(lambda s: s.rolling(window=2, min_periods=1).mean())
        )
        
        return df
    
    @staticmethod
    def _avg_two_quarters(series: pd.Series) -> pd.Series:
        """Calculate average of two consecutive quarters."""
        return series.rolling(window=2, min_periods=1).mean()
    
    def postprocess_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Post-process BANK-specific results.
        
        Args:
            df: DataFrame with calculated metrics
            
        Returns:
            Post-processed DataFrame
        """
        # Call parent postprocessing
        df = super().postprocess_results(df)
        
        # Select and rename columns for BANK output
        bank_cols = [
            # ID columns
            "SECURITY_CODE", "REPORT_DATE", "YEAR", "QUARTER", "FREQ_CODE",
            
            # Components
            "npl_amount", "nii", "toi", "noii", "opex", "provision_expense", 
            "pbt", "npatmi", "interest_income", "interest_expense",
            "iea", "ibl", "avg_iea_2q", "avg_ibl_2q", "equity_avg_2q",
            
            # Growth
            "total_credit", "customer_loan", "customer_deposit",
            
            # Profitability
            "roea_ttm", "roaa_ttm", "asset_yield_q", "funding_cost_q", 
            "nim_q", "loan_yield_q",
            
            # Efficiency
            "casa_ratio", "cir", "nii_toi", "noii_toi",
            
            # Liquidity/Capital
            "ldr_pure", "ldr_regulated_estimated", "debt_group2_ratio", 
            "npl_ratio", "group2_to_total_ratio", "llcr",
            
            # Valuation
            "bvps", "eps_ttm"
        ]
        
        # Filter available columns
        available_cols = [col for col in bank_cols if col in df.columns]
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