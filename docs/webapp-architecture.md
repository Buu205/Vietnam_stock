# WEBAPP Architecture

**Platform-agnostic Streamlit dashboard for Vietnam stock market analysis.**

---

## Overview

| Aspect | Description |
|--------|-------------|
| **Framework** | Streamlit |
| **Data Layer** | Parquet files (platform-agnostic) |
| **Pattern** | Service Layer (load from parquet, no transforms) |
| **Principle** | Pages display only, calculations in PROCESSORS |

---

## Directory Structure

```
WEBAPP/
├── main_app.py                      # Entry point, page routing
│
├── core/                            # Shared constants & styles
│   ├── styles.py                    # UI colors, chart layouts
│   ├── constants.py                 # Business constants
│   ├── trading_constants.py         # Thresholds, watchlists
│   ├── trading_rules.py             # Signal matrix, patterns
│   ├── valuation_config.py          # PE/PB/PS configs
│   └── chart_config.py              # Chart templates
│
├── services/                        # Global data services
│   ├── company_service.py           # Cross-page company data
│   ├── sector_service.py            # Cross-page sector data
│   └── valuation_service.py         # Cross-page valuation data
│
├── components/                      # Global reusable components
│   ├── cards/                       # Metric cards, info cards
│   ├── charts/                      # Common chart types
│   ├── tables/                      # Styled tables
│   └── filters/                     # Filter bars, selectors
│
├── utils/                           # Helper functions
│   ├── formatters.py                # Number/date formatting
│   └── validators.py                # Input validation
│
└── pages/                           # Dashboard pages
    ├── company/
    │   ├── company_dashboard.py     # Entry point
    │   ├── components/              # Page-specific components
    │   └── services/                # Page-specific data
    ├── bank/
    ├── sector/
    ├── security/
    ├── technical/
    ├── forecast/
    └── fx_commodities/
```

---

## Data Flow

```
PROCESSORS/calculators/     DATA/processed/*.parquet     WEBAPP/services/     WEBAPP/pages/
       │                            │                          │                    │
       │ Pre-calculate              │                          │                    │
       │ YoY, MA4, TTM              │                          │                    │
       ├───────────────────────────>│                          │                    │
       │                            │                          │                    │
       │                            │ pd.read_parquet()        │                    │
       │                            ├─────────────────────────>│                    │
       │                            │                          │                    │
       │                            │                          │ Return DataFrame   │
       │                            │                          ├───────────────────>│
       │                            │                          │                    │
       │                            │                          │                    │ Display
       │                            │                          │                    │ (no calc)
```

**Key Points:**
- All calculations happen in `PROCESSORS/`
- Results stored in `DATA/processed/*.parquet`
- Services load parquet, return DataFrame (no transforms)
- Pages display data (no calculations)

---

## Key Principles

### 1. Pages ONLY Display Data

```python
# ✅ CORRECT - Use pre-calculated column
yoy_col = YOY_COLUMN_MAP.get(col)
ma4_yoy = df[yoy_col]  # From parquet

# ❌ WRONG - Calculate inline
ttm_current = df[col].rolling(4).sum()
ttm_prev = ttm_current.shift(4)
ma4_yoy = (ttm_current / ttm_prev - 1) * 100
```

### 2. Services Load from Parquet (No Transforms)

```python
# ✅ CORRECT
@st.cache_data(ttl=3600)
def load_company_data(ticker: str) -> pd.DataFrame:
    df = pd.read_parquet("DATA/processed/fundamental/company/...")
    return df[df['symbol'] == ticker]

# ❌ WRONG
def load_company_data(ticker: str) -> pd.DataFrame:
    df = pd.read_parquet(...)
    df['roe'] = df['net_income'] / df['equity']  # NO! Pre-calculate in PROCESSORS
    return df
```

### 3. Constants Centralized in core/

```python
# ✅ CORRECT
from WEBAPP.core.trading_constants import OVERBOUGHT_THRESHOLD
from WEBAPP.core.trading_rules import SIGNAL_MATRIX

# ❌ WRONG
OVERBOUGHT_THRESHOLD = 80  # Hardcoded in page
```

### 4. Use @st.cache_data for Performance

```python
@st.cache_data(ttl=3600)  # Cache 1 hour
def load_metrics() -> pd.DataFrame:
    return pd.read_parquet(...)

@st.cache_resource  # Cache singleton objects
def get_registry():
    return MetricRegistry()
```

---

## Data Contract (Parquet Schemas)

### Company Financial Metrics

**Path:** `DATA/processed/fundamental/company/company_financial_metrics.parquet`

| Column Group | Columns |
|--------------|---------|
| ID | `symbol`, `report_date`, `year`, `quarter` |
| TTM | `net_revenue_ttm`, `npatmi_ttm`, `ebitda_ttm`, `fcf_ttm` |
| YoY Growth | `net_revenue_growth_yoy`, `npatmi_growth_yoy`, `ebitda_growth_yoy`, `fcf_growth_yoy` |
| MA4 Margins | `gross_profit_margin_ma4`, `ebit_margin_ma4`, `net_margin_ma4` |
| Ratios | `roe`, `roa`, `current_ratio`, `debt_to_equity` |

### Bank Financial Metrics

**Path:** `DATA/processed/fundamental/bank/bank_financial_metrics.parquet`

