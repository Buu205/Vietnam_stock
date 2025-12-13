# 🎨 Streamlit Dashboard UI/UX Redesign Plan v2.0

**Project:** Vietnam Stock Dashboard - Streamlit UI Transformation
**Version:** 2.0.0 (Updated based on user requirements)
**Date:** 2025-12-12
**Status:** 🚧 Planning Phase - Updated

---

## 📋 Key Changes from v1.0

### User Requirements (2025-12-12):
1. ✅ **Keep 3 FA pages:** Company, Bank, Securities (bỏ Insurance)
2. ✅ **Valuation Universal:** PE/PB chung cho tất cả, thêm PS và EV/EBITDA cho company
3. ✅ **Sector Valuation View:** Design giống bank_dashboard.py hiện tại
   - Candlestick chart với percentiles (P5, P25, P50, P75, P95)
   - Current value scatter points
   - Sector comparison view
4. ✅ **TA Page riêng:** Signal tables, screening, components phụ
5. ✅ **Commodity & Macro:** Daily tracking dashboard

---

## 🏗️ New Page Structure (6 Pages, 4 Categories)

### **Category 1: 📊 Fundamental Analysis (FA)** - 3 Pages

#### 1.1 Company Analysis
**File:** `WEBAPP/pages/1_fundamental/company_analysis.py`

**Data Source:**
```python
parquet_path = DataPaths.fundamental('company')
# DATA/processed/fundamental/company/company_financial_metrics.parquet
```

**Tabs:**
1. **Overview** - Key metrics dashboard
2. **Income Statement** - CIS metrics (Revenue, COGS, SGA, EBIT, NPATMI)
3. **Balance Sheet** - CBS metrics (Assets, Liabilities, Equity)
4. **Cash Flow** - CCS metrics (Operating CF, Free CF, Capex)
5. **Financial Ratios** - ROE, ROA, Margins, Turnover

**Charts:** (All Plotly)
- Revenue trend with MA4 (Bar + Line combo)
- Profitability margins (Multi-line)
- Growth rates (YoY, QoQ)
- Asset structure (Stacked bar)
- Cash flow waterfall

---

#### 1.2 Banking Analysis
**File:** `WEBAPP/pages/1_fundamental/banking_analysis.py`

**Data Source:**
```python
parquet_path = DataPaths.fundamental('bank')
# DATA/processed/fundamental/bank/bank_financial_metrics.parquet
```

**Tabs:**
1. **Overview** - Banking KPIs
2. **Income Statement** - BIS metrics (NII, Non-interest income, Provisions)
3. **Balance Sheet** - BBS metrics (Loans, Deposits, Equity)
4. **Banking Ratios** - NIM, CIR, CAR, NPL, LDR
5. **Credit Analysis** - Loan growth, Asset quality

**Charts:**
- NII trend with components
- Loan vs Deposit growth
- NPL ratio evolution
- CAR compliance chart
- Peer comparison boxplots

---

#### 1.3 Securities Analysis
**File:** `WEBAPP/pages/1_fundamental/securities_analysis.py`

**Data Source:**
```python
parquet_path = DataPaths.fundamental('security')
# DATA/processed/fundamental/security/security_financial_metrics.parquet
```

**Tabs:**
1. **Overview** - Securities metrics
2. **Income Statement** - SIS metrics (Brokerage, Investment income)
3. **Balance Sheet** - SBS metrics (Client deposits, Proprietary)
4. **Securities Ratios** - ROE, ROA, Revenue mix
5. **Market Share** - Trading volume, client accounts

**Charts:**
- Revenue breakdown (Stacked area)
- Market share trends
- Proprietary trading P&L
- Client asset growth

**Lý do giữ Securities:** Báo cáo tài chính khác biệt với Company/Bank, cần page riêng

---

### **Category 2: 💰 Valuation Analysis** - 1 Page (Universal)

#### 2.1 Valuation Dashboard
**File:** `WEBAPP/pages/2_valuation/valuation_dashboard.py`

