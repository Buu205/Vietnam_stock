"""
Company Dashboard - Fundamental analysis for companies (PyEcharts Version)
Updated with new tab structure: Standard, Financial Tables, Valuation
Using PyEcharts instead of Plotly for chart rendering
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import duckdb

# Add project root to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from streamlit_app.core.utils import get_data_path, load_custom_css, get_pyecharts_font_config, get_pyecharts_global_opts_with_font
from streamlit_app.layout.navigation import render_top_nav

# Load custom CSS (Nunito font)
load_custom_css()

# PyEcharts imports
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Scatter, Grid
from pyecharts.components import Table
from pyecharts.globals import ThemeType
from streamlit_echarts import st_pyecharts
from pyecharts.commons.utils import JsCode

# Ensure project paths are available before local imports
# - project root (repo)
# - streamlit_app directory (so `core` resolves to `streamlit_app/core`)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STREAMLIT_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
if STREAMLIT_APP_DIR not in sys.path:
    sys.path.append(STREAMLIT_APP_DIR)

# -----------------------------
# Helpers
# -----------------------------
def _ensure_columns(df: pd.DataFrame, required_cols: list[str], context: str) -> bool:
    """Check required columns exist. Warn missing ones. Return True if ok."""
    if df is None or df.empty:
        st.warning(f"No data available for {context}")
        return False
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.warning(
            f"Missing columns for {context}: {', '.join(missing)}. "
            "Please ensure the parquet has these fields."
        )
        return False
    return True

# Removed custom tooltip formatter to revert to default tooltips

# Import formatting utilities
from streamlit_app.core.formatters import formatter, format_value, format_valuation_df, format_summary_data
from streamlit_app.core.display_config import format_df_for_display, format_metrics_for_display, get_chart_tooltip_config

# Page config for wide layout
st.set_page_config(layout="wide", page_title="Company Dashboard (PyEcharts)", page_icon="🏢")

# Reduce default paddings/margins to utilize full width
st.markdown(
    """
    <style>
    /* Reduce padding around the main block */
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    /* Optional: tighten sidebar padding a bit */
    section[data-testid="stSidebar"] .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# New modular imports (domain loaders, components, features)
from streamlit_app.domains.company.data_loading_company import (
    get_company_symbols,
    load_company_valuation,
)

@st.cache_resource
def get_duckdb_connection():
    """Get DuckDB connection for efficient querying"""
    return duckdb.connect()

