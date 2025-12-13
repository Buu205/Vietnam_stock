"""
Company Financial Analysis Dashboard
======================================

Comprehensive financial analysis for non-financial companies.
Includes individual stock analysis (Tabs 1-5) and sector analysis (Tab 6).

Author: AI Assistant
Date: 2025-12-12
Version: 2.0.0 (Production)

Usage:
    streamlit run WEBAPP/pages/1_fundamental/company_analysis.py
"""

import streamlit as st
import pandas as pd
import sys
import json
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
    page_title="Company Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Navigation
render_main_nav()
render_breadcrumbs(["Home", "Fundamental Analysis", "Company Analysis"])


# ============================================================================
# DATA LOADING (Parquet-only, with caching)
# ============================================================================

@st.cache_data(ttl=3600)  # 1 hour cache
def load_company_data(symbol: str = None) -> pd.DataFrame:
    """
    Load company metrics. If symbol is None, loads all companies.

    This function loads ONCE and caches for 1 hour.
    Replaces the 5x redundant reads in old company_dashboard.
    """
    try:
        parquet_path = DataPaths.fundamental('company')
        df = pd.read_parquet(parquet_path)

        if symbol:
            # Filter for symbol
            symbol_data = df[df['symbol'] == symbol].copy()

            if symbol_data.empty:
                st.warning(f"⚠️ No data found for {symbol}")
                return pd.DataFrame()

            # Sort by date descending
            symbol_data = symbol_data.sort_values('date', ascending=False)
            return symbol_data
        else:
            # Return all data for sector analysis
            return df.sort_values('date', ascending=False)

    except FileNotFoundError:
        st.error(f"❌ Data file not found: {parquet_path}")
        st.info("💡 Run: `python3 PROCESSORS/fundamental/calculators/company_calculator.py`")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=86400)  # 24 hour cache
def load_ticker_details() -> dict:
    """Load ticker details including sector classification."""
    try:
        ticker_path = project_root / 'config' / 'metadata' / 'ticker_details.json'
        with open(ticker_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ Error loading ticker details: {e}")
        return {}


def get_sector_stocks(sector: str, ticker_details: dict) -> list:
    """Get all company tickers in a sector."""
    return [
        ticker for ticker, info in ticker_details.items()
        if info.get('entity') == 'COMPANY' and info.get('sector') == sector
    ]


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
        default_start='2020-01-01',
        default_end='2025-12-12',
        key='company_date_range'
    )


# ============================================================================
# LOAD DATA (ONCE)
# ============================================================================

st.title(f"📊 Company Analysis: {symbol}")

with st.spinner(f"Loading data for {symbol}..."):
    data = load_company_data(symbol)
    ticker_details = load_ticker_details()

if data.empty:
    st.error("❌ No data available for this symbol")
    st.stop()

# Get ticker info
ticker_info = ticker_details.get(symbol, {})
ticker_sector = ticker_info.get('sector', 'Unknown')

# Display ticker info
st.caption(f"**Sector:** {ticker_sector} | **Entity Type:** COMPANY")

# Filter by date range (use report_date or date depending on what's available)
date_col = 'report_date' if 'report_date' in data.columns else 'date'

data_filtered = data[
    (data[date_col] >= pd.to_datetime(start_date)) &
    (data[date_col] <= pd.to_datetime(end_date))
].copy()

if data_filtered.empty:
    st.warning(f"⚠️ No data in selected date range ({start_date} to {end_date})")
    st.stop()


# ============================================================================
# MAIN CONTENT (6 TABS)
# ============================================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Overview",
    "💰 Income Statement",
    "🏦 Balance Sheet",
    "💸 Cash Flow",
    "📊 Financial Ratios",
    "🌐 Sector Analysis"
])


# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

