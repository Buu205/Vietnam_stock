"""
Script to analyze BSC Forecast profit growth and add BSC Universal row.
====================================================================

Tasks:
1. Calculate total earning growth YoY (2025 vs 2024, 2026 vs 2025) from individual stocks
2. Add BSC Universal row with aggregated totals
3. Rename BSC_index -> BSC Universal if exists
4. Update bsc_sector_valuation.parquet with new columns

Run:
    python scripts/analyze_bsc_forecast_profit_growth.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "DATA" / "processed" / "forecast" / "bsc"


def load_data():
    """Load BSC forecast data."""
    individual_path = DATA_DIR / "bsc_individual.parquet"
    sector_path = DATA_DIR / "bsc_sector_valuation.parquet"

    individual_df = pd.read_parquet(individual_path)
    sector_df = pd.read_parquet(sector_path)

    print(f"Loaded {len(individual_df)} individual stocks")
    print(f"Loaded {len(sector_df)} sectors")

    return individual_df, sector_df


def calculate_total_profit_growth(individual_df: pd.DataFrame) -> dict:
    """
    Calculate total profit growth across BSC-covered stocks WITH VALID FORECAST DATA ONLY.

    IMPORTANT: Only includes stocks that have:
    - Valid npatmi_2025f (not NaN, > 0)
    - Valid npatmi_2026f (not NaN, > 0)
    - Valid npatmi_growth_yoy_2025 (not NaN, > -1)

    This ensures we compare apples-to-apples: same set of stocks for 2024 actual vs 2025F/2026F.

    Returns dict with:
    - total_npatmi_2024: Total NPATMI 2024 actual (only valid forecast stocks)
    - total_npatmi_2025f: Total NPATMI 2025 forecast (only valid forecast stocks)
    - total_npatmi_2026f: Total NPATMI 2026 forecast (only valid forecast stocks)
    - total_earning_growth_2025: YoY growth 2025 vs 2024
    - total_earning_growth_2026: YoY growth 2026 vs 2025
    - valid_stock_count: Number of stocks included in calculation
    - excluded_stocks: List of stocks excluded due to missing data
    """
    # Filter to only stocks with COMPLETE forecast data
    valid_stocks = individual_df[
        individual_df['npatmi_2025f'].notna() & (individual_df['npatmi_2025f'] > 0) &
        individual_df['npatmi_2026f'].notna() & (individual_df['npatmi_2026f'] > 0) &
        individual_df['npatmi_growth_yoy_2025'].notna() &
        (individual_df['npatmi_growth_yoy_2025'] > -1)  # Avoid division by zero
    ].copy()

    # Identify excluded stocks
    excluded = individual_df[~individual_df['symbol'].isin(valid_stocks['symbol'])]['symbol'].tolist()

    # Calculate 2024 actual from growth rate
    # npatmi_growth_yoy_2025 = (npatmi_2025f / npatmi_2024_actual) - 1
    # So: npatmi_2024_actual = npatmi_2025f / (1 + npatmi_growth_yoy_2025)
    valid_stocks['npatmi_2024_actual'] = valid_stocks['npatmi_2025f'] / (1 + valid_stocks['npatmi_growth_yoy_2025'])

    # Sum totals - ONLY from valid stocks (same stock set for all years)
    total_npatmi_2024 = valid_stocks['npatmi_2024_actual'].sum()
    total_npatmi_2025f = valid_stocks['npatmi_2025f'].sum()
    total_npatmi_2026f = valid_stocks['npatmi_2026f'].sum()

    # Calculate total growth rates
    total_earning_growth_2025 = (total_npatmi_2025f / total_npatmi_2024) - 1 if total_npatmi_2024 > 0 else np.nan
    total_earning_growth_2026 = (total_npatmi_2026f / total_npatmi_2025f) - 1 if total_npatmi_2025f > 0 else np.nan

    print("\n=== Total Profit Analysis (Valid Forecast Stocks Only) ===")
    print(f"Valid stocks: {len(valid_stocks)}/{len(individual_df)}")
    if excluded:
        print(f"Excluded (no forecast): {excluded}")
    print(f"Total NPATMI 2024 (actual): {total_npatmi_2024:,.0f} B VND")
    print(f"Total NPATMI 2025F: {total_npatmi_2025f:,.0f} B VND")
    print(f"Total NPATMI 2026F: {total_npatmi_2026f:,.0f} B VND")
    print(f"Total Earning Growth 2025 YoY: {total_earning_growth_2025*100:+.1f}%")
    print(f"Total Earning Growth 2026 YoY: {total_earning_growth_2026*100:+.1f}%")

    return {
        'total_npatmi_2024': total_npatmi_2024,
        'total_npatmi_2025f': total_npatmi_2025f,
        'total_npatmi_2026f': total_npatmi_2026f,
        'total_earning_growth_2025': total_earning_growth_2025,
        'total_earning_growth_2026': total_earning_growth_2026,
        'valid_stock_count': len(valid_stocks),
        'excluded_stocks': excluded,
    }


def calculate_sector_earning_growth(individual_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate sector-level earning growth from individual stocks WITH VALID FORECAST ONLY.

    IMPORTANT: Only includes stocks that have complete forecast data (2025F, 2026F, growth rate).
    This ensures consistent comparison across years within each sector.

    Returns DataFrame with sector, total_earning_growth_2025, total_earning_growth_2026.
    """
    # Filter to only stocks with COMPLETE forecast data
    valid_df = individual_df[
        individual_df['npatmi_2025f'].notna() & (individual_df['npatmi_2025f'] > 0) &
        individual_df['npatmi_2026f'].notna() & (individual_df['npatmi_2026f'] > 0) &
        individual_df['npatmi_growth_yoy_2025'].notna() &
        (individual_df['npatmi_growth_yoy_2025'] > -1)
    ].copy()

    # Calculate 2024 actual for valid stocks
    valid_df['npatmi_2024_actual'] = valid_df['npatmi_2025f'] / (1 + valid_df['npatmi_growth_yoy_2025'])

    # Aggregate by sector - ONLY valid stocks (same stock set for all years)
    sector_totals = valid_df.groupby('sector').agg({
        'npatmi_2024_actual': 'sum',
        'npatmi_2025f': 'sum',
        'npatmi_2026f': 'sum',
        'symbol': 'count',  # Track valid stock count per sector
    }).reset_index()
    sector_totals = sector_totals.rename(columns={'symbol': 'valid_stock_count'})

    # Calculate growth rates using same stock set
    sector_totals['total_earning_growth_2025'] = np.where(
        sector_totals['npatmi_2024_actual'] > 0,
        (sector_totals['npatmi_2025f'] / sector_totals['npatmi_2024_actual']) - 1,
        np.nan
    )

    sector_totals['total_earning_growth_2026'] = np.where(
        sector_totals['npatmi_2025f'] > 0,
        (sector_totals['npatmi_2026f'] / sector_totals['npatmi_2025f']) - 1,
        np.nan
    )

    return sector_totals[['sector', 'total_earning_growth_2025', 'total_earning_growth_2026']]


