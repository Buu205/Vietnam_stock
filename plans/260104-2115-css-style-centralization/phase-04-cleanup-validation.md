# Phase 4: Cleanup & Validation

## Context

- [Main Plan](./plan.md)
- [Phase 3: Medium Priority](./phase-03-refactor-medium-priority.md)
- **Prerequisite:** Phases 1-3 must be completed first

## Overview

1. Refactor remaining 18 files (~75 inline styles)
2. Create validation script to detect inline hex colors
3. Update documentation
4. Final visual regression testing

## Key Insights

1. Remaining files have low violation counts (1-10 each)
2. Validation script prevents future regressions
3. Documentation ensures team follows new patterns

## Remaining Files

| File | Count | Category |
|------|-------|----------|
| `technical_dashboard.py` | 10 | Dashboard |
| `unified_forecast_table.py` | 7 | Tables |
| `consensus_table.py` | 7 | Tables |
| `achievement_cards.py` | 7 | Cards |
| `signal_dashboard.py` | 6 | Dashboard |
| `valuation_dashboard.py` | 6 | Dashboard |
| `correlation_panel.py` | 5 | Panels |
| `screening_tab.py` | 5 | Tabs |
| `portfolio_builder.py` | 4 | Features |
| `fundamental_dashboard.py` | 4 | Dashboard |
| Other 8 files | ~14 | Various |

## Related Code Files

- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/technical/technical_dashboard.py`
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/forecast/components/unified_forecast_table.py`
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/forecast/components/consensus_table.py`
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/components/cards/achievement_cards.py`
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/technical/signal_dashboard.py`
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/valuation/valuation_dashboard.py`

## Implementation Steps

### Step 1: Batch Refactor Remaining Files

For each file:

1. Add imports from `WEBAPP.core.styles`
2. Apply standard replacements:

```python
# Standard replacements
replacements = {
    'style="color: #8B5CF6; font-weight: 600;"': 'class="text-primary-emphasis"',
    'style="color: #8B5CF6; font-weight: bold;"': 'class="text-primary-emphasis"',
    'style="color: #94A3B8;': 'class="text-muted"',
    'style="color: #64748B;': 'class="text-muted"',
    'style="color: #10B981;': 'class="status-positive"',
    'style="color: #EF4444;': 'class="status-negative"',
    'style="color: #F59E0B;': 'class="status-warning"',
}
```

3. Test file renders correctly

### Step 2: Create Validation Script

Create `/Users/buuphan/Dev/Vietnam_dashboard/scripts/validate_inline_styles.py`:

```python
#!/usr/bin/env python3
"""
Validate that WEBAPP files don't contain inline hex color styles.
Run as part of CI or pre-commit hook.
"""

import re
import sys
from pathlib import Path

# Pattern to detect inline hex colors in style attributes
INLINE_HEX_PATTERN = re.compile(r'style="[^"]*#[A-Fa-f0-9]{6}[^"]*"')

# Exceptions: files/patterns that are allowed to have inline colors
EXCEPTIONS = {
    # Computed heatmap colors
    'sector_rotation.py': ['rgba('],
    # Chart config colors (not HTML)
    'styles.py': ['CHART_COLORS', 'BAR_COLORS'],
}

def check_file(filepath: Path) -> list[tuple[int, str]]:
    """Check file for inline hex colors. Returns list of (line_num, line)."""
    violations = []
    try:
        content = filepath.read_text(encoding='utf-8')
        for i, line in enumerate(content.split('\n'), 1):
            if INLINE_HEX_PATTERN.search(line):
                # Check exceptions
                filename = filepath.name
                if filename in EXCEPTIONS:
                    if any(exc in line for exc in EXCEPTIONS[filename]):
                        continue
                violations.append((i, line.strip()[:100]))
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return violations

def main():
    """Main validation function."""
    webapp_path = Path(__file__).parent.parent / 'WEBAPP'

    if not webapp_path.exists():
        print(f"Error: WEBAPP directory not found at {webapp_path}")
        sys.exit(1)

    total_violations = 0
    files_with_violations = []

    for py_file in webapp_path.rglob('*.py'):
        violations = check_file(py_file)
        if violations:
            files_with_violations.append((py_file, violations))
            total_violations += len(violations)

    if files_with_violations:
        print(f"\n{'='*60}")
        print(f"INLINE STYLE VIOLATIONS FOUND: {total_violations}")
        print(f"{'='*60}\n")

        for filepath, violations in files_with_violations:
            rel_path = filepath.relative_to(webapp_path.parent)
            print(f"\n{rel_path} ({len(violations)} violations):")
            for line_num, line in violations[:5]:  # Show first 5
                print(f"  Line {line_num}: {line}")
            if len(violations) > 5:
                print(f"  ... and {len(violations) - 5} more")

        print(f"\n{'='*60}")
        print("Use CSS classes from WEBAPP/core/styles.py instead.")
        print(f"{'='*60}\n")
        sys.exit(1)
    else:
        print("✓ No inline hex color violations found.")
        sys.exit(0)

if __name__ == '__main__':
    main()
```

