#!/usr/bin/env python3
"""
Initialize source JSONs from existing data.

One-time migration script to create normalized JSON files from:
- BSC: bsc_individual.parquet
- VCI: vci_coverage_universe.parquet
- HCM: hcm_raw.json (extracted)
- SSI: ssi_raw.json (extracted)

Output: DATA/processed/forecast/sources/{source}.json

Run once to bootstrap, then edit JSONs directly for updates.
"""

import json
from pathlib import Path
from datetime import datetime
import pandas as pd

# Paths
PROJECT_ROOT = Path("/Users/buuphan/Dev/Vietnam_dashboard")
SOURCES_DIR = PROJECT_ROOT / "DATA" / "processed" / "forecast" / "sources"
RAW_FORECAST = PROJECT_ROOT / "DATA" / "raw" / "forecast"

# Ensure output dir exists
SOURCES_DIR.mkdir(parents=True, exist_ok=True)


def create_json_template(source: str, stocks: list) -> dict:
    """Create normalized JSON structure."""
    return {
        "source": source,
        "updated_at": datetime.now().strftime("%d/%m/%y"),
        "schema_version": "2026-2027",
        "stocks": stocks
    }


def normalize_stock(row: dict, source: str) -> dict:
    """Normalize a stock record to standard schema."""
    # Map various field names to standard schema
    stock = {
        "symbol": str(row.get('symbol', row.get('ticker', ''))).upper(),
        "sector": row.get('sector', ''),
        "entity_type": row.get('entity_type', 'COMPANY'),
        "target_price": row.get('target_price', row.get('targetPrice', None)),
        "current_price": row.get('current_price', row.get('currentPrice', None)),
        "rating": row.get('rating', ''),
        "npatmi_2026f": None,
        "npatmi_2027f": None,
        "eps_2026f": None,
        "eps_2027f": None,
        "pe_2026f": None,
        "pe_2027f": None,
        "notes": ""
    }

    # Handle different source field mappings
    # RULE: Keep original years - DO NOT shift! 2026F means 2026F forecast.
    if source == 'bsc':
        # BSC Excel has 2025F/2026F - keep as-is, no 2027F available
        stock['npatmi_2026f'] = row.get('npatmi_2026f', row.get('npatmi_2026'))
        stock['npatmi_2027f'] = None  # BSC doesn't have 2027F forecast yet
        stock['eps_2026f'] = row.get('eps_2026', row.get('eps_2026f'))
        stock['eps_2027f'] = None  # BSC doesn't have 2027F
        stock['pe_2026f'] = row.get('pe_fwd_2026', row.get('pe_2026f'))
        stock['pe_2027f'] = None  # BSC doesn't have 2027F

    elif source == 'vci':
        # VCI API has 2026F/2027F - keep as-is
        stock['npatmi_2026f'] = row.get('npatmi_2026F', row.get('npatmi_2026f'))
        stock['npatmi_2027f'] = row.get('npatmi_2027F', row.get('npatmi_2027f'))
        stock['eps_2026f'] = row.get('eps_2026F', row.get('eps_2026f'))
        stock['eps_2027f'] = row.get('eps_2027F', row.get('eps_2027f'))
        stock['pe_2026f'] = row.get('pe_2026F', row.get('pe_2026f'))
        stock['pe_2027f'] = row.get('pe_2027F', row.get('pe_2027f'))

    else:  # hcm, ssi
        # Raw extracts - check what years are available
        stock['npatmi_2026f'] = row.get('npatmi_2026f', row.get('npatmi_2026F'))
        stock['npatmi_2027f'] = row.get('npatmi_2027f', row.get('npatmi_2027F'))
        stock['eps_2026f'] = row.get('eps_2026f', row.get('eps_2026F'))
        stock['eps_2027f'] = row.get('eps_2027f', row.get('eps_2027F'))
        stock['pe_2026f'] = row.get('pe_2026f', row.get('pe_2026F'))
        stock['pe_2027f'] = row.get('pe_2027f', row.get('pe_2027F'))

    # Convert None to null-safe values
    for key in ['target_price', 'current_price', 'npatmi_2026f', 'npatmi_2027f',
                'eps_2026f', 'eps_2027f', 'pe_2026f', 'pe_2027f']:
        val = stock[key]
        if pd.isna(val) or val == 'nan' or val == '':
            stock[key] = None
        elif val is not None:
            try:
                stock[key] = float(val)
            except (ValueError, TypeError):
                stock[key] = None

    return stock


def init_bsc_json():
    """Create bsc.json from bsc_individual.parquet."""
    print("\n📦 Creating bsc.json...")

    parquet_path = PROJECT_ROOT / "DATA" / "processed" / "forecast" / "bsc" / "bsc_individual.parquet"
    if not parquet_path.exists():
        print(f"  ❌ Not found: {parquet_path}")
        return

    df = pd.read_parquet(parquet_path)
    stocks = [normalize_stock(row.to_dict(), 'bsc') for _, row in df.iterrows()]

    data = create_json_template('bsc', stocks)
    output_path = SOURCES_DIR / "bsc.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Saved: {output_path} ({len(stocks)} stocks)")


def init_vci_json():
    """Create vci.json from vci_coverage_universe.parquet."""
    print("\n📦 Creating vci.json...")

    parquet_path = PROJECT_ROOT / "DATA" / "processed" / "forecast" / "VCI" / "vci_coverage_universe.parquet"
    if not parquet_path.exists():
        print(f"  ❌ Not found: {parquet_path}")
        return

    df = pd.read_parquet(parquet_path)
    stocks = [normalize_stock(row.to_dict(), 'vci') for _, row in df.iterrows()]

    data = create_json_template('vci', stocks)
    output_path = SOURCES_DIR / "vci.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Saved: {output_path} ({len(stocks)} stocks)")


def init_hcm_json():
    """Create hcm.json from hcm_raw.json."""
    print("\n📦 Creating hcm.json...")

    raw_path = RAW_FORECAST / "hcm" / "extracted" / "hcm_raw.json"
    if not raw_path.exists():
        print(f"  ❌ Not found: {raw_path}")
        return

    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # Handle various raw formats
    raw_stocks = raw_data if isinstance(raw_data, list) else raw_data.get('stocks', raw_data.get('data', []))
    stocks = [normalize_stock(s, 'hcm') for s in raw_stocks]

    data = create_json_template('hcm', stocks)
    output_path = SOURCES_DIR / "hcm.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Saved: {output_path} ({len(stocks)} stocks)")


def init_ssi_json():
    """Create ssi.json from ssi_raw.json."""
    print("\n📦 Creating ssi.json...")

    raw_path = RAW_FORECAST / "ssi" / "extracted" / "ssi_raw.json"
    if not raw_path.exists():
        print(f"  ❌ Not found: {raw_path}")
        return

    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # Handle various raw formats
    raw_stocks = raw_data if isinstance(raw_data, list) else raw_data.get('stocks', raw_data.get('data', []))
    stocks = [normalize_stock(s, 'ssi') for s in raw_stocks]

    data = create_json_template('ssi', stocks)
    output_path = SOURCES_DIR / "ssi.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Saved: {output_path} ({len(stocks)} stocks)")


def main():
    print("=" * 60)
    print("Initializing Source JSONs from Existing Data")
    print("=" * 60)

    init_bsc_json()
    init_vci_json()
    init_hcm_json()
    init_ssi_json()

    print("\n" + "=" * 60)
    print("Source JSONs initialized!")
    print(f"Location: {SOURCES_DIR}")
    print("=" * 60)

    # List created files
    print("\nCreated files:")
    for f in SOURCES_DIR.glob("*.json"):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
