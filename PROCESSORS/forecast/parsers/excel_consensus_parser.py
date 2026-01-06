"""
Excel Consensus Parser
======================

Parse SSI_AI and HSC_AI sheets from Consensus.xlsx and update JSON files.

Usage:
    python PROCESSORS/forecast/parsers/excel_consensus_parser.py

Input:
    DATA/raw/forecast/Consensus.xlsx (sheets: HSC_AI, SSI_AI)

Output:
    DATA/processed/forecast/sources/ssi.json
    DATA/processed/forecast/sources/hcm.json
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


# Constants
EXCEL_PATH = Path("DATA/raw/forecast/Consensus.xlsx")
OUTPUT_DIR = Path("DATA/processed/forecast/sources")

# Mapping for sector lookup (from existing JSON or SectorRegistry)
SECTOR_LOOKUP_PATH = Path("DATA/processed/forecast/sources/bsc.json")


def load_sector_lookup() -> Dict[str, str]:
    """Load symbol -> sector mapping from BSC data."""
    if not SECTOR_LOOKUP_PATH.exists():
        return {}

    with open(SECTOR_LOOKUP_PATH, 'r', encoding='utf-8') as f:
        bsc_data = json.load(f)

    return {stock['symbol']: stock.get('sector', 'Unknown') for stock in bsc_data.get('stocks', [])}


def parse_sheet(xlsx: pd.ExcelFile, sheet_name: str) -> List[Dict[str, Any]]:
    """
    Parse a single sheet from Excel file.

    Args:
        xlsx: ExcelFile object
        sheet_name: Name of sheet to parse

    Returns:
        List of stock dictionaries
    """
    df = pd.read_excel(xlsx, sheet_name=sheet_name)

    # Normalize column names
    df.columns = df.columns.str.strip()

    # Expected columns mapping
    col_map = {
        'Symbol': 'symbol',
        'NPATMI_2025F': 'npatmi_2025f',
        'NPATMI_2026F': 'npatmi_2026f',
        'NPATMI_2027F': 'npatmi_2027f',
        'Target price': 'target_price'
    }

    # Rename columns
    df = df.rename(columns=col_map)

    # Load sector lookup
    sector_lookup = load_sector_lookup()

    stocks = []
    for _, row in df.iterrows():
        symbol = str(row.get('symbol', '')).strip().upper()
        if not symbol or pd.isna(row.get('symbol')):
            continue

        # Convert NPATMI from VND to Billion VND
        def to_billion(val):
            if pd.isna(val):
                return None
            return round(float(val) / 1e9, 2)

        stock = {
            'symbol': symbol,
            'sector': sector_lookup.get(symbol, 'Unknown'),
            'entity_type': 'COMPANY',  # Default, can be enhanced later
            'target_price': float(row.get('target_price')) if pd.notna(row.get('target_price')) else None,
            'current_price': None,  # Will be fetched from market data
            'rating': None,  # Not in Excel, keep existing if any
            'npatmi_2025f': to_billion(row.get('npatmi_2025f')),
            'npatmi_2026f': to_billion(row.get('npatmi_2026f')),
            'npatmi_2027f': to_billion(row.get('npatmi_2027f')),
            'eps_2025f': None,
            'eps_2026f': None,
            'eps_2027f': None,
            'pe_2025f': None,
            'pe_2026f': None,
            'pe_2027f': None,
            'notes': ''
        }
        stocks.append(stock)

    return stocks


def merge_with_existing(new_stocks: List[Dict], existing_path: Path) -> List[Dict]:
    """
    Merge new data with existing JSON, preserving ratings and other fields.

    Args:
        new_stocks: New stock data from Excel
        existing_path: Path to existing JSON file

    Returns:
        Merged stock list
    """
    if not existing_path.exists():
        return new_stocks

    with open(existing_path, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)

    # Create lookup from existing data
    existing_lookup = {s['symbol']: s for s in existing_data.get('stocks', [])}

    # Merge: update existing with new data, preserve rating
    merged = []
    for stock in new_stocks:
        symbol = stock['symbol']
        if symbol in existing_lookup:
            existing = existing_lookup[symbol]
            # Preserve rating if exists
            if existing.get('rating'):
                stock['rating'] = existing['rating']
            # Preserve sector if new is Unknown
            if stock.get('sector') == 'Unknown' and existing.get('sector'):
                stock['sector'] = existing['sector']
        merged.append(stock)

    return merged


def save_json(source: str, stocks: List[Dict], output_path: Path) -> None:
    """
    Save stocks to JSON file with metadata.

    Args:
        source: Source name (ssi, hcm)
        stocks: List of stock dictionaries
        output_path: Output file path
    """
    data = {
        'source': source,
        'updated_at': datetime.now().strftime('%d/%m/%y'),
        'schema_version': '2025-2027',
        'stocks': stocks
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(stocks)} stocks to {output_path}")


def main():
    """Main entry point."""
    if not EXCEL_PATH.exists():
        print(f"❌ Excel file not found: {EXCEL_PATH}")
        return

    print(f"📖 Reading {EXCEL_PATH}...")
    xlsx = pd.ExcelFile(EXCEL_PATH)

    # Parse HSC_AI -> hcm.json
    print("\n📊 Parsing HSC_AI sheet...")
    hsc_stocks = parse_sheet(xlsx, 'HSC_AI')
    hsc_stocks = merge_with_existing(hsc_stocks, OUTPUT_DIR / 'hcm.json')
    save_json('hcm', hsc_stocks, OUTPUT_DIR / 'hcm.json')

    # Parse SSI_AI -> ssi.json
    print("\n📊 Parsing SSI_AI sheet...")
    ssi_stocks = parse_sheet(xlsx, 'SSI_AI')
    ssi_stocks = merge_with_existing(ssi_stocks, OUTPUT_DIR / 'ssi.json')
    save_json('ssi', ssi_stocks, OUTPUT_DIR / 'ssi.json')

    print("\n✅ Done! JSON files updated.")

    # Summary
    print("\n📋 Summary:")
    print(f"   HSC: {len(hsc_stocks)} stocks")
    print(f"   SSI: {len(ssi_stocks)} stocks")


if __name__ == '__main__':
    main()
