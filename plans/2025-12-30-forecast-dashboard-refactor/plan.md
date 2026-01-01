# Implementation Plan: Forecast Dashboard Refactor

**Plan ID:** 2025-12-30-forecast-dashboard-refactor
**Status:** Implementation in Progress
**Updated:** 2025-12-31 (Registry Integration Complete)
**Estimated Effort:** 3-4 days

---

## STREAMLINED SUMMARY

### Mục tiêu
Refactor BSC Forecast Dashboard: cải thiện UX, integrate VCI consensus, thêm analyst accuracy tracking.

### Decisions Made

| Decision | Choice | Reason |
|----------|--------|--------|
| Stock table | Unified (no sub-tabs) | Zero clicks, full picture |
| **Sector table** | **Unified (merged Valuation + Growth)** | Same logic as stock table |
| Sticky columns | Symbol + Price | User context when scrolling |
| BSC vs VCI comparison | By TICKER (not sector) | Sector mapping khac nhau |
| Priority metrics | NPATMI > Target Price > PE/PB | PE/PB la derived, NPATMI la goc |
| Verdict format | BEAT/MEET/MISS + Auto-comment | Wall Street style |
| Data storage | Parquet append-only | BSC Excel + VCI API -> history/*.parquet |
| VCI workflow | Hook into fetch | Auto-snapshot moi lan fetch |
| **Filter system** | **Header only (no sidebar)** | Tab-specific, saves space, consistent |
| **Charts** | **Keep only Valuation Matrix** | 7 charts → 1, in Tab 1 Sector only |
| **Rating badges** | **Header compact badges** | Replace Rating Distribution chart |

### Data Architecture

```
DISPLAY (Dashboard)              HISTORY (Analytics)
─────────────────────               ─────────────────────
BSC Forecast.xlsx          →        bsc/history/forecast_history.parquet
vci_coverage_universe.parquet →     vci/history/forecast_history.parquet

Use cases:                          Use cases:
• Stock table hiển thị              • Tính Accuracy Score
• BSC vs VCI comparison             • Generate nhận xét tự động
                                    • StarMine Leaderboard
```

### Implementation Phases

| Phase | Focus | Key Deliverables | Status |
|-------|-------|------------------|--------|
| **P0** | Registry Integration | Data paths + Service methods | ✅ Done |
| **P1** | Core UX | Unified table + Sticky columns + Achievement cards | 🔜 Ready |
| **P2** | VCI Integration | BSC vs VCI comparison tab + Scatter/Bar charts | 🔜 Ready |
| **P3** | Visual Polish | Enhanced box chart (2025/2026 markers) + BSC Universal row | ⏳ Pending |
| **P4** | Advanced (Future) | Accuracy tracking + Revision Momentum + StarMine | ⏳ Future |

### Phase 0: Registry Integration ✅ COMPLETED (2025-12-31)

**Data Mapping Registry** (`config/data_mapping/configs/data_sources.yaml`):
- ✅ `bsc_forecast` - BSC latest forecast data
- ✅ `bsc_sector_valuation` - BSC sector valuation
- ✅ `vci_coverage` - VCI coverage universe
- ✅ `bsc_forecast_history` - BSC forecast history (P4)
- ✅ `vci_forecast_history` - VCI forecast history (P4)

**ForecastService Methods** (`WEBAPP/services/forecast_service.py`):
- ✅ `get_achievement_summary()` - 3 achievement card data (P1)
- ✅ `get_vci_consensus()` - Load VCI data (P2)
- ✅ `get_bsc_vs_vci_comparison()` - Merge BSC + VCI (P2)
- ✅ `get_consensus_summary()` - Consensus status counts (P2)

### Files to Create/Modify

**New:**
- `WEBAPP/components/tables/unified_forecast_table.py` - Created
- `WEBAPP/components/cards/achievement_cards.py`
- `WEBAPP/components/tables/consensus_table.py`
- `WEBAPP/components/filters/forecast_filter_bar.py` - Reusable header filter bar
- `PROCESSORS/forecast/snapshot_forecast.py`

**Modify:**
- `WEBAPP/pages/forecast/forecast_dashboard.py` (remove sub-tabs, add consensus tab, use filter bar)
- `PROCESSORS/api/vietcap/fetch_vci_forecast.py` (add snapshot hook)
- `WEBAPP/services/forecast_service.py` - ✅ VCI methods added (P0 complete)

---

### Design System (UI/UX Pro Max)

**Skill:** `ui-ux-pro-max` - Run before implementing any UI component.

**Color Palette (Fintech Dark):**
| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#0F172A` | Main background |
| `--bg-card` | `rgba(26, 22, 37, 0.98)` | Card/table background |
| `--text-primary` | `#F8FAFC` | Primary text |
| `--text-muted` | `#94A3B8` | Secondary text |
| `--border` | `#334155` | Borders |
| `--accent-purple` | `#8B5CF6` | Primary accent |
| `--accent-teal` | `#00C9AD` | Positive values |
| `--accent-red` | `#EF4444` | Negative values |
| `--accent-amber` | `#F59E0B` | Warning/neutral |

**Z-Index Scale (Consistent Layering):**
| Layer | Z-Index | Usage |
|-------|---------|-------|
| Base | `z-0` | Normal content |
| Sticky columns | `z-10` | Symbol, Price columns |
| Sticky header | `z-20` | Table header row |
| Corner cells | `z-30` | Header + sticky intersection |
| Overlay | `z-40` | Modals, dropdowns |
| Toast | `z-50` | Notifications |

**Typography:**
| Element | Font | Size |
|---------|------|------|
| Table data | JetBrains Mono | 12px |
| Table header | JetBrains Mono | 11px |
| Labels | System sans-serif | 14px |

**UI Rules (Non-Negotiable):**
- NO emojis as icons (use SVG: Heroicons, Lucide)
- NO arbitrary z-index (use scale above)
- ALL clickable elements have `cursor-pointer`
- ALL hover states have visual feedback
- Transitions: 150-300ms (not instant, not slow)

**Design Resources:**
| Resource | Location | Purpose |
|----------|----------|---------|
| Design System Guide | [design-system-guide.md](design-system-guide.md) | Full design system reference |
| SVG Icon Helper | `WEBAPP/components/ui/icons.py` | 47 icons, sizes, colors |
| Unified Table | `WEBAPP/components/tables/unified_forecast_table.py` | Sticky columns, z-index |

---

### Data Architecture (Detailed)

**File Structure:**
```
DATA/processed/forecast/
├── bsc/
│   ├── BSC Forecast.xlsx              # DISPLAY: Latest forecast
│   ├── bsc_individual.parquet         # Processed for dashboard
│   └── history/
│       └── forecast_history.parquet   # HISTORY: Append-only
│
└── vci/
    ├── vci_coverage_universe.parquet  # DISPLAY: Latest from API
    ├── vci_coverage_universe.json     # JSON backup
    └── history/
        └── forecast_history.parquet   # HISTORY: Append-only
```

**History Schema:**
```python
FORECAST_HISTORY_SCHEMA = {
    'ticker': str,              # ACB, VCB, FPT
    'snapshot_date': str,       # 2025-01-15
    'source': str,              # BSC, VCI
    'npatmi_forecast_2025': float,
    'npatmi_forecast_2026': float,
    'target_price': float,
    'rating': str,
    'pe_fwd_2025': float,
    'pe_fwd_2026': float,
    'sector': str,
}
```

**Snapshot Triggers:**
| Source | Trigger | Script |
|--------|---------|--------|
| BSC | Manual file update | `snapshot_forecast.py --source=bsc` |
| VCI | Hook in fetch_and_save() | Auto-call `snapshot_vci_forecast()` |

**Use Case Mapping:**
| Dashboard Feature | Data Source | Notes |
|-------------------|-------------|-------|
| BSC Universal table | `BSC Forecast.xlsx` | Latest only |
| BSC vs VCI Consensus | Both latest files | Join by ticker |
| Achievement % | Latest + Actual 9M | From fundamentals |
| Accuracy Score | `history/*.parquet` | Compare Q1 forecast vs actual |
| Auto-comments | `history/*.parquet` | Generate "BSC better at Banks" |

---

### Filter System (Header Only - No Sidebar)

**Decision:** Remove global sidebar filters. Each tab has its own context-aware filters in header.

**Rationale:**
- Sidebar filters hard to maintain consistency across pages
- Each tab has unique filter needs
- Saves ~200px horizontal screen space
- User context = tab selection, filter is tab-aware

**Layout (Full-Width, No Sidebar):**
```
┌───────────────────────────────────────────────────────────────────────────┐
│  PAGE HEADER: Forecast Dashboard                                          │
├───────────────────────────────────────────────────────────────────────────┤
│  TABS: [BSC Universal] [Sector] [Achievement] [Consensus]                │
├───────────────────────────────────────────────────────────────────────────┤
│  FILTER BAR (context-aware per tab)                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ Sector: [All v]  Rating: [BUY v]  Sort: [Upside v]  [Extended]     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
├───────────────────────────────────────────────────────────────────────────┤
│                          TABLE CONTENT                                    │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

**Filter Ownership per Tab:**

| Tab | Filters in Header | Notes |
|-----|-------------------|-------|
| Tab 0: BSC Universal | Sector, Rating, Sort, Extended Toggle | Full filter set |
| Tab 1: Sector | Sector (single select), Sort | Sector-focused |
| Tab 2: Achievement | Sector, Achievement Cards (BEAT/MEET/MISS) | Card = clickable filter |
| Tab 3: Consensus | Sector, Consensus Status | ALIGNED/BSC_BULL/VCI_BULL |

**Session State Keys:**
```python
# Tab-specific (all filters scoped to tab)
'tab0_sector': 'All',
'tab0_rating': 'All',
'tab0_sort': 'upside_desc',
'tab0_show_extended': False,

'tab1_sector': 'All',
'tab1_sort': 'pe_asc',

'tab2_sector': 'All',
'tab2_achievement_filter': 'all',  # all, beat, meet, miss

'tab3_sector': 'All',
'tab3_consensus_filter': 'all',    # all, aligned, bsc_bull, vci_bull
```

**Implementation Pattern:**
```python
# In forecast_dashboard.py - each tab handles its own filters

if active_tab == 0:
    # Header: Sort dropdown + Column toggle
    sorted_df = filtered_df.sort_values(sort_col, ascending=sort_asc)

elif active_tab == 2:
    # Header: Achievement cards (clickable)
    if achievement_filter != 'all':
        sorted_df = filtered_df[filtered_df['status'] == achievement_filter]
```

**Filter Bar Component:**
```python
# WEBAPP/components/filters/forecast_filter_bar.py

def render_filter_bar(
    tab_id: int,
    show_sector: bool = True,
    show_rating: bool = False,
    show_sort: bool = True,
    sort_options: list = None,
    extra_filters: list = None
) -> dict:
    """
    Reusable header filter bar for forecast tabs.

    Returns:
        dict with filter values: {'sector': 'All', 'sort': 'upside_desc', ...}
    """
    filters = {}
    cols = st.columns([2, 2, 2, 1])  # Responsive grid

    with cols[0]:
        if show_sector:
            filters['sector'] = st.selectbox(
                "Sector",
                options=['All'] + SECTOR_LIST,
                key=f'tab{tab_id}_sector'
            )

    with cols[1]:
        if show_rating:
            filters['rating'] = st.selectbox(
                "Rating",
                options=['All', 'BUY', 'HOLD', 'SELL'],
                key=f'tab{tab_id}_rating'
            )

    with cols[2]:
        if show_sort and sort_options:
            filters['sort'] = st.selectbox(
                "Sort by",
                options=sort_options,
                key=f'tab{tab_id}_sort'
            )

    with cols[3]:
        # Extra toggles/buttons
        for extra in (extra_filters or []):
            if extra['type'] == 'toggle':
                filters[extra['key']] = st.toggle(
                    extra['label'],
                    key=f'tab{tab_id}_{extra["key"]}'
                )

    return filters
```

**Usage per Tab:**
```python
# Tab 0: BSC Universal
filters = render_filter_bar(
    tab_id=0,
    show_sector=True,
    show_rating=True,
    show_sort=True,
    sort_options=[('Upside', 'upside_desc'), ('PE', 'pe_asc'), ('Growth', 'growth_desc')],
    extra_filters=[{'type': 'toggle', 'key': 'extended', 'label': 'Extended'}]
)

# Tab 2: Achievement (cards replace rating filter)
filters = render_filter_bar(tab_id=2, show_sector=True, show_rating=False, show_sort=False)
# Achievement cards rendered separately below filter bar
```

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [**Brainstorm Report**](../reports/brainstorm-2025-12-30-forecast-dashboard-refactor.md) | Problem analysis |
| [**Phase 1: Core UX**](phase-01-core-ux.md) | Detailed Phase 1 tasks |

---

## DETAILED ANALYSIS (below)

---

## 1. Current vs Proposed Analysis

### 1.1 Tab Structure Comparison

| Aspect | Current | Proposed |
|--------|---------|----------|
| **Number of Tabs** | 5 tabs | 4 tabs |
| **Individual Tab** | 2 sub-tabs (Valuation/Earnings) | Single unified table + Rating badges in header |
| **Sector Tab** | 2 sub-tabs (Valuation/Growth) | Unified table + Valuation Matrix (toggle view) |
| **9M Achievement** | Table only | Cards + Filtered table |
| **Charts Tab** | 7 chart types | REMOVED (only Valuation Matrix kept in Sector) |
| **Forward Tab** | Separate PE/PB matrix | REMOVED (merged into BSC Universal) |
| **Consensus Tab** | None | NEW - BSC vs VCI comparison |

### 1.1.1 Content Analysis (Final Decisions)

**Tab 0: BSC Universal**
- Rating badges (compact) in header - replaces Rating Distribution chart
- Unified stock table (92 stocks)
- Filters: Sector, Rating, Sort, Extended toggle

**Tab 1: Sector**
- Unified sector table (merged Valuation + Growth views)
- Valuation Matrix chart (toggle view, BSC coverage only ~92 stocks)
- Filters: Sector (single), Sort

**Tab 2: Achievement**
- Achievement cards (BEAT/MEET/MISS with dynamic thresholds)
- Filtered stock table by achievement status
- Clear filter button

**Tab 3: Consensus**
- BSC vs VCI comparison by ticker
- Verdict status (ALIGNED/BSC_BULL/VCI_BULL)
- Priority: NPATMI > Target Price > PE/PB

**Charts Consolidation (7 to 1):**
| Chart | Decision | Location |
|-------|----------|----------|
| PE vs FWD (sector bars) | MERGED | Tab 1 Sector unified table (columns) |
| PB TTM vs FWD (sector bars) | MERGED | Tab 1 Sector unified table (columns) |
| PE FWD by Sector | MERGED | Tab 1 Sector unified table |
| Sector Opportunity | REMOVED | Low usage |
| Rating Distribution | CONVERTED | Tab 0 header badges (compact) |
| Upside vs PE | REMOVED | Low actionability |
| **Valuation Matrix** | **KEEP** | Tab 1 Sector (toggle view, BSC coverage only) |

### 1.2 Feature-by-Feature Pros/Cons

---

#### Feature 1: Unified Stock Table

**CURRENT APPROACH:**
```
Tab: Individual
├── Sub-tab: Valuation View
│   └── Symbol, Target, Current, Upside, Rating, PE 25F, PE 26F, PB 25F, PB 26F, ROE, Sector, MktCap
└── Sub-tab: Earnings View
    └── Symbol, Sector, Rev 25F, Rev 26F, Rev Gr, NPATMI 25F, NPATMI 26F, Profit Gr, ROE 25F, ROE 26F, Rating
```

| Pros (Current) | Cons (Current) |
|----------------|----------------|
| ✓ Focused views for specific analysis | ✗ Duplicate columns: Symbol, Sector, Rating, ROE |
| ✓ Less horizontal scroll | ✗ 2 clicks required for full picture |
| ✓ Simpler table rendering | ✗ Can't compare valuation vs earnings at once |
| | ✗ Context switching loses mental model |

**PROPOSED APPROACH:**
```
Tab: BSC Universal
└── Unified Table with Column Groups
    ├── [Core]: Symbol*, Price*, Sector, Rating, Upside  (* = sticky)
    ├── [Valuation]: PE 25F, PE 26F, PB 25F, Δ PE
    ├── [Earnings]: NPATMI 25F, NPATMI 26F, Growth%
    └── [Extended] (toggle): Revenue, ROE, Target, MktCap
```

| Pros (Proposed) | Cons (Proposed) |
|-----------------|-----------------|
| ✓ Single view shows complete picture | ✗ More columns = wider table |
| ✓ No duplicate columns | ✗ May need horizontal scroll |
| ✓ Zero clicks to see full data | ✗ Slightly more complex rendering |
| ✓ Better data density | ✗ Column toggle adds state complexity |

**VERDICT:** Proposed is better - eliminates redundancy, reduces cognitive load

**RISK MITIGATION:**
- Use sticky first 2 columns (Symbol + Price) với shadow effect khi scroll
- Mobile: single sticky (Symbol only)
- Implement column toggle to hide extended columns by default
- Test on common screen widths (1366px, 1920px)

### MOCKUP: Unified Stock Table

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Toggle: [Extended Columns]                                                              Filter: Banks [v]   │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                             │
│  ┌─────────┬──────────┬──────────┬─────────┬─────────┬─────────┬─────────┬────────────┬────────────┬───────┐│
│  │ SYMBOL  │ SECTOR   │ PE 25F   │ PE 26F  │ Δ PE    │ PB 25F  │NPATMI25F│ NPATMI26F  │ GROWTH %   │RATING ││
│  ├─────────┼──────────┼──────────┼─────────┼─────────┼─────────┼─────────┼────────────┼────────────┼───────┤│
│  │ ACB     │ Banks    │   7.0x   │  5.9x   │ -15.7%  │  1.2x   │  17.8T  │   21.0T    │   +17.8%   │ BUY   ││
│  │ VCB     │ Banks    │   9.2x   │  8.1x   │ -12.0%  │  1.8x   │  45.2T  │   52.1T    │   +15.3%   │S.BUY  ││
│  │ TCB     │ Banks    │   5.8x   │  5.2x   │ -10.3%  │  0.9x   │  28.5T  │   32.4T    │   +13.7%   │ BUY   ││
│  │ MBB     │ Banks    │   6.1x   │  5.5x   │  -9.8%  │  1.1x   │  22.3T  │   25.8T    │   +15.7%   │ BUY   ││
│  │ CTG     │ Banks    │   7.1x   │  6.0x   │ -15.5%  │  1.1x   │  30.3T  │   35.8T    │   +18.2%   │S.BUY  ││
│  │ ...     │ ...      │   ...    │  ...    │  ...    │  ...    │  ...    │   ...      │   ...      │ ...   ││
│  └─────────┴──────────┴──────────┴─────────┴─────────┴─────────┴─────────┴────────────┴────────────┴───────┘│
│                                                                                                             │
│  Showing 15 of 92 stocks │ Sorted by: Upside ▼                                      [Download Excel]    │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

Color Legend:
┌────────────────────────────────────────────────────────────────┐
│ Δ PE:    [+] Negative = Improving     [-] Positive = Worsening │
│ GROWTH:  [+] Positive growth          [-] Negative growth      │
│ RATING:  [+] S.BUY/BUY   [=] HOLD   [-] SELL                   │
└────────────────────────────────────────────────────────────────┘

Extended Columns (when toggled ON):
┌─────────┬──────────┬─────────┬─────────┬────────┬────────┬─────────┐
│ ...     │ REV 25F  │ REV 26F │ ROE 25F │ TARGET │CURRENT │ MKT CAP │
├─────────┼──────────┼─────────┼─────────┼────────┼────────┼─────────┤
│ ACB     │  42.5T   │  48.2T  │  20.1%  │ 33,000 │ 23,900 │  123T   │
└─────────┴──────────┴─────────┴─────────┴────────┴────────┴─────────┘
```

---

#### Feature 2: Quick Action Cards (9M Achievement)

**CURRENT APPROACH:**
```
Tab: 9M Achievement
├── 4 metric cards (top)
├── Sort radio buttons
└── Full table (all stocks)
```

| Pros (Current) | Cons (Current) |
|----------------|----------------|
| ✓ All data visible in one table | ✗ No visual summary of revision needs |
| ✓ Simple sort options | ✗ Must scan entire table to find outliers |
| | ✗ No quick filter by achievement status |

**PROPOSED APPROACH:**
```
Tab: Achievement Tracker
├── 3 Action Cards (clickable filters)
│   [^] REVISE UP (>expected+20%) -> 8 stocks
│   [=] ON TRACK (expected +-20%) -> 45 stocks
│   [v] REVISE DOWN (<expected-20%) -> 12 stocks
├── Active filter chip
└── Filtered table

Dynamic Threshold Logic (25% per quarter):
├── Q1 data (3M) → expected = 25% → thresholds: <20% / 20-30% / >30%
├── Q2 data (6M) → expected = 50% → thresholds: <40% / 40-60% / >60%
├── Q3 data (9M) → expected = 75% → thresholds: <60% / 60-90% / >90%
└── Q4 data (12M)→ expected = 100%→ thresholds: <80% / 80-120%/ >120%
```

| Pros (Proposed) | Cons (Proposed) |
|-----------------|-----------------|
| ✓ Immediate visual summary | ✗ Adds 3 new UI components |
| ✓ Click to filter reduces scanning | ✗ Need to detect quarter from data |
| ✓ Highlights actionable insights | ✗ Card click = session state logic |
| ✓ Professional analyst workflow |  |
| ✓ Dynamic thresholds work year-round |  |

**VERDICT:** Proposed is significantly better for analyst workflow

**RISK MITIGATION:**
- Use 25% per quarter formula: `expected = quarters_completed * 0.25`
- Thresholds: Revise Down = `<(expected - 0.20)`, On Track = `±20%`, Revise Up = `>(expected + 0.20)`
- Auto-detect quarter from YTD data date column
- Add "Show All" option after filtering
- Use existing card styling from `components/data_display/metric_cards.py`

### MOCKUP: Achievement Cards + Table

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           9M 2025 Achievement Tracker                                           │
│                     Dynamic thresholds: 25% per quarter (expected: 75%)                         │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐         │
│  │   [^] REVISE UP         │  │   [=] ON TRACK          │  │   [v] REVISE DOWN       │         │
│  │                         │  │                         │  │                         │         │
│  │      8 stocks           │  │      52 stocks          │  │      12 stocks          │         │
│  │                         │  │                         │  │                         │         │
│  │   Achievement > 95%     │  │   Achievement 55-95%    │  │   Achievement < 55%     │         │
│  │                         │  │                         │  │                         │         │
│  │  ┌─────────────────┐    │  │                         │  │  ┌─────────────────┐    │         │
│  │  │CTG VCB ACB MBB  │    │  │                         │  │  │HPG VNM SSI FPT  │    │         │
│  │  │BID TCB ...      │    │  │                         │  │  │MWG PNJ ...      │    │         │
│  │  └─────────────────┘    │  │                         │  │  └─────────────────┘    │         │
│  │      [CLICK TO FILTER]  │  │      [CLICK TO FILTER]  │  │      [CLICK TO FILTER]  │         │
│  └─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘         │
│        Green border               Purple border               Red border                      │
│                                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Active Filter: [REVISE DOWN x]                                                 [Clear Filter] │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  ┌────────┬──────────┬──────────┬──────────┬──────────┬───────────┬───────────┬──────────┐     │
│  │ SYMBOL │ SECTOR   │ REV 25F  │ REV 9M   │  REV %   │NPATMI 25F │ NPATMI 9M │ PROFIT % │     │
│  ├────────┼──────────┼──────────┼──────────┼──────────┼───────────┼───────────┼──────────┤     │
│  │ HPG    │ Steel    │  142.5T  │  68.2T   │  47.9%   │   15.0T   │   6.2T    │  41.3%   │     │
│  │ VNM    │ F&B      │   58.2T  │  28.1T   │  48.3%   │    8.5T   │   3.8T    │  44.7%   │     │
│  │ SSI    │ Security │   12.5T  │   5.8T   │  46.4%   │    3.2T   │   1.4T    │  43.8%   │     │
│  │ ...    │ ...      │   ...    │   ...    │   ...    │    ...    │   ...     │   ...    │     │
│  └────────┴──────────┴──────────┴──────────┴──────────┴───────────┴───────────┴──────────┘     │
│                                                                                                 │
│  Showing 12 of 72 stocks with 9M data                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

Threshold Logic by Quarter:
┌──────────┬──────────┬─────────────┬────────────┬────────────┐
│ Quarter  │ Expected │ REVISE DOWN │ ON TRACK   │ REVISE UP  │
├──────────┼──────────┼─────────────┼────────────┼────────────┤
│ Q1 (3M)  │   25%    │    < 5%     │   5-45%    │   > 45%    │
│ Q2 (6M)  │   50%    │   < 30%     │  30-70%    │   > 70%    │
│ Q3 (9M)  │   75%    │   < 55%     │  55-95%    │   > 95%    │
│ Q4 (12M) │  100%    │   < 80%     │  80-120%   │  > 120%    │
└──────────┴──────────┴─────────────┴────────────┴────────────┘
```

---

#### Feature 3: BSC vs VCI Consensus Tab

**CURRENT APPROACH:**
- VCI data exists at `DATA/processed/forecast/VCI/vci_coverage_universe.parquet`
- NOT integrated into dashboard
- Users cannot compare internal vs external forecasts

| Pros (Current) | Cons (Current) |
|----------------|----------------|
| ✓ Simpler dashboard | ✗ Misses key value: consensus validation |
| ✓ No data sync issues | ✗ Team can't identify divergent views |
| | ✗ No external benchmark for BSC forecasts |

**PROPOSED APPROACH:**
```
Tab: BSC vs Consensus
├── Comparison Table (priority order)
│   └── Symbol, BSC NPATMI, VCI NPATMI, NPATMI Diff%, BSC TP, VCI TP, TP Diff%, Consensus
│
│   Key Metrics (ưu tiên so sánh):
│   ├── 1. NPATMI 25F/26F → Gốc của mọi valuation, trực tiếp từ forecast
│   └── 2. Target Price → Kết luận cuối cùng của analyst
│
│   Skip (derived, ko cần compare):
│   └── PE/PB Forward → Tính từ NPATMI, redundant
│
├── Scatter Plot (BSC TP vs VCI TP with 45° line)
├── Bar Chart (NPATMI comparison by sector)
└── Coverage Stats (overlap count)
```

| Pros (Proposed) | Cons (Proposed) |
|-----------------|-----------------|
| ✓ Validates internal forecasts | ✗ New service methods needed |
| ✓ Identifies contrarian views (alpha) | ✗ ~Sector mapping may differ~ (RESOLVED: compare by ticker) |
| ✓ Transparency for clients | ✗ VCI data refresh frequency unknown |
| ✓ Unique differentiator | ✗ 2 additional charts to maintain |
| ✓ Simple ticker-based join | ✗ Some tickers may have BSC or VCI only |

**VERDICT:** Proposed adds significant value - competitive advantage

**RISK MITIGATION:**
- **Compare by TICKER, not sector** (BSC/VCI sectors không nhất thiết phải khớp)
- Join data on `ticker` column → 3 categories:
  - **Both coverage:** Tickers có cả BSC & VCI forecast (comparison table)
  - **BSC only:** Tickers chỉ BSC cover (hiển thị riêng hoặc N/A for VCI columns)
  - **VCI only:** Tickers chỉ VCI cover (consolidated view option)
- Handle missing tickers gracefully
- Cache merged data to avoid repeat joins

---

### BRAINSTORM: 3-Way Comparison (BSC vs VCI vs Actual)

**Ý tưởng:** Không chỉ so BSC vs VCI, mà còn so với **số thực tế 9M** để đánh giá:
- Ai dự báo chính xác hơn? (BSC hay VCI?)
- Cổ phiếu nào cần revise forecast?
- Trend accuracy theo thời gian

#### Data Available:
```
BSC Forecast:     NPATMI 2025F (full year)
VCI Consensus:    NPATMI 2025F (full year)
Actual 9M:        NPATMI 9M (từ BCTC Q3)
```

#### Metrics tính toán (SIMPLE - không cần annualize):

```
Achievement % = Actual 9M / Forecast 25F
Expected = 75% (9/12 tháng)

Verdict Categories (Wall Street style):

1. Actual vs Expected (75%):
   [+] BEAT:  ACH% > 85%  -> Beating expectations
   [=] MEET:  ACH% 65-85% -> Meeting expectations
   [-] MISS:  ACH% < 65%  -> Missing expectations

2. BSC vs VCI Analyst View:
   [B] BSC BULL: BSC 25F > VCI 25F -> BSC optimistic than consensus
   [V] VCI BULL: VCI 25F > BSC 25F -> VCI optimistic than BSC
   [=] ALIGNED:  |Diff| < 5%       -> Both views aligned

3. Combined Verdict (Actual vs Both Forecasts):
   [OK] CONSENSUS CONFIRMED: Actual MEET both BSC & VCI
   [UP] UPGRADE SIGNAL:      Actual BEAT both -> Need revise up
   [DN] DOWNGRADE SIGNAL:    Actual MISS both -> Need revise down
   [B]  BSC WINS:            BSC forecast closer to actual
   [V]  VCI WINS:            VCI forecast closer to actual
```

**Example readings:**
```
ACB: Actual 9M = 14.2T | BSC 25F = 17.9T | VCI 25F = 17.9T
     BSC ACH = 79.3% [=] MEET
     VCI ACH = 79.3% [=] MEET
     Analyst View: ALIGNED
     -> Verdict: CONSENSUS CONFIRMED - Both views correct

HPG: Actual 9M = 8.5T | BSC 25F = 15.0T | VCI 25F = 18.5T
     BSC ACH = 56.7% [-] MISS
     VCI ACH = 45.9% [-] MISS
     Analyst View: VCI BULL (VCI more aggressive)
     -> Verdict: DOWNGRADE SIGNAL - Both need revise down, BSC WINS (closer to actual)

FPT: Actual 9M = 11.2T | BSC 25F = 12.8T | VCI 25F = 10.5T
     BSC ACH = 87.5% [+] BEAT
     VCI ACH = 106.7% [+] BEAT
     Analyst View: BSC BULL (BSC forecast higher)
     -> Verdict: UPGRADE SIGNAL - Need revise up, VCI WINS (closer to actual)
```

#### Presentation Ideas:

**Option A: Enhanced Table (SIMPLE FORMAT)**
```
┌────────┬───────────┬─────────┬─────────┬─────────┬─────────┬─────────────────┬────────────────────────────────────┐
│ Symbol │ Actual 9M │ BSC 25F │ BSC Ach │ VCI 25F │ VCI Ach │ Verdict         │ Comment                            │
├────────┼───────────┼─────────┼─────────┼─────────┼─────────┼─────────────────┼────────────────────────────────────┤
│ FPT    │   11.2T   │  12.8T  │  87.5%  │  10.5T  │ 106.7%  │ [+] OVER / OVER │ VCI conservative, both need upgrade│
│ ACB    │   14.2T   │  17.9T  │  79.3%  │  17.9T  │  79.3%  │ [=] INLINE/INLINE│ Forecast accurate                 │
│ HPG    │    8.5T   │  15.0T  │  56.7%  │  18.5T  │  45.9%  │ [-] OFF / OFF   │ VCI too optimistic, need downgrade │
│ STB    │    5.0T   │   6.0T  │  83.3%  │   8.0T  │  62.5%  │ [=] INLINE / [-]│ BSC accurate, VCI target too high  │
└────────┴───────────┴─────────┴─────────┴─────────┴─────────┴─────────────────┴────────────────────────────────────┘
```

**Auto-Comment Logic (generate từ verdict):**
```python
COMMENT_TEMPLATES = {
    # (BSC_verdict, VCI_verdict): "Nhận xét template"

    # Cả 2 aligned
    ("OVER", "OVER"):     "Cả 2 thận trọng, cần nâng dự báo",
    ("INLINE", "INLINE"): "Forecast sát thực tế",
    ("OFF", "OFF"):       "Cả 2 lạc quan quá, cần hạ dự báo",

    # BSC chuẩn hơn
    ("INLINE", "OVER"):   "BSC chuẩn, VCI quá thận trọng",
    ("INLINE", "OFF"):    "BSC chuẩn, VCI target quá cao",
    ("OVER", "OFF"):      "BSC thận trọng hơn, VCI lạc quan",

    # VCI chuẩn hơn
    ("OVER", "INLINE"):   "VCI chuẩn, BSC quá thận trọng",
    ("OFF", "INLINE"):    "VCI chuẩn, BSC target quá cao",
    ("OFF", "OVER"):      "VCI thận trọng hơn, BSC lạc quan",
}

def get_comment(bsc_ach: float, vci_ach: float) -> str:
    """Generate comment based on achievement %."""
    def status(ach):
        if ach > 0.85: return "OVER"
        if ach >= 0.65: return "INLINE"
        return "OFF"

    key = (status(bsc_ach), status(vci_ach))
    return COMMENT_TEMPLATES.get(key, "—")
```

**Legend:**
- [+] OVER: Ach > 85% (actual exceeded forecast)
- [=] INLINE: Ach 65-85% (on track)
- [-] OFF: Ach < 65% (actual below forecast)

**Option B: Wall Street Pro View (Bloomberg + StarMine inspired)**

---

#### B1. Surprise Bar (Bloomberg ERN Style)

**Concept:** Không chỉ status, mà còn hiển thị **magnitude** (độ lớn) của surprise.

```
┌────────┬───────────┬─────────┬─────────────────────────────────────────────────────┐
│ Symbol │ Actual 9M │ BSC 25F │              Surprise Bar (BSC)                     │
├────────┼───────────┼─────────┼─────────────────────────────────────────────────────┤
│ FPT    │   11.2T   │  12.8T  │         ◄▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓|                +17% BEAT │
│ ACB    │   14.2T   │  17.9T  │                      ▓▓▓|▓▓▓              +5% INLINE │
│ HPG    │    8.5T   │  15.0T  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓|►             -43% MISS   │
│ STB    │    5.0T   │   6.0T  │                    ▓▓▓▓▓|▓▓▓▓▓           +8% INLINE │
└────────┴───────────┴─────────┴─────────────────────────────────────────────────────┘

Legend: ◄▓▓▓| = Positive Surprise (Actual > expected pace)
        |▓▓▓► = Negative Surprise (Actual < expected pace)
        Surprise% = (Ach% - 75%) / 75%
```

**Implementation:**
```python
def surprise_pct(actual_9m, forecast_25f):
    """Calculate surprise % (deviation from expected 75%)."""
    ach = actual_9m / forecast_25f
    expected = 0.75
    return (ach - expected) / expected * 100  # e.g., +17% or -43%

def surprise_bar(surprise_pct, width=30):
    """Generate visual surprise bar."""
    mid = width // 2
    filled = int(abs(surprise_pct) / 5)  # Scale: 5% = 1 block
    filled = min(filled, mid)

    if surprise_pct >= 0:
        bar = " " * (mid - filled) + "▓" * filled + "|" + "▓" * filled
        return f"◄{bar} +{surprise_pct:.0f}%"
    else:
        bar = "▓" * filled + "|" + " " * (mid - filled) + "▓" * filled
        return f"{bar}► {surprise_pct:.0f}%"
```

---

#### B2. StarMine Accuracy Score (Refinitiv Style)

**Concept:** Track lịch sử accuracy của BSC vs VCI theo sector/stock để biết **ai thường đúng hơn**.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    ANALYST ACCURACY LEADERBOARD (Last 4 Quarters)                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   OVERALL ACCURACY                                                                  │
│   ┌─────────────────┐          ┌─────────────────┐                                  │
│   │  BSC: ⭐ 72%    │          │  VCI:    68%    │                                  │
│   │  (54/75 stocks) │          │  (51/75 stocks) │                                  │
│   └─────────────────┘          └─────────────────┘                                  │
│                                                                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│   SECTOR EXPERTISE (Who's better at which sector?)                                  │
│                                                                                     │
│   Sector       │ BSC Accuracy │ VCI Accuracy │ Expert │ Insight                     │
│   ─────────────┼──────────────┼──────────────┼────────┼────────────────────────────│
│   Ngân hàng    │   ⭐ 85%     │     78%      │  BSC   │ BSC có insight ngành bank   │
│   BĐS          │     62%      │   ⭐ 71%     │  VCI   │ VCI gần thị trường BĐS hơn │
│   Công nghệ    │   ⭐ 88%     │     82%      │  BSC   │ FPT specialist tại BSC      │
│   Thép         │     45%      │   ⭐ 52%     │  VCI   │ Cả 2 khó dự báo commodity   │
│   Bán lẻ       │   ⭐ 72%     │     69%      │  BSC   │ Tương đương                 │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Use case:** Khi đọc forecast của HPG (Thép), prefer VCI hơn BSC vì VCI có track record tốt hơn.

---

#### DATA ARCHITECTURE: Historical Forecast Storage

**Vấn đề hiện tại:**
```
BSC:  Copy đè file mới → Mất lịch sử forecast cũ
VCI:  API fetch mới → Đè lên dữ liệu cũ
→ Không thể tính Accuracy vì không biết forecast lúc đầu là bao nhiêu
```

**Giải pháp: Append-Only Forecast History**

```
DATA/processed/forecast/
├── bsc/
│   ├── BSC Forecast.xlsx          # Latest (current behavior)
│   └── history/
│       └── forecast_history.parquet   # NEW: Append-only history
│
└── vci/
    ├── vci_coverage_universe.parquet  # Latest
    └── history/
        └── forecast_history.parquet   # NEW: Append-only history
```

**Schema: forecast_history.parquet**
```python
FORECAST_HISTORY_SCHEMA = {
    'ticker': str,           # ACB, VCB, FPT
    'snapshot_date': str,    # 2024-01-15 (khi lấy forecast)
    'source': str,           # BSC, VCI
    'target_year': int,      # 2025, 2026
    'npatmi_forecast': float,    # 17.9T
    'revenue_forecast': float,   # 42.5T
    'target_price': float,       # 33000
    'rating': str,               # BUY, HOLD, SELL
}
```

**Implementation Options:**

**Option A: Script tự động snapshot (Recommended)**
```python
# PROCESSORS/forecast/snapshot_forecast.py

def snapshot_bsc_forecast():
    """Chạy MỖI KHI update BSC forecast file."""
    today = datetime.now().strftime('%Y-%m-%d')

    # 1. Load current forecast
    current = pd.read_excel('DATA/processed/forecast/bsc/BSC Forecast.xlsx')

    # 2. Add metadata
    current['snapshot_date'] = today
    current['source'] = 'BSC'

    # 3. Append to history (not overwrite!)
    history_path = 'DATA/processed/forecast/bsc/history/forecast_history.parquet'

    if Path(history_path).exists():
        history = pd.read_parquet(history_path)
        # Check if today already exists
        if today not in history['snapshot_date'].values:
            history = pd.concat([history, current], ignore_index=True)
    else:
        history = current

    # 4. Save
    history.to_parquet(history_path, index=False)
    print(f"[OK] Snapshot saved: {len(current)} rows for {today}")


def snapshot_vci_forecast():
    """
    Chạy MỖI KHI fetch VCI API.

    Current VCI fetch flow (PROCESSORS/api/vietcap/fetch_vci_forecast.py):
    1. fetch_coverage_universe() → API call
    2. Save → DATA/processed/forecast/VCI/vci_coverage_universe.parquet
    3. Already has: fetch_date, fetch_timestamp metadata

    Solution: Hook vào cuối fetch_and_save() để append history.
    """
    today = datetime.now().strftime('%Y-%m-%d')

    # 1. Load current (just saved by fetch_and_save)
    current = pd.read_parquet('DATA/processed/forecast/VCI/vci_coverage_universe.parquet')

    # 2. Normalize columns to match history schema
    history_cols = {
        'ticker': 'ticker',
        'npatmi_2025F': 'npatmi_forecast_2025',
        'npatmi_2026F': 'npatmi_forecast_2026',
        'targetPrice': 'target_price',
        'rating': 'rating',
        'pe_2025F': 'pe_fwd_2025',
        'pe_2026F': 'pe_fwd_2026',
        'sector': 'sector',
    }

    snapshot_df = current.rename(columns=history_cols)[list(history_cols.values())]
    snapshot_df['snapshot_date'] = today
    snapshot_df['source'] = 'VCI'

    # 3. Append to history
    history_path = Path('DATA/processed/forecast/vci/history/forecast_history.parquet')
    history_path.parent.mkdir(parents=True, exist_ok=True)

    if history_path.exists():
        history = pd.read_parquet(history_path)
        # Avoid duplicate snapshots on same day
        if today not in history['snapshot_date'].values:
            history = pd.concat([history, snapshot_df], ignore_index=True)
            history.to_parquet(history_path, index=False)
            print(f"[OK] VCI Snapshot saved: {len(snapshot_df)} rows for {today}")
        else:
            print(f"[!] VCI Snapshot for {today} already exists, skipping")
    else:
        snapshot_df.to_parquet(history_path, index=False)
        print(f"[OK] VCI History created: {len(snapshot_df)} rows for {today}")
```

**Option B: Git-based versioning (Simple)**
```bash
# Mỗi khi update BSC file, commit với timestamp
git add "DATA/processed/forecast/bsc/BSC Forecast.xlsx"
git commit -m "forecast(bsc): snapshot 2024-01-15"

# Để xem history:
git log --oneline -- "DATA/processed/forecast/bsc/BSC Forecast.xlsx"
git show HEAD~5:"DATA/processed/forecast/bsc/BSC Forecast.xlsx" > old_forecast.xlsx
```

**Option C: DuckDB (Scalable)**
```python
import duckdb

# Create append-only table
conn = duckdb.connect('DATA/forecast_history.duckdb')
conn.execute("""
    CREATE TABLE IF NOT EXISTS forecast_history (
        ticker VARCHAR,
        snapshot_date DATE,
        source VARCHAR,
        target_year INT,
        npatmi_forecast DOUBLE,
        target_price DOUBLE
    )
""")

# Append new data
conn.execute("""
    INSERT INTO forecast_history
    SELECT *, CURRENT_DATE as snapshot_date, 'BSC' as source
    FROM read_parquet('DATA/processed/forecast/bsc/latest.parquet')
""")
```

**Accuracy Calculation:**
```python
def calculate_accuracy(ticker: str, source: str, actual_9m: float) -> float:
    """
    So sánh forecast TẠI THỜI ĐIỂM ĐẦU NĂM với actual 9M.

    Logic:
    1. Lấy forecast snapshot đầu năm (Q1) của ticker
    2. So sánh với actual 9M hiện tại
    3. Tính accuracy = 1 - |error|
    """
    history = pd.read_parquet(f'DATA/processed/forecast/{source.lower()}/history/forecast_history.parquet')

    # Lấy forecast đầu năm (tháng 1-2)
    q1_forecast = history[
        (history['ticker'] == ticker) &
        (history['snapshot_date'] >= '2025-01-01') &
        (history['snapshot_date'] <= '2025-02-28') &
        (history['target_year'] == 2025)
    ].iloc[-1]  # Latest trong Q1

    predicted_npatmi = q1_forecast['npatmi_forecast']
    expected_9m = predicted_npatmi * 0.75

    error = abs(actual_9m - expected_9m) / expected_9m
    accuracy = max(0, 1 - error)

    return accuracy


def sector_accuracy_leaderboard(sector: str) -> pd.DataFrame:
    """Track BSC vs VCI accuracy by sector over last 4 quarters."""
    results = []

    for source in ['BSC', 'VCI']:
        for ticker in get_tickers_by_sector(sector):
            acc = calculate_accuracy(ticker, source, get_actual_9m(ticker))
            results.append({
                'ticker': ticker,
                'source': source,
                'accuracy': acc
            })

    df = pd.DataFrame(results)
    return df.groupby('source')['accuracy'].mean()
```

**Workflow Integration:**

**BSC Workflow (Excel-based):**
```
┌─────────────────────────────────────────────────────────────────────────┐
│                    BSC FORECAST UPDATE WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. BSC Analyst gửi file Excel mới                                      │
│     ↓                                                                   │
│  2. Copy vào DATA/processed/forecast/bsc/BSC Forecast.xlsx              │
│     ↓                                                                   │
│  3. RUN: python PROCESSORS/forecast/snapshot_forecast.py --source=bsc   │
│     ↓                                                                   │
│  4. Auto-append to bsc/history/forecast_history.parquet                 │
│     ↓                                                                   │
│  5. Dashboard tự động có data mới + track được lịch sử                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**VCI Workflow (API-based):**
```
┌─────────────────────────────────────────────────────────────────────────┐
│                    VCI FORECAST UPDATE WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Option A: Hook vào fetch script (Recommended)                          │
│  ───────────────────────────────────────────────                        │
│  1. RUN: python PROCESSORS/api/vietcap/fetch_vci_forecast.py            │
│     ↓                                                                   │
│  2. fetch_and_save() gọi API → save vci_coverage_universe.parquet       │
│     ↓                                                                   │
│  3. HOOK: Cuối fetch_and_save() gọi snapshot_vci_forecast()             │
│     ↓                                                                   │
│  4. Auto-append to vci/history/forecast_history.parquet                 │
│                                                                         │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  Option B: Chạy snapshot riêng sau khi fetch                            │
│  ───────────────────────────────────────────────                        │
│  1. RUN: python PROCESSORS/api/vietcap/fetch_vci_forecast.py            │
│  2. RUN: python PROCESSORS/forecast/snapshot_forecast.py --source=vci   │
│                                                                         │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  Option C: Daily cron (tự động hàng ngày)                               │
│  ───────────────────────────────────────────                            │
│  # crontab -e                                                           │
│  0 18 * * 1-5 cd ~/Vietnam_dashboard && \                               │
│    python PROCESSORS/api/vietcap/fetch_vci_forecast.py && \             │
│    python PROCESSORS/forecast/snapshot_forecast.py --source=vci         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Data Architecture (Phân tách rõ ràng):**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATA SEPARATION PRINCIPLE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DISPLAY (Streamlit Dashboard)        HISTORY (Accuracy Analytics)      │
│  ─────────────────────────────────    ─────────────────────────────────│
│  • Hiển thị forecast MỚI NHẤT         • Lưu trữ snapshot theo thời gian │
│  • User xem trực tiếp trên table      • Tính toán accuracy BSC vs VCI   │
│  • Real-time data                     • Generate nhận xét tự động       │
│  • Sources:                           • Sources:                        │
│    - BSC Forecast.xlsx                  - bsc/history/*.parquet         │
│    - vci_coverage_universe.parquet      - vci/history/*.parquet         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Files Structure:**
```
DATA/processed/forecast/
├── bsc/
│   ├── BSC Forecast.xlsx              # DISPLAY: Dashboard reads this
│   └── history/
│       └── forecast_history.parquet   # HISTORY: Accuracy tracking only
│
└── vci/
    ├── vci_coverage_universe.parquet  # DISPLAY: Dashboard reads this
    ├── vci_coverage_universe.json     # JSON backup
    └── history/
        └── forecast_history.parquet   # HISTORY: Accuracy tracking only
```

**Use Cases:**

| Task | Data Source | Description |
|------|-------------|-------------|
| Stock forecast table | `BSC Forecast.xlsx` | Latest BSC forecast on dashboard |
| BSC vs VCI comparison | Both latest files | Compare current forecasts |
| Accuracy Score | `history/*.parquet` | So sánh forecast đầu năm vs actual |
| Generate nhận xét | `history/*.parquet` | "BSC chuẩn hơn VCI với ngành Bank" |
| StarMine Leaderboard | `history/*.parquet` | Track who's more accurate by sector |

**VCI Workflow: Option A (Hook into fetch script) - SELECTED**

---

#### B3. Revision Momentum (Hedge Fund Style)

**Concept:** Sau khi có Actual, analyst phản ứng thế nào? Điều này quan trọng hơn số học đơn thuần.

```
Revision Signals:
[^] RAISED:  Analyst raised target after earnings
[=] HOLD:    Analyst kept target unchanged
[v] CUT:     Analyst cut target after earnings
```

**Action Matrix (Actual + Revision combined):**

| Actual vs FC | BSC Revision | VCI Revision | Signal | Explanation |
|--------------|--------------|--------------|--------|-------------|
| [+] BEAT | RAISED | RAISED | **STRONG BUY** | Consensus upgrade, strong momentum |
| [+] BEAT | HOLD | HOLD | **WATCH** | Good numbers but no upgrade? Quality concern |
| [-] MISS | CUT | CUT | **AVOID** | Consensus cut, downgrade risk |
| [-] MISS | RAISED | HOLD | **CONTRARIAN** | Bad news priced in, potential bottom |
| [=] INLINE | RAISED | RAISED | **ACCUMULATE** | Numbers OK + analyst bullish = good |

---

#### B4. Triangulation Dashboard (Tổng hợp tất cả)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              TRIANGULATION VIEW: FPT                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │  ACTUAL 9M     BSC 25F      VCI 25F      SURPRISE                                           │   │
│   │  11.2T         12.8T        10.5T        ◄▓▓▓▓▓▓▓▓|     +17% BEAT (BSC)                     │   │
│   │                                          ◄▓▓▓▓▓▓▓▓▓▓▓▓|  +42% BEAT (VCI)                     │   │
│   └─────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                     │
│   ┌─────────────────────────────┐  ┌─────────────────────────────┐  ┌─────────────────────────────┐ │
│   │ BSC VIEW                    │  │ VCI VIEW                    │  │ CONSENSUS                   │ │
│   │ Forecast: 12.8T             │  │ Forecast: 10.5T             │  │                             │ │
│   │ Ach%: 87.5% [+] BEAT        │  │ Ach%: 106.7% [+] BEAT       │  │ Both BEAT                   │ │
│   │ Revision: [^] +5%           │  │ Revision: [^] +8%           │  │ Signal: STRONG BUY          │ │
│   │ Accuracy (FPT): 88%         │  │ Accuracy (FPT): 75%         │  │ Prefer: BSC (track record)  │ │
│   └─────────────────────────────┘  └─────────────────────────────┘  └─────────────────────────────┘ │
│                                                                                                     │
│   NHẬN XÉT: VCI thận trọng quá, cả 2 cần nâng dự báo. BSC có track record tốt hơn với FPT.         │
│   ACTION: STRONG BUY - Positive momentum, consensus upgrade revision.                               │
│                                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

**Phase Roadmap:**
- **Phase 2 (MVP):** Option A (Simple Table) + Basic Surprise %
- **Phase 3 (Pro):** Option B1 (Surprise Bar) + B3 (Revision Momentum)
- **Phase 4 (Advanced):** B2 (Accuracy Leaderboard) + B4 (Triangulation)

**Option C: Scatter Plot (Forecast vs Actual)**
```
         BSC Forecast vs Actual 9M (Annualized)

    BSC 25F
    (T VND)
      50 ├──────────────────────────────●─VCB───────
         │                           ●
         │                      ●  /
      40 ├───────────────────●────/─────────────────
         │               ● ●   / CTG
         │            ●     /
      30 ├─────────●──────/─────────────────────────
         │      ●  ●   /
         │    ●     /
      20 ├───●────/─────────────────────────────────
         │ ●   /  ACB
         │  /
      10 ├/─────────────────────────────────────────
         │
       0 ├────┬────┬────┬────┬────┬────┬────┬────
            0   10   20   30   40   50   60
                    Actual 9M Annualized (T VND)

    ● Above line = BSC forecast > Actual (optimistic)
    ● Below line = BSC forecast < Actual (conservative)
    ● On line = Perfect accuracy
```

**Option D: Heatmap by Sector (Accuracy Distribution)**
```
                    FORECAST ACCURACY BY SECTOR

         Sector       │ BSC Accuracy │ VCI Accuracy │ Winner
         ─────────────┼──────────────┼──────────────┼────────
         Ngân hàng    │     85%      │     78%      │  BSC
         BĐS          │     62%      │     71%      │  VCI
         Công nghệ    │     88%      │     82%      │  BSC
         Thép         │     45%      │     52%      │  VCI
         Bán lẻ       │     72%      │     69%      │  BSC
         ─────────────┼──────────────┼──────────────┼────────
         OVERALL      │     72%      │     68%      │  BSC
```

#### Recommendation:

**Phân Phase:**
- **Phase 2 (MVP):** Option A (Enhanced Table) - simple, actionable
- **Phase 3 (Advanced):** Add Option B (Scorecard) + Option C (Scatter)

**Key Insight cho User:**
> "BSC dự báo NPATMI 25F của ACB là 17.9T. Thực tế 9M đạt 14.2T (79.3%).
> Nếu annualize: 14.2T / 0.75 = 18.9T → BSC có thể cần **revise up 5.6%**"

### MOCKUP: BSC vs VCI Consensus Tab

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    BSC vs VCI Consensus Comparison                                          │
│                               75 overlapping stocks between BSC (92) and VCI (83)                           │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                             │
│  View: [● Table] [○ Scatter Plot] [○ Sector Bar]                    Filter Consensus: [All ▼]              │
│                                                                                                             │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                             │
│  ┌────────┬────────────┬────────────┬───────────┬────────┬────────┬─────────┬───────────────────┐         │
│  │ SYMBOL │BSC NPAT25F │VCI NPAT25F │ NPAT DIFF │ BSC TP │ VCI TP │ TP DIFF │    CONSENSUS      │         │
│  ├────────┼────────────┼────────────┼───────────┼────────┼────────┼─────────┼───────────────────┤         │
│  │ ACB    │   17.9T    │   17.9T    │   +0.0%   │ 33,000 │ 33,300 │  -0.9%  │ [=] ALIGNED       │         │
│  │ VCB    │   45.2T    │   42.0T    │   +7.6%   │108,000 │ 95,000 │ +13.7%  │ [B] BSC BULLISH   │         │
│  │ CTG    │   30.3T    │   30.3T    │   +0.0%   │ 65,000 │ 65,000 │  +0.0%  │ [=] ALIGNED       │         │
│  │ HPG    │   15.0T    │   18.5T    │  -18.9%   │ 28,000 │ 32,000 │ -12.5%  │ [V] VCI BULLISH   │         │
│  │ VNM    │    8.5T    │    7.2T    │  +18.1%   │ 72,000 │ 68,000 │  +5.9%  │ [B] BSC BULLISH   │         │
│  │ FPT    │   12.8T    │   10.5T    │  +21.9%   │145,000 │125,000 │ +16.0%  │ [!] DIVERGENT     │         │
│  │ ...    │    ...     │    ...     │    ...    │  ...   │  ...   │   ...   │     ...           │         │
│  └────────┴────────────┴────────────┴───────────┴────────┴────────┴─────────┴───────────────────┘         │
│                                                                                                             │
│  Legend: [=] ALIGNED (<5%) | [B] BSC BULL (BSC>VCI >5%) | [V] VCI BULL (VCI>BSC >5%) | [!] DIVERGENT (>20%)│
│                                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

SCATTER PLOT VIEW:
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        Target Price: BSC vs VCI                                         │
│                                                                                         │
│  VCI TP                                                                                 │
│  (VND)                                              ● FPT (VCI Bull)                    │
│   150K ├──────────────────────────────────────────●─────────────────────────────────    │
│        │                                      ●                                         │
│        │                                 ●  ●      45° line                             │
│   100K ├────────────────────────────●───●──────────────/─────────────────────────────   │
│        │                        ●  ●  ●           /                                     │
│        │                    ●  ●  ●          /  ● VCB (BSC Bull)                        │
│    50K ├──────────────●──●──●────────────/──────────────────────────────────────────    │
│        │          ●●●●           /                                                      │
│        │      ●●●            /                                                          │
│     0K ├──●●─────────────/──────────────────────────────────────────────────────────    │
│        └────┬────┬────┬────┬────┬────┬────┬────┬────                                    │
│            0K   25K  50K  75K 100K 125K 150K                                            │
│                           BSC TP (VND)                                                  │
│                                                                                         │
│  ● Above line = VCI more bullish    ● Below line = BSC more bullish                    │
└─────────────────────────────────────────────────────────────────────────────────────────┘

SECTOR BAR CHART VIEW:
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                   NPATMI 2025F Comparison by Sector: BSC vs VCI                         │
│                                                                                         │
│                                                                                         │
│  Banks      ████████████████████████████████████ 125.3T (BSC)                           │
│             ██████████████████████████████████   120.0T (VCI)  -4.2% [=]               │
│                                                                                         │
│  Real Est   ████████████████  42.5T (BSC)                                               │
│             ██████████████    38.0T (VCI)  -10.6% [B]                                  │
│                                                                                         │
│  Retail     ██████████  28.0T (BSC)                                                     │
│             ██████████  29.5T (VCI)   +5.4% [V]                                        │
│                                                                                         │
│  Steel      █████████  22.5T (BSC)                                                      │
│             ██████████ 25.8T (VCI)  +14.7% [V]                                         │
│                                                                                         │
│  Tech       ███████  18.2T (BSC)                                                        │
│             █████    14.5T (VCI)   -20.3% [!]                                          │
│                                                                                         │
│             └────┬────┬────┬────┬────┬────┬────┬────                                    │
│                 0T   25T  50T  75T 100T 125T                                            │
│                                                                                         │
│  Legend: ███ BSC  ███ VCI   [=] Aligned  [B] BSC>VCI  [V] VCI>BSC  [!] Divergent       │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

#### Feature 4: Unified Filter System

**CURRENT APPROACH:**
```
Sidebar Filters:
├── Rating (multiselect)
├── Sector (dropdown)
├── Sort By (dropdown)
└── Refresh button

In-Page Filters:
├── Tab-specific radio buttons
└── Sub-tab selections
```

| Pros (Current) | Cons (Current) |
|----------------|----------------|
| ✓ Familiar Streamlit pattern | ✗ Sidebar takes screen space |
| ✓ Persistent across navigation | ✗ Filters not synced with in-page |
| | ✗ Sector filter doesn't work on Earnings view |
| | ✗ Confusing which filter applies where |

**PROPOSED APPROACH:**
```
Horizontal Filter Bar (below header):
├── [Sector ▼] [Rating ▼] [Source ▼] [Sort ▼]
├── Applied filter chips with × clear
└── All tabs respect same filters
```

| Pros (Proposed) | Cons (Proposed) |
|-----------------|-----------------|
| ✓ Single source of truth | ✗ Loses sidebar real estate for other pages |
| ✓ More horizontal space for content | ✗ Filter bar takes vertical space |
| ✓ Clear visual of active filters | ✗ Need to refactor session state |
| ✓ "Source" filter for BSC/VCI toggle |  |

**VERDICT:** Proposed is cleaner, but suggest hybrid approach

**HYBRID RECOMMENDATION:**
- Keep sidebar for GLOBAL filters (used across all pages)
- Use in-page filter bar for FORECAST-SPECIFIC filters
- This avoids full refactor while solving sync issues

---

#### Feature 5: Enhanced Candlestick/Box Chart

**CURRENT APPROACH:**
```
Valuation Matrix Chart:
├── Box plot (P25-P75 historical)
├── Single forward marker (diamond)
└── TTM marker (circle)
```

| Pros (Current) | Cons (Current) |
|----------------|----------------|
| ✓ Already functional | ✗ Only shows 2025 forward |
| ✓ Uses existing valuation_charts.py | ✗ No visual for 2026 trend |
| | ✗ Legend could be clearer |

**PROPOSED APPROACH:**
```
Enhanced Chart:
├── Box plot (P25-P75)
├── Circle (●) = TTM
├── Diamond Amber (◇) = FWD 2025
├── Diamond Purple (◆) = FWD 2026
└── Trend arrow if FWD26 < FWD25 < TTM
```

| Pros (Proposed) | Cons (Proposed) |
|-----------------|-----------------|
| ✓ Shows 2-year trend | ✗ Chart gets busier |
| ✓ Easy to spot improving stocks | ✗ Need to update valuation_charts.py |
| ✓ Purple/Amber color differentiation | ✗ May overlap on dense data |

**VERDICT:** Proposed is better - minimal effort, high visual value

**RISK MITIGATION:**
- Use offset for overlapping markers
- Add hover tooltip with all values
- Make 2026 marker slightly smaller

---

#### Feature 6: Sector Universal Comparison

**CURRENT APPROACH:**
```
Sector Tab:
├── Sector PE/PB/Upside columns
└── No BSC Universal benchmark row
```

| Pros (Current) | Cons (Current) |
|----------------|----------------|
| ✓ Simple sector list | ✗ No benchmark for comparison |
| | ✗ Can't answer "is Banks cheaper than overall?" |
| | ✗ Missing "vs Universe" relative metric |

**PROPOSED APPROACH:**
```
Enhanced Sector Tab:
├── BSC UNIVERSAL row (highlighted) at top
├── "vs Universe" column: Sector PE / Universe PE - 1
├── Total NPATMI columns
└── Earnings growth for sector aggregate
```

| Pros (Proposed) | Cons (Proposed) |
|-----------------|-----------------|
| ✓ Clear benchmark reference | ✗ Slightly more complex calculation |
| ✓ "vs Universe" shows relative value | ✗ Extra row may confuse |
| ✓ Professional institutional view |  |

**VERDICT:** Proposed is better - standard institutional analysis format

### MOCKUP: Sector Table with BSC Universal

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                         Sector Forward Valuation                                                    │
│                                 PE/PB Forward 2025-2026 with BSC Universal Benchmark                                │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                     │
│  ┌────────────────┬────────┬────────────┬────────────┬─────────┬─────────┬─────────┬─────────────┬─────────┐       │
│  │ SECTOR         │ STOCKS │ TOT NPAT25 │ TOT NPAT26 │ GROW %  │ PE 25F  │ PE 26F  │ vs UNIVERSE │ UPSIDE  │       │
│  ├────────────────┼────────┼────────────┼────────────┼─────────┼─────────┼─────────┼─────────────┼─────────┤       │
│  │ * BSC UNIV     │   92   │   235.5T   │   298.7T   │ +26.8%  │  11.2x  │   9.2x  │  Benchmark  │ +18.5%  │       │  <- Highlighted row
│  ├────────────────┼────────┼────────────┼────────────┼─────────┼─────────┼─────────┼─────────────┼─────────┤       │
│  │ Banks          │   15   │   125.3T   │   155.8T   │ +24.3%  │   8.5x  │   7.2x  │  -24.1% [+] │ +22.1%  │       │
│  │ Real Estate    │   12   │    42.5T   │    58.2T   │ +36.9%  │  14.2x  │  11.5x  │  +26.8% [-] │ +15.2%  │       │
│  │ Retail         │    8   │    28.0T   │    32.5T   │ +16.1%  │  18.5x  │  16.2x  │  +65.2% [-] │ +12.8%  │       │
│  │ Steel          │    6   │    22.5T   │    28.8T   │ +28.0%  │  12.8x  │  10.5x  │  +14.3% [=] │ +18.5%  │       │
│  │ Technology     │    5   │    18.2T   │    22.5T   │ +23.6%  │  16.5x  │  13.8x  │  +47.3% [-] │ +25.2%  │       │
│  │ F&B            │    7   │    15.8T   │    18.2T   │ +15.2%  │  22.5x  │  19.8x  │ +100.9% [-] │ +10.5%  │       │
│  │ Utilities      │    4   │    12.5T   │    14.8T   │ +18.4%  │   9.2x  │   8.0x  │  -17.9% [+] │ +14.2%  │       │
│  │ ...            │  ...   │    ...     │    ...     │   ...   │   ...   │   ...   │     ...     │   ...   │       │
│  └────────────────┴────────┴────────────┴────────────┴─────────┴─────────┴─────────┴─────────────┴─────────┘       │
│                                                                                                                     │
│  vs Universe Legend:  [+] Cheaper (<-10%)  |  [=] Fair (-10% to +20%)  |  [-] Expensive (>+20%)                    │
│  Formula: (Sector PE / BSC Universe PE) - 1                                                                        │
│                                                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### MOCKUP: Enhanced Candlestick/Box Chart (TTM vs FWD 2025 vs FWD 2026)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    PE Valuation Matrix: Banking Sector                                                      │
│                    Historical Distribution (P5-P95) vs Current & Forward                                    │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                             │
│  PE                                                                                                         │
│  Ratio                                                                                                      │
│                                                                                                             │
│   18 ├───────────────────────────────────────────────────────────────────────────────────────────────────   │
│      │                                                                                                      │
│   16 ├─────────────────────●───────────────────────────────────────────────────────────────────────────     │
│      │                     │                                                                                │
│   14 ├───────────────┬─────┴─────┬─────────────────────────────────────────────────────────────────────     │
│      │           ┌───┤  ●  ◇     │                                                   P95                    │
│   12 ├───────────│   │     ◆     ├───────●──────────────────────────────────────────────────────────────    │
│      │       ┌───┤   ├───────────┤   ┌───┤                                                                  │
│   10 ├───────│   │   │   ●       │   │   │  ◇                                                               │
│      │   ┌───┤   │   │     ◇     ├───┤   │    ◆    ●                                           P75          │
│    8 ├───│   │   │   │       ◆   │   │   ├───────────┬───────●───────────────────────────────────────────   │
│      │   │   │   │   │           │   │   │       ┌───┤   ◇                                                  │
│    6 ├───┤   │   │   │           │   │   │   ┌───┤   │     ◆             ●                     P25          │
│      │   │   ├───┘   │           ├───┘   │   │   │   ├───────┬───────────┬───────◇─────────────────────     │
│    4 ├───┴───┴───────┴───────────┴───────┴───┴───┴───┴───────┤       ┌───┤         ◆           P5           │
│      │                                                       │       │   │                                  │
│    2 ├───────────────────────────────────────────────────────┴───────┴───┴─────────────────────────────     │
│      │                                                                                                      │
│    0 └───────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┬───────────────────────       │
│             ACB     BID     CTG     MBB     STB     TCB     TPB     VCB     VIB                              │
│                                                                                                             │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                             │
│  LEGEND:                                                                                                    │
│  ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │  ┌────┐                                                                                            │    │
│  │  │    │  Box = Historical P25-P75 (Interquartile Range)                                            │    │
│  │  └────┘                                                                                            │    │
│  │    │     Whiskers = P5-P95 (excludes outliers)                                                     │    │
│  │                                                                                                    │    │
│  │    ●     TTM = Current Trailing PE (circle, white)                                                 │    │
│  │    ◇     FWD 2025 = Forward PE 2025 (diamond, amber #F59E0B)                                       │    │
│  │    ◆     FWD 2026 = Forward PE 2026 (diamond filled, purple #8B5CF6)                               │    │
│  │                                                                                                    │    │
│  │  INTERPRETATION:                                                                                   │    │
│  │  * If forward < TTM -> Improving trend (earnings growing faster than price) [+]                   │    │
│  │  * If forward > TTM -> Deteriorating trend (earnings slowing) [-]                                 │    │
│  │  • Position vs Box: Below P25 = Cheap, Above P75 = Expensive                                       │    │
│  └────────────────────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

TREND INDICATOR EXAMPLES:
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│  ACB: TTM 10.5 -> 25F 7.0 -> 26F 5.9   -44% over 2 years = STRONG IMPROVEMENT [+]    │
│  VCB: TTM 12.2 -> 25F 9.2 -> 26F 8.1   -34% over 2 years = GOOD IMPROVEMENT [+]      │
│  VIB: TTM 5.8  -> 25F 6.2 -> 26F 6.8   +17% over 2 years = SLOWING GROWTH [-]        │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Implementation Phases

### Phase 1: Core UX Improvements (P1) - Day 1-2

**Goal:** Eliminate tab switching, add quick insights

| Task | File | Effort | Status |
|------|------|--------|--------|
| 1.0 Add achievement_summary service method | `forecast_service.py` | 0.5h | ✅ Done (P0) |
| 1.1 Create unified stock table component | `WEBAPP/components/tables/unified_forecast_table.py` | 2h | 🔜 |
| 1.2 Refactor Tab 0 (Individual) to use unified table | `forecast_dashboard.py` | 1h | 🔜 |
| 1.3 Remove sub-tabs from Individual | `forecast_dashboard.py` | 0.5h | 🔜 |
| 1.4 Create achievement cards component | `WEBAPP/components/cards/achievement_cards.py` | 1.5h | 🔜 |
| 1.5 Integrate cards into Tab 2 (Achievement) | `forecast_dashboard.py` | 1h | 🔜 |
| 1.6 Add card click filtering | `session_state.py` + `forecast_dashboard.py` | 1h | 🔜 |

**Deliverables:**
- ✅ Single unified stock table (no sub-tabs)
- ✅ 3 clickable achievement cards
- ✅ Filter by achievement status

---

### Phase 2: VCI Integration (P2) - Day 2-3

**Goal:** Add consensus comparison capability

| Task | File | Effort | Status |
|------|------|--------|--------|
| 2.1 Add VCI data loading to ForecastService | `forecast_service.py` | 1h | ✅ Done (P0) |
| 2.2 Create BSC-VCI merge function | `forecast_service.py` | 1.5h | ✅ Done (P0) |
| 2.3 Create consensus comparison table | `components/tables/consensus_table.py` | 1.5h | 🔜 |
| 2.4 Create BSC vs VCI scatter chart | `components/charts/consensus_charts.py` | 1.5h | 🔜 |
| 2.5 Create sector NPATMI comparison bar | `components/charts/consensus_charts.py` | 1h | 🔜 |
| 2.6 Add Tab 3 (Consensus) to dashboard | `forecast_dashboard.py` | 1.5h | 🔜 |
| 2.7 Update session state for consensus tab | `session_state.py` | 0.5h | 🔜 |

**Deliverables:**
- ✅ BSC vs VCI comparison table
- ✅ Target price scatter plot
- ✅ Sector NPATMI bar chart

---

### Phase 3: Visual Enhancements (P3) - Day 3-4

**Goal:** Polish charts and sector view

| Task | File | Effort |
|------|------|--------|
| 3.1 Add 2026 forward marker to box chart | `components/charts/valuation_charts.py` | 1h |
| 3.2 Add trend arrows for improving stocks | `components/charts/valuation_charts.py` | 0.5h |
| 3.3 Add BSC Universal row to sector table | `forecast_service.py` | 0.5h |
| 3.4 Add "vs Universe" column | `forecast_dashboard.py` | 0.5h |
| 3.5 Merge sector sub-tabs (optional) | `forecast_dashboard.py` | 1h |
| 3.6 Add Total NPATMI columns to sector | `forecast_dashboard.py` | 0.5h |
| 3.7 Review and test all changes | - | 1h |

**Deliverables:**
- ✅ Enhanced box chart with 2025/2026 markers
- ✅ BSC Universal benchmark row
- ✅ "vs Universe" relative valuation column

---

## 3. File Changes Summary

### New Files to Create

| File | Purpose | Phase |
|------|---------|-------|
| `WEBAPP/components/tables/unified_forecast_table.py` | Unified stock table with column groups | P1 |
| `WEBAPP/components/cards/achievement_cards.py` | 3 clickable action cards | P1 |
| `WEBAPP/components/tables/consensus_table.py` | BSC vs VCI comparison table | P2 |
| `WEBAPP/components/charts/consensus_charts.py` | Scatter + bar charts for consensus | P2 |

### Existing Files to Modify

| File | Changes | Phase |
|------|---------|-------|
| `WEBAPP/pages/forecast/forecast_dashboard.py` | Tab restructure, remove sub-tabs, add consensus tab | P1, P2 |
| `WEBAPP/services/forecast_service.py` | Add VCI methods, BSC-VCI merge, achievement summary | P1, P2 |
| `WEBAPP/core/session_state.py` | Add achievement_filter, consensus states | P1, P2 |
| `WEBAPP/components/charts/valuation_charts.py` | Add 2026 marker, trend arrows | P3 |

---

## 4. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FORECAST DASHBOARD                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐     │
│  │ bsc_individual  │    │ bsc_sector_val   │    │ vci_coverage_univ  │     │
│  │   .parquet      │    │   .parquet       │    │   .parquet         │     │
│  └────────┬────────┘    └────────┬─────────┘    └─────────┬──────────┘     │
│           │                      │                        │                 │
│           ▼                      ▼                        ▼                 │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                      ForecastService                                │    │
│  ├────────────────────────────────────────────────────────────────────┤    │
│  │ get_individual_stocks()  │ get_vci_consensus() (NEW)               │    │
│  │ get_sector_valuation()   │ get_bsc_vs_vci_comparison() (NEW)       │    │
│  │ get_summary_stats()      │ get_achievement_summary() (NEW)         │    │
│  └──────────┬─────────────────────────────┬───────────────────────────┘    │
│             │                             │                                 │
│             ▼                             ▼                                 │
│  ┌──────────────────────┐      ┌──────────────────────────┐                │
│  │  Tab: BSC Universal │      │  Tab: BSC vs Consensus   │                │
│  │  - unified table     │      │  - comparison table      │                │
│  │  - column toggles    │      │  - scatter plot          │                │
│  └──────────────────────┘      │  - sector bar chart      │                │
│                                └──────────────────────────┘                │
│  ┌──────────────────────┐      ┌──────────────────────────┐                │
│  │  Tab: Sector Analysis│      │  Tab: Achievement Tracker│                │
│  │  - BSC Universal row │      │  - 3 action cards        │                │
│  │  - vs Universe col   │      │  - filtered table        │                │
│  └──────────────────────┘      └──────────────────────────┘                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Session State Updates

```python
# WEBAPP/core/session_state.py

PAGE_STATE_DEFAULTS['forecast'] = {
    # Tab navigation
    'forecast_active_tab': 0,      # 0=Stock, 1=Sector, 2=Achievement, 3=Consensus

    # Filters (shared across tabs)
    'forecast_sector_filter': 'All',
    'forecast_rating_filter': ['STRONG BUY', 'BUY', 'HOLD'],
    'forecast_sort': 'upside_desc',

    # Achievement-specific
    'achievement_filter': 'all',   # all, revise_up, on_track, revise_down

    # Consensus-specific (NEW)
    'consensus_view': 'table',     # table, scatter, bar
    'consensus_filter': 'all',     # all, aligned, bsc_bull, vci_bull, divergent

    # Column toggles
    'stock_table_extended': False, # Show extended columns
}
```

---

## 6. Dependencies & Risks

### Dependencies

| Dependency | Status | Risk Level |
|------------|--------|------------|
| VCI parquet data exists | Confirmed | Low |
| Ticker matching BSC ↔ VCI | No mapping needed | Low |
| Plotly scatter/bar charts | Already used | Low |
| Achievement data in BSC | Confirmed | Low |

**Note:** Sector mapping is NOT needed. BSC sector is the standard. Only match by ticker symbol.

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| VCI ticker mismatch with BSC | Low | Low | Join by ticker, use BSC sector as standard |
| Table too wide on smaller screens | Low | Medium | Implement responsive column hiding |
| Card click state not persisting | Low | Low | Use session_state properly |
| Performance with large merged data | Low | Low | Cache merged DataFrame |

---

## 7. Testing Checklist

### Phase 1 Testing
- [ ] Unified table renders all columns correctly
- [ ] Column toggle shows/hides extended columns
- [ ] Achievement cards show correct counts
- [ ] Card click filters table correctly
- [ ] "Show All" clears filter

### Phase 2 Testing
- [ ] VCI data loads without errors
- [ ] BSC-VCI merge handles missing tickers
- [ ] Consensus classification is correct
- [ ] Scatter plot shows 45° reference line
- [ ] Bar chart groups BSC vs VCI correctly

### Phase 3 Testing
- [ ] Box chart shows both 2025/2026 markers
- [ ] Markers don't overlap excessively
- [ ] BSC Universal row highlights correctly
- [ ] "vs Universe" calculation is accurate

---

## 8. Success Metrics

| Metric | Current | Target | How to Measure |
|--------|---------|--------|----------------|
| Clicks to see full stock data | 2 | 0 | User testing |
| Tabs to navigate | 5 | 4 | Count |
| Time to identify revise candidates | ~30s (scan table) | ~3s (cards) | User testing |
| BSC vs external comparison | Not possible | Fully supported | Feature exists |

---

## 9. Rollback Plan

Each phase is independent. If issues arise:

1. **Phase 1 rollback:** Revert to 2 sub-tabs in Individual (minimal disruption)
2. **Phase 2 rollback:** Hide Consensus tab via feature flag
3. **Phase 3 rollback:** Keep single forward marker in chart

---

## 10. Next Steps

1. ✅ User approves this plan
2. 🔲 Execute Phase 1 (1.5 days)
3. 🔲 Demo Phase 1 to user
4. 🔲 Execute Phase 2 (1.5 days)
5. 🔲 Execute Phase 3 (1 day)
6. 🔲 Final testing and polish

---

**Plan Author:** Claude Code (Planning Mode)
**Based on:** Brainstorm Report 2025-12-30
