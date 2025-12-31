"""
BSC Universal Tab
=================
Tab 0: Unified stock forecast table with all metrics.

Replaces the old Individual tab with Valuation/Earnings sub-tabs.
Now shows single unified table with optional extended columns toggle.
"""

import streamlit as st
import pandas as pd
from io import BytesIO

from WEBAPP.components.tables.unified_forecast_table import (
    unified_forecast_table,
    render_column_legend
)
from WEBAPP.components.filters.forecast_filter_bar import (
    render_filter_bar,
    apply_filters,
    apply_sort,
    render_rating_badges,
    SORT_OPTIONS
)


def render_bsc_universal_tab(
    df: pd.DataFrame,
    service,
    rating_filter: list = None,
    sector_filter: str = 'All',
    sort_by: str = 'upside_desc'
):
    """
    Render BSC Universal tab with unified forecast table.

    Args:
        df: Individual stocks DataFrame
        service: ForecastService instance
        rating_filter: Selected ratings filter
        sector_filter: Selected sector filter
        sort_by: Sort column and direction
    """
    st.markdown("### BSC Universal Stock Table")
    st.markdown("*92 stocks with unified view: Valuation + Earnings + Extended metrics*")

    # Apply filters
    filtered_df = df.copy()

    if rating_filter:
        filtered_df = filtered_df[filtered_df['rating'].isin(rating_filter)]

    if sector_filter != 'All':
        filtered_df = filtered_df[filtered_df['sector'] == sector_filter]

    # Apply sorting
    sort_mapping = {
        'upside_desc': ('upside_pct', False),
        'upside_asc': ('upside_pct', True),
        'pe_desc': ('pe_fwd_2025', False),
        'pe_asc': ('pe_fwd_2025', True),
        'growth_desc': ('npatmi_growth_yoy_2026', False),
        'mcap_desc': ('market_cap', False),
    }

    if sort_by in sort_mapping:
        col, asc = sort_mapping[sort_by]
        if col in filtered_df.columns:
            filtered_df = filtered_df.sort_values(col, ascending=asc, na_position='last')

    # Rating badges summary
    st.markdown(render_rating_badges(filtered_df), unsafe_allow_html=True)

    # Extended toggle
    show_extended = st.toggle("Show Extended Columns", key="bsc_show_extended", value=False)

    st.markdown(f"**Showing {len(filtered_df)} stocks**")

    if not filtered_df.empty:
        # Render column legend
        st.markdown(render_column_legend(), unsafe_allow_html=True)

        # Render unified table
        table_html = unified_forecast_table(filtered_df, show_extended=show_extended)
        st.markdown(table_html, unsafe_allow_html=True)

        # Download button
        st.markdown("---")
        all_cols = [c for c in df.columns if c != 'updated_at']
        raw_download = filtered_df[all_cols].copy()

        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            raw_download.to_excel(writer, index=False, sheet_name='BSC Universal')
        excel_data = excel_buffer.getvalue()

        st.download_button(
            "Download Full Data (Excel)",
            excel_data,
            "bsc_forecast_universal.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("No stocks match the selected filters.")
