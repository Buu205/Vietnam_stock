# Phase 3: Refactor Medium-Priority Files

## Context

- [Main Plan](./plan.md)
- [Phase 2: High Priority](./phase-02-refactor-high-priority.md)
- **Prerequisite:** Phases 1-2 must be completed first

## Overview

Refactor 3 medium-priority files totaling 79 inline styles:
1. `sector_dashboard.py` - 30 inline styles
2. `sector_rotation.py` - 26 inline styles
3. `comparison_styles.py` - 23 inline styles (style module candidate for consolidation)

## Key Insights

1. **sector_dashboard.py** - Sector metrics display, similar patterns to market_overview
2. **sector_rotation.py** - Rotation matrix, heatmap colors
3. **comparison_styles.py** - Already a style module, good consolidation candidate

## Requirements

1. Replace all inline hex colors with CSS classes
2. Consolidate comparison_styles.py functions into styles.py if appropriate
3. Maintain identical visual output
4. Test each file after refactoring

## Related Code Files

- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/sector/sector_dashboard.py`
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/technical/components/sector_rotation.py`
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/components/styles/comparison_styles.py`

## Implementation Steps

### File 1: sector_dashboard.py (30 styles)

#### Step 1.1: Add Imports

```python
from WEBAPP.core.styles import (
    render_styled_text,
    render_styled_status,
    render_styled_label,
    get_status_class,
)
```

#### Step 1.2: Common Patterns

| Before | After |
|--------|-------|
| `style="color: #8B5CF6; font-weight: 600;"` | `class="text-primary-emphasis"` |
| `style="color: #94A3B8; font-size: 0.75rem;"` | `class="text-secondary-sm"` |
| `style="color: #10B981;"` | `class="status-positive"` |
| `style="color: #EF4444;"` | `class="status-negative"` |

#### Step 1.3: Sector Metrics Cards

```python
# Before
f'''<div style="color: #94A3B8; font-size: 0.7rem; text-transform: uppercase;">Sector Score</div>
<span style="color: #F8FAFC; font-size: 1.2rem; font-weight: 700;">{score}</span>'''

# After
f'''<div class="metric-label">Sector Score</div>
<span class="metric-value-sm">{score}</span>'''
```

### File 2: sector_rotation.py (26 styles)

#### Step 2.1: Add Imports

```python
from WEBAPP.core.styles import (
    render_styled_text,
    render_styled_badge,
    get_status_class,
)
```

#### Step 2.2: Rotation Matrix Colors

Note: Heatmap colors may need CSS classes or remain as computed values.

```python
# Before - static colors
f'<td style="background-color: #10B981; color: white;">{value}</td>'

# After - use badge class
f'<td class="badge-success" style="padding: 8px;">{value}</td>'
```

#### Step 2.3: Quadrant Labels

```python
# Before
f'<span style="color: #8B5CF6; font-weight: 600;">Leading</span>'

# After
f'<span class="text-primary-emphasis">Leading</span>'
```

### File 3: comparison_styles.py (23 styles)

#### Analysis First

Read file to understand existing functions and determine consolidation strategy.

#### Step 3.1: Identify Reusable Functions

Functions that should move to `styles.py`:
- Any badge/status rendering functions
- Color mapping utilities

Functions that should stay (component-specific):
- Layout-specific HTML generators
- Complex conditional styling

#### Step 3.2: Update Imports in Consumers

Files that import from comparison_styles.py will need updated imports.

```python
# Before
from WEBAPP.components.styles.comparison_styles import get_comparison_color

# After (if consolidated)
from WEBAPP.core.styles import get_status_class
```

#### Step 3.3: Replace Inline Styles

```python
# Before
f'<span style="color: #10B981; font-weight: bold;">{value}</span>'

# After
f'<span class="status-positive font-bold">{value}</span>'
```

## Todo List

### sector_dashboard.py
- [ ] Add helper function imports
- [ ] Replace metric labels with CSS classes
- [ ] Replace metric values with CSS classes
- [ ] Replace status colors with CSS classes
- [ ] Test page renders correctly
- [ ] Verify no inline hex colors remain

### sector_rotation.py
- [ ] Add helper function imports
- [ ] Replace quadrant labels with CSS classes
- [ ] Replace rotation matrix colors with CSS classes
- [ ] Keep computed heatmap colors if necessary
- [ ] Test page renders correctly
- [ ] Verify no inline hex colors remain (except computed heatmap)

### comparison_styles.py
- [ ] Analyze existing functions
- [ ] Identify candidates for consolidation into styles.py
- [ ] Replace inline styles with CSS classes
- [ ] Update consumer imports if functions moved
- [ ] Test all pages using comparison_styles
- [ ] Verify no inline hex colors remain

## Success Criteria

- [ ] 0 inline hex colors in sector_dashboard.py
- [ ] 0 inline hex colors in sector_rotation.py (except computed heatmap)
- [ ] 0 inline hex colors in comparison_styles.py
- [ ] All 3 pages render visually identical
- [ ] No Python import errors

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Computed colors break | Medium | Medium | Document which colors must remain computed |
| Import path changes | Medium | Low | Search for all usages before changing |
| Heatmap visual regression | Medium | Medium | Keep computed colors for gradients |

## Verification Commands

```bash
# Count remaining inline hex colors
grep -c 'style="[^"]*#[A-Fa-f0-9]\{6\}' WEBAPP/pages/sector/sector_dashboard.py
grep -c 'style="[^"]*#[A-Fa-f0-9]\{6\}' WEBAPP/pages/technical/components/sector_rotation.py
grep -c 'style="[^"]*#[A-Fa-f0-9]\{6\}' WEBAPP/components/styles/comparison_styles.py

# Find files importing comparison_styles
grep -r "from WEBAPP.components.styles.comparison_styles" WEBAPP/

# Run dashboard
streamlit run WEBAPP/main_app.py
```

## Notes

**Heatmap Exception:**
Heatmaps often use computed colors based on value ranges. These may remain as inline styles:
```python
# Acceptable: computed gradient colors
bg_color = f"rgba({r}, {g}, {b}, 0.8)"
f'<td style="background-color: {bg_color};">{value}</td>'
```

**Consolidation Decision:**
If comparison_styles.py has <5 unique functions, consider full consolidation into styles.py.
If >5 functions with complex logic, keep as separate module but use CSS classes.
