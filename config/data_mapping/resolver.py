"""
Path and Dependency Resolvers
=============================

PathResolver: Resolve data paths with validation
DependencyResolver: Build dependency graph for impact analysis

Usage:
    from config.data_mapping import PathResolver, DependencyResolver

    # Path resolution
    resolver = PathResolver()
    path = resolver.resolve("bank_metrics")
    validation = resolver.validate_all()

    # Dependency analysis
    dep_resolver = DependencyResolver()
    impact = dep_resolver.get_impact_chain("ohlcv_raw")

Author: AI Assistant
Date: 2025-12-31
Version: 1.0.0
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

    def get_missing_sources(self) -> list[str]:
        """Get list of data sources with missing files."""
        validation = self.validate_all()
        return [name for name, exists in validation.items() if not exists]

    def get_existing_sources(self) -> list[str]:
        """Get list of data sources with existing files."""
        validation = self.validate_all()
        return [name for name, exists in validation.items() if exists]


class DependencyResolver:
    """
    Builds dependency graph for impact analysis.

    Usage:
        resolver = DependencyResolver()
        downstream = resolver.get_downstream("ohlcv_raw")  # What depends on this?
        upstream = resolver.get_upstream("bank_metrics")   # What does this need?
        order = resolver.get_execution_order("sector_valuation")  # Topological sort
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
            pipeline = self.registry.get_pipeline(pipeline_name)
            if not pipeline:
                continue

            # Track producers
            for output in pipeline.outputs:
                if output not in self._producers:
                    self._producers[output] = []
                self._producers[output].append(pipeline_name)

            # Track consumers
            for dep in pipeline.dependencies:
                if dep not in self._consumers:
                    self._consumers[dep] = []
                self._consumers[dep].append(pipeline_name)

    def get_upstream(self, source_name: str) -> list[str]:
        """
        Get upstream dependencies (what this source needs).

        Returns list of data source names that must exist for this source.
        """
        # Check derived_from field first
        source = self.registry.get_data_source(source_name)
        if source and source.derived_from:
            return list(source.derived_from)

        # Find pipeline that produces this source
        producers = self._producers.get(source_name, [])
        if not producers:
            return []

        # Get dependencies of that pipeline
        upstream = []
        for pipeline_name in producers:
            pipeline = self.registry.get_pipeline(pipeline_name)
            if pipeline:
                upstream.extend(pipeline.dependencies)

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
            pipeline = self.registry.get_pipeline(pipeline_name)
            if pipeline:
                downstream.extend(pipeline.outputs)

        return list(set(downstream))

    def get_all_downstream(self, source_name: str, visited: set = None) -> list[str]:
        """Get all downstream dependencies recursively."""
        if visited is None:
            visited = set()

        if source_name in visited:
            return []

        visited.add(source_name)
        direct = self.get_downstream(source_name)

        all_downstream = list(direct)
        for dep in direct:
            all_downstream.extend(self.get_all_downstream(dep, visited))

        return list(set(all_downstream))

    def get_impact_chain(self, source_name: str) -> dict:
        """
        Get full impact analysis for a source.

        Returns dict with upstream, downstream, and affected services/dashboards.
        """
        all_downstream = self.get_all_downstream(source_name)

        # Find affected services
        affected_services = set()
        for service_name in self.registry.list_services():
            sources = self.registry.get_sources_for_service(service_name)
            source_names = [s.name for s in sources]
            if source_name in source_names or any(d in source_names for d in all_downstream):
                affected_services.add(service_name)

        # Find affected dashboards
        affected_dashboards = set()
        for page_id in self.registry.list_dashboards():
            sources = self.registry.get_sources_for_dashboard(page_id)
            source_names = [s.name for s in sources]
            if source_name in source_names or any(d in source_names for d in all_downstream):
                affected_dashboards.add(page_id)

        return {
            "source": source_name,
            "upstream": self.get_upstream(source_name),
            "downstream": all_downstream,
            "affected_services": sorted(affected_services),
            "affected_dashboards": sorted(affected_dashboards),
        }

    def get_execution_order(self, target_sources: list[str] = None) -> list[str]:
        """
        Get pipeline execution order (topological sort).

        If target_sources provided, returns order needed to produce those.
        Otherwise returns full execution order for all pipelines.
        """
        if target_sources is None:
            target_sources = self.registry.list_data_sources()

        # Build dependency graph for pipelines
        pipeline_deps: dict[str, set[str]] = {}
        for pipeline_name in self.registry.list_pipelines():
            pipeline = self.registry.get_pipeline(pipeline_name)
            if not pipeline:
                continue

            # Find pipelines that produce our dependencies
            deps = set()
            for dep in pipeline.dependencies:
                producers = self._producers.get(dep, [])
                deps.update(producers)

            pipeline_deps[pipeline_name] = deps

        # Topological sort
        sorted_pipelines = []
        visited = set()
        temp_visited = set()

        def visit(pipeline: str):
            if pipeline in temp_visited:
                return  # Skip cycles
            if pipeline in visited:
                return

            temp_visited.add(pipeline)
            for dep in pipeline_deps.get(pipeline, []):
                visit(dep)
            temp_visited.remove(pipeline)

            visited.add(pipeline)
            sorted_pipelines.append(pipeline)

        for pipeline in pipeline_deps:
            visit(pipeline)

        return sorted_pipelines
