# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Vietnamese stock market financial data dashboard and analysis system. The project fetches, processes, and visualizes fundamental, technical, valuation, and forecast data for Vietnamese stocks through a Streamlit interface.

**Primary development location:** `/Users/buuphan/Dev/Vietnam_dashboard`

**Current Status:**
- ✅ Phase 0.1.6 complete (metric registry, sector mapping, OHLCV standardization)
- ✅ Phase 0.2 complete (base financial calculators)
- ✅ v2.0.0 Reorganization complete (clean structure, no technical debt)
- ✅ **v4.0.0 Canonical Architecture (Dec 2024) - 100% COMPLIANCE**
  - Week 1: Canonical structure migration (70% → 90%)
  - Week 2: Validation layer + unified pipelines (90% → 95%)
  - Week 3: BSC CSV adapter + extractors layer (95% → 98%)
  - Week 4: Transformers layer (98% → 100%)
- 🎯 Production ready - All phases complete

## Development Setup

### Python Environment

- **Python Version:** 3.13 (system Python)
- **Python Binary:** `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` or `python3`
- **Key Dependency:** `vnstock_data` installed globally at `/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages`

### Installing Dependencies

```bash
# Core Streamlit app dependencies
pip install -r streamlit_app/requirements.txt

# OHLCV data pipeline dependencies (if working with technical data)
pip install -r data_processor/technical/technical/ohlcv/requirements_ohlcv.txt
```

### Running the Application

```bash
# Start the Streamlit dashboard (default loads Company Dashboard)
streamlit run streamlit_app/main_app.py
```

## Commands for Data Processing

### Daily Update Pipelines

These orchestrator scripts run complete daily updates for their respective domains:

```bash
# Update all valuation metrics (PE/PB/EV_EBITDA, VN-Index PE, sector PE)
python3 data_processor/valuation/daily_full_valuation_pipeline.py

# Update OHLCV data
python3 data_processor/technical/daily_ohlcv_update.py

# Update macro & commodity data
python3 data_processor/technical/daily_macro_commodity_update.py

# Update news data
python3 data_processor/news/news_pipeline.py

# Update BSC forecast data
python3 data_processor/Bsc_forecast/run_bsc_auto_update.py
```

Optional `--date YYYY-MM-DD` argument can be passed to most pipelines for historical updates.

### Fundamental Data Processing (Entity-Specific)

**Phase 0.2 New Calculators (in `/data_processor/fundamental/base/`):**
```bash
# Process company financial data (new Phase 0.2 calculator)
python3 data_processor/fundamental/base/company_financial_calculator.py

# Process bank financial data (new Phase 0.2 calculator)
python3 data_processor/fundamental/base/bank_financial_calculator.py

# Process insurance financial data (new Phase 0.2 calculator)
python3 data_processor/fundamental/base/insurance_financial_calculator.py

# Process security/brokerage financial data (new Phase 0.2 calculator)
python3 data_processor/fundamental/base/security_financial_calculator.py
```

**Note:** Old calculators archived to `/archive/deprecated_v1.0/fundamental_old_calculators/`

### MongoDB Operations

```bash
# Upload all financial metrics to MongoDB Atlas
python -m mongodb.uploader

# Upload specific collection
python -m mongodb.uploader --collection company_metrics --parquet calculated_results/fundamental/company/company_financial_metrics.parquet
```

### MCP Server

```bash
# Start MCP server for MongoDB queries
python -m mcp_server.server

# Start local file-based MCP server (no MongoDB required)
python -m mcp_server.local_server
```

### Registry & Mapping Tools

```bash
# Build metric registry from BSC Excel templates
python3 data_processor/core/build_metric_registry.py

# Build sector/industry registry from ticker metadata
python3 data_processor/core/build_sector_registry.py

# Test unified ticker mapper integration
python3 data_processor/core/test_unified_mapper.py

# Demo metric lookup usage
python3 data_processor/core/metric_lookup.py

# Demo sector lookup usage
python3 data_processor/core/sector_lookup.py

# Demo unified mapper usage
PYTHONPATH=$PWD python3 data_processor/core/unified_mapper.py

# Test OHLCV standardization (Phase 0.1.6)
python3 data_processor/core/test_ohlcv_standardization.py

# Demo OHLCV formatter
python3 data_processor/core/ohlcv_formatter.py

# Demo OHLCV validator
python3 data_processor/core/ohlcv_validator.py
```

