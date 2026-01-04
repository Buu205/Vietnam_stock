#!/usr/bin/env python3
"""
RS Rating Calculator (Multi-Period)
====================================

Calculates Relative Strength Rating (1-99) for all stocks.
Provides individual RS Rating for each period: 1M, 3M, 6M, 9M, 12M.

Output Columns:
    - rs_1m, rs_3m, rs_6m, rs_9m, rs_12m: Individual period RS (1-99 percentile)
    - rs_rating: Combined weighted RS (backward compatible)
    - ret_1m, ret_3m, ret_6m, ret_9m, ret_12m: Raw returns (%)

Output:
    DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet

Author: Claude Code
Date: 2025-12-25
Updated: 2026-01-04 - Added individual period RS ratings
"""

import pandas as pd
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Constants
PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "DATA" / "processed" / "technical" / "rs_rating"

# Return periods (trading days)
PERIOD_1M = 21
PERIOD_3M = 63
PERIOD_6M = 126
PERIOD_9M = 189
PERIOD_12M = 252

# Weights for combined RS Score (Short-term focused)
# Total: 20% + 40% + 25% + 10% + 5% = 100%
WEIGHTS = {
    '1m': 0.20,   # 20% - Current momentum
    '3m': 0.40,   # 40% - Most important: medium-term trend
    '6m': 0.25,   # 25% - Extended trend
    '9m': 0.10,   # 10% - Historical context
    '12m': 0.05   # 5% - Long-term history
}

# Penalty factors for downtrend detection
# Applied to final raw_score to penalize stocks in TRUE downtrend (not noise/flat base)
PENALTY_1M = 0.85  # 15% penalty if 1M return < threshold
PENALTY_3M = 0.70  # 30% penalty if 3M return < threshold (broken trend = more severe)
# Combined penalty: 0.85 × 0.70 = 0.595 if both conditions met

# Tolerance thresholds - distinguish noise from real drops
# Stocks consolidating/flat base (e.g., -0.5% to -2%) won't be penalized
THRESHOLD_1M = -2.0   # 1M return must be < -2% to trigger penalty
THRESHOLD_3M = -2.0   # 3M return must be < -2% to trigger penalty

# Crash protection - "falling knife" detection
CRASH_THRESHOLD = -15.0  # If 1M drops > 15%, apply additional penalty
CRASH_PENALTY = 0.85     # Additional 15% penalty for crash


