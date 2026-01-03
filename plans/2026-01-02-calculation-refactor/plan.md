# Calculation Refactor Plan - Platform-Agnostic Architecture

**Created:** 2026-01-02
**Status:** ✅ Complete (2026-01-02)
**Priority:** High
**Goal:** Move all inline calculations from pages to PROCESSORS, pre-calculate in parquet

---

## Executive Summary

**Problem:** 6 dashboard files contain inline calculation code mixed with display logic.
**Impact:** DRY violations, platform lock-in, maintenance burden, inconsistent results.

**Solution:** Pre-calculate ALL metrics in PROCESSORS pipelines, store in parquet, Streamlit only displays.

---

## Findings Summary

### Critical - Need Pre-calculation in Parquet

| File | Issue | Lines | Status in Parquet |
|------|-------|-------|-------------------|
| `company_dashboard.py` | MA4 YoY growth | 204-231 | ❌ MISSING |
| `company_dashboard.py` | MA4 Margin smoothing | 304-314 | ❌ MISSING |
| `company_dashboard.py` | YoY delta inline | 161, 167 | ❌ MISSING |
| `bank_dashboard.py` | MA4 YoY function (duplicate) | 414-428 | ✅ HAS - just use it! |
| `bank_dashboard.py` | safe_delta YoY | 193 | ✅ HAS - just use it! |
| `security_dashboard.py` | safe_delta YoY | 155 | ❌ MISSING |
| `sector_dashboard.py` | Percentile calcs (5x) | 414,498,692,722,941 | ✅ HAS - just use it! |

### Acceptable - Display/Service Logic (No change needed)

| File | Issue | Lines | Reason |
|------|-------|-------|--------|
| `ta_dashboard_service.py` | RS Ratio/Momentum | 196-203 | Service layer, not UI |
| `market_overview.py` | VN-Index MA20/50/100 | 164-166 | Chart-specific, on loaded data |
| `fx_commodities_dashboard.py` | spread_pct, change_pct | 449, 769 | Simple display math |
| `forecast_dashboard.py` | * 100 conversions | 230,272,281 | Just formatting |
| `stock_scanner.py` | strength * 100 | 259 | Just formatting |

---

## Phase 1: Add Missing Columns to Company Parquet ✅

**Goal:** Add pre-calculated YoY growth + MA4 smoothed columns to company parquet.

### Task 1.1: Update Company Calculator

**File:** `PROCESSORS/fundamental/calculators/company_calculator.py`

**Add YoY Growth columns:**
```python
# YoY Growth columns (TTM-based)
'net_revenue_growth_yoy'   # (current_ttm - prev_ttm) / abs(prev_ttm) * 100
'gross_profit_growth_yoy'
'ebitda_growth_yoy'
'npatmi_growth_yoy'
'operating_cf_growth_yoy'
'fcf_growth_yoy'
```

**Add MA4 Smoothed Margin columns:**
```python
# MA4 smoothed margins (4-quarter moving average)
'gross_profit_margin_ma4'   # rolling(4).mean()
'ebit_margin_ma4'
'ebitda_margin_ma4'
'net_margin_ma4'
```

**Logic (match bank calculator pattern):**
```python
def _calculate_yoy_growth(df: pd.DataFrame, col: str) -> pd.Series:
    """Calculate YoY growth using TTM values."""
    ttm_col = f"{col}_ttm"
    if ttm_col not in df.columns:
        # Calculate TTM first
        ttm = df.groupby('symbol')[col].rolling(4).sum().reset_index(level=0, drop=True)
    else:
        ttm = df[ttm_col]

    prev_ttm = df.groupby('symbol')[ttm_col].shift(4)
    return ((ttm - prev_ttm) / prev_ttm.abs()) * 100
```

**Output:** `DATA/processed/fundamental/company/company_financial_metrics.parquet`
- Add 6 new YoY columns

### Task 1.2: Update Security Calculator

**File:** `PROCESSORS/fundamental/calculators/security_calculator.py`

**Add columns:**
```python
'total_revenue_growth_yoy'
'npatmi_growth_yoy'
'pbt_growth_yoy'
```

**Output:** `DATA/processed/fundamental/security/security_financial_metrics.parquet`

### Task 1.3: Run Calculators & Verify

