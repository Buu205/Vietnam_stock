# 🎨 Streamlit UI/UX Redesign - COMPLETE GUIDE

**Version:** 2.1 FINAL (with Sector Analysis)
**Date:** 2025-12-12
**Status:** ✅ Ready for Implementation

---

## 📊 User Requirements Summary

Dựa trên tất cả yêu cầu của bạn, đây là final design:

### 1. **Entity Types** (3 loại)
- ✅ Company (390 tickers)
- ✅ Bank (24 tickers)
- ✅ Securities (37 tickers)
- ❌ Insurance (bỏ qua)

### 2. **Analysis Levels** (2 levels)
- ✅ **Individual Level:** FA/TA từng cổ phiếu riêng lẻ
- ✅ **Sector Level:** FA/TA theo ngành (NEW requirement)

### 3. **Key Features**
- ✅ Valuation universal (PE/PB cho tất cả)
- ✅ PS và EV/EBITDA chỉ cho Company
- ✅ PE/PB candlestick design từ bank_dashboard.py
- ✅ TA signal tables với screening
- ✅ **Sector analysis:** Market breadth, trading value, dòng tiền
- ✅ Commodity & Macro daily tracking

---

## 🏗️ Complete Page Structure (7 Pages)

### **Category 1: 📊 Fundamental Analysis** - 3 Pages

#### Page 1.1: Company Analysis
**File:** `WEBAPP/pages/1_fundamental/company_analysis.py`

**2 Analysis Levels:**

##### Level 1: Individual Stock Analysis (Tab 1-5)
```python
# Sidebar: Symbol selector
symbol = st.selectbox("Select Company", company_symbols)
```

**Tabs:**
1. **Overview** - Key metrics dashboard
2. **Income Statement** - CIS metrics
3. **Balance Sheet** - CBS metrics
4. **Cash Flow** - CCS metrics
5. **Financial Ratios** - ROE, ROA, margins

##### Level 2: Sector Analysis (Tab 6 - NEW)
```python
# Tab 6: Sector Comparison
st.subheader("Sector-level Analysis")

# Sidebar: Sector selector
sector = st.selectbox("Select Sector", [
    "Bất động sản",
    "Công nghệ Thông tin",
    "Thực phẩm và đồ uống",
    # ... 16 sectors total
])

# Get all companies in sector
sector_companies = [
    ticker for ticker, info in ticker_details.items()
    if info['entity'] == 'COMPANY' and info['sector'] == sector
]
```

**Sector-Level Charts:**

**1. Sector Average Metrics**
```python
# Calculate sector averages
sector_df = company_df[company_df['symbol'].isin(sector_companies)]

sector_avg = sector_df.groupby('quarter').agg({
    'net_revenue': 'mean',
    'ebitda_margin': 'mean',
    'roe': 'mean',
    'debt_to_equity': 'mean'
}).reset_index()

# Chart: Sector average trends
fig = pcb.line_chart(
    df=sector_avg,
    x_col='quarter',
    y_cols=['ebitda_margin', 'roe'],
    title=f'Sector Average Metrics - {sector}'
)
```

**2. Sector Heatmap (Cross-stock comparison)**
```python
# Latest quarter data for all stocks in sector
latest = sector_df[sector_df['quarter'] == sector_df['quarter'].max()]

# Pivot table: Stocks (rows) x Metrics (columns)
heatmap_data = latest.pivot_table(
    index='symbol',
    values=['roe', 'ebitda_margin', 'revenue_growth_yoy', 'debt_to_equity']
)

# Heatmap
fig = pcb.heatmap(
    data=heatmap_data,
    title=f'Sector Metrics Heatmap - {sector}',
    x_label='Metrics',
    y_label='Company',
    colorscale='RdYlGn'  # Red = bad, Green = good
)
```

**3. Sector Distribution (Box plot)**
```python
# Distribution of key metrics across sector
fig = go.Figure()

for metric in ['roe', 'ebitda_margin', 'revenue_growth_yoy']:
    fig.add_trace(go.Box(
        y=latest[metric],
        name=metric,
        boxmean='sd'  # Show mean and std dev
    ))

fig.update_layout(title=f'Sector Metrics Distribution - {sector}')
```

**4. Top/Bottom Performers**
```python
# Top 5 by ROE
top_roe = latest.nlargest(5, 'roe')[['symbol', 'roe', 'revenue_growth_yoy']]
st.subheader("Top 5 by ROE")
st.dataframe(top_roe)

# Bottom 5 by Debt/Equity
bottom_de = latest.nsmallest(5, 'debt_to_equity')[['symbol', 'debt_to_equity']]
st.subheader("Lowest Debt/Equity")
st.dataframe(bottom_de)
```

