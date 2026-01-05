# Technical Dashboard - Trading Logic Reference

**Single Source of Truth for Trading Parameters & Logic**
**Last Updated:** 2026-01-04

---

## Quick Navigation

1. [Tab 1: Market Overview](#tab-1-market-overview)
2. [Tab 2: Sector Rotation (RRG)](#tab-2-sector-rotation)
3. [Tab 3: Stock Scanner](#tab-3-stock-scanner)
4. [Tab 4: RS Rating](#tab-4-rs-rating-relative-strength)
5. [Tab 5: Money Flow](#tab-5-money-flow)
6. [Tab 6: Sector Ranking](#tab-6-sector-ranking)
7. [Global Parameters](#global-parameters)
8. [Color Reference](#color-reference)

---

# Tab 1: Market Overview

## 1.1 Market Health Score

**Formula:**
```
Market Score = (MA50_breadth × 0.5) + (MA20_breadth × 0.3) + (MA100_breadth × 0.2)
```

| Component | Weight | Role |
|-----------|--------|------|
| MA50 | 50% | Trend backbone (primary) |
| MA20 | 30% | Timing/Trigger (entry) |
| MA100 | 20% | Safety filter (avoid bear) |

**Score Interpretation:**

| Score | Color | Market State | Action |
|-------|-------|--------------|--------|
| ≥ 60 | Green | Healthy | Aggressive deployment |
| 40-59 | Amber | Caution | Conservative approach |
| < 40 | Red | Bearish | Defensive/wait |

---

## 1.2 Regime Detection

**Method:** EMA9 vs EMA21 with 0.5% margin

| Condition | Regime | Meaning |
|-----------|--------|---------|
| EMA9 > EMA21 × 1.005 | BULLISH | Short-term above long-term by >0.5% |
| EMA9 < EMA21 × 0.995 | BEARISH | Short-term below long-term by >0.5% |
| Within margin | NEUTRAL | Choppy/transitional |

---

## 1.3 Uptrend Confirmation

**Rule:** Uptrend confirmed when BOTH:
- MA50 breadth ≥ 50%
- MA100 breadth ≥ 50%

If either < 50% → Downtrend or Sideways

---

## 1.4 Signal Matrix (9 Signals)

### Uptrend Signals (MA50 ≥ 50 AND MA100 ≥ 50)

| Signal | Condition | Action |
|--------|-----------|--------|
| **STRONG_BUY** | MA20 < 20% | Giải ngân mạnh. Rũ bỏ hoàn hảo. |
| **BUY** | MA20 < 40% | Mua gia tăng hoặc mở vị thế mới. |
| **HOLD** | MA20 40-80% | Nắm giữ danh mục. Trend vẫn tốt. |
| **WARNING** | MA20 > 80% | Không mua đuổi. Canh chốt lời margin. |

### Downtrend Signals (MA50 < 50 OR MA100 < 50)

| Signal | Condition | Action |
|--------|-----------|--------|
| **SELL** | MA20 > 70% | Bán hạ tỷ trọng. Đây là bẫy tăng giá. |
| **DANGER** | MA50 < 30% + MA20 < 20% + No Higher Low | Đứng ngoài tuyệt đối. Không bắt đáy. |
| **WAIT** | No clear signal | Quan sát. Chưa có điểm vào an toàn. |

### Bottom Detection Signals

| Signal | Condition | Action |
|--------|-----------|--------|
| **ACCUMULATING** | All MA < 30% + MA20 Higher Low | Theo dõi sát. Smart money đang tích lũy. |
| **EARLY_BUY** | MA20 ≥ 25% + Both Higher Lows | Test mua 10-20%. Stop-loss chặt dưới đáy. |

---

## 1.5 Bottom Formation (3 Stages)

Chỉ active khi NOT in uptrend (MA50 < 50 OR MA100 < 50)

| Stage | Threshold | Condition | Meaning |
|-------|-----------|-----------|---------|
| **1. CAPITULATION** | All MA < 25% | No MA20 higher low yet | Hoảng loạn bán tháo. Wait. |
| **2. ACCUMULATING** | All MA < 30% | MA20 higher low (7d) + rising | Smart money đang vào. Watch closely. |
| **3. EARLY_REVERSAL** | MA20 ≥ 25% | Both MA20 + MA50 higher lows | Đảo chiều sớm. Test buy 10-20%. |

**Flow:** CAPITULATION → ACCUMULATING → EARLY_REVERSAL → RECOVERY

---

## 1.6 Higher Low Detection

**Purpose:** Confirm downtrend reversing (recent low > previous low)

| Indicator | Window | Calculation |
|-----------|--------|-------------|
| MA20 | 7 days | min(last 7d) > min(previous 7d) |
| MA50 | 9 days | min(last 9d) > min(previous 9d) |

**Source:** 3-year backtest (2023-2025)
- MA20 median cycle: 14.5 days → window = 7 days
- MA50 median cycle: 19.0 days → window = 9 days

---

## 1.7 Capital Allocation (Exposure)

**Rule:** BEARISH regime = 0% exposure regardless of breadth

| Breadth | Exposure | Action |
|---------|----------|--------|
| ≥ 70% | 100% | Full deployment |
| 55-69% | 80% | Heavy deployment |
| 40-54% | 60% | Moderate deployment |
| 25-39% | 40% | Conservative deployment |
| < 25% | 20% | Minimal exposure |

---

## 1.8 Breadth Zones

| Zone | Range | Meaning |
|------|-------|---------|
| Extreme Overbought | 90-100% | Risk of pullback |
| Overbought | 80-90% | Caution zone |
| Neutral High | 60-80% | Healthy strength |
| Neutral | 40-60% | Balanced |
| Neutral Low | 20-40% | Weakness |
| Oversold | 10-20% | Opportunity |
| Extreme Oversold | 0-10% | Critical buying opportunity |

---

# Tab 2: Sector Rotation

## 2.1 RRG (Relative Rotation Graph) Overview

**Purpose:** Identify leading vs lagging sectors relative to VN-Index

**Dimensions:**
- X-axis: RS Ratio (strength vs VN-Index, normalized around 100)
- Y-axis: RS Momentum (rate of change of RS-Ratio, normalized around 100)

**Output:** `DATA/processed/technical/sector/rrg_latest.parquet`

---

## 2.2 RRG Calculation Steps

### Step-by-Step Formula

```python
RS_PERIOD = 10    # Period for RS-Ratio calculation
MOM_PERIOD = 10   # Period for RS-Momentum calculation
```

| Step | Formula | Description |
|------|---------|-------------|
| 1. Sector Price | Market-cap weighted average of sector stocks | Daily sector index |
| 2. RS-Line | sector_price / vnindex_price × 100 | Raw relative strength |
| 3. RS-Ratio (raw) | SMA(RS-Line, 10) | Smoothed RS |
| 4. RS-Ratio (norm) | RS-Ratio / SMA(RS-Ratio, 10) × 100 | Normalized around 100 |
| 5. RS-Momentum | pct_change(RS-Ratio, 10) × 100 + 100 | Rate of change, normalized |

### Sector Price Calculation (Market-Cap Weighted)

```python
# For each sector:
sector_price = np.average(stock_closes, weights=market_caps)
```

---

## 2.3 Quadrant Classification

| Quadrant | RS Ratio | RS Momentum | Action |
|----------|----------|-------------|--------|
| **LEADING** | ≥ 100 | ≥ 100 | BUY - Best performers, outperforming market |
| **WEAKENING** | ≥ 100 | < 100 | WATCH - Still strong but fading momentum |
| **LAGGING** | < 100 | < 100 | AVOID - Worst performers, underperforming |
| **IMPROVING** | < 100 | ≥ 100 | ACCUMULATE - Gaining momentum, potential turnaround |

**Rotation Direction (Clockwise):** IMPROVING → LEADING → WEAKENING → LAGGING → IMPROVING

---

## 2.4 Trend Direction (Based on Momentum)

| RS Momentum | Trend Direction | Meaning |
|-------------|-----------------|---------|
| > 102 | ACCELERATING | Momentum increasing rapidly |
| 100-102 | STABLE | Consistent momentum |
| 98-100 | SLOWING | Momentum decreasing |
| < 98 | DECLINING | Significant momentum loss |

---

## 2.5 RRG Interpretation

| Scenario | Signal | Action |
|----------|--------|--------|
| Sector entering LEADING | Strong outperformance | Increase allocation |
| Sector leaving LEADING to WEAKENING | Momentum fading | Reduce or hold |
| Sector in LAGGING | Underperforming | Avoid or short |
| Sector entering IMPROVING | Turnaround starting | Start accumulating |

---

## 2.6 Watchlists

| List | Count | Use Case |
|------|-------|----------|
| BSC Universe | 44 | Default balanced portfolio |
| VN30 | 30 | Index tracking |
| Banking | 15 | Sector focus |
| Securities | 10 | Sector focus |
| Real Estate | 10 | Sector focus |
| Technology | 4 | Sector focus |

---

# Tab 3: Stock Scanner

## 3.1 Signal Priority System

Khi nhiều signals trong 1 ngày cho 1 ticker, priority quyết định primary signal:

| Priority | Category | Patterns | Rationale |
|----------|----------|----------|-----------|
| 1 | Breakout | Volume/Price Breakout | Highest conviction |
| 2 | Strong Reversal | morning_star, evening_star, engulfing, three_white_soldiers, three_black_crows | Multi-candle, reliable |
| 3 | Single Candle | hammer, inverted_hammer, shooting_star, hanging_man | Needs confirmation |
| 4 | MA Crossover | MA20/50/100/200 Cross | Lagging indicator |
| 5 | Indecision | doji, spinning_top | Context-dependent |

---

## 3.2 Signal Strength Scoring

| Signal Type | Base Strength | Bonuses | Max |
|-------------|---------------|---------|-----|
| Breakout | 70 | +15 volume_confirmed, +15 vol_ratio>1.5 | 100 |
| Strong Reversal | 80-100 | - | 100 |
| Single Candle | 28-36 | - | 36 |
| MA Crossover | Period-based | MA20=50, MA50=75, MA100=85, MA200=100 | 100 |
| DOJI | 23 | - | 23 |

---

## 3.3 Context-Aware DOJI

DOJI signal phụ thuộc prior trend:

| Prior Trend | DOJI Signal | Interpretation |
|-------------|-------------|----------------|
| UPTREND / STRONG_UP | BEARISH | Reversal warning at top |
| DOWNTREND / STRONG_DOWN | BULLISH | Hope for reversal at bottom |
| SIDEWAYS | NEUTRAL | Indecision continues |

---

## 3.4 Trend Classification

| Condition | Trend |
|-----------|-------|
| SMA20 > 5% AND SMA50 > 5% | STRONG_UP |
| SMA20 > 2% AND SMA50 > 2% | UPTREND |
| SMA20 < -5% AND SMA50 < -5% | STRONG_DOWN |
| SMA20 < -2% AND SMA50 < -2% | DOWNTREND |
| Otherwise | SIDEWAYS |

---

## 3.5 Strategy Signal (TREND + PATTERN)

| Trend | Pattern Signal | Strategy |
|-------|----------------|----------|
| UPTREND | BULLISH | BUY |
| UPTREND | BEARISH | PULLBACK (wait) |
| DOWNTREND | BEARISH | SELL |
| DOWNTREND | BULLISH | BOUNCE (risky) |
| SIDEWAYS | BULLISH | BUY |
| SIDEWAYS | BEARISH | SELL |

---

## 3.6 Volume Context

| Level | Condition | Interpretation |
|-------|-----------|----------------|
| HIGH | ≥ 2x average | Strong conviction |
| AVG | Normal | Needs confirmation |
| LOW | Below average | Weak signal |

**Pattern + Volume Matrix:**

| Pattern | Volume | Interpretation |
|---------|--------|----------------|
| Engulfing + HIGH | - | Đảo chiều cực mạnh. Buyers áp đảo. |
| Engulfing + AVG | - | Đảo chiều. Cần theo dõi phiên sau. |
| Engulfing + LOW | - | Tín hiệu yếu. Chờ volume confirmation. |
| Hammer + HIGH | - | Từ chối mạnh. Đáy có thể hình thành. |
| Hammer + LOW | - | Từ chối yếu. Chưa an toàn vào. |

---

## 3.7 Candlestick Patterns

### Bullish Patterns

| Pattern | Vietnamese | Signal |
|---------|-----------|--------|
| Engulfing | Đảo chiều mạnh | Nến xanh bao trùm nến đỏ |
| Hammer | Từ chối giảm giá | Bấc dưới ≥ 2x thân |
| Morning Star | 3 nến đảo chiều | (1) Đỏ, (2) Doji, (3) Xanh |
| Three White Soldiers | 3 xanh liên tiếp | Đảo chiều tăng mạnh |
| Inverted Hammer | Bấc trên dài | Cần confirm phiên sau |
| Dragonfly Doji | Từ chối giảm mạnh | Bấc dưới cực dài |

### Bearish Patterns

| Pattern | Vietnamese | Signal |
|---------|-----------|--------|
| Bearish Engulfing | Đảo chiều giảm | Nến đỏ bao trùm nến xanh |
| Hanging Man | Cảnh báo đảo chiều | Giống Hammer nhưng ở đỉnh |
| Evening Star | 3 nến đảo chiều | (1) Xanh, (2) Doji, (3) Đỏ |
| Three Black Crows | 3 đỏ liên tiếp | Đảo chiều giảm mạnh |
| Shooting Star | Từ chối tăng giá | Bấc trên dài, thân nhỏ |
| Gravestone Doji | Từ chối tăng mạnh | Bấc trên cực dài |

---

## 3.8 Breakout/Breakdown

| Type | Condition | Strength Bonuses |
|------|-----------|------------------|
| BREAKOUT_UP | Price > Resistance | +15 if volume_confirmed, +15 if vol_ratio > 1.5 |
| BREAKDOWN | Price < Support | +15 if volume_confirmed, +15 if vol_ratio > 1.5 |

---

## 3.9 MA Crossover

| Type | Condition | Strength |
|------|-----------|----------|
| Golden Cross | Short MA > Long MA | MA20=50, MA50=75, MA100=85, MA200=100 |
| Death Cross | Short MA < Long MA | Same as above |

---

# Tab 4: RS Rating (Relative Strength)

## 4.1 RS Rating Overview

**Purpose:** Rank stocks by price performance (1-99 scale, higher = stronger)

**Output:** `DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet`

**Columns:**
- `rs_1m`, `rs_3m`, `rs_6m`, `rs_9m`, `rs_12m`: Individual period RS (1-99)
- `rs_rating`: Combined weighted RS with penalty
- `rs_rating_raw`: Combined RS before penalty
- `ret_1m`, `ret_3m`, `ret_6m`, `ret_9m`, `ret_12m`: Raw returns (%)

---

## 4.2 Return Periods

| Period | Trading Days | Purpose |
|--------|--------------|---------|
| 1M | 21 | Current momentum |
| 3M | 63 | Medium-term trend (most important) |
| 6M | 126 | Extended trend |
| 9M | 189 | Historical context |
| 12M | 252 | Long-term history |

---

## 4.3 Combined RS Score Weights

**Formula (Short-term Focused):**
```
rs_score = 0.20×rs_1m + 0.40×rs_3m + 0.25×rs_6m + 0.10×rs_9m + 0.05×rs_12m
```

| Period | Weight | Role |
|--------|--------|------|
| 1M | 20% | Current momentum |
| 3M | **40%** | Most important: medium-term trend |
| 6M | 25% | Extended trend |
| 9M | 10% | Historical context |
| 12M | 5% | Long-term history |

**Note:** Uses individual RS ratings (1-99) not raw returns to prevent extreme values from dominating.

---

## 4.4 Penalty System (Downtrend Detection)

**Purpose:** Penalize stocks in TRUE downtrend (not noise/flat base)

### Penalty Factors

| Condition | Penalty | Effect |
|-----------|---------|--------|
| 1M return < -2% | 0.85 | 15% reduction |
| 3M return < -2% | 0.70 | 30% reduction |
| 1M return < -15% | 0.85 | Additional 15% (crash protection) |

### Combined Penalty Examples

| Scenario | Penalty Calculation | Final Penalty |
|----------|---------------------|---------------|
| 1M only < -2% | 0.85 | 0.85 |
| 3M only < -2% | 0.70 | 0.70 |
| Both 1M & 3M < -2% | 0.85 × 0.70 | 0.595 |
| Crash (1M < -15%) + 3M < -2% | 0.85 × 0.85 × 0.70 | 0.506 |

### Tolerance Thresholds

| Threshold | Value | Purpose |
|-----------|-------|---------|
| THRESHOLD_1M | -2.0% | Distinguish noise from real drops |
| THRESHOLD_3M | -2.0% | Same as above |
| CRASH_THRESHOLD | -15.0% | "Falling knife" detection |

**Note:** Stocks consolidating/flat base (e.g., -0.5% to -2%) won't be penalized.

---

## 4.5 Final RS Rating Calculation

**Formula:**
```
rs_rating = (rs_rating_raw × penalty).round().clip(1, 99)
```

**Steps:**
1. Calculate individual period returns (ret_1m, ret_3m, etc.)
2. Rank each period return → individual RS (1-99 percentile)
3. Weighted sum of individual RS → rs_score_raw
4. Percentile rank of rs_score_raw → rs_rating_raw (1-99)
5. Apply penalty based on 1M/3M returns → rs_rating

---

## 4.6 RS Rating Interpretation

| RS Rating | Interpretation | Action |
|-----------|----------------|--------|
| 90-99 | Market leader | Strong buy candidate |
| 80-89 | Very strong | Buy on pullback |
| 70-79 | Above average | Hold/Accumulate |
| 50-69 | Average | Watch |
| 30-49 | Below average | Avoid |
| 1-29 | Laggard | Sell/Short |

---

## 4.7 Example: CSV Stock (After Fix)

**Before OHLCV Fix (Incorrect):**
- ret_12m: +373.7% (unadjusted stock split)
- rs_rating: 98 (artificially high)

**After OHLCV Fix (Correct):**
- ret_1m: -8.5%, ret_3m: -12.3%
- rs_1m: 8, rs_3m: 29
- rs_rating_raw: 6
- penalty: 0.595 (both 1M & 3M penalties)
- **rs_rating: 4** (correctly penalized)

---

## 4.8 Data Quality Note

**OHLCV Adjustment (2026-01-04):**
- All 458 symbols refreshed from vnstock_data API
- Corporate actions (splits/dividends) properly adjusted
- RS Rating penalty logic re-enabled

**Exchange Daily Limits (Guaranteed Detection):**
- HOSE: ±7%
- HNX: ±10%
- UPCOM: ±15%

If |daily_return| exceeds limit → 100% unadjusted corporate action → auto-refresh

---

# Tab 5: Money Flow

## 5.1 Money Flow Overview

**Purpose:** Track fund flows using volume-based indicators to identify accumulation/distribution

**Levels:**
- Individual Stock: `DATA/processed/technical/money_flow/individual_money_flow.parquet`
- Sector Level: `DATA/processed/technical/money_flow/sector_money_flow_1d.parquet`

---

## 5.2 Individual Stock Money Flow Indicators

### Chaikin Money Flow (CMF)

```python
cmf_20 = ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)
```

| CMF Value | Meaning |
|-----------|---------|
| > 0.10 | Strong accumulation (+2 score) |
| 0.05 - 0.10 | Accumulation (+1 score) |
| -0.05 - 0.05 | Neutral (0 score) |
| -0.10 - -0.05 | Distribution (-1 score) |
| < -0.10 | Strong distribution (-2 score) |

### Money Flow Index (MFI)

```python
mfi_14 = MFI(high, low, close, volume, timeperiod=14)
```

| MFI Value | Meaning | Score Impact |
|-----------|---------|--------------|
| > 70 | Overbought | -1 (reversal risk) |
| 30 - 70 | Normal | 0 |
| < 30 | Oversold | +1 (potential bounce) |

### On-Balance Volume (OBV)

```python
obv = OBV(close, volume)
obv_trend = obv > obv_ma20 * 1.05  # OBV above 20-MA by 5%
```

| OBV Trend | Meaning | Score Impact |
|-----------|---------|--------------|
| OBV > MA20 × 1.05 | Accumulation | +1 |
| OBV in range | Neutral | 0 |
| OBV < MA20 × 0.95 | Distribution | -1 |

### Accumulation/Distribution Line (AD)

```python
ad_line = AD(high, low, close, volume)
```

### Volume Price Trend (VPT)

```python
vpt[i] = vpt[i-1] + volume[i] × (close[i] - close[i-1]) / close[i-1]
```

---

## 5.3 Money Flow Signal Classification

**Composite Score = CMF Score + MFI Score + OBV Score**

| Total Score | Signal | Interpretation |
|-------------|--------|----------------|
| ≥ 3 | STRONG_ACCUMULATION | Smart money aggressively buying |
| 1-2 | ACCUMULATION | Net buying pressure |
| -2 to 2 | NEUTRAL | No clear direction |
| -2 to -1 | DISTRIBUTION | Net selling pressure |
| ≤ -3 | STRONG_DISTRIBUTION | Smart money aggressively selling |

---

## 5.4 Sector Money Flow

**Formula:**
```python
sector_money_flow = Σ(close × volume) for all stocks in sector
inflow_pct = (today_flow - prev_flow) / prev_flow × 100
```

### Multi-Timeframe Analysis

| Timeframe | Lookback | Purpose |
|-----------|----------|---------|
| 1D | 1 trading day | Daily momentum |
| 1W | 7 calendar days | Weekly trend |
| 1M | 30 calendar days | Monthly trend |

### Flow Signal Classification

| Inflow % | Signal | Action |
|----------|--------|--------|
| > +10% | STRONG_INFLOW | Sector heating up, consider buying |
| +3% to +10% | INFLOW | Positive flow, watch closely |
| -3% to +3% | NEUTRAL | Balanced flow |
| -10% to -3% | OUTFLOW | Money leaving sector |
| < -10% | STRONG_OUTFLOW | Sector cooling, avoid or sell |

---

## 5.5 Top Contributors

For each sector, identify top 3 stocks by money flow (close × volume).

**Example Output:**
```
Sector: Ngân hàng
Top Contributors: VCB, BID, CTG
Money Flow: 1,234B VND
Inflow: +8.5%
Signal: INFLOW
```

---

# Tab 6: Sector Ranking

## 6.1 Sector Ranking Overview

**Purpose:** Rank sectors using composite scoring from multiple factors

**Output:** `DATA/processed/technical/sector/ranking_latest.parquet`

---

## 6.2 Scoring Components & Weights

```python
WEIGHTS = {
    'rs_score': 0.30,         # Relative Strength
    'money_flow_score': 0.25, # Money Flow
    'breadth_score': 0.25,    # Market Breadth
    'momentum_score': 0.20    # Price Momentum
}
```

| Component | Weight | Source | Description |
|-----------|--------|--------|-------------|
| RS Score | 30% | RS Rating | Average RS rating of sector stocks |
| Money Flow Score | 25% | Sector Money Flow | Inflow/outflow percentage |
| Breadth Score | 25% | Sector Breadth | % stocks above MA50 |
| Momentum Score | 20% | Technical Data | 20-day sector return |

---

## 6.3 Score Calculations

### RS Score (30%)

```python
# Average RS rating of all stocks in sector
sector_rs = df.groupby('sector_code')['rs_rating'].mean()
# Normalize to 0-100 scale
rs_score = (sector_rs - min) / (max - min) × 100
```

### Money Flow Score (25%)

```python
# Based on inflow_pct (-100% to +100%)
money_flow_score = (inflow_pct + 100) / 2
# Result: 0-100 scale where 50 = neutral
```

### Breadth Score (25%)

```python
# % of sector stocks above MA50
breadth_score = above_ma50_pct  # Already 0-100 scale
```

### Momentum Score (20%)

```python
# Average 20-day return of sector stocks
avg_return = sector_stocks['close'].pct_change(20).mean()
# Normalize: -20% to +20% → 0 to 100
momentum_score = (avg_return + 0.20) / 0.40 × 100
```

---

## 6.4 Composite Score Formula

```python
composite_score = (
    rs_score × 0.30 +
    money_flow_score × 0.25 +
    breadth_score × 0.25 +
    momentum_score × 0.20
)
```

---

## 6.5 Sector Trend Classification

| Condition | Trend | Meaning |
|-----------|-------|---------|
| composite ≥ 70 AND rs ≥ 60 | LEADING | Top performer, strong RS |
| composite ≥ 50 AND money_flow ≥ 60 | IMPROVING | Gaining momentum |
| composite < 30 | LAGGING | Poor performer |
| composite < 50 AND money_flow < 40 | WEAKENING | Losing momentum |
| Otherwise | NEUTRAL | Average performer |

---

## 6.6 Sector Ranking Interpretation

| Rank | Score Range | Action |
|------|-------------|--------|
| 1-5 | 70-100 | Top sectors - overweight |
| 6-10 | 50-70 | Above average - market weight |
| 11-15 | 30-50 | Below average - underweight |
| 16-19 | 0-30 | Laggards - avoid |

---

## 6.7 Example Sector Ranking Output

```
Rank | Sector       | Score | RS | MF | Breadth | Momentum | Trend
-----|--------------|-------|----|----|---------|----------|-------
1    | Ngân hàng    | 78.5  | 82 | 75 | 80      | 72       | LEADING
2    | Chứng khoán  | 71.2  | 70 | 78 | 68      | 65       | LEADING
3    | Bất động sản | 65.3  | 60 | 70 | 65      | 62       | IMPROVING
...
19   | Dầu khí      | 28.1  | 30 | 25 | 32      | 22       | LAGGING
```

---

# Global Parameters

## Editable Thresholds

| Parameter | Value | Location | Description |
|-----------|-------|----------|-------------|
| `OVERBOUGHT_THRESHOLD` | 80 | trading_constants.py | Breadth > 80% = caution |
| `OVERSOLD_THRESHOLD` | 20 | trading_constants.py | Breadth < 20% = opportunity |
| `TREND_CONFIRMATION_THRESHOLD` | 50 | trading_constants.py | MA50 & MA100 ≥ 50% = uptrend |
| `CAPITULATION_THRESHOLD` | 25 | trading_constants.py | All MA < 25% = panic |
| `ACCUMULATION_THRESHOLD` | 30 | trading_constants.py | All MA < 30% = smart money zone |
| `EARLY_REVERSAL_MA20_MIN` | 25 | trading_constants.py | MA20 ≥ 25% for early reversal |
| `STRONG_BUY_THRESHOLD` | 20 | trading_constants.py | MA20 < 20% in uptrend |
| `BUY_THRESHOLD` | 40 | trading_constants.py | MA20 < 40% in uptrend |
| `WARNING_THRESHOLD` | 80 | trading_constants.py | MA20 > 80% in uptrend |
| `SELL_THRESHOLD` | 70 | trading_constants.py | MA20 > 70% in downtrend |
| `DANGER_MA50_THRESHOLD` | 30 | trading_constants.py | MA50 < 30% + MA20 < 20% |
| `MA20_HIGHER_LOW_WINDOW` | 7 | trading_constants.py | Days for MA20 higher low |
| `MA50_HIGHER_LOW_WINDOW` | 9 | trading_constants.py | Days for MA50 higher low |

## Market Score Weights

| Component | Weight | Editable in |
|-----------|--------|-------------|
| MA50 | 0.5 | `MARKET_SCORE_WEIGHTS['ma50']` |
| MA20 | 0.3 | `MARKET_SCORE_WEIGHTS['ma20']` |
| MA100 | 0.2 | `MARKET_SCORE_WEIGHTS['ma100']` |

---

# Color Reference

## Regime Colors

| Regime | Text | Background |
|--------|------|------------|
| BULLISH | #10B981 | rgba(16, 185, 129, 0.15) |
| BEARISH | #EF4444 | rgba(239, 68, 68, 0.15) |
| NEUTRAL | #F59E0B | rgba(245, 158, 11, 0.15) |

## Signal Colors

| Signal | Color | Background |
|--------|-------|------------|
| STRONG_BUY | #059669 | rgba(5, 150, 105, 0.15) |
| BUY | #10B981 | rgba(16, 185, 129, 0.15) |
| HOLD | #3B82F6 | rgba(59, 130, 246, 0.15) |
| WARNING | #F59E0B | rgba(245, 158, 11, 0.15) |
| SELL | #DC2626 | rgba(220, 38, 38, 0.15) |
| DANGER | #7F1D1D | rgba(127, 29, 29, 0.2) |
| WAIT | #64748B | rgba(100, 116, 139, 0.15) |
| ACCUMULATING | #6366F1 | rgba(99, 102, 241, 0.15) |
| EARLY_BUY | #22D3EE | rgba(34, 211, 238, 0.15) |

## Breadth Chart Colors

| Line | Color | Role |
|------|-------|------|
| MA20 | #8B5CF6 (Purple) | Short-term |
| MA50 | #06B6D4 (Cyan) | Medium-term |
| MA100 | #F59E0B (Amber) | Long-term |

## RRG Quadrant Colors

| Quadrant | Color |
|----------|-------|
| LEADING | #10B981 (Green) |
| WEAKENING | #F59E0B (Amber) |
| LAGGING | #EF4444 (Red) |
| IMPROVING | #06B6D4 (Cyan) |

---

# File Locations

## UI Components

| File | Content |
|------|---------|
| `WEBAPP/core/trading_constants.py` | Numeric thresholds, windows, weights |
| `WEBAPP/core/trading_rules.py` | Signal definitions, colors, patterns |
| `WEBAPP/pages/technical/services/ta_dashboard_service.py` | Service logic |
| `WEBAPP/pages/technical/components/market_overview.py` | Tab 1 UI |
| `WEBAPP/pages/technical/components/sector_rotation.py` | Tab 2 UI |
| `WEBAPP/pages/technical/components/stock_scanner.py` | Tab 3 UI |

## Calculators/Processors

| File | Content |
|------|---------|
| `PROCESSORS/technical/indicators/rs_rating.py` | RS Rating calculator |
| `PROCESSORS/technical/indicators/rrg_calculator.py` | RRG sector rotation |
| `PROCESSORS/technical/indicators/money_flow.py` | Individual stock money flow |
| `PROCESSORS/technical/indicators/sector_money_flow.py` | Sector money flow aggregation |
| `PROCESSORS/technical/indicators/sector_ranking_calculator.py` | Composite sector ranking |
| `PROCESSORS/technical/indicators/sector_breadth.py` | Sector breadth analysis |
| `PROCESSORS/technical/indicators/technical_processor.py` | Technical indicators (SMA, EMA, RSI, MACD) |
| `PROCESSORS/technical/indicators/alert_detector.py` | Pattern & breakout detection |

## Data Files

| File | Content |
|------|---------|
| `DATA/processed/technical/basic_data.parquet` | OHLCV + technical indicators |
| `DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet` | RS Rating by stock |
| `DATA/processed/technical/sector/rrg_latest.parquet` | RRG coordinates by sector |
| `DATA/processed/technical/sector/ranking_latest.parquet` | Sector rankings |
| `DATA/processed/technical/money_flow/individual_money_flow.parquet` | Stock money flow indicators |
| `DATA/processed/technical/money_flow/sector_money_flow_1d.parquet` | Daily sector money flow |
| `DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet` | Sector breadth data |

---

# Backtest Methodology

**Period:** 2023-01-01 to 2025-12-31 (3 years, 699 trading days)
**Universe:** VN30 + BSC Coverage (92 stocks)
**Strategy:** Swing Trading (4-8 week holding period)

**Key Findings:**
1. Breadth > 80% preceded corrections in 73% of cases
2. MA20 median cycle: 14.5 days → 7-day window
3. MA50 median cycle: 19.0 days → 9-day window
4. Bottom reversal success rate with higher low confirmation: 81%

---

**End of Trading Logic Reference**
