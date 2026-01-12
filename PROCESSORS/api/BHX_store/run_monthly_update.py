#!/usr/bin/env python3
"""
BHX Monthly Update Script
Run this monthly to fetch new store data and update tracking.

Usage:
    python3 run_monthly_update.py           # Full update: fetch + add to tracking
    python3 run_monthly_update.py --fetch   # Only fetch new data to raw database
    python3 run_monthly_update.py --update  # Only update tracking from latest snapshot
    python3 run_monthly_update.py --history # Show database history

Output files (in BSC_masterfile/):
    - bhx_raw_snapshots.parquet: Cumulative API snapshots
    - bhx_monthly_tracking.parquet: Monthly tracking pivot table
"""
import argparse
from bhx_store import (
    fetch_all_stores,
    append_to_raw_db,
    update_monthly_tracking,
    print_snapshot_summary,
    print_monthly_summary,
    print_db_history,
    RAW_DB_PATH,
    TRACKING_PATH
)


def main():
    parser = argparse.ArgumentParser(description='BHX Monthly Update')
    parser.add_argument('--fetch', action='store_true', help='Only fetch new data')
    parser.add_argument('--update', action='store_true', help='Only update tracking')
    parser.add_argument('--history', action='store_true', help='Show database history')
    parser.add_argument('--date', type=str, help='Date column (DD/MM/YYYY) for tracking')
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("BHX MONTHLY UPDATE")
    print("=" * 60)
    print(f"Output: {RAW_DB_PATH.parent}")

    # Show history only
    if args.history:
        print_db_history()
        print_monthly_summary()
        return

    # Fetch only
    if args.fetch:
        new_df = fetch_all_stores()
        append_to_raw_db(new_df)
        print_snapshot_summary(new_df)
        print_db_history()
        return

    # Update tracking only
    if args.update:
        update_monthly_tracking(args.date)
        print_monthly_summary()
        return

    # Default: Full update (fetch + update tracking)
    print("\n[1/2] Fetching store data from API...")
    new_df = fetch_all_stores()
    append_to_raw_db(new_df)
    print_snapshot_summary(new_df)

    print("\n[2/2] Updating monthly tracking...")
    update_monthly_tracking(args.date)
    print_monthly_summary()

    print("\n" + "=" * 60)
    print("UPDATE COMPLETE")
    print(f"  Raw data: {RAW_DB_PATH}")
    print(f"  Tracking: {TRACKING_PATH}")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
