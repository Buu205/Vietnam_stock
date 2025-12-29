"""
Update monthly tracking with new data
Compares current API snapshot with previous month to calculate continuing/new stores
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys


def load_monthly_tracking():
    """Load existing monthly tracking data"""
    file_path = Path(__file__).parent / "bhx_monthly_tracking.parquet"

    if not file_path.exists():
        print("❌ Monthly tracking file not found!")
        print("   Run: python3 create_monthly_template.py first")
        sys.exit(1)

    df = pd.read_parquet(file_path)
    print(f"✅ Loaded {len(df)} records from {file_path.name}")
    return df


def load_current_snapshot(fetch_date=None):
    """Load snapshot from cumulative raw database

    Args:
        fetch_date: Optional date string (YYYY-MM-DD). If None, loads latest snapshot.
    """
    raw_db_path = Path(__file__).parent / "bhx_raw_snapshots.parquet"

    if not raw_db_path.exists():
        print("❌ Raw database not found!")
        print("   Run: python3 fetch_bhx_stores_refactored.py first")
        sys.exit(1)

    # Load full database
    df_all = pd.read_parquet(raw_db_path)

    # Get latest snapshot if date not specified
    if fetch_date is None:
        fetch_date = df_all['fetch_date'].max()

    # Filter by fetch_date
    df = df_all[df_all['fetch_date'] == fetch_date].copy()

    if df.empty:
        print(f"❌ No snapshot found for date: {fetch_date}")
        available_dates = df_all['fetch_date'].unique().tolist()
        print(f"   Available dates: {available_dates}")
        sys.exit(1)

    print(f"✅ Loaded snapshot: {fetch_date} ({len(df):,} stores)")
    return df, fetch_date.replace('-', '')


def compare_with_previous_month(current_snapshot_df, previous_month_df):
    """
    Compare current snapshot with previous month data to calculate:
    - Continuing stores (in both)
    - New stores (only in current)
    - Closed stores (only in previous)
    """
    # Get previous month's total by province
    prev_totals = previous_month_df.groupby('province')['total'].sum().to_dict()

    # Count current stores by province from snapshot
    current_counts = current_snapshot_df['provinceName'].value_counts().to_dict()

    # Calculate changes
    changes = []
    for province in set(list(prev_totals.keys()) + list(current_counts.keys())):
        prev_total = prev_totals.get(province, 0)
        curr_total = current_counts.get(province, 0)

        # Continuing = previous month total (assuming no closures)
        # New = current - previous
        # This is simplified - ideally compare storeId sets

        continuing = min(prev_total, curr_total)
        new = max(0, curr_total - prev_total)
        total = curr_total
        pct_new = (new / total * 100) if total > 0 else 0

        changes.append({
            'province': province,
            'continuing': continuing,
            'new': new,
            'total': total,
            'pct_new': pct_new
        })

    return pd.DataFrame(changes)


def add_month_data(tracking_df, new_month_df, month_str, month_name):
    """Add new month data to tracking dataframe"""
    new_month_df = new_month_df.copy()
    new_month_df['month'] = month_str
    new_month_df['month_name'] = month_name

    # Append to existing data
    updated_df = pd.concat([tracking_df, new_month_df], ignore_index=True)

    return updated_df


def manual_entry_mode():
    """Manual entry mode for custom data input"""
    print("\n" + "="*80)
    print("MANUAL ENTRY MODE")
    print("="*80)

    print("\nEnter month (YYYY-MM): ", end='')
    month_str = input().strip()

    print("Enter month name (e.g., 'January 2025'): ", end='')
    month_name = input().strip()

    print("\nEnter province data (one per line, format: Province|Continuing|New|Total)")
    print("Example: TP. Hồ Chí Minh, Bà Rịa - Vũng Tàu|688|129|817")
    print("Enter empty line to finish:")

    data = []
    while True:
        line = input().strip()
        if not line:
            break

        try:
            parts = line.split('|')
            if len(parts) != 4:
                print("   ❌ Invalid format, skipping...")
                continue

            province, continuing, new, total = parts
            continuing = float(continuing)
            new = float(new)
            total = float(total)
            pct_new = (new / total * 100) if total > 0 else 0

            data.append({
                'province': province.strip(),
                'continuing': continuing,
                'new': new,
                'total': total,
                'pct_new': pct_new
            })
            print(f"   ✅ Added: {province.strip()}")

        except ValueError as e:
            print(f"   ❌ Error: {e}, skipping...")

    if not data:
        print("\n❌ No data entered!")
        return None

    df = pd.DataFrame(data)
    df['month'] = month_str
    df['month_name'] = month_name

    return df


def save_updated_data(df):
    """Save updated monthly tracking data"""
    output_path = Path(__file__).parent / "bhx_monthly_tracking.parquet"
    df.to_parquet(output_path, index=False, compression='snappy')
    print(f"\n✅ Saved updated data: {output_path.name} ({len(df):,} rows)")


def print_summary(df, month_str):
    """Print summary for specific month"""
    month_df = df[df['month'] == month_str]

    if month_df.empty:
        print(f"\n❌ No data found for month: {month_str}")
        return

    print("\n" + "="*80)
    print(f"SUMMARY: {month_df['month_name'].iloc[0]} ({month_str})")
    print("="*80)

    total_continuing = month_df['continuing'].sum()
    total_new = month_df['new'].sum()
    total_stores = month_df['total'].sum()
    pct_new = (total_new / total_stores * 100) if total_stores > 0 else 0

    print(f"\nOverall:")
    print(f"   Continuing stores: {total_continuing:>7,.0f}")
    print(f"   New stores:        {total_new:>7,.0f}")
    print(f"   Total stores:      {total_stores:>7,.0f}")
    print(f"   % New:             {pct_new:>7.1f}%")

    print(f"\nTop 10 Provinces (New Stores):")
    top10 = month_df.nlargest(10, 'new')[['province', 'continuing', 'new', 'total', 'pct_new']]

    print(f"\n{'Province':<40} {'Cont':>6} {'New':>6} {'Total':>6} {'% New':>7}")
    print("-" * 75)

    for _, row in top10.iterrows():
        print(f"{row['province'][:40]:<40} {row['continuing']:>6.0f} {row['new']:>6.0f} "
              f"{row['total']:>6.0f} {row['pct_new']:>6.1f}%")

    print("="*80)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Update monthly store tracking')
    parser.add_argument('--mode', choices=['auto', 'manual'], default='auto',
                        help='Update mode: auto (from snapshot) or manual (input data)')
    parser.add_argument('--month', type=str, help='Month in YYYY-MM format (for auto mode)')
    parser.add_argument('--name', type=str, help='Month name like "January 2025" (for auto mode)')

    args = parser.parse_args()

    print("\n" + "="*80)
    print("MONTHLY DATA UPDATE")
    print("="*80)

    # Load existing tracking data
    tracking_df = load_monthly_tracking()

    if args.mode == 'manual':
        # Manual entry mode
        new_month_df = manual_entry_mode()

        if new_month_df is None:
            sys.exit(1)

        month_str = new_month_df['month'].iloc[0]
        month_name = new_month_df['month_name'].iloc[0]

    else:
        # Auto mode - compare with snapshot
        snapshot_df, snapshot_date = load_current_snapshot()

        # Get previous month data
        latest_month = tracking_df['month'].max()
        prev_month_df = tracking_df[tracking_df['month'] == latest_month]

        print(f"\nPrevious month: {latest_month}")
        print(f"Snapshot date: {snapshot_date}")

        # Determine new month from args or snapshot date
        if args.month:
            month_str = args.month
            month_name = args.name or month_str
        else:
            # Auto-detect from snapshot date
            snapshot_dt = datetime.strptime(snapshot_date, '%Y%m%d')
            month_str = snapshot_dt.strftime('%Y-%m')
            month_name = snapshot_dt.strftime('%B %Y')

        print(f"New month: {month_str} ({month_name})")

        # Compare and calculate changes
        print("\nCalculating changes...")
        new_month_df = compare_with_previous_month(snapshot_df, prev_month_df)

    # Add new month to tracking
    updated_df = add_month_data(tracking_df, new_month_df, month_str, month_name)

    # Save
    save_updated_data(updated_df)

    # Print summary
    print_summary(updated_df, month_str)

    print("\n✅ Monthly data updated successfully!")
    print("="*80 + "\n")