### Data Validation & Quality

```bash
# Validate fundamental data consistency
python3 data_processor/core/data_validator.py

# Check consistency across quarters
python3 data_processor/core/consistency_checker.py

# Analyze missing quarters
python3 data_processor/core/analyze_missing_quarters.py

# Restore missing quarters from backups
python3 data_processor/core/restore_missing_quarters.py
```

### Utility Scripts

```bash
# Convert parquet files to Excel
python3 convert_parquet_to_excel.py

# Push data to GitHub
python3 scripts/push_data_to_github.py
```

---

## v4.0.0 Canonical Architecture (Dec 2024)

### Overview

The v4.0.0 release represents a complete migration to canonical architecture patterns, achieving **100% compliance** through a structured 4-week implementation:

- **Week 1:** DATA/PROCESSORS separation (70% → 90% compliance)
- **Week 2:** Validation layer + unified pipelines (90% → 95%)
- **Week 3:** BSC CSV adapter + extractors layer (95% → 98%)
- **Week 4:** Transformers layer (98% → 100%)

**Key Achievement:** Professional data engineering architecture with clean separation of concerns.

### Week 1: Canonical Structure Migration

**Goal:** Separate data from processing logic

**Changes:**
- Created `DATA/` directory (1.1GB) - All data centralized
  - `DATA/raw/` - Source data (OHLCV, fundamental CSVs, commodity, macro)
  - `DATA/processed/` - Calculated results (102 parquet files)
  - `DATA/metadata/` - Registries (metric_registry, sector_registry)
  - `DATA/schemas/` - Unified schemas

- Created `PROCESSORS/` directory (9.9MB) - All logic organized
  - `PROCESSORS/core/` - Utilities, formatters, registries, config
  - `PROCESSORS/fundamental/` - Financial calculators (4 entity types)
  - `PROCESSORS/technical/` - Technical indicators
  - `PROCESSORS/valuation/` - PE/PB calculators
  - `PROCESSORS/news/` - News processing
  - `PROCESSORS/forecast/` - BSC forecast

- Renamed `streamlit_app/` → `WEBAPP/`

- Deleted old folders: `data_warehouse/`, `calculated_results/`, `data_processor/`

- Fixed 35+ import paths

- Centralized paths: `PROCESSORS/core/config/paths.py`

**Result:** Reclaimed 1.1GB disk space, professional structure ready for production.

**Commands:**
```bash
# All calculators now run from PROCESSORS/
python3 PROCESSORS/fundamental/calculators/company_calculator.py
python3 PROCESSORS/fundamental/calculators/bank_calculator.py
```

### Week 2: Validation Layer + Unified Pipelines

**Goal:** Add input/output validation and create unified execution pipelines

**New Components:**

1. **InputValidator** (`PROCESSORS/core/validators/input_validator.py` - 11.5KB)
   - Validates CSV files before processing
   - Checks: file existence, schema compliance, data types, business logic
   - Auto-detects and adapts BSC CSV format

2. **OutputValidator** (`PROCESSORS/core/validators/output_validator.py` - 14.8KB)
   - Validates calculated metrics
   - Range checking for financial ratios
   - Data quality assertions

3. **Quarterly Report Pipeline** (`PROCESSORS/pipelines/quarterly_report.py` - 12.5KB)
   - Unified quarterly processing for all 4 entity types
   - Validation at each step
   - Automatic backup before processing

4. **Daily Update Pipeline** (`PROCESSORS/pipelines/daily_update.py` - 10.3KB)
   - Orchestrates daily updates (technical, valuation, commodity, macro)

**Usage:**
```bash
# Quarterly fundamental update with validation
python3 PROCESSORS/pipelines/quarterly_report.py --quarter 3 --year 2025

# Daily market data update
python3 PROCESSORS/pipelines/daily_update.py

# Validate CSV before processing
from PROCESSORS.core.validators import InputValidator
validator = InputValidator()
result = validator.validate_csv(csv_path, "COMPANY")
```

**Result:** Robust validation layer preventing invalid data from entering calculations.

