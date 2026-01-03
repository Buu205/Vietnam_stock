# Phase 5: Forecast Filter Cleanup

**Effort:** 1 day
**Dependencies:** Phase 3 (sync integration)
**Files to modify:** 2

---

## Objectives

1. Remove duplicate sidebar filters from Forecast dashboard
2. Keep header filters only (via `forecast_filter_bar.py`)
3. Ensure header filters work properly after sidebar removal

---

## Task 5.1: Remove Sidebar Filters

**File:** `WEBAPP/pages/forecast/forecast_dashboard.py` (MODIFY)

### Current structure (lines 142-180):

```python
# REMOVE THIS ENTIRE SECTION:
st.sidebar.markdown("## Filters")

# Rating filter
all_ratings = ['STRONG BUY', 'BUY', 'HOLD', 'SELL', 'N/A']
available_ratings = df['rating'].unique().tolist() if 'rating' in df.columns else []
rating_filter = st.sidebar.multiselect(
    "Rating",
    options=[r for r in all_ratings if r in available_ratings],
    default=[r for r in ['STRONG BUY', 'BUY', 'HOLD'] if r in available_ratings]
)

# Sector filter
all_sectors = ['All'] + service.get_sectors_list()
sector_filter = st.sidebar.selectbox(
    "Sector",
    options=all_sectors,
    index=0
)

# Sort by
sort_options = {
    "Upside % (High to Low)": ("upside_pct", False),
    # ... more options ...
}
sort_by = st.sidebar.selectbox("Sort By", options=list(sort_options.keys()), index=0)

st.sidebar.markdown("---")
if st.sidebar.button("Refresh Data", width='stretch'):
    st.cache_data.clear()
    st.rerun()
```

### After (no sidebar filters):

```python
# Sidebar section removed entirely
# All filtering handled by header filter bar in each tab
```

---

## Task 5.2: Verify Header Filters

**File:** `WEBAPP/components/filters/forecast_filter_bar.py` (VERIFY)

Ensure existing header filter bar has all necessary filters:

```python
def render_forecast_filters(service, key_prefix: str = "forecast") -> Dict:
    """
    Should include:
    - Sector filter
    - Rating filter (multiselect)
    - Sort by
    - Extended columns toggle
    - Refresh button
    """
    # Verify this function exists and works
    pass
```

### Update tab imports:

Each tab should use the header filter bar:

```python
# In tabs/bsc_universal_tab.py:
from WEBAPP.components.filters.forecast_filter_bar import render_forecast_filters

def render_bsc_universal_tab(df, service, rating_filter, sector_filter, sort_by):
    # Render header filters
    filters = render_forecast_filters(service)

    # Use filters from header bar instead of sidebar parameters
    rating_filter = filters['rating']
    sector_filter = filters['sector']
    sort_by = filters['sort_by']

    # Rest of tab logic...
```

---

## Task 5.3: Update Tab Function Signatures

**Files:** Tab modules in `WEBAPP/pages/forecast/tabs/`

Change from receiving sidebar filter values as parameters:

```python
# BEFORE:
def render_bsc_universal_tab(df, service, rating_filter, sector_filter, sort_by):
    pass

# AFTER:
def render_bsc_universal_tab(df, service):
    filters = render_forecast_filters(service)
    rating_filter = filters['rating']
    sector_filter = filters['sector']
    sort_by = filters['sort_by']
```

---

## Verification Checklist

- [ ] Sidebar no longer shows Forecast filters
- [ ] Each tab renders its own header filter bar
- [ ] Rating filter works (multiselect)
- [ ] Sector filter works
- [ ] Sort by works
- [ ] Extended columns toggle works
- [ ] Refresh button works
- [ ] All existing Forecast functionality intact

---

## Files Changed

| File | Action | Lines |
|------|--------|-------|
| `WEBAPP/pages/forecast/forecast_dashboard.py` | MODIFY | -40 |
| `WEBAPP/pages/forecast/tabs/bsc_universal_tab.py` | MODIFY | +5 |
| `WEBAPP/pages/forecast/tabs/sector_tab.py` | MODIFY | +5 |
| `WEBAPP/pages/forecast/tabs/achievement_tab.py` | MODIFY | +5 |
| `WEBAPP/pages/forecast/tabs/consensus_tab.py` | MODIFY | +5 |

**Net change:** -20 lines
