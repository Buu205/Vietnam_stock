"""
Bank Explorer - Interactive Multi-Metric Analysis
==================================================
Dynamic dashboard allowing users to select multiple metrics for comparison.

Features:
- Multi-select for bank tickers or bank types (Private/State)
- Multi-select for metrics (TOI, PBT, NIM, NPL, etc.)
- Auto-generate charts based on selection
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
    CHART_COLORS, render_styled_table, get_table_style
)

# ============================================================================
# PAGE CONFIG & STYLES
# ============================================================================
st.set_page_config(
    page_title="Bank Explorer | VN Market",
    page_icon=":material/account_balance:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(get_page_style(), unsafe_allow_html=True)
st.markdown(get_table_style(), unsafe_allow_html=True)

# ============================================================================
# METRIC DEFINITIONS
# ============================================================================
METRIC_GROUPS = {
    "Income Statement": {
        "NII": {"col": "nii", "unit": "B VND", "scale": 1e9, "description": "Thu nhập lãi thuần"},
        "TOI": {"col": "toi", "unit": "B VND", "scale": 1e9, "description": "Tổng thu nhập hoạt động"},
        "NOII": {"col": "noii", "unit": "B VND", "scale": 1e9, "description": "Thu nhập ngoài lãi"},
        "PPOP": {"col": "ppop", "unit": "B VND", "scale": 1e9, "description": "LN trước dự phòng"},
        "PBT": {"col": "pbt", "unit": "B VND", "scale": 1e9, "description": "LN trước thuế"},
        "NPATMI": {"col": "npatmi", "unit": "B VND", "scale": 1e9, "description": "LN sau thuế CĐCTM"},
    },
    "Profitability": {
        "NIM": {"col": "nim_q", "unit": "%", "scale": 1, "description": "Biên lãi ròng"},
        "ROE": {"col": "roea_ttm", "unit": "%", "scale": 1, "description": "Lợi nhuận/Vốn CSH"},
        "ROA": {"col": "roaa_ttm", "unit": "%", "scale": 1, "description": "Lợi nhuận/Tổng TS"},
        "Asset Yield": {"col": "asset_yield_q", "unit": "%", "scale": 1, "description": "Lợi suất tài sản"},
        "Funding Cost": {"col": "funding_cost_q", "unit": "%", "scale": 1, "description": "Chi phí vốn"},
        "Loan Yield": {"col": "loan_yield_q", "unit": "%", "scale": 1, "description": "Lợi suất cho vay"},
    },
    "Asset Quality": {
        "NPL": {"col": "npl_ratio", "unit": "%", "scale": 1, "description": "Tỷ lệ nợ xấu"},
        "Group 2": {"col": "debt_group2_ratio", "unit": "%", "scale": 1, "description": "Tỷ lệ nợ nhóm 2"},
        "LLCR": {"col": "llcr", "unit": "%", "scale": 1, "description": "Tỷ lệ bao phủ nợ xấu"},
        "Provision/Loan": {"col": "provision_to_loan", "unit": "%", "scale": 1, "description": "Dự phòng/Dư nợ"},
        "Credit Cost": {"col": "credit_cost", "unit": "%", "scale": 1, "description": "Chi phí tín dụng"},
    },
    "Efficiency": {
        "CIR": {"col": "cir", "unit": "%", "scale": 1, "description": "Chi phí/Thu nhập"},
        "CASA": {"col": "casa_ratio", "unit": "%", "scale": 1, "description": "Tiền gửi không kỳ hạn"},
        "LDR": {"col": "ldr_pure", "unit": "%", "scale": 1, "description": "Dư nợ/Huy động"},
        "NII/TOI": {"col": "nii_toi", "unit": "%", "scale": 1, "description": "Thu nhập lãi/Tổng TN"},
    },
    "Size": {
        "Total Assets": {"col": "total_assets", "unit": "B VND", "scale": 1e9, "description": "Tổng tài sản"},
        "Loan": {"col": "total_loan", "unit": "B VND", "scale": 1e9, "description": "Dư nợ cho vay"},
        "Deposit": {"col": "total_customer_deposit", "unit": "B VND", "scale": 1e9, "description": "Tiền gửi KH"},
        "Credit": {"col": "total_credit", "unit": "B VND", "scale": 1e9, "description": "Tổng tín dụng"},
    },
    "Growth (YoY)": {
        "NII Growth": {"col": "nii_growth_yoy", "unit": "%", "scale": 1, "description": "Tăng trưởng NII"},
        "TOI Growth": {"col": "toi_growth_yoy", "unit": "%", "scale": 1, "description": "Tăng trưởng TOI"},
        "PPOP Growth": {"col": "ppop_growth_yoy", "unit": "%", "scale": 1, "description": "Tăng trưởng PPOP"},
        "PBT Growth": {"col": "pbt_growth_yoy", "unit": "%", "scale": 1, "description": "Tăng trưởng PBT"},
        "NPATMI Growth": {"col": "npatmi_growth_yoy", "unit": "%", "scale": 1, "description": "Tăng trưởng NPATMI"},
    },
    "Growth (YTD)": {
        "Credit Growth": {"col": "credit_growth_ytd", "unit": "%", "scale": 1, "description": "Tăng trưởng tín dụng"},
        "Loan Growth": {"col": "loan_growth_ytd", "unit": "%", "scale": 1, "description": "Tăng trưởng cho vay"},
        "Deposit Growth": {"col": "deposit_growth_ytd", "unit": "%", "scale": 1, "description": "Tăng trưởng huy động"},
    },
}

# Bank classification
BANK_TYPES = {
    "Private": ["ACB", "TCB", "MBB", "VPB", "TPB", "HDB", "MSB", "OCB", "LPB", "EIB", "SHB", "STB", "SSB", "NAB", "ABB", "BAB", "KLB", "PGB", "NVB", "VBB", "BVB", "SGB"],
    "State": ["VCB", "CTG", "BID"],
}

# ============================================================================
# HEADER
# ============================================================================
st.title("Bank Explorer")
st.markdown("**Interactive multi-metric analysis for Vietnamese banks**")
st.markdown("---")

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data(ttl=3600)
def load_all_bank_data(limit: int = 12):
    """Load data for all banks."""
    service = BankService()
    tickers = service.get_available_tickers()

    all_data = []
    for ticker in tickers:
        df = service.get_financial_data(ticker, "Quarterly", limit=limit)
        if not df.empty:
            all_data.append(df)

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        combined['report_date'] = pd.to_datetime(combined['report_date'])
        return combined
    return pd.DataFrame()

# Load data
with st.spinner("Loading bank data..."):
    df_all = load_all_bank_data(limit=12)

if df_all.empty:
    st.error("No bank data available. Please run the bank calculator first.")
    st.stop()

# Get available tickers
available_tickers = sorted(df_all['symbol'].unique().tolist())

# ============================================================================
# SIDEBAR - FILTERS
# ============================================================================
st.sidebar.markdown("## Selection Panel")

# Selection mode
selection_mode = st.sidebar.radio(
    "Selection Mode",
    options=["By Ticker", "By Bank Type"],
    horizontal=True
)

if selection_mode == "By Ticker":
    selected_tickers = st.sidebar.multiselect(
        "Select Banks",
        options=available_tickers,
        default=["ACB", "VCB", "TCB"] if all(t in available_tickers for t in ["ACB", "VCB", "TCB"]) else available_tickers[:3],
        help="Select one or more banks to compare"
    )
else:
    selected_types = st.sidebar.multiselect(
        "Select Bank Types",
        options=list(BANK_TYPES.keys()),
        default=["Private"],
        help="Compare by bank ownership type"
    )
    # Get tickers from selected types
    selected_tickers = []
    for bank_type in selected_types:
        selected_tickers.extend([t for t in BANK_TYPES[bank_type] if t in available_tickers])

# Number of periods
num_periods = st.sidebar.number_input(
    "Number of periods to plot",
    min_value=4,
    max_value=20,
    value=10,
    step=1
)

st.sidebar.markdown("---")

# Metric selection with groups
st.sidebar.markdown("## Select Metrics")

# Flatten metrics for multiselect
all_metrics = {}
for group_name, metrics in METRIC_GROUPS.items():
    for metric_name, metric_info in metrics.items():
        all_metrics[metric_name] = {**metric_info, "group": group_name}

# Create grouped options
metric_options = list(all_metrics.keys())

# Default selections
default_metrics = ["TOI", "PBT", "NIM", "Loan Yield", "NPL", "Group 2"]
default_metrics = [m for m in default_metrics if m in metric_options]

selected_metrics = st.sidebar.multiselect(
    "Select Metrics (Z)",
    options=metric_options,
    default=default_metrics,
    help="Select metrics to display as charts"
)

# Show metric groups as expanders for quick selection
with st.sidebar.expander("Quick Select by Group"):
    for group_name in METRIC_GROUPS.keys():
        if st.button(f"Select all {group_name}", key=f"btn_{group_name}"):
            st.session_state['selected_metrics'] = list(METRIC_GROUPS[group_name].keys())
            st.rerun()

# Refresh button
st.sidebar.markdown("---")
if st.sidebar.button("Refresh Data", width='stretch'):
    st.cache_data.clear()
    st.rerun()

# ============================================================================
# FILTER DATA
# ============================================================================
if not selected_tickers:
    st.warning("Please select at least one bank.")
    st.stop()

if not selected_metrics:
    st.warning("Please select at least one metric.")
    st.stop()

# Filter by selected tickers
df_filtered = df_all[df_all['symbol'].isin(selected_tickers)].copy()

# Prepare period labels
df_filtered = df_filtered.sort_values(['symbol', 'report_date'])
df_filtered['period_label'] = df_filtered.apply(
    lambda r: f"{int(r['quarter'])}Q{str(int(r['year']))[-2:]}",
    axis=1
)

# Get latest N periods
unique_periods = df_filtered.sort_values('report_date')['period_label'].unique()
if len(unique_periods) > num_periods:
    latest_periods = unique_periods[-num_periods:]
    df_filtered = df_filtered[df_filtered['period_label'].isin(latest_periods)]

# ============================================================================
# DISPLAY INFO
# ============================================================================
col1, col2, col3 = st.columns(3)
with col1:
    if selection_mode == "By Ticker":
        st.info(f"**Selected Banks:** {', '.join(selected_tickers)}")
    else:
        st.info(f"**Bank Types:** {', '.join(selected_types)}")
with col2:
    st.info(f"**Periods:** {num_periods} quarters")
with col3:
    st.info(f"**Metrics:** {len(selected_metrics)} selected")

st.markdown("---")

# ============================================================================
# GENERATE CHARTS - Each metric as separate chart with all banks as lines
# ============================================================================
st.markdown(f"## Banking Metrics: {', '.join(selected_metrics)}")

# Extended color palette for multiple banks
EXTENDED_COLORS = [
    CHART_COLORS['primary'],      # Blue
    CHART_COLORS['secondary'],    # Teal
    CHART_COLORS['tertiary'],     # Gold
    CHART_COLORS['quaternary'],   # Purple
    CHART_COLORS['quinary'],      # Orange
    CHART_COLORS['positive'],     # Green
    '#E91E63',                    # Pink
    '#9C27B0',                    # Purple
    '#00BCD4',                    # Cyan
    '#FF5722',                    # Deep Orange
    '#795548',                    # Brown
    '#607D8B',                    # Blue Grey
    '#3F51B5',                    # Indigo
    '#CDDC39',                    # Lime
    '#FF9800',                    # Orange
]

# Calculate grid layout - 2 charts per row
num_charts = len(selected_metrics)
cols_per_row = 2
rows_needed = (num_charts + cols_per_row - 1) // cols_per_row

# Generate charts in grid
chart_idx = 0
for row in range(rows_needed):
    cols = st.columns(cols_per_row)
    for col_idx in range(cols_per_row):
        if chart_idx >= num_charts:
            break

        metric_name = selected_metrics[chart_idx]
        metric_info = all_metrics[metric_name]

        with cols[col_idx]:
            col_name = metric_info['col']
            unit = metric_info['unit']
            scale = metric_info['scale']
            description = metric_info.get('description', '')

            # Check if column exists
            if col_name not in df_filtered.columns:
                st.warning(f"{metric_name} data not available")
                chart_idx += 1
                continue

            # Create figure - ALWAYS separate lines per bank
            fig = go.Figure()

            # Each bank gets its own line
            for i, ticker in enumerate(selected_tickers):
                ticker_data = df_filtered[df_filtered['symbol'] == ticker].sort_values('report_date')

                if ticker_data.empty or ticker_data[col_name].isna().all():
                    continue

                y_vals = ticker_data[col_name] / scale if scale > 1 else ticker_data[col_name]

                # ALWAYS use lines - separate line per bank
                fig.add_trace(go.Scatter(
                    x=ticker_data['period_label'],
                    y=y_vals,
                    name=ticker,
                    mode='lines+markers',
                    line=dict(
                        color=EXTENDED_COLORS[i % len(EXTENDED_COLORS)],
                        width=2
                    ),
                    marker=dict(size=6),
                    hovertemplate=f"<b>{ticker}</b><br>" +
                                  f"{metric_name}: %{{y:.2f}} {unit}<br>" +
                                  "Period: %{x}<extra></extra>"
                ))

            # Update layout
            title = f"{metric_name}"
            if description:
                title += f"<br><sup>{description}</sup>"

            fig.update_layout(
                **get_chart_layout(f"{metric_name} ({unit})"),
                yaxis_title=unit,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=10)
                ),
                height=400,
                hovermode='x unified'
            )

            # Add gridlines for better readability
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            fig.update_xaxes(showgrid=False)

            st.plotly_chart(fig, width='stretch')

        chart_idx += 1

# ============================================================================
# DATA TABLE
# ============================================================================
st.markdown("---")
with st.expander("View Raw Data", expanded=False):
    # Prepare display columns
    display_cols = ['symbol', 'period_label'] + [all_metrics[m]['col'] for m in selected_metrics if all_metrics[m]['col'] in df_filtered.columns]

    df_display = df_filtered[display_cols].copy()

    # Rename columns for display
    rename_map = {'symbol': 'Bank', 'period_label': 'Period'}
    for m in selected_metrics:
        if all_metrics[m]['col'] in df_display.columns:
            rename_map[all_metrics[m]['col']] = m

    df_display = df_display.rename(columns=rename_map)

    st.dataframe(df_display, width='stretch', hide_index=True)

    # Download button
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download CSV",
        csv,
        "bank_explorer_data.csv",
        "text/csv",
        width='stretch'
    )

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption(f"Data: Bank Financial Metrics | Banks: {len(selected_tickers)} | Metrics: {len(selected_metrics)} | Periods: {num_periods}")
