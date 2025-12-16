# Company Dashboard Specification

> **Master Design Guide**: [DESIGN_SYSTEM_SPEC.md](../../../docs/DESIGN_SYSTEM_SPEC.md)
> **Formula Reference**: [FORMULA_IMPLEMENTATION_SUMMARY.md](../../../docs/FORMULA_IMPLEMENTATION_SUMMARY.md)
>
> Follow các nguyên tắc từ master spec:
> - Chart Library: **Plotly ONLY**
> - Data Units: **Billions VND** (display) / VND (storage)
> - Design Theme: **Professional Financial** (Dark + Brand colors)
> - Brand Colors: #295CA9 (blue), #009B87 (teal), #FFC132 (gold)

---

## 1. Metric Cards (Header - 4 KPIs)
| # | Metric | Column Name | Unit | Format | Delta |
|---|--------|-------------|------|--------|-------|
| 1 | Net Revenue | `net_revenue` | B VND | `{:,.1f}` | QoQ % |
| 2 | Net Profit (NPATMI) | `npatmi` | B VND | `{:,.1f}` | QoQ % |
| 3 | ROE | `roe` | % | `{:.2f}%` | delta pts |
| 4 | Debt/Equity | `debt_to_equity` | x | `{:.2f}x` | delta (inverse) |

---

## 2. Tab 1: Charts

### 2.1 Income Statement Chart (Line + Bar)
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 1 | Income Statement Trends | Line + Bar | `net_revenue`, `gross_profit`, `ebit`, `ebitda`, `npatmi` | Stacked/overlay revenue breakdown |

### 2.2 Profitability Margins (Line)
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 2 | Profitability Margins | Multi-line | `gross_profit_margin`, `ebit_margin`, `ebitda_margin`, `net_margin` | Margins trend over time |

### 2.3 ROE / ROA Chart (Dual Line)
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 3 | ROE / ROA | Dual-line | `roe`, `roa` | Profitability efficiency |

### 2.4 Balance Sheet Chart (Stacked Bar)
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 4 | Balance Sheet | Stacked Bar | `total_assets`, `total_liabilities`, `total_equity` | Asset structure |

### 2.5 Cash Flow Chart (Grouped Bar)
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 5 | Cash Flow | Grouped Bar | `operating_cf`, `investment_cf`, `financing_cf`, `fcf` | Cash flow waterfall |

---

## 3. Tab 2: Tables

### Table 1: KQKD / Income Statement
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| Doanh thu thuan | `net_revenue` | `{:,.1f} B` |
| Gia von | `cogs` | `{:,.1f} B` |
| Loi nhuan gop | `gross_profit` | `{:,.1f} B` |
| Chi phi BH & QLDN | `sga` | `{:,.1f} B` |
| EBIT | `ebit` | `{:,.1f} B` |
| EBITDA | `ebitda` | `{:,.1f} B` |
| Loi nhuan truoc thue | `ebt` | `{:,.1f} B` |
| LNST (NPATMI) | `npatmi` | `{:,.1f} B` |

### Table 2: Key Metrics
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| Bien LN gop | `gross_profit_margin` | `{:.2f}%` |
| Bien EBIT | `ebit_margin` | `{:.2f}%` |
| Bien EBITDA | `ebitda_margin` | `{:.2f}%` |
| Bien LN rong | `net_margin` | `{:.2f}%` |
| ROE | `roe` | `{:.2f}%` |
| ROA | `roa` | `{:.2f}%` |
| D/E | `debt_to_equity` | `{:.2f}x` |
| Current Ratio | `current_ratio` | `{:.2f}x` |

---

## 4. Available Data Columns (56 columns)

### Income Statement
- `net_revenue`, `cogs`, `gross_profit`, `sga`, `ebit`, `ebitda`, `ebt`, `npatmi`
- `net_finance_income`, `depreciation`
- `net_revenue_ttm`, `npatmi_ttm`

### Balance Sheet
- `total_assets`, `total_liabilities`, `total_equity`
- `cash`, `inventory`, `account_receivable`, `tangible_fixed_asset`
- `st_debt`, `lt_debt`, `net_debt`
- `current_assets`, `current_liabilities`, `working_capital`
- `common_shares`

### Cash Flow
- `operating_cf`, `investment_cf`, `financing_cf`, `capex`
- `fcf`, `fcfe`, `delta_working_capital`, `delta_net_borrowing`
- `operating_cf_ttm`