with tab1:
    st.header("Key Metrics Dashboard")

    # Get latest metrics
    latest = data_filtered.iloc[0]

    # Top metrics row
    st.subheader("Latest Quarter Metrics")

    # Build metric cards based on available columns
    metric_cards = []

    if 'net_revenue' in data_filtered.columns:
        metric_cards.append({
            'label': 'Net Revenue',
            'value': latest.get('net_revenue', 0),
            'delta': latest.get('net_revenue_growth', 0) if 'net_revenue_growth' in data_filtered.columns else None,
            'format': 'billions',
            'delta_format': 'percent'
        })

    if 'ebitda' in data_filtered.columns:
        metric_cards.append({
            'label': 'EBITDA',
            'value': latest.get('ebitda', 0),
            'delta': latest.get('ebitda_growth', 0) if 'ebitda_growth' in data_filtered.columns else None,
            'format': 'billions',
            'delta_format': 'percent'
        })

    if 'roe' in data_filtered.columns:
        metric_cards.append({
            'label': 'ROE',
            'value': latest.get('roe', 0),
            'delta': None,
            'format': 'percent'
        })

    # Calculate debt/equity if components exist
    if 'total_liabilities' in data_filtered.columns and 'total_equity' in data_filtered.columns:
        latest_debt = latest.get('total_liabilities', 0)
        latest_equity = latest.get('total_equity', 1)  # Avoid division by zero
        debt_to_equity = (latest_debt / latest_equity) if latest_equity > 0 else 0
        metric_cards.append({
            'label': 'Debt/Equity',
            'value': debt_to_equity,
            'delta': None,
            'format': 'ratio'
        })

    if metric_cards:
        metric_card_row(metric_cards)
    else:
        st.warning("⚠️ Calculated metrics not available. Run company calculator to generate full metrics.")
        st.info("Command: `PYTHONPATH=/Users/buuphan/Dev/Vietnam_dashboard python3 PROCESSORS/fundamental/calculators/company_calculator.py`")

    st.divider()

    # Charts in 2 columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue Trend")
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
        'ebit', 'ebitda', 'net_income', 'financial_income', 'financial_expense'
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
# TAB 3: BALANCE SHEET
# ============================================================================

