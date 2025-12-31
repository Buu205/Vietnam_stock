#!/usr/bin/env python3
"""
RS Rating Calculator (IBD-style)
=================================

Calculates Relative Strength Rating (1-99) for all stocks.
Based on IBD's proven methodology for identifying market leaders.

Formula:
    RS Score = 0.4×ret_3m + 0.2×ret_6m + 0.2×ret_9m + 0.2×ret_12m
    RS Rating = Percentile rank of RS Score (1-99)

Output:
    DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet

Author: Claude Code
Date: 2025-12-25
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Constants
PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "DATA" / "processed" / "technical" / "rs_rating"

# Return periods (trading days)
PERIOD_3M = 63
PERIOD_6M = 126
PERIOD_9M = 189
PERIOD_12M = 252

# Weights (IBD-style: recent performance weighted more)
WEIGHTS = {
    '3m': 0.4,
    '6m': 0.2,
    '9m': 0.2,
    '12m': 0.2
}


def calculate_rs_rating(
    ohlcv_df: pd.DataFrame,
    sector_map: Optional[dict] = None
) -> pd.DataFrame:
    """
    Calculate IBD-style RS Rating for all stocks.

    Args:
        ohlcv_df: OHLCV data with columns [symbol, date, close]
        sector_map: Optional mapping symbol -> sector_code

    Returns:
        DataFrame with [symbol, date, sector_code, rs_rating, rs_score,
                       ret_3m, ret_6m, ret_9m, ret_12m]
    """
    logger.info("Calculating RS Rating...")

    df = ohlcv_df.copy()

    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])

    # Sort by symbol and date
    df = df.sort_values(['symbol', 'date']).reset_index(drop=True)

    # Calculate returns for different periods
    logger.info("  Calculating multi-period returns...")
    df['ret_3m'] = df.groupby('symbol')['close'].pct_change(PERIOD_3M) * 100
    df['ret_6m'] = df.groupby('symbol')['close'].pct_change(PERIOD_6M) * 100
    df['ret_9m'] = df.groupby('symbol')['close'].pct_change(PERIOD_9M) * 100
    df['ret_12m'] = df.groupby('symbol')['close'].pct_change(PERIOD_12M) * 100

    # IBD-style weighted score
    logger.info("  Computing weighted RS Score...")
    df['rs_score'] = (
        WEIGHTS['3m'] * df['ret_3m'].fillna(0) +
        WEIGHTS['6m'] * df['ret_6m'].fillna(0) +
        WEIGHTS['9m'] * df['ret_9m'].fillna(0) +
        WEIGHTS['12m'] * df['ret_12m'].fillna(0)
    )

    # Percentile rank within each date (1-99)
    logger.info("  Computing percentile ranks...")
    df['rs_rating'] = df.groupby('date')['rs_score'].transform(
        lambda x: (x.rank(pct=True) * 98 + 1).round().astype(int)
    )

    # Clip to valid range
    df['rs_rating'] = df['rs_rating'].clip(1, 99)

    # Add sector mapping if provided
    if sector_map:
        df['sector_code'] = df['symbol'].map(sector_map)
    elif 'sector_code' not in df.columns:
        df['sector_code'] = None

    # Select output columns
    output_cols = [
        'symbol', 'date', 'sector_code',
        'rs_rating', 'rs_score',
        'ret_3m', 'ret_6m', 'ret_9m', 'ret_12m'
    ]

    result = df[[c for c in output_cols if c in df.columns]].copy()

    # Drop rows where RS rating couldn't be calculated (not enough history)
    result = result.dropna(subset=['rs_rating'])

    logger.info(f"  Calculated RS Rating for {result['symbol'].nunique()} stocks, "
                f"{result['date'].nunique()} dates")

    return result


def get_sector_mapping() -> dict:
    """Get symbol -> sector_code mapping from registry."""
    try:
        from config.registries import SectorRegistry
        registry = SectorRegistry()
        return registry.get_all_ticker_sectors()
    except ImportError:
        logger.warning("SectorRegistry not available, sector_code will be None")
        return {}


def save_rs_rating(df: pd.DataFrame, filename: str = "stock_rs_rating_daily.parquet"):
    """Save RS Rating to parquet file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filename
    df.to_parquet(output_path, index=False)
    logger.info(f"  Saved RS Rating to {output_path}")
    return output_path


