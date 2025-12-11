# Stock Dashboard Architecture Analysis & Refactoring Plan

**Date**: 2025-12-04
**Project**: Vietnamese Stock Market Financial Data Dashboard
**Location**: `/Users/buuphan/Dev/stock_dashboard`

---

## 📊 EXECUTIVE SUMMARY

This document provides a comprehensive analysis of the current stock dashboard codebase structure and proposes a clean architecture for long-term development with enhanced MCP integration and extensibility for features like PDF report generation.

### Current State
- **Total Python Files**: ~100+ files
- **Lines of Code**: ~32,000 LOC
- **Technical Debt Level**: HIGH
- **Architecture Quality**: GOOD foundation, POOR organization

### Key Issues
1. ⚠️ **Technical debt**: `/copy` directory with 100% duplicate code
2. ⚠️ **Large files**: Page files ranging 1,200-2,140 LOC
3. ⚠️ **Import issues**: 40+ files using `sys.path` hacks
4. ⚠️ **Code duplication**: 70-80% similarity in valuation calculators
5. ⚠️ **Config fragmentation**: 4 different `config.py` files

---

## 📋 TABLE OF CONTENTS

1. [Current Directory Organization](#1-current-directory-organization)
2. [Streamlit App Structure](#2-streamlit-app-structure)
3. [Data Processing Layer](#3-data-processing-layer)
4. [Data Storage Patterns](#4-data-storage-patterns)
5. [Code Duplication](#5-code-duplication)
6. [Dependency Patterns](#6-dependency-patterns)
7. [MCP Integration Points](#7-mcp-integration-points)
8. [Configuration Management](#8-configuration-management)
9. [Technical Debt & Poor Organization](#9-technical-debt--poor-organization)
10. [Specific Files Needing Reorganization](#10-specific-files-needing-reorganization)
11. [Import/Dependency Issues](#11-importdependency-issues)
12. [Proposed Clean Architecture](#12-proposed-clean-architecture)
13. [Migration Roadmap](#13-migration-roadmap)
14. [Implementation Examples](#14-implementation-examples)

---

## 1. CURRENT DIRECTORY ORGANIZATION

### Top-Level Structure
```
stock_dashboard/
├── streamlit_app/          # Frontend UI application (45 Python files, ~14,600 LOC)
├── data_processor/         # Data processing pipelines (45 Python files, ~17,800 LOC)
├── data_warehouse/         # Raw data storage (parquet/CSV files)
├── calculated_results/     # Processed/computed data outputs
├── mcp_server/            # MCP server implementations (12 Python files)
├── mongodb/               # MongoDB integration layer (6 Python files)
├── config/                # JSON configuration files
├── copy/                  # ⚠️ DUPLICATE FILES - Technical debt
├── scripts/               # Utility scripts
└── docs/                  # Documentation
```

### Key Issues Identified

1. **Log files in root directory** - Should be in dedicated logs folder
2. **`/copy` directory contains duplicates** of fundamental processors
3. **Missing proper package structure** - Only 9 `__init__.py` files
4. **No centralized requirements.txt** - Multiple requirement files scattered

---

## 2. STREAMLIT APP STRUCTURE

### Organization (Domain-Driven Design Pattern)
```
streamlit_app/
├── main_app.py                    # Entry point - loads Company Dashboard
├── core/                          # Shared configuration & utilities (9 files)
│   ├── config.py                  # DisplayConfig class
│   ├── constants.py               # Domain-agnostic constants
│   ├── data_paths.py             # ⭐ Centralized path configuration (GOOD)
│   ├── data_loading.py           # Generic data loading with DuckDB
│   ├── formatters.py             # Data formatting utilities
│   ├── utils.py                  # Shared utilities (path resolution, CSS)
│   ├── display_*.py              # Display configuration helpers
│   └── models/data_models.py     # Data models
├── domains/                       # Domain-specific data loaders
│   ├── banking/data_loading_bank.py
│   ├── company/data_loading_company.py
│   ├── forecast/data_loading_forecast*.py
│   └── technical/data_loading_technical.py
├── pages/                         # Dashboard pages (7 files, 1,207-2,140 LOC each)
│   ├── company_dashboard_pyecharts.py    # 1,207 LOC ⚠️
│   ├── bank_dashboard.py                 # 2,140 LOC ⚠️
│   ├── securities_dashboard.py           # 1,500 LOC ⚠️
│   ├── technical_dashboard.py            # 1,847 LOC ⚠️
│   ├── forecast_dashboard.py             # 1,387 LOC ⚠️
│   ├── news_dashboard.py
│   └── valuation_sector_dashboard.py
├── features/                      # Business logic (4 files)
│   ├── growth.py
│   ├── scoring.py
│   ├── signals.py
│   └── valuation.py
├── components/                    # Reusable UI components (2 files)
│   ├── metrics_display.py
│   └── summary_row.py
├── charts/                        # Chart configurations
│   └── valuation_charts.py
├── layout/                        # Layout components
│   ├── sidebar.py
│   └── navigation.py
├── services/                      # External services (6 files)
│   ├── llm_service.py
│   ├── chat_manager.py
│   ├── query_builder.py
│   ├── commodity_loader.py
│   ├── news_loader.py
│   └── response_formatter.py
└── ai/                           # AI integration
    ├── prompts.py
    ├── schemas.py
    └── validators.py
```

### Strengths
- ✅ **Excellent centralized path management** (`data_paths.py`)
- ✅ **Clear separation of concerns** (domains, features, components, services)
- ✅ **Domain-driven design** for data loading
- ✅ **Modular formatters and utilities**

### Weaknesses
- ⚠️ **Very large page files** (1,200-2,140 LOC) - should be split into smaller components
- ⚠️ **Inconsistent use of Plotly vs PyEcharts** (some pages use Plotly, others PyEcharts)
- ⚠️ **Domain loaders are minimal** - `banking/data_loading_bank.py` is only 41 LOC with placeholder
- ⚠️ **Heavy duplication in page files** - similar patterns repeated across dashboards

---

## 3. DATA PROCESSING LAYER

### Organization
```
data_processor/
├── fundamental/                   # Entity-specific processors
│   ├── company/company_financial_calculator.py    # 810 LOC
│   ├── bank/bank_financial_calculator.py
│   ├── insurance/insurance_processor.py
│   └── security/security_processor.py
├── valuation/                     # Valuation calculators
│   ├── core/                      # 5 calculator classes
│   │   ├── historical_pe_calculator.py           # 579 LOC
│   │   ├── historical_pb_calculator.py           # 538 LOC
│   │   ├── historical_ev_ebitda_calculator.py    # 644 LOC
│   │   ├── vnindex_pe_calculator_optimized.py    # 456 LOC
│   │   └── bsc_universal_pe_calculator.py        # 494 LOC
│   ├── daily_full_valuation_pipeline.py          # ⭐ Orchestrator
│   ├── daily_update_all_valuations.py            # 1,240 LOC
│   ├── daily_update_vnindex_pe.py
│   └── sector_pe_calculator.py
├── technical/                     # Technical analysis
│   ├── technical/                 # ⚠️ Nested directory issue
│   │   ├── ohlcv/ohlcv_daily_updater.py         # 444 LOC
│   │   ├── commodity/commodity_price_updater.py  # 1,044 LOC
│   │   ├── macro/macro_data_fetcher.py          # 801 LOC
│   │   └── technical_indicators/
│   │       ├── technical_processor.py            # 897 LOC
│   │       ├── market_breadth_processor.py       # 850 LOC
│   │       ├── historical_technical_processor.py # 661 LOC
│   │       ├── stock_screener.py                 # 447 LOC
│   │       ├── ma_screening_processor.py
│   │       └── daily_updater.py
│   ├── daily_full_technical_pipeline.py          # ⭐ Orchestrator
│   ├── daily_ohlcv_update.py
│   └── daily_macro_commodity_update.py
├── news/                          # News aggregation
│   └── news_pipeline.py
├── Bsc_forecast/                  # BSC forecast integration
│   └── run_bsc_auto_update.py
└── core/                          # Shared utilities (11 files)
    ├── data_validator.py          # 507 LOC
    ├── consistency_checker.py     # 633 LOC
    ├── backup_logger.py
    ├── date_formatter.py
    ├── restore_missing_quarters*.py
    └── database_migrator.py
```

### Strengths
- ✅ **Well-organized orchestrator scripts** (daily_full_*_pipeline.py)
- ✅ **Clean separation by domain** (fundamental, valuation, technical)
- ✅ **Entity-specific processors** for different financial institution types
- ✅ **Shared core utilities** for validation, backup, and data quality

### Weaknesses
- ⚠️ **Nested `technical/technical/` directory** - confusing structure
- ⚠️ **backup/ subdirectories** with old versions of scripts
- ⚠️ **Very large calculator files** (644-1,240 LOC) - monolithic classes
- ⚠️ **Inconsistent class naming** (Calculator vs Processor vs Updater)

---

## 4. DATA STORAGE PATTERNS

### Data Flow Architecture
```
┌─────────────────────────────────────────────────────────────┐
│ DATA WAREHOUSE (Raw Data - Source of Truth)                 │
├─────────────────────────────────────────────────────────────┤
│ data_warehouse/raw/                                          │
│ ├── ohlcv/OHLCV_mktcap.parquet              (Price data)   │
│ ├── fundamental/processed/                   (4 entity types)│
│ │   ├── company_full.parquet                               │
│ │   ├── bank_full.parquet                                  │
│ │   ├── insurance_full.parquet                             │
│ │   └── security_full.parquet                              │
│ ├── commodity/commodity_prices.parquet                      │
│ ├── macro/                                                  │
│ │   ├── interest_rates.parquet                             │
│ │   └── exchange_rates.parquet                             │
│ └── news/news_raw_*.parquet                                │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    DATA PROCESSORS
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ CALCULATED RESULTS (Processed/Computed Data)                │
├─────────────────────────────────────────────────────────────┤
│ calculated_results/                                          │
│ ├── fundamental/          (Entity-specific metrics)          │
│ │   ├── company/company_financial_metrics.parquet          │
│ │   ├── bank/bank_financial_metrics.parquet                │
│ │   ├── insurance/insurance_financial_metrics.parquet      │
│ │   └── security/security_financial_metrics.parquet        │
│ ├── valuation/                                              │
│ │   ├── pe/pe_historical_all_symbols_final.parquet         │
│ │   ├── pb/pb_historical_all_symbols_final.parquet         │
│ │   ├── ev_ebitda/ev_ebitda_historical_*.parquet           │
│ │   ├── vnindex_pe_historical_final.parquet                │
│ │   └── sector_pe/sector_pe_historical_final.parquet       │
│ ├── technical/            (14 subdirectories)               │
│ │   ├── basic_data/, moving_averages/, ema/                │
│ │   ├── rsi/, macd/, bollinger_bands/                      │
│ │   ├── market_breadth/, signals/, screening/              │
│ │   └── sector_rotation/, sector_trading/, volatility/     │
│ ├── commodity/, macro/, news/                              │
│ └── forecast/bsc/                                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
                   STREAMLIT APP
```

### Storage Pattern Analysis

**STRENGTHS:**
- ✅ **Clear separation** between raw and calculated data
- ✅ **Consistent entity-based organization** (company, bank, insurance, security)
- ✅ **Parquet format** for efficient storage and querying
- ✅ **DuckDB integration** for fast queries without loading full datasets

**WEAKNESSES:**
- ⚠️ **No data versioning** - overwrites on each run
- ⚠️ **Archive folders** (e.g., `archive_q3_2025`) indicate manual backup process
- ⚠️ **Backup subdirectories** scattered throughout calculated_results/technical/
- ⚠️ **No schema validation** between raw and calculated results

---

## 5. CODE DUPLICATION

### Critical Duplication Issues

#### 1. `/copy` Directory - EXACT DUPLICATES
```
/copy/company_financial_calculator.py  ←→  /data_processor/fundamental/company/company_financial_calculator.py
/copy/bank_financial_calculator.py     ←→  /data_processor/fundamental/bank/bank_financial_calculator.py
/copy/insurance_processor.py           ←→  /data_processor/fundamental/insurance/insurance_processor.py
/copy/security_processor.py            ←→  /data_processor/fundamental/security/security_processor.py
```
**ACTION REQUIRED:** Delete entire `/copy` directory - it's outdated technical debt.

#### 2. Duplicated Backup Scripts
```
data_processor/technical/backup/daily_commodity_update.py
data_processor/technical/backup/daily_macro_update.py
```
Now superseded by `daily_macro_commodity_update.py`

#### 3. Similar Calculator Patterns
- `historical_pe_calculator.py` (579 LOC)
- `historical_pb_calculator.py` (538 LOC)
- `historical_ev_ebitda_calculator.py` (644 LOC)

**Analysis:** These share 70-80% identical code - could use a base class or shared utilities.

**Duplication Example:**
```python
# All three calculators have nearly identical methods:
- load_price_data()
- load_fundamental_data()
- merge_data()
- calculate_statistics()
- save_results()

# Only difference is the ratio calculation formula:
PE:        price / earnings
PB:        price / book_value
EV/EBITDA: enterprise_value / ebitda
```

#### 4. Page File Duplication
All dashboard pages repeat similar patterns:
- Symbol selection sidebar
- Date range filtering
- Data loading with DuckDB
- Chart rendering (Plotly/PyEcharts)
- Metric display tables

Should extract common patterns into reusable components.

---

## 6. DEPENDENCY PATTERNS

### Import Path Issues

**CRITICAL PROBLEM:** Excessive `sys.path` manipulation (40+ occurrences):
```python
# Found in nearly every file:
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
sys.path.insert(0, project_root)
sys.path.append(PROJECT_ROOT)
```

**FILES WITH SYS.PATH HACKS:**
- All streamlit_app/pages/*.py files
- All data_processor fundamental calculators
- All data_processor valuation calculators
- Most technical processors

**ROOT CAUSE:** Project not set up as a proper Python package.

**SOLUTION:** Add proper `__init__.py` files and use relative imports.

### Import Dependency Graph

```
streamlit_app/pages/
    ↓
streamlit_app/core/
    ├── config.py, constants.py
    ├── data_paths.py  ⭐ (centralized)
    ├── formatters.py
    └── utils.py
    ↓
streamlit_app/domains/
    ├── company/data_loading_company.py
    ├── banking/data_loading_bank.py
    └── technical/data_loading_technical.py
    ↓
streamlit_app/core/data_loading.py (DuckDB queries)

data_processor/*/
    ↓
data_processor/core/
    ├── date_formatter.py  ⚠️ (frequently imported)
    ├── data_validator.py
    └── backup_logger.py
```

**CIRCULAR DEPENDENCY RISK:** None found, but high coupling between pages and core modules.

---

## 7. MCP INTEGRATION POINTS

### Two MCP Server Implementations

#### 1. MongoDB MCP Server (`mcp_server/server.py`)
```python
Tools:
├── query_collection          # Query MongoDB collections
├── aggregate_collection      # Run aggregation pipelines
├── get_collection_schema     # Get schema info
├── list_collections          # List available collections
└── get_collection_stats      # Collection statistics

Collections:
├── company_metrics
├── bank_metrics
├── insurance_metrics
└── security_metrics
```

#### 2. Local Data MCP Server (`mcp_server/local_server.py`)
```python
Tools:
├── list_local_datasets       # List available datasets
├── get_dataset_schema        # Get schema + preview
├── preview_dataset           # Preview rows
└── query_dataset             # Query with filters

Datasets (8 configured):
├── ohlcv
├── fundamental_company/bank/insurance/security
├── commodity_prices
├── interest_rates
└── exchange_rates
```

### MCP Server Architecture
```
mcp_server/
├── server.py              # MongoDB-based MCP server
├── local_server.py        # File-based MCP server (no DB required)
├── config.py              # MongoDB connection config
├── local_data.py          # Dataset registry & query logic
├── handlers/
│   ├── query_handler.py   # Query request handling
│   └── result_formatter.py
├── tools/
│   ├── query_tool.py      # MongoDB query tools
│   ├── aggregate_tool.py  # Aggregation tools
│   └── schema_tool.py     # Schema inspection
└── resources/
    ├── collections.py     # Collection resources
    └── metrics.py         # Metrics resources
```

### Strengths
- ✅ **Two deployment options** (with/without MongoDB)
- ✅ **Clean separation** of concerns (tools, handlers, resources)
- ✅ **Hardcoded dataset registry** in `local_data.py` - easy to extend

### Weaknesses
- ⚠️ **Duplicated config.py** (both mcp_server/config.py and mongodb/config.py)
- ⚠️ **No automatic dataset discovery** - must manually update `DATASETS` dict
- ⚠️ **Limited to raw data** - doesn't expose calculated_results/

---

## 8. CONFIGURATION MANAGEMENT

### Current Configuration Files

```
config/
├── data_sources.json                      # Data source configurations
└── frequency_filtering_rules.json        # Filtering rules

streamlit_app/core/
├── config.py                              # DisplayConfig class
├── constants.py                           # Domain constants
└── data_paths.py                          # ⭐ Path configuration (GOOD)

mcp_server/config.py                       # MongoDB connection
mongodb/config.py                          # MongoDB connection (DUPLICATE)

.env (not tracked)                         # MongoDB credentials
```

### Configuration Pattern Issues

**FRAGMENTATION:**
1. **4 different config.py files** (streamlit_app, mcp_server, mongodb, display)
2. **No central settings.py** for project-wide configuration
3. **Hardcoded paths** scattered across files despite data_paths.py existing
4. **JSON configs** in /config but rarely used

**RECOMMENDATION:** Create unified `settings.py` with:
- Database connections
- File paths (leverage data_paths.py)
- Display settings
- Processing defaults

---

## 9. TECHNICAL DEBT & POOR ORGANIZATION

### Critical Issues (Priority Order)

#### 🔴 HIGH PRIORITY

1. **Delete `/copy` directory** - 100% duplicate code (4 files, ~60KB)
2. **Remove sys.path hacks** - Convert to proper Python package with __init__.py
3. **Split large page files** - Extract components from 1,200-2,140 LOC files
4. **Consolidate config files** - Merge duplicate MongoDB configs

#### 🟡 MEDIUM PRIORITY

5. **Refactor calculator base classes** - Extract common patterns from PE/PB/EV_EBITDA calculators
6. **Clean up `technical/technical/` nesting** - Flatten directory structure
7. **Remove backup/ directories** - Use git for version control, not manual backups
8. **Standardize Plotly vs PyEcharts** - Choose one charting library
9. **Move log files** - Create dedicated logs/ directory

#### 🟢 LOW PRIORITY

10. **Add __init__.py files** - Proper package structure (only 9 exist, need ~30)
11. **Consolidate requirements.txt** - Merge into root requirements.txt
12. **Add data versioning** - Track schema changes and migrations
13. **Expand domain loaders** - `banking/data_loading_bank.py` is placeholder

---

## 10. SPECIFIC FILES NEEDING REORGANIZATION

### Immediate Actions Required

#### DELETE
```
/copy/                                      # ENTIRE DIRECTORY - duplicates
data_processor/technical/backup/            # Old scripts
calculated_results/technical/backup/        # Old outputs
calculated_results/fundamental/archive_q3_2025/  # Manual archive
```

#### REFACTOR (Split into smaller files)
```
streamlit_app/pages/bank_dashboard.py                (2,140 LOC → 3-4 files)
streamlit_app/pages/technical_dashboard.py           (1,847 LOC → 3-4 files)
streamlit_app/pages/securities_dashboard.py          (1,500 LOC → 3-4 files)
streamlit_app/pages/forecast_dashboard.py            (1,387 LOC → 3-4 files)
streamlit_app/pages/company_dashboard_pyecharts.py   (1,207 LOC → 3-4 files)

data_processor/valuation/daily_update_all_valuations.py  (1,240 LOC → 2-3 files)
data_processor/technical/technical/commodity/commodity_price_updater.py  (1,044 LOC → 2 files)
```

#### FLATTEN
```
data_processor/technical/technical/  →  data_processor/technical/
  ├── ohlcv/
  ├── commodity/
  ├── macro/
  └── indicators/
```

#### CONSOLIDATE
```
mcp_server/config.py  }
mongodb/config.py     }  →  config/mongodb.py  (single source)
```

#### CREATE
```
stock_dashboard/
├── __init__.py
├── settings.py                    # Central configuration
└── requirements.txt               # Consolidated dependencies

streamlit_app/
├── __init__.py
├── components/
│   ├── __init__.py
│   ├── symbol_selector.py         # Extract from pages
│   ├── date_range_picker.py       # Extract from pages
│   └── metric_table.py            # Extract from pages

data_processor/
├── __init__.py
├── fundamental/
│   ├── __init__.py
│   └── base_calculator.py         # Base class for calculators
```

---

## 11. IMPORT/DEPENDENCY ISSUES SUMMARY

### Problems

1. **40+ files with `sys.path` manipulation** - Should use relative imports

2. **Inconsistent import styles:**
   - Some use `from streamlit_app.core import utils`
   - Others use `from .core import utils`
   - Many use absolute paths with sys.path hacks

3. **Circular import risk in pages:**
   - Pages import core modules
   - Core modules sometimes need page-specific logic
   - No clear boundary

4. **Missing package structure:**
   - Only 9 `__init__.py` files in entire codebase
   - Should have ~30-35 for proper package structure

5. **Hardcoded paths despite data_paths.py:**
   - Many files still use `os.path.join(__file__, '..', '..')`
   - Should use `data_paths.py` centralized configuration

---

## 12. PROPOSED CLEAN ARCHITECTURE

### New Directory Structure

```
stock_dashboard/
├── pyproject.toml              # Modern Python packaging (thay setup.py)
├── requirements.txt            # Consolidated dependencies
├── .env.example                # Template for environment variables
│
├── src/                        # ⭐ NEW: Source code package
│   └── stock_dashboard/
│       ├── __init__.py
│       ├── settings.py         # ⭐ Centralized config
│       │
│       ├── core/               # ⭐ Shared domain logic
│       │   ├── __init__.py
│       │   ├── models/         # Data models, schemas
│       │   ├── utils/          # Utilities
│       │   └── constants.py
│       │
│       ├── data/               # ⭐ Data access layer
│       │   ├── __init__.py
│       │   ├── warehouse/      # Raw data storage
│       │   ├── repositories/   # Data access patterns
│       │   └── schemas/        # Data schemas & validation
│       │
│       ├── processors/         # ⭐ Renamed from data_processor
│       │   ├── __init__.py
│       │   ├── base/           # Base classes
│       │   ├── fundamental/    # Entity processors
│       │   ├── technical/      # Technical indicators
│       │   ├── valuation/      # Valuation calculators
│       │   ├── news/
│       │   └── pipelines/      # Orchestrators
│       │
│       ├── web/                # ⭐ Renamed from streamlit_app
│       │   ├── __init__.py
│       │   ├── app.py          # Entry point
│       │   ├── core/           # Web-specific config
│       │   ├── pages/          # Dashboard pages (SMALLER)
│       │   ├── components/     # Reusable UI (EXPANDED)
│       │   ├── features/       # Business logic
│       │   └── services/       # External services
│       │
│       ├── api/                # ⭐ NEW: Future REST/GraphQL API
│       │   ├── __init__.py
│       │   ├── routes/
│       │   └── schemas/
│       │
│       ├── mcp/                # ⭐ MCP servers
│       │   ├── __init__.py
│       │   ├── mongodb_server.py
│       │   ├── local_server.py
│       │   ├── handlers/
│       │   └── tools/
│       │
│       └── reports/            # ⭐ NEW: Report generation
│           ├── __init__.py
│           ├── pdf/            # PDF reports
│           ├── excel/          # Excel exports
│           └── templates/      # Report templates
│
├── tests/                      # ⭐ Proper test structure
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── data/                       # ⭐ Simplified data storage
│   ├── raw/                    # Raw data (from data_warehouse/raw)
│   ├── processed/              # Calculated results
│   └── reports/                # Generated reports
│
├── config/                     # Configuration files
│   ├── database.yaml
│   ├── datasets.yaml           # MCP dataset registry
│   └── pipelines.yaml
│
├── scripts/                    # Utility scripts
│   └── migrations/             # Data migration scripts
│
├── logs/                       # ⭐ Centralized logging
│   ├── processors/
│   ├── web/
│   └── mcp/
│
└── docs/                       # Documentation
    ├── architecture/
    ├── api/
    └── user_guides/
```

### Key Architectural Changes

1. **`src/` layout**: Modern Python best practice, separates source from config/data
2. **Proper package structure**: All modules have `__init__.py`, enabling clean imports
3. **Centralized settings**: Single `settings.py` for all configuration
4. **Flattened technical**: No more `technical/technical/` nesting
5. **Expanded components**: More reusable UI components
6. **New modules**: `api/`, `reports/` for future extensibility
7. **Centralized logging**: All logs in one place
8. **Simplified data**: `data/` instead of `data_warehouse/` and `calculated_results/`

---

## 13. MIGRATION ROADMAP

### Phase 1: Foundation (Week 1-2)

#### Actions
```bash
# 1. Backup current state
git tag -a v1.0-before-refactor -m "Backup before major refactor"
git push origin v1.0-before-refactor

# 2. Delete technical debt
rm -rf copy/
rm -rf data_processor/technical/backup/
find calculated_results -type d -name "backup" -exec rm -rf {} +
rm -rf calculated_results/fundamental/archive_q3_2025/

# 3. Move log files
mkdir -p logs/{processors,web,mcp}
find . -maxdepth 1 -name "*.log" -exec mv {} logs/processors/ \;

# 4. Setup package structure
mkdir -p src/stock_dashboard
touch src/stock_dashboard/__init__.py

# 5. Create pyproject.toml
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "stock-dashboard"
version = "0.1.0"
description = "Vietnamese Stock Market Financial Analysis System"
requires-python = ">=3.13"
dependencies = [
    "streamlit>=1.30.0",
    "pandas>=2.0.0",
    "duckdb>=0.9.0",
    "pyarrow>=14.0.0",
    "plotly>=5.18.0",
]

[tool.setuptools.packages.find]
where = ["src"]
EOF

# 6. Create settings.py (see implementation section)

# 7. Consolidate requirements
cat streamlit_app/requirements.txt \
    data_processor/technical/technical/ohlcv/requirements_ohlcv.txt \
    | sort -u > requirements.txt
```

#### Deliverables
- ✅ Technical debt removed
- ✅ Package structure initialized
- ✅ Centralized configuration created
- ✅ Consolidated requirements.txt

### Phase 2: Restructure (Week 3-4)

#### Actions
```bash
# 1. Create new directory structure
mkdir -p src/stock_dashboard/{core,data,processors,web,mcp,reports,api}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p data/{raw,processed,reports}
mkdir -p config scripts/migrations docs/{architecture,api,user_guides}

# 2. Move and rename directories
mv streamlit_app src/stock_dashboard/web
mv data_processor src/stock_dashboard/processors
mv mcp_server src/stock_dashboard/mcp
mv mongodb src/stock_dashboard/data/repositories/mongodb

# 3. Move data directories
mv data_warehouse/raw data/raw
mv calculated_results data/processed

# 4. Add __init__.py throughout
find src/stock_dashboard -type d -exec touch {}/__init__.py \;

# 5. Install in editable mode
pip install -e .

# 6. Run import updater script (create this in Phase 1)
python scripts/update_imports.py
```

#### Deliverables
- ✅ New directory structure implemented
- ✅ All modules properly packaged
- ✅ Data directories reorganized
- ✅ Package installable with pip

### Phase 3: Refactor Code (Week 5-6)

#### Actions

1. **Extract BaseValuationCalculator**
   - Create `src/stock_dashboard/processors/base/valuation_calculator.py`
   - Refactor PE/PB/EV_EBITDA calculators to inherit from base
   - Reduce from 1,761 LOC to ~250 LOC

2. **Split Large Page Files**
   - `bank_dashboard.py` (2,140 LOC) → 4 files (~500 LOC each)
   - `technical_dashboard.py` (1,847 LOC) → 4 files (~460 LOC each)
   - `securities_dashboard.py` (1,500 LOC) → 3 files (~500 LOC each)
   - `forecast_dashboard.py` (1,387 LOC) → 3 files (~460 LOC each)
   - `company_dashboard_pyecharts.py` (1,207 LOC) → 3 files (~400 LOC each)

3. **Create Reusable Components**
   - `symbol_selector.py`
   - `date_range_picker.py`
   - `metric_table.py`
   - `chart_renderer.py`

4. **Flatten technical/ directory**
   - Move `technical/technical/` contents up one level
   - Reorganize into logical subdirectories

#### Deliverables
- ✅ Base classes extracted
- ✅ Large files split into manageable sizes
- ✅ Reusable components library created
- ✅ Technical directory cleaned up

### Phase 4: Add New Features (Week 7-8)

#### Actions

1. **Implement PDF Report Generation**
   - Create `src/stock_dashboard/reports/pdf/` module
   - Company report template
   - Sector analysis report template
   - Technical analysis report template

2. **Enhanced MCP Tools**
   - Add `generate_report` tool
   - Add `query_with_ai_context` tool
   - Add automatic dataset discovery
   - Expose calculated_results/ through MCP

3. **API Endpoints (Optional)**
   - REST API with FastAPI
   - GraphQL endpoint
   - Authentication middleware

4. **Automated Testing**
   - Unit tests for calculators
   - Integration tests for pipelines
   - E2E tests for web app

#### Deliverables
- ✅ PDF report generation working
- ✅ Enhanced MCP server with new tools
- ✅ Optional API layer
- ✅ Test coverage >60%

---

## 14. IMPLEMENTATION EXAMPLES

### 1. Centralized Settings (`settings.py`)

```python
"""Centralized configuration for entire project."""
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parents[2]
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    REPORTS_DIR: Path = DATA_DIR / "reports"

    # Database
    MONGODB_URI: Optional[str] = Field(default=None, env="MONGODB_URI")
    MONGODB_DATABASE: str = "stock_dashboard"

    # Processing
    DEFAULT_BATCH_SIZE: int = 1000
    MAX_WORKERS: int = 4

    # Web app
    STREAMLIT_PORT: int = 8501
    CACHE_TTL_SECONDS: int = 3600

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Report generation
    REPORT_TEMPLATES_DIR: Path = PROJECT_ROOT / "src" / "stock_dashboard" / "reports" / "templates"
    PDF_FONT: str = "Helvetica"
    EXCEL_ENGINE: str = "openpyxl"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()

# Usage in any module:
# from stock_dashboard.settings import settings
# print(settings.RAW_DATA_DIR)
```

### 2. Base Valuation Calculator

```python
"""Base class for valuation calculators."""
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
import duckdb
from stock_dashboard.settings import settings
from stock_dashboard.core.utils import setup_logger

class BaseValuationCalculator(ABC):
    """Abstract base class for PE/PB/EV_EBITDA calculators.

    Reduces code duplication by centralizing common logic.
    Subclasses only need to implement ratio-specific methods.
    """

    def __init__(self, metric_name: str):
        """Initialize calculator.

        Args:
            metric_name: Name of the metric (PE, PB, EV_EBITDA)
        """
        self.metric_name = metric_name
        self.logger = setup_logger(f"{self.__class__.__name__}")
        self.output_path = settings.PROCESSED_DATA_DIR / "valuation" / metric_name.lower()
        self.output_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def calculate_ratio(self, price: float, fundamental_value: float) -> float:
        """Calculate the specific ratio.

        Args:
            price: Stock price
            fundamental_value: Fundamental value (earnings, book value, EBITDA)

        Returns:
            Calculated ratio value
        """
        pass

    @abstractmethod
    def get_fundamental_column(self) -> str:
        """Return the column name for fundamental value.

        Returns:
            Column name (e.g., 'earnings_per_share', 'book_value_per_share')
        """
        pass

    def load_price_data(self) -> pd.DataFrame:
        """Load OHLCV data with DuckDB.

        Returns:
            DataFrame with columns: symbol, date, close_price, market_cap
        """
        query = """
            SELECT symbol, date, close_price, market_cap
            FROM read_parquet(?)
            WHERE date IS NOT NULL
            ORDER BY symbol, date
        """
        ohlcv_path = settings.RAW_DATA_DIR / "ohlcv" / "OHLCV_mktcap.parquet"
        self.logger.info(f"Loading price data from {ohlcv_path}")
        return duckdb.query(query, [str(ohlcv_path)]).df()

    def load_fundamental_data(self) -> pd.DataFrame:
        """Load fundamental data for all entity types.

        Returns:
            Combined DataFrame from company, bank, insurance, security
        """
        dfs = []
        for entity_type in ["company", "bank", "insurance", "security"]:
            path = settings.RAW_DATA_DIR / "fundamental" / "processed" / f"{entity_type}_full.parquet"
            if path.exists():
                self.logger.info(f"Loading {entity_type} data from {path}")
                df = pd.read_parquet(path)
                df['entity_type'] = entity_type
                dfs.append(df)
            else:
                self.logger.warning(f"File not found: {path}")

        if not dfs:
            raise FileNotFoundError("No fundamental data files found")

        return pd.concat(dfs, ignore_index=True)

    def merge_data(self, price_df: pd.DataFrame, fundamental_df: pd.DataFrame) -> pd.DataFrame:
        """Merge price and fundamental data.

        Args:
            price_df: DataFrame with price data
            fundamental_df: DataFrame with fundamental data

        Returns:
            Merged DataFrame
        """
        self.logger.info("Merging price and fundamental data")

        # Convert dates to same format
        price_df['date'] = pd.to_datetime(price_df['date'])
        fundamental_df['report_date'] = pd.to_datetime(fundamental_df['report_date'])

        # Merge on symbol and date
        merged = pd.merge_asof(
            price_df.sort_values('date'),
            fundamental_df.sort_values('report_date'),
            left_on='date',
            right_on='report_date',
            by='symbol',
            direction='backward'
        )

        self.logger.info(f"Merged {len(merged)} records")
        return merged

    def calculate(self) -> pd.DataFrame:
        """Main calculation workflow.

        Returns:
            DataFrame with calculated ratios
        """
        self.logger.info(f"Starting {self.metric_name} calculation...")

        # Load data
        price_df = self.load_price_data()
        fundamental_df = self.load_fundamental_data()

        # Merge
        merged_df = self.merge_data(price_df, fundamental_df)

        # Calculate ratio
        fundamental_col = self.get_fundamental_column()
        merged_df[self.metric_name.lower()] = merged_df.apply(
            lambda row: self.calculate_ratio(
                row['close_price'],
                row[fundamental_col]
            ),
            axis=1
        )

        # Filter invalid values
        valid_df = merged_df[merged_df[self.metric_name.lower()].notna()]
        self.logger.info(f"Calculated {len(valid_df)} valid ratios")

        # Save
        self.save_results(valid_df)
        return valid_df

    def save_results(self, df: pd.DataFrame) -> None:
        """Save calculation results.

        Args:
            df: DataFrame to save
        """
        output_file = self.output_path / f"{self.metric_name.lower()}_historical_all_symbols_final.parquet"
        df.to_parquet(output_file, index=False)
        self.logger.info(f"Saved {len(df)} records to {output_file}")


# Concrete implementations become tiny:

class PECalculator(BaseValuationCalculator):
    """PE Ratio calculator."""

    def __init__(self):
        super().__init__(metric_name="PE")

    def calculate_ratio(self, price: float, fundamental_value: float) -> float:
        return price / fundamental_value if fundamental_value > 0 else None

    def get_fundamental_column(self) -> str:
        return "earnings_per_share"


class PBCalculator(BaseValuationCalculator):
    """PB Ratio calculator."""

    def __init__(self):
        super().__init__(metric_name="PB")

    def calculate_ratio(self, price: float, fundamental_value: float) -> float:
        return price / fundamental_value if fundamental_value > 0 else None

    def get_fundamental_column(self) -> str:
        return "book_value_per_share"


class EVEBITDACalculator(BaseValuationCalculator):
    """EV/EBITDA Ratio calculator."""

    def __init__(self):
        super().__init__(metric_name="EV_EBITDA")

    def calculate_ratio(self, price: float, fundamental_value: float) -> float:
        # Note: For EV/EBITDA we need market cap + debt - cash
        # This is simplified; actual implementation needs more data
        return price / fundamental_value if fundamental_value > 0 else None

    def get_fundamental_column(self) -> str:
        return "ebitda"
```

**Result:** From 1,761 LOC (579+538+644) to ~200 LOC base + 50 LOC implementations = ~250 LOC total. **85% reduction!**

### 3. Reusable UI Components

```python
# src/stock_dashboard/web/components/symbol_selector.py
"""Reusable symbol selector component."""
import streamlit as st
from typing import List, Optional

def render_symbol_selector(
    entity_type: str,
    available_symbols: List[str],
    key: str,
    default: Optional[str] = None
) -> str:
    """Render symbol selector with consistent styling.

    Args:
        entity_type: Type of entity (company, bank, insurance, security)
        available_symbols: List of available symbols
        key: Unique key for Streamlit widget
        default: Default selected symbol

    Returns:
        Selected symbol
    """
    label_map = {
        "company": "Select Company",
        "bank": "Select Bank",
        "insurance": "Select Insurance Company",
        "security": "Select Securities Firm"
    }

    label = label_map.get(entity_type, "Select Symbol")

    index = 0
    if default and default in available_symbols:
        index = available_symbols.index(default)

    return st.selectbox(
        label,
        options=available_symbols,
        index=index,
        key=key,
        help=f"Choose a {entity_type} to analyze"
    )


# src/stock_dashboard/web/components/date_range_picker.py
"""Reusable date range picker component."""
import streamlit as st
import pandas as pd
from typing import Tuple

def render_date_range_picker(
    min_date: pd.Timestamp,
    max_date: pd.Timestamp,
    key: str,
    default_range: str = "1Y"
) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """Render date range picker with presets.

    Args:
        min_date: Minimum selectable date
        max_date: Maximum selectable date
        key: Unique key for Streamlit widgets
        default_range: Default range (1M, 3M, 6M, 1Y, YTD, All)

    Returns:
        Tuple of (start_date, end_date)
    """
    col1, col2, col3 = st.columns([2, 2, 3])

    with col3:
        preset = st.radio(
            "Quick Select",
            options=["1M", "3M", "6M", "1Y", "YTD", "All"],
            horizontal=True,
            key=f"{key}_preset"
        )

        # Calculate preset dates
        if preset == "1M":
            start = max_date - pd.DateOffset(months=1)
        elif preset == "3M":
            start = max_date - pd.DateOffset(months=3)
        elif preset == "6M":
            start = max_date - pd.DateOffset(months=6)
        elif preset == "1Y":
            start = max_date - pd.DateOffset(years=1)
        elif preset == "YTD":
            start = pd.Timestamp(max_date.year, 1, 1)
        else:  # All
            start = min_date

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=start,
            min_value=min_date,
            max_value=max_date,
            key=f"{key}_start"
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key=f"{key}_end"
        )

    return pd.Timestamp(start_date), pd.Timestamp(end_date)


# src/stock_dashboard/web/components/metric_table.py
"""Reusable financial metrics table component."""
import streamlit as st
import pandas as pd
from typing import Dict, List, Optional

def render_financial_metrics_table(
    data: pd.DataFrame,
    metrics_config: Dict[str, dict],
    title: str = "Financial Metrics",
    highlighted_metrics: Optional[List[str]] = None
) -> None:
    """Render financial metrics table with formatting.

    Args:
        data: DataFrame with financial data
        metrics_config: Configuration dict with format specs
            Example: {
                "revenue": {"label": "Revenue", "format": ",.0f", "unit": "VND"},
                "profit_margin": {"label": "Profit Margin", "format": ".2%"}
            }
        title: Table title
        highlighted_metrics: List of metric keys to highlight
    """
    st.subheader(title)

    # Build display dataframe
    display_data = []

    for metric_key, config in metrics_config.items():
        if metric_key not in data.columns:
            continue

        value = data[metric_key].iloc[-1]  # Latest value

        # Format value
        fmt = config.get("format", ".2f")
        if fmt.endswith("%"):
            formatted = f"{value:{fmt}}"
        else:
            formatted = f"{value:{fmt}}"

        # Add unit
        unit = config.get("unit", "")
        if unit:
            formatted = f"{formatted} {unit}"

        row = {
            "Metric": config["label"],
            "Value": formatted
        }

        # Add highlight
        if highlighted_metrics and metric_key in highlighted_metrics:
            row["Metric"] = f"⭐ {row['Metric']}"

        display_data.append(row)

    # Render table
    st.dataframe(
        pd.DataFrame(display_data),
        use_container_width=True,
        hide_index=True
    )
```

### 4. Enhanced MCP Server with Report Generation

```python
# src/stock_dashboard/mcp/enhanced_server.py
"""Enhanced MCP server with report generation capabilities."""
from mcp.server import Server
from mcp.types import TextContent, ImageContent
import mcp.types as types
from stock_dashboard.settings import settings
from stock_dashboard.reports.pdf import CompanyPDFReport
from stock_dashboard.reports.excel import CompanyExcelReport
import pandas as pd
import base64

mcp = Server("stock-dashboard-enhanced")

@mcp.tool()
async def generate_company_report(
    symbol: str,
    report_type: str = "quarterly",
    format: str = "pdf",
    include_charts: bool = True
) -> dict:
    """Generate comprehensive company financial report.

    Args:
        symbol: Stock symbol (e.g., VNM, VCB)
        report_type: Type of report (quarterly, annual, custom)
        format: Output format (pdf, excel)
        include_charts: Whether to include charts

    Returns:
        Dict with report path and metadata
    """
    from stock_dashboard.data.repositories import CompanyRepository
    from stock_dashboard.processors.valuation import PECalculator, PBCalculator
    from stock_dashboard.processors.technical import TechnicalProcessor

    # Load all relevant data
    repo = CompanyRepository()
    company_data = repo.get_company_metrics(symbol)

    # Load valuation data
    pe_calc = PECalculator()
    valuation_data = pe_calc.get_ratios_for_symbol(symbol)

    # Load technical indicators
    tech_proc = TechnicalProcessor()
    technical_data = tech_proc.get_indicators_for_symbol(symbol)

    # Generate report based on format
    if format == "pdf":
        generator = CompanyPDFReport(symbol)
        report_path = generator.generate(
            company_metrics=company_data,
            valuation_data=valuation_data,
            technical_signals=technical_data,
            report_type=report_type,
            include_charts=include_charts
        )
    elif format == "excel":
        generator = CompanyExcelReport(symbol)
        report_path = generator.generate(
            company_metrics=company_data,
            valuation_data=valuation_data,
            technical_signals=technical_data,
            report_type=report_type
        )
    else:
        raise ValueError(f"Unsupported format: {format}")

    return {
        "status": "success",
        "symbol": symbol,
        "report_path": str(report_path),
        "report_type": report_type,
        "format": format,
        "file_size_kb": report_path.stat().st_size / 1024
    }


@mcp.tool()
async def query_with_ai_context(
    query: str,
    symbols: list[str],
    timeframe: str = "1Y"
) -> dict:
    """Query financial data with AI-enhanced context and analysis.

    This tool uses LLM to understand query intent, fetches relevant data,
    and generates an AI-powered summary with insights.

    Args:
        query: Natural language query (e.g., "Compare profitability of VNM and VCB")
        symbols: List of stock symbols to analyze
        timeframe: Time period (1M, 3M, 6M, 1Y, 3Y, 5Y)

    Returns:
        Dict with data and AI-generated summary
    """
    from stock_dashboard.services.llm_service import LLMService
    from stock_dashboard.data.repositories import DataRepository

    # Parse query intent using LLM
    llm = LLMService()
    intent = llm.parse_query_intent(query)

    # Fetch relevant datasets based on intent
    repo = DataRepository()
    datasets = {}

    if "fundamental" in intent.data_types:
        datasets["fundamental"] = repo.get_fundamental_data(symbols, timeframe)

    if "valuation" in intent.data_types:
        datasets["valuation"] = repo.get_valuation_data(symbols, timeframe)

    if "technical" in intent.data_types:
        datasets["technical"] = repo.get_technical_data(symbols, timeframe)

    # Generate AI summary
    summary = llm.generate_analysis_summary(
        query=query,
        datasets=datasets,
        symbols=symbols
    )

    return {
        "query": query,
        "symbols": symbols,
        "timeframe": timeframe,
        "intent": intent.dict(),
        "data": {k: v.to_dict() for k, v in datasets.items()},
        "ai_summary": summary,
        "data_points": sum(len(df) for df in datasets.values())
    }


@mcp.tool()
async def compare_companies(
    symbols: list[str],
    metrics: list[str],
    periods: int = 4
) -> dict:
    """Compare financial metrics across multiple companies.

    Args:
        symbols: List of stock symbols to compare
        metrics: List of metrics to compare (revenue, net_profit, roe, etc.)
        periods: Number of historical periods to include

    Returns:
        Comparison data with rankings and insights
    """
    from stock_dashboard.data.repositories import CompanyRepository

    repo = CompanyRepository()
    comparison_data = {}

    for symbol in symbols:
        data = repo.get_company_metrics(symbol, periods=periods)
        comparison_data[symbol] = data[metrics]

    # Calculate rankings
    rankings = {}
    for metric in metrics:
        latest_values = {
            symbol: data[metric].iloc[-1]
            for symbol, data in comparison_data.items()
        }
        rankings[metric] = sorted(
            latest_values.items(),
            key=lambda x: x[1],
            reverse=True
        )

    return {
        "symbols": symbols,
        "metrics": metrics,
        "periods": periods,
        "data": {k: v.to_dict() for k, v in comparison_data.items()},
        "rankings": rankings
    }


@mcp.resource("datasets://financial")
async def list_available_datasets() -> list[types.Resource]:
    """List all available financial datasets."""
    from stock_dashboard.data.repositories import DatasetRegistry

    registry = DatasetRegistry()
    datasets = registry.list_all()

    resources = []
    for dataset in datasets:
        resources.append(types.Resource(
            uri=f"dataset://{dataset['name']}",
            name=dataset['name'],
            description=dataset['description'],
            mimeType="application/x-parquet"
        ))

    return resources
```

### 5. PDF Report Generator

```python
# src/stock_dashboard/reports/pdf/company_report.py
"""PDF report generator for company financial analysis."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib import colors
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from stock_dashboard.settings import settings

class CompanyPDFReport:
    """Generate comprehensive company PDF report."""

    def __init__(self, symbol: str):
        """Initialize report generator.

        Args:
            symbol: Stock symbol
        """
        self.symbol = symbol
        self.output_dir = settings.REPORTS_DIR / "company"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_path = self.output_dir / f"{symbol}_report.pdf"
        self.styles = getSampleStyleSheet()

        # Custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30
        ))

    def generate(
        self,
        company_metrics: pd.DataFrame,
        valuation_data: pd.DataFrame,
        technical_signals: pd.DataFrame,
        report_type: str = "quarterly",
        include_charts: bool = True
    ) -> Path:
        """Generate complete PDF report.

        Args:
            company_metrics: Company financial metrics
            valuation_data: Valuation ratios (PE, PB, etc.)
            technical_signals: Technical indicators
            report_type: Type of report (quarterly, annual)
            include_charts: Whether to include charts

        Returns:
            Path to generated PDF file
        """
        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        story = []

        # Cover page
        story.extend(self._create_cover_page())
        story.append(PageBreak())

        # Executive summary
        story.extend(self._create_executive_summary(company_metrics, valuation_data))
        story.append(Spacer(1, 0.5*cm))

        # Financial analysis
        story.extend(self._create_financial_section(company_metrics))
        story.append(PageBreak())

        # Valuation analysis
        story.extend(self._create_valuation_section(valuation_data))
        story.append(Spacer(1, 0.5*cm))

        # Technical analysis
        story.extend(self._create_technical_section(technical_signals))

        # Charts
        if include_charts:
            story.append(PageBreak())
            story.extend(self._create_charts(
                company_metrics, valuation_data, technical_signals
            ))

        # Build PDF
        doc.build(story)
        return self.output_path

    def _create_cover_page(self) -> list:
        """Create cover page."""
        elements = []

        # Title
        title = Paragraph(
            f"Financial Analysis Report<br/>{self.symbol}",
            self.styles['CustomTitle']
        )
        elements.append(Spacer(1, 5*cm))
        elements.append(title)

        # Subtitle
        from datetime import datetime
        subtitle = Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y')}",
            self.styles['Normal']
        )
        elements.append(Spacer(1, 1*cm))
        elements.append(subtitle)

        return elements

    def _create_executive_summary(
        self,
        company_metrics: pd.DataFrame,
        valuation_data: pd.DataFrame
    ) -> list:
        """Create executive summary section."""
        elements = []

        # Section title
        elements.append(Paragraph("Executive Summary", self.styles['Heading1']))
        elements.append(Spacer(1, 0.5*cm))

        # Key metrics table
        latest_metrics = company_metrics.iloc[-1]
        latest_valuation = valuation_data.iloc[-1]

        data = [
            ["Metric", "Value"],
            ["Revenue (VND B)", f"{latest_metrics['revenue']/1e9:,.1f}"],
            ["Net Profit (VND B)", f"{latest_metrics['net_profit']/1e9:,.1f}"],
            ["ROE", f"{latest_metrics['roe']:.2%}"],
            ["ROA", f"{latest_metrics['roa']:.2%}"],
            ["PE Ratio", f"{latest_valuation['pe']:.2f}"],
            ["PB Ratio", f"{latest_valuation['pb']:.2f}"],
        ]

        table = Table(data, colWidths=[8*cm, 6*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        return elements

    def _create_financial_section(self, company_metrics: pd.DataFrame) -> list:
        """Create financial analysis section."""
        elements = []

        elements.append(Paragraph("Financial Performance", self.styles['Heading1']))
        elements.append(Spacer(1, 0.5*cm))

        # Revenue and profit analysis
        elements.append(Paragraph("Revenue & Profitability", self.styles['Heading2']))

        # Calculate growth rates
        revenue_growth = company_metrics['revenue'].pct_change().iloc[-1]
        profit_growth = company_metrics['net_profit'].pct_change().iloc[-1]

        analysis_text = f"""
        <b>Revenue Growth:</b> {revenue_growth:.2%} QoQ<br/>
        <b>Profit Growth:</b> {profit_growth:.2%} QoQ<br/>
        <br/>
        The company has shown {'strong' if revenue_growth > 0.1 else 'moderate'}
        revenue growth in the latest quarter.
        """

        elements.append(Paragraph(analysis_text, self.styles['Normal']))

        return elements

    def _create_valuation_section(self, valuation_data: pd.DataFrame) -> list:
        """Create valuation analysis section."""
        elements = []

        elements.append(Paragraph("Valuation Analysis", self.styles['Heading1']))
        elements.append(Spacer(1, 0.5*cm))

        # PE ratio analysis
        current_pe = valuation_data['pe'].iloc[-1]
        avg_pe = valuation_data['pe'].mean()

        valuation_text = f"""
        <b>Current PE Ratio:</b> {current_pe:.2f}<br/>
        <b>Average PE (Historical):</b> {avg_pe:.2f}<br/>
        <br/>
        The stock is currently trading at a
        {'premium' if current_pe > avg_pe else 'discount'}
        to its historical average.
        """

        elements.append(Paragraph(valuation_text, self.styles['Normal']))

        return elements

    def _create_technical_section(self, technical_signals: pd.DataFrame) -> list:
        """Create technical analysis section."""
        elements = []

        elements.append(Paragraph("Technical Analysis", self.styles['Heading1']))
        elements.append(Spacer(1, 0.5*cm))

        # Technical indicators summary
        latest_signals = technical_signals.iloc[-1]

        technical_text = f"""
        <b>RSI:</b> {latest_signals.get('rsi', 0):.1f}<br/>
        <b>MACD Signal:</b> {latest_signals.get('macd_signal', 'N/A')}<br/>
        <b>Moving Average:</b> {latest_signals.get('ma_signal', 'N/A')}<br/>
        """

        elements.append(Paragraph(technical_text, self.styles['Normal']))

        return elements

    def _create_charts(
        self,
        company_metrics: pd.DataFrame,
        valuation_data: pd.DataFrame,
        technical_signals: pd.DataFrame
    ) -> list:
        """Create charts section."""
        elements = []

        elements.append(Paragraph("Charts & Visualizations", self.styles['Heading1']))
        elements.append(Spacer(1, 0.5*cm))

        # Revenue chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(company_metrics.index, company_metrics['revenue']/1e9)
        ax.set_title('Revenue Trend (VND Billion)')
        ax.set_xlabel('Quarter')
        ax.set_ylabel('Revenue (B VND)')
        ax.grid(True, alpha=0.3)

        # Save temp chart
        chart_path = self.output_dir / f"{self.symbol}_revenue_chart.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()

        # Add to report
        elements.append(Image(str(chart_path), width=15*cm, height=9*cm))

        return elements
```

---

## 15. NEXT STEPS

### Recommended Immediate Actions

1. **Review this document** with stakeholders
2. **Prioritize phases** based on business needs
3. **Allocate resources** for migration effort
4. **Set up project tracking** (GitHub Issues/Projects)
5. **Create backup branches** before starting

### Migration Checklist

```markdown
- [ ] Phase 1: Foundation
  - [ ] Create backup tag
  - [ ] Delete technical debt (copy/, backup/ dirs)
  - [ ] Setup pyproject.toml
  - [ ] Create settings.py
  - [ ] Consolidate requirements.txt

- [ ] Phase 2: Restructure
  - [ ] Create src/ layout
  - [ ] Move streamlit_app → src/stock_dashboard/web
  - [ ] Move data_processor → src/stock_dashboard/processors
  - [ ] Move mcp_server → src/stock_dashboard/mcp
  - [ ] Reorganize data directories
  - [ ] Add __init__.py files
  - [ ] Update all imports

- [ ] Phase 3: Refactor Code
  - [ ] Extract BaseValuationCalculator
  - [ ] Split bank_dashboard.py
  - [ ] Split technical_dashboard.py
  - [ ] Split securities_dashboard.py
  - [ ] Split forecast_dashboard.py
  - [ ] Split company_dashboard_pyecharts.py
  - [ ] Create reusable components
  - [ ] Flatten technical/ directory

- [ ] Phase 4: Add Features
  - [ ] Implement PDF report generation
  - [ ] Enhanced MCP tools
  - [ ] API endpoints (optional)
  - [ ] Automated testing
```

### Success Metrics

- **Code Reduction**: Target 30-40% LOC reduction through deduplication
- **File Size**: No files >800 LOC
- **Import Cleanup**: Zero `sys.path` manipulations
- **Test Coverage**: Minimum 60%
- **Documentation**: All modules documented
- **Performance**: No regression in dashboard load times

---

## 16. CONCLUSION

### Summary

The stock dashboard project has a **solid architectural foundation** with excellent data flow patterns and domain-driven design. However, it suffers from **significant technical debt** that will hinder long-term development:

- Duplicate code in `/copy` directory and calculator classes
- Very large page files (up to 2,140 LOC)
- 40+ files using `sys.path` hacks instead of proper imports
- Fragmented configuration across 4 different files

### Proposed Solution

The proposed clean architecture addresses these issues through:

1. **Modern Python packaging** with `pyproject.toml` and `src/` layout
2. **Proper package structure** enabling clean imports
3. **Centralized configuration** via `settings.py`
4. **Base classes** reducing calculator code by 85%
5. **Component extraction** reducing page sizes by 60-75%
6. **Enhanced MCP integration** with report generation capabilities
7. **Extensible design** ready for PDF reports, API endpoints, and future features

### Investment vs. Return

**Estimated Effort:**
- Phase 1 (Foundation): 1-2 weeks
- Phase 2 (Restructure): 2-3 weeks
- Phase 3 (Refactor): 2-3 weeks
- Phase 4 (Features): 2-3 weeks
- **Total: 7-11 weeks**

**Expected Returns:**
- 30-40% reduction in codebase size
- 50-70% faster onboarding for new developers
- Easier maintenance and debugging
- Foundation for long-term feature development
- Professional codebase ready for production deployment

### Final Recommendation

**Proceed with migration in phases.** Start with Phase 1 (Foundation) to eliminate technical debt, then evaluate progress before committing to full refactor. The investment will pay off in maintainability, extensibility, and developer productivity.

---

**Document Version**: 1.0
**Last Updated**: 2025-12-04
**Author**: Claude Code Analysis
**Status**: Draft for Review