---

#### Page 1.2: Banking Analysis
**File:** `WEBAPP/pages/1_fundamental/banking_analysis.py`

**Same structure:**
- Tab 1-5: Individual bank analysis
- **Tab 6: Banking Sector Analysis (NEW)**
  - Sector average NIM, CAR, NPL
  - Bank heatmap (CAR, NPL, LDR, CIR)
  - Top banks by NIM/ROE
  - Asset quality comparison

---

#### Page 1.3: Securities Analysis
**File:** `WEBAPP/pages/1_fundamental/securities_analysis.py`

**Same structure:**
- Tab 1-5: Individual security analysis
- **Tab 6: Securities Sector Analysis (NEW)**
  - Sector average brokerage revenue
  - Market share distribution
  - Revenue mix comparison
  - Top performers by ROE

---

### **Category 2: 💰 Valuation Analysis** - 1 Page

#### Page 2.1: Valuation Dashboard
**File:** `WEBAPP/pages/2_valuation/valuation_dashboard.py`

**4 Tabs:**

##### Tab 1: Stock Valuation (Individual)
- PE/PB candlestick (for ALL stocks)
- PS/EV (for Company only)
- Historical percentiles

##### Tab 2: Sector Valuation (NEW - matching your requirement)
**Design:** PE/PB candlestick chart giống bank_dashboard.py, nhưng cho **tất cả sectors**

```python
# Sidebar: Multi-sector selection
selected_sectors = st.multiselect(
    "Select Sectors to Compare",
    options=[
        "Ngân hàng",
        "Bất động sản",
        "Công nghệ Thông tin",
        "Dịch vụ tài chính",
        "Thực phẩm và đồ uống",
        # ... all 19 sectors
    ],
    default=["Ngân hàng", "Bất động sản"]
)

# Get all tickers in selected sectors
sector_tickers = {}
for sector in selected_sectors:
    sector_tickers[sector] = [
        ticker for ticker, info in ticker_details.items()
        if info['sector'] == sector
    ]

# Create PE candlestick chart (design from bank_dashboard.py)
fig = go.Figure()

for sector, tickers in sector_tickers.items():
    for ticker in tickers:
        ticker_data = pe_df[pe_df['symbol'] == ticker]['pe_ratio'].dropna()

        if len(ticker_data) < 20:
            continue

        # Calculate percentiles (same as bank_dashboard.py line 1746-1751)
        p5 = ticker_data.quantile(0.05)
        p25 = ticker_data.quantile(0.25)
        p50 = ticker_data.quantile(0.50)
        p75 = ticker_data.quantile(0.75)
        p95 = ticker_data.quantile(0.95)

        current_val = ticker_data.iloc[-1]
        percentile = np.sum(ticker_data <= current_val) / len(ticker_data) * 100

        # Add candlestick (grey box)
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
                f"Median: {p50:.2f}<br>"
            )
        ))

fig.update_layout(
    title='PE Distribution by Sector',
    xaxis_title='Ticker (Grouped by Sector)',
    yaxis_title='PE Ratio',
    height=600
)
```

**Sector Average PE/PB:**
```python
# Calculate sector median PE/PB
sector_summary = []

for sector in selected_sectors:
    sector_tickers_list = sector_tickers[sector]
    sector_pe = pe_df[pe_df['symbol'].isin(sector_tickers_list)]['pe_ratio']

    sector_summary.append({
        'Sector': sector,
        'Median PE': sector_pe.median(),
        'Mean PE': sector_pe.mean(),
        '# Stocks': len(sector_tickers_list),
        'Min PE': sector_pe.min(),
        'Max PE': sector_pe.max()
    })

# Display as table
st.dataframe(pd.DataFrame(sector_summary))

# Bar chart: Sector median PE
fig = pcb.bar_chart(
    df=pd.DataFrame(sector_summary),
    x_col='Sector',
    y_col='Median PE',
    title='Sector Median PE Comparison'
)
```

##### Tab 3: VN-Index Valuation
##### Tab 4: Fair Value Calculator

---

### **Category 3: 📈 Technical Analysis** - 1 Page

#### Page 3.1: Technical Dashboard
**File:** `WEBAPP/pages/3_technical/technical_dashboard.py`

**5 Tabs:**

##### Tab 1: Stock Technical (Individual)
**Single stock TA:**
- Candlestick + Volume
- MA overlay
- RSI, MACD
- Bollinger Bands

