# 📊 DATA FLOW - COMPLETE MAPPING

**Project:** Vietnam Stock Dashboard
**Created:** 2025-12-08
**Purpose:** Chi tiết toàn bộ quy trình RAW → PROCESSOR → RESULT

---

## 🏗️ PROCESSORS ARCHITECTURE OVERVIEW

```
PROCESSORS/
├── core/              ← Utilities & shared components
├── transformers/      ← Pure calculation functions (NEW - Week 4)
├── extractors/        ← Data loading layer (Week 3)
├── fundamental/       ← Financial metrics processing
├── valuation/         ← PE/PB/EV calculations
├── technical/         ← OHLCV & technical indicators
├── news/              ← News aggregation
├── forecast/          ← BSC forecast
└── pipelines/         ← Unified orchestration (Week 2)
```

---

## 📋 I. FUNDAMENTAL DATA FLOW

### 1.1 Company Financial Metrics

```
┌──────────────────────────────────────────────────────────────────┐
│ RAW DATA (Input)                                                  │
└──────────────────────────────────────────────────────────────────┘
DATA/refined/fundamental/current/company_full.parquet (15MB)
  ↓
  ├─ Columns: SECURITY_CODE, METRIC_CODE, REPORT_DATE, METRIC_VALUE, FREQ_CODE
  ├─ Format: Long format (each row = 1 metric for 1 company at 1 date)
  └─ Source: BSC fundamental data

┌──────────────────────────────────────────────────────────────────┐
│ PROCESSOR (Processing)                                            │
└──────────────────────────────────────────────────────────────────┘
PROCESSORS/fundamental/calculators/company_calculator.py
  │
  ├─ Step 1: Load raw data
  │   └─ Method: BaseFinancialCalculator.load_data()
  │       └─ Reads: DATA/refined/fundamental/current/company_full.parquet
  │
  ├─ Step 2: Pivot to wide format
  │   └─ Method: BaseFinancialCalculator.pivot_data()
  │       └─ Transforms: Long → Wide (columns = metric codes)
  │
  ├─ Step 3: Calculate metrics using FORMULAS
  │   ├─ Uses: PROCESSORS/fundamental/formulas/company_formulas.py
  │   ├─ Uses: PROCESSORS/fundamental/formulas/_base_formulas.py
  │   ├─ Uses: PROCESSORS/fundamental/formulas/utils.py
  │   │
  │   └─ Calculations:
  │       ├─ ROE = calculate_roe(net_income, equity)
  │       ├─ ROA = calculate_roa(net_income, assets)
  │       ├─ Margins = calculate_gross_margin(gross_profit, revenue)
  │       ├─ Growth = yoy_growth(current, previous)
  │       └─ ... (50+ metrics)
  │
  ├─ Step 4: Format output
  │   └─ Method: BaseFinancialCalculator.format_output()
  │       └─ Standardizes: Dates, column names, data types
  │
  └─ Step 5: Save results
      └─ Method: BaseFinancialCalculator.save_results()
          └─ Writes: DATA/processed/fundamental/company/

┌──────────────────────────────────────────────────────────────────┐
│ RESULT (Output)                                                   │
└──────────────────────────────────────────────────────────────────┘
DATA/processed/fundamental/company/company_financial_metrics.parquet (5.1MB)
  ↓
  ├─ Columns (54): symbol, report_date, year, quarter, net_revenue,
  │                gross_profit, ebit, ebitda, npatmi, roe, roa, eps, ...
  ├─ Format: Wide format (each row = all metrics for 1 company at 1 date)
  ├─ Rows: 12,033 company-quarter records
  └─ Ready for: Streamlit dashboard, MCP queries

┌──────────────────────────────────────────────────────────────────┐
│ USAGE                                                             │
└──────────────────────────────────────────────────────────────────┘
WEBAPP/pages/company_dashboard.py
  └─ Loads: DATA/processed/fundamental/company/company_financial_metrics.parquet
      └─ Displays: Financial charts, metrics, comparisons
```

**Command to run:**
```bash
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/fundamental/calculators/company_calculator.py
```

---

### 1.2 Bank Financial Metrics

