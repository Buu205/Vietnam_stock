# 🏗️ ARCHITECTURE STANDARDS & WORKFLOW GUIDE

**Project:** Vietnam Stock Dashboard
**Version:** 4.0 (Formula-Based Architecture)
**Last Updated:** 2025-12-08
**Purpose:** Quy chuẩn architecture & workflow để biết chạy file nào khi cập nhật

---

## 📁 1. DATA ARCHITECTURE - FOLDER STRUCTURE

### ⚠️ QUAN TRỌNG: DATA/refined vs DATA/processed

```
DATA/
├── refined/          ← CŨ (Raw data from source)
│   ├── fundamental/
│   │   └── current/
│   │       ├── company_full.parquet   (15MB, Dec 1)
│   │       ├── bank_full.parquet      (1.7MB, Dec 1)
│   │       ├── insurance_full.parquet (632KB, Dec 1)
│   │       └── security_full.parquet  (4.2MB, Dec 1)
│   ├── market/
│   ├── technical/
│   └── valuation/
│
└── processed/        ← MỚI (Calculated results)
    ├── fundamental/
    │   ├── company/
    │   │   └── company_financial_metrics.parquet (5.1MB, Dec 4) ← USE THIS
    │   ├── bank/
    │   │   └── bank_financial_metrics.parquet (260KB, Dec 4)    ← USE THIS
    │   ├── insurance/
    │   │   └── insurance_financial_metrics.parquet
    │   ├── security/
    │   │   └── security_financial_metrics.parquet
    │   └── archive_q3_2025/ ← Backups
    ├── technical/
    ├── commodity/
    └── valuation/
```

### 📋 QUY CHUẨN:

**✅ USE:**
- `DATA/processed/` - **MỚI**, chứa calculated results
- Được tạo bởi calculators trong `PROCESSORS/`
- Update: Dec 4-5, 2025

**❌ DON'T USE (Deprecated):**
- `DATA/refined/` - **CŨ**, raw data from source
- Chưa qua calculation
- Update: Dec 1, 2025 (cũ hơn)

**🎯 RULE:**
```
refined/   → Input  (Raw fundamental data from BSC/VNStock)
processed/ → Output (Calculated financial metrics)
```

---

## 🏛️ 2. PROCESSOR ARCHITECTURE

### 2.1 Fundamental Processors

```
PROCESSORS/fundamental/
├── calculators/          ← ORCHESTRATION (Load data, apply formulas, save)
│   ├── base_financial_calculator.py   ← Base class cho tất cả
│   ├── company_calculator.py          ← Company metrics
│   ├── bank_calculator.py             ← Bank metrics
│   ├── insurance_calculator.py        ← Insurance metrics
│   ├── security_calculator.py         ← Security metrics
│   ├── calculator_integration_test.py ← Integration tests
│   ├── calculator_usage_example.py    ← Usage examples
│   └── README.md                      ← Documentation
│
├── formulas/            ← PURE CALCULATIONS (Business logic)
│   ├── utils.py                ← Helper functions (safe_divide, yoy_growth)
│   ├── _base_formulas.py       ← Common formulas (ROE, ROA, margins)
│   ├── company_formulas.py     ← Company-specific formulas
│   └── bank_formulas.py        ← Bank-specific formulas
│
└── base/                ← DEPRECATED (Old architecture)
    └── ... (archived)
```

### 2.2 Valuation Processors

```
PROCESSORS/valuation/
├── calculators/         ← ORCHESTRATION
│   ├── historical_pe_calculator.py
│   ├── historical_pb_calculator.py
│   ├── historical_ev_ebitda_calculator.py
│   └── pe_calculator_with_formulas.py  ← NEW (Formula-based example)
│
├── formulas/           ← PURE CALCULATIONS (NEW - Dec 8)
│   ├── valuation_formulas.py  ← 40+ valuation formulas (PE, PB, EV/EBITDA)
│   └── metric_mapper.py       ← Entity-specific metric codes
│
└── core/               ← OLD (Legacy calculators with inline formulas)
    ├── historical_pe_calculator.py
    ├── historical_pb_calculator.py
    └── historical_ev_ebitda_calculator.py
```

