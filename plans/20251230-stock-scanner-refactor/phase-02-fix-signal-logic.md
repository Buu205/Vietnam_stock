# Phase 2: Trend-Aware Signal Logic

**Priority:** P0 (Critical)
**Status:** In Progress
**Estimated Changes:** ~80 lines

## Core Principle: TA Flow

```
TREND (1M/3M) → PATTERN → CONCLUSION
```

Signal quality depends on pattern-trend alignment:
- **Aligned**: Pattern confirms trend → Strong signal
- **Counter**: Pattern against trend → Weak signal / HOLD

---

## Available Trend Data

From `basic_data.parquet`:

| Column | Description | Trend Signal |
|--------|-------------|--------------|
| `price_vs_sma20` | % above/below SMA20 | 1M trend |
| `price_vs_sma50` | % above/below SMA50 | 3M trend |
| `macd_hist` | MACD histogram | Momentum |

**Trend Classification:**
- `price_vs_sma20 > 2%` AND `price_vs_sma50 > 2%` → **UPTREND**
- `price_vs_sma20 < -2%` AND `price_vs_sma50 < -2%` → **DOWNTREND**
- Otherwise → **SIDEWAYS**

---

## Problems to Fix

### P1: Duplicate Tickers
Same stock appears multiple times when multiple patterns detected.

### P2: Conflicting Signals
Same stock shows both MUA and BÁN:
- Doji incorrectly mapped as BULLISH (should be NEUTRAL)
- Signal ignores trend context

### P3: Pattern-Trend Mismatch
Example: DTD shows MUA (bullish doji) in DOWNTREND
- TA-Lib output: `values[-1] > 0` = BULLISH
- Context: "Downtrend (counter)" but signal still BULLISH

---

## Solution: Trend-Aware Signal Mapping

### Step 1: JOIN Trend Data

```python
# In _load_signals(), after loading patterns
basic_path = Path("DATA/processed/technical/basic_data.parquet")
if basic_path.exists():
    basic_df = pd.read_parquet(basic_path, columns=[
        'symbol', 'date', 'price_vs_sma20', 'price_vs_sma50', 'trading_value'
    ])
    patterns_df = patterns_df.merge(basic_df, on=['symbol', 'date'], how='left')
```

### Step 2: Classify Trend

```python
def classify_trend(row):
    sma20 = row.get('price_vs_sma20', 0) or 0
    sma50 = row.get('price_vs_sma50', 0) or 0

    if sma20 > 2 and sma50 > 2:
        return 'UPTREND'
    elif sma20 < -2 and sma50 < -2:
        return 'DOWNTREND'
    return 'SIDEWAYS'

df['trend'] = df.apply(classify_trend, axis=1)
```

### Step 3: Trend-Aware Signal

```python
def get_signal_with_trend(row):
    pattern_signal = row['signal']  # BULLISH, BEARISH, NEUTRAL
    trend = row['trend']
    pattern_name = row.get('pattern_name', '')

    # Doji is always NEUTRAL (indecision)
    if pattern_name == 'doji':
        return 'NEUTRAL'

    # Aligned signals: pattern confirms trend
    if pattern_signal == 'BULLISH' and trend == 'UPTREND':
        return 'BUY'  # Strong buy: bullish continuation
    if pattern_signal == 'BEARISH' and trend == 'DOWNTREND':
        return 'SELL'  # Strong sell: bearish continuation

    # Counter-trend signals: risky, downgrade to HOLD
    if pattern_signal == 'BULLISH' and trend == 'DOWNTREND':
        return 'HOLD'  # Risky: bullish in downtrend
    if pattern_signal == 'BEARISH' and trend == 'UPTREND':
        return 'HOLD'  # Risky: bearish in uptrend

    # Sideways: follow pattern
    if pattern_signal == 'BULLISH':
        return 'BUY'
    if pattern_signal == 'BEARISH':
        return 'SELL'

    return 'NEUTRAL'

df['direction'] = df.apply(get_signal_with_trend, axis=1)
```

---

## Signal Logic Matrix

| Pattern | Trend | Direction | Rationale |
|---------|-------|-----------|-----------|
| BULLISH | UPTREND | **BUY** | Aligned - continuation signal |
| BULLISH | DOWNTREND | HOLD | Counter - risky reversal |
| BULLISH | SIDEWAYS | BUY | Follow pattern |
| BEARISH | DOWNTREND | **SELL** | Aligned - continuation signal |
| BEARISH | UPTREND | HOLD | Counter - risky reversal |
| BEARISH | SIDEWAYS | SELL | Follow pattern |
| Doji | Any | NEUTRAL | Indecision pattern |

