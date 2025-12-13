"""
Metric Card Component
=====================

KPI cards for dashboard overview.

Author: AI Assistant
Date: 2025-12-12
"""

import streamlit as st
from typing import List, Dict, Optional, Literal


def format_value(
    value: float,
    format_type: Literal['number', 'billions', 'percent', 'ratio'] = 'number'
) -> str:
    """
    Format numeric value for display.

    Args:
        value: Numeric value
        format_type: How to format
            - 'number': 1,234,567
            - 'billions': 1.23B VND
            - 'percent': 12.34%
            - 'ratio': 1.23x

    Returns:
        Formatted string
    """
    if value is None or (isinstance(value, float) and (value != value)):  # Check NaN
        return "N/A"

    if format_type == 'billions':
        return f"{value:,.2f}B VND"
    elif format_type == 'percent':
        return f"{value:,.2f}%"
    elif format_type == 'ratio':
        return f"{value:,.2f}x"
    else:  # number
        return f"{value:,.0f}"


def metric_card_row(metrics: List[Dict]):
    """
    Display a row of metric cards.

    Args:
        metrics: List of metric dictionaries, each with:
            - label: str (metric name)
            - value: float (metric value)
            - delta: float (change/comparison, optional)
            - format: str (how to format value)
            - delta_format: str (how to format delta)

    Usage:
        from WEBAPP.components.data_display import metric_card_row

        metric_card_row([
            {
                'label': 'Net Revenue',
                'value': 1234.56,
                'delta': 12.3,
                'format': 'billions',
                'delta_format': 'percent'
            },
            {
                'label': 'EBITDA',
                'value': 456.78,
                'delta': -5.2,
                'format': 'billions',
                'delta_format': 'percent'
            },
            {
                'label': 'ROE',
                'value': 18.5,
                'delta': 2.3,
                'format': 'percent',
                'delta_format': 'percent'
            }
        ])
    """
    cols = st.columns(len(metrics))

    for i, metric in enumerate(metrics):
        with cols[i]:
            label = metric.get('label', 'Metric')
            value = metric.get('value')
            delta = metric.get('delta')
            format_type = metric.get('format', 'number')
            delta_format = metric.get('delta_format', 'percent')

            # Format value
            formatted_value = format_value(value, format_type)

            # Format delta
            if delta is not None:
                formatted_delta = format_value(abs(delta), delta_format)
                delta_str = f"{formatted_delta}" if delta >= 0 else f"-{formatted_delta}"
            else:
                delta_str = None

            # Render metric
            st.metric(
                label=label,
                value=formatted_value,
                delta=delta_str
            )
