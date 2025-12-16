"""
Sector Service - Data Loading Layer
====================================

Service for loading sector analysis data combining valuation and registry.

Usage:
    from WEBAPP.services.sector_service import SectorService

    service = SectorService()
    df = service.get_sector_valuation()
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict


class SectorService:
    """Service layer for Sector analysis data."""

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize SectorService.

        Args:
            data_root: Root data directory (defaults to PROJECT_ROOT/DATA)
        """
        if data_root is None:
            current_file = Path(__file__).resolve()
            project_root = current_file.parents[2]
            data_root = project_root / "DATA"

        self.data_path = data_root / "processed" / "valuation"
        self.project_root = current_file.parents[2] if data_root is None else data_root.parent

        # Try to load sector registry
        self._sector_registry = None
        self._load_registry()

    def _load_registry(self):
        """Load sector registry if available."""
        try:
            from config.registries import SectorRegistry
            self._sector_registry = SectorRegistry()
        except Exception as e:
            print(f"Warning: Could not load SectorRegistry - {e}")

    def get_sector_valuation(self, date: Optional[str] = None, sectors_only: bool = False) -> pd.DataFrame:
        """
        Get PE/PB valuation for all sectors.

        Args:
            date: Specific date (YYYY-MM-DD), defaults to latest
            sectors_only: If True, only return sector scopes (exclude VNINDEX, BSC_INDEX)

        Returns:
            DataFrame with valuation per sector
        """
        # Try new file with sectors first
        parquet_file = self.data_path / "vnindex" / "vnindex_valuation_with_sectors.parquet"

        if not parquet_file.exists():
            # Fallback to old file
            parquet_file = self.data_path / "vnindex" / "vnindex_valuation_refined.parquet"

        if not parquet_file.exists():
            return pd.DataFrame()

        df = pd.read_parquet(parquet_file)

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

            if date:
                df = df[df['date'] == date]
            else:
                # Get latest date for each scope
                df = df.loc[df.groupby('scope')['date'].idxmax()]

        # Filter sectors only if requested
        if sectors_only and 'scope' in df.columns:
            df = df[df['scope'].str.startswith('SECTOR:')]
            # Clean up scope names (remove SECTOR: prefix)
            df = df.copy()
            df['scope'] = df['scope'].str.replace('SECTOR:', '', regex=False)

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

        # Fallback: get from valuation data
        parquet_file = self.data_path / "vnindex" / "vnindex_valuation_refined.parquet"

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
        Get historical valuation for a specific sector.

        Args:
            sector: Sector name (Vietnamese, e.g., "Ngân hàng")
            limit: Number of days (default 252 = 1 year)

        Returns:
            DataFrame with historical PE/PB
        """
        # Try new file with sectors first
        parquet_file = self.data_path / "vnindex" / "vnindex_valuation_with_sectors.parquet"

        if not parquet_file.exists():
            # Fallback to old file
            parquet_file = self.data_path / "vnindex" / "vnindex_valuation_refined.parquet"

        if not parquet_file.exists():
            return pd.DataFrame()

        df = pd.read_parquet(parquet_file)

        if 'scope' in df.columns:
            # Try with SECTOR: prefix first
            scope_name = f"SECTOR:{sector}"
            sector_df = df[df['scope'] == scope_name].copy()

            # If empty, try without prefix (for backward compatibility)
            if sector_df.empty:
                sector_df = df[df['scope'] == sector].copy()

            df = sector_df

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

        if limit:
            df = df.tail(limit)

        return df
