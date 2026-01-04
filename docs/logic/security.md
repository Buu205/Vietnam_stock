# Security Dashboard Logic Reference

Pure business logic for securities/brokerage analysis. No code.

---

## Overview

**Purpose:** Analyze Vietnamese brokerage companies
**Key Metrics:** Revenue Mix, ROAE, ROAA, Leverage, CIR, Portfolio
**Data Source:** `DATA/processed/fundamental/security/security_financial_metrics.parquet`

---

## Tab 1: Key Metrics Cards

### 4 Primary KPIs (Header)

| KPI | Column | Format | Delta Logic |
|-----|--------|--------|-------------|
| Total Revenue | `total_revenue` | Billions VND | QoQ % change |
| Net Profit | `net_profit` | Billions VND | QoQ % change |
| ROAE (TTM) | `roae_ttm` | % | Points change (pp) |
| Leverage | `leverage` | x | Ratio change |

---

## Tab 2: Charts

### Revenue Mix (Stacked Bar)

| Component | Column | Color |
|-----------|--------|-------|
| FVTPL Income | `income_fvtpl` | Primary |
| HTM Income | `income_htm` | Secondary |
| AFS Income | `income_afs` | Warning |
| Margin Lending | `income_loans` | Danger |
| Brokerage Fee | `brokerage_fee` | Success |

### ROAE & ROAA (Dual Line)

| Metric | Column | Color |
|--------|--------|-------|
| ROAE | `roae_ttm` | Primary |
| ROAA | `roaa_ttm` | Secondary |

### Portfolio Composition (Pie Chart - Latest)

| Segment | Column | Color |
|---------|--------|-------|
| FVTPL | `fvtpl` | Primary |
| HTM | `htm` | Secondary |
| AFS | `afs` | Warning |
| Margin Loans | `margin_loans` | Success |

### Profit Margins (Line)

| Metric | Column |
|--------|--------|
| Gross Margin | `gross_profit_margin` |
| Net Margin | `profit_margin` |

### CIR (Bar with Target)

| Element | Value |
|---------|-------|
| Target Line | 50% (warning color, dashed) |

### Leverage (Area)

- Fill to zero with warning color

---

## Tab 3: Tables

### Income Statement

| Metric | Column | Format |
|--------|--------|--------|
| Total Revenue | `total_revenue` | Billions |
| Brokerage Fee | `brokerage_fee` | Billions |
| Investment Revenue | `investment_revenue` | Billions |
| Gross Profit | `gross_profit` | Billions |
| Operating Expense | `opex` | Billions |
| Net Profit | `net_profit` | Billions |

### Balance Sheet Summary

| Metric | Column | Format |
|--------|--------|--------|
| Total Assets | `total_assets` | Billions |
| FVTPL Portfolio | `fvtpl` | Billions |
| HTM Portfolio | `htm` | Billions |
| AFS Portfolio | `afs` | Billions |
| Margin Loans | `margin_loans` | Billions |
| Total Equity | `total_equity` | Billions |

### Key Financial Ratios

| Metric | Column | Format |
|--------|--------|--------|
| Gross Margin | `gross_profit_margin` | % |
| Net Margin | `profit_margin` | % |
| ROAE (TTM) | `roae_ttm` | % |
| ROAA (TTM) | `roaa_ttm` | % |
| Leverage | `leverage` | x |
| CIR | `cir` | % |

---

## Key Brokerage Ratios

### Profitability

| Ratio | Formula | Good Range |
|-------|---------|------------|
| ROAE | Net Profit / Avg Equity | >15% |
| ROAA | Net Profit / Avg Assets | >2% |
| Net Margin | Net Profit / Revenue | >20% |

### Efficiency

| Ratio | Formula | Good Range |
|-------|---------|------------|
| CIR | Operating Expense / Revenue | <50% |
| Leverage | Total Assets / Equity | <5x |

---

## File Locations

| Component | Location |
|-----------|----------|
| Dashboard | `WEBAPP/pages/security/security_dashboard.py` |
| Service | `WEBAPP/services/security_service.py` |
| Calculator | `PROCESSORS/fundamental/calculators/security_calculator.py` |
| Data | `DATA/processed/fundamental/security/security_financial_metrics.parquet` |
