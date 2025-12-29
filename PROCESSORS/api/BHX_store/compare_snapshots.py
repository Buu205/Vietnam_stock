"""
Compare BHX store snapshots to detect new/closed stores by province
Requires multiple parquet files from different dates
"""
import pandas as pd
from pathlib import Path
from datetime import datetime


def load_snapshots(data_dir=Path(__file__).parent):
    """Load all available snapshots"""
    parquet_files = sorted(data_dir.glob("bhx_stores_*.parquet"))

    if len(parquet_files) < 2:
        print(f"❌ Need at least 2 snapshots to compare!")
        print(f"   Found: {len(parquet_files)} file(s)")
        print(f"\n💡 Run fetch script on different days:")
        print(f"   python3 fetch_bhx_stores.py  # Creates bhx_stores_YYYYMMDD.parquet")
        return None, None

    snapshots = []
    for file in parquet_files:
        df = pd.read_parquet(file)
        date = file.stem.replace('bhx_stores_', '')
        snapshots.append({
            'date': date,
            'file': file.name,
            'df': df,
            'store_ids': set(df['storeId'])
        })

    return snapshots[0], snapshots[-1]  # oldest, newest


def compare_snapshots(old_snap, new_snap):
    """Compare two snapshots and return differences"""
    old_ids = old_snap['store_ids']
    new_ids = new_snap['store_ids']

    # Detect changes
    new_stores = new_ids - old_ids        # Stores mới mở
    closed_stores = old_ids - new_ids     # Stores đóng cửa
    continuing = old_ids & new_ids        # Stores vẫn hoạt động

    return {
        'new': new_stores,
        'closed': closed_stores,
        'continuing': continuing
    }


def analyze_by_province(df, store_ids, province_col='provinceName'):
    """Count stores by province"""
    filtered = df[df['storeId'].isin(store_ids)]
    return filtered[province_col].value_counts()


def print_comparison_report(old_snap, new_snap, changes):
    """Print detailed comparison report"""
    print("\n" + "="*80)
    print("🔍 BHX STORE COMPARISON REPORT")
    print("="*80)

    print(f"\n📅 Comparison Period:")
    print(f"   Old snapshot: {old_snap['date']} ({len(old_snap['df']):,} stores)")
    print(f"   New snapshot: {new_snap['date']} ({len(new_snap['df']):,} stores)")
    print(f"   Time span: {old_snap['date']} → {new_snap['date']}")

    print(f"\n📊 Overall Changes:")
    print(f"   New stores opened:     {len(changes['new']):>5,}")
    print(f"   Stores closed:         {len(changes['closed']):>5,}")
    print(f"   Continuing stores:     {len(changes['continuing']):>5,}")
    print(f"   Net change:            {len(changes['new']) - len(changes['closed']):>+5,}")

    # New stores by province
    if changes['new']:
        print(f"\n🆕 NEW STORES BY PROVINCE (Top 10):")
        new_by_province = analyze_by_province(new_snap['df'], changes['new'])
        print(f"\n{'Province':<40} {'New Stores':>12} {'%':>7}")
        print("-" * 62)

        for province, count in new_by_province.head(10).items():
            pct = count / len(changes['new']) * 100
            print(f"{province[:40]:<40} {count:>12,} {pct:>6.1f}%")

        # List new stores
        print(f"\n📋 New Store Details:")
        new_stores_df = new_snap['df'][new_snap['df']['storeId'].isin(changes['new'])]
        for _, store in new_stores_df.head(10).iterrows():
            print(f"   • {store['storeId']:>6} - {store['storeLocation'][:60]}...")

    # Closed stores by province
    if changes['closed']:
        print(f"\n🚫 CLOSED STORES BY PROVINCE (Top 10):")
        closed_by_province = analyze_by_province(old_snap['df'], changes['closed'])
        print(f"\n{'Province':<40} {'Closed':>12} {'%':>7}")
        print("-" * 62)

        for province, count in closed_by_province.head(10).items():
            pct = count / len(changes['closed']) * 100
            print(f"{province[:40]:<40} {count:>12,} {pct:>6.1f}%")

        # List closed stores
        print(f"\n📋 Closed Store Details:")
        closed_stores_df = old_snap['df'][old_snap['df']['storeId'].isin(changes['closed'])]
        for _, store in closed_stores_df.head(10).iterrows():
            print(f"   • {store['storeId']:>6} - {store['storeLocation'][:60]}...")

    print("\n" + "="*80)


def export_changes_csv(old_snap, new_snap, changes, output_dir=Path(__file__).parent):
    """Export changes to CSV files"""
    if changes['new']:
        new_stores_df = new_snap['df'][new_snap['df']['storeId'].isin(changes['new'])]
        output_file = output_dir / f"new_stores_{old_snap['date']}_to_{new_snap['date']}.csv"
        new_stores_df.to_csv(output_file, index=False)
        print(f"\n✅ Exported new stores: {output_file.name}")

    if changes['closed']:
        closed_stores_df = old_snap['df'][old_snap['df']['storeId'].isin(changes['closed'])]
        output_file = output_dir / f"closed_stores_{old_snap['date']}_to_{new_snap['date']}.csv"
        closed_stores_df.to_csv(output_file, index=False)
        print(f"✅ Exported closed stores: {output_file.name}")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("BHX STORE SNAPSHOT COMPARISON")
    print("="*80)

    # Load snapshots
    old_snap, new_snap = load_snapshots()

    if old_snap is None:
        exit(1)

    # Compare
    changes = compare_snapshots(old_snap, new_snap)

    # Print report
    print_comparison_report(old_snap, new_snap, changes)

    # Export CSV
    export_changes_csv(old_snap, new_snap, changes)

    print("\n✅ Comparison complete!\n")
