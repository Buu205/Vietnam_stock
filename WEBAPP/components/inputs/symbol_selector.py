"""
Symbol Selector Component
==========================

Enhanced symbol dropdown with search and sector filtering.
Uses SymbolLoader for liquid tickers (315 symbols with >1B VND/day trading value).

Author: AI Assistant
Date: 2025-12-12
Updated: 2025-12-17 - Use SymbolLoader instead of SectorRegistry
"""

import streamlit as st
from typing import Literal, Optional, List
from WEBAPP.core.symbol_loader import SymbolLoader

# Keep SectorRegistry for ticker info lookup only
try:
    from config.registries import SectorRegistry
    _SECTOR_REGISTRY = SectorRegistry()
except Exception:
    _SECTOR_REGISTRY = None


@st.cache_resource
def _get_symbol_loader():
    """Cache symbol loader instance."""
    return SymbolLoader()


def symbol_selector(
    entity_type: Literal['company', 'bank', 'security', 'insurance', 'all'] = 'all',
    default: Optional[str] = None,
    key: str = 'symbol_selector',
    label: str = "Select Symbol"
) -> str:
    """
    Enhanced symbol selector with sector filtering.
    Uses master_symbols.json (315 liquid tickers with >1B VND/day).

    Args:
        entity_type: Filter by entity type
            - 'company': Non-financial companies (261)
            - 'bank': Banks (22)
            - 'security': Securities firms (27)
            - 'insurance': Insurance companies (5)
            - 'all': All liquid symbols (315)
        default: Default selected symbol
        key: Unique key for widget
        label: Label for selectbox

    Returns:
        Selected symbol (e.g., 'VNM', 'ACB')

    Usage:
        from WEBAPP.components.inputs import symbol_selector

        symbol = symbol_selector(entity_type='company', default='VNM')
    """
    loader = _get_symbol_loader()

    # Get symbols based on entity type
    if entity_type != 'all':
        entity_type_map = {
            'company': 'COMPANY',
            'bank': 'BANK',
            'security': 'SECURITY',
            'insurance': 'INSURANCE'
        }
        target_entity_type = entity_type_map.get(entity_type, 'COMPANY')
        symbols = loader.get_symbols_by_entity(target_entity_type)
    else:
        symbols = loader.get_all_symbols()

    symbols = sorted(symbols)

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
        help=f"Tổng số: {len(symbols)} symbols (liquid >1B VND/day)"
    )

    # Show ticker info below (use SectorRegistry for sector info)
    if selected and _SECTOR_REGISTRY:
        ticker_info = _SECTOR_REGISTRY.get_ticker(selected)
        if ticker_info:
            st.caption(
                f"**Sector:** {ticker_info.get('sector', 'N/A')} | "
                f"**Industry:** {ticker_info.get('industry', 'N/A')}"
            )

    return selected
