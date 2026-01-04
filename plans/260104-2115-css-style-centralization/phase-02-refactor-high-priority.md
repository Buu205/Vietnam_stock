# Phase 2: Refactor High-Priority Files

## Context

- [Main Plan](./plan.md)
- [Phase 1: Enhance styles.py](./phase-01-enhance-styles-py.md)
- **Prerequisite:** Phase 1 must be completed first

## Overview

Refactor 3 highest-offender files totaling 293 inline styles:
1. `market_overview.py` - 125 inline styles
2. `bsc_vs_consensus_tab.py` - 104 inline styles
3. `stock_scanner.py` - 64 inline styles

## Key Insights

1. **Pattern repetition** - Same 5-6 patterns repeated hundreds of times
2. **Replace f-strings** - Change `style="color: #8B5CF6"` to `class="text-primary-emphasis"`
3. **Import helper functions** - Use new functions from Phase 1
4. **Batch find-replace** - Most changes are mechanical substitutions

## Requirements

1. Replace all inline hex colors with CSS classes
2. Use helper functions where applicable
3. Maintain identical visual output
4. Test each file after refactoring

## Architecture

```
Before: f'<span style="color: #8B5CF6; font-weight: 600;">{text}</span>'
After:  f'<span class="text-primary-emphasis">{text}</span>'

Before: f'<span style="color: {"#10B981" if val > 0 else "#EF4444"}">{val}</span>'
After:  render_styled_status(val, "{:.2f}%")
```

## Related Code Files

- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/technical/components/market_overview.py`
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/forecast/tabs/bsc_vs_consensus_tab.py`
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/technical/components/stock_scanner.py`

## Implementation Steps

### File 1: market_overview.py (125 styles)

#### Step 1.1: Add Imports

```python
from WEBAPP.core.styles import (
    render_styled_text,
    render_styled_badge,
    render_styled_status,
    render_styled_label,
    render_styled_metric_inline,
    render_legend_item,
    get_status_class,
)
```

#### Step 1.2: Common Replacements

| Before | After |
|--------|-------|
| `style="color: #8B5CF6; font-weight: 600;"` | `class="text-primary-emphasis"` |
| `style="color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;"` | `class="metric-label"` |
| `style="color: #F8FAFC; font-size: 1.4rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;"` | `class="metric-value"` |
| `style="color: #64748B; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em;"` | `class="metric-label"` |
| `style="color: #E2E8F0; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;"` | `class="metric-value-xs text-mono"` |
| `style="color: #10B981; font-weight: 600;"` | `class="status-positive"` |
| `style="color: #EF4444; font-weight: 600;"` | `class="status-negative"` |

#### Step 1.3: Legend Items (lines 336-339)

```python
# Before
f'''<span style="color: #8B5CF6; font-weight: 600;">● VN-Index</span>
<span style="color: #10B981; font-weight: 600;">┄ MA20</span>
<span style="color: #F59E0B; font-weight: 600;">┄ MA50</span>
<span style="color: #EF4444; font-weight: 600;">┄ MA100</span>'''

# After
f'''{render_legend_item("●", "VN-Index", "legend-line-primary")}
{render_legend_item("┄", "MA20", "legend-line-positive")}
{render_legend_item("┄", "MA50", "legend-line-accent")}
{render_legend_item("┄", "MA100", "legend-line-negative")}'''
```

#### Step 1.4: Status Indicators

```python
# Before (line 452)
recovery_html = '<span style="color: #10B981; font-size: 0.7rem; margin-left: 6px;">▲ Recovering</span>'

# After
recovery_html = '<span class="status-positive" style="font-size: 0.7rem; margin-left: 6px;">▲ Recovering</span>'
```

#### Step 1.5: Progress Bars (lines 485-508)

```python
# Before
f'''<span style="color: #8B5CF6; font-size: 0.75rem; font-weight: 600; width: 45px;">MA20</span>'''

