"""
Valuation Service - Data Loading Layer
======================================

Service for loading PE/PB/EV-EBITDA valuation data from parquet files.
Uses DataMappingRegistry for path resolution.

Usage:
    from WEBAPP.services.valuation_service import ValuationService

    service = ValuationService()
    df = service.get_valuation_data(scope="VNINDEX")
    ticker_df = service.get_ticker_valuation("VNM")

Author: AI Assistant
Date: 2025-12-31
Version: 2.0.0 (Registry Integration)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict

from .base_service import BaseService

# Import SectorRegistry for industry sector mapping
try:
    from config.registries.sector_lookup import SectorRegistry
    SECTOR_REGISTRY = SectorRegistry()
except Exception:
    SECTOR_REGISTRY = None

# Import centralized config for outlier limits and status calculation
from WEBAPP.core.valuation_config import (
    OUTLIER_LIMITS,
    get_percentile_status,
    filter_outliers
)


class ValuationService(BaseService):
    """Service layer for Valuation data (PE, PB, EV/EBITDA)."""

    DATA_SOURCE = "pe_historical"
    ENTITY_TYPE = "all"

    # Tickers to exclude (outliers with unreliable data)
    EXCLUDED_TICKERS = [
        # Banks with data issues
        'NVB', 'KLB', 'BVB', 'VBB', 'PGB', 'ABB', 'BAB', 'NAB',
        # Securities with extreme volatility
        'VIX', 'VDS', 'VUA', 'ART', 'AGR', 'BMS', 'CTS', 'TVS', 'ORS',
        # Penny stocks / low liquidity
        'L14', 'L18', 'L43', 'L44', 'L61', 'L62',
    ]

    # Use centralized outlier rules from valuation_config
    OUTLIER_RULES = {
        k: {
            'max_value': v['max'],
            'min_value': v['min'],
            'multiplier_limit': v['multiplier']
        }
        for k, v in OUTLIER_LIMITS.items()
    }

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize ValuationService.

        Args:
            data_root: Root data directory (for testing, defaults to registry path)
        """
        super().__init__(data_root)
        self._pe_df = None
        self._pb_df = None
        self._ev_ebitda_df = None
        self._ps_df = None

    def _get_path(self, source_name: str) -> Path:
        """Get path for a data source via registry."""
        try:
            path_str = self.registry.get_path(source_name)
            if self._data_root:
                relative_str = str(path_str).replace("DATA/", "")
                return self._data_root / relative_str
            return self.project_root / path_str
        except KeyError:
            # Fallback to hardcoded path for backward compatibility
            fallback_paths = {
                "pe_historical": "processed/valuation/pe/historical/historical_pe.parquet",
                "pb_historical": "processed/valuation/pb/historical/historical_pb.parquet",
                "ps_historical": "processed/valuation/ps/historical/historical_ps.parquet",
                "ev_ebitda_historical": "processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet",
                "vnindex_valuation": "processed/valuation/vnindex/vnindex_valuation_refined.parquet",
            }
            if source_name in fallback_paths:
                return self.data_root / fallback_paths[source_name]
            return self.data_root / "processed" / "valuation" / f"{source_name}.parquet"

    def _load_pe_data(self) -> pd.DataFrame:
        """Load PE historical data (cached)."""
        if self._pe_df is None:
            pe_file = self._get_path("pe_historical")
            if pe_file.exists():
                self._pe_df = pd.read_parquet(pe_file)
                self._pe_df['date'] = pd.to_datetime(self._pe_df['date'])
            else:
                self._pe_df = pd.DataFrame()
        return self._pe_df

    def _load_pb_data(self) -> pd.DataFrame:
        """Load PB historical data (cached)."""
        if self._pb_df is None:
            pb_file = self._get_path("pb_historical")
            if pb_file.exists():
                self._pb_df = pd.read_parquet(pb_file)
                self._pb_df['date'] = pd.to_datetime(self._pb_df['date'])
            else:
                self._pb_df = pd.DataFrame()
        return self._pb_df

    def _load_ev_ebitda_data(self) -> pd.DataFrame:
        """Load EV/EBITDA historical data (cached)."""
        if self._ev_ebitda_df is None:
            ev_file = self._get_path("ev_ebitda_historical")
            if ev_file.exists():
                self._ev_ebitda_df = pd.read_parquet(ev_file)
                self._ev_ebitda_df['date'] = pd.to_datetime(self._ev_ebitda_df['date'])
            else:
                self._ev_ebitda_df = pd.DataFrame()
        return self._ev_ebitda_df

    def _load_ps_data(self) -> pd.DataFrame:
        """Load P/S (Price-to-Sales) historical data (cached)."""
        if self._ps_df is None:
            ps_file = self._get_path("ps_historical")
            if ps_file.exists():
                self._ps_df = pd.read_parquet(ps_file)
                self._ps_df['date'] = pd.to_datetime(self._ps_df['date'])
            else:
                self._ps_df = pd.DataFrame()
        return self._ps_df

    def get_all_tickers(self, sector: Optional[str] = None) -> List[str]:
        """Get list of all tickers with valuation data."""
        pe_df = self._load_pe_data()
        if pe_df.empty:
            return []

        if sector and 'sector' in pe_df.columns:
            tickers = pe_df[pe_df['sector'] == sector]['symbol'].unique().tolist()
        else:
            tickers = pe_df['symbol'].unique().tolist()

        return sorted(tickers)

    def get_sectors_list(self) -> List[str]:
        """Get list of entity types/sectors (COMPANY, BANK, INSURANCE, SECURITY)."""
        pe_df = self._load_pe_data()
        if pe_df.empty or 'sector' not in pe_df.columns:
            return []
        return pe_df['sector'].unique().tolist()

    def get_ticker_valuation(
        self,
        ticker: str,
        start_year: int = 2018,
        limit: Optional[int] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Get all valuation metrics for a single ticker.

        Args:
            ticker: Stock symbol (e.g., "VNM", "ACB")
            start_year: Start year for historical data
            limit: Optional limit on number of records

        Returns:
            Dict with 'pe', 'pb', 'ps', 'ev_ebitda' DataFrames
        """
        start_date = pd.Timestamp(f"{start_year}-01-01")

        # Load PE data
        pe_df = self._load_pe_data()
        pe_ticker = pd.DataFrame()
        if not pe_df.empty and 'symbol' in pe_df.columns:
            pe_ticker = pe_df[
                (pe_df['symbol'] == ticker) &
                (pe_df['date'] >= start_date)
            ].sort_values('date')
            if limit:
                pe_ticker = pe_ticker.tail(limit)

        # Load PB data
        pb_df = self._load_pb_data()
        pb_ticker = pd.DataFrame()
        if not pb_df.empty and 'symbol' in pb_df.columns:
            pb_ticker = pb_df[
                (pb_df['symbol'] == ticker) &
                (pb_df['date'] >= start_date)
            ].sort_values('date')
            if limit:
                pb_ticker = pb_ticker.tail(limit)

        # Load EV/EBITDA data
        ev_df = self._load_ev_ebitda_data()
        ev_ticker = pd.DataFrame()
        if not ev_df.empty and 'symbol' in ev_df.columns:
            ev_ticker = ev_df[
                (ev_df['symbol'] == ticker) &
                (ev_df['date'] >= start_date)
            ].sort_values('date')
            if limit:
                ev_ticker = ev_ticker.tail(limit)

        # Load P/S data
        ps_df = self._load_ps_data()
        ps_ticker = pd.DataFrame()
        if not ps_df.empty and 'symbol' in ps_df.columns:
            ps_ticker = ps_df[
                (ps_df['symbol'] == ticker) &
                (ps_df['date'] >= start_date)
            ].sort_values('date')
            if limit:
                ps_ticker = ps_ticker.tail(limit)

        return {
            'pe': pe_ticker,
            'pb': pb_ticker,
            'ps': ps_ticker,
            'ev_ebitda': ev_ticker
        }

    def get_sector_tickers_valuation(
        self,
        sector: str,
        metric: str = 'pe_ratio',
        start_year: int = 2018
    ) -> pd.DataFrame:
        """
        Get valuation data for all tickers in a sector.

        Args:
            sector: Sector name (COMPANY, BANK, INSURANCE, SECURITY)
            metric: 'pe_ratio', 'pb_ratio', 'ps_ratio', or 'ev_ebitda'
            start_year: Start year

        Returns:
            DataFrame with all tickers' valuation data
        """
        start_date = pd.Timestamp(f"{start_year}-01-01")

        if metric == 'pe_ratio':
            df = self._load_pe_data()
        elif metric == 'pb_ratio':
            df = self._load_pb_data()
        elif metric == 'ps_ratio':
            df = self._load_ps_data()
        elif metric == 'ev_ebitda':
            df = self._load_ev_ebitda_data()
        else:
            return pd.DataFrame()

        if df.empty:
            return pd.DataFrame()

        # Filter by sector and date
        filtered = df[
            (df['sector'] == sector) &
            (df['date'] >= start_date)
        ].copy()

        return filtered

    def get_sector_distribution_stats(
        self,
        sector: str,
        metric: str = 'pe_ratio'
    ) -> pd.DataFrame:
        """
        Get distribution statistics for each ticker in a sector.

        Args:
            sector: Sector name
            metric: 'pe_ratio', 'pb_ratio', 'ps_ratio', or 'ev_ebitda'

        Returns:
            DataFrame with stats per ticker (current, median, percentile, status)
        """
        df = self.get_sector_tickers_valuation(sector, metric)

        if df.empty:
            return pd.DataFrame()

        # Determine value column
        value_col_map = {
            'pe_ratio': 'pe_ratio',
            'pb_ratio': 'pb_ratio',
            'ps_ratio': 'ps_ratio',
            'ev_ebitda': 'ev_ebitda'
        }
        value_col = value_col_map.get(metric, 'pe_ratio')

        stats_data = []
        for ticker in df['symbol'].unique():
            ticker_data = df[df['symbol'] == ticker][value_col].dropna()

            if len(ticker_data) < 20:
                continue

            # Filter outliers
            median_val = ticker_data.median()
            if metric == 'pe_ratio':
                upper_limit = min(100, median_val * 5) if median_val > 0 else 100
                clean_data = ticker_data[(ticker_data > 0) & (ticker_data <= upper_limit)]
            else:
                upper_limit = median_val * 4 if median_val > 0 else 10
                clean_data = ticker_data[(ticker_data > 0) & (ticker_data <= upper_limit)]

            if len(clean_data) < 20:
                clean_data = ticker_data[ticker_data > 0]

            if len(clean_data) < 10:
                continue

            current_val = ticker_data.iloc[-1]
            p5 = clean_data.quantile(0.05)
            p25 = clean_data.quantile(0.25)
            p50 = clean_data.quantile(0.50)
            p75 = clean_data.quantile(0.75)
            p95 = clean_data.quantile(0.95)
            percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100

            # Determine status
            if percentile <= 10:
                status = "Very Cheap"
            elif percentile <= 25:
                status = "Cheap"
            elif percentile <= 75:
                status = "Fair"
            elif percentile <= 90:
                status = "Expensive"
            else:
                status = "Very Expensive"

            stats_data.append({
                'symbol': ticker,
                'current': current_val,
                'p5': p5,
                'p25': p25,
                'median': p50,
                'p75': p75,
                'p95': p95,
                'percentile': percentile,
                'status': status
            })

        return pd.DataFrame(stats_data).sort_values('percentile')

    def get_valuation_data(
        self,
        scope: str = "VNINDEX",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Load valuation data for a scope (VNINDEX or sector).

        Args:
            scope: "VNINDEX" or sector name (Vietnamese)
            start_date: Filter from this date (YYYY-MM-DD)
            end_date: Filter to this date (YYYY-MM-DD)
            limit: Maximum number of records to return (most recent)

        Returns:
            DataFrame with PE/PB metrics sorted by date
        """
        parquet_file = self._get_path("vnindex_valuation")

        if not parquet_file.exists():
            raise FileNotFoundError(
                f"Valuation file not found: {parquet_file}\n"
                f"Please run the valuation calculator first."
            )

        df = pd.read_parquet(parquet_file)

        # Filter by scope - try with SECTOR: prefix first for sector names
        if 'scope' in df.columns:
            if scope in df['scope'].unique():
                df = df[df['scope'] == scope].copy()
            else:
                sector_scope = f"SECTOR:{scope}"
                if sector_scope in df['scope'].unique():
                    df = df[df['scope'] == sector_scope].copy()
                else:
                    df = df[df['scope'] == scope].copy()

        if df.empty:
            return pd.DataFrame()

        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

            if start_date:
                df = df[df['date'] >= start_date]
            if end_date:
                df = df[df['date'] <= end_date]

            df = df.sort_values('date')

        if limit:
            df = df.tail(limit)

        return df

    def get_latest_valuation(self, scope: str = "VNINDEX") -> dict:
        """Get latest valuation metrics for a scope."""
        df = self.get_valuation_data(scope, limit=1)
        return df.iloc[-1].to_dict() if not df.empty else {}

    def get_all_scopes(self) -> List[str]:
        """Get list of available scopes (VNINDEX + sectors)."""
        parquet_file = self._get_path("vnindex_valuation")

        if not parquet_file.exists():
            return []

        df = pd.read_parquet(parquet_file, columns=['scope'])
        scopes = df['scope'].unique().tolist()

        # Clean up sector names for display
        clean_scopes = []
        for s in scopes:
            if s.startswith('SECTOR:'):
                clean_scopes.append(s.replace('SECTOR:', ''))
            else:
                clean_scopes.append(s)

        # Sort with VNINDEX first, then alphabetically
        market_scopes = ['VNINDEX', 'VNINDEX_EXCLUDE', 'BSC_INDEX']
        sorted_scopes = [s for s in market_scopes if s in clean_scopes]
        sorted_scopes += sorted([s for s in clean_scopes if s not in market_scopes])

        return sorted_scopes

    def get_sector_comparison(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        Get PE/PB comparison across all sectors for a specific date.

        Args:
            date: Specific date (YYYY-MM-DD), defaults to latest

        Returns:
            DataFrame with one row per sector
        """
        parquet_file = self._get_path("vnindex_valuation")

        if not parquet_file.exists():
            return pd.DataFrame()

        df = pd.read_parquet(parquet_file)

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

            if date:
                df = df[df['date'] == date]
            else:
                df = df.loc[df.groupby('scope')['date'].idxmax()]

        # Filter only sector scopes and clean names
        if 'scope' in df.columns:
            sector_df = df[df['scope'].str.startswith('SECTOR:')].copy()
            sector_df['scope'] = sector_df['scope'].str.replace('SECTOR:', '', regex=False)
            df = sector_df

        return df.sort_values('pe_ttm') if 'pe_ttm' in df.columns else df

    def get_pe_historical(
        self,
        ticker: Optional[str] = None,
        limit: Optional[int] = 252
    ) -> pd.DataFrame:
        """Get historical PE data."""
        df = self._load_pe_data()

        if df.empty:
            return pd.DataFrame()

        if ticker and 'symbol' in df.columns:
            df = df[df['symbol'] == ticker]

        if limit:
            df = df.tail(limit)

        return df

    def get_pb_historical(
        self,
        ticker: Optional[str] = None,
        limit: Optional[int] = 252
    ) -> pd.DataFrame:
        """Get historical PB data."""
        df = self._load_pb_data()

        if df.empty:
            return pd.DataFrame()

        if ticker and 'symbol' in df.columns:
            df = df[df['symbol'] == ticker]

        if limit:
            df = df.tail(limit)

        return df

    # ========================================================================
    # UNIFIED METRIC INTERFACE
    # ========================================================================

    METRIC_CONFIG = {
        'PE': {
            'value_col': 'pe_ratio',
            'data_loader': '_load_pe_data',
            'display_name': 'P/E Ratio',
            'format': '{:.1f}x'
        },
        'PB': {
            'value_col': 'pb_ratio',
            'data_loader': '_load_pb_data',
            'display_name': 'P/B Ratio',
            'format': '{:.2f}x'
        },
        'PS': {
            'value_col': 'ps_ratio',
            'data_loader': '_load_ps_data',
            'display_name': 'P/S Ratio',
            'format': '{:.2f}x'
        },
        'EV_EBITDA': {
            'value_col': 'ev_ebitda',
            'data_loader': '_load_ev_ebitda_data',
            'display_name': 'EV/EBITDA',
            'format': '{:.1f}x'
        }
    }

    def get_available_metrics(self) -> List[str]:
        """Get list of available valuation metrics."""
        return list(self.METRIC_CONFIG.keys())

    def get_metric_data(
        self,
        metric: str,
        ticker: Optional[str] = None,
        sector: Optional[str] = None,
        start_year: int = 2018
    ) -> pd.DataFrame:
        """
        Unified method to get any metric data for ticker or sector.

        Args:
            metric: 'PE', 'PB', 'PS', or 'EV_EBITDA'
            ticker: Single ticker (e.g., 'VNM')
            sector: Sector filter (e.g., 'BANK', 'COMPANY')
            start_year: Start year for historical data

        Returns:
            DataFrame with valuation data
        """
        if metric not in self.METRIC_CONFIG:
            raise ValueError(f"Unknown metric: {metric}. Available: {list(self.METRIC_CONFIG.keys())}")

        config = self.METRIC_CONFIG[metric]
        loader_method = getattr(self, config['data_loader'])
        df = loader_method()

        if df.empty:
            return pd.DataFrame()

        start_date = pd.Timestamp(f"{start_year}-01-01")
        df = df[df['date'] >= start_date].copy()

        if ticker:
            df = df[df['symbol'] == ticker]
        elif sector:
            df = df[df['sector'] == sector]

        return df.sort_values('date')

    def get_metric_stats(
        self,
        metric: str,
        ticker: str,
        start_year: int = 2018
    ) -> Dict:
        """
        Get statistical summary for a metric on a ticker.

        Args:
            metric: 'PE', 'PB', 'PS', or 'EV_EBITDA'
            ticker: Stock symbol
            start_year: Start year

        Returns:
            Dict with mean, std, min, max, current, percentile, z_score
        """
        df = self.get_metric_data(metric, ticker=ticker, start_year=start_year)

        if df.empty:
            return {}

        config = self.METRIC_CONFIG[metric]
        value_col = config['value_col']

        if value_col not in df.columns:
            return {}

        values = df[value_col].dropna()
        if len(values) < 10:
            return {}

        # Filter outliers
        median_val = values.median()
        if metric == 'PE':
            clean_values = values[(values > 0) & (values <= min(100, median_val * 5))]
        else:
            clean_values = values[(values > 0) & (values <= median_val * 4)]

        if len(clean_values) < 10:
            clean_values = values[values > 0]

        if len(clean_values) == 0:
            return {}

        current = values.iloc[-1]
        mean_val = clean_values.mean()
        std_val = clean_values.std()
        percentile = np.sum(clean_values <= current) / len(clean_values) * 100
        z_score = (current - mean_val) / std_val if std_val > 0 else 0

        return {
            'current': current,
            'mean': mean_val,
            'std': std_val,
            'min': clean_values.min(),
            'max': clean_values.max(),
            'median': clean_values.median(),
            'p5': clean_values.quantile(0.05),
            'p25': clean_values.quantile(0.25),
            'p75': clean_values.quantile(0.75),
            'p95': clean_values.quantile(0.95),
            'percentile': percentile,
            'z_score': z_score,
            'n_points': len(clean_values),
            'latest_date': df['date'].max()
        }

    def get_sector_candle_data(
        self,
        sector: str,
        metric: str = 'PE',
        start_year: int = 2018
    ) -> List[Dict]:
        """
        Get candlestick distribution data for all tickers in a sector.

        Args:
            sector: Sector name (BANK, COMPANY, INSURANCE, SECURITY)
            metric: 'PE', 'PB', 'PS', or 'EV_EBITDA'
            start_year: Start year

        Returns:
            List of dicts with distribution stats per ticker
        """
        df = self.get_metric_data(metric, sector=sector, start_year=start_year)

        if df.empty:
            return []

        config = self.METRIC_CONFIG[metric]
        value_col = config['value_col']

        results = []
        for ticker in df['symbol'].unique():
            ticker_data = df[df['symbol'] == ticker][value_col].dropna()

            if len(ticker_data) < 20:
                continue

            # Filter outliers
            median_val = ticker_data.median()
            if metric == 'PE':
                upper_limit = min(100, median_val * 5) if median_val > 0 else 100
                clean_data = ticker_data[(ticker_data > 0) & (ticker_data <= upper_limit)]
            else:
                upper_limit = median_val * 4 if median_val > 0 else 10
                clean_data = ticker_data[(ticker_data > 0) & (ticker_data <= upper_limit)]

            if len(clean_data) < 20:
                clean_data = ticker_data[ticker_data > 0]

            if len(clean_data) < 10:
                continue

            current = ticker_data.iloc[-1]
            percentile = np.sum(clean_data <= current) / len(clean_data) * 100

            # Determine status
            if percentile <= 10:
                status = "Very Cheap"
            elif percentile <= 25:
                status = "Cheap"
            elif percentile <= 75:
                status = "Fair"
            elif percentile <= 90:
                status = "Expensive"
            else:
                status = "Very Expensive"

            results.append({
                'symbol': ticker,
                'current': current,
                'p5': clean_data.quantile(0.05),
                'p25': clean_data.quantile(0.25),
                'median': clean_data.quantile(0.50),
                'p75': clean_data.quantile(0.75),
                'p95': clean_data.quantile(0.95),
                'percentile': percentile,
                'status': status
            })

        return sorted(results, key=lambda x: x['percentile'])

    # ========================================================================
    # INDUSTRY SECTOR METHODS (via SectorRegistry)
    # ========================================================================

    def get_industry_sectors(self) -> List[str]:
        """Get list of all industry sectors from SectorRegistry."""
        if SECTOR_REGISTRY is None:
            return []
        return SECTOR_REGISTRY.get_all_sectors()

    def get_tickers_by_industry(self, industry_sector: str) -> List[str]:
        """Get all tickers in an industry sector."""
        if SECTOR_REGISTRY is None:
            return []
        return SECTOR_REGISTRY.get_tickers_by_sector(industry_sector)

    def get_ticker_industry(self, ticker: str) -> Optional[str]:
        """Get industry sector for a ticker."""
        if SECTOR_REGISTRY is None:
            return None
        info = SECTOR_REGISTRY.get_ticker(ticker)
        return info.get('sector') if info else None

    def get_industry_candle_data(
        self,
        industry_sector: str,
        metric: str = 'PE',
        start_year: int = 2018
    ) -> List[Dict]:
        """
        Get candlestick distribution data for all tickers in an INDUSTRY sector.

        Args:
            industry_sector: Industry sector name (e.g., 'Ngân hàng', 'Bất động sản')
            metric: 'PE', 'PB', 'PS', or 'EV_EBITDA'
            start_year: Start year

        Returns:
            List of dicts with distribution stats per ticker
        """
        # Get tickers in this industry
        tickers = self.get_tickers_by_industry(industry_sector)
        if not tickers:
            return []

        # Remove excluded tickers (outliers)
        tickers = [t for t in tickers if t not in self.EXCLUDED_TICKERS]

        # Load metric data
        if metric not in self.METRIC_CONFIG:
            return []

        config = self.METRIC_CONFIG[metric]
        loader_method = getattr(self, config['data_loader'])
        df = loader_method()

        if df.empty:
            return []

        start_date = pd.Timestamp(f"{start_year}-01-01")
        df = df[df['date'] >= start_date].copy()
        df = df[df['symbol'].isin(tickers)]

        if df.empty:
            return []

        value_col = config['value_col']
        rules = self.OUTLIER_RULES.get(metric, self.OUTLIER_RULES['PE'])
        max_val = rules['max_value']
        min_val = rules['min_value']
        mult_limit = rules['multiplier_limit']

        results = []
        for ticker in df['symbol'].unique():
            ticker_data = df[df['symbol'] == ticker][value_col].dropna()

            if len(ticker_data) < 20:
                continue

            median_val = ticker_data.median()
            upper_limit = min(max_val, median_val * mult_limit) if median_val > 0 else max_val
            clean_data = ticker_data[(ticker_data > min_val) & (ticker_data <= upper_limit)]

            if len(clean_data) < 20:
                clean_data = ticker_data[ticker_data > min_val]

            if len(clean_data) < 10:
                continue

            # Skip if data variance is too extreme
            if clean_data.std() / clean_data.mean() > 2.0:
                continue

            raw_current = ticker_data.iloc[-1]
            p95 = clean_data.quantile(0.95)
            p5 = clean_data.quantile(0.05)

            if raw_current > p95 * 1.5 or raw_current < p5 * 0.5 or raw_current > max_val:
                valid_recent = ticker_data[(ticker_data <= p95 * 1.2) & (ticker_data <= max_val)]
                if len(valid_recent) > 0:
                    current = valid_recent.iloc[-1]
                else:
                    current = raw_current
            else:
                current = raw_current

            percentile = np.sum(clean_data <= current) / len(clean_data) * 100

            if percentile <= 10:
                status = "Very Cheap"
            elif percentile <= 25:
                status = "Cheap"
            elif percentile <= 75:
                status = "Fair"
            elif percentile <= 90:
                status = "Expensive"
            else:
                status = "Very Expensive"

            results.append({
                'symbol': ticker,
                'current': current,
                'min': clean_data.min(),
                'p25': clean_data.quantile(0.25),
                'median': clean_data.quantile(0.50),
                'p75': clean_data.quantile(0.75),
                'max': clean_data.max(),
                'percentile': percentile,
                'status': status
            })

        return sorted(results, key=lambda x: x['percentile'])

    def get_industry_full_data(
        self,
        industry_sector: str,
        metric: str = 'PE',
        start_year: int = 2018
    ) -> pd.DataFrame:
        """
        Get full historical data for all tickers in an industry sector.

        Args:
            industry_sector: Industry sector name (e.g., 'Ngân hàng', 'Tất cả')
            metric: 'PE', 'PB', 'PS', or 'EV_EBITDA'
            start_year: Start year

        Returns:
            DataFrame with full historical data for all tickers in sector
        """
        if industry_sector == "Tất cả":
            tickers = self.get_all_tickers()
        else:
            tickers = self.get_tickers_by_industry(industry_sector)

        if not tickers:
            return pd.DataFrame()

        tickers = [t for t in tickers if t not in self.EXCLUDED_TICKERS]

        if metric not in self.METRIC_CONFIG:
            return pd.DataFrame()

        config = self.METRIC_CONFIG[metric]
        loader_method = getattr(self, config['data_loader'])
        df = loader_method()

        if df.empty:
            return pd.DataFrame()

        start_date = pd.Timestamp(f"{start_year}-01-01")
        df = df[df['date'] >= start_date].copy()
        df = df[df['symbol'].isin(tickers)]

        # Add industry info
        if SECTOR_REGISTRY is not None:
            df['industry'] = df['symbol'].apply(
                lambda x: SECTOR_REGISTRY.get_ticker(x).get('sector', 'Unknown')
                if SECTOR_REGISTRY.get_ticker(x) else 'Unknown'
            )

        return df.sort_values(['symbol', 'date'])
