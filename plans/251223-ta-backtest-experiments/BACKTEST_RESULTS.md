# Comprehensive Backtest Results
**Date:** 2025-12-23
**Universe:** 151 stocks (Market cap >= 5,000 tỷ VND)
**Period:** 2022-01-04 to 2025-12-23

---

## Executive Summary

| Strategy | Signals | Win Rate | Avg PnL | Notes |
|----------|---------|----------|---------|-------|
| **EMA 9/21 Cross** | 2,273 | 33.4% | +2.47% | Best total return, PF 1.87 |
| **Breakout + Volume** | 6,863 | 50.9% | +1.21% | High frequency |
| **RSI<40 + EMA Bull** | 2,807 | 51.2% | +0.49% | Pullback buy |
| **EMA+RSI+Vol Combo** | 224 | 50.0% | +0.70% | Quality filter |
| **Exposure Control** | - | - | Sharpe 0.82 | -58% DD reduction |

---

## Test 1: EMA 9/21 Cross Strategy

### Setup
- Entry: EMA9 cross up EMA21 + RVOL >= 0.8
- Exit: EMA9 cross down EMA21
- Universe: Midcap+ (mcap >= 5,000 tỷ)

### Results
```
Total trades:    2,273
Win rate:        33.4%
Avg PnL:         +2.47%
Median PnL:      -1.99%
Total return:    +5,621%
Profit Factor:   1.87
Avg holding:     37 days
```

### Analysis
- Win rate thấp (33%) nhưng **winners lớn hơn losers** (PF 1.87)
- Chiến lược **trend following** - lợi nhuận đến từ vài trades lớn
- Phù hợp swing trading VN (hold ~5 tuần)

---

## Test 2: Breakout + Volume

### Setup
- Entry: Close > 10-bar swing high + RVOL > 1.3
- Exit: Fixed 5-day hoặc 10-day hold

### Results
```
Total signals:   6,863
5-day hold:      WR 49.3% | Avg +0.68%
10-day hold:     WR 50.9% | Avg +1.21%
```

### Analysis
- **Tần suất cao** - nhiều cơ hội trading
- Win rate ~51% với avg +1.21% → **Edge dương**
- Volume confirmation quan trọng (>1.3x)

---

## Test 3: RSI Oversold + EMA Bullish

### Setup
- Signal: RSI < 40 trong uptrend (EMA9 > EMA21)
- Exit: Fixed 10-day hold

### Results
```
Total signals:   2,807
5-day hold:      WR 48.7% | Avg +0.24%
10-day hold:     WR 51.2% | Avg +0.49%
```

### Analysis
- **Pullback strategy** trong uptrend
- Win rate > 51% nhưng avg return thấp
- Cần tối ưu exit để tăng profitability

---

## Test 4: EMA Cross + RSI + Volume Combo

### Setup
- Entry: EMA9 cross up EMA21 + RSI < 50 + RVOL > 1.0
- Exit: Fixed hold

### Results
```
Total signals:   224
10-day hold:     WR 50.0% | Avg +0.70%
20-day hold:     WR 45.5% | Avg -0.32%
```

### Analysis
- **Quality over quantity** - ít signal nhưng filtered
- 10-day tốt hơn 20-day → mean reversion

---

## Test 5: Refined Exposure Control

### Setup (5 levels thay vì 3)
```
EMA Bullish + Breadth >= 70%  → 100% exposure
EMA Bullish + Breadth 55-70%  → 80%
EMA Bullish + Breadth 40-55%  → 60%
EMA Bullish + Breadth 25-40%  → 40%
EMA Bullish + Breadth < 25%   → 20%
EMA Bearish                   → 0%
```

### Results
```
Buy & Hold:       +40.2%
Strategy:         +33.9%

Max DD B&H:       -35.1%
Max DD Strategy:  -14.5%  ← 58% reduction!

Sharpe B&H:       0.55
Sharpe Strategy:  0.82    ← 49% better risk-adjusted
```

### Exposure Distribution
| Level | Days | Percentage |
|-------|------|------------|
| 100% | 256 | 26% |
| 80% | 130 | 13% |
| 60% | 104 | 11% |
| 40% | 60 | 6% |
| 20% | 117 | 12% |
| 0% | 323 | 33% |

**Average exposure: 47.5%**

### Analysis
- Return thấp hơn B&H (-6%) nhưng **DD giảm 58%**
- Sharpe ratio tốt hơn 49%
- Phù hợp cho **quản trị rủi ro danh mục**

---

## VSA Signals Analysis

### Issue Found
VSA Stopping Volume = 0 signals vì điều kiện quá strict:
- `close < ma20` (downtrend) AND
- `rvol > 1.3` AND
- `close_position > 0.55`

Stocks midcap+ ít có pattern này. Cần relaxed hơn hoặc dùng cho penny stocks.

---

## Key Findings

### 1. Win Rate vs Profit Factor
```
Low WR (33%) + High PF (1.87) = Profitable
High WR (51%) + Low Avg (0.49%) = Marginal edge
```

### 2. Volume Confirmation Critical
- RVOL > 1.3 cho breakout
- RVOL > 0.8 cho EMA cross
- Low volume = false signal

### 3. Exposure Control Effective
- 5 levels smoother than 3 levels
- Giảm DD từ -35% xuống -15%
- Trade-off: Lower return nhưng better Sharpe

### 4. Holding Period Matters
- 10-day tốt hơn 20-day cho most signals
- EMA cross hold dài hơn (37 days avg)

---

## Recommended Strategy

### For Swing Trading
```
Entry:
- EMA9 cross up EMA21
- RVOL >= 0.8
- Market cap >= 5,000 tỷ
- Breadth >= 40%

Exit:
- EMA9 cross down EMA21
- OR 2x ATR trailing stop

Position Size:
- Based on exposure level (100/80/60/40/20%)
- Max 5 positions
```

### For Day/Short-term Trading
```
Entry:
- Breakout (close > 10-bar high)
- RVOL > 1.3

Exit:
- Fixed 5-10 day hold
- OR target +3-5%
```

---

## Next Steps

1. ✅ Backtest completed
2. 🔄 Fix VSA detection logic
3. 📊 Build dashboard với signals
4. 🧪 Paper trading validation

---

## Files
- `backtest_runner.py` - Reusable backtest code
- `ema_strategy_results.csv` - All EMA trades
