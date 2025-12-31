# WEBAPP Services & DataMappingRegistry Integration Scan

**Date:** 2025-12-31
**Status:** Complete Architecture Mapping
**Scope:** WEBAPP/services/ + config/data_mapping/ integration pattern

---

## Executive Summary

The WEBAPP services layer implements a clean architecture pattern with **centralized registry-based path resolution**. All services (BankService, CompanyService, SecurityService, etc.) extend BaseService, which provides automatic path resolution via DataMappingRegistry.

**Key Finding:** Services are completely decoupled from file paths. Data source names map to paths via YAML configs in config/data_mapping/configs/.

---

## 1. BaseService: Core Foundation

**Location:** `WEBAPP/services/base_service.py`

### Architecture

BaseService is an abstract base class providing:

- **Registry Integration** - Lazy-loads DataMappingRegistry (singleton)
- **Path Resolution** - Via PathResolver (validates existence)
- **Schema Validation** - Compares loaded columns against expected schema
- **Cache TTL Management** - Per-source cache duration
- **Data Loading** - Parquet file loading with optional column filtering

### Key Properties

```python
@property
def registry(self):
    """Lazy load registry - singleton pattern."""
    # Caches on first access
    from config.data_mapping import get_registry
    return get_registry()

@property
def resolver(self):
    """Lazy load path resolver."""
    from config.data_mapping import PathResolver
    return PathResolver(self.registry)

@property
def data_root(self) -> Path:
    """Get DATA directory (or test override)."""
    return self._data_root or (self.project_root / "DATA")
```

### Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `get_data_path()` | Get full path via registry | Path object |
| `get_schema()` | Expected columns for source | tuple[str, ...] |
| `get_cache_ttl()` | Cache duration in seconds | int |
| `load_data()` | Load parquet with validation | pd.DataFrame |
| `validate_data_exists()` | Check if data file exists | bool |
| `get_data_source_info()` | Get metadata (path, entity_type, etc.) | dict |

### Internal Initialization

```python
class BaseService(ABC):
    DATA_SOURCE: str = ""      # Override in subclass (e.g., "bank_metrics")
    ENTITY_TYPE: str = ""      # Override in subclass (e.g., "bank")
    
    def __init__(self, data_root: Optional[Path] = None):
        self._registry = None              # Lazy-loaded singleton
        self._resolver = None              # Lazy-loaded resolver
        self._data_root = data_root        # Test override
        self._cached_path: Optional[Path] = None
        self._project_root: Optional[Path] = None
```

---

## 2. Entity-Specific Services (Extend BaseService)

All entity services follow identical pattern - only differ by `DATA_SOURCE` name.

### 2.1 BankService

**Location:** `WEBAPP/services/bank_service.py`

```python
class BankService(BaseService):
    DATA_SOURCE = "bank_metrics"     # Resolves to DATA/processed/fundamental/bank/...
    ENTITY_TYPE = "bank"
```

**Key Methods:**

- `get_financial_data(ticker, period="Quarterly", limit=None)` - Load filtered by symbol, freq_code
- `get_latest_metrics(ticker)` - Most recent quarter data
- `get_available_tickers()` - List of liquid bank tickers (from master_symbols.json)
- `get_peer_comparison(ticker)` - Latest metrics for peers (uses SectorRegistry)

**Internal: Master Symbols**
```python
def _load_master_symbols(self) -> List[str]:
    """Filter to liquid BANK tickers only."""
    # Looks in: config/metadata/master_symbols.json
    # Returns: BANK entities from symbols_by_entity
```

---

### 2.2 CompanyService

**Location:** `WEBAPP/services/company_service.py`

```python
class CompanyService(BaseService):
    DATA_SOURCE = "company_metrics"  # Resolves via registry
    ENTITY_TYPE = "company"
```

**Key Methods:**

- `get_financial_data(ticker, period="Quarterly", limit=None, table_type="all")` - Supports column group filtering
- `get_latest_metrics(ticker)` - Latest quarter
- `get_available_tickers()` - Liquid company tickers
- `get_peer_comparison(ticker)` - Sector peers

**Column Groups (Efficient Loading):**

