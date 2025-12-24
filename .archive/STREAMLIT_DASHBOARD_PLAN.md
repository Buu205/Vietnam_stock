# Streamlit Dashboard Implementation Plan
# Kế Hoạch Triển Khai Dashboard Streamlit

> **Created:** 2025-12-14
> **Author:** Claude Code
> **Purpose:** Chi tiết thiết kế 3 dashboard pages cho Company, Bank, Securities

---

## 📁 CẤU TRÚC FILE

```
WEBAPP/
├── pages/
│   ├── 1_📊_Company_Analysis.py          # Company dashboard
│   ├── 2_🏦_Bank_Analysis.py             # Bank dashboard
│   ├── 3_💼_Securities_Analysis.py       # Securities dashboard
│   └── __init__.py
├── components/
│   ├── charts/
│   │   ├── income_statement_chart.py     # Income statement visualizations
│   │   ├── balance_sheet_chart.py        # Balance sheet visualizations
│   │   ├── cash_flow_chart.py            # Cash flow waterfall
│   │   ├── profitability_chart.py        # Margins & ratios
│   │   └── growth_chart.py               # Growth metrics
│   ├── metrics/
│   │   ├── metric_cards.py               # KPI cards component
│   │   └── metric_table.py               # Data table component
│   └── filters/
│       ├── ticker_selector.py            # Ticker selection
│       ├── date_range_selector.py        # Date range picker
│       └── period_selector.py            # Quarter/Year selector
└── services/
    ├── company_service.py                # Company data API
    ├── bank_service.py                   # Bank data API
    └── security_service.py               # Security data API
```

---

## 🏢 PAGE 1: COMPANY ANALYSIS DASHBOARD

### File: `WEBAPP/pages/1_📊_Company_Analysis.py`

### Layout Structure:

```python
"""
+----------------------------------------------------------+
|  HEADER: Company Financial Analysis                       |
|  [Ticker Selector] [Period Selector] [Refresh Button]    |
+----------------------------------------------------------+
|                                                           |
|  SECTION 1: KEY METRICS CARDS (4 columns)                |
|  +--------+  +--------+  +--------+  +--------+          |
|  | Revenue|  | Profit |  |  ROE   |  | D/E    |          |
|  | 1,234B |  |  234B  |  | 15.2%  |  | 0.45x  |          |
|  | +12.5% |  | +18.3% |  | +2.1pp |  | -0.05x |          |
|  +--------+  +--------+  +--------+  +--------+          |
|                                                           |
+----------------------------------------------------------+
|  SECTION 2: INCOME STATEMENT TRENDS (Full width)         |
|  [Line Chart] Revenue, Gross Profit, EBIT, EBITDA, NP   |
|                                                           |
+----------------------------------------------------------+
|  SECTION 3: PROFITABILITY MARGINS (Left 50%)            |
|  [Area Chart] Gross, EBIT, EBITDA, Net Margins          |
|                                                           |
+---------------------------+------------------------------+
|  SECTION 4: CASH FLOW     |  SECTION 5: LIQUIDITY       |
|  [Waterfall Chart]        |  [Gauge Charts]              |
|  Operating CF → FCFE      |  Current, Quick, Cash Ratios |
+---------------------------+------------------------------+
|  SECTION 6: BALANCE SHEET COMPOSITION                    |
|  [Stacked Bar] Assets vs Liabilities & Equity           |
|                                                           |
+----------------------------------------------------------+
|  SECTION 7: GROWTH & ACTIVITY RATIOS                     |
|  [Table] QoQ & YoY Growth | [Table] Activity Ratios     |
+----------------------------------------------------------+
"""
```

### Code Implementation:

```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from WEBAPP.services.company_service import CompanyService
from WEBAPP.components.metrics.metric_cards import render_metric_card
from WEBAPP.components.charts.income_statement_chart import render_income_statement_chart
from WEBAPP.components.filters.ticker_selector import render_ticker_selector

st.set_page_config(
    page_title="Company Analysis",
    page_icon="📊",
    layout="wide"
)

# Header
st.title("📊 Company Financial Analysis")
st.markdown("---")

# Filters
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    ticker = render_ticker_selector(entity_type="COMPANY")
with col2:
    period = st.selectbox(
        "Period",
        options=["Quarterly", "Yearly", "TTM"],
        index=0
    )
with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# Load data
@st.cache_data(ttl=3600)
def load_company_data(ticker, period):
    service = CompanyService()
    return service.get_financial_data(ticker, period)

df = load_company_data(ticker, period)

if df.empty:
    st.warning(f"No data available for {ticker}")
    st.stop()

# SECTION 1: Key Metrics Cards
st.subheader("Key Financial Metrics")
latest = df.iloc[-1]
previous = df.iloc[-2] if len(df) > 1 else latest

col1, col2, col3, col4 = st.columns(4)

with col1:
    render_metric_card(
        label="Net Revenue",
        value=latest['net_revenue'],
        delta=latest['net_revenue'] - previous['net_revenue'],
        delta_pct=True,
        unit="B VND"
    )

with col2:
    render_metric_card(
        label="Net Profit",
        value=latest['npatmi'],
        delta=latest['npatmi'] - previous['npatmi'],
        delta_pct=True,
        unit="B VND"
    )

with col3:
    render_metric_card(
        label="ROE",
        value=latest['roe'],
        delta=latest['roe'] - previous['roe'],
        delta_pct=False,
        unit="%"
    )

with col4:
    render_metric_card(
        label="Debt/Equity",
        value=latest['debt_to_equity'],
        delta=latest['debt_to_equity'] - previous['debt_to_equity'],
        delta_pct=False,
        unit="x",
        inverse=True  # Lower is better
    )

st.markdown("---")

# SECTION 2: Income Statement Trends
st.subheader("Income Statement Trends")
render_income_statement_chart(df)

st.markdown("---")

# SECTION 3 & 4: Margins and Cash Flow
col1, col2 = st.columns(2)

with col1:
    st.subheader("Profitability Margins")
    fig = go.Figure()

    margins = {
        'Gross Margin': 'gross_profit_margin',
        'EBIT Margin': 'ebit_margin',
        'EBITDA Margin': 'ebitda_margin',
        'Net Margin': 'net_margin'
    }

    for name, col in margins.items():
        fig.add_trace(go.Scatter(
            x=df['report_date'],
            y=df[col],
            name=name,
            mode='lines+markers',
            fill='tonexty' if name != 'Gross Margin' else None
        ))

    fig.update_layout(
        yaxis_title="Margin (%)",
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Cash Flow")
    # Waterfall chart for latest quarter
    latest_cf = df.iloc[-1]

    fig = go.Figure(go.Waterfall(
        name="Cash Flow",
        orientation="v",
        measure=["relative", "relative", "total", "relative", "total"],
        x=["Operating CF", "Capex", "FCF", "Δ Net Borrowing - Δ WC", "FCFE"],
        y=[
            latest_cf['operating_cf'],
            -latest_cf['capex'],
            0,  # FCF will be calculated
            latest_cf['delta_net_borrowing'] - latest_cf['delta_working_capital'],
            0   # FCFE will be calculated
        ],
        text=[
            f"{latest_cf['operating_cf']:.1f}",
            f"-{latest_cf['capex']:.1f}",
            f"{latest_cf['fcf']:.1f}",
            f"{latest_cf['delta_net_borrowing'] - latest_cf['delta_working_capital']:.1f}",
            f"{latest_cf['fcfe']:.1f}"
        ],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))

    fig.update_layout(
        title=f"Cash Flow - Q{latest['quarter']} {latest['year']}",
        yaxis_title="VND Billions",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# SECTION 5: Balance Sheet Composition
st.subheader("Balance Sheet Composition")

fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=("Assets", "Liabilities & Equity"),
    specs=[[{"type": "bar"}, {"type": "bar"}]]
)

# Assets
fig.add_trace(
    go.Bar(name="Current Assets", x=df['report_date'], y=df['current_assets']),
    row=1, col=1
)
fig.add_trace(
    go.Bar(name="Fixed Assets", x=df['report_date'], y=df['tangible_fixed_asset']),
    row=1, col=1
)
fig.add_trace(
    go.Bar(name="Other Assets", x=df['report_date'],
           y=df['total_assets'] - df['current_assets'] - df['tangible_fixed_asset']),
    row=1, col=1
)

# Liabilities & Equity
fig.add_trace(
    go.Bar(name="Current Liabilities", x=df['report_date'], y=df['current_liabilities']),
    row=1, col=2
)
fig.add_trace(
    go.Bar(name="LT Debt", x=df['report_date'], y=df['lt_debt']),
    row=1, col=2
)
fig.add_trace(
    go.Bar(name="Equity", x=df['report_date'], y=df['total_equity']),
    row=1, col=2
)

fig.update_layout(
    barmode='stack',
    height=500,
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# SECTION 6: Growth & Activity Ratios
col1, col2 = st.columns(2)

with col1:
    st.subheader("Growth Metrics (YoY)")

    growth_df = pd.DataFrame({
        'Metric': ['Revenue', 'Gross Profit', 'EBIT', 'EBITDA', 'Net Profit'],
        'Latest': [
            latest['net_revenue'],
            latest['gross_profit'],
            latest['ebit'],
            latest['ebitda'],
            latest['npatmi']
        ],
        'Growth %': [
            latest.get('CIS_10_yoy_growth', 0),
            latest.get('CIS_20_yoy_growth', 0),
            latest.get('ebit_yoy_growth', 0),
            latest.get('ebitda_yoy_growth', 0),
            latest.get('CIS_61_yoy_growth', 0)
        ]
    })

    st.dataframe(
        growth_df.style.format({
            'Latest': '{:.1f}',
            'Growth %': '{:.2f}%'
        }).background_gradient(subset=['Growth %'], cmap='RdYlGn', vmin=-20, vmax=20),
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("Activity Ratios")

    activity_df = pd.DataFrame({
        'Metric': ['Asset Turnover', 'Inventory Turnover', 'Receivables Turnover'],
        'Value': [
            latest['asset_turnover'],
            latest['inventory_turnover'],
            latest['receivables_turnover']
        ],
        'Unit': ['x', 'x', 'x']
    })

    st.dataframe(
        activity_df.style.format({'Value': '{:.2f}'}),
        use_container_width=True,
        hide_index=True
    )
```

