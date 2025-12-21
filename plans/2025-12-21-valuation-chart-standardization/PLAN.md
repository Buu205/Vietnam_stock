# Plan: Valuation Chart Standardization & Component Extraction

**Date:** 2025-12-21
**Status:** Ready for Implementation
**Estimated Effort:** 5 days

---

## Parallel Execution Strategy

### Dependency Graph

```
Phase 1 (Foundation)
    │
    ├──────────────────┐
    ▼                  ▼
Phase 2 (Sector)   Phase 3 (Forecast)  ← PARALLEL
    │                  │
    └──────────────────┘
           │
           ▼
     Phase 4 (Cleanup)
```

### Execution Order

| Step | Phases | Mode | Dependencies |
|------|--------|------|--------------|
| 1 | Phase 1 | Sequential | None |
| 2 | Phase 2 + Phase 3 | **PARALLEL** | Phase 1 |
| 3 | Phase 4 | Sequential | Phase 2 + 3 |

### File Ownership Matrix

| Phase | Files Owned (EXCLUSIVE) |
|-------|-------------------------|
| **Phase 1** | `chart_schema.py`, `valuation_config.py`, `valuation_charts.py`, `table_builders.py`, `valuation_filters.py` |
| **Phase 2** | `sector_dashboard.py`, `sector_service.py` |
| **Phase 3** | `forecast_dashboard.py`, `forecast_service.py` |
| **Phase 4** | `valuation_dashboard.py`, `main_app.py` |

### Phase Files

| Phase | File | Status |
|-------|------|--------|
| 01 | [phase-01-chart-schema-core-components.md](phase-01-chart-schema-core-components.md) | ✅ Created |
| 02 | [phase-02-sector-dashboard-refactor.md](phase-02-sector-dashboard-refactor.md) | ✅ Created |
| 03 | [phase-03-forecast-dashboard-isolation.md](phase-03-forecast-dashboard-isolation.md) | ✅ Created |
| 04 | [phase-04-deprecate-old-pages.md](phase-04-deprecate-old-pages.md) | ✅ Created |

---

## Executive Summary

Standardize valuation candlestick charts across the dashboard, fix outlier handling, extract reusable components, and consolidate duplicate pages.

---

## Problem Analysis

### 1. Duplicate Code Patterns Identified

| Pattern | sector_dashboard.py | valuation_dashboard.py | Est. Lines |
|---------|---------------------|------------------------|------------|
| Candlestick chart with current marker | Lines 245-285 | Lines 174-220 | ~80 each |
| Statistical bands (±1σ, ±2σ) | Lines 595-693 | Similar pattern | ~100 each |
| Outlier filtering (PE<=100, PB<=100) | Lines 213-216, 378-383 | Not centralized | ~20 each |
| Status color mapping | Lines 264-269 | Lines 196-203 | ~10 each |
| Excel export button | Lines 335-344, 492-501 | Similar | ~15 each |
| HTML table styling | Lines 291-499 (inline CSS) | Lines 291-499 | ~200 each |
| **Total Duplicate** | | | **~425 lines** |

### 2. Chart Type Requirements

**Type A: Historical Distribution (No Forward Data)**
- Use case: Sector comparison, VNIndex analysis
- Components: P25-P75 box, P5-P95 whiskers (or min-max), current marker (circle)
- Color: Current position → Undervalued (green) / Fair (yellow) / Expensive (red)

**Type B: Historical + Forward (BSC Forecast)**
- Use case: Individual stock analysis with BSC forecasts
- Components: Same as Type A + Diamond marker for Forward PE
- Already implemented: `valuation_box_with_markers()` in plotly_builders.py

### 3. Outlier Issues

Current problems:
- PE > 100 distorts charts (some stocks have PE 200+)
- PB > 20 distorts charts
- Different pages apply filters inconsistently
- Current value sometimes exceeds filtered range → dot outside chart

### 4. UI/UX Issues

- Diamond and circle markers too large (size=12-14 → should be 8-10)
- Empty space on charts (x-axis padding too aggressive)
- Scale inconsistency between pages (some fixed, some auto-scale)
- No unified legend explaining markers

### 5. Color Fragmentation (NEW)

**Current state:** Colors defined in 4+ places, inconsistent usage