### Week 3: BSC CSV Adapter + Extractors Layer

**Goal:** Handle BSC CSV format automatically and centralize data loading

**Critical Fix: BSC CSV Adapter** (`PROCESSORS/core/validators/bsc_csv_adapter.py` - 9.8KB)

**Problem:** BSC CSV files use different column names:
```python
# BSC Format:
SECURITY_CODE, REPORT_DATE, FREQ_CODE

# Expected Format:
ticker, year, quarter, lengthReport
```

**Solution:** Auto-adaptation layer
```python
from PROCESSORS.core.validators import BSCCSVAdapter

adapter = BSCCSVAdapter()
standard_df = adapter.adapt_csv_file("COMPANY_BALANCE_SHEET.csv")

# Column mappings:
# SECURITY_CODE → ticker
# REPORT_DATE   → year, quarter (parsed from date)
# FREQ_CODE     → lengthReport
#   Q + 3 months  → "Q1"
#   Q + 6 months  → "Q2"
#   Q + 9 months  → "Q3"
#   Y or Q + 12   → "YEAR"
```

**Tested:** 54,704 rows successfully adapted

**Extractors Layer** (`PROCESSORS/extractors/csv_loader.py` - 7.2KB)

Centralized CSV loading with auto-BSC adaptation:
```python
from PROCESSORS.extractors import CSVLoader

loader = CSVLoader()

# Single statement
df = loader.load_fundamental_csv("COMPANY", "balance_sheet", quarter=3, year=2025)

# All statements
statements = loader.load_all_statements("COMPANY", quarter=3, year=2025)
# Returns: {'balance_sheet': df1, 'income': df2, 'cashflow': df3}
```

**Result:** BSC CSV format fully supported, data loading centralized, no more format errors.

### Week 4: Transformers Layer

**Goal:** Separate calculation logic from data orchestration

**New Layer:** `PROCESSORS/transformers/financial/formulas.py` (600+ LOC, 30+ functions)

**Architecture Pattern:**
```
CALCULATORS (orchestration)
     ↓
TRANSFORMERS (pure calculations)
```

**Available Functions:**

**Basic Utilities:**
- `safe_divide(numerator, denominator)` - Division with None/zero handling
- `convert_to_billions(value)` - Convert to billions
- `percentage_change(current, previous)` - % change

**Financial Ratios:**
- `roe(net_income, total_equity)` - Return on Equity
- `roa(net_income, total_assets)` - Return on Assets
- `nim(net_interest_income, avg_earning_assets)` - Net Interest Margin (banks)
- `cir(operating_expenses, operating_income)` - Cost-to-Income Ratio (banks)
- `npl_ratio(non_performing_loans, total_loans)` - NPL ratio (banks)
- `combined_ratio(loss_ratio, expense_ratio)` - Combined ratio (insurance)

**Margins:**
- `gross_margin(gross_profit, revenue)`
- `net_margin(net_income, revenue)`
- `ebit_margin(ebit, revenue)`
- `ebitda_margin(ebitda, revenue)`

**Growth:**
- `qoq_growth(current_q, previous_q)` - Quarter-over-quarter
- `yoy_growth(current_y, previous_y)` - Year-over-year
- `cagr(ending, beginning, periods)` - Compound annual growth rate

**Valuation:**
- `pe_ratio(price, eps)` - Price-to-Earnings
- `pb_ratio(price, bvps)` - Price-to-Book
- `ev_ebitda(enterprise_value, ebitda)` - EV/EBITDA

**Usage Example:**
```python
from PROCESSORS.transformers.financial import roe, roa, gross_margin

# Pure function calls (no DataFrame required)
company_roe = roe(net_income=15.0, total_equity=200.0)  # 7.5%
company_roa = roa(net_income=15.0, total_assets=500.0)  # 3.0%
company_margin = gross_margin(gross_profit=30.0, revenue=100.0)  # 30.0%
```

**Testing:**
```bash
# Demo script
python3 PROCESSORS/transformers/financial/formulas.py

# Output:
# Gross Margin: 30.00%
# Net Margin: 15.00%
# ROE: 7.50%
# ROA: 3.00%
```

