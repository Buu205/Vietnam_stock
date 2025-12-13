# 🎨 Streamlit UI/UX Redesign - FINAL PLAN

**Date:** 2025-12-12
**Version:** 2.0 FINAL
**Status:** ✅ Ready for Implementation

---

## 📊 Executive Summary

### What We're Building
**Modern, unified Streamlit dashboard** với:
- ✅ 100% Plotly (bỏ PyEcharts)
- ✅ Parquet-only data loading
- ✅ Component library (no duplication)
- ✅ Sector classification từ `ticker_details.json`
- ✅ Modern UI/UX

### Page Structure
**7 pages, 4 categories:**
1. **FA:** Company, Bank, Securities (3 pages)
2. **Valuation:** Universal PE/PB + Sector view (1 page)
3. **TA:** Consolidated technical + Commodity/Macro (1 page)
4. **Intelligence:** Forecasts, News (2 pages)

---

## 🗂️ Data Architecture

### Ticker Classification (`ticker_details.json`)

**File:** `/Users/buuphan/Dev/Vietnam_dashboard/config/metadata/ticker_details.json`

**Structure:**
```json
{
  "VNM": {
    "entity": "COMPANY",
    "sector": "Thực phẩm và đồ uống"
  },
  "ACB": {
    "entity": "BANK",
    "sector": "Ngân hàng"
  },
  "SSI": {
    "entity": "SECURITY",
    "sector": "Dịch vụ tài chính"
  }
}
```

**Entities:**
- **BANK:** 24 tickers
- **COMPANY:** 390 tickers
- **SECURITY:** 37 tickers
- **INSURANCE:** 6 tickers (không hiển thị)

**Sectors (19 total):**
```
1. Ngân hàng
2. Bất động sản
3. Dịch vụ tài chính
4. Thực phẩm và đồ uống
5. Công nghệ Thông tin
6. Xây dựng và Vật liệu
7. Tài nguyên Cơ bản
8. Hàng & Dịch vụ Công nghiệp
9. Bán lẻ
10. Y tế
11. Viễn thông
12. Truyền thông
13. Du lịch và Giải trí
14. Hóa chất
15. Dầu khí
16. Điện, nước & xăng dầu khí đốt
17. Ô tô và phụ tùng
18. Hàng cá nhân & Gia dụng
19. Bảo hiểm
```

### Data Flow Architecture

```
┌─────────────────────────────────────────────┐
│ CONFIGURATION                               │
│ config/metadata/ticker_details.json        │
│ - Entity classification                     │
│ - Sector mapping                            │
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
│ │   └── ps/*.parquet (company only)        │
│ └── technical/                             │
│     ├── basic_data.parquet                 │
│     └── market_breadth.parquet             │
└────────────────┬────────────────────────────┘
                 │
                 ↓ Read parquet (ONLY)
┌─────────────────────────────────────────────┐
│ STREAMLIT (Dashboard Pages)               │
│ - Loads data from parquet                  │
│ - Uses ticker_details.json for sectors    │
│ - Renders with Plotly charts              │
└─────────────────────────────────────────────┘
```

---

## 📄 Page Details

### 1. Fundamental Analysis (3 pages)

#### 1.1 Company Analysis
**Entity:** COMPANY (390 tickers)
**Sectors:** 18 sectors (excluding Ngân hàng)

**Tabs:**
1. Overview - Key metrics
2. Income Statement - CIS metrics
3. Balance Sheet - CBS metrics
4. Cash Flow - CCS metrics
5. Financial Ratios - ROE, ROA, margins

**Sector Filter:**
```python
# Load ticker_details.json
with open('config/metadata/ticker_details.json') as f:
    ticker_details = json.load(f)

# Get company symbols by sector
sector_filter = st.selectbox("Sector", [
    "Tất cả",
    "Bất động sản",
    "Công nghệ Thông tin",
    "Thực phẩm và đồ uống",
    # ... etc
])

if sector_filter != "Tất cả":
    company_symbols = [
        ticker for ticker, info in ticker_details.items()
        if info['entity'] == 'COMPANY' and info['sector'] == sector_filter
    ]
else:
    company_symbols = [
        ticker for ticker, info in ticker_details.items()
        if info['entity'] == 'COMPANY'
    ]
```

---

#### 1.2 Banking Analysis
**Entity:** BANK (24 tickers)
**Sector:** Ngân hàng

**Tabs:**
1. Overview - Banking KPIs
2. Income Statement - BIS metrics (NII, provisions)
3. Balance Sheet - BBS metrics (Loans, deposits)
4. Banking Ratios - NIM, CIR, CAR, NPL, LDR
5. Credit Analysis - Loan growth, asset quality

