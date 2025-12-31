# Codebase Summary

**Project:** Vietnam Stock Dashboard
**Total Python Files:** 223 (110 PROCESSORS + 113 WEBAPP)
**Last Updated:** 2025-12-28

---

## 1. Directory Structure

```
Vietnam_dashboard/
├── WEBAPP/              # Streamlit frontend (113 files)
├── PROCESSORS/          # Data processing (110 files)
├── DATA/                # Data storage (~500 MB)
├── config/              # Configuration (2.2 MB, 41 files)
├── MCP_SERVER/          # MCP API Server (30 tools)
├── scripts/             # Utility scripts
├── tests/               # Test files
├── docs/                # Documentation (5 files)
└── plans/reports/       # Scout reports & audit findings
```

---

## 2. WEBAPP Module (Streamlit Frontend)

**Location:** `/WEBAPP`
**Files:** 113 Python files
**Entry Point:** `main_app.py`
**Theme:** Crypto Terminal Glassmorphism (dark mode, OLED-optimized)

### Structure

```
WEBAPP/
├── main_app.py              # Entry point (st.navigation, 8 pages)
├── pages/                   # Dashboard pages (8 modules)
│   ├── company/             # Company analysis
│   │   ├── company_dashboard.py
│   │   ├── components/
│   │   └── services/
│   ├── bank/                # Bank analysis
│   │   ├── bank_dashboard.py
│   │   ├── components/
│   │   └── services/
│   ├── security/            # Security analysis
│   │   ├── security_dashboard.py
│   │   └── services/
│   ├── sector/              # Sector overview
│   │   ├── sector_dashboard.py
│   │   └── services/
│   ├── valuation/           # Valuation metrics
│   │   ├── valuation_dashboard.py
│   │   └── services/
│   ├── technical/           # Technical analysis (3 tabs)
│   │   ├── technical_dashboard.py
│   │   ├── components/      # market_overview, sector_rotation, stock_scanner
│   │   ├── services/        # ta_dashboard_service.py
│   │   └── README.md        # Technical module documentation (658 lines)
│   ├── fx_commodities/      # FX & Commodities
│   │   ├── fx_dashboard.py
│   │   └── services/
│   └── forecast/            # BSC Forecast
│       ├── forecast_dashboard.py
│       └── services/
│
├── services/                # Data loading services (8 modules)
│   ├── company_service.py
│   ├── bank_service.py
│   ├── security_service.py
│   ├── sector_service.py
│   ├── valuation_service.py
│   ├── technical_service.py
│   ├── forecast_service.py
│   └── fx_service.py
│
├── core/                    # Core utilities (17 files)
│   ├── models/              # Pydantic models
│   │   ├── data_models.py   # OHLCVBase, FundamentalBase, BankMetrics, etc.
│   │   └── market_state.py  # MarketState model
│   ├── session_state.py     # CRITICAL: init_page_state() for all pages
│   ├── theme.py             # Crypto Terminal Glassmorphism theme
│   ├── styles.py            # CSS styles (glassmorphism, animations)
│   ├── config.py            # App configuration
│   ├── constants.py         # Constants (entity types, sectors)
│   ├── display_config.py    # Display settings
│   ├── formatters.py        # Data formatters
│   ├── data_loading.py      # Data loading utilities
│   ├── data_paths.py        # Data path management
│   ├── chart_config.py      # Chart configuration
│   ├── chart_schema.py      # Chart schema definitions
│   ├── display_settings.py  # Display settings
│   ├── valuation_config.py  # Valuation configuration
│   ├── symbol_loader.py     # Symbol loading
│   └── utils.py             # Utilities
│
└── components/              # Reusable UI components
    ├── charts/              # Plotly chart builders
    │   └── plotly_builders.py  # PlotlyChartBuilder class
    ├── tables/              # Data tables
    ├── metric_cards/        # Metric cards
    └── filters/             # Filter components
```

### Key Classes

| Class | File | Purpose |
|-------|------|---------|
| CompanyService | `services/company_service.py` | Load company financial data |
| BankService | `services/bank_service.py` | Load bank metrics |
| SecurityService | `services/security_service.py` | Load security metrics |
| SectorService | `services/sector_service.py` | Sector aggregation |
| TechnicalService | `services/technical_service.py` | OHLCV & indicators |
| ValuationService | `services/valuation_service.py` | PE/PB/EV metrics |
| ForecastService | `services/forecast_service.py` | BSC forecasts |
| TADashboardService | `pages/technical/services/ta_dashboard_service.py` | Technical dashboard data |
| PlotlyChartBuilder | `components/charts/plotly_builders.py` | Plotly charts (candlestick, OHLC, heatmap, RRG) |
| MarketState | `core/models/market_state.py` | Market state model |
| init_page_state() | `core/session_state.py` | CRITICAL: Initialize session state for all pages |

