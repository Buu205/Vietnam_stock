# PROCESSORS/ Architecture Scout Report

**Date:** 2025-12-29  
**Status:** Complete architecture mapped  
**Total Files:** 86 Python modules (110 in codebase incl. __pycache__)  
**Report Type:** External agentic scout (Bash + file analysis)

---

## Executive Summary

PROCESSORS/ is a production-grade data processing pipeline system for Vietnamese stock market analysis. It implements a **6-stage daily update pipeline** that orchestrates financial metrics calculation, technical indicator generation, valuation analysis, and sector-level aggregation.

**Key Metrics:**
- 9 major directories with distinct responsibilities
- 110 active Python modules
- 32,417 total lines of code
- 6 critical pipeline stages (OHLCV → Valuation → Sector)
- 3 entity types supported (company, bank, insurance, security)

---

## 🏗️ Directory Structure & Organization

### Core Hierarchy

```
PROCESSORS/
├── pipelines/         [9 files]   Master orchestration (entry points)
├── core/             [29 files]   Shared utilities & infrastructure
├── fundamental/      [11 files]   Financial metrics calculators
├── technical/        [12 files]   Technical analysis processors
├── valuation/        [12 files]   Valuation metrics (PE/PB/EV-EBITDA)
├── sector/           [13 files]   Sector aggregation & scoring
├── forecast/         [3 files]    BSC Excel forecast processing
├── api/              [15 files]   Data source APIs (VietCap, etc.)
└── decision/         [1 file]     Trading decisions (legacy/experimental)
```

---

## 📊 DETAILED BREAKDOWN

### 1. PIPELINES/ (9 files) - Entry Points & Orchestration

**Purpose:** Master orchestrator for daily updates with progress tracking and data integrity validation.

**Key Files:**
- `run_all_daily_updates.py` (660+ lines) - **MAIN ENTRY POINT**
  - Orchestrates all 6 pipeline stages
  - Supports `--skip-*` and `--only` flags
  - Includes logging, progress tracking, data integrity reports
  - ~45 minute execution time for full pipeline

- `daily/` subdirectory (8 files):
  - `daily_ohlcv_update.py` - Stage 1: Market data fetch (vnstock)
  - `daily_ta_complete.py` - Stage 2: Technical indicators (MA, RSI, MACD)
  - `daily_macro_commodity.py` - Stage 3: Macro/commodity data
  - `daily_valuation.py` - Stage 4: Individual stock valuation
  - `daily_sector_analysis.py` - Stage 5: Sector aggregation
  - `daily_bsc_forecast.py` - Stage 6: BSC forecast updates
  - `daily_rs_rating.py` - Relative strength rating
  - `DAILY_PIPELINE_SUMMARY.md` - Documentation

**Usage:**
```bash
# Run all updates
python3 PROCESSORS/pipelines/run_all_daily_updates.py

# Skip specific stages
python3 PROCESSORS/pipelines/run_all_daily_updates.py --skip-ohlcv --skip-ta

# Run only one stage
python3 PROCESSORS/pipelines/run_all_daily_updates.py --only valuation
```

---

### 2. CORE/ (29 files) - Shared Infrastructure

**Purpose:** Reusable utilities, path configuration, validation, and AI-powered tools.

#### 2.1 config/ (2 files) - Path Resolution
- `paths.py` - Centralized v4.0.0 path definitions
  - `PROJECT_ROOT`, `DATA_ROOT`, `RAW_DATA`, `PROCESSED_DATA`
  - Helper functions: `get_fundamental_path()`, `get_technical_path()`
  - Used by ALL modules for consistent data access

#### 2.2 shared/ (14 files) - Utilities & Data Management
**Active:**
- `unified_mapper.py` - Unified ticker/sector mapping (core utility)
- `symbol_loader.py` - Load symbols from metadata
- `data_source_manager.py` - Manage data sources
- `data_validator.py` - Validate input/output data
- `date_formatter.py` - Standardize date formats
- `consistency_checker.py` - Check data consistency
- `backup_logger.py` - Logging utilities