| File | Constants | Used By |
|------|-----------|---------|
| `core/styles.py` | CHART_COLORS, BAR_COLORS, DISTRIBUTION_COLORS, ASSESSMENT_COLORS, BAND_COLORS | sector, valuation pages |
| `core/theme.py` | TRADING_COLORS, SEMANTIC COLORS | theme system |
| `core/constants.py` | COLORS | legacy charts |
| `core/chart_config.py` | ChartConfig.COLORS, ChartConfig.BAND_COLORS | chart_config |

**Problems:**
- Same color defined with different names (`#00D4AA` = "undervalued" in styles.py, "positive" elsewhere)
- Pages import from different sources
- No single source of truth

### 6. Outlier Rules Fragmentation (NEW)

**`ValuationService.OUTLIER_RULES` exists but not used consistently:**

| Location | Rule Applied | Issue |
|----------|--------------|-------|
| `valuation_service.py:47` | PE max=100, PB max=20, multiplier limits | ✅ Defined correctly |
| `sector_dashboard.py:214` | `pe <= 100` hardcoded | ❌ Not using service |
| `sector_dashboard.py:378-383` | `pe <= 100, pb <= 100` | ❌ PB limit wrong (should be 20) |
| `plotly_builders.py` | No filtering | ❌ Relies on caller |

### 7. Number Formatting Inconsistency (NEW)

| Format | Occurrences | Examples |
|--------|-------------|----------|
| `f'{x:.2f}x'` | ~15 | PE ratio display |
| `f'{x:.1f}x'` | ~8 | Some metrics |
| `f'{x:.0f}%'` | ~10 | Percentile |
| `f'{x:+.2f}σ'` | ~3 | Z-score |
| No standard formatter | - | Each page formats differently |

---

## Solution Architecture

### Phase 1: Core Component Extraction (Day 1-2)

Create unified chart builders in `WEBAPP/components/charts/`:

```
components/charts/
├── plotly_builders.py          # ✅ Already exists
├── valuation_charts.py         # NEW - Valuation-specific charts
├── statistical_bands.py        # NEW - Reusable band overlays
└── __init__.py                 # Export all builders
```

#### 1.1 New File: `valuation_charts.py`

```python
"""
Unified Valuation Chart Components
==================================
Type A: distribution_candlestick() - Historical only
Type B: valuation_box_with_markers() - Historical + Forward (use existing)
"""

# Constants
OUTLIER_LIMITS = {
    'PE': {'min': 0, 'max': 100},
    'PB': {'min': 0, 'max': 20},
    'PS': {'min': 0, 'max': 50},
    'EV_EBITDA': {'min': 0, 'max': 50}
}

MARKER_SIZES = {
    'current': 10,      # Circle for current/trailing
    'forward': 10,      # Diamond for forward
    'border_width': 1.5
}

STATUS_COLORS = {
    'very_cheap': '#00D4AA',
    'cheap': '#7FFFD4',
    'fair': '#FFD666',
    'expensive': '#FF9F43',
    'very_expensive': '#FF6B6B'
}

def filter_outliers(series: pd.Series, metric: str) -> pd.Series:
    """Apply consistent outlier filtering based on metric type."""
    limits = OUTLIER_LIMITS.get(metric.upper(), {'min': 0, 'max': 100})
    return series[(series >= limits['min']) & (series <= limits['max'])]

def get_status_color(percentile: float) -> str:
    """Get color based on percentile position."""
    if percentile < 10:
        return STATUS_COLORS['very_cheap']
    elif percentile < 25:
        return STATUS_COLORS['cheap']
    elif percentile < 75:
        return STATUS_COLORS['fair']
    elif percentile < 90:
        return STATUS_COLORS['expensive']
    else:
        return STATUS_COLORS['very_expensive']

def distribution_candlestick(
    data: list[dict],
    metric_label: str = "PE",
    height: int = 500,
    y_range: tuple = None,
    show_legend: bool = True
) -> go.Figure:
    """
    Type A: Distribution candlestick chart (historical only).

    Args:
        data: List of dicts with keys:
            - symbol: str
            - p5, p25, p50, p75, p95: float (or min/max)
            - current: float
            - percentile: float (0-100)
        metric_label: "PE" | "PB" | etc.
        height: Chart height in pixels
        y_range: Optional (min, max) tuple for y-axis
        show_legend: Show color legend below chart

    Returns:
        Plotly Figure object
    """
    pass  # Implementation in Phase 1

def line_with_bands(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    metric_label: str = "PE",
    height: int = 400,
    show_current_marker: bool = True
) -> tuple[go.Figure, dict]:
    """
    Line chart with ±1σ, ±2σ statistical bands.

    Returns:
        (figure, stats_dict) where stats_dict contains:
        - current, median, mean, z_score, percentile
    """
    pass  # Implementation in Phase 1
```

