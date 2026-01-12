# Brainstorm: Filter Relocation to Header

**Date:** 2026-01-03
**Topic:** Move filters from sidebar to header filter bar for BSC Forecast & FX Commodities pages

---

## Current State Analysis

### 1. BSC Forecast Dashboard

**File:** `WEBAPP/pages/forecast/forecast_dashboard.py`

**Current Implementation (Sidebar):**
```python
# Lines 145-183
st.sidebar.markdown("## Filters")
rating_filter = st.sidebar.multiselect("Rating", ...)
sector_filter = st.sidebar.selectbox("Sector", ...)
sort_by = st.sidebar.selectbox("Sort By", ...)
st.sidebar.button("Refresh Data", ...)
```

**Header Filter Bar Component EXISTS but NOT USED:**
- File: `WEBAPP/components/filters/forecast_filter_bar.py`
- Function: `render_filter_bar()` - fully implemented
- Imported in `bsc_universal_tab.py` but never called!

**Tab Structure:**
| Tab | Filters Needed |
|-----|----------------|
| 0 - BSC Universal | Sector, Rating, Sort, Extended toggle |
| 1 - Sector | Sector, Sort (sector options) |
| 2 - Achievement | Sector only |
| 3 - Consensus | Sector, Consensus Status |

### 2. FX & Commodities Dashboard

**File:** `WEBAPP/pages/fx_commodities/fx_commodities_dashboard.py`

**Current Implementation (Sidebar):**
```python
# Lines 251-258
with st.sidebar:
    st.markdown("### Time Range")
    days = st.selectbox("Select Period", options=[30, 90, 180, 365, 730], ...)
```

**No header filter component exists** for this page.

---

## Existing Pattern: Header Filter Bar

**Reference:** `WEBAPP/components/filters/fundamental_filter_bar.py`

Pattern used by Company/Bank/Security dashboards:
```python
def render_fundamental_filters(tickers: list, entity_type: str) -> dict:
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    with col1:
        ticker = st.selectbox("Ticker", ...)
    with col2:
        period = st.selectbox("Period", ...)
    # ...
    return {'ticker': ticker, 'period': period, ...}
```

**Key Features:**
- Horizontal column layout
- Compact, inline filters
- Returns dict with filter values
- `label_visibility='collapsed'` for compact UI

---

## Proposed Solution

### Strategy: Global Filter Bar + Tab-Specific Filters

**Option A: Single Filter Bar Before Tabs** (Recommended)
- Place common filters (Sector, Sort) in header before tabs
- Tab-specific filters (Extended toggle, Consensus) inside tab

**Option B: Per-Tab Filter Bar**
- Each tab renders its own filter bar
- More flexible but potential UI inconsistency

**Recommendation:** Option A for cleaner UX

---

## Implementation Plan

### Phase 1: BSC Forecast Dashboard

#### Step 1.1: Modify Main Dashboard
**File:** `WEBAPP/pages/forecast/forecast_dashboard.py`

```python
# REMOVE sidebar filters (lines 145-183)
# DELETE:
# st.sidebar.markdown("## Filters")
# rating_filter = st.sidebar.multiselect(...)
# sector_filter = st.sidebar.selectbox(...)
# sort_by = st.sidebar.selectbox(...)

# ADD after header, before tabs:
from WEBAPP.components.filters.forecast_filter_bar import render_filter_bar

# Global filter bar
sectors_list = service.get_sectors_list()
global_filters = render_filter_bar(
    tab_id=99,  # Global
    sectors=sectors_list,
    show_sector=True,
    show_rating=True,
    show_sort=True,
    sort_options=SORT_OPTIONS['stock'],
    show_extended_toggle=False,  # Tab-specific
    show_consensus_filter=False,  # Tab-specific
    key_prefix='forecast_global'
)
```

#### Step 1.2: Modify BSC Universal Tab
**File:** `WEBAPP/pages/forecast/tabs/bsc_universal_tab.py`

```python
# Use filter values from parent
# Add tab-specific toggle only
show_extended = st.toggle("Extended Columns", key="bsc_extended")
```

#### Step 1.3: Tab Parameter Refactor

Current: Tabs receive filters as function parameters
```python
render_bsc_universal_tab(df, service, rating_filter, sector_filter, sort_by)
```

New: Tabs receive filter dict from parent
```python
render_bsc_universal_tab(df, service, filters=global_filters)
```

