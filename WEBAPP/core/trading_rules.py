"""
Trading Rules - Signal Matrix & State Machines
===============================================

All trading signals, regimes, and state machine definitions.
Separated from UI components for maintainability.

Usage:
    from WEBAPP.core.trading_rules import (
        SIGNAL_MATRIX, BOTTOM_STAGES,
        REGIME_STYLES, SIGNAL_STYLES
    )

Author: Claude Code
Created: 2026-01-02
"""

from .trading_constants import (
    OVERBOUGHT_THRESHOLD,
    OVERSOLD_THRESHOLD,
    TREND_CONFIRMATION_THRESHOLD,
    STRONG_BUY_THRESHOLD,
    BUY_THRESHOLD,
    WARNING_THRESHOLD,
    SELL_THRESHOLD,
    DANGER_MA50_THRESHOLD,
)

# =============================================================================
# REGIME STYLES
# =============================================================================

REGIME_STYLES = {
    'BULLISH': {
        'color': '#10B981',
        'bg': 'rgba(16, 185, 129, 0.15)',
        'border': '#10B981',
    },
    'BEARISH': {
        'color': '#EF4444',
        'bg': 'rgba(239, 68, 68, 0.15)',
        'border': '#EF4444',
    },
    'NEUTRAL': {
        'color': '#F59E0B',
        'bg': 'rgba(245, 158, 11, 0.15)',
        'border': '#F59E0B',
    },
}

# =============================================================================
# SIGNAL STYLES (Exposure Level Styling)
# =============================================================================

SIGNAL_STYLES = {
    'RISK_ON': {
        'color': '#10B981',
        'bg': 'rgba(16, 185, 129, 0.15)',
    },
    'RISK_OFF': {
        'color': '#EF4444',
        'bg': 'rgba(239, 68, 68, 0.15)',
    },
    'CAUTION': {
        'color': '#F59E0B',
        'bg': 'rgba(245, 158, 11, 0.15)',
    },
}

# =============================================================================
# BREADTH COLORS (for consistent chart styling)
# =============================================================================

BREADTH_COLORS = {
    'ma20': '#8B5CF6',  # Purple (short-term)
    'ma50': '#06B6D4',  # Cyan (medium-term)
    'ma100': '#F59E0B', # Amber (long-term)
}

# =============================================================================
# SIGNAL MATRIX
# Trading signals based on breadth + trend conditions
# =============================================================================

SIGNAL_MATRIX = {
    # ==========================================================================
    # UPTREND SIGNALS (MA50 >= 50% AND MA100 >= 50%)
    # ==========================================================================
    'STRONG_BUY': {
        'label': 'STRONG BUY',
        'subtitle': 'Deep Pullback',
        'condition': f'Uptrend + MA20 < {STRONG_BUY_THRESHOLD}%',
        'action': 'Giải ngân mạnh. Rũ bỏ hoàn hảo.',
        'color': '#059669',
        'bg': 'rgba(5, 150, 105, 0.15)',
    },
    'BUY': {
        'label': 'BUY',
        'subtitle': 'Normal Pullback',
        'condition': f'Uptrend + MA20 < {BUY_THRESHOLD}%',
        'action': 'Mua gia tăng hoặc mở vị thế mới.',
        'color': '#10B981',
        'bg': 'rgba(16, 185, 129, 0.15)',
    },
    'HOLD': {
        'label': 'HOLD',
        'subtitle': 'Riding Trend',
        'condition': f'Uptrend + {BUY_THRESHOLD}% <= MA20 <= {WARNING_THRESHOLD}%',
        'action': 'Nắm giữ danh mục. Trend vẫn tốt.',
        'color': '#3B82F6',
        'bg': 'rgba(59, 130, 246, 0.15)',
    },
    'WARNING': {
        'label': 'WARNING',
        'subtitle': 'Overheated',
        'condition': f'Uptrend + MA20 > {WARNING_THRESHOLD}%',
        'action': 'Không mua đuổi. Canh chốt lời margin.',
        'color': '#F59E0B',
        'bg': 'rgba(245, 158, 11, 0.15)',
    },

    # ==========================================================================
    # DOWNTREND SIGNALS (MA50 < 50% OR MA100 < 50%)
    # ==========================================================================
    'SELL': {
        'label': 'SELL',
        'subtitle': 'Bull Trap',
        'condition': f'Downtrend + MA20 > {SELL_THRESHOLD}%',
        'action': 'Bán hạ tỷ trọng. Đây là bẫy tăng giá.',
        'color': '#DC2626',
        'bg': 'rgba(220, 38, 38, 0.15)',
    },
    'DANGER': {
        'label': 'DANGER',
        'subtitle': 'Market Crash',
        'condition': f'MA50 < {DANGER_MA50_THRESHOLD}% + MA20 < {STRONG_BUY_THRESHOLD}% + No Higher Low',
        'action': 'Đứng ngoài tuyệt đối. Không bắt đáy.',
        'color': '#7F1D1D',
        'bg': 'rgba(127, 29, 29, 0.2)',
    },
    'WAIT': {
        'label': 'WAIT',
        'subtitle': 'No Trend',
        'condition': 'Downtrend/Sideways + No clear signal',
        'action': 'Quan sát. Chưa có điểm vào an toàn.',
        'color': '#64748B',
        'bg': 'rgba(100, 116, 139, 0.15)',
    },

    # ==========================================================================
    # BOTTOM DETECTION SIGNALS (Special states during market bottoms)
    # ==========================================================================
    'ACCUMULATING': {
        'label': 'ACCUMULATING',
        'subtitle': 'Smart Money Entering',
        'condition': 'All MA < 30% + MA20 Higher Low detected',
        'action': 'Theo dõi sát. Smart money đang tích lũy. Chuẩn bị vốn.',
        'color': '#6366F1',  # Indigo
        'bg': 'rgba(99, 102, 241, 0.15)',
    },
    'EARLY_BUY': {
        'label': 'EARLY BUY',
        'subtitle': 'Early Reversal',
        'condition': 'MA20 >= 25% + Both MA20 & MA50 Higher Low',
        'action': 'Test mua 10-20% danh mục. Stop-loss chặt dưới đáy gần nhất.',
        'color': '#22D3EE',  # Cyan
        'bg': 'rgba(34, 211, 238, 0.15)',
    },
}

