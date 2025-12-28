#!/usr/bin/env python3
"""
Sector Breadth Analyzer
========================

Calculate % stocks above various MAs for each sector.
Helps identify sector strength and rotation opportunities.

Metrics per sector:
- % stocks above MA20/50/100/200
- Advancing vs Declining stocks
- New highs vs New lows
- Sector trend classification

Author: Claude Code
Date: 2025-12-15
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging

# Add project root
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from config.registries import SectorRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SectorBreadthAnalyzer:
    """Calculate breadth metrics for each sector."""

    def __init__(self, technical_data_path: str = "DATA/processed/technical/basic_data.parquet"):
        """
        Initialize analyzer.

        Args:
            technical_data_path: Path to technical indicators data
        """
        self.technical_data_path = Path(technical_data_path)
        self.sector_reg = SectorRegistry()

        if not self.technical_data_path.exists():
            raise FileNotFoundError(f"Technical data not found: {self.technical_data_path}")

    def calculate_sector_breadth(self, date: str = None) -> pd.DataFrame:
        """
        Calculate breadth metrics for all sectors.

        Args:
            date: Target date (default: latest)

        Returns:
            DataFrame with sector breadth metrics
        """
        logger.info(f"Calculating sector breadth...")

        # Load technical data
        df = pd.read_parquet(self.technical_data_path)

        if date is None:
            date = df['date'].max()

        # Filter to date
        day_df = df[df['date'] == date].copy()

        if len(day_df) == 0:
            logger.warning(f"No data for date {date}")
            return pd.DataFrame()

        # Add sector information
        day_df['sector_code'] = day_df['symbol'].apply(self._get_sector)

        # Remove unknown sectors
        day_df = day_df[day_df['sector_code'] != 'UNKNOWN']

        # Calculate breadth for each sector
        sector_breadth_list = []

        for sector_code in day_df['sector_code'].unique():
            sector_df = day_df[day_df['sector_code'] == sector_code].copy()
            breadth = self._calculate_breadth_for_sector(sector_df, sector_code, date)
            if breadth:
                sector_breadth_list.append(breadth)

        if not sector_breadth_list:
            logger.warning("No sector breadth data calculated")
            return pd.DataFrame()

        result = pd.DataFrame(sector_breadth_list)

        # Sort by strength score
        result = result.sort_values('strength_score', ascending=False).reset_index(drop=True)

        logger.info(f"✅ Calculated breadth for {len(result)} sectors")
        return result

    def _calculate_breadth_for_sector(self, sector_df: pd.DataFrame, sector_code: str, date) -> dict:
        """Calculate breadth metrics for one sector."""
        total_stocks = len(sector_df)

        if total_stocks == 0:
            return None

        # MA breadth (handle NaN values)
        above_ma20 = (sector_df['close'] > sector_df['sma_20']).sum()
        above_ma50 = (sector_df['close'] > sector_df['sma_50']).sum()
        above_ma100 = (sector_df['close'] > sector_df['sma_100']).sum()
        above_ma200 = (sector_df['close'] > sector_df['sma_200']).sum()

        # Percentages
        pct_above_ma20 = (above_ma20 / total_stocks) * 100
        pct_above_ma50 = (above_ma50 / total_stocks) * 100
        pct_above_ma100 = (above_ma100 / total_stocks) * 100
        pct_above_ma200 = (above_ma200 / total_stocks) * 100

        # Advance/Decline
        advancing = (sector_df['close'] > sector_df['open']).sum()
        declining = (sector_df['close'] < sector_df['open']).sum()
        unchanged = (sector_df['close'] == sector_df['open']).sum()

        ad_ratio = advancing / declining if declining > 0 else 0

        # Trend strength (based on MA50)
        if pct_above_ma50 >= 70:
            sector_trend = 'STRONG_BULLISH'
        elif pct_above_ma50 >= 55:
            sector_trend = 'BULLISH'
        elif pct_above_ma50 >= 45:
            sector_trend = 'NEUTRAL'
        elif pct_above_ma50 >= 30:
            sector_trend = 'BEARISH'
        else:
            sector_trend = 'STRONG_BEARISH'

        # Strength score (0-100)
        strength_score = (
            pct_above_ma20 * 0.20 +
            pct_above_ma50 * 0.30 +
            pct_above_ma100 * 0.25 +
            pct_above_ma200 * 0.25
        )

        # RSI breadth
        bullish_rsi = ((sector_df['rsi_14'] >= 50) & (sector_df['rsi_14'] < 70)).sum()
        bearish_rsi = ((sector_df['rsi_14'] < 50) & (sector_df['rsi_14'] > 30)).sum()
        overbought = (sector_df['rsi_14'] >= 70).sum()
        oversold = (sector_df['rsi_14'] <= 30).sum()

        return {
            'date': date,
            'sector_code': sector_code,
            'total_stocks': int(total_stocks),
            'above_ma20': int(above_ma20),
            'above_ma50': int(above_ma50),
            'above_ma100': int(above_ma100),
            'above_ma200': int(above_ma200),
            'pct_above_ma20': round(pct_above_ma20, 2),
            'pct_above_ma50': round(pct_above_ma50, 2),
            'pct_above_ma100': round(pct_above_ma100, 2),
            'pct_above_ma200': round(pct_above_ma200, 2),
            'advancing': int(advancing),
            'declining': int(declining),
            'unchanged': int(unchanged),
            'ad_ratio': round(ad_ratio, 2),
            'bullish_rsi': int(bullish_rsi),
            'bearish_rsi': int(bearish_rsi),
            'overbought': int(overbought),
            'oversold': int(oversold),
            'sector_trend': sector_trend,
            'strength_score': round(strength_score, 2)
        }

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

    def save_sector_breadth(self, df: pd.DataFrame, output_path: str = "DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet"):
        """Save sector breadth (append mode)."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Normalize date to pd.Timestamp for consistent comparison
        df['date'] = pd.to_datetime(df['date'])
        target_date = df['date'].iloc[0]

        # Append or create
        if output_path.exists():
            existing = pd.read_parquet(output_path)
            # Normalize existing dates
            existing['date'] = pd.to_datetime(existing['date'])
            # Remove duplicate date
            existing = existing[existing['date'] != target_date]
            combined = pd.concat([existing, df], ignore_index=True)
            combined = combined.sort_values(['date', 'strength_score'], ascending=[True, False]).reset_index(drop=True)
            combined.to_parquet(output_path, index=False)
            logger.info(f"✅ Updated sector breadth (total: {len(combined)} records)")
        else:
            df.to_parquet(output_path, index=False)
            logger.info(f"✅ Created new sector breadth file")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Sector Breadth Analyzer')
    parser.add_argument('--date', type=str, default=None, help='Target date (YYYY-MM-DD)')

    args = parser.parse_args()

    try:
        analyzer = SectorBreadthAnalyzer()
        df = analyzer.calculate_sector_breadth(date=args.date)

        if not df.empty:
            analyzer.save_sector_breadth(df)

            # Print summary
            print("\n" + "=" * 120)
            print(f"SECTOR BREADTH ANALYSIS - {df['date'].iloc[0]}")
            print("=" * 120)
            print(df[['sector_code', 'total_stocks', 'pct_above_ma20', 'pct_above_ma50',
                      'pct_above_ma200', 'ad_ratio', 'sector_trend', 'strength_score']].to_string(index=False))
            print("=" * 120)

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
