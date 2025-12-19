#!/usr/bin/env python3
"""
BSC Forecast Excel Re-read Script
==================================

Manual script to re-read BSC Forecast Excel and regenerate parquet files.

Use this when BSC Research updates the forecast Excel file with new data.

Usage:
    python3 PROCESSORS/forecast/update_bsc_excel.py

Updated: 2025-12-17
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path - works from any directory
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Change to project root to ensure relative paths work
os.chdir(project_root)

import pandas as pd
from PROCESSORS.forecast.bsc_forecast_processor import BSCForecastProcessor


def verify_update(parquet_path: Path, symbol: str = "HDB") -> dict:
    """Verify the parquet was updated correctly."""
    if not parquet_path.exists():
        return {"error": "Parquet file not found"}

    df = pd.read_parquet(parquet_path)
    row = df[df['symbol'] == symbol]

    if len(row) == 0:
        return {"error": f"{symbol} not found in parquet"}

    return {
        "symbol": symbol,
        "target_price": row['target_price'].values[0],
        "current_price": row['current_price'].values[0],
        "updated_at": str(row['updated_at'].values[0]),
        "file_mtime": datetime.fromtimestamp(parquet_path.stat().st_mtime).isoformat()
    }


def main():
    """Re-read BSC Forecast Excel and regenerate parquet files."""
    print("=" * 60)
    print("BSC Forecast Excel Re-read")
    print("=" * 60)
    print()
    print(f"Project Root: {project_root}")
    print(f"Working Dir:  {os.getcwd()}")
    print()

    # Check if Excel file exists
    excel_path = project_root / "DATA" / "processed" / "forecast" / "BSC Forecast.xlsx"
    parquet_path = project_root / "DATA" / "processed" / "forecast" / "bsc" / "bsc_individual.parquet"

    if not excel_path.exists():
        print(f"ERROR: Excel file not found at {excel_path}")
        print("Please ensure the BSC Forecast Excel file exists.")
        sys.exit(1)

    # Show BEFORE state
    print("=" * 60)
    print("BEFORE UPDATE")
    print("=" * 60)
    before = verify_update(parquet_path)
    if "error" not in before:
        print(f"  HDB Target Price: {before['target_price']:,.0f}")
        print(f"  Last Updated: {before['updated_at']}")
    else:
        print(f"  {before['error']}")
    print()

    print(f"Excel file: {excel_path}")
    print(f"Excel mtime: {datetime.fromtimestamp(excel_path.stat().st_mtime).isoformat()}")
    print()

    # Run processor
    try:
        processor = BSCForecastProcessor(project_root)
        result = processor.run(generate_readme=True)
    except Exception as e:
        print(f"ERROR: Failed to run processor: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Print summary
    individual = result['individual']
    sector = result['sector']

    print()
    print("=" * 60)
    print("AFTER UPDATE")
    print("=" * 60)
    after = verify_update(parquet_path)
    if "error" not in after:
        print(f"  HDB Target Price: {after['target_price']:,.0f}")
        print(f"  Updated At: {after['updated_at']}")
        print(f"  File mtime: {after['file_mtime']}")
    else:
        print(f"  {after['error']}")
    print()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()

    print(f"Individual Stocks Processed: {len(individual)}")
    print(f"Sectors Processed: {len(sector)}")
    print()

    print("Rating Distribution:")
    print("-" * 30)
    for rating, count in individual['rating'].value_counts().items():
        print(f"  {rating}: {count}")
    print()

    print("Top 10 Upside Stocks:")
    print("-" * 50)
    top_upside = individual.nlargest(10, 'upside_pct')[['symbol', 'target_price', 'current_price', 'upside_pct', 'rating']]
    for _, row in top_upside.iterrows():
        upside = row['upside_pct'] * 100 if not pd.isna(row['upside_pct']) else 0
        print(f"  {row['symbol']:6} | Target: {row['target_price']:>8,.0f} | Current: {row['current_price']:>8,.0f} | Upside: {upside:>+6.1f}% | {row['rating']}")
    print()

    print("Sector PE/PB Forward 2025:")
    print("-" * 60)
    print(f"{'Sector':<25} {'PE FWD 2025':>12} {'PE FWD 2026':>12} {'PB FWD 2025':>12}")
    print("-" * 60)
    for _, row in sector.sort_values('pe_fwd_2025').iterrows():
        pe_25 = f"{row['pe_fwd_2025']:.1f}" if not pd.isna(row['pe_fwd_2025']) else "N/A"
        pe_26 = f"{row['pe_fwd_2026']:.1f}" if not pd.isna(row['pe_fwd_2026']) else "N/A"
        pb_25 = f"{row['pb_fwd_2025']:.2f}" if not pd.isna(row['pb_fwd_2025']) else "N/A"
        sector_name = row['sector']
        print(f"{sector_name:<25} {pe_25:>12} {pe_26:>12} {pb_25:>12}")
    print()

    print("Output files generated:")
    print(f"  - DATA/processed/forecast/bsc/bsc_individual.parquet")
    print(f"  - DATA/processed/forecast/bsc/bsc_sector_valuation.parquet")
    print(f"  - DATA/processed/forecast/bsc/bsc_combined.parquet")
    print(f"  - DATA/processed/forecast/bsc/README.md")
    print()
    print("✅ Done!")


if __name__ == "__main__":
    main()
