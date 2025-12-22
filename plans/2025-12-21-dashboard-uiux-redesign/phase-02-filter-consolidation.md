# Phase 2: Filter Consolidation

**Goal:** Single horizontal filter bar, remove sidebar filter duplication
**Effort:** 2 days | **Risk:** Medium

---

## Current State Analysis

### sector_dashboard.py Filter Locations
1. **Sidebar (lines 62-100):** Metric selector, time range, refresh button
2. **Tab 1 VNIndex (line 316):** Index selectbox
3. **Tab 2 Distribution (line 383):** Group radio (Sectors/Indices)
4. **Tab 3 Individual (lines 767-804):** Scope group radio + selectbox
5. **Tab 4 Macro (line 1074):** Category radio
6. **Tab 5 Commodity (line 1396):** Commodity selectbox

### Problem
- `selected_metric` and `days` set in sidebar
- Some tabs have additional inline filters
- User must scroll to sidebar, then scroll to tab content

---

## Solution: Global Filter Bar Component

### 1. Create global_filter_bar.py

**File:** `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/components/filters/global_filter_bar.py`

```python
"""
Global Filter Bar Component
===========================
Horizontal filter bar for chart-first dashboards.
Replaces sidebar filters with sticky top bar.

Usage:
    from WEBAPP.components.filters.global_filter_bar import render_global_filters

    filters = render_global_filters(
        show_metric=True,
        show_time_range=True
    )
    metric = filters['metric']
    days = filters['days']
"""

import streamlit as st
from typing import Dict, List, Optional

# Constants
METRIC_OPTIONS = ["PE TTM", "PB", "P/S Ratio", "EV/EBITDA"]
METRIC_MAP = {"PE TTM": "pe_ttm", "PB": "pb", "P/S Ratio": "ps", "EV/EBITDA": "ev_ebitda"}
TIME_RANGE_OPTIONS = {"3M": 63, "6M": 126, "1Y": 252, "3Y": 756, "ALL": 2000}


def render_global_filters(
    show_metric: bool = True,
    show_time_range: bool = True,
    show_ticker_search: bool = False,
    show_refresh: bool = True,
    key_prefix: str = "global"
) -> Dict:
    """
    Render horizontal filter bar at top of page.

    Args:
        show_metric: Show valuation metric selector
        show_time_range: Show time range selector
        show_ticker_search: Show ticker search input
        show_refresh: Show refresh button
        key_prefix: Prefix for session_state keys

    Returns:
        Dict with filter values:
        {
            'metric': str,  # Display name ("PE TTM")
            'metric_col': str,  # Column name ("pe_ttm")
            'days': int,  # Trading days
            'ticker': str,  # Ticker search value
            'refresh': bool  # Refresh button clicked
        }
    """
    result = {}

    # Initialize session state
    if f'{key_prefix}_metric' not in st.session_state:
        st.session_state[f'{key_prefix}_metric'] = "PE TTM"
    if f'{key_prefix}_time_range' not in st.session_state:
        st.session_state[f'{key_prefix}_time_range'] = "3Y"

    # Calculate column count
    col_count = sum([show_metric, show_time_range, show_ticker_search, show_refresh])
    if col_count == 0:
        return result

    # Create columns
    cols = st.columns(col_count)
    col_idx = 0

    # Metric selector
    if show_metric:
        with cols[col_idx]:
            selected_metric = st.selectbox(
                "Metric",
                METRIC_OPTIONS,
                index=METRIC_OPTIONS.index(st.session_state[f'{key_prefix}_metric']),
                key=f'{key_prefix}_metric_select',
                label_visibility="collapsed"
            )
            st.session_state[f'{key_prefix}_metric'] = selected_metric
            result['metric'] = selected_metric
            result['metric_col'] = METRIC_MAP[selected_metric]
        col_idx += 1

    # Time range selector
    if show_time_range:
        with cols[col_idx]:
            time_options = list(TIME_RANGE_OPTIONS.keys())
            selected_range = st.selectbox(
                "Time Range",
                time_options,
                index=time_options.index(st.session_state[f'{key_prefix}_time_range']),
                key=f'{key_prefix}_time_range_select',
                label_visibility="collapsed"
            )
            st.session_state[f'{key_prefix}_time_range'] = selected_range
            result['days'] = TIME_RANGE_OPTIONS[selected_range]
        col_idx += 1

    # Ticker search
    if show_ticker_search:
        with cols[col_idx]:
            ticker = st.text_input(
                "Ticker",
                placeholder="VCB, ACB...",
                key=f'{key_prefix}_ticker_input',
                label_visibility="collapsed"
            )
            result['ticker'] = ticker.upper().strip()
        col_idx += 1

    # Refresh button
    if show_refresh:
        with cols[col_idx]:
            if st.button("Refresh", key=f'{key_prefix}_refresh', use_container_width=True):
                st.cache_data.clear()
                result['refresh'] = True
            else:
                result['refresh'] = False

    return result


def get_filter_state(key_prefix: str = "global") -> Dict:
    """
    Get current filter state from session_state.
    Use when filters were rendered earlier in the page.

    Returns:
        Dict with metric, metric_col, days
    """
    metric = st.session_state.get(f'{key_prefix}_metric', "PE TTM")
    time_range = st.session_state.get(f'{key_prefix}_time_range', "3Y")

    return {
        'metric': metric,
        'metric_col': METRIC_MAP.get(metric, "pe_ttm"),
        'days': TIME_RANGE_OPTIONS.get(time_range, 756)
    }
```

