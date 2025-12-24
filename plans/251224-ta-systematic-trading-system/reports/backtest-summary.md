# Backtest Summary Report

**Date:** 2025-12-24
**Period:** 2022-01-04 to 2025-12-23
**Universe:** 151 stocks (Market cap >= 5,000 tỷ VND)

---

## Validated Strategies

### 1. EMA 9/21 Cross Strategy ✅

| Metric | Value | Assessment |
|--------|-------|------------|
| Total Trades | 2,273 | High frequency |
| Win Rate | 33.4% | Low but acceptable |
| Avg PnL | +2.47% | Profitable |
| Median PnL | -1.99% | Skewed by winners |
| Total Return | +5,621% | Excellent |
| Profit Factor | 1.87 | **PROFITABLE** |
| Avg Holding | 37 days | Swing trading |

**Key Insight:** Low win rate (33%) but high profit factor (1.87) = trend following works. Winners are much larger than losers.

---

### 2. Breakout + Volume Strategy ✅

| Metric | 5-Day Hold | 10-Day Hold |
|--------|------------|-------------|
| Signals | 6,863 | 6,863 |
| Win Rate | 49.3% | 50.9% |
| Avg PnL | +0.68% | +1.21% |

**Key Insight:** 10-day hold outperforms 5-day. Volume confirmation (RVOL > 1.3) is critical.

---

### 3. RSI Oversold + EMA Bullish ⚠️

| Metric | 5-Day Hold | 10-Day Hold |
|--------|------------|-------------|
| Signals | 2,807 | 2,807 |
| Win Rate | 48.7% | 51.2% |
| Avg PnL | +0.24% | +0.49% |

**Key Insight:** Marginal edge. Better as filter than standalone strategy.

---

### 4. Variable Exposure Control ✅✅

| Metric | Buy & Hold | Strategy | Improvement |
|--------|------------|----------|-------------|
| Return | +40.2% | +33.9% | -6% |
| Max DD | -35.1% | -14.5% | **-58%** |
| Sharpe | 0.55 | 0.82 | **+49%** |

**Exposure Distribution:**
| Level | Days | % Time |
|-------|------|--------|
| 100% | 256 | 26% |
| 80% | 130 | 13% |
| 60% | 104 | 11% |
| 40% | 60 | 6% |
| 20% | 117 | 12% |
| 0% | 323 | 33% |

**Avg Exposure:** 47.5%

**Key Insight:** Trade-off: Lower return (-6%) but dramatically reduced drawdown (-58%) and better risk-adjusted returns (Sharpe +49%).

---

### 5. VSA Stopping Volume ⚠️

| Metric | Value |
|--------|-------|
| Signals | Very few (strict conditions) |
| Win Rate | 54.3% |
| Avg PnL | +0.67% |

**Issue:** Conditions too strict for midcap+. Needs relaxed thresholds:
- `rvol > 1.3` instead of `rvol > 1.5`
- `close_position > 0.55` instead of `> 0.6`

---

## Key Findings

### 1. Win Rate vs Profit Factor
```
Low WR (33%) + High PF (1.87) = PROFITABLE (trend following)
High WR (51%) + Low Avg (0.49%) = MARGINAL (mean reversion)
```

### 2. Volume Confirmation is Critical
| Signal Type | RVOL Threshold | Purpose |
|-------------|---------------|---------|
| Breakout | > 1.3 | Strong confirmation |
| EMA Cross | >= 0.8 | Valid signal |
| VSA | > 1.3 | Pattern validity |

### 3. Market Cap Filter Essential
- Without filter: Results polluted by illiquid penny stocks
- With filter (>= 5,000 tỷ): Clean, tradeable signals
- Universe: 151 stocks

### 4. Exposure Control Effective
- 5 levels smoother than 3 levels
- Reduces DD from -35% to -15%
- Worth the slight return sacrifice

### 5. Holding Period Matters
- EMA strategy: 37 days avg (swing)
- Breakout: 10 days > 5 days
- RSI pullback: 10 days optimal

---

## Recommended Implementation

### For Swing Trading (Primary)
```
Entry:
- EMA9 cross up EMA21
- RVOL >= 0.8
- Market cap >= 5,000 tỷ
- Sector in top 50%
- Market breadth >= 40%

Exit:
- EMA9 cross down EMA21
- OR 1.5x ATR trailing stop

Position Size:
- Risk 1% per trade
- Adjust by exposure level (100/80/60/40/20%)
- Max 5-10 positions
```

### For Short-term Trading (Secondary)
```
Entry:
- Breakout (close > 10-bar swing high)
- RVOL > 1.3

Exit:
- Fixed 10-day hold
- OR target +5%
- OR stop -3%
```

---

## Files Reference

| File | Description |
|------|-------------|
| `BACKTEST_RESULTS.md` | Detailed backtest report |
| `backtest_runner.py` | Reusable backtest code |
| `ema_strategy_results.csv` | All EMA trades |
| `vsa_stopping_results.csv` | VSA signal results |

---

## Next Steps

1. ✅ Backtest validation - DONE
2. 📝 Implementation plan - DONE
3. 🔧 Add indicators to processors
4. 📊 Build dashboard pages
5. 🚀 Deploy daily pipeline