**Benefits:**
- ✅ Pure functions (no side effects)
- ✅ Easy to test (primitive types, not DataFrames)
- ✅ Reusable across all entity calculators
- ✅ Full type hints
- ✅ Zero duplication

**Documentation:** See `/docs/TRANSFORMERS_LAYER_GUIDE.md` for complete guide

**Result:** 100% separation of calculation logic from orchestration. Production-ready architecture.

---

## Architecture & Data Flow

### Three-Layer Data Architecture

1. **Raw Data** (`data_warehouse/raw/`)
   - `ohlcv/OHLCV_mktcap.parquet` - Price, volume, market cap data
   - `fundamental/processed/` - Processed financial statements by entity type:
     - `company_full.parquet`
     - `bank_full.parquet`
     - `insurance_full.parquet`
     - `security_full.parquet`
   - `commodity/` - Commodity prices
   - `macro/` - Interest rates, exchange rates
   - `news/` - News articles

2. **Processing Layer** (`data_processor/`)
   - `fundamental/{company,bank,insurance,security}/` - Financial metrics calculators
   - `technical/technical/` - Technical indicators (OHLCV, MA/EMA, RSI, MACD, Bollinger Bands, market breadth)
   - `valuation/core/` - PE/PB/EV_EBITDA calculators
   - `news/` - News aggregation pipeline
   - `Bsc_forecast/` - BSC Excel forecast integration
   - `core/` - Shared utilities (data validation, backup, restore, consistency checking)

3. **Calculated Results** (`calculated_results/`)
   - `fundamental/` - Calculated financial metrics by entity type
   - `technical/` - Technical indicators output (basic_data, moving_averages, rsi, macd, bollinger_bands, market_breadth, etc.)
   - `valuation/` - PE/PB ratios, VN-Index PE, sector PE
   - `commodity/`, `macro/` - Processed market data
   - `forecast/bsc/` - BSC forecast outputs

**Important:** All scripts in `data_processor` resolve paths relative to the project root. Never use iCloud paths.

### Data Processor Structure (v2.0.0 Reorganized)

```
data_processor/
├── __init__.py                     ✅ Proper Python package
├── core/                           # Shared utilities & registries ⭐
│   ├── __init__.py
│   ├── unified_mapper.py          # PRIMARY integration component
│   ├── metric_lookup.py           # Metric registry lookup
│   ├── sector_lookup.py           # Sector registry lookup
│   ├── ohlcv_formatter.py         # OHLCV display formatting (Phase 0.1.6)
│   ├── ohlcv_validator.py         # OHLCV data validation (Phase 0.1.6)
│   ├── data_validator.py          # Data validation
│   ├── consistency_checker.py     # Cross-quarter consistency
│   ├── backup_logger.py           # Data modification tracking
│   └── date_formatter.py          # Date handling
├── fundamental/                    # Financial metrics calculators
│   ├── __init__.py
│   └── base/                      # ✅ Phase 0.2 COMPLETE - New calculators
│       ├── base_financial_calculator.py      # Base class for all entities
│       ├── company_financial_calculator.py   # Company metrics
│       ├── bank_financial_calculator.py      # Bank metrics
│       ├── insurance_financial_calculator.py # Insurance metrics
│       └── security_financial_calculator.py  # Security metrics
├── technical/                      # ✅ FLATTENED (was technical/technical/)
│   ├── __init__.py
│   ├── ohlcv/                     # Price & volume data
│   │   ├── __init__.py
│   │   └── ohlcv_daily_updater.py
│   ├── commodity/                 # Commodity prices
│   │   ├── __init__.py
│   │   └── commodity_price_updater.py
│   ├── macro/                     # Macro indicators
│   │   ├── __init__.py
│   │   └── macro_data_fetcher.py
│   ├── indicators/                # ✅ Renamed from technical_indicators
│   │   ├── __init__.py
│   │   ├── technical_processor.py
│   │   ├── market_breadth_processor.py
│   │   └── ma_screening_processor.py
│   ├── daily_ohlcv_update.py
│   ├── daily_macro_commodity_update.py
│   └── daily_full_technical_pipeline.py
├── valuation/                      # PE/PB/EV ratios
│   ├── __init__.py
│   └── core/                      # Valuation calculators
├── news/                           # News aggregation
│   ├── __init__.py
│   └── news_pipeline.py
└── Bsc_forecast/                   # BSC Excel forecast integration
    └── run_bsc_auto_update.py
```