@st.cache_data(ttl=300, max_entries=32)  # Cache for 5 minutes to allow fresh Q3/2025 data
def load_financial_summary_data(symbol, start_year):
    """Load financial summary data for a specific symbol and year range"""
    try:
        # Use DuckDB for efficient selective loading
        conn = get_duckdb_connection()
        data_path = get_data_path('calculated_results/fundamental/company/company_financial_metrics.parquet')
        
        # Check if 'year' column exists, if not extract from report_date
        # First, load data to check columns
        sample_df = conn.execute("""
            SELECT * FROM read_parquet(?)
            WHERE symbol = ?
            LIMIT 1
        """, [str(data_path), symbol]).fetchdf()
        
        if sample_df.empty:
            return pd.DataFrame()
        
        # Build query based on available columns
        if 'year' in sample_df.columns:
            # Use year column directly
            df = conn.execute("""
                SELECT * FROM read_parquet(?)
                WHERE symbol = ? AND year >= ?
                ORDER BY year, quarter
            """, [str(data_path), symbol, start_year]).fetchdf()
        elif 'report_date' in sample_df.columns:
            # Extract year from report_date
            df = conn.execute("""
                SELECT *, 
                       EXTRACT(YEAR FROM TRY_CAST(report_date AS DATE)) as year,
                       EXTRACT(QUARTER FROM TRY_CAST(report_date AS DATE)) as quarter
                FROM read_parquet(?)
                WHERE symbol = ? 
                  AND EXTRACT(YEAR FROM TRY_CAST(report_date AS DATE)) >= ?
                ORDER BY year, quarter
            """, [str(data_path), symbol, start_year]).fetchdf()
        else:
            # Fallback: load all and filter in pandas
            df = conn.execute("""
                SELECT * FROM read_parquet(?)
                WHERE symbol = ?
            """, [str(data_path), symbol]).fetchdf()
            
            if 'report_date' in df.columns:
                df['report_date'] = pd.to_datetime(df['report_date'], errors='coerce')
                df['year'] = df['report_date'].dt.year
                df['quarter'] = df['report_date'].dt.quarter
                df = df[df['year'] >= start_year].copy()
                df = df.sort_values(['year', 'quarter'])
        
        # Ensure report_date is datetime
        if 'report_date' in df.columns:
            df['report_date'] = pd.to_datetime(df['report_date'], errors='coerce')
        
        # Sort by date
        if 'report_date' in df.columns:
            df = df.sort_values('report_date')
        
        return df
    except Exception as e:
        st.error(f"Error loading financial summary data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600, max_entries=16)  # Cache for 1 hour, max 16 entries
def get_valuation_data_update_info():
    """Get the latest valuation data update date"""
    try:
        conn = get_duckdb_connection()
        pe_path = get_data_path('calculated_results/valuation/pe/pe_historical_all_symbols_final.parquet')
        query = """
        SELECT MAX(report_date) as latest_date
        FROM read_parquet(?)
        """
        result = conn.execute(query, [str(pe_path)]).fetchone()
        latest_date = result[0] if result else None
        
        # Ensure latest_date is a datetime object
        if latest_date and isinstance(latest_date, str):
            latest_date = pd.to_datetime(latest_date)
        
        return latest_date
    except Exception as e:
        st.error(f"Error getting valuation data update info: {e}")
        return None

def render_company_dashboard():
    """Main company dashboard function"""
    
    # Render Top Navigation
    render_top_nav()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Symbol selection
        company_list = get_company_symbols()
        selected_symbol = st.selectbox(
            "Select Company",
            options=company_list,
            index=0 if company_list else None,
            label_visibility="collapsed"
        )
        
        # Data Settings
        col_year1, col_year2 = st.columns([2, 1])
        with col_year1:
            # Get start year from global state or use default
            default_start_year = st.session_state.get('global_start_year', 2020)
            max_year = max(datetime.now().year, 2025)
            year_options = list(range(2018, max_year + 2))
            start_year = st.selectbox(
                "Start Year",
                options=year_options,
                index=year_options.index(default_start_year) if default_start_year in year_options else 0,
                label_visibility="collapsed"
            )
            # Update global state
            st.session_state.global_start_year = start_year
            
        with col_year2:
             st.caption(f"From {start_year}")

        st.markdown("---")
        
        # Tab navigation buttons - Vertical layout for cleaner look
        st.caption("NAVIGATION")
        
        if st.button("Overview", 
                    type="primary" if st.session_state.get('active_tab') == "Standard" else "secondary", 
                    use_container_width=True):
            st.session_state.active_tab = "Standard"
        
        if st.button("Financial Tables", 
                    type="primary" if st.session_state.get('active_tab') == "Financial Tables" else "secondary",
                    use_container_width=True):
            st.session_state.active_tab = "Financial Tables"
        
        if st.button("Valuation", 
                    type="primary" if st.session_state.get('active_tab') == "Valuation" else "secondary",
                    use_container_width=True):
            st.session_state.active_tab = "Valuation"
        
    
    # Load data on-demand
    with st.spinner(f"Loading data for {selected_symbol}..."):
        fundamental_data = load_financial_summary_data(selected_symbol, start_year)
        valuation_data = load_company_valuation(selected_symbol, start_year)
    
    if fundamental_data.empty:
        st.warning(f"No fundamental data available for {selected_symbol}")
        return
    
    # Initialize session state for navigation
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Standard"
    
    # Display current tab title
    tab_titles = {
        "Standard": "Overview",
        "Financial Tables": "FS Table", 
        "Valuation": "Valuation"
    }
    
    # Remove subheader to avoid duplication with main_app header
    
    # Render content based on active tab
    if st.session_state.active_tab == "Standard":
        render_standard_tab(fundamental_data, valuation_data)
    elif st.session_state.active_tab == "Financial Tables":
        render_financial_tables_tab(selected_symbol, start_year)
    elif st.session_state.active_tab == "Valuation":
        render_valuation_tab(valuation_data)

def render_standard_tab(fundamental_data, valuation_data):
    """Render Standard tab: sequential sections (no sub-tabs)"""
    # Summary (Income Statement Overview)
    render_income_statement_overview(fundamental_data)

    # Margins
    st.markdown("---")
    render_margins_charts(fundamental_data)

    # Growth
    st.markdown("---")
    render_growth_charts(fundamental_data)

def render_income_statement_overview(data):
    """Render Overview: 5 charts (bar + MA4 line) in a 3+2 grid"""
    st.subheader("📈 Income Statement Overview")

    data_copy = data.copy()
    data_copy['quarter'] = data_copy['report_date'].dt.to_period('Q').apply(lambda x: f"Q{x.quarter}/{x.year}")

    # Add EBIT and NPATMI
    metrics = [
        ("net_revenue", "Net Revenue"),
        ("gross_profit", "Gross Profit"),
        ("ebitda", "EBITDA"),
        ("ebit", "EBIT"),
        ("npatmi", "NPATMI"),
    ]

    bar_colors = ["#295CA9", "#009B87", "#FFC132", "#295CA9", "#009B87"]
    # High-contrast line palette vs bars
    line_colors = ["#FFC132", "#FF5722", "#E91E63", "#9C27B0", "#673AB7"]

    def build_chart(idx: int, metric: str, title: str):
        quarters = data_copy['quarter'].tolist()
        values = data_copy[metric].fillna(0).astype(float).tolist()

        ma4_display = []
        try:
            conn = get_duckdb_connection()
            data_path = get_data_path('calculated_results/fundamental/company/company_financial_metrics.parquet')
            query = """
                SELECT symbol, report_date, net_revenue, gross_profit, ebit, ebitda, npatmi
                FROM read_parquet(?)
                WHERE symbol = ?
                ORDER BY report_date
            """
            sym = data_copy['symbol'].iloc[0] if 'symbol' in data_copy.columns else None
            if sym is not None:
                data_full = conn.execute(query, [str(data_path), sym]).fetchdf()
                data_full['report_date'] = pd.to_datetime(data_full['report_date'])
                data_full['quarter'] = data_full['report_date'].dt.to_period('Q').apply(lambda x: f"Q{x.quarter}/{x.year}")
                if len(data_full) >= 8 and metric in data_full.columns:
                    rolling_4q_current = data_full[metric].rolling(window=4, min_periods=4).sum()
                    rolling_4q_prev = rolling_4q_current.shift(4)
                    ma4 = (rolling_4q_current / rolling_4q_prev - 1) * 100.0
                    sel = data_full['quarter'].isin(quarters)
                    ma4_display = ma4[sel].tolist()
        except Exception:
            ma4_display = []

        bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="100%", height="300px"))
            .add_xaxis(quarters)
            .add_yaxis(
                title,
                values,
                itemstyle_opts=opts.ItemStyleOpts(color=bar_colors[idx % len(bar_colors)], opacity=0.75),
                label_opts=opts.LabelOpts(is_show=False)
            )
            .extend_axis(
                yaxis=opts.AxisOpts(
                    name="", type_="value",
                    axislabel_opts=opts.LabelOpts(is_show=False),
                    axisline_opts=opts.AxisLineOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False)
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=title, 
                    pos_left="center",
                    title_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif', font_size=18, font_weight='bold')
                ),
                xaxis_opts=opts.AxisOpts(
                    name="Quarter", 
                    axislabel_opts=opts.LabelOpts(rotate=45, font_family='Nunito, sans-serif'),
                    name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                ),
                yaxis_opts=opts.AxisOpts(
                    name="Value (Billion VND)",
                    axislabel_opts=opts.LabelOpts(font_family='Nunito, sans-serif'),
                    name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                ),
                legend_opts=opts.LegendOpts(
                    is_show=True, 
                    pos_bottom="2%", 
                    pos_left="center",
                    textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                ),
            )
        )

        if ma4_display and len(ma4_display) == len(quarters):
            line = (
                Line()
                .add_xaxis(quarters)
                .add_yaxis(
                    f"{title} MA4",
                    ma4_display,
                    yaxis_index=1,
                    is_smooth=True,
                    linestyle_opts=opts.LineStyleOpts(color=line_colors[idx % len(line_colors)], width=2.6),
                    symbol_size=5,
                    label_opts=opts.LabelOpts(is_show=False)
                )
            )
            bar.overlap(line)
        return bar

    # Render charts in a 2-column grid for better readability
    # Total 5 charts: 2 rows of 2, 1 row of 1 (centered or full width)
    
    # Row 1
    c1, c2 = st.columns(2)
    with c1:
        st_pyecharts(build_chart(0, metrics[0][0], metrics[0][1]), key=f"overview_{metrics[0][0]}")
    with c2:
        st_pyecharts(build_chart(1, metrics[1][0], metrics[1][1]), key=f"overview_{metrics[1][0]}")
        
    # Row 2
    c3, c4 = st.columns(2)
    with c3:
        st_pyecharts(build_chart(2, metrics[2][0], metrics[2][1]), key=f"overview_{metrics[2][0]}")
    with c4:
        st_pyecharts(build_chart(3, metrics[3][0], metrics[3][1]), key=f"overview_{metrics[3][0]}")
        
    # Row 3
    c5, c6 = st.columns([1, 1]) # Use columns to keep size consistent with above
    with c5:
        st_pyecharts(build_chart(4, metrics[4][0], metrics[4][1]), key=f"overview_{metrics[4][0]}")
    with c6:
        st.empty() # Placeholder to keep alignment

