"""
Stock Scanner Component - Tab 3
===============================

Unified Signal Scanner with FULL 100-point composite scoring (v2.1).

Design: Dark Mode OLED + Fintech palette
- No emojis - use text badges (++/+/=/-/--)
- Side-by-side MUA/BAN tables
- Score breakdown panels (6 factors)

6 Factors (100 pts total):
1. Pattern (15 pts) - Candlestick pattern quality
2. VSA (25 pts) - Volume Spread Analysis
3. Trend (20 pts) - Trend alignment
4. S/R (15 pts) - Support/Resistance proximity
5. RS (15 pts) - Relative Strength rating
6. Liquidity (10 pts) - Trading value

Author: Claude Code
Date: 2026-01-12
"""

import streamlit as st
import pandas as pd
from typing import TYPE_CHECKING, Optional
from datetime import datetime, timedelta

from WEBAPP.core.styles import get_table_style, get_status_class
from WEBAPP.core.trading_rules import (
    SIGNAL_TYPES, PATTERN_INTERPRETATIONS, PATTERN_VOLUME_MATRIX,
    VOLUME_CONTEXT, ACTION_COLORS
)
from WEBAPP.core.session_state import get_synced_ticker, has_synced_ticker

if TYPE_CHECKING:
    from ..services.ta_dashboard_service import TADashboardService


# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render_stock_scanner(service: 'TADashboardService') -> None:
    """
    Render Stock Scanner tab following dashboard conventions.

    Components:
    1. Single Stock Analysis (TOP - linked with Fundamental sync)
    2. Quick Filters (symbol search, sector, days filter)
    3. Advanced Filters (signal type, direction, min strength)
    4. Signal Summary (st.metric cards)
    5. Signal Table with:
       - Progress bar gauge for score
       - Pattern interpretation (Vietnamese with diacritics)
       - Volume context
       - Signal date
    6. Pattern Interpretation Guide panel
    """

    # Load signals data
    signals = service.get_signals()

    if signals is None or signals.empty:
        _render_empty_state()
        return

    # ============ SINGLE STOCK ANALYSIS (TOP - linked with Fundamental) ============
    _render_single_stock_analysis(signals)

    st.markdown("---")

    # ============ UNIFIED SIGNAL SCANNER (Full Spec Scoring) ============
    _render_unified_signal_scanner(signals, service)


def _render_pattern_tab(signals: pd.DataFrame, service: 'TADashboardService') -> None:
    """Render Pattern Signals tab content."""
    # ============ QUICK FILTERS (Composite Scoring UI) ============
    st.markdown("### Bộ lọc tín hiệu")

    # Check for synced ticker from Fundamental pages
    default_search = ""
    synced_indicator = ""
    if has_synced_ticker():
        synced = get_synced_ticker()
        if not st.session_state.get('scanner_quick_search'):
            default_search = synced
            synced_indicator = f" (from Fundamental)"

    # Row 1: Symbol + Direction + Score + Days
    qcol1, qcol2, qcol3, qcol4 = st.columns([2, 1, 1, 1])

    with qcol1:
        search_symbols = st.text_input(
            "Tìm mã",
            value=default_search if not st.session_state.get('scanner_quick_search') else None,
            placeholder="VCB, ACB, FPT (phân tách bằng dấu phẩy)",
            key="scanner_quick_search",
            label_visibility="collapsed",
            help=f"Pre-filled with synced ticker{synced_indicator}" if synced_indicator else None
        )

    with qcol2:
        # Direction filter - simplified for composite UI (no emoji icons)
        direction_options = ['Tất cả', 'MUA', 'BÁN', 'CHỜ']
        selected_direction = st.selectbox(
            "Hướng",
            direction_options,
            format_func=lambda x: {
                'Tất cả': 'Tất cả hướng',
                'MUA': 'MUA',
                'BÁN': 'BÁN',
                'CHỜ': 'CHỜ'
            }.get(x, x),
            key="scanner_direction_quick",
            label_visibility="collapsed"
        )

    with qcol3:
        # Composite Score filter as slider (more flexible than dropdown)
        min_score = st.slider(
            "Điểm tối thiểu",
            min_value=0,
            max_value=100,
            value=50,  # Default: 50 điểm
            step=5,
            key="scanner_min_score",
            label_visibility="collapsed",
            help="Điểm composite (6 yếu tố): 80+ Mạnh, 60-79 Khá, 50-59 TB, <50 Yếu"
        )

    with qcol4:
        days_options = {1: "1 phiên", 2: "2 phiên", 5: "5 phiên", 10: "10 phiên"}
        selected_days = st.selectbox(
            "Thời gian",
            options=list(days_options.keys()),
            format_func=lambda x: days_options[x],
            index=1,
            key="scanner_days",
            label_visibility="collapsed"
        )

    # ============ ADVANCED FILTERS (Composite Scoring) ============
    with st.expander("Bộ lọc nâng cao", expanded=False):
        # Row 1: Sector, Signal Type, Trend
        fcol1, fcol2, fcol3 = st.columns(3)

        with fcol1:
            sectors = service.get_sector_list()
            sector_options = ["Tất cả ngành"] + sectors
            selected_sector = st.selectbox(
                "Ngành",
                sector_options,
                key="scanner_sector",
                label_visibility="visible"
            )

        with fcol2:
            type_options = ['Tất cả'] + list(signals['signal_type'].unique()) if 'signal_type' in signals.columns else ['Tất cả']
            selected_type = st.selectbox(
                "Loại tín hiệu",
                type_options,
                format_func=lambda x: 'Tất cả loại' if x == 'Tất cả' else SIGNAL_TYPES.get(x, x.replace('_', ' ').title()),
                key="scanner_type"
            )

        with fcol3:
            # Trend filter - no emoji icons
            trend_options = ['Tất cả', 'UPTREND', 'DOWNTREND', 'SIDEWAYS']
            selected_trend = st.selectbox(
                "Xu hướng",
                trend_options,
                format_func=lambda x: {
                    'Tất cả': 'Tất cả xu hướng',
                    'UPTREND': 'Tăng (+ Strong Up)',
                    'DOWNTREND': 'Giảm (+ Strong Down)',
                    'SIDEWAYS': 'Đi ngang'
                }.get(x, x),
                key="scanner_trend"
            )

        # Row 2: VSA Context, Trend Alignment, Liquidity
        fcol4, fcol5, fcol6 = st.columns(3)

        with fcol4:
            # VSA Context filter (from composite scoring) - no emoji icons
            vsa_options = ['Tất cả', 'Bullish', 'Bearish', 'Neutral']
            selected_vsa = st.selectbox(
                "VSA Context",
                vsa_options,
                format_func=lambda x: {
                    'Tất cả': 'Tất cả VSA',
                    'Bullish': 'Tích lũy (+)',
                    'Bearish': 'Phân phối (-)',
                    'Neutral': 'Trung lập'
                }.get(x, x),
                key="scanner_vsa",
                help="Volume Spread Analysis: Tích lũy (+10-25đ), Phân phối (-5-25đ), Trung lập (0đ)"
            )

        with fcol5:
            # Trend Alignment filter - no emoji icons
            alignment_options = ['Tất cả', 'Aligned', 'Counter']
            selected_alignment = st.selectbox(
                "Trend Alignment",
                alignment_options,
                format_func=lambda x: {
                    'Tất cả': 'Tất cả',
                    'Aligned': 'Thuận trend (+20đ)',
                    'Counter': 'Ngược trend (-10đ)'
                }.get(x, x),
                key="scanner_alignment",
                help="Thuận trend: BUY trong uptrend, SELL trong downtrend"
            )

        with fcol6:
            # Liquidity filter with updated thresholds (plan v2.1)
            liquidity_options = [0, 30, 50, 100]
            min_value_bn = st.selectbox(
                "GTGD tối thiểu",
                liquidity_options,
                format_func=lambda x: {
                    0: 'Tất cả thanh khoản',
                    30: '≥30 tỷ (7đ)',
                    50: '≥50 tỷ (8đ)',
                    100: '≥100 tỷ (10đ)'
                }.get(x, f'≥{x} tỷ'),
                key="scanner_min_value",
                help="Thanh khoản: <10 tỷ (0đ), 10-30 tỷ (5đ), 30-50 tỷ (7đ), 50-100 tỷ (8đ), >100 tỷ (10đ)"
            )

        # Row 3: RS Rating range (optional)
        fcol7, fcol8, _ = st.columns(3)

        with fcol7:
            min_rs = st.slider(
                "RS Rating tối thiểu",
                min_value=0,
                max_value=100,
                value=0,
                key="scanner_min_rs",
                help="RS Rating: >70 (15đ), 50-70 (10đ), 30-50 (5đ), <30 (0đ)"
            )

    # ============ APPLY FILTERS (Composite Scoring) ============
    # Map direction from Quick Filter (MUA/BÁN/CHỜ → BUY/SELL/NEUTRAL)
    direction_map = {'MUA': 'BUY', 'BÁN': 'SELL', 'CHỜ': 'NEUTRAL'}
    mapped_direction = direction_map.get(selected_direction) if selected_direction != 'Tất cả' else None

    filtered = _apply_filters(
        signals,
        search_symbols,
        selected_sector if selected_sector != "Tất cả ngành" else None,
        selected_type if selected_type != 'Tất cả' else None,
        mapped_direction,  # Use mapped direction from Quick Filter
        min_score,  # Composite score (replaces min_strength)
        selected_days,
        min_value_bn,  # Liquidity filter (updated thresholds)
        selected_trend if selected_trend != 'Tất cả' else None,  # Trend filter
        selected_vsa if selected_vsa != 'Tất cả' else None,  # VSA context filter
        selected_alignment if selected_alignment != 'Tất cả' else None,  # Trend alignment filter
        min_rs  # RS Rating filter
    )

    st.markdown("---")

    # ============ SIGNAL SUMMARY (st.metric - dashboard standard) ============
    _render_signal_summary(filtered)

    st.markdown("---")

    # ============ SPLIT TABLES: MUA (left) | BÁN (right) ============
    _render_split_tables(filtered)

    # ============ PATTERN INTERPRETATION GUIDE ============
    if not filtered.empty:
        st.markdown("---")
        _render_pattern_guide(filtered)

    # ============ DOWNLOAD ============
    if not filtered.empty:
        _render_download_button(filtered)


# ============================================================================
# UNIFIED SIGNAL SCANNER (Full Spec Scoring)
# ============================================================================

