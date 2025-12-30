# Phase 2: Sector Tab (Tab 1)

**Duration:** Day 2
**Priority:** P2 (Medium Impact)
**Parent Plan:** [plan.md](plan.md) | **Design:** [design-system-guide.md](design-system-guide.md)

---

## Objectives

1. Unify sector table (merge Valuation + Growth views)
2. Add Valuation Matrix chart (toggle view)
3. Filter by sector with single select

---

## Scope

**Tab 1: Sector** now contains:
- Unified sector table with all metrics in one view
- Valuation Matrix chart (PE/PB TTM vs Forward) - BSC coverage only (~92 stocks)
- Toggle between Table and Chart views

---

## Task 2.1: Unified Sector Table Component

**File:** `WEBAPP/components/tables/unified_sector_table.py`

### Columns Design

| Group | Columns | Notes |
|-------|---------|-------|
| **Core** | Sector, # Stocks | First row = BSC Universal benchmark |
| **Earnings** | Total NPATMI 25F, Total NPATMI 26F, Growth% | Aggregated |
| **Valuation** | PE 25F, PE 26F, PB 25F | Weighted average |
| **Relative** | vs Universe | (Sector PE / BSC Universe PE) - 1 |
| **Performance** | Avg Upside | Average of stocks in sector |

### BSC Universal Row

First row should be highlighted as benchmark:
```
| * BSC UNIV     |   92   |   235.5T   |   298.7T   | +26.8%  |  11.2x  |  9.2x  | Benchmark |
```

---

## Task 2.2: Valuation Matrix Chart

**File:** `WEBAPP/components/charts/valuation_matrix.py`

### Design

**Colors from [design-system-guide.md](design-system-guide.md):**

Box chart showing PE distribution by sector:
- Whiskers: P5-P95 (excludes outliers)
- Box: P25-P75
- Markers:
  - TTM (circle, white #E8E8E8)
  - FWD 2025 (diamond, amber #F59E0B - IconColor.WARNING)
  - FWD 2026 (diamond filled, purple #8B5CF6 - IconColor.PRIMARY)

### Filter

- Sector dropdown (single select)
- Shows individual stocks within selected sector
- BSC coverage only (~92 stocks)

### Interpretation

```
If forward < TTM -> Improving trend [+]
If forward > TTM -> Deteriorating trend [-]
Position vs Box: Below P25 = Cheap, Above P75 = Expensive
```

---

## Task 2.3: Toggle View Implementation

**File:** `WEBAPP/pages/forecast/forecast_dashboard.py`

```python
# Tab 1: Sector
if active_tab == 1:
    view_mode = st.radio("View", ["Table", "Chart"], horizontal=True)

    sector_filter = st.selectbox("Sector", ["All"] + sector_list)

    if view_mode == "Table":
        # Render unified sector table
        html = unified_sector_table(sector_df, highlight_benchmark=True)
        st.markdown(html, unsafe_allow_html=True)
    else:
        # Render valuation matrix
        fig = valuation_matrix_chart(filtered_df, sector=sector_filter)
        st.plotly_chart(fig, use_container_width=True)
```

---

## Task 2.4: Remove Old Sector Sub-tabs

**Current (to remove):**
```python
# REMOVE this
view_tab = render_persistent_tabs(
    ["Valuation View", "Growth View"],
    "sector_view_tab"
)
```

**New (unified):**
Single table with all columns visible.

---

## Files to Create/Modify

| File | Action | Notes |
|------|--------|-------|
| `WEBAPP/components/tables/unified_sector_table.py` | CREATE | Similar to unified_forecast_table.py |
| `WEBAPP/components/charts/valuation_matrix.py` | CREATE | Plotly box chart |
| `WEBAPP/pages/forecast/forecast_dashboard.py` | MODIFY | Tab 1 refactor |

---

## Testing Checklist

- [ ] Sector table shows all sectors with BSC Universal first
- [ ] Valuation Matrix renders correctly with markers
- [ ] Toggle between Table/Chart works
- [ ] Sector filter updates both views
- [ ] Mobile responsive

---

## Dependencies

- `unified_forecast_table.py` (Phase 1) - reuse styling patterns
- BSC forecast data with sector column
