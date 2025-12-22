# Phase 4: UI/UX Polish

**Priority:** Low
**Effort:** 2 hours
**Risk:** Low

---

## Context

Research confirms glassmorphism design tokens exist in codebase (`styles.py`, lines 49-115).
Apply consistent styling across FX & Commodities dashboard to match rest of app.

## Overview

Polish pass to ensure:
1. Glassmorphism card styling on metric displays
2. JetBrains Mono font for numeric values
3. Purple/cyan color scheme consistency
4. Responsive chart sizing
5. Consistent spacing and padding

## Requirements

1. Apply existing glass styling from `styles.py`
2. Use design system colors (no hardcoded hex)
3. Ensure charts are full-width responsive
4. Consistent metric card styling
5. Match rest of dashboard aesthetic

## Related Code Files

### `styles.py` (lines 49-115) - Design Tokens
```css
--purple-primary: #8B5CF6;
--cyan-primary: #06B6D4;
--glass-bg: rgba(255, 255, 255, 0.03);
--glass-border: rgba(255, 255, 255, 0.08);
--font-mono: 'JetBrains Mono', monospace;
```

### `styles.py` (lines 1248-1261) - CHART_COLORS
```python
CHART_COLORS = {
    'primary': '#8B5CF6',
    'secondary': '#06B6D4',
    'tertiary': '#F59E0B',
    'positive': '#10B981',
    'negative': '#EF4444',
}
```

### `fx_commodities_dashboard.py` - Current styling
Mixed inline colors, some hardcoded, some from CHART_COLORS.

## Implementation Steps

### Step 1: Import Design Constants (MODIFY line ~12)
Ensure all design constants are imported:

```python
from WEBAPP.core.styles import (
    get_page_style,
    get_chart_layout,
    CHART_COLORS,
    render_styled_table,
    get_table_style,
    BAR_COLORS,
    CHART_TEXT_COLORS
)
```

### Step 2: Replace Hardcoded Colors (MODIFY throughout)
Search and replace hardcoded hex values:

| Before | After |
|--------|-------|
| `'#00FF88'` | `CHART_COLORS['positive']` |
| `'#FF6B6B'` | `CHART_COLORS['negative']` |
| `'#8B5CF6'` | `CHART_COLORS['primary']` |
| `'#06B6D4'` | `CHART_COLORS['secondary']` |
| `'#F59E0B'` | `CHART_COLORS['tertiary']` |

Example fixes:
```python
# Line 146 - Exchange rate chart
# Before
line=dict(color='#00FF88', width=2.5)
# After
line=dict(color=CHART_COLORS['primary'], width=2.5)

# Line 239 - Fill color
# Before
fillcolor='rgba(0, 255, 136, 0.1)'
# After
fillcolor='rgba(139, 92, 246, 0.1)'  # Purple at 10% opacity
```

### Step 3: Create Reusable Fill Colors (ADD after imports)
Add fill color helpers:

```python
# Fill colors for area charts (10% opacity versions)
FILL_COLORS = {
    'primary': 'rgba(139, 92, 246, 0.1)',   # Purple
    'secondary': 'rgba(6, 182, 212, 0.1)',   # Cyan
    'tertiary': 'rgba(245, 158, 11, 0.1)',   # Amber
    'positive': 'rgba(16, 185, 129, 0.1)',   # Green
    'negative': 'rgba(239, 68, 68, 0.1)',    # Red
}
```

### Step 4: Standardize Chart Layout (MODIFY chart creation)
Ensure all charts use `get_chart_layout()`:

```python
# Before - inconsistent layout
fig.update_layout(
    height=500,
    paper_bgcolor='rgba(0,0,0,0)',
    ...
)

# After - use helper
layout = get_chart_layout(height=500)
layout['showlegend'] = True
layout['legend'] = dict(
    orientation='h',
    yanchor='bottom',
    y=1.02,
    xanchor='center',
    x=0.5,
    font=dict(size=11, color='#FFFFFF')
)
fig.update_layout(**layout)
```

