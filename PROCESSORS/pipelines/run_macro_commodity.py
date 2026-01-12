#!/usr/bin/env python3
"""
Standalone Macro & Commodity Update Script
==========================================
Run macro and commodity data updates independently.

Usage:
    # Daily incremental update (last 30 days)
    python3 PROCESSORS/pipelines/run_macro_commodity.py

    # Full migration from 2015
    python3 PROCESSORS/pipelines/run_macro_commodity.py --migrate

    # Show current data status only
    python3 PROCESSORS/pipelines/run_macro_commodity.py --status
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import argparse
import pandas as pd

# Paths
SCRIPT_DIR = Path(__file__).parent
DAILY_SCRIPT = SCRIPT_DIR / "daily" / "daily_macro_commodity.py"
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_FILE = PROJECT_ROOT / "DATA" / "processed" / "macro_commodity" / "macro_commodity_unified.parquet"


def show_status():
    """Show current macro/commodity data status."""
    print("\n" + "=" * 60)
    print("📊 MACRO & COMMODITY DATA STATUS")
    print("=" * 60)

    if not DATA_FILE.exists():
        print("❌ Data file not found!")
        print(f"   Expected: {DATA_FILE}")
        print("\n   Run: python3 PROCESSORS/pipelines/run_macro_commodity.py --migrate")
        return False

    df = pd.read_parquet(DATA_FILE)
    df['date'] = pd.to_datetime(df['date'])

    latest = df['date'].max()
    oldest = df['date'].min()
    categories = df['category'].unique()

    print(f"\n📁 File: {DATA_FILE.name}")
    print(f"   Size: {DATA_FILE.stat().st_size / (1024*1024):.2f} MB")
    print(f"\n📅 Date Range: {oldest.strftime('%Y-%m-%d')} → {latest.strftime('%Y-%m-%d')}")
    print(f"📈 Total Records: {len(df):,}")
    print(f"📂 Categories: {len(categories)}")

    print("\n📋 By Category:")
    for cat in sorted(categories):
        cat_df = df[df['category'] == cat]
        symbols = cat_df['symbol'].nunique()
        cat_latest = cat_df['date'].max().strftime('%Y-%m-%d')
        print(f"   • {cat:<12} | {symbols:>3} symbols | Latest: {cat_latest}")

    # Check freshness
    days_old = (datetime.now() - latest).days
    print(f"\n🕐 Data Age: {days_old} day(s) old")

    if days_old <= 1:
        print("   ✅ UP TO DATE")
    elif days_old <= 3:
        print("   ⚠️  Slightly outdated (may be weekend)")
    else:
        print("   ❌ OUTDATED - Run update!")

    print("=" * 60 + "\n")
    return True


def run_update(migrate: bool = False):
    """Run macro/commodity update script."""
    print("\n" + "=" * 60)
    if migrate:
        print("🚀 FULL MIGRATION: Macro & Commodity Data")
        print("   Fetching data from 2015-01-01...")
    else:
        print("🔄 DAILY UPDATE: Macro & Commodity Data")
        print("   Fetching last 30 days...")
    print("=" * 60 + "\n")

    start = datetime.now()

    cmd = [sys.executable, str(DAILY_SCRIPT)]
    if migrate:
        cmd.append("--migrate")

    result = subprocess.run(cmd, capture_output=False)
    duration = (datetime.now() - start).total_seconds()

    print("\n" + "=" * 60)
    if result.returncode == 0:
        print(f"✅ SUCCESS - Completed in {duration:.1f}s")
    else:
        print(f"❌ FAILED - Exit code: {result.returncode}")
    print("=" * 60 + "\n")

    # Show updated status
    show_status()

    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description='Macro & Commodity Data Update',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Daily update (incremental)
  python3 PROCESSORS/pipelines/run_macro_commodity.py

  # Full migration from 2015
  python3 PROCESSORS/pipelines/run_macro_commodity.py --migrate

  # Check current status
  python3 PROCESSORS/pipelines/run_macro_commodity.py --status
        """
    )

    parser.add_argument('--migrate', action='store_true',
                        help='Full migration from 2015 (cleans up old folders)')
    parser.add_argument('--status', action='store_true',
                        help='Show current data status only')

    args = parser.parse_args()

    if args.status:
        show_status()
    else:
        success = run_update(migrate=args.migrate)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