### Step 3: Add Pre-commit Hook (Optional)

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: check-inline-styles
      name: Check for inline CSS hex colors
      entry: python3 scripts/validate_inline_styles.py
      language: system
      types: [python]
      pass_filenames: false
```

### Step 4: Update Documentation

Update `WEBAPP/core/styles.py` docstring:

```python
"""
Dashboard Styles - Crypto Terminal Glassmorphism
=================================================

...existing docstring...

## CSS Classes Reference

### Text Classes
- .text-primary-emphasis - Purple text, bold
- .text-secondary-emphasis - Cyan text, bold
- .text-accent-emphasis - Amber text, bold
- .text-muted - Muted gray text
- .text-secondary-sm - Small secondary text

### Status Classes
- .status-positive - Green (positive values)
- .status-negative - Red (negative values)
- .status-neutral - Gray (neutral)
- .status-warning - Amber (warnings)

### Badge Classes
- .badge - Base badge styling
- .badge-primary - Purple badge
- .badge-success - Green badge
- .badge-danger - Red badge
- .badge-warning - Amber badge
- .badge-info - Cyan badge

### Metric Classes
- .metric-label - Uppercase label
- .metric-value - Large monospace value
- .metric-value-sm - Medium monospace value
- .metric-delta-positive - Green delta
- .metric-delta-negative - Red delta

### Legend Classes
- .legend-line-primary - Purple legend
- .legend-line-secondary - Cyan legend
- .legend-line-accent - Amber legend
- .legend-line-positive - Green legend
- .legend-line-negative - Red legend

## Helper Functions

- render_styled_text(text, style) - Text with semantic class
- render_styled_badge(text, variant) - Status badge
- render_styled_status(value, format_str, threshold) - Colored value
- render_styled_label(text) - Uppercase label
- render_styled_metric_inline(label, value, delta) - Inline metric
- render_legend_item(symbol, label, color_class) - Chart legend

## Usage Example

```python
from WEBAPP.core.styles import render_styled_status, render_styled_badge

# Colored status value
st.markdown(render_styled_status(5.23, "{:+.2f}%"), unsafe_allow_html=True)

# Status badge
st.markdown(render_styled_badge("Active", "success"), unsafe_allow_html=True)
```
"""
```

### Step 5: Final Validation

Run comprehensive tests:

```bash
# Run validation script
python3 scripts/validate_inline_styles.py

# Start dashboard and manually test all pages
streamlit run WEBAPP/main_app.py

# Check specific pages:
# - Technical Dashboard
# - Forecast tabs
# - Sector Dashboard
# - Valuation Dashboard
```

## Todo List

### Batch Refactoring
- [ ] Refactor technical_dashboard.py (10 styles)
- [ ] Refactor unified_forecast_table.py (7 styles)
- [ ] Refactor consensus_table.py (7 styles)
- [ ] Refactor achievement_cards.py (7 styles)
- [ ] Refactor signal_dashboard.py (6 styles)
- [ ] Refactor valuation_dashboard.py (6 styles)
- [ ] Refactor remaining 12 files (~28 styles)

### Validation
- [ ] Create validate_inline_styles.py script
- [ ] Test script catches violations
- [ ] Test script allows exceptions
- [ ] Add pre-commit hook (optional)

### Documentation
- [ ] Update styles.py docstring with class reference
- [ ] Add usage examples
- [ ] Update CLAUDE.md if needed

### Final Testing
- [ ] Run validation script (0 violations)
- [ ] Test Technical Dashboard page
- [ ] Test Forecast pages
- [ ] Test Sector Dashboard page
- [ ] Test Valuation Dashboard page
- [ ] Visual comparison: before vs after

## Success Criteria

- [ ] 0 inline hex colors across all 24 files (except documented exceptions)
- [ ] Validation script passes with exit code 0
- [ ] All dashboard pages render correctly
- [ ] No visual regression detected
- [ ] Documentation updated

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Missed files | Low | Low | Validation script catches all |
| False positives in validation | Medium | Low | Maintain exceptions list |
| Visual regression on edge cases | Medium | Medium | Manual testing of all pages |

## Verification Commands

```bash
# Final violation count (should be 0)
grep -r 'style="[^"]*#[A-Fa-f0-9]\{6\}' WEBAPP/ --include="*.py" | wc -l

# Run validation script
python3 scripts/validate_inline_styles.py

# List all CSS classes defined
grep -o '\.[a-z][a-z0-9-]*' WEBAPP/core/styles.py | sort -u
```

## Post-Implementation

After all phases complete:

1. **Monitor:** Watch for new inline styles in PRs
2. **Enforce:** Add validation to CI pipeline
3. **Maintain:** Update CSS classes as design evolves
4. **Document:** Keep class reference up-to-date