**Design Philosophy:**
- PE/PB universal cho **ALL stocks** (Company + Bank + Securities)
- PS và EV/EBITDA **chỉ cho Company**
- Sector comparison view giống `bank_dashboard.py`

**Data Sources:**
```python
pe_path = DataPaths.valuation('pe')              # PE historical (ALL symbols)
pb_path = DataPaths.valuation('pb')              # PB historical (ALL symbols)
ev_path = DataPaths.valuation('ev_ebitda')       # EV/EBITDA (Company only)
ps_path = DataPaths.valuation('ps')              # PS (Company only) - NEW
sector_pe_path = DataPaths.valuation('sector_pe')  # Sector PE
```

**Tabs:**

##### Tab 1: Stock Valuation (Individual Stock)
**For ALL stocks (Company/Bank/Securities):**
- PE Ratio candlestick chart
- PB Ratio candlestick chart
- Historical percentile bands (±1σ, ±2σ)
- Current vs Historical median

**For Company ONLY:**
- PS Ratio trend
- EV/EBITDA trend

**Chart Design (Matching bank_dashboard.py):**
```python
# Candlestick với percentiles
fig = go.Figure()

# For each symbol in sector
for ticker in sector_symbols:
    ticker_data = df[df['symbol'] == ticker]['pe_ratio'].dropna()

    # Calculate percentiles
    p5 = ticker_data.quantile(0.05)
    p25 = ticker_data.quantile(0.25)
    p50 = ticker_data.quantile(0.50)  # Median
    p75 = ticker_data.quantile(0.75)
    p95 = ticker_data.quantile(0.95)

    # Add candlestick (grey color for percentile box)
    fig.add_trace(go.Candlestick(
        x=[ticker],
        open=[p25],
        high=[p95],    # Upper wick = P95
        low=[p5],      # Lower wick = P5
        close=[p75],
        increasing_line_color='lightgrey',
        decreasing_line_color='lightgrey'
    ))

    # Add current value as red scatter point
    current_val = ticker_data.iloc[-1]
    percentile = np.sum(ticker_data <= current_val) / len(ticker_data) * 100

    fig.add_trace(go.Scatter(
        x=[ticker],
        y=[current_val],
        mode='markers',
        marker=dict(size=8, color='#A95C68', symbol='circle'),
        hovertemplate=(
            f"<b>{ticker}</b><br>" +
            f"Current: {current_val:.2f}<br>" +
            f"Percentile: {percentile:.1f}%<br>" +
            f"Median: {p50:.2f}<br>"
        )
    ))

fig.update_layout(
    title='PE/PB Distribution by Ticker',
    xaxis_title='Ticker',
    yaxis_title='PE/PB Ratio'
)
```

**Key Features:**
- ✅ Candlestick shows historical distribution (P5-P95)
- ✅ Grey box = percentile range (P25-P75)
- ✅ Red dot = current value with percentile
- ✅ Hover shows: Current, Percentile, Median

---

##### Tab 2: Sector Valuation (Cross-sector comparison)
**Sectors to compare:**
- Banking (20 banks)
- Real Estate (VIC, VHM, NVL, etc.)
- Securities (SSI, VND, HCM, etc.)
- Consumer Goods (VNM, MSN, etc.)
- Technology (FPT, CMG, etc.)
- Industrial (HPG, HSG, etc.)

**Charts:**

**Chart 1: Sector PE/PB Heatmap**
```python
# Pivot table: Sectors (rows) x Metrics (columns)
sector_matrix = pd.pivot_table(
    df,
    values='pe_ratio',
    index='sector',
    columns='metric_type',
    aggfunc='median'
)

fig = pcb.heatmap(
    data=sector_matrix,
    title='Sector Valuation Heatmap',
    x_label='Metrics',
    y_label='Sectors',
    colorscale='RdYlGn_r'  # Red = expensive, Green = cheap
)
```

