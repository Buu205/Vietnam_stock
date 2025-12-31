"""
Data Mapping Registry
=====================

Singleton registry loading YAML configs into entities.
Provides lookup methods for paths, schemas, dependencies.

Usage:
    from config.data_mapping import get_registry, get_data_path

    registry = get_registry()
    path = registry.get_path("bank_metrics")

Author: AI Assistant
Date: 2025-12-31
Version: 1.0.0
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

        with open(path, encoding='utf-8') as f:
            data = yaml.safe_load(f)

        sources = {}
        for name, config in data.get("data_sources", {}).items():
            derived = config.get("derived_from", [])
            sources[name] = DataSource(
                name=name,
                path=config["path"],
                schema_columns=tuple(config.get("schema_columns", [])),
                entity_type=config.get("entity_type", "all"),
                category=config.get("category", "fundamental"),
                update_freq=config.get("update_freq", "daily"),
                cache_ttl=config.get("cache_ttl", 3600),
                derived_from=tuple(derived) if derived else (),
            )
        return sources

    def _load_services(self, path: Path) -> dict[str, ServiceBinding]:
        """Load services from YAML."""
        if not path.exists():
            return {}

        with open(path, encoding='utf-8') as f:
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

        with open(path, encoding='utf-8') as f:
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

        with open(path, encoding='utf-8') as f:
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
            available = list(self._config.data_sources.keys())
            raise KeyError(
                f"Unknown data source: '{source_name}'. "
                f"Available: {available[:10]}..."
            )
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

    def get_data_source(self, source_name: str) -> DataSource | None:
        """Get DataSource entity by name."""
        return self._config.data_sources.get(source_name)

    def get_sources_for_service(self, service_name: str) -> list[DataSource]:
        """Get all data sources for a service."""
        return self._config.get_sources_for_service(service_name)

    def get_sources_for_dashboard(self, page_id: str) -> list[DataSource]:
        """Get all data sources for a dashboard page."""
        return self._config.get_sources_for_dashboard(page_id)

    def get_pipeline(self, pipeline_name: str) -> PipelineOutput | None:
        """Get pipeline config by name."""
        return self._config.pipelines.get(pipeline_name)

    def get_dashboard(self, page_id: str) -> DashboardConfig | None:
        """Get dashboard config by page ID."""
        return self._config.dashboards.get(page_id)

    def get_service(self, service_name: str) -> ServiceBinding | None:
        """Get service binding by name."""
        return self._config.services.get(service_name)

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
                    "cache_ttl": ds.cache_ttl,
                }
                for name, ds in self._config.data_sources.items()
            },
            "services": list(self._config.services.keys()),
            "pipelines": list(self._config.pipelines.keys()),
            "dashboards": list(self._config.dashboards.keys()),
        }

    @property
    def config(self) -> DataMappingConfig:
        """Access raw config (for advanced usage)."""
        return self._config


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

@lru_cache(maxsize=1)
def get_registry() -> DataMappingRegistry:
    """Get singleton registry instance (cached)."""
    return DataMappingRegistry()


def get_data_path(source_name: str, data_root: str = "DATA") -> Path:
    """Shortcut to get path for a data source."""
    return get_registry().get_path(source_name, data_root)
