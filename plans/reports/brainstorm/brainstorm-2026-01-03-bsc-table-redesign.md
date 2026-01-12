# Brainstorm: BSC Universal Table Redesign

**Date:** 2026-01-03
**Topic:** Redesign BSC Universal table with better structure, missing columns, and improved UX

---

## Current State Analysis

### Existing Column Structure

```
CORE:       symbol, sector, rating, upside_pct
VALUATION:  pe_fwd_2025, pe_fwd_2026, pb_fwd_2025, pe_delta
EARNINGS:   npatmi_2025f, npatmi_2026f, npatmi_growth_yoy_2026
EXTENDED:   rev_2025f, rev_2026f, roe_2025f, target_price, market_cap
```

### Available Data (in parquet)

| Column | 2025F | 2026F | Notes |
|--------|-------|-------|-------|
| PE | ✅ | ✅ | Both available |
| PB | ✅ | ✅ | **PB 2026F available but NOT shown** |
| Revenue | ✅ | ✅ | In extended |
| NPATMI | ✅ | ✅ | Shown |
| EPS | ✅ | ✅ | **NOT shown in table** |
| ROE | ✅ | ✅ | Only 2025F in extended |
| ROA | ✅ | ✅ | **NOT shown** |
| Growth (Rev) | ✅ | ✅ | **NOT shown** |
| Growth (NPATMI) | ✅ | ✅ | Only 2026F shown |
| Achievement | ✅ | - | Rev + NPATMI ytd/target |

---

## Identified Issues

### 1. Missing Columns
- ❌ **PB 2026F** - Data available but not displayed
- ❌ **Δ PB** (PB Delta) - Not calculated
- ❌ **EPS** - Available but not shown
- ❌ **ROA** - Available but not shown
- ❌ **Rev Growth 2026F** - Available but not shown

### 2. Inconsistency
- PE has Delta (Δ PE), PB doesn't
- 2026 data incomplete for PB
- Growth only shown for NPATMI 2026, not Revenue

### 3. UX Issues
- Too many columns → horizontal scroll needed
- Symbol, Sector, Upside not sticky when scrolling
- No clear separation between 2025F vs 2026F metrics

---

## Design Options

### Option A: Keep Single Table + Add Missing Columns

**Add:**
- PB 2026F
- Δ PB
- Move more to Extended

**New Structure:**
```
CORE:       symbol, sector, rating, upside_pct
VALUATION:  pe_fwd_2025, pe_fwd_2026, pb_fwd_2025, pb_fwd_2026, pe_delta, pb_delta
EARNINGS:   npatmi_2025f, npatmi_2026f, npatmi_growth_yoy_2026
EXTENDED:   rev_2025f, rev_2026f, roe_2025f, roe_2026f, eps_2025f, eps_2026f, target_price, market_cap
```

**Pros:**
- Simple, single view
- Easy to compare all metrics at once

**Cons:**
- More columns = more horizontal scroll
- Info overload

### Option B: Tab-Based (2025F vs 2026F)

**Two tabs:**
- Tab 2025F: All 2025 metrics
- Tab 2026F: All 2026 metrics

**Pros:**
- Cleaner per-year view
- Less horizontal scroll

**Cons:**
- Hard to compare 2025 vs 2026 directly
- User must switch tabs

### Option C: Tab-Based (PE Focus vs PB Focus vs Earnings)

**Three tabs:**
- Valuation PE: PE 2025, PE 2026, Δ PE, related
- Valuation PB: PB 2025, PB 2026, Δ PB, related
- Earnings: NPATMI, Revenue, Growth

**Pros:**
- Focused views for specific analysis

**Cons:**
- Fragmentated data
- More clicks required

### Option D: Hybrid (Recommended) ⭐

**Single table with smarter column grouping:**

```
STICKY COLS:  symbol, sector, upside_pct
VALUATION:    pe_fwd_2025, pe_fwd_2026, Δ PE, pb_fwd_2025, pb_fwd_2026, Δ PB
EARNINGS:     npatmi_2025f, npatmi_2026f, npatmi_growth_26
EXTENDED:     rev_2025f, rev_growth_26, roe_2025f, eps_2025f, target_price, market_cap
```