def load_rs_rating(days: Optional[int] = None) -> Optional[pd.DataFrame]:
    """
    Load RS Rating data.

    Args:
        days: If provided, filter to last N days

    Returns:
        DataFrame or None if file doesn't exist
    """
    path = OUTPUT_DIR / "stock_rs_rating_daily.parquet"
    if not path.exists():
        return None

    df = pd.read_parquet(path)
    df['date'] = pd.to_datetime(df['date'])

    if days:
        cutoff = df['date'].max() - pd.Timedelta(days=days)
        df = df[df['date'] >= cutoff]

    return df


def get_latest_rs_rating() -> Optional[pd.DataFrame]:
    """
    Get latest RS Rating for all stocks.

    Returns:
        DataFrame with latest RS Rating per stock, sorted by rs_rating desc
    """
    df = load_rs_rating()
    if df is None:
        return None

    latest_date = df['date'].max()
    latest = df[df['date'] == latest_date].copy()
    latest = latest.sort_values('rs_rating', ascending=False)

    return latest


def get_top_rs_stocks(n: int = 50, sector: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Get top N stocks by RS Rating.

    Args:
        n: Number of stocks to return
        sector: Optional sector filter

    Returns:
        DataFrame with top N stocks
    """
    latest = get_latest_rs_rating()
    if latest is None:
        return None

    if sector and 'sector_code' in latest.columns:
        latest = latest[latest['sector_code'] == sector]

    return latest.head(n)


def get_rs_rating_history(symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
    """
    Get RS Rating history for a specific stock.

    Args:
        symbol: Stock ticker
        days: Number of days of history

    Returns:
        DataFrame with RS Rating history
    """
    df = load_rs_rating(days=days)
    if df is None:
        return None

    return df[df['symbol'] == symbol].sort_values('date')


class RSRatingCalculator:
    """
    Class-based interface for RS Rating calculation.
    Implements TAIndicator pattern for consistency.
    """

    def __init__(self, ohlcv_path: str = None):
        """
        Initialize RS Rating Calculator.

        Args:
            ohlcv_path: Path to OHLCV data (default: basic_data.parquet)
        """
        if ohlcv_path:
            self.ohlcv_path = Path(ohlcv_path)
        else:
            self.ohlcv_path = PROJECT_ROOT / "DATA" / "processed" / "technical" / "basic_data.parquet"

    @property
    def name(self) -> str:
        return "RS Rating (IBD-style)"

    def calculate(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Calculate RS Rating.

        Args:
            df: Optional OHLCV DataFrame. If None, loads from default path.

        Returns:
            DataFrame with RS Rating
        """
        if df is None:
            if not self.ohlcv_path.exists():
                raise FileNotFoundError(f"OHLCV data not found: {self.ohlcv_path}")
            df = pd.read_parquet(self.ohlcv_path)

        sector_map = get_sector_mapping()
        return calculate_rs_rating(df, sector_map)

    def run_and_save(self) -> Path:
        """Calculate RS Rating and save to file."""
        df = self.calculate()
        return save_rs_rating(df)

    def get_latest(self) -> Optional[pd.DataFrame]:
        """Get latest RS Rating for all stocks."""
        return get_latest_rs_rating()

    def save_history_30d(self) -> Optional[Path]:
        """
        Save last 30 days of RS Rating history for dashboard heatmap.
        Output: rs_rating_history_30d.parquet

        Used by Technical Dashboard Tab 3: Stock Scanner.
        """
        df = load_rs_rating(days=30)
        if df is None:
            logger.warning("No RS Rating data to export for 30d history")
            return None

        # Select only essential columns for heatmap
        cols = ['symbol', 'date', 'sector_code', 'rs_rating', 'rs_score']
        df = df[[c for c in cols if c in df.columns]].copy()

        # Save
        output_path = OUTPUT_DIR / "rs_rating_history_30d.parquet"
        df.to_parquet(output_path, index=False)
        logger.info(f"  Saved 30d RS Rating history to {output_path}")
        logger.info(f"  {df['symbol'].nunique()} symbols, {df['date'].nunique()} days")

        return output_path


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    calc = RSRatingCalculator()
    try:
        output_path = calc.run_and_save()
        print(f"\n✅ RS Rating saved to: {output_path}")

        # Show top 10
        top10 = get_top_rs_stocks(10)
        if top10 is not None:
            print("\nTop 10 by RS Rating:")
            print(top10[['symbol', 'rs_rating', 'rs_score']].to_string(index=False))
    except Exception as e:
        print(f"❌ Error: {e}")
