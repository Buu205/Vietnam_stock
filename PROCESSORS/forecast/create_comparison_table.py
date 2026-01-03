#!/usr/bin/env python3
"""
BSC vs Consensus Comparison Data Processor
==========================================
Creates pre-joined comparison table for Streamlit dashboard.

Output: DATA/processed/forecast/comparison/bsc_vs_consensus.parquet

Schema:
- symbol, sector, entity_type
- current_price, bsc_tp, hcm_tp, ssi_tp, vci_tp
- bsc_npatmi_25, hcm_npatmi_25, ssi_npatmi_25, vci_npatmi_25
- bsc_npatmi_26, hcm_npatmi_26, ssi_npatmi_26, vci_npatmi_26
- consensus_tp_mean, consensus_npatmi25_mean, consensus_npatmi26_mean
- tp_dev_pct, npatmi25_dev_pct, npatmi26_dev_pct (vs BSC)
- tp_spread_pct, npatmi25_spread_pct (range of consensus)
- max_dev_source, max_dev_pct
- insight (bullish/aligned/bearish)
- source_count
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
    """Pivot consensus data by source for easy merging."""
    # Target Price pivot
    tp_pivot = consensus.pivot_table(
        index='symbol',
        columns='source',
        values='target_price',
        aggfunc='first'
    )
    tp_pivot.columns = [f'{c}_tp' for c in tp_pivot.columns]

    # NPATMI 2025 pivot
    np25_pivot = consensus.pivot_table(
        index='symbol',
        columns='source',
        values='npatmi_2025f',
        aggfunc='first'
    )
    np25_pivot.columns = [f'{c}_npatmi_25' for c in np25_pivot.columns]

    # NPATMI 2026 pivot
    np26_pivot = consensus.pivot_table(
        index='symbol',
        columns='source',
        values='npatmi_2026f',
        aggfunc='first'
    )
    np26_pivot.columns = [f'{c}_npatmi_26' for c in np26_pivot.columns]

    # Merge all pivots
    pivoted = tp_pivot.join(np25_pivot, how='outer').join(np26_pivot, how='outer')
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

    # Select BSC columns and rename
    bsc_cols = bsc[['symbol', 'sector', 'entity_type', 'current_price',
                    'target_price', 'npatmi_2025f', 'npatmi_2026f', 'rating']].copy()
    bsc_cols = bsc_cols.rename(columns={
        'target_price': 'bsc_tp',
        'npatmi_2025f': 'bsc_npatmi_25',
        'npatmi_2026f': 'bsc_npatmi_26',
    })

    # Merge BSC with pivoted consensus
    print("Merging BSC with consensus...")
    merged = bsc_cols.merge(cons_pivot, on='symbol', how='outer')

    # Calculate stats for each metric
    print("Calculating statistics...")
    for metric in ['tp', 'npatmi_25', 'npatmi_26']:
        stats_list = merged.apply(lambda row: calculate_consensus_stats(row, metric), axis=1)
        stats_df = pd.DataFrame(stats_list.tolist())
        for col in stats_df.columns:
            merged[col] = stats_df[col]

    # Generate insight (use NPATMI 2026F as primary)
    merged['insight'] = merged.apply(
        lambda row: get_insight(
            row.get('tp_dev_pct'),
            row.get('npatmi_26_dev_pct'),
            row.get('npatmi_26_spread_pct')
        ),
        axis=1
    )

    # Count sources
    def count_sources(row):
        count = 0
        for src in ['hcm', 'ssi', 'vci']:
            if pd.notna(row.get(f'{src}_tp')) or pd.notna(row.get(f'{src}_npatmi_25')):
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
