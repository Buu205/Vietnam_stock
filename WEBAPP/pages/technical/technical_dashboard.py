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


def render_compact_status_bar(service: TADashboardService) -> None:
    """Render compact market status bar with glassmorphism styling."""
    try:
        state = service.get_market_state()

        # Regime styling
        regime_styles = {
            'BULLISH': ('#10B981', 'rgba(16, 185, 129, 0.15)'),
            'NEUTRAL': ('#F59E0B', 'rgba(245, 158, 11, 0.15)'),
            'BEARISH': ('#EF4444', 'rgba(239, 68, 68, 0.15)'),
        }
        signal_styles = {
            'RISK_ON': ('#10B981', 'rgba(16, 185, 129, 0.15)'),
            'CAUTION': ('#F59E0B', 'rgba(245, 158, 11, 0.15)'),
            'RISK_OFF': ('#EF4444', 'rgba(239, 68, 68, 0.15)'),
        }

        regime_color, regime_bg = regime_styles.get(state.regime, ('#64748B', 'rgba(100, 116, 139, 0.15)'))
        signal_color, signal_bg = signal_styles.get(state.signal, ('#64748B', 'rgba(100, 116, 139, 0.15)'))
        change_color = '#10B981' if state.vnindex_change_pct >= 0 else '#EF4444'
        change_sign = '+' if state.vnindex_change_pct >= 0 else ''

        # Exposure bar color
        if state.exposure_level >= 80:
            exp_color = '#10B981'
        elif state.exposure_level >= 60:
            exp_color = '#22C55E'
        elif state.exposure_level >= 40:
            exp_color = '#F59E0B'
        else:
            exp_color = '#EF4444'

        st.markdown(f'''
        <div style="display: flex; gap: 12px; padding: 8px 0; flex-wrap: wrap; align-items: stretch; margin-bottom: 16px;">
            <div style="flex: 1; min-width: 130px; background: rgba(139, 92, 246, 0.08); padding: 10px 14px; border-radius: 8px; border-left: 3px solid #8B5CF6;">
                <div style="color: #64748B; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">VN-Index</div>
                <div style="display: flex; align-items: baseline; gap: 6px; margin-top: 2px;">
                    <span style="color: #F8FAFC; font-size: 1.2rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">{state.vnindex_close:,.0f}</span>
                    <span style="color: {change_color}; font-size: 0.8rem; font-weight: 600;">{change_sign}{state.vnindex_change_pct:.2f}%</span>
                </div>
            </div>
            <div style="flex: 0.8; min-width: 100px; background: {regime_bg}; padding: 10px 14px; border-radius: 8px; border-left: 3px solid {regime_color};">
                <div style="color: #64748B; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Regime</div>
                <div style="color: {regime_color}; font-size: 0.95rem; font-weight: 700; margin-top: 2px; display: flex; align-items: center; gap: 4px;">
                    <span style="display: inline-block; width: 6px; height: 6px; background: {regime_color}; border-radius: 50%;"></span>
                    {state.regime}
                </div>
            </div>
            <div style="flex: 0.8; min-width: 100px; background: {signal_bg}; padding: 10px 14px; border-radius: 8px; border-left: 3px solid {signal_color};">
                <div style="color: #64748B; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Signal</div>
                <div style="color: {signal_color}; font-size: 0.95rem; font-weight: 700; margin-top: 2px; display: flex; align-items: center; gap: 4px;">
                    <span style="display: inline-block; width: 6px; height: 6px; background: {signal_color}; border-radius: 50%;"></span>
                    {state.signal.replace('_', ' ')}
                </div>
            </div>
            <div style="flex: 0.8; min-width: 90px; background: rgba(6, 182, 212, 0.08); padding: 10px 14px; border-radius: 8px; border-left: 3px solid #06B6D4;">
                <div style="color: #64748B; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">MA20</div>
                <div style="color: #06B6D4; font-size: 1.1rem; font-weight: 700; margin-top: 2px; font-family: 'JetBrains Mono', monospace;">{state.breadth_ma20_pct:.0f}%</div>
            </div>
            <div style="flex: 1.2; min-width: 140px; background: rgba(0, 0, 0, 0.25); padding: 10px 14px; border-radius: 8px; border-left: 3px solid {exp_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #64748B; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Exposure</span>
                    <span style="color: {exp_color}; font-size: 0.9rem; font-weight: 700;">{state.exposure_level}%</span>
                </div>
                <div style="height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-top: 6px; overflow: hidden;">
                    <div style="width: {state.exposure_level}%; height: 100%; background: {exp_color}; border-radius: 2px;"></div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"Could not load market status: {e}")


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

    # Compact status bar
    render_compact_status_bar(service)

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
