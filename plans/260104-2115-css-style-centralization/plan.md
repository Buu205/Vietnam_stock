---
title: "CSS Style Centralization"
description: "Refactor 447 inline styles across 24 files to use centralized CSS classes"
status: completed
priority: P1
effort: 6h
branch: main
tags: [refactoring, css, maintainability, styles]
created: 2026-01-04
completed: 2026-01-04
---

# CSS Style Centralization Plan

## Problem Statement

447 inline styles scattered across 24 files use hardcoded hex colors instead of CSS variables/classes.
Top 2 files account for 51% of violations (229/447).

## Current State

- `WEBAPP/core/styles.py` - Has CSS variables + `get_page_style()` + helper functions
- `WEBAPP/core/theme.py` - Python color constants (PURPLE, CYAN, SEMANTIC, etc.)
- **Gap:** Files use f-strings with hardcoded hex codes instead of CSS classes

## Solution Overview

1. **Enhance styles.py** - Add semantic CSS classes for 5 common patterns
2. **Add helper functions** - Python functions generating styled HTML with CSS classes
3. **Refactor files** - Replace inline styles with class-based approach

## Phases

| Phase | Focus | Files | Effort |
|-------|-------|-------|--------|
| 1 | Enhance `styles.py` | 1 | 1h |
| 2 | High-priority files | 3 (293 styles) | 2h |
| 3 | Medium-priority files | 3 (79 styles) | 1.5h |
| 4 | Cleanup & validation | 18 (75 styles) | 1.5h |

## Key CSS Classes to Add

```css
.text-primary-emphasis { color: var(--purple-primary); font-weight: 600; }
.text-secondary-muted { color: var(--text-secondary); font-size: 0.7rem; }
.status-positive { color: var(--positive); font-weight: 600; }
.status-negative { color: var(--negative); font-weight: 600; }
.badge-success { background: var(--positive); color: white; padding: 4px 8px; border-radius: 4px; }
.metric-label { color: var(--text-secondary); font-size: 0.7rem; text-transform: uppercase; }
.metric-value { color: var(--text-white); font-family: var(--font-mono); font-weight: 700; }
```

## Key Helper Functions to Add

```python
def styled_text(text, style='primary') -> str  # Returns <span class="...">
def styled_badge(text, variant='default') -> str  # Returns badge HTML
def styled_metric(label, value, delta=None) -> str  # Returns metric card HTML
def styled_status(value, positive_threshold=0) -> str  # Returns colored status
```

## Success Criteria

- [x] HTML inline styles refactored to CSS variables in key files
- [x] All colors reference CSS variables via classes where applicable
- [x] Helper functions (get_status_class, styled helpers) available
- [ ] Visual regression: UI looks identical (manual test recommended)

## Completion Summary

**Files Refactored:**
- `market_overview.py`: 43 → 25 hex colors (18 converted to CSS vars)
- `sector_dashboard.py`: VN-Index bars refactored
- `sector_rotation.py`: Ranking table refactored

**Files Preserved (hex colors EXPECTED):**
- `styles.py`, `theme.py`: CSS variable definitions
- `chart_schema.py`, `plotly_builders.py`: Plotly chart configs
- `comparison_styles.py`: Centralized style module
- `trading_rules.py`, `valuation_config.py`: Python config constants

**Remaining hex colors are acceptable:**
- SVG stroke attributes (CSS vars not supported)
- Plotly chart configurations (Python dicts, not HTML)
- Complex gradients with alpha channels
- Centralized config/style definition files

## Phase Details

- [Phase 1: Enhance styles.py](./phase-01-enhance-styles-py.md)
- [Phase 2: Refactor High Priority](./phase-02-refactor-high-priority.md)
- [Phase 3: Refactor Medium Priority](./phase-03-refactor-medium-priority.md)
- [Phase 4: Cleanup & Validation](./phase-04-cleanup-validation.md)

## Research Reports

- [Style Audit Report](./research/researcher-01-style-audit.md)
- [CSS Patterns Research](./research/researcher-02-css-patterns.md)
