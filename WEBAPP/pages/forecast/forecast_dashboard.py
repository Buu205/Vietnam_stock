"""
BSC Forecast Dashboard
======================
Research-grade forecast analysis from BSC Research.

Design: Midnight Financial Terminal
- Dark theme with brand teal accents
- Styled tables with rating color coding
- Sector PE/PB forward comparison

Run:
    streamlit run WEBAPP/pages/forecast/forecast_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path
from io import BytesIO

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from WEBAPP.services.forecast_service import ForecastService
from WEBAPP.core.styles import (
    get_page_style, get_chart_layout, get_table_style,
    render_styled_table, CHART_COLORS, BAR_COLORS
)

# Rating color mapping
RATING_COLORS = {
    'STRONG BUY': '#00C9AD',  # Bright teal
    'BUY': '#009B87',         # Brand teal
    'HOLD': '#FFC132',        # Brand gold
    'SELL': '#E63946',        # Red
    'STRONG SELL': '#9D0208', # Dark red
    'N/A': '#64748B',         # Gray
}

RATING_BG_COLORS = {
    'STRONG BUY': 'rgba(0, 201, 173, 0.15)',
    'BUY': 'rgba(0, 155, 135, 0.15)',
    'HOLD': 'rgba(255, 193, 50, 0.15)',
    'SELL': 'rgba(230, 57, 70, 0.15)',
    'STRONG SELL': 'rgba(157, 2, 8, 0.15)',
    'N/A': 'rgba(100, 116, 139, 0.15)',
}

# Inject premium styles
st.markdown(get_page_style(), unsafe_allow_html=True)
st.markdown(get_table_style(), unsafe_allow_html=True)

# Additional custom styles for rating badges and upside colors
st.markdown("""
<style>
/* Rating Badge Styles - Giữ nguyên style cũ, chỉ fix kích thước */
.rating-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    white-space: nowrap;
    line-height: 1.2;
}

/* STRONG BUY - Teal (brand color) */
.rating-strong-buy {
    background: rgba(0, 201, 173, 0.2);
    color: #00C9AD;
    border: 1px solid rgba(0, 201, 173, 0.4);
}

/* BUY - Green */
.rating-buy {
    background: rgba(34, 197, 94, 0.2);
    color: #22C55E;
    border: 1px solid rgba(34, 197, 94, 0.4);
}

/* HOLD - Gold/Yellow */
.rating-hold {
    background: rgba(255, 193, 50, 0.2);
    color: #FFC132;
    border: 1px solid rgba(255, 193, 50, 0.4);
}

/* SELL - Orange */
.rating-sell {
    background: rgba(249, 115, 22, 0.2);
    color: #F97316;
    border: 1px solid rgba(249, 115, 22, 0.4);
}

/* STRONG SELL - Red */
.rating-strong-sell {
    background: rgba(239, 68, 68, 0.2);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.4);
}

/* N/A - Gray */
.rating-na {
    background: rgba(100, 116, 139, 0.2);
    color: #94A3B8;
    border: 1px solid rgba(100, 116, 139, 0.4);
}

/* Upside color classes */
.upside-positive {
    color: #00C9AD !important;
    font-weight: 600;
}

.upside-negative {
    color: #FC8181 !important;
    font-weight: 600;
}

/* Styled table override for forecast tables */
.forecast-table td.cell {
    text-align: center;
}