**Bank List:**
```python
# Get all banks from ticker_details.json
banks = [
    ticker for ticker, info in ticker_details.items()
    if info['entity'] == 'BANK'
]
# ['VCB', 'TCB', 'ACB', 'MBB', ...]
```

---

#### 1.3 Securities Analysis
**Entity:** SECURITY (37 tickers)
**Sector:** Dịch vụ tài chính

**Tabs:**
1. Overview - Securities KPIs
2. Income Statement - SIS metrics (Brokerage, Investment income)
3. Balance Sheet - SBS metrics (Client deposits, Proprietary)
4. Securities Ratios - ROE, ROA, Revenue mix
5. Market Share - Trading volume, client accounts

**Securities List:**
```python
# Get all securities from ticker_details.json
securities = [
    ticker for ticker, info in ticker_details.items()
    if info['entity'] == 'SECURITY'
]
# ['SSI', 'VND', 'HCM', ...]
```

---

### 2. Valuation Dashboard (1 page)

**Universal for ALL entities** (Company + Bank + Security)

**Data Sources:**
```python
# Universal (all stocks)
pe_df = pd.read_parquet('DATA/processed/valuation/pe/pe_historical_all_symbols_final.parquet')
pb_df = pd.read_parquet('DATA/processed/valuation/pb/pb_historical_all_symbols_final.parquet')

# Company only
ev_df = pd.read_parquet('DATA/processed/valuation/ev_ebitda/ev_ebitda_historical.parquet')
ps_df = pd.read_parquet('DATA/processed/valuation/ps/ps_historical.parquet')  # NEW
```

**Tabs:**

#### Tab 1: Stock Valuation (Individual)
**For ALL stocks:**
- PE candlestick (design từ bank_dashboard.py)
- PB candlestick
- Historical percentiles
- Current vs Median

**For COMPANY only:**
- PS Ratio trend (NEW)
- EV/EBITDA trend

**Sidebar:**
```python
# Entity filter
entity_type = st.selectbox("Entity Type", ["All", "COMPANY", "BANK", "SECURITY"])

# Sector filter (based on entity)
if entity_type == "COMPANY":
    sectors = ["Tất cả", "Bất động sản", "Công nghệ Thông tin", ...]
elif entity_type == "BANK":
    sectors = ["Ngân hàng"]
elif entity_type == "SECURITY":
    sectors = ["Dịch vụ tài chính"]

sector = st.selectbox("Sector", sectors)

# Symbol filter
symbols = get_symbols_by_entity_sector(entity_type, sector, ticker_details)
symbol = st.selectbox("Symbol", symbols)
```

---

#### Tab 2: Sector Valuation (Cross-sector)
**Design:** Candlestick chart giống bank_dashboard.py nhưng cho **TẤT CẢ sectors**

**Sector Selection:**
```python
# Allow multiple sector comparison
selected_sectors = st.multiselect(
    "Select Sectors to Compare",
    options=[
        "Ngân hàng",
        "Bất động sản",
        "Công nghệ Thông tin",
        "Dịch vụ tài chính",
        "Thực phẩm và đồ uống",
        # ... etc
    ],
    default=["Ngân hàng", "Bất động sản", "Công nghệ Thông tin"]
)
```

**Chart: Sector PE Distribution**
```python
fig = go.Figure()

for sector in selected_sectors:
    # Get all tickers in sector
    sector_tickers = [
        ticker for ticker, info in ticker_details.items()
        if info['sector'] == sector
    ]

    # For each ticker, create candlestick
    for ticker in sector_tickers:
        ticker_data = pe_df[pe_df['symbol'] == ticker]['pe_ratio'].dropna()

        if len(ticker_data) < 20:
            continue

        # Calculate percentiles (same as bank_dashboard.py)
        p5 = ticker_data.quantile(0.05)
        p25 = ticker_data.quantile(0.25)
        p50 = ticker_data.quantile(0.50)
        p75 = ticker_data.quantile(0.75)
        p95 = ticker_data.quantile(0.95)

        current_val = ticker_data.iloc[-1]

        # Add candlestick (grey)
        fig.add_trace(go.Candlestick(
            x=[ticker],
            open=[p25], high=[p95], low=[p5], close=[p75],
            increasing_line_color='lightgrey',
            decreasing_line_color='lightgrey',
            showlegend=False
        ))

        # Add current value (red dot)
        fig.add_trace(go.Scatter(
            x=[ticker],
            y=[current_val],
            mode='markers',
            marker=dict(size=8, color='#A95C68'),
            showlegend=False,
            hovertemplate=(
                f"<b>{ticker}</b> ({sector})<br>" +
                f"Current: {current_val:.2f}<br>" +
                f"Median: {p50:.2f}<br>"
            )
        ))

fig.update_layout(
    title='PE Distribution by Sector',
    xaxis_title='Ticker (Grouped by Sector)',
    yaxis_title='PE Ratio'
)
```

