# Technical Analysis Dashboard - Logic & Formulas

**Date:** 2025-12-30
**Purpose:** Complete reference for TA dashboard components, formulas, decision trees, and implementation details
**Location:** `WEBAPP/pages/technical/` (components, services, models)

---

## Table of Contents

1. [Component Overview](#component-overview)
2. [Market Health Scoring](#market-health-scoring)
3. [Signal Matrix & Decision Tree](#signal-matrix--decision-tree)
4. [Bottom Detection System](#bottom-detection-system)
5. [Breadth Analysis](#breadth-analysis)
6. [Regime Detection](#regime-detection)
7. [Capital Allocation](#capital-allocation)
8. [Higher Lows Detection](#higher-lows-detection)
9. [Sector Rotation (RRG)](#sector-rotation-rrg)
10. [Stock Scanner Signals](#stock-scanner-signals)
11. [Color Schemes & Design](#color-schemes--design)
12. [Data Models](#data-models)

---

## Component Overview

### Architecture (File Locations)

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| **Market Overview** | `components/market_overview.py` | 813 | VN-Index, regime, breadth zones, signal matrix |
| **Sector Rotation** | `components/sector_rotation.py` | 715 | RRG quadrants, sector ranking, money flow |
| **Stock Scanner** | `components/stock_scanner.py` | 831 | Candlestick patterns, MA crossovers, volume, breakouts |
| **Filter Bar** | `components/ta_filter_bar.py` | 254 | Timeframe, sector, signal type selectors |
| **TA Service** | `services/ta_dashboard_service.py` | 520 | Data loading, calculations, caching |
| **Market State** | `core/models/market_state.py` | 69 | Data model with all market metrics |

---

## Market Health Scoring

### Formula

```
Market Score = (MA50_breadth × 0.5) + (MA20_breadth × 0.3) + (MA100_breadth × 0.2)
```

**Components:**
- **MA50 breadth (50% weight):** Percentage of stocks trading above 50-day MA
  - Represents medium-term trend backbone
  - Highest weight = most important
- **MA20 breadth (30% weight):** Percentage of stocks trading above 20-day MA
  - Represents short-term timing/trigger
  - 30% weight = secondary importance
- **MA100 breadth (20% weight):** Percentage of stocks trading above 100-day MA
  - Represents long-term safety filter
  - 20% weight = least important but critical for filter

### Score Interpretation

```
Range    Color     Interpretation           Action
────────────────────────────────────────────────────
≥ 60     Green     Healthy market          Aggressive deployment
40-59    Amber     Caution zone            Conservative approach
< 40     Red       Bearish conditions      Defensive/wait mode
```

### Example Calculation

```
Day 1:
- MA50 breadth: 55% → 55 × 0.5 = 27.5
- MA20 breadth: 42% → 42 × 0.3 = 12.6
- MA100 breadth: 38% → 38 × 0.2 = 7.6
- Market Score = 27.5 + 12.6 + 7.6 = 47.7 → AMBER (caution)
```

---

## Signal Matrix & Decision Tree

### Complete Signal Matrix (9 Signals)

| Signal | Color | Condition | Action | Priority |
|--------|-------|-----------|--------|----------|
| **STRONG_BUY** | #059669 | Extreme oversold in uptrend | Deploy capital aggressively | HIGHEST |
| **BUY** | #10B981 | Normal pullback in uptrend | Scale in / new position | HIGH |
| **HOLD** | #3B82F6 | Healthy uptrend continuing | Maintain position | MEDIUM |
| **WARNING** | #F59E0B | Overbought conditions | Don't chase, take profits | MEDIUM |
| **SELL** | #DC2626 | Bull trap in downtrend | Reduce exposure | HIGH |
| **DANGER** | #7F1D1D | Market crash/panic | Stay in cash absolutely | CRITICAL |
| **WAIT** | #64748B | Sideways/no clear trend | Observe, no entry | LOW |
| **ACCUMULATING** | #6366F1 | Smart money entering | Watch closely, prepare capital | HIGH |
| **EARLY_BUY** | #22D3EE | Early reversal confirmed | Test buy 10-20%, tight stop | HIGH |

### Decision Tree Logic

#### Uptrend Scenario (MA50 ≥ 50 AND MA100 ≥ 50)

```
IF (MA50 breadth ≥ 50 AND MA100 breadth ≥ 50):  # CONFIRMED UPTREND
    │
    ├─ IF (MA20 < 20):
    │   → STRONG_BUY
    │   Rationale: Extreme pullback, best risk/reward in uptrend
    │
    ├─ ELIF (20 ≤ MA20 < 40):
    │   → BUY
    │   Rationale: Normal pullback, healthy entry opportunity
    │
    ├─ ELIF (40 ≤ MA20 ≤ 80):
    │   → HOLD
    │   Rationale: Ride the trend, don't add to position
    │
    └─ ELIF (MA20 > 80):
        → WARNING
        Rationale: Overbought, take profits on strength
```

**Examples:**

1. VN-Index at new high, MA50=65%, MA20=85%, MA100=72%
   - Uptrend confirmed (MA50≥50, MA100≥50)
   - MA20=85% > 80% → **WARNING**
   - Action: Don't buy, wait for pullback

2. Market pullback, MA50=52%, MA20=18%, MA100=55%
   - Uptrend confirmed
   - MA20=18% < 20% → **STRONG_BUY**
   - Action: Deploy capital aggressively

#### Downtrend/Sideways Scenario (NOT in uptrend)

```
IF NOT (MA50 ≥ 50 AND MA100 ≥ 50):  # DOWNTREND or SIDEWAYS
    │
    ├─ IF (MA20 > 70):
    │   → SELL
    │   Rationale: Elevated but no uptrend, distribute holdings
    │
    ├─ ELIF (MA50 < 30 AND MA20 < 20 AND NO MA20 higher low):
    │   → DANGER
    │   Rationale: Extreme crash with no reversal signs yet
    │
    ├─ ELIF (bottom_stage == 'EARLY_REVERSAL'):
    │   → EARLY_BUY
    │   Rationale: Reversal confirmed, can resume uptrend
    │
    ├─ ELIF (bottom_stage == 'ACCUMULATING'):
    │   → ACCUMULATING
    │   Rationale: Smart money entering, potential bottom forming
    │
    └─ ELSE:
        → WAIT
        Rationale: No clear setup, observe market action
```

**Examples:**

1. Crash scenario: MA50=25%, MA20=15%, MA100=20%, no higher low
   - Not in uptrend
   - MA50<30, MA20<20, no higher low → **DANGER**
   - Action: Stay in cash

2. Accumulation phase: MA50=28%, MA20=22%, higher low just formed
   - Not in uptrend
   - All MA < 30%, MA20 has higher low → **ACCUMULATING**
   - Action: Watch closely, smart money accumulating

3. Early recovery: MA20=26%, both MA20/MA50 higher lows confirmed
   - Not in uptrend yet
   - bottom_stage='EARLY_REVERSAL' → **EARLY_BUY**
   - Action: Test buy 10-20%

---

## Bottom Detection System

### 3-Stage Bottom Formation

The system detects bottoms only when **NOT in uptrend** (MA50 < 50 or MA100 < 50).

### Stage 1: CAPITULATION

```
Trigger Condition:
  - ALL MA < 25% (extreme oversold)
  - AND NO MA20 higher low yet formed (still making lower lows)

Interpretation:
  - Maximum fear, panic selling
  - No institutional buyers yet
  - Wait for MA20 to form higher low before considering entry

Signal:
  - Label: "CAPITULATION"
  - Subtitle: "Hoảng loạn bán tháo" (Panic selling)
  - Color: #7F1D1D (dark red)
  - Action: "Đứng ngoài. Chờ tín hiệu dừng lỗ." (Stay out. Await bottom signal)

Example:
  Day 1: MA20=18%, MA50=22%, MA100=24%, recent low < previous low
  → CAPITULATION (all < 25%, no higher low yet)
```

### Stage 2: ACCUMULATING

```
Trigger Condition:
  - ALL MA < 30% (still oversold)
  - AND MA20 creates higher low (last 3 days low > previous 3 days low)
  - AND MA20 is rising from that low (current > recent low)

Higher Low Detection (3-day window):
  - Recent 3 days: Days 8, 9, 10 (last 3)
  - Previous 3 days: Days 5, 6, 7 (3-6 days ago)
  - Condition: min(days 8-10) > min(days 5-7)

Interpretation:
  - Institutional/smart money entering
  - Selling pressure diminishing
  - Potential bottom forming

Signal:
  - Label: "ACCUMULATING"
  - Subtitle: "Smart money đang vào" (Smart money entering)
  - Color: #6366F1 (indigo)
  - Action: "Theo dõi sát. Chuẩn bị vốn. Smart money tích lũy." (Watch closely. Prepare capital)

Example:
  Days 5-7: MA20 lows = 20%, 19%, 21% → min = 19%
  Days 8-10: MA20 lows = 22%, 23%, 24% → min = 22% (higher!)
  Current MA20 = 26% (rising from 22% low)
  All MA < 30%
  → ACCUMULATING (higher low + rising + all < 30%)
```

### Stage 3: EARLY_REVERSAL

```
Trigger Condition:
  - MA20 ≥ 25% (escaped oversold)
  - AND MA20 has higher low confirmed
  - AND MA50 creates higher low (5-day window)
  - AND MA50 is rising from that low

Higher Low Detection (5-day window):
  - MA20: Recent 3 days vs Previous 3 days
  - MA50: Recent 5 days vs Previous 5 days
  - Condition: min(recent) > min(previous) AND current > recent_low

Interpretation:
  - Both short and medium-term MAs reversing up
  - Uptrend likely to resume
  - Breadth expansion probable
  - Safe to increase exposure

Signal:
  - Label: "EARLY_REVERSAL"
  - Subtitle: "Đảo chiều sớm" (Early reversal)
  - Color: #22D3EE (cyan)
  - Action: "Test mua 10-20%. Stop-loss chặt dưới đáy." (Test buy 10-20%. Tight stop below low)

Example:
  MA20: Recent 3d low = 28%, Previous 3d low = 25% (higher!)
  MA50: Recent 5d low = 32%, Previous 5d low = 28% (higher!)
  Current MA50 = 35% (rising)
  → EARLY_REVERSAL (both have higher lows + rising)
```

---

## Breadth Analysis

### What is Breadth?

**Definition:** Percentage of stocks trading above a moving average

```
% > MA20 = (Number of stocks with Close > MA20) / Total stocks × 100
% > MA50 = (Number of stocks with Close > MA50) / Total stocks × 100
% > MA100 = (Number of stocks with Close > MA100) / Total stocks × 100
```

### Breadth Zones

| Zone | Range | Meaning | Market State |
|------|-------|---------|--------------|
| **Extreme Overbought** | 90-100% | Too extended | Risk of pullback |
| **Overbought** | 80-90% | Strong rally | Caution zone |
| **Neutral High** | 60-80% | Healthy strength | Good market |
| **Neutral** | 40-60% | Balanced | No clear bias |
| **Neutral Low** | 20-40% | Weakness | Caution zone |
| **Oversold** | 10-20% | Strong pullback | Opportunity |
| **Extreme Oversold** | 0-10% | Panic selling | Critical buying opportunity |

### Uptrend Confirmation

```
Uptrend requires BOTH conditions:
  - MA50 breadth ≥ 50%  (medium-term trend positive)
  - MA100 breadth ≥ 50% (long-term trend positive)

If either is < 50%, market is in downtrend or sideways
```

---

## Regime Detection

### Regime Definition

Market regime determined by comparing fast EMA vs slow EMA.

```python
EMA9 = 9-day Exponential Moving Average (responsive to recent price action)
EMA21 = 21-day Exponential Moving Average (represents trend)
Margin = 0.5% buffer to avoid false signals
```

### Regime Logic

```
IF (EMA9 > EMA21 × 1.005):
    → BULLISH ✅
    Interpretation: Short-term above long-term by >0.5%, uptrend confirmed

ELIF (EMA9 < EMA21 × 0.995):
    → BEARISH ❌
    Interpretation: Short-term below long-term by >0.5%, downtrend confirmed

ELSE (within 0.5% margin):
    → NEUTRAL ⚠️
    Interpretation: Choppy/transitional period, no clear direction
```

### Example Calculations

1. **Bullish Regime:**
   - EMA9 = 1,325.50, EMA21 = 1,320.00
   - EMA21 × 1.005 = 1,326.60
   - EMA9 (1,325.50) < 1,326.60 → Not quite bullish yet
   - Margin prevents false signals

2. **Strong Bullish:**
   - EMA9 = 1,330.00, EMA21 = 1,320.00
   - EMA21 × 1.005 = 1,326.60
   - EMA9 (1,330.00) > 1,326.60 → **BULLISH** ✅

---

## Capital Allocation

### Exposure Level Formula

```python
def calculate_exposure(regime: str, breadth: float) -> int:
    """
    Returns: 0, 20, 40, 60, 80, or 100 (percentage of capital)
    """

    # Regime check: BEARISH = stay in cash
    if regime == 'BEARISH':
        return 0  # 0% deployment

    # Breadth-based allocation
    if breadth ≥ 70:
        return 100  # 100% - Full deployment
    elif breadth ≥ 55:
        return 80   # 80% - Heavy deployment
    elif breadth ≥ 40:
        return 60   # 60% - Moderate deployment
    elif breadth ≥ 25:
        return 40   # 40% - Conservative deployment
    else:
        return 20   # 20% - Minimal exposure (heavy pullback)
```

### Exposure Levels Explained

| Level | Condition | Market State | Action |
|-------|-----------|--------------|--------|
| **100%** | Breadth ≥ 70% + Bullish | Strong rally | Deploy all capital |
| **80%** | Breadth 55-70% + Bullish | Heavy momentum | Aggressive position |
| **60%** | Breadth 40-55% + Bullish | Moderate strength | Normal position |
| **40%** | Breadth 25-40% + Bullish | Weak uptrend | Partial position |
| **20%** | Breadth < 25% + Bullish | Heavy pullback | Minimal exposure |
| **0%** | Any breadth + Bearish | Downtrend | Stay in cash |

### Color Coding

```
Exposure ≥ 80%  → Green (#10B981)      - Aggressive
Exposure ≥ 60%  → Light Green (#22C55E) - Normal
Exposure ≥ 40%  → Amber (#F59E0B)      - Caution
Exposure ≥ 20%  → Orange (#FF9F43)     - Conservative
Exposure < 20%  → Red (#EF4444)        - Defensive
```

---

## Higher Lows Detection

### Concept

**Higher Lows** = Confirmation that downtrend is reversing

- Recent low > Previous low = Buyers stopped selling pressure
- Current > Recent low = Moving up from the low
- Used in bottom detection as key confirmation signal

### MA20 Higher Lows (3-Day Window)

```python
# Get last 10 days of MA20 breadth data
last_10_days = breadth_df.tail(10)  # Days 1-10

# Recent 3 days (days 8, 9, 10 = last 3)
ma20_recent_window = last_10_days[-3:]
ma20_recent_low = min(ma20_recent_window)

# Previous 3 days (days 5, 6, 7)
ma20_prev_window = last_10_days[-6:-3]
ma20_prev_low = min(ma20_prev_window)

# Current value (day 10)
ma20_current = last_10_days.iloc[-1]

# Detection
ma20_higher_low = ma20_recent_low > ma20_prev_low
ma20_rising_from_low = ma20_current > ma20_recent_low
```

**Returned Values:**

```python
{
    'ma20_higher_low': bool,        # True if recent low > previous low
    'ma20_recent_low': float,       # Lowest value in last 3 days
    'ma20_prev_low': float,         # Lowest value in previous 3 days
    'ma20_rising_from_low': bool,   # Current > recent low
}
```

**Example:**

```
Day 5: MA20 = 22%
Day 6: MA20 = 20% ← Previous low
Day 7: MA20 = 21%
Day 8: MA20 = 23%
Day 9: MA20 = 24% ← Recent low
Day 10: MA20 = 25% (current)

Previous low (days 5-7) = 20%
Recent low (days 8-10) = 23%
23% > 20% → ma20_higher_low = TRUE ✅
Current 25% > recent 23% → ma20_rising_from_low = TRUE ✅
```

### MA50 Higher Lows (5-Day Window)

```python
# Recent 5 days (days 6, 7, 8, 9, 10 = last 5)
ma50_recent_window = last_10_days[-5:]
ma50_recent_low = min(ma50_recent_window)

# Previous 5 days (days 1, 2, 3, 4, 5)
ma50_prev_window = last_10_days[:-5]
ma50_prev_low = min(ma50_prev_window)

# Current value (day 10)
ma50_current = last_10_days.iloc[-1]

# Detection
ma50_higher_low = ma50_recent_low > ma50_prev_low
ma50_rising_from_low = ma50_current > ma50_recent_low
```

**Usage in Bottom Detection:**

- **ACCUMULATING stage:** Requires MA20 higher low
- **EARLY_REVERSAL stage:** Requires BOTH MA20 AND MA50 higher lows

---

## Sector Rotation (RRG)

### Relative Rotation Graph (RRG) Concept

**Purpose:** Identify which sectors are leading (strong + improving) vs lagging (weak + declining)

**Dimensions:**
- **X-axis:** RS Ratio (relative strength vs market average)
- **Y-axis:** RS Momentum (rate of change in relative strength)

### Calculation Logic

```python
# 1. Calculate sector strength score
sector_strength = (ema12 - ema26) / ema26 * 100  # MACD-style momentum

# 2. Calculate market average strength
market_avg_strength = sector_strength.mean()

# 3. Calculate RS Ratio (relative strength)
sector_df['rs_ratio'] = sector_strength / market_avg_strength

# 4. Calculate RS Momentum (5-day rate of change)
sector_df['rs_momentum'] = sector_df['rs_ratio'].diff(5) * 100

# 5. Apply smoothing (SMA3)
sector_df['rs_ratio_smooth'] = sector_df['rs_ratio'].rolling(3, min_periods=1).mean()
sector_df['rs_momentum_smooth'] = sector_df['rs_momentum'].rolling(3, min_periods=1).mean()
```

### Quadrant Determination

```python
def determine_quadrant(rs_ratio: float, rs_momentum: float) -> str:
    """
    Quadrant logic based on RS Ratio and RS Momentum
    """

    if rs_ratio > 1.0 and rs_momentum > 0:
        return 'LEADING'      # Top-right: Strong + Improving (BUY)
    elif rs_ratio > 1.0 and rs_momentum <= 0:
        return 'WEAKENING'    # Bottom-right: Strong but Declining (WATCH)
    elif rs_ratio <= 1.0 and rs_momentum <= 0:
        return 'LAGGING'      # Bottom-left: Weak + Declining (SELL)
    else:  # rs_ratio <= 1.0 and rs_momentum > 0
        return 'IMPROVING'    # Top-left: Weak but Improving (ACCUMULATE)
```

### Quadrant Colors & Interpretation

```
┌─────────────────────────────────┐
│  IMPROVING    │    LEADING      │
│  (Watch)      │    (Buy)        │  RS Momentum > 0 (Improving)
│  Cyan #06B6D4 │   Green #10B981 │
├─────────────────────────────────┤
│  LAGGING      │   WEAKENING     │
│  (Sell)       │   (Watch)       │  RS Momentum ≤ 0 (Declining)
│  Red #EF4444  │   Amber #F59E0B │
└─────────────────────────────────┘
    RS Ratio ≤ 1.0    RS Ratio > 1.0
    (Weak)             (Strong)

Trading Implications:
- LEADING: Best performers, momentum + strength → BUY
- IMPROVING: Turnarounds, potential upside → WATCH FOR ENTRY
- WEAKENING: Caution, strength fading → REDUCE/EXIT
- LAGGING: Worst performers → AVOID or SHORT
```

### Example RRG Analysis

```
Banking Sector:
- RS Ratio = 1.15 (strong vs market)
- RS Momentum = 0.08 (improving)
- Quadrant: LEADING ✅
- Action: Buy banking stocks, momentum strongest

Real Estate Sector:
- RS Ratio = 0.92 (weak vs market)
- RS Momentum = 0.05 (improving)
- Quadrant: IMPROVING ⚠️
- Action: Watch for entry, potential turnaround

Energy Sector:
- RS Ratio = 1.10 (strong vs market)
- RS Momentum = -0.12 (declining)
- Quadrant: WEAKENING ⚠️
- Action: Caution, strength is fading

Tech Sector:
- RS Ratio = 0.88 (weak vs market)
- RS Momentum = -0.08 (declining)
- Quadrant: LAGGING ❌
- Action: Avoid or exit positions
```

---

## Stock Scanner Signals

### Signal Types & Sources

#### 1. Candlestick Patterns (HIGHEST PRIORITY)

```
Source: DATA/processed/technical/alerts/daily/patterns_latest.parquet

Columns:
  - symbol: Stock ticker
  - date: Signal date
  - pattern_name: Pattern name (e.g., "Engulfing", "Hammer")
  - signal: "BULLISH" or "BEARISH"
  - price: Pattern price level
  - strength: 0-1 (confidence score)

Mapping:
  - BULLISH patterns → Buy signals
  - BEARISH patterns → Sell signals
```

**Bullish Patterns (11 types):**

| Pattern | Vietnamese | Signal | Interpretation |
|---------|-----------|--------|-----------------|
| Engulfing | Đảo chiều mạnh | BUY | Green candle completely engulfs red |
| Hammer | Từ chối giảm giá | BUY | Lower wick ≥ 2× body, buyers reject lows |
| Morning Star | Mô hình 3 nến | BUY | (1) Red, (2) Doji, (3) Green = reversal |
| Piercing | Xuyên thấu | BUY | Green opens below, closes >50% into red |
| Three White Soldiers | 3 nến xanh liên tiếp | BUY | Bullish reversal at bottom |
| Inverted Hammer | Bấc trên dài | BUY | Upper wick long, small body. Needs confirmation |
| Harami Bullish | Nến xanh nhỏ trong nến đỏ | BUY | Small green inside red = momentum weakening |
| Doji | Thị trường bất định | BUY | Open = Close = indecision |
| Dragonfly Doji | Từ chối giảm giá mạnh | BUY | Long lower wick, Open = High = Close |
| Marubozu White | Nến không bấc (xanh) | BUY | No wicks, buyers control 100% of session |
| Tweezer Bottom | Đáy nhíp | BUY | 2 candles with same low = strong support |

**Bearish Patterns (10 types):**

| Pattern | Vietnamese | Signal | Interpretation |
|---------|-----------|--------|-----------------|
| Bearish Engulfing | Đảo chiều giảm mạnh | SELL | Red completely engulfs green |
| Hanging Man | Cảnh báo đảo chiều | SELL | Like hammer but at top of uptrend |
| Evening Star | Mô hình 3 nến | SELL | (1) Green, (2) Doji, (3) Red |
| Shooting Star | Từ chối tăng giá | SELL | Long upper wick, small body at bottom |
| Dark Cloud Cover | Mây đen che phủ | SELL | Red opens above, closes <50% into green |
| Three Black Crows | 3 nến đỏ liên tiếp | SELL | Bearish reversal at top |
| Harami Bearish | Nến đỏ nhỏ trong nến xanh | SELL | Small red inside green = momentum fade |
| Gravestone Doji | Từ chối tăng giá mạnh | SELL | Long upper wick, Open = Low = Close |
| Marubozu Black | Nến không bấc (đỏ) | SELL | No wicks, sellers control 100% |
| Tweezer Top | Đỉnh nhíp | SELL | 2 candles with same high = resistance |

#### 2. MA Crossover Signals

```
Source: DATA/processed/technical/alerts/daily/ma_crossover_latest.parquet

Types:
  - MA_CROSS_ABOVE: Golden Cross (bullish), short MA crosses above long MA
  - MA_CROSS_BELOW: Death Cross (bearish), short MA crosses below long MA

Strength: 0.7 (default confidence)

Example:
  - MA20 crosses above MA50 → Golden Cross (BUY)
  - MA50 crosses below MA200 → Death Cross (SELL)
```

#### 3. Volume Spike Signals

```
Source: DATA/processed/technical/alerts/daily/volume_spike_latest.parquet

Columns:
  - symbol: Stock ticker
  - date: Signal date
  - signal: "BULLISH", "BEARISH", or "NOISE"
  - volume_ratio: Volume multiplier (e.g., 2.5x average)
  - confidence: Strength 0-1

Interpretation:
  - BULLISH + HIGH Vol: Strong conviction buying
  - BEARISH + HIGH Vol: Strong conviction selling
  - NOISE: High volume but no clear direction
```

#### 4. Breakout Signals

```
Source: DATA/processed/technical/alerts/daily/breakout_latest.parquet

Types:
  - BREAKOUT_UP: Price breaks above resistance (bullish)
  - BREAKDOWN: Price breaks below support (bearish)

Strength: 0.8 (default confidence)

Example:
  - Stock breaks above 52-week high → BREAKOUT_UP (BUY)
  - Stock breaks below support level → BREAKDOWN (SELL)
```

### Volume Context Interpretation

Volume context adds conviction level to patterns:

```
HIGH Volume (2x+)   → Strong conviction, high probability signal
AVERAGE Volume     → Normal confirmation needed
LOW Volume         → Weak signal, awaiting confirmation

Pattern Analysis Matrix:

Pattern + Volume Context → Interpretation

Engulfing + HIGH Vol   → "Đảo chiều cực mạnh. Buyers áp đảo." (Very strong reversal)
Engulfing + AVG Vol    → "Đảo chiều. Cần theo dõi phiên sau." (Reversal, watch next session)
Engulfing + LOW Vol    → "Tín hiệu yếu. Chờ volume confirmation." (Weak, await confirmation)

Hammer + HIGH Vol      → "Từ chối mạnh. Đáy có thể hình thành." (Strong reversal, bottom forming)
Hammer + AVG Vol       → "Từ chối giảm giá. Cần xác nhận." (Rejection, needs confirmation)
Hammer + LOW Vol       → "Từ chối yếu. Chưa an toàn vào." (Weak rejection, unsafe entry)
```

### Chart Patterns (Technical)

```
Double Bottom:       Classic reversal. Breakout above neckline = confirm
Double Top:         Classic reversal. Breakdown below neckline = confirm
Head & Shoulders:   Bearish reversal. Breakdown neckline = confirm
Cup & Handle:       Bullish continuation. Breakout rim = resume uptrend
Flag (Bull):        Continuation after rally. Breakout = more upside
Flag (Bear):        Continuation after decline. Breakdown = more downside
```

---

## Color Schemes & Design

### Regime Styles (Market Overview)

```python
REGIME_STYLES = {
    'BULLISH': {
        'color': '#10B981',
        'bg': 'rgba(16, 185, 129, 0.15)',
        'border': '#10B981'
    },
    'BEARISH': {
        'color': '#EF4444',
        'bg': 'rgba(239, 68, 68, 0.15)',
        'border': '#EF4444'
    },
    'NEUTRAL': {
        'color': '#F59E0B',
        'bg': 'rgba(245, 158, 11, 0.15)',
        'border': '#F59E0B'
    }
}
```

### Signal Styles (Market Overview)

```python
SIGNAL_STYLES = {
    'RISK_ON': {
        'color': '#10B981',
        'bg': 'rgba(16, 185, 129, 0.15)'
    },
    'RISK_OFF': {
        'color': '#EF4444',
        'bg': 'rgba(239, 68, 68, 0.15)'
    },
    'CAUTION': {
        'color': '#F59E0B',
        'bg': 'rgba(245, 158, 11, 0.15)'
    }
}
```

### Breadth Colors (Chart Lines)

```python
BREADTH_COLORS = {
    'ma20': '#8B5CF6',    # Purple - Fast moving, short-term
    'ma50': '#06B6D4',    # Cyan - Medium-term
    'ma100': '#F59E0B'    # Amber - Slow moving, long-term
}
```

### RRG Quadrant Colors (Sector Rotation)

```python
QUADRANT_COLORS = {
    'LEADING': '#10B981',      # Emerald Green - Strong + Improving
    'IMPROVING': '#06B6D4',    # Cyan - Weak but Improving
    'WEAKENING': '#F59E0B',    # Amber - Strong but Declining
    'LAGGING': '#EF4444'       # Red - Weak + Declining
}
```

---

## Data Models

### MarketState Dataclass

```python
@dataclass
class MarketState:
    """Complete market state snapshot for TA dashboard"""

    # Date & VN-Index
    date: datetime                   # Current date
    vnindex_close: float             # VN-Index closing price
    vnindex_change_pct: float        # Daily % change

    # Regime Detection (EMA9 vs EMA21)
    regime: str                      # 'BULLISH' | 'BEARISH' | 'NEUTRAL'
    ema9: float                      # 9-day EMA
    ema21: float                     # 21-day EMA

    # Breadth Metrics
    breadth_ma20_pct: float          # % stocks > MA20 (0-100)
    breadth_ma50_pct: float          # % stocks > MA50 (0-100)
    breadth_ma100_pct: float         # % stocks > MA100 (0-100)
    ad_ratio: float                  # Advance/Decline ratio

    # Capital Allocation
    exposure_level: int              # 0, 20, 40, 60, 80, or 100 (%)

    # Divergence (Not yet implemented)
    divergence_type: str             # 'BULLISH' | 'BEARISH' | None
    divergence_strength: int         # 0-3 (strength level)

    # Overall Signal
    signal: str                      # 'RISK_ON' | 'RISK_OFF' | 'CAUTION'

    # Previous Day Breadth (for comparison)
    prev_breadth_ma20_pct: float     # Previous day MA20%
    prev_breadth_ma50_pct: float     # Previous day MA50%

    # Higher Lows Detection (MA20)
    ma20_higher_low: bool            # Recent 3d low > Previous 3d low
    ma20_recent_low: float           # Min of last 3 days
    ma20_prev_low: float             # Min of previous 3 days
    ma20_rising_from_low: bool       # Current > recent low

    # Higher Lows Detection (MA50)
    ma50_higher_low: bool            # Recent 5d low > Previous 5d low
    ma50_recent_low: float           # Min of last 5 days
    ma50_prev_low: float             # Min of previous 5 days
    ma50_rising_from_low: bool       # Current > recent low

    # Bottom Detection Stage
    bottom_stage: str                # 'CAPITULATION' | 'ACCUMULATING' | 'EARLY_REVERSAL' | None
```

### Service Methods (ta_dashboard_service.py)

| Method | Returns | Purpose |
|--------|---------|---------|
| `get_market_state()` | `MarketState` | Current market snapshot with all metrics |
| `get_breadth_history(days)` | `DataFrame` | Historical breadth + VN-Index for charts |
| `get_sector_ranking()` | `DataFrame` | Sectors sorted by strength/ranking |
| `get_sector_money_flow(timeframe)` | `DataFrame` | Money flow by sector (1D/1W/1M) |
| `get_sector_rs_for_rrg(smooth, trail)` | `DataFrame` | RS Ratio/Momentum + quadrants |
| `get_signals(signal_type)` | `DataFrame` | All 4 signal types combined |
| `get_stock_rs_rating_history(days)` | `DataFrame` | RS Rating for heatmap |

### Caching Strategy

```python
Caching TTL (Time-To-Live):
- Market breadth:  300s (5 min)  - Real-time market state
- VN-Index:        300s (5 min)  - Regime detection
- Sector breadth:  300s (5 min)  - Sector rotation
- Signals:         60s  (1 min)  - Fast scan updates
- Sector list:     300s (5 min)  - Filter options
```

---

## Filter Bar Options

### Timeframe Selector

```python
TIMEFRAME_OPTIONS = {
    "30D":   30,    # 1 month
    "60D":   60,    # 2 months
    "90D":   90,    # 3 months (1 quarter)
    "180D":  180,   # 6 months
    "1Y":    252,   # 1 year (252 trading days)
}

Default: 180D (6 months)
Purpose: Control breadth history lookback window
```

### Sector Filter

```
Default: "All"
Purpose: Filter signals, RRG, RS heatmap by selected sector
Options: All sectors + "All" option
```

### Signal Type Filter

```python
SIGNAL_TYPES = {
    "all": "All Signals",
    "ma_crossover": "MA Cross",
    "volume_spike": "Volume",
    "breakout": "Breakout",
    "patterns": "Patterns",
}

Default: "all"
Purpose: Focus on specific signal types
```

---

## Watchlist Universe (Sector Rotation)

### Available Watchlists

| List | Count | Composition | Use Case |
|------|-------|-------------|----------|
| **BSC Universe** | 45 | Blue-chip banks, real estate, tech | Default balanced portfolio |
| **VN30** | 30 | 30 largest by market cap | Index tracking |
| **Banking** | 10 | Major Vietnamese banks | Sector focus |
| **Securities** | 10 | Brokerages | Sector focus |
| **Real Estate** | 10 | Real estate companies | Sector focus |
| **Technology** | 4 | Tech companies | Sector focus |

---

## Implementation Notes

### Design Philosophy

- **Glassmorphism:** Frosted glass effect with transparency gradients (modern crypto-terminal aesthetic)
- **Vietnamese Localization:** All action descriptions, patterns, UI text in Vietnamese with proper diacritics
- **Signal Strength:** Normalized 0-1 scale, displayed as 0-100% to users
- **Singleton Caching:** `@st.cache_resource` for service instance, `@st.cache_data` with TTL for methods
- **Parquet Format:** All data stored as parquet in `DATA/processed/technical/`
- **Session Persistence:** Filter state saved in `st.session_state` across reruns

### Known Limitations

1. **Divergence Detection:** Currently unimplemented (returns None)
   - Need: Price higher highs vs breadth lower highs (bearish)
   - Need: Price lower lows vs breadth higher lows (bullish)

2. **Volume Context:** Calculation logic not in service layer
   - Need: Determine HIGH/AVERAGE/LOW based on volume percentiles

3. **Sector Money Flow:** File path exists but calculation logic needs verification

4. **Recovery Indicator:** Condition for `is_recovering` flag not documented

---

## Summary Quick Reference

| Concept | Formula/Logic | Key Values |
|---------|--------------|-----------|
| **Market Score** | (MA50×0.5) + (MA20×0.3) + (MA100×0.2) | ≥60 Green, 40-59 Amber, <40 Red |
| **Uptrend** | MA50≥50 AND MA100≥50 | Required for STRONG_BUY, BUY, HOLD |
| **Regime** | If EMA9>EMA21×1.005 → BULLISH | 0.5% margin prevents false signals |
| **Exposure** | If BEARISH→0; else breadth-based | 0, 20, 40, 60, 80, 100% |
| **MA20 Higher Low** | min(last 3d) > min(previous 3d) | Triggers ACCUMULATING stage |
| **MA50 Higher Low** | min(last 5d) > min(previous 5d) | Triggers EARLY_REVERSAL stage |
| **RRG Quadrant** | rs_ratio > 1 AND rs_momentum > 0 | LEADING = buy, LAGGING = avoid |
| **Signal Priority** | Patterns > MA Cross > Volume > Breakouts | Patterns have highest conviction |

---

**End of Technical Analysis Dashboard Logic Document**
