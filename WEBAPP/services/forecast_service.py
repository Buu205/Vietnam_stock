"""
Forecast Service - Data Loading Layer
======================================

Service for loading BSC Forecast data from parquet files.

Usage:
    from WEBAPP.services.forecast_service import ForecastService

    service = ForecastService()
    individual = service.get_individual_stocks()
    sectors = service.get_sector_valuation()
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List


class ForecastService:
    """Service layer for BSC Forecast data."""

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize ForecastService.

        Args:
            data_root: Root data directory (defaults to PROJECT_ROOT/DATA)
        """
        if data_root is None:
            current_file = Path(__file__).resolve()
            project_root = current_file.parents[2]
            data_root = project_root / "DATA"

        self.data_root = data_root
        self.data_path = data_root / "processed" / "forecast" / "bsc"

    def get_individual_stocks(self) -> pd.DataFrame:
        """
        Load individual stocks forecast data.

        Returns:
            DataFrame with 92 stocks and all metrics
        """
        file_path = self.data_path / "bsc_individual.parquet"

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
        file_path = self.data_path / "bsc_sector_valuation.parquet"

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
        file_path = self.data_path / "bsc_combined.parquet"

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
        Get list of BSC sectors.

        Returns:
            List of sector names
        """
        df = self.get_sector_valuation()

        if df.empty or 'bsc_sector' not in df.columns:
            return []

        return sorted(df['bsc_sector'].unique().tolist())

    def get_stocks_by_sector(self, sector: str) -> pd.DataFrame:
        """
        Get individual stocks filtered by BSC sector.

        Args:
            sector: BSC sector name (e.g., "Bank", "RE")

        Returns:
            Filtered DataFrame
        """
        df = self.get_individual_stocks()

        if df.empty or 'bsc_sector' not in df.columns:
            return pd.DataFrame()

        return df[df['bsc_sector'] == sector]

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
