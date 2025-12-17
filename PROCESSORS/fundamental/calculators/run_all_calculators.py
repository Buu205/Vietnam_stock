#!/usr/bin/env python3
"""
Run All Financial Calculators
=============================

Unified script to load fundamental data from *_full.parquet files (long format)
and calculate all financial metrics for each entity type.

This script reads the canonical long-format data (with METRIC_CODE column)
and outputs calculated metrics to /DATA/processed/fundamental/{entity}/.

Usage:
    python3 PROCESSORS/fundamental/calculators/run_all_calculators.py

    # Run specific entity:
    python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity company
    python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity bank

Output:
    DATA/processed/fundamental/company/company_financial_metrics.parquet
    DATA/processed/fundamental/bank/bank_financial_metrics.parquet
    DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet
    DATA/processed/fundamental/security/security_financial_metrics.parquet

Data Flow:
    *_full.parquet (long format)
    → Pivot to wide format
    → Calculate metrics
    → *_financial_metrics.parquet (wide format)

Author: Claude Code
Date: 2025-12-16
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import argparse
from typing import Optional, Dict, List, Callable
from abc import ABC, abstractmethod

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = PROJECT_ROOT / "DATA" / "processed" / "fundamental"


# ==============================================================================
# BASE CALCULATOR CLASS
# ==============================================================================

class EntityCalculator(ABC):
    """Base class for entity-specific financial calculators."""

    def __init__(self, entity_type: str):
        self.entity_type = entity_type
        self.input_path = DATA_PATH / f"{entity_type}_full.parquet"
        self.output_dir = DATA_PATH / entity_type
        self.output_path = self.output_dir / f"{entity_type}_financial_metrics.parquet"

    def load_and_pivot(self, freq_code: str = 'Q') -> pd.DataFrame:
        """Load long-format data and pivot to wide format."""
        logger.info(f"Loading data from {self.input_path}")

        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        df = pd.read_parquet(self.input_path)
        logger.info(f"Loaded {len(df):,} rows")

        # Filter by frequency
        if 'FREQ_CODE' in df.columns and freq_code:
            df = df[df['FREQ_CODE'] == freq_code].copy()
            logger.info(f"Filtered to {freq_code} frequency: {len(df):,} rows")

        # Ensure date columns exist
        if 'REPORT_DATE' in df.columns:
            df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
            if 'YEAR' not in df.columns:
                df['YEAR'] = df['REPORT_DATE'].dt.year
            if 'QUARTER' not in df.columns:
                df['QUARTER'] = df['REPORT_DATE'].dt.quarter

        # Pivot from long to wide format
        logger.info("Pivoting to wide format...")
        index_cols = ['SECURITY_CODE', 'REPORT_DATE', 'YEAR', 'QUARTER', 'FREQ_CODE']
        available_index = [c for c in index_cols if c in df.columns]

        pivot = df.pivot_table(
            index=available_index,
            columns='METRIC_CODE',
            values='METRIC_VALUE',
            aggfunc='first'
        ).reset_index()

        pivot.columns.name = None
        logger.info(f"Pivoted to {len(pivot):,} rows, {len(pivot.columns)} columns")

        return pivot

    @abstractmethod
    def get_metric_mapping(self) -> Dict[str, str]:
        """Return mapping of output column names to metric codes."""
        pass

    @abstractmethod
    def calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived metrics (ratios, margins, etc.)."""
        pass

    def safe_divide(self, numerator, denominator, multiplier: float = 1.0):
        """Safe division handling zeros and NaNs."""
        return np.where(
            (denominator != 0) & (~pd.isna(denominator)),
            numerator / denominator * multiplier,
            np.nan
        )

    def calculate_ttm(self, df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
        """Calculate TTM (trailing 12 months) for specified columns."""
        df = df.sort_values(['SECURITY_CODE', 'REPORT_DATE'])

        for col in cols:
            if col in df.columns:
                df[f'{col}_ttm'] = df.groupby('SECURITY_CODE')[col].transform(
                    lambda x: x.rolling(window=4, min_periods=4).sum()
                )
        return df

    def run(self) -> pd.DataFrame:
        """Execute the full calculation pipeline."""
        logger.info(f"{'='*60}")
        logger.info(f"Starting {self.entity_type.upper()} Calculator")
        logger.info(f"{'='*60}")

        # Load and pivot
        df = self.load_and_pivot()

        # Rename columns using mapping
        mapping = self.get_metric_mapping()
        for new_name, metric_code in mapping.items():
            if metric_code in df.columns:
                df[new_name] = pd.to_numeric(df[metric_code], errors='coerce')

        # Calculate derived metrics
        df = self.calculate_derived_metrics(df)

        # Rename ID columns
        df = df.rename(columns={
            'SECURITY_CODE': 'symbol',
            'REPORT_DATE': 'report_date',
            'YEAR': 'year',
            'QUARTER': 'quarter',
            'FREQ_CODE': 'freq_code'
        })

        # Select output columns
        df = self.select_output_columns(df)

        # Save
        self.output_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self.output_path, index=False)

        logger.info(f"Saved to: {self.output_path}")
        logger.info(f"Total rows: {len(df):,}")
        logger.info(f"Total columns: {len(df.columns)}")
        logger.info(f"Unique tickers: {df['symbol'].nunique()}")
        logger.info(f"{'='*60}")

        return df

    @abstractmethod
    def select_output_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select and order output columns."""
        pass


# ==============================================================================
# COMPANY CALCULATOR
# ==============================================================================

class CompanyCalculator(EntityCalculator):
    """Calculator for Company (non-financial) entities."""

    def __init__(self):
        super().__init__('company')

    def get_metric_mapping(self) -> Dict[str, str]:
        """Metric code mapping for company financials."""
        return {
            # Income Statement
            'net_revenue': 'CIS_10',
            'cogs': 'CIS_11',
            'gross_profit': 'CIS_20',
            'selling_expense': 'CIS_25',
            'admin_expense': 'CIS_26',
            'finance_income': 'CIS_21',
            'finance_cost': 'CIS_22',
            'ebt': 'CIS_50',
            'npatmi': 'CIS_61',

            # Balance Sheet
            'total_assets': 'CBS_270',
            'total_liabilities': 'CBS_300',
            'total_equity': 'CBS_400',
            'cash': 'CBS_110',
            'inventory': 'CBS_140',
            'account_receivable': 'CBS_130',
            'tangible_fixed_asset': 'CBS_221',
            'st_debt': 'CBS_320',
            'lt_debt': 'CBS_338',
            'common_shares': 'CBS_411A',
            'current_assets': 'CBS_100',
            'current_liabilities': 'CBS_310',
            'gross_ppe': 'CBS_222',
            'accumulated_depreciation': 'CBS_223',
            'cip': 'CBS_230',

            # Cash Flow
            'operating_cf': 'CCFI_20',
            'investment_cf': 'CCFI_30',
            'financing_cf': 'CCFI_40',
            'capex': 'CCFI_21',
            'depreciation': 'CCFI_2',
        }

    def calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate company-specific derived metrics."""

        # SG&A (selling and admin are typically negative)
        selling = df.get('selling_expense', pd.Series([0]*len(df))).fillna(0)
        admin = df.get('admin_expense', pd.Series([0]*len(df))).fillna(0)
        df['sga'] = selling + admin

        # EBIT = Gross Profit - SG&A (note: SGA is typically negative)
        df['ebit'] = df['gross_profit'].fillna(0) + df['sga']

        # Net finance income
        fin_income = df.get('finance_income', pd.Series([0]*len(df))).fillna(0)
        fin_cost = df.get('finance_cost', pd.Series([0]*len(df))).fillna(0)
        df['net_finance_income'] = fin_income + fin_cost

        # EBITDA
        df['ebitda'] = df['ebit'] + df.get('depreciation', pd.Series([0]*len(df))).fillna(0)

        # Margins (%)
        df['gross_profit_margin'] = self.safe_divide(df['gross_profit'], df['net_revenue'], 100)
        df['ebit_margin'] = self.safe_divide(df['ebit'], df['net_revenue'], 100)
        df['ebitda_margin'] = self.safe_divide(df['ebitda'], df['net_revenue'], 100)
        df['net_margin'] = self.safe_divide(df['npatmi'], df['net_revenue'], 100)

        # Profitability ratios (%)
        df['roe'] = self.safe_divide(df['npatmi'], df['total_equity'], 100)
        df['roa'] = self.safe_divide(df['npatmi'], df['total_assets'], 100)

        # Liquidity ratios
        df['current_ratio'] = self.safe_divide(df['current_assets'], df['current_liabilities'])
        df['quick_ratio'] = self.safe_divide(
            df['current_assets'] - df.get('inventory', pd.Series([0]*len(df))).fillna(0),
            df['current_liabilities']
        )
        df['cash_ratio'] = self.safe_divide(df['cash'], df['current_liabilities'])

        # Solvency ratios
        total_debt = df.get('st_debt', pd.Series([0]*len(df))).fillna(0) + \
                     df.get('lt_debt', pd.Series([0]*len(df))).fillna(0)
        df['total_debt'] = total_debt
        df['debt_to_equity'] = self.safe_divide(total_debt, df['total_equity'])
        df['debt_to_assets'] = self.safe_divide(total_debt, df['total_assets'])

        # Activity ratios
        df['asset_turnover'] = self.safe_divide(df['net_revenue'], df['total_assets'])
        df['inventory_turnover'] = self.safe_divide(
            np.abs(df.get('cogs', pd.Series([0]*len(df))).fillna(0)),
            df.get('inventory', pd.Series([1]*len(df))).fillna(1)
        )
        df['receivables_turnover'] = self.safe_divide(df['net_revenue'], df['account_receivable'])

        # Working Capital (calculate first for FCFF)
        df['working_capital'] = df['current_assets'] - df['current_liabilities']

        # Free Cash Flow to Equity (FCF = Operating CF - CapEx)
        df['fcf'] = df.get('operating_cf', pd.Series([0]*len(df))).fillna(0) - \
                    np.abs(df.get('capex', pd.Series([0]*len(df))).fillna(0))

        # Free Cash Flow to Firm (FCFF)
        # FCFF = EBIT * (1 - Tax Rate) + Depreciation - CapEx - Delta Working Capital
        ebt = df.get('ebt', pd.Series([0]*len(df))).fillna(0)
        npatmi_val = df.get('npatmi', pd.Series([0]*len(df))).fillna(0)
        tax_expense = ebt - npatmi_val
        # Calculate effective tax rate, cap between 0 and 50%
        tax_rate = self.safe_divide(tax_expense, ebt)
        tax_rate = np.clip(np.where(pd.isna(tax_rate), 0.2, tax_rate), 0, 0.5)  # Default 20% if invalid

        nopat = df['ebit'] * (1 - tax_rate)
        depreciation = df.get('depreciation', pd.Series([0]*len(df))).fillna(0)
        capex_abs = np.abs(df.get('capex', pd.Series([0]*len(df))).fillna(0))

        # Calculate delta working capital (change from previous quarter)
        df = df.sort_values(['SECURITY_CODE', 'REPORT_DATE'] if 'REPORT_DATE' in df.columns else ['SECURITY_CODE', 'report_date'])
        df['delta_wc'] = df.groupby('SECURITY_CODE')['working_capital'].diff().fillna(0)

        df['fcff'] = nopat + depreciation - capex_abs - df['delta_wc']

        # Net Debt
        df['net_debt'] = total_debt - df.get('cash', pd.Series([0]*len(df))).fillna(0)

        # Investment ratios (%)
        df['depreciation_rate'] = self.safe_divide(
            np.abs(df.get('accumulated_depreciation', pd.Series([0]*len(df))).fillna(0)),
            df.get('gross_ppe', pd.Series([1]*len(df))).fillna(1),
            100
        )
        df['cip_rate'] = self.safe_divide(df.get('cip', pd.Series([0]*len(df))).fillna(0), df['total_assets'], 100)

        # Per share metrics
        shares = df.get('common_shares', pd.Series([1]*len(df))).fillna(1) * 10000  # shares in 10,000s
        df['eps'] = self.safe_divide(df['npatmi'], shares)
        df['bvps'] = self.safe_divide(df['total_equity'], shares)

        # TTM metrics
        df = self.calculate_ttm(df, ['net_revenue', 'npatmi', 'operating_cf'])

        return df

    def select_output_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select output columns for company metrics."""
        output_cols = [
            # ID columns
            'symbol', 'report_date', 'year', 'quarter', 'freq_code',

            # Income Statement (raw VND)
            'net_revenue', 'cogs', 'gross_profit', 'sga', 'ebit',
            'net_finance_income', 'ebt', 'npatmi', 'depreciation', 'ebitda',

            # Margins (%)
            'gross_profit_margin', 'ebit_margin', 'ebitda_margin', 'net_margin',

            # Balance Sheet (raw VND)
            'total_assets', 'total_liabilities', 'total_equity', 'cash',
            'inventory', 'account_receivable', 'tangible_fixed_asset',
            'st_debt', 'lt_debt', 'common_shares',
            'current_assets', 'current_liabilities',
            'gross_ppe', 'accumulated_depreciation', 'cip',

            # Cash Flow (raw VND)
            'operating_cf', 'investment_cf', 'financing_cf', 'capex', 'fcf', 'fcff',
            'total_debt', 'net_debt', 'working_capital', 'delta_wc',

            # TTM Metrics
            'net_revenue_ttm', 'npatmi_ttm', 'operating_cf_ttm',

            # Liquidity Ratios
            'current_ratio', 'quick_ratio', 'cash_ratio',

            # Solvency Ratios
            'debt_to_equity', 'debt_to_assets',

            # Activity Ratios
            'asset_turnover', 'inventory_turnover', 'receivables_turnover',

            # Profitability Ratios (%)
            'roe', 'roa',

            # Investment Ratios (%)
            'depreciation_rate', 'cip_rate',

            # Per Share
            'eps', 'bvps'
        ]

        available_cols = [c for c in output_cols if c in df.columns]
        return df[available_cols].copy()


# ==============================================================================
# BANK CALCULATOR
# ==============================================================================

class BankCalculator(EntityCalculator):
    """Calculator for Bank entities."""

    def __init__(self):
        super().__init__('bank')

    def load_and_pivot(self, freq_code: str = 'Q') -> pd.DataFrame:
        """
        Override load_and_pivot to handle BNOT metrics that may have different FREQ_CODE.
        BNOT metrics (CASA, NPL, Provision) are often reported only in S/Y frequency,
        so we need to merge them with Q frequency data.
        """
        logger.info(f"Loading data from {self.input_path}")

        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")

        df = pd.read_parquet(self.input_path)
        logger.info(f"Loaded {len(df):,} rows")

        # Ensure date columns exist
        if 'REPORT_DATE' in df.columns:
            df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
            if 'YEAR' not in df.columns:
                df['YEAR'] = df['REPORT_DATE'].dt.year
            if 'QUARTER' not in df.columns:
                df['QUARTER'] = df['REPORT_DATE'].dt.quarter

        # Split into Q frequency and BNOT metrics (any frequency)
        # BNOT_4 = total loans by debt group, BNOT_4_1/2/3/4/5 = groups 1-5
        # BNOT_26 = total deposits by type, BNOT_26_1/3/5 = CASA components (Current + Savings + Other)
        bnot_metrics = ['BNOT_4', 'BNOT_4_1', 'BNOT_4_2', 'BNOT_4_3', 'BNOT_4_4', 'BNOT_4_5',
                        'BNOT_26', 'BNOT_26_1', 'BNOT_26_3', 'BNOT_26_5',
                        'BNOT_29', 'BNOT_34', 'BNOT_35', 'BNOT_42', 'BNOT_45',
                        'BNOT_13_1_1_3']  # Short-term deposit collateral for LDR Regulated

        # Get Q frequency data (main data)
        df_q = df[df['FREQ_CODE'] == 'Q'].copy()
        logger.info(f"Q frequency data: {len(df_q):,} rows")

        # Get BNOT metrics from any frequency (prefer Q, then S, then Y)
        df_bnot = df[df['METRIC_CODE'].isin(bnot_metrics)].copy()
        # Sort by preference: Q > S > Y
        freq_order = {'Q': 0, 'S': 1, 'Y': 2}
        df_bnot['freq_priority'] = df_bnot['FREQ_CODE'].map(freq_order).fillna(3)
        df_bnot = df_bnot.sort_values(['SECURITY_CODE', 'REPORT_DATE', 'METRIC_CODE', 'freq_priority'])
        df_bnot = df_bnot.drop_duplicates(subset=['SECURITY_CODE', 'REPORT_DATE', 'METRIC_CODE'], keep='first')
        df_bnot = df_bnot.drop(columns=['freq_priority'])
        logger.info(f"BNOT metrics data: {len(df_bnot):,} rows")

        # Remove BNOT metrics from Q data to avoid duplicates, then combine
        df_q_no_bnot = df_q[~df_q['METRIC_CODE'].isin(bnot_metrics)]
        df_combined = pd.concat([df_q_no_bnot, df_bnot], ignore_index=True)
        logger.info(f"Combined data: {len(df_combined):,} rows")

        # Pivot from long to wide format
        logger.info("Pivoting to wide format...")
        index_cols = ['SECURITY_CODE', 'REPORT_DATE', 'YEAR', 'QUARTER']
        available_index = [c for c in index_cols if c in df_combined.columns]

        pivot = df_combined.pivot_table(
            index=available_index,
            columns='METRIC_CODE',
            values='METRIC_VALUE',
            aggfunc='first'
        ).reset_index()

        # Add FREQ_CODE column for compatibility
        pivot['FREQ_CODE'] = 'Q'
        pivot.columns.name = None
        logger.info(f"Pivoted to {len(pivot):,} rows, {len(pivot.columns)} columns")

        return pivot

    def get_metric_mapping(self) -> Dict[str, str]:
        """Metric code mapping for bank financials."""
        return {
            # Income Statement
            'interest_income': 'BIS_1',
            'interest_expense': 'BIS_2',
            'nii': 'BIS_3',  # Net Interest Income (Thu nhập lãi thuần)
            'fee_income': 'BIS_4',
            'fee_expense': 'BIS_5',
            'net_fee_income': 'BIS_6',
            'trading_income': 'BIS_8',
            'securities_income': 'BIS_9',
            'other_income': 'BIS_10',
            'toi': 'BIS_14A',  # Total Operating Income (Tổng thu nhập hoạt động)
            'ppop_raw': 'BIS_15',  # Pre-provision Operating Profit
            'provision_expense': 'BIS_16',  # Chi phí dự phòng
            'pbt': 'BIS_17',  # Profit Before Tax (Tổng lợi nhuận trước thuế)
            'opex': 'BIS_14',  # Operating Expenses (Chi phí hoạt động)
            'npat': 'BIS_21',  # Net Profit After Tax (Lợi nhuận sau thuế)
            'minority_interest': 'BIS_22',  # Minority Interest
            'npatmi': 'BIS_22A',  # NPATMI (Cổ đông của Công ty mẹ)

            # Balance Sheet
            'total_assets': 'BBS_100',
            'cash_balances': 'BBS_110',
            'placements_sbb': 'BBS_120',  # Placements with State Bank
            'placements_others': 'BBS_130',  # Placements with other banks
            'securities_trading': 'BBS_140',
            'securities_investment': 'BBS_150',  # Securities investment
            'total_credit': 'BBS_160',  # Total Credit (for LDR Regulated)
            'customer_loan': 'BBS_161',  # Customer Loans (for LDR Pure)
            'loan_provision_bs': 'BBS_169',  # Loan provision (balance sheet, negative)
            'total_deposit': 'BBS_330',  # Customer deposits (FIXED: was BBS_210)
            'valuable_papers': 'BBS_360',  # Valuable papers issued (Phát hành GTCG)
            'total_liabilities': 'BBS_300',  # Total liabilities (FIXED: was BBS_220)
            'total_equity': 'BBS_501',  # Owner's Equity (FIXED: was BBS_400 which is Total Liabilities)
            'charter_capital': 'BBS_411',

            # Notes - Asset Quality (Debt Groups)
            'total_loans_by_group': 'BNOT_4',  # Total loans by debt classification
            'debt_group1': 'BNOT_4_1',  # Group 1 - Standard
            'debt_group2': 'BNOT_4_2',  # Group 2 - Special Mention (FIXED: was BNOT_34)
            'npl_group3': 'BNOT_4_3',  # Group 3 - Substandard (NPL)
            'npl_group4': 'BNOT_4_4',  # Group 4 - Doubtful (NPL)
            'npl_group5': 'BNOT_4_5',  # Group 5 - Loss (NPL)
            'npl_amount_legacy': 'BNOT_35',  # NPL amount legacy (fallback)
            'debt_group2_legacy': 'BNOT_34',  # Group 2 debt (legacy, cumulative)
            'loan_provision_note': 'BNOT_29',  # Loan provision balance from notes

            # Notes - Deposits (BNOT_26 structure for CASA)
            'total_deposit_note': 'BNOT_26',  # Total deposits by type (denominator for CASA)
            'deposit_current': 'BNOT_26_1',  # Current account deposits (CASA component)
            'deposit_savings': 'BNOT_26_3',  # Savings deposits (CASA component)
            'deposit_other': 'BNOT_26_5',  # Other deposits (CASA component)
            'casa_balance_legacy': 'BNOT_42',  # CASA balance (legacy fallback)
            'term_deposit': 'BNOT_45',  # Term deposits

            # Notes - Funding structure (BNOT_13)
            'st_deposit_collateral': 'BNOT_13_1_1_3',  # Short-term deposit/collateral (for LDR Regulated)
        }

    def calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate bank-specific derived metrics."""

        # NOII = TOI - NII (Non-interest income)
        df['noii'] = df.get('toi', pd.Series([0]*len(df))).fillna(0) - \
                     df.get('nii', pd.Series([0]*len(df))).fillna(0)

        # PPOP = TOI - OPEX (Pre-provision operating profit)
        df['ppop'] = df.get('toi', pd.Series([0]*len(df))).fillna(0) - \
                     np.abs(df.get('opex', pd.Series([0]*len(df))).fillna(0))

        # Total Credit = BBS_160 (total credit including interbank)
        df['total_credit_bs'] = df.get('total_credit', pd.Series([0]*len(df))).fillna(0)

        # Customer Loan = BBS_161 (customer loans only, for LDR Pure)
        df['customer_loan_bs'] = df.get('customer_loan', pd.Series([0]*len(df))).fillna(0)

        # Total Customer Deposit
        df['total_customer_deposit'] = df.get('total_deposit', pd.Series([0]*len(df))).fillna(0)

        # IEA = Interest Earning Assets (approximation)
        df['iea'] = df.get('total_credit', pd.Series([0]*len(df))).fillna(0) + \
                    df.get('securities_investment', pd.Series([0]*len(df))).fillna(0) + \
                    df.get('placements_others', pd.Series([0]*len(df))).fillna(0)

        # IBL = Interest Bearing Liabilities (approximation)
        df['ibl'] = df.get('total_deposit', pd.Series([0]*len(df))).fillna(0)

        # NIM (quarterly) = NII / Average IEA * 4 * 100
        # Using simple approximation with current IEA
        df['nim_q'] = self.safe_divide(df['nii'], df['iea'], 400)  # Annualized

        # Asset Yield (quarterly)
        df['asset_yield_q'] = self.safe_divide(df['interest_income'], df['iea'], 400)

        # Funding Cost (quarterly) - use absolute value since interest_expense is negative
        df['funding_cost_q'] = self.safe_divide(np.abs(df['interest_expense']), df['ibl'], 400)

        # Loan Yield (quarterly)
        df['loan_yield_q'] = self.safe_divide(
            df['interest_income'] * 0.9,  # Approximation: 90% from loans
            df['total_credit_bs'],
            400
        )

        # CIR = OPEX / TOI * 100
        df['cir'] = self.safe_divide(np.abs(df['opex']), df['toi'], 100)

        # NII/TOI ratio
        df['nii_toi'] = self.safe_divide(df['nii'], df['toi'], 100)

        # NOII/TOI ratio
        df['noii_toi'] = self.safe_divide(df['noii'], df['toi'], 100)

        # NPL Amount calculation with multiple fallbacks:
        # Method 1: BNOT_4_3 + BNOT_4_4 + BNOT_4_5 (Group 3 + 4 + 5)
        # Method 2 (fallback): BNOT_4 - BNOT_4_1 - BNOT_4_2 (Total - Group1 - Group2)
        # Method 3 (fallback): abs(BNOT_35) legacy
        npl_g3 = df.get('npl_group3', pd.Series([0]*len(df))).fillna(0)
        npl_g4 = df.get('npl_group4', pd.Series([0]*len(df))).fillna(0)
        npl_g5 = df.get('npl_group5', pd.Series([0]*len(df))).fillna(0)
        npl_method1 = npl_g3 + npl_g4 + npl_g5

        # Fallback: BNOT_4 - BNOT_4_1 - BNOT_4_2
        total_loans_group = df.get('total_loans_by_group', pd.Series([0]*len(df))).fillna(0)
        debt_g1 = df.get('debt_group1', pd.Series([0]*len(df))).fillna(0)
        debt_g2 = df.get('debt_group2', pd.Series([0]*len(df))).fillna(0)
        npl_method2 = total_loans_group - debt_g1 - debt_g2
        npl_method2 = np.where(npl_method2 > 0, npl_method2, 0)  # Only positive values

        # Legacy fallback
        npl_legacy = df.get('npl_amount_legacy', pd.Series([0]*len(df))).fillna(0)
        npl_legacy_valid = np.where(npl_legacy > 0, npl_legacy, 0)

        # Use method 1 if > 0, else method 2 if > 0, else legacy
        df['npl_amount'] = np.where(
            npl_method1 > 0, npl_method1,
            np.where(npl_method2 > 0, npl_method2, npl_legacy_valid)
        )

        # NPL Ratio = NPL / Total Credit * 100
        df['npl_ratio'] = self.safe_divide(df['npl_amount'], df['total_credit_bs'], 100)

        # Group 2 Ratio - now using BNOT_4_2 directly
        df['debt_group2_ratio'] = self.safe_divide(
            df.get('debt_group2', pd.Series([0]*len(df))).fillna(0),
            df['total_credit_bs'],
            100
        )

        # Loan Provision Balance = abs(BBS_169)
        # BBS_169 is negative on balance sheet, so take absolute value
        df['loan_provision_balance'] = np.abs(df.get('loan_provision_bs', pd.Series([0]*len(df))).fillna(0))

        # LLCR = Provision / NPL * 100
        df['llcr'] = self.safe_divide(
            df['loan_provision_balance'],
            np.where(df['npl_amount'] > 0, df['npl_amount'], 1),  # Avoid division by zero
            100
        )

        # Provision to Loan
        df['provision_to_loan'] = self.safe_divide(
            df['loan_provision_balance'],
            df['total_credit_bs'],
            100
        )

        # Credit Cost = Provision Expense / Total Credit * 100 (annualized)
        df['credit_cost'] = self.safe_divide(
            np.abs(df.get('provision_expense', pd.Series([0]*len(df))).fillna(0)),
            df['total_credit_bs'],
            400  # Annualized
        )

        # CASA Ratio = (BNOT_26_1 + BNOT_26_3 + BNOT_26_5) / BNOT_26 * 100
        # CASA = Current account + Savings deposits + Other deposits
        deposit_current = df.get('deposit_current', pd.Series([0]*len(df))).fillna(0)
        deposit_savings = df.get('deposit_savings', pd.Series([0]*len(df))).fillna(0)
        deposit_other = df.get('deposit_other', pd.Series([0]*len(df))).fillna(0)
        total_deposit_note = df.get('total_deposit_note', pd.Series([0]*len(df))).fillna(0)

        casa_balance_new = deposit_current + deposit_savings + deposit_other

        # Fallback to legacy BNOT_42 if new formula gives 0
        casa_balance_legacy = df.get('casa_balance_legacy', pd.Series([0]*len(df))).fillna(0)
        casa_balance = np.where(casa_balance_new > 0, casa_balance_new, casa_balance_legacy)

        # Use BNOT_26 as denominator if available, else use BBS_330 (total_customer_deposit)
        casa_denominator = np.where(total_deposit_note > 0, total_deposit_note, df['total_customer_deposit'])

        df['casa_ratio'] = self.safe_divide(casa_balance, casa_denominator, 100)

        # LDR Pure = BBS_161 / BBS_330 * 100
        # Customer Loans / Customer Deposits
        df['ldr_pure'] = self.safe_divide(
            df.get('customer_loan', pd.Series([0]*len(df))).fillna(0),
            df['total_customer_deposit'],
            100
        )

        # LDR Regulated = (BBS_160 + BNOT_13_1_1_3) / (BBS_330 + BBS_360) * 100
        # (Total Credit + ST Deposit Collateral) / (Customer Deposits + Valuable Papers)
        total_credit_adj = df.get('total_credit', pd.Series([0]*len(df))).fillna(0) + \
                           df.get('st_deposit_collateral', pd.Series([0]*len(df))).fillna(0)
        total_funding = df['total_customer_deposit'] + \
                        df.get('valuable_papers', pd.Series([0]*len(df))).fillna(0)
        df['ldr_regulated'] = self.safe_divide(total_credit_adj, total_funding, 100)

        # ROAE and ROAA - need TTM calculation first
        df = self.calculate_ttm(df, ['npatmi'])

        # Average equity (2-quarter rolling)
        df['equity_avg_2q'] = df.groupby('SECURITY_CODE')['total_equity'].transform(
            lambda x: x.rolling(window=2, min_periods=1).mean()
        )

        # Average assets (2-quarter rolling)
        df['assets_avg_2q'] = df.groupby('SECURITY_CODE')['total_assets'].transform(
            lambda x: x.rolling(window=2, min_periods=1).mean()
        )

        # ROAE TTM = NPATMI_TTM / Average Equity * 100
        df['roea_ttm'] = self.safe_divide(df['npatmi_ttm'], df['equity_avg_2q'], 100)

        # ROAA TTM = NPATMI_TTM / Average Assets * 100
        df['roaa_ttm'] = self.safe_divide(df['npatmi_ttm'], df['assets_avg_2q'], 100)

        # EPS TTM
        charter = df.get('charter_capital', pd.Series([1]*len(df))).fillna(1) / 10000  # to shares
        df['eps_ttm'] = self.safe_divide(df['npatmi_ttm'], charter)

        # BVPS = Equity / Shares
        df['bvps'] = self.safe_divide(df['total_equity'], charter)

        # Growth rates (YoY) - need to calculate after sorting
        df = df.sort_values(['SECURITY_CODE', 'report_date'] if 'report_date' in df.columns else ['SECURITY_CODE', 'REPORT_DATE'])

        growth_cols = ['nii', 'toi', 'ppop', 'pbt', 'npatmi']
        for col in growth_cols:
            if col in df.columns:
                df[f'{col}_growth_yoy'] = df.groupby('SECURITY_CODE')[col].pct_change(periods=4) * 100

        # YTD growth for balance sheet items (vs Q4 of previous year)
        bs_cols = ['total_credit', 'total_loan', 'total_assets', 'total_customer_deposit']
        for col in bs_cols:
            if col in df.columns:
                col_name = col.replace('total_', '')
                df[f'{col_name}_growth_ytd'] = df.groupby('SECURITY_CODE')[col].pct_change(periods=1) * 100

        return df

    def select_output_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select output columns for bank metrics."""
        output_cols = [
            # ID columns
            'symbol', 'report_date', 'year', 'quarter', 'freq_code',

            # Balance Sheet items
            'total_assets', 'total_loan', 'total_credit', 'total_customer_deposit',
            'total_liabilities', 'total_equity', 'charter_capital',
            'npl_amount', 'debt_group2', 'loan_provision_balance',

            # Income Statement items
            'nii', 'noii', 'toi', 'opex', 'ppop', 'provision_expense', 'pbt', 'npatmi',
            'interest_income', 'interest_expense',

            # IEA/IBL
            'iea', 'ibl', 'equity_avg_2q', 'assets_avg_2q',

            # Yield/Cost metrics (%)
            'nim_q', 'asset_yield_q', 'funding_cost_q', 'loan_yield_q',

            # Efficiency metrics (%)
            'cir', 'nii_toi', 'noii_toi',

            # Asset Quality metrics (%)
            'npl_ratio', 'debt_group2_ratio', 'llcr', 'provision_to_loan', 'credit_cost',

            # Funding metrics (%)
            'casa_ratio', 'ldr_pure', 'ldr_regulated',

            # Profitability (%)
            'roea_ttm', 'roaa_ttm',

            # Growth metrics (%)
            'nii_growth_yoy', 'toi_growth_yoy', 'ppop_growth_yoy',
            'pbt_growth_yoy', 'npatmi_growth_yoy',
            'credit_growth_ytd', 'loan_growth_ytd', 'asset_growth_ytd', 'customer_deposit_growth_ytd',

            # Per share
            'eps_ttm', 'bvps',

            # TTM
            'npatmi_ttm',
        ]

        available_cols = [c for c in output_cols if c in df.columns]
        return df[available_cols].copy()


# ==============================================================================
# INSURANCE CALCULATOR (Simplified)
# ==============================================================================

class InsuranceCalculator(EntityCalculator):
    """Calculator for Insurance entities."""

    def __init__(self):
        super().__init__('insurance')

    def get_metric_mapping(self) -> Dict[str, str]:
        """Metric code mapping for insurance financials."""
        return {
            # Income Statement
            'premium_income': 'IIS_01',  # Doanh thu phí bảo hiểm
            'premium_ceded': 'IIS_02',   # Phí nhượng tái bảo hiểm
            'net_premium': 'IIS_03',     # Doanh thu phí bảo hiểm thuần
            'gross_profit_insurance': 'IIS_19',  # Lợi nhuận gộp hoạt động KDBH
            'investment_income': 'IIS_22',  # Thu nhập hoạt động tài chính
            'other_income': 'IIS_31',    # Thu nhập hoạt động khác
            'operating_expense': 'IIS_32',  # Chi phí hoạt động khác
            'pbt': 'IIS_50',             # Tổng lợi nhuận kế toán trước thuế
            'npat': 'IIS_60',            # Lợi nhuận sau thuế TNDN
            'npatmi': 'IIS_62',          # Lợi nhuận sau thuế của chủ sở hữu

            # Balance Sheet
            'total_assets': 'IBS_100',
            'cash': 'IBS_111',
            'investments': 'IBS_130',
            'receivables': 'IBS_140',
            'total_liabilities': 'IBS_200',
            'insurance_reserves': 'IBS_210',
            'total_equity': 'IBS_300',
            'charter_capital': 'IBS_311',
        }

    def calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate insurance-specific derived metrics."""

        # Combined Ratio = (Claims + Expenses) / Net Premium * 100
        claims = np.abs(df.get('claims_expense', pd.Series([0]*len(df))).fillna(0))
        expenses = np.abs(df.get('operating_expense', pd.Series([0]*len(df))).fillna(0))
        df['combined_ratio'] = self.safe_divide(claims + expenses, df['net_premium'], 100)

        # Loss Ratio = Claims / Net Premium * 100
        df['loss_ratio'] = self.safe_divide(claims, df['net_premium'], 100)

        # Expense Ratio = Operating Expense / Net Premium * 100
        df['expense_ratio'] = self.safe_divide(expenses, df['net_premium'], 100)

        # ROE and ROA
        df['roe'] = self.safe_divide(df['npatmi'], df['total_equity'], 100)
        df['roa'] = self.safe_divide(df['npatmi'], df['total_assets'], 100)

        # Solvency Ratio = Equity / Insurance Reserves * 100
        df['solvency_ratio'] = self.safe_divide(
            df['total_equity'],
            df.get('insurance_reserves', pd.Series([1]*len(df))).fillna(1),
            100
        )

        # Investment Yield = Investment Income / Investments * 100 (annualized)
        df['investment_yield'] = self.safe_divide(
            df.get('investment_income', pd.Series([0]*len(df))).fillna(0),
            df.get('investments', pd.Series([1]*len(df))).fillna(1),
            400
        )

        # Net Margin
        df['net_margin'] = self.safe_divide(df['npatmi'], df['net_premium'], 100)

        # TTM
        df = self.calculate_ttm(df, ['net_premium', 'npatmi'])

        # Per share
        charter = df.get('charter_capital', pd.Series([1]*len(df))).fillna(1) / 10000
        df['eps'] = self.safe_divide(df['npatmi'], charter)
        df['bvps'] = self.safe_divide(df['total_equity'], charter)

        return df

    def select_output_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select output columns for insurance metrics."""
        output_cols = [
            'symbol', 'report_date', 'year', 'quarter', 'freq_code',
            'premium_income', 'net_premium', 'investment_income',
            'claims_expense', 'operating_expense', 'pbt', 'npatmi',
            'total_assets', 'investments', 'insurance_reserves',
            'total_liabilities', 'total_equity',
            'combined_ratio', 'loss_ratio', 'expense_ratio',
            'roe', 'roa', 'solvency_ratio', 'investment_yield', 'net_margin',
            'net_premium_ttm', 'npatmi_ttm', 'eps', 'bvps'
        ]
        available_cols = [c for c in output_cols if c in df.columns]
        return df[available_cols].copy()


# ==============================================================================
# SECURITY CALCULATOR (Simplified)
# ==============================================================================

class SecurityCalculator(EntityCalculator):
    """Calculator for Security/Brokerage entities."""

    def __init__(self):
        super().__init__('security')

    def get_metric_mapping(self) -> Dict[str, str]:
        """Metric code mapping for security company financials."""
        return {
            # Income Statement
            'brokerage_income': 'SIS_11',
            'margin_income': 'SIS_13',
            'proprietary_income': 'SIS_14',
            'underwriting_income': 'SIS_15',
            'advisory_income': 'SIS_16',
            'custody_income': 'SIS_17',
            'total_revenue': 'SIS_20',
            'operating_expense': 'SIS_40',  # Total expenses (FIXED: was SIS_30 which is a small line item)
            'pbt': 'SIS_50',
            'npatmi': 'SIS_201',  # NPATMI - Lợi nhuận sau thuế của cổ đông công ty mẹ

            # Balance Sheet
            'total_assets': 'SBS_100',
            'cash': 'SBS_110',
            'margin_receivable': 'SBS_130',
            'proprietary_securities': 'SBS_140',
            'total_liabilities': 'SBS_200',
            'margin_payable': 'SBS_210',
            'total_equity': 'SBS_300',
            'charter_capital': 'SBS_311',
        }

    def calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate security company-specific derived metrics."""

        # Cost-to-Income Ratio
        df['cir'] = self.safe_divide(
            np.abs(df.get('operating_expense', pd.Series([0]*len(df))).fillna(0)),
            df['total_revenue'],
            100
        )

        # Revenue breakdown ratios
        df['brokerage_ratio'] = self.safe_divide(
            df.get('brokerage_income', pd.Series([0]*len(df))).fillna(0),
            df['total_revenue'],
            100
        )
        df['margin_ratio'] = self.safe_divide(
            df.get('margin_income', pd.Series([0]*len(df))).fillna(0),
            df['total_revenue'],
            100
        )
        df['proprietary_ratio'] = self.safe_divide(
            df.get('proprietary_income', pd.Series([0]*len(df))).fillna(0),
            df['total_revenue'],
            100
        )

        # ROE and ROA
        df['roe'] = self.safe_divide(df['npatmi'], df['total_equity'], 100)
        df['roa'] = self.safe_divide(df['npatmi'], df['total_assets'], 100)

        # Net Margin
        df['net_margin'] = self.safe_divide(df['npatmi'], df['total_revenue'], 100)

        # Leverage = Total Assets / Equity
        df['leverage'] = self.safe_divide(df['total_assets'], df['total_equity'])

        # Margin lending ratio = Margin Receivable / Equity * 100
        df['margin_lending_ratio'] = self.safe_divide(
            df.get('margin_receivable', pd.Series([0]*len(df))).fillna(0),
            df['total_equity'],
            100
        )

        # TTM
        df = self.calculate_ttm(df, ['total_revenue', 'npatmi'])

        # Per share
        charter = df.get('charter_capital', pd.Series([1]*len(df))).fillna(1) / 10000
        df['eps'] = self.safe_divide(df['npatmi'], charter)
        df['bvps'] = self.safe_divide(df['total_equity'], charter)

        return df

    def select_output_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select output columns for security metrics."""
        output_cols = [
            'symbol', 'report_date', 'year', 'quarter', 'freq_code',
            'brokerage_income', 'margin_income', 'proprietary_income',
            'underwriting_income', 'advisory_income', 'total_revenue',
            'operating_expense', 'pbt', 'npatmi',
            'total_assets', 'margin_receivable', 'proprietary_securities',
            'total_liabilities', 'margin_payable', 'total_equity',
            'cir', 'brokerage_ratio', 'margin_ratio', 'proprietary_ratio',
            'roe', 'roa', 'net_margin', 'leverage', 'margin_lending_ratio',
            'total_revenue_ttm', 'npatmi_ttm', 'eps', 'bvps'
        ]
        available_cols = [c for c in output_cols if c in df.columns]
        return df[available_cols].copy()


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def run_all():
    """Run all calculators."""
    calculators = [
        CompanyCalculator(),
        BankCalculator(),
        InsuranceCalculator(),
        SecurityCalculator(),
    ]

    results = {}
    for calc in calculators:
        try:
            df = calc.run()
            results[calc.entity_type] = df
            logger.info(f"{calc.entity_type.upper()} completed successfully")
        except Exception as e:
            logger.error(f"Error running {calc.entity_type} calculator: {e}")
            import traceback
            traceback.print_exc()

    return results


def run_entity(entity_type: str):
    """Run calculator for specific entity type."""
    calculators = {
        'company': CompanyCalculator,
        'bank': BankCalculator,
        'insurance': InsuranceCalculator,
        'security': SecurityCalculator,
    }

    if entity_type not in calculators:
        raise ValueError(f"Unknown entity type: {entity_type}. Valid options: {list(calculators.keys())}")

    calc = calculators[entity_type]()
    return calc.run()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run Financial Calculators')
    parser.add_argument('--entity', type=str, default=None,
                       help='Entity type to run (company, bank, insurance, security). Runs all if not specified.')

    args = parser.parse_args()

    if args.entity:
        run_entity(args.entity)
    else:
        run_all()


if __name__ == "__main__":
    main()
