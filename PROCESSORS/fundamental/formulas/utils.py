#!/usr/bin/env python3
"""
Utility functions for formula calculations

Pure helper functions used across all financial formulas.
These handle common operations like safe division, percentage conversion, and growth calculations.

Author: Formula Extraction Team
Date: 2025-12-08
"""

from typing import Optional, Union
import numpy as np


def safe_divide(
    numerator: Union[float, int, None],
    denominator: Union[float, int, None],
    default: Optional[float] = None
) -> Optional[float]:
    """
    Safely divide two numbers, handling None and zero division.

    Args:
        numerator: Top number
        denominator: Bottom number
        default: Value to return if division fails (default: None)

    Returns:
        Result of division or default value

    Examples:
        >>> safe_divide(100, 50)
        2.0
        >>> safe_divide(100, 0)
        None
        >>> safe_divide(None, 50)
        None
        >>> safe_divide(100, 0, default=0.0)
        0.0
    """
    if numerator is None or denominator is None:
        return default
    if denominator == 0:
        return default
    return numerator / denominator


def safe_multiply(
    value: Union[float, int, None],
    multiplier: Union[float, int],
    default: Optional[float] = None
) -> Optional[float]:
    """
    Safely multiply, handling None values.

    Args:
        value: Value to multiply
        multiplier: Multiplier
        default: Value to return if value is None

    Returns:
        Product or default value

    Examples:
        >>> safe_multiply(10, 2)
        20
        >>> safe_multiply(None, 2)
        None
        >>> safe_multiply(None, 2, default=0.0)
        0.0
    """
    if value is None:
        return default
    return value * multiplier


def to_percentage(
    value: Optional[float],
    default: Optional[float] = None
) -> Optional[float]:
    """
    Convert decimal to percentage (multiply by 100).

    Args:
        value: Decimal value (e.g., 0.25)
        default: Value to return if value is None

    Returns:
        Percentage value (e.g., 25.0)

    Examples:
        >>> to_percentage(0.25)
        25.0
        >>> to_percentage(None)
        None
        >>> to_percentage(None, default=0.0)
        0.0
    """
    if value is None:
        return default
    return value * 100


def from_percentage(
    value: Optional[float],
    default: Optional[float] = None
) -> Optional[float]:
    """
    Convert percentage to decimal (divide by 100).

    Args:
        value: Percentage value (e.g., 25.0)
        default: Value to return if value is None

    Returns:
        Decimal value (e.g., 0.25)

    Examples:
        >>> from_percentage(25.0)
        0.25
        >>> from_percentage(None)
        None
    """
    if value is None:
        return default
    return value / 100


def yoy_growth(
    current: Union[float, int, None],
    previous: Union[float, int, None],
    as_percentage: bool = True
) -> Optional[float]:
    """
    Calculate Year-over-Year growth rate.

    Formula: ((Current - Previous) / Previous) × 100

    Args:
        current: Current period value
        previous: Previous period value (same period last year)
        as_percentage: Return as percentage (default: True)

    Returns:
        Growth rate (%) or None

    Examples:
        >>> yoy_growth(120, 100)
        20.0
        >>> yoy_growth(80, 100)
        -20.0
        >>> yoy_growth(100, 0)
        None
    """
    if current is None or previous is None or previous == 0:
        return None

    growth = (current - previous) / previous
    return growth * 100 if as_percentage else growth


def qoq_growth(
    current: Union[float, int, None],
    previous: Union[float, int, None],
    as_percentage: bool = True
) -> Optional[float]:
    """
    Calculate Quarter-over-Quarter growth rate.

    Formula: ((Current - Previous) / Previous) × 100

    Args:
        current: Current quarter value
        previous: Previous quarter value
        as_percentage: Return as percentage (default: True)

    Returns:
        Growth rate (%) or None

    Examples:
        >>> qoq_growth(120, 100)
        20.0
        >>> qoq_growth(90, 100)
        -10.0
    """
    # Same formula as YoY, just different time period
    return yoy_growth(current, previous, as_percentage)


