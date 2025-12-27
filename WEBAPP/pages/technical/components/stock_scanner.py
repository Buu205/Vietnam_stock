"""
Stock Scanner Component - Tab 3
===============================

Comprehensive signal scanner with pattern recognition.
Design: Crypto Terminal Dark Mode (OLED optimized)

Layout (from plan phase-04):
- Quick Filters: Symbol search, Sector dropdown
- Advanced Filters: Signal Type, Pattern, Volume
- Signal Table: Compact with interpretation
- Summary: BUY/SELL/HOLD counts

Author: Claude Code
Date: 2025-12-27
Updated: Follow phase-04-scanner-lists-tabs.md plan
"""

import streamlit as st
import pandas as pd
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

from WEBAPP.core.styles import render_styled_table

if TYPE_CHECKING:
    from ..services.ta_dashboard_service import TADashboardService


# ============================================================================
# CONSTANTS - Following UI/UX Pro Max Guidelines
# ============================================================================

# Colors (Financial Dashboard palette)
COLORS = {
    'buy': '#10B981',       # Green - profit
    'sell': '#EF4444',      # Red - loss
    'hold': '#F59E0B',      # Amber - warning
    'neutral': '#64748B',   # Gray
    'purple': '#8B5CF6',    # Accent
    'cyan': '#06B6D4',      # Secondary
    'text': '#E2E8F0',      # Primary text
    'muted': '#94A3B8',     # Secondary text
    'bg_card': 'rgba(37, 32, 51, 0.6)',
}

# Signal Type Labels & Emoji (NO SVG - lesson learned)
SIGNAL_TYPES = {
    'patterns': {'label': 'Candlestick', 'emoji': '🕯️'},
    'ma_crossover': {'label': 'MA Cross', 'emoji': '📈'},
    'volume_spike': {'label': 'Volume', 'emoji': '📊'},
    'breakout': {'label': 'Breakout', 'emoji': '🚀'},
}

# Action Labels
ACTION_LABELS = {
    'BUY': {'label': 'MUA', 'emoji': '🟢', 'color': COLORS['buy']},
    'SELL': {'label': 'BÁN', 'emoji': '🔴', 'color': COLORS['sell']},
    'HOLD': {'label': 'CHỜ', 'emoji': '🟡', 'color': COLORS['hold']},
    'NEUTRAL': {'label': 'NEUTRAL', 'emoji': '⚪', 'color': COLORS['neutral']},
}


# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render_stock_scanner(service: 'TADashboardService') -> None:
    """
    Render Stock Scanner tab following phase-04 plan.

    Components:
    1. Quick Filters (symbol search, sector)
    2. Advanced Filters (signal type, direction)
    3. Signal Summary Cards
    4. Signal Table with styled HTML
    """

    # Load signals data
    signals = service.get_signals()

    if signals is None or signals.empty:
        _render_empty_state()
        return

    # ============ QUICK FILTERS ============
    st.markdown("#### 🔍 Quick Filters")

    qcol1, qcol2 = st.columns([2, 1])

    with qcol1:
        search_symbols = st.text_input(
            "Nhập mã cổ phiếu",
            placeholder="VCB, ACB, FPT (phân cách bằng dấu phẩy)",
            key="scanner_quick_search",
            label_visibility="collapsed"
        )

    with qcol2:
        sectors = service.get_sector_list()
        sector_options = ["Tất cả ngành"] + sectors
        selected_sector = st.selectbox(
            "Sector",
            sector_options,
            key="scanner_sector",
            label_visibility="collapsed"
        )

    # ============ ADVANCED FILTERS ============
    with st.expander("⚙️ Advanced Filters", expanded=False):
        fcol1, fcol2, fcol3 = st.columns(3)

        with fcol1:
            # Signal Type filter
            type_options = ['All'] + list(signals['signal_type'].unique()) if 'signal_type' in signals.columns else ['All']
            selected_type = st.selectbox(
                "Signal Type",
                type_options,
                format_func=lambda x: 'All Types' if x == 'All' else SIGNAL_TYPES.get(x, {}).get('label', x.replace('_', ' ').title()),
                key="scanner_type"
            )

        with fcol2:
            # Direction filter
            direction_options = ['All', 'BUY', 'SELL', 'NEUTRAL']
            selected_direction = st.selectbox(
                "Direction",
                direction_options,
                format_func=lambda x: ACTION_LABELS.get(x, {}).get('emoji', '') + ' ' + x if x != 'All' else 'All Signals',
                key="scanner_direction"
            )

        with fcol3:
            # Min strength filter
            min_strength = st.slider(
                "Min Strength",
                min_value=0,
                max_value=100,
                value=0,
                key="scanner_min_strength"
            )

    # ============ APPLY FILTERS ============
    filtered = _apply_filters(
        signals,
        search_symbols,
        selected_sector if selected_sector != "Tất cả ngành" else None,
        selected_type if selected_type != 'All' else None,
        selected_direction if selected_direction != 'All' else None,
        min_strength
    )

    st.markdown("---")

    # ============ SIGNAL SUMMARY ============
    _render_signal_summary(filtered)

    st.markdown("---")

    # ============ SIGNAL TABLE ============
    st.markdown("#### 📋 Trading Signals")
    _render_signal_table(filtered)

    # ============ DOWNLOAD ============
    if not filtered.empty:
        _render_download_button(filtered)


# ============================================================================
# FILTER LOGIC
# ============================================================================

