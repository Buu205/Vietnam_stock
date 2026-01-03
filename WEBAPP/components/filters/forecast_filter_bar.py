"""
Forecast Filter Bar Component
=============================
Reusable header filter bar for Forecast Dashboard tabs.

Each tab uses different filters:
- Tab 0 (BSC Universal): Sector, Rating, Sort, Extended toggle
- Tab 1 (Sector): Sector (single), Sort
- Tab 2 (Achievement): Sector only (cards handle filtering)
- Tab 3 (Consensus): Sector, Consensus Status

Design: Horizontal filter bar in header (no sidebar)
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple, Any

# Default sector list (will be loaded from data)
DEFAULT_SECTORS = [
    'Ngân hàng', 'Bất động sản', 'Chứng khoán', 'Bảo hiểm',
    'Thép', 'Bán lẻ', 'Thực phẩm', 'Công nghệ', 'Dầu khí',
    'Điện', 'Vật liệu xây dựng', 'Vận tải', 'Hóa chất',
    'Dược phẩm', 'Dệt may', 'Thủy sản', 'Cao su', 'Phân bón'
]

# Sort options for different views
SORT_OPTIONS = {
    'stock': [
        ('Upside ↓', 'upside_desc'),
        ('Upside ↑', 'upside_asc'),
        ('PE 25F ↓', 'pe_25_desc'),
        ('PE 25F ↑', 'pe_25_asc'),
        ('PE 26F ↓', 'pe_26_desc'),
        ('Δ PE ↓', 'pe_delta_asc'),  # Lower = improving
        ('PB 25F ↓', 'pb_25_desc'),
        ('PB 25F ↑', 'pb_25_asc'),
        ('PB 26F ↓', 'pb_26_desc'),
        ('Δ PB ↓', 'pb_delta_asc'),  # Lower = improving
        ('Growth ↓', 'growth_desc'),
        ('Market Cap ↓', 'mcap_desc'),
    ],
    'sector': [
        ('PE Fwd ↑', 'pe_asc'),
        ('PE Fwd ↓', 'pe_desc'),
        ('PB Fwd ↑', 'pb_asc'),
        ('PB Fwd ↓', 'pb_desc'),
        ('Growth ↓', 'growth_desc'),
        ('NPATMI ↓', 'npatmi_desc'),
    ]
}

RATING_OPTIONS = ['All', 'STRONG BUY', 'BUY', 'HOLD', 'SELL']

CONSENSUS_STATUS_OPTIONS = [
    ('All', 'all'),
    ('Aligned', 'ALIGNED'),
    ('BSC Bull', 'BSC_BULL'),
    ('VCI Bull', 'VCI_BULL'),
]


def render_filter_bar(
    tab_id: int,
    sectors: List[str] = None,
    show_sector: bool = True,
    show_rating: bool = False,
    show_sort: bool = True,
    sort_options: List[Tuple[str, str]] = None,
    show_extended_toggle: bool = False,
    show_consensus_filter: bool = False,
    show_ticker_search: bool = False,
    key_prefix: str = 'forecast'
) -> Dict[str, Any]:
    """
    Render reusable header filter bar for forecast tabs.

    Args:
        tab_id: Tab index (0-3)
        sectors: List of sector names (uses default if None)
        show_sector: Show sector filter
        show_rating: Show rating filter
        show_sort: Show sort dropdown
        sort_options: List of (label, value) tuples for sort
        show_extended_toggle: Show extended columns toggle
        show_consensus_filter: Show consensus status filter
        show_ticker_search: Show ticker search input
        key_prefix: Session state key prefix

    Returns:
        Dict with filter values: {'sector': 'All', 'sort': 'upside_desc', ...}
    """
    filters = {}
    sector_list = sectors or DEFAULT_SECTORS

    # Calculate number of columns needed
    num_cols = sum([
        show_ticker_search,
        show_sector,
        show_rating,
        show_sort,
        show_extended_toggle,
        show_consensus_filter
    ])

    if num_cols == 0:
        return filters

    # Create responsive columns
    col_weights = []
    if show_ticker_search:
        col_weights.append(1.2)  # Smaller for ticker input
    if show_sector:
        col_weights.append(2)
    if show_rating:
        col_weights.append(1.5)
    if show_sort:
        col_weights.append(2)
    if show_consensus_filter:
        col_weights.append(1.5)
    if show_extended_toggle:
        col_weights.append(1)

    cols = st.columns(col_weights)
    col_idx = 0

    # Ticker search input
    if show_ticker_search:
        with cols[col_idx]:
            ticker_key = f'{key_prefix}_tab{tab_id}_ticker'
            filters['ticker_search'] = st.text_input(
                "Ticker",
                key=ticker_key,
                placeholder="VCB, FPT...",
                label_visibility='collapsed',
                max_chars=10
            ).strip().upper()
        col_idx += 1

    # Sector filter
    if show_sector:
        with cols[col_idx]:
            sector_key = f'{key_prefix}_tab{tab_id}_sector'
            filters['sector'] = st.selectbox(
                "Sector",
                options=['All'] + sector_list,
                key=sector_key,
                label_visibility='collapsed'
            )
        col_idx += 1

    # Rating filter
    if show_rating:
        with cols[col_idx]:
            rating_key = f'{key_prefix}_tab{tab_id}_rating'
            filters['rating'] = st.selectbox(
                "Rating",
                options=RATING_OPTIONS,
                key=rating_key,
                label_visibility='collapsed'
            )
        col_idx += 1

    # Sort dropdown
    if show_sort:
        with cols[col_idx]:
            sort_key = f'{key_prefix}_tab{tab_id}_sort'
            options = sort_options or SORT_OPTIONS.get('stock', [])
            labels = [opt[0] for opt in options]
            values = [opt[1] for opt in options]

            selected_label = st.selectbox(
                "Sort by",
                options=labels,
                key=sort_key,
                label_visibility='collapsed'
            )
            selected_idx = labels.index(selected_label)
            filters['sort'] = values[selected_idx]
            filters['sort_label'] = selected_label
        col_idx += 1

    # Consensus status filter
    if show_consensus_filter:
        with cols[col_idx]:
            consensus_key = f'{key_prefix}_tab{tab_id}_consensus'
            labels = [opt[0] for opt in CONSENSUS_STATUS_OPTIONS]
            values = [opt[1] for opt in CONSENSUS_STATUS_OPTIONS]

            selected_label = st.selectbox(
                "Status",
                options=labels,
                key=consensus_key,
                label_visibility='collapsed'
            )
            selected_idx = labels.index(selected_label)
            filters['consensus_status'] = values[selected_idx]
        col_idx += 1

    # Extended columns toggle
    if show_extended_toggle:
        with cols[col_idx]:
            extended_key = f'{key_prefix}_tab{tab_id}_extended'
            filters['show_extended'] = st.toggle(
                "Extended",
                key=extended_key,
                value=False
            )
        col_idx += 1

    return filters


def apply_filters(
    df,
    filters: Dict[str, Any],
    sector_col: str = 'sector',
    rating_col: str = 'rating',
    consensus_col: str = 'consensus_status'
):
    """
    Apply filters to DataFrame.

    Args:
        df: DataFrame to filter
        filters: Dict from render_filter_bar()
        sector_col: Column name for sector
        rating_col: Column name for rating
        consensus_col: Column name for consensus status

    Returns:
        Filtered DataFrame
    """
    import pandas as pd

    if df.empty:
        return df

    result = df.copy()

    # Sector filter
    sector = filters.get('sector', 'All')
    if sector != 'All' and sector_col in result.columns:
        result = result[result[sector_col] == sector]

    # Rating filter
    rating = filters.get('rating', 'All')
    if rating != 'All' and rating_col in result.columns:
        result = result[result[rating_col] == rating]

    # Consensus status filter
    consensus = filters.get('consensus_status', 'all')
    if consensus != 'all' and consensus_col in result.columns:
        result = result[result[consensus_col] == consensus]

    return result


def apply_sort(
    df,
    sort_value: str,
    sort_mapping: Dict[str, Tuple[str, bool]] = None
):
    """
    Apply sorting to DataFrame.

    Args:
        df: DataFrame to sort
        sort_value: Sort value from filter (e.g., 'upside_desc')
        sort_mapping: Dict mapping sort values to (column, ascending)

    Returns:
        Sorted DataFrame
    """
    if df.empty:
        return df

    # Default sort mapping
    default_mapping = {
        'upside_desc': ('upside_pct', False),
        'upside_asc': ('upside_pct', True),
        'pe_desc': ('pe_fwd_2025', False),
        'pe_asc': ('pe_fwd_2025', True),
        'growth_desc': ('npatmi_growth_yoy_2026', False),
        'mcap_desc': ('market_cap', False),
        'npatmi_desc': ('npatmi_2025f', False),
    }

    mapping = sort_mapping or default_mapping

    if sort_value in mapping:
        col, ascending = mapping[sort_value]
        if col in df.columns:
            return df.sort_values(col, ascending=ascending, na_position='last')

    return df


def render_rating_badges(df, rating_col: str = 'rating') -> str:
    """
    Render compact rating badge summary for header.

    Args:
        df: DataFrame with rating column
        rating_col: Column name for rating

    Returns:
        HTML string for rating badges (never empty - always valid HTML for st.html())
    """
    # Always return valid HTML - st.html() cannot accept empty string
    placeholder = '<div style="display:flex;gap:8px;margin-bottom:12px;"></div>'

    if df.empty or rating_col not in df.columns:
        return placeholder

    counts = df[rating_col].value_counts()

    badge_styles = {
        'STRONG BUY': ('rgba(0, 201, 173, 0.2)', '#00C9AD'),
        'BUY': ('rgba(34, 197, 94, 0.2)', '#22C55E'),
        'HOLD': ('rgba(255, 193, 50, 0.2)', '#FFC132'),
        'SELL': ('rgba(249, 115, 22, 0.2)', '#F97316'),
        'STRONG SELL': ('rgba(239, 68, 68, 0.2)', '#EF4444'),
    }

    badges = []
    for rating, (bg, color) in badge_styles.items():
        count = counts.get(rating, 0)
        if count > 0:
            badge = (
                f'<span style="background:{bg};color:{color};padding:4px 10px;'
                f'border-radius:12px;font-size:11px;font-weight:600;">'
                f'{rating}: {count}</span>'
            )
            badges.append(badge)

    if not badges:
        return placeholder

    return f'<div style="display:flex;gap:8px;margin-bottom:12px;">{"".join(badges)}</div>'
