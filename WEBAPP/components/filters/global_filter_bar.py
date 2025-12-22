"""
Global Filter Bar Component
===========================
Horizontal filter bar for chart-first dashboards.
Replaces sidebar filters with sticky top bar.

Usage:
    from WEBAPP.components.filters.global_filter_bar import render_global_filters

    filters = render_global_filters(
        show_metric=True,
        show_time_range=True
    )
    metric = filters['metric']
    days = filters['days']

Created: 2025-12-21
"""

import streamlit as st
from typing import Dict, List, Optional

# ============================================================================
# CONSTANTS
# ============================================================================
METRIC_OPTIONS = ["PE", "PB", "P/S Ratio", "EV/EBITDA"]
METRIC_MAP = {
    "PE": "pe_ttm",  # Column name remains pe_ttm for data compatibility
    "PB": "pb",
    "P/S Ratio": "ps",
    "EV/EBITDA": "ev_ebitda"
}

TIME_RANGE_OPTIONS = {
    "3M": 63,
    "6M": 126,
    "1Y": 252,
    "3Y": 756,
    "5Y": 1260,
    "ALL": 2000
}


def render_global_filters(
    show_metric: bool = True,
    show_time_range: bool = True,
    show_ticker_search: bool = False,
    show_refresh: bool = True,
    show_export: bool = False,
    key_prefix: str = "global",
    metric_options: Optional[List[str]] = None,
    default_metric: str = "PE",
    default_time_range: str = "3Y"
) -> Dict:
    """
    Render horizontal filter bar at top of page.

    Args:
        show_metric: Show valuation metric selector
        show_time_range: Show time range selector
        show_ticker_search: Show ticker search input
        show_refresh: Show refresh button
        show_export: Show export button
        key_prefix: Prefix for session_state keys
        metric_options: Custom metric options (defaults to METRIC_OPTIONS)
        default_metric: Default metric selection
        default_time_range: Default time range selection

    Returns:
        Dict with filter values:
        {
            'metric': str,  # Display name ("PE")
            'metric_col': str,  # Column name ("pe_ttm")
            'days': int,  # Trading days
            'ticker': str,  # Ticker search value
            'refresh': bool  # Refresh button clicked
        }
    """
    result = {}
    metrics = metric_options or METRIC_OPTIONS

    # Initialize session state
    if f'{key_prefix}_metric' not in st.session_state:
        st.session_state[f'{key_prefix}_metric'] = default_metric
    if f'{key_prefix}_time_range' not in st.session_state:
        st.session_state[f'{key_prefix}_time_range'] = default_time_range

    # Calculate column weights for balanced layout
    # Metric: 2, Time: 1.5, Ticker: 2, Refresh: 1, Export: 1
    col_specs = []
    if show_metric:
        col_specs.append(2)
    if show_time_range:
        col_specs.append(1.5)
    if show_ticker_search:
        col_specs.append(2)
    if show_refresh:
        col_specs.append(1)
    if show_export:
        col_specs.append(1)

    if not col_specs:
        return result

    # Create columns
    cols = st.columns(col_specs)
    col_idx = 0

    # Metric selector
    if show_metric:
        with cols[col_idx]:
            current_metric = st.session_state.get(f'{key_prefix}_metric', default_metric)
            metric_index = metrics.index(current_metric) if current_metric in metrics else 0
            selected_metric = st.selectbox(
                "Metric",
                metrics,
                index=metric_index,
                key=f'{key_prefix}_metric_select',
                label_visibility="collapsed",
                help="Select valuation metric"
            )
            st.session_state[f'{key_prefix}_metric'] = selected_metric
            result['metric'] = selected_metric
            result['metric_col'] = METRIC_MAP.get(selected_metric, "pe_ttm")
        col_idx += 1

    # Time range selector
    if show_time_range:
        with cols[col_idx]:
            time_options = list(TIME_RANGE_OPTIONS.keys())
            current_range = st.session_state.get(f'{key_prefix}_time_range', default_time_range)
            range_index = time_options.index(current_range) if current_range in time_options else 3
            selected_range = st.selectbox(
                "Time Range",
                time_options,
                index=range_index,
                key=f'{key_prefix}_time_range_select',
                label_visibility="collapsed",
                help="Select time range"
            )
            st.session_state[f'{key_prefix}_time_range'] = selected_range
            result['days'] = TIME_RANGE_OPTIONS[selected_range]
            result['time_range'] = selected_range
        col_idx += 1

    # Ticker search
    if show_ticker_search:
        with cols[col_idx]:
            ticker = st.text_input(
                "Ticker",
                placeholder="Enter ticker (VCB, ACB...)",
                key=f'{key_prefix}_ticker_input',
                label_visibility="collapsed"
            )
            result['ticker'] = ticker.upper().strip()
        col_idx += 1

    # Refresh button
    if show_refresh:
        with cols[col_idx]:
            if st.button("Refresh", key=f'{key_prefix}_refresh', use_container_width=True, type="secondary"):
                st.cache_data.clear()
                result['refresh'] = True
            else:
                result['refresh'] = False
        col_idx += 1

    # Export button
    if show_export:
        with cols[col_idx]:
            result['export'] = st.button(
                "Export",
                key=f'{key_prefix}_export',
                use_container_width=True,
                type="secondary"
            )

    return result


def get_filter_state(key_prefix: str = "global") -> Dict:
    """
    Get current filter state from session_state.
    Use when filters were rendered earlier in the page.

    Returns:
        Dict with metric, metric_col, days
    """
    metric = st.session_state.get(f'{key_prefix}_metric', "PE")
    time_range = st.session_state.get(f'{key_prefix}_time_range', "3Y")

    return {
        'metric': metric,
        'metric_col': METRIC_MAP.get(metric, "pe_ttm"),
        'days': TIME_RANGE_OPTIONS.get(time_range, 756),
        'time_range': time_range
    }


def render_compact_filter_row(
    options: Dict[str, List],
    key_prefix: str = "compact"
) -> Dict:
    """
    Render a compact inline filter row using pills/chips style.

    Args:
        options: Dict of filter name -> list of options
        key_prefix: Prefix for session state keys

    Returns:
        Dict of filter name -> selected value
    """
    result = {}
    cols = st.columns(len(options))

    for idx, (name, opts) in enumerate(options.items()):
        with cols[idx]:
            selected = st.radio(
                name,
                opts,
                key=f'{key_prefix}_{name}_radio',
                horizontal=True,
                label_visibility="collapsed"
            )
            result[name] = selected

    return result