def calculate_rs_rating(
    ohlcv_df: pd.DataFrame,
    sector_map: Optional[dict] = None
) -> pd.DataFrame:
    """
    Calculate multi-period RS Rating for all stocks.

    Provides individual RS Rating for each period (1M, 3M, 6M, 9M, 12M)
    plus a combined weighted RS Rating for backward compatibility.

    Args:
        ohlcv_df: OHLCV data with columns [symbol, date, close]
        sector_map: Optional mapping symbol -> sector_code

    Returns:
        DataFrame with columns:
            - symbol, date, sector_code
            - rs_1m, rs_3m, rs_6m, rs_9m, rs_12m (individual period RS 1-99)
            - rs_rating, rs_score (combined weighted)
            - ret_1m, ret_3m, ret_6m, ret_9m, ret_12m (raw returns %)
    """
    logger.info("Calculating Multi-Period RS Rating...")

    df = ohlcv_df.copy()

    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])

    # Sort by symbol and date
    df = df.sort_values(['symbol', 'date']).reset_index(drop=True)

    # Calculate returns for all periods (including 1M)
    logger.info("  Calculating multi-period returns (1M, 3M, 6M, 9M, 12M)...")
    df['ret_1m'] = df.groupby('symbol')['close'].pct_change(PERIOD_1M) * 100
    df['ret_3m'] = df.groupby('symbol')['close'].pct_change(PERIOD_3M) * 100
    df['ret_6m'] = df.groupby('symbol')['close'].pct_change(PERIOD_6M) * 100
    df['ret_9m'] = df.groupby('symbol')['close'].pct_change(PERIOD_9M) * 100
    df['ret_12m'] = df.groupby('symbol')['close'].pct_change(PERIOD_12M) * 100

    # Individual RS Rating for each period (1-99 percentile rank)
    logger.info("  Computing individual period RS ratings...")
    for period in ['1m', '3m', '6m', '9m', '12m']:
        ret_col = f'ret_{period}'
        rs_col = f'rs_{period}'
        # Rank with na_option='keep' to handle NaN, then fillna and convert
        df[rs_col] = df.groupby('date')[ret_col].transform(
            lambda x: (x.rank(pct=True, na_option='keep') * 98 + 1).round()
        )
        # Fill NaN with 50 (neutral) and clip to 1-99
        df[rs_col] = df[rs_col].fillna(50).clip(1, 99).astype(int)

    # Combined weighted RS Score (using individual RS ratings, not returns)
    # This prevents extreme returns (e.g., +363%) from dominating the score
    logger.info("  Computing combined weighted RS Score with penalty...")

    # Step 1: Calculate raw weighted score using INDIVIDUAL RS RATINGS (1-99)
    # This normalizes all periods to same scale, preventing extreme values
    df['rs_score_raw'] = (
        WEIGHTS['1m'] * df['rs_1m'] +
        WEIGHTS['3m'] * df['rs_3m'] +
        WEIGHTS['6m'] * df['rs_6m'] +
        WEIGHTS['9m'] * df['rs_9m'] +
        WEIGHTS['12m'] * df['rs_12m']
    )

    # Step 2: Calculate rs_score (no penalty yet)
    df['rs_score'] = df['rs_score_raw']

    # Step 3: Calculate rs_rating_raw (percentile before penalty)
    df['rs_rating_raw'] = df.groupby('date')['rs_score'].transform(
        lambda x: (x.rank(pct=True) * 98 + 1).round().astype(int)
    )
    df['rs_rating_raw'] = df['rs_rating_raw'].clip(1, 99)

    # Step 4: Apply penalty for downtrend stocks
    # RE-ENABLED: 2026-01-04 after OHLCV data quality fix (all adjusted prices)
    df['penalty'] = 1.0  # Initialize with no penalty

    # Apply 1M penalty only if below tolerance threshold
    df.loc[df['ret_1m'] < THRESHOLD_1M, 'penalty'] *= PENALTY_1M

    # Apply 3M penalty only if below tolerance threshold
    df.loc[df['ret_3m'] < THRESHOLD_3M, 'penalty'] *= PENALTY_3M

    # Crash protection - "falling knife" detection
    df.loc[df['ret_1m'] < CRASH_THRESHOLD, 'penalty'] *= CRASH_PENALTY

    # Step 5: Final RS Rating = rs_rating_raw × penalty
    df['rs_rating'] = (df['rs_rating_raw'] * df['penalty']).round().clip(1, 99).astype(int)

    # Log penalty statistics
    penalized_count = (df['penalty'] < 1.0).sum()
    crash_count = (df['ret_1m'] < CRASH_THRESHOLD).sum()
    logger.info(f"  Penalty applied: {penalized_count} stocks penalized, {crash_count} crash warnings")

    # Add sector mapping if provided
    if sector_map:
        df['sector_code'] = df['symbol'].map(sector_map)
    elif 'sector_code' not in df.columns:
        df['sector_code'] = None

    # Select output columns (ordered for clarity)
    output_cols = [
        'symbol', 'date', 'sector_code',
        # Individual RS ratings
        'rs_1m', 'rs_3m', 'rs_6m', 'rs_9m', 'rs_12m',
        # Combined RS (with penalty applied to rs_rating)
        'rs_rating', 'rs_rating_raw', 'rs_score', 'penalty',
        # Raw returns
        'ret_1m', 'ret_3m', 'ret_6m', 'ret_9m', 'ret_12m'
    ]

    result = df[[c for c in output_cols if c in df.columns]].copy()

    # Drop rows where RS rating couldn't be calculated (not enough history)
    result = result.dropna(subset=['rs_rating'])

    logger.info(f"  Calculated RS Rating for {result['symbol'].nunique()} stocks, "
                f"{result['date'].nunique()} dates")
    logger.info(f"  Output columns: rs_1m, rs_3m, rs_6m, rs_9m, rs_12m + rs_rating (combined)")

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
        Includes individual period RS ratings (rs_1m, rs_3m, rs_6m, rs_9m, rs_12m).
        """
        df = load_rs_rating(days=30)
        if df is None:
            logger.warning("No RS Rating data to export for 30d history")
            return None

        # Select columns for heatmap (including individual period RS)
        cols = [
            'symbol', 'date', 'sector_code',
            'rs_1m', 'rs_3m', 'rs_6m', 'rs_9m', 'rs_12m',
            'rs_rating', 'rs_score'
        ]
        df = df[[c for c in cols if c in df.columns]].copy()

        # Save
        output_path = OUTPUT_DIR / "rs_rating_history_30d.parquet"
        df.to_parquet(output_path, index=False)
        logger.info(f"  Saved 30d RS Rating history to {output_path}")
        logger.info(f"  {df['symbol'].nunique()} symbols, {df['date'].nunique()} days")
        logger.info(f"  Columns: {', '.join(df.columns)}")

        return output_path


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    calc = RSRatingCalculator()
    try:
        output_path = calc.run_and_save()
        print(f"\n✅ RS Rating saved to: {output_path}")

        # Also save 30d history for dashboard
        calc.save_history_30d()

        # Show top 10 with individual period RS
        top10 = get_top_rs_stocks(10)
        if top10 is not None:
            print("\n" + "="*80)
            print("Top 10 by Combined RS Rating (with individual period RS):")
            print("="*80)
            display_cols = ['symbol', 'rs_1m', 'rs_3m', 'rs_6m', 'rs_9m', 'rs_12m', 'rs_rating']
            display_cols = [c for c in display_cols if c in top10.columns]
            print(top10[display_cols].to_string(index=False))

            print("\n" + "="*80)
            print("Example: CSV stock analysis")
            print("="*80)
            csv_data = top10[top10['symbol'] == 'CSV']
            if not csv_data.empty:
                for col in ['symbol', 'rs_1m', 'rs_3m', 'rs_6m', 'rs_9m', 'rs_12m', 'rs_rating',
                           'ret_1m', 'ret_3m', 'ret_6m', 'ret_9m', 'ret_12m']:
                    if col in csv_data.columns:
                        val = csv_data[col].values[0]
                        if 'ret_' in col:
                            print(f"  {col}: {val:+.2f}%")
                        else:
                            print(f"  {col}: {val}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
