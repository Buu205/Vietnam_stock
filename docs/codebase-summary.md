# Codebase Summary

**Project:** Vietnam Stock Dashboard
**Total Python Files:** 196
**Last Updated:** 2025-12-21

---

## 1. Directory Structure

```
Vietnam_dashboard/
├── WEBAPP/              # Streamlit frontend (76 files)
├── PROCESSORS/          # Data processing (102 files)
├── DATA/                # Data storage (~250 MB)
├── config/              # Configuration (2.2 MB)
├── MCP_SERVER/          # MCP API Server (18 files)
├── scripts/             # Utility scripts
├── tests/               # Test files
└── docs/                # Documentation
```

---

## 2. WEBAPP Module (Streamlit Frontend)

**Location:** `/WEBAPP`
**Files:** 76 Python files
**Entry Point:** `main_app.py`

### Structure

```
WEBAPP/
├── main_app.py              # Entry point (st.navigation)
├── pages/                   # Dashboard pages
│   ├── company/             # Company analysis
│   ├── bank/                # Bank analysis
│   ├── security/            # Security analysis
│   ├── sector/              # Sector overview
│   ├── valuation/           # Valuation metrics
│   ├── technical/           # Technical analysis
│   └── forecast/            # BSC Forecast
├── services/                # Data loading services
│   ├── company_service.py
│   ├── bank_service.py
│   ├── sector_service.py
│   ├── valuation_service.py
│   ├── technical_service.py
│   └── forecast_service.py
├── core/                    # Core utilities
│   ├── config.py
│   ├── theme.py
│   ├── styles.py
│   ├── data_paths.py
│   └── models/data_models.py
└── components/              # Reusable UI components
    ├── charts/
    ├── tables/
    └── navigation/
```

### Key Classes

| Class | File | Purpose |
|-------|------|---------|
| CompanyService | `services/company_service.py` | Load company financial data |
| BankService | `services/bank_service.py` | Load bank metrics |
| SectorService | `services/sector_service.py` | Sector aggregation |
| TechnicalService | `services/technical_service.py` | OHLCV & indicators |
| ValuationService | `services/valuation_service.py` | PE/PB/EV metrics |

---

## 3. PROCESSORS Module (Data Processing)

**Location:** `/PROCESSORS`
**Files:** 102 Python files

### Structure

```
PROCESSORS/
├── api/                     # API clients (11 files)
│   ├── clients/
│   │   ├── wichart_client.py
│   │   ├── simplize_client.py
│   │   └── vnstock_client.py
│   ├── core/
│   │   ├── base_client.py
│   │   └── retry_handler.py
│   └── unified_fetcher.py
│
├── core/                    # Shared utilities (26 files)
│   ├── shared/
│   │   ├── unified_mapper.py
│   │   ├── symbol_loader.py
│   │   └── data_validator.py
│   ├── formatters/
│   └── validators/
│
├── fundamental/             # Financial calculators (12 files)
│   ├── calculators/
│   │   └── run_all_calculators.py
│   └── formulas/
│       ├── _base_formulas.py
│       ├── company_formulas.py
│       ├── bank_formulas.py
│       └── registry.py
│
├── technical/               # Technical indicators (16 files)
│   ├── indicators/
│   │   ├── technical_processor.py
│   │   ├── market_regime.py
│   │   ├── money_flow.py
│   │   └── alert_detector.py
│   └── ohlcv/
│       └── ohlcv_daily_updater.py
│
├── valuation/               # Valuation calculators (12 files)
│   └── calculators/
│       ├── vnindex_valuation_calculator.py
│       ├── historical_pe_calculator.py
│       ├── historical_pb_calculator.py
│       └── historical_ev_ebitda_calculator.py
│
├── sector/                  # Sector analysis (14 files)
│   ├── sector_processor.py
│   ├── calculators/
│   │   ├── fa_aggregator.py
│   │   └── ta_aggregator.py
│   └── scoring/
│       ├── fa_scorer.py
│       ├── ta_scorer.py
│       └── signal_generator.py
│
├── forecast/                # BSC forecast (3 files)
│   └── bsc_forecast_processor.py
│
└── pipelines/               # Daily orchestration (7 files)
    ├── run_all_daily_updates.py
    ├── daily_ohlcv_update.py
    ├── daily_ta_complete.py
    ├── daily_valuation.py
    └── daily_sector_analysis.py
```

### Key Classes

| Class | File | Purpose |
|-------|------|---------|
| UnifiedDataFetcher | `api/unified_fetcher.py` | Combine all API clients |
| UnifiedTickerMapper | `core/shared/unified_mapper.py` | Ticker info integration |
| TechnicalProcessor | `technical/indicators/technical_processor.py` | TA-Lib indicators |
| SectorProcessor | `sector/sector_processor.py` | Sector analysis orchestrator |
| VNIndexValuationCalculator | `valuation/calculators/vnindex_valuation_calculator.py` | Market-cap weighted valuation |

