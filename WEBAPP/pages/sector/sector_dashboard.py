"""
Sector Analysis Dashboard
=========================
Premium financial dashboard for sector comparison and valuation.

Design: Financial Editorial Theme
- Dark terminal aesthetic with vibrant accents
- Distribution candlestick for all sectors
- Line charts with statistical bands for individual sectors

Run:
    streamlit run WEBAPP/pages/sector/sector_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from datetime import timedelta
from io import BytesIO

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from WEBAPP.services.sector_service import SectorService
from WEBAPP.services.macro_commodity_loader import MacroCommodityLoader
from WEBAPP.core.styles import (
    get_page_style, get_chart_layout,
    CHART_COLORS, BAR_COLORS, DISTRIBUTION_COLORS, ASSESSMENT_COLORS, BAND_COLORS,
    render_styled_table, get_table_style
)

# Note: st.set_page_config is handled by main_app.py

# Inject premium styles
st.markdown(get_page_style(), unsafe_allow_html=True)
st.markdown(get_table_style(), unsafe_allow_html=True)

# Header
st.title("Sector Analysis")
st.markdown("**Real-time sector valuation comparison across Vietnamese equity markets**")
st.markdown("---")

# Sidebar
st.sidebar.markdown("## Filters")

try:
    service = SectorService()
except Exception as e:
    st.error(f"Failed to initialize service: {e}")
    st.stop()

# Metric selector
st.sidebar.markdown("### Valuation Metric")
metric_options = ["PE TTM", "PB"]
selected_metric = st.sidebar.selectbox(
    "Primary Metric",
    options=metric_options,
    index=0,
    label_visibility="collapsed"
)

# Map to column names
metric_map = {"PE TTM": "pe_ttm", "PB": "pb"}
primary_metric = metric_map[selected_metric]

# Time range selector - selectbox with default 3Y
st.sidebar.markdown("### Time Range")
time_options = {"3M": 63, "6M": 126, "1Y": 252, "3Y": 756, "ALL": 2000}
selected_range = st.sidebar.selectbox(
    "Select Period",
    options=list(time_options.keys()),
    index=3,  # Default to 3Y
    label_visibility="collapsed"
)
days = time_options[selected_range]
# For candlestick distribution, always use ALL data
days_distribution = time_options["ALL"]

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Load data
@st.cache_data(ttl=3600)
def load_overview():
    return SectorService().get_market_overview()

@st.cache_data(ttl=3600)
def load_sector_data():
    return SectorService().get_sector_valuation(sectors_only=True)

@st.cache_data(ttl=3600)
def load_sector_history(sector: str, limit: int = 1000):
    """Load sector history filtered by days limit"""
    return SectorService().get_sector_history(sector, limit=limit)

@st.cache_data(ttl=3600)
def load_all_valuation():
    """Load all valuation data including market indices and sectors"""
    return SectorService().get_sector_valuation(sectors_only=False)

def filter_series_by_days(series_df: pd.DataFrame, days: int) -> pd.DataFrame:
    """Filter a time series DataFrame to last N days."""
    if series_df.empty or 'date' not in series_df.columns:
        return series_df
    series_df = series_df.copy()
    series_df['date'] = pd.to_datetime(series_df['date'])
    series_df = series_df.sort_values('date')
    return series_df.tail(days)

overview = load_overview()
sector_df = load_sector_data()
all_df = load_all_valuation()

# Separate Market Indices from Sectors
market_indices = ['VNINDEX', 'VNINDEX_EXCLUDE', 'BSC_INDEX']
if not all_df.empty:
    # Get unique scopes and clean names
    all_scopes = all_df['scope'].unique().tolist()
    sector_scopes = [s.replace('SECTOR:', '') for s in all_scopes if s.startswith('SECTOR:')]
    index_scopes = [s for s in all_scopes if s in market_indices]

# ============================================================================
# METRIC CARDS
# ============================================================================
st.markdown("### Market Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    top_sector = overview.get('top_sector', '-')
    st.metric("Lowest PE Sector", top_sector)

with col2:
    market_pe = overview.get('market_pe', 0) or 0
    st.metric("VNINDEX PE", f"{market_pe:.1f}x")

with col3:
    market_pb = overview.get('market_pb', 0) or 0
    st.metric("VNINDEX PB", f"{market_pb:.1f}x")

with col4:
    sector_count = overview.get('sector_count', 0)
    ticker_count = overview.get('ticker_count', 0)
    st.metric("Sectors / Tickers", f"{sector_count} / {ticker_count}")

st.markdown("---")

# ============================================================================
# TABS
# ============================================================================
tab_distribution, tab_individual, tab_macro, tab_commodity, tab_tables = st.tabs([
    "🕯️ All Sectors Distribution",
    "📈 Individual Analysis",
    "📊 Macro",
    "🛢️ Commodity",
    "📋 Data"
])

# ============================================================================
# TAB 1: ALL SECTORS DISTRIBUTION (Candlestick)
# ============================================================================
with tab_distribution:
    # Group selector
    group_type = st.radio(
        "Select Group",
        options=["📊 Sectors", "📈 Market Indices"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if group_type == "📊 Sectors":
        # =====================================================================
        # SECTORS: Candlestick Distribution Chart
        # =====================================================================
        st.markdown(f"### {selected_metric} Distribution by Sector")
        st.markdown("*Candlestick: Min-Max (whiskers), P25-P75 (body). Colored dot = current value.*")

        target_scopes = sector_scopes if sector_scopes else []

        if target_scopes:
            fig_candle = go.Figure()
            valid_items = []
            distribution_data = []

            for scope in target_scopes:
                # Load historical data - always use ALL for distribution chart
                history = load_sector_history(scope, days_distribution)

                if history.empty or primary_metric not in history.columns:
                    continue

                metric_data = history[primary_metric].dropna()

                if len(metric_data) < 20:
                    continue

                # Get current value first
                current_val = metric_data.iloc[-1] if len(metric_data) > 0 else None

                # For PE: Skip sector entirely if current PE is negative or invalid
                if primary_metric == 'pe_ttm':
                    if current_val is None or pd.isna(current_val) or current_val <= 0:
                        continue

                # Filter outliers
                if primary_metric == 'pe_ttm':
                    clean_data = metric_data[(metric_data > 0) & (metric_data <= 100)]
                else:
                    clean_data = metric_data[(metric_data >= 0) & (metric_data <= 100)]

                if len(clean_data) < 20:
                    continue

                valid_items.append(scope)

                p_min = clean_data.min()
                p5 = clean_data.quantile(0.05)
                p25 = clean_data.quantile(0.25)
                p50 = clean_data.quantile(0.50)
                p75 = clean_data.quantile(0.75)
                p95 = clean_data.quantile(0.95)
                p_max = clean_data.max()

                # Store for table
                if current_val:
                    percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100
                    distribution_data.append({
                        'Scope': scope,
                        'Current': current_val,
                        'Min': p_min,
                        'P25': p25,
                        'Median': p50,
                        'P75': p75,
                        'Max': p_max,
                        'Percentile': percentile
                    })

                # Add candlestick (body = P25-P75, whiskers = Min-Max)
                fig_candle.add_trace(go.Candlestick(
                    x=[scope],
                    open=[round(p25, 2)],
                    high=[round(p_max, 2)],
                    low=[round(p_min, 2)],
                    close=[round(p75, 2)],
                    name=scope,
                    showlegend=False,
                    increasing_line_color=DISTRIBUTION_COLORS['body'],
                    decreasing_line_color=DISTRIBUTION_COLORS['body'],
                    increasing_fillcolor=DISTRIBUTION_COLORS['body_fill'],
                    decreasing_fillcolor=DISTRIBUTION_COLORS['body_fill'],
                ))

                # Add current value as scatter point
                if current_val and not pd.isna(current_val):
                    percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100

                    if percentile < 25:
                        dot_color = ASSESSMENT_COLORS['undervalued']
                    elif percentile < 75:
                        dot_color = ASSESSMENT_COLORS['fair']
                    else:
                        dot_color = ASSESSMENT_COLORS['expensive']

                    fig_candle.add_trace(go.Scatter(
                        x=[scope],
                        y=[current_val],
                        mode='markers',
                        marker=dict(size=12, color=dot_color, symbol='circle', line=dict(width=2, color='white')),
                        name=f"{scope} Current",
                        showlegend=False,
                        hovertemplate=(
                            f'<b>{scope}</b><br>' +
                            f'Current: {current_val:.2f}x<br>' +
                            f'Percentile: {percentile:.1f}%<br>' +
                            f'Median: {p50:.2f}x<br>' +
                            '<extra></extra>'
                        )
                    ))

            if valid_items:
                layout = get_chart_layout(height=500)
                layout['xaxis'] = dict(
                    categoryorder='array',
                    categoryarray=valid_items,
                    rangeslider=dict(visible=False),
                    tickangle=-45,
                    tickfont=dict(size=10, color='#FFFFFF'),
                    fixedrange=True
                )
                layout['yaxis']['title'] = selected_metric
                layout['yaxis']['fixedrange'] = True
                layout['dragmode'] = False

                if primary_metric == 'pb':
                    layout['yaxis']['range'] = [0, 8]
                elif primary_metric == 'pe_ttm':
                    layout['yaxis']['range'] = [0, 50]

                fig_candle.update_layout(**layout)

                st.plotly_chart(fig_candle, use_container_width=True, config={'displayModeBar': False})

                # Legend
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("🟢 **Undervalued** (< P25)")
                with col2:
                    st.markdown("🟡 **Fair Value** (P25-P75)")
                with col3:
                    st.markdown("🔴 **Expensive** (> P75)")

                # Distribution table
                if distribution_data:
                    st.markdown("### Distribution Statistics")
                    dist_df = pd.DataFrame(distribution_data)
                    dist_df_raw = dist_df.copy()
                    dist_df = dist_df.sort_values('Percentile')
                    dist_df_raw = dist_df_raw.sort_values('Percentile')

                    dist_df_display = dist_df.copy()
                    for col in ['Current', 'Min', 'P25', 'Median', 'P75', 'Max']:
                        dist_df_display[col] = dist_df_display[col].apply(lambda x: f'{x:.2f}x')
                    dist_df_display['Percentile'] = dist_df_display['Percentile'].apply(lambda x: f'{x:.0f}%')

                    st.markdown(render_styled_table(dist_df_display), unsafe_allow_html=True)

                    # Excel download
                    excel_buffer = BytesIO()
                    dist_df_raw.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    st.download_button(
                        f"📥 Download {selected_metric} Distribution Data (Excel)",
                        excel_buffer,
                        f"{selected_metric.lower().replace(' ', '_')}_distribution_sectors.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            else:
                st.warning("Not enough historical data for distribution analysis")
        else:
            st.warning("No sector data available")

    else:
        # =====================================================================
        # MARKET INDICES: Line Chart (Combined View)
        # =====================================================================
        st.markdown(f"### {selected_metric} Historical Trend - Market Indices")
        st.markdown("*Line chart showing historical valuation trends for all market indices.*")

        target_scopes = index_scopes if index_scopes else []

        if target_scopes:
            fig_line = go.Figure()
            line_colors = [CHART_COLORS['primary'], CHART_COLORS['secondary'], CHART_COLORS['tertiary']]
            all_stats = []

            for i, idx_scope in enumerate(target_scopes[:3]):
                history = load_sector_history(idx_scope, days)

                if history.empty or primary_metric not in history.columns:
                    continue

                metric_data = history[primary_metric].dropna()

                # Filter outliers
                if primary_metric == 'pe_ttm':
                    metric_data = metric_data[(metric_data > 0) & (metric_data <= 100)]
                    plot_df = history[(history[primary_metric] > 0) & (history[primary_metric] <= 100)]
                else:
                    metric_data = metric_data[(metric_data >= 0) & (metric_data <= 100)]
                    plot_df = history[(history[primary_metric] >= 0) & (history[primary_metric] <= 100)]

                if len(metric_data) < 20:
                    continue

                current_val = metric_data.iloc[-1]
                median_val = metric_data.median()
                mean_val = metric_data.mean()
                std_val = metric_data.std()
                z_score = (current_val - mean_val) / std_val if std_val > 0 else 0
                percentile = (metric_data < current_val).mean() * 100

                all_stats.append({
                    'Index': idx_scope,
                    'Current': current_val,
                    'Median': median_val,
                    'Mean': mean_val,
                    'Z-Score': z_score,
                    'Percentile': percentile
                })

                # Add line trace
                fig_line.add_trace(go.Scatter(
                    x=plot_df['date'],
                    y=plot_df[primary_metric],
                    name=idx_scope,
                    mode='lines',
                    line=dict(color=line_colors[i % len(line_colors)], width=2.5),
                    hovertemplate=f'<b>{idx_scope}</b><br>Date: %{{x}}<br>{selected_metric}: %{{y:.2f}}x<extra></extra>'
                ))

            if all_stats:
                # Auto-scale based on all data
                all_values = []
                all_dates = []
                for idx_scope in target_scopes[:3]:
                    hist = load_sector_history(idx_scope, days)
                    if not hist.empty and primary_metric in hist.columns:
                        vals = hist[primary_metric].dropna()
                        if primary_metric == 'pe_ttm':
                            vals = vals[(vals > 0) & (vals <= 100)]
                        else:
                            vals = vals[(vals >= 0) & (vals <= 100)]
                        all_values.extend(vals.tolist())
                        if 'date' in hist.columns:
                            all_dates.extend(pd.to_datetime(hist['date']).tolist())

                if all_values:
                    y_min = max(0, min(all_values) * 0.9)
                    y_max = max(all_values) * 1.1
                else:
                    y_min, y_max = 0, 100

                # Larger chart height for main focus
                layout = get_chart_layout(height=600)
                layout['yaxis']['title'] = selected_metric
                layout['yaxis']['range'] = [y_min, y_max]
                layout['showlegend'] = True
                layout['legend'] = dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5,
                    font=dict(size=12, color='#E8E8E8')
                )

                # X-axis configuration
                layout['xaxis'] = dict(
                    showticklabels=True,
                    tickmode='auto',
                    nticks=8,  # Auto-select ~8 tick marks
                    tickformat='%b %Y',  # Jan 2023, Jul 2023, etc.
                    tickangle=0,  # Horizontal labels
                    tickfont=dict(size=10, family='Source Sans 3', color='#CBD5E1'),
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.05)',
                    showline=True,
                    linecolor='rgba(255,255,255,0.1)',
                    rangeslider=dict(visible=False)
                )

                # Add right padding for latest data visibility
                if all_dates:
                    max_date = max(all_dates)
                    min_date = min(all_dates)
                    padded_max = max_date + timedelta(days=30)
                    layout['xaxis']['range'] = [min_date, padded_max]

                # Add more bottom margin for x-axis labels
                layout['margin'] = dict(l=60, r=40, t=50, b=60)

                fig_line.update_layout(**layout)

                st.plotly_chart(fig_line, use_container_width=True)

                # Stats table
                st.markdown("### Statistics Comparison")
                stats_df = pd.DataFrame(all_stats)
                stats_df_raw = stats_df.copy()

                for col in ['Current', 'Median', 'Mean']:
                    stats_df[col] = stats_df[col].apply(lambda x: f'{x:.2f}x')
                stats_df['Z-Score'] = stats_df['Z-Score'].apply(lambda x: f'{x:+.2f}σ')
                stats_df['Percentile'] = stats_df['Percentile'].apply(lambda x: f'{x:.0f}%')

                st.markdown(render_styled_table(stats_df), unsafe_allow_html=True)

                # Excel download - Statistics
                excel_buffer = BytesIO()
                stats_df_raw.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)
                st.download_button(
                    f"📥 Download Market Indices {selected_metric} Statistics (Excel)",
                    excel_buffer,
                    f"market_indices_{primary_metric}_statistics_{days}d.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="download_market_indices_stats"
                )

                # Excel download - Full Historical Data (PE + PB)
                st.markdown("---")
                st.markdown("### Export Full Historical Data")
                full_data_list = []
                for idx_scope in target_scopes[:3]:
                    hist = load_sector_history(idx_scope, days)
                    if not hist.empty:
                        hist_copy = hist.copy()
                        hist_copy['index'] = idx_scope
                        # Select relevant columns
                        cols_to_keep = ['date', 'index']
                        if 'pe_ttm' in hist_copy.columns:
                            cols_to_keep.append('pe_ttm')
                        if 'pb' in hist_copy.columns:
                            cols_to_keep.append('pb')
                        if 'pe_fwd_2025' in hist_copy.columns:
                            cols_to_keep.append('pe_fwd_2025')
                        if 'pe_fwd_2026' in hist_copy.columns:
                            cols_to_keep.append('pe_fwd_2026')
                        full_data_list.append(hist_copy[[c for c in cols_to_keep if c in hist_copy.columns]])

                if full_data_list:
                    full_df = pd.concat(full_data_list, ignore_index=True)
                    # Sort by date and index
                    full_df = full_df.sort_values(['date', 'index'])

                    excel_buffer_full = BytesIO()
                    full_df.to_excel(excel_buffer_full, index=False, engine='openpyxl')
                    excel_buffer_full.seek(0)
                    st.download_button(
                        f"📥 Download Full Historical Data - PE & PB (Excel)",
                        excel_buffer_full,
                        f"market_indices_full_history_{days}d.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="download_market_indices_full"
                    )
                    st.caption(f"Contains {len(full_df)} rows × {len(full_df.columns)} columns for {len(target_scopes[:3])} indices")
            else:
                st.warning("Not enough valid data for market indices")
        else:
            st.warning("No market index data available")

# ============================================================================
# TAB 2: INDIVIDUAL ANALYSIS (Line chart with statistical bands)
# ============================================================================
with tab_individual:
    st.markdown(f"### {selected_metric} Historical Trend with Statistical Bands")
    st.markdown("*Line chart with median and ±1σ, ±2σ bands. Auto-scaled to data.*")

    # Scope selector - separate groups
    col1, col2 = st.columns([1, 3])

    with col1:
        scope_group = st.radio(
            "Select Group",
            options=["Market Indices", "Sectors"],
            index=1,
            label_visibility="collapsed"
        )

    # For Market Indices: select individual index only
    selected_scope = None

    with col2:
        if scope_group == "Market Indices":
            # Individual indices only (no Combined option)
            if index_scopes:
                selected_scope = st.selectbox(
                    "Select Index",
                    options=index_scopes,
                    index=0,
                    label_visibility="collapsed"
                )
            else:
                st.warning("No market indices available")
        else:
            # Sectors - just select individual sector
            available_scopes = sector_scopes
            if available_scopes:
                selected_scope = st.selectbox(
                    "Select Sector",
                    options=available_scopes,
                    index=0,
                    label_visibility="collapsed"
                )
            else:
                selected_scope = None
                st.warning("No sectors available")

    # Helper function to create individual chart with bands
    def create_individual_chart(scope_name, history_df, metric_col, metric_label, chart_height=400):
        """Create line chart with statistical bands for a single scope"""
        if history_df.empty or metric_col not in history_df.columns:
            return None, None

        metric_data = history_df[metric_col].dropna()

        # Filter outliers
        if metric_col == 'pe_ttm':
            metric_data = metric_data[(metric_data > 0) & (metric_data <= 100)]
        else:
            metric_data = metric_data[(metric_data >= 0) & (metric_data <= 100)]

        if len(metric_data) < 20:
            return None, None

        # Calculate statistics
        median_val = metric_data.median()
        std_val = metric_data.std()
        mean_val = metric_data.mean()

        # Filter history for plotting
        if metric_col == 'pe_ttm':
            plot_df = history_df[(history_df[metric_col] > 0) & (history_df[metric_col] <= 100)]
        else:
            plot_df = history_df[(history_df[metric_col] >= 0) & (history_df[metric_col] <= 100)]

        plus_1sd = mean_val + std_val
        plus_2sd = mean_val + 2 * std_val
        minus_1sd = mean_val - std_val
        minus_2sd = mean_val - 2 * std_val
        current_val = metric_data.iloc[-1]

        fig = go.Figure()

        # ±2 SD band - using brand blue
        fig.add_trace(go.Scatter(x=plot_df['date'], y=[plus_2sd]*len(plot_df), mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
        fig.add_trace(go.Scatter(x=plot_df['date'], y=[minus_2sd]*len(plot_df), mode='lines', line=dict(width=0), fill='tonexty', fillcolor=BAND_COLORS['band_2sd'], showlegend=False, hoverinfo='skip'))

        # ±1 SD band - using brand teal
        fig.add_trace(go.Scatter(x=plot_df['date'], y=[plus_1sd]*len(plot_df), mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
        fig.add_trace(go.Scatter(x=plot_df['date'], y=[minus_1sd]*len(plot_df), mode='lines', line=dict(width=0), fill='tonexty', fillcolor=BAND_COLORS['band_1sd'], showlegend=False, hoverinfo='skip'))

        # Main line - brand teal
        fig.add_trace(go.Scatter(x=plot_df['date'], y=plot_df[metric_col], name=metric_label, mode='lines', line=dict(color=BAND_COLORS['main_line'], width=2.5), hovertemplate=f'<b>Date</b>: %{{x}}<br><b>{metric_label}</b>: %{{y:.2f}}x<extra></extra>'))

        # Median line - brand gold
        fig.add_hline(y=median_val, line=dict(color=BAND_COLORS['median_line'], width=2, dash='solid'), annotation=dict(text=f'Med: {median_val:.1f}x', font=dict(color=BAND_COLORS['median_line'], size=10), bgcolor='rgba(16, 24, 32, 0.9)', borderpad=3, xanchor='right'))

        # Mean line - brand blue
        fig.add_hline(y=mean_val, line=dict(color=BAND_COLORS['mean_line'], width=1.5, dash='dash'), annotation=dict(text=f'μ: {mean_val:.1f}x', font=dict(color=BAND_COLORS['mean_line'], size=9), xanchor='left'))

        # ±1 SD lines - blue light
        fig.add_hline(y=plus_1sd, line=dict(color=BAND_COLORS['sd_line'], width=1, dash='dot'), annotation=dict(text=f'+1σ', font=dict(color=BAND_COLORS['sd_line'], size=8), xanchor='left'))
        fig.add_hline(y=minus_1sd, line=dict(color=BAND_COLORS['sd_line'], width=1, dash='dot'), annotation=dict(text=f'-1σ', font=dict(color=BAND_COLORS['sd_line'], size=8), xanchor='left'))

        # ±2 SD lines - subtle blue
        fig.add_hline(y=plus_2sd, line=dict(color='rgba(74, 123, 200, 0.5)', width=1, dash='dot'))
        fig.add_hline(y=minus_2sd, line=dict(color='rgba(74, 123, 200, 0.5)', width=1, dash='dot'))

        # Auto-scale
        y_min = max(0, metric_data.min() * 0.9)
        y_max = metric_data.max() * 1.1

        layout = get_chart_layout(height=chart_height)
        layout['yaxis']['title'] = metric_label
        layout['yaxis']['range'] = [y_min, y_max]
        layout['showlegend'] = False
        layout['title'] = dict(text=f'<b>{scope_name}</b>', font=dict(size=14, color='#E8E8E8'), x=0.5)
        # X-axis: clean date format, no range slider
        layout['xaxis'] = dict(
            tickformat='%b %Y',  # Jan 2023, Feb 2023, etc.
            tickmode='auto',
            nticks=8,
            tickangle=0,
            tickfont=dict(size=10, color='#CBD5E1'),
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            rangeslider=dict(visible=False)
        )
        # Add padding on right side for better visibility of latest data
        if not plot_df.empty and 'date' in plot_df.columns:
            last_date = pd.to_datetime(plot_df['date'].max())
            padding_days = max(30, len(plot_df) // 20)  # ~5% padding
            layout['xaxis']['range'] = [plot_df['date'].min(), last_date + timedelta(days=padding_days)]
        fig.update_layout(**layout)

        # Calculate stats for display
        z_score = (current_val - mean_val) / std_val if std_val > 0 else 0
        percentile = (metric_data < current_val).mean() * 100

        stats = {
            'current': current_val,
            'median': median_val,
            'z_score': z_score,
            'percentile': percentile
        }

        return fig, stats

    # Individual scope analysis (Market Index or Sector)
    if selected_scope:
        history = load_sector_history(selected_scope, days)
        fig, stats = create_individual_chart(selected_scope, history, primary_metric, selected_metric, chart_height=500)

        if fig:
            st.plotly_chart(fig, use_container_width=True)

            # Current position analysis
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current", f"{stats['current']:.2f}x")
            with col2:
                st.metric("Median", f"{stats['median']:.2f}x")
            with col3:
                st.metric("Z-Score", f"{stats['z_score']:+.2f}σ")
            with col4:
                st.metric("Percentile", f"{stats['percentile']:.0f}%")

            # Valuation assessment
            if stats['z_score'] < -1:
                assessment = "🟢 **Significantly Undervalued** - More than 1σ below mean"
            elif stats['z_score'] < 0:
                assessment = "🟢 **Undervalued** - Below historical mean"
            elif stats['z_score'] < 1:
                assessment = "🟡 **Fair Value** - Near historical mean"
            else:
                assessment = "🔴 **Expensive** - More than 1σ above mean"

            st.markdown(f"**Assessment**: {assessment}")
        else:
            st.warning(f"Not enough valid data for {selected_scope}")

# ============================================================================
# TAB 3: MACRO DATA
# ============================================================================
with tab_macro:
    st.markdown("### Macro Economic Indicators")
    st.markdown("*Interest rates, exchange rates, and government bond yields*")

    # Initialize loader
    macro_loader = MacroCommodityLoader()
    macro_df = macro_loader.get_macro()

    if macro_df.empty:
        st.warning("No macro data available. Please run the daily update pipeline.")
    else:
        # Get available macro symbols
        macro_symbols = macro_df['symbol'].unique().tolist()

        # Group indicators
        interest_rate_symbols = [s for s in macro_symbols if 'ls_' in s]
        exchange_rate_symbols = [s for s in macro_symbols if 'ty_gia' in s]
        bond_symbols = [s for s in macro_symbols if 'bond' in s]

        # Vietnamese labels for macro indicators
        macro_labels = {
            'ls_huy_dong_13_thang': 'Lãi suất huy động 13 tháng',
            'ls_huy_dong_1_3_thang': 'Lãi suất huy động 1-3 tháng',
            'ls_huy_dong_6_9_thang': 'Lãi suất huy động 6-9 tháng',
            'ls_lien_ngan_hang_ky_han_1_tuan': 'LS liên NH kỳ hạn 1 tuần',
            'ls_lien_ngan_hang_ky_han_2_tuan': 'LS liên NH kỳ hạn 2 tuần',
            'ls_qua_dem_lien_ngan_hang': 'LS qua đêm liên NH',
            'ty_gia_san': 'Tỷ giá sàn',
            'ty_gia_tran': 'Tỷ giá trần',
            'ty_gia_usd_nhtm_ban_ra': 'Tỷ giá USD NHTM bán ra',
            'ty_gia_usd_trung_tam': 'Tỷ giá USD trung tâm',
            'ty_gia_usd_tu_do_ban_ra': 'Tỷ giá USD tự do bán ra',
            'vn_gov_bond_5y': 'Lợi suất TPCP 5 năm'
        }

        # Selector for indicator type
        macro_type = st.radio(
            "Select Category",
            options=["💰 Lãi suất huy động", "🏦 Lãi suất liên ngân hàng", "💱 Tỷ giá USD", "📜 Trái phiếu CP"],
            horizontal=True
        )

        # =============================================
        # EXCHANGE RATE: Dual-axis chart section
        # =============================================
        if macro_type == "💱 Tỷ giá USD":
            # Dual-axis pairs for exchange rates (comparing different USD rates)
            exchange_dual_axis_pairs = {
                "💱 USD Trung tâm vs Tự do": ('ty_gia_usd_trung_tam', 'ty_gia_usd_tu_do_ban_ra', 'VND (TT)', 'VND (Tự do)'),
                "🏦 USD NHTM vs Tự do": ('ty_gia_usd_nhtm_ban_ra', 'ty_gia_usd_tu_do_ban_ra', 'VND (NHTM)', 'VND (Tự do)'),
                "📊 Tỷ giá Sàn vs Trần": ('ty_gia_san', 'ty_gia_tran', 'VND (Sàn)', 'VND (Trần)'),
            }

            # Individual exchange rates (not in pairs)
            exchange_individual = {
                "📌 USD Trung tâm": 'ty_gia_usd_trung_tam',
                "🏛️ USD NHTM bán ra": 'ty_gia_usd_nhtm_ban_ra',
                "💵 USD Tự do bán ra": 'ty_gia_usd_tu_do_ban_ra',
                "📉 Tỷ giá sàn": 'ty_gia_san',
                "📈 Tỷ giá trần": 'ty_gia_tran',
            }

            # Combined options: dual-axis pairs first, then individual
            all_exchange_options = list(exchange_dual_axis_pairs.keys()) + ["---"] + list(exchange_individual.keys())

            selected_exchange = st.selectbox(
                "Select Exchange Rate View",
                options=[opt for opt in all_exchange_options if opt != "---"],
                index=0,
                label_visibility="visible"
            )

            if selected_exchange in exchange_dual_axis_pairs:
                # Single-axis chart for exchange rate comparison (same unit VND)
                symbol1, symbol2, unit1, unit2 = exchange_dual_axis_pairs[selected_exchange]

                series1 = filter_series_by_days(macro_loader.get_series(symbol1), days)
                series2 = filter_series_by_days(macro_loader.get_series(symbol2), days)

                if not series1.empty and not series2.empty:
                    label1 = macro_labels.get(symbol1, symbol1)
                    label2 = macro_labels.get(symbol2, symbol2)

                    # Single-axis chart (same VND unit) to show gap clearly
                    fig_exchange = go.Figure()

                    # First series
                    fig_exchange.add_trace(
                        go.Scatter(
                            x=series1['date'],
                            y=series1['value'],
                            name=label1,
                            mode='lines',
                            line=dict(color=CHART_COLORS['primary'], width=2.5),
                            hovertemplate=f'<b>{label1}</b><br>Date: %{{x|%d/%m/%Y}}<br>Value: %{{y:,.0f}} VND<extra></extra>'
                        )
                    )

                    # Second series
                    fig_exchange.add_trace(
                        go.Scatter(
                            x=series2['date'],
                            y=series2['value'],
                            name=label2,
                            mode='lines',
                            line=dict(color=CHART_COLORS['tertiary'], width=2.5),
                            hovertemplate=f'<b>{label2}</b><br>Date: %{{x|%d/%m/%Y}}<br>Value: %{{y:,.0f}} VND<extra></extra>'
                        )
                    )

                    # Calculate y-axis range starting from 0
                    all_values = list(series1['value'].dropna()) + list(series2['value'].dropna())
                    y_max = max(all_values) * 1.05 if all_values else 30000

                    layout = get_chart_layout(height=500)
                    layout['showlegend'] = True
                    layout['legend'] = dict(
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='center',
                        x=0.5,
                        font=dict(size=11, color='#E8E8E8')
                    )
                    # X-axis formatting - clean date format, no grid
                    layout['xaxis'] = dict(
                        tickformat='%b %Y',
                        tickmode='auto',
                        nticks=8,
                        tickangle=0,
                        tickfont=dict(size=10, color='#CBD5E1'),
                        showgrid=False,
                        zeroline=False,
                        showline=True,
                        linecolor='rgba(255,255,255,0.2)'
                    )
                    # Y-axis - single axis, start from 0, no grid
                    layout['yaxis'] = dict(
                        title='VND',
                        title_font=dict(color='#E8E8E8'),
                        tickfont=dict(size=10, color='#CBD5E1'),
                        tickformat=',d',
                        showgrid=False,
                        zeroline=False,
                        range=[0, y_max],  # Start from 0
                        showline=True,
                        linecolor='rgba(255,255,255,0.2)'
                    )
                    layout['plot_bgcolor'] = 'rgba(0,0,0,0)'
                    fig_exchange.update_layout(**layout)

                    st.plotly_chart(fig_exchange, use_container_width=True)

                    # Show latest values
                    st.markdown("### Latest Values & Spread")
                    latest1 = series1.iloc[-1]['value']
                    latest2 = series2.iloc[-1]['value']
                    spread = latest2 - latest1
                    spread_pct = (spread / latest1) * 100 if latest1 > 0 else 0

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label1, f"{latest1:,.0f} VND")
                    with col2:
                        st.metric(label2, f"{latest2:,.0f} VND")
                    with col3:
                        st.metric("Spread (Chênh lệch)", f"{spread:+,.0f} VND", f"{spread_pct:+.2f}%")
                else:
                    st.warning("Data not available for selected exchange rate pair")

            elif selected_exchange in exchange_individual:
                # Single exchange rate chart
                symbol = exchange_individual[selected_exchange]
                series = filter_series_by_days(macro_loader.get_series(symbol), days)

                if not series.empty and 'value' in series.columns:
                    label = macro_labels.get(symbol, symbol)

                    fig_single = go.Figure()
                    fig_single.add_trace(go.Scatter(
                        x=series['date'],
                        y=series['value'],
                        name=label,
                        mode='lines',
                        line=dict(color=CHART_COLORS['primary'], width=2),
                        fill='tozeroy',
                        fillcolor=f"rgba(0, 255, 136, 0.1)",
                        hovertemplate=f'<b>{label}</b><br>Date: %{{x}}<br>Value: %{{y:,.0f}} VND<extra></extra>'
                    ))

                    layout = get_chart_layout(height=500)
                    layout['yaxis']['title'] = 'VND'
                    layout['yaxis']['tickformat'] = ',d'
                    # X-axis formatting - clean date format
                    layout['xaxis'] = dict(
                        tickformat='%b %Y',
                        tickmode='auto',
                        nticks=8,
                        tickangle=0,
                        tickfont=dict(size=10, color='#CBD5E1'),
                        showgrid=True,
                        gridcolor='rgba(255,255,255,0.05)'
                    )
                    fig_single.update_layout(**layout)

                    st.plotly_chart(fig_single, use_container_width=True)

                    # Latest value
                    latest = series.iloc[-1]
                    st.markdown("### Latest Value")
                    st.metric(label, f"{latest['value']:,.0f} VND",
                             delta=None,
                             help=f"Last updated: {latest['date'].strftime('%Y-%m-%d') if pd.notna(latest['date']) else '-'}")
                else:
                    st.warning("Data not available for selected exchange rate")

        # =============================================
        # OTHER MACRO CATEGORIES: Standard charts
        # =============================================
        else:
            if macro_type == "💰 Lãi suất huy động":
                target_symbols = [s for s in macro_symbols if 'ls_huy_dong' in s]
            elif macro_type == "🏦 Lãi suất liên ngân hàng":
                target_symbols = [s for s in macro_symbols if 'ls_lien_ngan_hang' in s or 'ls_qua_dem' in s]
            else:
                target_symbols = bond_symbols

            if target_symbols:
                # Create line chart
                fig_macro = go.Figure()
                colors = [CHART_COLORS['primary'], CHART_COLORS['secondary'], CHART_COLORS['tertiary'],
                         '#FF6B6B', '#4ECDC4', '#45B7D1']

                for i, symbol in enumerate(target_symbols):
                    series = filter_series_by_days(macro_loader.get_series(symbol), days)
                    if not series.empty and 'value' in series.columns:
                        label = macro_labels.get(symbol, symbol)
                        fig_macro.add_trace(go.Scatter(
                            x=series['date'],
                            y=series['value'],
                            name=label,
                            mode='lines',
                            line=dict(color=colors[i % len(colors)], width=2),
                            hovertemplate=f'<b>{label}</b><br>Date: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>'
                        ))

                layout = get_chart_layout(height=500)
                layout['showlegend'] = True
                layout['legend'] = dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5,
                    font=dict(size=10, color='#E8E8E8')
                )
                layout['yaxis']['title'] = 'Value (%)'
                # X-axis formatting - clean date format
                layout['xaxis'] = dict(
                    tickformat='%b %Y',
                    tickmode='auto',
                    nticks=8,
                    tickangle=0,
                    tickfont=dict(size=10, color='#CBD5E1'),
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.05)'
                )
                fig_macro.update_layout(**layout)

                st.plotly_chart(fig_macro, use_container_width=True)

                # Latest values table
                st.markdown("### Latest Values")
                latest_data = []
                for symbol in target_symbols:
                    series = macro_loader.get_series(symbol)
                    if not series.empty and 'value' in series.columns:
                        latest = series.iloc[-1]
                        latest_data.append({
                            'Indicator': macro_labels.get(symbol, symbol),
                            'Value': f"{latest['value']:.2f}",
                            'Unit': latest.get('unit', '%'),
                            'Date': latest['date'].strftime('%Y-%m-%d') if pd.notna(latest['date']) else '-'
                        })

                if latest_data:
                    latest_df = pd.DataFrame(latest_data)
                    st.markdown(render_styled_table(latest_df), unsafe_allow_html=True)
            else:
                st.info("No data available for selected category")

# ============================================================================
# TAB 4: COMMODITY DATA
# ============================================================================
with tab_commodity:
    st.markdown("### Commodity Prices")
    st.markdown("*Individual commodities with dual-axis charts for comparison pairs*")

    # Initialize loader
    commodity_loader = MacroCommodityLoader()
    commodity_df = commodity_loader.get_commodities()

    if commodity_df.empty:
        st.warning("No commodity data available. Please run the daily update pipeline.")
    else:
        # Get available commodity symbols
        commodity_symbols = commodity_df['symbol'].unique().tolist()

        # Vietnamese labels for commodities
        commodity_labels = {
            'gold_vn': 'Vàng Việt Nam',
            'gold_global': 'Vàng Thế giới',
            'oil_crude': 'Dầu thô WTI',
            'gas_natural': 'Khí thiên nhiên',
            'coke': 'Than cốc',
            'steel_d10': 'Thép thanh HPG (D10)',
            'steel_hrc': 'Thép HRC',
            'steel_coated': 'Tôn mạ HSG',
            'iron_ore': 'Quặng sắt',
            'fertilizer_ure_global': 'Ure Trung Đông',
            'fertilizer_ure_vn': 'Ure Phú Mỹ',
            'soybean': 'Đậu tương',
            'corn': 'Ngô (Bắp)',
            'sugar': 'Đường',
            'pork_north_vn': 'Heo hơi Miền Bắc VN',
            'pork_china': 'Heo hơi Trung Quốc',
            'pvc': 'PVC China',
            'cao_su': 'Cao su',
            'sua_bot_wmp': 'Sữa bột WMP'
        }

        # Dual-axis pairs (VN vs Global/China comparison)
        dual_axis_pairs = {
            "🥇 Vàng (VN vs Thế giới)": ('gold_vn', 'gold_global', 'VND/lượng', 'USD/oz'),
            "🐷 Heo hơi (VN vs Trung Quốc)": ('pork_north_vn', 'pork_china', 'VND/kg', 'CNY/kg'),
            "🧪 Phân bón Ure (VN vs Trung Đông)": ('fertilizer_ure_vn', 'fertilizer_ure_global', 'VND/kg', 'USD/tấn'),
        }

        # Individual commodities (single axis)
        individual_commodities = [
            ('oil_crude', '🛢️ Dầu thô WTI'),
            ('gas_natural', '⛽ Khí thiên nhiên'),
            ('coke', '�ite Than cốc'),
            ('steel_d10', '🔩 Thép thanh HPG (D10)'),
            ('steel_hrc', '🔩 Thép HRC'),
            ('steel_coated', '🔩 Tôn mạ HSG'),
            ('iron_ore', '�ite Quặng sắt'),
            ('soybean', '🌾 Đậu tương'),
            ('corn', '🌽 Ngô (Bắp)'),
            ('sugar', '🍬 Đường'),
            ('cao_su', '🌳 Cao su'),
            ('pvc', '🧪 PVC China'),
            ('sua_bot_wmp', '🥛 Sữa bột WMP'),
        ]

        # Build options list: dual pairs first, then individual
        all_options = list(dual_axis_pairs.keys()) + [label for _, label in individual_commodities if _ in commodity_symbols]

        selected_commodity = st.selectbox(
            "Select Commodity",
            options=all_options,
            index=0
        )

        # Check if selected is a dual-axis pair
        if selected_commodity in dual_axis_pairs:
            # DUAL-AXIS CHART
            symbol1, symbol2, unit1, unit2 = dual_axis_pairs[selected_commodity]

            series1 = filter_series_by_days(commodity_loader.get_series(symbol1), days)
            series2 = filter_series_by_days(commodity_loader.get_series(symbol2), days)

            if not series1.empty or not series2.empty:
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # First series (left Y-axis)
                if not series1.empty:
                    value_col1 = 'close' if 'close' in series1.columns and series1['close'].notna().any() else 'value'
                    fig.add_trace(
                        go.Scatter(
                            x=series1['date'],
                            y=series1[value_col1],
                            name=commodity_labels.get(symbol1, symbol1),
                            mode='lines',
                            line=dict(color=CHART_COLORS['primary'], width=2.5),
                            hovertemplate=f'<b>{commodity_labels.get(symbol1, symbol1)}</b><br>%{{x}}<br>%{{y:,.0f}} {unit1}<extra></extra>'
                        ),
                        secondary_y=False
                    )

                # Second series (right Y-axis)
                if not series2.empty:
                    value_col2 = 'close' if 'close' in series2.columns and series2['close'].notna().any() else 'value'
                    fig.add_trace(
                        go.Scatter(
                            x=series2['date'],
                            y=series2[value_col2],
                            name=commodity_labels.get(symbol2, symbol2),
                            mode='lines',
                            line=dict(color=CHART_COLORS['tertiary'], width=2.5),
                            hovertemplate=f'<b>{commodity_labels.get(symbol2, symbol2)}</b><br>%{{x}}<br>%{{y:,.0f}} {unit2}<extra></extra>'
                        ),
                        secondary_y=True
                    )

                # Layout
                layout = get_chart_layout(height=500)
                layout['showlegend'] = True
                layout['legend'] = dict(
                    orientation='h', yanchor='bottom', y=1.02,
                    xanchor='center', x=0.5, font=dict(size=11, color='#E8E8E8')
                )
                layout['xaxis'] = dict(
                    tickformat='%b %Y', tickmode='auto', nticks=8, tickangle=0,
                    tickfont=dict(size=10, color='#CBD5E1'),
                    showgrid=True, gridcolor='rgba(255,255,255,0.05)'
                )
                fig.update_layout(**layout)

                # Y-axis titles
                fig.update_yaxes(title_text=f"{commodity_labels.get(symbol1, symbol1)} ({unit1})",
                                secondary_y=False, title_font=dict(color=CHART_COLORS['primary']))
                fig.update_yaxes(title_text=f"{commodity_labels.get(symbol2, symbol2)} ({unit2})",
                                secondary_y=True, title_font=dict(color=CHART_COLORS['tertiary']))

                st.plotly_chart(fig, use_container_width=True)

                # Latest values
                st.markdown("### Latest Prices")
                latest_data = []
                for sym, unit in [(symbol1, unit1), (symbol2, unit2)]:
                    series = commodity_loader.get_series(sym)
                    if not series.empty:
                        latest = series.iloc[-1]
                        value_col = 'close' if 'close' in series.columns and pd.notna(latest.get('close')) else 'value'
                        value = latest.get(value_col, 0)
                        latest_data.append({
                            'Commodity': commodity_labels.get(sym, sym),
                            'Price': f"{value:,.0f}",
                            'Unit': unit,
                            'Date': latest['date'].strftime('%Y-%m-%d') if pd.notna(latest['date']) else '-'
                        })
                if latest_data:
                    st.markdown(render_styled_table(pd.DataFrame(latest_data)), unsafe_allow_html=True)
            else:
                st.warning("No data available for this pair")

        else:
            # SINGLE COMMODITY CHART
            # Find symbol from label
            symbol = None
            for sym, label in individual_commodities:
                if label == selected_commodity:
                    symbol = sym
                    break

            if symbol and symbol in commodity_symbols:
                series = filter_series_by_days(commodity_loader.get_series(symbol), days)

                if not series.empty:
                    value_col = 'close' if 'close' in series.columns and series['close'].notna().any() else 'value'

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=series['date'],
                        y=series[value_col],
                        name=commodity_labels.get(symbol, symbol),
                        mode='lines',
                        line=dict(color=CHART_COLORS['primary'], width=2.5),
                        fill='tozeroy',
                        fillcolor='rgba(45, 212, 191, 0.1)',
                        hovertemplate=f'<b>{commodity_labels.get(symbol, symbol)}</b><br>%{{x}}<br>Price: %{{y:,.0f}}<extra></extra>'
                    ))

                    layout = get_chart_layout(height=500)
                    layout['showlegend'] = False
                    layout['yaxis']['title'] = 'Price'
                    layout['xaxis'] = dict(
                        tickformat='%b %Y', tickmode='auto', nticks=8, tickangle=0,
                        tickfont=dict(size=10, color='#CBD5E1'),
                        showgrid=True, gridcolor='rgba(255,255,255,0.05)'
                    )
                    fig.update_layout(**layout)

                    st.plotly_chart(fig, use_container_width=True)

                    # Latest value
                    latest = series.iloc[-1]
                    value = latest.get(value_col, 0)
                    change_pct = None
                    if len(series) > 1:
                        prev = series[value_col].iloc[-2]
                        if prev and prev != 0:
                            change_pct = ((value - prev) / prev) * 100

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Latest Price", f"{value:,.0f}")
                    with col2:
                        st.metric("Change", f"{change_pct:+.2f}%" if change_pct else "-")
                    with col3:
                        st.metric("Date", latest['date'].strftime('%Y-%m-%d') if pd.notna(latest['date']) else '-')
                else:
                    st.warning(f"No data available for {selected_commodity}")
            else:
                st.warning("Commodity not found")

# ============================================================================
# TAB 5: DATA TABLES
# ============================================================================
with tab_tables:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Sector Valuation Overview")

        if not sector_df.empty:
            display_cols = ['scope', 'pe_ttm', 'pb']
            if 'pe_fwd_2025' in sector_df.columns:
                display_cols.append('pe_fwd_2025')

            display_df = sector_df[display_cols].copy()
            # Remove SECTOR: prefix for cleaner display
            display_df['scope'] = display_df['scope'].str.replace('SECTOR:', '', regex=False)
            display_df.columns = ['Sector', 'PE TTM', 'PB'] + (['PE Fwd 2025'] if 'pe_fwd_2025' in display_cols else [])

            # Format numbers
            for col in display_df.columns[1:]:
                display_df[col] = display_df[col].apply(lambda x: f'{x:.2f}x' if pd.notna(x) and x > 0 else '-')

            st.markdown(render_styled_table(display_df), unsafe_allow_html=True)

    with col2:
        st.markdown("### Sector Composition")

        all_sectors = service.get_all_sectors()
        composition_data = []

        for sector in all_sectors:
            tickers = service.get_sector_tickers(sector)
            composition_data.append({
                'Sector': sector,
                'Tickers': len(tickers),
                'Top 5': ', '.join(tickers[:5]) if tickers else '-'
            })

        if composition_data:
            comp_df = pd.DataFrame(composition_data)
            st.markdown(render_styled_table(comp_df), unsafe_allow_html=True)

    st.markdown("---")

    # Download button (Excel)
    if not sector_df.empty:
        excel_buffer = BytesIO()
        sector_df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)
        st.download_button(
            "📥 Download Sector Data (Excel)",
            excel_buffer,
            "sector_valuation.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.caption(f"Data: Sector Analysis | {len(service.get_all_sectors())} sectors tracked | Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
