# Phase 4: Stock Scanner Tab

**Goal:** Build Tab 3 with comprehensive signal scanner including pattern recognition

**Note:** Tab 4 (Trading Lists) sẽ được implement sau khi tối ưu file nhập danh mục.

---

## 1. Component Layout

### Tab 3: Stock Scanner

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      STOCK SCANNER                                                  │
├────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                     │
│  ┌─────────────────────────────────── QUICK FILTERS ───────────────────────────────────────────┐   │
│  │ Nhập mã: [VIC, ACB, FPT___________] │ Sector: [Ngân hàng ▼] │ View All Sector [✓]           │   │
│  └──────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                     │
│  ┌─────────────────────────────────── ADVANCED FILTERS ─────────────────────────────────────────┐  │
│  │ Signal Type ▼ │ Pattern ▼ │ Vol Context ▼ │ Min RVOL: 0.8 │ Min Value: 5B │ Min Score: 50   │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                     │
│  ┌─────────────────────────────── SIGNAL TABLE (Compact + Interpretation) ─────────────────────┐  │
│  │ Mã  │Ngành    │Tín hiệu + Giải thích                                   │Điểm       │Hành động│ │
│  │─────┼─────────┼────────────────────────────────────────────────────────┼───────────┼─────────│ │
│  │ ACB │Ngân hàng│🔼 Engulfing 🔥 + Cup&Handle                            │████████░░│🟢 MUA   │ │
│  │     │         │→ Đảo chiều cực mạnh, vol cao xác nhận buyers áp đảo    │   92      │         │ │
│  │─────┼─────────┼────────────────────────────────────────────────────────┼───────────┼─────────│ │
│  │ FPT │Công nghệ│🔼 Morning Star 🔥 + Flag                               │████████░░│🟢 MUA   │ │
│  │     │         │→ Mô hình 3 nến đảo chiều hoàn hảo, high conviction     │   88      │         │ │
│  │─────┼─────────┼────────────────────────────────────────────────────────┼───────────┼─────────│ │
│  │ VNM │Thực phẩm│🔼 Hammer + Double Bottom                               │███████░░░│🟢 MUA   │ │
│  │     │         │→ Từ chối giảm giá, vol TB - cần theo dõi thêm          │   75      │         │ │
│  │─────┼─────────┼────────────────────────────────────────────────────────┼───────────┼─────────│ │
│  │ TCB │Ngân hàng│🔼 Harami 📉                                            │██████░░░░│🟡 CHỜ   │ │
│  │     │         │→ Tín hiệu yếu - vol thấp, cần confirm phiên sau        │   62      │         │ │
│  │─────┼─────────┼────────────────────────────────────────────────────────┼───────────┼─────────│ │
│  │ HPG │Thép     │🔽 Evening Star 🔥 + H&S                                │████████░░│🔴 BÁN   │ │
│  │     │         │→ Đảo chiều giảm mạnh, sellers kiểm soát với volume lớn │   85      │         │ │
│  │─────┼─────────┼────────────────────────────────────────────────────────┼───────────┼─────────│ │
│  │ VIC │BĐS      │🔽 Hanging Man                                          │█████░░░░░│🟡 CHỜ   │ │
│  │     │         │→ Cảnh báo đảo chiều, cần xác nhận phiên tiếp theo      │   55      │         │ │
│  └───────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                     │
│  Tổng hợp: 🟢 MUA: 15 │ 🔴 BÁN: 8 │ 🟡 CHỜ: 17 │ Tổng signals: 40                                  │
│                                                                                                     │
│  ┌──────────────────────────────── SECTOR VIEW MODE ────────────────────────────────────────────┐  │
│  │ Ngành: Ngân hàng (15 CP) │ Điểm TB: 72 │ 🟢 Bullish: 8 │ 🔴 Bearish: 3 │ 🟡 Neutral: 4       │  │
│  │─────────────────────────────────────────────────────────────────────────────────────────────│  │
│  │ VCB │ ACB │ TCB │ MBB │ CTG │ BID │ STB │ HDB │ VPB │ TPB │ EIB │ LPB │ MSB │ OCB │ SHB   │  │
│  │ 92  │ 88  │ 75  │ 72  │ 68  │ 65  │ 62  │ 58  │ 55  │ 52  │ 48  │ 45  │ 42  │ 38  │ 35    │  │
│  │ MUA │ MUA │ CHỜ │ CHỜ │ CHỜ │ CHỜ │ CHỜ │ CHỜ │ CHỜ │ CHỜ │ CHỜ │ CHỜ │ BÁN │ BÁN │ BÁN  │  │
│  └───────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                     │
└────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Tab 4: Trading Lists (DEFERRED)

**Status:** Sẽ implement sau khi tối ưu file nhập danh mục

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRADING LISTS (Coming Soon)                  │
├─────────────────────────────────────────────────────────────────┤
│  Feature sẽ được thêm sau:                                       │
│  - Buy List với position sizing                                 │
│  - Sell List với urgency level                                  │
│  - Portfolio capital & risk management                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Pattern Recognition System

### 2.1 Candlestick Patterns (ta-lib)

Use ta-lib for reliable candlestick pattern detection:

