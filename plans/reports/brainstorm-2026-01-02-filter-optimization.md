# Brainstorm Report: Filter Optimization

**Date:** 2026-01-02
**Topic:** Dashboard Filter Architecture Redesign
**Status:** ✅ All Questions Resolved - Ready for Implementation

---

## 1. Problem Statement

Current filter system has multiple issues:
- Global sidebar filter (quick search) clears after one use - effectively useless
- Inconsistent filter locations: some pages use sidebar, some use header, Forecast uses both
- Copy-paste code: Company/Bank/Security have identical sidebar code (~40 lines x 3)
- No cross-page state: selecting ticker in one page doesn't affect others
- Filter components exist but underutilized
- **Technical dashboard:** Stock Scanner reimplements ~100 lines that `ta_filter_bar.py` already provides
- **Forecast dashboard:** Dual-filter anti-pattern (sidebar + header filters overlap)

**User Pain Point:** Filters không liền mạch, global filter vô dụng, UX confusing

---

## 2. Requirements Gathered

### User Preferences
| Aspect | Decision |
|--------|----------|
| Global filter scope | Entity-specific (banks→bank pages, companies→company pages) |
| Filter UI location | Header-based (not sidebar) |
| Sidebar purpose | Navigation only, no filters |
| Fundamental pages | Share same filter layout (DRY) |
| Fundamental ↔ Forecast | Auto-sync ticker selection |

### User Workflow (Expanded)
```
Gõ ticker ở Company/Bank/Security
→ Xem fundamental data
→ Navigate to Forecast → Auto-highlight ticker với forecast + valuation
→ Navigate to Technical → Single Stock Analysis auto-filled với ticker
```

### Auto-Sync Scope (Finalized)
| Sync Connection | Behavior |
|-----------------|----------|
| **Fundamental → Forecast** | Auto-highlight ticker row in tables |
| **Fundamental → Technical** | Pre-fill Single Stock Analysis input |
| **Fundamental → Sector** | (Optional) Highlight ticker in sector comparison |

---

## 3. Current State Analysis

### Filter Audit Summary

| Page | Current Location | Filter Types | Issues |
|------|-----------------|--------------|--------|
| **Company** | Sidebar | Ticker, Period, Num periods | Duplicated code |
| **Bank** | Sidebar | Ticker, Period, Num periods | Duplicated code |
| **Security** | Sidebar | Ticker, Period, Num periods | Duplicated code |
| **Sector** | Header | Metric, Time range | ✅ Good pattern |
| **Forecast** | Sidebar + Header | Sector, Rating, Sort | Dual filter (confusing) |
| **Technical** | Tab-specific | Timeframe, Sector, Signal | Scattered but functional |
| **FX/Commodities** | Mixed | Commodity, Timeframe | Minimal |

### Code Duplication
- 3 identical sidebar implementations: ~120 lines duplicated
- TIME_RANGE constants defined in 3+ places
- Metric mapping (PE→pe_ttm) hardcoded in multiple files

### Session State Issues
- `quick_search_ticker` cleared after single use
- No shared state between Fundamental and Forecast pages
- Technical dashboard has 30+ session keys (bloated)

---

## 3.5. Complete Filter Audit by Page

### Sector Dashboard ✅ Best Pattern
- **Location:** Header only (uses `render_global_filters()`)
- **Filters:** Metric, Time Range, Refresh
- **Inline selectors:** Sector/Stock selection inside tabs
- **Issues:** None significant - this is the model to follow

### Forecast Dashboard 🔴 Dual-Filter Anti-Pattern
```
SIDEBAR (lines 142-176):
├── Rating (multiselect): STRONG BUY, BUY, HOLD, SELL, N/A
├── Sector (selectbox): All + sector list
├── Sort By (selectbox): Upside, PE, Growth, etc.
└── Refresh button

HEADER (per tab via forecast_filter_bar.py):
├── Sector (AGAIN!)
├── Rating (AGAIN!)
├── Sort (AGAIN!)
└── Extended columns toggle
```
**Problem:** Duplicate filters in sidebar AND header → user confusion

### Technical/Stock Scanner 🔴 Reimplementation Problem
```
ta_filter_bar.py (UNUSED by Stock Scanner):
├── render_ta_filters() - configurable filter bar
├── TIMEFRAME_OPTIONS: {"30D": 30, "60D": 60, ...}
├── SIGNAL_TYPES: {"all": "All Signals", ...}
└── Session state prefixing

stock_scanner.py (REIMPLEMENTS from scratch):
├── scanner_quick_search (text_input)
├── scanner_sector (selectbox)
├── scanner_trend (selectbox) - NEW
├── scanner_days (selectbox) - DIFFERENT FORMAT!
├── scanner_type (selectbox)
├── scanner_direction (selectbox) - NEW
├── scanner_min_strength (slider) - NEW
├── scanner_min_value (slider) - NEW
└── ~100 lines of manual filter code
```
**Problem:** `ta_filter_bar.py` component exists but not used → duplication

