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
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from WEBAPP.core.styles import get_page_style
from WEBAPP.core.session_state import init_all_pages

# ============================================================================
# PAGE CONFIG - Must be first Streamlit command
# ============================================================================
st.set_page_config(
    page_title="VN Finance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Chart-first: maximize viewport
)

# ============================================================================
# INJECT GLOBAL STYLES (includes floating sidebar toggle)
# ============================================================================
st.markdown(get_page_style(), unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE (prevents widget reset issues)
# ============================================================================
init_all_pages()

# ============================================================================
# DEFINE PAGES using st.Page
# ============================================================================
# Use resolve() to get absolute paths - required for st.Page
pages_dir = Path(__file__).resolve().parent / "pages"

# Create page objects with absolute paths
# Using Material Icons (SVG) for professional, consistent sizing
company_page = st.Page(
    str(pages_dir / "company" / "company_dashboard.py"),
    title="Company Analysis",
    icon=":material/business:",
    default=True
)

bank_page = st.Page(
    str(pages_dir / "bank" / "bank_dashboard.py"),
    title="Bank Analysis",
    icon=":material/account_balance:"
)

security_page = st.Page(
    str(pages_dir / "security" / "security_dashboard.py"),
    title="Security Analysis",
    icon=":material/show_chart:"
)

sector_page = st.Page(
    str(pages_dir / "sector" / "sector_dashboard.py"),
    title="Sector & Valuation",
    icon=":material/pie_chart:"
)

fx_commodities_page = st.Page(
    str(pages_dir / "fx_commodities" / "fx_commodities_dashboard.py"),
    title="FX & Commodities",
    icon=":material/currency_exchange:"
)

technical_page = st.Page(
    str(pages_dir / "technical" / "technical_dashboard.py"),
    title="Technical Analysis",
    icon=":material/trending_up:"
)

forecast_page = st.Page(
    str(pages_dir / "forecast" / "forecast_dashboard.py"),
    title="BSC Forecast",
    icon=":material/track_changes:"
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

    # Quick Search - using session state to prevent page resets
    st.text_input(
        "🔍 Quick Search",
        placeholder="Enter ticker...",
        key="global_ticker_search",
        help="Type a ticker symbol",
        on_change=lambda: None  # Prevent form submission interference
    )
    search_ticker = st.session_state.get("global_ticker_search", "").upper().strip()

    if search_ticker:
        matches = [t for t in all_tickers if search_ticker in t]
        if matches:
            if len(matches) == 1 or search_ticker in matches:
                selected = search_ticker if search_ticker in matches else matches[0]
                st.session_state['quick_search_ticker'] = selected
            elif len(matches) <= 15:
                # Only show selectbox if there are multiple matches
                st.selectbox(
                    "Select",
                    matches,
                    key="search_select",
                    label_visibility="collapsed",
                    on_change=lambda: st.session_state.update({'quick_search_ticker': st.session_state.get('search_select')})
                )
        else:
            st.caption(f"❌ '{search_ticker}' not found")

    # Compact navigation buttons if ticker selected
    if st.session_state.get('quick_search_ticker'):
        ticker = st.session_state['quick_search_ticker']
        st.success(f"**{ticker}**", icon="✅")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏢", key="nav_company", help="Company", width='stretch'):
                st.switch_page("pages/company/company_dashboard.py")
            if st.button("💰", key="nav_valuation", help="Sector & Valuation", width='stretch'):
                st.switch_page("pages/sector/sector_dashboard.py")
        with c2:
            if st.button("🏦", key="nav_bank", help="Bank", width='stretch'):
                st.switch_page("pages/bank/bank_dashboard.py")
            if st.button("📉", key="nav_technical", help="Technical", width='stretch'):
                st.switch_page("pages/technical/technical_dashboard.py")

# ============================================================================
# NAVIGATION
# ============================================================================
pg = st.navigation({
    "Fundamental": [company_page, bank_page, security_page],
    "Analysis": [sector_page, technical_page, forecast_page, fx_commodities_page]
})

# ============================================================================
# RUN SELECTED PAGE
# ============================================================================
pg.run()