**Sector Heatmap:**
```python
# Average PE by sector
sector_pe = pe_df.merge(
    pd.DataFrame(ticker_details).T,
    left_on='symbol',
    right_index=True
).groupby('sector')['pe_ratio'].agg(['median', 'mean', 'std'])

fig = pcb.heatmap(
    data=sector_pe,
    title='Sector PE Heatmap',
    colorscale='RdYlGn_r'  # Red = expensive, Green = cheap
)
```

---

#### Tab 3: VN-Index Valuation
- VN-Index PE trend
- Historical percentiles
- Bull/Bear zones

---

#### Tab 4: Fair Value Calculator
- DCF inputs
- Peer multiple comparison

---

### 3. Technical Analysis Dashboard (1 page)

**Consolidated TA page với 4 tabs**

#### Tab 1: Stock Technical
**Individual stock TA:**
- Candlestick + Volume
- MA overlay (20/50/100/200)
- RSI, MACD
- Bollinger Bands

---

#### Tab 2: TA Screening (Signal Tables)
**User's key request: "signal tables, screening, components phụ"**

**Tables:**

**1. MA Alignment Signals**
```python
ma_signals = []

for symbol in all_symbols:
    latest = tech_df[tech_df['symbol'] == symbol].iloc[-1]

    price = latest['close']
    ma20 = latest['ma_20']
    ma50 = latest['ma_50']
    ma100 = latest['ma_100']
    ma200 = latest['ma_200']

    # Check alignment
    bullish = (price > ma20 > ma50 > ma100 > ma200)
    bearish = (price < ma20 < ma50 < ma100 < ma200)

    # Get sector from ticker_details
    sector = ticker_details.get(symbol, {}).get('sector', 'N/A')

    ma_signals.append({
        'Symbol': symbol,
        'Sector': sector,
        'Price': price,
        'MA20': ma20,
        'Signal': '🟢 Bullish' if bullish else ('🔴 Bearish' if bearish else '⚪ Neutral')
    })

# Display as sortable/filterable table
df_signals = pd.DataFrame(ma_signals)

# Sector filter
sector_filter = st.multiselect("Filter by Sector", df_signals['Sector'].unique())
if sector_filter:
    df_signals = df_signals[df_signals['Sector'].isin(sector_filter)]

st.dataframe(df_signals, use_container_width=True)
```

**2. RSI Signals**
```python
# Oversold: RSI < 30 (buy)
# Overbought: RSI > 70 (sell)
```

**3. MACD Signals**
```python
# Bullish cross, Bearish cross
```

**4. Combined Score**
```python
# Aggregate all signals (-5 to +5)
combined_signals = []

for symbol in all_symbols:
    score = calculate_ta_score(symbol, tech_df)  # Returns -5 to +5
    sector = ticker_details.get(symbol, {}).get('sector', 'N/A')

    combined_signals.append({
        'Symbol': symbol,
        'Sector': sector,
        'Score': score,
        'Signal': (
            '🟢 Strong Buy' if score >= 3 else
            '🔵 Buy' if score >= 1 else
            '🔴 Sell' if score <= -1 else
            '⚪ Neutral'
        )
    })

# Display
df_combined = pd.DataFrame(combined_signals).sort_values('Score', ascending=False)
st.dataframe(df_combined, use_container_width=True)

# Filter by signal
signal_filter = st.multiselect("Filter by Signal", ['🟢 Strong Buy', '🔵 Buy', '🔴 Sell', '⚪ Neutral'])
if signal_filter:
    df_combined = df_combined[df_combined['Signal'].isin(signal_filter)]
```

---

#### Tab 3: Market Technical
**Market breadth indicators:**
- Advance/Decline line
- % stocks above MA20/50/100/200
- New 52-week highs/lows
- Sector rotation heatmap
- VN-Index RSI/MACD

---

#### Tab 4: Commodity & Macro
**User's request: "các chỉ số commodity hay macro cần theo dõi mỗi ngày"**

