"""
Company Dashboard - Financial Statement Analysis
================================================
Professional dashboard for Vietnamese company fundamental analysis.

Features:
- Key Metrics Cards (Revenue, Profit, ROE, D/E)
- Interactive Charts Tab (Income Statement, Margins, ROE/ROA, Balance Sheet, Cash Flow)
- Financial Tables Tab (Income Statement, Balance Sheet, Cash Flow pivot tables)

Design: Midnight Terminal theme - unified with sector dashboard
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

from WEBAPP.services.company_service import CompanyService
from WEBAPP.components.tables.financial_tables import (
    render_income_statement_table,
    render_balance_sheet_table,
    render_cash_flow_table,
)
from WEBAPP.core.styles import (
    get_page_style, get_chart_layout,
    CHART_COLORS, BAR_COLORS,
    render_styled_table, get_table_style
)
from WEBAPP.core.session_state import init_page_state, render_persistent_tabs

# ============================================================================
# STYLES
# ============================================================================
# Note: st.set_page_config() is handled by main_app.py when using navigation

# Inject unified premium styles from core/styles.py
st.markdown(get_page_style(), unsafe_allow_html=True)
st.markdown(get_table_style(), unsafe_allow_html=True)

# Initialize session state for this page
init_page_state('company')

# ============================================================================
# HEADER
# ============================================================================
st.title("Company Analysis")
st.markdown("**Comprehensive fundamental analysis for Vietnamese equities**")
st.markdown("---")

# ============================================================================
# SIDEBAR - FILTERS
# ============================================================================
st.sidebar.markdown("## Filters")

try:
    service = CompanyService()
    available_tickers = service.get_available_tickers()

    if not available_tickers:
        st.error("No company data found. Please run the company calculator first.")
        st.stop()

except FileNotFoundError as e:
    st.error(f"Error: {e}")
    st.info("Run: `python3 PROCESSORS/fundamental/calculators/run_company_calculator.py`")
    st.stop()

# Ticker selector - check for Quick Search pre-selection
default_ticker = st.session_state.get('quick_search_ticker', None)
if default_ticker and default_ticker in available_tickers:
    default_index = available_tickers.index(default_ticker)
    # Clear the quick search after using it
    st.session_state['quick_search_ticker'] = None
else:
    default_index = 0 if available_tickers else None

ticker = st.sidebar.selectbox(
    "Select Company",
    options=available_tickers,
    index=default_index,
    help="Choose a company to analyze"
)

# Period selector
period = st.sidebar.selectbox(
    "Period",
    options=["Quarterly", "Yearly"],
    index=0,
    help="Select data frequency"
)

# Limit
limit = st.sidebar.slider(
    "Number of periods",
    min_value=4,
    max_value=20,
    value=12,
    help="How many periods to display"
)

if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def load_full_data(ticker, period):
    """Load full historical data for MA4 calculation (from 2018+)."""
    service = CompanyService()
    df = service.get_financial_data(ticker, period, limit=100)  # Get all available
    if not df.empty and 'report_date' in df.columns:
        df['report_date'] = pd.to_datetime(df['report_date'])
    return df

with st.spinner(f"Loading {ticker}..."):
    df_full = load_full_data(ticker, period)
    # Filter to display only requested periods, but keep df_full for MA4
    df = df_full.tail(limit).copy() if len(df_full) > limit else df_full.copy()

if df.empty:
    st.warning(f"No data available for {ticker}")
    st.stop()

# Add period labels
df['period_label'] = df.apply(
    lambda r: f"{int(r.get('quarter', 0))}Q{str(int(r['year']))[-2:]}" if period == 'Quarterly' else str(int(r['year'])),
    axis=1
)

# ============================================================================
# METRIC CARDS (4 KPIs)
# ============================================================================
latest = df.iloc[-1]
previous = df.iloc[-2] if len(df) > 1 else latest

latest_date = latest['report_date']
if period == 'Quarterly':
    quarter = latest.get('quarter', (latest_date.month - 1) // 3 + 1)
    date_str = f"{latest_date.year} Q{quarter}"
else:
    date_str = str(latest_date.year)

st.markdown(f"### {ticker} - {date_str}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    revenue = latest['net_revenue'] / 1e9 if latest['net_revenue'] else 0
    prev_rev = previous['net_revenue'] / 1e9 if previous['net_revenue'] else 0
    delta = ((revenue - prev_rev) / abs(prev_rev) * 100) if prev_rev != 0 else 0
    st.metric("Net Revenue", f"{revenue:,.0f}B", f"{delta:+.1f}%")

with col2:
    profit = latest['npatmi'] / 1e9 if latest['npatmi'] else 0
    prev_profit = previous['npatmi'] / 1e9 if previous['npatmi'] else 0
    delta = ((profit - prev_profit) / abs(prev_profit) * 100) if prev_profit != 0 else 0
    st.metric("Net Profit", f"{profit:,.0f}B", f"{delta:+.1f}%")

with col3:
    roe = latest.get('roe', 0) or 0
    prev_roe = previous.get('roe', 0) or 0
    delta = roe - prev_roe
    st.metric("ROE", f"{roe:.1f}%", f"{delta:+.1f}pp")

with col4:
    de = latest.get('debt_to_equity', 0) or 0
    prev_de = previous.get('debt_to_equity', 0) or 0
    delta = de - prev_de
    st.metric("D/E Ratio", f"{de:.2f}x", f"{delta:+.2f}x", delta_color="inverse")

st.markdown("---")

# ============================================================================
# MAIN TABS: Charts | Tables (Session State Persisted)
# ============================================================================
active_tab = render_persistent_tabs(["📈 Charts", "📋 Tables"], "company_active_tab")

# ============================================================================
# CHARTS TAB
# ============================================================================
if active_tab == 0:
    # Convert to billions for charts
    chart_df = df.copy()
    value_cols = ['net_revenue', 'gross_profit', 'ebit', 'ebitda', 'npatmi',
                  'total_assets', 'total_liabilities', 'total_equity',
                  'operating_cf', 'investment_cf', 'financing_cf', 'fcf', 'fcff', 'fcfe',
                  'sga', 'net_finance_income']
    for col in value_cols:
        if col in chart_df.columns:
            chart_df[col] = chart_df[col] / 1e9

    # Helper function for MA4 YoY Growth calculation using FULL historical data
    def compute_ma4_yoy_full(col_name: str) -> pd.Series:
        """
        Compute MA4 YoY Growth % based on TTM using FULL historical data.
        Then align to displayed quarters for continuous line from first bar.

        Logic:
        - TTM current = Sum of last 4 quarters
        - TTM previous = Sum of same 4 quarters from previous year (shift 4)
        - MA4 YoY = (TTM current / TTM previous - 1) * 100%
        """
        # Calculate on full data
        full_series = pd.to_numeric(df_full[col_name], errors='coerce')
        ttm_current = full_series.rolling(window=4, min_periods=4).sum()
        ttm_prev = ttm_current.shift(4)
        ma4_full = (ttm_current / ttm_prev - 1) * 100.0

        # Create mapping from period_label to MA4 value
        df_full['_temp_period'] = df_full.apply(
            lambda r: f"{int(r.get('quarter', 0))}Q{str(int(r['year']))[-2:]}" if period == 'Quarterly' else str(int(r['year'])),
            axis=1
        )
        ma4_map = dict(zip(df_full['_temp_period'], ma4_full))

        # Align to displayed quarters
        ma4_aligned = [ma4_map.get(q, None) for q in chart_df['period_label'].tolist()]
        ma4_display = pd.Series(ma4_aligned, dtype=float).interpolate(limit_direction='both')

        return ma4_display

    # ========================================================================
    # INCOME STATEMENT - 4 Bar Charts with MA4 YoY Lines
    # ========================================================================
    st.markdown("### Income Statement")

    income_items = [
        ("Revenue", "net_revenue", CHART_COLORS['secondary']),
        ("Gross Profit", "gross_profit", CHART_COLORS['positive']),
        ("EBITDA", "ebitda", CHART_COLORS['quaternary']),
        ("NPATMI", "npatmi", CHART_COLORS['tertiary']),
    ]

    # 2 charts per row
    for row_start in range(0, len(income_items), 2):
        cols = st.columns(2)
        for col_idx, item_idx in enumerate(range(row_start, min(row_start + 2, len(income_items)))):
            name, col, color = income_items[item_idx]
            with cols[col_idx]:
                if col in df.columns and df[col].notna().any():
                    fig = make_subplots(specs=[[{"secondary_y": True}]])

                    # Bar chart (primary y-axis) - values in Billions
                    fig.add_trace(
                        go.Bar(
                            x=chart_df['period_label'],
                            y=chart_df[col],
                            name=name,
                            marker_color=color,
                            hovertemplate=f"{name}: %{{y:,.1f}}B<extra></extra>"
                        ),
                        secondary_y=False
                    )

                    # MA4 YoY Growth % line (secondary y-axis) - calculated from FULL data
                    ma4_yoy = compute_ma4_yoy_full(col)
                    fig.add_trace(
                        go.Scatter(
                            x=chart_df['period_label'],
                            y=ma4_yoy,
                            name='MA4 YoY %',
                            mode='lines',
                            line=dict(color=CHART_COLORS['negative'], width=2, dash='dot'),
                            hovertemplate="MA4 YoY: %{y:,.1f}%<extra></extra>"
                        ),
                        secondary_y=True
                    )

                    layout = get_chart_layout(f"{name} (Billion VND)", height=280)
                    layout['showlegend'] = True
                    layout['legend'] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    fig.update_layout(**layout)
                    fig.update_yaxes(title_text="B VND", secondary_y=False)
                    fig.update_yaxes(title_text="YoY %", secondary_y=True, showgrid=False)

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"{name} data not available")

    # ========================================================================
    # PROFITABILITY MARGINS - 4 Bar Charts with MA4 Lines
    # ========================================================================
    st.markdown("---")
    st.markdown("### Profitability Margins")

    margin_items = [
        ("Gross Margin", "gross_profit_margin", CHART_COLORS['positive']),
        ("EBIT Margin", "ebit_margin", CHART_COLORS['secondary']),
        ("EBITDA Margin", "ebitda_margin", CHART_COLORS['quaternary']),
        ("Net Margin", "net_margin", CHART_COLORS['tertiary']),
    ]

    def compute_ma4_margin_full(col_name: str) -> pd.Series:
        """Compute simple 4-quarter moving average for margin metrics using FULL data."""
        full_series = pd.to_numeric(df_full[col_name], errors='coerce')
        ma4_full = full_series.rolling(window=4, min_periods=1).mean()

        # Map to displayed quarters
        ma4_map = dict(zip(df_full['_temp_period'], ma4_full))
        ma4_aligned = [ma4_map.get(q, None) for q in chart_df['period_label'].tolist()]
        ma4_display = pd.Series(ma4_aligned, dtype=float).interpolate(limit_direction='both')

        return ma4_display

    # 2 charts per row
    for row_start in range(0, len(margin_items), 2):
        cols = st.columns(2)
        for col_idx, item_idx in enumerate(range(row_start, min(row_start + 2, len(margin_items)))):
            name, col, color = margin_items[item_idx]
            with cols[col_idx]:
                if col in df.columns and df[col].notna().any():
                    fig = make_subplots(specs=[[{"secondary_y": True}]])

                    # Bar chart (primary y-axis) - margin in %
                    fig.add_trace(
                        go.Bar(
                            x=chart_df['period_label'],
                            y=df[col],
                            name=name,
                            marker_color=color,
                            hovertemplate=f"{name}: %{{y:,.1f}}%<extra></extra>"
                        ),
                        secondary_y=False
                    )

                    # MA4 line (same axis, just smoothed trend) - calculated from FULL data
                    ma4 = compute_ma4_margin_full(col)
                    fig.add_trace(
                        go.Scatter(
                            x=chart_df['period_label'],
                            y=ma4,
                            name='MA4',
                            mode='lines',
                            line=dict(color=CHART_COLORS['negative'], width=2, dash='dot'),
                            hovertemplate="MA4: %{y:,.1f}%<extra></extra>"
                        ),
                        secondary_y=False
                    )

                    layout = get_chart_layout(f"{name} (%)", height=280)
                    layout['showlegend'] = True
                    layout['legend'] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    fig.update_layout(**layout)
                    fig.update_yaxes(title_text="%", secondary_y=False)

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"{name} data not available")

    # Row 2: ROE/ROA + Balance Sheet
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ROE / ROA Trend")
        if 'roe' in chart_df.columns and 'roa' in chart_df.columns:
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            fig.add_trace(go.Scatter(
                x=chart_df['period_label'], y=chart_df['roe'],
                name='ROE', mode='lines+markers',
                line=dict(color=CHART_COLORS['secondary'], width=3),
                marker=dict(size=8),
                fill='tozeroy', fillcolor='rgba(41,92,169,0.15)'
            ), secondary_y=False)

            fig.add_trace(go.Scatter(
                x=chart_df['period_label'], y=chart_df['roa'],
                name='ROA', mode='lines+markers',
                line=dict(color=CHART_COLORS['primary'], width=2, dash='dot'),
                marker=dict(size=6, symbol='diamond')
            ), secondary_y=True)

            layout = get_chart_layout(height=380)
            layout['legend'] = dict(orientation="h", y=-0.15, x=0.5, xanchor='center', font=dict(color='#FFFFFF'))
            fig.update_layout(**layout)
            fig.update_yaxes(
                title_text="ROE (%)", secondary_y=False,
                gridcolor='rgba(160, 174, 192, 0.08)',
                title_font=dict(color=CHART_COLORS['secondary'])
            )
            fig.update_yaxes(
                title_text="ROA (%)", secondary_y=True,
                gridcolor='rgba(160, 174, 192, 0.08)',
                title_font=dict(color=CHART_COLORS['primary'])
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ROE/ROA data not available")

    with col2:
        st.markdown("#### Balance Sheet Structure")
        if all(col in chart_df.columns for col in ['total_assets', 'total_liabilities', 'total_equity']):
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=chart_df['period_label'], y=chart_df['total_liabilities'],
                name='Liabilities', marker_color=CHART_COLORS['tertiary'], opacity=0.9
            ))
            fig.add_trace(go.Bar(
                x=chart_df['period_label'], y=chart_df['total_equity'],
                name='Equity', marker_color=CHART_COLORS['primary'], opacity=0.9
            ))

            layout = get_chart_layout(height=380)
            layout['barmode'] = 'stack'
            layout['legend'] = dict(orientation="h", y=-0.15, x=0.5, xanchor='center', font=dict(color='#FFFFFF'))
            layout['yaxis']['title'] = "Billion VND"
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Balance sheet data not available")

    # Row 3: Cash Flow Analysis with FCF + FCFE
    st.markdown("#### Cash Flow Analysis")
    if all(col in chart_df.columns for col in ['operating_cf', 'investment_cf', 'financing_cf']):
        fig = go.Figure()

        # Bar traces for CF components
        fig.add_trace(go.Bar(
            x=chart_df['period_label'], y=chart_df['operating_cf'],
            name='Operating CF', marker_color=CHART_COLORS['positive']
        ))
        fig.add_trace(go.Bar(
            x=chart_df['period_label'], y=chart_df['investment_cf'],
            name='Investment CF', marker_color=CHART_COLORS['negative']
        ))
        fig.add_trace(go.Bar(
            x=chart_df['period_label'], y=chart_df['financing_cf'],
            name='Financing CF', marker_color=BAR_COLORS[4]  # Blue Light
        ))

        # FCF line
        if 'fcf' in chart_df.columns:
            fig.add_trace(go.Scatter(
                x=chart_df['period_label'], y=chart_df['fcf'],
                name='FCF', mode='lines+markers',
                line=dict(color=CHART_COLORS['secondary'], width=3),
                marker=dict(size=8, symbol='circle')
            ))

        # FCFF line (dotted)
        if 'fcff' in chart_df.columns:
            fig.add_trace(go.Scatter(
                x=chart_df['period_label'], y=chart_df['fcff'],
                name='FCFF', mode='lines+markers',
                line=dict(color='#00D4AA', width=2, dash='dot'),
                marker=dict(size=6, symbol='square')
            ))

        # FCFE line (dashed)
        if 'fcfe' in chart_df.columns:
            fig.add_trace(go.Scatter(
                x=chart_df['period_label'], y=chart_df['fcfe'],
                name='FCFE', mode='lines+markers',
                line=dict(color=CHART_COLORS['tertiary'], width=2, dash='dash'),
                marker=dict(size=6, symbol='diamond')
            ))

        layout = get_chart_layout(height=400)
        layout['barmode'] = 'group'
        layout['legend'] = dict(orientation="h", y=-0.12, x=0.5, xanchor='center', font=dict(color='#FFFFFF'))
        layout['yaxis']['title'] = "Billion VND"
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cash flow data not available")

    # Row 4: Investment Ratios (if available)
    if 'depreciation_rate' in chart_df.columns and 'cip_rate' in chart_df.columns:
        st.markdown("#### Investment Ratios")
        col1, col2 = st.columns(2)

        with col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=chart_df['period_label'], y=chart_df['depreciation_rate'],
                name='Depreciation Rate', mode='lines+markers+text',
                line=dict(color=CHART_COLORS['tertiary'], width=2),
                marker=dict(size=8),
                text=[f"{v:.1f}%" if pd.notna(v) else "" for v in chart_df['depreciation_rate']],
                textposition='top center',
                textfont=dict(size=10, color='#94A3B8')
            ))
            layout = get_chart_layout(height=300)
            layout['yaxis']['title'] = "Depreciation Rate (%)"
            layout['showlegend'] = False
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("📊 Tỷ lệ khấu hao tích lũy / Nguyên giá TSCĐ")

        with col2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=chart_df['period_label'], y=chart_df['cip_rate'],
                name='CIP Rate', mode='lines+markers+text',
                line=dict(color=CHART_COLORS['quaternary'], width=2),
                marker=dict(size=8),
                text=[f"{v:.2f}%" if pd.notna(v) else "" for v in chart_df['cip_rate']],
                textposition='top center',
                textfont=dict(size=10, color='#94A3B8')
            ))
            layout = get_chart_layout(height=300)
            layout['yaxis']['title'] = "CIP Rate (%)"
            layout['showlegend'] = False
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("📊 Tỷ lệ XDCB dở dang / Tổng tài sản")

# ============================================================================
# TABLES TAB
# ============================================================================
elif active_tab == 1:
    # Nested tabs for financial statement tables (Session State Persisted)
    tables_tab = render_persistent_tabs(
        ["Income Statement", "Balance Sheet", "Cash Flow"],
        "company_tables_tab",
        style="secondary"
    )

    if tables_tab == 0:
        render_income_statement_table(df, period)
    elif tables_tab == 1:
        render_balance_sheet_table(df, period)
    elif tables_tab == 2:
        render_cash_flow_table(df, period)

    # Export Section
    st.markdown("---")
    st.markdown("### Export Data")
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Full Dataset (CSV)",
        data=csv_data,
        file_name=f"{ticker}_financial_data.csv",
        mime="text/csv",
        use_container_width=True
    )

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption(f"💾 Data: `DATA/processed/fundamental/company/` | 📊 {ticker} | 📝 {len(df)} records")