**Chart 2: Sector PE Distribution (Box plot style)**
```python
# Similar to bank_dashboard.py but for all sectors
fig = go.Figure()

for sector in sectors:
    sector_data = df[df['sector'] == sector]['pe_ratio'].dropna()

    # Calculate percentiles
    p5, p25, p50, p75, p95 = sector_data.quantile([0.05, 0.25, 0.50, 0.75, 0.95])

    # Add candlestick
    fig.add_trace(go.Candlestick(
        x=[sector],
        open=[p25], high=[p95], low=[p5], close=[p75],
        increasing_line_color='lightgrey',
        decreasing_line_color='lightgrey'
    ))

    # Add sector median as marker
    fig.add_trace(go.Scatter(
        x=[sector],
        y=[p50],
        mode='markers',
        marker=dict(size=10, color='#1E40AF', symbol='diamond')
    ))
```

**Chart 3: Sector Valuation vs Market Cap**
```python
# Scatter plot: PE vs Market Cap (bubble size = revenue)
fig = go.Figure(data=[
    go.Scatter(
        x=sector_summary['market_cap'],
        y=sector_summary['pe_median'],
        mode='markers+text',
        marker=dict(
            size=sector_summary['revenue'] / 1000,  # Bubble size
            color=sector_summary['pe_percentile'],
            colorscale='RdYlGn_r',
            showscale=True
        ),
        text=sector_summary['sector'],
        textposition='top center'
    )
])
```

---

##### Tab 3: VN-Index Valuation (Market-wide view)
- VN-Index PE trend
- Historical percentiles
- Valuation cycles (Bull/Bear zones)

---

##### Tab 4: Fair Value Calculator (DCF & Comparable)
- Input assumptions
- DCF result visualization
- Peer multiple comparison

**PS Ratio Note:** Chỉ áp dụng cho Company (không áp dụng cho Bank/Securities vì revenue structure khác)

---

### **Category 3: 📈 Technical Analysis (TA)** - 1 Page (Consolidated)

#### 3.1 Technical Analysis Dashboard
**File:** `WEBAPP/pages/3_technical/technical_dashboard.py`

**Design Philosophy:** Tất cả TA trong 1 page với multiple tabs

**Data Source:**
```python
tech_path = DataPaths.technical('basic')  # MA, RSI, MACD, Bollinger, ATR
market_breadth_path = DataPaths.technical('market_breadth')  # NEW
```

**Tabs:**

##### Tab 1: Stock Technical (Individual Stock TA)
**Sidebar:** Symbol selector

**Charts:**
1. **Price Chart** - Candlestick with volume
   - Toggle MA lines (20/50/100/200)
   - Bollinger Bands overlay
2. **Moving Averages**
   - SMA 20/50/100/200
   - Golden/Death cross signals
3. **Oscillators**
   - RSI (14) with overbought/oversold zones
   - MACD histogram with signal line
4. **Volume Analysis**
   - Volume bars with MA
   - Volume profile

---

##### Tab 2: TA Screening (Signal Tables)
**NEW - User's request for signal tables**

**Screening Tables:**

**Table 1: MA Alignment Signals**
```python
# Bullish: Price > MA20 > MA50 > MA100 > MA200
# Bearish: Opposite

ma_signals = []
for symbol in all_symbols:
    symbol_data = tech_df[tech_df['symbol'] == symbol].iloc[-1]

    price = symbol_data['close']
    ma20 = symbol_data['ma_20']
    ma50 = symbol_data['ma_50']
    ma100 = symbol_data['ma_100']
    ma200 = symbol_data['ma_200']

    # Check alignment
    bullish = (price > ma20 > ma50 > ma100 > ma200)
    bearish = (price < ma20 < ma50 < ma100 < ma200)

    ma_signals.append({
        'Symbol': symbol,
        'Price': price,
        'MA20': ma20,
        'Signal': '🟢 Bullish' if bullish else ('🔴 Bearish' if bearish else '⚪ Neutral'),
        'Alignment Score': calculate_alignment_score(price, ma20, ma50, ma100, ma200)
    })

# Display as sortable table
st.dataframe(
    pd.DataFrame(ma_signals).sort_values('Alignment Score', ascending=False),
    use_container_width=True
)
```

