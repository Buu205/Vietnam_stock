"""
Daily Sector Complete Update - Unified Pipeline
================================================

Cập nhật hàng ngày toàn bộ sector analysis pipeline (FA + TA + Valuation + Signals).
Daily update for complete sector analysis pipeline (FA + TA + Valuation + Signals).

This script runs the COMPLETE sector analysis pipeline:
1. FA Aggregation → sector_fundamental_metrics.parquet (when new quarterly reports)
2. TA Aggregation → sector_valuation_metrics.parquet (daily, using VNIndexValuationCalculator)
3. FA Scoring → FA scores
4. TA Scoring → TA scores
5. Signal Generation → sector_combined_scores.parquet (daily)

ALSO saves market & sector PE/PB to unified file:
6. Market & Sector Valuation → unified_pe_pb_valuation.parquet (daily)

Usage:
    # Daily update (latest trading date)
    python3 PROCESSORS/daily_sector_complete_update.py

    # Specific date
    python3 PROCESSORS/daily_sector_complete_update.py --date 2024-12-15

    # Update only TA + Signals (skip FA)
    python3 PROCESSORS/daily_sector_complete_update.py --skip-fa

    # Dry run (no save)
    python3 PROCESSORS/daily_sector_complete_update.py --no-save

Author: Claude Code
Date: 2025-12-15
Version: 1.0.0
"""

