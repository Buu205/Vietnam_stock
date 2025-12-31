"""
Consensus Table Component
=========================
BSC vs VCI forecast comparison table.

Shows:
- Ticker, Sector
- BSC Forecast (NPATMI 25F, Target Price, Rating)
- VCI Forecast (NPATMI 25F, Target Price)
- Delta (difference between BSC and VCI)
- Consensus Status (ALIGNED, BSC_BULL, VCI_BULL)

Design: Dark theme matching unified_forecast_table styling
"""

import pandas as pd
from typing import Optional

# Consensus status definitions
CONSENSUS_STATUS = {
    'ALIGNED': {
        'label': 'ALIGNED',
        'color': '#00C9AD',
        'bg': 'rgba(0, 201, 173, 0.15)',
        'desc': 'Both views aligned (<5% diff)'
    },
    'BSC_BULL': {
        'label': 'BSC BULL',
        'color': '#8B5CF6',
        'bg': 'rgba(139, 92, 246, 0.15)',
        'desc': 'BSC more optimistic'
    },
    'VCI_BULL': {
        'label': 'VCI BULL',
        'color': '#F59E0B',
        'bg': 'rgba(245, 158, 11, 0.15)',
        'desc': 'VCI more optimistic'
    },
    'ALIGNED_BEARISH': {
        'label': 'ALIGNED',
        'color': '#64748B',
        'bg': 'rgba(100, 116, 139, 0.15)',
        'desc': 'Both conservative'
    }
}

CONSENSUS_TABLE_STYLE = """
<style>
.consensus-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    background: rgba(26, 22, 37, 0.5);
    border-radius: 8px;
    overflow: hidden;
}

.consensus-table th {
    background: rgba(139, 92, 246, 0.15);
    color: #E8E8E8;
    padding: 10px 8px;
    text-align: left;
    font-weight: 600;
    border-bottom: 1px solid rgba(139, 92, 246, 0.3);
    white-space: nowrap;
    font-size: 11px;
}

.consensus-table th.text-right {
    text-align: right;
}

.consensus-table th.group-bsc {
    background: rgba(0, 155, 135, 0.15);
    border-bottom-color: rgba(0, 155, 135, 0.3);
}

.consensus-table th.group-vci {
    background: rgba(245, 158, 11, 0.15);
    border-bottom-color: rgba(245, 158, 11, 0.3);
}

.consensus-table th.group-delta {
    background: rgba(59, 130, 246, 0.15);
    border-bottom-color: rgba(59, 130, 246, 0.3);
}

.consensus-table td {
    padding: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: #94A3B8;
}

.consensus-table td.text-right {
    text-align: right;
}

.consensus-table tr:hover {
    background: rgba(139, 92, 246, 0.1);
}

/* Status badge */
.consensus-badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.7rem;
    text-transform: uppercase;
    white-space: nowrap;
}

.status-aligned {
    background: rgba(0, 201, 173, 0.2);
    color: #00C9AD;
    border: 1px solid rgba(0, 201, 173, 0.4);
}

.status-bsc-bull {
    background: rgba(139, 92, 246, 0.2);
    color: #8B5CF6;
    border: 1px solid rgba(139, 92, 246, 0.4);
}

.status-vci-bull {
    background: rgba(245, 158, 11, 0.2);
    color: #F59E0B;
    border: 1px solid rgba(245, 158, 11, 0.4);
}

/* Delta colors */
.delta-positive { color: #00C9AD !important; font-weight: 600; }
.delta-negative { color: #EF4444 !important; font-weight: 600; }
.delta-neutral { color: #64748B !important; }

/* Scroll wrapper */
.consensus-scroll-wrapper {
    overflow-x: auto;
    overflow-y: auto;
    max-height: 600px;
    -webkit-overflow-scrolling: touch;
    margin-bottom: 1rem;
    border-radius: 8px;
    border: 1px solid rgba(139, 92, 246, 0.2);
}

/* Sticky header */
.consensus-table thead th {
    position: sticky;
    top: 0;
    z-index: 20;
    background: rgba(26, 22, 37, 0.98);
}

/* Sticky first column (Symbol) */
.consensus-table th:nth-child(1),
.consensus-table td:nth-child(1) {
    position: sticky;
    left: 0;
    background: rgba(26, 22, 37, 0.98);
    z-index: 10;
    min-width: 70px;
}

.consensus-table thead th:nth-child(1) {
    z-index: 30;
}
</style>
"""


def format_consensus_status(status: str) -> str:
    """Format consensus status as badge HTML."""
    status_upper = status.upper().replace(' ', '_') if status else 'ALIGNED'

    status_class = {
        'ALIGNED': 'status-aligned',
        'BSC_BULL': 'status-bsc-bull',
        'VCI_BULL': 'status-vci-bull',
        'ALIGNED_BEARISH': 'status-aligned',
    }.get(status_upper, 'status-aligned')

    label = CONSENSUS_STATUS.get(status_upper, {}).get('label', status or '-')
    return f'<span class="consensus-badge {status_class}">{label}</span>'