**Legacy (Reference Only):**
- `analyze_missing_quarters.py` - One-time fix script
- `database_migrator.py` - Old migration script
- `merge_from_copy.py` - One-time merge script
- `restore_missing_quarters*.py` - One-time restoration scripts
- `technical_data_retention.py` - Data retention policy

#### 2.3 formatters/ (2 files) - Data Formatting
- `ohlcv_formatter.py` - Format OHLCV data
- `ohlcv_validator.py` - Validate OHLCV structure

#### 2.4 validators/ (3 files) - Input/Output Validation
- `input_validator.py` - Validate input data
- `output_validator.py` - Validate output data
- `bsc_csv_adapter.py` - BSC CSV adapter

#### 2.5 ai/ (4 files) - AI-Powered Tools (Experimental)
- `formula_code_generator.py` - Generate formula code from descriptions
- `nlp_formula_parser.py` - Parse formulas using NLP
- `metric_registry_resolver.py` - Resolve metrics from registry
- `formula_ai_assistant.py` - AI formula assistant

---

### 3. FUNDAMENTAL/ (11 files) - Financial Metrics Calculators

**Purpose:** Calculate profitability, efficiency, and growth metrics for 4 entity types.

#### 3.1 calculators/ (2 files)
- `run_all_calculators.py` (1,032 lines) - **MAIN CALCULATOR**
  - Unified entry point for all entity calculators
  - Calculates metrics for: company, bank, insurance, security
  - Outputs parquet files to `DATA/processed/fundamental/{entity}/`
  - **Critical metrics:**
    - Company: ROE, ROA, gross/net margins, growth rates
    - Bank: NIM, CAR, LDR, CASA, NPL, LLCR
    - Insurance: ROA, combined ratio, solvency ratio
    - Security: ROA, commission ratio, market share

- `__init__.py` (49 lines) - Module initialization

**Execution:**
```bash
# Run all entity calculators
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py

# Run specific entity
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity bank
```

#### 3.2 formulas/ (7 files) - Pure Calculation Functions
- `_base_formulas.py` - Universal formulas for all entities
  - `calculate_roe()`, `calculate_roa()`, `calculate_gross_margin()`
  - `calculate_net_margin()`, `calculate_operating_margin()`
  - `calculate_debt_to_equity()`, `calculate_current_ratio()`
  - `calculate_yoy_growth()`, `calculate_qoq_growth()`
  - `calculate_ttm_sum()`, `calculate_ttm_avg()`
  - Utilities: `safe_divide()`, `to_percentage()`

- `company_formulas.py` - Company-specific calculations
  - `CompanyFormulas` class with revenue/profit growth, FCF

- `bank_formulas.py` - Bank-specific calculations
  - `BankFormulas` class with NIM, CAR, LDR, CASA, NPL

- `registry.py` - Formula registry for lookups

- `utils.py` - Helper functions

- `__init__.py` - Module exports

#### 3.3 Other Files
- `csv_to_full_parquet.py` - Convert raw CSV data to parquet
- `formula_modification_guide.md` - Documentation

**Output Locations:**
```
DATA/processed/fundamental/
├── company/company_financial_metrics.parquet
├── bank/bank_financial_metrics.parquet
├── insurance/insurance_financial_metrics.parquet
└── security/security_financial_metrics.parquet
```

---

### 4. TECHNICAL/ (12 files) - Technical Analysis Processors

**Purpose:** Generate technical indicators, alerts, breadth, and money flow analysis.

#### 4.1 indicators/ (8 files) - TA Processor Suite
- `technical_processor.py` (385 lines) - **MAIN TA PROCESSOR**
  - Calculates: MA, EMA, RSI, MACD, Bollinger Bands, Stochastic
  - Detects: Oversold/overbought conditions, crossovers
  - Generates: Buy/sell signals
  - Outputs: `DATA/processed/technical/basic_data.parquet`

- `alert_detector.py` (811 lines) - Complex alert detection
  - Golden cross, death cross, RSI crossovers
  - Bollinger band breakouts, channel breakouts
  - Momentum divergence, trend reversals

