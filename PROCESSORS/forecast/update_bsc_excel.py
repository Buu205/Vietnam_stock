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
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from PROCESSORS.forecast.bsc_forecast_processor import BSCForecastProcessor


def main():
    """Re-read BSC Forecast Excel and regenerate parquet files."""
    print("=" * 60)
    print("BSC Forecast Excel Re-read")
    print("=" * 60)
    print()

    # Check if Excel file exists
    excel_path = project_root / "DATA" / "processed" / "forecast" / "BSC Forecast.xlsx"
    if not excel_path.exists():
        print(f"ERROR: Excel file not found at {excel_path}")
        print("Please ensure the BSC Forecast Excel file exists.")
        sys.exit(1)

    print(f"Excel file: {excel_path}")
    print()

    # Run processor
    processor = BSCForecastProcessor(project_root)
    result = processor.run(generate_readme=True)

    # Print summary
    individual = result['individual']
    sector = result['sector']

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
    print(f"{'Sector':<15} {'PE FWD 2025':>12} {'PE FWD 2026':>12} {'PB FWD 2025':>12}")
    print("-" * 60)
    for _, row in sector.sort_values('pe_fwd_2025').iterrows():
        pe_25 = f"{row['pe_fwd_2025']:.1f}" if not pd.isna(row['pe_fwd_2025']) else "N/A"
        pe_26 = f"{row['pe_fwd_2026']:.1f}" if not pd.isna(row['pe_fwd_2026']) else "N/A"
        pb_25 = f"{row['pb_fwd_2025']:.2f}" if not pd.isna(row['pb_fwd_2025']) else "N/A"
        print(f"{row['bsc_sector']:<15} {pe_25:>12} {pe_26:>12} {pb_25:>12}")
    print()

    print("Output files generated:")
    print(f"  - DATA/processed/forecast/bsc/bsc_individual.parquet")
    print(f"  - DATA/processed/forecast/bsc/bsc_sector_valuation.parquet")
    print(f"  - DATA/processed/forecast/bsc/bsc_combined.parquet")
    print(f"  - DATA/processed/forecast/bsc/README.md")
    print()
    print("Done!")


if __name__ == "__main__":
    import pandas as pd
    main()