**Data Sources:**
```python
# Commodity prices
gold_df = pd.read_parquet('DATA/processed/commodity/gold.parquet')
oil_df = pd.read_parquet('DATA/processed/commodity/oil.parquet')

# Macro indicators
usd_vnd_df = pd.read_parquet('DATA/processed/macro/exchange_rate.parquet')
interest_df = pd.read_parquet('DATA/processed/macro/interest_rates.parquet')
```

**Layout:**
```python
# KPI cards row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Gold (USD/oz)", f"${gold_price:,.0f}", f"{gold_change:+.2f}%")

with col2:
    st.metric("Oil Brent (USD/bbl)", f"${oil_price:.2f}", f"{oil_change:+.2f}%")

with col3:
    st.metric("USD/VND", f"{usd_vnd:,.0f}", f"{usd_vnd_change:+.2f}%")

with col4:
    st.metric("VN-Index", f"{vnindex:.2f}", f"{vnindex_change:+.2f}%")

# Charts
col1, col2 = st.columns(2)

with col1:
    # Gold chart with MA
    fig = pcb.line_chart(
        df=gold_df,
        x_col='date',
        y_cols=['price', 'ma_20', 'ma_50'],
        title='Gold Price Trend'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Oil chart
    fig = pcb.line_chart(
        df=oil_df,
        x_col='date',
        y_cols=['brent', 'wti'],
        title='Oil Price Trend'
    )
    st.plotly_chart(fig, use_container_width=True)

# USD/VND exchange rate
fig = pcb.line_chart(
    df=usd_vnd_df,
    x_col='date',
    y_cols=['usd_vnd'],
    title='USD/VND Exchange Rate'
)
st.plotly_chart(fig, use_container_width=True)
```

---

### 4. Market Intelligence (2 pages)

#### 4.1 Analyst Forecasts
**BSC forecasts, target prices**

#### 4.2 News & Sentiment
**News feed, sentiment analysis**

---

## 🎨 Modern UI/UX Design

### Design Principles
1. **Clean & Minimal** - White space, card-based layout
2. **Responsive** - Works on desktop/tablet/mobile
3. **Interactive** - Hover tooltips, click filters
4. **Fast** - <2s load time, smooth transitions
5. **Accessible** - Clear labels, color-blind friendly

### Color Palette
```python
COLORS = {
    'primary': '#1E40AF',      # Deep blue (buttons, links)
    'secondary': '#10B981',    # Green (positive values)
    'accent': '#F59E0B',       # Amber (warnings)
    'danger': '#EF4444',       # Red (negative values, alerts)
    'neutral': '#6B7280',      # Grey (text)
    'background': '#F9FAFB',   # Light grey (page background)
    'card': '#FFFFFF',         # White (card background)
}
```

### Typography
```python
FONTS = {
    'primary': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    'heading': 'Inter, sans-serif',
    'mono': 'SF Mono, Monaco, Consolas, monospace'
}
```

### Component Styling
```python
# Global CSS
st.markdown("""
<style>
/* Card style */
.stMetric {
    background-color: #FFFFFF;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Chart container */
.stPlotlyChart {
    background-color: #FFFFFF;
    border-radius: 0.5rem;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Table style */
.stDataFrame {
    border-radius: 0.5rem;
}

/* Button style */
.stButton > button {
    background-color: #1E40AF;
    color: white;
    border-radius: 0.375rem;
    padding: 0.5rem 1rem;
    transition: all 0.2s;
}

.stButton > button:hover {
    background-color: #1E3A8A;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)
```

### Layout Pattern
```python
# Page header
st.title("📊 Page Title")
st.caption("Last updated: 2025-12-12 | Data source: parquet_file.parquet")

st.divider()

# Main content
tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

with tab1:
    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Metric 1", "Value", "Change")
    # ...

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

# Footer
st.divider()
st.caption("© 2025 Vietnam Stock Dashboard")
```

---

## 📅 Implementation Timeline (20 days)

### Phase 1: FA Pages (5 days)
- Day 1-2: Company Analysis
- Day 3: Banking Analysis
- Day 4: Securities Analysis
- Day 5: Testing

### Phase 2: Valuation (5 days)
- Day 6-7: Core charts (PE/PB candlestick)
- Day 8: Sector comparison
- Day 9: PS/EV for company
- Day 10: Testing

### Phase 3: TA (5 days)
- Day 11: Stock TA tab
- Day 12-13: Screening tables (signal tables)
- Day 14: Market breadth
- Day 15: Commodity & Macro

### Phase 4: Polish (5 days)
- Day 16: Forecasts
- Day 17: News
- Day 18: UI/UX polish
- Day 19: Performance
- Day 20: Testing

---

## ✅ Success Criteria

