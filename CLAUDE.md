# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL RULES FOR AI ASSISTANTS

### Rule 1: Update Existing Documentation, Don't Create New Files

**ALWAYS update existing markdown files instead of creating new ones.**

When documenting:
- ✅ **DO**: Update existing `.md` files in `.cursor/plans/` or root directory
- ✅ **DO**: Append new sections to existing documentation
- ✅ **DO**: Use clear section headers (##, ###) for organization
- ❌ **DON'T**: Create new `.md` files unless explicitly requested
- ❌ **DON'T**: Duplicate information across multiple files
- ❌ **DON'T**: Create "part 1", "part 2" files - use sections instead

**Primary Documentation Locations:**
- `.cursor/plans/*.md` - Active development plans (update these!)
- `CLAUDE.md` - This file (project instructions)
- `README.md` - User-facing documentation
- `docs/archive/` - Historical documentation (read-only)

**Example:**
```python
# ❌ WRONG: Creating new file
write_file("NEW_FEATURE_PLAN_PART2.md", content)

# ✅ CORRECT: Update existing plan
append_to_file(".cursor/plans/main_plan.md", "## New Feature\n\n" + content)
```

### Rule 2: Check for Existing Plans Before Creating

Before creating any documentation:
1. Search for existing plan files: `find .cursor/plans -name "*.md"`
2. If similar plan exists, update it
3. If creating new plan is necessary, consolidate related content first

---

## Project Overview

Vietnamese stock market financial data dashboard and analysis system. The project fetches, processes, and visualizes fundamental, technical, valuation, and forecast data for Vietnamese stocks through a Streamlit interface.

**Primary development location:** `/Users/buuphan/Dev/Vietnam_dashboard`

**Current Status:**
- ✅ Phase 0 complete (registries, calculators, transformers, schemas) - 40%
- 🚨 Phase 0.5 **CRITICAL** - Path Migration needed (95% files using wrong paths)
- ⏳ Phase 1 pending - FA+TA Sector Analysis orchestration layer
- 📋 Active Plan: `.cursor/plans/fa+ta_sector_analysis_-_complete_architecture_refactor_b2d5c14f.plan.md`

---

## Development Setup

### Python Environment

- **Python Version:** 3.13 (system Python)
- **Python Binary:** `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` or `python3`
- **Key Dependency:** `vnstock_data` installed globally

### Installing Dependencies

```bash
# Core Streamlit app dependencies
pip install -r WEBAPP/requirements.txt

# OHLCV data pipeline dependencies (if working with technical data)
pip install -r PROCESSORS/technical/ohlcv/requirements_ohlcv.txt
```

### Running the Application

```bash
# Start the Streamlit dashboard (default loads Company Dashboard)
streamlit run WEBAPP/main_app.py
```

---

## 🚨 CRITICAL: v4.0.0 Path Migration Status

**BLOCKING ISSUE:** Only **4.7% (2/43 files)** follow canonical architecture!

### Canonical v4.0.0 Paths (TARGET)

```
DATA/
├── raw/                    # Input data (READ from here)
│   ├── ohlcv/
│   ├── fundamental/csv/
│   ├── commodity/
│   └── macro/
│
└── processed/              # Output data (WRITE to here)
    ├── fundamental/
    │   ├── company/
    │   ├── bank/
    │   ├── insurance/
    │   └── security/
    ├── technical/
    ├── valuation/
    │   ├── pe/
    │   ├── pb/
    │   ├── ev_ebitda/
    │   └── sector_pe/
    ├── commodity/
    ├── macro/
    └── forecast/bsc/
```

### Current (WRONG) Paths - Need Migration

❌ **35 files (81.4%)** still use old paths:
- `calculated_results/` → Should be `DATA/processed/`
- `data_warehouse/raw/` → Should be `DATA/raw/`
- `DATA/refined/` → Should be `DATA/processed/`

**Files requiring updates:**
- PROCESSORS/valuation/calculators/* (9 files)
- PROCESSORS/technical/indicators/* (6 files)
- PROCESSORS/pipelines/* (1 file)
- PROCESSORS/forecast/* (1 file)
- PROCESSORS/technical/macro/* (1 file)
- All input readers (15+ files)

**See Section 1.5 in plan for complete migration strategy.**

---

## Configuration & Registry System (config/)

**CANONICAL STRUCTURE (Updated 2025-12-10):**

```
config/
├── registries/                    # ✅ Registry lookup classes (Python)
│   ├── __init__.py               # Exports MetricRegistry, SectorRegistry
│   ├── metric_lookup.py          # MetricRegistry class (fast metric lookup)
│   ├── sector_lookup.py          # SectorRegistry class (ticker/sector mapping)
│   └── builders/                 # Builder scripts
│       ├── build_metric_registry.py    # BSC Excel → metric_registry.json
│       └── build_sector_registry.py    # Metadata → sector_industry_registry.json
│
├── schema_registry.py            # ✅ SchemaRegistry singleton (master class)
├── schema_registry/              # ✅ Organized schema definitions (JSON)
│   ├── core/                     # Core schemas
│   │   ├── types.json
│   │   ├── entities.json
│   │   └── mappings.json
│   ├── domain/                   # Domain-specific schemas
│   │   ├── fundamental/
│   │   ├── technical/
│   │   ├── valuation/
│   │   └── unified/
│   └── display/                  # UI schemas
│       ├── charts.json
│       ├── tables.json
│       └── dashboards.json
│
├── metadata_registry/            # ✅ Metadata & lookup data (JSON)
│   ├── metrics/
│   ├── sectors/
│   ├── tickers/
│   └── config/
│
├── business_logic/               # ✅ Business rules & configs (JSON)
│   ├── analysis/
│   ├── decisions/
│   └── alerts/
│
└── schemas/                      # ⚠️ LEGACY (backward compatibility)
    ├── master_schema.json
    └── data/
        ├── fundamental_calculated_schema.json
        ├── technical_calculated_schema.json
        └── ...
```

**Key Changes (2025-12-10 Cleanup):**
- ✅ Moved registries: `PROCESSORS/core/registries/` → `config/registries/`
- ✅ Removed duplicates: 3 schema files, 2 metric_registry.json copies
- ✅ Single source of truth: `DATA/metadata/metric_registry.json` (770 KB)
- ✅ Deleted legacy `SchemaRegistry` in `PROCESSORS/core/registries/`

**Import Pattern:**
```python
# ✅ CORRECT (canonical)
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry

# ❌ DEPRECATED (will fail)
from PROCESSORS.core.registries.metric_lookup import MetricRegistry
from PROCESSORS.core.registries.schema_registry import SchemaRegistry
```

---

## Architecture & Data Flow

### v4.0.0 Canonical Architecture

**Current Implementation:** 40% complete

#### ✅ **COMPLETED COMPONENTS** (Foundation Layer)

| Component | Location | Status | Purpose |
|-----------|----------|--------|---------|
| **SectorRegistry** | `PROCESSORS/core/registries/sector_lookup.py` | ✅ | 457 tickers × 19 sectors × 4 entity types |
| **MetricRegistry** | `DATA/metadata/metric_registry.json` | ✅ | 2,099 metrics mapped (Vietnamese → English) |
| **UnifiedTickerMapper** | `PROCESSORS/core/shared/unified_mapper.py` | ✅ | Single API for ticker info, peers, validation |
| **Financial Calculators** | `PROCESSORS/fundamental/calculators/` | ✅ | 4 entity types (company, bank, insurance, security) |
| **Transformers Layer** | `PROCESSORS/transformers/financial/formulas.py` | ✅ | 30+ pure calculation functions |
| **Technical Indicators** | `PROCESSORS/technical/indicators/` | ✅ | MA, RSI, MACD, Bollinger, ATR, market breadth |
| **Valuation Calculators** | `PROCESSORS/valuation/calculators/` | ✅ | PE, PB, EV/EBITDA, VN-Index PE, Sector PE |
| **Data Models** | `WEBAPP/core/models/data_models.py` | ✅ | Pydantic models for all entities |
| **Schemas** | `config/schemas/data/` | ✅ | OHLCV, fundamental, technical, valuation schemas |

#### ❌ **MISSING COMPONENTS** (Orchestration Layer)

| Component | Target Location | Status | Purpose |
|-----------|----------------|--------|---------|
| **SectorAnalyzer** | `PROCESSORS/sector_analysis/sector_analyzer.py` | ❌ | Main orchestrator for FA+TA analysis |
| **FADataAggregator** | `PROCESSORS/sector_analysis/fa_aggregator.py` | ❌ | Aggregate fundamental metrics by sector |
| **TADataAggregator** | `PROCESSORS/sector_analysis/ta_aggregator.py` | ❌ | Aggregate technical indicators by sector |
| **FATACombiner** | `PROCESSORS/sector_analysis/fa_ta_combiner.py` | ❌ | Merge FA+TA scores with weights |
| **SignalGenerator** | `PROCESSORS/sector_analysis/signal_generator.py` | ❌ | Generate Buy/Sell/Hold signals |
| **ConfigManager** | `config/sector_analysis/config_manager.py` | ❌ | Manage FA/TA weights and preferences |
| **Sector Dashboard** | `WEBAPP/pages/sector_analysis_dashboard.py` | ❌ | Unified FA+TA sector analysis UI |
| **Sector Service** | `WEBAPP/services/sector_service.py` | ❌ | Single API for sector data access |

---

## Commands for Data Processing

### Daily Update Pipelines

```bash
# Update all valuation metrics (PE/PB/EV_EBITDA, VN-Index PE, sector PE)
python3 PROCESSORS/valuation/daily_full_valuation_pipeline.py

# Update OHLCV data
python3 PROCESSORS/technical/daily_ohlcv_update.py

# Update macro & commodity data
python3 PROCESSORS/technical/daily_macro_commodity_update.py

# Update news data
python3 PROCESSORS/news/news_pipeline.py

# Update BSC forecast data
python3 PROCESSORS/Bsc_forecast/run_bsc_auto_update.py
```

### Fundamental Data Processing

```bash
# Process company financial data
python3 PROCESSORS/fundamental/calculators/company_calculator.py

# Process bank financial data
python3 PROCESSORS/fundamental/calculators/bank_calculator.py

# Process insurance financial data
python3 PROCESSORS/fundamental/calculators/insurance_calculator.py

# Process security/brokerage financial data
python3 PROCESSORS/fundamental/calculators/security_calculator.py
```

### Registry & Mapping Tools

```bash
# Build metric registry from BSC Excel templates
python3 config/registries/builders/build_metric_registry.py

# Build sector/industry registry from ticker metadata
python3 config/registries/builders/build_sector_registry.py

# Test unified ticker mapper integration
python3 PROCESSORS/core/test_unified_mapper.py
```

---

## Key Technical Patterns

### 1. ALWAYS Use Registries (CRITICAL)

**When building new features, ALWAYS use the registry system:**

```python
# Import from canonical locations (as of 2025-12-10)
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry

# Metric lookup
metric_reg = MetricRegistry()
metric = metric_reg.get_metric("CIS_62", "COMPANY")
roe_formula = metric_reg.get_calculated_metric_formula("roe")

# Sector/ticker lookup
sector_reg = SectorRegistry()
ticker_info = sector_reg.get_ticker("ACB")
peers = sector_reg.get_peers("ACB")  # Returns other banking tickers

# Schema access
schema_reg = SchemaRegistry()
ohlcv_schema = schema_reg.get_schema('ohlcv')
formatted_price = schema_reg.format_price(25750.5)  # "25,750.50đ"
```

### 2. Use Existing Calculators (Don't Duplicate)

```python
# ✅ CORRECT: Load existing calculated results
import pandas as pd

company_metrics = pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")
bank_metrics = pd.read_parquet("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")
technical_data = pd.read_parquet("DATA/processed/technical/basic_data.parquet")
```

### 3. Use Transformer Functions (Pure Functions)

```python
from PROCESSORS.transformers.financial import roe, gross_margin, yoy_growth

# Calculate metrics using pure functions
sector_avg_roe = roe(total_net_income, total_equity)
sector_growth = yoy_growth(current_revenue, previous_revenue)
```

---

## Valuation Calculation Formulas

### PE Ratio (Reference for all metrics)

**File:** `PROCESSORS/valuation/calculators/vnindex_pe_calculator_optimized.py`

```python
# VN-Index PE = Total Market Cap (billions VND) / Total TTM Earnings (billions VND)
total_market_cap = sum(market_cap) / 1e9  # Convert to billions
total_ttm_earnings = sum(ttm_earning_billion_vnd)
pe_ratio = total_market_cap / total_ttm_earnings

# Validation
valid_data = data[
    (data['market_cap'] > 0) &
    (data['ttm_earning_billion_vnd'].notna()) &
    (data['ttm_earning_billion_vnd'] > 0)
]

# Symbol filtering (exclude VIC, VHM, VPB, etc.)
all_symbols = calc.symbols_list
exclude = ['VIC', 'VHM', 'VPB']
filtered = [s for s in all_symbols if s not in exclude]
result = calc.calculate_vnindex_pe(date, symbols=filtered)
```

**Similar formulas:** PB Ratio, EV/EBITDA, Sector PE (see plan Section 1.4)

---

## Code Conventions

### File & Module Naming
- Files/modules: `snake_case`
- Classes: `CamelCase`
- Functions/variables: `snake_case`
- DataFrame variables: descriptive with `_df` suffix (e.g., `price_df`, `pe_ratio_df`)

### Path Resolution (CRITICAL)

**ALWAYS use canonical v4.0.0 paths:**

```python
# ✅ CORRECT:
input_path = Path("DATA/raw/ohlcv/OHLCV_mktcap.parquet")
output_path = Path("DATA/processed/valuation/pe/pe_historical.parquet")

# ❌ WRONG (deprecated):
input_path = "data_warehouse/raw/ohlcv/OHLCV_mktcap.parquet"
output_path = "calculated_results/valuation/pe/pe_historical.parquet"
```

**Use centralized paths:**
```python
from PROCESSORS.core.config.paths import get_data_path

input_path = get_data_path("raw", "ohlcv", "OHLCV_mktcap.parquet")
output_path = get_data_path("processed", "valuation", "pe", "pe_historical.parquet")
```

---

## Active Development Plan

**Primary Plan:** `.cursor/plans/fa+ta_sector_analysis_-_complete_architecture_refactor_b2d5c14f.plan.md`

**Current Phase:** Phase 0.5 - Path Migration (BLOCKING)

**Next Steps:**
1. **Phase 0.5:** Fix 35 files using wrong paths (3-5 days)
2. **Phase 1:** Build FA/TA orchestration layer (2 weeks)
3. **Phase 2:** Configuration system (1 week)
4. **Phase 3:** Unified sector dashboard (2 weeks)

**See plan file for complete roadmap.**

---

## Important Notes

- **No virtual environment:** Project uses global Python 3.13 installation
- **Data files are expendable:** Files in `DATA/processed/` are generated artifacts
- **MongoDB credentials:** Store in `.env` file (never commit)
- **Streamlit caching:** App uses Redis for caching
- **BSC forecast:** Requires Excel file `PROCESSORS/Bsc_forecast/BSC Master File Equity Pro.xlsm`

---

## Documentation Rules (RECAP)

1. ✅ **UPDATE** existing `.md` files in `.cursor/plans/`
2. ✅ **APPEND** new sections to existing documentation
3. ✅ **CONSOLIDATE** related content into single files
4. ❌ **DON'T** create new `.md` files without checking existing ones
5. ❌ **DON'T** duplicate information across files
6. ❌ **DON'T** create "part 1", "part 2" files

**When in doubt, update the active plan file.**
