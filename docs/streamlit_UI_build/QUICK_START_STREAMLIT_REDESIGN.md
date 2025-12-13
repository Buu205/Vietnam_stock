# 🚀 Quick Start: Streamlit UI Redesign

**Date:** 2025-12-12
**Status:** Phase 0 Complete - Foundation Components Ready

---

## ✅ What's Been Built

### Component Library (Phase 0 - COMPLETE)

```
WEBAPP/components/
├── charts/
│   └── plotly_builders.py       # ✅ PlotlyChartBuilder với 7 chart methods
├── navigation/
│   ├── main_nav.py              # ✅ Category navigation
│   └── breadcrumbs.py           # ✅ Breadcrumb trail
├── inputs/
│   ├── symbol_selector.py       # ✅ Symbol dropdown với sector info
│   └── date_range.py            # ✅ Date range picker với presets
└── data_display/
    └── metric_cards.py          # ✅ KPI metric cards
```

### Demo Page

```
WEBAPP/pages/1_fundamental/
└── company_analysis_demo.py     # ✅ Full working example
```

---

## 🎯 Quick Test (5 minutes)

### Step 1: Verify Data Files

```bash
# Check if company parquet exists
ls -lh DATA/processed/fundamental/company/company_financial_metrics.parquet
```

**If file doesn't exist:**
```bash
# Run calculator to generate it
python3 PROCESSORS/fundamental/calculators/company_calculator.py
```

---

### Step 2: Run Demo Page

```bash
cd /Users/buuphan/Dev/Vietnam_dashboard

# Run demo page
streamlit run WEBAPP/pages/1_fundamental/company_analysis_demo.py
```

