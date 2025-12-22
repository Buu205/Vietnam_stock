# FX & Commodities Dashboard Refactor Plan

**Created:** 2025-12-21
**Status:** Planning Complete
**Scope:** Symbol mapping fix, dual-axis charts, performance tables, UI polish

---

## Executive Summary

Dashboard has 50% macro symbol mismatch causing chart failures. Commodities are clean.
Research confirms glassmorphism design tokens ready in codebase. KISS approach: fix symbols first.

## Problem Statement

- **Root Cause:** Dashboard `macro_labels` expects snake_case but data has Vietnamese diacritics
- **Example:** Data has `tỷ_giá_usd_trung_tâm` but dashboard looks for `ty_gia_usd_trung_tam`
- **Impact:** Interest rate charts fail for deposit rates (3 symbols), exchange rates (3 symbols)

## Architecture Decision

**Option A (Chosen):** Fix symbol mapping at dashboard level
- Pros: No data pipeline changes, quick fix, backward compatible
- Cons: Mapping dict maintenance burden

**Option B (Rejected):** Fix upstream data pipeline
- Pros: Clean data at source
- Cons: Requires pipeline changes, risk of breaking other consumers

## Phase Breakdown

| Phase | Scope | Est. Effort | Risk |
|-------|-------|-------------|------|
| 1 - Symbol Mapping | Map actual→expected symbols | 2h | Low |
| 2 - Dual-Axis Charts | Interest rates grouped, FX pairs | 3h | Medium |
| 3 - Performance Tables | 1D/1W/1M/3M/1Y with trends | 4h | Medium |
| 4 - UI/UX Polish | Glassmorphism, JetBrains Mono | 2h | Low |

**Total:** ~11 hours (1.5 days)

## Key Files

| File | Purpose | Changes |
|------|---------|---------|
| `fx_commodities_dashboard.py` | Main dashboard | Phases 1-4 |
| `macro_commodity_loader.py` | Data loader | Phase 1 only |
| `styles.py` | Glassmorphism CSS | Read-only (reuse) |
| `table_builders.py` | Table patterns | Phase 3 reference |

## Success Criteria

1. All 12 macro symbols render charts correctly
2. Interest rate groups (deposit, interbank) on shared axis
3. Performance table with color-coded 1D/1W/1M/3M/1Y columns
4. Purple/cyan glassmorphism theme applied consistently

## Dependencies

- Research reports completed (see `research/` folder)
- `styles.py` has design tokens ready (lines 49-115)
- `table_builders.py` has status color patterns (lines 84-91)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Upstream data format changes | High | Add symbol validation logging |
| Missing data for some tenors | Medium | Graceful fallback with warning |
| Performance with large tables | Low | Limit to 30 rows, add pagination |

---

## Phase Details

See individual phase files for implementation steps:
- `phase-01-symbol-mapping-fix.md`
- `phase-02-dual-axis-charts.md`
- `phase-03-performance-tables.md`
- `phase-04-uiux-polish.md`
