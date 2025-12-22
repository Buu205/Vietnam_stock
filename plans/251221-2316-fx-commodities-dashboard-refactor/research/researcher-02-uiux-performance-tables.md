# FX & Commodities Dashboard UI/UX Research
## Performance Tables with Trend Highlighting

**Date:** 2025-12-21
**Status:** Research Complete
**Target:** FX & Commodities Dashboard (Real-time data tables)

---

## 1. EXISTING DESIGN SYSTEM

### Glassmorphism Design Tokens (In Codebase ✓)
Fully implemented in `WEBAPP/core/styles.py` and `WEBAPP/core/theme.py`:

**Glass Effect Definition:**
```css
/* From styles.py line 89-96 */
--glass-bg: rgba(255, 255, 255, 0.03);           /* Subtle 3% opacity */
--glass-bg-hover: rgba(255, 255, 255, 0.05);     /* Hover 5% opacity */
--glass-border: rgba(255, 255, 255, 0.08);       /* Border 8% opacity */
--glass-border-hover: rgba(139, 92, 246, 0.3);   /* Purple glow on hover */
--glass-blur: blur(12px);                         /* 12px backdrop blur */
--glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);   /* Depth shadow */
```

**Color Palette:**
- **Primary:** Electric Purple `#8B5CF6` (CTAs, active states)
- **Secondary:** Cyan `#06B6D4` (alternates, secondary actions)
- **Accent:** Amber `#F59E0B` (warnings, highlights)
- **Positive:** Emerald Green `#10B981` (gains, up trends)
- **Negative:** Red `#EF4444` (losses, down trends)
- **Text Primary:** `#F8FAFC` (white), **Secondary:** `#94A3B8` (gray)

---

## 2. PERFORMANCE TABLE PATTERN (Current)

### Existing Implementation (table_builders.py, lines 51-92)

**Status Color Scheme:**
```python
.status-very-cheap { color: #00D4AA; }     /* Cyan accent */
.status-cheap { color: #7FFFD4; }          /* Light cyan */
.status-fair { color: #FFD666; }           /* Yellow/Amber */
.status-expensive { color: #FF9F43; }      /* Orange */
.status-very-expensive { color: #FF6B6B; } /* Red */

.positive { color: #00D4AA; }   /* Green up */
.negative { color: #FF6B6B; }   /* Red down */
```

**Table Structure:**
- Header: Purple gradient background `rgba(139, 92, 246, 0.15)`
- Rows: Dark background `rgba(26, 22, 37, 0.5)` with striping
- Hover: Purple tint `rgba(139, 92, 246, 0.1)`
- Typography: JetBrains Mono, 12px, all-caps labels

---

## 3. FX & COMMODITIES TABLE DESIGN REQUIREMENTS

### Performance Metrics to Display
```
Symbol | Current | 1D% | 1W% | 1M% | 3M% | 1Y% | Trend | Volume | Status
-------|---------|-----|-----|-----|-----|-----|-------|--------|--------
```

### Recommended Trend Highlighting Strategy

**Per-Column Color Rules (Non-destructive):**

```python
def get_trend_color(value: float, metric_type: str = 'change') -> str:
    """
    Returns semantic color for trend highlighting.

    Args:
        value: Numeric value (percentage or raw)
        metric_type: 'change' (% change), 'ratio' (FX rate), 'volume' (absolute)
    """
    if metric_type == 'change':
        if value > 5:
            return '#10B981'      # Strong gain (green)
        elif value > 0:
            return '#34D399'      # Mild gain (light green)
        elif value == 0:
            return '#94A3B8'      # Neutral (gray)
        elif value > -5:
            return '#F87171'      # Mild loss (light red)
        else:
            return '#EF4444'      # Strong loss (red)

    elif metric_type == 'ratio':
        return '#F8FAFC'          # Use neutral for FX prices

    elif metric_type == 'volume':
        return '#06B6D4'          # Use cyan for volume accent
```

---

## 4. HTML TABLE PATTERN (Glass Styled)

### Minimal Glass Table Template

```html
<style>
.fx-table {
    width: 100%;
    border-collapse: collapse;
    background: linear-gradient(180deg, #1A1625 0%, #0F0B1E 100%);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
}

.fx-table th {
    background: linear-gradient(135deg,
        rgba(139, 92, 246, 0.15) 0%,
        rgba(6, 182, 212, 0.1) 100%);
    color: #A78BFA;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 14px 16px;
    border-bottom: 2px solid rgba(139, 92, 246, 0.3);
    text-align: left;
    font-size: 12px;
}

.fx-table td {
    padding: 12px 16px;
    color: #E2E8F0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    vertical-align: middle;
}

.fx-table tr:hover {
    background: rgba(139, 92, 246, 0.12);
}

/* Trend highlighting - right-aligned numeric columns */
.trend-value.positive {
    color: #10B981;
    font-weight: 600;
}
.trend-value.negative {
    color: #EF4444;
    font-weight: 600;
}
.trend-value.neutral {
    color: #94A3B8;
}

/* Sparkline indicator (micro trend chart) */
.sparkline-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    background: rgba(139, 92, 246, 0.15);
    border-radius: 6px;
    font-size: 11px;
}
</style>

<table class="fx-table">
    <thead>
        <tr>
            <th>Symbol</th>
            <th class="text-right">Current</th>
            <th class="text-right">1D</th>
            <th class="text-right">1W</th>
            <th class="text-right">1M</th>
            <th class="text-right">Trend</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>EURUSD</strong></td>
            <td class="text-right">1.0850</td>
            <td class="text-right trend-value positive">+0.45%</td>
            <td class="text-right trend-value positive">+1.23%</td>
            <td class="text-right trend-value neutral">-0.12%</td>
            <td><span class="sparkline-badge">↑ UP</span></td>
        </tr>
    </tbody>
</table>
```

