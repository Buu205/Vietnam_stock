# Data Mapping Registry Architecture - Complete Scan

**Date:** 2025-12-31  
**Status:** Complete  
**Files Scanned:** 8 Python + 4 YAML configs

---

## 1. Overview

The `config/data_mapping/` module implements a **clean architecture registry system** for the Vietnam Dashboard project. It centralizes all data flow mappings in one place and provides dependency analysis, path resolution, and validation services.

**Core Purpose:**
- Single source of truth for data file locations, schemas, pipelines, services, and dashboards
- Dependency graph building for impact analysis
- Path resolution with validation
- Schema validation and health checking

**Architecture Style:** Clean Architecture with immutable domain entities (dataclasses) + service layers

---

## 2. Python Files & Classes

### 2.1 `entities.py` - Domain Layer (Pure Dataclasses)

**No external dependencies** - innermost clean architecture layer.

#### Type Aliases
```python
EntityType = Literal["bank", "company", "insurance", "security", "all"]
UpdateFrequency = Literal["realtime", "daily", "weekly", "quarterly", "yearly"]
DataCategory = Literal["fundamental", "technical", "valuation", "macro", "forecast", "sector"]
```

#### Core Entities

**DataSource** (frozen dataclass)
- Represents a single data file with metadata
- Key attributes:
  - `name`: Unique identifier (e.g., "bank_metrics")
  - `path`: Path relative to DATA/ (e.g., "processed/fundamental/bank/...")
  - `schema_columns`: Expected columns (immutable tuple)
  - `entity_type`: Which entity (bank, company, insurance, security, all)
  - `category`: Data category for grouping
  - `update_freq`: Update frequency
  - `cache_ttl`: Cache time-to-live in seconds
  - `derived_from`: List of source names this derives from
- Methods:
  - `full_path(data_root)`: Get full path from data root

**PipelineOutput** (mutable dataclass)
- Maps processing pipeline to output files
- Key attributes:
  - `pipeline_name`: Unique identifier
  - `script_path`: Path to pipeline script
  - `outputs`: List of DataSource names produced
  - `dependencies`: List of DataSource names required
  - `schedule`: Cron or frequency
  - `version`: Schema version

**DashboardConfig** (mutable dataclass)
- Maps dashboard page to required data
- Key attributes:
  - `page_id`: Unique page identifier
  - `page_path`: Path to Streamlit page file
  - `data_sources`: List of DataSource names required
  - `services`: List of Service names to use
  - `cache_ttl`: Override cache TTL
  - `requires_ticker`: Whether page needs ticker selection

**ServiceBinding** (mutable dataclass)
- Maps service class to data sources it consumes
- Key attributes:
  - `service_name`: Class name (e.g., "BankService")
  - `service_path`: Module path (e.g., "WEBAPP.services.bank_service")
  - `data_sources`: List of DataSource names consumed
  - `entity_type`: Primary entity type served
  - `methods`: List of public method names

**DataMappingConfig** (Aggregate Root)
- Root configuration aggregating all mappings
- Key attributes:
  - `data_sources`: Dict[str, DataSource]
  - `pipelines`: Dict[str, PipelineOutput]
  - `dashboards`: Dict[str, DashboardConfig]
  - `services`: Dict[str, ServiceBinding]
  - `version`: Schema version
- Key methods:
  - `get_data_source(name)`: Get source by name
  - `get_sources_for_service(service_name)`: Get all sources for a service
  - `get_sources_for_dashboard(page_id)`: Get all sources for a dashboard
  - `get_pipeline_for_output(output_name)`: Find pipeline that produces output

---

### 2.2 `registry.py` - Singleton Registry Layer

**DataMappingRegistry** (Singleton)

**Thread-safe, lazy-loaded singleton** that loads YAML configs once and provides fast lookups.

```python
registry = DataMappingRegistry()  # Same instance every call
```

**Initialization:**
- Loads all YAML configs in `configs/` directory
- Converts YAML to domain entities
- Cached via `@lru_cache` for performance

