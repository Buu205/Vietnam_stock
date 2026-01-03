# Phase 4: Technical Filter Consolidation

**Effort:** 2 days
**Dependencies:** Phase 1 (constants)
**Files to modify:** 2

---

## Objectives

1. Extend `ta_filter_bar.py` with scanner-specific options
2. Refactor `stock_scanner.py` to use extended filter bar
3. Remove ~100 lines of duplicate filter code

---

## Task 4.1: Extend TA Filter Bar

**File:** `WEBAPP/pages/technical/components/ta_filter_bar.py` (MODIFY)

### Add new filter options:

```python
# Import constants from centralized location
from WEBAPP.components.filters.constants import (
    TIMEFRAME_OPTIONS,
    SIGNAL_TYPES,
    TREND_OPTIONS,
    DIRECTION_OPTIONS,
)

# Add new parameters to render_ta_filters()

def render_ta_filters(
    service: 'TADashboardService',
    show_timeframe: bool = True,
    show_sector: bool = True,
    show_signal_type: bool = False,
    show_search: bool = False,
    show_refresh: bool = True,
    # NEW: Scanner-specific options
    show_trend: bool = False,
    show_direction: bool = False,
    show_strength_slider: bool = False,
    show_value_slider: bool = False,
    key_prefix: str = "ta"
) -> Dict:
    """
    Extended filter bar supporting both overview and scanner modes.

    New options:
        show_trend: Show trend filter (UPTREND/DOWNTREND/SIDEWAYS)
        show_direction: Show direction filter (BUY/SELL/PULLBACK/BOUNCE)
        show_strength_slider: Show min strength slider
        show_value_slider: Show min GTGD (trading value) slider
    """
    result = {}

    # ... existing initialization ...

    # Add new session state keys
    if f'{key_prefix}_trend' not in st.session_state:
        st.session_state[f'{key_prefix}_trend'] = "all"
    if f'{key_prefix}_direction' not in st.session_state:
        st.session_state[f'{key_prefix}_direction'] = "all"
    if f'{key_prefix}_min_strength' not in st.session_state:
        st.session_state[f'{key_prefix}_min_strength'] = 0
    if f'{key_prefix}_min_value' not in st.session_state:
        st.session_state[f'{key_prefix}_min_value'] = 0

    # Calculate column weights based on enabled options
    col_specs = []
    if show_timeframe: col_specs.append(1.2)
    if show_sector: col_specs.append(1.5)
    if show_signal_type: col_specs.append(1.2)
    if show_trend: col_specs.append(1.2)
    if show_direction: col_specs.append(1.2)
    if show_search: col_specs.append(2)
    if show_refresh: col_specs.append(0.8)

    # ... existing column rendering ...

    # NEW: Trend filter
    if show_trend:
        with cols[col_idx]:
            trend_options = list(TREND_OPTIONS.keys())
            current_trend = st.session_state.get(f'{key_prefix}_trend', "all")
            trend_index = trend_options.index(current_trend) if current_trend in trend_options else 0
            selected_trend = st.selectbox(
                "Trend",
                trend_options,
                index=trend_index,
                format_func=lambda x: TREND_OPTIONS[x],
                key=f'{key_prefix}_trend_select',
                label_visibility="collapsed"
            )
            st.session_state[f'{key_prefix}_trend'] = selected_trend
            result['trend'] = selected_trend
        col_idx += 1

    # NEW: Direction filter
    if show_direction:
        with cols[col_idx]:
            dir_options = list(DIRECTION_OPTIONS.keys())
            current_dir = st.session_state.get(f'{key_prefix}_direction', "all")
            dir_index = dir_options.index(current_dir) if current_dir in dir_options else 0
            selected_dir = st.selectbox(
                "Direction",
                dir_options,
                index=dir_index,
                format_func=lambda x: DIRECTION_OPTIONS[x],
                key=f'{key_prefix}_direction_select',
                label_visibility="collapsed"
            )
            st.session_state[f'{key_prefix}_direction'] = selected_dir
            result['direction'] = selected_dir
        col_idx += 1

    # ... rest of existing code ...

    return result


def render_scanner_filters(service, key_prefix: str = "scanner") -> Dict:
    """
    Convenience wrapper for Stock Scanner with all scanner-specific filters.
    """
    return render_ta_filters(
        service,
        show_timeframe=True,
        show_sector=True,
        show_signal_type=True,
        show_trend=True,
        show_direction=True,
        show_search=True,
        show_refresh=True,
        key_prefix=key_prefix
    )
```

