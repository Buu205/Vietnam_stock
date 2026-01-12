# Composite Signal Scoring System

**Version:** 2.1
**Date:** 2025-01-11
**Purpose:** Tính điểm tổng hợp cho tín hiệu giao dịch từ 6 yếu tố
**Target File:** `WEBAPP/pages/technical/services/ta_dashboard_service.py`

---

## Changelog

### v2.1 (2025-01-11)

**Logic Improvements:**

| # | Change | Section | Impact |
|---|--------|---------|--------|
| 1 | Pattern Context Multiplier | §2.3 | Reversal patterns in correct trend context get 1.2x bonus |
| 2 | VSA Conflict Multiplier | §3.8 | Strong conflicts get 0.6x penalty (was just -5 pts) |
| 3 | Fib Range Validation | §5.3 | Skip Fib levels in sideways market (range < 5×ATR) |
| 4 | Sector-Relative RS | §6.3 | Use relative RS change vs sector (not absolute) |
| 5 | Lower Liquidity Thresholds | §7.2 | 50 tỷ = 8 pts (was 100 tỷ), +1 pt for mid-caps |

**UI Implementation (§11):**

| # | Feature | Notes |
|---|---------|-------|
| 1 | Quick Filters | Hướng, Điểm (slider), Thời gian |
| 2 | Advanced Filters | VSA Context, Trend Alignment, RS Rating, GTGD |
| 3 | Accordion Selection | Multiselect max 5 tickers |
| 4 | Score Breakdown Panels | 6-factor bars with colors |
| 5 | Auto-sync Single Stock | 1 ticker selected → populate input |
| 6 | No Emoji Icons | Text symbols only (++/+/=/-/--) |

