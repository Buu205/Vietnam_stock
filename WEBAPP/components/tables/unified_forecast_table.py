"""
Unified Forecast Table Component
================================
Single table replacing Valuation View + Earnings View tabs.
Combines all metrics in one view with optional column toggle.

Design:
- Column Groups: Core, Valuation, Earnings, Extended (toggle)
- Dynamic Thresholds: 25% per quarter for achievement tracking
- Consistent styling with existing table builders

Usage:
    from WEBAPP.components.tables.unified_forecast_table import unified_forecast_table
    html = unified_forecast_table(df, show_extended=False)
    st.markdown(html, unsafe_allow_html=True)
"""

import pandas as pd
from typing import Optional


# =============================================================================
# COLUMN DEFINITIONS
# =============================================================================

# Sticky columns (always visible when scrolling horizontally)
CORE_COLUMNS = ['symbol', 'sector', 'upside_pct']

# PE/PB forward valuations with delta (change from 2025→2026)
VALUATION_COLUMNS = ['pe_fwd_2025', 'pe_fwd_2026', 'pe_delta', 'pb_fwd_2025', 'pb_fwd_2026', 'pb_delta']

EARNINGS_COLUMNS = ['npatmi_2025f', 'npatmi_2026f', 'npatmi_growth_yoy_2026']

# Extended: Rating moved here (less critical for quick scan) + detailed metrics
EXTENDED_COLUMNS = ['rating', 'rev_2025f', 'rev_2026f', 'rev_growth_yoy_2026', 'roe_2025f', 'target_price', 'market_cap']

COLUMN_LABELS = {
    'symbol': 'Symbol',
    'sector': 'Sector',
    'upside_pct': 'Upside',
    'pe_fwd_2025': 'PE 25F',
    'pe_fwd_2026': 'PE 26F',
    'pe_delta': 'Δ PE',
    'pb_fwd_2025': 'PB 25F',
    'pb_fwd_2026': 'PB 26F',
    'pb_delta': 'Δ PB',
    'npatmi_2025f': 'NPATMI 25F',
    'npatmi_2026f': 'NPATMI 26F',
    'npatmi_growth_yoy_2026': 'Gr 26F',
    'rating': 'Rating',
    'rev_2025f': 'Rev 25F',
    'rev_2026f': 'Rev 26F',
    'rev_growth_yoy_2026': 'Rev Gr 26F',
    'roe_2025f': 'ROE 25F',
    'target_price': 'Target',
    'market_cap': 'Mkt Cap',
}

# Alignment by column type
RIGHT_ALIGN_COLS = [
    'upside_pct', 'pe_fwd_2025', 'pe_fwd_2026', 'pe_delta',
    'pb_fwd_2025', 'pb_fwd_2026', 'pb_delta',
    'npatmi_2025f', 'npatmi_2026f', 'npatmi_growth_yoy_2026',
    'rev_2025f', 'rev_2026f', 'rev_growth_yoy_2026', 'roe_2025f', 'target_price', 'market_cap'
]


# =============================================================================
# FORMATTERS
# =============================================================================

def format_rating_badge(rating: str) -> str:
    """Format rating as colored badge HTML."""
    rating_class = {
        'STRONG BUY': 'rating-strong-buy',
        'BUY': 'rating-buy',
        'HOLD': 'rating-hold',
        'SELL': 'rating-sell',
        'STRONG SELL': 'rating-strong-sell',
        'N/A': 'rating-na',
    }.get(rating, 'rating-na')
    return f'<span class="rating-badge {rating_class}">{rating}</span>'


def format_upside(val) -> str:
    """Format upside percentage with color."""
    if pd.isna(val):
        return '-'
    pct = val * 100
    color_class = 'upside-positive' if pct >= 0 else 'upside-negative'
    return f'<span class="{color_class}">{pct:+.1f}%</span>'


def format_pe(val) -> str:
    """Format PE ratio."""
    if pd.isna(val) or val == 0:
        return '-'
    return f'{val:.1f}x'


def format_pb(val) -> str:
    """Format PB ratio."""
    if pd.isna(val) or val == 0:
        return '-'
    return f'{val:.2f}x'


