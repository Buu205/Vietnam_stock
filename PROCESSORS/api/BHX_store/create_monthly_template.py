"""
Create monthly store tracking template based on BHX historical data
Data structure: Province | Continuing | New | Total | % New | Month
"""
import pandas as pd
from datetime import datetime
from pathlib import Path


def create_december_2024_baseline():
    """
    Create baseline data for December 2024 from historical report
    This is the starting point for monthly tracking
    """
    # Data from historical report (end of Dec 2024)
    data = [
        {"province": "TP. Hồ Chí Minh, Bà Rịa - Vũng Tàu, Bình Dương", "continuing": 688.0, "new": 129.0, "total": 817.0, "pct_new": 15.8},
        {"province": "Hà Nội, Quảng Nam", "continuing": 0.0, "new": 85.0, "total": 85.0, "pct_new": 100.0},
        {"province": "Bình Định, Gia Lai", "continuing": 0.0, "new": 49.0, "total": 49.0, "pct_new": 100.0},
        {"province": "Cần Thơ, Hậu Giang, Sóc Trăng", "continuing": 103.0, "new": 47.0, "total": 150.0, "pct_new": 31.3},
        {"province": "Thanh Hóa", "continuing": 0.0, "new": 47.0, "total": 47.0, "pct_new": 100.0},
        {"province": "Nghệ An", "continuing": 0.0, "new": 44.0, "total": 44.0, "pct_new": 100.0},
        {"province": "Quảng Bình, Quảng Trị", "continuing": 0.0, "new": 39.0, "total": 39.0, "pct_new": 100.0},
        {"province": "Thành phố Huế", "continuing": 0.0, "new": 33.0, "total": 33.0, "pct_new": 100.0},
        {"province": "Hà Tĩnh", "continuing": 0.0, "new": 32.0, "total": 32.0, "pct_new": 100.0},
        {"province": "Kon Tum, Quảng Ngãi", "continuing": 0.0, "new": 26.0, "total": 26.0, "pct_new": 100.0},
        {"province": "Long An, Tây Ninh", "continuing": 147.0, "new": 26.0, "total": 173.0, "pct_new": 15.0},
        {"province": "Bình Phước, Đồng Nai", "continuing": 193.0, "new": 25.0, "total": 218.0, "pct_new": 11.5},
        {"province": "Đắk Lắk, Phú Yên", "continuing": 50.0, "new": 24.0, "total": 74.0, "pct_new": 32.4},
        {"province": "An Giang, Kiên Giang", "continuing": 110.0, "new": 24.0, "total": 134.0, "pct_new": 17.9},
        {"province": "Bình Thuận, Đắk Nông, Lâm Đồng", "continuing": 107.0, "new": 21.0, "total": 128.0, "pct_new": 16.4},
        {"province": "Khánh Hòa, Ninh Thuận", "continuing": 52.0, "new": 19.0, "total": 71.0, "pct_new": 26.8},
        {"province": "Bến Tre, Trà Vinh, Vĩnh Long", "continuing": 102.0, "new": 18.0, "total": 120.0, "pct_new": 15.0},
        {"province": "Bạc Liêu, Cà Mau", "continuing": 50.0, "new": 18.0, "total": 68.0, "pct_new": 26.5},
        {"province": "Đồng Tháp, Tiền Giang", "continuing": 107.0, "new": 16.0, "total": 123.0, "pct_new": 13.0},
    ]

    df = pd.DataFrame(data)
    df['month'] = '2024-12'
    df['month_name'] = 'December 2024'

    return df


def create_template_structure():
    """
    Define the template structure for monthly tracking
    """
    columns = {
        'month': 'str',           # Format: YYYY-MM
        'month_name': 'str',      # Format: "December 2024"
        'province': 'str',        # Province name
        'continuing': 'float',    # Stores from previous month
        'new': 'float',           # New stores opened this month
        'total': 'float',         # Total stores = continuing + new
        'pct_new': 'float',       # Percentage of new stores
    }

    return columns


def save_monthly_data(df, filename="bhx_monthly_tracking.parquet"):
    """Save monthly tracking data to parquet"""
    output_path = Path(__file__).parent / filename
    df.to_parquet(output_path, index=False, compression='snappy')
    print(f"✅ Saved: {output_path.name} ({len(df):,} rows)")
    return output_path


def print_summary(df):
    """Print summary statistics"""
    print("\n" + "="*80)
    print("MONTHLY STORE TRACKING - SUMMARY")
    print("="*80)

    for month in df['month'].unique():
        month_df = df[df['month'] == month]
        month_name = month_df['month_name'].iloc[0]

        total_continuing = month_df['continuing'].sum()
        total_new = month_df['new'].sum()
        total_stores = month_df['total'].sum()
        pct_new = (total_new / total_stores * 100) if total_stores > 0 else 0

        print(f"\n📅 {month_name} ({month}):")
        print(f"   Continuing stores: {total_continuing:>7,.0f}")
        print(f"   New stores:        {total_new:>7,.0f}")
        print(f"   Total stores:      {total_stores:>7,.0f}")
        print(f"   % New:             {pct_new:>7.1f}%")

        # Top 5 provinces by new stores
        print(f"\n   Top 5 Provinces (New Stores):")
        top5 = month_df.nlargest(5, 'new')[['province', 'new', 'total']]
        for idx, row in top5.iterrows():
            print(f"      {row['province'][:35]:<35} +{row['new']:>3.0f} → {row['total']:>4.0f}")

    print("\n" + "="*80)


if __name__ == '__main__':
    print("\n" + "="*80)
    print("CREATING MONTHLY STORE TRACKING TEMPLATE")
    print("="*80)

    # Create December 2024 baseline
    print("\n1. Creating December 2024 baseline...")
    df_dec_2024 = create_december_2024_baseline()

    # Save to parquet
    print("\n2. Saving to parquet...")
    output_file = save_monthly_data(df_dec_2024)

    # Print summary
    print_summary(df_dec_2024)

    # Print file info
    print("\n📊 Template Structure:")
    print(df_dec_2024.dtypes.to_string())

    print(f"\n📁 Output File: {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")

    print("\n✅ Template created! Use this as baseline for monthly updates.")
    print("="*80 + "\n")
