"""
Technical Data Retention Helper
===============================

Rolling window retention for technical analysis data.
Automatically cleans up old data to keep file sizes small for Streamlit dashboard.

ONLY for processed technical data:
- market_breadth
- sector_breadth
- alerts
- vnindex_indicators
- money_flow
- rs_rating

Raw OHLCV data is NOT affected - kept indefinitely for backtesting.

Usage:
    from PROCESSORS.core.shared.technical_data_retention import save_technical_data

    save_technical_data(df, output_path, data_type='market_breadth')

Author: Claude Code
Date: 2025-12-25
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)

# Retention periods for technical data (trading days)
TECHNICAL_RETENTION_DAYS = {
    'market_breadth': 365,      # 1 year - for trend analysis
    'sector_breadth': 365,      # 1 year - for RRG rotation
    'vnindex_indicators': 365,  # 1 year - for regime detection
    'money_flow': 180,          # 6 months - recent flow matters
    'alerts': 90,               # 3 months - only recent signals
    'rs_rating': 365,           # 1 year - for RS ranking
    'patterns': 90,             # 3 months - candlestick patterns
}

# Default retention if data_type not specified
DEFAULT_RETENTION_DAYS = 365


def save_technical_data(
    df: pd.DataFrame,
    output_path: Union[str, Path],
    data_type: str,
    date_column: str = 'date',
    dedup_columns: Optional[list] = None
) -> int:
    """
    Save technical data with rolling retention window.

    Args:
        df: DataFrame to save
        output_path: Path to parquet file
        data_type: Type of data (market_breadth, alerts, etc.)
        date_column: Name of date column for filtering
        dedup_columns: Columns for deduplication (default: [date_column])

    Returns:
        Number of rows saved

    Example:
        save_technical_data(
            breadth_df,
            'DATA/processed/technical/market_breadth/daily.parquet',
            data_type='market_breadth'
        )
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get retention period
    retention_days = TECHNICAL_RETENTION_DAYS.get(data_type, DEFAULT_RETENTION_DAYS)
    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=retention_days)

    # Ensure date column is datetime
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])

    # Dedup columns
    if dedup_columns is None:
        dedup_columns = [date_column]

    # Merge with existing data
    if output_path.exists():
        try:
            existing = pd.read_parquet(output_path)
            existing[date_column] = pd.to_datetime(existing[date_column])

            # Combine and deduplicate
            combined = pd.concat([existing, df], ignore_index=True)
            combined = combined.drop_duplicates(subset=dedup_columns, keep='last')
        except Exception as e:
            logger.warning(f"Could not read existing file, creating new: {e}")
            combined = df
    else:
        combined = df

    # Apply retention window - remove data older than cutoff
    before_count = len(combined)
    combined = combined[combined[date_column] >= cutoff_date]
    after_count = len(combined)

    if before_count > after_count:
        logger.info(f"Retention cleanup: removed {before_count - after_count} old rows")

    # Sort and save
    combined = combined.sort_values(date_column).reset_index(drop=True)
    combined.to_parquet(output_path, index=False)

    logger.info(f"Saved {len(combined)} rows to {output_path.name} (retention: {retention_days} days)")

    return len(combined)


def get_retention_days(data_type: str) -> int:
    """Get retention period for a data type."""
    return TECHNICAL_RETENTION_DAYS.get(data_type, DEFAULT_RETENTION_DAYS)


def cleanup_old_technical_data(
    output_path: Union[str, Path],
    data_type: str,
    date_column: str = 'date'
) -> int:
    """
    Cleanup old data from existing parquet file.

    Args:
        output_path: Path to parquet file
        data_type: Type of data for retention lookup
        date_column: Name of date column

    Returns:
        Number of rows removed
    """
    output_path = Path(output_path)
    if not output_path.exists():
        return 0

    retention_days = TECHNICAL_RETENTION_DAYS.get(data_type, DEFAULT_RETENTION_DAYS)
    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=retention_days)

    df = pd.read_parquet(output_path)
    df[date_column] = pd.to_datetime(df[date_column])

    before_count = len(df)
    df = df[df[date_column] >= cutoff_date]
    after_count = len(df)

    removed = before_count - after_count
    if removed > 0:
        df.to_parquet(output_path, index=False)
        logger.info(f"Cleaned up {removed} old rows from {output_path.name}")

    return removed