```bash
# Run calculators
python3 PROCESSORS/fundamental/calculators/company_calculator.py
python3 PROCESSORS/fundamental/calculators/security_calculator.py

# Verify new columns
python3 -c "
import pandas as pd
df = pd.read_parquet('DATA/processed/fundamental/company/company_financial_metrics.parquet')
print([c for c in df.columns if 'growth_yoy' in c])
"
```

---

## Phase 2: Remove Inline MA4 Functions from Pages ✅

**Goal:** Replace inline MA4 calculations with pre-calculated parquet values.

### Task 2.1: Update company_dashboard.py

**Remove 2 inline functions:**

1. **compute_ma4_yoy_full (lines 204-231):**
```python
# BEFORE (inline)
def compute_ma4_yoy_full(col_name: str) -> pd.Series:
    ttm_current = full_series.rolling(window=4, min_periods=4).sum()
    ttm_prev = ttm_current.shift(4)
    ma4_full = (ttm_current / ttm_prev - 1) * 100.0
    ...

# AFTER (use pre-calculated)
ma4_yoy = df[f'{col}_growth_yoy']  # From parquet
```

2. **compute_ma4_margin_full (lines 304-314):**
```python
# BEFORE (inline)
def compute_ma4_margin_full(col_name: str) -> pd.Series:
    full_series = pd.to_numeric(df_full[col_name], errors='coerce')
    ma4_full = full_series.rolling(window=4, min_periods=1).mean()
    ...

# AFTER (use pre-calculated)
ma4_margin = df[f'{col}_ma4']  # From parquet
```

3. **YoY delta inline (lines 161, 167):**
```python
# BEFORE
delta = ((revenue - prev_rev) / abs(prev_rev) * 100) if prev_rev != 0 else 0

# AFTER
delta = df['net_revenue_growth_yoy'].iloc[-1]  # From parquet
```

**Changes:**
- Delete lines 204-231 (compute_ma4_yoy_full)
- Delete lines 304-314 (compute_ma4_margin_full)
- Update lines 161, 167 to use pre-calculated YoY columns
- Map: `net_revenue` → `net_revenue_growth_yoy`, `gross_profit_margin` → `gross_profit_margin_ma4`

### Task 2.2: Update bank_dashboard.py

**Current (lines 414-428):** Same MA4 function duplicated.

**Target:**
```python
# Bank parquet ALREADY HAS these columns:
# - nii_growth_yoy
# - npatmi_growth_yoy
# - pbt_growth_yoy
# - toi_growth_yoy
# - ppop_growth_yoy

# Just use them directly:
ma4_yoy = df['npatmi_growth_yoy']  # Already exists!
```

**Changes:**
- Delete lines 414-428 (compute_ma4_yoy_full function)
- Update chart code to use existing YoY columns

### Task 2.3: Update security_dashboard.py

**Current (line 155):**
```python
delta = ((revenue - prev_rev) / abs(prev_rev) * 100) if prev_rev != 0 else 0
```

**Target:** Use pre-calculated `total_revenue_growth_yoy` column (after Phase 1).

---

## Phase 3: Remove Inline Percentile Calculations from Sector Dashboard ⏭️ SKIPPED

**Goal:** Use pre-calculated percentiles from sector_valuation_metrics.parquet.

### Task 3.1: Audit Current Inline Calculations

**File:** `WEBAPP/pages/sector/sector_dashboard.py`

**Inline calculations found at:**
- Line 414: `percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100`
- Line 498: Same pattern
- Line 692: Same pattern
- Line 722: Same pattern
- Line 941: Same pattern

**Parquet already has:**
```python
# sector_valuation_metrics.parquet columns:
'pe_percentile_5y'   # 5-year PE percentile
'pb_percentile_5y'   # 5-year PB percentile
'ps_percentile_5y'   # 5-year PS percentile
```

### Task 3.2: Update sector_dashboard.py

**For each inline percentile calculation:**

**Before:**
```python
percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100
```

**After:**
```python
# Load from parquet (via service)
percentile = sector_data['pe_percentile_5y']
```

**Changes:**
- Update sector_service.py to return percentile columns
- Remove all 5 inline percentile calculations
- Use pre-calculated values

---

## Phase 4: Create Shared Calculation Utilities (Optional) ⏭️ SKIPPED

