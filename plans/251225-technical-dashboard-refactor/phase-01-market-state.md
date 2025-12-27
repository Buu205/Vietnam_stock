# Phase 1: MarketState Dataclass + Service

**Goal:** Create data models and service layer for Technical Dashboard

---

## 0. TA Indicator Base Classes (NEW - From Review)

> **Added 2025-12-25**: Consolidate all TA calculations into reusable classes.

```python
# File: PROCESSORS/technical/indicators/base.py

from abc import ABC, abstractmethod
import pandas as pd
from dataclasses import dataclass
from typing import Any

class TAIndicator(ABC):
    """Base class for all TA indicators"""

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate indicator values, return DataFrame with new columns"""
        pass

    @abstractmethod
    def get_latest(self, df: pd.DataFrame) -> dict:
        """Get latest indicator value as dict"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Indicator name for display"""
        pass


# File: PROCESSORS/technical/indicators/quadrant.py

from enum import Enum

class Quadrant(Enum):
    LEADING = "LEADING"      # RS > 1, Momentum > 0
    WEAKENING = "WEAKENING"  # RS > 1, Momentum <= 0
    LAGGING = "LAGGING"      # RS <= 1, Momentum <= 0
    IMPROVING = "IMPROVING"  # RS <= 1, Momentum > 0

def determine_quadrant(rs_ratio: float, rs_momentum: float) -> Quadrant:
    """
    Common quadrant determination for RRG charts.
    Used by both Sector RRG and Stock RRG.

    Args:
        rs_ratio: Relative strength ratio (1.0 = neutral)
        rs_momentum: Rate of change of RS ratio

    Returns:
        Quadrant enum value
    """
    if rs_ratio > 1 and rs_momentum > 0:
        return Quadrant.LEADING
    elif rs_ratio > 1 and rs_momentum <= 0:
        return Quadrant.WEAKENING
    elif rs_ratio <= 1 and rs_momentum <= 0:
        return Quadrant.LAGGING
    else:
        return Quadrant.IMPROVING


# File: PROCESSORS/technical/indicators/relative_strength.py

import pandas as pd
import numpy as np
from .base import TAIndicator

class RSRatioCalculator(TAIndicator):
    """Calculate RS Ratio vs benchmark"""

    def __init__(self, benchmark_col: str = 'vnindex_close', period: int = 14):
        self.benchmark_col = benchmark_col
        self.period = period

    @property
    def name(self) -> str:
        return "RS Ratio"

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RS Ratio = (stock_close / benchmark) normalized to 100
        """
        df = df.copy()
        if self.benchmark_col not in df.columns:
            raise ValueError(f"Missing benchmark column: {self.benchmark_col}")

        # RS Line = stock / benchmark
        df['rs_line'] = df['close'] / df[self.benchmark_col]

        # Normalize: RS Ratio = (current RS / SMA of RS) * 100
        df['rs_ratio'] = (df['rs_line'] / df['rs_line'].rolling(self.period).mean()) * 100

        return df

    def get_latest(self, df: pd.DataFrame) -> dict:
        result = self.calculate(df)
        latest = result.iloc[-1]
        return {
            'rs_ratio': latest['rs_ratio'],
            'rs_line': latest['rs_line']
        }


class RSMomentumCalculator(TAIndicator):
    """Calculate RS Momentum (rate of change of RS Ratio)"""

    def __init__(self, period: int = 5):
        self.period = period

    @property
    def name(self) -> str:
        return "RS Momentum"

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if 'rs_ratio' not in df.columns:
            raise ValueError("Run RSRatioCalculator first")

        # Momentum = current RS Ratio - RS Ratio N periods ago
        df['rs_momentum'] = df['rs_ratio'] - df['rs_ratio'].shift(self.period)

        return df

    def get_latest(self, df: pd.DataFrame) -> dict:
        result = self.calculate(df)
        return {'rs_momentum': result.iloc[-1]['rs_momentum']}


# File: PROCESSORS/technical/indicators/volume_context.py

from enum import Enum
from dataclasses import dataclass
import pandas as pd

class VolumeContext(Enum):
    HIGH = "HIGH"    # RVOL >= 1.5
    AVG = "AVG"      # 0.8 <= RVOL < 1.5
    LOW = "LOW"      # RVOL < 0.8

@dataclass
class VolumeAnalysis:
    context: VolumeContext
    rvol: float
    interpretation: str

class VolumeContextAnalyzer:
    """Analyze volume context for signal validation"""

    def __init__(self, ma_period: int = 20):
        self.ma_period = ma_period

    def analyze(self, df: pd.DataFrame) -> VolumeAnalysis:
        """
        Analyze volume relative to moving average.

        Args:
            df: DataFrame with 'volume' column

        Returns:
            VolumeAnalysis with context and interpretation
        """
        if 'volume' not in df.columns:
            return VolumeAnalysis(VolumeContext.AVG, 1.0, "No volume data")

        latest_vol = df.iloc[-1]['volume']
        avg_vol = df['volume'].rolling(self.ma_period).mean().iloc[-1]

        rvol = latest_vol / avg_vol if avg_vol > 0 else 1.0

        if rvol >= 1.5:
            context = VolumeContext.HIGH
            interpretation = f"Vol cao ({rvol:.1f}x) - xác nhận mạnh"
        elif rvol >= 0.8:
            context = VolumeContext.AVG
            interpretation = f"Vol TB ({rvol:.1f}x) - trung tính"
        else:
            context = VolumeContext.LOW
            interpretation = f"Vol thấp ({rvol:.1f}x) - thiếu xác nhận"

        return VolumeAnalysis(context, rvol, interpretation)


# File: PROCESSORS/technical/indicators/confidence.py

from dataclasses import dataclass
from typing import Dict

@dataclass
class ConfidenceScore:
    score: int           # 0-100
    components: Dict[str, int]  # Breakdown
    interpretation: str  # Vietnamese

class ConfidenceScoreCalculator:
    """Calculate confidence score for trading signals"""

    WEIGHTS = {
        'pattern': 25,      # Candlestick pattern strength
        'volume': 20,       # Volume confirmation
        'chart_pattern': 20,  # Chart pattern
        'sector_rank': 20,  # Sector strength
        'trend': 15,        # Price vs MA alignment
    }

    def calculate(
        self,
        candle_signal: str,
        rvol: float,
        chart_pattern: str,
        sector_rank: int,
        price_vs_ma20: float,
        price_vs_ma50: float
    ) -> ConfidenceScore:
        """
        Calculate confidence score 0-100.

        Returns:
            ConfidenceScore with breakdown and interpretation
        """
        components = {}

        # 1. Candlestick pattern (0-25)
        if candle_signal == 'BULLISH':
            components['pattern'] = 25
        elif candle_signal == 'NEUTRAL':
            components['pattern'] = 12
        else:
            components['pattern'] = 0

        # 2. Volume (0-20)
        if rvol >= 2.0:
            components['volume'] = 20
        elif rvol >= 1.5:
            components['volume'] = 15
        elif rvol >= 1.0:
            components['volume'] = 10
        else:
            components['volume'] = 5

        # 3. Chart pattern (0-20)
        strong_patterns = ['Cup&Handle', 'Breakout', 'Ascending Triangle']
        if chart_pattern in strong_patterns:
            components['chart_pattern'] = 20
        elif chart_pattern:
            components['chart_pattern'] = 10
        else:
            components['chart_pattern'] = 0

        # 4. Sector rank (0-20)
        if sector_rank <= 3:
            components['sector_rank'] = 20
        elif sector_rank <= 6:
            components['sector_rank'] = 15
        elif sector_rank <= 10:
            components['sector_rank'] = 10
        else:
            components['sector_rank'] = 5

        # 5. Trend alignment (0-15)
        above_ma20 = price_vs_ma20 > 0 if price_vs_ma20 else False
        above_ma50 = price_vs_ma50 > 0 if price_vs_ma50 else False
        if above_ma20 and above_ma50:
            components['trend'] = 15
        elif above_ma20:
            components['trend'] = 10
        else:
            components['trend'] = 0

        total = sum(components.values())

        # Interpretation
        if total >= 80:
            interp = "Rất tự tin - tất cả yếu tố đồng thuận"
        elif total >= 60:
            interp = "Tự tin cao - đa số yếu tố tích cực"
        elif total >= 40:
            interp = "Trung bình - cần thêm xác nhận"
        else:
            interp = "Thấp - nhiều yếu tố chưa thuận lợi"

        return ConfidenceScore(total, components, interp)
```

