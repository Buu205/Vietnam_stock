# UI/UX Errors & Lessons Learned

**Date:** 2025-12-27
**Dashboard:** Technical Dashboard - Stock Scanner Tab

---

## Critical Errors Encountered

### 1. SVG Icons in st.markdown() - ESCAPE ISSUE

**Problem:** SVG icons embedded in HTML strings passed to `st.markdown(html, unsafe_allow_html=True)` get escaped and display as raw text.

```python
# ❌ WRONG - SVG will be escaped
icon = '<svg width="16" height="16" viewBox="0 0 24 24">...</svg>'
st.markdown(f'<div>{icon}</div>', unsafe_allow_html=True)
```

**Solution:** Use emoji or CSS/Unicode symbols instead of inline SVG.

```python
# ✅ CORRECT - Use emoji
SIGNAL_TYPE_EMOJI = {
    'ma_crossover': '📈',
    'volume_spike': '📊',
    'breakout': '🚀',
    'patterns': '🕯️',
}
```

---

### 2. st.dataframe() with Dark Theme CSS - INVISIBLE TEXT

**Problem:** Streamlit's `st.dataframe()` uses Arrow DataGrid (canvas-based rendering). Custom CSS selectors like `.stDataFrame [class*="cell"]` do NOT work because content is rendered on canvas, not as HTML elements.

```python
# ❌ WRONG - Text becomes invisible on dark theme
st.dataframe(df, use_container_width=True)
```

**Solution:** Use `render_styled_table()` from `WEBAPP/core/styles.py` which creates HTML tables with proper dark theme styling.

```python
# ✅ CORRECT - Use custom HTML table
from WEBAPP.core.styles import render_styled_table

html_table = render_styled_table(df, highlight_first_col=True)
st.markdown(html_table, unsafe_allow_html=True)
```

---

### 3. Complex Nested HTML - TRUNCATION/ESCAPE

**Problem:** Very long or complex HTML strings with many inline styles can get truncated or partially escaped by Streamlit.

```python
# ❌ RISKY - Complex nested HTML
html = '''
<div style="background: rgba(0,0,0,0.3); ...">
    <div style="display: flex; ...">
        <span style="color: #8B5CF6;">
            <svg width="16" ...>...</svg>  # SVG nested = FAIL
        </span>
    </div>
</div>
'''
```

**Solution:**
1. Keep HTML simple and flat
2. Use Streamlit native components (`st.columns()`, `st.metric()`) where possible
3. For tables, use `render_styled_table()`
4. For cards/badges, use simple spans without nested complex structures

```python
# ✅ CORRECT - Use native Streamlit components
cols = st.columns(4)
for i, (label, count) in enumerate(data.items()):
    with cols[i]:
        st.metric(label=label, value=count)
```

---

### 4. rgba() Colors in HTML - SAFE

**Note:** `rgba()` colors work fine in inline HTML styles. The issue was NOT with rgba().

```python
# ✅ WORKS - rgba colors are OK
html = '<span style="background: rgba(16,185,129,0.2); color: #10B981;">BUY</span>'
```

---

## Best Practices for Streamlit Dark Theme

### DO:
- Use `render_styled_table()` for data tables
- Use `st.columns()` for layouts
- Use `st.metric()` for KPI cards (same as Company/Sector dashboards)
- Keep HTML simple and avoid deep nesting
- Use HTML color badges for status: `<span style="background:rgba(16,185,129,0.15); color:#10B981;">BUY</span>`
- Test both light and dark themes
- Follow existing dashboard conventions (Company, Sector, Bank dashboards)

### DON'T:
- Use inline SVG in st.markdown() (gets escaped)
- Use st.dataframe() if custom dark theme CSS is applied (text invisible)
- Create overly complex nested HTML structures
- Assume CSS selectors will work on Streamlit's internal components
- **Use emoji in UI elements** - Use HTML color badges instead for professional look

---

## File References

- **Styled Table Function:** `WEBAPP/core/styles.py:render_styled_table()`
- **Table CSS:** `WEBAPP/core/styles.py:get_table_style()`
- **Theme Colors:** `WEBAPP/core/theme.py`
- **Stock Scanner:** `WEBAPP/pages/technical/components/stock_scanner.py`

