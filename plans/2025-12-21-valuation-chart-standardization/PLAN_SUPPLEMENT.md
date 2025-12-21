# Plan Supplement: Comprehensive Valuation Chart Standardization

**Date:** 2025-12-21
**Status:** Draft - Pending Approval
**Parent Plan:** `plans/2025-12-21-valuation-chart-standardization/PLAN.md`

---

## 1. CHART TYPE TAXONOMY (Expanded)

### 1.1 Type A: TTM Historical Distribution (No Forward Data)

**Use Case:** Sector comparison, VNIndex analysis, historical percentile ranking

**Chart Sub-types:**

| Sub-type | Description | Use Case |
|----------|-------------|----------|
| **A1: Candlestick Distribution** | P25-P75 body + Min-Max whiskers + Current marker | Sector overview comparison |
| **A2: Line with Statistical Bands** | Time series + ±1σ/±2σ bands + Mean/Median lines | Individual sector/index analysis |
| **A3: Histogram Distribution** | Frequency distribution + Mean ±1σ, ±2σ markers | Value distribution shape |

**Data Sources:**
- `SectorService.get_sector_history()` → Line charts
- `SectorService.get_sector_valuation()` → Candlestick distribution
- PE/PB/EV_EBITDA từ `DATA/processed/valuation/`

---

### 1.2 Type B: TTM + Forward (BSC Forecast)

**Use Case:** Individual stock analysis with BSC forecast PE/PB 2025-2026

**Chart Sub-types:**

| Sub-type | Description | Use Case |
|----------|-------------|----------|
| **B1: Box with Dual Markers** | P25-P75 box + ● TTM marker + ◆ Forward marker | Stock vs sector comparison |
| **B2: Forward Valuation Matrix** | TTM vs FWD side-by-side with premium/discount | BSC forecast dashboard |

**Data Sources:**
- BSC Forecast: `DATA/processed/forecast/bsc/bsc_forecast_latest.parquet`
- Columns: `pe_fwd_2025`, `pe_fwd_2026`, `pb_fwd_2025`, `target_price`

---

## 2. PAGE CONSOLIDATION STRATEGY

### 2.1 Current State

| Page | Lines | Key Functions | Overlap |
|------|-------|---------------|---------|
| `sector_dashboard.py` | 1,370 | Sector candlestick, line+bands, macro, commodity | High |
| `valuation_dashboard.py` | 1,032 | Individual stock valuation, sector comparison | High |
| `forecast_dashboard.py` | 1,393 | BSC forecast, forward PE, target price | Medium |

### 2.2 Proposed Merge Structure

```
pages/
├── sector/
│   └── sector_dashboard.py  ← MERGE: Sector + Valuation (TTM only)
│       ├── Tab 1: Sector Distribution (candlestick all sectors)
│       ├── Tab 2: Individual Sector Analysis (line + bands + histogram)
│       ├── Tab 3: VNIndex Analysis (3 types: VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX)
│       ├── Tab 4: Sector Data Tables
│       └── Tab 5: Macro & Commodity
│
├── forecast/
│   └── forecast_dashboard.py  ← ISOLATE: All forward-looking charts
│       ├── Tab 1: BSC Forecast Summary
│       ├── Tab 2: Forward Valuation Matrix (TTM vs FWD)
│       ├── Tab 3: Individual Stock with Forward Markers
│       └── Tab 4: Target Price Analysis
│
└── valuation/
    └── valuation_dashboard.py  ← DEPRECATE or REDIRECT to sector_dashboard.py
```

---

## 3. DETAILED CHART SPECIFICATIONS

### 3.1 Candlestick Distribution Chart (Type A1)

**For:** Sector comparison, VNIndex variants

```python
distribution_candlestick(
    data: List[Dict],           # [{symbol, p5/min, p25, p50, p75, p95/max, current, percentile}]
    metric_label: str,          # "PE" | "PB" | "EV/EBITDA" | "PS"
    height: int = 500,          # Fixed chart height
    y_range: Tuple = None,      # Auto-scale or fixed
    title: str = None
) -> go.Figure
```

