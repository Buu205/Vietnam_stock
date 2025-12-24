# Brainstorm: Technical Analysis Evaluation System
**Date:** 2025-12-23
**Status:** ✅ Backtest Completed
**Scope:** Market → Sector → Stock → Buy/Sell Lists → Signals → Position Sizing → Rotation

---

## 0. Backtest Results Summary (VALIDATED)

| Strategy | Win Rate | Avg PnL | Profit Factor |
|----------|----------|---------|---------------|
| **EMA 9/21 (Midcap+)** | 41.7% | +8.91% | **4.54** ✅ |
| Breakout + Volume | 53.4% | +4.28% | - |
| VSA Stopping Volume | 54.3% | +0.67% | - |
| Variable Exposure | - | Sharpe 0.94 | -47% DD vs B&H |

**Winner:** EMA 9/21 với market cap filter >= 5,000 tỷ VND
**Full results:** [BACKTEST_RESULTS.md](../251223-ta-backtest-experiments/BACKTEST_RESULTS.md)

---

## 1. Problem Statement

Xây dựng **bảng đánh giá kỹ thuật toàn diện** cho thị trường VN với 3 tầng:
1. **MARKET** (Vĩ mô) - Breadth, EMA trend, Exposure control
2. **SECTOR** (Ngành) - Rotation, Money Flow, Relative Strength
3. **STOCK** (Cổ phiếu) - EMA cross, Volume confirm, VSA patterns

---

## 2. Current Data Inventory (Đã Có)

### ✅ Sẵn Có - Tốt
| Data | Location | Columns Key |
|------|----------|-------------|
| Market Breadth | `market_breadth_daily.parquet` | above_ma20_pct, above_ma50_pct, ad_ratio |
| Market Regime | `market_regime_history.parquet` | regime, regime_score, risk_level |
| Sector Breadth | `sector_breadth_daily.parquet` | 19 ngành × strength_score |
| Sector Scores | `sector_combined_scores.parquet` | FA + TA → signal (BUY/SELL/HOLD) |
| Money Flow | `individual_money_flow.parquet` | cmf_20, mfi_14, obv |
| Sector Money Flow | `sector_money_flow_1d.parquet` | flow_signal, top_contributors |
| Technical Alerts | `combined_latest.parquet` | MA cross, Breakout, Volume spike |
| Candlestick Patterns | `patterns_latest.parquet` | doji, engulfing, hammer... |
| Basic TA | `basic_data.parquet` | RSI, MACD, Stoch, BB, ATR, ADX, CCI |

### ❌ Chưa Có - Cần Bổ Sung
| Indicator | Priority | Complexity | Use Case |
|-----------|----------|------------|----------|
| **Connors RSI (CRSI)** | 🔴 HIGH | Medium | Mean Reversion Entry |
| **McClellan Oscillator** | 🔴 HIGH | Medium | Market Timing |
| **TRIN (Arms Index)** | 🟡 MEDIUM | Low | Panic Detection |
| **RVOL** | 🔴 HIGH | Low | Volume Confirmation |
| **VSA Signals** | 🟡 MEDIUM | Medium | Smart Money Detection |
| **Sector Rotation Matrix** | 🔴 HIGH | Medium | Rotation Strategy |
| **Fear/Greed Index** | 🟡 MEDIUM | Medium | Sentiment |

---

## 3. Proposed Architecture

### 3.1 Three-Layer Dashboard Structure

