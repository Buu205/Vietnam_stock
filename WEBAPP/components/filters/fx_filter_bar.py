"""
FX & Commodities Filter Bar
============================
Header filter bar for FX & Commodities dashboard.
Simple time range selector in horizontal layout.
"""

import streamlit as st
from typing import Dict, Any

# Time range options
TIME_RANGE_OPTIONS = [
    ('1M', 30),
    ('3M', 90),
    ('6M', 180),
    ('1Y', 365),
    ('2Y', 730),
]


def render_fx_filter_bar(key_prefix: str = 'fx') -> Dict[str, Any]:
    """
    Render horizontal filter bar for FX & Commodities page.

    Args:
        key_prefix: Session state key prefix

    Returns:
        Dict with filter values: {'days': 180}
    """
    filters = {}

    # Single row with time range pills
    col1, col2 = st.columns([2, 8])

    with col1:
        labels = [opt[0] for opt in TIME_RANGE_OPTIONS]
        values = [opt[1] for opt in TIME_RANGE_OPTIONS]

        selected = st.selectbox(
            "Time Range",
            options=labels,
            index=2,  # Default 6M
            key=f"{key_prefix}_time_range",
            label_visibility='collapsed'
        )
        filters['days'] = values[labels.index(selected)]

    return filters