def format_pe_delta(val) -> str:
    """Format PE delta with color (negative = green, positive = red)."""
    if pd.isna(val):
        return '-'
    color_class = 'upside-positive' if val < 0 else 'upside-negative'
    return f'<span class="{color_class}">{val:+.1f}%</span>'


def format_pb_delta(val) -> str:
    """Format PB delta with color (negative = green = cheaper in 2026, positive = red)."""
    if pd.isna(val):
        return '-'
    color_class = 'upside-positive' if val < 0 else 'upside-negative'
    return f'<span class="{color_class}">{val:+.1f}%</span>'


def format_billions(val) -> str:
    """Format value in billions VND."""
    if pd.isna(val) or val == 0:
        return '-'
    if abs(val) >= 1000:
        return f'{val/1000:,.1f}T'
    return f'{val:,.0f}B'


def format_growth(val) -> str:
    """Format growth percentage with color."""
    if pd.isna(val):
        return '-'
    pct = val * 100 if abs(val) < 10 else val
    color_class = 'upside-positive' if pct >= 0 else 'upside-negative'
    return f'<span class="{color_class}">{pct:+.1f}%</span>'


def format_roe(val) -> str:
    """Format ROE percentage."""
    if pd.isna(val) or val == 0:
        return '-'
    pct = val * 100 if abs(val) < 1 else val
    return f'{pct:.1f}%'


def format_price(val) -> str:
    """Format price in VND."""
    if pd.isna(val) or val == 0:
        return '-'
    return f'{val:,.0f}'


def format_market_cap(val) -> str:
    """Format market cap in billions VND."""
    if pd.isna(val) or val == 0:
        return '-'
    if val >= 1000:
        return f'{val/1000:,.1f}T'
    return f'{val:,.0f}B'


COLUMN_FORMATTERS = {
    'symbol': lambda x: f'<b style="color: #00C9AD;">{x}</b>',
    'sector': lambda x: x if pd.notna(x) else '-',
    'upside_pct': format_upside,
    'pe_fwd_2025': format_pe,
    'pe_fwd_2026': format_pe,
    'pe_delta': format_pe_delta,
    'pb_fwd_2025': format_pb,
    'pb_fwd_2026': format_pb,
    'pb_delta': format_pb_delta,
    'npatmi_2025f': format_billions,
    'npatmi_2026f': format_billions,
    'npatmi_growth_yoy_2026': format_growth,
    'rating': format_rating_badge,
    'rev_2025f': format_billions,
    'rev_2026f': format_billions,
    'rev_growth_yoy_2026': format_growth,
    'roe_2025f': format_roe,
    'target_price': format_price,
    'market_cap': format_market_cap,
}


# =============================================================================
# TABLE STYLES
# =============================================================================

