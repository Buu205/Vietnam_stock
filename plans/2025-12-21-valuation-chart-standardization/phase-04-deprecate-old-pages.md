# Phase 4: Deprecate Old Pages

**Phase ID:** 04
**Status:** Pending
**Dependencies:** Phase 2 + Phase 3 (both complete)
**Parallel With:** None (cleanup phase)
**Estimated Effort:** Day 4

---

## File Ownership (EXCLUSIVE)

| File | Action | Lines |
|------|--------|-------|
| `WEBAPP/pages/valuation/valuation_dashboard.py` | DEPRECATE | -1000 |
| `WEBAPP/main_app.py` | MODIFY | ~20 |

---

## Task Checklist

### 4.1 Add Redirect to valuation_dashboard.py

- [ ] Keep `valuation_dashboard.py` minimal with redirect:
  ```python
  """
  DEPRECATED: Valuation functionality moved to sector_dashboard.py
  This page redirects to the new location.
  """
  import streamlit as st

  st.warning("This page has been merged into Sector & Valuation Dashboard.")
  st.markdown("[Go to Sector & Valuation →](/sector)")
  ```
- [ ] Add deprecation warning in docstring
- [ ] Remove all old chart code
- [ ] Keep for 1 release cycle, then delete

### 4.2 Update main_app.py Navigation

- [ ] Update page configuration:
  ```python
  pages = {
      "Sector & Valuation": "pages/sector/sector_dashboard.py",  # Merged
      "BSC Forecast": "pages/forecast/forecast_dashboard.py",
      # "Valuation": REMOVED or redirect
  }
  ```
- [ ] Update sidebar navigation labels
- [ ] Update any internal links

### 4.3 Remove Duplicate Code

- [ ] Delete duplicate functions that were copied to reusable components:
  - Old candlestick builders → now in `valuation_charts.py`
  - Old table builders → now in `table_builders.py`
  - Old filter code → now in `valuation_filters.py`
- [ ] Remove unused imports
- [ ] Clean up any dead code paths

### 4.4 Update Import References

- [ ] Search for old imports and update:
  ```python
  # Before
  from WEBAPP.pages.valuation.valuation_dashboard import some_function

  # After
  from WEBAPP.components.charts.valuation_charts import some_function
  ```
- [ ] Check all files for broken imports
- [ ] Run import validation

### 4.5 Documentation Update

- [ ] Update README if it references old page structure
- [ ] Update any inline comments referencing old pages
- [ ] Add migration note in valuation_dashboard.py

---

## Navigation Structure (Target)

```
main_app.py
├── Sidebar Navigation
│   ├── 📊 Sector & Valuation  ← Combined page
│   ├── 📈 BSC Forecast        ← Isolated forward-looking
│   ├── 📰 News
│   └── 🔧 Settings
│
└── Page Routing
    ├── /sector → sector_dashboard.py
    ├── /forecast → forecast_dashboard.py
    ├── /valuation → REDIRECT to /sector (deprecated)
    └── /news → news_dashboard.py
```

---

## Verification Checklist

- [ ] valuation_dashboard.py shows redirect warning
- [ ] main_app.py navigation works correctly
- [ ] No broken imports in any file
- [ ] All duplicate code removed
- [ ] App runs without errors

---

## Code Templates

### valuation_dashboard.py (Deprecated)

```python
"""
Valuation Dashboard (DEPRECATED)
================================
This page has been merged into Sector & Valuation Dashboard.
All valuation functionality is now available at /sector.

Migration Date: 2025-12-21
Remove After: 2025-01-21 (1 month)
"""

import streamlit as st

def main():
    st.set_page_config(
        page_title="Valuation (Deprecated)",
        page_icon="⚠️",
        layout="wide"
    )

    st.warning(
        "⚠️ **This page is deprecated.** "
        "Valuation functionality has been merged into the Sector & Valuation Dashboard."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Sector & Valuation Dashboard →", type="primary"):
            st.switch_page("pages/sector/sector_dashboard.py")
    with col2:
        st.caption("The old URL /valuation will be removed in the next release.")

if __name__ == "__main__":
    main()
```

### main_app.py Navigation Update

```python
# Navigation configuration
PAGES = {
    "📊 Sector & Valuation": {
        "path": "pages/sector/sector_dashboard.py",
        "icon": "📊",
        "description": "Sector analysis, VNIndex valuation, historical distributions"
    },
    "📈 BSC Forecast": {
        "path": "pages/forecast/forecast_dashboard.py",
        "icon": "📈",
        "description": "Forward PE/PB, target prices, BSC recommendations"
    },
    # DEPRECATED - redirect only
    # "Valuation": "pages/valuation/valuation_dashboard.py",
}

def render_sidebar():
    st.sidebar.title("Vietnam Stock Dashboard")

    for page_name, page_info in PAGES.items():
        if st.sidebar.button(page_name, use_container_width=True):
            st.switch_page(page_info["path"])
```

### Import Cleanup Script

```bash
# Find files with old imports
grep -r "from WEBAPP.pages.valuation" WEBAPP/ --include="*.py"
grep -r "import valuation_dashboard" WEBAPP/ --include="*.py"

# Find duplicate function definitions
grep -r "def distribution_candlestick" WEBAPP/ --include="*.py"
grep -r "def valuation_box_with_markers" WEBAPP/ --include="*.py"
```

---

## Exit Criteria

1. valuation_dashboard.py shows deprecation warning and redirect
2. main_app.py navigation updated
3. Zero broken imports
4. All duplicate code removed
5. App runs without errors after changes
6. User can navigate to all pages via new structure
