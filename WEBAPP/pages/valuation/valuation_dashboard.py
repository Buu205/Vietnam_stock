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
                # Color based on status - Financial Editorial Palette (muted, not neon)
                status_colors = {
                    "Very Cheap": "#3A6264",   # Teal Dark
                    "Cheap": "#4A7C7E",        # Muted Teal
                    "Fair": "#D4AF37",         # Champagne Gold
                    "Expensive": "#B45454",    # Muted Red
                    "Very Expensive": "#8B3A3A" # Dark Red
                }
                marker_color = status_colors.get(data['status'], '#78716C')

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

            # Premium table CSS + HTML - Financial Editorial Design
            table_css = """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=DM+Sans:wght@400;500;600&display=swap');

            .valuation-table-container {
                background: linear-gradient(180deg, #1A1A1A 0%, #242424 100%);
                border: 1px solid rgba(212, 175, 55, 0.2);
                border-radius: 8px;
                padding: 0;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            }

            .table-header-section {
                background: linear-gradient(135deg, rgba(212, 175, 55, 0.08) 0%, rgba(74, 124, 126, 0.05) 100%);
                padding: 24px 28px;
                border-bottom: 1px solid rgba(212, 175, 55, 0.15);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .table-title {
                font-family: 'Playfair Display', Georgia, serif;
                font-size: 20px;
                font-weight: 600;
                color: #F5F5F4;
                letter-spacing: -0.01em;
                margin: 0;
            }

            .table-subtitle {
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                color: #78716C;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-top: 6px;
            }

            .summary-badges {
                display: flex;
                gap: 12px;
            }

            .summary-badge {
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 6px 14px;
                border-radius: 4px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                font-weight: 500;
            }

            .badge-cheap {
                background: rgba(74, 124, 126, 0.15);
                color: #4A7C7E;
                border: 1px solid rgba(74, 124, 126, 0.3);
            }

            .badge-fair {
                background: rgba(212, 175, 55, 0.12);
                color: #D4AF37;
                border: 1px solid rgba(212, 175, 55, 0.3);
            }

            .badge-expensive {
                background: rgba(180, 84, 84, 0.12);
                color: #B45454;
                border: 1px solid rgba(180, 84, 84, 0.3);
            }

            .valuation-table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
            }

            .valuation-table thead tr {
                background: rgba(74, 124, 126, 0.06);
            }

            .valuation-table th {
                font-family: 'JetBrains Mono', monospace;
                font-size: 10px;
                font-weight: 600;
                color: #78716C;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                padding: 14px 16px;
                text-align: left;
                border-bottom: 1px solid rgba(212, 175, 55, 0.1);
            }

            .valuation-table th:first-child { padding-left: 28px; }
            .valuation-table th:last-child { padding-right: 28px; text-align: right; }

            .valuation-table tbody tr {
                transition: all 0.2s ease;
            }

            .valuation-table tbody tr:hover {
                background: rgba(212, 175, 55, 0.05);
            }

            .valuation-table tbody tr:nth-child(even) {
                background: rgba(255, 255, 255, 0.01);
            }

            .valuation-table td {
                font-family: 'JetBrains Mono', monospace;
                font-size: 13px;
                color: #E7E5E4;
                padding: 14px 16px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.02);
                vertical-align: middle;
            }

            .valuation-table td:first-child { padding-left: 28px; }
            .valuation-table td:last-child { padding-right: 28px; }

            .ticker-cell {
                font-family: 'Playfair Display', Georgia, serif;
                font-weight: 600;
                color: #FAFAF9;
                font-size: 14px;
            }

            .value-cell {
                font-weight: 500;
                color: #A8A29E;
            }

            .percentile-cell {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .percentile-bar-bg {
                flex: 1;
                height: 5px;
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

            /* Financial Editorial colors - muted, sophisticated */
            .pct-cheap { background: linear-gradient(90deg, #4A7C7E, #5F9A9C); }
            .pct-fair { background: linear-gradient(90deg, #D4AF37, #E5C158); }
            .pct-expensive { background: linear-gradient(90deg, #B45454, #8B3A3A); }

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
                border-radius: 4px;
                font-size: 10px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                float: right;
            }

            .status-very-cheap {
                background: rgba(58, 98, 100, 0.2);
                color: #3A6264;
                border: 1px solid rgba(58, 98, 100, 0.35);
            }

            .status-cheap {
                background: rgba(74, 124, 126, 0.15);
                color: #4A7C7E;
                border: 1px solid rgba(74, 124, 126, 0.3);
            }

            .status-fair {
                background: rgba(212, 175, 55, 0.12);
                color: #D4AF37;
                border: 1px solid rgba(212, 175, 55, 0.25);
            }

            .status-expensive {
                background: rgba(180, 84, 84, 0.12);
                color: #B45454;
                border: 1px solid rgba(180, 84, 84, 0.25);
            }

            .status-very-expensive {
                background: rgba(139, 58, 58, 0.15);
                color: #8B3A3A;
                border: 1px solid rgba(139, 58, 58, 0.3);
            }

            .table-footer {
                padding: 18px 28px;
                background: rgba(0, 0, 0, 0.15);
                border-top: 1px solid rgba(212, 175, 55, 0.08);
                font-family: 'JetBrains Mono', monospace;
                font-size: 10px;
                color: #78716C;
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

        # Financial Editorial colors - muted, sophisticated (not neon)
        MUTED_TEAL = '#4A7C7E'       # Primary metric color
        CHAMPAGNE_GOLD = '#D4AF37'  # Accent/highlight color
        MUTED_BLUE = '#5B7FA3'      # Alternative metric
        MUTED_WARM = '#B8962E'      # Gold dark variant

        # Color based on metric - using editorial palette
        metric_colors = {
            'PE': MUTED_TEAL,        # Teal for PE
            'PB': MUTED_BLUE,        # Blue for PB
            'PS': MUTED_WARM,        # Warm gold for PS
            'EV_EBITDA': '#7A9AB8'   # Light blue for EV/EBITDA
        }
        line_color = metric_colors.get(selected_metric, MUTED_TEAL)

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

        # Add ±2 SD band (outer, extremely subtle - editorial lithograph style)
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
            fillcolor='rgba(74, 124, 126, 0.05)',  # Teal extremely subtle
            name='±2 SD',
            showlegend=False,
            hoverinfo='skip'
        ))

        # Add ±1 SD band (inner, subtle - like hatched pattern effect)
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
            fillcolor='rgba(212, 175, 55, 0.06)',  # Champagne Gold very subtle
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

        # Mean line - Champagne Gold (premium accent)
        fig.add_trace(go.Scatter(
            x=[ticker_data['date'].min(), ticker_data['date'].max()],
            y=[mean_val, mean_val],
            mode='lines',
            name=f'Mean ({mean_val:.2f}x)',
            line=dict(color=CHAMPAGNE_GOLD, width=2, dash='solid')
        ))

        # +1 SD line - Muted red (not neon)
        fig.add_trace(go.Scatter(
            x=[ticker_data['date'].min(), ticker_data['date'].max()],
            y=[plus_1sd, plus_1sd],
            mode='lines',
            name=f'+1 SD ({plus_1sd:.2f}x)',
            line=dict(color='#B45454', width=1.5, dash='dash')
        ))

        # -1 SD line - Muted teal
        fig.add_trace(go.Scatter(
            x=[ticker_data['date'].min(), ticker_data['date'].max()],
            y=[minus_1sd, minus_1sd],
            mode='lines',
            name=f'-1 SD ({minus_1sd:.2f}x)',
            line=dict(color='#4A7C7E', width=1.5, dash='dash')
        ))

        # +2 SD line - Lighter muted red
        fig.add_trace(go.Scatter(
            x=[ticker_data['date'].min(), ticker_data['date'].max()],
            y=[plus_2sd, plus_2sd],
            mode='lines',
            name=f'+2 SD ({plus_2sd:.2f}x)',
            line=dict(color='#8B3A3A', width=1, dash='dot')
        ))

        # -2 SD line - Teal dark
        fig.add_trace(go.Scatter(
            x=[ticker_data['date'].min(), ticker_data['date'].max()],
            y=[minus_2sd, minus_2sd],
            mode='lines',
            name=f'-2 SD ({minus_2sd:.2f}x)',
            line=dict(color='#3A6264', width=1, dash='dot')
        ))

        # Current value marker - Champagne Gold (premium accent)
        fig.add_trace(go.Scatter(
            x=[ticker_data['date'].max()],
            y=[current_val],
            mode='markers+text',
            marker=dict(size=12, color=CHAMPAGNE_GOLD, symbol='circle', line=dict(width=2, color='#FAFAF9')),
            text=[f'{current_val:.2f}x'],
            textposition='top right',
            textfont=dict(size=11, color=CHAMPAGNE_GOLD, family='JetBrains Mono'),
            name='Current',
            showlegend=False,
            hovertemplate=f'<b>Current</b>: {current_val:.2f}x<extra></extra>'
        ))

        # Layout for large chart - Financial Editorial style
        fig.update_layout(
            height=600,
            autosize=True,
            margin=dict(l=60, r=40, t=60, b=60),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='JetBrains Mono, monospace', size=11, color='#A8A29E'),
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor='#242424',
                bordercolor=CHAMPAGNE_GOLD,
                font=dict(family='JetBrains Mono', size=12, color='#F5F5F4')
            ),
            xaxis=dict(
                type='date',
                tickformat='%b %Y',  # Format: Jan 2024
                dtick='M6',  # Tick every 6 months
                tickangle=-45,
                gridcolor='rgba(168, 162, 158, 0.05)',  # Extremely faint dotted grid
                griddash='dot',
                zerolinecolor='rgba(168, 162, 158, 0.08)',
                tickfont=dict(size=9, color='#78716C', family='JetBrains Mono'),
                linecolor='rgba(168, 162, 158, 0.08)',
                title=dict(text='', font=dict(size=11, color='#78716C')),
                showgrid=True,
                rangeslider=dict(visible=False),
            ),
            yaxis=dict(
                title=dict(text=f'{selected_metric_display} Ratio', font=dict(size=12, color='#A8A29E', family='DM Sans')),
                gridcolor='rgba(168, 162, 158, 0.05)',
                griddash='dot',
                zerolinecolor='rgba(168, 162, 158, 0.08)',
                tickfont=dict(size=10, color='#78716C', family='JetBrains Mono'),
                linecolor='rgba(168, 162, 158, 0.08)',
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(color='#E7E5E4', size=10, family='DM Sans'),
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

        # Status based on percentile - Editorial colors (muted, not neon)
        if percentile <= 25:
            status = "Cheap"
            status_color = '#4A7C7E'  # Muted Teal
            status_icon = "▼"
        elif percentile <= 75:
            status = "Fair"
            status_color = '#D4AF37'  # Champagne Gold
            status_icon = "●"
        else:
            status = "Expensive"
            status_color = '#B45454'  # Muted Red
            status_icon = "▲"

        # Layout: KPI Cards (1/3) + Histogram (2/3)
        col_kpi, col_hist = st.columns([1, 2])

        with col_kpi:
            # Compact single-column metrics - Financial Editorial style
            st.markdown(f"""
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #78716C; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 0.75rem;">Key Statistics</div>
            <div style="display: grid; gap: 0.6rem;">
                <div style="background: linear-gradient(135deg, #242424 0%, #2E2E2E 100%); padding: 0.8rem; border-radius: 6px; border-left: 3px solid {status_color};">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; color: #78716C; text-transform: uppercase; letter-spacing: 0.1em;">Current</div>
                    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.2rem; color: #FAFAF9; font-weight: 600;">{current:.2f}x</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: {status_color};">P{percentile:.0f}% {status_icon} {status}</div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                    <div style="background: #242424; padding: 0.6rem; border-radius: 4px;">
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: #78716C; text-transform: uppercase;">Mean</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; color: #E7E5E4;">{mean_val:.2f}x</div>
                    </div>
                    <div style="background: #242424; padding: 0.6rem; border-radius: 4px;">
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: #78716C; text-transform: uppercase;">Z-Score</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; color: #E7E5E4;">{z_score:+.2f}</div>
                    </div>
                    <div style="background: #242424; padding: 0.6rem; border-radius: 4px;">
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: #4A7C7E;">-1 SD</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; color: #E7E5E4;">{minus_1sd:.2f}x</div>
                    </div>
                    <div style="background: #242424; padding: 0.6rem; border-radius: 4px;">
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: #B45454;">+1 SD</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; color: #E7E5E4;">{plus_1sd:.2f}x</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_hist:
            # Large histogram - Financial Editorial style
            fig_hist = go.Figure()

            # Create histogram from ticker data
            values = ticker_data[value_col].dropna()

            fig_hist.add_trace(go.Histogram(
                x=values,
                nbinsx=25,
                marker_color='rgba(74, 124, 126, 0.6)',  # Muted Teal
                marker_line_color='#4A7C7E',
                marker_line_width=1,
                name='Distribution',
                hovertemplate='Value: %{x:.2f}x<br>Count: %{y}<extra></extra>'
            ))

            # Add ±1 SD shaded region - subtle
            fig_hist.add_vrect(
                x0=minus_1sd, x1=plus_1sd,
                fillcolor='rgba(212, 175, 55, 0.06)',  # Champagne Gold very subtle
                line_width=0,
                annotation_text="±1 SD",
                annotation_position="top left",
                annotation_font_size=9,
                annotation_font_color='#78716C'
            )

            # Add current value line (prominent)
            fig_hist.add_vline(
                x=current_val,
                line_color=status_color,
                line_width=2.5,
                annotation_text=f"Now: {current_val:.1f}x",
                annotation_position="top right",
                annotation_font_color=status_color,
                annotation_font_size=10
            )

            # Add mean line - Champagne Gold
            fig_hist.add_vline(
                x=mean_val,
                line_color=CHAMPAGNE_GOLD,
                line_width=2,
                line_dash='dash',
                annotation_text=f"Mean: {mean_val:.1f}x",
                annotation_position="bottom right",
                annotation_font_color='#A8A29E',
                annotation_font_size=10
            )

            fig_hist.update_layout(
                height=280,
                margin=dict(l=40, r=20, t=40, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                xaxis=dict(
                    title=dict(text=selected_metric_display, font=dict(size=10, color='#78716C', family='DM Sans')),
                    gridcolor='rgba(168, 162, 158, 0.06)',
                    griddash='dot',
                    tickfont=dict(size=9, color='#78716C', family='JetBrains Mono')
                ),
                yaxis=dict(
                    title=dict(text='Frequency', font=dict(size=10, color='#78716C', family='DM Sans')),
                    gridcolor='rgba(168, 162, 158, 0.06)',
                    griddash='dot',
                    tickfont=dict(size=9, color='#78716C', family='JetBrains Mono')
                ),
                title=dict(
                    text=f'{selected_metric_display} Distribution',
                    font=dict(size=13, color='#E7E5E4', family='Playfair Display'),
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
