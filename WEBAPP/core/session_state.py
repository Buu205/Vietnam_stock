"""
Session State Configuration
===========================

Centralized session state initialization for all dashboard pages.
Prevents widget interactions from causing page resets.

Usage:
    from WEBAPP.core.session_state import init_page_state

    # At the top of each dashboard page:
    init_page_state('company')  # or 'bank', 'technical', etc.

Author: Claude Code
Date: 2025-12-25
"""

import streamlit as st
from typing import Dict, Any, Optional


# Default state values for each page
# Tab indices: 0-based, persisted across widget interactions
PAGE_STATE_DEFAULTS: Dict[str, Dict[str, Any]] = {
    'global': {
        'global_ticker_search': '',
        'quick_search_ticker': None,
        'search_select': None,
    },
    'company': {
        'selected_ticker': 'VNM',
        'company_timeframe': 'Quarterly',
        'company_active_tab': 0,      # 0=Charts, 1=Tables
        'company_tables_tab': 0,      # 0=Income, 1=Balance, 2=CashFlow
    },
    'bank': {
        'selected_bank': 'VCB',
        'bank_timeframe': 'Quarterly',
        'bank_metric': 'nim',
        'bank_active_tab': 0,         # 0=Charts, 1=Tables
        'bank_tables_tab': 0,         # 0=Size, 1=Income, 2=Growth, 3=Quality, 4=Efficiency
    },
    'security': {
        'selected_security': 'SSI',
        'security_timeframe': 'Quarterly',
        'security_active_tab': 0,     # 0=Charts, 1=Tables
    },
    'sector': {
        'sector_metric': 'PE',
        'sector_filter': 'All',
        'sector_active_tab': 0,       # 0=VN-Index, 1=Valuation, 2=Tables
        'sector_tables_tab': 0,       # 0=SectorComp, 1=SectorInd, 2=StockComp, 3=StockInd
    },
    'valuation': {
        'valuation_metric': 'PE',
        'valuation_sector': 'All',
    },
    'technical': {
        'ta_active_tab': 0,           # 0=Market Overview, 1=Sector Rotation, 2=Stock Scanner
        'ta_selected_sector': 'All',
        'ta_selected_signal': 'all',
        'ta_search_symbol': '',
        'ta_timeframe': '180D',
        'breadth_tf': '6M',
        'rs_heatmap_top_n': 50,
        'rs_heatmap_days': '30D',
        'rs_heatmap_sector': 'All',
        'rs_heatmap_search': '',
        'rrg_mode': 'Sector',
        'rrg_trail': 5,
        'rrg_smooth': 5,
        'money_flow_timeframe': '1D',
    },
    'forecast': {
        'forecast_sector': 'All',
        'forecast_rating': 'All',
        'forecast_active_tab': 0,     # 0=Individual, 1=Sector, 2=9M, 3=Charts, 4=Forward
        'forecast_view_tab': 0,       # Sub-tab for views
        'forecast_sector_tab': 0,     # Sub-tab for sector
    },
    'fx_commodities': {
        'fx_commodity': 'gold',
        'fx_timeframe': '1Y',
        'fx_active_tab': 0,           # 0=Macro, 1=Commodity
    },
}


