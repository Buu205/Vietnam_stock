"""Market state dataclasses for Technical Dashboard"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class MarketState:
    """Market regime and breadth state for exposure control"""

    date: datetime
    vnindex_close: float
    vnindex_change_pct: float

    # Regime (EMA9 vs EMA21)
    regime: str  # BULLISH/NEUTRAL/BEARISH
    ema9: float
    ema21: float

    # Breadth - ALL THREE MAs for line chart
    breadth_ma20_pct: float
    breadth_ma50_pct: float
    breadth_ma100_pct: float

    # Advance/Decline
    ad_ratio: float

    # Exposure Control
    exposure_level: int  # 0, 20, 40, 60, 80, 100

    # Divergence Detection
    divergence_type: Optional[str]  # BULLISH/BEARISH/None
    divergence_strength: int  # 0-3

    # Signal
    signal: str  # RISK_ON / RISK_OFF / CAUTION

    # Optional fields for recovery and bottom detection (must be at end due to default values)
    prev_breadth_ma20_pct: Optional[float] = None
    prev_breadth_ma50_pct: Optional[float] = None

    # Bottom Detection: Higher Lows pattern (confirms uptrend forming)
    # MA20: Compare min of last 3 days vs min of previous 3 days
    ma20_higher_low: bool = False      # True if recent low > previous low
    ma20_recent_low: float = 0         # Min of last 3 days
    ma20_prev_low: float = 0           # Min of previous 3 days
    ma20_rising_from_low: bool = False # Current > recent low

    # MA50: Compare min of last 5 days vs min of previous 5 days
    ma50_higher_low: bool = False
    ma50_recent_low: float = 0
    ma50_prev_low: float = 0
    ma50_rising_from_low: bool = False

    # Bottom Formation Stage: CAPITULATION, ACCUMULATING, EARLY_REVERSAL, or None
    bottom_stage: Optional[str] = None


@dataclass
class BreadthHistory:
    """Historical breadth data for line chart"""

    date: List[datetime]
    ma20_pct: List[float]
    ma50_pct: List[float]
    ma100_pct: List[float]
    vnindex_close: List[float]
