#!/usr/bin/env python3
"""
Full 100-Point Composite Signal Scoring (v2.1 Spec)

Calculates composite scores using ALL 6 factors per spec:
1. Candlestick Pattern (15 pts)
2. VSA - Volume Spread Analysis (25 pts)
3. Trend Alignment (20 pts)
4. S/R Proximity (15 pts)
5. RS Rating (15 pts)
6. Liquidity (10 pts)

Total: 100 points
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# === CONSTANTS FROM SPEC ===

PATTERN_SCORES = {
    # S-Tier: Multi-candle, high reliability (15 pts)
    'morning_star': 15, 'evening_star': 15,
    'three_white_soldiers': 15, 'three_black_crows': 15,
    # A-Tier: Strong reversal (13 pts)
    'engulfing': 13, 'bullish_engulfing': 13, 'bearish_engulfing': 13,
    # B-Tier: Single candle reversal (10 pts)
    'hammer': 10, 'inverted_hammer': 10, 'shooting_star': 10,
    # C-Tier: Moderate reliability (8 pts)
    'hanging_man': 8, 'piercing': 8, 'dark_cloud': 8,
    'dragonfly_doji': 8, 'gravestone_doji': 8,
    # D-Tier: Weak/Indecision (5 pts)
    'doji': 5, 'spinning_top': 5,
    # Non-pattern alerts
    'breakout': 7, 'volume_spike': 5,
}

BULLISH_REVERSAL_PATTERNS = [
    'morning_star', 'hammer', 'bullish_engulfing',
    'inverted_hammer', 'piercing', 'dragonfly_doji'
]
BEARISH_REVERSAL_PATTERNS = [
    'evening_star', 'shooting_star', 'bearish_engulfing',
    'hanging_man', 'dark_cloud', 'gravestone_doji'
]


# === HELPER FUNCTIONS ===

def classify_trend(price_vs_sma20: float, price_vs_sma50: float) -> str:
    """Classify trend based on price vs SMA positions."""
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


def get_pattern_context_multiplier(pattern_name: str, trend: str) -> float:
    """Adjust pattern score based on trend context (v2.1)."""
    if not pattern_name:
        return 1.0

    pattern_lower = pattern_name.lower().replace(' ', '_')

    if pattern_lower in BULLISH_REVERSAL_PATTERNS:
        if trend in ['STRONG_DOWN', 'DOWNTREND']:
            return 1.2  # Perfect context for bullish reversal
        elif trend == 'SIDEWAYS':
            return 0.9

    if pattern_lower in BEARISH_REVERSAL_PATTERNS:
        if trend in ['STRONG_UP', 'UPTREND']:
            return 1.2  # Perfect context for bearish reversal
        elif trend == 'SIDEWAYS':
            return 0.9

    return 1.0


# === FACTOR 1: CANDLESTICK PATTERN (15 pts) ===

def get_candlestick_score(pattern_name: str, trend: str = None) -> int:
    """Get candlestick pattern score with context adjustment."""
    if not pattern_name:
        return 0

    pattern_key = pattern_name.lower().replace(' ', '_')
    base_score = PATTERN_SCORES.get(pattern_key, 5)

    if trend:
        multiplier = get_pattern_context_multiplier(pattern_key, trend)
        adjusted_score = base_score * multiplier
        return min(15, int(adjusted_score))

    return base_score


# === FACTOR 2: VSA (25 pts) ===

def classify_volume(vol_ratio: float) -> str:
    """Classify volume level."""
    if vol_ratio >= 2.5:
        return 'VERY_HIGH'
    elif vol_ratio >= 1.5:
        return 'HIGH'
    elif vol_ratio >= 0.7:
        return 'NORMAL'
    elif vol_ratio >= 0.5:
        return 'LOW'
    else:
        return 'VERY_LOW'


def classify_spread(spread_ratio: float) -> str:
    """Classify spread (price range) level."""
    if spread_ratio >= 1.3:
        return 'WIDE'
    elif spread_ratio >= 0.7:
        return 'NORMAL'
    elif spread_ratio >= 0.5:
        return 'NARROW'
    else:
        return 'VERY_NARROW'


def classify_close(close_position: float) -> str:
    """Classify close position."""
    if close_position >= 0.7:
        return 'HIGH'
    elif close_position >= 0.3:
        return 'MIDDLE'
    else:
        return 'LOW'


def get_volume_score(vol_ratio: float) -> int:
    """Score based on volume ratio vs 20-day average. (0-10 pts)"""
    if vol_ratio >= 3.0:
        return 10
    elif vol_ratio >= 2.5:
        return 9
    elif vol_ratio >= 2.0:
        return 8
    elif vol_ratio >= 1.5:
        return 6
    elif vol_ratio >= 1.2:
        return 4
    elif vol_ratio >= 1.0:
        return 3
    elif vol_ratio >= 0.7:
        return 1
    else:
        return 0


def get_spread_score(spread_ratio: float, close_position: float, vol_ratio: float) -> int:
    """Score based on spread quality. (0-8 pts)"""
    if spread_ratio >= 1.3:
        if close_position >= 0.7:
            return 8
        elif close_position <= 0.3:
            return 6
        else:
            return 5
    elif spread_ratio <= 0.7:
        if vol_ratio >= 1.5:
            return 6  # Absorption
        else:
            return 2
    else:
        if close_position >= 0.7:
            return 5
        elif close_position <= 0.3:
            return 4
        else:
            return 3


def get_close_alignment_score(close_position: float, signal_direction: str) -> int:
    """Score based on close position alignment with signal direction. (-2 to 7 pts)"""
    if signal_direction == 'BUY':
        if close_position >= 0.7:
            return 7
        elif close_position >= 0.5:
            return 4
        elif close_position >= 0.3:
            return 1
        else:
            return -2
    else:  # SELL
        if close_position <= 0.3:
            return 7
        elif close_position <= 0.5:
            return 4
        elif close_position <= 0.7:
            return 1
        else:
            return -2


def detect_vsa_signal(vol_class: str, spread_class: str, close_class: str,
                      trend: str) -> tuple:
    """Detect VSA signal from metrics."""
    # Stopping Volume
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class in ['NARROW', 'VERY_NARROW'] and close_class == 'LOW':
        return ('stopping_volume', 'BULLISH')

    # Demand Coming In
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class == 'WIDE' and close_class == 'HIGH':
        return ('demand_coming_in', 'BULLISH')

    # Supply Coming In
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class == 'WIDE' and close_class == 'LOW':
        return ('supply_coming_in', 'BEARISH')

    # No Supply
    if vol_class in ['LOW', 'VERY_LOW'] and spread_class in ['NARROW', 'VERY_NARROW'] and trend in ['DOWNTREND', 'STRONG_DOWN']:
        return ('no_supply', 'BULLISH')

    # No Demand
    if vol_class in ['LOW', 'VERY_LOW'] and spread_class in ['NARROW', 'VERY_NARROW'] and trend in ['UPTREND', 'STRONG_UP']:
        return ('no_demand', 'BEARISH')

    # Upthrust
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class == 'WIDE' and close_class == 'LOW' and trend in ['UPTREND', 'STRONG_UP']:
        return ('upthrust', 'BEARISH')

    # Effort No Result
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class in ['NARROW', 'VERY_NARROW']:
        return ('effort_no_result', 'NEUTRAL')

    return (None, None)


def get_vsa_alignment_bonus(vsa_bias: str, signal_direction: str) -> int:
    """Bonus/penalty for VSA alignment with signal direction. (-5 to +3)"""
    if vsa_bias is None:
        return 0

    if signal_direction == 'BUY':
        if vsa_bias == 'BULLISH':
            return 3
        elif vsa_bias == 'BEARISH':
            return -5
        else:
            return 0
    else:
        if vsa_bias == 'BEARISH':
            return 3
        elif vsa_bias == 'BULLISH':
            return -5
        else:
            return 0


def calculate_vsa_score(vol_ratio: float, spread_ratio: float,
                        close_position: float, signal_direction: str,
                        trend: str) -> dict:
    """Calculate total VSA score (25 pts max)."""
    vol_class = classify_volume(vol_ratio)
    spread_class = classify_spread(spread_ratio)
    close_class = classify_close(close_position)

    volume_score = get_volume_score(vol_ratio)  # 0-10
    spread_score = get_spread_score(spread_ratio, close_position, vol_ratio)  # 0-8
    close_score = get_close_alignment_score(close_position, signal_direction)  # -2 to 7

    vsa_signal, vsa_bias = detect_vsa_signal(vol_class, spread_class, close_class, trend)
    vsa_bonus = get_vsa_alignment_bonus(vsa_bias, signal_direction)  # -5 to +3

    raw_total = volume_score + spread_score + close_score + vsa_bonus

    # Conflict multiplier (v2.1)
    conflict_multiplier = 1.0
    if vsa_bonus <= -4:
        conflict_multiplier = 0.6
    elif vsa_bonus < 0:
        conflict_multiplier = 0.8

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
    }


# === FACTOR 3: TREND ALIGNMENT (20 pts) ===

TREND_ALIGNMENT_MATRIX = {
    ('BUY', 'STRONG_UP'): 20, ('BUY', 'UPTREND'): 17,
    ('BUY', 'SIDEWAYS'): 12, ('BUY', 'DOWNTREND'): 7, ('BUY', 'STRONG_DOWN'): 4,

    ('SELL', 'STRONG_DOWN'): 20, ('SELL', 'DOWNTREND'): 17,
    ('SELL', 'SIDEWAYS'): 12, ('SELL', 'UPTREND'): 7, ('SELL', 'STRONG_UP'): 4,

    ('BOUNCE', 'STRONG_UP'): 6, ('BOUNCE', 'UPTREND'): 8,
    ('BOUNCE', 'SIDEWAYS'): 10, ('BOUNCE', 'DOWNTREND'): 12, ('BOUNCE', 'STRONG_DOWN'): 10,
}


def get_trend_score_spec(signal_direction: str, trend: str, pattern_name: str = '') -> int:
    """
    Get trend alignment score using FULL spec logic.

    For REVERSAL patterns (swing trading 10-15 sessions):
    - Bullish reversal in DOWNTREND = high score (potential bottom)
    - Bearish reversal in UPTREND = high score (potential top)
    """
    pattern_lower = str(pattern_name).lower().replace(' ', '_')
    is_bullish_reversal = pattern_lower in BULLISH_REVERSAL_PATTERNS
    is_bearish_reversal = pattern_lower in BEARISH_REVERSAL_PATTERNS

    # REVERSAL pattern scoring
    if is_bullish_reversal and signal_direction == 'BUY':
        reversal_matrix = {
            'STRONG_DOWN': 20, 'DOWNTREND': 18, 'SIDEWAYS': 10,
            'UPTREND': 5, 'STRONG_UP': 0,
        }
        return reversal_matrix.get(trend, 5)

    if is_bearish_reversal and signal_direction == 'SELL':
        reversal_matrix = {
            'STRONG_UP': 20, 'UPTREND': 18, 'SIDEWAYS': 10,
            'DOWNTREND': 5, 'STRONG_DOWN': 0,
        }
        return reversal_matrix.get(trend, 5)

    # Standard trend alignment
    return TREND_ALIGNMENT_MATRIX.get((signal_direction, trend), 10)


# === FACTOR 4: S/R PROXIMITY (15 pts) ===

def calculate_sr_levels(df: pd.DataFrame, lookback_swing: int = 20, lookback_fib: int = 30) -> dict:
    """Calculate Support/Resistance levels with Fib validation."""
    if df.empty:
        return {'supports': [], 'resistances': [], 'current_price': 0, 'fib_valid': False}

    recent = df.tail(lookback_fib)
    swing_data = df.tail(lookback_swing)

    swing_high = swing_data['high'].max()
    swing_low = swing_data['low'].min()

    fib_high = recent['high'].max()
    fib_low = recent['low'].min()
    fib_range = fib_high - fib_low

    current_price = df.iloc[-1]['close']

    # Simplified ATR
    atr_14 = (df.tail(14)['high'] - df.tail(14)['low']).mean()
    fib_valid = fib_range >= (atr_14 * 5)

    supports = []
    resistances = []

    if swing_low < current_price * 0.995:
        supports.append({
            'price': swing_low,
            'label': 'Swing Low',
            'pct': (swing_low / current_price - 1) * 100,
        })
    if swing_high > current_price * 1.005:
        resistances.append({
            'price': swing_high,
            'label': 'Swing High',
            'pct': (swing_high / current_price - 1) * 100,
        })

    if fib_valid:
        fib_levels = [
            (fib_low + fib_range * 0.236, 'Fib 23.6%'),
            (fib_low + fib_range * 0.382, 'Fib 38.2%'),
            (fib_low + fib_range * 0.500, 'Fib 50%'),
            (fib_low + fib_range * 0.618, 'Fib 61.8%'),
        ]
        for level, label in fib_levels:
            if level < current_price * 0.995:
                supports.append({'price': level, 'label': label, 'pct': (level / current_price - 1) * 100})
            elif level > current_price * 1.005:
                resistances.append({'price': level, 'label': label, 'pct': (level / current_price - 1) * 100})

    supports.sort(key=lambda x: x['price'], reverse=True)
    resistances.sort(key=lambda x: x['price'])

    return {
        'current_price': current_price,
        'supports': supports[:3],
        'resistances': resistances[:3],
        'swing_high': swing_high,
        'swing_low': swing_low,
        'fib_valid': fib_valid,
    }


def get_sr_proximity_score(current_price: float, supports: list,
                           resistances: list, signal_direction: str) -> int:
    """Calculate S/R proximity score (0-12 pts)."""
    if signal_direction == 'BUY':
        if supports:
            distance_pct = abs(supports[0]['pct'])
            if distance_pct < 2:
                return 12
            elif distance_pct < 4:
                return 10
            elif distance_pct < 6:
                return 7
            elif distance_pct < 10:
                return 4
            else:
                return 2
        return 3
    else:
        if resistances:
            distance_pct = abs(resistances[0]['pct'])
            if distance_pct < 2:
                return 12
            elif distance_pct < 4:
                return 10
            elif distance_pct < 6:
                return 7
            elif distance_pct < 10:
                return 4
            else:
                return 2
        return 3


def get_rr_bonus(current_price: float, nearest_support: dict,
                 nearest_resistance: dict, signal_direction: str) -> int:
    """Bonus based on Risk/Reward ratio (-3 to +3)."""
    if not nearest_support or not nearest_resistance:
        return 0

    support_price = nearest_support['price']
    resistance_price = nearest_resistance['price']

    if signal_direction == 'BUY':
        risk = current_price - support_price
        reward = resistance_price - current_price
    else:
        risk = resistance_price - current_price
        reward = current_price - support_price

    if risk <= 0:
        return 0

    rr_ratio = reward / risk

    if rr_ratio >= 3.0:
        return 3
    elif rr_ratio >= 2.0:
        return 2
    elif rr_ratio >= 1.5:
        return 1
    elif rr_ratio >= 1.0:
        return 0
    else:
        return -3


def calculate_sr_score(symbol: str, price: float, ohlcv_df: pd.DataFrame,
                       signal_direction: str) -> dict:
    """Calculate total S/R factor score (15 pts max)."""
    symbol_df = ohlcv_df[ohlcv_df['symbol'] == symbol].sort_values('date').tail(60)

    if symbol_df.empty:
        return {'sr_score': 5, 'proximity_score': 5, 'rr_bonus': 0}

    sr_levels = calculate_sr_levels(symbol_df)

    proximity_score = get_sr_proximity_score(
        price, sr_levels['supports'], sr_levels['resistances'], signal_direction
    )

    rr_bonus = get_rr_bonus(
        price,
        sr_levels['supports'][0] if sr_levels['supports'] else None,
        sr_levels['resistances'][0] if sr_levels['resistances'] else None,
        signal_direction
    )

    total = max(0, min(15, proximity_score + rr_bonus))

    return {
        'sr_score': total,
        'proximity_score': proximity_score,
        'rr_bonus': rr_bonus,
        'sr_levels': sr_levels,
    }


# === FACTOR 5: RS RATING (15 pts) ===

def get_rs_base_score(rs_rating: int) -> int:
    """Convert RS Rating (1-99) to base score (0-10)."""
    if rs_rating >= 90:
        return 10
    elif rs_rating >= 80:
        return 9
    elif rs_rating >= 70:
        return 8
    elif rs_rating >= 60:
        return 7
    elif rs_rating >= 50:
        return 5
    elif rs_rating >= 40:
        return 4
    elif rs_rating >= 30:
        return 3
    elif rs_rating >= 20:
        return 2
    else:
        return 1


def get_rs_momentum_score(rs_rating_today: int, rs_rating_5d_ago: int) -> int:
    """Score based on RS momentum (-1 to +2)."""
    if rs_rating_5d_ago is None or rs_rating_5d_ago == 0:
        return 0

    rs_change = rs_rating_today - rs_rating_5d_ago

    if rs_change >= 8:
        return 2
    elif rs_change >= 4:
        return 1
    elif rs_change >= 0:
        return 0
    else:
        return -1


def get_rs_alignment_score(signal_direction: str, rs_rating: int) -> int:
    """Score based on RS alignment with signal direction (-2 to +2)."""
    if signal_direction == 'BUY':
        if rs_rating >= 70:
            return 2
        elif rs_rating >= 50:
            return 1
        elif rs_rating >= 30:
            return 0
        else:
            return -2
    else:
        if rs_rating <= 30:
            return 2
        elif rs_rating <= 50:
            return 1
        elif rs_rating <= 70:
            return 0
        else:
            return -2


def calculate_rs_score(symbol: str, rs_df: pd.DataFrame, signal_direction: str) -> dict:
    """Calculate total RS factor score (15 pts max)."""
    symbol_rs = rs_df[rs_df['symbol'] == symbol].sort_values('date', ascending=False)

    if symbol_rs.empty:
        return {'rs_score': 5, 'rs_rating': 50, 'momentum': 0, 'alignment': 0}

    rs_today = int(symbol_rs.iloc[0].get('rs_rating', 50))
    rs_5d_ago = int(symbol_rs.iloc[5].get('rs_rating', rs_today)) if len(symbol_rs) > 5 else rs_today

    base_score = get_rs_base_score(rs_today)
    momentum_score = get_rs_momentum_score(rs_today, rs_5d_ago)
    alignment_score = get_rs_alignment_score(signal_direction, rs_today)

    total = max(0, min(15, base_score + momentum_score + alignment_score))

    return {
        'rs_score': total,
        'rs_rating': rs_today,
        'base': base_score,
        'momentum': momentum_score,
        'alignment': alignment_score,
    }


# === FACTOR 6: LIQUIDITY (10 pts) ===

def get_trading_value_score(trading_value: float) -> int:
    """Score based on trading value (0-8 pts). v2.1 thresholds."""
    tv_billion = trading_value / 1e9

    if tv_billion >= 50:
        return 8
    elif tv_billion >= 30:
        return 7
    elif tv_billion >= 15:
        return 6
    elif tv_billion >= 8:
        return 5
    elif tv_billion >= 4:
        return 4
    elif tv_billion >= 2:
        return 2
    elif tv_billion >= 1:
        return 1
    else:
        return 0


def get_volume_trend_bonus(vol_vs_5d: float, vol_vs_20d: float) -> int:
    """Bonus based on volume trend (-2 to +2)."""
    if vol_vs_5d >= 1.5 and vol_vs_20d >= 1.3:
        return 2
    elif vol_vs_5d >= 1.2:
        return 1
    elif vol_vs_5d >= 0.8:
        return 0
    elif vol_vs_5d >= 0.5:
        return -1
    else:
        return -2


def calculate_liquidity_score(trading_value: float, vol_ratio: float,
                              vol_vs_5d: float = 1.0) -> dict:
    """Calculate total liquidity factor score (10 pts max)."""
    tv_score = get_trading_value_score(trading_value)
    vol_bonus = get_volume_trend_bonus(vol_vs_5d, vol_ratio)

    total = max(0, min(10, tv_score + vol_bonus))

    return {
        'liquidity_score': total,
        'tv_score': tv_score,
        'vol_bonus': vol_bonus,
        'trading_value_bn': trading_value / 1e9,
    }


# === MAIN: LOAD DATA & CALCULATE ===

def load_data():
    """Load all required data files."""
    base_path = Path("DATA/processed")
    raw_path = Path("DATA/raw")

    # Load signals (patterns)
    patterns_df = pd.read_parquet(base_path / "technical/alerts/historical/patterns_history.parquet")

    # Load OHLCV
    ohlcv_df = pd.read_parquet(raw_path / "ohlcv/OHLCV_mktcap.parquet")

    # Load technical data
    basic_df = pd.read_parquet(base_path / "technical/basic_data.parquet")

    # Load RS rating
    rs_df = pd.read_parquet(base_path / "technical/rs_rating/stock_rs_rating_daily.parquet")

    return patterns_df, ohlcv_df, basic_df, rs_df


def get_latest_patterns(patterns_df: pd.DataFrame, days: int = 3) -> pd.DataFrame:
    """Get patterns from last N days."""
    patterns_df['date'] = pd.to_datetime(patterns_df['date'])
    latest_date = patterns_df['date'].max()
    cutoff = latest_date - timedelta(days=days)

    return patterns_df[patterns_df['date'] >= cutoff].copy()


def calculate_full_composite_score(row, ohlcv_df, basic_df, rs_df):
    """Calculate FULL 100-point composite score for a single signal."""
    symbol = row['symbol']
    pattern_name = str(row.get('pattern_name', '')).lower().replace(' ', '_')
    signal_type = row.get('signal', 'BULLISH')

    # Get basic data for symbol (latest)
    basic_row = basic_df[basic_df['symbol'] == symbol].sort_values('date', ascending=False).iloc[0] if symbol in basic_df['symbol'].values else None

    if basic_row is None:
        return None

    # Extract values
    price = basic_row.get('close', 0)
    vol_ratio = basic_row.get('vol_ratio_20d', 1.0) or 1.0
    atr_14 = basic_row.get('atr_14', 1.0) or 1.0
    trading_value = basic_row.get('trading_value', 0) or 0
    price_vs_sma20 = basic_row.get('price_vs_sma20', 0) or 0
    price_vs_sma50 = basic_row.get('price_vs_sma50', 0) or 0

    # Calculate spread metrics from OHLCV
    symbol_ohlcv = ohlcv_df[ohlcv_df['symbol'] == symbol].sort_values('date', ascending=False)
    if not symbol_ohlcv.empty:
        latest_ohlcv = symbol_ohlcv.iloc[0]
        high = latest_ohlcv.get('high', price)
        low = latest_ohlcv.get('low', price)
        close = latest_ohlcv.get('close', price)
        spread = high - low
        spread_ratio = spread / atr_14 if atr_14 > 0 else 1.0
        close_position = (close - low) / spread if spread > 0 else 0.5
    else:
        spread_ratio = 1.0
        close_position = 0.5

    # Determine trend and direction
    trend = classify_trend(price_vs_sma20, price_vs_sma50)
    direction = 'BUY' if signal_type == 'BULLISH' else 'SELL'

    # === CALCULATE ALL 6 FACTORS ===

    # 1. Candlestick Score (15 pts)
    candlestick_score = get_candlestick_score(pattern_name, trend)

    # 2. VSA Score (25 pts)
    vsa_result = calculate_vsa_score(vol_ratio, spread_ratio, close_position, direction, trend)
    vsa_score = vsa_result['vsa_score']

    # 3. Trend Score (20 pts)
    trend_score = get_trend_score_spec(direction, trend, pattern_name)

    # 4. S/R Score (15 pts)
    sr_result = calculate_sr_score(symbol, price, ohlcv_df, direction)
    sr_score = sr_result['sr_score']

    # 5. RS Score (15 pts)
    rs_result = calculate_rs_score(symbol, rs_df, direction)
    rs_score = rs_result['rs_score']

    # 6. Liquidity Score (10 pts)
    liq_result = calculate_liquidity_score(trading_value, vol_ratio)
    liquidity_score = liq_result['liquidity_score']

    # TOTAL
    total_score = candlestick_score + vsa_score + trend_score + sr_score + rs_score + liquidity_score
    total_score = max(0, min(100, total_score))

    return {
        'symbol': symbol,
        'direction': direction,
        'pattern': pattern_name,
        'trend': trend,
        'total_score': total_score,
        'pattern_score': candlestick_score,
        'vsa_score': vsa_score,
        'trend_score': trend_score,
        'sr_score': sr_score,
        'rs_score': rs_score,
        'liquidity_score': liquidity_score,
        'rs_rating': rs_result['rs_rating'],
        'trading_value_bn': liq_result['trading_value_bn'],
        'vsa_signal': vsa_result.get('vsa_signal', ''),
        'vol_ratio': vol_ratio,
    }


def main():
    print("=" * 80)
    print("FULL 100-POINT COMPOSITE SIGNAL SCORING (v2.1 Spec)")
    print("=" * 80)
    print()

    # Load data
    print("Loading data...")
    patterns_df, ohlcv_df, basic_df, rs_df = load_data()
    print(f"  Patterns: {len(patterns_df):,} rows")
    print(f"  OHLCV: {len(ohlcv_df):,} rows")
    print(f"  Basic: {len(basic_df):,} rows")
    print(f"  RS: {len(rs_df):,} rows")
    print()

    # Get recent patterns (last 3 days)
    recent_patterns = get_latest_patterns(patterns_df, days=3)
    print(f"Recent patterns (3 days): {len(recent_patterns)} signals")
    print()

    # Calculate scores
    print("Calculating full composite scores...")
    results = []
    for _, row in recent_patterns.iterrows():
        result = calculate_full_composite_score(row, ohlcv_df, basic_df, rs_df)
        if result:
            results.append(result)

    results_df = pd.DataFrame(results)
    print(f"Scored {len(results_df)} signals")
    print()

    # Split by direction
    buy_signals = results_df[results_df['direction'] == 'BUY'].sort_values('total_score', ascending=False)
    sell_signals = results_df[results_df['direction'] == 'SELL'].sort_values('total_score', ascending=False)

    # === PRINT TOP 10 BUY ===
    print("=" * 80)
    print("TOP 10 BUY SIGNALS")
    print("=" * 80)
    print(f"{'Rank':<5} {'Symbol':<8} {'Score':<7} {'Pattern':<20} {'Trend':<12} {'Pat':<4} {'VSA':<4} {'Trd':<4} {'S/R':<4} {'RS':<4} {'Liq':<4} {'RS%':<5}")
    print("-" * 80)

    for i, (_, row) in enumerate(buy_signals.head(10).iterrows(), 1):
        print(f"{i:<5} {row['symbol']:<8} {row['total_score']:<7.0f} {row['pattern'][:20]:<20} {row['trend']:<12} "
              f"{row['pattern_score']:<4} {row['vsa_score']:<4} {row['trend_score']:<4} "
              f"{row['sr_score']:<4} {row['rs_score']:<4} {row['liquidity_score']:<4} {row['rs_rating']:<5}")

    print()

    # === PRINT TOP 10 SELL ===
    print("=" * 80)
    print("TOP 10 SELL SIGNALS")
    print("=" * 80)
    print(f"{'Rank':<5} {'Symbol':<8} {'Score':<7} {'Pattern':<20} {'Trend':<12} {'Pat':<4} {'VSA':<4} {'Trd':<4} {'S/R':<4} {'RS':<4} {'Liq':<4} {'RS%':<5}")
    print("-" * 80)

    for i, (_, row) in enumerate(sell_signals.head(10).iterrows(), 1):
        print(f"{i:<5} {row['symbol']:<8} {row['total_score']:<7.0f} {row['pattern'][:20]:<20} {row['trend']:<12} "
              f"{row['pattern_score']:<4} {row['vsa_score']:<4} {row['trend_score']:<4} "
              f"{row['sr_score']:<4} {row['rs_score']:<4} {row['liquidity_score']:<4} {row['rs_rating']:<5}")

    print()
    print("=" * 80)
    print("LEGEND:")
    print("  Pat = Pattern Score (max 15)")
    print("  VSA = Volume Spread Analysis (max 25)")
    print("  Trd = Trend Alignment (max 20)")
    print("  S/R = Support/Resistance Proximity (max 15)")
    print("  RS  = RS Rating Score (max 15)")
    print("  Liq = Liquidity Score (max 10)")
    print("  RS% = Raw RS Rating (1-99)")
    print("=" * 80)

    # Summary stats
    print()
    print("DISTRIBUTION:")
    print(f"  BUY signals:  {len(buy_signals):>4} | Avg Score: {buy_signals['total_score'].mean():.1f}")
    print(f"  SELL signals: {len(sell_signals):>4} | Avg Score: {sell_signals['total_score'].mean():.1f}")
    print(f"  Score >= 70:  {len(results_df[results_df['total_score'] >= 70]):>4}")
    print(f"  Score >= 60:  {len(results_df[results_df['total_score'] >= 60]):>4}")
    print(f"  Score >= 50:  {len(results_df[results_df['total_score'] >= 50]):>4}")


if __name__ == "__main__":
    main()