**Table 2: RSI Signals**
```python
# Oversold: RSI < 30 (potential buy)
# Overbought: RSI > 70 (potential sell)

rsi_signals = []
for symbol in all_symbols:
    rsi = tech_df[tech_df['symbol'] == symbol]['rsi_14'].iloc[-1]

    if rsi < 30:
        signal = '🟢 Oversold (Buy)'
    elif rsi > 70:
        signal = '🔴 Overbought (Sell)'
    else:
        signal = '⚪ Neutral'

    rsi_signals.append({
        'Symbol': symbol,
        'RSI': rsi,
        'Signal': signal
    })
```

**Table 3: MACD Crossover Signals**
```python
# Bullish: MACD crosses above signal line
# Bearish: MACD crosses below signal line

macd_signals = []
for symbol in all_symbols:
    symbol_data = tech_df[tech_df['symbol'] == symbol].tail(2)

    # Check crossover
    prev_macd = symbol_data.iloc[-2]['macd']
    prev_signal = symbol_data.iloc[-2]['macd_signal']
    curr_macd = symbol_data.iloc[-1]['macd']
    curr_signal = symbol_data.iloc[-1]['macd_signal']

    bullish_cross = (prev_macd < prev_signal) and (curr_macd > curr_signal)
    bearish_cross = (prev_macd > prev_signal) and (curr_macd < curr_signal)

    macd_signals.append({
        'Symbol': symbol,
        'MACD': curr_macd,
        'Signal Line': curr_signal,
        'Crossover': '🟢 Bullish' if bullish_cross else ('🔴 Bearish' if bearish_cross else '⚪ None')
    })
```

**Table 4: Bollinger Bands Squeeze**
```python
# Squeeze: Bands narrowing (low volatility, potential breakout)
# Expansion: Bands widening (high volatility)

bb_signals = []
for symbol in all_symbols:
    symbol_data = tech_df[tech_df['symbol'] == symbol].tail(5)

    # Calculate band width
    band_width = (symbol_data['bb_upper'] - symbol_data['bb_lower']) / symbol_data['bb_middle']

    # Check if narrowing (squeeze)
    is_squeeze = band_width.iloc[-1] < band_width.mean()

    bb_signals.append({
        'Symbol': symbol,
        'Band Width': band_width.iloc[-1],
        'Status': '🟡 Squeeze' if is_squeeze else '🔵 Normal'
    })
```

**Combined Signal Score:**
```python
# Aggregate all signals into single score
combined_signals = []
for symbol in all_symbols:
    score = 0

    # MA alignment (+2 if bullish, -2 if bearish)
    if ma_bullish(symbol):
        score += 2
    elif ma_bearish(symbol):
        score -= 2

    # RSI (+1 if oversold, -1 if overbought)
    rsi = get_rsi(symbol)
    if rsi < 30:
        score += 1
    elif rsi > 70:
        score -= 1

    # MACD (+1 if bullish cross, -1 if bearish cross)
    if macd_bullish_cross(symbol):
        score += 1
    elif macd_bearish_cross(symbol):
        score -= 1

    combined_signals.append({
        'Symbol': symbol,
        'Score': score,
        'Signal': '🟢 Strong Buy' if score >= 3 else (
                  '🔵 Buy' if score >= 1 else (
                  '🔴 Sell' if score <= -1 else '⚪ Neutral'))
    })

# Display as sortable table
st.dataframe(
    pd.DataFrame(combined_signals).sort_values('Score', ascending=False),
    use_container_width=True
)
```

---

##### Tab 3: Market Technical (Market-wide TA)
**Market Breadth Indicators:**

1. **Advance/Decline Line**
   ```python
   # Number of advancing vs declining stocks
   adv_dec_line = tech_df.groupby('date').apply(
       lambda x: (x['close'] > x['close'].shift(1)).sum() -
                 (x['close'] < x['close'].shift(1)).sum()
   ).cumsum()

   fig = pcb.line_chart(
       df=adv_dec_line.reset_index(),
       x_col='date',
       y_cols=['adv_dec_line'],
       title='Advance/Decline Line'
   )
   ```

