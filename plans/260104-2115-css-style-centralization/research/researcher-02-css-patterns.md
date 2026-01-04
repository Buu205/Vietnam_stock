# Research: CSS Variable Patterns for Streamlit

**Date:** 2026-01-04
**Scope:** CSS injection, variable usage, semantic naming, helper functions
**Sources:** Streamlit docs, community discussions, codebase analysis

---

## 1. CSS Injection Patterns in Streamlit

### Current Implementation (WEBAPP/core/styles.py)
Project uses direct `st.markdown()` with inline `<style>` block:
```python
def get_page_style() -> str:
    return """<style>
        :root { --purple-primary: #8B5CF6; ... }
        ...
    </style>"""

st.markdown(get_page_style(), unsafe_allow_html=True)
```

**Advantages:**
- Single call injects all CSS at once
- CSS variables defined in `:root` scope globally available
- No external file dependencies
- Streamlit caches markdown → efficient reuse

**Best Practice Verified:**
✅ Return CSS string from function (matches Streamlit documentation)
✅ Use `unsafe_allow_html=True` for `<style>` blocks
✅ Define variables in `:root` for app-wide scope

---

## 2. CSS Variables in Python HTML Strings

### Pattern: Variable Reference in f-strings
```python
# ✅ CORRECT: Reference CSS variables directly
def render_metric_card(label: str, value: str) -> str:
    return f'''
    <div class="metric-card">
        <span class="metric-label">{label}</span>
        <span class="metric-value">{value}</span>
    </div>
    '''

# CSS handles styling via variables
# .metric-card { background: var(--glass-bg); }
```

### Pattern: Python Constants + CSS Variables
```python
# Python constants for dynamic values
METRIC_COLORS = {
    'positive': '#10B981',
    'negative': '#EF4444'
}

# CSS variables for theme consistency
# CSS: --positive: #10B981; --negative: #EF4444;

def render_status(value: float) -> str:
    status_class = "positive" if value > 0 else "negative"
    return f'<span class="{status_class}-badge">{value}</span>'
```

**Key Insight:**
- Python constants for **dynamic/computational values** (colors based on conditions)
- CSS variables for **static/theme values** (brand colors, spacing)
- f-strings reference CSS classes, not CSS variable values directly

---

## 3. Semantic CSS Class Naming

### Naming Convention: Purpose-Based
```css
/* ✅ GOOD: Semantic, intent-clear */
.metric-positive { color: var(--positive); }
.header-gradient { background: linear-gradient(...); }
.filter-bar-container { position: sticky; ... }
.badge-critical { background: var(--negative); }

/* ❌ BAD: Non-semantic, implementation-detail focused */
.red-text { color: red; }
.float-left { float: left; }
.margin-10 { margin: 10px; }
```

### Organization Pattern (from codebase)
```css
/* Section headers with borders and underlines */
h3 {
    border-bottom: 1px solid var(--glass-border);
    position: relative;
}

h3::after {  /* Pseudo-element for accent bar */
    content: '';
    background: linear-gradient(...);
}

/* Metric card styling with glassmorphism */
.metric-card {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
}

.metric-card:hover {
    border-color: var(--glass-border-hover);
    transform: translateY(-4px);
}

/* Status indicators with color coding */
.status-badge { display: inline-flex; }
.status-positive { color: var(--positive); }
.status-negative { color: var(--negative); }
```

---

## 4. Helper Function Patterns

### Pattern 1: Styled HTML Generator
```python
def render_styled_badge(text: str, status: str) -> str:
    """Generate status badge with semantic class."""
    return f'<span class="status-badge status-{status}">{text}</span>'

# Usage
st.markdown(
    render_styled_badge("Active", "positive"),
    unsafe_allow_html=True
)
```

### Pattern 2: Container with CSS Variables
```python
def render_metric_container(metrics_dict: dict) -> str:
    """Generate metric grid using CSS variables for spacing/colors."""
    html = '<div class="metrics-grid">'
    for label, value in metrics_dict.items():
        # Classes define styling via CSS variables
        html += f'<div class="metric-item"><span class="label">{label}</span>'
        html += f'<span class="value">{value}</span></div>'
    html += '</div>'
    return html

# CSS handles responsive grid via variables
# .metrics-grid { display: grid; gap: var(--spacing-md); }
```

### Pattern 3: Conditional Styling Class Selection
```python
def get_valuation_class(z_score: float) -> str:
    """Return CSS class based on valuation metric."""
    if z_score < -1:
        return "valuation-very-cheap"
    elif z_score < 0:
        return "valuation-cheap"
    elif z_score < 1:
        return "valuation-fair"
    else:
        return "valuation-expensive"

def render_valuation_badge(z_score: float) -> str:
    css_class = get_valuation_class(z_score)
    return f'<span class="valuation-badge {css_class}">Value</span>'
```

---

## 5. Codebase Validation

### Verified Patterns (WEBAPP/core/styles.py)

✅ **CSS Variables in :root**
- 40+ semantic variables defined: `--purple-primary`, `--glass-bg`, `--text-primary`
- Glassmorphism variables: `--glass-blur`, `--glass-shadow`
- Semantic colors: `--positive`, `--negative`, `--warning`

✅ **Helper Functions**
- `get_page_style()` - Returns CSS string
- `render_styled_table()` - Generates HTML with semantic classes
- `render_valuation_legend()` - Renders colored badges
- `render_skeleton_card()` - Generates placeholder HTML

✅ **Semantic Classes**
- `.metric-card` (glassmorphic metrics)
- `.filter-bar-container` (sticky filter bar)
- `.status-badge` (colored indicators)
- `.skeleton-loader` (loading placeholders)

✅ **Python Color Constants**
- `CHART_COLORS` dict for chart palette
- `TRADING_CHART_COLORS` for bullish/bearish
- `ASSESSMENT_COLORS` for valuation

---

## 6. Key Best Practices Summary

| Pattern | Use Case | Example |
|---------|----------|---------|
| **CSS Variables** | Static theme values | `--purple-primary`, `--glass-blur` |
| **Python Constants** | Dynamic computations | `CHART_COLORS['positive']` |
| **Semantic Classes** | Intent-based styling | `.metric-positive`, `.filter-bar` |
| **f-strings** | Dynamic HTML generation | `f'<span class="{status}">{value}</span>'` |
| **Helper Functions** | Reusable HTML components | `render_styled_badge()` |
| **Pseudo-elements** | Accent decorations | `::before`, `::after` for gradients |

---

## 7. Implementation Checklist

- [x] Define all theme colors in CSS `:root`
- [x] Use `var(--name)` throughout CSS selectors
- [x] Create semantic class names (purpose-first)
- [x] Organize CSS by section with clear comments
- [x] Build HTML-generating helper functions
- [x] Use Python constants for computed/conditional values
- [x] Leverage pseudo-elements for decorative effects
- [x] Test CSS variable fallbacks for browser compatibility

---

## Unresolved Questions

None identified. Patterns are well-established and verified against Streamlit documentation and production codebase.