### Ratios & Margins
- `gross_profit_margin`, `ebit_margin`, `ebitda_margin`, `net_margin`
- `roe`, `roa`, `eps`, `bvps`
- `current_ratio`, `quick_ratio`, `cash_ratio`
- `debt_to_equity`, `debt_to_assets`
- `asset_turnover`, `inventory_turnover`, `receivables_turnover`

### Metadata
- `symbol`, `report_date`, `year`, `quarter`, `freq_code`

---

## 5. Notes
- Data source: `DATA/processed/fundamental/company/company_financial_metrics.parquet`
- Service: `WEBAPP/services/company_service.py`
- All monetary values stored in Billions VND

---

**Related Docs:**
- [Master Design Spec](../../../docs/DESIGN_SYSTEM_SPEC.md)
- [Theme Config](../../core/theme.py)
- [Chart Components](../../components/charts/)


---


# Bank Dashboard Specification

> **Master Design Guide**: [DESIGN_SYSTEM_SPEC.md](../../../docs/DESIGN_SYSTEM_SPEC.md)
> **Formula Reference**: [formula_migration_plan.md](../../../formula_migration_plan.md) - Bank Sheet section
>
> Follow các nguyên tắc từ master spec:
> - Chart Library: **Plotly ONLY**
> - Data Units: **Billions VND** (display) / VND (storage)
> - Design Theme: **Professional Financial** (Dark + Brand colors)
> - Brand Colors: #295CA9 (blue), #009B87 (teal), #FFC132 (gold)

---

## 1. Metric Cards (Header - 4 KPIs)
| # | Metric | Column Name | Unit | Format | Delta |
|---|--------|-------------|------|--------|-------|
| 1 | NII (Thu nhap lai thuan) | `nii` | B VND | `{:,.1f}` | QoQ % |
| 2 | NIM | `nim_q` | % | `{:.2f}%` | delta pts |
| 3 | ROAE (TTM) | `roea_ttm` | % | `{:.2f}%` | delta pts |
| 4 | NPL Ratio | `npl_ratio` | % | `{:.2f}%` | delta (inverse) |

---

## 2. Tab 1: Charts

### 2.1 Income & Asset Quality (Row 1)
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 1 | Income Breakdown | Stacked Bar | `nii`, `noii` | NII vs Non-II income |
| 2 | NPL & Coverage | Dual-axis | `npl_ratio`, `llcr` | NPL% (bar) vs LLCR% (line) |

### 2.2 Profitability Metrics (Row 2)
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 3 | NIM & Yield/Cost | Multi-line | `nim_q`, `asset_yield_q`, `funding_cost_q` | NIM components |
| 4 | ROAE & ROAA | Dual-line | `roea_ttm`, `roaa_ttm` | Return metrics (TTM) |

### 2.3 Efficiency Metrics (Row 3)
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 5 | CIR | Bar | `cir` | Cost-to-Income with 40% target line |
| 6 | CASA Ratio | Area | `casa_ratio` | CASA trend |

### 2.4 Growth Charts (Row 4) - NEW
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 7 | Income Growth (YoY) | Multi-line | `nii_growth_yoy`, `toi_growth_yoy`, `ppop_growth_yoy`, `npatmi_growth_yoy` | YoY income growth metrics |
| 8 | Balance Sheet Growth (YTD) | Grouped Bar | `credit_growth_ytd`, `asset_growth_ytd`, `loan_growth_ytd`, `deposit_growth_ytd` | YTD BS growth |

### 2.5 Asset Quality Charts (Row 5) - NEW
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 9 | Asset Quality Trend | Multi-line | `npl_ratio`, `debt_group2_ratio`, `provision_to_loan` | Quality metrics over time |
| 10 | Credit Cost & Coverage | Dual-axis | `credit_cost`, `llcr` | Credit cost (bar) vs LLCR (line) |

---

## 3. Tab 2: Tables (5 Sub-tabs)

### 3.1 Size Table (Quy mô)
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| Total Assets | `total_assets` | `{:,.1f} B` |
| Total Credit | `total_credit` | `{:,.1f} B` |
| Total Loan | `total_loan` | `{:,.1f} B` |
| Total Corp Bond | `total_corp_bond` | `{:,.1f} B` |
| Total Customer Deposit | `total_customer_deposit` | `{:,.1f} B` |

