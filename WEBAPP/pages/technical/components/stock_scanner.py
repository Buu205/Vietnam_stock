"""
Stock Scanner Component - Tab 3
===============================

Comprehensive signal scanner with pattern recognition.
Design: Crypto Terminal Glassmorphism - unified with dashboard theme

Layout (from plan phase-04):
- Quick Filters: Symbol search, Sector dropdown
- Advanced Filters: Signal Type, Direction, Min Strength
- Signal Summary: KPI metrics (st.metric)
- Signal Table: Styled HTML table with:
  - Progress bar gauge for score
  - Pattern interpretation text (Vietnamese with diacritics)
  - Volume context indicators
  - Signal date

Author: Claude Code
Date: 2025-12-27
"""

import streamlit as st
import pandas as pd
from typing import TYPE_CHECKING, Optional
from datetime import datetime, timedelta

from WEBAPP.core.styles import get_table_style

if TYPE_CHECKING:
    from ..services.ta_dashboard_service import TADashboardService


# ============================================================================
# CONSTANTS - Pattern Interpretation & Volume Context
# ============================================================================

# Signal Type Labels
SIGNAL_TYPES = {
    'patterns': 'Candlestick',
    'ma_crossover': 'MA Cross',
    'volume_spike': 'Volume Spike',
    'breakout': 'Breakout',
}