**Outlier Handling:**
```python
# Auto y_range by metric
Y_RANGE_DEFAULTS = {
    'PE': (0, 50),      # Max 50x to avoid outliers
    'PB': (0, 8),       # Max 8x for most sectors
    'PS': (0, 10),      # Max 10x
    'EV_EBITDA': (0, 25)  # Max 25x
}
```

---

### 3.2 Line with Statistical Bands (Type A2)

**For:** Individual sector, VNIndex time series

```python
line_with_statistical_bands(
    df: pd.DataFrame,
    date_col: str = 'date',
    value_col: str = 'pe_ttm',
    metric_label: str = "PE",
    height: int = 400,
    show_2sd: bool = True,
    days_limit: int = None
) -> Tuple[go.Figure, Dict]  # (figure, stats_dict)
```

**Stats Dict:**
```python
{
    'current': float,
    'median': float,
    'mean': float,
    'std': float,
    'z_score': float,
    'percentile': float,
    'plus_1sd': float,
    'minus_1sd': float,
    'plus_2sd': float,
    'minus_2sd': float
}
```

---

### 3.3 Histogram Distribution (Type A3) - NEW

**For:** Value distribution shape visualization

```python
def histogram_with_stats(
    data: pd.Series,
    metric_label: str = "PE",
    height: int = 300,
    bins: int = 30,
    show_mean_std: bool = True,
    current_value: float = None
) -> go.Figure:
    """
    Histogram with mean ±1σ, ±2σ vertical lines.

    Visual:
        - Bars: Value frequency distribution
        - Dashed lines: Mean, ±1σ, ±2σ
        - Triangle marker: Current value (if provided)
    """
    pass
```

---

### 3.4 Box with Dual Markers (Type B1) - Existing

**For:** Stock analysis with BSC forecast

```python
valuation_box_with_markers(
    stats_data: List[Dict],
    pe_forward_data: Dict = None,  # {symbol: pe_fwd_2025}
    metric_label: str = "PE",
    title: str = "PE Distribution: Trailing vs Forward",
    height: int = 500
) -> go.Figure
```

---

### 3.5 Forward Valuation Matrix Table (Type B2) - NEW

**For:** Side-by-side TTM vs Forward comparison

```python
def forward_valuation_matrix(
    df: pd.DataFrame,
    metrics: List[str] = ['pe', 'pb'],
    forward_years: List[str] = ['2025', '2026']
) -> pd.DataFrame:
    """
    Create matrix table:
    | Symbol | PE TTM | PE 2025F | PE 2026F | Δ 2025 | Δ 2026 | Status |
    |--------|--------|----------|----------|--------|--------|--------|
    | ACB    | 10.5x  | 8.2x     | 7.5x     | -22%   | -29%   | Cheap  |
    """
    pass
```

---

## 4. VNINDEX SECTION SPECIFICATION

### 4.1 Three VNIndex Variants

| Index | Description | Calculation |
|-------|-------------|-------------|
| **VNINDEX** | Full market PE/PB | Tất cả cổ phiếu VNIndex |
| **VNINDEX_EXCLUDE** | Exclude outliers (VIC, VHM, VPB...) | Loại trừ PE > 100 hoặc loss-making |
| **BSC_INDEX** | BSC universe | Chỉ cổ phiếu trong BSC coverage |

### 4.2 VNIndex Tab Content

```
VNIndex Analysis Tab
├── Row 1: 3 Metric Cards (VNINDEX PE, VNINDEX_EXCLUDE PE, BSC_INDEX PE)
│
├── Row 2: Candlestick Distribution (3 indices side-by-side)
│
├── Row 3: Individual Index Analysis
│   ├── Selectbox: Choose index (VNINDEX | VNINDEX_EXCLUDE | BSC_INDEX)
│   ├── Left: Line with Statistical Bands (mean ±1σ, ±2σ)
│   └── Right: Histogram Distribution
│
└── Row 4: Comparison Table
    | Index | Current | Median | Mean | Z-Score | Percentile | Status |
```

