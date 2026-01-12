#!/usr/bin/env python3
"""
RRG (Relative Rotation Graph) Calculator
==========================================

Calculate Relative Rotation Graph coordinates for sectors.
Used by Technical Dashboard Tab 2: Sector Rotation.

RRG Components:
- RS-Ratio: Relative strength vs VN-Index (normalized around 100)
- RS-Momentum: Rate of change of RS-Ratio (normalized around 100)

Quadrants:
- LEADING (upper right): RS-Ratio > 100, RS-Momentum > 100
- WEAKENING (lower right): RS-Ratio > 100, RS-Momentum < 100
- LAGGING (lower left): RS-Ratio < 100, RS-Momentum < 100
- IMPROVING (upper left): RS-Ratio < 100, RS-Momentum > 100

Output: DATA/processed/technical/sector/rrg_latest.parquet

Author: Claude Code
Date: 2025-12-31
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from typing import Optional

# Add project root
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RRGCalculator:
    """Calculate RRG coordinates for sectors."""

    # Lookback periods
    RS_PERIOD = 10  # Period for RS-Ratio calculation
    MOM_PERIOD = 10  # Period for RS-Momentum calculation
    HISTORY_DAYS = 60  # Days of history needed

    def __init__(self):
        """Initialize calculator."""
        self.project_root = project_root

        # Input paths
        self.technical_path = self.project_root / "DATA/processed/technical/basic_data.parquet"
        self.vnindex_path = self.project_root / "DATA/processed/technical/vnindex/vnindex_indicators.parquet"

        # Output
        self.output_dir = self.project_root / "DATA/processed/technical/sector"
        self.output_path = self.output_dir / "rrg_latest.parquet"

    def calculate(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate RRG coordinates for all sectors.

        Args:
            date: Target date (YYYY-MM-DD), defaults to latest

        Returns:
            DataFrame with sector RRG data
        """
        logger.info("Calculating RRG coordinates...")

        # Load data
        tech_df = self._load_technical_data()
        vnindex_df = self._load_vnindex()

        if tech_df.empty or vnindex_df.empty:
            logger.error("Insufficient data for RRG calculation")
            return pd.DataFrame()

        # Determine target date
        if date:
            target_date = pd.to_datetime(date)
        else:
            target_date = tech_df['date'].max()

        logger.info(f"Target date: {target_date}")

        # Calculate sector performance
        sector_prices = self._calculate_sector_prices(tech_df)

        # Calculate RS-Ratio and RS-Momentum for each sector
        results = []
        for sector, prices in sector_prices.items():
            rrg_data = self._calculate_rrg_values(prices, vnindex_df, target_date)
            if rrg_data:
                rrg_data['sector_code'] = sector
                rrg_data['date'] = target_date.strftime('%Y-%m-%d')
                results.append(rrg_data)

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)

        # Determine quadrant and trend
        df['quadrant'] = df.apply(self._determine_quadrant, axis=1)
        df['trend_direction'] = df.apply(self._determine_trend, axis=1)

        # Calculate days in current quadrant (simplified)
        df['days_in_quadrant'] = 1  # Would need historical tracking

        logger.info(f"Calculated RRG for {len(df)} sectors")
        return df

    def _load_technical_data(self) -> pd.DataFrame:
        """Load technical data with sufficient history."""
        if not self.technical_path.exists():
            logger.warning("Technical data not found")
            return pd.DataFrame()

        df = pd.read_parquet(self.technical_path)
        df['date'] = pd.to_datetime(df['date'])

        # Filter to last N days
        cutoff = df['date'].max() - pd.Timedelta(days=self.HISTORY_DAYS)
        df = df[df['date'] >= cutoff]

        return df

    def _load_vnindex(self) -> pd.DataFrame:
        """Load VN-Index data."""
        if not self.vnindex_path.exists():
            logger.warning("VN-Index data not found")
            return pd.DataFrame()

        df = pd.read_parquet(self.vnindex_path)
        df['date'] = pd.to_datetime(df['date'])

        return df

    def _calculate_sector_prices(self, df: pd.DataFrame) -> dict:
        """Calculate sector price series (market-cap weighted)."""
        try:
            from config.registries import SectorRegistry
            sector_reg = SectorRegistry()
        except Exception as e:
            logger.error(f"Cannot load SectorRegistry: {e}")
            return {}

        # Map symbols to sectors
        df = df.copy()

        def get_sector_safe(symbol):
            try:
                info = sector_reg.get_ticker(symbol)
                return info.get('sector', 'Unknown') if info else 'Unknown'
            except Exception:
                return 'Unknown'

        df['sector'] = df['symbol'].apply(get_sector_safe)

        # Filter out unknown
        df = df[df['sector'] != 'Unknown']

        # Calculate sector index (market-cap weighted)
        sector_prices = {}
        for sector in df['sector'].unique():
            sector_df = df[df['sector'] == sector]

            # Group by date, calculate weighted average close
            if 'market_cap' in sector_df.columns:
                daily = sector_df.groupby('date').apply(
                    lambda x: np.average(x['close'], weights=x['market_cap'])
                    if x['market_cap'].sum() > 0 else x['close'].mean(),
                    include_groups=False
                )
            else:
                daily = sector_df.groupby('date')['close'].mean()

            sector_prices[sector] = daily.sort_index()

        return sector_prices

    def _calculate_rrg_values(self, sector_prices: pd.Series, vnindex: pd.DataFrame,
                              target_date: pd.Timestamp) -> Optional[dict]:
        """Calculate RS-Ratio and RS-Momentum for a sector."""
        # Align dates
        vnindex = vnindex.set_index('date')['close']
        common_dates = sector_prices.index.intersection(vnindex.index)

        if len(common_dates) < self.RS_PERIOD + self.MOM_PERIOD:
            return None

        sector = sector_prices.loc[common_dates].sort_index()
        benchmark = vnindex.loc[common_dates].sort_index()

        # Calculate RS-Line (sector / benchmark)
        rs_line = sector / benchmark * 100

        # Normalize RS-Line using rolling mean and std
        rs_ratio = rs_line.rolling(self.RS_PERIOD).mean()

        # Normalize around 100
        rs_ratio_normalized = (rs_ratio / rs_ratio.rolling(self.RS_PERIOD).mean()) * 100

        # Calculate RS-Momentum (rate of change of RS-Ratio)
        rs_momentum = rs_ratio_normalized.pct_change(self.MOM_PERIOD, fill_method=None) * 100 + 100

        # Get latest values
        if target_date in rs_ratio_normalized.index and target_date in rs_momentum.index:
            rs_r = rs_ratio_normalized.loc[target_date]
            rs_m = rs_momentum.loc[target_date]
        else:
            rs_r = rs_ratio_normalized.iloc[-1]
            rs_m = rs_momentum.iloc[-1]

        if pd.isna(rs_r) or pd.isna(rs_m):
            return None

        return {
            'rs_ratio': round(rs_r, 2),
            'rs_momentum': round(rs_m, 2)
        }

    def _determine_quadrant(self, row) -> str:
        """Determine RRG quadrant."""
        rs_ratio = row['rs_ratio']
        rs_momentum = row['rs_momentum']

        if rs_ratio >= 100 and rs_momentum >= 100:
            return 'LEADING'
        elif rs_ratio >= 100 and rs_momentum < 100:
            return 'WEAKENING'
        elif rs_ratio < 100 and rs_momentum < 100:
            return 'LAGGING'
        else:  # rs_ratio < 100 and rs_momentum >= 100
            return 'IMPROVING'

    def _determine_trend(self, row) -> str:
        """Determine trend direction based on momentum."""
        rs_momentum = row['rs_momentum']

        if rs_momentum > 102:
            return 'ACCELERATING'
        elif rs_momentum > 100:
            return 'STABLE'
        elif rs_momentum > 98:
            return 'SLOWING'
        else:
            return 'DECLINING'

    def save(self, df: pd.DataFrame) -> Path:
        """Save RRG data to parquet."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self.output_path, index=False)
        logger.info(f"Saved RRG data to {self.output_path}")
        return self.output_path

    def run(self, date: Optional[str] = None) -> pd.DataFrame:
        """Calculate and save RRG data."""
        df = self.calculate(date)
        if not df.empty:
            self.save(df)
        return df


if __name__ == "__main__":
    calculator = RRGCalculator()
    result = calculator.run()
    if not result.empty:
        print("\nRRG by Quadrant:")
        for quadrant in ['LEADING', 'IMPROVING', 'WEAKENING', 'LAGGING']:
            sectors = result[result['quadrant'] == quadrant]['sector_code'].tolist()
            print(f"  {quadrant}: {', '.join(sectors[:5])}")
