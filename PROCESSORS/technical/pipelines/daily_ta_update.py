#!/usr/bin/env python3
"""
Daily Technical Analysis Update Pipeline
========================================

Daily update workflow:
1. Load latest 200 trading sessions from OHLCV
2. Calculate technical indicators using TA-Lib
3. Calculate market breadth
4. Save outputs

Usage:
    python3 PROCESSORS/technical/pipelines/daily_ta_update.py
    python3 PROCESSORS/technical/pipelines/daily_ta_update.py --sessions 200

Author: Claude Code
Date: 2025-12-15
"""

import sys
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime

# Add project root
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from PROCESSORS.technical.indicators.technical_processor import TechnicalProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarketBreadthCalculator:
    """Calculate market breadth metrics."""

    def calculate_breadth(self, df: pd.DataFrame, date: str = None) -> dict:
        """
        Calculate market breadth for specific date.

        Args:
            df: DataFrame with technical indicators
            date: Target date (default: latest)

        Returns:
            Breadth metrics dictionary
        """
        if date is None:
            date = df['date'].max()

        # Filter to specific date
        day_df = df[df['date'] == date].copy()

        if len(day_df) == 0:
            logger.warning(f"No data for date {date}")
            return None

        total_stocks = len(day_df)

        # MA breadth
        above_ma20 = (day_df['close'] > day_df['sma_20']).sum()
        above_ma50 = (day_df['close'] > day_df['sma_50']).sum()
        above_ma100 = (day_df['close'] > day_df['sma_100']).sum()
        above_ma200 = (day_df['close'] > day_df['sma_200']).sum()

        # Advance/Decline (need previous day)
        # For now, use price change
        advancing = (day_df['close'] > day_df['open']).sum()
        declining = (day_df['close'] < day_df['open']).sum()
        unchanged = (day_df['close'] == day_df['open']).sum()

        ad_ratio = advancing / declining if declining > 0 else 0

        # Market trend
        ma50_pct = (above_ma50 / total_stocks) * 100

        if ma50_pct > 60:
            market_trend = 'BULLISH'
        elif ma50_pct < 40:
            market_trend = 'BEARISH'
        else:
            market_trend = 'NEUTRAL'

        return {
            'date': date,
            'total_stocks': total_stocks,
            'above_ma20': int(above_ma20),
            'above_ma50': int(above_ma50),
            'above_ma100': int(above_ma100),
            'above_ma200': int(above_ma200),
            'above_ma20_pct': round((above_ma20 / total_stocks) * 100, 2),
            'above_ma50_pct': round(ma50_pct, 2),
            'above_ma100_pct': round((above_ma100 / total_stocks) * 100, 2),
            'above_ma200_pct': round((above_ma200 / total_stocks) * 100, 2),
            'advancing': int(advancing),
            'declining': int(declining),
            'unchanged': int(unchanged),
            'ad_ratio': round(ad_ratio, 2),
            'market_trend': market_trend
        }

    def save_breadth(self, breadth: dict, output_path: str = "DATA/processed/technical/market_breadth/market_breadth_daily.parquet"):
        """
        Save market breadth to file (append mode).

        Args:
            breadth: Breadth metrics dictionary
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to DataFrame
        new_row = pd.DataFrame([breadth])

        # Append or create
        if output_path.exists():
            existing = pd.read_parquet(output_path)

            # Remove duplicate date
            existing = existing[existing['date'] != breadth['date']]

            # Append
            combined = pd.concat([existing, new_row], ignore_index=True)
            combined = combined.sort_values('date').reset_index(drop=True)

            combined.to_parquet(output_path, index=False)
            logger.info(f"✅ Updated market breadth (total: {len(combined)} days)")
        else:
            new_row.to_parquet(output_path, index=False)
            logger.info(f"✅ Created new market breadth file")


def main():
    """Main pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description='Daily TA Update Pipeline')
    parser.add_argument('--sessions', type=int, default=200, help='Number of trading sessions')
    parser.add_argument('--date', type=str, default=None, help='Target date (YYYY-MM-DD)')

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("DAILY TECHNICAL ANALYSIS UPDATE")
    logger.info("=" * 80)

    try:
        # Step 1: Calculate technical indicators
        logger.info("\n[1/2] Calculating technical indicators...")
        processor = TechnicalProcessor()
        df = processor.run_full_processing(n_sessions=args.sessions)

        # Step 2: Calculate market breadth
        logger.info("\n[2/2] Calculating market breadth...")
        breadth_calc = MarketBreadthCalculator()

        target_date = args.date if args.date else df['date'].max()
        breadth = breadth_calc.calculate_breadth(df, target_date)

        if breadth:
            breadth_calc.save_breadth(breadth)

            # Print summary
            logger.info("\n" + "=" * 80)
            logger.info(f"MARKET BREADTH - {breadth['date']}")
            logger.info("=" * 80)
            logger.info(f"Total Stocks: {breadth['total_stocks']}")
            logger.info(f"Above MA20:   {breadth['above_ma20']} ({breadth['above_ma20_pct']}%)")
            logger.info(f"Above MA50:   {breadth['above_ma50']} ({breadth['above_ma50_pct']}%)")
            logger.info(f"Above MA100:  {breadth['above_ma100']} ({breadth['above_ma100_pct']}%)")
            logger.info(f"Above MA200:  {breadth['above_ma200']} ({breadth['above_ma200_pct']}%)")
            logger.info(f"AD Ratio:     {breadth['ad_ratio']:.2f} ({breadth['advancing']}↑ / {breadth['declining']}↓)")
            logger.info(f"Market Trend: {breadth['market_trend']}")
            logger.info("=" * 80)

        logger.info("\n✅ DAILY TA UPDATE COMPLETE")

    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