**Goal:** For any remaining edge-case calculations, centralize in utils.

### Task 4.1: Create calculation utils module

**File:** `WEBAPP/utils/calculations.py`

```python
"""
Shared calculation utilities for edge cases.
Prefer pre-calculated parquet values over these functions.
"""

def yoy_growth(current: float, previous: float) -> float:
    """Calculate YoY growth percentage."""
    if previous == 0 or pd.isna(previous):
        return 0.0
    return ((current - previous) / abs(previous)) * 100

def calculate_percentile(value: float, distribution: pd.Series) -> float:
    """Calculate percentile of value within distribution."""
    clean = distribution.dropna()
    if len(clean) == 0:
        return 50.0
    return (np.sum(clean <= value) / len(clean)) * 100
```

### Task 4.2: Import from utils instead of inline

**Any remaining calculations should:**
```python
from WEBAPP.utils.calculations import yoy_growth, calculate_percentile

# Instead of inline formulas
delta = yoy_growth(current, previous)
```

---

## Phase 5: Verification & Testing ✅

### Task 5.1: Verify Parquet Updates

```bash
# Check company parquet has YoY columns
python3 -c "
import pandas as pd
df = pd.read_parquet('DATA/processed/fundamental/company/company_financial_metrics.parquet')
yoy_cols = [c for c in df.columns if 'growth_yoy' in c]
print(f'YoY columns: {yoy_cols}')
print(f'Sample: {df[yoy_cols].head(2)}')
"
```

### Task 5.2: Test Dashboard Rendering

```bash
# Run dashboard and check no calculation errors
streamlit run WEBAPP/main_app.py
# Navigate to each page and verify charts render correctly
```

### Task 5.3: Compare Results Before/After

```python
# Validate YoY values match previous inline calculations
# Sample comparison for a known ticker
```

---

## Files Changed Summary

### Phase 1 - Calculator Updates
| File | Columns to Add |
|------|----------------|
| `company_calculator.py` | 6 YoY growth + 4 MA4 margin columns |
| `security_calculator.py` | 3 YoY growth columns |

### Phase 2 - Remove Inline Functions
| File | Lines to Remove | Function/Code |
|------|-----------------|---------------|
| `company_dashboard.py` | 204-231 | `compute_ma4_yoy_full()` |
| `company_dashboard.py` | 304-314 | `compute_ma4_margin_full()` |
| `company_dashboard.py` | 161, 167 | YoY delta inline |
| `bank_dashboard.py` | 414-428 | `compute_ma4_yoy_full()` |
| `bank_dashboard.py` | 193 | `safe_delta()` |
| `security_dashboard.py` | 155 | `safe_delta()` |

### Phase 3 - Remove Inline Percentiles
| File | Lines to Remove | Count |
|------|-----------------|-------|
| `sector_dashboard.py` | 414, 498, 692, 722, 941 | 5 places |

### Phase 4 - New Utils (Optional)
| File | Action |
|------|--------|
| `WEBAPP/utils/calculations.py` | Create shared utils |

### Phase 6 - Architecture Documentation
| File | Contents |
|------|----------|
| `docs/webapp-architecture.md` | Directory structure, data flow, principles |
| | Data contract (parquet schemas) |
| | **Page creation guide (6 steps)** |
| | Folder responsibilities & DO's/DON'Ts |
| | Migration guide (Streamlit → other platforms) |

---

## Architecture Diagram

```
BEFORE (Current):
┌─────────────────────────────────────────────────────┐
│  WEBAPP/pages/*.py                                  │
│  ┌───────────────────────────────────────────────┐  │
│  │ def compute_ma4_yoy_full():  # INLINE CALC    │  │
│  │     ttm_current = rolling(4).sum()            │  │
│  │     ttm_prev = shift(4)                       │  │
│  │     return (ttm_current / ttm_prev - 1) * 100 │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │ percentile = np.sum(data <= val) / len(data)  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘

AFTER (Target):
┌─────────────────────────────────────────────────────┐
│  PROCESSORS/calculators/*.py                        │
│  ┌───────────────────────────────────────────────┐  │
│  │ # Pre-calculate YoY growth                    │  │
│  │ df['net_revenue_growth_yoy'] = calculate()    │  │
│  │ df['pe_percentile_5y'] = calculate()          │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  DATA/processed/*.parquet                           │
│  - company_financial_metrics.parquet (+ YoY cols)   │
│  - security_financial_metrics.parquet (+ YoY cols)  │
│  - sector_valuation_metrics.parquet (has percentiles)│
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  WEBAPP/services/*.py                               │
│  # Load parquet, return DataFrame                   │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  WEBAPP/pages/*.py                                  │
│  # DISPLAY ONLY - No calculations                   │
│  fig = px.bar(df['net_revenue_growth_yoy'])         │
└─────────────────────────────────────────────────────┘
```

