# Trading Logic Reference

**Single Source of Truth for All Trading Parameters**

All constants defined in:
- `WEBAPP/core/trading_constants.py` - Numeric thresholds, windows, weights
- `WEBAPP/core/trading_rules.py` - Signal definitions, styling, state machines

---

## Breadth Thresholds

| Constant | Value | Rationale |
|----------|-------|-----------|
| `OVERBOUGHT_THRESHOLD` | 80% | >80% precedes corrections 73% of time (2023-2025 backtest) |
| `OVERSOLD_THRESHOLD` | 20% | <20% is extreme fear zone, potential reversal |
| `TREND_CONFIRMATION_THRESHOLD` | 50% | MA50≥50 AND MA100≥50 = confirmed uptrend |

**Usage:**
- Overbought: Don't chase, prepare to take profits on margin
- Oversold: Watch for reversal signals, potential accumulation zone
- Neutral Zone: 20-80% range where market is neither extreme

---

## Swing Detection Windows

**Source:** 3-year backtest (2023-2025, 699 trading days)

| Constant | Value | Derivation |
|----------|-------|------------|
| `MA20_HIGHER_LOW_WINDOW` | 7 days | Median cycle 14.5 days / 2 |
| `MA50_HIGHER_LOW_WINDOW` | 9 days | Median cycle 19.0 days / 2 |

**Purpose:** Detect higher lows in breadth indicators for bottom confirmation.

**Implementation:**
```python
from WEBAPP.core.trading_constants import MA20_HIGHER_LOW_WINDOW, MA50_HIGHER_LOW_WINDOW

# In ta_dashboard_service.py
def _calculate_higher_lows(df, window):
    # Find local minima within window period
    ...
```

---

## Market Score Weights

**Strategy:** 4-8 week Swing Trading

| Component | Weight | Role |
|-----------|--------|------|
| MA50 | 50% | Trend backbone (primary indicator) |
| MA20 | 30% | Timing/Trigger (entry signals) |
| MA100 | 20% | Safety filter (avoid bear markets) |

**Formula:**
```
Market Score = (MA50_breadth × 0.5) + (MA20_breadth × 0.3) + (MA100_breadth × 0.2)
```

---

## Bottom Detection Stages

| Stage | Threshold | Condition | Action |
|-------|-----------|-----------|--------|
| CAPITULATION | ALL < 25% | Extreme fear, no higher lows | Wait, don't catch falling knife |
| ACCUMULATING | ALL < 30% | MA20 showing higher low | Smart money entering, watch closely |
| EARLY_REVERSAL | MA20 ≥ 25% | Both MA20 and MA50 higher lows | Early entry opportunity |

**Flow:**
```
CAPITULATION → ACCUMULATING → EARLY_REVERSAL → RECOVERY
```

---

## Signal Matrix

9 trading signals based on market regime and breadth conditions:

| Signal | Regime | Condition | Action |
|--------|--------|-----------|--------|
| STRONG_BUY | Uptrend | MA20 < 20% | Deep pullback - deploy capital aggressively |
| BUY | Uptrend | MA20 < 40% | Normal pullback - add positions |
| HOLD | Uptrend | MA20 40-80% | Healthy trend - maintain positions |
| WARNING | Uptrend | MA20 > 80% | Overheated - reduce margin, take partial profits |
| SELL | Downtrend | MA20 > 70% | Bull trap - exit positions |
| DANGER | Downtrend | MA50 < 30%, MA20 < 20% | Capitulation - stay cash, wait for reversal |
| WAIT | Neutral | Any | Sideways - no clear signal |
| ACCUMULATING | Downtrend | All < 30%, MA20 higher low | Smart money phase - start DCA |
| EARLY_BUY | Recovery | MA20 ≥ 25%, both higher lows | Early reversal - position for recovery |

---

## Forecast Achievement Thresholds

