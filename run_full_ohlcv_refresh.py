#!/usr/bin/env python3
"""
Full OHLCV Refresh Script
=========================
Refresh all symbols from vnstock_data API to get adjusted OHLCV prices.
"""

import pandas as pd
import logging
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from PROCESSORS.technical.ohlcv.ohlcv_adjustment_detector import OHLCVAdjustmentDetector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ohlcv_full_refresh.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    # Load all symbols and sort by liquidity (average trading value)
    ohlcv_path = Path("DATA/raw/ohlcv/OHLCV_mktcap.parquet")
    df = pd.read_parquet(ohlcv_path)

    # Calculate average trading value per symbol (last 30 days)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['symbol', 'date'])
    recent_df = df.groupby('symbol').tail(30)
    avg_value = recent_df.groupby('symbol')['trading_value'].mean().sort_values(ascending=False)

    # Sort symbols by liquidity (highest first)
    symbols = avg_value.index.tolist()
    logger.info(f"Top 10 by liquidity: {symbols[:10]}")
    logger.info(f"Bottom 10 by liquidity: {symbols[-10:]}")

    logger.info(f"Starting FULL OHLCV refresh for {len(symbols)} symbols")
    logger.info(f"This will fetch complete history from vnstock_data API")
    logger.info(f"Estimated time: 1-2 hours")

    # Initialize detector
    detector = OHLCVAdjustmentDetector()

    # Force refresh all symbols
    logger.info("=" * 60)
    logger.info("PHASE 1: Refreshing all symbols from API")
    logger.info("=" * 60)

    # Use refresh_symbols() which properly saves at the end
    logger.info("Using detector.refresh_symbols() method...")
    results = detector.refresh_symbols(symbols, dry_run=False)

    success_count = results['success']
    failed_symbols = results['symbols_failed']

    logger.info("=" * 60)
    logger.info(f"PHASE 1 COMPLETE: {success_count}/{len(symbols)} symbols refreshed")
    if failed_symbols:
        logger.warning(f"Failed symbols: {failed_symbols}")
    logger.info("=" * 60)

    # Run selective cascade for technical indicators
    logger.info("PHASE 2: Running selective cascade for technical indicators")
    logger.info("=" * 60)

    try:
        detector._cascade_refresh_selective(symbols)
        logger.info("PHASE 2 COMPLETE: Technical indicators updated")
    except Exception as e:
        logger.error(f"Cascade refresh failed: {e}")

    logger.info("=" * 60)
    logger.info("FULL REFRESH COMPLETE!")
    logger.info(f"Success: {success_count} symbols")
    logger.info(f"Failed: {len(failed_symbols)} symbols")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