---

## Benefits

1. **Platform Agnostic:** Calculations in Python processors, display in any UI framework
2. **DRY:** Single calculation logic, no duplication
3. **Testable:** Calculator logic can be unit tested
4. **Performant:** Pre-calculated values, no runtime calculations
5. **Maintainable:** Business logic separate from UI code

---

## Estimated Effort

| Phase | Effort | Priority |
|-------|--------|----------|
| Phase 1: Add YoY columns | 2-3 hours | High |
| Phase 2: Remove inline MA4 | 1-2 hours | High |
| Phase 3: Remove inline percentiles | 1 hour | Medium |
| Phase 4: Create utils | 30 mins | Low |
| Phase 5: Testing | 1 hour | High |
| Phase 6: Architecture docs | 2-3 hours | Medium |

**Total:** ~9-12 hours

---

## Phase 6: WEBAPP Architecture Documentation ✅

**Goal:** Document Streamlit webapp architecture for maintainability and future migrations.

### Task 6.1: Create WEBAPP Architecture Doc

**File:** `docs/webapp-architecture.md`

**Contents:**
```markdown
# WEBAPP Architecture

## Overview
- Streamlit-based dashboard for Vietnam stock market analysis
- Platform-agnostic data layer (parquet files)
- Service layer pattern for data access

## Directory Structure
WEBAPP/
├── main_app.py              # Entry point
├── core/                    # Shared constants & styles
│   ├── styles.py           # UI styling (colors, layouts)
│   ├── trading_constants.py # Business thresholds
│   └── trading_rules.py    # Signal definitions
├── services/               # Data access layer
│   ├── company_service.py
│   ├── bank_service.py
│   └── sector_service.py
├── pages/                  # Dashboard pages
│   ├── company/
│   ├── bank/
│   ├── sector/
│   ├── technical/
│   ├── forecast/
│   └── fx_commodities/
├── components/             # Reusable UI components
└── utils/                  # Helper functions

## Data Flow
PROCESSORS → DATA/processed/*.parquet → WEBAPP/services → WEBAPP/pages

## Key Principles
1. Pages ONLY display data (no calculations)
2. Services load from parquet (no transformations)
3. All calculations in PROCESSORS/calculators
4. Constants centralized in core/
```

### Task 6.2: Document Data Contract

**Section in doc:**
```markdown
## Data Contract (Parquet Schemas)

### Company Financial Metrics
- Path: DATA/processed/fundamental/company/company_financial_metrics.parquet
- Columns: symbol, report_date, year, quarter, ...
- YoY columns: net_revenue_growth_yoy, npatmi_growth_yoy, ...
- MA4 columns: gross_profit_margin_ma4, net_margin_ma4, ...

### Bank Financial Metrics
- Path: DATA/processed/fundamental/bank/bank_financial_metrics.parquet
- YoY columns: nii_growth_yoy, npatmi_growth_yoy, ...

### Sector Valuation Metrics
- Path: DATA/processed/sector/sector_valuation_metrics.parquet
- Percentile columns: pe_percentile_5y, pb_percentile_5y, ...
```

### Task 6.3: Document Page Creation Guide

