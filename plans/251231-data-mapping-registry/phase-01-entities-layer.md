# Phase 1: Entities Layer (Core Domain)

**Est. Time:** 2 hours | **Priority:** High | **Dependencies:** None

## Context

Need type-safe dataclasses representing data mappings. These are pure domain objects with no external dependencies - innermost layer of Clean Architecture.

## Overview

Create core dataclasses in `config/data_mapping/entities.py`:
- `PipelineOutput` - Pipeline → output files mapping
- `DataSource` - File path + schema + metadata
- `DashboardConfig` - Dashboard → data sources mapping
- `ServiceBinding` - Service → data files mapping

## Requirements

1. Python dataclasses with Pydantic validation
2. Immutable where possible (frozen=True)
3. Type hints for all fields
4. Sensible defaults for optional fields
5. Version field for schema evolution

## Architecture

```python
# Core Entities (no external dependencies)
@dataclass(frozen=True)
class DataSource:
    """Represents a single data file with metadata."""
    path: str           # Relative to DATA/
    schema: list[str]   # Expected columns
    entity_type: str    # "bank" | "company" | "insurance" | "security"
    update_freq: str    # "daily" | "quarterly" | "yearly"
    cache_ttl: int      # Seconds

@dataclass
class PipelineOutput:
    """Maps pipeline to its output files."""
    pipeline_name: str
    outputs: list[DataSource]
    processors: list[str]
    version: str = "1.0"

@dataclass
class DashboardConfig:
    """Maps dashboard page to required data sources."""
    page_id: str
    data_sources: list[str]  # References DataSource paths
    refresh_freq: str = "daily"
    cache_ttl: int = 3600

@dataclass
class ServiceBinding:
    """Maps service to data files it consumes."""
    service_name: str
    data_sources: list[str]  # References DataSource paths
    entity_type: str
```

## Implementation Steps

### Step 1: Create entities module

**File:** `config/data_mapping/__init__.py`
```python
"""Data Mapping - Centralized data flow configuration."""
from .entities import (
    DataSource,
    PipelineOutput,
    DashboardConfig,
    ServiceBinding,
)

__all__ = [
    'DataSource',
    'PipelineOutput',
    'DashboardConfig',
    'ServiceBinding',
]
```

### Step 2: Define core dataclasses

**File:** `config/data_mapping/entities.py`

