#!/usr/bin/env python3
"""
Build Unified Forecast Parquet from Source JSONs.

Reads 4 normalized source JSONs (bsc, vci, hcm, ssi) and creates:
1. unified.parquet - All sources merged for comparison tab
2. Updates bsc/individual.parquet and bsc/sector.parquet

Usage:
    python build_unified.py
    python build_unified.py --sources bsc,vci  # Only specific sources

Schema (2026-2027 focus):
    symbol, sector, entity_type, source
    target_price, current_price, rating
    npatmi_2026f, npatmi_2027f
    eps_2026f, eps_2027f
    pe_2026f, pe_2027f
    updated_at
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# Load ticker metadata for canonical sector mapping
TICKER_METADATA_PATH = Path("/Users/buuphan/Dev/Vietnam_dashboard/config/metadata/ticker_details.json")
TICKER_METADATA = {}

if TICKER_METADATA_PATH.exists():
    with open(TICKER_METADATA_PATH, 'r', encoding='utf-8') as f:
        TICKER_METADATA = json.load(f)


def get_sector_from_metadata(symbol: str, fallback_sector: str = '') -> str:
    """Get canonical sector from ticker_details.json metadata.

    Args:
        symbol: Stock ticker symbol
        fallback_sector: Fallback sector if not found in metadata

    Returns:
        Vietnamese sector name from metadata, or fallback
    """
    if symbol in TICKER_METADATA:
        return TICKER_METADATA[symbol].get('sector', fallback_sector)
    return fallback_sector


def get_entity_from_metadata(symbol: str, fallback_entity: str = 'COMPANY') -> str:
    """Get entity type from ticker_details.json metadata."""
    if symbol in TICKER_METADATA:
        return TICKER_METADATA[symbol].get('entity', fallback_entity)
    return fallback_entity


# Paths
PROJECT_ROOT = Path("/Users/buuphan/Dev/Vietnam_dashboard")
SOURCES_DIR = PROJECT_ROOT / "DATA" / "processed" / "forecast" / "sources"
OUTPUT_DIR = PROJECT_ROOT / "DATA" / "processed" / "forecast"
BSC_DIR = OUTPUT_DIR / "bsc"

# All available sources
ALL_SOURCES = ['bsc', 'vci', 'hcm', 'ssi']


def load_source_json(source: str) -> list:
    """Load normalized JSON for a source."""
    json_path = SOURCES_DIR / f"{source}.json"
    if not json_path.exists():
        print(f"  ⚠️  {source}.json not found, skipping")
        return []

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stocks = data.get('stocks', [])
    # Add source field to each stock
    for stock in stocks:
        stock['source'] = source
        stock['source_updated_at'] = data.get('updated_at', '')

    print(f"  ✅ {source}: {len(stocks)} stocks")
    return stocks


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all required columns exist with proper types."""
    required_cols = {
        'symbol': str,
        'sector': str,
        'entity_type': str,
        'source': str,
        'target_price': float,
        'current_price': float,
        'rating': str,
        'npatmi_2026f': float,
        'npatmi_2027f': float,
        'eps_2026f': float,
        'eps_2027f': float,
        'pe_2026f': float,
        'pe_2027f': float,
        'source_updated_at': str,
    }

    for col, dtype in required_cols.items():
        if col not in df.columns:
            df[col] = None
        # Convert to appropriate type
        if dtype == float:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = df[col].astype(str).replace('nan', '').replace('None', '')

    return df


