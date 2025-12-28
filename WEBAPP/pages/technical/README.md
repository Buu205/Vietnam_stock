# Technical Analysis Module - Documentation

**Version:** 2.0.0
**Last Updated:** 2025-12-27
**Author:** Claude Code

---

## Table of Contents

1. [Overview](#1-overview)
2. [Module Structure](#2-module-structure)
3. [Technical Indicators](#3-technical-indicators)
4. [Alert Detection System](#4-alert-detection-system)
5. [Market Analysis](#5-market-analysis)
6. [Sector Analysis](#6-sector-analysis)
7. [Money Flow Analysis](#7-money-flow-analysis)
8. [RS Rating (IBD-style)](#8-rs-rating-ibd-style)
9. [Scoring & Reliability System](#9-scoring--reliability-system)
10. [Data Pipeline](#10-data-pipeline)
11. [Configuration & Customization](#11-configuration--customization)

---

## 1. Overview

The Technical Analysis module provides comprehensive market analysis using TA-Lib for high-performance indicator calculations. It supports:

- **458 symbols** from Vietnam stock market
- **19 industry sectors** classification
- **Real-time signal detection** with multi-factor confirmation
- **IBD-style RS Rating** for relative strength analysis

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| TechnicalProcessor | `PROCESSORS/technical/indicators/technical_processor.py` | Core TA indicators |
| AlertDetector | `PROCESSORS/technical/indicators/alert_detector.py` | Signal detection |
| MarketRegimeDetector | `PROCESSORS/technical/indicators/market_regime.py` | Market regime analysis |
| SectorBreadthAnalyzer | `PROCESSORS/technical/indicators/sector_breadth.py` | Sector strength |
| MoneyFlowAnalyzer | `PROCESSORS/technical/indicators/money_flow.py` | Fund flow tracking |
| RSRatingCalculator | `PROCESSORS/technical/indicators/rs_rating.py` | IBD-style RS Rating |
| TADashboardService | `WEBAPP/pages/technical/services/ta_dashboard_service.py` | UI data service |

---

## 2. Module Structure

```
WEBAPP/pages/technical/
├── README.md                     # This documentation
├── __init__.py
├── technical_dashboard.py        # Main dashboard page
├── components/
│   ├── __init__.py
│   ├── market_overview.py        # Tab 1: Market Overview
│   ├── sector_rotation.py        # Tab 2: Sector Rotation (RRG)
│   ├── stock_scanner.py          # Tab 3: Stock Scanner
│   └── ta_filter_bar.py          # Filter components
└── services/
    ├── __init__.py
    └── ta_dashboard_service.py   # Data service layer

PROCESSORS/technical/
├── indicators/
│   ├── technical_processor.py    # Core TA-Lib indicators
│   ├── alert_detector.py         # Signal detection
│   ├── market_regime.py          # Regime detection
│   ├── sector_breadth.py         # Sector analysis
│   ├── money_flow.py             # Volume-based indicators
│   ├── rs_rating.py              # IBD RS Rating
│   ├── vnindex_analyzer.py       # VN-Index analysis
│   └── sector_money_flow.py      # Sector fund flow
└── ohlcv/
    └── ohlcv_daily_updater.py    # OHLCV data management
```

---

## 3. Technical Indicators

### 3.1 Moving Averages

| Indicator | Period | Formula | Use Case |
|-----------|--------|---------|----------|
| SMA_20 | 20 days | `SMA(close, 20)` | Short-term trend |
| SMA_50 | 50 days | `SMA(close, 50)` | Medium-term trend |
| SMA_100 | 100 days | `SMA(close, 100)` | Long-term trend |
| SMA_200 | 200 days | `SMA(close, 200)` | Very long-term trend |
| EMA_20 | 20 days | `EMA(close, 20)` | Responsive short-term |
| EMA_50 | 50 days | `EMA(close, 50)` | Responsive medium-term |

**Price vs MA Calculation:**
```python
price_vs_sma20 = ((close - sma_20) / sma_20) * 100  # % above/below MA20
price_vs_sma50 = ((close - sma_50) / sma_50) * 100  # % above/below MA50
price_vs_sma200 = ((close - sma_200) / sma_200) * 100
```

### 3.2 Momentum Indicators

| Indicator | Parameters | Formula | Interpretation |
|-----------|------------|---------|----------------|
| RSI_14 | period=14 | `talib.RSI(close, 14)` | <30 oversold, >70 overbought |
| MACD | 12/26/9 | `talib.MACD(close, 12, 26, 9)` | Signal crossover |
| Stochastic | 14/3/3 | `talib.STOCH(high, low, close, 14, 3, 3)` | Overbought/Oversold |

**MACD Components:**
```python
macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
# macd = EMA(12) - EMA(26)
# macd_signal = EMA(macd, 9)
# macd_hist = macd - macd_signal
```

### 3.3 Volatility Indicators

| Indicator | Parameters | Formula | Use Case |
|-----------|------------|---------|----------|
| Bollinger Bands | 20/2 | `talib.BBANDS(close, 20, 2, 2)` | Volatility range |
| ATR_14 | period=14 | `talib.ATR(high, low, close, 14)` | Volatility measure |
| BB_Width | - | `(upperband - lowerband) / middleband * 100` | Squeeze detection |

### 3.4 Volume Indicators

| Indicator | Formula | Interpretation |
|-----------|---------|----------------|
| OBV | `talib.OBV(close, volume)` | Cumulative volume flow |
| AD Line | `talib.AD(high, low, close, volume)` | Accumulation/Distribution |
| CMF_20 | `talib.ADOSC(high, low, close, volume, 3, 10)` | Money flow pressure |
| MFI_14 | `talib.MFI(high, low, close, volume, 14)` | Volume-weighted RSI |

### 3.5 Trend Indicators

| Indicator | Parameters | Formula | Interpretation |
|-----------|------------|---------|----------------|
| ADX_14 | period=14 | `talib.ADX(high, low, close, 14)` | Trend strength (>25 trending) |
| CCI_20 | period=20 | `talib.CCI(high, low, close, 20)` | Momentum oscillator |

---

## 4. Alert Detection System

### 4.1 MA Crossover Detection

**Logic:**
```python
# Cross Above (Bullish)
if prev_close < prev_ma AND curr_close > curr_ma:
    signal = 'BULLISH'
    alert_type = 'MA_CROSS_ABOVE'

# Cross Below (Bearish)
if prev_close > prev_ma AND curr_close < curr_ma:
    signal = 'BEARISH'
    alert_type = 'MA_CROSS_BELOW'
```

**MA Periods Checked:** 20, 50, 100, 200

### 4.2 Smart Volume Spike Detection

**Multi-factor Confirmation System:**

| Factor | Condition | Points |
|--------|-----------|--------|
| Volume Spike | volume > avg_volume_20d × 1.5 | Required |
| Breakout | price > 20-day high | +1 |
| RSI Healthy | 40 <= RSI <= 70 | +1 |
| RSI Oversold | RSI < 30 | +1 |
| MACD Bullish | MACD > MACD Signal | +1 |
| Candlestick Pattern | Bullish pattern detected | +1 |

**Signal Classification:**

| Confirmations | Signal | Confidence |
|---------------|--------|------------|
| >= 3 + Breakout + MACD | STRONG_BUY | 0.85 |
| >= 3 + Price Up | BUY | 0.70 |
| >= 3 + Price Down | DISTRIBUTION | 0.65 |
| >= 2 | WATCH | 0.50 |
| < 2 | NOISE | 0.30 |

### 4.3 Breakout Detection

```python
resistance_20 = max(high[-21:-1])  # 20-day high (excluding current)
support_20 = min(low[-21:-1])      # 20-day low (excluding current)
volume_confirmed = current_volume > avg_volume × 1.5

# Breakout Up
if close > resistance_20 AND volume_confirmed:
    signal = 'BULLISH_BREAKOUT'

# Breakdown
if close < support_20 AND volume_confirmed:
    signal = 'BEARISH_BREAKDOWN'
```

### 4.4 Candlestick Pattern Detection (3-Metric System)

**Hệ thống scoring mới với 3 metrics riêng biệt:**

| Metric | Range | Description |
|--------|-------|-------------|
| `win_rate` | 50-60% | Historical win rate từ backtest research |
| `context_score` | 0-100 | Context confirmation score (dynamic) |
| `composite_score` | -100 to +100 | Weighted score for sorting |

---

#### Metric 1: Historical Win Rate (Fixed per Pattern)

**Data Sources:**
- [Quantified Strategies](https://www.quantifiedstrategies.com/the-complete-backtest-of-all-75-candlestick-patterns/) - 75 patterns on S&P 500
- [Liberated Stock Trader](https://www.liberatedstocktrader.com/candle-patterns-reliable-profitable/) - 56,680 trades on Dow Jones

| Pattern | Win Rate | Signal | Notes |
|---------|----------|--------|-------|
| Inverted Hammer | **60%** | BULLISH | Highest individual win rate |
| Three Black Crows | 58% | BEARISH | 3-candle reversal |
| Morning Star | 58% | BULLISH | 3-candle reversal |
| Engulfing | 57% | BOTH | Well-documented |
| Evening Star | 57% | BEARISH | Mirror of morning star |
| Gravestone Doji | 57% | BEARISH | Strong bearish signal |
| Three White Soldiers | 56% | BULLISH | Strong but rare |
| Hammer | 55% | BULLISH | Moderate reliability |
| Shooting Star | 55% | BEARISH | Moderate reliability |
| Hanging Man | 52% | BEARISH | Needs confirmation |
| Doji | **50%** | NEUTRAL | Coin flip - indecision |

---

#### Metric 2: Context Confirmation Score (Dynamic, 0-100)

**4 Factors (25 points each):**

| Factor | Condition | Points |
|--------|-----------|--------|
| **Volume** | Vol ≥ 2.5x avg | 25 |
| | Vol ≥ 2.0x | 20 |
| | Vol ≥ 1.5x | 15 |
| | Vol ≥ 1.0x | 5 |
| **RSI Alignment** | Bullish + RSI<30 (Oversold) | 25 |
| | Bearish + RSI>70 (Overbought) | 25 |
| | Aligned 40-60 range | 5-15 |
| **Trend** | P > EMA20 > EMA50 (Bullish) | 25 |
| | P < EMA20 < EMA50 (Bearish) | 25 |
| | Above/Below EMA20 only | 15 |
| **S/R Proximity** | Near support (Bullish) < 15% | 25 |
| | Near resistance (Bearish) < 15% | 25 |
| | Close to S/R < 30% | 15 |

**Context Details Output:**
```
Vol x2.1 (Strong) | RSI 72 (Overbought) | Downtrend (P<EMA20<EMA50) | Near resistance (8%)
```

---

#### Metric 3: Composite Score (For Sorting, -100 to +100)

**Formula:**
```python
weighted_score = (win_rate × 0.4) + (context_score × 0.6)
composite_score = direction × weighted_score

# Bullish → positive, Bearish → negative
```

**Example: KSB - Three Black Crows (BEARISH)**
```
win_rate = 58%
context_score = 75 (Vol x2.1, RSI=72, Downtrend, Near resistance)
weighted = (58 × 0.4) + (75 × 0.6) = 23.2 + 45 = 68.2
composite = -68 (Bearish direction)
```

**Score Interpretation:**

| Score Range | Signal | Meaning |
|-------------|--------|---------|
| > +60 | STRONG_BUY | High win rate + strong context |
| +30 to +60 | BUY | Moderate bullish signal |
| -30 to +30 | NEUTRAL | Low confidence either way |
| -60 to -30 | SELL | Moderate bearish signal |
| < -60 | STRONG_SELL | High win rate + strong context |

---

#### Data Schema (patterns_latest.parquet)

```python
{
    'symbol': str,
    'date': date,
    'pattern_name': str,
    'signal': str,           # BULLISH/BEARISH
    'win_rate': int,         # 50-60 (%)
    'context_score': int,    # 0-100
    'context_details': str,  # "Vol x2.1 | RSI 72 | ..."
    'composite_score': int,  # -100 to +100
    'strength': int,         # Legacy: abs(composite_score)
    'price': float
}
```

> **Note:** `strength` field kept for backward compatibility với UI hiện tại.

### 4.5 Combined Signal Scoring

**Scoring System (Total: -100 to +100):**

| Component | Weight | Bullish | Bearish |
|-----------|--------|---------|---------|
| MA Trend | 40 pts | Price > SMA20 > SMA50 | Price < SMA20 < SMA50 |
| RSI | 30 pts | 40-60: +30, <30: +20 | >70: -20 |
| MACD | 30 pts | MACD > Signal | MACD < Signal |

**Signal Classification:**

| Score | Signal | Confidence |
|-------|--------|------------|
| >= 70 | STRONG_BUY | 0.85 |
| >= 40 | BUY | 0.65 |
| <= -70 | STRONG_SELL | 0.85 |
| <= -40 | SELL | 0.65 |
| -40 to +40 | HOLD | 0.50 |

---

## 5. Market Analysis

### 5.1 Market Regime Detection

**Multi-Factor Scoring (Total: -100 to +100):**

| Factor | Weight | Range | Source |
|--------|--------|-------|--------|
| Valuation | 25% | -80 to +80 | VN-Index PE percentile |
| Breadth | 25% | -100 to +100 | % above MA50/200 |
| Volume | 15% | -50 to +50 | Current vs 20-day avg |
| Volatility | 15% | -100 to +100 | ATR z-score |
| Momentum | 20% | -100 to +100 | MACD + RSI distribution |

**Regime Classification:**

| Score Range | Regime | Description |
|-------------|--------|-------------|
| >= 60 | BUBBLE | Extreme optimism, high risk |
| 30 to 59 | EUPHORIA | Strong bullish, caution advised |
| -29 to 29 | NEUTRAL | Normal market conditions |
| -59 to -30 | FEAR | Bearish sentiment |
| <= -60 | BOTTOM | Extreme pessimism, potential opportunity |

**Valuation Score (PE Percentile):**
```python
# PE percentile in last 252 sessions
if percentile >= 90: score = -80  # Very expensive
if percentile >= 75: score = -50  # Expensive
if percentile >= 60: score = -20  # Slightly expensive
if percentile >= 40: score = 0    # Fair value
if percentile >= 25: score = 20   # Cheap
if percentile >= 10: score = 50   # Very cheap
else: score = 80                  # Extremely cheap
```

**Breadth Score:**
```python
pct_above_ma50 = (above_ma50 / total_stocks) * 100
pct_above_ma200 = (above_ma200 / total_stocks) * 100

breadth_score = (pct_above_ma50 - 50) * 1.5 + (pct_above_ma200 - 50) * 0.5
# Range: -100 to +100
```

**Momentum Score:**
```python
pct_bullish_macd = (bullish_macd / total_stocks) * 100
pct_bullish_rsi = (rsi_50_to_70 / total_stocks) * 100

momentum_score = (pct_bullish_macd - 50) * 1.2 + (pct_bullish_rsi - 50) * 0.8
```

### 5.2 Risk Level Assessment

| Regime Score | Volatility Score | Risk Level |
|--------------|------------------|------------|
| > 50 | < -30 | VERY_HIGH |
| > 30 OR volatility < -30 | - | HIGH |
| -30 to 30 | - | MEDIUM |
| < -50 | > 20 | LOW |

---

## 6. Sector Analysis

### 6.1 Sector Breadth Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| pct_above_ma20 | `(above_ma20 / total) × 100` | Short-term strength |
| pct_above_ma50 | `(above_ma50 / total) × 100` | Medium-term strength |
| pct_above_ma100 | `(above_ma100 / total) × 100` | Long-term strength |
| pct_above_ma200 | `(above_ma200 / total) × 100` | Very long-term strength |
| ad_ratio | `advancing / declining` | Advance/Decline ratio |

### 6.2 Sector Strength Score

```python
strength_score = (
    pct_above_ma20 × 0.20 +
    pct_above_ma50 × 0.30 +
    pct_above_ma100 × 0.25 +
    pct_above_ma200 × 0.25
)
# Range: 0 to 100
```

### 6.3 Sector Trend Classification

| pct_above_ma50 | Trend |
|----------------|-------|
| >= 70% | STRONG_BULLISH |
| >= 55% | BULLISH |
| 45% - 54% | NEUTRAL |
| 30% - 44% | BEARISH |
| < 30% | STRONG_BEARISH |

---

## 7. Money Flow Analysis

### 7.1 Indicators

| Indicator | TA-Lib Function | Interpretation |
|-----------|-----------------|----------------|
| CMF_20 | `ADOSC(high, low, close, volume, 3, 10)` | +0.10 = strong buying |
| MFI_14 | `MFI(high, low, close, volume, 14)` | >70 overbought, <30 oversold |
| OBV | `OBV(close, volume)` | Trend confirmation |
| AD Line | `AD(high, low, close, volume)` | Accumulation/Distribution |
| VPT | Custom | Volume Price Trend |

### 7.2 VPT (Volume Price Trend) Formula

```python
VPT[0] = 0
VPT[i] = VPT[i-1] + volume[i] × (close[i] - close[i-1]) / close[i-1]
```

### 7.3 Money Flow Classification

| CMF | MFI | OBV vs 20-day MA | Signal |
|-----|-----|------------------|--------|
| > 0.10 | - | > 1.05× | STRONG_ACCUMULATION |
| > 0.05 | < 30 | > avg | ACCUMULATION |
| < -0.10 | - | < 0.95× | STRONG_DISTRIBUTION |
| < -0.05 | > 70 | < avg | DISTRIBUTION |
| else | - | - | NEUTRAL |

---

## 8. RS Rating (IBD-style)

### 8.1 Formula

```python
# Return periods (trading days)
PERIOD_3M = 63   # 3 months
PERIOD_6M = 126  # 6 months
PERIOD_9M = 189  # 9 months
PERIOD_12M = 252 # 12 months

# Weights (IBD-style: recent performance weighted more)
WEIGHTS = {
    '3m': 0.4,  # 40% weight
    '6m': 0.2,  # 20% weight
    '9m': 0.2,  # 20% weight
    '12m': 0.2  # 20% weight
}

# RS Score calculation
rs_score = (
    0.4 × ret_3m +
    0.2 × ret_6m +
    0.2 × ret_9m +
    0.2 × ret_12m
)

# RS Rating = Percentile rank (1-99)
rs_rating = percentile_rank(rs_score) × 98 + 1
```

### 8.2 Interpretation

| RS Rating | Interpretation |
|-----------|----------------|
| 90-99 | Market leader, top 10% |
| 80-89 | Strong performer, top 20% |
| 70-79 | Above average |
| 50-69 | Average |
| 30-49 | Below average |
| 1-29 | Market laggard |

---

## 9. Scoring & Reliability System

### 9.1 Pattern Strength Score Components

```
Final Score = Base Score + Volume Bonus + RSI Bonus
            (30-85)        (+5 to +15)   (+5 to +10)

Maximum: 100
```

### 9.2 Combined Signal Scoring

```
MA Trend:     ±40 points
RSI Zone:     -20 to +30 points
MACD Cross:   ±30 points
───────────────────────────
Total Range:  -100 to +100
```

### 9.3 Market Regime Scoring

```
Valuation:    25% × (-80 to +80)
Breadth:      25% × (-100 to +100)
Volume:       15% × (-50 to +50)
Volatility:   15% × (-100 to +100)
Momentum:     20% × (-100 to +100)
─────────────────────────────────
Total Range:  -100 to +100
```

---

## 10. Data Pipeline

### 10.1 Daily Update Pipeline

**Command:**
```bash
python3 PROCESSORS/pipelines/daily/daily_ta_complete.py
```

**Pipeline Steps:**
1. VN-Index Analysis (500 sessions)
2. Technical Indicators (200 sessions)
3. Alert Detection (MA, Volume, Breakout, Patterns)
4. Money Flow Calculation
5. Sector Money Flow (1D, 1W, 1M)
6. Market Breadth
7. Sector Breadth
8. Market Regime Detection
9. RS Rating Calculation

### 10.2 Output Files

| File | Path | Description |
|------|------|-------------|
| basic_data.parquet | `DATA/processed/technical/` | All TA indicators |
| patterns_latest.parquet | `DATA/processed/technical/alerts/daily/` | Candlestick patterns |
| ma_crossover_latest.parquet | `DATA/processed/technical/alerts/daily/` | MA crossovers |
| volume_spike_latest.parquet | `DATA/processed/technical/alerts/daily/` | Volume spikes |
| breakout_latest.parquet | `DATA/processed/technical/alerts/daily/` | Breakouts |
| market_breadth_daily.parquet | `DATA/processed/technical/market_breadth/` | Market breadth |
| sector_breadth_daily.parquet | `DATA/processed/technical/sector_breadth/` | Sector breadth |
| market_regime_history.parquet | `DATA/processed/technical/market_regime/` | Regime history |
| stock_rs_rating_daily.parquet | `DATA/processed/technical/rs_rating/` | RS Rating |

---

## 11. Configuration & Customization

### 11.1 Pattern Base Scores

To modify pattern reliability scores, edit `alert_detector.py`:

```python
PATTERN_BASE_SCORES = {
    'three_white_soldiers': 85,
    'three_black_crows': 85,
    'morning_star': 80,
    'evening_star': 80,
    'engulfing': 75,
    'hammer': 70,
    'shooting_star': 70,
    'inverted_hammer': 55,
    'hanging_man': 55,
    'doji': 30,  # Adjust as needed
}
```

### 11.2 Regime Detection Weights

To modify regime factor weights, edit `market_regime.py`:

```python
regime_score = (
    valuation_score * 0.25 +   # Adjust weight
    breadth_score * 0.25 +
    volume_score * 0.15 +
    volatility_score * 0.15 +
    momentum_score * 0.20
)
```

### 11.3 RS Rating Weights

To modify return period weights, edit `rs_rating.py`:

```python
WEIGHTS = {
    '3m': 0.4,   # Most recent
    '6m': 0.2,
    '9m': 0.2,
    '12m': 0.2   # Oldest
}
```

### 11.4 Sector Strength Weights

To modify sector strength formula, edit `sector_breadth.py`:

```python
strength_score = (
    pct_above_ma20 * 0.20 +   # Short-term
    pct_above_ma50 * 0.30 +   # Medium-term (highest weight)
    pct_above_ma100 * 0.25 +
    pct_above_ma200 * 0.25    # Long-term
)
```

---

## Appendix: Vietnamese Pattern Interpretations

| Pattern | Vietnamese Interpretation |
|---------|---------------------------|
| Morning Star | Mô hình 3 nến đảo chiều hoàn hảo: (1) Nến đỏ dài, (2) Doji, (3) Nến xanh dài. High conviction. |
| Hammer | Từ chối giảm giá - Bấc dưới dài >= 2x thân. Buyers vào ở đáy. |
| Engulfing | Đảo chiều mạnh - Nến xanh bao trùm hoàn toàn nến đỏ trước. |
| Three White Soldiers | 3 nến xanh liên tiếp tăng dần - Đảo chiều tăng cực mạnh. |
| Evening Star | Mô hình 3 nến đảo chiều giảm: (1) Nến xanh, (2) Doji, (3) Nến đỏ dài. |
| Shooting Star | Từ chối tăng giá - Bấc trên dài, thân nhỏ ở dưới. Sellers vào. |
| Hanging Man | Cảnh báo đảo chiều giảm sau uptrend. Giống Hammer nhưng ở đỉnh. |
| Doji | Thị trường bất định - Open = Close. Chờ nến tiếp theo xác nhận. |

---

*Documentation generated by Claude Code - 2025-12-27*
