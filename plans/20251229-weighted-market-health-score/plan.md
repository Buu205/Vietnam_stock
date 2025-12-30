# Weighted Market Health Score Implementation

**Plan ID:** 20251229-weighted-market-health-score
**Created:** 2025-12-29
**Status:** ✅ Complete
**Priority:** Medium

---

## Overview

Refactor `avg_breadth` calculation in `market_overview.py` to use weighted Market Health Score from `strategy_pullback.md`.

**Current State:**
- Equal-weighted: `avg_breadth = (MA20 + MA50 + MA100) / 3`
- Thresholds: 70/30

**Target State:**
- Weighted: `market_score = MA50*0.5 + MA20*0.3 + MA100*0.2`
- Thresholds: 75/30
- Signal Matrix: DIAMOND BUY, STANDARD BUY, WARNING, HOLD, SELL, DANGER

---

## Phases

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 1 | [Weighted Score + Signal Matrix](phase-01-weighted-score-signal-matrix.md) | ✅ Complete | 100% |

---

## Files to Modify

| File | Changes |
|------|---------|
| `WEBAPP/pages/technical/components/market_overview.py` | `_render_breadth_gauges()` function (lines 368-420) |

---

## Dependencies

- `strategy_pullback.md` - Strategy document defining weights and signals
- `TADashboardService` - Provides `state.breadth_maXX_pct` values

---

## Success Criteria

1. ✅ Formula changed to weighted calculation
2. ✅ Thresholds updated to 75/30
3. ✅ Signal Matrix implemented with Vietnamese messages
4. ✅ UI colors remain consistent with existing design
5. ✅ No regressions in other components

---

## Related Documents

- [Strategy Pullback](../../strategy_pullback.md) - Trading strategy document
- [Codebase Summary](../../docs/codebase-summary.md)