**File Structure cho Indicators:**

```
PROCESSORS/technical/indicators/
├── __init__.py
├── base.py                 # TAIndicator abstract base
├── quadrant.py             # Quadrant determination (shared)
├── relative_strength.py    # RSRatioCalculator, RSMomentumCalculator
├── volume_context.py       # VolumeContextAnalyzer
├── confidence.py           # ConfidenceScoreCalculator
└── candlestick_patterns.py # CandlestickPatternDetector (ta-lib wrapper)
```

---

## 1. MarketState Dataclass

```python
# File: WEBAPP/core/models/market_state.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

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
    breadth_ma100_pct: float  # ADDED

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

    date: list[datetime]
    ma20_pct: list[float]
    ma50_pct: list[float]
    ma100_pct: list[float]
    vnindex_close: list[float]
```

---

## 2. TA Dashboard Service (Updated with Caching)

> **Updated 2025-12-25**: Added `@st.cache_data` decorators and singleton pattern.

```python
# File: WEBAPP/pages/technical/services/ta_dashboard_service.py

import streamlit as st
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# ==================== SINGLETON PATTERN ====================

@st.cache_resource
def get_ta_service() -> 'TADashboardService':
    """
    Get singleton TADashboardService instance.
    Call this from main dashboard, pass to all components.

    Usage:
        # In technical_dashboard.py
        service = get_ta_service()
        render_market_overview(service)
        render_sector_rotation(service)
    """
    return TADashboardService()


class TADashboardService:
    """Unified service for Technical Dashboard"""

    DATA_ROOT = Path("DATA/processed/technical")

    def __init__(self):
        # No preloading - use lazy loading with caching
        pass

    # ==================== MARKET LAYER ====================

    def get_market_state(self) -> MarketState:
        """Get current market state with regime and breadth"""
        vnindex = self._load_vnindex()
        breadth = self._load_market_breadth()

        latest_vn = vnindex.iloc[-1]
        latest_br = breadth.iloc[-1]

        # Regime detection
        ema9 = latest_vn.get('ema9', latest_vn.get('ema_9', 0))
        ema21 = latest_vn.get('ema21', latest_vn.get('ema_21', 0))
        regime = self._get_regime(ema9, ema21)

        # Breadth values
        ma20_pct = latest_br.get('above_ma20_pct', latest_br.get('pct_above_ma20', 0))
        ma50_pct = latest_br.get('above_ma50_pct', latest_br.get('pct_above_ma50', 0))
        ma100_pct = latest_br.get('above_ma100_pct', latest_br.get('pct_above_ma100', 0))

        # Exposure level
        exposure = self._calculate_exposure(regime, ma20_pct)

        # Signal
        signal = "RISK_ON" if exposure >= 60 else ("RISK_OFF" if exposure == 0 else "CAUTION")

        return MarketState(
            date=latest_vn['date'],
            vnindex_close=latest_vn['close'],
            vnindex_change_pct=latest_vn.get('change_pct', 0),
            regime=regime,
            ema9=ema9,
            ema21=ema21,
            breadth_ma20_pct=ma20_pct,
            breadth_ma50_pct=ma50_pct,
            breadth_ma100_pct=ma100_pct,
            ad_ratio=latest_br.get('ad_ratio', 1.0),
            exposure_level=exposure,
            divergence_type=None,  # TODO: implement
            divergence_strength=0,
            signal=signal
        )

    def get_breadth_history(self, days: int = 180) -> BreadthHistory:
        """Get historical breadth for line chart"""
        breadth = self._load_market_breadth().tail(days)
        vnindex = self._load_vnindex().tail(days)

        # Merge on date
        merged = breadth.merge(
            vnindex[['date', 'close']].rename(columns={'close': 'vnindex_close'}),
            on='date',
            how='left'
        )

        return BreadthHistory(
            date=merged['date'].tolist(),
            ma20_pct=merged.get('above_ma20_pct', merged.get('pct_above_ma20', 0)).tolist(),
            ma50_pct=merged.get('above_ma50_pct', merged.get('pct_above_ma50', 0)).tolist(),
            ma100_pct=merged.get('above_ma100_pct', merged.get('pct_above_ma100', 0)).tolist(),
            vnindex_close=merged['vnindex_close'].tolist()
        )

    # ==================== SECTOR LAYER ====================

    def get_sector_ranking(self) -> pd.DataFrame:
        """Get sector ranking with IBD-style scores"""
        # TODO: Implement from phase-02-sector-layer.md
        pass

    def get_sector_rs_for_rrg(self) -> pd.DataFrame:
        """Get sector RS data for RRG chart"""
        # TODO: Implement
        pass

    # ==================== STOCK LAYER ====================

    def get_signals(self, signal_type: str = None) -> pd.DataFrame:
        """Get EMA/Breakout/VSA signals"""
        # TODO: Implement from phase-03-stock-layer.md
        pass

    def get_buy_list(self) -> pd.DataFrame:
        """Get filtered buy candidates"""
        # TODO: Implement
        pass

    def get_sell_list(self) -> pd.DataFrame:
        """Get sell recommendations"""
        # TODO: Implement
        pass

    # ==================== PRIVATE METHODS (with Caching) ====================

    @staticmethod
    @st.cache_data(ttl=300)  # 5 min cache for market data
    def _load_market_breadth() -> pd.DataFrame:
        """Load market breadth with 5-min cache"""
        path = Path("DATA/processed/technical/market_breadth/market_breadth_daily.parquet")
        return pd.read_parquet(path)

    @staticmethod
    @st.cache_data(ttl=300)  # 5 min cache
    def _load_vnindex() -> pd.DataFrame:
        """Load VN-Index indicators with 5-min cache"""
        path = Path("DATA/processed/technical/vnindex/vnindex_indicators.parquet")
        return pd.read_parquet(path)

    @staticmethod
    @st.cache_data(ttl=300)  # 5 min cache
    def _load_sector_breadth() -> pd.DataFrame:
        """Load sector breadth with 5-min cache"""
        path = Path("DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet")
        return pd.read_parquet(path)

    @staticmethod
    @st.cache_data(ttl=60)  # 1 min cache for signals (more real-time)
    def _load_signals() -> pd.DataFrame:
        """Load signal data with 1-min cache"""
        path = Path("DATA/processed/technical/alerts/daily/combined_latest.parquet")
        return pd.read_parquet(path)

    @staticmethod
    @st.cache_data(ttl=300)
    def _load_sector_list() -> list:
        """Load sector list ONCE, shared across all tabs"""
        path = Path("DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet")
        df = pd.read_parquet(path)
        return sorted(df['sector_code'].unique().tolist())

    def _get_regime(self, ema9: float, ema21: float) -> str:
        if ema9 > ema21 * 1.005:
            return 'BULLISH'
        elif ema9 < ema21 * 0.995:
            return 'BEARISH'
        return 'NEUTRAL'

    def _calculate_exposure(self, regime: str, breadth: float) -> int:
        if regime == 'BEARISH':
            return 0
        if breadth >= 70:
            return 100
        elif breadth >= 55:
            return 80
        elif breadth >= 40:
            return 60
        elif breadth >= 25:
            return 40
        return 20
```