.forecast-table td.cell-first {
    font-weight: 600;
    color: #00C9AD;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("BSC Forecast Analysis")
st.markdown("**92 stocks with PE/PB Forward 2025-2026 from BSC Research**")
st.markdown("---")

# Initialize service
try:
    service = ForecastService()
    df = service.get_individual_stocks()
    sector_df = service.get_sector_valuation()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

if df.empty:
    st.warning("No BSC Forecast data available. Please run the BSC forecast pipeline first.")
    st.code("python3 PROCESSORS/pipelines/daily_bsc_forecast.py", language="bash")
    st.stop()

# Sidebar filters
st.sidebar.markdown("## Filters")

# Rating filter
all_ratings = ['STRONG BUY', 'BUY', 'HOLD', 'SELL', 'N/A']
available_ratings = df['rating'].unique().tolist() if 'rating' in df.columns else []
rating_filter = st.sidebar.multiselect(
    "Rating",
    options=[r for r in all_ratings if r in available_ratings],
    default=[r for r in ['STRONG BUY', 'BUY', 'HOLD'] if r in available_ratings]
)

# Sector filter
all_sectors = ['All'] + service.get_sectors_list()
sector_filter = st.sidebar.selectbox(
    "Sector",
    options=all_sectors,
    index=0
)

# Sort by
sort_options = {
    "Upside % (High to Low)": ("upside_pct", False),
    "Upside % (Low to High)": ("upside_pct", True),
    "PE FWD 2025 (Low to High)": ("pe_fwd_2025", True),
    "PE FWD 2025 (High to Low)": ("pe_fwd_2025", False),
    "Market Cap (High to Low)": ("market_cap", False),
    "Market Cap (Low to High)": ("market_cap", True),
    "Sector (A-Z)": ("sector", True),
    "Sector (Z-A)": ("sector", False),
    "Profit Growth 26F (High to Low)": ("npatmi_growth_yoy_2026", False),
    "Revenue 25F (High to Low)": ("rev_2025f", False),
}
sort_by = st.sidebar.selectbox("Sort By", options=list(sort_options.keys()), index=0)

st.sidebar.markdown("---")
if st.sidebar.button("Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Metric cards
stats = service.get_summary_stats()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Stocks", stats['total_stocks'])

with col2:
    st.metric("Strong Buy", stats['strong_buy_count'])

with col3:
    avg_upside = stats['avg_upside']
    upside_display = f"{avg_upside*100:+.1f}%" if avg_upside else "N/A"
    st.metric("Avg Upside", upside_display)

with col4:
    median_pe = stats['median_pe_fwd_2025']
    pe_display = f"{median_pe:.1f}x" if median_pe and median_pe > 0 else "N/A"
    st.metric("Median PE 25F", pe_display)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Individual Stocks", "Sector Valuation", "9M Achievement", "Charts"])


def format_rating_badge(rating: str) -> str:
    """Format rating as colored badge HTML."""
    rating_class = {
        'STRONG BUY': 'rating-strong-buy',
        'BUY': 'rating-buy',
        'HOLD': 'rating-hold',
        'SELL': 'rating-sell',
        'STRONG SELL': 'rating-strong-sell',
        'N/A': 'rating-na',
    }.get(rating, 'rating-na')

    # Giữ nguyên text đầy đủ như cũ
    return f'<span class="rating-badge {rating_class}">{rating}</span>'


def format_upside(val) -> str:
    """Format upside percentage with color."""
    if pd.isna(val):
        return '-'
    pct = val * 100
    color_class = 'upside-positive' if pct >= 0 else 'upside-negative'
    return f'<span class="{color_class}">{pct:+.1f}%</span>'


def format_number(val, decimals: int = 1, suffix: str = '') -> str:
    """Format number with decimals."""
    if pd.isna(val) or val == 0:
        return '-'
    return f"{val:.{decimals}f}{suffix}"


def format_price(val) -> str:
    """Format price in thousands VND."""
    if pd.isna(val) or val == 0:
        return '-'
    return f"{val:,.0f}"


def format_market_cap(val) -> str:
    """Format market cap in billions VND."""
    if pd.isna(val) or val == 0:
        return '-'
    # val is in billions already
    if val >= 1000:
        return f"{val/1000:,.1f}T"
    return f"{val:,.0f}B"


def format_billions(val) -> str:
    """Format value in billions VND."""
    if pd.isna(val) or val == 0:
        return '-'
    if val >= 1000:
        return f"{val/1000:,.1f}T"
    return f"{val:,.0f}B"


def format_growth(val) -> str:
    """Format growth percentage with color."""
    if pd.isna(val):
        return '-'
    pct = val * 100 if abs(val) < 10 else val  # Handle both ratio and percentage
    color_class = 'upside-positive' if pct >= 0 else 'upside-negative'
    return f'<span class="{color_class}">{pct:+.1f}%</span>'


def format_achievement(val) -> str:
    """Format achievement percentage with color coding."""
    if pd.isna(val):
        return '-'
    pct = val * 100 if abs(val) < 10 else val
    if pct >= 75:
        color = '#00C9AD'  # Green - on track
    elif pct >= 50:
        color = '#FFC132'  # Yellow - behind
    else:
        color = '#FC8181'  # Red - at risk
    return f'<span style="color: {color}; font-weight: 600;">{pct:.1f}%</span>'


# ============================================================================
# TAB 1: INDIVIDUAL STOCKS TABLE
# ============================================================================
with tab1:
    st.markdown("### Individual Stocks Forecast")
    st.markdown("*92 stocks covered by BSC Research with target prices, forward valuations, and earnings forecasts*")

    # Apply filters
    filtered_df = df.copy()

    if rating_filter:
        filtered_df = filtered_df[filtered_df['rating'].isin(rating_filter)]

    if sector_filter != 'All':
        filtered_df = filtered_df[filtered_df['sector'] == sector_filter]

    # Apply sorting
    sort_col, sort_asc = sort_options[sort_by]
    if sort_col in filtered_df.columns:
        filtered_df = filtered_df.sort_values(sort_col, ascending=sort_asc, na_position='last')

    st.markdown(f"**Showing {len(filtered_df)} stocks**")

    if not filtered_df.empty:
        # Sub-tabs for different views
        view_tab1, view_tab2 = st.tabs(["Valuation View", "Earnings View"])

        with view_tab1:
            st.markdown("#### Valuation Metrics")
            # Create display dataframe - Valuation focus
            display_cols = [
                'symbol', 'target_price', 'current_price', 'upside_pct', 'rating',
                'pe_fwd_2025', 'pe_fwd_2026', 'pb_fwd_2025', 'pb_fwd_2026',
                'roe_2025f', 'sector', 'market_cap'
            ]

            display_cols = [c for c in display_cols if c in filtered_df.columns]
            display_df = filtered_df[display_cols].copy()

            formatted_df = pd.DataFrame()
            formatted_df['Symbol'] = display_df['symbol']
            formatted_df['Target'] = display_df['target_price'].apply(format_price)
            formatted_df['Current'] = display_df['current_price'].apply(format_price)
            formatted_df['Upside'] = display_df['upside_pct'].apply(format_upside)
            formatted_df['Rating'] = display_df['rating'].apply(format_rating_badge)
            formatted_df['PE 25F'] = display_df['pe_fwd_2025'].apply(lambda x: format_number(x, 1, 'x'))
            formatted_df['PE 26F'] = display_df['pe_fwd_2026'].apply(lambda x: format_number(x, 1, 'x'))
            formatted_df['PB 25F'] = display_df['pb_fwd_2025'].apply(lambda x: format_number(x, 2, 'x'))
            formatted_df['PB 26F'] = display_df['pb_fwd_2026'].apply(lambda x: format_number(x, 2, 'x'))
            formatted_df['ROE 25F'] = display_df['roe_2025f'].apply(lambda x: format_number(x * 100 if pd.notna(x) else None, 1, '%'))
            formatted_df['Sector'] = display_df['sector']
            formatted_df['Mkt Cap'] = display_df['market_cap'].apply(format_market_cap)

            st.markdown(render_styled_table(formatted_df, highlight_first_col=True), unsafe_allow_html=True)

        with view_tab2:
            st.markdown("#### Earnings Forecast 2025-2026")
            # Create display dataframe - Earnings focus
            earnings_cols = [
                'symbol', 'sector', 'rev_2025f', 'rev_2026f', 'rev_growth_yoy_2026',
                'npatmi_2025f', 'npatmi_2026f', 'npatmi_growth_yoy_2026',
                'roe_2025f', 'roe_2026f', 'rating'
            ]

            earnings_cols = [c for c in earnings_cols if c in filtered_df.columns]
            earnings_df = filtered_df[earnings_cols].copy()

            formatted_earnings = pd.DataFrame()
            formatted_earnings['Symbol'] = earnings_df['symbol']
            formatted_earnings['Sector'] = earnings_df['sector']
            formatted_earnings['Rev 25F'] = earnings_df['rev_2025f'].apply(format_billions)
            formatted_earnings['Rev 26F'] = earnings_df['rev_2026f'].apply(format_billions)
            if 'rev_growth_yoy_2026' in earnings_df.columns:
                formatted_earnings['Rev Gr 26F'] = earnings_df['rev_growth_yoy_2026'].apply(format_growth)
            formatted_earnings['NPATMI 25F'] = earnings_df['npatmi_2025f'].apply(format_billions)
            formatted_earnings['NPATMI 26F'] = earnings_df['npatmi_2026f'].apply(format_billions)
            if 'npatmi_growth_yoy_2026' in earnings_df.columns:
                formatted_earnings['Profit Gr 26F'] = earnings_df['npatmi_growth_yoy_2026'].apply(format_growth)
            formatted_earnings['ROE 25F'] = earnings_df['roe_2025f'].apply(lambda x: format_number(x * 100 if pd.notna(x) else None, 1, '%'))
            formatted_earnings['ROE 26F'] = earnings_df['roe_2026f'].apply(lambda x: format_number(x * 100 if pd.notna(x) else None, 1, '%'))
            formatted_earnings['Rating'] = earnings_df['rating'].apply(format_rating_badge)

            st.markdown(render_styled_table(formatted_earnings, highlight_first_col=True), unsafe_allow_html=True)

        # Download button - Excel format
        st.markdown("---")
        all_cols = [c for c in df.columns if c != 'updated_at']
        raw_download = filtered_df[all_cols].copy()

        # Create Excel file in memory
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            raw_download.to_excel(writer, index=False, sheet_name='Individual Stocks')
        excel_data = excel_buffer.getvalue()

        st.download_button(
            "📥 Download Full Individual Stocks Data (Excel)",
            excel_data,
            "bsc_forecast_individual.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("No stocks match the selected filters.")


# ============================================================================
# TAB 2: SECTOR VALUATION TABLE
# ============================================================================
with tab2:
    st.markdown("### Sector Forward Valuation")
    st.markdown("*PE/PB Forward 2025-2026 aggregated by ICB L2 sector classification*")

    if not sector_df.empty:
        # Sub-tabs for different views of sector data
        sector_tab1, sector_tab2 = st.tabs(["Valuation View", "Growth View"])

        with sector_tab1:
            st.markdown("#### PE/PB Forward by Sector")
            # Create display dataframe - Valuation focus
            sector_display = pd.DataFrame()
            sector_display['Sector'] = sector_df['sector']
            sector_display['Stocks'] = sector_df['symbol_count'].astype(int)
            sector_display['Mkt Cap'] = sector_df['total_market_cap'].apply(format_market_cap)
            sector_display['PE 25F'] = sector_df['pe_fwd_2025'].apply(lambda x: format_number(x, 1, 'x'))
            sector_display['PE 26F'] = sector_df['pe_fwd_2026'].apply(lambda x: format_number(x, 1, 'x'))
            sector_display['PB 25F'] = sector_df['pb_fwd_2025'].apply(lambda x: format_number(x, 2, 'x'))
            sector_display['PB 26F'] = sector_df['pb_fwd_2026'].apply(lambda x: format_number(x, 2, 'x'))
            sector_display['Avg Upside'] = sector_df['avg_upside_pct'].apply(format_upside)
            sector_display['Avg ROE 25F'] = sector_df['avg_roe_2025f'].apply(lambda x: format_number(x * 100 if pd.notna(x) else None, 1, '%'))

            # Render styled table
            st.markdown(render_styled_table(sector_display, highlight_first_col=True), unsafe_allow_html=True)

        with sector_tab2:
            st.markdown("#### Revenue & Profit Growth by Sector (YoY)")
            st.markdown("*Tăng trưởng doanh thu và LNST trung bình theo ngành, chỉ tính các mã BSC coverage*")

            # Create display dataframe - Growth focus
            sector_growth = pd.DataFrame()
            sector_growth['Sector'] = sector_df['sector']
            sector_growth['Stocks'] = sector_df['symbol_count'].astype(int)
            sector_growth['Mkt Cap'] = sector_df['total_market_cap'].apply(format_market_cap)

            # Revenue growth columns
            if 'avg_rev_growth_2025' in sector_df.columns:
                sector_growth['Rev Gr 25F'] = sector_df['avg_rev_growth_2025'].apply(format_growth)
            if 'avg_rev_growth_2026' in sector_df.columns:
                sector_growth['Rev Gr 26F'] = sector_df['avg_rev_growth_2026'].apply(format_growth)

            # Profit growth columns
            if 'avg_npatmi_growth_2025' in sector_df.columns:
                sector_growth['Profit Gr 25F'] = sector_df['avg_npatmi_growth_2025'].apply(format_growth)
            if 'avg_npatmi_growth_2026' in sector_df.columns:
                sector_growth['Profit Gr 26F'] = sector_df['avg_npatmi_growth_2026'].apply(format_growth)

            sector_growth['Avg ROE 25F'] = sector_df['avg_roe_2025f'].apply(lambda x: format_number(x * 100 if pd.notna(x) else None, 1, '%'))
            sector_growth['Avg Upside'] = sector_df['avg_upside_pct'].apply(format_upside)

            # Render styled table
            st.markdown(render_styled_table(sector_growth, highlight_first_col=True), unsafe_allow_html=True)

            # Legend
            st.markdown("""
            **Giải thích:**
            - **Rev Gr 25F**: Tăng trưởng doanh thu 2024 → 2025 (forecast)
            - **Rev Gr 26F**: Tăng trưởng doanh thu 2025F → 2026F
            - **Profit Gr 25F**: Tăng trưởng LNST 2024 → 2025 (forecast)
            - **Profit Gr 26F**: Tăng trưởng LNST 2025F → 2026F
            """)

        # Summary metrics
        st.markdown("---")
        st.markdown("### Sector Summary")

        total_market_cap = sector_df['total_market_cap'].sum()
        avg_pe = sector_df['pe_fwd_2025'].median()
        avg_pb = sector_df['pb_fwd_2025'].median()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Sectors", len(sector_df))
        with col2:
            st.metric("Total Mkt Cap", format_market_cap(total_market_cap))
        with col3:
            st.metric("Median PE 25F", f"{avg_pe:.1f}x" if pd.notna(avg_pe) else "N/A")
        with col4:
            st.metric("Median PB 25F", f"{avg_pb:.2f}x" if pd.notna(avg_pb) else "N/A")

        # Download button - Excel format
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            sector_df.to_excel(writer, index=False, sheet_name='Sector Valuation')
        excel_data = excel_buffer.getvalue()

        st.download_button(
            "📥 Download Sector Valuation Data (Excel)",
            excel_data,
            "bsc_forecast_sector.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("No sector valuation data available.")


# ============================================================================
# TAB 3: 9M ACHIEVEMENT
# ============================================================================
with tab3:
    st.markdown("### 9M 2025 Achievement Tracking")
    st.markdown("*Đánh giá tiến độ hoàn thành kế hoạch dựa trên KQKD 9 tháng đầu năm*")

    # Filter stocks with achievement data
    achievement_df = df[df['npatmi_achievement_pct'].notna()].copy()

    if not achievement_df.empty:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        avg_rev_achievement = achievement_df['rev_achievement_pct'].mean()
        avg_profit_achievement = achievement_df['npatmi_achievement_pct'].mean()
        on_track_count = len(achievement_df[achievement_df['npatmi_achievement_pct'] >= 0.75])
        at_risk_count = len(achievement_df[achievement_df['npatmi_achievement_pct'] < 0.50])

        with col1:
            st.metric("Stocks with 9M Data", len(achievement_df))
        with col2:
            st.metric("Avg Revenue Achievement", f"{avg_rev_achievement*100:.1f}%" if pd.notna(avg_rev_achievement) else "N/A")
        with col3:
            st.metric("Avg Profit Achievement", f"{avg_profit_achievement*100:.1f}%" if pd.notna(avg_profit_achievement) else "N/A")
        with col4:
            st.metric("On Track (≥75%)", f"{on_track_count} / {len(achievement_df)}")

        st.markdown("---")

        # Achievement status legend
        st.markdown("""
        **Achievement Status:**
        - 🟢 **On Track** (≥75%): Likely to meet/exceed forecast
        - 🟡 **Monitor** (50-75%): May need Q4 push
        - 🔴 **At Risk** (<50%): Unlikely to meet forecast
        """)

        st.markdown("---")

        # Sort options for achievement table
        ach_sort = st.radio(
            "Sort Achievement Table By",
            options=["Profit Achievement (High to Low)", "Profit Achievement (Low to High)",
                    "Revenue Achievement (High to Low)", "Sector"],
            horizontal=True
        )

        if ach_sort == "Profit Achievement (High to Low)":
            achievement_df = achievement_df.sort_values('npatmi_achievement_pct', ascending=False)
        elif ach_sort == "Profit Achievement (Low to High)":
            achievement_df = achievement_df.sort_values('npatmi_achievement_pct', ascending=True)
        elif ach_sort == "Revenue Achievement (High to Low)":
            achievement_df = achievement_df.sort_values('rev_achievement_pct', ascending=False)
        else:
            achievement_df = achievement_df.sort_values(['sector', 'npatmi_achievement_pct'], ascending=[True, False])

        # Create achievement display table
        ach_display = pd.DataFrame()
        ach_display['Symbol'] = achievement_df['symbol']
        ach_display['Sector'] = achievement_df['sector']
        ach_display['Rev 25F'] = achievement_df['rev_2025f'].apply(format_billions)
        ach_display['Rev 9M'] = achievement_df['rev_ytd_2025'].apply(format_billions)
        ach_display['Rev %'] = achievement_df['rev_achievement_pct'].apply(format_achievement)
        ach_display['NPATMI 25F'] = achievement_df['npatmi_2025f'].apply(format_billions)
        ach_display['NPATMI 9M'] = achievement_df['npatmi_ytd_2025'].apply(format_billions)
        ach_display['Profit %'] = achievement_df['npatmi_achievement_pct'].apply(format_achievement)
        ach_display['Rating'] = achievement_df['rating'].apply(format_rating_badge)

        st.markdown(render_styled_table(ach_display, highlight_first_col=True), unsafe_allow_html=True)

        # Achievement distribution chart
        st.markdown("---")
        st.markdown("### Achievement Distribution")

        # Categorize achievement
        def categorize_achievement(pct):
            if pd.isna(pct):
                return 'N/A'
            if pct >= 0.75:
                return 'On Track (≥75%)'
            elif pct >= 0.50:
                return 'Monitor (50-75%)'
            else:
                return 'At Risk (<50%)'

        achievement_df['status'] = achievement_df['npatmi_achievement_pct'].apply(categorize_achievement)
        status_counts = achievement_df['status'].value_counts()

        status_order = ['On Track (≥75%)', 'Monitor (50-75%)', 'At Risk (<50%)']
        status_colors = {'On Track (≥75%)': '#00C9AD', 'Monitor (50-75%)': '#FFC132', 'At Risk (<50%)': '#FC8181'}

        fig = go.Figure()
        for status in status_order:
            if status in status_counts.index:
                fig.add_trace(go.Bar(
                    x=[status],
                    y=[status_counts[status]],
                    name=status,
                    marker_color=status_colors.get(status, '#64748B'),
                    text=[status_counts[status]],
                    textposition='auto'
                ))

        layout = get_chart_layout(height=350)
        layout['yaxis']['title'] = 'Number of Stocks'
        layout['showlegend'] = False
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)

        # Download - Excel format
        achievement_download = achievement_df[['symbol', 'sector', 'rev_2025f', 'rev_ytd_2025', 'rev_achievement_pct',
                             'npatmi_2025f', 'npatmi_ytd_2025', 'npatmi_achievement_pct', 'rating']].copy()

        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            achievement_download.to_excel(writer, index=False, sheet_name='9M Achievement')
        excel_data = excel_buffer.getvalue()

        st.download_button(
            "📥 Download 9M Achievement Data (Excel)",
            excel_data,
            "bsc_forecast_9m_achievement.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("No 9M achievement data available. Please ensure fundamental data for Q1-Q3 2025 is loaded.")


# ============================================================================
# TAB 4: CHARTS
# ============================================================================
with tab4:
    st.markdown("### Visualization")

    chart_type = st.radio(
        "Select Chart",
        options=["PE TTM vs FWD", "PB TTM vs FWD", "Sector Opportunity", "PE FWD by Sector", "Rating Distribution", "Upside vs PE"],
        horizontal=True
    )

    # -------------------------------------------------------------------------
    # CHART 1: PE TTM vs Forward - Compare current valuation vs forward
    # -------------------------------------------------------------------------
    if chart_type == "PE TTM vs FWD":
        st.markdown("### PE TTM vs Forward 2025 by Sector")
        st.markdown("*So sánh định giá hiện tại (TTM) vs dự báo (Forward) - chỉ tính các mã BSC coverage*")

        # Load sector data with PE TTM
        sector_pe_df = service.get_sector_with_pe_pb_ttm()

        if not sector_pe_df.empty and 'sector_pe_ttm' in sector_pe_df.columns:
            # Filter valid data
            chart_df = sector_pe_df[
                (sector_pe_df['pe_fwd_2025'].notna()) &
                (sector_pe_df['sector_pe_ttm'].notna()) &
                (sector_pe_df['sector_pe_ttm'] > 0) &
                (sector_pe_df['sector_pe_ttm'] < 100)  # Remove outliers
            ].copy()

            if not chart_df.empty:
                # Sort by PE TTM
                chart_df = chart_df.sort_values('sector_pe_ttm')

                fig = go.Figure()

                # PE TTM bars
                fig.add_trace(go.Bar(
                    x=chart_df['sector'],
                    y=chart_df['sector_pe_ttm'],
                    name='PE TTM',
                    marker_color='#FFC132',  # Gold for TTM
                    hovertemplate='<b>%{x}</b><br>PE TTM: %{y:.1f}x<extra></extra>'
                ))

                # PE FWD 2025 bars
                fig.add_trace(go.Bar(
                    x=chart_df['sector'],
                    y=chart_df['pe_fwd_2025'],
                    name='PE FWD 2025',
                    marker_color=CHART_COLORS['primary'],
                    hovertemplate='<b>%{x}</b><br>PE FWD 2025: %{y:.1f}x<extra></extra>'
                ))

                # PE FWD 2026 bars
                fig.add_trace(go.Bar(
                    x=chart_df['sector'],
                    y=chart_df['pe_fwd_2026'],
                    name='PE FWD 2026',
                    marker_color=CHART_COLORS['secondary'],
                    hovertemplate='<b>%{x}</b><br>PE FWD 2026: %{y:.1f}x<extra></extra>'
                ))

                layout = get_chart_layout(height=500)
                layout['barmode'] = 'group'
                layout['showlegend'] = True
                layout['legend'] = dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5,
                    font=dict(size=12, color='#E8E8E8')
                )
                layout['yaxis']['title'] = 'PE Ratio'
                layout['xaxis']['tickangle'] = -45

                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True)

                # Legend explanation
                st.markdown("""
                **Giải thích:**
                - **PE TTM** (vàng): Định giá hiện tại dựa trên lợi nhuận 12 tháng gần nhất
                - **PE FWD 2025** (xanh): Định giá dự báo dựa trên LNST 2025F của BSC
                - **PE FWD 2026** (xanh nhạt): Định giá dự báo dựa trên LNST 2026F của BSC

                → **Ngành hấp dẫn**: PE FWD < PE TTM (dự báo tăng trưởng tốt → PE giảm)
                """)
            else:
                st.info("Không có đủ dữ liệu PE TTM cho các ngành BSC coverage.")
        else:
            st.info("Không có dữ liệu PE TTM. Vui lòng chạy daily valuation pipeline.")

    # -------------------------------------------------------------------------
    # CHART 1.5: PB TTM vs Forward - Compare current book value valuation vs forward
    # -------------------------------------------------------------------------
    elif chart_type == "PB TTM vs FWD":
        st.markdown("### PB TTM vs Forward 2025 by Sector")
        st.markdown("*So sánh định giá theo giá trị sổ sách hiện tại (TTM) vs dự báo (Forward)*")

        # Load sector data with PB TTM
        sector_pb_df = service.get_sector_with_pe_pb_ttm()

        if not sector_pb_df.empty and 'sector_pb_ttm' in sector_pb_df.columns:
            # Filter valid data
            chart_df = sector_pb_df[
                (sector_pb_df['pb_fwd_2025'].notna()) &
                (sector_pb_df['sector_pb_ttm'].notna()) &
                (sector_pb_df['sector_pb_ttm'] > 0) &
                (sector_pb_df['sector_pb_ttm'] < 20)  # Remove outliers
            ].copy()

            if not chart_df.empty:
                # Sort by PB TTM
                chart_df = chart_df.sort_values('sector_pb_ttm')

                fig = go.Figure()

                # PB TTM bars
                fig.add_trace(go.Bar(
                    x=chart_df['sector'],
                    y=chart_df['sector_pb_ttm'],
                    name='PB TTM',
                    marker_color='#FFC132',  # Gold for TTM
                    hovertemplate='<b>%{x}</b><br>PB TTM: %{y:.2f}x<extra></extra>'
                ))

                # PB FWD 2025 bars
                fig.add_trace(go.Bar(
                    x=chart_df['sector'],
                    y=chart_df['pb_fwd_2025'],
                    name='PB FWD 2025',
                    marker_color=CHART_COLORS['primary'],
                    hovertemplate='<b>%{x}</b><br>PB FWD 2025: %{y:.2f}x<extra></extra>'
                ))

                # PB FWD 2026 bars
                fig.add_trace(go.Bar(
                    x=chart_df['sector'],
                    y=chart_df['pb_fwd_2026'],
                    name='PB FWD 2026',
                    marker_color=CHART_COLORS['secondary'],
                    hovertemplate='<b>%{x}</b><br>PB FWD 2026: %{y:.2f}x<extra></extra>'
                ))

                layout = get_chart_layout(height=500)
                layout['barmode'] = 'group'
                layout['showlegend'] = True
                layout['legend'] = dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5,
                    font=dict(size=12, color='#E8E8E8')
                )
                layout['yaxis']['title'] = 'PB Ratio'
                layout['xaxis']['tickangle'] = -45

                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True)

                # Legend explanation
                st.markdown("""
                **Giải thích:**
                - **PB TTM** (vàng): Định giá theo giá trị sổ sách hiện tại
                - **PB FWD 2025** (xanh): Định giá dự báo theo VCSH dự kiến 2025 (VCSH + LNST 2025F)
                - **PB FWD 2026** (xanh nhạt): Định giá dự báo theo VCSH dự kiến 2026

                → **Ngành hấp dẫn**: PB FWD < PB TTM (giá trị sổ sách tăng nhanh hơn giá)
                """)
            else:
                st.info("Không có đủ dữ liệu PB TTM cho các ngành BSC coverage.")
        else:
            st.info("Không có dữ liệu PB TTM. Vui lòng chạy daily valuation pipeline.")

    # -------------------------------------------------------------------------
    # CHART 2: Sector Opportunity Score - Combined ranking
    # -------------------------------------------------------------------------
    elif chart_type == "Sector Opportunity":
        st.markdown("### Sector Opportunity Score")
        st.markdown("*Điểm cơ hội đầu tư theo ngành - kết hợp Upside, Growth, Valuation*")

        # Load opportunity scores
        opp_df = service.get_sector_opportunity_score()

        if not opp_df.empty and 'opportunity_score' in opp_df.columns:
            # Create stacked bar for score components
            fig = go.Figure()

            # Color palette for score components
            component_colors = {
                'upside_score': '#00C9AD',      # Teal - Upside
                'growth_score': '#7C3AED',      # Purple - Growth
                'discount_score': '#FFC132',    # Gold - Valuation Discount
                'pe_level_score': '#3B82F6',    # Blue - PE Level
            }

            component_labels = {
                'upside_score': 'Upside (30%)',
                'growth_score': 'Growth (25%)',
                'discount_score': 'Discount vs TTM (25%)',
                'pe_level_score': 'Low PE (20%)',
            }

            # Add bars for each component
            for component, color in component_colors.items():
                if component in opp_df.columns:
                    fig.add_trace(go.Bar(
                        x=opp_df['sector'],
                        y=opp_df[component],
                        name=component_labels.get(component, component),
                        marker_color=color,
                        opacity=0.8,
                        hovertemplate=f'<b>%{{x}}</b><br>{component_labels.get(component, component)}: %{{y:.1f}}<extra></extra>'
                    ))

            layout = get_chart_layout(height=500)
            layout['barmode'] = 'stack'
            layout['showlegend'] = True
            layout['legend'] = dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5,
                font=dict(size=11, color='#E8E8E8')
            )
            layout['yaxis']['title'] = 'Opportunity Score (0-100)'
            layout['xaxis']['tickangle'] = -45

            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)

            # Show ranking table
            st.markdown("### Sector Ranking")

            rank_display = pd.DataFrame()
            rank_display['Rank'] = opp_df['rank'].astype(int)
            rank_display['Sector'] = opp_df['sector']
            rank_display['Score'] = opp_df['opportunity_score'].apply(lambda x: f"{x:.1f}")
            rank_display['Avg Upside'] = opp_df['avg_upside_pct'].apply(format_upside)
            rank_display['Profit Gr'] = opp_df['avg_npatmi_growth_2025'].apply(format_growth) if 'avg_npatmi_growth_2025' in opp_df.columns else 'N/A'
            rank_display['PE Discount'] = opp_df['pe_discount_pct'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else 'N/A')
            rank_display['PE FWD 25'] = opp_df['pe_fwd_2025'].apply(lambda x: f"{x:.1f}x" if pd.notna(x) else 'N/A')

            st.markdown(render_styled_table(rank_display, highlight_first_col=True), unsafe_allow_html=True)

            # Legend
            st.markdown("""
            **Giải thích Score Components:**
            - **Upside (30%)**: Avg upside % của các mã trong ngành → cao = tốt
            - **Growth (25%)**: Tăng trưởng LNST 2025F vs 2024 → cao = tốt
            - **Discount vs TTM (25%)**: PE FWD < PE TTM → dương = hấp dẫn (discount)
            - **Low PE (20%)**: PE FWD 2025 thấp → tốt

            **PE Discount**: Dương = PE Forward thấp hơn PE TTM (ngành được kỳ vọng tăng trưởng)
            """)
        else:
            st.info("Không có dữ liệu opportunity score.")

    elif chart_type == "PE FWD by Sector":
        st.markdown("### PE Forward 2025-2026 by Sector")

        if not sector_df.empty:
            # Sort by PE 2025
            chart_df = sector_df.sort_values('pe_fwd_2025')

            fig = go.Figure()

            # PE 2025 bars
            fig.add_trace(go.Bar(
                x=chart_df['sector'],
                y=chart_df['pe_fwd_2025'],
                name='PE FWD 2025',
                marker_color=CHART_COLORS['primary'],
                hovertemplate='<b>%{x}</b><br>PE FWD 2025: %{y:.1f}x<extra></extra>'
            ))

            # PE 2026 bars
            fig.add_trace(go.Bar(
                x=chart_df['sector'],
                y=chart_df['pe_fwd_2026'],
                name='PE FWD 2026',
                marker_color=CHART_COLORS['secondary'],
                hovertemplate='<b>%{x}</b><br>PE FWD 2026: %{y:.1f}x<extra></extra>'
            ))

            layout = get_chart_layout(height=500)
            layout['barmode'] = 'group'
            layout['showlegend'] = True
            layout['legend'] = dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5,
                font=dict(size=12, color='#E8E8E8')
            )
            layout['yaxis']['title'] = 'PE Forward'
            layout['xaxis']['tickangle'] = -45

            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Rating Distribution":
        st.markdown("### Rating Distribution")

        rating_counts = service.get_rating_distribution()

        if rating_counts:
            # Order ratings
            rating_order = ['STRONG BUY', 'BUY', 'HOLD', 'SELL', 'N/A']
            ordered_ratings = [r for r in rating_order if r in rating_counts]
            counts = [rating_counts[r] for r in ordered_ratings]
            colors = [RATING_COLORS.get(r, '#64748B') for r in ordered_ratings]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=ordered_ratings,
                y=counts,
                marker_color=colors,
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            ))

            layout = get_chart_layout(height=400)
            layout['yaxis']['title'] = 'Number of Stocks'
            layout['xaxis']['title'] = 'Rating'

            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)

            # Stats
            total = sum(counts)
            st.markdown(f"**Total: {total} stocks** | "
                       f"STRONG BUY: {rating_counts.get('STRONG BUY', 0)} | "
                       f"BUY: {rating_counts.get('BUY', 0)} | "
                       f"HOLD: {rating_counts.get('HOLD', 0)}")

    elif chart_type == "Upside vs PE":
        st.markdown("### Upside Potential vs PE Forward 2025")
        st.markdown("*Bubble size represents market cap*")

        if not df.empty:
            # Filter valid data for scatter
            scatter_df = df[
                (df['upside_pct'].notna()) &
                (df['pe_fwd_2025'].notna()) &
                (df['pe_fwd_2025'] > 0) &
                (df['pe_fwd_2025'] < 50) &  # Remove outliers
                (df['market_cap'] > 0)
            ].copy()

            if not scatter_df.empty:
                # Map ratings to colors
                scatter_df['color'] = scatter_df['rating'].map(RATING_COLORS).fillna('#64748B')

                # Scale market cap for bubble size
                scatter_df['size'] = scatter_df['market_cap'] / scatter_df['market_cap'].max() * 40 + 5

                fig = go.Figure()

                for rating in ['STRONG BUY', 'BUY', 'HOLD', 'SELL', 'N/A']:
                    rating_df = scatter_df[scatter_df['rating'] == rating]
                    if not rating_df.empty:
                        fig.add_trace(go.Scatter(
                            x=rating_df['pe_fwd_2025'],
                            y=rating_df['upside_pct'] * 100,
                            mode='markers',
                            name=rating,
                            marker=dict(
                                size=rating_df['size'],
                                color=RATING_COLORS.get(rating, '#64748B'),
                                opacity=0.7,
                                line=dict(width=1, color='white')
                            ),
                            text=rating_df['symbol'],
                            hovertemplate='<b>%{text}</b><br>PE FWD 2025: %{x:.1f}x<br>Upside: %{y:.1f}%<extra></extra>'
                        ))

                # Add reference lines
                fig.add_hline(y=0, line=dict(color='#FFC132', width=1, dash='dash'),
                             annotation=dict(text='Break-even', font=dict(color='#FFC132', size=10)))

                layout = get_chart_layout(height=500)
                layout['xaxis']['title'] = 'PE Forward 2025'
                layout['yaxis']['title'] = 'Upside Potential (%)'
                layout['showlegend'] = True
                layout['legend'] = dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5,
                    font=dict(size=11, color='#E8E8E8')
                )

                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough valid data for scatter plot.")

# Footer
st.markdown("---")
timestamp = service.get_data_timestamp()
st.caption(f"Data: BSC Research Forecast | {stats['total_stocks']} stocks | Last updated: {timestamp if timestamp else 'N/A'}")