```python
COLUMN_GROUPS = {
    'income_statement': ['net_revenue', 'cogs', 'gross_profit', 'ebit', 'ebitda', ...],
    'balance_sheet': ['total_assets', 'total_equity', 'cash', 'debt_to_equity', ...],
    'cash_flow': ['operating_cf', 'capex', 'fcf', 'fcff', 'fcfe', ...],
    'ratios': ['roe', 'roa', 'asset_turnover', 'eps', 'bvps', ...],
}
```

Services load only required columns for efficiency.

---

### 2.3 SecurityService

**Location:** `WEBAPP/services/security_service.py`

```python
class SecurityService(BaseService):
    DATA_SOURCE = "security_metrics"  # Securities/brokerage data
    ENTITY_TYPE = "security"
```

**Methods:** Identical to BankService

- `get_financial_data(ticker, period, limit)`
- `get_latest_metrics(ticker)`
- `get_available_tickers()`
- `get_peer_comparison(ticker)`

---

## 3. DataMappingRegistry: Path Resolution Engine

**Location:** `config/data_mapping/`

### 3.1 Registry Architecture

```
config/data_mapping/
├── __init__.py           # Public API exports
├── registry.py           # Singleton registry
├── resolver.py           # Path + Dependency resolvers
├── validator.py          # Schema validation
├── entities.py           # Domain entities (dataclasses)
└── configs/              # YAML configuration
    ├── data_sources.yaml      # File mappings
    ├── services.yaml          # Service bindings
    ├── pipelines.yaml         # Pipeline outputs
    └── dashboards.yaml        # Dashboard configs
```

### 3.2 DataMappingRegistry (Singleton)

**Purpose:** Single source of truth for all data mappings

**Loading Pattern:**

```python
class DataMappingRegistry:
    _instance = None        # Singleton
    _config = None          # Immutable after load
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_configs()  # Once on creation
        return cls._instance
```

**Core Methods:**

| Method | Purpose |
|--------|---------|
| `get_path(source_name)` | Returns Path for data source |
| `get_schema(source_name)` | Returns expected column tuple |
| `get_cache_ttl(source_name)` | Returns cache seconds |
| `get_data_source(source_name)` | Returns DataSource entity |
| `get_sources_for_service(service_name)` | List sources used by service |
| `get_sources_for_dashboard(page_id)` | List sources used by dashboard |
| `list_data_sources()` | All registered source names |

**Convenience Functions:**

```python
def get_registry() -> DataMappingRegistry:
    """Get singleton (cached with @lru_cache)."""
    return DataMappingRegistry()

def get_data_path(source_name: str) -> Path:
    """Shortcut: get_registry().get_path(source_name)."""
```

---

### 3.3 PathResolver: Validation & Safe Resolution

**Location:** `config/data_mapping/resolver.py`

**Purpose:** Resolve paths with existence validation

```python
resolver = PathResolver(registry)

# Strict resolution (raises if not found)
path = resolver.resolve("bank_metrics", validate=True)  # Path or FileNotFoundError

# Safe resolution (returns None if missing)
path = resolver.resolve_safe("bank_metrics")  # Path or None

# Bulk validation
validation = resolver.validate_all()  # {source_name: bool}
missing = resolver.get_missing_sources()  # List of missing files
existing = resolver.get_existing_sources()  # List of available files
```

**Usage in BaseService:**

```python
def get_data_path(self) -> Path:
    """Service uses resolver for path validation."""
    if self._cached_path is None:
        self._cached_path = self.resolver.resolve(
            self.DATA_SOURCE, validate=False  # Lazy validation
        )
    return self._cached_path
```

---

### 3.4 DependencyResolver: Impact Analysis

**Location:** `config/data_mapping/resolver.py`

**Purpose:** Build dependency graph for pipelines/dashboards

