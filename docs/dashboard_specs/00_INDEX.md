# Dashboard Specifications - Master Index
# Thiết Kế Chi Tiết Từng Dashboard

> **Created:** 2025-12-15
> **Status:** 🟢 APPROVED - Ready for implementation
> **Project:** Vietnamese Stock Market Dashboard Redesign

---

## 📋 Overview

This directory contains detailed specifications for each dashboard page in the WEBAPP redesign.

**Design Decisions (Confirmed):**
- ✅ **Chart Library:** Plotly ONLY
- ✅ **Data Units:** Billions VND (automatic conversion from VND)
- ✅ **Design Theme:** Professional Financial (Dark theme + Brand colors)
- ✅ **Total Pages:** 8 dashboards (removed Insurance)

---

## 📁 Document Structure

### Master Documents
- **[DESIGN_SYSTEM_SPEC.md](../DESIGN_SYSTEM_SPEC.md)** - Overall design system and decisions

### Individual Page Specifications

**Financial Entity Dashboards:**
1. **[01_company_dashboard.md](01_company_dashboard.md)** - Company fundamental analysis
2. **[02_bank_dashboard.md](02_bank_dashboard.md)** - Banking sector analysis
3. **[03_security_dashboard.md](03_security_dashboard.md)** - Securities/brokerage analysis

**Market Analysis Dashboards:**
4. **[04_technical_dashboard.md](04_technical_dashboard.md)** - Technical indicators & alerts
5. **[05_valuation_dashboard.md](05_valuation_dashboard.md)** - Valuation & sector PE/PB

**Advanced Analysis Dashboards:**
6. **[06_sector_dashboard.md](06_sector_dashboard.md)** - Sector FA+TA combined scores
7. **[07_macro_dashboard.md](07_macro_dashboard.md)** - Macro & commodity indicators
8. **[08_forecast_dashboard.md](08_forecast_dashboard.md)** - BSC analyst forecasts

---

## 🎨 Using Frontend-Design Plugin

Each page spec includes guidance on using the `/frontend-design` plugin to iterate on specific sections.

### How to Use the Plugin:

1. **For New Sections:**
   ```
   Tôi muốn thiết kế section "Balance Sheet Analysis" cho Company Dashboard.

   Requirements:
   - Display: Total Assets, Total Liabilities, Shareholders' Equity
   - Chart: Stacked bar chart showing asset/liability structure over time
   - Style: Dark theme with brand colors (#295CA9, #009B87, #FFC132)
   - Data: From CompanyService, columns: total_assets, total_liabilities, total_equity
   ```

2. **For Chart Improvements:**
   ```
   Tôi muốn cải thiện Income Statement chart trong Company Dashboard.

   Current: Multi-line chart with 5 metrics
   Improvements needed:
   - Add gradient fill between lines
   - Highlight latest data point
   - Add year-over-year growth annotations
   - Use brand teal color (#009B87) for revenue line
   ```

3. **For Layout Optimization:**
   ```
   Tôi muốn optimize layout của Technical Dashboard.

   Current: Single column layout, charts stacked vertically
   Goal: 2-column grid layout for better space utilization
   Sections: Price chart (full width), then 2 columns (RSI + MACD)
   ```

---

## 📊 Page Priority & Implementation Order

### Phase 1: Foundation (Week 1)
- Create service layer for all pages
- Build reusable chart components
- Remove PyEcharts, standardize on Plotly

### Phase 2: Core Pages (Week 2-3)
**Priority Order:**
1. **Company Dashboard** (70% done - extend existing)
2. **Bank Dashboard** (rebuild from scratch)
3. **Technical Dashboard** (rebuild existing page)
4. **Valuation Dashboard** (rebuild existing page)

### Phase 3: Advanced Pages (Week 4)
5. **Security Dashboard** (rebuild)
6. **Sector Dashboard** (new - FA+TA combined)
7. **Macro Dashboard** (new)
8. **Forecast Dashboard** (rebuild)

### Phase 4: Polish (Week 5)
- Performance optimization
- UX enhancements (export, tooltips)
- Documentation
- Testing

---

## 🎯 Common Patterns Across All Pages

### Standard Page Structure
```python
# Header
st.title("📊 Dashboard Name")
st.markdown("Description")
st.markdown("---")

# Sidebar Filters
st.sidebar.header("Filters")
# ... filters

# Section 1: Key Metrics (4 cards)
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
# ... metric cards

# Section 2: Main Charts
st.subheader("Chart Title")
# ... charts

# Section 3: Data Tables
st.subheader("Detailed Data")
# ... tables

# Footer
st.markdown("---")
st.caption("Data source and metadata")
```

