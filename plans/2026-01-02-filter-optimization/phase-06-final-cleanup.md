# Phase 6: FX/Commodities + Final Cleanup

**Effort:** 1 day
**Dependencies:** All previous phases
**Files to modify:** 3-4

---

## Objectives

1. Move FX/Commodities timeframe from sidebar to header
2. Verify and delete unused `valuation_filters.py`
3. Clean up obsolete session state keys
4. Document new filter architecture

---

## Task 6.1: FX/Commodities Header Filters

**File:** `WEBAPP/pages/fx_commodities/fx_commodities_dashboard.py` (MODIFY)

### Create header filter bar:

```python
from WEBAPP.components.filters.constants import TIMEFRAME_OPTIONS

def render_fx_header_filters(key_prefix: str = "fx") -> Dict:
    """Render header filter bar for FX/Commodities."""
    result = {}

    cols = st.columns([1.5, 1.5, 0.8])

    # Time range
    with cols[0]:
        time_options = list(TIMEFRAME_OPTIONS.keys())
        current = st.session_state.get(f'{key_prefix}_timeframe', '1Y')
        index = time_options.index(current) if current in time_options else 4

        selected = st.selectbox(
            "Time Range",
            time_options,
            index=index,
            key=f'{key_prefix}_time_select',
            label_visibility="collapsed"
        )
        st.session_state[f'{key_prefix}_timeframe'] = selected
        result['timeframe'] = selected
        result['days'] = TIMEFRAME_OPTIONS[selected]

    # Category (Commodities/FX/Macro)
    with cols[1]:
        categories = ["Commodities", "FX", "Macro"]
        current_cat = st.session_state.get(f'{key_prefix}_category', 'Commodities')
        cat_index = categories.index(current_cat) if current_cat in categories else 0

        selected_cat = st.selectbox(
            "Category",
            categories,
            index=cat_index,
            key=f'{key_prefix}_category_select',
            label_visibility="collapsed"
        )
        st.session_state[f'{key_prefix}_category'] = selected_cat
        result['category'] = selected_cat

    # Refresh
    with cols[2]:
        if st.button("⟳", key=f'{key_prefix}_refresh', help="Refresh"):
            st.cache_data.clear()
            result['refresh'] = True
        else:
            result['refresh'] = False

    return result
```

### Remove sidebar timeframe:

```python
# REMOVE from sidebar:
# fx_timeframe = st.sidebar.selectbox("Time Range", ...)

# ADD after title:
st.title("FX & Commodities")

filters = render_fx_header_filters()
timeframe = filters['timeframe']
category = filters['category']
```

---

## Task 6.2: Verify Unused Files

**File:** `WEBAPP/components/filters/valuation_filters.py` (VERIFY/DELETE)

Check if this file is imported anywhere:

```bash
grep -r "valuation_filters" WEBAPP/ --include="*.py"
```

If no imports found, delete the file:

```bash
rm WEBAPP/components/filters/valuation_filters.py
```

---

## Task 6.3: Clean Up Session State

**File:** `WEBAPP/core/session_state.py` (MODIFY)

Review and clean up obsolete keys:

```python
PAGE_STATE_DEFAULTS: Dict[str, Dict[str, Any]] = {
    'global': {
        # REMOVE these obsolete keys:
        # 'global_ticker_search': '',  # Removed in Phase 1
        # 'quick_search_ticker': None,  # Removed in Phase 1
        # 'search_select': None,  # Removed in Phase 1

        # KEEP these sync keys:
        'sync_last_ticker': None,
        'sync_last_entity': None,
        'sync_last_sector': None,
        'sync_timestamp': None,
    },
    # ... rest of pages
}
```

---

## Task 6.4: Document Architecture

**File:** `docs/filter-architecture.md` (NEW - optional)

```markdown
# Filter Architecture

## Overview

All dashboard filters follow header-based pattern:
- Sidebar: Navigation only
- Header: Page-specific filters

## Components

### Shared Filter Bars
- `fundamental_filter_bar.py`: Company/Bank/Security
- `forecast_filter_bar.py`: Forecast tabs
- `ta_filter_bar.py`: Technical dashboard

### Centralized Constants
- `WEBAPP/components/filters/constants.py`

### Cross-Page Sync
- `sync_last_ticker`: Last viewed ticker
- `sync_last_entity`: Entity type (BANK/COMPANY/SECURITY)
- `set_synced_ticker()`: Set when ticker changes
- `get_synced_ticker()`: Read in Forecast/Technical

## Adding New Pages

1. Import appropriate filter bar
2. Call `render_*_filters()` after title
3. Use returned filter values
```

---

## Verification Checklist

- [ ] FX/Commodities filters in header (not sidebar)
- [ ] `valuation_filters.py` deleted (if unused)
- [ ] No import errors after cleanup
- [ ] All pages load correctly
- [ ] Session state clean (no obsolete keys)
- [ ] Documentation updated (optional)

---

## Files Changed

| File | Action | Lines |
|------|--------|-------|
| `WEBAPP/pages/fx_commodities/fx_commodities_dashboard.py` | MODIFY | +30, -15 |
| `WEBAPP/components/filters/valuation_filters.py` | DELETE | -455 |
| `WEBAPP/core/session_state.py` | MODIFY | -5 |
| `docs/filter-architecture.md` | CREATE | +50 (optional) |

**Net change:** -395 lines (mostly from deleting unused file)

---

## Final Summary

### Total Code Impact

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Duplicated filter code | ~270 | 0 | -270 |
| Unused code (valuation_filters) | 455 | 0 | -455 |
| New shared components | 0 | ~300 | +300 |
| **Net lines** | - | - | **-425** |

### Architecture Improvements

- ✅ All filters in header (consistent UX)
- ✅ Shared components (DRY)
- ✅ Cross-page sync (Fundamental → Forecast/Technical)
- ✅ Centralized constants
- ✅ Scalable design patterns
