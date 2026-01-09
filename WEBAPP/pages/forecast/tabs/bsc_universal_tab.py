"""
BSC Universal Tab
=================
Tab 0: Unified stock forecast table with all metrics.

Replaces the old Individual tab with Valuation/Earnings sub-tabs.
Now shows single unified table with optional extended columns toggle.
Filter bar is rendered inside this tab for easier interaction.
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from typing import List

from WEBAPP.components.tables.unified_forecast_table import (
    unified_forecast_table,
    render_column_legend
)
from WEBAPP.components.filters.forecast_filter_bar import (
    render_filter_bar,
    apply_filters,
    apply_sort,
    render_rating_badges,
    SORT_OPTIONS,
    WATCHLIST_PRESETS
)


def render_bsc_universal_tab(
    df: pd.DataFrame,
    service,
    sectors_list: List[str] = None
):
    """
    Render BSC Universal tab with unified forecast table.

    Args:
        df: Individual stocks DataFrame
        service: ForecastService instance
        sectors_list: List of available sectors for filter
    """
    st.markdown("### BSC Universal Stock Table")
    st.markdown("*92 stocks with unified view: Valuation + Earnings + Extended metrics*")

    # Filter bar inside tab (below tab header)
    filters = render_filter_bar(
        tab_id=0,
        sectors=sectors_list or [],
        show_ticker_search=True,
        show_sector=True,
        show_watchlist=True,
        show_rating=True,
        show_sort=True,
        sort_options=SORT_OPTIONS['stock'],
        show_extended_toggle=True,
        show_consensus_filter=False,
        key_prefix='bsc_universal'
    )

    # Extract filter values
    ticker_search = filters.get('ticker_search', '')
    sector_filter = filters.get('sector', 'All')
    watchlist_filter = filters.get('watchlist', 'All')
    rating_filter = filters.get('rating', 'All')
    sort_by = filters.get('sort', 'upside_desc')
    show_extended = filters.get('show_extended', False)

    # Apply filters
    filtered_df = df.copy()

    # Watchlist filter (apply first)
    if watchlist_filter != 'All':
        watchlist_tickers = WATCHLIST_PRESETS.get(watchlist_filter, [])
        if watchlist_tickers:
            filtered_df = filtered_df[filtered_df['symbol'].isin(watchlist_tickers)].copy()

    # Ticker search filter (exact or partial match)
    if ticker_search:
        filtered_df = filtered_df[
            filtered_df['symbol'].str.upper().str.contains(ticker_search, na=False)
        ]

    if rating_filter and rating_filter != 'All':
        filtered_df = filtered_df[filtered_df['rating'] == rating_filter]

    if sector_filter != 'All':
        filtered_df = filtered_df[filtered_df['sector'] == sector_filter]

    # Calculate deltas if not present (for sorting)
    if 'pe_delta' not in filtered_df.columns and 'pe_fwd_2025' in filtered_df.columns:
        filtered_df['pe_delta'] = ((filtered_df['pe_fwd_2026'] - filtered_df['pe_fwd_2025']) / filtered_df['pe_fwd_2025'] * 100).where(
            filtered_df['pe_fwd_2025'] > 0, None
        )
    if 'pb_delta' not in filtered_df.columns and 'pb_fwd_2025' in filtered_df.columns:
        filtered_df['pb_delta'] = ((filtered_df['pb_fwd_2026'] - filtered_df['pb_fwd_2025']) / filtered_df['pb_fwd_2025'] * 100).where(
            filtered_df['pb_fwd_2025'] > 0, None
        )

    # Apply sorting
    sort_mapping = {
        'upside_desc': ('upside_pct', False),
        'upside_asc': ('upside_pct', True),
        'pe_25_desc': ('pe_fwd_2025', False),
        'pe_25_asc': ('pe_fwd_2025', True),
        'pe_26_desc': ('pe_fwd_2026', False),
        'pe_delta_asc': ('pe_delta', True),  # Ascending = most improving (negative delta)
        'pb_25_desc': ('pb_fwd_2025', False),
        'pb_25_asc': ('pb_fwd_2025', True),
        'pb_26_desc': ('pb_fwd_2026', False),
        'pb_delta_asc': ('pb_delta', True),  # Ascending = most improving (negative delta)
        'growth_desc': ('npatmi_growth_yoy_2026', False),
        'mcap_desc': ('market_cap', False),
        'sector_asc': ('sector', True),   # A-Z
        'sector_desc': ('sector', False),  # Z-A
    }

    if sort_by in sort_mapping:
        col, asc = sort_mapping[sort_by]
        if col in filtered_df.columns:
            filtered_df = filtered_df.sort_values(col, ascending=asc, na_position='last')

    # Rating badges summary - st.html() for complex HTML (function always returns valid HTML)
    st.html(render_rating_badges(filtered_df))

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
