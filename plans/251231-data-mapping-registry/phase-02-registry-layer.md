# Phase 2: Registry Layer (Use Cases)

**Est. Time:** 3 hours | **Priority:** High | **Dependencies:** Phase 1 complete

## Context

With entities defined, build the Use Cases layer: `DataMappingRegistry` loads YAML configs into entities, `PathResolver` resolves data paths, `DependencyResolver` builds data flow graph.

## Overview

1. Create YAML configuration files defining all mappings
2. Build `DataMappingRegistry` singleton to load/cache configs
3. Implement `PathResolver` for path lookups (replaces hardcoded paths)
4. Implement `DependencyResolver` for impact analysis

## Requirements

1. YAML for human-editable configs
2. Singleton pattern for registry (one source of truth)
3. Streamlit cache-compatible
4. Fail-fast on missing data sources
5. Export to JSON for API consumption

## Architecture

```
config/data_mapping/
├── __init__.py
├── entities.py          # Phase 1 (done)
├── registry.py          # DataMappingRegistry
├── resolver.py          # PathResolver, DependencyResolver
└── configs/
    ├── data_sources.yaml
    ├── pipelines.yaml
    ├── dashboards.yaml
    └── services.yaml
```

## Implementation Steps

### Step 1: Define YAML Configs

**File:** `config/data_mapping/configs/data_sources.yaml`

```yaml
# Data Sources Registry
# Maps data file names to paths, schemas, and metadata
version: "1.0"

data_sources:
  # ==========================================================================
  # FUNDAMENTAL DATA
  # ==========================================================================

  bank_metrics:
    path: "processed/fundamental/bank/bank_financial_metrics.parquet"
    schema_columns:
      - symbol
      - report_date
      - year
      - quarter
      - freq_code
      - nim
      - npl_ratio
      - car
      - casa_ratio
      - cir
      - roe
      - roa
    entity_type: bank
    category: fundamental
    update_freq: quarterly
    cache_ttl: 86400

  company_metrics:
    path: "processed/fundamental/company/company_financial_metrics.parquet"
    schema_columns:
      - symbol
      - report_date
      - year
      - quarter
      - freq_code
      - net_revenue
      - npatmi
      - roe
      - roa
      - gross_profit_margin
      - net_margin
    entity_type: company
    category: fundamental
    update_freq: quarterly
    cache_ttl: 86400

  insurance_metrics:
    path: "processed/fundamental/insurance/insurance_financial_metrics.parquet"
    schema_columns:
      - symbol
      - report_date
      - combined_ratio
      - loss_ratio
      - roe
    entity_type: insurance
    category: fundamental
    update_freq: quarterly
    cache_ttl: 86400

  security_metrics:
    path: "processed/fundamental/security/security_financial_metrics.parquet"
    schema_columns:
      - symbol
      - report_date
      - roe
      - roa
      - brokerage_income
    entity_type: security
    category: fundamental
    update_freq: quarterly
    cache_ttl: 86400

  # ==========================================================================
  # VALUATION DATA
  # ==========================================================================

  pe_historical:
    path: "processed/valuation/pe/historical/historical_pe.parquet"
    schema_columns:
      - ticker
      - date
      - pe_ratio
      - eps_ttm
      - close_price
    entity_type: all
    category: valuation
    update_freq: daily
    cache_ttl: 3600

  pb_historical:
    path: "processed/valuation/pb/historical/historical_pb.parquet"
    schema_columns:
      - ticker
      - date
      - pb_ratio
      - bvps
      - close_price
    entity_type: all
    category: valuation
    update_freq: daily
    cache_ttl: 3600

  vnindex_valuation:
    path: "processed/valuation/vnindex/vnindex_valuation_refined.parquet"
    schema_columns:
      - date
      - vnindex_pe
      - vnindex_pb
    entity_type: all
    category: valuation
    update_freq: daily
    cache_ttl: 3600

  # ==========================================================================
  # TECHNICAL DATA
  # ==========================================================================

  ohlcv_raw:
    path: "raw/ohlcv/OHLCV_mktcap.parquet"
    schema_columns:
      - ticker
      - date
      - open
      - high
      - low
      - close
      - volume
      - market_cap
    entity_type: all
    category: technical
    update_freq: daily
    cache_ttl: 3600

  # ==========================================================================
  # MACRO DATA
  # ==========================================================================

  macro_commodity_unified:
    path: "processed/macro_commodity/macro_commodity_unified.parquet"
    schema_columns:
      - date
      - deposit_rate
      - usd_vnd
      - gold_price
      - oil_price
    entity_type: all
    category: macro
    update_freq: daily
    cache_ttl: 3600

  # ==========================================================================
  # FORECAST DATA
  # ==========================================================================

  bsc_forecast:
    path: "processed/forecast/bsc/bsc_forecast_latest.json"
    schema_columns:
      - ticker
      - target_price
      - rating
      - eps_forecast
    entity_type: all
    category: forecast
    update_freq: daily
    cache_ttl: 3600
```

