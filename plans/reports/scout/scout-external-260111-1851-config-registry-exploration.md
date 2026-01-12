# Config & Registry System Exploration Report
**Date:** 2026-01-11  
**Agent:** scout-external (a8610f2)  
**Scope:** Configuration & Registry System  

## Executive Summary

The `config/` directory (1.6MB, 37 JSON files) serves as the **single source of truth** for all metadata, schemas, and business logic in the Vietnam Dashboard. It implements a comprehensive registry system with three core registries (MetricRegistry, SectorRegistry, SchemaRegistry) plus extensive configuration for data mapping, schemas, and business logic.

**Key Achievement:** v4.0.0 unit standardization with clean separation between storage (raw VND, decimals) and display formatting layers.

---

## Directory Structure

```
config/                          # 1.6MB total
├── registries/                  # Python lookup classes
│   ├── __init__.py             # Exports: MetricRegistry, SectorRegistry
│   ├── metric_lookup.py        # 2,099 metrics from BSC database
│   ├── sector_lookup.py        # 457 tickers × 19 sectors mapping
│   └── builders/               # Registry builder scripts
│
├── schema_registry/            # Data structure definitions (JSON schemas)
│   ├── core/                   # Base types & entities
│   │   ├── types.json         # Data types (price, volume, percentage)
│   │   ├── entities.json      # Entity types (COMPANY, BANK, INSURANCE, SECURITY)
│   │   └── mappings.json      # Field mappings
│   ├── domain/                 # Domain-specific schemas
│   │   ├── fundamental/       # Fundamental analysis schemas
│   │   ├── technical/         # Technical indicators
│   │   ├── valuation/         # Valuation models
│   │   └── unified/           # Sector analysis
│   └── display/               # UI/UX configs for Streamlit
│       ├── charts.json        # Chart configurations
│       ├── tables.json        # Table layouts
│       └── dashboards.json    # Dashboard specs
│
├── metadata/                   # Core data assets (large JSON files)
│   ├── metric_registry.json            # 770 KB - 2,099 metrics (CANONICAL)
│   ├── formula_registry.json           # Calculated metric formulas
│   ├── ticker_details.json             # Ticker metadata
│   └── master_symbols.json             # Symbol reference
│
├── data_mapping/              # Clean Architecture registry
│   ├── entities.py            # DataSource, PipelineOutput, ServiceBinding
│   ├── registry.py            # DataMappingRegistry singleton
│   ├── resolver.py            # PathResolver, DependencyResolver
│   ├── validator.py           # SchemaValidator, HealthChecker
│   └── configs/               # YAML configuration files
│       ├── data_sources.yaml  # 57 data sources
│       ├── services.yaml      # Service → data source mapping
│       ├── pipelines.yaml     # Pipeline outputs
│       └── dashboards.yaml    # Dashboard configurations
│
├── business_logic/            # Analysis & decision rules
│   ├── analysis/              # Analysis configurations
│   ├── decisions/             # Decision engine rules
│   └── alerts/                # Alert system
│
├── sector_analysis/           # Sector analysis configuration
│   └── config_manager.py      # FA/TA weights management
│
├── schema_registry.py         # SchemaRegistry class (formatting utilities)
├── unit_standards.json        # v4.0.0 unit standardization rules
└── README.md                  # Comprehensive documentation (1000 lines)
```

---

## Core Registries

### 1. MetricRegistry
**Location:** `config/registries/metric_lookup.py`  
**Data:** `config/metadata/metric_registry.json` (770 KB)

**Purpose:** Fast lookup utility for 2,099+ financial metrics from BSC database

**Features:**
- Get metric by code (CIS_62, BBS_100, etc.)
- Search metrics by Vietnamese/English name
- Get calculated metric formulas (ROE, gross_margin, etc.)
- Validate metric dependencies
- Support 4 entity types: COMPANY, BANK, INSURANCE, SECURITY

**Key Methods:**
```python
from config.registries import MetricRegistry

registry = MetricRegistry()

# Get specific metric
metric = registry.get_metric("CIS_62", "COMPANY")
# Returns: {'code': 'CIS_62', 'name_vi': 'Lợi nhuận sau thuế...', ...}

# Search by name
results = registry.search_by_name("lợi nhuận")

# Get calculated metric formula
roe_formula = registry.get_calculated_metric_formula("roe")
# Returns formula and dependencies

# Validate dependencies
validation = registry.validate_dependencies("roe", available_codes, "COMPANY")
```

