"""
API Module
==========

Centralized API management for external data sources.

This module provides:
- Base API client with retry logic and monitoring
- Specific clients for each data source (vnstock, wichart, simplize, fireant)
- Health checking and metrics logging
- Secure credential management
- Unified data fetcher

Usage:
    # Use specific clients
    from PROCESSORS.api.clients import WiChartClient, SimplizeClient, FireantClient, VNStockClient

    wichart = WiChartClient()
    fx_rates = wichart.get_exchange_rates()

    simplize = SimplizeClient()
    bonds = simplize.get_gov_bond_5y()

    # Use unified fetcher
    from PROCESSORS.api import UnifiedDataFetcher

    fetcher = UnifiedDataFetcher()
    df_all = fetcher.fetch_all()

    # Health monitoring
    from PROCESSORS.api.monitoring import HealthChecker

    checker = HealthChecker()
    checker.check_all()
    checker.print_report()

CLI Commands:
    # Check API health
    python -m PROCESSORS.api.monitoring.health_checker

    # Fetch data
    python -m PROCESSORS.api.unified_fetcher --type all --output output.parquet
"""

from PROCESSORS.api.core.base_client import BaseAPIClient, APIResponse
from PROCESSORS.api.core.exceptions import (
    APIError,
    APITimeoutError,
    APIConnectionError,
    APIAuthenticationError,
    APIRateLimitError,
    APIResponseError,
    APIDataError,
    APIConfigError,
)
from PROCESSORS.api.clients import (
    WiChartClient,
    SimplizeClient,
    FireantClient,
    VNStockClient,
)
from PROCESSORS.api.monitoring import (
    HealthChecker,
    HealthStatus,
    MetricsLogger,
)
from PROCESSORS.api.unified_fetcher import UnifiedDataFetcher

__all__ = [
    # Base
    "BaseAPIClient",
    "APIResponse",
    # Exceptions
    "APIError",
    "APITimeoutError",
    "APIConnectionError",
    "APIAuthenticationError",
    "APIRateLimitError",
    "APIResponseError",
    "APIDataError",
    "APIConfigError",
    # Clients
    "WiChartClient",
    "SimplizeClient",
    "FireantClient",
    "VNStockClient",
    # Monitoring
    "HealthChecker",
    "HealthStatus",
    "MetricsLogger",
    # Fetcher
    "UnifiedDataFetcher",
]

__version__ = "1.0.0"
