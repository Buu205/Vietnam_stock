"""
Consensus Tab
=============
Tab 3: Multi-Source Forecast Comparison (BSC, VCI, SSI, HSC)

Features:
- View mode toggle: BSC vs VCI (original) | All Sources (new)
- Summary cards showing coverage per source
- Multi-source comparison table
- Standard deviation to measure consensus
"""

import streamlit as st
import pandas as pd

from WEBAPP.components.tables.consensus_table import (
    consensus_comparison_table,
    render_consensus_summary
)


def _calculate_consensus_summary(df: pd.DataFrame) -> dict:
    """Calculate consensus summary based on NPATMI delta."""
    summary = {'ALIGNED': 0, 'BSC_BULL': 0, 'VCI_BULL': 0, 'ALIGNED_BEARISH': 0}

    for _, row in df.iterrows():
        delta = row.get('npatmi_delta_pct')
        if pd.isna(delta):
            continue

        if abs(delta) < 5:
            # Within 5% = aligned
            summary['ALIGNED'] += 1
        elif delta > 0:
            # BSC higher
            summary['BSC_BULL'] += 1
        else:
            # VCI higher
            summary['VCI_BULL'] += 1

    return summary


def _build_source_coverage_cards(stats: dict) -> str:
    """Build HTML cards showing coverage per source."""
    SOURCE_COLORS = {
        'bsc': {'color': '#8B5CF6', 'bg': 'rgba(139, 92, 246, 0.15)', 'label': 'BSC'},
        'vci': {'color': '#F59E0B', 'bg': 'rgba(245, 158, 11, 0.15)', 'label': 'VCI'},
        'ssi': {'color': '#10B981', 'bg': 'rgba(16, 185, 129, 0.15)', 'label': 'SSI'},
        'hcm': {'color': '#3B82F6', 'bg': 'rgba(59, 130, 246, 0.15)', 'label': 'HSC'},
    }

    cards_html = '<div style="display:flex;gap:12px;flex-wrap:wrap;">'
    for source, s in stats.items():
        config = SOURCE_COLORS.get(source, {'color': '#64748B', 'bg': 'rgba(100, 116, 139, 0.15)', 'label': source.upper()})
        count = s.get('count', 0)
        cards_html += f'''
        <div style="background:{config['bg']};border:1px solid {config['color']}40;border-radius:8px;padding:12px 16px;min-width:100px;">
            <div style="color:{config['color']};font-weight:700;font-size:11px;margin-bottom:4px;">{config['label']}</div>
            <div style="color:{config['color']};font-size:24px;font-weight:700;font-family:monospace;">{count}</div>
            <div style="color:#64748B;font-size:10px;">stocks</div>
        </div>
        '''
    cards_html += '</div>'
    return cards_html


def _build_multi_source_table(df: pd.DataFrame, year: str) -> str:
    """Build HTML table for multi-source comparison."""
    SOURCE_COLORS = {
        'bsc': '#8B5CF6',
        'vci': '#F59E0B',
        'ssi': '#10B981',
        'hcm': '#3B82F6',
    }

    def format_npatmi(val):
        if pd.isna(val):
            return '<span style="color:#64748B;">-</span>'
        return f'{val:,.0f}'

    def format_target(val):
        if pd.isna(val):
            return '<span style="color:#64748B;">-</span>'
        return f'{val:,.0f}'

    # Build table HTML
    html = '''
    <style>
        .ms-table { width: 100%; border-collapse: collapse; font-size: 13px; }
        .ms-table th { background: #1E293B; color: #E2E8F0; padding: 10px 8px; text-align: left; border-bottom: 2px solid #334155; font-weight: 600; }
        .ms-table td { padding: 8px; border-bottom: 1px solid #334155; color: #E2E8F0; }
        .ms-table tr:hover { background: rgba(59, 130, 246, 0.1); }
        .ms-symbol { font-weight: 700; color: #F59E0B; }
        .ms-sector { color: #94A3B8; font-size: 11px; }
        .ms-count { background: #1E293B; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
    </style>
    <table class="ms-table">
        <thead>
            <tr>
                <th>Symbol</th>
                <th>Sector</th>
    '''

    # Add source columns
    for source in ['bsc', 'vci', 'ssi', 'hcm']:
        color = SOURCE_COLORS.get(source, '#64748B')
        html += f'<th style="color:{color};">{source.upper()} NPATMI</th>'
        html += f'<th style="color:{color};">{source.upper()} Target</th>'

    html += '<th>Sources</th><th>Avg NPATMI</th><th>Std Dev</th></tr></thead><tbody>'

    # Add rows
    for _, row in df.iterrows():
        html += f'''
        <tr>
            <td class="ms-symbol">{row['symbol']}</td>
            <td class="ms-sector">{row.get('sector', '-')}</td>
        '''

        for source in ['bsc', 'vci', 'ssi', 'hcm']:
            npatmi = row.get(f'{source}_npatmi')
            target = row.get(f'{source}_target')
            html += f'<td>{format_npatmi(npatmi)}</td>'
            html += f'<td>{format_target(target)}</td>'

        source_count = row.get('source_count', 0)
        avg_npatmi = row.get('avg_npatmi')
        npatmi_std = row.get('npatmi_std')

        html += f'<td><span class="ms-count">{source_count}</span></td>'
        html += f'<td>{format_npatmi(avg_npatmi)}</td>'
        html += f'<td>{format_npatmi(npatmi_std)}</td>'
        html += '</tr>'

    html += '</tbody></table>'
    return html


