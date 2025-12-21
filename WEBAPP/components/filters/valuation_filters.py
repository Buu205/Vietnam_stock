"""
Sidebar Filter Components
=========================
Reusable filters for valuation pages.

Provides consistent filter UI across sector, valuation, and forecast dashboards.

Usage:
    from WEBAPP.components.filters.valuation_filters import (
        metric_selector,
        time_range_selector,
        sector_selector,
        ticker_search,
        render_sidebar_filters
    )

    # In sidebar
    metric = metric_selector()
    days = time_range_selector()
    sector = sector_selector(sectors_list)
"""

import streamlit as st
from typing import List, Optional, Dict, Tuple


# =============================================================================
# TIME RANGE OPTIONS
# =============================================================================
TIME_RANGE_OPTIONS = {
    "3M": 63,
    "6M": 126,
    "1Y": 252,
    "3Y": 756,
    "5Y": 1260,
    "ALL": 2000
}


# =============================================================================
# METRIC SELECTOR
# =============================================================================
def metric_selector(
    key: str = "metric",
    default: str = "PE TTM",
    include_ev: bool = True,
    location: str = "sidebar"
) -> str:
    """
    Valuation metric selectbox.

    Args:
        key: Streamlit widget key
        default: Default selected option
        include_ev: Include EV/EBITDA option
        location: "sidebar" or "main" for placement

    Returns:
        Selected metric string: "PE TTM", "PB", "P/S Ratio", or "EV/EBITDA"

    Example:
        >>> metric = metric_selector(key="sector_metric")
        >>> if metric == "PE TTM":
        >>>     load_pe_data()
    """
    options = ["PE TTM", "PB", "P/S Ratio"]
    if include_ev:
        options.append("EV/EBITDA")

    default_index = options.index(default) if default in options else 0

    if location == "sidebar":
        return st.sidebar.selectbox(
            "Valuation Metric",
            options,
            index=default_index,
            key=key
        )
    else:
        return st.selectbox(
            "Valuation Metric",
            options,
            index=default_index,
            key=key
        )


def metric_to_column(metric: str) -> str:
    """
    Convert metric display name to column name.

    Args:
        metric: Display name like "PE TTM", "PB", etc.

    Returns:
        Column name like "pe_ttm", "pb", etc.
    """
    mapping = {
        "PE TTM": "pe_ttm",
        "PB": "pb",
        "P/S Ratio": "ps",
        "EV/EBITDA": "ev_ebitda"
    }
    return mapping.get(metric, "pe_ttm")


# =============================================================================
# TIME RANGE SELECTOR
# =============================================================================
def time_range_selector(
    key: str = "time_range",
    default: str = "3Y",
    location: str = "sidebar"
) -> int:
    """
    Time range selectbox.

    Args:
        key: Streamlit widget key
        default: Default selected option ("3M", "6M", "1Y", "3Y", "5Y", "ALL")
        location: "sidebar" or "main" for placement

    Returns:
        Number of trading days for selected range

    Example:
        >>> days = time_range_selector(default="1Y")
        >>> data = load_data(days_limit=days)
    """
    options = list(TIME_RANGE_OPTIONS.keys())
    default_index = options.index(default) if default in options else 3

    if location == "sidebar":
        selected = st.sidebar.selectbox(
            "Time Range",
            options,
            index=default_index,
            key=key
        )
    else:
        selected = st.selectbox(
            "Time Range",
            options,
            index=default_index,
            key=key
        )

    return TIME_RANGE_OPTIONS[selected]


# =============================================================================
# SECTOR SELECTOR
# =============================================================================
def sector_selector(
    sectors: List[str],
    key: str = "sector",
    default: str = None,
    include_all: bool = False,
    location: str = "sidebar"
) -> str:
    """
    Sector selectbox with all available sectors.

    Args:
        sectors: List of sector names
        key: Streamlit widget key
        default: Default selected sector (if None, uses first)
        include_all: Add "All Sectors" option at top
        location: "sidebar" or "main" for placement

    Returns:
        Selected sector name

    Example:
        >>> sectors = sector_service.get_all_sectors()
        >>> sector = sector_selector(sectors)
        >>> data = sector_service.get_sector_data(sector)
    """
    if not sectors:
        sectors = ["No sectors available"]

    options = sectors.copy()
    if include_all:
        options = ["All Sectors"] + options

    default_index = 0
    if default and default in options:
        default_index = options.index(default)

    if location == "sidebar":
        return st.sidebar.selectbox(
            "Select Sector",
            options,
            index=default_index,
            key=key
        )
    else:
        return st.selectbox(
            "Select Sector",
            options,
            index=default_index,
            key=key
        )


# =============================================================================
# TICKER SEARCH
# =============================================================================
def ticker_search(
    key: str = "ticker_search",
    placeholder: str = "VCB, ACB...",
    location: str = "sidebar"
) -> str:
    """
    Ticker search input with autocomplete hint.

    Args:
        key: Streamlit widget key
        placeholder: Placeholder text
        location: "sidebar" or "main" for placement

    Returns:
        Entered ticker string (uppercase)

    Example:
        >>> ticker = ticker_search()
        >>> if ticker:
        >>>     data = company_service.get_company(ticker)
    """
    if location == "sidebar":
        value = st.sidebar.text_input(
            "Search Ticker",
            placeholder=placeholder,
            key=key
        )
    else:
        value = st.text_input(
            "Search Ticker",
            placeholder=placeholder,
            key=key
        )

    return value.upper().strip() if value else ""


