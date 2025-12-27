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


@dataclass
class BreadthHistory:
    """Historical breadth data for line chart"""

    date: List[datetime]
    ma20_pct: List[float]
    ma50_pct: List[float]
    ma100_pct: List[float]
    vnindex_close: List[float]