---

## 3. PROCESSORS Module (Data Processing)

**Location:** `/PROCESSORS`
**Files:** 110 Python files

### Structure

```
PROCESSORS/
├── api/                     # API clients (5 modules, unified fetcher)
│   ├── clients/
│   │   ├── vnstock_client.py
│   │   ├── simplize_client.py
│   │   ├── fireant_client.py
│   │   ├── wichart_client.py
│   │   └── vietcap_client.py
│   ├── core/
│   │   ├── base_client.py   # Abstract base class
│   │   └── retry_handler.py # Retry with exponential backoff
│   └── unified_fetcher.py   # Combine all API clients
│
├── core/                    # Shared utilities (10 files)
│   ├── shared/
│   │   ├── unified_mapper.py    # UnifiedTickerMapper (ticker info, peers, validation)
│   │   ├── symbol_loader.py     # Symbol loading
│   │   └── data_validator.py    # Data validation
│   ├── config/
│   │   └── paths.py             # Path configuration (v4.0.0 canonical)
│   ├── formatters/              # Data formatters
│   ├── validators/              # Data validators
│   └── ai_assistants/           # AI assistants for analysis
│
├── fundamental/             # Financial calculators (4 entity types)
│   ├── calculators/
│   │   ├── company_calculator.py    # 56-59 columns output
│   │   ├── bank_calculator.py       # 56-59 columns output
│   │   ├── insurance_calculator.py  # 56-59 columns output
│   │   ├── security_calculator.py   # 56-59 columns output
│   │   └── run_all_calculators.py   # Run all calculators
│   ├── transformers/
│   │   └── financial/formulas.py    # 40+ pure calculation functions
│   │       ├── _base_formulas.py    # Base formulas
│   │       ├── company_formulas.py  # Company-specific formulas
│   │       ├── bank_formulas.py     # Bank-specific formulas
│   │       └── registry.py          # Formula registry
│   └── readers/                     # CSV readers
│
├── technical/               # Technical indicators (16 files)
│   ├── indicators/
│   │   ├── technical_processor.py   # TA-Lib indicators (15+ indicators)
│   │   ├── alert_detector.py        # Signal detection (MA, volume, breakout, patterns)
│   │   ├── market_regime.py         # Market regime detection (5 regimes)
│   │   ├── sector_breadth.py        # Sector breadth analysis
│   │   ├── money_flow.py            # Money flow analysis (CMF, MFI, OBV, AD, VPT)
│   │   ├── rs_rating.py             # IBD-style RS Rating (1-99)
│   │   ├── vnindex_analyzer.py      # VN-Index analysis
│   │   └── sector_money_flow.py     # Sector money flow (1D, 1W, 1M)
│   └── ohlcv/
│       └── ohlcv_daily_updater.py   # OHLCV data management
│
├── valuation/               # Valuation calculators (12 files)
│   ├── calculators/
│   │   ├── vnindex_pe_calculator_optimized.py     # VN-Index PE (market-cap weighted)
│   │   ├── historical_pe_calculator.py            # Historical PE
│   │   ├── historical_pb_calculator.py            # Historical PB
│   │   ├── historical_ps_calculator.py            # Historical PS
│   │   ├── historical_ev_ebitda_calculator.py     # Historical EV/EBITDA
│   │   ├── sector_pe_calculator.py                # Sector PE
│   │   ├── sector_pb_calculator.py                # Sector PB
│   │   └── vnindex_valuation_calculator.py        # VN-Index valuation
│   └── readers/                     # Valuation data readers
│
├── sector/                  # Sector analysis (14 files)
│   ├── sector_processor.py          # Sector analysis orchestrator
│   ├── calculators/
│   │   ├── fa_aggregator.py         # FA aggregation
│   │   └── ta_aggregator.py         # TA aggregation
│   └── scoring/
│       ├── fa_scorer.py             # FA scoring
│       ├── ta_scorer.py             # TA scoring
│       └── signal_generator.py      # Signal generation (BUY/SELL/HOLD)
│
├── forecast/                # BSC forecast (3 files)
│   ├── bsc_forecast_processor.py    # BSC forecast processor
│   └── readers/                     # BSC Excel reader
│
├── pipelines/               # Daily orchestration (6 steps)
│   ├── daily/
│   │   ├── daily_ta_complete.py     # Complete TA pipeline (9 steps)
│   │   ├── daily_ohlcv_update.py    # OHLCV update
│   │   ├── daily_macro_commodity_update.py  # Macro & commodity update
│   │   └── daily_valuation.py       # Valuation update
│   ├── run_all_daily_updates.py     # Run all daily updates (6 steps)
│   └── daily_sector_complete_update.py  # Complete sector update
│
└── news/                    # News pipeline
    └── news_pipeline.py            # News data processing
```

