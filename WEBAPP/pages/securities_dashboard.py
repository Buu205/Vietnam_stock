"""
Securities Dashboard - Securities sector analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import duckdb

# Add the parent directory to sys.path to enable imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from WEBAPP.core.utils import get_data_path, load_custom_css, get_plotly_font_config
from WEBAPP.layout.navigation import render_top_nav

# Load custom CSS (Nunito font)
load_custom_css()

# Plotly configuration to avoid deprecation warnings
PLOTLY_CONFIG = {
    "displayModeBar": False,
    "staticPlot": False,
    "responsive": True,
    "autosizable": True,
    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"]
}

# Allowed securities list - only these securities will be shown
ALLOWED_SECURITIES = [
    'AGR', 'BSI', 'BVS', 'CTS', 'DSC', 'DSE', 'FTS', 'HCM', 'MBS', 
    'ORS', 'SHS', 'SSI', 'TVS', 'VCI', 'VDS', 'VIX', 'VND'
]

# PyEcharts imports for overview
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Boxplot
from pyecharts.commons.utils import JsCode
from streamlit_echarts import st_pyecharts

# Add project root to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import formatting utilities
from WEBAPP.core.formatters import formatter, format_value, format_df_column, format_summary_data

# PyEcharts helper functions for overview
def build_line(xs, ys, title, color):
    """Build a PyEcharts line chart"""
    # compute y padding ±5%
    try:
        numeric = [float(v) for v in ys if v is not None]
        if numeric:
            vmin, vmax = min(numeric), max(numeric)
            span = vmax - vmin
            pad = (span if span != 0 else (abs(vmax) if vmax != 0 else 1.0)) * 0.05
            y_min, y_max = vmin - pad, vmax + pad
        else:
            y_min, y_max = None, None
    except Exception:
        y_min, y_max = None, None

    return (
        Line(init_opts=opts.InitOpts(width="100%", height="300px"))
        .add_xaxis(xs)
        .add_yaxis("", ys, is_smooth=True,
                   linestyle_opts=opts.LineStyleOpts(color=color, width=2.6),
                   label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif', font_size=18, font_weight='bold')
            ),
            xaxis_opts=opts.AxisOpts(
                name="Date", 
                boundary_gap=False,
                axislabel_opts=opts.LabelOpts(font_family='Nunito, sans-serif'),
                name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            ),
            yaxis_opts=opts.AxisOpts(
                name="Value",
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
        )
    )


def build_bar(xs, ys, title, color):
    """Build a PyEcharts bar chart"""
    # compute y padding ±5%
    try:
        numeric = [float(v) for v in ys if v is not None]
        if numeric:
            vmin, vmax = min(numeric), max(numeric)
            span = vmax - vmin
            pad = (span if span != 0 else (abs(vmax) if vmax != 0 else 1.0)) * 0.05
            y_min, y_max = vmin - pad, vmax + pad
        else:
            y_min, y_max = None, None
    except Exception:
        y_min, y_max = None, None

    return (
        Bar(init_opts=opts.InitOpts(width="100%", height="300px"))
        .add_xaxis(xs)
        .add_yaxis("", ys,
                   itemstyle_opts=opts.ItemStyleOpts(color=color, opacity=0.8),
                   label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif', font_size=18, font_weight='bold')
            ),
            xaxis_opts=opts.AxisOpts(
                name="Date",
                axislabel_opts=opts.LabelOpts(font_family='Nunito, sans-serif'),
                name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
            ),
            yaxis_opts=opts.AxisOpts(
                name="Value",
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
        )
    )


def _safe_plot_pyecharts(df, col_name, xs, title, color, key_prefix):
    """Safely plot PyEcharts chart with data validation"""
    try:
        if col_name not in df.columns:
            return False
        
        # Get values and filter out None/NaN
        values = df[col_name].fillna(0).astype(float).tolist()
        if not values or all(v == 0 for v in values):
            return False
        
        # Create chart
        chart = build_line(xs, values, title, color)
        st_pyecharts(chart, key=f"{key_prefix}_{col_name}")
        return True
    except Exception as e:
        st.error(f"Error plotting {title}: {e}")
        return False


def get_security_symbols():
    """Get list of security symbols from data - only selected securities"""
    try:
        # Load from security_full.parquet and filter to only allowed securities
        security_path = get_data_path('DATA/processed/fundamental/security_full.parquet')
        df = pd.read_parquet(str(security_path))
        securities = df[df['ENTITY_TYPE'] == 'SECURITY']['SECURITY_CODE'].unique()
        # Filter to only allowed securities
        securities_list = sorted([s for s in securities.tolist() if s in ALLOWED_SECURITIES])
        return securities_list
    except Exception:
        # Fallback list - only allowed securities
        return sorted(ALLOWED_SECURITIES)


def create_mock_security_data(symbol, start_year):
    """Create mock data for securities when real data is not available"""
    dates = pd.date_range(start=f'{start_year}-01-01', end='2025-01-01', freq='Q')
    
    # Mock data structure for securities
    data = {
        'date': dates,
        'symbol': [symbol] * len(dates),
        'revenue': np.random.uniform(100, 500, len(dates)),
        'gross_profit': np.random.uniform(50, 200, len(dates)),
        'operating_income': np.random.uniform(30, 150, len(dates)),
        'net_income': np.random.uniform(20, 100, len(dates)),
        'total_assets': np.random.uniform(1000, 3000, len(dates)),
        'equity': np.random.uniform(500, 1500, len(dates)),
        'roe': np.random.uniform(5, 25, len(dates)),
        'roa': np.random.uniform(2, 10, len(dates)),
        'gross_margin': np.random.uniform(15, 35, len(dates)),
        'operating_margin': np.random.uniform(10, 25, len(dates)),
        'net_margin': np.random.uniform(5, 15, len(dates)),
    }
    
    return pd.DataFrame(data)


def create_mock_valuation_data(symbol, start_year):
    """Create mock valuation data"""
    dates = pd.date_range(start=f'{start_year}-01-01', end='2025-01-01', freq='M')
    
    return {
        'pe': pd.DataFrame({
            'date': dates,
            'symbol': [symbol] * len(dates),
            'pe_ratio': np.random.uniform(5, 30, len(dates)),
            'close_price': np.random.uniform(10, 100, len(dates))
        }),
        'pb': pd.DataFrame({
            'date': dates,
            'symbol': [symbol] * len(dates),
            'pb_ratio': np.random.uniform(0.5, 5, len(dates)),
            'close_price': np.random.uniform(10, 100, len(dates))
        })
    }


def render_securities_dashboard():
    """Render securities dashboard page with 3 tabs: Overview, Securities Metric, Valuation"""
    # Render Top Navigation
    render_top_nav()
    
    
    # Sidebar filters
    with st.sidebar:
        st.header("Navigation")
        
        # Get securities list
        securities_list = get_security_symbols()
        selected_symbol = st.selectbox(
            "Select Security",
            options=securities_list,
            index=0
        )
        # Sync selected security into session state for cross-tab linkage
        st.session_state.selected_security = selected_symbol
        
        # Date range
        start_year = st.slider(
            "Start Year",
            min_value=2020,
            max_value=2025,
            value=2022
        )
        
        # Update global state
        st.session_state.global_start_year = start_year
        
        # Tab navigation buttons
        if st.button("Overview",
                    type="primary" if st.session_state.get('active_tab') == "Overview" else "secondary"):
            st.session_state.active_tab = "Overview"
        
        if st.button("Securities Metric",
                    type="primary" if st.session_state.get('active_tab') == "Securities Metric" else "secondary"):
            st.session_state.active_tab = "Securities Metric"
        
        if st.button("Valuation",
                    type="primary" if st.session_state.get('active_tab') == "Valuation" else "secondary"):
            st.session_state.active_tab = "Valuation"
        
        # Metric Type selection (only show in Valuation tab)
        if st.session_state.get('active_tab') == "Valuation":
            st.markdown("---")
            st.subheader("Metric Type")
            metric_type = st.selectbox(
                "Select Metric",
                options=["P/E", "P/B"],
                key="securities_metric_type_sidebar",
                label_visibility="collapsed"
            )
            st.session_state.securities_metric_type = metric_type
    
    # Initialize session state for navigation
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Overview"
    
    # Load data on-demand
    with st.spinner(f"Loading data for {selected_symbol}..."):
        securities_data = load_securities_data(selected_symbol, start_year)
        valuation_data = load_securities_valuation_data(selected_symbol, start_year)
    
    # Render content based on active tab
    if st.session_state.active_tab == "Overview":
        render_overview_tab(securities_data)
    elif st.session_state.active_tab == "Securities Metric":
        render_securities_metric_tab(selected_symbol, start_year)
    elif st.session_state.active_tab == "Valuation":
        render_valuation_tab(valuation_data, selected_symbol, start_year)


def _get_security_parquet_path() -> Path:
    """Get path to security fundamental data"""
    return Path(get_data_path("DATA/processed/fundamental/security_full.parquet"))


@st.cache_data(ttl=300, max_entries=32)  # Cache for 5 minutes to allow fresh Q3/2025 data
def load_securities_data(symbol, start_year):
    """Load securities fundamental data from security_full.parquet"""
    try:
        p = _get_security_parquet_path()
        df = pd.read_parquet(str(p))
        
        # Filter for securities entity type and specific symbol
        df = df[df['ENTITY_TYPE'] == 'SECURITY'].copy()
        df = df[df['SECURITY_CODE'] == symbol].copy()
        
        # Convert date columns
        if 'REPORT_DATE' in df.columns:
            df['date'] = pd.to_datetime(df['REPORT_DATE'])
        elif 'REPORTED_DATE' in df.columns:
            df['date'] = pd.to_datetime(df['REPORTED_DATE'])
        else:
            df['date'] = pd.to_datetime(df.index)
        
        # Filter by year
        df = df[df['date'].dt.year >= start_year].copy()
        
        # Pivot the data to have metrics as columns
        df_pivot = df.pivot_table(
            index=['date', 'SECURITY_CODE'],
            columns='METRIC_CODE',
            values='METRIC_VALUE',
            aggfunc='first'
        ).reset_index()
        
        # Rename columns for easier access
        df_pivot.columns.name = None
        df_pivot = df_pivot.rename(columns={'SECURITY_CODE': 'symbol'})
        
        # Sort by date
        df_pivot = df_pivot.sort_values('date')
        return df_pivot
    except Exception:
        # Fallback to mock if any read error
        return create_mock_security_data(symbol, start_year)


@st.cache_data(ttl=300, max_entries=32)  # Cache for 5 minutes to allow fresh Q3/2025 data
def load_securities_valuation_data(symbol, start_year):
    """Load securities valuation data from PE/PB parquet files"""
    try:
        # Use DuckDB for efficient selective loading
        conn = duckdb.connect()
        
        # Load PE data with filtering
        pe_path = get_data_path('DATA/processed/valuation/pe/pe_historical_all_symbols_final.parquet')
        pe_data = conn.execute("""
            SELECT * FROM read_parquet(?)
            WHERE symbol = ? AND TRY_CAST(date AS DATE) >= ?
            ORDER BY date
        """, [str(pe_path), symbol, f'{start_year}-01-01']).fetchdf()
        
        if not pe_data.empty:
            pe_data['date'] = pd.to_datetime(pe_data['date'])
        
        # Load PB data with filtering
        pb_path = get_data_path('DATA/processed/valuation/pb/pb_historical_all_symbols_final.parquet')
        pb_data = conn.execute("""
            SELECT * FROM read_parquet(?)
            WHERE symbol = ? AND TRY_CAST(date AS DATE) >= ?
            ORDER BY date
        """, [str(pb_path), symbol, f'{start_year}-01-01']).fetchdf()
        
        if not pb_data.empty:
            pb_data['date'] = pd.to_datetime(pb_data['date'])
        
        return {
            'pe': pe_data,
            'pb': pb_data
        }
    except Exception as e:
        st.error(f"Error loading valuation data: {e}")
        # Fallback to mock data
        return create_mock_valuation_data(symbol, start_year)


def render_overview_tab(securities_data):
    """Render Overview tab with all charts in one page using PyEcharts with 2x2 grid"""
    if securities_data.empty:
        st.warning("No securities data available")
        return
    
    df = securities_data.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    xs = df['date'].dt.strftime('%Y-%m-%d').tolist()
    
    # Section 1: Income Statement - Bar + MA4 line (2x2 grid)
    st.markdown("### Income Statement & Operating Metrics")

    # Prepare quarter labels
    df_quarters = df.copy()
    if 'date' in df_quarters.columns:
        df_quarters['quarter'] = pd.to_datetime(df_quarters['date']).dt.to_period('Q').apply(lambda x: f"Q{x.quarter}/{x.year}")
    else:
        df_quarters['quarter'] = pd.to_datetime(df_quarters.index).to_period('Q').apply(lambda x: f"Q{x.quarter}/{x.year}")

    # Color palettes
    bar_colors = ["#2E8B57", "#4682B4", "#CD853F", "#DAA520", "#8B4513", "#A0522D"]
    # High-contrast line colors to bars
    line_colors = ["#000000", "#004B50", "#3D2C8D", "#00695C", "#4A148C", "#1B5E20"]

    # Securities-specific income statement items
    is_items = [
        ('REVENUE', 'Revenue'),
        ('GROSS_PROFIT', 'Gross Profit'),
        ('OPERATING_INCOME', 'Operating Income'),
        ('NET_INCOME', 'Net Income'),
        ('TOTAL_ASSETS', 'Total Assets'),
        ('EQUITY', 'Equity'),
    ]

    def build_is_chart(idx: int, metric: str, title: str):
        quarters = df_quarters['quarter'].tolist()
        series = df_quarters.get(metric, pd.Series([None]*len(df_quarters)))
        values = series.infer_objects(copy=False).fillna(0).astype(float).tolist()

        bar = (
            Bar()
            .add_xaxis(quarters)
            .add_yaxis(
                title,
                values,
                itemstyle_opts=opts.ItemStyleOpts(color=bar_colors[idx % len(bar_colors)], opacity=0.8),
                label_opts=opts.LabelOpts(is_show=False)
            )
            .extend_axis(
                yaxis=opts.AxisOpts(
                    name="",
                    type_="value",
                    axislabel_opts=opts.LabelOpts(is_show=False),
                    axisline_opts=opts.AxisLineOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False)
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=title, 
                    pos_left="center", 
                    padding=[14,0,14,0],
                    title_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif', font_size=18, font_weight='bold')
                ),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(font_family='Nunito, sans-serif', rotate=45),
                    name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                ),
                yaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(
                        formatter=JsCode("function(v){return Number(v).toFixed(0);}"),
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
                    textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                ),
            )
        )
        return bar

    # Render in 2x2 grid
    # First row: 2 charts
    cols_top = st.columns(2)
    for local_i, (idx, (metric, title)) in enumerate(list(enumerate(is_items))[:2]):
        chart = build_is_chart(idx, metric, title)
        with cols_top[local_i]:
            st_pyecharts(chart, key=f"securities_is_{metric}")

    # Second row: remaining charts
    remaining_items = list(enumerate(is_items))[2:]
    if remaining_items:
        cols_bottom = st.columns(2)
        for local_i, (idx, (metric, title)) in enumerate(remaining_items[:2]):  # Limit to 2 charts per row
            chart = build_is_chart(idx, metric, title)
            with cols_bottom[local_i]:
                st_pyecharts(chart, key=f"securities_is_{metric}")
        
        # If there are more than 4 charts, create additional rows
        if len(remaining_items) > 2:
            extra_items = list(enumerate(is_items))[4:]
            if extra_items:
                cols_extra = st.columns(2)
                for local_i, (idx, (metric, title)) in enumerate(extra_items[:2]):  # Limit to 2 charts per row
                    chart = build_is_chart(idx, metric, title)
                    with cols_extra[local_i]:
                        st_pyecharts(chart, key=f"securities_is_{metric}")
    
    st.markdown("---")
    
    # Section 2: Profitability Metrics (2x2 grid)
    st.markdown("### Key Performance Metrics")
    profitability_metrics = [
        ('ROE', 'ROE %', '#d62728'),
        ('ROA', 'ROA %', '#17becf'),
        ('GROSS_MARGIN', 'Gross Margin %', '#8c564b'),
        ('NET_MARGIN', 'Net Margin %', '#e377c2'),
    ]
    plotted = 0
    # First row: 2 charts
    cols_top = st.columns(2)
    for i, (col_name, title, color) in enumerate(profitability_metrics[:2]):
        with cols_top[i]:
            if _safe_plot_pyecharts(df, col_name, xs, title, color, "securities_profitability"):
                plotted += 1
    
    # Second row: remaining charts
    if len(profitability_metrics) > 2:
        cols_bottom = st.columns(2)
        for i, (col_name, title, color) in enumerate(profitability_metrics[2:4]):  # Limit to 2 charts per row
            with cols_bottom[i]:
                if _safe_plot_pyecharts(df, col_name, xs, title, color, "securities_profitability"):
                    plotted += 1
    if plotted == 0:
        st.info("No profitability metrics available.")
    
    st.markdown("---")
    
    # Section 3: Efficiency Metrics (2x2 grid)
    st.markdown("### Efficiency Metrics")
    efficiency_metrics = [
        ('ASSET_TURNOVER', 'Asset Turnover', '#ff7f0e'),
        ('EQUITY_TURNOVER', 'Equity Turnover', '#2ca02c'),
        ('INVENTORY_TURNOVER', 'Inventory Turnover', '#8c564b'),
    ]
    plotted = 0
    # First row: 2 charts
    cols_top = st.columns(2)
    for i, (col_name, title, color) in enumerate(efficiency_metrics[:2]):
        with cols_top[i]:
            if _safe_plot_pyecharts(df, col_name, xs, title, color, "securities_efficiency"):
                plotted += 1
    
    # Second row: remaining charts
    if len(efficiency_metrics) > 2:
        cols_bottom = st.columns(2)
        for i, (col_name, title, color) in enumerate(efficiency_metrics[2:4]):  # Limit to 2 charts per row
            with cols_bottom[i]:
                if _safe_plot_pyecharts(df, col_name, xs, title, color, "securities_efficiency"):
                    plotted += 1
    if plotted == 0:
        st.info("No efficiency metrics available.")
    
    st.markdown("---")
    
    # Section 4: Growth Analysis (2x2 grid)
    st.markdown("### Growth Analysis")
    
    # Calculate growth metrics from available data
    growth_metrics = []
    
    # Check for revenue and calculate growth
    if 'REVENUE' in df.columns:
        df['revenue_gr'] = df['REVENUE'].pct_change(periods=4, fill_method=None) * 100  # Quarterly YoY growth
        growth_metrics.append(('revenue_gr', 'Revenue Growth % (YoY)', '#1f77b4'))
    
    # Check for net_income and calculate growth
    if 'NET_INCOME' in df.columns:
        df['net_income_gr'] = df['NET_INCOME'].pct_change(periods=4, fill_method=None) * 100  # Quarterly YoY growth
        growth_metrics.append(('net_income_gr', 'Net Income Growth % (YoY)', '#ff7f0e'))
    
    # Check for total_assets and calculate growth
    if 'TOTAL_ASSETS' in df.columns:
        df['total_assets_gr'] = df['TOTAL_ASSETS'].pct_change(periods=4, fill_method=None) * 100  # Quarterly YoY growth
        growth_metrics.append(('total_assets_gr', 'Asset Growth % (YoY)', '#2ca02c'))
    
    # Check for equity and calculate growth
    if 'EQUITY' in df.columns:
        df['equity_gr'] = df['EQUITY'].pct_change(periods=4, fill_method=None) * 100  # Quarterly YoY growth
        growth_metrics.append(('equity_gr', 'Equity Growth % (YoY)', '#9467bd'))
    
    if growth_metrics:
        plotted = 0
        # First row: 2 charts
        cols_top = st.columns(2)
        for i, (col_name, title, color) in enumerate(growth_metrics[:2]):
            with cols_top[i]:
                if _safe_plot_pyecharts(df, col_name, xs, title, color, "securities_growth"):
                    plotted += 1
        
        # Second row: remaining charts
        if len(growth_metrics) > 2:
            cols_bottom = st.columns(2)
            for i, (col_name, title, color) in enumerate(growth_metrics[2:4]):  # Limit to 2 charts per row
                with cols_bottom[i]:
                    if _safe_plot_pyecharts(df, col_name, xs, title, color, "securities_growth"):
                        plotted += 1
        
        # Additional rows if more than 4 charts
        if len(growth_metrics) > 4:
            remaining_metrics = growth_metrics[4:]
            for row_start in range(0, len(remaining_metrics), 2):
                cols_extra = st.columns(2)
                for i, (col_name, title, color) in enumerate(remaining_metrics[row_start:row_start+2]):
                    with cols_extra[i]:
                        if _safe_plot_pyecharts(df, col_name, xs, title, color, "securities_growth"):
                            plotted += 1
        
        if plotted == 0:
            st.info("No growth metrics could be calculated from available data.")
    else:
        st.info("No base metrics available to calculate growth rates.")


def render_securities_metric_tab(selected_symbol, start_year):
    """Render Securities Metric tab with detailed analysis"""
    st.subheader("📊 Securities Detailed Metrics")
    st.info(f"Detailed metrics analysis for {selected_symbol} - Coming soon!")
    
    # Placeholder for detailed securities metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Revenue (TTM)", "1,234.5 B", "12.5%")
        st.metric("Net Income (TTM)", "234.1 B", "8.3%")
    
    with col2:
        st.metric("ROE", "18.5%", "2.1%")
        st.metric("ROA", "12.3%", "1.8%")


def render_valuation_tab(valuation_data, selected_symbol, start_year):
    """Render Valuation tab with comprehensive PE/PB analysis"""
    st.subheader("Valuation Analysis")
    
    # Check if valuation_data is a dict (real data) or DataFrame (mock data)
    if isinstance(valuation_data, dict):
        pe_data = valuation_data.get('pe', pd.DataFrame())
        pb_data = valuation_data.get('pb', pd.DataFrame())
        
        # Check if we have any data
        if pe_data.empty and pb_data.empty:
            st.warning("No valuation data available")
            return
        
        # Display latest data info in one compact line
        pe_date_str = ""
        pb_date_str = ""
        
        if not pe_data.empty:
            latest_pe_date = pe_data['date'].max()
            pe_date_str = f"PE: {latest_pe_date.strftime('%Y-%m-%d')}"
            
            # Check if data is recent (within last 30 days)
            days_old = (pd.Timestamp.now() - latest_pe_date).days
            if days_old > 30:
                st.warning(f"⚠️ Data is {days_old} days old. {selected_symbol} may have been delisted or suspended trading.")
        
        if not pb_data.empty:
            latest_pb_date = pb_data['date'].max()
            pb_date_str = f"PB: {latest_pb_date.strftime('%Y-%m-%d')}"
        
    else:
        # Handle DataFrame case (mock data)
        if valuation_data.empty:
            st.warning("No valuation data available")
            return
        st.info("📊 Using mock data for demonstration")
    
    # Get securities list from sidebar (same as in render_securities_dashboard)
    securities_list = get_security_symbols()
    
    # Get metric_type from sidebar session state
    metric_type = st.session_state.get('securities_metric_type', 'P/E')
    
    # Get metric column
    metric_col = "pe_ratio" if metric_type == "P/E" else "pb_ratio"
    
    # Load real PE/PB data for analysis
    try:
        pe_file = get_data_path("DATA/processed/valuation/pe/pe_historical_all_symbols_final.parquet")
        pb_file = get_data_path("DATA/processed/valuation/pb/pb_historical_all_symbols_final.parquet")
        
        file_path = pe_file if metric_type == "P/E" else pb_file
        if not os.path.exists(file_path):
            st.warning(f"Valuation data file not found: {file_path}")
            return
        
        df = pd.read_parquet(file_path)
        # Filter to only allowed securities
        df = df[df['symbol'].isin(ALLOWED_SECURITIES)]
        # Normalize datetime like company_dashboard_pyecharts: enforce datetime, drop TZ, day-level
        df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True).dt.tz_localize(None).dt.normalize()
        
        
        # Chart 1: Valuation Distribution Candle Chart
        
        # Use securities list from sidebar (filtered securities)
        securities_symbols = securities_list
        
        # Create candle chart
        fig_candle = go.Figure()
        
        # Prepare data for each ticker
        valid_tickers = []
        for ticker in securities_symbols:
            ticker_data = df[df['symbol'] == ticker][metric_col].dropna()
            
            if len(ticker_data) < 20:  # Skip if insufficient data
                continue
            
            valid_tickers.append(ticker)
            
            # Calculate percentiles with smart outlier handling
            median_val = ticker_data.median()
            
            # Only exclude extreme outliers (values more than 5x the median)
            if metric_type == "P/E":
                # For P/E, be more aggressive with outlier removal
                upper_limit = min(100, median_val * 5) if median_val > 0 else 100
                clean_data = ticker_data[ticker_data <= upper_limit]
            else:
                # For P/B, be more lenient
                upper_limit = median_val * 4 if median_val > 0 else 10
                clean_data = ticker_data[ticker_data <= upper_limit]
            
            # Ensure we still have enough data
            if len(clean_data) < 20:
                clean_data = ticker_data  # Use original if too much was filtered
            
            # Calculate percentiles for candle
            p5 = clean_data.quantile(0.05)
            p25 = clean_data.quantile(0.25)
            p50 = clean_data.quantile(0.50)
            p75 = clean_data.quantile(0.75)
            p95 = clean_data.quantile(0.95)
            
            # Get current value
            current_val = ticker_data.iloc[-1] if len(ticker_data) > 0 else None
            
            # Add candlestick with light grey color
            fig_candle.add_trace(go.Candlestick(
                x=[ticker],
                open=[round(p25, 2)],
                high=[round(p95, 2)],  # Use p95 for upper wick
                low=[round(p5, 2)],    # Use p5 for lower wick
                close=[round(p75, 2)],
                name=ticker,
                showlegend=False,
                increasing_line_color='lightgrey',
                decreasing_line_color='lightgrey',
                hovertext=f"{ticker}<br>Median: {p50:.2f}"
            ))
            
            # Add current value as scatter point with smaller size and custom color
            if current_val and not pd.isna(current_val):
                # Calculate percentile
                percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100
                
                fig_candle.add_trace(go.Scatter(
                    x=[ticker],
                    y=[current_val],
                    mode='markers',
                    marker=dict(size=8, color='#A95C68', symbol='circle'),
                    name=f"{ticker} Current",
                    showlegend=False,
                    hovertemplate=(
                        f"<b>{ticker}</b><br>" +
                        f"Current: {current_val:.2f}<br>" +
                        f"Percentile: {percentile:.1f}%<br>" +
                        f"Median: {p50:.2f}<br>" +
                        "<extra></extra>"
                    )
                ))
        
        # Update layout
        fig_candle.update_layout(
            **get_plotly_font_config(),
            title=f"{metric_type} Distribution - Securities Sector",
            xaxis_title="Securities",
            yaxis_title=f"{metric_type} Ratio",
            height=500,
            hovermode='x unified',
            xaxis=dict(
                categoryorder='array',
                categoryarray=valid_tickers,  # Maintain order
                rangeslider=dict(visible=False),  # Disable range slider
                fixedrange=True  # Disable zoom and pan
            ),
            yaxis=dict(
                fixedrange=True  # Disable zoom and pan on y-axis too
            ),
            dragmode=False  # Disable all drag interactions
        )
        
        st.plotly_chart(fig_candle, config=PLOTLY_CONFIG)
        
        # Use selected_symbol from sidebar navigation
        selected_ticker = selected_symbol
        
        # Calculate date filter based on start_year from sidebar (normalize, avoid TZ issues)
        start_date = pd.Timestamp(f"{start_year}-01-01", tz="UTC").tz_localize(None).normalize()
        
        # Display charts side by side
        col_chart1, col_chart2 = st.columns([6, 6])
        
        # Chart 2: Historical Valuation Time Series
        with col_chart1:
            # Filter data for selected ticker and date range
            # Normalize dates same as above to ensure latest date appears
            df_norm = df.copy()
            df_norm['date'] = pd.to_datetime(df_norm['date'], errors='coerce', utc=True).dt.tz_localize(None).dt.normalize()
            ticker_df = df_norm[(df_norm['symbol'] == selected_ticker) & (df_norm['date'] >= start_date)].copy()
            # Safety: if filter yields empty due to any parsing mismatch, fallback to full symbol data
            if ticker_df.empty:
                symbol_all = df_norm[df_norm['symbol'] == selected_ticker].copy().sort_values('date')
                if not symbol_all.empty:
                    # use last 730 days (2 years) as sensible default window
                    last_date = symbol_all['date'].max()
                    fallback_start = (last_date - pd.Timedelta(days=730)).normalize()
                    ticker_df = symbol_all[symbol_all['date'] >= fallback_start].copy()
            ticker_df = ticker_df.sort_values('date')
            
            if len(ticker_df) > 0:
                # Calculate statistics
                current_val = ticker_df[metric_col].iloc[-1]
                mean_val = ticker_df[metric_col].mean()
                std_val = ticker_df[metric_col].std()
                
                # Create figure
                fig_ts = go.Figure()
                
                # Add main valuation line with custom color
                fig_ts.add_trace(go.Scatter(
                    x=ticker_df['date'],
                    y=ticker_df[metric_col],
                    mode='lines',
                    name=f'{metric_type} Ratio',
                    line=dict(color='#A95C68', width=2)
                ))
                
                # Add mean line
                fig_ts.add_trace(go.Scatter(
                    x=[ticker_df['date'].min(), ticker_df['date'].max()],
                    y=[mean_val, mean_val],
                    mode='lines',
                    name='Mean',
                    line=dict(color='black', width=2, dash='solid')
                ))
                
                # Add +1 SD line
                fig_ts.add_trace(go.Scatter(
                    x=[ticker_df['date'].min(), ticker_df['date'].max()],
                    y=[mean_val + std_val, mean_val + std_val],
                    mode='lines',
                    name='+1 SD',
                    line=dict(color='red', width=1, dash='dash')
                ))
                
                # Add -1 SD line
                fig_ts.add_trace(go.Scatter(
                    x=[ticker_df['date'].min(), ticker_df['date'].max()],
                    y=[mean_val - std_val, mean_val - std_val],
                    mode='lines',
                    name='-1 SD',
                    line=dict(color='green', width=1, dash='dash')
                ))
                
                # Add current value marker as small grey dot
                fig_ts.add_trace(go.Scatter(
                    x=[ticker_df['date'].max()],
                    y=[current_val],
                    mode='markers',
                    name='Current',
                    marker=dict(size=8, color='grey', symbol='circle')
                ))
                
                # Update layout
                fig_ts.update_layout(
                    **get_plotly_font_config(),
                    title=f"{selected_ticker} - {metric_type} Trend",
                    xaxis_title="Date",
                    yaxis_title=f"{metric_type} Ratio",
                    height=400,
                    hovermode='x unified',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig_ts, config=PLOTLY_CONFIG)
                
                # Show statistics below the chart
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.metric("Current", f"{current_val:.2f}" if current_val else "N/A")
                    st.metric("Mean", f"{mean_val:.2f}")
                with col_stat2:
                    st.metric("Std Dev", f"{std_val:.2f}")
                    z_score = (current_val - mean_val) / std_val if std_val > 0 else 0
                    st.metric("Z-Score", f"{z_score:.2f}")
            else:
                st.warning(f"No data available for {selected_ticker}")
        
        # Chart 3: Valuation Distribution Histogram
        with col_chart2:
            # Generate histogram data for the same selected ticker
            ticker_data = df[df['symbol'] == selected_ticker][metric_col].dropna()
            
            if len(ticker_data) > 0:
                # Create histogram
                fig_hist = go.Figure()
                
                # Create histogram bins
                hist, bin_edges = np.histogram(ticker_data, bins=15)  # Reduce bins for better readability
                bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                # Create cleaner bin labels with rounded values
                bin_labels = []
                for i in range(len(bin_edges)-1):
                    low = round(bin_edges[i], 1)
                    high = round(bin_edges[i+1], 1)
                    if low == high:
                        bin_labels.append(f"{low:.1f}")
                    else:
                        bin_labels.append(f"{low:.1f}-{high:.1f}")
                
                # Find current value bin
                current_val = ticker_data.iloc[-1]
                current_bin_idx = None
                for i, (low, high) in enumerate(zip(bin_edges[:-1], bin_edges[1:])):
                    if low <= current_val < high:
                        current_bin_idx = i
                        break
                
                # Create bar colors - highlight current bin
                bar_colors = ['#FFC0CB'] * len(hist)
                if current_bin_idx is not None:
                    bar_colors[current_bin_idx] = '#A95C68'
                
                # Add bars
                fig_hist.add_trace(go.Bar(
                    x=bin_labels,
                    y=hist,
                    marker_color=bar_colors,
                    text=hist,
                    textposition='auto',
                    showlegend=False,
                    hovertemplate='Range: %{x}<br>Count: %{y}<extra></extra>'
                ))
                
                # Calculate percentile
                percentile = np.sum(ticker_data <= current_val) / len(ticker_data) * 100
                
                # Update layout
                fig_hist.update_layout(
                    **get_plotly_font_config(),
                    title=dict(
                        text=f"{selected_ticker} - {metric_type} Distribution<br>" +
                             f"<sub>Current: {current_val:.2f} (CDF: {percentile:.1f}%)</sub>",
                        x=0.5,
                        xanchor='center'
                    ),
                    xaxis_title=f"{metric_type} Range",
                    yaxis_title="Frequency",
                    height=400,
                    showlegend=False,
                    hovermode='x',
                    bargap=0.1,
                    xaxis=dict(
                        tickangle=45,  # Rotate labels for better readability
                        tickfont=dict(size=10),
                        title_font=dict(size=12)
                    ),
                    yaxis=dict(
                        tickfont=dict(size=10),
                        title_font=dict(size=12)
                    )
                )
                
                # Display histogram
                st.plotly_chart(fig_hist, config=PLOTLY_CONFIG)
                
                # Show distribution statistics below the histogram
                col_dist1, col_dist2 = st.columns(2)
                with col_dist1:
                    st.metric("Current Value", f"{current_val:.2f}")
                    st.metric("Percentile (CDF)", f"{percentile:.1f}%")
                with col_dist2:
                    st.metric("Median", f"{ticker_data.median():.2f}")
                    st.metric("Data Points", len(ticker_data))
            else:
                st.info(f"Insufficient data to generate histogram for {selected_ticker}")
        
        # Table: Valuation Statistics Table
        st.markdown("---")
        st.subheader("Valuation Statistics Summary")
        
        # Prepare statistics table (limit to securities)
        stats_data = []
        for ticker in securities_symbols:
            ticker_data = df[df['symbol'] == ticker][metric_col].dropna()
            if len(ticker_data) > 0:
                current_val = ticker_data.iloc[-1]
                median_val = ticker_data.median()
                percentile = np.sum(ticker_data <= current_val) / len(ticker_data) * 100
                
                # Determine status based on percentile (more robust)
                if percentile <= 10:
                    status = "Very Cheap"
                elif percentile <= 25:
                    status = "Cheap"
                elif percentile <= 75:
                    status = "Fair"
                elif percentile <= 90:
                    status = "Expensive"
                else:
                    status = "Very Expensive"
                
                stats_data.append({
                    'Ticker': ticker,
                    'Current': current_val,
                    'Median': median_val,
                    'Percentile': percentile,
                    'Status': status
                })
        
        if stats_data:
            stats_df = pd.DataFrame(stats_data)
            
            # Create interactive table using Plotly
            table_df = stats_df.copy()
            
            # Prepare formatted values for display
            formatted_current = table_df['Current'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
            formatted_median = table_df['Median'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
            formatted_percentile = table_df['Percentile'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
            
            # Prepare colors for status column
            status_colors = []
            for status in table_df['Status']:
                if status == "Very Cheap":
                    status_colors.append('#AFE1AF')
                elif status == "Cheap":
                    status_colors.append('#7FFFD4')
                elif status == "Fair":
                    status_colors.append('#FFC0CB')
                elif status == "Expensive":
                    status_colors.append('#D8BFD8')
                elif status == "Very Expensive":
                    status_colors.append('#A95C68')
                else:
                    status_colors.append('white')
            
            # Create the main table figure
            fig_table = go.Figure(data=[go.Table(
                header=dict(
                    values=['Ticker', 'Current', 'Median', 'Percentile', 'Status'],
                    fill_color='#A95C68',
                    font=dict(color='white', size=12),
                    align='left',
                    height=30
                ),
                cells=dict(
                    values=[
                        table_df['Ticker'],
                        formatted_current,
                        formatted_median,
                        formatted_percentile,
                        table_df['Status']
                    ],
                    fill_color=[
                        ['white'] * len(table_df),  # Ticker column
                        ['white'] * len(table_df),  # Current column
                        ['white'] * len(table_df),  # Median column
                        ['white'] * len(table_df),  # Percentile column
                        status_colors  # Status column with custom colors
                    ],
                    align='left',
                    height=25,
                    font=dict(size=13)
                )
            )])
            
            fig_table.update_layout(
                **get_plotly_font_config(),
                height=600,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            
            st.plotly_chart(fig_table, config=PLOTLY_CONFIG)
        else:
            st.info("No securities data available for statistics table")
    
    except Exception as e:
        st.error(f"Error loading valuation data: {e}")
        st.info("Please check if the valuation data files exist and are accessible.")
    
    # Additional dotplot analysis
    st.markdown("---")
    render_pe_pb_dotplot(valuation_data, selected_symbol, start_year)


def render_pe_pb_dotplot(valuation_data, selected_symbol, start_year):
    """Render PE/PB candlestick chart for securities stocks"""
    
    # Get metric_type from sidebar session state
    metric_type = st.session_state.get('securities_metric_type', 'P/E')
    st.caption(f"Historical trend analysis for {selected_symbol}")
    render_securities_historical_trend(selected_symbol, metric_type, start_year)

    st.markdown("---")
    st.subheader(f"{metric_type} Distribution - Securities Sector")
    
    # Load real PE/PB data for candlestick chart
    securities = get_security_symbols()
    
    # Create candlestick chart
    fig_candle = go.Figure()
    
    valid_tickers = []
    
    # Load real data
    try:
        if metric_type == "P/E":
            # Try to load latest PE data
            pe_files = [
                get_data_path("DATA/processed/valuation/pe/pe_historical_all_symbols_final.parquet")
            ]
            
            all_data = None
            for pe_file in pe_files:
                try:
                    df = pd.read_parquet(pe_file)
                    if 'symbol' in df.columns:
                        # Filter to only allowed securities
                        df = df[df['symbol'].isin(ALLOWED_SECURITIES)]
                        all_data = df
                        break
                except:
                    continue
                    
        else:  # P/B
            pb_file = get_data_path("DATA/processed/valuation/pb/pb_historical_all_symbols_final.parquet")
            all_data = pd.read_parquet(pb_file)
            # Filter to only allowed securities
            if 'symbol' in all_data.columns:
                all_data = all_data[all_data['symbol'].isin(ALLOWED_SECURITIES)]
        
        # Prepare data for each security
        for ticker in securities:
            if all_data is not None and 'symbol' in all_data.columns:
                # Filter data for this security
                security_data = all_data[all_data['symbol'] == ticker].copy()
                
                if len(security_data) > 0:
                    if metric_type == "P/E":
                        ticker_data = security_data['pe_ratio'].dropna()
                    else:
                        ticker_data = security_data['pb_ratio'].dropna()
                else:
                    # No real data, skip this security
                    continue
            else:
                # Fallback to mock data
                np.random.seed(hash(ticker) % 1000)
                if metric_type == "P/E":
                    ticker_data = pd.Series(np.random.normal(15, 5, 100))
                    ticker_data = ticker_data[ticker_data > 0]
                else:
                    ticker_data = pd.Series(np.random.normal(2.5, 0.8, 100))
                    ticker_data = ticker_data[ticker_data > 0]
        
            if len(ticker_data) < 20:
                continue
                
            valid_tickers.append(ticker)
            
            # Calculate percentiles with smart outlier handling
            median_val = ticker_data.median()
            
            # Only exclude extreme outliers
            if metric_type == "P/E":
                upper_limit = min(100, median_val * 4) if median_val > 0 else 100
                clean_data = ticker_data[ticker_data <= upper_limit]
            else:
                upper_limit = min(8.0, median_val * 3.0) if median_val > 0 else 8.0
                clean_data = ticker_data[ticker_data <= upper_limit]
            
            # Ensure we still have enough data
            if len(clean_data) < 20:
                clean_data = ticker_data
            
            # Calculate percentiles for candlestick
            p5 = clean_data.quantile(0.05)
            p25 = clean_data.quantile(0.25)
            p50 = clean_data.quantile(0.50)
            p75 = clean_data.quantile(0.75)
            p95 = clean_data.quantile(0.95)
            
            # Get current value (latest)
            current_val = ticker_data.iloc[-1] if len(ticker_data) > 0 else None
            
            # Add candlestick with light grey color
            fig_candle.add_trace(go.Candlestick(
                x=[ticker],
                open=[round(p25, 2)],
                high=[round(p95, 2)],  # Use p95 for upper wick
                low=[round(p5, 2)],    # Use p5 for lower wick
                close=[round(p75, 2)],
                name=ticker,
                showlegend=False,
                increasing_line_color='lightgrey',
                decreasing_line_color='lightgrey',
                hovertext=f"{ticker}<br>Median: {p50:.2f}"
            ))
            
            # Add current value as scatter point
            if current_val and not pd.isna(current_val):
                # Calculate percentile
                percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100
                
                fig_candle.add_trace(go.Scatter(
                    x=[ticker],
                    y=[current_val],
                    mode='markers',
                    marker=dict(size=8, color='#2E8B57', symbol='circle'),
                    name=f"{ticker} Current",
                    showlegend=False,
                    hovertemplate=(
                        f"<b>{ticker}</b><br>" +
                        f"Current: {current_val:.2f}<br>" +
                        f"Percentile: {percentile:.1f}%<br>" +
                        f"Median: {p50:.2f}<br>" +
                        "<extra></extra>"
                    )
                ))
            
    except Exception as e:
        st.error(f"Error loading {metric_type} data: {e}")
        st.info("Using mock data as fallback")
        
        # Fallback to mock data for all securities
        for ticker in securities:
            np.random.seed(hash(ticker) % 1000)
            if metric_type == "P/E":
                ticker_data = pd.Series(np.random.normal(15, 5, 100))
                ticker_data = ticker_data[ticker_data > 0]
            else:
                ticker_data = pd.Series(np.random.normal(2.5, 0.8, 100))
                ticker_data = ticker_data[ticker_data > 0]
            
            if len(ticker_data) < 20:
                continue
                
            valid_tickers.append(ticker)
            
            # Calculate percentiles with smart outlier handling
            median_val = ticker_data.median()
            
            # Only exclude extreme outliers
            if metric_type == "P/E":
                upper_limit = min(100, median_val * 4) if median_val > 0 else 100
                clean_data = ticker_data[ticker_data <= upper_limit]
            else:
                upper_limit = min(8.0, median_val * 3.0) if median_val > 0 else 8.0
                clean_data = ticker_data[ticker_data <= upper_limit]
            
            # Ensure we still have enough data
            if len(clean_data) < 20:
                clean_data = ticker_data
            
            # Calculate percentiles for candlestick
            p5 = clean_data.quantile(0.05)
            p25 = clean_data.quantile(0.25)
            p50 = clean_data.quantile(0.50)
            p75 = clean_data.quantile(0.75)
            p95 = clean_data.quantile(0.95)
            
            # Get current value (latest)
            current_val = ticker_data.iloc[-1] if len(ticker_data) > 0 else None
            
            # Add candlestick with light grey color
            fig_candle.add_trace(go.Candlestick(
                x=[ticker],
                open=[round(p25, 2)],
                high=[round(p95, 2)],  # Use p95 for upper wick
                low=[round(p5, 2)],    # Use p5 for lower wick
                close=[round(p75, 2)],
                name=ticker,
                showlegend=False,
                increasing_line_color='lightgrey',
                decreasing_line_color='lightgrey',
                hovertext=f"{ticker}<br>Median: {p50:.2f}"
            ))
            
            # Add current value as scatter point
            if current_val and not pd.isna(current_val):
                # Calculate percentile
                percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100
                
                fig_candle.add_trace(go.Scatter(
                    x=[ticker],
                    y=[current_val],
                    mode='markers',
                    marker=dict(size=8, color='#2E8B57', symbol='circle'),
                    name=f"{ticker} Current",
                    showlegend=False,
                    hovertemplate=(
                        f"<b>{ticker}</b><br>" +
                        f"Current: {current_val:.2f}<br>" +
                        f"Percentile: {percentile:.1f}%<br>" +
                        f"Median: {p50:.2f}<br>" +
                        "<extra></extra>"
                    )
                ))
    
    # Update layout
    fig_candle.update_layout(
        **get_plotly_font_config(),
        title=f"{metric_type} Distribution - Securities Sector",
        xaxis_title="Securities",
        yaxis_title=f"{metric_type} Ratio",
        height=500,
        hovermode='x unified',
        xaxis=dict(
            categoryorder='array',
            categoryarray=valid_tickers,
            rangeslider=dict(visible=False),
            fixedrange=True
        ),
        yaxis=dict(fixedrange=True),
        dragmode=False
    )
    
    st.plotly_chart(fig_candle, config=PLOTLY_CONFIG)


def render_securities_historical_trend(selected_ticker, metric_type, start_year):
    """Render historical trend chart for selected security using real data"""
    
    # Load real PE/PB data
    try:
        if metric_type == "P/E":
            # Try to load latest PE data
            pe_files = [
                get_data_path("DATA/processed/valuation/pe/pe_historical_all_symbols_final.parquet")
            ]
            
            ticker_df = None
            for pe_file in pe_files:
                try:
                    df = pd.read_parquet(pe_file)
                    if 'symbol' in df.columns:
                        # Filter to only allowed securities
                        df = df[df['symbol'].isin(ALLOWED_SECURITIES)]
                        security_data = df[df['symbol'] == selected_ticker].copy()
                        if len(security_data) > 0:
                            security_data['TRADE_DATE'] = pd.to_datetime(security_data['date'])
                            security_data['VALUE'] = security_data['pe_ratio']
                            ticker_df = security_data[['TRADE_DATE', 'VALUE']].sort_values('TRADE_DATE')
                            break
                except:
                    continue
                    
        else:  # P/B
            # Load latest PB data
            pb_file = get_data_path("DATA/processed/valuation/pb/pb_historical_all_symbols_final.parquet")
            df = pd.read_parquet(pb_file)
            # Filter to only allowed securities
            if 'symbol' in df.columns:
                df = df[df['symbol'].isin(ALLOWED_SECURITIES)]
                security_data = df[df['symbol'] == selected_ticker].copy()
                if len(security_data) > 0:
                    security_data['TRADE_DATE'] = pd.to_datetime(security_data['date'])
                    security_data['VALUE'] = security_data['pb_ratio']
                    ticker_df = security_data[['TRADE_DATE', 'VALUE']].sort_values('TRADE_DATE')
        
        # Filter by start_year
        if ticker_df is not None:
            start_date = datetime(start_year, 1, 1)
            ticker_df = ticker_df[ticker_df['TRADE_DATE'] >= start_date]
            
        # If no real data found, use mock data as fallback
        if ticker_df is None or len(ticker_df) == 0:
            st.warning(f"No real {metric_type} data found for {selected_ticker}. Using simulation.")
            
            # Calculate date filter from start_year
            start_date = datetime(start_year, 1, 1)
            latest_date = datetime.now()
            
            # Create mock historical data
            dates = pd.date_range(start=start_date, end=latest_date, freq='ME')
            
            # Generate realistic historical data based on ticker
            np.random.seed(hash(selected_ticker) % 1000)
            
            if metric_type == "P/E":
                # P/E ratios with some trend - securities typically have higher P/E than banks
                base_value = 15 + hash(selected_ticker) % 8  # 15-22 range
                values = []
                current = base_value
                for i in range(len(dates)):
                    # Add some trend and volatility
                    trend = 0.02 * np.sin(i * 0.1)  # Cyclical trend
                    volatility = np.random.normal(0, 1.0)
                    current += trend + volatility
                    current = max(5, min(50, current))  # Keep in reasonable range
                    values.append(current)
            else:
                # P/B ratios with some trend - securities typically have higher P/B than banks
                base_value = 2.0 + (hash(selected_ticker) % 15) * 0.2  # 2.0 to 5.0 base
                values = []
                current = base_value
                for i in range(len(dates)):
                    # Add some trend and volatility
                    trend = 0.005 * np.sin(i * 0.1)  # Cyclical trend
                    volatility = np.random.normal(0, 0.15)  # Higher volatility for securities
                    current += trend + volatility
                    current = max(0.5, min(8.0, current))  # Realistic securities P/B range
                    values.append(current)
            
            # Create DataFrame
            ticker_df = pd.DataFrame({
                'TRADE_DATE': dates,
                'VALUE': values
            })
            
        # Create the chart
        if len(ticker_df) > 0:
            fig = go.Figure()
            
            # Add main line
            fig.add_trace(go.Scatter(
                x=ticker_df['TRADE_DATE'],
                y=ticker_df['VALUE'],
                mode='lines',
                name=f'{metric_type} Ratio',
                line=dict(color='#2E8B57', width=2)
            ))
            
            # Add mean line
            mean_val = ticker_df['VALUE'].mean()
            fig.add_trace(go.Scatter(
                x=[ticker_df['TRADE_DATE'].min(), ticker_df['TRADE_DATE'].max()],
                y=[mean_val, mean_val],
                mode='lines',
                name='Mean',
                line=dict(color='red', width=2, dash='dash')
            ))
            
            # Update layout
            fig.update_layout(
                **get_plotly_font_config(),
                title=f"{selected_ticker} - {metric_type} Historical Trend",
                xaxis_title="Date",
                yaxis_title=f"{metric_type} Ratio",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, config=PLOTLY_CONFIG)
            
            # Show statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current", f"{ticker_df['VALUE'].iloc[-1]:.2f}")
            with col2:
                st.metric("Mean", f"{mean_val:.2f}")
            with col3:
                st.metric("Min", f"{ticker_df['VALUE'].min():.2f}")
            with col4:
                st.metric("Max", f"{ticker_df['VALUE'].max():.2f}")
        else:
            st.warning(f"No data available for {selected_ticker}")
            
    except Exception as e:
        st.error(f"Error loading historical data: {e}")
        st.info("Please check if the valuation data files exist and are accessible.")


if __name__ == "__main__":
    render_securities_dashboard()