---

## 🏦 PAGE 2: BANK ANALYSIS DASHBOARD

### File: `WEBAPP/pages/2_🏦_Bank_Analysis.py`

### Layout Structure:

```python
"""
+----------------------------------------------------------+
|  HEADER: Bank Financial Analysis                         |
|  [Ticker Selector] [Period Selector] [Refresh Button]    |
+----------------------------------------------------------+
|                                                           |
|  SECTION 1: KEY METRICS CARDS (6 columns)                |
|  +------+ +------+ +------+ +------+ +------+ +------+   |
|  |Assets| |Loans | |Depos.| | NIM  | | ROE  | | NPL% |   |
|  |1,234T| | 850T | | 950T | | 3.5% | | 18%  | | 1.2% |   |
|  +------+ +------+ +------+ +------+ +------+ +------+   |
|                                                           |
+----------------------------------------------------------+
|  SECTION 2: INCOME STATEMENT WATERFALL                   |
|  NII → Fees → Other → TOI → OPEX → Provision → NPATMI   |
|                                                           |
+----------------------------------------------------------+
|  SECTION 3: ASSET QUALITY      |  SECTION 4: PROFITABILITY|
|  [NPL Trend Line Chart]        |  [Multi-line Chart]      |
|  [Loan Groups Pie Chart]       |  NIM, Yield, COF         |
+-------------------------------+---------------------------+
|  SECTION 5: EFFICIENCY RATIOS                            |
|  [CIR Gauge] [CASA Gauge] [LDR Gauge]                   |
|                                                           |
+----------------------------------------------------------+
|  SECTION 6: GROWTH DASHBOARD                             |
|  [Bar Chart] Loan, Deposit, Credit Growth (YTD & YoY)   |
|                                                           |
+----------------------------------------------------------+
"""
```