### Key Classes

| Class | File | Purpose |
|-------|------|---------|
| UnifiedDataFetcher | `api/unified_fetcher.py` | Combine all API clients (VNStock, WiChart, Simplize, Fireant, Vietcap) |
| UnifiedTickerMapper | `core/shared/unified_mapper.py` | Ticker info integration (get_ticker, get_peers, validate) |
| TechnicalProcessor | `technical/indicators/technical_processor.py` | TA-Lib indicators (15+ indicators: SMA, RSI, MACD, BB, ATR, ADX, Stochastic, CCI) |
| AlertDetector | `technical/indicators/alert_detector.py` | Signal detection (MA crossover, volume spike, breakout, candlestick patterns with 3-metric scoring) |
| MarketRegimeDetector | `technical/indicators/market_regime.py` | Market regime detection (5 regimes: BUBBLE, EUPHORIA, NEUTRAL, FEAR, BOTTOM) |
| SectorBreadthAnalyzer | `technical/indicators/sector_breadth.py` | Sector breadth analysis (4 MA periods: 20/50/100/200) |
| MoneyFlowAnalyzer | `technical/indicators/money_flow.py` | Money flow analysis (CMF, MFI, OBV, AD, VPT) |
| RSRatingCalculator | `technical/indicators/rs_rating.py` | IBD-style RS Rating (1-99 percentile, 4-period weighting) |
| SectorProcessor | `sector/sector_processor.py` | Sector analysis orchestrator (FA+TA scoring) |
| VNIndexValuationCalculator | `valuation/calculators/vnindex_pe_calculator_optimized.py` | Market-cap weighted PE calculation |

---

## 4. DATA Module (Data Storage)

**Location:** `/DATA`
**Size:** ~500 MB

### Structure

