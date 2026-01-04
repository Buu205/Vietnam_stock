# v4.0.0 Architecture Guide

Complete architecture overview of the Vietnam Dashboard project.

---

## Project Overview

Vietnamese stock market financial data dashboard and analysis system. The project fetches, processes, and visualizes fundamental, technical, valuation, and forecast data for Vietnamese stocks through a Streamlit interface.

**Domain:**
- **457 tickers** across **4 entity types** (Company, Bank, Insurance, Security)
- **19 sectors** (Ngân hàng, Bất động sản, Công nghệ, etc.)
- **2,099 metrics** (Vietnamese → English mapping)

**Current Status:**
- ✅ Phase 0 complete (registries, calculators, transformers, schemas)
- ✅ Path migration complete (100% compliance)
- ✅ Trading logic centralization complete
- ⏳ Performance optimization in progress

---

## Configuration & Registry System

### Canonical Structure

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

### Key Changes (2025-12-10 Cleanup)

- ✅ Moved registries: `PROCESSORS/core/registries/` → `config/registries/`
- ✅ Removed duplicates: 3 schema files, 2 metric_registry.json copies
- ✅ Single source of truth: `DATA/metadata/metric_registry.json` (770 KB)
- ✅ Deleted legacy `SchemaRegistry` in `PROCESSORS/core/registries/`

---

## Data Architecture (v4.0.0)

### Directory Structure

```
DATA/
├── raw/                    # Input data (READ from here)
│   ├── ohlcv/              # OHLCV price data
│   ├── fundamental/csv/    # Raw financial statements
│   ├── commodity/          # Commodity prices
│   └── macro/              # Macroeconomic data
│
└── processed/              # Output data (WRITE to here)
    ├── fundamental/        # Calculated financial metrics
    │   ├── company/
    │   ├── bank/
    │   ├── insurance/
    │   └── security/
    ├── technical/          # Technical indicators
    │   ├── indicators/
    │   ├── alerts/
    │   └── market_breadth/
    ├── valuation/          # Valuation ratios
    │   ├── pe/
    │   ├── pb/
    │   ├── ev_ebitda/
    │   └── sector_pe/
    ├── commodity/          # Processed commodity data
    ├── macro/              # Processed macro data
    └── forecast/           # Analyst forecasts
        └── bsc/
```

---

## Component Architecture

### ✅ COMPLETED COMPONENTS (Foundation Layer)

| Component | Location | Status | Purpose |
|-----------|----------|--------|---------|
| **SectorRegistry** | `config/registries/sector_lookup.py` | ✅ | 457 tickers × 19 sectors × 4 entity types |
| **MetricRegistry** | `DATA/metadata/metric_registry.json` | ✅ | 2,099 metrics mapped (Vietnamese → English) |
| **UnifiedTickerMapper** | `PROCESSORS/core/shared/unified_mapper.py` | ✅ | Single API for ticker info, peers, validation |
| **Financial Calculators** | `PROCESSORS/fundamental/calculators/` | ✅ | 4 entity types (company, bank, insurance, security) |
| **Transformers Layer** | `PROCESSORS/transformers/financial/formulas.py` | ✅ | 30+ pure calculation functions |
| **Technical Indicators** | `PROCESSORS/technical/indicators/` | ✅ | MA, RSI, MACD, Bollinger, ATR, market breadth |
| **Valuation Calculators** | `PROCESSORS/valuation/calculators/` | ✅ | PE, PB, EV/EBITDA, VN-Index PE, Sector PE |
| **Data Models** | `WEBAPP/core/models/data_models.py` | ✅ | Pydantic models for all entities |
| **Schemas** | `config/schemas/data/` | ✅ | OHLCV, fundamental, technical, valuation schemas |

---

## Registry System Deep Dive

### MetricRegistry

**Purpose:** Vietnamese → English metric name mapping

**Location:** `config/registries/metric_lookup.py`

**Data Source:** `DATA/metadata/metric_registry.json` (770 KB)

**Usage:**
```python
from config.registries import MetricRegistry

metric_reg = MetricRegistry()

# Get metric info
metric = metric_reg.get_metric("CIS_62", "COMPANY")
# Returns: {"vietnamese_name": "Lợi nhuận sau thuế", ...}

# Search metrics
profit_metrics = metric_reg.search_metrics("profit", entity_type="COMPANY")

# Get calculated metric formula
roe_formula = metric_reg.get_calculated_metric_formula("roe")
```

**Key Features:**
- 2,099 metrics indexed
- Fast O(1) lookup by code
- Full-text search support
- Entity-type filtering

### SectorRegistry

**Purpose:** Ticker → Sector/Industry mapping

**Location:** `config/registries/sector_lookup.py`

**Data Source:** `DATA/metadata/sector_industry_registry.json`

