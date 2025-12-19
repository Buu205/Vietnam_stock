"""
Health Checker
==============

API health checking service for monitoring data freshness and API availability.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from enum import Enum

import pandas as pd

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """API health status levels."""

    OK = "OK"
    WARN = "WARN"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


@dataclass
class APIHealthResult:
    """Health check result for a single API."""

    api_name: str
    status: HealthStatus
    latency_ms: float
    last_success: Optional[str]
    data_fresh: bool
    data_age_days: Optional[int]
    error_message: Optional[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "api_name": self.api_name,
            "status": self.status.value,
            "latency_ms": round(self.latency_ms, 0),
            "last_success": self.last_success,
            "data_fresh": self.data_fresh,
            "data_age_days": self.data_age_days,
            "error_message": self.error_message,
        }


class HealthChecker:
    """
    API Health Checker.

    Performs health checks on all configured APIs and reports status.

    Usage:
        checker = HealthChecker()
        results = checker.check_all()
        checker.print_report()
    """

    # Maximum data age before considered stale (days)
    MAX_DATA_AGE_DAYS = 3

    def __init__(self, data_root: Path = None):
        """
        Initialize health checker.

        Args:
            data_root: Root directory for data files. Auto-detected if not provided.
        """
        self.data_root = data_root or self._find_data_root()
        self._results: Dict[str, APIHealthResult] = {}

    def _find_data_root(self) -> Path:
        """Find DATA directory."""
        current = Path(__file__).resolve()
        while current.parent != current:
            if (current / "DATA").exists():
                return current / "DATA"
            current = current.parent
        return Path("DATA")

    def check_wichart(self) -> APIHealthResult:
        """Check WiChart API health."""
        import time

        try:
            from PROCESSORS.api.clients import WiChartClient

            start = time.time()
            client = WiChartClient()
            is_healthy = client.health_check()
            latency = (time.time() - start) * 1000

            if is_healthy:
                # Check data freshness
                data_path = self.data_root / "processed" / "macro_commodity" / "macro_commodity_unified.parquet"
                data_fresh, age_days = self._check_data_freshness(data_path, "wichart")

                return APIHealthResult(
                    api_name="wichart",
                    status=HealthStatus.OK if data_fresh else HealthStatus.WARN,
                    latency_ms=latency,
                    last_success=datetime.now().isoformat(),
                    data_fresh=data_fresh,
                    data_age_days=age_days,
                    error_message=None if data_fresh else f"Data is {age_days} days old",
                )
            else:
                return APIHealthResult(
                    api_name="wichart",
                    status=HealthStatus.ERROR,
                    latency_ms=latency,
                    last_success=None,
                    data_fresh=False,
                    data_age_days=None,
                    error_message="Health check failed",
                )

        except Exception as e:
            logger.error(f"WiChart health check failed: {e}")
            return APIHealthResult(
                api_name="wichart",
                status=HealthStatus.ERROR,
                latency_ms=0,
                last_success=None,
                data_fresh=False,
                data_age_days=None,
                error_message=str(e),
            )

    def check_simplize(self) -> APIHealthResult:
        """Check Simplize API health."""
        import time

        try:
            from PROCESSORS.api.clients import SimplizeClient

            start = time.time()
            client = SimplizeClient()

            # Check if credentials are configured
            if not client.validate_credentials():
                return APIHealthResult(
                    api_name="simplize",
                    status=HealthStatus.WARN,
                    latency_ms=0,
                    last_success=None,
                    data_fresh=False,
                    data_age_days=None,
                    error_message="No API token configured",
                )

            is_healthy = client.health_check()
            latency = (time.time() - start) * 1000

            if is_healthy:
                # Check data freshness (rubber, WMP)
                data_path = self.data_root / "processed" / "macro_commodity" / "macro_commodity_unified.parquet"
                data_fresh, age_days = self._check_data_freshness(data_path, "simplize")

                return APIHealthResult(
                    api_name="simplize",
                    status=HealthStatus.OK if data_fresh else HealthStatus.WARN,
                    latency_ms=latency,
                    last_success=datetime.now().isoformat(),
                    data_fresh=data_fresh,
                    data_age_days=age_days,
                    error_message=None if data_fresh else f"Data is {age_days} days old",
                )
            else:
                return APIHealthResult(
                    api_name="simplize",
                    status=HealthStatus.ERROR,
                    latency_ms=latency,
                    last_success=None,
                    data_fresh=False,
                    data_age_days=None,
                    error_message="Health check failed (token may be expired)",
                )

        except Exception as e:
            logger.error(f"Simplize health check failed: {e}")
            return APIHealthResult(
                api_name="simplize",
                status=HealthStatus.ERROR,
                latency_ms=0,
                last_success=None,
                data_fresh=False,
                data_age_days=None,
                error_message=str(e),
            )

    def check_fireant(self) -> APIHealthResult:
        """Check Fireant API health."""
        import time

        try:
            from PROCESSORS.api.clients import FireantClient

            start = time.time()
            client = FireantClient()

            # Check if credentials are configured
            if not client.validate_credentials():
                return APIHealthResult(
                    api_name="fireant",
                    status=HealthStatus.WARN,
                    latency_ms=0,
                    last_success=None,
                    data_fresh=False,
                    data_age_days=None,
                    error_message="No bearer token configured",
                )

            is_healthy = client.health_check()
            latency = (time.time() - start) * 1000

            if is_healthy:
                return APIHealthResult(
                    api_name="fireant",
                    status=HealthStatus.OK,
                    latency_ms=latency,
                    last_success=datetime.now().isoformat(),
                    data_fresh=True,
                    data_age_days=0,
                    error_message=None,
                )
            else:
                return APIHealthResult(
                    api_name="fireant",
                    status=HealthStatus.ERROR,
                    latency_ms=latency,
                    last_success=None,
                    data_fresh=False,
                    data_age_days=None,
                    error_message="Health check failed",
                )

        except Exception as e:
            logger.error(f"Fireant health check failed: {e}")
            return APIHealthResult(
                api_name="fireant",
                status=HealthStatus.ERROR,
                latency_ms=0,
                last_success=None,
                data_fresh=False,
                data_age_days=None,
                error_message=str(e),
            )

    def check_vnstock(self) -> APIHealthResult:
        """Check VNStock (vnstock_data library) health."""
        import time

        try:
            from PROCESSORS.api.clients import VNStockClient

            start = time.time()
            client = VNStockClient()
            is_healthy = client.health_check()
            latency = (time.time() - start) * 1000

            if is_healthy:
                return APIHealthResult(
                    api_name="vnstock",
                    status=HealthStatus.OK,
                    latency_ms=latency,
                    last_success=datetime.now().isoformat(),
                    data_fresh=True,
                    data_age_days=0,
                    error_message=None,
                )
            else:
                return APIHealthResult(
                    api_name="vnstock",
                    status=HealthStatus.ERROR,
                    latency_ms=latency,
                    last_success=None,
                    data_fresh=False,
                    data_age_days=None,
                    error_message="vnstock_data library not available",
                )

        except Exception as e:
            logger.error(f"VNStock health check failed: {e}")
            return APIHealthResult(
                api_name="vnstock",
                status=HealthStatus.ERROR,
                latency_ms=0,
                last_success=None,
                data_fresh=False,
                data_age_days=None,
                error_message=str(e),
            )

    def _check_data_freshness(
        self, data_path: Path, source_filter: str = None
    ) -> tuple[bool, Optional[int]]:
        """
        Check if data file is fresh.

        Args:
            data_path: Path to parquet file
            source_filter: Optional source column value to filter

        Returns:
            Tuple of (is_fresh, age_in_days)
        """
        if not data_path.exists():
            return False, None

        try:
            df = pd.read_parquet(data_path)

            if df.empty:
                return False, None

            # Filter by source if specified
            if source_filter and "source" in df.columns:
                df = df[df["source"].str.contains(source_filter, case=False, na=False)]

            if df.empty:
                return False, None

            # Get latest date
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                latest_date = df["date"].max().date()
                age_days = (date.today() - latest_date).days
                is_fresh = age_days <= self.MAX_DATA_AGE_DAYS
                return is_fresh, age_days

            return False, None

        except Exception as e:
            logger.error(f"Error checking data freshness: {e}")
            return False, None

    def check_all(self) -> Dict[str, APIHealthResult]:
        """
        Run health checks on all APIs.

        Returns:
            Dictionary of API name to health result
        """
        logger.info("Running health checks on all APIs...")

        self._results = {
            "wichart": self.check_wichart(),
            "simplize": self.check_simplize(),
            "fireant": self.check_fireant(),
            "vnstock": self.check_vnstock(),
        }

        return self._results

    def get_results(self) -> Dict[str, APIHealthResult]:
        """Get latest health check results."""
        return self._results

    def print_report(self):
        """Print formatted health report to console."""
        if not self._results:
            self.check_all()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print()
        print("=" * 70)
        print(f"API HEALTH REPORT - {now}")
        print("=" * 70)
        print(f"{'API':<12} | {'Status':<6} | {'Latency':<8} | {'Last Success':<14} | {'Data Fresh':<10}")
        print("-" * 70)

        for api_name, result in self._results.items():
            status_str = result.status.value
            latency_str = f"{result.latency_ms:.0f}ms" if result.latency_ms else "N/A"

            if result.last_success:
                last_dt = datetime.fromisoformat(result.last_success)
                last_str = self._format_time_ago(last_dt)
            else:
                last_str = "N/A"

            if result.data_fresh:
                fresh_str = "Yes"
            elif result.data_age_days is not None:
                fresh_str = f"No ({result.data_age_days}d)"
            else:
                fresh_str = "N/A"

            # Add color codes for terminal
            if result.status == HealthStatus.OK:
                status_display = f"\033[92m{status_str}\033[0m"  # Green
            elif result.status == HealthStatus.WARN:
                status_display = f"\033[93m{status_str}\033[0m"  # Yellow
            else:
                status_display = f"\033[91m{status_str}\033[0m"  # Red

            print(f"{api_name:<12} | {status_display:<15} | {latency_str:<8} | {last_str:<14} | {fresh_str:<10}")

        print("=" * 70)

        # Print any errors
        errors = [r for r in self._results.values() if r.error_message]
        if errors:
            print("\nErrors:")
            for result in errors:
                print(f"  - {result.api_name}: {result.error_message}")

        print()

    def _format_time_ago(self, dt: datetime) -> str:
        """Format datetime as 'X ago' string."""
        delta = datetime.now() - dt
        if delta.total_seconds() < 60:
            return "Just now"
        elif delta.total_seconds() < 3600:
            mins = int(delta.total_seconds() / 60)
            return f"{mins} min ago"
        elif delta.total_seconds() < 86400:
            hours = int(delta.total_seconds() / 3600)
            return f"{hours} hr ago"
        else:
            days = int(delta.total_seconds() / 86400)
            return f"{days} day ago"

    def to_dict(self) -> Dict:
        """Get report as dictionary."""
        return {
            "timestamp": datetime.now().isoformat(),
            "apis": {name: result.to_dict() for name, result in self._results.items()},
        }


def main():
    """CLI entry point for health checker."""
    import argparse

    parser = argparse.ArgumentParser(description="Check API health status")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    checker = HealthChecker()
    checker.check_all()

    if args.json:
        import json
        print(json.dumps(checker.to_dict(), indent=2))
    else:
        checker.print_report()


if __name__ == "__main__":
    main()
