# TA Dashboard Plan - Review Report

**Date:** 2025-12-25
**Reviewer:** Claude Code
**Status:** ✅ All Issues Fixed

---

## Executive Summary

Đã review toàn bộ 5 phase files. Phát hiện **7 issues chính** - **TẤT CẢ ĐÃ ĐƯỢC FIX**.

| Category | Issues Found | Priority | Status |
|----------|-------------|----------|--------|
| Code Duplication | 3 | HIGH | ✅ FIXED |
| Data Loading | 2 | HIGH | ✅ FIXED |
| Filter Sync | 1 | MEDIUM | ✅ FIXED |
| Calculation Consolidation | 1 | MEDIUM | ✅ FIXED |

**Fixes Applied:**
- phase-01-market-state.md: Added TA Indicator base classes, caching decorators, singleton pattern
- phase-05-integration.md: Added filter sync pattern, updated component signatures

---

## 1. CODE DUPLICATION Issues 🔴

### 1.1 TADashboardService instantiation repeated

**Problem:** Mỗi component đều khởi tạo `service = TADashboardService()` riêng.

**Locations:**
- `phase-02-market-overview-tab.md:69` - `render_market_overview()`
- `phase-03-sector-rotation-tab.md:72` - `render_sector_rotation()`
- `phase-04-scanner-lists-tabs.md` - `render_stock_scanner()`

**Fix:** Pass service từ main dashboard, không tạo mới trong mỗi component.

```python
# BAD (current)
def render_market_overview():
    service = TADashboardService()  # New instance each time!

# GOOD (proposed)
def render_market_overview(service: TADashboardService):
    # Use passed instance
```

---

### 1.2 Sector list loaded multiple times

**Problem:** `get_sector_list()` được gọi ở nhiều nơi:
- Phase 3: RS Heatmap filter
- Phase 4: Stock Scanner sector filter

**Fix:** Load một lần trong service, cache với `@st.cache_data`.

---

### 1.3 Quadrant calculation duplicated

**Problem:** Quadrant logic (`LEADING/WEAKENING/LAGGING/IMPROVING`) xuất hiện ở:
- `phase-03-sector-rotation-tab.md` - `calculate_stock_rs_for_rrg()`
- `phase-02-sector-layer.md` (reference plan)

**Fix:** Extract thành utility function trong `PROCESSORS/technical/indicators/quadrant.py`.

```python
def determine_quadrant(rs_ratio: float, rs_momentum: float) -> str:
    """Common quadrant determination logic"""
    if rs_ratio > 1 and rs_momentum > 0:
        return 'LEADING'
    elif rs_ratio > 1 and rs_momentum <= 0:
        return 'WEAKENING'
    elif rs_ratio <= 1 and rs_momentum <= 0:
        return 'LAGGING'
    else:
        return 'IMPROVING'
```

---

## 2. DATA LOADING Issues 🔴

### 2.1 No caching strategy defined

**Problem:** Service methods không có `@st.cache_data` decorator.

**Locations:**
- `phase-01-market-state.md:176-192` - `_load_*` methods

**Fix:** Add caching với TTL:

```python
class TADashboardService:
    @staticmethod
    @st.cache_data(ttl=300)  # 5 min cache
    def _load_market_breadth():
        return pd.read_parquet(...)

    @staticmethod
    @st.cache_data(ttl=60)  # 1 min for signals
    def _load_signals():
        return pd.read_parquet(...)
```

---

### 2.2 Lazy loading not implemented

**Problem:** Plan nói "lazy loading" nhưng code load tất cả trong `__init__`.

**Current flow:**
```
Page load → TADashboardService() → Load ALL data → Show Tab 1
```

**Expected flow:**
```
Page load → Show Tab 1 only
Click Tab 2 → Load Tab 2 data
```

**Fix:** Remove `__init__` preloading, use on-demand loading:

```python
class TADashboardService:
    def __init__(self):
        # DON'T preload here
        pass

    def get_market_state(self):
        # Load on demand
        vnindex = self._load_vnindex()  # Cached
        ...
```

---

## 3. FILTER SYNC Issues 🟡

### 3.1 Filters not synced across tabs

**Problem:** Sector filter ở Tab 3 (Scanner) và Tab 2 (RS Heatmap) là independent.

**Current:**
```
Tab 2: Sector = "Ngân hàng" (independent)
Tab 3: Sector = "All" (independent)
```

**Expected:**
```
Tab 2: Sector = "Ngân hàng"
Tab 3: Auto-sync to "Ngân hàng" (or keep last selection)
```

**Fix:** Use `st.session_state` for shared filters:

```python
# In main dashboard
if 'selected_sector' not in st.session_state:
    st.session_state.selected_sector = "All"

# In each component
sector = st.selectbox(
    "Sector",
    options,
    index=options.index(st.session_state.selected_sector),
    key="sector_filter"
)
st.session_state.selected_sector = sector
```

---

## 4. CALCULATION CONSOLIDATION 🟡