---

## 4. DATA Module (Data Storage)

**Location:** `/DATA`
**Size:** ~250 MB

### Structure

```
DATA/
├── raw/                     # Input data (READ from here)
│   ├── ohlcv/               # OHLCV_mktcap.parquet
│   ├── fundamental/csv/     # BSC CSV files (Q3/2025)
│   ├── commodity/
│   └── macro/
│
├── processed/               # Output data (WRITE to here)
│   ├── fundamental/         # Entity financial metrics
│   │   ├── company/
│   │   ├── bank/
│   │   ├── insurance/
│   │   └── security/
│   ├── technical/           # TA indicators, alerts
│   ├── valuation/           # PE/PB/PS/EV historical
│   ├── sector/              # Sector scores
│   ├── forecast/bsc/        # BSC forecasts
│   └── macro_commodity/
│
└── metadata/                # Registries (JSON)
    ├── sector_industry_registry.json
    ├── master_symbols.json
    └── liquid_tickers.json
```

### Key Files

| File | Location | Records | Purpose |
|------|----------|---------|---------|
| OHLCV_mktcap.parquet | raw/ohlcv/ | 457 tickers | Daily OHLCV + market cap |
| company_financial_metrics.parquet | processed/fundamental/company/ | 37,145 | Company metrics |
| bank_financial_metrics.parquet | processed/fundamental/bank/ | 1,033 | Bank metrics |
| basic_data.parquet | processed/technical/ | 89,821 | TA indicators |
| sector_combined_scores.parquet | processed/sector/ | 19 sectors | FA+TA scores |
| bsc_individual.parquet | processed/forecast/bsc/ | 93 stocks | BSC forecasts |

---

## 5. config Module (Configuration)

**Location:** `/config`
**Size:** 2.2 MB

### Structure

```
config/
├── registries/              # Registry classes
│   ├── __init__.py
│   ├── metric_lookup.py     # MetricRegistry
│   └── sector_lookup.py     # SectorRegistry
│
├── schema_registry.py       # SchemaRegistry singleton
│
├── schema_registry/         # Schema definitions (JSON)
│   ├── core/
│   ├── domain/
│   └── display/
│
├── metadata/                # Lookup data (JSON)
│   ├── metric_registry.json # 2,099 metrics (770 KB)
│   └── formula_registry.json
│
└── business_logic/          # Analysis rules
    ├── analysis/
    └── decisions/
```

### Key Classes

| Class | File | Purpose |
|-------|------|---------|
| MetricRegistry | `registries/metric_lookup.py` | Metric code lookup |
| SectorRegistry | `registries/sector_lookup.py` | Ticker-sector mapping |
| SchemaRegistry | `schema_registry.py` | Data formatting |

---

## 6. MCP_SERVER Module

**Location:** `/MCP_SERVER`
**Files:** 18 Python files
**Tools:** 30 MCP tools

### Structure

```
MCP_SERVER/
├── bsc_mcp/
│   ├── server.py            # FastMCP server
│   ├── config.py            # Configuration
│   └── tools/               # Tool implementations
│       ├── ticker_tools.py
│       ├── fundamental_tools.py
│       ├── technical_tools.py
│       ├── valuation_tools.py
│       └── forecast_tools.py
└── README.md
```

### Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| Ticker | 5 | List, search, info, peers |
| Fundamental | 5 | Financial metrics, comparison |
| Technical | 8 | Indicators, alerts, patterns |
| Valuation | 6 | PE/PB stats, sector comparison |
| Forecast | 4 | BSC forecasts, upside |
| Macro | 2 | Economic data, commodities |

---

## 7. Module Dependencies

```
WEBAPP (Frontend)
    ↓ imports
services/ → PROCESSORS/core/ + config/registries
    ↓ reads
DATA/processed/

PROCESSORS (Backend)
    ↓ imports
api/ → external APIs (VNStock, WiChart, Simplize)
core/ → config/registries
    ↓ writes
DATA/processed/

config/ (Shared)
    ↑ imported by
WEBAPP, PROCESSORS, MCP_SERVER
```

---

## 8. Daily Pipeline Order

```
1. OHLCV Update
   └── OHLCVDailyUpdater → DATA/raw/ohlcv/

2. Technical Analysis
   └── TechnicalProcessor → DATA/processed/technical/

3. Macro & Commodity
   └── MacroCommodityFetcher → DATA/processed/macro_commodity/

4. Valuation Metrics
   └── HistoricalPE/PB/PS/EV → DATA/processed/valuation/

5. Sector Analysis
   └── SectorProcessor → DATA/processed/sector/
```

**Command:**
```bash
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

---

## Related Documents

- [Project Overview](project-overview-pdr.md)
- [System Architecture](system-architecture.md)
- [Code Standards](code-standards.md)
