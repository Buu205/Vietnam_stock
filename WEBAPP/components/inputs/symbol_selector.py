"""
Symbol Selector Component
==========================

Enhanced symbol dropdown with search and sector filtering.

Author: AI Assistant
Date: 2025-12-12
"""

import streamlit as st
from typing import Literal, Optional, List
from config.registries import SectorRegistry


@st.cache_resource
def _get_sector_registry():
    """Cache sector registry instance."""
    return SectorRegistry()


def symbol_selector(
    entity_type: Literal['company', 'bank', 'security', 'insurance', 'all'] = 'all',
    default: Optional[str] = None,
    key: str = 'symbol_selector',
    label: str = "Select Symbol"
) -> str:
    """
    Enhanced symbol selector with sector filtering.

    Args:
        entity_type: Filter by entity type
            - 'company': Non-financial companies
            - 'bank': Banks
            - 'security': Securities firms
            - 'insurance': Insurance companies
            - 'all': All symbols
        default: Default selected symbol
        key: Unique key for widget
        label: Label for selectbox

    Returns:
        Selected symbol (e.g., 'VNM', 'ACB')

    Usage:
        from WEBAPP.components.inputs import symbol_selector

        symbol = symbol_selector(entity_type='company', default='VNM')
    """
    sector_reg = _get_sector_registry()

    # Get all symbols
    all_symbols = sector_reg.get_all_tickers()

    # Filter by entity type if specified
    if entity_type != 'all':
        entity_type_map = {
            'company': 'COMPANY',
            'bank': 'BANK',
            'security': 'SECURITY',
            'insurance': 'INSURANCE'
        }
        target_entity_type = entity_type_map.get(entity_type, 'COMPANY')

        filtered_symbols = []
        for symbol in all_symbols:
            ticker_info = sector_reg.get_ticker(symbol)
            if ticker_info and ticker_info.get('entity_type') == target_entity_type:
                filtered_symbols.append(symbol)

        symbols = sorted(filtered_symbols)
    else:
        symbols = sorted(all_symbols)

    # Set default index
    default_index = 0
    if default and default in symbols:
        default_index = symbols.index(default)

    # Render selectbox
    selected = st.selectbox(
        label,
        options=symbols,
        index=default_index,
        key=key,
        help=f"Tổng số: {len(symbols)} symbols"
    )

    # Show ticker info below
    if selected:
        ticker_info = sector_reg.get_ticker(selected)
        if ticker_info:
            st.caption(
                f"**Sector:** {ticker_info.get('sector', 'N/A')} | "
                f"**Industry:** {ticker_info.get('industry', 'N/A')}"
            )

    return selected