# Pattern Interpretations (Vietnamese with diacritics) - lowercase keys for matching
# Based on ta-lib candlestick patterns from phase-04 plan
PATTERN_INTERPRETATIONS = {
    # ============ BULLISH PATTERNS ============
    'engulfing': 'Đảo chiều mạnh - Nến xanh bao trùm hoàn toàn nến đỏ trước.',
    'bullish engulfing': 'Đảo chiều cực mạnh - Buyers áp đảo, nến xanh lớn bao trùm nến đỏ.',
    'hammer': 'Từ chối giảm giá - Bấc dưới dài >= 2x thân. Buyers vào ở đáy.',
    'morning star': 'Mô hình 3 nến đảo chiều hoàn hảo: (1) Nến đỏ dài, (2) Doji, (3) Nến xanh dài. High conviction.',
    'morning doji star': 'Mô hình 3 nến đảo chiều với Doji ở giữa. Tín hiệu mạnh.',
    'piercing': 'Mô hình xuyên thấu - Nến xanh xuyên thấu >50% thân nến đỏ trước.',
    'three white soldiers': '3 nến xanh liên tiếp tăng dần - Đảo chiều tăng cực mạnh, trend reversal.',
    'inverted hammer': 'Bấc trên dài, thân nhỏ. Cần confirm bằng nến tăng tiếp theo.',
    'inverted_hammer': 'Bấc trên dài, thân nhỏ. Cần confirm bằng nến tăng tiếp theo.',
    'harami': 'Nến nhỏ nằm trong thân nến lớn. Momentum yếu đi, cần theo dõi.',
    'harami bullish': 'Harami tăng - Nến xanh nhỏ trong nến đỏ. Momentum giảm đang yếu đi.',
    'harami_bullish': 'Harami tăng - Nến xanh nhỏ trong nến đỏ. Momentum giảm đang yếu đi.',
    'doji': 'Thị trường bất định - Open = Close. Chờ nến tiếp theo xác nhận.',
    'dragonfly doji': 'Từ chối giảm giá mạnh - Bấc dưới cực dài, Open = High = Close.',
    'dragonfly_doji': 'Từ chối giảm giá mạnh - Bấc dưới cực dài, Open = High = Close.',
    'marubozu': 'Nến không bấc - Buyers control 100%. Momentum tăng mạnh.',
    'marubozu white': 'Marubozu xanh - Buyers hoàn toàn thống trị phiên.',
    'marubozu_white': 'Marubozu xanh - Buyers hoàn toàn thống trị phiên.',
    'tweezer bottom': 'Đáy nhíp - 2 nến liên tiếp có low bằng nhau. Support mạnh.',
    'tweezer_bottom': 'Đáy nhíp - 2 nến liên tiếp có low bằng nhau. Support mạnh.',

    # ============ BEARISH PATTERNS ============
    'bearish engulfing': 'Đảo chiều giảm mạnh - Nến đỏ bao trùm hoàn toàn nến xanh.',
    'engulfing bearish': 'Đảo chiều giảm mạnh - Sellers áp đảo, nến đỏ lớn bao trùm.',
    'engulfing_bearish': 'Đảo chiều giảm mạnh - Sellers áp đảo, nến đỏ lớn bao trùm.',
    'hanging man': 'Cảnh báo đảo chiều giảm sau uptrend. Giống Hammer nhưng ở đỉnh.',
    'hanging_man': 'Cảnh báo đảo chiều giảm sau uptrend. Giống Hammer nhưng ở đỉnh.',
    'evening star': 'Mô hình 3 nến đảo chiều giảm: (1) Nến xanh, (2) Doji, (3) Nến đỏ dài. High conviction.',
    'evening doji star': 'Mô hình 3 nến đảo chiều giảm với Doji ở giữa.',
    'shooting star': 'Từ chối tăng giá - Bấc trên dài, thân nhỏ ở dưới. Sellers vào.',
    'shooting_star': 'Từ chối tăng giá - Bấc trên dài, thân nhỏ ở dưới. Sellers vào.',
    'dark cloud cover': 'Mây đen che phủ - Nến đỏ mở gap lên, đóng cửa <50% nến xanh trước.',
    'dark_cloud_cover': 'Mây đen che phủ - Nến đỏ mở gap lên, đóng cửa <50% nến xanh trước.',
    'dark cloud': 'Mây đen che phủ - Áp lực bán tăng sau gap up.',
    'three black crows': '3 nến đỏ liên tiếp giảm dần - Đảo chiều giảm cực mạnh.',
    'three_black_crows': '3 nến đỏ liên tiếp giảm dần - Đảo chiều giảm cực mạnh.',
    'harami bearish': 'Harami giảm - Nến đỏ nhỏ trong nến xanh. Momentum tăng yếu đi.',
    'harami_bearish': 'Harami giảm - Nến đỏ nhỏ trong nến xanh. Momentum tăng yếu đi.',
    'gravestone doji': 'Từ chối tăng giá mạnh - Bấc trên cực dài, Open = Low = Close.',
    'gravestone_doji': 'Từ chối tăng giá mạnh - Bấc trên cực dài, Open = Low = Close.',
    'marubozu black': 'Marubozu đỏ - Sellers hoàn toàn thống trị phiên.',
    'marubozu_black': 'Marubozu đỏ - Sellers hoàn toàn thống trị phiên.',
    'tweezer top': 'Đỉnh nhíp - 2 nến liên tiếp có high bằng nhau. Resistance mạnh.',
    'tweezer_top': 'Đỉnh nhíp - 2 nến liên tiếp có high bằng nhau. Resistance mạnh.',

    # ============ CHART PATTERNS ============
    'double bottom': 'Đáy đôi - Mô hình đảo chiều tăng cổ điển. Breakout neckline xác nhận.',
    'double_bottom': 'Đáy đôi - Mô hình đảo chiều tăng cổ điển. Breakout neckline xác nhận.',
    'double top': 'Đỉnh đôi - Mô hình đảo chiều giảm cổ điển. Breakdown neckline xác nhận.',
    'double_top': 'Đỉnh đôi - Mô hình đảo chiều giảm cổ điển. Breakdown neckline xác nhận.',
    'head shoulders': 'Vai-Đầu-Vai - Mô hình đảo chiều giảm. Breakdown neckline = confirm.',
    'head_shoulders': 'Vai-Đầu-Vai - Mô hình đảo chiều giảm. Breakdown neckline = confirm.',
    'cup handle': 'Tách và tay cầm - Mô hình tiếp diễn tăng. Breakout rim = confirm.',
    'cup_handle': 'Tách và tay cầm - Mô hình tiếp diễn tăng. Breakout rim = confirm.',
    'flag bull': 'Cờ tăng - Tiếp diễn sau sóng tăng mạnh. Breakout = tiếp tục tăng.',
    'flag_bull': 'Cờ tăng - Tiếp diễn sau sóng tăng mạnh. Breakout = tiếp tục tăng.',
    'flag bear': 'Cờ giảm - Tiếp diễn sau sóng giảm mạnh. Breakdown = tiếp tục giảm.',
    'flag_bear': 'Cờ giảm - Tiếp diễn sau sóng giảm mạnh. Breakdown = tiếp tục giảm.',

    # ============ MA SIGNALS ============
    'ma cross up': 'Golden Cross - EMA ngắn cắt lên EMA dài. Xu hướng tăng mới bắt đầu.',
    'ma cross down': 'Death Cross - EMA ngắn cắt xuống EMA dài. Xu hướng giảm.',
    'ma_crossover': 'MA Crossover - Giao cắt đường trung bình động.',
    'golden cross': 'Golden Cross - EMA20 cắt lên EMA50. Xu hướng tăng trung hạn.',
    'death cross': 'Death Cross - EMA20 cắt xuống EMA50. Xu hướng giảm trung hạn.',

    # ============ VOLUME SIGNALS ============
    'vol spike': 'Volume đột biến - Sức mua/bán bất thường, cần theo dõi giá.',
    'volume spike': 'Volume tăng đột biến - Có thể báo hiệu breakout hoặc climax.',
    'volume_spike': 'Volume tăng đột biến - Có thể báo hiệu breakout hoặc climax.',

    # ============ BREAKOUT SIGNALS ============
    'breakout': 'Phá vỡ resistance - Xu hướng tăng mới. Volume cao xác nhận.',
    'breakdown': 'Phá vỡ support - Xu hướng giảm. Volume cao xác nhận.',
    'resistance break': 'Vượt resistance - Giá đóng cửa trên vùng kháng cự.',
    'support break': 'Xuyên support - Giá đóng cửa dưới vùng hỗ trợ.',
}

