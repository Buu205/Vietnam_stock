"""
Unified Valuation Chart Components
==================================
Standardized chart builders for valuation dashboards.

Chart Types:
    - Type A: distribution_candlestick() - Historical distribution only
    - Type B: valuation_box_with_markers() - Historical + Forward (BSC forecast)
    - Type C: line_with_statistical_bands() - Time series with ±1σ, ±2σ bands

All charts use centralized config from valuation_config.py for:
    - Colors (STATUS_COLORS, CHART_COLORS)
    - Outlier limits (OUTLIER_LIMITS)
    - Marker sizes (MARKER_SIZES)
    - Formatters (format_ratio, format_percent, format_zscore)

Usage:
    from WEBAPP.components.charts.valuation_charts import (
        distribution_candlestick,
        valuation_box_with_markers,
        line_with_statistical_bands
    )
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import List, Dict, Optional, Tuple
from datetime import timedelta

from WEBAPP.core.valuation_config import (
    OUTLIER_LIMITS, STATUS_COLORS, CHART_COLORS, MARKER_SIZES,
    format_ratio, format_percent, format_zscore,
    get_status_color, get_percentile_status, filter_outliers, calculate_statistics
)
from WEBAPP.core.chart_schema import (
    CHART_SCHEMA, get_chart_config, get_y_range, get_base_layout,
    HistogramConfig
)


# =============================================================================
# CHART LAYOUT DEFAULTS
# =============================================================================
def _get_base_layout(height: int = 500, title: str = "") -> dict:
    """Get base layout for all valuation charts."""
    return {
        'title': dict(
            text=title,
            font=dict(family='Space Grotesk, sans-serif', size=16, color='#E8E8E8')
        ),
        'height': height,
        'template': 'plotly_dark',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': dict(family='JetBrains Mono, monospace', color='#94A3B8'),
        'xaxis': dict(
            gridcolor='rgba(255, 255, 255, 0.05)',
            showline=True,
            linecolor='rgba(255,255,255,0.1)'
        ),
        'yaxis': dict(
            gridcolor='rgba(255, 255, 255, 0.05)',
            zeroline=False,
            showline=True,
            linecolor='rgba(255,255,255,0.1)'
        ),
        'hoverlabel': dict(
            bgcolor='#1A1625',
            bordercolor='#8B5CF6',
            font=dict(color='#F8FAFC')
        )
    }


# =============================================================================
# TYPE A: DISTRIBUTION CANDLESTICK (Historical Only)
# =============================================================================
def distribution_candlestick(
    data: List[Dict],
    metric_label: str = "PE",
    height: int = 500,
    y_range: Tuple[float, float] = None,
    show_legend: bool = True,
    title: str = None
) -> go.Figure:
    """
    Type A: Distribution candlestick chart (historical only).

    Creates a candlestick-style chart showing valuation distribution:
        - Body: P25-P75 (IQR)
        - Whiskers: Min-Max (or P5-P95 if provided)
        - Colored dot: Current value (color = status)

    Args:
        data: List of dicts with keys:
            - symbol: str
            - p5 or min: float (whisker low)
            - p25: float (box low)
            - median or p50: float
            - p75: float (box high)
            - p95 or max: float (whisker high)
            - current: float
            - percentile: float (0-100)
            - status: str (optional, calculated if missing)
        metric_label: "PE" | "PB" | "PS" | "EV/EBITDA"
        height: Chart height in pixels
        y_range: Optional (min, max) tuple for y-axis
        show_legend: Show color legend below chart
        title: Optional chart title

    Returns:
        Plotly Figure object

    Example:
        >>> stats = valuation_service.get_industry_candle_data('Ngân hàng', 'PE')
        >>> fig = distribution_candlestick(stats, metric_label='PE')
        >>> st.plotly_chart(fig, use_container_width=True)
    """
    if not data:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='#94A3B8')
        )
        return fig

    # Sort by current value
    data = sorted(data, key=lambda x: x.get('current', 0) or 0)

    symbols = [d['symbol'] for d in data]

    fig = go.Figure()

    for d in data:
        symbol = d['symbol']
        p25 = d.get('p25', 0)
        p75 = d.get('p75', 0)
        high_val = d.get('max', d.get('p95', p75))
        low_val = d.get('min', d.get('p5', p25))
        current = d.get('current')
        percentile = d.get('percentile', 50)
        status = d.get('status', get_percentile_status(percentile))
        median = d.get('median', d.get('p50', (p25 + p75) / 2))

        # Add candlestick (body = P25-P75, whiskers = min-max or P5-P95)
        fig.add_trace(go.Candlestick(
            x=[symbol],
            open=[round(p25, 2)],
            high=[round(high_val, 2)],
            low=[round(low_val, 2)],
            close=[round(p75, 2)],
            name=symbol,
            showlegend=False,
            increasing_line_color=CHART_COLORS['body'],
            decreasing_line_color=CHART_COLORS['body'],
            increasing_fillcolor=CHART_COLORS['body_fill'],
            decreasing_fillcolor=CHART_COLORS['body_fill'],
        ))

        # Add current value marker
        if current is not None and not pd.isna(current):
            dot_color = get_status_color(percentile)

            fig.add_trace(go.Scatter(
                x=[symbol],
                y=[current],
                mode='markers',
                marker=dict(
                    size=MARKER_SIZES['trailing'],
                    color=dot_color,
                    symbol='circle',
                    line=dict(width=MARKER_SIZES['border_width'], color='white')
                ),
                name=f"{symbol} Current",
                showlegend=False,
                hovertemplate=(
                    f'<b>{symbol}</b><br>' +
                    f'Current: {current:.2f}x<br>' +
                    f'Percentile: {percentile:.1f}%<br>' +
                    f'Median: {median:.2f}x<br>' +
                    f'Status: {status}<br>' +
                    '<extra></extra>'
                )
            ))

    # Layout
    layout = _get_base_layout(height, title or f"{metric_label} Distribution")
    layout['xaxis'].update({
        'categoryorder': 'array',
        'categoryarray': symbols,
        'rangeslider': dict(visible=False),
        'tickangle': -45,
        'tickfont': dict(size=10, color='#FFFFFF'),
        'fixedrange': True
    })
    layout['yaxis'].update({
        'title': metric_label,
        'fixedrange': True
    })
    layout['dragmode'] = False

    # Apply y_range if provided, otherwise auto-scale based on metric
    if y_range:
        layout['yaxis']['range'] = list(y_range)
    else:
        limits = OUTLIER_LIMITS.get(metric_label.upper().replace('/', '_'), {'max': 100})
        if metric_label.upper() == 'PB':
            layout['yaxis']['range'] = [0, 8]
        elif metric_label.upper() in ['PE', 'PS']:
            layout['yaxis']['range'] = [0, min(50, limits['max'])]

    fig.update_layout(**layout)

    return fig


# =============================================================================
# TYPE B: VALUATION BOX WITH MARKERS (Historical + Forward)
# =============================================================================
def valuation_box_with_markers(
    stats_data: List[Dict],
    pe_forward_data: Dict = None,
    pe_forward_2026_data: Dict = None,
    title: str = "PE Distribution: Trailing vs Forward",
    metric_label: str = "PE",
    height: int = 500,
    show_legend: bool = True
) -> go.Figure:
    """
    Type B: Box chart with trailing (circle) and forward (diamond) markers.

    Visual representation (candlestick-style):
        - Body (thick bar): P25-P75 (IQR) range
        - Whiskers (thin line): P5-P95 range
        - Circle (●): PE Trailing (current value)
        - Diamond (◇): PE Forward 2025 (BSC forecast) - hollow
        - Diamond (◆): PE Forward 2026 (BSC forecast) - filled

    Args:
        stats_data: List of dicts from ValuationService.get_industry_candle_data()
                   Each dict: {symbol, current, p25, median, p75, p5, p95, percentile, status}
        pe_forward_data: Dict mapping symbol -> pe_forward_2025 value (e.g., from BSC forecast)
                        Example: {'ACB': 8.5, 'VCB': 12.3, ...}
        pe_forward_2026_data: Dict mapping symbol -> pe_forward_2026 value (optional)
        title: Chart title
        metric_label: Label for metric (PE, PB, etc.)
        height: Chart height in pixels
        show_legend: Show legend

    Returns:
        Plotly Figure with box + markers

    Example:
        >>> stats = val_svc.get_industry_candle_data('Ngân hàng', metric='PE')
        >>> pe_fwd_2025 = dict(zip(bsc_df['symbol'], bsc_df['pe_fwd_2025']))
        >>> pe_fwd_2026 = dict(zip(bsc_df['symbol'], bsc_df['pe_fwd_2026']))
        >>> fig = valuation_box_with_markers(stats, pe_fwd_2025, pe_fwd_2026, title='Bank PE: TTM vs 2025F vs 2026F')
    """
    if not stats_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='#94A3B8')
        )
        return fig

    if pe_forward_data is None:
        pe_forward_data = {}
    if pe_forward_2026_data is None:
        pe_forward_2026_data = {}

    # Sort by current PE (trailing)
    stats_data = sorted(stats_data, key=lambda x: x.get('current', 0) or 0)

    # Extract data for plotting
    symbols = [d['symbol'] for d in stats_data]
    p25_vals = [d.get('p25', 0) for d in stats_data]
    p75_vals = [d.get('p75', 0) for d in stats_data]
    p5_vals = [d.get('p5', d.get('min', 0)) for d in stats_data]
    p95_vals = [d.get('p95', d.get('max', 0)) for d in stats_data]
    median_vals = [d.get('median', 0) for d in stats_data]
    current_vals = [d.get('current', 0) for d in stats_data]
    statuses = [d.get('status', 'Fair') for d in stats_data]

    # Get forward PE values
    forward_vals = [pe_forward_data.get(s) for s in symbols]
    forward_2026_vals = [pe_forward_2026_data.get(s) for s in symbols]

    # Color mapping using centralized config
    status_color_map = {
        'Very Cheap': STATUS_COLORS['very_cheap'],
        'Cheap': STATUS_COLORS['cheap'],
        'Fair': STATUS_COLORS['fair'],
        'Expensive': STATUS_COLORS['expensive'],
        'Very Expensive': STATUS_COLORS['very_expensive']
    }

    fig = go.Figure()

    # Whiskers (P5-P95) using error bars
    fig.add_trace(go.Scatter(
        x=symbols,
        y=[(p5 + p95) / 2 for p5, p95 in zip(p5_vals, p95_vals)],
        mode='markers',
        marker=dict(size=0.1, color='rgba(0,0,0,0)'),
        error_y=dict(
            type='data',
            symmetric=False,
            array=[(p95 - (p5 + p95) / 2) for p5, p95 in zip(p5_vals, p95_vals)],
            arrayminus=[((p5 + p95) / 2 - p5) for p5, p95 in zip(p5_vals, p95_vals)],
            color='rgba(148, 163, 184, 0.5)',
            thickness=1.5,
            width=4
        ),
        showlegend=False,
        hoverinfo='skip'
    ))

    # Box body (P25-P75) using bar chart
    box_colors = [status_color_map.get(s, '#6B7280') for s in statuses]
    fig.add_trace(go.Bar(
        x=symbols,
        y=[p75 - p25 for p25, p75 in zip(p25_vals, p75_vals)],
        base=p25_vals,
        marker=dict(
            color=box_colors,
            opacity=0.6,
            line=dict(color=box_colors, width=1)
        ),
        width=0.6,
        name='P25-P75 Range',
        showlegend=True,
        hovertemplate='<b>%{x}</b><br>P25: %{base:.1f}x<br>P75: %{customdata:.1f}x<br><extra></extra>',
        customdata=p75_vals
    ))

    # Median line within box
    fig.add_trace(go.Scatter(
        x=symbols,
        y=median_vals,
        mode='markers',
        marker=dict(symbol='line-ew', size=12, line=dict(width=2, color='white')),
        showlegend=False,
        hoverinfo='skip'
    ))

    # Trailing PE markers (circle)
    trailing_colors = [status_color_map.get(s, '#6B7280') for s in statuses]
    fig.add_trace(go.Scatter(
        x=symbols,
        y=current_vals,
        mode='markers',
        name=f'{metric_label} Trailing (TTM)',
        marker=dict(
            symbol='circle',
            size=MARKER_SIZES['trailing'],
            color=trailing_colors,
            line=dict(color='white', width=MARKER_SIZES['border_width'])
        ),
        hovertemplate=f'<b>%{{x}}</b><br>{metric_label} TTM: %{{y:.1f}}x<br><extra></extra>'
    ))

    # Forward PE 2025 markers (hollow diamond)
    forward_x = []
    forward_y = []
    forward_hover = []
    for i, (sym, fwd) in enumerate(zip(symbols, forward_vals)):
        if fwd is not None and fwd > 0:
            forward_x.append(sym)
            forward_y.append(fwd)
            trailing = current_vals[i]
            change_pct = ((fwd - trailing) / trailing * 100) if trailing > 0 else 0
            forward_hover.append(f'{fwd:.1f}x ({change_pct:+.1f}%)')

    if forward_x:
        fig.add_trace(go.Scatter(
            x=forward_x,
            y=forward_y,
            mode='markers',
            name=f'{metric_label} 2025F',
            marker=dict(
                symbol='diamond-open',  # Hollow diamond
                size=MARKER_SIZES['forward'],
                color='#F59E0B',  # Amber for 2025
                line=dict(color='#F59E0B', width=MARKER_SIZES['border_width'])
            ),
            hovertemplate=f'<b>%{{x}}</b><br>{metric_label} 2025F: %{{customdata}}<br><extra></extra>',
            customdata=forward_hover
        ))

    # Forward PE 2026 markers (filled diamond)
    forward_2026_x = []
    forward_2026_y = []
    forward_2026_hover = []
    for i, (sym, fwd) in enumerate(zip(symbols, forward_2026_vals)):
        if fwd is not None and fwd > 0:
            forward_2026_x.append(sym)
            forward_2026_y.append(fwd)
            trailing = current_vals[i]
            change_pct = ((fwd - trailing) / trailing * 100) if trailing > 0 else 0
            forward_2026_hover.append(f'{fwd:.1f}x ({change_pct:+.1f}%)')

    if forward_2026_x:
        fig.add_trace(go.Scatter(
            x=forward_2026_x,
            y=forward_2026_y,
            mode='markers',
            name=f'{metric_label} 2026F',
            marker=dict(
                symbol='diamond',  # Filled diamond
                size=MARKER_SIZES['forward'],
                color='#8B5CF6',  # Purple for 2026
                line=dict(color='white', width=MARKER_SIZES['border_width'])
            ),
            hovertemplate=f'<b>%{{x}}</b><br>{metric_label} 2026F: %{{customdata}}<br><extra></extra>',
            customdata=forward_2026_hover
        ))

    # Sector median reference line
    overall_median = sum(median_vals) / len(median_vals) if median_vals else 0
    fig.add_hline(
        y=overall_median,
        line_dash="dot",
        line_color="gray",
        opacity=0.5,
        annotation_text=f"Sector Median: {overall_median:.1f}x",
        annotation_position="top right",
        annotation_font=dict(size=10, color='#94A3B8')
    )

    # Layout
    layout = _get_base_layout(height, title)
    layout.update({
        'xaxis_title': 'Symbol',
        'yaxis_title': f'{metric_label} Ratio',
        'showlegend': show_legend,
        'legend': dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=10)
        ),
        'barmode': 'overlay'
    })
    layout['xaxis'].update({
        'tickangle': -45,
        'tickfont': dict(size=9)
    })

    fig.update_layout(**layout)

    return fig


# =============================================================================
# TYPE C: LINE WITH STATISTICAL BANDS
# =============================================================================
def line_with_statistical_bands(
    df: pd.DataFrame,
    date_col: str = 'date',
    value_col: str = 'pe_ttm',
    metric_label: str = "PE",
    height: int = 400,
    title: str = None,
    show_2sd: bool = True,
    days_limit: int = None
) -> Tuple[go.Figure, Dict]:
    """
    Type C: Line chart with ±1σ, ±2σ statistical bands.

    Creates a time series chart with:
        - Main value line (teal)
        - Median line (gold, solid)
        - Mean line (blue, dashed)
        - ±1σ band (teal, transparent)
        - ±2σ band (blue, more transparent)

    Args:
        df: DataFrame with date and value columns
        date_col: Name of date column
        value_col: Name of value column (e.g., 'pe_ttm', 'pb')
        metric_label: Display label (e.g., "PE TTM", "P/B")
        height: Chart height in pixels
        title: Optional chart title
        show_2sd: Show ±2σ band (default True)
        days_limit: Limit data to last N days (optional)

    Returns:
        Tuple of (figure, stats_dict) where stats_dict contains:
            - current, median, mean, std, z_score, percentile

    Example:
        >>> history = sector_service.get_sector_history('Ngân hàng')
        >>> fig, stats = line_with_statistical_bands(history, value_col='pe_ttm')
        >>> st.plotly_chart(fig, use_container_width=True)
        >>> st.metric("Z-Score", format_zscore(stats['z_score']))
    """
    if df.empty or value_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='#94A3B8')
        )
        return fig, {}

    # Copy and prepare data
    plot_df = df.copy()
    plot_df[date_col] = pd.to_datetime(plot_df[date_col])
    plot_df = plot_df.sort_values(date_col)

    # Apply days limit if specified
    if days_limit:
        plot_df = plot_df.tail(days_limit)

    # Extract metric type for outlier filtering
    metric_type = metric_label.upper().replace(' ', '_').replace('/', '_').split('_')[0]

    # Filter outliers
    metric_data = plot_df[value_col].dropna()
    filtered_data = filter_outliers(metric_data, metric_type)

    if len(filtered_data) < 20:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data (< 20 points)",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='#94A3B8')
        )
        return fig, {}

    # Filter plot_df to match
    limits = OUTLIER_LIMITS.get(metric_type, {'min': 0, 'max': 100})
    plot_df = plot_df[
        (plot_df[value_col] >= limits['min']) &
        (plot_df[value_col] <= limits['max'])
    ]

    # Calculate statistics
    current_val = plot_df[value_col].iloc[-1]
    median_val = filtered_data.median()
    mean_val = filtered_data.mean()
    std_val = filtered_data.std()

    plus_1sd = mean_val + std_val
    plus_2sd = mean_val + 2 * std_val
    minus_1sd = max(0, mean_val - std_val)
    minus_2sd = max(0, mean_val - 2 * std_val)

    z_score = (current_val - mean_val) / std_val if std_val > 0 else 0
    percentile = (filtered_data < current_val).mean() * 100

    fig = go.Figure()

    # ±2σ band (optional)
    if show_2sd:
        fig.add_trace(go.Scatter(
            x=plot_df[date_col],
            y=[plus_2sd] * len(plot_df),
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=plot_df[date_col],
            y=[minus_2sd] * len(plot_df),
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor=CHART_COLORS['band_2sd'],
            showlegend=False,
            hoverinfo='skip'
        ))

    # ±1σ band
    fig.add_trace(go.Scatter(
        x=plot_df[date_col],
        y=[plus_1sd] * len(plot_df),
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=plot_df[date_col],
        y=[minus_1sd] * len(plot_df),
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor=CHART_COLORS['band_1sd'],
        showlegend=False,
        hoverinfo='skip'
    ))

    # Main value line
    fig.add_trace(go.Scatter(
        x=plot_df[date_col],
        y=plot_df[value_col],
        name=metric_label,
        mode='lines',
        line=dict(color=CHART_COLORS['main_line'], width=2.5),
        hovertemplate=f'<b>Date</b>: %{{x}}<br><b>{metric_label}</b>: %{{y:.2f}}x<extra></extra>'
    ))

    # Median line
    fig.add_hline(
        y=median_val,
        line=dict(color=CHART_COLORS['median_line'], width=2, dash='solid'),
        annotation=dict(
            text=f'Med: {median_val:.1f}x',
            font=dict(color=CHART_COLORS['median_line'], size=10),
            bgcolor='rgba(16, 24, 32, 0.9)',
            borderpad=3,
            xanchor='right'
        )
    )

    # Mean line
    fig.add_hline(
        y=mean_val,
        line=dict(color=CHART_COLORS['mean_line'], width=1.5, dash='dash'),
        annotation=dict(
            text=f'μ: {mean_val:.1f}x',
            font=dict(color=CHART_COLORS['mean_line'], size=9),
            xanchor='left'
        )
    )

    # ±1σ lines
    fig.add_hline(
        y=plus_1sd,
        line=dict(color=CHART_COLORS['sd_line'], width=1, dash='dot'),
        annotation=dict(text='+1σ', font=dict(color=CHART_COLORS['sd_line'], size=8), xanchor='left')
    )
    fig.add_hline(
        y=minus_1sd,
        line=dict(color=CHART_COLORS['sd_line'], width=1, dash='dot'),
        annotation=dict(text='-1σ', font=dict(color=CHART_COLORS['sd_line'], size=8), xanchor='left')
    )

    # ±2σ lines (subtle)
    if show_2sd:
        fig.add_hline(y=plus_2sd, line=dict(color='rgba(74, 123, 200, 0.5)', width=1, dash='dot'))
        fig.add_hline(y=minus_2sd, line=dict(color='rgba(74, 123, 200, 0.5)', width=1, dash='dot'))

    # Auto-scale y-axis
    y_min = max(0, filtered_data.min() * 0.9)
    y_max = filtered_data.max() * 1.1

    # Layout
    layout = _get_base_layout(height, title or f"{metric_label} with Statistical Bands")
    layout['yaxis'].update({
        'title': metric_label,
        'range': [y_min, y_max]
    })
    layout['xaxis'].update({
        'tickformat': '%b %Y',
        'tickmode': 'auto',
        'nticks': 8,
        'tickangle': 0,
        'rangeslider': dict(visible=False)
    })
    layout['showlegend'] = False

    # Add right padding for latest data visibility
    if not plot_df.empty:
        last_date = plot_df[date_col].max()
        padding_days = max(10, len(plot_df) // 50)  # ~2% padding
        layout['xaxis']['range'] = [plot_df[date_col].min(), last_date + timedelta(days=padding_days)]

    fig.update_layout(**layout)

    # Stats dict
    stats = {
        'current': current_val,
        'median': median_val,
        'mean': mean_val,
        'std': std_val,
        'z_score': z_score,
        'percentile': percentile,
        'plus_1sd': plus_1sd,
        'minus_1sd': minus_1sd,
        'plus_2sd': plus_2sd,
        'minus_2sd': minus_2sd
    }

    return fig, stats


# =============================================================================
# TYPE A3: HISTOGRAM WITH STATS
# =============================================================================
def histogram_with_stats(
    data: pd.Series,
    metric_label: str = "PE",
    height: int = None,
    bins: int = None,
    show_mean_std: bool = True,
    current_value: float = None,
    title: str = None
) -> go.Figure:
    """
    Type A3: Histogram distribution chart with mean ±1σ, ±2σ vertical lines.

    Creates a histogram showing value distribution with:
        - Bars: Value frequency distribution
        - Dashed lines: Mean, ±1σ, ±2σ
        - Triangle marker: Current value (if provided)

    Args:
        data: Pandas Series with valuation data
        metric_label: "PE" | "PB" | "PS" | "EV/EBITDA"
        height: Chart height in pixels (default from schema: 300)
        bins: Number of histogram bins (default from schema: 35)
        show_mean_std: Show mean and standard deviation lines
        current_value: Current value to mark with triangle
        title: Optional chart title

    Returns:
        Plotly Figure object

    Example:
        >>> pe_data = sector_df['pe_ttm'].dropna()
        >>> fig = histogram_with_stats(pe_data, metric_label='PE', current_value=12.5)
        >>> st.plotly_chart(fig, use_container_width=True)
    """
    config = get_chart_config('histogram')
    height = height or config.height
    bins = bins or config.bins

    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='#94A3B8')
        )
        return fig

    # Filter outliers
    metric_type = metric_label.upper().replace(' ', '_').replace('/', '_').split('_')[0]
    filtered_data = filter_outliers(data.dropna(), metric_type)

    if len(filtered_data) < 10:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data (< 10 points)",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='#94A3B8')
        )
        return fig

    # Calculate statistics
    mean_val = filtered_data.mean()
    std_val = filtered_data.std()
    plus_1sd = mean_val + std_val
    plus_2sd = mean_val + 2 * std_val
    minus_1sd = max(0, mean_val - std_val)
    minus_2sd = max(0, mean_val - 2 * std_val)

    fig = go.Figure()

    # Histogram bars
    fig.add_trace(go.Histogram(
        x=filtered_data,
        nbinsx=bins,
        marker=dict(
            color=config.bar_color,
            opacity=config.bar_opacity,
            line=dict(color='rgba(255,255,255,0.3)', width=0.5)
        ),
        hovertemplate=f'{metric_label}: %{{x:.2f}}x<br>Count: %{{y}}<extra></extra>',
        name=metric_label
    ))

    # Get y-axis max for line heights (approximate based on histogram)
    hist_values, _ = np.histogram(filtered_data, bins=bins)
    y_max = hist_values.max() * 1.1

    if show_mean_std:
        # Mean line
        fig.add_vline(
            x=mean_val,
            line=dict(color=config.mean_line_color, width=2, dash='dash'),
            annotation=dict(
                text=f'μ: {mean_val:.1f}x',
                font=dict(color=config.mean_line_color, size=10),
                bgcolor='rgba(16, 24, 32, 0.9)',
                borderpad=3,
                yanchor='bottom'
            )
        )

        # +1σ line
        fig.add_vline(
            x=plus_1sd,
            line=dict(color=config.sd_line_color, width=1.5, dash='dot'),
            annotation=dict(
                text=f'+1σ',
                font=dict(color=config.sd_line_color, size=9),
                yanchor='bottom'
            )
        )

        # -1σ line
        if minus_1sd > 0:
            fig.add_vline(
                x=minus_1sd,
                line=dict(color=config.sd_line_color, width=1.5, dash='dot'),
                annotation=dict(
                    text=f'-1σ',
                    font=dict(color=config.sd_line_color, size=9),
                    yanchor='bottom'
                )
            )

        # +2σ line (subtle)
        fig.add_vline(
            x=plus_2sd,
            line=dict(color='rgba(74, 123, 200, 0.5)', width=1, dash='dot')
        )

        # -2σ line (subtle)
        if minus_2sd > 0:
            fig.add_vline(
                x=minus_2sd,
                line=dict(color='rgba(74, 123, 200, 0.5)', width=1, dash='dot')
            )

    # Current value marker
    if current_value is not None and config.show_current_marker:
        # Calculate z-score for current value
        z_score = (current_value - mean_val) / std_val if std_val > 0 else 0

        fig.add_trace(go.Scatter(
            x=[current_value],
            y=[y_max * 0.9],
            mode='markers',
            marker=dict(
                symbol='triangle-down',
                size=15,
                color=config.current_marker_color,
                line=dict(color='white', width=1.5)
            ),
            name='Current',
            hovertemplate=(
                f'<b>Current Value</b><br>'
                f'{metric_label}: {current_value:.2f}x<br>'
                f'Z-Score: {z_score:+.2f}σ<br>'
                '<extra></extra>'
            )
        ))

    # Layout
    layout = _get_base_layout(height, title or f"{metric_label} Distribution")
    layout['xaxis'].update({
        'title': metric_label,
        'tickformat': '.1f'
    })
    layout['yaxis'].update({
        'title': 'Frequency',
        'showgrid': True
    })
    layout['showlegend'] = False
    layout['bargap'] = 0.05

    # Apply y_range from schema
    y_range = get_y_range(metric_type)
    if y_range:
        layout['xaxis']['range'] = list(y_range)

    fig.update_layout(**layout)

    return fig


# =============================================================================
# LEGEND COMPONENT
# =============================================================================
def render_status_legend() -> str:
    """
    Return HTML for status legend (for use with st.markdown).

    Example:
        >>> st.markdown(render_status_legend(), unsafe_allow_html=True)
    """
    return """
    <div style="display: flex; gap: 20px; padding: 10px 0; flex-wrap: wrap;">
        <span style="color: #00D4AA;">● <b>Undervalued</b> (&lt; P25)</span>
        <span style="color: #FFD666;">● <b>Fair Value</b> (P25-P75)</span>
        <span style="color: #FF6B6B;">● <b>Expensive</b> (&gt; P75)</span>
    </div>
    """


def render_marker_legend() -> str:
    """
    Return HTML for marker legend (trailing vs forward).

    Example:
        >>> st.markdown(render_marker_legend(), unsafe_allow_html=True)
    """
    return """
    <div style="display: flex; gap: 20px; padding: 10px 0; flex-wrap: wrap; font-size: 12px;">
        <span>● <b>Circle</b> = PE Trailing (TTM)</span>
        <span style="color: #F59E0B;">◆ <b>Diamond</b> = PE Forward (BSC 2025F)</span>
        <span>━ <b>Line</b> = Median (P50)</span>
    </div>
    """
