"""
Valuation Dashboard
===================
Premium financial dashboard for PE/PB/EV-EBITDA valuation analysis.

Features:
- Tab 1: Industry Sector Comparison (candle chart distribution + statistics table)
- Tab 2: Individual Stock Analysis (single trend chart with mean/SD bands)

Design: Financial Editorial Theme
- Dark terminal aesthetic with vibrant accents
- Statistical bands (mean, ±1 SD)
- Interactive metric and scope selectors

Run:
    streamlit run WEBAPP/pages/valuation/valuation_dashboard.py
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from WEBAPP.services.valuation_service import ValuationService
from WEBAPP.core.styles import (
    get_page_style, get_chart_layout, get_table_style,
    CHART_COLORS, BAR_COLORS
)

# ============================================================================
# STYLES - Midnight Terminal Theme
# ============================================================================
# Note: st.set_page_config() is handled by main_app.py when using navigation

# Inject unified premium styles from core/styles.py
st.markdown(get_page_style(), unsafe_allow_html=True)
st.markdown(get_table_style(), unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================
st.title("Valuation Analysis")
st.markdown("**PE/PB/EV-EBITDA valuation with historical distribution analysis**")
st.markdown("---")

# Initialize service
try:
    service = ValuationService()
except FileNotFoundError as e:
    st.error(f"Error: {e}")
    st.stop()

# ============================================================================
# SIDEBAR - Unified filters for both tabs
# ============================================================================
st.sidebar.markdown("## Filters")

# Metric selector - used for both tabs
st.sidebar.markdown("### Valuation Metric")
metric_options = {
    "P/E Ratio": "PE",
    "P/B Ratio": "PB",
    "P/S Ratio": "PS",
    "EV/EBITDA": "EV_EBITDA"
}
selected_metric_display = st.sidebar.selectbox(
    "Select Metric",
    options=list(metric_options.keys()),
    index=0,
    label_visibility="collapsed"
)
selected_metric = metric_options[selected_metric_display]

# Industry Sector selector
st.sidebar.markdown("### Industry Sector")
industry_sectors = service.get_industry_sectors()
if not industry_sectors:
    # Fallback to entity types if no industry sectors
    industry_sectors = ["Ngân hàng", "Bất động sản", "Xây dựng và Vật liệu"]

# Add "Tất cả" option at the beginning for all sectors
sector_options = ["Tất cả"] + industry_sectors

# Default to "Ngân hàng" if available, otherwise first option
default_index = 0
if "Ngân hàng" in sector_options:
    default_index = sector_options.index("Ngân hàng")

selected_industry = st.sidebar.selectbox(
    "Select Industry",
    options=sector_options,
    index=default_index,  # Default to "Ngân hàng"
    label_visibility="collapsed"
)

# Get tickers for selected industry (or all tickers if "Tất cả" selected)
if selected_industry == "Tất cả":
    available_tickers = service.get_all_tickers()
else:
    available_tickers = service.get_tickers_by_industry(selected_industry) if selected_industry else []
    if not available_tickers:
        # Fallback
        available_tickers = service.get_all_tickers()

# Ticker selector (for Individual Analysis tab)
st.sidebar.markdown(f"### Ticker ({len(available_tickers)} available)")
selected_ticker = st.sidebar.selectbox(
    "Select Ticker",
    options=available_tickers,
    index=0 if available_tickers else None,
    label_visibility="collapsed",
    help="Choose a ticker for individual analysis"
)

# Start year
st.sidebar.markdown("### History")
start_year = st.sidebar.slider("Start Year", min_value=2018, max_value=2024, value=2020)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data", width='stretch'):
    st.cache_data.clear()
    st.rerun()

# ============================================================================
# TABS
# ============================================================================
tab_sector, tab_individual = st.tabs(["📊 Sector Comparison", "📈 Individual Analysis"])

# ============================================================================
# TAB 1: SECTOR COMPARISON (by Industry)
# ============================================================================
with tab_sector:
    st.markdown(f"### {selected_metric_display} Distribution — {selected_industry}")
    st.markdown("*Candlestick: P5-P95 (whiskers), P25-P75 (body). Colored dot = current value.*")

    # Load industry candle data
    @st.cache_data(ttl=3600)
    def load_industry_candle_data(industry: str, metric: str, start_year: int):
        return service.get_industry_candle_data(industry, metric, start_year)

    candle_data = load_industry_candle_data(selected_industry, selected_metric, start_year)

    if candle_data:
        # Create candlestick chart
        fig_candle = go.Figure()

        symbols = [d['symbol'] for d in candle_data]

        for data in candle_data:
            # Add candlestick (body = P25-P75, whiskers = P5-P95)
            fig_candle.add_trace(go.Candlestick(
                x=[data['symbol']],
                open=[round(data['p25'], 2)],
                high=[round(data['p95'], 2)],
                low=[round(data['p5'], 2)],
                close=[round(data['p75'], 2)],
                name=data['symbol'],
                showlegend=False,
                increasing_line_color='lightgrey',
                decreasing_line_color='lightgrey',
                increasing_fillcolor='rgba(200, 200, 200, 0.3)',
                decreasing_fillcolor='rgba(200, 200, 200, 0.3)',
            ))

            # Add current value marker
            if data['current'] and not pd.isna(data['current']):
                # Color based on status
                status_colors = {
                    "Very Cheap": "#00D4AA",
                    "Cheap": "#7FFFD4",
                    "Fair": "#FFD666",
                    "Expensive": "#FF9F43",
                    "Very Expensive": "#FF6B6B"
                }
                marker_color = status_colors.get(data['status'], '#A95C68')

                fig_candle.add_trace(go.Scatter(
                    x=[data['symbol']],
                    y=[data['current']],
                    mode='markers',
                    marker=dict(size=8, color=marker_color, symbol='circle'),
                    name=f"{data['symbol']} Current",
                    showlegend=False,
                    hovertemplate=(
                        f"<b>{data['symbol']}</b><br>" +
                        f"Current: {data['current']:.2f}x<br>" +
                        f"Percentile: {data['percentile']:.1f}%<br>" +
                        f"Median: {data['median']:.2f}x<br>" +
                        f"Status: {data['status']}<br>" +
                        "<extra></extra>"
                    )
                ))

        layout = get_chart_layout(height=500)
        layout['xaxis'] = dict(
            categoryorder='array',
            categoryarray=symbols,
            rangeslider=dict(visible=False),
            tickangle=-45,
            tickfont=dict(size=10, color='#FFFFFF'),
            fixedrange=True
        )
        layout['yaxis']['title'] = selected_metric_display
        layout['yaxis']['fixedrange'] = True
        layout['dragmode'] = False
        fig_candle.update_layout(**layout)

        st.plotly_chart(fig_candle, width='stretch', config={'displayModeBar': False})

        # ================================================================
        # PREMIUM STATISTICS TABLE - Financial Editorial Design
        # ================================================================
        st.markdown("---")

        # Prepare table data with enhanced formatting
        table_rows = []
        for data in candle_data:
            # Status styling
            status = data['status']
            if status == "Very Cheap":
                status_class = "status-very-cheap"
                status_icon = "▼▼"
            elif status == "Cheap":
                status_class = "status-cheap"
                status_icon = "▼"
            elif status == "Fair":
                status_class = "status-fair"
                status_icon = "●"
            elif status == "Expensive":
                status_class = "status-expensive"
                status_icon = "▲"
            else:
                status_class = "status-very-expensive"
                status_icon = "▲▲"

            # Percentile bar width
            pct_width = min(data['percentile'], 100)

            # Format values
            current_val = f"{data['current']:.2f}x" if data['current'] and not pd.isna(data['current']) else "—"
            median_val = f"{data['median']:.2f}x"
            percentile_val = f"{data['percentile']:.0f}%"

            table_rows.append({
                'symbol': data['symbol'],
                'current': current_val,
                'median': median_val,
                'percentile': percentile_val,
                'pct_width': pct_width,
                'status': status,
                'status_class': status_class,
                'status_icon': status_icon
            })

        if table_rows:
            # Summary counts
            cheap_count = len([d for d in candle_data if d['status'] in ['Very Cheap', 'Cheap']])
            fair_count = len([d for d in candle_data if d['status'] == 'Fair'])
            expensive_count = len([d for d in candle_data if d['status'] in ['Expensive', 'Very Expensive']])
            total_count = len(candle_data)

            # Premium table CSS + HTML
            table_css = """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap');

            .valuation-table-container {
                background: linear-gradient(180deg, rgba(10, 15, 28, 0.95) 0%, rgba(16, 24, 40, 0.98) 100%);
                border: 1px solid rgba(41, 92, 169, 0.3);
                border-radius: 16px;
                padding: 0;
                overflow: hidden;
                box-shadow:
                    0 4px 24px rgba(0, 0, 0, 0.4),
                    0 0 0 1px rgba(255, 255, 255, 0.03) inset;
            }

            .table-header-section {
                background: linear-gradient(135deg, rgba(41, 92, 169, 0.15) 0%, rgba(0, 155, 135, 0.08) 100%);
                padding: 20px 24px;
                border-bottom: 1px solid rgba(41, 92, 169, 0.2);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .table-title {
                font-family: 'DM Sans', sans-serif;
                font-size: 18px;
                font-weight: 600;
                color: #F0F4F8;
                letter-spacing: -0.02em;
                margin: 0;
            }

            .table-subtitle {
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                color: #718096;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-top: 4px;
            }

            .summary-badges {
                display: flex;
                gap: 12px;
            }

            .summary-badge {
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 6px 12px;
                border-radius: 20px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 12px;
                font-weight: 500;
            }

            .badge-cheap {
                background: rgba(0, 212, 170, 0.15);
                color: #00D4AA;
                border: 1px solid rgba(0, 212, 170, 0.3);
            }

            .badge-fair {
                background: rgba(255, 193, 50, 0.15);
                color: #FFC132;
                border: 1px solid rgba(255, 193, 50, 0.3);
            }

            .badge-expensive {
                background: rgba(239, 68, 68, 0.15);
                color: #EF4444;
                border: 1px solid rgba(239, 68, 68, 0.3);
            }

            .valuation-table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
            }

            .valuation-table thead tr {
                background: rgba(41, 92, 169, 0.08);
            }

            .valuation-table th {
                font-family: 'JetBrains Mono', monospace;
                font-size: 10px;
                font-weight: 600;
                color: #718096;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                padding: 14px 16px;
                text-align: left;
                border-bottom: 1px solid rgba(41, 92, 169, 0.15);
            }

            .valuation-table th:first-child { padding-left: 24px; }
            .valuation-table th:last-child { padding-right: 24px; text-align: right; }

            .valuation-table tbody tr {
                transition: all 0.2s ease;
            }

            .valuation-table tbody tr:hover {
                background: rgba(41, 92, 169, 0.08);
            }

            .valuation-table tbody tr:nth-child(even) {
                background: rgba(255, 255, 255, 0.01);
            }

            .valuation-table td {
                font-family: 'JetBrains Mono', monospace;
                font-size: 13px;
                color: #E2E8F0;
                padding: 12px 16px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.03);
                vertical-align: middle;
            }

            .valuation-table td:first-child { padding-left: 24px; }
            .valuation-table td:last-child { padding-right: 24px; }

            .ticker-cell {
                font-weight: 600;
                color: #FFFFFF;
                font-size: 14px;
            }

            .value-cell {
                font-weight: 500;
                color: #A0AEC0;
            }

            .percentile-cell {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .percentile-bar-bg {
                flex: 1;
                height: 6px;
                background: rgba(255, 255, 255, 0.06);
                border-radius: 3px;
                overflow: hidden;
                max-width: 80px;
            }

            .percentile-bar-fill {
                height: 100%;
                border-radius: 3px;
                transition: width 0.5s ease;
            }

            .pct-cheap { background: linear-gradient(90deg, #00D4AA, #00B894); }
            .pct-fair { background: linear-gradient(90deg, #FFC132, #FFD666); }
            .pct-expensive { background: linear-gradient(90deg, #FF6B6B, #EF4444); }

            .percentile-value {
                min-width: 40px;
                text-align: right;
                font-weight: 500;
            }

            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 5px 12px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                float: right;
            }

            .status-very-cheap {
                background: rgba(0, 212, 170, 0.15);
                color: #00D4AA;
                border: 1px solid rgba(0, 212, 170, 0.25);
            }

            .status-cheap {
                background: rgba(127, 255, 212, 0.12);
                color: #7FFFD4;
                border: 1px solid rgba(127, 255, 212, 0.2);
            }

            .status-fair {
                background: rgba(255, 193, 50, 0.12);
                color: #FFC132;
                border: 1px solid rgba(255, 193, 50, 0.2);
            }

            .status-expensive {
                background: rgba(255, 159, 67, 0.12);
                color: #FF9F43;
                border: 1px solid rgba(255, 159, 67, 0.2);
            }

            .status-very-expensive {
                background: rgba(239, 68, 68, 0.15);
                color: #EF4444;
                border: 1px solid rgba(239, 68, 68, 0.25);
            }

            .table-footer {
                padding: 16px 24px;
                background: rgba(0, 0, 0, 0.2);
                border-top: 1px solid rgba(255, 255, 255, 0.03);
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                color: #718096;
                display: flex;
                justify-content: space-between;
            }
            </style>
            """

            # Build table rows HTML
            rows_html = ""
            for row in table_rows:
                # Determine bar color class
                if row['pct_width'] <= 25:
                    bar_class = "pct-cheap"
                elif row['pct_width'] <= 75:
                    bar_class = "pct-fair"
                else:
                    bar_class = "pct-expensive"

                rows_html += f"""
                <tr>
                    <td class="ticker-cell">{row['symbol']}</td>
                    <td class="value-cell">{row['current']}</td>
                    <td class="value-cell">{row['median']}</td>
                    <td>
                        <div class="percentile-cell">
                            <div class="percentile-bar-bg">
                                <div class="percentile-bar-fill {bar_class}" style="width: {row['pct_width']}%"></div>
                            </div>
                            <span class="percentile-value">{row['percentile']}</span>
                        </div>
                    </td>
                    <td>
                        <span class="status-badge {row['status_class']}">
                            <span>{row['status_icon']}</span>
                            {row['status']}
                        </span>
                    </td>
                </tr>
                """

            table_html = f"""
            {table_css}
            <div class="valuation-table-container">
                <div class="table-header-section">
                    <div>
                        <h3 class="table-title">{selected_metric_display} Valuation Summary</h3>
                        <div class="table-subtitle">{selected_industry} Sector • {total_count} Tickers</div>
                    </div>
                    <div class="summary-badges">
                        <div class="summary-badge badge-cheap">
                            <span>▼</span>
                            <span>{cheap_count} Undervalued</span>
                        </div>
                        <div class="summary-badge badge-fair">
                            <span>●</span>
                            <span>{fair_count} Fair</span>
                        </div>
                        <div class="summary-badge badge-expensive">
                            <span>▲</span>
                            <span>{expensive_count} Overvalued</span>
                        </div>
                    </div>
                </div>
                <table class="valuation-table">
                    <thead>
                        <tr>
                            <th>Ticker</th>
                            <th>Current</th>
                            <th>Median</th>
                            <th>Percentile</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
                <div class="table-footer">
                    <span>Data from {start_year} to present</span>
                    <span>Sorted by percentile (lowest to highest)</span>
                </div>
            </div>
            """

            # Calculate dynamic height based on number of rows
            table_height = min(800, 180 + len(table_rows) * 45)
            components.html(table_html, height=table_height, scrolling=True)

            # Download Excel button
            st.markdown("---")
            df_export = pd.DataFrame(candle_data)
            from io import BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Valuation')
            excel_data = buffer.getvalue()
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"valuation_{selected_industry}_{selected_metric}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                help="Download sector valuation data as Excel"
            )

    else:
        st.warning(f"No data available for {selected_industry} sector with {selected_metric_display} metric")

# ============================================================================
# TAB 2: INDIVIDUAL STOCK ANALYSIS (Single Chart using sidebar metric)
# ============================================================================
with tab_individual:
    # Use ticker from sidebar
    active_ticker = selected_ticker

    if not active_ticker:
        st.warning("No ticker available. Please select an industry sector with available data.")
        st.stop()

    # Header with ticker info
    ticker_industry = service.get_ticker_industry(active_ticker)
    header_text = f"{active_ticker} — {selected_metric_display}"
    if ticker_industry:
        header_text += f" | {ticker_industry}"
    st.markdown(f"### {header_text}")

    # Load data for the selected ticker and metric
    @st.cache_data(ttl=3600)
    def load_ticker_metric_data(ticker: str, metric: str, start_year: int):
        df = service.get_metric_data(metric, ticker=ticker, start_year=start_year)
        stats = service.get_metric_stats(metric, ticker, start_year)
        return df, stats

    ticker_data, ticker_stats = load_ticker_metric_data(active_ticker, selected_metric, start_year)

    # Metric display info
    metric_config = service.METRIC_CONFIG.get(selected_metric, {})
    value_col = metric_config.get('value_col', 'pe_ratio')

    # ================================================================
    # CHART FIRST - Primary focus on visualization
    # ================================================================
    if not ticker_data.empty and ticker_stats and value_col in ticker_data.columns:
        # Get statistics
        mean_val = ticker_stats['mean']
        std_val = ticker_stats['std']
        current_val = ticker_stats['current']

        # High-contrast colors for dark background
        CHART_GOLD = '#FFD700'      # Bright gold - very visible
        CHART_CYAN = '#00FFFF'      # Cyan - stands out on dark
        CHART_ORANGE = '#FF8C00'    # Orange - high contrast
        BRAND_GOLD = '#FFC132'

        # Color based on metric - using high-contrast colors
        metric_colors = {
            'PE': CHART_GOLD,       # Gold for PE
            'PB': CHART_CYAN,       # Cyan for PB
            'EV_EBITDA': CHART_ORANGE # Orange for EV/EBITDA
        }
        line_color = metric_colors.get(selected_metric, CHART_GOLD)

        # Check for data gaps/NaN - warn user if significant
        nan_count = ticker_data[value_col].isna().sum()
        total_count = len(ticker_data)
        nan_pct = nan_count / total_count * 100 if total_count > 0 else 0

        if nan_pct > 10:
            st.warning(f"⚠️ **{nan_pct:.1f}% of data is missing** ({nan_count}/{total_count} records). Chart may show gaps. This often occurs when EBITDA is negative.")

        # ================================================================
        # SINGLE LARGE CHART: Historical Trend with ±1 SD and ±2 SD Bands
        # ================================================================
        fig = go.Figure()

        # Calculate band values
        plus_2sd = mean_val + 2 * std_val
        plus_1sd = mean_val + std_val
        minus_1sd = mean_val - std_val
        minus_2sd = max(0, mean_val - 2 * std_val)  # Ensure not negative

        # Add ±2 SD band (outer, lighter)
        fig.add_trace(go.Scatter(
            x=ticker_data['date'],
            y=[plus_2sd] * len(ticker_data),
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=ticker_data['date'],
            y=[minus_2sd] * len(ticker_data),
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(255, 140, 0, 0.08)',  # Orange very light
            name='±2 SD',
            showlegend=False,
            hoverinfo='skip'
        ))

        # Add ±1 SD band (inner, darker)
        fig.add_trace(go.Scatter(
            x=ticker_data['date'],
            y=[plus_1sd] * len(ticker_data),
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=ticker_data['date'],
            y=[minus_1sd] * len(ticker_data),
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(255, 215, 0, 0.12)',  # Gold light
            name='±1 SD',
            showlegend=False,
            hoverinfo='skip'
        ))

        # Main metric line - prominent
        fig.add_trace(go.Scatter(
            x=ticker_data['date'],
            y=ticker_data[value_col],
            name=selected_metric_display,
            mode='lines',
            line=dict(color=line_color, width=2.5),
            hovertemplate=f'<b>{selected_metric_display}</b>: %{{y:.2f}}x<br>Date: %{{x|%Y-%m-%d}}<extra></extra>'
        ))

        # Mean line (solid black)
        fig.add_trace(go.Scatter(
            x=[ticker_data['date'].min(), ticker_data['date'].max()],
            y=[mean_val, mean_val],
            mode='lines',
            name=f'Mean ({mean_val:.2f}x)',
            line=dict(color='#FFFFFF', width=2, dash='solid')
        ))

        # +1 SD line
        fig.add_trace(go.Scatter(
            x=[ticker_data['date'].min(), ticker_data['date'].max()],
            y=[plus_1sd, plus_1sd],
            mode='lines',
            name=f'+1 SD ({plus_1sd:.2f}x)',
            line=dict(color='#E53E3E', width=1.5, dash='dash')
        ))

        # -1 SD line
        fig.add_trace(go.Scatter(
            x=[ticker_data['date'].min(), ticker_data['date'].max()],
            y=[minus_1sd, minus_1sd],
            mode='lines',
            name=f'-1 SD ({minus_1sd:.2f}x)',
            line=dict(color='#10B981', width=1.5, dash='dash')
        ))

        # +2 SD line
        fig.add_trace(go.Scatter(
            x=[ticker_data['date'].min(), ticker_data['date'].max()],
            y=[plus_2sd, plus_2sd],
            mode='lines',
            name=f'+2 SD ({plus_2sd:.2f}x)',
            line=dict(color='#FF6B6B', width=1, dash='dot')
        ))

        # -2 SD line
        fig.add_trace(go.Scatter(
            x=[ticker_data['date'].min(), ticker_data['date'].max()],
            y=[minus_2sd, minus_2sd],
            mode='lines',
            name=f'-2 SD ({minus_2sd:.2f}x)',
            line=dict(color='#34D399', width=1, dash='dot')
        ))

        # Current value marker - prominent gold marker
        fig.add_trace(go.Scatter(
            x=[ticker_data['date'].max()],
            y=[current_val],
            mode='markers+text',
            marker=dict(size=14, color=BRAND_GOLD, symbol='circle', line=dict(width=2, color='#FFFFFF')),
            text=[f'{current_val:.2f}x'],
            textposition='top right',
            textfont=dict(size=12, color=BRAND_GOLD, family='IBM Plex Mono'),
            name='Current',
            showlegend=False,
            hovertemplate=f'<b>Current</b>: {current_val:.2f}x<extra></extra>'
        ))

        # Layout for large chart - 600px height for prominence
        fig.update_layout(
            height=600,
            autosize=True,
            margin=dict(l=60, r=30, t=60, b=60),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='IBM Plex Mono, monospace', size=11, color='#A0AEC0'),
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor='#101820',
                bordercolor='#009B87',
                font=dict(family='IBM Plex Mono', size=12, color='#F0F4F8')
            ),
            xaxis=dict(
                type='date',
                tickformat='%b %Y',  # Format: Jan 2024
                dtick='M6',  # Tick every 6 months
                tickangle=-45,
                gridcolor='rgba(160, 174, 192, 0.08)',
                zerolinecolor='rgba(160, 174, 192, 0.15)',
                tickfont=dict(size=9, color='#A0AEC0'),
                linecolor='rgba(160, 174, 192, 0.1)',
                title=dict(text='', font=dict(size=11, color='#718096')),
                showgrid=True,
                rangeslider=dict(visible=False),
            ),
            yaxis=dict(
                title=dict(text=f'{selected_metric_display} Ratio', font=dict(size=12, color='#A0AEC0')),
                gridcolor='rgba(160, 174, 192, 0.08)',
                zerolinecolor='rgba(160, 174, 192, 0.15)',
                tickfont=dict(size=10, color='#A0AEC0'),
                linecolor='rgba(160, 174, 192, 0.1)',
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(color='#FFFFFF', size=10),
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(0,0,0,0)'
            )
        )

        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

        # ================================================================
        # KPI CARDS (compact) + HISTOGRAM (large) - Same row
        # ================================================================
        st.markdown("---")

        # Get values for display
        current = ticker_stats.get('current', 0)
        percentile = ticker_stats.get('percentile', 0)
        z_score = ticker_stats.get('z_score', 0)

        # Status based on percentile
        if percentile <= 25:
            status = "Cheap"
            status_color = '#009B87'
            status_icon = "🟢"
        elif percentile <= 75:
            status = "Fair"
            status_color = '#FFC132'
            status_icon = "🟡"
        else:
            status = "Expensive"
            status_color = '#E53E3E'
            status_icon = "🔴"

        # Layout: KPI Cards (1/3) + Histogram (2/3)
        col_kpi, col_hist = st.columns([1, 2])

        with col_kpi:
            # Compact single-column metrics with smaller text
            st.markdown(f"""
            <div style="font-size: 0.75rem; color: #718096; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">Key Stats</div>
            <div style="display: grid; gap: 0.5rem;">
                <div style="background: rgba(16,24,32,0.8); padding: 0.6rem; border-radius: 8px; border-left: 3px solid {status_color};">
                    <div style="font-size: 0.65rem; color: #718096; text-transform: uppercase;">Current</div>
                    <div style="font-size: 1.1rem; color: #FFFFFF; font-weight: 600;">{current:.2f}x</div>
                    <div style="font-size: 0.7rem; color: {status_color};">P{percentile:.0f}% {status_icon} {status}</div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem;">
                    <div style="background: rgba(16,24,32,0.6); padding: 0.5rem; border-radius: 6px;">
                        <div style="font-size: 0.6rem; color: #718096;">Mean</div>
                        <div style="font-size: 0.9rem; color: #E2E8F0;">{mean_val:.2f}x</div>
                    </div>
                    <div style="background: rgba(16,24,32,0.6); padding: 0.5rem; border-radius: 6px;">
                        <div style="font-size: 0.6rem; color: #718096;">Z-Score</div>
                        <div style="font-size: 0.9rem; color: #E2E8F0;">{z_score:+.2f}</div>
                    </div>
                    <div style="background: rgba(16,24,32,0.6); padding: 0.5rem; border-radius: 6px;">
                        <div style="font-size: 0.6rem; color: #10B981;">-1 SD</div>
                        <div style="font-size: 0.9rem; color: #E2E8F0;">{minus_1sd:.2f}x</div>
                    </div>
                    <div style="background: rgba(16,24,32,0.6); padding: 0.5rem; border-radius: 6px;">
                        <div style="font-size: 0.6rem; color: #E53E3E;">+1 SD</div>
                        <div style="font-size: 0.9rem; color: #E2E8F0;">{plus_1sd:.2f}x</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_hist:
            # Large histogram showing distribution with current position
            fig_hist = go.Figure()

            # Create histogram from ticker data
            values = ticker_data[value_col].dropna()

            fig_hist.add_trace(go.Histogram(
                x=values,
                nbinsx=25,
                marker_color='rgba(0, 155, 135, 0.7)',
                marker_line_color='#009B87',
                marker_line_width=1,
                name='Distribution',
                hovertemplate='Value: %{x:.2f}x<br>Count: %{y}<extra></extra>'
            ))

            # Add ±1 SD shaded region
            fig_hist.add_vrect(
                x0=minus_1sd, x1=plus_1sd,
                fillcolor='rgba(0, 155, 135, 0.1)',
                line_width=0,
                annotation_text="±1 SD",
                annotation_position="top left",
                annotation_font_size=9,
                annotation_font_color='#718096'
            )

            # Add current value line (prominent)
            fig_hist.add_vline(
                x=current_val,
                line_color=status_color,
                line_width=3,
                annotation_text=f"Now: {current_val:.1f}x",
                annotation_position="top right",
                annotation_font_color=status_color,
                annotation_font_size=11
            )

            # Add mean line
            fig_hist.add_vline(
                x=mean_val,
                line_color='#FFFFFF',
                line_width=2,
                line_dash='dash',
                annotation_text=f"Mean: {mean_val:.1f}x",
                annotation_position="bottom right",
                annotation_font_color='#A0AEC0',
                annotation_font_size=10
            )

            fig_hist.update_layout(
                height=280,
                margin=dict(l=40, r=20, t=40, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                xaxis=dict(
                    title=dict(text=selected_metric_display, font=dict(size=10, color='#718096')),
                    gridcolor='rgba(160, 174, 192, 0.1)',
                    tickfont=dict(size=9, color='#A0AEC0')
                ),
                yaxis=dict(
                    title=dict(text='Frequency', font=dict(size=10, color='#718096')),
                    gridcolor='rgba(160, 174, 192, 0.1)',
                    tickfont=dict(size=9, color='#A0AEC0')
                ),
                title=dict(
                    text=f'{selected_metric_display} Historical Distribution',
                    font=dict(size=12, color='#E2E8F0'),
                    x=0.5
                )
            )

            st.plotly_chart(fig_hist, width='stretch', config={'displayModeBar': False})

        # Download Excel button for individual ticker
        st.markdown("---")
        from io import BytesIO
        buffer_ticker = BytesIO()
        with pd.ExcelWriter(buffer_ticker, engine='openpyxl') as writer:
            ticker_data.to_excel(writer, index=False, sheet_name=f'{active_ticker}_{selected_metric}')
        excel_ticker = buffer_ticker.getvalue()
        st.download_button(
            label="📥 Download Excel",
            data=excel_ticker,
            file_name=f"valuation_{active_ticker}_{selected_metric}.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            help=f"Download {active_ticker} {selected_metric_display} historical data"
        )

    else:
        st.info(f"No {selected_metric_display} data available for {active_ticker}")

# Footer
st.markdown("---")
st.caption(f"Data: Valuation Analysis | Industry: **{selected_industry}** | Ticker: **{active_ticker}** | Metric: **{selected_metric_display}** | Start Year: {start_year}")
