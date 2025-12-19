"""
API Monitoring Module
=====================

Health checking and metrics logging for API clients.

Components:
- HealthChecker: Check API health status
- MetricsLogger: Log API metrics (success/fail/latency)
- GlobalMetricsRegistry: Central registry for all metrics

Usage:
    from PROCESSORS.api.monitoring import HealthChecker, MetricsLogger

    # Health check
    checker = HealthChecker()
    results = checker.check_all()
    checker.print_report()

    # Metrics logging
    logger = MetricsLogger("simplize")
    logger.log_request("/api/data", 200, 150.5)

CLI Usage:
    python -m PROCESSORS.api.monitoring.health_checker
    python -m PROCESSORS.api.monitoring.health_checker --json
"""

from PROCESSORS.api.monitoring.metrics_logger import (
    MetricsLogger,
    APIMetrics,
    GlobalMetricsRegistry,
    get_metrics_registry,
)
from PROCESSORS.api.monitoring.health_checker import (
    HealthChecker,
    HealthStatus,
    APIHealthResult,
)

__all__ = [
    "HealthChecker",
    "HealthStatus",
    "APIHealthResult",
    "MetricsLogger",
    "APIMetrics",
    "GlobalMetricsRegistry",
    "get_metrics_registry",
]
