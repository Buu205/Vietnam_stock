# Phase 2: Sector Dashboard Refactor

**Phase ID:** 02
**Status:** Pending
**Dependencies:** Phase 1 (complete)
**Parallel With:** Phase 3 (can run simultaneously)
**Estimated Effort:** Day 2-3

---

## File Ownership (EXCLUSIVE)

| File | Action | Lines |
|------|--------|-------|
| `WEBAPP/pages/sector/sector_dashboard.py` | MODIFY | ~300 |
| `WEBAPP/services/sector_service.py` | MODIFY | +50 |

---

## Task Checklist

### 2.1 Add VNIndex Tab with 3 Variants

- [ ] Add new tab to sector_dashboard.py: "VNIndex Analysis"
- [ ] Implement 3 metric cards side-by-side:
  - VNINDEX PE/PB
  - VNINDEX_EXCLUDE PE/PB
  - BSC_INDEX PE/PB
- [ ] Load data from `DATA/processed/market_indices/vnindex_valuation.parquet`
- [ ] Add candlestick distribution chart showing 3 variants
- [ ] Add selectbox to choose individual index
- [ ] Add line_with_statistical_bands for selected index
- [ ] Add histogram_with_stats (new function from Phase 1)

### 2.2 Add Histogram to Individual Sector Tab

- [ ] Import `histogram_with_stats` from `valuation_charts.py`
- [ ] Add histogram below line chart in Individual Sector view
- [ ] Layout: Left (70%) line chart, Right (30%) histogram
- [ ] Use `st.columns([0.7, 0.3])`
- [ ] Pass sector PE data to histogram

### 2.3 Refactor All Charts to Use chart_schema

- [ ] Replace hardcoded values with config:
  ```python
  # Before
  fig.update_layout(height=500)

  # After
  from WEBAPP.core.chart_schema import get_chart_config
  config = get_chart_config('candlestick_distribution')
  fig.update_layout(height=config.height)
  ```
- [ ] Update `distribution_candlestick()` calls to use schema
- [ ] Update `line_with_statistical_bands()` calls to use schema
- [ ] Update marker sizes from `MarkerConfig`

### 2.4 Standardize Outlier Filtering

- [ ] Replace hardcoded `pe <= 100` with config:
  ```python
  from WEBAPP.core.valuation_config import filter_outliers
  clean_data = filter_outliers(pe_data, 'PE')
  ```
- [ ] Update all filtering in sector_dashboard.py:
  - Line ~214: `clean_data = metric_data[(metric_data > 0) & (metric_data <= 100)]`
  - Line ~378-383: `filtered_data[(pe <= 100) & (pb <= 100)]`

### 2.5 Update SectorService

- [ ] Add method to load VNIndex variants:
  ```python
  def get_vnindex_valuation(self, index_type: str = "VNINDEX") -> pd.DataFrame:
      """Load VNINDEX, VNINDEX_EXCLUDE, or BSC_INDEX data."""
  ```
- [ ] Ensure `get_sector_history()` applies consistent outlier filtering
- [ ] Import `OUTLIER_LIMITS` from `valuation_config.py`

### 2.6 Fix Y-Axis Scaling

- [ ] Use `Y_AXIS_DISPLAY_RANGE` for all charts:
  ```python
  from WEBAPP.core.chart_schema import get_y_range
  y_range = get_y_range(metric_label)
  fig.update_layout(yaxis=dict(range=list(y_range)))
  ```
- [ ] Apply tighter ranges: PE (0,50), PB (0,8)

---

## Tab Structure (Target)

```
Sector & Valuation Dashboard
├── Tab 1: Sector Distribution (candlestick all 19 sectors)
│   ├── Metric Radio: PE | PB | PS | EV/EBITDA
│   ├── Candlestick Chart (sorted by current value)
│   └── Legend + Export Button
│
├── Tab 2: Individual Sector Analysis
│   ├── Sector Selectbox (19 sectors)
│   ├── 4 Metric Cards (Current, Median, Z-Score, Percentile)
│   ├── Row: [Line Chart 70%] [Histogram 30%]
│   └── Stock Table + Export
│
├── Tab 3: VNIndex Analysis (NEW)
│   ├── 3 Metric Cards (VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX)
│   ├── Candlestick Distribution (3 indices)
│   ├── Index Selectbox
│   ├── Row: [Line Chart] [Histogram]
│   └── Comparison Table
│
├── Tab 4: Macro & Commodity
└── Tab 5: Data Export
```

---

## Verification Checklist

- [ ] VNIndex tab displays 3 variants correctly
- [ ] Histogram renders in Individual Sector tab
- [ ] All charts use chart_schema configs
- [ ] Outlier filtering uses `filter_outliers()`
- [ ] Y-axis uses tighter display ranges
- [ ] No hardcoded PE max=100 or PB max=100

---

## Code Templates

### VNIndex Tab Layout

```python
with tabs[2]:  # VNIndex Analysis
    st.markdown("### VNIndex Valuation Analysis")

    # 3 Metric Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("VNINDEX", vnindex_data)
    with col2:
        render_metric_card("VNINDEX_EXCLUDE", exclude_data)
    with col3:
        render_metric_card("BSC_INDEX", bsc_data)

    # Candlestick Distribution
    candlestick_data = prepare_vnindex_candlestick(all_data)
    fig = distribution_candlestick(candlestick_data, metric_label=metric)
    st.plotly_chart(fig, use_container_width=True)

    # Individual Index Analysis
    selected_index = st.selectbox(
        "Select Index",
        ["VNINDEX", "VNINDEX_EXCLUDE", "BSC_INDEX"]
    )

    col_line, col_hist = st.columns([0.7, 0.3])
    with col_line:
        fig_line, stats = line_with_statistical_bands(index_df, ...)
        st.plotly_chart(fig_line, use_container_width=True)
    with col_hist:
        fig_hist = histogram_with_stats(index_df[value_col], ...)
        st.plotly_chart(fig_hist, use_container_width=True)
```

### Import Updates

```python
# Add to sector_dashboard.py imports
from WEBAPP.core.chart_schema import (
    get_chart_config,
    get_y_range,
    CHART_SCHEMA
)
from WEBAPP.components.charts.valuation_charts import (
    distribution_candlestick,
    line_with_statistical_bands,
    histogram_with_stats  # NEW
)
from WEBAPP.core.valuation_config import filter_outliers
```

---

## Exit Criteria

1. VNIndex tab fully functional
2. Histogram visible in Individual Sector tab
3. All charts use chart_schema configs
4. Zero hardcoded outlier limits
5. Y-axis scaling consistent across charts
