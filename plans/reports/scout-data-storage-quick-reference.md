# DATA Architecture - Quick Reference

## Directory Layout (470 MB Total)

```
DATA/
├── raw/ (241 MB)
│   ├── fundamental/csv/Q3_2025/ (175 MB)
│   │   └── {COMPANY|BANK|INSURANCE|SECURITY}_{BALANCE_SHEET|INCOME|CF_DIRECT|CF_INDIRECT|NOTE}.csv
│   ├── ohlcv/ (56 MB)
│   │   └── OHLCV_mktcap.parquet (457 tickers, daily)
│   ├── news/ (0.8 MB)
│   │   └── news_raw_*.parquet (4 files, Nov 2025)
│   └── Metric_code/ (0.7 MB)
│       └── BSC - Mô tả CSDL.xlsx
│
├── processed/ (229 MB) - All Parquet (Snappy compressed)
│   ├── fundamental/ (98 MB)
│   │   ├── company_full.parquet (86 MB)
│   │   ├── bank_full.parquet
│   │   ├── insurance_full.parquet
│   │   ├── security_full.parquet
│   │   ├── company/ → company_financial_metrics.parquet (17 MB, 37,145 rows)
│   │   ├── bank/ → bank_financial_metrics.parquet (447 KB, 1,033 rows)
│   │   ├── insurance/ → insurance_financial_metrics.parquet (90 KB)
│   │   ├── security/ → security_financial_metrics.parquet (440 KB)
│   │   └── macro/ → {interest_rates|deposit|exchange|bonds}.parquet
│   │
│   ├── technical/ (38 MB)
│   │   ├── basic_data.parquet (19 MB, 89,933 rows, 40 cols)
│   │   ├── alerts/{daily|historical}/ → {breakout|ma_crossover|patterns|volume_spike|combined}_*.parquet
│   │   ├── money_flow/ → individual_money_flow.parquet (6.6 MB), sector_money_flow_*.parquet
│   │   ├── rs_rating/ → stock_rs_rating_daily.parquet
│   │   ├── sector_breadth/ → sector_breadth_daily.parquet
│   │   ├── market_breadth/ → market_breadth_daily.parquet
│   │   ├── market_regime/ → market_regime_history.parquet
│   │   └── vnindex/ → vnindex_indicators.parquet
│   │
│   ├── valuation/ (45 MB)
│   │   ├── pe/historical/ → historical_pe.parquet (9.9 MB, 792K rows)
│   │   ├── pb/historical/ → historical_pb.parquet (11 MB)
│   │   ├── ps/historical/ → historical_ps.parquet
│   │   ├── ev_ebitda/historical/ → historical_ev_ebitda.parquet (12 MB)
│   │   └── vnindex/ → (VN-Index PE/PB)
│   │
│   ├── stock_valuation/ (32 MB) [DUPLICATE]
│   │   ├── individual_pe.parquet (9.8 MB)
│   │   ├── individual_pb.parquet (10 MB)
│   │   └── individual_ev_ebitda.parquet (12 MB)
│   │
│   ├── sector/ (7.2 MB)
│   │   ├── sector_fundamental_metrics.parquet (589 rows)
│   │   ├── sector_valuation_metrics.parquet (51K rows)
│   │   └── sector_combined_scores.parquet (380 rows)
│   │
│   ├── market_indices/ (1.1 MB)
│   │   ├── vnindex_valuation.parquet (5,784 rows)
│   │   └── sector_pe_summary.parquet (36K rows)
│   │
│   ├── macro_commodity/ (0.4 MB)
│   │   └── macro_commodity_unified.parquet (24,883 rows, 12 cols)
│   │
│   └── forecast/ (0.1 MB)
│       ├── bsc/
│       │   ├── bsc_individual.parquet (93 stocks, 32 cols)
│       │   ├── bsc_sector_valuation.parquet (15 sectors)
│       │   ├── bsc_combined.parquet (93 stocks + sector metrics)
│       │   └── README.md
│       └── VCI/
│           └── vci_coverage_universe.parquet (85 KB)
│
└── metadata/ (124 KB)
    ├── sector_industry_registry.json (94 KB)
    ├── master_symbols.json (8.2 KB)
    ├── liquid_tickers.json (4.3 KB)
    └── generate_liquid_tickers.py (6.4 KB)
```

---

## Data Coverage at a Glance

| Metric | Value | Range |
|--------|-------|-------|
| **Tickers** | 457 total | Company (2,246), Bank (57), Insurance (34), Security (154) |
| **Sectors** | 19 | Ngân hàng, Bất động sản, Xây dựng, etc. |
| **Time Period** | 7+ years | 2018 fundamentals, 2020 technical, 2015 valuation |
| **Total Rows** | 19.9M+ | Fundamentals (19.9M) + Technical (89K) + Valuation (792K) |
| **Update Frequency** | Mixed | Daily (market/TA), Quarterly (fundamentals) |
| **Compression** | 60-80% | Parquet snappy reduces vs CSV by 60-80% |

---

## Key Files by Use Case