### FX/Commodities Dashboard 🟡 Minor Issues
- **Sidebar:** Time Range only (minimal, acceptable)
- **Inline:** Category radio, Exchange/Commodity selectbox
- **Issue:** Timeframe in sidebar (inconsistent with Sector header pattern)

### Summary Table
| Page | Pattern | Filters Location | Severity |
|------|---------|-----------------|----------|
| Company/Bank/Security | Sidebar | Ticker, Period, Slider | 🔴 Duplicate |
| Sector | Header | Metric, Time Range | ✅ Model |
| Forecast | Dual! | Sidebar + Header overlap | 🔴 Confusing |
| Technical (Scanner) | Custom | Reimplements ta_filter_bar | 🔴 Wasteful |
| FX/Commodities | Sidebar+Inline | Time Range + category | 🟡 Minor |

---

## 4. Proposed Architecture

### 4.1 Sidebar Redesign

**BEFORE (Current):**
```
┌─────────────────────┐
│ SIDEBAR             │
├─────────────────────┤
│ Quick Ticker Search │  ← Useless (clears)
│ [Search input]      │
│ [Dropdown]          │
│ [Page buttons]      │
│                     │
│ Page-specific:      │
│ [Ticker selector]   │  ← Duplicated 3x
│ [Period selector]   │
│ [Slider]            │
│ [Refresh]           │
└─────────────────────┘
```

**AFTER (Proposed):**
```
┌─────────────────────┐
│ SIDEBAR             │
├─────────────────────┤
│ Navigation Links    │
│ • Company           │
│ • Bank              │
│ • Security          │
│ • Sector            │
│ • Forecast          │
│ • Technical         │
│ • FX & Commodities  │
│                     │
│ ─────────────────── │
│ Recently Viewed:    │
│ 📍 ACB (Bank)       │  ← Optional indicator
└─────────────────────┘
```

### 4.2 Page Header Filters

**Fundamental Pages (Company/Bank/Security) - Shared Component:**
```
┌────────────────────────────────────────────────────────────┐
│ 🔍 [Ticker ▼ ACB]  [Period ▼ Quarterly]  [Periods: ●──12]  [⟳] │
└────────────────────────────────────────────────────────────┘
```

**Sector Page:**
```
┌────────────────────────────────────────────────────────────┐
│ [Metric ▼ PE]  [Time Range ▼ 1Y]  [⟳ Refresh]              │
└────────────────────────────────────────────────────────────┘
```

**Forecast Page:**
```
┌────────────────────────────────────────────────────────────┐
│ [Sector ▼ All]  [Rating ▼ BUY]  [Sort ▼ Upside]  [⟳]      │
│                                                            │
│ 📍 Viewing: ACB (from Bank page)  [Clear]                  │  ← Auto-sync indicator
└────────────────────────────────────────────────────────────┘
```

**Technical Page:**
```
┌────────────────────────────────────────────────────────────┐
│ [Timeframe ▼ 180D]  [Sector ▼ All]  [Signal ▼ All]  [🔍 Search] │
└────────────────────────────────────────────────────────────┘
```

**FX/Commodities Page:**
```
┌────────────────────────────────────────────────────────────┐
│ [Time Range ▼ 1Y]  [Category ▼ Commodities]  [⟳ Refresh]  │
└────────────────────────────────────────────────────────────┘
```

### 4.3 Shared State Architecture

```python
# WEBAPP/core/session_state.py - New shared state

SHARED_STATE = {
    # Fundamental → Forecast sync
    'last_viewed_ticker': None,      # "ACB"
    'last_viewed_entity': None,      # "BANK"
    'last_viewed_sector': None,      # "Ngân hàng"
    'last_viewed_timestamp': None,   # datetime
}

# Usage in Fundamental pages:
def on_ticker_change(ticker, entity_type, sector):
    st.session_state['last_viewed_ticker'] = ticker
    st.session_state['last_viewed_entity'] = entity_type
    st.session_state['last_viewed_sector'] = sector

# Usage in Forecast page:
def get_synced_ticker():
    return st.session_state.get('last_viewed_ticker')
```

### 4.4 Component Structure

```
WEBAPP/components/filters/
├── __init__.py
├── fundamental_filter_bar.py    # NEW: Shared for Company/Bank/Security
├── sector_filter_bar.py         # Refactor from global_filter_bar.py
├── forecast_filter_bar.py       # Existing (keep, add sync indicator)
├── technical_filter_bar.py      # Move from pages/technical/components/
└── constants.py                 # NEW: Centralized TIME_RANGE, METRICS, etc.
```

