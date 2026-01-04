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
import html

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from WEBAPP.services.sector_service import SectorService
from WEBAPP.services.macro_commodity_loader import MacroCommodityLoader
from WEBAPP.core.styles import (
    get_page_style, get_chart_layout,
    CHART_COLORS, BAR_COLORS, DISTRIBUTION_COLORS, ASSESSMENT_COLORS, BAND_COLORS,
    render_styled_table, get_table_style, render_valuation_legend, render_valuation_assessment,
)
# Import centralized valuation config and chart components
from WEBAPP.core.valuation_config import (
    OUTLIER_LIMITS, STATUS_COLORS, CHART_COLORS as VAL_CHART_COLORS,
    format_ratio, format_percent, format_zscore,
    get_status_color, get_percentile_status, get_status_label, render_status_badge, filter_outliers
)
from WEBAPP.components.charts.valuation_charts import (
    distribution_candlestick,
    line_with_statistical_bands,
    histogram_with_stats,
    render_status_legend
)
from WEBAPP.core.chart_schema import get_chart_config, get_y_range, CHART_SCHEMA
from WEBAPP.components.filters.global_filter_bar import render_global_filters
from WEBAPP.core.session_state import init_page_state, render_persistent_tabs

# Note: st.set_page_config is handled by main_app.py

# Inject premium styles
st.markdown(get_page_style(), unsafe_allow_html=True)
st.markdown(get_table_style(), unsafe_allow_html=True)

# Initialize session state for this page
init_page_state('sector')

# Header
st.title("Sector Analysis")
st.markdown("**Real-time sector valuation comparison across Vietnamese equity markets**")

# ============================================================================
# GLOBAL FILTER BAR (Horizontal, replaces sidebar filters)
# ============================================================================
st.markdown('<div class="filter-bar-container">', unsafe_allow_html=True)
filters = render_global_filters(
    show_metric=True,
    show_time_range=True,
    show_refresh=True,
    key_prefix="sector"
)
st.markdown('</div>', unsafe_allow_html=True)

# Extract filter values
selected_metric = filters.get('metric', "PE")
primary_metric = filters.get('metric_col', "pe_ttm")
days = filters.get('days', 756)
days_distribution = 2000  # Always use ALL for distribution

# Handle refresh
if filters.get('refresh'):
    st.rerun()

st.markdown("---")

try:
    service = SectorService()
except Exception as e:
    st.error(f"Failed to initialize service: {e}")
    st.stop()

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

@st.cache_data(ttl=3600)
def load_stock_valuation(ticker: str, limit: int = 1000):
    """Load individual stock valuation history (PE, PB, PS, EV/EBITDA) from parquet files"""
    from pathlib import Path

    data_path = Path(__file__).resolve().parents[3] / "DATA" / "processed" / "valuation"

    pe_file = data_path / "pe" / "historical" / "historical_pe.parquet"
    pb_file = data_path / "pb" / "historical" / "historical_pb.parquet"
    ps_file = data_path / "ps" / "historical" / "historical_ps.parquet"
    ev_file = data_path / "ev_ebitda" / "historical" / "historical_ev_ebitda.parquet"

    result = pd.DataFrame()

    # Load PE
    if pe_file.exists():
        pe_df = pd.read_parquet(pe_file)
        if 'symbol' in pe_df.columns:
            pe_ticker = pe_df[pe_df['symbol'] == ticker].copy()
            if not pe_ticker.empty:
                pe_ticker = pe_ticker.sort_values('date')
                if limit:
                    pe_ticker = pe_ticker.tail(limit)
                if 'pe_ratio' in pe_ticker.columns:
                    pe_ticker['pe_ttm'] = pe_ticker['pe_ratio']
                result = pe_ticker

    # Load PB
    if pb_file.exists():
        pb_df = pd.read_parquet(pb_file)
        if 'symbol' in pb_df.columns:
            pb_ticker = pb_df[pb_df['symbol'] == ticker].copy()
            if not pb_ticker.empty:
                pb_ticker = pb_ticker.sort_values('date')
                if limit:
                    pb_ticker = pb_ticker.tail(limit)
                if 'pb_ratio' in pb_ticker.columns:
                    pb_ticker['pb'] = pb_ticker['pb_ratio']
                elif 'pb' not in pb_ticker.columns and 'close_price' in pb_ticker.columns and 'book_value' in pb_ticker.columns:
                    pb_ticker['pb'] = pb_ticker['close_price'] / pb_ticker['book_value']

                if result.empty:
                    result = pb_ticker
                else:
                    pb_cols = ['date', 'symbol', 'pb'] if 'pb' in pb_ticker.columns else ['date', 'symbol']
                    result = result.merge(pb_ticker[pb_cols], on=['date', 'symbol'], how='outer')

    # Load P/S
    if ps_file.exists():
        ps_df = pd.read_parquet(ps_file)
        if 'symbol' in ps_df.columns:
            ps_ticker = ps_df[ps_df['symbol'] == ticker].copy()
            if not ps_ticker.empty:
                ps_ticker = ps_ticker.sort_values('date')
                if limit:
                    ps_ticker = ps_ticker.tail(limit)
                if 'ps_ratio' in ps_ticker.columns:
                    ps_ticker['ps'] = ps_ticker['ps_ratio']

                if result.empty:
                    result = ps_ticker
                else:
                    ps_cols = ['date', 'symbol', 'ps'] if 'ps' in ps_ticker.columns else ['date', 'symbol']
                    result = result.merge(ps_ticker[ps_cols], on=['date', 'symbol'], how='outer')

    # Load EV/EBITDA
    if ev_file.exists():
        ev_df = pd.read_parquet(ev_file)
        if 'symbol' in ev_df.columns:
            ev_ticker = ev_df[ev_df['symbol'] == ticker].copy()
            if not ev_ticker.empty:
                ev_ticker = ev_ticker.sort_values('date')
                if limit:
                    ev_ticker = ev_ticker.tail(limit)

                if result.empty:
                    result = ev_ticker
                else:
                    ev_cols = ['date', 'symbol', 'ev_ebitda'] if 'ev_ebitda' in ev_ticker.columns else ['date', 'symbol']
                    result = result.merge(ev_ticker[ev_cols], on=['date', 'symbol'], how='outer')

    return result.sort_values('date') if not result.empty else pd.DataFrame()

