# Data Storage Architecture Scout Report

**Date:** 2025-12-29  
**Scope:** Complete DATA/ directory audit  
**Total Size:** 470 MB (241 MB raw + 229 MB processed)  
**Files:** 150+ parquet files + metadata  

---

## Executive Summary

Vietnam Dashboard employs a **layered data architecture** with clear separation between raw inputs and processed outputs. All data is stored in **Parquet format** (columnar, compressed) for efficiency. The system supports 457 tickers across 19 sectors with 4 entity types (Company, Bank, Insurance, Security).

**Key Characteristics:**
- Raw data: CSV inputs + Market data (OHLCV) + News + Metadata
- Processed data: 8 major categories with hierarchical organization
- Total records: 19.9M+ fundamental + 89K+ technical + 792K+ valuation
- Update frequency: Daily pipelines + Quarterly CSVs
- Format: Parquet (snappy compression)

---

## 1. Directory Structure (Root Level)

```
DATA/
├── raw/                    # 241 MB - INPUT DATA (READ ONLY)
│   ├── Metric_code/        # 0.7 MB - Metric definitions
│   ├── fundamental/        # 175 MB - Quarterly financials (CSV)
│   ├── ohlcv/             # 56 MB - OHLCV market data
│   └── news/              # 0.8 MB - News data (parquet)
│
├── processed/             # 229 MB - OUTPUT DATA (parquet)
│   ├── fundamental/       # 98 MB - Financial metrics by entity type
│   ├── technical/         # 38 MB - TA indicators & alerts
│   ├── valuation/         # 45 MB - PE/PB/PS/EV ratios
│   ├── sector/            # 7.2 MB - Aggregated sector metrics
│   ├── stock_valuation/   # 32 MB - Individual stock valuations
│   ├── market_indices/    # 1.1 MB - Index metrics
│   ├── macro_commodity/   # 0.4 MB - Macro & commodity data
│   └── forecast/          # 0.1 MB - BSC analyst forecasts
│
└── metadata/              # 124 KB - Registries & configs
    ├── sector_industry_registry.json
    ├── liquid_tickers.json
    ├── master_symbols.json
    └── generate_liquid_tickers.py
```

---

## 2. RAW Data Layer (241 MB)

### 2.1 Fundamental Data - CSV Input

**Location:** `DATA/raw/fundamental/csv/Q3_2025/`  
**Size:** 175 MB  
**Frequency:** Quarterly updates  
**Format:** Wide-format CSV (metrics as columns)  

| Entity | Files | Size | Tickers | Coverage |
|--------|-------|------|---------|----------|
| **COMPANY** | 5 files | ~155 MB | 2,246 | Balance Sheet, Income, CF (Direct/Indirect), Notes |
| **BANK** | 5 files | ~8 MB | 57 | Balance Sheet, Income, CF (Direct/Indirect), Notes |
| **INSURANCE** | 5 files | ~2 MB | 34 | Balance Sheet, Income, CF (Direct/Indirect), Notes |
| **SECURITY** | 5 files | ~10 MB | 154 | Balance Sheet, Income, CF (Direct/Indirect), Notes |

**Key CSV Files:**
```
COMPANY_BALANCE_SHEET.csv     58 MB
COMPANY_INCOME.csv            19 MB
COMPANY_CF_INDIRECT.csv       19 MB
COMPANY_CF_DIRECT.csv         4.5 MB
COMPANY_NOTE.csv              53 MB
BANK_BALANCE_SHEET.csv        1.6 MB
BANK_INCOME.csv               0.6 MB
[... 20 files total ...]
```

**Data Coverage:**
- **Time Period:** 2018-03-31 to 2025-09-30 (Q3/2025)
- **Total Rows:** 19,900,657 raw records
- **Metric Coverage:** 2,099+ raw metrics per entity
- **Format:** Wide (columns = metrics, rows = ticker × period)

**Column Naming:**
- Prefix by entity: `CIS_*` (Company Income), `CBS_*` (Company Balance Sheet), `BIS_*` (Bank Income), etc.
- Example: `CIS_10` = Net Revenue, `CIS_61` = Net Income After Tax (NPATMI), `CBS_270` = Total Assets