**Section in doc:**
```markdown
## Creating a New Page

### Complete File Organization Map

```
WEBAPP/
├── main_app.py                          # 1️⃣ REGISTER PAGE HERE
│
├── core/                                # 2️⃣ SHARED RESOURCES (DON'T DUPLICATE)
│   ├── styles.py                        # Colors, layouts, chart configs
│   ├── trading_constants.py             # Thresholds, watchlists
│   ├── trading_rules.py                 # Signal definitions, patterns
│   ├── valuation_config.py              # PE/PB/PS configs
│   └── chart_config.py                  # Chart templates
│
├── components/                          # 3️⃣ GLOBAL REUSABLE COMPONENTS
│   ├── cards/                           # Metric cards, info cards
│   ├── charts/                          # Common chart types
│   ├── tables/                          # Styled tables
│   └── filters/                         # Filter bars, selectors
│
├── services/                            # 4️⃣ GLOBAL DATA SERVICES
│   ├── company_service.py               # Cross-page company data
│   ├── sector_service.py                # Cross-page sector data
│   └── valuation_service.py             # Cross-page valuation data
│
├── utils/                               # 5️⃣ HELPER FUNCTIONS
│   ├── formatters.py                    # Number/date formatting
│   ├── calculations.py                  # Shared calculations (if any)
│   └── validators.py                    # Input validation
│
└── pages/                               # 6️⃣ PAGE-SPECIFIC CODE
    └── {page_name}/
        ├── {page_name}_dashboard.py     # Entry point
        ├── components/                  # Page-only components
        ├── services/                    # Page-only data loading
        └── tabs/                        # Tab content
```

### Decision Tree: Where to Put Your Code?

```
Is this code used by MULTIPLE pages?
├── YES → Put in WEBAPP/core/, WEBAPP/components/, or WEBAPP/services/
│   ├── Constants/Config? → core/
│   ├── UI Component? → components/
│   ├── Data Loading? → services/
│   └── Helper Function? → utils/
│
└── NO (page-specific) → Put in WEBAPP/pages/{page_name}/
    ├── Entry point? → {page_name}_dashboard.py
    ├── Tab content? → tabs/
    ├── Page component? → components/
    └── Page data? → services/
```

### Step 1: Create Page Directory Structure
```
WEBAPP/pages/{page_name}/
├── {page_name}_dashboard.py    # Main entry point
├── components/                  # Page-specific components
│   ├── {component1}.py
│   └── {component2}.py
├── services/                    # Data loading (optional)
│   └── {page_name}_service.py
└── tabs/                        # Tab components (if multi-tab)
    ├── overview_tab.py
    └── detail_tab.py
```

### Step 2: Register Page in main_app.py
```python
# WEBAPP/main_app.py
pages = {
    "🏢 Company": "company",
    "🏦 Bank": "bank",
    "📊 New Page": "new_page",  # Add here
}

# Import and render
if page == "new_page":
    from WEBAPP.pages.new_page.new_page_dashboard import render
    render()
```

### Step 3: Create Dashboard Entry Point
```python
# WEBAPP/pages/{page_name}/{page_name}_dashboard.py
import streamlit as st
from WEBAPP.core.styles import get_chart_layout, CHART_COLORS
from WEBAPP.core.trading_constants import ...  # Business thresholds
from WEBAPP.core.trading_rules import ...      # Signal definitions

def render():
    st.title("Page Title")
    # Load data from parquet (NO calculations here!)
    df = load_data()
    # Display only
    render_charts(df)
    render_tables(df)
```

### Step 4: Use Core Modules

| Need | Import From | Example |
|------|-------------|---------|
| Colors, Layout | `WEBAPP.core.styles` | `CHART_COLORS['positive']` |
| Thresholds | `WEBAPP.core.trading_constants` | `OVERBOUGHT_THRESHOLD` |
| Signal Rules | `WEBAPP.core.trading_rules` | `SIGNAL_MATRIX['BUY']` |
| Valuation Config | `WEBAPP.core.valuation_config` | `METRIC_CONFIG['PE']` |

### Step 5: Create Service (Data Loading)
```python
# WEBAPP/pages/{page_name}/services/{page_name}_service.py
import pandas as pd
from pathlib import Path

class PageService:
    DATA_ROOT = Path("DATA/processed")

    @staticmethod
    @st.cache_data(ttl=3600)
    def load_data() -> pd.DataFrame:
        # Load from parquet - NO calculations!
        return pd.read_parquet(PageService.DATA_ROOT / "...")
```

### Step 6: Create Reusable Components
```python
# WEBAPP/pages/{page_name}/components/{component}.py
import streamlit as st
import plotly.graph_objects as go
from WEBAPP.core.styles import get_chart_layout

