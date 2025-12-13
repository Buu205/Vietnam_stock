"""
Company Financial Analysis Dashboard (DEMO)
============================================

Example dashboard using new component library.
Comprehensive financial analysis for non-financial companies.

Author: AI Assistant
Date: 2025-12-12
Version: 2.0.0 (Demo)

Usage:
    streamlit run WEBAPP/pages/1_fundamental/company_analysis_demo.py
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Project imports
from WEBAPP.core.data_paths import DataPaths
from WEBAPP.components.charts import PlotlyChartBuilder as pcb
from WEBAPP.components.navigation import render_main_nav, render_breadcrumbs
from WEBAPP.components.inputs import symbol_selector, date_range_picker
from WEBAPP.components.data_display import metric_card_row

# Page config
st.set_page_config(
    page_title="Company Analysis Demo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Navigation
render_main_nav()
render_breadcrumbs(["Home", "Fundamental Analysis", "Company Analysis (Demo)"])


# ============================================================================
# DATA LOADING (Parquet-only, with caching)
# ============================================================================

@st.cache_data(ttl=3600)  # 1 hour cache
def load_company_data(symbol: str) -> pd.DataFrame:
    """
    Load all company metrics for a symbol.

    This function loads ONCE and caches for 1 hour.
    Replaces the 5x redundant reads in old company_dashboard.
    """
    try:
        parquet_path = DataPaths.fundamental('company')
        df = pd.read_parquet(parquet_path)

        # Filter for symbol
        symbol_data = df[df['symbol'] == symbol].copy()

        if symbol_data.empty:
            st.warning(f"⚠️ No data found for {symbol}")
            return pd.DataFrame()

        # Sort by date descending
        symbol_data = symbol_data.sort_values('date', ascending=False)

        return symbol_data

    except FileNotFoundError:
        st.error(f"❌ Data file not found: {parquet_path}")
        st.info("💡 Run: `python3 PROCESSORS/fundamental/calculators/company_calculator.py`")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()


# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

with st.sidebar:
    st.header("⚙️ Settings")

    # Symbol selector
    symbol = symbol_selector(
        entity_type='company',
        default='VNM',
        key='company_symbol'
    )

    st.divider()

    # Date range
    start_date, end_date = date_range_picker(
        default_start='2023-01-01',
        default_end='2025-12-12',
        key='company_date_range'
    )


# ============================================================================
# LOAD DATA (ONCE)
# ============================================================================

st.title(f"📊 Company Analysis: {symbol}")

with st.spinner(f"Loading data for {symbol}..."):
    data = load_company_data(symbol)

if data.empty:
    st.error("❌ No data available for this symbol")
    st.stop()

# Filter by date range
data_filtered = data[
    (data['date'] >= pd.to_datetime(start_date)) &
    (data['date'] <= pd.to_datetime(end_date))
].copy()

if data_filtered.empty:
    st.warning(f"⚠️ No data in selected date range ({start_date} to {end_date})")
    st.stop()


# ============================================================================
# MAIN CONTENT (3 TABS FOR DEMO)
# ============================================================================

tab1, tab2, tab3 = st.tabs([
    "📈 Overview",
    "💰 Income Statement",
    "📊 Financial Ratios"
])


# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

with tab1:
    st.header("Key Metrics Dashboard")

    # Get latest metrics
    latest = data_filtered.iloc[0]

    # Top metrics row (DEMO: using metric_card_row component)
    st.subheader("Latest Quarter Metrics")

    metric_card_row([
        {
            'label': 'Net Revenue',
            'value': latest.get('net_revenue', 0),
            'delta': latest.get('revenue_growth_yoy', 0),
            'format': 'billions',
            'delta_format': 'percent'
        },
        {
            'label': 'EBITDA',
            'value': latest.get('ebitda', 0),
            'delta': latest.get('ebitda_growth_yoy', 0),
            'format': 'billions',
            'delta_format': 'percent'
        },
        {
            'label': 'ROE',
            'value': latest.get('roe', 0),
            'delta': None,
            'format': 'percent'
        },
        {
            'label': 'Debt/Equity',
            'value': latest.get('debt_to_equity', 0),
            'delta': None,
            'format': 'ratio'
        }
    ])

    st.divider()

    # Charts in 2 columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue Trend")
        # DEMO: Using bar_line_combo from PlotlyChartBuilder
        if 'net_revenue' in data_filtered.columns and 'net_revenue_ma4' in data_filtered.columns:
            fig1 = pcb.bar_line_combo(
                df=data_filtered,
                x_col='quarter',
                bar_col='net_revenue',
                line_col='net_revenue_ma4',
                title='Net Revenue with MA4',
                bar_name='Revenue (billions VND)',
                line_name='MA4 Trend'
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Revenue trend chart requires 'net_revenue' and 'net_revenue_ma4' columns")

    with col2:
        st.subheader("Profitability Margins")
        # DEMO: Using line_chart from PlotlyChartBuilder
        margin_cols = ['gross_margin', 'ebit_margin', 'ebitda_margin', 'net_margin']
        available_margin_cols = [col for col in margin_cols if col in data_filtered.columns]

        if available_margin_cols:
            fig2 = pcb.line_chart(
                df=data_filtered,
                x_col='quarter',
                y_cols=available_margin_cols,
                title='Profitability Margins',
                y_axis_title='Margin (%)'
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Profitability chart requires margin columns")

    # Growth rates
    st.subheader("Revenue Growth YoY")
    if 'revenue_growth_yoy' in data_filtered.columns:
        fig3 = pcb.bar_chart(
            df=data_filtered,
            x_col='quarter',
            y_col='revenue_growth_yoy',
            title='Revenue Growth YoY',
            color='#10B981'
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Growth chart requires 'revenue_growth_yoy' column")


# ============================================================================
# TAB 2: INCOME STATEMENT
# ============================================================================

with tab2:
    st.header("Income Statement Analysis")

    # Available CIS metrics
    potential_cis_metrics = [
        'net_revenue', 'cogs', 'gross_profit', 'sga_expense',
        'ebit', 'ebitda', 'net_income'
    ]
    available_cis_metrics = [col for col in potential_cis_metrics if col in data_filtered.columns]

    if not available_cis_metrics:
        st.warning("⚠️ No income statement metrics found in data")
    else:
        # Metric selector
        selected_metrics = st.multiselect(
            "Select metrics to display",
            options=available_cis_metrics,
            default=available_cis_metrics[:4]  # First 4
        )

        if selected_metrics:
            # Multi-line chart for selected metrics
            fig = pcb.line_chart(
                df=data_filtered,
                x_col='quarter',
                y_cols=selected_metrics,
                title='Income Statement Metrics',
                y_axis_title='VND (billions)'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Detailed table
            st.subheader("Detailed Income Statement")

            display_cols = ['quarter', 'date'] + selected_metrics
            available_display_cols = [col for col in display_cols if col in data_filtered.columns]

            st.dataframe(
                data_filtered[available_display_cols].head(12),  # Last 3 years
                use_container_width=True,
                hide_index=True
            )


# ============================================================================
# TAB 3: FINANCIAL RATIOS
# ============================================================================

with tab3:
    st.header("Financial Ratios")

    # Ratio categories
    ratio_cols = st.columns(3)

    with ratio_cols[0]:
        st.subheader("Profitability")
        profitability_metrics = ['roe', 'roa', 'roic']
        available_prof = [col for col in profitability_metrics if col in data_filtered.columns]

        if available_prof:
            fig = pcb.line_chart(
                df=data_filtered,
                x_col='quarter',
                y_cols=available_prof,
                title='Profitability Ratios',
                y_axis_title='Ratio (%)',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No profitability ratios available")

    with ratio_cols[1]:
        st.subheader("Efficiency")
        efficiency_metrics = ['asset_turnover', 'inventory_turnover']
        available_eff = [col for col in efficiency_metrics if col in data_filtered.columns]

        if available_eff:
            fig = pcb.line_chart(
                df=data_filtered,
                x_col='quarter',
                y_cols=available_eff,
                title='Efficiency Ratios',
                y_axis_title='Times',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No efficiency ratios available")

    with ratio_cols[2]:
        st.subheader("Liquidity")
        liquidity_metrics = ['current_ratio', 'quick_ratio']
        available_liq = [col for col in liquidity_metrics if col in data_filtered.columns]

        if available_liq:
            fig = pcb.line_chart(
                df=data_filtered,
                x_col='quarter',
                y_cols=available_liq,
                title='Liquidity Ratios',
                y_axis_title='Ratio',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No liquidity ratios available")


# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption(f"""
Last updated: {latest['date'].strftime('%Y-%m-%d')} |
Data source: company_financial_metrics.parquet |
**DEMO VERSION** - Using new component library
""")

# Debug info (collapsible)
with st.expander("🔍 Debug Info"):
    st.write("**Available Columns:**")
    st.write(data_filtered.columns.tolist())
    st.write(f"**Total rows:** {len(data_filtered)}")
    st.write(f"**Date range:** {data_filtered['date'].min()} to {data_filtered['date'].max()}")