---

## 3. File Structure

```
WEBAPP/pages/technical/
├── services/
│   ├── __init__.py
│   └── ta_dashboard_service.py
├── components/
│   ├── __init__.py
│   └── (to be created in Phase 2-4)
├── technical_dashboard.py
└── __init__.py
```

---

## 4. Implementation Checklist

- [ ] Create `WEBAPP/core/models/market_state.py`
- [ ] Create `WEBAPP/pages/technical/services/ta_dashboard_service.py`
- [ ] Implement `get_market_state()`
- [ ] Implement `get_breadth_history()`
- [ ] Test with existing parquet files
- [ ] Verify MA100 column exists in market_breadth_daily.parquet

---

## 5. Data Verification

Before implementing, check if MA100 exists:

```python
import pandas as pd
df = pd.read_parquet('DATA/processed/technical/market_breadth/market_breadth_daily.parquet')
print(df.columns.tolist())
# Should include: above_ma100_pct or pct_above_ma100
```

If not exists, need to update breadth processor first.

---

## 6. Daily Pipeline Requirements (NEW - 2025-12-25)

> **Added 2025-12-25**: Pipeline files required to update data for TA Dashboard.

### 6.1 Required Data Files

| File | Source Pipeline | TTL | Required For |
|------|-----------------|-----|--------------|
| `technical/basic_data.parquet` | daily_ta_complete.py | 5 min | All TA indicators |
| `technical/rs_rating/stock_rs_rating_daily.parquet` | daily_ta_complete.py | 5 min | RS Rating Heatmap |
| `technical/market_breadth/market_breadth_daily.parquet` | daily_ta_complete.py | 5 min | Market Overview Tab |
| `technical/vnindex/vnindex_indicators.parquet` | daily_ta_complete.py | 5 min | Regime detection |
| `technical/sector_breadth/sector_breadth_daily.parquet` | daily_ta_complete.py | 5 min | Sector Rotation Tab |
| `technical/money_flow/sector_money_flow_1d.parquet` | daily_ta_complete.py | 5 min | Money Flow Heatmap |
| `technical/alerts/daily/combined_latest.parquet` | daily_ta_complete.py | 1 min | Stock Scanner Tab |

