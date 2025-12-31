# Phase 4: Validation Layer

**Est. Time:** 2 hours | **Priority:** Medium | **Dependencies:** Phase 3 complete

## Context

Add schema validation, config validation, and dependency checks. Catches errors early before runtime failures.

## Overview

1. Pydantic models for YAML config validation
2. Schema validator for parquet files
3. Dependency validator for missing sources
4. Health check endpoint for dashboards

## Requirements

1. Validate YAML configs at load time
2. Validate parquet schemas before component render
3. Report missing dependencies before pipeline runs
4. Provide health check for dashboard data availability

## Architecture

```
config/data_mapping/
├── entities.py      # Phase 1
├── registry.py      # Phase 2
├── resolver.py      # Phase 2
├── validator.py     # NEW: Validation layer
└── health.py        # NEW: Health checks
```

## Implementation Steps

### Step 1: Pydantic Config Models

**File:** `config/data_mapping/validator.py`

```python
"""
Validation Layer
================

Pydantic models for YAML config validation.
Schema validation for parquet files.
Dependency validation for data sources.
"""

from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC CONFIG MODELS (YAML Validation)
# ============================================================================

class DataSourceConfig(BaseModel):
    """Validates data source config from YAML."""
    path: str
    schema_columns: list[str]
    entity_type: str
    category: str
    update_freq: str = "daily"
    cache_ttl: int = 3600

    @field_validator('entity_type')
    @classmethod
    def validate_entity_type(cls, v: str) -> str:
        valid = {"bank", "company", "insurance", "security", "all"}
        if v not in valid:
            raise ValueError(f"entity_type must be one of {valid}")
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        valid = {"fundamental", "technical", "valuation", "macro", "forecast"}
        if v not in valid:
            raise ValueError(f"category must be one of {valid}")
        return v

    @field_validator('update_freq')
    @classmethod
    def validate_update_freq(cls, v: str) -> str:
        valid = {"realtime", "daily", "weekly", "quarterly", "yearly"}
        if v not in valid:
            raise ValueError(f"update_freq must be one of {valid}")
        return v


class ServiceConfig(BaseModel):
    """Validates service config from YAML."""
    service_path: str
    data_sources: list[str]
    entity_type: str
    methods: list[str] = []


class PipelineConfig(BaseModel):
    """Validates pipeline config from YAML."""
    script_path: str
    outputs: list[str]
    dependencies: list[str] = []
    schedule: str = "daily"


class DashboardPageConfig(BaseModel):
    """Validates dashboard config from YAML."""
    page_path: str
    data_sources: list[str]
    services: list[str] = []
    requires_ticker: bool = False
    cache_ttl: int = 3600


# ============================================================================
# SCHEMA VALIDATOR
# ============================================================================

class SchemaValidator:
    """
    Validates parquet file schemas against expected columns.

    Usage:
        validator = SchemaValidator()
        result = validator.validate("bank_metrics")
        if not result.valid:
            print(f"Missing: {result.missing_columns}")
    """

    def __init__(self, registry=None):
        if registry is None:
            from .registry import get_registry
            registry = get_registry()
        self.registry = registry

    def validate(self, source_name: str) -> "ValidationResult":
        """
        Validate a data source's parquet schema.

        Args:
            source_name: Name from data_sources.yaml

        Returns:
            ValidationResult with status and details
        """
        try:
            # Get expected schema
            expected = set(self.registry.get_schema(source_name))

            # Get actual schema from file
            from .resolver import PathResolver
            resolver = PathResolver(self.registry)
            path = resolver.resolve(source_name, validate=True)

            # Read parquet metadata only (efficient)
            actual = set(pd.read_parquet(path, columns=[]).columns.tolist())

            missing = expected - actual
            extra = actual - expected

            return ValidationResult(
                source_name=source_name,
                valid=len(missing) == 0,
                missing_columns=list(missing),
                extra_columns=list(extra),
                expected_count=len(expected),
                actual_count=len(actual),
            )

        except FileNotFoundError as e:
            return ValidationResult(
                source_name=source_name,
                valid=False,
                error=str(e),
            )
        except Exception as e:
            return ValidationResult(
                source_name=source_name,
                valid=False,
                error=f"Unexpected error: {e}",
            )

    def validate_all(self) -> list["ValidationResult"]:
        """Validate all registered data sources."""
        results = []
        for name in self.registry.list_data_sources():
            results.append(self.validate(name))
        return results


class ValidationResult(BaseModel):
    """Result of schema validation."""
    source_name: str
    valid: bool
    missing_columns: list[str] = []
    extra_columns: list[str] = []
    expected_count: int = 0
    actual_count: int = 0
    error: Optional[str] = None


# ============================================================================
# DEPENDENCY VALIDATOR
# ============================================================================

class DependencyValidator:
    """
    Validates data source dependencies are available.

    Usage:
        validator = DependencyValidator()
        result = validator.validate_pipeline("bank_calculator")
    """

    def __init__(self, registry=None):
        if registry is None:
            from .registry import get_registry
            registry = get_registry()
        self.registry = registry

    def validate_pipeline(self, pipeline_name: str) -> dict:
        """
        Check if pipeline dependencies exist.

        Returns:
            dict with status and missing dependencies
        """
        from .resolver import PathResolver
        resolver = PathResolver(self.registry)

        pipeline = self.registry._config.pipelines.get(pipeline_name)
        if not pipeline:
            return {
                "pipeline": pipeline_name,
                "valid": False,
                "error": "Pipeline not found in registry",
            }

        missing = []
        for dep in pipeline.dependencies:
            path = resolver.resolve_safe(dep)
            if path is None:
                missing.append(dep)

        return {
            "pipeline": pipeline_name,
            "valid": len(missing) == 0,
            "missing_dependencies": missing,
            "total_dependencies": len(pipeline.dependencies),
        }

    def validate_service(self, service_name: str) -> dict:
        """Check if service data sources exist."""
        from .resolver import PathResolver
        resolver = PathResolver(self.registry)

        service = self.registry._config.services.get(service_name)
        if not service:
            return {
                "service": service_name,
                "valid": False,
                "error": "Service not found in registry",
            }

        missing = []
        for source in service.data_sources:
            path = resolver.resolve_safe(source)
            if path is None:
                missing.append(source)

        return {
            "service": service_name,
            "valid": len(missing) == 0,
            "missing_sources": missing,
            "total_sources": len(service.data_sources),
        }

    def validate_dashboard(self, page_id: str) -> dict:
        """Check if dashboard data sources exist."""
        from .resolver import PathResolver
        resolver = PathResolver(self.registry)

        dashboard = self.registry._config.dashboards.get(page_id)
        if not dashboard:
            return {
                "dashboard": page_id,
                "valid": False,
                "error": "Dashboard not found in registry",
            }

        missing = []
        for source in dashboard.data_sources:
            path = resolver.resolve_safe(source)
            if path is None:
                missing.append(source)

        return {
            "dashboard": page_id,
            "valid": len(missing) == 0,
            "missing_sources": missing,
            "total_sources": len(dashboard.data_sources),
        }


# ============================================================================
# CONFIG VALIDATOR
# ============================================================================

class ConfigValidator:
    """
    Validates YAML config files at load time.

    Usage:
        validator = ConfigValidator()
        errors = validator.validate_configs()
        if errors:
            print(f"Config errors: {errors}")
    """

    def validate_configs(self) -> list[str]:
        """
        Validate all YAML configs.

        Returns:
            List of error messages (empty if valid)
        """
        import yaml
        from pathlib import Path

        errors = []
        config_dir = Path(__file__).parent / "configs"

        # Validate data_sources.yaml
        ds_file = config_dir / "data_sources.yaml"
        if ds_file.exists():
            with open(ds_file) as f:
                data = yaml.safe_load(f)
            for name, config in data.get("data_sources", {}).items():
                try:
                    DataSourceConfig(**config)
                except Exception as e:
                    errors.append(f"data_sources.{name}: {e}")

        # Validate services.yaml
        svc_file = config_dir / "services.yaml"
        if svc_file.exists():
            with open(svc_file) as f:
                data = yaml.safe_load(f)
            for name, config in data.get("services", {}).items():
                try:
                    ServiceConfig(**config)
                except Exception as e:
                    errors.append(f"services.{name}: {e}")

        # Validate pipelines.yaml
        pipe_file = config_dir / "pipelines.yaml"
        if pipe_file.exists():
            with open(pipe_file) as f:
                data = yaml.safe_load(f)
            for name, config in data.get("pipelines", {}).items():
                try:
                    PipelineConfig(**config)
                except Exception as e:
                    errors.append(f"pipelines.{name}: {e}")

        # Validate dashboards.yaml
        dash_file = config_dir / "dashboards.yaml"
        if dash_file.exists():
            with open(dash_file) as f:
                data = yaml.safe_load(f)
            for name, config in data.get("dashboards", {}).items():
                try:
                    DashboardPageConfig(**config)
                except Exception as e:
                    errors.append(f"dashboards.{name}: {e}")

        return errors
```

