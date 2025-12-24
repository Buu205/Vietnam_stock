#!/usr/bin/env python3
"""
OHLCV Adjustment Detector
=========================
Auto-detect dividend/split adjustments by comparing stored OHLCV with fresh API data.
When adjustment detected (median price diff > threshold), refresh full history.

Usage:
    # Detect only (report which symbols need refresh)
    python ohlcv_adjustment_detector.py --detect

    # Detect and refresh flagged symbols
    python ohlcv_adjustment_detector.py --detect --refresh

    # RECOMMENDED: Detect, refresh, selective cascade (10x faster)
    python ohlcv_adjustment_detector.py --detect --refresh --cascade-selective

    # Legacy: Detect, refresh, full cascade (all 458 symbols)
    python ohlcv_adjustment_detector.py --detect --refresh --cascade

    # Force refresh specific symbols with selective cascade
    python ohlcv_adjustment_detector.py --symbols CTG,HDB --refresh --cascade-selective

    # Dry run (show what would be refreshed)
    python ohlcv_adjustment_detector.py --detect --refresh --dry-run
"""

import pandas as pd
import numpy as np
import logging
import argparse
import time
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import warnings
import sys

warnings.filterwarnings('ignore')

# Add project root to path for CLI usage
_this_file = Path(__file__).resolve()
_project_root = _this_file.parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Import from existing updater
from PROCESSORS.core.config.paths import PROJECT_ROOT, RAW_OHLCV
from PROCESSORS.technical.ohlcv.ohlcv_daily_updater import OHLCVDailyUpdater

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ohlcv_adjustment_detector.log')
    ]
)
logger = logging.getLogger(__name__)