# =============================================================================
# INDEX SELECTOR
# =============================================================================
def index_selector(
    key: str = "index",
    default: str = "VNINDEX",
    location: str = "sidebar"
) -> str:
    """
    VNIndex variant selector.

    Args:
        key: Streamlit widget key
        default: Default selected index
        location: "sidebar" or "main" for placement

    Returns:
        Selected index name: "VNINDEX", "VNINDEX_EXCLUDE", or "BSC_INDEX"

    Example:
        >>> index = index_selector()
        >>> data = valuation_service.get_vnindex_history(scope=index)
    """
    options = ["VNINDEX", "VNINDEX_EXCLUDE", "BSC_INDEX"]
    labels = {
        "VNINDEX": "VN-Index (Full)",
        "VNINDEX_EXCLUDE": "VN-Index (Exclude Outliers)",
        "BSC_INDEX": "BSC Coverage"
    }

    # Create display options
    display_options = [labels[opt] for opt in options]
    default_index = options.index(default) if default in options else 0

    if location == "sidebar":
        selected_label = st.sidebar.selectbox(
            "Index Scope",
            display_options,
            index=default_index,
            key=key
        )
    else:
        selected_label = st.selectbox(
            "Index Scope",
            display_options,
            index=default_index,
            key=key
        )

    # Map back to key
    for key_name, label in labels.items():
        if label == selected_label:
            return key_name
    return "VNINDEX"


# =============================================================================
# COMBINED SIDEBAR FILTERS
# =============================================================================
def render_sidebar_filters(
    sectors: List[str] = None,
    show_metric: bool = True,
    show_time_range: bool = True,
    show_sector: bool = False,
    show_ticker_search: bool = True,
    show_index: bool = False,
    show_refresh: bool = True,
    key_prefix: str = ""
) -> Dict[str, any]:
    """
    Render complete sidebar filter panel.

    Args:
        sectors: List of sector names (required if show_sector=True)
        show_metric: Show metric selector
        show_time_range: Show time range selector
        show_sector: Show sector selector
        show_ticker_search: Show ticker search input
        show_index: Show VNIndex variant selector
        show_refresh: Show refresh button
        key_prefix: Prefix for all widget keys

    Returns:
        Dict with selected filter values:
        {
            'metric': str,
            'time_range': int (days),
            'sector': str,
            'ticker': str,
            'index': str,
            'refresh': bool
        }

    Example:
        >>> filters = render_sidebar_filters(
        >>>     sectors=sector_list,
        >>>     show_sector=True
        >>> )
        >>> if filters['refresh']:
        >>>     st.cache_data.clear()
    """
    result = {}

    # Ticker search at top
    if show_ticker_search:
        result['ticker'] = ticker_search(key=f"{key_prefix}ticker_search")

    st.sidebar.divider()

    # Metric selector
    if show_metric:
        result['metric'] = metric_selector(key=f"{key_prefix}metric")

    # Time range
    if show_time_range:
        result['time_range'] = time_range_selector(key=f"{key_prefix}time_range")

    # Sector selector
    if show_sector and sectors:
        result['sector'] = sector_selector(sectors, key=f"{key_prefix}sector")

    # Index selector
    if show_index:
        result['index'] = index_selector(key=f"{key_prefix}index")

    st.sidebar.divider()

    # Refresh button
    if show_refresh:
        result['refresh'] = st.sidebar.button(
            "Refresh Data",
            key=f"{key_prefix}refresh",
            use_container_width=True
        )
    else:
        result['refresh'] = False

    return result


# =============================================================================
# INLINE METRIC RADIO
# =============================================================================
def metric_radio(
    key: str = "metric_radio",
    default: str = "PE TTM",
    include_ev: bool = True,
    horizontal: bool = True
) -> str:
    """
    Inline metric radio buttons (for page content, not sidebar).

    Args:
        key: Streamlit widget key
        default: Default selected option
        include_ev: Include EV/EBITDA option
        horizontal: Display horizontally

    Returns:
        Selected metric string

    Example:
        >>> metric = metric_radio(key="sector_metric_radio")
    """
    options = ["PE TTM", "PB", "P/S Ratio"]
    if include_ev:
        options.append("EV/EBITDA")

    default_index = options.index(default) if default in options else 0

    return st.radio(
        "Metric",
        options,
        index=default_index,
        key=key,
        horizontal=horizontal,
        label_visibility="collapsed"
    )


# =============================================================================
# TAB-BASED NAVIGATION
# =============================================================================
def create_tab_navigation(
    tabs: List[str],
    key: str = "tabs"
) -> str:
    """
    Create tab-style navigation.

    Args:
        tabs: List of tab names
        key: Streamlit widget key

    Returns:
        Selected tab name

    Example:
        >>> tab = create_tab_navigation(["Sectors", "VNIndex", "Stocks"])
        >>> if tab == "Sectors":
        >>>     render_sectors()
    """
    return st.radio(
        "Navigation",
        tabs,
        key=key,
        horizontal=True,
        label_visibility="collapsed"
    )