```python
resolver = DependencyResolver()

# What data depends on this source?
downstream = resolver.get_downstream("ohlcv_raw")  # All sources derived from this
all_downstream = resolver.get_all_downstream("ohlcv_raw")  # Recursive

# What does this source need?
upstream = resolver.get_upstream("bank_metrics")  # Dependencies

# Full impact analysis
impact = resolver.get_impact_chain("ohlcv_raw")
# Returns: {
#     "source": "ohlcv_raw",
#     "upstream": ["raw_ohlcv_source"],
#     "downstream": ["company_metrics", "pe_historical", ...],
#     "affected_services": ["CompanyService", "ValuationService"],
#     "affected_dashboards": ["fundamental", "valuation"],
# }

# Pipeline execution order
order = resolver.get_execution_order()  # Topological sort
```

---

## 4. Domain Entities (config/data_mapping/entities.py)

Pure dataclasses - no dependencies (Clean Architecture inner layer).

### 4.1 DataSource

```python
@dataclass(frozen=True)
class DataSource:
    name: str                      # "bank_metrics"
    path: str                      # "processed/fundamental/bank/..."
    schema_columns: tuple[str,...]  # Expected columns
    entity_type: str              # "bank", "company", etc.
    category: str                 # "fundamental", "technical", "valuation"
    update_freq: str              # "daily", "weekly", etc.
    cache_ttl: int                # Seconds (3600, etc.)
    derived_from: tuple[str,...]  # Upstream sources
    
    def full_path(self, data_root: str = "DATA") -> str:
        return f"{data_root}/{self.path}"
```

### 4.2 ServiceBinding

```python
@dataclass
class ServiceBinding:
    service_name: str              # "BankService"
    service_path: str              # "WEBAPP/services/bank_service.py"
    data_sources: list[str]        # ["bank_metrics"]
    entity_type: str               # "bank"
    methods: list[str]             # ["get_financial_data", ...]
```

### 4.3 Type Aliases

```python
EntityType = Literal["bank", "company", "insurance", "security", "all"]
UpdateFrequency = Literal["realtime", "daily", "weekly", "quarterly", "yearly"]
DataCategory = Literal["fundamental", "technical", "valuation", "macro", "forecast", "sector"]
```

---

## 5. Registry Integration Flow

### 5.1 Service Initialization to Data Loading

```
1. Create Service
   service = BankService()
   
2. Service calls get_financial_data(ticker)
   
3. get_financial_data() calls self.load_data()
   
4. load_data() calls self.get_data_path()
   
5. get_data_path() uses registry:
   path = self.resolver.resolve(self.DATA_SOURCE)
   
6. Resolver uses registry:
   registry.get_path("bank_metrics")
   
7. Registry looks up in _config.data_sources["bank_metrics"]
   
8. Returns DataSource entity with .path = "processed/fundamental/bank/..."
   
9. Absolute path = project_root / "DATA" / relative_path
   
10. Load parquet file from absolute path
```

### 5.2 Optional Test Override

```python
# Normal: Uses registry paths
service = BankService()

# Testing: Override data_root
service = BankService(data_root=Path("/test/data"))
# Still uses registry for relative path, but joins with custom root
```

---

## 6. YAML Configuration Files

**Location:** `config/data_mapping/configs/`

### 6.1 data_sources.yaml

Maps source names → paths & schemas

```yaml
data_sources:
  bank_metrics:
    path: processed/fundamental/bank/bank_financial_metrics.parquet
    entity_type: bank
    category: fundamental
    update_freq: daily
    cache_ttl: 3600
    schema_columns: [symbol, report_date, year, quarter, roe, roa, ...]
    
  company_metrics:
    path: processed/fundamental/company/company_financial_metrics.parquet
    entity_type: company
    category: fundamental
    update_freq: daily
    cache_ttl: 3600
    schema_columns: [symbol, report_date, net_revenue, npatmi, ...]
    
  security_metrics:
    path: processed/fundamental/security/security_financial_metrics.parquet
    entity_type: security
    category: fundamental
    update_freq: daily
    cache_ttl: 3600
```

### 6.2 services.yaml

Maps services → data sources

```yaml
services:
  BankService:
    service_path: WEBAPP/services/bank_service.py
    data_sources: [bank_metrics]
    entity_type: bank
    methods: [get_financial_data, get_latest_metrics, get_available_tickers]
    
  CompanyService:
    service_path: WEBAPP/services/company_service.py
    data_sources: [company_metrics]
    entity_type: company
    methods: [get_financial_data, get_latest_metrics, get_available_tickers]
```