### 📋 QUY CHUẨN PHÂN TẦNG:

```
┌─────────────────────────────────────────────┐
│  CALCULATORS (Orchestration Layer)          │
│  - Load data                                 │
│  - Apply formulas                            │
│  - Save results                              │
│  - Handle entity-specific codes              │
└─────────────────────────────────────────────┘
                   ↓ uses
┌─────────────────────────────────────────────┐
│  FORMULAS (Business Logic Layer)            │
│  - Pure calculation functions                │
│  - Testable in isolation                     │
│  - Reusable across calculators               │
└─────────────────────────────────────────────┘
                   ↓ uses
┌─────────────────────────────────────────────┐
│  UTILS (Helper Functions)                    │
│  - safe_divide, to_percentage                │
│  - yoy_growth, qoq_growth                    │
└─────────────────────────────────────────────┘
```

---

## 🔄 3. WORKFLOW - CHẠY FILE NÀO KHI CẬP NHẬT?

### 3.1 Cập nhật Fundamental Data (Quarterly)

**Khi nào chạy:** Khi có báo cáo tài chính mới (quarterly)

**Chạy theo thứ tự:**

```bash
# Step 1: Update company metrics
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/fundamental/calculators/company_calculator.py

# Step 2: Update bank metrics
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/fundamental/calculators/bank_calculator.py

# Step 3: Update insurance metrics
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/fundamental/calculators/insurance_calculator.py

# Step 4: Update security metrics
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/fundamental/calculators/security_calculator.py
```

**Output:**
```
DATA/processed/fundamental/
├── company/company_financial_metrics.parquet   ← Updated
├── bank/bank_financial_metrics.parquet         ← Updated
├── insurance/insurance_financial_metrics.parquet ← Updated
└── security/security_financial_metrics.parquet  ← Updated
```

---

### 3.2 Cập nhật Valuation Data (Daily)

**Khi nào chạy:** Hàng ngày khi có giá mới

**Option A: Chạy toàn bộ valuation pipeline**
```bash
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/valuation/pipelines/daily_full_valuation_pipeline.py
```

**Option B: Chạy từng metric riêng**
```bash
# PE ratio
python3 PROCESSORS/valuation/core/historical_pe_calculator.py

# PB ratio
python3 PROCESSORS/valuation/core/historical_pb_calculator.py

# EV/EBITDA
python3 PROCESSORS/valuation/core/historical_ev_ebitda_calculator.py
```

**Output:**
```
DATA/processed/valuation/
├── pe/historical/*.parquet      ← PE timeseries
├── pb/historical/*.parquet      ← PB timeseries
└── ev_ebitda/*.parquet          ← EV/EBITDA timeseries
```

---

### 3.3 Cập nhật Technical Data (Daily)

**Khi nào chạy:** Hàng ngày khi có OHLCV mới

```bash
python3 PROCESSORS/technical/daily_ohlcv_update.py
```

**Output:**
```
DATA/processed/technical/
└── ohlcv/*.parquet
```

---

## 📊 4. FORMULA-BASED ARCHITECTURE (NEW)

### 4.1 Structure

```
Formulas/
├── utils.py                ← Helper functions
├── _base_formulas.py       ← Common formulas (all entities)
├── company_formulas.py     ← Company-specific
├── bank_formulas.py        ← Bank-specific
├── insurance_formulas.py   ← Insurance-specific (TODO)
├── security_formulas.py    ← Security-specific (TODO)
└── valuation_formulas.py   ← Valuation metrics (PE, PB, EV)
```

### 4.2 Usage Pattern

