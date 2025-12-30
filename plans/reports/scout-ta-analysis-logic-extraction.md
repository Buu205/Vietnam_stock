# Technical Analysis Dashboard - Logic & Formula Extraction Report

**Date:** 2025-12-30  
**Scope:** WEBAPP/pages/technical/ components, services, and models  
**Purpose:** Document all constants, formulas, signal logic, and pattern detection

---

## 1. FILE LOCATIONS & ARCHITECTURE

### Component Files
- **Market Overview** → `WEBAPP/pages/technical/components/market_overview.py` (813 lines)
- **Sector Rotation** → `WEBAPP/pages/technical/components/sector_rotation.py` (715 lines)
- **Stock Scanner** → `WEBAPP/pages/technical/components/stock_scanner.py` (831 lines)
- **Filter Bar** → `WEBAPP/pages/technical/components/ta_filter_bar.py` (254 lines)

### Service Layer
- **TA Dashboard Service** → `WEBAPP/pages/technical/services/ta_dashboard_service.py` (520 lines)

### Data Models
- **Market State** → `WEBAPP/core/models/market_state.py` (69 lines)

---

## 2. DESIGN CONSTANTS & COLOR SCHEMES

### Regime Styles (market_overview.py)
```python
REGIME_STYLES = {
    'BULLISH':  {'color': '#10B981', 'bg': 'rgba(16, 185, 129, 0.15)', 'border': '#10B981'},
    'BEARISH':  {'color': '#EF4444', 'bg': 'rgba(239, 68, 68, 0.15)', 'border': '#EF4444'},
    'NEUTRAL':  {'color': '#F59E0B', 'bg': 'rgba(245, 158, 11, 0.15)', 'border': '#F59E0B'},
}
```

### Signal Styles (market_overview.py)
```python
SIGNAL_STYLES = {
    'RISK_ON':  {'color': '#10B981', 'bg': 'rgba(16, 185, 129, 0.15)'},
    'RISK_OFF': {'color': '#EF4444', 'bg': 'rgba(239, 68, 68, 0.15)'},
    'CAUTION':  {'color': '#F59E0B', 'bg': 'rgba(245, 158, 11, 0.15)'},
}
```

### Breadth Colors (market_overview.py)
```python
BREADTH_COLORS = {
    'ma20': '#8B5CF6',   # Purple (short-term, fastest moving)
    'ma50': '#06B6D4',   # Cyan (medium-term)
    'ma100': '#F59E0B',  # Amber (long-term, slowest moving)
}
```

### Market Score Weighting (market_overview.py)
```python
MARKET_SCORE_WEIGHTS = {
    'ma50': 0.5,   # Trend backbone (50% importance)
    'ma20': 0.3,   # Timing/Trigger (30%)
    'ma100': 0.2,  # Safety filter (20%)
}
```

### RRG Quadrant Colors (sector_rotation.py)
```python
QUADRANT_COLORS = {
    'LEADING': '#10B981',      # Emerald Green  - Strong momentum + relative strength
    'IMPROVING': '#06B6D4',    # Cyan          - Strength improving
    'WEAKENING': '#F59E0B',    # Amber         - Strength declining
    'LAGGING': '#EF4444',      # Red           - Weak momentum + relative weakness
}
```

### Timeframe Definitions (ta_filter_bar.py)
```python
TIMEFRAME_OPTIONS = {
    "30D": 30,     # 1 month
    "60D": 60,     # 2 months
    "90D": 90,     # 3 months (1 quarter)
    "180D": 180,   # 6 months
    "1Y": 252,     # 1 year (252 trading days)
}
```

---

## 3. SIGNAL MATRIX - ACTION SIGNALS & RECOMMENDATIONS

### Signal Matrix Structure (market_overview.py)

**STRONG_BUY**
- Label: "STRONG BUY"
- Subtitle: "Deep Pullback"
- Action: "Giải ngân mạnh. Rũ bỏ hoàn hảo." (Strong deployment. Perfect shaking)
- Color: #059669 (dark green)
- Use Case: Extreme oversold pullback in uptrend

