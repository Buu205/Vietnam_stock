"""
Daily Sector Valuation Update Script
=====================================

Updates sector valuation metrics daily based on latest market data.
Compares with existing data to show changes.

Author: Claude Code
Date: 2025-12-15
Version: 1.0.0

Usage:
    python3 PROCESSORS/sector/daily_sector_valuation_update.py
    python3 PROCESSORS/sector/daily_sector_valuation_update.py --date 2025-12-15
    python3 PROCESSORS/sector/daily_sector_valuation_update.py --compare-days 7
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse
import logging

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from config.registries import SectorRegistry
from PROCESSORS.sector.calculators import TAAggregator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DailySectorValuationUpdater:
    """
    Daily updater for sector valuation metrics.

    This script:
    1. Loads latest OHLCV and valuation data
    2. Aggregates by sector for latest trading day
    3. Compares with previous day/week
    4. Appends to existing sector_valuation_metrics.parquet
    5. Shows summary of changes
    """

    def __init__(self):
        """Initialize updater."""
        self.project_root = project_root
        self.data_root = self.project_root / "DATA"
        self.output_path = self.data_root / "processed" / "sector" / "sector_valuation_metrics.parquet"

        # Initialize sector registry
        self.sector_reg = SectorRegistry()

        # Initialize TA Aggregator (does valuation aggregation)
        from config.schema_registry import SchemaRegistry
        self.ta_agg = TAAggregator(
            config_manager=SchemaRegistry(),
            sector_registry=self.sector_reg
        )

        logger.info(f"Initialized DailySectorValuationUpdater")
        logger.info(f"Output path: {self.output_path}")

    def load_existing_data(self) -> pd.DataFrame:
        """Load existing sector valuation data."""
        if self.output_path.exists():
            df = pd.read_parquet(self.output_path)
            logger.info(f"Loaded existing data: {len(df)} records, latest date: {df['date'].max()}")
            return df
        else:
            logger.warning("No existing sector valuation data found")
            return pd.DataFrame()

    def get_latest_trading_date(self) -> pd.Timestamp:
        """Get latest trading date from OHLCV data."""
        ohlcv_path = self.data_root / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"
        df = pd.read_parquet(ohlcv_path)
        latest = df['time'].max()
        logger.info(f"Latest trading date: {latest}")
        return latest

    def calculate_daily_valuation(self, target_date: str = None) -> pd.DataFrame:
        """
        Calculate sector valuation for a specific date.

        Args:
            target_date: Target date (YYYY-MM-DD). If None, uses latest trading date.

        Returns:
            DataFrame with sector valuation metrics for the date
        """
        if target_date is None:
            target_date = self.get_latest_trading_date()

        logger.info(f"Calculating sector valuation for {target_date}")

        # Run TA aggregation for single date
        # This internally calls the same logic as full pipeline
        result_df = self.ta_agg.aggregate_sector_valuation(
            start_date=str(target_date),
            end_date=str(target_date)
        )

        logger.info(f"Calculated {len(result_df)} sector records")
        return result_df

    def compare_with_previous(
        self,
        current: pd.DataFrame,
        previous: pd.DataFrame,
        comparison_date: pd.Timestamp
    ) -> pd.DataFrame:
        """
        Compare current valuation with previous date.

        Args:
            current: Current date sector data
            previous: Previous date sector data
            comparison_date: Date to compare with

        Returns:
            DataFrame with comparison metrics
        """
        if previous.empty:
            logger.warning("No previous data for comparison")
            return current

        # Filter previous to comparison date
        prev_data = previous[previous['date'] == comparison_date]

        if prev_data.empty:
            logger.warning(f"No data found for comparison date {comparison_date}")
            return current

        # Merge and calculate changes
        comparison = current.merge(
            prev_data[['sector_code', 'sector_pe', 'sector_pb', 'sector_market_cap']],
            on='sector_code',
            how='left',
            suffixes=('', '_prev')
        )

        # Calculate changes
        comparison['pe_change'] = comparison['sector_pe'] - comparison['sector_pe_prev']
        comparison['pe_change_pct'] = (comparison['pe_change'] / comparison['sector_pe_prev']) * 100

        comparison['pb_change'] = comparison['sector_pb'] - comparison['sector_pb_prev']
        comparison['pb_change_pct'] = (comparison['pb_change'] / comparison['sector_pb_prev']) * 100

        comparison['mktcap_change'] = comparison['sector_market_cap'] - comparison['sector_market_cap_prev']
        comparison['mktcap_change_pct'] = (comparison['mktcap_change'] / comparison['sector_market_cap_prev']) * 100

        return comparison

    def update_and_save(self, new_data: pd.DataFrame, mode: str = 'append'):
        """
        Update existing data with new records.

        Args:
            new_data: New sector valuation data
            mode: 'append' or 'replace'
        """
        if mode == 'replace':
            new_data.to_parquet(self.output_path, index=False)
            logger.info(f"Replaced data: {len(new_data)} records")
        else:
            existing = self.load_existing_data()

            if existing.empty:
                new_data.to_parquet(self.output_path, index=False)
                logger.info(f"Created new file: {len(new_data)} records")
            else:
                # Remove duplicates (same date + sector)
                existing = existing[~existing['date'].isin(new_data['date'].unique())]

                # Append new data
                combined = pd.concat([existing, new_data], ignore_index=True)
                combined = combined.sort_values(['date', 'sector_code'])

                combined.to_parquet(self.output_path, index=False)
                logger.info(f"Updated data: {len(existing)} → {len(combined)} records (+{len(new_data)})")

    def print_summary(self, comparison: pd.DataFrame):
        """Print summary of valuation changes."""
        print()
        print("=" * 100)
        print(f"SECTOR VALUATION UPDATE SUMMARY - {comparison['date'].iloc[0].date()}")
        print("=" * 100)
        print()

        # Sort by PE change
        comparison_sorted = comparison.sort_values('pe_change_pct', ascending=False)

        print(f"{'Sector':<30} {'PE':>8} {'ΔPE':>8} {'PB':>8} {'ΔPB':>8} {'Mkt Cap(T)':>12} {'ΔCap%':>8}")
        print("-" * 100)

        for idx, row in comparison_sorted.iterrows():
            pe_change = f"{row['pe_change_pct']:+.1f}%" if not pd.isna(row.get('pe_change_pct')) else "N/A"
            pb_change = f"{row['pb_change_pct']:+.1f}%" if not pd.isna(row.get('pb_change_pct')) else "N/A"
            cap_change = f"{row['mktcap_change_pct']:+.1f}%" if not pd.isna(row.get('mktcap_change_pct')) else "N/A"

            print(f"{row['sector_code']:<30} "
                  f"{row['sector_pe']:>8.2f} "
                  f"{pe_change:>8} "
                  f"{row['sector_pb']:>8.2f} "
                  f"{pb_change:>8} "
                  f"{row['sector_market_cap']/1e12:>12.2f} "
                  f"{cap_change:>8}")

        print()
        print("=" * 100)

        # Key statistics
        if 'pe_change_pct' in comparison.columns:
            avg_pe_change = comparison['pe_change_pct'].mean()
            avg_pb_change = comparison['pb_change_pct'].mean()
            avg_cap_change = comparison['mktcap_change_pct'].mean()

            print(f"Average Changes: PE {avg_pe_change:+.2f}%, PB {avg_pb_change:+.2f}%, Market Cap {avg_cap_change:+.2f}%")
            print("=" * 100)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Daily Sector Valuation Update')
    parser.add_argument(
        '--date',
        type=str,
        default=None,
        help='Target date (YYYY-MM-DD). Default: latest trading date'
    )
    parser.add_argument(
        '--compare-days',
        type=int,
        default=1,
        help='Number of days back to compare (default: 1 = previous trading day)'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results (dry run)'
    )

    args = parser.parse_args()

    # Initialize updater
    updater = DailySectorValuationUpdater()

    # Calculate for target date
    new_data = updater.calculate_daily_valuation(target_date=args.date)

    if new_data.empty:
        logger.error("No data calculated")
        return

    # Load existing data for comparison
    existing = updater.load_existing_data()

    # Find comparison date
    if not existing.empty:
        target_date = new_data['date'].iloc[0]
        available_dates = sorted(existing['date'].unique(), reverse=True)

        # Find Nth previous trading day
        comparison_date = None
        if len(available_dates) >= args.compare_days:
            comparison_date = available_dates[args.compare_days - 1]

        if comparison_date:
            comparison = updater.compare_with_previous(new_data, existing, comparison_date)
            updater.print_summary(comparison)
        else:
            logger.warning(f"Not enough historical data for {args.compare_days}-day comparison")

    # Save results
    if not args.no_save:
        updater.update_and_save(new_data, mode='append')
        logger.info("✅ Update complete!")
    else:
        logger.info("Dry run - no data saved")


if __name__ == '__main__':
    main()