```python
"""
Core Domain Entities for Data Mapping
=====================================

Pure dataclasses with Pydantic validation.
No external dependencies - innermost Clean Architecture layer.
"""

from dataclasses import dataclass, field
from typing import Literal
from pydantic import BaseModel, field_validator

# ============================================================================
# ENUMS/LITERALS
# ============================================================================

EntityType = Literal["bank", "company", "insurance", "security", "all"]
UpdateFrequency = Literal["realtime", "daily", "weekly", "quarterly", "yearly"]
DataCategory = Literal["fundamental", "technical", "valuation", "macro", "forecast"]

# ============================================================================
# CORE ENTITIES
# ============================================================================

@dataclass(frozen=True)
class DataSource:
    """
    Represents a single data file with metadata.

    Attributes:
        name: Unique identifier (e.g., "bank_metrics", "pe_historical")
        path: Path relative to DATA/ (e.g., "processed/fundamental/bank/...")
        schema_columns: Expected columns in the file
        entity_type: Which entity this data belongs to
        category: Data category for grouping
        update_freq: How often the data updates
        cache_ttl: Cache time-to-live in seconds
    """
    name: str
    path: str
    schema_columns: tuple[str, ...]  # Immutable
    entity_type: EntityType
    category: DataCategory
    update_freq: UpdateFrequency = "daily"
    cache_ttl: int = 3600

    def full_path(self, data_root: str = "DATA") -> str:
        """Get full path from data root."""
        return f"{data_root}/{self.path}"


@dataclass
class PipelineOutput:
    """
    Maps a processing pipeline to its output files.

    Attributes:
        pipeline_name: Unique pipeline identifier
        script_path: Path to pipeline script
        outputs: List of DataSource names this pipeline produces
        dependencies: List of input DataSource names
        schedule: Cron expression or frequency
        version: Schema version for evolution tracking
    """
    pipeline_name: str
    script_path: str
    outputs: list[str]  # DataSource names
    dependencies: list[str] = field(default_factory=list)
    schedule: str = "daily"
    version: str = "1.0"


@dataclass
class DashboardConfig:
    """
    Maps a dashboard page to its required data sources.

    Attributes:
        page_id: Unique page identifier (matches Streamlit page name)
        page_path: Path to Streamlit page file
        data_sources: List of DataSource names required
        services: List of Service names to use
        cache_ttl: Override cache TTL for this page
        requires_ticker: Whether page needs ticker selection
    """
    page_id: str
    page_path: str
    data_sources: list[str]  # DataSource names
    services: list[str] = field(default_factory=list)
    cache_ttl: int = 3600
    requires_ticker: bool = False


@dataclass
class ServiceBinding:
    """
    Maps a service class to the data files it consumes.

    Attributes:
        service_name: Class name (e.g., "BankService", "CompanyService")
        service_path: Module path (e.g., "WEBAPP.services.bank_service")
        data_sources: List of DataSource names consumed
        entity_type: Primary entity type served
        methods: List of public method names
    """
    service_name: str
    service_path: str
    data_sources: list[str]  # DataSource names
    entity_type: EntityType
    methods: list[str] = field(default_factory=list)


# ============================================================================
# AGGREGATE ROOT
# ============================================================================

@dataclass
class DataMappingConfig:
    """
    Root configuration aggregating all mappings.

    This is the complete data flow definition loaded from YAML.
    """
    data_sources: dict[str, DataSource]
    pipelines: dict[str, PipelineOutput]
    dashboards: dict[str, DashboardConfig]
    services: dict[str, ServiceBinding]
    version: str = "1.0"

    def get_data_source(self, name: str) -> DataSource | None:
        """Get data source by name."""
        return self.data_sources.get(name)

    def get_sources_for_service(self, service_name: str) -> list[DataSource]:
        """Get all data sources for a service."""
        binding = self.services.get(service_name)
        if not binding:
            return []
        return [
            self.data_sources[name]
            for name in binding.data_sources
            if name in self.data_sources
        ]

    def get_sources_for_dashboard(self, page_id: str) -> list[DataSource]:
        """Get all data sources for a dashboard page."""
        config = self.dashboards.get(page_id)
        if not config:
            return []
        return [
            self.data_sources[name]
            for name in config.data_sources
            if name in self.data_sources
        ]
```

### Step 3: Add Pydantic validators (optional strictness)

**File:** `config/data_mapping/validators.py` (stub for Phase 4)

```python
"""Pydantic validators for YAML loading - implemented in Phase 4."""
pass
```

## Success Criteria

- [ ] All dataclasses defined with type hints
- [ ] Import works: `from config.data_mapping import DataSource, PipelineOutput`
- [ ] Frozen dataclasses are immutable
- [ ] `DataMappingConfig` aggregates all entities
- [ ] Unit test passes for dataclass instantiation

## Test Script

```python
# tests/test_data_mapping_entities.py
from config.data_mapping import DataSource, PipelineOutput, DashboardConfig

def test_data_source_creation():
    ds = DataSource(
        name="bank_metrics",
        path="processed/fundamental/bank/bank_financial_metrics.parquet",
        schema_columns=("symbol", "report_date", "nim", "npl_ratio"),
        entity_type="bank",
        category="fundamental"
    )
    assert ds.name == "bank_metrics"
    assert ds.full_path() == "DATA/processed/fundamental/bank/bank_financial_metrics.parquet"

def test_immutability():
    ds = DataSource(name="test", path="test", schema_columns=(), entity_type="bank", category="fundamental")
    try:
        ds.name = "changed"  # Should raise FrozenInstanceError
        assert False
    except:
        assert True
```

## Notes

- Keep entities pure - no file I/O, no external dependencies
- Pydantic validation added in Phase 4 for YAML loading
- Schema columns as tuple (immutable) rather than list