**Sample Structure:**
```python
# COMPANY_BALANCE_SHEET.csv
ticker, date, CBS_100, CBS_270, CBS_400, CBS_500, ...
ACB,    2025-09-30, 12345, 567890, 234567, 100000, ...
```

### 2.2 Market Data - OHLCV

**Location:** `DATA/raw/ohlcv/`  
**Size:** 56 MB  
**File:** `OHLCV_mktcap.parquet`  
**Coverage:** 457 tickers, daily data  

**Columns:**
```
symbol, date, open, high, low, close, volume, 
market_cap, shares_outstanding, trading_value
```

**Data Range:** 2020-04-07 to 2025-12-26 (5.5 years)

### 2.3 News Data

**Location:** `DATA/raw/news/`  
**Size:** 435 KB  
**Format:** Parquet  
**Files:** 4 parquet files (dated 2025-11-27 to 2025-11-28)  

Purpose: Raw news sentiment data (pre-aggregated)

### 2.4 Metadata - Metric Definitions

**Location:** `DATA/raw/Metric_code/`  

**File:** `BSC - Mô tả CSDL.xlsx` (364 KB)  
- Contains metric definitions & formula references
- Source: BSC Research metric library

---

## 3. PROCESSED Data Layer (229 MB)

### 3.1 Fundamental Data (98 MB)

**Architecture:** Multi-stage processing
```
CSV (raw) → *_full.parquet (long format) → *_financial_metrics.parquet (wide + calculated)
```

**Stage 1: Full Parquet (Long Format)**
- Location: Root of `DATA/processed/fundamental/`
- Files: `{entity}_full.parquet`
- Format: METRIC_CODE in rows (long format)
- Purpose: Bridge between raw CSV and processed metrics

| File | Rows | Tickers | Size |
|------|------|---------|------|
| company_full.parquet | 16,040,568 | 2,246 | 86 MB |
| bank_full.parquet | 611,078 | 57 | 3.3 MB |
| insurance_full.parquet | 253,302 | 34 | 1.2 MB |
| security_full.parquet | 2,995,709 | 154 | 7.8 MB |

**Stage 2: Financial Metrics (Wide Format + Calculated)**
- Location: `DATA/processed/fundamental/{entity}/`
- Files: `{entity}_financial_metrics.parquet`
- Format: Wide (columns = metrics, rows = ticker × period)
- Includes: Raw metrics + Calculated ratios

**Company Financial Metrics:**
- **File:** `company_financial_metrics.parquet`
- **Size:** 17 MB
- **Rows:** 37,145 (1,633 tickers × periods)
- **Columns:** 61 metrics

**Sample Columns:**
```
Revenue Metrics:     net_revenue, gross_profit, cogs, sga
Income Metrics:      ebit, ebitda, npatmi, depreciation, net_finance_income
Asset/Equity:        total_assets, total_liabilities, total_equity, cash, inventory
Profitability:       roe, roa, gross_profit_margin, ebit_margin, net_margin
Per-Share:           eps, bvps
Liquidity:           current_ratio, quick_ratio, cash_ratio
Solvency:            debt_to_equity, debt_to_assets, net_debt, working_capital
Activity:            asset_turnover, inventory_turnover, receivables_turnover
Trends:              net_revenue_ttm, npatmi_ttm, operating_cf_ttm
Cash Flow:           operating_cf, investment_cf, financing_cf, fcf, capex
```

**Bank Financial Metrics:**
- **File:** `bank_financial_metrics.parquet`
- **Size:** 447 KB
- **Rows:** 1,033 (46 banks × periods)
- **Columns:** 55 metrics

**Bank-Specific Columns:**
```
Income:              nii (Net Interest Income), toi (Total Operating Income), ppop, npatmi
Efficiency:          cir (Cost-to-Income), nii_toi, noii_toi
Asset Quality:       npl_ratio, debt_group2_ratio, llcr, provision_to_loan, credit_cost
Funding:             casa_ratio, ldr (Loan-to-Deposit)
Yield/Cost:          nim (Net Interest Margin - Q & TTM), asset_yield, funding_cost, loan_yield
Profitability:       roea_ttm, roaa_ttm
Growth:              nii_growth_yoy, toi_growth_yoy, ppop_growth_yoy, credit_growth_ytd
```

