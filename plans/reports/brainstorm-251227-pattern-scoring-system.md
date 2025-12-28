# Brainstorm: Pattern Scoring System Redesign

**Date:** 2025-12-27
**Status:** Ready for Implementation
**Author:** Claude Code

---

## Problem Statement

Current scoring system có semantic không rõ ràng:
- KSB hiển thị "BEARISH 95 điểm" → User nghĩ "nên bán 95%"
- System thực tế nói: "Pattern này đáng tin cậy 95%"
- Điểm cơ sở hiện tại dựa trên estimation, không có backtest data

**User Requirements:**
1. Cần cả sort/filter VÀ hiểu pattern quality (ưu tiên quality)
2. Target: Professional traders - cần chi tiết
3. Cần có backtesting accuracy thực

---

## Research: Backtest Win Rates

### Sources
- [Quantified Strategies - 75 Patterns Backtest](https://www.quantifiedstrategies.com/the-complete-backtest-of-all-75-candlestick-patterns/)
- [Liberated Stock Trader - 56,680 Trades Study](https://www.liberatedstocktrader.com/candle-patterns-reliable-profitable/)
- [YourTradingCoach - Win Percentages](https://yourtradingcoach.com/trading-process-and-strategy/candlestick-pattern-win-percentages/)

### Key Findings (S&P 500 / Dow Jones Backtest)

| Pattern | Win Rate | Avg Profit/Trade | Sample Size | Source |
|---------|----------|------------------|-------------|--------|
| Inverted Hammer | **60%** | 1.12% | Large | Liberated |
| Three Outside Down | 58% | **0.73%** | S&P 500 | Quantified |
| Bearish Engulfing | 57-71% | 0.53% | 296 trades | Quantified |
| Gravestone Doji | 57% | - | Large | Liberated |
| Bearish Marubozu | 56.1% | - | Large | Liberated |
| Bullish Piercing Line | **Highest** | - | S&P 500 | Quantified |
| Bearish Belt Hold | 50% | - | S&P 500 | Quantified |
| Doji (general) | ~50% | - | - | Multiple |

### Critical Insight
> "Patterns only predictive for **max 10 days**. Context matters more than pattern alone."

---

## Recommended Solution: Dual-Metric System

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PATTERN SIGNAL CARD                          │
├─────────────────────────────────────────────────────────────────┤
│ KSB - Three Black Crows                        🔴 BEARISH       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│ │ Historical      │  │ Context         │  │ Composite       │  │
│ │ Win Rate        │  │ Confirmation    │  │ Score           │  │
│ │ ───────────     │  │ ───────────     │  │ ───────────     │  │
│ │ 57%             │  │ ██████░░ 75%    │  │ 73/100          │  │
│ │ (Based on 296   │  │                 │  │ (Strong Sell)   │  │
│ │  backtested     │  │ ✅ Vol ×2.1     │  │                 │  │
│ │  trades)        │  │ ✅ RSI=72 OB    │  │ Sortable        │  │
│ │                 │  │ ✅ Downtrend    │  │                 │  │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                 │
│ 📊 Recommendation: Strong signal, high probability setup       │
└─────────────────────────────────────────────────────────────────┘
```

### Metric 1: Historical Win Rate (Fixed per Pattern)

Based on backtested data, không đổi theo context:

```python
PATTERN_HISTORICAL_WIN_RATES = {
    # Bullish Patterns (research-based)
    'inverted_hammer': 60,      # Liberated: 60% win rate, 1.12% profit
    'hammer': 55,               # Moderate reliability
    'morning_star': 58,         # 3-candle reversal
    'three_white_soldiers': 56, # Strong but less frequent
    'engulfing_bullish': 57,    # Well-documented

    # Bearish Patterns
    'three_black_crows': 58,    # Three Outside Down proxy
    'evening_star': 57,         # Mirror of morning star
    'engulfing_bearish': 57,    # 57% win, 71% in some studies
    'shooting_star': 55,        # Moderate reliability
    'hanging_man': 52,          # Needs confirmation
    'gravestone_doji': 57,      # Liberated: 57%

    # Neutral/Low Reliability
    'doji': 50,                 # Indecision, coin flip
    'spinning_top': 50,         # No directional bias
}
```

### Metric 2: Context Confirmation Score (0-100%)

Dynamic, calculated based on current market conditions:

```python
def calculate_context_score(pattern, df, is_bullish):
    """
    Context confirmation checklist for professional traders.
    Returns score 0-100 and list of confirmations.
    """
    confirmations = []
    score = 0
    max_score = 100

    # 1. Volume Confirmation (25 points max)
    vol_ratio = current_volume / avg_volume_20
    if vol_ratio >= 2.5:
        score += 25
        confirmations.append(f"✅ Vol ×{vol_ratio:.1f} (Very Strong)")
    elif vol_ratio >= 2.0:
        score += 20
        confirmations.append(f"✅ Vol ×{vol_ratio:.1f} (Strong)")
    elif vol_ratio >= 1.5:
        score += 15
        confirmations.append(f"✅ Vol ×{vol_ratio:.1f} (Good)")
    elif vol_ratio >= 1.0:
        score += 5
        confirmations.append(f"⚠️ Vol ×{vol_ratio:.1f} (Normal)")
    else:
        confirmations.append(f"❌ Vol ×{vol_ratio:.1f} (Weak)")

    # 2. RSI Alignment (25 points max)
    rsi = calculate_rsi(df)
    if is_bullish:
        if rsi < 30:
            score += 25
            confirmations.append(f"✅ RSI={rsi:.0f} (Oversold)")
        elif rsi < 40:
            score += 15
            confirmations.append(f"✅ RSI={rsi:.0f} (Low)")
        elif rsi < 50:
            score += 5
            confirmations.append(f"⚠️ RSI={rsi:.0f} (Neutral)")
        else:
            confirmations.append(f"❌ RSI={rsi:.0f} (High for bullish)")
    else:  # Bearish
        if rsi > 70:
            score += 25
            confirmations.append(f"✅ RSI={rsi:.0f} (Overbought)")
        elif rsi > 60:
            score += 15
            confirmations.append(f"✅ RSI={rsi:.0f} (High)")
        elif rsi > 50:
            score += 5
            confirmations.append(f"⚠️ RSI={rsi:.0f} (Neutral)")
        else:
            confirmations.append(f"❌ RSI={rsi:.0f} (Low for bearish)")

    # 3. Trend Alignment (25 points max)
    ema20 = df['ema_20'].iloc[-1]
    ema50 = df['ema_50'].iloc[-1]
    price = df['close'].iloc[-1]

    if is_bullish:
        if price > ema20 > ema50:
            score += 25
            confirmations.append("✅ Uptrend (Price > EMA20 > EMA50)")
        elif price > ema20:
            score += 15
            confirmations.append("✅ Above EMA20")
        elif price > ema50:
            score += 5
            confirmations.append("⚠️ Above EMA50 only")
        else:
            confirmations.append("❌ Downtrend (counter-trend)")
    else:  # Bearish
        if price < ema20 < ema50:
            score += 25
            confirmations.append("✅ Downtrend (Price < EMA20 < EMA50)")
        elif price < ema20:
            score += 15
            confirmations.append("✅ Below EMA20")
        elif price < ema50:
            score += 5
            confirmations.append("⚠️ Below EMA50 only")
        else:
            confirmations.append("❌ Uptrend (counter-trend)")

    # 4. Support/Resistance Proximity (25 points max)
    high_20 = df['high'].rolling(20).max().iloc[-1]
    low_20 = df['low'].rolling(20).min().iloc[-1]
    range_20 = high_20 - low_20

    if is_bullish:
        # Near support = good for bullish
        distance_from_low = (price - low_20) / range_20 * 100
        if distance_from_low < 15:
            score += 25
            confirmations.append(f"✅ Near support ({distance_from_low:.0f}% from low)")
        elif distance_from_low < 30:
            score += 15
            confirmations.append(f"✅ Close to support ({distance_from_low:.0f}% from low)")
        else:
            confirmations.append(f"⚠️ Far from support ({distance_from_low:.0f}% from low)")
    else:  # Bearish
        # Near resistance = good for bearish
        distance_from_high = (high_20 - price) / range_20 * 100
        if distance_from_high < 15:
            score += 25
            confirmations.append(f"✅ Near resistance ({distance_from_high:.0f}% from high)")
        elif distance_from_high < 30:
            score += 15
            confirmations.append(f"✅ Close to resistance ({distance_from_high:.0f}% from high)")
        else:
            confirmations.append(f"⚠️ Far from resistance ({distance_from_high:.0f}% from high)")

    return score, confirmations
```

### Metric 3: Composite Score (for Sorting)

```python
def calculate_composite_score(win_rate, context_score, is_bullish):
    """
    Composite score for sorting/filtering.
    Range: -100 to +100

    Formula: Direction × Weighted Average
    - Win Rate weight: 40%
    - Context weight: 60%
    """
    weighted_score = (win_rate * 0.4) + (context_score * 0.6)

    # Apply direction
    if is_bullish:
        return round(weighted_score)
    else:
        return round(-weighted_score)  # Negative for bearish

# Examples:
# KSB: BEARISH, win_rate=57%, context=75%
# Composite = -(57*0.4 + 75*0.6) = -(22.8 + 45) = -67.8 ≈ -68 (Strong Sell)

# ABC: BULLISH, win_rate=60%, context=90%
# Composite = +(60*0.4 + 90*0.6) = +(24 + 54) = +78 (Strong Buy)
```

---

## UI Display Recommendation

### Table View (Sortable)

| Symbol | Signal | Pattern | Win Rate | Context | Score | Action |
|--------|--------|---------|----------|---------|-------|--------|
| KSB | 🔴 | 3 Black Crows | 57% | 75% | -68 | Strong Sell |
| FPT | 🟢 | Inv. Hammer | 60% | 90% | +78 | Strong Buy |
| VNM | 🟢 | Doji | 50% | 40% | +23 | Weak (Skip) |
| ACB | 🔴 | Engulfing | 57% | 30% | -25 | Weak Sell |

**Sorting Options:**
- By Composite Score (default) → Best signals first
- By Win Rate → Most reliable patterns
- By Context → Best current setups

### Detail View (On Click)

```
┌────────────────────────────────────────────────────────────────┐
│ KSB - Three Black Crows                                        │
│ ════════════════════════════════════════════════════════════   │
│                                                                │
│ 📊 HISTORICAL PERFORMANCE                                      │
│ ─────────────────────────────                                  │
│ Win Rate: 57% (based on 296 S&P 500 backtested trades)        │
│ Avg Profit/Trade: 0.53%                                        │
│ Predictive Window: 5-10 days                                   │
│ Source: Quantified Strategies Research                         │
│                                                                │
│ 🎯 CONTEXT CONFIRMATION (75/100)                               │
│ ─────────────────────────────────                              │
│ ✅ Volume ×2.1 (Strong confirmation)           +20             │
│ ✅ RSI=72 (Overbought, good for bearish)       +25             │
│ ✅ Below EMA20 (Trend aligned)                 +15             │
│ ✅ Near 20-day high (Resistance zone)          +15             │
│                                                                │
│ 📈 COMPOSITE SCORE: -68 (Strong Sell)                          │
│                                                                │
│ ⚠️ NOTE: Pattern accuracy varies by market. VN market may      │
│    differ from S&P 500 backtest. Consider sector context.     │
└────────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Update Base Scores (alert_detector.py)

```python
# Replace PATTERN_BASE_SCORES with research-based win rates
PATTERN_HISTORICAL_WIN_RATES = {
    'inverted_hammer': 60,
    'hammer': 55,
    'morning_star': 58,
    'three_white_soldiers': 56,
    'engulfing': 57,  # Both bullish/bearish
    'three_black_crows': 58,
    'evening_star': 57,
    'shooting_star': 55,
    'hanging_man': 52,
    'doji': 50,
}
```

### Phase 2: Add Context Calculation

New method in AlertDetector:
- `calculate_context_score(symbol, df, is_bullish)`
- Returns: `(score: int, confirmations: List[str])`

### Phase 3: Update Parquet Schema

```python
# patterns_latest.parquet schema update
{
    'symbol': str,
    'date': date,
    'pattern_name': str,
    'signal': str,  # BULLISH/BEARISH
    'win_rate': int,  # Historical win rate (50-60)
    'context_score': int,  # 0-100
    'context_details': str,  # JSON string of confirmations
    'composite_score': int,  # -100 to +100
    'price': float
}
```

### Phase 4: Update UI (stock_scanner.py)

- Table columns: Symbol, Signal, Pattern, Win Rate, Context, Score
- Sort by composite_score default
- Click to expand details
- Color coding:
  - Score > 50: 🟢 Strong Buy
  - Score 25-50: 🟡 Buy
  - Score -25 to 25: ⚪ Neutral
  - Score -50 to -25: 🟡 Sell
  - Score < -50: 🔴 Strong Sell

---

## Success Metrics

1. **Clarity**: User understands difference between Win Rate vs Context
2. **Actionability**: Composite score enables quick sorting
3. **Trust**: Backtested data with source citations
4. **Professionalism**: Detailed breakdown for deep analysis

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| VN market differs from S&P 500 | Win rates may be inaccurate | Add disclaimer, future VN backtest |
| Too complex for UI | User overwhelmed | Default to simple view, expand on click |
| Context calculation slow | Dashboard lag | Cache context scores, batch calculate |

---

## Next Steps

1. ✅ Research complete
2. ⏳ User approval of approach
3. ⏳ Implement Phase 1-4
4. ⏳ Update README documentation
5. ⏳ Test with real data

---

## Unresolved Questions

1. **VN Market Backtest**: Should we build our own backtest for VN stocks? (Recommended but requires historical data + effort)
2. **Pattern Frequency**: Some patterns rare (Three White Soldiers) - warn user about sample size?
3. **Holding Period**: Current system shows signal but not exit. Add suggested hold time (5-10 days based on research)?
