# Technical Dashboard - Trading Logic Reference

**Single Source of Truth for Trading Parameters & Logic**
**Last Updated:** 2026-01-04

---

## Quick Navigation

1. [Tab 1: Market Overview](#tab-1-market-overview)
2. [Tab 2: Sector Rotation](#tab-2-sector-rotation)
3. [Tab 3: Stock Scanner](#tab-3-stock-scanner)
4. [Global Parameters](#global-parameters)
5. [Color Reference](#color-reference)

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

## 2.1 RRG (Relative Rotation Graph)

**Purpose:** Identify leading vs lagging sectors

**Dimensions:**
- X-axis: RS Ratio (strength vs market average)
- Y-axis: RS Momentum (rate of change)

---

## 2.2 RS Calculation

| Step | Formula |
|------|---------|
| 1. Sector Strength | (EMA12 - EMA26) / EMA26 × 100 |
| 2. RS Ratio | sector_strength / market_avg_strength |
| 3. RS Momentum | RS Ratio change over 5 days × 100 |
| 4. Smoothing | SMA(3) applied to both |

---

## 2.3 Quadrant Rules

| Quadrant | RS Ratio | RS Momentum | Action |
|----------|----------|-------------|--------|
| **LEADING** | > 1.0 | > 0 | BUY - Best performers |
| **WEAKENING** | > 1.0 | ≤ 0 | WATCH - Strength fading |
| **LAGGING** | ≤ 1.0 | ≤ 0 | AVOID - Worst performers |
| **IMPROVING** | ≤ 1.0 | > 0 | ACCUMULATE - Potential turnaround |

**Rotation Direction:** IMPROVING → LEADING → WEAKENING → LAGGING → IMPROVING

---

## 2.4 Watchlists

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

| File | Content |
|------|---------|
| `WEBAPP/core/trading_constants.py` | Numeric thresholds, windows, weights |
| `WEBAPP/core/trading_rules.py` | Signal definitions, colors, patterns |
| `WEBAPP/pages/technical/services/ta_dashboard_service.py` | Service logic |
| `WEBAPP/pages/technical/components/market_overview.py` | Tab 1 UI |
| `WEBAPP/pages/technical/components/sector_rotation.py` | Tab 2 UI |
| `WEBAPP/pages/technical/components/stock_scanner.py` | Tab 3 UI |

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
