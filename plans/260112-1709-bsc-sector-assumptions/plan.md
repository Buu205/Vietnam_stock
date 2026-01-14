# BSC Sector Assumptions Tab - Implementation Plan

**Status:** `completed`
**Created:** 2026-01-12
**Type:** Feature Implementation

---

## 1. Problem Statement

User cần xem **sector assumptions** từ BSC masterfiles, hiển thị full detail metrics cho từng ngành với UI/UX clean, organized by sector.

**Current State:**
- BSC Forecast dashboard có các tabs: BSC Universal, Sector, Achievement, Consensus
- Data nằm trong 4 Excel masterfiles với sheet `read_python`

**Target State:**
- Thêm sub-tab "Sector Assumptions" trong BSC Forecast
- Selector để chọn sector (Banking, Brokerage, MWG, Utility)
- Display full metrics với Cards + Table layout
- Theme: Crypto Terminal Glassmorphism (consistent với dashboard)

---

## 2. Data Sources

### 2.1 Banking Sector
**Data Sources:**
| Category | Source | Description |
|----------|--------|-------------|
| **Stock Info** | BSC Forecast (existing) | Rating, Target Price, Closing Price, Upside |
| **Valuation** | BSC Forecast (existing) | EPS, P/E, BVPS, P/B |
| **Quality** | Excel `read_python` | Credit Growth, NPL, NPL Formation, Credit Cost |
| **Efficiency** | Excel `read_python` | NIM, CIR, ROAA, ROAE |
| **Size** | Excel `read_python` | Total Assets, Equity, CAR |
| **Income** | Excel `read_python` | NII, NoII, TOI, PBT, NPATMI, %YoY growth |

**Excel File:** `BSC_masterfile/Banking Masterfile.xlsx` → Sheet `read_python`

### 2.2 Brokerage Sector
**File:** `BSC_masterfile/Brokerage Masterfile.xlsx`
**Sheet:** `read_python`
**Data:** Market share time series by quarter (2016-present)
**Tickers:** VPS, SSI, VND, HCM, VCI, TCBS, MAS, MBS, FTS, KIS, BSC, SHS

### 2.3 MWG Sector
**File:** `BSC_masterfile/MWG 29.12.2025.xlsx`
**Sheet:** `Read_python`
**Metrics:**
- Business segments: TGDĐ+ĐMX, BHX (revenue, store count, DT/CH/Tháng)
- Financials: DTT, LNG, EBIT, LNTT, LNST, EPS
- Quarterly breakdown: Q1-Q4 2024, Q1-Q3 2025

**Sheet:** `bhx_monthly_tracking`
- BHX store expansion by province/month

**Sheet:** `bhx`
- Historical BHX performance (2016-2026F)

### 2.4 Utility Sector
**File:** `BSC_masterfile/Masterfile_Utitlities.xlsx`
**Sheet:** `Tổng hợp định giá` (Valuation Summary)
**Structure:** Project-level valuation data grouped by type
**Types:** Thủy điện (Hydro), Điện gió (Wind), Điện mặt trời (Solar)
**Companies:** HDG, PC1, REE, GEG, GEX, DPG, TTA
**Metrics per project:**
- Công suất (MW) - Capacity
- Tổng mức đầu tư (tỷ VND) - Total Investment
- Suất đầu tư (tỷ VND/MW) - Investment per MW
- Định giá (tỷ VND) - Valuation
- Định giá mỗi công suất - Valuation per MW
- Hiệu suất hoạt động - Operating Efficiency

---

## 3. UI/UX Design

### 3.1 Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  BSC Forecast Analysis                                      │
├─────────────────────────────────────────────────────────────┤
│  [BSC Universal] [Sector] [Achievement] [Consensus] [Assumptions]
│
│  ┌─────────────────────────────────────────────────────────┐
│  │  Sector Selector:  [Banking ▼]  [Brokerage] [MWG] [Utility]
│  └─────────────────────────────────────────────────────────┘
│
│  ═══════════════════════════════════════════════════════════
│  SUMMARY CARDS (Sector-specific KPIs)
│  ═══════════════════════════════════════════════════════════
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  │ Avg ROE  │ │ Avg NIM  │ │ Avg NPL  │ │ Stocks   │
│  │  15.2%   │ │   3.8%   │ │   1.5%   │ │   17     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘
│
│  ═══════════════════════════════════════════════════════════
│  DETAIL TABLE (Full metrics - scrollable horizontally)
│  ═══════════════════════════════════════════════════════════
│  ┌─────────────────────────────────────────────────────────┐
│  │ Ticker | Rating | TP | Price | Upside | NII 25F | ... │
│  ├─────────────────────────────────────────────────────────┤
│  │ VCB    | BUY    | 73k| 57k   | +28.6% | 56T     | ... │
│  │ BID    | HOLD   | 44k| 37k   | +18.7% | 62T     | ... │
│  └─────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Sector-Specific Cards Design

