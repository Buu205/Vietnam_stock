"""
Sector Tab
==========
Tab 1: Sector Forward Valuation with Table/Chart toggle.

Features:
- Unified sector table (no sub-tabs)
- Valuation Matrix chart (PE TTM vs 2026F)
- Single sector filter
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from WEBAPP.core.styles import render_styled_table


def format_number(val, decimals: int = 1, suffix: str = '') -> str:
    """Format number with suffix."""
    if pd.isna(val) or val == 0:
        return '-'
    return f"{val:,.{decimals}f}{suffix}"


def format_market_cap(val) -> str:
    """Format market cap in trillions."""
    if pd.isna(val) or val == 0:
        return '-'
    if val >= 1000:
        return f"{val/1000:,.1f}T"
    return f"{val:,.0f}B"


def format_upside(val) -> str:
    """Format upside with color."""
    if pd.isna(val):
        return '-'
    color = '#22C55E' if val >= 0 else '#EF4444'
    return f'<span style="color:{color};font-weight:600;">{val*100:+.1f}%</span>'


def format_growth(val) -> str:
    """Format growth percentage."""
    if pd.isna(val):
        return '-'
    color = '#22C55E' if val >= 0 else '#EF4444'
    return f'<span style="color:{color};">{val*100:+.1f}%</span>'


def render_valuation_matrix(
    stats_data: list,
    bsc_forward_2026: dict,
    selected_sector: str,
    metric: str = "PE",
    vci_forward_2026: dict = None
) -> go.Figure:
    """
    Simplified Valuation Matrix: TTM vs 2026F (BSC + VCI).
    Only shows stocks that exist in BSC Universal.

    Args:
        stats_data: List of dicts with {symbol, current, p25, p75, p5, p95, status}
        bsc_forward_2026: Dict mapping symbol -> BSC PE FWD 2026
        selected_sector: Sector name for title
        metric: PE or PB
        vci_forward_2026: Dict mapping symbol -> VCI PE FWD 2026 (optional)
    """
    if not stats_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='#94A3B8')
        )
        return fig

    # Filter only stocks in BSC Universal (those with forward values)
    bsc_symbols = set(bsc_forward_2026.keys())
    stats_data = [d for d in stats_data if d['symbol'] in bsc_symbols]

    if not stats_data:
        fig = go.Figure()
        fig.add_annotation(
            text=f"No BSC coverage for {selected_sector}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='#94A3B8')
        )
        return fig

    # Sort by current value
    stats_data = sorted(stats_data, key=lambda x: x.get('current', 0) or 0)

    symbols = [d['symbol'] for d in stats_data]
    p25_vals = [d.get('p25', 0) for d in stats_data]
    p75_vals = [d.get('p75', 0) for d in stats_data]
    p5_vals = [d.get('p5', d.get('min', 0)) for d in stats_data]
    p95_vals = [d.get('p95', d.get('max', 0)) for d in stats_data]
    current_vals = [d.get('current', 0) for d in stats_data]
    statuses = [d.get('status', 'Fair') for d in stats_data]

    # Forward 2026 values
    bsc_2026_vals = [bsc_forward_2026.get(s) for s in symbols]
    vci_2026_vals = [vci_forward_2026.get(s) if vci_forward_2026 else None for s in symbols]

    # Overlap detection: if values are within 5% of TTM, use wider X offset
    OVERLAP_THRESHOLD_PCT = 0.05  # 5%
    X_OFFSET_NORMAL = 0.1    # Normal offset
    X_OFFSET_OVERLAP = 0.18  # Wider offset when overlapping

    def calc_x_offsets(i: int, ttm: float, bsc: float, vci: float) -> tuple:
        """Calculate X offsets based on value proximity (<5% = overlap)."""
        if ttm is None or ttm <= 0:
            return i, i - X_OFFSET_NORMAL, i + X_OFFSET_NORMAL

        threshold = ttm * OVERLAP_THRESHOLD_PCT
        distances = []
        if bsc and bsc > 0:
            distances.append(abs(ttm - bsc))
        if vci and vci > 0:
            distances.append(abs(ttm - vci))
        if bsc and vci and bsc > 0 and vci > 0:
            distances.append(abs(bsc - vci))

        # If any pair is closer than 5%, use wider offset
        min_dist = min(distances) if distances else float('inf')
        offset = X_OFFSET_OVERLAP if min_dist < threshold else X_OFFSET_NORMAL

        return i, i - offset, i + offset  # ttm_x, bsc_x, vci_x

    # Pre-calculate X positions for all stocks
    x_positions = [
        calc_x_offsets(i, current_vals[i], bsc_2026_vals[i], vci_2026_vals[i])
        for i in range(len(symbols))
    ]

    # Status colors
    status_colors = {
        'Very Cheap': '#22C55E',
        'Cheap': '#86EFAC',
        'Fair': '#FFC132',
        'Expensive': '#FB923C',
        'Very Expensive': '#EF4444'
    }

    fig = go.Figure()

    # Use numeric x-axis for precise positioning
    x_indices = list(range(len(symbols)))

    # Whiskers (P5-P95)
    fig.add_trace(go.Scatter(
        x=x_indices,
        y=[(p5 + p95) / 2 for p5, p95 in zip(p5_vals, p95_vals)],
        mode='markers',
        marker=dict(size=0.1, color='rgba(0,0,0,0)'),
        error_y=dict(
            type='data',
            symmetric=False,
            array=[(p95 - (p5 + p95) / 2) for p5, p95 in zip(p5_vals, p95_vals)],
            arrayminus=[((p5 + p95) / 2 - p5) for p5, p95 in zip(p5_vals, p95_vals)],
            color='rgba(148, 163, 184, 0.5)',
            thickness=1.5,
            width=4
        ),
        showlegend=False,
        hoverinfo='skip'
    ))

    # Box body (P25-P75)
    box_colors = [status_colors.get(s, '#6B7280') for s in statuses]
    fig.add_trace(go.Bar(
        x=x_indices,
        y=[p75 - p25 for p25, p75 in zip(p25_vals, p75_vals)],
        base=p25_vals,
        marker=dict(color=box_colors, opacity=0.6),
        width=0.6,
        name='P25-P75 Range',
        hovertemplate='<b>%{customdata[0]}</b><br>P25: %{base:.1f}x<br>P75: %{customdata[1]:.1f}x<extra></extra>',
        customdata=list(zip(symbols, p75_vals))
    ))

    # TTM markers - horizontal white line on box (centered)
    fig.add_trace(go.Scatter(
        x=x_indices,
        y=current_vals,
        mode='markers',
        name=f'{metric} TTM',
        marker=dict(
            symbol='line-ew',  # Horizontal line
            size=18,
            color='white',
            line=dict(color='white', width=3)
        ),
        hovertemplate='<b>%{customdata}</b><br>' + f'{metric} TTM: ' + '%{y:.1f}x<extra></extra>',
        customdata=symbols
    ))

    # BSC 2026F markers - diamond, dynamic offset left
    bsc_x, bsc_y, bsc_hover = [], [], []
    for i, (sym, fwd) in enumerate(zip(symbols, bsc_2026_vals)):
        if fwd is not None and fwd > 0:
            _, bsc_offset_x, _ = x_positions[i]  # Use pre-calculated offset
            bsc_x.append(bsc_offset_x)
            bsc_y.append(fwd)
            trailing = current_vals[i]
            change = ((fwd - trailing) / trailing * 100) if trailing > 0 else 0
            bsc_hover.append(f'{sym}: {fwd:.1f}x ({change:+.1f}%)')

    if bsc_x:
        fig.add_trace(go.Scatter(
            x=bsc_x,
            y=bsc_y,
            mode='markers',
            name=f'BSC {metric} 26F',
            marker=dict(
                symbol='diamond',
                size=11,  # Same size as VCI
                color='#A78BFA',
                line=dict(color='white', width=1.5)
            ),
            hovertemplate='<b>BSC</b> %{customdata}<extra></extra>',
            customdata=bsc_hover
        ))

    # VCI 2026F markers - triangle, dynamic offset right
    vci_x, vci_y, vci_hover = [], [], []
    for i, (sym, fwd) in enumerate(zip(symbols, vci_2026_vals)):
        if fwd is not None and fwd > 0:
            _, _, vci_offset_x = x_positions[i]  # Use pre-calculated offset
            vci_x.append(vci_offset_x)
            vci_y.append(fwd)
            trailing = current_vals[i]
            change = ((fwd - trailing) / trailing * 100) if trailing > 0 else 0
            vci_hover.append(f'{sym}: {fwd:.1f}x ({change:+.1f}%)')

    if vci_x:
        fig.add_trace(go.Scatter(
            x=vci_x,
            y=vci_y,
            mode='markers',
            name=f'VCI {metric} 26F',
            marker=dict(
                symbol='triangle-up',
                size=11,  # Same size as BSC
                color='#F472B6',
                line=dict(color='white', width=1.5)
            ),
            hovertemplate='<b>VCI</b> %{customdata}<extra></extra>',
            customdata=vci_hover
        ))

    # Layout
    fig.update_layout(
        title=dict(
            text=f'{selected_sector}: {metric} Historical vs Forward 2026',
            font=dict(size=16, color='#E8E8E8')
        ),
        xaxis=dict(
            title='',
            tickmode='array',
            tickvals=x_indices,
            ticktext=symbols,
            tickangle=-45,
            tickfont=dict(size=10, color='#94A3B8'),
            gridcolor='rgba(148, 163, 184, 0.1)'
        ),
        yaxis=dict(
            title=f'{metric} Ratio',
            tickfont=dict(size=11, color='#94A3B8'),
            gridcolor='rgba(148, 163, 184, 0.1)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=11, color='#E8E8E8')
        ),
        margin=dict(l=50, r=30, t=80, b=80),
        bargap=0.3
    )

    return fig


def render_sector_tab(sector_df: pd.DataFrame, individual_df: pd.DataFrame, service):
    """
    Render Sector tab: Chart on top, Table below.

    Args:
        sector_df: Sector aggregated DataFrame
        individual_df: Individual stocks DataFrame (for chart)
        service: ForecastService instance
    """
    st.markdown("### Sector Forward Valuation")

    if sector_df.empty:
        st.warning("No sector data available.")
        return

    # === CHART SECTION (TOP) ===
    # Sector and metric filter
    col1, col2, col3 = st.columns([2, 1, 2])

    sectors = sorted(sector_df['sector'].dropna().unique().tolist())
    sectors = [s for s in sectors if s != 'BSC Universal']

    with col1:
        selected_sector = st.selectbox("Sector", sectors, key="sector_chart_filter")
    with col2:
        metric = st.radio("Metric", ["PE", "PB"], horizontal=True, key="sector_chart_metric")

    # Render Valuation Matrix chart
    try:
        from WEBAPP.services.valuation_service import ValuationService
        val_service = ValuationService()

        stats_data = val_service.get_industry_candle_data(selected_sector, metric=metric)

        if stats_data:
            # Get forward 2026 values from BSC
            bsc_fwd_2026 = {}
            vci_fwd_2026 = {}

            if not individual_df.empty:
                sector_stocks = individual_df[individual_df['sector'] == selected_sector]
                if metric == "PE":
                    bsc_fwd_2026 = dict(zip(sector_stocks['symbol'], sector_stocks['pe_fwd_2026']))
                else:
                    bsc_fwd_2026 = dict(zip(sector_stocks['symbol'], sector_stocks['pb_fwd_2026']))

            # Get VCI data
            try:
                comparison_df = service.get_bsc_vs_vci_comparison()
                if not comparison_df.empty:
                    vci_sector = comparison_df[comparison_df['sector'] == selected_sector]
                    if metric == "PE" and 'vci_pe_2026' in comparison_df.columns:
                        vci_fwd_2026 = dict(zip(vci_sector['symbol'], vci_sector['vci_pe_2026']))
                    elif metric == "PB" and 'vci_pb_2026' in comparison_df.columns:
                        vci_fwd_2026 = dict(zip(vci_sector['symbol'], vci_sector['vci_pb_2026']))
                    else:
                        vci_fwd_2026 = {}
            except Exception:
                vci_fwd_2026 = {}

            fig = render_valuation_matrix(stats_data, bsc_fwd_2026, selected_sector, metric, vci_fwd_2026)
            st.plotly_chart(fig, width='stretch')

            # Compact legend
            st.caption(f"━ {metric} TTM | ◆ BSC 26F (trái) | △ VCI 26F (phải) | Box: P25-P75")
        else:
            st.info(f"No historical {metric} data for {selected_sector}.")

    except Exception as e:
        st.error(f"Failed to load valuation data: {e}")

    # === TABLE SECTION (BOTTOM) ===
    st.markdown("---")
    st.markdown("#### All Sectors Summary")

    # Calculate BSC Universal aggregate row
    total_stocks = sector_df['symbol_count'].sum()
    total_mktcap = sector_df['total_market_cap'].sum()
    total_rev_25 = sector_df['total_rev_2025f'].sum() if 'total_rev_2025f' in sector_df.columns else 0
    total_rev_26 = sector_df['total_rev_2026f'].sum() if 'total_rev_2026f' in sector_df.columns else 0
    total_npatmi_25 = sector_df['total_npatmi_2025f'].sum() if 'total_npatmi_2025f' in sector_df.columns else 0
    total_npatmi_26 = sector_df['total_npatmi_2026f'].sum() if 'total_npatmi_2026f' in sector_df.columns else 0

    # Weighted average PE/PB (by market cap)
    weights = sector_df['total_market_cap'] / total_mktcap
    avg_pe_25 = (sector_df['pe_fwd_2025'] * weights).sum()
    avg_pe_26 = (sector_df['pe_fwd_2026'] * weights).sum()
    avg_pb_25 = (sector_df['pb_fwd_2025'] * weights).sum()
    avg_upside = sector_df['avg_upside_pct'].mean()

    # Growth rates for BSC Universal
    rev_growth_26 = (total_rev_26 - total_rev_25) / total_rev_25 if total_rev_25 > 0 else 0
    npatmi_growth_26 = (total_npatmi_26 - total_npatmi_25) / total_npatmi_25 if total_npatmi_25 > 0 else 0

    # Create BSC Universal row
    bsc_universal = pd.DataFrame([{
        'sector': 'BSC Universal',
        'symbol_count': total_stocks,
        'total_market_cap': total_mktcap,
        'total_rev_2025f': total_rev_25,
        'total_rev_2026f': total_rev_26,
        'total_npatmi_2025f': total_npatmi_25,
        'total_npatmi_2026f': total_npatmi_26,
        'pe_fwd_2025': avg_pe_25,
        'pe_fwd_2026': avg_pe_26,
        'pb_fwd_2025': avg_pb_25,
        'avg_upside_pct': avg_upside,
        'avg_rev_growth_2026': rev_growth_26,
        'avg_npatmi_growth_2026': npatmi_growth_26,
    }])

    # Prepend BSC Universal row
    display_df = pd.concat([bsc_universal, sector_df], ignore_index=True)

    # Build display table with core + extended columns
    sector_display = pd.DataFrame()
    sector_display['Sector'] = display_df['sector']
    sector_display['Stocks'] = display_df['symbol_count'].astype(int)
    sector_display['Mkt Cap'] = display_df['total_market_cap'].apply(format_market_cap)

    # Core metrics: NPATMI (25F, 26F, Growth), PE, Upside
    sector_display['NPATMI 25F'] = display_df['total_npatmi_2025f'].apply(lambda x: format_market_cap(x) if pd.notna(x) else '-')
    sector_display['NPATMI 26F'] = display_df['total_npatmi_2026f'].apply(lambda x: format_market_cap(x) if pd.notna(x) else '-')
    sector_display['Δ NPATMI'] = display_df['avg_npatmi_growth_2026'].apply(format_growth)
    sector_display['PE 25F'] = display_df['pe_fwd_2025'].apply(lambda x: format_number(x, 1, 'x'))
    sector_display['PE 26F'] = display_df['pe_fwd_2026'].apply(lambda x: format_number(x, 1, 'x'))
    sector_display['Upside'] = display_df['avg_upside_pct'].apply(format_upside)

    # Extended metrics: Revenue
    sector_display['Rev 25F'] = display_df['total_rev_2025f'].apply(lambda x: format_market_cap(x) if pd.notna(x) else '-')
    sector_display['Rev 26F'] = display_df['total_rev_2026f'].apply(lambda x: format_market_cap(x) if pd.notna(x) else '-')
    sector_display['Δ Rev'] = display_df['avg_rev_growth_2026'].apply(format_growth)

    st.markdown(f"**{len(sector_df)} sectors + BSC Universal**")
    st.markdown(
        render_styled_table(sector_display, highlight_first_col=True, highlight_row='BSC Universal'),
        unsafe_allow_html=True
    )
