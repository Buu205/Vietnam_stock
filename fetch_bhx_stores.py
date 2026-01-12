"""
Fetch all Bach Hoa Xanh stores from API and sync to MongoDB
- Dynamically fetches province IDs from GetFull API (handles new provinces)
- Tracks new/closed stores with first_seen/last_seen dates
"""
import requests
import pandas as pd
import time
from datetime import datetime
from typing import List, Dict
from pymongo import MongoClient

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://dkng27:%40nhMaiyeu123@vibing.nqggjql.mongodb.net/?retryWrites=true&w=majority&appName=Vibing"
DB_NAME = "ticker_data"
COLLECTION_NAME = "bhx_stores_list"

# API Configuration
API_URL_STORES = 'https://apibhx.tgdd.vn/Location/V2/GetStoresByLocation'
API_URL_PROVINCES = 'https://apibhx.tgdd.vn/Location/V2/GetFull'

HEADERS = {
    'Authorization': 'Bearer D72FA5AF3987B6A427BF1B21A363125B',
    'Customer-Id': '859c256d-cc7d-4496-b0ab-5398c025aa99',
    'Deviceid': '859c256d-cc7d-4496-b0ab-5398c025aa99',
    'Origin': 'https://www.bachhoanxanh.com',
    'Referer': 'https://www.bachhoanxanh.com/he-thong-cua-hang',
    'Reversehost': 'http://bhxapi.live',
    'Xapikey': 'bhx-api-core-2022',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}


def fetch_province_data():
    """
    Fetch province IDs and names dynamically from BHX API

    Returns:
        Tuple of (province_ids_list, province_id_to_name_mapping)
    """
    print("Fetching province data from API...")

    response = requests.get(API_URL_PROVINCES, headers=HEADERS, timeout=15)
    data = response.json()

    if response.status_code != 200 or data.get('code') != 0:
        raise Exception(f"Failed to fetch provinces: {data.get('errorReason', 'Unknown error')}")

    provinces = data.get('data', {}).get('provinces', [])

    if not provinces:
        raise Exception("No province data found in API response")

    # Build mapping (multiple provinces can share same ID)
    province_mapping = {}
    for p in provinces:
        if p['id'] in province_mapping:
            province_mapping[p['id']] += ', ' + p['name']
        else:
            province_mapping[p['id']] = p['name']

    province_ids = sorted(province_mapping.keys())

    print(f"Found {len(province_ids)} unique province IDs (range: {min(province_ids)} to {max(province_ids)})")

    return province_ids, province_mapping

def fetch_stores_by_province(province_id: int, ward_id: int = 0, delay: float = 0.5, max_retries: int = 3):
    """
    Fetch all stores for a given province with pagination and retry logic

    Args:
        province_id: Province ID
        ward_id: Ward ID (0 for all wards)
        delay: Delay between requests in seconds
        max_retries: Max retry attempts per request

    Returns:
        List of store dicts
    """
    all_stores = []
    page_index = 0
    page_size = 50
    total = 0

    print(f'Fetching stores for provinceId={province_id}...', end=' ')

    while True:
        params = {
            'provinceId': province_id,
            'wardId': ward_id,
            'pageSize': page_size,
            'pageIndex': page_index
        }

        success = False
        for attempt in range(max_retries):
            try:
                response = requests.get(API_URL_STORES, params=params, headers=HEADERS, timeout=30)
                data = response.json()

                if response.status_code != 200 or data.get('code') != 0:
                    break

                stores = data.get('data', {}).get('stores', [])
                total = data.get('data', {}).get('total', 0)
                success = True
                break

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff: 2, 4, 6 seconds
                    print(f"[retry {attempt + 1}]", end=' ')
                    time.sleep(wait_time)
                else:
                    print(f"Error after {max_retries} retries: {e}")

            except Exception as e:
                print(f"Error: {e}")
                break

        if not success or not stores:
            break

        all_stores.extend(stores)

        if len(all_stores) >= total:
            break

        page_index += 1
        time.sleep(delay)

    print(f"{len(all_stores)} stores")
    return all_stores


