# BHX Store Data Tracker

Long-term tracking system for Bách Hóa Xanh store expansion data.

**Location:** `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/api/BHX_store`

## Project Structure

```
PROCESSORS/api/BHX_store/
├── 🚀 Core Scripts
│   ├── fetch_bhx_stores_refactored.py   # Fetch API → cumulative DB
│   ├── update_monthly_data.py           # Update monthly tracking
│   └── create_monthly_template.py       # Initialize baseline
│
├── 📊 Analysis Tools
│   ├── analyze_stores.py                # Summary tables
│   ├── compare_snapshots.py             # Snapshot comparison
│   └── demo_coordinates.py              # Lat/lng tools
│
├── 💾 Data Files
│   ├── bhx_raw_snapshots.parquet        # Raw DB (ALL snapshots)
│   └── bhx_monthly_tracking.parquet     # Monthly summary
│
└── 📖 Documentation
    └── README.md                         # This file
```

## Quick Start

```bash
# 1. Fetch data (appends to cumulative database)
python3 fetch_bhx_stores_refactored.py
# → Output: bhx_raw_snapshots.parquet (cumulative, growing)

# 2. Show database history
python3 fetch_bhx_stores_refactored.py --history
# → Shows all snapshots in database

# 3. Analyze current snapshot
python3 analyze_stores.py
# → Console output với summary tables

# 4. Update monthly tracking
python3 update_monthly_data.py --mode auto --month 2025-01 --name "January 2025"
# → Compares latest snapshot with previous month
```

## Files

**Core Scripts:**
- `fetch_bhx_stores_refactored.py` ⭐ - Fetch API → cumulative raw database
- `update_monthly_data.py` - Monthly tracking update (auto/manual)
- `create_monthly_template.py` - Create Dec 2024 baseline

**Analysis Tools:**
- `analyze_stores.py` - Terminal analysis với summary tables
- `compare_snapshots.py` - So sánh 2 snapshots (detect new/closed stores)
- `demo_coordinates.py` - Lat/lng demo + distance calculator

**Data Files:**
- `bhx_raw_snapshots.parquet` - Cumulative raw database (all historical snapshots)
- `bhx_monthly_tracking.parquet` - Monthly province-level tracking (20 rows × growing columns)

**Deprecated:**
- `fetch_bhx_stores.py` - Old version (creates multiple files)

## Current Data (2025-12-29)

- **2,547 stores** × **20 provinces** × **1,091 wards**
- **Top province:** TPHCM (832 stores, 32.7%)
- **Coverage:** 8.60°N → 20.44°N (1,326 km)
- **Operating:** 5:30-21:30 (69.8%), no 24/7 stores

## API Endpoints

- Province list: `https://apibhx.tgdd.vn/Location/V2/GetFull`
- Stores: `https://apibhx.tgdd.vn/Location/V2/GetStoresByLocation?provinceId=X`

**Fields:** storeId, lat, lng, storeLocation, provinceId, districtId, wardId, isStoreVirtual, openHour

## Data Storage Architecture

**Two-Tier Storage System:**

```
📂 bhx_raw_snapshots.parquet (RAW DATABASE)
├── All historical store snapshots
├── Columns: storeId, lat, lng, storeLocation, provinceId, districtId, wardId,
│            isStoreVirtual, openHour, provinceName, fetch_date
├── Size: ~70 KB/month (Parquet compression)
└── Purpose: Long-term storage, detailed analysis

📂 bhx_monthly_tracking.parquet (MONTHLY TRACKING)
├── Province-level tracking (20 rows fixed, columns grow monthly)
├── Columns: province_new, province_old, 31/12/2024, 29/12/2025, new_dec, YTD_dec, MOM_dec
│   • province_new: Government standard name (single province)
│   • province_old: BHX API name (merged provinces)
│   • Date columns: Store counts per snapshot (31/12/2024, 29/12/2025, ...)
│   • new_dec: New stores since December baseline
│   • YTD_dec: Year-to-Date growth % (vs year-start baseline)
│   • MOM_dec: Month-over-Month growth % (vs previous month)
├── Size: ~300 bytes/month
└── Purpose: Long-term province growth tracking with government mapping
```

**Why This Design?**
- ✅ Single cumulative file easier to query than multiple files
- ✅ Parquet compression keeps size efficient
- ✅ fetch_date column enables time-series analysis
- ✅ Raw database preserves all details for future analysis
- ✅ Monthly tracking provides quick aggregated insights

## Track New Stores

### Recommended Workflow (Monthly)

```bash
# Step 1: Monthly data collection (first day of month)
python3 fetch_bhx_stores_refactored.py
# → Appends new snapshot to bhx_raw_snapshots.parquet

# Step 2: View database history
python3 fetch_bhx_stores_refactored.py --history
# → Shows all snapshots collected

# Step 3: Update monthly tracking
python3 update_monthly_data.py --mode auto --month 2025-02 --name "February 2025"
# → Adds new month column (e.g., 31/01/2025) with YTD/MOM calculations
# → Updates bhx_monthly_tracking.parquet

# Step 4: View monthly trends
python3 -c "
import pandas as pd
df = pd.read_parquet('bhx_monthly_tracking.parquet')
print(df[['province_new', '31/12/2024', '29/12/2025', 'YTD_dec', 'MOM_dec']])
"
```

### Growth Calculation Rules

**Base Line (Fixed per Year):**
- 2025: `31/12/2024` (baseline for all 2025 months)
- 2026: `29/12/2025` (baseline for all 2026 months)
- 2027: `31/12/2026` (baseline for all 2027 months)

**Formulas:**
- `new_dec = Current Month - December Baseline`
- `YTD_dec = (Current Month - Year Start) / Year Start × 100`
- `MOM_dec = (Current Month - Previous Month) / Previous Month × 100`

**Example (January 2026):**
- Base: `29/12/2025 = 2,547` (fixed for entire 2026)
- Current: `31/01/2026 = 2,600`
- `new_dec = 2600 - 2547 = 53`
- `YTD_dec = (2600 - 2547) / 2547 × 100 = 2.08%`
- `MOM_dec = (2600 - 2547) / 2547 × 100 = 2.08%` (January = YTD)

### Manual Data Entry (Alternative)

```bash
# If you have data from external source
python3 update_monthly_data.py --mode manual
# → Enter data: Province|Continuing|New|Total
```

### Automated Collection (Cron Job)

```bash
# Run on 1st day of each month at 6 AM
0 6 1 * * cd /path/to/BHX_Store && python3 fetch_bhx_stores_refactored.py
```

## Dependencies

```bash
pip3 install pandas requests
```