**Key Changes:**
1. **Sticky columns**: Symbol, Sector, Upside fixed when scrolling
2. **Add PB 2026 + Δ PB** to Valuation group
3. **Rating move to Extended** (less important for quick scan)
4. **Rev Growth 26F** added (useful metric)
5. **EPS** added to Extended

---

## Recommended Column Structure

### Core (Sticky - Always Visible)
| Column | Notes |
|--------|-------|
| symbol | Ticker |
| sector | Industry |
| upside_pct | Key metric for quick filtering |

### Valuation Group
| Column | Current | New |
|--------|---------|-----|
| pe_fwd_2025 | ✅ | ✅ |
| pe_fwd_2026 | ✅ | ✅ |
| pe_delta | ✅ | ✅ |
| pb_fwd_2025 | ✅ | ✅ |
| pb_fwd_2026 | ❌ | ✅ NEW |
| pb_delta | ❌ | ✅ NEW |

### Earnings Group
| Column | Current | New |
|--------|---------|-----|
| npatmi_2025f | ✅ | ✅ |
| npatmi_2026f | ✅ | ✅ |
| npatmi_growth_yoy_2026 | ✅ | ✅ |

### Extended (Toggle)
| Column | Current | New | Notes |
|--------|---------|-----|-------|
| rating | In CORE | Move here | Less critical |
| rev_2025f | ✅ | ✅ | |
| rev_2026f | ✅ | ✅ | |
| rev_growth_yoy_2026 | ❌ | ✅ NEW | |
| roe_2025f | ✅ | ✅ | |
| roe_2026f | ❌ | ✅ NEW | |
| eps_2025f | ❌ | ✅ NEW | |
| eps_2026f | ❌ | ✅ NEW | |
| target_price | ✅ | ✅ | |
| market_cap | ✅ | ✅ | |

---

## Sticky Column Implementation

Current CSS has sticky for nth-child(1) and nth-child(2), but it's hardcoded.

**Recommended:**
- Make Symbol, Sector, Upside sticky (3 columns)
- Use CSS classes instead of nth-child for maintainability

```css
.sticky-col-1 { position: sticky; left: 0; z-index: 10; }
.sticky-col-2 { position: sticky; left: 70px; z-index: 10; }
.sticky-col-3 { position: sticky; left: 150px; z-index: 10; box-shadow: 2px 0 8px rgba(0,0,0,0.3); }
```

---

## Delta Calculation

### Current: PE Delta
```python
pe_delta = (pe_fwd_2026 - pe_fwd_2025) / pe_fwd_2025 * 100
```

### New: PB Delta (same logic)
```python
pb_delta = (pb_fwd_2026 - pb_fwd_2025) / pb_fwd_2025 * 100
```

**Interpretation:**
- Negative delta = valuation improves (cheaper in 2026)
- Positive delta = valuation worsens (more expensive in 2026)

---

## Sort Options Update

Current:
```python
SORT_OPTIONS = {
    'stock': [
        ('Upside ↓', 'upside_desc'),
        ('PE 25F ↓', 'pe_desc'),
        ('PB 25F ↓', 'pb_desc'),
        ...
    ]
}
```

**Add:**
- PB 26F ↓/↑
- Δ PB ↓/↑
- Rev Growth ↓

---

## Summary: Recommended Changes

| Change | Priority | Effort |
|--------|----------|--------|
| Add PB 2026F column | HIGH | Low |
| Add Δ PB column | HIGH | Low |
| Make Symbol, Sector, Upside sticky | HIGH | Medium |
| Move Rating to Extended | MEDIUM | Low |
| Add Rev Growth 2026 to Extended | MEDIUM | Low |
| Add EPS 2025/2026 to Extended | LOW | Low |
| Add ROE 2026 to Extended | LOW | Low |

---

## Files to Modify

1. `unified_forecast_table.py` - Column definitions, formatters, sticky CSS
2. `forecast_filter_bar.py` - Add PB sort options
3. `bsc_universal_tab.py` - Update sort mapping

---

## Unresolved Questions

1. Should Achievement columns (ytd/target) be shown somewhere?
2. ROA useful enough to include?
3. Tab design (2025F vs 2026F) worth pursuing later?