def render_metric_chart(data, metric, title, y_axis_title):
    """Render individual metric chart with bar chart and trend line"""
    
    # Prepare data
    quarters = data['quarter'].tolist()
    values = data[metric].tolist()
    
    # Format values for tooltip
    formatted_values = [format_value(x, 'currency') if pd.notna(x) else "N/A" for x in values]
    
    # Create bar chart
    bar_chart = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="100%", height="300px"))
        .add_xaxis(quarters)
        .add_yaxis(
            title,
            values,
            itemstyle_opts=opts.ItemStyleOpts(
                color="#295CA9",
                opacity=0.8
            ),
            label_opts=opts.LabelOpts(is_show=False)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title, 
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif', font_size=18, font_weight='bold')
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=45, font_family='Nunito, sans-serif'),
                name="Quarter",
                name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            ),
            yaxis_opts=opts.AxisOpts(
                name=y_axis_title,
                axislabel_opts=opts.LabelOpts(formatter="{value}", font_family='Nunito, sans-serif'),
                name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                formatter=f"<b>{title}</b><br/>Quarter: {{b0}}<br/>Value: {{c0}}<br/>",
                textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            ),
            legend_opts=opts.LegendOpts(
                is_show=False,
                textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            )
        )
    )
    
    # Calculate MA4 trend line
    try:
        conn = get_duckdb_connection()
        data_path = get_data_path('calculated_results/fundamental/company/company_financial_metrics.parquet')
        query = """
        SELECT symbol, report_date, year, quarter, net_revenue, gross_profit, ebit, ebitda
        FROM read_parquet(?)
        WHERE symbol = ?
        ORDER BY report_date
        """
        data_full = conn.execute(query, [str(data_path), data['symbol'].iloc[0]]).fetchdf()
        data_full['report_date'] = pd.to_datetime(data_full['report_date'])
        data_full['quarter'] = data_full['report_date'].dt.to_period('Q').apply(lambda x: f"Q{x.quarter}/{x.year}")
        
        if len(data_full) >= 8:  # Need at least 8 quarters
            # Calculate 4-quarter rolling sum
            rolling_4q_current = data_full[metric].rolling(window=4, min_periods=4).sum()
            rolling_4q_prev = rolling_4q_current.shift(4)
            ma4 = (rolling_4q_current / rolling_4q_prev - 1) * 100
            
            # Get MA4 for displayed quarters
            ma4_display = ma4[data_full['quarter'].isin(quarters)]
            
            if not ma4_display.empty:
                # Create line chart for MA4
                line_chart = (
                    Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="100%", height="300px"))
                    .add_xaxis(quarters)
                    .add_yaxis(
                        f"{title} MA4",
                        ma4_display.tolist(),
                        linestyle_opts=opts.LineStyleOpts(
                            color="#FFC132",
                            width=2,
                            type_="smooth"
                        ),
                        symbol="circle",
                        symbol_size=4,
                        label_opts=opts.LabelOpts(is_show=False)
                    )
                    .set_global_opts(
                        xaxis_opts=opts.AxisOpts(
                            axislabel_opts=opts.LabelOpts(rotate=45, font_family='Nunito, sans-serif'),
                            name="Quarter",
                            name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                        ),
                        yaxis_opts=opts.AxisOpts(
                            name="Growth (%)",
                            axislabel_opts=opts.LabelOpts(formatter="{value}%", font_family='Nunito, sans-serif'),
                            name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                        ),
                        tooltip_opts=opts.TooltipOpts(
                            trigger="axis",
                            formatter=f"<b>{title} MA4</b><br/>Quarter: {{b0}}<br/>Growth: {{c0}}%<br/>",
                            textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                        ),
                        legend_opts=opts.LegendOpts(
                            is_show=False,
                            textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                        )
                    )
                )
                
                # Combine bar and line charts
                from pyecharts.charts import Grid
                grid = Grid(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="100%", height="300px"))
                grid.add(bar_chart, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="10%", pos_bottom="10%"))
                grid.add(line_chart, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="10%", pos_bottom="10%"))
                
                st_pyecharts(grid, key=f"{metric}_chart")
            else:
                st_pyecharts(bar_chart, key=f"{metric}_chart")
        else:
            st_pyecharts(bar_chart, key=f"{metric}_chart")
    except:
        st_pyecharts(bar_chart, key=f"{metric}_chart")

