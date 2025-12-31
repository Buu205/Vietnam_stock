"""
Schema and Data Validators
==========================

Validates data files against registry definitions.
Catches issues before they hit the dashboard.

Usage:
    from config.data_mapping import SchemaValidator, HealthChecker

    # Validate schema
    validator = SchemaValidator()
    result = validator.validate("bank_metrics")

    # Health check
    checker = HealthChecker()
    report = checker.full_report()

Author: AI Assistant
Date: 2025-12-31
Version: 1.0.0
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

from .registry import DataMappingRegistry, get_registry
from .resolver import PathResolver


@dataclass
class ValidationResult:
    """Result of schema validation."""
    source_name: str
    is_valid: bool
    expected_columns: tuple[str, ...]
    actual_columns: tuple[str, ...]
    missing_columns: tuple[str, ...]
    extra_columns: tuple[str, ...]
    error: Optional[str] = None


@dataclass
class HealthStatus:
    """Health status of a data source."""
    source_name: str
    exists: bool
    is_stale: bool
    last_modified: Optional[datetime]
    file_size_mb: float
    row_count: Optional[int]
    error: Optional[str] = None


class SchemaValidator:
    """
    Validates parquet file schemas against registry definitions.

    Usage:
        validator = SchemaValidator()
        result = validator.validate("bank_metrics")
        if not result.is_valid:
            print(f"Missing: {result.missing_columns}")
    """

    def __init__(self, registry: Optional[DataMappingRegistry] = None):
        self.registry = registry or get_registry()
        self.path_resolver = PathResolver(self.registry)

    def validate(self, source_name: str) -> ValidationResult:
        """
        Validate a data source against its schema.

        Args:
            source_name: Data source name from registry

        Returns:
            ValidationResult with details
        """
        try:
            # Get expected schema
            expected = self.registry.get_schema(source_name)

            # Get actual file
            path = self.path_resolver.resolve(source_name, validate=True)

            # Read parquet schema (just columns, not full data)
            if str(path).endswith('.parquet'):
                df = pd.read_parquet(path, columns=None)
                actual = tuple(df.columns.tolist())
            elif str(path).endswith('.json'):
                df = pd.read_json(path)
                actual = tuple(df.columns.tolist())
            else:
                return ValidationResult(
                    source_name=source_name,
                    is_valid=False,
                    expected_columns=expected,
                    actual_columns=(),
                    missing_columns=(),
                    extra_columns=(),
                    error=f"Unsupported file type: {path.suffix}"
                )

            # Compare
            expected_set = set(expected)
            actual_set = set(actual)

            missing = tuple(expected_set - actual_set)
            extra = tuple(actual_set - expected_set)

            return ValidationResult(
                source_name=source_name,
                is_valid=len(missing) == 0,
                expected_columns=expected,
                actual_columns=actual,
                missing_columns=missing,
                extra_columns=extra,
            )

        except FileNotFoundError as e:
            return ValidationResult(
                source_name=source_name,
                is_valid=False,
                expected_columns=self.registry.get_schema(source_name),
                actual_columns=(),
                missing_columns=(),
                extra_columns=(),
                error=f"File not found: {e}"
            )
        except Exception as e:
            return ValidationResult(
                source_name=source_name,
                is_valid=False,
                expected_columns=(),
                actual_columns=(),
                missing_columns=(),
                extra_columns=(),
                error=str(e)
            )

    def validate_all(self) -> dict[str, ValidationResult]:
        """Validate all data sources."""
        results = {}
        for name in self.registry.list_data_sources():
            results[name] = self.validate(name)
        return results

    def get_invalid_sources(self) -> list[ValidationResult]:
        """Get list of sources that failed validation."""
        results = self.validate_all()
        return [r for r in results.values() if not r.is_valid]


class HealthChecker:
    """
    Checks health of data files (existence, staleness, size).

    Usage:
        checker = HealthChecker()
        report = checker.full_report()
        stale = checker.get_stale_sources(max_age_hours=24)
    """

    def __init__(
        self,
        registry: Optional[DataMappingRegistry] = None,
        staleness_thresholds: Optional[dict[str, int]] = None
    ):
        self.registry = registry or get_registry()
        self.path_resolver = PathResolver(self.registry)

        # Default staleness thresholds (hours)
        self.staleness_thresholds = staleness_thresholds or {
            "daily": 26,      # 26 hours for daily data
            "quarterly": 2200,  # ~3 months
            "yearly": 8800,   # ~1 year
            "realtime": 1,    # 1 hour
            "weekly": 170,    # ~1 week
        }

    def check(self, source_name: str) -> HealthStatus:
        """
        Check health of a data source.

        Args:
            source_name: Data source name from registry

        Returns:
            HealthStatus with details
        """
        try:
            source = self.registry.get_data_source(source_name)
            if not source:
                return HealthStatus(
                    source_name=source_name,
                    exists=False,
                    is_stale=True,
                    last_modified=None,
                    file_size_mb=0,
                    row_count=None,
                    error="Source not found in registry"
                )

            path = self.path_resolver.resolve_safe(source_name)
            if not path:
                return HealthStatus(
                    source_name=source_name,
                    exists=False,
                    is_stale=True,
                    last_modified=None,
                    file_size_mb=0,
                    row_count=None,
                    error="File not found"
                )

            # Get file stats
            stat = path.stat()
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            file_size_mb = stat.st_size / (1024 * 1024)

            # Check staleness
            threshold_hours = self.staleness_thresholds.get(
                source.update_freq, 24
            )
            age = datetime.now() - last_modified
            is_stale = age > timedelta(hours=threshold_hours)

            # Get row count (optional, skip for large files)
            row_count = None
            if file_size_mb < 100:  # Only for files < 100MB
                try:
                    if str(path).endswith('.parquet'):
                        df = pd.read_parquet(path)
                        row_count = len(df)
                except:
                    pass

            return HealthStatus(
                source_name=source_name,
                exists=True,
                is_stale=is_stale,
                last_modified=last_modified,
                file_size_mb=round(file_size_mb, 2),
                row_count=row_count,
            )

        except Exception as e:
            return HealthStatus(
                source_name=source_name,
                exists=False,
                is_stale=True,
                last_modified=None,
                file_size_mb=0,
                row_count=None,
                error=str(e)
            )

    def check_all(self) -> dict[str, HealthStatus]:
        """Check health of all data sources."""
        results = {}
        for name in self.registry.list_data_sources():
            results[name] = self.check(name)
        return results

    def get_stale_sources(self, max_age_hours: int = None) -> list[HealthStatus]:
        """Get list of stale data sources."""
        results = self.check_all()
        return [r for r in results.values() if r.is_stale]

    def get_missing_sources(self) -> list[HealthStatus]:
        """Get list of missing data sources."""
        results = self.check_all()
        return [r for r in results.values() if not r.exists]

    def full_report(self) -> dict:
        """
        Generate full health report.

        Returns:
            Dict with summary and details
        """
        all_health = self.check_all()

        healthy = [h for h in all_health.values() if h.exists and not h.is_stale]
        stale = [h for h in all_health.values() if h.exists and h.is_stale]
        missing = [h for h in all_health.values() if not h.exists]

        total_size_mb = sum(h.file_size_mb for h in all_health.values())

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_sources": len(all_health),
                "healthy": len(healthy),
                "stale": len(stale),
                "missing": len(missing),
                "total_size_mb": round(total_size_mb, 2),
            },
            "stale_sources": [h.source_name for h in stale],
            "missing_sources": [h.source_name for h in missing],
            "details": {
                name: {
                    "exists": h.exists,
                    "is_stale": h.is_stale,
                    "last_modified": h.last_modified.isoformat() if h.last_modified else None,
                    "size_mb": h.file_size_mb,
                    "row_count": h.row_count,
                    "error": h.error,
                }
                for name, h in all_health.items()
            }
        }
