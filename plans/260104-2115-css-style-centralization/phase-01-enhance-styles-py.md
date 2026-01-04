# Phase 1: Enhance WEBAPP/core/styles.py

## Context

- [Main Plan](./plan.md)
- [Style Audit](./research/researcher-01-style-audit.md)
- [CSS Patterns](./research/researcher-02-css-patterns.md)

## Overview

Add semantic CSS classes and Python helper functions to `styles.py` to support centralized styling.
This phase creates the foundation for refactoring inline styles in subsequent phases.

## Key Insights

1. **5 common patterns** cover ~480 of 700+ color occurrences
2. **CSS classes** must use existing CSS variables (already defined in `:root`)
3. **Helper functions** should return HTML strings with class references, not inline styles
4. **Backward compatible** - existing functions unchanged

## Requirements

1. Add 15+ semantic CSS classes to `get_page_style()`
2. Add 6 helper functions for styled HTML generation
3. Classes must reference existing CSS variables
4. No breaking changes to existing API

## Architecture

```
styles.py (enhanced)
├── get_page_style() - Add new CSS classes section
├── render_styled_text() - NEW: Text with semantic class
├── render_styled_badge() - NEW: Status badges
├── render_styled_metric_inline() - NEW: Inline metric display
├── render_styled_status() - NEW: Positive/negative indicators
├── render_styled_label() - NEW: Uppercase labels
└── get_status_class() - NEW: Returns CSS class name based on value
```

## Related Code Files

- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/core/styles.py` - Target file
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/core/theme.py` - Color constants reference

## Implementation Steps

### Step 1: Add CSS Classes to `get_page_style()`

Insert after line ~1242 (before closing `</style>`):

```css
/* ============================================================
   SEMANTIC TEXT CLASSES
   ============================================================ */
.text-primary-emphasis {
    color: var(--purple-primary);
    font-weight: 600;
}

.text-secondary-emphasis {
    color: var(--cyan-primary);
    font-weight: 600;
}

.text-accent-emphasis {
    color: var(--amber-primary);
    font-weight: 600;
}

.text-muted {
    color: var(--text-muted);
}

.text-secondary-sm {
    color: var(--text-secondary);
    font-size: 0.7rem;
}

/* ============================================================
   STATUS INDICATORS
   ============================================================ */
.status-positive {
    color: var(--positive);
    font-weight: 600;
}

.status-negative {
    color: var(--negative);
    font-weight: 600;
}

.status-neutral {
    color: var(--text-secondary);
}

.status-warning {
    color: var(--warning);
    font-weight: 600;
}

/* ============================================================
   BADGE STYLES
   ============================================================ */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    font-family: var(--font-body);
}

.badge-primary {
    background: rgba(139, 92, 246, 0.2);
    color: var(--purple-light);
    border: 1px solid rgba(139, 92, 246, 0.3);
}

.badge-success {
    background: rgba(16, 185, 129, 0.2);
    color: var(--positive-light);
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-danger {
    background: rgba(239, 68, 68, 0.2);
    color: var(--negative-light);
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-warning {
    background: rgba(245, 158, 11, 0.2);
    color: var(--amber-light);
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-info {
    background: rgba(6, 182, 212, 0.2);
    color: var(--cyan-light);
    border: 1px solid rgba(6, 182, 212, 0.3);
}

/* ============================================================
   METRIC DISPLAY CLASSES
   ============================================================ */
.metric-label {
    color: var(--text-secondary);
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.metric-value {
    color: var(--text-white);
    font-size: 1.4rem;
    font-weight: 700;
    font-family: var(--font-mono);
}

.metric-value-sm {
    color: var(--text-white);
    font-size: 1.1rem;
    font-weight: 700;
    font-family: var(--font-mono);
}

.metric-value-xs {
    color: var(--text-primary);
    font-size: 0.75rem;
    font-family: var(--font-mono);
}

.metric-delta-positive {
    color: var(--positive);
    font-size: 0.85rem;
    font-weight: 600;
}

.metric-delta-negative {
    color: var(--negative);
    font-size: 0.85rem;
    font-weight: 600;
}

/* ============================================================
   LEGEND & INDICATOR CLASSES
   ============================================================ */
.legend-line-primary { color: var(--purple-primary); font-weight: 600; }
.legend-line-secondary { color: var(--cyan-primary); font-weight: 600; }
.legend-line-accent { color: var(--amber-primary); font-weight: 600; }
.legend-line-positive { color: var(--positive); font-weight: 600; }
.legend-line-negative { color: var(--negative); font-weight: 600; }

/* ============================================================
   UTILITY CLASSES
   ============================================================ */
.text-mono {
    font-family: var(--font-mono);
}

.text-uppercase {
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.font-semibold {
    font-weight: 600;
}

.font-bold {
    font-weight: 700;
}
```

### Step 2: Add Helper Functions

Add after `render_skeleton_metric()` (around line 1740):