### 6.3 pipelines.yaml

Maps pipelines → outputs & dependencies

```yaml
pipelines:
  company_calculator:
    script_path: PROCESSORS/fundamental/calculators/company_calculator.py
    outputs: [company_metrics]
    dependencies: [company_raw]
    schedule: daily
```

### 6.4 dashboards.yaml

Maps pages → services & sources

```yaml
dashboards:
  fundamental:
    page_path: WEBAPP/pages/01_fundamental_analysis.py
    services: [BankService, CompanyService]
    data_sources: [bank_metrics, company_metrics]
    cache_ttl: 3600
    requires_ticker: true
```

---

## 7. Service Loading Pattern (Summary)

### How Services Use Registry

**Step 1: Define Service Class**
```python
class BankService(BaseService):
    DATA_SOURCE = "bank_metrics"      # ← Key: Source name
    ENTITY_TYPE = "bank"
```

**Step 2: Registry Lookup (Lazy)**
```python
@property
def registry(self):
    from config.data_mapping import get_registry
    return get_registry()  # Singleton, cached
```

**Step 3: Path Resolution**
```python
def get_data_path(self) -> Path:
    return self.resolver.resolve(self.DATA_SOURCE)
    # → registry.get_path("bank_metrics")
    # → "DATA/processed/fundamental/bank/bank_financial_metrics.parquet"
```

**Step 4: Data Loading**
```python
def load_data(self, columns=None, validate_schema=True) -> pd.DataFrame:
    path = self.get_data_path()  # Via registry
    df = pd.read_parquet(path, columns=columns)
    
    if validate_schema:
        expected = self.registry.get_schema(self.DATA_SOURCE)
        # Check df.columns contains expected columns
    
    return df
```

**Step 5: Service Methods Use load_data()**
```python
def get_financial_data(self, ticker: str, period: str = "Quarterly"):
    df = self.load_data()  # Gets path from registry
    df = df[df['symbol'] == ticker]
    if period == "Quarterly":
        df = df[df['freq_code'] == 'Q']
    return df
```

---

## 8. Key Patterns & Conventions

### 8.1 Naming Convention

| Item | Pattern | Example |
|------|---------|---------|
| Service Class | PascalCase | `BankService` |
| DATA_SOURCE | snake_case | `"bank_metrics"` |
| ENTITY_TYPE | lowercase | `"bank"` |
| File path | snake_case | `bank_financial_metrics.parquet` |
| DataFrame var | snake_case_df | `bank_df` |

### 8.2 Column Filtering

CompanyService uses column groups for efficiency:

```python
COLUMN_GROUPS = {
    'income_statement': ['net_revenue', 'cogs', ...],
    'balance_sheet': ['total_assets', 'equity', ...],
    'ratios': ['roe', 'roa', ...],
}

# Usage
df = self.load_data(columns=COLUMN_GROUPS['ratios'])
```

### 8.3 Master Symbols Filtering

All entity services load liquid tickers from master_symbols.json:

```python
def _load_master_symbols(self) -> List[str]:
    # Looks for: config/metadata/master_symbols.json
    # Returns: BANK/COMPANY/SECURITY entities only
```

### 8.4 Peer Comparison Pattern

All services implement get_peer_comparison():

```python
def get_peer_comparison(self, ticker: str) -> pd.DataFrame:
    from config.registries import SectorRegistry
    
    sector_reg = SectorRegistry()
    peers = sector_reg.get_peers(ticker)  # ← Integrates with SectorRegistry
    
    # Load latest data for each peer
    dfs = [self.get_financial_data(p, "Quarterly", limit=1) for p in peers]
    return pd.concat(dfs)
```

---

## 9. Schema Validation

BaseService validates columns on load:

```python
def _validate_schema(self, df: pd.DataFrame) -> None:
    expected = set(self.get_schema())      # From registry
    actual = set(df.columns.tolist())
    missing = expected - actual
    
    if missing:
        logger.warning(f"Missing columns: {missing}")  # Warns, doesn't fail
```

**Behavior:**
- Warnings logged for missing columns
- Load succeeds even if columns missing
- Uses validate_schema=False in get_financial_data() by design