### Step 5: Metric Card Enhancement (MODIFY metric displays)
Replace st.metric with styled version where possible:

```python
# Current - plain st.metric
col1.metric("USD Trung tâm", f"{latest1:,.0f} VND")

# Enhanced - with delta styling
col1.metric(
    label="USD Trung tâm",
    value=f"{latest1:,.0f} VND",
    delta=f"{change_pct:+.2f}%" if change_pct else None,
    delta_color="normal"  # Uses green/red automatically
)
```

### Step 6: Responsive Chart Container (ADD CSS)
Add responsive wrapper class:

```python
# Add after page style injection
st.markdown("""
<style>
.fx-chart-container {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
}

/* Ensure Plotly charts are full width */
.stPlotlyChart > div > div {
    width: 100% !important;
}

/* Chart spacing */
.stPlotlyChart {
    margin-bottom: 0.5rem !important;
}

/* Performance table spacing */
.perf-table-container {
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)
```

### Step 7: Consistent Section Headers (MODIFY h3 usage)
Use consistent markdown styling:

```python
# Before - plain markdown
st.markdown("### Latest Values")

# After - with consistent styling (uses CSS from styles.py)
st.markdown("### Latest Values")  # CSS already handles h3 styling
```

### Step 8: Loading States (ADD)
Add loading indicators:

```python
with st.spinner('Loading macro data...'):
    macro_df = macro_loader.get_macro()

if macro_df.empty:
    st.warning("No macro data available. Please run the daily update pipeline.")
    st.stop()
```

### Step 9: Add Live Indicator (OPTIONAL)
Use codebase's live indicator class:

```python
# After page title
st.markdown('<span class="live-indicator">LIVE</span>', unsafe_allow_html=True)
```

### Step 10: Footer Consistency (MODIFY line 560)
Update footer to match codebase pattern:

```python
# Before
st.caption(f"Data: Macro & Commodities | Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")

# After - with icon and consistent format
st.markdown("---")
st.caption(f"📊 Data: Macro & Commodities | 🕐 Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
```

## Color Reference Card

For quick reference during implementation:

| Use Case | Variable | Hex |
|----------|----------|-----|
| Primary charts | `CHART_COLORS['primary']` | #8B5CF6 |
| Secondary lines | `CHART_COLORS['secondary']` | #06B6D4 |
| Tertiary/accent | `CHART_COLORS['tertiary']` | #F59E0B |
| Gains/bullish | `CHART_COLORS['positive']` | #10B981 |
| Losses/bearish | `CHART_COLORS['negative']` | #EF4444 |
| Neutral text | `#94A3B8` | Gray |
| Primary text | `#E2E8F0` | Light gray |
| Bright text | `#FFFFFF` | White |

## Success Criteria

1. [ ] No hardcoded hex colors (all use CHART_COLORS)
2. [ ] JetBrains Mono font on all numeric values
3. [ ] Charts are full-width on all screen sizes
4. [ ] Metric cards have glass effect on hover
5. [ ] Consistent 1rem spacing between sections
6. [ ] Footer matches other dashboard pages

## Testing Steps

1. Run dashboard and visually compare to Valuation dashboard
2. Hover over metric cards - verify glass effect
3. Resize browser - verify charts resize properly
4. Check fonts in browser inspector - numeric values in JetBrains Mono
5. Compare color scheme with design tokens

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| CSS conflicts | Low | Low | Use scoped class names |
| Font loading slow | Low | Low | Font already in global styles |
| Mobile layout issues | Medium | Low | Test on mobile viewport |

## Dependencies

- Phases 1-3 complete
- `styles.py` already loaded in dashboard

## File Changes Summary

| File | Change Type | Scope |
|------|-------------|-------|
| `fx_commodities_dashboard.py` | Modify | Replace hardcoded colors, add CSS |

No new files created in this phase.