def _render_unified_signal_scanner(signals: pd.DataFrame, service: 'TADashboardService') -> None:
    """
    Render unified Signal Scanner with FULL 100-point scoring.

    Design: Dark Mode OLED + Fintech palette
    - Side-by-side MUA/BAN tables
    - Score breakdown panels (6 factors)
    - No emojis - use text badges

    Layout:
    1. Quick Filters (Huong, Diem, Thoi gian, Ma, Nganh)
    2. Summary metrics (st.metric)
    3. Side-by-side MUA/BAN tables
    4. Score breakdown panels for selected tickers
    """
    # ============ HEADER ============
    st.markdown("### Signal Scanner (100 pts)")

    # Check for synced ticker
    default_search = ""
    if has_synced_ticker():
        synced = get_synced_ticker()
        if not st.session_state.get('scanner_quick_search'):
            default_search = synced

    # ============ QUICK FILTERS (Row 1) ============
    fcol1, fcol2, fcol3, fcol4 = st.columns([2, 1, 1, 1])

    with fcol1:
        search_symbols = st.text_input(
            "Tìm mã",
            value=default_search if not st.session_state.get('scanner_quick_search') else None,
            placeholder="VCB, ACB, FPT (dấu phẩy)",
            key="scanner_quick_search",
            label_visibility="collapsed"
        )

    with fcol2:
        direction_options = ['Tất cả', 'MUA', 'BÁN']
        selected_direction = st.selectbox(
            "Hướng",
            direction_options,
            format_func=lambda x: {'Tất cả': 'Tất cả', 'MUA': 'MUA (+)', 'BÁN': 'BÁN (-)'}.get(x, x),
            key="scanner_direction_unified",
            label_visibility="collapsed"
        )

    with fcol3:
        min_score = st.slider(
            "Điểm tối thiểu",
            min_value=0, max_value=100, value=50, step=5,
            key="scanner_min_score_unified",
            label_visibility="collapsed",
            help="Composite Score: 80+ Mạnh, 60-79 Khá, 50-59 TB"
        )

    with fcol4:
        days_options = {1: "1 phiên", 2: "2 phiên", 5: "5 phiên"}
        selected_days = st.selectbox(
            "Thời gian",
            options=list(days_options.keys()),
            format_func=lambda x: days_options[x],
            index=1,
            key="scanner_days_unified",
            label_visibility="collapsed"
        )

    # ============ ADVANCED FILTERS (Expandable) ============
    with st.expander("Bộ lọc nâng cao", expanded=False):
        afcol1, afcol2, afcol3 = st.columns(3)

        with afcol1:
            sectors = service.get_sector_list()
            selected_sector = st.selectbox(
                "Ngành",
                ["Tất cả ngành"] + sectors,
                key="scanner_sector_unified"
            )

        with afcol2:
            trend_options = ['Tất cả', 'UPTREND', 'DOWNTREND', 'SIDEWAYS']
            selected_trend = st.selectbox(
                "Xu hướng",
                trend_options,
                format_func=lambda x: {'Tất cả': 'Tất cả', 'UPTREND': 'Tăng (++/+)', 'DOWNTREND': 'Giảm (--/-)', 'SIDEWAYS': 'Ngang (=)'}.get(x, x),
                key="scanner_trend_unified"
            )

        with afcol3:
            min_rs = st.slider(
                "RS Rating tối thiểu",
                min_value=0, max_value=100, value=0,
                key="scanner_min_rs_unified",
                help="RS: 80+ (15đ), 70-79 (13đ), 50-69 (10đ)"
            )

    # ============ APPLY FILTERS ============
    direction_map = {'MUA': 'BUY', 'BÁN': 'SELL'}
    mapped_direction = direction_map.get(selected_direction) if selected_direction != 'Tất cả' else None

    filtered = _apply_unified_filters(
        signals,
        search_symbols,
        selected_sector if selected_sector != "Tất cả ngành" else None,
        mapped_direction,
        min_score,
        selected_days,
        selected_trend if selected_trend != 'Tất cả' else None,
        min_rs
    )

    st.markdown("---")

    # ============ SUMMARY METRICS ============
    _render_unified_summary(filtered)

    st.markdown("---")

    # ============ SIDE-BY-SIDE TABLES: MUA | BAN ============
    _render_unified_tables(filtered)

    # ============ SCORE BREAKDOWN PANELS ============
    if not filtered.empty:
        st.markdown("---")
        _render_unified_breakdown(filtered)


def _apply_unified_filters(
    df: pd.DataFrame,
    symbols_str: str,
    sector: str,
    direction: str,
    min_score: int,
    days: int,
    trend: str,
    min_rs: int
) -> pd.DataFrame:
    """Apply filters for unified scanner."""
    filtered = df.copy()

    # Filter by trading sessions (not calendar days)
    if 'date' in filtered.columns:
        try:
            filtered['date'] = pd.to_datetime(filtered['date'])
            # Get unique trading dates sorted descending
            unique_dates = filtered['date'].dropna().unique()
            unique_dates = pd.to_datetime(unique_dates)
            unique_dates = sorted(unique_dates, reverse=True)
            # Take top N trading sessions
            if len(unique_dates) >= days:
                valid_dates = unique_dates[:days]
                filtered = filtered[filtered['date'].isin(valid_dates)]
        except Exception:
            pass

    # Symbol search
    if symbols_str and symbols_str.strip():
        symbols = [s.strip().upper() for s in symbols_str.split(',')]
        filtered = filtered[filtered['symbol'].isin(symbols)]

    # Sector filter
    if sector and 'sector_code' in filtered.columns:
        filtered = filtered[filtered['sector_code'] == sector]

    # Direction filter
    if direction and 'direction' in filtered.columns:
        if direction == 'BUY':
            filtered = filtered[filtered['direction'].isin(['BUY', 'PULLBACK'])]
        elif direction == 'SELL':
            filtered = filtered[filtered['direction'].isin(['SELL', 'BOUNCE'])]

    # Trend filter
    if trend and 'trend' in filtered.columns:
        if trend == 'UPTREND':
            filtered = filtered[filtered['trend'].isin(['UPTREND', 'STRONG_UP'])]
        elif trend == 'DOWNTREND':
            filtered = filtered[filtered['trend'].isin(['DOWNTREND', 'STRONG_DOWN'])]
        elif trend == 'SIDEWAYS':
            filtered = filtered[filtered['trend'] == 'SIDEWAYS']

    # Composite Score filter
    score_col = 'composite_score' if 'composite_score' in filtered.columns else 'strength'
    if min_score > 0 and score_col in filtered.columns:
        score_values = filtered[score_col].copy()
        if score_values.max() <= 1:
            score_values = score_values * 100
        filtered = filtered[score_values >= min_score]

    # RS Rating filter
    if min_rs > 0 and 'rs_rating' in filtered.columns:
        filtered = filtered[filtered['rs_rating'] >= min_rs]

    # Sort by composite score
    if score_col in filtered.columns:
        filtered = filtered.sort_values(score_col, ascending=False)

    return filtered


def _render_unified_summary(signals: pd.DataFrame) -> None:
    """Render summary metrics for unified scanner."""
    if signals.empty:
        st.info("Không có tín hiệu phù hợp")
        return

    buy_signals = signals[signals['direction'].isin(['BUY', 'PULLBACK'])] if 'direction' in signals.columns else pd.DataFrame()
    sell_signals = signals[signals['direction'].isin(['SELL', 'BOUNCE'])] if 'direction' in signals.columns else pd.DataFrame()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Tổng", len(signals))
    with col2:
        st.metric("MUA", len(buy_signals), delta=None)
    with col3:
        st.metric("BÁN", len(sell_signals), delta=None)
    with col4:
        avg_score = signals['composite_score'].mean() if 'composite_score' in signals.columns else 0
        st.metric("Điểm TB", f"{avg_score:.0f}")


def _render_unified_tables(signals: pd.DataFrame) -> None:
    """Render side-by-side MUA/BAN tables."""
    if signals.empty:
        return

    # Split by direction
    buy_signals = signals[signals['direction'].isin(['BUY', 'PULLBACK'])].copy() if 'direction' in signals.columns else pd.DataFrame()
    sell_signals = signals[signals['direction'].isin(['SELL', 'BOUNCE'])].copy() if 'direction' in signals.columns else pd.DataFrame()

    # Sort by score
    score_col = 'composite_score' if 'composite_score' in signals.columns else 'strength'
    buy_signals = buy_signals.sort_values(score_col, ascending=False).head(20)
    sell_signals = sell_signals.sort_values(score_col, ascending=False).head(20)

    # Ticker selection for breakdown
    all_tickers = signals['symbol'].unique().tolist()
    st.markdown("##### Chọn mã để xem chi tiết")
    selected_tickers = st.multiselect(
        "Mã",
        options=all_tickers[:50],  # Limit options
        default=[],
        max_selections=5,
        key="scanner_selected_unified",
        label_visibility="collapsed",
        help="Chọn tối đa 5 mã"
    )
    st.session_state['_unified_selected_tickers'] = selected_tickers

    # Two columns
    col1, col2 = st.columns(2)

    with col1:
        _render_signal_table_unified(buy_signals, "MUA", "#10B981", True)

    with col2:
        _render_signal_table_unified(sell_signals, "BÁN", "#EF4444", False)


def _render_signal_table_unified(df: pd.DataFrame, title: str, accent_color: str, is_buy: bool) -> None:
    """Render signal table with Dark Mode OLED style."""
    # Trend badges (no emoji)
    trend_badges = {
        'STRONG_UP': ('++', '#10B981'),
        'UPTREND': ('+', '#34D399'),
        'SIDEWAYS': ('=', '#64748B'),
        'DOWNTREND': ('-', '#F87171'),
        'STRONG_DOWN': ('--', '#EF4444'),
    }

    has_trend = 'trend' in df.columns

    # Header
    header_html = f'''
    <div style="
        background: linear-gradient(90deg, {accent_color}15 0%, rgba(15,23,42,0.95) 100%);
        border: 1px solid {accent_color}40;
        border-radius: 12px 12px 0 0;
        padding: 10px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <span style="color: {accent_color}; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">{title}</span>
        <span style="background: {accent_color}20; color: {accent_color}; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; font-family: monospace;">{len(df)}</span>
    </div>
    '''

    # Table body
    table_html = f'''
    <div style="
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid {accent_color}20;
        border-top: none;
        border-radius: 0 0 12px 12px;
        max-height: 400px;
        overflow-y: auto;
    ">
    <table style="width: 100%; border-collapse: collapse;">
    <thead>
        <tr style="background: rgba(30, 41, 59, 0.8);">
            <th style="padding: 8px 12px; text-align: left; color: #94A3B8; font-size: 0.7rem; font-weight: 600;">MA</th>
            {'<th style="padding: 8px 6px; text-align: center; color: #94A3B8; font-size: 0.7rem;">TREND</th>' if has_trend else ''}
            <th style="padding: 8px 12px; text-align: left; color: #94A3B8; font-size: 0.7rem;">MAU HINH</th>
            <th style="padding: 8px 12px; text-align: right; color: #94A3B8; font-size: 0.7rem;">DIEM</th>
        </tr>
    </thead>
    <tbody>
    '''

    for _, row in df.iterrows():
        symbol = row.get('symbol', '-')
        pattern = row.get('type_label', row.get('pattern_name', '-'))
        score = row.get('composite_score', row.get('strength', 0))
        # Handle NaN values
        if pd.isna(score):
            score = 0
        elif score <= 1:
            score = int(score * 100)
        score = int(score)

        # Score color gradient
        if is_buy:
            if score >= 70:
                bar_color = '#10B981'
                text_color = '#10B981'
            elif score >= 50:
                bar_color = '#34D399'
                text_color = '#34D399'
            else:
                bar_color = '#64748B'
                text_color = '#64748B'
        else:
            if score >= 70:
                bar_color = '#EF4444'
                text_color = '#EF4444'
            elif score >= 50:
                bar_color = '#F87171'
                text_color = '#F87171'
            else:
                bar_color = '#64748B'
                text_color = '#64748B'

        # Trend badge (text, not emoji)
        trend = row.get('trend', '') if has_trend else ''
        if pd.isna(trend) or not isinstance(trend, str):
            trend = ''
        trend_badge, trend_color = trend_badges.get(trend, ('', '#64748B'))

        trend_cell = f'''
            <td style="padding: 8px 6px; text-align: center;">
                <span style="color: {trend_color}; font-weight: 700; font-size: 0.85rem; font-family: monospace;" title="{trend}">{trend_badge}</span>
            </td>
        ''' if has_trend else ''

        row_html = f'''
        <tr style="background: rgba(15, 23, 42, 0.6); border-bottom: 1px solid rgba(148,163,184,0.1);">
            <td style="padding: 8px 12px; color: #F8FAFC; font-weight: 600; font-family: monospace; font-size: 0.85rem;">
                {symbol}
            </td>
            {trend_cell}
            <td style="padding: 8px 12px; color: #CBD5E1; font-size: 0.8rem;">
                {pattern[:20]}
            </td>
            <td style="padding: 8px 12px;">
                <div style="display: flex; align-items: center; gap: 8px; justify-content: flex-end;">
                    <div style="flex: 1; max-width: 50px; height: 5px; background: rgba(148,163,184,0.2); border-radius: 3px; overflow: hidden;">
                        <div style="width: {score}%; height: 100%; background: {bar_color}; border-radius: 3px;"></div>
                    </div>
                    <span style="color: {text_color}; font-weight: 700; font-size: 0.8rem; min-width: 24px; text-align: right; font-family: monospace;">
                        {score}
                    </span>
                </div>
            </td>
        </tr>
        '''
        table_html += row_html

    table_html += '</tbody></table></div>'
    st.html(header_html + table_html)