**File:** `config/data_mapping/configs/services.yaml`

```yaml
# Services Registry
# Maps service classes to data sources they consume
version: "1.0"

services:
  BankService:
    service_path: "WEBAPP.services.bank_service"
    data_sources:
      - bank_metrics
    entity_type: bank
    methods:
      - get_financial_data
      - get_latest_metrics
      - get_available_tickers
      - get_peer_comparison

  CompanyService:
    service_path: "WEBAPP.services.company_service"
    data_sources:
      - company_metrics
    entity_type: company
    methods:
      - get_financial_data
      - get_latest_metrics
      - get_available_tickers
      - get_peer_comparison

  ValuationService:
    service_path: "WEBAPP.services.valuation_service"
    data_sources:
      - pe_historical
      - pb_historical
      - vnindex_valuation
    entity_type: all
    methods:
      - get_ticker_pe
      - get_ticker_pb
      - get_vnindex_valuation

  TechnicalService:
    service_path: "WEBAPP.services.technical_service"
    data_sources:
      - ohlcv_raw
    entity_type: all
    methods:
      - get_ohlcv
      - get_indicators

  ForecastService:
    service_path: "WEBAPP.services.forecast_service"
    data_sources:
      - bsc_forecast
    entity_type: all
    methods:
      - get_forecast
      - get_top_upside
```

**File:** `config/data_mapping/configs/pipelines.yaml`

```yaml
# Pipelines Registry
# Maps pipeline scripts to their outputs and dependencies
version: "1.0"

pipelines:
  bank_calculator:
    script_path: "PROCESSORS/fundamental/calculators/bank_calculator.py"
    outputs:
      - bank_metrics
    dependencies:
      - ohlcv_raw
    schedule: "quarterly"

  company_calculator:
    script_path: "PROCESSORS/fundamental/calculators/company_calculator.py"
    outputs:
      - company_metrics
    dependencies:
      - ohlcv_raw
    schedule: "quarterly"

  pe_calculator:
    script_path: "PROCESSORS/valuation/calculators/vnindex_pe_calculator_optimized.py"
    outputs:
      - pe_historical
      - vnindex_valuation
    dependencies:
      - company_metrics
      - bank_metrics
      - ohlcv_raw
    schedule: "daily"

  daily_update_pipeline:
    script_path: "PROCESSORS/pipelines/run_all_daily_updates.py"
    outputs:
      - pe_historical
      - pb_historical
      - ohlcv_raw
      - macro_commodity_unified
    dependencies: []
    schedule: "daily"
```

**File:** `config/data_mapping/configs/dashboards.yaml`

```yaml
# Dashboards Registry
# Maps Streamlit pages to required data sources
version: "1.0"

dashboards:
  bank_analysis:
    page_path: "WEBAPP/pages/bank_analysis.py"
    data_sources:
      - bank_metrics
      - pe_historical
    services:
      - BankService
      - ValuationService
    requires_ticker: true
    cache_ttl: 3600

  company_analysis:
    page_path: "WEBAPP/pages/company_analysis.py"
    data_sources:
      - company_metrics
      - pe_historical
      - pb_historical
    services:
      - CompanyService
      - ValuationService
    requires_ticker: true
    cache_ttl: 3600

  sector_overview:
    page_path: "WEBAPP/pages/sector_overview.py"
    data_sources:
      - company_metrics
      - bank_metrics
      - vnindex_valuation
    services:
      - CompanyService
      - BankService
      - ValuationService
    requires_ticker: false
    cache_ttl: 7200

  forecast_dashboard:
    page_path: "WEBAPP/pages/forecast.py"
    data_sources:
      - bsc_forecast
      - pe_historical
    services:
      - ForecastService
    requires_ticker: false
    cache_ttl: 3600
```

### Step 2: Create Registry Class

**File:** `config/data_mapping/registry.py`