---

### 2. Update sector_dashboard.py

**Remove sidebar filters (lines 62-100):**
```python
# DELETE these lines:
st.sidebar.markdown("## Filters")
st.sidebar.markdown("### Valuation Metric")
...
st.sidebar.button("Refresh Data")
```

**Add global filter bar after header (line 59):**
```python
# After st.markdown("---")
from WEBAPP.components.filters.global_filter_bar import render_global_filters

# Render horizontal filter bar
filters = render_global_filters(
    show_metric=True,
    show_time_range=True,
    show_refresh=True,
    key_prefix="sector"
)

selected_metric = filters.get('metric', "PE TTM")
primary_metric = filters.get('metric_col', "pe_ttm")
days = filters.get('days', 756)
days_distribution = 2000  # Always use ALL for distribution

if filters.get('refresh'):
    st.rerun()
```

---

### 3. CSS: Sticky Filter Header

**Add to styles.py (after sidebar section):**

```css
/* ============================================================
   STICKY FILTER BAR
   ============================================================ */
.filter-bar-container {
    position: sticky;
    top: 0;
    z-index: var(--z-sticky);
    background: linear-gradient(180deg, var(--bg-void) 0%, var(--bg-deep) 100%);
    padding: 0.75rem 0;
    margin: -0.5rem -2.5rem 1rem -2.5rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    border-bottom: 1px solid var(--glass-border);
    backdrop-filter: blur(12px);
}

/* Compact filter inputs in top bar */
.filter-bar-container .stSelectbox > div > div {
    min-height: 36px !important;
    font-size: 13px !important;
}

.filter-bar-container .stButton > button {
    min-height: 36px !important;
    padding: 0.4rem 1rem !important;
    font-size: 13px !important;
}
```

**Usage in page:**
```python
st.markdown('<div class="filter-bar-container">', unsafe_allow_html=True)
filters = render_global_filters(...)
st.markdown('</div>', unsafe_allow_html=True)
```

---

## Implementation Steps

1. **Create global_filter_bar.py**
   - Copy component code above
   - Test import works

2. **Update sector_dashboard.py**
   - Remove sidebar filter code (lines 62-100)
   - Add global filter bar after header
   - Update variable references (`selected_metric`, `days`)

3. **Update styles.py**
   - Add sticky filter bar CSS

4. **Test**
   - Filters render horizontally
   - State persists across tab switches
   - Charts respond to filter changes

---

## Validation Checklist
- [ ] Global filter bar renders after title
- [ ] Metric selector works (PE, PB, PS, EV/EBITDA)
- [ ] Time range selector works (3M, 6M, 1Y, 3Y, ALL)
- [ ] Refresh button clears cache and reruns
- [ ] Tab-specific filters still work (index selector, category radio)
- [ ] No duplicate filters in sidebar
- [ ] Filter state persists within page

---

## Rollback
Keep original sidebar code commented out until phase validated.
