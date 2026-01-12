# Brainstorm Report: Forecast Dashboard Refactor

**Date:** 2025-12-30
**Topic:** BSC Forecast Dashboard UI/UX Optimization
**Status:** ✅ Planning Complete

---

## 📋 Related Documents

| Document | Purpose |
|----------|---------|
| **This file** | Problem analysis, pros/cons, initial proposals |
| [**Implementation Plan**](../2025-12-30-forecast-dashboard-refactor/plan.md) | Detailed implementation with phases |
| [**Phase 1: Core UX**](../2025-12-30-forecast-dashboard-refactor/phase-01-core-ux.md) | Unified table + Achievement cards |

---

## 1. Problem Statement

Current Forecast Dashboard (`WEBAPP/pages/forecast/forecast_dashboard.py`) có nhiều issues:

1. **Tab/View Fragmentation**: Valuation View vs Earnings View tách riêng → user phải click nhiều lần
2. **Column Duplication**: `Symbol`, `Sector`, `Rating` xuất hiện ở cả 2 tables
3. **Sector Aggregation Thiếu**: Chưa có BSC Universal so sánh tổng lợi nhuận vs sector
4. **Chart Visualization Chưa Tập Trung**: Candlestick TTM vs FWD chưa trực quan
5. **9M Achievement Summary**: Chỉ có table, thiếu quick-glance cards cho revision signals
6. **Filter Conflict**: Sidebar filter vs in-page filter không đồng bộ
7. **VCI Consensus Data**: Có data nhưng chưa integrate để compare BSC vs VCI

---

## 2. Data Analysis

### 2.1 BSC Data Structure (92 stocks, 15 sectors)

**bsc_individual.parquet columns:**
- Valuation: `pe_fwd_2025`, `pe_fwd_2026`, `pb_fwd_2025`, `pb_fwd_2026`, `roe_2025f`
- Earnings: `rev_2025f`, `rev_2026f`, `npatmi_2025f`, `npatmi_2026f`, `npatmi_growth_yoy_2026`
- Target: `target_price`, `current_price`, `upside_pct`, `rating`
- Achievement: `rev_achievement_pct`, `npatmi_achievement_pct`

### 2.2 VCI Consensus Data (83 stocks)

**vci_coverage_universe.parquet columns:**
- `ticker`, `sector`, `targetPrice`, `rating`
- `pe_2025F`, `pe_2026F`, `pb_2025F`, `pb_2026F`
- `npatmi_2025F`, `npatmi_2026F`, `npatmiGrowth_2025F`, `npatmiGrowth_2026F`
- `roe_2025F`, `roe_2026F`
- `projectedTsrPercentage`, `analyst`

### 2.3 Overlap Analysis

VCI có 83 stocks, BSC có 92 stocks → ~70-75 overlap có thể dùng để compare.

---

## 3. Proposed Solutions

### 3.1 Unified Table Design (Problem 1, 2)

**Current:** 2 tabs (Valuation View / Earnings View) với duplicate columns

**Proposed:** Single unified table với collapsible column groups

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ STOCK INFO      │ VALUATION          │ EARNINGS            │ STATUS            │
├────────────────-┼────────────────────┼─────────────────────┼───────────────────┤
│ Symbol │ Sector │ PE 25F │ PE 26F │ PB 25F │ NPATMI 25F │ NPATMI 26F │ Gr% │ Upside │ Rating│
│ ACB    │ Banks  │ 7.0x   │ 5.9x   │ 1.2x   │ 17.8T      │ 21.0T      │+18% │ +39%   │ BUY   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Column Groups (hover để expand):**
- **Core**: Symbol, Sector, Rating, Upside
- **Valuation**: PE 25F, PE 26F, PB 25F, PB 26F
- **Earnings**: NPATMI 25F, 26F, Growth
- **Extended** (toggle): Revenue, ROE, Target Price, Market Cap

**Implementation Approach:**
- Use st.expander or custom CSS column groups
- Default show: Symbol, PE 25F/26F, NPATMI 25F/26F, Upside, Rating
- Toggle for full columns

---

### 3.2 Quick Action Cards for 9M Achievement (Problem 4)

**Current:** Full table with all stocks

**Proposed:** Summary cards above table

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ 🔼 REVISE UP     │  │ ✓ ON TRACK      │  │ 🔻 REVISE DOWN   │
│ 8 stocks         │  │ 45 stocks        │  │ 12 stocks        │
│ Achievement >90% │  │ 75-90%           │  │ < 75%            │
│                  │  │                  │  │                  │
│ CTG, VCB, ACB... │  │                  │  │ HPG, VNM...      │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

**Thresholds (configurable):**
- **Revise Up**: achievement > 90% (over-performing)
- **On Track**: 75-90%
- **Revise Down**: < 75%

**Clickable cards** → filter table to show only that category

---

### 3.3 Sector Aggregation with BSC Universal (Problem 2)

**Current:** Sector table có PE/PB FWD nhưng chưa có:
- Tổng NPATMI của ngành
- So sánh với BSC Universal (benchmark)

