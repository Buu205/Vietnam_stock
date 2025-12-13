"""
Date Range Picker Component
============================

Date range selection with presets.

Author: AI Assistant
Date: 2025-12-12
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple


def date_range_picker(
    default_start: str = '2023-01-01',
    default_end: str = '2025-12-12',
    key: str = 'date_range'
) -> Tuple[str, str]:
    """
    Date range picker with quick presets.

    Args:
        default_start: Default start date (YYYY-MM-DD)
        default_end: Default end date (YYYY-MM-DD)
        key: Unique key for widget

    Returns:
        Tuple of (start_date, end_date) as strings (YYYY-MM-DD)

    Usage:
        from WEBAPP.components.inputs import date_range_picker

        start_date, end_date = date_range_picker(
            default_start='2023-01-01',
            default_end='2025-12-12'
        )
    """
    st.subheader("📅 Date Range")

    # Quick presets
    preset = st.selectbox(
        "Quick Select",
        options=[
            "Custom",
            "Last 1 Year",
            "Last 2 Years",
            "Last 3 Years",
            "Last 5 Years",
            "All Time"
        ],
        key=f"{key}_preset"
    )

    # Calculate dates based on preset
    end_date = datetime.now()

    if preset == "Last 1 Year":
        start_date = end_date - timedelta(days=365)
    elif preset == "Last 2 Years":
        start_date = end_date - timedelta(days=730)
    elif preset == "Last 3 Years":
        start_date = end_date - timedelta(days=1095)
    elif preset == "Last 5 Years":
        start_date = end_date - timedelta(days=1825)
    elif preset == "All Time":
        start_date = datetime(2020, 1, 1)
    else:  # Custom
        start_date = datetime.strptime(default_start, '%Y-%m-%d')
        end_date = datetime.strptime(default_end, '%Y-%m-%d')

    # If custom, show date inputs
    if preset == "Custom":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=start_date,
                key=f"{key}_start"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=end_date,
                key=f"{key}_end"
            )

    # Convert to string format
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    st.caption(f"Selected: {start_str} to {end_str}")

    return start_str, end_str
