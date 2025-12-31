"""
Company Service - Data Loading Layer
====================================

Service for loading company financial data from parquet files.
Uses DataMappingRegistry for path resolution.

Usage:
    from WEBAPP.services.company_service import CompanyService

    service = CompanyService()
    df = service.get_financial_data("VNM", "Quarterly")

Author: AI Assistant
Date: 2025-12-31
Version: 2.0.0 (Registry Integration)
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List

from .base_service import BaseService

# Column groups for efficient data loading
COLUMN_GROUPS = {
    'meta': ['symbol', 'report_date', 'year', 'quarter', 'freq_code'],
    'income_statement': [
        'symbol', 'report_date', 'year', 'quarter', 'freq_code',
        'net_revenue', 'cogs', 'gross_profit', 'sga', 'ebit',
        'ebitda', 'ebt', 'npatmi', 'net_finance_income', 'depreciation',
        'gross_profit_margin', 'ebit_margin', 'ebitda_margin', 'net_margin',
        'net_revenue_ttm', 'npatmi_ttm'
    ],
    'balance_sheet': [
        'symbol', 'report_date', 'year', 'quarter', 'freq_code',
        'total_assets', 'total_liabilities', 'total_equity',
        'current_assets', 'current_liabilities', 'cash', 'inventory',
        'account_receivable', 'tangible_fixed_asset', 'st_debt', 'lt_debt',
        'net_debt', 'working_capital', 'common_shares',
        'current_ratio', 'quick_ratio', 'cash_ratio',
        'debt_to_equity', 'debt_to_assets',
        'depreciation_rate', 'cip_rate', 'gross_ppe', 'accumulated_depreciation', 'cip'
    ],
    'cash_flow': [
        'symbol', 'report_date', 'year', 'quarter', 'freq_code',
        'operating_cf', 'investment_cf', 'financing_cf', 'capex',
        'depreciation', 'fcf', 'fcff', 'fcfe',
        'delta_working_capital', 'delta_wc', 'delta_net_borrowing', 'operating_cf_ttm'
    ],
    'ratios': [
        'symbol', 'report_date', 'year', 'quarter', 'freq_code',
        'roe', 'roa', 'asset_turnover', 'inventory_turnover',
        'receivables_turnover', 'eps', 'bvps'
    ]
}


class CompanyService(BaseService):
    """Service layer for Company financial data."""

    DATA_SOURCE = "company_metrics"
    ENTITY_TYPE = "company"

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize CompanyService.

        Args:
            data_root: Root data directory (for testing, defaults to registry path)
        """
        super().__init__(data_root)
        self._master_symbols = None

    def _load_master_symbols(self) -> List[str]:
        """Load master symbols filtered list for COMPANY entity."""
        if self._master_symbols is not None:
            return self._master_symbols

        import json

        locations = [
            self.project_root / "config" / "metadata" / "master_symbols.json",
            self.data_root / "metadata" / "master_symbols.json",
        ]

        for master_file in locations:
            if master_file.exists():
                with open(master_file) as f:
                    data = json.load(f)
                self._master_symbols = data.get('symbols_by_entity', {}).get('COMPANY', [])
                return self._master_symbols

        self._master_symbols = []
        return self._master_symbols

    def get_financial_data(
        self,
        ticker: str,
        period: str = "Quarterly",
        limit: Optional[int] = None,
        table_type: str = "all"
    ) -> pd.DataFrame:
        """
        Load financial data for a company ticker.

        Args:
            ticker: Stock symbol (e.g., "VNM", "FPT")
            period: "Quarterly", "Yearly", or "TTM"
            limit: Maximum number of records to return (most recent)
            table_type: Column group to load - "all", "income_statement",
                       "balance_sheet", "cash_flow", or "ratios"

        Returns:
            DataFrame with financial metrics sorted by date
        """
        # Determine columns to load
        columns = None
        if table_type != "all" and table_type in COLUMN_GROUPS:
            columns = COLUMN_GROUPS[table_type]

        # Use base class - gets path from registry
        try:
            df = self.load_data(columns=columns, validate_schema=False)
        except Exception:
            # Fallback: load all columns if specified columns don't exist
            df = self.load_data(validate_schema=False)
            if columns:
                existing_cols = [c for c in columns if c in df.columns]
                if existing_cols:
                    df = df[existing_cols]

        # Filter by ticker
        df = df[df['symbol'] == ticker].copy()

        if df.empty:
            return pd.DataFrame()

        # Filter by period
        if period == "Quarterly":
            df = df[df['freq_code'] == 'Q']
        elif period == "Yearly":
            df = df[df['freq_code'] == 'Y']

        df = df.sort_values('report_date')

        if limit:
            df = df.tail(limit)

        return df

    def get_latest_metrics(self, ticker: str) -> Dict:
        """Get latest quarter metrics for a ticker."""
        df = self.get_financial_data(ticker, "Quarterly", limit=1)
        return df.iloc[-1].to_dict() if not df.empty else {}

    def get_available_tickers(self) -> List[str]:
        """Get list of available company tickers (filtered by master_symbols for liquidity)."""
        df = self.load_data(columns=['symbol'], validate_schema=False)
        all_tickers = set(df['symbol'].unique().tolist())

        # Filter by master symbols (liquid tickers only)
        master_symbols = self._load_master_symbols()
        if master_symbols:
            filtered = [t for t in master_symbols if t in all_tickers]
            return sorted(filtered)

        return sorted(all_tickers)

    def get_peer_comparison(self, ticker: str) -> pd.DataFrame:
        """Get peer comparison data (latest quarter for ticker and peers)."""
        try:
            from config.registries import SectorRegistry

            sector_reg = SectorRegistry()
            peers = sector_reg.get_peers(ticker)

            dfs = []
            for peer in peers:
                peer_df = self.get_financial_data(peer, "Quarterly", limit=1)
                if not peer_df.empty:
                    dfs.append(peer_df.iloc[-1])

            return pd.DataFrame(dfs) if dfs else pd.DataFrame()

        except Exception as e:
            print(f"Warning: Could not load peer comparison - {e}")
            return pd.DataFrame()