**Proposed Enhancement:**

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ SECTOR     │ STOCKS │ TOT NPATMI 25F │ TOT NPATMI 26F │ GR% │ PE 25F │ vs Universe │ UPSIDE│
├────────────┼────────┼────────────────┼────────────────┼─────┼────────┼─────────────┼───────┤
│ BSC UNIV   │ 92     │ 235.5T         │ 298.7T         │+27% │ 11.2x  │ Benchmark   │ +18%  │ ← Highlighted
│ Banks      │ 15     │ 125.3T         │ 155.8T         │+24% │ 8.5x   │ -24% PE     │ +22%  │
│ Real Est   │ 12     │ 42.5T          │ 58.2T          │+37% │ 14.2x  │ +27% PE     │ +15%  │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

**"vs Universe"** column: PE sector / PE Universal - 1 → negative = cheaper than market

---

### 3.4 Enhanced Candlestick/Box Chart for TTM vs FWD (Problem 3)

**Current:** Valuation Matrix có box plot nhưng:
- Chỉ có 1 forward marker (2025)
- Legend khó hiểu

**Proposed Enhancement:**

```
                    TTM vs FWD 2025 vs FWD 2026
                         Historical Distribution
    │
 30 ├─────────────────┬──────●────────────────────  ← TTM (circle)
    │                 │ ◆    │                        ← FWD 2026 (diamond purple)
 25 ├─────────────────│──◇───┤                        ← FWD 2025 (diamond amber)
    │                 ├──────┤ ← P25-P75 Box
 20 ├─────────────────│      │
    │                 │      │
 15 ├─────────────────┼──────┘
    │     ┌──────┬────┴──────────┐
    └─────ACB────BID─────CTG─────VCB────
```

**Visual Hierarchy:**
- **Circle (●)**: TTM - current trailing PE
- **Diamond Amber (◇)**: FWD 2025
- **Diamond Purple (◆)**: FWD 2026
- **Box**: Historical P25-P75

**Trend Arrow**: If FWD 2026 < FWD 2025 < TTM → Green arrow down (improving)

---

### 3.5 BSC vs VCI Consensus Comparison (Problem 7)

**NEW TAB: "Consensus Compare"**

#### 3.5.1 Table View

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ SYMBOL │ SECTOR │ BSC TP │ VCI TP │ TP Diff │ BSC NPATMI 25F │ VCI NPATMI 25F │ NPATMI Diff │ Consensus │
├────────┼────────┼────────┼────────┼─────────┼────────────────┼────────────────┼─────────────┼───────────┤
│ ACB    │ Banks  │ 33,000 │ 33,300 │ -0.9%   │ 17,872B        │ 17,872B        │ 0.0%        │ ALIGNED   │
│ VCB    │ Banks  │ 108K   │ 95K    │ +13.7%  │ 45,200B        │ 42,000B        │ +7.6%       │ BSC BULL  │
│ HPG    │ Steel  │ 28K    │ 32K    │ -12.5%  │ 15,000B        │ 18,500B        │ -18.9%      │ VCI BULL  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Consensus Classification:**
- **ALIGNED**: TP diff < 5% AND NPATMI diff < 10%
- **BSC BULL**: BSC TP > VCI TP by >5%
- **VCI BULL**: VCI TP > BSC TP by >5%
- **DIVERGENT**: NPATMI forecasts differ >20%

#### 3.5.2 Scatter Plot: Target Price Comparison

```
                VCI Target Price (VND)
    50K ├───────────────────────────────────●VCB (BSC Bull)
        │                              ●
    40K ├──────────────────────────●───────
        │                     ●       ●
    30K ├─────────────────●───────────────── ← 45° line (perfect alignment)
        │            ●  ●  ●
    20K ├───────●──●────────────────────────
        │     ●●
    10K ├──●●───────────────────────────────
        │
        └───┬───┬───┬───┬───┬───┬───┬───┬──
           10K 20K 30K 40K 50K
                BSC Target Price (VND)
```

- Points above 45° line → VCI more bullish
- Points below 45° line → BSC more bullish

#### 3.5.3 Bar Chart: NPATMI Comparison by Sector

```
            BSC vs VCI NPATMI Forecast 2025 by Sector

    Banks    ████████████ 125.3T (BSC)
             ███████████  120.0T (VCI)  -4.2%

    RealEst  ███████ 42.5T (BSC)
             █████   38.0T (VCI)       -10.6%

    Retail   █████ 28.0T (BSC)
             █████ 29.5T (VCI)         +5.4%
```

---

### 3.6 Unified Filter System (Problem 6)

**Current Problem:**
- Sidebar: Rating, Sector, Sort
- In-page: Per-tab filters
- Not synchronized

**Proposed: Single Filter Bar (Below Header)**

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ [Sector ▼ All]  [Rating ▼ BUY/STRONG BUY]  [Source ▼ BSC+VCI]  [Sort ▼ Upside Desc]     │
│                                                                                         │
│ Applied: Banks, BUY+STRONG BUY, BSC Only, Sorted by Upside                    [Clear ×]│
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Implementation:**
- Remove sidebar filters for forecast page
- Use horizontal filter bar under page header
- All tabs respect same filters
- Show active filter chips with clear button