**Data Structure:**
```json
{
  "version": "1.0",
  "entity_types": {
    "COMPANY": {
      "income_statement": {"CIS_10": {...}, "CIS_62": {...}},
      "balance_sheet": {"CBS_270": {...}, "CBS_400": {...}}
    }
  },
  "calculated_metrics": {
    "roe": {
      "formula": "net_income / avg_equity * 100",
      "dependencies": {"COMPANY": ["CIS_62", "CBS_270"]}
    }
  }
}
```

---

### 2. SectorRegistry
**Location:** `config/registries/sector_lookup.py`  
**Data:** `config/metadata/ticker_details.json`

**Purpose:** Ticker → Entity Type + Sector mapping (457 tickers × 19 sectors)

**Features:**
- Map ticker → entity type (COMPANY/BANK/SECURITY)
- Map ticker → sector (19 sectors)
- Find peer companies (same sector)
- Validate ticker existence
- Get calculator class for ticker

**Key Methods:**
```python
from config.registries import SectorRegistry

registry = SectorRegistry()

# Get ticker info
info = registry.get_ticker("ACB")
# Returns: {'entity_type': 'BANK', 'sector': 'Ngân hàng', ...}

# Get peers
peers = registry.get_peers("ACB")
# Returns: ['VCB', 'CTG', 'BID', 'TCB', ...]

# Get all tickers in sector
banks = registry.get_tickers_by_sector("Ngân hàng")

# Validate ticker
is_valid = registry.is_valid_ticker("ACB")
```

**Coverage:**
- 457 tickers total
- 390 companies, 24 banks, 37 securities, 6 insurance
- 19 sectors (Banking, Real Estate, Technology, etc.)

---

### 3. SchemaRegistry
**Location:** `config/schema_registry.py`  
**Status:** Singleton pattern

**Purpose:** Central schema management with formatting utilities

**Features:**
- Formatting methods (price, volume, percentages, market cap, ratios)
- Color schemes (positive/negative/neutral changes)
- Chart configurations
- Schema definitions

**Key Methods:**
```python
from config.schema_registry import SchemaRegistry

registry = SchemaRegistry()

# Formatting
price_str = registry.format_price(25750.5)       # "25,750.50đ"
volume_str = registry.format_volume(1_500_000)   # "1.5M"
pct_str = registry.format_percentage(0.0523)     # "5.23%"
mcap_str = registry.format_market_cap(12.2e12)   # "12,241.7B"

# Get schema
ohlcv_schema = registry.get_schema('ohlcv')

# Colors
green = registry.get_color('positive_change')     # "#00C853"
red = registry.get_color('negative_change')       # "#D50000"
```

---

## Unit Standards (v4.0.0)

**Location:** `config/unit_standards.json`

**Core Principles:**
1. **Storage Layer:** Store RAW values (VND, decimal ratios) - NO conversion
2. **Display Layer:** UI/Streamlit handles all formatting
3. **Precision:** Maximize by storing full values
4. **Consistency:** All entity types follow same standard

**Standardization Table:**

| Metric Type | Storage Unit | Example Storage | Display | Example Display |
|-------------|--------------|-----------------|---------|-----------------|
| **Absolute Values**<br>(Revenue, Assets) | VND | `2,500,123,000` | value/1e9 + " Tỷ" | `2.5 Tỷ VND` |
| **Ratios/Margins**<br>(ROE, NIM) | Decimal (0-1) | `0.1523` | value*100 + "%" | `15.23%` |
| **Per Share**<br>(EPS, BVPS) | VND/share | `15,234` | #,##0 + " VND/cp" | `15,234 VND/cp` |
| **Multiples**<br>(P/E, Leverage) | Times (x) | `15.23` | "0.00x" | `15.23x` |

**Applies To:**
- Absolute: revenue, profit, assets, equity, debt, cash flows
- Ratios: ROE, ROA, margins, NIM, CIR, CASA ratio, NPL ratio
- Per Share: EPS, BVPS, DPS
- Multiples: PE, PB, EV/EBITDA, debt/equity, leverage

---

## Data Mapping System

**Location:** `config/data_mapping/`  
**Architecture:** Clean Architecture registry