### Add sliders in separate row (optional advanced filters):

```python
def render_scanner_advanced_filters(key_prefix: str = "scanner") -> Dict:
    """Render advanced scanner filters (sliders) in a separate row."""
    result = {}

    col1, col2 = st.columns(2)

    with col1:
        min_strength = st.slider(
            "Min Strength",
            min_value=0,
            max_value=100,
            value=st.session_state.get(f'{key_prefix}_min_strength', 0),
            key=f'{key_prefix}_strength_slider',
            help="Minimum signal strength"
        )
        st.session_state[f'{key_prefix}_min_strength'] = min_strength
        result['min_strength'] = min_strength

    with col2:
        min_value = st.slider(
            "Min GTGD (tỷ)",
            min_value=0,
            max_value=100,
            value=st.session_state.get(f'{key_prefix}_min_value', 0),
            key=f'{key_prefix}_value_slider',
            help="Minimum trading value"
        )
        st.session_state[f'{key_prefix}_min_value'] = min_value
        result['min_value'] = min_value

    return result
```

---

## Task 4.2: Refactor Stock Scanner

**File:** `WEBAPP/pages/technical/components/stock_scanner.py` (MODIFY)

### Before (~100 lines of manual filters):

```python
# REMOVE all of this:
def render_stock_scanner_filters():
    col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
    with col1:
        search = st.text_input("Quick Search", ...)
    with col2:
        sector = st.selectbox("Sector", ...)
    # ... 80+ more lines ...
```

### After (use shared component):

```python
from WEBAPP.pages.technical.components.ta_filter_bar import (
    render_scanner_filters,
    render_scanner_advanced_filters
)

def render_stock_scanner(service: TADashboardService):
    """Stock Scanner tab with consolidated filters."""

    st.subheader("Stock Scanner")

    # Row 1: Main filters (using shared component)
    filters = render_scanner_filters(service, key_prefix="scanner")

    # Row 2: Advanced filters (sliders)
    with st.expander("Advanced Filters", expanded=False):
        advanced = render_scanner_advanced_filters(key_prefix="scanner")
        filters.update(advanced)

    # Use filter values
    timeframe = filters.get('timeframe', '180D')
    sector = filters.get('sector', 'All')
    signal_type = filters.get('signal_type', 'all')
    trend = filters.get('trend', 'all')
    direction = filters.get('direction', 'all')
    search = filters.get('search', '')
    min_strength = filters.get('min_strength', 0)
    min_value = filters.get('min_value', 0)

    # Rest of scanner logic (unchanged)
    # ...
```

---

## Verification Checklist

- [ ] `ta_filter_bar.py` has new parameters: `show_trend`, `show_direction`
- [ ] `render_scanner_filters()` convenience function works
- [ ] Stock Scanner uses shared filter bar
- [ ] All existing scanner functionality still works
- [ ] Filter values persist correctly
- [ ] ~100 lines removed from `stock_scanner.py`

---

## Files Changed

| File | Action | Lines |
|------|--------|-------|
| `WEBAPP/pages/technical/components/ta_filter_bar.py` | MODIFY | +80 |
| `WEBAPP/pages/technical/components/stock_scanner.py` | MODIFY | -100, +15 |

**Net change:** -5 lines (consolidation saves code)
