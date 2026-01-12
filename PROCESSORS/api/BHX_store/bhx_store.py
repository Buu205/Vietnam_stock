"""
BHX Store Tracker - Core Module
Fetch Bach Hoa Xanh store data and track monthly changes.

Output files (saved to BSC_masterfile/):
- bhx_raw_snapshots.parquet: All API snapshots (cumulative)
- bhx_monthly_tracking.parquet: Monthly tracking pivot table
"""
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths - Output to BSC_masterfile directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # Vietnam_dashboard
OUTPUT_DIR = PROJECT_ROOT / "BSC_masterfile"
OUTPUT_DIR.mkdir(exist_ok=True)
RAW_DB_PATH = OUTPUT_DIR / "bhx_raw_snapshots.parquet"
TRACKING_PATH = OUTPUT_DIR / "bhx_monthly_tracking.parquet"

# API Configuration
BASE_URL = "https://apibhx.tgdd.vn/Location/V2"
PROVINCES_ENDPOINT = f"{BASE_URL}/GetFull"
STORES_ENDPOINT = f"{BASE_URL}/GetStoresByLocation"
API_TIMEOUT = 60  # seconds - BHX API can be slow
MAX_RETRIES = 3

# API Headers (required for authentication)
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


# =============================================================================
# API FETCHING
# =============================================================================

def get_stored_provinces() -> list[dict]:
    """Get province IDs from existing raw data (fallback when API fails)."""
    if not RAW_DB_PATH.exists():
        return []
    df = pd.read_parquet(RAW_DB_PATH)
    # Get unique province ID and name pairs
    provinces = df.groupby('provinceName')['provinceId'].first().reset_index()
    result = [{'id': row['provinceId'], 'name': row['provinceName']} for _, row in provinces.iterrows()]
    logger.info(f"Loaded {len(result)} provinces from stored data")
    return result


