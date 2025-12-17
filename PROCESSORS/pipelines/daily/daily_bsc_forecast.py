#!/usr/bin/env python3
"""
Daily BSC Forecast Update Pipeline
===================================

Updates BSC Forecast parquet files with latest market prices and calculated metrics.
Run this after OHLCV and Fundamental updates to ensure latest data.

Usage:
    python3 PROCESSORS/pipelines/daily_bsc_forecast.py

Output files:
    - DATA/processed/forecast/bsc/bsc_individual.parquet
    - DATA/processed/forecast/bsc/bsc_sector_valuation.parquet
    - DATA/processed/forecast/bsc/bsc_combined.parquet
    - DATA/processed/forecast/bsc/README.md

Updated: 2025-12-17
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent  # daily/pipelines/PROCESSORS is 3 levels deep
sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run BSC Forecast daily update."""
    logger.info("=" * 60)
    logger.info("BSC Forecast Daily Update - Starting")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Check if Excel file exists
    excel_path = PROJECT_ROOT / "DATA" / "processed" / "forecast" / "BSC Forecast.xlsx"
    if not excel_path.exists():
        logger.warning(f"BSC Forecast Excel not found: {excel_path}")
        logger.info("Skipping BSC Forecast update (no input file)")
        return 0

    try:
        from PROCESSORS.forecast.bsc_forecast_processor import BSCForecastProcessor

        processor = BSCForecastProcessor(PROJECT_ROOT)
        result = processor.run(generate_readme=True)

        # Print summary
        individual = result['individual']
        sector = result['sector']

        logger.info("")
        logger.info("=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Individual Stocks: {len(individual)}")
        logger.info(f"Sectors: {len(sector)}")
        logger.info("")

        # Rating distribution
        logger.info("Rating Distribution:")
        for rating, count in individual['rating'].value_counts().items():
            logger.info(f"  {rating}: {count}")

        logger.info("")
        logger.info("=" * 60)
        logger.info("BSC Forecast Daily Update - COMPLETE")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"BSC Forecast update failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