```
DATA/
├── raw/                     # Input data (READ from here)
│   ├── ohlcv/
│   │   └── OHLCV_mktcap.parquet            # 457 tickers, daily OHLCV + market cap
│   ├── fundamental/csv/                    # BSC CSV files (Q3/2025, 20 files)
│   │   ├── COMPANY_BALANCE_SHEET.csv
│   │   ├── COMPANY_INCOME.csv
│   │   ├── BANK_BALANCE_SHEET.csv
│   │   ├── BANK_INCOME.csv
│   │   └── ... (16 more files)
│   ├── commodity/                          # Commodity data
│   └── macro/                              # Macro data
│
├── processed/               # Output data (WRITE to here)
│   ├── fundamental/                         # Entity financial metrics
│   │   ├── company/
│   │   │   └── company_financial_metrics.parquet        # 37,145 records, 1,633 tickers
│   │   ├── bank/
│   │   │   └── bank_financial_metrics.parquet            # 1,033 records, 46 banks
│   │   ├── insurance/
│   │   │   └── insurance_financial_metrics.parquet      # 418 records, 18 insurance
│   │   └── security/
│   │       └── security_financial_metrics.parquet       # 2,811 records, 146 securities
│   │
│   ├── technical/                           # TA indicators, alerts, money flow
│   │   ├── basic_data.parquet                            # 89,805 records, 458 symbols, 200-session indicators
│   │   ├── alerts/
│   │   │   ├── daily/
│   │   │   │   ├── breakout_latest.parquet               # Breakout alerts
│   │   │   │   ├── combined_latest.parquet               # Combined alerts
│   │   │   │   ├── ma_crossover_latest.parquet           # MA crossover alerts
│   │   │   │   ├── patterns_latest.parquet               # Candlestick patterns (3-metric scoring)
│   │   │   │   └── volume_spike_latest.parquet           # Volume spike alerts
│   │   │   └── historical/                               # Historical alerts
│   │   ├── market_breadth/
│   │   │   └── market_breadth_daily.parquet              # Market breadth metrics
│   │   ├── sector_breadth/
│   │   │   └── sector_breadth_daily.parquet              # Sector breadth metrics
│   │   ├── money_flow/
│   │   │   ├── individual_money_flow.parquet             # Individual money flow
│   │   │   ├── sector_money_flow_1d.parquet              # Sector money flow (1D)
│   │   │   ├── sector_money_flow_1w.parquet              # Sector money flow (1W)
│   │   │   └── sector_money_flow_1m.parquet              # Sector money flow (1M)
│   │   ├── market_regime/
│   │   │   └── market_regime_history.parquet             # Market regime history
│   │   ├── rs_rating/
│   │   │   └── stock_rs_rating_daily.parquet              # RS Rating (1-99)
│   │   └── vnindex/
│   │       └── vnindex_indicators.parquet                 # VN-Index indicators
│   │
│   ├── valuation/                           # PE/PB/PS/EV historical
│   │   ├── pe/
│   │   │   └── historical/historical_pe.parquet           # 789,611 records
│   │   ├── pb/
│   │   │   └── historical/historical_pb.parquet           # 789,611 records
│   │   ├── ps/
│   │   │   └── historical/historical_ps.parquet           # 789,611 records
│   │   ├── ev_ebitda/
│   │   │   └── historical/historical_ev_ebitda.parquet    # 789,611 records
│   │   ├── vnindex/
│   │   │   └── vnindex_valuation_refined.parquet         # VN-Index PE/PB
│   │   └── sector_pe/
│   │       └── sector_pe_pb_data.parquet                  # Sector PE/PB
│   │
│   ├── sector/                              # Sector scores
│   │   ├── sector_fundamental_metrics.parquet             # Sector fundamental metrics
│   │   ├── sector_valuation_metrics.parquet               # Sector valuation metrics
│   │   └── sector_combined_scores.parquet                 # Sector FA+TA scores (19 sectors)
│   │
│   ├── forecast/                            # BSC forecasts
│   │   └── bsc/
│   │       ├── bsc_individual.parquet                    # Individual forecasts (93 stocks)
│   │       ├── bsc_combined.parquet                       # Combined forecasts
│   │       ├── bsc_sector_valuation.parquet               # Sector valuation
│   │       └── vci_coverage_universe.json                 # VCI coverage metadata
│   │
│   └── macro_commodity/                     # Macro & commodity data
│       └── macro_commodity_unified.parquet               # Unified macro & commodity data
│
└── metadata/                # Registries (JSON)
    ├── sector_industry_registry.json          # 457 tickers × 19 sectors × 4 entity types
    ├── master_symbols.json                    # Master symbols list
    └── liquid_tickers.json                    # Liquid tickers list
```

### Key Files

| File | Location | Records | Purpose |
|------|----------|---------|---------|
| OHLCV_mktcap.parquet | raw/ohlcv/ | 457 tickers | Daily OHLCV + market cap (source for all TA calculations) |
| company_financial_metrics.parquet | processed/fundamental/company/ | 37,145 | Company metrics (ROE, ROA, EPS, margins, growth) |
| bank_financial_metrics.parquet | processed/fundamental/bank/ | 1,033 | Bank metrics (NIM, CIR, NPL, LDR, CAR, CASA) |
| insurance_financial_metrics.parquet | processed/fundamental/insurance/ | 418 | Insurance metrics (combined ratio, claims ratio) |
| security_financial_metrics.parquet | processed/fundamental/security/ | 2,811 | Security metrics (brokerage revenue, commission) |
| basic_data.parquet | processed/technical/ | 89,805 | TA indicators (15+ indicators, 200 sessions) |
| patterns_latest.parquet | processed/technical/alerts/daily/ | Daily | Candlestick patterns (3-metric scoring: win_rate, context_score, composite_score) |
| market_breadth_daily.parquet | processed/technical/market_breadth/ | Daily | Market breadth metrics (% above MA20/50/100/200) |
| sector_breadth_daily.parquet | processed/technical/sector_breadth/ | Daily | Sector breadth metrics (19 sectors) |
| market_regime_history.parquet | processed/technical/market_regime/ | Daily | Market regime history (5 regimes) |
| stock_rs_rating_daily.parquet | processed/technical/rs_rating/ | Daily | RS Rating (1-99, IBD-style) |
| historical_pe.parquet | processed/valuation/pe/historical/ | 789,611 | PE TTM historical (2018-2025) |
| historical_pb.parquet | processed/valuation/pb/historical/ | 789,611 | PB TTM historical |
| vnindex_valuation_refined.parquet | processed/valuation/vnindex/ | 60 days | VN-Index PE/PB (market-cap weighted) |
| sector_combined_scores.parquet | processed/sector/ | 19 sectors | Sector FA+TA scores with signals |
| bsc_individual.parquet | processed/forecast/bsc/ | 93 stocks | BSC forecasts (2025-2026 targets) |
| macro_commodity_unified.parquet | processed/macro_commodity/ | Daily | Macro & commodity data (gold, oil, steel, rubber, USD/VND, bond yields) |