#### 1.2 Move Existing Function

Move `valuation_box_with_markers()` from `plotly_builders.py` to `valuation_charts.py` and update imports.

### Phase 2: Centralize Colors, Outliers & Formatting (Day 2)

#### 2.1 Create Unified Config File

Create `WEBAPP/core/valuation_config.py`:

```python
"""
Valuation Chart Configuration
=============================
Single source of truth for colors, outliers, formatting, and marker sizes.
"""

# =============================================================================
# OUTLIER LIMITS
# =============================================================================
OUTLIER_LIMITS = {
    'PE': {'min': 0, 'max': 100, 'multiplier': 5},
    'PB': {'min': 0, 'max': 20, 'multiplier': 4},
    'PS': {'min': 0, 'max': 30, 'multiplier': 4},
    'EV_EBITDA': {'min': 0, 'max': 50, 'multiplier': 4}
}

# =============================================================================
# VALUATION STATUS COLORS
# =============================================================================
STATUS_COLORS = {
    'very_cheap': '#00D4AA',    # Bright teal - P0-10
    'cheap': '#7FFFD4',          # Light aqua - P10-25
    'fair': '#FFD666',           # Gold - P25-75
    'expensive': '#FF9F43',      # Orange - P75-90
    'very_expensive': '#FF6B6B'  # Coral red - P90-100
}

# =============================================================================
# CHART COLORS (Candlestick & Bands)
# =============================================================================
CHART_COLORS = {
    # Candlestick
    'body': '#A0AEC0',           # Gray body
    'body_fill': 'rgba(160, 174, 192, 0.3)',
    'whisker': '#718096',

    # Line chart
    'main_line': '#00D4AA',      # Teal
    'mean_line': '#4A7BC8',      # Blue
    'median_line': '#FFD666',    # Gold

    # Statistical bands
    'band_1sd': 'rgba(0, 212, 170, 0.15)',   # Teal transparent
    'band_2sd': 'rgba(74, 123, 200, 0.1)',   # Blue transparent
    'sd_line': 'rgba(74, 123, 200, 0.6)',
}

# =============================================================================
# MARKER SIZES
# =============================================================================
MARKER_SIZES = {
    'trailing': 10,      # Circle for TTM/current
    'forward': 10,       # Diamond for forward
    'border_width': 1.5
}

# =============================================================================
# NUMBER FORMATTERS
# =============================================================================
def format_ratio(value: float, precision: int = 2) -> str:
    """Format PE/PB/EV ratios: 15.23x"""
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.{precision}f}x"

def format_percent(value: float, precision: int = 0) -> str:
    """Format percentile: 75%"""
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.{precision}f}%"

def format_zscore(value: float) -> str:
    """Format z-score: +1.52σ"""
    if value is None or pd.isna(value):
        return "—"
    return f"{value:+.2f}σ"

def format_change(value: float) -> str:
    """Format change percent: +12.5% or -8.3%"""
    if value is None or pd.isna(value):
        return "—"
    return f"{value:+.1f}%"
```

#### 2.2 Update ValuationService

Move `OUTLIER_RULES` → import from `valuation_config.py`:

```python
# Before (valuation_service.py:47)
OUTLIER_RULES = {...}  # DELETE

# After
from WEBAPP.core.valuation_config import OUTLIER_LIMITS
```

#### 2.3 Update All Pages to Use Centralized Config

Replace hardcoded values:

```python
# Before (sector_dashboard.py:214)
clean_data = metric_data[(metric_data > 0) & (metric_data <= 100)]

# After
from WEBAPP.core.valuation_config import OUTLIER_LIMITS
limits = OUTLIER_LIMITS[metric.upper()]
clean_data = metric_data[(metric_data > limits['min']) & (metric_data <= limits['max'])]
```

#### 2.4 Deprecate Old Color Definitions

Add deprecation warnings to old color constants:

