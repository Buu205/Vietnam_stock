# 🔄 WORKFLOW DIAGRAM - Complete Data Pipeline

**Version:** v4.0.0 Canonical Architecture
**Date:** 2025-12-08

---

## 📊 COMPLETE DATA FLOW

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                 │
├─────────────────────────────────────────────────────────────────────┤
│  • BSC Fundamental CSVs (Quarterly)                                 │
│  • VNStock OHLCV API (Daily)                                        │
│  • Commodity/Macro APIs (Daily)                                     │
│  • News Sources (Daily)                                             │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA/refined/                                   │
│                      (RAW INPUT - CŨ)                               │
├─────────────────────────────────────────────────────────────────────┤
│  fundamental/current/                                               │
│    ├── company_full.parquet      (15MB, Dec 1)                     │
│    ├── bank_full.parquet         (1.7MB, Dec 1)                    │
│    ├── insurance_full.parquet    (632KB, Dec 1)                    │
│    └── security_full.parquet     (4.2MB, Dec 1)                    │
│                                                                      │
│  ⚠️ KHÔNG SỬ DỤNG - Đây là raw data cũ!                           │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PROCESSORS/                                     │
│                   (CALCULATION ENGINE)                               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 1: EXTRACTORS (Data Loading)                                │
├─────────────────────────────────────────────────────────────────────┤
│  PROCESSORS/extractors/csv_loader.py                                │
│  PROCESSORS/core/validators/bsc_csv_adapter.py                      │
│                                                                      │
│  • Load CSVs from DATA/refined/                                     │
│  • Auto-adapt BSC format → Standard format                          │
│  • Validate schema & data types                                     │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 2: TRANSFORMERS (Pure Calculations)                         │
├─────────────────────────────────────────────────────────────────────┤
│  PROCESSORS/fundamental/formulas/                                   │
│    ├── utils.py              (Helper functions)                    │
│    ├── _base_formulas.py     (30+ common formulas)                 │
│    ├── company_formulas.py   (Company-specific)                    │
│    └── bank_formulas.py      (Bank-specific)                       │
│                                                                      │
│  PROCESSORS/valuation/formulas/                                     │
│    ├── valuation_formulas.py (40+ PE/PB/EV formulas)               │
│    └── metric_mapper.py      (Entity-specific codes)               │
│                                                                      │
│  PROCESSORS/transformers/financial/                                 │
│    └── formulas.py           (600+ LOC, Week 4 formulas)           │
│                                                                      │
│  • Pure functions (no side effects)                                 │
│  • Take primitives (float/int), return Optional[float]              │
│  • Testable in isolation                                            │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 3: CALCULATORS (Orchestration)                              │
├─────────────────────────────────────────────────────────────────────┤
│  PROCESSORS/fundamental/calculators/                                │
│    ├── company_calculator.py                                       │
│    ├── bank_calculator.py                                          │
│    ├── insurance_calculator.py                                     │
│    └── security_calculator.py                                      │
│                                                                      │
│  PROCESSORS/valuation/core/                                         │
│    ├── historical_pe_calculator.py                                 │
│    ├── historical_pb_calculator.py                                 │
│    └── historical_ev_ebitda_calculator.py                          │
│                                                                      │
│  • Load data (via Extractors)                                       │
│  • Apply formulas (via Transformers)                                │
│  • Save results                                                     │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 4: VALIDATORS (Data Quality)                                │
├─────────────────────────────────────────────────────────────────────┤
│  PROCESSORS/core/validators/                                        │
│    ├── input_validator.py   (CSV validation)                       │
│    └── output_validator.py  (Metrics validation)                   │
│                                                                      │
│  • Validate input CSVs                                              │
│  • Check output ranges                                              │
│  • Business logic assertions                                        │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 5: PIPELINES (Unified Execution)                            │
├─────────────────────────────────────────────────────────────────────┤
│  PROCESSORS/pipelines/                                              │
│    ├── quarterly_report.py   (Fundamental updates)                 │
│    └── daily_update.py       (Daily market data)                   │
│                                                                      │
│  PROCESSORS/valuation/pipelines/                                    │
│    └── daily_full_valuation_pipeline.py                            │
│                                                                      │
│  • Orchestrate multiple calculators                                 │
│  • Validate at each step                                            │
│  • Auto backup before processing                                    │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA/processed/                                 │
│                   (CALCULATED RESULTS - MỚI)                        │
├─────────────────────────────────────────────────────────────────────┤
│  fundamental/                                                        │
│    ├── company/company_financial_metrics.parquet   (5.1MB, Dec 4) │
│    ├── bank/bank_financial_metrics.parquet         (260KB, Dec 4) │
│    ├── insurance/insurance_financial_metrics.parquet               │
│    └── security/security_financial_metrics.parquet                 │
│                                                                      │
│  valuation/                                                          │
│    ├── pe/historical/*.parquet                                     │
│    ├── pb/historical/*.parquet                                     │
│    └── ev_ebitda/*.parquet                                         │
│                                                                      │
│  technical/                                                          │
│    └── ohlcv/*.parquet                                             │
│                                                                      │
│  ✅ SỬ DỤNG - Calculated metrics mới nhất!                         │
└──────────────────┬──────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         WEBAPP/                                      │
│                   (Streamlit Dashboard)                              │
├─────────────────────────────────────────────────────────────────────┤
│  • Load từ DATA/processed/                                          │
│  • Display financial metrics                                        │
│  • Interactive charts & tables                                      │
│  • AI-powered analysis                                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 WORKFLOW BY USE CASE

### 1. QUARTERLY FUNDAMENTAL UPDATE

```
BSC CSV Files (Q1/Q2/Q3/Q4)
         │
         ▼
   BSCCSVAdapter
   (Auto-adapt format)
         │
         ▼
   InputValidator
   (Validate schema)
         │
         ▼
   Fundamental Calculators
   ├── company_calculator.py
   ├── bank_calculator.py
   ├── insurance_calculator.py
   └── security_calculator.py
         │
         ▼
   Transformers (Formulas)
   ├── ROE, ROA, Margins
   ├── NIM, CIR, NPL (Banks)
   └── Combined Ratio (Insurance)
         │
         ▼
   OutputValidator
   (Range checking)
         │
         ▼
   DATA/processed/fundamental/
   (Parquet files updated)
```

**Command:**
```bash
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/fundamental/calculators/company_calculator.py
```

---

### 2. DAILY VALUATION UPDATE

```
OHLCV Data (Prices)
         │
         ▼
   Valuation Calculators
   ├── historical_pe_calculator.py
   ├── historical_pb_calculator.py
   └── historical_ev_ebitda_calculator.py
         │
         ▼
   Metric Mapper
   (Get correct codes for entity)
         │
         ▼
   Valuation Formulas
   ├── calculate_pe_ratio()
   ├── calculate_pb_ratio()
   └── calculate_ev_ebitda()
         │
         ▼
   DATA/processed/valuation/
   (PE/PB/EV timeseries)
```

**Command:**
```bash
python3 PROCESSORS/valuation/pipelines/daily_full_valuation_pipeline.py
```

---

### 3. DAILY TECHNICAL UPDATE

```
VNStock API
         │
         ▼
   OHLCV Daily Updater
   (Fetch price/volume)
         │
         ▼
   Technical Indicators
   ├── Moving Averages
   ├── RSI
   ├── MACD
   └── Bollinger Bands
         │
         ▼
   DATA/processed/technical/
   (OHLCV + indicators)
```

**Command:**
```bash
python3 PROCESSORS/technical/daily_ohlcv_update.py
```

---

## 🎯 ENTITY-SPECIFIC METRIC CODES

```
┌─────────────────┬─────────┬─────────┬───────────┬──────────┐
│ METRIC          │ COMPANY │ BANK    │ INSURANCE │ SECURITY │
├─────────────────┼─────────┼─────────┼───────────┼──────────┤
│ Net Income      │ CIS_61  │ BIS_22A │ IIS_62    │ SIS_201  │
│ Total Equity    │ CBS_270 │ BBS_80  │ IBS_80    │ SBS_80   │
│ Revenue         │ CIS_10  │ BIS_1   │ IIS_1     │ SIS_1    │
│ Cash            │ CBS_20  │ BBS_20  │ IBS_20    │ SBS_20   │
└─────────────────┴─────────┴─────────┴───────────┴──────────┘
```

**Handled by:** `PROCESSORS/valuation/formulas/metric_mapper.py`

**Usage:**
```python
from PROCESSORS.valuation.formulas.metric_mapper import ValuationMetricMapper

mapper = ValuationMetricMapper()
code = mapper.get_metric_code('net_income', 'BANK')
# Returns: 'BIS_22A'
```

---

## 🧪 TESTING WORKFLOW

```
Create Formulas
       │
       ▼
Test Formulas
(python3 formulas.py)
       │
       ▼
Backup Old Output
       │
       ▼
Run Calculator
       │
       ▼
Compare Output
(compare_parquet_detailed.py)
       │
       ▼
Verify: Δ = 0.0000?
       │
       ├─ YES ─→ ✅ PASS
       │
       └─ NO ──→ ❌ Debug
```

---

## 📋 DAILY/QUARTERLY SCHEDULE

### QUARTERLY (Every 3 months)
**When:** After Q1/Q2/Q3/Q4 earnings released

1. Backup `DATA/processed/fundamental/`
2. Run 4 fundamental calculators
3. Verify output
4. Commit changes

**Time estimate:** ~10 minutes

---

### DAILY (Every trading day)
**When:** After market close (3:30 PM Vietnam time)

1. Run `daily_full_valuation_pipeline.py` (PE/PB/EV)
2. Run `daily_ohlcv_update.py` (Price data)
3. Run `daily_macro_commodity_update.py` (Macro data)
4. Check logs for errors

**Time estimate:** ~5 minutes

---

## 🚨 ERROR HANDLING

### Error: ModuleNotFoundError
```bash
# Problem: Python can't find PROCESSORS module
# Solution: Set PYTHONPATH
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard python3 script.py
```

### Error: File not found
```bash
# Problem: Looking for files in wrong folder
# Solution: Check if using DATA/processed/ (not DATA/refined/)
ls -la DATA/processed/fundamental/company/
```

### Error: Metric code not found
```bash
# Problem: Using wrong metric code for entity type
# Solution: Use ValuationMetricMapper
python3 PROCESSORS/valuation/formulas/metric_mapper.py
```

---

## 📚 RELATED DOCUMENTATION

- **QUICK_REFERENCE.md** - Quick commands cheat sheet
- **ARCHITECTURE_STANDARDS.md** - Complete architecture guide
- **DATA_FLOW_COMPLETE_MAPPING.md** - Detailed processors mapping
- **VALUATION_FORMULAS_COMPLETE_REPORT.md** - Valuation formulas guide

---

**Generated by:** Claude Code
**Version:** v4.0.0 Canonical Architecture
**Date:** 2025-12-08
**Status:** ✅ Production Ready