**BUY**
- Label: "BUY"
- Subtitle: "Normal Pullback"
- Action: "Mua gia tăng hoặc mở vị thế mới." (Scale in or new position)
- Color: #10B981 (green)
- Use Case: Moderate pullback in uptrend

**HOLD**
- Label: "HOLD"
- Subtitle: "Riding Trend"
- Action: "Nắm giữ danh mục. Trend vẫn tốt." (Maintain portfolio. Trend still good)
- Color: #3B82F6 (blue)
- Use Case: Healthy uptrend, no action needed

**WARNING**
- Label: "WARNING"
- Subtitle: "Overheated"
- Action: "Không mua đuổi. Canh chốt lời margin." (Don't chase. Take profit on rallies)
- Color: #F59E0B (amber)
- Use Case: Overbought conditions

**SELL**
- Label: "SELL"
- Subtitle: "Bull Trap"
- Action: "Bán hạ tỷ trọng. Đây là bẫy tăng giá." (Reduce exposure. This is a bull trap)
- Color: #DC2626 (red)
- Use Case: Bearish signal in downtrend

**DANGER**
- Label: "DANGER"
- Subtitle: "Market Crash"
- Action: "Đứng ngoài tuyệt đối. Không bắt đáy." (Stay on sidelines. Don't catch falling knife)
- Color: #7F1D1D (dark red)
- Use Case: Market crash/extreme panic

**WAIT**
- Label: "WAIT"
- Subtitle: "No Trend"
- Action: "Quan sát. Chưa có điểm vào an toàn." (Observe. No safe entry point)
- Color: #64748B (slate gray)
- Use Case: Sideways, no clear trend

### Bottom Detection Signals (market_overview.py)

**ACCUMULATING**
- Label: "ACCUMULATING"
- Subtitle: "Smart Money Entering"
- Action: "Theo dõi sát. Smart money đang tích lũy. Chuẩn bị vốn." (Watch closely. Accumulation phase. Prepare capital)
- Color: #6366F1 (indigo)
- Trigger: All MA < 30%, MA20 creating higher low + rising

**EARLY_BUY**
- Label: "EARLY BUY"
- Subtitle: "Early Reversal"
- Action: "Test mua 10-20% danh mục. Stop-loss chặt dưới đáy gần nhất." (Test buy 10-20%. Tight stop below recent low)
- Color: #22D3EE (cyan)
- Trigger: MA20 ≥ 25% + higher low confirmed, MA50 creating higher low

---

## 4. BOTTOM FORMATION STAGES

### Stage 1: CAPITULATION
```
Label:       "CAPITULATION"
Description: "Hoảng loạn bán tháo" (Panic selling)
Icon:        "1"
Color:       #7F1D1D (dark red)

Condition:   All MA < 25% (extreme oversold)
             AND no higher low yet formed
             
Interpretation: Market in maximum fear. Smart money may be preparing entry.
                Wait for MA20 to form higher low before considering entry.
```

### Stage 2: ACCUMULATING
```
Label:       "ACCUMULATING"
Description: "Smart money đang vào" (Smart money entering)
Icon:        "2"
Color:       #6366F1 (indigo)

Condition:   All MA < 30% (oversold)
             AND MA20 creates higher low (3-day window)
             AND MA20 is rising from that low
             
Logic:       - Recent 3d low > Previous 3d low
             - Current MA20 > Recent 3d low
             
Interpretation: Institutional buyers entering. Potential bottom forming.
                Risk-on traders can test entry 10-20% of position.
```

### Stage 3: EARLY_REVERSAL
```
Label:       "EARLY_REVERSAL"
Description: "Đảo chiều sớm" (Early reversal)
Icon:        "3"
Color:       #22D3EE (cyan)

Condition:   MA20 ≥ 25% (escaped oversold)
             AND MA20 higher low confirmed
             AND MA50 creates higher low (5-day window)
             AND MA50 is rising from that low
             
Logic:       - MA20 recent 3d low > MA20 previous 3d low
             - MA50 recent 5d low > MA50 previous 5d low
             - Current MA50 > Recent 5d low
             
Interpretation: Trend is reversing upward. Breadth expansion likely.
                Can increase exposure or add to positions.
```

---

## 5. BREADTH & MARKET HEALTH SCORING

### Market Breadth Definition
**What it measures:** Percentage of stocks trading above key moving averages

```
% > MA20  = (Stocks closing above 20-day MA) / Total stocks × 100
% > MA50  = (Stocks closing above 50-day MA) / Total stocks × 100
% > MA100 = (Stocks closing above 100-day MA) / Total stocks × 100
```

### Breadth Zones & Interpretation
```
Zone        Range    Interpretation
────────────────────────────────────
Overbought  80-100%  Too many stocks extended above MA
            
Neutral     20-80%   Balanced, healthy breadth
            
Oversold    0-20%    Extreme weakness, potential bottom
```

### Weighted Market Health Score (Line 505-509, market_overview.py)
```python
Market Score = (MA50_pct × 0.5) + (MA20_pct × 0.3) + (MA100_pct × 0.2)

Maximum score: 100 (all stocks above all MAs)
Minimum score: 0 (no stocks above any MA)

Score Color Coding:
- ≥ 60 → Green (#10B981) - Healthy
- 40-59 → Amber (#F59E0B) - Caution
- < 40 → Red (#EF4444) - Bearish
```

### Trend Filter Logic (Line 516-517, market_overview.py)
```python
is_uptrend = (breadth_ma50 ≥ 50) AND (breadth_ma100 ≥ 50)
```
**Interpretation:** Both medium and long-term breadth must be healthy for uptrend signal

---

## 6. SIGNAL MATRIX LOGIC - DECISION TREE

### Uptrend Scenario (Line 525-534, market_overview.py)
```
IF (MA50 ≥ 50 AND MA100 ≥ 50):  # UPTREND confirmed
    
    IF (MA20 < 20):
        → STRONG_BUY (extreme pullback, best risk/reward)
    
    ELIF (MA20 < 40):
        → BUY (normal pullback)
    
    ELIF (MA20 > 80):
        → WARNING (overbought, no new buys)
    
    ELSE (40 ≤ MA20 ≤ 80):
        → HOLD (ride the trend)
```

### Downtrend/Sideways Scenario (Line 536-547, market_overview.py)
```
IF NOT (MA50 ≥ 50 AND MA100 ≥ 50):  # DOWNTREND or SIDEWAYS
    
    IF (MA20 > 70):
        → SELL (elevated, distribute)
    
    ELIF (MA50 < 30 AND MA20 < 20 AND NOT MA20_higher_low):
        → DANGER (extreme crash, stay out)
    
    ELIF (bottom_stage == 'EARLY_REVERSAL'):
        → EARLY_BUY (reversal confirmed)
    
    ELIF (bottom_stage == 'ACCUMULATING'):
        → ACCUMULATING (smart money entering)
    
    ELSE:
        → WAIT (no clear setup)
```

---

## 7. CAPITAL ALLOCATION (EXPOSURE CONTROL)

### Exposure Level Calculation (Line 375-386, ta_dashboard_service.py)
```python
def _calculate_exposure(regime: str, breadth: float) -> int:
    """
    Determine capital allocation percentage based on regime and breadth.
    
    Returns: 0, 20, 40, 60, 80, or 100 (percentage of capital to deploy)
    """
    
    if regime == 'BEARISH':
        return 0  # Stay in cash
    
    if breadth ≥ 70:
        return 100  # Full deployment (strong breadth)
    elif breadth ≥ 55:
        return 80   # Heavy deployment
    elif breadth ≥ 40:
        return 60   # Moderate deployment
    elif breadth ≥ 25:
        return 40   # Conservative deployment
    else:
        return 20   # Minimal exposure (heavy pullback)
```

### Exposure Color Logic (Line 216-225, market_overview.py)
```python
if exposure ≥ 80:
    color = '#10B981'  # Green - aggressive
elif exposure ≥ 60:
    color = '#22C55E'  # Light Green
elif exposure ≥ 40:
    color = '#F59E0B'  # Amber - caution
elif exposure ≥ 20:
    color = '#FF9F43'  # Orange
else:
    color = '#EF4444'  # Red - defensive
```

---

## 8. REGIME DETECTION

### Regime Definition (Line 368-373, ta_dashboard_service.py)
```python
def _get_regime(ema9: float, ema21: float) -> str:
    """
    Detect market regime using 2 EMAs.
    
    EMA9 = Fast moving average (responsive)
    EMA21 = Slow moving average (trend)
    
    Margin: 0.5% threshold to avoid false signals
    """
    
    if ema9 > ema21 * 1.005:
        return 'BULLISH'    # EMA9 above EMA21
    elif ema9 < ema21 * 0.995:
        return 'BEARISH'    # EMA9 below EMA21
    else:
        return 'NEUTRAL'    # Within 0.5% = choppy/transition
```

---

## 9. HIGHER LOWS DETECTION - BOTTOM CONFIRMATION

### Higher Lows Concept
```
What: Compare recent low to previous low in breadth values
Why:  Confirms uptrend is forming even in downtrend environment
Pattern: Recent Low > Previous Low = Higher Low = Bullish reversal signal
```

### MA20 Higher Lows (3-Day Window) (Line 445-458, ta_dashboard_service.py)
```python
# Get last 10 days of MA20 breadth data
last_10_days = breadth_df.tail(10)

# Recent 3 days: positions [-3:] (days 8, 9, 10)
ma20_recent_window = last_3_days
ma20_recent_low = min(ma20_recent_window)

# Previous 3 days: positions [-6:-3] (days 5, 6, 7)
ma20_prev_window = days_5_to_7
ma20_prev_low = min(ma20_prev_window)

# Get current value (day 10)
ma20_current = last_10_days[-1]

# Higher Low Detection
ma20_higher_low = ma20_recent_low > ma20_prev_low
ma20_rising_from_low = ma20_current > ma20_recent_low

Returns:
{
    'ma20_higher_low': bool,        # True if recent low > previous low
    'ma20_recent_low': float,       # Lowest value in last 3 days
    'ma20_prev_low': float,         # Lowest value in previous 3 days
    'ma20_rising_from_low': bool,   # Current > recent low
}
```

### MA50 Higher Lows (5-Day Window) (Line 460-473, ta_dashboard_service.py)
```python
# Recent 5 days: positions [-5:] (days 6, 7, 8, 9, 10)
ma50_recent_window = last_5_days
ma50_recent_low = min(ma50_recent_window)

# Previous 5 days: positions [-10:-5] (days 1, 2, 3, 4, 5)
ma50_prev_window = days_1_to_5
ma50_prev_low = min(ma50_prev_window)

# Get current value (day 10)
ma50_current = last_10_days[-1]

# Higher Low Detection
ma50_higher_low = ma50_recent_low > ma50_prev_low
ma50_rising_from_low = ma50_current > ma50_recent_low

Returns:
{
    'ma50_higher_low': bool,        # True if recent low > previous low
    'ma50_recent_low': float,       # Lowest value in last 5 days
    'ma50_prev_low': float,         # Lowest value in previous 5 days
    'ma50_rising_from_low': bool,   # Current > recent low
}
```

---

## 10. BOTTOM DETECTION ALGORITHM

### Complete Bottom Detection (Line 477-519, ta_dashboard_service.py)

```python
def _detect_bottom_stage(ma20, ma50, ma100, higher_lows):
    """
    Detect 3-stage bottom formation process.
    Only triggered when NOT in uptrend (ma50 < 50 or ma100 < 50)
    """
    
    # Pre-check: Already in uptrend? No bottom needed
    if ma50 ≥ 50 and ma100 ≥ 50:
        return None
    
    # Calculate oversold conditions
    all_oversold = ma20 < 30 and ma50 < 30 and ma100 < 30
    extreme_oversold = ma20 < 25 and ma50 < 25 and ma100 < 25
    
    # Extract higher low information
    ma20_higher_low = higher_lows['ma20_higher_low']
    ma20_rising = higher_lows['ma20_rising_from_low']
    ma50_higher_low = higher_lows['ma50_higher_low']
    ma50_rising = higher_lows['ma50_rising_from_low']
    
    # ===== STAGE 1: CAPITULATION =====
    # Condition: Extreme panic, no buyers yet
    if extreme_oversold and not ma20_higher_low:
        return 'CAPITULATION'
        # All three MAs < 25%, AND MA20 still creating lower lows
        # = maximum fear, no signs of recovery yet
    
    # ===== STAGE 2: ACCUMULATING =====
    # Condition: Oversold but bottom forming (smart money entering)
    if all_oversold and ma20_higher_low and ma20_rising:
        return 'ACCUMULATING'
        # All three MAs < 30%, BUT
        # MA20 recent low > previous low (higher low)
        # AND MA20 is currently > recent low
        # = Smart money accumulating at the bottom
    
    # ===== STAGE 3: EARLY_REVERSAL =====
    # Condition: Escape oversold zone + both MAs forming higher lows
    if ma20 ≥ 25 and ma20_higher_low and ma50_higher_low and ma50_rising:
        return 'EARLY_REVERSAL'
        # MA20 escaped oversold (≥ 25%), AND
        // Both MA20 and MA50 have higher lows, AND
        // MA50 is rising from its low
        // = Reversal confirmed, uptrend starting
    
    # No stage detected
    return None
```

---

## 11. PATTERN INTERPRETATIONS - CANDLESTICK & CHART PATTERNS

### Bullish Patterns (stock_scanner.py, lines 48-68)

| Pattern | Vietnamese | Interpretation |
|---------|-----------|-----------------|
| Engulfing | Đảo chiều mạnh | Green candle completely engulfs red one |
| Hammer | Từ chối giảm giá | Lower wick ≥ 2× body, buyers reject lows |
| Morning Star | Mô hình 3 nến | (1) Long red, (2) Doji, (3) Long green = high conviction |
| Piercing | Xuyên thấu | Green opens below, closes >50% into red body |
| Three White Soldiers | 3 nến xanh liên tiếp | Bullish reversal at bottom |
| Inverted Hammer | Bấc trên dài | Upper wick long, small body. Needs confirmation |
| Harami Bullish | Nến xanh nhỏ trong nến đỏ | Small green inside red = momentum weakening |
| Doji | Thị trường bất định | Open = Close = indecision, await confirmation |
| Dragonfly Doji | Từ chối giảm giá mạnh | Long lower wick, Open = High = Close |
| Marubozu White | Nến không bấc (xanh) | No wicks, buyers control 100% of session |
| Tweezer Bottom | Đáy nhíp | 2 candles with same low = strong support |

### Bearish Patterns (stock_scanner.py, lines 71-92)

| Pattern | Vietnamese | Interpretation |
|---------|-----------|-----------------|
| Bearish Engulfing | Đảo chiều giảm mạnh | Red completely engulfs green |
| Hanging Man | Cảnh báo đảo chiều | Like hammer but at top of uptrend |
| Evening Star | Mô hình 3 nến | (1) Long green, (2) Doji, (3) Long red |
| Shooting Star | Từ chối tăng giá | Long upper wick, small body at bottom |
| Dark Cloud Cover | Mây đen che phủ | Red opens above, closes <50% into green |
| Three Black Crows | 3 nến đỏ liên tiếp | Bearish reversal at top |
| Harami Bearish | Nến đỏ nhỏ trong nến xanh | Small red inside green = momentum fade |
| Gravestone Doji | Từ chối tăng giá mạnh | Long upper wick, Open = Low = Close |
| Marubozu Black | Nến không bấc (đỏ) | No wicks, sellers control 100% |
| Tweezer Top | Đỉnh nhíp | 2 candles with same high = strong resistance |

### Chart Patterns (stock_scanner.py, lines 94-106)

| Pattern | Vietnamese | Interpretation |
|---------|-----------|-----------------|
| Double Bottom | Đáy đôi | Classic reversal. Breakout above neckline = confirm |
| Double Top | Đỉnh đôi | Classic reversal. Breakdown below neckline = confirm |
| Head Shoulders | Vai-Đầu-Vai | Bearish reversal. Breakdown neckline = confirm |
| Cup Handle | Tách và tay cầm | Bullish continuation. Breakout rim = resume uptrend |
| Flag Bull | Cờ tăng | Continuation after strong rally. Breakout = more upside |
| Flag Bear | Cờ giảm | Continuation after decline. Breakdown = more downside |

### Volume Context Interpretation Matrix (stock_scanner.py, lines 128-153)

**High Volume** = Strong conviction
**Average Volume** = Normal confirmation needed
**Low Volume** = Weak signal, awaiting confirmation

Example: Engulfing Pattern
```
Engulfing + HIGH Vol   → "Đảo chiều cực mạnh - Buyers áp đảo"
Engulfing + AVG Vol    → "Đảo chiều - Cần theo dõi phiên sau"
Engulfing + LOW Vol    → "Tín hiệu yếu - Chờ volume confirmation"
```

---

## 12. RELATIVE ROTATION GRAPH (RRG) - QUADRANT LOGIC

### RRG Concept
**Purpose:** Identify which sectors are leading (strong + improving) vs lagging (weak + deteriorating)

### Quadrant Definition (Line 388-399, ta_dashboard_service.py)
```python
def _determine_quadrant(rs_ratio, rs_momentum):
    """
    RS Ratio = Sector strength relative to market average
    RS Momentum = Rate of change of RS Ratio (5-day momentum)
    """
    
    # X-axis: RS Ratio
    # Y-axis: RS Momentum
    
    if rs_ratio > 1 and rs_momentum > 0:
        return 'LEADING'    # Top-right: Strong + Improving
    elif rs_ratio > 1 and rs_momentum <= 0:
        return 'WEAKENING'  # Bottom-right: Strong but Deteriorating
    elif rs_ratio <= 1 and rs_momentum <= 0:
        return 'LAGGING'    # Bottom-left: Weak + Declining
    else:
        return 'IMPROVING'  # Top-left: Weak but Improving
```

### Calculation Logic (Line 163-199, ta_dashboard_service.py)
```python
# RS Ratio = Sector strength score / Market average strength
sector_df['rs_ratio'] = sector_df['strength_score'] / sector_df['strength_score'].mean()

# RS Momentum = 5-day rate of change in RS Ratio
sector_df['rs_momentum'] = sector_df['rs_ratio'].diff(5) * 100

# Apply smoothing (default SMA3)
sector_df['rs_ratio_smooth'] = sector_df['rs_ratio'].rolling(3, min_periods=1).mean()
sector_df['rs_momentum_smooth'] = sector_df['rs_momentum'].rolling(3, min_periods=1).mean()
```

### Interpretation
```
LEADING:   Buy sector leaders. Momentum strongest.
IMPROVING: Watch accumulation. Entry candidates.
WEAKENING: Exit before breakdown. Losing momentum.
LAGGING:   Stay out. Worst performers.
```

---

## 13. STOCK SCANNER - SIGNAL TYPES & DETECTION

### Signal Type Categories (ta_filter_bar.py, lines 35-41)
```python
SIGNAL_TYPES = {
    "all": "All Signals",
    "ma_crossover": "MA Cross",
    "volume_spike": "Volume",
    "breakout": "Breakout",
    "patterns": "Patterns",
}
```

### Signal Loading Pipeline (Line 205-356, ta_dashboard_service.py)

**1. Candlestick Patterns (HIGHEST PRIORITY)**
```
Source: DATA/processed/technical/alerts/daily/patterns_latest.parquet
Columns: symbol, date, pattern_name, signal, price, strength
Maps: BULLISH → BUY, BEARISH → SELL
```

**2. MA Crossover Signals**
```
Source: DATA/processed/technical/alerts/daily/ma_crossover_latest.parquet
Types: MA_CROSS_ABOVE (Golden Cross), MA_CROSS_BELOW (Death Cross)
Strength: 0.7 (default)
```

**3. Volume Spike Signals**
```
Source: DATA/processed/technical/alerts/daily/volume_spike_latest.parquet
Signal: Based on signal column (BULLISH, BEARISH, NOISE)
Volume Context: Derived from volume_ratio (e.g., "2.5x")
Strength: confidence column
```

**4. Breakout Signals**
```
Source: DATA/processed/technical/alerts/daily/breakout_latest.parquet
Types: BREAKOUT_UP (bullish), BREAKDOWN (bearish)
Strength: 0.8 (default)
```

---

## 14. MARKET STATE DATACLASS

### MarketState Fields (market_state.py)

| Field | Type | Purpose |
|-------|------|---------|
| `date` | datetime | Current date |
| `vnindex_close` | float | VN-Index closing price |
| `vnindex_change_pct` | float | Daily % change |
| `regime` | str | BULLISH/NEUTRAL/BEARISH |
| `ema9` | float | 9-day EMA (fast) |
| `ema21` | float | 21-day EMA (slow) |
| `breadth_ma20_pct` | float | % stocks > MA20 (0-100) |
| `breadth_ma50_pct` | float | % stocks > MA50 (0-100) |
| `breadth_ma100_pct` | float | % stocks > MA100 (0-100) |
| `ad_ratio` | float | Advance/Decline ratio |
| `exposure_level` | int | Capital allocation (0, 20, 40, 60, 80, 100) |
| `divergence_type` | str | BULLISH/BEARISH or None |
| `divergence_strength` | int | 0-3 (strength of divergence) |
| `signal` | str | RISK_ON/RISK_OFF/CAUTION |
| `prev_breadth_ma20_pct` | float | Previous day MA20 (optional) |
| `prev_breadth_ma50_pct` | float | Previous day MA50 (optional) |
| `ma20_higher_low` | bool | Recent low > previous low |
| `ma20_recent_low` | float | Min of last 3 days MA20 |
| `ma20_prev_low` | float | Min of previous 3 days MA20 |
| `ma20_rising_from_low` | bool | Current > recent low |
| `ma50_higher_low` | bool | Recent low > previous low |
| `ma50_recent_low` | float | Min of last 5 days MA50 |
| `ma50_prev_low` | float | Min of previous 5 days MA50 |
| `ma50_rising_from_low` | bool | Current > recent low |
| `bottom_stage` | str | CAPITULATION/ACCUMULATING/EARLY_REVERSAL/None |

---

## 15. SERVICE METHODS - DATA LOADING & CACHING

### Caching Strategy (ta_dashboard_service.py)

| Data | Cache TTL | Purpose |
|------|-----------|---------|
| Market breadth | 300s (5 min) | Real-time market state |
| VN-Index | 300s (5 min) | Regime detection |
| Sector breadth | 300s (5 min) | Sector rotation |
| Signals | 60s (1 min) | Fast scan updates |
| Sector list | 300s (5 min) | Filter options |

### Key Service Methods

**get_market_state()**
- Combines VN-Index, breadth, higher lows detection
- Calculates regime, exposure, bottom stage
- Returns: MarketState object

**get_breadth_history(days)**
- Returns historical breadth + VN-Index for line chart
- Merges market breadth with price data

**get_sector_ranking()**
- Gets latest sector strength scores
- Sorts by ranking

**get_sector_money_flow(timeframe)**
- Returns 1D/1W/1M money flow by sector

**get_sector_rs_for_rrg(smooth, trail_days)**
- Calculates RS Ratio and Momentum
- Determines quadrant for each sector

**get_signals(signal_type)**
- Loads all 4 signal types (patterns, MA cross, volume, breakout)
- Combines and normalizes

**get_stock_rs_rating_history(days)**
- Returns RS Rating history for heatmap visualization

---

## 16. FILTER BAR & OPTIONS

### Timeframe Selector
```
Options: 30D, 60D, 90D, 180D, 1Y
Default: 180D (6 months)
Purpose: Control breadth history lookback
```

### Sector Filter
```
Default: "All"
Purpose: Filter signals, RRG, RS heatmap by sector
```

### Signal Type Filter
```
Options: all, ma_crossover, volume_spike, breakout, patterns
Default: all
Purpose: Focus on specific signal types
```

### Watchlists (sector_rotation.py, lines 55-78)

**BSC Universe** (Default)
- 45 stocks: blue-chip banks, real estate, technology, energy
- Balanced sector representation

**VN30** (30 largest by cap)
**Banking** (10 major banks)
**Securities** (10 brokerages)
**Real Estate** (10 real estate companies)
**Technology** (4 tech companies)

---

## 17. UNRESOLVED QUESTIONS & NOTES

### Questions

1. **Divergence Detection**: Current implementation sets `divergence_type=None` and `divergence_strength=0` - no actual divergence calculation present. Need implementation for:
   - Price higher highs vs breadth lower highs (bearish)
   - Price lower lows vs breadth higher lows (bullish)

2. **Volume Context Calculation**: How is `volume_context` ('HIGH'/'AVG'/'LOW') determined? Not found in service layer - should be calculated when generating signals.

3. **Sector Money Flow**: File path checked but data source/calculation logic not visible. Need to verify pipeline generates this data.

4. **Recovery Indicator**: Line 567 shows recovery HTML rendering but recovery_html only populated if `is_recovering` is True - what triggers this flag?

### Notes

- **Glassmorphism Design**: All components use frosted glass effect with transparency gradients for modern crypto-terminal aesthetic
- **Vietnamese Localization**: All action descriptions, pattern names, and UI text in Vietnamese with proper diacritics
- **Signal Strength**: 0-1 scale (decimal) normalized to 0-100 for display
- **Singleton Caching**: Service uses @st.cache_resource for singleton, @st.cache_data for method caching with 60-300s TTL
- **Data Files**: All sourcing from `DATA/processed/technical/` parquet format
- **Session State**: Multiple session state keys for filter persistence across reruns

---

## 18. KEY FORMULAS SUMMARY TABLE

| Calculation | Formula | Purpose |
|------------|---------|---------|
| Market Score | (MA50% × 0.5) + (MA20% × 0.3) + (MA100% × 0.2) | Weighted breadth health |
| Exposure | If BEARISH→0; else if Breadth≥70→100; ≥55→80; ≥40→60; ≥25→40; else→20 | Capital allocation % |
| Regime | If EMA9 > EMA21×1.005→BULLISH; <0.995→BEARISH; else→NEUTRAL | Market direction |
| RS Ratio | Sector Strength Score / Market Average Strength | Relative performance |
| RS Momentum | Diff of RS Ratio over 5 days × 100 | Rate of change |
| Higher Low (MA20) | Min(last 3 days) > Min(previous 3 days) | Bottom confirmation |
| Higher Low (MA50) | Min(last 5 days) > Min(previous 5 days) | Trend reversal |
| Quadrant | Based on RS Ratio > 1 AND RS Momentum > 0 | Sector positioning |

---

**End of Report**
