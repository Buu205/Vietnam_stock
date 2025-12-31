"""
Forecast Service - Data Loading Layer
======================================

Service for loading BSC Forecast data from parquet files.
Uses DataMappingRegistry for path resolution.

Usage:
    from WEBAPP.services.forecast_service import ForecastService

    service = ForecastService()
    individual = service.get_individual_stocks()
    sectors = service.get_sector_valuation()

Author: AI Assistant
Date: 2025-12-31
Version: 2.0.0 (Registry Integration)
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List

from .base_service import BaseService


class ForecastService(BaseService):
    """Service layer for BSC Forecast data."""

    DATA_SOURCE = "bsc_individual"
    ENTITY_TYPE = "all"

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize ForecastService.

        Args:
            data_root: Root data directory (for testing, defaults to registry path)
        """
        super().__init__(data_root)

    def _get_path(self, source_name: str) -> Path:
        """Get path for a data source via registry."""
        try:
            path_str = self.registry.get_path(source_name)
            if self._data_root:
                # Use override path for testing
                relative_str = str(path_str).replace("DATA/", "")
                return self._data_root / relative_str
            return self.project_root / path_str
        except KeyError:
            # Fallback to hardcoded path
            return self.data_root / "processed" / "forecast" / "bsc" / f"{source_name}.parquet"

    def get_individual_stocks(self) -> pd.DataFrame:
        """
        Load individual stocks forecast data.

        Returns:
            DataFrame with 92 stocks and all metrics
        """
        file_path = self._get_path("bsc_individual")

        if not file_path.exists():
            return pd.DataFrame()

        df = pd.read_parquet(file_path)

        # Sort by upside_pct descending (best opportunities first)
        if 'upside_pct' in df.columns:
            df = df.sort_values('upside_pct', ascending=False)

        return df

    def get_sector_valuation(self) -> pd.DataFrame:
        """
        Load sector valuation data with PE/PB FWD 2025-2026.

        Returns:
            DataFrame with 15 BSC sectors
        """
        file_path = self._get_path("bsc_sector_valuation")

        if not file_path.exists():
            return pd.DataFrame()

        df = pd.read_parquet(file_path)

        # Sort by PE FWD 2025 ascending (lowest PE first)
        if 'pe_fwd_2025' in df.columns:
            df = df.sort_values('pe_fwd_2025')

        return df

    def get_combined_data(self) -> pd.DataFrame:
        """
        Load combined data (individual + sector metrics merged).

        Returns:
            DataFrame with individual stocks + sector PE/PB
        """
        file_path = self._get_path("bsc_combined")

        if not file_path.exists():
            return pd.DataFrame()

        return pd.read_parquet(file_path)

    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics for dashboard metric cards.

        Returns:
            Dict with total_stocks, strong_buy_count, buy_count,
            avg_upside, median_pe_fwd_2025
        """
        df = self.get_individual_stocks()

        if df.empty:
            return {
                'total_stocks': 0,
                'strong_buy_count': 0,
                'buy_count': 0,
                'avg_upside': 0,
                'median_pe_fwd_2025': 0,
            }

        return {
            'total_stocks': len(df),
            'strong_buy_count': len(df[df['rating'] == 'STRONG BUY']),
            'buy_count': len(df[df['rating'] == 'BUY']),
            'avg_upside': df['upside_pct'].mean() if 'upside_pct' in df.columns else 0,
            'median_pe_fwd_2025': df['pe_fwd_2025'].median() if 'pe_fwd_2025' in df.columns else 0,
        }

    def get_rating_distribution(self) -> Dict[str, int]:
        """
        Get rating distribution counts.

        Returns:
            Dict with rating -> count mapping
        """
        df = self.get_individual_stocks()

        if df.empty or 'rating' not in df.columns:
            return {}

        return df['rating'].value_counts().to_dict()

    def get_sectors_list(self) -> List[str]:
        """
        Get list of ICB L2 sectors (Vietnamese).

        Returns:
            List of sector names
        """
        df = self.get_sector_valuation()

        if df.empty or 'sector' not in df.columns:
            return []

        return sorted(df['sector'].unique().tolist())

    def get_stocks_by_sector(self, sector: str) -> pd.DataFrame:
        """
        Get individual stocks filtered by ICB L2 sector.

        Args:
            sector: ICB L2 sector name (Vietnamese, e.g., "Ngân hàng", "Bất động sản")

        Returns:
            Filtered DataFrame
        """
        df = self.get_individual_stocks()

        if df.empty or 'sector' not in df.columns:
            return pd.DataFrame()

        return df[df['sector'] == sector]

    def get_stocks_by_rating(self, rating: str) -> pd.DataFrame:
        """
        Get individual stocks filtered by rating.

        Args:
            rating: Rating value (e.g., "STRONG BUY", "BUY")

        Returns:
            Filtered DataFrame
        """
        df = self.get_individual_stocks()

        if df.empty or 'rating' not in df.columns:
            return pd.DataFrame()

        return df[df['rating'] == rating]

    def get_top_upside_stocks(self, n: int = 10) -> pd.DataFrame:
        """
        Get top N stocks by upside potential.

        Args:
            n: Number of stocks to return

        Returns:
            Top N stocks by upside_pct
        """
        df = self.get_individual_stocks()

        if df.empty or 'upside_pct' not in df.columns:
            return pd.DataFrame()

        return df.nlargest(n, 'upside_pct')

    def get_data_timestamp(self) -> Optional[str]:
        """
        Get the last update timestamp from the data.

        Returns:
            Timestamp string or None
        """
        df = self.get_individual_stocks()

        if df.empty or 'updated_at' not in df.columns:
            return None

        return str(df['updated_at'].iloc[0])

    def get_sector_with_pe_pb_ttm(self) -> pd.DataFrame:
        """
        Get sector data merged with PE/PB TTM calculated from BSC symbols only.

        PE/PB TTM is calculated as: Sum(Market Cap) / Sum(TTM Earnings or Equity)
        for BSC-covered stocks in each sector (ICB L2).

        Returns:
            DataFrame with sector, pe_fwd_2025, pe_fwd_2026, pe_ttm, pb_ttm, pb_fwd
        """
        import numpy as np

        # Load sector data
        sector_df = self.get_sector_valuation()
        individual_df = self.get_individual_stocks()

        if sector_df.empty or individual_df.empty:
            return sector_df

        # Load PE/PB TTM via registry
        pe_ttm_path = self._get_path("pe_historical")
        pb_ttm_path = self._get_path("pb_historical")

        if not pe_ttm_path.exists():
            return sector_df

        # Get BSC symbols
        bsc_symbols = individual_df['symbol'].tolist()

        # Load PE historical, filter to BSC symbols, get latest
        pe_hist = pd.read_parquet(pe_ttm_path)
        pe_bsc = pe_hist[pe_hist['symbol'].isin(bsc_symbols)]
        latest_date = pe_bsc['date'].max()
        pe_latest = pe_bsc[pe_bsc['date'] == latest_date][['symbol', 'pe_ratio', 'ttm_earning_billion_vnd']].copy()
        pe_latest = pe_latest.rename(columns={'pe_ratio': 'pe_ttm', 'ttm_earning_billion_vnd': 'ttm_earnings'})

        # Merge PE into individual stocks
        individual_with_valuation = individual_df.merge(pe_latest[['symbol', 'pe_ttm', 'ttm_earnings']], on='symbol', how='left')

        # Load PB TTM if available
        if pb_ttm_path.exists():
            pb_hist = pd.read_parquet(pb_ttm_path)
            pb_bsc = pb_hist[pb_hist['symbol'].isin(bsc_symbols)]
            pb_latest = pb_bsc[pb_bsc['date'] == latest_date][['symbol', 'pb_ratio', 'equity_billion_vnd']].copy()
            pb_latest = pb_latest.rename(columns={'pb_ratio': 'pb_ttm', 'equity_billion_vnd': 'book_value'})
            individual_with_valuation = individual_with_valuation.merge(pb_latest, on='symbol', how='left')
        else:
            individual_with_valuation['pb_ttm'] = np.nan
            individual_with_valuation['book_value'] = np.nan

        # Calculate sector PE/PB TTM as weighted average (sum market_cap / sum earnings or equity)
        sector_ttm = individual_with_valuation.groupby('sector').agg({
            'market_cap': 'sum',
            'ttm_earnings': 'sum',
            'book_value': 'sum',
            'pe_ttm': 'median',
            'pb_ttm': 'median'
        }).reset_index()

        # Calculate sector-level PE (weighted)
        sector_ttm['sector_pe_ttm'] = sector_ttm['market_cap'] / sector_ttm['ttm_earnings']
        sector_ttm['sector_pe_ttm'] = sector_ttm['sector_pe_ttm'].replace([np.inf, -np.inf], np.nan)

        # Calculate sector-level PB TTM (weighted)
        sector_ttm['sector_pb_ttm'] = sector_ttm['market_cap'] / sector_ttm['book_value']
        sector_ttm['sector_pb_ttm'] = sector_ttm['sector_pb_ttm'].replace([np.inf, -np.inf], np.nan)

        # Rename and select
        sector_ttm = sector_ttm.rename(columns={'pe_ttm': 'median_pe_ttm', 'pb_ttm': 'median_pb_ttm'})
        sector_ttm = sector_ttm[['sector', 'sector_pe_ttm', 'sector_pb_ttm', 'median_pe_ttm', 'median_pb_ttm']]

        # Merge with sector data
        merged = sector_df.merge(sector_ttm, on='sector', how='left')

        return merged

    def get_sector_with_pe_ttm(self) -> pd.DataFrame:
        """Alias for backward compatibility."""
        return self.get_sector_with_pe_pb_ttm()

    def get_sector_opportunity_score(self) -> pd.DataFrame:
        """
        Calculate sector opportunity score based on multiple factors.

        Score components:
        - Upside: Higher avg_upside_pct = better (30%)
        - Growth: Higher avg_npatmi_growth_2025 = better (25%)
        - Valuation Discount: pe_fwd_2025 < pe_ttm = better (25%)
        - PE Level: Lower pe_fwd_2025 = better (20%)

        Returns:
            DataFrame with opportunity scores and ranking
        """
        import numpy as np

        df = self.get_sector_with_pe_ttm()

        if df.empty:
            return pd.DataFrame()

        result = df.copy()

        # 1. Upside Score (higher = better) - weight 30%
        if 'avg_upside_pct' in result.columns:
            upside_min = result['avg_upside_pct'].min()
            upside_max = result['avg_upside_pct'].max()
            if upside_max != upside_min:
                result['upside_score'] = ((result['avg_upside_pct'] - upside_min) / (upside_max - upside_min)) * 100
            else:
                result['upside_score'] = 50
        else:
            result['upside_score'] = 50

        # 2. Growth Score (higher growth = better) - weight 25%
        if 'avg_npatmi_growth_2025' in result.columns:
            # Handle NaN by filling with median
            growth_col = result['avg_npatmi_growth_2025'].fillna(result['avg_npatmi_growth_2025'].median())
            growth_min = growth_col.min()
            growth_max = growth_col.max()
            if growth_max != growth_min:
                result['growth_score'] = ((growth_col - growth_min) / (growth_max - growth_min)) * 100
            else:
                result['growth_score'] = 50
        else:
            result['growth_score'] = 50

        # 3. Valuation Discount Score (pe_fwd < pe_ttm = better) - weight 25%
        if 'pe_fwd_2025' in result.columns and 'sector_pe_ttm' in result.columns:
            # Calculate discount: positive means forward PE is lower than TTM (good)
            result['pe_discount_pct'] = (result['sector_pe_ttm'] - result['pe_fwd_2025']) / result['sector_pe_ttm'] * 100
            discount_col = result['pe_discount_pct'].fillna(0)
            discount_min = discount_col.min()
            discount_max = discount_col.max()
            if discount_max != discount_min:
                result['discount_score'] = ((discount_col - discount_min) / (discount_max - discount_min)) * 100
            else:
                result['discount_score'] = 50
        else:
            result['discount_score'] = 50
            result['pe_discount_pct'] = 0

        # 4. PE Level Score (lower PE = better) - weight 20%
        if 'pe_fwd_2025' in result.columns:
            pe_col = result['pe_fwd_2025'].fillna(result['pe_fwd_2025'].median())
            pe_min = pe_col.min()
            pe_max = pe_col.max()
            if pe_max != pe_min:
                # Invert: lower PE = higher score
                result['pe_level_score'] = ((pe_max - pe_col) / (pe_max - pe_min)) * 100
            else:
                result['pe_level_score'] = 50
        else:
            result['pe_level_score'] = 50

        # Calculate total opportunity score
        result['opportunity_score'] = (
            result['upside_score'] * 0.30 +
            result['growth_score'] * 0.25 +
            result['discount_score'] * 0.25 +
            result['pe_level_score'] * 0.20
        )

        # Rank sectors
        result['rank'] = result['opportunity_score'].rank(ascending=False).astype(int)

        # Sort by opportunity score
        result = result.sort_values('opportunity_score', ascending=False)

        return result