**Expected result:**
- ✅ Page loads in browser (http://localhost:8501)
- ✅ Shows VNM company data (default)
- ✅ 3 tabs: Overview, Income Statement, Financial Ratios
- ✅ Charts render with Plotly (responsive, interactive)
- ✅ Symbol selector works (change to ACB, VIC, etc.)
- ✅ Date range picker works

---

### Step 3: Explore Components

**Try these interactions:**

1. **Symbol Selector (Sidebar)**
   - Change from VNM to ACB
   - Notice sector info below dropdown ("Banking | Commercial Banks")
   - Page reloads with new data

2. **Date Range Picker (Sidebar)**
   - Try "Last 1 Year" preset
   - Try "Last 3 Years" preset
   - Charts update automatically

3. **Charts (Tab 1: Overview)**
   - Hover over bars/lines to see values
   - Click legend items to hide/show series
   - Zoom in/out (drag to select area)
   - Pan (hold shift + drag)
   - Reset (double-click chart)

4. **Metric Cards (Top of Tab 1)**
   - Shows latest quarter metrics
   - Green/red delta indicators
   - Formatted values (billions, percent, ratio)

5. **Debug Info (Bottom)**
   - Expand "🔍 Debug Info"
   - See available columns in data
   - Check date range loaded

---

## 📖 Using Components in Your Own Pages

### Example: Create Banking Analysis Page

```python
"""
Banking Analysis Dashboard
"""

import streamlit as st
import pandas as pd
from WEBAPP.core.data_paths import DataPaths
from WEBAPP.components.charts import PlotlyChartBuilder as pcb
from WEBAPP.components.navigation import render_main_nav, render_breadcrumbs
from WEBAPP.components.inputs import symbol_selector, date_range_picker
from WEBAPP.components.data_display import metric_card_row

# Page config
st.set_page_config(page_title="Banking Analysis", layout="wide")

# Navigation
render_main_nav()
render_breadcrumbs(["Home", "Fundamental", "Banking"])

# Sidebar
with st.sidebar:
    symbol = symbol_selector(entity_type='bank', default='ACB')
    start_date, end_date = date_range_picker()

# Load data
@st.cache_data(ttl=3600)
def load_bank_data(symbol):
    path = DataPaths.fundamental('bank')
    df = pd.read_parquet(path)
    return df[df['symbol'] == symbol]

data = load_bank_data(symbol)

# Filter by date
data_filtered = data[
    (data['date'] >= pd.to_datetime(start_date)) &
    (data['date'] <= pd.to_datetime(end_date))
]

# Display metrics
latest = data_filtered.iloc[0]
metric_card_row([
    {'label': 'NII', 'value': latest['nii'], 'format': 'billions'},
    {'label': 'NIM', 'value': latest['nim'], 'format': 'percent'},
    {'label': 'CAR', 'value': latest['car'], 'format': 'percent'},
    {'label': 'NPL', 'value': latest['npl_ratio'], 'format': 'percent'}
])

# Display chart
fig = pcb.bar_line_combo(
    df=data_filtered,
    x_col='quarter',
    bar_col='nii',
    line_col='nii_ma4',
    title='Net Interest Income Trend'
)
st.plotly_chart(fig, use_container_width=True)
```

Save as: `WEBAPP/pages/1_fundamental/banking_analysis.py`

Run: `streamlit run WEBAPP/pages/1_fundamental/banking_analysis.py`

---

## 🎨 Chart Examples

### 1. Bar + Line Combo (Most Common)

**Use case:** Revenue with moving average

```python
fig = pcb.bar_line_combo(
    df=data,
    x_col='quarter',
    bar_col='net_revenue',
    line_col='net_revenue_ma4',
    title='Revenue Trend',
    bar_name='Revenue',
    line_name='MA4'
)
st.plotly_chart(fig, use_container_width=True)
```

**Replaces:** 50+ lines of PyEcharts code

---

### 2. Multi-line Chart

**Use case:** Compare multiple metrics

```python
fig = pcb.line_chart(
    df=data,
    x_col='quarter',
    y_cols=['gross_margin', 'ebit_margin', 'net_margin'],
    title='Profitability Margins',
    y_axis_title='Margin (%)'
)
st.plotly_chart(fig, use_container_width=True)
```

---

### 3. Candlestick Chart

**Use case:** PE/PB valuation

```python
# Data must have: date, open, high, low, close
fig = pcb.candlestick_chart(
    df=pe_data,
    title='PE Ratio Candlestick - ACB'
)
st.plotly_chart(fig, use_container_width=True)
```

**Matches:** User's `render_pe_pb_dotplot()` function

---

### 4. Heatmap

**Use case:** Sector comparison

```python
# sector_matrix is 2D DataFrame
fig = pcb.heatmap(
    data=sector_matrix,
    title='Sector PE Comparison',
    x_label='Sectors',
    y_label='Metrics',
    colorscale='RdYlGn_r'
)
st.plotly_chart(fig, use_container_width=True)
```

---

### 5. Waterfall Chart

**Use case:** Cash flow breakdown

```python
fig = pcb.waterfall_chart(
    categories=['Operating CF', 'Investing CF', 'Financing CF', 'Net'],
    values=[1000, -500, -200, 300],
    title='Cash Flow Waterfall'
)
st.plotly_chart(fig, use_container_width=True)
```

---

## 📁 File Locations

### Components
```
/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/components/
├── charts/plotly_builders.py
├── navigation/main_nav.py
├── navigation/breadcrumbs.py
├── inputs/symbol_selector.py
├── inputs/date_range.py
└── data_display/metric_cards.py
```

### Documentation
```
/Users/buuphan/Dev/Vietnam_dashboard/
├── streamlit_ui_redesign_plan.md          # Full 4-week implementation plan
├── QUICK_START_STREAMLIT_REDESIGN.md      # This file
└── WEBAPP/components/README.md            # Component library docs
```

### Demo Page
```
/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/1_fundamental/company_analysis_demo.py
```

---

## 🔧 Troubleshooting

### Issue 1: "Module not found: WEBAPP.components"

**Solution:**
```python
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))
```

---

### Issue 2: "Data file not found"

**Solution:**
```bash
# Generate company data
python3 PROCESSORS/fundamental/calculators/company_calculator.py

# Generate bank data
python3 PROCESSORS/fundamental/calculators/bank_calculator.py

# Generate valuation data
python3 PROCESSORS/valuation/calculators/run_daily_valuation_update.py
```

---

### Issue 3: "Column not found in DataFrame"

**Solution:** Check available columns in debug expander at bottom of demo page.

Some metrics may not exist for all entity types:
- `net_revenue` → Company-specific
- `nii` (Net Interest Income) → Bank-specific
- `premiums` → Insurance-specific

---

### Issue 4: Charts show "Error: ..."

**Cause:** Missing required columns

**Solution:** Use column existence checks:

```python
if 'net_revenue' in df.columns and 'net_revenue_ma4' in df.columns:
    fig = pcb.bar_line_combo(...)
else:
    st.info("Chart requires 'net_revenue' and 'net_revenue_ma4' columns")
```

---

## 📊 Performance Comparison

### Old PyEcharts Pattern (50+ lines)

```python
from pyecharts import options as opts
from pyecharts.charts import Bar, Line

bar = Bar()
bar.add_xaxis(quarters)
bar.add_yaxis("Revenue", revenues, ...)
bar.set_global_opts(
    title_opts=opts.TitleOpts(title="Revenue"),
    xaxis_opts=opts.AxisOpts(...),
    yaxis_opts=opts.AxisOpts(...),
    ...
)

line = Line()
line.add_xaxis(quarters)
line.add_yaxis("MA4", ma4_values, ...)
line.set_global_opts(...)

chart = bar.overlap(line)
st_pyecharts(chart, height="400px")
```

### New Plotly Pattern (5 lines)

```python
from WEBAPP.components.charts import PlotlyChartBuilder as pcb

fig = pcb.bar_line_combo(
    df=df, x_col='quarter', bar_col='net_revenue',
    line_col='net_revenue_ma4', title='Revenue Trend'
)
st.plotly_chart(fig, use_container_width=True)
```

**Benefits:**
- ✅ 90% less code
- ✅ Responsive (auto-scales)
- ✅ Interactive (zoom, pan, export)
- ✅ Consistent styling
- ✅ Better error handling

---

## 🎯 Next Steps

### Week 1 (Current): Foundation ✅

- [x] Create PlotlyChartBuilder (7 chart methods)
- [x] Create navigation components
- [x] Create input components
- [x] Create data display components
- [x] Build demo page
- [x] Write documentation

### Week 2: Migrate FA Pages

- [ ] Company Analysis (2 days)
- [ ] Banking Analysis (1 day)
- [ ] Securities Analysis (1 day)
- [ ] Insurance Analysis (1 day)

**To start:**
1. Copy `company_analysis_demo.py` as template
2. Modify for each entity type
3. Test with real data

### Week 3: Valuation & TA Pages

- [ ] Valuation Dashboard (2 days)
- [ ] Stock Technical (2 days)
- [ ] Market Technical (1 day)

### Week 4: Polish & AI Integration

- [ ] Analyst Forecasts (1 day)
- [ ] News & Sentiment (1 day)
- [ ] AI Formula Explorer (2 days) - NEW
- [ ] Theme & testing (2 days)

---

## 💡 Tips

1. **Always cache data loading:**
   ```python
   @st.cache_data(ttl=3600)  # 1 hour
   def load_data(symbol):
       ...
   ```

2. **Use `use_container_width=True` for responsive charts:**
   ```python
   st.plotly_chart(fig, use_container_width=True)
   ```

3. **Load data ONCE per page:**
   ```python
   # ✅ GOOD: Single load
   data = load_data(symbol)

   # ❌ BAD: Multiple loads
   data1 = pd.read_parquet(path)
   data2 = pd.read_parquet(path)  # Redundant!
   ```

4. **Check column existence before using:**
   ```python
   if 'column' in df.columns:
       # Use column
   else:
       st.info("Column not available")
   ```

---

## 📚 Additional Resources

- **Full Plan:** `streamlit_ui_redesign_plan.md` (60+ pages, complete architecture)
- **Component Docs:** `WEBAPP/components/README.md` (API reference)
- **AI Integration:** `finance_glm_plan.md` (Section 2: AI Formula Generation)
- **Demo Page:** `WEBAPP/pages/1_fundamental/company_analysis_demo.py`

---

## 🤝 Getting Help

**Check these first:**
1. Component README: `WEBAPP/components/README.md`
2. Demo page: `company_analysis_demo.py`
3. Full plan: `streamlit_ui_redesign_plan.md`

**Common solutions:**
- Missing data? → Run calculators to generate parquet files
- Module not found? → Add project root to Python path
- Column not found? → Check debug info in demo page

---

## 🚀 Ready to Build?

```bash
# 1. Test demo page
streamlit run WEBAPP/pages/1_fundamental/company_analysis_demo.py

# 2. Copy template
cp WEBAPP/pages/1_fundamental/company_analysis_demo.py \
   WEBAPP/pages/1_fundamental/my_new_page.py

# 3. Customize for your needs

# 4. Run your page
streamlit run WEBAPP/pages/1_fundamental/my_new_page.py
```

**Chúc may mắn! 🎉**