**Internal Methods:**
- `_load_data_sources()`: Load data_sources.yaml
- `_load_services()`: Load services.yaml
- `_load_pipelines()`: Load pipelines.yaml
- `_load_dashboards()`: Load dashboards.yaml

**Public API Methods:**

| Method | Returns | Purpose |
|--------|---------|---------|
| `get_path(source_name, data_root)` | `Path` | Get full path to data file |
| `get_schema(source_name)` | `tuple[str, ...]` | Get expected columns |
| `get_cache_ttl(source_name)` | `int` | Get cache TTL in seconds |
| `get_data_source(source_name)` | `DataSource \| None` | Get DataSource entity |
| `get_sources_for_service(service_name)` | `list[DataSource]` | Get sources for service |
| `get_sources_for_dashboard(page_id)` | `list[DataSource]` | Get sources for dashboard |
| `get_pipeline(pipeline_name)` | `PipelineOutput \| None` | Get pipeline config |
| `get_dashboard(page_id)` | `DashboardConfig \| None` | Get dashboard config |
| `get_service(service_name)` | `ServiceBinding \| None` | Get service binding |
| `list_data_sources()` | `list[str]` | List all source names |
| `list_services()` | `list[str]` | List all service names |
| `list_pipelines()` | `list[str]` | List all pipeline names |
| `list_dashboards()` | `list[str]` | List all dashboard page IDs |
| `to_dict()` | `dict` | Export as JSON-serializable dict |

**Convenience Functions:**
```python
get_registry() -> DataMappingRegistry  # Cached singleton
get_data_path(source_name, data_root) -> Path  # Shortcut to registry.get_path()
```

---

### 2.3 `resolver.py` - Path & Dependency Resolution

**PathResolver** - Resolves data paths with validation

```python
resolver = PathResolver()
path = resolver.resolve("bank_metrics")  # Returns absolute Path
path = resolver.resolve_safe("bank_metrics")  # Returns Path | None
```

Methods:
- `resolve(source_name, validate=True)`: Get absolute path, optionally validate exists
- `resolve_safe(source_name)`: Safe version, returns None if not found
- `validate_all()`: Validate all registered sources exist
- `get_missing_sources()`: List sources with missing files
- `get_existing_sources()`: List sources with existing files

**DependencyResolver** - Builds dependency graph for impact analysis

```python
dep = DependencyResolver()
upstream = dep.get_upstream("bank_metrics")  # What does this need?
downstream = dep.get_downstream("ohlcv_raw")  # What depends on this?
impact = dep.get_impact_chain("ohlcv_raw")  # Full impact analysis
order = dep.get_execution_order()  # Topological sort
```

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `get_upstream(source_name)` | Get dependencies (sources needed by this) |
| `get_downstream(source_name)` | Get dependents (what depends on this) |
| `get_all_downstream(source_name)` | Recursive downstream dependencies |
| `get_impact_chain(source_name)` | Full impact: upstream, downstream, affected services/dashboards |
| `get_execution_order(target_sources)` | Topological sort for pipeline execution |

**Internal Graph:**
- `_producers`: Maps source → list of pipelines that produce it
- `_consumers`: Maps source → list of pipelines that consume it

---

### 2.4 `validator.py` - Schema & Health Validation

**ValidationResult** (dataclass)
- Result of schema validation
- Attributes:
  - `source_name`: Source being validated
  - `is_valid`: Boolean validation result
  - `expected_columns`: Expected columns from registry
  - `actual_columns`: Actual columns in file
  - `missing_columns`: In expected but not in file
  - `extra_columns`: In file but not in expected
  - `error`: Error message if validation failed

**HealthStatus** (dataclass)
- Health status of a data source
- Attributes:
  - `source_name`: Source name
  - `exists`: Whether file exists
  - `is_stale`: Whether data is outdated
  - `last_modified`: File modification time
  - `file_size_mb`: File size in MB
  - `row_count`: Number of rows (optional, not for large files)
  - `error`: Error message if check failed

**SchemaValidator** - Validates parquet/JSON schemas

```python
validator = SchemaValidator()
result = validator.validate("bank_metrics")
if not result.is_valid:
    print(f"Missing: {result.missing_columns}")
```