```
┌──────────────────────────────────────────────────────────────────┐
│ RAW → PROCESSOR → RESULT                                          │
└──────────────────────────────────────────────────────────────────┘

RAW:
DATA/refined/fundamental/current/bank_full.parquet (1.7MB)

PROCESSOR:
PROCESSORS/fundamental/calculators/bank_calculator.py
  ├─ Uses formulas: PROCESSORS/fundamental/formulas/bank_formulas.py
  ├─ Calculations:
  │   ├─ NIM (Net Interest Margin)
  │   ├─ CIR (Cost-to-Income Ratio)
  │   ├─ NPL Ratio (Non-Performing Loans)
  │   ├─ LDR (Loan-to-Deposit Ratio)
  │   ├─ CASA Ratio
  │   └─ ROE, ROA, etc.
  └─ Metric codes: BIS_22A (net income), BBS_80 (equity), etc.

RESULT:
DATA/processed/fundamental/bank/bank_financial_metrics.parquet (260KB)
  ├─ Columns (42): symbol, nim_q, cir, npl_ratio, ldr, roea_ttm, ...
  └─ Rows: 775 bank-quarter records

USAGE:
WEBAPP/pages/bank_dashboard.py
```

**Command:**
```bash
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/fundamental/calculators/bank_calculator.py
```

---

### 1.3 Insurance & Security (Same pattern)

**Insurance:**
```
RAW:    DATA/refined/fundamental/current/insurance_full.parquet
PROC:   PROCESSORS/fundamental/calculators/insurance_calculator.py
RESULT: DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet
```

**Security:**
```
RAW:    DATA/refined/fundamental/current/security_full.parquet
PROC:   PROCESSORS/fundamental/calculators/security_calculator.py
RESULT: DATA/processed/fundamental/security/security_financial_metrics.parquet
```

---

## 📊 II. VALUATION DATA FLOW

### 2.1 PE Ratio (Price-to-Earnings)

```
┌──────────────────────────────────────────────────────────────────┐
│ RAW DATA (Multiple Inputs)                                        │
└──────────────────────────────────────────────────────────────────┘
Input 1: DATA/refined/fundamental/current/company_full.parquet
  └─ Metrics: CIS_61 (net income for COMPANY)
              BIS_22A (net income for BANK)
              IIS_62 (net income for INSURANCE)
              SIS_201 (net income for SECURITY)

Input 2: DATA/raw/ohlcv/OHLCV_mktcap.parquet
  └─ Columns: ticker, time, close (price), volume, market_cap

Input 3: DATA/metadata/ticker_details.json
  └─ Metadata: entity_type, shares_outstanding, sector

┌──────────────────────────────────────────────────────────────────┐
│ PROCESSOR (NEW - Formula-Based)                                   │
└──────────────────────────────────────────────────────────────────┘
PROCESSORS/valuation/calculators/pe_calculator_with_formulas.py
  │
  ├─ Step 1: Get entity type
  │   └─ From: DATA/metadata/ticker_details.json
  │       └─ Example: VCB → entity_type = 'BANK'
  │
  ├─ Step 2: Get correct metric code
  │   └─ Uses: PROCESSORS/valuation/formulas/metric_mapper.py
  │       ├─ mapper.get_metric_code('net_income', 'BANK')
  │       └─ Returns: 'BIS_22A'
  │
  ├─ Step 3: Load net income data
  │   └─ Filter: fundamental_data[
  │                (METRIC_CODE == 'BIS_22A') &
  │                (SECURITY_CODE == 'VCB')
  │              ]
  │       └─ Calculate TTM (4 quarters sum)
  │
  ├─ Step 4: Calculate EPS using FORMULA
  │   └─ Uses: PROCESSORS/valuation/formulas/valuation_formulas.py
  │       └─ eps = calculate_eps(net_income_ttm, shares_outstanding)
  │
  ├─ Step 5: Get price data
  │   └─ From: OHLCV_mktcap.parquet
  │       └─ Example: VCB price = 85,000 VND
  │
  ├─ Step 6: Calculate PE using FORMULA
  │   └─ Uses: PROCESSORS/valuation/formulas/valuation_formulas.py
  │       └─ pe = calculate_pe_ratio(price=85000, eps=6500)
  │           └─ Result: 13.08x
  │
  └─ Step 7: Save timeseries
      └─ Creates: Daily PE ratio for each date

┌──────────────────────────────────────────────────────────────────┐
│ LEGACY PROCESSOR (OLD - Inline formulas)                          │
└──────────────────────────────────────────────────────────────────┘
PROCESSORS/valuation/core/historical_pe_calculator.py
  ├─ Same logic but with INLINE calculations
  ├─ Hardcoded metric codes:
  │   └─ self.net_income_metrics = {
  │         'company': 'CIS_61',
  │         'bank': 'BIS_22A', ...
  │       }
  └─ Inline calculation: pe = price / eps

┌──────────────────────────────────────────────────────────────────┐
│ RESULT                                                            │
└──────────────────────────────────────────────────────────────────┘
DATA/processed/valuation/pe/historical/{ticker}_pe_history.parquet
  ├─ Columns: date, symbol, price, eps_ttm, pe_ratio
  ├─ One file per ticker (e.g., VCB_pe_history.parquet)
  └─ Daily timeseries from 2018 to present

USAGE:
WEBAPP/pages/valuation_dashboard.py
  └─ Shows: PE trends, sector PE, historical charts
```