# After
f'''<span class="text-primary-emphasis" style="font-size: 0.75rem; width: 45px;">MA20</span>'''
```

Note: Keep `width` in inline style (layout-specific, not themeable)

### File 2: bsc_vs_consensus_tab.py (104 styles)

#### Step 2.1: Add Imports

```python
from WEBAPP.core.styles import (
    render_styled_text,
    render_styled_badge,
    render_styled_status,
    get_status_class,
)
```

#### Step 2.2: Common Replacements

| Pattern | Count | Before | After |
|---------|-------|--------|-------|
| Rating badges | ~30 | `style="background-color: #10B981; color: white; padding: 4px 8px;"` | `class="badge badge-success"` |
| Price targets | ~25 | `style="color: #8B5CF6; font-weight: bold;"` | `class="text-primary-emphasis"` |
| Upside/downside | ~20 | `style="color: {"#10B981" if x > 0 else "#EF4444"}"` | `class="{get_status_class(x)}"` |
| Table headers | ~15 | `style="color: #94A3B8; font-size: 12px;"` | `class="text-secondary-sm"` |

#### Step 2.3: Dynamic Status Pattern

```python
# Before
f'<span style="color: {"#10B981" if upside > 0 else "#EF4444"}; font-weight: bold;">{upside:+.1f}%</span>'

# After
f'{render_styled_status(upside, "{:+.1f}%")}'
```

### File 3: stock_scanner.py (64 styles)

#### Step 3.1: Add Imports

```python
from WEBAPP.core.styles import (
    render_styled_text,
    render_styled_badge,
    render_styled_status,
    render_styled_label,
    get_status_class,
)
```

#### Step 3.2: Signal Badges

```python
# Before
f'<span style="background-color: #10B981; color: white; padding: 2px 8px; border-radius: 4px; font-weight: 600;">BUY</span>'

# After
render_styled_badge("BUY", "success")
```

#### Step 3.3: Scanner Results Table

```python
# Before
f'''<td style="color: #E2E8F0; padding: 8px;">{ticker}</td>
<td style="color: {"#10B981" if change > 0 else "#EF4444"}; padding: 8px;">{change:+.2f}%</td>'''

# After
f'''<td class="text-primary" style="padding: 8px;">{ticker}</td>
<td class="{get_status_class(change)}" style="padding: 8px;">{change:+.2f}%</td>'''
```

## Todo List

### market_overview.py
- [ ] Add helper function imports
- [ ] Replace metric labels (style→class)
- [ ] Replace metric values (style→class)
- [ ] Replace status indicators (style→class)
- [ ] Replace legend items with helper function
- [ ] Replace progress bar colors (style→class)
- [ ] Test page renders correctly
- [ ] Verify no inline hex colors remain

### bsc_vs_consensus_tab.py
- [ ] Add helper function imports
- [ ] Replace rating badges (style→class)
- [ ] Replace price targets (style→class)
- [ ] Replace upside/downside with render_styled_status()
- [ ] Replace table headers (style→class)
- [ ] Test page renders correctly
- [ ] Verify no inline hex colors remain

### stock_scanner.py
- [ ] Add helper function imports
- [ ] Replace signal badges with render_styled_badge()
- [ ] Replace scanner results table cells (style→class)
- [ ] Replace change values with get_status_class()
- [ ] Test page renders correctly
- [ ] Verify no inline hex colors remain

## Success Criteria

- [ ] 0 inline hex colors in market_overview.py
- [ ] 0 inline hex colors in bsc_vs_consensus_tab.py
- [ ] 0 inline hex colors in stock_scanner.py
- [ ] All 3 pages render visually identical to before
- [ ] No Python errors or warnings

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Visual regression | Medium | High | Side-by-side comparison before/after |
| Missing class definition | Low | Medium | Test in browser, check CSS is loaded |
| Dynamic class name issues | Medium | Low | Use get_status_class() helper |
| Layout-specific styles removed | Medium | Medium | Keep layout props (width, padding) inline |

## Verification Commands

```bash
# Count remaining inline hex colors
grep -c 'style="[^"]*#[A-Fa-f0-9]\{6\}' WEBAPP/pages/technical/components/market_overview.py
grep -c 'style="[^"]*#[A-Fa-f0-9]\{6\}' WEBAPP/pages/forecast/tabs/bsc_vs_consensus_tab.py
grep -c 'style="[^"]*#[A-Fa-f0-9]\{6\}' WEBAPP/pages/technical/components/stock_scanner.py

# Run dashboard and test pages
streamlit run WEBAPP/main_app.py
```

## Notes

**Keep inline for layout-specific properties:**
- `width`, `min-width`, `max-width`
- `padding`, `margin`
- `gap`, `display: flex/grid`
- `position`, `top/left/right/bottom`

**Replace with classes for theme properties:**
- `color`
- `background-color`
- `font-weight`, `font-family`, `font-size`
- `border-color`
