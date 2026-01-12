# BHX Store Data Tracker

Long-term tracking system for Bách Hóa Xanh store expansion data.

## Project Structure

```
PROCESSORS/api/BHX_store/
├── bhx_store.py           # Core module (API + data logic)
├── run_monthly_update.py  # Update script
└── README.md

BSC_masterfile/
├── bhx_raw_snapshots.parquet     # Cumulative API snapshots
└── bhx_monthly_tracking.parquet  # Monthly tracking pivot table
```

## Quick Start

```bash
# Full update (fetch + update tracking)
python3 run_monthly_update.py

# Fetch only (API → raw database)
python3 run_monthly_update.py --fetch

# Update tracking only (from latest snapshot)
python3 run_monthly_update.py --update

# Show history
python3 run_monthly_update.py --history
```

## Output Files

**Location:** `BSC_masterfile/`

**bhx_raw_snapshots.parquet:**
- All historical store snapshots
- Columns: storeId, lat, lng, storeLocation, provinceName, fetch_date, ...
- Size: ~70 KB/month

**bhx_monthly_tracking.parquet:**
- Province-level tracking (pivot table format)
- Columns: province_new, province_old, [date columns], new_dec, new_mom, YTD_dec, MOM_dec
- Size: ~300 bytes/month

## API Endpoints

- Province list: `https://apibhx.tgdd.vn/Location/V2/GetFull`
- Stores: `https://apibhx.tgdd.vn/Location/V2/GetStoresByLocation?provinceId=X`

## Dependencies

```bash
pip3 install pandas requests
```

## Monthly Cron Job

```bash
# Run on 1st day of each month at 6 AM
0 6 1 * * cd /path/to/BHX_store && python3 run_monthly_update.py
```