---

## 5. SECTOR SECTION SPECIFICATION

### 5.1 Sector Tab Content

```
Sector Distribution Tab
├── Row 1: Radio (PE TTM | PB | PS | EV/EBITDA)
│
├── Row 2: Candlestick Chart (all 19 sectors)
│   - Sorted by current value
│   - Y-axis auto-scaled per metric
│   - Color-coded by percentile status
│
└── Row 3: Legend + Export Button

Individual Sector Tab
├── Sidebar: Sector Selectbox (19 options)
│
├── Row 1: 4 Metric Cards (Current, Median, Z-Score, Percentile)
│
├── Row 2:
│   ├── Left (70%): Line with Statistical Bands
│   └── Right (30%): Histogram Distribution
│
├── Row 3: Table (individual stocks in sector)
│   | Symbol | PE TTM | PB | Percentile | Status |
│
└── Row 4: Excel Export
```

---

## 6. COMPONENT EXTRACTION PLAN

### 6.1 New Files to Create

```
WEBAPP/
├── core/
│   └── valuation_config.py      ✅ EXISTS - Extend
│
├── components/
│   └── charts/
│       ├── valuation_charts.py  ✅ EXISTS - Add histogram_with_stats
│       ├── table_builders.py    NEW - Styled tables for valuation
│       └── __init__.py          UPDATE exports
│
└── components/
    └── filters/
        └── valuation_filters.py  NEW - Sidebar filter components
```

### 6.2 `table_builders.py` Specification

```python
"""
Table Builders for Valuation Dashboards
=======================================
Unified table components with consistent styling.
"""

def sector_comparison_table(
    data: List[Dict],
    metric: str = "PE",
    columns: List[str] = ['sector', 'current', 'median', 'z_score', 'percentile', 'status']
) -> str:
    """Return HTML table with styled rows."""
    pass

def stock_valuation_table(
    df: pd.DataFrame,
    columns: List[str] = ['symbol', 'pe_ttm', 'pb', 'percentile', 'status'],
    format_rules: Dict = None
) -> str:
    """Return HTML table for stock list."""
    pass

def forward_matrix_table(
    df: pd.DataFrame,
    metrics: List[str] = ['pe', 'pb']
) -> str:
    """TTM vs Forward comparison table."""
    pass
```

### 6.3 `valuation_filters.py` Specification

```python
"""
Sidebar Filter Components
=========================
Reusable filters for valuation pages.
"""

def metric_selector(key: str = "metric") -> str:
    """Metric selectbox: PE TTM | PB | PS | EV/EBITDA"""
    options = ["PE TTM", "PB", "P/S Ratio", "EV/EBITDA"]
    return st.sidebar.selectbox("Valuation Metric", options, key=key)

def time_range_selector(key: str = "time_range") -> int:
    """Time range: 3M | 6M | 1Y | 3Y | ALL"""
    options = {"3M": 63, "6M": 126, "1Y": 252, "3Y": 756, "ALL": 2000}
    selected = st.sidebar.selectbox("Time Range", list(options.keys()), index=3, key=key)
    return options[selected]

def sector_selector(sectors: List[str], key: str = "sector") -> str:
    """Sector selectbox with all available sectors."""
    return st.sidebar.selectbox("Select Sector", sectors, key=key)

def ticker_search(key: str = "ticker_search") -> str:
    """Ticker search input with autocomplete hint."""
    return st.sidebar.text_input("🔍 Search Ticker", placeholder="VCB, ACB...", key=key)
```

---

## 7. CHART CONFIG STANDARDIZATION

### 7.1 Chart Size Standards

| Chart Type | Height | Use Case |
|------------|--------|----------|
| Candlestick Distribution | 500px | Main comparison chart |
| Line with Bands | 400px | Individual analysis |
| Histogram | 300px | Distribution shape |
| Dual-Axis | 450px | Combined metrics |
| Mini Chart | 200px | Metric card sparkline |