### 3.2 Income Statement Table
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| NII (Thu nhập lãi thuần) | `nii` | `{:,.1f} B` |
| TOI (Tổng thu nhập HĐ) | `toi` | `{:,.1f} B` |
| NOII (Thu nhập phi lãi) | `noii` | `{:,.1f} B` |
| OPEX (Chi phí hoạt động) | `opex` | `{:,.1f} B` |
| PPOP (LN trước dự phòng) | `ppop` | `{:,.1f} B` |
| Provision (Chi phí DP) | `provision_expense` | `{:,.1f} B` |
| PBT (LN trước thuế) | `pbt` | `{:,.1f} B` |
| NPATMI (LNST CĐCTM) | `npatmi` | `{:,.1f} B` |

### 3.3 Growth Table (Tăng trưởng)
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| NII Growth (YoY) | `nii_growth_yoy` | `{:.2f}%` |
| TOI Growth (YoY) | `toi_growth_yoy` | `{:.2f}%` |
| PPOP Growth (YoY) | `ppop_growth_yoy` | `{:.2f}%` |
| PBT Growth (YoY) | `pbt_growth_yoy` | `{:.2f}%` |
| NPATMI Growth (YoY) | `npatmi_growth_yoy` | `{:.2f}%` |
| Credit Growth (YTD) | `credit_growth_ytd` | `{:.2f}%` |
| Asset Growth (YTD) | `asset_growth_ytd` | `{:.2f}%` |
| Loan Growth (YTD) | `loan_growth_ytd` | `{:.2f}%` |
| Deposit Growth (YTD) | `deposit_growth_ytd` | `{:.2f}%` |

### 3.4 Asset Quality Table
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| Group 2 Ratio | `debt_group2_ratio` | `{:.2f}%` |
| NPL Ratio | `npl_ratio` | `{:.2f}%` |
| NPL Amount | `npl_amount` | `{:,.1f} B` |
| Provision/Loan | `provision_to_loan` | `{:.2f}%` |
| LLCR | `llcr` | `{:.2f}%` |
| Accrued/Loan | `accrued_to_loan` | `{:.2f}%` |
| Credit Cost | `credit_cost` | `{:.2f}%` |

### 3.5 Efficiency & Earning Quality Table
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| NIM (Q) | `nim_q` | `{:.2f}%` |
| Asset Yield (Q) | `asset_yield_q` | `{:.2f}%` |
| Funding Cost (Q) | `funding_cost_q` | `{:.2f}%` |
| Loan Yield (Q) | `loan_yield_q` | `{:.2f}%` |
| CIR | `cir` | `{:.2f}%` |
| CASA Ratio | `casa_ratio` | `{:.2f}%` |
| NII/TOI | `nii_toi` | `{:.2f}%` |
| NOII/TOI | `noii_toi` | `{:.2f}%` |
| LDR Pure | `ldr_pure` | `{:.2f}%` |
| LDR Regulated | `ldr_regulated_estimated` | `{:.2f}%` |
| ROAE (TTM) | `roea_ttm` | `{:.2f}%` |
| ROAA (TTM) | `roaa_ttm` | `{:.2f}%` |
| BVPS | `bvps` | `{:,.0f}` |
| EPS (TTM) | `eps_ttm` | `{:,.0f}` |

---

## 4. Available Data Columns (56 columns)

### Size Metrics (NEW)
- `total_assets`, `total_credit`, `total_loan`, `total_corp_bond`, `total_customer_deposit`

### Income Statement
- `nii`, `noii`, `toi`, `opex`, `ppop` (NEW), `provision_expense`, `pbt`, `npatmi`
- `interest_income`, `interest_expense`
- `nii_toi`, `noii_toi`

### Growth Metrics (NEW)
- YoY: `nii_growth_yoy`, `toi_growth_yoy`, `ppop_growth_yoy`, `pbt_growth_yoy`, `npatmi_growth_yoy`
- YTD: `credit_growth_ytd`, `asset_growth_ytd`, `loan_growth_ytd`, `deposit_growth_ytd`

### Profitability (with averages)
- `roea_ttm`, `roaa_ttm`
- `nim_q`, `asset_yield_q`, `funding_cost_q`, `loan_yield_q`
- `equity_avg_2q`, `avg_iea_2q`, `avg_ibl_2q`

