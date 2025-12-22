# Phase 4: Page Organization & Layout Hierarchy

**Goal:** Restructure pages with consistent layout patterns, optimal information hierarchy
**Effort:** 3-4 days | **Risk:** Medium

---

## Current Page Structure Analysis

| Page | Current Tabs | Issues |
|------|-------------|--------|
| Company | Charts \| Tables (nested IS/BS/CF) | Too many nested levels |
| Bank | Charts \| Tables (5 nested sub-tabs) | Complex navigation |
| Sector | 6 tabs (VNIndex, Distribution, Individual, Macro, Commodity, Data) | Good structure, keep |
| Forecast | 5 tabs (Individual, Sector Val, 9M, Charts, Forward) | Good structure, keep |
| Technical | 3 tabs (Price & Volume, Oscillators, Data) | Simple, effective |
| Security | Charts \| Tables | Same as company/bank |

---

## Recommended Layout Pattern: Data-Dense Dashboard

**Pattern:** Maximum data visibility with minimal padding, grid-based

### Core Layout Structure (Per Page)

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER: Page Title + Global Filter Bar (from Phase 2)      │
├─────────────────────────────────────────────────────────────┤
│ KPI CARDS ROW: 4-6 metric cards (compact, 1rem padding)    │
├─────────────────────────────────────────────────────────────┤
│ PRIMARY CHART ZONE: Main chart 60% width | Side 40%        │
│ ┌───────────────────────────────┬─────────────────────────┐ │
│ │                               │  Secondary Chart        │ │
│ │   Main Chart (larger)        │  or Data Table          │ │
│ │                               │                         │ │
│ └───────────────────────────────┴─────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ TABS: Context-specific views (minimize to 3-4 max)          │
└─────────────────────────────────────────────────────────────┘
```

---

## Page-Specific Recommendations

### 1. Company Dashboard

**Current:** Charts tab → Tables tab → nested IS/BS/CF

**Proposed:** Flatten hierarchy, show key metrics first

```
┌─────────────────────────────────────────────────────────────┐
│ [Company Name] VCB - Vietcombank           [Metric] [Days] │
├─────────────────────────────────────────────────────────────┤
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐     │
│ │ ROE  │ │ ROA  │ │ EPS  │ │ PE   │ │ PB   │ │ D/E  │     │
│ │18.5% │ │ 2.1% │ │3,200 │ │12.3x │ │ 2.1x │ │ 0.45 │     │
│ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘     │
├─────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────┬──────────────────────────┐  │
│ │   Valuation Chart          │  Key Financials Table    │  │
│ │   (PE with mean/std)       │  (Income Statement)      │  │
│ │                            │                          │  │
│ └────────────────────────────┴──────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│ [Financials] [Balance Sheet] [Cash Flow] [Technicals]      │
└─────────────────────────────────────────────────────────────┘
```

**Implementation:**
```python
# company_dashboard.py structure
def render_company_dashboard(ticker: str):
    # 1. Header + Filter bar
    render_global_filters()

    # 2. KPI Cards (compact row)
    cols = st.columns(6)
    metrics = ['ROE', 'ROA', 'EPS', 'PE', 'PB', 'Debt/Equity']
    for i, m in enumerate(metrics):
        cols[i].metric(m, value, delta)

    # 3. Main chart + side table (60/40 split)
    chart_col, table_col = st.columns([3, 2])
    with chart_col:
        render_valuation_chart(ticker)
    with table_col:
        render_key_financials_table(ticker)

    # 4. Detail tabs (flattened)
    tab1, tab2, tab3, tab4 = st.tabs([
        "Financials", "Balance Sheet", "Cash Flow", "Technicals"
    ])
```

### 2. Sector Dashboard (Keep Current, Optimize)

**Current structure is good. Optimize visual density:**

```
Tab 1 (VNIndex): Keep histogram + time series
Tab 2 (Distribution): Sector candlestick distribution
Tab 3 (Individual): Ticker-level analysis
Tab 4 (Macro): Interest rates, FX, bonds
Tab 5 (Commodity): Gold, oil, steel, rubber
Tab 6 (Data): Export tables
```

**Add:** Sector comparison heatmap (new visualization)

### 3. Forecast Dashboard (Keep Current, Add Matrix)

**Already has good structure after Phase 2-3 refactoring**

**Add:** Forward PE/PB matrix view (grid comparison)

---

## Tab Organization Rules

### Maximum Tabs Per Page

| Page Complexity | Max Tabs | Reasoning |
|----------------|----------|-----------|
| Simple (Technical) | 3 | Price, Oscillators, Data |
| Medium (Company) | 4 | Flatten nested tabs |
| Complex (Sector) | 6 | Already optimal |

### Tab Naming Convention

```
✅ GOOD: "Financials", "Balance Sheet", "Cash Flow"
❌ BAD: "Charts", "Tables", "Data" (too generic)

✅ GOOD: "VNIndex", "Sector Distribution", "Macro"
❌ BAD: "Tab 1", "Tab 2", "Tab 3"
```

### Tab Content Rules

1. **No nested tabs** - Flatten to single level
2. **Each tab = one purpose** - Don't mix charts and tables
3. **First tab = most important** - Show key insights first
4. **Last tab = data export** - Raw data for advanced users

---

## Implementation CSS

**Add to styles.py:**

```css
/* ============================================================
   DATA-DENSE LAYOUT - GRID STRUCTURE
   ============================================================ */

/* Main content grid */
.main-content-grid {
    display: grid;
    grid-template-columns: 3fr 2fr;
    gap: 1rem;
    margin-bottom: 1rem;
}

/* KPI card row - 6 cards */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 0.75rem;
    margin-bottom: 1rem;
}

@media (max-width: 1200px) {
    .kpi-row {
        grid-template-columns: repeat(3, 1fr);
    }
}

/* Compact KPI card override */
[data-testid="stMetric"] {
    padding: 0.75rem 1rem !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
}

[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
}
```

---

## Validation Checklist

- [ ] Company dashboard uses flat tab structure
- [ ] Bank dashboard uses same pattern as company
- [ ] Sector dashboard keeps 6-tab structure
- [ ] All pages have KPI cards at top
- [ ] Main chart occupies 60%+ of width
- [ ] Tabs have descriptive names
- [ ] No nested tabs anywhere
- [ ] Mobile: KPI cards stack 3x2

---

## Rollback

If layout changes cause issues, revert to current nested tabs structure.
