# Company Dashboard Specification
# Dashboard Phân Tích Công Ty

> **Page:** `WEBAPP/pages/1_company_dashboard.py`
> **Service:** `CompanyService`
> **Data:** `DATA/processed/fundamental/company/company_financial_metrics.parquet`
> **Status:** 70% Complete - Extend existing `company_dashboard_v2.py`
> **Priority:** 🔴 HIGH (Implement First)

---

## 1. Page Overview

### Purpose
Comprehensive fundamental analysis for non-financial companies (manufacturing, retail, tech, etc.)

### Target Users
- Investors analyzing company fundamentals
- Analysts comparing company performance over time
- Portfolio managers screening stocks

### Key Features
- ✅ 4 KPI metric cards (Revenue, Profit, ROE, D/E) - DONE
- ✅ Income statement trend chart - DONE
- ✅ Profitability margins chart - DONE
- ✅ Summary data table - DONE
- ✅ ROE/ROA trend chart - DONE (2025-12-15)
- 🆕 Balance sheet analysis - TO ADD
- 🆕 Cash flow waterfall chart - TO ADD
- 🆕 Peer comparison section - TO ADD

---

## 2. Data Requirements

### Service Layer
```python
from WEBAPP.services.company_service import CompanyService

service = CompanyService()

# Available methods:
df = service.get_financial_data(ticker, period="Quarterly", limit=8)
latest = service.get_latest_metrics(ticker)
tickers = service.get_available_tickers()
peers_df = service.get_peer_comparison(ticker)  # Load peer data
```

### Required Columns

**Income Statement:**
- `report_date`, `symbol`, `freq_code`, `quarter`, `year`
- `net_revenue`, `gross_profit`, `ebit`, `ebitda`, `npatmi`
- `gross_profit_margin`, `ebit_margin`, `ebitda_margin`, `net_margin`

**Balance Sheet:**
- `total_assets`, `total_liabilities`, `total_equity`
- `current_assets`, `current_liabilities`
- `cash`, `inventory`, `receivables`

**Cash Flow:**
- `operating_cash_flow`, `investing_cash_flow`, `financing_cash_flow`
- `free_cash_flow`

**Ratios:**
- `roe`, `roa`, `debt_to_equity`, `current_ratio`

---

## 3. Layout Design

### Overall Structure
```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Company Financial Analysis                               │
│ Professional dashboard for Vietnamese stock analysis        │
├─────────────────────────────────────────────────────────────┤
│ SIDEBAR                │ MAIN CONTENT                       │
│ ┌─────────────────┐    │ ┌─────────────────────────────┐  │
│ │ Filters         │    │ │ SECTION 1: Key Metrics      │  │
│ │ - Select Ticker │    │ │ [Revenue] [Profit] [ROE] [D/E] │
│ │ - Period        │    │ └─────────────────────────────┘  │
│ │ - # Periods     │    │                                  │
│ │ [Refresh]       │    │ ┌─────────────────────────────┐  │
│ └─────────────────┘    │ │ SECTION 2: Income Statement │  │
│                        │ │ [Multi-line trend chart]    │  │
│                        │ └─────────────────────────────┘  │
│                        │                                  │
│                        │ ┌──────────────┬──────────────┐  │
│                        │ │ SECTION 3:   │ SECTION 4:   │  │
│                        │ │ Margins      │ ROE/ROA      │  │
│                        │ │ [Area chart] │ [Line chart] │  │
│                        │ └──────────────┴──────────────┘  │
│                        │                                  │
│                        │ ┌─────────────────────────────┐  │
│                        │ │ SECTION 5: Balance Sheet    │  │
│                        │ │ [Stacked bar chart]         │  │
│                        │ └─────────────────────────────┘  │
│                        │                                  │
│                        │ ┌─────────────────────────────┐  │
│                        │ │ SECTION 6: Cash Flow        │  │
│                        │ │ [Waterfall chart]           │  │
│                        │ └─────────────────────────────┘  │
│                        │                                  │
│                        │ ┌─────────────────────────────┐  │
│                        │ │ SECTION 7: Peer Comparison  │  │
│                        │ │ [Horizontal bar chart]      │  │
│                        │ └─────────────────────────────┘  │
│                        │                                  │
│                        │ ┌─────────────────────────────┐  │
│                        │ │ SECTION 8: Data Table       │  │
│                        │ │ [Financial summary]         │  │
│                        │ └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Section-by-Section Specifications

### SECTION 1: Key Metrics (4 Cards) ✅ DONE

**Current Implementation:** Working, no changes needed

**Metrics:**
1. **Net Revenue** - Latest revenue with QoQ/YoY growth
2. **Net Profit (NPATMI)** - Latest profit with growth
3. **ROE** - Return on Equity (percentage)
4. **Debt/Equity** - Leverage ratio (lower is better)

**Code Pattern:**
```python
from WEBAPP.components.metrics.metric_cards import render_metric_card