def render_margins_charts(data):
    """Render Margins charts with 2x2 grid using PyEcharts"""
    st.subheader("💰 Margins Analysis")

    if data is None or data.empty:
        st.warning("No margins data available")
        return

    # Validate columns
    if not _ensure_columns(
        data, [
            'report_date', 'gross_margin', 'ebit_margin', 'ebitda_margin', 'net_margin'
        ], 'Margins'
    ):
        return

    # Convert report_date to quarter format
    data_copy = data.copy()
    data_copy['quarter'] = data_copy['report_date'].dt.to_period('Q').apply(lambda x: f"Q{x.quarter}/{x.year}")

    # Create 2x2 grid layout similar to Overview (overlap Bar + Line)
    col1, col2 = st.columns(2)

    with col1:
        render_margin_chart(data_copy, 'gross_margin', 'Gross Margin %', color_bar="#295CA9", color_line="#FFC132")
    with col2:
        render_margin_chart(data_copy, 'ebit_margin', 'EBIT Margin %', color_bar="#009B87", color_line="#FF5722")

    col3, col4 = st.columns(2)
    with col3:
        render_margin_chart(data_copy, 'ebitda_margin', 'EBITDA Margin %', color_bar="#295CA9", color_line="#E91E63")
    with col4:
        render_margin_chart(data_copy, 'net_margin', 'NPAT Margin %', color_bar="#009B87", color_line="#9C27B0")