2. **% Stocks Above MA**
   ```python
   # % stocks above MA20/50/100/200
   pct_above_ma = {
       'MA20': (tech_df['close'] > tech_df['ma_20']).mean() * 100,
       'MA50': (tech_df['close'] > tech_df['ma_50']).mean() * 100,
       'MA100': (tech_df['close'] > tech_df['ma_100']).mean() * 100,
       'MA200': (tech_df['close'] > tech_df['ma_200']).mean() * 100
   }

   # Bar chart
   fig = go.Figure(data=[
       go.Bar(x=list(pct_above_ma.keys()), y=list(pct_above_ma.values()))
   ])
   ```

3. **New Highs/Lows**
   ```python
   # Stocks at 52-week high/low
   new_highs = (tech_df['close'] == tech_df['close'].rolling(252).max()).sum()
   new_lows = (tech_df['close'] == tech_df['close'].rolling(252).min()).sum()
   ```

4. **Sector Rotation Heatmap**
   ```python
   # Relative strength by sector
   sector_performance = tech_df.groupby('sector').apply(
       lambda x: ((x['close'].iloc[-1] / x['close'].iloc[-20]) - 1) * 100
   )

   fig = pcb.heatmap(
       data=sector_performance.to_frame().T,
       title='Sector Performance (20-day)',
       colorscale='RdYlGn'
   )
   ```

5. **VN-Index Technical**
   - VN-Index RSI
   - VN-Index MACD
   - Volume trend

---

##### Tab 4: Commodity & Macro (Daily Tracking)
**User's request: "các chỉ số commodity hay macro cần theo dõi mỗi ngày"**

**Data Source:**
```python
macro_path = DataPaths.macro('indicators')
commodity_path = DataPaths.commodity('prices')
# DATA/processed/macro/macro_indicators.parquet
# DATA/processed/commodity/commodity_prices.parquet
```

**Metrics to Track:**

**Commodity Prices:**
1. **Gold (XAU/USD)**
   - Current price
   - Daily change %
   - 20-day MA
   - Chart: Line with 20/50 MA

2. **Oil (Brent/WTI)**
   - Current price
   - Daily change %
   - Chart: Line with MA

3. **Copper**
   - Current price
   - Chart: Line trend

**Macro Indicators:**
1. **USD/VND Exchange Rate**
   - Current rate
   - Daily change
   - Chart: Line with bands

2. **Interest Rates**
   - VN policy rate
   - US Fed rate
   - Chart: Multi-line

3. **VN-Index**
   - Current level
   - Daily change %
   - Volume

**Layout:**
```python
# Top row: KPI cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Gold (USD/oz)",
        value=f"${gold_price:,.0f}",
        delta=f"{gold_change:+.2f}%"
    )

with col2:
    st.metric(
        label="Oil Brent (USD/bbl)",
        value=f"${oil_price:.2f}",
        delta=f"{oil_change:+.2f}%"
    )

with col3:
    st.metric(
        label="USD/VND",
        value=f"{usd_vnd:,.0f}",
        delta=f"{usd_vnd_change:+.2f}%"
    )

with col4:
    st.metric(
        label="VN-Index",
        value=f"{vnindex:.2f}",
        delta=f"{vnindex_change:+.2f}%"
    )

# Charts
col1, col2 = st.columns(2)

with col1:
    # Gold chart
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
```

**Alert System (Optional):**
```python
# Show alerts if significant moves
if abs(gold_change) > 2:
    st.warning(f"⚠️ Gold moved {gold_change:+.2f}% today!")

if abs(usd_vnd_change) > 0.5:
    st.warning(f"⚠️ USD/VND moved {usd_vnd_change:+.2f}% today!")
```

---

### **Category 4: 🔍 Market Intelligence** - 2 Pages

#### 4.1 Analyst Forecasts
**File:** `WEBAPP/pages/4_intelligence/analyst_forecasts.py`

(Same as v1.0)

---

#### 4.2 News & Sentiment
**File:** `WEBAPP/pages/4_intelligence/news_sentiment.py`