---

##### Tab 2: TA Screening (Signal Tables)
**Individual stock screening:**
- MA Alignment Signals
- RSI Signals
- MACD Signals
- Combined Score

**With Sector Filtering:**
```python
# Get all symbols with sector info
screening_data = []

for symbol in all_symbols:
    ta_score = calculate_ta_score(symbol, tech_df)
    sector = ticker_details.get(symbol, {}).get('sector', 'N/A')

    screening_data.append({
        'Symbol': symbol,
        'Sector': sector,
        'TA Score': ta_score,
        'Signal': get_signal_label(ta_score)
    })

df_screening = pd.DataFrame(screening_data)

# Sector filter
sector_filter = st.multiselect("Filter by Sector", df_screening['Sector'].unique())
if sector_filter:
    df_screening = df_screening[df_screening['Sector'].isin(sector_filter)]

# Display
st.dataframe(df_screening.sort_values('TA Score', ascending=False))
```

---

##### Tab 3: Market Breadth (Market-wide)
**From technical_dashboard.py:**

**1. Market Breadth Chart**
```python
# % stocks above MA20/MA50/MA100
# Reference: technical_dashboard.py line 182-363
render_market_breadth_chart()
```

**2. Sector Breadth Table**
```python
# Reference: technical_dashboard.py line 454-
render_sector_breadth_table()
```

---

##### Tab 4: Sector TA Analysis (NEW - Your key requirement)
**"TA các cổ phiếu trong ngành"**

```python
st.subheader("Sector Technical Analysis")

# Sector selector
sector = st.selectbox("Select Sector", all_sectors)

# Get all stocks in sector
sector_stocks = [
    ticker for ticker, info in ticker_details.items()
    if info['sector'] == sector
]

st.write(f"**{len(sector_stocks)} stocks in {sector} sector**")
```

**Chart 1: Số lượng CP > MA20/MA50 trong ngành**
```python
# Calculate % stocks above MA in sector
sector_tech_df = tech_df[tech_df['symbol'].isin(sector_stocks)]

sector_ma_breadth = sector_tech_df.groupby('date').apply(lambda x: {
    'above_ma20': (x['close'] > x['ma_20']).sum() / len(x) * 100,
    'above_ma50': (x['close'] > x['ma_50']).sum() / len(x) * 100,
    'above_ma100': (x['close'] > x['ma_100']).sum() / len(x) * 100
}).apply(pd.Series)

# Chart
fig = pcb.line_chart(
    df=sector_ma_breadth.reset_index(),
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

**Chart 2: Dòng tiền theo ngành (Trading Value)**
```python
# Reference: technical_dashboard.py line 367-453
# Trading value by sector over time

# Get trading value data for sector
sector_trading = []

for date in unique_dates:
    daily_df = tech_df[tech_df['date'] == date]
    sector_daily = daily_df[daily_df['symbol'].isin(sector_stocks)]

    # Calculate total trading value for sector
    trading_value = (sector_daily['close'] * sector_daily['volume']).sum()

    sector_trading.append({
        'date': date,
        'trading_value': trading_value
    })

df_trading = pd.DataFrame(sector_trading)

# Calculate change
df_trading['change_5d'] = df_trading['trading_value'].pct_change(5) * 100
df_trading['change_20d'] = df_trading['trading_value'].pct_change(20) * 100

# Chart: Trading value trend
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_trading['date'],
    y=df_trading['trading_value'] / 1e9,  # Convert to billions
    name='Trading Value',
    marker=dict(
        color=df_trading['change_5d'],
        colorscale='RdYlGn',
        showscale=True
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
col1.metric(
    "Latest Trading Value",
    f"{latest_tv['trading_value']/1e9:.2f}B"
)
col2.metric(
    "Change 5D",
    f"{latest_tv['change_5d']:+.1f}%"
)
col3.metric(
    "Change 20D",
    f"{latest_tv['change_20d']:+.1f}%"
)
```

**Chart 3: Sector TA Signals Summary**
```python
# Calculate TA scores for all stocks in sector
sector_signals = []

for symbol in sector_stocks:
    ta_score = calculate_ta_score(symbol, tech_df)

    sector_signals.append({
        'Symbol': symbol,
        'TA Score': ta_score,
        'Signal': get_signal_label(ta_score)
    })

df_signals = pd.DataFrame(sector_signals)

# Summary: Count by signal type
signal_counts = df_signals['Signal'].value_counts()

# Pie chart
fig = go.Figure(data=[go.Pie(
    labels=signal_counts.index,
    values=signal_counts.values,
    hole=0.4
)])

fig.update_layout(title=f'TA Signal Distribution - {sector} Sector')
st.plotly_chart(fig, use_container_width=True)

# Table: All stocks
st.subheader(f"All Stocks in {sector} Sector")
st.dataframe(
    df_signals.sort_values('TA Score', ascending=False),
    use_container_width=True
)
```

**Chart 4: Sector Momentum (Average RSI/MACD)**
```python
# Calculate sector average RSI and MACD
sector_momentum = sector_tech_df.groupby('date').agg({
    'rsi_14': 'mean',
    'macd': 'mean',
    'macd_signal': 'mean'
}).reset_index()

# RSI Chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=sector_momentum['date'],
    y=sector_momentum['rsi_14'],
    name='Sector Avg RSI',
    line=dict(color='#1E40AF')
))