def calculate_comparison_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate comparison metrics between BSC and consensus.

    Output schema matches existing bsc_vs_consensus.parquet:
    - symbol, sector, entity_type, current_price, rating
    - bsc_tp, bsc_npatmi_26, bsc_npatmi_27
    - hcm_tp, ssi_tp, vci_tp
    - hcm_npatmi_26, ssi_npatmi_26, vci_npatmi_26
    - hcm_npatmi_27, ssi_npatmi_27, vci_npatmi_27
    - tp_cons_mean, tp_dev_pct, tp_spread_pct, tp_max_dev_src, tp_max_dev_pct
    - npatmi_26_cons_mean, npatmi_26_dev_pct, npatmi_26_spread_pct, ...
    - npatmi_27_cons_mean, npatmi_27_dev_pct, npatmi_27_spread_pct, ...
    - insight, source_count
    """
    comparison_rows = []

    for symbol, group in df.groupby('symbol'):
        row = {'symbol': symbol}

        # Get canonical sector and entity from metadata (single source of truth)
        row['sector'] = get_sector_from_metadata(symbol, '')
        row['entity_type'] = get_entity_from_metadata(symbol, 'COMPANY')

        # Get BSC data as reference
        bsc_data = group[group['source'] == 'bsc']
        if not bsc_data.empty:
            bsc = bsc_data.iloc[0]
            # Use metadata sector, fallback to BSC sector if not in metadata
            if not row['sector']:
                row['sector'] = bsc['sector'] or ''
            row['current_price'] = bsc['current_price']
            row['bsc_tp'] = bsc['target_price']
            row['bsc_npatmi_26'] = bsc['npatmi_2026f']
            row['bsc_npatmi_27'] = bsc['npatmi_2027f']
            row['rating'] = bsc['rating']
        else:
            # No BSC data, use first available for price only
            first = group.iloc[0]
            # Use metadata sector, fallback to source sector if not in metadata
            if not row['sector']:
                row['sector'] = first['sector'] or ''
            row['current_price'] = first['current_price']
            row['bsc_tp'] = None
            row['bsc_npatmi_26'] = None
            row['bsc_npatmi_27'] = None
            row['rating'] = None

        # Get consensus data (HCM, SSI, VCI)
        for src in ['hcm', 'ssi', 'vci']:
            src_data = group[group['source'] == src]
            if not src_data.empty:
                s = src_data.iloc[0]
                row[f'{src}_tp'] = s['target_price']
                row[f'{src}_npatmi_26'] = s['npatmi_2026f']
                row[f'{src}_npatmi_27'] = s['npatmi_2027f']
            else:
                row[f'{src}_tp'] = None
                row[f'{src}_npatmi_26'] = None
                row[f'{src}_npatmi_27'] = None

        # Calculate metrics for each type (tp, npatmi_26, npatmi_27)
        for metric_key, bsc_key in [('tp', 'bsc_tp'), ('npatmi_26', 'bsc_npatmi_26'), ('npatmi_27', 'bsc_npatmi_27')]:
            bsc_val = row.get(bsc_key)

            # Collect consensus values
            cons_vals = {}
            for src in ['hcm', 'ssi', 'vci']:
                val = row.get(f'{src}_{metric_key}')
                if pd.notna(val) and val > 0:
                    cons_vals[src] = val

            if cons_vals:
                cons_mean = np.mean(list(cons_vals.values()))
                row[f'{metric_key}_cons_mean'] = cons_mean

                # Deviation from BSC
                if bsc_val and bsc_val > 0:
                    row[f'{metric_key}_dev_pct'] = ((cons_mean - bsc_val) / bsc_val) * 100
                else:
                    row[f'{metric_key}_dev_pct'] = None

                # Spread (range of consensus)
                if len(cons_vals) >= 2:
                    vals = list(cons_vals.values())
                    row[f'{metric_key}_spread_pct'] = ((max(vals) - min(vals)) / cons_mean) * 100
                else:
                    row[f'{metric_key}_spread_pct'] = None

                # Max deviation source
                if bsc_val and bsc_val > 0 and cons_vals:
                    max_dev = 0
                    max_dev_src = None
                    for src, val in cons_vals.items():
                        dev = abs((val - bsc_val) / bsc_val * 100)
                        if dev > abs(max_dev):
                            max_dev = (val - bsc_val) / bsc_val * 100
                            max_dev_src = src
                    row[f'{metric_key}_max_dev_src'] = max_dev_src
                    row[f'{metric_key}_max_dev_pct'] = max_dev
                else:
                    row[f'{metric_key}_max_dev_src'] = None
                    row[f'{metric_key}_max_dev_pct'] = None
            else:
                row[f'{metric_key}_cons_mean'] = None
                row[f'{metric_key}_dev_pct'] = None
                row[f'{metric_key}_spread_pct'] = None
                row[f'{metric_key}_max_dev_src'] = None
                row[f'{metric_key}_max_dev_pct'] = None

        # Determine insight based on NPATMI 2027 deviation (next year)
        dev_27 = row.get('npatmi_27_dev_pct')
        dev_26 = row.get('npatmi_26_dev_pct')
        spread_27 = row.get('npatmi_27_spread_pct')

        if pd.isna(dev_27) and pd.isna(dev_26):
            row['insight'] = 'no_data'
        elif spread_27 and spread_27 > 30:
            row['insight'] = 'high_variance'
        else:
            # Use 2027 deviation primarily
            dev = dev_27 if pd.notna(dev_27) else dev_26
            if dev is None:
                row['insight'] = 'no_data'
            elif dev <= -15:
                row['insight'] = 'strong_bullish'  # BSC much higher
            elif dev <= -5:
                row['insight'] = 'bullish_gap'  # BSC higher
            elif dev >= 15:
                row['insight'] = 'strong_bearish'  # BSC much lower
            elif dev >= 5:
                row['insight'] = 'bearish_gap'  # BSC lower
            else:
                row['insight'] = 'aligned'

        # Source count (consensus sources only, not BSC)
        row['source_count'] = sum(1 for src in ['hcm', 'ssi', 'vci']
                                   if pd.notna(row.get(f'{src}_npatmi_27')) or pd.notna(row.get(f'{src}_tp')))

        comparison_rows.append(row)

    return pd.DataFrame(comparison_rows)


def build_unified(sources: list = None):
    """Build unified parquet from source JSONs."""
    if sources is None:
        sources = ALL_SOURCES

    print("=" * 60)
    print("Building Unified Forecast Parquet")
    print(f"Sources: {sources}")
    print("=" * 60)

    # Load all sources
    print("\n📥 Loading source JSONs...")
    all_stocks = []
    for src in sources:
        stocks = load_source_json(src)
        all_stocks.extend(stocks)

    if not all_stocks:
        print("\n❌ No data loaded from any source!")
        return False

    print(f"\n📊 Total: {len(all_stocks)} stock records from {len(sources)} sources")

    # Create DataFrame
    df = pd.DataFrame(all_stocks)
    df = normalize_columns(df)

    # Build comparison metrics
    print("\n🔄 Calculating comparison metrics...")
    unified_df = calculate_comparison_metrics(df)

    # Add metadata
    unified_df['build_timestamp'] = datetime.now().isoformat()

    # Save unified parquet
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    unified_path = OUTPUT_DIR / "unified.parquet"
    unified_df.to_parquet(unified_path, index=False)
    print(f"\n💾 Saved: {unified_path}")
    print(f"   Rows: {len(unified_df)}, Columns: {len(unified_df.columns)}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Unique symbols: {unified_df['symbol'].nunique()}")
    print(f"With BSC data: {unified_df['bsc_tp'].notna().sum()}")
    print(f"With consensus: {(unified_df['source_count'] > 1).sum()}")

    insight_counts = unified_df['insight'].value_counts()
    print(f"\nInsight distribution:")
    for insight, count in insight_counts.items():
        print(f"  {insight}: {count}")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build unified forecast parquet")
    parser.add_argument('--sources', type=str, default=None,
                        help='Comma-separated sources (default: all)')

    args = parser.parse_args()

    sources = None
    if args.sources:
        sources = [s.strip() for s in args.sources.split(',')]

    success = build_unified(sources)
    if success:
        print("\n✅ Done!")
    else:
        print("\n❌ Failed!")
        exit(1)