(Same as v1.0)

---

## 📊 Complete Page Summary

| Category | Page | File | Key Features |
|----------|------|------|--------------|
| **1. FA** | Company Analysis | `1_fundamental/company_analysis.py` | CIS/CBS/CCS metrics, 5 tabs |
| | Banking Analysis | `1_fundamental/banking_analysis.py` | BIS/BBS/BCS metrics, 5 tabs |
| | Securities Analysis | `1_fundamental/securities_analysis.py` | SIS/SBS/SCS metrics, 5 tabs |
| **2. Valuation** | Valuation Dashboard | `2_valuation/valuation_dashboard.py` | PE/PB universal, PS/EV for company, Sector view |
| **3. TA** | Technical Dashboard | `3_technical/technical_dashboard.py` | 4 tabs: Stock TA, Screening, Market, Commodity |
| **4. Intelligence** | Analyst Forecasts | `4_intelligence/analyst_forecasts.py` | BSC forecasts, target prices |
| | News & Sentiment | `4_intelligence/news_sentiment.py` | News feed, sentiment analysis |

**Total:** 7 pages (giảm từ 8 xuống 7, bỏ Insurance)

---

## 🔧 Key Implementation Details

### 1. Valuation Candlestick Chart (Matching bank_dashboard.py)

**Reference:** `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/bank_dashboard.py`
- Function: `render_pe_pb_dotplot()` (line 1658-1807)
- Function: `render_valuation_tab()` (line 815-914)

**Implementation:**
```python
def create_valuation_candlestick(df, symbols, metric_type='pe'):
    """
    Create candlestick chart showing valuation distribution.

    Design:
    - Grey candlestick = percentile box (P25-P75)
    - Upper wick = P95
    - Lower wick = P5
    - Red dot = current value
    - Shows percentile rank in hover

    Args:
        df: DataFrame with columns [symbol, date, pe_ratio/pb_ratio]
        symbols: List of symbols to include
        metric_type: 'pe' or 'pb'

    Returns:
        Plotly Figure
    """
    metric_col = 'pe_ratio' if metric_type == 'pe' else 'pb_ratio'

    fig = go.Figure()

    for ticker in symbols:
        ticker_data = df[df['symbol'] == ticker][metric_col].dropna()

        if len(ticker_data) < 20:
            continue

        # Smart outlier handling (same as bank_dashboard.py)
        median_val = ticker_data.median()

        if metric_type == 'pe':
            upper_limit = min(50, median_val * 3) if median_val > 0 else 50
            clean_data = ticker_data[ticker_data <= upper_limit]
        else:
            upper_limit = min(4.0, median_val * 2.0) if median_val > 0 else 4.0
            clean_data = ticker_data[ticker_data <= upper_limit]

        if len(clean_data) < 20:
            clean_data = ticker_data

        # Calculate percentiles
        p5 = clean_data.quantile(0.05)
        p25 = clean_data.quantile(0.25)
        p50 = clean_data.quantile(0.50)
        p75 = clean_data.quantile(0.75)
        p95 = clean_data.quantile(0.95)

        # Current value
        current_val = ticker_data.iloc[-1]
        percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100

        # Add candlestick (grey)
        fig.add_trace(go.Candlestick(
            x=[ticker],
            open=[round(p25, 2)],
            high=[round(p95, 2)],
            low=[round(p5, 2)],
            close=[round(p75, 2)],
            name=ticker,
            showlegend=False,
            increasing_line_color='lightgrey',
            decreasing_line_color='lightgrey',
            hovertext=f"{ticker}<br>Median: {p50:.2f}"
        ))

        # Add current value (red dot)
        fig.add_trace(go.Scatter(
            x=[ticker],
            y=[current_val],
            mode='markers',
            marker=dict(size=8, color='#A95C68', symbol='circle'),
            showlegend=False,
            hovertemplate=(
                f"<b>{ticker}</b><br>" +
                f"Current: {current_val:.2f}<br>" +
                f"Percentile: {percentile:.1f}%<br>" +
                f"Median: {p50:.2f}<br>" +
                "<extra></extra>"
            )
        ))

    fig.update_layout(
        title=f'{metric_type.upper()} Distribution by Ticker',
        xaxis_title='Ticker',
        yaxis_title=f'{metric_type.upper()} Ratio',
        height=600,
        showlegend=False,
        template='plotly_white'
    )

    return fig
```

