# WEBAPP Specification Document

> **Version:** 1.0
> **Last Updated:** 2025-12-16
> **Purpose:** Comprehensive guide for UI/UX optimization, data verification, and chart customization

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Navigation & Pages](#2-navigation--pages)
3. [Design System](#3-design-system)
4. [Page Specifications](#4-page-specifications)
   - [4.1 Company Dashboard](#41-company-dashboard)
   - [4.2 Bank Dashboard](#42-bank-dashboard)
   - [4.3 Security Dashboard](#43-security-dashboard)
   - [4.4 Sector Dashboard](#44-sector-dashboard)
   - [4.5 Valuation Dashboard](#45-valuation-dashboard)
   - [4.6 Technical Dashboard](#46-technical-dashboard)
5. [Services Layer](#5-services-layer)
6. [Components Library](#6-components-library)
7. [Common Issues & Fixes](#7-common-issues--fixes)
8. [UI/UX Optimization Checklist](#8-uiux-optimization-checklist)

---

## 1. Architecture Overview

```
WEBAPP/
├── main_app.py                 # Entry point - st.navigation()
├── pages/                      # 6 dashboard pages
│   ├── company/
│   ├── bank/
│   ├── security/
│   ├── sector/
│   ├── valuation/
│   └── technical/
├── services/                   # Data loading layer (15 files)
├── core/                       # Config, styles, theme (17 files)
├── components/                 # Reusable UI components (17 files)
├── domains/                    # Domain-specific data loaders
├── features/                   # Business logic (signals, scoring)
└── ai/                         # LLM integration
```

### Key Files

| File | Purpose |
|------|---------|
| `main_app.py` | Navigation router with st.navigation() |
| `core/styles.py` | Unified CSS/styling system |
| `core/theme.py` | Brand colors & typography |
| `services/*_service.py` | Data loading from parquet |

---

## 2. Navigation & Pages

### Main Navigation Structure (main_app.py:79-82)

```python
pg = st.navigation({
    "Fundamental": [company_page, bank_page, security_page],
    "Analysis": [sector_page, valuation_page, technical_page]
})
```

| Section | Pages | Icons |
|---------|-------|-------|
| **Fundamental** | Company, Bank, Security | 🏢 🏦 📈 |
| **Analysis** | Sector, Valuation, Technical | 🌐 💰 📉 |

---

## 3. Design System

### Brand Colors (core/theme.py)

```python
BRAND = {
    'blue': '#295CA9',      # Primary Blue (R:41 G:92 B:169)
    'teal': '#009B87',      # Accent Teal - PRIMARY CHART COLOR
    'gold': '#FFC132',      # Warning Gold
}
```

### Semantic Colors

| Purpose | Color | Hex |
|---------|-------|-----|
| Positive/Success | Teal | `#009B87` |
| Negative/Loss | Red | `#E53E3E` |
| Warning/Fair | Gold | `#FFC132` |
| Info | Blue | `#295CA9` |
| Neutral | Gray | `#718096` |

### Chart Color Palette (core/styles.py:1009-1035)

```python
CHART_COLORS = {
    'primary': '#009B87',       # Brand Teal
    'secondary': '#295CA9',     # Brand Blue
    'tertiary': '#FFC132',      # Brand Gold
    'quaternary': '#00C9AD',    # Teal Light
    'quinary': '#4A7BC8',       # Blue Light
    'positive': '#009B87',
    'negative': '#E53E3E',
}

BAR_COLORS = [
    '#009B87', '#295CA9', '#FFC132', '#00C9AD',
    '#4A7BC8', '#FFD666', '#007A6B', '#1E4580'
]
```

### Typography

| Type | Font | Usage |
|------|------|-------|
| Display | Geist | Headlines, titles |
| Body | IBM Plex Sans | General text |
| Mono | IBM Plex Mono | Data, numbers, tables |

### Theme: Midnight Terminal

- **Background**: Deep navy gradient (`#04080F` → `#0A1118` → `#101820`)
- **Surface**: `#101820`
- **Elevated**: `#182028`
- **Text**: High contrast whites/silvers

---

## 4. Page Specifications

---

### 4.1 Company Dashboard

**File:** `pages/company/company_dashboard.py` (532 lines)

#### Data Source

```
DATA/processed/fundamental/company/company_financial_metrics.parquet
```

#### Service

```python
from WEBAPP.services.company_service import CompanyService
service = CompanyService()
df = service.get_financial_data(ticker, period, limit=100)
```

#### Sidebar Filters

| Filter | Type | Options | Default |
|--------|------|---------|---------|
| Company | `selectbox` | All company tickers | First ticker |
| Period | `selectbox` | Quarterly, Yearly | Quarterly |
| Number of periods | `slider` | 4-20 | 12 |
| Refresh | `button` | - | - |

#### Metric Cards (4 KPIs)

| Position | Metric | Formula | Delta |
|----------|--------|---------|-------|
| 1 | Net Revenue | `latest['net_revenue'] / 1e9` | % change vs previous |
| 2 | Net Profit | `latest['npatmi'] / 1e9` | % change vs previous |
| 3 | ROE | `latest['roe']` | Point change |
| 4 | D/E Ratio | `latest['debt_to_equity']` | Change (delta_color=inverse) |

#### Tabs Structure

```
📈 Charts
├── Income Statement (4 bar charts with MA4 YoY lines)
│   ├── Revenue (net_revenue)
│   ├── Gross Profit (gross_profit)
│   ├── EBITDA (ebitda)
│   └── NPATMI (npatmi)
├── Profitability Margins (4 bar charts with MA4 lines)
│   ├── Gross Margin (gross_profit_margin)
│   ├── EBIT Margin (ebit_margin)
│   ├── EBITDA Margin (ebitda_margin)
│   └── Net Margin (net_margin)
├── ROE/ROA Trend (dual-axis line chart)
├── Balance Sheet Structure (stacked bar)
├── Cash Flow Analysis (grouped bar + FCF/FCFE lines)
└── Investment Ratios (if available)
    ├── Depreciation Rate
    └── CIP Rate

📋 Tables
├── Income Statement (pivot table)
├── Balance Sheet (pivot table)
└── Cash Flow (pivot table)
```

#### Chart Types & Formulas

**1. Income Statement Bar Charts (lines 226-277)**
```python
# Bar chart with secondary y-axis for MA4 YoY Growth
fig = make_subplots(specs=[[{"secondary_y": True}]])

# MA4 YoY Growth Formula:
ttm_current = series.rolling(window=4, min_periods=4).sum()
ttm_prev = ttm_current.shift(4)
ma4_yoy = (ttm_current / ttm_prev - 1) * 100.0
```

**2. Profitability Margins (lines 285-347)**
```python
# Simple 4-quarter moving average
ma4 = series.rolling(window=4, min_periods=1).mean()
```

**3. ROE/ROA Dual-Axis (lines 350-385)**
```python
fig = make_subplots(specs=[[{"secondary_y": True}]])
# ROE on primary y-axis with fill='tozeroy'
# ROA on secondary y-axis with dash='dot'
```

**4. Balance Sheet Stacked Bar (lines 389-410)**
```python
fig.add_trace(go.Bar(..., marker_color=CHART_COLORS['tertiary']))  # Liabilities
fig.add_trace(go.Bar(..., marker_color=CHART_COLORS['primary']))   # Equity
layout['barmode'] = 'stack'
```

**5. Cash Flow Grouped Bar + Lines (lines 413-456)**
```python
# Operating CF: CHART_COLORS['positive']
# Investment CF: CHART_COLORS['negative']
# Financing CF: BAR_COLORS[4]
# FCF line: CHART_COLORS['secondary']
# FCFE line: CHART_COLORS['tertiary'], dash='dash'
layout['barmode'] = 'group'
```

#### Data Columns Used

**Income Statement:**
- `net_revenue`, `gross_profit`, `ebit`, `ebitda`, `npatmi`
- `sga`, `net_finance_income`
- `gross_profit_margin`, `ebit_margin`, `ebitda_margin`, `net_margin`

**Balance Sheet:**
- `total_assets`, `total_liabilities`, `total_equity`
- `depreciation_rate`, `cip_rate`

**Cash Flow:**
- `operating_cf`, `investment_cf`, `financing_cf`
- `fcf`, `fcfe`

**Ratios:**
- `roe`, `roa`, `debt_to_equity`

---

### 4.2 Bank Dashboard

**File:** `pages/bank/bank_dashboard.py` (682 lines)

#### Data Source

```
DATA/processed/fundamental/bank/bank_financial_metrics.parquet
```

#### Service

```python
from WEBAPP.services.bank_service import BankService
service = BankService()
df = service.get_financial_data(ticker, period, limit=100)
```

#### Available Metrics (18 metrics)

```python
AVAILABLE_METRICS = {
    # Key Performance (7)
    "NIM": "nim_q",
    "CIR": "cir",
    "NPL": "npl_ratio",
    "ROE": "roea_ttm",
    "ROA": "roaa_ttm",
    "LLCR": "llcr",
    "Provision/Loan": "provision_to_loan",

    # Growth (5)
    "Credit Growth": "credit_growth_ytd",
    "Deposit Growth": "deposit_growth_ytd",
    "Loan Growth": "loan_growth_ytd",
    "NII Growth": "nii_growth_yoy",
    "NPATMI Growth": "npatmi_growth_yoy",

    # Other (6)
    "CASA": "casa_ratio",
    "LDR": "ldr_pure",
    "Asset Yield": "asset_yield_q",
    "Funding Cost": "funding_cost_q",
    "Group 2": "debt_group2_ratio",
    "Credit Cost": "credit_cost",
}
```

#### Metric Cards (4 KPIs)

| Position | Metric | Column | Format |
|----------|--------|--------|--------|
| 1 | Net Interest Income | `nii` | Billions (B) |
| 2 | NIM (Quarterly) | `nim_q` | Percent (%) |
| 3 | ROAE (TTM) | `roea_ttm` | Percent (%) |
| 4 | NPL Ratio | `npl_ratio` | Percent (%) - inverse |

#### Tabs Structure

```
📊 Charts
├── Selected Metrics Grid (dynamic, 2 per row)
│   └── Line charts for trends (NIM, ROE, ROA, Growth metrics)
│   └── Bar charts for others
└── Income Statement (5 bar charts with MA4 YoY)
    ├── NII (nii)
    ├── TOI (toi)
    ├── PPOP (ppop)
    ├── PBT (pbt)
    └── NPATMI (npatmi)

📋 Tables
├── Size (total_assets, total_credit, etc.)
├── Income Statement (nii, toi, noii, opex, etc.)
├── Growth (YoY and YTD metrics)
├── Asset Quality (npl_ratio, llcr, etc.)
└── Efficiency (nim_q, cir, casa_ratio, etc.)
```

#### Quick Select Buttons

```python
# 4 preset configurations
"Key Performance": ["NIM", "CIR", "NPL", "ROE", "ROA", "LLCR", "Provision/Loan"]
"Growth Focus": ["Credit Growth", "Deposit Growth", "Loan Growth", "NII Growth", "NPATMI Growth", "ROE", "NIM", "NPL"]
"All Metrics": list(AVAILABLE_METRICS.keys())
"Reset Default": DEFAULT_METRICS
```

#### Reference Lines in Charts (lines 228-241)

```python
# CIR target line
fig.add_hline(y=40, line_dash="dash", annotation_text="Target 40%")

# NPL warning line
fig.add_hline(y=3, annotation_text="Warning 3%")

# LLCR minimum line
fig.add_hline(y=100, annotation_text="Min 100%")

# LDR limit line
fig.add_hline(y=85, annotation_text="SBV Limit 85%")
```

---

### 4.3 Security Dashboard

**File:** `pages/security/security_dashboard.py` (451 lines)

#### Data Source

```
DATA/processed/fundamental/security/security_financial_metrics.parquet
```

#### Metric Cards (4 KPIs)

| Position | Metric | Column | Format |
|----------|--------|--------|--------|
| 1 | Total Revenue | `total_revenue` | Billions |
| 2 | Net Profit | `net_profit` | Billions |
| 3 | ROAE (TTM) | `roae_ttm` | Percent |
| 4 | Leverage | `leverage` | Ratio (x) |

#### Tabs Structure

```
📊 Charts
├── Row 1 (2 columns)
│   ├── Revenue Mix (stacked bar)
│   │   └── income_fvtpl, income_htm, income_afs, income_loans, brokerage_fee
│   └── ROAE & ROAA (dual line chart)
├── Row 2 (2 columns)
│   ├── Portfolio Composition (pie chart)
│   │   └── fvtpl, htm, afs, margin_loans
│   └── Profit Margins (line chart)
│       └── gross_profit_margin, profit_margin
├── Row 3 (2 columns)
│   ├── CIR (bar with reference line y=50)
│   └── Leverage Trend (line with fill)

📋 Tables
├── Income Statement
│   └── total_revenue, brokerage_fee, investment_revenue, gross_profit, opex, net_profit
├── Balance Sheet Summary
│   └── total_assets, fvtpl, htm, afs, margin_loans, total_equity
└── Key Financial Ratios
    └── gross_profit_margin, profit_margin, roae_ttm, roaa_ttm, leverage, cir
```

---

### 4.4 Sector Dashboard

**File:** `pages/sector/sector_dashboard.py` (827 lines)

#### Data Source

```
DATA/processed/valuation/vnindex/vnindex_valuation_with_sectors.parquet
DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet (fallback)
```

#### Service

```python
from WEBAPP.services.sector_service import SectorService
service = SectorService()
```

#### Sidebar Filters

| Filter | Options | Default |
|--------|---------|---------|
| Primary Metric | PE TTM, PB | PE TTM |
| History (Days) | 30-2000 | 1000 |

#### Metric Cards (4 KPIs)

| Position | Metric | Source |
|----------|--------|--------|
| 1 | Lowest PE Sector | `overview['top_sector']` |
| 2 | VNINDEX PE | `overview['market_pe']` |
| 3 | VNINDEX PB | `overview['market_pb']` |
| 4 | Sectors / Tickers | `overview['sector_count']` / `ticker_count` |

#### Tabs Structure

```
🕯️ All Sectors Distribution
├── Radio: "📊 Sectors" | "📈 Market Indices"
├── Sectors: Candlestick distribution chart
│   └── Whiskers: P5-P95
│   └── Body: P25-P75
│   └── Current value dot (colored by percentile)
│   └── Distribution Statistics table
└── Market Indices: Combined line chart
    └── VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX

📈 Individual Analysis
├── Scope selector: Market Indices | Sectors
├── Combined view (all 3 indices) OR Single scope
└── Line chart with statistical bands
    ├── ±2 SD band (blue, light)
    ├── ±1 SD band (teal, light)
    ├── Main line (teal)
    ├── Median line (gold)
    ├── Mean line (blue, dashed)
    └── ±1σ, ±2σ reference lines

📋 Data
├── Sector Valuation Overview table
└── Sector Composition table
```

#### Color Coding (Valuation Assessment)

```python
ASSESSMENT_COLORS = {
    'undervalued': '#009B87',   # < P25
    'fair': '#FFC132',          # P25-P75
    'expensive': '#E53E3E',     # > P75
}
```

#### Band Colors (Individual Analysis)

```python
BAND_COLORS = {
    'main_line': '#009B87',                 # Brand Teal
    'median_line': '#FFC132',               # Brand Gold
    'mean_line': '#295CA9',                 # Brand Blue
    'band_1sd': 'rgba(0, 155, 135, 0.15)',  # Teal band
    'band_2sd': 'rgba(41, 92, 169, 0.1)',   # Blue band
}
```

---

### 4.5 Valuation Dashboard

**File:** `pages/valuation/valuation_dashboard.py` (980 lines)

#### Data Source

Multiple parquet files via ValuationService

#### Sidebar Filters

| Filter | Options | Default |
|--------|---------|---------|
| Metric | P/E, P/B, P/S, EV/EBITDA | P/E |
| Industry | "Tất cả" + all industries | "Ngân hàng" |
| Ticker | Filtered by industry | First available |
| Start Year | 2018-2024 | 2020 |

#### Tabs Structure

```
📊 Sector Comparison
├── Candlestick chart (same as Sector dashboard)
├── Premium Statistics Table (custom HTML)
│   └── Ticker, Current, Median, Percentile bar, Status badge
└── Download Excel button

📈 Individual Analysis
├── Large trend chart (600px height)
│   ├── ±2 SD band
│   ├── ±1 SD band
│   ├── Main metric line
│   ├── Mean line (white, solid)
│   ├── ±1 SD lines (red/green, dashed)
│   ├── ±2 SD lines (lighter, dotted)
│   └── Current value marker (gold)
├── KPI Cards + Histogram row
│   ├── KPI: Current, Mean, Z-Score, ±1 SD
│   └── Histogram with current/mean lines
└── Download Excel button
```

#### Status Classifications

```python
status_colors = {
    "Very Cheap": "#00D4AA",    # < P10
    "Cheap": "#7FFFD4",         # P10-P25
    "Fair": "#FFD666",          # P25-P75
    "Expensive": "#FF9F43",     # P75-P90
    "Very Expensive": "#FF6B6B" # > P90
}
```

---

### 4.6 Technical Dashboard

**File:** `pages/technical/technical_dashboard.py` (559 lines)

#### Data Source

```
DATA/processed/technical/basic_data.parquet
```

#### Sidebar Filters

| Filter | Options | Default |
|--------|---------|---------|
| Stock | All tickers | First ticker |
| History (Days) | 30-500 | 180 |
| Show Volume | Checkbox | True |
| Show Bollinger Bands | Checkbox | False |

#### Metric Cards (5 KPIs)

| Position | Metric | Column | Interpretation |
|----------|--------|--------|----------------|
| 1 | Close Price | `close` | % change |
| 2 | RSI (14) | `rsi_14` | 🔴/>70, 🟢/<30, ⚪/else |
| 3 | Price vs SMA50 | `price_vs_sma50` | 📈/>0, 📉/<0 |
| 4 | ADX (14) | `adx_14` | 💪/>25, 😴/<25 |
| 5 | MACD | `macd` vs `macd_signal` | 🟢/🔴 |

#### Tabs Structure

```
📊 Price & Volume
├── OHLC Candlestick chart
│   ├── Candlestick (green: #00D4AA, red: #FF6B6B)
│   ├── SMA 20 (#5B8DEF)
│   ├── SMA 50 (#FFD666)
│   ├── SMA 200 (#A78BFA)
│   └── Bollinger Bands (optional, yellow)
├── Volume bars (colored by direction)
├── MA Signal Summary table
└── Trend Analysis table

📈 Oscillators
├── RSI (14)
│   ├── Line with fill
│   ├── Overbought zone (70-100, red)
│   └── Oversold zone (0-30, green)
├── MACD
│   ├── Histogram (green/red)
│   ├── MACD line (#5B8DEF)
│   └── Signal line (#FFD666)
├── Stochastic Oscillator (%K, %D)
└── CCI (20)

📋 Data
├── Price & Moving Averages table
├── Volatility table
├── Momentum Indicators table
└── Volume Indicators table
```

#### Technical Indicators Available

| Category | Indicators |
|----------|------------|
| **Moving Averages** | sma_20, sma_50, sma_100, sma_200, ema_20, ema_50 |
| **Momentum** | rsi_14, macd, macd_signal, macd_hist, adx_14, stoch_k, stoch_d, cci_20, mfi_14 |
| **Volatility** | atr_14, bb_upper, bb_middle, bb_lower, bb_width |
| **Volume** | volume, obv, cmf_20 |
| **Price** | price_vs_sma50 |

---

## 5. Services Layer

### Service Pattern

All services follow the same pattern:

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

### Data Path Mappings

| Service | Data Path |
|---------|-----------|
| CompanyService | `DATA/processed/fundamental/company/` |
| BankService | `DATA/processed/fundamental/bank/` |
| SecurityService | `DATA/processed/fundamental/security/` |
| SectorService | `DATA/processed/valuation/vnindex/` |
| ValuationService | `DATA/processed/valuation/` |
| TechnicalService | `DATA/processed/technical/` |

---

## 6. Components Library

### Charts (components/charts/)

| Component | File | Usage |
|-----------|------|-------|
| PlotlyBuilders | `plotly_builders.py` | Standardized chart builders |
| IncomeStatementChart | `income_statement_chart.py` | Income statement visualization |

### Tables (components/tables/)

| Component | File | Usage |
|-----------|------|-------|
| FinancialTables | `financial_tables.py` | Pivot tables for financial statements |

### Inputs (components/inputs/)

| Component | File | Usage |
|-----------|------|-------|
| SymbolSelector | `symbol_selector.py` | Ticker selection widget |
| DateRange | `date_range.py` | Date range picker |

### Metrics (components/metrics/)

| Component | File | Usage |
|-----------|------|-------|
| MetricCards | `metric_cards.py` | KPI card rendering |

---

## 7. Common Issues & Fixes

### Issue 1: White Dropdown Background

**Fix:** Already applied in `core/styles.py:629-706`

```css
[data-baseweb="popover"] { background: #101820 !important; }
[data-baseweb="menu"] li { background: #101820 !important; }
```

### Issue 2: Chart Overflow in Columns

**Fix:** Applied in `core/styles.py:543-565`

```css
.stPlotlyChart { width: 100% !important; max-width: 100% !important; }
[data-testid="column"] .stPlotlyChart { min-width: 0; }
```

### Issue 3: X-axis Labels Overlap

**Fix:** In `get_chart_layout()`:

```python
'xaxis': {
    'tickangle': -45,
    'automargin': True,
    'nticks': 10,
}
```

### Issue 4: DataFrame Dark Styling

**Fix:** Use `render_styled_table()` instead of `st.dataframe()`:

```python
from WEBAPP.core.styles import render_styled_table, get_table_style

st.markdown(get_table_style(), unsafe_allow_html=True)
st.markdown(render_styled_table(df), unsafe_allow_html=True)
```

---

## 8. UI/UX Optimization Checklist

### Global

- [ ] All dropdowns have dark background
- [ ] All charts responsive in columns
- [ ] Consistent color usage (brand colors only)
- [ ] Loading spinners during data fetch
- [ ] Error messages with actionable instructions

### Per Page

- [ ] Metric cards show meaningful deltas
- [ ] Charts have clear titles and labels
- [ ] Tables have proper column alignment
- [ ] Download buttons functional
- [ ] Footer shows data source and count

### Charts

- [ ] Consistent height (280-400px for regular, 500-600px for main)
- [ ] Legend position: horizontal, top or bottom
- [ ] Hover labels have dark background
- [ ] Grid lines subtle (opacity 0.08)
- [ ] Reference lines for thresholds where applicable

### Data Validation

- [ ] Handle NaN values gracefully
- [ ] Show warnings for missing data
- [ ] Validate data ranges (e.g., PE > 0)
- [ ] Cache data with TTL (3600s default)

---

## Quick Reference: Chart Heights

| Chart Type | Height |
|------------|--------|
| Small (grid cell) | 280px |
| Medium | 300-400px |
| Large (main focus) | 500-600px |
| With volume subplot | 550px |

## Quick Reference: Layout Patterns

| Pattern | Code |
|---------|------|
| 2 columns | `st.columns(2)` |
| 4 metric cards | `st.columns(4)` |
| Tabs | `st.tabs(["📊 Charts", "📋 Tables"])` |
| Nested tabs | Inside tab, use another `st.tabs()` |

---

## 9. Using Claude Frontend Design Skill

### Kích hoạt Skill

Khi cần tối ưu UI/UX, sử dụng Claude's frontend-design skill:

```
/skill frontend-design
```

### Workflow Tối ưu UI/UX

1. **Capture Screenshot**
   - Chụp screenshot trang hiện tại
   - Mô tả vấn đề cần cải thiện

2. **Request Analysis**
   ```
   Analyze this Streamlit dashboard screenshot and suggest:
   - Color improvements following brand guidelines
   - Layout optimization for better data visualization
   - Component spacing and alignment fixes
   ```

3. **Generate Code**
   - Skill sẽ tạo code CSS/HTML
   - Review và integrate vào `core/styles.py`

---

## 10. Design Prompt Templates

Sử dụng các prompts sau với frontend-design skill để tạo nhanh design mẫu.

### Template 1: High-End Financial Editorial

```
Redesign this Stock Valuation Dashboard using a 'High-End Financial Editorial' aesthetic.

Core Philosophy: Trust, Precision, and Elegance. Think The Financial Times meets a luxury watch interface.

Visual Rules:

Typography:
- Use Serif font (Playfair Display/Merriweather) for Ticker Symbol and KPI headers
- Pair with Monospace font (JetBrains Mono) for all data points and axis labels

Color Palette:
- Background: 'Deep Charcoal' or 'Rich Navy'
- Accent: Champagne Gold (#D4AF37) for Mean line
- Primary: Muted Teal (#4A7C7E) for P/E line
- Avoid neon green/red

Chart Styling:
- Grid lines extremely faint (dotted)
- SD bands use hatched patterns (diagonal lines) instead of opacity fills
- Look like a printed technical lithograph

Layout:
- Generous negative space
- Tabs look like physical paper tabs or minimalist underscores

Technical constraints: Implementable via Custom CSS in Streamlit and Plotly configuration.
```

### Template 2: Bloomberg Terminal

```
Redesign this dashboard in the style of a Bloomberg Terminal.

Visual Rules:

Typography:
- All text in monospace (IBM Plex Mono)
- Uppercase labels
- Dense information layout

Color Palette:
- Background: Pure black (#000000)
- Primary text: Amber (#FFB000)
- Secondary text: White
- Positive: Green (#00FF00)
- Negative: Red (#FF0000)
- Accent: Cyan (#00FFFF)

Layout:
- No rounded corners (sharp edges only)
- Dense grid layout
- Minimal padding
- Status bar at bottom

Charts:
- No fill areas (lines only)
- Thin grid lines
- Crosshair cursor
```

### Template 3: Minimalist Light Mode

```
Redesign this dashboard with a minimalist light mode aesthetic.

Visual Rules:

Typography:
- Clean sans-serif (Inter, SF Pro)
- Light font weights
- Subtle color hierarchy

Color Palette:
- Background: Off-white (#FAFAFA)
- Surface: Pure white (#FFFFFF)
- Text: Dark gray (#333333)
- Accent: Single brand color (#009B87)
- Charts: Grayscale with one accent

Layout:
- Lots of whitespace
- Card-based design with subtle shadows
- Rounded corners (12px)
- Clear visual hierarchy

Charts:
- Minimal grid
- Soft colors
- Subtle animations
```

### Template 4: Japanese Minimalism

```
Redesign this dashboard inspired by Japanese minimalism and Muji aesthetics.

Visual Rules:

Typography:
- Clean, neutral fonts
- Moderate spacing
- No bold weights (use size hierarchy)

Color Palette:
- Background: Warm off-white (#FAF8F5)
- Surface: White with warm undertone
- Text: Soft black (#2C2C2C)
- Accent: Natural tones (terracotta, sage, stone)
- No bright/saturated colors

Layout:
- Asymmetric balance
- Generous breathing room
- Natural proportions
- Hidden complexity

Charts:
- Brush stroke style lines
- Muted color fills
- Ink wash effect for backgrounds
```

### Template 5: Cyberpunk/Neon

```
Redesign this dashboard with a cyberpunk/neon aesthetic.

Visual Rules:

Typography:
- Tech/futuristic fonts
- Glowing text effects
- All caps headers

Color Palette:
- Background: Deep dark blue (#0D0221)
- Primary: Neon pink (#FF00FF)
- Secondary: Electric cyan (#00FFFF)
- Accent: Neon green (#39FF14)
- Glow effects on all elements

Layout:
- Skewed/angled elements
- Holographic card effects
- Scanlines overlay
- Animated borders

Charts:
- Glowing lines
- Gradient fills
- Particle effects on data points
```

---

## 11. UI/UX Improvement Plan

### Phase 1: Critical Fixes (Immediate)

- [ ] **Dropdown Background**: Verify all dropdowns have dark background
- [ ] **Chart Overflow**: Fix charts overflowing in columns
- [ ] **Loading States**: Add skeleton loading for charts

### Phase 2: Enhancement (This Week)

- [ ] **Metric Cards**: Add sparklines mini charts
- [ ] **Tables**: Implement sticky headers for large tables
- [ ] **Tooltips**: Improve hover tooltips with context

### Phase 3: Advanced (Next Week)

- [ ] **Animations**: Smooth transitions between tabs
- [ ] **Mobile Responsive**: Test and fix on tablet
- [ ] **Accessibility**: Improve color contrast for text

### Priority Issues Per Page

#### Company Dashboard
1. ⚠️ MA4 line can be NaN at start - need interpolate
2. ⚠️ Cash Flow chart can be crowded with many traces
3. 💡 Add comparison with industry average

#### Bank Dashboard
1. ⚠️ Too many metrics can overwhelm user
2. 💡 Add preset views (Key Metrics, Growth, Quality)
3. 💡 Reference lines need legend

#### Sector Dashboard
1. ⚠️ Candlestick chart confusing for negative PE
2. 💡 Add sector icons
3. 💡 Add date range selector for historical

#### Valuation Dashboard
1. ⚠️ Custom HTML table may not be responsive
2. 💡 Add comparison mode (2 tickers side by side)
3. 💡 Export to PDF

#### Technical Dashboard
1. ⚠️ RSI/MACD subplots may be too small
2. 💡 Add drawing tools
3. 💡 Add pattern recognition alerts

---

## 12. Quick Start: Design Iteration Workflow

### Step 1: Capture Current State
```bash
# Take screenshot of current page
streamlit run WEBAPP/main_app.py
# Navigate to page, screenshot manually
```

### Step 2: Use Frontend Design Skill
```
/skill frontend-design

Prompt: [Paste one of the templates above]
Attach: [Screenshot of current page]
```

### Step 3: Review Generated Code
- CSS changes → `core/styles.py`
- Plotly config → `get_chart_layout()`
- Color changes → `core/theme.py`

### Step 4: Test & Iterate
```bash
# Hot reload should show changes
# If not, restart streamlit
pkill -f streamlit
streamlit run WEBAPP/main_app.py
```

---

*End of WEBAPP Specification Document*