def render_margin_chart(data, metric, title, color_bar="#ff7f0e", color_line="#4caf50"):
    """Render margin chart: Bar (Margin %) + Line (QoQ %) overlapped, legend bottom."""
    
    # Prepare data
    quarters = data['quarter'].tolist()
    values = data[metric].tolist()
    
    # Calculate QoQ change
    qoq_change = data[metric].pct_change(fill_method=None) * 100
    
    # Build overlapped chart like Overview
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="100%", height="300px"))
        .add_xaxis(quarters)
        .add_yaxis(
            title,
            values,
            itemstyle_opts=opts.ItemStyleOpts(color=color_bar, opacity=0.75),
            label_opts=opts.LabelOpts(is_show=False)
        )
        .extend_axis(
            yaxis=opts.AxisOpts(
                name="", type_="value",
                axislabel_opts=opts.LabelOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False)
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title, 
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif', font_size=18, font_weight='bold')
            ),
            xaxis_opts=opts.AxisOpts(
                name="Quarter", 
                axislabel_opts=opts.LabelOpts(rotate=45, font_family='Nunito, sans-serif'),
                name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            ),
            yaxis_opts=opts.AxisOpts(
                name="Margin %", 
                axislabel_opts=opts.LabelOpts(formatter="{value}%", font_family='Nunito, sans-serif'),
                name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            ),
            legend_opts=opts.LegendOpts(
                is_show=True, 
                pos_bottom="2%", 
                pos_left="center",
                textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            )
        )
    )

    line = (
        Line()
        .add_xaxis(quarters)
        .add_yaxis(
            f"{title} QoQ",
            qoq_change.fillna(0).tolist(),
            yaxis_index=1,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(color=color_line, width=2.6),
            symbol_size=5,
            label_opts=opts.LabelOpts(is_show=False)
        )
    )
    bar.overlap(line)
    st_pyecharts(bar, key=f"{metric}_chart")

def render_growth_charts(data):
    """Render Growth charts with 2x2 grid using PyEcharts"""
    st.subheader("📊 Growth Analysis")

    if data is None or data.empty:
        st.warning("No growth data available")
        return

    # Validate columns
    if not _ensure_columns(
        data, [
            'report_date', 'net_revenue_gr', 'gross_profit_gr', 'ebit_gr', 'ebitda_gr', 'npatmi_gr'
        ], 'Growth'
    ):
        return

    # Convert report_date to quarter format
    data_copy = data.copy()
    data_copy['quarter'] = data_copy['report_date'].dt.to_period('Q').apply(lambda x: f"Q{x.quarter}/{x.year}")

    # Render as 3x2 grid (6 charts total)
    g1, g2 = st.columns(2)
    with g1:
        render_growth_chart(data_copy, 'net_revenue_gr', 'net_revenue', 'Net Revenue Growth', color_bar="#295CA9", color_line="#FFC132")
    with g2:
        render_growth_chart(data_copy, 'gross_profit_gr', 'gross_profit', 'Gross Profit Growth', color_bar="#009B87", color_line="#FF5722")
    
    g3, g4 = st.columns(2)
    with g3:
        render_growth_chart(data_copy, 'ebit_gr', 'ebit', 'EBIT Growth', color_bar="#295CA9", color_line="#E91E63")
    with g4:
        render_growth_chart(data_copy, 'ebitda_gr', 'ebitda', 'EBITDA Growth', color_bar="#009B87", color_line="#9C27B0")
    
    g5, g6 = st.columns(2)
    with g5:
        render_growth_chart(data_copy, 'npatmi_gr', 'npatmi', 'NPATMI Growth', color_bar="#295CA9", color_line="#FFC132")
    with g6:
        st.empty()  # Empty space for symmetry

def render_growth_chart(data, metric_qoq, base_metric, title, color_bar="#2ca02c", color_line="#2196f3"):
    """Render growth chart: Bar (YoY %) + Line (QoQ %) overlapped, legend bottom.
    
    Args:
        data: DataFrame with quarterly data
        metric_qoq: QoQ growth column from database (e.g., 'net_revenue_gr')
        base_metric: Base value column to calculate YoY (e.g., 'net_revenue')
        title: Chart title
        color_bar: Bar color
        color_line: Line color
        
    Note: 
        - YoY = Year over Year (so với cùng quý năm trước) - công thức: (Q3/2025 / Q3/2024 - 1) * 100
        - QoQ = Quarter over Quarter (so với quý trước) - công thức: (Q3/2025 / Q2/2025 - 1) * 100
    """
    
    # Prepare data
    quarters = data['quarter'].tolist()
    qoq_values = data[metric_qoq].tolist()  # QoQ from database (already calculated)
    
    # Calculate YoY from base values (compare with 4 quarters ago)
    # YoY = (Value(t) / Value(t-4) - 1) * 100
    yoy_values = data[base_metric].pct_change(periods=4, fill_method=None) * 100
    
    # Build overlapped chart: Bar = YoY, Line = QoQ
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="100%", height="300px"))
        .add_xaxis(quarters)
        .add_yaxis(
            f"{title} YoY",  # Bar displays YoY growth (vs same quarter last year)
            yoy_values.fillna(0).tolist(),
            itemstyle_opts=opts.ItemStyleOpts(color=color_bar, opacity=0.75),
            label_opts=opts.LabelOpts(is_show=False)
        )
        .extend_axis(
            yaxis=opts.AxisOpts(
                name="", type_="value",
                axislabel_opts=opts.LabelOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False)
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title, 
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif', font_size=18, font_weight='bold')
            ),
            xaxis_opts=opts.AxisOpts(
                name="Quarter", 
                axislabel_opts=opts.LabelOpts(rotate=45, font_family='Nunito, sans-serif'),
                name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            ),
            yaxis_opts=opts.AxisOpts(
                name="Growth %", 
                axislabel_opts=opts.LabelOpts(formatter="{value}%", font_family='Nunito, sans-serif'),
                name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            ),
            legend_opts=opts.LegendOpts(
                is_show=True, 
                pos_bottom="2%", 
                pos_left="center",
                textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            )
        )
    )

    line = (
        Line()
        .add_xaxis(quarters)
        .add_yaxis(
            f"{title} QoQ",  # Line displays QoQ growth (vs previous quarter)
            qoq_values,
            yaxis_index=1,
            is_smooth=True,
            linestyle_opts=opts.LineStyleOpts(color=color_line, width=2.6),
            symbol_size=5,
            label_opts=opts.LabelOpts(is_show=False)
        )
    )
    bar.overlap(line)
    st_pyecharts(bar, key=f"{base_metric}_growth_chart")

