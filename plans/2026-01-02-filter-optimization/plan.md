# Implementation Plan: Filter Optimization

**Created:** 2026-01-02
**Source:** `plans/reports/brainstorm-2026-01-02-filter-optimization.md`
**Status:** Ready for Implementation
**Effort:** 8-11 days (6 phases)

---

## Overview

Refactor dashboard filter architecture to:
1. Move all filters from sidebar to header (consistent UX)
2. Create shared filter components (DRY)
3. Implement cross-page ticker sync (Fundamental → Forecast/Technical)
4. Eliminate ~270 lines of duplicate code

## Phases

| Phase | Name | Effort | Files | Dependencies |
|-------|------|--------|-------|--------------|
| 1 | [Foundation](phase-01-foundation.md) | 1-2 days | 3 | None |
| 2 | [Fundamental Pages](phase-02-fundamental-pages.md) | 2-3 days | 4 | Phase 1 |
| 3 | [Auto-Sync](phase-03-auto-sync.md) | 1-2 days | 3 | Phase 2 |
| 4 | [Technical Consolidation](phase-04-technical-consolidation.md) | 2 days | 2 | Phase 1 |
| 5 | [Forecast Cleanup](phase-05-forecast-cleanup.md) | 1 day | 2 | Phase 3 |
| 6 | [Final Cleanup](phase-06-final-cleanup.md) | 1 day | 3 | All |

## Architecture

### Before
```
SIDEBAR                          HEADER
├── Global ticker search         └── (empty or page-specific)
├── Company filters (40 lines)
├── Bank filters (40 lines)
├── Security filters (40 lines)
└── Forecast filters (duplicate)
```

### After
```
SIDEBAR                          HEADER
├── Navigation only              ├── fundamental_filter_bar.py (shared)
└── Recently viewed indicator    ├── forecast_filter_bar.py
                                 ├── ta_filter_bar.py (extended)
                                 └── fx_filter_bar.py (new)
```

### New Files
```
WEBAPP/components/filters/
├── constants.py                 # NEW: Centralized filter constants
├── fundamental_filter_bar.py    # NEW: Shared for Company/Bank/Security
└── (existing files)
```

## Scalability Design

### Namespace Convention
```python
SYNC_STATE_KEYS = {'sync_last_ticker', 'sync_last_entity', 'sync_last_sector'}
FILTER_STATE_KEYS = {'filter_period', 'filter_num_periods', 'filter_timeframe'}
```

### Filter Bar Modes
```python
render_fundamental_filters(service, mode='basic')    # Ticker + Period + Refresh
render_fundamental_filters(service, mode='advanced') # + Comparison + Export
```

### Entity Config Pattern
```python
ENTITY_CONFIGS = {
    'company': {'default_ticker': 'VNM', 'service': 'CompanyService'},
    'bank': {'default_ticker': 'VCB', 'service': 'BankService'},
    'security': {'default_ticker': 'SSI', 'service': 'SecurityService'},
}
```

## Success Criteria

| Metric | Before | After |
|--------|--------|-------|
| Duplicated filter code | ~270 lines | 0 |
| Filter constants locations | 3+ places | 1 place |
| Cross-page ticker sync | None | Automatic |
| User clicks for forecast | 3+ | 1 (navigate) |

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Streamlit rerun clears state | Use `st.session_state` with callbacks |
| Auto-sync confuses users | Visual indicator + "Clear" button |
| Breaking existing functionality | Test each page after phase |

## Testing Strategy

Each phase requires:
1. **Manual test:** Dashboard loads without errors
2. **Filter test:** All filters work correctly
3. **Sync test:** Cross-page navigation maintains state
4. **Visual test:** UI looks correct (no layout breaks)

---

## Quick Start

```bash
# After each phase, test with:
streamlit run WEBAPP/main_app.py

# Check for import errors:
python3 -c "from WEBAPP.components.filters import constants"
```

## References

- Brainstorm: `plans/reports/brainstorm-2026-01-02-filter-optimization.md`
- Model pattern: `WEBAPP/pages/sector/sector_dashboard.py` (uses render_global_filters)
- Existing filter bar: `WEBAPP/pages/technical/components/ta_filter_bar.py`