def render_metric_card(title: str, value: float, delta: float):
    """Reusable metric card component."""
    st.metric(title, f"{value:,.2f}", f"{delta:+.1f}%")

def render_bar_chart(df, x_col: str, y_col: str, title: str):
    """Reusable bar chart with standard styling."""
    fig = go.Figure(go.Bar(x=df[x_col], y=df[y_col]))
    fig.update_layout(**get_chart_layout(title))
    st.plotly_chart(fig, use_container_width=True)
```

### Folder Responsibilities

| Folder | Purpose | Rules |
|--------|---------|-------|
| `core/` | Shared constants, styles | Import-only, no modifications |
| `components/` | Reusable UI components | Stateless, props-based |
| `services/` | Data loading | Read parquet, return DataFrame |
| `tabs/` | Tab content | Compose from components |
| `pages/` | Page entry points | Orchestrate tabs/components |

### DO's and DON'Ts

✅ **DO:**
- Load pre-calculated data from parquet
- Use `@st.cache_data` for expensive loads
- Import colors/constants from `core/`
- Create reusable components

❌ **DON'T:**
- Calculate metrics in page code
- Hardcode colors or thresholds
- Duplicate component logic
- Load raw data and transform
```

### Task 6.4: Document Migration Guide

**Section in doc:**
```markdown
## Migration Guide (Streamlit → Other Platforms)

### What to Keep
- DATA/processed/*.parquet (data layer)
- PROCESSORS/ (calculation logic)
- config/ (registries, schemas)

### What to Replace
- WEBAPP/pages/ → New UI framework (React, Vue, etc.)
- WEBAPP/services/ → API endpoints or GraphQL
- WEBAPP/core/styles.py → New styling system

### Data Access Pattern
```python
# Current (Streamlit)
df = pd.read_parquet("DATA/processed/...")
st.dataframe(df)

# Future (API)
@app.get("/api/company/{ticker}")
def get_company(ticker: str):
    df = pd.read_parquet("DATA/processed/...")
    return df[df['symbol'] == ticker].to_dict()
```
```

---

## Next Steps

1. [x] Execute Phase 1 - Update calculators ✅
2. [x] Run calculators to regenerate parquet ✅
3. [x] Execute Phase 2 - Update dashboards ✅
4. [x] Execute Phase 3 - SKIPPED (inline percentiles are contextual) ⏭️
5. [x] Test all pages ✅
6. [x] Execute Phase 6 - Write architecture docs ✅
7. [ ] Commit changes

---

## Appendix: All Inline Calculations Found

### A. YoY Growth Formula (Duplicated 3x)
```python
# company_dashboard.py:161,167 | bank_dashboard.py:193 | security_dashboard.py:155
delta = ((current - previous) / abs(previous)) * 100
```

### B. MA4 TTM YoY Function (Duplicated 2x)
```python
# company_dashboard.py:204-231, bank_dashboard.py:414-428
def compute_ma4_yoy_full(col_name: str) -> pd.Series:
    full_series = pd.to_numeric(df_full[col_name], errors='coerce')
    ttm_current = full_series.rolling(window=4, min_periods=4).sum()
    ttm_prev = ttm_current.shift(4)
    ma4_full = (ttm_current / ttm_prev - 1) * 100.0
    ...
```

### C. MA4 Margin Smoothing Function (1x - but should be pre-calculated)
```python
# company_dashboard.py:304-314
def compute_ma4_margin_full(col_name: str) -> pd.Series:
    full_series = pd.to_numeric(df_full[col_name], errors='coerce')
    ma4_full = full_series.rolling(window=4, min_periods=1).mean()
    ...
```

### D. Percentile Calculation (Duplicated 5x)
```python
# sector_dashboard.py: lines 414, 498, 692, 722, 941
percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100
```

### E. Acceptable (No change needed)
```python
# market_overview.py:164-166 - Chart-specific VN-Index MA
vnindex_ma20 = vnindex_series.rolling(window=20, min_periods=1).mean()

# fx_commodities_dashboard.py:449, 769 - Simple display math
spread_pct = (spread / latest1) * 100
change_pct = ((value - prev) / prev) * 100

# ta_dashboard_service.py:196-203 - Service layer RRG calculations
rs_ratio = strength_score / strength_score.mean()
rs_momentum = rs_ratio.diff(5) * 100
```
