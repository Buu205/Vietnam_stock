# Performance Optimization Plan

**Created:** 2026-01-04
**Status:** Active (Phase 1-3 Complete)
**Priority:** High
**Scope:** WEBAPP caching, data loading, UX improvements

---

## Objective

Optimize dashboard performance through:
1. Fix broken caching in Forecast module
2. Add missing caches to core data loading
3. Implement lazy loading for tabs
4. Standardize TTL values
5. UX improvements (dark mode, responsive, loading states)

---

## Phase 1: Critical Caching Fixes (P0)

### Task 1.1: Fix Forecast Module Caching

**File:** `WEBAPP/domains/forecast/data_loading_forecast_csv.py`

**Problem:** 4 functions have cache disabled due to "Series hash error"

**Functions to fix:**
- [ ] `load_forecast_csv()` (line 43)
- [ ] `load_market_data()` (line 80)
- [ ] `merge_forecast_with_market()` (line 172)
- [ ] `get_forecast_summary()` (line 602)

**Solution:** Use `hash_funcs` or return tuple instead of DataFrame

```python
@st.cache_data(ttl=1800, hash_funcs={pd.DataFrame: lambda df: df.to_json()})
def load_forecast_csv(_self) -> pd.DataFrame:
    ...
```

**Effort:** 30 min | **Impact:** High

---

### Task 1.2: Add Cache to Core Data Loading

**File:** `WEBAPP/core/data_loading.py`

**Functions to cache:**
- [ ] `load_valuation_generic()` - Add `@st.cache_data(ttl=3600)`
- [ ] `load_symbol_list()` - Add `@st.cache_data(ttl=86400)`

**Effort:** 15 min | **Impact:** High

---

## Phase 2: Standardize TTL Values (P1)

### Task 2.1: Define TTL Tiers

Create constant file or add to `WEBAPP/core/constants.py`:

```python
# Cache TTL tiers (seconds)
CACHE_TTL_HOT = 60        # Real-time data (technical)
CACHE_TTL_WARM = 300      # Frequently updated (news, prices)
CACHE_TTL_COLD = 3600     # Infrequently updated (fundamentals)
CACHE_TTL_STATIC = 86400  # Static data (symbols, sectors)
```

### Task 2.2: Update Existing Caches

| Current | New | Files |
|---------|-----|-------|
| 60s | CACHE_TTL_HOT | technical data |
| 300s | CACHE_TTL_WARM | news, commodity |
| 900s | CACHE_TTL_WARM | news (reduce to 300s) |
| 3600s | CACHE_TTL_COLD | dashboards |

**Effort:** 30 min | **Impact:** Low (consistency)

---

## Phase 3: Lazy Loading for Tabs (P2)

### Task 3.1: Identify Tab-Heavy Dashboards

| Dashboard | Tabs | Data Load Issue |
|-----------|------|-----------------|
| Technical | 4 tabs | All load on page |
| Forecast | 3 tabs | All load on page |
| Sector | Multiple sections | All load on page |

### Task 3.2: Implement Lazy Loading Pattern

```python
# Current (bad)
tab1, tab2, tab3 = st.tabs(["A", "B", "C"])
with tab1:
    data_a = load_heavy_data_a()  # Always loads
with tab2:
    data_b = load_heavy_data_b()  # Always loads

# Better (lazy)
tab1, tab2, tab3 = st.tabs(["A", "B", "C"])
with tab1:
    data_a = load_heavy_data_a()  # Loads
with tab2:
    if st.session_state.get('tab2_loaded'):
        data_b = load_heavy_data_b()
    else:
        st.button("Load Data", on_click=lambda: st.session_state.update({'tab2_loaded': True}))
```

**Or use st.fragment (Streamlit 1.33+):**
```python
@st.fragment
def tab2_content():
    data_b = load_heavy_data_b()
    # render...
```

**Effort:** 2-3 hours | **Impact:** Medium

---

## Phase 4: UX Improvements (P3)

### Task 4.1: Dark Mode Toggle

**Location:** `WEBAPP/core/theme.py` or new `WEBAPP/core/dark_mode.py`

```python
# Simple toggle using session state
if st.sidebar.toggle("Dark Mode", key="dark_mode"):
    st.markdown(DARK_MODE_CSS, unsafe_allow_html=True)
```

**Effort:** 1 hour | **Impact:** Medium (user preference)

### Task 4.2: Loading States / Skeleton Screens

Add spinner or skeleton to heavy data loads:

```python
with st.spinner("Loading data..."):
    data = load_heavy_data()
```

Or custom skeleton:
```python
placeholder = st.empty()
placeholder.markdown("⏳ Loading...")
data = load_data()
placeholder.empty()
```

**Effort:** 30 min | **Impact:** Medium (perceived performance)

### Task 4.3: Responsive Breakpoints

Check existing CSS in `WEBAPP/core/styles.py`:
- Add media queries for mobile/tablet
- Adjust column layouts

**Effort:** 1-2 hours | **Impact:** Medium

---

## Summary

| Phase | Tasks | Effort | Impact |
|-------|-------|--------|--------|
| 1 | Fix caching (P0) | 45 min | High |
| 2 | Standardize TTL (P1) | 30 min | Low |
| 3 | Lazy loading (P2) | 2-3 hrs | Medium |
| 4 | UX improvements (P3) | 3-4 hrs | Medium |

**Total Estimated Effort:** 6-8 hours

---

## Execution Order

1. **Start:** Phase 1 (critical caching) → immediate performance gain
2. **Next:** Phase 2 (TTL) → quick win, consistency
3. **Then:** Phase 4.2 (loading states) → better UX during loads
4. **Later:** Phase 3 (lazy loading) → requires more refactoring
5. **Finally:** Phase 4.1, 4.3 (dark mode, responsive) → polish

---

## Verification

After each phase:
1. Test dashboard load time (Chrome DevTools → Network)
2. Check Streamlit cache stats in terminal
3. Verify no regressions in functionality
