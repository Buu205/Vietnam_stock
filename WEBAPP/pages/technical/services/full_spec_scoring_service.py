"""
Full 100-Point Composite Signal Scoring Service (v2.1)
======================================================

Complete implementation of 6-factor scoring per spec document.

Factors (100 pts total):
1. Candlestick Pattern (15 pts max)
2. VSA - Volume Spread Analysis (25 pts max)
3. Trend Alignment (20 pts max)
4. S/R Proximity (15 pts max)
5. RS Rating (15 pts max)
6. Liquidity (10 pts max)

Reference: composite_signal_scoring_logic.md
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple

# Conditional streamlit import to avoid warnings when running as script
try:
    import streamlit as st
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    _IN_STREAMLIT = get_script_run_ctx() is not None
except Exception:
    _IN_STREAMLIT = False
    st = None

# Fallback cache decorator for non-streamlit contexts
def _noop_cache(*args, **kwargs):
    """No-op cache decorator when not in Streamlit."""
    def decorator(func):
        return func
    return decorator

# Use st.cache_data if in Streamlit, otherwise no-op
cache_data = st.cache_data if _IN_STREAMLIT and st else _noop_cache


# =============================================================================
# CONSTANTS
# =============================================================================

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


# =============================================================================
# DATA LOADING (Cached)
# =============================================================================

@cache_data(ttl=300)
def load_full_scoring_data() -> Tuple[Dict, Dict, Dict]:
    """
    Load all data needed for full spec scoring.

    Returns:
        (basic_lookup, rs_lookup, vol_avg_lookup)
        - basic_lookup: symbol -> {close, high, low, atr_14, volume, trading_value, price_vs_sma20, price_vs_sma50, ...}
        - rs_lookup: symbol -> {rs_rating, rs_momentum}
        - vol_avg_lookup: symbol -> vol_20d_avg (pre-calculated)
    """
    # =========================================================================
    # 1. BASIC DATA LATEST (with OHLCV and indicators)
    # =========================================================================
    basic_lookup = {}
    basic_path = Path("DATA/processed/technical/basic_data_latest.parquet")
    if basic_path.exists():
        df = pd.read_parquet(basic_path)
        for _, row in df.iterrows():
            basic_lookup[row['symbol']] = row.to_dict()

    # =========================================================================
    # 2. VOLUME 20D AVERAGE (for vol_ratio calculation)
    # =========================================================================
    vol_avg_lookup = {}
    basic_full_path = Path("DATA/processed/technical/basic_data.parquet")
    if basic_full_path.exists():
        basic_df = pd.read_parquet(basic_full_path, columns=['symbol', 'date', 'volume'])
        # Get latest 20 days per symbol
        basic_df = basic_df.sort_values('date', ascending=False)
        for symbol in basic_df['symbol'].unique():
            sym_data = basic_df[basic_df['symbol'] == symbol].head(20)
            if len(sym_data) >= 5:  # Minimum 5 days
                vol_avg_lookup[symbol] = sym_data['volume'].mean()

    # =========================================================================
    # 3. RS RATING with momentum
    # =========================================================================
    rs_lookup = {}
    rs_path = Path("DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet")
    if rs_path.exists():
        rs_df = pd.read_parquet(rs_path)
        rs_df = rs_df.sort_values('date', ascending=False)
        for symbol in rs_df['symbol'].unique():
            sym_data = rs_df[rs_df['symbol'] == symbol]
            if len(sym_data) >= 1:
                rs_rating = sym_data.iloc[0].get('rs_rating', 0) or 0
                rs_momentum = 0
                if len(sym_data) >= 5:
                    rs_5d_ago = sym_data.iloc[4].get('rs_rating', rs_rating) or rs_rating
                    rs_momentum = rs_rating - rs_5d_ago
                rs_lookup[symbol] = {
                    'rs_rating': rs_rating,
                    'rs_momentum': rs_momentum
                }

    return basic_lookup, rs_lookup, vol_avg_lookup


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def classify_trend(price_vs_sma20: float, price_vs_sma50: float) -> str:
    """Classify trend based on price vs SMA positions."""
    sma20 = (price_vs_sma20 or 0) * 100  # Convert from decimal to percent
    sma50 = (price_vs_sma50 or 0) * 100

    if sma20 > 5 and sma50 > 5:
        return 'STRONG_UP'
    elif sma20 > 2 and sma50 > 2:
        return 'UPTREND'
    elif sma20 < -5 and sma50 < -5:
        return 'STRONG_DOWN'
    elif sma20 < -2 and sma50 < -2:
        return 'DOWNTREND'
    return 'SIDEWAYS'


def get_pattern_context_multiplier(pattern_name: str, trend: str) -> float:
    """Adjust pattern score based on trend context."""
    if not pattern_name:
        return 1.0

    pattern_lower = pattern_name.lower().replace(' ', '_')

    if pattern_lower in BULLISH_REVERSAL_PATTERNS:
        if trend in ['STRONG_DOWN', 'DOWNTREND']:
            return 1.2  # Perfect context
        elif trend == 'SIDEWAYS':
            return 0.9

    if pattern_lower in BEARISH_REVERSAL_PATTERNS:
        if trend in ['STRONG_UP', 'UPTREND']:
            return 1.2  # Perfect context
        elif trend == 'SIDEWAYS':
            return 0.9

    return 1.0


# =============================================================================
# FACTOR 1: CANDLESTICK PATTERN (15 pts)
# =============================================================================

def calculate_candlestick_score(pattern_name: str, trend: str = None) -> int:
    """Get candlestick pattern score with context adjustment."""
    if not pattern_name:
        return 0

    pattern_key = pattern_name.lower().replace(' ', '_')
    base_score = PATTERN_SCORES.get(pattern_key, 5)

    if trend:
        multiplier = get_pattern_context_multiplier(pattern_key, trend)
        adjusted = base_score * multiplier
        return min(15, int(adjusted))

    return min(15, base_score)


# =============================================================================
# FACTOR 2: VSA (25 pts) - Full Implementation
# =============================================================================

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
    return 'VERY_LOW'


def classify_spread(spread_ratio: float) -> str:
    """Classify spread (price range vs ATR)."""
    if spread_ratio >= 1.3:
        return 'WIDE'
    elif spread_ratio >= 0.7:
        return 'NORMAL'
    elif spread_ratio >= 0.5:
        return 'NARROW'
    return 'VERY_NARROW'


def classify_close(close_position: float) -> str:
    """Classify close position within candle."""
    if close_position >= 0.7:
        return 'HIGH'
    elif close_position >= 0.3:
        return 'MIDDLE'
    return 'LOW'


def get_volume_score(vol_ratio: float) -> int:
    """Score based on volume ratio. (0-10 pts)"""
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
    return 0


def get_spread_score(spread_ratio: float, close_position: float, vol_ratio: float) -> int:
    """Score based on spread quality. (0-8 pts)"""
    if spread_ratio >= 1.3:  # Wide spread
        if close_position >= 0.7:
            return 8  # Strong close high
        elif close_position <= 0.3:
            return 6  # Strong close low
        return 5
    elif spread_ratio <= 0.7:  # Narrow spread
        if vol_ratio >= 1.5:
            return 6  # Absorption pattern
        return 2
    else:  # Normal spread
        if close_position >= 0.7:
            return 5
        elif close_position <= 0.3:
            return 4
        return 3


def get_close_alignment_score(close_position: float, direction: str) -> int:
    """Score based on close alignment with direction. (-2 to 7 pts)"""
    if direction == 'BUY':
        if close_position >= 0.7:
            return 7
        elif close_position >= 0.5:
            return 4
        elif close_position >= 0.3:
            return 1
        return -2
    else:  # SELL
        if close_position <= 0.3:
            return 7
        elif close_position <= 0.5:
            return 4
        elif close_position <= 0.7:
            return 1
        return -2


def detect_vsa_signal(vol_class: str, spread_class: str, close_class: str, trend: str) -> Tuple[str, str]:
    """Detect VSA signal pattern."""
    # Stopping Volume
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class in ['NARROW', 'VERY_NARROW'] and close_class == 'LOW':
        return ('stopping_volume', 'BULLISH')

    # Demand Coming In
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class == 'WIDE' and close_class == 'HIGH':
        return ('demand_coming_in', 'BULLISH')

    # Supply Coming In
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class == 'WIDE' and close_class == 'LOW':
        return ('supply_coming_in', 'BEARISH')

    # No Supply (in downtrend)
    if vol_class in ['LOW', 'VERY_LOW'] and spread_class in ['NARROW', 'VERY_NARROW'] and trend in ['DOWNTREND', 'STRONG_DOWN']:
        return ('no_supply', 'BULLISH')

    # No Demand (in uptrend)
    if vol_class in ['LOW', 'VERY_LOW'] and spread_class in ['NARROW', 'VERY_NARROW'] and trend in ['UPTREND', 'STRONG_UP']:
        return ('no_demand', 'BEARISH')

    # Upthrust
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class == 'WIDE' and close_class == 'LOW' and trend in ['UPTREND', 'STRONG_UP']:
        return ('upthrust', 'BEARISH')

    # Effort No Result
    if vol_class in ['HIGH', 'VERY_HIGH'] and spread_class in ['NARROW', 'VERY_NARROW']:
        return ('effort_no_result', 'NEUTRAL')

    return (None, None)


def get_vsa_alignment_bonus(vsa_bias: str, direction: str) -> int:
    """Bonus/penalty for VSA alignment. (-5 to +3)"""
    if vsa_bias is None:
        return 0

    if direction == 'BUY':
        if vsa_bias == 'BULLISH':
            return 3
        elif vsa_bias == 'BEARISH':
            return -5
    else:  # SELL
        if vsa_bias == 'BEARISH':
            return 3
        elif vsa_bias == 'BULLISH':
            return -5
    return 0


def calculate_vsa_score(vol_ratio: float, spread_ratio: float, close_position: float,
                        direction: str, trend: str) -> Dict:
    """Calculate total VSA score (25 pts max)."""
    vol_class = classify_volume(vol_ratio)
    spread_class = classify_spread(spread_ratio)
    close_class = classify_close(close_position)

    volume_score = get_volume_score(vol_ratio)  # 0-10
    spread_score = get_spread_score(spread_ratio, close_position, vol_ratio)  # 0-8
    close_score = get_close_alignment_score(close_position, direction)  # -2 to 7

    vsa_signal, vsa_bias = detect_vsa_signal(vol_class, spread_class, close_class, trend)
    vsa_bonus = get_vsa_alignment_bonus(vsa_bias, direction)  # -5 to +3

    raw_total = volume_score + spread_score + close_score + vsa_bonus

    # Conflict multiplier (v2.1)
    conflict_mult = 1.0
    if vsa_bonus <= -4:
        conflict_mult = 0.6  # Strong conflict
    elif vsa_bonus < 0:
        conflict_mult = 0.8  # Mild conflict

    adjusted_total = raw_total * conflict_mult
    total = max(0, min(25, int(adjusted_total)))

    return {
        'vsa_score': total,
        'volume_score': volume_score,
        'spread_score': spread_score,
        'close_score': close_score,
        'vsa_signal': vsa_signal,
        'vsa_bias': vsa_bias,
        'vsa_bonus': vsa_bonus,
        'conflict_mult': conflict_mult,
    }


# =============================================================================
# FACTOR 3: TREND ALIGNMENT (20 pts)
# =============================================================================

TREND_ALIGNMENT_MATRIX = {
    ('BUY', 'STRONG_UP'): 20, ('BUY', 'UPTREND'): 17,
    ('BUY', 'SIDEWAYS'): 12, ('BUY', 'DOWNTREND'): 7, ('BUY', 'STRONG_DOWN'): 4,

    ('SELL', 'STRONG_DOWN'): 20, ('SELL', 'DOWNTREND'): 17,
    ('SELL', 'SIDEWAYS'): 12, ('SELL', 'UPTREND'): 7, ('SELL', 'STRONG_UP'): 4,
}


def calculate_trend_score(direction: str, trend: str, pattern_name: str = '') -> int:
    """
    Calculate trend alignment score (20 pts max).

    For REVERSAL patterns (swing trading):
    - Bullish reversal in DOWNTREND = high score (potential bottom)
    - Bearish reversal in UPTREND = high score (potential top)
    """
    pattern_lower = str(pattern_name).lower().replace(' ', '_')
    is_bullish_reversal = pattern_lower in BULLISH_REVERSAL_PATTERNS
    is_bearish_reversal = pattern_lower in BEARISH_REVERSAL_PATTERNS

    # REVERSAL pattern scoring
    if is_bullish_reversal and direction == 'BUY':
        reversal_matrix = {
            'STRONG_DOWN': 20, 'DOWNTREND': 18, 'SIDEWAYS': 10,
            'UPTREND': 5, 'STRONG_UP': 0,
        }
        return reversal_matrix.get(trend, 5)

    if is_bearish_reversal and direction == 'SELL':
        reversal_matrix = {
            'STRONG_UP': 20, 'UPTREND': 18, 'SIDEWAYS': 10,
            'DOWNTREND': 5, 'STRONG_DOWN': 0,
        }
        return reversal_matrix.get(trend, 5)

    # Standard trend alignment for momentum
    return TREND_ALIGNMENT_MATRIX.get((direction, trend), 10)


# =============================================================================
# FACTOR 4: S/R PROXIMITY (15 pts)
# =============================================================================

def calculate_sr_score(price: float, low_10d: float, high_10d: float, direction: str) -> Dict:
    """Calculate S/R proximity score (15 pts max)."""
    if price <= 0:
        return {'sr_score': 5, 'proximity_score': 5, 'rr_bonus': 0}

    # Proximity to support (for BUY)
    if direction == 'BUY' and low_10d > 0:
        support_pct = ((price / low_10d) - 1) * 100
        if support_pct <= 2:
            proximity = 12
        elif support_pct <= 4:
            proximity = 10
        elif support_pct <= 6:
            proximity = 7
        elif support_pct <= 10:
            proximity = 4
        else:
            proximity = 2
    # Proximity to resistance (for SELL)
    elif direction == 'SELL' and high_10d > 0:
        resist_pct = ((high_10d / price) - 1) * 100
        if resist_pct <= 2:
            proximity = 12
        elif resist_pct <= 4:
            proximity = 10
        elif resist_pct <= 6:
            proximity = 7
        elif resist_pct <= 10:
            proximity = 4
        else:
            proximity = 2
    else:
        proximity = 5

    # R:R bonus (simplified)
    rr_bonus = 0
    if low_10d > 0 and high_10d > 0:
        range_total = high_10d - low_10d
        if range_total > 0:
            if direction == 'BUY':
                risk = price - low_10d
                reward = high_10d - price
            else:
                risk = high_10d - price
                reward = price - low_10d

            if risk > 0:
                rr_ratio = reward / risk
                if rr_ratio >= 3.0:
                    rr_bonus = 3
                elif rr_ratio >= 2.0:
                    rr_bonus = 2
                elif rr_ratio >= 1.5:
                    rr_bonus = 1
                elif rr_ratio < 1.0:
                    rr_bonus = -3

    total = max(0, min(15, proximity + rr_bonus))

    return {
        'sr_score': total,
        'proximity_score': proximity,
        'rr_bonus': rr_bonus,
    }


# =============================================================================
# FACTOR 5: RS RATING (15 pts)
# =============================================================================

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
    return 1


def calculate_rs_score(rs_rating: int, rs_momentum: int, direction: str) -> Dict:
    """Calculate RS score (15 pts max)."""
    base_score = get_rs_base_score(rs_rating)

    # Momentum bonus (-1 to +2)
    if rs_momentum >= 8:
        momentum_score = 2
    elif rs_momentum >= 4:
        momentum_score = 1
    elif rs_momentum >= 0:
        momentum_score = 0
    else:
        momentum_score = -1

    # Alignment bonus (-2 to +2)
    if direction == 'BUY':
        if rs_rating >= 70:
            alignment = 2
        elif rs_rating >= 50:
            alignment = 1
        elif rs_rating >= 30:
            alignment = 0
        else:
            alignment = -2
    else:  # SELL
        if rs_rating <= 30:
            alignment = 2
        elif rs_rating <= 50:
            alignment = 1
        elif rs_rating <= 70:
            alignment = 0
        else:
            alignment = -2

    total = max(0, min(15, base_score + momentum_score + alignment))

    return {
        'rs_score': total,
        'base': base_score,
        'momentum': momentum_score,
        'alignment': alignment,
    }


# =============================================================================
# FACTOR 6: LIQUIDITY (10 pts)
# =============================================================================

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
    return 0


def calculate_liquidity_score(trading_value: float, vol_ratio: float) -> Dict:
    """Calculate liquidity score (10 pts max)."""
    tv_score = get_trading_value_score(trading_value)

    # Volume trend bonus (-2 to +2)
    if vol_ratio >= 1.5:
        vol_bonus = 2
    elif vol_ratio >= 1.2:
        vol_bonus = 1
    elif vol_ratio >= 0.8:
        vol_bonus = 0
    elif vol_ratio >= 0.5:
        vol_bonus = -1
    else:
        vol_bonus = -2

    total = max(0, min(10, tv_score + vol_bonus))

    return {
        'liquidity_score': total,
        'tv_score': tv_score,
        'vol_bonus': vol_bonus,
        'trading_value_bn': trading_value / 1e9,
    }


# =============================================================================
# MAIN: CALCULATE FULL COMPOSITE SCORE
# =============================================================================

def calculate_full_composite_score(
    symbol: str,
    pattern_name: str,
    signal_type: str,  # 'BULLISH' or 'BEARISH'
    basic_lookup: Dict,
    rs_lookup: Dict,
    vol_avg_lookup: Dict,
) -> Optional[Dict]:
    """
    Calculate FULL 100-point composite score for a single signal.

    Args:
        symbol: Stock symbol
        pattern_name: Pattern name (e.g., 'morning_star')
        signal_type: 'BULLISH' or 'BEARISH'
        basic_lookup: Pre-loaded basic data lookup
        rs_lookup: Pre-loaded RS rating lookup
        vol_avg_lookup: Pre-loaded volume average lookup

    Returns:
        Dict with all scores and metadata, or None if data missing
    """
    basic_data = basic_lookup.get(symbol)
    if basic_data is None:
        return None

    # Extract values
    price = basic_data.get('close', 0) or 0
    high = basic_data.get('high', price) or price
    low = basic_data.get('low', price) or price
    volume = basic_data.get('volume', 0) or 0
    trading_value = basic_data.get('trading_value', 0) or 0
    atr_14 = basic_data.get('atr_14', 1) or 1
    price_vs_sma20 = basic_data.get('price_vs_sma20', 0) or 0
    price_vs_sma50 = basic_data.get('price_vs_sma50', 0) or 0

    # Calculate VSA metrics
    vol_avg_20d = vol_avg_lookup.get(symbol, volume) or volume
    vol_ratio = volume / vol_avg_20d if vol_avg_20d > 0 else 1.0

    spread = high - low
    spread_ratio = spread / atr_14 if atr_14 > 0 else 1.0
    close_position = (price - low) / spread if spread > 0 else 0.5

    # Determine trend and direction
    trend = classify_trend(price_vs_sma20, price_vs_sma50)
    direction = 'BUY' if signal_type == 'BULLISH' else 'SELL'

    # === CALCULATE ALL 6 FACTORS ===

    # 1. Candlestick Score (15 pts)
    candlestick_score = calculate_candlestick_score(pattern_name, trend)

    # 2. VSA Score (25 pts)
    vsa_result = calculate_vsa_score(vol_ratio, spread_ratio, close_position, direction, trend)
    vsa_score = vsa_result['vsa_score']

    # 3. Trend Score (20 pts)
    trend_score = calculate_trend_score(direction, trend, pattern_name)

    # 4. S/R Score (15 pts)
    sr_result = calculate_sr_score(price, low, high, direction)
    sr_score = sr_result['sr_score']

    # 5. RS Score (15 pts)
    rs_data = rs_lookup.get(symbol, {'rs_rating': 50, 'rs_momentum': 0})
    rs_rating = rs_data.get('rs_rating', 50)
    rs_momentum = rs_data.get('rs_momentum', 0)
    rs_result = calculate_rs_score(rs_rating, rs_momentum, direction)
    rs_score = rs_result['rs_score']

    # 6. Liquidity Score (10 pts)
    liq_result = calculate_liquidity_score(trading_value, vol_ratio)
    liquidity_score = liq_result['liquidity_score']

    # TOTAL (already capped in individual functions)
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
        # Metadata
        'rs_rating': rs_rating,
        'trading_value_bn': liq_result['trading_value_bn'],
        'vol_ratio': round(vol_ratio, 2),
        'vsa_signal': vsa_result.get('vsa_signal', ''),
        'vsa_bias': vsa_result.get('vsa_bias', ''),
        'price': price,
    }


def calculate_full_scores_batch(signals_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate full composite scores for batch of signals.

    Args:
        signals_df: DataFrame with signals (requires: symbol, pattern_name, signal)

    Returns:
        DataFrame with all score columns added
    """
    if signals_df.empty:
        return signals_df

    # Load scoring data (cached)
    basic_lookup, rs_lookup, vol_avg_lookup = load_full_scoring_data()

    results = []
    for _, row in signals_df.iterrows():
        symbol = row.get('symbol', '')
        pattern_name = str(row.get('pattern_name', '')).lower().replace(' ', '_')
        signal_type = row.get('signal', 'BULLISH')

        result = calculate_full_composite_score(
            symbol, pattern_name, signal_type,
            basic_lookup, rs_lookup, vol_avg_lookup
        )

        if result:
            results.append(result)

    if not results:
        return pd.DataFrame()

    return pd.DataFrame(results)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_top_signals(signals_df: pd.DataFrame, direction: str = 'BUY', n: int = 10) -> pd.DataFrame:
    """Get top N signals by direction."""
    if signals_df.empty:
        return signals_df

    scored = calculate_full_scores_batch(signals_df)
    if scored.empty:
        return scored

    filtered = scored[scored['direction'] == direction]
    return filtered.sort_values('total_score', ascending=False).head(n)


def get_signal_grade(score: float) -> str:
    """Convert score to letter grade."""
    if score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    return 'F'