---

## 5. Implementation Plan (Revised)

### Phase 1: Foundation (1-2 days)
1. Create `WEBAPP/components/filters/constants.py` - centralize filter constants (TIMEFRAME_OPTIONS, SIGNAL_TYPES, PERIOD_OPTIONS, etc.)
2. Update `WEBAPP/core/session_state.py` - add shared state keys for auto-sync
3. Remove global ticker search from `main_app.py` sidebar

### Phase 2: Fundamental Pages (2-3 days)
1. Create `fundamental_filter_bar.py` component (shared for Company/Bank/Security)
2. Refactor Company page - move sidebar filters to header
3. Refactor Bank page - use shared component
4. Refactor Security page - use shared component
5. Implement `on_ticker_change` callback to update shared state

### Phase 3: Auto-Sync Integration (1-2 days)
1. **Forecast sync:**
   - Read `last_viewed_ticker` and **highlight row** in tables
   - Add sync indicator banner "📍 Viewing: ACB (from Bank page)"
   - Add "Clear" button to reset sync
2. **Technical sync:**
   - Pre-fill Single Stock Analysis input with `last_viewed_ticker`
   - Show indicator "(synced from Fundamental)"

### Phase 4: Technical Filter Consolidation (2 days)
1. Extend `ta_filter_bar.py` with new options (or create `scanner_filter_bar.py` in same folder if too long):
   - `show_trend`: Trend filter (UPTREND/DOWNTREND/SIDEWAYS)
   - `show_direction`: Direction filter (BUY/SELL/PULLBACK/BOUNCE)
   - `show_strength_slider`: Min strength slider
   - `show_value_slider`: Min GTGD slider
2. Refactor `stock_scanner.py` to USE the filter bar component instead of reimplementing
3. Remove ~100 lines of duplicate filter code

### Phase 5: Forecast Filter Cleanup (1 day)
1. Remove sidebar filters from `forecast_dashboard.py` (lines 142-180)
2. Keep header filters only via `forecast_filter_bar.py`
3. Ensure header filters work properly after sidebar removal

### Phase 6: FX/Commodities + Final Cleanup (1 day)
1. Move FX/Commodities timeframe from sidebar to header
2. Delete unused `valuation_filters.py` (if confirmed unused)
3. Update `session_state.py` to remove obsolete keys
4. Document new filter architecture in `docs/`

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Streamlit rerun clears state | Medium | High | Use `st.session_state` properly with callbacks |
| Auto-sync confuses users | Low | Medium | Add clear visual indicator + "Clear" button |
| Breaking existing functionality | Medium | High | Test each page thoroughly after refactor |
| Technical page has 30+ keys | Low | Low | Phase out gradually, don't break existing |

---

## 6.5. Scalability Design Patterns

### Hạn chế tiềm ẩn & Giải pháp

| Issue | Mitigation | Implementation |
|-------|------------|----------------|
| Filter bar quá nhiều options | Tách Basic/Advanced | `render_filter_bar(mode='basic'\|'advanced')` |
| Session state bloated | Namespace prefix | Keys: `sync_*`, `filter_*`, `page_*` |
| Complex filter dependencies | Callback pattern | `on_change` callbacks, không dùng observer |
| Scale thêm entity types | Config-driven | Filter bar nhận `entity_config` dict |

### Session State Namespace Convention

```python
# WEBAPP/core/session_state.py - Namespace prefixes

SYNC_STATE_KEYS = {
    'sync_last_ticker': None,       # Cross-page ticker sync
    'sync_last_entity': None,       # "BANK", "COMPANY", etc.
    'sync_last_sector': None,       # Sector name
    'sync_timestamp': None,         # When synced
}

FILTER_STATE_KEYS = {
    'filter_period': 'Quarterly',   # Shared period preference
    'filter_num_periods': 8,        # Shared periods count
    'filter_timeframe': '1Y',       # Shared timeframe
}
```

### Filter Bar Mode Pattern

```python
# fundamental_filter_bar.py

def render_fundamental_filters(
    service,
    mode: str = 'basic',           # 'basic' | 'advanced'
    entity_type: str = 'company',  # 'company' | 'bank' | 'security'
    show_sync_indicator: bool = False,
) -> Dict:
    """
    Basic mode: Ticker + Period + Refresh
    Advanced mode: + Comparison + Export + Date range
    """
    if mode == 'basic':
        return _render_basic_filters(service, entity_type)
    else:
        return _render_advanced_filters(service, entity_type)
```

