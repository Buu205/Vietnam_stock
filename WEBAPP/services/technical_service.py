"""
Technical Service - Data Loading Layer
======================================

Service for loading technical indicators data from parquet files.
Uses DataMappingRegistry for path resolution.
Uses SymbolLoader for liquid tickers (315 symbols with >1B VND/day trading value).

Usage:
    from WEBAPP.services.technical_service import TechnicalService

    service = TechnicalService()
    df = service.get_technical_data("VNM", limit=100)

Author: AI Assistant
Date: 2025-12-31
Version: 2.1.0 (Registry Integration + Dashboard Methods)
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List

from .base_service import BaseService


class TechnicalService(BaseService):
    """Service layer for Technical indicators data."""

    DATA_SOURCE = "technical_basic"
    ENTITY_TYPE = "all"

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize TechnicalService.

        Args:
            data_root: Root data directory (for testing, defaults to registry path)
        """
        super().__init__(data_root)
        self._symbol_loader = None

    def _get_path(self, source_name: str) -> Path:
        """Get path for a data source via registry."""
        try:
            path_str = self.registry.get_path(source_name)
            if self._data_root:
                relative_str = str(path_str).replace("DATA/", "")
                return self._data_root / relative_str
            return self.project_root / path_str
        except KeyError:
            # Fallback to hardcoded path
            return self.data_root / "processed" / "technical" / f"{source_name}.parquet"

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
        parquet_file = self._get_path("technical_basic")

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
            parquet_file = self._get_path("technical_basic")
            if not parquet_file.exists():
                return []
            df = pd.read_parquet(parquet_file, columns=['symbol'])
            return sorted(df['symbol'].unique().tolist())

    def get_market_breadth(self) -> pd.DataFrame:
        """Get market breadth data."""
        breadth_path = self._get_path("market_breadth")

        if not breadth_path.exists():
            return pd.DataFrame()

        return pd.read_parquet(breadth_path)

    def get_sector_breadth(self, sector: Optional[str] = None) -> pd.DataFrame:
        """Get sector breadth data."""
        breadth_path = self._get_path("sector_breadth")

        if not breadth_path.exists():
            return pd.DataFrame()

        df = pd.read_parquet(breadth_path)

        if sector and 'sector' in df.columns:
            df = df[df['sector'] == sector]

        return df

    def get_market_regime(self) -> pd.DataFrame:
        """Get market regime history data."""
        regime_path = self._get_path("market_regime")

        if not regime_path.exists():
            return pd.DataFrame()

        return pd.read_parquet(regime_path)

    def get_money_flow(self, scope: str = "sector") -> pd.DataFrame:
        """
        Get money flow data.

        Args:
            scope: "individual" or "sector"

        Returns:
            DataFrame with money flow data
        """
        source_name = f"{scope}_money_flow"
        flow_path = self._get_path(source_name)

        if not flow_path.exists():
            return pd.DataFrame()

        return pd.read_parquet(flow_path)

    def get_rs_rating(self, ticker: Optional[str] = None) -> pd.DataFrame:
        """
        Get RS Rating data.

        Args:
            ticker: Optional ticker filter

        Returns:
            DataFrame with RS ratings
        """
        rs_path = self._get_path("stock_rs_rating")

        if not rs_path.exists():
            return pd.DataFrame()

        df = pd.read_parquet(rs_path)

        if ticker and 'symbol' in df.columns:
            df = df[df['symbol'] == ticker]

        return df

    def get_vnindex_indicators(self) -> pd.DataFrame:
        """Get VN-Index technical indicators."""
        vnindex_path = self._get_path("vnindex_indicators")

        if not vnindex_path.exists():
            return pd.DataFrame()

        return pd.read_parquet(vnindex_path)

    # =========================================================================
    # Technical Dashboard Methods (Tab 1-4)
    # =========================================================================

    def get_market_state(self) -> pd.DataFrame:
        """
        Get current market state (regime, breadth, exposure).
        Used by Technical Dashboard Tab 1: Market Overview.

        Returns:
            DataFrame with single row containing market state
        """
        state_path = self._get_path("market_state_latest")

        if not state_path.exists():
            return pd.DataFrame()

        return pd.read_parquet(state_path)

    def get_sector_ranking(self) -> pd.DataFrame:
        """
        Get current sector ranking with scores.
        Used by Technical Dashboard Tab 2: Sector Rotation.

        Returns:
            DataFrame with 19 sectors ranked by composite score
        """
        ranking_path = self._get_path("sector_ranking_latest")

        if not ranking_path.exists():
            return pd.DataFrame()

        return pd.read_parquet(ranking_path)

    def get_sector_rrg(self) -> pd.DataFrame:
        """
        Get RRG (Relative Rotation Graph) coordinates for sectors.
        Used by Technical Dashboard Tab 2: Sector Rotation.

        Returns:
            DataFrame with sector RRG data (rs_ratio, rs_momentum, quadrant)
        """
        rrg_path = self._get_path("sector_rrg_latest")

        if not rrg_path.exists():
            return pd.DataFrame()

        return pd.read_parquet(rrg_path)

    def get_rs_rating_history(self, days: int = 30) -> pd.DataFrame:
        """
        Get RS Rating history for heatmap visualization.

        Args:
            days: Number of days of history (default 30)

        Returns:
            DataFrame with RS ratings history
        """
        history_path = self._get_path("rs_rating_history")

        if not history_path.exists():
            return pd.DataFrame()

        df = pd.read_parquet(history_path)

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').tail(days * 315)  # ~315 symbols * days

        return df

    def get_buy_list(self) -> pd.DataFrame:
        """
        Get current buy list candidates with position sizing.
        Used by Technical Dashboard Tab 4: Trading Lists.

        Returns:
            DataFrame with top 10 buy candidates
        """
        buy_path = self._get_path("buy_list_latest")

        if not buy_path.exists():
            return pd.DataFrame()

        return pd.read_parquet(buy_path)

    def get_sell_list(self) -> pd.DataFrame:
        """
        Get current sell/exit signals.
        Used by Technical Dashboard Tab 4: Trading Lists.

        Returns:
            DataFrame with exit signals for positions
        """
        sell_path = self._get_path("sell_list_latest")

        if not sell_path.exists():
            return pd.DataFrame()

        return pd.read_parquet(sell_path)

    def get_alerts(self, alert_type: Optional[str] = None, latest_only: bool = True) -> pd.DataFrame:
        """
        Get technical alerts (breakout, MA crossover, patterns, volume spike).

        Args:
            alert_type: Filter by type ('breakout', 'ma_crossover', 'patterns', 'volume_spike')
                       None for combined alerts
            latest_only: If True, get daily latest; else get historical

        Returns:
            DataFrame with alerts
        """
        if alert_type:
            source = f"{alert_type}_{'latest' if latest_only else 'history'}"
        else:
            source = f"combined_alerts_{'latest' if latest_only else 'history'}"

        alerts_path = self._get_path(source)

        if not alerts_path.exists():
            return pd.DataFrame()

        return pd.read_parquet(alerts_path)
