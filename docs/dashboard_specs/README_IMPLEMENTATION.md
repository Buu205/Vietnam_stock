# Implementation Guide - Quick Reference
# Hướng Dẫn Triển Khai Dashboard

> **Purpose:** Quick reference for implementing each dashboard
> **Approach:** Incremental improvement of existing pages

---

## 📋 Dashboard Implementation Summary

| # | Dashboard | Existing File | Status | Priority | Estimated Time |
|---|-----------|---------------|--------|----------|----------------|
| 1 | **Company** | `company_dashboard_pyecharts.py` + `company_dashboard_v2.py` | 70% done | 🔴 HIGH | 1-2 days |
| 2 | **Bank** | `bank_dashboard.py` | Needs improvement | 🟡 MEDIUM | 2-3 days |
| 3 | **Security** | `securities_dashboard.py` | Needs improvement | 🟡 MEDIUM | 2 days |
| 4 | **Technical** | `technical_analysis.py` | Good base, enhance | 🟢 LOW | 1-2 days |
| 5 | **Valuation** | `valuation_sector_dashboard.py` | Good base, enhance | 🟢 LOW | 1-2 days |
| 6 | **Sector FA+TA** | None | Create new | 🟡 MEDIUM | 3-4 days |
| 7 | **Macro** | None | Create new | 🟢 LOW | 2-3 days |
| 8 | **Forecast** | `forecast_dashboard.py` | Needs improvement | 🟢 LOW | 2 days |

**Total Estimated Time:** 15-20 days (3-4 weeks with testing)

---

## 🎯 Implementation Strategy

### Phase 1: Quick Wins (Week 1)
**Goal:** Get 3 dashboards production-ready

1. **Company Dashboard** (Days 1-2)
   - Base: `company_dashboard_v2.py` (already 70% done)
   - Add: Balance Sheet, Cash Flow, Peer Comparison
   - Tool: `/frontend-design` for new sections

2. **Technical Dashboard** (Days 3-4)
   - Base: `technical_analysis.py` (good structure)
   - Improve: Replace any PyEcharts with Plotly
   - Add: Market regime indicators
   - Tool: Refine existing charts

3. **Valuation Dashboard** (Day 5)
   - Base: `valuation_sector_dashboard.py`
   - Improve: Add VN-Index valuation bands
   - Enhance: Sector PE comparison visuals
   - Tool: Minor tweaks only

---

### Phase 2: Financial Entities (Week 2)
**Goal:** Complete all entity-specific dashboards

4. **Bank Dashboard** (Days 6-8)
   - Base: `bank_dashboard.py`
   - Improve: Banking metrics (NIM, NPL, CAR)
   - Add: Asset quality, loan breakdown
   - Tool: `/frontend-design` for banking charts

5. **Security Dashboard** (Days 9-10)
   - Base: `securities_dashboard.py`
   - Improve: Brokerage metrics
   - Add: Market share, trading volume
   - Tool: Similar to Bank approach

---

### Phase 3: Advanced Features (Week 3)
**Goal:** Add new analytical capabilities

6. **Sector FA+TA Dashboard** (Days 11-14)
   - Base: None (create new)
   - Data: `DATA/processed/sector/` files
   - Features: Combined scores, rankings, signals
   - Tool: `/frontend-design` for all sections

7. **Macro Dashboard** (Days 15-17)
   - Base: None (create new)
   - Data: `DATA/processed/macro_commodity/`
   - Features: Interest rates, FX, commodities
   - Tool: `/frontend-design` for macro charts

---

### Phase 4: Polish (Week 4)
**Goal:** Finalize and optimize

8. **Forecast Dashboard** (Days 18-19)
   - Base: `forecast_dashboard.py`
   - Improve: BSC forecast visualization
   - Add: Accuracy tracking
   - Tool: Minor improvements

9. **Testing & Optimization** (Day 20)
   - Test all dashboards
   - Fix bugs
   - Optimize performance
   - Document changes

---

## 🛠️ Incremental Improvement Workflow

### For Each Dashboard:

**Step 1: Analyze Existing** (30 minutes)
```bash
# Open existing page
code WEBAPP/pages/{dashboard_name}.py

# Questions to answer:
# - What data sources does it use?
# - What charts are already implemented?
# - What needs improvement?
# - Are there any PyEcharts charts to replace?
```