---

## Color Palette (Dark Theme - OLED)

| Purpose | Color | Hex |
|---------|-------|-----|
| Background Deep | Dark Purple-Black | #0F0B1E |
| Background Surface | Dark Purple | #1A1625 |
| Text Primary | Light Gray | #E2E8F0 |
| Text Secondary | Gray | #94A3B8 |
| Accent Purple | Electric Purple | #8B5CF6 |
| Accent Cyan | Cyan | #06B6D4 |
| Positive/BUY | Green | #10B981 |
| Negative/SELL | Red | #EF4444 |
| Warning/HOLD | Amber | #F59E0B |
| Neutral | Gray | #64748B |

---

## Additional UI Components Implemented

### Progress Bar Gauge (Score Display)

For showing strength/score as visual gauge like `████████░░ 85`:

```python
def _render_progress_bar_html(value: float, max_value: float = 100) -> str:
    pct = min(100, max(0, (value / max_value) * 100))

    # Color coding
    if pct >= 70:
        color = '#10B981'  # Green
    elif pct >= 50:
        color = '#06B6D4'  # Cyan
    elif pct >= 30:
        color = '#F59E0B'  # Amber
    else:
        color = '#64748B'  # Gray

    filled = int(pct / 10)
    empty = 10 - filled

    return f'<span style="color:{color};">{"█" * filled}</span><span style="color:#374151;">{"░" * empty}</span> <span style="color:#E2E8F0;">{int(pct)}</span>'
```

### Pattern Interpretation (Vietnamese)

Store interpretations in dictionary for quick lookup:

```python
PATTERN_INTERPRETATIONS = {
    'Morning Star': 'Mo hinh 3 nen dao chieu hoan hao, high conviction.',
    'Hammer': 'Tu choi giam gia, bac duoi dai.',
    'Engulfing': 'Dao chieu manh, buyers ap dao.',
    # ... more patterns
}
```

### Custom HTML Table (vs st.dataframe)

For dark theme compatibility, use custom HTML tables:

```python
table_html = '''
<style>
.styled-table { width: 100%; border-collapse: collapse; }
.styled-table th { background: rgba(139, 92, 246, 0.2); color: #8B5CF6; }
.styled-table td { padding: 10px; border-bottom: 1px solid rgba(100, 116, 139, 0.2); }
.styled-table tr:hover { background: rgba(139, 92, 246, 0.1); }
</style>
<table class="styled-table">...</table>
'''
st.markdown(table_html, unsafe_allow_html=True)
```

---

## Final Working Solution: st.html() (Streamlit v1.33+)

### The Fix That Works

After testing multiple approaches, **`st.html()`** (added in Streamlit v1.33) is the reliable solution for rendering complex HTML tables with custom styling.

```python
# ✅ WORKING - Use st.html() for complex HTML
table_style = '''
<style>
.scanner-table-wrapper {
    background: linear-gradient(180deg, #0F0B1E 0%, #0A0816 100%);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 32px rgba(0, 0, 0, 0.5);
}
.styled-table th { ... }
.styled-table td { ... }
</style>
'''

table_html = '''
<div class="scanner-table-wrapper">
<table class="styled-table">...</table>
</div>
'''

# Use st.html() to render (Streamlit v1.33+)
st.html(table_style + table_html)
```

### Why This Works

1. `st.html()` renders raw HTML without escaping
2. `st.markdown(unsafe_allow_html=True)` can still escape complex HTML structures
3. `st.dataframe()` uses canvas rendering - CSS doesn't work

### UI/UX Patterns Applied (Financial Dashboard + Dark Mode OLED)

- **Colors:** Green #10B981/#22C55E (BUY), Red #EF4444 (SELL), Purple #8B5CF6 (accent)
- **Shadows:** Multi-layer box-shadow for depth
- **Borders:** Subtle rgba borders with glow effect
- **Typography:** System fonts for body, monospace for symbols
- **Hover:** Subtle scale transform + background change
- **Badges:** Gradient background + matching border + glow

---

*Last Updated: 2025-12-27*