---

## 5. config Module (Configuration)

**Location:** `/config`
**Size:** 2.2 MB
**Files:** 41 (5 Python + 36 JSON)

### Structure

```
config/
├── data_mapping/            # Data Mapping Registry (NEW v1.0.0) (5 modules + YAML)
│   ├── __init__.py          # Public exports (17 items)
│   ├── entities.py          # Dataclasses (DataSource, PipelineOutput, DashboardConfig, ServiceBinding)
│   ├── registry.py          # DataMappingRegistry singleton (YAML loader, lookup methods)
│   ├── resolver.py          # PathResolver (validation), DependencyResolver (impact analysis)
│   ├── validator.py         # SchemaValidator, HealthChecker, ValidationResult
│   └── configs/             # YAML configuration files
│       ├── data_sources.yaml    # 18 data sources with paths, schemas, metadata
│       ├── services.yaml        # 8 services mapped to data sources
│       ├── pipelines.yaml       # 14 pipelines with outputs & dependencies
│       └── dashboards.yaml      # 8 dashboards mapped to sources & services
│
├── registries/              # Registry classes (Python)
│   ├── __init__.py
│   ├── metric_lookup.py     # MetricRegistry class (2,099 metrics)
│   ├── sector_lookup.py     # SectorRegistry class (457 tickers)
│   └── builders/            # Registry builders
│       ├── build_metric_registry.py  # BSC Excel → metric_registry.json
│       └── build_sector_registry.py  # Metadata → sector_industry_registry.json
│
├── schema_registry.py       # SchemaRegistry singleton (master class)
│
├── schema_registry/         # Schema definitions (JSON, 17 files)
│   ├── core/                # Core schemas
│   │   ├── types.json       # Data types
│   │   ├── entities.json    # Entity types
│   │   └── mappings.json    # Field mappings
│   ├── domain/              # Domain-specific schemas
│   │   ├── fundamental/     # Fundamental schemas
│   │   ├── technical/       # Technical schemas
│   │   ├── valuation/       # Valuation schemas
│   │   └── unified/         # Unified schemas
│   └── display/             # Display schemas
│       ├── charts.json      # Chart configurations
│       ├── tables.json      # Table configurations
│       └── dashboards.json  # Dashboard configurations
│
├── metadata_registry/       # Metadata & lookup data (JSON)
│   ├── metrics/
│   │   └── metric_registry.json         # 2,099 metrics (770 KB)
│   ├── sectors/
│   │   ├── sector_industry_registry.json  # 457 tickers × 19 sectors × 4 entity types
│   │   └── ...
│   ├── tickers/
│   │   ├── ticker_details.json
│   │   └── ...
│   └── config/
│       └── ...
│
├── business_logic/          # Business rules & configs (JSON, 9 files)
│   ├── analysis/
│   │   └── ...
│   ├── decisions/
│   │   └── ...
│   └── alerts/
│       └── ...
│
└── schemas/                 # LEGACY (backward compatibility)
    ├── master_schema.json
    └── data/
        ├── fundamental_calculated_schema.json
        ├── technical_calculated_schema.json
        └── ...
```

### Key Classes

| Class | File | Purpose |
|-------|------|---------|
| DataMappingRegistry | `data_mapping/registry.py` | Singleton YAML loader (data_sources, pipelines, dashboards, services) - zero hardcoded paths |
| PathResolver | `data_mapping/resolver.py` | Path validation & resolution via registry |
| DependencyResolver | `data_mapping/resolver.py` | Impact analysis (what breaks when source changes) |
| SchemaValidator | `data_mapping/validator.py` | Schema validation against YAML definitions |
| HealthChecker | `data_mapping/validator.py` | Data quality health checks (missing files, schema mismatches) |
| MetricRegistry | `registries/metric_lookup.py` | Metric code lookup (2,099 metrics, Vietnamese to English mapping) |
| SectorRegistry | `registries/sector_lookup.py` | Ticker-sector mapping (457 tickers, 19 sectors, 4 entity types) |
| SchemaRegistry | `schema_registry.py` | Data formatting (format_price, format_percent, format_market_cap) |

