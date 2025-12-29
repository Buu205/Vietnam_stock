"""
Fetch BHX stores and append to cumulative raw database
Single parquet file for long-term storage
"""
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
BASE_URL = "https://apibhx.tgdd.vn/Location/V2"
PROVINCES_ENDPOINT = f"{BASE_URL}/GetFull"
STORES_ENDPOINT = f"{BASE_URL}/GetStoresByLocation"

# File paths
RAW_DATABASE_FILE = Path(__file__).parent / "bhx_raw_snapshots.parquet"


def fetch_provinces():
    """Fetch all provinces from BHX API"""
    try:
        response = requests.get(PROVINCES_ENDPOINT, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        provinces = []
        for region in data.get('result', []):
            if 'provinceList' in region:
                for province in region['provinceList']:
                    provinces.append({
                        'id': province['id'],
                        'name': province['name']
                    })
        
        logger.info(f"✅ Fetched {len(provinces)} provinces")
        return provinces
    
    except Exception as e:
        logger.error(f"❌ Failed to fetch provinces: {e}")
        raise


def fetch_stores_by_province(province_id: int, delay: float = 0.5, max_retries: int = 3):
    """Fetch all stores for a province with retry logic"""
    for attempt in range(max_retries):
        try:
            params = {'provinceId': province_id}
            response = requests.get(STORES_ENDPOINT, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            stores = data.get('result', {}).get('storeList', [])
            
            time.sleep(delay)
            return stores
        
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"⚠️  Retry {attempt + 1}/{max_retries} for province {province_id}")
                time.sleep(delay * 2)
            else:
                logger.error(f"❌ Failed province {province_id} after {max_retries} attempts: {e}")
                return []


def fetch_all_stores():
    """Fetch all stores from all provinces"""
    logger.info("🚀 Starting BHX store fetch...")
    
    # Get provinces
    provinces = fetch_provinces()
    
    # Fetch stores
    all_stores = []
    fetch_date = datetime.now().strftime('%Y-%m-%d')
    
    for i, province in enumerate(provinces, 1):
        province_id = province['id']
        province_name = province['name']
        
        logger.info(f"📍 [{i}/{len(provinces)}] Fetching {province_name} (ID: {province_id})...")
        
        stores = fetch_stores_by_province(province_id)
        
        # Add fetch_date and province_name to each store
        for store in stores:
            store['fetch_date'] = fetch_date
            store['provinceName'] = province_name
        
        all_stores.extend(stores)
        logger.info(f"   → {len(stores)} stores")
    
    logger.info(f"✅ Total stores fetched: {len(all_stores):,}")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_stores)
    
    return df


def append_to_raw_database(new_df: pd.DataFrame):
    """Append new snapshot to cumulative raw database"""
    
    if RAW_DATABASE_FILE.exists():
        # Load existing data
        existing_df = pd.read_parquet(RAW_DATABASE_FILE)
        logger.info(f"📂 Existing database: {len(existing_df):,} rows")
        
        # Check if fetch_date already exists
        fetch_date = new_df['fetch_date'].iloc[0]
        if fetch_date in existing_df['fetch_date'].values:
            logger.warning(f"⚠️  Data for {fetch_date} already exists! Skipping append.")
            logger.info(f"   To re-fetch, delete rows with fetch_date='{fetch_date}' first.")
            return existing_df
        
        # Append new data
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        logger.info(f"➕ Appending {len(new_df):,} new rows")
        
    else:
        # First time - create new database
        combined_df = new_df
        logger.info(f"🆕 Creating new database with {len(new_df):,} rows")
    
    # Sort by fetch_date and storeId
    combined_df = combined_df.sort_values(['fetch_date', 'storeId']).reset_index(drop=True)
    
    # Save to parquet
    combined_df.to_parquet(RAW_DATABASE_FILE, index=False, compression='snappy')
    
    file_size_kb = RAW_DATABASE_FILE.stat().st_size / 1024
    logger.info(f"✅ Saved: {RAW_DATABASE_FILE.name} ({len(combined_df):,} rows, {file_size_kb:.1f} KB)")
    
    return combined_df


def print_summary(df: pd.DataFrame):
    """Print summary of fetched data"""
    fetch_date = df['fetch_date'].iloc[0]
    
    print("\n" + "=" * 80)
    print(f"BHX STORE DATABASE - {fetch_date}")
    print("=" * 80)
    
    # Overall stats
    total_stores = len(df)
    total_provinces = df['provinceName'].nunique()
    total_wards = df['wardId'].nunique()
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total stores:     {total_stores:>6,}")
    print(f"   Total provinces:  {total_provinces:>6,}")
    print(f"   Total wards:      {total_wards:>6,}")
    
    # Top provinces
    print(f"\n🏆 Top 10 Provinces:")
    top_provinces = df['provinceName'].value_counts().head(10)
    
    print(f"\n   {'Province':<40} {'Stores':>8} {'%':>6}")
    print("   " + "-" * 60)
    
    for province, count in top_provinces.items():
        pct = (count / total_stores) * 100
        print(f"   {province[:40]:<40} {count:>8,} {pct:>6.1f}%")
    
    print("\n" + "=" * 80 + "\n")


def show_database_history():
    """Show all snapshots in the database"""
    if not RAW_DATABASE_FILE.exists():
        logger.info("📂 No database found yet.")
        return
    
    df = pd.read_parquet(RAW_DATABASE_FILE)
    
    print("\n" + "=" * 80)
    print("DATABASE HISTORY")
    print("=" * 80)
    
    # Group by fetch_date
    history = df.groupby('fetch_date').agg({
        'storeId': 'count',
        'provinceName': 'nunique'
    }).reset_index()
    
    history.columns = ['fetch_date', 'stores', 'provinces']
    
    print(f"\nTotal snapshots: {len(history)}")
    print(f"Total rows: {len(df):,}")
    print(f"\n{'Fetch Date':<12} {'Stores':>8} {'Provinces':>10}")
    print("-" * 35)
    
    for _, row in history.iterrows():
        print(f"{row['fetch_date']:<12} {row['stores']:>8,} {row['provinces']:>10}")
    
    file_size_kb = RAW_DATABASE_FILE.stat().st_size / 1024
    print(f"\n📁 File: {RAW_DATABASE_FILE.name} ({file_size_kb:.1f} KB)")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch BHX stores to cumulative database')
    parser.add_argument('--history', action='store_true', help='Show database history')
    
    args = parser.parse_args()
    
    if args.history:
        show_database_history()
    else:
        # Fetch and append
        new_df = fetch_all_stores()
        combined_df = append_to_raw_database(new_df)
        
        # Show summary
        print_summary(new_df)
        show_database_history()

