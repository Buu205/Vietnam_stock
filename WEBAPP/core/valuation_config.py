"""
Valuation Chart Configuration
=============================
Single source of truth for colors, outliers, formatting, and marker sizes.

This module centralizes all valuation-related constants to ensure consistency
across sector, valuation, and forecast dashboards.

Usage:
    from WEBAPP.core.valuation_config import (
        OUTLIER_LIMITS, STATUS_COLORS, CHART_COLORS, MARKER_SIZES,
        format_ratio, format_percent, format_zscore, get_status_color,
        filter_outliers, get_percentile_status
    )
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple

# =============================================================================
# OUTLIER LIMITS
# =============================================================================
# Maximum/minimum values for each valuation metric to filter chart distortions
OUTLIER_LIMITS = {
    'PE': {'min': 0, 'max': 100, 'multiplier': 5},
    'PB': {'min': 0, 'max': 20, 'multiplier': 4},
    'PS': {'min': 0, 'max': 30, 'multiplier': 4},
    'EV_EBITDA': {'min': 0, 'max': 50, 'multiplier': 4}
}

# Alias for backward compatibility
OUTLIER_RULES = OUTLIER_LIMITS

# =============================================================================
# VALUATION STATUS COLORS
# =============================================================================
# Colors for valuation status based on percentile position
STATUS_COLORS = {
    'very_cheap': '#3B82F6',     # Blue - P0-10
    'cheap': '#22C55E',          # Lime green - P10-40
    'fair': '#FFD666',           # Gold - P40-70
    'expensive': '#FF9F43',      # Orange - P70-90
    'very_expensive': '#FF6B6B'  # Coral red - P90-100
}

# Gradient colors for beautiful display (start -> end)
STATUS_GRADIENTS = {
    'very_cheap': ('#60A5FA', '#3B82F6'),     # Light blue -> Blue
    'cheap': ('#4ADE80', '#22C55E'),           # Light green -> Green
    'fair': ('#FDE047', '#FFD666'),            # Light gold -> Gold
    'expensive': ('#FDBA74', '#FF9F43'),       # Light orange -> Orange
    'very_expensive': ('#FCA5A5', '#FF6B6B')   # Light coral -> Coral red
}

# =============================================================================
# CHART COLORS (Candlestick & Bands)
# =============================================================================
CHART_COLORS = {
    # Candlestick
    'body': '#A0AEC0',                         # Gray body
    'body_fill': 'rgba(160, 174, 192, 0.3)',   # Transparent gray
    'whisker': '#718096',                      # Darker gray

    # Line chart
    'main_line': '#00D4AA',      # Teal (primary)
    'mean_line': '#4A7BC8',      # Blue
    'median_line': '#FFD666',    # Gold

    # Statistical bands
    'band_1sd': 'rgba(0, 212, 170, 0.15)',    # Teal transparent
    'band_2sd': 'rgba(74, 123, 200, 0.1)',    # Blue transparent
    'sd_line': 'rgba(74, 123, 200, 0.6)',     # Blue semi-transparent

    # Markers
    'trailing_marker': '#00D4AA',   # Teal for TTM/current
    'forward_marker': '#FF6B6B',    # Coral for forward
}

# =============================================================================
# MARKER SIZES
# =============================================================================
MARKER_SIZES = {
    'trailing': 10,       # Circle for TTM/current
    'forward': 10,        # Diamond for forward
    'border_width': 1.5,  # Marker border
    'small': 8,           # Small markers for dense charts
    'large': 12           # Large markers for emphasis
}

# =============================================================================
# PERCENTILE THRESHOLDS (Mean Reversion Valuation Matrix)
# =============================================================================
# Primary metric: Percentile Rank (0-100%)
# Secondary: Z-Score for reference
PERCENTILE_THRESHOLDS = {
    'very_cheap': (0, 10),      # Z < -1.5
    'cheap': (10, 40),          # -1.5 ≤ Z < -0.5
    'fair': (40, 70),           # -0.5 ≤ Z ≤ 0.5
    'expensive': (70, 90),      # 0.5 < Z ≤ 1.5
    'very_expensive': (90, 100) # Z > 1.5
}

# Vietnamese status labels
STATUS_LABELS = {
    'very_cheap': 'Rất Rẻ',
    'cheap': 'Rẻ',
    'fair': 'Hợp lý',
    'expensive': 'Đắt',
    'very_expensive': 'Rất Đắt'
}

# Status badge colors (CSS-ready hex codes for HTML badges)
STATUS_BADGE_COLORS = {
    'very_cheap': '#3B82F6',     # Blue - P0-10
    'cheap': '#22C55E',          # Lime green - P10-40
    'fair': '#FFD666',           # Gold - P40-70
    'expensive': '#FF9F43',      # Orange - P70-90
    'very_expensive': '#FF6B6B'  # Coral red - P90-100
}


# =============================================================================
# NUMBER FORMATTERS
# =============================================================================
def format_ratio(value: Optional[float], precision: int = 2) -> str:
    """
    Format PE/PB/EV ratios.

    Args:
        value: Numeric value to format
        precision: Decimal places (default 2)

    Returns:
        Formatted string like "15.23x" or "—" for invalid values

    Example:
        >>> format_ratio(15.234)
        '15.23x'
        >>> format_ratio(None)
        '—'
    """
    if value is None or (isinstance(value, float) and (pd.isna(value) or np.isnan(value))):
        return "—"
    return f"{value:.{precision}f}x"


def format_percent(value: Optional[float], precision: int = 0) -> str:
    """
    Format percentile values.

    Args:
        value: Percentile value (0-100)
        precision: Decimal places (default 0)

    Returns:
        Formatted string like "75%" or "—" for invalid values

    Example:
        >>> format_percent(75.5)
        '76%'
        >>> format_percent(75.5, precision=1)
        '75.5%'
    """
    if value is None or (isinstance(value, float) and (pd.isna(value) or np.isnan(value))):
        return "—"
    return f"{value:.{precision}f}%"


def format_zscore(value: Optional[float]) -> str:
    """
    Format z-score values with sign.

    Args:
        value: Z-score value

    Returns:
        Formatted string like "+1.52σ" or "-0.87σ" or "—" for invalid values

    Example:
        >>> format_zscore(1.52)
        '+1.52σ'
        >>> format_zscore(-0.87)
        '-0.87σ'
    """
    if value is None or (isinstance(value, float) and (pd.isna(value) or np.isnan(value))):
        return "—"
    return f"{value:+.2f}σ"


def format_change(value: Optional[float]) -> str:
    """
    Format change percent with sign.

    Args:
        value: Change percentage

    Returns:
        Formatted string like "+12.5%" or "-8.3%" or "—" for invalid values

    Example:
        >>> format_change(12.5)
        '+12.5%'
        >>> format_change(-8.3)
        '-8.3%'
    """
    if value is None or (isinstance(value, float) and (pd.isna(value) or np.isnan(value))):
        return "—"
    return f"{value:+.1f}%"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def get_status_key(percentile: float) -> str:
    """
    Get status key based on percentile position (using new thresholds).

    Thresholds:
        - 0-10%: very_cheap
        - 10-40%: cheap
        - 40-70%: fair
        - 70-90%: expensive
        - 90-100%: very_expensive
    """
    if percentile <= 10:
        return 'very_cheap'
    elif percentile <= 40:
        return 'cheap'
    elif percentile <= 70:
        return 'fair'
    elif percentile <= 90:
        return 'expensive'
    else:
        return 'very_expensive'


def get_status_color(percentile: float) -> str:
    """
    Get color based on percentile position.

    Args:
        percentile: Value from 0-100

    Returns:
        Hex color code
    """
    key = get_status_key(percentile)
    return STATUS_COLORS[key]


def get_percentile_status(percentile: float) -> str:
    """
    Get Vietnamese status label based on percentile.

    Args:
        percentile: Value from 0-100

    Returns:
        Vietnamese status: 'Rất Rẻ', 'Rẻ', 'Hợp lý', 'Đắt', 'Rất Đắt'
    """
    key = get_status_key(percentile)
    return STATUS_LABELS[key]


def get_status_with_emoji(percentile: float) -> str:
    """
    DEPRECATED: Use get_status_label() or render_status_badge() instead.
    Returns plain text status label (no emoji).

    Args:
        percentile: Value from 0-100

    Returns:
        Vietnamese status label (e.g., 'Rất Rẻ', 'Đắt')
    """
    key = get_status_key(percentile)
    return STATUS_LABELS[key]


def get_status_label(percentile: float) -> str:
    """
    Get plain text status label based on percentile.

    Args:
        percentile: Value from 0-100

    Returns:
        Vietnamese status label (e.g., 'Rất Rẻ', 'Đắt')
    """
    key = get_status_key(percentile)
    return STATUS_LABELS[key]


def render_status_badge(percentile: float) -> str:
    """
    Render HTML status badge with colored dot and text.

    Args:
        percentile: Value from 0-100

    Returns:
        HTML string for colored badge: '<span class="status-badge ...">● Label</span>'

    Example:
        >>> render_status_badge(5)
        '<span class="status-badge status-very-cheap">● Rất Rẻ</span>'
    """
    key = get_status_key(percentile)
    color = STATUS_BADGE_COLORS[key]
    label = STATUS_LABELS[key]
    css_class = key.replace('_', '-')
    return f'<span class="status-badge status-{css_class}" style="color: {color};">● {label}</span>'


def render_status_dot(percentile: float) -> str:
    """
    Render HTML colored dot indicator.

    Args:
        percentile: Value from 0-100

    Returns:
        HTML string for colored dot: '<span style="color: #...;">●</span>'
    """
    key = get_status_key(percentile)
    color = STATUS_BADGE_COLORS[key]
    return f'<span style="color: {color}; font-size: 1.2em;">●</span>'


def get_valuation_status(percentile: float) -> Tuple[str, str, str]:
    """
    Get complete valuation status info.

    Args:
        percentile: Value from 0-100

    Returns:
        Tuple of (status_key, status_label, status_color)

    Example:
        >>> get_valuation_status(5)
        ('very_cheap', 'Rất Rẻ', '#00D4AA')
    """
    key = get_status_key(percentile)
    return (key, STATUS_LABELS[key], STATUS_COLORS[key])


def filter_outliers(series: pd.Series, metric: str) -> pd.Series:
    """
    Apply consistent outlier filtering based on metric type.

    Args:
        series: Pandas Series with valuation data
        metric: Metric name ('PE', 'PB', 'PS', 'EV_EBITDA')

    Returns:
        Filtered Series with outliers removed

    Example:
        >>> pe_data = pd.Series([5, 10, 15, 200, 500])
        >>> filter_outliers(pe_data, 'PE')
        0     5
        1    10
        2    15
        dtype: int64
    """
    metric_upper = metric.upper().replace('/', '_').replace('-', '_')
    limits = OUTLIER_LIMITS.get(metric_upper, {'min': 0, 'max': 100})
    return series[(series >= limits['min']) & (series <= limits['max'])]


def calculate_y_range(data: pd.Series, metric: str) -> Tuple[float, float]:
    """
    Calculate appropriate y-axis range based on data distribution.

    Uses P5-P95 for scaling to avoid outlier distortion.

    Args:
        data: Pandas Series with valuation data
        metric: Metric name for outlier limits

    Returns:
        Tuple of (y_min, y_max)

    Example:
        >>> data = pd.Series([5, 10, 15, 20, 25, 30])
        >>> calculate_y_range(data, 'PE')
        (4.5, 33.0)
    """
    limits = OUTLIER_LIMITS.get(metric.upper(), {'min': 0, 'max': 100})
    filtered = filter_outliers(data, metric)

    if filtered.empty:
        return (0, limits['max'])

    # Use P5-P95 for auto-scaling, not min-max
    y_min = max(0, filtered.quantile(0.05) * 0.9)
    y_max = min(limits['max'], filtered.quantile(0.95) * 1.1)

    return (y_min, y_max)


def calculate_statistics(data: pd.Series) -> dict:
    """
    Calculate common statistics for valuation data.

    Args:
        data: Pandas Series with valuation data (already filtered)

    Returns:
        Dict with p5, p25, p50, p75, p95, min, max, mean, std
    """
    if data.empty:
        return {}

    return {
        'min': data.min(),
        'p5': data.quantile(0.05),
        'p25': data.quantile(0.25),
        'p50': data.quantile(0.50),  # median
        'p75': data.quantile(0.75),
        'p95': data.quantile(0.95),
        'max': data.max(),
        'mean': data.mean(),
        'std': data.std()
    }
