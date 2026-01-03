"""
Filter Constants
================
Centralized constants for all dashboard filters.
Single source of truth - import from here, don't redefine.

Created: 2026-01-02
"""

# Timeframe options (used by Technical, Sector, FX)
TIMEFRAME_OPTIONS = {
    "30D": 30,
    "60D": 60,
    "90D": 90,
    "180D": 180,
    "1Y": 252,
    "2Y": 504,
}

# Period options (used by Fundamental pages)
PERIOD_OPTIONS = ["Quarterly", "Yearly"]

# Default number of periods to show
DEFAULT_NUM_PERIODS = 8
MAX_NUM_PERIODS = 20
MIN_NUM_PERIODS = 4

# Signal types (used by Technical)
SIGNAL_TYPES = {
    "all": "All Signals",
    "ma_crossover": "MA Cross",
    "volume_spike": "Volume",
    "breakout": "Breakout",
    "patterns": "Patterns",
}

# Trend options (used by Stock Scanner)
TREND_OPTIONS = {
    "all": "All Trends",
    "uptrend": "Uptrend",
    "downtrend": "Downtrend",
    "sideways": "Sideways",
}

# Direction options (used by Stock Scanner)
DIRECTION_OPTIONS = {
    "all": "All Directions",
    "buy": "BUY",
    "sell": "SELL",
    "pullback": "Pullback",
    "bounce": "Bounce",
}

# Entity configurations (for fundamental_filter_bar)
ENTITY_CONFIGS = {
    "company": {
        "default_ticker": "VNM",
        "ticker_key": "selected_ticker",
        "period_key": "company_timeframe",
    },
    "bank": {
        "default_ticker": "VCB",
        "ticker_key": "selected_bank",
        "period_key": "bank_timeframe",
    },
    "security": {
        "default_ticker": "SSI",
        "ticker_key": "selected_security",
        "period_key": "security_timeframe",
    },
}

# Sort options (used by Forecast)
FORECAST_SORT_OPTIONS = {
    "upside_desc": "Upside % (High to Low)",
    "upside_asc": "Upside % (Low to High)",
    "pe_asc": "PE FWD 2025 (Low to High)",
    "pe_desc": "PE FWD 2025 (High to Low)",
    "mcap_desc": "Market Cap (High to Low)",
    "growth_desc": "Profit Growth 26F (High to Low)",
}

# Rating options (used by Forecast)
RATING_OPTIONS = ["STRONG BUY", "BUY", "HOLD", "SELL", "N/A"]