```
┌─────────────────────────────────────────────────────────┐
│                    MARKET LAYER                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐    │
│  │ Breadth     │ │ Regime      │ │ Fear/Greed      │    │
│  │ Gauge       │ │ Light       │ │ Index           │    │
│  │ (MA20/50%)  │ │ (🟢🟡🔴)    │ │ (0-100)         │    │
│  └─────────────┘ └─────────────┘ └─────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │ McClellan Oscillator + Breadth Divergence       │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    SECTOR LAYER                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Sector Rotation Matrix (RRG-style)              │    │
│  │ X: Relative Strength | Y: Momentum              │    │
│  │ Quadrants: Leading/Weakening/Lagging/Improving  │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐    │
│  │ Money Flow  │ │ Sector      │ │ Top Sectors     │    │
│  │ Heatmap     │ │ Breadth     │ │ (by Signal)     │    │
│  └─────────────┘ └─────────────┘ └─────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    STOCK LAYER                          │
│  ┌───────────────────────┐ ┌───────────────────────┐    │
│  │ BUY LIST              │ │ SELL LIST             │    │
│  │ - CRSI < 10           │ │ - CRSI > 90           │    │
│  │ - Above MA200         │ │ - Breaking support    │    │
│  │ - Volume confirmation │ │ - No Demand           │    │
│  │ - Position Size       │ │ - Distribution        │    │
│  └───────────────────────┘ └───────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Signal Scanner (Breakout/Reversal/VSA)          │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Key Output Tables

#### Table 1: Market Overview
| Metric | Value | Trend | Signal |
|--------|-------|-------|--------|
| VN-Index | 1,245 | ↑ | - |
| % > MA20 | 45% | ↓ | CAUTION |
| % > MA50 | 38% | ↓ | BEARISH |
| McClellan | -35 | ↓ | OVERSOLD |
| TRIN | 1.8 | ↑ | PANIC |
| Regime | CORRECTION | - | DEFENSIVE |

#### Table 2: Sector Rotation
| Sector | RS Score | Momentum | Quadrant | Money Flow | Action |
|--------|----------|----------|----------|------------|--------|
| Ngân hàng | 1.15 | ↑ | LEADING | +500B | OVERWEIGHT |
| BĐS | 0.85 | ↓ | LAGGING | -300B | UNDERWEIGHT |
| Chứng khoán | 0.95 | ↑ | IMPROVING | +200B | ACCUMULATE |

#### Table 3: Buy/Sell Lists
**BUY LIST (Top 10)**
| Ticker | Price | CRSI | Setup | ATR Size | Target |
|--------|-------|------|-------|----------|--------|
| ACB | 25,500 | 8 | Pullback | 500 cp | +8% |
| VNM | 72,000 | 12 | Stopping Vol | 200 cp | +6% |

**SELL LIST (Top 10)**
| Ticker | Price | CRSI | Pattern | Risk |
|--------|-------|------|---------|------|
| VIC | 45,000 | 92 | No Demand | HIGH |

---

## 4. Implementation Roadmap

### Phase 1: Missing Indicators (1-2 ngày)
**Priority: 🔴 HIGH**

```python
# CRSI Calculation
def connors_rsi(close, rsi_period=3, streak_period=2, pct_rank_period=100):
    rsi_price = ta.RSI(close, rsi_period)
    streak = calculate_up_down_streak(close)
    rsi_streak = ta.RSI(streak, streak_period)
    pct_rank = percent_rank(close.pct_change(), pct_rank_period)
    return (rsi_price + rsi_streak + pct_rank) / 3

# McClellan Oscillator
def mcclellan_oscillator(advances, declines):
    ratio_adj = (advances - declines) / (advances + declines) * 1000
    ema19 = ratio_adj.ewm(span=19).mean()
    ema39 = ratio_adj.ewm(span=39).mean()
    return ema19 - ema39

# RVOL (Relative Volume)
def rvol(volume, period=20):
    return volume / volume.rolling(period).mean()
```

**Files to modify:**
- `PROCESSORS/technical/indicators/technical_processor.py`
- Add: `connors_rsi`, `mcclellan`, `trin`, `rvol`

### Phase 2: VSA Signals (1 ngày)
**Priority: 🟡 MEDIUM**

```python
def stopping_volume(df):
    """High volume + narrow spread + close near high in downtrend"""
    cond1 = df['close'] < df['sma_20']  # Downtrend
    cond2 = df['volume'] > 1.5 * df['vol_sma20']  # High vol
    cond3 = (df['close'] - df['low']) / (df['high'] - df['low']) > 0.6
    return cond1 & cond2 & cond3

def no_demand(df):
    """Up candle + low volume in uptrend"""
    cond1 = df['close'] > df['open']  # Up candle
    cond2 = df['volume'] < df['vol_sma20']  # Low vol
    cond3 = df['volume'] < df['volume'].shift(1)
    return cond1 & cond2 & cond3
```

### Phase 3: Sector Rotation (1 ngày)
**Priority: 🔴 HIGH**

RRG (Relative Rotation Graph) style:
```python
def sector_rotation_quadrant(sector_df, benchmark='VNINDEX'):
    """Calculate RS and momentum for each sector"""
    # Relative Strength = sector_return / benchmark_return
    rs = sector_df['return_20d'] / benchmark['return_20d']

    # Momentum = change in RS
    momentum = rs.pct_change(5)  # 5-day momentum

    # Quadrant assignment
    # Leading: RS > 1, Momentum > 0
    # Weakening: RS > 1, Momentum < 0
    # Lagging: RS < 1, Momentum < 0
    # Improving: RS < 1, Momentum > 0
