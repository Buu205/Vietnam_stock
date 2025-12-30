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

# Weighted Market Health Score (4-8 week swing trading strategy)
MARKET_SCORE_WEIGHTS = {
    'ma50': 0.5,   # Trend backbone (50%)
    'ma20': 0.3,   # Timing/Trigger (30%)
    'ma100': 0.2,  # Safety filter (20%)
}

# Signal Matrix Styles (No emojis - clean professional design)
SIGNAL_MATRIX = {
    'STRONG_BUY': {
        'label': 'STRONG BUY',
        'subtitle': 'Deep Pullback',
        'action': 'Giải ngân mạnh. Rũ bỏ hoàn hảo.',
        'color': '#059669',
        'bg': 'rgba(5, 150, 105, 0.15)',
    },
    'BUY': {
        'label': 'BUY',
        'subtitle': 'Normal Pullback',
        'action': 'Mua gia tăng hoặc mở vị thế mới.',
        'color': '#10B981',
        'bg': 'rgba(16, 185, 129, 0.15)',
    },
    'HOLD': {
        'label': 'HOLD',
        'subtitle': 'Riding Trend',
        'action': 'Nắm giữ danh mục. Trend vẫn tốt.',
        'color': '#3B82F6',
        'bg': 'rgba(59, 130, 246, 0.15)',
    },
    'WARNING': {
        'label': 'WARNING',
        'subtitle': 'Overheated',
        'action': 'Không mua đuổi. Canh chốt lời margin.',
        'color': '#F59E0B',
        'bg': 'rgba(245, 158, 11, 0.15)',
    },
    'SELL': {
        'label': 'SELL',
        'subtitle': 'Bull Trap',
        'action': 'Bán hạ tỷ trọng. Đây là bẫy tăng giá.',
        'color': '#DC2626',
        'bg': 'rgba(220, 38, 38, 0.15)',
    },
    'DANGER': {
        'label': 'DANGER',
        'subtitle': 'Market Crash',
        'action': 'Đứng ngoài tuyệt đối. Không bắt đáy.',
        'color': '#7F1D1D',
        'bg': 'rgba(127, 29, 29, 0.2)',
    },
    'WAIT': {
        'label': 'WAIT',
        'subtitle': 'No Trend',
        'action': 'Quan sát. Chưa có điểm vào an toàn.',
        'color': '#64748B',
        'bg': 'rgba(100, 116, 139, 0.15)',
    },
    # Bottom Detection Signals
    'ACCUMULATING': {
        'label': 'ACCUMULATING',
        'subtitle': 'Smart Money Entering',
        'action': 'Theo dõi sát. Smart money đang tích lũy. Chuẩn bị vốn.',
        'color': '#6366F1',  # Indigo
        'bg': 'rgba(99, 102, 241, 0.15)',
    },
    'EARLY_BUY': {
        'label': 'EARLY BUY',
        'subtitle': 'Early Reversal',
        'action': 'Test mua 10-20% danh mục. Stop-loss chặt dưới đáy gần nhất.',
        'color': '#22D3EE',  # Cyan
        'bg': 'rgba(34, 211, 238, 0.15)',
    },
}

