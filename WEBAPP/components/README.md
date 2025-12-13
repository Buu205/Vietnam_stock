# Component Library Documentation

## 📋 Overview

Reusable Streamlit components for Vietnam Stock Dashboard redesign.
**Version:** 2.0.0
**Date:** 2025-12-12

---

## 🏗️ Structure

```
WEBAPP/components/
├── charts/                   # Plotly chart builders
│   ├── __init__.py
│   └── plotly_builders.py    # PlotlyChartBuilder class
│
├── navigation/               # Navigation components
│   ├── __init__.py
│   ├── main_nav.py           # Main category navigation
│   └── breadcrumbs.py        # Breadcrumb trail
│
├── inputs/                   # Input controls
│   ├── __init__.py
│   ├── symbol_selector.py    # Symbol dropdown
│   └── date_range.py         # Date range picker
│
├── data_display/             # Data display
│   ├── __init__.py
│   └── metric_cards.py       # KPI metric cards
│
└── README.md                 # This file
```

---

## 🚀 Quick Start

### 1. Import Components

```python
# Charts
from WEBAPP.components.charts import PlotlyChartBuilder as pcb

# Navigation
from WEBAPP.components.navigation import render_main_nav, render_breadcrumbs

# Inputs
from WEBAPP.components.inputs import symbol_selector, date_range_picker

# Data Display
from WEBAPP.components.data_display import metric_card_row
```

### 2. Build a Page

```python
import streamlit as st
from WEBAPP.components.charts import PlotlyChartBuilder as pcb
from WEBAPP.components.navigation import render_main_nav, render_breadcrumbs

# Page config
st.set_page_config(page_title="My Page", layout="wide")

# Navigation
render_main_nav()
render_breadcrumbs(["Home", "Category", "Page"])

# Load data (your code)
df = load_data()

# Build chart
fig = pcb.bar_line_combo(
    df=df,
    x_col='quarter',
    bar_col='revenue',
    line_col='revenue_ma4',
    title='Revenue Trend'
)

# Display
st.plotly_chart(fig, use_container_width=True)
```

---

## 📊 Chart Components

### PlotlyChartBuilder

Main class for building Plotly charts.

#### Available Methods

##### 1. `line_chart()` - Multi-line chart

```python
fig = pcb.line_chart(
    df=data,
    x_col='quarter',
    y_cols=['revenue', 'profit', 'ebitda'],
    title='Financial Metrics',
    y_axis_title='VND (billions)'
)
```

**Use cases:** Trend analysis, multiple metrics comparison

---

##### 2. `bar_chart()` - Simple bar chart

```python
fig = pcb.bar_chart(
    df=data,
    x_col='quarter',
    y_col='revenue_growth_yoy',
    title='Revenue Growth YoY',
    color='#10B981',
    show_values=True
)
```

**Use cases:** Growth rates, categorical comparisons

---

##### 3. `bar_line_combo()` - Bar + Line overlay (⭐ MOST USED)

```python
fig = pcb.bar_line_combo(
    df=data,
    x_col='quarter',
    bar_col='net_revenue',
    line_col='net_revenue_ma4',
    title='Revenue with MA4',
    bar_name='Revenue',
    line_name='MA4 Trend'
)
```

**Use cases:** Value + moving average, actual vs target

**Replaces:** PyEcharts `bar.overlap(line)` pattern (300+ LOC eliminated)

---

##### 4. `candlestick_chart()` - Candlestick for PE/PB

```python
# Data must have: date, open, high, low, close
fig = pcb.candlestick_chart(
    df=pe_data,
    title='PE Ratio Candlestick - ACB',
    show_rangeslider=False
)
```

**Use cases:** PE/PB valuation analysis, price charts

**Matches:** User's `render_pe_pb_dotplot()` function

---

##### 5. `heatmap()` - Sector comparison

```python
fig = pcb.heatmap(
    data=sector_matrix,  # 2D DataFrame
    title='Sector PE Heatmap',
    x_label='Sectors',
    y_label='Metrics',
    colorscale='RdYlGn_r'
)
```

**Use cases:** Sector comparison, correlation matrices

---

##### 6. `line_with_bands()` - Statistical bands