Methods:
- `validate(source_name)`: Validate one source
- `validate_all()`: Validate all registered sources
- `get_invalid_sources()`: Get list of sources that failed validation

**HealthChecker** - Checks data freshness & availability

```python
checker = HealthChecker()
report = checker.full_report()
stale = checker.get_stale_sources()
```

**Staleness Thresholds:**
```python
{
    "daily": 26,           # 26 hours for daily data
    "quarterly": 2200,     # ~3 months
    "yearly": 8800,        # ~1 year
    "realtime": 1,         # 1 hour
    "weekly": 170,         # ~1 week
}
```

Methods:
- `check(source_name)`: Check health of one source
- `check_all()`: Check all sources
- `get_stale_sources(max_age_hours)`: Get stale data
- `get_missing_sources()`: Get missing files
- `full_report()`: Generate comprehensive health report

---

### 2.5 `__init__.py` - Package Exports

**Exports all public APIs in one place:**

```python
from config.data_mapping import (
    # Type aliases
    EntityType, UpdateFrequency, DataCategory,
    
    # Entities
    DataSource, PipelineOutput, DashboardConfig, ServiceBinding, DataMappingConfig,
    
    # Registry
    DataMappingRegistry, get_registry, get_data_path,
    
    # Resolvers
    PathResolver, DependencyResolver,
    
    # Validators
    SchemaValidator, HealthChecker, ValidationResult, HealthStatus,
)
```

---

## 3. YAML Configuration Files

All configs in `config/data_mapping/configs/` directory.

### 3.1 `data_sources.yaml` - Data Source Registry

**Maps data files to paths, schemas, metadata.**

Structure:
```yaml
version: "1.0"
data_sources:
  <source_name>:
    path: "relative/path/to/file.parquet"
    schema_columns: [col1, col2, col3]
    entity_type: "bank|company|insurance|security|all"
    category: "fundamental|technical|valuation|macro|forecast|sector"
    update_freq: "daily|quarterly|yearly"
    cache_ttl: 3600  # seconds
    derived_from: [optional_upstream_source]
```

**Data Categories:**

| Category | Files | Update Freq |
|----------|-------|------------|
| **Fundamental** | bank_metrics, company_metrics, insurance_metrics, security_metrics | Quarterly |
| **Valuation** | pe_historical, pb_historical, vnindex_valuation, sector_valuation | Daily |
| **Technical** | ohlcv_raw, technical_basic, market_breadth | Daily |
| **Macro** | macro_commodity | Daily |
| **Forecast** | bsc_individual, bsc_sector_valuation | Daily |

**Total Sources:** 18 registered data sources

Key sources:
- `bank_metrics`: Bank fundamentals (NIM, NPL, CAR, CASA, ROE, ROA)
- `company_metrics`: Company fundamentals (revenue, margins, ROE, ROA)
- `pe_historical`: Daily PE ratios by ticker
- `pb_historical`: Daily PB ratios by ticker
- `vnindex_valuation`: VN-Index valuation metrics + forward PE
- `sector_valuation`: Sector PE/PB TTM
- `ohlcv_raw`: Raw price data (source of truth)
- `technical_basic`: Price + indicators (SMA, RSI)
- `bsc_individual`: Individual stock forecasts + upside %
- `bsc_sector_valuation`: Sector forward PE forecasts

---

### 3.2 `services.yaml` - Service Bindings

**Maps service classes to data sources they consume.**

Structure:
```yaml
version: "1.0"
services:
  <ServiceName>:
    service_path: "WEBAPP.services.service_module"
    data_sources: [source1, source2]
    entity_type: "bank|company|all"
    methods: [method1, method2]
```

**Registered Services:** 8 services

| Service | Entity Type | Data Sources | Purpose |
|---------|-------------|--------------|---------|
| **BankService** | bank | bank_metrics | Bank financial analysis |
| **CompanyService** | company | company_metrics | Company financial analysis |
| **SecurityService** | security | security_metrics | Brokerage analysis |
| **ValuationService** | all | pe_historical, pb_historical, vnindex_valuation, sector_valuation | Valuation metrics |
| **TechnicalService** | all | ohlcv_raw, technical_basic, market_breadth | Technical analysis |
| **SectorService** | all | sector_valuation, company_metrics, bank_metrics | Sector analysis |
| **ForecastService** | all | bsc_individual, bsc_sector_valuation, pe_historical | Forecasts + upside |
| **FxService** | all | macro_commodity | FX rates + commodity prices |