**Components:**

### 1. Entities (`entities.py`)
- `DataSource`: File path, schema, entity type, category
- `PipelineOutput`: Script → output files mapping
- `DashboardConfig`: Dashboard data sources
- `ServiceBinding`: Service class → data sources
- Enums: EntityType, UpdateFrequency, DataCategory

### 2. Registry (`registry.py`)
```python
from config.data_mapping import get_registry, get_data_path

# Get path by source name
path = get_data_path("bank_metrics")
# Returns: Path("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")

# Get registry for advanced lookups
registry = get_registry()
sources = registry.get_sources_for_service("BankService")
```

### 3. Resolver (`resolver.py`)
- `PathResolver`: Convert source names to file paths
- `DependencyResolver`: Track data dependencies

### 4. Validator (`validator.py`)
- `SchemaValidator`: Validate data against schema
- `HealthChecker`: Check data file health/availability

### 5. YAML Configs (`configs/`)

**data_sources.yaml** (57 data sources):
```yaml
data_sources:
  bank_metrics:
    path: "processed/fundamental/bank/bank_financial_metrics.parquet"
    schema_columns: [symbol, report_date, total_assets, roe, roa, ...]
    entity_type: bank
    category: fundamental
    update_freq: quarterly
    cache_ttl: 86400
```

**services.yaml** (Service → data source mapping):
```yaml
services:
  BankService:
    service_path: "WEBAPP.services.bank_service"
    data_sources: [bank_metrics]
    entity_type: bank
    methods: [get_financial_data, get_latest_metrics, ...]
```

**pipelines.yaml** (Pipeline outputs)
**dashboards.yaml** (Dashboard configurations)

---

## Schema Registry (JSON Schemas)

**Location:** `config/schema_registry/`

### Core Schemas
- `types.json`: Data type definitions (price, volume, percentage, ratio, market_cap, date, ticker, currency)
- `entities.json`: Entity types (COMPANY, BANK, INSURANCE, SECURITY) with icons, colors, calculator classes
- `mappings.json`: Field mappings between different data formats

### Domain Schemas
**Fundamental:**
- `metrics.json`: Fundamental metric definitions
- `reports.json`: Report type schemas
- `calculations.json`: Calculation formulas

**Technical:**
- `indicators.json`: Technical indicator schemas (MA, RSI, MACD, etc.)
- `signals.json`: Trading signal definitions
- `trends.json`: Trend analysis schemas

**Valuation:**
- `metrics.json`: Valuation metrics (PE, PB, EV/EBITDA)
- `models.json`: Valuation model definitions

**Unified:**
- `sector.json`: Sector analysis schemas
- `decisions.json`: Decision schemas
- `insights.json`: Insight generation schemas

### Display Schemas
- `charts.json`: Plotly chart configurations
- `tables.json`: Streamlit table layouts
- `dashboards.json`: Dashboard layout specifications

---

## Business Logic Configuration

**Location:** `config/business_logic/`

### Analysis (`analysis/`)
- `fa_analysis.json`: Fundamental analysis rules
- `ta_analysis.json`: Technical analysis rules
- `valuation_analysis.json`: Valuation analysis rules
- `unified_analysis.json`: Combined analysis logic

### Decisions (`decisions/`)
- `rules.json`: Trading decision rules (buy/hold/sell conditions)
- `thresholds.json`: Metric thresholds for decisions
- `weights.json`: Scoring weights

**Example from rules.json:**
```json
{
  "decision_rules": {
    "buy": {
      "conditions": [
        "overall_score > 70",
        "fundamental_score > 60",
        "technical_score > 50",
        "valuation_score < 30"
      ]
    }
  }
}
```

### Alerts (`alerts/`)
- `rules.json`: Alert triggering rules
- `channels.json`: Alert channel configurations
- `subscriptions.json`: User alert subscriptions

---

## Sector Analysis Configuration

**Location:** `config/sector_analysis/config_manager.py`

**Purpose:** Manage user preferences for FA+TA sector analysis

**Features:**
- Load default weights
- Load user preferences
- Merge configs (default + user overrides)
- Provide active configuration

**Configuration Files:**
- `default_weights.json`: Default FA/TA weights
- `indicators_config.json`: Indicator settings
- `user_preferences.json`: User overrides

---

## Key Files & Their Purposes