### Standard Color Mapping
```python
from WEBAPP.core.theme import BRAND, SEMANTIC

# Financial metrics
revenue_color = SEMANTIC['revenue']      # #009B87 (brand teal)
profit_color = SEMANTIC['profit']        # #00C9AD (light teal)
expense_color = SEMANTIC['expense']      # #E63946 (red)
asset_color = SEMANTIC['asset']          # #295CA9 (brand blue)
liability_color = SEMANTIC['liability']  # #FFC132 (brand gold)
equity_color = SEMANTIC['equity']        # #4A7BC8 (light blue)

# Indicators
positive = SEMANTIC['positive']  # #00A878 (teal green)
negative = SEMANTIC['negative']  # #E63946 (red)
neutral = SEMANTIC['neutral']    # #6B7280 (gray)
```

### Standard Data Formatting
```python
# Currency (Billions VND)
f"{value:,.1f}B VND"  # 1,234.5B VND

# Percentages (2 decimals)
f"{value:.2f}%"  # 15.75%

# Ratios (2 decimals)
f"{value:.2f}x"  # 1.25x

# Dates
date_str = f"{year}-Q{quarter}"  # 2024-Q3 (quarterly)
date_str = str(year)              # 2024 (yearly)
```

---

## 📝 Each Page Spec Contains

For every dashboard page, you'll find:

1. **Page Overview**
   - Purpose and target users
   - Key features
   - Data sources

2. **Layout Design**
   - Section-by-section breakdown
   - Component placement
   - Responsive behavior

3. **Data Requirements**
   - Which service to use
   - Required columns
   - Data transformations

4. **Chart Specifications**
   - Chart types
   - Color mappings
   - Interactivity features

5. **Frontend-Design Usage**
   - Example prompts for specific sections
   - Iteration strategies
   - Common customizations

6. **Implementation Checklist**
   - Step-by-step guide
   - Testing requirements
   - Performance considerations

---

## 🚀 Getting Started

**⭐ IMPORTANT: Build Upon Existing Pages**

DO NOT rebuild from scratch! Use existing pages in `WEBAPP/pages/` as foundation:
- Giữ lại cấu trúc, logic loading data hiện tại
- Cải thiện từng section một (incremental improvement)
- Sử dụng plugin `/frontend-design` cho sections cụ thể
- Tận dụng existing databases và services

**To implement a specific dashboard:**

1. **Read existing page** (e.g., `WEBAPP/pages/company_dashboard_pyecharts.py`)
2. **Read spec** (e.g., `01_company_dashboard.md`) - see what to improve
3. **Identify sections to enhance** (e.g., "add Balance Sheet section")
4. **Use `/frontend-design` plugin** to design specific improvements
5. **Update incrementally** - one section at a time
6. **Test after each change** - ensure nothing breaks
7. **Iterate** based on user feedback

**Example workflow for Company Dashboard:**
```bash
# 1. Read spec
cat docs/dashboard_specs/01_company_dashboard.md

# 2. Test service
python3 -c "from WEBAPP.services.company_service import CompanyService; print(CompanyService().get_available_tickers())"

# 3. Use frontend-design plugin (in chat)
# "Tôi muốn thiết kế Balance Sheet section cho Company Dashboard..."

# 4. Implement
# Edit WEBAPP/pages/1_company_dashboard.py

# 5. Test
streamlit run WEBAPP/pages/1_company_dashboard.py
```

---

## 💡 Tips for Using Frontend-Design Plugin

**Best Practices:**

1. **Be Specific:** Provide exact data structure, column names, and requirements
2. **Reference Brand Colors:** Always mention the 3 brand colors in prompts
3. **Iterate:** Start with basic design, then refine with follow-up prompts
4. **Test with Real Data:** Provide sample data structure to plugin
5. **Focus on One Section:** Design one section at a time, not entire page

**Example: Good Prompt**
```
Tôi muốn thiết kế "Peer Comparison" section cho Company Dashboard.

Data structure:
- DataFrame với columns: symbol, net_revenue, npatmi, roe, pe_ratio
- 5-10 companies (peers trong cùng sector)
- Current company highlight

Requirements:
- Horizontal bar chart comparing ROE across peers
- Highlight current company with brand blue (#295CA9)
- Other peers in gray
- Sort by ROE descending
- Show exact ROE value at end of each bar

Style:
- Dark theme background (#0A1E42)
- Professional, clean layout
- Inter font family
```

**Example: Bad Prompt**
```
Thiết kế comparison chart cho tôi.
```

---

**Status:** 🟢 READY - All specs completed, ready for implementation

**Next Step:** Choose a dashboard to implement and follow its spec document.
