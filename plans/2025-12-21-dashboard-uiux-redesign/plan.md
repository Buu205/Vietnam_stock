# Dashboard UI/UX Redesign Plan

**Goal:** Maximize chart viewport, minimize interaction friction, chart-first layout
**Status:** Completed (Core) | **Priority:** High
**Updated:** 2025-12-21

**Summary:** All core phases completed. Sector dashboard refactored with global filter bar. Company/Bank dashboards optional.

---

## Problem Statement
1. Sidebar occupies ~300px (15% of viewport) - reduces chart area
2. Filter duplication: sidebar filters + inline tab filters (sector_dashboard.py)
3. 2+ clicks to see data: expand sidebar → select filter → view chart
4. Not chart-first: filters dominate visual hierarchy

## Solution: Collapsed Sidebar + Top Filter Bar

### Phase 0: Chart Schema Consolidation
- [x] **Status:** Completed
- Created `WEBAPP/core/chart_schema.py` - unified chart configuration
- Merged valuation_config.py and chart_config.py into single source
- ChartType enum, ChartSchema dataclass, CHART_REGISTRY

### Phase 1: Sidebar Collapse (1 day)
- [x] **Status:** Completed
- **File:** [phase-01-sidebar-collapse.md](./phase-01-sidebar-collapse.md)
- Changed `initial_sidebar_state="collapsed"` in main_app.py:37
- Added compact sidebar CSS with smooth transitions
- Navigation works via hamburger icon

### Phase 2: Filter Consolidation (2 days)
- [x] **Status:** Completed
- **File:** [phase-02-filter-consolidation.md](./phase-02-filter-consolidation.md)
- Created `WEBAPP/components/filters/global_filter_bar.py`
- Horizontal filter bar component with metric/time_range/refresh
- Added sticky filter bar CSS to styles.py
- Session state integration for filter persistence

### Phase 3: Chart-First Layout (1 day)
- [x] **Status:** Completed
- **File:** [phase-03-chart-first-layout.md](./phase-03-chart-first-layout.md)
- Reduced block-container padding (2.5rem → 1.5rem)
- Compact metric cards (1.5rem → 1rem padding)
- Compact tabs (0.65rem → 0.5rem padding)
- Reduced chart wrapper padding (1rem → 0.5rem)
- Updated get_chart_layout() with tighter margins

### Phase 4: Page Organization (3-4 days)
- [x] **Status:** Completed (Sector Dashboard)
- **File:** [phase-04-page-organization.md](./phase-04-page-organization.md)
- Refactored sector_dashboard.py to use global_filter_bar
- Removed duplicate sidebar filters
- Horizontal filter bar at top of page
- Remaining: Company/Bank dashboard flattening (optional)

### Phase 5: Advanced Visualizations (5-7 days)
- [x] **Status:** Completed (Components Created)
- **File:** [phase-05-advanced-visualizations.md](./phase-05-advanced-visualizations.md)
- Created `WEBAPP/components/charts/advanced_charts.py`
- Heatmap: sector_correlation_heatmap()
- Treemap: market_cap_treemap()
- Waterfall: pnl_waterfall()
- Bullet chart: bullet_chart()
- Radar chart: radar_comparison()
- Gauge chart: gauge_chart()
- Sparklines: sparkline()
- Sunburst: sunburst_allocation()

---

## Files Modified/Created
| File | Status | Changes |
|------|--------|---------|
| `WEBAPP/main_app.py` | Modified | `initial_sidebar_state="collapsed"` |
| `WEBAPP/core/styles.py` | Modified | Compact sidebar CSS, sticky filter header, chart-first layout |
| `WEBAPP/core/chart_schema.py` | **NEW** | Unified chart config schema (17 chart types), legacy HistogramConfig |
| `WEBAPP/components/filters/global_filter_bar.py` | **NEW** | Horizontal filter component |
| `WEBAPP/components/charts/advanced_charts.py` | **NEW** | 8 advanced chart functions |
| `WEBAPP/components/charts/__init__.py` | Modified | Export advanced charts |
| `WEBAPP/components/charts/valuation_charts.py` | **FIXED** | Updated histogram_with_stats() to use ChartSchema colors dict |
| `WEBAPP/pages/sector/sector_dashboard.py` | **Modified** | Uses global_filter_bar, removed sidebar filters |
| `WEBAPP/pages/company/company_dashboard.py` | Pending | Flatten tabs, add KPI row |
| `WEBAPP/pages/bank/bank_dashboard.py` | Pending | Flatten tabs, add radar chart |

## Constraints
- Keep dark OLED theme (no color changes)
- Streamlit limitations: no custom HTML layout
- Mobile not priority (desktop focus)
- sector_dashboard.py as template for other pages

## Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Content Width | ~1500px | ~1800px |
| Clicks to Data | 2+ | 0-1 |
| Sidebar State | expanded | collapsed |
| Nested Tab Depth | 2-3 levels | 1 level |
| Chart Types | 5 basic | 13 advanced |
| KPI Card Visibility | scroll required | above fold |
| Page Load Time | ~2s | <1.5s |

## Total Effort Estimate
| Phase | Effort | Risk |
|-------|--------|------|
| Phase 1: Sidebar Collapse | 1 day | Low |
| Phase 2: Filter Consolidation | 2 days | Medium |
| Phase 3: Chart-First Layout | 1 day | Low |
| Phase 4: Page Organization | 3-4 days | Medium |
| Phase 5: Advanced Visualizations | 5-7 days | Medium-High |
| **Total** | **12-15 days** | **Medium** |

---

## Unresolved Questions
1. Should global filters persist across page navigation? (Recommend: Yes)
2. Real-time filter updates vs "Apply" button? (Recommend: Real-time)
3. Keep sidebar ticker search or move to top bar? (Recommend: Move to top)
4. Which advanced charts to implement first? (Recommend: Heatmap → Treemap → Waterfall)
5. Should sparklines be inline with tables or separate? (Recommend: Inline)
6. Use TradingView Lightweight Charts for candlestick? (Recommend: Stick with Plotly for consistency)