def _apply_filters(
    df: pd.DataFrame,
    symbols_str: Optional[str],
    sector: Optional[str],
    signal_type: Optional[str],
    direction: Optional[str],
    min_strength: int
) -> pd.DataFrame:
    """Apply all filters to signals dataframe."""

    filtered = df.copy()

    # Symbol search
    if symbols_str and symbols_str.strip():
        symbols = [s.strip().upper() for s in symbols_str.split(',')]
        filtered = filtered[filtered['symbol'].isin(symbols)]

    # Sector filter (if sector_code column exists)
    if sector and 'sector_code' in filtered.columns:
        filtered = filtered[filtered['sector_code'] == sector]

    # Signal type filter
    if signal_type and 'signal_type' in filtered.columns:
        filtered = filtered[filtered['signal_type'] == signal_type]

    # Direction filter
    if direction and 'direction' in filtered.columns:
        filtered = filtered[filtered['direction'] == direction]

    # Strength filter
    if min_strength > 0 and 'strength' in filtered.columns:
        # Convert to 0-100 scale if needed
        strength_col = filtered['strength']
        if strength_col.max() <= 1:
            strength_col = strength_col * 100
        filtered = filtered[strength_col >= min_strength]

    return filtered


# ============================================================================
# SUMMARY CARDS (Using st.columns - NO complex HTML)
# ============================================================================

def _render_signal_summary(signals: pd.DataFrame) -> None:
    """Render signal summary using native Streamlit components."""

    # Count by direction
    if 'direction' not in signals.columns:
        return

    direction_counts = signals['direction'].value_counts()

    total = len(signals)
    buy_count = direction_counts.get('BUY', 0) + direction_counts.get('BULLISH', 0)
    sell_count = direction_counts.get('SELL', 0) + direction_counts.get('BEARISH', 0)
    hold_count = direction_counts.get('HOLD', 0) + direction_counts.get('NEUTRAL', 0)

    # Summary row using st.columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Signals",
            value=total,
            delta=None
        )

    with col2:
        st.metric(
            label="🟢 MUA",
            value=buy_count,
            delta=f"{buy_count/total*100:.0f}%" if total > 0 else "0%"
        )

    with col3:
        st.metric(
            label="🔴 BÁN",
            value=sell_count,
            delta=f"{sell_count/total*100:.0f}%" if total > 0 else "0%",
            delta_color="inverse"
        )

    with col4:
        st.metric(
            label="🟡 CHỜ",
            value=hold_count,
            delta=None
        )

    # Signal type breakdown using columns (NO complex HTML)
    if 'signal_type' in signals.columns:
        type_counts = signals['signal_type'].value_counts()
        if not type_counts.empty:
            st.markdown("**Signal Types:**")
            type_cols = st.columns(len(type_counts))
            for i, (sig_type, count) in enumerate(type_counts.items()):
                info = SIGNAL_TYPES.get(sig_type, {'emoji': '📌', 'label': sig_type})
                with type_cols[i]:
                    st.markdown(f"{info['emoji']} **{info['label']}**: `{count}`")


# ============================================================================
# SIGNAL TABLE (Using render_styled_table - lesson learned)
# ============================================================================

def _render_signal_table(signals: pd.DataFrame) -> None:
    """Render signals table using styled HTML (NOT st.dataframe)."""

    if signals.empty:
        st.info("No signals match your filters")
        return

    # Prepare display data
    display_df = signals.head(100).copy()

    # Build formatted table data
    table_rows = []
    for _, row in display_df.iterrows():
        # Symbol
        symbol = row.get('symbol', '-')

        # Type with emoji
        sig_type = row.get('signal_type', '')
        type_info = SIGNAL_TYPES.get(sig_type, {'emoji': '📌', 'label': sig_type})
        type_label = row.get('type_label', type_info['label'])
        type_display = f"{type_info['emoji']} {type_label}"

        # Direction with colored badge
        direction = row.get('direction', 'NEUTRAL')
        action_info = ACTION_LABELS.get(direction, ACTION_LABELS['NEUTRAL'])
        direction_display = f"{action_info['emoji']} {action_info['label']}"

        # Price
        price = row.get('price', 0)
        price_display = f"{price:,.0f}" if pd.notna(price) and price > 0 else "-"

        # Strength as simple text (NO complex HTML progress bars)
        strength = row.get('strength', 0)
        if pd.notna(strength):
            strength_val = strength * 100 if strength <= 1 else strength
            strength_display = f"{strength_val:.0f}%"
        else:
            strength_display = "-"

        table_rows.append({
            'Symbol': symbol,
            'Type': type_display,
            'Signal': direction_display,
            'Price': price_display,
            'Strength': strength_display
        })

    # Create DataFrame and render
    table_df = pd.DataFrame(table_rows)

    # Show count
    st.caption(f"Showing {len(table_df)} of {len(signals)} signals")

    # Use render_styled_table (lesson learned - NOT st.dataframe)
    html_table = render_styled_table(table_df, highlight_first_col=True)
    st.markdown(html_table, unsafe_allow_html=True)


# ============================================================================
# DOWNLOAD BUTTON
# ============================================================================

def _render_download_button(signals: pd.DataFrame) -> None:
    """Render download CSV button."""

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        csv = signals.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"trading_signals_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_signals_csv"
        )


# ============================================================================
# EMPTY STATE
# ============================================================================

def _render_empty_state() -> None:
    """Render empty state when no signals available."""

    st.warning("No Trading Signals Available")

    st.markdown("""
    Run the daily technical analysis pipeline to generate trading signals:

    ```bash
    python3 PROCESSORS/pipelines/daily/daily_ta_complete.py
    ```
    """)