### Step 2: Health Check Module

**File:** `config/data_mapping/health.py`

```python
"""
Health Check Module
===================

Provides health status for dashboards and services.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class HealthStatus:
    """Health check result."""
    name: str
    healthy: bool
    message: str
    last_checked: datetime
    details: Optional[dict] = None


class HealthChecker:
    """
    Check health of data sources, services, and dashboards.

    Usage:
        checker = HealthChecker()
        status = checker.check_dashboard("bank_analysis")
        if not status.healthy:
            st.warning(status.message)
    """

    def __init__(self, registry=None):
        if registry is None:
            from .registry import get_registry
            registry = get_registry()
        self.registry = registry

    def check_data_source(self, source_name: str) -> HealthStatus:
        """Check if data source file exists and is recent."""
        from .resolver import PathResolver
        resolver = PathResolver(self.registry)

        try:
            path = resolver.resolve(source_name, validate=True)

            # Check file age
            import os
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            age_hours = (datetime.now() - mtime).total_seconds() / 3600

            # Get expected update frequency
            source = self.registry._config.data_sources.get(source_name)
            update_freq = source.update_freq if source else "daily"

            # Determine if stale
            max_age = {
                "realtime": 1,
                "daily": 25,
                "weekly": 170,
                "quarterly": 2200,
                "yearly": 8800,
            }.get(update_freq, 25)

            if age_hours > max_age:
                return HealthStatus(
                    name=source_name,
                    healthy=False,
                    message=f"Data stale: {age_hours:.1f}h old (max {max_age}h)",
                    last_checked=datetime.now(),
                    details={"file_age_hours": age_hours, "max_age_hours": max_age},
                )

            return HealthStatus(
                name=source_name,
                healthy=True,
                message=f"OK ({age_hours:.1f}h old)",
                last_checked=datetime.now(),
                details={"file_age_hours": age_hours},
            )

        except FileNotFoundError:
            return HealthStatus(
                name=source_name,
                healthy=False,
                message="File not found",
                last_checked=datetime.now(),
            )
        except Exception as e:
            return HealthStatus(
                name=source_name,
                healthy=False,
                message=f"Error: {e}",
                last_checked=datetime.now(),
            )

    def check_service(self, service_name: str) -> HealthStatus:
        """Check if service's data sources are healthy."""
        sources = self.registry.get_sources_for_service(service_name)

        if not sources:
            return HealthStatus(
                name=service_name,
                healthy=False,
                message="No data sources configured",
                last_checked=datetime.now(),
            )

        unhealthy = []
        for source in sources:
            status = self.check_data_source(source.name)
            if not status.healthy:
                unhealthy.append(source.name)

        if unhealthy:
            return HealthStatus(
                name=service_name,
                healthy=False,
                message=f"Unhealthy sources: {unhealthy}",
                last_checked=datetime.now(),
                details={"unhealthy_sources": unhealthy},
            )

        return HealthStatus(
            name=service_name,
            healthy=True,
            message=f"All {len(sources)} sources healthy",
            last_checked=datetime.now(),
        )

    def check_dashboard(self, page_id: str) -> HealthStatus:
        """Check if dashboard's data sources are healthy."""
        sources = self.registry.get_sources_for_dashboard(page_id)

        if not sources:
            return HealthStatus(
                name=page_id,
                healthy=False,
                message="No data sources configured",
                last_checked=datetime.now(),
            )

        unhealthy = []
        for source in sources:
            status = self.check_data_source(source.name)
            if not status.healthy:
                unhealthy.append(source.name)

        if unhealthy:
            return HealthStatus(
                name=page_id,
                healthy=False,
                message=f"Unhealthy sources: {unhealthy}",
                last_checked=datetime.now(),
                details={"unhealthy_sources": unhealthy},
            )

        return HealthStatus(
            name=page_id,
            healthy=True,
            message=f"All {len(sources)} sources healthy",
            last_checked=datetime.now(),
        )

    def check_all(self) -> dict:
        """Run health checks on all components."""
        results = {
            "data_sources": {},
            "services": {},
            "dashboards": {},
            "overall": True,
        }

        # Check data sources
        for name in self.registry.list_data_sources():
            status = self.check_data_source(name)
            results["data_sources"][name] = status.healthy
            if not status.healthy:
                results["overall"] = False

        # Check services
        for name in self.registry.list_services():
            status = self.check_service(name)
            results["services"][name] = status.healthy
            if not status.healthy:
                results["overall"] = False

        # Check dashboards
        for name in self.registry.list_dashboards():
            status = self.check_dashboard(name)
            results["dashboards"][name] = status.healthy
            if not status.healthy:
                results["overall"] = False

        return results
```

