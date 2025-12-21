# Phase 3: Forecast Dashboard Isolation

**Phase ID:** 03
**Status:** Pending
**Dependencies:** Phase 1 (complete)
**Parallel With:** Phase 2 (can run simultaneously)
**Estimated Effort:** Day 2-3

---

## File Ownership (EXCLUSIVE)

| File | Action | Lines |
|------|--------|-------|
| `WEBAPP/pages/forecast/forecast_dashboard.py` | MODIFY | ~200 |
| `WEBAPP/services/forecast_service.py` | MODIFY | +30 |

---

## Task Checklist

### 3.1 Add Forward Valuation Matrix

- [ ] Create matrix table showing TTM vs Forward comparison:
  ```
  | Symbol | PE TTM | PE 2025F | PE 2026F | Δ 2025 | Δ 2026 | Status |
  |--------|--------|----------|----------|--------|--------|--------|
  | ACB    | 10.5x  | 8.2x     | 7.5x     | -22%   | -29%   | Cheap  |
  ```
- [ ] Load data from `DATA/processed/forecast/bsc/bsc_combined.parquet`
- [ ] Use columns: `pe_ttm`, `pe_fwd_2025`, `pe_fwd_2026`
- [ ] Calculate delta: `(fwd - ttm) / ttm * 100`
- [ ] Import `forward_matrix_table()` from `table_builders.py`

### 3.2 Update Box Chart for 2025 + 2026 Markers

- [ ] Modify `valuation_box_with_markers()` to accept:
  ```python
  pe_forward_data = {
      'symbol': {
          '2025': pe_fwd_2025,
          '2026': pe_fwd_2026
      }
  }
  ```
- [ ] Add dual forward markers:
  - ◇ Hollow diamond for 2025
  - ◆ Filled diamond for 2026
- [ ] Update legend to explain 3 marker types:
  - ● TTM/Current
  - ◇ Forward 2025
  - ◆ Forward 2026
- [ ] Use chart_schema colors for markers

### 3.3 Load BSC Data from Correct Path

- [ ] Update ForecastService to load from:
  ```python
  BSC_DATA_PATH = "DATA/processed/forecast/bsc/"
  ```
- [ ] Load files:
  - `bsc_combined.parquet` - 93 stocks × 32 columns
  - `bsc_sector_valuation.parquet` - sector-level forward PE/PB
- [ ] Ensure columns available: `pe_fwd_2025`, `pe_fwd_2026`, `pb_fwd_2025`, `pb_fwd_2026`

### 3.4 Refactor Charts to Use chart_schema

- [ ] Update all chart calls to use schema:
  ```python
  from WEBAPP.core.chart_schema import get_chart_config, CHART_SCHEMA
  config = get_chart_config('box_with_markers')
  ```
- [ ] Use `MarkerConfig` for marker sizes
- [ ] Use `ChartColors.forward_marker` for forward markers
- [ ] Apply `Y_AXIS_DISPLAY_RANGE` for y-axis

### 3.5 Standardize Number Formatting

- [ ] Use formatters from `valuation_config.py`:
  ```python
  from WEBAPP.core.valuation_config import format_ratio, format_percent
  ```
- [ ] Format PE/PB as `15.2x`
- [ ] Format delta as `+12.5%` or `-8.3%`
- [ ] Format percentile as `75%`

---

## Tab Structure (Target)

```
BSC Forecast Dashboard
├── Tab 1: Forecast Summary
│   ├── Top 10 Upside Stocks
│   ├── Sector Coverage Cards
│   └── Rating Distribution (BUY/HOLD/SELL)
│
├── Tab 2: Forward Valuation Matrix (NEW)
│   ├── Metric Toggle: PE | PB
│   ├── Matrix Table: TTM vs 2025F vs 2026F
│   ├── Highlight: Δ < -20% = green, Δ > 20% = red
│   └── Export Button
│
├── Tab 3: Individual Stock Analysis
│   ├── Stock Selectbox (93 BSC-covered stocks)
│   ├── Box Chart: Historical + TTM + 2025F + 2026F markers
│   ├── Sector Comparison Row
│   └── Target Price Analysis
│
└── Tab 4: Sector Forward Valuations
    ├── Sector PE 2025F vs 2026F
    └── Sector PB 2025F vs 2026F
```