**Before (Inline - Old):**
```python
# In calculator
df['roe'] = (df['net_income'] / df['equity']) * 100
df['roa'] = (df['net_income'] / df['assets']) * 100
```

**After (Formula-Based - New):**
```python
# Import formulas
from PROCESSORS.fundamental.formulas._base_formulas import calculate_roe, calculate_roa

# Apply formulas
df['roe'] = df.apply(
    lambda row: calculate_roe(row['net_income'], row['equity']),
    axis=1
)
df['roa'] = df.apply(
    lambda row: calculate_roa(row['net_income'], row['assets']),
    axis=1
)
```

**Benefits:**
- ✅ Testable in isolation
- ✅ Reusable across calculators
- ✅ Centralized business logic
- ✅ Easier to maintain

---

## 🎯 5. ENTITY-SPECIFIC METRIC CODES

### 5.1 Problem

Mỗi entity type dùng metric codes khác nhau:

```
Net Income:
- COMPANY:   CIS_61
- BANK:      BIS_22A
- INSURANCE: IIS_62
- SECURITY:  SIS_201
```

### 5.2 Solution: Metric Mapper

**File:** `PROCESSORS/valuation/formulas/metric_mapper.py`

**Usage:**
```python
from PROCESSORS.valuation.formulas.metric_mapper import ValuationMetricMapper

mapper = ValuationMetricMapper()

# Get correct metric code for entity
entity_type = 'BANK'  # From ticker metadata
net_income_code = mapper.get_metric_code('net_income', entity_type)
# Returns: 'BIS_22A'

# Load data with correct code
df = fundamental_data[
    (fundamental_data['METRIC_CODE'] == net_income_code)
]
```

**Supported metrics:**
- `net_income` - For EPS, PE
- `total_equity` - For BVPS, PB
- `revenue` - For PS
- `operating_cf` - For PCF
- `cash` - For EV
- `total_debt` - For EV

---

## 🧪 6. TESTING WORKFLOW

### 6.1 Test Formulas

```bash
# Test fundamental formulas
python3 PROCESSORS/fundamental/formulas/utils.py
python3 PROCESSORS/fundamental/formulas/_base_formulas.py

# Test valuation formulas
cd PROCESSORS/valuation/formulas
python3 valuation_formulas.py
python3 metric_mapper.py
```

### 6.2 Test Calculators

```bash
# Test company calculator
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/fundamental/calculators/calculator_usage_example.py

# Test integration
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/fundamental/calculators/calculator_integration_test.py
```

### 6.3 Compare Output (Before/After)

```bash
# Backup current output
cp DATA/processed/fundamental/company/company_financial_metrics.parquet \
   backup_company_OLD.parquet

# Run calculator
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/fundamental/calculators/company_calculator.py

# Compare
python3 compare_parquet_detailed.py
```

---

## 📝 7. CHECKLIST KHI CẬP NHẬT

### ✅ Quarterly Update (Fundamental):

- [ ] Có báo cáo tài chính mới (Q1/Q2/Q3/Q4)
- [ ] Backup `DATA/processed/fundamental/` trước
- [ ] Chạy `company_calculator.py`
- [ ] Chạy `bank_calculator.py`
- [ ] Chạy `insurance_calculator.py`
- [ ] Chạy `security_calculator.py`
- [ ] Verify output với `compare_parquet_detailed.py`
- [ ] Commit changes nếu OK

### ✅ Daily Update (Valuation):

- [ ] Giá stock mới từ OHLCV
- [ ] Chạy `daily_full_valuation_pipeline.py`
- [ ] Hoặc chạy riêng PE/PB/EV calculators
- [ ] Check output trong `DATA/processed/valuation/`

### ✅ Daily Update (Technical):

- [ ] OHLCV data mới
- [ ] Chạy `daily_ohlcv_update.py`
- [ ] Check output trong `DATA/processed/technical/`

---

## 🚨 8. COMMON ISSUES & SOLUTIONS