### Technical
- ✅ 100% Plotly (no PyEcharts in new pages)
- ✅ <2s page load
- ✅ Parquet-only loading
- ✅ Sector classification từ ticker_details.json
- ✅ PE/PB candlestick matching bank_dashboard.py

### Functional
- ✅ 7 pages working
- ✅ All entities (Company, Bank, Security)
- ✅ All 19 sectors supported
- ✅ TA signal tables with scoring
- ✅ Commodity & Macro tracking

### UX
- ✅ Modern, clean design
- ✅ Responsive (mobile/tablet/desktop)
- ✅ Fast, smooth interactions
- ✅ Intuitive navigation

---

## 📁 File Structure (Final)

```
/Users/buuphan/Dev/Vietnam_dashboard/

📄 Documentation
├── STREAMLIT_INDEX.md                     # Navigation guide
├── STREAMLIT_REDESIGN_FINAL.md           # This file
├── streamlit_ui_redesign_plan_v2.md      # Detailed plan
└── QUICK_START_STREAMLIT_REDESIGN.md     # Quick start

🧩 Components
WEBAPP/components/
├── charts/plotly_builders.py             # 7 chart methods
├── navigation/main_nav.py                # Category nav
├── inputs/symbol_selector.py             # Symbol dropdown
└── data_display/metric_cards.py          # KPI cards

📊 Pages
WEBAPP/pages/
├── 1_fundamental/
│   ├── company_analysis.py               # COMPANY (390 tickers)
│   ├── banking_analysis.py               # BANK (24 tickers)
│   └── securities_analysis.py            # SECURITY (37 tickers)
├── 2_valuation/
│   └── valuation_dashboard.py            # PE/PB universal + Sector view
├── 3_technical/
│   └── technical_dashboard.py            # 4 tabs: Stock/Screening/Market/Macro
└── 4_intelligence/
    ├── analyst_forecasts.py              # BSC forecasts
    └── news_sentiment.py                 # News & sentiment

🗂️ Configuration
config/metadata/
└── ticker_details.json                   # Entity & Sector classification
```

---

## 🚀 Quick Start

### 1. Test Demo Page
```bash
streamlit run WEBAPP/pages/1_fundamental/company_analysis_demo.py
```

### 2. Start Building
```bash
# Copy demo as template
cp WEBAPP/pages/1_fundamental/company_analysis_demo.py \
   WEBAPP/pages/1_fundamental/company_analysis.py

# Edit and customize
# Add sector filtering using ticker_details.json
```

### 3. Load Sector Data
```python
import json

# Load ticker classification
with open('config/metadata/ticker_details.json') as f:
    ticker_details = json.load(f)

# Get company symbols in "Thực phẩm và đồ uống" sector
food_companies = [
    ticker for ticker, info in ticker_details.items()
    if info['entity'] == 'COMPANY' and info['sector'] == 'Thực phẩm và đồ uống'
]
# ['VNM', 'MSN', 'SAB', ...]
```

---

## 💡 Key Integration Points

### 1. Sector Classification
```python
# Always use ticker_details.json for sector info
def get_ticker_sector(symbol):
    with open('config/metadata/ticker_details.json') as f:
        ticker_details = json.load(f)
    return ticker_details.get(symbol, {}).get('sector', 'N/A')

# Use in filtering
sector_filter = st.selectbox("Sector", sectors)
filtered_symbols = [
    ticker for ticker, info in ticker_details.items()
    if info['sector'] == sector_filter
]
```

### 2. Parquet Data Loading
```python
# Always read from processed parquet
@st.cache_data(ttl=3600)
def load_company_data(symbol):
    path = DataPaths.fundamental('company')
    df = pd.read_parquet(path)
    return df[df['symbol'] == symbol]
```

### 3. Valuation Candlestick
```python
# Use design from bank_dashboard.py (line 1658-1807)
from WEBAPP.pages.bank_dashboard import create_valuation_candlestick

fig = create_valuation_candlestick(
    df=pe_df,
    symbols=banking_symbols,
    metric_type='pe'
)
```

---

## 📞 Resources

- **Documentation:** `STREAMLIT_INDEX.md` (start here)
- **Component API:** `WEBAPP/components/README.md`
- **Full Plan:** `streamlit_ui_redesign_plan_v2.md`
- **Ticker Data:** `config/metadata/ticker_details.json`
- **Bank Dashboard Reference:** `WEBAPP/pages/bank_dashboard.py`

---

**Status:** ✅ Ready for Implementation
**Next:** Start Phase 1 - Build 3 FA pages

**Có câu hỏi gì hỏi tôi nhé!** 🚀