with tab3:
    st.header("Balance Sheet Analysis")

    # Two column layout for Assets and Liabilities
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Assets")
        asset_metrics = [
            'total_assets', 'current_assets', 'cash',
            'short_term_investments', 'receivables', 'inventory',
            'long_term_assets', 'ppe_net', 'intangible_assets'
        ]
        available_assets = [col for col in asset_metrics if col in data_filtered.columns]

        if available_assets:
            selected_assets = st.multiselect(
                "Select asset metrics",
                options=available_assets,
                default=available_assets[:3],
                key='assets_selector'
            )

            if selected_assets:
                fig = pcb.line_chart(
                    df=data_filtered,
                    x_col='quarter',
                    y_cols=selected_assets,
                    title='Asset Composition',
                    y_axis_title='VND (billions)'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No asset metrics available")

    with col2:
        st.subheader("Liabilities & Equity")
        liability_metrics = [
            'total_liabilities', 'current_liabilities', 'short_term_debt',
            'payables', 'long_term_liabilities', 'long_term_debt',
            'total_equity', 'charter_capital', 'retained_earnings'
        ]
        available_liabilities = [col for col in liability_metrics if col in data_filtered.columns]

        if available_liabilities:
            selected_liabilities = st.multiselect(
                "Select liability & equity metrics",
                options=available_liabilities,
                default=available_liabilities[:3],
                key='liabilities_selector'
            )

            if selected_liabilities:
                fig = pcb.line_chart(
                    df=data_filtered,
                    x_col='quarter',
                    y_cols=selected_liabilities,
                    title='Liabilities & Equity',
                    y_axis_title='VND (billions)'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No liability/equity metrics available")

    # Detailed balance sheet table
    st.divider()
    st.subheader("Detailed Balance Sheet")

    bs_metrics = available_assets + available_liabilities
    if bs_metrics:
        display_cols = ['quarter', 'date'] + bs_metrics
        available_display_cols = [col for col in display_cols if col in data_filtered.columns]

        st.dataframe(
            data_filtered[available_display_cols].head(8),  # Last 2 years
            use_container_width=True,
            hide_index=True
        )


# ============================================================================
# TAB 4: CASH FLOW
# ============================================================================

with tab4:
    st.header("Cash Flow Analysis")

    # Cash flow metrics
    cf_metrics = [
        'operating_cash_flow', 'investing_cash_flow', 'financing_cash_flow',
        'net_cash_flow', 'free_cash_flow', 'capex'
    ]
    available_cf_metrics = [col for col in cf_metrics if col in data_filtered.columns]

    if not available_cf_metrics:
        st.warning("⚠️ No cash flow metrics found in data")
    else:
        # Waterfall chart for cash flow components
        st.subheader("Cash Flow Breakdown")

        # Select metrics to display
        selected_cf = st.multiselect(
            "Select cash flow metrics",
            options=available_cf_metrics,
            default=available_cf_metrics[:4],
            key='cf_selector'
        )

        if selected_cf:
            # Line chart for trends
            fig = pcb.line_chart(
                df=data_filtered,
                x_col='quarter',
                y_cols=selected_cf,
                title='Cash Flow Trends',
                y_axis_title='VND (billions)'
            )
            st.plotly_chart(fig, use_container_width=True)

            # If waterfall components exist
            if 'operating_cash_flow' in data_filtered.columns and 'net_cash_flow' in data_filtered.columns:
                st.subheader("Latest Quarter Cash Flow Waterfall")

                latest_quarter = data_filtered.iloc[0]
                waterfall_data = {
                    'Operating CF': latest_quarter.get('operating_cash_flow', 0),
                    'Investing CF': latest_quarter.get('investing_cash_flow', 0),
                    'Financing CF': latest_quarter.get('financing_cash_flow', 0),
                    'Net CF': latest_quarter.get('net_cash_flow', 0)
                }

                # Use waterfall chart from component library
                waterfall_df = pd.DataFrame({
                    'category': list(waterfall_data.keys()),
                    'value': list(waterfall_data.values())
                })

                fig2 = pcb.waterfall_chart(
                    df=waterfall_df,
                    title=f'Cash Flow Waterfall - {latest_quarter["quarter"]}'
                )
                st.plotly_chart(fig2, use_container_width=True)

        # Detailed cash flow table
        st.divider()
        st.subheader("Detailed Cash Flow Statement")

        display_cols = ['quarter', 'date'] + available_cf_metrics
        available_display_cols = [col for col in display_cols if col in data_filtered.columns]

        st.dataframe(
            data_filtered[available_display_cols].head(8),  # Last 2 years
            use_container_width=True,
            hide_index=True
        )


# ============================================================================
# TAB 5: FINANCIAL RATIOS
# ============================================================================

with tab5:
    st.header("Financial Ratios")

    # Ratio categories in 3 columns
    ratio_cols = st.columns(3)

    with ratio_cols[0]:
        st.subheader("Profitability")
        profitability_metrics = ['roe', 'roa', 'roic', 'gross_margin', 'net_margin']
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
        efficiency_metrics = ['asset_turnover', 'inventory_turnover', 'receivables_turnover']
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
        liquidity_metrics = ['current_ratio', 'quick_ratio', 'cash_ratio']
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

    # Leverage ratios
    st.divider()
    st.subheader("Leverage Ratios")

    leverage_metrics = ['debt_to_equity', 'debt_to_assets', 'interest_coverage']
    available_lev = [col for col in leverage_metrics if col in data_filtered.columns]

    if available_lev:
        fig = pcb.line_chart(
            df=data_filtered,
            x_col='quarter',
            y_cols=available_lev,
            title='Leverage Ratios',
            y_axis_title='Ratio'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No leverage ratios available")


# ============================================================================
# TAB 6: SECTOR ANALYSIS
# ============================================================================

with tab6:
    st.header(f"Sector Analysis: {ticker_sector}")

    # Load all company data for sector analysis
    with st.spinner(f"Loading sector data for {ticker_sector}..."):
        all_company_data = load_company_data(symbol=None)

    if all_company_data.empty or not ticker_details:
        st.error("❌ Cannot perform sector analysis - missing data")
    else:
        # Get all tickers in same sector
        sector_tickers = get_sector_stocks(ticker_sector, ticker_details)

        if len(sector_tickers) < 2:
            st.warning(f"⚠️ Not enough companies in {ticker_sector} sector for analysis")
        else:
            st.info(f"Analyzing {len(sector_tickers)} companies in {ticker_sector} sector")

            # Filter data for sector
            sector_data = all_company_data[all_company_data['symbol'].isin(sector_tickers)].copy()

            # Use same date column as main data
            sector_date_col = 'report_date' if 'report_date' in sector_data.columns else 'date'
            sector_data_filtered = sector_data[
                (sector_data[sector_date_col] >= pd.to_datetime(start_date)) &
                (sector_data[sector_date_col] <= pd.to_datetime(end_date))
            ]

            if sector_data_filtered.empty:
                st.warning("⚠️ No sector data in selected date range")
            else:
                # 1. Sector Average Metrics Over Time
                st.subheader("1. Sector Average Metrics Trend")

                avg_metrics = ['net_revenue', 'ebitda', 'net_income', 'roe', 'roa']
                available_avg_metrics = [col for col in avg_metrics if col in sector_data_filtered.columns]

                if available_avg_metrics:
                    selected_avg = st.multiselect(
                        "Select metrics for sector average",
                        options=available_avg_metrics,
                        default=available_avg_metrics[:3],
                        key='sector_avg_selector'
                    )

                    if selected_avg:
                        # Calculate sector average by quarter
                        sector_avg = sector_data_filtered.groupby('quarter')[selected_avg].mean().reset_index()

                        fig = pcb.line_chart(
                            df=sector_avg,
                            x_col='quarter',
                            y_cols=selected_avg,
                            title=f'{ticker_sector} Sector - Average Metrics',
                            y_axis_title='Average Value'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                st.divider()

                # 2. Latest Quarter Sector Heatmap
                st.subheader("2. Latest Quarter - Sector Comparison Heatmap")

                # Get latest quarter data for all sector companies
                latest_quarter = sector_data_filtered['quarter'].max()
                latest_sector_data = sector_data_filtered[sector_data_filtered['quarter'] == latest_quarter]

                heatmap_metrics = ['roe', 'roa', 'net_margin', 'revenue_growth_yoy', 'debt_to_equity']
                available_heatmap = [col for col in heatmap_metrics if col in latest_sector_data.columns]

                if available_heatmap and len(latest_sector_data) > 0:
                    # Create heatmap data (stocks x metrics)
                    heatmap_data = latest_sector_data.set_index('symbol')[available_heatmap].T

                    # Only show top 10 companies by revenue if too many
                    if len(heatmap_data.columns) > 10:
                        if 'net_revenue' in latest_sector_data.columns:
                            top_companies = latest_sector_data.nlargest(10, 'net_revenue')['symbol'].tolist()
                            heatmap_data = heatmap_data[top_companies]

                    fig = pcb.heatmap(
                        data=heatmap_data.values,
                        title=f'{ticker_sector} Sector - Key Metrics Comparison ({latest_quarter})',
                        x_labels=heatmap_data.columns.tolist(),
                        y_labels=heatmap_data.index.tolist()
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for heatmap")

                st.divider()

                # 3. Top/Bottom Performers
                st.subheader("3. Top/Bottom Performers")

                perf_col1, perf_col2 = st.columns(2)

                with perf_col1:
                    st.caption("**Top 5 by Revenue Growth YoY**")
                    if 'revenue_growth_yoy' in latest_sector_data.columns:
                        top_growth = latest_sector_data.nlargest(5, 'revenue_growth_yoy')[
                            ['symbol', 'revenue_growth_yoy', 'net_revenue']
                        ]
                        st.dataframe(top_growth, hide_index=True, use_container_width=True)
                    else:
                        st.info("Revenue growth data not available")

                with perf_col2:
                    st.caption("**Top 5 by ROE**")
                    if 'roe' in latest_sector_data.columns:
                        top_roe = latest_sector_data.nlargest(5, 'roe')[
                            ['symbol', 'roe', 'roa', 'net_margin']
                        ]
                        st.dataframe(top_roe, hide_index=True, use_container_width=True)
                    else:
                        st.info("ROE data not available")

                st.divider()

                # 4. Sector Distribution (Box Plot)
                st.subheader("4. Sector Metric Distribution")

                dist_metric = st.selectbox(
                    "Select metric for distribution analysis",
                    options=available_heatmap,
                    key='dist_metric_selector'
                )

                if dist_metric:
                    # Show distribution over last 4 quarters
                    recent_quarters = sector_data_filtered['quarter'].unique()[-4:]
                    recent_sector_data = sector_data_filtered[
                        sector_data_filtered['quarter'].isin(recent_quarters)
                    ]

                    # Box plot by quarter
                    import plotly.graph_objects as go

                    box_data = []
                    for quarter in sorted(recent_quarters):
                        quarter_data = recent_sector_data[recent_sector_data['quarter'] == quarter]
                        box_data.append(
                            go.Box(
                                y=quarter_data[dist_metric].dropna(),
                                name=quarter,
                                boxmean='sd'
                            )
                        )

                    fig = go.Figure(data=box_data)
                    fig.update_layout(
                        title=f'{ticker_sector} Sector - {dist_metric} Distribution',
                        yaxis_title=dist_metric,
                        showlegend=True,
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Show current stock's position
                    if symbol in recent_sector_data['symbol'].values:
                        symbol_value = latest_sector_data[
                            latest_sector_data['symbol'] == symbol
                        ][dist_metric].values[0] if len(latest_sector_data[latest_sector_data['symbol'] == symbol]) > 0 else None

                        if symbol_value is not None:
                            sector_values = latest_sector_data[dist_metric].dropna()
                            percentile = (sector_values < symbol_value).sum() / len(sector_values) * 100

                            st.info(f"**{symbol}** {dist_metric}: {symbol_value:.2f} (Percentile: {percentile:.1f}%)")


# ============================================================================
# FOOTER
# ============================================================================

st.divider()
# Use available date column
footer_date = latest[date_col] if date_col in latest.index else 'Unknown'
if isinstance(footer_date, pd.Timestamp):
    footer_date = footer_date.strftime('%Y-%m-%d')

st.caption(f"""
Last updated: {footer_date} |
Data source: company_financial_metrics.parquet |
**Production Version v2.0.0**
""")

# Debug info (collapsible)
with st.expander("🔍 Debug Info"):
    st.write("**Available Columns:**")
    st.write(data_filtered.columns.tolist())
    st.write(f"**Total rows:** {len(data_filtered)}")
    st.write(f"**Date range:** {data_filtered[date_col].min()} to {data_filtered[date_col].max()}")
    st.write(f"**Sector:** {ticker_sector}")
    st.write(f"**Companies in sector:** {len(get_sector_stocks(ticker_sector, ticker_details))}")
    st.write(f"**Date column used:** {date_col}")