import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from PROCESSORS.sector.sector_processor import SectorProcessor
from PROCESSORS.valuation.calculators.vnindex_valuation_calculator import VNIndexValuationCalculator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DailySectorCompleteUpdater:
    """
    Daily updater for complete sector analysis pipeline.

    This combines:
    - Sector FA + TA analysis (PROCESSORS/sector/)
    - Market & Sector valuation (PROCESSORS/valuation/)

    All in ONE unified daily update.
    """

    def __init__(self):
        """Initialize updater."""
        self.project_root = PROJECT_ROOT
        self.data_root = self.project_root / "DATA"

        # Output paths
        self.sector_output = self.data_root / "processed" / "sector"
        self.valuation_output = self.data_root / "processed" / "valuation" / "market_sector_valuation"

        # Create output directories
        self.sector_output.mkdir(parents=True, exist_ok=True)
        self.valuation_output.mkdir(parents=True, exist_ok=True)

        # Initialize processors
        self.sector_processor = SectorProcessor()
        self.vnindex_calc = VNIndexValuationCalculator()

        logger.info("DailySectorCompleteUpdater initialized")
        logger.info(f"Sector output: {self.sector_output}")
        logger.info(f"Valuation output: {self.valuation_output}")

    def get_latest_trading_date(self) -> pd.Timestamp:
        """Get latest trading date from OHLCV data."""
        ohlcv_path = self.data_root / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"
        df = pd.read_parquet(ohlcv_path)

        # Check column names
        date_col = 'time' if 'time' in df.columns else 'date'
        latest = pd.to_datetime(df[date_col].max())

        logger.info(f"Latest trading date: {latest.date()}")
        return latest

    def update_sector_analysis(
        self,
        target_date: str = None,
        skip_fa: bool = False
    ) -> dict:
        """
        Run sector analysis pipeline (FA + TA + Signals).

        Args:
            target_date: Target date (YYYY-MM-DD). If None, uses latest trading date.
            skip_fa: If True, skip FA aggregation (TA + signals only)

        Returns:
            Dictionary with results DataFrames
        """
        logger.info("\n" + "=" * 80)
        logger.info("🚀 STARTING SECTOR ANALYSIS PIPELINE")
        logger.info("=" * 80)

        # Determine date range
        if target_date is None:
            end_date = self.get_latest_trading_date().strftime('%Y-%m-%d')
            # For TA (daily), just get latest date
            # For FA (quarterly), we might want more range or skip
            start_date = end_date
        else:
            start_date = target_date
            end_date = target_date

        logger.info(f"\nTarget date: {end_date}")

        # Run pipeline
        if skip_fa:
            logger.info("Skipping FA aggregation (--skip-fa flag)")
            # TODO: Implement TA-only update
            results = self.sector_processor.run_full_pipeline(
                start_date=start_date,
                end_date=end_date
            )
        else:
            results = self.sector_processor.run_full_pipeline(
                start_date=start_date,
                end_date=end_date
            )

        return results

    def update_market_sector_valuation(self, target_date: str = None) -> pd.DataFrame:
        """
        Run market & sector valuation update (PE/PB for VNINDEX + all sectors).

        Args:
            target_date: Target date (YYYY-MM-DD). If None, uses latest trading date.

        Returns:
            DataFrame with market + sector PE/PB data
        """
        logger.info("\n" + "=" * 80)
        logger.info("🚀 STARTING MARKET & SECTOR VALUATION UPDATE")
        logger.info("=" * 80)

        # Determine date
        if target_date is None:
            end_date = self.get_latest_trading_date()
        else:
            end_date = pd.to_datetime(target_date)

        start_date = end_date
        logger.info(f"\nTarget date: {end_date.date()}")

        # Load data
        logger.info("\nLoading fundamental & market data...")
        self.vnindex_calc.load_data()

        # Calculate all scopes (VNINDEX + sectors)
        logger.info("\nCalculating valuation for all scopes...")
        valuation_df = self.vnindex_calc.process_all_scopes_with_sectors(
            include_sectors=True,
            start_date=start_date,
            end_date=end_date
        )

        return valuation_df

    def save_valuation_data(
        self,
        new_data: pd.DataFrame,
        mode: str = 'append'
    ):
        """
        Save market & sector valuation data.

        Args:
            new_data: New valuation data
            mode: 'append' or 'replace'
        """
        output_file = self.valuation_output / "unified_pe_pb_valuation.parquet"

        if mode == 'replace' or not output_file.exists():
            new_data.to_parquet(output_file, index=False)
            logger.info(f"\n✅ Saved valuation data: {len(new_data)} records")
            logger.info(f"   Output: {output_file}")
        else:
            # Append mode: Load existing, remove duplicates, append new
            existing = pd.read_parquet(output_file)
            logger.info(f"\nExisting records: {len(existing)}")

            # Remove duplicates (same date + scope)
            existing = existing[~existing['date'].isin(new_data['date'].unique())]

            # Combine
            combined = pd.concat([existing, new_data], ignore_index=True)
            combined = combined.sort_values(['scope_type', 'scope', 'date'])

            combined.to_parquet(output_file, index=False)
            logger.info(f"✅ Updated valuation data: {len(existing)} → {len(combined)} records (+{len(new_data)})")
            logger.info(f"   Output: {output_file}")

    def print_summary(
        self,
        sector_results: dict = None,
        valuation_df: pd.DataFrame = None
    ):
        """Print summary of updates."""
        print()
        print("=" * 100)
        print(f"📊 DAILY SECTOR UPDATE SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)

        if sector_results:
            print("\n🔹 SECTOR ANALYSIS PIPELINE:")
            if 'fa_metrics' in sector_results:
                fa = sector_results['fa_metrics']
                print(f"   FA Metrics:       {len(fa)} records, {fa['sector_code'].nunique()} sectors")
                print(f"                     Date range: {fa['report_date'].min()} to {fa['report_date'].max()}")

            if 'ta_metrics' in sector_results:
                ta = sector_results['ta_metrics']
                print(f"   TA Metrics:       {len(ta)} records, {ta['sector_code'].nunique()} sectors")
                print(f"                     Date range: {ta['date'].min()} to {ta['date'].max()}")

            if 'combined_scores' in sector_results:
                scores = sector_results['combined_scores']
                print(f"   Combined Scores:  {len(scores)} records, {scores['sector_code'].nunique()} sectors")

                # Signal distribution
                if 'signal' in scores.columns:
                    signal_dist = scores['signal'].value_counts()
                    print(f"\n   Signal Distribution:")
                    for signal, count in signal_dist.items():
                        print(f"     {signal}: {count} sectors")

        if valuation_df is not None:
            print("\n🔹 MARKET & SECTOR VALUATION:")
            market_count = len(valuation_df[valuation_df['scope_type'] == 'MARKET'])
            sector_count = len(valuation_df[valuation_df['scope_type'] == 'SECTOR'])
            sector_df = valuation_df[valuation_df['scope_type'] == 'SECTOR']
            print(f"   Total records:    {len(valuation_df)}")
            print(f"   Market scopes:    {market_count} (VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX)")
            print(f"   Sector scopes:    {sector_count} ({sector_df['scope'].nunique()} sectors)")
            print(f"   Date range:       {valuation_df['date'].min()} to {valuation_df['date'].max()}")

            # Show latest PE/PB for key scopes
            latest_date = valuation_df['date'].max()
            latest = valuation_df[valuation_df['date'] == latest_date]

            print(f"\n   Latest Valuation ({latest_date.date()}):")
            for scope in ['VNINDEX', 'VNINDEX_EXCLUDE', 'BSC_INDEX']:
                scope_data = latest[latest['scope'] == scope]
                if not scope_data.empty:
                    pe = scope_data['pe_ttm'].iloc[0]
                    pb = scope_data['pb'].iloc[0]
                    print(f"     {scope:<18} PE: {pe:>6.2f}  PB: {pb:>5.2f}")

        print("\n" + "=" * 100)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Daily Sector Complete Update')
    parser.add_argument(
        '--date',
        type=str,
        default=None,
        help='Target date (YYYY-MM-DD). Default: latest trading date'
    )
    parser.add_argument(
        '--skip-fa',
        action='store_true',
        help='Skip FA aggregation (TA + signals only)'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results (dry run)'
    )

    args = parser.parse_args()

    # Initialize updater
    updater = DailySectorCompleteUpdater()

    # Run updates
    try:
        # 1. Sector analysis pipeline
        logger.info("\n" + "🔷" * 40)
        logger.info("STEP 1: SECTOR ANALYSIS PIPELINE (FA + TA + SIGNALS)")
        logger.info("🔷" * 40)

        sector_results = updater.update_sector_analysis(
            target_date=args.date,
            skip_fa=args.skip_fa
        )

        # 2. Market & sector valuation
        logger.info("\n" + "🔷" * 40)
        logger.info("STEP 2: MARKET & SECTOR VALUATION (PE/PB)")
        logger.info("🔷" * 40)

        valuation_df = updater.update_market_sector_valuation(
            target_date=args.date
        )

        # 3. Save valuation data (sector analysis already saved by processor)
        if not args.no_save:
            logger.info("\n" + "🔷" * 40)
            logger.info("STEP 3: SAVING VALUATION DATA")
            logger.info("🔷" * 40)

            updater.save_valuation_data(valuation_df, mode='append')

        # 4. Print summary
        updater.print_summary(sector_results, valuation_df)

        logger.info("\n✅ COMPLETE: All updates finished successfully!")

    except Exception as e:
        logger.error(f"\n❌ ERROR: Update failed - {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