**Commands:**
```bash
# NEW (Formula-based)
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/valuation/calculators/pe_calculator_with_formulas.py

# OLD (Still working - legacy)
python3 PROCESSORS/valuation/core/historical_pe_calculator.py
```

---

### 2.2 PB Ratio & EV/EBITDA (Same pattern)

**PB Ratio:**
```
RAW:    Fundamental (equity) + OHLCV (price)
PROC:   PROCESSORS/valuation/core/historical_pb_calculator.py
        └─ Uses: metric_mapper for equity codes (CBS_270, BBS_80, ...)
RESULT: DATA/processed/valuation/pb/historical/
```

**EV/EBITDA:**
```
RAW:    Fundamental (ebitda, debt, cash) + OHLCV (market cap)
PROC:   PROCESSORS/valuation/core/historical_ev_ebitda_calculator.py
        └─ Formulas: calculate_enterprise_value(), calculate_ev_ebitda()
RESULT: DATA/processed/valuation/ev_ebitda/
```

---

## 🔧 III. TECHNICAL DATA FLOW

### 3.1 OHLCV (Price & Volume)

```
RAW:
DATA/raw/ohlcv/OHLCV_mktcap.parquet
  └─ Columns: ticker, time, open, high, low, close, volume, market_cap

PROCESSOR:
PROCESSORS/technical/ohlcv/ohlcv_daily_updater.py
  └─ Fetches: Latest OHLCV from vnstock API
  └─ Updates: Existing parquet with new data

RESULT:
DATA/processed/technical/ohlcv/OHLCV_updated.parquet
  └─ Daily OHLCV for all tickers

PIPELINE:
PROCESSORS/technical/pipelines/daily_ohlcv_update.py
  └─ Runs: ohlcv_daily_updater.py
```

---

### 3.2 Technical Indicators

```
RAW:
DATA/processed/technical/ohlcv/OHLCV_updated.parquet

PROCESSOR:
PROCESSORS/technical/indicators/technical_processor.py
  ├─ Uses: PROCESSORS/transformers/financial/formulas.py (if needed)
  └─ Calculates:
      ├─ Moving Averages (MA5, MA10, MA20, MA50, MA200)
      ├─ RSI (Relative Strength Index)
      ├─ MACD (Moving Average Convergence Divergence)
      ├─ Bollinger Bands
      └─ Volume indicators

RESULT:
DATA/processed/technical/indicators/
  ├─ ma_data.parquet
  ├─ rsi_data.parquet
  ├─ macd_data.parquet
  └─ bollinger_data.parquet

PIPELINE:
PROCESSORS/technical/pipelines/daily_full_technical_pipeline.py
  └─ Orchestrates: All technical indicator calculations
```

---

## 🎯 IV. TRANSFORMERS LAYER (NEW - Week 4)

### 4.1 Financial Transformers

```
PROCESSORS/transformers/financial/formulas.py
  ├─ Pure calculation functions (30+ formulas)
  ├─ Used by: fundamental calculators, valuation calculators
  │
  └─ Functions:
      ├─ roe(net_income, equity) → ROE %
      ├─ roa(net_income, assets) → ROA %
      ├─ gross_margin(gross_profit, revenue) → Margin %
      ├─ qoq_growth(current, previous) → Growth %
      ├─ yoy_growth(current, previous) → Growth %
      ├─ safe_divide(num, denom) → Safe division
      └─ ... (30+ more)
```

**Integration with Calculators:**
```python
# In company_calculator.py
from PROCESSORS/transformers/financial/formulas import roe, roa

df['roe'] = df.apply(
    lambda row: roe(row['net_income'], row['equity']),
    axis=1
)
```

**Benefits:**
- ✅ Testable in isolation
- ✅ Reusable across all calculators
- ✅ Single source of truth for formulas
- ✅ No duplication

---