### 7.2 Marker Size Standards

| Marker Type | Size | Use Case |
|-------------|------|----------|
| Current (TTM) | 10 | ● Circle marker |
| Forward | 10 | ◆ Diamond marker |
| Small | 8 | Dense charts |
| Large | 12 | Emphasis |
| Border Width | 1.5 | All markers |

### 7.3 Color Standards (from `valuation_config.py`)

| Status | Color | Percentile Range |
|--------|-------|------------------|
| Very Cheap | `#00D4AA` | P0-10 |
| Cheap | `#7FFFD4` | P10-25 |
| Fair | `#FFD666` | P25-75 |
| Expensive | `#FF9F43` | P75-90 |
| Very Expensive | `#FF6B6B` | P90-100 |

---

## 8. OUTLIER HANDLING RULES (Centralized)

### 8.1 `OUTLIER_LIMITS` in `valuation_config.py`

```python
OUTLIER_LIMITS = {
    'PE': {'min': 0, 'max': 100, 'multiplier': 5},
    'PB': {'min': 0, 'max': 20, 'multiplier': 4},
    'PS': {'min': 0, 'max': 30, 'multiplier': 4},
    'EV_EBITDA': {'min': 0, 'max': 50, 'multiplier': 4}
}
```

### 8.2 Y-Axis Display Range (Tighter for Readability)

```python
Y_AXIS_DISPLAY_RANGE = {
    'PE': (0, 50),       # Show 0-50x even if max=100
    'PB': (0, 8),        # Show 0-8x even if max=20
    'PS': (0, 10),       # Show 0-10x
    'EV_EBITDA': (0, 25) # Show 0-25x
}
```

### 8.3 Apply to All Charts

```python
# In distribution_candlestick()
if y_range is None:
    display_range = Y_AXIS_DISPLAY_RANGE.get(metric_label.upper())
    if display_range:
        layout['yaxis']['range'] = list(display_range)
```

---

## 9. FILTER UI/UX OPTIMIZATION

### 9.1 Current Problems

1. **Duplicate Filters:** Metric selectbox in both sidebar AND page content
2. **Inconsistent Placement:** Some pages use sidebar, some use inline
3. **No Unified Search:** Ticker search not available on all pages

### 9.2 Proposed Solution

**Sidebar (Global Filters):**
```
┌─────────────────────┐
│ 🔍 Search Ticker    │  ← Universal search
├─────────────────────┤
│ Valuation Metric    │  ← PE | PB | PS | EV/EBITDA
│ [PE TTM         ▼]  │
├─────────────────────┤
│ Time Range          │  ← 3M | 6M | 1Y | 3Y | ALL
│ [3Y             ▼]  │
├─────────────────────┤
│ 🔄 Refresh Data     │
└─────────────────────┘
```

**Page Content (Context Filters):**
```
┌─────────────────────────────────────┐
│ [📊 Sectors] [📈 Indices]           │  ← Tab/Radio for context
│                                     │
│ [Select Sector ▼] (only in tab)     │  ← Context-specific
└─────────────────────────────────────┘
```

---

## 10. NUMBER FORMATTING STANDARDS

### 10.1 Formatter Functions (from `valuation_config.py`)

| Function | Example Output | Use Case |
|----------|----------------|----------|
| `format_ratio(15.234)` | `15.23x` | PE, PB, EV/EBITDA |
| `format_percent(75.5)` | `76%` | Percentile |
| `format_zscore(1.52)` | `+1.52σ` | Z-score |
| `format_change(12.5)` | `+12.5%` | Delta, Growth |

### 10.2 Table Column Formatting

```python
TABLE_FORMAT_RULES = {
    'pe_ttm': lambda x: format_ratio(x, 1),      # 15.2x
    'pb': lambda x: format_ratio(x, 2),          # 3.45x
    'percentile': lambda x: format_percent(x),    # 75%
    'z_score': lambda x: format_zscore(x),        # +1.52σ
    'change': lambda x: format_change(x)          # +12.5%
}
```