**Step 2: Identify Improvements** (15 minutes)
- Read spec file (e.g., `01_company_dashboard.md`)
- List specific sections to add/improve
- Prioritize improvements (must-have vs nice-to-have)

**Step 3: Design with `/frontend-design`** (Per Section)
- Use plugin for each new chart/section
- Provide data structure and requirements
- Test generated code in isolation
- Refine until satisfied

**Step 4: Integrate** (Per Section)
```python
# Add new component function
# WEBAPP/components/charts/xyz_charts.py
def render_new_chart(df, ...):
    # Paste tested code from plugin
    pass

# Use in dashboard
from WEBAPP.components.charts.xyz_charts import render_new_chart
render_new_chart(df)
```

**Step 5: Test** (Per Section)
```bash
# Run dashboard
streamlit run WEBAPP/pages/{dashboard_name}.py

# Test checklist:
# - Chart renders correctly
# - Colors match brand
# - Data formats correct (Billions VND, %)
# - Responsive (narrow mode)
# - No errors in console
```

**Step 6: Move to Next Section**
- Don't try to complete entire page at once
- One section → Test → Next section
- Iterate until page is complete

---

## 📝 Per-Dashboard Improvement Notes

### 1. Company Dashboard
**Existing:** `company_dashboard_v2.py` (good base)

**Keep:**
- ✅ Sidebar filters (ticker, period, limit)
- ✅ 4 KPI cards
- ✅ Income statement chart
- ✅ Margins chart
- ✅ Summary table

**Add:**
- 🆕 ROE/ROA trend (dual-axis line)
- 🆕 Balance Sheet (stacked bar)
- 🆕 Cash Flow (waterfall)
- 🆕 Peer Comparison (horizontal bar)
- 🆕 CSV download button

**Replace:**
- None (already using Plotly)

---

### 2. Bank Dashboard
**Existing:** `bank_dashboard.py` (mixed Plotly/PyEcharts)

**Keep:**
- ✅ Sidebar structure
- ✅ Basic layout

**Improve:**
- 🔄 Replace PyEcharts charts with Plotly
- 🔄 Add banking-specific KPIs (NIM, NPL, CAR)
- 🔄 Better color coding (NPL red if >3%, green if <2%)

**Add:**
- 🆕 Asset quality section (NPL trend)
- 🆕 Loan portfolio breakdown
- 🆕 Capital adequacy (CAR, Tier 1/2)
- 🆕 Peer comparison (banking metrics)

**Use Plugin For:**
- NPL ratio with warning zones
- Loan portfolio stacked area
- Capital structure bars with regulatory lines

---

### 3. Technical Dashboard
**Existing:** `technical_analysis.py` (mostly Plotly, good base)

**Keep:**
- ✅ All existing sections (indicators, alerts, breadth)
- ✅ Chart structure

**Improve:**
- 🔄 Apply brand colors to all charts
- 🔄 Standardize chart heights and layouts

**Add:**
- 🆕 Market regime classification (visible indicator)
- 🆕 Sector rotation heatmap

**Replace:**
- Check for any remaining PyEcharts imports

---

### 4. Valuation Dashboard
**Existing:** `valuation_sector_dashboard.py` (Plotly, good)

**Keep:**
- ✅ Sector PE loading and display
- ✅ Chart structure

**Improve:**
- 🔄 Add VN-Index PE/PB bands visualization
- 🔄 Enhance sector comparison with percentile colors

**Add:**
- 🆕 Individual stock valuation (PE/PB bands)
- 🆕 Relative valuation (stock vs sector)

**Use Plugin For:**
- PE/PB bands with historical percentiles
- Valuation heatmap (sectors cheap→expensive)

---

### 5. Security Dashboard
**Existing:** `securities_dashboard.py`

**Similar to Bank Dashboard** - entity-specific metrics for securities firms

**Key Metrics:**
- Trading volume, commission income, ROE
- Market share
- Revenue breakdown (brokerage, proprietary, advisory)

---

### 6. Sector FA+TA Dashboard
**Existing:** None (create new)