```python
# ============================================================
# STYLED HTML HELPER FUNCTIONS
# ============================================================

def get_status_class(value: float, threshold: float = 0) -> str:
    """
    Get CSS class name based on value comparison.

    Args:
        value: Numeric value to evaluate
        threshold: Comparison threshold (default 0)

    Returns:
        CSS class name: 'status-positive', 'status-negative', or 'status-neutral'
    """
    if value > threshold:
        return "status-positive"
    elif value < threshold:
        return "status-negative"
    return "status-neutral"


def render_styled_text(text: str, style: str = 'primary') -> str:
    """
    Render text with semantic CSS class.

    Args:
        text: Text content
        style: Style variant - 'primary', 'secondary', 'accent', 'muted'

    Returns:
        HTML span with appropriate class

    Example:
        >>> st.markdown(render_styled_text("VN-Index", "primary"), unsafe_allow_html=True)
    """
    class_map = {
        'primary': 'text-primary-emphasis',
        'secondary': 'text-secondary-emphasis',
        'accent': 'text-accent-emphasis',
        'muted': 'text-muted',
    }
    css_class = class_map.get(style, 'text-primary-emphasis')
    return f'<span class="{css_class}">{text}</span>'


def render_styled_badge(text: str, variant: str = 'primary') -> str:
    """
    Render status badge with semantic styling.

    Args:
        text: Badge text
        variant: 'primary', 'success', 'danger', 'warning', 'info'

    Returns:
        HTML span with badge classes

    Example:
        >>> st.markdown(render_styled_badge("Active", "success"), unsafe_allow_html=True)
    """
    return f'<span class="badge badge-{variant}">{text}</span>'


def render_styled_status(value: float, format_str: str = "{:+.2f}%", threshold: float = 0) -> str:
    """
    Render value with positive/negative color coding.

    Args:
        value: Numeric value
        format_str: Format string for value display
        threshold: Comparison threshold

    Returns:
        HTML span with status class

    Example:
        >>> st.markdown(render_styled_status(5.23), unsafe_allow_html=True)
        >>> st.markdown(render_styled_status(-2.1, "{:.1f}%"), unsafe_allow_html=True)
    """
    css_class = get_status_class(value, threshold)
    formatted = format_str.format(value)
    return f'<span class="{css_class}">{formatted}</span>'


def render_styled_label(text: str) -> str:
    """
    Render uppercase metric label.

    Args:
        text: Label text

    Returns:
        HTML div with metric-label class

    Example:
        >>> st.markdown(render_styled_label("VN-Index"), unsafe_allow_html=True)
    """
    return f'<div class="metric-label">{text}</div>'


def render_styled_metric_inline(label: str, value: str, delta: float = None) -> str:
    """
    Render inline metric with label, value, and optional delta.

    Args:
        label: Metric label
        value: Formatted value string
        delta: Optional delta value for color coding

    Returns:
        HTML structure with metric classes

    Example:
        >>> st.markdown(render_styled_metric_inline("Price", "25,750", 2.5), unsafe_allow_html=True)
    """
    delta_html = ""
    if delta is not None:
        delta_class = "metric-delta-positive" if delta >= 0 else "metric-delta-negative"
        delta_sign = "+" if delta >= 0 else ""
        delta_html = f' <span class="{delta_class}">{delta_sign}{delta:.2f}%</span>'

    return f'''
    <div>
        <div class="metric-label">{label}</div>
        <span class="metric-value">{value}</span>{delta_html}
    </div>
    '''


def render_legend_item(symbol: str, label: str, color_class: str) -> str:
    """
    Render chart legend item.

    Args:
        symbol: Legend symbol (e.g., "●", "┄")
        label: Legend label
        color_class: CSS class for color (e.g., "legend-line-primary")

    Returns:
        HTML span with legend styling

    Example:
        >>> st.markdown(render_legend_item("●", "VN-Index", "legend-line-primary"), unsafe_allow_html=True)
    """
    return f'<span class="{color_class}">{symbol} {label}</span>'
```

### Step 3: Export New Functions

Add to module exports (if using `__all__`):

```python
__all__ = [
    'get_page_style',
    'get_chart_layout',
    'render_styled_table',
    'get_table_style',
    'render_valuation_legend',
    'render_valuation_assessment',
    'render_skeleton_card',
    'render_skeleton_text',
    'render_skeleton_metric',
    # New exports
    'get_status_class',
    'render_styled_text',
    'render_styled_badge',
    'render_styled_status',
    'render_styled_label',
    'render_styled_metric_inline',
    'render_legend_item',
    # Color constants
    'CHART_COLORS',
    'CHART_TEXT_COLORS',
    'BAR_COLORS',
    'TRADING_CHART_COLORS',
    'DISTRIBUTION_COLORS',
    'ASSESSMENT_COLORS',
    'BAND_COLORS',
]
```

## Todo List

- [ ] Add semantic CSS classes to `get_page_style()` (15+ classes)
- [ ] Add `get_status_class()` helper function
- [ ] Add `render_styled_text()` helper function
- [ ] Add `render_styled_badge()` helper function
- [ ] Add `render_styled_status()` helper function
- [ ] Add `render_styled_label()` helper function
- [ ] Add `render_styled_metric_inline()` helper function
- [ ] Add `render_legend_item()` helper function
- [ ] Test CSS classes render correctly in browser
- [ ] Test helper functions output valid HTML

## Success Criteria

- [ ] 15+ semantic CSS classes added
- [ ] 7 helper functions implemented
- [ ] No breaking changes to existing API
- [ ] Dashboard still renders correctly
- [ ] CSS classes use existing CSS variables (no new hex codes)

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| CSS specificity conflicts | Medium | Low | Use unique class names with prefixes |
| Breaking existing styles | Low | High | Test all pages after changes |
| Browser compatibility | Low | Medium | Use standard CSS properties only |

## Verification Commands

```bash
# Run dashboard and verify no visual regression
streamlit run WEBAPP/main_app.py

# Grep for new classes to confirm they're added
grep -n "text-primary-emphasis" WEBAPP/core/styles.py

# Check helper functions are callable
python3 -c "from WEBAPP.core.styles import render_styled_text; print(render_styled_text('test', 'primary'))"
```