```

### Phase 4: Dashboard Integration (2-3 ngày)
**Priority: 🔴 HIGH**

New Streamlit pages:
1. `technical_market_overview.py` - Market Layer
2. `sector_rotation_dashboard.py` - Sector Layer
3. `stock_scanner.py` - Buy/Sell Lists

---

## 5. Decision Points (Cần Xác Nhận)

### Q1: CRSI Threshold
- **Option A:** CRSI < 10 (Conservative - ít tín hiệu, chất lượng cao)
- **Option B:** CRSI < 15 (Moderate - nhiều tín hiệu hơn)
- **Recommend:** Option A cho market đi ngang, Option B cho uptrend mạnh

### Q2: Position Sizing Method
- **Option A:** Fixed % (1% risk per trade)
- **Option B:** Kelly Criterion (optimal sizing)
- **Recommend:** Option A - đơn giản, kiểm soát được

### Q3: Sector Rotation Period
- **Option A:** Weekly rebalance
- **Option B:** Monthly rebalance
- **Recommend:** Option A - phù hợp với thị trường VN biến động

### Q4: Backtest Integration
- **Option A:** No backtest (focus on real-time signals)
- **Option B:** Simple backtest (win rate, profit factor)
- **Option C:** Full backtest engine (với vectorbt)
- **Recommend:** Option B first → Option C later

---

## 6. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data quality (OHLCV adjustment) | HIGH | Already have adjustment detector |
| Over-optimization | MEDIUM | Keep rules simple, fixed parameters |
| Latency (real-time) | LOW | Daily EOD data is sufficient |
| False signals | MEDIUM | Combine multiple confirmations |

---

## 7. Success Criteria

1. **Market timing accuracy:** Identify major tops/bottoms 3-5 sessions early
2. **Sector rotation:** Outperform VNINDEX by 10%+ annualized
3. **Stock picks:** Win rate > 55%, Profit factor > 1.5
4. **User experience:** Dashboard loads < 3 seconds

---

## 8. Validated Framework (Post-Backtest)

### MARKET LEVEL
```
EMA9 > EMA21 + % > MA20 >= 40% → Full exposure (70-100%)
EMA9 > EMA21 + % > MA20 < 40%  → Reduced (40-60%)
EMA9 < EMA21                    → Defensive (0-20%)
```

### STOCK LEVEL (EMA 9/21 Strategy)
```
Entry: EMA9 cross up EMA21 + RVOL >= 0.8 + Market cap >= 5,000 tỷ
Exit:  EMA9 cross down EMA21 OR Trailing stop 2x ATR
```

### Expected Performance (Backtest 2023-2025)
- Win rate: ~42%
- Avg PnL per trade: +9%
- Profit Factor: 4.5+
- Max Drawdown: -30% (vs -35% B&H)

---

## 9. Final Indicator Set (Minimal - 8 total)

| # | Indicator | Purpose | Validated |
|---|-----------|---------|-----------|
| 1 | EMA9/EMA21 | Trend + Entry/Exit | ✅ PF 4.54 |
| 2 | % > MA20 | Breadth/Exposure | ✅ -47% DD |
| 3 | RVOL | Volume confirmation | ✅ Filter false |
| 4 | Sector RS | Rotation | 🔄 To test |
| 5 | VSA Patterns | Smart money | ✅ 54% WR |
| 6 | ATR | Position sizing | ✅ Risk mgmt |
| 7 | Market Cap | Liquidity filter | ✅ Critical |
| 8 | Swing H/L | Breakout levels | ✅ 53% WR |

---

## 10. Next Steps

1. ✅ **Backtest validation** - DONE
2. 📝 **Create implementation plan** - `/plan:hard`
3. 🔧 **Add missing indicators** - RVOL, VSA to processors
4. 📊 **Build dashboard** - Market/Sector/Stock scanner
5. 🚀 **Deploy** - Daily signals generation

---

## 11. Unresolved Questions

1. **Sector RS backtest?** - Cần test thêm sector rotation
2. **Trailing stop optimization?** - 2x ATR hay dynamic?
3. **Real-time vs EOD?** - EOD đủ cho swing trading

---

## Summary

**Backtest validated** EMA 9/21 strategy với:
- Market cap filter >= 5,000 tỷ
- Volume confirmation (RVOL >= 0.8)
- Breadth-based exposure control

**Key insight:** Win rate 42% OK khi Profit Factor > 4 (winners lớn hơn losers).

**Files:**
- [BACKTEST_RESULTS.md](../251223-ta-backtest-experiments/BACKTEST_RESULTS.md)
- [backtest_runner.py](../251223-ta-backtest-experiments/backtest_runner.py)
- [ema_strategy_results.csv](../251223-ta-backtest-experiments/ema_strategy_results.csv)