---

## 4. UI/UX Best Practices Applied

### 4.1 Color Palette (Dark Mode Financial Dashboard)

| Element | Color | Hex |
|---------|-------|-----|
| Background | Deep Black | #0F172A |
| Card Background | Slate 800 | #1E293B |
| Primary (Brand) | Teal | #00C9AD |
| CTA/Accent | Purple | #8B5CF6 |
| Positive | Green | #22C55E |
| Negative | Red | #EF4444 |
| Warning | Amber | #F59E0B |
| Muted Text | Slate 400 | #94A3B8 |
| Border | Slate 700 | #334155 |

### 4.2 Chart Recommendations

| Purpose | Chart Type | Library |
|---------|-----------|---------|
| TTM vs FWD comparison | Box plot with markers | Plotly |
| BSC vs VCI scatter | Scatter with 45° line | Plotly |
| Sector NPATMI compare | Grouped horizontal bar | Plotly |
| Rating distribution | Pie/Donut | Plotly |
| Achievement status | Stacked bar | Plotly |

### 4.3 Table Design Principles

- **Data-Dense**: Max info per row, minimize scrolling
- **Sticky Header**: Always visible column names
- **Sortable Columns**: Click header to sort
- **Color-Coded Values**: Green/red for positive/negative
- **Overflow Handling**: Horizontal scroll for mobile

---

## 5. Proposed Tab Structure

**Current:** 5 tabs (Individual, Sector, 9M Achievement, Charts, Forward)

**Proposed:** 4 tabs (consolidated)

1. **Stock Overview** (merge Individual + Forward Matrix)
   - Unified table: Valuation + Earnings + Forward Delta
   - Column group toggles

2. **Sector Analysis** (enhanced)
   - Sector PE/PB with BSC Universal comparison
   - Total earnings aggregation
   - Opportunity Score chart

3. **Achievement Tracker** (enhanced 9M)
   - Quick action cards (Revise Up/On Track/Revise Down)
   - Filterable table
   - Distribution chart

4. **BSC vs Consensus** (NEW - VCI integration)
   - Target price comparison table
   - Scatter plot: BSC TP vs VCI TP
   - NPATMI diff by sector chart
   - Analyst coverage overlap

---

## 6. Implementation Priority

| Priority | Feature | Effort | Impact |
|----------|---------|--------|--------|
| P1 | Unified Stock Table | Medium | High - solves Problem 1, 2 |
| P1 | Quick Action Cards (9M) | Low | High - immediate value |
| P2 | BSC vs VCI Tab | Medium | High - new capability |
| P2 | Unified Filter Bar | Medium | Medium - UX improvement |
| P3 | Enhanced Candlestick Chart | Low | Medium - visual upgrade |
| P3 | Sector Universal Comparison | Low | Medium - enhancement |

---

## 7. Technical Considerations

### 7.1 Service Layer Changes

`ForecastService` cần thêm methods:
- `get_vci_consensus()` → Load VCI parquet
- `get_bsc_vs_vci_comparison()` → Merge BSC + VCI by ticker
- `get_achievement_summary()` → Cards data for 9M

### 7.2 New Component Needs

- `components/cards/achievement_cards.py` → Quick action cards
- `components/charts/consensus_charts.py` → BSC vs VCI visualizations
- `components/tables/unified_forecast_table.py` → Column group table

### 7.3 Session State Updates

```python
PAGE_STATE_DEFAULTS['forecast'] = {
    'forecast_active_tab': 0,      # 0=Stock, 1=Sector, 2=Achievement, 3=Consensus
    'forecast_sector_filter': 'All',
    'forecast_rating_filter': ['STRONG BUY', 'BUY', 'HOLD'],
    'forecast_source_filter': 'BSC',  # BSC, VCI, Both
    'forecast_sort': 'upside_desc',
    'achievement_filter': 'all',   # all, revise_up, on_track, revise_down
}
```

---

## 8. Unresolved Questions

1. **VCI Data Refresh Frequency**: VCI data fetched weekly or daily? Need sync schedule.
2. **Column Priority**: Which metrics are most important for first view? Need user input.
3. **Achievement Thresholds**: 75%/90% thresholds - are these appropriate for Vietnamese market?
4. **Sector Mapping**: BSC sectors = VCI sectors? Need mapping validation.

---

## 9. Next Steps

1. ✅ **User Approval**: Brainstorm reviewed
2. ✅ **Create Implementation Plan**: [plan.md](../2025-12-30-forecast-dashboard-refactor/plan.md)
3. 🔲 **Phase 1 Implementation**: Unified table + Quick cards (P1 items)
4. 🔲 **Phase 2**: BSC vs VCI integration
5. 🔲 **Phase 3**: Visual enhancements

---

## 10. Updates Log

| Date | Update |
|------|--------|
| 2025-12-30 | Initial brainstorm created |
| 2025-12-30 | Implementation plan created, linked |
| 2025-12-30 | Dynamic thresholds updated: 25%/quarter instead of fixed 75%/90% |

---

**Report Generated By:** Claude Code (Brainstorm Mode)
**Duration:** ~15 minutes context gathering + analysis
