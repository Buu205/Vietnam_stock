# Design System Specification
# Thiết Kế Hệ Thống Giao Diện Dashboard

> **Created:** 2025-12-15
> **Purpose:** Unified design decisions for Streamlit dashboard redesign
> **Status:** 🔴 PENDING APPROVAL - Requires user decision

---

## ⚠️ CRITICAL DECISIONS REQUIRED

Before implementing the redesign, we need to standardize:

### 1. **Chart Library** (Choose ONE)
### 2. **Data Display Units** (Standardize formatting)
### 3. **Design Aesthetic** (Visual direction)

---

## 📊 DECISION 1: CHART LIBRARY

### Current State:
- **Plotly** (v5.15.0+) - Used in `bank_dashboard.py`
- **PyEcharts** (v2.0.5+) - Used in `company_dashboard_pyecharts.py`
- **streamlit-echarts** - Wrapper for PyEcharts in Streamlit

### Comparison:

| Feature | Plotly | PyEcharts |
|---------|--------|-----------|
| **Interactivity** | ⭐⭐⭐⭐⭐ Excellent (zoom, pan, hover) | ⭐⭐⭐⭐ Good |
| **Streamlit Integration** | ⭐⭐⭐⭐⭐ Native `st.plotly_chart()` | ⭐⭐⭐ Requires `streamlit-echarts` |
| **Chart Types** | 40+ types | 50+ types (more variety) |
| **Performance** | ⭐⭐⭐⭐ Good for <10k points | ⭐⭐⭐⭐⭐ Better for large datasets |
| **Customization** | ⭐⭐⭐⭐⭐ Python-native, easy | ⭐⭐⭐ More config-based |
| **Financial Charts** | ⭐⭐⭐⭐⭐ Waterfall, Candlestick | ⭐⭐⭐⭐ Good support |
| **Documentation** | ⭐⭐⭐⭐⭐ Excellent (English) | ⭐⭐⭐ Mostly Chinese |
| **Maintenance** | ⭐⭐⭐⭐⭐ Active | ⭐⭐⭐⭐ Active |
| **Modern Aesthetics** | ⭐⭐⭐⭐ Clean, professional | ⭐⭐⭐⭐⭐ More design flexibility |

### 🎯 **RECOMMENDATION: Plotly**

**Reasons:**
1. ✅ **Better Streamlit integration** - Native support, no wrapper needed
2. ✅ **Easier customization** - Pure Python, no JS config
3. ✅ **Better documentation** - English docs, larger community
4. ✅ **Financial chart support** - Waterfall, Candlestick, OHLC built-in
5. ✅ **Simpler codebase** - Less dependencies

**Trade-off:**
- ❌ PyEcharts has more chart variety (Gauge, Sankey, etc.)
- ✅ But Plotly has all charts we need for financial dashboards

### ✅ **YOUR DECISION: Option A - Plotly ONLY**

**Confirmed:** Use Plotly as the single chart library across all dashboards.
- Remove all PyEcharts dependencies
- Consistent, professional charts with native Streamlit integration

---

## 💰 DECISION 2: DATA DISPLAY UNITS

### Current State:
From `formatters.py` and `schema_registry.py`:
- Currency: VND (Vietnamese Dong)
- Large numbers: Need standardization

### Unit Options:

#### **Option A: Billions VND (Tỷ đồng)** ⭐ RECOMMENDED

```python
# Examples:
Revenue: 1,234.5B VND  # 1.2345 trillion VND
Profit:    234.8B VND  # 234.8 billion VND
Equity:    500.0B VND  # 500 billion VND
```

**Pros:**
- ✅ Standard in Vietnamese finance
- ✅ Easy to read (1,234.5B vs 1,234,500,000,000)
- ✅ Matches BSC/VCBS reports

**Display Rules:**
- **1B+ VND:** Display as "X,XXX.XB VND" (1 decimal)
- **<1B VND:** Display as "XXX.XM VND" (millions)
- **Ratios:** Display as "X.XX" or "X.XX%" (2 decimals)
- **Percentages:** Display as "XX.XX%" (2 decimals)

#### **Option B: Millions VND (Triệu đồng)**

```python
# Examples:
Revenue: 1,234,500M VND
Profit:    234,800M VND
```

**Pros:**
- ✅ More precision
**Cons:**
- ❌ Harder to read (too many digits)
- ❌ Not standard for large caps

#### **Option C: Auto-scaling**

```python
# Examples:
Revenue: 1.23T VND   # Trillions
Profit:  234.8B VND  # Billions
Cash:    50.5M VND   # Millions
```

**Pros:**
- ✅ Optimal readability per value
**Cons:**
- ❌ Inconsistent units across metrics
- ❌ Harder to compare

### 🎯 **RECOMMENDATION: Option A (Billions VND)**

**Implementation:**

```python
def format_currency(value: float, unit: str = "B") -> str:
    """
    Format currency in billions VND.

    Args:
        value: Value in VND
        unit: "B" (billions), "M" (millions), "T" (trillions)

    Returns:
        Formatted string: "1,234.5B VND"
    """
    if pd.isna(value):
        return "N/A"

    if unit == "B":
        # Convert to billions (1e9)
        value_formatted = value / 1e9
        if value_formatted >= 1000:
            # Switch to trillions
            return f"{value_formatted/1000:,.1f}T VND"
        return f"{value_formatted:,.1f}B VND"

    elif unit == "M":
        # Convert to millions (1e6)
        return f"{value/1e6:,.1f}M VND"

    elif unit == "T":
        # Convert to trillions (1e12)
        return f"{value/1e12:,.2f}T VND"

# Examples:
format_currency(1_234_567_890_000)  # "1,234.6B VND"
format_currency(500_000_000_000)    # "500.0B VND"
format_currency(50_000_000_000)     # "50.0B VND"
```

