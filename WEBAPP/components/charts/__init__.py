"""
Chart Components
================

Reusable Plotly chart builders.

Modules:
- plotly_builders: Base chart builder class
- valuation_charts: Valuation-specific charts (PE/PB distribution, box plots)
- advanced_charts: Professional financial charts (heatmap, treemap, waterfall, etc.)

Created: 2025-12-16
Updated: 2025-12-21 - Added advanced_charts module
"""

from .plotly_builders import PlotlyChartBuilder
from .valuation_charts import (
    distribution_candlestick,
    valuation_box_with_markers,
    line_with_statistical_bands,
    histogram_with_stats,
    render_status_legend,
    render_marker_legend
)
from .advanced_charts import (
    sector_correlation_heatmap,
    market_cap_treemap,
    pnl_waterfall,
    bullet_chart,
    radar_comparison,
    gauge_chart,
    sparkline,
    sunburst_allocation
)

__all__ = [
    'PlotlyChartBuilder',
    # Valuation charts
    'distribution_candlestick',
    'valuation_box_with_markers',
    'line_with_statistical_bands',
    'histogram_with_stats',
    'render_status_legend',
    'render_marker_legend',
    # Advanced charts
    'sector_correlation_heatmap',
    'market_cap_treemap',
    'pnl_waterfall',
    'bullet_chart',
    'radar_comparison',
    'gauge_chart',
    'sparkline',
    'sunburst_allocation'
]