- `money_flow.py` (319 lines) - Individual stock money flow
  - Buy/sell volume analysis
  - Money flow accumulation patterns

- `sector_money_flow.py` (427 lines) - Sector-level money flow
  - Aggregate money flow by sector
  - Identify sector rotation patterns

- `sector_breadth.py` (247 lines) - Sector breadth metrics
  - Advance/decline ratios
  - Sector performance ranking

- `market_regime.py` (375 lines) - Market regime detection
  - Bull/bear/neutral regime classification
  - Volatility assessment

- `vnindex_analyzer.py` (309 lines) - VN-Index analysis
  - VN-Index technical levels
  - Market structure analysis

- `rs_rating.py` (287 lines) - Relative strength rating
  - Compare ticker strength to market/sector

**Execution:**
```bash
python3 PROCESSORS/technical/indicators/technical_processor.py
```

#### 4.2 ohlcv/ (2 files) - OHLCV Data Management
- `ohlcv_daily_updater.py` (488 lines) - Daily market data update
  - Fetch from vnstock API
  - Validate and store in parquet format
  - Outputs: `DATA/raw/ohlcv/OHLCV_mktcap.parquet`

- `ohlcv_adjustment_detector.py` (628 lines) - Detect data adjustments
  - Identify stock splits, dividends, corporate actions
  - Flag suspicious price movements

#### 4.3 macro_commodity/ (1 file) - Macro/Commodity Fetching
- `macro_commodity_fetcher.py` (191 lines) - Fetch economic data
  - Fetch GDP, inflation, interest rates, commodities
  - Outputs: `DATA/processed/macro_commodity/macro_commodity_unified.parquet`

---

### 5. VALUATION/ (12 files) - Valuation Metrics

**Purpose:** Calculate PE, PB, PS, EV/EBITDA ratios for stocks and VN-Index.

#### 5.1 calculators/ (6 files)
- `historical_pe_calculator.py` (661 lines) - P/E ratio calculator
  - Individual stock PE ratios
  - Tracks PE trends over time
  - Outputs: `DATA/processed/valuation/pe/historical/historical_pe.parquet`

- `historical_pb_calculator.py` (545 lines) - P/B ratio calculator
  - Book value ratios
  - Outputs: `DATA/processed/valuation/pb/historical/historical_pb.parquet`

- `historical_ps_calculator.py` (read-only, 545 lines) - P/S ratio calculator
  - Price-to-sales ratios
  - Outputs: `DATA/processed/valuation/ps/historical/historical_ps.parquet`

- `historical_ev_ebitda_calculator.py` (347 lines) - EV/EBITDA calculator
  - Enterprise value ratios
  - Outputs: `DATA/processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet`

- `vnindex_valuation_calculator.py` (545 lines) - VN-Index valuation
  - Aggregate index PE, PB, EV/EBITDA
  - Outputs: `DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet`

- `run_full_backfill.py` (117 lines) - One-time backfill script

#### 5.2 formulas/ (2 files)
- `valuation_formulas.py` (661 lines) - Pure valuation functions
  - `calculate_pe_ratio()`, `calculate_pb_ratio()`
  - `calculate_ps_ratio()`, `calculate_ev_ebitda()`
  - Handle edge cases (zero denominator, missing data)

- `metric_mapper.py` (225 lines) - Map metrics between data sources

---

### 6. SECTOR/ (13 files) - Sector Aggregation & Scoring

**Purpose:** Aggregate company-level metrics to sector level and generate sector scores.

#### 6.1 calculators/ (4 files)
- `fa_aggregator.py` (42K) - Fundamental aggregation
  - Aggregate company financials to sector level
  - Calculate sector averages, medians, distributions
  - Outputs: `DATA/processed/sector/sector_fundamental_metrics.parquet`

- `ta_aggregator.py` (31K) - Technical aggregation
  - Aggregate TA signals to sector level
  - Sector momentum, breadth, money flow
  - Outputs: `DATA/processed/sector/sector_technical_metrics.parquet`

- `base_aggregator.py` (5.7K) - Abstract base class
  - Common aggregation logic
  - Template for FA/TA aggregators