**Insurance & Security:**
- Insurance: 418 rows, 18 tickers, 28 columns
- Security: 2,811 rows, 146 tickers, 28 columns

**Macro Data (Sub-category):**
- **Location:** `DATA/processed/fundamental/macro/`
- **Files:** 4 parquet files
  - `interest_rates.parquet` - VN interest rate history
  - `deposit_interest_rates.parquet` - Deposit rate by bank
  - `exchange_rates.parquet` - VND/USD, etc.
  - `gov_bond_yields.parquet` - Government bond yields

### 3.2 Technical Data (38 MB)

**Location:** `DATA/processed/technical/`  
**Base:** `basic_data.parquet` (19 MB, 89,933 rows)

**Base Technical Data Columns:**
```
OHLCV:              symbol, date, open, high, low, close, volume, resolution, trading_value
Market Cap:         market_cap, shares_outstanding
Indicators:         sma_20, sma_50, sma_100, sma_200
                    ema_20, ema_50, (+ more indicators)
Metadata:           updated_at, expected_trading_value, trading_value_diff
```

**Data Range:** 2020-04-07 to 2025-12-26

**Sub-Categories:**

| Category | Files | Purpose |
|----------|-------|---------|
| **alerts/daily/** | 5 files | Latest daily alerts (breakout, MA crossover, patterns, volume spike, combined) |
| **alerts/historical/** | 5 files | Historical alert logs |
| **money_flow/** | 5 files | Individual money flow + sector money flow (1D, 1W, 1M) |
| **rs_rating/** | 1 file | Stock RS rating daily |
| **sector_breadth/** | 1 file | Sector breadth daily |
| **market_breadth/** | 1 file | Market breadth daily |
| **market_regime/** | 1 file | Market regime history |
| **vnindex/** | 1 file | VN-Index technical indicators |

**File Sizes:**
- `individual_money_flow.parquet` - 6.6 MB (largest)
- Alert files - 6-45 KB each
- Breadth/Regime files - 5-60 KB each

### 3.3 Valuation Data (45 MB)

**Location:** `DATA/processed/valuation/`  
**Organization:** By metric type, then historical

```
valuation/
├── pe/
│   └── historical/
│       └── historical_pe.parquet          (9.9 MB, 792,805 rows)
├── pb/
│   └── historical/
│       └── historical_pb.parquet          (11 MB, similar rows)
├── ps/
│   └── historical/
│       └── historical_ps.parquet          (? rows)
├── ev_ebitda/
│   └── historical/
│       ├── historical_ev_ebitda.parquet   (12 MB)
│       └── ev_ebitda_historical_test.parquet
└── vnindex/                                (VN-Index PE/PB)
```

**Data Range:** 2018-01-02 to 2025-12-26 (7+ years)

**Historical Columns (PE example):**
```
ticker, date, pe_current (TTM), pe_forward (2025/2026), 
pe_percentile, pe_5y_avg, pe_sector_avg, ...
```

**Duplicates:**
- `stock_valuation/` directory also contains:
  - `individual_pe.parquet` (9.8 MB)
  - `individual_pb.parquet` (10 MB)
  - `individual_ev_ebitda.parquet` (12 MB)
  
Note: These appear to be duplicate/alternative storage formats for same data.

### 3.4 Sector Aggregated Data (7.2 MB)

**Location:** `DATA/processed/sector/`

| File | Rows | Columns | Purpose |
|------|------|---------|---------|
| `sector_fundamental_metrics.parquet` | 589 | 48 | Aggregated sector financials |
| `sector_valuation_metrics.parquet` | 51,268 | 29 | Sector PE/PB/PS by date |
| `sector_combined_scores.parquet` | 380 | 23 | FA+TA combined scores |

**Sector Fundamental Metrics (589 rows):**
- 1 row per sector × period
- Aggregates: total revenue, net profit, ROE, ROA, NIM, NPL, etc.
- Data quality score included
- Calculations: margin, growth (YoY/QoQ)

**Sample Columns:**
```
sector_code, sector_name_vi, report_date, ticker_count, entity_types,
total_revenue, net_profit, gross_margin, net_margin, roe, roa,
nim_q, nim_ttm, npl_ratio, ldr, casa_ratio, cir,
revenue_growth_yoy, profit_growth_yoy, ...
```

### 3.5 Market Indices (1.1 MB)

**Location:** `DATA/processed/market_indices/`

| File | Rows | Purpose |
|------|------|---------|
| `vnindex_valuation.parquet` | 5,784 | VN-Index PE/PB/PS/EV historical |
| `sector_pe_summary.parquet` | 36,441 | Sector PE summary by date |

### 3.6 Macro & Commodity (0.4 MB)

**Location:** `DATA/processed/macro_commodity/`

**File:** `macro_commodity_unified.parquet` (24,883 rows, 12 columns)

**Symbols Tracked:**
- Commodities: Oil, Gold, etc.
- Macro: VND/USD, Interest rates, etc.

**Columns:**
```
date, symbol, category, name, value, unit, source,
open, high, low, close, volume
```

### 3.7 Forecast Data (0.1 MB)

**Location:** `DATA/processed/forecast/`

**BSC Research Forecasts:**

| File | Rows | Columns | Purpose |
|------|------|---------|---------|
| `bsc/bsc_individual.parquet` | 93 | 32 | Individual stock PE/PB forward 2025-2026 |
| `bsc/bsc_sector_valuation.parquet` | 15 | 14 | Sector aggregation of BSC forecasts |
| `bsc/bsc_combined.parquet` | 93 | 38 | Individual + sector metrics merged |

**BSC Individual Columns:**
```
symbol, sector, entity_type, current_price, target_price, upside_pct, rating,
rev_2025f, rev_2026f, npatmi_2025f, npatmi_2026f, eps_2025f, eps_2026f,
roe_2025f, roa_2025f, rev_growth_yoy_2025, npatmi_growth_yoy_2025,
pe_fwd_2025, pe_fwd_2026, pb_fwd_2025, pb_fwd_2026,
market_cap, total_equity, updated_at
```

**VCI Coverage:**
- `vci_coverage_universe.parquet` - VCI analyst coverage universe (85 KB)

**Last Updated:** 2025-12-28 10:45:35

---

## 4. Metadata Layer (124 KB)

**Location:** `DATA/metadata/`

| File | Size | Purpose |
|------|------|---------|
| `sector_industry_registry.json` | 94 KB | 19 sectors + 57 industries mapping |
| `master_symbols.json` | 8.2 KB | 457 tickers + metadata |
| `liquid_tickers.json` | 4.3 KB | Actively traded tickers (filtered list) |
| `generate_liquid_tickers.py` | 6.4 KB | Script to filter & maintain liquid ticker list |

**Sector Registry Content:**
```json
{
  "sectors": {
    "Ngân hàng": {
      "code": "1010",
      "tickers": ["ACB", "VCB", "BID", ...],
      "industries": {
        "1010.11": "Ngân hàng thương mại"
      }
    },
    ...
  }
}
```

---

## 5. Data Flow & Pipeline Architecture

### 5.1 Input Pipeline (Raw → Processed)

```mermaid
DATA/raw/fundamental/csv/Q3_2025/*.csv
    ↓ [csv_to_full_parquet.py]
DATA/processed/fundamental/*_full.parquet (long format, 19.9M rows)
    ↓ [run_all_calculators.py]
DATA/processed/fundamental/{entity}/*_financial_metrics.parquet (wide format, calculated)
    ↓
Dashboard & Analysis
```

**Key Scripts:**
- `PROCESSORS/fundamental/csv_to_full_parquet.py` - CSV → Full parquet conversion
- `PROCESSORS/fundamental/calculators/run_all_calculators.py` - Metric calculation
- `PROCESSORS/pipelines/run_all_daily_updates.py` - Daily pipeline orchestrator

### 5.2 Daily Update Pipeline

**Frequency:** Daily (typically overnight)  
**Duration:** ~45 minutes  
**Order of Operations:**

1. **OHLCV Update** - Fetch latest market data into `DATA/raw/ohlcv/`
2. **Technical Indicators** - Recalculate TA indicators, alerts, money flow
3. **Macro & Commodity** - Update commodity prices, interest rates
4. **Valuation Metrics** - Recalculate PE/PB using new market caps
5. **Sector Analysis** - Aggregate sector scores, FA+TA rankings

**Command:**
```bash
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

### 5.3 Quarterly Update Pipeline

**Frequency:** Quarterly (after financial statements released)  
**Input:** New CSV files downloaded to `DATA/raw/fundamental/csv/Q3_2025/`  
**Process:**

1. Place new quarter CSV files in `DATA/raw/fundamental/csv/Q3_2025/`
2. Run `PROCESSORS/fundamental/csv_to_full_parquet.py`
3. Run `PROCESSORS/fundamental/calculators/run_all_calculators.py`
4. Validate & deploy

---

## 6. Entity Coverage

### 6.1 By Entity Type

| Entity | Tickers | Files | Key Metrics | Sample |
|--------|---------|-------|------------|--------|
| **COMPANY** | 2,246 | 5 CSV | Revenue, Margins, ROE, Debt ratios | VCB, SBT, REE |
| **BANK** | 57 | 5 CSV | NII, NIM, NPL, CAR, CASA | ACB, VCB, BID, CTG |
| **INSURANCE** | 34 | 5 CSV | Net Premium, Claims, ROE | APH, PVI, BIC |
| **SECURITY** | 154 | 5 CSV | Commission, AUM, Trading | VCI, HCM, FTS |

### 6.2 By Sector (19 total)

**Major Sectors:**
```
1. Ngân hàng (Banking) - 27 banks
2. Dịch vụ tài chính (Financial Services)
3. Xây dựng và Vật liệu (Construction & Materials)
4. Thực phẩm và đồ uống (Food & Beverage)
5. Tài nguyên Cơ bản (Basic Resources)
[... 14 more ...]
```

**Stored in:** `DATA/metadata/sector_industry_registry.json`

---

## 7. Data Quality & Statistics

### 7.1 Coverage Summary

| Category | Total Records | Date Range | Update Freq |
|----------|---------------|-----------|------------|
| Fundamental | 19,900,657 | 2018-03-31 to 2025-09-30 | Q (Quarterly) |
| Technical/OHLCV | 89,933 | 2020-04-07 to 2025-12-26 | Daily |
| Valuation | 792,805+ | 2018-01-02 to 2025-12-26 | Daily |
| Sector | 51,268 | 2015-01-05 to 2025-12-26 | Daily |
| Forecast | 93-380 | Current snapshot | Quarterly |
| Macro/Commodity | 24,883 | Various | Daily |

### 7.2 Data Validation

**Legacy Comparison (Q1/2025):**
- **Company metrics:** 99.98% match with legacy system (116,889/116,908 rows)
- **VNM Q2/2025:** 100% match on all key metrics
- **Minor mismatches:** 19 in CNOT (notes) fields only

**Coverage Improvement (vs. Legacy):**
- COMPANY: 438 → 2,246 (+413%)
- BANK: 27 → 57 (+111%)
- INSURANCE: 6 → 34 (+467%)
- SECURITY: 35 → 154 (+340%)

---

## 8. File Format Details

### 8.1 Parquet Compression

**Standard:** Snappy compression  
**Benefits:**
- Columnar storage (efficient analytics)
- High compression ratio (60-80% reduction vs CSV)
- Fast read performance
- Native pandas support

**Example Sizes (Compression Ratio):**
```
company_financial_metrics.parquet:     17 MB    (60% smaller than CSV)
individual_money_flow.parquet:         6.6 MB   (highly compressed)
historical_pe.parquet:                 9.9 MB   (~70% reduction)
```

### 8.2 CSV Format (Raw Input)

**Wide Format:**
- Columns: ticker, date, metric1, metric2, ...
- Metrics as column headers (e.g., CIS_10, CBS_270)
- One row per ticker × period
- Encoding: UTF-8

**Typical Row:**
```csv
ACB, 2025-09-30, 12345.5, 67890.2, 23456.1, ...
```

---

## 9. Storage Optimization

### 9.1 Size Analysis

**Total:** 470 MB (compact for 457 stocks + 8 years history)

**Breakdown:**
- Raw CSV: 175 MB (33.3%) - Read-only, for reproducibility
- Fundamental processed: 98 MB (20.8%) - Most valuable data
- Valuation historical: 45 MB (9.6%) - Time-series analysis
- Technical: 38 MB (8.1%) - Indicators & alerts
- Sector aggregations: 7.2 MB (1.5%) - High-level analysis
- Other: 108 MB (23%) - Duplicates, forecasts, indices, macro

### 9.2 Largest Files

```
company_full.parquet:           86 MB   (widest data range, most records)
company_financial_metrics.parquet: 17 MB
individual_money_flow.parquet:   6.6 MB
sector_valuation_metrics.parquet: 7.2 MB
historical_pe.parquet:           9.9 MB
historical_pb.parquet:           11 MB
basic_data.parquet:             19 MB
OHLCV_mktcap.parquet:           56 MB   (raw market data)
```

---

## 10. Access Patterns & Best Practices

### 10.1 Reading Data

**Standard Pattern:**
```python
import pandas as pd

# Read fundamental data
company_df = pd.read_parquet('DATA/processed/fundamental/company/company_financial_metrics.parquet')

# Filter & analyze
acb_df = company_df[company_df['symbol'] == 'ACB']
print(acb_df[['symbol', 'report_date', 'roe', 'roa', 'net_margin']])
```

**Efficient Patterns:**
```python
# Load only needed columns (reduces memory)
df = pd.read_parquet('path.parquet', columns=['symbol', 'date', 'pe', 'pb'])

# Filter early with query
df = df.query("ticker in ['ACB', 'VCB'] and date >= '2024-01-01'")

# Use cached reads with Streamlit
@st.cache_data(ttl=3600)
def load_company_metrics():
    return pd.read_parquet('...')
```

### 10.2 Writing Data

**Canonical Pattern (v4.0.0):**
```python
from pathlib import Path

# Ensure directory exists
output_path = Path('DATA/processed/fundamental/company/company_financial_metrics.parquet')
output_path.parent.mkdir(parents=True, exist_ok=True)

# Write with compression
df.to_parquet(output_path, index=False, compression='snappy')
```

### 10.3 Path Resolution

**CORRECT (Using canonical paths):**
```python
from pathlib import Path

data_path = Path('DATA/processed/fundamental/company')
df = pd.read_parquet(data_path / 'company_financial_metrics.parquet')
```

**CORRECT (Using helper function):**
```python
from PROCESSORS.core.config.paths import get_data_path

path = get_data_path('processed', 'fundamental', 'company', 'company_financial_metrics.parquet')
df = pd.read_parquet(path)
```

**WRONG (Deprecated paths - will fail):**
```python
# ❌ These paths no longer exist
df = pd.read_parquet('calculated_results/fundamental/company/metrics.parquet')
df = pd.read_parquet('data_warehouse/raw/ohlcv/data.parquet')
df = pd.read_parquet('DATA/refined/valuations.parquet')
```

---

## 11. Integration Points

### 11.1 Dashboard Integration

**Streamlit pages access:**
- Company Analysis → `company_financial_metrics.parquet`
- Bank Analysis → `bank_financial_metrics.parquet`
- Valuation → `stock_valuation/*.parquet`
- Sector Overview → `sector/*_metrics.parquet`
- Technical → `technical/basic_data.parquet` + alerts
- BSC Forecast → `forecast/bsc/*.parquet`

### 11.2 Registry Integration

**Metric lookups:**
```python
from config.registries import MetricRegistry

metric_reg = MetricRegistry()
company_metrics = metric_reg.search_metrics('roe', entity_type='COMPANY')
formula = metric_reg.get_calculated_metric_formula('roe')
```

**Sector/Ticker lookups:**
```python
from config.registries import SectorRegistry

sector_reg = SectorRegistry()
ticker_info = sector_reg.get_ticker('ACB')
peers = sector_reg.get_peers('ACB')
```

---

## 12. Key Observations & Recommendations

### 12.1 Architecture Strengths

✅ **Clear separation:** Raw CSV input → Full parquet bridge → Wide processed metrics  
✅ **Comprehensive coverage:** 2,246 companies + 57 banks + 34 insurance + 154 securities  
✅ **Long time series:** 7+ years of data enables trend analysis  
✅ **Efficient storage:** Snappy-compressed parquet reduces size 60-80%  
✅ **Daily + Quarterly:** Flexible update schedule (quick market data, deep fundamentals)  
✅ **Metadata-driven:** Registries enable single source of truth  

### 12.2 Potential Optimization Areas

⚠️ **Duplicate valuations:** Both `valuation/` and `stock_valuation/` contain similar PE/PB data  
- Recommend consolidating to reduce 32 MB duplication

⚠️ **Large full parquets:** `company_full.parquet` (86 MB) rarely accessed  
- Could archive or split by year to improve startup performance

⚠️ **News data outdated:** 4 files from Nov 27-28, 2025  
- Recommend establishing automated news collection pipeline

⚠️ **Macro data minimal:** Only 24,883 records across commodities & macro  
- Consider expanding macro dataset for macroeconomic analysis

### 12.3 New Analysis Opportunities

💡 **Supply Chain Analytics:** Cross-sector dependency analysis using financial correlations  
💡 **Earnings Revision Tracking:** Compare BSC forecast updates to actual quarterly results  
💡 **Sector Rotation Signals:** Combine valuation + technical for sector timing  
💡 **Liquidity Stress Monitoring:** Track CASA ratio, NIM trends across banking sector  
💡 **Relative Strength Evolution:** Time-series RS rating analysis by sector  

---

## 13. Git Considerations

### 13.1 Committed Files (24 essential)

**Currently committed:**
- `DATA/metadata/*` - Registries & configs (always)
- `DATA/processed/*/` - All processed parquet (required for dashboard)
- `DATA/raw/Metric_code/` - Metric definitions

**Size tracked:** 83.2 MB (latest DATA/.DS_Store commit)

### 13.2 Excluded Files

**In `.gitignore`:**
- `DATA/raw/fundamental/csv/` - Too large (175 MB), regenerated quarterly
- `DATA/raw/ohlcv/OHLCV_mktcap.parquet` - ~28 MB, regenerated daily
- `DATA/raw/news/` - Transient, regenerated

---

## Summary Table: File Inventory

| Category | Location | Files | Size | Type | Update Freq |
|----------|----------|-------|------|------|------------|
| Fundamental CSV | `raw/fundamental/csv/` | 20 | 175 MB | CSV | Q |
| Full Parquets | `processed/fundamental/` | 4 | 98 MB | Parquet | Q |
| Entity Metrics | `processed/fundamental/{entity}/` | 4 | varies | Parquet | Q |
| Macro | `processed/fundamental/macro/` | 4 | 96 KB | Parquet | Ad-hoc |
| Technical Base | `processed/technical/` | 1 | 19 MB | Parquet | Daily |
| TA Alerts | `processed/technical/alerts/` | 10 | ~200 KB | Parquet | Daily |
| Money Flow | `processed/technical/money_flow/` | 5 | 6.6 MB | Parquet | Daily |
| Valuation | `processed/valuation/` | 5 | 45 MB | Parquet | Daily |
| Sector | `processed/sector/` | 3 | 7.2 MB | Parquet | Daily |
| Forecast | `processed/forecast/` | 3 | 80 KB | Parquet | Quarterly |
| Indices | `processed/market_indices/` | 2 | 1.1 MB | Parquet | Daily |
| Metadata | `metadata/` | 4 | 124 KB | JSON | Q |
| **TOTAL** | **DATA/** | **150+** | **470 MB** | Mixed | Mixed |

---

## Unresolved Questions

1. **News pipeline status:** News data is 1+ month old - is active collection suspended?
2. **Valuation duplication:** Should `stock_valuation/` be merged with `valuation/`?
3. **Archive strategy:** Should old quarters in `company_full.parquet` be archived?
4. **Macro dataset:** Why is macro data minimal? Are there plans to expand?
5. **VCI forecast:** Is VCI data actively maintained alongside BSC forecasts?

---

**Report Generated:** 2025-12-29  
**Next Scout:** Recommend re-audit after Q4/2025 financial data release  
**Access:** Data available for analysis & dashboard rendering  