### For Dashboard
```python
# Company Analysis
df = pd.read_parquet('DATA/processed/fundamental/company/company_financial_metrics.parquet')

# Bank Analysis
df = pd.read_parquet('DATA/processed/fundamental/bank/bank_financial_metrics.parquet')

# Technical Indicators
df = pd.read_parquet('DATA/processed/technical/basic_data.parquet')

# Valuation
df = pd.read_parquet('DATA/processed/valuation/pe/historical/historical_pe.parquet')

# Sector Overview
df = pd.read_parquet('DATA/processed/sector/sector_fundamental_metrics.parquet')

# BSC Forecast
df = pd.read_parquet('DATA/processed/forecast/bsc/bsc_individual.parquet')
```

### For Data Processing
```python
# Raw CSV input (quarterly)
df = pd.read_csv('DATA/raw/fundamental/csv/Q3_2025/COMPANY_BALANCE_SHEET.csv')

# Full parquet (long format bridge)
df = pd.read_parquet('DATA/processed/fundamental/company_full.parquet')

# Market data
df = pd.read_parquet('DATA/raw/ohlcv/OHLCV_mktcap.parquet')

# Metadata registries
import json
with open('DATA/metadata/sector_industry_registry.json') as f:
    registry = json.load(f)
```

---

## Column Reference by Category

### Company Metrics (61 columns)
```
Revenue:     net_revenue, gross_profit, cogs, sga, ebit, ebitda, npatmi
Assets:      total_assets, total_equity, total_liabilities, cash, inventory
Ratios:      roe, roa, current_ratio, debt_to_equity, asset_turnover
Margins:     gross_profit_margin, ebit_margin, ebitda_margin, net_margin
Per-Share:   eps, bvps
Trends:      net_revenue_ttm, npatmi_ttm, operating_cf_ttm
Cash Flow:   operating_cf, investment_cf, financing_cf, fcf, capex
```

### Bank Metrics (55 columns)
```
Income:      nii, toi, ppop, npatmi
Efficiency:  cir, nii_toi, noii_toi
Quality:     npl_ratio, debt_group2_ratio, llcr, provision_to_loan
Funding:     casa_ratio, ldr (Loan-to-Deposit)
Yield/Cost:  nim (Q & TTM), asset_yield, funding_cost, loan_yield
Growth:      nii_growth_yoy, toi_growth_yoy, ppop_growth_yoy
```

### Technical Indicators (40+ columns)
```
OHLCV:       open, high, low, close, volume
Market Cap:  market_cap, shares_outstanding, trading_value
MA:          sma_20, sma_50, sma_100, sma_200
EMA:         ema_20, ema_50, ...
```

### Valuation (varies)
```
PE:          pe_current (TTM), pe_forward (2025/2026), pe_percentile, pe_5y_avg, pe_sector_avg
PB:          Similar structure to PE
PS/EV:       Similar structure to PE
```

---

## Data Processing Pipeline

### Stage 1: Raw Input
```
DATA/raw/fundamental/csv/Q3_2025/*.csv (Wide format, metrics as columns)
                ↓
         PROCESSORS/fundamental/csv_to_full_parquet.py
```

### Stage 2: Full Parquet Bridge
```
DATA/processed/fundamental/{entity}_full.parquet (Long format, 19.9M rows)
                ↓
         PROCESSORS/fundamental/calculators/run_all_calculators.py
```

### Stage 3: Processed Metrics
```
DATA/processed/fundamental/{entity}/{entity}_financial_metrics.parquet (Wide + calculated)
                ↓
         Dashboard & Analysis
```

### Daily Updates
```
PROCESSORS/pipelines/run_all_daily_updates.py
    ↓ OHLCV → technical → macro → valuation → sector
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **Path not found** | Use canonical `DATA/processed/` NOT `calculated_results/` or `data_warehouse/` |
| **Column not found** | Different columns per entity (company ≠ bank). Check schema first |
| **Slow read** | Use `columns=` parameter to load only needed columns |
| **Large file** | `company_full.parquet` (86 MB) is rarely needed; use `company_financial_metrics.parquet` |
| **Missing current date** | Technical updated daily, fundamentals quarterly. Check `updated_at` timestamp |

---

## File Statistics Summary

| Directory | Files | Size | Primary Format | Update |
|-----------|-------|------|-----------------|--------|
| raw/ | 25+ | 241 MB | CSV + Parquet | Q + Daily |
| fundamental/ | 8 | 98 MB | Parquet | Q |
| technical/ | 25+ | 38 MB | Parquet | Daily |
| valuation/ | 5 | 45 MB | Parquet | Daily |
| sector/ | 3 | 7.2 MB | Parquet | Daily |
| forecast/ | 3 | 0.1 MB | Parquet | Quarterly |
| metadata/ | 4 | 124 KB | JSON | Q |
| **TOTAL** | **150+** | **470 MB** | Mixed | Mixed |

---

## Quick Commands

```bash
# Check file sizes
du -sh DATA/processed/*

# List all parquet files
find DATA -name "*.parquet" | sort

# Count rows in parquet (Python)
python3 -c "import pandas as pd; df = pd.read_parquet('path.parquet'); print(len(df))"

# View parquet schema (Python)
python3 -c "import pandas as pd; df = pd.read_parquet('path.parquet'); print(df.dtypes)"

# Daily update
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

