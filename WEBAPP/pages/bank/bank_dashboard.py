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
from WEBAPP.components.filters.fundamental_filter_bar import render_fundamental_filters
from config.sector_analysis.bank_config import BANK_CLASSIFICATION, TIER_COLORS, TIER_NAMES_VI, get_bank_tier

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

# ============================================================================
# INITIALIZE SERVICE & HEADER FILTERS
# ============================================================================
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

# ============================================================================
# CACHED DATA LOADERS (must be defined before use)
# ============================================================================
@st.cache_data(ttl=3600)
def load_bank_group_data():
    """Load aggregated bank group metrics."""
    path = Path("DATA/processed/fundamental/bank/bank_group_metrics.parquet")
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


@st.cache_data(ttl=3600)
def load_bank_data_full(ticker: str, period: str):
    """Load FULL bank financial data for MA4 calculation (from 2018+)."""
    service = BankService()
    df = service.get_financial_data(ticker, period, limit=100)
    if not df.empty and 'report_date' in df.columns:
        df['report_date'] = pd.to_datetime(df['report_date'])
    return df


# ============================================================================
# VIEW MODE SELECTOR
# ============================================================================
view_mode = st.radio(
    "View Mode",
    options=["Individual Bank", "By Tier Group"],
    horizontal=True,
    help="Individual: Single bank analysis | Tier Group: SOCB vs Tier-1/2/3 comparison"
)

# Conditional filters based on view mode
if view_mode == "Individual Bank":
    # Header filter bar (replaces sidebar filters)
    filters = render_fundamental_filters(
        service=service,
        entity_type='bank',
        mode='basic'
    )
    ticker = filters['ticker']
    period = filters['period']
    limit = filters['num_periods']
