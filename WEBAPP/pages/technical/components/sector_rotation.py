"""
Sector Rotation Component - Tab 2
=================================

Premium sector rotation analysis with RRG chart, rankings, and money flow.

Design: Crypto Terminal with fintech aesthetics
- Quadrant colors for RRG (Leading/Improving/Weakening/Lagging)
- Purple (#8B5CF6) for primary accents
- Trading colors for signals

Author: Claude Code
Date: 2025-12-25
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import TYPE_CHECKING, Optional

from WEBAPP.core.styles import get_chart_layout, BAR_COLORS

if TYPE_CHECKING:
    from ..services.ta_dashboard_service import TADashboardService


# ============================================================================
# DESIGN CONSTANTS
# ============================================================================

QUADRANT_COLORS = {
    'LEADING': '#10B981',     # Emerald Green
    'WEAKENING': '#F59E0B',   # Amber
    'LAGGING': '#EF4444',     # Red
    'IMPROVING': '#06B6D4',   # Cyan
}

QUADRANT_BG = {
    'LEADING': 'rgba(16, 185, 129, 0.15)',
    'WEAKENING': 'rgba(245, 158, 11, 0.15)',
    'LAGGING': 'rgba(239, 68, 68, 0.15)',
    'IMPROVING': 'rgba(6, 182, 212, 0.15)',
}

# Trail colors with alpha for RRG lines
QUADRANT_TRAIL = {
    'LEADING': 'rgba(16, 185, 129, 0.25)',
    'WEAKENING': 'rgba(245, 158, 11, 0.25)',
    'LAGGING': 'rgba(239, 68, 68, 0.25)',
    'IMPROVING': 'rgba(6, 182, 212, 0.25)',
    'UNKNOWN': 'rgba(100, 116, 139, 0.25)',
}

# BSC Universe - Default stock list for Stock RRG mode
BSC_UNIVERSE = [
    'VCB', 'ACB', 'TCB', 'MBB', 'CTG', 'BID', 'STB', 'HDB', 'VPB', 'TPB',
    'SSI', 'VCI', 'HCM', 'VND', 'SHS',
    'VHM', 'VIC', 'NVL', 'KDH', 'DXG', 'PDR',
    'FPT', 'CMG',
    'VNM', 'MSN', 'MWG', 'PNJ', 'DGW',
    'HPG', 'HSG', 'NKG', 'GVR', 'DPM', 'DCM',
    'GAS', 'PLX', 'PVD', 'PVS',
    'POW', 'REE', 'PC1',
    'HVN', 'VJC', 'GMD',
]

# Predefined watchlists
WATCHLISTS = {
    'BSC Universe': BSC_UNIVERSE,
    'VN30': ['VCB', 'VHM', 'VIC', 'VNM', 'HPG', 'FPT', 'GAS', 'MSN', 'MWG', 'TCB',
             'ACB', 'MBB', 'CTG', 'BID', 'VPB', 'STB', 'HDB', 'TPB', 'VJC', 'PLX',
             'POW', 'REE', 'SSI', 'VND', 'GVR', 'SAB', 'BCM', 'VRE', 'PDR', 'KDH'],
    'Banking': ['VCB', 'ACB', 'TCB', 'MBB', 'CTG', 'BID', 'STB', 'HDB', 'VPB', 'TPB',
                'EIB', 'LPB', 'MSB', 'OCB', 'SHB'],
    'Securities': ['SSI', 'VCI', 'HCM', 'VND', 'SHS', 'MBS', 'VIX', 'BSI', 'CTS', 'FTS'],
    'Real Estate': ['VHM', 'VIC', 'NVL', 'KDH', 'DXG', 'PDR', 'NLG', 'CEO', 'HDG', 'DIG'],
    'Technology': ['FPT', 'CMG', 'VGI', 'FOX'],
}


def render_sector_rotation(service: 'TADashboardService') -> None:
    """
    Render Sector Rotation tab with premium styling.

    Components:
    - RRG chart with mode selector (Sector/Stock)
    - Sector ranking table (IBD-style)
    - Money flow horizontal bar chart
    - RS Rating heatmap
    """
    # ============ RRG CHART ============
    st.markdown("### Relative Rotation Graph")
    _render_rrg_with_options(service)

    st.markdown("---")

    # ============ TWO COLUMNS: RANKING + MONEY FLOW ============
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Sector Ranking")
        ranking = service.get_sector_ranking()
        if ranking is not None and not ranking.empty:
            _render_sector_ranking_table(ranking)
        else:
            _render_empty_state("No ranking data available")

    with col2:
        # Money flow timeframe selector
        tf_col1, tf_col2 = st.columns([3, 1])
        with tf_col1:
            st.markdown("### Money Flow")
        with tf_col2:
            timeframe = st.selectbox(
                "Period",
                ['1D', '1W', '1M'],
                key="money_flow_timeframe",
                label_visibility="collapsed"
            )

        money_flow = service.get_sector_money_flow(timeframe=timeframe)
        if money_flow is not None and not money_flow.empty:
            _render_money_flow_chart(money_flow)
        else:
            _render_empty_state("No money flow data available")

    st.markdown("---")

    # ============ RS RATING HEATMAP ============
    _render_stock_rs_heatmap(service)


def _render_rrg_with_options(service: 'TADashboardService') -> None:
    """Render RRG chart with mode selector and options."""

    # ============ OPTIONS ROW ============
    col1, col2, col3, col4 = st.columns([1.5, 1.5, 1, 1])

    with col1:
        rrg_mode = st.radio(
            "Mode",
            ["Sector", "Stock"],
            horizontal=True,
            key="rrg_mode",
            label_visibility="collapsed"
        )

    with col2:
        if rrg_mode == "Stock":
            watchlist_name = st.selectbox(
                "Watchlist",
                list(WATCHLISTS.keys()),
                key="rrg_watchlist",
                label_visibility="collapsed"
            )
        else:
            watchlist_name = None

    with col3:
        trail_days = st.selectbox(
            "Trail",
            [0, 3, 5, 10],
            index=2,
            format_func=lambda x: f"{x}d trail" if x > 0 else "No trail",
            key="rrg_trail",
            label_visibility="collapsed"
        )

    with col4:
        smooth_period = st.selectbox(
            "Smooth",
            [1, 3, 5],
            index=1,
            format_func=lambda x: f"SMA{x}" if x > 1 else "Raw",
            key="rrg_smooth",
            label_visibility="collapsed"
        )

    # ============ GET DATA ============
    if rrg_mode == "Sector":
        rrg_data = service.get_sector_rs_for_rrg(smooth=smooth_period, trail_days=trail_days)
        entity_col = 'sector_code'
    else:
        rrg_data = None  # Not implemented yet
        entity_col = 'symbol'

    # ============ RENDER CHART ============
    if rrg_data is not None and not rrg_data.empty:
        fig = _create_rrg_chart(rrg_data, entity_col=entity_col, show_trail=(trail_days > 0))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Quadrant summary
        _render_rrg_summary(rrg_data, entity_col)
    else:
        if rrg_mode == "Stock":
            _render_empty_state("Stock RRG mode coming soon", icon="construction")
        else:
            _render_empty_state("No RRG data available. Run RS calculation pipeline.", icon="chart")


def _create_rrg_chart(
    rrg_df: pd.DataFrame,
    entity_col: str = 'sector_code',
    show_trail: bool = False
) -> go.Figure:
    """Create premium RRG scatter plot."""

    fig = go.Figure()

    # Get latest date for current positions
    latest_date = rrg_df['date'].max()
    latest_data = rrg_df[rrg_df['date'] == latest_date]

    # Add quadrant backgrounds
    # Leading (top-right)
    fig.add_shape(type="rect", x0=1, x1=1.3, y0=0, y1=10,
                  fillcolor="rgba(16, 185, 129, 0.05)", line_width=0)
    # Weakening (bottom-right)
    fig.add_shape(type="rect", x0=1, x1=1.3, y0=-10, y1=0,
                  fillcolor="rgba(245, 158, 11, 0.05)", line_width=0)
    # Lagging (bottom-left)
    fig.add_shape(type="rect", x0=0.7, x1=1, y0=-10, y1=0,
                  fillcolor="rgba(239, 68, 68, 0.05)", line_width=0)
    # Improving (top-left)
    fig.add_shape(type="rect", x0=0.7, x1=1, y0=0, y1=10,
                  fillcolor="rgba(6, 182, 212, 0.05)", line_width=0)

    # Add trail lines if enabled
    if show_trail and 'date' in rrg_df.columns:
        for entity in latest_data[entity_col].unique():
            entity_data = rrg_df[rrg_df[entity_col] == entity].sort_values('date')
            if len(entity_data) > 1:
                quadrant = entity_data.iloc[-1].get('quadrant', 'UNKNOWN')
                trail_color = QUADRANT_TRAIL.get(quadrant, 'rgba(100, 116, 139, 0.25)')
                fig.add_trace(go.Scatter(
                    x=entity_data['rs_ratio_smooth'],
                    y=entity_data['rs_momentum_smooth'],
                    mode='lines',
                    line=dict(width=1.5, color=trail_color),
                    showlegend=False,
                    hoverinfo='skip'
                ))

    # Add scatter points for current position
    for _, row in latest_data.iterrows():
        quadrant = row.get('quadrant', 'UNKNOWN')
        color = QUADRANT_COLORS.get(quadrant, '#64748B')

        fig.add_trace(go.Scatter(
            x=[row['rs_ratio_smooth']],
            y=[row['rs_momentum_smooth']],
            mode='markers+text',
            marker=dict(
                size=16,
                color=color,
                line=dict(width=2, color='rgba(255,255,255,0.8)'),
                symbol='circle'
            ),
            text=[row[entity_col]],
            textposition='top center',
            textfont=dict(size=11, color='#E2E8F0', family='DM Sans'),
            name=row[entity_col],
            hovertemplate=(
                f"<b>{row[entity_col]}</b><br>"
                f"RS Ratio: {row['rs_ratio_smooth']:.3f}<br>"
                f"Momentum: {row['rs_momentum_smooth']:.1f}<br>"
                f"Quadrant: {quadrant}"
                "<extra></extra>"
            )
        ))

    # Quadrant lines
    fig.add_hline(y=0, line=dict(color='#64748B', width=1, dash='solid'))
    fig.add_vline(x=1, line=dict(color='#64748B', width=1, dash='solid'))

    # Quadrant labels with HTML styling
    fig.add_annotation(x=0.82, y=7, text="IMPROVING", showarrow=False,
                       font=dict(size=11, color=QUADRANT_COLORS['IMPROVING'], family='DM Sans'),
                       bgcolor='rgba(6, 182, 212, 0.1)', borderpad=4)
    fig.add_annotation(x=1.18, y=7, text="LEADING", showarrow=False,
                       font=dict(size=11, color=QUADRANT_COLORS['LEADING'], family='DM Sans'),
                       bgcolor='rgba(16, 185, 129, 0.1)', borderpad=4)
    fig.add_annotation(x=0.82, y=-7, text="LAGGING", showarrow=False,
                       font=dict(size=11, color=QUADRANT_COLORS['LAGGING'], family='DM Sans'),
                       bgcolor='rgba(239, 68, 68, 0.1)', borderpad=4)
    fig.add_annotation(x=1.18, y=-7, text="WEAKENING", showarrow=False,
                       font=dict(size=11, color=QUADRANT_COLORS['WEAKENING'], family='DM Sans'),
                       bgcolor='rgba(245, 158, 11, 0.1)', borderpad=4)

    # Layout - increased height for better sector visibility
    layout = get_chart_layout(height=500)
    layout['showlegend'] = False
    layout['xaxis'] = dict(
        title='RS Ratio',
        range=[0.7, 1.3],
        tickfont=dict(color='#64748B'),
        gridcolor='rgba(255,255,255,0.05)',
        zerolinecolor='rgba(255,255,255,0.1)'
    )
    layout['yaxis'] = dict(
        title='RS Momentum',
        range=[-10, 10],
        tickfont=dict(color='#64748B'),
        gridcolor='rgba(255,255,255,0.05)',
        zerolinecolor='rgba(255,255,255,0.1)'
    )
    layout['hovermode'] = 'closest'

    fig.update_layout(**layout)

    return fig


def _render_rrg_summary(rrg_df: pd.DataFrame, entity_col: str) -> None:
    """Render quadrant summary with styled cards - shows ALL sectors."""
    latest_date = rrg_df['date'].max()
    latest = rrg_df[rrg_df['date'] == latest_date]

    quadrant_counts = latest['quadrant'].value_counts()

    quadrants = ['LEADING', 'IMPROVING', 'WEAKENING', 'LAGGING']

    # Build HTML for summary cards - show ALL sectors with text wrap
    cards_html = '<div style="display: flex; gap: 12px; flex-wrap: wrap; margin-top: 12px;">'

    for q in quadrants:
        count = quadrant_counts.get(q, 0)
        color = QUADRANT_COLORS.get(q, '#64748B')
        bg = QUADRANT_BG.get(q, 'rgba(100, 116, 139, 0.15)')
        entities = latest[latest['quadrant'] == q][entity_col].tolist()
        # Show ALL sectors, not truncated
        entities_str = ', '.join(entities) if entities else '-'

        # Card with text wrap to show all sectors
        card = f'<div style="flex: 1; min-width: 180px; max-width: 280px; background: {bg}; padding: 12px 16px; border-radius: 10px; border-left: 3px solid {color};"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;"><span style="color: {color}; font-size: 0.8rem; font-weight: 600;">{q}</span><span style="color: #F8FAFC; font-size: 1.2rem; font-weight: 700;">{count}</span></div><div style="color: #94A3B8; font-size: 0.7rem; line-height: 1.4; max-height: 60px; overflow-y: auto;">{entities_str}</div></div>'
        cards_html += card

    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)


def _render_sector_ranking_table(ranking: pd.DataFrame) -> None:
    """Render sector ranking as styled HTML table."""

    # Determine available columns
    available_cols = ranking.columns.tolist()

    # Build display columns
    display_cols = ['sector_code', 'strength_score']
    optional_cols = ['ret_1w', 'ret_1m', 'ret_3m', 'quadrant']
    for col in optional_cols:
        if col in available_cols:
            display_cols.append(col)

    display_df = ranking[display_cols].head(15).copy()

    # Build HTML table
    html = '''
    <div style="max-height: 400px; overflow-y: auto; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08);">
    <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
    <thead>
    <tr style="background: rgba(139, 92, 246, 0.1); position: sticky; top: 0;">
        <th style="padding: 10px 12px; text-align: left; color: #8B5CF6; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.08);">#</th>
        <th style="padding: 10px 12px; text-align: left; color: #8B5CF6; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.08);">Sector</th>
        <th style="padding: 10px 12px; text-align: right; color: #8B5CF6; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.08);">Score</th>
    '''

    if 'ret_1w' in display_df.columns:
        html += '<th style="padding: 10px 12px; text-align: right; color: #8B5CF6; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.08);">1W</th>'
    if 'quadrant' in display_df.columns:
        html += '<th style="padding: 10px 12px; text-align: center; color: #8B5CF6; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.08);">Phase</th>'

    html += '</tr></thead><tbody>'

    for idx, row in enumerate(display_df.itertuples(), 1):
        bg = 'rgba(37, 32, 51, 0.5)' if idx % 2 == 0 else 'transparent'
        score = row.strength_score if pd.notna(row.strength_score) else 0
        score_color = '#10B981' if score > 70 else ('#EF4444' if score < 30 else '#F8FAFC')

        html += f'''
        <tr style="background: {bg}; transition: background 0.15s;">
            <td style="padding: 10px 12px; color: #64748B; border-bottom: 1px solid rgba(255,255,255,0.05);">{idx}</td>
            <td style="padding: 10px 12px; color: #F8FAFC; font-weight: 500; border-bottom: 1px solid rgba(255,255,255,0.05);">{row.sector_code}</td>
            <td style="padding: 10px 12px; text-align: right; color: {score_color}; font-family: 'JetBrains Mono', monospace; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.05);">{score:.1f}</td>
        '''

        if 'ret_1w' in display_df.columns:
            ret = getattr(row, 'ret_1w', None)
            if pd.notna(ret):
                ret_color = '#10B981' if ret > 0 else '#EF4444'
                html += f'<td style="padding: 10px 12px; text-align: right; color: {ret_color}; font-family: \'JetBrains Mono\', monospace; border-bottom: 1px solid rgba(255,255,255,0.05);">{ret:+.1f}%</td>'
            else:
                html += '<td style="padding: 10px 12px; text-align: right; color: #64748B; border-bottom: 1px solid rgba(255,255,255,0.05);">-</td>'

        if 'quadrant' in display_df.columns:
            quadrant = getattr(row, 'quadrant', None)
            if quadrant and quadrant in QUADRANT_COLORS:
                q_color = QUADRANT_COLORS[quadrant]
                html += f'<td style="padding: 10px 12px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.05);"><span style="display: inline-block; width: 8px; height: 8px; background: {q_color}; border-radius: 50%;" title="{quadrant}"></span></td>'
            else:
                html += '<td style="padding: 10px 12px; text-align: center; color: #64748B; border-bottom: 1px solid rgba(255,255,255,0.05);">-</td>'

        html += '</tr>'

    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)


def _render_money_flow_chart(money_flow: pd.DataFrame) -> None:
    """Render diverging bar chart anchored at x=0 for money flow."""

    # Find the correct column
    flow_col = None
    for col in ['net_flow_1d', 'net_inflow', 'inflow_pct', 'net_flow']:
        if col in money_flow.columns:
            flow_col = col
            break

    if flow_col is None:
        _render_empty_state("No money flow column found")
        return

    # Sort by value ascending (smallest/negative at bottom, largest/positive at top)
    df = money_flow.sort_values(flow_col, ascending=True)

    # Diverging colors: Green for positive (right), Red for negative (left)
    colors = ['#10B981' if x >= 0 else '#EF4444' for x in df[flow_col]]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df['sector_code'],
        x=df[flow_col],
        orientation='h',
        marker_color=colors,
        text=[f"{x:+.1f}%" for x in df[flow_col]],
        textposition='outside',
        textfont=dict(size=10, color='#E2E8F0'),
        hovertemplate='<b>%{y}</b>: %{x:+.2f}%<extra></extra>'
    ))

    # Zero line anchor (white for visibility)
    fig.add_vline(x=0, line=dict(color='#FFFFFF', width=1))

    # Fixed height for 19 sectors
    layout = get_chart_layout(height=350)
    layout['xaxis'] = dict(
        title='Net Inflow/Outflow (%)',
        tickformat='.1f',  # Format: 10.5 (1 decimal)
        ticksuffix='%',
        zeroline=True,
        zerolinecolor='#FFFFFF',
        zerolinewidth=1,
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='#94A3B8', size=10)
    )
    layout['yaxis']['title'] = ''
    layout['showlegend'] = False
    layout['margin'] = dict(l=100, r=60, t=20, b=40)

    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Caption
    st.caption("*Dương (+): Tiền ròng chảy vào ngành | Âm (-): Tiền ròng chảy ra khỏi ngành*")


def _render_stock_rs_heatmap(service: 'TADashboardService') -> None:
    """Render Stock RS Rating Heatmap with 2D scroll (vertical + horizontal)."""

    st.markdown("### RS Rating Heatmap")

    # ============ FILTERS ============
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

    with col1:
        top_n = st.selectbox(
            "Show Top",
            [20, 50, 100, 200, 300],
            index=1,
            key="rs_heatmap_top_n",
            label_visibility="collapsed"
        )

    with col2:
        # Days selector for horizontal scroll
        days_options = {"30D": 30, "60D": 60, "90D": 90, "180D": 180}
        selected_days_label = st.selectbox(
            "Days",
            list(days_options.keys()),
            index=0,
            key="rs_heatmap_days",
            label_visibility="collapsed"
        )
        days = days_options[selected_days_label]

    with col3:
        sectors = ["All"] + service.get_sector_list()
        selected_sector = st.selectbox(
            "Sector",
            sectors,
            key="rs_heatmap_sector",
            label_visibility="collapsed"
        )

    with col4:
        search_symbol = st.text_input(
            "Search",
            key="rs_heatmap_search",
            placeholder="VCB, ACB, FPT...",
            label_visibility="collapsed"
        )

    # ============ GET DATA ============
    rs_data = service.get_stock_rs_rating_history(days=days)

    if rs_data is None or rs_data.empty:
        _render_empty_state("No RS Rating data. Run RS calculation pipeline.", icon="chart")
        return

    # ============ APPLY FILTERS ============
    filtered_df = rs_data.copy()

    if selected_sector != "All" and 'sector_code' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['sector_code'] == selected_sector]

    if search_symbol:
        symbols = [s.strip().upper() for s in search_symbol.split(',')]
        filtered_df = filtered_df[filtered_df['symbol'].isin(symbols)]

    # Sort by latest RS rating
    latest_date = filtered_df['date'].max()
    latest_rs = filtered_df[filtered_df['date'] == latest_date][['symbol', 'rs_rating']]
    latest_rs = latest_rs.sort_values('rs_rating', ascending=False)

    top_symbols = latest_rs.head(int(top_n))['symbol'].tolist()
    filtered_df = filtered_df[filtered_df['symbol'].isin(top_symbols)]

    if filtered_df.empty:
        _render_empty_state("No data matching filters")
        return

    # ============ PIVOT FOR HEATMAP ============
    pivot_df = filtered_df.pivot_table(
        index='symbol',
        columns='date',
        values='rs_rating',
        aggfunc='first'
    )

    # Sort by latest RS
    sorted_symbols = latest_rs[latest_rs['symbol'].isin(pivot_df.index)]['symbol'].tolist()
    pivot_df = pivot_df.reindex(sorted_symbols)

    # Format date columns
    pivot_df.columns = [d.strftime('%d/%m') for d in pivot_df.columns]

    # ============ CREATE HEATMAP ============
    num_stocks = len(pivot_df)
    num_days = len(pivot_df.columns)

    # Force content expansion - NEVER auto-fit to container
    # Minimum cell size: 40px width x 28px height for readability
    CELL_WIDTH = 40   # px per column (date)
    CELL_HEIGHT = 28  # px per row (stock)
    MIN_WIDTH = 1200  # Absolute minimum width

    chart_width = max(MIN_WIDTH, num_days * CELL_WIDTH + 150)  # +150 for margins/colorbar
    chart_height = max(500, num_stocks * CELL_HEIGHT + 100)    # +100 for axis/margins

    fig = _create_rs_heatmap_figure(pivot_df, width=chart_width, height=chart_height)

    # ============ SCROLLABLE CONTAINER ============
    # Fixed viewport: 600px height, 100% width
    # Enable both horizontal and vertical scroll
    # Force inner content to expand beyond container (no shrink)
    st.markdown(f'''
    <style>
    #rs-heatmap-container {{
        max-height: 600px;
        width: 100%;
        overflow-x: auto;
        overflow-y: auto;
        border-radius: 10px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        background: rgba(0, 0, 0, 0.2);
    }}
    #rs-heatmap-container > div {{
        min-width: {chart_width}px !important;
        width: {chart_width}px !important;
    }}
    /* Custom scrollbar styling */
    #rs-heatmap-container::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    #rs-heatmap-container::-webkit-scrollbar-track {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
    }}
    #rs-heatmap-container::-webkit-scrollbar-thumb {{
        background: rgba(139, 92, 246, 0.4);
        border-radius: 4px;
    }}
    #rs-heatmap-container::-webkit-scrollbar-thumb:hover {{
        background: rgba(139, 92, 246, 0.6);
    }}
    </style>
    <div id="rs-heatmap-container">
    ''', unsafe_allow_html=True)

    # Render chart with fixed dimensions (no use_container_width)
    st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False})

    st.markdown('</div>', unsafe_allow_html=True)

    # ============ INFO BAR ============
    st.markdown(f'''
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; color: #64748B; font-size: 0.75rem;">
        <span>Showing {num_stocks} stocks × {num_days} days</span>
        <span>Chart size: {chart_width}×{chart_height}px | Scroll ↔↕ to navigate</span>
    </div>
    ''', unsafe_allow_html=True)

    # ============ LEGEND ============
    st.markdown('''
    <div style="display: flex; gap: 16px; justify-content: center; padding: 8px 0; flex-wrap: wrap; font-size: 0.75rem;">
        <span style="display: flex; align-items: center; gap: 6px;"><span style="width: 12px; height: 12px; background: #4A148C; border-radius: 2px;"></span><span style="color: #94A3B8;">1-19 Very Weak</span></span>
        <span style="display: flex; align-items: center; gap: 6px;"><span style="width: 12px; height: 12px; background: #7B1FA2; border-radius: 2px;"></span><span style="color: #94A3B8;">20-49 Weak</span></span>
        <span style="display: flex; align-items: center; gap: 6px;"><span style="width: 12px; height: 12px; background: #9E9E9E; border-radius: 2px;"></span><span style="color: #94A3B8;">50-79 Average</span></span>
        <span style="display: flex; align-items: center; gap: 6px;"><span style="width: 12px; height: 12px; background: #4CAF50; border-radius: 2px;"></span><span style="color: #94A3B8;">80-99 Strong</span></span>
    </div>
    ''', unsafe_allow_html=True)


def _create_rs_heatmap_figure(pivot_df: pd.DataFrame, width: int = 800, height: int = 400) -> go.Figure:
    """
    Create styled RS Rating heatmap with forced dimensions.

    Key design decisions:
    - Force minimum cell size for readability (40px width, 28px height)
    - Larger typography: 12px for cell values, 12px for axis labels
    - Fixed dimensions - chart does NOT shrink to container
    """

    colorscale = [
        [0.0, '#4A148C'],    # Very weak (1-19)
        [0.2, '#7B1FA2'],    # Weak (20-39)
        [0.4, '#9E9E9E'],    # Below average (40-59)
        [0.6, '#81C784'],    # Above average (60-79)
        [0.8, '#4CAF50'],    # Strong (80-89)
        [1.0, '#1B5E20']     # Very strong (90-99)
    ]

    z_values = pivot_df.values
    text_values = [[str(int(v)) if pd.notna(v) else '' for v in row] for row in z_values]

    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=pivot_df.columns.tolist(),
        y=pivot_df.index.tolist(),
        colorscale=colorscale,
        zmin=1,
        zmax=99,
        text=text_values,
        texttemplate='%{text}',
        textfont=dict(size=12, color='#F8FAFC', family='JetBrains Mono, monospace'),
        hovertemplate='<b>%{y}</b><br>Date: %{x}<br>RS: %{z}<extra></extra>',
        colorbar=dict(
            title=dict(text='RS', font=dict(color='#94A3B8', size=12)),
            tickvals=[1, 25, 50, 75, 99],
            ticktext=['1', '25', '50', '75', '99'],
            tickfont=dict(color='#94A3B8', size=11),
            len=0.8,
            thickness=12
        ),
        xgap=1,  # Gap between cells for clarity
        ygap=1
    ))

    layout = get_chart_layout(height=height)
    layout['width'] = width
    layout['xaxis'] = dict(
        side='top',
        tickangle=45,
        tickfont=dict(size=12, color='#94A3B8', family='DM Sans'),
        dtick=1,  # Show all date labels
        showgrid=False
    )
    layout['yaxis'] = dict(
        autorange='reversed',
        tickfont=dict(size=12, color='#E2E8F0', family='DM Sans'),
        showgrid=False
    )
    layout['margin'] = dict(l=90, r=50, t=70, b=20)

    fig.update_layout(**layout)

    return fig


def _render_empty_state(message: str, icon: str = "info") -> None:
    """Render styled empty state message."""

    icons = {
        "info": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>',
        "chart": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" stroke-width="2"><path d="M12 20V10M6 20V4M18 20v-6"/></svg>',
        "construction": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>',
    }

    st.markdown(f'''
    <div style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 12px; padding: 24px; text-align: center;">
        {icons.get(icon, icons['info'])}
        <div style="color: #94A3B8; font-size: 0.9rem; margin-top: 8px;">{message}</div>
    </div>
    ''', unsafe_allow_html=True)
