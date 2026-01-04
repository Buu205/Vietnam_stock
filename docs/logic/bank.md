# Bank Dashboard Logic Reference

Pure business logic for bank financial analysis. No code.

---

## Overview

**Purpose:** Analyze Vietnamese banking sector financials
**Key Metrics:** NII, NIM, ROAE, NPL, CASA, LDR, CIR, CAR
**Data Source:** `DATA/processed/fundamental/bank/bank_financial_metrics.parquet`

---

## Tab 1: Key Metrics Cards

### 4 Primary KPIs (Header)

| KPI | Column | Format | Delta Logic |
|-----|--------|--------|-------------|
| Net Interest Income | `nii` | Billions VND | QoQ % change |
| NIM (Quarterly) | `nim_q` | % | Points change (pp) |
| ROAE (TTM) | `roea_ttm` | % | Points change (pp) |
| NPL Ratio | `npl_ratio` | % (inverse) | Points change (lower=better) |

---

## Tab 2: Charts - Metric Types

### Line Chart Metrics (Trend Focus)
- NIM, ROE, ROA, CIR
- Credit Growth, Deposit Growth, Loan Growth
- NII Growth, NPATMI Growth

### Bar Chart Metrics (Point-in-Time)
- NPL, LLCR, Provision/Loan, LDR
- CASA, Asset Yield, Funding Cost
- Group 2, Credit Cost

### Reference Lines on Charts

| Metric | Threshold | Meaning |
|--------|-----------|---------|
| CIR | 40% | Target efficiency |
| NPL | 3% | SBV warning level |
| LLCR | 100% | Minimum coverage |
| LDR | 85% | SBV regulatory limit |

---

## Tab 3: Financial Tables

### Table Groups

| Sub-Tab | Metrics |
|---------|---------|
| Size | Total Assets, Credit, Loan, Corp Bond, Customer Deposit |
| Income | NII, TOI, NOII, OPEX, PPOP, Provision, PBT, NPATMI |
| Growth | YoY growth rates (NII, TOI, PPOP, PBT, NPATMI, Credit, Asset, Loan, Deposit) |
| Quality | Group 2, NPL, NPL Amount, Provision/Loan, LLCR, Accrued/Loan, Credit Cost |
| Efficiency | NIM, Asset Yield, Funding Cost, Loan Yield, CIR, CASA, NII/TOI, NOII/TOI, LDR, ROAE, ROAA |

---

## Key Banking Ratios

### Profitability

| Ratio | Formula | Good Range |
|-------|---------|------------|
| NIM (Q) | (Interest Income - Interest Expense) / Avg Earning Assets × 4 | 3-5% |
| ROAE (TTM) | NPATMI TTM / Avg Equity | >15% |
| ROAA (TTM) | NPATMI TTM / Avg Assets | >1% |

### Asset Quality

| Ratio | Formula | Good Range |
|-------|---------|------------|
| NPL Ratio | NPL / Total Loan | <3% (SBV warning) |
| LLCR | Loan Loss Reserve / NPL | >100% (minimum) |
| Group 2 | Sub-standard Debt / Total Loan | <5% |

### Efficiency

| Ratio | Formula | Good Range |
|-------|---------|------------|
| CIR | OPEX / TOI | <40% |
| CASA | CASA Deposit / Total Deposit | >20% |
| LDR | Total Loan / Total Deposit | <85% (SBV) |

---

## Color Reference

| State | Hex | Usage |
|-------|-----|-------|
| Primary | #8B5CF6 | Default chart color |
| Positive | #10B981 | Growth metrics, ROE, ROA |
| Negative | #EF4444 | NPL, cost metrics, risks |
| Warning | #F59E0B | Near threshold values |

---

## File Locations

| Component | Location |
|-----------|----------|
| Dashboard | `WEBAPP/pages/bank/bank_dashboard.py` |
| Service | `WEBAPP/services/bank_service.py` |
| Calculator | `PROCESSORS/fundamental/calculators/bank_calculator.py` |
| Data | `DATA/processed/fundamental/bank/bank_financial_metrics.parquet` |