else:
    # Tier selection for group view
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_tiers = st.multiselect(
            "Select Tiers",
            options=list(BANK_CLASSIFICATION.keys()),
            default=["SOCB", "Tier-1", "Tier-2"],
            help="Compare performance across bank tiers"
        )
    with col2:
        limit = st.slider("Periods", 4, 20, 8)
    period = "Quarterly"  # Fixed for tier view
    ticker = None  # Not used in tier view

    st.markdown("---")

    # =========================================================================
    # TIER GROUP VIEW - Load and render
    # =========================================================================
    df_group = load_bank_group_data()

    if df_group.empty:
        st.error("Bank group data not found. Run: `python3 -c \"import sys; sys.path.insert(0,'.'); from PROCESSORS.fundamental.formulas.bank_formulas import calculate_bank_group_metrics; calculate_bank_group_metrics()\"`")
        st.stop()

    # Filter by selected tiers and limit periods
    df_group = df_group[df_group['tier'].isin(selected_tiers)].copy()
    df_group = df_group.sort_values(['year', 'quarter'])

    # Get latest N periods
    unique_periods = df_group[['year', 'quarter']].drop_duplicates().tail(limit)
    df_group = df_group.merge(unique_periods, on=['year', 'quarter'])

    if df_group.empty:
        st.warning("No data for selected tiers")
        st.stop()

    # -------------------------------------------------------------------------
    # METRIC CARDS - Latest Period Summary
    # -------------------------------------------------------------------------
    st.subheader("Tier Group Summary (Latest Period)")

    latest_period = df_group.groupby('tier').last().reset_index()

    cols = st.columns(len(selected_tiers))
    for i, tier in enumerate(selected_tiers):
        tier_data = latest_period[latest_period['tier'] == tier]
        if tier_data.empty:
            continue
        row = tier_data.iloc[0]
        with cols[i]:
            st.markdown(f"**{tier}** ({int(row.get('bank_count', 0))} banks)")
            c1, c2 = st.columns(2)
            with c1:
                nim = row.get('nim_q_wavg')
                st.metric("NIM", f"{nim:.2f}%" if pd.notna(nim) else "-")
                roe = row.get('roea_ttm_wavg')
                st.metric("ROE", f"{roe:.2f}%" if pd.notna(roe) else "-")
            with c2:
                npl = row.get('npl_ratio_wavg')
                st.metric("NPL", f"{npl:.2f}%" if pd.notna(npl) else "-")
                cir = row.get('cir_wavg')
                st.metric("CIR", f"{cir:.2f}%" if pd.notna(cir) else "-")

    # -------------------------------------------------------------------------
    # TOP CONTRIBUTORS ANALYSIS - Which banks drive tier improvement?
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.subheader("Top Contributors per Tier")

    # Metrics available for contributor analysis
    CONTRIBUTOR_METRICS = {
        "NIM": {"col": "nim_q", "higher_better": True, "unit": "%"},
        "ROE": {"col": "roea_ttm", "higher_better": True, "unit": "%"},
        "NPL": {"col": "npl_ratio", "higher_better": False, "unit": "%"},
        "CIR": {"col": "cir", "higher_better": False, "unit": "%"},
        "CASA": {"col": "casa_ratio", "higher_better": True, "unit": "%"},
        "Credit Cost": {"col": "credit_cost", "higher_better": False, "unit": "%"},
    }

    selected_contributor_metric = st.selectbox(
        "Select metric to analyze",
        options=list(CONTRIBUTOR_METRICS.keys()),
        index=0,
        key="contributor_metric"
    )

    metric_info = CONTRIBUTOR_METRICS[selected_contributor_metric]
    metric_col = metric_info["col"]
    higher_better = metric_info["higher_better"]

    # Load individual bank data to identify contributors
    try:
        bank_df = pd.read_parquet(Path("DATA/processed/fundamental/bank/bank_financial_metrics.parquet"))

        # Get tier classification
        bank_df['tier'] = bank_df['symbol'].apply(get_bank_tier)
        bank_df = bank_df[bank_df['tier'].isin(selected_tiers)]

        # Get last 2 periods to calculate change
        periods = bank_df[['year', 'quarter']].drop_duplicates().sort_values(['year', 'quarter']).tail(2)
        if len(periods) >= 2:
            prev_period = periods.iloc[0]
            curr_period = periods.iloc[1]

            prev_df = bank_df[(bank_df['year'] == prev_period['year']) & (bank_df['quarter'] == prev_period['quarter'])]
            curr_df = bank_df[(bank_df['year'] == curr_period['year']) & (bank_df['quarter'] == curr_period['quarter'])]

            # Merge to calculate change
            cols_to_merge = ['symbol', 'tier', metric_col, 'total_assets']
            cols_to_merge = [c for c in cols_to_merge if c in curr_df.columns]

            if metric_col in curr_df.columns and metric_col in prev_df.columns:
                merged = curr_df[cols_to_merge].merge(
                    prev_df[['symbol', metric_col]],
                    on='symbol',
                    suffixes=('_curr', '_prev')
                )
                merged['change'] = merged[f'{metric_col}_curr'] - merged[f'{metric_col}_prev']

                # Sort: higher_better=True means improvement is positive change
                sort_ascending = not higher_better
                merged = merged.sort_values('change', ascending=sort_ascending)

                # Build consolidated table per tier
                tier_cols = st.columns(len(selected_tiers))
                for i, tier in enumerate(selected_tiers):
                    tier_banks = merged[merged['tier'] == tier].copy()
                    if tier_banks.empty:
                        continue

                    # Re-sort within tier
                    tier_banks = tier_banks.sort_values('change', ascending=not higher_better)

                    with tier_cols[i]:
                        st.markdown(f"**{tier}** ({len(tier_banks)} banks)")

                        # Prepare display dataframe
                        display_df = tier_banks[['symbol', f'{metric_col}_curr', 'change']].copy()
                        display_df.columns = ['Bank', selected_contributor_metric, 'Δ (pp)']
                        display_df[selected_contributor_metric] = display_df[selected_contributor_metric].apply(lambda x: f"{x:.2f}")
                        display_df['Δ (pp)'] = display_df['Δ (pp)'].apply(lambda x: f"{x:+.2f}")

                        # Use centralized styled table function
                        html_table = render_styled_table(display_df, highlight_first_col=True)
                        st.markdown(html_table, unsafe_allow_html=True)

                period_label = f"Q{int(curr_period['quarter'])}/{int(curr_period['year'])} vs Q{int(prev_period['quarter'])}/{int(prev_period['year'])}"
                st.caption(f"{selected_contributor_metric} change: {period_label}")
            else:
                st.info(f"Metric '{metric_col}' not available in data")
    except Exception as e:
        st.warning(f"Could not load contributor analysis: {e}")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # TIME SERIES COMPARISON CHARTS
    # -------------------------------------------------------------------------
    st.subheader("Tier Comparison Over Time")

    TIER_METRICS = {
        "NIM (%)": "nim_q_wavg",
        "ROE (%)": "roea_ttm_wavg",
        "NPL (%)": "npl_ratio_wavg",
        "CIR (%)": "cir_wavg",
        "CASA (%)": "casa_ratio_wavg",
        "Credit Growth (%)": "credit_growth_ytd_wavg",
        "TOI (B VND)": "toi_sum",
        "NPATMI (B VND)": "npatmi_sum",
    }

    selected_tier_metrics = st.multiselect(
        "Select metrics to compare",
        options=list(TIER_METRICS.keys()),
        default=["NIM (%)", "ROE (%)", "NPL (%)", "CIR (%)"],
        label_visibility="collapsed"
    )

    # Generate charts - 2 per row
    chart_idx = 0
    while chart_idx < len(selected_tier_metrics):
        cols = st.columns(2)
        for col_idx in range(2):
            if chart_idx >= len(selected_tier_metrics):
                break

            metric_name = selected_tier_metrics[chart_idx]
            col_name = TIER_METRICS[metric_name]

            with cols[col_idx]:
                fig = go.Figure()

                for tier in selected_tiers:
                    tier_df = df_group[df_group['tier'] == tier].sort_values(['year', 'quarter'])

                    if col_name not in tier_df.columns:
                        continue

                    y_vals = tier_df[col_name]
                    if '_sum' in col_name:
                        y_vals = y_vals / 1e9

                    fig.add_trace(go.Scatter(
                        x=tier_df['period'],
                        y=y_vals,
                        name=tier,
                        mode='lines+markers',
                        line=dict(color=TIER_COLORS.get(tier, '#888'), width=2),
                        marker=dict(size=6),
                        hovertemplate=f"<b>{tier}</b><br>{metric_name}: %{{y:.2f}}<extra></extra>"
                    ))

                # Get base layout and customize legend
                base_layout = get_chart_layout(metric_name, height=350)
                base_layout['legend'] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#FFFFFF'))
                fig.update_layout(
                    **base_layout,
                    showlegend=True,
                    hovermode='x unified'
                )
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')

                st.plotly_chart(fig, use_container_width=True)

            chart_idx += 1

    # -------------------------------------------------------------------------
    # DATA TABLE
    # -------------------------------------------------------------------------
    st.markdown("---")
    with st.expander("View Raw Group Data", expanded=False):
        display_cols = ['tier', 'period', 'bank_count'] + [TIER_METRICS[m] for m in selected_tier_metrics if TIER_METRICS[m] in df_group.columns]
        st.dataframe(df_group[display_cols], use_container_width=True, hide_index=True)

        st.download_button(
            "Download Group Data (CSV)",
            df_group.to_csv(index=False).encode('utf-8'),
            "bank_tier_comparison.csv",
            "text/csv",
            use_container_width=True
        )

    # Footer for tier view
    st.markdown("---")
    st.caption(f"Data: Bank Tier Metrics | Tiers: {', '.join(selected_tiers)} | Periods: {limit}")
    st.stop()  # End execution - don't run individual bank code

st.markdown("---")

# ============================================================================
# INDIVIDUAL BANK VIEW - Load Data
# ============================================================================
if view_mode == "Individual Bank":
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
st.markdown("### Select Metrics")
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

st.markdown("---")

# ============================================================================
# TABS (Session State Persisted)
# ============================================================================
active_tab = render_persistent_tabs(["Charts", "Tables"], "bank_active_tab")

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

    # Mapping from chart column to pre-calculated YoY growth column in parquet
    YOY_COLUMN_MAP = {
        'nii': 'nii_growth_yoy',
        'toi': 'toi_growth_yoy',
        'ppop': 'ppop_growth_yoy',
        'pbt': 'pbt_growth_yoy',
        'npatmi': 'npatmi_growth_yoy',
    }

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

                    # MA4 YoY Growth % line (secondary y-axis) - from pre-calculated parquet
                    yoy_col = YOY_COLUMN_MAP.get(col)
                    ma4_yoy = df[yoy_col] if yoy_col and yoy_col in df.columns else pd.Series([np.nan] * len(df))
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
        ["Size", "Income", "Growth", "Quality", "Efficiency"],
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
        "Download Data (CSV)",
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