**Note:** Old calculators (company/, bank/, insurance/, security/ folders) archived to `/archive/deprecated_v1.0/`

### Streamlit App Structure (v2.0.0)

```
streamlit_app/
├── __init__.py           # ✅ Package marker (v2.0.0)
├── main_app.py           # Entry point - loads Company Dashboard by default
├── core/                 # Configuration, data loading, formatters, utilities, models
├── domains/              # Domain-specific data loading (banking, company, forecast, technical)
├── pages/                # Dashboard pages (bank, company, securities, forecast, news)
│                         # ⚠️ Large files (1,200-2,140 LOC) - future: split into modular
├── features/             # Business logic (growth, scoring, signals, valuation)
├── components/           # Reusable UI components (metrics display, summary rows)
├── charts/               # Chart configurations (valuation_charts.py)
├── layout/               # UI layout components (sidebar.py)
├── services/             # External services (LLM, chat, loaders, query builders)
└── ai/                   # AI integration (prompts, schemas, validators)
```

The app uses domain-driven design with separate data loaders for each entity type (company, bank, insurance, security).

**Note:** Page files are large (1,200-2,140 LOC). Future Phase 0.3+ will split into smaller, modular components (<500 LOC each).

### MongoDB Integration

- **Collections:** `company_metrics`, `bank_metrics`, `insurance_metrics`, `security_metrics`
- **Connection:** MongoDB Atlas via `MONGODB_URI` environment variable
- **Schema:** Unique index on `(symbol, report_date, year, quarter)`
- **Uploader:** `mongodb/uploader.py` handles upsert logic
- **Queries:** `mongodb/queries.py` provides query patterns (latest, timeseries, top symbols, comparisons)

### MCP Server Architecture

Two MCP servers are available:

1. **MongoDB MCP Server** (`mcp_server/server.py`):
   - Tools: `query_collection`, `get_collection_schema`, `list_collections`, `get_collection_stats`
   - Query types: symbol, latest, top, timeseries, compare
   - Handlers in `mcp_server/handlers/`

2. **Local Data MCP Server** (`mcp_server/local_server.py`):
   - Direct parquet/CSV access without MongoDB
   - Tools: `list_local_datasets`, `get_dataset_schema`, `preview_dataset`, `query_dataset`
   - Pre-configured datasets: ohlcv, fundamental (company/bank/insurance/security), commodity, interest_rates, exchange_rates

## Code Conventions

### File & Module Naming
- Files/modules: `snake_case`
- Classes: `CamelCase`
- Functions/variables: `snake_case`
- DataFrame variables: descriptive with `_df` suffix (e.g., `price_df`, `pe_ratio_df`)
- Streamlit widget keys: `lower_snake_case`

### Data Processing Patterns
- Parquet is the primary data format for storage
- Use `pandas` for data manipulation
- DuckDB for efficient parquet queries
- PyArrow for parquet I/O
- Always handle NaN/None values before MongoDB upload
- Normalize symbols: uppercase, strip whitespace

### Path Resolution
All paths in `data_processor` scripts should:
- Use `Path(__file__).resolve().parents[N]` to find project root
- Read from `data_warehouse/raw/`
- Write to `calculated_results/`
- Never hardcode absolute paths or iCloud paths

### Error Handling & Logging
- Use Python's `logging` module
- **Log files centralized in `/logs/processors/`** (v2.0.0 reorganization)
- Include context in error messages
- Use `backup_logger.py` for data modification tracking

### v2.0.0 Reorganization Changes

**Centralized Logs:**
```
logs/
├── processors/  # All data processing logs (moved from root + data_processor/logs/)
├── streamlit/   # Streamlit app logs (future)
└── mcp/         # MCP server logs (future)
```

**Archived Technical Debt:**
```
archive/
└── deprecated_v1.0/
    ├── copy/                            # Old duplicate code (removed from active codebase)
    └── fundamental_old_calculators/     # Pre-Phase 0.2 calculators
        ├── company/
        ├── bank/
        ├── insurance/
        └── security/
```