---

### Phase 2: FX & Commodities Dashboard

#### Step 2.1: Create Filter Bar Component
**File:** `WEBAPP/components/filters/fx_filter_bar.py`

```python
"""
FX & Commodities Filter Bar
===========================
Header filter bar for FX & Commodities dashboard.
"""

import streamlit as st
from typing import Dict, Any

TIME_RANGE_OPTIONS = [
    ('1M', 30),
    ('3M', 90),
    ('6M', 180),
    ('1Y', 365),
    ('2Y', 730),
]

def render_fx_filter_bar(key_prefix: str = 'fx') -> Dict[str, Any]:
    """Render horizontal filter bar for FX page."""
    filters = {}

    col1, col2 = st.columns([2, 8])

    with col1:
        labels = [opt[0] for opt in TIME_RANGE_OPTIONS]
        values = [opt[1] for opt in TIME_RANGE_OPTIONS]

        selected = st.selectbox(
            "Time Range",
            options=labels,
            index=2,  # Default 6M
            key=f"{key_prefix}_time_range",
            label_visibility='collapsed'
        )
        filters['days'] = values[labels.index(selected)]

    return filters
```

#### Step 2.2: Modify FX Dashboard
**File:** `WEBAPP/pages/fx_commodities/fx_commodities_dashboard.py`

```python
# REMOVE sidebar (lines 251-258)
# DELETE:
# with st.sidebar:
#     st.markdown("### Time Range")
#     days = st.selectbox(...)

# ADD after header:
from WEBAPP.components.filters.fx_filter_bar import render_fx_filter_bar

# Header filter bar
filters = render_fx_filter_bar()
days = filters['days']
```

---

## UI/UX Design Considerations

### Filter Bar Layout

```
┌──────────────────────────────────────────────────────────────────┐
│ BSC Forecast Analysis                                            │
│ 92 stocks with PE/PB Forward 2025-2026 from BSC Research        │
├──────────────────────────────────────────────────────────────────┤
│ [Sector ▼]  [Rating ▼]  [Sort By ▼]  [🔄 Refresh]              │
├──────────────────────────────────────────────────────────────────┤
│ [BSC Universal] [Sector] [Achievement] [Consensus]              │
└──────────────────────────────────────────────────────────────────┘
```

### CSS Styling

```css
/* Filter bar container */
.filter-bar {
    display: flex;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 16px;
}

/* Compact select boxes */
.filter-bar .stSelectbox {
    min-width: 140px;
}

/* Match existing glassmorphism theme */
.filter-bar .stSelectbox > div > div {
    background: rgba(37, 32, 51, 0.6);
    border: 1px solid rgba(139, 92, 246, 0.3);
}
```

---

## Files to Modify

| File | Action | Priority |
|------|--------|----------|
| `forecast_dashboard.py` | Remove sidebar, add header filter | HIGH |
| `bsc_universal_tab.py` | Use filter dict, add extended toggle only | HIGH |
| `sector_tab.py` | Use filter dict | MEDIUM |
| `achievement_tab.py` | Use filter dict | MEDIUM |
| `consensus_tab.py` | Add consensus filter toggle | MEDIUM |
| `fx_commodities_dashboard.py` | Remove sidebar, add header filter | HIGH |
| NEW: `fx_filter_bar.py` | Create component | HIGH |
| `styles.py` | Add filter-bar CSS (optional) | LOW |

---

## Success Criteria

- [ ] BSC Forecast sidebar removed, header filter works
- [ ] All 4 tabs filter correctly with header filters
- [ ] FX Commodities sidebar removed, header filter works
- [ ] UI consistent with Company/Bank/Security pages
- [ ] No breaking changes to existing functionality
- [ ] Filter state persists across tab switches

---

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| Header filters | Cleaner UI, more visible | Less space for many filters |
| Sidebar filters | More space, standard | Hidden, requires click |
| Per-tab filters | Flexibility | Inconsistent UX |
| Global filters | Consistent, simple | May not fit all tabs |

**Recommendation:** Global header filters + tab-specific toggles for best UX.

---

## Notes

- `forecast_filter_bar.py` already implements header filter bar - just needs to be used
- FX dashboard needs simpler filter bar (only time range)
- Consider adding pill-style filter buttons for time range (like Company page Period filter)
