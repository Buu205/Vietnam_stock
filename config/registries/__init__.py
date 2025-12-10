"""
Registry System - Central Lookup Utilities
==========================================

Provides fast lookup utilities for:
- MetricRegistry: Financial metrics (BSC codes → Vietnamese/English names)
- SectorRegistry: Ticker → Sector/Industry mappings
- SchemaRegistry: Schema management (in config/schema_registry.py)

Usage:
    from config.registries import MetricRegistry, SectorRegistry
    from config.schema_registry import SchemaRegistry

    metric_reg = MetricRegistry()
    sector_reg = SectorRegistry()
    schema_reg = SchemaRegistry()

Moved from PROCESSORS/core/registries/ to config/registries/ (2025-12-10)
Rationale: Registries are configuration/metadata, not processing logic
"""

from .metric_lookup import MetricRegistry, get_registry as get_metric_registry
from .sector_lookup import SectorRegistry

__all__ = [
    'MetricRegistry',
    'SectorRegistry',
    'get_metric_registry',
]
