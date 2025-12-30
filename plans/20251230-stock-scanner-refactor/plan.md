# Stock Scanner Tab - Complete Refactor Plan

**Created:** 2025-12-30
**Status:** Planning
**Priority:** High

## Overview

Technical Dashboard's Stock Scanner tab (Tab 3) has critical issues affecting signal quality and user experience. This plan addresses 6 identified problems through 4 implementation phases.

## Problems Summary

| ID | Problem | Impact | Phase |
|----|---------|--------|-------|
| P1 | Duplicate tickers | Table clutter, confusion | Phase 2 |
| P2 | Conflicting signals (MUA+BÁN) | Trader confusion | Phase 2 |
| P3 | Wrong data source (1 day only) | Date filter broken | Phase 1 |
| P4 | No action priority sort | Buy signals buried | Phase 3 |
| P5 | No liquidity filter | Penny stocks appear | Phase 3 |
| P6 | Score default = 0 | Too many weak signals | Phase 3 |

## Phase Summary

| Phase | Name | Status | Est. Lines |
|-------|------|--------|------------|
| [Phase 1](phase-01-fix-data-source.md) | Fix Data Source | ✅ Done | ~30 |
| [Phase 2](phase-02-fix-signal-logic.md) | Trend-Aware Signal Logic | ✅ Done | ~80 |
| [Phase 3](phase-03-add-filters.md) | Add Filters & Sort | ✅ Done | ~80 |
| [Phase 4](phase-04-ui-redesign.md) | UI Redesign - Split Tables | ✅ Done | ~150 |
| Phase 5 | Single Stock Analysis | ✅ Done | ~200 |

## Files to Modify

| File | Changes |
|------|---------|
| `WEBAPP/pages/technical/services/ta_dashboard_service.py` | Load history files, add trading_value JOIN |
| `WEBAPP/pages/technical/components/stock_scanner.py` | Add filters UI, update defaults, dedup logic |

## Dependencies

- `DATA/processed/technical/alerts/historical/patterns_history.parquet` (9 days data)
- `DATA/processed/technical/basic_data.parquet` (trading_value column)

## Success Criteria

1. ✅ No duplicate tickers in table (1 row per ticker+date)
2. ✅ Date filter works correctly (multiple days visible)
3. ✅ MUA signals displayed first, sorted by score
4. ✅ Liquidity filter available (GTGD slider)
5. ✅ Score filter default = 50
6. ✅ **UI: Split tables** - MUA | BÁN | PULLBACK/BOUNCE (3 columns)
7. ✅ **UI: Compact design** - 4 columns (Mã, Trend, Mẫu hình, Điểm)
8. ✅ **UI: Progress bars** - Color-coded by score range
9. ✅ **UI: Trend filter** - Filter by UPTREND/DOWNTREND/SIDEWAYS
10. ✅ **UI: Trend badges** - ⬆⬆/⬆/↔/⬇/⬇⬇ icons on each row
11. ✅ **UI: Single Stock Analysis** - Enter ticker → see trend + patterns + strategy
12. ✅ **UI: Volume Analysis** - GTGD + Volume trend ratio in single stock view

## Constraints

- KISS: Simple solutions only
- No breaking changes to existing UI structure
- Maintain Vietnamese labels and interpretations