```python
# File: PROCESSORS/technical/indicators/candlestick_patterns.py

import talib
import pandas as pd
from dataclasses import dataclass
from enum import Enum

class PatternSignal(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

@dataclass
class CandlestickPattern:
    name: str
    signal: PatternSignal
    description_vi: str
    interpretation: str
    reliability: int  # 1-5 stars
    talib_func: str

# ========== BULLISH PATTERNS (Đảo chiều tăng) ==========

BULLISH_PATTERNS = {
    'ENGULFING': CandlestickPattern(
        name='Bullish Engulfing',
        signal=PatternSignal.BULLISH,
        description_vi='Nến nhấn chìm tăng',
        interpretation='Đảo chiều mạnh, thân nến xanh bao trùm hoàn toàn nến đỏ trước. Buyers kiểm soát hoàn toàn.',
        reliability=4,
        talib_func='CDLENGULFING'
    ),
    'HAMMER': CandlestickPattern(
        name='Hammer',
        signal=PatternSignal.BULLISH,
        description_vi='Nến búa',
        interpretation='Từ chối giảm giá, bấc dưới dài >= 2x thân. Xuất hiện cuối downtrend = tín hiệu đảo chiều.',
        reliability=3,
        talib_func='CDLHAMMER'
    ),
    'MORNING_STAR': CandlestickPattern(
        name='Morning Star',
        signal=PatternSignal.BULLISH,
        description_vi='Sao mai',
        interpretation='Mô hình 3 nến đảo chiều: (1) Nến đỏ dài, (2) Doji/Spinning top, (3) Nến xanh dài. Cần confirm volume.',
        reliability=5,
        talib_func='CDLMORNINGSTAR'
    ),
    'PIERCING': CandlestickPattern(
        name='Piercing Pattern',
        signal=PatternSignal.BULLISH,
        description_vi='Mô hình xuyên thấu',
        interpretation='Nến xanh mở thấp hơn low nến đỏ trước, đóng trên 50% thân nến đỏ. Tín hiệu đảo chiều vừa.',
        reliability=3,
        talib_func='CDLPIERCING'
    ),
    'MARUBOZU_WHITE': CandlestickPattern(
        name='White Marubozu',
        signal=PatternSignal.BULLISH,
        description_vi='Nến trắng không bấc',
        interpretation='Thân nến dài không bấc - buyers control 100%. Momentum tăng mạnh, thường tiếp tục xu hướng.',
        reliability=4,
        talib_func='CDLMARUBOZU'
    ),
    'THREE_WHITE_SOLDIERS': CandlestickPattern(
        name='Three White Soldiers',
        signal=PatternSignal.BULLISH,
        description_vi='Ba chú lính trắng',
        interpretation='3 nến xanh liên tiếp, mỗi nến mở trong thân nến trước và đóng cao hơn. Đảo chiều cực mạnh.',
        reliability=5,
        talib_func='CDL3WHITESOLDIERS'
    ),
    'HARAMI_BULLISH': CandlestickPattern(
        name='Bullish Harami',
        signal=PatternSignal.BULLISH,
        description_vi='Harami tăng',
        interpretation='Nến nhỏ nằm trong thân nến đỏ lớn trước đó. Momentum giảm yếu đi, có thể đảo chiều.',
        reliability=2,
        talib_func='CDLHARAMI'
    ),
    'INVERTED_HAMMER': CandlestickPattern(
        name='Inverted Hammer',
        signal=PatternSignal.BULLISH,
        description_vi='Nến búa ngược',
        interpretation='Bấc trên dài, thân nhỏ ở dưới. Cần confirm bởi nến tăng tiếp theo.',
        reliability=2,
        talib_func='CDLINVERTEDHAMMER'
    ),
    'TWEEZER_BOTTOM': CandlestickPattern(
        name='Tweezer Bottom',
        signal=PatternSignal.BULLISH,
        description_vi='Đáy nhíp',
        interpretation='2 nến có mức low bằng nhau tại vùng hỗ trợ. Support được test và giữ vững.',
        reliability=3,
        talib_func='CDLUNIQUE3RIVER'  # Approximate
    ),
    'DOJI_DRAGONFLY': CandlestickPattern(
        name='Dragonfly Doji',
        signal=PatternSignal.BULLISH,
        description_vi='Doji chuồn chuồn',
        interpretation='Open = High = Close, bấc dưới dài. Từ chối giảm giá mạnh mẽ.',
        reliability=3,
        talib_func='CDLDRAGONFLYDOJI'
    ),
}

# ========== BEARISH PATTERNS (Đảo chiều giảm) ==========

BEARISH_PATTERNS = {
    'ENGULFING_BEARISH': CandlestickPattern(
        name='Bearish Engulfing',
        signal=PatternSignal.BEARISH,
        description_vi='Nến nhấn chìm giảm',
        interpretation='Nến đỏ bao trùm hoàn toàn nến xanh trước. Sellers kiểm soát, đảo chiều mạnh.',
        reliability=4,
        talib_func='CDLENGULFING'
    ),
    'HANGING_MAN': CandlestickPattern(
        name='Hanging Man',
        signal=PatternSignal.BEARISH,
        description_vi='Người treo cổ',
        interpretation='Giống Hammer nhưng xuất hiện sau uptrend. Cảnh báo đảo chiều giảm.',
        reliability=3,
        talib_func='CDLHANGINGMAN'
    ),
    'EVENING_STAR': CandlestickPattern(
        name='Evening Star',
        signal=PatternSignal.BEARISH,
        description_vi='Sao hôm',
        interpretation='Ngược Morning Star: (1) Nến xanh, (2) Doji/Spinning, (3) Nến đỏ dài. Tín hiệu giảm mạnh.',
        reliability=5,
        talib_func='CDLEVENINGSTAR'
    ),
    'SHOOTING_STAR': CandlestickPattern(
        name='Shooting Star',
        signal=PatternSignal.BEARISH,
        description_vi='Sao băng',
        interpretation='Bấc trên dài, thân nhỏ ở dưới, xuất hiện sau uptrend. Từ chối tăng giá.',
        reliability=3,
        talib_func='CDLSHOOTINGSTAR'
    ),
    'DARK_CLOUD': CandlestickPattern(
        name='Dark Cloud Cover',
        signal=PatternSignal.BEARISH,
        description_vi='Mây đen che phủ',
        interpretation='Nến đỏ mở cao hơn close nến xanh, đóng dưới 50% thân nến xanh. Áp lực bán.',
        reliability=3,
        talib_func='CDLDARKCLOUDCOVER'
    ),
    'THREE_BLACK_CROWS': CandlestickPattern(
        name='Three Black Crows',
        signal=PatternSignal.BEARISH,
        description_vi='Ba con quạ đen',
        interpretation='3 nến đỏ liên tiếp, mỗi nến mở trong thân nến trước và đóng thấp hơn. Giảm rất mạnh.',
        reliability=5,
        talib_func='CDL3BLACKCROWS'
    ),
    'HARAMI_BEARISH': CandlestickPattern(
        name='Bearish Harami',
        signal=PatternSignal.BEARISH,
        description_vi='Harami giảm',
        interpretation='Nến nhỏ nằm trong thân nến xanh lớn trước. Momentum tăng yếu đi.',
        reliability=2,
        talib_func='CDLHARAMI'
    ),
    'DOJI_GRAVESTONE': CandlestickPattern(
        name='Gravestone Doji',
        signal=PatternSignal.BEARISH,
        description_vi='Doji bia mộ',
        interpretation='Open = Low = Close, bấc trên dài. Từ chối tăng giá mạnh mẽ.',
        reliability=3,
        talib_func='CDLGRAVESTONEDOJI'
    ),
}

ALL_PATTERNS = {**BULLISH_PATTERNS, **BEARISH_PATTERNS}


def detect_candlestick_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect all candlestick patterns using ta-lib

    Args:
        df: DataFrame with OHLC columns (open, high, low, close)

    Returns:
        DataFrame with pattern detection columns
    """
    result = df.copy()

    # Ensure column names are lowercase
    col_map = {c: c.lower() for c in df.columns}
    result = result.rename(columns=col_map)

    o, h, l, c = result['open'], result['high'], result['low'], result['close']

    # Detect all patterns
    pattern_results = {}

    # Bullish patterns
    pattern_results['engulfing'] = talib.CDLENGULFING(o, h, l, c)
    pattern_results['hammer'] = talib.CDLHAMMER(o, h, l, c)
    pattern_results['morning_star'] = talib.CDLMORNINGSTAR(o, h, l, c)
    pattern_results['piercing'] = talib.CDLPIERCING(o, h, l, c)
    pattern_results['marubozu'] = talib.CDLMARUBOZU(o, h, l, c)
    pattern_results['three_white_soldiers'] = talib.CDL3WHITESOLDIERS(o, h, l, c)
    pattern_results['harami'] = talib.CDLHARAMI(o, h, l, c)
    pattern_results['inverted_hammer'] = talib.CDLINVERTEDHAMMER(o, h, l, c)
    pattern_results['doji_dragonfly'] = talib.CDLDRAGONFLYDOJI(o, h, l, c)

    # Bearish patterns
    pattern_results['hanging_man'] = talib.CDLHANGINGMAN(o, h, l, c)
    pattern_results['evening_star'] = talib.CDLEVENINGSTAR(o, h, l, c)
    pattern_results['shooting_star'] = talib.CDLSHOOTINGSTAR(o, h, l, c)
    pattern_results['dark_cloud'] = talib.CDLDARKCLOUDCOVER(o, h, l, c)
    pattern_results['three_black_crows'] = talib.CDL3BLACKCROWS(o, h, l, c)
    pattern_results['doji_gravestone'] = talib.CDLGRAVESTONEDOJI(o, h, l, c)

    # Standard Doji
    pattern_results['doji'] = talib.CDLDOJI(o, h, l, c)

    # Aggregate pattern detection
    result['candle_pattern'] = None
    result['candle_signal'] = None
    result['pattern_interpretation'] = None

    # Process each row for pattern detection
    for idx in result.index:
        detected = []
        for pattern_name, values in pattern_results.items():
            if values[idx] != 0:
                signal = 'BULLISH' if values[idx] > 0 else 'BEARISH'
                detected.append((pattern_name, signal, abs(values[idx])))

        if detected:
            # Sort by strength (abs value)
            detected.sort(key=lambda x: x[2], reverse=True)
            top_pattern = detected[0]
            result.loc[idx, 'candle_pattern'] = top_pattern[0].upper()
            result.loc[idx, 'candle_signal'] = top_pattern[1]

    return result


def get_pattern_interpretation(pattern_name: str) -> str:
    """Get Vietnamese interpretation for a pattern"""
    pattern = ALL_PATTERNS.get(pattern_name.upper())
    if pattern:
        return pattern.interpretation
    return "Không xác định"
```

### 2.2 Chart Patterns (Price Action)

Detect classical chart patterns using price structure analysis:

```python
# File: PROCESSORS/technical/indicators/chart_patterns.py

import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum
from scipy.signal import argrelextrema

class ChartPatternType(Enum):
    DOUBLE_BOTTOM = "Double Bottom"
    DOUBLE_TOP = "Double Top"
    HEAD_SHOULDERS = "Head & Shoulders"
    INV_HEAD_SHOULDERS = "Inverse H&S"
    CUP_HANDLE = "Cup & Handle"
    FLAG_BULL = "Bull Flag"
    FLAG_BEAR = "Bear Flag"
    TRIANGLE_ASC = "Ascending Triangle"
    TRIANGLE_DESC = "Descending Triangle"
    TRIANGLE_SYM = "Symmetrical Triangle"
    WEDGE_RISING = "Rising Wedge"
    WEDGE_FALLING = "Falling Wedge"
    CHANNEL_UP = "Ascending Channel"
    CHANNEL_DOWN = "Descending Channel"


@dataclass
class ChartPattern:
    pattern_type: ChartPatternType
    signal: str  # BULLISH, BEARISH, NEUTRAL
    description_vi: str
    interpretation: str
    target_calculation: str


CHART_PATTERNS = {
    'DOUBLE_BOTTOM': ChartPattern(
        pattern_type=ChartPatternType.DOUBLE_BOTTOM,
        signal='BULLISH',
        description_vi='Đáy đôi',
        interpretation='Giá test support 2 lần không phá vỡ. Breakout neckline = tín hiệu mua. Target = chiều cao pattern.',
        target_calculation='Target = Neckline + (Neckline - Low)'
    ),
    'DOUBLE_TOP': ChartPattern(
        pattern_type=ChartPatternType.DOUBLE_TOP,
        signal='BEARISH',
        description_vi='Đỉnh đôi',
        interpretation='Giá test resistance 2 lần không vượt qua. Breakdown neckline = tín hiệu bán.',
        target_calculation='Target = Neckline - (High - Neckline)'
    ),
    'HEAD_SHOULDERS': ChartPattern(
        pattern_type=ChartPatternType.HEAD_SHOULDERS,
        signal='BEARISH',
        description_vi='Vai - Đầu - Vai',
        interpretation='Mô hình đảo chiều cổ điển sau uptrend. Breakdown neckline xác nhận. Reliability cao.',
        target_calculation='Target = Neckline - (Head - Neckline)'
    ),
    'INV_HEAD_SHOULDERS': ChartPattern(
        pattern_type=ChartPatternType.INV_HEAD_SHOULDERS,
        signal='BULLISH',
        description_vi='Vai - Đầu - Vai ngược',
        interpretation='Đảo chiều tăng sau downtrend. Breakout neckline kèm volume = strong buy.',
        target_calculation='Target = Neckline + (Neckline - Head)'
    ),
    'CUP_HANDLE': ChartPattern(
        pattern_type=ChartPatternType.CUP_HANDLE,
        signal='BULLISH',
        description_vi='Cốc - Tay cầm',
        interpretation='Continuation pattern trong uptrend. Breakout handle resistance với volume cao.',
        target_calculation='Target = Entry + Cup Depth'
    ),
    'FLAG_BULL': ChartPattern(
        pattern_type=ChartPatternType.FLAG_BULL,
        signal='BULLISH',
        description_vi='Cờ tăng',
        interpretation='Consolidation sau rally mạnh. Breakout flag = continue uptrend. Flagpole height = target.',
        target_calculation='Target = Breakout + Flagpole Height'
    ),
    'FLAG_BEAR': ChartPattern(
        pattern_type=ChartPatternType.FLAG_BEAR,
        signal='BEARISH',
        description_vi='Cờ giảm',
        interpretation='Consolidation sau đợt giảm mạnh. Breakdown flag = continue downtrend.',
        target_calculation='Target = Breakdown - Flagpole Height'
    ),
    'TRIANGLE_ASC': ChartPattern(
        pattern_type=ChartPatternType.TRIANGLE_ASC,
        signal='BULLISH',
        description_vi='Tam giác tăng',
        interpretation='Flat resistance + higher lows. Thường breakout lên. Volume quan trọng.',
        target_calculation='Target = Breakout + Triangle Height'
    ),
    'TRIANGLE_DESC': ChartPattern(
        pattern_type=ChartPatternType.TRIANGLE_DESC,
        signal='BEARISH',
        description_vi='Tam giác giảm',
        interpretation='Flat support + lower highs. Thường breakdown xuống.',
        target_calculation='Target = Breakdown - Triangle Height'
    ),
    'WEDGE_RISING': ChartPattern(
        pattern_type=ChartPatternType.WEDGE_RISING,
        signal='BEARISH',
        description_vi='Nêm tăng',
        interpretation='Converging highs/lows đều tăng nhưng momentum yếu dần. Thường breakdown.',
        target_calculation='Target = Entry at wedge base'
    ),
    'WEDGE_FALLING': ChartPattern(
        pattern_type=ChartPatternType.WEDGE_FALLING,
        signal='BULLISH',
        description_vi='Nêm giảm',
        interpretation='Converging highs/lows đều giảm. Thường breakout lên khi momentum bán cạn kiệt.',
        target_calculation='Target = Entry at wedge base'
    ),
}


def detect_chart_patterns(
    df: pd.DataFrame,
    lookback: int = 60,
    min_pattern_bars: int = 10
) -> dict:
    """
    Detect classical chart patterns

    Args:
        df: OHLCV DataFrame
        lookback: Number of bars to analyze
        min_pattern_bars: Minimum bars for valid pattern

    Returns:
        dict with detected pattern info
    """
    if len(df) < lookback:
        return {'pattern': None, 'signal': None}

    recent = df.tail(lookback).copy()
    close = recent['close'].values
    high = recent['high'].values
    low = recent['low'].values

    # Find local peaks and troughs
    order = 5  # Number of points for comparison
    local_max_idx = argrelextrema(high, np.greater_equal, order=order)[0]
    local_min_idx = argrelextrema(low, np.less_equal, order=order)[0]

    local_maxs = [(i, high[i]) for i in local_max_idx]
    local_mins = [(i, low[i]) for i in local_min_idx]

    pattern_result = {
        'pattern': None,
        'signal': None,
        'description': None,
        'interpretation': None
    }

    # ===== Double Bottom Detection =====
    if len(local_mins) >= 2:
        last_two_mins = local_mins[-2:]
        min1_idx, min1_val = last_two_mins[0]
        min2_idx, min2_val = last_two_mins[1]

        # Check if bottoms are within 3% of each other
        if abs(min1_val - min2_val) / min1_val < 0.03:
            # Check for price breakout above neckline (max between bottoms)
            neckline = max(high[min1_idx:min2_idx+1])
            if close[-1] > neckline:
                pattern_result = {
                    'pattern': 'DOUBLE_BOTTOM',
                    'signal': 'BULLISH',
                    'description': 'Đáy đôi đã breakout',
                    'interpretation': CHART_PATTERNS['DOUBLE_BOTTOM'].interpretation
                }
                return pattern_result

    # ===== Double Top Detection =====
    if len(local_maxs) >= 2:
        last_two_maxs = local_maxs[-2:]
        max1_idx, max1_val = last_two_maxs[0]
        max2_idx, max2_val = last_two_maxs[1]

        if abs(max1_val - max2_val) / max1_val < 0.03:
            neckline = min(low[max1_idx:max2_idx+1])
            if close[-1] < neckline:
                pattern_result = {
                    'pattern': 'DOUBLE_TOP',
                    'signal': 'BEARISH',
                    'description': 'Đỉnh đôi đã breakdown',
                    'interpretation': CHART_PATTERNS['DOUBLE_TOP'].interpretation
                }
                return pattern_result

    # ===== Head and Shoulders Detection =====
    if len(local_maxs) >= 3 and len(local_mins) >= 2:
        # Need left shoulder, head, right shoulder
        peaks = local_maxs[-3:]
        left_shoulder = peaks[0][1]
        head = peaks[1][1]
        right_shoulder = peaks[2][1]

        # Head should be highest, shoulders similar
        if head > left_shoulder and head > right_shoulder:
            if abs(left_shoulder - right_shoulder) / left_shoulder < 0.05:
                # Calculate neckline
                troughs = [m for m in local_mins if peaks[0][0] < m[0] < peaks[2][0]]
                if len(troughs) >= 2:
                    neckline = (troughs[0][1] + troughs[-1][1]) / 2
                    if close[-1] < neckline:
                        pattern_result = {
                            'pattern': 'HEAD_SHOULDERS',
                            'signal': 'BEARISH',
                            'description': 'Vai-Đầu-Vai đã breakdown neckline',
                            'interpretation': CHART_PATTERNS['HEAD_SHOULDERS'].interpretation
                        }
                        return pattern_result

    # ===== Bull Flag Detection =====
    # Look for strong rally followed by consolidation
    if len(close) >= 20:
        rally_start = lookback - 20
        rally_end = lookback - 10
        consolidation = close[-10:]

        rally_return = (close[rally_end] - close[rally_start]) / close[rally_start]
        consolidation_range = (max(consolidation) - min(consolidation)) / min(consolidation)

        if rally_return > 0.1 and consolidation_range < 0.05:
            # Flag detected, check for breakout
            flag_high = max(consolidation)
            if close[-1] > flag_high * 1.01:
                pattern_result = {
                    'pattern': 'FLAG_BULL',
                    'signal': 'BULLISH',
                    'description': 'Cờ tăng đã breakout',
                    'interpretation': CHART_PATTERNS['FLAG_BULL'].interpretation
                }
                return pattern_result

    return pattern_result


def get_chart_pattern_for_symbol(
    symbol: str,
    ohlcv_df: pd.DataFrame,
    lookback: int = 60
) -> dict:
    """Get chart pattern detection for a single symbol"""
    if symbol not in ohlcv_df['symbol'].values:
        return {'pattern': None}

    symbol_df = ohlcv_df[ohlcv_df['symbol'] == symbol].tail(lookback)
    return detect_chart_patterns(symbol_df, lookback=lookback)
```

### 2.3 Volume Context Analysis (NEW)

Volume là yếu tố quan trọng để xác nhận độ tin cậy của pattern:

```python
# File: PROCESSORS/technical/indicators/volume_context.py

from enum import Enum
from dataclasses import dataclass

class VolumeContext(Enum):
    HIGH = "HIGH"      # RVOL >= 1.5 - Strong confirmation
    AVERAGE = "AVG"    # 0.8 <= RVOL < 1.5 - Normal
    LOW = "LOW"        # RVOL < 0.8 - Weak, needs confirmation

@dataclass
class VolumeAnalysis:
    context: VolumeContext
    rvol: float
    interpretation: str
    confidence_modifier: float  # -0.5 to +1.0

# Volume context thresholds
VOLUME_THRESHOLDS = {
    'HIGH': 1.5,   # RVOL >= 1.5
    'AVG': 0.8,    # 0.8 <= RVOL < 1.5
    'LOW': 0.0     # RVOL < 0.8
}

# Volume context display
VOLUME_DISPLAY = {
    'HIGH': '🔥 HIGH',
    'AVG': '📊 AVG',
    'LOW': '📉 LOW'
}


def analyze_volume_context(rvol: float, candle_pattern: str = None) -> VolumeAnalysis:
    """
    Analyze volume context for pattern confirmation

    Args:
        rvol: Relative volume (current vol / avg vol)
        candle_pattern: Optional pattern for context-specific interpretation

    Returns:
        VolumeAnalysis with context, interpretation, and confidence modifier
    """
    if rvol >= VOLUME_THRESHOLDS['HIGH']:
        context = VolumeContext.HIGH
        confidence_modifier = 1.0

        if candle_pattern:
            interpretation = f"Volume cao xác nhận {candle_pattern} - Tín hiệu mạnh"
        else:
            interpretation = "Volume cao - Sức mua/bán mạnh, pattern đáng tin cậy"

    elif rvol >= VOLUME_THRESHOLDS['AVG']:
        context = VolumeContext.AVERAGE
        confidence_modifier = 0.0

        interpretation = "Volume trung bình - Pattern cần theo dõi thêm"

    else:
        context = VolumeContext.LOW
        confidence_modifier = -0.5

        if candle_pattern:
            interpretation = f"{candle_pattern} với volume thấp - Cần chờ confirmation"
        else:
            interpretation = "Volume thấp - Tín hiệu yếu, có thể là false signal"

    return VolumeAnalysis(
        context=context,
        rvol=rvol,
        interpretation=interpretation,
        confidence_modifier=confidence_modifier
    )


# Pattern + Volume interpretation matrix
PATTERN_VOLUME_INTERPRETATION = {
    # Bullish patterns
    ('ENGULFING', 'HIGH'): 'Đảo chiều cực mạnh - Volume cao xác nhận buyers áp đảo',
    ('ENGULFING', 'AVG'): 'Đảo chiều - Cần theo dõi phiên sau',
    ('ENGULFING', 'LOW'): 'Tín hiệu yếu - Chờ volume confirmation',

    ('HAMMER', 'HIGH'): 'Từ chối giảm giá mạnh - Volume cao = buyers vào mạnh ở đáy',
    ('HAMMER', 'AVG'): 'Có thể đảo chiều - Volume chưa confirm',
    ('HAMMER', 'LOW'): 'Hammer yếu - Có thể chỉ là nghỉ ngơi tạm thời',

    ('MORNING_STAR', 'HIGH'): 'Đảo chiều 3 nến hoàn hảo - High conviction BUY',
    ('MORNING_STAR', 'AVG'): 'Đảo chiều - Entry cẩn thận, đặt stop loss',
    ('MORNING_STAR', 'LOW'): 'Pattern chưa hoàn chỉnh - Chờ thêm signals',

    ('DOJI', 'HIGH'): 'Indecision với volume cao - Có thể đảo chiều, chờ nến sau',
    ('DOJI', 'AVG'): 'Doji thông thường - Market đang cân bằng',
    ('DOJI', 'LOW'): 'Doji volume thấp - Không có ý nghĩa, bỏ qua',

    # Bearish patterns
    ('EVENING_STAR', 'HIGH'): 'Đảo chiều giảm mạnh - Sellers kiểm soát với volume lớn',
    ('EVENING_STAR', 'AVG'): 'Cảnh báo đảo chiều - Cân nhắc giảm position',
    ('EVENING_STAR', 'LOW'): 'Tín hiệu yếu - Có thể chỉ là correction nhẹ',

    ('SHOOTING_STAR', 'HIGH'): 'Từ chối tăng giá mạnh - Volume xác nhận áp lực bán',
    ('SHOOTING_STAR', 'AVG'): 'Có thể đảo chiều - Theo dõi',
    ('SHOOTING_STAR', 'LOW'): 'Không đáng tin - Volume không confirm',
}


def get_pattern_volume_interpretation(pattern: str, volume_context: str) -> str:
    """Get specific interpretation for pattern + volume combination"""
    key = (pattern.upper(), volume_context.upper())
    return PATTERN_VOLUME_INTERPRETATION.get(
        key,
        f"{pattern} với volume {volume_context}"
    )
```

### 2.4 Confidence Score Calculation (NEW)

