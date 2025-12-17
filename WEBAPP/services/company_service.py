"""
Company Service - Data Loading Layer
====================================

Service for loading company financial data from parquet files.

Usage:
    from WEBAPP.services.company_service import CompanyService

    service = CompanyService()
    df = service.get_financial_data("VNM", "Quarterly")
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List

# Column groups for efficient data loading (Option B - column selection)
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


class CompanyService:
    """Service layer for Company financial data."""

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize CompanyService.

        Args:
            data_root: Root data directory (defaults to PROJECT_ROOT/DATA)
        """
        if data_root is None:
            # Auto-detect project root
            current_file = Path(__file__).resolve()
            project_root = current_file.parents[2]  # Go up to project root
            data_root = project_root / "DATA"

        self.data_root = data_root
        self.data_path = data_root / "processed" / "fundamental" / "company"
        self._master_symbols = None

        # Check if path exists
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Company data path not found: {self.data_path}\n"
                f"Please ensure DATA/processed/fundamental/company/ exists."
            )

    def _load_master_symbols(self) -> List[str]:
        """Load master symbols filtered list for COMPANY entity."""
        if self._master_symbols is not None:
            return self._master_symbols

        import json

        # Try config/metadata first, then DATA/metadata
        project_root = self.data_root.parent
        locations = [
            project_root / "config" / "metadata" / "master_symbols.json",
            self.data_root / "metadata" / "master_symbols.json",
        ]

        for master_file in locations:
            if master_file.exists():
                with open(master_file) as f:
                    data = json.load(f)
                # Get COMPANY symbols only
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
            ticker: Stock symbol (e.g., "VNM", "ACB")
            period: "Quarterly", "Yearly", or "TTM"
            limit: Maximum number of records to return (most recent)
            table_type: Column group to load - "all", "income_statement",
                       "balance_sheet", "cash_flow", or "ratios"

        Returns:
            DataFrame with financial metrics sorted by date

        Example:
            >>> service = CompanyService()
            >>> df = service.get_financial_data("VNM", "Quarterly", limit=8)
            >>> print(df[['report_date', 'net_revenue', 'npatmi']].tail())

            # Load only income statement columns for efficiency
            >>> df_is = service.get_financial_data("VNM", "Quarterly", table_type="income_statement")
        """
        # Load from parquet
        parquet_file = self.data_path / "company_financial_metrics.parquet"

        if not parquet_file.exists():
            raise FileNotFoundError(
                f"Company metrics file not found: {parquet_file}\n"
                f"Please run the company calculator first."
            )

        # Determine columns to load
        columns = None
        if table_type != "all" and table_type in COLUMN_GROUPS:
            # Get requested columns, filter to only those that exist in file
            all_parquet_cols = pd.read_parquet(parquet_file, columns=[]).columns.tolist()
            columns = [c for c in COLUMN_GROUPS[table_type] if c in all_parquet_cols]

        df = pd.read_parquet(parquet_file, columns=columns)

        # Filter by ticker
        df = df[df['symbol'] == ticker].copy()

        if df.empty:
            return pd.DataFrame()

        # Filter by period
        if period == "Quarterly":
            df = df[df['freq_code'] == 'Q']
        elif period == "Yearly":
            df = df[df['freq_code'] == 'Y']
        # For TTM, keep all rows (TTM columns already in data)

        # Sort by date
        df = df.sort_values('report_date')

        # Limit records if specified
        if limit:
            df = df.tail(limit)

        return df

    def get_latest_metrics(self, ticker: str) -> Dict:
        """
        Get latest quarter metrics for a ticker.

        Args:
            ticker: Stock symbol

        Returns:
            Dictionary with latest metrics

        Example:
            >>> service = CompanyService()
            >>> latest = service.get_latest_metrics("VNM")
            >>> print(f"Revenue: {latest['net_revenue']:.1f}B VND")
        """
        df = self.get_financial_data(ticker, "Quarterly", limit=1)
        return df.iloc[-1].to_dict() if not df.empty else {}

    def get_available_tickers(self) -> List[str]:
        """
        Get list of available company tickers (filtered by master_symbols for liquidity).

        Returns:
            Sorted list of ticker symbols

        Example:
            >>> service = CompanyService()
            >>> tickers = service.get_available_tickers()
            >>> print(f"Found {len(tickers)} companies")
        """
        parquet_file = self.data_path / "company_financial_metrics.parquet"

        if not parquet_file.exists():
            return []

        df = pd.read_parquet(parquet_file, columns=['symbol'])
        all_tickers = set(df['symbol'].unique().tolist())

        # Filter by master symbols (liquid tickers only)
        master_symbols = self._load_master_symbols()
        if master_symbols:
            filtered = [t for t in master_symbols if t in all_tickers]
            return sorted(filtered)

        return sorted(all_tickers)

    def get_peer_comparison(self, ticker: str) -> pd.DataFrame:
        """
        Get peer comparison data (latest quarter for ticker and peers).

        Args:
            ticker: Stock symbol

        Returns:
            DataFrame with latest metrics for ticker and peers

        Example:
            >>> service = CompanyService()
            >>> peers_df = service.get_peer_comparison("VNM")
            >>> print(peers_df[['symbol', 'net_revenue', 'roe']])
        """
        try:
            from config.registries import SectorRegistry

            sector_reg = SectorRegistry()
            peers = sector_reg.get_peers(ticker)

            # Load data for all peers
            dfs = []
            for peer in peers:
                peer_df = self.get_financial_data(peer, "Quarterly", limit=1)
                if not peer_df.empty:
                    dfs.append(peer_df.iloc[-1])

            return pd.DataFrame(dfs) if dfs else pd.DataFrame()

        except Exception as e:
            print(f"Warning: Could not load peer comparison - {e}")
            return pd.DataFrame()