---

## 11. IMPLEMENTATION PHASES

### Phase 1: Chart Schema & Core Components (Day 1-2)

- [ ] **CREATE** `WEBAPP/core/chart_schema.py` with complete schema definition
- [ ] **UPDATE** `WEBAPP/core/valuation_config.py` to import from chart_schema
- [ ] Add `histogram_with_stats()` to `valuation_charts.py`
- [ ] Create `table_builders.py` with styled tables
- [ ] Create `valuation_filters.py` with reusable filters

### Phase 2: Sector Dashboard Refactor (Day 2-3)

- [ ] Merge valuation functions into `sector_dashboard.py`
- [ ] Add VNIndex tab with 3 variants (VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX)
- [ ] Add Histogram chart to Individual Sector tab
- [ ] Refactor all charts to use `get_chart_config()` from chart_schema

### Phase 3: Forecast Dashboard Isolation (Day 3-4)

- [ ] Move all forward-looking charts to `forecast_dashboard.py`
- [ ] Add Forward Valuation Matrix table (TTM vs 2025F vs 2026F)
- [ ] Update `valuation_box_with_markers()` for 2025 + 2026 forward
- [ ] Load BSC data from `DATA/processed/forecast/bsc/`

### Phase 4: Deprecate Old Pages (Day 4)

- [ ] Add redirect from `valuation_dashboard.py` to `sector_dashboard.py`
- [ ] Remove duplicate code
- [ ] Update `main_app.py` navigation

### Phase 5: Testing & Polish (Day 5)

- [ ] Test all pages with edge cases
- [ ] Verify color consistency via chart_schema
- [ ] Verify Y-axis scaling (no outlier distortion)
- [ ] Performance testing (cache validation)

---

## 12. SUCCESS CRITERIA

| Criterion | Metric |
|-----------|--------|
| **DRY** | 0 duplicate chart functions across pages |
| **Color Consistency** | 100% charts use `valuation_config.py` colors |
| **Outlier Handling** | All charts apply `OUTLIER_LIMITS` + `Y_AXIS_DISPLAY_RANGE` |
| **Formatting** | All tables use `format_*()` functions |
| **UI/UX** | Sidebar filters unified, no duplicate controls |
| **Chart Scale** | All charts have fixed height per type |

---

## 13. CONFIRMED DATA SOURCES

### 13.1 Market Indices (✅ Available)

**Path:** `DATA/processed/market_indices/`

| File | Shape | Columns | Scopes |
|------|-------|---------|--------|
| `vnindex_valuation.parquet` | 5,784 × 6 | date, pe_ttm, pb, scope, pe_fwd_2025, pe_fwd_2026 | VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX |
| `sector_pe_summary.parquet` | 36,441 × 6 | date, pe_ttm, pb, scope, pe_fwd_2025, pe_fwd_2026 | 19 sectors |

### 13.2 BSC Forecast (✅ Available)

**Path:** `DATA/processed/forecast/bsc/`

| File | Shape | Key Columns |
|------|-------|-------------|
| `bsc_combined.parquet` | 93 × 32 | symbol, pe_fwd_2025, pe_fwd_2026, pb_fwd_2025, pb_fwd_2026, target_price, rating |
| `bsc_sector_valuation.parquet` | 15 × 21 | sector, pe_fwd_2025, pe_fwd_2026, pb_fwd_2025, pb_fwd_2026 |

---

## 14. RESOLVED QUESTIONS

| Question | Answer |
|----------|--------|
| VNIndex Data | ✅ Available: VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX |
| Histogram Bins | **35 bins** (confirmed) |
| Forward Years | ✅ Both 2025 + 2026 available |
| Mobile Priority | **Not prioritized** - Focus on Streamlit web |

---

## 15. CHART CONFIG SCHEMA (UI/UX Blueprint)

### 15.1 Schema Location

**Create file:** `WEBAPP/core/chart_schema.py`