Điểm số tổng hợp để đánh giá độ tin cậy của signal:

```python
# File: PROCESSORS/technical/indicators/confidence_score.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class ConfidenceScore:
    score: int           # 0-100
    components: dict     # Breakdown of score components
    interpretation: str  # Vietnamese description

# Pattern reliability scores
PATTERN_RELIABILITY = {
    # 5-star patterns (strongest)
    'MORNING_STAR': 5, 'EVENING_STAR': 5,
    'THREE_WHITE_SOLDIERS': 5, 'THREE_BLACK_CROWS': 5,

    # 4-star patterns
    'ENGULFING': 4, 'ENGULFING_BEARISH': 4,
    'MARUBOZU': 4,

    # 3-star patterns
    'HAMMER': 3, 'SHOOTING_STAR': 3,
    'PIERCING': 3, 'DARK_CLOUD': 3,
    'DOJI_DRAGONFLY': 3, 'DOJI_GRAVESTONE': 3,

    # 2-star patterns
    'HARAMI': 2, 'HARAMI_BEARISH': 2,
    'INVERTED_HAMMER': 2, 'HANGING_MAN': 2,
    'TWEEZER_BOTTOM': 2,

    # 1-star patterns
    'DOJI': 1,
}

# Chart pattern weights
CHART_PATTERN_WEIGHT = {
    'DOUBLE_BOTTOM': 20, 'DOUBLE_TOP': 20,
    'HEAD_SHOULDERS': 25, 'INV_HEAD_SHOULDERS': 25,
    'CUP_HANDLE': 20,
    'FLAG_BULL': 15, 'FLAG_BEAR': 15,
    'TRIANGLE_ASC': 12, 'TRIANGLE_DESC': 12,
}


def calculate_confidence_score(
    ema_signal: str,
    candle_pattern: Optional[str],
    candle_signal: str,
    chart_pattern: Optional[str],
    chart_signal: str,
    rvol: float,
    sector_rank: int,
    price_vs_ma20: float = None,  # % above/below MA20
    price_vs_ma50: float = None   # % above/below MA50
) -> ConfidenceScore:
    """
    Calculate comprehensive confidence score (0-100)

    Components:
    - Pattern reliability: 0-25 points
    - Volume context: 0-20 points
    - Chart pattern: 0-25 points
    - Sector rank: 0-15 points
    - Trend alignment: 0-15 points

    Returns:
        ConfidenceScore with score, stars, and breakdown
    """
    components = {}
    total_score = 0

    # 1. Candlestick Pattern Reliability (0-25 points)
    if candle_pattern:
        reliability = PATTERN_RELIABILITY.get(candle_pattern.upper(), 1)
        pattern_score = reliability * 5  # 1-5 stars → 5-25 points
        components['candle_pattern'] = pattern_score
        total_score += pattern_score
    else:
        components['candle_pattern'] = 0

    # 2. Volume Context (0-20 points)
    if rvol >= 2.0:
        vol_score = 20  # Exceptional volume
    elif rvol >= 1.5:
        vol_score = 15  # High volume
    elif rvol >= 1.0:
        vol_score = 10  # Above average
    elif rvol >= 0.8:
        vol_score = 5   # Normal
    else:
        vol_score = 0   # Low volume = no confidence boost

    components['volume'] = vol_score
    total_score += vol_score

    # 3. Chart Pattern (0-25 points)
    if chart_pattern:
        chart_score = CHART_PATTERN_WEIGHT.get(chart_pattern.upper(), 10)
        components['chart_pattern'] = chart_score
        total_score += chart_score
    else:
        components['chart_pattern'] = 0

    # 4. Sector Rank (0-15 points)
    # Top 5 sectors = full points for bullish, 0 for bearish
    if candle_signal == 'BULLISH':
        if sector_rank <= 3:
            sector_score = 15
        elif sector_rank <= 5:
            sector_score = 12
        elif sector_rank <= 10:
            sector_score = 8
        else:
            sector_score = 3
    elif candle_signal == 'BEARISH':
        if sector_rank >= 15:
            sector_score = 15  # Weak sector confirms bearish
        elif sector_rank >= 10:
            sector_score = 10
        else:
            sector_score = 5
    else:
        sector_score = 7  # Neutral

    components['sector_rank'] = sector_score
    total_score += sector_score

    # 5. Trend Alignment (0-15 points)
    trend_score = 0
    if price_vs_ma20 is not None and price_vs_ma50 is not None:
        if candle_signal == 'BULLISH':
            if price_vs_ma20 > 0 and price_vs_ma50 > 0:
                trend_score = 15  # Above both MAs = uptrend
            elif price_vs_ma20 > 0:
                trend_score = 10  # Above MA20 only
            elif price_vs_ma50 > 0:
                trend_score = 5   # Above MA50 only
        elif candle_signal == 'BEARISH':
            if price_vs_ma20 < 0 and price_vs_ma50 < 0:
                trend_score = 15  # Below both MAs = downtrend
            elif price_vs_ma20 < 0:
                trend_score = 10
            elif price_vs_ma50 < 0:
                trend_score = 5

    components['trend_alignment'] = trend_score
    total_score += trend_score

    # Interpretation (Vietnamese)
    if total_score >= 80:
        interpretation = "Tín hiệu rất mạnh"
    elif total_score >= 60:
        interpretation = "Tín hiệu tốt"
    elif total_score >= 40:
        interpretation = "Cần theo dõi thêm"
    elif total_score >= 20:
        interpretation = "Tín hiệu yếu"
    else:
        interpretation = "Bỏ qua"

    return ConfidenceScore(
        score=total_score,
        components=components,
        interpretation=interpretation
    )
```

### 2.5 Signal Action Determination (UPDATED)

Combine all signals with volume context and confidence:

```python
# File: PROCESSORS/technical/indicators/signal_action.py

from .volume_context import analyze_volume_context, VolumeContext, VOLUME_DISPLAY
from .confidence_score import calculate_confidence_score

def determine_action(
    ema_signal: str,
    candle_pattern: str,
    candle_signal: str,
    chart_pattern: str,
    chart_signal: str,
    rvol: float,
    sector_rank: int,
    price_vs_ma20: float = None,
    price_vs_ma50: float = None
) -> tuple[str, str, int, str]:
    """
    Determine trading action based on multiple signals

    Returns:
        (action, reasoning, score, volume_context) tuple
    """
    bullish_points = 0
    bearish_points = 0
    reasons = []

    # Analyze volume context
    vol_analysis = analyze_volume_context(rvol, candle_pattern)

    # EMA signal (2 points)
    if ema_signal in ['EMA_CROSS_UP', 'BREAKOUT']:
        bullish_points += 2
        reasons.append(f"EMA/Breakout tăng")
    elif ema_signal in ['EMA_CROSS_DOWN', 'BREAKDOWN']:
        bearish_points += 2
        reasons.append(f"EMA/Breakdown giảm")

    # Candlestick pattern (1-3 points based on reliability + volume)
    if candle_signal == 'BULLISH':
        base_points = 2 if candle_pattern in ['MORNING_STAR', 'THREE_WHITE_SOLDIERS', 'ENGULFING'] else 1
        # Volume modifier: +1 for HIGH, 0 for AVG, -0.5 for LOW
        vol_modifier = 1 if vol_analysis.context == VolumeContext.HIGH else (0 if vol_analysis.context == VolumeContext.AVERAGE else -0.5)
        points = max(0.5, base_points + vol_modifier)
        bullish_points += points
        reasons.append(f"Nến {candle_pattern} ({VOLUME_DISPLAY[vol_analysis.context.value]})")
    elif candle_signal == 'BEARISH':
        base_points = 2 if candle_pattern in ['EVENING_STAR', 'THREE_BLACK_CROWS', 'ENGULFING_BEARISH'] else 1
        vol_modifier = 1 if vol_analysis.context == VolumeContext.HIGH else (0 if vol_analysis.context == VolumeContext.AVERAGE else -0.5)
        points = max(0.5, base_points + vol_modifier)
        bearish_points += points
        reasons.append(f"Nến {candle_pattern} ({VOLUME_DISPLAY[vol_analysis.context.value]})")

    # Chart pattern (3 points - strong signal)
    if chart_signal == 'BULLISH':
        bullish_points += 3
        reasons.append(f"Chart: {chart_pattern}")
    elif chart_signal == 'BEARISH':
        bearish_points += 3
        reasons.append(f"Chart: {chart_pattern}")

    # Volume confirmation bonus (only for HIGH volume)
    if vol_analysis.context == VolumeContext.HIGH:
        if bullish_points > bearish_points:
            bullish_points += 1
            reasons.append("Vol HIGH confirm")
        elif bearish_points > bullish_points:
            bearish_points += 1
            reasons.append("Vol HIGH confirm")

    # Sector rank bonus (1 point)
    if sector_rank <= 5 and bullish_points > bearish_points:
        bullish_points += 1
        reasons.append(f"Sector top {sector_rank}")
    elif sector_rank >= 15 and bearish_points > bullish_points:
        bearish_points += 1
        reasons.append(f"Sector yếu #{sector_rank}")

    # Calculate confidence score
    confidence = calculate_confidence_score(
        ema_signal, candle_pattern, candle_signal,
        chart_pattern, chart_signal, rvol, sector_rank,
        price_vs_ma20, price_vs_ma50
    )

    # Determine action based on points AND confidence
    net_score = bullish_points - bearish_points

    if net_score >= 3 and confidence.score >= 50:
        action = "🟢 MUA"
    elif net_score <= -3 and confidence.score >= 50:
        action = "🔴 BÁN"
    else:
        action = "🟡 CHỜ"

    return (
        action,
        "; ".join(reasons),
        confidence.score,
        vol_analysis.context.value
    )


# Pattern display helpers

CANDLE_PATTERN_DISPLAY = {
    'ENGULFING': '🔼 Engulfing',
    'HAMMER': '🔼 Hammer',
    'MORNING_STAR': '🔼 Morning Star',
    'PIERCING': '🔼 Piercing',
    'MARUBOZU': '🔼 Marubozu',
    'THREE_WHITE_SOLDIERS': '🔼 3 White Soldiers',
    'HARAMI': '🔼 Harami',
    'INVERTED_HAMMER': '🔼 Inv. Hammer',
    'DOJI_DRAGONFLY': '🔼 Dragonfly Doji',
    'ENGULFING_BEARISH': '🔽 Engulfing',
    'HANGING_MAN': '🔽 Hanging Man',
    'EVENING_STAR': '🔽 Evening Star',
    'SHOOTING_STAR': '🔽 Shooting Star',
    'DARK_CLOUD': '🔽 Dark Cloud',
    'THREE_BLACK_CROWS': '🔽 3 Black Crows',
    'DOJI_GRAVESTONE': '🔽 Gravestone Doji',
    'DOJI': '⚪ Doji',
}

def format_candle_pattern(pattern: str, signal: str) -> str:
    """Format candlestick pattern for display"""
    if not pattern:
        return "-"

    display = CANDLE_PATTERN_DISPLAY.get(pattern, pattern)
    if not display.startswith(('🔼', '🔽', '⚪')):
        prefix = '🔼' if signal == 'BULLISH' else '🔽' if signal == 'BEARISH' else '⚪'
        display = f"{prefix} {pattern}"

    return display
```