### Asset Quality
- `npl_ratio`, `npl_amount`, `debt_group2_ratio`, `group2_to_total_ratio`
- `llcr`, `provision_to_loan` (NEW), `accrued_to_loan` (NEW), `credit_cost` (NEW)

### Efficiency & Liquidity
- `cir`, `casa_ratio`
- `ldr_pure`, `ldr_regulated_estimated`
- `iea`, `ibl`

### Valuation
- `bvps`, `eps_ttm`

### Metadata
- `symbol`, `report_date`, `year`, `quarter`, `freq_code`

---

## 5. Notes
- Data source: `DATA/processed/fundamental/bank/bank_financial_metrics.parquet`
- Service: `WEBAPP/services/bank_service.py`
- Calculator: `PROCESSORS/fundamental/calculators/bank_calculator.py`
- Bank-specific metrics use 2Q averages for yield/cost calculations
- Growth YoY = Year-over-Year (same period last year, 4 quarters ago)
- Growth YTD = Year-to-Date (vs previous year-end, 4 quarters ago)

---

**Related Docs:**
- [Master Design Spec](../../../docs/DESIGN_SYSTEM_SPEC.md)
- [Formula Migration Plan](../../../formula_migration_plan.md) - Bank Sheet section
- [Theme Config](../../core/theme.py)
- [Chart Components](../../components/charts/)


---


# Security (Brokerage) Dashboard Specification

> **Master Design Guide**: [DESIGN_SYSTEM_SPEC.md](../../../docs/DESIGN_SYSTEM_SPEC.md)
> **Formula Reference**: [FORMULA_IMPLEMENTATION_SUMMARY.md](../../../docs/FORMULA_IMPLEMENTATION_SUMMARY.md)
>
> Follow các nguyên tắc từ master spec:
> - Chart Library: **Plotly ONLY**
> - Data Units: **Billions VND** (display) / VND (storage)
> - Design Theme: **Professional Financial** (Dark + Brand colors)
> - Brand Colors: #295CA9 (blue), #009B87 (teal), #FFC132 (gold)

---

## 1. Metric Cards (Header - 4 KPIs)
| # | Metric | Column Name | Unit | Format | Delta |
|---|--------|-------------|------|--------|-------|
| 1 | Total Revenue | `total_revenue` | B VND | `{:,.1f}` | QoQ % |
| 2 | Net Profit | `net_profit` | B VND | `{:,.1f}` | QoQ % |
| 3 | ROAE (TTM) | `roae_ttm` | % | `{:.2f}%` | delta pts |
| 4 | Leverage | `leverage` | x | `{:.2f}x` | delta |

---

## 2. Tab 1: Charts

### 2.1 Revenue Composition
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 1 | Revenue Mix | Stacked Bar | `investment_revenue`, `income_loans`, `income_fvtpl`, `income_htm`, `income_afs` | Revenue by source |

### 2.2 Business Line Margins
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 2 | Business Margins | Multi-bar | `gross_profit_margin`, `profit_margin`, `brokerage_ratio`, `ib_ratio` | Profitability by segment |

### 2.3 Portfolio Composition
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 3 | Portfolio Mix | Pie Chart | `fvtpl`, `htm`, `afs`, `margin_loans` | Investment breakdown |

### 2.4 Profitability Metrics
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 4 | ROAE / ROAA | Dual-line | `roae_ttm`, `roaa_ttm` | Return metrics |
| 5 | Efficiency | Multi-line | `cir`, `ga_ratio`, `opex_ratio` | Cost efficiency |

### 2.5 Capital Structure
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 6 | Leverage Trend | Line | `leverage`, `loans_to_equity`, `capital_ratio` | Debt structure |

---

## 3. Tab 2: Tables

### Table 1: Income Statement
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| Tong doanh thu | `total_revenue` | `{:,.1f} B` |
| Loi nhuan gop | `gross_profit` | `{:,.1f} B` |
| Loi nhuan rong | `net_profit` | `{:,.1f} B` |
| Thu nhap dau tu | `investment_revenue` | `{:,.1f} B` |
| Thu nhap FVTPL | `income_fvtpl` | `{:,.1f} B` |
| Thu nhap cho vay | `income_loans` | `{:,.1f} B` |

