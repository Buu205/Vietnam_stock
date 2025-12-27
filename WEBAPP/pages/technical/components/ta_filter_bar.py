"""
TA Dashboard Filter Bar
=======================
Horizontal filter bar specialized for Technical Analysis dashboard.
Compact, sticky top bar with mode selector, timeframe, and sector filter.

Usage:
    from WEBAPP.pages.technical.components.ta_filter_bar import render_ta_filters

    filters = render_ta_filters(service)
    timeframe = filters['timeframe']
    sector = filters['sector']

Created: 2025-12-25
"""

import streamlit as st
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..services.ta_dashboard_service import TADashboardService

# ============================================================================
# CONSTANTS
# ============================================================================

TIMEFRAME_OPTIONS = {
    "30D": 30,
    "60D": 60,
    "90D": 90,
    "180D": 180,
    "1Y": 252,
}

SIGNAL_TYPES = {
    "all": "All Signals",
    "ma_crossover": "MA Cross",
    "volume_spike": "Volume",
    "breakout": "Breakout",
    "patterns": "Patterns",
}


def render_ta_filters(
    service: 'TADashboardService',
    show_timeframe: bool = True,
    show_sector: bool = True,
    show_signal_type: bool = False,
    show_search: bool = False,
    show_refresh: bool = True,
    key_prefix: str = "ta"
) -> Dict:
    """
    Render horizontal filter bar for TA Dashboard.

    Args:
        service: TADashboardService instance for sector list
        show_timeframe: Show timeframe selector
        show_sector: Show sector filter
        show_signal_type: Show signal type filter
        show_search: Show symbol search input
        show_refresh: Show refresh button
        key_prefix: Prefix for session_state keys

    Returns:
        Dict with filter values:
        {
            'timeframe': str,      # "30D", "60D", etc.
            'days': int,           # Trading days count
            'sector': str,         # Selected sector or "All"
            'signal_type': str,    # Signal type key
            'search': str,         # Symbol search value
            'refresh': bool        # Refresh button clicked
        }
    """
    result = {}

    # Initialize session state
    if f'{key_prefix}_timeframe' not in st.session_state:
        st.session_state[f'{key_prefix}_timeframe'] = "180D"
    if f'{key_prefix}_sector' not in st.session_state:
        st.session_state[f'{key_prefix}_sector'] = "All"
    if f'{key_prefix}_signal_type' not in st.session_state:
        st.session_state[f'{key_prefix}_signal_type'] = "all"

    # Calculate column weights
    col_specs = []
    if show_timeframe:
        col_specs.append(1.2)
    if show_sector:
        col_specs.append(1.5)
    if show_signal_type:
        col_specs.append(1.2)
    if show_search:
        col_specs.append(2)
    if show_refresh:
        col_specs.append(0.8)

    if not col_specs:
        return result

    # Create columns
    cols = st.columns(col_specs)
    col_idx = 0

    # Timeframe selector
    if show_timeframe:
        with cols[col_idx]:
            time_options = list(TIMEFRAME_OPTIONS.keys())
            current_tf = st.session_state.get(f'{key_prefix}_timeframe', "180D")
            tf_index = time_options.index(current_tf) if current_tf in time_options else 3
            selected_tf = st.selectbox(
                "Timeframe",
                time_options,
                index=tf_index,
                key=f'{key_prefix}_timeframe_select',
                label_visibility="collapsed",
                help="Select analysis timeframe"
            )
            st.session_state[f'{key_prefix}_timeframe'] = selected_tf
            result['timeframe'] = selected_tf
            result['days'] = TIMEFRAME_OPTIONS[selected_tf]
        col_idx += 1

    # Sector filter
    if show_sector:
        with cols[col_idx]:
            sectors = ["All"] + service.get_sector_list()
            current_sector = st.session_state.get(f'{key_prefix}_sector', "All")
            sector_index = sectors.index(current_sector) if current_sector in sectors else 0
            selected_sector = st.selectbox(
                "Sector",
                sectors,
                index=sector_index,
                key=f'{key_prefix}_sector_select',
                label_visibility="collapsed",
                help="Filter by sector"
            )
            st.session_state[f'{key_prefix}_sector'] = selected_sector
            result['sector'] = selected_sector
        col_idx += 1

    # Signal type filter
    if show_signal_type:
        with cols[col_idx]:
            signal_options = list(SIGNAL_TYPES.keys())
            current_signal = st.session_state.get(f'{key_prefix}_signal_type', "all")
            signal_index = signal_options.index(current_signal) if current_signal in signal_options else 0
            selected_signal = st.selectbox(
                "Signal Type",
                signal_options,
                index=signal_index,
                format_func=lambda x: SIGNAL_TYPES[x],
                key=f'{key_prefix}_signal_type_select',
                label_visibility="collapsed",
                help="Filter by signal type"
            )
            st.session_state[f'{key_prefix}_signal_type'] = selected_signal
            result['signal_type'] = selected_signal
        col_idx += 1

    # Symbol search
    if show_search:
        with cols[col_idx]:
            search = st.text_input(
                "Search",
                placeholder="VCB, ACB, FPT...",
                key=f'{key_prefix}_search_input',
                label_visibility="collapsed"
            )
            result['search'] = search.upper().strip() if search else ""
        col_idx += 1

    # Refresh button
    if show_refresh:
        with cols[col_idx]:
            if st.button("Refresh", key=f'{key_prefix}_refresh', use_container_width=True, type="secondary"):
                st.cache_data.clear()
                result['refresh'] = True
            else:
                result['refresh'] = False

    return result