- `metric_mappings.py` (8.2K) - Metric definitions
  - Define which metrics to aggregate
  - Weight configurations

#### 6.2 scoring/ (3 files)
- `fa_scorer.py` - Fundamental analysis scoring
  - Score sectors by: profitability, growth, valuation
  - Generate buy/hold/sell signals

- `ta_scorer.py` - Technical analysis scoring
  - Score sectors by: momentum, trend, breadth
  - Identify sector rotation opportunities

- `signal_generator.py` - Combined signal generation
  - Merge FA/TA signals
  - Generate final buy/hold/sell recommendation

#### 6.3 Main Orchestrator
- `sector_processor.py` - Master sector orchestrator
  - Runs FA aggregator → TA aggregator → Scorers
  - Generates sector analysis reports
  - Outputs: `DATA/processed/sector/sector_*.parquet`

#### 6.4 Testing
- `test_scoring.py` - Test scoring logic
- `tests/` - Unit tests directory

---

### 7. FORECAST/ (3 files) - BSC Excel Forecast Processing

**Purpose:** Convert BSC Research Excel forecasts to parquet format.

- `bsc_forecast_processor.py` - **Main processor**
  - Read Excel files from BSC
  - Convert to standardized parquet format
  - Outputs: `DATA/processed/forecast/bsc/`

- `update_bsc_excel.py` - Re-read Excel script
  - Run when BSC updates forecast Excel file
  - Updates current prices for forecast

- `__init__.py` - Module initialization

---

### 8. API/ (15 files) - Data Source APIs

**Purpose:** External data fetching and integration.

**Structure:**
- `clients/` - API client implementations
- `config/` - API configuration
- `core/` - Core API utilities
- `monitoring/` - API health monitoring
- `vietcap/` - VietCap-specific integration
- `unified_fetcher.py` - Unified data fetching interface

---

### 9. DECISION/ (1 file) - Trading Decisions (Legacy)

- `valuation_ta_decision.py` - Combines valuation + TA for decisions
  - **Status:** Experimental, uses old import paths
  - **Action:** Needs update to v4.0.0 architecture

---

## 🔄 Data Flow Architecture

### Pipeline Stages (6-stage daily update)

```
Stage 1: OHLCV Update
├── Input: vnstock API
├── Process: ohlcv_daily_updater.py
└── Output: DATA/raw/ohlcv/OHLCV_mktcap.parquet

Stage 2: Technical Analysis
├── Input: OHLCV data
├── Process: technical_processor.py → 8 indicator files
└── Output: DATA/processed/technical/{indicators,alerts,breadth}/

Stage 3: Macro & Commodity
├── Input: External APIs
├── Process: macro_commodity_fetcher.py
└── Output: DATA/processed/macro_commodity/

Stage 4: Valuation
├── Input: Fundamental + OHLCV
├── Process: PE/PB/EV-EBITDA calculators
└── Output: DATA/processed/valuation/{pe,pb,ps,ev_ebitda,vnindex}/

Stage 5: Sector Analysis
├── Input: Company metrics + TA indicators
├── Process: FA aggregator → TA aggregator → Scorers
└── Output: DATA/processed/sector/sector_*.parquet

Stage 6: BSC Forecast Update
├── Input: Excel forecasts
├── Process: bsc_forecast_processor.py
└── Output: DATA/processed/forecast/bsc/
```

### Entity Type Breakdown

**Company:** 100+ metrics
- Profitability: ROE, ROA, gross/net margins
- Growth: Revenue/profit YoY/QoQ
- Efficiency: Asset turnover, receivables turnover
- Health: Debt-to-equity, current ratio

**Bank:** 20+ metrics
- NIM (Net Interest Margin)
- CAR (Capital Adequacy Ratio)
- LDR (Loan-to-Deposit Ratio) - Pure & Regulated
- CASA (Current Account Savings Account)
- NPL (Non-Performing Loans)
- LLCR (Loan Loss Coverage Ratio)

**Insurance:** TBD

**Security:** TBD

---

## 📈 Key Design Patterns

### 1. Unified Calculators
- Single entry point: `run_all_calculators.py`
- Supports `--entity` flag to run specific entity type
- Consistent output structure across all entities