### Step 3: Update __init__.py

**File:** `config/data_mapping/__init__.py` (UPDATED)

```python
"""
Data Mapping - Centralized Data Flow Configuration
===================================================
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
from .validator import (
    SchemaValidator,
    DependencyValidator,
    ConfigValidator,
    ValidationResult,
)
from .health import (
    HealthChecker,
    HealthStatus,
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
    # Validators
    'SchemaValidator',
    'DependencyValidator',
    'ConfigValidator',
    'ValidationResult',
    # Health
    'HealthChecker',
    'HealthStatus',
]
```

### Step 4: CLI Validation Script

**File:** `scripts/validate_data_mapping.py`

```python
#!/usr/bin/env python3
"""
Validate Data Mapping Configuration
====================================

Run before deployment to catch config errors.

Usage:
    python scripts/validate_data_mapping.py
    python scripts/validate_data_mapping.py --verbose
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.data_mapping import (
    ConfigValidator,
    SchemaValidator,
    DependencyValidator,
    HealthChecker,
)


def main(verbose: bool = False):
    print("=" * 60)
    print("DATA MAPPING VALIDATION")
    print("=" * 60)

    errors = []

    # 1. Validate YAML configs
    print("\n[1] Validating YAML configs...")
    config_validator = ConfigValidator()
    config_errors = config_validator.validate_configs()
    if config_errors:
        errors.extend(config_errors)
        for e in config_errors:
            print(f"  ERROR: {e}")
    else:
        print("  OK: All configs valid")

    # 2. Validate schemas
    print("\n[2] Validating parquet schemas...")
    schema_validator = SchemaValidator()
    results = schema_validator.validate_all()
    for r in results:
        if not r.valid:
            msg = f"Schema mismatch: {r.source_name} - missing {r.missing_columns}"
            errors.append(msg)
            print(f"  WARN: {msg}")
        elif verbose:
            print(f"  OK: {r.source_name}")

    if all(r.valid for r in results):
        print("  OK: All schemas valid")

    # 3. Validate dependencies
    print("\n[3] Validating dependencies...")
    dep_validator = DependencyValidator()
    from config.data_mapping import get_registry
    registry = get_registry()

    for service in registry.list_services():
        result = dep_validator.validate_service(service)
        if not result["valid"]:
            msg = f"Service {service} missing: {result['missing_sources']}"
            errors.append(msg)
            print(f"  WARN: {msg}")
        elif verbose:
            print(f"  OK: {service}")

    # 4. Health checks
    print("\n[4] Running health checks...")
    checker = HealthChecker()
    health = checker.check_all()

    unhealthy_count = sum(1 for v in health["data_sources"].values() if not v)
    print(f"  Data sources: {len(health['data_sources']) - unhealthy_count}/{len(health['data_sources'])} healthy")

    # Summary
    print("\n" + "=" * 60)
    if errors:
        print(f"VALIDATION FAILED: {len(errors)} error(s)")
        sys.exit(1)
    else:
        print("VALIDATION PASSED")
        sys.exit(0)


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    main(verbose)
```

