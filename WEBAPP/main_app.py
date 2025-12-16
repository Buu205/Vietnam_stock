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

# ============================================================================
# NAVIGATION
# ============================================================================
pg = st.navigation({
    "Fundamental": [company_page, bank_page, security_page],
    "Analysis": [sector_page, valuation_page, technical_page]
})

# ============================================================================
# RUN SELECTED PAGE
# ============================================================================
pg.run()