# Add overbought/oversold zones
fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")

fig.update_layout(
    title=f'Sector Average RSI - {sector}',
    yaxis_title='RSI'
)

st.plotly_chart(fig, use_container_width=True)
```

---

##### Tab 5: Commodity & Macro
**Daily tracking:**
- Gold, Oil, USD/VND
- Interest rates
- VN-Index

---

### **Category 4: 🔍 Market Intelligence** - 2 Pages

#### Page 4.1: Analyst Forecasts
#### Page 4.2: News & Sentiment

---

## 📊 Complete Feature Matrix

| Page | Individual Analysis | Sector Analysis | Key Charts |
|------|-------------------|-----------------|------------|
| **Company FA** | ✅ CIS/CBS/CCS metrics | ✅ Sector avg, heatmap, distribution | Revenue, margins, ratios |
| **Bank FA** | ✅ BIS/BBS metrics | ✅ Sector avg, CAR/NPL comparison | NIM, CAR, NPL, LDR |
| **Securities FA** | ✅ SIS/SBS metrics | ✅ Sector market share | Brokerage revenue, ROE |
| **Valuation** | ✅ PE/PB/PS/EV | ✅ Sector PE/PB candlestick | Distribution, percentiles |
| **TA** | ✅ Candlestick, indicators | ✅ Market breadth, trading value, signals | MA, RSI, MACD, volume |

---

## 🗂️ Data Files Required

### From ticker_details.json
```python
# Entity & Sector classification
{
  "VNM": {"entity": "COMPANY", "sector": "Thực phẩm và đồ uống"},
  "ACB": {"entity": "BANK", "sector": "Ngân hàng"},
  "SSI": {"entity": "SECURITY", "sector": "Dịch vụ tài chính"}
}
```

### Parquet Files
```
DATA/processed/
├── fundamental/
│   ├── company/company_financial_metrics.parquet
│   ├── bank/bank_financial_metrics.parquet
│   └── security/security_financial_metrics.parquet
│
├── valuation/
│   ├── pe/pe_historical_all_symbols_final.parquet
│   ├── pb/pb_historical_all_symbols_final.parquet
│   ├── ev_ebitda/ev_ebitda_historical.parquet
│   └── ps/ps_historical.parquet (NEW - for company only)
│
├── technical/
│   ├── basic_data.parquet (MA, RSI, MACD for all symbols)
│   ├── market_breadth_global.parquet
│   └── market_breadth/market_breadth_sector.parquet
│
├── commodity/
│   ├── gold.parquet
│   └── oil.parquet
│
└── macro/
    ├── exchange_rate.parquet
    └── interest_rates.parquet
```

---

## 🚀 Implementation Priority

### Phase 1: FA Pages with Sector Analysis (Week 1)
**Day 1-3:** Company Analysis
- Individual tabs (1-5)
- **Sector analysis tab (6)** - NEW

**Day 4:** Banking Analysis
- Individual tabs (1-5)
- **Sector analysis tab (6)** - NEW

**Day 5:** Securities Analysis
- Individual tabs (1-5)
- **Sector analysis tab (6)** - NEW

### Phase 2: Valuation with Sector View (Week 2)
**Day 6-7:** Individual stock valuation (PE/PB/PS/EV)

**Day 8-9:** **Sector valuation** (NEW)
- Sector PE/PB candlestick (design from bank_dashboard.py)
- Sector comparison heatmap
- Sector summary table

**Day 10:** Testing

### Phase 3: TA with Sector TA (Week 3)
**Day 11:** Stock technical (individual)

**Day 12:** TA screening tables

**Day 13:** Market breadth (market-wide)

**Day 14:** **Sector TA** (NEW - your key requirement)
- % stocks above MA by sector
- Trading value by sector (dòng tiền)
- Sector TA signals
- Sector momentum (avg RSI/MACD)

**Day 15:** Commodity & Macro

### Phase 4: Intelligence & Polish (Week 4)
**Day 16-17:** Forecasts, News
**Day 18-20:** UI/UX polish, performance, testing

---

## 💡 Key Code Patterns

### Loading Sector Data
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

# Example
banking_stocks = get_sector_stocks('Ngân hàng')
# ['VCB', 'TCB', 'ACB', ...]

tech_stocks = get_sector_stocks('Công nghệ Thông tin')
# ['FPT', 'CMG', ...]
```

