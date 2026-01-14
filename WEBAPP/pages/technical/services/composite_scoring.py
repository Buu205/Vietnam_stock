"""
Composite Signal Scoring Calculator
====================================

6-Factor scoring system for trading signals (v2.1):
1. Candlestick Pattern (15 pts max)
2. VSA Context (25 pts max, can be negative)
3. Trend Alignment (20 pts max, can be negative)
4. S/R Proximity (15 pts max)
5. RS Rating (15 pts max)
6. Liquidity (10 pts max)

Total: 100 pts max

Reference: composite_signal_scoring_logic.md
Author: Claude Code
Date: 2026-01-11
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

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

# Pattern base scores (15 pts max)
PATTERN_SCORES = {
    # Strong reversal (12-15 pts)
    'morning_star': 15,
    'evening_star': 15,
    'three_white_soldiers': 15,
    'three_black_crows': 15,
    'bullish_engulfing': 14,
    'bearish_engulfing': 14,
    # Medium reversal (9-11 pts)
    'hammer': 11,
    'inverted_hammer': 10,
    'shooting_star': 11,
    'hanging_man': 10,
    'piercing_line': 10,
    'dark_cloud_cover': 10,
    # Weak/Indecision (5-8 pts)
    'doji': 7,
    'spinning_top': 6,
    'harami': 8,
}

# Bullish reversal patterns (for context multiplier)
BULLISH_REVERSAL_PATTERNS = [
    'morning_star', 'hammer', 'bullish_engulfing', 'inverted_hammer',
    'piercing_line', 'three_white_soldiers', 'harami'
]

# Bearish reversal patterns (for context multiplier)
BEARISH_REVERSAL_PATTERNS = [
    'evening_star', 'shooting_star', 'bearish_engulfing', 'hanging_man',
    'dark_cloud_cover', 'three_black_crows'
]


# =============================================================================
# SCORING FUNCTIONS
# =============================================================================

def calculate_pattern_score(
    pattern_name: str,
    trend: str,
    strength: float = 100
) -> Tuple[float, float]:
    """
    Calculate pattern score with context multiplier (Section 2).

    Args:
        pattern_name: Pattern name (e.g., 'morning_star')
        trend: Current trend ('STRONG_UP', 'UPTREND', 'SIDEWAYS', 'DOWNTREND', 'STRONG_DOWN')
        strength: Pattern strength from detector (0-100)

    Returns:
        (base_score, context_multiplier)
    """
    if not pattern_name:
        return 0, 1.0

    pattern_lower = str(pattern_name).lower().replace(' ', '_')

    # Get base score
    base_score = PATTERN_SCORES.get(pattern_lower, 8)

    # Scale by pattern strength if provided (with floor at 70%)
    # This prevents weak patterns from getting too low scores
    if strength and strength <= 1:
        strength = strength * 100
    if strength and strength < 100:
        # Floor at 70% - so 30% strength still gets 70% of base score
        strength_multiplier = max(0.7, strength / 100)
        base_score = base_score * strength_multiplier

    # Context multiplier (v2.1)
    multiplier = 1.0

    if pattern_lower in BULLISH_REVERSAL_PATTERNS:
        if trend in ['STRONG_DOWN', 'DOWNTREND']:
            multiplier = 1.2  # Perfect context for bullish reversal
        elif trend == 'SIDEWAYS':
            multiplier = 0.9  # Less meaningful in sideways
        elif trend in ['STRONG_UP', 'UPTREND']:
            multiplier = 0.8  # Counter-trend, less reliable

    elif pattern_lower in BEARISH_REVERSAL_PATTERNS:
        if trend in ['STRONG_UP', 'UPTREND']:
            multiplier = 1.2  # Perfect context for bearish reversal
        elif trend == 'SIDEWAYS':
            multiplier = 0.9
        elif trend in ['STRONG_DOWN', 'DOWNTREND']:
            multiplier = 0.8

    # Apply multiplier and cap at 15
    final_score = min(15, base_score * multiplier)

    return round(final_score, 1), round(multiplier, 2)


def calculate_vsa_score(
    money_flow_data: Optional[pd.Series],
    direction: str
) -> Tuple[float, str]:
    """
    Calculate VSA score (Section 3).

    Uses available columns: money_flow_signal, mfi_14, cmf_20
    (buy_value/sell_value not available in current data)

    Args:
        money_flow_data: Money flow data for the ticker
        direction: Signal direction ('BUY', 'SELL', etc.)

    Returns:
        (vsa_score, vsa_context)  # score 0-15 for aligned, negative for conflict
    """
    if money_flow_data is None or money_flow_data.empty:
        return 0, 'Neutral'

    # Use money_flow_signal (pre-calculated in pipeline)
    mf_signal = money_flow_data.get('money_flow_signal', 'NEUTRAL')
    mfi = money_flow_data.get('mfi_14', 50) or 50

    # Determine VSA context from money_flow_signal
    if mf_signal == 'STRONG_ACCUMULATION':
        vsa_context = 'Bullish'
        base_score = 15  # Max bullish
    elif mf_signal == 'ACCUMULATION':
        vsa_context = 'Bullish'
        base_score = 10
    elif mf_signal == 'STRONG_DISTRIBUTION':
        vsa_context = 'Bearish'
        base_score = -15  # Max bearish
    elif mf_signal == 'DISTRIBUTION':
        vsa_context = 'Bearish'
        base_score = -10
    else:
        vsa_context = 'Neutral'
        base_score = 0

    # MFI bonus (extreme readings)
    if mfi >= 70:  # Overbought - confirms accumulation
        if vsa_context == 'Bullish':
            base_score = min(15, base_score + 3)
    elif mfi <= 30:  # Oversold - confirms distribution
        if vsa_context == 'Bearish':
            base_score = max(-15, base_score - 3)

    # Alignment logic
    if direction == 'BUY' and vsa_context == 'Bullish':
        score = base_score  # Aligned - positive
    elif direction == 'SELL' and vsa_context == 'Bearish':
        score = abs(base_score)  # Aligned - flip to positive for SELL
    elif direction == 'BUY' and vsa_context == 'Bearish':
        score = base_score  # Conflict - negative penalizes BUY
    elif direction == 'SELL' and vsa_context == 'Bullish':
        score = -base_score  # Conflict - negative penalizes SELL
    else:
        score = 0  # Neutral

    return round(score, 1), vsa_context


def calculate_trend_score(
    trend: str,
    direction: str,
    pattern_name: str = ''
) -> float:
    """
    Calculate trend alignment score (Section 4).

    For REVERSAL patterns (swing trade bottom/top detection):
    - Bullish reversal in DOWNTREND = HIGH score (tạo đáy)
    - Bearish reversal in UPTREND = HIGH score (tạo đỉnh)

    For MOMENTUM/CONTINUATION patterns:
    - BUY in UPTREND = HIGH score
    - SELL in DOWNTREND = HIGH score

    Args:
        trend: Current trend
        direction: Signal direction
        pattern_name: Pattern name to detect reversal type

    Returns:
        trend_score (-10 to +20)
    """
    pattern_lower = str(pattern_name).lower().replace(' ', '_')

    # Check if pattern is reversal type
    is_bullish_reversal = pattern_lower in BULLISH_REVERSAL_PATTERNS
    is_bearish_reversal = pattern_lower in BEARISH_REVERSAL_PATTERNS

    # REVERSAL pattern scoring (for swing trading 10-15 sessions)
    if is_bullish_reversal and direction == 'BUY':
        # Bullish reversal patterns WANT downtrend (potential bottom)
        reversal_matrix = {
            'STRONG_DOWN': 20,  # Perfect: reversal at bottom
            'DOWNTREND': 18,
            'SIDEWAYS': 10,     # OK: consolidation breakout
            'UPTREND': 5,       # Weak: continuation, not reversal
            'STRONG_UP': 0,     # Bad: already up, no room
        }
        return reversal_matrix.get(trend, 5)

    if is_bearish_reversal and direction == 'SELL':
        # Bearish reversal patterns WANT uptrend (potential top)
        reversal_matrix = {
            'STRONG_UP': 20,    # Perfect: reversal at top
            'UPTREND': 18,
            'SIDEWAYS': 10,
            'DOWNTREND': 5,
            'STRONG_DOWN': 0,
        }
        return reversal_matrix.get(trend, 5)

    # MOMENTUM/CONTINUATION scoring (default behavior)
    alignment_matrix = {
        # (trend, direction): score
        ('STRONG_UP', 'BUY'): 20,
        ('STRONG_UP', 'PULLBACK'): 15,
        ('UPTREND', 'BUY'): 18,
        ('UPTREND', 'PULLBACK'): 12,
        ('SIDEWAYS', 'BUY'): 5,
        ('SIDEWAYS', 'SELL'): 5,
        ('DOWNTREND', 'SELL'): 18,
        ('DOWNTREND', 'BOUNCE'): 12,
        ('STRONG_DOWN', 'SELL'): 20,
        ('STRONG_DOWN', 'BOUNCE'): 15,
        # Counter-trend (negative for momentum)
        ('STRONG_UP', 'SELL'): -10,
        ('UPTREND', 'SELL'): -5,
        ('STRONG_DOWN', 'BUY'): -10,
        ('DOWNTREND', 'BUY'): -5,
    }

    key = (trend, direction)
    return alignment_matrix.get(key, 0)


def calculate_sr_score(
    ticker: str,
    current_price: float,
    basic_data: Optional[pd.DataFrame] = None
) -> Tuple[float, dict]:
    """
    Calculate S/R proximity score (Section 5).

    Args:
        ticker: Stock symbol
        current_price: Current price
        basic_data: Basic data with high/low for Fib calculation

    Returns:
        (sr_score, sr_info)
    """
    if basic_data is None or basic_data.empty or current_price <= 0:
        return 0, {}

    ticker_data = basic_data[basic_data['symbol'] == ticker].sort_values('date', ascending=False)
    if len(ticker_data) < 10:
        return 0, {}

    # Get swing high/low from 10 days
    data_10d = ticker_data.head(10)
    swing_high = data_10d['high'].max()
    swing_low = data_10d['low'].min()

    # Get Fib range from 30 days
    data_30d = ticker_data.head(30)
    fib_high = data_30d['high'].max()
    fib_low = data_30d['low'].min()
    fib_range = fib_high - fib_low

    # Calculate ATR for validation
    atr_14 = (data_30d.head(14)['high'] - data_30d.head(14)['low']).mean()

    # Validate Fib range (v2.1 - skip if sideways)
    fib_valid = fib_range >= (atr_14 * 5)

    sr_info = {
        'swing_high': swing_high,
        'swing_low': swing_low,
        'fib_high': fib_high,
        'fib_low': fib_low,
        'fib_valid': fib_valid
    }

    # Calculate proximity to support
    if swing_low > 0:
        support_pct = ((current_price / swing_low) - 1) * 100

        # Score based on proximity (closer = higher score)
        if support_pct <= 2:  # Within 2% of support
            sr_score = 15
        elif support_pct <= 5:
            sr_score = 12
        elif support_pct <= 10:
            sr_score = 8
        else:
            sr_score = 5
    else:
        sr_score = 5

    return sr_score, sr_info


def calculate_rs_score(
    ticker: str,
    rs_data: Optional[pd.DataFrame] = None
) -> Tuple[float, float, float]:
    """
    Calculate RS Rating score (Section 6).

    Args:
        ticker: Stock symbol
        rs_data: RS Rating data

    Returns:
        (rs_score, rs_rating, rs_momentum)
    """
    if rs_data is None or rs_data.empty:
        return 0, 0, 0

    ticker_rs = rs_data[rs_data['symbol'] == ticker].sort_values('date', ascending=False)
    if ticker_rs.empty:
        return 0, 0, 0

    # Get current RS Rating
    rs_rating = ticker_rs.iloc[0].get('rs_rating', 0) or 0

    # Get RS momentum (5-day change)
    rs_momentum = 0
    if len(ticker_rs) >= 5:
        rs_5d_ago = ticker_rs.iloc[4].get('rs_rating', rs_rating) or rs_rating
        rs_momentum = rs_rating - rs_5d_ago

    # Base score from RS Rating (15 pts max)
    if rs_rating >= 80:
        base_score = 15
    elif rs_rating >= 70:
        base_score = 13
    elif rs_rating >= 60:
        base_score = 10
    elif rs_rating >= 50:
        base_score = 7
    elif rs_rating >= 30:
        base_score = 5
    else:
        base_score = 0

    # Momentum bonus (max 2 pts, v2.1)
    if rs_momentum >= 10:
        momentum_bonus = 2
    elif rs_momentum >= 5:
        momentum_bonus = 1
    else:
        momentum_bonus = 0

    final_score = min(15, base_score + momentum_bonus)

    return final_score, rs_rating, rs_momentum


def calculate_liquidity_score(trading_value: float) -> float:
    """
    Calculate liquidity score (Section 7, v2.1 thresholds).

    Args:
        trading_value: Trading value in VND

    Returns:
        liquidity_score (0-10)
    """
    if not trading_value or trading_value <= 0:
        return 0

    # Convert to billion
    tv_billion = trading_value / 1e9

    # v2.1 thresholds (lowered)
    if tv_billion >= 100:
        return 10
    elif tv_billion >= 50:
        return 8
    elif tv_billion >= 30:
        return 7
    elif tv_billion >= 10:
        return 5
    else:
        return 0


def calculate_vsa_conflict_multiplier(vsa_score: float) -> float:
    """
    Calculate VSA conflict multiplier (v2.1 Section 3.8).

    Args:
        vsa_score: VSA score (can be negative)

    Returns:
        conflict_multiplier (0.6 to 1.0)
    """
    if vsa_score <= -15:
        return 0.6  # Strong conflict - 40% penalty
    elif vsa_score < 0:
        return 0.8  # Mild conflict - 20% penalty
    return 1.0


# =============================================================================
# MAIN SCORING FUNCTION
# =============================================================================

@cache_data(ttl=300)
def load_scoring_data() -> Tuple[dict, dict, dict, pd.DataFrame]:
    """
    Load all data needed for scoring with caching.

    OPTIMIZED: Uses basic_data_latest.parquet (146KB) instead of full basic_data (20MB).
    Returns pre-computed lookup dictionaries for O(1) access.

    Returns:
        (basic_lookup, mf_lookup, rs_lookup, basic_latest_df)
    """
    # =========================================================================
    # 1. BASIC DATA - Load lightweight latest snapshot
    # =========================================================================
    latest_path = Path("DATA/processed/technical/basic_data_latest.parquet")
    if latest_path.exists():
        basic_latest = pd.read_parquet(latest_path)
    else:
        # Fallback to full file if latest not available
        basic_path = Path("DATA/processed/technical/basic_data.parquet")
        if basic_path.exists():
            basic_df = pd.read_parquet(basic_path)
            basic_latest = (
                basic_df.sort_values('date', ascending=False)
                .groupby('symbol', as_index=False)
                .first()
            )
        else:
            basic_latest = pd.DataFrame()

    # Pre-compute trend from SMA
    if not basic_latest.empty and 'price_vs_sma20' in basic_latest.columns:
        def derive_trend(row):
            vs20 = row.get('price_vs_sma20', 0) or 0
            vs50 = row.get('price_vs_sma50', 0) or 0
            if vs20 > 0.05 and vs50 > 0.05:
                return 'STRONG_UP'
            elif vs20 > 0 and vs50 > 0:
                return 'UPTREND'
            elif vs20 < -0.05 and vs50 < -0.05:
                return 'STRONG_DOWN'
            elif vs20 < 0 and vs50 < 0:
                return 'DOWNTREND'
            return 'SIDEWAYS'
        basic_latest['trend'] = basic_latest.apply(derive_trend, axis=1)

    # Create basic lookup dict: symbol -> row dict
    basic_lookup = {}
    if not basic_latest.empty:
        for _, row in basic_latest.iterrows():
            basic_lookup[row['symbol']] = row.to_dict()

    # =========================================================================
    # 2. MONEY FLOW - Load and create lookup
    # =========================================================================
    mf_lookup = {}
    mf_path = Path("DATA/processed/technical/money_flow/individual_money_flow.parquet")
    if mf_path.exists():
        mf_df = pd.read_parquet(mf_path)
        if not mf_df.empty:
            # Get latest per symbol
            if 'date' in mf_df.columns:
                mf_df = mf_df.sort_values('date', ascending=False)
            mf_latest = mf_df.groupby('symbol', as_index=False).first()
            for _, row in mf_latest.iterrows():
                mf_lookup[row['symbol']] = row.to_dict()

    # =========================================================================
    # 3. RS RATING - Load and create lookup with momentum
    # =========================================================================
    rs_lookup = {}
    rs_path = Path("DATA/processed/technical/rs_rating/stock_rs_rating_1y.parquet")
    if rs_path.exists():
        rs_df = pd.read_parquet(rs_path)
        if not rs_df.empty:
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

    return basic_lookup, mf_lookup, rs_lookup, basic_latest


def calculate_composite_scores(signals_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate composite scores for all signals.

    OPTIMIZED: Uses pre-computed lookup dictionaries for O(1) access.
    - basic_lookup: symbol -> {trading_value, trend, high, low, ...}
    - mf_lookup: symbol -> {buy_value, sell_value, net_value}
    - rs_lookup: symbol -> {rs_rating, rs_momentum}

    Args:
        signals_df: DataFrame with signals (must have: symbol, date, type_label, direction)

    Returns:
        DataFrame with additional score columns
    """
    if signals_df.empty:
        return signals_df

    # Drop existing composite_score if present (will be recalculated)
    cols_to_drop = [c for c in ['composite_score', 'context_score'] if c in signals_df.columns]
    if cols_to_drop:
        signals_df = signals_df.drop(columns=cols_to_drop)

    # Load scoring data (cached with pre-computed lookups)
    basic_lookup, mf_lookup, rs_lookup, basic_latest = load_scoring_data()

    # ==========================================================================
    # ENRICH SIGNALS WITH BASIC DATA (trading_value, trend) via merge
    # ==========================================================================
    if not basic_latest.empty:
        # Merge trading_value if not present
        if 'trading_value' not in signals_df.columns and 'trading_value' in basic_latest.columns:
            signals_df = signals_df.merge(
                basic_latest[['symbol', 'trading_value']],
                on='symbol', how='left'
            )
        # Merge trend if not present
        if 'trend' not in signals_df.columns and 'trend' in basic_latest.columns:
            signals_df = signals_df.merge(
                basic_latest[['symbol', 'trend']],
                on='symbol', how='left'
            )
            signals_df['trend'] = signals_df['trend'].fillna('SIDEWAYS')

    # ==========================================================================
    # CALCULATE SCORES using O(1) dict lookups (NOT O(n) DataFrame filtering)
    # ==========================================================================
    scores = []

    for _, row in signals_df.iterrows():
        symbol = row.get('symbol', '')
        pattern = row.get('type_label', row.get('pattern_name', ''))
        direction = row.get('direction', 'NEUTRAL')
        trend = row.get('trend', 'SIDEWAYS') or 'SIDEWAYS'
        strength = row.get('strength', 100)
        trading_value = row.get('trading_value', 0) or 0
        price = row.get('price', 0) or 0

        # 1. Pattern Score
        pattern_score, _ = calculate_pattern_score(pattern, trend, strength)

        # 2. VSA Score (O(1) lookup)
        mf_data = mf_lookup.get(symbol)
        if mf_data:
            mf_series = pd.Series(mf_data)
            vsa_score, vsa_context = calculate_vsa_score(mf_series, direction)
        else:
            vsa_score, vsa_context = 0, 'Neutral'

        # 3. Trend Score (with pattern awareness for reversal detection)
        trend_score = calculate_trend_score(trend, direction, pattern)

        # 4. S/R Score (O(1) lookup from basic_lookup)
        basic_data = basic_lookup.get(symbol, {})
        if basic_data and price > 0:
            # Use low as support proxy
            swing_low = basic_data.get('low', 0)
            if swing_low > 0:
                support_pct = ((price / swing_low) - 1) * 100
                if support_pct <= 2:
                    sr_score = 15
                elif support_pct <= 5:
                    sr_score = 12
                elif support_pct <= 10:
                    sr_score = 8
                else:
                    sr_score = 5
            else:
                sr_score = 5
        else:
            sr_score = 5

        # 5. RS Score (O(1) lookup)
        rs_data = rs_lookup.get(symbol, {})
        rs_rating = rs_data.get('rs_rating', 0)
        rs_momentum = rs_data.get('rs_momentum', 0)

        if rs_rating >= 80:
            rs_score = 15
        elif rs_rating >= 70:
            rs_score = 13
        elif rs_rating >= 60:
            rs_score = 10
        elif rs_rating >= 50:
            rs_score = 7
        elif rs_rating >= 30:
            rs_score = 5
        else:
            rs_score = 0

        # Momentum bonus (max 2 pts)
        if rs_momentum >= 10:
            rs_score = min(15, rs_score + 2)
        elif rs_momentum >= 5:
            rs_score = min(15, rs_score + 1)

        # 6. Liquidity Score
        liquidity_score = calculate_liquidity_score(trading_value)

        # Calculate raw total
        raw_total = pattern_score + vsa_score + trend_score + sr_score + rs_score + liquidity_score

        # Apply VSA conflict multiplier (v2.1)
        conflict_mult = calculate_vsa_conflict_multiplier(vsa_score)
        composite_score = max(0, min(100, raw_total * conflict_mult))

        # Determine alignment
        is_aligned = (
            (trend in ['STRONG_UP', 'UPTREND'] and direction in ['BUY', 'PULLBACK']) or
            (trend in ['STRONG_DOWN', 'DOWNTREND'] and direction in ['SELL', 'BOUNCE'])
        )

        scores.append({
            'composite_score': round(composite_score, 1),
            'pattern_score': round(pattern_score, 1),
            'vsa_score': round(vsa_score, 1),
            'trend_score': round(trend_score, 1),
            'sr_score': round(sr_score, 1),
            'rs_score': round(rs_score, 1),
            'liquidity_score': round(liquidity_score, 1),
            'vsa_context': vsa_context,
            'is_aligned': is_aligned,
            'rs_rating': rs_rating,
        })

    # Add scores to DataFrame
    scores_df = pd.DataFrame(scores)
    result = pd.concat([signals_df.reset_index(drop=True), scores_df], axis=1)

    return result
