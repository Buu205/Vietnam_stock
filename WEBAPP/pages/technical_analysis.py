#!/usr/bin/env python3
"""
Technical Analysis Dashboard
=============================

Comprehensive technical analysis dashboard with:
- Technical Indicators Overview
- Trading Alerts
- Money Flow Analysis
- Market Breadth
- Sector Analysis
- VN-Index Analysis
- Market Regime

Author: Claude Code
Date: 2025-12-15
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add project root
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from config.registries import SectorRegistry

# Page config
st.set_page_config(
    page_title="Technical Analysis",
    page_icon="📊",
    layout="wide"
)

# Initialize registry
@st.cache_resource
def get_sector_registry():
    return SectorRegistry()

sector_reg = get_sector_registry()


# === DATA LOADING FUNCTIONS ===

@st.cache_data(ttl=3600)
def load_technical_data():
    """Load technical indicators data."""
    path = Path("DATA/processed/technical/basic_data.parquet")
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_alerts(alert_type):
    """Load alert data."""
    path = Path(f"DATA/processed/technical/alerts/daily/{alert_type}_latest.parquet")
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_money_flow():
    """Load money flow data."""
    path = Path("DATA/processed/technical/money_flow/individual_money_flow.parquet")
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_sector_money_flow():
    """Load sector money flow data."""
    path = Path("DATA/processed/technical/money_flow/sector_money_flow.parquet")
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_market_breadth():
    """Load market breadth data."""
    path = Path("DATA/processed/technical/market_breadth/market_breadth_daily.parquet")
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_sector_breadth():
    """Load sector breadth data."""
    path = Path("DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet")
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_market_regime():
    """Load market regime data."""
    path = Path("DATA/processed/technical/market_regime/market_regime_history.parquet")
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_vnindex():
    """Load VN-Index data."""
    path = Path("DATA/processed/technical/vnindex/vnindex_indicators.parquet")
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()


# === HELPER FUNCTIONS ===

def get_signal_color(signal):
    """Get color for signal."""
    if 'BUY' in str(signal) or 'BULLISH' in str(signal):
        return 'green'
    elif 'SELL' in str(signal) or 'BEARISH' in str(signal):
        return 'red'
    else:
        return 'gray'


# === MAIN DASHBOARD ===

st.title("📊 Technical Analysis Dashboard")

# Sidebar
st.sidebar.header("Settings")

# Load data
tech_df = load_technical_data()

if tech_df.empty:
    st.error("⚠️ No technical data available. Please run the daily TA update pipeline first.")
    st.code("python3 PROCESSORS/technical/pipelines/daily_complete_ta_update.py")
    st.stop()

# Get latest date
latest_date = tech_df['date'].max()
st.sidebar.info(f"📅 Latest data: {latest_date}")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Market Overview",
    "🚨 Trading Alerts",
    "💰 Money Flow",
    "📊 Market Breadth",
    "🏢 Sector Analysis",
    "📉 VN-Index",
    "🌡️ Market Regime"
])

# === TAB 1: Market Overview ===
with tab1:
    st.header("Market Overview")

    # Market Breadth
    breadth_df = load_market_breadth()
    if not breadth_df.empty:
        latest_breadth = breadth_df[breadth_df['date'] == latest_date].iloc[0]

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Market Trend",
                latest_breadth['market_trend'],
                delta=None
            )

        with col2:
            st.metric(
                "Above MA20",
                f"{latest_breadth['above_ma20']} ({latest_breadth['above_ma20_pct']:.1f}%)"
            )

        with col3:
            st.metric(
                "Above MA50",
                f"{latest_breadth['above_ma50']} ({latest_breadth['above_ma50_pct']:.1f}%)"
            )

        with col4:
            st.metric(
                "Above MA200",
                f"{latest_breadth['above_ma200']} ({latest_breadth['above_ma200_pct']:.1f}%)"
            )

        with col5:
            st.metric(
                "A/D Ratio",
                f"{latest_breadth['ad_ratio']:.2f}",
                delta=f"{latest_breadth['advancing']} / {latest_breadth['declining']}"
            )

    # Market Breadth Chart
    st.subheader("Market Breadth Trend")
    if not breadth_df.empty:
        # Last 60 days
        breadth_60 = breadth_df.tail(60)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=breadth_60['date'],
            y=breadth_60['above_ma20_pct'],
            name='Above MA20',
            line=dict(color='blue', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=breadth_60['date'],
            y=breadth_60['above_ma50_pct'],
            name='Above MA50',
            line=dict(color='green', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=breadth_60['date'],
            y=breadth_60['above_ma200_pct'],
            name='Above MA200',
            line=dict(color='red', width=2)
        ))

        # Add reference lines
        fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_hline(y=70, line_dash="dot", line_color="green", opacity=0.3)
        fig.add_hline(y=30, line_dash="dot", line_color="red", opacity=0.3)

        fig.update_layout(
            title="% Stocks Above Moving Averages",
            xaxis_title="Date",
            yaxis_title="Percentage (%)",
            hovermode='x unified',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

# === TAB 2: Trading Alerts ===
with tab2:
    st.header("🚨 Trading Alerts")

    alert_col1, alert_col2 = st.columns(2)

    # MA Crossover Alerts
    with alert_col1:
        st.subheader("MA Crossover Alerts")
        ma_alerts = load_alerts('ma_crossover')
        if not ma_alerts.empty:
            ma_latest = ma_alerts[ma_alerts['date'] == latest_date]

            # Filter
            signal_filter = st.selectbox(
                "Filter by signal",
                ['All', 'BULLISH', 'BEARISH'],
                key='ma_filter'
            )

            if signal_filter != 'All':
                ma_latest = ma_latest[ma_latest['signal'] == signal_filter]

            # Display
            st.dataframe(
                ma_latest[['symbol', 'alert_type', 'ma_period', 'price', 'signal']].style.applymap(
                    lambda x: f'color: {get_signal_color(x)}',
                    subset=['signal']
                ),
                use_container_width=True,
                height=400
            )

            st.info(f"Found {len(ma_latest)} MA crossover alerts")

    # Volume Spike Alerts
    with alert_col2:
        st.subheader("Smart Volume Spike Alerts")
        vol_alerts = load_alerts('volume_spike')
        if not vol_alerts.empty:
            vol_latest = vol_alerts[vol_alerts['date'] == latest_date]

            # Sort by confidence
            vol_latest = vol_latest.sort_values('confidence', ascending=False)

            # Display
            st.dataframe(
                vol_latest[['symbol', 'volume_ratio', 'confirmations', 'confidence', 'signal']].style.applymap(
                    lambda x: f'color: {get_signal_color(x)}',
                    subset=['signal']
                ),
                use_container_width=True,
                height=400
            )

            st.info(f"Found {len(vol_latest)} volume spike alerts")

    # Breakout Alerts
    st.subheader("Breakout/Breakdown Alerts")
    breakout_alerts = load_alerts('breakout')
    if not breakout_alerts.empty:
        breakout_latest = breakout_alerts[breakout_alerts['date'] == latest_date]

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Breakout Up", len(breakout_latest[breakout_latest['signal'] == 'BULLISH_BREAKOUT']))

        with col2:
            st.metric("Breakdown", len(breakout_latest[breakout_latest['signal'] == 'BEARISH_BREAKDOWN']))

        st.dataframe(
            breakout_latest[['symbol', 'alert_type', 'price', 'resistance_level', 'volume_confirmed', 'signal']],
            use_container_width=True
        )

    # Pattern Alerts
    st.subheader("Candlestick Pattern Alerts")
    pattern_alerts = load_alerts('patterns')
    if not pattern_alerts.empty:
        pattern_latest = pattern_alerts[pattern_alerts['date'] == latest_date]

        # Group by pattern
        pattern_counts = pattern_latest.groupby(['pattern_name', 'signal']).size().reset_index(name='count')

        col1, col2 = st.columns([1, 2])

        with col1:
            st.dataframe(pattern_counts, use_container_width=True, height=300)

        with col2:
            # Pattern filter
            selected_pattern = st.selectbox(
                "Select pattern",
                ['All'] + sorted(pattern_latest['pattern_name'].unique().tolist())
            )

            if selected_pattern != 'All':
                filtered_patterns = pattern_latest[pattern_latest['pattern_name'] == selected_pattern]
            else:
                filtered_patterns = pattern_latest

            st.dataframe(
                filtered_patterns[['symbol', 'pattern_name', 'signal', 'strength', 'price']],
                use_container_width=True,
                height=300
            )

# === TAB 3: Money Flow ===
with tab3:
    st.header("💰 Money Flow Analysis")

    # Sector Money Flow
    st.subheader("Sector Money Flow")
    sector_mf = load_sector_money_flow()
    if not sector_mf.empty:
        sector_mf_latest = sector_mf[sector_mf['date'] == latest_date].copy()

        # Sort by inflow %
        sector_mf_latest = sector_mf_latest.sort_values('inflow_pct', ascending=False)

        # Chart
        fig = px.bar(
            sector_mf_latest,
            x='sector_code',
            y='inflow_pct',
            color='flow_signal',
            title='Sector Money Flow (% Change)',
            color_discrete_map={
                'STRONG_INFLOW': 'darkgreen',
                'INFLOW': 'green',
                'NEUTRAL': 'gray',
                'OUTFLOW': 'orange',
                'STRONG_OUTFLOW': 'red'
            }
        )

        fig.add_hline(y=0, line_dash="dash", line_color="black")
        fig.update_layout(height=400)

        st.plotly_chart(fig, use_container_width=True)

        # Table
        st.dataframe(
            sector_mf_latest[['sector_code', 'money_flow', 'inflow_pct', 'flow_signal', 'stock_count', 'top_contributors']],
            use_container_width=True
        )

    # Individual Stock Money Flow
    st.subheader("Individual Stock Money Flow")
    mf_df = load_money_flow()
    if not mf_df.empty:
        mf_latest = mf_df[mf_df['date'] == latest_date].copy()

        # Filter
        mf_signal_filter = st.selectbox(
            "Filter by signal",
            ['All', 'STRONG_ACCUMULATION', 'ACCUMULATION', 'NEUTRAL', 'DISTRIBUTION', 'STRONG_DISTRIBUTION']
        )

        if mf_signal_filter != 'All':
            mf_latest = mf_latest[mf_latest['money_flow_signal'] == mf_signal_filter]

        # Display top 50
        st.dataframe(
            mf_latest[['symbol', 'cmf_20', 'mfi_14', 'obv', 'money_flow_signal']].head(50),
            use_container_width=True,
            height=400
        )

# === TAB 4: Market Breadth ===
with tab4:
    st.header("📊 Market Breadth")

    breadth_df = load_market_breadth()
    if not breadth_df.empty:
        # Last 90 days
        breadth_90 = breadth_df.tail(90)

        col1, col2 = st.columns(2)

        with col1:
            # MA Breadth
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=breadth_90['date'],
                y=breadth_90['above_ma20'],
                name='Above MA20',
                fill='tonexty',
                line=dict(color='blue')
            ))

            fig.add_trace(go.Scatter(
                x=breadth_90['date'],
                y=breadth_90['above_ma50'],
                name='Above MA50',
                fill='tonexty',
                line=dict(color='green')
            ))

            fig.add_trace(go.Scatter(
                x=breadth_90['date'],
                y=breadth_90['above_ma200'],
                name='Above MA200',
                line=dict(color='red')
            ))

            fig.update_layout(
                title="Stocks Above Moving Averages",
                xaxis_title="Date",
                yaxis_title="Number of Stocks",
                hovermode='x unified',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # A/D Ratio
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=breadth_90['date'],
                y=breadth_90['ad_ratio'],
                name='A/D Ratio',
                line=dict(color='purple', width=2),
                fill='tozeroy'
            ))

            fig.add_hline(y=1.0, line_dash="dash", line_color="gray")

            fig.update_layout(
                title="Advance/Decline Ratio",
                xaxis_title="Date",
                yaxis_title="A/D Ratio",
                hovermode='x unified',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        # Data table
        st.dataframe(
            breadth_90[['date', 'total_stocks', 'above_ma20', 'above_ma50', 'above_ma200',
                       'advancing', 'declining', 'ad_ratio', 'market_trend']].tail(30),
            use_container_width=True
        )

# === TAB 5: Sector Analysis ===
with tab5:
    st.header("🏢 Sector Analysis")

    sector_breadth_df = load_sector_breadth()
    if not sector_breadth_df.empty:
        sector_breadth_latest = sector_breadth_df[sector_breadth_df['date'] == latest_date].copy()

        # Sector Strength Heatmap
        st.subheader("Sector Strength Score")

        fig = px.bar(
            sector_breadth_latest.sort_values('strength_score', ascending=False),
            x='sector_code',
            y='strength_score',
            color='sector_trend',
            title='Sector Strength Ranking',
            color_discrete_map={
                'STRONG_BULLISH': 'darkgreen',
                'BULLISH': 'green',
                'NEUTRAL': 'gray',
                'BEARISH': 'orange',
                'STRONG_BEARISH': 'red'
            }
        )

        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Detailed table
        st.subheader("Sector Breadth Details")
        st.dataframe(
            sector_breadth_latest[[
                'sector_code', 'total_stocks', 'pct_above_ma20', 'pct_above_ma50',
                'pct_above_ma200', 'ad_ratio', 'sector_trend', 'strength_score'
            ]],
            use_container_width=True
        )

        # RSI Breadth
        st.subheader("Sector RSI Distribution")

        col1, col2, col3, col4 = st.columns(4)

        for idx, row in sector_breadth_latest.iterrows():
            with eval(f"col{(idx % 4) + 1}"):
                st.metric(
                    row['sector_code'],
                    f"Bullish: {row['bullish_rsi']}",
                    delta=f"OB: {row['overbought']} / OS: {row['oversold']}"
                )

# === TAB 6: VN-Index ===
with tab6:
    st.header("📉 VN-Index Technical Analysis")

    vnindex_df = load_vnindex()
    if not vnindex_df.empty:
        # Latest data
        latest_vni = vnindex_df.tail(1).iloc[0]

        # Metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Close", f"{latest_vni['close']:.2f}")

        with col2:
            st.metric("Trend", latest_vni['trend'])

        with col3:
            st.metric("RSI", f"{latest_vni['rsi_14']:.2f}")

        with col4:
            st.metric("MACD", f"{latest_vni['macd']:.2f}")

        with col5:
            st.metric("ADX", f"{latest_vni['adx_14']:.2f}")

        # Chart
        st.subheader("VN-Index Price Chart (Last 6 Months)")

        vni_6m = vnindex_df.tail(120)

        fig = go.Figure()

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=vni_6m['date'],
            open=vni_6m['open'],
            high=vni_6m['high'],
            low=vni_6m['low'],
            close=vni_6m['close'],
            name='VN-Index'
        ))

        # Moving averages
        fig.add_trace(go.Scatter(
            x=vni_6m['date'],
            y=vni_6m['sma_20'],
            name='SMA20',
            line=dict(color='blue', width=1)
        ))

        fig.add_trace(go.Scatter(
            x=vni_6m['date'],
            y=vni_6m['sma_50'],
            name='SMA50',
            line=dict(color='green', width=1)
        ))

        fig.add_trace(go.Scatter(
            x=vni_6m['date'],
            y=vni_6m['sma_200'],
            name='SMA200',
            line=dict(color='red', width=1)
        ))

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price",
            hovermode='x unified',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # Indicators
        col1, col2 = st.columns(2)

        with col1:
            # RSI
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(
                x=vni_6m['date'],
                y=vni_6m['rsi_14'],
                name='RSI',
                line=dict(color='purple')
            ))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            fig_rsi.update_layout(title="RSI", height=300)
            st.plotly_chart(fig_rsi, use_container_width=True)

        with col2:
            # MACD
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(
                x=vni_6m['date'],
                y=vni_6m['macd'],
                name='MACD',
                line=dict(color='blue')
            ))
            fig_macd.add_trace(go.Scatter(
                x=vni_6m['date'],
                y=vni_6m['macd_signal'],
                name='Signal',
                line=dict(color='red')
            ))
            fig_macd.add_bar(
                x=vni_6m['date'],
                y=vni_6m['macd_hist'],
                name='Histogram'
            )
            fig_macd.update_layout(title="MACD", height=300)
            st.plotly_chart(fig_macd, use_container_width=True)

# === TAB 7: Market Regime ===
with tab7:
    st.header("🌡️ Market Regime")

    regime_df = load_market_regime()
    if not regime_df.empty:
        latest_regime = regime_df[regime_df['date'] == latest_date].iloc[0]

        # Current regime
        st.subheader("Current Market Regime")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            regime_color = {
                'BUBBLE': '🔴',
                'EUPHORIA': '🟠',
                'NEUTRAL': '🟡',
                'FEAR': '🔵',
                'BOTTOM': '🟢'
            }.get(latest_regime['regime'], '⚪')

            st.metric(
                "Regime",
                f"{regime_color} {latest_regime['regime']}",
                delta=None
            )

        with col2:
            st.metric("Regime Score", f"{latest_regime['regime_score']:.2f}")

        with col3:
            st.metric("Risk Level", latest_regime['risk_level'])

        with col4:
            st.metric("Sentiment", latest_regime['market_sentiment'])

        # Component scores
        st.subheader("Component Scores")

        component_data = {
            'Component': ['Valuation', 'Breadth', 'Volume', 'Volatility', 'Momentum'],
            'Score': [
                latest_regime['valuation_score'],
                latest_regime['breadth_score'],
                latest_regime['volume_score'],
                latest_regime['volatility_score'],
                latest_regime['momentum_score']
            ]
        }

        fig = px.bar(
            component_data,
            x='Component',
            y='Score',
            title='Regime Component Breakdown',
            color='Score',
            color_continuous_scale=['red', 'yellow', 'green']
        )

        fig.add_hline(y=0, line_dash="dash", line_color="black")
        fig.update_layout(height=400)

        st.plotly_chart(fig, use_container_width=True)

        # Historical regime
        st.subheader("Regime History (Last 60 Days)")

        regime_60 = regime_df.tail(60)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=regime_60['date'],
            y=regime_60['regime_score'],
            name='Regime Score',
            line=dict(color='blue', width=2),
            fill='tozeroy'
        ))

        fig.add_hline(y=0, line_dash="dash", line_color="black")
        fig.add_hline(y=60, line_dash="dot", line_color="red", annotation_text="Bubble")
        fig.add_hline(y=-60, line_dash="dot", line_color="green", annotation_text="Bottom")

        fig.update_layout(
            title="Market Regime Score Trend",
            xaxis_title="Date",
            yaxis_title="Regime Score",
            hovermode='x unified',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Data table
        st.dataframe(
            regime_60[['date', 'regime', 'regime_score', 'risk_level', 'market_sentiment']].tail(20),
            use_container_width=True
        )

# Footer
st.markdown("---")
st.caption(f"Last updated: {latest_date} | Data source: VN-Index OHLCV")