---

## 6. MCP_SERVER Module

**Location:** `/MCP_SERVER`
**Files:** 18 Python files
**Tools:** 30 MCP tools (FastMCP)

### Structure

```
MCP_SERVER/
├── bsc_mcp/
│   ├── server.py            # FastMCP server (stdio transport)
│   ├── config.py            # Configuration
│   └── tools/               # Tool implementations (30 tools)
│       ├── ticker_tools.py              # 5 tools (list, search, info, peers, sectors)
│       ├── fundamental_tools.py          # 5 tools (financials, comparison, screening)
│       ├── technical_tools.py            # 8 tools (indicators, alerts, patterns, breadth)
│       ├── valuation_tools.py            # 6 tools (PE/PB stats, comparison)
│       ├── forecast_tools.py             # 4 tools (BSC forecasts, upside)
│       └── macro_tools.py                # 2 tools (economic data, commodities)
└── README.md
```

### Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| Ticker | 5 | List tickers, search, get info, get peers, list sectors |
| Fundamental | 5 | Get financials, compare fundamentals, screen by metrics |
| Technical | 8 | Get indicators, get alerts, get patterns, market breadth |
| Valuation | 6 | Get PE/PB stats, compare valuations, sector valuation |
| Forecast | 4 | List BSC forecasts, get BSC forecast, get top upside stocks |
| Macro | 2 | Get macro data, get commodity prices |

---

## 7. Module Dependencies

```
WEBAPP (Frontend - 113 files)
    ↓ imports
services/ → PROCESSORS/core/ + config/registries
    ↓ reads
DATA/processed/
    ↓ uses
core/session_state.py (CRITICAL for page stability)
core/theme.py (Crypto Terminal Glassmorphism)

PROCESSORS (Backend - 110 files)
    ↓ imports
api/ → external APIs (VNStock, WiChart, Simplize, Fireant, Vietcap)
core/ → config/registries
    ↓ writes
DATA/processed/

config/ (Shared - 41 files)
    ↑ imported by
WEBAPP, PROCESSORS, MCP_SERVER
```

---

## 8. Daily Pipeline Order (6 Steps)

```
1. OHLCV Update
   └── OHLCVDailyUpdater → DATA/raw/ohlcv/OHLCV_mktcap.parquet

2. Technical Analysis (9 steps)
   └── daily_ta_complete.py →
       ├── VN-Index Analysis (500 sessions)
       ├── Technical Indicators (200 sessions)
       ├── Alert Detection (MA, Volume, Breakout, Patterns)
       ├── Money Flow Calculation
       ├── Sector Money Flow (1D, 1W, 1M)
       ├── Market Breadth
       ├── Sector Breadth
       ├── Market Regime Detection
       └── RS Rating Calculation
   └→ DATA/processed/technical/

3. Macro & Commodity
   └── MacroCommodityFetcher → DATA/processed/macro_commodity/

4. Valuation Metrics
   └── HistoricalPE/PB/PS/EV → DATA/processed/valuation/

5. Sector Analysis
   └── SectorProcessor → DATA/processed/sector/

6. Unified Update (Recommended)
   └── run_all_daily_updates.py (runs all above)
```

**Commands:**
```bash
# Recommended: Run all updates
python3 PROCESSORS/pipelines/run_all_daily_updates.py

# Individual updates
python3 PROCESSORS/pipelines/daily/daily_ta_complete.py          # Complete TA pipeline
python3 PROCESSORS/pipelines/daily/daily_ohlcv_update.py         # OHLCV update
python3 PROCESSORS/pipelines/daily/daily_macro_commodity_update.py # Macro & commodity
python3 PROCESSORS/pipelines/daily/daily_valuation.py            # Valuation metrics
python3 PROCESSORS/pipelines/daily_sector_complete_update.py     # Complete sector update
```

---

## Related Documents

- [Project Overview](project-overview-pdr.md) - Vision, requirements, roadmap
- [System Architecture](system-architecture.md) - Data flow, component interactions
- [Code Standards](code-standards.md) - Naming conventions, patterns
- [CLAUDE.md](../CLAUDE.md) - AI/Developer guidelines (CRITICAL)
- [Technical Module README](../WEBAPP/pages/technical/README.md) - Technical analysis documentation (658 lines)