### Key Charts for Bank:

1. **Income Waterfall**: NII → TOI → PPOP → PBT → NPATMI
2. **NPL Trend**: Line chart with NPL%, Group 2%, LLCR
3. **Loan Composition**: Pie chart (Group 1-5)
4. **Yield Analysis**: Dual-axis (Yield & COF)
5. **Efficiency Gauges**: CIR (<40% good), CASA (>30% good), LDR (<90% good)

---

## 💼 PAGE 3: SECURITIES ANALYSIS DASHBOARD

### File: `WEBAPP/pages/3_💼_Securities_Analysis.py`

### Layout Structure:

```python
"""
+----------------------------------------------------------+
|  HEADER: Securities Company Analysis                     |
|  [Ticker Selector] [Period Selector] [Refresh Button]    |
+----------------------------------------------------------+
|                                                           |
|  SECTION 1: KEY METRICS CARDS (5 columns)                |
|  +--------+ +--------+ +--------+ +--------+ +--------+  |
|  | Assets | | Equity | |Leverage| |  ROAE  | |  ROAA  |  |
|  | 10,000B| | 5,000B |  | 2.0x   | | 15.2%  | | 7.5%   |  |
|  +--------+ +--------+ +--------+ +--------+ +--------+  |
|                                                           |
+----------------------------------------------------------+
|  SECTION 2: REVENUE COMPOSITION                          |
|  [Stacked Bar] Investment | Lending | Brokerage | IB     |
|                                                           |
+----------------------------------------------------------+
|  SECTION 3: PROFITABILITY BY BUSINESS LINE               |
|  [Grouped Bar] Margins by segment over time             |
|                                                           |
+----------------------------------------------------------+
|  SECTION 4: PORTFOLIO      |  SECTION 5: YIELD METRICS   |
|  [Pie Chart]               |  [Line Chart]                |
|  FVTPL, HTM, AFS, Loans    |  Inv Yield, Loan Yield, COF  |
+------------------------------+-----------------------------+
|  SECTION 6: CAPITAL STRUCTURE                            |
|  [Stacked Area] Assets, Debt, Equity evolution           |
|                                                           |
+----------------------------------------------------------+
"""
```

### Key Charts for Securities:

1. **Revenue Breakdown**: Stacked bar (Investment, Lending, Brokerage, IB)
2. **Profitability by Segment**: Grouped bar comparing margins
3. **Portfolio Mix**: Pie chart (FVTPL, HTM, AFS, Margin Loans)
4. **Yield Comparison**: Multi-line (Investment Yield, Loan Yield, Funding Cost)
5. **Leverage Trend**: Line chart showing Assets/Equity ratio

---

## 🎨 SHARED COMPONENTS

### 1. Metric Card Component
**File:** `WEBAPP/components/metrics/metric_cards.py`