def render_consensus_tab(service):
    """
    Render Consensus tab with multi-source comparison.

    Args:
        service: ForecastService instance
    """
    # View mode selector
    view_mode = st.radio(
        "View Mode",
        ["BSC vs VCI", "All Sources"],
        horizontal=True,
        key="consensus_view_mode"
    )

    if view_mode == "BSC vs VCI":
        _render_bsc_vci_view(service)
    else:
        _render_multi_source_view(service)


def _render_bsc_vci_view(service):
    """Original BSC vs VCI comparison view."""
    st.markdown("### BSC vs VCI Consensus Comparison")
    st.markdown("*Compare BSC Research forecasts with VCI (VietCap) coverage*")

    # Try to load comparison data
    try:
        comparison_df = service.get_bsc_vs_vci_comparison()
    except AttributeError:
        st.warning("VCI comparison methods not available. Please update ForecastService.")
        return
    except Exception as e:
        st.error(f"Failed to load comparison data: {e}")
        return

    if comparison_df.empty:
        st.info("No overlapping coverage between BSC and VCI. Comparison not available.")
        return

    # Initialize year selector state
    if 'consensus_year' not in st.session_state:
        st.session_state.consensus_year = '2025F'
    selected_year = st.session_state.consensus_year

    # Prepare data based on selected year
    display_df = comparison_df.copy()
    if selected_year == "2026F":
        bsc_npatmi_col = 'npatmi_2026f' if 'npatmi_2026f' in display_df.columns else 'npatmi_2025f'
        vci_npatmi_col = 'vci_npatmi_2026' if 'vci_npatmi_2026' in display_df.columns else 'vci_npatmi_2025'
    else:
        bsc_npatmi_col = 'npatmi_2025f'
        vci_npatmi_col = 'vci_npatmi_2025'

    # Create standardized columns for display
    display_df['bsc_npatmi_display'] = display_df[bsc_npatmi_col] if bsc_npatmi_col in display_df.columns else pd.NA
    display_df['vci_npatmi_display'] = display_df[vci_npatmi_col] if vci_npatmi_col in display_df.columns else pd.NA

    # Recalculate NPATMI delta for selected year
    bsc_val = display_df['bsc_npatmi_display']
    vci_val = display_df['vci_npatmi_display']
    display_df['npatmi_delta_pct'] = ((bsc_val - vci_val) / vci_val * 100).where(vci_val != 0, pd.NA)

    # Get consensus summary for selected year
    summary = _calculate_consensus_summary(display_df)

    # Layout: Cards + Year selector in one row
    col_cards, col_year = st.columns([5, 1.5])

    with col_cards:
        if summary:
            st.html(render_consensus_summary(summary))

    with col_year:
        st.markdown("**Forecast Year**")
        st.radio(
            "Year",
            ["2025F", "2026F"],
            horizontal=True,
            key="consensus_year",
            label_visibility="collapsed"
        )

    st.markdown("---")

    # Filter options
    col1, col2 = st.columns([2, 2])

    with col1:
        sectors = ['All'] + sorted(display_df['sector'].dropna().unique().tolist())
        sector_filter = st.selectbox("Filter by Sector", sectors, key="consensus_sector")

    with col2:
        def get_status_from_delta(delta):
            if pd.isna(delta):
                return 'ALIGNED'
            if abs(delta) < 5:
                return 'ALIGNED'
            return 'BSC_BULL' if delta > 0 else 'VCI_BULL'

        display_df['display_status'] = display_df['npatmi_delta_pct'].apply(get_status_from_delta)
        status_options = ['All', 'ALIGNED', 'BSC_BULL', 'VCI_BULL']
        status_filter = st.selectbox("Filter by Status", status_options, key="consensus_status")

    # Apply filters
    filtered_df = display_df.copy()

    if sector_filter != 'All':
        filtered_df = filtered_df[filtered_df['sector'] == sector_filter]

    if status_filter != 'All':
        filtered_df = filtered_df[filtered_df['display_status'] == status_filter]

    st.markdown(f"**Showing {len(filtered_df)} overlapping stocks**")

    # Render comparison table with year context
    if not filtered_df.empty:
        table_html = consensus_comparison_table(filtered_df, show_rating=True, year=selected_year)
        st.markdown(table_html, unsafe_allow_html=True)

        # Legend
        st.markdown("---")
        st.markdown("""
        **Consensus Status:**
        - **ALIGNED**: BSC and VCI forecasts within 5% difference
        - **BSC BULL**: BSC more optimistic (higher NPATMI or target)
        - **VCI BULL**: VCI more optimistic (higher NPATMI or target)
        """)
    else:
        st.info("No stocks match the selected filters.")