```python
fig = pcb.line_with_bands(
    df=pe_data,
    x_col='date',
    y_col='pe_ratio',
    mean_col='pe_mean',
    std_col='pe_std',
    title='PE Ratio with ±1σ Bands',
    num_std=1
)
```

**Use cases:** Valuation percentiles, volatility analysis

---

##### 7. `waterfall_chart()` - Cash flow waterfall

```python
fig = pcb.waterfall_chart(
    categories=['Operating CF', 'Investing CF', 'Financing CF', 'Net Change'],
    values=[1000, -500, -200, 300],
    title='Cash Flow Waterfall'
)
```

**Use cases:** Cash flow analysis, change breakdown

---

### Convenience Functions

Pre-configured chart templates:

```python
# Revenue trend (bar + line combo)
fig = revenue_trend_chart(df, symbol='VNM')

# Profitability margins (multi-line)
fig = profitability_chart(df, symbol='ACB')

# PE candlestick
fig = pe_candlestick_chart(df, symbol='HPG')
```

---

## 🧭 Navigation Components

### `render_main_nav()`

Display top-level category navigation (4 categories).

```python
from WEBAPP.components.navigation import render_main_nav

render_main_nav()
# Shows: [📊 Fundamental] [💰 Valuation] [📈 Technical] [🔍 Intelligence]
```

---

### `render_breadcrumbs()`

Display breadcrumb trail.

```python
from WEBAPP.components.navigation import render_breadcrumbs

render_breadcrumbs(["Home", "Fundamental Analysis", "Company Analysis"])
# Shows: Home > Fundamental Analysis > Company Analysis
```

---

## 🎛️ Input Components

### `symbol_selector()`

Enhanced symbol dropdown with sector info.

```python
from WEBAPP.components.inputs import symbol_selector

symbol = symbol_selector(
    entity_type='company',  # 'company', 'bank', 'security', 'insurance', 'all'
    default='VNM',
    key='my_symbol_selector'
)

# Returns: 'VNM', 'ACB', etc.
```

**Features:**
- Filter by entity type
- Show sector/industry info
- Search functionality (built-in Streamlit)

---

### `date_range_picker()`

Date range picker with quick presets.

```python
from WEBAPP.components.inputs import date_range_picker

start_date, end_date = date_range_picker(
    default_start='2023-01-01',
    default_end='2025-12-12',
    key='my_date_range'
)

# Returns: ('2023-01-01', '2025-12-12')
```

**Presets:**
- Last 1/2/3/5 Years
- All Time
- Custom

---

## 📈 Data Display Components

### `metric_card_row()`

Display KPI metrics in a row.

```python
from WEBAPP.components.data_display import metric_card_row

metric_card_row([
    {
        'label': 'Net Revenue',
        'value': 1234.56,
        'delta': 12.3,
        'format': 'billions',
        'delta_format': 'percent'
    },
    {
        'label': 'ROE',
        'value': 18.5,
        'delta': 2.3,
        'format': 'percent',
        'delta_format': 'percent'
    }
])
```

**Format types:**
- `'number'`: 1,234,567
- `'billions'`: 1.23B VND
- `'percent'`: 12.34%
- `'ratio'`: 1.23x

---

## 🎨 Color Palette

Consistent colors across all charts:

```python
PlotlyChartBuilder.COLORS = {
    'primary': '#1E40AF',    # Deep blue
    'secondary': '#10B981',  # Green
    'accent': '#F59E0B',     # Amber
    'danger': '#EF4444',     # Red
    'chart': [
        '#1E40AF', '#10B981', '#F59E0B', '#EF4444',
        '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'
    ]
}
```

---

## 🧪 Testing

### Run Demo Page

```bash
streamlit run WEBAPP/pages/1_fundamental/company_analysis_demo.py
```

This demo page shows:
- ✅ All chart types in action
- ✅ Symbol selector + date range picker
- ✅ Metric cards
- ✅ Navigation components
- ✅ Error handling

---

## 📝 Code Examples

### Example 1: Simple Revenue Chart

```python
import streamlit as st
import pandas as pd
from WEBAPP.components.charts import PlotlyChartBuilder as pcb

# Load data
df = pd.read_parquet('company_financial_metrics.parquet')
df = df[df['symbol'] == 'VNM']

# Build chart
fig = pcb.bar_line_combo(
    df=df,
    x_col='quarter',
    bar_col='net_revenue',
    line_col='net_revenue_ma4',
    title='VNM Revenue Trend'
)

# Display
st.plotly_chart(fig, use_container_width=True)
```

