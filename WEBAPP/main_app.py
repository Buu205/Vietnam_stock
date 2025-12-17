"""
VN Finance Dashboard - Main Application (v2.0)
==============================================

Multi-page Streamlit application using st.navigation (Streamlit 1.36+).

Pages:
1. Company Dashboard - Company financial analysis
2. Bank Dashboard - Bank financial analysis
3. Security Dashboard - Securities company analysis
4. Sector Dashboard - Sector-level aggregation
5. Valuation Dashboard - PE/PB/PS/EV-EBITDA valuation
6. Technical Dashboard - Technical analysis indicators

Run:
    streamlit run WEBAPP/main_app.py
"""

import streamlit as st
from pathlib import Path

# ============================================================================
# PAGE CONFIG - Must be first Streamlit command
# ============================================================================
st.set_page_config(
    page_title="VN Finance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# DEFINE PAGES using st.Page
# ============================================================================
# Use resolve() to get absolute paths - required for st.Page
pages_dir = Path(__file__).resolve().parent / "pages"

# Create page objects with absolute paths
company_page = st.Page(
    str(pages_dir / "company" / "company_dashboard.py"),
    title="Company Analysis",
    icon="🏢",
    default=True
)

bank_page = st.Page(
    str(pages_dir / "bank" / "bank_dashboard.py"),
    title="Bank Analysis",
    icon="🏦"
)

security_page = st.Page(
    str(pages_dir / "security" / "security_dashboard.py"),
    title="Security Analysis",
    icon="📈"
)

sector_page = st.Page(
    str(pages_dir / "sector" / "sector_dashboard.py"),
    title="Sector Overview",
    icon="🌐"
)

valuation_page = st.Page(
    str(pages_dir / "valuation" / "valuation_dashboard.py"),
    title="Valuation",
    icon="💰"
)

technical_page = st.Page(
    str(pages_dir / "technical" / "technical_dashboard.py"),
    title="Technical Analysis",
    icon="📉"
)

forecast_page = st.Page(
    str(pages_dir / "forecast" / "forecast_dashboard.py"),
    title="BSC Forecast",
    icon="🎯"
)

# ============================================================================
# SIDEBAR - QUICK TICKER SEARCH (Compact)
# ============================================================================
with st.sidebar:
    # Load available tickers for autocomplete
    @st.cache_data(ttl=3600)
    def load_all_tickers():
        """Load all available tickers from valuation data."""
        import pandas as pd
        try:
            pe_file = Path(__file__).resolve().parent.parent / "DATA" / "processed" / "valuation" / "pe" / "historical" / "historical_pe.parquet"
            if pe_file.exists():
                df = pd.read_parquet(pe_file, columns=['symbol'])
                return sorted(df['symbol'].unique().tolist())
        except:
            pass
        return []

    all_tickers = load_all_tickers()

    # Compact search input
    search_ticker = st.text_input(
        "🔍 Quick Search",
        placeholder="Enter ticker...",
        key="global_ticker_search",
        help="Type a ticker symbol"
    ).upper().strip()

    if search_ticker:
        matches = [t for t in all_tickers if search_ticker in t]
        if matches:
            if len(matches) == 1 or search_ticker in matches:
                selected = search_ticker if search_ticker in matches else matches[0]
                st.session_state['quick_search_ticker'] = selected
            else:
                selected = st.selectbox(
                    "Select",
                    matches[:15],
                    key="search_select",
                    label_visibility="collapsed"
                )
                if selected:
                    st.session_state['quick_search_ticker'] = selected
        else:
            st.caption(f"❌ '{search_ticker}' not found")

    # Compact navigation buttons if ticker selected
    if st.session_state.get('quick_search_ticker'):
        ticker = st.session_state['quick_search_ticker']
        st.success(f"**{ticker}**", icon="✅")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏢", key="nav_company", help="Company", use_container_width=True):
                st.switch_page("pages/company/company_dashboard.py")
            if st.button("💰", key="nav_valuation", help="Valuation", use_container_width=True):
                st.switch_page("pages/valuation/valuation_dashboard.py")
        with c2:
            if st.button("🏦", key="nav_bank", help="Bank", use_container_width=True):
                st.switch_page("pages/bank/bank_dashboard.py")
            if st.button("📉", key="nav_technical", help="Technical", use_container_width=True):
                st.switch_page("pages/technical/technical_dashboard.py")

# ============================================================================
# NAVIGATION
# ============================================================================
pg = st.navigation({
    "Fundamental": [company_page, bank_page, security_page],
    "Analysis": [sector_page, valuation_page, technical_page, forecast_page]
})

# ============================================================================
# RUN SELECTED PAGE
# ============================================================================
pg.run()
