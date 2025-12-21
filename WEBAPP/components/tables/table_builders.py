"""
Table Builders for Valuation Dashboards
========================================
Unified table components with consistent styling.

All tables use centralized config from valuation_config.py for:
    - Colors (STATUS_COLORS)
    - Formatters (format_ratio, format_percent, format_zscore, format_change)

Usage:
    from WEBAPP.components.tables.table_builders import (
        sector_comparison_table,
        stock_valuation_table,
        forward_matrix_table
    )
"""

import pandas as pd
from typing import List, Dict, Optional
from WEBAPP.core.valuation_config import (
    STATUS_COLORS,
    format_ratio, format_percent, format_zscore, format_change,
    get_status_color, get_percentile_status
)


# =============================================================================
# TABLE FORMAT RULES
# =============================================================================
TABLE_FORMAT_RULES = {
    'pe_ttm': lambda x: format_ratio(x, 1),
    'pb': lambda x: format_ratio(x, 2),
    'ps': lambda x: format_ratio(x, 2),
    'ev_ebitda': lambda x: format_ratio(x, 1),
    'pe_fwd_2025': lambda x: format_ratio(x, 1),
    'pe_fwd_2026': lambda x: format_ratio(x, 1),
    'pb_fwd_2025': lambda x: format_ratio(x, 2),
    'pb_fwd_2026': lambda x: format_ratio(x, 2),
    'percentile': lambda x: format_percent(x),
    'z_score': lambda x: format_zscore(x),
    'change': lambda x: format_change(x),
    'current': lambda x: format_ratio(x, 2),
    'median': lambda x: format_ratio(x, 2),
    'mean': lambda x: format_ratio(x, 2),
}


# =============================================================================
# TABLE STYLES
# =============================================================================
TABLE_STYLE = """
<style>
.valuation-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    background: rgba(26, 22, 37, 0.5);
    border-radius: 8px;
    overflow: hidden;
}
.valuation-table th {
    background: rgba(139, 92, 246, 0.15);
    color: #E8E8E8;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
    border-bottom: 1px solid rgba(139, 92, 246, 0.3);
}
.valuation-table td {
    padding: 8px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: #94A3B8;
}
.valuation-table tr:hover {
    background: rgba(139, 92, 246, 0.1);
}
.valuation-table .text-right {
    text-align: right;
}
.valuation-table .text-center {
    text-align: center;
}
.status-very-cheap { color: #00D4AA; font-weight: 600; }
.status-cheap { color: #7FFFD4; }
.status-fair { color: #FFD666; }
.status-expensive { color: #FF9F43; }
.status-very-expensive { color: #FF6B6B; font-weight: 600; }
.positive { color: #00D4AA; }
.negative { color: #FF6B6B; }
</style>
"""


def _get_status_class(status: str) -> str:
    """Get CSS class for status."""
    status_map = {
        'Very Cheap': 'status-very-cheap',
        'Cheap': 'status-cheap',
        'Fair': 'status-fair',
        'Expensive': 'status-expensive',
        'Very Expensive': 'status-very-expensive'
    }
    return status_map.get(status, '')


def _get_change_class(value: float) -> str:
    """Get CSS class for positive/negative change."""
    if value is None:
        return ''
    return 'positive' if value > 0 else 'negative' if value < 0 else ''


# =============================================================================
# SECTOR COMPARISON TABLE
# =============================================================================
def sector_comparison_table(
    data: List[Dict],
    metric: str = "PE",
    columns: List[str] = None,
    show_style: bool = True
) -> str:
    """
    Generate HTML table for sector comparison.

    Args:
        data: List of dicts with keys:
            - sector: str
            - current: float
            - median: float
            - z_score: float
            - percentile: float
            - status: str
        metric: Metric label (PE, PB, etc.)
        columns: List of column keys to display
        show_style: Include inline CSS styles

    Returns:
        HTML string for the table

    Example:
        >>> sectors = valuation_service.get_sector_comparison('PE')
        >>> html = sector_comparison_table(sectors, metric='PE')
        >>> st.markdown(html, unsafe_allow_html=True)
    """
    if not data:
        return "<p>No data available</p>"

    columns = columns or ['sector', 'current', 'median', 'z_score', 'percentile', 'status']

    column_labels = {
        'sector': 'Sector',
        'current': f'{metric} Current',
        'median': 'Median',
        'mean': 'Mean',
        'z_score': 'Z-Score',
        'percentile': 'Percentile',
        'status': 'Status'
    }

    html = TABLE_STYLE if show_style else ""
    html += '<table class="valuation-table">'

    # Header
    html += '<thead><tr>'
    for col in columns:
        align = 'text-right' if col in ['current', 'median', 'mean', 'z_score', 'percentile'] else ''
        html += f'<th class="{align}">{column_labels.get(col, col.title())}</th>'
    html += '</tr></thead>'

    # Body
    html += '<tbody>'
    for row in data:
        html += '<tr>'
        for col in columns:
            value = row.get(col, '')
            align = 'text-right' if col in ['current', 'median', 'mean', 'z_score', 'percentile'] else ''

            # Format value
            if col in TABLE_FORMAT_RULES and value is not None:
                formatted = TABLE_FORMAT_RULES[col](value)
            elif col == 'status':
                status_class = _get_status_class(value)
                formatted = f'<span class="{status_class}">{value}</span>'
            else:
                formatted = str(value)

            html += f'<td class="{align}">{formatted}</td>'
        html += '</tr>'
    html += '</tbody></table>'

    return html


