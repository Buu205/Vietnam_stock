"""
Advanced Chart Components
=========================
Professional financial visualization components for Vietnam Finance Dashboard.

Contents:
- sector_correlation_heatmap(): Sector correlation matrix
- market_cap_treemap(): Market cap distribution by sector/industry
- pnl_waterfall(): P&L breakdown waterfall chart
- bullet_chart(): Performance vs target comparison
- radar_comparison(): Multi-variable ticker vs sector comparison
- gauge_chart(): Single metric with target indicator
- sparkline(): Minimal inline trend chart
- sunburst_allocation(): Hierarchical allocation breakdown

Usage:
    from WEBAPP.components.charts.advanced_charts import (
        sector_correlation_heatmap,
        market_cap_treemap,
        gauge_chart
    )

Created: 2025-12-21
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple

# ============================================================================
# THEME CONSTANTS (Match chart_schema.py)
# ============================================================================
DARK_THEME = {
    'bg_void': '#0F0B1E',
    'bg_deep': '#1A1625',
    'bg_surface': '#252033',
    'text_primary': '#F1F5F9',
    'text_secondary': '#94A3B8',
    'text_muted': '#64748B',
    'purple_primary': '#8B5CF6',
    'cyan_accent': '#06B6D4',
    'amber_warning': '#F59E0B',
    'green_positive': '#22C55E',
    'red_negative': '#EF4444',
    'glass_bg': 'rgba(139, 92, 246, 0.08)',
    'glass_border': 'rgba(139, 92, 246, 0.15)',
}


def _get_base_layout(title: str = "", height: int = 400) -> Dict:
    """Get base Plotly layout for dark theme."""
    return {
        'template': 'plotly_dark',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': DARK_THEME['bg_void'],
        'font': {'color': DARK_THEME['text_secondary'], 'family': 'JetBrains Mono'},
        'title': {
            'text': title,
            'font': {'color': DARK_THEME['text_primary'], 'size': 14},
            'x': 0,
            'xanchor': 'left'
        },
        'height': height,
        'margin': {'l': 40, 'r': 20, 't': 50, 'b': 40}
    }


# ============================================================================
# 1. HEATMAP - SECTOR CORRELATION MATRIX
# ============================================================================
def sector_correlation_heatmap(
    correlation_matrix: pd.DataFrame,
    title: str = "Sector Correlation Matrix",
    height: int = 500,
    show_values: bool = True
) -> go.Figure:
    """
    Create sector correlation heatmap with dark theme.

    Args:
        correlation_matrix: DataFrame with correlation values (-1 to 1)
        title: Chart title
        height: Chart height in pixels
        show_values: Whether to show correlation values in cells

    Returns:
        Plotly Figure object
    """
    # Custom colorscale: Red (negative) -> Neutral -> Purple/Cyan (positive)
    colorscale = [
        [0.0, '#EF4444'],    # -1: Strong negative (red)
        [0.25, '#F59E0B'],   # -0.5: Weak negative (amber)
        [0.5, DARK_THEME['bg_deep']],    # 0: Neutral
        [0.75, '#06B6D4'],   # 0.5: Weak positive (cyan)
        [1.0, '#8B5CF6'],    # 1: Strong positive (purple)
    ]

    fig = px.imshow(
        correlation_matrix,
        color_continuous_scale=colorscale,
        aspect='auto',
        zmin=-1,
        zmax=1,
        text_auto='.2f' if show_values else False
    )

    fig.update_layout(**_get_base_layout(title, height))
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Correlation",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=['-1', '-0.5', '0', '0.5', '1']
        )
    )

    return fig


# ============================================================================
# 2. TREEMAP - MARKET CAP DISTRIBUTION
# ============================================================================
def market_cap_treemap(
    df: pd.DataFrame,
    path_columns: List[str] = ['sector', 'industry', 'ticker'],
    values_column: str = 'market_cap',
    color_column: str = 'pct_change',
    title: str = "Market Cap Distribution",
    height: int = 500
) -> go.Figure:
    """
    Create treemap showing market cap hierarchy.

    Args:
        df: DataFrame with hierarchical data
        path_columns: Column names for hierarchy levels
        values_column: Column for cell sizes
        color_column: Column for cell colors
        title: Chart title
        height: Chart height

    Returns:
        Plotly Figure object
    """
    # Red -> Neutral -> Green colorscale for price changes
    colorscale = ['#EF4444', DARK_THEME['bg_deep'], '#22C55E']

    fig = px.treemap(
        df,
        path=path_columns,
        values=values_column,
        color=color_column,
        color_continuous_scale=colorscale,
        color_continuous_midpoint=0
    )

    fig.update_layout(**_get_base_layout(title, height))
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0)
    )

    return fig


# ============================================================================
# 3. WATERFALL - P&L BREAKDOWN
# ============================================================================
def pnl_waterfall(
    items: List[str],
    values: List[float],
    title: str = "P&L Breakdown",
    height: int = 400
) -> go.Figure:
    """
    Create waterfall chart for P&L breakdown.

    First item is 'absolute' (starting value like Revenue).
    Middle items are 'relative' (costs, expenses).
    Last item is 'total' (net result).

    Args:
        items: List of item names (e.g., ['Revenue', 'COGS', 'Expenses', 'Net Income'])
        values: List of values (negative for costs)
        title: Chart title
        height: Chart height

    Returns:
        Plotly Figure object
    """
    # Determine measure type for each item
    n = len(items)
    measures = ['absolute'] + ['relative'] * (n - 2) + ['total']

    fig = go.Figure(go.Waterfall(
        orientation='v',
        measure=measures,
        x=items,
        y=values,
        decreasing={'marker': {'color': DARK_THEME['red_negative']}},
        increasing={'marker': {'color': DARK_THEME['green_positive']}},
        totals={'marker': {'color': DARK_THEME['purple_primary']}},
        textposition='outside',
        text=[f'{v:,.0f}' for v in values],
        textfont={'color': DARK_THEME['text_secondary']},
        connector={'line': {'color': DARK_THEME['glass_border']}}
    ))

    fig.update_layout(**_get_base_layout(title, height))
    fig.update_layout(showlegend=False)

    return fig


# ============================================================================
# 4. BULLET CHART - PERFORMANCE VS TARGET
# ============================================================================
def bullet_chart(
    metric: str,
    actual: float,
    target: float,
    ranges: List[float],
    title: str = "",
    height: int = 80
) -> go.Figure:
    """
    Create bullet chart comparing actual vs target with background ranges.

    Args:
        metric: Metric name
        actual: Actual value
        target: Target value
        ranges: List of 3 values for [good, acceptable, poor] ranges
        title: Chart title (defaults to metric name)
        height: Chart height

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # Background ranges (poor -> acceptable -> good)
    range_colors = [
        'rgba(200,230,201,0.2)',  # Good (green tint)
        'rgba(255,249,196,0.2)',  # Acceptable (yellow tint)
        'rgba(255,205,210,0.2)',  # Poor (red tint)
    ]

    max_range = max(ranges)

    for i, (r, c) in enumerate(zip(ranges, range_colors)):
        fig.add_shape(
            type='rect',
            x0=0, x1=r,
            y0=-0.2, y1=0.2,
            fillcolor=c,
            line_width=0
        )

    # Actual bar
    fig.add_trace(go.Bar(
        x=[actual],
        y=[metric],
        orientation='h',
        marker_color=DARK_THEME['purple_primary'],
        width=0.3,
        showlegend=False
    ))

    # Target marker (white line)
    fig.add_shape(
        type='line',
        x0=target, x1=target,
        y0=-0.3, y1=0.3,
        line=dict(color='white', width=3)
    )

    fig.update_layout(**_get_base_layout(title or metric, height))
    fig.update_layout(
        margin=dict(l=100, r=20, t=30, b=10),
        xaxis=dict(range=[0, max_range * 1.1], showgrid=False),
        yaxis=dict(showticklabels=True)
    )

    return fig