```python
import streamlit as st

def render_metric_card(label, value, delta=None, delta_pct=False, unit="", inverse=False):
    """
    Render a metric card with optional delta indicator.

    Args:
        label: Metric name
        value: Current value
        delta: Change from previous period
        delta_pct: If True, show delta as percentage
        unit: Unit of measurement (B VND, %, x, etc.)
        inverse: If True, negative delta is good (e.g., for costs)
    """

    # Format value
    if isinstance(value, float):
        if unit == "%":
            formatted_value = f"{value:.2f}%"
        elif unit == "x":
            formatted_value = f"{value:.2f}x"
        elif "B" in unit or "T" in unit:
            formatted_value = f"{value:,.1f} {unit}"
        else:
            formatted_value = f"{value:,.0f} {unit}"
    else:
        formatted_value = f"{value} {unit}"

    # Format delta
    delta_color = "normal"
    if delta is not None:
        if delta_pct:
            delta_text = f"{delta:+.2f}%"
        else:
            delta_text = f"{delta:+.2f}"

        # Determine color
        if (delta > 0 and not inverse) or (delta < 0 and inverse):
            delta_color = "normal"  # Positive (green)
        elif (delta < 0 and not inverse) or (delta > 0 and inverse):
            delta_color = "inverse"  # Negative (red)
    else:
        delta_text = None

    # Render
    st.metric(
        label=label,
        value=formatted_value,
        delta=delta_text,
        delta_color=delta_color
    )
```

### 2. Chart Color Scheme
**File:** `WEBAPP/components/charts/colors.py`

```python
# Color scheme for financial charts
COLORS = {
    # Income/Positive metrics
    'income': '#10b981',       # Green
    'revenue': '#059669',      # Dark green
    'profit': '#34d399',       # Light green

    # Expense/Negative metrics
    'expense': '#ef4444',      # Red
    'cost': '#dc2626',         # Dark red
    'loss': '#f87171',         # Light red

    # Asset colors
    'asset': '#3b82f6',        # Blue
    'cash': '#60a5fa',         # Light blue
    'investment': '#2563eb',   # Dark blue

    # Liability colors
    'liability': '#f59e0b',    # Orange
    'debt': '#d97706',         # Dark orange

    # Equity colors
    'equity': '#8b5cf6',       # Purple

    # Neutral
    'neutral': '#6b7280',      # Gray
    'background': '#f9fafb',   # Light gray
}
```

---

## 📊 CHART SPECIFICATIONS

### Chart Type Matrix:

| Data Type | Recommended Chart | Use Case | Plotly Type |
|-----------|-------------------|----------|-------------|
| **Time Series (Single)** | Line Chart | Revenue trend | `go.Scatter` |
| **Time Series (Multiple)** | Multi-line | NIM, Yield, COF | `go.Scatter` × n |
| **Composition over Time** | Stacked Area/Bar | Revenue breakdown | `go.Bar` (barmode='stack') |
| **Part-to-Whole** | Pie Chart | Portfolio mix | `go.Pie` |
| **Comparison** | Grouped Bar | YoY comparison | `go.Bar` (barmode='group') |
| **Flow** | Waterfall | Cash flow | `go.Waterfall` |
| **Gauge** | Gauge Chart | Ratios vs targets | `go.Indicator` (mode='gauge') |
| **Dual Metrics** | Dual-axis | NPL% vs LLCR | `make_subplots` (secondary_y) |

### Example: Waterfall Chart for Cash Flow

```python
import plotly.graph_objects as go

def render_cash_flow_waterfall(df, quarter_idx=-1):
    """Render cash flow waterfall chart."""
    data = df.iloc[quarter_idx]

    fig = go.Figure(go.Waterfall(
        name="Cash Flow",
        orientation="v",
        measure=["relative", "relative", "total", "relative", "total"],
        x=["Operating CF", "Capex", "FCF", "Net Financing", "FCFE"],
        y=[
            data['operating_cf'],
            -data['capex'],
            0,  # Will auto-calculate
            data['delta_net_borrowing'] - data['delta_working_capital'],
            0   # Will auto-calculate
        ],
        text=[
            f"{data['operating_cf']:.1f}B",
            f"-{data['capex']:.1f}B",
            f"{data['fcf']:.1f}B",
            f"{data['delta_net_borrowing'] - data['delta_working_capital']:.1f}B",
            f"{data['fcfe']:.1f}B"
        ],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": COLORS['income']}},
        decreasing={"marker": {"color": COLORS['expense']}},
        totals={"marker": {"color": COLORS['asset']}}
    ))

    fig.update_layout(
        title=f"Cash Flow Waterfall - Q{data['quarter']} {data['year']}",
        yaxis_title="VND Billions",
        showlegend=False,
        height=450
    )

    return fig
```