class OHLCVAdjustmentDetector:
    """
    Detect and refresh OHLCV data when corporate actions (dividends/splits) occur.

    Algorithm:
    1. For each symbol, fetch 30 recent days from API
    2. Compare with stored parquet data
    3. If median_diff > threshold (2%) for 10+ days → flag for refresh
    4. Refresh: delete old data → fetch full history → recalculate metrics
    """

    # Detection parameters
    THRESHOLD_PCT = 2.0          # Median diff threshold (%)
    MIN_DAYS_WITH_DIFF = 10      # Minimum days with significant diff
    CHECK_WINDOW_DAYS = 35       # Days to fetch for comparison
    HISTORY_START_DATE = "2015-01-01"  # Full history start

    def __init__(self, parquet_path: Optional[Path] = None):
        """
        Initialize detector.

        Args:
            parquet_path: Path to OHLCV parquet file (default: DATA/raw/ohlcv/OHLCV_mktcap.parquet)
        """
        self.parquet_path = parquet_path or (RAW_OHLCV / "OHLCV_mktcap.parquet")
        self.backup_path = self.parquet_path.with_suffix('.parquet.bak')

        # Load existing data
        self.existing_df = self._load_existing_data()

        # Initialize updater for API calls
        self.updater = OHLCVDailyUpdater()

        logger.info(f"Initialized detector with {len(self.existing_df)} records")
        logger.info(f"Threshold: {self.THRESHOLD_PCT}%, Min days: {self.MIN_DAYS_WITH_DIFF}")

    def _load_existing_data(self) -> pd.DataFrame:
        """Load existing OHLCV data from parquet."""
        if not self.parquet_path.exists():
            logger.error(f"Parquet file not found: {self.parquet_path}")
            return pd.DataFrame()

        df = pd.read_parquet(self.parquet_path)
        df['date'] = pd.to_datetime(df['date'])
        return df

    def _fetch_recent_data(self, symbol: str, days: int = 35) -> pd.DataFrame:
        """
        Fetch recent OHLCV data from API for comparison.

        Args:
            symbol: Stock symbol
            days: Number of days to fetch

        Returns:
            DataFrame with date, close columns (close in VND)
        """
        try:
            from vnstock_data import Quote

            end_date = date.today()
            start_date = end_date - timedelta(days=days + 10)  # Extra buffer for weekends

            quote = Quote(symbol=symbol, source='vnd')
            df = quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            if df.empty:
                return pd.DataFrame()

            df['date'] = pd.to_datetime(df['time']).dt.normalize()
            df['close'] = df['close'] * 1000  # Convert to VND

            return df[['date', 'close']].copy()

        except Exception as e:
            logger.debug(f"Error fetching {symbol}: {e}")
            return pd.DataFrame()

    def detect_adjustment(self, symbol: str) -> Dict:
        """
        Detect if symbol needs adjustment refresh.

        Args:
            symbol: Stock symbol

        Returns:
            Dict with detection results:
            {
                'symbol': str,
                'needs_refresh': bool,
                'median_diff': float,
                'max_diff': float,
                'days_compared': int,
                'days_with_diff': int
            }
        """
        result = {
            'symbol': symbol,
            'needs_refresh': False,
            'median_diff': 0.0,
            'max_diff': 0.0,
            'days_compared': 0,
            'days_with_diff': 0,
            'error': None
        }

        try:
            # Fetch fresh data from API
            new_df = self._fetch_recent_data(symbol, self.CHECK_WINDOW_DAYS)
            if new_df.empty:
                result['error'] = 'No API data'
                return result

            # Get stored data for same period
            min_date = new_df['date'].min()
            max_date = new_df['date'].max()

            old_df = self.existing_df[
                (self.existing_df['symbol'] == symbol) &
                (self.existing_df['date'] >= min_date) &
                (self.existing_df['date'] <= max_date)
            ].copy()

            if old_df.empty or len(old_df) < 10:
                result['error'] = 'Insufficient stored data'
                return result

            # Merge and compare
            merged = old_df.merge(
                new_df[['date', 'close']],
                on='date',
                suffixes=('_old', '_new')
            )

            if len(merged) < 10:
                result['error'] = 'Insufficient matching dates'
                return result

            # Calculate diff
            merged['pct_diff'] = abs(merged['close_old'] - merged['close_new']) / merged['close_old'] * 100

            result['median_diff'] = float(merged['pct_diff'].median())
            result['max_diff'] = float(merged['pct_diff'].max())
            result['days_compared'] = len(merged)
            result['days_with_diff'] = int((merged['pct_diff'] > 1).sum())

            # Check if needs refresh
            result['needs_refresh'] = (
                result['median_diff'] > self.THRESHOLD_PCT and
                result['days_with_diff'] >= self.MIN_DAYS_WITH_DIFF
            )

        except Exception as e:
            result['error'] = str(e)
            logger.debug(f"Error detecting {symbol}: {e}")

        return result

    def detect_all(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Detect adjustments for all symbols.

        Args:
            symbols: List of symbols to check (default: all in parquet)

        Returns:
            DataFrame with detection results
        """
        if symbols is None:
            symbols = self.existing_df['symbol'].unique().tolist()

        logger.info(f"Starting detection for {len(symbols)} symbols...")

        results = []
        for i, symbol in enumerate(symbols):
            if (i + 1) % 50 == 0:
                logger.info(f"Progress: {i + 1}/{len(symbols)}...")

            result = self.detect_adjustment(symbol)
            results.append(result)

            time.sleep(0.05)  # Rate limit protection

        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('median_diff', ascending=False)

        # Summary
        needs_refresh = results_df['needs_refresh'].sum()
        logger.info(f"Detection complete: {needs_refresh}/{len(results)} symbols need refresh")

        return results_df

    def _backup_parquet(self):
        """Create backup of parquet before refresh."""
        if self.parquet_path.exists():
            shutil.copy2(self.parquet_path, self.backup_path)
            logger.info(f"Backup created: {self.backup_path}")

    def _fetch_full_history(self, symbol: str) -> pd.DataFrame:
        """
        Fetch full historical OHLCV for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            DataFrame with full OHLCV history
        """
        try:
            ohlcv_df = self.updater.get_ohlcv_data(
                symbol,
                self.HISTORY_START_DATE,
                date.today().strftime('%Y-%m-%d')
            )

            if ohlcv_df is not None and not ohlcv_df.empty:
                logger.info(f"Fetched {len(ohlcv_df)} records for {symbol}")
                return ohlcv_df

        except Exception as e:
            logger.error(f"Error fetching full history for {symbol}: {e}")

        return pd.DataFrame()

    def refresh_symbol(self, symbol: str) -> bool:
        """
        Refresh full history for a single symbol.

        Args:
            symbol: Stock symbol

        Returns:
            True if successful
        """
        try:
            # Fetch fresh full history
            new_data = self._fetch_full_history(symbol)
            if new_data.empty:
                logger.warning(f"No data fetched for {symbol}")
                return False

            # Calculate derived metrics
            new_data = self.updater.calculate_derived_metrics(new_data)

            # Remove old data for this symbol
            self.existing_df = self.existing_df[self.existing_df['symbol'] != symbol].copy()

            # Append new data
            self.existing_df = pd.concat([self.existing_df, new_data], ignore_index=True)

            logger.info(f"Refreshed {symbol}: {len(new_data)} records")
            return True

        except Exception as e:
            logger.error(f"Error refreshing {symbol}: {e}")
            return False

    def refresh_symbols(self, symbols: List[str], dry_run: bool = False) -> Dict:
        """
        Refresh multiple symbols.

        Args:
            symbols: List of symbols to refresh
            dry_run: If True, don't actually refresh

        Returns:
            Dict with refresh results
        """
        results = {
            'total': len(symbols),
            'success': 0,
            'failed': 0,
            'symbols_refreshed': [],
            'symbols_failed': []
        }

        if dry_run:
            logger.info(f"[DRY RUN] Would refresh {len(symbols)} symbols: {symbols[:10]}...")
            results['symbols_refreshed'] = symbols
            return results

        # Backup before refresh
        self._backup_parquet()

        for i, symbol in enumerate(symbols):
            logger.info(f"Refreshing {symbol} ({i + 1}/{len(symbols)})...")

            if self.refresh_symbol(symbol):
                results['success'] += 1
                results['symbols_refreshed'].append(symbol)
            else:
                results['failed'] += 1
                results['symbols_failed'].append(symbol)

            time.sleep(0.5)  # Rate limit for full history fetch

        # Save updated parquet
        if results['success'] > 0:
            self._save_parquet()

        logger.info(f"Refresh complete: {results['success']} success, {results['failed']} failed")
        return results

    def _save_parquet(self):
        """Save updated data to parquet."""
        self.existing_df['date'] = pd.to_datetime(self.existing_df['date']).dt.date
        self.existing_df = self.existing_df.sort_values(['symbol', 'date']).reset_index(drop=True)
        self.existing_df.to_parquet(self.parquet_path, index=False)
        logger.info(f"Saved {len(self.existing_df)} records to {self.parquet_path}")

    def _cascade_refresh_technical(self, n_sessions: int = 500):
        """
        Cascade refresh all technical indicators after OHLCV update.

        This ensures all derived data (MA, RSI, MACD, alerts, money flow, etc.)
        is recalculated from the updated OHLCV prices.
        """
        logger.info("=" * 60)
        logger.info("CASCADE REFRESH: Regenerating technical indicators...")
        logger.info("=" * 60)

        try:
            from PROCESSORS.pipelines.daily.daily_ta_complete import CompleteTAUpdatePipeline

            pipeline = CompleteTAUpdatePipeline()
            pipeline.run(n_sessions=n_sessions)

            logger.info("✅ Cascade refresh complete")

        except Exception as e:
            logger.error(f"❌ Cascade refresh failed: {e}")
            import traceback
            traceback.print_exc()

    def _cascade_refresh_selective(self, symbols: List[str], n_sessions: int = 500):
        """
        Selective cascade refresh for affected symbols only.

        Steps:
        1. Recalc technical indicators for symbols
        2. Recalc alerts for symbols
        3. Recalc money flow for symbols
        4. ALWAYS recalc market breadth (full - needs all symbols for %)

        Args:
            symbols: List of symbols to refresh
            n_sessions: Historical lookback sessions
        """
        logger.info("=" * 60)
        logger.info(f"SELECTIVE CASCADE REFRESH: {len(symbols)} symbols")
        logger.info(f"Symbols: {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")
        logger.info("=" * 60)

        try:
            from PROCESSORS.technical.indicators.technical_processor import TechnicalProcessor
            from PROCESSORS.technical.indicators.alert_detector import TechnicalAlertDetector
            from PROCESSORS.technical.indicators.money_flow import MoneyFlowAnalyzer

            # Step 1: Technical indicators (selective)
            logger.info("\n[1/4] Recalculating technical indicators...")
            processor = TechnicalProcessor()
            tech_df = processor.calculate_selective_indicators(symbols, n_sessions)
            if not tech_df.empty:
                processor.atomic_merge_basic_data(tech_df, symbols)
                logger.info(f"  ✅ Merged {len(symbols)} symbols into basic_data.parquet")

            # Step 2: Alerts (selective)
            logger.info("\n[2/4] Recalculating alerts...")
            detector = TechnicalAlertDetector()
            alerts = detector.detect_all_alerts(n_sessions=n_sessions, symbols=symbols)
            detector.merge_alerts_selective(alerts, symbols)
            logger.info(f"  ✅ Merged alerts for {len(symbols)} symbols")

            # Step 3: Money flow (selective)
            logger.info("\n[3/4] Recalculating money flow...")
            mf_analyzer = MoneyFlowAnalyzer()
            mf_df = mf_analyzer.calculate_all_money_flow(n_sessions=n_sessions, symbols=symbols)
            if not mf_df.empty:
                mf_analyzer.atomic_merge_money_flow(mf_df, symbols)
                logger.info(f"  ✅ Merged money flow for {len(symbols)} symbols")

            # Step 4: Market breadth (always full - needs all symbols for %)
            logger.info("\n[4/4] Recalculating market breadth (full)...")
            self._recalc_market_breadth()

            # Step 5: Create cache invalidation marker for BSC MCP
            self._create_cache_invalidation_marker()

            logger.info("\n✅ SELECTIVE CASCADE REFRESH COMPLETE")

        except Exception as e:
            logger.error(f"❌ Selective cascade failed: {e}")
            import traceback
            traceback.print_exc()

    def _recalc_market_breadth(self):
        """Always full recalc - needs all symbols for % calculations."""
        try:
            from PROCESSORS.technical.indicators.sector_breadth import SectorBreadthAnalyzer

            breadth = SectorBreadthAnalyzer()
            df = breadth.calculate_sector_breadth(date=date.today())
            if not df.empty:
                breadth.save_sector_breadth(df)
                logger.info("  ✅ Market breadth recalculated")
        except Exception as e:
            logger.warning(f"  ⚠️ Market breadth recalc failed: {e}")

    def _create_cache_invalidation_marker(self):
        """
        Create cache invalidation marker for BSC MCP.

        BSC MCP DataLoader checks for this marker and clears its cache
        when detected, ensuring fresh data is loaded after OHLCV refresh.
        """
        marker_path = Path("DATA/.cache_invalidated")
        try:
            marker_path.touch()
            logger.info("  ✅ Cache invalidation marker created for BSC MCP")
        except Exception as e:
            logger.warning(f"  ⚠️ Could not create cache marker: {e}")

    def run(
        self,
        detect: bool = True,
        refresh: bool = False,
        symbols: Optional[List[str]] = None,
        dry_run: bool = False,
        threshold: Optional[float] = None,
        cascade: bool = False,
        cascade_selective: bool = False
    ) -> Dict:
        """
        Run detection and/or refresh.

        Args:
            detect: Run detection phase
            refresh: Run refresh phase
            symbols: Specific symbols to process (overrides detection)
            dry_run: Don't actually refresh
            threshold: Override default threshold
            cascade: Run cascade refresh of technical indicators after OHLCV update (FULL - all 458 symbols)
            cascade_selective: Run selective cascade refresh (RECOMMENDED - only affected symbols)

        Returns:
            Dict with run results
        """
        if threshold:
            self.THRESHOLD_PCT = threshold

        results = {
            'detection': None,
            'refresh': None,
            'cascade': False,
            'cascade_mode': None
        }

        # Determine symbols to refresh
        refresh_symbols = []

        if symbols:
            # Force refresh specific symbols
            refresh_symbols = symbols
            logger.info(f"Force refresh mode: {len(symbols)} symbols")
        elif detect:
            # Run detection
            detection_df = self.detect_all()
            results['detection'] = detection_df

            # Get symbols needing refresh
            refresh_symbols = detection_df[detection_df['needs_refresh']]['symbol'].tolist()

            # Print summary
            print("\n" + "=" * 60)
            print(f"DETECTION RESULTS (threshold: {self.THRESHOLD_PCT}%)")
            print("=" * 60)
            print(f"Total symbols analyzed: {len(detection_df)}")
            print(f"Symbols needing refresh: {len(refresh_symbols)}")

            if len(refresh_symbols) > 0:
                print(f"\nTop symbols by median_diff:")
                top = detection_df[detection_df['needs_refresh']].head(20)
                for _, row in top.iterrows():
                    print(f"  {row['symbol']}: {row['median_diff']:.2f}%")

        # Run refresh if requested
        if refresh and refresh_symbols:
            print("\n" + "=" * 60)
            print(f"REFRESH {'(DRY RUN)' if dry_run else ''}")
            print("=" * 60)

            results['refresh'] = self.refresh_symbols(refresh_symbols, dry_run)

            print(f"Success: {results['refresh']['success']}")
            print(f"Failed: {results['refresh']['failed']}")

            # Cascade refresh if requested and OHLCV was actually updated
            if not dry_run and results['refresh']['success'] > 0:
                refreshed_symbols = results['refresh']['symbols_refreshed']

                if cascade_selective:
                    # Selective cascade (RECOMMENDED) - only affected symbols
                    self._cascade_refresh_selective(refreshed_symbols)
                    results['cascade'] = True
                    results['cascade_mode'] = 'selective'
                elif cascade:
                    # Full cascade (legacy) - all 458 symbols
                    self._cascade_refresh_technical()
                    results['cascade'] = True
                    results['cascade_mode'] = 'full'

        return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='OHLCV Adjustment Detector - Auto-detect and refresh dividend/split adjusted prices'
    )
    parser.add_argument('--detect', action='store_true', help='Run detection phase')
    parser.add_argument('--refresh', action='store_true', help='Run refresh phase')
    parser.add_argument('--symbols', type=str, help='Comma-separated symbols to force refresh')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without doing it')
    parser.add_argument('--threshold', type=float, default=2.0, help='Detection threshold %% (default: 2.0)')
    parser.add_argument('--cascade', action='store_true', help='Full cascade: refresh ALL technical indicators (slow, legacy)')
    parser.add_argument('--cascade-selective', action='store_true', help='Selective cascade: only refresh TA for affected symbols (RECOMMENDED, 10x faster)')
    parser.add_argument('--output', type=str, help='Save detection results to CSV')

    args = parser.parse_args()

    # Parse symbols if provided
    symbols = None
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(',')]

    # Must specify at least one action
    if not args.detect and not args.refresh:
        print("Error: Must specify --detect and/or --refresh")
        print("Use --help for usage information")
        return

    # Run detector
    detector = OHLCVAdjustmentDetector()
    results = detector.run(
        detect=args.detect,
        refresh=args.refresh,
        symbols=symbols,
        dry_run=args.dry_run,
        threshold=args.threshold,
        cascade=args.cascade,
        cascade_selective=args.cascade_selective
    )

    # Save detection results if requested
    if args.output and results['detection'] is not None:
        results['detection'].to_csv(args.output, index=False)
        print(f"\nDetection results saved to: {args.output}")


if __name__ == "__main__":
    main()
