"""
Core Domain Entities for Data Mapping
=====================================

Pure dataclasses representing data flow configuration.
No external dependencies - innermost Clean Architecture layer.

Author: AI Assistant
Date: 2025-12-31
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Literal

# ============================================================================
# TYPE ALIASES
# ============================================================================

EntityType = Literal["bank", "company", "insurance", "security", "all"]
UpdateFrequency = Literal["realtime", "daily", "weekly", "quarterly", "yearly"]
DataCategory = Literal["fundamental", "technical", "valuation", "macro", "forecast", "sector"]

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
        schema_columns: Expected columns in the file (immutable tuple)
        entity_type: Which entity this data belongs to
        category: Data category for grouping
        update_freq: How often the data updates
        cache_ttl: Cache time-to-live in seconds
        derived_from: List of source names this is derived from (cross-pipeline)
    """
    name: str
    path: str
    schema_columns: tuple[str, ...]
    entity_type: EntityType
    category: DataCategory
    update_freq: UpdateFrequency = "daily"
    cache_ttl: int = 3600
    derived_from: tuple[str, ...] = ()

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
        dependencies: List of input DataSource names required
        schedule: Cron expression or frequency
        version: Schema version for evolution tracking
    """
    pipeline_name: str
    script_path: str
    outputs: list[str] = field(default_factory=list)
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
    data_sources: list[str] = field(default_factory=list)
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
    data_sources: list[str] = field(default_factory=list)
    entity_type: EntityType = "all"
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
    data_sources: dict[str, DataSource] = field(default_factory=dict)
    pipelines: dict[str, PipelineOutput] = field(default_factory=dict)
    dashboards: dict[str, DashboardConfig] = field(default_factory=dict)
    services: dict[str, ServiceBinding] = field(default_factory=dict)
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

    def get_pipeline_for_output(self, output_name: str) -> PipelineOutput | None:
        """Find pipeline that produces a given output."""
        for pipeline in self.pipelines.values():
            if output_name in pipeline.outputs:
                return pipeline
        return None
