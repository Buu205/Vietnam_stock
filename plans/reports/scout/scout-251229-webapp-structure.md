# WEBAPP Scout Report - Streamlit Application Structure

**Date:** 2025-12-29  
**Scope:** WEBAPP directory structure, navigation, pages, services, and components  
**Total Files:** 113 Python files + 3 markdown files  
**Status:** ✅ Complete architectural overview

---

## Executive Summary

Vietnam Dashboard is a **multi-page Streamlit application** (v1.36+) with professional UI/UX using modern fintech/crypto aesthetic. The app features 8 dashboard pages, comprehensive data layer, reusable component library, and glassmorphism design system.

**Architecture:** MVC-inspired with separation of concerns
- **Pages** (View layer) - 8 dashboards for different analyses
- **Services** (Data layer) - Parquet data loading abstraction
- **Core** (Config layer) - Styles, theme, session state, utilities
- **Components** (UI layer) - Reusable chart, table, and input components

---

## Directory Structure (Complete Map)

```
WEBAPP/
├── main_app.py                    # Entry point - st.navigation() router (v2.0)
│
├── pages/                         # 8 Dashboard pages (View Layer)
│   ├── company/
│   │   ├── __init__.py
│   │   └── company_dashboard.py   (532 lines) - Company fundamentals
│   ├── bank/
│   │   ├── __init__.py
│   │   └── bank_dashboard.py      (682 lines) - Bank metrics + MA4 charts
│   ├── security/
│   │   ├── __init__.py
│   │   └── security_dashboard.py  (451 lines) - Brokerage analysis
│   ├── sector/
│   │   ├── __init__.py
│   │   └── sector_dashboard.py    (827 lines) - VN-Index valuation analysis
│   ├── valuation/
│   │   ├── __init__.py
│   │   └── valuation_dashboard.py (980 lines) - PE/PB/PS/EV-EBITDA percentile
│   ├── technical/
│   │   ├── __init__.py
│   │   ├── README.md
│   │   └── technical_dashboard.py (559 lines) - Price action + indicators
│   ├── forecast/
│   │   ├── __init__.py
│   │   └── forecast_dashboard.py  - BSC consensus forecasts
│   └── fx_commodities/
│       ├── __init__.py
│       └── fx_commodities_dashboard.py - FX rates + commodity prices
│
├── services/                      # Data Loading Layer (8 services)
│   ├── __init__.py
│   ├── company_service.py         - Load company financials parquet
│   ├── bank_service.py            - Load bank metrics parquet
│   ├── security_service.py        - Load securities data
│   ├── sector_service.py          - Load VN-Index valuation data
│   ├── valuation_service.py       - Load PE/PB/PS/EV ratios
│   ├── technical_service.py       - Load technical indicators
│   ├── forecast_service.py        - Load BSC forecast consensus
│   ├── llm_service.py             - LLM/Claude integration
│   ├── chat_manager.py            - Chat session management
│   ├── query_builder.py           - Query generation
│   ├── response_formatter.py      - Format LLM responses
│   ├── news_loader.py             - News data loading
│   ├── commodity_loader.py        - Commodity data
│   ├── macro_commodity_loader.py  - Macro + commodity combined
│   ├── financial_metrics_loader.py
│   └── bank_service.py
│
├── core/                          # Configuration & Core Utilities (16 files)
│   ├── __init__.py
│   ├── styles.py                  - Premium CSS (1000+ lines) - CRYPTO TERMINAL theme
│   ├── theme.py                   - Color palettes & design tokens
│   ├── session_state.py           - Streamlit session state init
│   ├── config.py                  - App configuration
│   ├── constants.py               - App-wide constants
│   ├── utils.py                   - Utility functions (datetime, percentile, etc)
│   ├── formatters.py              - Number/currency formatting
│   ├── chart_config.py            - Chart templates
│   ├── chart_schema.py            - Chart schema definitions
│   ├── data_loading.py            - Generic data loading helpers
│   ├── data_paths.py              - Path resolution utilities
│   ├── symbol_loader.py           - Symbol/ticker utilities
│   ├── display_config.py          - Display configuration
│   ├── display_settings.py        - Display settings
│   ├── valuation_config.py        - Valuation-specific config
│   └── models/
│       ├── __init__.py
│       ├── data_models.py         - Pydantic data models
│       └── market_state.py        - Market state tracking
│
├── components/                    # Reusable UI Components (Modular)
│   ├── __init__.py
│   ├── README.md                  - Component library documentation
│   │
│   ├── charts/                    # Chart builders
│   │   ├── __init__.py
│   │   ├── plotly_builders.py     - PlotlyChartBuilder class (8+ methods)
│   │   ├── valuation_charts.py    - PE/PB specific charts
│   │   ├── income_statement_chart.py
│   │   ├── advanced_charts.py
│   │   └── README.md
│   │
│   ├── navigation/                # Navigation components
│   │   ├── __init__.py
│   │   ├── main_nav.py            - Main category navigation
│   │   └── breadcrumbs.py         - Breadcrumb trail
│   │
│   ├── inputs/                    # Input controls
│   │   ├── __init__.py
│   │   ├── symbol_selector.py     - Ticker dropdown with filtering
│   │   └── date_range.py          - Date range picker with presets
│   │
│   ├── data_display/              # Data display components
│   │   ├── __init__.py
│   │   └── metric_cards.py        - KPI metric card rendering
│   │
│   ├── tables/                    # Table components
│   │   ├── __init__.py
│   │   ├── financial_tables.py    - Pivot table builders
│   │   ├── table_builders.py      - Generic table rendering
│   │   └── performance_table.py   - Performance metrics tables
│   │
│   ├── filters/                   # Filter components
│   │   ├── __init__.py
│   │   ├── global_filter_bar.py   - Global filters
│   │   └── valuation_filters.py   - Valuation-specific filters
│   │
│   ├── metrics/                   # Metric display
│   │   ├── __init__.py
│   │   ├── metric_cards.py        - Metric card rendering
│   │   ├── metrics_display.py
│   │   └── summary_row.py
│   │
│   └── ai/                        # AI components
│       └── __init__.py
│
├── domains/                       # Domain-Specific Data Loaders
│   ├── __init__.py
│   ├── banking/
│   │   ├── __init__.py
│   │   └── data_loading_bank.py
│   ├── company/
│   │   ├── __init__.py
│   │   └── data_loading_company.py
│   ├── technical/
│   │   ├── __init__.py
│   │   └── data_loading_technical.py
│   ├── valuation/
│   │   ├── __init__.py
│   │   └── data_loading_valuation.py
│   └── forecast/
│       ├── __init__.py
│       └── data_loading_forecast_csv.py
│
├── features/                      # Business Logic
│   ├── __init__.py
│   ├── growth.py                  - Growth metrics
│   ├── scoring.py                 - Scoring algorithms
│   ├── signals.py                 - Trading signals
│   └── valuation.py               - Valuation metrics
│
├── layout/                        # Layout components
│   ├── __init__.py
│   ├── sidebar.py                 - Sidebar layout
│   └── navigation.py              - Navigation layout
│
├── charts/                        # Chart configurations
│   ├── __init__.py
│   └── valuation_charts.py        - Valuation chart configs
│
├── ai/                            # AI/LLM integration
│   ├── __init__.py
│   ├── prompts.py                 - LLM prompts
│   ├── schemas.py                 - Response schemas
│   └── validators.py              - Response validators
│
├── WEBAPP_SPEC.md                 # Complete spec document (1075 lines)
└── __init__.py                    # Package metadata (v2.0.0)
```

---

## Application Flow & Navigation

### Entry Point: main_app.py (184 lines)

```python
# 1. Page Config (MUST be first st command)
st.set_page_config(
    page_title="VN Finance Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"  # Maximize viewport
)

# 2. Global Styles
st.markdown(get_page_style(), unsafe_allow_html=True)

# 3. Session State Init
init_all_pages()

# 4. Define Pages using st.Page
pages = [
    company_page,
    bank_page,
    security_page,
    sector_page,
    valuation_page,
    fx_commodities_page,
    technical_page,
    forecast_page,
]

# 5. Navigation Router (Streamlit 1.36+ feature)
pg = st.navigation({
    "Fundamental": [company_page, bank_page, security_page],
    "Analysis": [sector_page, technical_page, forecast_page, fx_commodities_page]
})

# 6. Run selected page
pg.run()
```

### Navigation Structure

```
[Fundamental Analysis]
  ├── Company Analysis     (main_app.py:59-64)
  ├── Bank Analysis        (main_app.py:66-70)
  └── Security Analysis    (main_app.py:72-76)

[Analysis & Valuation]
  ├── Sector Valuation     (main_app.py:78-82, but titled "Valuation")
  ├── Technical Analysis   (main_app.py:96-100)
  ├── FX & Commodities     (main_app.py:90-94)
  └── BSC Forecast         (main_app.py:102-106)

[Sidebar: Quick Ticker Search]
  - Text input with autocomplete
  - Filtered selectbox if multiple matches
  - Quick navigation buttons (Company, Bank, Valuation, Technical)
```

---

## Page Details (8 Dashboards)

### 1. Company Dashboard (company_dashboard.py - 532 lines)

**Purpose:** Comprehensive financial statement analysis for Vietnamese companies

**Data Source:**
```
DATA/processed/fundamental/company/company_financial_metrics.parquet
```

**Service:** `CompanyService()` - Loads financial metrics

**Sidebar Filters:**
- Ticker selector (all company tickers)
- Period: Quarterly / Yearly
- Number of periods: 4-20 (default: 12)
- Refresh button

**Metric Cards (4 KPIs):**
1. Net Revenue (billions VND)
2. Net Profit (billions VND)
3. ROE (ratio)
4. D/E Ratio (inverse delta coloring)

**Tabs:**
- **📈 Charts** → 5 chart groups:
  - Income Statement (4 bar+line combo charts with MA4 YoY)
  - Profitability Margins (4 line charts with MA4)
  - ROE/ROA Trend (dual-axis line)
  - Balance Sheet Structure (stacked bar)
  - Cash Flow Analysis (grouped bar + FCF/FCFE lines)
  
- **📋 Tables** → 3 pivot tables:
  - Income Statement
  - Balance Sheet
  - Cash Flow

**Data Columns Used:**
- Income: net_revenue, gross_profit, ebit, ebitda, npatmi
- Ratios: roe, roa, debt_to_equity
- Margins: gross_profit_margin, ebit_margin, ebitda_margin, net_margin

---

### 2. Bank Dashboard (bank_dashboard.py - 682 lines)

**Purpose:** Bank-specific metrics (NIM, CIR, NPL, CASA, ROE/ROA)

**Data Source:**
```
DATA/processed/fundamental/bank/bank_financial_metrics.parquet
```

**Service:** `BankService()` - 18 available metrics

**Available Metrics (3 categories):**
- Key Performance: NIM, CIR, NPL, ROE, ROA, LLCR, Provision/Loan
- Growth: Credit Growth, Deposit Growth, Loan Growth, NII Growth, NPATMI Growth
- Other: CASA, LDR, Asset Yield, Funding Cost, Group 2, Credit Cost

**Metric Cards (4 KPIs):**
1. Net Interest Income (billions)
2. NIM Quarterly (%)
3. ROAE TTM (%)
4. NPL Ratio (%) - inverse delta

**Tabs:**
- **📊 Charts** → Dynamic metric grid (2 per row)
  - Line charts for trends (NIM, ROE, ROA, Growth)
  - Bar charts for others
  - Income Statement with MA4 YoY (5 metrics)
  
- **📋 Tables** → 5 category tables:
  - Size, Income Statement, Growth, Asset Quality, Efficiency

**Reference Lines:**
- CIR Target: 40%
- NPL Warning: 3%
- LLCR Minimum: 100%
- LDR SBV Limit: 85%

---

### 3. Security Dashboard (security_dashboard.py - 451 lines)

**Purpose:** Securities/Brokerage company analysis

**Data Source:**
```
DATA/processed/fundamental/security/security_financial_metrics.parquet
```

**Metric Cards (4 KPIs):**
1. Total Revenue (billions)
2. Net Profit (billions)
3. ROAE TTM (%)
4. Leverage (x)

**Tabs:**
- **📊 Charts** (3 rows × 2 columns):
  - Revenue Mix (stacked bar)
  - ROAE & ROAA (dual line)
  - Portfolio Composition (pie)
  - Profit Margins (line)
  - CIR (bar with y=50 reference)
  - Leverage Trend (line with fill)
  
- **📋 Tables**:
  - Income Statement
  - Balance Sheet Summary
  - Key Financial Ratios

---

### 4. Sector Dashboard (sector_dashboard.py - 827 lines)

**Purpose:** Market-level PE/PB valuation analysis by sector

**Data Source:**
```
DATA/processed/valuation/vnindex/vnindex_valuation_with_sectors.parquet
```

**Service:** `SectorService()` - VN-Index valuation aggregates

**Sidebar Filters:**
- Primary Metric: PE TTM / PB
- History (Days): 30-2000 (default: 1000)

**Metric Cards (4 KPIs):**
1. Lowest PE Sector (text)
2. VNINDEX PE (current)
3. VNINDEX PB (current)
4. Sector Count / Ticker Count

**Tabs:**
- **🕯️ All Sectors Distribution**:
  - Candlestick distribution chart
    - Whiskers: P5-P95
    - Body: P25-P75
    - Current value dot (colored by percentile)
  - Distribution statistics table
  
- **📈 Individual Analysis**:
  - Scope selector: Market Indices | Sectors
  - Line chart with statistical bands
    - ±2 SD band (blue, light)
    - ±1 SD band (teal, light)
    - Main line (teal)
    - Median line (gold)
    - Mean line (blue, dashed)
  
- **📋 Data**:
  - Sector Valuation Overview
  - Sector Composition

**Color Coding:**
- Undervalued: #009B87 (< P25)
- Fair: #FFC132 (P25-P75)
- Expensive: #E53E3E (> P75)

---

### 5. Valuation Dashboard (valuation_dashboard.py - 980 lines)

**Purpose:** Individual stock PE/PB/PS/EV-EBITDA percentile analysis

**Data Source:** Multiple valuation parquet files via `ValuationService`

**Sidebar Filters:**
- Metric: P/E, P/B, P/S, EV/EBITDA
- Industry: "Tất cả" + all industries (default: Banking)
- Ticker: Filtered by industry
- Start Year: 2018-2024 (default: 2020)

**Tabs:**
- **📊 Sector Comparison**:
  - Candlestick chart (same as Sector dashboard)
  - Premium Statistics Table (custom HTML)
    - Ticker, Current, Median, Percentile bar, Status badge
  - Download Excel button
  
- **📈 Individual Analysis**:
  - Large trend chart (600px height)
    - ±2 SD & ±1 SD bands
    - Main metric line (teal)
    - Mean line (white, solid)
    - Current value marker (gold)
  - KPI Cards + Histogram
    - Current, Mean, Z-Score, ±1 SD
  - Download Excel button

**Status Classifications:**
- Very Cheap: #00D4AA (< P10)
- Cheap: #7FFFD4 (P10-P25)
- Fair: #FFD666 (P25-P75)
- Expensive: #FF9F43 (P75-P90)
- Very Expensive: #FF6B6B (> P90)

---

### 6. Technical Dashboard (technical_dashboard.py - 559 lines)

**Purpose:** Technical analysis with indicators (RSI, MACD, ADX, Moving Averages)

**Data Source:**
```
DATA/processed/technical/basic_data.parquet
```

**Sidebar Filters:**
- Stock: All tickers
- History (Days): 30-500 (default: 180)
- Show Volume: Checkbox
- Show Bollinger Bands: Checkbox

**Metric Cards (5 KPIs):**
1. Close Price (% change)
2. RSI (14) - 🔴/>70, 🟢/<30, ⚪/else
3. Price vs SMA50 - 📈/>0, 📉/<0
4. ADX (14) - 💪/>25, 😴/<25
5. MACD - 🟢/🔴 signal

**Tabs:**
- **📊 Price & Volume**:
  - OHLC candlestick (green: #00D4AA, red: #FF6B6B)
  - SMA 20, SMA 50, SMA 200, Bollinger Bands
  - Volume bars (colored by direction)
  - MA Signal Summary table
  - Trend Analysis table
  
- **📈 Oscillators**:
  - RSI (14) with zones
  - MACD (histogram + lines)
  - Stochastic Oscillator (%K, %D)
  - CCI (20)
  
- **📋 Data**:
  - Price & Moving Averages
  - Volatility
  - Momentum Indicators
  - Volume Indicators

**Technical Indicators Available:**
- Moving Averages: sma_20, sma_50, sma_100, sma_200, ema_20, ema_50
- Momentum: rsi_14, macd, macd_signal, macd_hist, adx_14, stoch_k, stoch_d, cci_20, mfi_14
- Volatility: atr_14, bb_upper, bb_middle, bb_lower, bb_width
- Volume: volume, obv, cmf_20
- Price: price_vs_sma50

---

### 7. Forecast Dashboard (forecast_dashboard.py)

**Purpose:** BSC consensus forecasts

---

### 8. FX & Commodities Dashboard (fx_commodities_dashboard.py)

**Purpose:** FX rates and commodity prices tracking

---

## Services Layer (Data Abstraction)

All services follow **consistent pattern**:

```python
class XxxService:
    def __init__(self, data_root: Optional[Path] = None):
        # Auto-detect project root if not provided
        self.data_path = data_root / "processed" / "xxx"
        # Validate path exists
    
    def get_financial_data(self, ticker, period, limit) -> pd.DataFrame:
        # Load parquet, filter, sort, limit
    
    def get_latest_metrics(self, ticker) -> Dict:
        # Return last row as dict
    
    def get_available_tickers(self) -> List[str]:
        # Unique sorted tickers
```

### Services Available (8 files)

| Service | Data Path | Purpose |
|---------|-----------|---------|
| **CompanyService** | `DATA/processed/fundamental/company/` | Company financials |
| **BankService** | `DATA/processed/fundamental/bank/` | Bank metrics |
| **SecurityService** | `DATA/processed/fundamental/security/` | Securities data |
| **SectorService** | `DATA/processed/valuation/vnindex/` | VN-Index valuation |
| **ValuationService** | `DATA/processed/valuation/` | PE/PB/PS/EV-EBITDA |
| **TechnicalService** | `DATA/processed/technical/` | Price + indicators |
| **ForecastService** | `DATA/processed/forecast/bsc/` | BSC forecasts |
| **LLMService** | N/A | Claude API integration |

### Service Features

**Data Loading:**
- Auto-detect project root
- Column selection for performance
- TTL-based caching (3600s default)
- Error handling with informative messages

**Available Methods:**
- `get_financial_data(ticker, period, limit)` → DataFrame
- `get_latest_metrics(ticker)` → Dict
- `get_available_tickers()` → List[str]
- `validate_ticker(ticker)` → bool

---

## Core Configuration System

### Theme System (crypto_terminal_glassmorphism.md)

**Design Direction:** Fintech/Crypto Terminal with glassmorphism effects

**Color Palette:**
```python
PURPLE = {
    'primary': '#8B5CF6',      # Electric Purple (CTA)
    'dark': '#7C3AED',         # Hover states
    'light': '#A78BFA',        # Highlights
    'glow': 'rgba(139, 92, 246, 0.4)'
}

CYAN = {
    'primary': '#06B6D4',      # Secondary actions
    'dark': '#0891B2',
    'light': '#22D3EE'
}

AMBER = {
    'primary': '#F59E0B',      # Highlights, warnings
    'light': '#FBBF24'
}

SEMANTIC = {
    'positive': '#10B981',     # Bullish (green candles)
    'negative': '#EF4444',     # Bearish (red candles)
    'neutral': '#6B7280'       # Unchanged
}
```

**Dark Theme (OLED Optimized):**
```python
DARK_THEME = {
    'background': '#0F0B1E',          # Deep purple-black
    'surface': '#1A1625',             # Card surface
    'elevated': '#252033',            # Elevated cards
    'text_primary': '#F8FAFC',        # White text
    'text_secondary': '#94A3B8'       # Muted gray
}
```

**Glassmorphism Effects:**
```python
GLASS = {
    'bg_subtle': 'rgba(255, 255, 255, 0.03)',
    'bg_medium': 'rgba(255, 255, 255, 0.05)',
    'blur': 'blur(12px)',
    'shadow': '0 8px 32px rgba(0, 0, 0, 0.3)',
    'inner_highlight': 'inset 0 1px 0 rgba(255, 255, 255, 0.05)'
}
```

**Typography:**
- Display/Heading: Space Grotesk
- Body: DM Sans
- Mono/Data: JetBrains Mono

### Styles System (styles.py - 1000+ lines)

**Premium CSS Injection:**
- Dark dropdown backgrounds
- Chart overflow fixes
- Responsive containers
- Custom table styling
- Glassmorphism card effects

**Functions:**
- `get_page_style()` → Complete CSS
- `get_chart_layout()` → Plotly layout config
- `render_styled_table()` → Dark-themed table HTML
- `get_table_style()` → Table-specific CSS

### Session State Management (session_state.py)

**Purpose:** Prevent widget reset issues on interaction

**Page State Defaults:**
```python
PAGE_STATE_DEFAULTS = {
    'global': {
        'global_ticker_search': '',
        'quick_search_ticker': None,
    },
    'company': {
        'selected_ticker': 'VNM',
        'company_timeframe': 'Quarterly',
        'company_active_tab': 0,      # Persist tab selection
    },
    'bank': {
        'selected_bank': 'VCB',
        'bank_timeframe': 'Quarterly',
        'bank_active_tab': 0,
    },
    # ... per-page state for all 8 pages
}

def init_page_state(page_name: str) -> None:
    """Initialize session state for a page."""
    if page_name not in st.session_state:
        st.session_state[page_name] = PAGE_STATE_DEFAULTS.get(page_name, {})
```

---

## Components Library

### Chart Components (charts/)

**PlotlyChartBuilder** - Main chart builder class

Available Methods:
1. `line_chart()` - Multi-line trend charts
2. `bar_chart()` - Simple bar charts
3. `bar_line_combo()` - Bar + Line overlay (MOST USED)
4. `candlestick_chart()` - PE/PB analysis
5. `heatmap()` - Sector comparison
6. `line_with_bands()` - Statistical bands (valuation)
7. `waterfall_chart()` - Cash flow breakdown

**Usage:**
```python
from WEBAPP.components.charts import PlotlyChartBuilder as pcb

fig = pcb.bar_line_combo(
    df=data,
    x_col='quarter',
    bar_col='net_revenue',
    line_col='net_revenue_ma4',
    title='Revenue with MA4',
    bar_name='Revenue',
    line_name='MA4 Trend'
)
st.plotly_chart(fig, use_container_width=True)
```

### Input Components (inputs/)

**SymbolSelector** - Enhanced ticker dropdown
```python
symbol = symbol_selector(
    entity_type='company',  # 'company', 'bank', 'security', 'insurance', 'all'
    default='VNM',
    key='my_symbol_selector'
)
```

**DateRangePicker** - Date range with presets
```python
start_date, end_date = date_range_picker(
    default_start='2023-01-01',
    default_end='2025-12-29',
    key='my_date_range'
)
```

### Display Components (data_display/)

**MetricCards** - KPI metric rendering
```python
metric_card_row([
    {
        'label': 'Net Revenue',
        'value': 1234.56,
        'delta': 12.3,
        'format': 'billions',
        'delta_format': 'percent'
    }
])
```

### Table Components (tables/)

**FinancialTables** - Pivot table builders
- Income Statement table
- Balance Sheet table
- Cash Flow table

---

## Data Flow & Integration

### Standard Data Flow

```
┌─────────────────┐
│  Data Pipeline  │ (PROCESSORS/)
│  (v4.0.0)       │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────┐
│  DATA/processed/            │ (Parquet files)
│  ├── fundamental/           │
│  │   ├── company/           │
│  │   ├── bank/              │
│  │   ├── security/          │
│  │   └── insurance/         │
│  ├── valuation/             │
│  ├── technical/             │
│  └── forecast/              │
└────────┬────────────────────┘
         │
         ↓
┌─────────────────────────────┐
│  Services Layer             │ (WEBAPP/services/)
│  ├── CompanyService         │ → Reads parquet
│  ├── BankService            │ → Filters by ticker
│  ├── ValuationService       │ → Returns DataFrame
│  └── TechnicalService       │
└────────┬────────────────────┘
         │
         ↓
┌─────────────────────────────┐
│  Page Controllers           │ (WEBAPP/pages/)
│  ├── company_dashboard.py   │ → Loads via service
│  ├── bank_dashboard.py      │ → Caches with @st.cache_data
│  └── ...                    │ → Renders with components
└────────┬────────────────────┘
         │
         ↓
┌─────────────────────────────┐
│  Components                 │ (WEBAPP/components/)
│  ├── Charts (Plotly)        │ → Builds charts
│  ├── Tables (HTML)          │ → Formats data
│  └── Inputs                 │ → User interaction
└────────┬────────────────────┘
         │
         ↓
┌─────────────────────────────┐
│  Browser (Streamlit Client) │
│  Rendered UI                │
└─────────────────────────────┘
```

### Caching Strategy

**Level 1: Service Caching**
```python
@st.cache_data(ttl=3600)
def get_financial_data(ticker, period):
    """Cache parquet reads for 1 hour"""
    service = CompanyService()
    return service.get_financial_data(ticker, period)
```

**Level 2: Session State**
```python
# Prevent re-renders on widget interaction
init_page_state('company')
ticker = st.session_state.get('company_ticker', 'VNM')
```

**Level 3: Data-Level Caching**
```python
# Services internally cache/batch read parquet
df = service.get_financial_data(ticker, period, limit=100)
```

---

## Registry Integration (Critical)

All pages follow registry pattern for metadata:

```python
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry

# Metric lookup (Vietnamese → English)
metric_reg = MetricRegistry()
metric = metric_reg.get_metric("CIS_62", "COMPANY")

# Ticker/Sector lookup
sector_reg = SectorRegistry()
ticker_info = sector_reg.get_ticker("VNM")
peers = sector_reg.get_peers("VNM")

# Data formatting via schema
schema_reg = SchemaRegistry()
formatted_price = schema_reg.format_price(25750.5)  # "25,750.50đ"
formatted_percent = schema_reg.format_percent(0.156)  # "15.60%"
```

---

## Key Features & Patterns

### 1. Multi-Page Navigation
- Uses Streamlit 1.36+ `st.navigation()` feature
- 2 main categories: "Fundamental" & "Analysis"
- Grouped into 8 pages
- Quick search sidebar for ticker jumping

### 2. Session State Management
- Per-page state initialization prevents widget resets
- Tab selection persists across interactions
- Sidebar filters maintain state

### 3. Responsive Layout
- Wide layout (maximize viewport)
- 2-4 column grids for metric cards
- Dynamic chart heights (300-600px)
- Glassmorphism card design

### 4. Dark Theme (Crypto Terminal)
- Deep purple-black background (#0F0B1E)
- Electric purple accent (#8B5CF6)
- Cyan secondary (#06B6D4)
- OLED-optimized colors

### 5. Data Abstraction
- Service layer hides parquet complexity
- Auto-detection of project root
- Consistent API across services
- Column-level filtering for performance

### 6. Chart Components
- PlotlyChartBuilder for consistency
- 7+ chart methods (line, bar, combo, candlestick, etc)
- Built-in styling (colors, fonts, layouts)
- Responsive sizing

### 7. Financial Formatting
- Number formatting with separators
- Currency display (billions VND)
- Percentage formatting
- Ratio display (x)

---

## Configuration Files

### WEBAPP_SPEC.md (1075 lines)

**Comprehensive specification document:**
- Architecture overview
- Page specifications (4.1-4.6)
- Service layer documentation
- Components library reference
- Common issues & fixes
- UI/UX optimization checklist
- Design prompt templates (5 aesthetic options)
- Quick start guides

### main_app.py (184 lines)

**Entry point configuration:**
- Page definitions (st.Page objects)
- Navigation structure (st.navigation groups)
- Sidebar quick search
- Global styles injection
- Session state initialization

---

## Code Quality Standards

### Imports Pattern
```python
# 1. Standard library
import sys
from pathlib import Path

# 2. Third-party packages
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 3. Local imports
from WEBAPP.services.company_service import CompanyService
from WEBAPP.core.styles import get_page_style
```

### Session State Initialization
```python
# Each page starts with:
from WEBAPP.core.session_state import init_page_state

st.markdown(get_page_style(), unsafe_allow_html=True)
init_page_state('company')
```

### Data Loading
```python
# Cache data with TTL
@st.cache_data(ttl=3600, show_spinner=False)
def load_data(ticker, period):
    service = CompanyService()
    return service.get_financial_data(ticker, period, limit=100)
```

### Chart Rendering
```python
# Always use use_container_width=True
fig = pcb.bar_line_combo(df, ...)
st.plotly_chart(fig, use_container_width=True)
```

---

## Known Design Patterns & Standards

### Chart Colors
- Primary: Teal #009B87
- Secondary: Blue #295CA9
- Tertiary: Gold #FFC132
- Positive: Emerald #10B981
- Negative: Red #E53E3E

### Chart Heights
- Small grid cell: 280px
- Medium: 300-400px
- Large (main focus): 500-600px
- With volume: 550px

### Layout Patterns
- 2 columns: `st.columns(2)` for balanced layout
- 4 metric cards: `st.columns(4)` for KPIs
- Tabs: `st.tabs(["Tab1", "Tab2"])` for organization
- Sections: `st.markdown("---")` for visual separation

---

## Performance Considerations

1. **Parquet Column Selection** - Load only needed columns
2. **TTL Caching** - 3600s default for data stability
3. **Session State** - Prevents re-runs on widget interaction
4. **Lazy Loading** - Charts built on-demand
5. **Vectorized Operations** - Pandas for data processing

---

## Extension Points

### Adding New Dashboard Page

1. Create `WEBAPP/pages/mynew/mynew_dashboard.py`
2. Define service in `WEBAPP/services/mynew_service.py`
3. Add to `main_app.py` navigation:
```python
mynew_page = st.Page(
    "WEBAPP/pages/mynew/mynew_dashboard.py",
    title="My New Page",
    icon=":material/icon:"
)
pg = st.navigation({
    "Category": [..., mynew_page]
})
```

### Adding New Chart Type

1. Add method to `PlotlyChartBuilder` in `components/charts/plotly_builders.py`
2. Import and use in page:
```python
from WEBAPP.components.charts import PlotlyChartBuilder as pcb
fig = pcb.my_new_chart(df, ...)
```

### Adding New Component

1. Create `WEBAPP/components/newtype/my_component.py`
2. Export in `components/__init__.py`
3. Use in any page:
```python
from WEBAPP.components.newtype import my_component
my_component(data)
```

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Python Files** | 113 |
| **Total Markdown Docs** | 3 |
| **Dashboard Pages** | 8 |
| **Data Services** | 8 |
| **Component Modules** | 12 |
| **Core Config Files** | 16 |
| **Total Lines of Code** | ~15,000+ |

---

## Quick Navigation

**Key Files to Read First:**
1. `main_app.py` - Entry point (184 lines)
2. `WEBAPP_SPEC.md` - Complete specification (1075 lines)
3. `pages/company/company_dashboard.py` - Page template (532 lines)
4. `services/company_service.py` - Service template (150+ lines)
5. `core/styles.py` - Styling system (1000+ lines)
6. `core/theme.py` - Design tokens (472 lines)

**For New Contributors:**
1. Read `WEBAPP_SPEC.md` sections 1-3
2. Study `pages/company/company_dashboard.py` structure
3. Review `components/charts/plotly_builders.py` methods
4. Check `services/company_service.py` pattern
5. Run dashboard: `streamlit run WEBAPP/main_app.py`

---

## Unresolved Questions

1. **Forecast Dashboard** - Implementation status (fx_commodities page exists but not fully documented)
2. **AI Integration** - LLM service and chat manager status
3. **FX & Commodities** - Data source and refresh frequency
4. **Mobile Responsive** - Streamlit mobile support status
5. **Performance** - Parquet file sizes and loading times for large datasets

