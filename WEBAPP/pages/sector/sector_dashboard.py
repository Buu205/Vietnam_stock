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

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from WEBAPP.services.sector_service import SectorService
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

# Days selector - max data available (since 2018)
days = st.sidebar.slider("History (Days)", min_value=30, max_value=2000, value=1000)

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
tab_distribution, tab_individual, tab_tables = st.tabs([
    "🕯️ All Sectors Distribution",
    "📈 Individual Analysis",
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
        st.markdown("*Candlestick shows P5-P95 range (whiskers), P25-P75 (body). Red dot = current value.*")

        target_scopes = sector_scopes if sector_scopes else []

        if target_scopes:
            fig_candle = go.Figure()
            valid_items = []
            distribution_data = []

            for scope in target_scopes:
                # Load historical data
                history = load_sector_history(scope, days)

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

                p5 = clean_data.quantile(0.05)
                p25 = clean_data.quantile(0.25)
                p50 = clean_data.quantile(0.50)
                p75 = clean_data.quantile(0.75)
                p95 = clean_data.quantile(0.95)

                # Store for table
                if current_val:
                    percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100
                    distribution_data.append({
                        'Scope': scope,
                        'Current': current_val,
                        'P5': p5,
                        'P25': p25,
                        'Median': p50,
                        'P75': p75,
                        'P95': p95,
                        'Percentile': percentile
                    })

                # Add candlestick
                fig_candle.add_trace(go.Candlestick(
                    x=[scope],
                    open=[round(p25, 2)],
                    high=[round(p95, 2)],
                    low=[round(p5, 2)],
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
                layout = get_chart_layout(height=550)
                layout['xaxis'] = dict(
                    categoryorder='array',
                    categoryarray=valid_items,
                    rangeslider=dict(visible=False),
                    tickangle=-45,
                    tickfont=dict(size=10, family='Source Sans 3')
                )
                layout['yaxis']['title'] = selected_metric

                if primary_metric == 'pb':
                    layout['yaxis']['range'] = [0, 8]
                elif primary_metric == 'pe_ttm':
                    layout['yaxis']['range'] = [0, 50]

                fig_candle.update_layout(**layout)

                st.plotly_chart(fig_candle, use_container_width=True)

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
                    for col in ['Current', 'P5', 'P25', 'Median', 'P75', 'P95']:
                        dist_df_display[col] = dist_df_display[col].apply(lambda x: f'{x:.2f}x')
                    dist_df_display['Percentile'] = dist_df_display['Percentile'].apply(lambda x: f'{x:.0f}%')

                    st.markdown(render_styled_table(dist_df_display), unsafe_allow_html=True)

                    csv_data = dist_df_raw.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        f"📥 Download {selected_metric} Distribution Data (CSV)",
                        csv_data,
                        f"{selected_metric.lower().replace(' ', '_')}_distribution_sectors.csv",
                        "text/csv",
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
                    tickfont=dict(size=10, family='Source Sans 3', color='#A0AEC0'),
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

                # CSV download
                csv_data = stats_df_raw.to_csv(index=False).encode('utf-8')
                st.download_button(
                    f"📥 Download Market Indices {selected_metric} Statistics (CSV)",
                    csv_data,
                    f"market_indices_{primary_metric}_statistics_{days}d.csv",
                    "text/csv",
                    use_container_width=True
                )
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

    # For Market Indices: 4 options - Combined + 3 individual indices
    show_combined = False
    selected_scope = None

    with col2:
        if scope_group == "Market Indices":
            # 4 options: Combined + 3 individual indices
            index_options = ["📊 Combined (All 3)"] + index_scopes
            selected_index_option = st.selectbox(
                "Select View",
                options=index_options,
                index=0,
                label_visibility="collapsed"
            )

            if selected_index_option == "📊 Combined (All 3)":
                show_combined = True
                selected_scope = None
            else:
                show_combined = False
                selected_scope = selected_index_option
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
        # Add range slider always visible
        layout['xaxis']['rangeslider'] = dict(
            visible=True,
            bgcolor='rgba(16, 24, 32, 0.8)',
            thickness=0.08
        )
        # Add padding on right side for better visibility of latest data
        if not plot_df.empty and 'date' in plot_df.columns:
            from datetime import timedelta
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

    # Show Combined chart (all 3 indices on same chart)
    if show_combined and scope_group == "Market Indices" and index_scopes:
        st.markdown("#### All Market Indices - Combined View")

        # Create combined chart with all 3 indices - using brand colors
        fig_combined = go.Figure()
        line_colors = [CHART_COLORS['primary'], CHART_COLORS['secondary'], CHART_COLORS['tertiary']]  # Teal, Blue, Gold
        all_stats = []

        for i, idx_scope in enumerate(index_scopes[:3]):
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

            # Add line trace for this index
            fig_combined.add_trace(go.Scatter(
                x=plot_df['date'],
                y=plot_df[primary_metric],
                name=idx_scope,
                mode='lines',
                line=dict(color=line_colors[i], width=2.5),
                hovertemplate=f'<b>{idx_scope}</b><br>Date: %{{x}}<br>{selected_metric}: %{{y:.2f}}x<extra></extra>'
            ))

        if all_stats:
            # Auto-scale based on all data
            all_values = []
            for idx_scope in index_scopes[:3]:
                hist = load_sector_history(idx_scope, days)
                if not hist.empty and primary_metric in hist.columns:
                    vals = hist[primary_metric].dropna()
                    if primary_metric == 'pe_ttm':
                        vals = vals[(vals > 0) & (vals <= 100)]
                    else:
                        vals = vals[(vals >= 0) & (vals <= 100)]
                    all_values.extend(vals.tolist())

            if all_values:
                y_min = max(0, min(all_values) * 0.9)
                y_max = max(all_values) * 1.1
            else:
                y_min, y_max = 0, 100

            layout = get_chart_layout(height=500)
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
            # Add range slider always visible
            layout['xaxis']['rangeslider'] = dict(
                visible=True,
                bgcolor='rgba(16, 24, 32, 0.8)',
                thickness=0.08
            )
            fig_combined.update_layout(**layout)

            st.plotly_chart(fig_combined, use_container_width=True)

            # Stats table
            stats_df = pd.DataFrame(all_stats)
            for col in ['Current', 'Median', 'Mean']:
                stats_df[col] = stats_df[col].apply(lambda x: f'{x:.2f}x')
            stats_df['Z-Score'] = stats_df['Z-Score'].apply(lambda x: f'{x:+.2f}σ')
            stats_df['Percentile'] = stats_df['Percentile'].apply(lambda x: f'{x:.0f}%')

            st.markdown("#### Statistics Comparison")
            st.markdown(render_styled_table(stats_df), unsafe_allow_html=True)

            # CSV download for Combined View
            csv_raw_df = pd.DataFrame(all_stats)  # Use raw unformatted data
            csv_data = csv_raw_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                f"📥 Download Market Indices {selected_metric} Statistics (CSV)",
                csv_data,
                f"market_indices_{primary_metric}_statistics_{days}d.csv",
                "text/csv",
                use_container_width=True
            )
        else:
            st.warning("No valid data for any index")

    # Single scope analysis
    elif selected_scope:
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
# TAB 3: DATA TABLES
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

    # Download button
    if not sector_df.empty:
        csv = sector_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Sector Data (CSV)",
            csv,
            "sector_valuation.csv",
            "text/csv",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.caption(f"Data: Sector Analysis | {len(service.get_all_sectors())} sectors tracked | Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
