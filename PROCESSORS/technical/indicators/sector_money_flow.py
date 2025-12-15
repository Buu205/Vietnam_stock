#!/usr/bin/env python3
"""
Sector Money Flow Analyzer
===========================

Track money flow by sector:
- Aggregate (Price × Volume) per sector
- Calculate inflow/outflow % vs previous period (1D, 1W, 1M)
- Identify top contributors
- Multi-timeframe analysis (daily, weekly, monthly)

Author: Claude Code
Date: 2025-12-15
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

# Add project root
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from config.registries import SectorRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SectorMoneyFlowAnalyzer:
    """Calculate money flow for each sector."""

    def __init__(self, ohlcv_path: str = "DATA/raw/ohlcv/OHLCV_mktcap.parquet"):
        """
        Initialize analyzer.

        Args:
            ohlcv_path: Path to OHLCV data
        """
        self.ohlcv_path = Path(ohlcv_path)
        self.sector_reg = SectorRegistry()

        if not self.ohlcv_path.exists():
            raise FileNotFoundError(f"OHLCV file not found: {self.ohlcv_path}")

    def calculate_sector_money_flow(self, date: str = None) -> pd.DataFrame:
        """
        Calculate daily money flow for all sectors.

        Args:
            date: Target date (default: latest)

        Returns:
            DataFrame with sector money flow
        """
        logger.info(f"Calculating sector money flow...")

        # Load OHLCV data
        df = pd.read_parquet(self.ohlcv_path)

        if date is None:
            date = df['date'].max()

        # Filter to date
        day_df = df[df['date'] == date].copy()

        if len(day_df) == 0:
            logger.warning(f"No data for date {date}")
            return pd.DataFrame()

        # Calculate money flow for each stock
        day_df['money_flow'] = day_df['close'] * day_df['volume']

        # Add sector information
        day_df['sector_code'] = day_df['symbol'].apply(
            lambda x: self._get_sector(x)
        )

        # Remove unknown sectors
        day_df = day_df[day_df['sector_code'] != 'UNKNOWN']

        # Aggregate by sector
        sector_flow = day_df.groupby('sector_code').agg({
            'money_flow': 'sum',
            'symbol': 'count'
        }).reset_index()

        sector_flow.columns = ['sector_code', 'money_flow', 'stock_count']

        # Get previous day for comparison
        prev_date = self._get_previous_trading_date(df, date)
        if prev_date:
            prev_flow = self._calculate_for_date(df, prev_date)
            sector_flow = sector_flow.merge(
                prev_flow[['sector_code', 'money_flow']],
                on='sector_code',
                how='left',
                suffixes=('', '_prev')
            )

            sector_flow['inflow_pct'] = (
                (sector_flow['money_flow'] - sector_flow['money_flow_prev']) /
                sector_flow['money_flow_prev'] * 100
            ).fillna(0)
        else:
            sector_flow['inflow_pct'] = 0.0

        # Classify flow signal
        sector_flow['flow_signal'] = sector_flow['inflow_pct'].apply(
            lambda x: 'STRONG_INFLOW' if x > 10 else
                     'INFLOW' if x > 3 else
                     'STRONG_OUTFLOW' if x < -10 else
                     'OUTFLOW' if x < -3 else
                     'NEUTRAL'
        )

        # Top contributors
        sector_flow['top_contributors'] = sector_flow['sector_code'].apply(
            lambda s: self._get_top_contributors(day_df, s, top_n=3)
        )

        sector_flow['date'] = date

        # Sort by money flow
        sector_flow = sector_flow.sort_values('money_flow', ascending=False)

        logger.info(f"✅ Calculated sector money flow for {len(sector_flow)} sectors")

        return sector_flow[['date', 'sector_code', 'money_flow', 'inflow_pct', 'flow_signal', 'stock_count', 'top_contributors']]

    def _get_sector(self, symbol: str) -> str:
        """Get sector for symbol."""
        try:
            ticker_info = self.sector_reg.get_ticker(symbol)
            if ticker_info:
                # Try sector_code first, fallback to industry_code
                return ticker_info.get('sector_code') or ticker_info.get('industry_code', 'UNKNOWN')
            return 'UNKNOWN'
        except:
            return 'UNKNOWN'

    def _calculate_for_date(self, df: pd.DataFrame, date) -> pd.DataFrame:
        """Helper to calculate for specific date."""
        day_df = df[df['date'] == date].copy()
        day_df['money_flow'] = day_df['close'] * day_df['volume']
        day_df['sector_code'] = day_df['symbol'].apply(self._get_sector)
        day_df = day_df[day_df['sector_code'] != 'UNKNOWN']

        sector_flow = day_df.groupby('sector_code').agg({
            'money_flow': 'sum'
        }).reset_index()

        return sector_flow

    def _get_previous_trading_date(self, df: pd.DataFrame, date, lookback_days: int = 1):
        """
        Get previous trading date with lookback period.

        Args:
            df: DataFrame with dates
            date: Current date
            lookback_days: Number of calendar days to look back (1, 7, 30)

        Returns:
            Previous trading date
        """
        all_dates = sorted(df['date'].unique())

        if lookback_days == 1:
            # Get previous day
            try:
                idx = all_dates.index(date)
                if idx > 0:
                    return all_dates[idx - 1]
            except:
                pass
        else:
            # Get closest date N days ago
            target_date = date - timedelta(days=lookback_days)

            # Find closest trading date before target_date
            dates_before = [d for d in all_dates if d <= target_date]
            if dates_before:
                return dates_before[-1]

        return None

    def _get_top_contributors(self, df: pd.DataFrame, sector_code: str, top_n: int = 3) -> str:
        """Get top N stocks by money flow in sector."""
        sector_df = df[df['sector_code'] == sector_code].copy()
        sector_df = sector_df.nlargest(top_n, 'money_flow')
        return ', '.join(sector_df['symbol'].tolist())

    def calculate_multi_timeframe_flow(self, date: str = None) -> dict:
        """
        Calculate sector money flow for multiple timeframes.

        Args:
            date: Target date (default: latest)

        Returns:
            Dictionary with DataFrames for 1D, 1W, 1M timeframes
        """
        logger.info(f"Calculating multi-timeframe sector money flow...")

        # Load OHLCV data
        df = pd.read_parquet(self.ohlcv_path)

        if date is None:
            date = df['date'].max()

        # Convert date to datetime.date if it's a string
        if isinstance(date, str):
            date = pd.to_datetime(date).date()

        results = {}

        # 1D (Daily)
        logger.info("  [1/3] Calculating 1D money flow...")
        flow_1d = self._calculate_flow_with_lookback(df, date, lookback_days=1, timeframe='1D')
        results['1D'] = flow_1d

        # 1W (Weekly - 7 days)
        logger.info("  [2/3] Calculating 1W money flow...")
        flow_1w = self._calculate_flow_with_lookback(df, date, lookback_days=7, timeframe='1W')
        results['1W'] = flow_1w

        # 1M (Monthly - 30 days)
        logger.info("  [3/3] Calculating 1M money flow...")
        flow_1m = self._calculate_flow_with_lookback(df, date, lookback_days=30, timeframe='1M')
        results['1M'] = flow_1m

        logger.info(f"✅ Multi-timeframe calculation complete")
        return results

    def _calculate_flow_with_lookback(self, df: pd.DataFrame, date, lookback_days: int, timeframe: str) -> pd.DataFrame:
        """
        Calculate sector money flow with specific lookback period.

        Args:
            df: OHLCV DataFrame
            date: Target date
            lookback_days: Days to look back (1, 7, 30)
            timeframe: Timeframe label ('1D', '1W', '1M')

        Returns:
            DataFrame with sector money flow
        """
        # Filter to date
        day_df = df[df['date'] == date].copy()

        if len(day_df) == 0:
            logger.warning(f"No data for date {date}")
            return pd.DataFrame()

        # Calculate money flow for each stock
        day_df['money_flow'] = day_df['close'] * day_df['volume']

        # Add sector information
        day_df['sector_code'] = day_df['symbol'].apply(self._get_sector)

        # Remove unknown sectors
        day_df = day_df[day_df['sector_code'] != 'UNKNOWN']

        # Aggregate by sector
        sector_flow = day_df.groupby('sector_code').agg({
            'money_flow': 'sum',
            'symbol': 'count'
        }).reset_index()

        sector_flow.columns = ['sector_code', 'money_flow', 'stock_count']

        # Get previous period for comparison
        prev_date = self._get_previous_trading_date(df, date, lookback_days=lookback_days)

        if prev_date:
            prev_flow = self._calculate_for_date(df, prev_date)
            sector_flow = sector_flow.merge(
                prev_flow[['sector_code', 'money_flow']],
                on='sector_code',
                how='left',
                suffixes=('', '_prev')
            )

            sector_flow['inflow_pct'] = (
                (sector_flow['money_flow'] - sector_flow['money_flow_prev']) /
                sector_flow['money_flow_prev'] * 100
            ).fillna(0)
        else:
            sector_flow['inflow_pct'] = 0.0

        # Classify flow signal
        sector_flow['flow_signal'] = sector_flow['inflow_pct'].apply(
            lambda x: 'STRONG_INFLOW' if x > 10 else
                     'INFLOW' if x > 3 else
                     'STRONG_OUTFLOW' if x < -10 else
                     'OUTFLOW' if x < -3 else
                     'NEUTRAL'
        )

        # Top contributors
        sector_flow['top_contributors'] = sector_flow['sector_code'].apply(
            lambda s: self._get_top_contributors(day_df, s, top_n=3)
        )

        sector_flow['date'] = date
        sector_flow['timeframe'] = timeframe

        # Sort by money flow
        sector_flow = sector_flow.sort_values('money_flow', ascending=False)

        return sector_flow[['date', 'timeframe', 'sector_code', 'money_flow', 'inflow_pct',
                           'flow_signal', 'stock_count', 'top_contributors']]

    def save_sector_money_flow(self, df: pd.DataFrame, output_path: str = "DATA/processed/technical/money_flow/sector_money_flow.parquet"):
        """Save sector money flow (append mode)."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert date
        df['date'] = pd.to_datetime(df['date']).dt.date

        # Append or create
        if output_path.exists():
            existing = pd.read_parquet(output_path)
            # Remove duplicate date
            existing = existing[existing['date'] != df['date'].iloc[0]]
            combined = pd.concat([existing, df], ignore_index=True)
            combined = combined.sort_values('date').reset_index(drop=True)
            combined.to_parquet(output_path, index=False)
            logger.info(f"✅ Updated sector money flow (total: {len(combined)} records)")
        else:
            df.to_parquet(output_path, index=False)
            logger.info(f"✅ Created new sector money flow file")

    def save_multi_timeframe_flow(self, results: dict):
        """
        Save multi-timeframe sector money flow.

        Args:
            results: Dictionary with DataFrames for 1D, 1W, 1M
        """
        output_dir = Path("DATA/processed/technical/money_flow")
        output_dir.mkdir(parents=True, exist_ok=True)

        for timeframe, df in results.items():
            if df.empty:
                continue

            output_path = output_dir / f"sector_money_flow_{timeframe.lower()}.parquet"

            # Convert date
            df['date'] = pd.to_datetime(df['date']).dt.date

            # Append or create
            if output_path.exists():
                existing = pd.read_parquet(output_path)
                # Remove duplicate date
                existing = existing[existing['date'] != df['date'].iloc[0]]
                combined = pd.concat([existing, df], ignore_index=True)
                combined = combined.sort_values('date').reset_index(drop=True)
                combined.to_parquet(output_path, index=False)
                logger.info(f"✅ Updated {timeframe} sector money flow (total: {len(combined)} records)")
            else:
                df.to_parquet(output_path, index=False)
                logger.info(f"✅ Created new {timeframe} sector money flow file")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Sector Money Flow Analyzer')
    parser.add_argument('--date', type=str, default=None, help='Target date (YYYY-MM-DD)')
    parser.add_argument('--multi-timeframe', action='store_true', help='Calculate for 1D, 1W, 1M')

    args = parser.parse_args()

    try:
        analyzer = SectorMoneyFlowAnalyzer()

        if args.multi_timeframe:
            # Multi-timeframe mode
            results = analyzer.calculate_multi_timeframe_flow(date=args.date)
            analyzer.save_multi_timeframe_flow(results)

            # Print summary
            date_str = results['1D']['date'].iloc[0] if not results['1D'].empty else 'N/A'
            print("\n" + "=" * 100)
            print(f"SECTOR MONEY FLOW (MULTI-TIMEFRAME) - {date_str}")
            print("=" * 100)

            for timeframe in ['1D', '1W', '1M']:
                df = results[timeframe]
                if not df.empty:
                    print(f"\n{timeframe} Timeframe:")
                    print("-" * 100)
                    print(df[['sector_code', 'money_flow', 'inflow_pct', 'flow_signal']].head(10).to_string(index=False))

            print("=" * 100)

        else:
            # Single day mode (default)
            df = analyzer.calculate_sector_money_flow(date=args.date)

            if not df.empty:
                analyzer.save_sector_money_flow(df)

                # Print summary
                print("\n" + "=" * 80)
                print(f"SECTOR MONEY FLOW - {df['date'].iloc[0]}")
                print("=" * 80)
                print(df[['sector_code', 'money_flow', 'inflow_pct', 'flow_signal', 'top_contributors']].to_string(index=False))
                print("=" * 80)

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
