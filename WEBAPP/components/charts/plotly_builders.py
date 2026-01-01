"""
Reusable Plotly Chart Builders
================================

Standardized chart builders to replace PyEcharts and eliminate duplication.
Tất cả charts đều responsive và có styling nhất quán.

Author: AI Assistant
Date: 2025-12-12
Version: 2.0.0

Usage:
    from WEBAPP.components.charts import PlotlyChartBuilder as pcb

    fig = pcb.bar_line_combo(df, 'quarter', 'revenue', 'revenue_ma4', 'Revenue Trend')
    st.plotly_chart(fig, width='stretch')
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Optional, Dict, Tuple, Union
import logging

logger = logging.getLogger(__name__)


class PlotlyChartBuilder:
    """
    Centralized chart building với consistent styling.

    Design Principles:
    1. All charts responsive (width='stretch')
    2. Consistent color palette (Brand-aligned)
    3. Vietnamese labels support
    4. Auto-formatting (numbers, dates, percentages)
    5. Built-in error handling
    6. Accessibility patterns for colorblind users
    """

    # Color palette (Crypto Terminal - matching theme.py)
    COLORS = {
        'primary': '#8B5CF6',      # Electric Purple - MAIN
        'secondary': '#06B6D4',    # Cyan
        'accent': '#F59E0B',       # Amber Gold
        'positive': '#10B981',     # Emerald Green (bullish)
        'negative': '#EF4444',     # Red (bearish)
        'neutral': '#6B7280',      # Gray
        'danger': '#EF4444',       # Red (alias)
        'bullish': '#10B981',      # Trading green
        'bearish': '#EF4444',      # Trading red
        'chart': [
            '#8B5CF6',  # Electric Purple (Primary)
            '#06B6D4',  # Cyan
            '#F59E0B',  # Amber
            '#10B981',  # Emerald
            '#EC4899',  # Pink
            '#3B82F6',  # Blue
            '#A78BFA',  # Purple Light
            '#22D3EE',  # Cyan Light
        ]
    }

    # Pattern shapes for accessibility (colorblind users)
    PATTERNS = ['', '/', '\\', 'x', '-', '|', '+', '.']

    @staticmethod
    def get_pattern(index: int) -> str:
        """Get pattern shape for series index (accessibility)."""
        return PlotlyChartBuilder.PATTERNS[index % len(PlotlyChartBuilder.PATTERNS)]

    @staticmethod
    def line_chart(
        df: pd.DataFrame,
        x_col: str,
        y_cols: List[str],
        title: str,
        colors: Optional[List[str]] = None,
        height: int = 400,
        y_axis_title: str = "",
        show_legend: bool = True
    ) -> go.Figure:
        """
        Build responsive line chart with multiple series.

        Args:
            df: Source DataFrame
            x_col: Column for x-axis (usually 'date' or 'quarter')
            y_cols: List of columns for y-axis
            title: Chart title
            colors: Custom colors (optional)
            height: Chart height in pixels
            y_axis_title: Y-axis label
            show_legend: Show legend or not

        Returns:
            Plotly Figure object

        Example:
            >>> fig = PlotlyChartBuilder.line_chart(
            ...     df=revenue_df,
            ...     x_col='quarter',
            ...     y_cols=['net_revenue', 'gross_profit'],
            ...     title='Revenue Trend',
            ...     y_axis_title='VND (billions)'
            ... )
            >>> st.plotly_chart(fig, width='stretch')
        """
        try:
            if colors is None:
                colors = PlotlyChartBuilder.COLORS['chart']

            fig = go.Figure()

            for i, y_col in enumerate(y_cols):
                if y_col not in df.columns:
                    logger.warning(f"Column '{y_col}' not found in DataFrame")
                    continue

                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[y_col],
                    mode='lines+markers',
                    name=y_col,
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=6),
                    hovertemplate='%{x}<br>%{y:,.0f}<extra></extra>'
                ))

            fig.update_layout(
                title=dict(text=title, font=dict(family='Space Grotesk, sans-serif', size=16, color='#C4B5FD')),
                xaxis_title=x_col.title(),
                yaxis_title=y_axis_title,
                height=height,
                hovermode='x unified',
                showlegend=show_legend,
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='JetBrains Mono, monospace', color='#94A3B8'),
                xaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)'),
                yaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)'),
                hoverlabel=dict(bgcolor='#1A1625', bordercolor='#8B5CF6', font=dict(color='#F8FAFC'))
            )

            return fig

        except Exception as e:
            logger.error(f"Error building line chart: {e}")
            # Return empty figure with error message
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

    @staticmethod
    def bar_chart(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        color: Optional[str] = None,
        height: int = 400,
        show_values: bool = True
    ) -> go.Figure:
        """
        Build bar chart with value labels.

        Args:
            df: Source DataFrame
            x_col: Column for x-axis
            y_col: Column for y-axis (bar height)
            title: Chart title
            color: Bar color (optional)
            height: Chart height
            show_values: Show value labels on bars

        Returns:
            Plotly Figure object

        Example:
            >>> fig = PlotlyChartBuilder.bar_chart(
            ...     df=growth_df,
            ...     x_col='quarter',
            ...     y_col='revenue_growth_yoy',
            ...     title='Revenue Growth YoY',
            ...     color='#10B981'
            ... )
        """
        try:
            if color is None:
                color = PlotlyChartBuilder.COLORS['primary']

            fig = go.Figure(data=[
                go.Bar(
                    x=df[x_col],
                    y=df[y_col],
                    marker_color=color,
                    text=df[y_col] if show_values else None,
                    texttemplate='%{text:.1f}%' if show_values else None,
                    textposition='outside',
                    hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
                )
            ])

            fig.update_layout(
                title=dict(text=title, font=dict(family='Space Grotesk, sans-serif', size=16, color='#C4B5FD')),
                xaxis_title=x_col.title(),
                yaxis_title=y_col.title(),
                height=height,
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='JetBrains Mono, monospace', color='#94A3B8'),
                xaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)'),
                yaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)')
            )

            return fig

        except Exception as e:
            logger.error(f"Error building bar chart: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

    @staticmethod
    def bar_line_combo(
        df: pd.DataFrame,
        x_col: str,
        bar_col: str,
        line_col: str,
        title: str,
        bar_name: str = "Value",
        line_name: str = "MA4",
        bar_color: Optional[str] = None,
        line_color: Optional[str] = None,
        height: int = 400
    ) -> go.Figure:
        """
        Build bar + line combo chart (REPLACES PyEcharts overlap).

        This is the most common pattern - replaces 300+ LOC of duplicated
        PyEcharts code across company/bank/securities dashboards.

        Args:
            df: Source DataFrame
            x_col: Column for x-axis
            bar_col: Column for bars (e.g., 'revenue')
            line_col: Column for line (e.g., 'revenue_ma4')
            title: Chart title
            bar_name: Legend name for bars
            line_name: Legend name for line
            bar_color: Bar color (optional)
            line_color: Line color (optional)
            height: Chart height

        Returns:
            Plotly Figure with secondary y-axis

        Example:
            >>> # Replace PyEcharts bar.overlap(line) pattern
            >>> fig = PlotlyChartBuilder.bar_line_combo(
            ...     df=revenue_df,
            ...     x_col='quarter',
            ...     bar_col='net_revenue',
            ...     line_col='net_revenue_ma4',
            ...     title='Net Revenue with MA4',
            ...     bar_name='Revenue',
            ...     line_name='MA4 Trend'
            ... )
            >>> st.plotly_chart(fig, width='stretch')
        """
        try:
            if bar_color is None:
                bar_color = PlotlyChartBuilder.COLORS['primary']
            if line_color is None:
                line_color = PlotlyChartBuilder.COLORS['accent']

            # Create subplot with secondary y-axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # Add bar trace
            fig.add_trace(
                go.Bar(
                    x=df[x_col],
                    y=df[bar_col],
                    name=bar_name,
                    marker_color=bar_color,
                    hovertemplate='%{x}<br>%{y:,.0f}<extra></extra>'
                ),
                secondary_y=False
            )

            # Add line trace
            fig.add_trace(
                go.Scatter(
                    x=df[x_col],
                    y=df[line_col],
                    mode='lines+markers',
                    name=line_name,
                    line=dict(color=line_color, width=2),
                    marker=dict(size=6),
                    hovertemplate='%{x}<br>%{y:,.0f}<extra></extra>'
                ),
                secondary_y=True
            )

            # Update layout
            fig.update_layout(
                title=dict(text=title, font=dict(family='Space Grotesk, sans-serif', size=16, color='#C4B5FD')),
                xaxis_title=x_col.title(),
                height=height,
                hovermode='x unified',
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='JetBrains Mono, monospace', color='#94A3B8'),
                xaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)'),
                yaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)')
            )

            # Set y-axes titles
            fig.update_yaxes(title_text=bar_name, secondary_y=False, gridcolor='rgba(255, 255, 255, 0.05)')
            fig.update_yaxes(title_text=line_name, secondary_y=True, gridcolor='rgba(255, 255, 255, 0.05)')

            return fig

        except Exception as e:
            logger.error(f"Error building bar+line combo: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

    @staticmethod
    def candlestick_chart(
        df: pd.DataFrame,
        title: str,
        height: int = 400,
        show_rangeslider: bool = False
    ) -> go.Figure:
        """
        Build candlestick chart (for PE/PB valuation or price).

        Matches user's render_pe_pb_dotplot function from bank_dashboard.

        Args:
            df: DataFrame with columns: date, open, high, low, close
            title: Chart title
            height: Chart height
            show_rangeslider: Show date range slider below

        Returns:
            Plotly Figure with candlestick

        Example:
            >>> # PE ratio candlestick (matching user's requirement)
            >>> fig = PlotlyChartBuilder.candlestick_chart(
            ...     df=pe_df,  # Must have: date, open, high, low, close
            ...     title='PE Ratio Candlestick - ACB'
            ... )
            >>> st.plotly_chart(fig, width='stretch')
        """
        try:
            required_cols = ['date', 'open', 'high', 'low', 'close']
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            fig = go.Figure(data=[go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name=title
            )])

            fig.update_layout(
                title=dict(text=title, font=dict(family='Space Grotesk, sans-serif', size=16, color='#C4B5FD')),
                yaxis_title='Value',
                xaxis_title='Date',
                height=height,
                xaxis_rangeslider_visible=show_rangeslider,
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='JetBrains Mono, monospace', color='#94A3B8'),
                xaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)'),
                yaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)')
            )

            return fig

        except Exception as e:
            logger.error(f"Error building candlestick chart: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

    @staticmethod
    def heatmap(
        data: pd.DataFrame,
        title: str,
        x_label: str = "X",
        y_label: str = "Y",
        colorscale: str = 'RdYlGn',
        height: int = 500,
        show_values: bool = True
    ) -> go.Figure:
        """
        Build heatmap (for sector comparison, correlation matrices).

        Args:
            data: 2D DataFrame or numpy array
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            colorscale: Plotly color scale
                - 'RdYlGn': Red (low) to Green (high)
                - 'RdYlGn_r': Red (high) to Green (low) - reversed
                - 'Viridis': Purple to yellow
                - 'Blues': White to dark blue
            height: Chart height
            show_values: Show values in cells

        Returns:
            Plotly Figure with heatmap

        Example:
            >>> # Sector PE heatmap
            >>> fig = PlotlyChartBuilder.heatmap(
            ...     data=sector_pe_matrix,
            ...     title='Sector PE Ratio Heatmap',
            ...     x_label='Sectors',
            ...     y_label='Metrics',
            ...     colorscale='RdYlGn_r'
            ... )
        """
        try:
            fig = go.Figure(data=go.Heatmap(
                z=data.values,
                x=data.columns,
                y=data.index,
                colorscale=colorscale,
                text=data.values if show_values else None,
                texttemplate='%{text:.1f}' if show_values else None,
                colorbar=dict(title="Value")
            ))

            fig.update_layout(
                title=dict(text=title, font=dict(family='Space Grotesk, sans-serif', size=16, color='#C4B5FD')),
                xaxis_title=x_label,
                yaxis_title=y_label,
                height=height,
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='JetBrains Mono, monospace', color='#94A3B8')
            )

            return fig

        except Exception as e:
            logger.error(f"Error building heatmap: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

    @staticmethod
    def line_with_bands(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        mean_col: str,
        std_col: str,
        title: str,
        height: int = 400,
        num_std: int = 1
    ) -> go.Figure:
        """
        Build line chart with statistical bands (±nσ).

        Used for valuation percentile charts, volatility analysis.

        Args:
            df: Source DataFrame
            x_col: Column for x-axis (date)
            y_col: Column for main line (e.g., 'pe_ratio')
            mean_col: Column for mean/average
            std_col: Column for standard deviation
            title: Chart title
            height: Chart height
            num_std: Number of std deviations for bands

        Returns:
            Plotly Figure with bands

        Example:
            >>> # PE ratio with ±1σ bands
            >>> fig = PlotlyChartBuilder.line_with_bands(
            ...     df=pe_df,
            ...     x_col='date',
            ...     y_col='pe_ratio',
            ...     mean_col='pe_mean',
            ...     std_col='pe_std',
            ...     title='PE Ratio with Historical Bands'
            ... )
        """
        try:
            # Calculate band boundaries
            upper_band = df[mean_col] + (num_std * df[std_col])
            lower_band = df[mean_col] - (num_std * df[std_col])

            fig = go.Figure()

            # Add upper band
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=upper_band,
                mode='lines',
                name=f'+{num_std}σ',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))

            # Add lower band (fill area)
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=lower_band,
                mode='lines',
                name=f'-{num_std}σ',
                line=dict(width=0),
                fillcolor='rgba(30, 64, 175, 0.2)',  # Light blue
                fill='tonexty',
                showlegend=False,
                hoverinfo='skip'
            ))

            # Add mean line
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[mean_col],
                mode='lines',
                name='Mean',
                line=dict(color='gray', width=1, dash='dash')
            ))

            # Add actual value line
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='lines+markers',
                name=y_col.title(),
                line=dict(color=PlotlyChartBuilder.COLORS['primary'], width=2),
                marker=dict(size=4)
            ))

            fig.update_layout(
                title=dict(text=title, font=dict(family='Space Grotesk, sans-serif', size=16, color='#C4B5FD')),
                xaxis_title='Date',
                yaxis_title=y_col.title(),
                height=height,
                hovermode='x unified',
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='JetBrains Mono, monospace', color='#94A3B8'),
                xaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)'),
                yaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)')
            )

            return fig

        except Exception as e:
            logger.error(f"Error building line with bands: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

    @staticmethod
    def waterfall_chart(
        categories: List[str],
        values: List[float],
        title: str,
        height: int = 500
    ) -> go.Figure:
        """
        Build waterfall chart (for cash flow analysis).

        Args:
            categories: List of category names
            values: List of values (positive/negative)
            title: Chart title
            height: Chart height

        Returns:
            Plotly Figure with waterfall

        Example:
            >>> # Cash flow waterfall
            >>> fig = PlotlyChartBuilder.waterfall_chart(
            ...     categories=['Operating CF', 'Investing CF', 'Financing CF', 'Net Change'],
            ...     values=[1000, -500, -200, 300],
            ...     title='Cash Flow Waterfall'
            ... )
        """
        try:
            # Determine measure type for each category
            measure = ['relative'] * (len(categories) - 1) + ['total']

            fig = go.Figure(go.Waterfall(
                name='Cash Flow',
                orientation='v',
                measure=measure,
                x=categories,
                y=values,
                connector={'line': {'color': 'rgb(63, 63, 63)'}}
            ))

            fig.update_layout(
                title=dict(text=title, font=dict(family='Space Grotesk, sans-serif', size=16, color='#C4B5FD')),
                showlegend=True,
                height=height,
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='JetBrains Mono, monospace', color='#94A3B8'),
                xaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)'),
                yaxis=dict(gridcolor='rgba(255, 255, 255, 0.05)')
            )

            return fig

        except Exception as e:
            logger.error(f"Error building waterfall chart: {e}")
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig


# Convenience functions for common charts
def revenue_trend_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """Pre-configured revenue trend chart."""
    return PlotlyChartBuilder.bar_line_combo(
        df=df,
        x_col='quarter',
        bar_col='net_revenue',
        line_col='net_revenue_ma4',
        title=f'Net Revenue Trend - {symbol}',
        bar_name='Revenue',
        line_name='MA4'
    )


def profitability_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """Pre-configured profitability margins chart."""
    return PlotlyChartBuilder.line_chart(
        df=df,
        x_col='quarter',
        y_cols=['gross_margin', 'ebit_margin', 'ebitda_margin', 'net_margin'],
        title=f'Profitability Margins - {symbol}',
        y_axis_title='Margin (%)'
    )


def pe_candlestick_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """Pre-configured PE candlestick chart."""
    return PlotlyChartBuilder.candlestick_chart(
        df=df,
        title=f'PE Ratio Candlestick - {symbol}'
    )


def valuation_box_with_markers(
    stats_data: list,
    pe_forward_data: dict = None,
    title: str = "PE Distribution: Trailing vs Forward",
    metric_label: str = "PE",
    height: int = 500,
    show_legend: bool = True
) -> go.Figure:
    """
    Build valuation box chart with trailing (circle) and forward (diamond) markers.

    Visual representation (candlestick-style):
        - Body (thick bar): P25-P75 (IQR) range
        - Whiskers (thin line): P5-P95 range
        - Circle (●): PE Trailing (current value)
        - Diamond (◆): PE Forward (BSC forecast)

    Args:
        stats_data: List of dicts from ValuationService.get_industry_candle_data()
                   Each dict: {symbol, current, p25, median, p75, p5, p95, percentile, status}
        pe_forward_data: Dict mapping symbol -> pe_forward value (e.g., from BSC forecast)
                        Example: {'ACB': 8.5, 'VCB': 12.3, ...}
        title: Chart title
        metric_label: Label for metric (PE, PB, etc.)
        height: Chart height in pixels
        show_legend: Show legend

    Returns:
        Plotly Figure with box + markers

    Example:
        >>> from WEBAPP.services.valuation_service import ValuationService
        >>> from WEBAPP.services.forecast_service import ForecastService
        >>>
        >>> val_svc = ValuationService()
        >>> forecast_svc = ForecastService()
        >>>
        >>> # Get historical distribution stats
        >>> stats = val_svc.get_industry_candle_data('Ngân hàng', metric='PE')
        >>>
        >>> # Get forward PE from BSC
        >>> bsc_df = forecast_svc.get_individual_stocks()
        >>> pe_fwd = dict(zip(bsc_df['symbol'], bsc_df['pe_fwd_2025']))
        >>>
        >>> fig = valuation_box_with_markers(stats, pe_fwd, title='Bank PE: TTM vs 2025F')
        >>> st.plotly_chart(fig, width='stretch')
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

    # Sort by current PE (trailing)
    stats_data = sorted(stats_data, key=lambda x: x.get('current', 0))

    # Extract data for plotting
    symbols = [d['symbol'] for d in stats_data]
    p25_vals = [d.get('p25', 0) for d in stats_data]
    p75_vals = [d.get('p75', 0) for d in stats_data]
    p5_vals = [d.get('p5', d.get('min', 0)) for d in stats_data]
    p95_vals = [d.get('p95', d.get('max', 0)) for d in stats_data]
    median_vals = [d.get('median', 0) for d in stats_data]
    current_vals = [d.get('current', 0) for d in stats_data]
    statuses = [d.get('status', 'Fair') for d in stats_data]

    # Get forward PE values (only for symbols that have forecast)
    forward_vals = [pe_forward_data.get(s) for s in symbols]

    # Color mapping for status
    status_colors = {
        'Very Cheap': '#00D4AA',
        'Cheap': '#7FFFD4',
        'Fair': '#FFD666',
        'Expensive': '#FF9F43',
        'Very Expensive': '#FF6B6B'
    }

    fig = go.Figure()

    # Use candlestick-style rendering for box plots
    # Candlestick: open=P25, close=P75, low=P5, high=P95
    # Color based on status (not price direction)

    # Create candlestick data for distribution boxes
    candle_data = []
    for i, symbol in enumerate(symbols):
        candle_data.append({
            'x': symbol,
            'open': p25_vals[i],
            'high': p95_vals[i],
            'low': p5_vals[i],
            'close': p75_vals[i],
            'color': status_colors.get(statuses[i], '#6B7280')
        })

    # Add candlestick trace for distribution boxes
    # Use scatter with error bars to simulate candlestick
    # Whiskers (P5-P95)
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

    # Box body (P25-P75) - use bar chart
    box_colors = [status_colors.get(s, '#6B7280') for s in statuses]
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
        hovertemplate='<b>%{x}</b><br>' +
                      'P25: %{base:.1f}x<br>' +
                      'P75: %{customdata:.1f}x<br>' +
                      '<extra></extra>',
        customdata=p75_vals
    ))

    # Median line within box
    fig.add_trace(go.Scatter(
        x=symbols,
        y=median_vals,
        mode='markers',
        marker=dict(
            symbol='line-ew',
            size=12,
            line=dict(width=2, color='white')
        ),
        showlegend=False,
        hoverinfo='skip'
    ))

    # Add trailing PE markers (circle)
    trailing_colors = [status_colors.get(s, '#6B7280') for s in statuses]
    fig.add_trace(go.Scatter(
        x=symbols,
        y=current_vals,
        mode='markers',
        name=f'{metric_label} Trailing (TTM)',
        marker=dict(
            symbol='circle',
            size=14,
            color=trailing_colors,
            line=dict(color='white', width=2)
        ),
        hovertemplate='<b>%{x}</b><br>' +
                      f'{metric_label} TTM: ' + '%{y:.1f}x<br>' +
                      '<extra></extra>'
    ))

    # Add forward PE markers (diamond) - only for stocks with forecast
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
            name=f'{metric_label} Forward (2025F)',
            marker=dict(
                symbol='diamond',
                size=12,
                color='#F59E0B',  # Amber for forward
                line=dict(color='white', width=1.5)
            ),
            hovertemplate='<b>%{x}</b><br>' +
                          f'{metric_label} 2025F: ' + '%{customdata}<br>' +
                          '<extra></extra>',
            customdata=forward_hover
        ))

    # Add median reference line
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
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family='Space Grotesk, sans-serif', size=16, color='#C4B5FD')
        ),
        xaxis_title='Symbol',
        yaxis_title=f'{metric_label} Ratio',
        height=height,
        showlegend=show_legend,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=10)
        ),
        barmode='overlay',
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono, monospace', color='#94A3B8'),
        xaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.05)',
            tickangle=-45,
            tickfont=dict(size=9)
        ),
        yaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.05)',
            zeroline=False
        ),
        hoverlabel=dict(
            bgcolor='#1A1625',
            bordercolor='#8B5CF6',
            font=dict(color='#F8FAFC')
        )
    )

    return fig