**Max Score Adjustments:**
- RS Momentum: 3 pts → 2 pts (§6.3)
- Pattern Context: Can exceed 15 pts (capped at 15)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Factor 1: Candlestick Pattern (15 pts)](#2-factor-1-candlestick-pattern-15-pts)
3. [Factor 2: VSA - Volume Spread Analysis (25 pts)](#3-factor-2-vsa---volume-spread-analysis-25-pts)
4. [Factor 3: Trend Alignment (20 pts)](#4-factor-3-trend-alignment-20-pts)
5. [Factor 4: Support/Resistance Proximity (15 pts)](#5-factor-4-supportresistance-proximity-15-pts)
6. [Factor 5: RS Rating (15 pts)](#6-factor-5-rs-rating-15-pts)
7. [Factor 6: Liquidity (10 pts)](#7-factor-6-liquidity-10-pts)
8. [Final Score Calculation](#8-final-score-calculation)
9. [Direction Logic](#9-direction-logic)
10. [Quality Labels & Filters](#10-quality-labels--filters)
11. [Data Sources](#11-data-sources)
12. [Implementation Notes](#12-implementation-notes)

---

## 1. Overview

### 1.1 Mục tiêu

Tạo hệ thống scoring phân hóa rõ ràng giữa các tín hiệu giao dịch, thay vì tất cả đều có điểm 100 hoặc tương tự nhau.

### 1.2 Tổng quan 6 Factors

| Factor | Max Points | Weight | Mô tả |
|--------|------------|--------|-------|
| Candlestick Pattern | 15 | 15% | Độ tin cậy của mẫu hình nến |
| VSA (Volume Spread Analysis) | 25 | 25% | Volume + Spread + Close Position |
| Trend Alignment | 20 | 20% | Signal đi cùng hay ngược trend |
| S/R Proximity | 15 | 15% | Khoảng cách đến Support/Resistance |
| RS Rating | 15 | 15% | Relative Strength (1-99) |
| Liquidity | 10 | 10% | Thanh khoản giao dịch |
| **TOTAL** | **100** | **100%** | |

### 1.3 Expected Score Distribution

| Score Range | Quality | Expected % | Ý nghĩa |
|-------------|---------|------------|---------|
| 90-100 | EXCELLENT | 2-5% | Setup hoàn hảo, tất cả factors aligned |
| 75-89 | GOOD | 10-15% | Đa số factors tốt |
| 60-74 | MODERATE | 25-30% | Setup ổn với vài điểm yếu nhỏ |
| 45-59 | WEAK | 30-35% | Tín hiệu trung bình, mixed |
| 30-44 | POOR | 15-20% | Nhiều yếu tố tiêu cực |
| <30 | AVOID | Filter out | Quá nhiều conflicts |

---

## 2. Factor 1: Candlestick Pattern (15 pts)

### 2.1 Logic

Pattern có win rate cao hơn (dựa trên backtest research) → điểm cao hơn.

### 2.2 Pattern Score Table

```python
PATTERN_SCORES = {
    # S-Tier: Multi-candle, high reliability (15 pts)
    'morning_star': 15,
    'evening_star': 15,
    'three_white_soldiers': 15,
    'three_black_crows': 15,
    
    # A-Tier: Strong reversal (13 pts)
    'engulfing': 13,
    'bullish_engulfing': 13,
    'bearish_engulfing': 13,
    
    # B-Tier: Single candle reversal (10 pts)
    'hammer': 10,
    'inverted_hammer': 10,
    'shooting_star': 10,
    
    # C-Tier: Moderate reliability (8 pts)
    'hanging_man': 8,
    'piercing': 8,
    'dark_cloud': 8,
    'dragonfly_doji': 8,
    'gravestone_doji': 8,
    
    # D-Tier: Weak/Indecision (5 pts)
    'doji': 5,
    'spinning_top': 5,
    
    # No pattern (breakout only, volume spike only)
    'breakout': 7,      # Breakout không có pattern
    'volume_spike': 5,  # Volume spike không có pattern
}
```

### 2.3 Context Multiplier (NEW - v2.1)

Reversal patterns có ý nghĩa khác nhau tùy vào vị trí trong trend:
- Bullish reversal (morning_star, hammer) SAU downtrend → mạnh hơn
- Bearish reversal (evening_star, shooting_star) SAU uptrend → mạnh hơn
- Pattern trong sideways → ít meaningful hơn

```python
# Pattern categories for context adjustment
BULLISH_REVERSAL_PATTERNS = [
    'morning_star', 'hammer', 'bullish_engulfing',
    'inverted_hammer', 'piercing', 'dragonfly_doji'
]
BEARISH_REVERSAL_PATTERNS = [
    'evening_star', 'shooting_star', 'bearish_engulfing',
    'hanging_man', 'dark_cloud', 'gravestone_doji'
]

def get_pattern_context_multiplier(pattern_name: str, trend: str) -> float:
    """
    Adjust pattern score based on trend context.

    Logic:
    - Bullish reversal + STRONG_DOWN/DOWNTREND → 1.2x (perfect reversal setup)
    - Bearish reversal + STRONG_UP/UPTREND → 1.2x (perfect reversal setup)
    - Any pattern + SIDEWAYS → 0.9x (less meaningful)
    - Otherwise → 1.0x (no adjustment)

    Returns:
        Multiplier 0.9 to 1.2
    """
    if not pattern_name:
        return 1.0

    pattern_lower = pattern_name.lower().replace(' ', '_')

    # Bullish reversal patterns
    if pattern_lower in BULLISH_REVERSAL_PATTERNS:
        if trend in ['STRONG_DOWN', 'DOWNTREND']:
            return 1.2  # Perfect context for bullish reversal
        elif trend == 'SIDEWAYS':
            return 0.9  # Less meaningful in sideways

    # Bearish reversal patterns
    if pattern_lower in BEARISH_REVERSAL_PATTERNS:
        if trend in ['STRONG_UP', 'UPTREND']:
            return 1.2  # Perfect context for bearish reversal
        elif trend == 'SIDEWAYS':
            return 0.9

    return 1.0  # No adjustment for continuation patterns
```

### 2.4 Implementation

```python
def get_candlestick_score(pattern_name: str, trend: str = None) -> int:
    """
    Get candlestick pattern score with context adjustment.

    Args:
        pattern_name: Tên pattern (lowercase, underscore)
        trend: Current trend ('STRONG_UP', 'UPTREND', 'SIDEWAYS', 'DOWNTREND', 'STRONG_DOWN')

    Returns:
        Score 0-18 (base 0-15 × multiplier up to 1.2)
    """
    if not pattern_name:
        return 0

    pattern_key = pattern_name.lower().replace(' ', '_')
    base_score = PATTERN_SCORES.get(pattern_key, 5)  # Default 5 nếu không biết

    # Apply context multiplier
    if trend:
        multiplier = get_pattern_context_multiplier(pattern_key, trend)
        adjusted_score = base_score * multiplier
        return min(15, int(adjusted_score))  # Cap at 15

    return base_score
```

---

## 3. Factor 2: VSA - Volume Spread Analysis (25 pts)

### 3.1 Logic

Kết hợp 3 sub-factors của VSA để đánh giá chất lượng price action:
- Volume Ratio (khối lượng so với trung bình)
- Spread Quality (biên độ giá)
- Close Position (vị trí đóng cửa trong bar)

### 3.2 VSA Thresholds

```python
# Volume thresholds (vs 20-day average)
VOL_VERY_HIGH = 2.5    # ≥250% avg
VOL_HIGH = 1.5         # ≥150% avg
VOL_NORMAL_LOW = 1.0   # 100% avg
VOL_LOW = 0.7          # ≤70% avg
VOL_VERY_LOW = 0.5     # ≤50% avg

# Spread thresholds (vs 14-day ATR)
SPREAD_WIDE = 1.3      # ≥130% ATR
SPREAD_NORMAL = 1.0    # 100% ATR
SPREAD_NARROW = 0.7    # ≤70% ATR
SPREAD_VERY_NARROW = 0.5  # ≤50% ATR

# Close position (0 = close at low, 1 = close at high)
CLOSE_HIGH = 0.7       # Upper 30% of bar
CLOSE_MID_HIGH = 0.5   # Middle
CLOSE_MID_LOW = 0.5    # Middle
CLOSE_LOW = 0.3        # Lower 30% of bar
```

### 3.3 Sub-factor 2.1: Volume Score (10 pts max)

```python
def get_volume_score(vol_ratio: float) -> int:
    """
    Score based on volume ratio vs 20-day average.
    
    Args:
        vol_ratio: current_volume / avg_volume_20d
        
    Returns:
        Score 0-10
    """
    if vol_ratio >= 3.0:
        return 10    # Exceptional volume
    elif vol_ratio >= 2.5:
        return 9     # Very strong
    elif vol_ratio >= 2.0:
        return 8     # Strong
    elif vol_ratio >= 1.5:
        return 6     # Good
    elif vol_ratio >= 1.2:
        return 4     # Above average
    elif vol_ratio >= 1.0:
        return 3     # Normal
    elif vol_ratio >= 0.7:
        return 1     # Below average
    else:
        return 0     # Weak - không confirm
```

### 3.4 Sub-factor 2.2: Spread Quality Score (8 pts max)

```python
def get_spread_score(spread_ratio: float, close_position: float, vol_ratio: float) -> int:
    """
    Score based on spread (price range) quality.
    
    Args:
        spread_ratio: (high - low) / ATR_14
        close_position: (close - low) / (high - low), range 0-1
        vol_ratio: current_volume / avg_volume_20d
        
    Returns:
        Score 0-8
    """
    # Wide spread (>1.3x ATR)
    if spread_ratio >= 1.3:
        if close_position >= 0.7:
            return 8    # Wide spread + close high = strong conviction
        elif close_position <= 0.3:
            return 6    # Wide spread + close low = distribution/stopping
        else:
            return 5    # Wide spread + close middle = indecision với volatility
    
    # Narrow spread (<0.7x ATR)
    elif spread_ratio <= 0.7:
        if vol_ratio >= 1.5:
            return 6    # Narrow spread + high vol = effort no result (absorption)
        else:
            return 2    # Narrow spread + low vol = no interest
    
    # Normal spread
    else:
        if close_position >= 0.7:
            return 5    # Normal spread + close high
        elif close_position <= 0.3:
            return 4    # Normal spread + close low
        else:
            return 3    # Normal spread + close middle
```

### 3.5 Sub-factor 2.3: Close Position Alignment Score (7 pts max)

```python
def get_close_alignment_score(close_position: float, signal_direction: str) -> int:
    """
    Score based on close position alignment with signal direction.
    
    Args:
        close_position: (close - low) / (high - low), range 0-1
        signal_direction: 'BUY' or 'SELL'
        
    Returns:
        Score -2 to 7 (can be negative for strong conflict)
    """
    if signal_direction == 'BUY':
        # BULLISH signal muốn close HIGH
        if close_position >= 0.7:
            return 7    # Close high = buyers won (perfect)
        elif close_position >= 0.5:
            return 4    # Close middle = contested
        elif close_position >= 0.3:
            return 1    # Close mid-low = sellers có lực
        else:
            return -2   # Close low = sellers won (conflict!)
    
    else:  # SELL
        # BEARISH signal muốn close LOW
        if close_position <= 0.3:
            return 7    # Close low = sellers won (perfect)
        elif close_position <= 0.5:
            return 4    # Close middle = contested
        elif close_position <= 0.7:
            return 1    # Close mid-high = buyers có lực
        else:
            return -2   # Close high = buyers won (conflict!)
```

### 3.6 VSA Signal Detection & Bonus

```python
# VSA Signal types
VSA_SIGNALS = {
    # Bullish VSA signals
    'stopping_volume': {
        'condition': 'vol HIGH/VERY_HIGH + spread NARROW + close LOW',
        'meaning': 'Smart money absorbing supply',
        'bias': 'BULLISH'
    },
    'demand_coming_in': {
        'condition': 'vol HIGH/VERY_HIGH + spread WIDE + close HIGH',
        'meaning': 'Aggressive buying',
        'bias': 'BULLISH'
    },
    'no_supply': {
        'condition': 'vol LOW/VERY_LOW + spread NARROW + downtrend',
        'meaning': 'Sellers exhausted',
        'bias': 'BULLISH'
    },
    'test_success': {
        'condition': 'vol LOW + down bar + near support',
        'meaning': 'Supply absorbed',
        'bias': 'BULLISH'
    },
    
    # Bearish VSA signals
    'supply_coming_in': {
        'condition': 'vol HIGH/VERY_HIGH + spread WIDE + close LOW',
        'meaning': 'Aggressive selling',
        'bias': 'BEARISH'
    },
    'no_demand': {
        'condition': 'vol LOW/VERY_LOW + spread NARROW + uptrend',
        'meaning': 'Buyers exhausted',
        'bias': 'BEARISH'
    },
    'upthrust': {
        'condition': 'vol HIGH + spread WIDE + close LOW + uptrend',
        'meaning': 'Bull trap',
        'bias': 'BEARISH'
    },
    
    # Neutral
    'effort_no_result': {
        'condition': 'vol HIGH + spread NARROW',
        'meaning': 'Absorption happening',
        'bias': 'NEUTRAL'
    },
}

def detect_vsa_signal(vol_class: str, spread_class: str, close_class: str, 
                       trend: str, price_change_pct: float) -> tuple:
    """
    Detect VSA signal from metrics.
    
    Returns:
        (signal_name, bias) or (None, None)
    """
    # Stopping Volume
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class == 'NARROW' and close_class == 'LOW':
        return ('stopping_volume', 'BULLISH')
    
    # Demand Coming In
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class == 'WIDE' and close_class == 'HIGH':
        return ('demand_coming_in', 'BULLISH')
    
    # Supply Coming In
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class == 'WIDE' and close_class == 'LOW':
        return ('supply_coming_in', 'BEARISH')
    
    # No Supply (in downtrend)
    if vol_class in ['LOW', 'VERY_LOW'] and spread_class == 'NARROW' and trend in ['DOWNTREND', 'STRONG_DOWN']:
        return ('no_supply', 'BULLISH')
    
    # No Demand (in uptrend)
    if vol_class in ['LOW', 'VERY_LOW'] and spread_class == 'NARROW' and trend in ['UPTREND', 'STRONG_UP']:
        return ('no_demand', 'BEARISH')
    
    # Upthrust
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class == 'WIDE' and close_class == 'LOW' and trend in ['UPTREND', 'STRONG_UP']:
        return ('upthrust', 'BEARISH')
    
    # Effort No Result
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class in ['NARROW', 'VERY_NARROW']:
        return ('effort_no_result', 'NEUTRAL')
    
    return (None, None)


def get_vsa_alignment_bonus(vsa_bias: str, signal_direction: str) -> int:
    """
    Bonus/penalty for VSA alignment with signal direction.
    
    Returns:
        -5 to +3
    """
    if vsa_bias is None:
        return 0
    
    if signal_direction == 'BUY':
        if vsa_bias == 'BULLISH':
            return 3     # VSA confirms BUY
        elif vsa_bias == 'BEARISH':
            return -5    # VSA conflicts with BUY
        else:
            return 0     # Neutral
    
    else:  # SELL
        if vsa_bias == 'BEARISH':
            return 3     # VSA confirms SELL
        elif vsa_bias == 'BULLISH':
            return -5    # VSA conflicts with SELL
        else:
            return 0     # Neutral
```

### 3.7 Total VSA Score Calculation

```python
def calculate_vsa_score(vol_ratio: float, spread_ratio: float,
                        close_position: float, signal_direction: str,
                        trend: str, price_change_pct: float) -> dict:
    """
    Calculate total VSA score.

    Returns:
        dict with score breakdown and VSA signal info
    """
    # Classify metrics
    vol_class = classify_volume(vol_ratio)
    spread_class = classify_spread(spread_ratio)
    close_class = classify_close(close_position)

    # Sub-scores
    volume_score = get_volume_score(vol_ratio)                           # 0-10
    spread_score = get_spread_score(spread_ratio, close_position, vol_ratio)  # 0-8
    close_score = get_close_alignment_score(close_position, signal_direction) # -2 to 7

    # VSA signal detection
    vsa_signal, vsa_bias = detect_vsa_signal(vol_class, spread_class, close_class,
                                              trend, price_change_pct)
    vsa_bonus = get_vsa_alignment_bonus(vsa_bias, signal_direction)      # -5 to +3

    # Calculate raw total
    raw_total = volume_score + spread_score + close_score + vsa_bonus

    # NEW (v2.1): Apply conflict multiplier penalty
    # When VSA conflicts with signal direction, apply stronger penalty
    has_conflict = False
    conflict_multiplier = 1.0

    if vsa_bonus <= -4:  # Strong conflict (VSA strongly against signal)
        conflict_multiplier = 0.6  # 40% penalty
        has_conflict = True
    elif vsa_bonus < 0:  # Mild conflict
        conflict_multiplier = 0.8  # 20% penalty
        has_conflict = True

    adjusted_total = raw_total * conflict_multiplier
    total = max(0, min(25, int(adjusted_total)))

    return {
        'vsa_score': total,
        'volume_score': volume_score,
        'spread_score': spread_score,
        'close_score': close_score,
        'vsa_signal': vsa_signal,
        'vsa_bias': vsa_bias,
        'vsa_bonus': vsa_bonus,
        'vol_class': vol_class,
        'spread_class': spread_class,
        'close_class': close_class,
        'has_conflict': has_conflict,           # NEW
        'conflict_multiplier': conflict_multiplier,  # NEW
    }
```

### 3.8 Conflict Multiplier Rationale (NEW - v2.1)

| VSA Bonus | Conflict Level | Multiplier | Example |
|-----------|---------------|------------|---------|
| +3 to +1 | None (aligned) | 1.0x | BUY signal + Bullish VSA |
| 0 | Neutral | 1.0x | No clear VSA signal |
| -1 to -3 | Mild | 0.8x | BUY signal + Slightly bearish VSA |
| -4 to -5 | Strong | 0.6x | BUY signal + Supply Coming In |

**Impact Example:**
- Before: Raw total 18, bonus -5 → 18 - 5 = 13, clip to 13/25
- After: Raw total 18, bonus -5 → (18 - 5) × 0.6 = 7.8, clip to 8/25

Strong conflicts now receive proportionally lower scores, better reflecting the risk.

---

## 4. Factor 3: Trend Alignment (20 pts)

### 4.1 Logic

Signal đi cùng xu hướng → điểm cao, signal ngược xu hướng → điểm thấp.

### 4.2 Trend Classification

```python
def classify_trend(price_vs_sma20: float, price_vs_sma50: float) -> str:
    """
    Classify trend based on price vs SMA positions.
    
    Args:
        price_vs_sma20: (price / SMA20 - 1) * 100 (percentage)
        price_vs_sma50: (price / SMA50 - 1) * 100 (percentage)
        
    Returns:
        Trend label
    """
    sma20 = price_vs_sma20 or 0
    sma50 = price_vs_sma50 or 0
    
    if sma20 > 5 and sma50 > 5:
        return 'STRONG_UP'
    elif sma20 > 2 and sma50 > 2:
        return 'UPTREND'
    elif sma20 < -5 and sma50 < -5:
        return 'STRONG_DOWN'
    elif sma20 < -2 and sma50 < -2:
        return 'DOWNTREND'
    else:
        return 'SIDEWAYS'
```

### 4.3 Trend Alignment Matrix

```python
TREND_ALIGNMENT_MATRIX = {
    # (signal_direction, trend) → score
    
    # BUY signals
    ('BUY', 'STRONG_UP'):   20,   # Perfect alignment
    ('BUY', 'UPTREND'):     17,   # Good alignment
    ('BUY', 'SIDEWAYS'):    12,   # Neutral
    ('BUY', 'DOWNTREND'):    7,   # Counter-trend (risky)
    ('BUY', 'STRONG_DOWN'):  4,   # Strong counter-trend (very risky)
    
    # SELL signals
    ('SELL', 'STRONG_DOWN'): 20,  # Perfect alignment
    ('SELL', 'DOWNTREND'):   17,  # Good alignment
    ('SELL', 'SIDEWAYS'):    12,  # Neutral
    ('SELL', 'UPTREND'):      7,  # Counter-trend
    ('SELL', 'STRONG_UP'):    4,  # Strong counter-trend
    
    # PULLBACK signals (bullish pattern in uptrend but showing weakness)
    ('PULLBACK', 'STRONG_UP'):  15,
    ('PULLBACK', 'UPTREND'):    14,
    ('PULLBACK', 'SIDEWAYS'):   10,
    ('PULLBACK', 'DOWNTREND'):   6,
    ('PULLBACK', 'STRONG_DOWN'): 4,
    
    # BOUNCE signals (bullish pattern in downtrend - counter-trend)
    ('BOUNCE', 'STRONG_UP'):    6,
    ('BOUNCE', 'UPTREND'):      8,
    ('BOUNCE', 'SIDEWAYS'):    10,
    ('BOUNCE', 'DOWNTREND'):   12,
    ('BOUNCE', 'STRONG_DOWN'): 10,  # Risky but can work at extremes
}

def get_trend_score(signal_direction: str, trend: str) -> int:
    """
    Get trend alignment score.
    
    Returns:
        Score 0-20
    """
    return TREND_ALIGNMENT_MATRIX.get((signal_direction, trend), 10)
```

---

## 5. Factor 4: Support/Resistance Proximity (15 pts)

### 5.1 Logic

- BULLISH signal gần support → điểm cao (good entry, clear stop loss)
- BEARISH signal gần resistance → điểm cao
- Risk/Reward ratio tốt → bonus

### 5.2 S/R Level Calculation

```python
def calculate_sr_levels(df: pd.DataFrame, lookback_swing: int = 20,
                        lookback_fib: int = 30) -> dict:
    """
    Calculate Support/Resistance levels with Fib validation.

    Args:
        df: OHLCV DataFrame for single symbol, sorted by date
        lookback_swing: Days for swing high/low
        lookback_fib: Days for Fibonacci range

    Returns:
        dict with support and resistance levels
    """
    recent = df.tail(lookback_fib)
    swing_data = df.tail(lookback_swing)

    # Swing High/Low (always calculated)
    swing_high = swing_data['high'].max()
    swing_low = swing_data['low'].min()

    # Fibonacci from 30d range
    fib_high = recent['high'].max()
    fib_low = recent['low'].min()
    fib_range = fib_high - fib_low

    current_price = df.iloc[-1]['close']

    # NEW (v2.1): Validate if Fib range is meaningful
    # In sideways market, Fib levels cluster and are not useful
    atr_14 = df.tail(14)['high'].subtract(df.tail(14)['low']).mean()  # Simplified ATR

    fib_valid = fib_range >= (atr_14 * 5)  # Fib range should be >= 5x ATR

    supports = []
    resistances = []

    # Always add Swing High/Low (primary levels)
    if swing_low < current_price * 0.995:
        supports.append({
            'price': swing_low,
            'label': 'Swing Low',
            'pct': (swing_low / current_price - 1) * 100,
            'type': 'swing'
        })
    if swing_high > current_price * 1.005:
        resistances.append({
            'price': swing_high,
            'label': 'Swing High',
            'pct': (swing_high / current_price - 1) * 100,
            'type': 'swing'
        })

    # Only add Fib levels if range is meaningful
    if fib_valid:
        fib_236 = fib_low + fib_range * 0.236
        fib_382 = fib_low + fib_range * 0.382
        fib_500 = fib_low + fib_range * 0.500
        fib_618 = fib_low + fib_range * 0.618
        fib_786 = fib_low + fib_range * 0.786

        # Add Fib supports
        for level, label in [(fib_236, 'Fib 23.6%'),
                             (fib_382, 'Fib 38.2%'),
                             (fib_500, 'Fib 50%'),
                             (fib_618, 'Fib 61.8%')]:
            if level < current_price * 0.995:
                pct = (level / current_price - 1) * 100
                supports.append({'price': level, 'label': label, 'pct': pct, 'type': 'fib'})

        # Add Fib resistances
        for level, label in [(fib_618, 'Fib 61.8%'),
                             (fib_786, 'Fib 78.6%'),
                             (fib_high, 'Fib 100%')]:
            if level > current_price * 1.005:
                pct = (level / current_price - 1) * 100
                resistances.append({'price': level, 'label': label, 'pct': pct, 'type': 'fib'})

    # Sort: supports descending (nearest first), resistances ascending
    supports.sort(key=lambda x: x['price'], reverse=True)
    resistances.sort(key=lambda x: x['price'])
    
    return {
        'current_price': current_price,
        'supports': supports[:3],      # Top 3 nearest
        'resistances': resistances[:3],
        'swing_high': swing_high,
        'swing_low': swing_low,
        'fib_valid': fib_valid,        # NEW (v2.1)
        'fib_range': fib_range,        # For debugging
        'atr_threshold': atr_14 * 5,   # For debugging
    }
```

### 5.3 Fib Validation Rationale (NEW - v2.1)

| Market Type | Fib Range | ATR × 5 | fib_valid | S/R Source |
|-------------|-----------|---------|-----------|------------|
| Strong Trend | 10,000 | 1,500 | ✅ True | Swing + Fib |
| Mild Trend | 5,000 | 1,200 | ✅ True | Swing + Fib |
| Sideways | 1,000 | 1,500 | ❌ False | Swing only |

When `fib_valid=False`:
- Only Swing High/Low are used
- Max S/R score reduced from 15 to ~10 (fewer levels to choose from)

### 5.3 Proximity Score

```python
def get_sr_proximity_score(current_price: float, supports: list, 
                           resistances: list, signal_direction: str) -> dict:
    """
    Calculate S/R proximity score.
    
    Returns:
        dict with score and details
    """
    score = 0
    details = {}
    
    # Get nearest levels
    nearest_support = supports[0] if supports else None
    nearest_resistance = resistances[0] if resistances else None
    
    if signal_direction in ['BUY', 'BOUNCE']:
        # BULLISH: want to be NEAR SUPPORT
        if nearest_support:
            distance_pct = abs(nearest_support['pct'])
            
            if distance_pct < 2:
                score = 12    # Very close to support (perfect entry)
            elif distance_pct < 4:
                score = 10    # Close to support
            elif distance_pct < 6:
                score = 7     # Moderate distance
            elif distance_pct < 10:
                score = 4     # Far from support
            else:
                score = 2     # Very far
                
            details['nearest_support'] = nearest_support
            details['distance_to_support'] = distance_pct
        else:
            score = 3  # No support identified
            
    else:  # SELL, PULLBACK
        # BEARISH: want to be NEAR RESISTANCE
        if nearest_resistance:
            distance_pct = abs(nearest_resistance['pct'])
            
            if distance_pct < 2:
                score = 12
            elif distance_pct < 4:
                score = 10
            elif distance_pct < 6:
                score = 7
            elif distance_pct < 10:
                score = 4
            else:
                score = 2
                
            details['nearest_resistance'] = nearest_resistance
            details['distance_to_resistance'] = distance_pct
        else:
            score = 3
    
    details['base_score'] = score
    return {'score': score, 'details': details}
```

### 5.4 Risk/Reward Bonus

```python
def get_rr_bonus(current_price: float, nearest_support: dict, 
                 nearest_resistance: dict, signal_direction: str) -> int:
    """
    Bonus based on Risk/Reward ratio.
    
    Returns:
        Bonus -3 to +3
    """
    if not nearest_support or not nearest_resistance:
        return 0
    
    support_price = nearest_support['price']
    resistance_price = nearest_resistance['price']
    
    if signal_direction in ['BUY', 'BOUNCE']:
        # Risk = distance to support, Reward = distance to resistance
        risk = current_price - support_price
        reward = resistance_price - current_price
    else:
        # Risk = distance to resistance, Reward = distance to support
        risk = resistance_price - current_price
        reward = current_price - support_price
    
    if risk <= 0:
        return 0
    
    rr_ratio = reward / risk
    
    if rr_ratio >= 3.0:
        return 3     # Excellent R:R
    elif rr_ratio >= 2.0:
        return 2     # Good R:R
    elif rr_ratio >= 1.5:
        return 1     # Acceptable R:R
    elif rr_ratio >= 1.0:
        return 0     # Neutral
    else:
        return -3    # Poor R:R (risk > reward)
```

### 5.5 Total S/R Score

```python
def calculate_sr_score(df: pd.DataFrame, signal_direction: str) -> dict:
    """
    Calculate total S/R factor score.
    
    Returns:
        dict with score (0-15) and details
    """
    # Get S/R levels
    sr_levels = calculate_sr_levels(df)
    
    # Proximity score (0-12)
    proximity_result = get_sr_proximity_score(
        sr_levels['current_price'],
        sr_levels['supports'],
        sr_levels['resistances'],
        signal_direction
    )
    
    # R:R bonus (-3 to +3)
    rr_bonus = get_rr_bonus(
        sr_levels['current_price'],
        sr_levels['supports'][0] if sr_levels['supports'] else None,
        sr_levels['resistances'][0] if sr_levels['resistances'] else None,
        signal_direction
    )
    
    # Total (clip to 0-15)
    total = max(0, min(15, proximity_result['score'] + rr_bonus))
    
    return {
        'sr_score': total,
        'proximity_score': proximity_result['score'],
        'rr_bonus': rr_bonus,
        'supports': sr_levels['supports'],
        'resistances': sr_levels['resistances'],
        'details': proximity_result['details']
    }
```

---

## 6. Factor 5: RS Rating (15 pts)

### 6.1 Logic

RS Rating (1-99) đã là percentile ranking, stock mạnh hơn thị trường sẽ có RS cao.

### 6.2 RS Rating Score (10 pts)

```python
def get_rs_base_score(rs_rating: int) -> int:
    """
    Convert RS Rating (1-99) to base score (0-10).
    
    Args:
        rs_rating: RS Rating from 1-99
        
    Returns:
        Score 0-10
    """
    if rs_rating >= 90:
        return 10    # Top 10% - Leaders
    elif rs_rating >= 80:
        return 9     # Top 20%
    elif rs_rating >= 70:
        return 8     # Top 30%
    elif rs_rating >= 60:
        return 7     # Above average
    elif rs_rating >= 50:
        return 5     # Average
    elif rs_rating >= 40:
        return 4     # Below average
    elif rs_rating >= 30:
        return 3     # Weak
    elif rs_rating >= 20:
        return 2     # Very weak
    else:
        return 1     # Laggards (bottom 20%)
```

### 6.3 RS Momentum Score (2 pts) - UPDATED v2.1

**Change:** Reduced max score from 3 to 2, use RELATIVE RS change instead of absolute.

**Rationale:** Absolute RS change can be noise from sector rotation or market-wide moves.
Stock RS +12 when sector RS +10 is only +2 relative outperformance.

```python
def get_rs_momentum_score(
    rs_rating_today: int,
    rs_rating_5d_ago: int,
    sector_rs_today: int = None,      # NEW (v2.1)
    sector_rs_5d_ago: int = None       # NEW (v2.1)
) -> int:
    """
    Score based on RELATIVE RS momentum (stock vs sector).

    Returns:
        Score -1 to +2 (was +3)
    """
    if rs_rating_5d_ago is None or rs_rating_5d_ago == 0:
        return 0

    # Stock RS change
    stock_rs_change = rs_rating_today - rs_rating_5d_ago

    # If sector RS available, use relative change
    if sector_rs_today is not None and sector_rs_5d_ago is not None:
        sector_rs_change = sector_rs_today - sector_rs_5d_ago
        relative_rs_change = stock_rs_change - sector_rs_change
    else:
        # Fallback: Use absolute change but with lower scores
        relative_rs_change = stock_rs_change

    # Score based on RELATIVE change
    if relative_rs_change >= 8:
        return 2     # Truly outperforming sector
    elif relative_rs_change >= 4:
        return 1     # Slightly outperforming
    elif relative_rs_change >= 0:
        return 0     # In-line with sector
    else:
        return -1    # Underperforming sector
```

### 6.3.1 RS Momentum Examples (NEW)

| Stock RS Change | Sector RS Change | Relative | Score | Interpretation |
|-----------------|------------------|----------|-------|----------------|
| +12 | +10 | +2 | 0 | In-line with sector |
| +12 | +2 | +10 | +2 | True outperformer |
| +5 | +8 | -3 | -1 | Underperforming sector |
| +5 | 0 | +5 | +1 | Slightly outperforming |

### 6.4 RS-Signal Alignment Score (2 pts)

```python
def get_rs_alignment_score(signal_direction: str, rs_rating: int) -> int:
    """
    Score based on RS alignment with signal direction.
    
    Logic:
    - BUY signal + high RS = good (buying strength)
    - BUY signal + low RS = risky (catching falling knife)
    - SELL signal + low RS = good (selling weakness)
    - SELL signal + high RS = risky (shorting leader)
    
    Returns:
        Score -2 to +2
    """
    if signal_direction in ['BUY', 'BOUNCE']:
        if rs_rating >= 70:
            return 2     # Buying strength - aligned
        elif rs_rating >= 50:
            return 1     # Neutral
        elif rs_rating >= 30:
            return 0     # Buying weakness - risky
        else:
            return -2    # Catching falling knife
    
    else:  # SELL, PULLBACK
        if rs_rating <= 30:
            return 2     # Selling weakness - aligned
        elif rs_rating <= 50:
            return 1     # Neutral
        elif rs_rating <= 70:
            return 0     # Selling strength - risky
        else:
            return -2    # Shorting leader - very risky
```

### 6.5 Total RS Score

```python
def calculate_rs_score(rs_rating: int, rs_rating_5d_ago: int, 
                       signal_direction: str) -> dict:
    """
    Calculate total RS factor score.
    
    Returns:
        dict with score (0-15) and components
    """
    # Base score from RS Rating (0-10)
    base_score = get_rs_base_score(rs_rating)
    
    # Momentum score (-1 to +3)
    momentum_score = get_rs_momentum_score(rs_rating, rs_rating_5d_ago)
    
    # Alignment score (-2 to +2)
    alignment_score = get_rs_alignment_score(signal_direction, rs_rating)
    
    # Total (clip to 0-15)
    total = max(0, min(15, base_score + momentum_score + alignment_score))
    
    return {
        'rs_score': total,
        'base_score': base_score,
        'momentum_score': momentum_score,
        'alignment_score': alignment_score,
        'rs_rating': rs_rating,
        'rs_change_5d': rs_rating - rs_rating_5d_ago if rs_rating_5d_ago else None,
    }
```

---

## 7. Factor 6: Liquidity (10 pts)

### 7.1 Logic

Stock có thanh khoản cao → dễ vào/ra position → an toàn hơn.

### 7.2 Trading Value Score (8 pts) - UPDATED v2.1

**Change:** Lowered thresholds to not over-penalize mid-cap stocks.

**Rationale:** 20 tỷ GTGD đủ cho retail trader (position < 1 tỷ).
Old thresholds favored VN30 too much.

```python
def get_trading_value_score(trading_value: float) -> int:
    """
    Score based on trading value (VND).

    Args:
        trading_value: close * volume (VND)

    Returns:
        Score 0-8

    v2.1 Changes:
    - 50 tỷ now scores 8 (was 100 tỷ)
    - 15 tỷ now scores 6 (was 20 tỷ)
    - Overall: +1 point for mid-cap stocks
    """
    # Convert to billions for easier reading
    tv_billion = trading_value / 1e9

    # v2.1: Lowered thresholds
    if tv_billion >= 50:
        return 8     # Very liquid (was 100)
    elif tv_billion >= 30:
        return 7     # Liquid (was 50)
    elif tv_billion >= 15:
        return 6     # Good (was 20)
    elif tv_billion >= 8:
        return 5     # Acceptable (was 10)
    elif tv_billion >= 4:
        return 4     # Tradeable (was 5)
    elif tv_billion >= 2:
        return 2     # Poor liquidity
    elif tv_billion >= 1:
        return 1     # Very poor
    else:
        return 0     # Avoid - hard to exit
```

### 7.2.1 Threshold Comparison (OLD vs NEW)

| GTGD (tỷ) | OLD Score | NEW Score | Change |
|-----------|-----------|-----------|--------|
| 100+ | 8 | 8 | = |
| 50-99 | 7 | 8 | +1 |
| 30-49 | 6 | 7 | +1 |
| 20-29 | 6 | 6-7 | = |
| 15-19 | 5 | 6 | +1 |
| 10-14 | 5 | 5 | = |
| 8-9 | 4 | 5 | +1 |
| 5-7 | 4 | 4 | = |

### 7.3 Volume Trend Bonus (2 pts)

```python
def get_volume_trend_bonus(vol_vs_5d: float, vol_vs_20d: float) -> int:
    """
    Bonus based on volume trend.
    
    Args:
        vol_vs_5d: today_volume / avg_volume_5d
        vol_vs_20d: today_volume / avg_volume_20d
        
    Returns:
        Bonus -2 to +2
    """
    # Volume increasing (good for signal confirmation)
    if vol_vs_5d >= 1.5 and vol_vs_20d >= 1.3:
        return 2     # Strong volume increase
    elif vol_vs_5d >= 1.2:
        return 1     # Volume picking up
    elif vol_vs_5d >= 0.8:
        return 0     # Normal volume
    elif vol_vs_5d >= 0.5:
        return -1    # Volume declining
    else:
        return -2    # Very low volume
```

### 7.4 Total Liquidity Score

```python
def calculate_liquidity_score(trading_value: float, volume: float,
                              avg_volume_5d: float, avg_volume_20d: float) -> dict:
    """
    Calculate total liquidity factor score.
    
    Returns:
        dict with score (0-10) and components
    """
    # Trading value score (0-8)
    tv_score = get_trading_value_score(trading_value)
    
    # Volume trend bonus (-2 to +2)
    vol_vs_5d = volume / avg_volume_5d if avg_volume_5d > 0 else 1
    vol_vs_20d = volume / avg_volume_20d if avg_volume_20d > 0 else 1
    vol_bonus = get_volume_trend_bonus(vol_vs_5d, vol_vs_20d)
    
    # Total (clip to 0-10)
    total = max(0, min(10, tv_score + vol_bonus))
    
    return {
        'liquidity_score': total,
        'trading_value_score': tv_score,
        'volume_trend_bonus': vol_bonus,
        'trading_value_bn': trading_value / 1e9,
        'vol_vs_5d': vol_vs_5d,
        'vol_vs_20d': vol_vs_20d,
    }
```

---

## 8. Final Score Calculation

### 8.1 Composite Score Function

```python
def calculate_composite_score(
    # Pattern info
    pattern_name: str,
    pattern_signal: str,  # 'BULLISH' or 'BEARISH'
    
    # OHLCV data
    open_price: float,
    high: float,
    low: float,
    close: float,
    volume: float,
    
    # Technical data
    price_vs_sma20: float,
    price_vs_sma50: float,
    atr_14: float,
    avg_volume_20d: float,
    avg_volume_5d: float,
    
    # RS data
    rs_rating: int,
    rs_rating_5d_ago: int,
    
    # S/R data (from calculate_sr_levels)
    supports: list,
    resistances: list,
    
    # Calculated
    trading_value: float,
    signal_direction: str,  # 'BUY', 'SELL', 'PULLBACK', 'BOUNCE'
    trend: str,             # 'STRONG_UP', 'UPTREND', etc.
) -> dict:
    """
    Calculate composite signal score from all 6 factors.
    
    Returns:
        dict with total score and breakdown
    """
    
    # 1. CANDLESTICK SCORE (15 pts)
    candlestick_score = get_candlestick_score(pattern_name)
    
    # 2. VSA SCORE (25 pts)
    # Calculate VSA metrics
    spread = high - low
    spread_ratio = spread / atr_14 if atr_14 > 0 else 1.0
    close_position = (close - low) / spread if spread > 0 else 0.5
    vol_ratio = volume / avg_volume_20d if avg_volume_20d > 0 else 1.0
    price_change_pct = (close / open_price - 1) * 100
    
    vsa_result = calculate_vsa_score(
        vol_ratio=vol_ratio,
        spread_ratio=spread_ratio,
        close_position=close_position,
        signal_direction=signal_direction,
        trend=trend,
        price_change_pct=price_change_pct
    )
    vsa_score = vsa_result['vsa_score']
    
    # 3. TREND SCORE (20 pts)
    trend_score = get_trend_score(signal_direction, trend)
    
    # 4. S/R SCORE (15 pts)
    sr_result = get_sr_proximity_score(close, supports, resistances, signal_direction)
    rr_bonus = get_rr_bonus(
        close,
        supports[0] if supports else None,
        resistances[0] if resistances else None,
        signal_direction
    )
    sr_score = max(0, min(15, sr_result['score'] + rr_bonus))
    
    # 5. RS SCORE (15 pts)
    rs_result = calculate_rs_score(rs_rating, rs_rating_5d_ago, signal_direction)
    rs_score = rs_result['rs_score']
    
    # 6. LIQUIDITY SCORE (10 pts)
    liquidity_result = calculate_liquidity_score(
        trading_value=trading_value,
        volume=volume,
        avg_volume_5d=avg_volume_5d,
        avg_volume_20d=avg_volume_20d
    )
    liquidity_score = liquidity_result['liquidity_score']
    
    # TOTAL
    total_score = (candlestick_score + vsa_score + trend_score + 
                   sr_score + rs_score + liquidity_score)
    total_score = max(0, min(100, total_score))
    
    # Quality label
    quality = get_quality_label(total_score)
    
    return {
        'composite_score': total_score,
        'quality': quality,
        
        # Factor breakdown
        'candlestick_score': candlestick_score,
        'vsa_score': vsa_score,
        'trend_score': trend_score,
        'sr_score': sr_score,
        'rs_score': rs_score,
        'liquidity_score': liquidity_score,
        
        # Detailed breakdown
        'vsa_details': vsa_result,
        'rs_details': rs_result,
        'liquidity_details': liquidity_result,
        
        # Max scores for display
        'max_scores': {
            'candlestick': 15,
            'vsa': 25,
            'trend': 20,
            'sr': 15,
            'rs': 15,
            'liquidity': 10,
            'total': 100,
        }
    }
```

---

## 9. Direction Logic

### 9.1 Determine Signal Direction

```python
def determine_direction(pattern_signal: str, trend: str) -> str:
    """
    Determine signal direction from pattern signal and trend.
    
    Args:
        pattern_signal: 'BULLISH' or 'BEARISH' (from candlestick)
        trend: 'STRONG_UP', 'UPTREND', 'SIDEWAYS', 'DOWNTREND', 'STRONG_DOWN'
        
    Returns:
        'BUY', 'SELL', 'PULLBACK', or 'BOUNCE'
    """
    if trend in ['STRONG_UP', 'UPTREND']:
        if pattern_signal == 'BULLISH':
            return 'BUY'        # Trend-aligned bullish
        else:
            return 'PULLBACK'   # Counter-trend bearish (warning)
    
    elif trend in ['STRONG_DOWN', 'DOWNTREND']:
        if pattern_signal == 'BEARISH':
            return 'SELL'       # Trend-aligned bearish
        else:
            return 'BOUNCE'     # Counter-trend bullish (risky)
    
    else:  # SIDEWAYS
        if pattern_signal == 'BULLISH':
            return 'BUY'
        else:
            return 'SELL'
```

### 9.2 Action Labels (Vietnamese)

```python
ACTION_LABELS = {
    'BUY': 'MUA',
    'SELL': 'BÁN',
    'PULLBACK': 'CHỜ PULLBACK',
    'BOUNCE': 'BOUNCE (RỦI RO)',
    'NEUTRAL': 'THEO DÕI',
}

QUALITY_ACTIONS = {
    # (quality, direction) → action_label
    ('EXCELLENT', 'BUY'): 'MUA MẠNH',
    ('GOOD', 'BUY'): 'MUA',
    ('MODERATE', 'BUY'): 'CÂN NHẮC MUA',
    ('WEAK', 'BUY'): 'CHỜ XÁC NHẬN',
    
    ('EXCELLENT', 'SELL'): 'BÁN MẠNH',
    ('GOOD', 'SELL'): 'BÁN',
    ('MODERATE', 'SELL'): 'CÂN NHẮC BÁN',
    ('WEAK', 'SELL'): 'CHỜ XÁC NHẬN',
    
    ('EXCELLENT', 'PULLBACK'): 'CHỜ PULLBACK - TỐT',
    ('GOOD', 'PULLBACK'): 'CHỜ PULLBACK',
    ('MODERATE', 'PULLBACK'): 'CẢNH BÁO',
    ('WEAK', 'PULLBACK'): 'THEO DÕI',
    
    ('EXCELLENT', 'BOUNCE'): 'BOUNCE - CÓ THỂ MUA',
    ('GOOD', 'BOUNCE'): 'BOUNCE - RỦI RO',
    ('MODERATE', 'BOUNCE'): 'BOUNCE - RỦI RO CAO',
    ('WEAK', 'BOUNCE'): 'TRÁNH',
}
```

---

## 10. Quality Labels & Filters

### 10.1 Quality Labels

```python
def get_quality_label(score: int) -> str:
    """
    Get quality label from composite score.
    """
    if score >= 80:
        return 'EXCELLENT'
    elif score >= 65:
        return 'GOOD'
    elif score >= 50:
        return 'MODERATE'
    elif score >= 35:
        return 'WEAK'
    else:
        return 'AVOID'
```

### 10.2 Filter Thresholds

```python
# Minimum scores to display signals
MIN_SCORE_TO_DISPLAY = 40       # Don't show signals below this

# Minimum scores for recommendation strength
MIN_SCORE_BUY = 50              # Need 50+ to show as BUY
MIN_SCORE_STRONG_BUY = 70       # Need 70+ for STRONG BUY
MIN_SCORE_SELL = 50             # Need 50+ to show as SELL
MIN_SCORE_STRONG_SELL = 70      # Need 70+ for STRONG SELL

# Filter by quality
QUALITY_FILTERS = {
    'show_all': 40,             # Show WEAK and above
    'moderate_plus': 50,        # Show MODERATE and above
    'good_plus': 65,            # Show GOOD and above
    'excellent_only': 80,       # Show EXCELLENT only
}
```

### 10.3 Apply Filters

```python
def filter_signals(signals_df: pd.DataFrame, min_score: int = 40) -> pd.DataFrame:
    """
    Filter signals by minimum composite score.
    
    Args:
        signals_df: DataFrame with 'composite_score' column
        min_score: Minimum score to keep
        
    Returns:
        Filtered DataFrame
    """
    return signals_df[signals_df['composite_score'] >= min_score].copy()
```

---

## 11. Data Sources

### 11.1 Required Input Data

| Data | Source File | Columns Needed |
|------|-------------|----------------|
| OHLCV | `DATA/raw/ohlcv/OHLCV_mktcap.parquet` | symbol, date, open, high, low, close, volume |
| Technical | `DATA/processed/technical/basic_data.parquet` | price_vs_sma20, price_vs_sma50, trading_value, atr_14, avg_volume_20d |
| RS Rating | `DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet` | symbol, date, rs_rating |
| Patterns | `DATA/processed/technical/alerts/historical/patterns_history.parquet` | symbol, date, pattern_name, signal, strength |
| Breakout | `DATA/processed/technical/alerts/historical/breakout_history.parquet` | symbol, date, alert_type, signal, volume_ratio |

### 11.2 Additional Calculated Fields

```python
# Fields to calculate on-the-fly or pre-process
CALCULATED_FIELDS = {
    'spread': 'high - low',
    'spread_ratio': 'spread / atr_14',
    'close_position': '(close - low) / spread',
    'vol_ratio': 'volume / avg_volume_20d',
    'price_change_pct': '(close / open - 1) * 100',
    'trading_value': 'close * volume',
    'trend': 'classify_trend(price_vs_sma20, price_vs_sma50)',
    'rs_rating_5d_ago': 'rs_rating shifted by 5 days',
}
```

---

## 12. Implementation Notes

### 12.1 Integration Points

1. **Modify `_load_signals()` trong `ta_dashboard_service.py`:**
   - Load tất cả required data sources
   - Calculate composite score cho mỗi signal
   - Filter by min_score
   - Sort by composite_score descending

2. **Update UI trong `stock_scanner.py`:**
   - Hiển thị composite_score thay vì strength cũ
   - Thêm score breakdown tooltip
   - Color-code theo quality level

### 12.2 Performance Considerations

```python
# Cache S/R levels calculation (expensive)
@st.cache_data(ttl=300)
def get_sr_levels_cached(symbol: str) -> dict:
    ...

# Pre-calculate RS momentum for all symbols
@st.cache_data(ttl=300)  
def get_rs_momentum_batch() -> pd.DataFrame:
    ...
```

### 12.3 Handling Missing Data

```python
def safe_get(row: pd.Series, key: str, default=0):
    """Safely get value from row with default."""
    val = row.get(key, default)
    if pd.isna(val):
        return default
    return val

# Use throughout scoring functions
vol_ratio = safe_get(row, 'vol_ratio', 1.0)
rs_rating = safe_get(row, 'rs_rating', 50)  # Default to median
```

### 12.4 Testing

```python
# Test với các scenarios
TEST_SCENARIOS = [
    {
        'name': 'Perfect BUY',
        'expected_score': '90+',
        'pattern': 'morning_star',
        'trend': 'UPTREND',
        'vol_ratio': 2.5,
        'rs_rating': 85,
        'near_support': True,
    },
    {
        'name': 'Weak signal - filter out',
        'expected_score': '<40',
        'pattern': 'doji',
        'trend': 'DOWNTREND',  # conflict
        'vol_ratio': 0.6,      # low
        'rs_rating': 25,       # laggard
        'near_support': False,
    },
]
```

---

## Appendix: Score Breakdown Display

### UI Display Format (Score Breakdown Panel)

```
┌─────────────────────────────────────────────────────────┐
│ VCB - Morning Star                      SCORE: 87/100   │
├─────────────────────────────────────────────────────────┤
│  Pattern    ████████████████░░░░  15/15                │
│  VSA        ████████████████████░░░░░  20/25           │
│  Trend      ████████████████░░░░  17/20                │
│  S/R        ████████████░░░░░░░░  12/15                │
│  RS Rating  █████████████░░░░░░░  13/15                │
│  Liquidity  ████████████████████  10/10                │
└─────────────────────────────────────────────────────────┘
```

---

## 11. UI Implementation (v2.1)

### 11.1 Filter Layout

**Quick Filters (Main Row):**
| Filter | UI Element | Default | Notes |
|--------|-----------|---------|-------|
| Mã | Text input | Synced from Fundamental | Comma-separated |
| Hướng | Dropdown | Tất cả | MUA/BÁN/CHỜ |
| Điểm | Slider 0-100 | 50 | Step=5, composite score |
| Thời gian | Dropdown | 2 ngày | 1/2/5/10 ngày |

**Advanced Filters (Expander):**
| Filter | UI Element | Options |
|--------|-----------|---------|
| Ngành | Dropdown | All sectors |
| Loại tín hiệu | Dropdown | Pattern types |
| Xu hướng | Dropdown | Tăng/Giảm/Đi ngang |
| VSA Context | Dropdown | Tích lũy(+)/Phân phối(-)/Trung lập |
| Trend Alignment | Dropdown | Thuận trend(+20đ)/Ngược trend(-10đ) |
| GTGD tối thiểu | Dropdown | 30/50/100 tỷ |
| RS Rating | Slider 0-100 | Min RS filter |

### 11.2 Accordion Behavior

**Selection Method:** Multiselect widget (max 5 tickers)
- User selects tickers from available signals
- Selected tickers show score breakdown panels below tables
- Multiple selections allowed (accordion style)

**Auto-sync with Single Stock Analysis:**
- When exactly 1 ticker selected → auto-populate Single Stock input
- Session state: `scanner_selected_tickers`

### 11.3 Score Breakdown Panel

Each panel shows for selected ticker:

```python
# Panel Structure
{
    "header": "{ticker} {direction}  {total_score} pts",
    "subheader": "{pattern_name} | Trend: {trend}",
    "bars": [
        ("Pattern", score, 15, "#8B5CF6"),
        ("VSA", score, 25, color_by_sign),
        ("Trend", score, 20, color_by_sign),
        ("S/R", score, 15, "#22D3EE"),
        ("RS", score, 15, "#A78BFA"),
        ("Liquidity", score, 10, "#64748B")
    ]
}
```

**Score Bar Rendering:**
- Positive scores: show progress bar with color
- Negative scores: show empty bar, red text
- Format: `+{score}` for positive, `{score}` for negative

### 11.4 UI Rules (No Emoji Icons)

Per UI/UX Pro Max guidelines:
- No emoji icons in dropdowns or labels
- Trend badges: `++/+/=/-/--` (text symbols)
- Direction colors only (no emoji prefixes)

### 11.5 Signal Tables (Split View)

Three-column layout:
1. **MUA (Trend-aligned)** - Green accent (#10B981)
2. **BÁN (Trend-aligned)** - Red accent (#EF4444)
3. **PULLBACK/BOUNCE** - Orange accent (#F59E0B)

Each table shows:
- Ticker (monospace)
- Trend badge (++/+/=/-/--)
- Pattern name
- Composite score with progress bar

---

## 12. Performance Issues (2026-01-11)

### 12.1 Bug Report: Stock Scanner Not Loading

**Symptom:** Stock Scanner tab stuck on "Running TADashboardService._load_signals()"

**Root Cause:** O(N×M) complexity in `calculate_composite_scores()` function

### 12.2 Performance Analysis

**Data Sizes:**
- `basic_data.parquet`: 93,337 rows (20MB)
- `money_flow/individual_money_flow.parquet`: 93,374 rows (6.6MB)
- `rs_rating/stock_rs_rating_daily.parquet`: ~93K rows

**Problem Code (composite_scoring.py lines 499, 506, 509):**

```python
for _, row in signals_df.iterrows():
    # Line 499: O(n) filter for each row
    mf_row = mf_df[mf_df['symbol'] == symbol].iloc[0]

    # Line 506: calls calculate_sr_score() which filters basic_df
    sr_score, sr_info = calculate_sr_score(symbol, price, basic_df)

    # Line 509: calls calculate_rs_score() which filters rs_df
    rs_score, rs_rating, rs_momentum = calculate_rs_score(symbol, rs_df)
```

**Complexity:**
- N = number of signals (~500-1000)
- M = rows in each data file (~93,000)
- Operations: N × M × 3 files = ~140 million comparisons

### 12.3 Proposed Solutions

#### Option A: Pre-compute Lookup Dictionaries (Runtime Optimization)

```python
# Before loop - O(M) once
mf_lookup = mf_df.groupby('symbol').first().to_dict('index')
rs_lookup = rs_df.sort_values('date', ascending=False).groupby('symbol').first().to_dict('index')
sr_lookup = {...}  # Pre-compute swing high/low per symbol

# In loop - O(1) lookup
for _, row in signals_df.iterrows():
    mf_data = mf_lookup.get(symbol)  # O(1)
    rs_data = rs_lookup.get(symbol)  # O(1)
    sr_data = sr_lookup.get(symbol)  # O(1)
```

**Pros:** Simple fix, no pipeline changes
**Cons:** Still loops, memory for dictionaries

#### Option B: Pre-calculate Scores in Pipeline (Best Performance)

Add to daily pipeline (`daily_ta_complete.py`):

```python
# After signal detection, calculate composite scores ONCE
signals_df = calculate_composite_scores(signals_df)
signals_df.to_parquet("DATA/processed/technical/alerts/signals_with_scores.parquet")
```

**UI loads pre-scored data:**
```python
@st.cache_data(ttl=60)
def _load_signals():
    return pd.read_parquet("DATA/processed/technical/alerts/signals_with_scores.parquet")
```

**Pros:** Fastest UI load, scores already computed
**Cons:** Requires pipeline modification, scores stale until next run

#### Option C: Vectorized Calculation (Pandas Optimization)

Replace loop with vectorized merge operations:

```python
# Merge all data first (single merge per data source)
signals = signals.merge(mf_latest[['symbol', 'buy_value', 'sell_value']], on='symbol', how='left')
signals = signals.merge(rs_latest[['symbol', 'rs_rating']], on='symbol', how='left')
signals = signals.merge(sr_data[['symbol', 'swing_low', 'swing_high']], on='symbol', how='left')

# Then calculate scores vectorized
signals['vsa_score'] = signals.apply(calc_vsa_vectorized, axis=1)
signals['rs_score'] = signals['rs_rating'].apply(rs_to_score)
# etc.
```

**Pros:** Much faster than loop, no extra storage
**Cons:** Some complexity, may need refactoring

### 12.4 Recommended Action

1. **Quick fix (Option A):** Pre-compute lookup dicts before loop
2. **Long-term (Option B):** Move scoring to pipeline, read pre-scored parquet

### 12.5 Files to Modify

| File | Change |
|------|--------|
| `WEBAPP/pages/technical/services/composite_scoring.py` | Optimize `calculate_composite_scores()` |
| `PROCESSORS/pipelines/daily/daily_ta_complete.py` | Add pre-scoring step (Option B) |
| `WEBAPP/pages/technical/services/ta_dashboard_service.py` | Load pre-scored parquet (Option B) |

---

**End of Document**