---

### 3.3 `pipelines.yaml` - Pipeline Registry

**Maps pipeline scripts to outputs and dependencies.**

Structure:
```yaml
version: "1.0"
pipelines:
  <pipeline_name>:
    script_path: "PROCESSORS/path/to/script.py"
    outputs: [source1, source2]
    dependencies: [upstream1, upstream2]
    schedule: "daily|quarterly|manual"
```

**Registered Pipelines:** 14 pipelines

**Execution Order (Topological):**

1. **Step 0 - Raw Data**
   - `ohlcv_updater` → ohlcv_raw (no deps)

2. **Step 1 - Fundamentals** (Quarterly)
   - `bank_calculator` → bank_metrics
   - `company_calculator` → company_metrics
   - `insurance_calculator` → insurance_metrics
   - `security_calculator` → security_metrics

3. **Step 2 - Technical** (Daily)
   - `technical_processor` → technical_basic, market_breadth (deps: ohlcv_raw)

4. **Step 3 - Macro/Commodity** (Daily)
   - `macro_commodity_updater` → macro_commodity

5. **Step 4 - Valuation** (Daily)
   - `pe_calculator` → pe_historical, vnindex_valuation (deps: ohlcv_raw, company_metrics, bank_metrics)
   - `pb_calculator` → pb_historical (deps: ohlcv_raw, company_metrics, bank_metrics)
   - `sector_valuation_calculator` → sector_valuation (deps: pe_historical, pb_historical)

6. **Step 5 - Forecast** (Manual)
   - `bsc_forecast_processor` → bsc_individual, bsc_sector_valuation

7. **Unified Daily Update**
   - `daily_update_all` → ohlcv_raw, technical_basic, market_breadth, pe_historical, pb_historical, vnindex_valuation, macro_commodity

---

### 3.4 `dashboards.yaml` - Dashboard Registry

**Maps Streamlit pages to required data sources and services.**

Structure:
```yaml
version: "1.0"
dashboards:
  <page_id>:
    page_path: "WEBAPP/pages/path/to/page.py"
    data_sources: [source1, source2]
    services: [service1, service2]
    requires_ticker: true|false
    cache_ttl: 3600
```

**Registered Dashboards:** 8 pages

| Dashboard | Requires Ticker | Data Sources | Services | Cache TTL |
|-----------|-----------------|--------------|----------|-----------|
| **bank_dashboard** | Yes | bank_metrics, pe_historical, pb_historical | BankService, ValuationService | 3600 |
| **company_dashboard** | Yes | company_metrics, pe_historical, pb_historical | CompanyService, ValuationService | 3600 |
| **security_dashboard** | Yes | security_metrics | SecurityService | 3600 |
| **sector_dashboard** | No | company_metrics, bank_metrics, sector_valuation, vnindex_valuation | SectorService, CompanyService, BankService, ValuationService | 7200 |
| **valuation_dashboard** | Yes | pe_historical, pb_historical, vnindex_valuation, sector_valuation | ValuationService | 3600 |
| **technical_dashboard** | Yes | ohlcv_raw, technical_basic, market_breadth | TechnicalService | 300 |
| **forecast_dashboard** | No | bsc_individual, bsc_sector_valuation, pe_historical, pb_historical | ForecastService, ValuationService | 3600 |
| **fx_commodities_dashboard** | No | macro_commodity | FxService | 3600 |

---

## 4. How the Registry System Works

### 4.1 Core Flow Diagram