UNIFIED_TABLE_STYLE = """
<style>
.unified-forecast-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    background: rgba(26, 22, 37, 0.5);
    border-radius: 8px;
    overflow: hidden;
}

.unified-forecast-table th {
    background: rgba(139, 92, 246, 0.15);
    color: #E8E8E8;
    padding: 12px 10px;
    text-align: left;
    font-weight: 600;
    border-bottom: 1px solid rgba(139, 92, 246, 0.3);
    white-space: nowrap;
    font-size: 12px;
}

.unified-forecast-table th.text-right {
    text-align: right;
}

.unified-forecast-table th.group-valuation {
    background: rgba(0, 155, 135, 0.15);
    border-bottom-color: rgba(0, 155, 135, 0.3);
}

.unified-forecast-table th.group-earnings {
    background: rgba(255, 193, 50, 0.15);
    border-bottom-color: rgba(255, 193, 50, 0.3);
}

.unified-forecast-table th.group-extended {
    background: rgba(59, 130, 246, 0.15);
    border-bottom-color: rgba(59, 130, 246, 0.3);
}

.unified-forecast-table td {
    padding: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: #94A3B8;
}

.unified-forecast-table td.text-right {
    text-align: right;
}

.unified-forecast-table tr:hover {
    background: rgba(139, 92, 246, 0.1);
}

/* Rating badges */
.rating-badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.7rem;
    text-transform: uppercase;
    white-space: nowrap;
}

.rating-strong-buy { background: rgba(0, 201, 173, 0.2); color: #00C9AD; border: 1px solid rgba(0, 201, 173, 0.4); }
.rating-buy { background: rgba(34, 197, 94, 0.2); color: #22C55E; border: 1px solid rgba(34, 197, 94, 0.4); }
.rating-hold { background: rgba(255, 193, 50, 0.2); color: #FFC132; border: 1px solid rgba(255, 193, 50, 0.4); }
.rating-sell { background: rgba(249, 115, 22, 0.2); color: #F97316; border: 1px solid rgba(249, 115, 22, 0.4); }
.rating-strong-sell { background: rgba(239, 68, 68, 0.2); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.4); }
.rating-na { background: rgba(100, 116, 139, 0.2); color: #94A3B8; border: 1px solid rgba(100, 116, 139, 0.4); }

/* Upside colors */
.upside-positive { color: #00C9AD !important; font-weight: 600; }
.upside-negative { color: #FC8181 !important; font-weight: 600; }

/* Scroll wrapper with vertical + horizontal scroll */
.table-scroll-wrapper {
    overflow-x: auto;
    overflow-y: auto;
    max-height: 600px;  /* Fixed height for vertical scroll */
    -webkit-overflow-scrolling: touch;
    margin-bottom: 1rem;
    border-radius: 8px;
    border: 1px solid rgba(139, 92, 246, 0.2);
    position: relative;  /* Required for sticky to work */
}

/* Z-Index Scale: z-0 base, z-10 sticky cols, z-20 header, z-30 corners */

/* Sticky header row - MUST be opaque and use !important */
.unified-forecast-table thead {
    position: sticky !important;
    top: 0 !important;
    z-index: 20 !important;
}

.unified-forecast-table thead th {
    position: sticky !important;
    top: 0 !important;
    z-index: 20 !important;
    /* Solid base + gradient overlay for visual effect */
    background: linear-gradient(135deg, #2D1F4A 0%, #1A2535 100%) !important;
}

/* Sticky Column 1: Symbol */
.unified-forecast-table th:nth-child(1),
.unified-forecast-table td:nth-child(1) {
    position: sticky !important;
    left: 0 !important;
    background: #1A1625 !important;
    z-index: 10 !important;
    min-width: 70px;
}

/* Sticky Column 2: Sector */
.unified-forecast-table th:nth-child(2),
.unified-forecast-table td:nth-child(2) {
    position: sticky !important;
    left: 70px !important;
    background: #1A1625 !important;
    z-index: 10 !important;
    min-width: 100px;
}

/* Sticky Column 3: Upside - with shadow separator */
.unified-forecast-table th:nth-child(3),
.unified-forecast-table td:nth-child(3) {
    position: sticky !important;
    left: 170px !important;
    background: #1A1625 !important;
    z-index: 10 !important;
    min-width: 70px;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3);
}

/* Corner cells (header + sticky column intersection) - highest z-index */
.unified-forecast-table thead th:nth-child(1),
.unified-forecast-table thead th:nth-child(2),
.unified-forecast-table thead th:nth-child(3) {
    z-index: 30 !important;
}

/* Row hover with cursor pointer */
.unified-forecast-table tbody tr {
    cursor: pointer;
    transition: background-color 200ms ease;
}

/* Mobile: only Symbol sticky */
@media (max-width: 768px) {
    .table-scroll-wrapper {
        max-height: 500px;
    }

    .unified-forecast-table th:nth-child(2),
    .unified-forecast-table td:nth-child(2),
    .unified-forecast-table th:nth-child(3),
    .unified-forecast-table td:nth-child(3) {
        position: relative !important;
        left: auto !important;
        box-shadow: none !important;
    }

    .unified-forecast-table thead th:nth-child(2),
    .unified-forecast-table thead th:nth-child(3) {
        z-index: 20 !important;
    }
}
</style>
"""


# =============================================================================
# MAIN TABLE BUILDER
# =============================================================================

