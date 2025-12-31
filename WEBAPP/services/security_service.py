"""
Security Service - Data Loading Layer
=====================================

Service for loading securities/brokerage company financial data from parquet files.
Uses DataMappingRegistry for path resolution.

Usage:
    from WEBAPP.services.security_service import SecurityService

    service = SecurityService()
    df = service.get_financial_data("SSI", "Quarterly")

Author: AI Assistant
Date: 2025-12-31
Version: 2.0.0 (Registry Integration)
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List

from .base_service import BaseService


class SecurityService(BaseService):
    """Service layer for Securities/Brokerage company financial data."""

    DATA_SOURCE = "security_metrics"
    ENTITY_TYPE = "security"

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize SecurityService.

        Args:
            data_root: Root data directory (for testing, defaults to registry path)
        """
        super().__init__(data_root)
        self._master_symbols = None

    def _load_master_symbols(self) -> List[str]:
        """Load master symbols filtered list for SECURITY entity."""
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
                self._master_symbols = data.get('symbols_by_entity', {}).get('SECURITY', [])
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
        Load financial data for a securities company ticker.

        Args:
            ticker: Stock symbol (e.g., "SSI", "VND", "HCM")
            period: "Quarterly" or "Yearly"
            limit: Maximum number of records to return (most recent)

        Returns:
            DataFrame with financial metrics sorted by date
        """
        # Use base class load_data() - gets path from registry
        df = self.load_data(validate_schema=False)

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
        """Get latest quarter metrics for a securities company ticker."""
        df = self.get_financial_data(ticker, "Quarterly", limit=1)
        return df.iloc[-1].to_dict() if not df.empty else {}

    def get_available_tickers(self) -> List[str]:
        """Get list of available securities company tickers (filtered by master_symbols for liquidity)."""
        df = self.load_data(columns=['symbol'], validate_schema=False)
        all_tickers = set(df['symbol'].unique().tolist())

        # Filter by master symbols (liquid tickers only)
        master_symbols = self._load_master_symbols()
        if master_symbols:
            filtered = [t for t in master_symbols if t in all_tickers]
            return sorted(filtered)

        return sorted(all_tickers)

    def get_peer_comparison(self, ticker: str) -> pd.DataFrame:
        """Get peer comparison data for securities companies."""
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