```python
"""
Data Mapping Registry
=====================

Singleton registry loading YAML configs into entities.
Provides lookup methods for paths, schemas, dependencies.
"""

import yaml
from pathlib import Path
from typing import Optional
from functools import lru_cache

from .entities import (
    DataSource,
    PipelineOutput,
    DashboardConfig,
    ServiceBinding,
    DataMappingConfig,
)

# ============================================================================
# SINGLETON REGISTRY
# ============================================================================

class DataMappingRegistry:
    """
    Central registry for all data mappings.

    Loads YAML configs once, provides fast lookups.
    Thread-safe via immutable data after initialization.

    Usage:
        registry = DataMappingRegistry()
        path = registry.get_path("bank_metrics")
        sources = registry.get_sources_for_service("BankService")
    """

    _instance: Optional["DataMappingRegistry"] = None
    _config: Optional[DataMappingConfig] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_configs()
        return cls._instance

    def _load_configs(self) -> None:
        """Load all YAML configs into entities."""
        config_dir = Path(__file__).parent / "configs"

        # Load data sources
        data_sources = self._load_data_sources(config_dir / "data_sources.yaml")

        # Load services
        services = self._load_services(config_dir / "services.yaml")

        # Load pipelines
        pipelines = self._load_pipelines(config_dir / "pipelines.yaml")

        # Load dashboards
        dashboards = self._load_dashboards(config_dir / "dashboards.yaml")

        self._config = DataMappingConfig(
            data_sources=data_sources,
            pipelines=pipelines,
            dashboards=dashboards,
            services=services,
        )

    def _load_data_sources(self, path: Path) -> dict[str, DataSource]:
        """Load data sources from YAML."""
        if not path.exists():
            return {}

        with open(path) as f:
            data = yaml.safe_load(f)

        sources = {}
        for name, config in data.get("data_sources", {}).items():
            sources[name] = DataSource(
                name=name,
                path=config["path"],
                schema_columns=tuple(config.get("schema_columns", [])),
                entity_type=config.get("entity_type", "all"),
                category=config.get("category", "fundamental"),
                update_freq=config.get("update_freq", "daily"),
                cache_ttl=config.get("cache_ttl", 3600),
            )
        return sources

    def _load_services(self, path: Path) -> dict[str, ServiceBinding]:
        """Load services from YAML."""
        if not path.exists():
            return {}

        with open(path) as f:
            data = yaml.safe_load(f)

        services = {}
        for name, config in data.get("services", {}).items():
            services[name] = ServiceBinding(
                service_name=name,
                service_path=config["service_path"],
                data_sources=config.get("data_sources", []),
                entity_type=config.get("entity_type", "all"),
                methods=config.get("methods", []),
            )
        return services

    def _load_pipelines(self, path: Path) -> dict[str, PipelineOutput]:
        """Load pipelines from YAML."""
        if not path.exists():
            return {}

        with open(path) as f:
            data = yaml.safe_load(f)

        pipelines = {}
        for name, config in data.get("pipelines", {}).items():
            pipelines[name] = PipelineOutput(
                pipeline_name=name,
                script_path=config["script_path"],
                outputs=config.get("outputs", []),
                dependencies=config.get("dependencies", []),
                schedule=config.get("schedule", "daily"),
            )
        return pipelines

    def _load_dashboards(self, path: Path) -> dict[str, DashboardConfig]:
        """Load dashboards from YAML."""
        if not path.exists():
            return {}

        with open(path) as f:
            data = yaml.safe_load(f)

        dashboards = {}
        for name, config in data.get("dashboards", {}).items():
            dashboards[name] = DashboardConfig(
                page_id=name,
                page_path=config["page_path"],
                data_sources=config.get("data_sources", []),
                services=config.get("services", []),
                cache_ttl=config.get("cache_ttl", 3600),
                requires_ticker=config.get("requires_ticker", False),
            )
        return dashboards

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    def get_path(self, source_name: str, data_root: str = "DATA") -> Path:
        """
        Get full path for a data source.

        Args:
            source_name: Name from data_sources.yaml (e.g., "bank_metrics")
            data_root: Data root directory

        Returns:
            Path object to the data file

        Raises:
            KeyError: If source_name not found
        """
        source = self._config.data_sources.get(source_name)
        if not source:
            raise KeyError(f"Unknown data source: {source_name}")
        return Path(data_root) / source.path

    def get_schema(self, source_name: str) -> tuple[str, ...]:
        """Get expected columns for a data source."""
        source = self._config.data_sources.get(source_name)
        if not source:
            raise KeyError(f"Unknown data source: {source_name}")
        return source.schema_columns

    def get_cache_ttl(self, source_name: str) -> int:
        """Get cache TTL for a data source."""
        source = self._config.data_sources.get(source_name)
        return source.cache_ttl if source else 3600

    def get_sources_for_service(self, service_name: str) -> list[DataSource]:
        """Get all data sources for a service."""
        return self._config.get_sources_for_service(service_name)

    def get_sources_for_dashboard(self, page_id: str) -> list[DataSource]:
        """Get all data sources for a dashboard page."""
        return self._config.get_sources_for_dashboard(page_id)

    def list_data_sources(self) -> list[str]:
        """List all registered data source names."""
        return list(self._config.data_sources.keys())

    def list_services(self) -> list[str]:
        """List all registered service names."""
        return list(self._config.services.keys())

    def list_pipelines(self) -> list[str]:
        """List all registered pipeline names."""
        return list(self._config.pipelines.keys())

    def list_dashboards(self) -> list[str]:
        """List all registered dashboard page IDs."""
        return list(self._config.dashboards.keys())

    def to_dict(self) -> dict:
        """Export config as dictionary (for JSON serialization)."""
        return {
            "version": self._config.version,
            "data_sources": {
                name: {
                    "path": ds.path,
                    "entity_type": ds.entity_type,
                    "category": ds.category,
                }
                for name, ds in self._config.data_sources.items()
            },
            "services": list(self._config.services.keys()),
            "pipelines": list(self._config.pipelines.keys()),
            "dashboards": list(self._config.dashboards.keys()),
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

@lru_cache(maxsize=1)
def get_registry() -> DataMappingRegistry:
    """Get singleton registry instance (cached)."""
    return DataMappingRegistry()


def get_data_path(source_name: str) -> Path:
    """Shortcut to get path for a data source."""
    return get_registry().get_path(source_name)
```