### Table 2: Key Metrics
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| Bien LN gop | `gross_profit_margin` | `{:.2f}%` |
| Bien LN rong | `profit_margin` | `{:.2f}%` |
| ROAE (TTM) | `roae_ttm` | `{:.2f}%` |
| ROAA (TTM) | `roaa_ttm` | `{:.2f}%` |
| CIR | `cir` | `{:.2f}%` |
| Leverage | `leverage` | `{:.2f}x` |
| Loans/Equity | `loans_to_equity` | `{:.2f}x` |
| Capital Ratio | `capital_ratio` | `{:.2f}%` |

---

## 4. Available Data Columns (45 columns)

### Income Statement
- `total_revenue`, `gross_profit`, `net_profit`, `net_profit_ttm`
- `investment_revenue`, `income_fvtpl`, `income_htm`, `income_afs`, `income_loans`

### Portfolio
- `fvtpl`, `htm`, `afs`, `margin_loans`, `total_investment`

### Balance Sheet
- `total_assets`, `equity`, `liabilities`
- `st_debt`, `lt_debt`, `total_debt`
- `cash`

### Ratios
- `gross_profit_margin`, `profit_margin`
- `roae_ttm`, `roaa_ttm`
- `cir`, `ga_ratio`, `opex_ratio`
- `brokerage_ratio`, `ib_ratio`, `investment_ratio`, `lending_ratio`
- `leverage`, `loans_to_equity`, `loans_to_assets`, `inv_to_assets`
- `capital_ratio`, `liquidity_ratio`
- `assets_avg_2q`, `equity_avg_2q`

### Metadata
- `symbol`, `report_date`, `year`, `quarter`, `freq_code`

---

## 5. Notes
- Data source: `DATA/processed/fundamental/security/security_financial_metrics.parquet`
- Service: `WEBAPP/services/security_service.py`

---

**Related Docs:**
- [Master Design Spec](../../../docs/DESIGN_SYSTEM_SPEC.md)
- [Theme Config](../../core/theme.py)
- [Chart Components](../../components/charts/)


---


# Sector Analysis Dashboard Specification

> **Master Design Guide**: [DESIGN_SYSTEM_SPEC.md](../../../docs/DESIGN_SYSTEM_SPEC.md)
>
> Follow các nguyên tắc từ master spec:
> - Chart Library: **Plotly ONLY**
> - Design Theme: **Professional Financial** (Dark + Brand colors)
> - Brand Colors: #295CA9 (blue), #009B87 (teal), #FFC132 (gold)

---

## 1. Metric Cards (Header - 4 KPIs)
| # | Metric | Description | Source |
|---|--------|-------------|--------|
| 1 | Top Sector by PE | Sector voi PE thap nhat | Valuation data |
| 2 | Market PE (VNINDEX) | Current market PE | Valuation data |
| 3 | Sector Count | So sectors dang track | Registry |
| 4 | Ticker Count | Tong so ma | Registry |

---

## 2. Tab 1: Charts

### 2.1 Sector PE/PB Comparison
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 1 | Sector PE | Horizontal Bar | `pe_ttm` by sector | All sectors PE comparison |
| 2 | Sector PB | Horizontal Bar | `pb` by sector | All sectors PB comparison |

### 2.2 Sector Heatmap
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 3 | Valuation Heatmap | Heatmap | `pe_ttm`, `pb` by sector | Color-coded valuation |

### 2.3 Historical Comparison
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 4 | Sector PE History | Multi-line | Historical PE by top 5 sectors | Trend comparison |

### 2.4 Sector Composition
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 5 | Market Cap Treemap | Treemap | Market cap by sector | Size visualization |

---

## 3. Tab 2: Tables

### Table 1: Sector Valuation Overview
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| Sector | `scope` | String |
| PE (TTM) | `pe_ttm` | `{:.2f}x` |
| PB | `pb` | `{:.2f}x` |
| PE Fwd 2025 | `pe_fwd_2025` | `{:.2f}x` |

### Table 2: Sector Composition
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| Sector | `sector` | String |
| Ticker Count | `count` | `{:d}` |
| Top Tickers | `tickers` | String (comma-separated) |

---

## 4. Data Sources

### Valuation Data
- `DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet`
  - Columns: `date`, `scope`, `pe_ttm`, `pb`, `pe_fwd_2025`, `pe_fwd_2026`

