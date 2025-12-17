"""
Bank Service - Data Loading Layer
=================================

Service for loading bank financial data from parquet files.

Usage:
    from WEBAPP.services.bank_service import BankService

    service = BankService()
    df = service.get_financial_data("ACB", "Quarterly")
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List


class BankService:
    """Service layer for Bank financial data."""

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize BankService.

        Args:
            data_root: Root data directory (defaults to PROJECT_ROOT/DATA)
        """
        if data_root is None:
            current_file = Path(__file__).resolve()
            project_root = current_file.parents[2]
            data_root = project_root / "DATA"

        self.data_root = data_root
        self.data_path = data_root / "processed" / "fundamental" / "bank"
        self._master_symbols = None

        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Bank data path not found: {self.data_path}\n"
                f"Please ensure DATA/processed/fundamental/bank/ exists."
            )

    def _load_master_symbols(self) -> List[str]:
        """Load master symbols filtered list for BANK entity."""
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
                self._master_symbols = data.get('symbols_by_entity', {}).get('BANK', [])
                return self._master_symbols

        self._master_symbols = []
        return self._master_symbols

    def get_financial_data(
        self,
        ticker: str,
        period: str = "Quarterly",
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Load financial data for a bank ticker.

        Args:
            ticker: Stock symbol (e.g., "ACB", "VCB", "TCB")
            period: "Quarterly" or "Yearly"
            limit: Maximum number of records to return (most recent)

        Returns:
            DataFrame with financial metrics sorted by date
        """
        parquet_file = self.data_path / "bank_financial_metrics.parquet"

        if not parquet_file.exists():
            raise FileNotFoundError(
                f"Bank metrics file not found: {parquet_file}\n"
                f"Please run the bank calculator first."
            )

        df = pd.read_parquet(parquet_file)
        df = df[df['symbol'] == ticker].copy()

        if df.empty:
            return pd.DataFrame()

        if period == "Quarterly":
            df = df[df['freq_code'] == 'Q']
        elif period == "Yearly":
            df = df[df['freq_code'] == 'Y']

        df = df.sort_values('report_date')

        if limit:
            df = df.tail(limit)

        return df

    def get_latest_metrics(self, ticker: str) -> Dict:
        """Get latest quarter metrics for a bank ticker."""
        df = self.get_financial_data(ticker, "Quarterly", limit=1)
        return df.iloc[-1].to_dict() if not df.empty else {}

    def get_available_tickers(self) -> List[str]:
        """Get list of available bank tickers (filtered by master_symbols for liquidity)."""
        parquet_file = self.data_path / "bank_financial_metrics.parquet"

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
        """Get peer comparison data for banks."""
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
