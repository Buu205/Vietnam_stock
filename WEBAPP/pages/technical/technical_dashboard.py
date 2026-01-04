"""
Technical Dashboard - 3-Layer Systematic Trading
================================================

Premium financial dashboard with Crypto Terminal aesthetic.
Features glassmorphism design, trading-focused colors, and optimized filters.

3-Layer Analysis:
- Layer 1 (Market): Regime detection, breadth analysis, exposure model
- Layer 2 (Sector): RRG rotation, sector ranking, money flow
- Layer 3 (Stock): Signal scanner, RS Rating heatmap

Design: Crypto Terminal Dark Mode
- Purple (#8B5CF6) primary accent
- Cyan (#06B6D4) secondary accent
- Green (#10B981) bullish/positive
- Red (#EF4444) bearish/negative
- Glassmorphism cards with subtle blur

Author: Claude Code
Date: 2025-12-25
"""

import streamlit as st
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from WEBAPP.pages.technical.components import (
    render_market_overview,
    render_sector_rotation,
    render_stock_scanner,
)
from WEBAPP.pages.technical.services import get_ta_service, TADashboardService
from WEBAPP.core.styles import get_page_style, get_table_style
from WEBAPP.core.session_state import init_page_state, render_persistent_tabs

# Note: st.set_page_config is handled by main_app.py

# Inject premium styles
st.markdown(get_page_style(), unsafe_allow_html=True)
st.markdown(get_table_style(), unsafe_allow_html=True)

# Initialize session state for this page
init_page_state('technical')


def render_header() -> None:
    """Render dashboard header with title and subtitle."""
    st.markdown('''
    <div style="margin-bottom: 8px;">
        <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #F8FAFC; letter-spacing: -0.02em;">Technical Dashboard</h1>
        <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.9rem;">Market / Sector / Stock — Systematic Trading Analysis</p>
    </div>
    ''', unsafe_allow_html=True)


def main() -> None:
    """Main dashboard entry point."""

    # Header
    render_header()

    # Get singleton service
    try:
        service = get_ta_service()
    except Exception as e:
        st.error(f"Failed to initialize TA service: {e}")
        st.markdown('''
        <div style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0;">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" stroke-width="2" style="margin-bottom: 12px;">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
            </svg>
            <div style="color: #F8FAFC; font-size: 1.1rem; font-weight: 600; margin-bottom: 8px;">Run Data Pipeline First</div>
            <code style="background: rgba(0,0,0,0.4); color: #06B6D4; padding: 8px 16px; border-radius: 6px; font-size: 0.85rem;">
                python3 PROCESSORS/pipelines/daily/daily_ta_complete.py
            </code>
        </div>
        ''', unsafe_allow_html=True)
        return

    # ============ TAB NAVIGATION (Session State Persisted) ============
    active_tab = render_persistent_tabs(
        ["Market Overview", "Sector Rotation", "Stock Scanner"],
        "ta_active_tab"
    )

    # ============ RENDER ACTIVE TAB CONTENT ============
    if active_tab == 0:
        render_market_overview(service)
    elif active_tab == 1:
        render_sector_rotation(service)
    elif active_tab == 2:
        render_stock_scanner(service)

    # Footer
    st.markdown("---")
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M')
    st.markdown(f'''
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0;">
        <span style="color: #64748B; font-size: 0.75rem;">Technical Dashboard v2.0 | 3-Layer Systematic Trading</span>
        <span style="color: #64748B; font-size: 0.75rem;">Last update: {last_update}</span>
    </div>
    ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