**Usage:**
```python
# In valuation_dashboard.py

# For Banking sector
banking_symbols = ['VCB', 'TCB', 'ACB', 'MBB', ...]
fig = create_valuation_candlestick(pe_df, banking_symbols, 'pe')
st.plotly_chart(fig, use_container_width=True)

# For all sectors (combined view)
all_symbols = sector_reg.get_all_symbols()
fig = create_valuation_candlestick(pe_df, all_symbols, 'pe')
st.plotly_chart(fig, use_container_width=True)
```

---

### 2. TA Signal Scoring System

**Concept:** Aggregate multiple TA signals into single actionable score

**Implementation:**
```python
def calculate_ta_score(symbol, tech_df):
    """
    Calculate combined TA score (-5 to +5).

    Scoring:
    - MA Alignment: ±2 points
    - RSI: ±1 point
    - MACD Cross: ±1 point
    - Volume: ±1 point

    Returns:
        dict with score and breakdown
    """
    symbol_data = tech_df[tech_df['symbol'] == symbol].tail(2)

    score = 0
    breakdown = {}

    # 1. MA Alignment (±2)
    latest = symbol_data.iloc[-1]
    price = latest['close']
    ma20 = latest['ma_20']
    ma50 = latest['ma_50']
    ma100 = latest['ma_100']
    ma200 = latest['ma_200']

    if price > ma20 > ma50 > ma100 > ma200:
        score += 2
        breakdown['MA'] = '+2 (Bullish alignment)'
    elif price < ma20 < ma50 < ma100 < ma200:
        score -= 2
        breakdown['MA'] = '-2 (Bearish alignment)'
    else:
        breakdown['MA'] = '0 (Mixed)'

    # 2. RSI (±1)
    rsi = latest['rsi_14']
    if rsi < 30:
        score += 1
        breakdown['RSI'] = '+1 (Oversold)'
    elif rsi > 70:
        score -= 1
        breakdown['RSI'] = '-1 (Overbought)'
    else:
        breakdown['RSI'] = '0 (Neutral)'

    # 3. MACD Cross (±1)
    prev = symbol_data.iloc[-2]
    curr = symbol_data.iloc[-1]

    if (prev['macd'] < prev['macd_signal']) and (curr['macd'] > curr['macd_signal']):
        score += 1
        breakdown['MACD'] = '+1 (Bullish cross)'
    elif (prev['macd'] > prev['macd_signal']) and (curr['macd'] < curr['macd_signal']):
        score -= 1
        breakdown['MACD'] = '-1 (Bearish cross)'
    else:
        breakdown['MACD'] = '0 (No cross)'

    # 4. Volume (±1)
    vol_ma = latest['volume_ma_20']
    if latest['volume'] > vol_ma * 1.5:
        score += 1 if price > prev['close'] else -1
        breakdown['Volume'] = f"{'+1' if price > prev['close'] else '-1'} (High volume)"
    else:
        breakdown['Volume'] = '0 (Normal)'

    return {
        'score': score,
        'breakdown': breakdown,
        'signal': (
            '🟢 Strong Buy' if score >= 3 else
            '🔵 Buy' if score >= 1 else
            '🔴 Sell' if score <= -1 else
            '⚪ Neutral'
        )
    }
```

---

### 3. Commodity & Macro Data Loading

**Data Sources:**
```python
# Gold (from external API or parquet)
gold_df = pd.read_parquet(DataPaths.commodity('gold'))
# Columns: date, price, currency

# Oil (from external API or parquet)
oil_df = pd.read_parquet(DataPaths.commodity('oil'))
# Columns: date, brent_price, wti_price

# USD/VND (from SBV or forex API)
usd_vnd_df = pd.read_parquet(DataPaths.macro('exchange_rate'))
# Columns: date, usd_vnd

# Interest rates
interest_df = pd.read_parquet(DataPaths.macro('interest_rates'))
# Columns: date, vn_policy_rate, us_fed_rate
```