def _render_unified_breakdown(signals: pd.DataFrame) -> None:
    """Render score breakdown panels for selected tickers."""
    selected_tickers = st.session_state.get('_unified_selected_tickers', [])

    if not selected_tickers:
        st.caption("Chọn mã từ dropdown phía trên để xem chi tiết điểm 6 yếu tố")
        return

    selected_signals = signals[signals['symbol'].isin(selected_tickers)]
    if selected_signals.empty:
        return

    st.markdown("##### Chi tiết điểm Composite (6 yếu tố)")

    # Render each ticker
    ticker_chunks = [selected_tickers[i:i+3] for i in range(0, len(selected_tickers), 3)]

    for chunk in ticker_chunks:
        cols = st.columns(len(chunk))

        for idx, ticker in enumerate(chunk):
            with cols[idx]:
                ticker_data = selected_signals[selected_signals['symbol'] == ticker]
                if ticker_data.empty:
                    continue
                ticker_row = ticker_data.iloc[0]

                # Extract scores
                total = ticker_row.get('composite_score', 0)
                if total <= 1:
                    total = total * 100
                pattern_s = ticker_row.get('pattern_score', 0)
                vsa_s = ticker_row.get('vsa_score', 0)
                trend_s = ticker_row.get('trend_score', 0)
                sr_s = ticker_row.get('sr_score', 0)
                rs_s = ticker_row.get('rs_score', 0)
                liq_s = ticker_row.get('liquidity_score', 0)

                # Normalize
                pattern_s = min(15, max(0, pattern_s if not pd.isna(pattern_s) else 0))
                vsa_s = min(25, max(0, vsa_s if not pd.isna(vsa_s) else 0))
                trend_s = min(20, max(0, trend_s if not pd.isna(trend_s) else 0))
                sr_s = min(15, max(0, sr_s if not pd.isna(sr_s) else 0))
                rs_s = min(15, max(0, rs_s if not pd.isna(rs_s) else 0))
                liq_s = min(10, max(0, liq_s if not pd.isna(liq_s) else 0))

                direction = ticker_row.get('direction', 'NEUTRAL')
                trend = ticker_row.get('trend', 'SIDEWAYS')
                pattern = ticker_row.get('type_label', ticker_row.get('pattern_name', '-'))

                # Direction color
                dir_color = {'BUY': '#10B981', 'SELL': '#EF4444', 'PULLBACK': '#F59E0B', 'BOUNCE': '#F59E0B'}.get(direction, '#64748B')

                breakdown_html = f'''
                <div style="
                    background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
                    border: 1px solid rgba(148, 163, 184, 0.2);
                    border-radius: 12px;
                    padding: 16px;
                ">
                    <!-- Header -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="color: #F8FAFC; font-weight: 700; font-family: monospace; font-size: 1.1rem;">{ticker}</span>
                            <span style="color: {dir_color}; font-size: 0.8rem; font-weight: 600;">{direction}</span>
                        </div>
                        <div style="
                            background: rgba(59, 130, 246, 0.2);
                            color: #60A5FA;
                            padding: 4px 12px;
                            border-radius: 20px;
                            font-size: 0.85rem;
                            font-weight: 700;
                            font-family: monospace;
                        ">{int(total)} pts</div>
                    </div>

                    <!-- Pattern & Trend -->
                    <div style="color: #94A3B8; font-size: 0.75rem; margin-bottom: 12px;">
                        {pattern[:25]} | {trend}
                    </div>

                    <!-- 6 Factor Bars -->
                    <div style="display: flex; flex-direction: column; gap: 5px;">
                        {_render_unified_bar("Pattern", pattern_s, 15, "#8B5CF6")}
                        {_render_unified_bar("VSA", vsa_s, 25, "#06B6D4")}
                        {_render_unified_bar("Trend", trend_s, 20, "#10B981")}
                        {_render_unified_bar("S/R", sr_s, 15, "#22D3EE")}
                        {_render_unified_bar("RS", rs_s, 15, "#A78BFA")}
                        {_render_unified_bar("Liq", liq_s, 10, "#64748B")}
                    </div>
                </div>
                '''
                st.html(breakdown_html)


def _render_unified_bar(label: str, score: float, max_score: float, color: str) -> str:
    """Render a single score bar."""
    pct = min(100, (score / max_score) * 100) if max_score > 0 else 0
    return f'''
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="color: #64748B; font-size: 0.65rem; min-width: 45px; text-transform: uppercase;">{label}</span>
        <div style="flex: 1; height: 5px; background: rgba(100,116,139,0.2); border-radius: 3px; overflow: hidden;">
            <div style="width: {pct}%; height: 100%; background: {color}; border-radius: 3px;"></div>
        </div>
        <span style="color: {color}; font-size: 0.7rem; font-weight: 600; min-width: 24px; text-align: right; font-family: monospace;">{int(score)}</span>
    </div>
    '''


# ============================================================================
# FILTER LOGIC
# ============================================================================

def _apply_filters(
    df: pd.DataFrame,
    symbols_str: Optional[str],
    sector: Optional[str],
    signal_type: Optional[str],
    direction: Optional[str],
    min_score: int,  # Composite score (0-100)
    days: int = 2,
    min_value_bn: float = 0,  # Liquidity filter
    trend: Optional[str] = None,  # Trend filter
    vsa_context: Optional[str] = None,  # VSA context filter
    alignment: Optional[str] = None,  # Trend alignment filter
    min_rs: int = 0  # RS Rating filter
) -> pd.DataFrame:
    """
    Apply all filters to signals dataframe.

    Composite Scoring UI filters:
    - min_score: Composite score (6 factors) 0-100
    - vsa_context: Bullish/Bearish/Neutral
    - alignment: Aligned/Counter (trend alignment)
    - min_rs: Minimum RS Rating
    """

    filtered = df.copy()

    # Filter by trading sessions (not calendar days)
    if 'date' in filtered.columns:
        try:
            filtered['date'] = pd.to_datetime(filtered['date'])
            # Get unique trading dates sorted descending
            unique_dates = filtered['date'].dropna().unique()
            unique_dates = pd.to_datetime(unique_dates)
            unique_dates = sorted(unique_dates, reverse=True)
            # Take top N trading sessions
            if len(unique_dates) >= days:
                valid_dates = unique_dates[:days]
                filtered = filtered[filtered['date'].isin(valid_dates)]
        except Exception:
            pass

    # Symbol search
    if symbols_str and symbols_str.strip():
        symbols = [s.strip().upper() for s in symbols_str.split(',')]
        filtered = filtered[filtered['symbol'].isin(symbols)]

    # Sector filter
    if sector and 'sector_code' in filtered.columns:
        filtered = filtered[filtered['sector_code'] == sector]

    # Signal type filter
    if signal_type and 'signal_type' in filtered.columns:
        filtered = filtered[filtered['signal_type'] == signal_type]

    # Direction filter (BUY/SELL includes PULLBACK/BOUNCE if related)
    if direction and 'direction' in filtered.columns:
        if direction == 'BUY':
            filtered = filtered[filtered['direction'].isin(['BUY', 'PULLBACK'])]
        elif direction == 'SELL':
            filtered = filtered[filtered['direction'].isin(['SELL', 'BOUNCE'])]
        elif direction == 'NEUTRAL':
            filtered = filtered[filtered['direction'] == 'NEUTRAL']
        else:
            filtered = filtered[filtered['direction'] == direction]

    # Trend filter (UPTREND includes STRONG_UP, DOWNTREND includes STRONG_DOWN)
    if trend and 'trend' in filtered.columns:
        if trend == 'UPTREND':
            filtered = filtered[filtered['trend'].isin(['UPTREND', 'STRONG_UP'])]
        elif trend == 'DOWNTREND':
            filtered = filtered[filtered['trend'].isin(['DOWNTREND', 'STRONG_DOWN'])]
        elif trend == 'SIDEWAYS':
            filtered = filtered[filtered['trend'] == 'SIDEWAYS']

    # Composite Score filter (replaces pattern strength)
    # Uses 'composite_score' column if exists, falls back to 'strength'
    score_col = 'composite_score' if 'composite_score' in filtered.columns else 'strength'
    if min_score > 0 and score_col in filtered.columns:
        score_values = filtered[score_col].copy()
        if score_values.max() <= 1:  # Normalize if 0-1 scale
            score_values = score_values * 100
        filtered = filtered[score_values >= min_score]

    # VSA Context filter
    if vsa_context and 'vsa_context' in filtered.columns:
        filtered = filtered[filtered['vsa_context'] == vsa_context]
    elif vsa_context and 'vsa_score' in filtered.columns:
        # Infer VSA context from score if column not present
        if vsa_context == 'Bullish':
            filtered = filtered[filtered['vsa_score'] > 5]
        elif vsa_context == 'Bearish':
            filtered = filtered[filtered['vsa_score'] < -5]
        elif vsa_context == 'Neutral':
            filtered = filtered[(filtered['vsa_score'] >= -5) & (filtered['vsa_score'] <= 5)]

    # Trend Alignment filter
    if alignment:
        # Calculate alignment if not present
        if 'is_aligned' not in filtered.columns and 'trend' in filtered.columns and 'direction' in filtered.columns:
            def check_aligned(row):
                t = row.get('trend', '')
                d = row.get('direction', '')
                if t in ['UPTREND', 'STRONG_UP'] and d in ['BUY', 'PULLBACK']:
                    return True
                if t in ['DOWNTREND', 'STRONG_DOWN'] and d in ['SELL', 'BOUNCE']:
                    return True
                return False
            filtered['_is_aligned'] = filtered.apply(check_aligned, axis=1)
            align_col = '_is_aligned'
        else:
            align_col = 'is_aligned'

        if align_col in filtered.columns:
            if alignment == 'Aligned':
                filtered = filtered[filtered[align_col] == True]
            elif alignment == 'Counter':
                filtered = filtered[filtered[align_col] == False]

        # Cleanup temp column
        if '_is_aligned' in filtered.columns:
            filtered = filtered.drop(columns=['_is_aligned'], errors='ignore')

    # RS Rating filter
    if min_rs > 0 and 'rs_rating' in filtered.columns:
        filtered = filtered[filtered['rs_rating'] >= min_rs]

    # Liquidity filter (GTGD)
    if min_value_bn > 0 and 'trading_value' in filtered.columns:
        min_value = min_value_bn * 1e9
        filtered = filtered[filtered['trading_value'] >= min_value]

    # Filter to only primary signals
    if 'is_primary' in filtered.columns:
        filtered = filtered[filtered['is_primary'] == True]

    # Sort by composite score (highest first), then by date
    sort_col = 'composite_score' if 'composite_score' in filtered.columns else 'strength'
    if 'direction' in filtered.columns:
        priority_map = {'BUY': 1, 'SELL': 2, 'PULLBACK': 3, 'BOUNCE': 4, 'NEUTRAL': 5}
        filtered['_priority'] = filtered['direction'].map(priority_map).fillna(6)

        if 'date' in filtered.columns:
            filtered = filtered.sort_values(
                ['date', '_priority', sort_col],
                ascending=[False, True, False]
            )
        else:
            filtered = filtered.sort_values(
                ['_priority', sort_col],
                ascending=[True, False]
            )

        filtered = filtered.drop(columns=['_priority'], errors='ignore')
    elif 'date' in filtered.columns:
        filtered = filtered.sort_values(['date', sort_col], ascending=[False, False])

    return filtered


