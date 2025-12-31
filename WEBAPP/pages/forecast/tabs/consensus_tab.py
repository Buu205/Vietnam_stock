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

    # Get consensus summary
    try:
        summary = service.get_consensus_summary()
    except Exception:
        summary = {}

    # Render summary cards
    if summary:
        st.markdown(render_consensus_summary(summary), unsafe_allow_html=True)

    st.markdown("---")

    # Filter options
    col1, col2 = st.columns([2, 2])

    with col1:
        sectors = ['All'] + sorted(comparison_df['sector'].dropna().unique().tolist())
        sector_filter = st.selectbox("Filter by Sector", sectors, key="consensus_sector")

    with col2:
        status_options = ['All', 'ALIGNED', 'BSC_BULL', 'VCI_BULL']
        status_filter = st.selectbox("Filter by Status", status_options, key="consensus_status")

    # Apply filters
    filtered_df = comparison_df.copy()

    if sector_filter != 'All':
        filtered_df = filtered_df[filtered_df['sector'] == sector_filter]

    if status_filter != 'All':
        filtered_df = filtered_df[filtered_df['consensus_status'] == status_filter]

    st.markdown(f"**Showing {len(filtered_df)} overlapping stocks**")

    # Render comparison table
    if not filtered_df.empty:
        table_html = consensus_comparison_table(filtered_df, show_rating=True)
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