#### Banking Cards (4 KPI cards)
**Note:** Stock Info + Valuation từ BSC Forecast, Quality/Efficiency từ Excel
```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ STOCKS COVERED │  │   AVG ROE 25F  │  │  AVG NIM 25F   │  │  AVG NPL 25F   │
│      17        │  │     15.2%      │  │     3.8%       │  │     1.5%       │
│   [purple]     │  │    [green]     │  │    [cyan]      │  │   [amber]      │
│ (BSC Forecast) │  │    (Excel)     │  │    (Excel)     │  │    (Excel)     │
└────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘
```

#### Brokerage Cards (4 KPI cards)
```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ BROKERS TRACKED│  │  TOP 3 SHARE   │  │  VPS SHARE     │  │  SSI SHARE     │
│      14        │  │     42.8%      │  │     14.2%      │  │     12.1%      │
│   [purple]     │  │    [green]     │  │    [cyan]      │  │   [amber]      │
└────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘
```

#### MWG Cards (4 KPI cards)
```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│  DTT 2025F     │  │  TGDĐ STORES   │  │   BHX STORES   │  │  LNST 2025F    │
│    160T        │  │     3,029      │  │     2,537      │  │    6.8T        │
│   [purple]     │  │    [green]     │  │    [cyan]      │  │   [amber]      │
└────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘
```

#### Utility Cards (4 KPI cards)
**Note:** Data từ sheet "Tổng hợp định giá" - project-level valuation
```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ TOTAL PROJECTS │  │ TOTAL CAPACITY │  │ AVG VAL/MW     │  │ COMPANIES      │
│      40+       │  │   ~3,000 MW    │  │  20 tỷ/MW      │  │   7 (HDG,REE)  │
│   [purple]     │  │    [green]     │  │    [cyan]      │  │   [amber]      │
└────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘

Project types summary:
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   THỦY ĐIỆN    │  │   ĐIỆN GIÓ     │  │ ĐIỆN MẶT TRỜI │
│  Hydro: 19 dự │  │  Wind: 11 dự   │  │  Solar: 10 dự  │
│  Avg: 26 tỷ/MW │  │ Avg: 13 tỷ/MW  │  │ Avg: 14 tỷ/MW  │
└────────────────┘  └────────────────┘  └────────────────┘
```

### 3.3 Table Design (Glassmorphism Style)

```css
/* Styled Table - Crypto Terminal Theme */
.sector-assumptions-table {
  background: linear-gradient(180deg, #1A1625 0%, #0F0B1E 100%);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 12px;
}

/* Header Row - Purple Accent */
.sector-assumptions-table thead tr {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(6, 182, 212, 0.1));
}

/* Ticker Column - Sticky + Highlighted */
.sector-assumptions-table td:first-child {
  position: sticky;
  left: 0;
  background: rgba(26, 22, 37, 0.98);
  color: #00C9AD; /* Teal for ticker */
  font-weight: 600;
}

/* Rating Badge Colors */
.rating-buy { color: #22C55E; background: rgba(34, 197, 94, 0.2); }
.rating-hold { color: #FFC132; background: rgba(255, 193, 50, 0.2); }
.rating-sell { color: #EF4444; background: rgba(239, 68, 68, 0.2); }

/* Upside Colors */
.upside-positive { color: #00C9AD; }
.upside-negative { color: #FC8181; }

/* Growth Colors */
.growth-positive { color: #10B981; }
.growth-negative { color: #EF4444; }
```

### 3.4 Selector Design (Pill Buttons)

```
┌─────────────────────────────────────────────────────────────┐
│  Select Sector                                              │
│                                                             │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │
│  │  Banking  │ │ Brokerage │ │    MWG    │ │  Utility  │  │
│  │  [active] │ │           │ │           │ │           │  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Active state:
- Background: linear-gradient(135deg, #8B5CF6, #7C3AED)
- Text: white
- Box-shadow: 0 0 20px rgba(139, 92, 246, 0.3)

Inactive state:
- Background: rgba(255, 255, 255, 0.03)
- Border: 1px solid rgba(255, 255, 255, 0.08)
- Text: #94A3B8
```

---

## 4. Implementation Approach

### Option A: Sub-Tab under Forecast (Recommended)
- Add "Assumptions" as 5th tab in forecast_dashboard.py
- Create `WEBAPP/pages/forecast/tabs/assumptions_tab.py`
- Pros: Consistent with existing structure, easy navigation
- Cons: Adds complexity to forecast tabs

### Option B: Separate Page
- Create `WEBAPP/pages/assumptions/` with its own dashboard
- Pros: Clean separation, scalable
- Cons: Requires new navigation entry

**Decision: Option A** - More cohesive user experience within BSC Forecast context.

---

## 5. File Structure

```
WEBAPP/pages/forecast/
├── forecast_dashboard.py          # Add tab 4: "Assumptions"
├── tabs/
│   ├── __init__.py               # Update exports
│   ├── bsc_universal_tab.py
│   ├── sector_tab.py
│   ├── achievement_tab.py
│   ├── bsc_vs_consensus_tab.py
│   └── assumptions_tab.py        # NEW - Sector Assumptions

WEBAPP/services/
└── assumptions_service.py        # NEW - Data loading/parsing service
```

---

## 6. Implementation Steps