# ============================================================================
# SUMMARY CARDS (st.metric - dashboard standard)
# ============================================================================

def _render_signal_summary(signals: pd.DataFrame) -> None:
    """Render signal summary using st.metric (dashboard standard)."""

    if 'direction' not in signals.columns:
        return

    direction_counts = signals['direction'].value_counts()

    total = len(signals)
    buy_count = direction_counts.get('BUY', 0) + direction_counts.get('BULLISH', 0)
    sell_count = direction_counts.get('SELL', 0) + direction_counts.get('BEARISH', 0)
    hold_count = direction_counts.get('HOLD', 0) + direction_counts.get('NEUTRAL', 0)

    # Summary using st.metric (standard across all dashboards)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Tổng tín hiệu", total)

    with col2:
        pct = f"{buy_count/total*100:.0f}%" if total > 0 else "0%"
        st.metric("MUA", buy_count, pct)

    with col3:
        pct = f"{sell_count/total*100:.0f}%" if total > 0 else "0%"
        st.metric("BÁN", sell_count, pct, delta_color="inverse")

    with col4:
        st.metric("CHỜ", hold_count)


# ============================================================================
# ENHANCED SIGNAL TABLE with Progress Bar Gauge
# ============================================================================

def _render_progress_bar_html(value: float, max_value: float = 100) -> str:
    """
    Render HTML progress bar gauge with gradient fill.
    Design: Fintech dashboard style with smooth gradient.

    Args:
        value: Current value (0-100)
        max_value: Maximum value

    Returns:
        HTML string for progress bar
    """
    # Normalize to 0-100
    pct = min(100, max(0, (value / max_value) * 100))

    # Determine color based on score (Financial Dashboard colors)
    if pct >= 80:
        bar_color = 'linear-gradient(90deg, #10B981, #22C55E)'  # Green gradient
        text_color = '#22C55E'
    elif pct >= 60:
        bar_color = 'linear-gradient(90deg, #06B6D4, #22D3EE)'  # Cyan gradient
        text_color = '#06B6D4'
    elif pct >= 40:
        bar_color = 'linear-gradient(90deg, #8B5CF6, #A78BFA)'  # Purple gradient
        text_color = '#8B5CF6'
    elif pct >= 20:
        bar_color = 'linear-gradient(90deg, #F59E0B, #FBBF24)'  # Amber gradient
        text_color = '#F59E0B'
    else:
        bar_color = 'linear-gradient(90deg, #64748B, #94A3B8)'  # Gray gradient
        text_color = '#64748B'

    return f'''
    <div style="display:flex; align-items:center; gap:8px;">
        <div style="flex:1; height:8px; background:rgba(100,116,139,0.2); border-radius:4px; overflow:hidden; min-width:80px;">
            <div style="width:{pct}%; height:100%; background:{bar_color}; border-radius:4px; transition:width 0.3s ease;"></div>
        </div>
        <span style="color:{text_color}; font-weight:600; font-size:0.85rem; min-width:28px; text-align:right;">{int(pct)}</span>
    </div>
    '''


def _get_pattern_interpretation(type_label: str, volume_context: str = None) -> str:
    """
    Get Vietnamese interpretation for a pattern/signal type.
    Uses volume context for more specific interpretation when available.

    Args:
        type_label: Pattern or signal type label
        volume_context: Optional volume context ('HIGH', 'AVG', 'LOW')

    Returns:
        Vietnamese interpretation string
    """
    if not type_label:
        return ''

    # Clean up label and convert to lowercase for lookup
    clean_label = type_label.strip().lower()
    clean_label_space = clean_label.replace('_', ' ')

    # First, try volume-context specific interpretation
    if volume_context:
        vol_ctx = volume_context.upper()
        # Try with original label
        if (clean_label, vol_ctx) in PATTERN_VOLUME_MATRIX:
            return PATTERN_VOLUME_MATRIX[(clean_label, vol_ctx)]
        # Try with space-replaced label
        if (clean_label_space, vol_ctx) in PATTERN_VOLUME_MATRIX:
            return PATTERN_VOLUME_MATRIX[(clean_label_space, vol_ctx)]

    # Fall back to pattern-only interpretation
    # Direct lookup (case-insensitive)
    if clean_label in PATTERN_INTERPRETATIONS:
        return PATTERN_INTERPRETATIONS[clean_label]

    # Replace underscores with spaces and try again
    if clean_label_space in PATTERN_INTERPRETATIONS:
        return PATTERN_INTERPRETATIONS[clean_label_space]

    # Partial match for volume spike (e.g., "vol spike 2.5x")
    if 'vol spike' in clean_label or 'volume' in clean_label:
        return PATTERN_INTERPRETATIONS.get('volume spike', PATTERN_INTERPRETATIONS.get('vol spike', ''))

    # Partial match for breakout/breakdown
    if 'breakout' in clean_label:
        return PATTERN_INTERPRETATIONS.get('breakout', '')
    if 'breakdown' in clean_label:
        return PATTERN_INTERPRETATIONS.get('breakdown', '')

    # Partial match for MA crossover
    if 'cross' in clean_label:
        if 'up' in clean_label or 'golden' in clean_label:
            return PATTERN_INTERPRETATIONS.get('golden cross', PATTERN_INTERPRETATIONS.get('ma cross up', ''))
        elif 'down' in clean_label or 'death' in clean_label:
            return PATTERN_INTERPRETATIONS.get('death cross', PATTERN_INTERPRETATIONS.get('ma cross down', ''))
        return PATTERN_INTERPRETATIONS.get('ma_crossover', '')

    # Partial match for engulfing patterns
    if 'engulf' in clean_label:
        if 'bearish' in clean_label:
            return PATTERN_INTERPRETATIONS.get('bearish engulfing', '')
        return PATTERN_INTERPRETATIONS.get('bullish engulfing', PATTERN_INTERPRETATIONS.get('engulfing', ''))

    # Partial match for star patterns
    if 'star' in clean_label:
        if 'morning' in clean_label:
            return PATTERN_INTERPRETATIONS.get('morning star', '')
        elif 'evening' in clean_label:
            return PATTERN_INTERPRETATIONS.get('evening star', '')
        elif 'shooting' in clean_label:
            return PATTERN_INTERPRETATIONS.get('shooting star', '')

    # Partial match for doji patterns
    if 'doji' in clean_label:
        if 'dragonfly' in clean_label:
            return PATTERN_INTERPRETATIONS.get('dragonfly doji', '')
        elif 'gravestone' in clean_label:
            return PATTERN_INTERPRETATIONS.get('gravestone doji', '')
        return PATTERN_INTERPRETATIONS.get('doji', '')

    return ''


# ============================================================================
# PHASE 4: SPLIT TABLES (MUA | BÁN)
# ============================================================================