# =============================================================================
# BOTTOM FORMATION STAGES
# 3-stage bottom detection model
# =============================================================================

BOTTOM_STAGES = {
    'CAPITULATION': {
        'label': 'CAPITULATION',
        'description': 'Hoảng loạn bán tháo',
        'condition': 'Tất cả MA < 25%, chưa tạo đáy cao hơn',
        'color': '#7F1D1D',
        'icon': '1',
    },
    'ACCUMULATING': {
        'label': 'ACCUMULATING',
        'description': 'Smart money đang vào',
        'condition': 'Tất cả MA < 30%, MA20 tạo đáy cao hơn (7d) và đang tăng',
        'color': '#6366F1',
        'icon': '2',
    },
    'EARLY_REVERSAL': {
        'label': 'EARLY REVERSAL',
        'description': 'Đảo chiều sớm',
        'condition': 'MA20 >= 25% + Higher Low, MA50 tạo đáy cao hơn (9d)',
        'color': '#22D3EE',
        'icon': '3',
    },
}

# =============================================================================
# FORECAST - RATING STYLING
# =============================================================================

RATING_COLORS = {
    'STRONG BUY': '#00C9AD',  # Bright teal
    'BUY': '#009B87',         # Brand teal
    'HOLD': '#FFC132',        # Brand gold
    'SELL': '#E63946',        # Red
    'STRONG SELL': '#9D0208', # Dark red
    'N/A': '#64748B',         # Gray
}

RATING_BG_COLORS = {
    'STRONG BUY': 'rgba(0, 201, 173, 0.15)',
    'BUY': 'rgba(0, 155, 135, 0.15)',
    'HOLD': 'rgba(255, 193, 50, 0.15)',
    'SELL': 'rgba(230, 57, 70, 0.15)',
    'STRONG SELL': 'rgba(157, 2, 8, 0.15)',
    'N/A': 'rgba(100, 116, 139, 0.15)',
}

# =============================================================================
# RRG - QUADRANT STYLING
# =============================================================================

QUADRANT_COLORS = {
    'LEADING': '#10B981',     # Emerald Green
    'WEAKENING': '#F59E0B',   # Amber
    'LAGGING': '#EF4444',     # Red
    'IMPROVING': '#06B6D4',   # Cyan
}

QUADRANT_BG = {
    'LEADING': 'rgba(16, 185, 129, 0.15)',
    'WEAKENING': 'rgba(245, 158, 11, 0.15)',
    'LAGGING': 'rgba(239, 68, 68, 0.15)',
    'IMPROVING': 'rgba(6, 182, 212, 0.15)',
}

QUADRANT_TRAIL = {
    'LEADING': 'rgba(16, 185, 129, 0.25)',
    'WEAKENING': 'rgba(245, 158, 11, 0.25)',
    'LAGGING': 'rgba(239, 68, 68, 0.25)',
    'IMPROVING': 'rgba(6, 182, 212, 0.25)',
    'UNKNOWN': 'rgba(100, 116, 139, 0.25)',
}