### 15.2 Complete Schema Definition

```python
"""
Chart Configuration Schema
==========================
Single source of truth for all chart configurations.
Edit this file to adjust UI/UX globally.

Usage:
    from WEBAPP.core.chart_schema import CHART_SCHEMA, get_chart_config
    config = get_chart_config('candlestick_distribution')
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================
class ChartType(Enum):
    CANDLESTICK_DISTRIBUTION = "candlestick_distribution"
    LINE_WITH_BANDS = "line_with_bands"
    HISTOGRAM = "histogram"
    BOX_WITH_MARKERS = "box_with_markers"
    DUAL_AXIS = "dual_axis"
    SPARKLINE = "sparkline"


class MetricType(Enum):
    PE = "PE"
    PB = "PB"
    PS = "PS"
    EV_EBITDA = "EV_EBITDA"


# =============================================================================
# LAYOUT CONFIG
# =============================================================================
@dataclass
class LayoutConfig:
    """Chart layout settings."""
    height: int = 400
    margin_left: int = 50
    margin_right: int = 30
    margin_top: int = 50
    margin_bottom: int = 50
    padding: int = 4
    autosize: bool = True


# =============================================================================
# AXIS CONFIG
# =============================================================================
@dataclass
class AxisConfig:
    """Axis configuration."""
    grid_color: str = "rgba(255, 255, 255, 0.05)"
    zero_line_color: str = "rgba(255, 255, 255, 0.1)"
    line_color: str = "rgba(255, 255, 255, 0.08)"
    tick_font_size: int = 10
    tick_font_color: str = "#64748B"
    title_font_size: int = 12
    title_font_color: str = "#94A3B8"
    tick_angle: int = 0
    show_grid: bool = True
    fixed_range: bool = False


# =============================================================================
# MARKER CONFIG
# =============================================================================
@dataclass
class MarkerConfig:
    """Marker settings for scatter plots."""
    size_trailing: int = 10        # ● Circle for current/TTM
    size_forward: int = 10         # ◆ Diamond for forward
    size_small: int = 8            # Dense charts
    size_large: int = 12           # Emphasis
    border_width: float = 1.5      # Marker border
    border_color: str = "white"


# =============================================================================
# COLOR PALETTES
# =============================================================================
@dataclass
class StatusColors:
    """Valuation status colors based on percentile."""
    very_cheap: str = "#00D4AA"      # P0-10
    cheap: str = "#7FFFD4"           # P10-25
    fair: str = "#FFD666"            # P25-75
    expensive: str = "#FF9F43"       # P75-90
    very_expensive: str = "#FF6B6B"  # P90-100


@dataclass
class ChartColors:
    """Chart element colors."""
    # Candlestick
    body: str = "#A0AEC0"
    body_fill: str = "rgba(160, 174, 192, 0.3)"
    whisker: str = "#718096"

    # Lines
    main_line: str = "#00D4AA"       # Teal
    mean_line: str = "#4A7BC8"       # Blue
    median_line: str = "#FFD666"     # Gold

    # Statistical bands
    band_1sd: str = "rgba(0, 212, 170, 0.15)"
    band_2sd: str = "rgba(74, 123, 200, 0.1)"
    sd_line: str = "rgba(74, 123, 200, 0.6)"

    # Forward markers
    forward_marker: str = "#F59E0B"  # Amber


# =============================================================================
# Y-AXIS RANGE BY METRIC
# =============================================================================
Y_AXIS_DISPLAY_RANGE: Dict[str, Tuple[float, float]] = {
    'PE': (0, 50),
    'PB': (0, 8),
    'PS': (0, 10),
    'EV_EBITDA': (0, 25)
}

OUTLIER_LIMITS: Dict[str, Dict[str, float]] = {
    'PE': {'min': 0, 'max': 100, 'multiplier': 5},
    'PB': {'min': 0, 'max': 20, 'multiplier': 4},
    'PS': {'min': 0, 'max': 30, 'multiplier': 4},
    'EV_EBITDA': {'min': 0, 'max': 50, 'multiplier': 4}
}


# =============================================================================
# PERCENTILE THRESHOLDS
# =============================================================================
PERCENTILE_THRESHOLDS: Dict[str, Tuple[float, float]] = {
    'very_cheap': (0, 10),
    'cheap': (10, 25),
    'fair': (25, 75),
    'expensive': (75, 90),
    'very_expensive': (90, 100)
}


# =============================================================================
# CHART TYPE CONFIGS
# =============================================================================
@dataclass
class CandlestickDistributionConfig:
    """Type A1: Distribution candlestick chart."""
    chart_type: str = "candlestick_distribution"
    height: int = 500
    x_tick_angle: int = -45
    x_tick_font_size: int = 10
    show_range_slider: bool = False
    show_legend: bool = True
    drag_mode: str = "pan"  # or "zoom", "select"
    fixed_range: bool = True  # Disable zoom for simplicity


@dataclass
class LineWithBandsConfig:
    """Type A2: Line chart with statistical bands."""
    chart_type: str = "line_with_bands"
    height: int = 400
    line_width: float = 2.5
    mean_line_dash: str = "dash"
    median_line_dash: str = "solid"
    sd_line_dash: str = "dot"
    sd_line_width: float = 1.0
    show_2sd: bool = True
    x_tick_format: str = "%b %Y"
    x_padding_percent: float = 0.02  # 2% padding on right


@dataclass
class HistogramConfig:
    """Type A3: Histogram distribution chart."""
    chart_type: str = "histogram"
    height: int = 300
    bins: int = 35
    bar_color: str = "#8B5CF6"       # Purple
    bar_opacity: float = 0.7
    mean_line_color: str = "#F59E0B"  # Amber
    sd_line_color: str = "#4A7BC8"    # Blue
    show_mean_std: bool = True
    show_current_marker: bool = True
    current_marker_color: str = "#00D4AA"


@dataclass
class BoxWithMarkersConfig:
    """Type B1: Box with trailing/forward markers."""
    chart_type: str = "box_with_markers"
    height: int = 500
    bar_width: float = 0.6
    bar_opacity: float = 0.6
    whisker_thickness: float = 1.5
    whisker_width: int = 4
    trailing_symbol: str = "circle"
    forward_symbol: str = "diamond"
    show_sector_median_line: bool = True


@dataclass
class DualAxisConfig:
    """Dual axis chart (e.g., PE + PB)."""
    chart_type: str = "dual_axis"
    height: int = 450
    primary_line_color: str = "#00D4AA"
    secondary_line_color: str = "#F59E0B"
    primary_line_width: float = 2.5
    secondary_line_width: float = 2.0


@dataclass
class SparklineConfig:
    """Mini chart for metric cards."""
    chart_type: str = "sparkline"
    height: int = 80
    line_width: float = 1.5
    fill_opacity: float = 0.2
    show_axis: bool = False
    show_grid: bool = False


# =============================================================================
# TYPOGRAPHY
# =============================================================================
@dataclass
class TypographyConfig:
    """Font settings for charts."""
    font_family_display: str = "Space Grotesk, sans-serif"
    font_family_body: str = "DM Sans, sans-serif"
    font_family_mono: str = "JetBrains Mono, monospace"
    title_size: int = 16
    title_color: str = "#E8E8E8"
    axis_title_size: int = 12
    tick_size: int = 10
    legend_size: int = 11
    annotation_size: int = 10


# =============================================================================
# HOVER/TOOLTIP CONFIG
# =============================================================================
@dataclass
class HoverConfig:
    """Hover/tooltip settings."""
    bgcolor: str = "#1A1625"
    border_color: str = "#8B5CF6"
    font_color: str = "#F8FAFC"
    font_size: int = 12


# =============================================================================
# MASTER CHART SCHEMA
# =============================================================================
CHART_SCHEMA = {
    # Global configs
    'layout': LayoutConfig(),
    'axis': AxisConfig(),
    'marker': MarkerConfig(),
    'status_colors': StatusColors(),
    'chart_colors': ChartColors(),
    'typography': TypographyConfig(),
    'hover': HoverConfig(),

    # Y-axis ranges by metric
    'y_axis_display_range': Y_AXIS_DISPLAY_RANGE,
    'outlier_limits': OUTLIER_LIMITS,
    'percentile_thresholds': PERCENTILE_THRESHOLDS,

    # Chart-specific configs
    'candlestick_distribution': CandlestickDistributionConfig(),
    'line_with_bands': LineWithBandsConfig(),
    'histogram': HistogramConfig(),
    'box_with_markers': BoxWithMarkersConfig(),
    'dual_axis': DualAxisConfig(),
    'sparkline': SparklineConfig(),
}


# =============================================================================
# ACCESSOR FUNCTIONS
# =============================================================================
def get_chart_config(chart_type: str) -> Any:
    """Get config for specific chart type."""
    return CHART_SCHEMA.get(chart_type)


def get_y_range(metric: str) -> Tuple[float, float]:
    """Get display y-range for metric."""
    return Y_AXIS_DISPLAY_RANGE.get(metric.upper(), (0, 100))


def get_outlier_limits(metric: str) -> Dict[str, float]:
    """Get outlier limits for metric."""
    return OUTLIER_LIMITS.get(metric.upper(), {'min': 0, 'max': 100})


def get_status_color(percentile: float) -> str:
    """Get color based on percentile."""
    colors = StatusColors()
    if percentile < 10:
        return colors.very_cheap
    elif percentile < 25:
        return colors.cheap
    elif percentile < 75:
        return colors.fair
    elif percentile < 90:
        return colors.expensive
    else:
        return colors.very_expensive
```