def _hex_to_rgb(hex_color: str) -> str:
    """Convert hex to RGB string for rgba()."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"{r}, {g}, {b}"


def _get_score_gradient(score: int, is_buy: bool) -> str:
    """Get gradient color based on score."""
    if score >= 80:
        return "linear-gradient(90deg, #10B981, #22C55E)" if is_buy else "linear-gradient(90deg, #EF4444, #F87171)"
    elif score >= 60:
        return "linear-gradient(90deg, #06B6D4, #22D3EE)"
    elif score >= 45:
        return "linear-gradient(90deg, #8B5CF6, #A78BFA)"
    else:
        return "linear-gradient(90deg, #64748B, #94A3B8)"


def _get_score_text_color(score: int, is_buy: bool) -> str:
    """Get text color based on score."""
    if score >= 80:
        return "#22C55E" if is_buy else "#F87171"
    elif score >= 60:
        return "#22D3EE"
    elif score >= 45:
        return "#A78BFA"
    else:
        return "#94A3B8"


def _render_signal_table_compact(
    df: pd.DataFrame,
    title: str,
    accent_color: str,
    is_buy: bool = True
) -> None:
    """Render compact signal table with progress bars and trend badges."""
    if df.empty:
        st.caption(f"{title}: 0 tín hiệu")
        return

    count = len(df)
    rgb = _hex_to_rgb(accent_color)

    # Trend badge mapping - use text symbols instead of emoji
    trend_badges = {
        'STRONG_UP': ('++', '#10B981'),
        'UPTREND': ('+', '#22C55E'),
        'SIDEWAYS': ('=', '#64748B'),
        'DOWNTREND': ('-', '#F59E0B'),
        'STRONG_DOWN': ('--', '#EF4444'),
    }

    # Header
    header_html = f'''
    <div style="
        background: linear-gradient(135deg, rgba({rgb}, 0.15) 0%, rgba(0,0,0,0) 100%);
        border: 1px solid rgba({rgb}, 0.3);
        border-radius: 12px 12px 0 0;
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <span style="color: {accent_color}; font-weight: 600; font-size: 0.85rem;">
            {title}
        </span>
        <span style="
            background: rgba({rgb}, 0.2);
            color: {accent_color};
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-family: monospace;
        ">{count}</span>
    </div>
    '''

    # Check if trend column exists
    has_trend = 'trend' in df.columns

    # Table body
    table_html = f'''
    <div style="
        background: rgba(26, 22, 37, 0.8);
        border: 1px solid rgba(255,255,255,0.08);
        border-top: none;
        border-radius: 0 0 12px 12px;
        max-height: 400px;
        overflow-y: auto;
    ">
    <table style="width: 100%; border-collapse: collapse;">
    <thead>
        <tr style="background: rgba(139, 92, 246, 0.1);">
            <th style="padding: 8px 12px; text-align: left; color: #8B5CF6; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">Mã</th>
            {'<th style="padding: 8px 6px; text-align: center; color: #8B5CF6; font-size: 0.7rem; font-weight: 600;">Trend</th>' if has_trend else ''}
            <th style="padding: 8px 12px; text-align: left; color: #8B5CF6; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">Mẫu hình</th>
            <th style="padding: 8px 12px; text-align: right; color: #8B5CF6; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">Điểm</th>
        </tr>
    </thead>
    <tbody>
    '''

    for _, row in df.iterrows():
        symbol = row.get('symbol', '-')
        pattern = row.get('type_label', row.get('pattern_name', '-'))
        strength = row.get('strength', 0)
        if strength <= 1:
            strength = int(strength * 100)
        strength = int(strength)

        bar_color = _get_score_gradient(strength, is_buy)
        text_color = _get_score_text_color(strength, is_buy)

        # Trend badge
        trend = row.get('trend', '') if has_trend else ''
        # Handle NaN/float values
        if pd.isna(trend) or not isinstance(trend, str):
            trend = ''
        trend_icon, trend_color = trend_badges.get(trend, ('', '#64748B'))

        trend_cell = f'''
            <td style="padding: 8px 6px; text-align: center;">
                <span style="color: {trend_color}; font-size: 0.9rem;" title="{trend}">{trend_icon}</span>
            </td>
        ''' if has_trend else ''

        row_html = f'''
        <tr style="background: rgba(26, 22, 37, 0.6); border-bottom: 1px solid rgba(255,255,255,0.05);">
            <td style="padding: 8px 12px; color: #FFFFFF; font-weight: 600; font-family: monospace; font-size: 0.85rem;">
                {symbol}
            </td>
            {trend_cell}
            <td style="padding: 8px 12px; color: #C4B5FD; font-size: 0.8rem;">
                {pattern}
            </td>
            <td style="padding: 8px 12px;">
                <div style="display: flex; align-items: center; gap: 8px; justify-content: flex-end;">
                    <div style="flex: 1; max-width: 50px; height: 6px; background: rgba(100,116,139,0.2); border-radius: 3px; overflow: hidden;">
                        <div style="width: {strength}%; height: 100%; background: {bar_color}; border-radius: 3px;"></div>
                    </div>
                    <span style="color: {text_color}; font-weight: 700; font-size: 0.8rem; min-width: 24px; text-align: right; font-family: monospace;">
                        {strength}
                    </span>
                </div>
            </td>
        </tr>
        '''
        table_html += row_html

    table_html += '</tbody></table></div>'

    st.html(header_html + table_html)


def _render_split_tables(signals: pd.DataFrame) -> None:
    """Render signal tables with click-to-expand accordion and score breakdown."""
    if signals.empty:
        st.info("Không có tín hiệu phù hợp với bộ lọc")
        return

    # Initialize session state for selected signals (accordion)
    if 'scanner_selected_tickers' not in st.session_state:
        st.session_state.scanner_selected_tickers = []

    # Split by direction
    buy_signals = signals[signals['direction'] == 'BUY'].copy()
    sell_signals = signals[signals['direction'] == 'SELL'].copy()
    pullback_signals = signals[signals['direction'].isin(['PULLBACK', 'BOUNCE'])].copy()

    # Sort by composite score (or strength) descending
    score_col = 'composite_score' if 'composite_score' in signals.columns else 'strength'
    buy_signals = buy_signals.sort_values(score_col, ascending=False).head(30)
    sell_signals = sell_signals.sort_values(score_col, ascending=False).head(30)
    pullback_signals = pullback_signals.sort_values(score_col, ascending=False).head(30)

    # Get all available tickers for selection
    all_tickers = signals['symbol'].unique().tolist()

    # Ticker selection for accordion expansion
    st.markdown("##### Chọn mã để xem chi tiết điểm")
    selected_tickers = st.multiselect(
        "Chọn mã cổ phiếu",
        options=all_tickers,
        default=st.session_state.scanner_selected_tickers[:5],  # Max 5 for performance
        max_selections=5,
        key="scanner_ticker_select",
        label_visibility="collapsed",
        help="Chọn tối đa 5 mã để xem breakdown điểm composite (6 yếu tố)"
    )

    # Update session state
    st.session_state.scanner_selected_tickers = selected_tickers

    # Auto-sync with Single Stock Analysis (wire click)
    # Note: Cannot directly set single_stock_input after widget instantiated
    # Use a flag to trigger sync on next rerun
    if selected_tickers and len(selected_tickers) == 1:
        new_ticker = selected_tickers[0]
        if st.session_state.get('_pending_sync_ticker') != new_ticker:
            st.session_state._pending_sync_ticker = new_ticker
            st.rerun()  # Trigger rerun to apply sync

    # Three columns layout for tables
    col1, col2, col3 = st.columns(3)

    with col1:
        _render_signal_table_compact(
            buy_signals,
            title="MUA (Trend-aligned)",
            accent_color="#10B981",
            is_buy=True
        )

    with col2:
        _render_signal_table_compact(
            sell_signals,
            title="BÁN (Trend-aligned)",
            accent_color="#EF4444",
            is_buy=False
        )

    with col3:
        _render_signal_table_compact(
            pullback_signals,
            title="PULLBACK/BOUNCE",
            accent_color="#F59E0B",
            is_buy=True
        )

    # Render detail panels for selected tickers (accordion expansion)
    if selected_tickers:
        st.markdown("---")
        st.markdown("##### Chi tiết điểm Composite")
        _render_score_breakdown_panels(signals, selected_tickers)


def _render_score_breakdown_panels(signals: pd.DataFrame, selected_tickers: list) -> None:
    """
    Render score breakdown panels for selected tickers (accordion expansion).

    Shows 6-factor composite score breakdown:
    1. Candlestick Pattern (15 pts max)
    2. VSA Context (25 pts max)
    3. Trend Alignment (20 pts max)
    4. S/R Proximity (15 pts max)
    5. RS Rating (15 pts max)
    6. Liquidity (10 pts max)

    Plus S/R levels and R:R ratio.
    """
    if not selected_tickers:
        return

    # Filter signals for selected tickers
    selected_signals = signals[signals['symbol'].isin(selected_tickers)]

    if selected_signals.empty:
        return

    # Render each ticker in columns (max 3 per row)
    ticker_chunks = [selected_tickers[i:i+3] for i in range(0, len(selected_tickers), 3)]

    for chunk in ticker_chunks:
        cols = st.columns(len(chunk))

        for idx, ticker in enumerate(chunk):
            with cols[idx]:
                ticker_data = selected_signals[selected_signals['symbol'] == ticker].iloc[0] if len(selected_signals[selected_signals['symbol'] == ticker]) > 0 else None

                if ticker_data is None:
                    continue

                # Get score components (use defaults if columns don't exist)
                total_score = ticker_data.get('composite_score', ticker_data.get('strength', 0) * 100)
                if total_score <= 1:
                    total_score = total_score * 100

                pattern_score = ticker_data.get('pattern_score', 10)
                vsa_score = ticker_data.get('vsa_score', 15)
                trend_score = ticker_data.get('trend_score', 15)
                sr_score = ticker_data.get('sr_score', 10)
                rs_score = ticker_data.get('rs_score', 10)
                liquidity_score = ticker_data.get('liquidity_score', 8)

                # Normalize scores if needed
                pattern_score = min(15, max(0, pattern_score if not pd.isna(pattern_score) else 10))
                vsa_score = min(25, max(-25, vsa_score if not pd.isna(vsa_score) else 15))
                trend_score = min(20, max(-10, trend_score if not pd.isna(trend_score) else 15))
                sr_score = min(15, max(0, sr_score if not pd.isna(sr_score) else 10))
                rs_score = min(15, max(0, rs_score if not pd.isna(rs_score) else 10))
                liquidity_score = min(10, max(0, liquidity_score if not pd.isna(liquidity_score) else 8))

                # Get pattern and direction
                pattern = ticker_data.get('type_label', ticker_data.get('pattern_name', '-'))
                direction = ticker_data.get('direction', 'NEUTRAL')
                trend = ticker_data.get('trend', 'SIDEWAYS')

                # Direction color
                dir_color = {
                    'BUY': '#10B981', 'SELL': '#EF4444',
                    'PULLBACK': '#F59E0B', 'BOUNCE': '#F59E0B',
                    'NEUTRAL': '#64748B'
                }.get(direction, '#64748B')

                # Build score breakdown HTML
                breakdown_html = f'''
                <div style="
                    background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(26, 22, 37, 0.95) 100%);
                    border: 1px solid rgba(139, 92, 246, 0.3);
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 12px;
                ">
                    <!-- Header -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="color: #FFFFFF; font-weight: 700; font-family: monospace; font-size: 1.1rem;">{ticker}</span>
                            <span style="color: {dir_color}; font-size: 0.8rem; font-weight: 600;">{direction}</span>
                        </div>
                        <div style="
                            background: rgba(139, 92, 246, 0.2);
                            color: #A78BFA;
                            padding: 4px 12px;
                            border-radius: 20px;
                            font-size: 0.85rem;
                            font-weight: 700;
                            font-family: monospace;
                        ">{int(total_score)} pts</div>
                    </div>

                    <!-- Pattern -->
                    <div style="color: #C4B5FD; font-size: 0.8rem; margin-bottom: 12px;">
                        {pattern} | Trend: {trend}
                    </div>

                    <!-- 6 Factor Bars -->
                    <div style="display: flex; flex-direction: column; gap: 6px;">
                        {_render_score_bar("Pattern", pattern_score, 15, "#8B5CF6")}
                        {_render_score_bar("VSA", vsa_score, 25, "#06B6D4" if vsa_score > 0 else "#EF4444")}
                        {_render_score_bar("Trend", trend_score, 20, "#10B981" if trend_score > 0 else "#F59E0B")}
                        {_render_score_bar("S/R", sr_score, 15, "#22D3EE")}
                        {_render_score_bar("RS", rs_score, 15, "#A78BFA")}
                        {_render_score_bar("Liquidity", liquidity_score, 10, "#64748B")}
                    </div>
                </div>
                '''

                st.html(breakdown_html)


def _render_score_bar(label: str, score: float, max_score: float, color: str) -> str:
    """Render a single score bar for the breakdown panel."""
    # Handle negative scores (VSA, Trend can be negative)
    if score < 0:
        pct = 0
        display_score = f"{int(score)}"
        bar_bg = "rgba(239, 68, 68, 0.3)"
    else:
        pct = min(100, (score / max_score) * 100)
        display_score = f"+{int(score)}" if score > 0 else "0"
        bar_bg = color

    return f'''
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="color: #94A3B8; font-size: 0.7rem; min-width: 55px; text-transform: uppercase;">{label}</span>
        <div style="flex: 1; height: 6px; background: rgba(100,116,139,0.2); border-radius: 3px; overflow: hidden;">
            <div style="width: {pct}%; height: 100%; background: {bar_bg}; border-radius: 3px;"></div>
        </div>
        <span style="color: {color}; font-size: 0.75rem; font-weight: 600; min-width: 28px; text-align: right; font-family: monospace;">{display_score}</span>
    </div>
    '''


def _render_signal_table_enhanced(signals: pd.DataFrame) -> None:
    """
    Render signals table with:
    - Progress bar gauge for strength/score
    - Pattern interpretation text (Vietnamese with diacritics)
    - Color badges for direction
    - Signal date
    """

    if signals.empty:
        st.info("Không có tín hiệu phù hợp với bộ lọc")
        return

    # Prepare display data
    display_df = signals.head(100).copy()

    # Create styled header with signal count indicator
    total_signals = len(signals)
    buy_count = len(signals[signals['direction'].isin(['BUY', 'BULLISH'])]) if 'direction' in signals.columns else 0
    sell_count = len(signals[signals['direction'].isin(['SELL', 'BEARISH'])]) if 'direction' in signals.columns else 0

    header_html = f'''
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
        <h3 style="margin:0; color:#C4B5FD; font-family:'Space Grotesk',sans-serif; font-size:0.75rem; font-weight:600; text-transform:uppercase; letter-spacing:0.1em;">
            Tín hiệu giao dịch
        </h3>
        <div style="display:flex; gap:12px;">
            <span style="background:rgba(16,185,129,0.15); color:#10B981; padding:4px 12px; border-radius:20px; font-size:0.7rem; font-weight:600; font-family:'JetBrains Mono',monospace;">
                {buy_count} MUA
            </span>
            <span style="background:rgba(239,68,68,0.15); color:#EF4444; padding:4px 12px; border-radius:20px; font-size:0.7rem; font-weight:600; font-family:'JetBrains Mono',monospace;">
                {sell_count} BÁN
            </span>
        </div>
    </div>
    '''

    # Build formatted table rows with HTML
    table_html = '''
    <div class="scanner-table-wrapper">
    <table class="scanner-table">
    <thead>
        <tr>
            <th>Mã</th>
            <th>Ngày</th>
            <th>Tín hiệu</th>
            <th>Giải thích</th>
            <th>Điểm</th>
            <th>Hành động</th>
        </tr>
    </thead>
    <tbody>
    '''

    for _, row in display_df.iterrows():
        # Symbol
        symbol = row.get('symbol', '-')

        # Date
        signal_date = row.get('date', None)
        if pd.notna(signal_date):
            try:
                if isinstance(signal_date, str):
                    signal_date = pd.to_datetime(signal_date)
                date_str = signal_date.strftime('%d/%m')
            except Exception:
                date_str = '-'
        else:
            date_str = '-'

        # Type label with secondary signals tooltip
        type_label = row.get('type_label', SIGNAL_TYPES.get(row.get('signal_type', ''), '-'))

        # Check for secondary signals (+X tooltip)
        secondary_signals = row.get('secondary_signals', [])
        if secondary_signals and len(secondary_signals) > 0:
            # Build tooltip content
            secondary_list = ', '.join(secondary_signals[:3])  # Max 3 in tooltip
            if len(secondary_signals) > 3:
                secondary_list += f' +{len(secondary_signals) - 3}'
            tooltip_html = f'<span style="cursor:help; margin-left:4px; padding:2px 6px; background:rgba(139,92,246,0.15); color:#A78BFA; border-radius:4px; font-size:0.65rem; font-weight:500;" title="{secondary_list}">+{len(secondary_signals)}</span>'
            type_label = f'{type_label}{tooltip_html}'

        # Get volume context if available
        volume_context = row.get('volume_context', None)
        if pd.isna(volume_context):
            volume_context = None

        # Pattern interpretation with volume context
        interpretation = _get_pattern_interpretation(type_label, volume_context)
        if not interpretation:
            interpretation = '-'

        # Add volume context badge if available
        vol_badge = ''
        if volume_context and volume_context in VOLUME_CONTEXT:
            vol_info = VOLUME_CONTEXT[volume_context]
            vol_badge = f' <span style="background:{vol_info["bg"]}; color:{vol_info["color"]}; padding:2px 6px; border-radius:4px; font-size:0.65rem; font-weight:600; margin-left:4px;">{vol_info["label"]}</span>'

        # Combine interpretation with volume badge
        interpretation_html = f'{interpretation}{vol_badge}' if interpretation != '-' else interpretation

        # Strength/Score as progress bar
        strength = row.get('strength', 0)
        if pd.notna(strength):
            strength_val = strength * 100 if strength <= 1 else strength
            score_html = _render_progress_bar_html(strength_val)
        else:
            score_html = '<span style="color:#64748B;">-</span>'

        # Direction badge
        direction = row.get('direction', 'NEUTRAL')
        action = ACTION_COLORS.get(direction, ACTION_COLORS['NEUTRAL'])

        # Enhanced action badge with refined styling
        if direction in ['BUY', 'BULLISH']:
            badge_style = f'''
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(16, 185, 129, 0.1) 100%);
                color: #10B981;
                border: 1px solid rgba(16, 185, 129, 0.3);
            '''
        elif direction in ['SELL', 'BEARISH']:
            badge_style = f'''
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.1) 100%);
                color: #EF4444;
                border: 1px solid rgba(239, 68, 68, 0.3);
            '''
        else:
            badge_style = f'''
                background: rgba(100, 116, 139, 0.15);
                color: #94A3B8;
                border: 1px solid rgba(100, 116, 139, 0.2);
            '''

        action_badge = f'<span style="{badge_style} padding:6px 14px; border-radius:6px; font-weight:600; font-size:0.75rem; display:inline-block;">{action["label"]}</span>'

        # Row HTML
        table_html += f'''
        <tr>
            <td class="symbol-cell">{symbol}</td>
            <td class="date-cell">{date_str}</td>
            <td class="signal-cell">{type_label}</td>
            <td class="interpretation-cell">{interpretation_html}</td>
            <td class="score-cell">{score_html}</td>
            <td class="action-cell">{action_badge}</td>
        </tr>
        '''

    table_html += '''
    </tbody>
    </table>
    </div>
    '''

    # Custom table styles - Crypto Terminal Glassmorphism (matching dashboard theme)
    table_style = '''
    <style>
    .scanner-table-wrapper {
        background: linear-gradient(180deg, #1A1625 0%, #0F0B1E 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        overflow-x: auto;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        margin: 0.5rem 0 1rem 0;
    }
    .scanner-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'DM Sans', -apple-system, sans-serif;
        font-size: 0.85rem;
    }
    .scanner-table thead tr {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%);
    }
    .scanner-table th {
        color: #8B5CF6;
        font-family: 'DM Sans', -apple-system, sans-serif;
        font-weight: 600;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 14px 16px;
        border-bottom: 2px solid rgba(139, 92, 246, 0.3);
        text-align: left;
        white-space: nowrap;
    }
    .scanner-table tbody tr {
        background: rgba(26, 22, 37, 0.6);
        transition: all 0.2s ease;
    }
    .scanner-table tbody tr:nth-child(even) {
        background: rgba(37, 32, 51, 0.7);
    }
    .scanner-table tbody tr:hover {
        background: rgba(139, 92, 246, 0.12);
    }
    .scanner-table td {
        padding: 12px 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        vertical-align: middle;
        color: #E2E8F0;
    }
    .scanner-table .symbol-cell {
        color: #FFFFFF;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    .scanner-table .date-cell {
        color: #94A3B8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }
    .scanner-table .signal-cell {
        color: #C4B5FD;
        font-weight: 500;
    }
    .scanner-table .interpretation-cell {
        color: #94A3B8;
        font-size: 0.8rem;
        max-width: 300px;
    }
    .scanner-table .score-cell {
        min-width: 140px;
    }
    .scanner-table .action-cell {
        text-align: center;
    }
    .scanner-table tbody tr:hover td {
        color: #F8FAFC;
    }
    .scanner-table tbody tr:hover .symbol-cell {
        color: #A78BFA;
    }
    </style>
    '''

    # Show count
    st.caption(f"Hiển thị {len(display_df)} / {len(signals)} tín hiệu")

    # Render table using st.html() (Streamlit v1.33+)
    st.html(table_style + header_html + table_html)


# ============================================================================
# SINGLE STOCK ANALYSIS COMPONENT
# ============================================================================

# ============================================================================
# FIBONACCI SUPPORT/RESISTANCE CALCULATION
# ============================================================================

@st.cache_data(ttl=3600)
def _calculate_fib_sr_levels(ticker: str) -> dict:
    """
    Calculate Support/Resistance using Fibonacci retracement.

    Method: Swing High/Low 10d + Fib levels from 30d range.

    Returns:
        dict with: swing_high, swing_low, current_price, supports, resistances
    """
    from pathlib import Path

    result = {
        'swing_high': 0,
        'swing_low': 0,
        'current_price': 0,
        'supports': [],
        'resistances': []
    }

    # Use 30d file (2.2MB) instead of full file (20MB) for S/R calculation
    basic_path = Path("DATA/processed/technical/basic_data_30d.parquet")
    if not basic_path.exists():
        # Fallback to full file
        basic_path = Path("DATA/processed/technical/basic_data.parquet")
    if not basic_path.exists():
        return result

    basic_df = pd.read_parquet(basic_path)
    ticker_data = basic_df[basic_df['symbol'] == ticker].sort_values('date', ascending=False)

    if ticker_data.empty or len(ticker_data) < 10:
        return result

    # Swing High/Low from 10 days
    data_10d = ticker_data.head(10)
    swing_high_10d = data_10d['high'].max()
    swing_low_10d = data_10d['low'].min()

    # Fib range from 30 days
    data_30d = ticker_data.head(30)
    fib_high = data_30d['high'].max()
    fib_low = data_30d['low'].min()

    current_price = ticker_data.iloc[0]['close']

    result['swing_high'] = swing_high_10d
    result['swing_low'] = swing_low_10d
    result['current_price'] = current_price

    # Calculate Fib levels from 30d range
    price_range = fib_high - fib_low
    if price_range <= 0:
        return result

    fib_levels = [
        (0.0, 'Low 30d'),
        (0.236, 'Fib 23.6%'),
        (0.382, 'Fib 38.2%'),
        (0.5, 'Fib 50%'),
        (0.618, 'Fib 61.8%'),
        (0.786, 'Fib 78.6%'),
        (1.0, 'High 30d')
    ]

    supports = []
    resistances = []

    # Round swing levels for comparison
    swing_low_rounded = round(swing_low_10d, -2)
    swing_high_rounded = round(swing_high_10d, -2)

    for level, label in fib_levels:
        fib_price = fib_low + (price_range * level)
        fib_price = round(fib_price, -2)  # Round to nearest 100
        pct = ((fib_price / current_price) - 1) * 100

        info = {'price': fib_price, 'label': label, 'pct': pct}

        # Skip if too close to Swing levels (within 1%)
        if swing_low_rounded > 0 and abs(fib_price - swing_low_rounded) / swing_low_rounded < 0.01:
            continue
        if swing_high_rounded > 0 and abs(fib_price - swing_high_rounded) / swing_high_rounded < 0.01:
            continue

        if fib_price < current_price * 0.995:  # Below price (0.5% buffer)
            supports.append(info)
        elif fib_price > current_price * 1.005:  # Above price
            resistances.append(info)

    # Sort: supports descending (nearest first), resistances ascending
    supports.sort(key=lambda x: x['price'], reverse=True)
    resistances.sort(key=lambda x: x['price'])

    result['supports'] = supports[:3]  # Top 3 Fib supports (excl. duplicates with Swing)
    result['resistances'] = resistances[:2]  # Top 2 Fib resistances (excl. duplicates)

    return result


TREND_ICONS = {
    'STRONG_UP': '++',
    'UPTREND': '+',
    'SIDEWAYS': '=',
    'DOWNTREND': '-',
    'STRONG_DOWN': '--',
}

TREND_COLORS = {
    'STRONG_UP': '#10B981',
    'UPTREND': '#22C55E',
    'SIDEWAYS': '#64748B',
    'DOWNTREND': '#F59E0B',
    'STRONG_DOWN': '#EF4444',
}

STRATEGY_RECOMMENDATIONS = {
    ('STRONG_UP', 'BUY'): ('MUA THÊM', 'Trend continuation mạnh'),
    ('STRONG_UP', 'PULLBACK'): ('GIỮ', 'Pullback bình thường, chờ test support'),
    ('UPTREND', 'BUY'): ('MUA', 'Trend following'),
    ('UPTREND', 'PULLBACK'): ('GIỮ', 'Có thể pullback, set stop loss'),
    ('SIDEWAYS', 'BUY'): ('MUA NHẸ', 'Range trading'),
    ('SIDEWAYS', 'SELL'): ('BÁN NHẸ', 'Range trading'),
    ('DOWNTREND', 'SELL'): ('BÁN', 'Trend following'),
    ('DOWNTREND', 'BOUNCE'): ('CHỜ', 'Counter-trend risky'),
    ('STRONG_DOWN', 'SELL'): ('BÁN/SHORT', 'Trend continuation'),
    ('STRONG_DOWN', 'BOUNCE'): ('TRÁNH MUA', 'Counter-trend rất risky'),
}


def _render_single_stock_analysis(signals: pd.DataFrame) -> None:
    """Render Single Stock Analysis component.

    Shows trend + pattern + strategy for individual stocks.
    Linked with Fundamental filter sync for seamless navigation.
    """
    st.markdown("### Phân tích cổ phiếu")

    # Check for synced ticker from Fundamental pages or Scanner selection
    default_ticker = ""
    synced_info = ""

    # Priority: 1) Scanner selection, 2) Fundamental sync
    if st.session_state.get('_pending_sync_ticker'):
        default_ticker = st.session_state._pending_sync_ticker
        synced_info = " (từ Scanner)"
    elif has_synced_ticker():
        default_ticker = get_synced_ticker()
        synced_info = " (từ trang Fundamental)"

    # Input row with sync indicator
    input_col, info_col = st.columns([2, 1])

    with input_col:
        ticker_input = st.text_input(
            "Mã cổ phiếu",
            value=default_ticker if default_ticker else None,
            placeholder="VD: VCB, ACB, FPT",
            key="single_stock_input",
            label_visibility="collapsed",
            help=f"Nhập mã cổ phiếu để xem phân tích{synced_info}"
        )

    with info_col:
        # Get unique tickers with trend data
        if 'trend' in signals.columns:
            available_tickers = signals['symbol'].unique().tolist()
            ticker_count = len(available_tickers)
            if synced_info:
                st.caption(f"{default_ticker}{synced_info}")
            else:
                st.caption(f"{ticker_count} mã có dữ liệu")

    # If user entered a ticker
    if ticker_input and ticker_input.strip():
        ticker = ticker_input.strip().upper()

        # Filter signals for this ticker
        ticker_signals = signals[signals['symbol'] == ticker].copy()

        if ticker_signals.empty:
            st.warning(f"Không có tín hiệu cho {ticker}")
            return

        # Load fresh data directly from basic_data_30d (2.2MB vs 20MB)
        from pathlib import Path
        basic_path = Path("DATA/processed/technical/basic_data_30d.parquet")
        if not basic_path.exists():
            basic_path = Path("DATA/processed/technical/basic_data.parquet")

        sma20, sma50, price, trading_value, expected_value = 0, 0, 0, 0, 0
        trend = 'SIDEWAYS'
        daily_change = 0  # Daily price change %

        # Trading value comparisons
        tv_vs_1w, tv_vs_3w, tv_vs_1m = 0, 0, 0

        if basic_path.exists():
            basic_df = pd.read_parquet(basic_path)
            ticker_basic = basic_df[basic_df['symbol'] == ticker].sort_values('date', ascending=False)

            if not ticker_basic.empty:
                latest_basic = ticker_basic.iloc[0]
                sma20 = latest_basic.get('price_vs_sma20', 0) or 0
                sma50 = latest_basic.get('price_vs_sma50', 0) or 0
                price = latest_basic.get('close', 0) or 0
                trading_value = latest_basic.get('trading_value', 0) or 0

                # Calculate daily change %
                daily_change = 0
                if len(ticker_basic) >= 2:
                    prev_close = ticker_basic.iloc[1].get('close', 0) or 0
                    if prev_close > 0:
                        daily_change = (price / prev_close - 1) * 100

                # Calculate trading value vs periods
                avg_1w = ticker_basic.head(5)['trading_value'].mean()  # 5 days
                avg_3w = ticker_basic.head(15)['trading_value'].mean()  # 15 days
                avg_1m = ticker_basic.head(22)['trading_value'].mean()  # 22 days

                if avg_1w > 0:
                    tv_vs_1w = (trading_value / avg_1w - 1) * 100
                if avg_3w > 0:
                    tv_vs_3w = (trading_value / avg_3w - 1) * 100
                if avg_1m > 0:
                    tv_vs_1m = (trading_value / avg_1m - 1) * 100

                # Classify trend from fresh data
                if sma20 > 5 and sma50 > 5:
                    trend = 'STRONG_UP'
                elif sma20 > 2 and sma50 > 2:
                    trend = 'UPTREND'
                elif sma20 < -5 and sma50 < -5:
                    trend = 'STRONG_DOWN'
                elif sma20 < -2 and sma50 < -2:
                    trend = 'DOWNTREND'
                else:
                    trend = 'SIDEWAYS'

        trend_icon = TREND_ICONS.get(trend, '?')
        trend_color = TREND_COLORS.get(trend, '#64748B')
        trend_label = str(trend).replace('_', ' ')

        # Get recent patterns/signals
        recent_patterns = ticker_signals.sort_values('date', ascending=False).head(5)

        # Calculate Fib S/R levels (Swing 10d + Fib 30d)
        sr_levels = _calculate_fib_sr_levels(ticker)
        supports = sr_levels.get('supports', [])
        resistances = sr_levels.get('resistances', [])

        # Build analysis card HTML
        card_html = f'''
        <div style="
            background: linear-gradient(135deg, rgba({_hex_to_rgb(trend_color)}, 0.15) 0%, rgba(26, 22, 37, 0.95) 100%);
            border: 1px solid rgba({_hex_to_rgb(trend_color)}, 0.4);
            border-radius: 16px;
            padding: 20px 24px;
            margin: 16px 0;
        ">
            <!-- Header: Ticker + Trend -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="
                        color: #FFFFFF;
                        font-size: 1.5rem;
                        font-weight: 700;
                        font-family: 'JetBrains Mono', monospace;
                    ">{ticker}</span>
                    <span style="
                        background: rgba({_hex_to_rgb(trend_color)}, 0.2);
                        color: {trend_color};
                        padding: 6px 14px;
                        border-radius: 20px;
                        font-size: 0.85rem;
                        font-weight: 600;
                    ">{trend_icon} {trend_label}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: #94A3B8; font-size: 0.9rem;">
                        {price:,.0f}đ
                    </span>
                    <span style="
                        color: {'#10B981' if daily_change > 0 else '#EF4444' if daily_change < 0 else '#64748B'};
                        font-size: 0.85rem;
                        font-weight: 600;
                        font-family: monospace;
                    ">({'+' if daily_change > 0 else ''}{daily_change:.2f}%)</span>
                </div>
            </div>

            <!-- SMA & Trading Value Indicators -->
            <div style="
                display: flex;
                gap: 20px;
                padding: 12px 0;
                border-top: 1px solid rgba(255,255,255,0.1);
                border-bottom: 1px solid rgba(255,255,255,0.1);
                margin-bottom: 16px;
                flex-wrap: wrap;
            ">
                <div>
                    <span style="color: #8B5CF6; font-size: 0.7rem; text-transform: uppercase;">SMA20</span>
                    <div style="color: {'#10B981' if sma20 > 0 else '#EF4444'}; font-size: 1rem; font-weight: 600; font-family: monospace;">
                        {'+' if sma20 > 0 else ''}{sma20:.1f}%
                    </div>
                </div>
                <div>
                    <span style="color: #8B5CF6; font-size: 0.7rem; text-transform: uppercase;">SMA50</span>
                    <div style="color: {'#10B981' if sma50 > 0 else '#EF4444'}; font-size: 1rem; font-weight: 600; font-family: monospace;">
                        {'+' if sma50 > 0 else ''}{sma50:.1f}%
                    </div>
                </div>
                <div style="border-left: 1px solid rgba(255,255,255,0.1); padding-left: 20px;">
                    <span style="color: #8B5CF6; font-size: 0.7rem; text-transform: uppercase;">GTGD</span>
                    <div style="color: #C4B5FD; font-size: 1rem; font-weight: 600; font-family: monospace;">
                        {trading_value/1e9:.1f} tỷ
                    </div>
                </div>
                <div>
                    <span style="color: #8B5CF6; font-size: 0.7rem; text-transform: uppercase;">vs 1W</span>
                    <div style="color: {'#10B981' if tv_vs_1w > 0 else '#EF4444' if tv_vs_1w < 0 else '#64748B'}; font-size: 0.9rem; font-weight: 600; font-family: monospace;">
                        {'+' if tv_vs_1w > 0 else ''}{tv_vs_1w:.0f}%
                    </div>
                </div>
                <div>
                    <span style="color: #8B5CF6; font-size: 0.7rem; text-transform: uppercase;">vs 3W</span>
                    <div style="color: {'#10B981' if tv_vs_3w > 0 else '#EF4444' if tv_vs_3w < 0 else '#64748B'}; font-size: 0.9rem; font-weight: 600; font-family: monospace;">
                        {'+' if tv_vs_3w > 0 else ''}{tv_vs_3w:.0f}%
                    </div>
                </div>
                <div>
                    <span style="color: #8B5CF6; font-size: 0.7rem; text-transform: uppercase;">vs 1M</span>
                    <div style="color: {'#10B981' if tv_vs_1m > 0 else '#EF4444' if tv_vs_1m < 0 else '#64748B'}; font-size: 0.9rem; font-weight: 600; font-family: monospace;">
                        {'+' if tv_vs_1m > 0 else ''}{tv_vs_1m:.0f}%
                    </div>
                </div>
            </div>

            <!-- Support/Resistance (Swing + Fib) -->
            <div style="
                display: flex;
                gap: 16px;
                padding: 12px 16px;
                background: rgba(139, 92, 246, 0.08);
                border-radius: 8px;
                margin-bottom: 16px;
            ">
                <div style="flex: 1;">
                    <span style="color: #10B981; font-size: 0.7rem; text-transform: uppercase; display: block; margin-bottom: 6px;">
                        Hỗ trợ
                    </span>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; padding: 2px 0; border-bottom: 1px solid rgba(6, 182, 212, 0.2);">
                        <span style="color: #06B6D4; font-size: 0.8rem; font-weight: 500;">{sr_levels.get('swing_low', 0):,.0f} (Swing Low 10d)</span>
                        <span style="color: #10B981; font-size: 0.8rem; font-family: monospace;">{((sr_levels.get('swing_low', 0) / price - 1) * 100 if price > 0 else 0):+.1f}%</span>
                    </div>
                    {''.join([f'<div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span style="color: #94A3B8; font-size: 0.8rem;">{s["price"]:,.0f} ({s["label"]})</span><span style="color: #10B981; font-size: 0.8rem; font-family: monospace;">{s["pct"]:+.1f}%</span></div>' for s in supports]) if supports else ''}
                </div>
                <div style="width: 1px; background: rgba(255,255,255,0.1);"></div>
                <div style="flex: 1;">
                    <span style="color: #EF4444; font-size: 0.7rem; text-transform: uppercase; display: block; margin-bottom: 6px;">
                        Kháng cự
                    </span>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; padding: 2px 0; border-bottom: 1px solid rgba(6, 182, 212, 0.2);">
                        <span style="color: #06B6D4; font-size: 0.8rem; font-weight: 500;">{sr_levels.get('swing_high', 0):,.0f} (Swing High 10d)</span>
                        <span style="color: #EF4444; font-size: 0.8rem; font-family: monospace;">{((sr_levels.get('swing_high', 0) / price - 1) * 100 if price > 0 else 0):+.1f}%</span>
                    </div>
                    {''.join([f'<div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span style="color: #94A3B8; font-size: 0.8rem;">{r["price"]:,.0f} ({r["label"]})</span><span style="color: #EF4444; font-size: 0.8rem; font-family: monospace;">{r["pct"]:+.1f}%</span></div>' for r in resistances]) if resistances else ''}
                </div>
            </div>

            <!-- Recent Patterns -->
            <div style="margin-bottom: 16px;">
                <span style="color: #8B5CF6; font-size: 0.75rem; text-transform: uppercase; display: block; margin-bottom: 8px;">
                    Mẫu hình gần đây
                </span>
        '''

        # Add pattern rows
        for _, row in recent_patterns.iterrows():
            pattern_date = row.get('date', '')
            if isinstance(pattern_date, str):
                date_str = pattern_date
            else:
                try:
                    date_str = pattern_date.strftime('%d/%m')
                except Exception:
                    date_str = str(pattern_date)[:5]

            pattern_name = row.get('type_label', row.get('pattern_name', '-'))
            direction = row.get('direction', 'NEUTRAL')

            dir_color = {
                'BUY': '#10B981',
                'SELL': '#EF4444',
                'PULLBACK': '#F59E0B',
                'BOUNCE': '#F59E0B',
                'NEUTRAL': '#64748B'
            }.get(direction, '#64748B')

            card_html += f'''
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 6px 0;
                    border-left: 2px solid rgba({_hex_to_rgb(dir_color)}, 0.5);
                    padding-left: 12px;
                    margin-left: 4px;
                ">
                    <span style="color: #64748B; font-size: 0.8rem; min-width: 40px;">{date_str}</span>
                    <span style="color: #C4B5FD; font-size: 0.85rem;">{pattern_name}</span>
                    <span style="color: {dir_color}; font-size: 0.8rem;">→ {direction}</span>
                </div>
            '''

        # Strategy recommendation with S/R context
        latest_direction = recent_patterns.iloc[0].get('direction', 'NEUTRAL') if not recent_patterns.empty else 'NEUTRAL'
        base_strategy = STRATEGY_RECOMMENDATIONS.get((trend, latest_direction), ('THEO DÕI', 'Chờ tín hiệu rõ hơn'))

        # Build enhanced strategy text with S/R context
        strategy_action = base_strategy[0]
        strategy_text = base_strategy[1]

        # Add S/R context to strategy (simple version - just append S/R info)
        if supports and resistances:
            nearest_support = supports[0]
            nearest_resistance = resistances[0]

            # Simple S/R context without changing base strategy logic
            if nearest_resistance['pct'] < 3:  # Near resistance
                strategy_text = f"{base_strategy[1]}. Gần kháng cự {nearest_resistance['price']:,.0f}."
            elif nearest_support['pct'] > -3:  # Near support
                stop_text = f" Stop: {supports[1]['price']:,.0f}" if len(supports) > 1 else ""
                strategy_text = f"{base_strategy[1]}. Hỗ trợ: {nearest_support['price']:,.0f} ({nearest_support['label']}).{stop_text}"
            else:
                strategy_text = f"{base_strategy[1]}. S: {nearest_support['price']:,.0f} | R: {nearest_resistance['price']:,.0f}"

        card_html += f'''
            </div>

            <!-- Strategy -->
            <div style="
                background: rgba(139, 92, 246, 0.1);
                border-radius: 8px;
                padding: 12px 16px;
            ">
                <span style="color: #8B5CF6; font-size: 0.75rem; text-transform: uppercase;">Chiến lược</span>
                <div style="display: flex; align-items: center; gap: 12px; margin-top: 6px;">
                    <span style="
                        color: #FFFFFF;
                        font-weight: 600;
                        font-size: 1rem;
                    ">{strategy_action}</span>
                    <span style="color: #94A3B8; font-size: 0.85rem;">{strategy_text}</span>
                </div>
            </div>
        </div>
        '''

        st.html(card_html)


# ============================================================================
# PATTERN INTERPRETATION GUIDE
# ============================================================================

def _render_pattern_guide(signals: pd.DataFrame) -> None:
    """Render pattern interpretation guide panel."""

    with st.expander("Hướng dẫn giải thích mẫu hình", expanded=False):
        # Get unique patterns from current signals
        patterns = signals['type_label'].unique().tolist() if 'type_label' in signals.columns else []

        if not patterns:
            st.info("Không có mẫu hình nào được phát hiện trong các tín hiệu hiện tại.")
            return

        col1, col2 = st.columns(2)

        # Bullish patterns
        bullish = []
        bearish = []

        for pattern in patterns:
            if any(b in str(pattern).lower() for b in ['bullish', 'hammer', 'morning', 'piercing', 'white', 'up', 'breakout', 'golden']):
                bullish.append(pattern)
            elif any(b in str(pattern).lower() for b in ['bearish', 'evening', 'shooting', 'hanging', 'dark', 'black', 'down', 'breakdown', 'death']):
                bearish.append(pattern)

        with col1:
            st.markdown("**Mẫu hình tăng giá**")
            for pattern in bullish[:5]:
                interp = _get_pattern_interpretation(pattern)
                if interp:
                    st.markdown(f"- **{pattern}**: {interp}")
                else:
                    st.markdown(f"- {pattern}")

        with col2:
            st.markdown("**Mẫu hình giảm giá**")
            for pattern in bearish[:5]:
                interp = _get_pattern_interpretation(pattern)
                if interp:
                    st.markdown(f"- **{pattern}**: {interp}")
                else:
                    st.markdown(f"- {pattern}")


# ============================================================================
# DOWNLOAD BUTTON
# ============================================================================

def _render_download_button(signals: pd.DataFrame) -> None:
    """Render download CSV button."""

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        csv = signals.to_csv(index=False)
        st.download_button(
            label="Tải xuống CSV",
            data=csv,
            file_name=f"tin_hieu_giao_dich_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="download_signals_csv"
        )


# ============================================================================
# MOMENTUM TAB (Buy List from RS Strategy)
# ============================================================================

def _render_momentum_tab(service: 'TADashboardService') -> None:
    """
    Render Momentum tab showing Buy List stocks.

    Buy List = RS Momentum strategy stocks with:
    - High RS Rating (relative strength)
    - Breakout/MA crossover signals
    - Good liquidity
    """
    from pathlib import Path

    # Load buy list
    buy_list_path = Path("DATA/processed/technical/lists/buy_list_latest.parquet")

    if not buy_list_path.exists():
        st.info("Chưa có Buy List. Chạy pipeline hàng ngày để tạo.")
        return

    buy_list = pd.read_parquet(buy_list_path)

    if buy_list.empty:
        st.info("Không có cổ phiếu trong Buy List hôm nay.")
        return

    # ============ SUMMARY METRICS ============
    st.markdown("### 🚀 Momentum - RS Strategy")
    st.caption("Cổ phiếu momentum mạnh dựa trên RS Rating và tín hiệu kỹ thuật")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tổng mã", len(buy_list))
    with col2:
        avg_rs = buy_list['rs_rating'].mean()
        st.metric("RS TB", f"{avg_rs:.0f}")
    with col3:
        avg_score = buy_list['score'].mean()
        st.metric("Điểm TB", f"{avg_score:.1f}")
    with col4:
        top_sector = buy_list['sector_code'].mode().iloc[0] if not buy_list.empty else "N/A"
        st.metric("Ngành mạnh", top_sector)

    st.markdown("---")

    # ============ BUY LIST TABLE ============
    st.markdown("### Danh sách mua khuyến nghị")

    # Sort by score descending
    buy_list = buy_list.sort_values('score', ascending=False)

    # Build HTML table
    table_html = '''
    <div style="
        background: linear-gradient(135deg, rgba(26, 22, 37, 0.95) 0%, rgba(16, 12, 26, 0.98) 100%);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 12px;
        overflow: hidden;
    ">
    <table style="width: 100%; border-collapse: collapse;">
    <thead>
        <tr style="background: rgba(16, 185, 129, 0.15);">
            <th style="padding: 12px; text-align: left; color: #10B981; font-size: 0.75rem; font-weight: 600;">MÃ</th>
            <th style="padding: 12px; text-align: center; color: #10B981; font-size: 0.75rem; font-weight: 600;">NGÀNH</th>
            <th style="padding: 12px; text-align: center; color: #10B981; font-size: 0.75rem; font-weight: 600;">RS</th>
            <th style="padding: 12px; text-align: right; color: #10B981; font-size: 0.75rem; font-weight: 600;">ĐIỂM</th>
            <th style="padding: 12px; text-align: right; color: #10B981; font-size: 0.75rem; font-weight: 600;">GIÁ VÀO</th>
            <th style="padding: 12px; text-align: right; color: #10B981; font-size: 0.75rem; font-weight: 600;">CẮT LỖ</th>
            <th style="padding: 12px; text-align: right; color: #10B981; font-size: 0.75rem; font-weight: 600;">MỤC TIÊU</th>
        </tr>
    </thead>
    <tbody>
    '''

    for _, row in buy_list.iterrows():
        symbol = row.get('symbol', '-')
        sector = row.get('sector_code', '-')
        rs = row.get('rs_rating', 0)
        score = row.get('score', 0)
        entry = row.get('entry_price', 0)
        stop_loss = row.get('stop_loss', 0)
        target = row.get('target_1', 0)

        # RS color
        if rs >= 90:
            rs_color = '#10B981'  # Green
        elif rs >= 80:
            rs_color = '#34D399'
        elif rs >= 70:
            rs_color = '#FCD34D'  # Yellow
        else:
            rs_color = '#94A3B8'

        # Score bar
        score_pct = min(100, score)

        row_html = f'''
        <tr style="background: rgba(26, 22, 37, 0.6); border-bottom: 1px solid rgba(255,255,255,0.05);">
            <td style="padding: 10px 12px; color: #FFFFFF; font-weight: 700; font-family: monospace; font-size: 0.9rem;">
                {symbol}
            </td>
            <td style="padding: 10px 12px; text-align: center;">
                <span style="background: rgba(139, 92, 246, 0.2); color: #C4B5FD; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem;">
                    {sector}
                </span>
            </td>
            <td style="padding: 10px 12px; text-align: center;">
                <span style="color: {rs_color}; font-weight: 700; font-size: 0.9rem;">{rs:.0f}</span>
            </td>
            <td style="padding: 10px 12px;">
                <div style="display: flex; align-items: center; gap: 8px; justify-content: flex-end;">
                    <div style="flex: 1; max-width: 60px; height: 6px; background: rgba(100,116,139,0.2); border-radius: 3px; overflow: hidden;">
                        <div style="width: {score_pct}%; height: 100%; background: linear-gradient(90deg, #10B981, #34D399); border-radius: 3px;"></div>
                    </div>
                    <span style="color: #10B981; font-weight: 700; font-size: 0.85rem; font-family: monospace;">
                        {score:.1f}
                    </span>
                </div>
            </td>
            <td style="padding: 10px 12px; text-align: right; color: #E2E8F0; font-family: monospace; font-size: 0.85rem;">
                {entry:,.0f}
            </td>
            <td style="padding: 10px 12px; text-align: right; color: #EF4444; font-family: monospace; font-size: 0.85rem;">
                {stop_loss:,.0f}
            </td>
            <td style="padding: 10px 12px; text-align: right; color: #10B981; font-family: monospace; font-size: 0.85rem;">
                {target:,.0f}
            </td>
        </tr>
        '''
        table_html += row_html

    table_html += '</tbody></table></div>'
    st.html(table_html)

    # ============ LEGEND ============
    with st.expander("📖 Giải thích", expanded=False):
        st.markdown("""
        **RS Rating (Relative Strength):**
        - 90+ : Momentum cực mạnh, dẫn đầu thị trường
        - 80-89: Momentum mạnh
        - 70-79: Momentum khá

        **Điểm (Score):**
        - Tổng hợp RS Rating + Breakout + MA Crossover + Volume

        **Giá vào / Cắt lỗ / Mục tiêu:**
        - Entry: Giá hiện tại
        - Stop Loss: -7% (quản trị rủi ro)
        - Target 1: +10% (chốt lời đầu)
        """)


# ============================================================================
# EMPTY STATE
# ============================================================================

def _render_empty_state() -> None:
    """Render empty state when no signals available."""

    st.warning("Không có tín hiệu giao dịch")

    st.markdown("""
    Chạy pipeline phân tích kỹ thuật hàng ngày để tạo tín hiệu giao dịch:

    ```bash
    python3 PROCESSORS/pipelines/daily/daily_ta_complete.py
    ```
    """)