---

## Verification Checklist

- [ ] Forward matrix table displays correctly
- [ ] Box chart shows 3 marker types (TTM, 2025, 2026)
- [ ] BSC data loads from correct path
- [ ] All charts use chart_schema configs
- [ ] Number formatting consistent

---

## Code Templates

### Forward Valuation Matrix

```python
def render_forward_matrix_tab(bsc_df: pd.DataFrame, metric: str = "pe"):
    """Render TTM vs Forward comparison matrix."""
    st.markdown("### Forward Valuation Matrix")

    # Calculate deltas
    df = bsc_df.copy()
    df['delta_2025'] = (df[f'{metric}_fwd_2025'] - df[f'{metric}_ttm']) / df[f'{metric}_ttm'] * 100
    df['delta_2026'] = (df[f'{metric}_fwd_2026'] - df[f'{metric}_ttm']) / df[f'{metric}_ttm'] * 100

    # Format columns
    from WEBAPP.core.valuation_config import format_ratio, format_change
    df['pe_ttm_fmt'] = df[f'{metric}_ttm'].apply(lambda x: format_ratio(x, 1))
    df['pe_2025_fmt'] = df[f'{metric}_fwd_2025'].apply(lambda x: format_ratio(x, 1))
    df['pe_2026_fmt'] = df[f'{metric}_fwd_2026'].apply(lambda x: format_ratio(x, 1))
    df['delta_2025_fmt'] = df['delta_2025'].apply(format_change)
    df['delta_2026_fmt'] = df['delta_2026'].apply(format_change)

    # Display table
    from WEBAPP.components.charts.table_builders import forward_matrix_table
    table_html = forward_matrix_table(df, metrics=[metric])
    st.markdown(table_html, unsafe_allow_html=True)
```

### Box Chart with Dual Forward Markers

```python
def valuation_box_with_markers(
    stats_data: List[Dict],
    pe_forward_data: Dict = None,  # {symbol: {'2025': val, '2026': val}}
    metric_label: str = "PE",
    ...
):
    config = get_chart_config('box_with_markers')
    marker_config = CHART_SCHEMA['marker']
    colors = CHART_SCHEMA['chart_colors']

    # Add forward 2025 markers (hollow diamond)
    if pe_forward_data:
        for symbol, fwd_values in pe_forward_data.items():
            if '2025' in fwd_values:
                fig.add_trace(go.Scatter(
                    x=[symbol],
                    y=[fwd_values['2025']],
                    mode='markers',
                    marker=dict(
                        symbol='diamond-open',
                        size=marker_config.size_forward,
                        color=colors.forward_marker,
                        line=dict(width=2, color=colors.forward_marker)
                    ),
                    name='Forward 2025',
                    showlegend=...
                ))

            if '2026' in fwd_values:
                fig.add_trace(go.Scatter(
                    x=[symbol],
                    y=[fwd_values['2026']],
                    mode='markers',
                    marker=dict(
                        symbol='diamond',
                        size=marker_config.size_forward,
                        color='#FF6B6B',  # Different color for 2026
                        line=dict(width=1.5, color='white')
                    ),
                    name='Forward 2026',
                    showlegend=...
                ))
```

### Import Updates

```python
# Add to forecast_dashboard.py imports
from WEBAPP.core.chart_schema import (
    get_chart_config,
    get_y_range,
    CHART_SCHEMA
)
from WEBAPP.core.valuation_config import (
    format_ratio,
    format_percent,
    format_change,
    filter_outliers
)
from WEBAPP.components.charts.table_builders import forward_matrix_table
```

---

## Exit Criteria

1. Forward matrix table functional
2. Box chart shows TTM + 2025 + 2026 markers
3. BSC data loads correctly
4. All charts use chart_schema configs
5. Number formatting consistent with valuation_config
