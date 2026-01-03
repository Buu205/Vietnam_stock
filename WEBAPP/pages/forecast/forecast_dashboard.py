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

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from WEBAPP.services.forecast_service import ForecastService
from WEBAPP.core.styles import get_page_style, get_table_style
from WEBAPP.core.session_state import (
    init_page_state, render_persistent_tabs,
    get_synced_ticker, get_synced_entity, clear_synced_ticker, has_synced_ticker
)
from WEBAPP.core.trading_rules import RATING_COLORS, RATING_BG_COLORS

# Tab modules (modularized for maintainability)
from WEBAPP.pages.forecast.tabs.bsc_universal_tab import render_bsc_universal_tab
from WEBAPP.pages.forecast.tabs.sector_tab import render_sector_tab
from WEBAPP.pages.forecast.tabs.achievement_tab import render_achievement_tab
from WEBAPP.pages.forecast.tabs.consensus_tab import render_consensus_tab

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
if st.sidebar.button("Refresh Data", width='stretch'):
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

# Sync indicator - show if user navigated from Fundamental pages
synced_ticker = None
if has_synced_ticker():
    synced_ticker = get_synced_ticker()
    entity = get_synced_entity()
    entity_label = {'BANK': 'Bank', 'COMPANY': 'Company', 'SECURITY': 'Security'}.get(entity, entity)

    sync_col1, sync_col2 = st.columns([6, 1])
    with sync_col1:
        st.info(f"Viewing: **{synced_ticker}** (from {entity_label} page)")
    with sync_col2:
        if st.button("Clear", key="forecast_clear_sync"):
            clear_synced_ticker()
            st.rerun()

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
# TAB 1: SECTOR VALUATION (Table + Valuation Matrix Chart)
# ============================================================================
elif active_tab == 1:
    render_sector_tab(sector_df, df, service)


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