def render_mode_toggle(key_prefix: str = "ta") -> str:
    """
    Render mode toggle (Sector vs Stock) as pills.

    Returns:
        Selected mode: "Sector" or "Stock"
    """
    if f'{key_prefix}_mode' not in st.session_state:
        st.session_state[f'{key_prefix}_mode'] = "Sector"

    mode = st.radio(
        "Mode",
        ["Sector", "Stock"],
        horizontal=True,
        key=f'{key_prefix}_mode_radio',
        label_visibility="collapsed"
    )
    st.session_state[f'{key_prefix}_mode'] = mode
    return mode


def render_watchlist_selector(key_prefix: str = "ta") -> str:
    """
    Render watchlist dropdown for Stock mode.

    Returns:
        Selected watchlist name
    """
    from ..components.sector_rotation import WATCHLISTS

    if f'{key_prefix}_watchlist' not in st.session_state:
        st.session_state[f'{key_prefix}_watchlist'] = "BSC Universe"

    watchlist_options = list(WATCHLISTS.keys())
    current = st.session_state.get(f'{key_prefix}_watchlist', "BSC Universe")
    index = watchlist_options.index(current) if current in watchlist_options else 0

    selected = st.selectbox(
        "Watchlist",
        watchlist_options,
        index=index,
        key=f'{key_prefix}_watchlist_select',
        label_visibility="collapsed"
    )
    st.session_state[f'{key_prefix}_watchlist'] = selected
    return selected


def get_ta_filter_state(key_prefix: str = "ta") -> Dict:
    """
    Get current filter state from session_state.
    Use when filters were rendered earlier in the page.

    Returns:
        Dict with timeframe, days, sector, signal_type
    """
    timeframe = st.session_state.get(f'{key_prefix}_timeframe', "180D")
    sector = st.session_state.get(f'{key_prefix}_sector', "All")
    signal_type = st.session_state.get(f'{key_prefix}_signal_type', "all")
    mode = st.session_state.get(f'{key_prefix}_mode', "Sector")

    return {
        'timeframe': timeframe,
        'days': TIMEFRAME_OPTIONS.get(timeframe, 180),
        'sector': sector,
        'signal_type': signal_type,
        'mode': mode
    }