def format_delta(val: float, as_pct: bool = True) -> str:
    """Format delta value with color."""
    if pd.isna(val):
        return '-'

    if as_pct:
        if abs(val) < 5:
            color_class = 'delta-neutral'
        elif val > 0:
            color_class = 'delta-positive'
        else:
            color_class = 'delta-negative'
        return f'<span class="{color_class}">{val:+.1f}%</span>'
    else:
        if abs(val) < 0.05:
            color_class = 'delta-neutral'
        elif val > 0:
            color_class = 'delta-positive'
        else:
            color_class = 'delta-negative'
        return f'<span class="{color_class}">{val*100:+.1f}%</span>'


def format_billions(val) -> str:
    """Format value in billions VND."""
    if pd.isna(val) or val == 0:
        return '-'
    if abs(val) >= 1000:
        return f'{val/1000:,.1f}T'
    return f'{val:,.0f}B'


def format_price(val) -> str:
    """Format price in VND."""
    if pd.isna(val) or val == 0:
        return '-'
    return f'{val:,.0f}'


def consensus_comparison_table(
    df: pd.DataFrame,
    show_rating: bool = True
) -> str:
    """
    Render BSC vs VCI consensus comparison table.

    Args:
        df: DataFrame with columns:
            - symbol: Stock ticker
            - sector: Sector name
            - bsc_npatmi_2025: BSC NPATMI forecast
            - bsc_target: BSC target price
            - bsc_rating: BSC rating (optional)
            - vci_npatmi_2025: VCI NPATMI forecast
            - vci_target: VCI target price
            - npatmi_delta_pct: NPATMI difference %
            - target_delta_pct: Target price difference %
            - consensus_status: ALIGNED/BSC_BULL/VCI_BULL
        show_rating: Show BSC rating column

    Returns:
        HTML table string
    """
    if df.empty:
        return '<p style="color: #94A3B8;">No consensus data available</p>'

    html = CONSENSUS_TABLE_STYLE
    html += '<div class="consensus-scroll-wrapper">'
    html += '<table class="consensus-table">'

    # Header row
    html += '<thead><tr>'
    html += '<th>Symbol</th>'
    html += '<th>Sector</th>'
    html += '<th class="text-right group-bsc">BSC NPATMI</th>'
    html += '<th class="text-right group-bsc">BSC Target</th>'
    if show_rating:
        html += '<th class="group-bsc">Rating</th>'
    html += '<th class="text-right group-vci">VCI NPATMI</th>'
    html += '<th class="text-right group-vci">VCI Target</th>'
    html += '<th class="text-right group-delta">Δ NPATMI</th>'
    html += '<th class="text-right group-delta">Δ Target</th>'
    html += '<th>Status</th>'
    html += '</tr></thead>'

    # Body rows
    html += '<tbody>'
    for _, row in df.iterrows():
        symbol = row.get('symbol', '-')
        sector = row.get('sector', '-')

        # BSC columns
        bsc_npatmi = format_billions(row.get('bsc_npatmi_2025', row.get('npatmi_forecast_2025')))
        bsc_target = format_price(row.get('bsc_target', row.get('target_price_bsc')))
        bsc_rating = row.get('bsc_rating', row.get('rating', '-'))

        # VCI columns
        vci_npatmi = format_billions(row.get('vci_npatmi_2025', row.get('vci_npatmi_forecast_2025')))
        vci_target = format_price(row.get('vci_target', row.get('target_price_vci')))

        # Delta columns
        npatmi_delta = format_delta(row.get('npatmi_delta_pct', row.get('npatmi_diff_pct')))
        target_delta = format_delta(row.get('target_delta_pct', row.get('target_diff_pct')))

        # Status
        status = format_consensus_status(row.get('consensus_status', 'ALIGNED'))

        html += '<tr>'
        html += f'<td><b style="color: #00C9AD;">{symbol}</b></td>'
        html += f'<td>{sector if pd.notna(sector) else "-"}</td>'
        html += f'<td class="text-right">{bsc_npatmi}</td>'
        html += f'<td class="text-right">{bsc_target}</td>'
        if show_rating:
            html += f'<td>{bsc_rating}</td>'
        html += f'<td class="text-right">{vci_npatmi}</td>'
        html += f'<td class="text-right">{vci_target}</td>'
        html += f'<td class="text-right">{npatmi_delta}</td>'
        html += f'<td class="text-right">{target_delta}</td>'
        html += f'<td>{status}</td>'
        html += '</tr>'

    html += '</tbody>'
    html += '</table>'
    html += '</div>'

    return html


def render_consensus_summary(summary: dict) -> str:
    """
    Render consensus summary cards.

    Args:
        summary: Dict with status counts {'ALIGNED': 45, 'BSC_BULL': 20, ...}

    Returns:
        HTML string for summary cards
    """
    html = '<div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">'

    for status, config in CONSENSUS_STATUS.items():
        count = summary.get(status, 0)
        html += f'''
        <div style="
            background: {config['bg']};
            border: 1px solid {config['color']}40;
            border-radius: 8px;
            padding: 12px 16px;
            min-width: 120px;
        ">
            <div style="color: {config['color']}; font-weight: 700; font-size: 11px; margin-bottom: 4px;">
                {config['label']}
            </div>
            <div style="color: {config['color']}; font-size: 24px; font-weight: 700; font-family: monospace;">
                {count}
            </div>
            <div style="color: #64748B; font-size: 10px;">
                {config['desc']}
            </div>
        </div>
        '''

    html += '</div>'
    return html