---

## 🔧 DATA SERVICE LAYER

### Company Service Example
**File:** `WEBAPP/services/company_service.py`

```python
import pandas as pd
from pathlib import Path

class CompanyService:
    """Service layer for Company financial data."""

    def __init__(self):
        self.data_path = Path("DATA/processed/fundamental/company/")

    def get_financial_data(self, ticker, period="Quarterly"):
        """
        Load financial data for a company ticker.

        Args:
            ticker: Stock symbol
            period: "Quarterly", "Yearly", or "TTM"

        Returns:
            DataFrame with financial metrics
        """
        # Load from parquet
        df = pd.read_parquet(
            self.data_path / "company_financial_metrics.parquet"
        )

        # Filter by ticker
        df = df[df['symbol'] == ticker].copy()

        # Filter by period
        if period == "Quarterly":
            df = df[df['freq_code'] == 'Q']
        elif period == "Yearly":
            df = df[df['freq_code'] == 'Y']
        # TTM columns already in data

        # Sort by date
        df = df.sort_values('report_date')

        return df

    def get_latest_metrics(self, ticker):
        """Get latest quarter metrics."""
        df = self.get_financial_data(ticker, "Quarterly")
        return df.iloc[-1].to_dict() if not df.empty else {}

    def get_peer_comparison(self, ticker):
        """Get peer comparison data."""
        from config.registries import SectorRegistry

        sector_reg = SectorRegistry()
        peers = sector_reg.get_peers(ticker)

        # Load data for all peers
        dfs = []
        for peer in peers:
            peer_df = self.get_financial_data(peer, "Quarterly")
            if not peer_df.empty:
                dfs.append(peer_df.iloc[-1])

        return pd.DataFrame(dfs) if dfs else pd.DataFrame()
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Phase 1: Core Infrastructure ⚠️
- [ ] Create `WEBAPP/components/` structure
- [ ] Implement `metric_cards.py`
- [ ] Implement color scheme (`colors.py`)
- [ ] Create service layer (`company_service.py`, `bank_service.py`, `security_service.py`)

### Phase 2: Company Dashboard 📊
- [ ] Create `1_📊_Company_Analysis.py`
- [ ] Implement income statement chart
- [ ] Implement profitability margins chart
- [ ] Implement cash flow waterfall
- [ ] Implement balance sheet composition
- [ ] Add growth & activity tables

### Phase 3: Bank Dashboard 🏦
- [ ] Create `2_🏦_Bank_Analysis.py`
- [ ] Implement income waterfall
- [ ] Implement NPL trend chart
- [ ] Implement loan composition pie chart
- [ ] Implement yield analysis chart
- [ ] Add efficiency gauges (CIR, CASA, LDR)

### Phase 4: Securities Dashboard 💼
- [ ] Create `3_💼_Securities_Analysis.py`
- [ ] Implement revenue composition stacked bar
- [ ] Implement profitability by segment
- [ ] Implement portfolio pie chart
- [ ] Implement yield metrics chart
- [ ] Add capital structure stacked area

### Phase 5: Testing & Polish ✨
- [ ] Test all dashboards with real data
- [ ] Responsive design check
- [ ] Performance optimization
- [ ] Add export functionality (CSV, Excel)
- [ ] Add screenshot/PDF export

---

**Created by:** Claude Code
**Last Updated:** 2025-12-14
