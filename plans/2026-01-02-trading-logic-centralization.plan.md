# Trading Logic Centralization Plan

**Created:** 2026-01-02
**Status:** ✅ Complete
**Priority:** High
**Scope:** Technical Dashboard + Forecast Dashboard

---

## Objective

Centralize all trading constants, thresholds, và business rules vào `WEBAPP/core/` để:
- Single source of truth cho parameters
- Dễ tune/adjust mà không sửa UI code
- Chuẩn bị cho future migration (HTML/React)

---

## Deliverables

| File | Purpose |
|------|---------|
| `WEBAPP/core/trading_constants.py` | Thresholds, windows, weights |
| `WEBAPP/core/trading_rules.py` | Signal matrix, state machines |
| `docs/TRADING_LOGIC.md` | Human-readable reference |

---

## Phase 1: Technical Dashboard - Market Overview ✅ COMPLETE

### Task 1.1: Create trading_constants.py ✅
- [x] Create `WEBAPP/core/trading_constants.py`
- [x] Add breadth thresholds (OVERBOUGHT=80, OVERSOLD=20)
- [x] Add swing windows (MA20_WINDOW=7, MA50_WINDOW=9)
- [x] Add market score weights
- [x] Add bottom detection thresholds
- [x] Add docstrings with rationale

### Task 1.2: Create trading_rules.py ✅
- [x] Create `WEBAPP/core/trading_rules.py`
- [x] Move `SIGNAL_MATRIX` from market_overview.py
- [x] Move `BOTTOM_STAGES` from market_overview.py
- [x] Move `REGIME_STYLES` from market_overview.py
- [x] Move `SIGNAL_STYLES` from market_overview.py

### Task 1.3: Update market_overview.py ✅
- [x] Import from `WEBAPP.core.trading_constants`
- [x] Import from `WEBAPP.core.trading_rules`
- [x] Remove inline constant definitions
- [x] Test UI renders correctly

### Task 1.4: Update ta_dashboard_service.py ✅
- [x] Import `MA20_HIGHER_LOW_WINDOW`, `MA50_HIGHER_LOW_WINDOW`
- [x] Replace hardcoded values (7, 9)
- [x] Test higher low detection works

---

## Phase 2: Technical Dashboard - Stock Scanner ✅ COMPLETE

### Task 2.1: Extract pattern constants ✅
- [x] Move `SIGNAL_TYPES` to trading_rules.py
- [x] Move `PATTERN_INTERPRETATIONS` to trading_rules.py (66 patterns)
- [x] Move `PATTERN_VOLUME_MATRIX` to trading_rules.py

### Task 2.2: Extract scanner display constants ✅
- [x] Move `ACTION_COLORS` to trading_rules.py
- [x] Move `VOLUME_CONTEXT` to trading_rules.py

### Task 2.3: Update stock_scanner.py ✅
- [x] Import from trading_rules
- [x] Remove inline definitions
- [x] Test scanner imports correctly

---

## Phase 3: Technical Dashboard - Sector Rotation ✅ COMPLETE

### Task 3.1: Extract RRG constants ✅
- [x] Move `QUADRANT_COLORS` to trading_rules.py
- [x] Move `QUADRANT_BG` to trading_rules.py
- [x] Move `QUADRANT_TRAIL` to trading_rules.py
- [x] Move `BSC_UNIVERSE` to trading_constants.py (44 stocks)
- [x] Move `WATCHLISTS` to trading_constants.py (6 lists)

### Task 3.2: Update sector_rotation.py ✅
- [x] Import from trading modules
- [x] Remove inline definitions
- [x] Test imports correctly

---

## Phase 4: Forecast Dashboard ✅ COMPLETE

### Task 4.1: Extract forecast constants ✅
- [x] Add `RATING_COLORS` to trading_rules.py
- [x] Add `RATING_BG_COLORS` to trading_rules.py
- [x] Add achievement thresholds (85%, 65%, 50%) to trading_constants.py