## 🔄 V. COMPLETE DATA FLOW DIAGRAM

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           DATA SOURCES (RAW)                              │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
   ┌─────────┐              ┌──────────────┐            ┌─────────────┐
   │Fundamental              │   OHLCV      │            │  Metadata   │
   │(BSC CSV)│              │  (VNStock)   │            │   (JSON)    │
   └─────────┘              └──────────────┘            └─────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        DATA/refined/ (Input Layer)                        │
│  - fundamental/current/*.parquet (Long format, raw metrics)               │
│  - ohlcv/*.parquet (Price & volume data)                                 │
│  - metadata/*.json (Ticker details, sectors)                              │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        PROCESSORS/ (Processing Layer)                     │
└──────────────────────────────────────────────────────────────────────────┘
        │
        ├─── LAYER 1: EXTRACTORS (Data Loading)
        │    └─ PROCESSORS/extractors/csv_loader.py
        │        └─ Loads raw data, handles BSC CSV format
        │
        ├─── LAYER 2: TRANSFORMERS (Pure Calculations)
        │    ├─ PROCESSORS/transformers/financial/formulas.py
        │    │   └─ Pure functions: roe(), roa(), margins, growth
        │    └─ PROCESSORS/fundamental/formulas/
        │        ├─ utils.py (safe_divide, yoy_growth)
        │        ├─ _base_formulas.py (ROE, ROA, margins)
        │        ├─ company_formulas.py
        │        └─ bank_formulas.py
        │
        ├─── LAYER 3: CALCULATORS (Orchestration)
        │    ├─ PROCESSORS/fundamental/calculators/
        │    │   ├─ company_calculator.py
        │    │   ├─ bank_calculator.py
        │    │   ├─ insurance_calculator.py
        │    │   └─ security_calculator.py
        │    │
        │    ├─ PROCESSORS/valuation/calculators/
        │    │   ├─ pe_calculator_with_formulas.py (NEW)
        │    │   └─ historical_pe_calculator.py (OLD)
        │    │
        │    └─ PROCESSORS/technical/indicators/
        │        ├─ technical_processor.py
        │        └─ market_breadth_processor.py
        │
        ├─── LAYER 4: VALIDATORS (Data Quality)
        │    └─ PROCESSORS/core/validators/
        │        ├─ input_validator.py
        │        └─ output_validator.py
        │
        └─── LAYER 5: PIPELINES (Unified Execution)
             ├─ PROCESSORS/pipelines/
             │   ├─ quarterly_report.py (Run all fundamental calculators)
             │   └─ daily_update.py (Run daily updates)
             │
             ├─ PROCESSORS/fundamental/pipelines/ (Empty - TODO)
             ├─ PROCESSORS/technical/pipelines/
             │   ├─ daily_full_technical_pipeline.py
             │   └─ daily_ohlcv_update.py
             │
             └─ PROCESSORS/valuation/pipelines/
                 └─ daily_full_valuation_pipeline.py
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      DATA/processed/ (Output Layer)                       │
│  - fundamental/{company,bank,insurance,security}/*.parquet                │
│  - valuation/{pe,pb,ev_ebitda}/*.parquet                                 │
│  - technical/{ohlcv,indicators}/*.parquet                                │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         WEBAPP/ (Presentation Layer)                      │
│  - Streamlit dashboard reads processed data                               │
│  - Displays charts, metrics, comparisons                                 │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 📝 VI. PYTHON FILES - DETAILED MAPPING

### 6.1 Fundamental Processing

| File | Purpose | Input | Output | Status |
|------|---------|-------|--------|--------|
| **company_calculator.py** | Calculate company metrics | refined/fundamental/current/company_full.parquet | processed/fundamental/company/*.parquet | ✅ Active |
| **bank_calculator.py** | Calculate bank metrics | refined/fundamental/current/bank_full.parquet | processed/fundamental/bank/*.parquet | ✅ Active |
| **insurance_calculator.py** | Calculate insurance metrics | refined/fundamental/current/insurance_full.parquet | processed/fundamental/insurance/*.parquet | ✅ Active |
| **security_calculator.py** | Calculate security metrics | refined/fundamental/current/security_full.parquet | processed/fundamental/security/*.parquet | ✅ Active |
| **base_financial_calculator.py** | Base class for all calculators | - | - | ✅ Active |

---

### 6.2 Valuation Processing

| File | Purpose | Input | Output | Status |
|------|---------|-------|--------|--------|
| **pe_calculator_with_formulas.py** | PE ratio (formula-based) | fundamental + ohlcv | processed/valuation/pe/*.parquet | ✅ NEW |
| **historical_pe_calculator.py** | PE ratio (legacy) | fundamental + ohlcv | processed/valuation/pe/*.parquet | ⚠️ Legacy |
| **historical_pb_calculator.py** | PB ratio | fundamental + ohlcv | processed/valuation/pb/*.parquet | ✅ Active |
| **historical_ev_ebitda_calculator.py** | EV/EBITDA | fundamental + ohlcv | processed/valuation/ev_ebitda/*.parquet | ✅ Active |
| **daily_full_valuation_pipeline.py** | Orchestrate all valuation calcs | - | All valuation outputs | ✅ Pipeline |

---

### 6.3 Technical Processing

| File | Purpose | Input | Output | Status |
|------|---------|-------|--------|--------|
| **ohlcv_daily_updater.py** | Update OHLCV data | VNStock API | processed/technical/ohlcv/*.parquet | ✅ Active |
| **technical_processor.py** | Calculate technical indicators | OHLCV | processed/technical/indicators/*.parquet | ✅ Active |
| **market_breadth_processor.py** | Market breadth indicators | OHLCV | processed/technical/market_breadth/*.parquet | ✅ Active |
| **daily_full_technical_pipeline.py** | Orchestrate all technical calcs | - | All technical outputs | ✅ Pipeline |

---

### 6.4 Formulas & Transformers

| File | Purpose | Used By | Type | Status |
|------|---------|---------|------|--------|
| **transformers/financial/formulas.py** | 30+ pure calculation functions | Calculators | Pure functions | ✅ Week 4 |
| **fundamental/formulas/utils.py** | Helper functions | All calculators | Utilities | ✅ Week 2 |
| **fundamental/formulas/_base_formulas.py** | Common formulas (ROE, ROA) | All calculators | Pure functions | ✅ Week 2 |
| **fundamental/formulas/company_formulas.py** | Company-specific formulas | company_calculator | Class-based | ✅ Existing |
| **fundamental/formulas/bank_formulas.py** | Bank-specific formulas | bank_calculator | Class-based | ✅ Existing |
| **valuation/formulas/valuation_formulas.py** | 40+ valuation formulas | Valuation calculators | Pure functions | ✅ Dec 8 |
| **valuation/formulas/metric_mapper.py** | Entity-specific metric codes | Valuation calculators | Mapper | ✅ Dec 8 |

---

## 🎯 VII. WORKFLOW - WHEN TO RUN WHAT

### Daily Updates:

```bash
# 1. Update OHLCV (Price data)
python3 PROCESSORS/technical/pipelines/daily_ohlcv_update.py

# 2. Update Valuation (PE, PB, EV/EBITDA)
python3 PROCESSORS/valuation/pipelines/daily_full_valuation_pipeline.py

# 3. Update Technical Indicators
python3 PROCESSORS/technical/pipelines/daily_full_technical_pipeline.py
```

### Quarterly Updates:

```bash
# Run all fundamental calculators
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/pipelines/quarterly_report.py --quarter 4 --year 2025
```

Or individual:
```bash
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/fundamental/calculators/company_calculator.py

PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/fundamental/calculators/bank_calculator.py
```

---

## ✅ SUMMARY

### Key Takeaways:

**1. Data Folders:**
- `DATA/refined/` = RAW input (CŨ, Dec 1)
- `DATA/processed/` = Calculated output (MỚI, Dec 4+)

**2. Processor Layers:**
- **Extractors** → Load data
- **Transformers** → Pure calculations (formulas)
- **Calculators** → Orchestration (load → calc → save)
- **Validators** → Data quality
- **Pipelines** → Unified execution

**3. PROCESSORS/transformers:**
- **transformers/financial/formulas.py** → 30+ pure functions (Week 4)
- Used by: fundamental & valuation calculators
- Benefits: Testable, reusable, maintainable

**4. PROCESSORS/valuation:**
- **core/** → Legacy calculators (inline formulas)
- **calculators/** → Modern calculators (some formula-based)
- **formulas/** → Pure valuation formulas (NEW - Dec 8)
  - valuation_formulas.py (PE, PB, EV/EBITDA)
  - metric_mapper.py (Entity-specific codes)

**5. Commands:**
- Daily: Run pipelines (ohlcv, valuation, technical)
- Quarterly: Run fundamental calculators
- Test: Compare outputs before committing

---

**Generated by:** Claude Code
**Date:** 2025-12-08
**Version:** Complete Mapping v1.0
