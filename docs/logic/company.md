# Company Dashboard Logic Reference

Pure business logic for company fundamental analysis. No code.

---

## Overview

**Purpose:** Analyze Vietnamese company financials
**Key Metrics:** Revenue, Profit, ROE, ROA, Margins, D/E, Cash Flow
**Data Source:** `DATA/processed/fundamental/company/company_financial_metrics.parquet`

---

## Tab 1: Key Metrics Cards

### 4 Primary KPIs (Header)

| KPI | Column | Format | Delta Logic |
|-----|--------|--------|-------------|
| Net Revenue | `net_revenue` | Billions VND | QoQ % change |
| Net Profit | `npatmi` | Billions VND | QoQ % change |
| ROE | `roe` | % | Points change (pp) |
| D/E Ratio | `debt_to_equity` | x (inverse) | Change (lower=better) |

---

## Tab 2: Charts

### Income Statement Charts

| Chart | Column | Color | MA4 Line |
|-------|--------|-------|----------|
| Revenue | `net_revenue` | Secondary | `net_revenue_growth_yoy` |
| Gross Profit | `gross_profit` | Positive | `gross_profit_growth_yoy` |
| EBITDA | `ebitda` | Quaternary | `ebitda_growth_yoy` |
| NPATMI | `npatmi` | Tertiary | `npatmi_growth_yoy` |

### Profitability Margin Charts

| Chart | Column | MA4 Column |
|-------|--------|------------|
| Gross Margin | `gross_profit_margin` | `gross_profit_margin_ma4` |
| EBIT Margin | `ebit_margin` | `ebit_margin_ma4` |
| EBITDA Margin | `ebitda_margin` | `ebitda_margin_ma4` |
| Net Margin | `net_margin` | `net_margin_ma4` |

### Balance Sheet Structure

- Stacked bar: Liabilities + Equity = Total Assets
- Colors: Tertiary (Liabilities), Primary (Equity)

### Cash Flow Analysis

| Trace | Column | Type | Color |
|-------|--------|------|-------|
| Operating CF | `operating_cf` | Bar | Positive |
| Investment CF | `investment_cf` | Bar | Negative |
| Financing CF | `financing_cf` | Bar | Blue Light |
| FCF | `fcf` | Line | Secondary |
| FCFF | `fcff` | Dotted Line | Teal |
| FCFE | `fcfe` | Dashed Line | Tertiary |

---

## Tab 3: Financial Tables

### Sub-Tabs

| Tab | Contents |
|-----|----------|
| Income Statement | Revenue, COGS, Gross Profit, SG&A, EBIT, EBITDA, PBT, NPATMI |
| Balance Sheet | Assets, Liabilities, Equity breakdown |
| Cash Flow | Operating, Investing, Financing, FCF, FCFF, FCFE |

---

## Key Ratios

### Profitability

| Ratio | Formula | Good Range |
|-------|---------|------------|
| Gross Margin | Gross Profit / Revenue | Industry-dependent |
| Net Margin | NPATMI / Revenue | >10% |
| ROE | NPATMI / Avg Equity | >15% |
| ROA | NPATMI / Avg Assets | >5% |

### Leverage

| Ratio | Formula | Good Range |
|-------|---------|------------|
| D/E | Total Debt / Equity | <1.5x |
| Debt Ratio | Total Debt / Assets | <50% |

### Cash Flow

| Ratio | Formula | Good Range |
|-------|---------|------------|
| FCF | Operating CF - CapEx | Positive |
| FCF/Revenue | FCF / Revenue | >5% |

---

## Color Reference

| State | Hex | Usage |
|-------|-----|-------|
| Primary | #8B5CF6 | ROA, Equity |
| Secondary | #06B6D4 | Revenue, ROE |
| Tertiary | #F59E0B | NPATMI, Liabilities |
| Positive | #10B981 | Gross Profit, Operating CF |
| Negative | #EF4444 | Investment CF (outflow) |

---

## File Locations

| Component | Location |
|-----------|----------|
| Dashboard | `WEBAPP/pages/company/company_dashboard.py` |
| Service | `WEBAPP/services/company_service.py` |
| Calculator | `PROCESSORS/fundamental/calculators/company_calculator.py` |
| Data | `DATA/processed/fundamental/company/company_financial_metrics.parquet` |