def format_pivot_values(value, metric_name):
    """Format values based on metric type"""
    if pd.isna(value):
        return "N/A"
    
    # Currency metrics (billion VND)
    currency_metrics = ['net_revenue', 'gross_profit', 'ebit', 'ebitda', 'npatmi', 'sga', 
                       'net_finance_income', 'total_assets', 'total_liabilities', 'cash', 
                       'inventory', 'account_receivable', 'tangible_fixed_asset', 
                       'long_term_asset_in_progress', 'st_debt', 'lt_debt', 'total_equity',
                       'operating_cf', 'inv_cf', 'capex', 'fin_cf', 'fcf', 'depreciation']
    
    # Percentage metrics
    percentage_metrics = ['net_revenue_gr', 'gross_profit_gr', 'gross_margin', 'sga_dtt_ratio',
                         'ebit_gr', 'ebit_margin', 'ebitda_gr', 'ebitda_margin', 
                         'npatmi_gr', 'net_margin']
    
    if metric_name.lower() in currency_metrics:
        return f"{value:,.1f}" if abs(value) >= 1 else f"{value:.3f}"
    elif metric_name.lower() in percentage_metrics:
        return f"{value:.1f}%"
    else:
        return f"{value:,.1f}" if abs(value) >= 1 else f"{value:.3f}"

def render_html_table(pivot_df, table_title):
    """Render pivot table as HTML for better control"""
    if pivot_df.empty:
        return
    
    # Create HTML table
    html = f"""
    <div class="table-container">
        <table class="financial-table">
            <thead>
                <tr>
                    <th>KEYCODE</th>
    """
    
    # Add column headers
    for col in pivot_df.columns:
        html += f'<th>{col}</th>'
    
    html += """
                </tr>
            </thead>
            <tbody>
    """
    
    # Add data rows
    for idx, row in pivot_df.iterrows():
        html += f'<tr><td style="font-weight: 600; text-align: left;">{idx}</td>'
        for value in row:
            html += f'<td>{value}</td>'
        html += '</tr>'
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def create_financial_pivot_table(symbol, start_year, metrics_list):
    """Create pivot table with KEYCODE as rows and quarterly periods as columns"""
    data_path = get_data_path('calculated_results/fundamental/company/company_financial_metrics.parquet')
    
    try:
        # Load data
        df = pd.read_parquet(data_path)
        
        # Filter for the selected symbol and year
        if 'symbol' in df.columns:
            df = df[df['symbol'] == symbol].copy()
        
        # Ensure report_date is datetime
        if 'report_date' in df.columns:
            df['report_date'] = pd.to_datetime(df['report_date'], errors='coerce')
        
        # Extract year from report_date if 'year' column doesn't exist
        if 'year' not in df.columns and 'report_date' in df.columns:
            df['year'] = df['report_date'].dt.year
        
        # Filter by year
        if 'year' in df.columns:
            df = df[df['year'] >= start_year].copy()
        
        if df.empty:
            return pd.DataFrame()
        
        # Create quarter column
        df['quarter'] = df['report_date'].dt.year.astype(str) + 'Q' + df['report_date'].dt.quarter.astype(str)
        
        # Filter for available metrics only
        available_metrics = [metric for metric in metrics_list if metric in df.columns]
        
        if not available_metrics:
            return pd.DataFrame()
        
        # Prepare data for pivot
        pivot_data = []
        
        for metric in available_metrics:
            # Get the latest value for each quarter
            metric_data = df[['quarter', metric]].dropna()
            if not metric_data.empty:
                latest_per_quarter = metric_data.groupby('quarter')[metric].last()
                
                row_data = {'KEYCODE': metric.upper()}
                for quarter, value in latest_per_quarter.items():
                    # Format the value based on metric type
                    row_data[quarter] = format_pivot_values(value, metric)
                
                pivot_data.append(row_data)
        
        if not pivot_data:
            return pd.DataFrame()
        
        # Create pivot DataFrame
        pivot_df = pd.DataFrame(pivot_data)
        
        # Set KEYCODE as index
        pivot_df.set_index('KEYCODE', inplace=True)
        
        # Sort columns by quarter
        quarter_cols = [col for col in pivot_df.columns if col.startswith(('20'))]
        quarter_cols.sort()
        pivot_df = pivot_df[quarter_cols]
        
        return pivot_df
        
    except Exception as e:
        st.error(f"Error creating pivot table: {e}")
        return pd.DataFrame()

