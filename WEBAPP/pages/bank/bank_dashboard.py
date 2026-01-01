"""
Bank Dashboard - Financial Statement Analysis
==============================================
Professional dashboard for Vietnamese banking sector analysis.

Features:
- Key Banking Metrics Cards (NII, NIM, ROAE, NPL)
- Selectable Charts (8-10 metrics, bar chart style)
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

from WEBAPP.services.bank_service import BankService
from WEBAPP.core.styles import (
    get_page_style, get_chart_layout,
    CHART_COLORS, BAR_COLORS,
    render_styled_table, get_table_style
)
from WEBAPP.core.session_state import init_page_state, render_persistent_tabs

# ============================================================================
# PAGE CONFIG & STYLES
# ============================================================================
# Note: st.set_page_config is handled by main_app.py

# Inject unified premium styles from core/styles.py
st.markdown(get_page_style(), unsafe_allow_html=True)
st.markdown(get_table_style(), unsafe_allow_html=True)

# Initialize session state for this page
init_page_state('bank')

# ============================================================================
# METRIC DEFINITIONS (for selectable charts)
# ============================================================================
AVAILABLE_METRICS = {
    # Key Performance
    "NIM": {"col": "nim_q", "unit": "%", "description": "Net Interest Margin"},
    "CIR": {"col": "cir", "unit": "%", "description": "Cost-to-Income Ratio"},
    "NPL": {"col": "npl_ratio", "unit": "%", "description": "Non-Performing Loan Ratio"},
    "ROE": {"col": "roea_ttm", "unit": "%", "description": "Return on Equity (TTM)"},
    "ROA": {"col": "roaa_ttm", "unit": "%", "description": "Return on Assets (TTM)"},
    "LLCR": {"col": "llcr", "unit": "%", "description": "Loan Loss Coverage Ratio"},
    "Provision/Loan": {"col": "provision_to_loan", "unit": "%", "description": "Provision to Loan"},
    # Growth
    "Credit Growth": {"col": "credit_growth_ytd", "unit": "%", "description": "Credit Growth YTD"},
    "Deposit Growth": {"col": "customer_deposit_growth_ytd", "unit": "%", "description": "Deposit Growth YTD"},
    "Loan Growth": {"col": "loan_growth_ytd", "unit": "%", "description": "Loan Growth YTD"},
    "NII Growth": {"col": "nii_growth_yoy", "unit": "%", "description": "NII Growth YoY"},
    "NPATMI Growth": {"col": "npatmi_growth_yoy", "unit": "%", "description": "Profit Growth YoY"},
    # Other
    "CASA": {"col": "casa_ratio", "unit": "%", "description": "CASA Ratio"},
    "LDR": {"col": "ldr_pure", "unit": "%", "description": "Loan-to-Deposit Ratio"},
    "Asset Yield": {"col": "asset_yield_q", "unit": "%", "description": "Asset Yield"},
    "Funding Cost": {"col": "funding_cost_q", "unit": "%", "description": "Funding Cost"},
    "Group 2": {"col": "debt_group2_ratio", "unit": "%", "description": "Group 2 Debt Ratio"},
    "Credit Cost": {"col": "credit_cost", "unit": "%", "description": "Credit Cost"},
}

DEFAULT_METRICS = ["NIM", "CIR", "NPL", "ROE", "ROA", "LLCR", "Provision/Loan", "Credit Growth", "Deposit Growth", "Loan Growth", "NII Growth", "NPATMI Growth"]

# ============================================================================
# HEADER
# ============================================================================
st.title("Bank Analysis")
st.markdown("**Comprehensive analysis for Vietnamese banking sector**")
st.markdown("---")

# ============================================================================
# SIDEBAR - FILTERS
# ============================================================================
st.sidebar.markdown("## Filters")

try:
    service = BankService()
    available_tickers = service.get_available_tickers()

    if not available_tickers:
        st.error("No bank data found. Please run the bank calculator first.")
        st.stop()

except FileNotFoundError as e:
    st.error(f"Error: {e}")
    st.info("Run: `python3 PROCESSORS/fundamental/calculators/run_bank_calculator.py`")
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
    "Select Bank",
    options=available_tickers,
    index=default_index,
    help="Choose a bank to analyze"
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

st.sidebar.markdown("---")

# Refresh button
if st.sidebar.button("🔄 Refresh Data", width='stretch'):
    st.cache_data.clear()
    st.rerun()

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data(ttl=3600)
def load_bank_data_full(ticker: str, period: str):
    """Load FULL bank financial data for MA4 calculation (from 2018+)."""
    service = BankService()
    df = service.get_financial_data(ticker, period, limit=100)  # Get all available
    if not df.empty and 'report_date' in df.columns:
        df['report_date'] = pd.to_datetime(df['report_date'])
    return df

df_full = load_bank_data_full(ticker, period)

if df_full.empty:
    st.warning(f"No data available for {ticker}")
    st.stop()

# Filter to display only requested periods, but keep df_full for MA4
df_full = df_full.sort_values('report_date', ascending=True)
df = df_full.tail(limit).copy() if len(df_full) > limit else df_full.copy()

# Prepare period labels (short format for better chart display)
df['period_label'] = df.apply(
    lambda r: f"{int(r['quarter'])}Q{str(int(r['year']))[-2:]}" if period == 'Quarterly' else str(int(r['year'])),
    axis=1
)
df_full['period_label'] = df_full.apply(
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

LINE_CHART_METRICS = ["NIM", "ROE", "ROA", "CIR", "Credit Growth", "Deposit Growth", "Loan Growth", "NII Growth", "NPATMI Growth"]

def create_metric_chart(data, metric_name, metric_info):
    """Create a chart for a single metric - line or bar based on metric type."""
    col_name = metric_info['col']
    unit = metric_info['unit']

    if col_name not in data.columns or data[col_name].isna().all():
        return None

    fig = go.Figure()

    # Use line chart for trend metrics, bar for others
    use_line = metric_name in LINE_CHART_METRICS

    # Determine color based on metric type
    if 'NPL' in metric_name or 'Cost' in metric_name or 'Group 2' in metric_name:
        chart_color = CHART_COLORS['negative']
    elif 'Growth' in metric_name or 'ROE' in metric_name or 'ROA' in metric_name:
        chart_color = CHART_COLORS['positive']
    else:
        chart_color = CHART_COLORS['primary']

    if use_line:
        fig.add_trace(go.Scatter(
            x=data['period_label'],
            y=data[col_name],
            name=metric_name,
            mode='lines+markers',
            line=dict(color=chart_color, width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor=f'rgba({int(chart_color[1:3], 16)}, {int(chart_color[3:5], 16)}, {int(chart_color[5:7], 16)}, 0.1)',
            hovertemplate=f"{metric_name}: %{{y:.2f}}{unit}<extra></extra>"
        ))
    else:
        fig.add_trace(go.Bar(
            x=data['period_label'],
            y=data[col_name],
            name=metric_name,
            marker_color=chart_color,
            hovertemplate=f"{metric_name}: %{{y:.2f}}{unit}<extra></extra>"
        ))

    # Add reference lines for certain metrics
    if metric_name == "CIR":
        fig.add_hline(y=40, line_dash="dash", line_color=CHART_COLORS['tertiary'],
                      annotation_text="Target 40%", annotation_position="right")
    elif metric_name == "NPL":
        fig.add_hline(y=3, line_dash="dash", line_color=CHART_COLORS['tertiary'],
                      annotation_text="Warning 3%", annotation_position="right")
    elif metric_name == "LLCR":
        fig.add_hline(y=100, line_dash="dash", line_color=CHART_COLORS['tertiary'],
                      annotation_text="Min 100%", annotation_position="right")
    elif metric_name == "LDR":
        fig.add_hline(y=85, line_dash="dash", line_color=CHART_COLORS['negative'],
                      annotation_text="SBV Limit 85%", annotation_position="right")
    elif 'Growth' in metric_name:
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        **get_chart_layout(f"{metric_name} ({unit})", height=300),
        yaxis_title=unit,
        showlegend=False
    )

    return fig

# ============================================================================
# METRIC CARDS
# ============================================================================
st.subheader("Key Banking Metrics")

latest = df.iloc[-1]
previous = df.iloc[-2] if len(df) > 1 else latest

col1, col2, col3, col4 = st.columns(4)

with col1:
    nii = latest.get('nii', np.nan)
    nii_prev = previous.get('nii', np.nan)
    delta = safe_delta(nii, nii_prev)
    st.metric(
        "Net Interest Income",
        format_value(nii, 'billions') if pd.notna(nii) else "-",
        f"{delta:+.1f}%" if delta else None
    )

with col2:
    nim = latest.get('nim_q', np.nan)
    nim_prev = previous.get('nim_q', np.nan)
    delta_pts = (nim - nim_prev) if pd.notna(nim) and pd.notna(nim_prev) else None
    st.metric(
        "NIM (Quarterly)",
        format_value(nim, 'percent') if pd.notna(nim) else "-",
        f"{delta_pts:+.2f} pts" if delta_pts else None
    )

with col3:
    roae = latest.get('roea_ttm', np.nan)
    roae_prev = previous.get('roea_ttm', np.nan)
    delta_pts = (roae - roae_prev) if pd.notna(roae) and pd.notna(roae_prev) else None
    st.metric(
        "ROAE (TTM)",
        format_value(roae, 'percent') if pd.notna(roae) else "-",
        f"{delta_pts:+.2f} pts" if delta_pts else None
    )

with col4:
    npl = latest.get('npl_ratio', np.nan)
    npl_prev = previous.get('npl_ratio', np.nan)
    delta_pts = (npl - npl_prev) if pd.notna(npl) and pd.notna(npl_prev) else None
    st.metric(
        "NPL Ratio",
        format_value(npl, 'percent') if pd.notna(npl) else "-",
        f"{delta_pts:+.2f} pts" if delta_pts else None,
        delta_color="inverse"  # Lower is better
    )

st.markdown("---")

# ============================================================================
# METRIC SELECTOR (Horizontal in main page)
# ============================================================================
st.markdown("### 📊 Select Metrics")
st.markdown(
    """<style>
    .stMultiSelect [data-baseweb="tag"] {
        font-size: 0.75rem !important;
        padding: 2px 6px !important;
        height: 24px !important;
    }
    .stMultiSelect [data-baseweb="select"] > div {
        font-size: 0.8rem !important;
    }
    </style>""", unsafe_allow_html=True
)

# Horizontal multiselect with smaller font
selected_metrics = st.multiselect(
    "Choose metrics to display (max 12 recommended)",
    options=list(AVAILABLE_METRICS.keys()),
    default=DEFAULT_METRICS,
    help="Select metrics to show as charts",
    label_visibility="collapsed"
)

# Quick select buttons in horizontal layout
quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
with quick_col1:
    if st.button("🎯 Key Performance", width='stretch'):
        st.session_state['selected_metrics'] = ["NIM", "CIR", "NPL", "ROE", "ROA", "LLCR", "Provision/Loan"]
        st.rerun()
with quick_col2:
    if st.button("📈 Growth Focus", width='stretch'):
        st.session_state['selected_metrics'] = ["Credit Growth", "Deposit Growth", "Loan Growth", "NII Growth", "NPATMI Growth", "ROE", "NIM", "NPL"]
        st.rerun()
with quick_col3:
    if st.button("💰 All Metrics", width='stretch'):
        st.session_state['selected_metrics'] = list(AVAILABLE_METRICS.keys())
        st.rerun()
with quick_col4:
    if st.button("🔄 Reset Default", width='stretch'):
        st.session_state['selected_metrics'] = DEFAULT_METRICS
        st.rerun()

st.markdown("---")

# ============================================================================
# TABS (Session State Persisted)
# ============================================================================
active_tab = render_persistent_tabs(["📊 Charts", "📋 Tables"], "bank_active_tab")

# ============================================================================
# TAB 1: CHARTS - Dynamic based on selection
# ============================================================================
if active_tab == 0:
    if not selected_metrics:
        st.warning("Please select at least one metric from the sidebar.")
    else:
        st.markdown(f"### Selected Metrics ({len(selected_metrics)} charts)")

        # Calculate grid layout - 2 charts per row
        num_charts = len(selected_metrics)
        cols_per_row = 2

        # Generate charts in grid
        chart_idx = 0
        while chart_idx < num_charts:
            cols = st.columns(cols_per_row)

            for col_idx in range(cols_per_row):
                if chart_idx >= num_charts:
                    break

                metric_name = selected_metrics[chart_idx]
                metric_info = AVAILABLE_METRICS[metric_name]

                with cols[col_idx]:
                    fig = create_metric_chart(df, metric_name, metric_info)
                    if fig:
                        st.plotly_chart(fig, width='stretch')
                    else:
                        st.info(f"{metric_name} data not available")

                chart_idx += 1

    # Income Statement Charts - Separate bar charts with MA4 YoY Growth trend
    st.markdown("---")
    st.markdown("### Income Statement")

    income_items = [
        ("NII", "nii", CHART_COLORS['primary']),
        ("TOI", "toi", CHART_COLORS['secondary']),
        ("PPOP", "ppop", CHART_COLORS['tertiary']),
        ("PBT", "pbt", CHART_COLORS['quaternary']),
        ("NPATMI", "npatmi", CHART_COLORS['positive']),
    ]

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
        ma4_map = dict(zip(df_full['period_label'], ma4_full))

        # Align to displayed quarters
        ma4_aligned = [ma4_map.get(q, None) for q in df['period_label'].tolist()]
        ma4_display = pd.Series(ma4_aligned, dtype=float).interpolate(limit_direction='both')

        return ma4_display

    # 2 charts per row
    chart_idx = 0
    while chart_idx < len(income_items):
        cols = st.columns(2)
        for col_idx in range(2):
            if chart_idx >= len(income_items):
                break

            name, col, color = income_items[chart_idx]
            with cols[col_idx]:
                if col in df.columns and df[col].notna().any():
                    fig = make_subplots(specs=[[{"secondary_y": True}]])

                    # Bar chart (primary y-axis) - values in Billions
                    fig.add_trace(
                        go.Bar(
                            x=df['period_label'],
                            y=df[col] / 1e9,
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
                            x=df['period_label'],
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

                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info(f"{name} data not available")

            chart_idx += 1

# ============================================================================
# TAB 2: TABLES
# ============================================================================
elif active_tab == 1:
    # Sub-tabs for organized tables (Session State Persisted)
    tables_tab = render_persistent_tabs(
        ["📊 Size", "💰 Income", "📈 Growth", "🛡️ Quality", "⚙️ Efficiency"],
        "bank_tables_tab",
        style="secondary"
    )

    # === Size Table ===
    if tables_tab == 0:
        st.markdown("### Size Metrics")
        size_metrics = {
            'Total Assets': ('total_assets', 'billions'),
            'Total Credit': ('total_credit', 'billions'),
            'Total Loan': ('total_loan', 'billions'),
            'Total Corp Bond': ('total_corp_bond', 'billions'),
            'Total Customer Deposit': ('total_customer_deposit', 'billions'),
        }

        table_data = []
        for display_name, (col_name, fmt) in size_metrics.items():
            if col_name in df.columns:
                row = {'METRIC': display_name}
                for _, r in df.iterrows():
                    period_key = r['period_label']
                    val = r.get(col_name, np.nan)
                    row[period_key] = format_value(val, fmt) if pd.notna(val) else "-"
                table_data.append(row)

        if table_data:
            size_df = pd.DataFrame(table_data)
            html_table = render_styled_table(size_df, highlight_first_col=True)
            st.markdown(html_table, unsafe_allow_html=True)
        else:
            st.info("Size data not available")

    # === Income Statement Table ===
    elif tables_tab == 1:
        st.markdown("### Income Statement")
        income_metrics = {
            'NII': ('nii', 'billions'),
            'TOI': ('toi', 'billions'),
            'NOII': ('noii', 'billions'),
            'OPEX': ('opex', 'billions'),
            'PPOP': ('ppop', 'billions'),
            'Provision': ('provision_expense', 'billions'),
            'PBT': ('pbt', 'billions'),
            'NPATMI': ('npatmi', 'billions'),
        }

        table_data = []
        for display_name, (col_name, fmt) in income_metrics.items():
            if col_name in df.columns:
                row = {'METRIC': display_name}
                for _, r in df.iterrows():
                    period_key = r['period_label']
                    val = r.get(col_name, np.nan)
                    row[period_key] = format_value(val, fmt) if pd.notna(val) else "-"
                table_data.append(row)

        if table_data:
            income_df = pd.DataFrame(table_data)
            html_table = render_styled_table(income_df, highlight_first_col=True)
            st.markdown(html_table, unsafe_allow_html=True)

    # === Growth Table ===
    elif tables_tab == 2:
        st.markdown("### Growth Metrics")
        st.markdown("**YoY = Year-over-Year | YTD = Year-to-Date**")

        growth_metrics = {
            'NII Growth (YoY)': ('nii_growth_yoy', 'percent'),
            'TOI Growth (YoY)': ('toi_growth_yoy', 'percent'),
            'PPOP Growth (YoY)': ('ppop_growth_yoy', 'percent'),
            'PBT Growth (YoY)': ('pbt_growth_yoy', 'percent'),
            'NPATMI Growth (YoY)': ('npatmi_growth_yoy', 'percent'),
            'Credit Growth (YTD)': ('credit_growth_ytd', 'percent'),
            'Asset Growth (YTD)': ('asset_growth_ytd', 'percent'),
            'Loan Growth (YTD)': ('loan_growth_ytd', 'percent'),
            'Deposit Growth (YTD)': ('deposit_growth_ytd', 'percent'),
        }

        table_data = []
        for display_name, (col_name, fmt) in growth_metrics.items():
            if col_name in df.columns:
                row = {'METRIC': display_name}
                for _, r in df.iterrows():
                    period_key = r['period_label']
                    val = r.get(col_name, np.nan)
                    row[period_key] = format_value(val, fmt) if pd.notna(val) else "-"
                table_data.append(row)

        if table_data:
            growth_df = pd.DataFrame(table_data)
            html_table = render_styled_table(growth_df, highlight_first_col=True)
            st.markdown(html_table, unsafe_allow_html=True)
        else:
            st.info("Growth data not available")

    # === Asset Quality Table ===
    elif tables_tab == 3:
        st.markdown("### Asset Quality")

        quality_metrics = {
            'Group 2 Ratio (%)': ('debt_group2_ratio', 'percent'),
            'NPL Ratio (%)': ('npl_ratio', 'percent'),
            'NPL Amount': ('npl_amount', 'billions'),
            'Provision/Loan (%)': ('provision_to_loan', 'percent'),
            'LLCR (%)': ('llcr', 'percent'),
            'Accrued/Loan (%)': ('accrued_to_loan', 'percent'),
            'Credit Cost (%)': ('credit_cost', 'percent'),
        }

        table_data = []
        for display_name, (col_name, fmt) in quality_metrics.items():
            if col_name in df.columns:
                row = {'METRIC': display_name}
                for _, r in df.iterrows():
                    period_key = r['period_label']
                    val = r.get(col_name, np.nan)
                    row[period_key] = format_value(val, fmt) if pd.notna(val) else "-"
                table_data.append(row)

        if table_data:
            quality_df = pd.DataFrame(table_data)
            html_table = render_styled_table(quality_df, highlight_first_col=True)
            st.markdown(html_table, unsafe_allow_html=True)
        else:
            st.info("Asset quality data not available")

    # === Efficiency Table ===
    elif tables_tab == 4:
        st.markdown("### Efficiency & Earning Quality")

        efficiency_metrics = {
            'NIM (Q) (%)': ('nim_q', 'percent'),
            'Asset Yield (Q) (%)': ('asset_yield_q', 'percent'),
            'Funding Cost (Q) (%)': ('funding_cost_q', 'percent'),
            'Loan Yield (Q) (%)': ('loan_yield_q', 'percent'),
            'CIR (%)': ('cir', 'percent'),
            'CASA Ratio (%)': ('casa_ratio', 'percent'),
            'NII/TOI (%)': ('nii_toi', 'percent'),
            'NOII/TOI (%)': ('noii_toi', 'percent'),
            'LDR Pure (%)': ('ldr_pure', 'percent'),
            'LDR Regulated (%)': ('ldr_regulated_estimated', 'percent'),
            'ROAE (TTM) (%)': ('roea_ttm', 'percent'),
            'ROAA (TTM) (%)': ('roaa_ttm', 'percent'),
        }

        table_data = []
        for display_name, (col_name, fmt) in efficiency_metrics.items():
            if col_name in df.columns:
                row = {'METRIC': display_name}
                for _, r in df.iterrows():
                    period_key = r['period_label']
                    val = r.get(col_name, np.nan)
                    row[period_key] = format_value(val, fmt) if pd.notna(val) else "-"
                table_data.append(row)

        if table_data:
            efficiency_df = pd.DataFrame(table_data)
            html_table = render_styled_table(efficiency_df, highlight_first_col=True)
            st.markdown(html_table, unsafe_allow_html=True)

        # Valuation metrics
        st.markdown("---")
        st.markdown("### Valuation")
        valuation_metrics = {
            'BVPS (VND)': ('bvps', 'number'),
            'EPS (TTM) (VND)': ('eps_ttm', 'number'),
        }

        table_data = []
        for display_name, (col_name, fmt) in valuation_metrics.items():
            if col_name in df.columns:
                row = {'METRIC': display_name}
                for _, r in df.iterrows():
                    period_key = r['period_label']
                    val = r.get(col_name, np.nan)
                    row[period_key] = format_value(val, fmt) if pd.notna(val) else "-"
                table_data.append(row)

        if table_data:
            valuation_df = pd.DataFrame(table_data)
            html_table = render_styled_table(valuation_df, highlight_first_col=True)
            st.markdown(html_table, unsafe_allow_html=True)

    # Download button
    st.markdown("---")
    st.download_button(
        "📥 Download Data (CSV)",
        df.to_csv(index=False).encode('utf-8'),
        f"{ticker}_bank_data.csv",
        "text/csv",
        width='stretch'
    )

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption(f"Data: Bank Financial Metrics | Ticker: **{ticker}** | Records: {len(df)} | Last updated: {df['report_date'].max().strftime('%Y-%m-%d') if not df.empty else 'N/A'}")