# Bottom Formation Stages for indicator display
BOTTOM_STAGES = {
    'CAPITULATION': {
        'label': 'CAPITULATION',
        'description': 'Hoảng loạn bán tháo',
        'condition': 'Tất cả MA < 25%, chưa tạo đáy cao hơn',
        'color': '#7F1D1D',
        'icon': '1',
    },
    'ACCUMULATING': {
        'label': 'ACCUMULATING',
        'description': 'Smart money đang vào',
        'condition': 'Tất cả MA < 30%, MA20 tạo đáy cao hơn (3d) và đang tăng',
        'color': '#6366F1',
        'icon': '2',
    },
    'EARLY_REVERSAL': {
        'label': 'EARLY REVERSAL',
        'description': 'Đảo chiều sớm',
        'condition': 'MA20 ≥ 25% + Higher Low, MA50 tạo đáy cao hơn (5d)',
        'color': '#22D3EE',
        'icon': '3',
    },
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

    # Handle missing data
    if state is None:
        st.warning("⚠️ Market data not available. Please run the data pipeline first.")
        st.code("python3 PROCESSORS/pipelines/run_all_daily_updates.py", language="bash")
        return

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

    # ============ BREADTH GAUGES (Full Width Horizontal) ============
    st.markdown("### Breadth Gauges")
    _render_breadth_gauges(state)

    # ============ DIVERGENCE ALERT (Below Gauges) ============
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
        vertical_spacing=0.06,
        row_heights=[0.4, 0.6],
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}]]
    )

    # Calculate VN-Index MAs
    import pandas as pd
    vnindex_series = pd.Series(history.vnindex_close)
    vnindex_ma20 = vnindex_series.rolling(window=20, min_periods=1).mean()
    vnindex_ma50 = vnindex_series.rolling(window=50, min_periods=1).mean()
    vnindex_ma100 = vnindex_series.rolling(window=100, min_periods=1).mean()

    # Row 1: VN-Index with MAs (Trading Terminal Style)
    # Main VN-Index line - Primary purple, prominent
    fig.add_trace(
        go.Scatter(
            x=history.date,
            y=history.vnindex_close,
            name='VN-Index',
            line=dict(color='#8B5CF6', width=2.5),
            hovertemplate='<b>VN-Index</b>: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )

    # MA20 - Green (short-term, fast)
    fig.add_trace(
        go.Scatter(
            x=history.date,
            y=vnindex_ma20,
            name='MA20',
            line=dict(color='#10B981', width=1.5, dash='dot'),
            opacity=0.85,
            hovertemplate='<b>MA20</b>: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )

    # MA50 - Amber (medium-term)
    fig.add_trace(
        go.Scatter(
            x=history.date,
            y=vnindex_ma50,
            name='MA50',
            line=dict(color='#F59E0B', width=1.5, dash='dot'),
            opacity=0.85,
            hovertemplate='<b>MA50</b>: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )

    # MA100 - Red (long-term, slow)
    fig.add_trace(
        go.Scatter(
            x=history.date,
            y=vnindex_ma100,
            name='MA100',
            line=dict(color='#EF4444', width=1.5, dash='dot'),
            opacity=0.85,
            hovertemplate='<b>MA100</b>: %{y:,.0f}<extra></extra>'
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

    # Calculate VN-Index y-axis range (min -5%, max +5%)
    vnindex_min = min(history.vnindex_close)
    vnindex_max = max(history.vnindex_close)
    vnindex_y_min = vnindex_min * 0.95  # -5%
    vnindex_y_max = vnindex_max * 1.05  # +5%

    # Layout from theme
    layout = get_chart_layout(height=540)
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
        range=[vnindex_y_min, vnindex_y_max],
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

    # Legend caption with two rows
    st.markdown(f'''
    <div style="display: flex; flex-direction: column; gap: 6px; padding: 8px 0; font-size: 0.75rem;">
        <div style="display: flex; gap: 20px; justify-content: center;">
            <span style="color: #8B5CF6; font-weight: 600;">● VN-Index</span>
            <span style="color: #10B981; font-weight: 600;">┄ MA20</span>
            <span style="color: #F59E0B; font-weight: 600;">┄ MA50</span>
            <span style="color: #EF4444; font-weight: 600;">┄ MA100</span>
        </div>
        <div style="display: flex; gap: 20px; justify-content: center; color: #64748B;">
            <span>Breadth:</span>
            <span style="color: {BREADTH_COLORS['ma20']}; font-weight: 600;">% > MA20</span>
            <span style="color: {BREADTH_COLORS['ma50']}; font-weight: 600;">% > MA50</span>
            <span style="color: {BREADTH_COLORS['ma100']}; font-weight: 600;">% > MA100</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)


def _render_breadth_gauges(state) -> None:
    """Render breadth gauges horizontally with progress bars."""

    gauges = [
        ("MA20", state.breadth_ma20_pct, BREADTH_COLORS['ma20']),
        ("MA50", state.breadth_ma50_pct, BREADTH_COLORS['ma50']),
        ("MA100", state.breadth_ma100_pct, BREADTH_COLORS['ma100']),
    ]

    # Render gauges in 3 columns horizontally
    cols = st.columns(3)
    for col, (label, value, color) in zip(cols, gauges):
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

        with col:
            st.markdown(f'''
            <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 8px; border-left: 3px solid {color};">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: {color}; font-size: 0.85rem; font-weight: 600;">{label}</span>
                    <span style="color: #F8FAFC; font-size: 1.1rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">{value:.0f}%</span>
                </div>
                <div style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;">
                    <div style="width: {min(value, 100)}%; height: 100%; background: {color}; border-radius: 3px;"></div>
                </div>
                <div style="color: {status_color}; font-size: 0.7rem; margin-top: 6px; text-align: right;">{status}</div>
            </div>
            ''', unsafe_allow_html=True)

    # Calculate Weighted Market Health Score
    market_score = (
        state.breadth_ma50_pct * MARKET_SCORE_WEIGHTS['ma50'] +
        state.breadth_ma20_pct * MARKET_SCORE_WEIGHTS['ma20'] +
        state.breadth_ma100_pct * MARKET_SCORE_WEIGHTS['ma100']
    )

    # Get breadth values for Signal Matrix logic
    b_ma20 = state.breadth_ma20_pct
    b_ma50 = state.breadth_ma50_pct
    b_ma100 = state.breadth_ma100_pct

    # Trend Filter: Uptrend when MA50 >= 50 AND MA100 >= 50
    is_uptrend = (b_ma50 >= 50) and (b_ma100 >= 50)

    # Recovery detection: MA20 is bouncing back (ONLY relevant in uptrend with buy signals)
    is_recovering = False
    if state.prev_breadth_ma20_pct is not None:
        is_recovering = b_ma20 > state.prev_breadth_ma20_pct

    # Determine Signal based on Signal Matrix (with Bottom Detection)
    if is_uptrend:
        # UPTREND scenarios (Buy signals)
        if b_ma20 < 20:
            signal_key = 'STRONG_BUY'
        elif b_ma20 < 40:
            signal_key = 'BUY'
        elif b_ma20 > 80:
            signal_key = 'WARNING'
        else:
            signal_key = 'HOLD'
    else:
        # DOWNTREND/SIDEWAYS scenarios (Defensive + Bottom Detection signals)
        if b_ma20 > 70:
            signal_key = 'SELL'
        elif b_ma50 < 30 and b_ma20 < 20 and not state.ma20_higher_low:
            signal_key = 'DANGER'
        # Bottom Detection Signals (based on higher lows pattern)
        elif state.bottom_stage == 'EARLY_REVERSAL':
            signal_key = 'EARLY_BUY'
        elif state.bottom_stage == 'ACCUMULATING':
            signal_key = 'ACCUMULATING'
        else:
            signal_key = 'WAIT'

    # Get signal style
    signal = SIGNAL_MATRIX[signal_key]

    # Trend status styling
    trend_color = '#10B981' if is_uptrend else '#EF4444'
    trend_label = 'UPTREND' if is_uptrend else 'DOWNTREND'
    trend_icon = '▲' if is_uptrend else '▼'

    # Score color based on value
    if market_score >= 60:
        score_color = '#10B981'
    elif market_score >= 40:
        score_color = '#F59E0B'
    else:
        score_color = '#EF4444'

    # Recovery indicator ONLY for buy signals in uptrend
    recovery_html = ""
    if is_uptrend and signal_key in ['STRONG_BUY', 'BUY'] and is_recovering:
        recovery_html = '<span style="color: #10B981; font-size: 0.7rem; margin-left: 6px;">▲ Recovering</span>'

    # Render comprehensive Signal Matrix Card
    st.markdown(f'''
    <div style="margin-top: 16px; background: rgba(0,0,0,0.4); border-radius: 12px; overflow: hidden;">
        <!-- Header Row: Score + Trend + Signal -->
        <div style="display: flex; align-items: stretch; border-bottom: 1px solid rgba(255,255,255,0.1);">
            <!-- Score Box -->
            <div style="padding: 16px 20px; background: rgba(0,0,0,0.3); border-right: 1px solid rgba(255,255,255,0.1); text-align: center; min-width: 90px;">
                <div style="color: {score_color}; font-size: 2rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; line-height: 1;">{market_score:.0f}</div>
                <div style="color: #64748B; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px;">Score</div>
            </div>
            <!-- Trend Status -->
            <div style="padding: 16px; border-right: 1px solid rgba(255,255,255,0.1); display: flex; flex-direction: column; justify-content: center;">
                <div style="color: {trend_color}; font-size: 0.75rem; font-weight: 600; display: flex; align-items: center; gap: 4px;">
                    <span>{trend_icon}</span>
                    <span>{trend_label}</span>
                </div>
                <div style="color: #64748B; font-size: 0.65rem; margin-top: 2px;">MA50≥50 & MA100≥50</div>
            </div>
            <!-- Signal Badge -->
            <div style="flex: 1; padding: 16px; display: flex; align-items: center; justify-content: flex-end;">
                <div style="background: {signal['bg']}; border: 1px solid {signal['color']}40; border-radius: 8px; padding: 8px 16px;">
                    <div style="color: {signal['color']}; font-size: 1rem; font-weight: 700; letter-spacing: 0.05em;">{signal['label']}</div>
                    <div style="color: #94A3B8; font-size: 0.7rem;">{signal['subtitle']}{recovery_html}</div>
                </div>
            </div>
        </div>
        <!-- Breadth Breakdown -->
        <div style="padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.1);">
            <div style="color: #64748B; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">Breadth Breakdown</div>
            <!-- MA20 -->
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="color: #8B5CF6; font-size: 0.75rem; font-weight: 600; width: 45px;">MA20</span>
                <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;">
                    <div style="width: {min(b_ma20, 100)}%; height: 100%; background: #8B5CF6; border-radius: 3px;"></div>
                </div>
                <span style="color: #E2E8F0; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; width: 35px; text-align: right;">{b_ma20:.0f}%</span>
                <span style="color: #64748B; font-size: 0.65rem; width: 50px;">Timing</span>
            </div>
            <!-- MA50 -->
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="color: #06B6D4; font-size: 0.75rem; font-weight: 600; width: 45px;">MA50</span>
                <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;">
                    <div style="width: {min(b_ma50, 100)}%; height: 100%; background: #06B6D4; border-radius: 3px;"></div>
                </div>
                <span style="color: #E2E8F0; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; width: 35px; text-align: right;">{b_ma50:.0f}%</span>
                <span style="color: #64748B; font-size: 0.65rem; width: 50px;">Trend{'  ⚠' if b_ma50 < 50 else ''}</span>
            </div>
            <!-- MA100 -->
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="color: #F59E0B; font-size: 0.75rem; font-weight: 600; width: 45px;">MA100</span>
                <div style="flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;">
                    <div style="width: {min(b_ma100, 100)}%; height: 100%; background: #F59E0B; border-radius: 3px;"></div>
                </div>
                <span style="color: #E2E8F0; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; width: 35px; text-align: right;">{b_ma100:.0f}%</span>
                <span style="color: #64748B; font-size: 0.65rem; width: 50px;">Safety</span>
            </div>
            <!-- Higher Lows Detection Info -->
            <div style="display: flex; flex-direction: column; gap: 6px; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.05);">
                <!-- MA20 Higher Low (3-day window) -->
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: #8B5CF6; font-size: 0.65rem; width: 75px;">MA20 (3d):</span>
                    <span style="color: #64748B; font-size: 0.65rem;">Low trước</span>
                    <span style="color: #94A3B8; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace;">{state.ma20_prev_low:.1f}%</span>
                    <span style="color: {'#10B981' if state.ma20_higher_low else '#EF4444'}; font-size: 0.7rem;">{'→' if not state.ma20_higher_low else '↗'}</span>
                    <span style="color: #64748B; font-size: 0.65rem;">Low sau</span>
                    <span style="color: {'#10B981' if state.ma20_higher_low else '#E2E8F0'}; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; font-weight: 600;">{state.ma20_recent_low:.1f}%</span>
                    <span style="color: {'#10B981' if state.ma20_higher_low else '#64748B'}; font-size: 0.65rem; font-weight: 600;">{'✓ Higher Low' if state.ma20_higher_low else ''}</span>
                </div>
                <!-- MA50 Higher Low (5-day window) -->
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: #06B6D4; font-size: 0.65rem; width: 75px;">MA50 (5d):</span>
                    <span style="color: #64748B; font-size: 0.65rem;">Low trước</span>
                    <span style="color: #94A3B8; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace;">{state.ma50_prev_low:.1f}%</span>
                    <span style="color: {'#10B981' if state.ma50_higher_low else '#EF4444'}; font-size: 0.7rem;">{'→' if not state.ma50_higher_low else '↗'}</span>
                    <span style="color: #64748B; font-size: 0.65rem;">Low sau</span>
                    <span style="color: {'#10B981' if state.ma50_higher_low else '#E2E8F0'}; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; font-weight: 600;">{state.ma50_recent_low:.1f}%</span>
                    <span style="color: {'#10B981' if state.ma50_higher_low else '#64748B'}; font-size: 0.65rem; font-weight: 600;">{'✓ Higher Low' if state.ma50_higher_low else ''}</span>
                </div>
            </div>
        </div>
        <!-- Action Recommendation -->
        <div style="padding: 12px 16px; background: {signal['bg']}; border-left: 3px solid {signal['color']};">
            <div style="color: {signal['color']}; font-size: 0.85rem; font-weight: 500;">{signal['action']}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # Render Bottom Formation Stage Indicator (only when bottom_stage is detected)
    _render_bottom_stage_indicator(state)


def _render_bottom_stage_indicator(state) -> None:
    """
    Render Bottom Formation Stage indicator with progress visualization.
    Only shows when market is in bottom formation phase.
    """
    if not state.bottom_stage:
        return  # No bottom stage detected, don't render

    stage_info = BOTTOM_STAGES.get(state.bottom_stage)
    if not stage_info:
        return

    # Determine progress position (1=CAPITULATION, 2=ACCUMULATING, 3=EARLY_REVERSAL, 4=CONFIRMED)
    stage_positions = {
        'CAPITULATION': 1,
        'ACCUMULATING': 2,
        'EARLY_REVERSAL': 3,
    }
    current_pos = stage_positions.get(state.bottom_stage, 0)

    # Build stage dots
    def get_stage_dot(pos: int, stage_key: str, label: str) -> str:
        stage = BOTTOM_STAGES.get(stage_key, {})
        color = stage.get('color', '#64748B')
        is_current = pos == current_pos
        is_completed = pos < current_pos

        # Dot style
        if is_current:
            dot_style = f"background: {color}; box-shadow: 0 0 8px {color};"
            text_color = color
            font_weight = "700"
        elif is_completed:
            dot_style = f"background: {color}80;"
            text_color = f"{color}80"
            font_weight = "500"
        else:
            dot_style = "background: rgba(255,255,255,0.2);"
            text_color = "#64748B"
            font_weight = "400"

        return f'''
        <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
            <div style="width: 24px; height: 24px; border-radius: 50%; {dot_style} display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; color: {'#0F172A' if is_current else '#94A3B8'};">{pos}</div>
            <div style="color: {text_color}; font-size: 0.6rem; font-weight: {font_weight}; margin-top: 4px; text-align: center;">{label}</div>
        </div>
        '''

    # Progress line position (0-100%)
    progress_pct = ((current_pos - 1) / 3) * 100

    st.markdown(f'''
    <div style="margin-top: 12px; background: rgba(0,0,0,0.4); border: 1px solid {stage_info['color']}40; border-radius: 12px; overflow: hidden;">
        <!-- Header -->
        <div style="padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 8px; height: 8px; background: {stage_info['color']}; border-radius: 50%; animation: pulse 2s infinite;"></div>
                <span style="color: #E2E8F0; font-size: 0.8rem; font-weight: 600;">BOTTOM FORMATION DETECTED</span>
            </div>
            <div style="background: {stage_info['color']}20; border: 1px solid {stage_info['color']}40; border-radius: 6px; padding: 4px 10px;">
                <span style="color: {stage_info['color']}; font-size: 0.75rem; font-weight: 700;">{stage_info['label']}</span>
            </div>
        </div>

        <!-- Stage Progress -->
        <div style="padding: 16px;">
            <!-- Progress Track -->
            <div style="position: relative; margin-bottom: 8px;">
                <div style="height: 3px; background: rgba(255,255,255,0.1); border-radius: 2px;"></div>
                <div style="position: absolute; top: 0; left: 0; height: 3px; width: {progress_pct}%; background: linear-gradient(90deg, #7F1D1D, #6366F1, #22D3EE); border-radius: 2px;"></div>
            </div>

            <!-- Stage Dots -->
            <div style="display: flex; justify-content: space-between; margin-top: -20px;">
                {get_stage_dot(1, 'CAPITULATION', 'Capitulation')}
                {get_stage_dot(2, 'ACCUMULATING', 'Accumulating')}
                {get_stage_dot(3, 'EARLY_REVERSAL', 'Early Reversal')}
                <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
                    <div style="width: 24px; height: 24px; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; color: #64748B;">4</div>
                    <div style="color: #64748B; font-size: 0.6rem; font-weight: 400; margin-top: 4px; text-align: center;">Confirmed</div>
                </div>
            </div>
        </div>

        <!-- Current Stage Details -->
        <div style="padding: 12px 16px; background: {stage_info['color']}10; border-top: 1px solid rgba(255,255,255,0.05);">
            <div style="color: {stage_info['color']}; font-size: 0.85rem; font-weight: 600; margin-bottom: 4px;">{stage_info['description']}</div>
            <div style="color: #94A3B8; font-size: 0.75rem;">
                <span style="color: #64748B;">Điều kiện:</span> {stage_info['condition']}
            </div>
        </div>
    </div>

    <style>
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
    </style>
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