def create_bsc_universal_row(individual_df: pd.DataFrame, sector_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create BSC Universal row with aggregated totals across all sectors.

    This row represents the entire BSC coverage universe (92 stocks).
    """
    # Calculate totals
    total_data = {
        'sector': 'BSC Universal',
        'symbol_count': len(individual_df),
        'total_market_cap': individual_df['market_cap'].sum(),
        'total_rev_2025f': individual_df['rev_2025f'].sum(),
        'total_rev_2026f': individual_df['rev_2026f'].sum(),
        'total_npatmi_2025f': individual_df['npatmi_2025f'].sum(),
        'total_npatmi_2026f': individual_df['npatmi_2026f'].sum(),
    }

    # Calculate total equity (from sector totals)
    total_data['total_equity_2025f'] = sector_df['total_equity_2025f'].sum()
    total_data['total_equity_2026f'] = sector_df['total_equity_2026f'].sum()

    # Calculate PE/PB forward
    total_data['pe_fwd_2025'] = total_data['total_market_cap'] / total_data['total_npatmi_2025f']
    total_data['pe_fwd_2026'] = total_data['total_market_cap'] / total_data['total_npatmi_2026f']
    total_data['pb_fwd_2025'] = total_data['total_market_cap'] / total_data['total_equity_2025f']
    total_data['pb_fwd_2026'] = total_data['total_market_cap'] / total_data['total_equity_2026f']

    # Calculate weighted averages for growth metrics
    total_data['avg_rev_growth_2025'] = individual_df['rev_growth_yoy_2025'].mean()
    total_data['avg_rev_growth_2026'] = individual_df['rev_growth_yoy_2026'].mean()
    total_data['avg_npatmi_growth_2025'] = individual_df['npatmi_growth_yoy_2025'].mean()
    total_data['avg_npatmi_growth_2026'] = individual_df['npatmi_growth_yoy_2026'].mean()

    # Calculate avg upside and ROE
    total_data['avg_upside_pct'] = individual_df['upside_pct'].mean()
    total_data['avg_roe_2025f'] = individual_df['roe_2025f'].mean()
    total_data['avg_roe_2026f'] = individual_df['roe_2026f'].mean()

    # Calculate total earning growth (market cap weighted)
    growth_data = calculate_total_profit_growth(individual_df)
    total_data['total_earning_growth_2025'] = growth_data['total_earning_growth_2025']
    total_data['total_earning_growth_2026'] = growth_data['total_earning_growth_2026']

    total_data['updated_at'] = datetime.now()

    return pd.DataFrame([total_data])


def update_sector_valuation(sector_df: pd.DataFrame, individual_df: pd.DataFrame) -> pd.DataFrame:
    """
    Update sector valuation with:
    1. Total earning growth columns (2025, 2026)
    2. BSC Universal row
    3. Rename BSC_index -> BSC Universal if exists
    """
    # Step 1: Calculate sector earning growth
    sector_growth = calculate_sector_earning_growth(individual_df)

    # Drop existing growth columns if present (avoid duplicate _x/_y suffix)
    cols_to_drop = [c for c in sector_df.columns if 'total_earning_growth' in c]
    if cols_to_drop:
        sector_df = sector_df.drop(columns=cols_to_drop)

    # Merge growth into sector_df
    result = sector_df.merge(sector_growth, on='sector', how='left')

    # Step 2: Rename BSC_index if exists
    if 'BSC_index' in result['sector'].values:
        result['sector'] = result['sector'].replace('BSC_index', 'BSC Universal')
        print("Renamed BSC_index -> BSC Universal")

    # Step 3: Remove existing BSC Universal row if present
    result = result[result['sector'] != 'BSC Universal']

    # Step 4: Create and add BSC Universal row
    bsc_universal = create_bsc_universal_row(individual_df, result)

    # Ensure columns match
    for col in result.columns:
        if col not in bsc_universal.columns:
            bsc_universal[col] = np.nan

    bsc_universal = bsc_universal[result.columns]

    # Append BSC Universal row
    result = pd.concat([result, bsc_universal], ignore_index=True)

    return result


def main():
    """Main execution."""
    print("=" * 60)
    print("BSC Forecast Profit Growth Analysis")
    print("=" * 60)

    # Load data
    individual_df, sector_df = load_data()

    # Print current sector columns
    print("\nCurrent sector columns:")
    print(sector_df.columns.tolist())

    # Update sector valuation
    updated_sector_df = update_sector_valuation(sector_df, individual_df)

    # Print updated columns
    print("\nUpdated sector columns:")
    print(updated_sector_df.columns.tolist())

    # Print BSC Universal row
    print("\n=== BSC Universal Row ===")
    bsc_row = updated_sector_df[updated_sector_df['sector'] == 'BSC Universal']
    print(bsc_row[['sector', 'symbol_count', 'total_market_cap', 'pe_fwd_2025', 'pe_fwd_2026',
                   'total_earning_growth_2025', 'total_earning_growth_2026']].to_string())

    # Print sector growth summary
    print("\n=== Sector Total Earning Growth ===")
    growth_cols = ['sector', 'total_earning_growth_2025', 'total_earning_growth_2026']
    print(updated_sector_df[growth_cols].to_string())

    # Save updated parquet
    output_path = DATA_DIR / "bsc_sector_valuation.parquet"
    updated_sector_df.to_parquet(output_path, index=False)
    print(f"\nSaved updated sector valuation to: {output_path}")

    print("\n" + "=" * 60)
    print("Analysis Complete")
    print("=" * 60)

    return updated_sector_df


if __name__ == "__main__":
    result = main()