def fetch_provinces() -> list[dict]:
    """Fetch provinces - try API first, fallback to stored data.

    Note: BHX API groups multiple provinces under same ID (e.g., HCM + BR-VT + Binh Duong = ID 1027).
    This function merges names for same ID (e.g., "TP. Hồ Chí Minh, Bà Rịa - Vũng Tàu, Bình Dương").
    """
    # Try API first
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(PROVINCES_ENDPOINT, headers=HEADERS, timeout=API_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            # API structure: {'code': 0, 'data': {'provinces': [...]}}
            provinces_raw = data.get('data', {}).get('provinces', [])

            # Merge names for same province ID
            province_mapping = {}
            for p in provinces_raw:
                pid = p['id']
                pname = p['name']
                if pid in province_mapping:
                    province_mapping[pid] += ', ' + pname
                else:
                    province_mapping[pid] = pname

            provinces = [{'id': pid, 'name': pname} for pid, pname in province_mapping.items()]

            logger.info(f"Fetched {len(provinces)} province groups from API")
            return provinces
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                wait_time = (attempt + 1) * 5  # 5s, 10s, 15s
                logger.warning(f"Retry {attempt + 1}/{MAX_RETRIES} for provinces (wait {wait_time}s): {e}")
                time.sleep(wait_time)
            else:
                logger.warning(f"API failed after {MAX_RETRIES} attempts, using stored provinces")
                stored = get_stored_provinces()
                if stored:
                    return stored
                raise RuntimeError("No stored provinces available and API failed")


def fetch_stores_by_province(province_id: int, delay: float = 0.5) -> list[dict]:
    """Fetch all stores for a province with pagination and retry logic."""
    all_stores = []
    page_index = 0
    page_size = 50

    while True:
        for attempt in range(MAX_RETRIES):
            try:
                params = {
                    'provinceId': province_id,
                    'wardId': 0,
                    'pageSize': page_size,
                    'pageIndex': page_index
                }
                response = requests.get(STORES_ENDPOINT, params=params, headers=HEADERS, timeout=API_TIMEOUT)
                response.raise_for_status()
                data = response.json()

                # API structure: {'code': 0, 'data': {'stores': [...], 'total': N}}
                stores = data.get('data', {}).get('stores', [])
                total = data.get('data', {}).get('total', 0)

                all_stores.extend(stores)
                time.sleep(delay)

                # Check if we got all stores
                if len(all_stores) >= total or not stores:
                    return all_stores

                page_index += 1
                break  # Success, move to next page

            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    wait_time = (attempt + 1) * 3  # 3s, 6s, 9s
                    logger.warning(f"Retry {attempt + 1}/{MAX_RETRIES} for province {province_id} (wait {wait_time}s)")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed province {province_id}: {e}")
                    return all_stores  # Return what we got so far
        else:
            # All retries failed for this page
            return all_stores

    return all_stores


def fetch_all_stores() -> pd.DataFrame:
    """Fetch all stores from all provinces."""
    logger.info("Starting BHX store fetch...")
    provinces = fetch_provinces()
    fetch_date = datetime.now().strftime('%Y-%m-%d')

    all_stores = []
    for i, prov in enumerate(provinces, 1):
        logger.info(f"[{i}/{len(provinces)}] {prov['name']}...")
        stores = fetch_stores_by_province(prov['id'])
        for s in stores:
            s['fetch_date'] = fetch_date
            s['provinceName'] = prov['name']
        all_stores.extend(stores)
        logger.info(f"   → {len(stores)} stores")

    logger.info(f"Total: {len(all_stores):,} stores")
    return pd.DataFrame(all_stores)


# =============================================================================
# RAW SNAPSHOT DATABASE
# =============================================================================

def append_to_raw_db(new_df: pd.DataFrame) -> pd.DataFrame:
    """Append new snapshot to cumulative raw database."""
    fetch_date = new_df['fetch_date'].iloc[0]

    if RAW_DB_PATH.exists():
        existing_df = pd.read_parquet(RAW_DB_PATH)
        if fetch_date in existing_df['fetch_date'].values:
            logger.warning(f"Data for {fetch_date} already exists! Skipping.")
            return existing_df
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        logger.info(f"Appending {len(new_df):,} rows to existing {len(existing_df):,}")
    else:
        combined_df = new_df
        logger.info(f"Creating new database with {len(new_df):,} rows")

    combined_df = combined_df.sort_values(['fetch_date', 'storeId']).reset_index(drop=True)
    combined_df.to_parquet(RAW_DB_PATH, index=False, compression='snappy')
    logger.info(f"Saved: {RAW_DB_PATH.name} ({len(combined_df):,} rows)")
    return combined_df


def get_snapshot(fetch_date: str = None) -> pd.DataFrame:
    """Get snapshot for a specific date or latest."""
    if not RAW_DB_PATH.exists():
        raise FileNotFoundError("Raw database not found. Run fetch first.")

    df_all = pd.read_parquet(RAW_DB_PATH)
    if fetch_date is None:
        fetch_date = df_all['fetch_date'].max()

    df = df_all[df_all['fetch_date'] == fetch_date].copy()
    if df.empty:
        available = df_all['fetch_date'].unique().tolist()
        raise ValueError(f"No snapshot for {fetch_date}. Available: {available}")

    return df


def get_db_history() -> pd.DataFrame:
    """Get summary of all snapshots in database."""
    if not RAW_DB_PATH.exists():
        return pd.DataFrame()
    df = pd.read_parquet(RAW_DB_PATH)
    return df.groupby('fetch_date').agg(
        stores=('storeId', 'count'),
        provinces=('provinceName', 'nunique')
    ).reset_index()


# =============================================================================
# MONTHLY TRACKING (Pivot Table Format)
# =============================================================================

def load_monthly_tracking() -> pd.DataFrame:
    """Load monthly tracking data."""
    if not TRACKING_PATH.exists():
        raise FileNotFoundError(f"Tracking file not found: {TRACKING_PATH}")
    return pd.read_parquet(TRACKING_PATH)


def get_date_columns(df: pd.DataFrame) -> list[str]:
    """Get date columns from tracking dataframe (format: DD/MM/YYYY)."""
    import re
    date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')
    return [c for c in df.columns if date_pattern.match(c)]


def update_monthly_tracking(new_date_col: str = None) -> pd.DataFrame:
    """
    Update monthly tracking with latest snapshot data.
    Adds a new date column with store counts by province.

    Args:
        new_date_col: Date column name (DD/MM/YYYY format). Auto-generates from snapshot date if None.

    Returns:
        Updated tracking DataFrame
    """
    # Load latest snapshot
    snapshot_df = get_snapshot()
    snapshot_date = snapshot_df['fetch_date'].iloc[0]

    # Generate date column name if not provided (format: DD/MM/YYYY)
    if new_date_col is None:
        dt = datetime.strptime(snapshot_date, '%Y-%m-%d')
        new_date_col = dt.strftime('%d/%m/%Y')

    # Load existing tracking
    tracking_df = load_monthly_tracking()

    # Check if date already exists
    if new_date_col in tracking_df.columns:
        logger.warning(f"Column {new_date_col} already exists! Skipping.")
        return tracking_df

    # Count stores by province from snapshot (provinceName = province_old from API)
    province_counts = snapshot_df['provinceName'].value_counts()

    # Map using province_old (API names match provinceName in snapshot)
    tracking_df[new_date_col] = tracking_df['province_old'].map(province_counts).fillna(0).astype(int)

    # Update Total row
    total_idx = tracking_df[tracking_df['province_new'] == 'Total'].index
    if len(total_idx) > 0:
        tracking_df.loc[total_idx[0], new_date_col] = province_counts.sum()

    # Recalculate growth metrics
    date_cols = get_date_columns(tracking_df)
    if len(date_cols) >= 2:
        # Sort date columns chronologically
        sorted_dates = sorted(date_cols, key=lambda x: datetime.strptime(x, '%d/%m/%Y'))
        latest = sorted_dates[-1]
        prev = sorted_dates[-2]

        # MOM (Month-over-Month) % change
        # Find last date of previous month in parquet
        latest_dt = datetime.strptime(latest, '%d/%m/%Y')
        prev_month = latest_dt.month - 1 if latest_dt.month > 1 else 12
        prev_year = latest_dt.year if latest_dt.month > 1 else latest_dt.year - 1

        # Get all dates from previous month
        prev_month_dates = [d for d in sorted_dates
                           if datetime.strptime(d, '%d/%m/%Y').month == prev_month
                           and datetime.strptime(d, '%d/%m/%Y').year == prev_year]
        mom_baseline = prev_month_dates[-1] if prev_month_dates else prev  # Fallback to immediate prev

        tracking_df['new_mom'] = tracking_df[latest] - tracking_df[mom_baseline]
        tracking_df['MOM_dec'] = ((tracking_df[latest] - tracking_df[mom_baseline]) / tracking_df[mom_baseline].replace(0, float('nan')) * 100).round(2)

        # YTD - baseline is last date of previous year
        # Find baseline: latest date before current year
        latest_dt = datetime.strptime(latest, '%d/%m/%Y')
        baseline_candidates = [d for d in sorted_dates if datetime.strptime(d, '%d/%m/%Y').year < latest_dt.year]
        baseline = baseline_candidates[-1] if baseline_candidates else sorted_dates[0]

        tracking_df['new_dec'] = tracking_df[latest] - tracking_df[baseline]
        # Handle division by zero (replace inf with NaN)
        tracking_df['YTD_dec'] = ((tracking_df[latest] - tracking_df[baseline]) / tracking_df[baseline].replace(0, float('nan')) * 100).round(2)

    # Reorder columns: province_new, province_old, sorted dates, then metrics
    date_cols = get_date_columns(tracking_df)
    sorted_dates = sorted(date_cols, key=lambda x: datetime.strptime(x, '%d/%m/%Y'))
    metric_cols = ['new_dec', 'new_mom', 'YTD_dec', 'MOM_dec']
    ordered_cols = ['province_new', 'province_old'] + sorted_dates + metric_cols
    tracking_df = tracking_df[ordered_cols]

    # Save
    tracking_df.to_parquet(TRACKING_PATH, index=False, compression='snappy')
    logger.info(f"Added column: {new_date_col}")
    logger.info(f"Saved: {TRACKING_PATH.name}")

    return tracking_df


# =============================================================================
# REPORTING
# =============================================================================

def print_snapshot_summary(df: pd.DataFrame):
    """Print summary of a snapshot."""
    fetch_date = df['fetch_date'].iloc[0]
    print(f"\n{'='*60}")
    print(f"SNAPSHOT: {fetch_date}")
    print(f"{'='*60}")
    print(f"Total stores: {len(df):,}")
    print(f"Provinces: {df['provinceName'].nunique()}")
    print(f"\nTop 10 provinces:")
    for prov, cnt in df['provinceName'].value_counts().head(10).items():
        print(f"  {prov:<40} {cnt:>5,}")


def print_monthly_summary():
    """Print monthly tracking summary."""
    if not TRACKING_PATH.exists():
        print("No tracking file found.")
        return

    df = load_monthly_tracking()
    date_cols = get_date_columns(df)

    print(f"\n{'='*60}")
    print("MONTHLY TRACKING SUMMARY")
    print(f"{'='*60}")
    print(f"Provinces: {len(df) - 1}")  # Exclude Total row
    print(f"Date columns: {len(date_cols)}")

    if date_cols:
        sorted_dates = sorted(date_cols, key=lambda x: datetime.strptime(x, '%d/%m/%Y'))
        print(f"\nDate range: {sorted_dates[0]} → {sorted_dates[-1]}")

        # Show totals for each date
        total_row = df[df['province_new'] == 'Total']
        if not total_row.empty:
            print(f"\nTotal stores by date:")
            for d in sorted_dates:
                val = total_row[d].values[0]
                print(f"  {d}: {val:,.0f}")


def print_db_history():
    """Print database history."""
    hist = get_db_history()
    if hist.empty:
        print("No database found.")
        return

    print(f"\n{'='*60}")
    print("RAW DATABASE HISTORY")
    print(f"{'='*60}")
    print(f"{'Date':<12} {'Stores':>8} {'Provinces':>10}")
    print("-" * 32)
    for _, r in hist.iterrows():
        print(f"{r['fetch_date']:<12} {r['stores']:>8,} {r['provinces']:>10}")