### Scale Pattern: Adding New Entity Type

```python
# Thêm Insurance page - chỉ cần config, không cần code mới

ENTITY_CONFIGS = {
    'company': {'default_ticker': 'VNM', 'period_options': ['Quarterly', 'Yearly']},
    'bank': {'default_ticker': 'VCB', 'period_options': ['Quarterly', 'Yearly']},
    'security': {'default_ticker': 'SSI', 'period_options': ['Quarterly', 'Yearly']},
    'insurance': {'default_ticker': 'BVH', 'period_options': ['Quarterly', 'Yearly']},  # NEW
}

# Usage in Insurance page:
filters = render_fundamental_filters(service, entity_type='insurance')
```

---

## 7. Success Metrics

| Metric | Before | After |
|--------|--------|-------|
| Lines of duplicated filter code | ~120 | 0 |
| Filter constants definitions | 3+ places | 1 place |
| Cross-page ticker sync | None | Automatic |
| Sidebar filter confusion | High | None (removed) |
| User clicks to view ticker forecast | 3+ (search, select, navigate) | 1 (just navigate) |

---

## 8. Files to Modify

### Create New
- `WEBAPP/components/filters/constants.py` - Centralized filter constants (TIMEFRAME, SIGNAL_TYPES, PERIOD, etc.)
- `WEBAPP/components/filters/fundamental_filter_bar.py` - Shared for Company/Bank/Security

### Modify (Foundation)
- `WEBAPP/core/session_state.py` - Add shared state keys (last_viewed_ticker, etc.)
- `WEBAPP/main_app.py` - Remove global search, simplify sidebar

### Modify (Fundamental + Sync)
- `WEBAPP/pages/company/company_dashboard.py` - Move filters to header + sync callback
- `WEBAPP/pages/bank/bank_dashboard.py` - Move filters to header + sync callback
- `WEBAPP/pages/security/security_dashboard.py` - Move filters to header + sync callback
- `WEBAPP/pages/forecast/forecast_dashboard.py` - Add sync indicator + remove sidebar filters
- `WEBAPP/pages/technical/components/stock_scanner.py` - Pre-fill from sync state

### Modify (Technical Consolidation)
- `WEBAPP/pages/technical/components/ta_filter_bar.py` - Add trend/direction/slider options
- `WEBAPP/pages/technical/components/stock_scanner.py` - Use ta_filter_bar instead of manual

### Modify (FX/Commodities)
- `WEBAPP/pages/fx_commodities/fx_commodities_dashboard.py` - Move timeframe to header

### Potentially Delete
- `WEBAPP/components/filters/valuation_filters.py` - 455 lines, appears unused

---

## 9. Resolved Questions

| # | Question | Decision |
|---|----------|----------|
| 1 | **Forecast dual-filter** | ✅ Move to header (remove sidebar filters) |
| 2 | **FX/Commodities timeframe** | ✅ Move to header (consistent with Sector pattern) |
| 3 | **"Recently Viewed" in sidebar** | ⏳ TBD - defer to implementation |
| 4 | **Forecast sync scope** | ✅ Highlight row (not filter table) |
| 5 | **Technical Scanner filters** | ✅ Extend `ta_filter_bar.py`, or create new file in same folder if too long |
| 6 | **Constants location** | ✅ Create new `WEBAPP/components/filters/constants.py` (separate for easier control) |

---

## 10. Next Steps

1. User confirms this report
2. Create implementation plan (`/plan` command)
3. Execute phased implementation
4. Test each phase before proceeding

---

## 11. Effort Estimate Summary

| Phase | Scope | Effort |
|-------|-------|--------|
| Phase 1: Foundation | Constants, session state, remove global search | 1-2 days |
| Phase 2: Fundamental Pages | Create shared filter bar, refactor 3 pages | 2-3 days |
| Phase 3: Auto-Sync | Forecast + Technical sync integration | 1-2 days |
| Phase 4: Technical Consolidation | Extend ta_filter_bar, refactor stock_scanner | 2 days |
| Phase 5: Forecast Cleanup | Remove duplicate sidebar filters | 1 day |
| Phase 6: Final Cleanup | FX timeframe, delete unused, docs | 1 day |
| **TOTAL** | | **8-11 days** |

### Code Impact
- **Lines to remove:** ~270 (120 sidebar duplicate + 100 scanner + 50 forecast)
- **Lines to add:** ~150 (new components + sync logic)
- **Net reduction:** ~120 lines

---

**Report Author:** Claude (Brainstormer Agent)
**Consensus:** ✅ Reached with user on 2026-01-02
**Last Updated:** 2026-01-02 (All questions resolved - decisions finalized)
