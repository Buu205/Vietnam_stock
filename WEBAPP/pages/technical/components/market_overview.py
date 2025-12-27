"""
Market Overview Component - Tab 1
=================================

Premium market overview with glassmorphism design.
Displays market regime, breadth, exposure and divergence alerts.

Design: Crypto Terminal with trading-focused colors
- Green (#10B981) for bullish/positive
- Red (#EF4444) for bearish/negative
- Purple (#8B5CF6) for primary accents
- Cyan (#06B6D4) for secondary accents

Author: Claude Code
Date: 2025-12-25
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import TYPE_CHECKING

from WEBAPP.core.styles import get_chart_layout, CHART_COLORS, TRADING_CHART_COLORS

if TYPE_CHECKING:
    from ..services.ta_dashboard_service import TADashboardService


# ============================================================================
# DESIGN CONSTANTS
# ============================================================================

REGIME_STYLES = {
    'BULLISH': {'color': '#10B981', 'bg': 'rgba(16, 185, 129, 0.15)', 'border': '#10B981'},
    'BEARISH': {'color': '#EF4444', 'bg': 'rgba(239, 68, 68, 0.15)', 'border': '#EF4444'},
    'NEUTRAL': {'color': '#F59E0B', 'bg': 'rgba(245, 158, 11, 0.15)', 'border': '#F59E0B'},
}

SIGNAL_STYLES = {
    'RISK_ON': {'color': '#10B981', 'bg': 'rgba(16, 185, 129, 0.15)'},
    'RISK_OFF': {'color': '#EF4444', 'bg': 'rgba(239, 68, 68, 0.15)'},
    'CAUTION': {'color': '#F59E0B', 'bg': 'rgba(245, 158, 11, 0.15)'},
}

BREADTH_COLORS = {
    'ma20': '#8B5CF6',  # Purple (short-term)
    'ma50': '#06B6D4',  # Cyan (medium-term)
    'ma100': '#F59E0B', # Amber (long-term)
}


def render_market_overview(service: 'TADashboardService') -> None:
    """
    Render Market Overview tab with premium styling.

    Components:
    - Compact metrics bar (VN-Index, Regime, Signal, Exposure)
    - Breadth line chart (MA20/50/100 with zones)
    - Breadth gauges + Divergence alert
    """
    state = service.get_market_state()

    # ============ COMPACT METRICS BAR ============
    _render_market_metrics_bar(state)

    st.markdown("---")

    # ============ BREADTH LINE CHART ============
    timeframe_options = {"3M": 63, "6M": 126, "9M": 189, "1Y": 252}

    # Initialize session state
    if "breadth_tf" not in st.session_state:
        st.session_state.breadth_tf = "6M"

    col_title, col_tf = st.columns([3, 1])
    with col_title:
        st.markdown("### Market Breadth")
    with col_tf:
        selected_tf = st.selectbox(
            "Timeframe",
            options=list(timeframe_options.keys()),
            index=list(timeframe_options.keys()).index(st.session_state.breadth_tf),
            key="breadth_timeframe_select",
            label_visibility="collapsed"
        )
        st.session_state.breadth_tf = selected_tf

    days = timeframe_options[selected_tf]
    history = service.get_breadth_history(days=days)
    _render_breadth_chart(history)

    # ============ BOTTOM ROW: GAUGES + DIVERGENCE ============
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Breadth Gauges")
        _render_breadth_gauges(state)

    with col2:
        st.markdown("### Divergence Alert")
        _render_divergence_alert(state)


def _render_market_metrics_bar(state) -> None:
    """Render compact inline metrics bar with HTML styling."""

    # Get style for regime
    regime_style = REGIME_STYLES.get(state.regime, REGIME_STYLES['NEUTRAL'])
    signal_style = SIGNAL_STYLES.get(state.signal, SIGNAL_STYLES['CAUTION'])

    # VN-Index change color
    change_color = '#10B981' if state.vnindex_change_pct >= 0 else '#EF4444'
    change_sign = '+' if state.vnindex_change_pct >= 0 else ''

    # Exposure color (gradient from red to green)
    if state.exposure_level >= 80:
        exp_color = '#10B981'
    elif state.exposure_level >= 60:
        exp_color = '#22C55E'
    elif state.exposure_level >= 40:
        exp_color = '#F59E0B'
    elif state.exposure_level >= 20:
        exp_color = '#FF9F43'
    else:
        exp_color = '#EF4444'

    st.markdown(f'''
    <div style="display: flex; gap: 16px; padding: 12px 0; flex-wrap: wrap; align-items: stretch;">
        <div style="flex: 1; min-width: 140px; background: rgba(139, 92, 246, 0.1); padding: 12px 16px; border-radius: 10px; border-left: 3px solid #8B5CF6;">
            <div style="color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">VN-Index</div>
            <div style="display: flex; align-items: baseline; gap: 8px; margin-top: 4px;">
                <span style="color: #F8FAFC; font-size: 1.4rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">{state.vnindex_close:,.0f}</span>
                <span style="color: {change_color}; font-size: 0.9rem; font-weight: 600;">{change_sign}{state.vnindex_change_pct:.2f}%</span>
            </div>
        </div>
        <div style="flex: 1; min-width: 120px; background: {regime_style['bg']}; padding: 12px 16px; border-radius: 10px; border-left: 3px solid {regime_style['border']};">
            <div style="color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Regime</div>
            <div style="color: {regime_style['color']}; font-size: 1.1rem; font-weight: 700; margin-top: 4px;">
                <span style="display: inline-block; width: 8px; height: 8px; background: {regime_style['color']}; border-radius: 50%; margin-right: 6px;"></span>
                {state.regime}
            </div>
        </div>
        <div style="flex: 1; min-width: 120px; background: {signal_style['bg']}; padding: 12px 16px; border-radius: 10px; border-left: 3px solid {signal_style['color']};">
            <div style="color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Signal</div>
            <div style="color: {signal_style['color']}; font-size: 1.1rem; font-weight: 700; margin-top: 4px;">
                <span style="display: inline-block; width: 8px; height: 8px; background: {signal_style['color']}; border-radius: 50%; margin-right: 6px;"></span>
                {state.signal.replace('_', ' ')}
            </div>
        </div>
        <div style="flex: 1.5; min-width: 180px; background: rgba(0, 0, 0, 0.3); padding: 12px 16px; border-radius: 10px; border-left: 3px solid {exp_color};">
            <div style="color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Capital Allocation</div>
            <div style="margin-top: 8px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="color: #E2E8F0; font-size: 0.8rem;">Recommended</span>
                    <span style="color: {exp_color}; font-size: 1rem; font-weight: 700;">{state.exposure_level}%</span>
                </div>
                <div style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;">
                    <div style="width: {state.exposure_level}%; height: 100%; background: linear-gradient(90deg, {exp_color}, {exp_color}aa); border-radius: 3px; transition: width 0.3s ease;"></div>
                </div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


def _render_breadth_chart(history) -> None:
    """Create multi-MA breadth line chart with VN-Index overlay."""

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.3, 0.7],
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}]]
    )

    # Row 1: VN-Index
    fig.add_trace(
        go.Scatter(
            x=history.date,
            y=history.vnindex_close,
            name='VN-Index',
            line=dict(color='#8B5CF6', width=2),
            fill='tozeroy',
            fillcolor='rgba(139, 92, 246, 0.1)',
            hovertemplate='<b>VN-Index</b>: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )

    # Row 2: Breadth Lines
    # MA20 - Purple (fastest)
    fig.add_trace(
        go.Scatter(
            x=history.date,
            y=history.ma20_pct,
            name='% > MA20',
            line=dict(color=BREADTH_COLORS['ma20'], width=2.5),
            hovertemplate='<b>MA20</b>: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )

    # MA50 - Cyan (medium)
    fig.add_trace(
        go.Scatter(
            x=history.date,
            y=history.ma50_pct,
            name='% > MA50',
            line=dict(color=BREADTH_COLORS['ma50'], width=2),
            hovertemplate='<b>MA50</b>: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )

    # MA100 - Amber (slowest)
    fig.add_trace(
        go.Scatter(
            x=history.date,
            y=history.ma100_pct,
            name='% > MA100',
            line=dict(color=BREADTH_COLORS['ma100'], width=2),
            hovertemplate='<b>MA100</b>: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )

    # Overbought zone (80-100%)
    fig.add_hrect(
        y0=80, y1=100,
        fillcolor="rgba(239, 68, 68, 0.08)",
        line_width=0,
        row=2, col=1
    )

    # Oversold zone (0-20%)
    fig.add_hrect(
        y0=0, y1=20,
        fillcolor="rgba(16, 185, 129, 0.08)",
        line_width=0,
        row=2, col=1
    )

    # Threshold lines
    fig.add_hline(y=80, line=dict(color='#EF4444', width=1, dash='dash'),
                  annotation_text="Overbought", annotation_position="right",
                  row=2, col=1)
    fig.add_hline(y=20, line=dict(color='#10B981', width=1, dash='dash'),
                  annotation_text="Oversold", annotation_position="right",
                  row=2, col=1)
    fig.add_hline(y=50, line=dict(color='#64748B', width=1, dash='dot'),
                  row=2, col=1)

    # Layout from theme
    layout = get_chart_layout(height=420)
    layout['showlegend'] = True
    layout['legend'] = dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5,
        font=dict(size=11, color='#E2E8F0')
    )
    layout['hovermode'] = 'x unified'

    # Time axis format
    layout['xaxis2'] = dict(
        tickformat='%d/%m',
        tickmode='auto',
        nticks=10,
        tickangle=-30,
        tickfont=dict(size=10, color='#64748B'),
        showgrid=True,
        gridcolor='rgba(255,255,255,0.05)'
    )

    fig.update_layout(**layout)

    fig.update_yaxes(
        title_text="",
        tickfont=dict(color='#64748B'),
        gridcolor='rgba(255,255,255,0.05)',
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="% Above MA",
        range=[0, 100],
        tickfont=dict(color='#64748B'),
        gridcolor='rgba(255,255,255,0.05)',
        row=2, col=1
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Legend caption
    st.markdown(f'''
    <div style="display: flex; gap: 20px; justify-content: center; padding: 8px 0; font-size: 0.75rem;">
        <span style="color: {BREADTH_COLORS['ma20']}; font-weight: 600;">MA20 (Short)</span>
        <span style="color: {BREADTH_COLORS['ma50']}; font-weight: 600;">MA50 (Medium)</span>
        <span style="color: {BREADTH_COLORS['ma100']}; font-weight: 600;">MA100 (Long)</span>
    </div>
    ''', unsafe_allow_html=True)


def _render_breadth_gauges(state) -> None:
    """Render breadth gauges with progress bars and HTML styling."""

    gauges = [
        ("Short-term (MA20)", state.breadth_ma20_pct, BREADTH_COLORS['ma20']),
        ("Medium-term (MA50)", state.breadth_ma50_pct, BREADTH_COLORS['ma50']),
        ("Long-term (MA100)", state.breadth_ma100_pct, BREADTH_COLORS['ma100']),
    ]

    for label, value, color in gauges:
        # Status based on zone
        if value > 80:
            status = "Overbought"
            status_color = "#EF4444"
        elif value < 20:
            status = "Oversold"
            status_color = "#10B981"
        else:
            status = "Neutral"
            status_color = "#94A3B8"

        st.markdown(f'''
        <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                <span style="color: {color}; font-size: 0.8rem; font-weight: 600;">{label}</span>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: {status_color}; font-size: 0.75rem;">{status}</span>
                    <span style="color: #F8FAFC; font-size: 0.9rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">{value:.0f}%</span>
                </div>
            </div>
            <div style="height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                <div style="width: {min(value, 100)}%; height: 100%; background: linear-gradient(90deg, {color}, {color}aa); border-radius: 4px; transition: width 0.3s ease;"></div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    # Add summary
    avg_breadth = (state.breadth_ma20_pct + state.breadth_ma50_pct + state.breadth_ma100_pct) / 3
    if avg_breadth > 70:
        summary = "Market overbought - consider reducing exposure"
        summary_color = "#EF4444"
    elif avg_breadth < 30:
        summary = "Market oversold - potential buying opportunity"
        summary_color = "#10B981"
    else:
        summary = "Market in neutral zone"
        summary_color = "#94A3B8"

    st.markdown(f'''
    <div style="margin-top: 16px; padding: 12px; background: rgba(0,0,0,0.3); border-radius: 8px; border-left: 3px solid {summary_color};">
        <span style="color: {summary_color}; font-size: 0.85rem; font-weight: 500;">{summary}</span>
    </div>
    ''', unsafe_allow_html=True)


def _render_divergence_alert(state) -> None:
    """Render divergence detection alert with premium styling."""

    if state.divergence_type:
        if state.divergence_type == "BULLISH":
            icon_svg = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2"><path d="M12 19V5M5 12l7-7 7 7"/></svg>'''
            color = "#10B981"
            bg = "rgba(16, 185, 129, 0.1)"
            description = "VN-Index: Lower Lows | Breadth: Higher Lows"
            action = "Potential bullish reversal signal"
        else:
            icon_svg = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2"><path d="M12 5v14M5 12l7 7 7-7"/></svg>'''
            color = "#EF4444"
            bg = "rgba(239, 68, 68, 0.1)"
            description = "VN-Index: Higher Highs | Breadth: Lower Highs"
            action = "Potential bearish reversal signal"

        # Strength dots
        strength_dots = ''.join([
            f'<span style="display: inline-block; width: 8px; height: 8px; background: {color if i < state.divergence_strength else "rgba(255,255,255,0.2)"}; border-radius: 50%; margin-right: 4px;"></span>'
            for i in range(3)
        ])

        st.markdown(f'''
        <div style="background: {bg}; border: 1px solid {color}40; border-radius: 12px; padding: 20px; border-left: 4px solid {color};">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                {icon_svg}
                <div>
                    <div style="color: {color}; font-size: 1.1rem; font-weight: 700;">{state.divergence_type} DIVERGENCE</div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                        <span style="color: #94A3B8; font-size: 0.75rem;">Strength:</span>
                        {strength_dots}
                    </div>
                </div>
            </div>
            <div style="color: #E2E8F0; font-size: 0.85rem; margin-bottom: 8px;">{description}</div>
            <div style="color: {color}; font-size: 0.85rem; font-weight: 500;">{action}</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 12px; padding: 20px; text-align: center;">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" stroke-width="2" style="margin-bottom: 8px;">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 8v4M12 16h.01"/>
            </svg>
            <div style="color: #94A3B8; font-size: 0.9rem;">No divergence detected</div>
            <div style="color: #64748B; font-size: 0.75rem; margin-top: 4px;">Price and breadth moving in sync</div>
        </div>
        ''', unsafe_allow_html=True)
