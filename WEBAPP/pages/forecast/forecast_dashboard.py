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
import sys
from pathlib import Path
from io import BytesIO

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from WEBAPP.services.forecast_service import ForecastService
from WEBAPP.core.styles import get_page_style, get_table_style, render_styled_table
from WEBAPP.core.session_state import init_page_state, render_persistent_tabs

# Tab modules (modularized for maintainability)
from WEBAPP.pages.forecast.tabs.bsc_universal_tab import render_bsc_universal_tab
from WEBAPP.pages.forecast.tabs.achievement_tab import render_achievement_tab
from WEBAPP.pages.forecast.tabs.consensus_tab import render_consensus_tab

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

# Initialize session state for this page
init_page_state('forecast')

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

# Tabs (Session State Persisted) - 4 tabs per refactor plan
active_tab = render_persistent_tabs(
    ["BSC Universal", "Sector", "Achievement", "Consensus"],
    "forecast_active_tab"
)


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
# TAB 0: BSC UNIVERSAL (Unified Stock Table)
# ============================================================================
if active_tab == 0:
    render_bsc_universal_tab(
        df=df,
        service=service,
        rating_filter=rating_filter,
        sector_filter=sector_filter,
        sort_by=sort_by
    )


# ============================================================================
# TAB 2: SECTOR VALUATION TABLE
# ============================================================================
elif active_tab == 1:
    st.markdown("### Sector Forward Valuation")
    st.markdown("*PE/PB Forward 2025-2026 aggregated by ICB L2 sector classification*")

    if not sector_df.empty:
        # Sub-tabs for different views of sector data (Session State Persisted)
        sector_tab = render_persistent_tabs(
            ["Valuation View", "Growth View"],
            "forecast_sector_tab",
            style="secondary"
        )

        if sector_tab == 0:
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

            # Add Total Earning Growth columns
            if 'total_earning_growth_2025' in sector_df.columns:
                sector_display['Earn Gr 25'] = sector_df['total_earning_growth_2025'].apply(format_growth)
            if 'total_earning_growth_2026' in sector_df.columns:
                sector_display['Earn Gr 26'] = sector_df['total_earning_growth_2026'].apply(format_growth)

            # Render styled table with BSC Universal row highlighted
            st.markdown(render_styled_table(sector_display, highlight_first_col=True, highlight_row='BSC Universal'), unsafe_allow_html=True)

        elif sector_tab == 1:
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

            # Profit growth columns (average)
            if 'avg_npatmi_growth_2025' in sector_df.columns:
                sector_growth['Profit Gr 25F'] = sector_df['avg_npatmi_growth_2025'].apply(format_growth)
            if 'avg_npatmi_growth_2026' in sector_df.columns:
                sector_growth['Profit Gr 26F'] = sector_df['avg_npatmi_growth_2026'].apply(format_growth)

            # Total Earning Growth columns (aggregated sector total)
            if 'total_earning_growth_2025' in sector_df.columns:
                sector_growth['Tot Earn Gr 25'] = sector_df['total_earning_growth_2025'].apply(format_growth)
            if 'total_earning_growth_2026' in sector_df.columns:
                sector_growth['Tot Earn Gr 26'] = sector_df['total_earning_growth_2026'].apply(format_growth)

            sector_growth['Avg ROE 25F'] = sector_df['avg_roe_2025f'].apply(lambda x: format_number(x * 100 if pd.notna(x) else None, 1, '%'))
            sector_growth['Avg Upside'] = sector_df['avg_upside_pct'].apply(format_upside)

            # Render styled table with BSC Universal highlighted
            st.markdown(render_styled_table(sector_growth, highlight_first_col=True, highlight_row='BSC Universal'), unsafe_allow_html=True)

            # Legend
            st.markdown("""
            **Giải thích:**
            - **Rev Gr 25F**: Tăng trưởng doanh thu TB 2024 → 2025 (forecast)
            - **Rev Gr 26F**: Tăng trưởng doanh thu TB 2025F → 2026F
            - **Profit Gr 25F**: Tăng trưởng LNST TB 2024 → 2025 (forecast)
            - **Profit Gr 26F**: Tăng trưởng LNST TB 2025F → 2026F
            - **Tot Earn Gr 25**: Tổng tăng trưởng lợi nhuận ngành 2024 → 2025
            - **Tot Earn Gr 26**: Tổng tăng trưởng lợi nhuận ngành 2025F → 2026F
            - **BSC Universal**: Tổng hợp toàn bộ 92+ mã trong BSC coverage
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
# TAB 2: ACHIEVEMENT (Cards + Filtered Table)
# ============================================================================
elif active_tab == 2:
    render_achievement_tab(df, service)


# ============================================================================
# TAB 3: CONSENSUS (BSC vs VCI Comparison) - NEW
# ============================================================================
elif active_tab == 3:
    render_consensus_tab(service)


# Footer
st.markdown("---")
timestamp = service.get_data_timestamp()
st.caption(f"Data: BSC Research Forecast | {stats['total_stocks']} stocks | Last updated: {timestamp if timestamp else 'N/A'}")