**Update Pipeline:**
```bash
# Daily update script
python3 PROCESSORS/technical/pipelines/daily_macro_commodity_update.py
```

---

## 📅 Implementation Timeline (Updated)

### Phase 0: Foundation ✅ COMPLETE (2 days)
- [x] Component library
- [x] Demo page
- [x] Documentation

### Phase 1: FA Pages (5 days)
- [ ] Day 1-2: Company Analysis (2 days)
- [ ] Day 3: Banking Analysis (1 day)
- [ ] Day 4: Securities Analysis (1 day)
- [ ] Day 5: Buffer/Testing (1 day)

### Phase 2: Valuation Page (5 days)
- [ ] Day 6-7: Core valuation charts (2 days)
  - PE/PB candlestick (matching bank_dashboard.py)
  - Individual stock view
- [ ] Day 8: Sector comparison (1 day)
  - Sector heatmap
  - Sector distribution charts
- [ ] Day 9: PS/EV for company (1 day)
- [ ] Day 10: Testing & polish (1 day)

### Phase 3: TA Page (5 days)
- [ ] Day 11: Stock TA tab (1 day)
- [ ] Day 12-13: Screening tables (2 days)
  - MA signals
  - RSI signals
  - MACD signals
  - Combined score
- [ ] Day 14: Market breadth tab (1 day)
- [ ] Day 15: Commodity & Macro tab (1 day)

### Phase 4: Intelligence & Polish (5 days)
- [ ] Day 16: Analyst forecasts (1 day)
- [ ] Day 17: News & sentiment (1 day)
- [ ] Day 18: Theme & styling (1 day)
- [ ] Day 19: Performance optimization (1 day)
- [ ] Day 20: Testing & documentation (1 day)

**Total:** 20 days (4 weeks)

---

## 🎯 Success Criteria

### Performance
- ✅ <2s page load time
- ✅ <500ms page navigation
- ✅ 80% cache hit rate

### Functionality
- ✅ PE/PB candlestick matching bank_dashboard.py design
- ✅ TA signal tables with scoring system
- ✅ Commodity & Macro daily tracking
- ✅ Sector comparison views
- ✅ PS/EV for company only

### Code Quality
- ✅ 0 duplication (component library)
- ✅ 100% Plotly (no PyEcharts in new pages)
- ✅ Parquet-only data loading
- ✅ Smart caching (TTL based on volatility)

---

## 📁 Updated File Structure

```
WEBAPP/pages/
├── 1_fundamental/
│   ├── company_analysis.py       # Company FA (CIS/CBS/CCS)
│   ├── banking_analysis.py       # Bank FA (BIS/BBS/BCS)
│   └── securities_analysis.py    # Securities FA (SIS/SBS/SCS)
│
├── 2_valuation/
│   └── valuation_dashboard.py    # PE/PB universal, PS/EV for company
│                                 # Sector comparison (candlestick design)
│
├── 3_technical/
│   └── technical_dashboard.py    # 4 tabs:
│                                 # - Stock TA
│                                 # - Screening (signal tables)
│                                 # - Market breadth
│                                 # - Commodity & Macro
│
└── 4_intelligence/
    ├── analyst_forecasts.py      # BSC forecasts
    └── news_sentiment.py         # News & sentiment
```

**Total:** 7 pages (bỏ insurance_analysis.py)

---

## 🚀 Next Steps

1. **Review & Approve Plan** - Confirm this matches your requirements
2. **Start Phase 1** - Build 3 FA pages (Company, Bank, Securities)
3. **Focus on Valuation** - Implement candlestick design from bank_dashboard.py
4. **Build TA Screening** - Signal tables with scoring
5. **Add Commodity/Macro** - Daily tracking dashboard

---

**Có gì cần điều chỉnh thêm không bạn?** 😊
