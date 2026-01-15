"""
Data Loader Service
===================

Centralized data loading service with caching for efficient data access.
This service handles loading parquet files and provides caching to avoid
repeated disk reads.

Features:
---------
- Lazy loading: Files are only loaded when first accessed
- TTL caching: Data is cached for 5 minutes (configurable)
- Type-specific loaders: Separate methods for each data type
"""

import time
import logging
from pathlib import Path
from typing import Dict, Optional, List
import pandas as pd

from bsc_mcp.config import get_config, Config

# Set up logging
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Centralized data loading service with TTL caching.

    This class provides methods to load various data files (parquet format)
    with built-in caching to improve performance.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize DataLoader with configuration.

        Args:
            config: Configuration instance. If None, uses global config.
        """
        self.config = config or get_config()
        self._cache: Dict[str, pd.DataFrame] = {}
        self._cache_timestamps: Dict[str, float] = {}

        logger.info(f"DataLoader initialized with DATA_ROOT: {self.config.DATA_ROOT}")

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid (not expired)."""
        if cache_key not in self._cache:
            return False

        cache_time = self._cache_timestamps.get(cache_key, 0)
        elapsed = time.time() - cache_time

        return elapsed < self.config.CACHE_TTL

    def _load_cached(
        self,
        cache_key: str,
        relative_path: str,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Load data from cache or disk with caching logic.

        Args:
            cache_key: Unique key for this data in the cache
            relative_path: Path relative to DATA_ROOT
            force_refresh: If True, bypass cache and reload from disk

        Returns:
            pd.DataFrame: The loaded data
        """
        # Check cache validity
        if not force_refresh and self._is_cache_valid(cache_key):
            logger.debug(f"Cache hit for {cache_key}")
            return self._cache[cache_key]

        # Load from disk
        full_path = self.config.DATA_ROOT / relative_path

        if not full_path.exists():
            raise FileNotFoundError(
                f"Data file not found: {full_path}\n"
                f"Please run the data pipeline to generate this file."
            )

        logger.info(f"Loading {cache_key} from disk: {full_path}")
        start_time = time.time()

        df = pd.read_parquet(full_path)

        # Validate empty DataFrame
        if df.empty:
            logger.warning(f"Loaded empty DataFrame for {cache_key} from {full_path}")

        elapsed = time.time() - start_time
        logger.info(f"Loaded {cache_key}: {len(df)} rows in {elapsed:.2f}s")

        # Update cache
        self._cache[cache_key] = df
        self._cache_timestamps[cache_key] = time.time()

        return df

    def clear_cache(self, cache_key: Optional[str] = None):
        """Clear cached data."""
        if cache_key:
            self._cache.pop(cache_key, None)
            self._cache_timestamps.pop(cache_key, None)
            logger.info(f"Cleared cache for {cache_key}")
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
            logger.info("Cleared all cache")

    # =========================================================================
    # Fundamental Data Loaders
    # =========================================================================

    def get_company_fundamentals(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load company financial metrics data."""
        return self._load_cached(
            cache_key="company_fundamentals",
            relative_path=self.config.COMPANY_FUNDAMENTALS_PATH,
            force_refresh=force_refresh
        )

    def get_company_full(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load full company data including all entities."""
        return self._load_cached(
            cache_key="company_full",
            relative_path=self.config.COMPANY_FULL_PATH,
            force_refresh=force_refresh
        )

    def get_bank_fundamentals(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load bank financial metrics data."""
        return self._load_cached(
            cache_key="bank_fundamentals",
            relative_path=self.config.BANK_FUNDAMENTALS_PATH,
            force_refresh=force_refresh
        )

    def get_insurance_fundamentals(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load insurance financial metrics data."""
        return self._load_cached(
            cache_key="insurance_fundamentals",
            relative_path=self.config.INSURANCE_FUNDAMENTALS_PATH,
            force_refresh=force_refresh
        )

    def get_security_fundamentals(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load security/brokerage financial metrics data."""
        return self._load_cached(
            cache_key="security_fundamentals",
            relative_path=self.config.SECURITY_FUNDAMENTALS_PATH,
            force_refresh=force_refresh
        )

    # =========================================================================
    # Valuation Data Loaders
    # =========================================================================

    def get_pe_historical(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load historical PE ratio data."""
        return self._load_cached(
            cache_key="pe_historical",
            relative_path=self.config.PE_HISTORICAL_PATH,
            force_refresh=force_refresh
        )

    def get_pb_historical(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load historical PB ratio data."""
        return self._load_cached(
            cache_key="pb_historical",
            relative_path=self.config.PB_HISTORICAL_PATH,
            force_refresh=force_refresh
        )

    def get_ps_historical(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load historical PS ratio data."""
        return self._load_cached(
            cache_key="ps_historical",
            relative_path=self.config.PS_HISTORICAL_PATH,
            force_refresh=force_refresh
        )

    def get_ev_ebitda_historical(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load historical EV/EBITDA data."""
        return self._load_cached(
            cache_key="ev_ebitda_historical",
            relative_path=self.config.EV_EBITDA_HISTORICAL_PATH,
            force_refresh=force_refresh
        )

    def get_vnindex_valuation(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load VN-Index valuation data."""
        return self._load_cached(
            cache_key="vnindex_valuation",
            relative_path=self.config.VNINDEX_VALUATION_PATH,
            force_refresh=force_refresh
        )

    # =========================================================================
    # Technical Data Loaders
    # =========================================================================

    def get_technical_basic(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load technical indicators data."""
        self.check_cache_invalidation()
        return self._load_cached(
            cache_key="technical_basic",
            relative_path=self.config.TECHNICAL_BASIC_PATH,
            force_refresh=force_refresh
        )

    def get_market_breadth(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load market breadth data."""
        return self._load_cached(
            cache_key="market_breadth",
            relative_path=self.config.MARKET_BREADTH_PATH,
            force_refresh=force_refresh
        )

    def get_sector_breadth(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load sector breadth data."""
        return self._load_cached(
            cache_key="sector_breadth",
            relative_path=self.config.SECTOR_BREADTH_PATH,
            force_refresh=force_refresh
        )

    def get_money_flow(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load individual money flow data."""
        return self._load_cached(
            cache_key="money_flow",
            relative_path=self.config.MONEY_FLOW_PATH,
            force_refresh=force_refresh
        )

    def get_vnindex_indicators(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load VN-Index technical indicators."""
        return self._load_cached(
            cache_key="vnindex_indicators",
            relative_path=self.config.VNINDEX_INDICATORS_PATH,
            force_refresh=force_refresh
        )

    # =========================================================================
    # Technical Alerts Loaders
    # =========================================================================

    def get_breakout_alerts(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load breakout alerts."""
        return self._load_cached(
            cache_key="breakout_alerts",
            relative_path=self.config.BREAKOUT_LATEST_PATH,
            force_refresh=force_refresh
        )

    def get_ma_crossover_alerts(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load MA crossover alerts."""
        return self._load_cached(
            cache_key="ma_crossover_alerts",
            relative_path=self.config.MA_CROSSOVER_LATEST_PATH,
            force_refresh=force_refresh
        )

    def get_volume_spike_alerts(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load volume spike alerts."""
        return self._load_cached(
            cache_key="volume_spike_alerts",
            relative_path=self.config.VOLUME_SPIKE_LATEST_PATH,
            force_refresh=force_refresh
        )

    def get_combined_alerts(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load combined alerts."""
        return self._load_cached(
            cache_key="combined_alerts",
            relative_path=self.config.COMBINED_ALERTS_PATH,
            force_refresh=force_refresh
        )

    def get_pattern_alerts(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load candlestick pattern alerts."""
        return self._load_cached(
            cache_key="pattern_alerts",
            relative_path=self.config.PATTERNS_LATEST_PATH,
            force_refresh=force_refresh
        )

    # =========================================================================
    # Forecast Data Loaders
    # =========================================================================

    def get_bsc_individual(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load BSC individual stock forecasts."""
        return self._load_cached(
            cache_key="bsc_individual",
            relative_path=self.config.BSC_INDIVIDUAL_PATH,
            force_refresh=force_refresh
        )

    def get_bsc_sector(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load BSC sector valuation data."""
        return self._load_cached(
            cache_key="bsc_sector",
            relative_path=self.config.BSC_SECTOR_PATH,
            force_refresh=force_refresh
        )

    def get_bsc_combined(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load BSC combined forecast data."""
        return self._load_cached(
            cache_key="bsc_combined",
            relative_path=self.config.BSC_COMBINED_PATH,
            force_refresh=force_refresh
        )

    # =========================================================================
    # Sector Data Loaders
    # =========================================================================

    def get_sector_valuation(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load sector valuation metrics."""
        return self._load_cached(
            cache_key="sector_valuation",
            relative_path=self.config.SECTOR_VALUATION_PATH,
            force_refresh=force_refresh
        )

    def get_sector_fundamentals(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load sector fundamental metrics."""
        return self._load_cached(
            cache_key="sector_fundamentals",
            relative_path=self.config.SECTOR_FUNDAMENTALS_PATH,
            force_refresh=force_refresh
        )

    # =========================================================================
    # Macro Data Loaders
    # =========================================================================

    def get_macro_commodity(self, force_refresh: bool = False) -> pd.DataFrame:
        """Load macro and commodity data."""
        return self._load_cached(
            cache_key="macro_commodity",
            relative_path=self.config.MACRO_COMMODITY_PATH,
            force_refresh=force_refresh
        )

    # =========================================================================
    # Raw OHLCV Data Loader
    # =========================================================================

    def get_ohlcv_raw(
        self,
        ticker: str = None,
        limit: int = 60,
        include_value: bool = True
    ) -> pd.DataFrame:
        """
        Read directly from raw OHLCV parquet.

        Use this for real-time access to OHLCV after adjustment refresh,
        bypassing processed pipeline delays.

        Args:
            ticker: Optional ticker filter (e.g., "VCB")
            limit: Number of recent days per symbol to return
            include_value: Include trading value columns

        Returns:
            DataFrame with raw OHLCV data
        """
        ohlcv_path = self.config.DATA_ROOT / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"

        if not ohlcv_path.exists():
            logger.warning(f"OHLCV file not found: {ohlcv_path}")
            return pd.DataFrame()

        df = pd.read_parquet(ohlcv_path)
        df['date'] = pd.to_datetime(df['date'])

        if ticker:
            df = df[df['symbol'] == ticker.upper()]

        # Get most recent N days per symbol
        if not df.empty:
            df = df.sort_values(['symbol', 'date'], ascending=[True, False])
            df = df.groupby('symbol').head(limit)
            df = df.sort_values(['symbol', 'date'])

        # Select columns
        base_cols = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
        if include_value and 'market_cap' in df.columns:
            base_cols.append('market_cap')

        return df[base_cols] if not df.empty else df

    def check_cache_invalidation(self):
        """
        Check for external cache invalidation marker.

        Called at start of data loading to detect when data pipeline
        has updated parquet files and cache should be cleared.
        """
        marker_path = self.config.DATA_ROOT / ".cache_invalidated"

        if marker_path.exists():
            self.clear_cache()
            marker_path.unlink()
            logger.info("Cache invalidated by external update (OHLCV refresh)")

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_available_tickers(self) -> List[str]:
        """Get list of all available tickers from technical data."""
        self.check_cache_invalidation()
        try:
            df = self.get_technical_basic()
            return sorted(df['symbol'].unique().tolist())
        except Exception:
            return []

    def get_ticker_entity_type(self, ticker: str) -> Optional[str]:
        """
        Determine entity type for a ticker.

        Returns: 'BANK', 'COMPANY', 'INSURANCE', 'SECURITY', or None
        """
        ticker = ticker.upper()

        # Check banks
        try:
            bank_df = self.get_bank_fundamentals()
            if ticker in bank_df['symbol'].values:
                return 'BANK'
        except FileNotFoundError:
            pass

        # Check insurance
        try:
            ins_df = self.get_insurance_fundamentals()
            if ticker in ins_df['symbol'].values:
                return 'INSURANCE'
        except FileNotFoundError:
            pass

        # Check securities
        try:
            sec_df = self.get_security_fundamentals()
            if ticker in sec_df['symbol'].values:
                return 'SECURITY'
        except FileNotFoundError:
            pass

        # Check companies
        try:
            company_df = self.get_company_fundamentals()
            if ticker in company_df['symbol'].values:
                return 'COMPANY'
        except FileNotFoundError:
            pass

        return None


# =============================================================================
# Singleton Pattern
# =============================================================================

_data_loader: Optional[DataLoader] = None


def get_data_loader() -> DataLoader:
    """
    Get the global DataLoader singleton instance.

    Returns:
        DataLoader: The global DataLoader instance
    """
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader
