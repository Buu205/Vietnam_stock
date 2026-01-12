# WEBAPP Architecture Analysis Report

**Date:** 2026-01-11  
**Project:** Vietnam Dashboard  
**Component:** WEBAPP (Streamlit Application)  
**Files Analyzed:** 133 Python files  
**Purpose:** Document web application structure, architecture patterns, and key functionality

---

## Executive Summary

The WEBAPP is a **multi-page Streamlit application** for Vietnamese stock market analysis. It provides comprehensive financial, valuation, technical, and forecasting analysis across 7 main dashboards serving 457 tickers across 19 sectors.

**Key Design Philosophy:**
- **Theme:** Crypto Terminal Dark Mode with Glassmorphism
- **Primary Colors:** Electric Purple (#8B5CF6), Cyan (#06B6D4), Amber (#F59E0B)
- **Architecture:** Service-oriented with component-based UI
- **Data Layer:** Parquet files via DuckDB for performance

---

## Directory Structure

```
WEBAPP/
├── main_app.py                 # Entry point - st.navigation() router
├── requirements.txt            # Python dependencies
├── WEBAPP_SPEC.md             # Comprehensive spec (27KB)
│
├── pages/                      # 7 Dashboard Pages
│   ├── company/               # Company fundamental analysis
│   ├── bank/                  # Bank financial metrics
│   ├── security/              # Securities company analysis
│   ├── sector/                # Sector & valuation overview
│   ├── technical/             # Technical analysis
│   ├── forecast/              # BSC Forecast module
│   └── fx_commodities/        # FX & commodities
│
├── services/                   # Data Loading Layer (15 services)
│   ├── base_service.py        # Abstract base class
│   ├── company_service.py     # Company data loader
│   ├── bank_service.py        # Bank data loader
│   ├── security_service.py    # Securities data loader
│   ├── sector_service.py      # Sector aggregation
│   ├── valuation_service.py   # PE/PB/EV-EBITDA
│   ├── technical_service.py   # Price/technical indicators
│   ├── forecast_service.py    # Forecast data loader
│   ├── commodity_loader.py    # Commodity data
│   ├── macro_commodity_loader.py
│   ├── financial_metrics_loader.py
│   ├── news_loader.py
│   ├── llm_service.py         # AI integration
│   ├── chat_manager.py
│   ├── query_builder.py
│   └── response_formatter.py
│
├── core/                       # Core Utilities (20 files)
│   ├── config.py              # Display configuration
│   ├── data_loading.py        # Generic data loaders
│   ├── data_paths.py          # Path resolution
│   ├── formatters.py          # Number/date formatting
│   ├── styles.py              # CSS/styling (1000+ lines)
│   ├── theme.py               # Color palette & design tokens
│   ├── session_state.py       # State management (435 lines)
│   ├── symbol_loader.py       # Master symbols loader
│   ├── chart_schema.py        # Plotly schema
│   ├── trading_constants.py   # Trading rules/thresholds
│   ├── display_config.py
│   ├── display_settings.py
│   ├── trading_rules.py
│   ├── constants.py
│   └── utils.py
│   └── models/
│       ├── data_models.py
│       └── market_state.py
│
├── components/                 # Reusable UI Components
│   ├── charts/                # Chart builders
│   │   ├── plotly_builders.py
│   │   ├── income_statement_chart.py
│   │   ├── valuation_charts.py
│   │   └── advanced_charts.py
│   ├── tables/                # Table renderers
│   │   ├── financial_tables.py
│   │   ├── table_builders.py
│   │   ├── consensus_table.py
│   │   ├── performance_table.py
│   │   └── unified_forecast_table.py
│   ├── metrics/               # KPI cards
│   │   └── metrics_display.py
│   ├── filters/               # Input widgets
│   │   ├── fundamental_filter_bar.py
│   │   └── symbol_selector.py
│   ├── inputs/
│   ├── data_display/
│   ├── navigation/
│   ├── styles/
│   ├── cards/
│   ├── summary_row.py
│   ├── ui/
│   └── metrics_display.py
│
├── domains/                    # Domain-Specific Data Loaders
│   ├── company/
│   │   └── data_loading_company.py
│   ├── banking/
│   │   └── data_loading_bank.py
│   ├── technical/
│   │   └── data_loading_technical.py
│   ├── valuation/
│   │   └── data_loading_valuation.py
│   └── forecast/
│       └── data_loading_forecast_csv.py
│
├── features/                   # Business Logic
│   ├── signals.py             # Trading signals
│   ├── scoring.py             # Stock scoring
│   ├── growth.py              # Growth metrics
│   └── valuation.py
│
├── ai/                         # LLM Integration
│   ├── prompts.py             # Prompt templates
│   ├── schemas.py             # Response schemas
│   └── validators.py
│
├── layout/                     # Layout Components
│   ├── navigation.py          # Navigation helpers
│   └── sidebar.py
│
├── assets/                     # Static assets
└── .streamlit/                # Streamlit config
```

---

## Architecture Patterns

### 1. **Service Pattern (Data Layer)**

All data access goes through service classes that inherit from `BaseService`:

```python
class CompanyService(BaseService):
    DATA_SOURCE = "company_metrics"
    ENTITY_TYPE = "company"
    
    def get_financial_data(self, ticker, period, limit) -> pd.DataFrame:
        # Load parquet, filter, sort, return
```

**Key Services:**
| Service | Data Path | Purpose |
|---------|-----------|---------|
| `CompanyService` | `DATA/processed/fundamental/company/` | Company financials |
| `BankService` | `DATA/processed/fundamental/bank/` | Bank metrics (NIM, CIR, NPL) |
| `SecurityService` | `DATA/processed/fundamental/security/` | Brokerage metrics |
| `SectorService` | `DATA/processed/valuation/vnindex/` | Sector aggregation |
| `ValuationService` | `DATA/processed/valuation/` | PE/PB/EV-EBITDA |
| `TechnicalService` | `DATA/processed/technical/` | Price data & indicators |
| `ForecastService` | `DATA/processed/forecast/bsc/` | BSC forecasts |

**Features:**
- Path resolution via registry
- Automatic schema validation
- Caching with TTL (3600s default)
- Outlier filtering

---

### 2. **Session State Management**

Centralized state management via `session_state.py`:

**Pattern:**
```python
# Initialize page state
init_page_state('company')

# Persistent tabs (don't reset on widget interaction)
render_persistent_tabs(["Charts", "Tables"], "company_active_tab")

# Cross-page ticker sync
set_synced_ticker("ACB", "BANK", "Ngân hàng")
```

**State Keys:**
- `company_active_tab`: Charts vs Tables
- `selected_ticker`: Current ticker selection
- `sync_last_ticker`: Cross-page sync (Fundamental → Forecast/Technical)
- Lazy loading flags: `_loaded_{tab_name}`

---

### 3. **Component-Based UI**

Reusable components organized by type:

**Charts** (`components/charts/`):
- `plotly_builders.py`: Standardized chart layouts
- `income_statement_chart.py`: Income statement visualization
- `valuation_charts.py`: Valuation distribution charts
- `advanced_charts.py`: Complex multi-axis charts

**Tables** (`components/tables/`):
- `financial_tables.py`: Income statement, balance sheet, cash flow pivot tables
- `table_builders.py`: Generic table builders
- `unified_forecast_table.py`: Forecast data grid
- `consensus_table.py`: Analyst consensus

**Metrics** (`components/metrics/`):
- `metrics_display.py`: KPI card rendering with deltas

---

### 4. **Theming System (Crypto Terminal Dark Mode)**

**Design Philosophy:**
- **Aesthetic:** Fintech/crypto terminal with glassmorphism
- **Primary:** Electric Purple (#8B5CF6)
- **Secondary:** Cyan (#06B6D4)
- **Accent:** Amber (#F59E0B)
- **Background:** Deep purple-black (#0F0B1E - OLED optimized)

**Theme Files:**
- `core/theme.py`: Color definitions (472 lines)
- `core/styles.py`: CSS injection (1000+ lines)
- `core/formatters.py`: Number/date formatting

**Color Palette:**
```python
# Primary Colors
PURPLE = {
    'primary': '#8B5CF6',     # Main CTA, active tabs
    'dark': '#7C3AED',
    'light': '#A78BFA',
    'glow': 'rgba(139, 92, 246, 0.4)',
}

CYAN = {
    'primary': '#06B6D4',     # Secondary actions
    'dark': '#0891B2',
    'light': '#22D3EE',
}

# Semantic
SEMANTIC = {
    'positive': '#10B981',    # Bullish, gains
    'negative': '#EF4444',    # Bearish, losses
    'warning': '#F59E0B',     # Amber
}
```

**Glassmorphism Effects:**
```css
background: rgba(255, 255, 255, 0.03);
backdrop-filter: blur(12px);
border: 1px solid rgba(255, 255, 255, 0.08);
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
```

---

## Page Modules

### 1. **Company Dashboard** (`pages/company/`)

**File:** `company_dashboard.py` (532 lines)

**Features:**
- 4 KPI cards: Revenue, Profit, ROE, D/E ratio
- Charts tab: Income statement, margins, ROE/ROA, balance sheet, cash flow
- Tables tab: Financial statement pivot tables

**Data Source:**
```python
service = CompanyService()
df = service.get_financial_data(ticker, period, limit=100)
```

**Key Charts:**
- Income Statement (bar + MA4 YoY line)
- Profitability Margins (bar + MA4 line)
- ROE/ROA Trend (dual-axis)
- Balance Sheet Structure (stacked bar)
- Cash Flow Analysis (grouped bar + FCF/FCFE lines)

---

### 2. **Bank Dashboard** (`pages/bank/`)

**File:** `bank_dashboard.py` (682 lines)

**Features:**
- 18 available metrics: NIM, CIR, NPL, ROE, ROA, LLCR, CASA, LDR, etc.
- Quick select buttons: Key Performance, Growth Focus, All Metrics
- Income statement charts with MA4 YoY

**Key Metrics:**
| Metric | Column | Format |
|--------|--------|--------|
| Net Interest Income | `nii` | Billions |
| NIM | `nim_q` | Percent |
| ROAE (TTM) | `roea_ttm` | Percent |
| NPL Ratio | `npl_ratio` | Percent |

**Reference Lines:**
- CIR target: 40%
- NPL warning: 3%
- LLCR minimum: 100%
- LDR SBV limit: 85%

---

### 3. **Security Dashboard** (`pages/security/`)

**File:** `security_dashboard.py` (451 lines)

**Features:**
- Revenue mix breakdown (brokerage fee, investment income)
- Portfolio composition pie chart (FVTPL, HTM, AFS, margin loans)
- ROAE & ROAA trends
- CIR (reference line at 50%)
- Leverage trend with fill

---

### 4. **Sector Dashboard** (`pages/sector/`)

**File:** `sector_dashboard.py` (827 lines)

**Features:**
- All Sectors Distribution: Candlestick chart (P5-P95 whiskers, P25-P75 body)
- Individual Analysis: Line chart with ±1SD, ±2SD bands
- Market Indices: VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX
- Valuation Assessment: Undervalued (<P25), Fair (P25-P75), Expensive (>P75)

**Color Coding:**
```python
ASSESSMENT_COLORS = {
    'undervalued': '#009B87',   # Teal
    'fair': '#FFC132',          # Gold
    'expensive': '#E53E3E',     # Red
}
```

---

### 5. **Technical Dashboard** (`pages/technical/`)

**File:** `technical_dashboard.py` (559 lines)

**Features:**
- 5 KPI cards: Close, RSI(14), Price vs SMA50, ADX(14), MACD
- Price & Volume: OHLC candlestick with SMA 20/50/200, Bollinger Bands
- Oscillators: RSI, MACD, Stochastic, CCI
- Technical indicators: 20+ indicators (MA, RSI, MACD, ADX, ATR, BB, OBV, etc.)

**Indicators Available:**
| Category | Indicators |
|----------|------------|
| Moving Averages | sma_20, sma_50, sma_200, ema_20, ema_50 |
| Momentum | rsi_14, macd, adx_14, stoch_k, stoch_d, cci_20, mfi_14 |
| Volatility | atr_14, bb_upper, bb_middle, bb_lower |
| Volume | volume, obv, cmf_20 |

---

### 6. **Forecast Dashboard** (`pages/forecast/`)

**Features:**
- BSC price target forecasts
- Sector aggregation
- 9-month forward estimates
- Consensus vs analyst estimates
- Rating distribution

**Data Source:**
```python
service = ForecastService()
df = service.get_forecast_data()
```

---

### 7. **FX & Commodities** (`pages/fx_commodities/`)

**Features:**
- FX rates (USD/VND, EUR/VND)
- Commodity prices (gold, oil, copper)
- Historical trend analysis

---

## Core Utilities

### **Data Loading** (`core/data_loading.py`)

**Functions:**
```python
@st.cache_data(ttl=3600)
def load_valuation_generic(symbol, start_date, pe_path, pb_path, ev_path):
    # Load PE/PB/EV-EBITDA with outlier filtering

def get_all_symbols(entity_type=None):
    # Get liquid symbols (315 tickers with >1B VND/day)
```

**Features:**
- DuckDB for fast parquet reads
- Outlier clipping (PE <100, PB <10, EV/EBITDA <100)
- Cached with configurable TTL

---

### **Formatters** (`core/formatters.py`)

**Format Functions:**
```python
format_currency(value)      # VND with separators
format_percentage(value)    # Percent with 1 decimal
format_ratio(value)         # PE/PB with 2 decimals
format_date(value, type)    # Display/axis/tooltip formats
```

**Date Formats:**
```python
DATE_FORMATS = {
    'display': '%Y/%m/%d',    # YYYY/MM/DD
    'axis': '%m/%Y',          # MM/YYYY
    'tooltip': '%d/%m/%Y',    # DD/MM/YYYY
}
```

---

### **Session State** (`core/session_state.py`)

**Key Functions:**
```python
init_page_state(page_name, extra_defaults=None)
render_persistent_tabs(tab_names, state_key, style="primary")
set_synced_ticker(ticker, entity_type, sector)
lazy_load_data(tab_key, load_func, *args, **kwargs)
```

**Cross-Page Sync:**
- When user selects ticker in Fundamental pages → syncs to Forecast/Technical
- Keys: `sync_last_ticker`, `sync_last_entity`, `sync_last_sector`

---

### **Styles** (`core/styles.py`)

**Purpose:** Unified styling system for all pages

**Key Functions:**
```python
get_page_style()           # Inject global CSS (1000+ lines)
get_chart_layout()         # Plotly layout template
get_table_style()          # Table CSS styling
render_styled_table(df)    # Render DataFrame with custom styles
```

**Chart Layout Template:**
```python
{
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'font': {'color': '#F8FAFC', 'size': 11},
    'margin': {'l': 60, 'r': 60, 't': 80, 'b': 60},
    'xaxis': {'gridcolor': 'rgba(255,255,255,0.08)'},
    'yaxis': {'gridcolor': 'rgba(255,255,255,0.08)'},
    'legend': {'orientation': 'h', 'y': -0.15},
}
```

---

## Navigation System

### **Main App Router** (`main_app.py`)

**Architecture:** Streamlit 1.36+ `st.navigation()`

```python
pg = st.navigation({
    "Fundamental": [company_page, bank_page, security_page],
    "Analysis": [sector_page, technical_page, forecast_page, fx_commodities_page]
})
pg.run()
```

**Pages:**
1. Company Analysis (default)
2. Bank Analysis
3. Security Analysis
4. Sector & Valuation
5. Technical Analysis
6. BSC Forecast
7. FX & Commodities

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT DASHBOARD                       │
│                   (main_app.py + pages/)                     │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVICES LAYER                            │
│         (company_service, bank_service, etc.)                │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                   PARQUET DATA FILES                         │
│         DATA/processed/{fundamental|technical|valuation}/    │
└─────────────────────────────────────────────────────────────┘
```

**Loading Pattern:**
1. User selects ticker/period in UI
2. Page calls `service.get_financial_data(ticker, period)`
3. Service loads parquet via DuckDB (cached)
4. Returns filtered DataFrame
5. Components render charts/tables

---

## Performance Optimizations

### **Caching Strategy**

```python
# Static data (24h TTL)
@st.cache_data(ttl=86400)
def load_symbol_list(path):

# Cold data (1h TTL)
@st.cache_data(ttl=3600)
def load_valuation_generic(...):

# Per-page data (1h TTL)
@st.cache_data(ttl=3600)
def load_full_data(ticker, period):
```

### **Lazy Loading**

```python
# Only load tab data when first accessed
if not is_tab_loaded('forecast_sector_tab'):
    load_sector_data()
    mark_tab_loaded('forecast_sector_tab')
```

### **Column-Selective Loading**

```python
# Load only needed columns
COLUMN_GROUPS = {
    'income_statement': ['symbol', 'net_revenue', 'gross_profit', ...],
    'balance_sheet': ['symbol', 'total_assets', 'total_equity', ...],
}
df = load_data(columns=COLUMN_GROUPS['income_statement'])
```

---

## Key Features

### **1. Cross-Page Ticker Sync**

When user selects ticker in Fundamental pages:
```python
set_synced_ticker("ACB", "BANK", "Ngân hàng")
```

Technical/Forecast pages can auto-select same ticker:
```python
ticker = get_synced_ticker() or default_ticker
```

### **2. Persistent Tabs**

Tabs don't reset when widgets change:
```python
render_persistent_tabs(["Charts", "Tables"], "company_active_tab")
```

### **3. Master Symbols Filter**

Only shows liquid tickers (>1B VND/day):
```python
# 315 liquid symbols filtered from 457 total
master_symbols = SymbolLoader().get_all_symbols()
```

### **4. Outlier Filtering**

Automatic clipping of extreme values:
```python
OUTLIERS_DEFAULT = {
    'pe_ratio': (0, 100),
    'pb_ratio': (0, 10),
    'ev_ebitda_ratio': (0, 100),
}
```

### **5. Responsive Charts**

All charts use consistent layout template:
- Height: 280-600px (depending on importance)
- Font: IBM Plex Sans (data), Space Grotesk (titles)
- Colors: Brand palette (purple/cyan/amber)
- Grid: Subtle (opacity 0.08)
- Legend: Horizontal, bottom

---

## Integration Points

### **With Processors**

Services load data generated by processors:
```
PROCESSORS/fundamental/calculators/company_calculator.py
  → DATA/processed/fundamental/company/company_financial_metrics.parquet
  → WEBAPP/services/company_service.py
```

### **With Registries**

Services use registries for metadata:
```python
from config.registries import SectorRegistry
sector_reg = SectorRegistry()
peers = sector_reg.get_peers("ACB")
```

### **With Schema Registry**

Formatting uses schema definitions:
```python
from config.schema_registry import SchemaRegistry
schema_reg = SchemaRegistry()
formatted = schema_reg.format_price(25750.5)  # "25,750.50đ"
```

---

## Dependencies

**Key Libraries:**
- `streamlit`: Web framework
- `pandas`: Data manipulation
- `plotly`: Interactive charts
- `duckdb`: Fast parquet reads
- `numpy`: Numerical computing

**Streamlit Config:**
- Theme: Custom dark mode
- Layout: Wide
- Sidebar: Collapsed (chart-first)

---

## Known Issues & TODO

### **Performance (from WEBAPP_SPEC.md)**

**Phase 1: Critical Fixes (Immediate)**
- [x] Dropdown backgrounds (fixed in styles.py)
- [x] Chart overflow in columns (fixed)
- [ ] Forecast module caching (P0 - critical)
- [ ] Add cache to core data loading functions

**Phase 2: Enhancement**
- [ ] Metric cards: Add sparklines
- [ ] Tables: Implement sticky headers
- [ ] Tooltips: Improve hover tooltips

**Phase 3: Advanced**
- [ ] Animations: Smooth transitions
- [ ] Mobile responsive
- [ ] Accessibility improvements

### **Per-Page Issues**

**Company Dashboard:**
- MA4 line can be NaN at start
- Cash Flow chart crowded with many traces
- Missing industry average comparison

**Bank Dashboard:**
- Too many metrics can overwhelm
- Need preset views (Key Metrics, Growth, Quality)

**Sector Dashboard:**
- Candlestick chart confusing for negative PE
- Missing date range selector

**Technical Dashboard:**
- RSI/MACD subplots too small
- Missing drawing tools
- No pattern recognition alerts

---

## Code Quality

### **Strengths**
- Clear separation of concerns (services/components/pages)
- Consistent design system (Crypto Terminal theme)
- Comprehensive documentation (WEBAPP_SPEC.md)
- Registry integration (no hardcoding)
- Caching strategy (performance optimization)

### **Areas for Improvement**
- Some long files (bank_dashboard.py: 682 lines, sector_dashboard.py: 827 lines)
- Duplicate chart code (could abstract to common functions)
- Missing error handling in some services
- No automated tests for UI

---

## Summary

The WEBAPP is a **well-architected Streamlit application** with:

- **7 dashboard pages** serving different analysis types
- **Service-oriented architecture** for data access
- **Component-based UI** with reusable charts/tables/metrics
- **Unified theming system** (Crypto Terminal Dark Mode)
- **Performance optimizations** (caching, lazy loading, column filtering)
- **133 Python files** organized by purpose
- **Integration with processors** and registries

**Key Design Principles:**
1. **Single source of truth** (registries, not hardcoding)
2. **Reusable components** (charts, tables, metrics)
3. **Consistent theming** (purple/cyan/amber palette)
4. **Performance first** (caching, DuckDB, lazy loading)
5. **User experience** (persistent tabs, cross-page sync)

**Active Plan:** Performance optimization (Phase 1: Critical fixes complete, Phase 2: Enhancement in progress)

---

**Report End**