## Success Criteria

- [ ] ConfigValidator catches invalid YAML on load
- [ ] SchemaValidator reports missing columns
- [ ] DependencyValidator shows missing data sources
- [ ] HealthChecker reports stale data
- [ ] `python scripts/validate_data_mapping.py` runs without errors

## Test Script

```python
# tests/test_validation.py
from config.data_mapping import ConfigValidator, SchemaValidator, HealthChecker

def test_config_validator():
    validator = ConfigValidator()
    errors = validator.validate_configs()
    # Should be empty if configs are valid
    assert isinstance(errors, list)

def test_schema_validator():
    validator = SchemaValidator()
    result = validator.validate("bank_metrics")
    assert result.source_name == "bank_metrics"
    assert isinstance(result.valid, bool)

def test_health_checker():
    checker = HealthChecker()
    status = checker.check_data_source("bank_metrics")
    assert status.name == "bank_metrics"
    assert isinstance(status.healthy, bool)
```

## Integration with Streamlit

Add health banner to dashboard pages:

```python
# WEBAPP/pages/bank_analysis.py
import streamlit as st
from config.data_mapping import HealthChecker

def show_health_banner():
    checker = HealthChecker()
    status = checker.check_dashboard("bank_analysis")

    if not status.healthy:
        st.warning(f"Data may be stale: {status.message}")

# At top of page
show_health_banner()
```