### Sector Registry
- `config/registries/sector_lookup.py`
  - 19 sectors, 457 tickers
  - Methods: `get_sector_tickers()`, `get_all_sectors()`

### Technical Data (for market breadth)
- `DATA/processed/technical/market_breadth/`
- `DATA/processed/technical/sector_breadth/`

---

## 5. Notes
- Service: `WEBAPP/services/sector_service.py`
- Su dung `SectorRegistry` tu `config/registries`
- 19 sectors: Bank, Security, Insurance, Real Estate, Retail, etc.

---

**Related Docs:**
- [Master Design Spec](../../../docs/DESIGN_SYSTEM_SPEC.md)
- [Theme Config](../../core/theme.py)
- [Chart Components](../../components/charts/)


---


# Valuation Dashboard Specification

> **Master Design Guide**: [DESIGN_SYSTEM_SPEC.md](../../../docs/DESIGN_SYSTEM_SPEC.md)
>
> Follow các nguyên tắc từ master spec:
> - Chart Library: **Plotly ONLY**
> - Design Theme: **Professional Financial** (Dark + Brand colors)
> - Brand Colors: #295CA9 (blue), #009B87 (teal), #FFC132 (gold)

---

## 1. Metric Cards (Header - 4 KPIs)
| # | Metric | Column Name | Unit | Format | Description |
|---|--------|-------------|------|--------|-------------|
| 1 | PE (TTM) | `pe_ttm` | x | `{:.1f}x` | Trailing PE |
| 2 | PB | `pb` | x | `{:.1f}x` | Price-to-Book |
| 3 | PE Fwd 2025 | `pe_fwd_2025` | x | `{:.1f}x` | Forward PE |
| 4 | PE Fwd 2026 | `pe_fwd_2026` | x | `{:.1f}x` | Forward PE |

---

## 2. Tab 1: Charts

### 2.1 PE Historical Chart
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 1 | PE Trend | Line | `pe_ttm`, `date` | PE over time |
| 2 | PE vs Forward | Multi-line | `pe_ttm`, `pe_fwd_2025`, `pe_fwd_2026` | Trailing vs Forward |

### 2.2 PB Historical Chart
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 3 | PB Trend | Line | `pb`, `date` | PB over time |

### 2.3 PE/PB Comparison
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 4 | Market vs Sector | Grouped Bar | `pe_ttm`, `pb` (filtered by scope) | VNINDEX vs Sectors |

### 2.4 Valuation Bands
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 5 | PE Bands | Area | Historical PE percentiles | +/- 1 SD bands |

---

## 3. Tab 2: Tables

### Table 1: Current Valuation
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| Date | `date` | `YYYY-MM-DD` |
| Scope | `scope` | String |
| PE (TTM) | `pe_ttm` | `{:.2f}x` |
| PB | `pb` | `{:.2f}x` |
| PE Fwd 2025 | `pe_fwd_2025` | `{:.2f}x` |
| PE Fwd 2026 | `pe_fwd_2026` | `{:.2f}x` |

### Table 2: Sector Comparison
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| Sector | `scope` | String |
| PE (TTM) | `pe_ttm` | `{:.2f}x` |
| PB | `pb` | `{:.2f}x` |

---

## 4. Available Data Columns (6 columns)

### Valuation Metrics
- `pe_ttm` - Trailing 12-month PE
- `pb` - Price-to-Book
- `pe_fwd_2025` - Forward PE 2025
- `pe_fwd_2026` - Forward PE 2026

### Metadata
- `date` - Valuation date
- `scope` - VNINDEX or sector name

---

## 5. Notes
- Data source: `DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet`
- Service: `WEBAPP/services/valuation_service.py`
- Additional PE/PB data in `DATA/processed/valuation/pe/` and `pb/`

---

**Related Docs:**
- [Master Design Spec](../../../docs/DESIGN_SYSTEM_SPEC.md)
- [Theme Config](../../core/theme.py)
- [Chart Components](../../components/charts/)


---


# Technical Analysis Dashboard Specification

> **Master Design Guide**: [DESIGN_SYSTEM_SPEC.md](../../../docs/DESIGN_SYSTEM_SPEC.md)
>
> Follow các nguyên tắc từ master spec:
> - Chart Library: **Plotly ONLY**
> - Design Theme: **Professional Financial** (Dark + Brand colors)
> - Brand Colors: #295CA9 (blue), #009B87 (teal), #FFC132 (gold)