---

## Deduplication Logic

Keep only 1 signal per ticker+date (highest strength):

```python
# Dedup: Keep highest strength per ticker+date
combined = combined.sort_values('strength', ascending=False)
combined = combined.drop_duplicates(subset=['symbol', 'date'], keep='first')
```

---

## File Changes

### `WEBAPP/pages/technical/services/ta_dashboard_service.py`

**Location:** `_load_signals()` function (~line 286-390)

**Complete rewrite of patterns loading section:**

```python
# 1. Candlestick Patterns - most useful signal type
patterns_path = history_dir / "patterns_history.parquet"
if not patterns_path.exists():
    patterns_path = daily_dir / "patterns_latest.parquet"

if patterns_path.exists():
    df = pd.read_parquet(patterns_path)
    df['signal_type'] = 'patterns'
    df['type_label'] = df['pattern_name'].fillna('Pattern')

    # JOIN trend data from basic_data
    basic_path = Path("DATA/processed/technical/basic_data.parquet")
    if basic_path.exists():
        basic_df = pd.read_parquet(basic_path, columns=[
            'symbol', 'date', 'price_vs_sma20', 'price_vs_sma50', 'trading_value'
        ])
        # Normalize dates for join
        basic_df['date'] = pd.to_datetime(basic_df['date']).dt.date
        df['date'] = pd.to_datetime(df['date']).dt.date
        df = df.merge(basic_df, on=['symbol', 'date'], how='left')

    # Classify trend
    def classify_trend(row):
        sma20 = row.get('price_vs_sma20', 0) or 0
        sma50 = row.get('price_vs_sma50', 0) or 0
        if sma20 > 2 and sma50 > 2:
            return 'UPTREND'
        elif sma20 < -2 and sma50 < -2:
            return 'DOWNTREND'
        return 'SIDEWAYS'

    df['trend'] = df.apply(classify_trend, axis=1)

    # Trend-aware signal
    def get_signal_with_trend(row):
        pattern_signal = row['signal']
        trend = row['trend']
        pattern_name = row.get('pattern_name', '')

        if pattern_name == 'doji':
            return 'NEUTRAL'
        if pattern_signal == 'BULLISH' and trend == 'UPTREND':
            return 'BUY'
        if pattern_signal == 'BEARISH' and trend == 'DOWNTREND':
            return 'SELL'
        if pattern_signal == 'BULLISH' and trend == 'DOWNTREND':
            return 'HOLD'
        if pattern_signal == 'BEARISH' and trend == 'UPTREND':
            return 'HOLD'
        if pattern_signal == 'BULLISH':
            return 'BUY'
        if pattern_signal == 'BEARISH':
            return 'SELL'
        return 'NEUTRAL'

    df['direction'] = df.apply(get_signal_with_trend, axis=1)

    all_signals.append(df[[
        'symbol', 'date', 'signal_type', 'type_label', 'direction',
        'price', 'strength', 'trend', 'trading_value'
    ]])
```

---

## Implementation Steps

- [x] Phase 1: Fix data source (load history files)
- [ ] Add trend data JOIN in `_load_signals()`
- [ ] Implement `classify_trend()` function
- [ ] Implement `get_signal_with_trend()` function
- [ ] Update column selection to include trend, trading_value
- [ ] Add deduplication logic
- [ ] Test: Verify trend-aligned signals

---

## Test Cases

### Before (Wrong)
| Ticker | Pattern | Trend | Direction |
|--------|---------|-------|-----------|
| DTD | doji | DOWNTREND | MUA ❌ |
| HLD | hammer | DOWNTREND | MUA ❌ |

### After (Correct)
| Ticker | Pattern | Trend | Direction |
|--------|---------|-------|-----------|
| DTD | doji | DOWNTREND | NEUTRAL ✅ |
| HLD | hammer | DOWNTREND | HOLD ✅ |

---

## Success Criteria

- [ ] No duplicate tickers per date
- [ ] Doji → NEUTRAL (not MUA)
- [ ] Bullish pattern in downtrend → HOLD (not MUA)
- [ ] Bearish pattern in uptrend → HOLD (not BÁN)
- [ ] Aligned patterns → Strong BUY/SELL
- [ ] Trend column visible in UI (optional)

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing basic_data | Fallback to original signal | Check file exists |
| Date format mismatch | JOIN fails | Normalize both to date |
| Counter-trend = HOLD | Fewer actionable signals | User can filter by direction |