### Phase 1: Data Service (assumptions_service.py)
1. Create `AssumptionsService` class
2. Implement Excel parsers for each masterfile:
   - `load_banking_assumptions()` - Parse Banking Masterfile
   - `load_brokerage_assumptions()` - Parse Brokerage Masterfile
   - `load_mwg_assumptions()` - Parse MWG Masterfile (3 sheets)
   - `load_utility_assumptions()` - Parse Utility Masterfile
3. Add caching with `@st.cache_data(ttl=3600)`

### Phase 2: Tab Implementation (assumptions_tab.py)
1. Create `render_assumptions_tab()` function
2. Implement sector selector (radio buttons/pills)
3. Create sector-specific card renderers:
   - `render_banking_cards()`
   - `render_brokerage_cards()`
   - `render_mwg_cards()`
   - `render_utility_cards()`
4. Create sector-specific table renderers:
   - `render_banking_table()`
   - `render_brokerage_table()`
   - `render_mwg_table()`
   - `render_utility_table()`

### Phase 3: Dashboard Integration
1. Import `render_assumptions_tab` in forecast_dashboard.py
2. Add "Assumptions" to tab list
3. Add conditional rendering for tab 4

### Phase 4: Styling & Polish
1. Ensure consistent glassmorphism styling
2. Add loading states (skeleton loaders)
3. Add horizontal scroll for wide tables
4. Test responsive behavior

---

## 7. Data Parsing Logic

### Banking Parser (Merged Data)
```python
def load_banking_assumptions(forecast_service: ForecastService):
    """
    Merge BSC Forecast data with Excel assumptions.
    Stock Info + Valuation từ BSC Forecast, Quality/Efficiency/Size từ Excel.
    """
    # 1. Get base data from BSC Forecast (existing)
    bsc_df = forecast_service.get_individual_stocks()
    bank_tickers = bsc_df[bsc_df['sector'] == 'Ngân hàng']['symbol'].tolist()

    # 2. Load Excel assumptions (Quality, Efficiency, Size)
    excel_df = pd.read_excel(
        'BSC_masterfile/Banking Masterfile.xlsx',
        sheet_name='read_python',
        header=1  # Row 1 has metric names
    )

    # 3. Extract relevant columns: NIM, CIR, ROA, ROE, NPL, Credit Growth, etc.
    # 4. Merge by ticker
    merged_df = bsc_df.merge(excel_df[['Ticker', 'NIM', 'CIR', 'NPL', ...]],
                              left_on='symbol', right_on='Ticker')

    return {
        'summary': calculate_sector_averages(merged_df),
        'detail': merged_df
    }
```

### Utility Parser (Project-Level)
```python
def load_utility_assumptions():
    """
    Load project-level valuation from 'Tổng hợp định giá' sheet.
    Returns data grouped by project type (Thủy điện, Điện gió, Điện mặt trời).
    """
    df = pd.read_excel(
        'BSC_masterfile/Masterfile_Utitlities.xlsx',
        sheet_name='Tổng hợp định giá',
        header=2  # Row 2 has column names
    )

    # Clean and structure data
    df.columns = ['project', 'company', 'type', 'capacity_mw',
                  'total_investment', 'investment_per_mw',
                  'valuation', 'valuation_per_mw', 'efficiency']

    # Group by type for summary cards
    summary = df.groupby('type').agg({
        'capacity_mw': 'sum',
        'valuation_per_mw': 'mean',
        'project': 'count'
    })

    return {
        'summary': summary,
        'detail': df,
        'by_company': df.groupby('company')
    }
```

### MWG Parser (3 sheets)
```python
def load_mwg_assumptions():
    # 1. Main forecast
    main_df = pd.read_excel(..., sheet_name='Read_python')

    # 2. BHX tracking by province
    bhx_tracking = pd.read_excel(..., sheet_name='bhx_monthly_tracking')

    # 3. BHX historical
    bhx_history = pd.read_excel(..., sheet_name='bhx')

    return {
        'forecast': main_df,
        'bhx_tracking': bhx_tracking,
        'bhx_history': bhx_history
    }
```

---

## 8. Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Excel structure changes | High | Add validation, error handling |
| Large file load time | Medium | Cache with st.cache_data |
| Complex multi-row headers | Medium | Careful parsing, unit tests |
| Table too wide | Low | Horizontal scroll, column groups |

---

## 9. Success Criteria

- [ ] Sector selector works correctly (4 sectors)
- [ ] Cards display correct aggregated KPIs
- [ ] Tables show full detail metrics
- [ ] Styling consistent with dashboard theme
- [ ] Data loads within 3 seconds (with cache)
- [ ] Responsive on different screen sizes

---

## 10. Effort Estimate

| Phase | Complexity | Files Changed |
|-------|------------|---------------|
| Data Service | Medium | 1 new file |
| Tab Implementation | Medium-High | 1 new file |
| Dashboard Integration | Low | 2 files |
| Styling & Polish | Low | 1 file |

**Total: ~4-6 hours of implementation**

---

## Next Steps

1. User approval of this plan
2. Implement AssumptionsService
3. Implement assumptions_tab.py
4. Integrate into forecast_dashboard.py
5. Test and polish