@st.cache_data(ttl=3600)
def get_sector_tickers(sector: str):
    """Get all tickers in a sector"""
    return SectorService().get_sector_tickers(sector)

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
# MARKET OVERVIEW - Removed (cards moved to summary section)
# ============================================================================

# ============================================================================
# TABS (Session State Persisted)
# ============================================================================
active_tab = render_persistent_tabs(
    ["VN-Index", "Valuation", "Data"],
    "sector_active_tab"
)

# ============================================================================
# TAB 0: VNINDEX ANALYSIS
# ============================================================================
if active_tab == 0:
    # Load vnindex data
    @st.cache_data(ttl=3600)
    def load_vnindex_data():
        vnindex_file = service.data_root / "processed" / "valuation" / "vnindex" / "vnindex_valuation_refined.parquet"
        if vnindex_file.exists():
            df = pd.read_parquet(vnindex_file)
            df['date'] = pd.to_datetime(df['date'])
            return df
        return pd.DataFrame()

    vnindex_df = load_vnindex_data()

    if not vnindex_df.empty:
        # Get latest values for 3 variants
        latest_vnindex = vnindex_df[vnindex_df['scope'] == 'VNINDEX'].sort_values('date').iloc[-1] if len(vnindex_df[vnindex_df['scope'] == 'VNINDEX']) > 0 else None
        latest_vnindex_exclude = vnindex_df[vnindex_df['scope'] == 'VNINDEX_EXCLUDE'].sort_values('date').iloc[-1] if len(vnindex_df[vnindex_df['scope'] == 'VNINDEX_EXCLUDE']) > 0 else None
        latest_bsc = vnindex_df[vnindex_df['scope'] == 'BSC_INDEX'].sort_values('date').iloc[-1] if len(vnindex_df[vnindex_df['scope'] == 'BSC_INDEX']) > 0 else None

        # =====================================================================
        # COMPACT METRICS BAR (Data-Dense Dashboard style)
        # =====================================================================
        def _fmt(val, suffix='x'):
            return f"{val:.1f}{suffix}" if pd.notna(val) else "—"

        pe_vni = latest_vnindex.get('pe_ttm') if latest_vnindex is not None else None
        pb_vni = latest_vnindex.get('pb') if latest_vnindex is not None else None
        pe_exc = latest_vnindex_exclude.get('pe_ttm') if latest_vnindex_exclude is not None else None
        pb_exc = latest_vnindex_exclude.get('pb') if latest_vnindex_exclude is not None else None
        pe_fwd25 = latest_bsc.get('pe_fwd_2025') if latest_bsc is not None else None
        pe_fwd26 = latest_bsc.get('pe_fwd_2026') if latest_bsc is not None else None

        # Inline compact metrics using HTML with CSS variables
        st.markdown(f'''
        <div style="display: flex; gap: 24px; padding: 12px 0; flex-wrap: wrap; align-items: center;">
            <div style="display: flex; gap: 16px; align-items: center; background: rgba(139, 92, 246, 0.1); padding: 8px 16px; border-radius: 8px; border-left: 3px solid var(--purple-primary);">
                <span style="color: var(--purple-light); font-size: 0.75rem; font-weight: 600;">VNINDEX</span>
                <span style="color: var(--text-primary);">PE <b style="color: var(--positive-light);">{_fmt(pe_vni)}</b></span>
                <span style="color: var(--text-primary);">PB <b style="color: var(--cyan-primary);">{_fmt(pb_vni)}</b></span>
            </div>
            <div style="display: flex; gap: 16px; align-items: center; background: rgba(6, 182, 212, 0.1); padding: 8px 16px; border-radius: 8px; border-left: 3px solid var(--cyan-primary);">
                <span style="color: var(--cyan-light); font-size: 0.75rem; font-weight: 600;">EXCLUDE</span>
                <span style="color: var(--text-primary);">PE <b style="color: var(--positive-light);">{_fmt(pe_exc)}</b></span>
                <span style="color: var(--text-primary);">PB <b style="color: var(--cyan-primary);">{_fmt(pb_exc)}</b></span>
            </div>
            <div style="display: flex; gap: 16px; align-items: center; background: rgba(245, 158, 11, 0.1); padding: 8px 16px; border-radius: 8px; border-left: 3px solid var(--amber-primary);">
                <span style="color: var(--amber-light); font-size: 0.75rem; font-weight: 600;">BSC FWD</span>
                <span style="color: var(--text-primary);">2025 <b style="color: var(--amber-primary);">{_fmt(pe_fwd25)}</b></span>
                <span style="color: var(--text-primary);">2026 <b style="color: var(--purple-primary);">{_fmt(pe_fwd26)}</b></span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # =====================================================================
        # 3-INDEX COMPARISON LINE CHART
        # =====================================================================
        st.markdown(f"### {selected_metric} Comparison: 3 Index Variants")

        if primary_metric not in ['ps', 'ev_ebitda']:
            # Build multi-line chart
            fig_compare = go.Figure()

            # Define colors for each index
            index_colors = {
                'VNINDEX': '#8B5CF6',        # Purple
                'VNINDEX_EXCLUDE': '#06B6D4', # Cyan
                'BSC_INDEX': '#F59E0B'        # Amber
            }
            index_names = {
                'VNINDEX': 'VNIndex',
                'VNINDEX_EXCLUDE': 'VNIndex (Exclude)',
                'BSC_INDEX': 'BSC Index'
            }

            for scope in ['VNINDEX', 'VNINDEX_EXCLUDE', 'BSC_INDEX']:
                scope_data = vnindex_df[vnindex_df['scope'] == scope].copy()
                if scope_data.empty or primary_metric not in scope_data.columns:
                    continue

                scope_data = scope_data.sort_values('date')
                if days < len(scope_data):
                    scope_data = scope_data.tail(days)

                # Filter outliers for cleaner chart
                metric_key = primary_metric.upper().replace('_TTM', '').replace('_', '')
                limits = OUTLIER_LIMITS.get(metric_key, {'min': 0, 'max': 100})
                scope_data = scope_data[
                    (scope_data[primary_metric] >= limits['min']) &
                    (scope_data[primary_metric] <= limits['max'])
                ]

                if len(scope_data) > 0:
                    fig_compare.add_trace(go.Scatter(
                        x=scope_data['date'],
                        y=scope_data[primary_metric],
                        name=index_names[scope],
                        mode='lines',
                        line=dict(color=index_colors[scope], width=2),
                        hovertemplate=f'<b>{index_names[scope]}</b><br>Date: %{{x}}<br>{selected_metric}: %{{y:.2f}}x<extra></extra>'
                    ))

            # Layout with proper time axis
            from WEBAPP.core.styles import get_chart_layout
            layout = get_chart_layout(height=350)
            layout['yaxis']['title'] = selected_metric
            layout['xaxis'] = dict(
                tickformat='%d/%m/%Y',
                tickmode='auto',
                nticks=8,
                tickangle=-30,
                tickfont=dict(size=10, color='#CBD5E1'),
                showgrid=True,
                gridcolor='rgba(255,255,255,0.05)',
                hoverformat='%d/%m/%Y'
            )
            layout['showlegend'] = True
            layout['legend'] = dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5,
                font=dict(size=11)
            )
            layout['hovermode'] = 'x unified'
            fig_compare.update_layout(**layout)

            # Update hover template with proper date format
            for trace in fig_compare.data:
                trace.update(hovertemplate=f'<b>{trace.name}</b><br>{selected_metric}: %{{y:.2f}}x<extra></extra>')

            st.plotly_chart(fig_compare, width='stretch', config={'displayModeBar': False})
        else:
            st.info(f"**{selected_metric}** is not available for Market Indices. Only PE and PB are tracked.")

        # =====================================================================
        # DISTRIBUTION CANDLESTICK (Compact)
        # =====================================================================
        st.markdown(f"### {selected_metric} Distribution")

        # Build candlestick data for 3 variants
        candle_data = []
        for scope in ['VNINDEX', 'VNINDEX_EXCLUDE', 'BSC_INDEX']:
            scope_data = vnindex_df[vnindex_df['scope'] == scope].copy()

            if scope_data.empty or primary_metric not in scope_data.columns:
                continue

            metric_vals = scope_data[primary_metric].dropna()

            # Filter by time range
            scope_data = scope_data.sort_values('date')
            if days_distribution < len(scope_data):
                scope_data = scope_data.tail(days_distribution)
                metric_vals = scope_data[primary_metric].dropna()

            if len(metric_vals) < 20:
                continue

            # Get current value
            current_val = metric_vals.iloc[-1] if len(metric_vals) > 0 else None

            # Filter outliers
            metric_key = primary_metric.upper().replace('_TTM', '').replace('_', '')
            clean_data = filter_outliers(metric_vals, metric_key)

            if len(clean_data) < 20:
                continue

            p_min = clean_data.min()
            p25 = clean_data.quantile(0.25)
            p50 = clean_data.quantile(0.50)
            p75 = clean_data.quantile(0.75)
            p_max = clean_data.max()

            percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100 if current_val else 50

            candle_data.append({
                'symbol': scope,
                'current': current_val,
                'min': p_min,
                'p25': p25,
                'median': p50,
                'p75': p75,
                'max': p_max,
                'percentile': percentile
            })

        if candle_data:
            # Auto-scale Y-axis based on actual data range (with padding)
            all_mins = [d['min'] for d in candle_data if d.get('min') is not None]
            all_maxs = [d['max'] for d in candle_data if d.get('max') is not None]
            all_currents = [d['current'] for d in candle_data if d.get('current') is not None]

            if all_mins and all_maxs:
                data_min = min(all_mins + all_currents)
                data_max = max(all_maxs + all_currents)
                data_range = data_max - data_min
                # Add 10% padding on each side for better visibility
                y_min = max(0, data_min - data_range * 0.1)
                y_max = data_max + data_range * 0.1
                y_range = (y_min, y_max)
            else:
                # Fallback to schema range if no data
                metric_type = primary_metric.upper().replace('_TTM', '').replace('_', '')
                y_range = get_y_range(metric_type)

            fig_candle = distribution_candlestick(
                candle_data,
                metric_label=selected_metric,
                height=450,  # Taller for better visibility
                y_range=y_range,
                title=None
            )
            st.plotly_chart(fig_candle, width='stretch', config={'displayModeBar': False})

            # Legend (HTML styled, no emojis)
            st.markdown(render_valuation_legend(), unsafe_allow_html=True)
        else:
            st.warning("Not enough data for candlestick distribution")

        # =====================================================================
        # INDIVIDUAL INDEX DETAIL (Displayed directly, no expander)
        # =====================================================================
        st.markdown("---")
        st.markdown("### Individual Index Analysis")

        # Index selector with pill-style buttons using HTML
        index_options = ['VNINDEX', 'VNINDEX_EXCLUDE', 'BSC_INDEX']
        index_labels = {'VNINDEX': 'VNIndex', 'VNINDEX_EXCLUDE': 'VNIndex (Exclude)', 'BSC_INDEX': 'BSC Index'}
        index_colors_detail = {'VNINDEX': '#8B5CF6', 'VNINDEX_EXCLUDE': '#06B6D4', 'BSC_INDEX': '#F59E0B'}

        # Use radio buttons styled horizontally
        selected_index = st.radio(
            "Select Index",
            options=index_options,
            format_func=lambda x: index_labels.get(x, x),
            horizontal=True,
            key='vnindex_selector',
            label_visibility='collapsed'
        )

        if selected_index and primary_metric not in ['ps', 'ev_ebitda']:
            index_history = vnindex_df[vnindex_df['scope'] == selected_index].copy()

            # Filter by time range
            index_history = index_history.sort_values('date')
            if days < len(index_history):
                index_history = index_history.tail(days)

            if not index_history.empty and primary_metric in index_history.columns:
                # Stats row at top (compact cards)
                metric_data = index_history[primary_metric].dropna()
                if len(metric_data) >= 20:
                    current_val = metric_data.iloc[-1]
                    median_val = metric_data.median()
                    mean_val = metric_data.mean()
                    std_val = metric_data.std()
                    z_score = (current_val - mean_val) / std_val if std_val > 0 else 0
                    percentile = np.sum(metric_data <= current_val) / len(metric_data) * 100
                    status_color = get_status_color(percentile)
                    status_label = get_status_label(percentile)

                    # Compact stats bar with CSS variables
                    z_color = 'var(--positive-light)' if z_score < 0 else 'var(--negative-light)'
                    st.markdown(f'''
                    <div style="display: flex; gap: 16px; padding: 16px 0; flex-wrap: wrap; align-items: center;">
                        <div style="background: rgba(0,0,0,0.3); padding: 12px 20px; border-radius: 8px; border-left: 3px solid {index_colors_detail[selected_index]};">
                            <div class="metric-label">CURRENT</div>
                            <div class="metric-value-sm">{current_val:.2f}x</div>
                        </div>
                        <div style="background: rgba(0,0,0,0.3); padding: 12px 20px; border-radius: 8px;">
                            <div class="metric-label">MEDIAN</div>
                            <div class="metric-value-sm">{median_val:.2f}x</div>
                        </div>
                        <div style="background: rgba(0,0,0,0.3); padding: 12px 20px; border-radius: 8px;">
                            <div class="metric-label">Z-SCORE</div>
                            <div style="color: {z_color}; font-size: 1.25rem; font-weight: 600;">{z_score:+.2f}σ</div>
                        </div>
                        <div style="background: rgba(0,0,0,0.3); padding: 12px 20px; border-radius: 8px;">
                            <div class="metric-label">PERCENTILE</div>
                            <div class="metric-value-sm">{percentile:.0f}%</div>
                        </div>
                        <div style="background: rgba(0,0,0,0.3); padding: 12px 20px; border-radius: 8px; border-left: 3px solid {status_color};">
                            <div class="metric-label">STATUS</div>
                            <div style="color: {status_color}; font-size: 1.1rem; font-weight: 600;">● {status_label}</div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

                # Create line chart with bands + histogram side-by-side
                col_line, col_hist = st.columns([0.7, 0.3])

                with col_line:
                    fig_line, stats_line = line_with_statistical_bands(
                        index_history,
                        date_col='date',
                        value_col=primary_metric,
                        metric_label=selected_metric,
                        height=350,
                        title=None  # Title already shown above
                    )
                    if fig_line:
                        # Update xaxis format
                        fig_line.update_layout(
                            xaxis=dict(
                                tickformat='%d/%m/%Y',
                                tickmode='auto',
                                nticks=6,
                                tickangle=-30,
                                hoverformat='%d/%m/%Y'
                            ),
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig_line, width='stretch', config={'displayModeBar': False})

                with col_hist:
                    # Histogram
                    metric_data = index_history[primary_metric].dropna()
                    current_val = metric_data.iloc[-1] if len(metric_data) > 0 else None

                    fig_hist = histogram_with_stats(
                        metric_data,
                        metric_label=selected_metric,
                        height=350,
                        current_value=current_val,
                        title="Distribution"
                    )
                    st.plotly_chart(fig_hist, width='stretch', config={'displayModeBar': False})
            else:
                st.warning(f"No {selected_metric} data available for {selected_index}")

        # =====================================================================
        # DOWNLOAD ALL INDEX DATA (Excel)
        # =====================================================================
        st.markdown("---")
        st.markdown("### Download Data")

        # Prepare export data for all 3 indices
        export_cols = ['date', 'scope', 'pe_ttm', 'pb']
        available_cols = [c for c in export_cols if c in vnindex_df.columns]
        export_df = vnindex_df[vnindex_df['scope'].isin(['VNINDEX', 'VNINDEX_EXCLUDE', 'BSC_INDEX'])][available_cols].copy()
        export_df = export_df.sort_values(['scope', 'date'])

        # Map scope names for cleaner export
        scope_names = {'VNINDEX': 'VN-Index', 'VNINDEX_EXCLUDE': 'VN-Index (Exclude)', 'BSC_INDEX': 'BSC Index'}
        export_df['scope'] = export_df['scope'].map(scope_names)
        export_df['date'] = pd.to_datetime(export_df['date']).dt.strftime('%Y-%m-%d')

        if not export_df.empty:
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                # All data in one sheet
                export_df.to_excel(writer, sheet_name='All_Indices', index=False)

                # Separate sheets per index
                for scope_raw, scope_name in scope_names.items():
                    scope_data = vnindex_df[vnindex_df['scope'] == scope_raw][available_cols].copy()
                    if not scope_data.empty:
                        scope_data['date'] = pd.to_datetime(scope_data['date']).dt.strftime('%Y-%m-%d')
                        scope_data = scope_data.sort_values('date')
                        sheet_name = scope_name.replace(' ', '_').replace('(', '').replace(')', '')[:31]
                        scope_data.to_excel(writer, sheet_name=sheet_name, index=False)

            excel_buffer.seek(0)
            st.download_button(
                "Download All Index Data (PE/PB) - Excel",
                excel_buffer,
                "vnindex_valuation_data.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width='stretch'
            )
            st.caption(f"Includes {len(export_df):,} rows for VN-Index, VN-Index (Exclude), BSC Index")

    else:
        st.warning("VNIndex data not available. Please run the daily valuation pipeline.")

# ============================================================================
# TAB 1: VALUATION (with sub-tabs)
# ============================================================================
elif active_tab == 1:
    # Sub-tabs for Sector Overview (Session State Persisted)
    valuation_tab = render_persistent_tabs(
        ["Sector Comp", "Sector Ind", "Stock Comp", "Stock Ind"],
        "sector_tables_tab",
        style="secondary"
    )

    # =========================================================================
    # SUB-TAB 1: SECTOR COMPARISON (Candlestick)
    # =========================================================================
    if valuation_tab == 0:
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
            all_min_values = []  # For auto-scaling
            all_max_values = []  # For auto-scaling

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

                # Filter outliers using centralized config
                metric_key = primary_metric.upper().replace('_TTM', '').replace('_', '')
                limits = OUTLIER_LIMITS.get(metric_key, {'min': 0, 'max': 100})
                clean_data = metric_data[(metric_data > limits['min']) & (metric_data <= limits['max'])]

                if len(clean_data) < 20:
                    continue

                valid_items.append(scope)

                p_min = clean_data.min()
                p25 = clean_data.quantile(0.25)
                p50 = clean_data.quantile(0.50)
                p75 = clean_data.quantile(0.75)
                p_max = clean_data.max()
                mean_val = clean_data.mean()
                std_val = clean_data.std()

                # Collect for auto-scaling
                all_min_values.append(p_min)
                all_max_values.append(p_max)
                if current_val is not None and not pd.isna(current_val):
                    all_min_values.append(current_val)
                    all_max_values.append(current_val)

                # Store for table
                if current_val:
                    percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100
                    z_score = (current_val - mean_val) / std_val if std_val > 0 else 0
                    status = render_status_badge(percentile)  # HTML badge with colored dot

                    distribution_data.append({
                        'Scope': scope,
                        'Current': current_val,
                        'Median': p50,
                        'Percentile': percentile,
                        'Z-Score': z_score,
                        'Status': status
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

                # Add current value as scatter point with 5-level color
                if current_val and not pd.isna(current_val):
                    percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100
                    dot_color = get_status_color(percentile)

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
                            f'Z-Score: {z_score:+.2f}σ<br>' +
                            f'Median: {p50:.2f}x<br>' +
                            '<extra></extra>'
                        )
                    ))

            if valid_items:
                # Use chart_schema for configuration
                chart_config = get_chart_config('candlestick_distribution')
                layout = get_chart_layout(height=chart_config.height)
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

                # Auto-scale Y-axis based on actual data range (with padding)
                if all_min_values and all_max_values:
                    data_min = min(all_min_values)
                    data_max = max(all_max_values)
                    data_range = data_max - data_min
                    # Add 10% padding on each side for better visibility
                    y_min = max(0, data_min - data_range * 0.1)
                    y_max = data_max + data_range * 0.1
                    layout['yaxis']['range'] = [y_min, y_max]
                else:
                    # Fallback to schema range if no data
                    metric_type = primary_metric.upper().replace('_TTM', '').replace('_', '')
                    y_range = get_y_range(metric_type)
                    layout['yaxis']['range'] = list(y_range)

                fig_candle.update_layout(**layout)

                st.plotly_chart(fig_candle, width='stretch', config={'displayModeBar': False})

                # Legend (5 levels - HTML styled, no emojis)
                st.markdown(render_valuation_legend(), unsafe_allow_html=True)

                # Distribution table (Valuation Matrix)
                if distribution_data:
                    st.markdown("### Valuation Matrix")
                    dist_df = pd.DataFrame(distribution_data)
                    dist_df_raw = dist_df.copy()
                    dist_df = dist_df.sort_values('Percentile')
                    dist_df_raw = dist_df_raw.sort_values('Percentile')

                    # Format display columns
                    dist_df_display = dist_df.copy()
                    dist_df_display['Current'] = dist_df_display['Current'].apply(lambda x: f'{x:.2f}x')
                    dist_df_display['Median'] = dist_df_display['Median'].apply(lambda x: f'{x:.2f}x')
                    dist_df_display['Percentile'] = dist_df_display['Percentile'].apply(lambda x: f'{x:.1f}%')
                    dist_df_display['Z-Score'] = dist_df_display['Z-Score'].apply(lambda x: f'{x:+.2f}σ')

                    # Reorder columns for clarity
                    dist_df_display = dist_df_display[['Scope', 'Current', 'Median', 'Percentile', 'Z-Score', 'Status']]
                    dist_df_display.columns = ['Sector', 'Current', 'Hist. Median', 'Percentile', 'Z-Score', 'Status']

                    st.markdown(render_styled_table(dist_df_display), unsafe_allow_html=True)

                    # Excel download
                    excel_buffer = BytesIO()
                    dist_df_raw.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    st.download_button(
                        f"Download {selected_metric} Valuation Matrix (Excel)",
                        excel_buffer,
                        f"{selected_metric.lower().replace(' ', '_')}_valuation_matrix_sectors.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width='stretch'
                    )
            else:
                st.warning("Not enough historical data for distribution analysis")
        else:
            st.warning("No sector data available")

    # =========================================================================
    # SUB-TAB 2: INDIVIDUAL SECTOR (Line chart with statistical bands)
    # =========================================================================
    elif valuation_tab == 1:
        st.markdown(f"### {selected_metric} Historical Trend with Statistical Bands")
        st.markdown("*Line chart with median and ±1σ, ±2σ bands for individual sector.*")

        # Sector selector
        available_sectors = sector_scopes if sector_scopes else []
        if available_sectors:
            selected_sector = st.selectbox(
                "Select Sector",
                options=available_sectors,
                index=0,
                key="individual_sector_select"
            )

            # Load sector history
            sector_history = load_sector_history(selected_sector, days)

            if not sector_history.empty and primary_metric in sector_history.columns:
                # Create line chart with bands + histogram side-by-side
                col_line, col_hist = st.columns([0.7, 0.3])

                with col_line:
                    fig_sector, stats_sector = line_with_statistical_bands(
                        sector_history,
                        date_col='date',
                        value_col=primary_metric,
                        metric_label=selected_metric,
                        height=get_chart_config('line_with_bands').height,
                        title=f"{selected_sector} - {selected_metric}"
                    )
                    if fig_sector:
                        st.plotly_chart(fig_sector, width='stretch')
                    else:
                        st.warning(f"Not enough valid data for {selected_sector}")

                with col_hist:
                    # Histogram distribution
                    metric_data = sector_history[primary_metric].dropna()
                    metric_key = primary_metric.upper().replace('_TTM', '').replace('_', '')
                    clean_data = filter_outliers(metric_data, metric_key)

                    if len(clean_data) >= 10:
                        current_val = metric_data.iloc[-1] if len(metric_data) > 0 else None
                        fig_hist = histogram_with_stats(
                            clean_data,
                            metric_label=selected_metric,
                            height=get_chart_config('line_with_bands').height,
                            current_value=current_val,
                            title="Distribution"
                        )
                        st.plotly_chart(fig_hist, width='stretch')

                # Stats cards
                if stats_sector:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Current", format_ratio(stats_sector.get('current')))
                    with col2:
                        st.metric("Median", format_ratio(stats_sector.get('median')))
                    with col3:
                        st.metric("Z-Score", format_zscore(stats_sector.get('z_score')))
                    with col4:
                        st.metric("Percentile", format_percent(stats_sector.get('percentile')))

                    # Valuation assessment (HTML styled, no emojis)
                    z = stats_sector.get('z_score', 0)
                    st.markdown(f"**Assessment**: {render_valuation_assessment(z)}", unsafe_allow_html=True)
            else:
                st.warning(f"No {selected_metric} data available for {selected_sector}")
        else:
            st.warning("No sectors available")

    # =========================================================================
    # SUB-TAB 3: STOCK COMPARISON (Candlestick)
    # =========================================================================
    elif valuation_tab == 2:
        st.markdown(f"### {selected_metric} Distribution: Stocks in Sector")
        st.markdown("*Candlestick: Min-Max (whiskers), P25-P75 (body). Colored dot = current value.*")

        # Sector selector for stock comparison
        if sector_scopes:
            stock_comp_sector = st.selectbox(
                "Select Sector",
                options=sector_scopes,
                index=0,
                key="stock_comp_sector_select"
            )

            # Get tickers in this sector
            sector_tickers = get_sector_tickers(stock_comp_sector)

            if sector_tickers:
                # Build candlestick data for stocks
                stock_candle_data = []
                for ticker in sector_tickers[:30]:  # Limit to 30 stocks
                    try:
                        ticker_history = load_stock_valuation(ticker, days_distribution)
                        if ticker_history.empty or primary_metric not in ticker_history.columns:
                            continue

                        metric_vals = ticker_history[primary_metric].dropna()
                        if len(metric_vals) < 20:
                            continue

                        current_val = metric_vals.iloc[-1] if len(metric_vals) > 0 else None
                        if primary_metric == 'pe_ttm' and (current_val is None or current_val <= 0):
                            continue

                        # Filter outliers
                        metric_key = primary_metric.upper().replace('_TTM', '').replace('_', '')
                        clean_data = filter_outliers(metric_vals, metric_key)
                        if len(clean_data) < 20:
                            continue

                        p25 = clean_data.quantile(0.25)
                        p50 = clean_data.quantile(0.50)
                        p75 = clean_data.quantile(0.75)
                        p_min = clean_data.min()
                        p_max = clean_data.max()
                        mean_val = clean_data.mean()
                        std_val = clean_data.std()
                        percentile = np.sum(clean_data <= current_val) / len(clean_data) * 100 if current_val else 50
                        z_score = (current_val - mean_val) / std_val if std_val > 0 else 0

                        # Use 5-level status (HTML badge with colored dot)
                        status = render_status_badge(percentile)

                        stock_candle_data.append({
                            'symbol': ticker,
                            'current': current_val,
                            'min': p_min,
                            'p25': p25,
                            'median': p50,
                            'p75': p75,
                            'max': p_max,
                            'percentile': percentile,
                            'z_score': z_score,
                            'status': status
                        })
                    except Exception:
                        continue

                if stock_candle_data:
                    # Sort by percentile (cheapest first)
                    stock_candle_data = sorted(stock_candle_data, key=lambda x: x.get('percentile', 50))

                    # Auto-scale Y-axis based on actual data range (with padding)
                    all_mins = [d['min'] for d in stock_candle_data if d.get('min') is not None]
                    all_maxs = [d['max'] for d in stock_candle_data if d.get('max') is not None]
                    all_currents = [d['current'] for d in stock_candle_data if d.get('current') is not None]

                    if all_mins and all_maxs:
                        data_min = min(all_mins + all_currents)
                        data_max = max(all_maxs + all_currents)
                        data_range = data_max - data_min
                        # Add 10% padding on each side for better visibility
                        y_min = max(0, data_min - data_range * 0.1)
                        y_max = data_max + data_range * 0.1
                        y_range = (y_min, y_max)
                    else:
                        # Fallback to schema range if no data
                        metric_type = primary_metric.upper().replace('_TTM', '').replace('_', '')
                        y_range = get_y_range(metric_type)

                    fig_stock_candle = distribution_candlestick(
                        stock_candle_data,
                        metric_label=selected_metric,
                        height=get_chart_config('candlestick_distribution').height,
                        y_range=y_range,
                        title=f"{selected_metric} Distribution: {stock_comp_sector} Stocks"
                    )
                    st.plotly_chart(fig_stock_candle, width='stretch', config={'displayModeBar': False})

                    # Legend (5 levels - HTML styled, no emojis)
                    st.markdown(render_valuation_legend(), unsafe_allow_html=True)

                    # Stock Valuation Matrix
                    st.markdown("### Valuation Matrix")
                    stock_df = pd.DataFrame(stock_candle_data)
                    stock_df_raw = stock_df.copy()
                    stock_df_display = stock_df.copy()

                    # Format display columns
                    stock_df_display['current'] = stock_df_display['current'].apply(lambda x: f'{x:.2f}x' if pd.notna(x) else '-')
                    stock_df_display['median'] = stock_df_display['median'].apply(lambda x: f'{x:.2f}x' if pd.notna(x) else '-')
                    stock_df_display['percentile'] = stock_df_display['percentile'].apply(lambda x: f'{x:.1f}%')
                    stock_df_display['z_score'] = stock_df_display['z_score'].apply(lambda x: f'{x:+.2f}σ')

                    # Reorder columns
                    stock_df_display = stock_df_display[['symbol', 'current', 'median', 'percentile', 'z_score', 'status']]
                    stock_df_display.columns = ['Ticker', 'Current', 'Hist. Median', 'Percentile', 'Z-Score', 'Status']
                    st.markdown(render_styled_table(stock_df_display), unsafe_allow_html=True)

                    # Excel download
                    excel_buffer = BytesIO()
                    stock_df_raw.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    st.download_button(
                        f"Download {stock_comp_sector} Stock Data (Excel)",
                        excel_buffer,
                        f"{stock_comp_sector.lower().replace(' ', '_')}_stocks_{selected_metric.lower().replace(' ', '_')}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width='stretch'
                    )
                else:
                    st.warning(f"Not enough data for stocks in {stock_comp_sector}")
            else:
                st.warning(f"No tickers found in {stock_comp_sector}")
        else:
            st.warning("No sectors available")

    # =========================================================================
    # SUB-TAB 4: INDIVIDUAL STOCK (Line chart with statistical bands)
    # =========================================================================
    elif valuation_tab == 3:
        st.markdown(f"### {selected_metric} Historical Trend with Statistical Bands")
        st.markdown("*Line chart with median and ±1σ, ±2σ bands for individual stock.*")

        # Sector selector for individual stock
        if sector_scopes:
            stock_ind_sector = st.selectbox(
                "Select Sector",
                options=sector_scopes,
                index=0,
                key="stock_ind_sector_select"
            )

            # Get tickers in this sector
            ind_sector_tickers = get_sector_tickers(stock_ind_sector)

            if ind_sector_tickers:
                selected_stock = st.selectbox(
                    "Select Stock",
                    options=ind_sector_tickers,
                    index=0,
                    key="individual_stock_select"
                )

                if selected_stock:
                    stock_history = load_stock_valuation(selected_stock, days)

                    if not stock_history.empty and primary_metric in stock_history.columns:
                        # Create line chart with bands + histogram side-by-side
                        col_line, col_hist = st.columns([0.7, 0.3])

                        with col_line:
                            fig_stock, stats_stock = line_with_statistical_bands(
                                stock_history,
                                date_col='date',
                                value_col=primary_metric,
                                metric_label=selected_metric,
                                height=get_chart_config('line_with_bands').height,
                                title=f"{selected_stock} - {selected_metric}"
                            )
                            if fig_stock:
                                st.plotly_chart(fig_stock, width='stretch')
                            else:
                                st.warning(f"Not enough valid data for {selected_stock}")

                        with col_hist:
                            # Histogram distribution
                            metric_data = stock_history[primary_metric].dropna()
                            metric_key = primary_metric.upper().replace('_TTM', '').replace('_', '')
                            clean_data = filter_outliers(metric_data, metric_key)

                            if len(clean_data) >= 10:
                                current_val = metric_data.iloc[-1] if len(metric_data) > 0 else None
                                fig_hist = histogram_with_stats(
                                    clean_data,
                                    metric_label=selected_metric,
                                    height=get_chart_config('line_with_bands').height,
                                    current_value=current_val,
                                    title="Distribution"
                                )
                                st.plotly_chart(fig_hist, width='stretch')

                        # Stats cards
                        if stats_stock:
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Current", format_ratio(stats_stock.get('current')))
                            with col2:
                                st.metric("Median", format_ratio(stats_stock.get('median')))
                            with col3:
                                st.metric("Z-Score", format_zscore(stats_stock.get('z_score')))
                            with col4:
                                st.metric("Percentile", format_percent(stats_stock.get('percentile')))

                            # Valuation assessment (HTML styled, no emojis)
                            z = stats_stock.get('z_score', 0)
                            st.markdown(f"**Assessment**: {render_valuation_assessment(z)}", unsafe_allow_html=True)
                    else:
                        st.warning(f"No {selected_metric} data available for {selected_stock}")
            else:
                st.warning(f"No tickers found in {stock_ind_sector}")
        else:
            st.warning("No sectors available")

# ============================================================================
# TAB 2: DATA TABLES
# ============================================================================
elif active_tab == 2:
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
            display_df.columns = ['Sector', 'PE', 'PB'] + (['PE Fwd 2025'] if 'pe_fwd_2025' in display_cols else [])

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
            "Download Sector Data (Excel)",
            excel_buffer,
            "sector_valuation.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )

# Footer
st.markdown("---")
st.caption(f"Data: Sector Analysis | {len(service.get_all_sectors())} sectors tracked | Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