# =============================================================================
# STOCK VALUATION TABLE
# =============================================================================
def stock_valuation_table(
    df: pd.DataFrame,
    columns: List[str] = None,
    format_rules: Dict = None,
    show_style: bool = True
) -> str:
    """
    Generate HTML table for stock valuation list.

    Args:
        df: DataFrame with stock valuation data
        columns: List of column names to display
        format_rules: Dict mapping column name to format function
        show_style: Include inline CSS styles

    Returns:
        HTML string for the table

    Example:
        >>> stocks_df = sector_service.get_sector_stocks('Ngân hàng')
        >>> html = stock_valuation_table(stocks_df, columns=['symbol', 'pe_ttm', 'pb', 'percentile', 'status'])
        >>> st.markdown(html, unsafe_allow_html=True)
    """
    if df.empty:
        return "<p>No data available</p>"

    columns = columns or ['symbol', 'pe_ttm', 'pb', 'percentile', 'status']
    format_rules = {**TABLE_FORMAT_RULES, **(format_rules or {})}

    column_labels = {
        'symbol': 'Symbol',
        'ticker': 'Ticker',
        'pe_ttm': 'PE TTM',
        'pb': 'P/B',
        'ps': 'P/S',
        'ev_ebitda': 'EV/EBITDA',
        'percentile': 'Percentile',
        'z_score': 'Z-Score',
        'status': 'Status',
        'pe_fwd_2025': 'PE 2025F',
        'pe_fwd_2026': 'PE 2026F'
    }

    html = TABLE_STYLE if show_style else ""
    html += '<table class="valuation-table">'

    # Header
    html += '<thead><tr>'
    for col in columns:
        if col in df.columns:
            align = 'text-right' if col not in ['symbol', 'ticker', 'status'] else ''
            html += f'<th class="{align}">{column_labels.get(col, col.title())}</th>'
    html += '</tr></thead>'

    # Body
    html += '<tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in columns:
            if col not in df.columns:
                continue
            value = row[col]
            align = 'text-right' if col not in ['symbol', 'ticker', 'status'] else ''

            # Format value
            if col in format_rules and value is not None and pd.notna(value):
                formatted = format_rules[col](value)
            elif col == 'status':
                status = str(value) if pd.notna(value) else 'Fair'
                status_class = _get_status_class(status)
                formatted = f'<span class="{status_class}">{status}</span>'
            elif pd.isna(value):
                formatted = '—'
            else:
                formatted = str(value)

            html += f'<td class="{align}">{formatted}</td>'
        html += '</tr>'
    html += '</tbody></table>'

    return html