**Data:** `DATA/processed/sector/sector_combined_scores.parquet`

**Sections:**
1. Sector rankings table (sortable)
2. FA score breakdown (heatmap)
3. TA score breakdown (heatmap)
4. Bubble chart (FA vs TA)
5. Buy/Sell/Hold signals

**Use Plugin For:** All sections (new page)

---

### 7. Macro Dashboard
**Existing:** None (create new)

**Data:** `DATA/processed/macro_commodity/macro_commodity_unified.parquet`

**Sections:**
1. Interest rates (line chart)
2. Exchange rates (VND/USD)
3. Commodity prices (gold, oil)
4. Correlation matrix (VN-Index vs indicators)

**Use Plugin For:** All sections (new page)

---

### 8. Forecast Dashboard
**Existing:** `forecast_dashboard.py`

**Improve:**
- 🔄 Better visualization of target prices
- 🔄 Consensus ratings display
- 🔄 Forecast accuracy tracking

---

## 🎨 Using Frontend-Design Plugin - Examples

### Example 1: Add Balance Sheet to Company Dashboard

**Prompt to plugin:**
```
Tôi muốn thêm "Balance Sheet Analysis" section vào Company Dashboard.

Context:
- Đang cải thiện existing page: WEBAPP/pages/company_dashboard_v2.py
- Section này sẽ thêm sau section "Profitability Margins"

Data structure:
- Service: CompanyService
- DataFrame columns: report_date, total_assets, total_liabilities, total_equity
- 8 quarterly periods
- Values in Billions VND
- Accounting equation: Assets = Liabilities + Equity

Requirements:
- Stacked bar chart comparing Assets vs (Liabilities + Equity)
- Assets: Single bar, brand blue (#295CA9)
- Liabilities + Equity: Stacked bars (Gold #FFC132 + Light blue #4A7BC8)
- Y-axis: "VND Billions"
- Dark theme (#0A1E42 background)
- Height: 400px
- Plotly only (không dùng PyEcharts)

Output needed:
- Complete Python function for WEBAPP/components/charts/fundamental_charts.py
- Usage example for dashboard page
```

### Example 2: Improve Existing Chart

**Prompt to plugin:**
```
Tôi muốn cải thiện Income Statement chart đang có trong Company Dashboard.

Current implementation:
- File: WEBAPP/components/charts/income_statement_chart.py
- Function: render_income_statement_chart()
- Chart: Multi-line (5 metrics: revenue, gross profit, EBIT, EBITDA, net profit)

Improvements needed:
1. Đổi colors sang brand colors:
   - Revenue: #009B87 (brand teal)
   - Gross Profit: #00C9AD (light teal)
   - EBIT: #295CA9 (brand blue)
   - Net Profit: #FFC132 (brand gold)
2. Thêm gradient fill dưới revenue line (subtle)
3. Bold latest data point (larger marker)
4. Smooth line animation

Giữ nguyên:
- Data structure (DataFrame với 5 columns)
- Chart height (450px)
- Hover behavior

Output: Updated function code
```

---

## ✅ Final Checklist (Before Moving to Next Dashboard)

For each dashboard:

**Functional:**
- [ ] All sections render without errors
- [ ] Data updates when filters change
- [ ] Charts interactive (zoom, pan, hover)
- [ ] No console errors

**Visual:**
- [ ] Brand colors used consistently
- [ ] Dark theme (#0A1E42) background
- [ ] All text readable (contrast check)
- [ ] Responsive layout (test narrow mode)

**Data:**
- [ ] Billions VND for currency (X,XXX.XB VND)
- [ ] Percentages with 2 decimals (XX.XX%)
- [ ] Ratios with 2 decimals (X.XXx)
- [ ] Dates formatted correctly (YYYY-QQ)

**Performance:**
- [ ] Page load < 2 seconds
- [ ] Chart render < 500ms each
- [ ] No unnecessary re-renders

**Code Quality:**
- [ ] No PyEcharts imports
- [ ] Components reusable (in charts/ folder)
- [ ] Code commented where needed
- [ ] No hardcoded values

---

**Status:** 🟢 READY - Follow this guide for systematic improvement of all dashboards

**Next:** Start with Company Dashboard (highest priority, already 70% done)