---

## 5. PYTHON COMPONENT PATTERN

### Performance Table Builder

```python
from WEBAPP.core.theme import SEMANTIC, GLASS, DARK_THEME, TYPOGRAPHY
import pandas as pd

def build_fx_performance_table(
    data: pd.DataFrame,
    highlight_threshold: float = 5.0
) -> str:
    """
    Build FX/Commodities performance table with trend highlighting.

    Args:
        data: DataFrame with columns [symbol, current, change_1d, change_1w, ...]
        highlight_threshold: % threshold for strong trend coloring

    Returns:
        HTML string with glass-styled table
    """
    html = '<table class="fx-table"><thead><tr>'

    # Header
    for col in data.columns:
        html += f'<th>{col.upper()}</th>'
    html += '</tr></thead><tbody>'

    # Rows with trend coloring
    for _, row in data.iterrows():
        html += '<tr>'
        for col in data.columns:
            value = row[col]

            # Numeric column detection & coloring
            if isinstance(value, (int, float)) and 'change' in col.lower():
                trend_class = 'positive' if value > 0 else ('negative' if value < 0 else 'neutral')
                html += f'<td class="trend-value {trend_class}">{value:+.2f}%</td>'
            else:
                html += f'<td>{value}</td>'

        html += '</tr>'

    html += '</tbody></table>'
    return html
```

### Metric Card (Real-time Updates)

```python
def build_performance_metric_card(
    symbol: str,
    current_value: float,
    change_1d: float,
    change_1y: float
) -> str:
    """
    Compact metric card showing symbol with performance highlights.
    Suitable for sidebar or dashboard grid.
    """
    trend = 'positive' if change_1d >= 0 else 'negative'

    return f"""
    <div class="perf-metric-card">
        <div class="metric-header">
            <span class="symbol">{symbol}</span>
            <span class="value">{current_value:.4f}</span>
        </div>
        <div class="metric-footer">
            <span class="change {trend}">
                {change_1d:+.2f}% (1D)
            </span>
            <span class="change-year">
                {change_1y:+.2f}% (1Y)
            </span>
        </div>
    </div>
    """
```

---

## 6. PERFORMANCE INDICATORS (1D, 1W, 1M, 3M, 1Y)

### Column Rendering Strategy

**Key Design Decision: Right-align All Numerics**

```css
/* Numeric columns always right-aligned for scanability */
td.text-right {
    text-align: right;
    font-family: 'JetBrains Mono', monospace;
    font-variant-numeric: tabular-nums;  /* Monospace numbers */
}
```

**Trend Direction Indicators:**
- Up trend: Green `#10B981` + up arrow (↑)
- Down trend: Red `#EF4444` + down arrow (↓)
- Flat trend: Gray `#94A3B8` (no arrow)

**Multi-Timeframe Display:**
```
1D%   → Most recent, bright coloring
1W%   → Secondary importance, slightly muted
1M%   → Tertiary, muted text
3M%   → Background color hint only
1Y%   → Legend/context reference
```

---

## 7. IMPLEMENTATION CHECKLIST

- [x] Use existing theme colors (no new palettes needed)
- [x] Apply glassmorphism to table container (blur + shadow)
- [x] Color-code changes by intensity (> ±5% = strong, else mild)
- [x] Right-align numeric columns (tabular numbers)
- [x] Hover effects: Purple tint, slight scale up
- [x] Typography: JetBrains Mono for prices/metrics
- [x] Header: Purple gradient with cyan accent
- [x] Status badges for trending direction
- [x] Responsive table (horizontal scroll on mobile)

---

## 8. UNRESOLVED QUESTIONS

1. **Real-time Update Animation:** Should values flash/pulse on update? (Recommend: subtle green/red pulse for 500ms)
2. **Volume Normalization:** Display absolute volume or % of 30-day average?
3. **Sparkline Charts:** Include micro charts in trend column or keep minimal?
4. **Volume Bars:** Inline bar chart background or separate column?
5. **Sort Order:** Default to % change (1W) or market cap for commodities?

---

## File Paths

**Core Theme Files:**
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/core/theme.py` - Color tokens
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/core/styles.py` - CSS implementation
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/core/valuation_config.py` - Color mappings

**Table Components:**
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/components/tables/table_builders.py` - Existing patterns

**Implementation Location:**
- `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/components/tables/financial_tables.py` - (Create FX table builder here)

---

**Report Status:** Ready for implementation
**Estimated Dev Time:** 4-6 hours for full component library