### ✅ **YOUR DECISION: Option A - Billions VND (Tỷ đồng)**

**Confirmed:** Use Billions VND as the standard unit for all financial metrics.
- Automatic conversion: VND → Billions (divide by 1e9)
- Ratios: 2 decimal places (e.g., 1.25x)
- Percentages: 2 decimal places (e.g., 15.75%)

---

## 🎨 DECISION 3: DESIGN AESTHETIC

### Options:

#### **Option 1: Professional Financial (Bloomberg/Reuters Style)** ⭐ RECOMMENDED

**Visual Identity:**
- Dark theme (#0A0E27 background)
- Professional sans-serif (Inter/Roboto)
- Muted colors with accent highlights
- Dense data layout
- Minimal whitespace

**Colors:**
```python
THEME = {
    'background': '#0A0E27',      # Dark navy
    'surface': '#151B3D',         # Lighter navy
    'text': '#E2E8F0',            # Light gray text
    'accent': '#3B82F6',          # Blue accent
    'positive': '#10B981',        # Green (gains)
    'negative': '#EF4444',        # Red (losses)
    'neutral': '#6B7280',         # Gray
}
```

**Typography:**
- Headers: **Inter Bold** 24-32px
- Body: **Inter Regular** 14-16px
- Numbers: **JetBrains Mono** (monospaced for alignment)

**Best for:** Professional traders, serious investors

---

#### **Option 2: Modern Minimalist (Clean & Light)**

**Visual Identity:**
- White background
- Generous whitespace
- Soft colors (pastel blues/greens)
- Clean typography
- Card-based layout

**Colors:**
```python
THEME = {
    'background': '#FFFFFF',
    'surface': '#F8FAFC',         # Off-white
    'text': '#1E293B',            # Dark gray
    'accent': '#0EA5E9',          # Sky blue
    'positive': '#059669',        # Emerald
    'negative': '#DC2626',        # Rose
}
```

**Typography:**
- Headers: **Poppins SemiBold** 20-28px
- Body: **Inter Regular** 14px

**Best for:** Casual investors, beginners

---

#### **Option 3: Bold Data-Driven (Vibrant & Energetic)**

**Visual Identity:**
- Gradient backgrounds
- Animated metrics
- Vibrant accent colors
- Large numbers
- Eye-catching charts

**Colors:**
```python
THEME = {
    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'accent': '#F59E0B',          # Amber
    'positive': '#00D9FF',        # Cyan
    'negative': '#FF006E',        # Hot pink
}
```

**Best for:** Younger audience, growth stocks

---

### 🎯 **RECOMMENDATION: Option 1 (Professional Financial)**

**Reasons:**
1. ✅ Matches Vietnamese brokerage platforms (SSI, VCBS)
2. ✅ Better for long reading sessions (dark theme)
3. ✅ Professional credibility
4. ✅ Data-dense without overwhelming

### ✅ **YOUR DECISION: Option 1 - Professional Financial (Optimized)**

**Confirmed:** Professional Financial dark theme with custom brand colors.
- Dark theme base (#0A0E27 background)
- **Brand colors integrated:** #295CA9 (blue), #009B87 (teal), #FFC132 (gold)
- Will be optimized using `/frontend-design` plugin for each page
- Professional, data-dense layout for serious investors

---

## 📐 LAYOUT SPECIFICATIONS

### Grid System:
- **Desktop:** 12-column grid
- **Tablet:** 8-column grid
- **Mobile:** 4-column grid

### Spacing Scale (Tailwind-inspired):
```python
SPACING = {
    'xs': '0.25rem',   # 4px
    'sm': '0.5rem',    # 8px
    'md': '1rem',      # 16px
    'lg': '1.5rem',    # 24px
    'xl': '2rem',      # 32px
    '2xl': '3rem',     # 48px
}
```

### Component Sizes:
```python
SIZES = {
    'metric_card_height': '120px',
    'chart_height': '400px',
    'table_max_height': '600px',
    'sidebar_width': '280px',
}
```

---

## 🚀 NEXT STEPS

Once you decide:

1. ✅ **Chart Library** → Remove unused library from `requirements.txt`
2. ✅ **Data Units** → Update `formatters.py` with standardized functions
3. ✅ **Design Aesthetic** → Create `WEBAPP/core/theme.py` with color palette
4. ✅ **Start Redesign** → Begin with Company Dashboard using `/feature-dev` workflow

---

## 📝 APPROVAL

**Your decisions:**
- Chart Library: `_______________`
- Data Units: `_______________`
- Design Aesthetic: `_______________`

**Ready to proceed?** `[ ] Yes  [ ] Need discussion`

---

## 🐛 COMMON ERRORS & FIXES

### Error 1: AttributeError - 'str' object has no attribute 'strftime'

**Problem:**
```python
df.iloc[-1]['report_date'].strftime('%Y-Q%q')
# AttributeError: 'str' object has no attribute 'strftime'
```

**Cause:** `report_date` column is string, not datetime

**Fix:**
```python
# Always convert to datetime when loading data
df['report_date'] = pd.to_datetime(df['report_date'])

# Or handle safely:
latest_date = df.iloc[-1]['report_date']
if period == 'Quarterly':
    quarter = df.iloc[-1].get('quarter', (latest_date.month - 1) // 3 + 1)
    date_str = f"{latest_date.year}-Q{quarter}"
else:
    date_str = str(latest_date.year)
```

**Best Practice:**
- Convert date columns in data loading layer (Service)
- Always check column types before using `.strftime()`
- Use `.get()` with defaults for optional columns

---

**Created by:** Claude Code
**Awaiting:** User approval to begin redesign
**Last Updated:** 2025-12-15 (Added error fixes + comprehensive redesign plan)

---

## 7. WEBAPP REDESIGN IMPLEMENTATION PLAN

### 7.1 Current State Analysis

**Existing Pages (8 total):**
1. [company_dashboard_pyecharts.py](../WEBAPP/pages/company_dashboard_pyecharts.py) - Company fundamental analysis (PyEcharts)
2. [company_dashboard_v2.py](../WEBAPP/pages/company_dashboard_v2.py) - Quick prototype (Plotly) ✅
3. [bank_dashboard.py](../WEBAPP/pages/bank_dashboard.py) - Banking sector analysis (Mixed Plotly/PyEcharts)
4. [securities_dashboard.py](../WEBAPP/pages/securities_dashboard.py) - Securities/brokerage analysis
5. [technical_analysis.py](../WEBAPP/pages/technical_analysis.py) - Technical indicators & alerts (Plotly)
6. [valuation_sector_dashboard.py](../WEBAPP/pages/valuation_sector_dashboard.py) - Sector PE/PB analysis (Plotly)
7. [forecast_dashboard.py](../WEBAPP/pages/forecast_dashboard.py) - BSC forecast data
8. [news_dashboard.py](../WEBAPP/pages/news_dashboard.py) - News & sentiment analysis

**Issues Identified:**
- ❌ **Inconsistent chart libraries**: Mixed Plotly + PyEcharts usage
- ❌ **No unified theme**: Each page has different styling
- ❌ **Duplicate data loading**: No standardized service layer (partial - `FinancialMetricsLoader` exists but not used consistently)
- ❌ **Inconsistent formatting**: Different data units and formats across pages
- ❌ **Legacy paths**: Some files use old path conventions
- ⚠️ **Component duplication**: Multiple `metric_cards.py` files in different locations
  - `WEBAPP/components/data_display/metric_cards.py` (old)
  - `WEBAPP/components/metrics/metric_cards.py` (new) ✅

**Available Data Sources (43 parquet files):**

**Fundamental:**
- `DATA/processed/fundamental/company/company_financial_metrics.parquet`
- `DATA/processed/fundamental/bank/bank_financial_metrics.parquet`
- `DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet`
- `DATA/processed/fundamental/security/security_financial_metrics.parquet`
- `DATA/processed/fundamental/macro/*.parquet` (interest rates, exchange rates, bonds)

**Technical:**
- `DATA/processed/technical/basic_data.parquet` (indicators for all stocks)
- `DATA/processed/technical/vnindex/vnindex_indicators.parquet`
- `DATA/processed/technical/alerts/daily/*.parquet` (5 alert types)
- `DATA/processed/technical/money_flow/*.parquet` (individual + sector)
- `DATA/processed/technical/market_breadth/market_breadth_daily.parquet`
- `DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet`
- `DATA/processed/technical/market_regime/market_regime_history.parquet`

**Valuation:**
- `DATA/processed/valuation/pe/historical/historical_pe.parquet`
- `DATA/processed/valuation/pb/historical/historical_pb.parquet`
- `DATA/processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet`
- `DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet`
- `DATA/processed/market_indices/sector_pe_summary.parquet`

**Sector Analysis:**
- `DATA/processed/sector/sector_fundamental_metrics.parquet`
- `DATA/processed/sector/sector_valuation_metrics.parquet`
- `DATA/processed/sector/sector_combined_scores.parquet`

**Macro/Commodity:**
- `DATA/processed/macro_commodity/macro_commodity_unified.parquet`

---

### 7.2 Redesign Architecture

#### New Directory Structure

```
WEBAPP/
├── pages/                          # Streamlit pages (rebuild all)
│   ├── 1_company_dashboard.py     # Company analysis (NEW)
│   ├── 2_bank_dashboard.py        # Bank analysis (REBUILD)
│   ├── 3_insurance_dashboard.py   # Insurance analysis (NEW)
│   ├── 4_security_dashboard.py    # Securities analysis (REBUILD)
│   ├── 5_technical_dashboard.py   # Technical analysis (REBUILD)
│   ├── 6_valuation_dashboard.py   # Valuation & sector PE/PB (REBUILD)
│   ├── 7_sector_dashboard.py      # Sector FA+TA combined (NEW)
│   ├── 8_macro_dashboard.py       # Macro & commodity (NEW)
│   └── 9_forecast_dashboard.py    # BSC forecast (REBUILD)
│
├── services/                       # Data loading layer (NEW/REBUILD)
│   ├── company_service.py         # ✅ Already created
│   ├── bank_service.py            # Load bank data
│   ├── insurance_service.py       # Load insurance data
│   ├── security_service.py        # Load security data
│   ├── technical_service.py       # Load technical indicators
│   ├── valuation_service.py       # Load valuation data
│   ├── sector_service.py          # Load sector data
│   ├── macro_service.py           # Load macro/commodity data
│   └── alert_service.py           # Load technical alerts
│
├── components/                     # Reusable UI components (CONSOLIDATE)
│   ├── metrics/
│   │   └── metric_cards.py        # ✅ Already created (keep this)
│   ├── charts/
│   │   ├── fundamental_charts.py  # Income statement, balance sheet, cash flow
│   │   ├── technical_charts.py    # Price, indicators, volume
│   │   ├── valuation_charts.py    # PE/PB bands, sector comparison
│   │   └── sector_charts.py       # Sector rankings, heatmaps
│   ├── tables/
│   │   ├── financial_tables.py    # Financial statement tables
│   │   ├── screening_tables.py    # Stock screening tables
│   │   └── alert_tables.py        # Alert history tables
│   └── filters/
│       ├── ticker_selector.py     # Company/ticker selection
│       ├── date_range.py          # Date range picker
│       └── sector_filter.py       # Sector/industry filter
│
├── core/                           # Core utilities
│   ├── theme.py                   # ✅ Already created
│   ├── formatters.py              # Data formatting utilities (exists, needs update)
│   └── config.py                  # App configuration
│
└── main_app.py                     # Main entry point (check if exists)
```

**Actions Required:**
1. ❌ Remove duplicate: `WEBAPP/components/data_display/metric_cards.py`
2. ✅ Keep: `WEBAPP/components/metrics/metric_cards.py`
3. 🆕 Create 8 new service files
4. 🆕 Create 4 chart component modules
5. 🆕 Create 3 table component modules
6. 🆕 Create 3 filter component modules

---

### 7.3 Implementation Phases

#### Phase 1: Foundation (Week 1) ⭐ HIGH PRIORITY

**Goal:** Standardize infrastructure and create reusable components

**Tasks:**

**1.1 Standardize Chart Library**
   - ✅ **Decision:** Use **Plotly** for all charts (RECOMMENDED)
   - ❌ Remove PyEcharts dependencies from all pages
   - 🆕 Create Plotly templates with brand colors in `theme.py`

   ```python
   # Add to theme.py
   def get_plotly_config():
       """Standard Plotly config for all charts."""
       return {
           'displayModeBar': True,
           'staticPlot': False,
           'responsive': True,
           'toImageButtonOptions': {
               'format': 'png',
               'filename': 'chart',
               'height': 600,
               'width': 1000
           }
       }

   def get_plotly_layout(title: str, yaxis_title: str):
       """Standard layout with brand colors."""
       return {
           'title': {
               'text': title,
               'font': {'size': 18, 'family': 'Inter', 'color': BRAND['primary']}
           },
           'xaxis_title': 'Period',
           'yaxis_title': yaxis_title,
           'font': {'family': 'Inter', 'size': 12},
           'plot_bgcolor': 'rgba(0,0,0,0)',
           'paper_bgcolor': 'rgba(0,0,0,0)',
           'hovermode': 'x unified'
       }
   ```

**1.2 Create Service Layer** (9 services)

Pattern for all services:
```python
# Example: bank_service.py
from pathlib import Path
from typing import Optional, List, Dict
import pandas as pd

class BankService:
    """Service layer for Bank financial data."""

    def __init__(self, data_root: Optional[Path] = None):
        if data_root is None:
            current_file = Path(__file__).resolve()
            project_root = current_file.parents[2]
            data_root = project_root / "DATA"

        self.data_path = data_root / "processed" / "fundamental" / "bank"

        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Bank data path not found: {self.data_path}"
            )

    def get_financial_data(
        self,
        ticker: str,
        period: str = "Quarterly",
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Load financial data for a bank ticker."""
        parquet_file = self.data_path / "bank_financial_metrics.parquet"

        if not parquet_file.exists():
            raise FileNotFoundError(f"Bank metrics file not found: {parquet_file}")

        df = pd.read_parquet(parquet_file)
        df = df[df['symbol'] == ticker].copy()

        if df.empty:
            return pd.DataFrame()

        # Filter by period
        if period == "Quarterly":
            df = df[df['freq_code'] == 'Q']
        elif period == "Yearly":
            df = df[df['freq_code'] == 'Y']

        # Sort and limit
        df = df.sort_values('report_date')

        # Convert dates
        if 'report_date' in df.columns:
            df['report_date'] = pd.to_datetime(df['report_date'])

        if limit:
            df = df.tail(limit)

        return df

    def get_latest_metrics(self, ticker: str) -> Dict:
        """Get latest quarter metrics."""
        df = self.get_financial_data(ticker, "Quarterly", limit=1)
        return df.iloc[-1].to_dict() if not df.empty else {}

    def get_available_tickers(self) -> List[str]:
        """Get list of available bank tickers."""
        parquet_file = self.data_path / "bank_financial_metrics.parquet"

        if not parquet_file.exists():
            return []

        df = pd.read_parquet(parquet_file, columns=['symbol'])
        return sorted(df['symbol'].unique().tolist())
```

**Services to create:**
1. ✅ `company_service.py` (already exists)
2. 🆕 `bank_service.py` (copy pattern from company)
4. 🆕 `security_service.py` (copy pattern from company)
5. 🆕 `technical_service.py` (loads from technical/ dir)
6. 🆕 `valuation_service.py` (loads PE/PB/EV data)
7. 🆕 `sector_service.py` (loads sector analysis data)
8. 🆕 `macro_service.py` (loads macro/commodity data)
9. 🆕 `alert_service.py` (loads technical alerts)

**1.3 Build Chart Components** (4 modules)

**`fundamental_charts.py`:**
```python
def render_income_statement_chart(df: pd.DataFrame, height: int = 450):
    """Income statement multi-line chart (Revenue → Profit)."""
    # Already implemented in income_statement_chart.py
    # Move here and enhance
    pass

def render_balance_sheet_chart(df: pd.DataFrame, height: int = 400):
    """Balance sheet structure (Assets vs Liabilities + Equity)."""
    pass

def render_cash_flow_chart(df: pd.DataFrame, height: int = 400):
    """Cash flow waterfall chart."""
    pass

def render_margins_chart(df: pd.DataFrame, height: int = 400):
    """Profitability margins area chart."""
    # Already implemented
    pass
```

**`technical_charts.py`:**
```python
def render_price_chart_with_indicators(df: pd.DataFrame, indicators: List[str]):
    """Price chart with MA, Bollinger Bands, etc."""
    pass

def render_volume_chart(df: pd.DataFrame):
    """Volume bar chart with color coding."""
    pass

def render_rsi_chart(df: pd.DataFrame):
    """RSI indicator with overbought/oversold zones."""
    pass

def render_macd_chart(df: pd.DataFrame):
    """MACD histogram with signal line."""
    pass
```

**`valuation_charts.py`:**
```python
def render_pe_band_chart(df: pd.DataFrame, ticker: str):
    """PE ratio with historical bands (median, ±1σ, ±2σ)."""
    pass

def render_pb_band_chart(df: pd.DataFrame, ticker: str):
    """PB ratio with historical bands."""
    pass

def render_sector_pe_comparison(df: pd.DataFrame):
    """Sector PE comparison bar chart."""
    pass

def render_valuation_heatmap(df: pd.DataFrame):
    """Sector valuation heatmap (cheap → expensive)."""
    pass
```

**`sector_charts.py`:**
```python
def render_sector_ranking_chart(df: pd.DataFrame, metric: str):
    """Horizontal bar chart of sector rankings."""
    pass

def render_sector_bubble_chart(df: pd.DataFrame):
    """Bubble chart (x=FA score, y=TA score, size=market cap)."""
    pass

def render_sector_rotation_heatmap(df: pd.DataFrame):
    """Sector rotation heatmap (momentum vs strength)."""
    pass
```

**1.4 Consolidate Components**
   - ✅ Keep `WEBAPP/components/metrics/metric_cards.py`
   - ❌ Delete `WEBAPP/components/data_display/metric_cards.py`
   - 🔄 Update all imports to use single location

**Deliverables:**
- ✅ Updated `theme.py` with Plotly templates
- 🆕 9 service classes (1 exists + 8 new)
- 🆕 4 chart component modules
- ✅ Clean component directory (no duplicates)

---

#### Phase 2: Core Dashboards (Week 2-3)

**Goal:** Rebuild main analysis dashboards with new architecture

**2.1 Financial Entity Dashboards (4 pages)**

Priority order:

**1. Company Dashboard** (70% done - extend company_dashboard_v2.py)

   **Current:** 4 KPI cards, income statement, margins, summary table

   **Add:**
   - Balance sheet section (assets, liabilities, equity chart)
   - Cash flow section (waterfall chart)
   - Peer comparison section (compare with sector peers)
   - ROE/ROA trend chart

   **File:** `WEBAPP/pages/1_company_dashboard.py`

**2. Bank Dashboard** (rebuild from scratch)

   **Data:** `bank_service.py` → `bank_financial_metrics.parquet`

   **Sections:**
   1. Key Metrics: NII, NIM, NPL Ratio, CAR
   2. Income Statement: NII, Non-II, Operating Expenses, Net Profit
   3. Asset Quality: NPL ratio trend, Loan Loss Provisions
   4. Efficiency: CIR (Cost-to-Income Ratio), ROA, ROE
   5. Capital: CAR, Tier 1 Capital Ratio
   6. Peer Comparison

   **File:** `WEBAPP/pages/2_bank_dashboard.py`

**3. Insurance Dashboard** (new)

   **Data:** `insurance_service.py` → `insurance_financial_metrics.parquet`

   **Sections:**
   1. Key Metrics: Premium Revenue, Combined Ratio, Claims Ratio
   2. Revenue Breakdown: Direct Premium, Reinsurance Premium
   3. Claims Analysis: Claims paid, Claims ratio trend
   4. Profitability: Underwriting profit, Investment income
   5. Peer Comparison

   **File:** `WEBAPP/pages/3_insurance_dashboard.py`

**4. Security Dashboard** (rebuild)

   **Data:** `security_service.py` → `security_financial_metrics.parquet`

   **Sections:**
   1. Key Metrics: Trading Volume, Commission Income, ROE
   2. Revenue Breakdown: Brokerage, Proprietary Trading, Advisory
   3. Market Share: Trading volume vs market
   4. Profitability: Margins, ROE, ROA
   5. Peer Comparison

   **File:** `WEBAPP/pages/4_security_dashboard.py`

**Common Structure Template:**
```python
import streamlit as st
from WEBAPP.services.{entity}_service import {Entity}Service
from WEBAPP.components.metrics.metric_cards import render_metric_card
from WEBAPP.components.charts.fundamental_charts import (
    render_income_statement_chart,
    render_margins_chart,
    render_balance_sheet_chart
)

st.set_page_config(page_title="{Entity} Analysis", layout="wide", page_icon="🏢")

# Sidebar
ticker = st.sidebar.selectbox("Select {Entity}", service.get_available_tickers())
period = st.sidebar.selectbox("Period", ["Quarterly", "Yearly"])
limit = st.sidebar.slider("Periods", 4, 20, 8)

# Load data
service = {Entity}Service()
df = service.get_financial_data(ticker, period, limit)

# Section 1: Key Metrics
st.subheader("Key Metrics")
latest = df.iloc[-1]
previous = df.iloc[-2] if len(df) > 1 else latest

col1, col2, col3, col4 = st.columns(4)
# ... metric cards

# Section 2: Income Statement
st.subheader("Income Statement Trends")
render_income_statement_chart(df)

# Section 3: Profitability
col1, col2 = st.columns(2)
with col1:
    render_margins_chart(df)
with col2:
    # Entity-specific chart

# ... more sections
```

**2.2 Technical Analysis Dashboard**

**Status:** Rebuild existing page

**Data:** `technical_service.py` → `DATA/processed/technical/`

**Sections:**
1. **Technical Indicators Overview**
   - Price chart with MA (20, 50, 200)
   - Volume with color coding
   - RSI, MACD, Bollinger Bands

2. **Trading Alerts**
   - MA crossover alerts (Golden Cross, Death Cross)
   - Breakout alerts (52-week high/low)
   - Volume spike alerts
   - Pattern alerts (Double Top, Head & Shoulders)

3. **Money Flow Analysis**
   - Individual stock money flow (buying/selling pressure)
   - Sector money flow (1d, 1w, 1m timeframes)
   - Money flow heatmap

4. **Market Breadth**
   - Advance/Decline line
   - New highs/lows
   - % stocks above MA (20, 50, 200)

5. **Market Regime**
   - Trend classification (Uptrend, Downtrend, Sideways)
   - Volatility level (Low, Medium, High)
   - Risk-on/Risk-off indicator

**File:** `WEBAPP/pages/5_technical_dashboard.py`

**2.3 Valuation & Sector Dashboard**

**Status:** Rebuild existing page

**Data:** `valuation_service.py` + `sector_service.py`

**Sections:**
1. **Individual Stock Valuation**
   - PE ratio with historical bands
   - PB ratio with historical bands
   - EV/EBITDA ratio
   - Current vs historical percentile

2. **VN-Index Valuation**
   - Market PE historical chart
   - Market PB historical chart
   - Valuation percentile (cheap/fair/expensive)

3. **Sector PE Comparison**
   - Current sector PE vs historical median
   - Sector PE ranking
   - Overvalued/Undervalued sectors

4. **Sector PB Comparison**
   - Similar to PE

5. **Relative Valuation**
   - Stock PE vs Sector PE
   - Stock PB vs Sector PB
   - Premium/Discount analysis

**File:** `WEBAPP/pages/6_valuation_dashboard.py`

**Deliverables:**
- ✅ 6 rebuilt dashboard pages
- ✅ All using new service layer
- ✅ Consistent design (brand colors from theme.py)
- ✅ Plotly charts only (no PyEcharts)
- ✅ All financial values in Billions VND

---

#### Phase 3: Advanced Features (Week 4)

**Goal:** Add new dashboards and advanced features

**3.1 Sector FA+TA Dashboard** (NEW)

**Data:** `sector_service.py` → `DATA/processed/sector/`

**Features:**
1. **Sector Rankings Dashboard**
   - Combined score table (FA + TA)
   - Sortable by FA score, TA score, or combined
   - Buy/Sell/Hold signals per sector

2. **FA Score Breakdown**
   - ROE, Growth, Margins contribution
   - Heatmap of FA metrics by sector

3. **TA Score Breakdown**
   - Trend, Momentum, Breadth contribution
   - Sector technical strength heatmap

4. **Sector Rotation Analysis**
   - Bubble chart (x=FA, y=TA, size=market cap)
   - Quadrant analysis (Strong Both, Strong FA, Strong TA, Weak Both)

5. **Sector Signals**
   - BUY sectors (high combined score)
   - SELL sectors (low combined score)
   - HOLD sectors (neutral)
   - Historical accuracy backtest

**File:** `WEBAPP/pages/7_sector_dashboard.py`

**3.2 Macro & Commodity Dashboard** (NEW)

**Data:** `macro_service.py` → `DATA/processed/macro_commodity/`

**Features:**
1. **Interest Rates**
   - Deposit interest rates trend
   - Government bond yields (5Y, 10Y)
   - Impact on banking sector

2. **Exchange Rates**
   - VND/USD trend
   - Impact on exporters/importers
   - Sector correlation

3. **Commodity Prices**
   - Gold price (domestic + international)
   - Oil price (Brent, WTI)
   - Impact on transportation, manufacturing sectors

4. **Macro Indicators**
   - CPI (inflation)
   - GDP growth
   - PMI (Purchasing Managers Index)

5. **VN-Index Correlation**
   - Correlation matrix (VN-Index vs macro indicators)
   - Leading indicators

**File:** `WEBAPP/pages/8_macro_dashboard.py`

**3.3 Forecast Dashboard** (REBUILD)

**Data:** BSC forecast parquet (from `forecast_service.py`)

**Features:**
1. **Analyst Forecasts**
   - Revenue forecast (next 4 quarters)
   - EPS forecast
   - Target price consensus

2. **Price Targets**
   - Current price vs target price
   - Upside/downside potential
   - Price target distribution

3. **Consensus Ratings**
   - Buy/Hold/Sell distribution
   - Rating changes over time

4. **Forecast Accuracy**
   - Historical forecast vs actual
   - Analyst track record

**File:** `WEBAPP/pages/9_forecast_dashboard.py`

**Deliverables:**
- ✅ 3 new/rebuilt dashboards
- ✅ Sector FA+TA integration complete
- ✅ Macro data integration
- ✅ Forecast data visualization

---

#### Phase 4: Polish & Optimization (Week 5)

**Goal:** Performance optimization and UX enhancements

**4.1 Performance Optimization**

1. **Caching Strategy**
   ```python
   # Data loading: Cache for 5 minutes
   @st.cache_data(ttl=300, show_spinner=False)
   def load_data(...):
       pass

   # Resource loading: Cache indefinitely
   @st.cache_resource
   def get_service():
       return ServiceClass()
   ```

2. **DuckDB Queries**
   ```python
   # For large datasets, use DuckDB
   import duckdb

   conn = duckdb.connect()
   query = """
       SELECT * FROM read_parquet(?)
       WHERE symbol = ? AND report_date >= ?
   """
   df = conn.execute(query, [file_path, ticker, start_date]).fetchdf()
   ```

3. **Lazy Loading**
   - Load charts only when tab is active
   - Use `st.spinner()` for loading states

**4.2 UX Enhancements**

1. **Data Export**
   ```python
   # Add to each dashboard
   st.download_button(
       label="📥 Download CSV",
       data=df.to_csv(index=False).encode('utf-8'),
       file_name=f"{ticker}_data.csv",
       mime="text/csv"
   )
   ```

2. **Chart Download**
   ```python
   # Built into Plotly config
   config = {
       'toImageButtonOptions': {
           'format': 'png',
           'filename': f'{ticker}_chart',
           'height': 600,
           'width': 1000
       }
   }
   st.plotly_chart(fig, config=config)
   ```

3. **Loading States**
   ```python
   with st.spinner(f"Loading data for {ticker}..."):
       df = service.get_financial_data(ticker, period, limit)
   ```

4. **Error Handling**
   ```python
   try:
       df = service.get_financial_data(ticker, period, limit)
       if df.empty:
           st.warning(f"⚠️ No data available for {ticker}")
           st.stop()
   except FileNotFoundError as e:
       st.error(f"❌ Error: {e}")
       st.info("💡 Run: `python3 PROCESSORS/fundamental/calculators/company_calculator.py`")
       st.stop()
   ```

5. **Tooltips & Help**
   ```python
   st.sidebar.selectbox(
       "Select Company",
       options=tickers,
       help="Choose a company to analyze"
   )

   st.metric(
       label="ROE",
       value=f"{roe:.2f}%",
       help="Return on Equity = Net Income / Shareholders' Equity"
   )
   ```

**4.3 Documentation**

1. **README Update**
   - Document new page structure
   - Add screenshots of each dashboard
   - Update installation instructions

2. **User Guide** (create `docs/USER_GUIDE.md`)
   - How to navigate dashboards
   - How to interpret metrics
   - How to export data

3. **API Documentation** (create `docs/API_REFERENCE.md`)
   - Service layer API reference
   - Component API reference
   - Data schema documentation

**4.4 Testing**

1. **Data Validation**
   - Test all entity types (company, bank, insurance, security)
   - Test with missing data scenarios
   - Test date formatting edge cases

2. **Cross-browser Testing**
   - Chrome, Firefox, Safari
   - Mobile responsive (Streamlit mobile view)

3. **Performance Benchmarks**
   - Page load time < 2 seconds
   - Chart render time < 500ms
   - Data query time < 1 second

**Deliverables:**
- ✅ All pages optimized and tested
- ✅ User documentation complete
- ✅ Performance benchmarks met
- ✅ Error handling comprehensive

---

### 7.4 Design Standards (Apply to All Pages)

#### Color Usage

```python
# Import theme
from WEBAPP.core.theme import BRAND, SEMANTIC, CHART_PALETTE

# KPI cards - Color coding
positive_color = SEMANTIC['positive']  # #00A878 (teal green)
negative_color = SEMANTIC['negative']  # #E63946 (red)
neutral_color = SEMANTIC['neutral']    # #6B7280 (gray)

# Charts - Consistent color mapping
revenue_color = SEMANTIC['revenue']    # #009B87 (brand teal)
profit_color = SEMANTIC['profit']      # #00C9AD (light teal)
expense_color = SEMANTIC['expense']    # #E63946 (red)
asset_color = SEMANTIC['asset']        # #295CA9 (brand blue)
liability_color = SEMANTIC['liability'] # #FFC132 (brand gold)
equity_color = SEMANTIC['equity']      # #4A7BC8 (light blue)
```

#### Data Formatting Standards

**✅ Decision: Use Billions VND for all financial metrics**

```python
# Service layer returns values in billions
# (Option: Do conversion in service or in display layer)

# Display formatting
from WEBAPP.core.formatters import format_currency

st.metric("Revenue", format_currency(value, unit="B"))
# Output: "1,234.5B VND"

# Chart axis labels
yaxis_title = "VND Billions"

# Table formatting
df['net_revenue_display'] = df['net_revenue'].apply(
    lambda x: format_currency(x, unit="B")
)
```

#### Chart Configuration Standards

```python
from WEBAPP.core.theme import get_plotly_config, get_plotly_layout

# Apply to all charts
fig.update_layout(get_plotly_layout(
    title="Income Statement Trends",
    yaxis_title="VND Billions"
))

st.plotly_chart(fig, config=get_plotly_config(), use_container_width=True)
```

#### Page Structure Template

```python
# Standard page structure for all dashboards

import streamlit as st
from pathlib import Path
import sys

# Add project root
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from WEBAPP.services.{entity}_service import {Entity}Service
from WEBAPP.components.metrics.metric_cards import render_metric_card
from WEBAPP.components.charts.{type}_charts import render_*_chart
from WEBAPP.core.theme import BRAND, SEMANTIC

# Page config
st.set_page_config(
    page_title="{Entity} Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (optional, for fine-tuning)
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================
st.title("📊 {Entity} Financial Analysis")
st.markdown("Professional dashboard for Vietnamese stock analysis")
st.markdown("---")

# ============================================================================
# SIDEBAR - FILTERS
# ============================================================================
st.sidebar.header("Filters")

# Initialize service
service = {Entity}Service()
tickers = service.get_available_tickers()

ticker = st.sidebar.selectbox("Select {Entity}", options=tickers)
period = st.sidebar.selectbox("Period", ["Quarterly", "Yearly"])
limit = st.sidebar.slider("Periods", 4, 20, 8)

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data(ttl=300, show_spinner=False)
def load_data(ticker, period, limit):
    return service.get_financial_data(ticker, period, limit)

with st.spinner(f"Loading data for {ticker}..."):
    df = load_data(ticker, period, limit)

if df.empty:
    st.warning(f"⚠️ No data available for {ticker}")
    st.stop()

# ============================================================================
# SECTION 1: KEY METRICS
# ============================================================================
st.subheader("Key Financial Metrics")
# ... metric cards

# ============================================================================
# SECTION 2: CHARTS
# ============================================================================
st.subheader("Income Statement Trends")
# ... charts

# ============================================================================
# SECTION 3: TABLES
# ============================================================================
st.subheader("Financial Data")
# ... tables

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption(f"Data: DATA/processed/fundamental/{entity}/ | Ticker: {ticker} | Records: {len(df)}")
```

---

### 7.5 Migration Checklist

**Before starting each page:**
- [ ] Identify data sources (which parquet files)
- [ ] Create/update corresponding service class
- [ ] Design page layout (sketch sections)
- [ ] List required chart components
- [ ] List required filter components
- [ ] Check if data conversion needed (datetime, units)

**During implementation:**
- [ ] Import service from `WEBAPP.services`
- [ ] Import components from `WEBAPP.components`
- [ ] Import theme from `WEBAPP.core.theme`
- [ ] Use `st.cache_data` for data loading
- [ ] Convert dates to datetime in service layer
- [ ] Apply brand colors from theme
- [ ] Use Billions VND for all financial values
- [ ] Add loading spinners
- [ ] Add error handling
- [ ] Test with real data

**After implementation:**
- [ ] No PyEcharts imports
- [ ] No hardcoded colors
- [ ] No hardcoded paths
- [ ] Consistent spacing (use st.markdown("---") for dividers)
- [ ] Mobile-responsive (test in narrow mode)
- [ ] Performance < 2s page load
- [ ] Document any edge cases in code comments

---

### 7.6 Success Metrics

**By end of redesign (5 weeks):**

1. ✅ **All 9 pages rebuilt** with consistent design
2. ✅ **Single chart library** (Plotly only, no PyEcharts)
3. ✅ **Complete service layer** (9 services operational)
4. ✅ **Reusable component library** (charts, tables, filters)
5. ✅ **Brand colors** applied throughout (from theme.py)
6. ✅ **Consistent formatting** (Billions VND, 2 decimals for %)
7. ✅ **No legacy code** (no duplicate components, clean imports)
8. ✅ **Performance** (<2s page load, <500ms chart render)
9. ✅ **Documentation** (README, USER_GUIDE, API_REFERENCE)
10. ✅ **User feedback** (collect from 3+ users, iterate)

**Quality Metrics:**
- Code coverage: 80%+ (for services)
- Load time: <2s for all pages
- Error rate: <1% (robust error handling)
- User satisfaction: 4/5+ rating

---

### 7.7 Next Steps

**To start redesign:**

1. **Get user approval** on critical decisions:
   - [ ] Chart library: Plotly (recommended)
   - [ ] Data units: Billions VND (recommended)
   - [ ] Design theme: Use brand colors from theme.py

2. **Phase 1 kickoff:**
   ```bash
   # Create service files
   touch WEBAPP/services/{bank,insurance,security,technical,valuation,sector,macro,alert}_service.py

   # Create chart components
   mkdir -p WEBAPP/components/charts
   touch WEBAPP/components/charts/{fundamental,technical,valuation,sector}_charts.py

   # Create table components
   mkdir -p WEBAPP/components/tables
   touch WEBAPP/components/tables/{financial,screening,alert}_tables.py

   # Create filter components
   mkdir -p WEBAPP/components/filters
   touch WEBAPP/components/filters/{ticker_selector,date_range,sector_filter}.py

   # Remove duplicate
   rm WEBAPP/components/data_display/metric_cards.py
   ```

3. **Start with Company Dashboard** (already 70% done):
   - Extend company_dashboard_v2.py
   - Add balance sheet, cash flow, peer comparison
   - Test thoroughly
   - Use as template for other entity dashboards

4. **Iterate through phases** (Foundation → Core → Advanced → Polish)

---

**Status:** 🟡 **AWAITING USER APPROVAL** to begin implementation


---

## 8. Detailed Dashboard Specifications

**📁 All detailed specs moved to:** `docs/dashboard_specs/`

For detailed implementation guides for each dashboard page, see:

### Master Documents
- **[00_INDEX.md](dashboard_specs/00_INDEX.md)** - Overview và frontend-design plugin usage
- **[README_IMPLEMENTATION.md](dashboard_specs/README_IMPLEMENTATION.md)** - Quick reference, incremental improvement workflow

### Individual Page Specs
1. **[01_company_dashboard.md](dashboard_specs/01_company_dashboard.md)** - Company analysis (DETAILED - 70% done, extend existing)
2. **[02_bank_dashboard.md](dashboard_specs/02_bank_dashboard.md)** - Bank analysis (improve existing page)
3. **03_security_dashboard.md** - Securities analysis (improve existing page)
4. **04_technical_dashboard.md** - Technical indicators (enhance existing page)
5. **05_valuation_dashboard.md** - Valuation & sector PE/PB (enhance existing page)
6. **06_sector_dashboard.md** - Sector FA+TA combined (create new)
7. **07_macro_dashboard.md** - Macro & commodity (create new)
8. **08_forecast_dashboard.md** - BSC forecasts (improve existing page)

**⭐ Key Principle:** Build upon existing pages in `WEBAPP/pages/` - don't rebuild from scratch!

---

## 9. Quick Start

**To begin implementation:**

1. **Read**: [dashboard_specs/README_IMPLEMENTATION.md](dashboard_specs/README_IMPLEMENTATION.md) - Implementation strategy
2. **Start with**: Company Dashboard (Priority #1, 70% complete)
3. **Use**: `/frontend-design` plugin for specific sections
4. **Follow**: Incremental improvement workflow (one section at a time)
5. **Test**: After each section addition

**Implementation order:** Company → Technical → Valuation → Bank → Security → Sector → Macro → Forecast

**Estimated timeline:** 3-4 weeks (with testing and iteration)

---

**DESIGN DECISIONS (FINAL):**
- ✅ Chart Library: **Plotly ONLY** (remove PyEcharts)
- ✅ Data Units: **Billions VND** (auto-convert from VND)
- ✅ Design Theme: **Professional Financial** (Dark + Brand colors)
- ✅ Approach: **Incremental improvement** of existing pages

**Status:** ✅ **APPROVED** - Ready for implementation
