"""
Base Models
===========

Shared enums and base models for bsc_mcp server.
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Entity types for Vietnamese stocks."""
    BANK = "BANK"
    COMPANY = "COMPANY"
    INSURANCE = "INSURANCE"
    SECURITY = "SECURITY"
    ALL = "ALL"


class Period(str, Enum):
    """Financial reporting period."""
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"


class ValuationMetric(str, Enum):
    """Valuation metrics."""
    PE = "PE"
    PB = "PB"
    PS = "PS"
    EV_EBITDA = "EV_EBITDA"


class AlertType(str, Enum):
    """Technical alert types."""
    BREAKOUT = "breakout"
    MA_CROSSOVER = "ma_crossover"
    VOLUME_SPIKE = "volume_spike"
    PATTERNS = "patterns"
    ALL = "all"


class SortOrder(str, Enum):
    """Sort order for results."""
    ASC = "asc"
    DESC = "desc"


class MacroIndicator(str, Enum):
    """Macro economic indicators."""
    DEPOSIT_RATE = "deposit_rate"
    LENDING_RATE = "lending_rate"
    USD_VND = "usd_vnd"
    GOV_BOND_10Y = "gov_bond_10y"
    CPI = "cpi"


class Commodity(str, Enum):
    """Commodity types."""
    GOLD = "gold"
    OIL_BRENT = "oil_brent"
    STEEL = "steel"
    RUBBER = "rubber"


# =============================================================================
# Response Models
# =============================================================================

class TickerInfo(BaseModel):
    """Basic ticker information."""
    symbol: str
    entity_type: Optional[str] = None
    sector: Optional[str] = None
    exchange: Optional[str] = None
    industry_code: Optional[str] = None


class FundamentalMetrics(BaseModel):
    """Key fundamental metrics."""
    symbol: str
    period: str
    year: int
    quarter: Optional[int] = None
    net_revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    npatmi: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    gross_margin: Optional[float] = None
    net_margin: Optional[float] = None
    eps: Optional[float] = None
    bvps: Optional[float] = None


class ValuationData(BaseModel):
    """Valuation data point."""
    symbol: str
    date: str
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None


class TechnicalIndicators(BaseModel):
    """Technical indicator values."""
    symbol: str
    date: str
    close: float
    volume: float
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None


class BSCForecast(BaseModel):
    """BSC analyst forecast."""
    symbol: str
    target_price: Optional[float] = None
    current_price: Optional[float] = None
    upside_pct: Optional[float] = None
    rating: Optional[str] = None
    eps_2025f: Optional[float] = None
    eps_2026f: Optional[float] = None


class SectorScore(BaseModel):
    """Sector analysis score."""
    sector: str
    date: str
    fa_score: Optional[float] = None
    ta_score: Optional[float] = None
    combined_score: Optional[float] = None
    signal: Optional[str] = None
    signal_strength: Optional[int] = None
