"""
Security (Brokerage) Dashboard - Financial Statement Analysis
=============================================================
Professional dashboard for Vietnamese securities/brokerage analysis.

Features:
- Key Metrics Cards (Revenue, Profit, ROAE, Leverage)
- Interactive Charts Tab (Revenue Mix, Portfolio, ROE/ROA, Margin Lending)
- Financial Tables Tab (Income Statement, Key Metrics)

Design: Midnight Terminal theme - unified with company dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from WEBAPP.services.security_service import SecurityService
from WEBAPP.core.styles import (
    get_page_style, get_chart_layout,
    CHART_COLORS, BAR_COLORS,
    render_styled_table, get_table_style
)
from WEBAPP.core.session_state import init_page_state, render_persistent_tabs
from WEBAPP.components.filters.fundamental_filter_bar import render_fundamental_filters

# ============================================================================
# PAGE CONFIG & STYLES
# ============================================================================
# Note: st.set_page_config is handled by main_app.py

# Inject unified premium styles from core/styles.py
st.markdown(get_page_style(), unsafe_allow_html=True)
st.markdown(get_table_style(), unsafe_allow_html=True)

# Initialize session state for this page
init_page_state('security')

# ============================================================================
# HEADER
# ============================================================================
st.title("Securities/Brokerage Analysis")
st.markdown("**Comprehensive analysis for Vietnamese brokerage companies**")

# ============================================================================
# INITIALIZE SERVICE & HEADER FILTERS
# ============================================================================
try:
    service = SecurityService()
    available_tickers = service.get_available_tickers()

    if not available_tickers:
        st.error("No security data found. Please run the security calculator first.")
        st.stop()

except FileNotFoundError as e:
    st.error(f"Error: {e}")
    st.info("Run: `python3 PROCESSORS/fundamental/calculators/run_security_calculator.py`")
    st.stop()

# Header filter bar (replaces sidebar filters)
filters = render_fundamental_filters(
    service=service,
    entity_type='security',
    mode='basic'
)
ticker = filters['ticker']
period = filters['period']
limit = filters['num_periods']

st.markdown("---")

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data(ttl=3600)
def load_security_data(ticker: str, period: str, limit: int):
    """Load security financial data."""
    service = SecurityService()
    df = service.get_financial_data(ticker, period, limit=limit)
    if not df.empty and 'report_date' in df.columns:
        df['report_date'] = pd.to_datetime(df['report_date'])
    return df

df = load_security_data(ticker, period, limit)

if df.empty:
    st.warning(f"No data available for {ticker}")
    st.stop()

# Prepare period labels
df = df.sort_values('report_date', ascending=True)
df['period_label'] = df.apply(
    lambda r: f"{int(r['quarter'])}Q{str(int(r['year']))[-2:]}" if period == 'Quarterly' else str(int(r['year'])),
    axis=1
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def format_value(value, format_type='number'):
    """Format values for display."""
    if pd.isna(value) or value is None:
        return "-"
    if format_type == 'billions':
        return f"{value/1e9:,.1f}B"
    elif format_type == 'percent':
        return f"{value:.2f}%"
    elif format_type == 'ratio':
        return f"{value:.2f}x"
    else:
        return f"{value:,.1f}"

def safe_delta(current, previous):
    """Calculate safe delta percentage."""
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return None
    return ((current - previous) / abs(previous)) * 100

# ============================================================================
# METRIC CARDS
# ============================================================================
st.subheader("Key Brokerage Metrics")

latest = df.iloc[-1]
previous = df.iloc[-2] if len(df) > 1 else latest

col1, col2, col3, col4 = st.columns(4)

with col1:
    rev = latest.get('total_revenue', np.nan)
    rev_prev = previous.get('total_revenue', np.nan)
    delta = safe_delta(rev, rev_prev)
    st.metric(
        "Total Revenue",
        format_value(rev, 'billions') if pd.notna(rev) else "-",
        f"{delta:+.1f}%" if delta else None
    )

with col2:
    profit = latest.get('net_profit', np.nan)
    profit_prev = previous.get('net_profit', np.nan)
    delta = safe_delta(profit, profit_prev)
    st.metric(
        "Net Profit",
        format_value(profit, 'billions') if pd.notna(profit) else "-",
        f"{delta:+.1f}%" if delta else None
    )

with col3:
    roae = latest.get('roae_ttm', np.nan)
    roae_prev = previous.get('roae_ttm', np.nan)
    delta_pts = (roae - roae_prev) if pd.notna(roae) and pd.notna(roae_prev) else None
    st.metric(
        "ROAE (TTM)",
        format_value(roae, 'percent') if pd.notna(roae) else "-",
        f"{delta_pts:+.2f} pts" if delta_pts else None
    )

with col4:
    lev = latest.get('leverage', np.nan)
    lev_prev = previous.get('leverage', np.nan)
    delta = (lev - lev_prev) if pd.notna(lev) and pd.notna(lev_prev) else None
    st.metric(
        "Leverage",
        format_value(lev, 'ratio') if pd.notna(lev) else "-",
        f"{delta:+.2f}x" if delta else None
    )

st.markdown("---")

# ============================================================================
# TABS (Session State Persisted)
# ============================================================================
active_tab = render_persistent_tabs(["Charts", "Tables"], "security_active_tab")

# ============================================================================
# TAB 1: CHARTS
# ============================================================================
if active_tab == 0:
    # Row 1: Revenue Mix & Profitability
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Revenue Mix")
        rev_cols = ['income_fvtpl', 'income_htm', 'income_afs', 'income_loans', 'brokerage_fee']
        available = [c for c in rev_cols if c in df.columns and df[c].notna().any()]
        if available:
            fig = go.Figure()
            colors = [CHART_COLORS['primary'], CHART_COLORS['secondary'], CHART_COLORS['warning'],
                     CHART_COLORS['danger'], CHART_COLORS['success']]
            names = ['FVTPL', 'HTM', 'AFS', 'Margin Lending', 'Brokerage']
            for i, col in enumerate(available):
                fig.add_trace(go.Bar(
                    x=df['period_label'],
                    y=df[col] / 1e9 if df[col].abs().max() > 1e6 else df[col],
                    name=names[i] if i < len(names) else col.replace('income_', '').upper(),
                    marker_color=colors[i % len(colors)]
                ))
            fig.update_layout(
                **get_chart_layout("Revenue Mix (Billion VND)"),
                barmode='stack',
                yaxis_title="Billion VND"
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Revenue breakdown data not available")

    with col2:
        st.markdown("### ROAE & ROAA")
        if 'roae_ttm' in df.columns or 'roaa_ttm' in df.columns:
            fig = go.Figure()
            if 'roae_ttm' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['period_label'], y=df['roae_ttm'],
                    name='ROAE', mode='lines+markers',
                    line=dict(color=CHART_COLORS['primary'], width=2)
                ))
            if 'roaa_ttm' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['period_label'], y=df['roaa_ttm'],
                    name='ROAA', mode='lines+markers',
                    line=dict(color=CHART_COLORS['secondary'], width=2)
                ))
            fig.update_layout(
                **get_chart_layout("Return Metrics (TTM %)"),
                yaxis_title="%"
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("ROE/ROA data not available")

    # Row 2: Portfolio & Margins
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Portfolio Composition (Latest)")
        portfolio_cols = ['fvtpl', 'htm', 'afs', 'margin_loans']
        available = [c for c in portfolio_cols if c in df.columns and pd.notna(latest.get(c))]
        if available:
            values = [latest[c] / 1e9 for c in available]  # Convert to billions
            labels = ['FVTPL', 'HTM', 'AFS', 'Margin Loans'][:len(available)]
            colors = [CHART_COLORS['primary'], CHART_COLORS['secondary'],
                     CHART_COLORS['warning'], CHART_COLORS['success']]

            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                marker_colors=colors[:len(available)],
                hole=0.4,
                textinfo='percent+label'
            )])
            fig.update_layout(
                **get_chart_layout("Portfolio Allocation"),
                showlegend=True
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Portfolio data not available")

    with col2:
        st.markdown("### Profit Margins")
        margin_cols = ['gross_profit_margin', 'profit_margin']
        available = [c for c in margin_cols if c in df.columns]
        if available:
            fig = go.Figure()
            colors = [CHART_COLORS['primary'], CHART_COLORS['secondary']]
            names = ['Gross Margin', 'Net Margin']
            for i, col in enumerate(available):
                fig.add_trace(go.Scatter(
                    x=df['period_label'], y=df[col],
                    name=names[i] if i < len(names) else col,
                    mode='lines+markers',
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
            fig.update_layout(
                **get_chart_layout("Profit Margins (%)"),
                yaxis_title="%"
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Margin data not available")

    # Row 3: CIR & Leverage
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Cost-to-Income Ratio")
        if 'cir' in df.columns:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['period_label'], y=df['cir'],
                name='CIR',
                marker_color=CHART_COLORS['primary']
            ))
            fig.add_hline(y=50, line_dash="dash", line_color=CHART_COLORS['warning'],
                          annotation_text="Target 50%")
            fig.update_layout(
                **get_chart_layout("Cost-to-Income Ratio (%)"),
                yaxis_title="%"
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("CIR data not available")

    with col2:
        st.markdown("### Leverage Trend")
        if 'leverage' in df.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['period_label'], y=df['leverage'],
                name='Leverage',
                mode='lines+markers',
                fill='tozeroy',
                line=dict(color=CHART_COLORS['warning'], width=2)
            ))
            fig.update_layout(
                **get_chart_layout("Leverage Ratio"),
                yaxis_title="x"
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Leverage data not available")

# ============================================================================
# TAB 2: TABLES
# ============================================================================
elif active_tab == 1:
    # Income Statement Table
    st.markdown("### Income Statement")
    income_metrics = {
        'Total Revenue': 'total_revenue',
        'Brokerage Fee': 'brokerage_fee',
        'Investment Revenue': 'investment_revenue',
        'Gross Profit': 'gross_profit',
        'Operating Expense': 'opex',
        'Net Profit': 'net_profit'
    }

    table_data = []
    for display_name, col_name in income_metrics.items():
        if col_name in df.columns:
            row = {'METRIC': display_name}
            for _, r in df.iterrows():
                period_key = r['period_label']
                val = r.get(col_name, np.nan)
                row[period_key] = format_value(val, 'billions') if pd.notna(val) else "-"
            table_data.append(row)

    if table_data:
        income_df = pd.DataFrame(table_data)
        html_table = render_styled_table(income_df, highlight_first_col=True)
        st.markdown(html_table, unsafe_allow_html=True)

    st.markdown("---")

    # Balance Sheet Summary
    st.markdown("### Balance Sheet Summary")
    bs_metrics = {
        'Total Assets': 'total_assets',
        'FVTPL Portfolio': 'fvtpl',
        'HTM Portfolio': 'htm',
        'AFS Portfolio': 'afs',
        'Margin Loans': 'margin_loans',
        'Total Equity': 'total_equity'
    }

    table_data = []
    for display_name, col_name in bs_metrics.items():
        if col_name in df.columns:
            row = {'METRIC': display_name}
            for _, r in df.iterrows():
                period_key = r['period_label']
                val = r.get(col_name, np.nan)
                row[period_key] = format_value(val, 'billions') if pd.notna(val) else "-"
            table_data.append(row)

    if table_data:
        bs_df = pd.DataFrame(table_data)
        html_table = render_styled_table(bs_df, highlight_first_col=True)
        st.markdown(html_table, unsafe_allow_html=True)

    st.markdown("---")

    # Key Metrics Table
    st.markdown("### Key Financial Ratios")
    key_metrics = {
        'Gross Margin': ('gross_profit_margin', 'percent'),
        'Net Margin': ('profit_margin', 'percent'),
        'ROAE (TTM)': ('roae_ttm', 'percent'),
        'ROAA (TTM)': ('roaa_ttm', 'percent'),
        'Leverage': ('leverage', 'ratio'),
        'CIR': ('cir', 'percent')
    }

    table_data = []
    for display_name, (col_name, fmt) in key_metrics.items():
        if col_name in df.columns:
            row = {'METRIC': display_name}
            for _, r in df.iterrows():
                period_key = r['period_label']
                val = r.get(col_name, np.nan)
                row[period_key] = format_value(val, fmt) if pd.notna(val) else "-"
            table_data.append(row)

    if table_data:
        metrics_df = pd.DataFrame(table_data)
        html_table = render_styled_table(metrics_df, highlight_first_col=True)
        st.markdown(html_table, unsafe_allow_html=True)

    # Download button
    st.markdown("---")
    st.download_button(
        "Download Data (CSV)",
        df.to_csv(index=False).encode('utf-8'),
        f"{ticker}_security_data.csv",
        "text/csv",
        width='stretch'
    )

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption(f"Data: Securities Financial Metrics | Ticker: **{ticker}** | Records: {len(df)} | Last updated: {df['report_date'].max().strftime('%Y-%m-%d') if not df.empty else 'N/A'}")
