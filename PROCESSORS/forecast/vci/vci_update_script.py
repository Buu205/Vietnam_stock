#!/usr/bin/env python3
"""
Fetch Vietcap IQ Coverage Universe và lưu parquet
Output: DATA/processed/forecast/VCI/vci_coverage_universe.parquet
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent.parent.parent  # vci -> forecast -> PROCESSORS -> PROJECT_ROOT
OUTPUT_DIR = PROJECT_ROOT / "DATA/processed/forecast/VCI"
OUTPUT_FILE = OUTPUT_DIR / "vci_coverage_universe.parquet"
JSON_BACKUP = OUTPUT_DIR / "vci_coverage_universe.json"


def flatten_nested_dict(data: list) -> list:
    """
    Flatten nested dicts (pe, pb, roe, etc.) thành columns riêng

    Input:  {"pe": {"2025F": 6.96, "2026F": 5.92}}
    Output: {"pe_2025F": 6.96, "pe_2026F": 5.92}
    """
    flattened = []
    for item in data:
        flat_item = {}
        for key, value in item.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat_item[f"{key}_{sub_key}"] = sub_value
            else:
                flat_item[key] = value
        flattened.append(flat_item)
    return flattened


def fetch_and_save():
    """Fetch coverage universe và lưu parquet"""
    from .vietcap_client import fetch_coverage_universe

    print("🔄 Fetching Vietcap IQ Coverage Universe...")

    data = fetch_coverage_universe()

    if not data:
        print("❌ Không fetch được data!")
        return False

    print(f"✅ Got {len(data)} tickers")

    # Flatten nested dicts
    print("📦 Flattening nested data...")
    flat_data = flatten_nested_dict(data)

    # Convert to DataFrame
    df = pd.DataFrame(flat_data)

    # Add metadata
    df['fetch_date'] = datetime.now().strftime('%Y-%m-%d')
    df['fetch_timestamp'] = datetime.now().isoformat()

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save parquet
    df.to_parquet(OUTPUT_FILE, index=False)
    print(f"💾 Saved parquet: {OUTPUT_FILE}")
    print(f"   Rows: {len(df)}, Columns: {len(df.columns)}")

    # Save JSON backup
    with open(JSON_BACKUP, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved JSON backup: {JSON_BACKUP}")

    # Print sample
    print("\n📊 Sample data:")
    # Show available columns dynamically
    display_cols = ['ticker', 'sector', 'rating', 'targetPrice']
    for col in ['pe_2026F', 'pe_2025F', 'roe_2026F', 'roe_2025F']:
        if col in df.columns:
            display_cols.append(col)
            break
    print(df[display_cols].head(10).to_string())

    # Print columns
    print(f"\n📋 Columns ({len(df.columns)}):")
    print(df.columns.tolist())

    return True


def load_data() -> pd.DataFrame:
    """Load data từ parquet"""
    if OUTPUT_FILE.exists():
        return pd.read_parquet(OUTPUT_FILE)
    return None


# ============ CLI ============
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--load":
        # Load mode
        df = load_data()
        if df is not None:
            print(f"✅ Loaded {len(df)} rows from {OUTPUT_FILE}")
            print(df.head())
        else:
            print("❌ No data file found")
    else:
        # Fetch mode (default)
        success = fetch_and_save()
        if success:
            print("\n✅ Done!")
        else:
            print("\n❌ Failed!")
            sys.exit(1)