---

## 3. Implementation

### 3.1 Stock Scanner Component

```python
# File: WEBAPP/pages/technical/components/stock_scanner.py

import streamlit as st
import pandas as pd
from ..services.ta_dashboard_service import TADashboardService
from PROCESSORS.technical.indicators.signal_action import (
    determine_action, format_candle_pattern, CANDLE_PATTERN_DISPLAY
)
from PROCESSORS.technical.indicators.candlestick_patterns import (
    get_pattern_interpretation, ALL_PATTERNS
)
from PROCESSORS.technical.indicators.chart_patterns import CHART_PATTERNS
from PROCESSORS.technical.indicators.volume_context import (
    VOLUME_DISPLAY, get_pattern_volume_interpretation
)
from PROCESSORS.technical.indicators.confidence_score import format_confidence_stars

SIGNAL_COLORS = {
    'EMA_CROSS_UP': '#4CAF50',
    'BREAKOUT': '#2196F3',
    'HIGH_VOL_REV': '#FF9800',
    'MA_CROSSOVER': '#9C27B0',
    'EMA_CROSS_DOWN': '#F44336',
    'BREAKDOWN': '#E91E63'
}

# Pattern filter options
PATTERN_FILTERS = [
    "All Patterns",
    "Bullish Only",
    "Bearish Only",
    "High Reliability (4-5★)",
    "Reversal Patterns",
    "Continuation Patterns"
]

# Volume context filter options
VOLUME_FILTERS = [
    "All Volume",
    "High Volume Only (🔥)",
    "Normal+ Volume",
    "Low Volume Warnings"
]


def render_stock_scanner():
    """Render Stock Scanner tab with pattern recognition"""

    service = TADashboardService()

    # ============ QUICK FILTERS (NEW) ============
    st.markdown("### 🔍 Quick Filters")

    qcol1, qcol2, qcol3 = st.columns([2, 1.5, 0.5])

    with qcol1:
        search_symbols = st.text_input(
            "Nhập mã cổ phiếu",
            placeholder="VIC, ACB, FPT (phân cách bằng dấu phẩy)",
            key="scanner_quick_search",
            help="Nhập 1 hoặc nhiều mã, phân cách bằng dấu phẩy"
        )

    with qcol2:
        sectors = service.get_sector_list()
        quick_sector = st.selectbox(
            "Chọn ngành",
            ["-- Chọn ngành --"] + sectors,
            key="scanner_quick_sector"
        )

    with qcol3:
        view_all_sector = st.checkbox(
            "Xem tất cả CP trong ngành",
            key="view_all_sector",
            help="Bỏ filter signal, hiện tất cả CP trong ngành"
        )

    st.markdown("---")

    # ============ ADVANCED FILTERS ============
    with st.expander("⚙️ Advanced Filters", expanded=False):
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            signal_type = st.selectbox(
                "Signal Type",
                ["All", "EMA_CROSS_UP", "BREAKOUT", "HIGH_VOL_REV", "MA_CROSSOVER",
                 "EMA_CROSS_DOWN", "BREAKDOWN"],
                key="scanner_signal_type"
            )

        with col2:
            pattern_filter = st.selectbox(
                "Pattern Filter",
                PATTERN_FILTERS,
                key="scanner_pattern_filter"
            )

        with col3:
            volume_filter = st.selectbox(
                "Volume Context",
                VOLUME_FILTERS,
                key="scanner_volume_filter"
            )

        with col4:
            min_rvol = st.number_input(
                "Min RVOL",
                min_value=0.0,
                max_value=3.0,
                value=0.8,
                step=0.1,
                key="scanner_rvol"
            )

        with col5:
            min_value = st.number_input(
                "Min Avg Value (tỷ)",
                min_value=0.0,
                max_value=50.0,
                value=5.0,
                step=1.0,
                key="scanner_min_value"
            )

        with col6:
            min_score = st.slider(
                "Min Score",
                min_value=0,
                max_value=100,
                value=0,
                key="scanner_min_score"
            )

    # ============ DETERMINE FILTER MODE ============
    filter_mode = "normal"
    symbols_list = None
    sector_filter = None

    # Priority 1: Quick search by symbols
    if search_symbols and search_symbols.strip():
        filter_mode = "symbols"
        symbols_list = [s.strip().upper() for s in search_symbols.split(',') if s.strip()]

    # Priority 2: View all sector
    elif quick_sector != "-- Chọn ngành --":
        if view_all_sector:
            filter_mode = "sector_all"
            sector_filter = quick_sector
        else:
            filter_mode = "sector_signals"
            sector_filter = quick_sector

    # ============ GET DATA ============
    if filter_mode == "symbols":
        # Search specific symbols - show all info regardless of signals
        signals = service.get_stock_scanner_by_symbols(symbols_list)
        st.info(f"🔍 Tìm thấy {len(signals) if signals is not None else 0} / {len(symbols_list)} mã")

    elif filter_mode == "sector_all":
        # Show all stocks in sector with their current status
        signals = service.get_sector_stocks_status(sector_filter)
        st.info(f"📊 Ngành {sector_filter}: {len(signals) if signals is not None else 0} cổ phiếu")

    elif filter_mode == "sector_signals":
        # Show only signals from sector
        signals = service.get_signals_with_patterns(
            signal_type=None if signal_type == "All" else signal_type,
            sector=sector_filter,
            pattern_filter=pattern_filter,
            volume_filter=volume_filter,
            min_rvol=min_rvol,
            min_avg_value=min_value * 1e9,
            min_score=min_score
        )
    else:
        # Normal mode - all signals with filters
        signals = service.get_signals_with_patterns(
            signal_type=None if signal_type == "All" else signal_type,
            sector=None,
            pattern_filter=pattern_filter,
            volume_filter=volume_filter,
            min_rvol=min_rvol,
            min_avg_value=min_value * 1e9,
            min_score=min_score
        )

    # ============ RENDER RESULTS ============
    if signals is not None and not signals.empty:
        # Sector view mode
        if filter_mode in ["sector_all", "sector_signals"]:
            render_sector_view_mode(signals, sector_filter)
            st.markdown("---")

        # Main signal table
        render_signal_table_with_patterns(signals)

        # Signal summary
        st.markdown("---")
        render_signal_summary(signals)

        # Pattern interpretation panel
        st.markdown("---")
        render_pattern_interpretation(signals)
    else:
        st.info("Không có signals phù hợp với bộ lọc. Điều chỉnh bộ lọc hoặc kiểm tra data pipeline.")


def render_sector_view_mode(signals: pd.DataFrame, sector: str):
    """Render sector overview with stock cards"""

    st.markdown(f"### 📊 Sector View: {sector}")

    # Calculate sector stats
    total_stocks = len(signals)
    avg_score = signals['score'].mean() if 'score' in signals.columns else 0

    buy_count = len(signals[signals['action'].str.contains('BUY', na=False)])
    sell_count = len(signals[signals['action'].str.contains('SELL', na=False)])
    hold_count = total_stocks - buy_count - sell_count

    # Sector summary row
    scol1, scol2, scol3, scol4, scol5 = st.columns(5)
    with scol1:
        st.metric("Tổng CP", total_stocks)
    with scol2:
        st.metric("Điểm TB", f"{avg_score:.0f}")
    with scol3:
        st.metric("🟢 Bullish", buy_count)
    with scol4:
        st.metric("🔴 Bearish", sell_count)
    with scol5:
        st.metric("🟡 Neutral", hold_count)

    # Stock cards grid (compact view)
    st.markdown("**Quick View (sorted by Score)**")

    # Sort by score descending
    sorted_df = signals.sort_values('score', ascending=False)

    # Create compact cards
    cols_per_row = 10
    rows = (len(sorted_df) + cols_per_row - 1) // cols_per_row

    for row in range(min(rows, 3)):  # Max 3 rows
        cols = st.columns(cols_per_row)
        for col_idx, col in enumerate(cols):
            stock_idx = row * cols_per_row + col_idx
            if stock_idx < len(sorted_df):
                stock = sorted_df.iloc[stock_idx]
                symbol = stock['symbol']
                score = stock.get('score', 0)
                action = stock.get('action', 'HOLD')

                # Determine color based on action
                if 'BUY' in str(action):
                    bg_color = '#E8F5E9'
                    text = f"**{symbol}**\n{score:.0f}⭐"
                elif 'SELL' in str(action):
                    bg_color = '#FFEBEE'
                    text = f"**{symbol}**\n{score:.0f}"
                else:
                    bg_color = '#FFF8E1'
                    text = f"{symbol}\n{score:.0f}"

                with col:
                    st.markdown(
                        f"<div style='text-align:center;padding:4px;background:{bg_color};border-radius:4px;font-size:11px'>"
                        f"<b>{symbol}</b><br>{score:.0f}</div>",
                        unsafe_allow_html=True
                    )


def render_signal_table_with_patterns(signals: pd.DataFrame):
    """
    Render COMPACT signal table with inline interpretation

    Layout: Mã | Ngành | Tín hiệu + Giải thích | Điểm | Hành động
    - Gộp candle pattern + volume + chart pattern + interpretation vào 1 cột
    - Bỏ stars (không cần thiết khi đã có điểm số)
    """
    from PROCESSORS.technical.indicators.volume_context import (
        get_pattern_volume_interpretation, VOLUME_DISPLAY
    )

    # Calculate action if not exist
    if 'action' not in signals.columns:
        action_results = signals.apply(
            lambda r: determine_action(
                r.get('signal_type'),
                r.get('candle_pattern'),
                r.get('candle_signal'),
                r.get('chart_pattern'),
                r.get('chart_signal'),
                r.get('rvol', 1.0),
                r.get('sector_rank', 10),
                r.get('price_vs_ma20'),
                r.get('price_vs_ma50')
            ), axis=1
        )
        signals['action'] = action_results.apply(lambda x: x[0])
        signals['score'] = action_results.apply(lambda x: x[2])
        signals['volume_context'] = action_results.apply(lambda x: x[3])

    # Build compact signal description with inline interpretation
    def build_signal_description(row):
        """
        Build 2-line signal description:
        Line 1: Pattern icons + names
        Line 2: → Interpretation
        """
        parts = []

        # Candle pattern with volume icon
        candle = row.get('candle_pattern')
        candle_signal = row.get('candle_signal', '')
        vol_ctx = row.get('volume_context', 'AVG')

        if candle:
            icon = '🔼' if candle_signal == 'BULLISH' else '🔽' if candle_signal == 'BEARISH' else '⚪'
            vol_icon = '🔥' if vol_ctx == 'HIGH' else '📉' if vol_ctx == 'LOW' else ''
            parts.append(f"{icon} {candle} {vol_icon}".strip())

        # Chart pattern
        chart = row.get('chart_pattern')
        if chart:
            parts.append(f"+ {chart}")

        # Line 1: Pattern summary
        line1 = ' '.join(parts) if parts else row.get('signal_type', '-')

        # Line 2: Interpretation
        interpretation = get_pattern_volume_interpretation(
            candle or '', vol_ctx
        ) if candle else ""

        if interpretation:
            return f"{line1}\n→ {interpretation}"
        return line1

    signals['signal_description'] = signals.apply(build_signal_description, axis=1)

    # Prepare compact display columns
    display_df = signals[['symbol', 'sector_code', 'signal_description', 'score', 'action']].copy()
    display_df.columns = ['Mã', 'Ngành', 'Tín hiệu + Giải thích', 'Điểm', 'Hành động']

    # Render with progress bar for score (gauge-like)
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            'Mã': st.column_config.TextColumn(width='small'),
            'Ngành': st.column_config.TextColumn(width='medium'),
            'Tín hiệu + Giải thích': st.column_config.TextColumn(width='large'),
            'Điểm': st.column_config.ProgressColumn(
                "Điểm",
                help="Điểm tin cậy 0-100",
                format="%d",
                min_value=0,
                max_value=100,
            ),
            'Hành động': st.column_config.TextColumn(width='small'),
        }
    )


def render_signal_summary(signals: pd.DataFrame):
    """Render signal count summary with pattern breakdown"""

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Signal Types**")
        signal_counts = signals['signal_type'].value_counts()
        cols = st.columns(min(len(signal_counts) + 1, 5))

        for i, (signal_type, count) in enumerate(signal_counts.items()):
            if i < len(cols) - 1:
                with cols[i]:
                    st.metric(
                        label=signal_type.replace('_', ' '),
                        value=count
                    )

        with cols[-1]:
            st.metric(label="Total", value=len(signals))

    with col2:
        st.markdown("**Action Summary**")
        action_counts = signals['action'].value_counts()
        cols = st.columns(3)

        buy_count = sum(1 for a in signals['action'] if 'BUY' in a)
        sell_count = sum(1 for a in signals['action'] if 'SELL' in a)
        hold_count = sum(1 for a in signals['action'] if 'HOLD' in a)

        with cols[0]:
            st.metric("🟢 BUY", buy_count)
        with cols[1]:
            st.metric("🔴 SELL", sell_count)
        with cols[2]:
            st.metric("🟡 HOLD", hold_count)


def render_pattern_interpretation(signals: pd.DataFrame):
    """Render pattern interpretation panel"""

    st.markdown("### Pattern Interpretation Guide")

    # Get unique patterns from current signals
    candle_patterns = signals['candle_pattern'].dropna().unique().tolist()
    chart_patterns = signals['chart_pattern'].dropna().unique().tolist()

    if not candle_patterns and not chart_patterns:
        st.info("No patterns detected in current signals.")
        return

    col1, col2 = st.columns(2)

    with col1:
        if candle_patterns:
            st.markdown("**🕯️ Candlestick Patterns**")
            for pattern in candle_patterns[:5]:  # Limit to top 5
                pattern_info = ALL_PATTERNS.get(pattern.upper())
                if pattern_info:
                    with st.expander(f"{format_candle_pattern(pattern, pattern_info.signal.value)} - {pattern_info.description_vi}"):
                        st.write(f"**Signal:** {pattern_info.signal.value}")
                        st.write(f"**Reliability:** {'⭐' * pattern_info.reliability}")
                        st.write(f"**Interpretation:** {pattern_info.interpretation}")

    with col2:
        if chart_patterns:
            st.markdown("**📊 Chart Patterns**")
            for pattern in chart_patterns[:5]:
                pattern_info = CHART_PATTERNS.get(pattern)
                if pattern_info:
                    with st.expander(f"{pattern_info.pattern_type.value} - {pattern_info.description_vi}"):
                        st.write(f"**Signal:** {pattern_info.signal}")
                        st.write(f"**Interpretation:** {pattern_info.interpretation}")
                        st.write(f"**Target:** {pattern_info.target_calculation}")
```

