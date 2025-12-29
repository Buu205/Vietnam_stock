"""
Analyze Bach Hoa Xanh store data from parquet file
Generates detailed statistics and visualizations
"""
import pandas as pd
from pathlib import Path
from datetime import datetime


def load_latest_data(data_dir: Path = Path(__file__).parent) -> pd.DataFrame:
    """Load the most recent parquet file"""
    parquet_files = sorted(data_dir.glob("bhx_stores_*.parquet"), reverse=True)

    if not parquet_files:
        raise FileNotFoundError(f"No parquet files found in {data_dir}")

    latest_file = parquet_files[0]
    print(f"📂 Loading data from: {latest_file.name}")

    df = pd.read_parquet(latest_file)
    print(f"   Loaded {len(df):,} stores (fetch date: {df['fetch_date'].iloc[0]})")

    return df


def analyze_geographic_distribution(df: pd.DataFrame):
    """Analyze store distribution by geography"""
    print("\n" + "="*80)
    print("📍 GEOGRAPHIC DISTRIBUTION")
    print("="*80)

    # Province distribution
    province_stats = df['provinceName'].value_counts()
    print(f"\n🏪 Stores by Province (Total: {len(province_stats)} provinces):")
    print(f"\n{'Province':<40} {'Count':>8} {'%':>7} {'Chart':<30}")
    print("-" * 88)

    for province, count in province_stats.head(20).items():
        pct = count / len(df) * 100
        bar = '█' * int(count / province_stats.max() * 30)
        print(f"{province[:40]:<40} {count:>8,} {pct:>6.1f}% {bar}")

    # Virtual vs Physical stores
    virtual_stats = df['isStoreVirtual'].value_counts()
    print(f"\n🏬 Store Type Distribution:")
    print(f"   Physical stores: {virtual_stats.get(False, 0):,} ({virtual_stats.get(False, 0)/len(df)*100:.1f}%)")
    print(f"   Virtual stores:  {virtual_stats.get(True, 0):,} ({virtual_stats.get(True, 0)/len(df)*100:.1f}%)")


def analyze_operating_hours(df: pd.DataFrame):
    """Analyze store operating hours patterns"""
    print("\n" + "="*80)
    print("⏰ OPERATING HOURS ANALYSIS")
    print("="*80)

    # Most common opening hours
    opening_hours = df['openHour'].value_counts()
    print(f"\n🕐 Top 10 Operating Hour Patterns:")
    print(f"\n{'Operating Hours':<50} {'Count':>8} {'%':>7}")
    print("-" * 68)

    for hours, count in opening_hours.head(10).items():
        pct = count / len(df) * 100
        print(f"{hours[:50]:<50} {count:>8,} {pct:>6.1f}%")


def analyze_coordinates(df: pd.DataFrame):
    """Analyze geographic coordinates"""
    print("\n" + "="*80)
    print("🗺️  COORDINATE ANALYSIS")
    print("="*80)

    print(f"\n📊 Latitude Range:")
    print(f"   Min: {df['lat'].min():.6f} (Southernmost)")
    print(f"   Max: {df['lat'].max():.6f} (Northernmost)")
    print(f"   Avg: {df['lat'].mean():.6f}")

    print(f"\n📊 Longitude Range:")
    print(f"   Min: {df['lng'].min():.6f} (Westernmost)")
    print(f"   Max: {df['lng'].max():.6f} (Easternmost)")
    print(f"   Avg: {df['lng'].mean():.6f}")

    # Identify regions based on latitude
    df_temp = df.copy()
    df_temp['region'] = pd.cut(
        df_temp['lat'],
        bins=[0, 11, 16, 25],
        labels=['Southern', 'Central', 'Northern']
    )

    region_stats = df_temp['region'].value_counts()
    print(f"\n🌏 Regional Distribution (by latitude):")
    for region, count in region_stats.items():
        pct = count / len(df) * 100
        print(f"   {region}: {count:,} stores ({pct:.1f}%)")


def analyze_store_density(df: pd.DataFrame):
    """Analyze store density metrics"""
    print("\n" + "="*80)
    print("📈 STORE DENSITY METRICS")
    print("="*80)

    # District analysis
    district_stats = df.groupby('districtId').size().describe()
    print(f"\n🏘️  Stores per District:")
    print(f"   Average:  {district_stats['mean']:.1f} stores/district")
    print(f"   Median:   {district_stats['50%']:.1f} stores/district")
    print(f"   Max:      {district_stats['max']:.0f} stores/district")
    print(f"   Min:      {district_stats['min']:.0f} stores/district")

    # Find districts with most stores
    top_districts = df.groupby(['districtId', 'provinceName']).size().sort_values(ascending=False)
    print(f"\n🏆 Top 10 Districts by Store Count:")
    print(f"\n{'Province':<40} {'District ID':>12} {'Count':>8}")
    print("-" * 63)

    for (district_id, province), count in top_districts.head(10).items():
        print(f"{province[:40]:<40} {district_id:>12,} {count:>8,}")


def generate_summary_table(df: pd.DataFrame):
    """Generate overall summary table"""
    print("\n" + "="*80)
    print("📋 OVERALL SUMMARY")
    print("="*80)

    summary_data = {
        'Metric': [
            'Total Stores',
            'Total Provinces',
            'Total Districts',
            'Total Wards',
            'Physical Stores',
            'Virtual Stores',
            'Fetch Date',
            'Average Stores per Province',
            'Average Stores per District',
        ],
        'Value': [
            f"{len(df):,}",
            f"{df['provinceId'].nunique():,}",
            f"{df['districtId'].nunique():,}",
            f"{df['wardId'].nunique():,}",
            f"{(~df['isStoreVirtual']).sum():,}",
            f"{df['isStoreVirtual'].sum():,}",
            df['fetch_date'].iloc[0],
            f"{len(df) / df['provinceId'].nunique():.1f}",
            f"{len(df) / df['districtId'].nunique():.1f}",
        ]
    }

    summary_df = pd.DataFrame(summary_data)
    print("\n" + summary_df.to_string(index=False))


def export_detailed_stats(df: pd.DataFrame, output_dir: Path = Path(__file__).parent):
    """Export detailed statistics to CSV"""
    # Province-level stats
    province_stats = df.groupby('provinceName').agg({
        'storeId': 'count',
        'lat': ['min', 'max', 'mean'],
        'lng': ['min', 'max', 'mean'],
        'isStoreVirtual': lambda x: (x == True).sum()
    }).round(6)

    province_stats.columns = ['total_stores', 'lat_min', 'lat_max', 'lat_avg',
                              'lng_min', 'lng_max', 'lng_avg', 'virtual_stores']
    province_stats = province_stats.sort_values('total_stores', ascending=False)

    output_file = output_dir / f"province_stats_{datetime.now().strftime('%Y%m%d')}.csv"
    province_stats.to_csv(output_file)

    print(f"\n📊 Exported province statistics to: {output_file.name}")
    print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("BACH HOA XANH STORE ANALYZER")
    print("="*80)

    # Load data
    df = load_latest_data()

    # Run analyses
    generate_summary_table(df)
    analyze_geographic_distribution(df)
    analyze_coordinates(df)
    analyze_operating_hours(df)
    analyze_store_density(df)

    # Export stats
    export_detailed_stats(df)

    print("\n" + "="*80)
    print("✅ Analysis complete!")
    print("="*80 + "\n")
