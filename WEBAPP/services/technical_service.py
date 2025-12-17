"""
Technical Service - Data Loading Layer
======================================

Service for loading technical indicators data from parquet files.
Uses SymbolLoader for liquid tickers (315 symbols with >1B VND/day trading value).

Usage:
    from WEBAPP.services.technical_service import TechnicalService

    service = TechnicalService()
    df = service.get_technical_data("VNM", limit=100)

Updated: 2025-12-17 - Use SymbolLoader for symbol lists
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List


class TechnicalService:
    """Service layer for Technical indicators data."""

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize TechnicalService.

        Args:
            data_root: Root data directory (defaults to PROJECT_ROOT/DATA)
        """
        if data_root is None:
            current_file = Path(__file__).resolve()
            project_root = current_file.parents[2]
            data_root = project_root / "DATA"

        self.data_path = data_root / "processed" / "technical"

        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Technical data path not found: {self.data_path}\n"
                f"Please ensure DATA/processed/technical/ exists."
            )

        # Initialize SymbolLoader
        self._symbol_loader = None

    def get_technical_data(
        self,
        ticker: str,
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load technical data for a ticker.

        Args:
            ticker: Stock symbol (e.g., "VNM", "ACB")
            limit: Maximum number of records to return (most recent)
            start_date: Filter from this date (YYYY-MM-DD)
            end_date: Filter to this date (YYYY-MM-DD)

        Returns:
            DataFrame with technical indicators sorted by date
        """
        parquet_file = self.data_path / "basic_data.parquet"

        if not parquet_file.exists():
            raise FileNotFoundError(
                f"Technical data file not found: {parquet_file}\n"
                f"Please run the technical calculator first."
            )

        df = pd.read_parquet(parquet_file)
        df = df[df['symbol'] == ticker].copy()

        if df.empty:
            return pd.DataFrame()

        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

            # Apply date filters
            if start_date:
                df = df[df['date'] >= start_date]
            if end_date:
                df = df[df['date'] <= end_date]

            df = df.sort_values('date')

        if limit:
            df = df.tail(limit)

        return df

    def get_latest_indicators(self, ticker: str) -> dict:
        """Get latest technical indicators for a ticker."""
        df = self.get_technical_data(ticker, limit=1)
        return df.iloc[-1].to_dict() if not df.empty else {}

    def get_available_tickers(self, entity_type: Optional[str] = None) -> List[str]:
        """
        Get list of liquid tickers from master_symbols.json.
        Returns 315 symbols with >1B VND/day trading value.

        Args:
            entity_type: 'COMPANY', 'BANK', 'SECURITY', 'INSURANCE' or None for all

        Returns:
            List of liquid symbols
        """
        try:
            if self._symbol_loader is None:
                from WEBAPP.core.symbol_loader import SymbolLoader
                self._symbol_loader = SymbolLoader()

            if entity_type:
                return self._symbol_loader.get_symbols_by_entity(entity_type.upper())
            return self._symbol_loader.get_all_symbols()
        except Exception as e:
            print(f"Warning: Could not load SymbolLoader - {e}")
            # Fallback to parquet if SymbolLoader fails
            parquet_file = self.data_path / "basic_data.parquet"
            if not parquet_file.exists():
                return []
            df = pd.read_parquet(parquet_file, columns=['symbol'])
            return sorted(df['symbol'].unique().tolist())

    def get_market_breadth(self) -> pd.DataFrame:
        """Get market breadth data."""
        breadth_path = self.data_path / "market_breadth"

        if not breadth_path.exists():
            return pd.DataFrame()

        # Find latest breadth file
        files = list(breadth_path.glob("*.parquet"))
        if not files:
            return pd.DataFrame()

        # Return latest file
        latest_file = max(files, key=lambda x: x.stat().st_mtime)
        return pd.read_parquet(latest_file)

    def get_sector_breadth(self, sector: Optional[str] = None) -> pd.DataFrame:
        """Get sector breadth data."""
        breadth_path = self.data_path / "sector_breadth"

        if not breadth_path.exists():
            return pd.DataFrame()

        files = list(breadth_path.glob("*.parquet"))
        if not files:
            return pd.DataFrame()

        latest_file = max(files, key=lambda x: x.stat().st_mtime)
        df = pd.read_parquet(latest_file)

        if sector and 'sector' in df.columns:
            df = df[df['sector'] == sector]

        return df
