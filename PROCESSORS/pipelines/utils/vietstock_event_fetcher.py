#!/usr/bin/env python3
"""
Vietstock Event Fetcher
Fetch corporate events (dividends, rights issues) and cache as parquet.

Run weekly (Sunday) to update event cache for next 60 days.

Usage:
    python3 PROCESSORS/pipelines/utils/vietstock_event_fetcher.py
    python3 PROCESSORS/pipelines/utils/vietstock_event_fetcher.py --days 90

Output:
    DATA/processed/events/vietstock_events.parquet
"""
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import logging
import json

# Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
OUTPUT_PATH = PROJECT_ROOT / "DATA" / "processed" / "events" / "vietstock_events.parquet"
TICKER_FILE = PROJECT_ROOT / "config" / "metadata" / "ticker_details.json"

# Vietstock API config
API_URL = "https://finance.vietstock.vn/data/eventstypedata"

# Note: These tokens may expire. Update from browser if API returns 401/403.
HEADERS = {
    'Accept': '*/*',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://finance.vietstock.vn',
    'Referer': 'https://finance.vietstock.vn/lich-su-kien.htm?page=1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': (
        '_cc_id=c46db549a0ec0e2f953a621a21d1434; language=vi-VN; Theme=Light; '
        'AnonymousNotification=; vst_usr_lg_token=/l4XWStttEmi1tcBi6BxnQ==; '
        'ASP.NET_SessionId=npo31zgvr3rempqidwjocogx; '
        '__RequestVerificationToken=6OP-kfj8zJri5OJuWIsZp9HDIXjnKEofhuGtxzboMz3YgrcrKveajEWK7TtxUb_-wqEFf6R6F87lSIjPm1l4c-47Y9fTwy9-BWXU5AcVQ8Q1'
    )
}

REQUEST_TOKEN = "YjrOqkfTp-7e3bSY_zKaCvJ2xErVx6tf7-uDTqf0xcMmhTBW2nPonZuJ5J-eBz4PnsSg3GPPrQzciXr1hnMs7U0V9g2f4DS_QOWj3Y6A8rs1"

# Event type mapping
EVENT_TYPES = {
    1: "DIVIDEND",      # Cổ tức (tiền mặt, cổ phiếu, thưởng)
    2: "AGM",           # Đại hội cổ đông
    3: "RIGHTS_ISSUE",  # Phát hành thêm
}


def parse_vietstock_date(date_str: str) -> str | None:
    """Convert /Date(timestamp)/ to YYYY-MM-DD."""
    if not date_str or '/Date(' not in date_str:
        return None
    try:
        timestamp = int(date_str.replace('/Date(', '').replace(')/', '')) / 1000
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    except:
        return None


def load_tracked_tickers() -> set[str]:
    """Load tickers from ticker_details.json."""
    if not TICKER_FILE.exists():
        logger.warning(f"Ticker file not found: {TICKER_FILE}")
        return set()

    with open(TICKER_FILE, 'r') as f:
        data = json.load(f)
    return set(data.keys())


def fetch_events(
    event_type_id: int = 1,
    from_date: str = None,
    to_date: str = None,
    page_size: int = 50
) -> list[dict]:
    """
    Fetch events from Vietstock API.

    Args:
        event_type_id: 1=Dividend, 2=AGM, 3=Rights Issue
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        page_size: Results per page

    Returns:
        List of event dicts
    """
    all_events = []
    page = 1

    while True:
        payload = (
            f"eventTypeID={event_type_id}&channelID=0&code=&catID=-1"
            f"&fDate={from_date}&tDate={to_date}"
            f"&page={page}&pageSize={page_size}"
            f"&orderBy=Date1&orderDir=ASC"
            f"&__RequestVerificationToken={REQUEST_TOKEN}"
        )

        try:
            response = requests.post(API_URL, headers=HEADERS, data=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list) or len(data) < 2:
                break

            events = data[0]
            if not events:
                break

            all_events.extend(events)

            # Check if more pages
            total_count = data[1][0] if data[1] else 0
            if len(all_events) >= total_count:
                break

            page += 1

        except Exception as e:
            logger.error(f"API error (type={event_type_id}, page={page}): {e}")
            break

    return all_events