### 2.2 Trading Lists Component

```python
# File: WEBAPP/pages/technical/components/trading_lists.py

import streamlit as st
import pandas as pd
from ..services.ta_dashboard_service import TADashboardService

URGENCY_ICONS = {
    'HIGH': '🔴',
    'MEDIUM': '🟡',
    'LOW': '🟢'
}

def render_trading_lists():
    """Render Trading Lists tab"""

    service = TADashboardService()
    market_state = service.get_market_state()

    # ============ PORTFOLIO CONFIG ============
    st.markdown("### Portfolio Settings")

    col1, col2, col3 = st.columns(3)

    with col1:
        capital = st.number_input(
            "Capital (VND)",
            min_value=100_000_000,
            max_value=100_000_000_000,
            value=1_000_000_000,
            step=100_000_000,
            format="%d",
            key="portfolio_capital"
        )

    with col2:
        risk_pct = st.slider(
            "Risk per Trade (%)",
            min_value=0.5,
            max_value=3.0,
            value=1.0,
            step=0.5,
            key="risk_pct"
        )

    with col3:
        # Show current exposure level
        st.metric(
            "Exposure Level",
            f"{market_state.exposure_level}%",
            delta=market_state.signal
        )

    st.markdown("---")

    # ============ BUY LIST ============
    st.markdown("### 🟢 Buy List (Top 10 Candidates)")

    if market_state.exposure_level == 0:
        st.warning("⚠️ Market in BEARISH regime. No buy signals generated.")
    else:
        buy_list = service.get_buy_list(
            capital=capital,
            risk_pct=risk_pct / 100
        )

        if buy_list is not None and not buy_list.empty:
            render_buy_table(buy_list)
        else:
            st.info("No buy candidates matching criteria today.")

    st.markdown("---")

    # ============ SELL LIST ============
    st.markdown("### 🔴 Sell List (Exit Signals)")

    sell_list = service.get_sell_list()

    if sell_list is not None and not sell_list.empty:
        render_sell_table(sell_list)
    else:
        st.info("No sell signals today.")


def render_buy_table(buy_list: pd.DataFrame):
    """Render buy list with position sizing"""

    display_df = buy_list[[
        'symbol', 'sector_code', 'signal_type',
        'close', 'stop_loss', 'target', 'shares', 'score'
    ]].copy()

    display_df.columns = [
        'Symbol', 'Sector', 'Signal',
        'Entry', 'Stop', 'Target', 'Qty', 'Score'
    ]

    # Format columns
    for col in ['Entry', 'Stop', 'Target']:
        display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}")

    display_df['Qty'] = display_df['Qty'].apply(
        lambda x: f"{x/1000:.1f}K" if x >= 1000 else str(x)
    )
    display_df['Score'] = display_df['Score'].apply(lambda x: f"{x:.0f}")

    # Add rank column
    display_df.insert(0, '#', range(1, len(display_df) + 1))

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Position summary
    total_value = buy_list['position_value'].sum()
    st.caption(f"Total Position Value: {total_value/1e9:.2f} tỷ VND")


def render_sell_table(sell_list: pd.DataFrame):
    """Render sell list with urgency"""

    display_df = sell_list[[
        'symbol', 'entry_price', 'current_price',
        'pnl_pct', 'exit_reason', 'urgency'
    ]].copy()

    display_df.columns = [
        'Symbol', 'Entry', 'Current', 'PnL %', 'Reason', 'Urgency'
    ]

    # Format columns
    for col in ['Entry', 'Current']:
        display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}")

    display_df['PnL %'] = display_df['PnL %'].apply(
        lambda x: f"+{x:.1f}%" if x > 0 else f"{x:.1f}%"
    )

    # Add urgency icons
    display_df['Urgency'] = display_df['Urgency'].apply(
        lambda x: f"{URGENCY_ICONS.get(x, '')} {x}"
    )

    st.dataframe(display_df, use_container_width=True, hide_index=True)
```

---

## 4. Service Methods Required

Add to `TADashboardService`:

```python
# File: WEBAPP/pages/technical/services/ta_dashboard_service.py (additions)

from PROCESSORS.technical.indicators.candlestick_patterns import detect_candlestick_patterns
from PROCESSORS.technical.indicators.chart_patterns import detect_chart_patterns, get_chart_pattern_for_symbol
from PROCESSORS.technical.indicators.signal_action import determine_action

# High reliability patterns for filtering
HIGH_RELIABILITY_PATTERNS = [
    'MORNING_STAR', 'EVENING_STAR', 'THREE_WHITE_SOLDIERS', 'THREE_BLACK_CROWS',
    'ENGULFING', 'ENGULFING_BEARISH', 'MARUBOZU', 'MARUBOZU_BLACK'
]

REVERSAL_PATTERNS = [
    'MORNING_STAR', 'EVENING_STAR', 'HAMMER', 'SHOOTING_STAR',
    'ENGULFING', 'ENGULFING_BEARISH', 'HANGING_MAN', 'INVERTED_HAMMER',
    'DOJI_DRAGONFLY', 'DOJI_GRAVESTONE', 'HARAMI', 'HARAMI_BEARISH',
    'DOUBLE_BOTTOM', 'DOUBLE_TOP', 'HEAD_SHOULDERS', 'INV_HEAD_SHOULDERS'
]

CONTINUATION_PATTERNS = [
    'THREE_WHITE_SOLDIERS', 'THREE_BLACK_CROWS', 'MARUBOZU',
    'FLAG_BULL', 'FLAG_BEAR', 'TRIANGLE_ASC', 'TRIANGLE_DESC',
    'CUP_HANDLE', 'WEDGE_RISING', 'WEDGE_FALLING'
]


class TADashboardService:
    # ... existing methods ...

    def get_sector_list(self) -> list:
        """Get list of sector codes for filter dropdown"""
        sector_breadth = self._load_sector_breadth()
        return sorted(sector_breadth['sector_code'].unique().tolist())

    def get_stock_scanner_by_symbols(self, symbols: list[str]) -> pd.DataFrame:
        """
        Get scanner info for specific symbols (regardless of signals)

        Used for Quick Search filter - shows all requested stocks
        with their current technical status.

        Args:
            symbols: List of stock symbols (e.g., ['VIC', 'ACB', 'FPT'])

        Returns:
            DataFrame with technical status for each symbol
        """
        if not symbols:
            return pd.DataFrame()

        # Load OHLCV data
        ohlcv = self._load_ohlcv_for_patterns()
        if ohlcv.empty:
            return pd.DataFrame()

        # Filter by symbols
        ohlcv = ohlcv[ohlcv['symbol'].isin(symbols)]

        # Get latest row for each symbol
        result = ohlcv.groupby('symbol').last().reset_index()

        # Add sector info
        result = self._add_sector_info(result)

        # Detect patterns
        result = self._add_candlestick_patterns(result, ohlcv)
        result = self._add_chart_patterns(result, ohlcv)

        # Calculate volume context
        result = self._add_volume_context(result)

        # Calculate confidence score and action
        result = self._calculate_action_and_score(result)

        return result

    def get_sector_stocks_status(self, sector: str) -> pd.DataFrame:
        """
        Get technical status for ALL stocks in a sector

        Used for Sector View mode - shows complete sector overview
        with scores for each stock.

        Args:
            sector: Sector code (e.g., 'Ngân hàng')

        Returns:
            DataFrame with all stocks in sector and their scores
        """
        # Get all tickers in sector
        tickers = self._get_sector_tickers(sector)
        if not tickers:
            return pd.DataFrame()

        # Get scanner info for all tickers
        return self.get_stock_scanner_by_symbols(tickers)

    def _get_sector_tickers(self, sector: str) -> list[str]:
        """Get all tickers belonging to a sector"""
        # Use sector registry or metadata
        sector_meta_path = Path("DATA/metadata/sector_industry_registry.json")
        if sector_meta_path.exists():
            import json
            with open(sector_meta_path) as f:
                registry = json.load(f)
            return registry.get('sectors', {}).get(sector, {}).get('tickers', [])

        # Fallback: get from basic_data
        basic_data = pd.read_parquet(self.DATA_ROOT / "basic_data.parquet")
        return basic_data[basic_data['sector_code'] == sector]['symbol'].unique().tolist()

    def _add_sector_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add sector_code and sector_rank to dataframe"""
        # Load sector ranking
        ranking_path = self.DATA_ROOT / "sector_breadth/sector_breadth_daily.parquet"
        if ranking_path.exists():
            ranking = pd.read_parquet(ranking_path)
            # Merge sector rank by sector_code
            df = df.merge(
                ranking[['sector_code', 'rank']].rename(columns={'rank': 'sector_rank'}),
                on='sector_code',
                how='left'
            )
        else:
            df['sector_rank'] = 10  # Default middle rank

        return df

    def _add_volume_context(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume_context column based on RVOL"""
        from PROCESSORS.technical.indicators.volume_context import analyze_volume_context

        def get_context(row):
            rvol = row.get('rvol', 1.0)
            analysis = analyze_volume_context(rvol, row.get('candle_pattern'))
            return analysis.context.value

        df['volume_context'] = df.apply(get_context, axis=1)
        return df

    def _calculate_action_and_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate action, score, stars for each row"""
        from PROCESSORS.technical.indicators.signal_action import determine_action

        def calc_action(row):
            return determine_action(
                row.get('signal_type'),
                row.get('candle_pattern'),
                row.get('candle_signal'),
                row.get('chart_pattern'),
                row.get('chart_signal'),
                row.get('rvol', 1.0),
                row.get('sector_rank', 10),
                row.get('price_vs_ma20'),
                row.get('price_vs_ma50')
            )

        results = df.apply(calc_action, axis=1)
        df['action'] = results.apply(lambda x: x[0])
        df['action_reason'] = results.apply(lambda x: x[1])
        df['score'] = results.apply(lambda x: x[2])
        df['volume_context'] = results.apply(lambda x: x[3])

        return df

    def get_signals_with_patterns(
        self,
        signal_type: str = None,
        sector: str = None,
        pattern_filter: str = "All Patterns",
        volume_filter: str = "All Volume",
        min_rvol: float = 0.8,
        min_avg_value: float = 5e9,
        min_score: int = 0
    ) -> pd.DataFrame:
        """
        Get signals with candlestick and chart pattern detection

        Args:
            signal_type: EMA_CROSS_UP, BREAKOUT, etc.
            sector: Sector code filter
            pattern_filter: Pattern category filter
            volume_filter: Volume context filter (HIGH, AVG, LOW)
            min_rvol: Minimum relative volume
            min_avg_value: Minimum 20-day avg trading value
            min_score: Minimum confidence score (0-100)

        Returns:
            DataFrame with signal + pattern columns
        """
        # Load base signals
        signals = self.get_signals(
            signal_type=signal_type,
            sector=sector,
            min_rvol=min_rvol,
            min_avg_value=min_avg_value
        )

        if signals is None or signals.empty:
            return signals

        # Load OHLCV for pattern detection
        ohlcv = self._load_ohlcv_for_patterns()

        # Detect candlestick patterns
        signals = self._add_candlestick_patterns(signals, ohlcv)

        # Detect chart patterns
        signals = self._add_chart_patterns(signals, ohlcv)

        # Apply pattern filter
        signals = self._apply_pattern_filter(signals, pattern_filter)

        # Calculate action, score, stars, volume_context (updated)
        action_results = signals.apply(
            lambda r: determine_action(
                r.get('signal_type'),
                r.get('candle_pattern'),
                r.get('candle_signal'),
                r.get('chart_pattern'),
                r.get('chart_signal'),
                r.get('rvol', 1.0),
                r.get('sector_rank', 10),
                r.get('price_vs_ma20'),
                r.get('price_vs_ma50')
            ), axis=1
        )

        signals['action'] = action_results.apply(lambda x: x[0])
        signals['action_reason'] = action_results.apply(lambda x: x[1])
        signals['score'] = action_results.apply(lambda x: x[2])
        signals['volume_context'] = action_results.apply(lambda x: x[3])

        # Apply volume filter
        signals = self._apply_volume_filter(signals, volume_filter)

        # Apply min score filter
        if min_score > 0:
            signals = signals[signals['score'] >= min_score]

        return signals.sort_values('score', ascending=False)

    def _apply_volume_filter(
        self,
        signals: pd.DataFrame,
        volume_filter: str
    ) -> pd.DataFrame:
        """Apply volume context filtering"""

        if volume_filter == "All Volume":
            return signals

        elif volume_filter == "High Volume Only (🔥)":
            return signals[signals['volume_context'] == 'HIGH']

        elif volume_filter == "Normal+ Volume":
            return signals[signals['volume_context'].isin(['HIGH', 'AVG'])]

        elif volume_filter == "Low Volume Warnings":
            return signals[signals['volume_context'] == 'LOW']

        return signals

    def _load_ohlcv_for_patterns(self) -> pd.DataFrame:
        """Load recent OHLCV data for pattern detection"""
        path = self.DATA_ROOT / "basic_data.parquet"
        if not path.exists():
            return pd.DataFrame()

        df = pd.read_parquet(path)
        # Keep last 60 days for chart pattern detection
        return df.groupby('symbol').tail(60).reset_index(drop=True)

    def _add_candlestick_patterns(
        self,
        signals: pd.DataFrame,
        ohlcv: pd.DataFrame
    ) -> pd.DataFrame:
        """Add candlestick pattern columns to signals"""

        def detect_for_symbol(symbol):
            symbol_df = ohlcv[ohlcv['symbol'] == symbol]
            if len(symbol_df) < 5:
                return None, None

            detected = detect_candlestick_patterns(symbol_df.tail(5))
            if detected is None or detected.empty:
                return None, None

            last_row = detected.iloc[-1]
            return last_row.get('candle_pattern'), last_row.get('candle_signal')

        patterns = signals['symbol'].apply(detect_for_symbol)
        signals['candle_pattern'] = patterns.apply(lambda x: x[0] if x else None)
        signals['candle_signal'] = patterns.apply(lambda x: x[1] if x else None)

        return signals

    def _add_chart_patterns(
        self,
        signals: pd.DataFrame,
        ohlcv: pd.DataFrame
    ) -> pd.DataFrame:
        """Add chart pattern columns to signals"""

        def detect_for_symbol(symbol):
            result = get_chart_pattern_for_symbol(symbol, ohlcv, lookback=60)
            return result.get('pattern'), result.get('signal')

        patterns = signals['symbol'].apply(detect_for_symbol)
        signals['chart_pattern'] = patterns.apply(lambda x: x[0] if x else None)
        signals['chart_signal'] = patterns.apply(lambda x: x[1] if x else None)

        return signals

    def _apply_pattern_filter(
        self,
        signals: pd.DataFrame,
        pattern_filter: str
    ) -> pd.DataFrame:
        """Apply pattern-based filtering"""

        if pattern_filter == "All Patterns":
            return signals

        elif pattern_filter == "Bullish Only":
            mask = (
                (signals['candle_signal'] == 'BULLISH') |
                (signals['chart_signal'] == 'BULLISH')
            )
            return signals[mask]

        elif pattern_filter == "Bearish Only":
            mask = (
                (signals['candle_signal'] == 'BEARISH') |
                (signals['chart_signal'] == 'BEARISH')
            )
            return signals[mask]

        elif pattern_filter == "High Reliability (4-5★)":
            mask = signals['candle_pattern'].isin(HIGH_RELIABILITY_PATTERNS)
            return signals[mask]

        elif pattern_filter == "Reversal Patterns":
            mask = (
                signals['candle_pattern'].isin(REVERSAL_PATTERNS) |
                signals['chart_pattern'].isin(REVERSAL_PATTERNS)
            )
            return signals[mask]

        elif pattern_filter == "Continuation Patterns":
            mask = (
                signals['candle_pattern'].isin(CONTINUATION_PATTERNS) |
                signals['chart_pattern'].isin(CONTINUATION_PATTERNS)
            )
            return signals[mask]

        return signals

    def get_signals(
        self,
        signal_type: str = None,
        sector: str = None,
        min_rvol: float = 0.8,
        min_avg_value: float = 5e9
    ) -> pd.DataFrame:
        """
        Get filtered signals from combined_latest.parquet

        Filters:
        - signal_type: EMA_CROSS_UP, BREAKOUT, HIGH_VOL_REV, MA_CROSSOVER
        - sector: Sector code
        - min_rvol: Minimum relative volume
        - min_avg_value: Minimum 20-day avg trading value
        """
        path = self.DATA_ROOT / "alerts/daily/combined_latest.parquet"
        if not path.exists():
            return None

        signals = pd.read_parquet(path)

        # Apply filters
        if signal_type:
            signals = signals[signals['signal_type'] == signal_type]

        if sector:
            signals = signals[signals['sector_code'] == sector]

        signals = signals[
            (signals['rvol'] >= min_rvol) &
            (signals['avg_value_20d'] >= min_avg_value)
        ]

        # Calculate score if not exists
        if 'score' not in signals.columns:
            signals['score'] = (
                signals['rvol'].clip(0, 3) * 30 +
                (20 - signals.get('sector_rank', 10).clip(1, 19)) * 3 +
                signals.get('market_cap', 5000).clip(0, 50000) / 1000
            )

        return signals.sort_values('score', ascending=False)

    def get_buy_list(
        self,
        capital: float = 1_000_000_000,
        risk_pct: float = 0.01
    ) -> pd.DataFrame:
        """
        Get top 10 buy candidates with position sizing

        Filters applied:
        1. Market exposure > 0
        2. Sector rank <= 10 (top 50%)
        3. Valid signal with RVOL >= 0.8
        """
        market_state = self.get_market_state()

        if market_state.exposure_level == 0:
            return pd.DataFrame()

        signals = self.get_signals(min_rvol=0.8)

        if signals is None or signals.empty:
            return pd.DataFrame()

        # Filter by sector rank
        sector_ranking = self.get_sector_ranking()
        if sector_ranking is not None:
            top_sectors = sector_ranking[sector_ranking['rank'] <= 10]['sector_code'].tolist()
            signals = signals[signals['sector_code'].isin(top_sectors)]

        # Calculate position sizing
        signals['position_value'] = signals.apply(
            lambda row: self._calculate_position(
                capital, risk_pct, row['close'], row.get('atr', row['close'] * 0.02),
                market_state.exposure_level
            )['position_value'],
            axis=1
        )

        signals['shares'] = signals.apply(
            lambda row: self._calculate_position(
                capital, risk_pct, row['close'], row.get('atr', row['close'] * 0.02),
                market_state.exposure_level
            )['shares'],
            axis=1
        )

        signals['stop_loss'] = signals.apply(
            lambda row: row['close'] - row.get('atr', row['close'] * 0.02) * 1.5,
            axis=1
        )

        signals['target'] = signals.apply(
            lambda row: row['close'] + row.get('atr', row['close'] * 0.02) * 3,
            axis=1
        )

        return signals.nlargest(10, 'score')

    def get_sell_list(self) -> pd.DataFrame:
        """
        Get sell signals from holdings

        Exit conditions:
        - EMA cross down
        - Stop loss hit
        - Market bearish (exposure = 0)
        """
        path = self.DATA_ROOT / "lists/sell_list_daily.parquet"
        if not path.exists():
            # Return empty if no holdings file
            return pd.DataFrame()

        return pd.read_parquet(path)

    def _calculate_position(
        self,
        capital: float,
        risk_pct: float,
        entry_price: float,
        atr: float,
        exposure_level: int
    ) -> dict:
        """Calculate position size based on ATR stop"""
        stop_distance = atr * 1.5
        adjusted_capital = capital * (exposure_level / 100)
        max_risk = adjusted_capital * risk_pct
        shares = int(max_risk / stop_distance) if stop_distance > 0 else 0

        return {
            'shares': shares,
            'position_value': shares * entry_price,
            'stop_loss': entry_price - stop_distance
        }
```

