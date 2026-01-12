# Brainstorm: Streamlit Pages Optimization

**Date:** 2025-12-21
**Status:** Pending Decision
**Author:** Claude + User

---

## Problem Statement

1. **Code Duplication:** Sector Overview và Valuation pages có nhiều code trùng lặp (~400-500 lines)
2. **Forecast UX:** Forecast page chưa optimal cho việc xem dự báo & định giá BSC forecast
3. **File Conflict:** Tồn tại 2 file forecast_dashboard.py

---

## Current State Analysis

### File Sizes

| Page | Location | Lines |
|------|----------|-------|
| Sector | `/WEBAPP/pages/sector/sector_dashboard.py` | 1,370 |
| Valuation | `/WEBAPP/pages/valuation/valuation_dashboard.py` | 1,032 |
| Forecast (old) | `/WEBAPP/pages/forecast_dashboard.py` | 1,045 |
| Forecast (new) | `/WEBAPP/pages/forecast/forecast_dashboard.py` | 1,393 |

### Duplicate Patterns Identified

| Pattern | Est. Duplicate Lines | Reduction Potential |
|---------|---------------------|---------------------|
| Candlestick chart | ~120 | 70% |
| Statistical bands (±1σ, ±2σ) | ~100 | 80% |
| Excel export buttons | ~50 | 95% |
| Metrics cards | ~25 | 100% |
| HTML table styling | ~200 | 60% |
| **Total** | **~495** | **~350 lines** |

---

## Proposed Solutions

### Option A: Component Extraction (Recommended)

Extract shared components:

```
WEBAPP/components/
├── charts/
│   ├── candlestick_distribution.py
│   ├── statistical_bands.py
│   └── dual_axis_chart.py
├── tables/
│   ├── styled_html_table.py
│   └── excel_exporter.py
└── filters/
    └── sidebar_filters.py
```

| Pros | Cons |
|------|------|
| DRY: Giảm ~40% code | Cần 2-3 ngày refactor |
| Fix 1 chỗ = fix everywhere | Có thể break existing |
| Consistent UI/UX | Testing required |

### Option B: Unified Dashboard

Merge sector + valuation vào 1 page:

```
Sector & Valuation Dashboard
├── Tab: Sector Overview
├── Tab: Sector Valuation
├── Tab: Individual Analysis
├── Tab: Macro & Commodity
└── Tab: Data Tables
```

| Pros | Cons |
|------|------|
| Single source of truth | File lớn (2,400+ lines) |
| Better navigation UX | Slow initial load |

### Option C: Forecast Redesign

Consolidate 2 forecast files + improve UX:

```
Forecast Dashboard (Unified)
├── Tab: Summary Cards
├── Tab: Valuation Matrix (NEW)
│   └── TTM vs Forward PE/PB side-by-side
│   └── Premium/Discount to sector
├── Tab: Individual Stocks
├── Tab: Sector Aggregates
└── Tab: Charts
```

---

## Open Questions (Cần trả lời)

### Priority

- [ ] Focus giảm code duplication trước hay Forecast UX trước?

### Forecast Page

- [ ] File nào đang được sử dụng? (old hay new)
- [ ] Merge 2 file hay xoá 1?

### Valuation Matrix

- [ ] Metrics nào cần side-by-side?
  - [ ] PE TTM vs PE FWD 2025 vs PE FWD 2026?
  - [ ] PB TTM vs PB FWD?
  - [ ] Premium/Discount to sector?

### Breaking Changes

- [ ] Có user nào dùng direct URLs?
- [ ] Có thể thay đổi page structure?

### Timeline

- [ ] Deadline?
- [ ] Acceptance criteria?

---

## Next Steps

1. User trả lời Open Questions
2. Finalize approach (A, B, C hoặc hybrid)
3. Tạo implementation plan
4. Execute refactoring

---

## Notes

_Thêm comments/notes ở đây khi review lại:_

```
[2025-12-21] User:
[2025-12-21] Claude:
```