| Category | Threshold | Meaning |
|----------|-----------|---------|
| BEAT | > 85% | 9M actual > 85% of FY forecast - Beating expectations |
| MEET | 65-85% | On track to meet FY forecast |
| MISS | < 65% | At risk of missing FY forecast |

**Usage:**
```python
from WEBAPP.core.trading_constants import BEAT_THRESHOLD, MEET_THRESHOLD

def classify_achievement(ach_pct):
    if ach_pct > BEAT_THRESHOLD:  # > 0.85
        return 'beat'
    elif ach_pct >= MEET_THRESHOLD:  # >= 0.65
        return 'meet'
    else:
        return 'miss'
```

---

## Rating Colors

| Rating | Text Color | Background |
|--------|------------|------------|
| STRONG BUY | #00C9AD (teal) | rgba(0, 201, 173, 0.15) |
| BUY | #009B87 (dark teal) | rgba(0, 155, 135, 0.15) |
| HOLD | #FFC132 (gold) | rgba(255, 193, 50, 0.15) |
| SELL | #E63946 (red) | rgba(230, 57, 70, 0.15) |
| STRONG SELL | #C62828 (dark red) | rgba(198, 40, 40, 0.15) |
| N/A | #64748B (gray) | rgba(100, 116, 139, 0.15) |

---

## RRG Quadrant Colors

| Quadrant | Color | Description |
|----------|-------|-------------|
| LEADING | #10B981 (green) | Strong momentum, strong trend |
| WEAKENING | #F59E0B (amber) | Strong momentum fading, trend still up |
| LAGGING | #EF4444 (red) | Weak momentum, weak trend |
| IMPROVING | #06B6D4 (cyan) | Momentum recovering, trend improving |

---

## Stock Watchlists

| Watchlist | Count | Sectors |
|-----------|-------|---------|
| BSC Universe | 44 | Multi-sector portfolio |
| VN30 | 30 | Index components |
| Banking | 15 | All commercial banks |
| Securities | 10 | Brokerage firms |
| Real Estate | 10 | Property developers |
| Technology | 4 | Tech companies |

---

## Pattern Interpretations

66 candlestick patterns with interpretations:

| Pattern | Signal | Volume Context |
|---------|--------|----------------|
| DOJI | Neutral/Reversal | - |
| HAMMER | Bullish reversal | High volume = confirmation |
| SHOOTING_STAR | Bearish reversal | High volume = confirmation |
| ENGULFING_BULL | Strong bullish | Volume surge = strong signal |
| ENGULFING_BEAR | Strong bearish | Volume surge = strong signal |
| THREE_WHITE_SOLDIERS | Very bullish | - |
| THREE_BLACK_CROWS | Very bearish | - |
| MORNING_STAR | Bullish reversal | - |
| EVENING_STAR | Bearish reversal | - |

*Full pattern list in `WEBAPP/core/trading_rules.py` → `PATTERN_INTERPRETATIONS`*

---

## Stock Scanner Signal Logic

**Location:** `WEBAPP/pages/technical/services/ta_dashboard_service.py`

### Signal Priority System

When multiple signals occur on the same day for a ticker, priority determines which is primary:

| Priority | Category | Patterns | Rationale |
|----------|----------|----------|-----------|
| 1 | Breakout | Volume Breakout, Price Breakout | Highest conviction, confirms trend |
| 2 | Strong Reversal | morning_star, evening_star, engulfing, three_white_soldiers, three_black_crows | Multi-candle patterns, more reliable |
| 3 | Single Candle Reversal | hammer, inverted_hammer, shooting_star, hanging_man | Single candle, needs confirmation |
| 4 | MA Crossover | MA20/50/100/200 Cross ↑/↓ | Trend following, lagging indicator |
| 5 | Indecision | doji, spinning_top | Least actionable, context-dependent |

### Context-Aware DOJI

DOJI signal direction depends on prior trend:

| Prior Trend | DOJI Signal | Interpretation |
|-------------|-------------|----------------|
| UPTREND / STRONG_UP | BEARISH | Reversal warning at top |
| DOWNTREND / STRONG_DOWN | BULLISH | Hope for reversal at bottom |
| SIDEWAYS | NEUTRAL | Indecision continues |

**Implementation:**
```python
def refine_doji_signal(row):
    if row.get('pattern_name') != 'doji':
        return row['signal']
    trend = row.get('trend', 'SIDEWAYS')
    if trend in ['STRONG_UP', 'UPTREND']:
        return 'BEARISH'
    elif trend in ['STRONG_DOWN', 'DOWNTREND']:
        return 'BULLISH'
    return 'NEUTRAL'
```

### Signal Strength Scoring

| Signal Type | Base Strength | Bonuses | Max |
|-------------|---------------|---------|-----|
| Breakout | 70 | +15 volume_confirmed, +15 if vol_ratio>1.5 | 100 |
| Strong Reversal | 80-100 | - | 100 |
| Single Candle | 28-36 | - | 36 |
| MA Crossover | Period-based | MA20=50, MA50=75, MA100=85, MA200=100 | 100 |
| DOJI | 23 | - | 23 |

### Primary/Secondary Signal Display

Each ticker+date combination shows ONE primary signal with optional secondary indicator:

**Backend Output:**
- `is_primary`: Boolean flag for display filtering
- `secondary_signals`: List of other signal names for that day

**UI Display:**
```
hanging_man +1    ← Primary signal + tooltip showing "doji"
engulfing +2      ← Primary signal + tooltip showing "MA20 Cross ↑, MA200 Cross ↑"
```

**Example - DXG 2025-12-22:**
```
Primary: hanging_man (SELL, strength=100)
Secondary: ['MA200 Cross ↑', 'doji']
Display: "hanging_man +2" with tooltip
```

---

## Backtest Methodology

**Period:** 2023-01-01 to 2025-12-31 (3 years, ~699 trading days)
**Universe:** VN30 + BSC Coverage (92 stocks)
**Strategy:** Swing Trading (4-8 week holding period)

**Key Findings:**
1. Breadth > 80% preceded corrections in 73% of cases
2. MA20 median cycle: 14.5 days → 7-day window for higher low detection
3. MA50 median cycle: 19.0 days → 9-day window for higher low detection
4. Bottom reversal success rate with higher low confirmation: 81%

---

## File Locations

```
WEBAPP/core/
├── trading_constants.py    # Numbers: thresholds, windows, weights
└── trading_rules.py        # Rules: signals, colors, patterns
```

**Import Examples:**
```python
# Constants
from WEBAPP.core.trading_constants import (
    OVERBOUGHT_THRESHOLD, OVERSOLD_THRESHOLD,
    MA20_HIGHER_LOW_WINDOW, MA50_HIGHER_LOW_WINDOW,
    MARKET_SCORE_WEIGHTS, BSC_UNIVERSE, WATCHLISTS,
    BEAT_THRESHOLD, MEET_THRESHOLD
)

# Rules
from WEBAPP.core.trading_rules import (
    SIGNAL_MATRIX, BOTTOM_STAGES, REGIME_STYLES,
    RATING_COLORS, QUADRANT_COLORS, PATTERN_INTERPRETATIONS
)
```

---

## Change Log

| Date | Change | Rationale |
|------|--------|-----------|
| 2026-01-02 | Initial centralization | Single source of truth |
| 2026-01-02 | Higher low windows (7d/9d) | 3-year backtest optimization |
| 2026-01-02 | Signal Priority System | Multiple signals per day → select most important |
| 2026-01-02 | Context-aware DOJI | DOJI signal based on prior trend |
| 2026-01-02 | MA Strength Scaling | MA20=50, MA50=75, MA100=85, MA200=100 |
| 2026-01-02 | Primary/Secondary Display | +X tooltip for multiple signals |
