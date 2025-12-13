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
    st.plotly_chart(fig, use_container_width=True)
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
    1. All charts responsive (use_container_width=True)
    2. Consistent color palette
    3. Vietnamese labels support
    4. Auto-formatting (numbers, dates, percentages)
    5. Built-in error handling
    """

    # Color palette (matching design system)
    COLORS = {
        'primary': '#1E40AF',      # Deep blue
        'secondary': '#10B981',    # Green
        'accent': '#F59E0B',       # Amber
        'danger': '#EF4444',       # Red
        'chart': [
            '#1E40AF', '#10B981', '#F59E0B', '#EF4444',
            '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'
        ]
    }

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
            >>> st.plotly_chart(fig, use_container_width=True)
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
                title=title,
                xaxis_title=x_col.title(),
                yaxis_title=y_axis_title,
                height=height,
                hovermode='x unified',
                showlegend=show_legend,
                template='plotly_white'
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
                title=title,
                xaxis_title=x_col.title(),
                yaxis_title=y_col.title(),
                height=height,
                template='plotly_white'
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
            >>> st.plotly_chart(fig, use_container_width=True)
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
                title=title,
                xaxis_title=x_col.title(),
                height=height,
                hovermode='x unified',
                template='plotly_white'
            )

            # Set y-axes titles
            fig.update_yaxes(title_text=bar_name, secondary_y=False)
            fig.update_yaxes(title_text=line_name, secondary_y=True)

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
            >>> st.plotly_chart(fig, use_container_width=True)
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
                title=title,
                yaxis_title='Value',
                xaxis_title='Date',
                height=height,
                xaxis_rangeslider_visible=show_rangeslider,
                template='plotly_white'
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
                title=title,
                xaxis_title=x_label,
                yaxis_title=y_label,
                height=height,
                template='plotly_white'
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
                title=title,
                xaxis_title='Date',
                yaxis_title=y_col.title(),
                height=height,
                hovermode='x unified',
                template='plotly_white'
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
                title=title,
                showlegend=True,
                height=height,
                template='plotly_white'
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
