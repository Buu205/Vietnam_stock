"""
Main Navigation Component
==========================

Category-based navigation for dashboard.

Author: AI Assistant
Date: 2025-12-12
"""

import streamlit as st


def render_main_nav():
    """
    Render main navigation with 4 categories.

    Categories:
    1. Fundamental Analysis (FA)
    2. Valuation Analysis
    3. Technical Analysis (TA)
    4. Market Intelligence

    Usage:
        from WEBAPP.components.navigation import render_main_nav

        render_main_nav()
    """
    st.markdown("""
    <style>
    .main-nav {
        background-color: #F9FAFB;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .nav-category {
        display: inline-block;
        margin-right: 1rem;
        padding: 0.5rem 1rem;
        background-color: #FFFFFF;
        border-radius: 0.375rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .nav-category:hover {
        background-color: #1E40AF;
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        cols = st.columns(4)

        with cols[0]:
            if st.button("Fundamental Analysis", key="nav_fa", width='stretch'):
                st.switch_page("pages/1_fundamental/company_analysis.py")

        with cols[1]:
            if st.button("Valuation", key="nav_valuation", width='stretch'):
                st.switch_page("pages/2_valuation/valuation_dashboard.py")

        with cols[2]:
            if st.button("Technical", key="nav_technical", width='stretch'):
                st.switch_page("pages/3_technical/stock_technical.py")

        with cols[3]:
            if st.button("Intelligence", key="nav_intelligence", width='stretch'):
                st.switch_page("pages/4_intelligence/analyst_forecasts.py")

    st.divider()
