"""
Consensus Tab
=============
Tab 3: BSC vs VCI Forecast Comparison (NEW)

Features:
- Summary cards showing consensus status distribution
- Comparison table with BSC and VCI forecasts
- Delta columns highlighting differences
- Status badges (ALIGNED, BSC_BULL, VCI_BULL)
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


def _build_summary_cards_html(summary: dict) -> str:
    """Build HTML for summary cards."""
    CARD_CONFIG = {
        'ALIGNED': {'label': 'ALIGNED', 'color': '#00C9AD', 'bg': 'rgba(0, 201, 173, 0.15)', 'desc': 'Both views aligned (<5% diff)'},
        'BSC_BULL': {'label': 'BSC BULL', 'color': '#8B5CF6', 'bg': 'rgba(139, 92, 246, 0.15)', 'desc': 'BSC more optimistic'},
        'VCI_BULL': {'label': 'VCI BULL', 'color': '#F59E0B', 'bg': 'rgba(245, 158, 11, 0.15)', 'desc': 'VCI more optimistic'},
        'ALIGNED_BEARISH': {'label': 'ALIGNED', 'color': '#64748B', 'bg': 'rgba(100, 116, 139, 0.15)', 'desc': 'Both conservative'},
    }

    cards_html = ""
    for status, config in CARD_CONFIG.items():
        count = summary.get(status, 0)
        cards_html += f'''
        <div style="background:{config['bg']};border:1px solid {config['color']}40;border-radius:8px;padding:12px 16px;min-width:120px;">
            <div style="color:{config['color']};font-weight:700;font-size:11px;margin-bottom:4px;">{config['label']}</div>
            <div style="color:{config['color']};font-size:24px;font-weight:700;font-family:monospace;">{count}</div>
            <div style="color:#64748B;font-size:10px;">{config['desc']}</div>
        </div>
        '''
    return cards_html


def render_consensus_tab(service):
    """
    Render Consensus tab with BSC vs VCI comparison.

    Args:
        service: ForecastService instance with VCI methods
    """
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
        st.markdown("""
        **Possible reasons:**
        - VCI data not loaded (`DATA/processed/forecast/vci/vci_coverage_universe.parquet`)
        - No matching tickers between BSC and VCI coverage
        """)
        return

    # Initialize year selector state
    if 'consensus_year' not in st.session_state:
        st.session_state.consensus_year = '2025F'
    selected_year = st.session_state.consensus_year

    # Prepare data based on selected year
    display_df = comparison_df.copy()
    if selected_year == "2026F":
        # Use 2026F columns
        bsc_npatmi_col = 'npatmi_2026f' if 'npatmi_2026f' in display_df.columns else 'npatmi_2025f'
        vci_npatmi_col = 'vci_npatmi_2026' if 'vci_npatmi_2026' in display_df.columns else 'vci_npatmi_2025'
    else:
        # Default: 2025F columns
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
        # Calculate status based on delta
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

        **Priority Metrics:** NPATMI > Target Price > PE/PB (derived metrics)
        """)
    else:
        st.info("No stocks match the selected filters.")
