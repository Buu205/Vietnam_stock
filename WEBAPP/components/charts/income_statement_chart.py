"""
Income Statement Chart Component - Quick Prototype
==================================================

Multi-line chart showing income statement trends over time.

Usage:
    from WEBAPP.components.charts.income_statement_chart import render_income_statement_chart

    render_income_statement_chart(df)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def render_income_statement_chart(df: pd.DataFrame, height: int = 450):
    """
    Render income statement trends chart (Revenue → Net Profit).

    Args:
        df: DataFrame with columns: report_date, net_revenue, gross_profit,
            ebit, ebitda, npatmi
        height: Chart height in pixels

    Expected columns:
        - report_date: Date column
        - net_revenue: Net revenue/sales
        - gross_profit: Gross profit
        - ebit: EBIT (Earnings Before Interest & Tax)
        - ebitda: EBITDA (EBIT + D&A)
        - npatmi: Net profit after tax & minority interest
    """
    if df.empty:
        st.warning("No data available for chart")
        return

    # Create figure
    fig = go.Figure()

    # Define metrics to plot
    metrics = {
        'Net Revenue': {'column': 'net_revenue', 'color': '#059669'},  # Dark green
        'Gross Profit': {'column': 'gross_profit', 'color': '#10B981'},  # Green
        'EBIT': {'column': 'ebit', 'color': '#3B82F6'},  # Blue
        'EBITDA': {'column': 'ebitda', 'color': '#60A5FA'},  # Light blue
        'Net Profit': {'column': 'npatmi', 'color': '#F59E0B'},  # Amber
    }

    # Add traces for each metric
    for name, config in metrics.items():
        col = config['column']
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['report_date'],
                y=df[col],
                name=name,
                mode='lines+markers',
                line=dict(color=config['color'], width=2),
                marker=dict(size=6),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                              'Date: %{x|%Y-Q%q}<br>' +
                              'Value: %{y:,.1f}B VND<br>' +
                              '<extra></extra>'
            ))

    # Update layout
    fig.update_layout(
        title={
            'text': 'Income Statement Trends',
            'font': {'size': 18, 'family': 'Inter'},
            'x': 0
        },
        xaxis_title='Period',
        yaxis_title='VND Billions',
        hovermode='x unified',
        height=height,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    # Style axes
    fig.update_xaxes(
        showgrid=True,
        gridcolor='rgba(128,128,128,0.1)',
        showline=True,
        linecolor='rgba(128,128,128,0.3)'
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(128,128,128,0.1)',
        showline=True,
        linecolor='rgba(128,128,128,0.3)',
        tickformat=',.0f'
    )

    # Render
    st.plotly_chart(fig, use_container_width=True)


def render_margins_chart(df: pd.DataFrame, height: int = 400):
    """
    Render profitability margins chart (area chart).

    Args:
        df: DataFrame with margin columns
        height: Chart height in pixels

    Expected columns:
        - report_date
        - gross_profit_margin
        - ebit_margin
        - ebitda_margin
        - net_margin
    """
    if df.empty:
        st.warning("No data available for margins chart")
        return

    fig = go.Figure()

    margins = {
        'Gross Margin': {'column': 'gross_profit_margin', 'color': '#10B981'},
        'EBIT Margin': {'column': 'ebit_margin', 'color': '#3B82F6'},
        'EBITDA Margin': {'column': 'ebitda_margin', 'color': '#60A5FA'},
        'Net Margin': {'column': 'net_margin', 'color': '#F59E0B'}
    }

    for name, config in margins.items():
        col = config['column']
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['report_date'],
                y=df[col],
                name=name,
                mode='lines+markers',
                fill='tonexty' if name != 'Gross Margin' else None,
                line=dict(color=config['color'], width=2),
                marker=dict(size=6),
                hovertemplate='<b>%{fullData.name}</b><br>' +
                              'Date: %{x|%Y-Q%q}<br>' +
                              'Margin: %{y:.2f}%<br>' +
                              '<extra></extra>'
            ))

    fig.update_layout(
        title={
            'text': 'Profitability Margins',
            'font': {'size': 18, 'family': 'Inter'},
            'x': 0
        },
        xaxis_title='Period',
        yaxis_title='Margin (%)',
        hovermode='x unified',
        height=height,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    fig.update_xaxes(showgrid=True, gridcolor='rgba(128,128,128,0.1)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(128,128,128,0.1)', tickformat='.2f')

    st.plotly_chart(fig, use_container_width=True)


def render_roe_roa_chart(df: pd.DataFrame, height: int = 400):
    """
    Render ROE/ROA dual-axis trend chart with brand colors.

    Professional financial aesthetic with:
    - Dual Y-axes for different scales
    - Bold brand colors (#295CA9 blue, #009B87 teal)
    - Gradient fill under ROE line for emphasis
    - Large markers on latest data points
    - Smooth transitions and refined typography

    Args:
        df: DataFrame with columns: report_date, roe, roa
        height: Chart height in pixels

    Expected columns:
        - report_date: Date column
        - roe: Return on Equity (%)
        - roa: Return on Assets (%)
    """
    if df.empty:
        st.warning("No data available for ROE/ROA chart")
        return

    # Verify required columns
    required_cols = ['report_date', 'roe', 'roa']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Missing required columns. Need: {required_cols}")
        return

    # Brand colors from theme
    BRAND_BLUE = '#295CA9'    # Primary - for ROE (more important metric)
    BRAND_TEAL = '#009B87'    # Accent - for ROA

    # Create figure with secondary y-axis
    fig = go.Figure()

    # ROE trace (primary y-axis) - Bold line with gradient fill
    fig.add_trace(go.Scatter(
        x=df['report_date'],
        y=df['roe'],
        name='ROE',
        mode='lines+markers',
        line=dict(
            color=BRAND_BLUE,
            width=3,
            shape='spline',  # Smooth curves
        ),
        marker=dict(
            size=8,
            color=BRAND_BLUE,
            line=dict(color='white', width=2),  # White border for depth
        ),
        fill='tozeroy',  # Fill to baseline
        fillcolor=f'rgba(41, 92, 169, 0.15)',  # Subtle blue gradient
        yaxis='y',
        hovertemplate='<b style="color: {color}">ROE</b><br>'.format(color=BRAND_BLUE) +
                      'Period: %{x|%Y-Q%q}<br>' +
                      'Value: <b>%{y:.2f}%</b><br>' +
                      '<extra></extra>'
    ))

    # ROA trace (secondary y-axis) - Complementary line
    fig.add_trace(go.Scatter(
        x=df['report_date'],
        y=df['roa'],
        name='ROA',
        mode='lines+markers',
        line=dict(
            color=BRAND_TEAL,
            width=2.5,
            shape='spline',
            dash='dot',  # Dotted to distinguish from ROE
        ),
        marker=dict(
            size=7,
            color=BRAND_TEAL,
            symbol='diamond',  # Different shape for distinction
            line=dict(color='white', width=1.5),
        ),
        yaxis='y2',
        hovertemplate='<b style="color: {color}">ROA</b><br>'.format(color=BRAND_TEAL) +
                      'Period: %{x|%Y-Q%q}<br>' +
                      'Value: <b>%{y:.2f}%</b><br>' +
                      '<extra></extra>'
    ))

    # Highlight latest data point with larger markers
    if len(df) > 0:
        latest_date = df.iloc[-1]['report_date']
        latest_roe = df.iloc[-1]['roe']
        latest_roa = df.iloc[-1]['roa']

        # Large marker for latest ROE
        fig.add_trace(go.Scatter(
            x=[latest_date],
            y=[latest_roe],
            mode='markers',
            marker=dict(
                size=14,
                color=BRAND_BLUE,
                line=dict(color='white', width=3),
            ),
            yaxis='y',
            showlegend=False,
            hoverinfo='skip'
        ))

        # Large marker for latest ROA
        fig.add_trace(go.Scatter(
            x=[latest_date],
            y=[latest_roa],
            mode='markers',
            marker=dict(
                size=12,
                color=BRAND_TEAL,
                symbol='diamond',
                line=dict(color='white', width=3),
            ),
            yaxis='y2',
            showlegend=False,
            hoverinfo='skip'
        ))

    # Layout with professional financial styling
    fig.update_layout(
        title={
            'text': '<b>Return Metrics Trend</b><br><sup style="font-size: 12px; color: #9CA3AF;">ROE vs ROA Performance Analysis</sup>',
            'font': {'size': 20, 'family': 'Inter, sans-serif', 'color': '#FFFFFF'},
            'x': 0,
            'xanchor': 'left'
        },

        # Dual Y-axes configuration
        yaxis=dict(
            title=dict(
                text='<b>ROE (%)</b>',
                font=dict(size=13, color=BRAND_BLUE, family='Inter')
            ),
            tickformat='.2f',
            tickfont=dict(color=BRAND_BLUE, size=11),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.08)',
            zeroline=True,
            zerolinecolor='rgba(255, 255, 255, 0.2)',
            zerolinewidth=1,
        ),
        yaxis2=dict(
            title=dict(
                text='<b>ROA (%)</b>',
                font=dict(size=13, color=BRAND_TEAL, family='Inter')
            ),
            tickformat='.2f',
            tickfont=dict(color=BRAND_TEAL, size=11),
            overlaying='y',
            side='right',
            showgrid=False,  # Avoid grid conflict
        ),

        xaxis=dict(
            title=dict(
                text='<b>Period</b>',
                font=dict(size=13, color='#E3EBF7', family='Inter')
            ),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.05)',
            showline=True,
            linecolor='rgba(255, 255, 255, 0.2)',
            tickfont=dict(size=11, color='#E3EBF7'),
        ),

        # Dark professional background
        plot_bgcolor='#0A1E42',      # Deep navy
        paper_bgcolor='#0A1E42',

        height=height,
        hovermode='x unified',

        # Legend configuration
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.15,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.05)',
            bordercolor='rgba(255, 255, 255, 0.1)',
            borderwidth=1,
            font=dict(size=12, color='#FFFFFF', family='Inter')
        ),

        font=dict(family='Inter, sans-serif', size=12, color='#E3EBF7'),
        margin=dict(l=60, r=60, t=80, b=80)
    )

    # Render with animation
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d']
        }
    )


def render_balance_sheet_chart(df: pd.DataFrame, height: int = 400):
    """
    Render Balance Sheet structure chart (Assets vs Liabilities + Equity).

    Args:
        df: DataFrame with columns: report_date, total_assets, total_liabilities, total_equity
        height: Chart height in pixels
    """
    if df.empty:
        st.warning("No data available for Balance Sheet chart")
        return

    required_cols = ['report_date', 'total_assets', 'total_liabilities', 'total_equity']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Missing required columns. Need: {required_cols}")
        return

    BRAND_BLUE = '#295CA9'
    BRAND_GOLD = '#FFC132'
    LIGHT_BLUE = '#4A7BC8'

    fig = go.Figure()

    df_chart = df.copy()
    # Format: 1Q24, 2Q24, 3Q24
    dates = pd.to_datetime(df_chart['report_date'])
    df_chart['period_label'] = dates.dt.quarter.astype(str) + 'Q' + dates.dt.year.astype(str).str[-2:]

    fig.add_trace(go.Bar(
        name='Total Assets',
        x=df_chart['period_label'],
        y=df_chart['total_assets'],
        marker_color=BRAND_BLUE,
        hovertemplate='<b>Total Assets</b><br>Period: %{x}<br>Value: %{y:,.1f}B VND<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        name='Total Liabilities',
        x=df_chart['period_label'],
        y=df_chart['total_liabilities'],
        marker_color=BRAND_GOLD,
        hovertemplate='<b>Total Liabilities</b><br>Period: %{x}<br>Value: %{y:,.1f}B VND<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        name='Total Equity',
        x=df_chart['period_label'],
        y=df_chart['total_equity'],
        marker_color=LIGHT_BLUE,
        hovertemplate='<b>Total Equity</b><br>Period: %{x}<br>Value: %{y:,.1f}B VND<extra></extra>'
    ))

    fig.update_layout(
        title={'text': 'Balance Sheet Structure', 'font': {'size': 18, 'family': 'Inter'}, 'x': 0},
        barmode='group',
        xaxis_title='Period',
        yaxis_title='VND Billions',
        height=height,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
        margin=dict(l=50, r=50, t=80, b=50),
        hovermode='x unified'
    )

    fig.update_xaxes(showgrid=True, gridcolor='rgba(128,128,128,0.1)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(128,128,128,0.1)', tickformat=',.0f')

    st.plotly_chart(fig, use_container_width=True)


def render_cash_flow_chart(df: pd.DataFrame, height: int = 400):
    """
    Render Cash Flow analysis chart with Operating, Investment, Financing CFs.

    Args:
        df: DataFrame with cash flow columns
        height: Chart height in pixels
    """
    if df.empty:
        st.warning("No data available for Cash Flow chart")
        return

    required_cols = ['report_date', 'operating_cf', 'investment_cf', 'financing_cf']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Missing required columns. Need: {required_cols}")
        return

    BRAND_TEAL = '#009B87'
    BRAND_GOLD = '#FFC132'
    NEGATIVE_RED = '#E63946'
    BRAND_BLUE = '#295CA9'

    fig = go.Figure()

    df_chart = df.copy()
    # Format: 1Q24, 2Q24, 3Q24
    dates = pd.to_datetime(df_chart['report_date'])
    df_chart['period_label'] = dates.dt.quarter.astype(str) + 'Q' + dates.dt.year.astype(str).str[-2:]

    fig.add_trace(go.Bar(
        name='Operating CF',
        x=df_chart['period_label'],
        y=df_chart['operating_cf'],
        marker_color=[BRAND_TEAL if v >= 0 else NEGATIVE_RED for v in df_chart['operating_cf']],
        hovertemplate='<b>Operating CF</b><br>Period: %{x}<br>Value: %{y:,.1f}B VND<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        name='Investment CF',
        x=df_chart['period_label'],
        y=df_chart['investment_cf'],
        marker_color=[BRAND_TEAL if v >= 0 else NEGATIVE_RED for v in df_chart['investment_cf']],
        hovertemplate='<b>Investment CF</b><br>Period: %{x}<br>Value: %{y:,.1f}B VND<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        name='Financing CF',
        x=df_chart['period_label'],
        y=df_chart['financing_cf'],
        marker_color=[BRAND_GOLD if v >= 0 else NEGATIVE_RED for v in df_chart['financing_cf']],
        hovertemplate='<b>Financing CF</b><br>Period: %{x}<br>Value: %{y:,.1f}B VND<extra></extra>'
    ))

    if 'fcf' in df_chart.columns:
        fig.add_trace(go.Scatter(
            name='Free Cash Flow',
            x=df_chart['period_label'],
            y=df_chart['fcf'],
            mode='lines+markers',
            line=dict(color=BRAND_BLUE, width=3),
            marker=dict(size=8, color=BRAND_BLUE),
            hovertemplate='<b>FCF</b><br>Period: %{x}<br>Value: %{y:,.1f}B VND<extra></extra>'
        ))

    fig.update_layout(
        title={'text': 'Cash Flow Analysis', 'font': {'size': 18, 'family': 'Inter'}, 'x': 0},
        barmode='group',
        xaxis_title='Period',
        yaxis_title='VND Billions',
        height=height,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
        margin=dict(l=50, r=50, t=80, b=50),
        hovermode='x unified'
    )

    fig.add_hline(y=0, line_dash="dash", line_color="rgba(128,128,128,0.5)")
    fig.update_xaxes(showgrid=True, gridcolor='rgba(128,128,128,0.1)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(128,128,128,0.1)', tickformat=',.0f')

    st.plotly_chart(fig, use_container_width=True)


def render_peer_comparison_chart(
    peers_data: pd.DataFrame,
    metric: str = 'roe',
    metric_label: str = 'ROE (%)',
    height: int = 400
):
    """
    Render horizontal bar chart comparing a company with its sector peers.

    Args:
        peers_data: DataFrame with columns: symbol, {metric}, is_target (optional)
        metric: Column name of the metric to compare
        metric_label: Display label for the metric
        height: Chart height in pixels
    """
    if peers_data.empty:
        st.warning("No peer data available for comparison")
        return

    if metric not in peers_data.columns:
        st.error(f"Metric '{metric}' not found in data")
        return

    BRAND_BLUE = '#295CA9'
    BRAND_TEAL = '#009B87'

    df_sorted = peers_data.sort_values(metric, ascending=True).copy()

    if 'is_target' in df_sorted.columns:
        colors = [BRAND_BLUE if row['is_target'] else BRAND_TEAL for _, row in df_sorted.iterrows()]
    else:
        colors = [BRAND_TEAL] * len(df_sorted)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df_sorted['symbol'],
        x=df_sorted[metric],
        orientation='h',
        marker_color=colors,
        text=df_sorted[metric].apply(lambda x: f'{x:.2f}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>' + f'{metric_label}: ' + '%{x:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title={'text': f'Peer Comparison: {metric_label}', 'font': {'size': 18, 'family': 'Inter'}, 'x': 0},
        xaxis_title=metric_label,
        yaxis_title='',
        height=height,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
        margin=dict(l=80, r=80, t=60, b=50),
        showlegend=False
    )

    fig.update_xaxes(showgrid=True, gridcolor='rgba(128,128,128,0.1)')
    fig.update_yaxes(showgrid=False)

    st.plotly_chart(fig, use_container_width=True)
