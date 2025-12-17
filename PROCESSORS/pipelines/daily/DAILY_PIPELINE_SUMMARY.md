# Daily Pipeline Summary

**Last Updated:** 2025-12-16
**Status:** All processors running successfully

---

## Quick Commands

```bash
# Full daily update (all 5 steps)
python3 PROCESSORS/pipelines/run_all_daily_updates.py

# Skip specific steps
python3 PROCESSORS/pipelines/run_all_daily_updates.py --skip-ohlcv --skip-ta

# Check logs
cat logs/daily_update_$(date +%Y%m%d).log
```

---

## Data Status Summary

| Data Type | Rows | Tickers | Latest Date | Status |
|-----------|------|---------|-------------|--------|
| **OHLCV** | 1,001,436 | 458 | 2025-12-16 | OK |
| **PE Ratio** | 789,154 | 458 | 2025-12-16 | OK |
| **PB Ratio** | 789,154 | 458 | 2025-12-16 | OK |
| **EV/EBITDA** | 668,521 | 390 | 2025-12-16 | OK |
| **Technical (TA)** | 89,805 | 458 | 2025-12-16 | OK |
| **Sector Scores** | 380 | 19 sectors | 2025-09-30 | OK |
| **Company Metrics** | 37,145 | 1,633 | Q3/2025 | OK |
| **Bank Metrics** | 1,033 | 46 | Q3/2025 | OK |
| **Insurance Metrics** | 418 | 18 | Q3/2025 | OK |
| **Security Metrics** | 2,811 | 146 | Q3/2025 | OK |

---

## Pipeline Steps

### Step 1: OHLCV Data Update
- **Script:** `PROCESSORS/technical/ohlcv/daily_ohlcv_update.py`
- **Output:** `DATA/raw/ohlcv/OHLCV_mktcap.parquet`
- **Critical:** This is the foundation - other steps depend on this

### Step 2: Technical Analysis (Full)
- **Script:** `PROCESSORS/technical/indicators/run_all_indicators.py`
- **Output:** `DATA/processed/technical/basic_data.parquet`
- **Includes:** MA, RSI, MACD, Bollinger, ATR, Volume analysis

### Step 3: Macro & Commodity Data
- **Script:** `PROCESSORS/technical/macro/daily_macro_commodity_update.py`
- **Output:** `DATA/processed/macro_commodity/macro_commodity_unified.parquet`

### Step 4: Stock Valuation
- **Script:** `PROCESSORS/pipelines/daily_valuation.py`
- **Output:**
  - `DATA/processed/valuation/pe/historical/historical_pe.parquet`
  - `DATA/processed/valuation/pb/historical/historical_pb.parquet`
  - `DATA/processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet`
  - `DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet`

### Step 5: Sector Analysis
- **Script:** `PROCESSORS/sector/sector_daily_update.py`
- **Output:**
  - `DATA/processed/sector/sector_fundamental_metrics.parquet`
  - `DATA/processed/sector/sector_valuation_metrics.parquet`
  - `DATA/processed/sector/sector_combined_scores.parquet`
- **Signals:** HOLD (370), BUY (10)

---

## Fundamental Data Processing

### Step 1: Convert CSV to Parquet

```bash
python3 PROCESSORS/fundamental/csv_to_full_parquet.py
```

**Input:** `DATA/raw/fundamental/csv/Q3_2025/*.csv`
**Output:** `DATA/processed/fundamental/*_full.parquet`

| Entity | Rows | Tickers | Metrics |
|--------|------|---------|---------|
| Company | 16,040,568 | 2,246 | 517 |
| Bank | 611,078 | 57 | 579 |
| Insurance | 253,302 | 34 | 646 |
| Security | 2,995,709 | 154 | 1,203 |
| **TOTAL** | **19,900,657** | - | - |

### Step 2: Run Calculators

```bash
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py
```

**Output:** `DATA/processed/fundamental/{entity}/{entity}_financial_metrics.parquet`

| Entity | Rows | Tickers | Columns |
|--------|------|---------|---------|
| Company | 37,145 | 1,633 | 59 |
| Bank | 1,033 | 46 | 56 |
| Insurance | 418 | 18 | 28 |
| Security | 2,811 | 146 | 28 |

---

## Logging

Daily logs are saved to: `logs/daily_update_YYYYMMDD.log`

Each run logs:
- Start time
- Each step's status (success/failure/skipped)
- Elapsed time per step
- OHLCV data status (critical check)
- Summary of output files

### Example Log Check

```bash
# Today's log
cat logs/daily_update_$(date +%Y%m%d).log

# Last 50 lines
tail -50 logs/daily_update_$(date +%Y%m%d).log

# Search for errors
grep -i "error\|failed" logs/daily_update_*.log
```

---

## Troubleshooting

### OHLCV Not Updated
- Check internet connection
- Verify vnstock_data package: `pip show vnstock-data`
- Check log for specific error

### Valuation Failed
- Ensure OHLCV is updated first
- Check if fundamental data exists in `DATA/processed/fundamental/`

### Sector Analysis Failed
- Requires both OHLCV and valuation data
- Check `DATA/processed/sector/` directory exists

---

## File Locations

```
DATA/
├── raw/
│   ├── ohlcv/OHLCV_mktcap.parquet          # Daily OHLCV data
│   └── fundamental/csv/Q3_2025/*.csv        # Quarterly fundamental CSVs
│
├── processed/
│   ├── fundamental/                         # Calculated financial metrics
│   │   ├── company/company_financial_metrics.parquet
│   │   ├── bank/bank_financial_metrics.parquet
│   │   ├── insurance/insurance_financial_metrics.parquet
│   │   └── security/security_financial_metrics.parquet
│   │
│   ├── technical/                           # Technical indicators
│   │   ├── basic_data.parquet
│   │   ├── alerts/daily/*.parquet
│   │   └── market_breadth/*.parquet
│   │
│   ├── valuation/                           # PE, PB, EV/EBITDA
│   │   ├── pe/historical/historical_pe.parquet
│   │   ├── pb/historical/historical_pb.parquet
│   │   ├── ev_ebitda/historical/historical_ev_ebitda.parquet
│   │   └── vnindex/vnindex_valuation_refined.parquet
│   │
│   └── sector/                              # Sector analysis
│       ├── sector_fundamental_metrics.parquet
│       ├── sector_valuation_metrics.parquet
│       └── sector_combined_scores.parquet

logs/
└── daily_update_YYYYMMDD.log                # Daily pipeline logs
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `config/metadata/metric_registry.json` | 2,099 raw metric definitions |
| `config/metadata/formula_registry.json` | Calculated metric formulas |
| `config/registries/sector_lookup.py` | 457 tickers, 19 sectors |

---

## Data Quality

- **Fundamental vs Legacy:** 99.98% exact match (116,889/116,908 rows)
- **Data Coverage:** 413% more company tickers than legacy
- **Date Range:** 2018-03-31 to Q3/2025 (fundamental), 2018 to today (OHLCV)