def init_page_state(page_name: str, extra_defaults: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize session state for a specific page.

    Args:
        page_name: Name of the page ('company', 'bank', 'technical', etc.)
        extra_defaults: Additional default values specific to the page

    Example:
        init_page_state('company', {'custom_filter': 'default'})
    """
    # Always initialize global state first
    _init_state_group('global')

    # Initialize page-specific state
    if page_name in PAGE_STATE_DEFAULTS:
        _init_state_group(page_name)

    # Initialize any extra defaults
    if extra_defaults:
        for key, value in extra_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value


def _init_state_group(group_name: str) -> None:
    """Initialize a group of session state values."""
    defaults = PAGE_STATE_DEFAULTS.get(group_name, {})
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_state(key: str, default: Any = None) -> Any:
    """
    Safely get a session state value.

    Args:
        key: Session state key
        default: Default value if key doesn't exist

    Returns:
        The session state value or default
    """
    return st.session_state.get(key, default)


def set_state(key: str, value: Any) -> None:
    """
    Set a session state value.

    Args:
        key: Session state key
        value: Value to set
    """
    st.session_state[key] = value


def clear_page_state(page_name: str) -> None:
    """
    Clear all session state values for a specific page.

    Args:
        page_name: Name of the page to clear
    """
    if page_name in PAGE_STATE_DEFAULTS:
        for key in PAGE_STATE_DEFAULTS[page_name]:
            if key in st.session_state:
                del st.session_state[key]


def reset_to_defaults(page_name: str) -> None:
    """
    Reset page state to default values.

    Args:
        page_name: Name of the page to reset
    """
    if page_name in PAGE_STATE_DEFAULTS:
        for key, value in PAGE_STATE_DEFAULTS[page_name].items():
            st.session_state[key] = value


# Convenience functions for common operations
def init_all_pages() -> None:
    """Initialize session state for all pages (use in main_app.py)."""
    for page_name in PAGE_STATE_DEFAULTS:
        _init_state_group(page_name)


def get_widget_callback(key: str):
    """
    Get a no-op callback for widgets to prevent unintended form submissions.

    Usage:
        st.text_input("Search", key="search", on_change=get_widget_callback('search'))
    """
    def callback():
        pass  # Intentionally empty - just triggers normal session state update
    return callback


def render_persistent_tabs(
    tab_names: list,
    state_key: str,
    style: str = "primary"
) -> int:
    """
    Render persistent tab navigation with Crypto Terminal Dark Mode styling.

    Design: Premium fintech aesthetic with subtle glow effects
    - Purple (#8B5CF6) for primary tabs
    - Cyan (#06B6D4) for secondary/nested tabs
    - Smooth transitions, no layout shift on hover

    Args:
        tab_names: List of tab names to display
        state_key: Session state key to store active tab index
        style: Tab style - "primary" (purple) or "secondary" (cyan)

    Returns:
        Current active tab index (0-based)
    """
    # Get current active tab from session state
    active_tab = st.session_state.get(state_key, 0)

    # Ensure valid index
    if active_tab >= len(tab_names):
        active_tab = 0
        st.session_state[state_key] = 0

    # Inject premium tab styling (Crypto Terminal Dark Mode)
    st.markdown('''
    <style>
    /* Premium Tab Container Styling */
    div[data-testid="stHorizontalBlock"]:has(button[kind="primary"]),
    div[data-testid="stHorizontalBlock"]:has(button[kind="secondary"]) {
        background: rgba(0, 0, 0, 0.25);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        gap: 6px !important;
        margin-bottom: 20px;
    }
    /* All tab buttons base style */
    div[data-testid="stHorizontalBlock"] button[kind="primary"],
    div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 10px 16px !important;
        transition: all 0.2s ease !important;
        border: 1px solid transparent !important;
    }
    /* Active tab (primary) */
    div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        background: rgba(139, 92, 246, 0.2) !important;
        border-color: #8B5CF6 !important;
        color: #F8FAFC !important;
        box-shadow: 0 0 12px rgba(139, 92, 246, 0.25) !important;
    }
    /* Inactive tab (secondary) */
    div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        background: transparent !important;
        color: #64748B !important;
    }
    div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #94A3B8 !important;
    }
    </style>
    ''', unsafe_allow_html=True)

    # Render tab buttons using Streamlit's native buttons
    cols = st.columns(len(tab_names))
    for idx, (col, name) in enumerate(zip(cols, tab_names)):
        with col:
            is_active = (idx == active_tab)
            # Clean emoji prefixes for cleaner look
            clean_name = name.lstrip('📊📈📋🔄🎯💰🛢️⚙️🛡️ ')
            if st.button(
                clean_name,
                key=f"{state_key}_btn_{idx}",
                width='stretch',
                type="primary" if is_active else "secondary"
            ):
                st.session_state[state_key] = idx
                st.rerun()

    return active_tab
