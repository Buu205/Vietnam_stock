# Research: Financial Dashboard Filter & Layout Patterns
**Date:** 2025-12-21 | **Focus:** UI/UX optimization for Streamlit financial dashboards

---

## 1. Sidebar vs Horizontal Filters

### Sidebar Pattern (Recommended for Dashboards)
**Pros:**
- Fixed screen real estate for persistent controls
- Scales well with growing filter count (vertical scrolling hidden)
- Industry standard in Bloomberg, TradingView, Fin-tech platforms
- Mobile-responsive with collapsible toggle

**Cons:**
- Reduces chart viewport by 15-25% on desktop
- Hidden on mobile (requires toggle button)

### Horizontal Top Bar Pattern
**Pros:**
- Maximizes vertical chart space
- Better for mobile-first design
- Works with sticky header

**Cons:**
- Limited horizontal space (2-3 filters max without wrapping)
- Crowded on small screens
- Hard to scan vertically

**Recommendation:** Hybrid approach - collapsible sidebar (Bloomberg style) + sticky top bar for frequently-used filters.

---

## 2. Collapsible Sidebar (Bloomberg Terminal Style)

**Key Implementation Details:**
```
Pattern: Icon toggles sidebar state (chevron icon)
Width: 250px expanded → 50px collapsed
Animation: Smooth CSS transition (0.3s)
Icons: Show filter icons when collapsed, full labels when expanded
Content Hierarchy: Primary filters always visible, secondary in expandable sections
```

**Best Practices:**
- Show filter count badge: "Filters (3 active)"
- Preserve scroll position on toggle
- Persist state in browser localStorage
- Keyboard shortcut (Cmd/Ctrl + B) to toggle

---

## 3. Chart-First Layout Patterns

**Priority Hierarchy:**
1. Primary chart (60-70% viewport)
2. Filters (collapsible sidebar, 15%)
3. Data table/details (25%, scrollable)
4. Secondary charts (below main, lazy-load)

**Streamlit Implementation:**
```python
col1, col2 = st.columns([4, 1])  # 80/20 split
with col1:
    st.plotly_chart(main_chart, use_container_width=True)
with col2:
    st.button("⚙️ Filters")
    # Sidebar toggle implementation
```

**Responsiveness:**
- Desktop (>1200px): sidebar + chart + table (3-column)
- Tablet (768-1200px): top filters + full-width chart
- Mobile (<768px): collapsible filters, full-width chart

---

## 4. Filter Consolidation Best Practices

**Group Filters by Domain:**
```
├── Time Range (Date picker, Preset buttons)
├── Entity Filters (Ticker, Sector, Industry)
├── Metrics (Show/Hide, Threshold ranges)
└── Advanced (Custom formulas, Comparisons)
```

**Smart Defaults:**
- Load filters from URL params (`?sector=Banking&date=2025-12-21`)
- Auto-collapse advanced filters
- Show "Filters: X active" badge
- Reset button clears all selections

**Filter Count:**
- Max 5-7 primary filters visible
- Remaining in "More Filters" expandable
- Search box for >10 filters

---

## 5. Streamlit-Specific Optimizations

### Layout Containers
```python
# Use columns for side-by-side layout (more control than sidebar)
with st.sidebar:
    st.markdown("### Filters")
    sector = st.multiselect("Sector", options=sectors, key="sector_filter")
    ticker = st.text_input("Ticker", key="ticker_filter")

# OR use columns for modern 2-column layout:
filter_col, chart_col = st.columns([1, 4], gap="large")
with filter_col:
    # Filters here
with chart_col:
    # Charts here
```

### Performance Tips
- Use `st.session_state` to cache filter selections
- Lazy-load secondary charts with `@st.cache_data`
- Use `use_container_width=True` for responsive charts
- Implement filter debouncing (0.5s delay before rerender)

### Accessibility
- Use `key=` parameter consistently for reproducible state
- Add aria-labels: `st.markdown('<label for="sector_filter">Sector</label>', unsafe_allow_html=True)`
- Color contrast (WCAG AA minimum)
- Keyboard navigation: Tab through filters, Enter to apply

---

## 6. Recommendations for Vietnam Dashboard

**Immediate Changes:**
1. **Migrate to 2-column layout** (filters: 250px, charts: responsive)
2. **Group filters by domain** (time, entity, metrics)
3. **Add collapsible sections** for advanced filters
4. **Sticky header** with "Apply Filters" button
5. **Show filter count badge** in header

**Implementation Priority:**
- Phase 1: Sidebar layout with collapsible sections (Streamlit built-in)
- Phase 2: Responsive breakpoints (mobile/tablet)
- Phase 3: URL parameter persistence (shareable filter states)
- Phase 4: Dark mode toggle in header

---

## Unresolved Questions
- Should filters persist across page navigation? (Recommend: Yes, in URL)
- Mobile strategy: hamburger menu or bottom sheet? (Recommend: hamburger sidebar)
- Real-time filter updates vs "Apply" button? (Recommend: Real-time with 0.5s debounce)
