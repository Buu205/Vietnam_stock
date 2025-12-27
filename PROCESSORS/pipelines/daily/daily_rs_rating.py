#!/usr/bin/env python3
"""
Daily RS Rating Update Pipeline
================================

Calculates and updates IBD-style RS Rating for all stocks.

This pipeline:
1. Loads OHLCV data from basic_data.parquet
2. Calculates RS Rating (1-99 percentile rank)
3. Saves to stock_rs_rating_daily.parquet

Output:
    DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet

Usage:
    python3 PROCESSORS/pipelines/daily/daily_rs_rating.py
    python3 PROCESSORS/pipelines/daily/daily_rs_rating.py --verify

Author: Claude Code
Date: 2025-12-25
"""

import sys
from pathlib import Path
import logging
from datetime import datetime
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_rs_rating_update(verify_only: bool = False):
    """
    Run RS Rating calculation pipeline.

    Args:
        verify_only: If True, only verify existing data without recalculating
    """
    logger.info("=" * 60)
    logger.info("DAILY RS RATING UPDATE PIPELINE")
    logger.info("=" * 60)

    start_time = datetime.now()

    try:
        from PROCESSORS.technical.indicators.rs_rating import (
            RSRatingCalculator,
            get_latest_rs_rating,
            get_top_rs_stocks,
            OUTPUT_DIR
        )

        output_path = OUTPUT_DIR / "stock_rs_rating_daily.parquet"

        if verify_only:
            logger.info("\n📋 Verification Mode - Checking existing data...")

            if output_path.exists():
                import pandas as pd
                df = pd.read_parquet(output_path)
                latest_date = pd.to_datetime(df['date']).max()

                logger.info(f"  File: {output_path}")
                logger.info(f"  Records: {len(df):,}")
                logger.info(f"  Symbols: {df['symbol'].nunique()}")
                logger.info(f"  Latest Date: {latest_date.strftime('%Y-%m-%d')}")
                logger.info(f"  File Size: {output_path.stat().st_size / 1024:.1f} KB")

                # Show RS Rating distribution
                latest = df[df['date'] == latest_date]
                logger.info(f"\n📊 RS Rating Distribution (Latest):")
                logger.info(f"  80-99 (Strong): {len(latest[latest['rs_rating'] >= 80])}")
                logger.info(f"  50-79 (Medium): {len(latest[(latest['rs_rating'] >= 50) & (latest['rs_rating'] < 80)])}")
                logger.info(f"  20-49 (Weak):   {len(latest[(latest['rs_rating'] >= 20) & (latest['rs_rating'] < 50)])}")
                logger.info(f"  1-19 (V.Weak):  {len(latest[latest['rs_rating'] < 20])}")

                # Top 5
                top5 = latest.nlargest(5, 'rs_rating')
                logger.info(f"\n🔝 Top 5 by RS Rating:")
                for _, row in top5.iterrows():
                    logger.info(f"  {row['symbol']}: {row['rs_rating']} (score: {row['rs_score']:.1f})")

                logger.info("\n✅ Verification complete")
            else:
                logger.warning(f"\n❌ RS Rating file not found: {output_path}")
                logger.info("  Run without --verify to calculate RS Rating")

            return True

        # Full calculation
        logger.info("\n[1/3] Loading OHLCV data...")
        calculator = RSRatingCalculator()

        logger.info("\n[2/3] Calculating RS Rating...")
        output_path = calculator.run_and_save()

        logger.info("\n[3/3] Verifying output...")
        latest = get_latest_rs_rating()

        if latest is not None:
            logger.info(f"\n📊 Results Summary:")
            logger.info(f"  Total Stocks: {len(latest)}")
            logger.info(f"  Latest Date: {latest['date'].iloc[0].strftime('%Y-%m-%d')}")

            # Distribution
            logger.info(f"\n  RS Rating Distribution:")
            logger.info(f"    80-99 (Strong): {len(latest[latest['rs_rating'] >= 80])}")
            logger.info(f"    50-79 (Medium): {len(latest[(latest['rs_rating'] >= 50) & (latest['rs_rating'] < 80)])}")
            logger.info(f"    20-49 (Weak):   {len(latest[(latest['rs_rating'] >= 20) & (latest['rs_rating'] < 50)])}")
            logger.info(f"    1-19 (V.Weak):  {len(latest[latest['rs_rating'] < 20])}")

            # Top 10
            top10 = get_top_rs_stocks(10)
            logger.info(f"\n🔝 Top 10 by RS Rating:")
            for _, row in top10.iterrows():
                sector = row.get('sector_code', '-')
                logger.info(f"  {row['symbol']:<6} | RS: {row['rs_rating']:>2} | Score: {row['rs_score']:>6.1f} | Sector: {sector}")

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"\n⏱️  Processing time: {elapsed:.1f}s")
            logger.info(f"📁 Output: {output_path}")
            logger.info("\n✅ RS RATING UPDATE COMPLETE")

            return True
        else:
            logger.error("\n❌ Failed to verify output")
            return False

    except FileNotFoundError as e:
        logger.error(f"\n❌ Required data file not found: {e}")
        logger.info("  Make sure to run daily_ta_complete.py first to generate basic_data.parquet")
        return False

    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Daily RS Rating Update')
    parser.add_argument('--verify', action='store_true',
                       help='Only verify existing data without recalculating')
    args = parser.parse_args()

    success = run_rs_rating_update(verify_only=args.verify)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