# =============================================================================
# SCANNER - SIGNAL TYPES
# =============================================================================

SIGNAL_TYPES = {
    'patterns': 'Candlestick',
    'ma_crossover': 'MA Cross',
    'volume_spike': 'Volume Spike',
    'breakout': 'Breakout',
}

# =============================================================================
# SCANNER - PATTERN INTERPRETATIONS (Vietnamese)
# Based on ta-lib candlestick patterns
# =============================================================================

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

# =============================================================================
# SCANNER - PATTERN VOLUME MATRIX
# Interpretation based on pattern + volume combination
# =============================================================================

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

# =============================================================================
# SCANNER - VOLUME CONTEXT STYLING
# =============================================================================

VOLUME_CONTEXT = {
    'HIGH': {'label': 'VOL CAO', 'color': '#10B981', 'bg': 'rgba(16, 185, 129, 0.15)'},
    'AVG': {'label': 'VOL TB', 'color': '#F59E0B', 'bg': 'rgba(245, 158, 11, 0.15)'},
    'LOW': {'label': 'VOL THẤP', 'color': '#64748B', 'bg': 'rgba(100, 116, 139, 0.15)'},
}

# =============================================================================
# SCANNER - ACTION COLORS
# =============================================================================

ACTION_COLORS = {
    'BUY': {'bg': 'rgba(16, 185, 129, 0.15)', 'text': '#10B981', 'label': 'MUA'},
    'SELL': {'bg': 'rgba(239, 68, 68, 0.15)', 'text': '#EF4444', 'label': 'BÁN'},
    'HOLD': {'bg': 'rgba(245, 158, 11, 0.15)', 'text': '#F59E0B', 'label': 'CHỜ'},
    'NEUTRAL': {'bg': 'rgba(100, 116, 139, 0.15)', 'text': '#64748B', 'label': 'TRUNG LẬP'},
    'BULLISH': {'bg': 'rgba(16, 185, 129, 0.15)', 'text': '#10B981', 'label': 'MUA'},
    'BEARISH': {'bg': 'rgba(239, 68, 68, 0.15)', 'text': '#EF4444', 'label': 'BÁN'},
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_signal_style(signal_key: str) -> dict:
    """Get styling for a signal key."""
    return SIGNAL_MATRIX.get(signal_key, SIGNAL_MATRIX['WAIT'])


def get_regime_style(regime: str) -> dict:
    """Get styling for a regime."""
    return REGIME_STYLES.get(regime, REGIME_STYLES['NEUTRAL'])


def is_uptrend(ma50_pct: float, ma100_pct: float) -> bool:
    """Check if market is in uptrend based on breadth."""
    return (ma50_pct >= TREND_CONFIRMATION_THRESHOLD and
            ma100_pct >= TREND_CONFIRMATION_THRESHOLD)


def determine_signal(
    ma20_pct: float,
    ma50_pct: float,
    ma100_pct: float,
    ma20_higher_low: bool,
    ma50_higher_low: bool,
    bottom_stage: str | None
) -> str:
    """
    Determine trading signal based on market conditions.

    Args:
        ma20_pct: MA20 breadth percentage
        ma50_pct: MA50 breadth percentage
        ma100_pct: MA100 breadth percentage
        ma20_higher_low: Whether MA20 shows higher low pattern
        ma50_higher_low: Whether MA50 shows higher low pattern
        bottom_stage: Current bottom formation stage (if any)

    Returns:
        Signal key (e.g., 'STRONG_BUY', 'WAIT', 'DANGER')
    """
    uptrend = is_uptrend(ma50_pct, ma100_pct)

    if uptrend:
        # UPTREND scenarios (Buy signals)
        if ma20_pct < STRONG_BUY_THRESHOLD:
            return 'STRONG_BUY'
        elif ma20_pct < BUY_THRESHOLD:
            return 'BUY'
        elif ma20_pct > WARNING_THRESHOLD:
            return 'WARNING'
        else:
            return 'HOLD'
    else:
        # DOWNTREND/SIDEWAYS scenarios (Defensive + Bottom Detection)
        if ma20_pct > SELL_THRESHOLD:
            return 'SELL'
        elif ma50_pct < DANGER_MA50_THRESHOLD and ma20_pct < STRONG_BUY_THRESHOLD and not ma20_higher_low:
            return 'DANGER'
        # Bottom Detection Signals
        elif bottom_stage == 'EARLY_REVERSAL':
            return 'EARLY_BUY'
        elif bottom_stage == 'ACCUMULATING':
            return 'ACCUMULATING'
        else:
            return 'WAIT'
