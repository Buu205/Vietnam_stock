"""
Data Mapping - Centralized Data Flow Configuration
===================================================

Clean Architecture registry for mapping:
- Pipeline → Output files
- Data files → Schema + metadata
- Dashboard → Data sources
- Service → Data files

Usage:
    from config.data_mapping import get_registry, get_data_path

    # Get path by source name
    path = get_data_path("bank_metrics")

    # Get registry for advanced lookups
    registry = get_registry()
    sources = registry.get_sources_for_service("BankService")

    # Dependency analysis
    from config.data_mapping import DependencyResolver
    resolver = DependencyResolver()
    impact = resolver.get_impact_chain("ohlcv_raw")

Author: AI Assistant
Date: 2025-12-31
Version: 1.0.0
"""

from .entities import (
    DataSource,
    PipelineOutput,
    DashboardConfig,
    ServiceBinding,
    DataMappingConfig,
    EntityType,
    UpdateFrequency,
    DataCategory,
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
    HealthChecker,
    ValidationResult,
    HealthStatus,
)

__all__ = [
    # Type aliases
    'EntityType',
    'UpdateFrequency',
    'DataCategory',
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
    'HealthChecker',
    'ValidationResult',
    'HealthStatus',
]
