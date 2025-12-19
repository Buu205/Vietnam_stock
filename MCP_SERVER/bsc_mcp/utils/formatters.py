"""
Response Formatters
===================

Utilities for formatting data into Markdown responses.
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
import numpy as np


def format_number(value: Any, decimals: int = 2) -> str:
    """
    Format a number with thousand separators.

    Args:
        value: Number to format
        decimals: Number of decimal places

    Returns:
        Formatted string (e.g., "1,234.56")
    """
    if pd.isna(value) or value is None:
        return "N/A"
    try:
        if isinstance(value, (int, np.integer)):
            return f"{int(value):,}"
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def format_percent(value: Any, decimals: int = 2) -> str:
    """
    Format a number as percentage.

    Args:
        value: Number to format (0.15 = 15% or 15 = 15%)
        decimals: Number of decimal places

    Returns:
        Formatted string (e.g., "15.00%")
    """
    if pd.isna(value) or value is None:
        return "N/A"
    try:
        num = float(value)
        # If value is already in percentage form (> 1 or < -1), don't multiply
        if abs(num) <= 1:
            num = num * 100
        return f"{num:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)


def format_price(value: Any, currency: str = "VND") -> str:
    """
    Format a price with currency.

    Args:
        value: Price value
        currency: Currency code

    Returns:
        Formatted string (e.g., "25,750 VND")
    """
    if pd.isna(value) or value is None:
        return "N/A"
    try:
        return f"{int(float(value)):,} {currency}"
    except (ValueError, TypeError):
        return str(value)


def format_billions(value: Any, decimals: int = 2) -> str:
    """
    Format large numbers in billions.

    Args:
        value: Number to format
        decimals: Decimal places

    Returns:
        Formatted string (e.g., "1,234.56 tỷ")
    """
    if pd.isna(value) or value is None:
        return "N/A"
    try:
        num = float(value)
        if abs(num) >= 1e9:
            return f"{num/1e9:,.{decimals}f} tỷ"
        elif abs(num) >= 1e6:
            return f"{num/1e6:,.{decimals}f} triệu"
        else:
            return f"{num:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def format_dataframe_markdown(
    df: pd.DataFrame,
    title: Optional[str] = None,
    max_rows: int = 50,
    columns: Optional[List[str]] = None,
    format_map: Optional[Dict[str, str]] = None
) -> str:
    """
    Convert DataFrame to Markdown table.

    Args:
        df: DataFrame to convert
        title: Optional title for the table
        max_rows: Maximum rows to show
        columns: Specific columns to include
        format_map: Dict mapping column names to format types
                   ('number', 'percent', 'price', 'billions')

    Returns:
        Markdown formatted table string
    """
    if df.empty:
        return f"## {title}\n\nNo data available." if title else "No data available."

    lines = []

    if title:
        lines.append(f"## {title}\n")

    # Select columns
    if columns:
        df = df[[c for c in columns if c in df.columns]]

    # Limit rows
    if len(df) > max_rows:
        df = df.head(max_rows)
        truncated = True
    else:
        truncated = False

    # Format values
    format_map = format_map or {}
    formatted_df = df.copy()

    for col in formatted_df.columns:
        if col in format_map:
            fmt = format_map[col]
            if fmt == 'number':
                formatted_df[col] = formatted_df[col].apply(format_number)
            elif fmt == 'percent':
                formatted_df[col] = formatted_df[col].apply(format_percent)
            elif fmt == 'price':
                formatted_df[col] = formatted_df[col].apply(format_price)
            elif fmt == 'billions':
                formatted_df[col] = formatted_df[col].apply(format_billions)
        else:
            # Auto-detect and format
            formatted_df[col] = formatted_df[col].apply(
                lambda x: format_number(x) if isinstance(x, (int, float, np.number)) and not pd.isna(x) else (str(x) if not pd.isna(x) else "N/A")
            )

    # Build markdown table
    headers = " | ".join(formatted_df.columns)
    separator = " | ".join(["---"] * len(formatted_df.columns))
    lines.append(f"| {headers} |")
    lines.append(f"| {separator} |")

    for _, row in formatted_df.iterrows():
        values = " | ".join(str(v) for v in row.values)
        lines.append(f"| {values} |")

    if truncated:
        lines.append("")
        lines.append(f"*Showing first {max_rows} rows. Total: {len(df)} rows.*")

    return "\n".join(lines)


def format_dict_markdown(
    data: Dict[str, Any],
    title: Optional[str] = None,
    format_map: Optional[Dict[str, str]] = None
) -> str:
    """
    Convert dict to Markdown key-value list.

    Args:
        data: Dictionary to format
        title: Optional title
        format_map: Dict mapping keys to format types

    Returns:
        Markdown formatted string
    """
    lines = []

    if title:
        lines.append(f"## {title}\n")

    format_map = format_map or {}

    for key, value in data.items():
        if key in format_map:
            fmt = format_map[key]
            if fmt == 'number':
                value = format_number(value)
            elif fmt == 'percent':
                value = format_percent(value)
            elif fmt == 'price':
                value = format_price(value)
            elif fmt == 'billions':
                value = format_billions(value)
        elif isinstance(value, float):
            value = format_number(value)

        # Convert key to readable format
        display_key = key.replace('_', ' ').title()
        lines.append(f"- **{display_key}**: {value}")

    return "\n".join(lines)


def format_comparison_table(
    data: List[Dict[str, Any]],
    title: Optional[str] = None,
    id_column: str = "ticker"
) -> str:
    """
    Format comparison data as a table.

    Args:
        data: List of dicts with same keys
        title: Optional title
        id_column: Column to use as identifier

    Returns:
        Markdown table
    """
    if not data:
        return "No data to compare."

    df = pd.DataFrame(data)
    return format_dataframe_markdown(df, title=title)


def format_ticker_header(
    ticker: str,
    entity_type: Optional[str] = None,
    sector: Optional[str] = None
) -> str:
    """
    Format a standard ticker header.

    Args:
        ticker: Stock ticker
        entity_type: BANK, COMPANY, etc.
        sector: Sector name

    Returns:
        Formatted header string
    """
    lines = [f"## {ticker}"]

    info_parts = []
    if entity_type:
        info_parts.append(f"**Type:** {entity_type}")
    if sector:
        info_parts.append(f"**Sector:** {sector}")

    if info_parts:
        lines.append(" | ".join(info_parts))

    lines.append("")
    return "\n".join(lines)
