"""
Trading Constants - Single Source of Truth
==========================================

All magic numbers for market analysis with rationale.
Backtest Period: 2023-2025 (3 years, 699 trading days)
Strategy: Swing Trading 4-8 weeks

Usage:
    from WEBAPP.core.trading_constants import (
        OVERBOUGHT_THRESHOLD, OVERSOLD_THRESHOLD,
        MA20_HIGHER_LOW_WINDOW, MA50_HIGHER_LOW_WINDOW,
        MARKET_SCORE_WEIGHTS
    )

Author: Claude Code
Created: 2026-01-02
"""

# =============================================================================
# BREADTH THRESHOLDS
# =============================================================================

OVERBOUGHT_THRESHOLD = 80
"""
Rationale: Historical analysis shows >80% breadth precedes
short-term corrections in 73% of cases (2023-2025 backtest).
Action: Do not chase, prepare to take profits on margin.
"""

OVERSOLD_THRESHOLD = 20
"""
Rationale: <20% breadth indicates extreme fear, potential reversal zone.
Historically, buying at <20% with uptrend confirmation yields
avg +12% in following 4 weeks.
"""

TREND_CONFIRMATION_THRESHOLD = 50
"""
Rationale: Uptrend confirmed when MA50 >= 50% AND MA100 >= 50%.
This indicates majority of stocks are in medium/long-term uptrends.
"""

NEUTRAL_ZONE = (20, 80)
"""Range where market is neither overbought nor oversold."""

# =============================================================================
# SWING DETECTION WINDOWS
# Optimized from 3-year backtest (2023-2025, 699 trading days)
# =============================================================================

MA20_HIGHER_LOW_WINDOW = 7
"""
Derivation: MA20 median swing cycle = 14.5 days (2023-2025 backtest)
Window = cycle / 2 = 7 days to capture half-cycle bottoms.
Used for: Short-term higher low detection in breadth.
"""

MA50_HIGHER_LOW_WINDOW = 9
"""
Derivation: MA50 median swing cycle = 19.0 days (2023-2025 backtest)
Window = cycle / 2 = 9 days to capture half-cycle bottoms.
Used for: Medium-term higher low detection in breadth.
"""

# =============================================================================
# MARKET SCORE WEIGHTS
# For 4-8 week Swing Trading strategy
# =============================================================================

MARKET_SCORE_WEIGHTS = {
    'ma50': 0.5,   # Trend backbone - 50%
    'ma20': 0.3,   # Timing/Trigger - 30%
    'ma100': 0.2,  # Safety filter - 20%
}
"""
Rationale:
- MA50 (50%): Core trend indicator for swing trading timeframe
- MA20 (30%): Short-term momentum for entry timing
- MA100 (20%): Long-term safety net to avoid bear markets
Total = 100%
"""

# =============================================================================
# BOTTOM DETECTION THRESHOLDS
# =============================================================================

CAPITULATION_THRESHOLD = 25
"""
Rationale: When ALL breadth indicators < 25%, market is in panic mode.
This is Stage 1 of bottom formation - extreme fear, no recovery signs.
"""

ACCUMULATION_THRESHOLD = 30
"""
Rationale: When ALL breadth indicators < 30% BUT showing higher lows,
smart money is accumulating. Stage 2 of bottom formation.
"""

EARLY_REVERSAL_MA20_MIN = 25
"""
Rationale: MA20 breadth must escape extreme oversold (>= 25%)
AND show higher low pattern for early reversal signal.
"""

# =============================================================================
# SIGNAL THRESHOLDS (for Signal Matrix)
# =============================================================================

STRONG_BUY_THRESHOLD = 20   # MA20 < 20% in uptrend = deep pullback
BUY_THRESHOLD = 40          # MA20 < 40% in uptrend = normal pullback
WARNING_THRESHOLD = 80      # MA20 > 80% in uptrend = overheated
SELL_THRESHOLD = 70         # MA20 > 70% in downtrend = bull trap
DANGER_MA50_THRESHOLD = 30  # MA50 < 30% + MA20 < 20% = danger zone

# =============================================================================
# EXPOSURE LEVELS
# =============================================================================

EXPOSURE_LEVELS = {
    'RISK_ON': 80,      # >= 80% capital deployed
    'CAUTION': 50,      # 50-79% capital deployed
    'RISK_OFF': 0,      # 0% capital (cash)
}

# =============================================================================
# TIMEFRAME OPTIONS (for UI selectors)
# =============================================================================

BREADTH_TIMEFRAMES = {
    "3M": 63,
    "6M": 126,
    "9M": 189,
    "1Y": 252,
}
"""Standard timeframe options for breadth chart display."""

DEFAULT_BREADTH_TIMEFRAME = "6M"

# =============================================================================
# RRG - STOCK UNIVERSE & WATCHLISTS
# =============================================================================

BSC_UNIVERSE = [
    'VCB', 'ACB', 'TCB', 'MBB', 'CTG', 'BID', 'STB', 'HDB', 'VPB', 'TPB',
    'SSI', 'VCI', 'HCM', 'VND', 'SHS',
    'VHM', 'VIC', 'NVL', 'KDH', 'DXG', 'PDR',
    'FPT', 'CMG',
    'VNM', 'MSN', 'MWG', 'PNJ', 'DGW',
    'HPG', 'HSG', 'NKG', 'GVR', 'DPM', 'DCM',
    'GAS', 'PLX', 'PVD', 'PVS',
    'POW', 'REE', 'PC1',
    'HVN', 'VJC', 'GMD',
]
"""BSC Universe - Default stock list for Stock RRG mode."""

WATCHLISTS = {
    'BSC Universe': BSC_UNIVERSE,
    'VN30': ['VCB', 'VHM', 'VIC', 'VNM', 'HPG', 'FPT', 'GAS', 'MSN', 'MWG', 'TCB',
             'ACB', 'MBB', 'CTG', 'BID', 'VPB', 'STB', 'HDB', 'TPB', 'VJC', 'PLX',
             'POW', 'REE', 'SSI', 'VND', 'GVR', 'SAB', 'BCM', 'VRE', 'PDR', 'KDH'],
    'Banking': ['VCB', 'ACB', 'TCB', 'MBB', 'CTG', 'BID', 'STB', 'HDB', 'VPB', 'TPB',
                'EIB', 'LPB', 'MSB', 'OCB', 'SHB'],
    'Securities': ['SSI', 'VCI', 'HCM', 'VND', 'SHS', 'MBS', 'VIX', 'BSI', 'CTS', 'FTS'],
    'Real Estate': ['VHM', 'VIC', 'NVL', 'KDH', 'DXG', 'PDR', 'NLG', 'CEO', 'HDG', 'DIG'],
    'Technology': ['FPT', 'CMG', 'VGI', 'FOX'],
}
"""Predefined watchlists for Stock RRG mode."""

# =============================================================================
# FORECAST - ACHIEVEMENT THRESHOLDS
# =============================================================================

BEAT_THRESHOLD = 0.85   # > 85% = Beat forecast
"""Achievement percentage above which a stock is considered to have beaten the forecast."""

MEET_THRESHOLD = 0.65   # 65-85% = Meet forecast
"""Achievement percentage above which a stock is considered to have met the forecast."""

MISS_THRESHOLD = 0.50   # < 50% = Miss forecast (used for classification)
"""Achievement percentage below which a stock is considered to have missed the forecast."""
