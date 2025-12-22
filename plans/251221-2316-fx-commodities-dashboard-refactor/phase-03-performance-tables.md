# Phase 3: Performance Tables

**Priority:** Medium
**Effort:** 4 hours
**Risk:** Medium

---

## Context

Research report (`researcher-02`, lines 60-66) identified need for performance summary tables with:
- Multi-timeframe changes: 1D, 1W, 1M, 3M, 1Y
- Color-coded trend highlighting (green/red)
- Strongest gainers/losers indicators

Current dashboard only shows latest value, no historical comparison.

## Overview

Add performance summary table component showing:
```
Symbol | Current | 1D% | 1W% | 1M% | 3M% | 1Y% | Trend
-------|---------|-----|-----|-----|-----|-----|------
```

## Requirements

1. Calculate period changes (1D, 1W, 1M, 3M, 1Y) from historical data
2. Color-code changes: green for gains, red for losses
3. Show trend direction indicator (up/down arrow)
4. Support both Macro and Commodity data
5. Use existing glassmorphism table styling

## Related Code Files

### `table_builders.py` (lines 51-92)
Status color classes already defined:
```python
.positive { color: #00D4AA; }
.negative { color: #FF6B6B; }
```

### `styles.py` (lines 1368-1475)
Styled table CSS with glassmorphism - `.styled-table-container`, `.styled-table`

### Research Pattern (`researcher-02`, lines 200-242)
Recommended `build_fx_performance_table()` function structure

## Implementation Steps

### Step 1: Create Performance Calculation Helper (ADD)
Add to `macro_commodity_loader.py` or new file `WEBAPP/services/performance_calc.py`:

```python
import pandas as pd
from typing import Dict, Optional

def calculate_period_changes(series: pd.DataFrame, value_col: str = 'value') -> Dict[str, Optional[float]]:
    """
    Calculate percentage changes for standard periods.

    Args:
        series: DataFrame with 'date' and value column
        value_col: Name of value column

    Returns:
        Dict with keys: current, change_1d, change_1w, change_1m, change_3m, change_1y
    """
    if series.empty or value_col not in series.columns:
        return {
            'current': None, 'change_1d': None, 'change_1w': None,
            'change_1m': None, 'change_3m': None, 'change_1y': None
        }

    series = series.sort_values('date').reset_index(drop=True)
    current = series[value_col].iloc[-1]
    current_date = series['date'].iloc[-1]

    def get_change(days: int) -> Optional[float]:
        target_date = current_date - pd.Timedelta(days=days)
        # Find closest date before target
        past = series[series['date'] <= target_date]
        if past.empty:
            return None
        past_value = past[value_col].iloc[-1]
        if past_value == 0:
            return None
        return ((current - past_value) / past_value) * 100

    return {
        'current': current,
        'change_1d': get_change(1),
        'change_1w': get_change(7),
        'change_1m': get_change(30),
        'change_3m': get_change(90),
        'change_1y': get_change(365)
    }
```

### Step 2: Create Performance Table Builder (ADD)
Add to `table_builders.py` or new file `WEBAPP/components/tables/performance_table.py`:

```python
import pandas as pd
from typing import List, Dict

PERFORMANCE_TABLE_STYLE = """
<style>
.perf-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    background: linear-gradient(180deg, #1A1625 0%, #0F0B1E 100%);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.perf-table th {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%);
    color: #A78BFA;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 14px 12px;
    border-bottom: 2px solid rgba(139, 92, 246, 0.3);
    text-align: right;
    font-size: 11px;
}

.perf-table th:first-child {
    text-align: left;
}

.perf-table td {
    padding: 10px 12px;
    color: #E2E8F0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    text-align: right;
}

.perf-table td:first-child {
    text-align: left;
    font-weight: 500;
    color: #FFFFFF;
}

.perf-table tr:hover {
    background: rgba(139, 92, 246, 0.12);
}

.perf-table .perf-positive {
    color: #10B981;
    font-weight: 600;
}

.perf-table .perf-negative {
    color: #EF4444;
    font-weight: 600;
}

.perf-table .perf-neutral {
    color: #94A3B8;
}

.perf-table .trend-up {
    color: #10B981;
}

.perf-table .trend-down {
    color: #EF4444;
}

.perf-table .trend-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}

.perf-table .trend-badge.up {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
}

.perf-table .trend-badge.down {
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
}
</style>
"""


def _format_change(value: float) -> str:
    """Format change with color class."""
    if value is None:
        return '<span class="perf-neutral">—</span>'
    css_class = 'perf-positive' if value > 0 else ('perf-negative' if value < 0 else 'perf-neutral')
    arrow = '↑' if value > 0 else ('↓' if value < 0 else '')
    return f'<span class="{css_class}">{arrow}{value:+.2f}%</span>'


def _get_trend_badge(change_1w: float, change_1m: float) -> str:
    """Determine trend from 1W and 1M changes."""
    if change_1w is None or change_1m is None:
        return '<span class="perf-neutral">—</span>'

    # Strong trend if both agree
    if change_1w > 0 and change_1m > 0:
        return '<span class="trend-badge up">↑ UP</span>'
    elif change_1w < 0 and change_1m < 0:
        return '<span class="trend-badge down">↓ DOWN</span>'
    else:
        return '<span class="perf-neutral">→ MIXED</span>'


def build_performance_table(
    data: List[Dict],
    show_1y: bool = True,
    show_style: bool = True
) -> str:
    """
    Build HTML performance table.

    Args:
        data: List of dicts with keys:
            - symbol: str
            - label: str (display name)
            - current: float
            - change_1d, change_1w, change_1m, change_3m, change_1y: float
        show_1y: Include 1Y column
        show_style: Include CSS style block

    Returns:
        HTML string
    """
    if not data:
        return "<p>No performance data available</p>"

    html = PERFORMANCE_TABLE_STYLE if show_style else ""
    html += '<table class="perf-table">'

    # Header
    html += '<thead><tr>'
    html += '<th>Indicator</th>'
    html += '<th>Current</th>'
    html += '<th>1D</th>'
    html += '<th>1W</th>'
    html += '<th>1M</th>'
    html += '<th>3M</th>'
    if show_1y:
        html += '<th>1Y</th>'
    html += '<th>Trend</th>'
    html += '</tr></thead>'

    # Body
    html += '<tbody>'
    for row in data:
        html += '<tr>'
        html += f'<td>{row.get("label", row.get("symbol", ""))}</td>'

        # Current value
        current = row.get('current')
        if current is not None:
            html += f'<td>{current:,.2f}</td>'
        else:
            html += '<td>—</td>'

        # Change columns
        html += f'<td>{_format_change(row.get("change_1d"))}</td>'
        html += f'<td>{_format_change(row.get("change_1w"))}</td>'
        html += f'<td>{_format_change(row.get("change_1m"))}</td>'
        html += f'<td>{_format_change(row.get("change_3m"))}</td>'
        if show_1y:
            html += f'<td>{_format_change(row.get("change_1y"))}</td>'

        # Trend badge
        html += f'<td>{_get_trend_badge(row.get("change_1w"), row.get("change_1m"))}</td>'
        html += '</tr>'

    html += '</tbody></table>'

    return html
```

