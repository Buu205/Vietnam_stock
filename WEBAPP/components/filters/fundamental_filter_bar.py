"""
Fundamental Filter Bar
======================
Shared filter bar for Company, Bank, and Security dashboards.
Supports basic and advanced modes for scalability.

Usage:
    from WEBAPP.components.filters.fundamental_filter_bar import render_fundamental_filters

    filters = render_fundamental_filters(
        service=company_service,
        entity_type='company',
        on_ticker_change=handle_ticker_change
    )
    ticker = filters['ticker']
    period = filters['period']
"""

import streamlit as st
from typing import Dict, Callable, Optional, TYPE_CHECKING

from WEBAPP.components.filters.constants import (
    PERIOD_OPTIONS,
    DEFAULT_NUM_PERIODS,
    MAX_NUM_PERIODS,
    MIN_NUM_PERIODS,
    ENTITY_CONFIGS,
)
from WEBAPP.core.session_state import set_synced_ticker

if TYPE_CHECKING:
    pass  # Add service type hints if needed


def render_fundamental_filters(
    service,
    entity_type: str = 'company',
    mode: str = 'basic',
    on_ticker_change: Optional[Callable] = None,
    show_refresh: bool = True,
    key_prefix: Optional[str] = None,
) -> Dict:
    """
    Render horizontal filter bar for Fundamental pages.

    Args:
        service: Data service with get_ticker_list() method
        entity_type: 'company' | 'bank' | 'security'
        mode: 'basic' (Ticker+Period+Refresh) | 'advanced' (+ more options)
        on_ticker_change: Callback when ticker changes
        show_refresh: Show refresh button
        key_prefix: Optional prefix for session state keys

    Returns:
        Dict with filter values:
        {
            'ticker': str,
            'period': str,
            'num_periods': int,
            'refresh': bool
        }
    """
    config = ENTITY_CONFIGS.get(entity_type, ENTITY_CONFIGS['company'])
    prefix = key_prefix or entity_type

    result = {}

    # Initialize session state
    ticker_key = f'{prefix}_filter_ticker'
    period_key = f'{prefix}_filter_period'
    num_periods_key = f'{prefix}_filter_num_periods'

    if ticker_key not in st.session_state:
        st.session_state[ticker_key] = config['default_ticker']
    if period_key not in st.session_state:
        st.session_state[period_key] = 'Quarterly'
    if num_periods_key not in st.session_state:
        st.session_state[num_periods_key] = DEFAULT_NUM_PERIODS

    # Column layout: Ticker | Period | Slider | Refresh
    col_weights = [2, 1.2, 1.5, 0.8] if show_refresh else [2, 1.2, 1.5]
    cols = st.columns(col_weights)

    # Ticker selector
    with cols[0]:
        # Support both method names used by different services
        if hasattr(service, 'get_available_tickers'):
            tickers = service.get_available_tickers()
        elif hasattr(service, 'get_ticker_list'):
            tickers = service.get_ticker_list()
        else:
            tickers = []
        current_ticker = st.session_state.get(ticker_key, config['default_ticker'])

        # Ensure current ticker is in list
        if current_ticker not in tickers and tickers:
            current_ticker = tickers[0]

        ticker_index = tickers.index(current_ticker) if current_ticker in tickers else 0

        selected_ticker = st.selectbox(
            "Ticker",
            options=tickers,
            index=ticker_index,
            key=f'{prefix}_ticker_select',
            label_visibility="collapsed",
            placeholder="Select ticker..."
        )

        # Handle ticker change
        if selected_ticker != st.session_state.get(ticker_key):
            st.session_state[ticker_key] = selected_ticker
            # Update sync state
            sector = _get_ticker_sector(service, selected_ticker)
            set_synced_ticker(selected_ticker, entity_type.upper(), sector)
            if on_ticker_change:
                on_ticker_change(selected_ticker)

        result['ticker'] = selected_ticker

    # Period selector
    with cols[1]:
        current_period = st.session_state.get(period_key, 'Quarterly')
        period_index = PERIOD_OPTIONS.index(current_period) if current_period in PERIOD_OPTIONS else 0

        selected_period = st.selectbox(
            "Period",
            options=PERIOD_OPTIONS,
            index=period_index,
            key=f'{prefix}_period_select',
            label_visibility="collapsed"
        )
        st.session_state[period_key] = selected_period
        result['period'] = selected_period

    # Number of periods slider
    with cols[2]:
        num_periods = st.slider(
            "Periods",
            min_value=MIN_NUM_PERIODS,
            max_value=MAX_NUM_PERIODS,
            value=st.session_state.get(num_periods_key, DEFAULT_NUM_PERIODS),
            key=f'{prefix}_periods_slider',
            label_visibility="collapsed"
        )
        st.session_state[num_periods_key] = num_periods
        result['num_periods'] = num_periods

    # Refresh button
    if show_refresh:
        with cols[3]:
            if st.button("⟳", key=f'{prefix}_refresh', help="Refresh data"):
                st.cache_data.clear()
                result['refresh'] = True
            else:
                result['refresh'] = False

    return result


def _get_ticker_sector(service, ticker: str) -> Optional[str]:
    """Get sector for a ticker from service."""
    try:
        if hasattr(service, 'get_ticker_info'):
            info = service.get_ticker_info(ticker)
            return info.get('sector')
    except Exception:
        pass
    return None


def render_sync_indicator() -> Optional[str]:
    """
    Render sync indicator if there's a synced ticker from another page.
    Returns the synced ticker if indicator is shown, None otherwise.
    """
    from WEBAPP.core.session_state import get_synced_ticker, get_synced_entity, clear_synced_ticker

    synced_ticker = get_synced_ticker()
    if not synced_ticker:
        return None

    entity = get_synced_entity()
    entity_label = {
        'BANK': 'Bank',
        'COMPANY': 'Company',
        'SECURITY': 'Security'
    }.get(entity, entity)

    col1, col2 = st.columns([4, 1])
    with col1:
        st.info(f"Viewing: **{synced_ticker}** (from {entity_label} page)")
    with col2:
        if st.button("Clear", key="clear_sync"):
            clear_synced_ticker()
            st.rerun()

    return synced_ticker