**Usage:**
```python
from config.registries import SectorRegistry

sector_reg = SectorRegistry()

# Get ticker info
ticker_info = sector_reg.get_ticker("ACB")
# Returns: {"ticker": "ACB", "sector": "Ngân hàng", ...}

# Get peers
peers = sector_reg.get_peers("ACB", limit=10)
# Returns: ["VCB", "BID", "CTG", "MBB", ...]

# Get all tickers in sector
banking_tickers = sector_reg.get_tickers_by_sector("Ngân hàng")

# Validate ticker
if sector_reg.is_valid_ticker("XYZ"):
    process_ticker("XYZ")
```

**Key Features:**
- 457 tickers indexed
- 19 sectors, 4 entity types
- Peer discovery
- Validation support

### SchemaRegistry

**Purpose:** Schema management and data formatting

**Location:** `config/schema_registry.py`

**Usage:**
```python
from config.schema_registry import SchemaRegistry

schema_reg = SchemaRegistry()

# Get schema
ohlcv_schema = schema_reg.get_schema('ohlcv')
fundamental_schema = schema_reg.get_schema('fundamental', entity_type='company')

# Format values
formatted_price = schema_reg.format_price(25750.5)  # "25,750.50đ"
formatted_percent = schema_reg.format_percent(0.156)  # "15.60%"
```

---

## Processor Architecture

### Fundamental Processors

```
PROCESSORS/fundamental/
├── calculators/
│   ├── company_calculator.py       # Company financial metrics
│   ├── bank_calculator.py          # Bank-specific metrics (NIM, NPL, CAR)
│   ├── insurance_calculator.py     # Insurance metrics
│   └── security_calculator.py      # Brokerage metrics
└── transformers/
    └── financial/
        └── formulas.py             # Pure calculation functions
```

**Output:** `DATA/processed/fundamental/{entity_type}/{entity_type}_financial_metrics.parquet`

### Technical Processors

```
PROCESSORS/technical/
├── indicators/
│   ├── basic_indicators.py         # MA, RSI, MACD, Bollinger
│   ├── alert_detector.py           # Breakout, crossover, volume alerts
│   ├── market_breadth.py           # Advance/decline, McClellan
│   └── sector_breadth.py           # Sector-level breadth
└── ohlcv/
    └── ohlcv_fetcher.py            # OHLCV data fetcher
```

**Output:** `DATA/processed/technical/basic_data.parquet`

### Valuation Processors

```
PROCESSORS/valuation/calculators/
├── vnindex_pe_calculator_optimized.py      # VN-Index PE
├── vnindex_pb_calculator_optimized.py      # VN-Index PB
├── ev_ebitda_calculator_optimized.py       # EV/EBITDA
└── sector_pe_calculator.py                 # Sector PE
```

**Output:** `DATA/processed/valuation/{metric}/historical_{metric}.parquet`

---

## Web Application Architecture

### Streamlit Multi-Page App

```
WEBAPP/
├── main_app.py                     # Entry point, routing
├── core/
│   ├── models/
│   │   └── data_models.py          # Pydantic models
│   └── state/
│       ├── session_state.py        # Session state manager
│       └── market_state.py         # Market state cache
├── pages/
│   ├── company/                    # Company dashboard
│   ├── bank/                       # Bank dashboard
│   ├── sector/                     # Sector dashboard
│   ├── forecast/                   # Forecast dashboard
│   ├── technical/                  # Technical dashboard
│   └── fx_commodities/             # FX & Commodities dashboard
├── components/                     # Reusable UI components
└── services/                       # Data access layer
```

### Dashboard Pattern

Each dashboard follows this structure:
```
pages/{dashboard_name}/
├── {dashboard_name}_dashboard.py   # Main dashboard file
├── components/                     # UI components
│   ├── metrics_card.py
│   ├── chart.py
│   └── table.py
└── services/                       # Data services
    └── {dashboard_name}_service.py
```

---

## Data Flow

```
┌──────────────┐
│  Raw Data    │ (vnstock_data API, BSC Excel)
└──────┬───────┘
       │
       ├─> OHLCV Fetcher
       ├─> Fundamental Fetcher
       ├─> Forecast Fetcher
       │
       v
┌──────────────┐
│ DATA/raw/    │
└──────┬───────┘
       │
       ├─> Calculators (fundamental, valuation)
       ├─> Indicators (technical)
       ├─> Transformers (formulas)
       │
       v
┌──────────────┐
│DATA/processed│
└──────┬───────┘
       │
       ├─> Dashboard Services
       │
       v
┌──────────────┐
│  Streamlit   │ (User Interface)
│  Dashboard   │
└──────────────┘
```

---

## Important Notes

- **No virtual environment:** Project uses global Python 3.13 installation
- **Data files are expendable:** Files in `DATA/processed/` are generated artifacts
- **Single source of truth:** All lookups go through registries
- **Parquet format:** All processed data stored as Parquet (efficient, columnar)
- **Streamlit caching:** Use `@st.cache_data` and `@st.cache_resource` appropriately

---

## Next Steps (Roadmap)

1. **Performance Optimization:** Fix caching, lazy loading, TTL standardization
2. **UX Improvements:** Dark mode, responsive design, loading states
3. **Feature Enhancements:** Export functionality, comparison mode

**See active plan:** `plans/260104-2043-performance-optimization/plan.md`