### Sector Analysis Pattern
```python
# General pattern for sector analysis

def analyze_sector(sector, data_df):
    """Analyze metrics for all stocks in a sector"""

    # 1. Get sector stocks
    sector_stocks = get_sector_stocks(sector)

    # 2. Filter data
    sector_data = data_df[data_df['symbol'].isin(sector_stocks)]

    # 3. Calculate sector averages
    sector_avg = sector_data.groupby('date').agg({
        'metric1': 'mean',
        'metric2': 'mean',
        'metric3': 'median'
    })

    # 4. Calculate distributions
    latest = sector_data[sector_data['date'] == sector_data['date'].max()]
    p25 = latest['metric1'].quantile(0.25)
    median = latest['metric1'].quantile(0.50)
    p75 = latest['metric1'].quantile(0.75)

    return {
        'avg': sector_avg,
        'latest': latest,
        'stats': {'p25': p25, 'median': median, 'p75': p75}
    }
```

### Trading Value by Sector (Reference)
```python
# From technical_dashboard.py line 367-453
def render_trading_value_chart():
    """Trading Value by Sector"""

    sector_path = get_data_path(
        "DATA/processed/technical/market_breadth/market_breadth_sector.parquet"
    )

    df_latest = conn.execute("""
        SELECT
            sector,
            trading_value,
            trading_value_pct,
            trading_value_change_5d,
            trading_value_change_20d
        FROM read_parquet(?)
        WHERE date = (SELECT max(date) FROM read_parquet(?))
        ORDER BY trading_value DESC
        LIMIT 10
    """, [str(sector_path), str(sector_path)]).fetchdf()

    # Bar chart with color by change
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_latest['sector'],
        y=df_latest['trading_value'] / 1e9,
        marker=dict(
            color=df_latest['trading_value_change_5d'],
            colorscale='RdYlGn'
        )
    ))
```

---

## ✅ Final Checklist

### Must-Have Features
- [x] 3 FA pages (Company, Bank, Securities)
- [x] Sector-level FA analysis for each entity type
- [x] Universal Valuation (PE/PB for all)
- [x] Sector Valuation view (candlestick design)
- [x] PS/EV for company only
- [x] TA screening with signal tables
- [x] **Sector TA analysis** (market breadth, trading value, signals)
- [x] Commodity & Macro tracking
- [x] 100% Plotly (no PyEcharts)
- [x] Parquet-only data loading
- [x] Modern UI/UX

### Data Requirements
- [x] ticker_details.json (entity & sector classification)
- [x] Fundamental parquet files (company, bank, security)
- [x] Valuation parquet files (pe, pb, ev, ps)
- [x] Technical parquet files (basic_data, market_breadth, sector_breadth)
- [x] Commodity & Macro parquet files

---

## 📁 Files Summary

**Documentation (5 files):**
1. `STREAMLIT_INDEX.md` - Navigation guide
2. `STREAMLIT_UI_COMPLETE_GUIDE.md` - This file (complete reference)
3. `streamlit_ui_redesign_plan_v2.md` - Detailed plan
4. `STREAMLIT_REDESIGN_FINAL.md` - Architecture overview
5. `QUICK_START_STREAMLIT_REDESIGN.md` - Quick start

**Components (13 files):**
- `WEBAPP/components/` - All reusable components

**Demo Page (1 file):**
- `WEBAPP/pages/1_fundamental/company_analysis_demo.py`

---

## 🎯 Next Steps

1. **Start Phase 1** - Build Company Analysis with Sector tab
2. **Reference:** technical_dashboard.py for sector TA patterns
3. **Reference:** bank_dashboard.py for valuation candlestick
4. **Use:** ticker_details.json for sector classification

---

**All requirements covered! Ready to build! 🚀**
