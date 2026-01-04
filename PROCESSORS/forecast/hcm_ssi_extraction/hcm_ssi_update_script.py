#!/usr/bin/env python3
"""
Normalize and back-calculate consensus forecast data from multiple sources.

This script:
1. Reads raw JSON extracts from HCM, SSI, VCI
2. Back-calculates missing NPATMI using growth rates
3. Cross-references with BSC data for validation
4. Normalizes to standard schema matching BSC format
5. Outputs cleaned parquet files for consensus comparison

Usage:
    python normalize_consensus_data.py
    python normalize_consensus_data.py --output-format json
    python normalize_consensus_data.py --validate-only
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# Paths
PROJECT_ROOT = Path("/Users/buuphan/Dev/Vietnam_dashboard")
RAW_FORECAST_DIR = PROJECT_ROOT / "DATA" / "raw" / "forecast"
DATA_DIR = PROJECT_ROOT / "DATA/processed/forecast"
BSC_PATH = DATA_DIR / "bsc/bsc_combined.parquet"
OUTPUT_DIR = DATA_DIR / "consensus"
SOURCES_DIR = DATA_DIR / "sources"

# Source-specific paths
def get_extracted_json(source: str) -> Path:
    """Get path to extracted JSON for a source."""
    return RAW_FORECAST_DIR / source / "extracted" / f"{source}_raw.json"

# Simplified schema - focus on 2026F/2027F (2025 data outdated soon)
STANDARD_SCHEMA = {
    'symbol': str,
    'source': str,  # hcm, ssi, vci
    'target_price': float,
    'npatmi_2026f': float,
    'npatmi_2027f': float,
    'eps_2026f': float,
    'eps_2027f': float,
    'pe_2026f': float,
    'pe_2027f': float,
    'is_calculated': bool,  # Flag if NPATMI was back-calculated
}


def load_bsc_reference() -> pd.DataFrame:
    """Load BSC data as reference for cross-validation."""
    if BSC_PATH.exists():
        df = pd.read_parquet(BSC_PATH)
        df = df.rename(columns={'symbol': 'ticker'})
        return df
    return pd.DataFrame()


def load_fundamental_2024() -> pd.DataFrame:
    """Load 2024 actual NPATMI from fundamental data (sum of 4 quarters for all entity types)."""
    base_path = Path("/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/fundamental")

    all_data = []
    entity_types = ['company', 'bank', 'insurance', 'security']

    for entity_type in entity_types:
        file_path = base_path / entity_type / f"{entity_type}_financial_metrics.parquet"
        if not file_path.exists():
            continue

        df = pd.read_parquet(file_path)

        # Check if npatmi column exists
        if 'npatmi' not in df.columns:
            continue

        # Get 2024 quarterly data (Q1, Q2, Q3, Q4)
        df_2024_q = df[(df['year'] == 2024) & (df['freq_code'] == 'Q')][['symbol', 'quarter', 'npatmi']].copy()

        if not df_2024_q.empty:
            # Sum 4 quarters per stock
            df_sum = df_2024_q.groupby('symbol')['npatmi'].sum().reset_index()
            all_data.append(df_sum)
            print(f"[INFO] {entity_type.upper()}: {len(df_sum)} stocks with 2024 data")

    if not all_data:
        print("[WARNING] No fundamental 2024 data found")
        return pd.DataFrame()

    # Combine all entity types
    df_2024 = pd.concat(all_data, ignore_index=True)
    df_2024.columns = ['ticker', 'npatmi_2024a']

    # Convert VND to billion VND
    df_2024['npatmi_2024a'] = df_2024['npatmi_2024a'] / 1e9

    print(f"[INFO] Total: {len(df_2024)} stocks with 2024 NPATMI (sum of Q1-Q4)")
    return df_2024


def load_raw_json(filename: str) -> list:
    """Load raw JSON extract from staging directory."""
    filepath = STAGING_DIR / filename
    if not filepath.exists():
        print(f"[WARNING] File not found: {filepath}")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Dedupe: merge duplicate tickers, prefer non-None values
    ticker_map = {}
    for d in data:
        ticker = d.get('ticker', '').upper()
        if not ticker:
            continue
        if ticker not in ticker_map:
            ticker_map[ticker] = d.copy()
        else:
            # Merge: prefer non-None values from new entry
            for key, value in d.items():
                if value is not None and ticker_map[ticker].get(key) is None:
                    ticker_map[ticker][key] = value

    deduped = list(ticker_map.values())
    if len(deduped) < len(data):
        print(f"[INFO] Deduped: {len(data)} → {len(deduped)} records")

    return deduped


def load_ohlcv_data() -> pd.DataFrame:
    """Load latest OHLCV data for market cap and shares outstanding."""
    ohlcv_path = PROJECT_ROOT / "DATA" / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"
    if not ohlcv_path.exists():
        print("[WARNING] OHLCV data not found")
        return pd.DataFrame()

    df = pd.read_parquet(ohlcv_path)
    # Get latest data per ticker
    df = df.sort_values('date').groupby('symbol').tail(1)
    df = df[['symbol', 'close', 'market_cap', 'shares_outstanding']].copy()
    df.columns = ['ticker', 'close', 'market_cap', 'shares_outstanding']
    return df


def back_calculate_npatmi(stock: dict, bsc_ref: pd.DataFrame, fundamental_2024: pd.DataFrame,
                          ohlcv_df: pd.DataFrame = None) -> dict:
    """
    Back-calculate missing NPATMI values using multiple strategies.

    Priority:
    1. Direct extraction (already in stock dict)
    2. Growth rate + 2024 fundamental
    3. PE Forward + Market Cap/Outstanding Shares
    4. BSC reference fallback
    """
    ticker = stock.get('ticker', '').upper()
    result = stock.copy()
    result['is_calculated'] = False

    # Get values
    npatmi_2024a = stock.get('npatmi_2024a')
    npatmi_2025f = stock.get('npatmi_2025f')
    npatmi_2026f = stock.get('npatmi_2026f')
    growth_2025 = stock.get('npatmi_growth_2025')
    growth_2026 = stock.get('npatmi_growth_2026')

    # Try to get fundamental 2024 actual data
    fund_row = fundamental_2024[fundamental_2024['ticker'] == ticker] if not fundamental_2024.empty else pd.DataFrame()

    # Try to get BSC reference values
    bsc_row = bsc_ref[bsc_ref['ticker'] == ticker] if not bsc_ref.empty else pd.DataFrame()

    # Strategy 0: Get 2024 actual from fundamental data if missing
    if npatmi_2024a is None and not fund_row.empty:
        fund_npatmi = fund_row['npatmi_2024a'].values[0]
        if pd.notna(fund_npatmi):
            npatmi_2024a = fund_npatmi
            result['npatmi_2024a'] = round(npatmi_2024a, 2)
            result['calc_note'] = 'base_from_fundamental'

    # Strategy 1: Use 2024a + growth to calculate 2025f
    if npatmi_2025f is None and npatmi_2024a is not None and growth_2025 is not None:
        npatmi_2025f = npatmi_2024a * (1 + growth_2025)
        result['npatmi_2025f'] = round(npatmi_2025f, 2)
        result['is_calculated'] = True

    # Strategy 2: Use 2025f + growth to calculate 2026f
    if npatmi_2026f is None and npatmi_2025f is not None and growth_2026 is not None:
        npatmi_2026f = npatmi_2025f * (1 + growth_2026)
        result['npatmi_2026f'] = round(npatmi_2026f, 2)
        result['is_calculated'] = True

    # Strategy 3: PE-based calculation (Priority 3)
    # Option A: NPATMI = Market Cap / PE
    # Option B: NPATMI = (Target Price / PE) * Outstanding Shares
    if result.get('npatmi_2025f') is None and ohlcv_df is not None and not ohlcv_df.empty:
        ohlcv_row = ohlcv_df[ohlcv_df['ticker'] == ticker]
        pe_2025 = stock.get('pe_fwd_2025')
        target_price = stock.get('target_price')

        if not ohlcv_row.empty and pe_2025 is not None and pe_2025 > 0:
            shares = ohlcv_row['shares_outstanding'].values[0]
            mkt_cap = ohlcv_row['market_cap'].values[0]

            # Option A: Use market cap if available
            if pd.notna(mkt_cap) and mkt_cap > 0:
                # Market cap is in VND, convert to billion VND
                npatmi_2025f = (mkt_cap / 1e9) / pe_2025
                result['npatmi_2025f'] = round(npatmi_2025f, 2)
                result['is_calculated'] = True
                result['calc_note'] = 'from_pe_mktcap'

            # Option B: Use target price + shares
            elif pd.notna(shares) and shares > 0 and target_price is not None and target_price > 0:
                eps_2025 = target_price / pe_2025  # VND
                npatmi_2025f = (eps_2025 * shares) / 1e9  # Convert to billion VND
                result['npatmi_2025f'] = round(npatmi_2025f, 2)
                result['is_calculated'] = True
                result['calc_note'] = 'from_pe_tp_shares'

    # Strategy 4: If still missing 2025f, try BSC reference + our growth
    if result.get('npatmi_2025f') is None and not bsc_row.empty and growth_2025 is not None:
        bsc_npatmi_2025 = bsc_row['npatmi_2025f'].values[0]
        if pd.notna(bsc_npatmi_2025):
            # Use BSC as base, but note it's cross-referenced
            result['npatmi_2025f'] = round(bsc_npatmi_2025, 2)
            result['is_calculated'] = True
            result['calc_note'] = 'from_bsc_ref'

    # Strategy 4: Calculate 2026f from newly filled 2025f
    if result.get('npatmi_2026f') is None and result.get('npatmi_2025f') is not None and growth_2026 is not None:
        npatmi_2026f = result['npatmi_2025f'] * (1 + growth_2026)
        result['npatmi_2026f'] = round(npatmi_2026f, 2)
        result['is_calculated'] = True

    return result


def normalize_stock(stock: dict, source: str) -> dict:
    """Normalize a single stock record to simplified schema (TP + NPATMI only)."""
    ticker = stock.get('ticker', '').upper().strip()
    if not ticker:
        return None

    normalized = {
        'symbol': ticker,
        'source': source,
        'target_price': stock.get('target_price'),
        'npatmi_2025f': stock.get('npatmi_2025f'),
        'npatmi_2026f': stock.get('npatmi_2026f'),
        'is_calculated': stock.get('is_calculated', False),
    }

    return normalized


def process_source(filename: str, source: str, bsc_ref: pd.DataFrame,
                   fundamental_2024: pd.DataFrame, ohlcv_df: pd.DataFrame = None) -> pd.DataFrame:
    """Process a single source file."""
    print(f"\n{'='*60}")
    print(f"Processing: {source.upper()} ({filename})")
    print(f"{'='*60}")

    raw_data = load_raw_json(filename)
    if not raw_data:
        return pd.DataFrame()

    print(f"Loaded {len(raw_data)} raw records")

    # Back-calculate and normalize
    processed = []
    calc_count = 0
    filled_from_fundamental = 0
    filled_from_pe = 0

    for stock in raw_data:
        # Back-calculate missing NPATMI
        stock = back_calculate_npatmi(stock, bsc_ref, fundamental_2024, ohlcv_df)
        if stock.get('is_calculated'):
            calc_count += 1
        if stock.get('calc_note') == 'base_from_fundamental':
            filled_from_fundamental += 1
        if stock.get('calc_note') in ['from_pe_mktcap', 'from_pe_tp_shares']:
            filled_from_pe += 1

        # Normalize to standard schema
        normalized = normalize_stock(stock, source)
        if normalized:
            processed.append(normalized)

    df = pd.DataFrame(processed)

    # Stats
    has_npatmi_2025 = df['npatmi_2025f'].notna().sum()
    has_npatmi_2026 = df['npatmi_2026f'].notna().sum()

    print(f"Processed: {len(df)} stocks")
    print(f"Back-calculated: {calc_count} stocks")
    print(f"  - From 2024 fundamental: {filled_from_fundamental}")
    print(f"  - From PE calculation: {filled_from_pe}")
    print(f"Has NPATMI 2025F: {has_npatmi_2025}/{len(df)}")
    print(f"Has NPATMI 2026F: {has_npatmi_2026}/{len(df)}")

    return df


def create_combined_consensus(dfs: dict) -> pd.DataFrame:
    """Create combined consensus dataset from all sources."""
    all_data = []

    for source, df in dfs.items():
        if not df.empty:
            all_data.append(df)

    if not all_data:
        return pd.DataFrame()

    combined = pd.concat(all_data, ignore_index=True)

    # Sort by symbol, then source
    combined = combined.sort_values(['symbol', 'source']).reset_index(drop=True)

    return combined


def generate_consensus_summary(combined: pd.DataFrame) -> pd.DataFrame:
    """Generate consensus summary with mean/min/max across sources (TP + NPATMI only)."""
    if combined.empty:
        return pd.DataFrame()

    summary = combined.groupby('symbol').agg({
        'source': lambda x: ','.join(sorted(x.unique())),
        'target_price': ['mean', 'min', 'max', 'count'],
        'npatmi_2025f': ['mean', 'min', 'max', 'count'],
        'npatmi_2026f': ['mean', 'min', 'max', 'count'],
    }).reset_index()

    # Flatten column names
    summary.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col
                       for col in summary.columns]

    return summary


def main():
    parser = argparse.ArgumentParser(description="Normalize consensus forecast data")
    parser.add_argument('--output-format', choices=['parquet', 'json', 'both'],
                        default='parquet', help='Output format (default: parquet only)')
    parser.add_argument('--validate-only', action='store_true',
                        help='Only validate, do not save')
    args = parser.parse_args()

    print("="*60)
    print("CONSENSUS DATA NORMALIZATION")
    print("="*60)

    # Load BSC reference
    bsc_ref = load_bsc_reference()
    print(f"BSC Reference: {len(bsc_ref)} stocks loaded")

    # Load 2024 actual NPATMI from fundamental data
    fundamental_2024 = load_fundamental_2024()

    # Load OHLCV data for PE-based calculation
    ohlcv_df = load_ohlcv_data()
    print(f"OHLCV Data: {len(ohlcv_df)} stocks loaded")

    # Process each source
    sources = {
        'hcm': 'hcm_raw.json',
        'ssi': 'ssi_raw.json',
        'vci': 'vci_raw.json',
    }

    dfs = {}
    for source, filename in sources.items():
        dfs[source] = process_source(filename, source, bsc_ref, fundamental_2024, ohlcv_df)

    # Create combined dataset
    combined = create_combined_consensus(dfs)

    print(f"\n{'='*60}")
    print("COMBINED CONSENSUS DATA")
    print(f"{'='*60}")
    print(f"Total records: {len(combined)}")
    print(f"Unique tickers: {combined['symbol'].nunique()}")
    print(f"Sources: {combined['source'].unique().tolist()}")

    # Coverage stats
    coverage = combined.groupby('symbol')['source'].count()
    print(f"\nCoverage distribution:")
    print(f"  - 1 source: {(coverage == 1).sum()} stocks")
    print(f"  - 2 sources: {(coverage == 2).sum()} stocks")
    print(f"  - 3 sources: {(coverage == 3).sum()} stocks")

    if args.validate_only:
        print("\n[VALIDATE ONLY] No files saved.")
        return

    # Save outputs
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save individual source files
    for source, df in dfs.items():
        if df.empty:
            continue

        if args.output_format in ['parquet', 'both']:
            output_path = OUTPUT_DIR / f"{source}_forecast.parquet"
            df.to_parquet(output_path, index=False)
            print(f"\nSaved: {output_path}")

        if args.output_format in ['json', 'both']:
            output_path = OUTPUT_DIR / f"{source}_forecast.json"
            df.to_json(output_path, orient='records', force_ascii=False, indent=2)
            print(f"Saved: {output_path}")

    # Save combined dataset
    if args.output_format in ['parquet', 'both']:
        output_path = OUTPUT_DIR / "consensus_combined.parquet"
        combined.to_parquet(output_path, index=False)
        print(f"\nSaved: {output_path}")

    if args.output_format in ['json', 'both']:
        output_path = OUTPUT_DIR / "consensus_combined.json"
        combined.to_json(output_path, orient='records', force_ascii=False, indent=2,
                        date_format='iso')
        print(f"Saved: {output_path}")

    # Generate and save summary
    summary = generate_consensus_summary(combined)
    if not summary.empty:
        summary_path = OUTPUT_DIR / "consensus_summary.parquet"
        summary.to_parquet(summary_path, index=False)
        print(f"Saved: {summary_path}")

    print(f"\n{'='*60}")
    print("DONE!")
    print(f"{'='*60}")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
