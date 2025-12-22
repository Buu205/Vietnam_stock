"""
Performance Table Component
===========================
Builds HTML performance tables with trend highlighting for FX & Commodities dashboard.

Features:
- Multi-timeframe changes: 1D, 1W, 1M, 3M, 1Y
- Color-coded trend highlighting (green gains, red losses)
- Trend direction badges (UP/DOWN/MIXED)
- Glassmorphism styling matching codebase theme
"""

import pandas as pd
from typing import List, Dict, Optional


# Glassmorphism styled performance table CSS
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
    font-variant-numeric: tabular-nums;
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

.perf-table .perf-strong-positive {
    color: #10B981;
    font-weight: 700;
    background: rgba(16, 185, 129, 0.1);
}

.perf-table .perf-strong-negative {
    color: #EF4444;
    font-weight: 700;
    background: rgba(239, 68, 68, 0.1);
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

.perf-table .trend-badge.mixed {
    background: rgba(148, 163, 184, 0.15);
    color: #94A3B8;
}

.perf-table .trend-badge.reversal {
    background: rgba(245, 158, 11, 0.15);
    color: #F59E0B;
}
</style>
"""


def calculate_period_changes(series: pd.DataFrame, value_col: str = 'value') -> Dict[str, Optional[float]]:
    """
    Calculate percentage changes for standard periods.

    Args:
        series: DataFrame with 'date' and value column
        value_col: Name of value column

    Returns:
        Dict with keys: current, change_1d, change_1w, change_1m, change_3m, change_1y
    """
    empty_result = {
        'current': None, 'change_1d': None, 'change_1w': None,
        'change_1m': None, 'change_3m': None, 'change_1y': None,
        'latest_date': None
    }

    if series.empty or value_col not in series.columns:
        return empty_result

    # Ensure date column and sort
    if 'date' not in series.columns:
        return empty_result

    series = series.copy()
    series['date'] = pd.to_datetime(series['date'])
    series = series.sort_values('date').reset_index(drop=True)

    # Get valid data
    valid_series = series[series[value_col].notna() & (series[value_col] > 0)]
    if valid_series.empty:
        return empty_result

    current = float(valid_series[value_col].iloc[-1])
    current_date = valid_series['date'].iloc[-1]

    def get_change(days: int) -> Optional[float]:
        target_date = current_date - pd.Timedelta(days=days)
        past = valid_series[valid_series['date'] <= target_date]
        if past.empty:
            return None
        past_value = float(past[value_col].iloc[-1])
        if past_value == 0:
            return None
        return ((current - past_value) / past_value) * 100

    return {
        'current': current,
        'change_1d': get_change(1),
        'change_1w': get_change(7),
        'change_1m': get_change(30),
        'change_3m': get_change(90),
        'change_1y': get_change(365),
        'latest_date': current_date.strftime('%Y-%m-%d') if pd.notna(current_date) else None
    }


def _format_change(value: Optional[float], threshold: float = 5.0) -> str:
    """Format change value with color class and arrow."""
    if value is None:
        return '<span class="perf-neutral">—</span>'

    # Determine CSS class based on value and threshold
    if value > threshold:
        css_class = 'perf-strong-positive'
    elif value > 0:
        css_class = 'perf-positive'
    elif value < -threshold:
        css_class = 'perf-strong-negative'
    elif value < 0:
        css_class = 'perf-negative'
    else:
        css_class = 'perf-neutral'

    arrow = '↑' if value > 0 else ('↓' if value < 0 else '')
    return f'<span class="{css_class}">{arrow}{value:+.2f}%</span>'


def _get_trend_badge(change_1w: Optional[float], change_1m: Optional[float]) -> str:
    """Determine trend from 1W and 1M changes."""
    if change_1w is None or change_1m is None:
        return '<span class="trend-badge mixed">— N/A</span>'

    # Check for trend reversal (different directions)
    if (change_1w > 0 and change_1m < -3) or (change_1w < 0 and change_1m > 3):
        direction = '↗️' if change_1w > 0 else '↘️'
        return f'<span class="trend-badge reversal">{direction} REVERSAL</span>'

    # Strong trend if both agree
    if change_1w > 0 and change_1m > 0:
        return '<span class="trend-badge up">↑ UP</span>'
    elif change_1w < 0 and change_1m < 0:
        return '<span class="trend-badge down">↓ DOWN</span>'
    else:
        return '<span class="trend-badge mixed">→ MIXED</span>'


def build_performance_table(
    data: List[Dict],
    show_1y: bool = True,
    show_style: bool = True,
    value_format: str = ',.2f',
    unit: str = ''
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
        value_format: Format string for current value
        unit: Unit suffix for current value

    Returns:
        HTML string
    """
    if not data:
        return "<p style='color: #94A3B8;'>No performance data available</p>"

    html = PERFORMANCE_TABLE_STYLE if show_style else ""
    html += '<div class="perf-table-container">'
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
            formatted = f'{current:{value_format}}'
            html += f'<td>{formatted}{unit}</td>'
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
    html += '</div>'

    return html


def get_top_movers(data: List[Dict], n: int = 3, period: str = 'change_1w') -> tuple:
    """
    Get top gainers and losers by specified period.

    Args:
        data: List of performance data dicts
        n: Number of top movers to return
        period: Period key (change_1d, change_1w, change_1m, etc.)

    Returns:
        Tuple of (gainers, losers)
    """
    valid_data = [d for d in data if d.get(period) is not None]
    sorted_data = sorted(valid_data, key=lambda x: x[period], reverse=True)

    gainers = [d for d in sorted_data[:n] if d[period] > 0]
    losers = [d for d in sorted_data[-n:][::-1] if d[period] < 0]

    return gainers, losers