col1, col2, col3, col4 = st.columns(4)

with col1:
    revenue_delta = latest['net_revenue'] - previous['net_revenue']
    render_metric_card(
        label="Net Revenue",
        value=latest['net_revenue'],
        delta=revenue_delta,
        delta_pct=True,
        unit="B VND"
    )
```

---

### SECTION 2: Income Statement Trends ✅ DONE

**Current Implementation:** Working, no changes needed

**Chart Type:** Multi-line chart (Plotly)

**Metrics Displayed:**
- Net Revenue (dark green #059669)
- Gross Profit (green #10B981)
- EBIT (blue #3B82F6)
- EBITDA (light blue #60A5FA)
- Net Profit (amber #F59E0B)

**Code:** Already in `WEBAPP/components/charts/income_statement_chart.py`

---

### SECTION 3: Profitability Margins ✅ DONE

**Current Implementation:** Working, no changes needed

**Chart Type:** Area chart (Plotly)

**Metrics:**
- Gross Margin
- EBIT Margin
- EBITDA Margin
- Net Margin

**Code:** Already in `WEBAPP/components/charts/income_statement_chart.py`

---

### SECTION 4: ROE/ROA Trend 🆕 TO ADD

**Purpose:** Show return on equity and assets over time

**Chart Type:** Dual-axis line chart (Plotly)

**Data:**
- X-axis: `report_date`
- Y-axis Left: ROE (%)
- Y-axis Right: ROA (%)

**Colors:**
- ROE: Brand blue (#295CA9)
- ROA: Brand teal (#009B87)

**Frontend-Design Prompt:**
```
Tôi muốn thiết kế "ROE/ROA Trend" chart cho Company Dashboard.

Data structure:
- DataFrame with columns: report_date, roe, roa
- 8-20 periods (quarterly or yearly)
- ROE: typically 10-30%
- ROA: typically 5-15%

