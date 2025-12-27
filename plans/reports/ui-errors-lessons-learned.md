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
- Use emoji for icons (📈 📊 🚀 🕯️ 🟢 🔴 ⚪)
- Use `st.columns()` for layouts
- Use `st.metric()` for KPI cards
- Keep HTML simple and avoid deep nesting
- Test both light and dark themes

### DON'T:
- Use inline SVG in st.markdown()
- Use st.dataframe() if custom dark theme CSS is applied
- Create overly complex nested HTML structures
- Assume CSS selectors will work on Streamlit's internal components

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

*Last Updated: 2025-12-27*
