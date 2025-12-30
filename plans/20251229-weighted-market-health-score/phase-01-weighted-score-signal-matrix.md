# Phase 1: Weighted Score + Signal Matrix

**Parent Plan:** [plan.md](plan.md)
**Date:** 2025-12-29
**Priority:** Medium
**Status:** ✅ Complete

---

## Context

The current `_render_breadth_gauges()` function uses simple average for market health scoring. The `strategy_pullback.md` document specifies a weighted approach optimized for 4-8 week swing trading.

---

## Key Insights

| Insight | Detail |
|---------|--------|
| **MA50 = Trend backbone** | Most important for swing trading (50% weight) |
| **MA20 = Trigger** | Short-term momentum for timing (30% weight) |
| **MA100 = Safety filter** | Long-term context (20% weight) |
| **Signal Matrix** | 6 states based on trend (MA50+MA100) + momentum (MA20) |

---

## Requirements

### Functional
1. Replace equal-weighted average with: `market_score = MA50*0.5 + MA20*0.3 + MA100*0.2`
2. Update threshold from 70 to 75 for overbought
3. Implement Signal Matrix with 6 states
4. Vietnamese messages per strategy doc

### Non-Functional
- Maintain existing UI/color scheme
- No breaking changes to other components

---

## Architecture

### Signal Matrix Logic

```
UPTREND (MA50 >= 50 AND MA100 >= 50):
├── MA20 < 20  → 💎 DIAMOND BUY (Deep Pullback)
├── MA20 < 40  → ✅ STANDARD BUY (Normal Pullback)
├── MA20 > 80  → ⚠️ WARNING (Overheated)
└── else       → ⚓ HOLD (Riding Trend)

DOWNTREND/SIDEWAYS:
├── MA20 > 70  → ⛔ SELL (Bull Trap)
├── MA50 < 30 AND MA20 < 20 → ☠️ DANGER (Market Crash)
└── else       → 💤 WAIT (No Trend)
```

### Color Mapping

| Signal | Color | Hex |
|--------|-------|-----|
| DIAMOND BUY | Dark Green | #059669 |
| STANDARD BUY | Green | #10B981 |
| WARNING | Amber | #F59E0B |
| HOLD | Blue | #3B82F6 |
| SELL | Red | #DC2626 |
| DANGER | Dark Red | #7F1D1D |
| WAIT | Gray | #9CA3AF |

---

## Related Code Files

| File | Purpose |
|------|---------|
| `WEBAPP/pages/technical/components/market_overview.py` | Target file (function `_render_breadth_gauges`) |
| `strategy_pullback.md` | Source strategy document |

---

## Implementation Steps

### Step 1: Add Weight Constants
```python
# At top of file, after BREADTH_COLORS
MARKET_SCORE_WEIGHTS = {
    'ma50': 0.5,   # Trend backbone
    'ma20': 0.3,   # Trigger
    'ma100': 0.2,  # Safety filter
}
```

### Step 2: Replace avg_breadth Calculation
```python
# OLD (line 405)
avg_breadth = (state.breadth_ma20_pct + state.breadth_ma50_pct + state.breadth_ma100_pct) / 3

# NEW
market_score = (
    state.breadth_ma50_pct * MARKET_SCORE_WEIGHTS['ma50'] +
    state.breadth_ma20_pct * MARKET_SCORE_WEIGHTS['ma20'] +
    state.breadth_ma100_pct * MARKET_SCORE_WEIGHTS['ma100']
)
```

### Step 3: Implement Signal Matrix Logic
Replace simple threshold logic (lines 406-414) with Signal Matrix.

### Step 4: Update Summary Display
Keep existing HTML structure, update text and colors per Signal Matrix.

---

## Todo List

- [x] Add `MARKET_SCORE_WEIGHTS` constant
- [x] Replace `avg_breadth` with `market_score` calculation
- [x] Implement Signal Matrix logic (7 states including HOLD)
- [x] Update summary messages to Vietnamese
- [x] Add recovery indicator (ONLY for buy signals in uptrend)
- [x] Redesign Signal Matrix Card with professional trading terminal UI
- [x] Verify UI consistency

---

## Success Criteria

1. Formula uses weights: MA50=50%, MA20=30%, MA100=20%
2. Threshold changed: 70→75 for overbought
3. 6 signal states display correctly with proper colors
4. Vietnamese messages match strategy doc
5. No visual regressions

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| State object missing fields | Low | Medium | Check `state` has `breadth_maXX_pct` |
| Color contrast issues | Low | Low | Use existing color palette |

---

## Security Considerations

None - UI-only change, no data processing.

---

## Next Steps

After implementation:
1. Test with live dashboard
2. Consider adding Market Score metric card in metrics bar
