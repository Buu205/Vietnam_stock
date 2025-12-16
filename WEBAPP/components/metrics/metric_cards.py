"""
Metric Cards Component - Quick Prototype
========================================

Simple, professional metric cards for dashboard KPIs.

Usage:
    from WEBAPP.components.metrics.metric_cards import render_metric_card

    render_metric_card(
        label="Revenue",
        value=1234.5,
        delta=12.5,
        unit="B VND"
    )
"""

import streamlit as st
import pandas as pd


def render_metric_card(
    label: str,
    value: float,
    delta: float = None,
    delta_pct: bool = False,
    unit: str = "",
    inverse: bool = False
):
    """
    Render a metric card with optional delta indicator.

    Args:
        label: Metric name (e.g., "Revenue", "ROE")
        value: Current value
        delta: Change from previous period (optional)
        delta_pct: If True, show delta as percentage change
        unit: Unit of measurement ("B VND", "%", "x", etc.)
        inverse: If True, negative delta is good (e.g., for costs, debt)

    Example:
        >>> render_metric_card("Revenue", 1234.5, delta=12.5, unit="B VND")
        # Displays: Revenue | 1,234.5 B VND | +12.5%
    """
    # Format value based on unit
    if pd.isna(value) or value is None:
        formatted_value = "N/A"
    elif unit == "%":
        formatted_value = f"{value:.2f}%"
    elif unit == "x":
        formatted_value = f"{value:.2f}x"
    elif "B" in unit or "T" in unit:
        # Billions or Trillions
        formatted_value = f"{value:,.1f} {unit}"
    elif "M" in unit:
        # Millions
        formatted_value = f"{value:,.1f} {unit}"
    else:
        # Generic number
        formatted_value = f"{value:,.0f} {unit}"

    # Format delta
    delta_text = None
    delta_color = "off"  # Default: no color

    if delta is not None and not pd.isna(delta):
        # Calculate percentage change if needed
        if delta_pct and value != 0:
            delta_value = (delta / (value - delta)) * 100
            delta_text = f"{delta_value:+.1f}%"
        else:
            # Show absolute change
            if unit == "%":
                delta_text = f"{delta:+.2f}pp"  # percentage points
            elif unit == "x":
                delta_text = f"{delta:+.2f}x"
            else:
                delta_text = f"{delta:+.1f}"

        # Determine color (green = good, red = bad)
        if (delta > 0 and not inverse) or (delta < 0 and inverse):
            delta_color = "normal"  # Green
        elif (delta < 0 and not inverse) or (delta > 0 and inverse):
            delta_color = "inverse"  # Red
        else:
            delta_color = "off"  # Neutral

    # Render using Streamlit's native metric
    st.metric(
        label=label,
        value=formatted_value,
        delta=delta_text,
        delta_color=delta_color
    )


def render_metric_card_row(metrics: list[dict]):
    """
    Render a row of metric cards.

    Args:
        metrics: List of metric dictionaries with keys:
            - label, value, delta (optional), unit (optional), inverse (optional)

    Example:
        >>> metrics = [
        >>>     {"label": "Revenue", "value": 1234.5, "delta": 12.5, "unit": "B VND"},
        >>>     {"label": "ROE", "value": 15.2, "delta": 2.1, "unit": "%"},
        >>> ]
        >>> render_metric_card_row(metrics)
    """
    cols = st.columns(len(metrics))

    for i, metric in enumerate(metrics):
        with cols[i]:
            render_metric_card(
                label=metric.get("label", ""),
                value=metric.get("value", 0),
                delta=metric.get("delta"),
                delta_pct=metric.get("delta_pct", False),
                unit=metric.get("unit", ""),
                inverse=metric.get("inverse", False)
            )