### 6.2 Pipeline Files Created

```
PROCESSORS/
├── technical/
│   └── indicators/
│       └── rs_rating.py              # RS Rating calculator (IBD-style)
│
└── pipelines/
    ├── daily/
    │   ├── daily_ta_complete.py      # Main TA pipeline (9 steps)
    │   └── daily_rs_rating.py        # Standalone RS Rating update
    └── run_all_daily_updates.py      # Master runner (updated)
```

### 6.3 RS Rating Pipeline

```python
# RS Rating is integrated into daily_ta_complete.py as Step 9

# Pipeline steps:
# 1. VN-Index Analysis
# 2. Technical Indicators
# 3. Alerts Detection
# 4. Money Flow
# 5. Sector Money Flow
# 6. Market Breadth
# 7. Sector Breadth
# 8. Market Regime
# 9. RS Rating (NEW)

# Run command:
python3 PROCESSORS/pipelines/daily/daily_ta_complete.py

# Or standalone:
python3 PROCESSORS/pipelines/daily/daily_rs_rating.py
python3 PROCESSORS/pipelines/daily/daily_rs_rating.py --verify  # Check only
```

### 6.4 RS Rating Output Schema

```
stock_rs_rating_daily.parquet:
├── symbol (str)         # Ticker symbol
├── date (datetime)      # Trading date
├── sector_code (str)    # Sector mapping
├── rs_rating (int)      # 1-99 percentile rank
├── rs_score (float)     # Weighted return score
├── ret_3m (float)       # 3-month return %
├── ret_6m (float)       # 6-month return %
├── ret_9m (float)       # 9-month return %
└── ret_12m (float)      # 12-month return %
```

### 6.5 Update Checklist (Pipelines)

- [x] Create `PROCESSORS/technical/indicators/rs_rating.py`
- [x] Create `PROCESSORS/pipelines/daily/daily_rs_rating.py`
- [x] Update `daily_ta_complete.py` to include RS Rating (Step 9)
- [x] Update `run_all_daily_updates.py` data integrity check
- [ ] Run and verify: `python3 PROCESSORS/pipelines/daily/daily_ta_complete.py`
- [ ] Verify RS Rating output: `python3 PROCESSORS/pipelines/daily/daily_rs_rating.py --verify`