### Step 3: Create Resolvers

**File:** `config/data_mapping/resolver.py`

```python
"""
Path and Dependency Resolvers
=============================

PathResolver: Resolve data paths with validation
DependencyResolver: Build dependency graph for impact analysis
"""

from pathlib import Path
from typing import Optional
from .registry import DataMappingRegistry, get_registry


class PathResolver:
    """
    Resolves data paths with existence validation.

    Usage:
        resolver = PathResolver()
        path = resolver.resolve("bank_metrics")  # Returns Path or raises
        path = resolver.resolve_safe("bank_metrics")  # Returns Path or None
    """

    def __init__(self, registry: Optional[DataMappingRegistry] = None):
        self.registry = registry or get_registry()
        self._project_root = Path(__file__).resolve().parents[2]

    def resolve(self, source_name: str, validate: bool = True) -> Path:
        """
        Resolve path for data source.

        Args:
            source_name: Data source name
            validate: If True, verify file exists

        Returns:
            Absolute path to data file

        Raises:
            KeyError: Source not found
            FileNotFoundError: File doesn't exist (if validate=True)
        """
        relative_path = self.registry.get_path(source_name)
        absolute_path = self._project_root / relative_path

        if validate and not absolute_path.exists():
            raise FileNotFoundError(
                f"Data file not found: {absolute_path}\n"
                f"Source: {source_name}"
            )

        return absolute_path

    def resolve_safe(self, source_name: str) -> Optional[Path]:
        """Resolve path, return None if not found."""
        try:
            return self.resolve(source_name, validate=True)
        except (KeyError, FileNotFoundError):
            return None

    def validate_all(self) -> dict[str, bool]:
        """Validate all registered data sources exist."""
        results = {}
        for name in self.registry.list_data_sources():
            results[name] = self.resolve_safe(name) is not None
        return results


class DependencyResolver:
    """
    Builds dependency graph for impact analysis.

    Usage:
        resolver = DependencyResolver()
        downstream = resolver.get_downstream("ohlcv_raw")  # What depends on this?
        upstream = resolver.get_upstream("bank_metrics")   # What does this need?
    """

    def __init__(self, registry: Optional[DataMappingRegistry] = None):
        self.registry = registry or get_registry()
        self._build_graph()

    def _build_graph(self) -> None:
        """Build dependency graph from pipeline definitions."""
        # source -> list of pipelines that produce it
        self._producers: dict[str, list[str]] = {}

        # source -> list of pipelines that consume it
        self._consumers: dict[str, list[str]] = {}

        for pipeline_name in self.registry.list_pipelines():
            config = self.registry._config.pipelines[pipeline_name]

            # Track producers
            for output in config.outputs:
                if output not in self._producers:
                    self._producers[output] = []
                self._producers[output].append(pipeline_name)

            # Track consumers
            for dep in config.dependencies:
                if dep not in self._consumers:
                    self._consumers[dep] = []
                self._consumers[dep].append(pipeline_name)

    def get_upstream(self, source_name: str) -> list[str]:
        """
        Get upstream dependencies (what this source needs).

        Returns list of data source names that must exist for this source.
        """
        # Find pipeline that produces this source
        producers = self._producers.get(source_name, [])
        if not producers:
            return []

        # Get dependencies of that pipeline
        upstream = []
        for pipeline_name in producers:
            config = self.registry._config.pipelines[pipeline_name]
            upstream.extend(config.dependencies)

        return list(set(upstream))

    def get_downstream(self, source_name: str) -> list[str]:
        """
        Get downstream dependents (what depends on this source).

        Returns list of data source names that would break if this source changes.
        """
        # Find pipelines that consume this source
        consumers = self._consumers.get(source_name, [])
        if not consumers:
            return []

        # Get outputs of those pipelines
        downstream = []
        for pipeline_name in consumers:
            config = self.registry._config.pipelines[pipeline_name]
            downstream.extend(config.outputs)

        return list(set(downstream))

    def get_impact_chain(self, source_name: str) -> dict:
        """
        Get full impact analysis for a source.

        Returns dict with upstream, downstream, and affected services/dashboards.
        """
        downstream = self.get_downstream(source_name)

        # Find affected services
        affected_services = []
        for service_name in self.registry.list_services():
            sources = self.registry.get_sources_for_service(service_name)
            source_names = [s.name for s in sources]
            if source_name in source_names or any(d in source_names for d in downstream):
                affected_services.append(service_name)

        # Find affected dashboards
        affected_dashboards = []
        for page_id in self.registry.list_dashboards():
            sources = self.registry.get_sources_for_dashboard(page_id)
            source_names = [s.name for s in sources]
            if source_name in source_names or any(d in source_names for d in downstream):
                affected_dashboards.append(page_id)

        return {
            "source": source_name,
            "upstream": self.get_upstream(source_name),
            "downstream": downstream,
            "affected_services": affected_services,
            "affected_dashboards": affected_dashboards,
        }
```