### 15.3 Usage Example

```python
# In valuation_charts.py
from WEBAPP.core.chart_schema import (
    CHART_SCHEMA,
    get_chart_config,
    get_y_range,
    get_status_color
)

def distribution_candlestick(data, metric_label="PE", **kwargs):
    config = get_chart_config('candlestick_distribution')
    colors = CHART_SCHEMA['chart_colors']

    # Use config values
    height = kwargs.get('height', config.height)
    y_range = kwargs.get('y_range', get_y_range(metric_label))

    fig = go.Figure()
    # ... chart logic using config values ...

    fig.update_layout(
        height=height,
        yaxis=dict(range=list(y_range)),
        xaxis=dict(tickangle=config.x_tick_angle)
    )
    return fig
```

### 15.4 Quick Reference Table

| Config Class | Key Settings | Adjustable Via |
|--------------|--------------|----------------|
| `LayoutConfig` | height, margins, padding | `CHART_SCHEMA['layout']` |
| `AxisConfig` | grid_color, tick_size, tick_angle | `CHART_SCHEMA['axis']` |
| `MarkerConfig` | size_trailing=10, size_forward=10 | `CHART_SCHEMA['marker']` |
| `StatusColors` | very_cheap=#00D4AA, fair=#FFD666 | `CHART_SCHEMA['status_colors']` |
| `ChartColors` | main_line, mean_line, band colors | `CHART_SCHEMA['chart_colors']` |
| `CandlestickDistributionConfig` | height=500, x_tick_angle=-45 | `get_chart_config('candlestick_distribution')` |
| `LineWithBandsConfig` | height=400, line_width=2.5 | `get_chart_config('line_with_bands')` |
| `HistogramConfig` | height=300, bins=35 | `get_chart_config('histogram')` |

---

## 16. REFERENCES

- **Parent Plan:** `plans/2025-12-21-valuation-chart-standardization/PLAN.md`
- **Brainstorm Report:** `plans/reports/brainstorm-2025-12-21-streamlit-pages-optimization.md`
- **Existing Config:** `WEBAPP/core/valuation_config.py`
- **Existing Charts:** `WEBAPP/components/charts/valuation_charts.py`

---

*Document created: 2025-12-21*
*Status: Ready for User Review*