### Issue 1: ModuleNotFoundError

```bash
# Solution: Set PYTHONPATH
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard python3 script.py
```

### Issue 2: File not found

```bash
# Check if using correct data folder
ls -la DATA/processed/fundamental/company/

# Should see company_financial_metrics.parquet (Dec 4+)
# NOT DATA/refined/ (older, Dec 1)
```

### Issue 3: Output không thay đổi

```bash
# Formulas chưa được integrate vào calculator
# Calculator vẫn dùng inline logic

# Solution:
# 1. Kiểm tra calculator có import formulas chưa
# 2. Nếu chưa, cần update calculator code
```

### Issue 4: Metric codes không đúng

```bash
# Use metric mapper
from PROCESSORS.valuation.formulas.metric_mapper import ValuationMetricMapper

mapper = ValuationMetricMapper()
code = mapper.get_metric_code('net_income', entity_type)
```

---

## 📚 9. DOCUMENTATION FILES

### Core Documentation:

```
/CLAUDE.md                              ← Project overview
/ARCHITECTURE_STANDARDS.md              ← This file (quy chuẩn)
/CURRENT_STATUS.md                      ← Current implementation status
/FORMULA_EXTRACTION_PLAN.md             ← Formula extraction roadmap
/FORMULA_EXTRACTION_SUMMARY_REPORT.md   ← Formula work summary
/VALUATION_FORMULAS_COMPLETE_REPORT.md  ← Valuation formulas guide
```

### Processor Documentation:

```
/PROCESSORS/fundamental/calculators/README.md  ← Calculator usage
/PROCESSORS/valuation/formulas/README.md       ← Formula usage (TODO)
/docs/TRANSFORMERS_LAYER_GUIDE.md              ← Transformers explained
```

---

## 🎯 10. QUICK REFERENCE

### Tôi muốn...

**→ Cập nhật báo cáo tài chính mới:**
```bash
PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard \
python3 PROCESSORS/fundamental/calculators/company_calculator.py
```

**→ Cập nhật PE/PB hàng ngày:**
```bash
python3 PROCESSORS/valuation/pipelines/daily_full_valuation_pipeline.py
```

**→ Test formulas:**
```bash
python3 PROCESSORS/fundamental/formulas/_base_formulas.py
python3 PROCESSORS/valuation/formulas/valuation_formulas.py
```

**→ So sánh output cũ vs mới:**
```bash
python3 compare_parquet_detailed.py
```

**→ Kiểm tra metric codes:**
```bash
python3 PROCESSORS/valuation/formulas/metric_mapper.py
```

---

## 📊 11. DATA FLOW DIAGRAM

```
┌─────────────────┐
│  Raw Data       │
│  (refined/)     │  ← Input from BSC/VNStock
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CALCULATORS    │
│  Load → Apply   │  ← PROCESSORS/fundamental/calculators/
│  Formulas →     │
│  Save           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Processed Data │
│  (processed/)   │  ← Output: company/bank metrics
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  WEBAPP         │
│  Dashboard      │  ← Streamlit UI displays data
└─────────────────┘
```

---

## ✅ SUMMARY

### Key Principles:

1. **Data Separation:**
   - `refined/` = Raw input (CŨ)
   - `processed/` = Calculated output (MỚI)

2. **Code Separation:**
   - `calculators/` = Orchestration
   - `formulas/` = Pure calculations

3. **Entity-Specific:**
   - Use `metric_mapper` for correct codes
   - Each entity has different metric codes

4. **Formula-Based:**
   - Formulas are pure functions
   - Testable, reusable, maintainable

5. **Workflow:**
   - Quarterly: Run fundamental calculators
   - Daily: Run valuation/technical pipelines
   - Test: Compare outputs before commit

---

**Generated by:** Claude Code
**Date:** 2025-12-08
**Version:** 1.0
**Status:** ✅ Production Standard
