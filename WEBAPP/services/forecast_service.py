"""
Forecast Service - Data Loading Layer
======================================

Service for loading BSC & VCI Forecast data from parquet files.
Uses DataMappingRegistry for path resolution.

Usage:
    from WEBAPP.services.forecast_service import ForecastService

    service = ForecastService()
    individual = service.get_individual_stocks()
    sectors = service.get_sector_valuation()
    vci = service.get_vci_consensus()  # P2
    comparison = service.get_bsc_vs_vci_comparison()  # P2

Author: AI Assistant
Date: 2025-12-31
Version: 2.1.0 (VCI Integration for P2)
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

    # =========================================================================
    # P1: Achievement Summary
    # =========================================================================

    def get_achievement_summary(self) -> Dict[str, Dict]:
        """
        Get achievement summary for 3 clickable cards.

        Categories:
        - STRONG BUY: rating == 'STRONG BUY'
        - BUY: rating == 'BUY'
        - HOLD/SELL: rating in ['HOLD', 'SELL', 'REDUCE']

        Returns:
            Dict with counts and avg upside per category
        """
        df = self.get_individual_stocks()

        if df.empty:
            return {
                'strong_buy': {'count': 0, 'avg_upside': 0, 'stocks': []},
                'buy': {'count': 0, 'avg_upside': 0, 'stocks': []},
                'hold_sell': {'count': 0, 'avg_upside': 0, 'stocks': []},
            }

        # Strong Buy
        strong_buy = df[df['rating'] == 'STRONG BUY']
        # Buy
        buy = df[df['rating'] == 'BUY']
        # Hold/Sell
        hold_sell = df[df['rating'].isin(['HOLD', 'SELL', 'REDUCE', 'UNDERPERFORM'])]

        return {
            'strong_buy': {
                'count': len(strong_buy),
                'avg_upside': strong_buy['upside_pct'].mean() if len(strong_buy) > 0 else 0,
                'stocks': strong_buy['symbol'].tolist()[:10]  # Top 10
            },
            'buy': {
                'count': len(buy),
                'avg_upside': buy['upside_pct'].mean() if len(buy) > 0 else 0,
                'stocks': buy['symbol'].tolist()[:10]
            },
            'hold_sell': {
                'count': len(hold_sell),
                'avg_upside': hold_sell['upside_pct'].mean() if len(hold_sell) > 0 else 0,
                'stocks': hold_sell['symbol'].tolist()[:10]
            },
        }

    # =========================================================================
    # P2: VCI Integration
    # =========================================================================

    def get_vci_consensus(self) -> pd.DataFrame:
        """
        Load VCI coverage universe data.

        Returns:
            DataFrame with VCI forecasts (ticker, target_price, rating, pe_fwd, etc.)
        """
        file_path = self._get_path("vci_coverage")

        if not file_path.exists():
            return pd.DataFrame()

        df = pd.read_parquet(file_path)

        # Normalize column names
        if 'ticker' in df.columns:
            df = df.rename(columns={'ticker': 'symbol'})

        return df

    def get_bsc_vs_vci_comparison(self) -> pd.DataFrame:
        """
        Compare BSC vs VCI forecasts for overlapping tickers.

        Returns:
            DataFrame with BSC and VCI forecasts side by side
        """
        bsc_df = self.get_individual_stocks()
        vci_df = self.get_vci_consensus()

        if bsc_df.empty or vci_df.empty:
            return pd.DataFrame()

        # Rename VCI columns with suffix (comprehensive for reuse)
        vci_cols = {
            'targetPrice': 'vci_target_price',
            'rating': 'vci_rating',
            'pe_2025F': 'vci_pe_2025',
            'pe_2026F': 'vci_pe_2026',
            'pb_2025F': 'vci_pb_2025',
            'pb_2026F': 'vci_pb_2026',
            'npatmi_2025F': 'vci_npatmi_2025',
            'npatmi_2026F': 'vci_npatmi_2026',
            'npatmiGrowth_2025F': 'vci_npatmi_growth_2025',
            'npatmiGrowth_2026F': 'vci_npatmi_growth_2026',
            'roe_2025F': 'vci_roe_2025',
            'roe_2026F': 'vci_roe_2026',
            'projectedTsrPercentage': 'vci_upside_pct',
        }
        vci_renamed = vci_df.rename(columns=vci_cols)

        # Convert VCI NPATMI from raw VND to billions (to match BSC units)
        for col in ['vci_npatmi_2025', 'vci_npatmi_2026']:
            if col in vci_renamed.columns:
                vci_renamed[col] = vci_renamed[col] / 1e9

        # Select relevant columns
        vci_selected = vci_renamed[['symbol'] + [c for c in vci_cols.values() if c in vci_renamed.columns]]

        # Merge on symbol
        merged = bsc_df.merge(vci_selected, on='symbol', how='inner')

        # Calculate differences
        if 'target_price' in merged.columns and 'vci_target_price' in merged.columns:
            merged['target_diff_pct'] = (merged['target_price'] - merged['vci_target_price']) / merged['vci_target_price'] * 100

        if 'upside_pct' in merged.columns and 'vci_upside_pct' in merged.columns:
            merged['upside_diff'] = merged['upside_pct'] - merged['vci_upside_pct']

        # Determine consensus status
        def get_consensus_status(row):
            if 'vci_rating' not in row or pd.isna(row.get('vci_rating')):
                return 'NO_VCI_DATA'
            bsc_bullish = row.get('rating', '') in ['STRONG BUY', 'BUY']
            vci_bullish = str(row.get('vci_rating', '')).upper() in ['BUY', 'OUTPERFORM', 'OVERWEIGHT']
            if bsc_bullish and vci_bullish:
                return 'ALIGNED'
            elif bsc_bullish and not vci_bullish:
                return 'BSC_BULL'
            elif not bsc_bullish and vci_bullish:
                return 'VCI_BULL'
            else:
                return 'ALIGNED_BEARISH'

        merged['consensus_status'] = merged.apply(get_consensus_status, axis=1)

        return merged

    def get_consensus_summary(self) -> Dict[str, int]:
        """
        Get consensus status distribution.

        Returns:
            Dict with status -> count
        """
        df = self.get_bsc_vs_vci_comparison()

        if df.empty or 'consensus_status' not in df.columns:
            return {}

        return df['consensus_status'].value_counts().to_dict()

    # =========================================================================
    # P3: Multi-Source Consensus (BSC, VCI, SSI, HSC)
    # =========================================================================

    def _load_source_json(self, source: str) -> pd.DataFrame:
        """
        Load forecast data from JSON source files.

        Args:
            source: Source name (bsc, vci, ssi, hcm)

        Returns:
            DataFrame with standardized columns
        """
        import json

        json_path = self.data_root / "processed" / "forecast" / "sources" / f"{source}.json"

        if not json_path.exists():
            return pd.DataFrame()

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        stocks = data.get('stocks', [])
        if not stocks:
            return pd.DataFrame()

        df = pd.DataFrame(stocks)

        # Standardize column names
        if 'symbol' not in df.columns and 'Symbol' in df.columns:
            df = df.rename(columns={'Symbol': 'symbol'})

        # Add source column
        df['source'] = source

        return df

    def get_all_sources_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load data from all forecast sources.

        Returns:
            Dict mapping source name to DataFrame
        """
        sources = ['bsc', 'vci', 'ssi', 'hcm']
        result = {}

        for source in sources:
            df = self._load_source_json(source)
            if not df.empty:
                result[source] = df

        return result

    def get_multi_source_comparison(self, year: str = '2025F') -> pd.DataFrame:
        """
        Compare forecasts across multiple sources for overlapping tickers.

        Args:
            year: Forecast year ('2025F', '2026F', '2027F')

        Returns:
            DataFrame with ticker and forecasts from each source
        """
        import numpy as np

        sources_data = self.get_all_sources_data()

        if not sources_data:
            return pd.DataFrame()

        # Determine NPATMI column based on year
        year_suffix = year.lower().replace('f', 'f')  # e.g., '2025f'
        npatmi_col = f'npatmi_{year_suffix}'

        # Collect all unique symbols
        all_symbols = set()
        for df in sources_data.values():
            if 'symbol' in df.columns:
                all_symbols.update(df['symbol'].dropna().unique())

        # Build comparison dataframe
        rows = []
        for symbol in sorted(all_symbols):
            row = {'symbol': symbol}

            for source, df in sources_data.items():
                source_df = df[df['symbol'] == symbol]
                if source_df.empty:
                    row[f'{source}_npatmi'] = None
                    row[f'{source}_target'] = None
                else:
                    stock = source_df.iloc[0]
                    row[f'{source}_npatmi'] = stock.get(npatmi_col)
                    row[f'{source}_target'] = stock.get('target_price')
                    # Get sector from first available source
                    if 'sector' not in row or row.get('sector') == 'Unknown':
                        row['sector'] = stock.get('sector', 'Unknown')

            rows.append(row)

        result_df = pd.DataFrame(rows)

        # Calculate consensus metrics
        npatmi_cols = [c for c in result_df.columns if c.endswith('_npatmi')]
        target_cols = [c for c in result_df.columns if c.endswith('_target')]

        # Count how many sources cover each ticker
        result_df['source_count'] = result_df[npatmi_cols].notna().sum(axis=1)

        # Calculate average NPATMI and target across sources
        result_df['avg_npatmi'] = result_df[npatmi_cols].mean(axis=1, skipna=True)
        result_df['avg_target'] = result_df[target_cols].mean(axis=1, skipna=True)

        # Calculate std dev (measure of consensus)
        result_df['npatmi_std'] = result_df[npatmi_cols].std(axis=1, skipna=True)
        result_df['target_std'] = result_df[target_cols].std(axis=1, skipna=True)

        # Filter to tickers with at least 2 sources
        result_df = result_df[result_df['source_count'] >= 2].copy()

        # Sort by source count (more coverage = more interesting)
        result_df = result_df.sort_values('source_count', ascending=False)

        return result_df

    def get_source_coverage_stats(self) -> Dict[str, Dict]:
        """
        Get coverage statistics for each source.

        Returns:
            Dict with source -> {count, avg_npatmi_2025f, avg_target}
        """
        sources_data = self.get_all_sources_data()
        stats = {}

        for source, df in sources_data.items():
            if df.empty:
                continue

            stats[source] = {
                'count': len(df),
                'avg_npatmi_2025f': df['npatmi_2025f'].mean() if 'npatmi_2025f' in df.columns else None,
                'avg_npatmi_2026f': df['npatmi_2026f'].mean() if 'npatmi_2026f' in df.columns else None,
                'avg_target': df['target_price'].mean() if 'target_price' in df.columns else None,
            }

        return stats
