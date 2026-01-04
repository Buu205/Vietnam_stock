#!/usr/bin/env python3
"""
BSC vs Consensus Comparison Data Processor
==========================================
Creates pre-joined comparison table for Streamlit dashboard.

Output: DATA/processed/forecast/comparison/bsc_vs_consensus.parquet

Schema (2026F/2027F):
- symbol, sector, entity_type
- current_price, bsc_tp, hcm_tp, ssi_tp, vci_tp
- bsc_npatmi_26, hcm_npatmi_26, ssi_npatmi_26, vci_npatmi_26
- bsc_npatmi_27, hcm_npatmi_27, ssi_npatmi_27, vci_npatmi_27
- consensus_tp_mean, consensus_npatmi26_mean, consensus_npatmi27_mean
- tp_dev_pct, npatmi26_dev_pct, npatmi27_dev_pct (vs BSC)
- tp_spread_pct, npatmi26_spread_pct (range of consensus)
- max_dev_source, max_dev_pct
- insight (bullish/aligned/bearish)
- source_count

Note: Schema migrated from 2025F/2026F to 2026F/2027F in Jan 2026.
BSC data still uses 2025F/2026F, mapped to 2026F/2027F for comparison.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
PROJECT_ROOT = Path("/Users/buuphan/Dev/Vietnam_dashboard")
BSC_PATH = PROJECT_ROOT / "DATA/processed/forecast/bsc/bsc_combined.parquet"
CONSENSUS_PATH = PROJECT_ROOT / "DATA/processed/forecast/consensus/consensus_combined.parquet"
OUTPUT_DIR = PROJECT_ROOT / "DATA/processed/forecast/comparison"
OUTPUT_PATH = OUTPUT_DIR / "bsc_vs_consensus.parquet"


def load_data():
    """Load BSC and consensus data."""
    bsc = pd.read_parquet(BSC_PATH)
    consensus = pd.read_parquet(CONSENSUS_PATH)
    return bsc, consensus


def pivot_consensus(consensus: pd.DataFrame) -> pd.DataFrame:
    """Pivot consensus data by source for easy merging.

    Handles both old (2025F/2026F) and new (2026F/2027F) schemas.
    """
    # Target Price pivot
    tp_pivot = consensus.pivot_table(
        index='symbol',
        columns='source',
        values='target_price',
        aggfunc='first'
    )
    tp_pivot.columns = [f'{c}_tp' for c in tp_pivot.columns]

    # Detect schema version
    has_2026f = 'npatmi_2026f' in consensus.columns
    has_2027f = 'npatmi_2027f' in consensus.columns
    has_2025f = 'npatmi_2025f' in consensus.columns

    # NPATMI Year 1 (current year forecast)
    # New schema: 2026F, Old schema: 2025F
    year1_col = 'npatmi_2026f' if has_2026f else 'npatmi_2025f'
    np_year1_pivot = consensus.pivot_table(
        index='symbol',
        columns='source',
        values=year1_col,
        aggfunc='first'
    )
    np_year1_pivot.columns = [f'{c}_npatmi_26' for c in np_year1_pivot.columns]

    # NPATMI Year 2 (next year forecast)
    # New schema: 2027F, Old schema: 2026F
    year2_col = 'npatmi_2027f' if has_2027f else 'npatmi_2026f'
    np_year2_pivot = consensus.pivot_table(
        index='symbol',
        columns='source',
        values=year2_col,
        aggfunc='first'
    )
    np_year2_pivot.columns = [f'{c}_npatmi_27' for c in np_year2_pivot.columns]

    # Merge all pivots
    pivoted = tp_pivot.join(np_year1_pivot, how='outer').join(np_year2_pivot, how='outer')
    return pivoted.reset_index()


def calculate_consensus_stats(row: pd.Series, metric: str) -> dict:
    """Calculate consensus mean, spread, max deviation for a metric."""
    sources = ['hcm', 'ssi', 'vci']
    bsc_col = f'bsc_{metric}'

    # Get values
    bsc_val = row.get(bsc_col)
    cons_vals = {src: row.get(f'{src}_{metric}') for src in sources}
    valid_vals = {k: v for k, v in cons_vals.items() if pd.notna(v) and v > 0}

    result = {
        f'{metric}_cons_mean': None,
        f'{metric}_dev_pct': None,
        f'{metric}_spread_pct': None,
        f'{metric}_max_dev_src': None,
        f'{metric}_max_dev_pct': None,
    }

    if not valid_vals:
        return result

    # Consensus mean
    cons_mean = np.mean(list(valid_vals.values()))
    result[f'{metric}_cons_mean'] = cons_mean

    # Deviation from BSC (%)
    if pd.notna(bsc_val) and bsc_val > 0:
        dev_pct = (cons_mean - bsc_val) / bsc_val * 100
        result[f'{metric}_dev_pct'] = dev_pct

        # Spread (range as % of BSC)
        cons_min = min(valid_vals.values())
        cons_max = max(valid_vals.values())
        spread_pct = (cons_max - cons_min) / bsc_val * 100
        result[f'{metric}_spread_pct'] = spread_pct

        # Max deviation source
        max_src = None
        max_dev = 0
        for src, val in valid_vals.items():
            dev = (val - bsc_val) / bsc_val * 100
            if abs(dev) > abs(max_dev):
                max_dev = dev
                max_src = src

        result[f'{metric}_max_dev_src'] = max_src
        result[f'{metric}_max_dev_pct'] = max_dev

    return result


def get_insight(tp_dev: float, npatmi_dev: float, spread: float) -> str:
    """Generate insight label based on deviations.

    Note: dev values are (Consensus - BSC) / BSC
    - Positive = Consensus > BSC = BSC conservative (bearish)
    - Negative = Consensus < BSC = BSC optimistic (bullish)

    We want BSC vs Consensus perspective:
    - BSC > Consensus (dev negative) = BSC Bullish
    - BSC < Consensus (dev positive) = BSC Bearish
    """
    # Use NPATMI as primary, TP as secondary
    primary_dev = npatmi_dev if pd.notna(npatmi_dev) else tp_dev

    if pd.isna(primary_dev):
        return "no_data"

    # Flip signs: negative dev = BSC higher = bullish
    if primary_dev <= -15:
        return "strong_bullish"  # BSC >> Consensus
    elif primary_dev <= -5:
        return "bullish_gap"     # BSC > Consensus
    elif primary_dev >= 15:
        return "strong_bearish"  # BSC << Consensus
    elif primary_dev >= 5:
        return "bearish_gap"     # BSC < Consensus
    else:
        # Within ±5%
        if pd.notna(spread) and spread > 15:
            return "high_variance"
        return "aligned"


def create_comparison_table():
    """Create the full comparison table."""
    print("Loading data...")
    bsc, consensus = load_data()

    print(f"BSC: {len(bsc)} stocks, Consensus: {len(consensus)} records")

    # Pivot consensus by source
    print("Pivoting consensus data...")
    cons_pivot = pivot_consensus(consensus)

    # Detect BSC schema version and select columns
    # BSC may have 2025F/2026F or 2026F/2027F
    bsc_has_2026f = 'npatmi_2026f' in bsc.columns
    bsc_has_2027f = 'npatmi_2027f' in bsc.columns

    # Use 2025F/2026F mapped to 26/27 labels (year shift for comparison)
    if bsc_has_2027f:
        # New schema
        bsc_cols = bsc[['symbol', 'sector', 'entity_type', 'current_price',
                        'target_price', 'npatmi_2026f', 'npatmi_2027f', 'rating']].copy()
        bsc_cols = bsc_cols.rename(columns={
            'target_price': 'bsc_tp',
            'npatmi_2026f': 'bsc_npatmi_26',
            'npatmi_2027f': 'bsc_npatmi_27',
        })
    else:
        # Old schema - map 2025F→26, 2026F→27 for year alignment
        bsc_cols = bsc[['symbol', 'sector', 'entity_type', 'current_price',
                        'target_price', 'npatmi_2025f', 'npatmi_2026f', 'rating']].copy()
        bsc_cols = bsc_cols.rename(columns={
            'target_price': 'bsc_tp',
            'npatmi_2025f': 'bsc_npatmi_26',  # Map 2025F to current year (26)
            'npatmi_2026f': 'bsc_npatmi_27',  # Map 2026F to next year (27)
        })
        print("[INFO] BSC using 2025F/2026F schema, mapped to 2026F/2027F labels")

    # Merge BSC with pivoted consensus
    print("Merging BSC with consensus...")
    merged = bsc_cols.merge(cons_pivot, on='symbol', how='outer')

    # Calculate stats for each metric (updated to 26/27 year labels)
    print("Calculating statistics...")
    for metric in ['tp', 'npatmi_26', 'npatmi_27']:
        stats_list = merged.apply(lambda row: calculate_consensus_stats(row, metric), axis=1)
        stats_df = pd.DataFrame(stats_list.tolist())
        for col in stats_df.columns:
            merged[col] = stats_df[col]

    # Generate insight (use NPATMI 2027F as primary - next year forecast)
    merged['insight'] = merged.apply(
        lambda row: get_insight(
            row.get('tp_dev_pct'),
            row.get('npatmi_27_dev_pct'),
            row.get('npatmi_27_spread_pct')
        ),
        axis=1
    )

    # Count sources
    def count_sources(row):
        count = 0
        for src in ['hcm', 'ssi', 'vci']:
            if pd.notna(row.get(f'{src}_tp')) or pd.notna(row.get(f'{src}_npatmi_26')):
                count += 1
        return count

    merged['source_count'] = merged.apply(count_sources, axis=1)

    # Filter to stocks with data
    merged = merged[
        (merged['bsc_tp'].notna()) |
        (merged['source_count'] > 0)
    ].copy()

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(OUTPUT_PATH, index=False)

    print(f"\n=== OUTPUT SUMMARY ===")
    print(f"Total stocks: {len(merged)}")
    print(f"With BSC data: {merged['bsc_tp'].notna().sum()}")
    print(f"With consensus: {(merged['source_count'] > 0).sum()}")
    print(f"Overlap (BSC + consensus): {((merged['bsc_tp'].notna()) & (merged['source_count'] > 0)).sum()}")
    print(f"\nInsight distribution:")
    print(merged['insight'].value_counts())
    print(f"\nSaved to: {OUTPUT_PATH}")

    return merged


if __name__ == "__main__":
    create_comparison_table()