**Import Path Changes:**

❌ **Old (Broken):**
```python
from data_processor.technical.technical.ohlcv import ohlcv_daily_updater
from data_processor.technical.technical.commodity import commodity_price_updater
from data_processor.technical.technical.technical_indicators import technical_processor
```

✅ **New (Correct):**
```python
from data_processor.technical.ohlcv import ohlcv_daily_updater
from data_processor.technical.commodity import commodity_price_updater
from data_processor.technical.indicators import technical_processor
```

**Key Improvements:**
- Reduced directory nesting from 3 → 2 levels
- Added 12+ `__init__.py` package markers for proper Python imports
- Eliminated 100% duplicate code
- Centralized all logs to single location
- Professional structure ready for Phase 0.3+

## Entity Types & Financial Metrics

The system handles four entity types, each with specialized metrics:

1. **Company** - Standard corporations (most common)
2. **Bank** - Banking institutions (specialized ratios like NPL, CIR, NIM)
3. **Insurance** - Insurance companies (combined ratio, loss ratio)
4. **Security** - Securities/brokerage firms

### Metric & Sector Registries (Phase 0.1-0.1.6 Complete)

**Metric Registry** (`data_warehouse/metadata/metric_registry.json`):
- 2,099 metrics extracted from BSC Excel templates
- Maps Vietnamese names → metric codes (e.g., "Lợi nhuận sau thuế" → "net_income")
- Enables AI-powered natural language queries
- Lookup: `data_processor/core/metric_lookup.py`

**Sector/Industry Registry** (`data_warehouse/metadata/sector_industry_registry.json`):
- 457 tickers classified by 19 sectors and 4 entity types
- Source: `data_warehouse/raw/metadata/ticker_details.json`
- Lookup: `data_processor/core/sector_lookup.py`

**Unified Ticker Mapper** (`data_processor/core/unified_mapper.py`):
- **PRIMARY integration component** for Phase 0.2+
- Auto-selects calculator class by ticker
- Validates metrics for entity type
- Identifies peer tickers by sector
- Single interface for AI agents and calculators

**OHLCV Schema & Tools** (`calculated_results/schemas/ohlcv_data_schema.json`):
- Standardized display formats for prices, volumes, percentages
- Frequency codes (D/W/M/Q/Y) with descriptions
- Validation rules for trading data quality
- **OHLCVFormatter** (`data_processor/core/ohlcv_formatter.py`): Display formatting utilities
- **OHLCVValidator** (`data_processor/core/ohlcv_validator.py`): Data quality validation
- Usage examples:
  ```python
  from data_processor.core.ohlcv_formatter import OHLCVFormatter
  from data_processor.core.ohlcv_validator import OHLCVValidator

  # Format prices for display
  formatter = OHLCVFormatter()
  price_str = formatter.format_price(25750.5)  # "25,750.50đ"

  # Validate OHLCV data
  validator = OHLCVValidator()
  result = validator.validate_ohlcv_data(df)
  if not result.is_valid:
      print(validator.generate_report(result))
  ```

**Legacy Metrics Metadata** (pre-Phase 0.1):
- `data_warehouse/raw/metadata/entity_metrics/{entity_type}_metrics.py`
- Still used by current calculators (will be refactored in Phase 0.2)

## Key Technical Patterns

### Using UnifiedTickerMapper (Phase 0.2+)

**When building new features, ALWAYS use UnifiedTickerMapper instead of hardcoding entity detection:**

```python
from data_processor.core.unified_mapper import UnifiedTickerMapper

# Initialize once (can be reused)
mapper = UnifiedTickerMapper()

# Get complete ticker information
info = mapper.get_complete_info("ACB")
# Returns: {
#   "ticker": "ACB",
#   "entity_type": "BANK",
#   "sector": "Ngân hàng",
#   "calculator_class": "BankFinancialCalculator",
#   "available_metrics": {...},  # All valid metrics for banks
#   "peer_tickers": ["VCB", "CTG", ...],  # Same sector
#   "metric_prefixes": ["bank_", "company_"]
# }

# Auto-select calculator based on ticker
calculator_class = info["calculator_class"]

# Validate metric codes before calculation
valid_metrics = mapper.validate_metric_codes("ACB", ["roe", "roa", "nim"])
# Returns only metrics valid for this entity type

# Find peer companies
peers = mapper.get_peer_tickers("ACB")  # Returns other banks

# Search metrics by Vietnamese name
metrics = mapper.search_metrics("lợi nhuận")  # Returns all profit-related metrics
```