### Step 3: Integrate Performance Table into Dashboard (MODIFY)
Add to `fx_commodities_dashboard.py` after chart rendering:

```python
# Add import at top
from WEBAPP.components.tables.performance_table import build_performance_table, calculate_period_changes

# After chart in Macro tab (around line 340):
st.markdown("### Performance Summary")

# Build performance data for all symbols in current group
perf_data = []
for symbol in group['symbols']:
    actual_symbol = get_actual_symbol(symbol)
    series = macro_loader.get_series(actual_symbol)
    if not series.empty:
        changes = calculate_period_changes(series, 'value')
        perf_data.append({
            'symbol': symbol,
            'label': get_label(symbol),
            **changes
        })

if perf_data:
    st.markdown(build_performance_table(perf_data), unsafe_allow_html=True)
```

### Step 4: Add Commodity Performance Table (MODIFY)
Add similar logic to Commodity tab after commodity chart:

```python
# After commodity chart (around line 495):
st.markdown("### Performance Summary")

# Calculate performance for selected commodities
commodity_perf = []
displayed_symbols = [symbol1, symbol2] if selected_commodity in dual_axis_pairs else [symbol]

for sym in displayed_symbols:
    series = commodity_loader.get_series(sym)
    if not series.empty:
        value_col = 'close' if 'close' in series.columns else 'value'
        changes = calculate_period_changes(series, value_col)
        commodity_perf.append({
            'symbol': sym,
            'label': commodity_labels.get(sym, sym),
            **changes
        })

if commodity_perf:
    st.markdown(build_performance_table(commodity_perf, show_1y=True), unsafe_allow_html=True)
```

### Step 5: Add Gainers/Losers Summary (OPTIONAL ENHANCEMENT)
Add at top of each tab:

```python
def get_top_movers(data: List[Dict], n: int = 3) -> tuple:
    """Get top gainers and losers by 1W change."""
    sorted_data = sorted(
        [d for d in data if d.get('change_1w') is not None],
        key=lambda x: x['change_1w'],
        reverse=True
    )
    gainers = sorted_data[:n]
    losers = sorted_data[-n:][::-1]  # Reverse for biggest losers first
    return gainers, losers


# Add summary cards at top of tab
if all_perf_data:
    gainers, losers = get_top_movers(all_perf_data)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📈 Top Gainers (1W)")
        for g in gainers:
            st.markdown(f"**{g['label']}**: {g['change_1w']:+.2f}%")
    with col2:
        st.markdown("#### 📉 Top Losers (1W)")
        for l in losers:
            st.markdown(f"**{l['label']}**: {l['change_1w']:+.2f}%")
```

## Success Criteria

1. [ ] Performance table renders below charts
2. [ ] All 5 time periods (1D, 1W, 1M, 3M, 1Y) show correct changes
3. [ ] Green color for gains, red for losses
4. [ ] Trend badge shows UP/DOWN/MIXED correctly
5. [ ] Table uses glassmorphism styling matching codebase
6. [ ] No errors for missing data (graceful fallback)

## Testing Steps

1. Navigate to Macro tab, select interest rate group
2. Verify performance table appears below chart
3. Check 1D change reflects actual 1-day difference
4. Check trend badge logic (both 1W & 1M positive = UP)
5. Navigate to Commodities tab
6. Verify performance table for commodity pairs
7. Test with missing data (new commodity with <1Y history)

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Stale data causing wrong changes | Medium | High | Add data freshness warning |
| Calculation errors at period edges | Medium | Medium | Use closest available date |
| Table too wide on mobile | Medium | Low | Hide 1Y column on mobile |
| Performance with many rows | Low | Low | Limit to 30 rows |

## Dependencies

- Phase 1 complete (symbol mapping)
- Phase 2 complete (chart groups defined)
- `styles.py` glass styling patterns

## File Changes Summary

| File | Change Type | Lines |
|------|-------------|-------|
| `performance_table.py` | New file | ~120 lines |
| `fx_commodities_dashboard.py` | Add imports + integration | ~30 lines |