def render_financial_tables_tab(symbol, start_year):
    """Render Financial Tables tab with 3 sub-tabs - on-demand loading"""
    
    # Sub-tabs for Financial Tables
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
    
    with sub_tab1:
        render_financial_summary_table(symbol, start_year)
    
    with sub_tab2:
        render_balance_sheet_table(symbol, start_year)
    
    with sub_tab3:
        render_cash_flow_table(symbol, start_year)

def render_financial_summary_table(symbol, start_year):
    """Render Income Statement table - on-demand loading with pivot format"""
    st.subheader("Income Statement")
    
    # Add CSS for clean table display with frozen KEYCODE column
    st.markdown("""
    <style>
    .financial-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8rem;
        margin: 10px 0;
        min-width: 100%;
    }
    .financial-table th {
        background-color: #fffacd;
        font-weight: 600;
        text-align: center;
        padding: 8px 6px;
        border: 1px solid #ddd;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    .financial-table th:first-child {
        position: sticky;
        left: 0;
        z-index: 30;
        min-width: 120px;
        background-color: #fffacd !important;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
    }
    .financial-table td {
        text-align: right;
        padding: 6px;
        border: 1px solid #ddd;
        white-space: nowrap;
    }
    .financial-table td:first-child {
        position: sticky;
        left: 0;
        z-index: 25;
        font-weight: 600;
        text-align: left;
        min-width: 120px;
        background-color: white !important;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
    }
    .financial-table tr:hover td:not(:first-child) {
        background-color: #f8f9fa;
    }
    .financial-table tr:hover td:first-child {
        background-color: #f0f0f0 !important;
    }
    .table-container {
        overflow-x: auto;
        border: 1px solid #ddd;
        border-radius: 5px;
        max-height: 600px;
        overflow-y: auto;
        position: relative;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Define Income Statement metrics
    income_statement_metrics = [
        'net_revenue', 'net_revenue_gr', 'gross_profit', 'gross_profit_gr', 'gross_margin',
        'sga', 'sga_dtt_ratio', 'ebit', 'ebit_gr', 'ebit_margin', 'ebitda', 'ebitda_gr', 
        'ebitda_margin', 'net_finance_income', 'npatmi', 'npatmi_gr', 'net_margin'
    ]
    
    # Load and format data
    with st.spinner("Loading income statement data..."):
        pivot_df = create_financial_pivot_table(symbol, start_year, income_statement_metrics)
    
    if pivot_df.empty:
        st.warning(f"No income statement data available for {symbol}")
        return
    
    # Show data info
    st.caption(f"📊 Showing {len(pivot_df)} metrics across {len(pivot_df.columns)} quarters")
    
    # Display the pivot table as HTML for clean scrolling
    render_html_table(pivot_df, "Income Statement")

def render_balance_sheet_table(symbol, start_year):
    """Render Balance Sheet table - on-demand loading with pivot format"""
    st.subheader("Balance Sheet")
    
    # Define Balance Sheet metrics
    balance_sheet_metrics = [
        'total_assets', 'cash', 'inventory', 'account_receivable', 'tangible_fixed_asset',
        'long_term_asset_in_progress', 'total_liabilities', 'st_debt', 'lt_debt', 'total_equity'
    ]
    
    # Load and format data
    with st.spinner("Loading balance sheet data..."):
        pivot_df = create_financial_pivot_table(symbol, start_year, balance_sheet_metrics)
    
    if pivot_df.empty:
        st.warning(f"No balance sheet data available for {symbol}")
        return
    
    # Show data info
    st.caption(f"📊 Showing {len(pivot_df)} metrics across {len(pivot_df.columns)} quarters")
    
    # Display the pivot table as HTML for clean scrolling
    render_html_table(pivot_df, "Balance Sheet")

def render_cash_flow_table(symbol, start_year):
    """Render Cash Flow table - on-demand loading with pivot format"""
    st.subheader("Cash Flow")
    
    # Define Cash Flow metrics
    cash_flow_metrics = [
        'operating_cf', 'depreciation', 'inv_cf', 'capex', 'fin_cf', 'fcf'
    ]
    
    # Load and format data
    with st.spinner("Loading cash flow data..."):
        pivot_df = create_financial_pivot_table(symbol, start_year, cash_flow_metrics)
    
    if pivot_df.empty:
        st.warning(f"No cash flow data available for {symbol}")
        return
    
    # Display the pivot table as HTML for clean scrolling
    render_html_table(pivot_df, "Cash Flow")

def render_valuation_tab(valuation_data):
    """Render Valuation tab: summary metrics + historical trends (merged view)"""
    # Render valuation charts
    render_valuation_charts(valuation_data)

def render_valuation_charts(valuation_data):
    """Render Valuation Charts (PE, PB, EV/EBITDA) using PyEcharts"""
    st.subheader("📊 Valuation Charts")
    
    # Show data range info
    if isinstance(valuation_data, dict):
        for metric, df in valuation_data.items():
            if not df.empty and 'date' in df.columns:
                min_date = pd.to_datetime(df['date']).min().strftime('%Y-%m-%d')
                max_date = pd.to_datetime(df['date']).max().strftime('%Y-%m-%d')
                st.caption(f"📅 {metric.upper()} data: {min_date} to {max_date} ({len(df)} records)")
                break

    def build_line_with_bands(df, x_col, y_col, title, color):
        if df is None or df.empty or y_col not in df.columns or x_col not in df.columns:
            st.warning(f"No data for {title}")
            return None

        # Defensive normalization: ensure datetime x-axis and numeric y-axis
        df_norm = df[[x_col, y_col]].copy()
        df_norm[x_col] = pd.to_datetime(df_norm[x_col], errors='coerce')
        df_norm[y_col] = pd.to_numeric(df_norm[y_col], errors='coerce')
        df_norm = df_norm.dropna(subset=[x_col, y_col])
        if df_norm.empty:
            st.warning(f"No valid points for {title}")
            return None

        df_sorted = df_norm.sort_values(x_col)
        x_vals = df_sorted[x_col].dt.strftime('%Y-%m-%d').tolist()
        # Round series to 1 decimal place for display consistency
        y_vals_raw = [float(v) for v in df_sorted[y_col].astype(float).tolist()]
        y_vals = [round(v, 1) for v in y_vals_raw]

        series_mean = float(np.nanmean(y_vals)) if len(y_vals) else 0.0
        series_std = float(np.nanstd(y_vals)) if len(y_vals) else 0.0
        band_plus = [round(series_mean + series_std, 1)] * len(x_vals)
        band_mean = [round(series_mean, 1)] * len(x_vals)
        band_minus = [round(max(series_mean - series_std, 0.0), 1)] * len(x_vals)

        # Compute dynamic y padding (±5%) to avoid cramped visuals
        if y_vals_raw:
            vmin = min(y_vals_raw)
            vmax = max(y_vals_raw)
            span = vmax - vmin
            base = span if span != 0 else (abs(vmax) if vmax != 0 else 1.0)
            pad = base * 0.05
            y_min = vmin - pad
            y_max = vmax + pad
        else:
            y_min = None
            y_max = None

        main = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="100%", height="320px"))
            .add_xaxis(x_vals)
            .add_yaxis(
                title,
                y_vals,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(color=color, width=2.6),
                symbol_size=5,
                label_opts=opts.LabelOpts(is_show=False)
            )
            .add_yaxis(
                f"{title} +1σ",
                band_plus,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(color="#9e9e9e", width=1.2, type_="dashed"),
                label_opts=opts.LabelOpts(is_show=False)
            )
            .add_yaxis(
                f"{title} mean",
                band_mean,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(color="#616161", width=1.2, type_="dotted"),
                label_opts=opts.LabelOpts(is_show=False)
            )
            .add_yaxis(
                f"{title} -1σ",
                band_minus,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(color="#9e9e9e", width=1.2, type_="dashed"),
                label_opts=opts.LabelOpts(is_show=False)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=title, 
                    pos_left="center", 
                    padding=[10,0,10,0],
                    title_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif', font_size=18, font_weight='bold')
                ),
                xaxis_opts=opts.AxisOpts(
                    name="Date", 
                    axislabel_opts=opts.LabelOpts(rotate=0, font_family='Nunito, sans-serif'),
                    name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                ),
                yaxis_opts=opts.AxisOpts(
                    name=title,
                    min_=y_min,
                    max_=y_max,
                    axislabel_opts=opts.LabelOpts(
                        formatter=JsCode("function(v){return Number(v).toFixed(1);}"),
                        font_family='Nunito, sans-serif'
                    ),
                    name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                ),
                legend_opts=opts.LegendOpts(
                    is_show=True, 
                    pos_bottom="2%", 
                    pos_left="center", 
                    item_gap=12,
                    textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                )
            )
        )
        return main

    pe_df = valuation_data.get('pe') if isinstance(valuation_data, dict) else None
    pb_df = valuation_data.get('pb') if isinstance(valuation_data, dict) else None
    ev_df = valuation_data.get('ev_ebitda') if isinstance(valuation_data, dict) else None

    # Render one chart per row for clarity
    chart_pe = build_line_with_bands(pe_df, 'date', 'pe_ratio', 'P/E', '#1f77b4')
    if chart_pe is not None:
        st_pyecharts(chart_pe, key="pe_chart")
        st.markdown("---")

    chart_pb = build_line_with_bands(pb_df, 'date', 'pb_ratio', 'P/B', '#ff7f0e')
    if chart_pb is not None:
        st_pyecharts(chart_pb, key="pb_chart")
        st.markdown("---")

    chart_ev = build_line_with_bands(ev_df, 'date', 'ev_ebitda_ratio', 'EV/EBITDA', '#2ca02c')
    if chart_ev is not None:
        st_pyecharts(chart_ev, key="ev_chart")

# Main execution
if __name__ == "__main__":
    render_company_dashboard()