Requirements:
- Dual-axis line chart (ROE on left axis, ROA on right axis)
- ROE line: Brand blue (#295CA9), thicker (width=3)
- ROA line: Brand teal (#009B87), thinner (width=2)
- Markers on each data point (size=6)
- Hover shows: Date, ROE: X.XX%, ROA: Y.YY%
- Grid lines: subtle gray (rgba(128,128,128,0.1))

Style:
- Dark background (#0A1E42)
- Title: "Return on Equity & Assets" (Inter font, 18px)
- Height: 400px
- Responsive: use_container_width=True
```

**Implementation Location:**
- ✅ IMPLEMENTED in `WEBAPP/components/charts/income_statement_chart.py`:
  ```python
  def render_roe_roa_chart(df: pd.DataFrame, height: int = 400):
      """
      Render ROE/ROA dual-axis trend chart with brand colors.

      Features:
      - Dual Y-axes for different scales
      - ROE (primary): Blue #295CA9, solid line, width=3
      - ROA (secondary): Teal #009B87, dotted line, width=2.5
      - Gradient fill under ROE line
      - Large markers on latest data points
      - Smooth spline curves
      - Professional dark theme (#0A1E42)
      """
  ```

**Implementation Notes (2025-12-15):**
- Chart successfully integrated into Company Dashboard Section 4
- Uses dual Y-axes with color-coded labels (blue for ROE, teal for ROA)
- Includes gradient fill under ROE line for emphasis
- Latest data points highlighted with larger markers (size=14 for ROE, size=12 for ROA)
- Diamond-shaped markers for ROA to distinguish from circular ROE markers
- Smooth spline curves for professional appearance
- Hover template shows formatted percentages (2 decimals)

**⚠️ Data Requirement Issue:**
- Current `company_financial_metrics.parquet` only contains balance sheet data (23 columns)
- Missing required columns: `roe`, `roa`, `net_revenue`, `npatmi`, income statement metrics
- Chart will display info message if ROE/ROA columns are not present
- **TODO:** Update company calculator to include income statement + calculated ratios (ROE, ROA)
- Temporary workaround: Dashboard checks for column existence before rendering

---

### SECTION 5: Balance Sheet Analysis 🆕 TO ADD

**Purpose:** Show asset/liability/equity structure over time

**Chart Type:** Stacked bar chart (Plotly)

**Data:**
- X-axis: `report_date`
- Y-axis: Value in Billions VND
- Bars:
  - Total Assets (brand blue #295CA9)
  - Total Liabilities (brand gold #FFC132)
  - Total Equity (light blue #4A7BC8)

**Layout:**
- Assets bar (full height)
- On same x-position: Liabilities (bottom) + Equity (top) stacked to equal Assets

**Frontend-Design Prompt:**
```
Tôi muốn thiết kế "Balance Sheet Structure" chart cho Company Dashboard.

Data structure:
- DataFrame with columns: report_date, total_assets, total_liabilities, total_equity
- Accounting equation: Assets = Liabilities + Equity
- 8 periods (quarterly)
- Example: Assets=10,000B, Liabilities=6,000B, Equity=4,000B

Requirements:
- Grouped + stacked bar chart
- Group 1 (Assets): Single bar, brand blue (#295CA9)
- Group 2 (Liabilities + Equity): Stacked bars
  - Liabilities: Brand gold (#FFC132)
  - Equity: Light blue (#4A7BC8)
- Hover: Show date, metric name, value in "X,XXX.XB VND" format
- Y-axis: "VND Billions"

Style:
- Dark background (#0A1E42)
- Title: "Balance Sheet Structure" (Inter font, 18px)
- Height: 400px
- Legend: horizontal, top-right
```

**Implementation Location:**
- Add to `WEBAPP/components/charts/fundamental_charts.py`:
  ```python
  def render_balance_sheet_chart(df: pd.DataFrame, height: int = 400):
      """Balance sheet structure bar chart."""
      # Implementation here
  ```

---

### SECTION 6: Cash Flow Waterfall 🆕 TO ADD

**Purpose:** Show cash flow breakdown (Operating, Investing, Financing)

**Chart Type:** Waterfall chart (Plotly)

**Data (Latest Period):**
- Starting: Operating Cash Flow (positive, green #00A878)
- Change: Investing Cash Flow (usually negative, red #E63946)
- Change: Financing Cash Flow (can be positive or negative)
- Ending: Free Cash Flow (final bar, brand blue #295CA9)

**Frontend-Design Prompt:**
```
Tôi muốn thiết kế "Cash Flow Waterfall" chart cho Company Dashboard.

Data structure:
- Latest period only (e.g., Q3 2024)
- Columns: operating_cash_flow, investing_cash_flow, financing_cash_flow, free_cash_flow
- Example values: OCF=+500B, ICF=-200B, FCF=+100B, FreeCF=+400B

Requirements:
- Waterfall chart showing cash flow progression
- Bars:
  1. Operating CF: Start (positive, teal green #00A878)
  2. Investing CF: Change (usually negative, red #E63946)
  3. Financing CF: Change (can be +/-, neutral gray or green/red)
  4. Free CF: End (total, brand blue #295CA9)
- Connect bars with lines showing flow
- Show exact value on each bar

Style:
- Dark background (#0A1E42)
- Title: "Cash Flow Breakdown - {date}" (Inter font, 18px)
- Height: 400px
- Y-axis: "VND Billions"
```

**Implementation Location:**
- Add to `WEBAPP/components/charts/fundamental_charts.py`:
  ```python
  def render_cash_flow_waterfall(latest_row: pd.Series, height: int = 400):
      """Cash flow waterfall chart for single period."""
      # Implementation here
  ```

---

### SECTION 7: Peer Comparison 🆕 TO ADD

**Purpose:** Compare current company with sector peers on key metrics

**Chart Type:** Horizontal bar chart (Plotly)

**Data:**
- Y-axis: Company symbols (ticker names)
- X-axis: ROE (%)
- Highlight current company with brand blue (#295CA9)
- Other peers in gray (#6B7280)

**Metrics to Compare:** ROE, Revenue Growth, Net Margin (tabs or dropdown)

**Frontend-Design Prompt:**
```
Tôi muốn thiết kế "Peer Comparison - ROE" chart cho Company Dashboard.

Data structure:
- DataFrame with columns: symbol, roe
- 5-10 companies (current company + peers in same sector)
- Current company: "VNM"
- Peers: ["VCF", "MCH", "DBC", "SAB", "SBT"]
- Example: VNM (ROE=25%), VCF (ROE=18%), MCH (ROE=22%)...

Requirements:
- Horizontal bar chart, sorted by ROE descending
- Current company bar: Brand blue (#295CA9), thicker (height=0.8)
- Peer bars: Gray (#6B7280), thinner (height=0.6)
- Show ROE value at end of each bar ("{value:.2f}%")
- Hover: Symbol, ROE
- X-axis: "Return on Equity (%)"

Style:
- Dark background (#0A1E42)
- Title: "Peer Comparison - ROE" (Inter font, 18px)
- Height: 300px (compact)
- Highlight current company with label "(You)"
```

**Data Loading:**
```python
# Use SectorRegistry to get peers
from config.registries import SectorRegistry

sector_reg = SectorRegistry()
peers = sector_reg.get_peers(ticker)  # Returns list of peer tickers

# Load data for all peers
peers_data = []
for peer in peers:
    peer_latest = service.get_latest_metrics(peer)
    if peer_latest:
        peers_data.append(peer_latest)

peers_df = pd.DataFrame(peers_data)
```

**Implementation Location:**
- Add to `WEBAPP/components/charts/fundamental_charts.py`:
  ```python
  def render_peer_comparison_chart(
      peers_df: pd.DataFrame,
      current_ticker: str,
      metric: str = "roe",
      height: int = 300
  ):
      """Peer comparison horizontal bar chart."""
      # Implementation here
  ```

---

### SECTION 8: Financial Data Table ✅ DONE (Minor Update)

**Current Implementation:** Working summary table

**Enhancement:** Add download button for CSV export

**Code Addition:**
```python
# After displaying st.dataframe()

csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Data (CSV)",
    data=csv,
    file_name=f"{ticker}_financial_data.csv",
    mime="text/csv",
    use_container_width=True
)
```

---

## 5. Implementation Checklist

### Step 1: Extend Existing File
```bash
# Copy current prototype as base
cp WEBAPP/pages/company_dashboard_v2.py WEBAPP/pages/1_company_dashboard.py
```

### Step 2: Add New Chart Functions
```bash
# Edit fundamental_charts.py
# Add 3 new functions:
# - render_roe_roa_chart()
# - render_balance_sheet_chart()
# - render_cash_flow_waterfall()
# - render_peer_comparison_chart()
```

### Step 3: Update Page Structure
```python
# In 1_company_dashboard.py

# After Section 3 (Margins), add:

# SECTION 4: ROE/ROA Trend
col1, col2 = st.columns(2)
with col1:
    render_margins_chart(df)  # Existing
with col2:
    render_roe_roa_chart(df)  # NEW

st.markdown("---")

# SECTION 5: Balance Sheet
st.subheader("Balance Sheet Analysis")
render_balance_sheet_chart(df)  # NEW

st.markdown("---")

# SECTION 6: Cash Flow
st.subheader("Cash Flow Breakdown")
latest_row = df.iloc[-1]
render_cash_flow_waterfall(latest_row)  # NEW

st.markdown("---")

# SECTION 7: Peer Comparison
st.subheader("Peer Comparison")

# Load peers
from config.registries import SectorRegistry
sector_reg = SectorRegistry()
peers = sector_reg.get_peers(ticker)

# Load peer data
peers_data = []
for peer in peers:
    peer_metrics = service.get_latest_metrics(peer)
    if peer_metrics:
        peers_data.append(peer_metrics)

if peers_data:
    peers_df = pd.DataFrame(peers_data)

    # Metric selector
    comparison_metric = st.selectbox(
        "Compare by",
        options=["roe", "net_margin", "revenue_growth"],
        format_func=lambda x: {
            "roe": "Return on Equity (ROE)",
            "net_margin": "Net Profit Margin",
            "revenue_growth": "Revenue Growth"
        }[x]
    )

    render_peer_comparison_chart(peers_df, ticker, comparison_metric)  # NEW
else:
    st.info("No peer data available for comparison.")

st.markdown("---")

# SECTION 8: Data Table (existing, add download)
# ... existing code ...
# Add CSV download button
```

### Step 4: Testing
```bash
# Test with different tickers
streamlit run WEBAPP/pages/1_company_dashboard.py

# Test cases:
# 1. VNM (large cap, complete data)
# 2. FPT (tech company)
# 3. HPG (steel - cyclical)
# 4. MWG (retail)
```

### Step 5: Validation
- [ ] All sections render without errors
- [ ] Charts use brand colors correctly
- [ ] Data formatting: Billions VND, 2 decimals
- [ ] Responsive layout (test narrow mode)
- [ ] Page load time < 2 seconds
- [ ] All tooltips and help text working

---

## 6. Frontend-Design Plugin Workflow

### Workflow for Each New Section:

**Step 1: Design with Plugin**
```
User: "Tôi muốn thiết kế Balance Sheet chart..."
[Provide requirements from Section 5 above]

Plugin: [Returns Plotly code]
```

**Step 2: Test Code in Notebook**
```python
# Test in Jupyter or Python REPL
import pandas as pd
import plotly.graph_objects as go

# Sample data
df = service.get_financial_data("VNM", "Quarterly", limit=8)

# Paste plugin code here
# ... test chart ...
```

**Step 3: Integrate into Component**
```python
# Add to WEBAPP/components/charts/fundamental_charts.py
def render_balance_sheet_chart(df, height=400):
    # Paste tested code
    # Adjust imports, parameters
    st.plotly_chart(fig, config=get_plotly_config(), use_container_width=True)
```

**Step 4: Use in Page**
```python
# In 1_company_dashboard.py
from WEBAPP.components.charts.fundamental_charts import render_balance_sheet_chart

render_balance_sheet_chart(df)
```

### Iteration Strategy:

1. **First Pass:** Basic functionality (get it working)
2. **Second Pass:** Apply brand colors
3. **Third Pass:** Fine-tune interactivity (hover, click)
4. **Fourth Pass:** Optimize performance

---

## 7. Performance Considerations

### Data Loading
```python
# Cache data loading (5 minutes TTL)
@st.cache_data(ttl=300, show_spinner=False)
def load_company_data(ticker, period, limit):
    return service.get_financial_data(ticker, period, limit)

# Cache service instance (indefinite)
@st.cache_resource
def get_company_service():
    return CompanyService()
```

### Chart Rendering
- Use `use_container_width=True` for responsive charts
- Limit data points: Default 8 periods, max 20
- Lazy load peer comparison (only when section is viewed)

### Expected Performance
- Page load: < 2 seconds
- Chart render: < 500ms each
- Total time to interactive: < 3 seconds

---

## 8. Success Criteria

### Functional
- ✅ All 8 sections render correctly
- ✅ Data updates when filters change
- ✅ All charts interactive (zoom, pan, hover)
- ✅ Peer comparison loads correctly
- ✅ CSV download works

### Visual
- ✅ Brand colors applied consistently
- ✅ Dark theme throughout
- ✅ Professional, clean layout
- ✅ Responsive on all screen sizes

### Performance
- ✅ Load time < 2s
- ✅ No errors in console
- ✅ Smooth interactions

---

## 9. Next Steps After Completion

Once Company Dashboard is complete:

1. **User Testing:** Get feedback from 2-3 users
2. **Iterate:** Fix any issues found
3. **Document:** Add screenshots to README
4. **Template:** Use as template for Bank and Security dashboards
5. **Move to Next:** Start Bank Dashboard (02_bank_dashboard.md)

---

**Status:** 📝 READY FOR IMPLEMENTATION
**Estimated Time:** 2-3 days
**Dependencies:** CompanyService (done), fundamental_charts.py (needs new functions)
