"""
Sector Service - Data Loading Layer
====================================

Service for loading sector analysis data combining valuation and registry.
Uses DataMappingRegistry for path resolution.

Usage:
    from WEBAPP.services.sector_service import SectorService

    service = SectorService()
    df = service.get_sector_valuation()

Author: AI Assistant
Date: 2025-12-31
Version: 2.0.0 (Registry Integration)
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict

from .base_service import BaseService


class SectorService(BaseService):
    """Service layer for Sector analysis data."""

    DATA_SOURCE = "sector_valuation"
    ENTITY_TYPE = "all"

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize SectorService.

        Args:
            data_root: Root data directory (for testing, defaults to registry path)
        """
        super().__init__(data_root)
        self._sector_registry = None
        self._load_registry()

    def _load_registry(self):
        """Load sector registry if available."""
        try:
            from config.registries import SectorRegistry
            self._sector_registry = SectorRegistry()
        except Exception as e:
            print(f"Warning: Could not load SectorRegistry - {e}")

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
            if source_name == "sector_valuation":
                return self.data_root / "processed" / "sector" / "sector_valuation_metrics.parquet"
            elif source_name == "vnindex_valuation":
                return self.data_root / "processed" / "valuation" / "vnindex" / "vnindex_valuation_refined.parquet"
            return self.data_root / "processed" / f"{source_name}.parquet"

    def get_sector_valuation(self, date: Optional[str] = None, sectors_only: bool = False) -> pd.DataFrame:
        """
        Get PE/PB valuation for all sectors and market indices.

        Args:
            date: Specific date (YYYY-MM-DD), defaults to latest
            sectors_only: If True, only return sector scopes (exclude VNINDEX, BSC_INDEX)

        Returns:
            DataFrame with valuation per sector/index
        """
        all_dfs = []

        # Load sector data via registry
        sector_file = self._get_path("sector_valuation")

        if sector_file.exists():
            sector_df = pd.read_parquet(sector_file)

            # Add SECTOR: prefix to sector_code for dashboard compatibility
            if 'sector_code' in sector_df.columns:
                sector_df['sector_code'] = 'SECTOR:' + sector_df['sector_code'].astype(str)

            # Map columns to expected format
            column_mapping = {
                'sector_code': 'scope',
                'sector_pe': 'pe_ttm',
                'sector_pb': 'pb',
                'sector_ps': 'ps',
                'sector_ev_ebitda': 'ev_ebitda',
                'sector_market_cap': 'market_cap'
            }
            sector_df = sector_df.rename(columns=column_mapping)

            if 'date' in sector_df.columns:
                sector_df['date'] = pd.to_datetime(sector_df['date'])

            all_dfs.append(sector_df)

        # Load market index data via registry
        if not sectors_only:
            vnindex_file = self._get_path("vnindex_valuation")

            if vnindex_file.exists():
                vnindex_df = pd.read_parquet(vnindex_file)

                if 'date' in vnindex_df.columns:
                    vnindex_df['date'] = pd.to_datetime(vnindex_df['date'])

                all_dfs.append(vnindex_df)

        # Merge all dataframes
        if not all_dfs:
            return pd.DataFrame()

        df = pd.concat(all_dfs, ignore_index=True)

        # Filter by date
        if 'date' in df.columns:
            if date:
                df = df[df['date'] == date]
            else:
                # Get latest date for each scope
                df = df.loc[df.groupby('scope')['date'].idxmax()]

        # Filter sectors only if requested
        if sectors_only and 'scope' in df.columns:
            df = df[df['scope'].str.startswith('SECTOR:')]

        # Sort by PE
        if 'pe_ttm' in df.columns:
            df = df.sort_values('pe_ttm')

        return df

    def get_all_sectors(self) -> List[str]:
        """Get list of all tracked sectors."""
        if self._sector_registry:
            try:
                return self._sector_registry.get_all_sectors()
            except Exception:
                pass

        # Get from sector_valuation_metrics.parquet via registry
        sector_file = self._get_path("sector_valuation")

        if sector_file.exists():
            df = pd.read_parquet(sector_file, columns=['sector_code'])
            return sorted(df['sector_code'].unique().tolist())

        # Fallback: get from vnindex valuation data
        parquet_file = self._get_path("vnindex_valuation")

        if not parquet_file.exists():
            return []

        df = pd.read_parquet(parquet_file, columns=['scope'])
        scopes = df['scope'].unique().tolist()

        # Remove VNINDEX from sectors list
        return sorted([s for s in scopes if s != 'VNINDEX'])

    def get_sector_tickers(self, sector: str) -> List[str]:
        """Get list of tickers in a sector."""
        if self._sector_registry:
            try:
                return self._sector_registry.get_tickers_by_sector(sector)
            except Exception:
                pass
        return []

    def get_sector_info(self, sector: str) -> Dict:
        """
        Get detailed info for a sector.

        Returns:
            Dict with sector name, ticker count, valuation, etc.
        """
        result = {
            'sector': sector,
            'ticker_count': 0,
            'tickers': [],
            'pe_ttm': None,
            'pb': None
        }

        # Get tickers
        tickers = self.get_sector_tickers(sector)
        result['ticker_count'] = len(tickers)
        result['tickers'] = tickers[:10]  # Top 10 only

        # Get valuation
        valuation = self.get_sector_valuation()
        if not valuation.empty and 'scope' in valuation.columns:
            sector_row = valuation[valuation['scope'] == sector]
            if not sector_row.empty:
                row = sector_row.iloc[0]
                result['pe_ttm'] = row.get('pe_ttm')
                result['pb'] = row.get('pb')

        return result

    def get_market_overview(self) -> Dict:
        """
        Get market-wide overview.

        Returns:
            Dict with VNINDEX valuation, sector count, ticker count
        """
        result = {
            'market_pe': None,
            'market_pb': None,
            'sector_count': 0,
            'ticker_count': 0,
            'top_sector': None,
            'bottom_sector': None
        }

        # Get VNINDEX valuation
        valuation = self.get_sector_valuation()
        if not valuation.empty:
            vnindex = valuation[valuation['scope'] == 'VNINDEX']
            if not vnindex.empty:
                result['market_pe'] = vnindex.iloc[0].get('pe_ttm')
                result['market_pb'] = vnindex.iloc[0].get('pb')

            # Get sector stats (only SECTOR: scopes)
            sectors = valuation[valuation['scope'].str.startswith('SECTOR:')]
            if not sectors.empty and 'pe_ttm' in sectors.columns:
                # Filter valid PE (positive)
                valid_sectors = sectors[sectors['pe_ttm'] > 0].copy()
                if not valid_sectors.empty:
                    valid_sectors = valid_sectors.sort_values('pe_ttm')
                    # Clean up names
                    top_scope = valid_sectors.iloc[0]['scope'].replace('SECTOR:', '')
                    bottom_scope = valid_sectors.iloc[-1]['scope'].replace('SECTOR:', '')
                    result['top_sector'] = top_scope  # Lowest PE
                    result['bottom_sector'] = bottom_scope  # Highest PE

        # Get counts
        all_sectors = self.get_all_sectors()
        result['sector_count'] = len(all_sectors)

        if self._sector_registry:
            try:
                result['ticker_count'] = len(self._sector_registry.get_all_tickers())
            except Exception:
                pass

        return result

    def get_sector_comparison(
        self,
        metrics: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Get comparison table across all sectors.

        Args:
            metrics: List of metrics to include (default: pe_ttm, pb)

        Returns:
            DataFrame with sectors as rows, metrics as columns
        """
        if metrics is None:
            metrics = ['pe_ttm', 'pb', 'pe_fwd_2025', 'pe_fwd_2026']

        df = self.get_sector_valuation()

        if df.empty:
            return pd.DataFrame()

        # Filter columns
        available_cols = ['scope', 'date'] + [m for m in metrics if m in df.columns]
        df = df[available_cols]

        # Exclude VNINDEX for pure sector comparison
        df = df[df['scope'] != 'VNINDEX']

        return df

    def get_sector_history(
        self,
        sector: str,
        limit: Optional[int] = 252
    ) -> pd.DataFrame:
        """
        Get historical valuation for a specific sector or market index.

        Args:
            sector: Sector name (Vietnamese, e.g., "Ngân hàng") or market index (VNINDEX, BSC_INDEX)
            limit: Number of days (default 252 = 1 year)

        Returns:
            DataFrame with historical PE/PB
        """
        # Check if this is a market index
        market_indices = ['VNINDEX', 'VNINDEX_EXCLUDE', 'BSC_INDEX']

        if sector in market_indices:
            # Load from vnindex file via registry
            vnindex_file = self._get_path("vnindex_valuation")

            if not vnindex_file.exists():
                return pd.DataFrame()

            df = pd.read_parquet(vnindex_file)

            if 'scope' in df.columns:
                df = df[df['scope'] == sector].copy()

            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')

            if limit:
                df = df.tail(limit)

            return df

        # For sectors: Load from sector_valuation_metrics.parquet via registry
        sector_file = self._get_path("sector_valuation")

        if sector_file.exists():
            df = pd.read_parquet(sector_file)

            # Filter by sector (handle both with and without SECTOR: prefix)
            if 'sector_code' in df.columns:
                clean_sector = sector.replace('SECTOR:', '')
                df = df[df['sector_code'] == clean_sector].copy()

            # Map columns to expected format
            column_mapping = {
                'sector_code': 'scope',
                'sector_pe': 'pe_ttm',
                'sector_pb': 'pb',
                'sector_ps': 'ps',
                'sector_ev_ebitda': 'ev_ebitda',
                'sector_market_cap': 'market_cap'
            }
            df = df.rename(columns=column_mapping)

            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')

            if limit:
                df = df.tail(limit)

            return df

        return pd.DataFrame()