# Volume Context Interpretation Matrix (pattern + volume)
PATTERN_VOLUME_MATRIX = {
    # ENGULFING patterns
    ('engulfing', 'HIGH'): 'Đảo chiều cực mạnh - Volume cao xác nhận buyers áp đảo',
    ('engulfing', 'AVG'): 'Đảo chiều - Cần theo dõi phiên sau',
    ('engulfing', 'LOW'): 'Tín hiệu yếu - Chờ volume confirmation',

    # HAMMER patterns
    ('hammer', 'HIGH'): 'Từ chối giảm giá mạnh - Volume cao = buyers vào mạnh ở đáy',
    ('hammer', 'AVG'): 'Có thể đảo chiều - Volume chưa confirm',
    ('hammer', 'LOW'): 'Hammer yếu - Có thể chỉ là nghỉ ngơi tạm thời',

    # MORNING STAR patterns
    ('morning star', 'HIGH'): 'Đảo chiều cực mạnh - Volume đáy cao xác nhận',
    ('morning star', 'AVG'): 'Đảo chiều tốt - Chờ thêm 1 phiên confirm',
    ('morning star', 'LOW'): 'Cẩn thận - Volume thấp giảm độ tin cậy',

    # SHOOTING STAR patterns
    ('shooting star', 'HIGH'): 'Từ chối tăng giá mạnh - Volume cao xác nhận sellers',
    ('shooting star', 'AVG'): 'Có thể đảo chiều - Theo dõi phiên sau',
    ('shooting star', 'LOW'): 'Shooting Star yếu - Cần confirm',

    # DOJI patterns
    ('doji', 'HIGH'): 'Bất định nhưng vol cao - Có thể là climax, chờ confirm',
    ('doji', 'AVG'): 'Bất định - Thị trường do dự',
    ('doji', 'LOW'): 'Bất định vol thấp - Không có tín hiệu rõ ràng',
}

# Volume Context Labels
VOLUME_CONTEXT = {
    'HIGH': {'label': 'VOL CAO', 'color': '#10B981', 'bg': 'rgba(16, 185, 129, 0.15)'},
    'AVG': {'label': 'VOL TB', 'color': '#F59E0B', 'bg': 'rgba(245, 158, 11, 0.15)'},
    'LOW': {'label': 'VOL THẤP', 'color': '#64748B', 'bg': 'rgba(100, 116, 139, 0.15)'},
}

# Action colors (matching dashboard theme)
ACTION_COLORS = {
    'BUY': {'bg': 'rgba(16, 185, 129, 0.15)', 'text': '#10B981', 'label': 'MUA'},
    'SELL': {'bg': 'rgba(239, 68, 68, 0.15)', 'text': '#EF4444', 'label': 'BÁN'},
    'HOLD': {'bg': 'rgba(245, 158, 11, 0.15)', 'text': '#F59E0B', 'label': 'CHỜ'},
    'NEUTRAL': {'bg': 'rgba(100, 116, 139, 0.15)', 'text': '#64748B', 'label': 'TRUNG LẬP'},
    'BULLISH': {'bg': 'rgba(16, 185, 129, 0.15)', 'text': '#10B981', 'label': 'MUA'},
    'BEARISH': {'bg': 'rgba(239, 68, 68, 0.15)', 'text': '#EF4444', 'label': 'BÁN'},
}


# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render_stock_scanner(service: 'TADashboardService') -> None:
    """
    Render Stock Scanner tab following dashboard conventions.

    Components:
    1. Quick Filters (symbol search, sector, days filter)
    2. Advanced Filters (signal type, direction, min strength)
    3. Signal Summary (st.metric cards)
    4. Signal Table with:
       - Progress bar gauge for score
       - Pattern interpretation (Vietnamese with diacritics)
       - Volume context
       - Signal date
    5. Pattern Interpretation Guide panel
    """

    # Load signals data
    signals = service.get_signals()

    if signals is None or signals.empty:
        _render_empty_state()
        return

    # ============ QUICK FILTERS ============
    st.markdown("### Bộ lọc nhanh")

    qcol1, qcol2, qcol3 = st.columns([2, 1, 1])

    with qcol1:
        search_symbols = st.text_input(
            "Tìm mã",
            placeholder="VCB, ACB, FPT (phân tách bằng dấu phẩy)",
            key="scanner_quick_search",
            label_visibility="collapsed"
        )

    with qcol2:
        sectors = service.get_sector_list()
        sector_options = ["Tất cả ngành"] + sectors
        selected_sector = st.selectbox(
            "Ngành",
            sector_options,
            key="scanner_sector",
            label_visibility="collapsed"
        )

    with qcol3:
        days_options = {1: "Hôm nay", 2: "2 ngày gần nhất", 5: "5 ngày", 10: "10 ngày"}
        selected_days = st.selectbox(
            "Thời gian",
            options=list(days_options.keys()),
            format_func=lambda x: days_options[x],
            index=1,  # Default: 2 ngày gần nhất
            key="scanner_days",
            label_visibility="collapsed"
        )

    # ============ ADVANCED FILTERS ============
    with st.expander("Bộ lọc nâng cao", expanded=False):
        fcol1, fcol2, fcol3 = st.columns(3)

        with fcol1:
            type_options = ['Tất cả'] + list(signals['signal_type'].unique()) if 'signal_type' in signals.columns else ['Tất cả']
            selected_type = st.selectbox(
                "Loại tín hiệu",
                type_options,
                format_func=lambda x: 'Tất cả loại' if x == 'Tất cả' else SIGNAL_TYPES.get(x, x.replace('_', ' ').title()),
                key="scanner_type"
            )

        with fcol2:
            direction_options = ['Tất cả', 'BUY', 'SELL', 'NEUTRAL']
            selected_direction = st.selectbox(
                "Hướng",
                direction_options,
                format_func=lambda x: {'Tất cả': 'Tất cả', 'BUY': 'MUA', 'SELL': 'BÁN', 'NEUTRAL': 'TRUNG LẬP'}.get(x, x),
                key="scanner_direction"
            )

        with fcol3:
            min_strength = st.slider(
                "Điểm tối thiểu",
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
        selected_type if selected_type != 'Tất cả' else None,
        selected_direction if selected_direction != 'Tất cả' else None,
        min_strength,
        selected_days
    )

    st.markdown("---")

    # ============ SIGNAL SUMMARY (st.metric - dashboard standard) ============
    _render_signal_summary(filtered)

    st.markdown("---")

    # ============ SIGNAL TABLE with Progress Bar & Interpretation ============
    _render_signal_table_enhanced(filtered)

    # ============ PATTERN INTERPRETATION GUIDE ============
    if not filtered.empty:
        st.markdown("---")
        _render_pattern_guide(filtered)

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
    min_strength: int,
    days: int = 2
) -> pd.DataFrame:
    """Apply all filters to signals dataframe."""

    filtered = df.copy()

    # Filter by days (recent signals only)
    if 'date' in filtered.columns:
        try:
            filtered['date'] = pd.to_datetime(filtered['date'])
            # Normalize cutoff to start of day for comparison
            cutoff_date = pd.Timestamp(datetime.now().date()) - pd.Timedelta(days=days)
            filtered = filtered[filtered['date'] >= cutoff_date]
        except Exception:
            pass  # If date parsing fails, skip date filter

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

    # Direction filter
    if direction and 'direction' in filtered.columns:
        filtered = filtered[filtered['direction'] == direction]

    # Strength filter
    if min_strength > 0 and 'strength' in filtered.columns:
        strength_col = filtered['strength']
        if strength_col.max() <= 1:
            strength_col = strength_col * 100
        filtered = filtered[strength_col >= min_strength]

    # Sort by date (newest first) then by strength
    if 'date' in filtered.columns:
        filtered = filtered.sort_values(['date', 'strength'], ascending=[False, False])

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

        # Type label
        type_label = row.get('type_label', SIGNAL_TYPES.get(row.get('signal_type', ''), '-'))

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
