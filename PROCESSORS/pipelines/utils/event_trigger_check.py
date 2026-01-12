#!/usr/bin/env python3
"""
Event Trigger Check
Check for tickers needing full OHLCV refresh on GDKHQ date.

Used by daily pipeline to detect corporate events that require data refresh.

Usage (standalone):
    python3 PROCESSORS/pipelines/utils/event_trigger_check.py
    python3 PROCESSORS/pipelines/utils/event_trigger_check.py --date 2026-01-15

Usage (import):
    from PROCESSORS.pipelines.utils.event_trigger_check import get_tickers_needing_refresh
    tickers = get_tickers_needing_refresh()
"""
import pandas as pd
from pathlib import Path
from datetime import datetime, date
import logging
import json

# Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
EVENTS_PATH = PROJECT_ROOT / "DATA" / "processed" / "events" / "vietstock_events.parquet"
TICKER_FILE = PROJECT_ROOT / "config" / "metadata" / "ticker_details.json"


def load_events_cache(target_date: date = None) -> pd.DataFrame | None:
    """Load cached events from parquet.

    Returns None if cache is missing or stale (doesn't cover target_date).
    """
    if target_date is None:
        target_date = date.today()

    if not EVENTS_PATH.exists():
        logger.warning(f"Events cache not found: {EVENTS_PATH}")
        return None

    df = pd.read_parquet(EVENTS_PATH)

    # Check cache freshness - must cover target_date
    if 'fetched_at' in df.columns:
        fetched = pd.to_datetime(df['fetched_at'].iloc[0]).date()
        # Cache is stale if fetched before target_date (won't have today's events)
        if fetched < target_date:
            logger.warning(f"Events cache stale (fetched {fetched}, need {target_date})")
            return None

    return df


def load_tracked_tickers() -> set[str]:
    """Load tracked tickers from config."""
    if not TICKER_FILE.exists():
        return set()

    with open(TICKER_FILE, 'r') as f:
        data = json.load(f)
    return set(data.keys())


def get_gdkhq_tickers(target_date: date = None) -> list[str]:
    """
    Get tickers with GDKHQ (ex-date) on target date.

    Args:
        target_date: Date to check (default: today)

    Returns:
        List of ticker symbols needing full OHLCV refresh
    """
    if target_date is None:
        target_date = date.today()

    target_str = target_date.strftime('%Y-%m-%d')

    # Load events cache (returns None if stale)
    events_df = load_events_cache(target_date)
    if events_df is None:
        return None  # Signal to caller: need to refresh cache

    # Filter by ex_date
    events_df['ex_date'] = pd.to_datetime(events_df['ex_date']).dt.date
    today_events = events_df[events_df['ex_date'] == target_date]

    if today_events.empty:
        logger.info(f"No GDKHQ events for {target_str}")
        return []

    # Get unique tickers
    tickers = today_events['ticker'].unique().tolist()

    # Filter to tracked tickers only
    tracked = load_tracked_tickers()
    if tracked:
        tickers = [t for t in tickers if t in tracked]

    if tickers:
        logger.info(f"Found {len(tickers)} tickers with GDKHQ on {target_str}: {tickers}")

        # Log event details
        for ticker in tickers:
            event = today_events[today_events['ticker'] == ticker].iloc[0]
            logger.info(f"  {ticker}: {event['event_subtype']} - {event['note'][:50]}...")

    return tickers


def get_tickers_needing_refresh(target_date: date = None) -> list[str] | None:
    """
    Main function: Get all tickers needing full OHLCV refresh.

    Currently checks:
    1. GDKHQ (ex-dividend/rights date) = target_date

    Future: Add fallback checks for shares/price anomalies.

    Args:
        target_date: Date to check (default: today)

    Returns:
        List of ticker symbols needing refresh, or None if cache is stale/missing
    """
    affected = set()

    # 1. GDKHQ-based triggers (primary)
    gdkhq_tickers = get_gdkhq_tickers(target_date)
    if gdkhq_tickers is None:
        return None  # Cache stale - signal caller to refresh
    affected.update(gdkhq_tickers)

    # 2. Future: Shares outstanding anomaly detection
    # shares_anomalies = detect_shares_changes(target_date)
    # affected.update(shares_anomalies)

    # 3. Future: Price anomaly detection (>8% move)
    # price_anomalies = detect_price_moves(target_date, threshold=0.08)
    # affected.update(price_anomalies)

    return list(affected)


def print_summary(tickers: list[str], target_date: date) -> None:
    """Print summary of tickers needing refresh."""
    print("\n" + "=" * 60)
    print(f"EVENT TRIGGER CHECK - {target_date.strftime('%Y-%m-%d')}")
    print("=" * 60)

    if not tickers:
        print("\n✅ No tickers need full OHLCV refresh today")
    else:
        print(f"\n🔄 {len(tickers)} ticker(s) need full OHLCV refresh:")
        for ticker in tickers:
            print(f"   • {ticker}")

    print("\n" + "=" * 60 + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Check for GDKHQ triggers')
    parser.add_argument('--date', type=str, help='Date to check (YYYY-MM-DD), default: today')
    args = parser.parse_args()

    # Parse date
    if args.date:
        target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
    else:
        target_date = date.today()

    # Get tickers
    tickers = get_tickers_needing_refresh(target_date)

    # Print summary
    print_summary(tickers, target_date)

    # Return exit code for scripting
    return 0 if not tickers else len(tickers)


if __name__ == '__main__':
    exit(main())