# ============================================================================
# 5. RADAR CHART - MULTI-VARIABLE COMPARISON
# ============================================================================
def radar_comparison(
    ticker_values: List[float],
    sector_values: List[float],
    categories: List[str],
    ticker_name: str = "Ticker",
    sector_name: str = "Sector Avg",
    title: str = "Performance Profile",
    height: int = 400
) -> go.Figure:
    """
    Create radar chart comparing ticker vs sector on multiple metrics.

    Args:
        ticker_values: Values for the ticker (normalized 0-100)
        sector_values: Values for sector average (normalized 0-100)
        categories: List of metric names
        ticker_name: Name for ticker legend
        sector_name: Name for sector legend
        title: Chart title
        height: Chart height

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # Close the polygon by repeating first value
    ticker_closed = ticker_values + [ticker_values[0]]
    sector_closed = sector_values + [sector_values[0]]
    categories_closed = categories + [categories[0]]

    # Ticker trace (filled)
    fig.add_trace(go.Scatterpolar(
        r=ticker_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(139, 92, 246, 0.2)',
        line_color=DARK_THEME['purple_primary'],
        name=ticker_name
    ))

    # Sector average trace (dashed line)
    fig.add_trace(go.Scatterpolar(
        r=sector_closed,
        theta=categories_closed,
        line=dict(color=DARK_THEME['cyan_accent'], dash='dash'),
        name=sector_name
    ))

    fig.update_layout(**_get_base_layout(title, height))
    fig.update_layout(
        polar=dict(
            bgcolor=DARK_THEME['bg_void'],
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor=DARK_THEME['glass_border'],
                linecolor=DARK_THEME['glass_border']
            ),
            angularaxis=dict(
                gridcolor=DARK_THEME['glass_border'],
                linecolor=DARK_THEME['glass_border']
            )
        ),
        showlegend=True,
        legend=dict(
            font=dict(color=DARK_THEME['text_primary']),
            bgcolor='rgba(0,0,0,0)'
        )
    )

    return fig


# ============================================================================
# 6. GAUGE CHART - SINGLE METRIC FOCUS
# ============================================================================
def gauge_chart(
    value: float,
    title: str = "",
    min_val: float = 0,
    max_val: float = 100,
    target: float = 50,
    height: int = 200
) -> go.Figure:
    """
    Create gauge chart with target marker.

    Args:
        value: Current value
        title: Metric name
        min_val: Minimum value
        max_val: Maximum value
        target: Target value (shown as threshold line)
        height: Chart height

    Returns:
        Plotly Figure object
    """
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=value,
        title={'text': title, 'font': {'color': DARK_THEME['text_secondary'], 'size': 14}},
        gauge={
            'axis': {
                'range': [min_val, max_val],
                'tickcolor': DARK_THEME['text_muted']
            },
            'bar': {'color': DARK_THEME['purple_primary']},
            'bgcolor': DARK_THEME['bg_deep'],
            'borderwidth': 0,
            'steps': [
                {'range': [min_val, target * 0.7], 'color': 'rgba(239,68,68,0.3)'},
                {'range': [target * 0.7, target], 'color': 'rgba(245,158,11,0.3)'},
                {'range': [target, max_val], 'color': 'rgba(34,197,94,0.3)'}
            ],
            'threshold': {
                'line': {'color': 'white', 'width': 2},
                'thickness': 0.8,
                'value': target
            }
        },
        number={'font': {'color': DARK_THEME['text_primary'], 'size': 28}}
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        height=height,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


# ============================================================================
# 7. SPARKLINE - INLINE TREND
# ============================================================================
def sparkline(
    values: List[float],
    color: str = '#8B5CF6',
    height: int = 40,
    width: int = 120,
    show_endpoints: bool = True
) -> go.Figure:
    """
    Create minimal sparkline chart for inline display.

    Args:
        values: List of values
        color: Line color (hex)
        height: Chart height in pixels
        width: Chart width in pixels
        show_endpoints: Show dots at start and end

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # Main line
    fig.add_trace(go.Scatter(
        y=values,
        mode='lines',
        line=dict(color=color, width=1.5),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}',
        showlegend=False
    ))

    # Endpoint markers
    if show_endpoints and len(values) >= 2:
        fig.add_trace(go.Scatter(
            x=[0, len(values) - 1],
            y=[values[0], values[-1]],
            mode='markers',
            marker=dict(color=color, size=4),
            showlegend=False
        ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        width=width,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


# ============================================================================
# 8. SUNBURST - HIERARCHICAL PROPORTIONS
# ============================================================================
def sunburst_allocation(
    df: pd.DataFrame,
    path_columns: List[str] = ['category', 'subcategory', 'item'],
    values_column: str = 'value',
    color_column: str = 'growth',
    title: str = "Allocation Breakdown",
    height: int = 500
) -> go.Figure:
    """
    Create sunburst chart for hierarchical allocation.

    Args:
        df: DataFrame with hierarchical data
        path_columns: Column names for hierarchy levels
        values_column: Column for segment sizes
        color_column: Column for segment colors
        title: Chart title
        height: Chart height

    Returns:
        Plotly Figure object
    """
    colorscale = ['#EF4444', DARK_THEME['bg_deep'], '#22C55E']

    fig = px.sunburst(
        df,
        path=path_columns,
        values=values_column,
        color=color_column,
        color_continuous_scale=colorscale,
        color_continuous_midpoint=0
    )

    fig.update_layout(**_get_base_layout(title, height))
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0)
    )

    return fig


# ============================================================================
# UTILITY: CREATE SAMPLE DATA FOR TESTING
# ============================================================================
def create_sample_correlation_matrix() -> pd.DataFrame:
    """Create sample correlation matrix for testing."""
    sectors = ['Banking', 'Real Estate', 'Technology', 'Consumer', 'Industrial']
    n = len(sectors)
    data = np.random.uniform(-1, 1, (n, n))
    # Make symmetric
    data = (data + data.T) / 2
    np.fill_diagonal(data, 1)
    return pd.DataFrame(data, index=sectors, columns=sectors)


def create_sample_treemap_data() -> pd.DataFrame:
    """Create sample treemap data for testing."""
    return pd.DataFrame({
        'sector': ['Banking'] * 3 + ['Real Estate'] * 2,
        'industry': ['Commercial', 'Commercial', 'Investment', 'Residential', 'Commercial'],
        'ticker': ['VCB', 'ACB', 'SSI', 'VIC', 'VHM'],
        'market_cap': [500000, 300000, 100000, 400000, 350000],
        'pct_change': [2.5, -1.2, 0.5, -3.0, 1.8]
    })
