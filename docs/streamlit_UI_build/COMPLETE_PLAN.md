# 🎨 Streamlit UI/UX Complete Redesign Plan

**Version:** 3.0 FINAL
**Date:** 2025-12-12
**Author:** AI Assistant
**Status:** ✅ Ready for Implementation

> **Consolidated documentation** - Tất cả thông tin trong 1 file duy nhất

---

## 📑 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Requirements & Scope](#2-requirements--scope)
3. [Data Architecture](#3-data-architecture)
4. [Page Structure](#4-page-structure)
5. [Component Library](#5-component-library)
6. [Implementation Guide](#6-implementation-guide)
7. [Code Examples](#7-code-examples)
8. [Timeline & Phases](#8-timeline--phases)
9. [Testing & Deployment](#9-testing--deployment)
10. [Quick Reference](#10-quick-reference)

---

## 1. Executive Summary

### 1.1 Vision

Transform Streamlit dashboard từ fragmented PyEcharts-based UI sang **modern, unified Plotly-powered analytics platform** với:
- 100% Plotly charts (eliminate PyEcharts)
- Parquet-only data loading (no raw CSV/Excel processing)
- Component library (zero duplication)
- **2-level analysis:** Individual stocks + Sector-level
- Modern UI/UX (responsive, fast, intuitive)

### 1.2 Key Metrics

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Page Load Time | 4-6s | <2s | 67% faster |
| Data Query Count | 5-10x | 1-2x | 80% reduction |
| Code Duplication | 300+ LOC | 0 LOC | 100% eliminated |
| Chart Library | Mixed | 100% Plotly | Standardized |
| Analysis Levels | 1 (individual) | 2 (individual + sector) | NEW feature |

### 1.3 Deliverables

- **7 pages** (Company, Bank, Securities, Valuation, TA, Forecasts, News)
- **13 reusable components** (charts, navigation, inputs, display)
- **1 demo page** (working example)
- **Complete documentation** (this file)

---

## 2. Requirements & Scope

### 2.1 Entity Types

| Entity | Count | Sectors | Status |
|--------|-------|---------|--------|
| **COMPANY** | 390 | 16 sectors (excl. Ngân hàng, Bảo hiểm, DV tài chính) | ✅ Include |
| **BANK** | 24 | Ngân hàng | ✅ Include |
| **SECURITY** | 37 | Dịch vụ tài chính | ✅ Include |
| **INSURANCE** | 6 | Bảo hiểm | ❌ Exclude |

**Total:** 451 tickers across 19 sectors

### 2.2 Sectors (from ticker_details.json)

```
1. Ngân hàng (Banking) - 24 tickers
2. Bất động sản (Real Estate)
3. Dịch vụ tài chính (Financial Services) - Securities
4. Thực phẩm và đồ uống (Food & Beverage)
5. Công nghệ Thông tin (IT)
6. Xây dựng và Vật liệu (Construction & Materials)
7. Tài nguyên Cơ bản (Basic Resources)
8. Hàng & Dịch vụ Công nghiệp (Industrial Goods & Services)
9. Bán lẻ (Retail)
10. Y tế (Healthcare)
11. Viễn thông (Telecom)
12. Truyền thông (Media)
13. Du lịch và Giải trí (Travel & Leisure)
14. Hóa chất (Chemicals)
15. Dầu khí (Oil & Gas)
16. Điện, nước & xăng dầu khí đốt (Utilities)
17. Ô tô và phụ tùng (Auto & Parts)
18. Hàng cá nhân & Gia dụng (Personal & Household Goods)
19. Bảo hiểm (Insurance) - excluded
```

### 2.3 Analysis Levels

#### Level 1: Individual Stock Analysis
- FA: Income Statement, Balance Sheet, Cash Flow, Ratios
- TA: Price chart, MA, RSI, MACD, Bollinger Bands
- Valuation: PE, PB, PS (company), EV/EBITDA (company)

#### Level 2: Sector Analysis (NEW)
- **FA Sector:**
  - Sector average metrics (ROE, margins, growth)
  - Sector distribution (box plots, heatmaps)
  - Top/Bottom performers by sector
- **TA Sector:**
  - Market breadth by sector (% stocks > MA20/50/100)
  - Trading value by sector (dòng tiền)
  - Sector TA signals (aggregated RSI/MACD/MA)
- **Valuation Sector:**
  - Sector PE/PB distribution (candlestick design)
  - Sector median valuation comparison

### 2.4 Key Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **PE/PB Universal** | PE/PB cho tất cả entity types (Company, Bank, Securities) | HIGH |
| **PS & EV/EBITDA** | Chỉ cho Company (không áp dụng Bank/Securities) | MEDIUM |
| **Sector Candlestick** | PE/PB distribution by sector (design từ bank_dashboard.py) | HIGH |
| **TA Screening** | Signal tables (MA, RSI, MACD, Combined score) | HIGH |
| **Sector TA** | Market breadth, trading value by sector | HIGH |
| **Commodity & Macro** | Gold, Oil, USD/VND daily tracking | MEDIUM |

---

## 3. Data Architecture

### 3.1 Data Flow

```
┌─────────────────────────────────────────────┐
│ CONFIGURATION                               │
│ config/metadata/ticker_details.json        │
│ {                                           │
│   "VNM": {                                 │
│     "entity": "COMPANY",                   │
│     "sector": "Thực phẩm và đồ uống"       │
│   }                                        │
│ }                                          │
└────────────────┬────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────┐
│ PROCESSORS (Generate Parquet)              │
│ - fundamental/calculators/*.py             │
│ - valuation/calculators/*.py               │
│ - technical/indicators/*.py                │
└────────────────┬────────────────────────────┘
                 │
                 ↓ Write parquet
┌─────────────────────────────────────────────┐
│ DATA/processed/ (Parquet Files)           │
│ ├── fundamental/                           │
│ │   ├── company/*.parquet                  │
│ │   ├── bank/*.parquet                     │
│ │   └── security/*.parquet                 │
│ ├── valuation/                             │
│ │   ├── pe/*.parquet                       │
│ │   ├── pb/*.parquet                       │
│ │   ├── ev_ebitda/*.parquet                │
│ │   └── ps/*.parquet (NEW)                 │
│ └── technical/                             │
│     ├── basic_data.parquet                 │
│     └── market_breadth_sector.parquet      │
└────────────────┬────────────────────────────┘
                 │
                 ↓ Read parquet
┌─────────────────────────────────────────────┐
│ STREAMLIT PAGES                            │
│ - Individual Analysis (Tab 1-5)            │
│ - Sector Analysis (Tab 6) ← NEW           │
│                                            │
│ Uses:                                      │
│ - ticker_details.json (sector mapping)     │
│ - Parquet files (data)                     │
│ - PlotlyChartBuilder (charts)              │
└─────────────────────────────────────────────┘
```

### 3.2 Parquet Files

#### Fundamental Data
```python
# Company metrics
"DATA/processed/fundamental/company/company_financial_metrics.parquet"
# Columns: symbol, date, quarter, entity_type,
#          net_revenue, cogs, gross_profit, sga_expense, ebit, ebitda,
#          total_assets, total_liabilities, total_equity,
#          operating_cash_flow, free_cash_flow,
#          roe, roa, gross_margin, ebit_margin, net_margin,
#          revenue_growth_yoy, revenue_growth_qoq, ...

# Bank metrics
"DATA/processed/fundamental/bank/bank_financial_metrics.parquet"
# Columns: symbol, date, quarter, entity_type,
#          nii, non_interest_income, provisions,
#          loans, deposits, equity,
#          nim, cir, car, npl_ratio, ldr, ...

# Security metrics
"DATA/processed/fundamental/security/security_financial_metrics.parquet"
# Columns: symbol, date, quarter, entity_type,
#          brokerage_revenue, investment_income,
#          client_deposits, proprietary_investments,
#          roe, roa, revenue_mix, ...
```

#### Valuation Data
```python
# PE ratio (all stocks)
"DATA/processed/valuation/pe/pe_historical_all_symbols_final.parquet"
# Columns: symbol, date, pe_ratio

# PB ratio (all stocks)
"DATA/processed/valuation/pb/pb_historical_all_symbols_final.parquet"
# Columns: symbol, date, pb_ratio

# EV/EBITDA (company only)
"DATA/processed/valuation/ev_ebitda/ev_ebitda_historical.parquet"
# Columns: symbol, date, ev_ebitda

# PS ratio (company only) - NEW
"DATA/processed/valuation/ps/ps_historical.parquet"
# Columns: symbol, date, ps_ratio
```

#### Technical Data
```python
# Basic TA indicators (all stocks)
"DATA/processed/technical/basic_data.parquet"
# Columns: symbol, date, close, volume,
#          ma_20, ma_50, ma_100, ma_200,
#          rsi_14, macd, macd_signal, macd_histogram,
#          bb_upper, bb_middle, bb_lower, atr_14

# Market breadth (global)
"DATA/processed/technical/market_breadth_global.parquet"
# Columns: date, pct_ma20, pct_ma50, pct_ma100, total_stocks

# Market breadth by sector
"DATA/processed/technical/market_breadth/market_breadth_sector.parquet"
# Columns: date, sector, pct_ma20, pct_ma50, pct_ma100,
#          trading_value, trading_value_pct,
#          trading_value_change_5d, trading_value_change_20d
```

#### Commodity & Macro Data
```python
# Gold prices
"DATA/processed/commodity/gold.parquet"
# Columns: date, price, currency

# Oil prices
"DATA/processed/commodity/oil.parquet"
# Columns: date, brent_price, wti_price

# USD/VND exchange rate
"DATA/processed/macro/exchange_rate.parquet"
# Columns: date, usd_vnd

# Interest rates
"DATA/processed/macro/interest_rates.parquet"
# Columns: date, vn_policy_rate, us_fed_rate
```

### 3.3 Data Loading Pattern

```python
import json
import pandas as pd
from WEBAPP.core.data_paths import DataPaths

# 1. Load ticker classification
with open('config/metadata/ticker_details.json') as f:
    ticker_details = json.load(f)

# 2. Get sector stocks
def get_sector_stocks(sector):
    return [
        ticker for ticker, info in ticker_details.items()
        if info['sector'] == sector
    ]

# 3. Load parquet data
@st.cache_data(ttl=3600)
def load_company_data():
    path = DataPaths.fundamental('company')
    return pd.read_parquet(path)

# 4. Filter by sector
sector = "Thực phẩm và đồ uống"
sector_stocks = get_sector_stocks(sector)
company_df = load_company_data()
sector_df = company_df[company_df['symbol'].isin(sector_stocks)]
```

---

## 4. Page Structure

### 4.1 Overview (7 Pages)

| # | Category | Page | File | Individual | Sector |
|---|----------|------|------|------------|--------|
| 1 | FA | Company Analysis | `1_fundamental/company_analysis.py` | ✅ Tab 1-5 | ✅ Tab 6 |
| 2 | FA | Banking Analysis | `1_fundamental/banking_analysis.py` | ✅ Tab 1-5 | ✅ Tab 6 |
| 3 | FA | Securities Analysis | `1_fundamental/securities_analysis.py` | ✅ Tab 1-5 | ✅ Tab 6 |
| 4 | Valuation | Valuation Dashboard | `2_valuation/valuation_dashboard.py` | ✅ Tab 1 | ✅ Tab 2 |
| 5 | TA | Technical Dashboard | `3_technical/technical_dashboard.py` | ✅ Tab 1-2 | ✅ Tab 3-4 |
| 6 | Intelligence | Analyst Forecasts | `4_intelligence/analyst_forecasts.py` | ✅ | - |
| 7 | Intelligence | News & Sentiment | `4_intelligence/news_sentiment.py` | ✅ | - |

### 4.2 Page 1: Company Analysis

**File:** `WEBAPP/pages/1_fundamental/company_analysis.py`

#### Sidebar
```python
# Entity filter (always COMPANY)
st.sidebar.header("⚙️ Settings")

# Sector filter
sector = st.sidebar.selectbox(
    "Sector",
    ["Tất cả"] + [s for s in all_sectors if s not in ["Ngân hàng", "Dịch vụ tài chính", "Bảo hiểm"]]
)

# Symbol selector
symbols = get_sector_stocks(sector) if sector != "Tất cả" else all_company_symbols
symbol = st.sidebar.selectbox("Symbol", symbols)

# Date range
start_date, end_date = date_range_picker()
```

#### Tab 1-5: Individual Stock Analysis
- **Tab 1: Overview** - Key metrics (Revenue, EBITDA, ROE, D/E)
- **Tab 2: Income Statement** - CIS metrics (Revenue, COGS, SGA, EBIT, Net Income)
- **Tab 3: Balance Sheet** - CBS metrics (Assets, Liabilities, Equity)
- **Tab 4: Cash Flow** - CCS metrics (Operating CF, Investing CF, Financing CF, Free CF)
- **Tab 5: Financial Ratios** - ROE, ROA, ROIC, Margins, Turnover ratios

**Charts:**
```python
# Revenue trend (Bar + Line combo)
fig = pcb.bar_line_combo(
    df=data_filtered,
    x_col='quarter',
    bar_col='net_revenue',
    line_col='net_revenue_ma4',
    title=f'Net Revenue Trend - {symbol}'
)

# Profitability margins (Multi-line)
fig = pcb.line_chart(
    df=data_filtered,
    x_col='quarter',
    y_cols=['gross_margin', 'ebit_margin', 'ebitda_margin', 'net_margin'],
    title='Profitability Margins'
)

# Cash flow waterfall
fig = pcb.waterfall_chart(
    categories=['Operating CF', 'Investing CF', 'Financing CF', 'Net Change'],
    values=[operating_cf, investing_cf, financing_cf, net_change],
    title='Cash Flow Waterfall (Latest Quarter)'
)
```

#### Tab 6: Sector Analysis (NEW)

**Charts:**

**1. Sector Average Metrics**
```python
# Calculate sector averages over time
sector_df = company_df[company_df['symbol'].isin(sector_stocks)]

sector_avg = sector_df.groupby('quarter').agg({
    'net_revenue': 'mean',
    'ebitda': 'mean',
    'roe': 'mean',
    'ebitda_margin': 'mean'
}).reset_index()

# Line chart
fig = pcb.line_chart(
    df=sector_avg,
    x_col='quarter',
    y_cols=['roe', 'ebitda_margin'],
    title=f'Sector Average Metrics - {sector}',
    y_axis_title='%'
)
st.plotly_chart(fig, use_container_width=True)
```

**2. Sector Heatmap (Cross-stock comparison)**
```python
# Latest quarter data
latest = sector_df[sector_df['quarter'] == sector_df['quarter'].max()]

# Pivot table: Stocks (rows) x Metrics (columns)
heatmap_data = latest.pivot_table(
    index='symbol',
    values=['roe', 'ebitda_margin', 'revenue_growth_yoy', 'debt_to_equity']
)

# Normalize for better visualization (0-100 scale)
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 100))
heatmap_normalized = pd.DataFrame(
    scaler.fit_transform(heatmap_data),
    index=heatmap_data.index,
    columns=heatmap_data.columns
)

# Heatmap (Red = bad, Green = good)
fig = pcb.heatmap(
    data=heatmap_normalized,
    title=f'Sector Metrics Heatmap - {sector}',
    x_label='Metrics',
    y_label='Company',
    colorscale='RdYlGn'  # Red = low score, Green = high score
)
st.plotly_chart(fig, use_container_width=True)
```

**3. Sector Distribution (Box plots)**
```python
# Distribution of key metrics
fig = go.Figure()

for metric in ['roe', 'ebitda_margin', 'revenue_growth_yoy']:
    fig.add_trace(go.Box(
        y=latest[metric],
        name=metric,
        boxmean='sd'  # Show mean + std dev
    ))

fig.update_layout(
    title=f'Sector Metrics Distribution - {sector}',
    yaxis_title='Value',
    height=400
)
st.plotly_chart(fig, use_container_width=True)
```

**4. Top/Bottom Performers**
```python
# Top 5 by ROE
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔝 Top 5 by ROE")
    top_roe = latest.nlargest(5, 'roe')[['symbol', 'roe', 'ebitda_margin', 'revenue_growth_yoy']]
    st.dataframe(top_roe, hide_index=True)

with col2:
    st.subheader("💚 Lowest Debt/Equity")
    low_de = latest.nsmallest(5, 'debt_to_equity')[['symbol', 'debt_to_equity', 'roe']]
    st.dataframe(low_de, hide_index=True)
```

### 4.3 Page 2: Banking Analysis

**File:** `WEBAPP/pages/1_fundamental/banking_analysis.py`

**Same structure as Company Analysis:**
- Tab 1-5: Individual bank (NII, CAR, NPL, LDR, CIR)
- **Tab 6: Banking Sector Analysis**
  - Sector average NIM, CAR, NPL
  - Bank heatmap (CAR, NPL, LDR, CIR, ROE)
  - Top banks by NIM/ROE
  - Asset quality comparison

**Key Metrics:**
- NIM (Net Interest Margin)
- CAR (Capital Adequacy Ratio)
- NPL (Non-Performing Loan ratio)
- LDR (Loan-to-Deposit Ratio)
- CIR (Cost-to-Income Ratio)

### 4.4 Page 3: Securities Analysis

**File:** `WEBAPP/pages/1_fundamental/securities_analysis.py`

**Same structure:**
- Tab 1-5: Individual security
- **Tab 6: Securities Sector Analysis**
  - Brokerage revenue comparison
  - Market share distribution
  - Revenue mix (Brokerage vs Investment vs Margin)
  - Top performers by ROE

### 4.5 Page 4: Valuation Dashboard

**File:** `WEBAPP/pages/2_valuation/valuation_dashboard.py`

#### Tab 1: Stock Valuation (Individual)

**For ALL stocks (Company + Bank + Securities):**
```python
# PE candlestick (design from bank_dashboard.py)
def create_pe_candlestick(symbol, pe_df):
    ticker_data = pe_df[pe_df['symbol'] == symbol]['pe_ratio'].dropna()

    # Calculate percentiles
    p5 = ticker_data.quantile(0.05)
    p25 = ticker_data.quantile(0.25)
    p50 = ticker_data.quantile(0.50)
    p75 = ticker_data.quantile(0.75)
    p95 = ticker_data.quantile(0.95)

    current_val = ticker_data.iloc[-1]
    percentile = np.sum(ticker_data <= current_val) / len(ticker_data) * 100

    fig = go.Figure()

    # Grey candlestick (percentile box)
    fig.add_trace(go.Candlestick(
        x=[symbol],
        open=[p25], high=[p95], low=[p5], close=[p75],
        increasing_line_color='lightgrey',
        decreasing_line_color='lightgrey',
        showlegend=False
    ))

    # Red dot (current value)
    fig.add_trace(go.Scatter(
        x=[symbol],
        y=[current_val],
        mode='markers',
        marker=dict(size=10, color='#A95C68'),
        hovertemplate=(
            f"<b>{symbol}</b><br>" +
            f"Current PE: {current_val:.2f}<br>" +
            f"Percentile: {percentile:.1f}%<br>" +
            f"Median: {p50:.2f}<br>"
        )
    ))

    fig.update_layout(
        title=f'PE Ratio Distribution - {symbol}',
        yaxis_title='PE Ratio',
        height=400
    )

    return fig

# Display
fig = create_pe_candlestick(symbol, pe_df)
st.plotly_chart(fig, use_container_width=True)

# PB candlestick (same pattern)
fig = create_pe_candlestick(symbol, pb_df)  # Reuse function
st.plotly_chart(fig, use_container_width=True)
```

**For COMPANY only:**
```python
# PS Ratio trend
if entity_type == 'COMPANY':
    ps_df = pd.read_parquet(DataPaths.valuation('ps'))
    ps_data = ps_df[ps_df['symbol'] == symbol]

    fig = pcb.line_chart(
        df=ps_data,
        x_col='date',
        y_cols=['ps_ratio'],
        title=f'PS Ratio Trend - {symbol}'
    )
    st.plotly_chart(fig, use_container_width=True)

    # EV/EBITDA trend
    ev_df = pd.read_parquet(DataPaths.valuation('ev_ebitda'))
    ev_data = ev_df[ev_df['symbol'] == symbol]

    fig = pcb.line_chart(
        df=ev_data,
        x_col='date',
        y_cols=['ev_ebitda'],
        title=f'EV/EBITDA Trend - {symbol}'
    )
    st.plotly_chart(fig, use_container_width=True)
```

#### Tab 2: Sector Valuation (Cross-sector comparison)

**Design:** Multiple sectors PE/PB candlestick (matching bank_dashboard.py)

```python
# Sidebar: Multi-sector selection
selected_sectors = st.sidebar.multiselect(
    "Select Sectors",
    options=all_sectors,
    default=["Ngân hàng", "Bất động sản", "Công nghệ Thông tin"]
)

# Get tickers by sector
sector_tickers = {}
for sector in selected_sectors:
    sector_tickers[sector] = get_sector_stocks(sector)

# Create combined candlestick chart
fig = go.Figure()

for sector, tickers in sector_tickers.items():
    for ticker in tickers:
        ticker_data = pe_df[pe_df['symbol'] == ticker]['pe_ratio'].dropna()

        if len(ticker_data) < 20:
            continue

        # Smart outlier handling (from bank_dashboard.py)
        median_val = ticker_data.median()
        upper_limit = min(50, median_val * 3) if median_val > 0 else 50
        clean_data = ticker_data[ticker_data <= upper_limit]

        if len(clean_data) < 20:
            clean_data = ticker_data

        # Calculate percentiles
        p5, p25, p50, p75, p95 = clean_data.quantile([0.05, 0.25, 0.50, 0.75, 0.95])
        current_val = ticker_data.iloc[-1]
        percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100

        # Add candlestick (grey)
        fig.add_trace(go.Candlestick(
            x=[ticker],
            open=[p25], high=[p95], low=[p5], close=[p75],
            increasing_line_color='lightgrey',
            decreasing_line_color='lightgrey',
            showlegend=False,
            name=f"{ticker} ({sector})"
        ))

        # Add current value (red dot)
        fig.add_trace(go.Scatter(
            x=[ticker],
            y=[current_val],
            mode='markers',
            marker=dict(size=8, color='#A95C68'),
            showlegend=False,
            hovertemplate=(
                f"<b>{ticker}</b><br>" +
                f"Sector: {sector}<br>" +
                f"Current PE: {current_val:.2f}<br>" +
                f"Percentile: {percentile:.1f}%<br>" +
                f"Median: {p50:.2f}"
            )
        ))

fig.update_layout(
    title='PE Distribution by Sector',
    xaxis_title='Ticker (Grouped by Sector)',
    yaxis_title='PE Ratio',
    height=600,
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)
```

**Sector Summary Table:**
```python
# Calculate sector median PE/PB
sector_summary = []

for sector in selected_sectors:
    sector_stocks = sector_tickers[sector]
    sector_pe = pe_df[pe_df['symbol'].isin(sector_stocks)]['pe_ratio']
    sector_pb = pb_df[pb_df['symbol'].isin(sector_stocks)]['pb_ratio']

    sector_summary.append({
        'Sector': sector,
        '# Stocks': len(sector_stocks),
        'Median PE': sector_pe.median(),
        'Mean PE': sector_pe.mean(),
        'Median PB': sector_pb.median(),
        'Mean PB': sector_pb.mean()
    })

df_summary = pd.DataFrame(sector_summary)
st.dataframe(df_summary, use_container_width=True)

# Bar chart: Sector median PE comparison
fig = pcb.bar_chart(
    df=df_summary,
    x_col='Sector',
    y_col='Median PE',
    title='Sector Median PE Comparison',
    show_values=True
)
st.plotly_chart(fig, use_container_width=True)
```

#### Tab 3: VN-Index Valuation
#### Tab 4: Fair Value Calculator

### 4.6 Page 5: Technical Dashboard

**File:** `WEBAPP/pages/3_technical/technical_dashboard.py`

#### Tab 1: Stock Technical (Individual)

**Candlestick + Volume:**
```python
# Load technical data
tech_df = pd.read_parquet(DataPaths.technical('basic'))
symbol_data = tech_df[tech_df['symbol'] == symbol].tail(100)  # Last 100 days

# Candlestick with volume
fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.7, 0.3],
    shared_xaxes=True,
    vertical_spacing=0.03,
    subplot_titles=(f'{symbol} Price Chart', 'Volume')
)

# Candlestick
fig.add_trace(
    go.Candlestick(
        x=symbol_data['date'],
        open=symbol_data['open'],
        high=symbol_data['high'],
        low=symbol_data['low'],
        close=symbol_data['close'],
        name='Price'
    ),
    row=1, col=1
)

# MA overlay
if show_ma20:
    fig.add_trace(
        go.Scatter(x=symbol_data['date'], y=symbol_data['ma_20'],
                   name='MA20', line=dict(color='orange')),
        row=1, col=1
    )

if show_ma50:
    fig.add_trace(
        go.Scatter(x=symbol_data['date'], y=symbol_data['ma_50'],
                   name='MA50', line=dict(color='blue')),
        row=1, col=1
    )

# Volume bars
fig.add_trace(
    go.Bar(x=symbol_data['date'], y=symbol_data['volume'], name='Volume'),
    row=2, col=1
)

fig.update_layout(height=600, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
```

**RSI:**
```python
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=symbol_data['date'],
    y=symbol_data['rsi_14'],
    name='RSI',
    line=dict(color='#1E40AF')
))

# Overbought/Oversold zones
fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")

fig.update_layout(title=f'RSI (14) - {symbol}', yaxis_range=[0, 100])
st.plotly_chart(fig, use_container_width=True)
```

**MACD:**
```python
fig = go.Figure()

fig.add_trace(go.Scatter(x=symbol_data['date'], y=symbol_data['macd'], name='MACD'))
fig.add_trace(go.Scatter(x=symbol_data['date'], y=symbol_data['macd_signal'], name='Signal'))
fig.add_trace(go.Bar(x=symbol_data['date'], y=symbol_data['macd_histogram'], name='Histogram'))

fig.update_layout(title=f'MACD - {symbol}')
st.plotly_chart(fig, use_container_width=True)
```

#### Tab 2: TA Screening (Signal Tables)

**MA Alignment Signals:**
```python
ma_signals = []

for symbol in all_symbols:
    latest = tech_df[tech_df['symbol'] == symbol].iloc[-1]

    price = latest['close']
    ma20, ma50, ma100, ma200 = latest['ma_20'], latest['ma_50'], latest['ma_100'], latest['ma_200']

    # Check alignment
    bullish = (price > ma20 > ma50 > ma100 > ma200)
    bearish = (price < ma20 < ma50 < ma100 < ma200)

    # Get sector
    sector = ticker_details.get(symbol, {}).get('sector', 'N/A')

    ma_signals.append({
        'Symbol': symbol,
        'Sector': sector,
        'Price': price,
        'MA20': ma20,
        'MA50': ma50,
        'Signal': '🟢 Bullish' if bullish else ('🔴 Bearish' if bearish else '⚪ Neutral'),
        'Score': 2 if bullish else (-2 if bearish else 0)
    })

df_ma_signals = pd.DataFrame(ma_signals)

# Filters
col1, col2 = st.columns(2)
with col1:
    sector_filter = st.multiselect("Filter by Sector", df_ma_signals['Sector'].unique())
with col2:
    signal_filter = st.multiselect("Filter by Signal", ['🟢 Bullish', '🔴 Bearish', '⚪ Neutral'])

if sector_filter:
    df_ma_signals = df_ma_signals[df_ma_signals['Sector'].isin(sector_filter)]
if signal_filter:
    df_ma_signals = df_ma_signals[df_ma_signals['Signal'].isin(signal_filter)]

# Display
st.dataframe(
    df_ma_signals.sort_values('Score', ascending=False),
    use_container_width=True
)
```

**RSI Signals:**
```python
rsi_signals = []

for symbol in all_symbols:
    rsi = tech_df[tech_df['symbol'] == symbol]['rsi_14'].iloc[-1]
    sector = ticker_details.get(symbol, {}).get('sector', 'N/A')

    if rsi < 30:
        signal = '🟢 Oversold (Buy)'
        score = 1
    elif rsi > 70:
        signal = '🔴 Overbought (Sell)'
        score = -1
    else:
        signal = '⚪ Neutral'
        score = 0

    rsi_signals.append({
        'Symbol': symbol,
        'Sector': sector,
        'RSI': rsi,
        'Signal': signal,
        'Score': score
    })

df_rsi = pd.DataFrame(rsi_signals)
st.dataframe(df_rsi.sort_values('Score', ascending=False), use_container_width=True)
```

**Combined TA Score:**
```python
def calculate_ta_score(symbol, tech_df):
    """Calculate combined TA score (-5 to +5)"""
    latest = tech_df[tech_df['symbol'] == symbol].tail(2)
    curr = latest.iloc[-1]
    prev = latest.iloc[-2]

    score = 0

    # MA Alignment (±2)
    if (curr['close'] > curr['ma_20'] > curr['ma_50'] > curr['ma_100'] > curr['ma_200']):
        score += 2
    elif (curr['close'] < curr['ma_20'] < curr['ma_50'] < curr['ma_100'] < curr['ma_200']):
        score -= 2

    # RSI (±1)
    if curr['rsi_14'] < 30:
        score += 1
    elif curr['rsi_14'] > 70:
        score -= 1

    # MACD Cross (±1)
    if (prev['macd'] < prev['macd_signal']) and (curr['macd'] > curr['macd_signal']):
        score += 1  # Bullish cross
    elif (prev['macd'] > prev['macd_signal']) and (curr['macd'] < curr['macd_signal']):
        score -= 1  # Bearish cross

    # Volume (±1)
    vol_ma = curr['volume_ma_20']
    if curr['volume'] > vol_ma * 1.5:
        score += 1 if curr['close'] > prev['close'] else -1

    return score

# Calculate for all symbols
combined_signals = []

for symbol in all_symbols:
    score = calculate_ta_score(symbol, tech_df)
    sector = ticker_details.get(symbol, {}).get('sector', 'N/A')

    signal = (
        '🟢 Strong Buy' if score >= 3 else
        '🔵 Buy' if score >= 1 else
        '🔴 Sell' if score <= -1 else
        '⚪ Neutral'
    )

    combined_signals.append({
        'Symbol': symbol,
        'Sector': sector,
        'TA Score': score,
        'Signal': signal
    })

df_combined = pd.DataFrame(combined_signals).sort_values('TA Score', ascending=False)
st.dataframe(df_combined, use_container_width=True)
```

#### Tab 3: Market Breadth (Market-wide)

**Reference:** `technical_dashboard.py` line 182-363

```python
# Load market breadth data
breadth_df = pd.read_parquet('DATA/processed/technical/market_breadth_global.parquet')

# Calculate % stocks above MA
latest = breadth_df.iloc[-1]

col1, col2, col3 = st.columns(3)
col1.metric("Above MA20", f"{latest['pct_ma20']:.1f}%")
col2.metric("Above MA50", f"{latest['pct_ma50']:.1f}%")
col3.metric("Above MA100", f"{latest['pct_ma100']:.1f}%")

# Chart
fig = pcb.line_chart(
    df=breadth_df.tail(250),  # Last year
    x_col='date',
    y_cols=['pct_ma20', 'pct_ma50', 'pct_ma100'],
    title='Market Breadth (% Stocks Above MA)',
    y_axis_title='%'
)

# Add zones (median ± 1σ)
p20_50 = breadth_df['pct_ma50'].quantile(0.20)
p80_50 = breadth_df['pct_ma50'].quantile(0.80)

fig.add_hrect(y0=0, y1=p20_50, fillcolor="red", opacity=0.1, annotation_text="Bearish Zone")
fig.add_hrect(y0=p80_50, y1=100, fillcolor="green", opacity=0.1, annotation_text="Bullish Zone")

st.plotly_chart(fig, use_container_width=True)
```

#### Tab 4: Sector TA Analysis (NEW)

**1. % Stocks Above MA by Sector:**
```python
st.subheader("Sector Technical Analysis")

# Sector selector
sector = st.selectbox("Select Sector", all_sectors)

# Get sector stocks
sector_stocks = get_sector_stocks(sector)
st.write(f"**{len(sector_stocks)} stocks in {sector}**")

# Filter technical data for sector
sector_tech_df = tech_df[tech_df['symbol'].isin(sector_stocks)]

# Calculate % above MA over time
sector_ma_breadth = sector_tech_df.groupby('date').apply(lambda x: pd.Series({
    'above_ma20': (x['close'] > x['ma_20']).sum() / len(x) * 100,
    'above_ma50': (x['close'] > x['ma_50']).sum() / len(x) * 100,
    'above_ma100': (x['close'] > x['ma_100']).sum() / len(x) * 100
})).reset_index()

# Chart
fig = pcb.line_chart(
    df=sector_ma_breadth.tail(250),
    x_col='date',
    y_cols=['above_ma20', 'above_ma50', 'above_ma100'],
    title=f'% Stocks Above MA - {sector} Sector',
    y_axis_title='%'
)
st.plotly_chart(fig, use_container_width=True)

# Current metrics
latest = sector_ma_breadth.iloc[-1]
col1, col2, col3 = st.columns(3)
col1.metric("Above MA20", f"{latest['above_ma20']:.1f}%")
col2.metric("Above MA50", f"{latest['above_ma50']:.1f}%")
col3.metric("Above MA100", f"{latest['above_ma100']:.1f}%")
```

**2. Trading Value by Sector (Dòng tiền):**

**Reference:** `technical_dashboard.py` line 367-453

```python
# Calculate trading value for sector
sector_trading = []

for date in sector_tech_df['date'].unique():
    daily_df = sector_tech_df[sector_tech_df['date'] == date]

    # Trading value = price * volume
    trading_value = (daily_df['close'] * daily_df['volume']).sum()

    sector_trading.append({
        'date': date,
        'trading_value': trading_value
    })

df_trading = pd.DataFrame(sector_trading)

# Calculate changes
df_trading['change_5d'] = df_trading['trading_value'].pct_change(5) * 100
df_trading['change_20d'] = df_trading['trading_value'].pct_change(20) * 100

# Chart: Trading value trend with color by change
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_trading['date'],
    y=df_trading['trading_value'] / 1e9,  # Billions
    marker=dict(
        color=df_trading['change_5d'],
        colorscale='RdYlGn',
        showscale=True,
        colorbar=dict(title="Change 5D (%)")
    ),
    hovertemplate='Date: %{x}<br>Value: %{y:.2f}B<br>Change 5D: %{customdata:.1f}%<extra></extra>',
    customdata=df_trading['change_5d']
))

fig.update_layout(
    title=f'Trading Value Trend - {sector} Sector',
    xaxis_title='Date',
    yaxis_title='Trading Value (Billion VND)',
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# Summary metrics
latest_tv = df_trading.iloc[-1]
col1, col2, col3 = st.columns(3)
col1.metric("Latest", f"{latest_tv['trading_value']/1e9:.2f}B")
col2.metric("Change 5D", f"{latest_tv['change_5d']:+.1f}%")
col3.metric("Change 20D", f"{latest_tv['change_20d']:+.1f}%")
```

**3. Sector TA Signals:**
```python
# Calculate TA scores for all stocks in sector
sector_signals = []

for symbol in sector_stocks:
    score = calculate_ta_score(symbol, tech_df)

    signal = (
        '🟢 Strong Buy' if score >= 3 else
        '🔵 Buy' if score >= 1 else
        '🔴 Sell' if score <= -1 else
        '⚪ Neutral'
    )

    sector_signals.append({
        'Symbol': symbol,
        'TA Score': score,
        'Signal': signal
    })

df_signals = pd.DataFrame(sector_signals)

# Summary: Count by signal
signal_counts = df_signals['Signal'].value_counts()

# Pie chart
fig = go.Figure(data=[go.Pie(
    labels=signal_counts.index,
    values=signal_counts.values,
    hole=0.4
)])

fig.update_layout(title=f'TA Signal Distribution - {sector} Sector')
st.plotly_chart(fig, use_container_width=True)

# Table
st.subheader(f"All Stocks in {sector}")
st.dataframe(df_signals.sort_values('TA Score', ascending=False), use_container_width=True)
```

**4. Sector Momentum (Avg RSI/MACD):**
```python
# Calculate sector average RSI and MACD
sector_momentum = sector_tech_df.groupby('date').agg({
    'rsi_14': 'mean',
    'macd': 'mean',
    'macd_signal': 'mean'
}).reset_index()

# RSI chart
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=sector_momentum['date'],
    y=sector_momentum['rsi_14'],
    name='Sector Avg RSI',
    line=dict(color='#1E40AF')
))

fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")

fig.update_layout(
    title=f'Sector Average RSI - {sector}',
    yaxis_title='RSI',
    yaxis_range=[0, 100]
)

st.plotly_chart(fig, use_container_width=True)
```

#### Tab 5: Commodity & Macro

```python
# Load data
gold_df = pd.read_parquet('DATA/processed/commodity/gold.parquet')
oil_df = pd.read_parquet('DATA/processed/commodity/oil.parquet')
usd_vnd_df = pd.read_parquet('DATA/processed/macro/exchange_rate.parquet')

# KPI cards
col1, col2, col3, col4 = st.columns(4)

gold_latest = gold_df.iloc[-1]
gold_change = (gold_latest['price'] / gold_df.iloc[-2]['price'] - 1) * 100

oil_latest = oil_df.iloc[-1]
oil_change = (oil_latest['brent_price'] / oil_df.iloc[-2]['brent_price'] - 1) * 100

usd_vnd_latest = usd_vnd_df.iloc[-1]
usd_vnd_change = (usd_vnd_latest['usd_vnd'] / usd_vnd_df.iloc[-2]['usd_vnd'] - 1) * 100

with col1:
    st.metric("Gold (USD/oz)", f"${gold_latest['price']:,.0f}", f"{gold_change:+.2f}%")

with col2:
    st.metric("Oil Brent (USD/bbl)", f"${oil_latest['brent_price']:.2f}", f"{oil_change:+.2f}%")

with col3:
    st.metric("USD/VND", f"{usd_vnd_latest['usd_vnd']:,.0f}", f"{usd_vnd_change:+.2f}%")

with col4:
    # VN-Index (from technical data)
    vnindex = tech_df[tech_df['symbol'] == 'VNINDEX']['close'].iloc[-1]
    vnindex_change = (vnindex / tech_df[tech_df['symbol'] == 'VNINDEX']['close'].iloc[-2] - 1) * 100
    st.metric("VN-Index", f"{vnindex:,.2f}", f"{vnindex_change:+.2f}%")

st.divider()

# Charts
col1, col2 = st.columns(2)

with col1:
    # Gold chart with MA
    fig = pcb.line_chart(
        df=gold_df.tail(250),
        x_col='date',
        y_cols=['price'],
        title='Gold Price Trend (1 Year)'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Oil chart
    fig = pcb.line_chart(
        df=oil_df.tail(250),
        x_col='date',
        y_cols=['brent_price', 'wti_price'],
        title='Oil Price Trend (1 Year)'
    )
    st.plotly_chart(fig, use_container_width=True)

# USD/VND
fig = pcb.line_chart(
    df=usd_vnd_df.tail(250),
    x_col='date',
    y_cols=['usd_vnd'],
    title='USD/VND Exchange Rate (1 Year)'
)
st.plotly_chart(fig, use_container_width=True)

# Alerts
if abs(gold_change) > 2:
    st.warning(f"⚠️ Gold moved {gold_change:+.2f}% today!")

if abs(usd_vnd_change) > 0.5:
    st.warning(f"⚠️ USD/VND moved {usd_vnd_change:+.2f}% today!")
```

### 4.7 Page 6-7: Intelligence

**Analyst Forecasts:** BSC forecasts, target prices
**News & Sentiment:** News feed, sentiment analysis

---

## 5. Component Library

### 5.1 Overview

**Location:** `WEBAPP/components/`

**Structure:**
```
WEBAPP/components/
├── __init__.py
├── charts/
│   ├── __init__.py
│   └── plotly_builders.py          # PlotlyChartBuilder class
├── navigation/
│   ├── __init__.py
│   ├── main_nav.py                 # render_main_nav()
│   └── breadcrumbs.py              # render_breadcrumbs()
├── inputs/
│   ├── __init__.py
│   ├── symbol_selector.py          # symbol_selector()
│   └── date_range.py               # date_range_picker()
└── data_display/
    ├── __init__.py
    └── metric_cards.py             # metric_card_row()
```

### 5.2 PlotlyChartBuilder

**File:** `WEBAPP/components/charts/plotly_builders.py`

**7 Chart Methods:**

```python
class PlotlyChartBuilder:
    """Reusable Plotly chart builder"""

    COLORS = {
        'primary': '#1E40AF',
        'secondary': '#10B981',
        'accent': '#F59E0B',
        'danger': '#EF4444',
        'chart': ['#1E40AF', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316']
    }

    @staticmethod
    def line_chart(df, x_col, y_cols, title, **kwargs):
        """Multi-line chart"""

    @staticmethod
    def bar_chart(df, x_col, y_col, title, **kwargs):
        """Bar chart with labels"""

    @staticmethod
    def bar_line_combo(df, x_col, bar_col, line_col, title, **kwargs):
        """⭐ Most used - Bar + Line overlay"""

    @staticmethod
    def candlestick_chart(df, title, **kwargs):
        """Candlestick (for PE/PB valuation)"""

    @staticmethod
    def heatmap(data, title, **kwargs):
        """Heatmap (for sector comparison)"""

    @staticmethod
    def line_with_bands(df, x_col, y_col, mean_col, std_col, title, **kwargs):
        """Line with statistical bands (±nσ)"""

    @staticmethod
    def waterfall_chart(categories, values, title, **kwargs):
        """Waterfall (for cash flow)"""
```

**Usage:**
```python
from WEBAPP.components.charts import PlotlyChartBuilder as pcb

# Example: Bar + Line combo
fig = pcb.bar_line_combo(
    df=data,
    x_col='quarter',
    bar_col='net_revenue',
    line_col='net_revenue_ma4',
    title='Revenue Trend'
)

st.plotly_chart(fig, use_container_width=True)
```

### 5.3 Other Components

**Navigation:**
```python
from WEBAPP.components.navigation import render_main_nav, render_breadcrumbs

render_main_nav()  # 4 category buttons
render_breadcrumbs(["Home", "FA", "Company Analysis"])
```

**Inputs:**
```python
from WEBAPP.components.inputs import symbol_selector, date_range_picker

symbol = symbol_selector(entity_type='company', default='VNM')
start_date, end_date = date_range_picker()
```

**Data Display:**
```python
from WEBAPP.components.data_display import metric_card_row

metric_card_row([
    {'label': 'Revenue', 'value': 1234.56, 'delta': 12.3, 'format': 'billions'},
    {'label': 'ROE', 'value': 18.5, 'delta': 2.1, 'format': 'percent'}
])
```

---

## 6. Implementation Guide

### 6.1 Prerequisites

**Check data files:**
```bash
# Fundamental
ls -lh DATA/processed/fundamental/company/company_financial_metrics.parquet
ls -lh DATA/processed/fundamental/bank/bank_financial_metrics.parquet
ls -lh DATA/processed/fundamental/security/security_financial_metrics.parquet

# Valuation
ls -lh DATA/processed/valuation/pe/pe_historical_all_symbols_final.parquet
ls -lh DATA/processed/valuation/pb/pb_historical_all_symbols_final.parquet

# Technical
ls -lh DATA/processed/technical/basic_data.parquet
ls -lh DATA/processed/technical/market_breadth_global.parquet

# Configuration
ls -lh config/metadata/ticker_details.json
```

**If missing, run calculators:**
```bash
# Generate fundamental data
python3 PROCESSORS/fundamental/calculators/company_calculator.py
python3 PROCESSORS/fundamental/calculators/bank_calculator.py
python3 PROCESSORS/fundamental/calculators/security_calculator.py

# Generate valuation data
python3 PROCESSORS/valuation/calculators/run_daily_valuation_update.py

# Generate technical data
python3 PROCESSORS/technical/pipelines/daily_ohlcv_update.py
```

### 6.2 Step-by-Step Implementation

#### Week 1: FA Pages with Sector Analysis

**Day 1-2: Company Analysis**

1. Copy demo as template:
```bash
cp WEBAPP/pages/1_fundamental/company_analysis_demo.py \
   WEBAPP/pages/1_fundamental/company_analysis.py
```

2. Update tabs to 6 (add Sector Analysis tab):
```python
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Overview",
    "💰 Income Statement",
    "🏦 Balance Sheet",
    "💸 Cash Flow",
    "📊 Financial Ratios",
    "🌐 Sector Analysis"  # NEW
])
```

3. Implement sector analysis tab (see Section 4.2, Tab 6)

4. Test:
```bash
streamlit run WEBAPP/pages/1_fundamental/company_analysis.py
```

**Day 3: Banking Analysis**
- Copy company_analysis.py structure
- Replace Company metrics with Bank metrics (NII, CAR, NPL, LDR)
- Update sector analysis for banking sector

**Day 4: Securities Analysis**
- Copy structure
- Replace with Securities metrics (Brokerage revenue, market share)
- Update sector analysis

**Day 5: Testing & Refinement**
- Test all 3 FA pages
- Check sector filtering works
- Verify charts render correctly

#### Week 2: Valuation with Sector View

**Day 6-7: Individual Valuation**
- Implement PE/PB candlestick (design from bank_dashboard.py)
- Add PS and EV/EBITDA (company only)
- Test with multiple symbols

**Day 8-9: Sector Valuation**
- Implement multi-sector candlestick chart
- Add sector summary table
- Add sector comparison bar chart

**Day 10: Testing**

#### Week 3: TA with Sector TA

**Day 11: Stock Technical**
- Candlestick + volume
- MA overlay
- RSI, MACD charts

**Day 12: TA Screening**
- MA alignment table
- RSI signals table
- Combined score table

**Day 13: Market Breadth**
- % stocks above MA (global)
- Market breadth chart with zones

**Day 14: Sector TA (NEW)**
- % stocks above MA by sector
- Trading value by sector
- Sector TA signals
- Sector momentum

**Day 15: Commodity & Macro**
- Gold, Oil charts
- USD/VND chart
- KPI cards with alerts

#### Week 4: Polish & Deploy

**Day 16-17: Intelligence Pages**
- Forecasts page
- News & sentiment page

**Day 18: UI/UX Polish**
- Apply consistent styling
- Add dark mode (optional)
- Improve navigation

**Day 19: Performance Optimization**
- Audit cache usage
- Measure page load times
- Optimize slow queries

**Day 20: Testing & Documentation**
- Integration testing
- User acceptance testing
- Update documentation

### 6.3 Common Patterns

**Pattern 1: Loading sector data**
```python
import json

# Load ticker classification
with open('config/metadata/ticker_details.json') as f:
    ticker_details = json.load(f)

# Get stocks by sector
def get_sector_stocks(sector):
    return [
        ticker for ticker, info in ticker_details.items()
        if info['sector'] == sector
    ]

# Usage
banking_stocks = get_sector_stocks('Ngân hàng')
tech_stocks = get_sector_stocks('Công nghệ Thông tin')
```

**Pattern 2: Parquet data loading with caching**
```python
from WEBAPP.core.data_paths import DataPaths

@st.cache_data(ttl=3600)  # 1 hour cache
def load_company_data():
    path = DataPaths.fundamental('company')
    return pd.read_parquet(path)

# Usage
company_df = load_company_data()
```

**Pattern 3: Sector analysis**
```python
def analyze_sector(sector, data_df, ticker_details):
    """Generic sector analysis function"""

    # 1. Get sector stocks
    sector_stocks = [
        ticker for ticker, info in ticker_details.items()
        if info['sector'] == sector
    ]

    # 2. Filter data
    sector_data = data_df[data_df['symbol'].isin(sector_stocks)]

    # 3. Calculate sector averages
    sector_avg = sector_data.groupby('date').agg({
        'metric1': 'mean',
        'metric2': 'median',
        'metric3': 'std'
    })

    # 4. Calculate distributions
    latest = sector_data[sector_data['date'] == sector_data['date'].max()]
    distributions = {
        'p25': latest['metric1'].quantile(0.25),
        'p50': latest['metric1'].quantile(0.50),
        'p75': latest['metric1'].quantile(0.75)
    }

    return sector_avg, latest, distributions
```

---

## 7. Code Examples

### 7.1 Complete Page Template

```python
"""
Page Template
=============

Standard template for all pages.
"""

import streamlit as st
import pandas as pd
import json
from WEBAPP.core.data_paths import DataPaths
from WEBAPP.components.charts import PlotlyChartBuilder as pcb
from WEBAPP.components.navigation import render_main_nav, render_breadcrumbs
from WEBAPP.components.inputs import symbol_selector, date_range_picker
from WEBAPP.components.data_display import metric_card_row

# Page config
st.set_page_config(
    page_title="Page Title",
    page_icon="📊",
    layout="wide"
)

# Navigation
render_main_nav()
render_breadcrumbs(["Home", "Category", "Page"])

# Load ticker classification
@st.cache_resource
def load_ticker_details():
    with open('config/metadata/ticker_details.json') as f:
        return json.load(f)

ticker_details = load_ticker_details()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # Sector filter
    sector = st.selectbox("Sector", all_sectors)

    # Symbol selector
    symbols = get_sector_stocks(sector)
    symbol = st.selectbox("Symbol", symbols)

    # Date range
    start_date, end_date = date_range_picker()

# Load data
@st.cache_data(ttl=3600)
def load_data():
    path = DataPaths.fundamental('company')
    return pd.read_parquet(path)

data = load_data()
symbol_data = data[data['symbol'] == symbol]

# Main content
st.title(f"📊 Page Title: {symbol}")

tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

with tab1:
    # Metrics
    latest = symbol_data.iloc[-1]

    metric_card_row([
        {'label': 'Metric 1', 'value': latest['metric1'], 'format': 'billions'},
        {'label': 'Metric 2', 'value': latest['metric2'], 'format': 'percent'}
    ])

    # Chart
    fig = pcb.line_chart(
        df=symbol_data,
        x_col='quarter',
        y_cols=['metric1', 'metric2'],
        title='Chart Title'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Content for tab 2
    pass

with tab3:
    # Content for tab 3
    pass

# Footer
st.divider()
st.caption(f"Last updated: {latest['date'].strftime('%Y-%m-%d')} | Data source: parquet_file.parquet")
```

### 7.2 Sector Analysis Template

```python
"""
Sector Analysis Tab Template
=============================

Reusable template for sector analysis tabs.
"""

def render_sector_analysis_tab(sector, data_df, ticker_details, metrics):
    """
    Render sector analysis tab.

    Args:
        sector: Sector name (e.g., "Thực phẩm và đồ uống")
        data_df: DataFrame with all data
        ticker_details: Dict from ticker_details.json
        metrics: List of metric column names to analyze

    Example:
        render_sector_analysis_tab(
            sector="Ngân hàng",
            data_df=bank_df,
            ticker_details=ticker_details,
            metrics=['nim', 'car', 'npl_ratio', 'roe']
        )
    """
    st.subheader(f"Sector Analysis: {sector}")

    # Get sector stocks
    sector_stocks = [
        ticker for ticker, info in ticker_details.items()
        if info['sector'] == sector
    ]

    st.write(f"**{len(sector_stocks)} stocks in sector**")

    # Filter data
    sector_data = data_df[data_df['symbol'].isin(sector_stocks)]

    # 1. Sector Average Trends
    st.subheader("1️⃣ Sector Average Trends")

    sector_avg = sector_data.groupby('quarter')[metrics].mean().reset_index()

    fig = pcb.line_chart(
        df=sector_avg,
        x_col='quarter',
        y_cols=metrics,
        title=f'Sector Average Metrics - {sector}'
    )
    st.plotly_chart(fig, use_container_width=True)

    # 2. Sector Heatmap
    st.subheader("2️⃣ Sector Heatmap (Latest Quarter)")

    latest = sector_data[sector_data['quarter'] == sector_data['quarter'].max()]

    heatmap_data = latest.pivot_table(
        index='symbol',
        values=metrics
    )

    # Normalize
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 100))
    heatmap_normalized = pd.DataFrame(
        scaler.fit_transform(heatmap_data),
        index=heatmap_data.index,
        columns=heatmap_data.columns
    )

    fig = pcb.heatmap(
        data=heatmap_normalized,
        title=f'Sector Metrics Heatmap - {sector}',
        colorscale='RdYlGn'
    )
    st.plotly_chart(fig, use_container_width=True)

    # 3. Sector Distribution
    st.subheader("3️⃣ Metrics Distribution")

    fig = go.Figure()

    for metric in metrics:
        fig.add_trace(go.Box(
            y=latest[metric],
            name=metric,
            boxmean='sd'
        ))

    fig.update_layout(title=f'Sector Metrics Distribution - {sector}')
    st.plotly_chart(fig, use_container_width=True)

    # 4. Top Performers
    st.subheader("4️⃣ Top & Bottom Performers")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Top 5 by {metrics[0]}**")
        top = latest.nlargest(5, metrics[0])[['symbol'] + metrics]
        st.dataframe(top, hide_index=True)

    with col2:
        st.write(f"**Bottom 5 by {metrics[0]}**")
        bottom = latest.nsmallest(5, metrics[0])[['symbol'] + metrics]
        st.dataframe(bottom, hide_index=True)
```

### 7.3 Reference Implementation

**From existing code:**

```python
# Valuation candlestick design
# Reference: bank_dashboard.py line 1658-1807

def create_valuation_candlestick(df, symbols, metric_type='pe'):
    """
    Create PE/PB candlestick chart.

    Design:
    - Grey candlestick = percentile box (P25-P75)
    - Upper wick = P95
    - Lower wick = P5
    - Red dot = current value
    """
    # See Section 4.5, Tab 1 for full implementation

# Trading value by sector
# Reference: technical_dashboard.py line 367-453

def render_trading_value_chart(sector):
    """
    Render trading value chart for sector.

    Shows:
    - Daily trading value (bar chart)
    - Color by 5-day change
    - Summary metrics
    """
    # See Section 4.6, Tab 4 for full implementation
```

---

## 8. Timeline & Phases

### 8.1 Overview (20 days)

| Week | Phase | Focus | Days |
|------|-------|-------|------|
| **1** | FA Pages | Company, Bank, Securities + Sector tabs | 5 |
| **2** | Valuation | Individual + Sector candlestick | 5 |
| **3** | TA | Stock TA, Screening, Market Breadth, Sector TA | 5 |
| **4** | Polish | Intelligence, UI/UX, Performance, Testing | 5 |

### 8.2 Detailed Timeline

#### Week 1: FA Pages (Day 1-5)

**Day 1-2: Company Analysis**
- ✅ Copy demo template
- ✅ Implement tabs 1-5 (individual)
- ✅ Implement tab 6 (sector analysis)
  - Sector average trends
  - Sector heatmap
  - Sector distribution
  - Top/bottom performers
- ✅ Test with real data

**Day 3: Banking Analysis**
- ✅ Adapt template for bank metrics
- ✅ Replace CIS → BIS metrics
- ✅ Banking sector analysis tab
- ✅ Test with ACB, VCB, TCB

**Day 4: Securities Analysis**
- ✅ Adapt template for securities metrics
- ✅ Replace with SIS metrics
- ✅ Securities sector analysis tab
- ✅ Test with SSI, VND, HCM

**Day 5: Testing & Refinement**
- ✅ Test all 3 FA pages
- ✅ Verify sector filtering
- ✅ Check data loading performance
- ✅ Fix any bugs

**Deliverables:** 3 FA pages with individual + sector analysis

---

#### Week 2: Valuation (Day 6-10)

**Day 6-7: Individual Valuation**
- ✅ PE candlestick (design from bank_dashboard.py)
- ✅ PB candlestick
- ✅ PS ratio (company only)
- ✅ EV/EBITDA (company only)
- ✅ Historical percentiles

**Day 8-9: Sector Valuation**
- ✅ Multi-sector candlestick chart
  - Grey candlestick for each ticker
  - Red dot for current value
  - Grouped by sector
- ✅ Sector summary table
  - Median PE/PB by sector
  - # stocks per sector
- ✅ Sector comparison bar chart
- ✅ Test with multiple sectors

**Day 10: Testing & VN-Index**
- ✅ VN-Index PE trend
- ✅ Fair value calculator (optional)
- ✅ Test all valuation features
- ✅ Performance check

**Deliverables:** Universal valuation page with sector view

---

#### Week 3: TA (Day 11-15)

**Day 11: Stock Technical**
- ✅ Candlestick + volume chart
- ✅ MA overlay (20/50/100/200)
- ✅ RSI chart with zones
- ✅ MACD chart

**Day 12: TA Screening**
- ✅ MA alignment table
- ✅ RSI signals table
- ✅ MACD signals table
- ✅ Combined TA score table
- ✅ Sector filtering

**Day 13: Market Breadth**
- ✅ % stocks above MA (global)
- ✅ Market breadth chart with zones
- ✅ Advance/Decline line
- ✅ New highs/lows

**Day 14: Sector TA (KEY REQUIREMENT)**
- ✅ % stocks above MA by sector
- ✅ Trading value by sector (dòng tiền)
- ✅ Sector TA signals distribution
- ✅ Sector momentum (avg RSI/MACD)

**Day 15: Commodity & Macro**
- ✅ Gold price chart
- ✅ Oil price chart
- ✅ USD/VND exchange rate
- ✅ KPI cards with alerts
- ✅ Interest rates (optional)

**Deliverables:** Complete TA page with sector analysis

---

#### Week 4: Polish & Deploy (Day 16-20)

**Day 16: Analyst Forecasts**
- ✅ BSC forecast table
- ✅ Target price chart
- ✅ EPS estimates
- ✅ Rating distribution

**Day 17: News & Sentiment**
- ✅ News feed with filters
- ✅ Sentiment timeline
- ✅ Word cloud
- ✅ Event calendar

**Day 18: UI/UX Polish**
- ✅ Apply consistent styling (CSS)
- ✅ Theme colors
- ✅ Typography
- ✅ Dark mode (optional)
- ✅ Improve navigation

**Day 19: Performance Optimization**
- ✅ Audit cache usage
- ✅ Measure page load times
- ✅ Optimize slow queries
- ✅ Check memory usage
- ✅ Browser performance testing

**Day 20: Testing & Documentation**
- ✅ Integration testing (all pages)
- ✅ User acceptance testing
- ✅ Browser compatibility
- ✅ Mobile responsiveness
- ✅ Update documentation
- ✅ Deployment checklist

**Deliverables:** Production-ready dashboard

---

## 9. Testing & Deployment

### 9.1 Testing Checklist

#### Functional Testing

**Data Loading:**
- [ ] All parquet files load correctly
- [ ] ticker_details.json loads and parses
- [ ] Sector filtering works
- [ ] Symbol selector works
- [ ] Date range picker works

**Charts:**
- [ ] All charts render without errors
- [ ] Charts are responsive (resize correctly)
- [ ] Hover tooltips work
- [ ] Zoom/pan works (Plotly)
- [ ] Export works (download PNG)

**Pages:**
- [ ] Company Analysis (6 tabs)
- [ ] Banking Analysis (6 tabs)
- [ ] Securities Analysis (6 tabs)
- [ ] Valuation Dashboard (4 tabs)
- [ ] Technical Dashboard (5 tabs)
- [ ] Analyst Forecasts
- [ ] News & Sentiment

**Sector Analysis:**
- [ ] Sector average calculations correct
- [ ] Sector heatmap displays correctly
- [ ] Sector distribution box plots work
- [ ] Top/bottom performers correct
- [ ] Trading value by sector correct
- [ ] % stocks above MA by sector correct

#### Performance Testing

- [ ] Page load < 2s
- [ ] Chart render < 300ms
- [ ] Cache hit rate > 80%
- [ ] Memory usage < 500MB
- [ ] CPU usage < 50%

#### Browser Compatibility

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

#### Responsive Testing

- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

### 9.2 Deployment Steps

#### 1. Pre-Deployment

```bash
# 1. Run all calculators to ensure latest data
python3 PROCESSORS/fundamental/calculators/company_calculator.py
python3 PROCESSORS/fundamental/calculators/bank_calculator.py
python3 PROCESSORS/fundamental/calculators/security_calculator.py
python3 PROCESSORS/valuation/calculators/run_daily_valuation_update.py
python3 PROCESSORS/technical/pipelines/daily_ohlcv_update.py

# 2. Verify data files
ls -lh DATA/processed/fundamental/
ls -lh DATA/processed/valuation/
ls -lh DATA/processed/technical/

# 3. Test demo page
streamlit run WEBAPP/pages/1_fundamental/company_analysis_demo.py
```

#### 2. Deploy to Staging

```bash
# Deploy to staging server
git add .
git commit -m "feat: Complete Streamlit UI redesign v3.0"
git push staging main

# Run on staging
ssh staging-server
cd /path/to/app
streamlit run WEBAPP/main_app.py --server.port 8502
```

#### 3. User Acceptance Testing (UAT)

- Invite 5 beta users
- Collect feedback via survey
- Monitor errors in logs
- Fix critical bugs

#### 4. Production Deployment

```bash
# Merge to production
git push origin main

# Deploy
ssh prod-server
cd /path/to/app
streamlit run WEBAPP/main_app.py --server.port 8501
```

#### 5. Post-Deployment Monitoring

- Monitor page load times
- Monitor error rates
- Monitor user engagement
- Collect user feedback

### 9.3 Rollback Plan

If issues arise:

```bash
# Revert to previous version
git revert HEAD
git push origin main

# Or use feature flag
# In app, set ENABLE_NEW_UI=false
```

---

## 10. Quick Reference

### 10.1 File Locations

**Documentation:**
```
docs/streamlit_UI_build/
└── COMPLETE_PLAN.md                # This file
```

**Components:**
```
WEBAPP/components/
├── charts/plotly_builders.py       # 7 chart methods
├── navigation/main_nav.py          # Category nav
├── inputs/symbol_selector.py       # Symbol dropdown
└── data_display/metric_cards.py    # KPI cards
```

**Pages:**
```
WEBAPP/pages/
├── 1_fundamental/
│   ├── company_analysis.py         # Company FA
│   ├── banking_analysis.py         # Bank FA
│   └── securities_analysis.py      # Securities FA
├── 2_valuation/
│   └── valuation_dashboard.py      # PE/PB/PS/EV + Sector
├── 3_technical/
│   └── technical_dashboard.py      # TA + Sector TA
└── 4_intelligence/
    ├── analyst_forecasts.py        # Forecasts
    └── news_sentiment.py           # News
```

**Configuration:**
```
config/metadata/
└── ticker_details.json             # Entity & Sector classification
```

**Demo:**
```
WEBAPP/pages/1_fundamental/
└── company_analysis_demo.py        # Working example
```

### 10.2 Common Commands

**Test demo:**
```bash
streamlit run WEBAPP/pages/1_fundamental/company_analysis_demo.py
```

**Run calculator:**
```bash
python3 PROCESSORS/fundamental/calculators/company_calculator.py
```

**Check data:**
```bash
ls -lh DATA/processed/fundamental/company/company_financial_metrics.parquet
```

**Load ticker details:**
```python
import json
with open('config/metadata/ticker_details.json') as f:
    ticker_details = json.load(f)
```

### 10.3 Key Patterns

**Get sector stocks:**
```python
sector_stocks = [
    ticker for ticker, info in ticker_details.items()
    if info['sector'] == 'Ngân hàng'
]
```

**Load parquet:**
```python
@st.cache_data(ttl=3600)
def load_data():
    return pd.read_parquet(DataPaths.fundamental('company'))
```

**Sector analysis:**
```python
sector_df = df[df['symbol'].isin(sector_stocks)]
sector_avg = sector_df.groupby('quarter')['metric'].mean()
```

### 10.4 Troubleshooting

**Issue: Data file not found**
```bash
# Solution: Run calculator
python3 PROCESSORS/fundamental/calculators/company_calculator.py
```

**Issue: Module not found**
```python
# Solution: Add project root to path
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))
```

**Issue: Column not found**
```python
# Solution: Check available columns
st.write("Columns:", df.columns.tolist())
```

**Issue: Chart shows error**
```python
# Solution: Check DataFrame structure
st.write(df.head())
st.write(df.dtypes)
```

### 10.5 Key References

**Valuation candlestick design:**
- File: `WEBAPP/pages/bank_dashboard.py`
- Lines: 1658-1807
- Function: `render_pe_pb_dotplot()`

**Market breadth:**
- File: `WEBAPP/pages/technical_dashboard.py`
- Lines: 182-363
- Function: `render_market_breadth_chart()`

**Trading value by sector:**
- File: `WEBAPP/pages/technical_dashboard.py`
- Lines: 367-453
- Function: `render_trading_value_chart()`

**Sector breadth:**
- File: `WEBAPP/pages/technical_dashboard.py`
- Lines: 454+
- Function: `render_sector_breadth_table()`

---

## 🎯 Summary

### What We're Building

**7 pages, 2 analysis levels:**
- Individual stock analysis (Tab 1-5)
- **Sector analysis (Tab 6 - NEW)**

### Key Features

✅ **FA:** Individual + Sector average, heatmap, distribution, top/bottom
✅ **Valuation:** PE/PB universal + Sector candlestick design
✅ **TA:** Stock TA + Sector TA (market breadth, trading value, signals)
✅ **Data:** 100% Parquet loading + ticker_details.json for sectors
✅ **UI:** 100% Plotly, modern design, responsive

### Timeline

- **Week 1:** FA pages (Company, Bank, Securities) + Sector tabs
- **Week 2:** Valuation (Individual + Sector candlestick)
- **Week 3:** TA (Stock + Screening + Market + **Sector TA**)
- **Week 4:** Polish & Deploy

### Success Criteria

- ✅ <2s page load
- ✅ 80% reduction in data queries
- ✅ 0 code duplication
- ✅ Individual + Sector analysis working
- ✅ Sector candlestick matching bank_dashboard.py design

---

**🚀 Ready to implement! All requirements covered in 1 document.**

**Last Updated:** 2025-12-12
**Version:** 3.0 FINAL