def unified_forecast_table(
    df: pd.DataFrame,
    show_extended: bool = False,
    highlight_first_col: bool = True
) -> str:
    """
    Single unified table replacing Valuation + Earnings tabs.

    Args:
        df: DataFrame with all BSC forecast columns
        show_extended: Show extended columns (Revenue, ROE, Target, MktCap)
        highlight_first_col: Highlight Symbol column (default True)

    Returns:
        HTML table string

    Column Groups:
        - Core: Symbol, Sector, Rating, Upside
        - Valuation: PE 25F, PE 26F, PB 25F, Δ PE
        - Earnings: NPATMI 25F, 26F, Growth%
        - Extended (toggle): Rev 25F, Rev 26F, ROE, Target, MktCap
    """
    if df.empty:
        return '<p style="color: #94A3B8;">No data available</p>'

    df = df.copy()

    # Calculate PE delta if not present
    if 'pe_delta' not in df.columns and 'pe_fwd_2025' in df.columns and 'pe_fwd_2026' in df.columns:
        df['pe_delta'] = ((df['pe_fwd_2026'] - df['pe_fwd_2025']) / df['pe_fwd_2025'] * 100).where(
            df['pe_fwd_2025'] > 0, None
        )

    # Calculate PB delta if not present
    if 'pb_delta' not in df.columns and 'pb_fwd_2025' in df.columns and 'pb_fwd_2026' in df.columns:
        df['pb_delta'] = ((df['pb_fwd_2026'] - df['pb_fwd_2025']) / df['pb_fwd_2025'] * 100).where(
            df['pb_fwd_2025'] > 0, None
        )

    # Build column list
    all_columns = CORE_COLUMNS + VALUATION_COLUMNS + EARNINGS_COLUMNS
    if show_extended:
        all_columns = all_columns + EXTENDED_COLUMNS

    # Filter to available columns
    available_cols = [c for c in all_columns if c in df.columns]

    # Start building HTML
    html = UNIFIED_TABLE_STYLE
    html += '<div class="table-scroll-wrapper">'
    html += '<table class="unified-forecast-table">'

    # Header row
    html += '<thead><tr>'
    for col in available_cols:
        align_class = 'text-right' if col in RIGHT_ALIGN_COLS else ''

        # Determine column group for header color
        if col in VALUATION_COLUMNS:
            group_class = 'group-valuation'
        elif col in EARNINGS_COLUMNS:
            group_class = 'group-earnings'
        elif col in EXTENDED_COLUMNS:
            group_class = 'group-extended'
        else:
            group_class = ''

        label = COLUMN_LABELS.get(col, col.title())
        html += f'<th class="{align_class} {group_class}">{label}</th>'
    html += '</tr></thead>'

    # Body rows
    html += '<tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in available_cols:
            align_class = 'text-right' if col in RIGHT_ALIGN_COLS else ''
            value = row.get(col)

            # Format value
            if col in COLUMN_FORMATTERS:
                formatted = COLUMN_FORMATTERS[col](value)
            elif pd.isna(value):
                formatted = '-'
            else:
                formatted = str(value)

            html += f'<td class="{align_class}">{formatted}</td>'
        html += '</tr>'
    html += '</tbody>'

    html += '</table>'
    html += '</div>'

    return html


# =============================================================================
# HELPER: COLUMN GROUP LEGEND
# =============================================================================

def render_column_legend() -> str:
    """Render legend explaining column groups."""
    return """
    <div style="margin-bottom: 12px; font-size: 11px; color: #64748B;">
        <span style="display: inline-block; padding: 2px 8px; background: rgba(139, 92, 246, 0.15); border-radius: 4px; margin-right: 8px;">Core</span>
        <span style="display: inline-block; padding: 2px 8px; background: rgba(0, 155, 135, 0.15); border-radius: 4px; margin-right: 8px;">Valuation</span>
        <span style="display: inline-block; padding: 2px 8px; background: rgba(255, 193, 50, 0.15); border-radius: 4px; margin-right: 8px;">Earnings</span>
        <span style="display: inline-block; padding: 2px 8px; background: rgba(59, 130, 246, 0.15); border-radius: 4px;">Extended</span>
    </div>
    """