```python
# core/styles.py
import warnings

# Keep for backward compatibility, but warn
def _deprecated_colors():
    warnings.warn(
        "CHART_COLORS from styles.py is deprecated. Use valuation_config.CHART_COLORS",
        DeprecationWarning
    )
    return {...}
```

### Phase 3: UI/UX Fixes (Day 2-3)

#### 3.1 Marker Size Standardization

Update all chart functions:
```python
# Before
marker=dict(size=12, ...)

# After
marker=dict(size=MARKER_SIZES['current'], ...)
```

#### 3.2 Chart Scaling

Implement adaptive y-axis scaling:
```python
def calculate_y_range(data: pd.Series, metric: str) -> tuple:
    """Calculate appropriate y-axis range based on data distribution."""
    limits = OUTLIER_LIMITS[metric]
    filtered = filter_outliers(data, metric)

    # Use P5-P95 for auto-scaling, not min-max
    y_min = max(0, filtered.quantile(0.05) * 0.9)
    y_max = min(limits['max'], filtered.quantile(0.95) * 1.1)

    return (y_min, y_max)
```

#### 3.3 Empty Space Fix

Reduce x-axis padding:
```python
# Before
padding_days = max(30, len(plot_df) // 20)

# After
padding_days = max(10, len(plot_df) // 50)  # ~2% padding
```

### Phase 4: Page Consolidation (Day 3-4)

#### 4.1 Option A: Tab Merge (Recommended)

Merge Sector Overview and Valuation into single page with tabs:

```
Sector & Valuation Dashboard
├── Tab 1: Sector Distribution (candlestick all sectors)
├── Tab 2: Individual Sector Analysis (line + bands)
├── Tab 3: Stock Valuation (by industry)
├── Tab 4: Macro & Commodity
└── Tab 5: Data Export
```

#### 4.2 Implementation Steps

1. Create `WEBAPP/pages/sector_valuation/dashboard.py`
2. Import shared components from `valuation_charts.py`
3. Combine sidebar filters (metric, sector, time range)
4. Remove old pages or redirect

### Phase 5: Testing & Cleanup (Day 4)

- Test all chart types with edge cases (empty data, outliers, single point)
- Verify hover tooltips work correctly
- Check mobile responsiveness
- Remove deprecated code from old pages
- Update imports throughout codebase

---

## File Changes Summary

| File | Action | Lines Changed | Description |
|------|--------|---------------|-------------|
| `core/valuation_config.py` | CREATE | +100 | Unified colors, outliers, formatters |
| `components/charts/valuation_charts.py` | CREATE | +350 | Chart components |
| `components/charts/plotly_builders.py` | MODIFY | -260 | Move valuation functions |
| `components/charts/__init__.py` | MODIFY | +10 | Export new components |
| `services/valuation_service.py` | MODIFY | -30 | Remove OUTLIER_RULES, use config |
| `pages/sector/sector_dashboard.py` | MODIFY | -300 | Use components, import config |
| `pages/valuation/valuation_dashboard.py` | MODIFY | -250 | Use components, import config |
| `pages/forecast/forecast_dashboard.py` | MODIFY | +20 | Update imports |
| `core/styles.py` | MODIFY | +10 | Deprecation warnings |
| **Net Change** | | **-350 lines** |

---

## Success Criteria

1. **DRY**: No duplicate chart code across pages
2. **Colors**: Single source of truth in `valuation_config.py` - all pages import from there
3. **Outliers**: PE max=100, PB max=20, PS max=30, EV/EBITDA max=50 - applied consistently
4. **Formatting**: `format_ratio()`, `format_percent()`, `format_zscore()` used everywhere
5. **Usability**: Charts don't distort from outliers, markers visible but not overwhelming
6. **Maintainability**: Fix in one place = fix everywhere

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing pages | High | Test each page after component migration |
| Performance regression | Medium | Verify caching still works with new components |
| Visual differences | Low | Screenshot compare before/after |

---

## Open Questions

None - ready to proceed.

---

## Next Steps

1. [ ] User approves plan
2. [ ] Phase 1: Create `valuation_charts.py`
3. [ ] Phase 2: Centralize outlier handling
4. [ ] Phase 3: UI/UX fixes
5. [ ] Phase 4: Page consolidation
6. [ ] Phase 5: Testing & cleanup