| File | Purpose | Size/Records |
|------|---------|--------------|
| `metric_registry.json` | 2,099 financial metrics from BSC | 770 KB |
| `ticker_details.json` | Ticker metadata (457 tickers) | ~50 KB |
| `unit_standards.json` | v4.0.0 unit standardization | 8.5 KB |
| `data_sources.yaml` | 57 data source mappings | YAML |
| `services.yaml` | Service → data source mapping | YAML |
| `schema_registry.py` | SchemaRegistry class | Python |
| `metric_lookup.py` | MetricRegistry class | Python |
| `sector_lookup.py` | SectorRegistry class | Python |
| `config_manager.py` | Sector analysis config | Python |

---

## Usage Patterns

### Import Registries
```python
# Canonical import locations (as of 2025-12-10)
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry
from config.data_mapping import get_registry, get_data_path
```

### Initialize Registries
```python
metric_reg = MetricRegistry()  # 2,099 metrics
sector_reg = SectorRegistry()  # 457 tickers × 19 sectors
schema_reg = SchemaRegistry()  # Singleton
data_reg = get_registry()      # Data mapping registry
```

### Get Data Paths
```python
# Using data mapping registry
path = get_data_path("bank_metrics")
# Returns: Path("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")

# Or using registry
registry = get_registry()
path = registry.get_path("company_metrics")
```

### Load Data with Schema Validation
```python
import pandas as pd
from config.data_mapping import SchemaValidator

# Load data
df = pd.read_parquet("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")

# Validate against schema
validator = SchemaValidator()
result = validator.validate(df, "bank_metrics")
```

---

## Migration History

### 2025-12-15: Config Cleanup
- Deleted legacy files (data_sources.json, frequency_filtering_rules.json)
- Fixed path casing issues
- Consolidated daily scripts to PROCESSORS/pipelines/

### 2025-12-14: Unit Standardization v4.0.0
- Created unit_standards.json
- Updated all calculators to store in VND (not billions)
- Changed ratios to decimals (not percentages)
- Added bilingual docstring requirements

### 2025-12-10: Registry & Schema Cleanup
- Moved PROCESSORS/core/registries/ → config/registries/
- Removed duplicate schema files
- Removed duplicate metric_registry.json copies
- Storage saved: ~2.4 MB

**Import Pattern Changed:**
```python
# ✅ NEW (canonical)
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry

# ❌ OLD (deprecated)
from PROCESSORS.core.registries.metric_lookup import MetricRegistry
```

---

## Important Notes

### Single Source of Truth
- `config/metadata/metric_registry.json` is CANONICAL
- NO copies, NO manual edits
- ONLY use builder scripts to update

### Backward Compatibility
- Files in `config/schemas/` are LEGACY (deprecated)
- Use `config/schema_registry/` for new code

### Unit Standards Enforcement
- All calculators MUST follow v4.0.0
- Storage: VND (absolute), decimals (ratios)
- NO conversion at calculator layer

### Docstring Requirement
- All Python files MUST have bilingual docstrings (Vietnamese + English)
- Module, class, and function docstrings required

---

## Unresolved Questions

1. **Schema Registry Status:** The SchemaRegistry class loads defaults but references removed master_schema.json. Is this intentional for Streamlit rebuild?

2. **Data Mapping YAML vs JSON:** Data mapping uses YAML configs while schemas use JSON. Is this intentional or should we standardize?

3. **Business Logic Activation:** Business logic configs exist (rules, thresholds, weights) but unclear if actively used in calculations or just reference.

4. **Registry Builders:** Builder scripts exist in `config/registries/builders/` but not examined. When/how are they run?

5. **Schema Registry Display Schemas:** `schema_registry/display/` JSON files exist but integration with Streamlit not verified.

---

## Recommendations

1. **Verify Schema Registry Integration:** Confirm display schemas are actively used in Streamlit rebuild
2. **Standardize Config Format:** Consider YAML vs JSON consistency
3. **Document Builder Workflow:** Add instructions for when/how to rebuild registries
4. **Activate Business Logic:** If decision/threshold configs are unused, consider removal or integration
5. **Add Schema Validation:** Implement runtime validation against schemas

---

**Report Generated:** 2026-01-11  
**Agent:** scout-external (a8610f2)  
**Status:** Configuration system fully documented