```
YAML Files
├── data_sources.yaml
├── services.yaml
├── pipelines.yaml
└── dashboards.yaml
         ↓
    (Loaded Once)
         ↓
DataMappingRegistry (Singleton)
├── _config: DataMappingConfig
│   ├── data_sources: Dict[str, DataSource]
│   ├── services: Dict[str, ServiceBinding]
│   ├── pipelines: Dict[str, PipelineOutput]
│   └── dashboards: Dict[str, DashboardConfig]
├── Public API (lookup methods)
└── @property config (raw access)
         ↓
    (Fast lookups, no reloading)
         ↓
PathResolver, DependencyResolver, Validators
(Use registry for dependency analysis)
```

### 4.2 Usage Pattern 1: Get Path to Data File

```python
from config.data_mapping import get_data_path, get_registry

# Quick path lookup
path = get_data_path("bank_metrics")
# Returns: Path("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")

# With validation
registry = get_registry()
if registry.get_data_source("bank_metrics"):
    full_path = registry.get_path("bank_metrics", data_root="DATA")
```

### 4.3 Usage Pattern 2: Service Data Dependencies

```python
from config.data_mapping import get_registry

registry = get_registry()

# What data does BankService need?
sources = registry.get_sources_for_service("BankService")
# Returns: [DataSource(name="bank_metrics", ...)]

# What methods does this service have?
service = registry.get_service("BankService")
print(service.methods)  # ['get_financial_data', 'get_latest_metrics', ...]
```

### 4.4 Usage Pattern 3: Dashboard Dependency Analysis

```python
from config.data_mapping import get_registry, DependencyResolver

registry = get_registry()

# What data does bank_dashboard need?
sources = registry.get_sources_for_dashboard("bank_dashboard")
# Returns: [bank_metrics, pe_historical, pb_historical]

# What services should it use?
dashboard = registry.get_dashboard("bank_dashboard")
print(dashboard.services)  # ['BankService', 'ValuationService']
```

### 4.5 Usage Pattern 4: Dependency Graph Analysis

```python
from config.data_mapping import DependencyResolver

dep = DependencyResolver()

# Impact analysis - what breaks if this changes?
impact = dep.get_impact_chain("ohlcv_raw")
print(impact)
# {
#     'source': 'ohlcv_raw',
#     'upstream': [],  # No dependencies
#     'downstream': ['technical_basic', 'pe_historical', 'pb_historical'],
#     'affected_services': ['TechnicalService', 'ValuationService'],
#     'affected_dashboards': ['technical_dashboard', 'valuation_dashboard', 'sector_dashboard'],
# }

# What order should pipelines run?
order = dep.get_execution_order()
# Returns topologically sorted pipeline names
```

### 4.6 Usage Pattern 5: Data Health Checking

```python
from config.data_mapping import SchemaValidator, HealthChecker

# Validate all file schemas
validator = SchemaValidator()
invalid = validator.get_invalid_sources()
if invalid:
    for result in invalid:
        print(f"{result.source_name}: Missing {result.missing_columns}")

# Check data freshness
checker = HealthChecker()
report = checker.full_report()
print(report['summary'])  # {healthy, stale, missing, total_size_mb}

for stale in checker.get_stale_sources():
    print(f"{stale.source_name} is stale: last modified {stale.last_modified}")
```

---

## 5. Key Architecture Patterns

### 5.1 Clean Architecture Layers

```
Domain Layer (Innermost) - entities.py
├── Pure dataclasses (frozen/immutable)
├── No external dependencies
└── Type aliases & domain logic

Application Layer - registry.py, resolver.py, validator.py
├── Business use cases
├── Orchestration of domain entities
└── Thin wrapper around data

Infrastructure Layer (Outermost)
├── YAML loading
├── File I/O
└── External system access
```

### 5.2 Singleton Pattern

```python
# First call: loads YAML, builds graph, initializes
registry = DataMappingRegistry()

# Subsequent calls: returns same instance
registry2 = DataMappingRegistry()
assert registry is registry2  # True
```

### 5.3 Immutability

**DataSource** is frozen (immutable):
```python
source = DataSource(name="test", ...)
source.name = "other"  # Raises FrozenInstanceError
```

**Prevents accidental modification of registry state.**

### 5.4 Lazy Dependency Resolution

Dependencies are resolved on-demand via `DependencyResolver`:
- Builds graph from pipeline definitions
- Topological sort for execution order
- Recursive downstream analysis
- No pre-computed graph (memory efficient)

