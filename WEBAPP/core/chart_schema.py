"""
Chart Schema - Unified Visual Configuration
============================================

Single source of truth cho TẤT CẢ chart configs trong project.
Tổ chức theo CHART TYPE - mỗi loại chart có config riêng đầy đủ.

Merged from: valuation_config.py + chart_config.py + theme colors

Structure:
- ChartType: Enum các loại chart
- ChartSchema: Dataclass config đầy đủ cho mỗi loại
- CHART_REGISTRY: Dict chứa tất cả chart configs
- Helpers: Functions để lấy config, format values

Usage:
    from WEBAPP.core.chart_schema import (
        get_chart_schema, build_plotly_layout,
        ChartType, format_value, get_status_color
    )

    # Get full config for a chart type
    schema = get_chart_schema('valuation_line')
    fig.update_layout(**build_plotly_layout(schema, title="PE Ratio"))

Created: 2025-12-21
Updated: 2025-12-21 - Unified from valuation_config + chart_config
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import pandas as pd
import numpy as np

# =============================================================================
# THEME CONSTANTS (Global)
# =============================================================================
THEME = {
    # Backgrounds (OLED Dark)
    'bg_void': '#0F0B1E',
    'bg_deep': '#1A1625',
    'bg_surface': '#252033',
    'bg_elevated': '#2D2640',
    'bg_hover': '#352E4D',

    # Text
    'text_white': '#F8FAFC',
    'text_bright': '#F1F5F9',
    'text_primary': '#E2E8F0',
    'text_secondary': '#94A3B8',
    'text_accent': '#C4B5FD',
    'text_muted': '#64748B',

    # Primary Colors
    'purple': '#8B5CF6',
    'purple_dark': '#7C3AED',
    'purple_light': '#A78BFA',
    'cyan': '#06B6D4',
    'cyan_light': '#22D3EE',
    'amber': '#F59E0B',
    'amber_light': '#FBBF24',

    # Semantic
    'positive': '#10B981',
    'positive_light': '#22C55E',
    'negative': '#EF4444',
    'negative_light': '#F87171',
    'warning': '#F59E0B',
    'info': '#8B5CF6',
    'neutral': '#6B7280',

    # Typography
    'font_display': 'Space Grotesk, sans-serif',
    'font_body': 'DM Sans, sans-serif',
    'font_mono': 'JetBrains Mono, monospace',
}


# =============================================================================
# CHART TYPE ENUM
# =============================================================================
class ChartType(str, Enum):
    """Tất cả các loại chart trong hệ thống."""

    # === VALUATION CHARTS ===
    VALUATION_LINE = 'valuation_line'
    VALUATION_BOX = 'valuation_box'
    VALUATION_CANDLESTICK = 'valuation_candlestick'
    VALUATION_HISTOGRAM = 'valuation_histogram'

    # === TRADING CHARTS ===
    OHLC_CANDLESTICK = 'ohlc_candlestick'
    VOLUME_BAR = 'volume_bar'
    OSCILLATOR = 'oscillator'

    # === ADVANCED CHARTS ===
    HEATMAP = 'heatmap'
    TREEMAP = 'treemap'
    WATERFALL = 'waterfall'
    BULLET = 'bullet'
    RADAR = 'radar'
    GAUGE = 'gauge'
    SPARKLINE = 'sparkline'
    SUNBURST = 'sunburst'

    # === BASIC CHARTS ===
    LINE = 'line'
    BAR = 'bar'
    AREA = 'area'
    SCATTER = 'scatter'

    # Legacy aliases
    CANDLESTICK_DISTRIBUTION = 'valuation_candlestick'
    LINE_WITH_BANDS = 'valuation_line'
    BOX_WITH_MARKERS = 'valuation_box'
    HISTOGRAM = 'valuation_histogram'


# =============================================================================
# CHART SCHEMA DATACLASS
# =============================================================================
@dataclass
class ChartSchema:
    """Complete configuration for a chart type."""

    # === IDENTITY ===
    chart_type: str
    name: str
    description: str = ""

    # === DIMENSIONS ===
    height: int = 420
    min_height: int = 200
    max_height: int = 800
    margins: Dict = field(default_factory=lambda: {
        'l': 50, 'r': 30, 't': 50, 'b': 50, 'pad': 4
    })

    # === COLORS - Full color scheme for this chart type ===
    colors: Dict = field(default_factory=dict)

    # === DATA CONFIG ===
    outlier_limits: Dict = field(default_factory=dict)
    y_axis_range: Optional[Tuple[float, float]] = None
    dtick: Optional[float] = None

    # === UI/UX ===
    show_legend: bool = True
    show_grid: bool = True
    show_hover: bool = True
    hover_mode: str = 'x unified'
    animation: bool = True
    animation_duration: int = 500
    fixed_range: bool = False
    drag_mode: str = 'pan'

    # === TYPOGRAPHY ===
    title_font_size: int = 16
    title_font_color: str = '#E8E8E8'
    axis_font_size: int = 11
    tick_font_size: int = 10
    legend_font_size: int = 11

    # === FORMATTERS ===
    value_formatter: str = 'default'
    precision: int = 2

    # === CHART-SPECIFIC ===
    bins: int = 35  # For histograms
    line_width: float = 2.5
    bar_width: float = 0.6
    marker_size: int = 10
    marker_border: float = 1.5

    def get_layout(self, title: str = "") -> Dict:
        """Convert schema to Plotly layout dict."""
        return {
            'title': {
                'text': title,
                'font': {
                    'family': THEME['font_display'],
                    'size': self.title_font_size,
                    'color': self.title_font_color
                },
                'x': 0,
                'xanchor': 'left'
            },
            'height': self.height,
            'autosize': True,
            'margin': self.margins,
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'font': {
                'family': THEME['font_mono'],
                'size': self.axis_font_size,
                'color': THEME['text_secondary']
            },
            'showlegend': self.show_legend,
            'hovermode': self.hover_mode if self.show_hover else False,
            'dragmode': self.drag_mode,
            'xaxis': {
                'gridcolor': 'rgba(255,255,255,0.05)' if self.show_grid else 'rgba(0,0,0,0)',
                'zerolinecolor': 'rgba(255,255,255,0.1)',
                'tickfont': {'size': self.tick_font_size, 'color': THEME['text_muted']},
                'linecolor': 'rgba(255,255,255,0.08)',
                'automargin': True,
                'fixedrange': self.fixed_range,
            },
            'yaxis': {
                'gridcolor': 'rgba(255,255,255,0.05)' if self.show_grid else 'rgba(0,0,0,0)',
                'zerolinecolor': 'rgba(255,255,255,0.1)',
                'tickfont': {'size': self.tick_font_size, 'color': THEME['text_muted']},
                'linecolor': 'rgba(255,255,255,0.08)',
                'automargin': True,
                'fixedrange': self.fixed_range,
                'range': list(self.y_axis_range) if self.y_axis_range else None,
                'dtick': self.dtick,
            },
            'legend': {
                'font': {'size': self.legend_font_size, 'color': '#FFFFFF'},
                'bgcolor': 'rgba(0,0,0,0)',
            },
            'hoverlabel': {
                'bgcolor': THEME['bg_deep'],
                'bordercolor': THEME['purple'],
                'font': {'family': THEME['font_mono'], 'size': 12, 'color': THEME['text_white']}
            }
        }


# =============================================================================
# CHART REGISTRY - Tất cả chart configs
# =============================================================================
CHART_REGISTRY: Dict[str, ChartSchema] = {

    # =========================================================================
    # VALUATION CHARTS
    # =========================================================================

    'valuation_line': ChartSchema(
        chart_type='valuation_line',
        name='Line with Statistical Bands',
        description='PE/PB/EV time series with mean/std bands',
        height=420,
        colors={
            'main_line': '#00D4AA',
            'mean_line': '#4A7BC8',
            'median_line': '#FFD666',
            'band_1sd': 'rgba(0, 212, 170, 0.15)',
            'band_2sd': 'rgba(74, 123, 200, 0.1)',
            'sd_line': 'rgba(74, 123, 200, 0.6)',
            'sd_line_dash': 'dot',
            'line_width': 2.5,
        },
        outlier_limits={'PE': (0, 100), 'PB': (0, 20), 'PS': (0, 30), 'EV_EBITDA': (0, 50)},
        show_legend=True,
        value_formatter='ratio',
        line_width=2.5,
    ),

    'valuation_box': ChartSchema(
        chart_type='valuation_box',
        name='Box Plot with Markers',
        description='Sector/ticker comparison with trailing/forward markers',
        height=500,
        colors={
            'box_fill': 'rgba(139, 92, 246, 0.3)',
            'box_line': '#8B5CF6',
            'whisker': '#718096',
            'median': '#F59E0B',
            'trailing_marker': '#00D4AA',
            'forward_marker': '#FF6B6B',
            'forward_2026_marker': '#F59E0B',
        },
        show_legend=True,
        value_formatter='ratio',
        marker_size=10,
        marker_border=1.5,
    ),

    'valuation_candlestick': ChartSchema(
        chart_type='valuation_candlestick',
        name='Distribution Candlestick',
        description='Sector PE/PB distribution over time',
        height=500,
        margins={'l': 50, 'r': 30, 't': 50, 'b': 80, 'pad': 4},
        colors={
            'body': '#A0AEC0',
            'body_fill': 'rgba(160, 174, 192, 0.3)',
            'whisker': '#718096',
            'median': '#F59E0B',
            'current_dot': '#00D4AA',
        },
        show_legend=False,
        fixed_range=True,
        value_formatter='ratio',
    ),

    'valuation_histogram': ChartSchema(
        chart_type='valuation_histogram',
        name='Distribution Histogram',
        description='Histogram với mean/std markers',
        height=350,
        margins={'l': 40, 'r': 20, 't': 40, 'b': 40, 'pad': 2},
        colors={
            'bar': '#8B5CF6',
            'bar_opacity': 0.7,
            'mean_line': '#F59E0B',
            'std_line': '#06B6D4',
            'current_marker': '#22C55E',
        },
        show_legend=False,
        bins=35,
        value_formatter='ratio',
    ),

    # =========================================================================
    # TRADING CHARTS
    # =========================================================================

    'ohlc_candlestick': ChartSchema(
        chart_type='ohlc_candlestick',
        name='OHLC Candlestick',
        description='Stock price candlestick with MA lines',
        height=600,
        colors={
            'bullish': '#10B981',
            'bearish': '#EF4444',
            'volume_up': 'rgba(16, 185, 129, 0.4)',
            'volume_down': 'rgba(239, 68, 68, 0.4)',
            'ma_20': '#8B5CF6',
            'ma_50': '#06B6D4',
            'ma_200': '#F59E0B',
            'bollinger_upper': '#EF4444',
            'bollinger_lower': '#22C55E',
            'bollinger_middle': '#8B5CF6',
        },
        show_legend=False,
    ),

    'volume_bar': ChartSchema(
        chart_type='volume_bar',
        name='Volume Bar',
        description='Trading volume bars',
        height=150,
        margins={'l': 50, 'r': 30, 't': 20, 'b': 30, 'pad': 4},
        colors={
            'up': 'rgba(16, 185, 129, 0.6)',
            'down': 'rgba(239, 68, 68, 0.6)',
        },
        show_legend=False,
        show_grid=False,
    ),

    'oscillator': ChartSchema(
        chart_type='oscillator',
        name='Oscillator',
        description='RSI, MACD, Stochastic',
        height=200,
        margins={'l': 50, 'r': 30, 't': 30, 'b': 30, 'pad': 4},
        colors={
            'rsi_line': '#8B5CF6',
            'rsi_overbought': '#EF4444',
            'rsi_oversold': '#22C55E',
            'macd_positive': '#22C55E',
            'macd_negative': '#EF4444',
            'macd_signal': '#F59E0B',
            'macd_histogram_up': 'rgba(34, 197, 94, 0.6)',
            'macd_histogram_down': 'rgba(239, 68, 68, 0.6)',
        },
        show_legend=True,
        y_axis_range=(0, 100),
    ),

    # =========================================================================
    # ADVANCED CHARTS
    # =========================================================================

    'heatmap': ChartSchema(
        chart_type='heatmap',
        name='Correlation Heatmap',
        description='Sector correlation matrix',
        height=500,
        margins={'l': 80, 'r': 20, 't': 50, 'b': 80, 'pad': 4},
        colors={
            'colorscale': [
                [0.0, '#EF4444'],
                [0.25, '#F59E0B'],
                [0.5, '#1A1625'],
                [0.75, '#06B6D4'],
                [1.0, '#8B5CF6'],
            ],
            'zmin': -1,
            'zmax': 1,
        },
        show_legend=False,
    ),

    'treemap': ChartSchema(
        chart_type='treemap',
        name='Treemap',
        description='Market cap hierarchical distribution',
        height=600,
        margins={'l': 0, 'r': 0, 't': 30, 'b': 0, 'pad': 0},
        colors={
            'colorscale': ['#EF4444', '#1A1625', '#22C55E'],
            'border_color': '#FFFFFF',
            'border_width': 2,
        },
        show_legend=False,
    ),

    'waterfall': ChartSchema(
        chart_type='waterfall',
        name='Waterfall',
        description='P&L breakdown',
        height=420,
        margins={'l': 60, 'r': 30, 't': 50, 'b': 50, 'pad': 4},
        colors={
            'increasing': '#22C55E',
            'decreasing': '#EF4444',
            'totals': '#8B5CF6',
            'connector': '#64748B',
        },
        show_legend=False,
    ),

    'bullet': ChartSchema(
        chart_type='bullet',
        name='Bullet Chart',
        description='Performance vs target',
        height=80,
        margins={'l': 100, 'r': 20, 't': 10, 'b': 10, 'pad': 0},
        colors={
            'poor': 'rgba(239, 68, 68, 0.2)',
            'acceptable': 'rgba(245, 158, 11, 0.2)',
            'good': 'rgba(34, 197, 94, 0.2)',
            'actual': '#8B5CF6',
            'target': '#FFFFFF',
        },
        show_legend=False,
        show_grid=False,
    ),

    'radar': ChartSchema(
        chart_type='radar',
        name='Radar Chart',
        description='Multi-variable comparison',
        height=420,
        margins={'l': 60, 'r': 60, 't': 60, 'b': 60, 'pad': 4},
        colors={
            'ticker_fill': 'rgba(139, 92, 246, 0.2)',
            'ticker_line': '#8B5CF6',
            'sector_line': '#06B6D4',
            'sector_dash': 'dash',
            'grid': 'rgba(255, 255, 255, 0.1)',
        },
        show_legend=True,
    ),

    'gauge': ChartSchema(
        chart_type='gauge',
        name='Gauge',
        description='Single metric focus',
        height=200,
        margins={'l': 20, 'r': 20, 't': 40, 'b': 20, 'pad': 0},
        colors={
            'bar': '#8B5CF6',
            'bg': '#1A1625',
            'threshold_low': 'rgba(239, 68, 68, 0.3)',
            'threshold_mid': 'rgba(245, 158, 11, 0.3)',
            'threshold_high': 'rgba(34, 197, 94, 0.3)',
        },
        show_legend=False,
        show_grid=False,
    ),

    'sparkline': ChartSchema(
        chart_type='sparkline',
        name='Sparkline',
        description='Inline trend indicator',
        height=40,
        min_height=30,
        max_height=60,
        margins={'l': 0, 'r': 0, 't': 0, 'b': 0, 'pad': 0},
        colors={
            'line': '#8B5CF6',
            'fill': 'rgba(139, 92, 246, 0.1)',
            'line_width': 1.5,
        },
        show_legend=False,
        show_grid=False,
        show_hover=False,
        animation=False,
        line_width=1.5,
    ),

    'sunburst': ChartSchema(
        chart_type='sunburst',
        name='Sunburst',
        description='Hierarchical proportions',
        height=600,
        margins={'l': 0, 'r': 0, 't': 30, 'b': 0, 'pad': 0},
        colors={
            'colorscale': ['#EF4444', '#1A1625', '#22C55E'],
            'layer_opacity_step': 0.15,
        },
        show_legend=False,
    ),

    # =========================================================================
    # BASIC CHARTS
    # =========================================================================

    'line': ChartSchema(
        chart_type='line',
        name='Line Chart',
        description='Simple line chart',
        height=420,
        colors={
            'primary': '#8B5CF6',
            'secondary': '#06B6D4',
            'tertiary': '#F59E0B',
            'quaternary': '#22C55E',
        },
    ),

    'bar': ChartSchema(
        chart_type='bar',
        name='Bar Chart',
        description='Simple bar chart',
        height=420,
        colors={
            'primary': '#8B5CF6',
            'secondary': '#06B6D4',
            'positive': '#22C55E',
            'negative': '#EF4444',
        },
    ),
}


# =============================================================================
# STATUS COLORS (Valuation Assessment)
# =============================================================================
STATUS_COLORS = {
    'very_cheap': '#00D4AA',
    'cheap': '#7FFFD4',
    'fair': '#FFD666',
    'expensive': '#FF9F43',
    'very_expensive': '#FF6B6B',
}

PERCENTILE_THRESHOLDS = {
    'very_cheap': (0, 10),
    'cheap': (10, 25),
    'fair': (25, 75),
    'expensive': (75, 90),
    'very_expensive': (90, 100)
}

Y_AXIS_DISPLAY_RANGE = {
    'PE': (0, 50),
    'PB': (0, 8),
    'PS': (0, 10),
    'EV_EBITDA': (0, 25)
}

OUTLIER_LIMITS = {
    'PE': {'min': 0, 'max': 100, 'multiplier': 5},
    'PB': {'min': 0, 'max': 20, 'multiplier': 4},
    'PS': {'min': 0, 'max': 30, 'multiplier': 4},
    'EV_EBITDA': {'min': 0, 'max': 50, 'multiplier': 4}
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_chart_schema(chart_type: str) -> ChartSchema:
    """Get schema for a specific chart type."""
    if chart_type in CHART_REGISTRY:
        return CHART_REGISTRY[chart_type]
    # Legacy aliases
    aliases = {
        'candlestick_distribution': 'valuation_candlestick',
        'line_with_bands': 'valuation_line',
        'box_with_markers': 'valuation_box',
        'histogram': 'valuation_histogram',
    }
    if chart_type in aliases:
        return CHART_REGISTRY[aliases[chart_type]]
    return CHART_REGISTRY['line']


def get_chart_config(chart_type: str) -> ChartSchema:
    """Alias for get_chart_schema (backward compatibility)."""
    return get_chart_schema(chart_type)


def build_plotly_layout(schema: ChartSchema, title: str = "", **overrides) -> Dict:
    """Build Plotly layout from schema with optional overrides."""
    layout = schema.get_layout(title)
    for key, value in overrides.items():
        if key in layout and isinstance(layout[key], dict) and isinstance(value, dict):
            layout[key].update(value)
        else:
            layout[key] = value
    return layout


def get_chart_colors(chart_type: str) -> Dict:
    """Get color scheme for a chart type."""
    return get_chart_schema(chart_type).colors


def get_y_range(metric: str) -> Tuple[float, float]:
    """Get display y-range for metric."""
    return Y_AXIS_DISPLAY_RANGE.get(metric.upper(), (0, 100))


def get_outlier_limits(metric: str) -> Dict[str, float]:
    """Get outlier limits for metric."""
    return OUTLIER_LIMITS.get(metric.upper(), {'min': 0, 'max': 100})


def get_status_color(percentile: float) -> str:
    """Get color based on percentile."""
    if percentile < 10:
        return STATUS_COLORS['very_cheap']
    elif percentile < 25:
        return STATUS_COLORS['cheap']
    elif percentile < 75:
        return STATUS_COLORS['fair']
    elif percentile < 90:
        return STATUS_COLORS['expensive']
    return STATUS_COLORS['very_expensive']


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
    return 'Very Expensive'


# =============================================================================
# VALUE FORMATTERS
# =============================================================================

def format_value(value: Optional[float], format_type: str = 'default', precision: int = 2) -> str:
    """Format value based on type."""
    if value is None or (isinstance(value, float) and (pd.isna(value) or np.isnan(value))):
        return "—"
    formatters = {
        'ratio': lambda v, p: f"{v:.{p}f}x",
        'percent': lambda v, p: f"{v:.{p}f}%",
        'zscore': lambda v, p: f"{v:+.2f}σ",
        'change': lambda v, p: f"{v:+.1f}%",
        'number': lambda v, p: f"{v:,.{p}f}",
        'currency': lambda v, p: f"{v:,.0f}đ",
        'default': lambda v, p: f"{v:.{p}f}",
    }
    return formatters.get(format_type, formatters['default'])(value, precision)


def format_ratio(value: Optional[float], precision: int = 2) -> str:
    """Format PE/PB/EV ratios."""
    return format_value(value, 'ratio', precision)


def format_percent(value: Optional[float], precision: int = 0) -> str:
    """Format percentile values."""
    return format_value(value, 'percent', precision)


def format_zscore(value: Optional[float]) -> str:
    """Format z-score values."""
    return format_value(value, 'zscore')


def format_change(value: Optional[float]) -> str:
    """Format change percent."""
    return format_value(value, 'change')


def filter_outliers(series: pd.Series, metric: str) -> pd.Series:
    """Apply outlier filtering based on metric type."""
    metric_upper = metric.upper().replace('/', '_').replace('-', '_')
    limits = OUTLIER_LIMITS.get(metric_upper, {'min': 0, 'max': 100})
    return series[(series >= limits['min']) & (series <= limits['max'])]


def calculate_y_range(data: pd.Series, metric: str) -> Tuple[float, float]:
    """Calculate appropriate Y-axis range based on data distribution."""
    limits = OUTLIER_LIMITS.get(metric.upper(), {'min': 0, 'max': 100})
    filtered = filter_outliers(data, metric)
    if filtered.empty:
        return (0, limits['max'])
    y_min = max(0, filtered.quantile(0.05) * 0.9)
    y_max = min(limits['max'], filtered.quantile(0.95) * 1.1)
    return (y_min, y_max)


def calculate_statistics(data: pd.Series) -> Dict:
    """Calculate common statistics for valuation data."""
    if data.empty:
        return {}
    return {
        'min': data.min(),
        'p5': data.quantile(0.05),
        'p25': data.quantile(0.25),
        'p50': data.quantile(0.50),
        'p75': data.quantile(0.75),
        'p95': data.quantile(0.95),
        'max': data.max(),
        'mean': data.mean(),
        'std': data.std()
    }


def get_base_layout(height: int = 400, title: str = "") -> dict:
    """Get base layout for all valuation charts (backward compat)."""
    return get_chart_schema('line').get_layout(title)


def list_chart_types() -> List[str]:
    """Get list of all available chart types."""
    return list(CHART_REGISTRY.keys())


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================
# Old references still work
CHART_SCHEMA = {
    'outlier_limits': OUTLIER_LIMITS,
    'y_axis_display_range': Y_AXIS_DISPLAY_RANGE,
    'percentile_thresholds': PERCENTILE_THRESHOLDS,
    'status_colors': STATUS_COLORS,
}

# Legacy dataclass access
class StatusColors:
    very_cheap = STATUS_COLORS['very_cheap']
    cheap = STATUS_COLORS['cheap']
    fair = STATUS_COLORS['fair']
    expensive = STATUS_COLORS['expensive']
    very_expensive = STATUS_COLORS['very_expensive']


class HistogramConfig:
    """Legacy histogram config for backward compatibility."""
    bins = 35
    bar_width = 0.7
    opacity = 0.7
    color = '#8B5CF6'


class ChartColors:
    body = '#A0AEC0'
    body_fill = 'rgba(160, 174, 192, 0.3)'
    whisker = '#718096'
    main_line = '#00D4AA'
    mean_line = '#4A7BC8'
    median_line = '#FFD666'
    band_1sd = 'rgba(0, 212, 170, 0.15)'
    band_2sd = 'rgba(74, 123, 200, 0.1)'
    sd_line = 'rgba(74, 123, 200, 0.6)'
    forward_marker = '#F59E0B'


# =============================================================================
# EXPORTS
# =============================================================================
__all__ = [
    # Core
    'ChartType', 'ChartSchema', 'CHART_REGISTRY', 'THEME',
    # Accessors
    'get_chart_schema', 'get_chart_config', 'get_chart_colors',
    'build_plotly_layout', 'get_base_layout',
    # Status
    'STATUS_COLORS', 'PERCENTILE_THRESHOLDS', 'get_status_color', 'get_percentile_status',
    # Data
    'Y_AXIS_DISPLAY_RANGE', 'OUTLIER_LIMITS', 'get_y_range', 'get_outlier_limits',
    'filter_outliers', 'calculate_y_range', 'calculate_statistics',
    # Formatters
    'format_value', 'format_ratio', 'format_percent', 'format_zscore', 'format_change',
    # Utils
    'list_chart_types',
    # Legacy
    'CHART_SCHEMA', 'StatusColors', 'ChartColors', 'HistogramConfig',
]
