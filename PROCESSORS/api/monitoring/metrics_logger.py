"""
Metrics Logger
==============

Log API metrics (success/fail/latency) for monitoring and debugging.
"""

import json
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class APIMetrics:
    """Metrics for a single API."""

    api_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    last_error: Optional[str] = None
    endpoint_stats: Dict[str, Dict] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency in milliseconds."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        result = asdict(self)
        result["success_rate"] = round(self.success_rate, 2)
        result["avg_latency_ms"] = round(self.avg_latency_ms, 2)
        return result


class MetricsLogger:
    """
    Logger for API metrics.

    Tracks request counts, latency, success/failure rates per API.

    Usage:
        logger = MetricsLogger("simplize")
        logger.log_request("/api/data", 200, 150.5)
        logger.log_failure("/api/data", "Connection timeout")
        print(logger.get_summary())
    """

    def __init__(self, api_name: str, log_file: Path = None):
        """
        Initialize metrics logger.

        Args:
            api_name: Name of the API being monitored
            log_file: Optional file to persist metrics
        """
        self.api_name = api_name
        self.log_file = log_file
        self._metrics = APIMetrics(api_name=api_name)

    def log_request(self, endpoint: str, status_code: int, latency_ms: float):
        """
        Log a successful API request.

        Args:
            endpoint: API endpoint path
            status_code: HTTP status code
            latency_ms: Request latency in milliseconds
        """
        self._metrics.total_requests += 1
        self._metrics.successful_requests += 1
        self._metrics.total_latency_ms += latency_ms
        self._metrics.last_success = datetime.now().isoformat()

        # Track per-endpoint stats
        if endpoint not in self._metrics.endpoint_stats:
            self._metrics.endpoint_stats[endpoint] = {
                "requests": 0,
                "total_latency": 0.0,
                "last_status": None,
            }

        self._metrics.endpoint_stats[endpoint]["requests"] += 1
        self._metrics.endpoint_stats[endpoint]["total_latency"] += latency_ms
        self._metrics.endpoint_stats[endpoint]["last_status"] = status_code

        logger.debug(f"[{self.api_name}] {endpoint} -> {status_code} ({latency_ms:.0f}ms)")

    def log_failure(self, endpoint: str, error_message: str):
        """
        Log a failed API request.

        Args:
            endpoint: API endpoint path
            error_message: Error description
        """
        self._metrics.total_requests += 1
        self._metrics.failed_requests += 1
        self._metrics.last_failure = datetime.now().isoformat()
        self._metrics.last_error = error_message

        logger.warning(f"[{self.api_name}] {endpoint} -> FAILED: {error_message}")

    def get_metrics(self) -> APIMetrics:
        """Get current metrics."""
        return self._metrics

    def get_summary(self) -> Dict:
        """Get metrics summary as dictionary."""
        return self._metrics.to_dict()

    def reset(self):
        """Reset all metrics."""
        self._metrics = APIMetrics(api_name=self.api_name)

    def save(self):
        """Save metrics to file if configured."""
        if not self.log_file:
            return

        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

            # Load existing data or create new
            if self.log_file.exists():
                with open(self.log_file, "r") as f:
                    data = json.load(f)
            else:
                data = {"history": []}

            # Append current metrics with timestamp
            entry = {
                "timestamp": datetime.now().isoformat(),
                "metrics": self.get_summary(),
            }
            data["history"].append(entry)

            # Keep only last 1000 entries
            if len(data["history"]) > 1000:
                data["history"] = data["history"][-1000:]

            with open(self.log_file, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"[{self.api_name}] Metrics saved to {self.log_file}")

        except Exception as e:
            logger.error(f"[{self.api_name}] Failed to save metrics: {e}")


class GlobalMetricsRegistry:
    """
    Global registry for all API metrics.

    Usage:
        registry = GlobalMetricsRegistry()
        registry.register("simplize", simplize_logger)
        registry.register("wichart", wichart_logger)
        print(registry.get_all_summaries())
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loggers = {}
        return cls._instance

    def register(self, api_name: str, logger: MetricsLogger):
        """Register a metrics logger."""
        self._loggers[api_name] = logger

    def get_logger(self, api_name: str) -> Optional[MetricsLogger]:
        """Get logger for an API."""
        return self._loggers.get(api_name)

    def get_all_summaries(self) -> Dict[str, Dict]:
        """Get summaries from all registered loggers."""
        return {name: logger.get_summary() for name, logger in self._loggers.items()}

    def get_health_overview(self) -> Dict:
        """Get overall health status."""
        summaries = self.get_all_summaries()

        healthy = 0
        degraded = 0
        unhealthy = 0

        for api_name, metrics in summaries.items():
            success_rate = metrics.get("success_rate", 0)
            if success_rate >= 95:
                healthy += 1
            elif success_rate >= 80:
                degraded += 1
            else:
                unhealthy += 1

        return {
            "timestamp": datetime.now().isoformat(),
            "total_apis": len(summaries),
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "apis": summaries,
        }


def get_metrics_registry() -> GlobalMetricsRegistry:
    """Get global metrics registry."""
    return GlobalMetricsRegistry()