def process_events(raw_events: list[dict], event_type: str) -> pd.DataFrame:
    """Process raw API events into clean DataFrame."""
    records = []

    for event in raw_events:
        record = {
            'ticker': event.get('Code', ''),
            'event_type': event_type,
            'event_subtype': event.get('Name', ''),
            'ex_date': parse_vietstock_date(event.get('GDKHQDate')),
            'record_date': parse_vietstock_date(event.get('NDKCCDate')),
            'payment_date': parse_vietstock_date(event.get('Time')),
            'note': event.get('Note', ''),
            'title': event.get('Title', ''),
            'exchange': event.get('Exchange', ''),
        }
        records.append(record)

    df = pd.DataFrame(records)

    # Filter out empty tickers
    df = df[df['ticker'].str.len() > 0]

    return df


def fetch_all_events(days_ahead: int = 60) -> pd.DataFrame:
    """
    Fetch all event types for next N days.

    Args:
        days_ahead: Number of days to look ahead

    Returns:
        Combined DataFrame of all events
    """
    from_date = datetime.now().strftime('%Y-%m-%d')
    to_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')

    logger.info(f"Fetching events from {from_date} to {to_date}")

    all_dfs = []

    for event_type_id, event_type in EVENT_TYPES.items():
        logger.info(f"  Fetching {event_type} events (type={event_type_id})...")
        raw_events = fetch_events(event_type_id, from_date, to_date)

        if raw_events:
            df = process_events(raw_events, event_type)
            all_dfs.append(df)
            logger.info(f"    → {len(df)} events")
        else:
            logger.info(f"    → 0 events")

    if not all_dfs:
        return pd.DataFrame()

    combined = pd.concat(all_dfs, ignore_index=True)

    # Add metadata
    combined['fetched_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return combined


def filter_tracked_tickers(events_df: pd.DataFrame) -> pd.DataFrame:
    """Filter events to only include tracked tickers."""
    tracked = load_tracked_tickers()

    if not tracked:
        logger.warning("No tracked tickers found, keeping all events")
        return events_df

    before = len(events_df)
    filtered = events_df[events_df['ticker'].isin(tracked)]
    after = len(filtered)

    logger.info(f"Filtered: {before} → {after} events (only tracked tickers)")

    return filtered


def save_events(df: pd.DataFrame) -> None:
    """Save events to parquet."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False, compression='snappy')

    size_kb = OUTPUT_PATH.stat().st_size / 1024
    logger.info(f"Saved: {OUTPUT_PATH.name} ({len(df)} events, {size_kb:.1f} KB)")


def print_summary(df: pd.DataFrame) -> None:
    """Print summary of fetched events."""
    if df.empty:
        print("\n❌ No events found")
        return

    print("\n" + "=" * 60)
    print("VIETSTOCK EVENTS CACHE - SUMMARY")
    print("=" * 60)

    # By event type
    print(f"\nBy Event Type:")
    for etype, count in df['event_type'].value_counts().items():
        print(f"  {etype}: {count}")

    # Upcoming ex-dates (next 7 days)
    today = datetime.now().strftime('%Y-%m-%d')
    next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    upcoming = df[(df['ex_date'] >= today) & (df['ex_date'] <= next_week)]

    if not upcoming.empty:
        print(f"\n📅 Upcoming GDKHQ (next 7 days): {len(upcoming)} events")
        for _, row in upcoming.head(10).iterrows():
            print(f"  {row['ex_date']} | {row['ticker']:<6} | {row['event_subtype'][:30]}")

    print("\n" + "=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Fetch Vietstock events')
    parser.add_argument('--days', type=int, default=60, help='Days ahead to fetch (default: 60)')
    parser.add_argument('--all', action='store_true', help='Include all tickers (not just tracked)')
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("VIETSTOCK EVENT FETCHER")
    print("=" * 60)

    # Fetch all events
    df = fetch_all_events(days_ahead=args.days)

    if df.empty:
        logger.warning("No events fetched!")
        return

    # Filter to tracked tickers only (unless --all)
    if not args.all:
        df = filter_tracked_tickers(df)

    # Save
    save_events(df)

    # Summary
    print_summary(df)

    print(f"\n✅ Event cache updated: {OUTPUT_PATH}")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
