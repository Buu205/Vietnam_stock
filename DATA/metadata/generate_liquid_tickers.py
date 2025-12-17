#!/usr/bin/env python3
"""
Generate Liquid Tickers List
============================
Creates a JSON file with tickers filtered by liquidity (avg trading value > threshold).

Usage:
    python generate_liquid_tickers.py [--min-value 2.0] [--days 20]

Output:
    DATA/metadata/liquid_tickers.json
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

# Path Setup
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Paths
DATA_DIR = PROJECT_ROOT / "DATA"
OHLCV_FILE = DATA_DIR / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"
OUTPUT_DIR = DATA_DIR / "metadata"
OUTPUT_FILE = OUTPUT_DIR / "liquid_tickers.json"

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LiquidTickers")


def load_ohlcv_data() -> pd.DataFrame:
    """Load OHLCV data with trading value."""
    if not OHLCV_FILE.exists():
        logger.error(f"OHLCV file not found: {OHLCV_FILE}")
        return pd.DataFrame()

    df = pd.read_parquet(OHLCV_FILE)
    df['date'] = pd.to_datetime(df['date'])

    # Normalize column name: symbol -> ticker
    if 'symbol' in df.columns and 'ticker' not in df.columns:
        df = df.rename(columns={'symbol': 'ticker'})

    # Calculate trading value if not present
    if 'trading_value' not in df.columns:
        if 'volume' in df.columns and 'close' in df.columns:
            df['trading_value'] = df['volume'] * df['close']
        else:
            logger.error("Cannot calculate trading_value: missing volume or close columns")
            return pd.DataFrame()

    return df


def load_entity_mapping() -> dict:
    """Load ticker to entity type mapping from sector registry."""
    try:
        from config.registries import SectorRegistry
        registry = SectorRegistry()

        mapping = {}
        for ticker in registry.get_all_tickers():
            info = registry.get_ticker(ticker)
            if info:
                entity_type = info.get('entity_type', 'COMPANY')
                mapping[ticker] = entity_type.upper()

        return mapping
    except Exception as e:
        logger.warning(f"Could not load SectorRegistry: {e}")
        return {}


def calculate_avg_trading_value(df: pd.DataFrame, days: int = 20) -> pd.DataFrame:
    """Calculate average trading value for last N days per ticker."""
    # Get latest N days of data
    latest_date = df['date'].max()
    cutoff_date = latest_date - pd.Timedelta(days=days)

    recent_df = df[df['date'] > cutoff_date].copy()

    # Calculate average trading value per ticker
    avg_values = recent_df.groupby('ticker').agg({
        'trading_value': 'mean',
        'date': 'count'  # Number of trading days
    }).reset_index()

    avg_values.columns = ['ticker', 'avg_trading_value', 'trading_days']

    # Convert to billions VND
    avg_values['avg_trading_value_billion'] = avg_values['avg_trading_value'] / 1e9

    return avg_values


def filter_liquid_tickers(avg_values: pd.DataFrame, min_value_billion: float = 2.0) -> pd.DataFrame:
    """Filter tickers by minimum average trading value (in billions VND)."""
    return avg_values[avg_values['avg_trading_value_billion'] >= min_value_billion].copy()


def group_by_entity_type(liquid_df: pd.DataFrame, entity_mapping: dict) -> dict:
    """Group liquid tickers by entity type."""
    grouped = {
        'BANK': [],
        'COMPANY': [],
        'SECURITY': [],
        'INSURANCE': []
    }

    for ticker in liquid_df['ticker'].tolist():
        entity_type = entity_mapping.get(ticker, 'COMPANY')
        if entity_type in grouped:
            grouped[entity_type].append(ticker)
        else:
            grouped['COMPANY'].append(ticker)

    # Sort each list
    for key in grouped:
        grouped[key] = sorted(grouped[key])

    return grouped


def main():
    parser = argparse.ArgumentParser(description="Generate liquid tickers list")
    parser.add_argument('--min-value', type=float, default=2.0,
                        help='Minimum avg trading value in billion VND (default: 2.0)')
    parser.add_argument('--days', type=int, default=20,
                        help='Number of trading days to average (default: 20)')
    args = parser.parse_args()

    logger.info(f"Starting liquid tickers generation (min: {args.min_value}B VND, days: {args.days})")

    # 1. Load OHLCV data
    df = load_ohlcv_data()
    if df.empty:
        logger.error("No OHLCV data loaded. Exiting.")
        return

    logger.info(f"Loaded {len(df):,} OHLCV records, {df['ticker'].nunique()} tickers")

    # 2. Load entity mapping
    entity_mapping = load_entity_mapping()
    logger.info(f"Loaded entity mapping for {len(entity_mapping)} tickers")

    # 3. Calculate average trading value
    avg_values = calculate_avg_trading_value(df, args.days)
    logger.info(f"Calculated avg trading value for {len(avg_values)} tickers")

    # 4. Filter by liquidity threshold
    liquid_df = filter_liquid_tickers(avg_values, args.min_value)
    logger.info(f"Found {len(liquid_df)} tickers with avg trading value >= {args.min_value}B VND")

    # 5. Group by entity type
    grouped = group_by_entity_type(liquid_df, entity_mapping)

    # 6. Create output JSON
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "min_trading_value_billion": args.min_value,
        "averaging_days": args.days,
        "total_liquid_tickers": len(liquid_df),
        "tickers": grouped,
        "summary": {
            "BANK": len(grouped['BANK']),
            "COMPANY": len(grouped['COMPANY']),
            "SECURITY": len(grouped['SECURITY']),
            "INSURANCE": len(grouped['INSURANCE'])
        }
    }

    # 7. Save to file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved to {OUTPUT_FILE}")

    # Print summary
    print("\n" + "=" * 50)
    print("LIQUID TICKERS SUMMARY")
    print("=" * 50)
    print(f"Min Trading Value: {args.min_value}B VND/day")
    print(f"Averaging Period: {args.days} trading days")
    print(f"Total Liquid Tickers: {len(liquid_df)}")
    print("-" * 50)
    for entity_type, tickers in grouped.items():
        print(f"{entity_type}: {len(tickers)} tickers")
        if tickers:
            print(f"  Top 5: {', '.join(tickers[:5])}")
    print("=" * 50)


if __name__ == "__main__":
    main()