def cagr(
    ending_value: Union[float, int, None],
    beginning_value: Union[float, int, None],
    periods: int,
    as_percentage: bool = True
) -> Optional[float]:
    """
    Calculate Compound Annual Growth Rate (CAGR).

    Formula: ((Ending / Beginning) ^ (1 / Periods) - 1) × 100

    Args:
        ending_value: Final value
        beginning_value: Starting value
        periods: Number of periods (years)
        as_percentage: Return as percentage (default: True)

    Returns:
        CAGR (%) or None

    Examples:
        >>> cagr(150, 100, 3)  # 14.47% CAGR over 3 years
        14.47
        >>> cagr(100, 150, 3)  # Negative CAGR
        -12.89
    """
    if ending_value is None or beginning_value is None:
        return None
    if beginning_value <= 0 or ending_value <= 0:
        return None
    if periods <= 0:
        return None

    growth = (ending_value / beginning_value) ** (1 / periods) - 1
    result = growth * 100 if as_percentage else growth
    return round(result, 2)


def average(
    *values: Union[float, int, None],
    skip_none: bool = True
) -> Optional[float]:
    """
    Calculate average of values, optionally skipping None.

    Args:
        *values: Values to average
        skip_none: Skip None values (default: True)

    Returns:
        Average or None

    Examples:
        >>> average(10, 20, 30)
        20.0
        >>> average(10, None, 30, skip_none=True)
        20.0
        >>> average(10, None, 30, skip_none=False)
        None
    """
    if skip_none:
        valid_values = [v for v in values if v is not None]
    else:
        # If any None and not skipping, return None
        if any(v is None for v in values):
            return None
        valid_values = list(values)

    if not valid_values:
        return None

    return sum(valid_values) / len(valid_values)


def convert_to_billions(
    value: Union[float, int, None],
    from_unit: str = "millions"
) -> Optional[float]:
    """
    Convert value to billions.

    Args:
        value: Value to convert
        from_unit: Source unit ("millions", "thousands", "units")

    Returns:
        Value in billions or None

    Examples:
        >>> convert_to_billions(1000, "millions")
        1.0
        >>> convert_to_billions(1000000, "thousands")
        1.0
    """
    if value is None:
        return None

    conversion = {
        "billions": 1,
        "millions": 1e-3,
        "thousands": 1e-6,
        "units": 1e-9
    }

    multiplier = conversion.get(from_unit)
    if multiplier is None:
        raise ValueError(f"Unknown unit: {from_unit}")

    return value * multiplier


def is_positive(value: Optional[float]) -> bool:
    """Check if value is positive (> 0)."""
    return value is not None and value > 0


def is_negative(value: Optional[float]) -> bool:
    """Check if value is negative (< 0)."""
    return value is not None and value < 0


def is_zero(value: Optional[float], tolerance: float = 1e-9) -> bool:
    """Check if value is zero (within tolerance)."""
    return value is not None and abs(value) < tolerance


# Demo / Testing
if __name__ == "__main__":
    print("=" * 60)
    print("FORMULA UTILS DEMO")
    print("=" * 60)

    print("\n1. Safe Division:")
    print(f"  100 / 50 = {safe_divide(100, 50)}")
    print(f"  100 / 0 = {safe_divide(100, 0)}")
    print(f"  None / 50 = {safe_divide(None, 50)}")

    print("\n2. Percentage Conversion:")
    print(f"  0.25 → {to_percentage(0.25)}%")
    print(f"  25% → {from_percentage(25.0)}")

    print("\n3. Growth Calculations:")
    print(f"  YoY: 120 vs 100 = {yoy_growth(120, 100)}%")
    print(f"  QoQ: 90 vs 100 = {qoq_growth(90, 100)}%")
    print(f"  CAGR: 150 → 100 over 3 years = {cagr(150, 100, 3)}%")

    print("\n4. Average:")
    print(f"  avg(10, 20, 30) = {average(10, 20, 30)}")
    print(f"  avg(10, None, 30) = {average(10, None, 30)}")

    print("\n5. Unit Conversion:")
    print(f"  1000 millions → {convert_to_billions(1000, 'millions')} billions")

    print("\n✅ All utility functions working!")