def fetch_all_provinces(province_ids: List[int], province_mapping: Dict[int, str]):
    """
    Fetch stores for multiple provinces

    Args:
        province_ids: List of province IDs to fetch
        province_mapping: Dict mapping province ID to province name

    Returns:
        DataFrame with all stores
    """
    all_stores = []

    for province_id in province_ids:
        stores = fetch_stores_by_province(province_id)

        province_name = province_mapping.get(province_id, 'Unknown')
        for store in stores:
            store['provinceName'] = province_name

        all_stores.extend(stores)
        time.sleep(1)

    return pd.DataFrame(all_stores)


def sync_to_mongodb(df_api: pd.DataFrame, today: str):
    """
    Sync API results with MongoDB - track new/closed stores
    """
    client = MongoClient(MONGODB_URI)
    collection = client[DB_NAME][COLLECTION_NAME]

    # Get existing stores from DB
    db_stores = {doc['storeId']: doc for doc in collection.find({}, {'_id': 0})}
    db_ids = set(db_stores.keys())
    api_ids = set(df_api['storeId'])

    new_ids = api_ids - db_ids
    closed_ids = db_ids - api_ids
    continuing_ids = api_ids & db_ids

    # Filter closed to only active stores (don't re-close already closed)
    closed_ids = {sid for sid in closed_ids if db_stores[sid]['status'] == 'active'}

    # Find reopened stores (were closed, now back in API)
    reopened_ids = {sid for sid in continuing_ids if db_stores[sid]['status'] == 'closed'}

    # Update continuing stores - last_seen
    if continuing_ids:
        collection.update_many(
            {'storeId': {'$in': list(continuing_ids)}},
            {'$set': {'last_seen': today, 'status': 'active'}}
        )

    # Insert new stores
    new_stores = []
    if new_ids:
        cols = ['storeId', 'lat', 'lng', 'storeLocation', 'provinceId', 'districtId',
                'wardId', 'openHour', 'provinceName']
        new_df = df_api[df_api['storeId'].isin(new_ids)][cols].copy()
        new_df['first_seen'] = today
        new_df['last_seen'] = today
        new_df['status'] = 'active'
        new_stores = new_df.to_dict('records')
        collection.insert_many(new_stores)

    # Mark closed stores
    if closed_ids:
        collection.update_many(
            {'storeId': {'$in': list(closed_ids)}},
            {'$set': {'status': 'closed'}}
        )

    # Get final counts
    active = collection.count_documents({'status': 'active'})
    closed = collection.count_documents({'status': 'closed'})

    client.close()

    return {
        'new': len(new_ids),
        'closed': len(closed_ids),
        'reopened': len(reopened_ids),
        'active': active,
        'total_closed': closed,
        'new_stores': new_stores
    }


if __name__ == '__main__':
    today = datetime.now().strftime('%Y-%m-%d')

    print("\n" + "="*60)
    print(f"Bach Hoa Xanh Store Scraper (Date: {today})")
    print("="*60)

    province_ids, province_mapping = fetch_province_data()

    print(f"\nFetching stores for {len(province_ids)} provinces...")
    df_stores = fetch_all_provinces(province_ids, province_mapping)

    print(f"\nSyncing to MongoDB...")
    result = sync_to_mongodb(df_stores, today)

    print(f"\n{'='*60}")
    print(f"New stores: {result['new']}")
    print(f"Reopened stores: {result['reopened']}")
    print(f"Closed stores: {result['closed']}")
    print(f"Total active: {result['active']}")
    print(f"Total closed: {result['total_closed']}")

    if result['new_stores']:
        print(f"\nNew stores added:")
        for s in result['new_stores']:
            print(f"  - {s['storeId']}: {s['storeLocation'][:60]}...")

    print(f"{'='*60}")