---

### Example 2: Complete Page Template

```python
import streamlit as st
from WEBAPP.components.charts import PlotlyChartBuilder as pcb
from WEBAPP.components.navigation import render_main_nav, render_breadcrumbs
from WEBAPP.components.inputs import symbol_selector
from WEBAPP.components.data_display import metric_card_row
from WEBAPP.core.data_paths import DataPaths

# Page config
st.set_page_config(page_title="My Page", layout="wide")

# Navigation
render_main_nav()
render_breadcrumbs(["Home", "My Category", "My Page"])

# Sidebar
with st.sidebar:
    symbol = symbol_selector(entity_type='company', default='VNM')

# Load data
@st.cache_data(ttl=3600)
def load_data(symbol):
    path = DataPaths.fundamental('company')
    df = pd.read_parquet(path)
    return df[df['symbol'] == symbol]

data = load_data(symbol)

# Display metrics
latest = data.iloc[0]
metric_card_row([
    {'label': 'Revenue', 'value': latest['net_revenue'], 'format': 'billions'}
])

# Display chart
fig = pcb.line_chart(data, 'quarter', ['net_revenue'], 'Revenue')
st.plotly_chart(fig, use_container_width=True)
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"

**Solution:** Ensure project root is in Python path:

```python
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))
```

---

### Issue: "Column not found in DataFrame"

**Solution:** Check available columns:

```python
st.write("Available columns:", data.columns.tolist())
```

Charts handle missing columns gracefully with error messages.

---

### Issue: Chart shows "Error: ..."

**Solution:** Check DataFrame structure:

```python
st.write(data.head())
st.write(data.dtypes)
```

Ensure required columns exist and have correct data types.

---

## 🔗 Integration with Existing System

### Data Loading (Parquet-centric)

Always use `DataPaths`:

```python
from WEBAPP.core.data_paths import DataPaths

# Load fundamental data
company_path = DataPaths.fundamental('company')
df = pd.read_parquet(company_path)

# Load valuation data
pe_path = DataPaths.valuation('pe')
pe_df = pd.read_parquet(pe_path)

# Load technical data
tech_path = DataPaths.technical('basic')
tech_df = pd.read_parquet(tech_path)
```

### Registry Integration

Use registries for metadata:

```python
from config.registries import MetricRegistry, SectorRegistry

# Metric info
metric_reg = MetricRegistry()
metric = metric_reg.get_metric('CIS_10', 'COMPANY')

# Sector info
sector_reg = SectorRegistry()
peers = sector_reg.get_peers('VNM')
```

---

## 📚 Additional Resources

- **Full Plan:** `/Users/buuphan/Dev/Vietnam_dashboard/streamlit_ui_redesign_plan.md`
- **Demo Page:** `WEBAPP/pages/1_fundamental/company_analysis_demo.py`
- **AI Integration:** `finance_glm_plan.md` (Section 2: AI Formula Generation)
- **Data Paths:** `WEBAPP/core/data_paths.py`

---

## 🚦 Next Steps

1. ✅ **Test demo page:**
   ```bash
   streamlit run WEBAPP/pages/1_fundamental/company_analysis_demo.py
   ```

2. ✅ **Create your first page:**
   - Copy `company_analysis_demo.py` as template
   - Modify data loading for your entity type
   - Customize charts

3. ✅ **Follow implementation plan:**
   - Week 1: Foundation components (DONE)
   - Week 2: Migrate FA pages
   - Week 3: Valuation & TA pages
   - Week 4: Polish & testing

---

## 💡 Tips

1. **Always use `use_container_width=True`** for responsive charts:
   ```python
   st.plotly_chart(fig, use_container_width=True)
   ```

2. **Cache data loading** to avoid redundant reads:
   ```python
   @st.cache_data(ttl=3600)
   def load_data(symbol):
       ...
   ```

3. **Handle missing data gracefully:**
   ```python
   if 'column' in df.columns:
       # Build chart
   else:
       st.info("Chart requires 'column'")
   ```

4. **Use convenience functions** for common patterns:
   ```python
   fig = revenue_trend_chart(df, symbol='VNM')
   ```

---

**Happy coding! 🚀**