# =============================================================================
# FORWARD VALUATION MATRIX TABLE
# =============================================================================
def forward_matrix_table(
    df: pd.DataFrame,
    metrics: List[str] = None,
    forward_years: List[str] = None,
    show_style: bool = True
) -> str:
    """
    Generate HTML table for TTM vs Forward valuation comparison.

    Creates matrix table:
    | Symbol | PE TTM | PE 2025F | PE 2026F | Delta 2025 | Delta 2026 | Status |

    Args:
        df: DataFrame with columns: symbol, pe_ttm, pe_fwd_2025, pe_fwd_2026, pb, pb_fwd_2025, pb_fwd_2026
        metrics: List of metrics to include ('pe', 'pb')
        forward_years: List of forward years ('2025', '2026')
        show_style: Include inline CSS styles

    Returns:
        HTML string for the table

    Example:
        >>> bsc_df = forecast_service.get_bsc_forecasts()
        >>> html = forward_matrix_table(bsc_df, metrics=['pe'], forward_years=['2025', '2026'])
        >>> st.markdown(html, unsafe_allow_html=True)
    """
    if df.empty:
        return "<p>No data available</p>"

    metrics = metrics or ['pe']
    forward_years = forward_years or ['2025', '2026']

    html = TABLE_STYLE if show_style else ""
    html += '<table class="valuation-table">'

    # Build header
    html += '<thead><tr>'
    html += '<th>Symbol</th>'

    for metric in metrics:
        metric_upper = metric.upper()
        html += f'<th class="text-right">{metric_upper} TTM</th>'
        for year in forward_years:
            html += f'<th class="text-right">{metric_upper} {year}F</th>'
        for year in forward_years:
            html += f'<th class="text-right">Delta {year}</th>'

    html += '<th class="text-center">Status</th>'
    html += '</tr></thead>'

    # Build body
    html += '<tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        html += f'<td><b>{row.get("symbol", "")}</b></td>'

        for metric in metrics:
            # TTM value
            ttm_col = f'{metric}_ttm' if f'{metric}_ttm' in df.columns else metric
            ttm_val = row.get(ttm_col)
            html += f'<td class="text-right">{format_ratio(ttm_val, 1)}</td>'

            # Forward values and deltas
            deltas = []
            for year in forward_years:
                fwd_col = f'{metric}_fwd_{year}'
                fwd_val = row.get(fwd_col)
                html += f'<td class="text-right">{format_ratio(fwd_val, 1)}</td>'

                # Calculate delta
                if ttm_val and fwd_val and ttm_val > 0:
                    delta = ((fwd_val - ttm_val) / ttm_val) * 100
                    deltas.append(delta)
                else:
                    deltas.append(None)

            # Add delta columns
            for delta in deltas:
                if delta is not None:
                    delta_class = _get_change_class(delta)
                    html += f'<td class="text-right {delta_class}">{format_change(delta)}</td>'
                else:
                    html += '<td class="text-right">—</td>'

        # Status based on first metric's forward delta
        first_metric = metrics[0]
        ttm_col = f'{first_metric}_ttm' if f'{first_metric}_ttm' in df.columns else first_metric
        fwd_col = f'{first_metric}_fwd_2025'
        ttm_val = row.get(ttm_col)
        fwd_val = row.get(fwd_col)

        if ttm_val and fwd_val and ttm_val > 0:
            delta_pct = ((fwd_val - ttm_val) / ttm_val) * 100
            if delta_pct < -20:
                status = 'Very Cheap'
            elif delta_pct < -10:
                status = 'Cheap'
            elif delta_pct > 20:
                status = 'Very Expensive'
            elif delta_pct > 10:
                status = 'Expensive'
            else:
                status = 'Fair'
        else:
            status = 'Fair'

        status_class = _get_status_class(status)
        html += f'<td class="text-center"><span class="{status_class}">{status}</span></td>'
        html += '</tr>'

    html += '</tbody></table>'

    return html


# =============================================================================
# VNINDEX COMPARISON TABLE
# =============================================================================
def vnindex_comparison_table(
    data: List[Dict],
    metric: str = "PE",
    show_style: bool = True
) -> str:
    """
    Generate HTML table for VNIndex variant comparison.

    Args:
        data: List of dicts with keys:
            - index: str (VNINDEX, VNINDEX_EXCLUDE, BSC_INDEX)
            - current: float
            - median: float
            - mean: float
            - z_score: float
            - percentile: float
            - status: str
        metric: Metric label (PE, PB)
        show_style: Include inline CSS styles

    Returns:
        HTML string for the table

    Example:
        >>> indices = valuation_service.get_vnindex_comparison('PE')
        >>> html = vnindex_comparison_table(indices)
        >>> st.markdown(html, unsafe_allow_html=True)
    """
    if not data:
        return "<p>No data available</p>"

    html = TABLE_STYLE if show_style else ""
    html += '<table class="valuation-table">'

    # Header
    html += '<thead><tr>'
    html += f'<th>Index</th>'
    html += f'<th class="text-right">{metric} Current</th>'
    html += '<th class="text-right">Median</th>'
    html += '<th class="text-right">Mean</th>'
    html += '<th class="text-right">Z-Score</th>'
    html += '<th class="text-right">Percentile</th>'
    html += '<th class="text-center">Status</th>'
    html += '</tr></thead>'

    # Body
    html += '<tbody>'
    for row in data:
        html += '<tr>'
        html += f'<td><b>{row.get("index", "")}</b></td>'
        html += f'<td class="text-right">{format_ratio(row.get("current"), 2)}</td>'
        html += f'<td class="text-right">{format_ratio(row.get("median"), 2)}</td>'
        html += f'<td class="text-right">{format_ratio(row.get("mean"), 2)}</td>'
        html += f'<td class="text-right">{format_zscore(row.get("z_score"))}</td>'
        html += f'<td class="text-right">{format_percent(row.get("percentile"))}</td>'

        status = row.get('status', 'Fair')
        status_class = _get_status_class(status)
        html += f'<td class="text-center"><span class="{status_class}">{status}</span></td>'
        html += '</tr>'

    html += '</tbody></table>'

    return html