def _render_multi_source_view(service):
    """Multi-source comparison view (BSC, VCI, SSI, HSC)."""
    st.markdown("### Multi-Source Consensus Comparison")
    st.markdown("*Compare forecasts from BSC, VCI, SSI, and HSC*")

    # Year selector
    col1, col2 = st.columns([3, 1])
    with col2:
        year = st.selectbox(
            "Forecast Year",
            ["2025F", "2026F", "2027F"],
            key="multi_source_year"
        )

    # Load coverage stats
    try:
        stats = service.get_source_coverage_stats()
    except Exception as e:
        st.error(f"Failed to load source stats: {e}")
        return

    # Show coverage cards
    st.html(_build_source_coverage_cards(stats))

    st.markdown("---")

    # Load multi-source comparison
    try:
        comparison_df = service.get_multi_source_comparison(year)
    except Exception as e:
        st.error(f"Failed to load comparison: {e}")
        return

    if comparison_df.empty:
        st.info("No overlapping coverage found. Need at least 2 sources covering the same stock.")
        return

    # Filters
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        sectors = ['All'] + sorted(comparison_df['sector'].dropna().unique().tolist())
        sector_filter = st.selectbox("Filter by Sector", sectors, key="ms_sector")

    with col2:
        min_sources = st.selectbox(
            "Min Sources",
            [2, 3, 4],
            key="ms_min_sources"
        )

    with col3:
        sort_by = st.selectbox(
            "Sort By",
            ["Source Count", "Avg NPATMI", "Std Dev (Low)"],
            key="ms_sort"
        )

    # Apply filters
    filtered_df = comparison_df.copy()

    if sector_filter != 'All':
        filtered_df = filtered_df[filtered_df['sector'] == sector_filter]

    filtered_df = filtered_df[filtered_df['source_count'] >= min_sources]

    # Sort
    if sort_by == "Source Count":
        filtered_df = filtered_df.sort_values('source_count', ascending=False)
    elif sort_by == "Avg NPATMI":
        filtered_df = filtered_df.sort_values('avg_npatmi', ascending=False)
    else:  # Std Dev (Low) = high consensus
        filtered_df = filtered_df.sort_values('npatmi_std', ascending=True)

    st.markdown(f"**Showing {len(filtered_df)} stocks with {min_sources}+ source coverage**")

    # Render table
    if not filtered_df.empty:
        table_html = _build_multi_source_table(filtered_df, year)
        st.markdown(table_html, unsafe_allow_html=True)

        # Legend
        st.markdown("---")
        st.markdown("""
        **Notes:**
        - **NPATMI**: Net Profit After Tax to Minority Interests (Billion VND)
        - **Std Dev**: Lower = higher consensus between sources
        - **Sources**: Number of research houses covering the stock
        """)
    else:
        st.info("No stocks match the selected filters.")