### 2. Pure Functions + State Management
- Calculation logic: Pure functions in `formulas/`
- Data loading/saving: Stateful managers in `calculators/`
- Validation: Dedicated validators in `core/validators/`

### 3. Registry-Based Lookups
- Metric registry: English name ↔ Vietnamese name mapping
- Sector registry: Ticker ↔ Sector ↔ Industry mapping
- Schema registry: Field definitions, type validation

### 4. Aggregation Layers
- Company-level: Individual financials/technicals
- Sector-level: Aggregated metrics (sum, avg, median)
- Index-level: VN-Index and sector indexes

### 5. Error Handling & Logging
- Centralized logging in `core/shared/backup_logger.py`
- Data validation at each pipeline stage
- Consistency checks before output

---

## 🎯 Entry Points & Usage

### Daily Operations
```bash
# Full daily update (~45 minutes)
python3 PROCESSORS/pipelines/run_all_daily_updates.py

# Skip specific stages
python3 PROCESSORS/pipelines/run_all_daily_updates.py --skip-ohlcv --skip-ta

# Run only valuation
python3 PROCESSORS/pipelines/run_all_daily_updates.py --only valuation
```

### Individual Module Testing
```bash
# Fundamental metrics
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity bank

# Technical analysis
python3 PROCESSORS/technical/indicators/technical_processor.py

# Valuation
python3 PROCESSORS/valuation/calculators/historical_pe_calculator.py

# Sector analysis
python3 PROCESSORS/sector/sector_processor.py

# BSC forecast update
python3 PROCESSORS/forecast/update_bsc_excel.py
```

---

## 📊 File Statistics

| Module | Files | Lines | Purpose |
|--------|-------|-------|---------|
| pipelines | 9 | 660+ | Daily orchestration |
| core | 29 | ~3000 | Shared utilities |
| fundamental | 11 | 1081 | Financial metrics |
| technical | 12 | 4000+ | TA indicators |
| valuation | 12 | 2400+ | PE/PB/EV-EBITDA |
| sector | 13 | 5000+ | Sector aggregation |
| forecast | 3 | ~300 | BSC forecasts |
| api | 15 | ~1500 | Data sources |
| **TOTAL** | **86+** | **32,417** | **Production system** |

---

## ⚠️ Legacy & Experimental

### Experimental (Use with Caution)
- `core/ai/` - AI formula generation (experimental)
- `decision/valuation_ta_decision.py` - Old import paths

### Legacy (Reference Only)
- `core/shared/analyze_missing_quarters.py`
- `core/shared/database_migrator.py`
- `core/shared/merge_from_copy.py`
- `core/shared/restore_missing_quarters*.py`

---

## 🚀 Architecture Highlights

1. **Modularity:** Each module has single responsibility
2. **Reusability:** Pure functions for easy testing
3. **Scalability:** Parquet-based output for large datasets
4. **Consistency:** Registry-based lookups for data integrity
5. **Observability:** Comprehensive logging and validation
6. **Extensibility:** Template classes for new calculators/indicators

---

## 🔗 Dependencies

### External Libraries
- **pandas** - Data manipulation
- **parquet** - Data storage format
- **vnstock** - Vietnamese stock data
- **ta-lib** - Technical analysis indicators
- **streamlit** - Dashboard framework

### Internal Dependencies
```
pipelines/
  └─> core/
  └─> fundamental/
  └─> technical/
  └─> valuation/
  └─> sector/
  └─> forecast/
  └─> api/
```

---

## Summary

PROCESSORS/ is a well-organized, production-grade pipeline system with:
- **Clear separation of concerns** across 9 modules
- **86 Python modules** implementing 6 daily update stages
- **4 entity types** (company, bank, insurance, security)
- **32,417 lines of code** spanning metrics, technicals, valuation, sectors
- **Single entry point** (`run_all_daily_updates.py`) for orchestration
- **Extensible architecture** for adding new metrics/indicators

The codebase follows v4.0.0 architecture with centralized path management, registry-based lookups, and pure functions for calculations.
