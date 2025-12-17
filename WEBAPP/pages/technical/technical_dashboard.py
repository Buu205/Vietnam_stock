"""
Technical Analysis Dashboard
============================
Premium financial dashboard for technical analysis.

Design: Financial Editorial Theme
- Dark terminal aesthetic with vibrant accents
- Candlestick charts with MA overlays
- RSI, MACD, Bollinger Bands

Run:
    streamlit run WEBAPP/pages/technical/technical_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from WEBAPP.services.technical_service import TechnicalService
from WEBAPP.core.styles import get_page_style, get_chart_layout, CHART_COLORS

# Note: st.set_page_config is handled by main_app.py

# Inject premium styles
st.markdown(get_page_style(), unsafe_allow_html=True)

# Header
st.title("Technical Analysis")
st.markdown("**Price charts and technical indicators for Vietnamese stocks**")
st.markdown("---")

# Sidebar
st.sidebar.markdown("## Filters")

try:
    service = TechnicalService()
    available_tickers = service.get_available_tickers()
    if not available_tickers:
        st.error("No technical data found.")
        st.stop()
except FileNotFoundError as e:
    st.error(f"Error: {e}")
    st.stop()

# Ticker selector - check for Quick Search pre-selection
st.sidebar.markdown("### Stock")
default_ticker = st.session_state.get('quick_search_ticker', None)
if default_ticker and default_ticker in available_tickers:
    default_index = available_tickers.index(default_ticker)
    # Clear the quick search after using it
    st.session_state['quick_search_ticker'] = None
else:
    default_index = 0

ticker = st.sidebar.selectbox(
    "Select Stock",
    options=available_tickers,
    index=default_index,
    label_visibility="collapsed"
)

# Days selector
limit = st.sidebar.slider("History (Days)", min_value=30, max_value=500, value=180)

# Chart options
st.sidebar.markdown("### Chart Options")
show_volume = st.sidebar.checkbox("Show Volume", value=True)
show_bb = st.sidebar.checkbox("Show Bollinger Bands", value=False)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Load data
@st.cache_data(ttl=3600)
def load_data(ticker, limit):
    service = TechnicalService()
    return service.get_technical_data(ticker, limit=limit)

df = load_data(ticker, limit)
if df.empty:
    st.warning(f"No data for {ticker}")
    st.stop()

# Get latest values
latest = df.iloc[-1]

# ============================================================================
# METRIC CARDS
# ============================================================================
st.markdown(f"### Current Indicators — {ticker}")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    close = latest.get('close', 0) or 0
    # Calculate delta
    if len(df) > 1:
        prev_close = df.iloc[-2].get('close', close)
        delta_pct = ((close - prev_close) / prev_close * 100) if prev_close > 0 else 0
        st.metric("Close Price", f"{close:,.0f}", f"{delta_pct:+.2f}%")
    else:
        st.metric("Close Price", f"{close:,.0f}")

with col2:
    rsi = latest.get('rsi_14', 0) or 0
    rsi_status = "🔴 Overbought" if rsi > 70 else "🟢 Oversold" if rsi < 30 else "⚪ Neutral"
    st.metric("RSI (14)", f"{rsi:.1f}", rsi_status)

with col3:
    pct = latest.get('price_vs_sma50', 0) or 0
    trend = "📈 Above" if pct > 0 else "📉 Below"
    st.metric("Price vs SMA50", f"{pct:+.1f}%", trend)

with col4:
    adx = latest.get('adx_14', 0) or 0
    adx_status = "💪 Strong" if adx > 25 else "😴 Weak"
    st.metric("ADX (14)", f"{adx:.1f}", adx_status)

with col5:
    macd = latest.get('macd', 0) or 0
    macd_signal = latest.get('macd_signal', 0) or 0
    macd_trend = "🟢 Bullish" if macd > macd_signal else "🔴 Bearish"
    st.metric("MACD", f"{macd:.2f}", macd_trend)

st.markdown("---")

# ============================================================================
# TABS
# ============================================================================
tab_charts, tab_oscillators, tab_tables = st.tabs(["📊 Price & Volume", "📈 Oscillators", "📋 Data"])

# ============================================================================
# TAB 1: PRICE & VOLUME CHARTS
# ============================================================================
with tab_charts:
    st.markdown("### OHLC Chart with Moving Averages")

    # Main price chart
    if show_volume:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.75, 0.25]
        )
    else:
        fig = go.Figure()

    # Candlestick
    if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
        fig.add_trace(go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLC',
            increasing=dict(line=dict(color='#00D4AA'), fillcolor='#00D4AA'),
            decreasing=dict(line=dict(color='#FF6B6B'), fillcolor='#FF6B6B'),
        ), row=1 if show_volume else None, col=1 if show_volume else None)

    # Moving averages
    ma_configs = [
        ('sma_20', '#5B8DEF', 'SMA 20'),
        ('sma_50', '#FFD666', 'SMA 50'),
        ('sma_200', '#A78BFA', 'SMA 200'),
    ]

    for ma_col, color, name in ma_configs:
        if ma_col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df[ma_col],
                name=name,
                mode='lines',
                line=dict(color=color, width=1.5),
                hovertemplate=f'<b>{name}</b>: %{{y:,.0f}}<extra></extra>'
            ), row=1 if show_volume else None, col=1 if show_volume else None)

    # Bollinger Bands
    if show_bb and all(col in df.columns for col in ['bb_upper', 'bb_middle', 'bb_lower']):
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['bb_upper'],
            name='BB Upper',
            mode='lines',
            line=dict(color='rgba(255, 214, 102, 0.5)', width=1),
            showlegend=False,
            hoverinfo='skip'
        ), row=1 if show_volume else None, col=1 if show_volume else None)

        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['bb_lower'],
            name='BB Lower',
            mode='lines',
            line=dict(color='rgba(255, 214, 102, 0.5)', width=1),
            fill='tonexty',
            fillcolor='rgba(255, 214, 102, 0.1)',
            showlegend=False,
            hoverinfo='skip'
        ), row=1 if show_volume else None, col=1 if show_volume else None)

        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['bb_middle'],
            name='BB Middle',
            mode='lines',
            line=dict(color='rgba(255, 214, 102, 0.7)', width=1, dash='dot'),
            hovertemplate='<b>BB Middle</b>: %{y:,.0f}<extra></extra>'
        ), row=1 if show_volume else None, col=1 if show_volume else None)

    # Volume
    if show_volume and 'volume' in df.columns:
        colors = ['#00D4AA' if df['close'].iloc[i] >= df['open'].iloc[i] else '#FF6B6B'
                  for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7,
            hovertemplate='<b>Volume</b>: %{y:,.0f}<extra></extra>'
        ), row=2, col=1)

    layout = get_chart_layout(height=550 if show_volume else 450)
    layout['xaxis']['rangeslider'] = {'visible': False}
    layout['legend'] = dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1
    )

    if show_volume:
        layout['yaxis'] = dict(title='Price', gridcolor='rgba(148, 163, 184, 0.1)')
        layout['yaxis2'] = dict(title='Volume', gridcolor='rgba(148, 163, 184, 0.1)')

    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)

    # Signal summary
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### MA Signal Summary")
        ma_signals = []

        price = latest.get('close', 0)
        for ma_col, _, name in ma_configs:
            if ma_col in df.columns:
                ma_val = latest.get(ma_col, 0)
                if ma_val and ma_val > 0:
                    signal = "🟢 Above" if price > ma_val else "🔴 Below"
                    pct_diff = ((price - ma_val) / ma_val * 100) if ma_val > 0 else 0
                    ma_signals.append({
                        'MA': name,
                        'Value': f"{ma_val:,.0f}",
                        'Signal': signal,
                        'Distance': f"{pct_diff:+.1f}%"
                    })

        if ma_signals:
            st.dataframe(pd.DataFrame(ma_signals), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("### Trend Analysis")

        # Calculate trend
        if len(df) >= 20:
            sma_20_trend = df['sma_20'].iloc[-1] > df['sma_20'].iloc[-20] if 'sma_20' in df.columns else None
            sma_50_trend = df['sma_50'].iloc[-1] > df['sma_50'].iloc[-20] if 'sma_50' in df.columns and len(df) >= 50 else None

            trend_data = []
            if sma_20_trend is not None:
                trend_data.append({
                    'Indicator': 'SMA 20 Direction',
                    'Status': '📈 Uptrend' if sma_20_trend else '📉 Downtrend'
                })
            if sma_50_trend is not None:
                trend_data.append({
                    'Indicator': 'SMA 50 Direction',
                    'Status': '📈 Uptrend' if sma_50_trend else '📉 Downtrend'
                })

            # Golden/Death Cross check
            if 'sma_50' in df.columns and 'sma_200' in df.columns:
                golden = latest.get('sma_50', 0) > latest.get('sma_200', 0)
                trend_data.append({
                    'Indicator': 'MA Cross',
                    'Status': '🌟 Golden Cross' if golden else '💀 Death Cross'
                })

            if trend_data:
                st.dataframe(pd.DataFrame(trend_data), use_container_width=True, hide_index=True)

# ============================================================================
# TAB 2: OSCILLATORS
# ============================================================================
with tab_oscillators:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### RSI (14)")
        if 'rsi_14' in df.columns:
            fig = go.Figure()

            # RSI line
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['rsi_14'],
                name='RSI',
                mode='lines',
                line=dict(color='#00D4AA', width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 212, 170, 0.1)',
                hovertemplate='<b>RSI</b>: %{y:.1f}<extra></extra>'
            ))

            # Overbought/Oversold zones
            fig.add_hrect(y0=70, y1=100, fillcolor='rgba(255, 107, 107, 0.1)', line_width=0)
            fig.add_hrect(y0=0, y1=30, fillcolor='rgba(0, 212, 170, 0.1)', line_width=0)

            fig.add_hline(y=70, line=dict(color='#FF6B6B', width=1, dash='dash'),
                         annotation=dict(text='Overbought (70)', font=dict(color='#FF6B6B', size=10)))
            fig.add_hline(y=30, line=dict(color='#00D4AA', width=1, dash='dash'),
                         annotation=dict(text='Oversold (30)', font=dict(color='#00D4AA', size=10)))
            fig.add_hline(y=50, line=dict(color='#94A3B8', width=1, dash='dot'))

            layout = get_chart_layout(height=300)
            layout['yaxis']['range'] = [0, 100]
            fig.update_layout(**layout)

            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### MACD")
        if all(col in df.columns for col in ['macd', 'macd_signal', 'macd_hist']):
            fig = go.Figure()

            # MACD histogram
            colors = ['#00D4AA' if v >= 0 else '#FF6B6B' for v in df['macd_hist']]
            fig.add_trace(go.Bar(
                x=df['date'],
                y=df['macd_hist'],
                name='Histogram',
                marker_color=colors,
                opacity=0.6,
                hovertemplate='<b>Histogram</b>: %{y:.2f}<extra></extra>'
            ))

            # MACD & Signal lines
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['macd'],
                name='MACD',
                mode='lines',
                line=dict(color='#5B8DEF', width=2),
                hovertemplate='<b>MACD</b>: %{y:.2f}<extra></extra>'
            ))

            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['macd_signal'],
                name='Signal',
                mode='lines',
                line=dict(color='#FFD666', width=2),
                hovertemplate='<b>Signal</b>: %{y:.2f}<extra></extra>'
            ))

            fig.add_hline(y=0, line=dict(color='#94A3B8', width=1, dash='dot'))

            layout = get_chart_layout(height=300)
            layout['legend'] = dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            fig.update_layout(**layout)

            st.plotly_chart(fig, use_container_width=True)

    # Stochastic and other oscillators
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Stochastic Oscillator")
        if all(col in df.columns for col in ['stoch_k', 'stoch_d']):
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['stoch_k'],
                name='%K',
                mode='lines',
                line=dict(color='#5B8DEF', width=2),
            ))

            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['stoch_d'],
                name='%D',
                mode='lines',
                line=dict(color='#FFD666', width=2),
            ))

            fig.add_hrect(y0=80, y1=100, fillcolor='rgba(255, 107, 107, 0.1)', line_width=0)
            fig.add_hrect(y0=0, y1=20, fillcolor='rgba(0, 212, 170, 0.1)', line_width=0)

            fig.add_hline(y=80, line=dict(color='#FF6B6B', width=1, dash='dash'))
            fig.add_hline(y=20, line=dict(color='#00D4AA', width=1, dash='dash'))

            layout = get_chart_layout(height=250)
            layout['yaxis']['range'] = [0, 100]
            layout['legend'] = dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            fig.update_layout(**layout)

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Stochastic data not available")

    with col2:
        st.markdown("### CCI (20)")
        if 'cci_20' in df.columns:
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['cci_20'],
                name='CCI',
                mode='lines',
                line=dict(color='#A78BFA', width=2),
                fill='tozeroy',
                fillcolor='rgba(167, 139, 250, 0.1)',
            ))

            fig.add_hline(y=100, line=dict(color='#FF6B6B', width=1, dash='dash'),
                         annotation=dict(text='Overbought (+100)', font=dict(size=10)))
            fig.add_hline(y=-100, line=dict(color='#00D4AA', width=1, dash='dash'),
                         annotation=dict(text='Oversold (-100)', font=dict(size=10)))
            fig.add_hline(y=0, line=dict(color='#94A3B8', width=1, dash='dot'))

            layout = get_chart_layout(height=250)
            fig.update_layout(**layout)

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("CCI data not available")

# ============================================================================
# TAB 3: DATA TABLES
# ============================================================================
with tab_tables:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Price & Moving Averages")
        price_cols = {
            'Close': 'close',
            'SMA 20': 'sma_20',
            'SMA 50': 'sma_50',
            'SMA 100': 'sma_100',
            'SMA 200': 'sma_200',
            'EMA 20': 'ema_20',
            'EMA 50': 'ema_50'
        }

        table_data = []
        for name, col in price_cols.items():
            if col in df.columns:
                val = latest.get(col)
                table_data.append({
                    'Indicator': name,
                    'Value': f"{val:,.0f}" if pd.notna(val) else "-"
                })

        if table_data:
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

        st.markdown("### Volatility")
        vol_cols = {
            'ATR (14)': 'atr_14',
            'BB Upper': 'bb_upper',
            'BB Middle': 'bb_middle',
            'BB Lower': 'bb_lower',
            'BB Width': 'bb_width'
        }

        vol_data = []
        for name, col in vol_cols.items():
            if col in df.columns:
                val = latest.get(col)
                if col == 'bb_width':
                    vol_data.append({'Indicator': name, 'Value': f"{val:.2f}" if pd.notna(val) else "-"})
                else:
                    vol_data.append({'Indicator': name, 'Value': f"{val:,.0f}" if pd.notna(val) else "-"})

        if vol_data:
            st.dataframe(pd.DataFrame(vol_data), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("### Momentum Indicators")
        ind_cols = {
            'RSI (14)': 'rsi_14',
            'ADX (14)': 'adx_14',
            'MACD': 'macd',
            'MACD Signal': 'macd_signal',
            'MACD Histogram': 'macd_hist',
            'Stoch %K': 'stoch_k',
            'Stoch %D': 'stoch_d',
            'CCI (20)': 'cci_20',
            'MFI (14)': 'mfi_14'
        }

        table_data = []
        for name, col in ind_cols.items():
            if col in df.columns:
                val = latest.get(col)
                table_data.append({
                    'Indicator': name,
                    'Value': f"{val:.2f}" if pd.notna(val) else "-"
                })

        if table_data:
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

        st.markdown("### Volume Indicators")
        vol_ind_cols = {
            'Volume': 'volume',
            'OBV': 'obv',
            'CMF (20)': 'cmf_20'
        }

        vol_ind_data = []
        for name, col in vol_ind_cols.items():
            if col in df.columns:
                val = latest.get(col)
                if col == 'volume' or col == 'obv':
                    vol_ind_data.append({'Indicator': name, 'Value': f"{val:,.0f}" if pd.notna(val) else "-"})
                else:
                    vol_ind_data.append({'Indicator': name, 'Value': f"{val:.3f}" if pd.notna(val) else "-"})

        if vol_ind_data:
            st.dataframe(pd.DataFrame(vol_ind_data), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Technical Data (CSV)",
        csv,
        f"{ticker}_technical_data.csv",
        "text/csv",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.caption(f"Data: Technical Analysis | Ticker: **{ticker}** | {len(df)} trading days | Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
