# Data Conversion Pipeline

## Overview

This document describes the data conversion process from raw CSV files to processed parquet files.

## Data Flow

```
DATA/raw/fundamental/csv/Q3_2025/*.csv (wide format)
    │
    ▼ csv_to_full_parquet.py
    │
DATA/processed/fundamental/*_full.parquet (long format with METRIC_CODE)
    │
    ▼ run_all_calculators.py
    │
DATA/processed/fundamental/{entity}/{entity}_financial_metrics.parquet (wide format with calculated metrics)
```

## Input Files

Location: `DATA/raw/fundamental/csv/Q3_2025/`

| Entity | Files |
|--------|-------|
| COMPANY | COMPANY_BALANCE_SHEET.csv, COMPANY_INCOME.csv, COMPANY_CF_DIRECT.csv, COMPANY_CF_INDIRECT.csv, COMPANY_NOTE.csv |
| BANK | BANK_BALANCE_SHEET.csv, BANK_INCOME.csv, BANK_CF_DIRECT.csv, BANK_CF_INDIRECT.csv, BANK_NOTE.csv |
| INSURANCE | INSURANCE_BALANCE_SHEET.csv, INSURANCE_INCOME.csv, INSURANCE_CF_DIRECT.csv, INSURANCE_CF_INDIRECT.csv, INSURANCE_NOTE.csv |
| SECURITY | SECURITY_BALANCE_SHEET.csv, SECURITY_INCOME.csv, SECURITY_CF_DIRECT.csv, SECURITY_CF_INDIRECT.csv, SECURITY_NOTE.csv |

## Step 1: Convert CSV to Full Parquet (Long Format)

### Command
```bash
python3 PROCESSORS/fundamental/csv_to_full_parquet.py
```

### What it does
- Reads wide-format CSV files (metrics as columns)
- Converts to long-format parquet (METRIC_CODE column)
- Combines all statement types per entity

### Output Files
| File | Rows | Tickers | Metrics |
|------|------|---------|---------|
| company_full.parquet | 16,040,568 | 2,246 | 517 |
| bank_full.parquet | 611,078 | 57 | 579 |
| insurance_full.parquet | 253,302 | 34 | 646 |
| security_full.parquet | 2,995,709 | 154 | 1,203 |
| **TOTAL** | **19,900,657** | - | - |

### Data Range
- Start: 2018-03-31
- End: 2025-09-30 (Q3/2025)

## Step 2: Run Financial Calculators

### Command
```bash
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py
```

### What it does
- Loads *_full.parquet (long format)
- Pivots to wide format
- Calculates derived metrics (ROE, ROA, margins, ratios, etc.)
- Saves calculated metrics parquet

### Output Files
| File | Rows | Tickers | Columns |
|------|------|---------|---------|
| company/company_financial_metrics.parquet | 37,145 | 1,633 | 59 |
| bank/bank_financial_metrics.parquet | 1,033 | 46 | 56 |
| insurance/insurance_financial_metrics.parquet | 418 | 18 | 28 |
| security/security_financial_metrics.parquet | 2,811 | 146 | 28 |

## Metric Prefixes

| Entity | Prefix Examples |
|--------|-----------------|
| COMPANY | CBS (Balance Sheet), CIS (Income), CCFD/CCFI (Cash Flow), CNOT (Notes) |
| BANK | BBS, BIS, BCFD/BCFI, BNOT |
| INSURANCE | IBS, IIS, ICFD/ICFI, INOT |
| SECURITY | SBS, SIS, SCFD/SCFI, SNOT |

## Key Metrics by Entity

### COMPANY
- CIS_10: Net Revenue
- CIS_20: Gross Profit
- CIS_61: NPATMI
- CBS_270: Total Assets
- CBS_400: Total Equity
- CCFI_20: Operating Cash Flow

### BANK
- BIS_3: Net Interest Income (NII)
- BIS_14A: Total Operating Income (TOI)
- BIS_22A: NPATMI
- BBS_100: Total Assets
- BBS_180: Total Loans
- BBS_400: Total Equity

### INSURANCE
- IIS_03: Net Premium
- IIS_62: NPATMI
- IBS_100: Total Assets
- IBS_300: Total Equity

### SECURITY
- SIS_20: Total Revenue
- SIS_60: NPAT
- SBS_100: Total Assets
- SBS_300: Total Equity

## Calculated Metrics (Output)

### Company Metrics
- Margins: gross_profit_margin, ebit_margin, ebitda_margin, net_margin
- Profitability: roe, roa
- Liquidity: current_ratio, quick_ratio, cash_ratio
- Solvency: debt_to_equity, debt_to_assets
- Activity: asset_turnover, inventory_turnover, receivables_turnover
- Per Share: eps, bvps
- TTM: net_revenue_ttm, npatmi_ttm, operating_cf_ttm

### Bank Metrics
- Yield/Cost: nim_q, asset_yield_q, funding_cost_q, loan_yield_q
- Efficiency: cir, nii_toi, noii_toi
- Asset Quality: npl_ratio, debt_group2_ratio, llcr, provision_to_loan, credit_cost
- Funding: casa_ratio, ldr_pure
- Profitability: roea_ttm, roaa_ttm
- Growth: nii_growth_yoy, toi_growth_yoy, ppop_growth_yoy, credit_growth_ytd

## Data Quality Check

### Comparison with Legacy (full_database.parquet)
- Q1/2025 data: **99.98% exact match** (116,889/116,908 rows)
- VNM Q2/2025: **100% match** on all key metrics
- Only 19 minor mismatches in CNOT (notes) fields

### Data Coverage
| Entity | Legacy Tickers | New Tickers | Improvement |
|--------|----------------|-------------|-------------|
| COMPANY | 438 | 2,246 | +413% |
| BANK | 27 | 57 | +111% |
| INSURANCE | 6 | 34 | +467% |
| SECURITY | 35 | 154 | +340% |

## Registry Configuration

Metric mappings are stored in:
- `config/metadata/metric_registry.json` - Raw metric definitions (2,099 metrics)
- `config/metadata/formula_registry.json` - Calculated metric formulas

## Last Updated

- Date: 2025-12-16
- Data through: Q3/2025 (2025-09-30)
- Total rows: 19,900,657