| Column Group | Columns |
|--------------|---------|
| ID | `symbol`, `report_date`, `year`, `quarter` |
| YoY Growth | `nii_growth_yoy`, `toi_growth_yoy`, `npatmi_growth_yoy` |
| Bank Ratios | `nim`, `npl_ratio`, `car`, `casa_ratio`, `cir` |

### Security Financial Metrics

**Path:** `DATA/processed/fundamental/security/security_financial_metrics.parquet`

| Column Group | Columns |
|--------------|---------|
| ID | `symbol`, `report_date`, `year`, `quarter` |
| YoY Growth | `total_revenue_growth_yoy`, `npatmi_growth_yoy`, `pbt_growth_yoy` |
| Ratios | `roe`, `roa`, `cir`, `margin_lending_ratio` |

---

## Creating a New Page

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

### Step 1: Create Page Directory

```
WEBAPP/pages/{page_name}/
├── {page_name}_dashboard.py    # Main entry point
├── components/                 # Page-specific components
├── services/                   # Data loading
└── tabs/                       # Tab components
```

### Step 2: Register in main_app.py

```python
# WEBAPP/main_app.py
pages = {
    "Company": "company",
    "Bank": "bank",
    "New Page": "new_page",  # Add here
}

if page == "new_page":
    from WEBAPP.pages.new_page.new_page_dashboard import render
    render()
```

### Step 3: Create Dashboard Entry Point

```python
# WEBAPP/pages/{page_name}/{page_name}_dashboard.py
import streamlit as st
from WEBAPP.core.styles import CHART_COLORS
from WEBAPP.core.trading_constants import ...

def render():
    st.title("Page Title")

    # Load data from parquet (NO calculations!)
    df = load_data()

    # Display only
    render_charts(df)
    render_tables(df)
```

### Step 4: Create Service (Data Loading)

```python
# WEBAPP/pages/{page_name}/services/{page_name}_service.py
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def load_data(ticker: str) -> pd.DataFrame:
    path = "DATA/processed/..."
    df = pd.read_parquet(path)
    return df[df['symbol'] == ticker]  # Filter only, no transform
```

### Step 5: Create Components

```python
# WEBAPP/pages/{page_name}/components/metric_card.py
import streamlit as st

def render_metric_card(title: str, value: float, delta: float):
    st.metric(title, f"{value:,.2f}", f"{delta:+.1f}%")
```

---

## DO's and DON'Ts

### DO

| Action | Example |
|--------|---------|
| Load pre-calculated data | `df['net_revenue_growth_yoy']` |
| Use `@st.cache_data` | `@st.cache_data(ttl=3600)` |
| Import from `core/` | `from WEBAPP.core.styles import ...` |
| Create reusable components | `def render_metric_card(...)` |
| Use service layer | `CompanyService.load_data(ticker)` |

### DON'T

| Action | Why |
|--------|-----|
| Calculate in pages | Not platform-agnostic |
| Hardcode colors/thresholds | Duplicate, hard to maintain |
| Transform data in services | Services = load only |
| Load raw data | Use processed parquet |
| Skip caching | Performance issue |

---

## Migration Guide (Streamlit → Other Platforms)

### What to Keep (Platform-Agnostic)

```
DATA/processed/*.parquet      # Data layer
PROCESSORS/                   # Calculation logic
config/                       # Registries, schemas
WEBAPP/core/trading_*.py      # Business rules
```

### What to Replace

| Streamlit | New Platform |
|-----------|--------------|
| `WEBAPP/pages/` | React/Vue components |
| `WEBAPP/services/` | REST API endpoints |
| `WEBAPP/core/styles.py` | CSS/Tailwind |
| `st.dataframe()` | Table component |
| `st.plotly_chart()` | Chart library |

### Data Access Pattern

```python
# Current (Streamlit)
df = pd.read_parquet("DATA/processed/...")
st.dataframe(df)

# Future (API)
@app.get("/api/company/{ticker}")
def get_company(ticker: str):
    df = pd.read_parquet("DATA/processed/...")
    return df[df['symbol'] == ticker].to_dict('records')

# Future (Frontend)
const data = await fetch(`/api/company/${ticker}`);
<DataTable data={data} />
```

---

## Column Mapping Reference

### Company Dashboard

```python
YOY_COLUMN_MAP = {
    'net_revenue': 'net_revenue_growth_yoy',
    'gross_profit': 'gross_profit_growth_yoy',
    'ebitda': 'ebitda_growth_yoy',
    'npatmi': 'npatmi_growth_yoy',
    'operating_cf': 'operating_cf_growth_yoy',
    'fcf': 'fcf_growth_yoy',
}

MARGIN_MA4_MAP = {
    'gross_profit_margin': 'gross_profit_margin_ma4',
    'ebit_margin': 'ebit_margin_ma4',
    'ebitda_margin': 'ebitda_margin_ma4',
    'net_margin': 'net_margin_ma4',
}
```

### Bank Dashboard

```python
YOY_COLUMN_MAP = {
    'nii': 'nii_growth_yoy',
    'toi': 'toi_growth_yoy',
    'ppop': 'ppop_growth_yoy',
    'pbt': 'pbt_growth_yoy',
    'npatmi': 'npatmi_growth_yoy',
}
```

---

## Change Log

| Date | Change |
|------|--------|
| 2026-01-02 | Initial architecture doc |
| 2026-01-02 | Added YoY/MA4 pre-calculation pattern |
| 2026-01-02 | Added column mapping reference |