---

## 1. Metric Cards (Header - 4 KPIs)
| # | Metric | Column Name | Unit | Format | Description |
|---|--------|-------------|------|--------|-------------|
| 1 | Price | `close` | VND | `{:,.0f}` | Latest close price |
| 2 | RSI (14) | `rsi_14` | - | `{:.1f}` | Momentum indicator |
| 3 | Price vs SMA50 | `price_vs_sma50` | % | `{:+.1f}%` | Trend strength |
| 4 | ADX (14) | `adx_14` | - | `{:.1f}` | Trend strength |

---

## 2. Tab 1: Charts

### 2.1 Price Chart with Overlays
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 1 | OHLC + MA | Candlestick | `open`, `high`, `low`, `close`, `sma_20`, `sma_50`, `sma_200` | Price with moving averages |

### 2.2 Bollinger Bands
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 2 | Bollinger | Line | `close`, `bb_upper`, `bb_middle`, `bb_lower`, `bb_width` | Volatility bands |

### 2.3 Momentum Indicators
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 3 | RSI | Line | `rsi_14` | Overbought/Oversold (70/30) |
| 4 | Stochastic | Multi-line | `stoch_k`, `stoch_d` | Momentum oscillator |
| 5 | CCI | Line | `cci_20` | Commodity Channel Index |

### 2.4 MACD
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 6 | MACD | Line + Histogram | `macd`, `macd_signal`, `macd_hist` | Trend momentum |

### 2.5 Volume Analysis
| # | Chart Name | Chart Type | Columns Used | Description |
|---|------------|------------|--------------|-------------|
| 7 | Volume | Bar | `volume`, `trading_value` | Volume + Value |
| 8 | OBV | Line | `obv` | On-Balance Volume |
| 9 | CMF | Line | `cmf_20` | Chaikin Money Flow |

---

## 3. Tab 2: Tables

### Table 1: Price & Moving Averages
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| Close | `close` | `{:,.0f}` |
| SMA 20 | `sma_20` | `{:,.0f}` |
| SMA 50 | `sma_50` | `{:,.0f}` |
| SMA 100 | `sma_100` | `{:,.0f}` |
| SMA 200 | `sma_200` | `{:,.0f}` |
| EMA 20 | `ema_20` | `{:,.0f}` |
| EMA 50 | `ema_50` | `{:,.0f}` |

### Table 2: Technical Indicators
| Column Display Name | Column Code | Format |
|---------------------|-------------|--------|
| RSI (14) | `rsi_14` | `{:.1f}` |
| ADX (14) | `adx_14` | `{:.1f}` |
| ATR (14) | `atr_14` | `{:.2f}` |
| MACD | `macd` | `{:.2f}` |
| MACD Signal | `macd_signal` | `{:.2f}` |
| CCI (20) | `cci_20` | `{:.1f}` |
| MFI (14) | `mfi_14` | `{:.1f}` |

---

## 4. Available Data Columns (40 columns)

### Price Data
- `open`, `high`, `low`, `close`, `volume`
- `trading_value`, `trading_value_diff`
- `market_cap`, `shares_outstanding`

### Moving Averages
- `sma_20`, `sma_50`, `sma_100`, `sma_200`
- `ema_20`, `ema_50`
- `price_vs_sma20`, `price_vs_sma50`, `price_vs_sma200`

### Bollinger Bands
- `bb_upper`, `bb_middle`, `bb_lower`, `bb_width`

### Momentum Indicators
- `rsi_14`, `stoch_k`, `stoch_d`
- `macd`, `macd_signal`, `macd_hist`
- `cci_20`, `mfi_14`, `adx_14`

### Volume Indicators
- `obv`, `cmf_20`, `ad_line`

### Other
- `atr_14`, `expected_trading_value`

### Metadata
- `symbol`, `date`, `resolution`, `updated_at`

---

## 5. Notes
- Data source: `DATA/processed/technical/basic_data.parquet`
- Service: `WEBAPP/services/technical_service.py`

---

**Related Docs:**
- [Master Design Spec](../../../docs/DESIGN_SYSTEM_SPEC.md)
- [Theme Config](../../core/theme.py)
- [Chart Components](../../components/charts/)
