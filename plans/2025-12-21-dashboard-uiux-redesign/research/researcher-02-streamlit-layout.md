# Streamlit Layout Optimization Research
**Date:** 2025-12-21
**Topic:** Maximize content area, minimize sidebar footprint
**Status:** 5 techniques evaluated

---

## 1. CSS: Hide/Shrink Sidebar

**Current Implementation:** Your app uses `initial_sidebar_state="expanded"` in `config.toml`.

### Technique A: Compact Sidebar CSS
```css
/* Reduce sidebar width from default ~300px to ~220px */
[data-testid="stSidebar"] {
    width: 220px !important;
}

/* Reduce padding inside sidebar */
[data-testid="stSidebar"] > div {
    padding: 0.75rem 0.5rem !important;
}

/* Shrink navigation item padding */
[data-testid="stSidebarNavLink"] {
    padding: 0.35rem 0.5rem !important;
    min-height: 32px !important;
}

/* Compact input fields */
[data-testid="stSidebar"] .stSelectbox,
[data-testid="stSidebar"] .stTextInput {
    font-size: 12px !important;
    margin-bottom: 0.5rem !important;
}
```

### Technique B: Hide Sidebar Completely (Collapsible)
```python
# main_app.py - Set initial state
st.set_page_config(
    page_title="VN Finance Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"  # ← Change from "expanded"
)

# Users can toggle with hamburger icon (default Streamlit button)
```

### Technique C: Custom Hide Button + Session State
```python
import streamlit as st

# Add toggle button in header
col1, col2 = st.columns([0.95, 0.05])
with col2:
    if st.button("≡", key="sidebar_toggle", help="Toggle sidebar"):
        st.session_state.sidebar_hidden = not st.session_state.sidebar_hidden

# CSS to hide sidebar
if st.session_state.get("sidebar_hidden", False):
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="stMain"] > div:first-child { margin-left: 0 !important; }
        </style>
    """, unsafe_allow_html=True)
```

---

## 2. st.sidebar Alternatives

### Alternative 1: Floating Horizontal Filter Bar (Top)
```python
# Instead of sidebar, use columns across top
st.markdown("### 🔍 Quick Filters")
col1, col2, col3, col4 = st.columns(4)

with col1:
    ticker = st.selectbox("Ticker", options=["ACB", "VNM", "FPT"])
with col2:
    metric = st.selectbox("Metric", options=["PE", "PB", "ROE"])
with col3:
    period = st.selectbox("Period", options=["Monthly", "Quarterly", "Yearly"])
with col4:
    if st.button("📊 Analyze"):
        st.session_state.filter_applied = True
```

**Pros:** Eliminates sidebar entirely, increases main content width by 300px+
**Cons:** Reduces vertical space for filters

### Alternative 2: Expanders for Filter Groups
```python
with st.expander("📊 Data Filters", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.multiselect("Tickers", ["ACB", "VNM", "FPT"])
    with col2:
        pe_range = st.slider("PE Ratio Range", 5, 25)

with st.expander("⚙️ Display Options", expanded=False):
    show_chart = st.checkbox("Show Charts")
    show_table = st.checkbox("Show Table")
```

**Pros:** Collapsible, saves space, scannable
**Cons:** 2-click access to filters (expander + interaction)

### Alternative 3: Tabs as Filter Containers
```python
tab1, tab2, tab3 = st.tabs(["Company Data", "Technical", "Valuation"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.selectbox("Company", ["ACB", "VNM"])
    # Company-specific content

with tab2:
    period = st.selectbox("Time Period", ["5D", "1M", "3M"])
    # Technical analysis content

with tab3:
    metric = st.selectbox("Valuation Metric", ["PE", "PB"])
    # Valuation content
```

**Pros:** Content + filters integrated, cleaner UX
**Cons:** Reduces filter visibility

---

## 3. Configuration: initial_sidebar_state Behavior

```toml
# .streamlit/config.toml

[client]
# "expanded" = sidebar open on load (current)
# "collapsed" = sidebar closed on load
# "hidden" = NO HAMBURGER BUTTON (use if fully removing sidebar)
toolbarMode = "minimal"
showSidebarNavigation = true
```

