# Phase 1: Sidebar Collapse

**Goal:** Collapse sidebar by default, gain ~300px chart width
**Effort:** 1 day | **Risk:** Low

---

## Changes

### 1. main_app.py - Collapse Sidebar Default

**File:** `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/main_app.py`
**Line:** 37

```python
# BEFORE (line 33-38)
st.set_page_config(
    page_title="VN Finance Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"  # <-- CHANGE THIS
)

# AFTER
st.set_page_config(
    page_title="VN Finance Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"  # <-- COLLAPSED
)
```

### 2. styles.py - Compact Sidebar CSS

**File:** `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/core/styles.py`
**Location:** Add after line 316 (SIDEBAR section)

```css
/* ============================================================
   SIDEBAR - COMPACT COLLAPSED MODE
   ============================================================ */

/* Reduce sidebar width when expanded (from 300px to 220px) */
[data-testid="stSidebar"][aria-expanded="true"] {
    width: 220px !important;
    min-width: 220px !important;
}

/* Tighter padding in sidebar */
[data-testid="stSidebar"] > div:first-child {
    padding: 0.5rem 0.75rem !important;
}

/* Compact navigation links */
[data-testid="stSidebarNavLink"] {
    padding: 0.35rem 0.6rem !important;
    min-height: 34px !important;
    font-size: 12px !important;
}

/* Smaller nav icons */
[data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"] {
    width: 14px !important;
    height: 14px !important;
    margin-right: 6px !important;
}

/* Compact sidebar inputs */
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stTextInput > div > div {
    font-size: 12px !important;
    min-height: 34px !important;
    padding: 0.4rem 0.6rem !important;
}

/* Hide sidebar on mobile */
@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="stMainBlockContainer"] {
        margin-left: 0 !important;
    }
}
```

---

## Implementation Steps

1. **Edit main_app.py**
   ```bash
   # Line 37: Change "expanded" to "collapsed"
   ```

2. **Edit styles.py**
   - Add compact sidebar CSS after existing SIDEBAR section (line 316)
   - No changes to theme colors

3. **Test**
   - `streamlit run WEBAPP/main_app.py`
   - Verify: sidebar is collapsed on load
   - Verify: hamburger icon opens sidebar
   - Verify: navigation pages still work
   - Verify: Quick Search in sidebar still functional

---

## Validation Checklist
- [ ] Sidebar collapsed on initial load
- [ ] Hamburger icon visible in top-left
- [ ] Clicking hamburger expands sidebar
- [ ] Navigation links work (Company, Bank, Sector, etc.)
- [ ] Quick ticker search works in sidebar
- [ ] Charts use full width (~1800px)
- [ ] No CSS conflicts with existing styles

---

## Rollback
If issues occur, revert line 37:
```python
initial_sidebar_state="expanded"
```