### Task 4.2: Update forecast files ✅
- [x] Update forecast_dashboard.py imports
- [x] Update achievement_cards.py imports
- [x] Test forecast imports correctly

---

## Phase 5: Documentation ✅ COMPLETE

### Task 5.1: Create TRADING_LOGIC.md ✅
- [x] Document all thresholds with rationale
- [x] Document signal matrix logic
- [x] Document bottom detection stages
- [x] Add backtest methodology notes

### Task 5.2: Update existing docs
- [x] Created `docs/TRADING_LOGIC.md` as central reference

---

## Phase 6: Verification ✅ COMPLETE

### Task 6.1: Test all imports ✅
- [x] trading_constants.py - 44 stocks, all thresholds
- [x] trading_rules.py - 9 signals, 66 patterns
- [x] market_overview.py imports correctly
- [x] stock_scanner.py imports correctly
- [x] sector_rotation.py imports correctly
- [x] forecast_dashboard.py imports correctly
- [x] achievement_cards.py imports correctly
- [x] ta_dashboard_service.py imports correctly

### Task 6.2: Code review ✅
- [x] No duplicate constants remain (all extracted)
- [x] All imports work (verified with Python)

---

## Constants Reference

### Breadth Thresholds
| Constant | Value | Rationale |
|----------|-------|-----------|
| `OVERBOUGHT_THRESHOLD` | 80 | >80% precedes corrections 73% of time |
| `OVERSOLD_THRESHOLD` | 20 | <20% is extreme fear zone |
| `TREND_CONFIRMATION` | 50 | MA50≥50 AND MA100≥50 = uptrend |

### Swing Windows (3-year backtest 2023-2025)
| Constant | Value | Derivation |
|----------|-------|------------|
| `MA20_HIGHER_LOW_WINDOW` | 7 days | Median cycle 14.5d / 2 |
| `MA50_HIGHER_LOW_WINDOW` | 9 days | Median cycle 19.0d / 2 |

### Market Score Weights
| Component | Weight | Role |
|-----------|--------|------|
| MA50 | 50% | Trend backbone |
| MA20 | 30% | Timing/Trigger |
| MA100 | 20% | Safety filter |

### Bottom Detection
| Stage | Threshold | Condition |
|-------|-----------|-----------|
| CAPITULATION | <25% | All MAs < 25%, no higher low |
| ACCUMULATING | <30% | All MAs < 30%, MA20 higher low |
| EARLY_REVERSAL | ≥25% | MA20 ≥25% + both higher lows |

---

## Notes

- Colors (UI) stay in components or styles.py
- Only business logic numbers move to trading_constants.py
- Signal definitions with conditions move to trading_rules.py
- Run dashboard after each phase to catch errors early

---

## Progress Log

| Date | Phase | Status | Notes |
|------|-------|--------|-------|
| 2026-01-02 | Plan created | ✅ | - |
| 2026-01-02 | Phase 1 | ✅ | Market Overview centralized |
| 2026-01-02 | Phase 2 | ✅ | Stock Scanner centralized |
| 2026-01-02 | Phase 3 | ✅ | Sector Rotation centralized |
| 2026-01-02 | Phase 4 | ✅ | Forecast Dashboard centralized |
| 2026-01-02 | Phase 5 | ✅ | docs/TRADING_LOGIC.md created |
| 2026-01-02 | Phase 6 | ✅ | All imports verified |

---

## Final Summary

**Centralized ~300+ lines** of inline constants from 6 UI components into 2 core modules:

| Module | Contents |
|--------|----------|
| `WEBAPP/core/trading_constants.py` | 44 stocks, 6 watchlists, breadth thresholds, swing windows, weights |
| `WEBAPP/core/trading_rules.py` | 9 signals, 66 patterns, rating colors, quadrant colors |

**Benefits:**
- Single source of truth for all trading parameters
- Easy to tune thresholds without touching UI code
- Ready for future HTML/React migration
