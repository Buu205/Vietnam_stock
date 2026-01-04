#!/usr/bin/env python3
"""
Integrate VCI API data into consensus forecast format.

This script:
1. Reads VCI API data from vci_coverage_universe.parquet
2. Converts to consensus format (2026F/2027F)
3. Outputs vci_forecast.parquet for consensus comparison

Usage:
    python integrate_vci_api.py
    python integrate_vci_api.py --update-consensus  # Also regenerate combined file
"""

import argparse
import pandas as pd
from pathlib import Path

# Paths
PROJECT_ROOT = Path("/Users/buuphan/Dev/Vietnam_dashboard")
VCI_API_PATH = PROJECT_ROOT / "DATA/processed/forecast/VCI/vci_coverage_universe.parquet"
OUTPUT_DIR = PROJECT_ROOT / "DATA/processed/forecast/consensus"


def load_vci_api_data() -> pd.DataFrame:
    """Load VCI API data from parquet."""
    if not VCI_API_PATH.exists():
        print(f"[ERROR] VCI API data not found: {VCI_API_PATH}")
        return pd.DataFrame()

    df = pd.read_parquet(VCI_API_PATH)
    print(f"[INFO] Loaded {len(df)} stocks from VCI API")
    return df


def convert_to_consensus_format(vci_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert VCI API data to consensus format.

    VCI API has:
    - npatmi_2026F, npatmi_2027F (in full VND)
    - targetPrice
    - rating

    Consensus format needs:
    - symbol, source, target_price
    - npatmi_2026f, npatmi_2027f (in billion VND)
    - is_calculated
    """
    if vci_df.empty:
        return pd.DataFrame()

    # Create consensus format dataframe
    consensus = pd.DataFrame({
        'symbol': vci_df['ticker'].str.upper(),
        'source': 'vci',
        'target_price': vci_df['targetPrice'],
        'npatmi_2026f': vci_df['npatmi_2026F'] / 1e9,  # Convert to billion VND
        'npatmi_2027f': vci_df['npatmi_2027F'] / 1e9,  # Convert to billion VND
        'is_calculated': False,  # Direct from API, not calculated
    })

    # Round NPATMI values
    consensus['npatmi_2026f'] = consensus['npatmi_2026f'].round(2)
    consensus['npatmi_2027f'] = consensus['npatmi_2027f'].round(2)

    # Sort by symbol
    consensus = consensus.sort_values('symbol').reset_index(drop=True)

    return consensus


def update_combined_consensus(vci_df: pd.DataFrame) -> pd.DataFrame:
    """
    Update consensus_combined.parquet with new VCI data.

    This replaces existing VCI entries with fresh API data.
    HCM and SSI data are preserved.
    """
    combined_path = OUTPUT_DIR / "consensus_combined.parquet"

    # Load existing combined data
    if combined_path.exists():
        existing = pd.read_parquet(combined_path)

        # Check if schema needs update (2025F/2026F vs 2026F/2027F)
        if 'npatmi_2025f' in existing.columns:
            print("[INFO] Migrating schema from 2025F/2026F to 2026F/2027F...")
            # Rename columns for year shift
            existing = existing.rename(columns={
                'npatmi_2025f': 'npatmi_2026f',
                'npatmi_2026f': 'npatmi_2027f'
            })

        # Remove existing VCI entries
        non_vci = existing[existing['source'] != 'vci'].copy()
        print(f"[INFO] Existing non-VCI records: {len(non_vci)}")
    else:
        non_vci = pd.DataFrame()

    # Combine with new VCI data
    combined = pd.concat([non_vci, vci_df], ignore_index=True)
    combined = combined.sort_values(['symbol', 'source']).reset_index(drop=True)

    return combined


def generate_summary(combined: pd.DataFrame) -> pd.DataFrame:
    """Generate consensus summary with mean/min/max across sources."""
    if combined.empty:
        return pd.DataFrame()

    summary = combined.groupby('symbol').agg({
        'source': lambda x: ','.join(sorted(x.unique())),
        'target_price': ['mean', 'min', 'max', 'count'],
        'npatmi_2026f': ['mean', 'min', 'max', 'count'],
        'npatmi_2027f': ['mean', 'min', 'max', 'count'],
    }).reset_index()

    # Flatten column names
    summary.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col
                       for col in summary.columns]

    return summary


def main():
    parser = argparse.ArgumentParser(description="Integrate VCI API data into consensus format")
    parser.add_argument('--update-consensus', action='store_true',
                        help='Also update consensus_combined.parquet')
    args = parser.parse_args()

    print("=" * 60)
    print("VCI API INTEGRATION")
    print("=" * 60)

    # Load VCI API data
    vci_raw = load_vci_api_data()
    if vci_raw.empty:
        print("[ERROR] No VCI API data to process")
        return

    # Convert to consensus format
    vci_consensus = convert_to_consensus_format(vci_raw)
    print(f"\n[CONVERTED] {len(vci_consensus)} VCI stocks to consensus format")

    # Stats
    npatmi_2026_coverage = vci_consensus['npatmi_2026f'].notna().sum()
    npatmi_2027_coverage = vci_consensus['npatmi_2027f'].notna().sum()
    tp_coverage = vci_consensus['target_price'].notna().sum()

    print(f"  - NPATMI 2026F: {npatmi_2026_coverage}/{len(vci_consensus)} ({npatmi_2026_coverage/len(vci_consensus)*100:.0f}%)")
    print(f"  - NPATMI 2027F: {npatmi_2027_coverage}/{len(vci_consensus)} ({npatmi_2027_coverage/len(vci_consensus)*100:.0f}%)")
    print(f"  - Target Price: {tp_coverage}/{len(vci_consensus)} ({tp_coverage/len(vci_consensus)*100:.0f}%)")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save VCI forecast
    vci_path = OUTPUT_DIR / "vci_forecast.parquet"
    vci_consensus.to_parquet(vci_path, index=False)
    print(f"\n[SAVED] {vci_path}")

    # Update combined consensus if requested
    if args.update_consensus:
        print("\n" + "=" * 60)
        print("UPDATING COMBINED CONSENSUS")
        print("=" * 60)

        combined = update_combined_consensus(vci_consensus)
        print(f"\n[COMBINED] Total records: {len(combined)}")
        print(f"  - Unique tickers: {combined['symbol'].nunique()}")
        print(f"  - Sources: {combined['source'].unique().tolist()}")

        # Coverage distribution
        coverage = combined.groupby('symbol')['source'].count()
        print(f"\n[COVERAGE]")
        print(f"  - 1 source: {(coverage == 1).sum()} stocks")
        print(f"  - 2 sources: {(coverage == 2).sum()} stocks")
        print(f"  - 3 sources: {(coverage >= 3).sum()} stocks")

        # Save combined
        combined_path = OUTPUT_DIR / "consensus_combined.parquet"
        combined.to_parquet(combined_path, index=False)
        print(f"\n[SAVED] {combined_path}")

        # Generate and save summary
        summary = generate_summary(combined)
        if not summary.empty:
            summary_path = OUTPUT_DIR / "consensus_summary.parquet"
            summary.to_parquet(summary_path, index=False)
            print(f"[SAVED] {summary_path}")

    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
