"""
Chart Configuration Schema
==========================
Single source of truth for all chart configurations.
Edit this file to adjust UI/UX globally.

Usage:
    from WEBAPP.core.chart_schema import CHART_SCHEMA, get_chart_config
    config = get_chart_config('candlestick_distribution')
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================
class ChartType(Enum):
    CANDLESTICK_DISTRIBUTION = "candlestick_distribution"
    LINE_WITH_BANDS = "line_with_bands"
    HISTOGRAM = "histogram"
    BOX_WITH_MARKERS = "box_with_markers"
    DUAL_AXIS = "dual_axis"
    SPARKLINE = "sparkline"


class MetricType(Enum):
    PE = "PE"
    PB = "PB"
    PS = "PS"
    EV_EBITDA = "EV_EBITDA"


# =============================================================================
# LAYOUT CONFIG
# =============================================================================
@dataclass
class LayoutConfig:
    """Chart layout settings."""
    height: int = 400
    margin_left: int = 50
    margin_right: int = 30
    margin_top: int = 50
    margin_bottom: int = 50
    padding: int = 4
    autosize: bool = True


# =============================================================================
# AXIS CONFIG
# =============================================================================
@dataclass
class AxisConfig:
    """Axis configuration."""
    grid_color: str = "rgba(255, 255, 255, 0.05)"
    zero_line_color: str = "rgba(255, 255, 255, 0.1)"
    line_color: str = "rgba(255, 255, 255, 0.08)"
    tick_font_size: int = 10
    tick_font_color: str = "#64748B"
    title_font_size: int = 12
    title_font_color: str = "#94A3B8"
    tick_angle: int = 0
    show_grid: bool = True
    fixed_range: bool = False


# =============================================================================
# MARKER CONFIG
# =============================================================================
@dataclass
class MarkerConfig:
    """Marker settings for scatter plots."""
    size_trailing: int = 10        # Circle for current/TTM
    size_forward: int = 10         # Diamond for forward
    size_small: int = 8            # Dense charts
    size_large: int = 12           # Emphasis
    border_width: float = 1.5      # Marker border
    border_color: str = "white"


# =============================================================================
# COLOR PALETTES
# =============================================================================
@dataclass
class StatusColors:
    """Valuation status colors based on percentile."""
    very_cheap: str = "#00D4AA"      # P0-10
    cheap: str = "#7FFFD4"           # P10-25
    fair: str = "#FFD666"            # P25-75
    expensive: str = "#FF9F43"       # P75-90
    very_expensive: str = "#FF6B6B"  # P90-100


@dataclass
class ChartColors:
    """Chart element colors."""
    # Candlestick
    body: str = "#A0AEC0"
    body_fill: str = "rgba(160, 174, 192, 0.3)"
    whisker: str = "#718096"

    # Lines
    main_line: str = "#00D4AA"       # Teal
    mean_line: str = "#4A7BC8"       # Blue
    median_line: str = "#FFD666"     # Gold

    # Statistical bands
    band_1sd: str = "rgba(0, 212, 170, 0.15)"
    band_2sd: str = "rgba(74, 123, 200, 0.1)"
    sd_line: str = "rgba(74, 123, 200, 0.6)"

    # Forward markers
    forward_marker: str = "#F59E0B"  # Amber


# =============================================================================
# Y-AXIS RANGE BY METRIC
# =============================================================================
Y_AXIS_DISPLAY_RANGE: Dict[str, Tuple[float, float]] = {
    'PE': (0, 50),
    'PB': (0, 8),
    'PS': (0, 10),
    'EV_EBITDA': (0, 25)
}

OUTLIER_LIMITS: Dict[str, Dict[str, float]] = {
    'PE': {'min': 0, 'max': 100, 'multiplier': 5},
    'PB': {'min': 0, 'max': 20, 'multiplier': 4},
    'PS': {'min': 0, 'max': 30, 'multiplier': 4},
    'EV_EBITDA': {'min': 0, 'max': 50, 'multiplier': 4}
}


# =============================================================================
# PERCENTILE THRESHOLDS
# =============================================================================
PERCENTILE_THRESHOLDS: Dict[str, Tuple[float, float]] = {
    'very_cheap': (0, 10),
    'cheap': (10, 25),
    'fair': (25, 75),
    'expensive': (75, 90),
    'very_expensive': (90, 100)
}


# =============================================================================
# CHART TYPE CONFIGS
# =============================================================================
@dataclass
class CandlestickDistributionConfig:
    """Type A1: Distribution candlestick chart."""
    chart_type: str = "candlestick_distribution"
    height: int = 500
    x_tick_angle: int = -45
    x_tick_font_size: int = 10
    show_range_slider: bool = False
    show_legend: bool = True
    drag_mode: str = "pan"  # or "zoom", "select"
    fixed_range: bool = True  # Disable zoom for simplicity


@dataclass
class LineWithBandsConfig:
    """Type A2: Line chart with statistical bands."""
    chart_type: str = "line_with_bands"
    height: int = 400
    line_width: float = 2.5
    mean_line_dash: str = "dash"
    median_line_dash: str = "solid"
    sd_line_dash: str = "dot"
    sd_line_width: float = 1.0
    show_2sd: bool = True
    x_tick_format: str = "%b %Y"
    x_padding_percent: float = 0.02  # 2% padding on right


@dataclass
class HistogramConfig:
    """Type A3: Histogram distribution chart."""
    chart_type: str = "histogram"
    height: int = 300
    bins: int = 35
    bar_color: str = "#8B5CF6"       # Purple
    bar_opacity: float = 0.7
    mean_line_color: str = "#F59E0B"  # Amber
    sd_line_color: str = "#4A7BC8"    # Blue
    show_mean_std: bool = True
    show_current_marker: bool = True
    current_marker_color: str = "#00D4AA"


@dataclass
class BoxWithMarkersConfig:
    """Type B1: Box with trailing/forward markers."""
    chart_type: str = "box_with_markers"
    height: int = 500
    bar_width: float = 0.6
    bar_opacity: float = 0.6
    whisker_thickness: float = 1.5
    whisker_width: int = 4
    trailing_symbol: str = "circle"
    forward_symbol: str = "diamond"
    show_sector_median_line: bool = True


@dataclass
class DualAxisConfig:
    """Dual axis chart (e.g., PE + PB)."""
    chart_type: str = "dual_axis"
    height: int = 450
    primary_line_color: str = "#00D4AA"
    secondary_line_color: str = "#F59E0B"
    primary_line_width: float = 2.5
    secondary_line_width: float = 2.0


@dataclass
class SparklineConfig:
    """Mini chart for metric cards."""
    chart_type: str = "sparkline"
    height: int = 80
    line_width: float = 1.5
    fill_opacity: float = 0.2
    show_axis: bool = False
    show_grid: bool = False


# =============================================================================
# TYPOGRAPHY
# =============================================================================
@dataclass
class TypographyConfig:
    """Font settings for charts."""
    font_family_display: str = "Space Grotesk, sans-serif"
    font_family_body: str = "DM Sans, sans-serif"
    font_family_mono: str = "JetBrains Mono, monospace"
    title_size: int = 16
    title_color: str = "#E8E8E8"
    axis_title_size: int = 12
    tick_size: int = 10
    legend_size: int = 11
    annotation_size: int = 10


# =============================================================================
# HOVER/TOOLTIP CONFIG
# =============================================================================
@dataclass
class HoverConfig:
    """Hover/tooltip settings."""
    bgcolor: str = "#1A1625"
    border_color: str = "#8B5CF6"
    font_color: str = "#F8FAFC"
    font_size: int = 12


# =============================================================================
# MASTER CHART SCHEMA
# =============================================================================
CHART_SCHEMA = {
    # Global configs
    'layout': LayoutConfig(),
    'axis': AxisConfig(),
    'marker': MarkerConfig(),
    'status_colors': StatusColors(),
    'chart_colors': ChartColors(),
    'typography': TypographyConfig(),
    'hover': HoverConfig(),

    # Y-axis ranges by metric
    'y_axis_display_range': Y_AXIS_DISPLAY_RANGE,
    'outlier_limits': OUTLIER_LIMITS,
    'percentile_thresholds': PERCENTILE_THRESHOLDS,

    # Chart-specific configs
    'candlestick_distribution': CandlestickDistributionConfig(),
    'line_with_bands': LineWithBandsConfig(),
    'histogram': HistogramConfig(),
    'box_with_markers': BoxWithMarkersConfig(),
    'dual_axis': DualAxisConfig(),
    'sparkline': SparklineConfig(),
}


# =============================================================================
# ACCESSOR FUNCTIONS
# =============================================================================
def get_chart_config(chart_type: str) -> Any:
    """Get config for specific chart type."""
    return CHART_SCHEMA.get(chart_type)


def get_y_range(metric: str) -> Tuple[float, float]:
    """Get display y-range for metric."""
    return Y_AXIS_DISPLAY_RANGE.get(metric.upper(), (0, 100))


def get_outlier_limits(metric: str) -> Dict[str, float]:
    """Get outlier limits for metric."""
    return OUTLIER_LIMITS.get(metric.upper(), {'min': 0, 'max': 100})


def get_status_color(percentile: float) -> str:
    """Get color based on percentile."""
    colors = StatusColors()
    if percentile < 10:
        return colors.very_cheap
    elif percentile < 25:
        return colors.cheap
    elif percentile < 75:
        return colors.fair
    elif percentile < 90:
        return colors.expensive
    else:
        return colors.very_expensive


def get_percentile_status(percentile: float) -> str:
    """Get status label based on percentile."""
    if percentile < 10:
        return 'Very Cheap'
    elif percentile < 25:
        return 'Cheap'
    elif percentile < 75:
        return 'Fair'
    elif percentile < 90:
        return 'Expensive'
    else:
        return 'Very Expensive'


def get_base_layout(height: int = 400, title: str = "") -> dict:
    """Get base layout for all valuation charts using schema config."""
    typography = CHART_SCHEMA['typography']
    hover = CHART_SCHEMA['hover']
    axis = CHART_SCHEMA['axis']

    return {
        'title': dict(
            text=title,
            font=dict(
                family=typography.font_family_display,
                size=typography.title_size,
                color=typography.title_color
            )
        ),
        'height': height,
        'template': 'plotly_dark',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': dict(
            family=typography.font_family_mono,
            color=axis.title_font_color
        ),
        'xaxis': dict(
            gridcolor=axis.grid_color,
            showline=True,
            linecolor=axis.line_color
        ),
        'yaxis': dict(
            gridcolor=axis.grid_color,
            zeroline=False,
            showline=True,
            linecolor=axis.line_color
        ),
        'hoverlabel': dict(
            bgcolor=hover.bgcolor,
            bordercolor=hover.border_color,
            font=dict(color=hover.font_color, size=hover.font_size)
        )
    }