---

## 5. Implementation Checklist

### Pattern Recognition (New)
- [ ] Create `PROCESSORS/technical/indicators/candlestick_patterns.py`
  - [ ] Implement `CandlestickPattern` dataclass
  - [ ] Define `BULLISH_PATTERNS` and `BEARISH_PATTERNS` dictionaries
  - [ ] Implement `detect_candlestick_patterns()` using ta-lib
  - [ ] Implement `get_pattern_interpretation()`
- [ ] Create `PROCESSORS/technical/indicators/chart_patterns.py`
  - [ ] Implement `ChartPattern` dataclass
  - [ ] Define `CHART_PATTERNS` dictionary
  - [ ] Implement `detect_chart_patterns()` using scipy.signal
  - [ ] Implement `get_chart_pattern_for_symbol()`
- [ ] Create `PROCESSORS/technical/indicators/volume_context.py` **(NEW)**
  - [ ] Implement `VolumeContext` enum (HIGH, AVG, LOW)
  - [ ] Implement `VolumeAnalysis` dataclass
  - [ ] Implement `analyze_volume_context()` function
  - [ ] Define `PATTERN_VOLUME_INTERPRETATION` matrix
  - [ ] Implement `get_pattern_volume_interpretation()`
- [ ] Create `PROCESSORS/technical/indicators/confidence_score.py` **(NEW)**
  - [ ] Implement `ConfidenceScore` dataclass (score, components, interpretation)
  - [ ] Define `PATTERN_RELIABILITY` scores
  - [ ] Define `CHART_PATTERN_WEIGHT` scores
  - [ ] Implement `calculate_confidence_score()` with 5 components
- [ ] Create `PROCESSORS/technical/indicators/signal_action.py`
  - [ ] Implement `determine_action()` returning (action, reason, score, volume_context)
  - [ ] Implement `format_candle_pattern()` display helper
  - [ ] Define `CANDLE_PATTERN_DISPLAY` mapping

### Stock Scanner (Updated)
- [ ] Create `WEBAPP/pages/technical/components/stock_scanner.py`
- [ ] Implement Quick Filters section (symbol search, sector dropdown, view all checkbox)
- [ ] Implement `render_stock_scanner()` with 3 filter modes (symbols, sector_all, sector_signals)
- [ ] Implement `render_sector_view_mode()` with compact card grid
- [ ] Implement `render_signal_table_with_patterns()` - compact table với inline interpretation
- [ ] Implement `build_signal_description()` - gộp pattern + volume + chart + giải thích
- [ ] Implement ProgressColumn cho điểm số (gauge-like)
- [ ] Implement `render_signal_summary()` with action breakdown

### Trading Lists (DEFERRED)
- [ ] ~~Create `WEBAPP/pages/technical/components/trading_lists.py`~~
- [ ] ~~Implement `render_trading_lists()`~~
- [ ] ~~Implement `render_buy_table()`~~
- [ ] ~~Implement `render_sell_table()`~~
- **Note:** Deferred until portfolio file optimization is complete

### Service Layer
- [ ] Add `get_sector_list()` method - dropdown options
- [ ] Add `get_signals_with_patterns()` method with volume_filter, min_score params
- [ ] Add `get_stock_scanner_by_symbols()` method **(NEW)**
- [ ] Add `get_sector_stocks_status()` method **(NEW)**
- [ ] Add `_load_ohlcv_for_patterns()` helper
- [ ] Add `_add_candlestick_patterns()` helper
- [ ] Add `_add_chart_patterns()` helper
- [ ] Add `_apply_pattern_filter()` helper
- [ ] Add `_apply_volume_filter()` helper **(NEW)**
- [ ] Add `get_signals()`, ~~`get_buy_list()`~~, ~~`get_sell_list()`~~

### Testing
- [ ] Test candlestick pattern detection with sample OHLCV
- [ ] Test chart pattern detection with sample OHLCV
- [ ] Test volume context analysis
- [ ] Test confidence score calculation (verify 5 components)
- [ ] Test action determination scoring
- [ ] Test symbol search filter
- [ ] Test sector view mode
- [ ] Test with existing parquet files
- [ ] Verify pattern interpretation display

---

## 6. Data Requirements

| Field | Source | Notes |
|-------|--------|-------|
| `signal_type` | combined_latest.parquet | EMA_CROSS_UP, BREAKOUT, etc. |
| `rvol` | calculated | Relative volume (current/avg) |
| `avg_value_20d` | OHLCV | 20-day average trading value |
| `sector_code` | ticker metadata | Sector assignment |
| `sector_rank` | sector_ranking_daily.parquet | IBD-style rank (1-19) |
| `atr` | technical/basic_data.parquet | For position sizing |
| `close` | OHLCV | Current price |
| `price_vs_ma20` | calculated | % above/below MA20 |
| `price_vs_ma50` | calculated | % above/below MA50 |
| `candle_pattern` | calculated (ta-lib) | Detected candlestick pattern |
| `candle_signal` | calculated | BULLISH/BEARISH/NEUTRAL |
| `chart_pattern` | calculated (scipy) | Detected chart pattern |
| `chart_signal` | calculated | BULLISH/BEARISH |
| `volume_context` | calculated | HIGH/AVG/LOW based on RVOL thresholds |
| `score` | calculated | 0-100 confidence score (5 components), displayed as ProgressColumn |
| `action` | calculated | 🟢 MUA / 🔴 BÁN / 🟡 CHỜ |

### Pattern Dependencies

| Library | Usage | Install |
|---------|-------|---------|
| ta-lib | Candlestick pattern detection | `pip install TA-Lib` (requires C library) |
| scipy | Chart pattern peak/trough detection | `pip install scipy` |
| numpy | Array operations | `pip install numpy` |

### Pattern Data Flow

```
OHLCV Data (basic_data.parquet)
       │
       ├──► ta-lib candlestick detection
       │         │
       │         └──► candle_pattern, candle_signal
       │
       └──► scipy peak/trough detection
                 │
                 └──► chart_pattern, chart_signal
                           │
                           ▼
                  determine_action()
                           │
                           └──► action (BUY/SELL/HOLD)
```