---

## 10. File Structure Summary

```
WEBAPP/services/
├── __init__.py
├── base_service.py          ← Core (path resolution, schema validation)
├── bank_service.py          ← DATA_SOURCE="bank_metrics"
├── company_service.py       ← DATA_SOURCE="company_metrics"
├── security_service.py      ← DATA_SOURCE="security_metrics"
├── [other services...]      ← (technical, valuation, forecast, etc.)
└── [utilities...]           ← (chat_manager, llm_service, etc.)

config/data_mapping/
├── __init__.py              ← Public API
├── registry.py              ← Singleton registry
├── resolver.py              ← Path & dependency resolvers
├── validator.py             ← Schema validation
├── entities.py              ← Domain entities (dataclasses)
└── configs/
    ├── data_sources.yaml    ← Source → Path mapping
    ├── services.yaml        ← Service → Sources mapping
    ├── pipelines.yaml       ← Pipeline → Outputs mapping
    └── dashboards.yaml      ← Dashboard → Sources mapping
```

---

## 11. Service Capabilities Matrix

| Feature | BankService | CompanyService | SecurityService |
|---------|-------------|-----------------|-----------------|
| get_financial_data(ticker, period, limit) | ✓ | ✓ (with table_type) | ✓ |
| get_latest_metrics(ticker) | ✓ | ✓ | ✓ |
| get_available_tickers() | ✓ | ✓ | ✓ |
| get_peer_comparison(ticker) | ✓ | ✓ | ✓ |
| Column group filtering | - | ✓ (income_statement, balance_sheet, cash_flow, ratios) | - |
| Schema validation | ✓ (BaseService) | ✓ (BaseService) | ✓ (BaseService) |
| Cache TTL management | ✓ (BaseService) | ✓ (BaseService) | ✓ (BaseService) |
| Registry path resolution | ✓ (BaseService) | ✓ (BaseService) | ✓ (BaseService) |

---

## 12. Access Patterns

### Direct Service Access

```python
from WEBAPP.services.bank_service import BankService

service = BankService()
df = service.get_financial_data("ACB", "Quarterly", limit=8)
peers = service.get_peer_comparison("ACB")
```

### Registry Discovery

```python
from config.data_mapping import get_registry

registry = get_registry()
sources = registry.get_sources_for_service("BankService")
# Returns: [DataSource("bank_metrics", ...)]
```

### Dependency Analysis

```python
from config.data_mapping import DependencyResolver

dep_resolver = DependencyResolver()
impact = dep_resolver.get_impact_chain("bank_metrics")
# Shows all services/dashboards affected by changes to bank_metrics
```

---

## 13. Integration with Other Registries

Services also integrate with **SectorRegistry** for peer lookups:

```python
# In get_peer_comparison()
from config.registries import SectorRegistry

sector_reg = SectorRegistry()
peers = sector_reg.get_peers(ticker)  # Separate registry for ticker → peers mapping
```

**Two Registry Systems:**
- **DataMappingRegistry** - File paths & schemas (this document)
- **SectorRegistry** - Ticker info & sector mappings (separate system)

---

## 14. Unresolved Questions

1. **Where is data_sources.yaml?** - Expected at `config/data_mapping/configs/data_sources.yaml` (not scanned - need to verify it exists)
2. **How are cached paths invalidated?** - Cache TTL is managed but invalidation logic not reviewed
3. **InsuranceService?** - Only BankService, CompanyService, SecurityService reviewed. Other entity services likely follow identical pattern

---

## Conclusion

The service architecture implements **clean separation of concerns** through registry-based path resolution:

- **BaseService** = Common behavior (path resolution, loading, validation)
- **Entity Services** = Entity-specific logic (filtering, peer comparison)
- **DataMappingRegistry** = Single source of truth (YAML → entities)
- **Resolvers** = Safe path resolution + dependency analysis
- **Config-Driven** = All paths defined in YAML (no hardcoding)

This pattern enables:
- Adding new services without code changes (just add YAML)
- Validating data integrity (schema checks)
- Understanding impact of data changes (dependency graphs)
- Testing with custom data paths (data_root override)
