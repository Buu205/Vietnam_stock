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

    # Bottom Detection: Higher Lows pattern using Swing Low detection
    # Swing Low = local minimum with ≥2 days bounce confirmation
    ma20_higher_low: bool = False      # True if recent swing low > previous swing low
    ma20_recent_low: float = 0         # Most recent confirmed swing low value
    ma20_prev_low: float = 0           # Previous confirmed swing low value
    ma20_rising_from_low: bool = False # Current > recent swing low

    # MA20 Pending Swing Low (1 day bounce, waiting for confirmation)
    ma20_pending_low: Optional[float] = None        # Pending swing low value
    ma20_pending_higher_low: Optional[bool] = None  # Will be Higher Low if confirmed?
    ma20_just_confirmed: bool = False               # True if swing low was just confirmed today

    # MA50: Same logic as MA20
    ma50_higher_low: bool = False
    ma50_recent_low: float = 0
    ma50_prev_low: float = 0
    ma50_rising_from_low: bool = False

    # MA50 Pending Swing Low
    ma50_pending_low: Optional[float] = None
    ma50_pending_higher_low: Optional[bool] = None
    ma50_just_confirmed: bool = False               # True if swing low was just confirmed today

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