**Current State Analysis:**
- Your app: `initial_sidebar_state="expanded"` (line 37 main_app.py)
- Users see 7 pages + quick ticker search
- Sidebar occupies ~300px, leaving ~1500px for content (wide layout)
- Chart containers are constrained to 100% of remaining width

**Recommendation:** Change to `collapsed` + use floating top filter bar

---

## 4. Custom CSS for Compact Layout

### Complete Sidebar Minimization Package
```css
/* CSS injection - add to get_page_style() */

/* Sidebar width reduction */
[data-testid="stSidebar"] {
    width: 200px !important;
    min-width: 200px !important;
}

/* Remove sidebar background padding */
[data-testid="stSidebar"] > section:first-child {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

/* Navigation: single-line items, smaller icons */
[data-testid="stSidebarNavLink"] {
    font-size: 12px !important;
    padding: 0.25rem 0.5rem !important;
    margin-bottom: 2px !important;
}

[data-testid="stSidebarNavLink"] svg {
    width: 14px !important;
    height: 14px !important;
    margin-right: 6px !important;
}

/* Hide sidebar on mobile */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stMainBlockContainer"] { margin-left: 0 !important; }
}

/* Sticky header filters */
.filter-header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: linear-gradient(170deg, #0F0B1E 0%, #1A1625 50%);
    padding: 1rem;
    border-bottom: 1px solid rgba(139, 92, 246, 0.2);
    backdrop-filter: blur(12px);
}
```

---

## 5. Session State for Sidebar Toggle

```python
# main_app.py - Add to page config section

st.set_page_config(
    page_title="VN Finance Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"  # ← Collapsed by default
)

# Initialize session state
if "sidebar_expanded" not in st.session_state:
    st.session_state.sidebar_expanded = False

# Floating toggle button (CSS positioned)
st.markdown("""
    <style>
        .sidebar-toggle-btn {
            position: fixed;
            top: 0.5rem;
            right: 0.5rem;
            z-index: 1000;
            background: linear-gradient(135deg, #8B5CF6, #06B6D4);
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            font-size: 18px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
        }
        .sidebar-toggle-btn:hover {
            box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
        }
    </style>
""", unsafe_allow_html=True)

# Toggle logic with session state
col1, col2, col3 = st.columns([0.9, 0.05, 0.05])
with col3:
    if st.button("☰", help="Toggle Sidebar", key="sidebar_btn"):
        st.session_state.sidebar_expanded = not st.session_state.sidebar_expanded
        st.rerun()
```

---

## 6. Implementation Strategy (Your Dashboard)

### Current Situation
- Wide layout: 1800px max-width (line 132 styles.py)
- Sidebar: ~300px (default Streamlit)
- Content area: ~1500px remaining
- 7 navigation pages actively used

### Recommended Approach
**Option A (Minimal Code, Maximum Impact):**
1. Change `initial_sidebar_state="collapsed"` in main_app.py
2. Add sticky horizontal filter bar at top (columns-based)
3. Users click hamburger icon if needed

**Option B (Full Optimization):**
1. Collapse sidebar by default
2. Move ticker search to top sticky bar
3. Use expanders for advanced filters
4. Add custom toggle button for sidebar

### Code Example (Option A)
```python
# main_app.py line 33-38
st.set_page_config(
    page_title="VN Finance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # ← Change from expanded
)

# After style injection (line 43), add top filter bar
st.markdown("### 🔍 Dashboard Filters")
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

with col1:
    selected_ticker = st.selectbox(
        "Select Ticker",
        options=list_available_tickers(),
        key="main_ticker_search"
    )
# ... more filters in col2-col5
```

---

## Key Metrics (Your Dashboard)

| Metric | Current | Optimized (Collapsed) |
|--------|---------|----------------------|
| Content Width | ~1500px | ~1800px (+300px) |
| Initial Load | Sidebar visible | Sidebar hidden |
| User Clicks to Filters | 0 (always visible) | 1 (open hamburger) |
| Mobile Experience | Sidebar visible | Sidebar auto-hidden |

---

## Unresolved Questions

1. **Data load strategy:** Should top filter bar trigger data refresh automatically or require "Apply" button?
2. **Filter persistence:** Should user's last filter choices persist in session state across page navigation?
3. **Mobile sidebar:** On mobile, should sidebar be completely hidden or use bottom navigation?
4. **Performance:** Are any current sidebar selectbox queries slow (loading 450+ tickers)?
