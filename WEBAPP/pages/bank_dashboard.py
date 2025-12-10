"""
Bank Dashboard - Banking sector analysis
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
import importlib

# Add project root to Python path for imports (same pattern as technical_dashboard)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ensure Streamlit package namespace is registered (for Streamlit Cloud reloads)
streamlit_app = importlib.import_module("streamlit_app")

from WEBAPP.core.utils import get_data_path, load_custom_css, get_plotly_font_config
from WEBAPP.core.formatters import formatter, format_value, format_df_column, format_summary_data
from WEBAPP.core.display_config import format_df_for_display, format_metrics_for_display
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

# PyEcharts imports for overview
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Boxplot
from pyecharts.commons.utils import JsCode
from streamlit_echarts import st_pyecharts

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
                   itemstyle_opts=opts.ItemStyleOpts(color=color),
                   label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif', font_size=18, font_weight='bold')
            ),
            xaxis_opts=opts.AxisOpts(
                name="Date", 
                boundary_gap=True,
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
    """Safely plot PyEcharts chart with error handling"""
    try:
        if col_name not in df.columns:
            st.warning(f"Column {col_name} not found in data. Available columns: {list(df.columns)}")
            return False
        
        # Get data and handle missing values
        data = df[col_name].dropna()
        if len(data) == 0:
            st.warning(f"No data available for {col_name}. Total rows: {len(df)}, Non-null count: {df[col_name].notna().sum()}")
            return False
        
        # Ensure xs and ys have same length
        if len(xs) != len(data):
            # Truncate xs to match data length
            xs_trimmed = xs[-len(data):]
        else:
            xs_trimmed = xs
        
        # Round for display: use 2 decimals for percentage-like sections
        is_two_decimal_section = key_prefix in ("bank_margin", "bank_aq", "bank_growth")
        if is_two_decimal_section:
            ys = [round(float(v), 2) if pd.notna(v) else None for v in data.tolist()]
        else:
            ys = [round(float(v), 1) if pd.notna(v) else None for v in data.tolist()]
        
        # Create chart
        chart = build_line(xs_trimmed, ys, title, color)
        st_pyecharts(chart, key=f"{key_prefix}_{col_name}")
        return True
    except Exception as e:
        st.error(f"Error plotting {col_name}: {e}")
        return False
from WEBAPP.core.display_config import format_df_for_display, format_metrics_for_display

# New modular imports (optional wiring)
try:
    from WEBAPP.domains.banking.data_loading_bank import get_bank_symbols
except Exception:
    get_bank_symbols = None

def render_bank_dashboard():
    # Render Top Navigation
    render_top_nav()

    
    # Sidebar filters
    with st.sidebar:
        st.header("Navigation")
        
        # Symbol selection (use loader if available, else fallback list)
        bank_list = []
        if get_bank_symbols is not None:
            try:
                bank_list = get_bank_symbols() or []
            except Exception:
                bank_list = []
        if not bank_list:
            bank_list = [
                "VCB", "TCB", "BID", "CTG", "MBB", "ACB", "VPB", "HDB", "TPB", "STB",
                "SHB", "MSB", "LPB", "VIB", "OCB", "NAB", "SSB", "EIB", "VBB", "PGB"
            ]

        selected_symbol = st.selectbox(
            "Select Bank",
            options=bank_list,
            index=0
        )
        # Sync selected bank into session state for cross-tab linkage
        st.session_state.selected_bank = selected_symbol
        
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
            # Button click will trigger rerun automatically
        
        if st.button("Bank Metric",
                    type="primary" if st.session_state.get('active_tab') == "Bank Metric" else "secondary"):
            st.session_state.active_tab = "Bank Metric"
            # Button click will trigger rerun automatically
        
        if st.button("Valuation",
                    type="primary" if st.session_state.get('active_tab') == "Valuation" else "secondary"):
            st.session_state.active_tab = "Valuation"
            # Button click will trigger rerun automatically
        
        # Metric Type selection (only show in Valuation tab)
        if st.session_state.get('active_tab') == "Valuation":
            st.markdown("---")
            st.subheader("Metric Type")
            metric_type = st.selectbox(
                "Select Metric",
                options=["P/E", "P/B"],
                key="bank_metric_type_sidebar",
                label_visibility="collapsed"
            )
            st.session_state.bank_metric_type = metric_type
    
    # Initialize session state for navigation
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Overview"
    
    # Display current tab title
    tab_titles = {
        "Overview": "Overview",
        "Bank Metric": "Bank Metric", 
        "Valuation": "Valuation"
    }
    
    # Load data on-demand
    with st.spinner(f"Loading data for {selected_symbol}..."):
        bank_data = load_bank_data(selected_symbol, start_year)
        valuation_data = load_bank_valuation_data(selected_symbol, start_year)
    
    # Render content based on active tab
    if st.session_state.active_tab == "Overview":
        render_overview_tab(bank_data)
    elif st.session_state.active_tab == "Bank Metric":
        render_bank_metric_tab(selected_symbol, start_year)
    elif st.session_state.active_tab == "Valuation":
        render_valuation_tab(valuation_data, selected_symbol, start_year)

def _get_bank_parquet_path() -> Path:
    """Get bank fundamental data path using centralized config"""
    from WEBAPP.core.data_paths import get_fundamental_path
    return get_fundamental_path('bank')

@st.cache_data(ttl=300, max_entries=32)  # Cache for 5 minutes to allow fresh Q3/2025 data
def load_bank_data(symbol, start_year):
    """Load bank fundamental data using centralized config"""
    try:
        p = _get_bank_parquet_path()
        df = pd.read_parquet(str(p))
        if 'report_date' in df.columns:
            df['report_date'] = pd.to_datetime(df['report_date'])
            df['date'] = df['report_date']
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        else:
            return pd.DataFrame()
        # Filter by symbol and start_year
        if 'symbol' in df.columns:
            df = df[df['symbol'] == symbol].copy()
        df = df[df['date'].dt.year >= int(start_year)].copy()
        # Keep all columns for comprehensive analysis
        # No need to filter columns - keep all available data
        # Sort by date
        df = df.sort_values('date')
        return df
    except Exception:
        # Fallback to mock if any read error
        return create_mock_bank_data(symbol, start_year)

@st.cache_data(ttl=300, max_entries=32)  # Cache for 5 minutes to allow fresh Q3/2025 data
def load_bank_valuation_data(symbol, start_year):
    """Load bank valuation data from actual parquet files"""
    try:
        # Use DuckDB for efficient selective loading
        conn = duckdb.connect()
        
        # Load PE data with filtering
        pe_path = get_data_path('calculated_results/valuation/pe/pe_historical_all_symbols_final.parquet')
        pe_data = conn.execute("""
            SELECT * FROM read_parquet(?)
            WHERE symbol = ? AND TRY_CAST(date AS DATE) >= ?
            ORDER BY date
        """, [str(pe_path), symbol, f'{start_year}-01-01']).fetchdf()
        
        if not pe_data.empty:
            pe_data['date'] = pd.to_datetime(pe_data['date'])
        
        # Load PB data with filtering
        pb_path = get_data_path('calculated_results/valuation/pb/pb_historical_all_symbols_final.parquet')
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

def render_overview_tab(bank_data):
    """Render Overview tab with all charts in one page using PyEcharts"""
    if bank_data.empty:
        st.warning("No bank data available")
        return
    
    df = bank_data.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    xs = df['date'].dt.strftime('%Y-%m-%d').tolist()
    
    # Section 1: Income Statement - Bar + MA4 line (like company overview)
    st.markdown("### Income Statement & Operating Metrics")

    # Prepare quarter labels
    df_quarters = df.copy()
    if 'date' in df_quarters.columns:
        df_quarters['quarter'] = pd.to_datetime(df_quarters['date']).dt.to_period('Q').apply(lambda x: f"Q{x.quarter}/{x.year}")
    else:
        df_quarters['quarter'] = pd.to_datetime(df_quarters.index).to_period('Q').apply(lambda x: f"Q{x.quarter}/{x.year}")

    # Color palettes
    bar_colors = ["#A95C68", "#FFC0CB", "#D8BFD8", "#AFE1AF", "#7FFFD4", "#5F8575"]
    # High-contrast line colors to bars
    line_colors = ["#000000", "#004B50", "#3D2C8D", "#00695C", "#4A148C", "#1B5E20"]

    is_items = [
        ('nii', 'Net Interest Income'),
        ('toi', 'Total Operating Income'),
        ('ppop', 'PPOP'),
        ('pbt', 'PBT'),
        ('npatmi', 'NPATMI'),
        ('interest_income', 'Interest Income'),
    ]

    def build_is_chart(idx: int, metric: str, title: str):
        quarters = df_quarters['quarter'].tolist()
        values = df_quarters.get(metric, pd.Series([None]*len(df_quarters))).fillna(0).infer_objects(copy=False).astype(float).tolist()

        # Compute MA4 using full historical data since 2018 (not only filtered view)
        # Then align to displayed quarters and fill for continuous line
        ma4_display = []
        try:
            symbol_val = df_quarters['symbol'].iloc[0] if 'symbol' in df_quarters.columns else None
        except Exception:
            symbol_val = None
        try:
            if symbol_val:
                full_path = _get_bank_parquet_path()
                df_full = pd.read_parquet(str(full_path))
                df_full = df_full[df_full['symbol'] == symbol_val].copy()
                df_full['date'] = pd.to_datetime(df_full.get('date', df_full.get('report_date')))
                df_full = df_full.sort_values('date')
                # Use all history (from 2018+) if available
                df_full = df_full[df_full['date'].dt.year >= 2018]
                df_full['quarter'] = df_full['date'].dt.to_period('Q').apply(lambda x: f"Q{x.quarter}/{x.year}")
                if metric in df_full.columns and df_full[metric].notna().sum() > 0:
                    series_full = pd.to_numeric(df_full[metric], errors='coerce')
                    ttm_current = series_full.rolling(window=4, min_periods=4).sum()
                    ttm_prev = ttm_current.shift(4)
                    ma4_full = (ttm_current / ttm_prev - 1) * 100.0
                    # Map to displayed quarters
                    ma4_map = dict(zip(df_full['quarter'], ma4_full))
                    ma4_aligned = [ma4_map.get(q, None) for q in df_quarters['quarter'].tolist()]
                    # Interpolate for continuity across the displayed range
                    ma4_display = pd.Series(ma4_aligned, dtype=float).interpolate(limit_direction='both').tolist()
        except Exception:
            # Fallback to local df_quarters computation if full load fails
            series = pd.to_numeric(df_quarters.get(metric, pd.Series(dtype=float)), errors='coerce')
            if series is not None and len(series) >= 1:
                rolling_4q_current = series.rolling(window=4, min_periods=4).sum()
                rolling_4q_prev = rolling_4q_current.shift(4)
                ma4 = (rolling_4q_current / rolling_4q_prev - 1) * 100.0
                ma4_display = ma4.interpolate(limit_direction='both').tolist()

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
                    name="Quarter",
                    name_gap=36,
                    axislabel_opts=opts.LabelOpts(rotate=45, margin=20, font_family='Nunito, sans-serif'),
                    name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                ),
                yaxis_opts=opts.AxisOpts(
                    name="Value",
                    name_gap=28,
                    axislabel_opts=opts.LabelOpts(margin=20, font_family='Nunito, sans-serif'),
                    name_textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                ),
                legend_opts=opts.LegendOpts(
                    is_show=False,
                    textstyle_opts=opts.TextStyleOpts(font_family='Nunito, sans-serif')
                ),
            )
        )

        if ma4_display and len(ma4_display) == len(quarters):
            line = (
                Line()
                .add_xaxis(quarters)
                .add_yaxis(
                    f"{title} MA4 (YoY %)",
                    [round(float(v), 1) if pd.notna(v) else None for v in ma4_display],
                    yaxis_index=1,
                    is_smooth=True,
                    linestyle_opts=opts.LineStyleOpts(color=line_colors[idx % len(line_colors)], width=2.4),
                    symbol_size=4,
                    label_opts=opts.LabelOpts(is_show=False)
                )
            )
            # Ensure line renders on top of bars
            bar.overlap(line)
        return bar

    # Render in grid 3 + 3
    # First row: 2 charts
    cols_top = st.columns(2)
    for local_i, (idx, (metric, title)) in enumerate(list(enumerate(is_items))[:2]):
        chart = build_is_chart(idx, metric, title)
        with cols_top[local_i]:
            st_pyecharts(chart, key=f"bank_is_{metric}")

    # Second row: remaining charts
    remaining_items = list(enumerate(is_items))[2:]
    if remaining_items:
        cols_bottom = st.columns(2)
        for local_i, (idx, (metric, title)) in enumerate(remaining_items[:2]):  # Limit to 2 charts per row
            chart = build_is_chart(idx, metric, title)
            with cols_bottom[local_i]:
                st_pyecharts(chart, key=f"bank_is_{metric}")
        
        # If there are more than 4 charts, create additional rows
        if len(remaining_items) > 2:
            extra_items = list(enumerate(is_items))[4:]
            if extra_items:
                cols_extra = st.columns(2)
                for local_i, (idx, (metric, title)) in enumerate(extra_items[:2]):  # Limit to 2 charts per row
                    chart = build_is_chart(idx, metric, title)
                    with cols_extra[local_i]:
                        st_pyecharts(chart, key=f"bank_is_{metric}")
    
    st.markdown("---")
    
    # Section 2: Margins
    st.markdown("### Key Performance Metrics")
    margins = [
        ('roea_ttm', 'ROE TTM %', '#d62728'),
        ('roaa_ttm', 'ROA TTM %', '#17becf'),
        ('nim_q', 'NIM %', '#8c564b'),
        ('cir', 'Cost/Income %', '#e377c2'),
    ]
    plotted = 0
    # First row: 2 charts
    cols_top = st.columns(2)
    for i, (col_name, title, color) in enumerate(margins[:2]):
        with cols_top[i]:
            if _safe_plot_pyecharts(df, col_name, xs, title, color, "bank_margin"):
                plotted += 1
    
    # Second row: remaining charts
    if len(margins) > 2:
        cols_bottom = st.columns(2)
        for i, (col_name, title, color) in enumerate(margins[2:4]):  # Limit to 2 charts per row
            with cols_bottom[i]:
                if _safe_plot_pyecharts(df, col_name, xs, title, color, "bank_margin"):
                    plotted += 1
    if plotted == 0:
        st.info("No margin metrics available.")
    
    st.markdown("---")
    
    # Section 3: Asset Quality
    st.markdown("### Asset Quality")
    aq_items = [
        ('npl_ratio', 'NPL %', '#ff7f0e'),
        ('group2_to_total_ratio', 'Group 2 %', '#2ca02c'),
        ('llcr', 'LLR %', '#8c564b'),
    ]
    plotted = 0
    # First row: 2 charts
    cols_top = st.columns(2)
    for i, (col_name, title, color) in enumerate(aq_items[:2]):
        with cols_top[i]:
            if _safe_plot_pyecharts(df, col_name, xs, title, color, "bank_aq"):
                plotted += 1
    
    # Second row: remaining charts
    if len(aq_items) > 2:
        cols_bottom = st.columns(2)
        for i, (col_name, title, color) in enumerate(aq_items[2:4]):  # Limit to 2 charts per row
            with cols_bottom[i]:
                if _safe_plot_pyecharts(df, col_name, xs, title, color, "bank_aq"):
                    plotted += 1
    if plotted == 0:
        st.info("No asset quality metrics available.")
    
    st.markdown("---")
    
    # Section 4: Growth Analysis
    st.markdown("### Growth Analysis")
    
    # Calculate growth metrics from available data
    growth_metrics = []
    
    # Check for total_assets and calculate growth
    if 'total_assets' in df.columns:
        df['total_assets_gr'] = df['total_assets'].pct_change(periods=4, fill_method=None) * 100  # Quarterly YoY growth
        growth_metrics.append(('total_assets_gr', 'Asset Growth % (YoY)', '#1f77b4'))
    
    # Check for total_credit and calculate growth
    if 'total_credit' in df.columns:
        df['total_credit_gr'] = df['total_credit'].pct_change(periods=4, fill_method=None) * 100  # Quarterly YoY growth
        growth_metrics.append(('total_credit_gr', 'Credit Growth % (YoY)', '#ff7f0e'))
    
    # Check for customer_deposit and calculate growth
    if 'customer_deposit' in df.columns:
        df['customer_deposit_gr'] = df['customer_deposit'].pct_change(periods=4, fill_method=None) * 100  # Quarterly YoY growth
        growth_metrics.append(('customer_deposit_gr', 'Deposit Growth % (YoY)', '#2ca02c'))
    
    # Check for customer_loan and calculate growth
    if 'customer_loan' in df.columns:
        df['customer_loan_gr'] = df['customer_loan'].pct_change(periods=4, fill_method=None) * 100  # Quarterly YoY growth
        growth_metrics.append(('customer_loan_gr', 'Loan Growth % (YoY)', '#9467bd'))
    
    # Check for equity and calculate growth
    if 'equity' in df.columns:
        df['equity_gr'] = df['equity'].pct_change(periods=4, fill_method=None) * 100  # Quarterly YoY growth
        growth_metrics.append(('equity_gr', 'Equity Growth % (YoY)', '#d62728'))
    
    # Check for toi (Total Operating Income) and calculate growth
    if 'toi' in df.columns:
        df['toi_gr'] = df['toi'].pct_change(periods=4, fill_method=None) * 100  # Quarterly YoY growth
        growth_metrics.append(('toi_gr', 'Income Growth % (YoY)', '#8c564b'))
    
    if growth_metrics:
        plotted = 0
        # First row: 2 charts
        cols_top = st.columns(2)
        for i, (col_name, title, color) in enumerate(growth_metrics[:2]):
            with cols_top[i]:
                if _safe_plot_pyecharts(df, col_name, xs, title, color, "bank_growth"):
                    plotted += 1
        
        # Second row: remaining charts
        if len(growth_metrics) > 2:
            cols_bottom = st.columns(2)
            for i, (col_name, title, color) in enumerate(growth_metrics[2:4]):  # Limit to 2 charts per row
                with cols_bottom[i]:
                    if _safe_plot_pyecharts(df, col_name, xs, title, color, "bank_growth"):
                        plotted += 1
        
        # Additional rows if more than 4 charts
        if len(growth_metrics) > 4:
            remaining_metrics = growth_metrics[4:]
            for row_start in range(0, len(remaining_metrics), 2):
                cols_extra = st.columns(2)
                for i, (col_name, title, color) in enumerate(remaining_metrics[row_start:row_start+2]):
                    with cols_extra[i]:
                        if _safe_plot_pyecharts(df, col_name, xs, title, color, "bank_growth"):
                            plotted += 1
        
        if plotted == 0:
            st.info("No growth metrics could be calculated from available data.")
    else:
        st.info("No base metrics available to calculate growth rates.")


@st.cache_data(ttl=300, max_entries=32)  # Cache for 5 minutes to allow fresh Q3/2025 data
def build_bank_metrics_table(symbol: str, start_year: int, metrics_spec: list) -> pd.DataFrame:
    """Build the requested bank metrics table with YoY from real data.
    metrics_spec: list of (display_name, source_column, kind)
    """
    try:
        # Use DuckDB for efficient filtering
        from WEBAPP.core.data_paths import get_fundamental_path
        conn = duckdb.connect()
        p = get_fundamental_path('bank')
        
        df = conn.execute("""
            SELECT * FROM read_parquet(?)
            WHERE symbol = ?
            ORDER BY report_date
        """, [str(p), symbol]).fetchdf()
        
        if df.empty:
            return pd.DataFrame()
            
        # Standardize date column
        if 'report_date' in df.columns:
            df['report_date'] = pd.to_datetime(df['report_date'])
            df['date'] = df['report_date']
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        else:
            return pd.DataFrame()
        # Prepare full history for YoY baseline (from 2018 onward)
        df_full = df[df['date'].dt.year >= 2018].copy()
        df_full['year'] = df_full['date'].dt.year
        df_full['quarter'] = ((df_full['date'].dt.month - 1)//3) + 1
        df_full['quarter_label'] = df_full['year'].astype(str) + 'Q' + df_full['quarter'].astype(str)
        # Quarters to display respect start_year
        df_disp = df_full[df_full['year'] >= int(start_year)].copy()
        if df_disp.empty:
            return pd.DataFrame()
        quarters = sorted(df_disp['quarter_label'].unique().tolist(), key=lambda x: (int(x[:4]), int(x[-1])))
        # Helper to compute YoY per quarter
        def compute_yoy(series, years_back=1):
            s = series.copy()
            # Align by (year, quarter)
            s_q = s.groupby(df_full['quarter_label']).last()
            yoy_vals = {}
            for q in quarters:
                y = int(q[:4]); qu = int(q[-1])
                prev_label = f"{y-years_back}Q{qu}"
                cur = s_q.get(q)
                prev = s_q.get(prev_label)
                if y == 2018 or pd.isna(cur) or pd.isna(prev) or prev == 0:
                    yoy_vals[q] = "N/A"
                else:
                    yoy = (cur - prev) / abs(prev) * 100.0
                    yoy_vals[q] = f"{yoy:.1f}%"
            return yoy_vals
        # Build rows
        rows = []
        for display, col, kind in metrics_spec:
            row = {'KEYCODE': display}
            if kind == 'yoy':
                if col in df.columns:
                    yoy_map = compute_yoy(df[col])
                    for q in quarters:
                        row[q] = yoy_map.get(q, "N/A")
                else:
                    for q in quarters:
                        row[q] = "N/A"
            else:
                if col not in df_full.columns:
                    for q in quarters:
                        row[q] = "N/A"
                else:
                    s_q = df_full.groupby('quarter_label')[col].last()
                    for q in quarters:
                        val = s_q.get(q)
                        if pd.isna(val):
                            row[q] = "N/A"
                        else:
                            if kind == 'percent':
                                row[q] = f"{val:.1f}%"
                            else:
                                row[q] = f"{val:,.1f}" if abs(val) >= 1 else f"{val:.3f}"
            rows.append(row)
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows).set_index('KEYCODE')
    except Exception as e:
        st.error(f"Error creating bank metrics table: {e}")
        return pd.DataFrame()


def render_html_table(pivot_df: pd.DataFrame, title: str) -> None:
    """Render HTML table with styling"""
    if pivot_df.empty:
        return
    st.markdown(
        """
        <style>
        .financial-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
        .financial-table th { background-color: #fffacd; font-weight: 600; text-align: center; padding: 8px 6px; border: 1px solid #ddd; position: sticky; top: 0; z-index: 10; }
        .financial-table td { text-align: right; padding: 6px; border: 1px solid #ddd; white-space: nowrap; }
        .financial-table td:first-child { text-align: left; font-weight: 600; }
        .table-container { overflow-x: auto; border: 1px solid #ddd; border-radius: 5px; max-height: 600px; overflow-y: auto; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    html = [
        '<div class="table-container">',
        '<table class="financial-table">',
        '<thead><tr><th>KEYCODE</th>',
    ]
    for col in pivot_df.columns:
        html.append(f'<th>{col}</th>')
    html.append('</tr></thead><tbody>')
    for idx, row in pivot_df.iterrows():
        html.append(f'<tr><td>{idx}</td>')
        for v in row:
            html.append(f'<td>{v}</td>')
        html.append('</tr>')
    html.append('</tbody></table></div>')
    st.markdown(''.join(html), unsafe_allow_html=True)


def render_bank_metric_tab(symbol, start_year):
    """Render Bank Metric tab with pivot table"""
    st.subheader("Bank Metric")
    
    # Requested metrics spec: (display_name, source_column, kind)
    # kind: 'value' | 'percent' | 'yoy'
    metrics_spec = [
        ("TOI", "toi", "value"),
        ("TOI YoY", "toi", "yoy"),
        ("PPOP", "ppop", "value"),
        ("PPOP YoY", "ppop", "yoy"),
        ("Provisions", "provision_expense", "value"),
        ("Provisions YoY", "provision_expense", "yoy"),
        ("PBT", "pbt", "value"),
        ("PBT YoY", "pbt", "yoy"),
        ("NPATMI", "npatmi", "value"),
        ("NPATMI YoY", "npatmi", "yoy"),
        ("Total Credit YoY", "total_credit", "yoy"),
        ("Deposits from Customers YoY", "customer_deposit", "yoy"),
        ("CASA", "casa_ratio", "percent"),
        ("Avg. Asset Yield", "asset_yield_q", "percent"),
        ("Loan yield", "loan_yield_q", "percent"),
        ("Avg. Funding Cost", "funding_cost_q", "percent"),
        ("NIM", "nim_q", "percent"),
        ("NPL (3-5)", "npl_ratio", "percent"),
        ("Group 5 %", "group5_ratio", "percent"),
        ("LLR", "llcr", "percent"),
        ("ROAE", "roea_ttm", "percent"),
        ("ROAA", "roaa_ttm", "percent"),
    ]
    
    # Load and format data
    with st.spinner("Loading bank metric data..."):
        pivot_df = build_bank_metrics_table(symbol, start_year, metrics_spec)
    
    if pivot_df.empty:
        st.warning("No bank metric data available")
        return
    
    # Display the pivot table as HTML for clean scrolling
    render_html_table(pivot_df, "Bank Metrics")

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
    
    # Get bank list from sidebar (same as in render_bank_dashboard)
    bank_list = []
    if get_bank_symbols is not None:
        try:
            bank_list = get_bank_symbols() or []
        except Exception:
            bank_list = []
    if not bank_list:
        bank_list = [
            "VCB", "TCB", "BID", "CTG", "MBB", "ACB", "VPB", "HDB", "TPB", "STB",
            "SHB", "MSB", "LPB", "VIB", "OCB", "NAB", "SSB", "EIB", "VBB", "PGB"
        ]
    
    # Get metric_type from sidebar session state
    metric_type = st.session_state.get('bank_metric_type', 'P/E')
    
    # Get metric column
    metric_col = "pe_ratio" if metric_type == "P/E" else "pb_ratio"
    
    # Load real PE/PB data for analysis
    try:
        pe_file = get_data_path("calculated_results/valuation/pe/pe_historical_all_symbols_final.parquet")
        pb_file = get_data_path("calculated_results/valuation/pb/pb_historical_all_symbols_final.parquet")
        
        file_path = pe_file if metric_type == "P/E" else pb_file
        if not os.path.exists(file_path):
            st.warning(f"Valuation data file not found: {file_path}")
            return
        
        df = pd.read_parquet(file_path)
        # Normalize datetime like company_dashboard_pyecharts: enforce datetime, drop TZ, day-level
        df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True).dt.tz_localize(None).dt.normalize()
        
        
        # Chart 1: Valuation Distribution Candle Chart
        
        # Use bank list from sidebar (filtered 20 banks)
        bank_symbols = bank_list
        
        # Create candle chart
        fig_candle = go.Figure()
        
        # Prepare data for each ticker
        valid_tickers = []
        for ticker in bank_symbols:
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
            title=f"{metric_type} Distribution - Bank Sector",
            xaxis_title="Bank",
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
        
        # Prepare statistics table (limit to 19-20 banks)
        stats_data = []
        for ticker in bank_symbols:
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
            
            # Display the main table
            st.plotly_chart(fig_table, config=PLOTLY_CONFIG)
            
            # Summary statistics
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                cheap_count = len(stats_df[stats_df['Status'].isin(['Very Cheap', 'Cheap'])])
                st.metric("Undervalued Banks", cheap_count)
            
            with col2:
                fair_count = len(stats_df[stats_df['Status'] == 'Fair'])
                st.metric("Fairly Valued Banks", fair_count)
            
            with col3:
                expensive_count = len(stats_df[stats_df['Status'].isin(['Expensive', 'Very Expensive'])])
                st.metric("Overvalued Banks", expensive_count)
        else:
            st.warning("Insufficient data to generate statistics table")
    
    except Exception as e:
        st.error(f"Error loading valuation data: {e}")

def format_pivot_values(value, metric_name):
    """Format values based on metric type"""
    if pd.isna(value):
        return "N/A"
    
    # Currency metrics (billion VND)
    currency_metrics = ['net_interest_income', 'fee_income', 'total_income', 'total_expense',
                       'net_income', 'total_assets', 'total_liabilities', 'equity']
    
    # Percentage metrics
    percentage_metrics = ['roea_ttm', 'roaa_ttm', 'nim_q', 'cost_income_ratio', 'car_ratio']
    
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

def create_bank_pivot_table(symbol, start_year, metrics_list):
    """Build the requested bank metrics table with YoY from real data.
    metrics_list: list of (display_name, source_column, kind)
    """
    try:
        p = _get_bank_parquet_path()
        df = pd.read_parquet(str(p))
        if 'report_date' in df.columns:
            df['report_date'] = pd.to_datetime(df['report_date'])
            df['date'] = df['report_date']
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        else:
            return pd.DataFrame()
        if 'symbol' in df.columns:
            df = df[df['symbol'] == symbol].copy()
        if df.empty:
            return pd.DataFrame()
        # Prepare full history for YoY baseline (from 2018 onward)
        df_full = df[df['date'].dt.year >= 2018].copy()
        df_full['year'] = df_full['date'].dt.year
        df_full['quarter'] = ((df_full['date'].dt.month - 1)//3) + 1
        df_full['quarter_label'] = df_full['year'].astype(str) + 'Q' + df_full['quarter'].astype(str)
        # Quarters to display respect start_year
        df_disp = df_full[df_full['year'] >= int(start_year)].copy()
        if df_disp.empty:
            return pd.DataFrame()
        quarters = sorted(df_disp['quarter_label'].unique().tolist(), key=lambda x: (int(x[:4]), int(x[-1])))
        # Helper to compute YoY per quarter
        def compute_yoy(series, years_back=1):
            s = series.copy()
            # Align by (year, quarter)
            s_q = s.groupby(df_full['quarter_label']).last()
            yoy_vals = {}
            for q in quarters:
                y = int(q[:4]); qu = int(q[-1])
                prev_label = f"{y-years_back}Q{qu}"
                cur = s_q.get(q)
                prev = s_q.get(prev_label)
                if y == 2018 or pd.isna(cur) or pd.isna(prev) or prev == 0:
                    yoy_vals[q] = "N/A"
                else:
                    yoy = (cur - prev) / abs(prev) * 100.0
                    yoy_vals[q] = f"{yoy:.1f}%"
            return yoy_vals
        # Build rows
        rows = []
        for display, col, kind in metrics_list:
            row = {'KEYCODE': display}
            if kind == 'yoy':
                if col in df.columns:
                    yoy_map = compute_yoy(df[col])
                    for q in quarters:
                        row[q] = yoy_map.get(q, "N/A")
                else:
                    for q in quarters:
                        row[q] = "N/A"
            else:
                if col not in df_full.columns:
                    for q in quarters:
                        row[q] = "N/A"
                else:
                    s_q = df_full.groupby('quarter_label')[col].last()
                    for q in quarters:
                        val = s_q.get(q)
                        if pd.isna(val):
                            row[q] = "N/A"
                        else:
                            if kind == 'percent':
                                row[q] = f"{val:.1f}%"
                            else:
                                row[q] = f"{val:,.1f}" if abs(val) >= 1 else f"{val:.3f}"
            rows.append(row)
        if not rows:
            return pd.DataFrame()
        table = pd.DataFrame(rows).set_index('KEYCODE')
        return table
    except Exception:
        return pd.DataFrame()

def render_bank_summary_charts(bank_data):
    """Render bank summary charts with MA4"""
    st.subheader("Bank Summary Charts")
    
    # Create mock charts for demonstration
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Net Interest Income', 'Total Income', 'Net Income', 'Total Assets'),
        vertical_spacing=0.3
    )
    
    # Mock data for charts
    dates = pd.date_range(start='2022-01-01', periods=12, freq='M')
    
    # Add sample traces
    for i, metric in enumerate(['Net Interest Income', 'Total Income', 'Net Income', 'Total Assets']):
        row = (i // 2) + 1
        col = (i % 2) + 1
        
    fig.add_trace(
        go.Scatter(
                x=dates,
                y=[100 + i*10 + j*5 for j in range(12)],
            mode='lines+markers',
                name=metric,
                line=dict(color=['blue', 'green', 'red', 'orange'][i])
        ),
            row=row, col=col
    )
    
        # Add MA4 line
    fig.add_trace(
        go.Scatter(
                x=dates[3:],
                y=[sum([100 + i*10 + j*5 for j in range(k-3, k+1)])/4 for k in range(3, 12)],
                mode='lines',
                name=f'{metric} MA4',
                line=dict(color=['blue', 'green', 'red', 'orange'][i], dash='solid')
            ),
            row=row, col=col
    )
    
    fig.update_layout(**get_plotly_font_config(), height=600, showlegend=False)
    st.plotly_chart(fig, config=PLOTLY_CONFIG)

def render_bank_margins_charts(bank_data, symbol, start_year, metrics_list):
    """Create pivot table with KEYCODE as rows and quarterly periods as columns from real data"""
    try:
        p = _get_bank_parquet_path()
        df = pd.read_parquet(str(p))
        # Ensure date
        if 'report_date' in df.columns:
            df['report_date'] = pd.to_datetime(df['report_date'])
            df['date'] = df['report_date']
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        else:
            return create_mock_pivot_data(symbol, start_year, metrics_list)
        # Filter
        if 'symbol' in df.columns:
            df = df[df['symbol'] == symbol].copy()
        df = df[df['date'].dt.year >= int(start_year)].copy()
        if df.empty:
            return pd.DataFrame()
        # Quarter label
        df['quarter_label'] = df['date'].dt.year.astype(str) + 'Q' + (((df['date'].dt.month - 1)//3) + 1).astype(str)
        # Build pivot rows
        rows = []
        # Order quarters
        quarters = sorted(df['quarter_label'].unique().tolist(), key=lambda x: (int(x[:4]), int(x[-1])))
        for metric in metrics_list:
            if metric not in df.columns:
                # skip missing metric
                continue
            row = {'KEYCODE': metric.upper()}
            s = df.groupby('quarter_label')[metric].last()
            for q in quarters:
                val = s.get(q)
                if pd.isna(val):
                    row[q] = "N/A"
                else:
                    row[q] = format_pivot_values(val, metric)
            rows.append(row)
        if not rows:
            return pd.DataFrame()
        pivot_df = pd.DataFrame(rows).set_index('KEYCODE')
        return pivot_df
    except Exception:
        return create_mock_pivot_data(symbol, start_year, metrics_list)

def build_bank_margins_charts():
    """Render bank margins charts with MA4"""
    st.subheader("Bank Margins Charts")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('ROE TTM', 'ROA TTM', 'NIM', 'Cost Income Ratio'),
        vertical_spacing=0.3
    )
    
    dates = pd.date_range(start='2022-01-01', periods=12, freq='M')
    
    for i, metric in enumerate(['ROE TTM', 'ROA TTM', 'NIM', 'Cost Income Ratio']):
        row = (i // 2) + 1
        col = (i % 2) + 1
        
    fig.add_trace(
            go.Scatter(
                x=dates,
                y=[10 + i*2 + j*0.5 for j in range(12)],
                mode='lines+markers',
                name=metric,
                line=dict(color=['blue', 'green', 'red', 'orange'][i])
            ),
            row=row, col=col
        )
    
    fig.update_layout(**get_plotly_font_config(), height=600, showlegend=False)
    st.plotly_chart(fig, config=PLOTLY_CONFIG)

def render_bank_growth_charts(bank_data):
    """Render bank growth charts with MA4"""
    st.subheader("Bank Growth Charts")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Income Growth', 'Asset Growth', 'Equity Growth', 'Loan Growth'),
        vertical_spacing=0.3
    )
    
    dates = pd.date_range(start='2022-01-01', periods=12, freq='M')
    
    for i, metric in enumerate(['Income Growth', 'Asset Growth', 'Equity Growth', 'Loan Growth']):
        row = (i // 2) + 1
        col = (i % 2) + 1
        
    fig.add_trace(
        go.Scatter(
                x=dates,
                y=[5 + i*3 + j*1 for j in range(12)],
            mode='lines+markers',
                name=metric,
                line=dict(color=['blue', 'green', 'red', 'orange'][i])
        ),
            row=row, col=col
    )
    
    fig.update_layout(**get_plotly_font_config(), height=600, showlegend=False)
    st.plotly_chart(fig, config=PLOTLY_CONFIG)

def render_pe_pb_dotplot(valuation_data, selected_symbol, start_year):
    """Render PE/PB candlestick chart for bank stocks"""
    
    # Get metric_type from sidebar session state
    metric_type = st.session_state.get('bank_metric_type', 'P/E')
    st.caption(f"Historical trend analysis for {selected_symbol}")
    render_bank_historical_trend(selected_symbol, metric_type, start_year)

    st.markdown("---")
    st.subheader(f"{metric_type} Distribution - Bank Sector")
    
    # Load real PE/PB data for candlestick chart
    banks = [
        'VCB', 'TCB', 'BID', 'CTG', 'MBB', 'ACB', 'VPB', 'HDB', 'TPB', 'STB',
        'SHB', 'MSB', 'LPB', 'VIB', 'OCB', 'NAB', 'SSB', 'EIB', 'VBB', 'PGB'
    ]
    
    # Create candlestick chart
    fig_candle = go.Figure()
    
    valid_tickers = []
    
    # Load real data
    try:
        if metric_type == "P/E":
            # Try to load latest PE data
            pe_files = [
                get_data_path("calculated_results/valuation/pe/pe_historical_all_symbols_final.parquet")
            ]
            
            all_data = None
            for pe_file in pe_files:
                try:
                    df = pd.read_parquet(pe_file)
                    if 'symbol' in df.columns:
                        all_data = df
                        break
                except:
                    continue
                    
        else:  # P/B
            pb_file = get_data_path("calculated_results/valuation/pb/pb_historical_all_symbols_final.parquet")
            all_data = pd.read_parquet(pb_file)
        
        # Prepare data for each bank
        for ticker in banks:
            if all_data is not None and 'symbol' in all_data.columns:
                # Filter data for this bank
                bank_data = all_data[all_data['symbol'] == ticker].copy()
                
                if len(bank_data) > 0:
                    if metric_type == "P/E":
                        ticker_data = bank_data['pe_ratio'].dropna()
                    else:
                        ticker_data = bank_data['pb_ratio'].dropna()
                else:
                    # No real data, skip this bank
                    continue
            else:
                # Fallback to mock data
                np.random.seed(hash(ticker) % 1000)
                if metric_type == "P/E":
                    ticker_data = pd.Series(np.random.normal(10, 3, 100))
                    ticker_data = ticker_data[ticker_data > 0]
                else:
                    ticker_data = pd.Series(np.random.normal(2.0, 0.4, 100))
                    ticker_data = ticker_data[ticker_data > 0]
        
            if len(ticker_data) < 20:
                continue
                
            valid_tickers.append(ticker)
            
            # Calculate percentiles with smart outlier handling
            median_val = ticker_data.median()
            
            # Only exclude extreme outliers
            if metric_type == "P/E":
                upper_limit = min(50, median_val * 3) if median_val > 0 else 50
                clean_data = ticker_data[ticker_data <= upper_limit]
            else:
                upper_limit = min(4.0, median_val * 2.0) if median_val > 0 else 4.0
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
            
    except Exception as e:
        st.error(f"Error loading {metric_type} data: {e}")
        st.info("Using mock data as fallback")
        
        # Fallback to mock data for all banks
        for ticker in banks:
            np.random.seed(hash(ticker) % 1000)
            if metric_type == "P/E":
                ticker_data = pd.Series(np.random.normal(10, 3, 100))
                ticker_data = ticker_data[ticker_data > 0]
            else:
                ticker_data = pd.Series(np.random.normal(2.0, 0.4, 100))
                ticker_data = ticker_data[ticker_data > 0]
            
            if len(ticker_data) < 20:
                continue
                
            valid_tickers.append(ticker)
            
            # Calculate percentiles with smart outlier handling
            median_val = ticker_data.median()
            
            # Only exclude extreme outliers
            if metric_type == "P/E":
                upper_limit = min(50, median_val * 3) if median_val > 0 else 50
                clean_data = ticker_data[ticker_data <= upper_limit]
            else:
                upper_limit = min(4.0, median_val * 2.0) if median_val > 0 else 4.0
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
                marker=dict(size=8, color='#478B81', symbol='circle'),
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
        title=f"{metric_type} Distribution - Bank Sector",
        xaxis_title="Bank",
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

def render_bank_historical_trend(selected_ticker, metric_type, start_year):
    """Render historical trend chart for selected bank using real data"""
    
    # Load real PE/PB data
    try:
        if metric_type == "P/E":
            # Try to load latest PE data
            pe_files = [
                get_data_path("calculated_results/valuation/pe/pe_historical_all_symbols_final.parquet")
            ]
            
            ticker_df = None
            for pe_file in pe_files:
                try:
                    df = pd.read_parquet(pe_file)
                    if 'symbol' in df.columns:
                        bank_data = df[df['symbol'] == selected_ticker].copy()
                        if len(bank_data) > 0:
                            bank_data['TRADE_DATE'] = pd.to_datetime(bank_data['date'])
                            bank_data['VALUE'] = bank_data['pe_ratio']
                            ticker_df = bank_data[['TRADE_DATE', 'VALUE']].sort_values('TRADE_DATE')
                            break
                except:
                    continue
                    
        else:  # P/B
            # Load latest PB data
            pb_file = get_data_path("calculated_results/valuation/pb/pb_historical_all_symbols_final.parquet")
            df = pd.read_parquet(pb_file)
            
            if 'symbol' in df.columns:
                bank_data = df[df['symbol'] == selected_ticker].copy()
                if len(bank_data) > 0:
                    bank_data['TRADE_DATE'] = pd.to_datetime(bank_data['date'])
                    bank_data['VALUE'] = bank_data['pb_ratio']
                    ticker_df = bank_data[['TRADE_DATE', 'VALUE']].sort_values('TRADE_DATE')
        
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
                # P/E ratios with some trend
                base_value = 10 + hash(selected_ticker) % 5
                values = []
                current = base_value
                for i in range(len(dates)):
                    # Add some trend and volatility
                    trend = 0.01 * np.sin(i * 0.1)  # Cyclical trend
                    volatility = np.random.normal(0, 0.5)
                    current += trend + volatility
                    current = max(3, min(25, current))  # Keep in reasonable range
                    values.append(current)
            else:
                # P/B ratios with some trend - realistic range for banks (1.0-3.5)
                base_value = 1.5 + (hash(selected_ticker) % 10) * 0.15  # 1.5 to 3.0 base
                values = []
                current = base_value
                for i in range(len(dates)):
                    # Add some trend and volatility
                    trend = 0.003 * np.sin(i * 0.1)  # Cyclical trend
                    volatility = np.random.normal(0, 0.08)  # Reduced volatility
                    current += trend + volatility
                    current = max(1.0, min(3.5, current))  # Realistic bank P/B range
                    values.append(current)
            
            # Create DataFrame
            ticker_df = pd.DataFrame({
                'TRADE_DATE': dates,
                'VALUE': values
            })
            
    except Exception as e:
        st.error(f"Error loading {metric_type} data: {e}")
        return
    
    if len(ticker_df) > 0:
        # Calculate statistics
        mean_val = ticker_df['VALUE'].mean()
        std_val = ticker_df['VALUE'].std()
        median_val = ticker_df['VALUE'].median()
        current_val = ticker_df['VALUE'].iloc[-1]
        percentile = np.sum(ticker_df['VALUE'] <= current_val) / len(ticker_df) * 100
        z_score = (current_val - mean_val) / std_val if std_val > 0 else 0
        
        # Create figure
        fig_ts = go.Figure()
        
        # Add main valuation line
        fig_ts.add_trace(go.Scatter(
            x=ticker_df['TRADE_DATE'],
            y=ticker_df['VALUE'],
            mode='lines',
            name=f'{metric_type} Ratio',
            line=dict(color='#A95C68', width=2)
        ))
        
        # Add mean line
        fig_ts.add_trace(go.Scatter(
            x=[ticker_df['TRADE_DATE'].min(), ticker_df['TRADE_DATE'].max()],
            y=[mean_val, mean_val],
            mode='lines',
            name='Mean',
            line=dict(color='black', width=2, dash='solid')
        ))
        
        # Add +1 SD line
        fig_ts.add_trace(go.Scatter(
            x=[ticker_df['TRADE_DATE'].min(), ticker_df['TRADE_DATE'].max()],
            y=[mean_val + std_val, mean_val + std_val],
            mode='lines',
            name='+1 SD',
            line=dict(color='red', width=1, dash='dash')
        ))
        
        # Add -1 SD line
        fig_ts.add_trace(go.Scatter(
            x=[ticker_df['TRADE_DATE'].min(), ticker_df['TRADE_DATE'].max()],
            y=[mean_val - std_val, mean_val - std_val],
            mode='lines',
            name='-1 SD',
            line=dict(color='green', width=1, dash='dash')
        ))
        
        # Add current value marker
        fig_ts.add_trace(go.Scatter(
            x=[ticker_df['TRADE_DATE'].max()],
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
            st.metric("Current", f"{current_val:.2f}")
            st.metric("Median", f"{median_val:.2f}")
        with col_stat2:
            st.metric("Percentile", f"{percentile:.1f}%")
            status = "Overvalued" if percentile > 75 else "Undervalued" if percentile < 25 else "Fair Value"
            color = "inverse" if percentile > 75 else "normal" if percentile < 25 else "off"
            st.metric("Status", status, delta=status, delta_color=color)
    else:
        st.warning(f"No data available for {selected_ticker}")

def create_mock_bank_data(symbol, start_year):
    """Create mock bank data for demonstration"""
    dates = pd.date_range(start=f'{start_year}-01-01', periods=12, freq='ME')
    data = []
    
    for i, date in enumerate(dates):
        data.append({
            'symbol': symbol,
            'date': date,
            'net_interest_income': 1000 + i*50,
            'total_income': 1200 + i*60,
            'net_income': 200 + i*10,
            'total_assets': 50000 + i*2000,
            'roea_ttm': 15 + i*0.5,
            'roaa_ttm': 1.5 + i*0.05,
            'nim_q': 3.5 + i*0.1
        })
    
    return pd.DataFrame(data)

def create_mock_valuation_data(symbol, start_year):
    """Create mock valuation data for demonstration"""
    dates = pd.date_range(start=f'{start_year}-01-01', periods=12, freq='ME')
    data = []
    
    for i, date in enumerate(dates):
        data.append({
                'symbol': symbol,
                'date': date,
            'pe_ratio': 8 + i*0.5,
            'pb_ratio': 1.2 + i*0.05,
            'close_price': 50 + i*2
            })
    
    return pd.DataFrame(data)

def create_mock_pivot_data(symbol, start_year, metrics_list):
    """Create mock pivot table data for demonstration"""
    from datetime import datetime
    now = datetime.now()
    current_year = now.year
    current_quarter = (now.month - 1) // 3 + 1
    # Ensure timeline covers at least up to 2025Q2
    end_year = max(2025, current_year)
    quarters = []
    for year in range(start_year, end_year + 1):
        if year < 2025:
            q_end = 4
        elif year == 2025:
            # At least Q2/2025; extend further if current time beyond
            q_end = max(2, current_quarter if current_year == 2025 else 4)
        else:
            q_end = current_quarter if year == current_year else 4
        for q in range(1, q_end + 1):
            quarters.append(f"{year}Q{q}")
    
    data = []
    for metric in metrics_list:
        row = {'KEYCODE': metric.upper()}
        for quarter in quarters:
            # Mock values
            if 'ratio' in metric.lower() or 'roe' in metric.lower() or 'roa' in metric.lower():
                row[quarter] = f"{10 + hash(metric) % 10:.1f}%"
            else:
                row[quarter] = f"{1000 + hash(metric) % 5000:,.1f}"
        data.append(row)
    
    df = pd.DataFrame(data)
    df.set_index('KEYCODE', inplace=True)
    return df

if __name__ == "__main__":
    render_bank_dashboard()