### 4.1 TA Calculations scattered across files

**Problem:** Các công thức tính toán nằm rải rác:
- RS Ratio: `phase-03-sector-rotation-tab.md`
- RS Rating: `phase-03-sector-rotation-tab.md`
- Confidence Score: `phase-04-scanner-lists-tabs.md`
- Sector Score: `phase-02-sector-layer.md`

**Fix:** Consolidate vào class hierarchy:

```
PROCESSORS/technical/indicators/
├── __init__.py
├── base.py              # TAIndicator base class
├── relative_strength.py # RSRatioCalculator, RSRatingCalculator
├── sector_score.py      # SectorScoreCalculator
├── confidence.py        # ConfidenceScoreCalculator
├── quadrant.py          # QuadrantDeterminer
├── volume_context.py    # VolumeContextAnalyzer
└── candlestick_patterns.py
```

**Base class pattern:**

```python
# base.py
from abc import ABC, abstractmethod

class TAIndicator(ABC):
    """Base class for all TA indicators"""

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_latest(self, df: pd.DataFrame) -> dict:
        pass
```

---

## 5. UI/UX Compliance Check ✅

| Rule | Status | Notes |
|------|--------|-------|
| Use Plotly (not matplotlib) | ✅ | All charts use `go.Figure` |
| Responsive layout | ✅ | `st.columns`, `use_container_width=True` |
| Dark/Light mode | ⚠️ | Need verify `rgba(0,0,0,0)` backgrounds work |
| Vietnamese labels | ✅ | Phase 4 uses tiếng Việt |
| Progress columns for scores | ✅ | Phase 4 uses `ProgressColumn` |

---

## 6. Recommended Changes

### Priority 1 (Before Implementation)

1. **Create shared service instance pattern**
   - Pass `TADashboardService` from main to all components
   - Add `@st.cache_resource` for service singleton

2. **Add caching decorators**
   - `@st.cache_data(ttl=300)` for market/sector data
   - `@st.cache_data(ttl=60)` for signal data

3. **Extract quadrant logic**
   - Create `PROCESSORS/technical/indicators/quadrant.py`
   - Import in both sector and stock RRG calculations

### Priority 2 (During Implementation)

4. **Implement session state for filters**
   - Add `st.session_state.selected_sector`
   - Sync across Tab 2 and Tab 3

5. **Create indicator class hierarchy**
   - Base class with `calculate()` and `get_latest()`
   - Consistent interface for all calculators

---

## 7. Action Items

| # | Task | File to Update | Effort |
|---|------|----------------|--------|
| 1 | Add service singleton pattern | phase-05-integration.md | 30 min |
| 2 | Add caching decorators | phase-01-market-state.md | 15 min |
| 3 | Extract quadrant function | NEW: phase-01-market-state.md | 20 min |
| 4 | Add session state filters | phase-05-integration.md | 20 min |
| 5 | Update component signatures | phase-02, phase-03, phase-04 | 30 min |
| 6 | Create indicator base class | phase-01-market-state.md | 45 min |

**Total estimated effort:** ~2.5 hours

---

## Appendix: Data Flow Diagram (Proposed)

```
┌─────────────────────────────────────────────────────────────────────┐
│                      technical_dashboard.py                          │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  service = get_ta_service()  # Singleton, cached             │   │
│  │  st.session_state.sector = "All"  # Shared filter            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│         ┌────────────────────┼────────────────────┐                 │
│         ▼                    ▼                    ▼                 │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐         │
│  │   Tab 1     │      │   Tab 2     │      │   Tab 3     │         │
│  │  Market     │      │  Sector     │      │  Scanner    │         │
│  │             │      │             │      │             │         │
│  │ service →   │      │ service →   │      │ service →   │         │
│  │ session →   │      │ session →   │      │ session →   │         │
│  └─────────────┘      └─────────────┘      └─────────────┘         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     TADashboardService                               │
│                                                                      │
│  @st.cache_data(ttl=300)                                            │
│  ├── get_market_state()                                             │
│  ├── get_breadth_history()                                          │
│  ├── get_sector_ranking()                                           │
│  └── ...                                                            │
│                                                                      │
│  Uses:                                                               │
│  ├── RSRatioCalculator                                              │
│  ├── RSRatingCalculator                                             │
│  ├── SectorScoreCalculator                                          │
│  ├── ConfidenceScoreCalculator                                      │
│  └── VolumeContextAnalyzer                                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     DATA/processed/technical/                        │
│                                                                      │
│  market_breadth/market_breadth_daily.parquet     # ~500KB           │
│  vnindex/vnindex_indicators.parquet              # ~100KB           │
│  sector_breadth/sector_breadth_daily.parquet     # ~200KB           │
│  alerts/daily/combined_latest.parquet            # ~1MB             │
│  rs_rating/stock_rs_rating_daily.parquet         # ~2MB             │
└─────────────────────────────────────────────────────────────────────┘
```

---

**End of Report**