---

## 6. Key Exports from `__init__.py`

```python
# Type Aliases (3)
EntityType
UpdateFrequency
DataCategory

# Domain Entities (5)
DataSource
PipelineOutput
DashboardConfig
ServiceBinding
DataMappingConfig

# Registry (3)
DataMappingRegistry
get_registry()        # Cached singleton getter
get_data_path()       # Shortcut to registry.get_path()

# Resolvers (2)
PathResolver
DependencyResolver

# Validators (4)
SchemaValidator
HealthChecker
ValidationResult
HealthStatus
```

**Total public API:** 17 items

---

## 7. Data Coverage Summary

### 7.1 Entity Types Covered
- Bank (5 metrics related)
- Company (7+ metrics related)
- Insurance (4 metrics related)
- Security/Brokerage (3 metrics related)
- Cross-entity (valuation, technical, macro, forecast)

### 7.2 Data Categories
1. **Fundamental** (4 sources) - Quarterly
2. **Technical** (3 sources) - Daily (300s cache for realtime)
3. **Valuation** (4 sources) - Daily
4. **Macro/Commodity** (1 source) - Daily
5. **Forecast** (2 sources) - Daily (manual input)
6. **Sector** (derived from valuation) - Daily

### 7.3 Pipeline Dependency Chain

```
ohlcv_raw (raw)
  ├→ technical_basic → market_breadth
  ├→ pe_calculator → pb_calculator → sector_valuation_calculator
  └→ macro_commodity (independent)

Quarterly fundamentals:
  bank_metrics ──┐
                 ├→ pe_calculator
  company_metrics ┘
```

---

## 8. Usage Recommendations

### For Adding New Data Source:
1. Add entry to `data_sources.yaml` with path, schema, update frequency
2. Create pipeline entry in `pipelines.yaml` with dependencies
3. Update service bindings if new service needed
4. Update dashboard entries if new pages use it

### For Adding New Service:
1. Add entry to `services.yaml` with data source list
2. Implement service class in `WEBAPP/services/`
3. Reference in dashboard entries

### For Adding New Dashboard:
1. Add entry to `dashboards.yaml` with required sources/services
2. Update cache_ttl based on data freshness requirements
3. Create page file in `WEBAPP/pages/`

### For Data Quality Checks:
```python
from config.data_mapping import HealthChecker, SchemaValidator

# Daily health check routine
checker = HealthChecker()
validator = SchemaValidator()

report = checker.full_report()
if report['summary']['stale'] > 0:
    alert("Stale data detected!")
    
for result in validator.get_invalid_sources():
    alert(f"Schema mismatch in {result.source_name}")
```

---

## 9. Integration Points

### Used By:
- **Dashboard Pages** → `get_registry()` to load data sources
- **Services** → `get_sources_for_service()` to find required files
- **Pipelines** → `DependencyResolver()` for execution order
- **Health Checks** → `HealthChecker` for data freshness
- **Path Resolution** → `get_data_path()` for file locations

### Integrates With:
- `PROCESSORS/` - Pipeline scripts register outputs here
- `WEBAPP/services/` - Services reference data sources
- `WEBAPP/pages/` - Dashboards use this for caching + data loading
- `PROCESSORS/core/config/paths.py` - Alternative path resolution

---

## Summary Table

| Component | Type | Count | Purpose |
|-----------|------|-------|---------|
| **Data Sources** | YAML entries | 18 | Maps files to schemas |
| **Pipelines** | YAML entries | 14 | Maps processing scripts |
| **Services** | YAML entries | 8 | Service bindings |
| **Dashboards** | YAML entries | 8 | Streamlit pages |
| **Python Classes** | Domain entities | 5 | Core data structures |
| **Resolver Classes** | Business logic | 2 | Path + dependency resolution |
| **Validator Classes** | Business logic | 2 | Schema + health validation |
| **Public Exports** | API | 17 | Convenience functions + classes |

---

**Total Scope:** Clean, well-organized registry covering 18 data sources across 457 tickers, 19 sectors, 4 entity types, mapped to 8 services and 8 dashboards.
