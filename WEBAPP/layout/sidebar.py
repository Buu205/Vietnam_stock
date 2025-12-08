"""Sidebar builder (bilingual / song ngữ)

VN: Hàm dựng Sidebar chung: chọn symbol, số năm, và điều hướng tab.
"""

from __future__ import annotations
import streamlit as st
from typing import List, Tuple


def build_sidebar(symbols: List[str]) -> Tuple[str, int, str]:
    """Render sidebar chung và trả về (selected_symbol, years, active_tab).

    Tabs: 'Standard', 'Financial Tables', 'Valuation'
    """
    with st.sidebar:
        st.header("📊 Configuration")

        selected_symbol = st.selectbox(
            "Select Company",
            options=symbols,
            index=0 if symbols else None,
            help="Choose a company to analyze",
        )

        st.header("⚙️ Data Settings")
        years = st.slider(
            "Years of Historical Data",
            min_value=1, max_value=10, value=5,
            help="Select number of years of historical data to display",
        )

        st.header("🚀 Quick Navigation")
        active_tab = st.radio(
            "Go to",
            options=["Standard", "Financial Tables", "Valuation"],
            horizontal=False,
        )
    return selected_symbol, years, active_tab