### Step 4: Update __init__.py

**File:** `config/data_mapping/__init__.py`

```python
"""
Data Mapping - Centralized Data Flow Configuration
===================================================

Provides:
- DataMappingRegistry: Load YAML configs, lookup paths/schemas
- PathResolver: Resolve paths with validation
- DependencyResolver: Impact analysis for data changes

Usage:
    from config.data_mapping import get_registry, get_data_path

    # Get path by source name
    path = get_data_path("bank_metrics")

    # Get registry for advanced lookups
    registry = get_registry()
    sources = registry.get_sources_for_service("BankService")
"""

from .entities import (
    DataSource,
    PipelineOutput,
    DashboardConfig,
    ServiceBinding,
    DataMappingConfig,
)
from .registry import (
    DataMappingRegistry,
    get_registry,
    get_data_path,
)
from .resolver import (
    PathResolver,
    DependencyResolver,
)

__all__ = [
    # Entities
    'DataSource',
    'PipelineOutput',
    'DashboardConfig',
    'ServiceBinding',
    'DataMappingConfig',
    # Registry
    'DataMappingRegistry',
    'get_registry',
    'get_data_path',
    # Resolvers
    'PathResolver',
    'DependencyResolver',
]
```

## Success Criteria

- [ ] All 4 YAML configs created and valid
- [ ] `DataMappingRegistry` loads configs on first access
- [ ] `get_data_path("bank_metrics")` returns correct path
- [ ] `PathResolver.validate_all()` shows file existence status
- [ ] `DependencyResolver.get_impact_chain("ohlcv_raw")` shows affected services

## Test Script

```python
# tests/test_data_mapping_registry.py
from config.data_mapping import get_registry, get_data_path, PathResolver, DependencyResolver

def test_registry_loads():
    registry = get_registry()
    assert len(registry.list_data_sources()) > 0
    assert "bank_metrics" in registry.list_data_sources()

def test_path_resolution():
    path = get_data_path("bank_metrics")
    assert "bank_financial_metrics.parquet" in str(path)

def test_schema_lookup():
    registry = get_registry()
    schema = registry.get_schema("bank_metrics")
    assert "symbol" in schema
    assert "nim" in schema

def test_dependency_resolver():
    resolver = DependencyResolver()
    impact = resolver.get_impact_chain("ohlcv_raw")
    assert "downstream" in impact
    assert "affected_services" in impact
```