**Why use UnifiedTickerMapper:**
- Single source of truth for ticker → entity type mapping
- Auto-validates metrics for entity type (prevents bank metrics on insurance companies)
- Enables peer comparison (same sector)
- Supports natural language queries (Vietnamese → metric codes)

### Date Formatting
- Use `data_processor/core/date_formatter.py` for consistent date handling
- Standard format: `YYYY-MM-DD`
- Quarter format: `Q{quarter} {year}` (e.g., `Q3 2025`)

### Data Validation & Consistency
- `data_processor/core/data_validator.py` - Validation logic
- `data_processor/core/consistency_checker.py` - Cross-quarter consistency
- `data_processor/core/analyze_missing_quarters.py` - Gap detection
- `data_processor/core/restore_missing_quarters.py` - Gap filling

### Backup & Recovery
- `data_processor/core/backup_logger.py` - Track data modifications
- Backup logs stored in `data_processor/logs/backup/`
- Archive previous quarter data in `calculated_results/fundamental/archive_q{quarter}_{year}/`

## Testing

Test infrastructure exists in:
- `data_processor/technical/technical/ohlcv/tests*`
- Limited test coverage currently

Run tests:
```bash
pytest data_processor/technical/
```

When adding new features, include regression tests for:
- New technical indicators
- Data transformations
- API wrappers

## Development Roadmap & Next Steps

### Completed Phases
- ✅ **Phase 0.1:** Metric Registry (2,099 metrics mapped)
- ✅ **Phase 0.1.5:** Sector/Industry Mapping (457 tickers classified)
- ✅ **Phase 0.1.6:** OHLCV Standardization (schemas + formatter + validator, 6/6 tests passing)
- ✅ **Phase 0.2:** Base Financial Calculators (unified calculator system with inheritance)
- ✅ **v2.0.0 Reorganization:** Clean structure, no technical debt, proper Python packages

### Next Phase (Phase 0.3)
**Schema Consolidation & Validation System** - 1-2 weeks estimated
- Consolidate all schemas to `/config/schemas/` (from 3 locations → 1)
- Update all formatters to use `SchemaRegistry`
- Create symlinks for metric/sector registries
- Add comprehensive data validation
- See: `/docs/REORGANIZATION_MASTER_PLAN.md` → Week 1-2

### Future Phases
- **Phase 0.4-0.5:** Enhanced Data Pipeline (incremental updates, caching)
- **Phase 1+:** vnstock_ta migration, API layer (FastAPI), comprehensive testing
- See: `/docs/MASTER_PLAN.md` for complete roadmap

### Immediate Next Steps
1. Schema consolidation (Week 1):
   - Merge OHLCV schemas: `calculated_results/schemas/ohlcv_data_schema.json` + `data_warehouse/schemas/ohlcv_schema.json` → `config/schemas/data/ohlcv.json`
   - Consolidate fundamental/technical/valuation schemas
   - Update formatters to use `SchemaRegistry`

2. Streamlit integration (Week 2):
   - Create `streamlit_app/core/formatters.py` wrapper
   - Update 2-3 pages as proof of concept
   - Split large page files into modular components

3. Testing & validation:
   - Add comprehensive tests for base calculators
   - Validate all pipelines work with new structure

## Important Notes

- **No virtual environment:** Project uses global Python 3.13 installation
- **Data files are expendable:** Files in `calculated_results/` and `logs/` are generated artifacts
- **MongoDB credentials:** Store in `.env` file (never commit)
- **iCloud dependency removed:** Old backup at `~/Library/Mobile Documents/.../GitHub/stock_dashboard` is deprecated
- **Streamlit caching:** App uses Redis for caching (configure via environment)
- **BSC forecast:** Requires Excel file `data_processor/Bsc_forecast/BSC Master File Equity Pro.xlsm`
- **Documentation:** Comprehensive guides in `/docs/` - start with `MASTER_PLAN.md`
