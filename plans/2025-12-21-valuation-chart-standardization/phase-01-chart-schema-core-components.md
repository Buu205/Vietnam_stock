# Phase 1: Chart Schema & Core Components

**Phase ID:** 01
**Status:** Pending
**Dependencies:** None (Foundation)
**Parallel With:** None
**Estimated Effort:** Day 1-2

---

## File Ownership (EXCLUSIVE)

| File | Action | Lines |
|------|--------|-------|
| `WEBAPP/core/chart_schema.py` | CREATE | +350 |
| `WEBAPP/core/valuation_config.py` | UPDATE | +30 |
| `WEBAPP/components/charts/valuation_charts.py` | UPDATE | +100 |
| `WEBAPP/components/charts/table_builders.py` | CREATE | +150 |
| `WEBAPP/components/filters/valuation_filters.py` | CREATE | +80 |
| `WEBAPP/components/filters/__init__.py` | CREATE | +5 |

---

## Task Checklist

### 1.1 Create `chart_schema.py`

- [ ] Create file at `WEBAPP/core/chart_schema.py`
- [ ] Implement all dataclass configs:
  - `LayoutConfig` - height, margins, padding
  - `AxisConfig` - grid, tick styles
  - `MarkerConfig` - trailing=10, forward=10
  - `StatusColors` - 5 percentile-based colors
  - `ChartColors` - line, band, marker colors
  - `TypographyConfig` - font families and sizes
  - `HoverConfig` - tooltip styling
- [ ] Implement chart-specific configs:
  - `CandlestickDistributionConfig` - height=500, x_tick_angle=-45
  - `LineWithBandsConfig` - height=400, line_width=2.5
  - `HistogramConfig` - height=300, bins=35
  - `BoxWithMarkersConfig` - height=500
  - `DualAxisConfig` - height=450
  - `SparklineConfig` - height=80
- [ ] Implement constants:
  - `Y_AXIS_DISPLAY_RANGE` - PE (0,50), PB (0,8), etc.
  - `OUTLIER_LIMITS` - PE max=100, PB max=20, etc.
  - `PERCENTILE_THRESHOLDS` - 5 status ranges
- [ ] Implement accessor functions:
  - `get_chart_config(chart_type)`
  - `get_y_range(metric)`
  - `get_outlier_limits(metric)`
  - `get_status_color(percentile)`

### 1.2 Update `valuation_config.py`

- [ ] Import from `chart_schema.py`:
  ```python
  from WEBAPP.core.chart_schema import (
      CHART_SCHEMA, Y_AXIS_DISPLAY_RANGE, get_status_color
  )
  ```
- [ ] Keep backward-compatible exports
- [ ] Add alias: `OUTLIER_RULES = OUTLIER_LIMITS`

### 1.3 Add `histogram_with_stats()` to `valuation_charts.py`

- [ ] Implement histogram function:
  ```python
  def histogram_with_stats(
      data: pd.Series,
      metric_label: str = "PE",
      height: int = 300,
      bins: int = 35,
      show_mean_std: bool = True,
      current_value: float = None
  ) -> go.Figure
  ```
- [ ] Features:
  - Bar chart for value distribution
  - Vertical dashed lines for mean, ±1σ, ±2σ
  - Triangle marker for current value
  - Use `HistogramConfig` from chart_schema
- [ ] Update imports to use chart_schema

### 1.4 Create `table_builders.py`

- [ ] Create file at `WEBAPP/components/charts/table_builders.py`
- [ ] Implement functions:
  ```python
  def sector_comparison_table(data, metric="PE", columns=None) -> str
  def stock_valuation_table(df, columns=None, format_rules=None) -> str
  def forward_matrix_table(df, metrics=['pe', 'pb']) -> str
  ```
- [ ] Use formatters from `valuation_config.py`:
  - `format_ratio()`, `format_percent()`, `format_zscore()`
- [ ] Include CSS styling (inline or from theme)

### 1.5 Create `valuation_filters.py`

- [ ] Create directory: `WEBAPP/components/filters/`
- [ ] Create `__init__.py` with exports
- [ ] Create `valuation_filters.py` with:
  ```python
  def metric_selector(key="metric") -> str
  def time_range_selector(key="time_range") -> int
  def sector_selector(sectors, key="sector") -> str
  def ticker_search(key="ticker_search") -> str
  ```
- [ ] Return Streamlit widgets with consistent styling

---

## Verification Checklist

- [ ] `chart_schema.py` imports without errors
- [ ] `valuation_config.py` backward-compatible
- [ ] `histogram_with_stats()` renders correctly
- [ ] `table_builders.py` outputs valid HTML
- [ ] `valuation_filters.py` widgets work in sidebar

---

## Code Templates

### chart_schema.py (key sections)

```python
from dataclasses import dataclass
from typing import Dict, Any, Tuple

@dataclass
class MarkerConfig:
    size_trailing: int = 10
    size_forward: int = 10
    size_small: int = 8
    size_large: int = 12
    border_width: float = 1.5
    border_color: str = "white"

@dataclass
class HistogramConfig:
    chart_type: str = "histogram"
    height: int = 300
    bins: int = 35
    bar_color: str = "#8B5CF6"
    bar_opacity: float = 0.7
    mean_line_color: str = "#F59E0B"
    sd_line_color: str = "#4A7BC8"
    show_mean_std: bool = True
    show_current_marker: bool = True
    current_marker_color: str = "#00D4AA"
```

### histogram_with_stats() signature

```python
def histogram_with_stats(
    data: pd.Series,
    metric_label: str = "PE",
    height: int = None,
    bins: int = None,
    show_mean_std: bool = True,
    current_value: float = None
) -> go.Figure:
    """
    Histogram with mean ±1σ, ±2σ vertical lines.

    Args:
        data: Series of values (already filtered for outliers)
        metric_label: "PE" | "PB" | "PS" | "EV_EBITDA"
        height: Chart height (default from HistogramConfig)
        bins: Number of bins (default 35)
        show_mean_std: Show vertical lines for mean, std
        current_value: Current value to mark with triangle

    Returns:
        Plotly Figure
    """
```

---

## Exit Criteria

1. All 6 files created/updated
2. Zero import errors
3. All functions have docstrings
4. Unit tests pass (if applicable)
