#!/usr/bin/env python3
"""
Macro Commodity Fetcher
=======================

Thin wrapper to the new centralized API module.
All legacy code has been removed for security (hardcoded tokens).

Usage:
    from PROCESSORS.technical.macro_commodity.macro_commodity_fetcher import MacroCommodityFetcher

    fetcher = MacroCommodityFetcher()

    # Check API health first
    health = fetcher.health_check()
    print(health)

    # Fetch data
    df = fetcher.fetch_all()

New API module (recommended):
    from PROCESSORS.api import UnifiedDataFetcher, HealthChecker

    # Health check
    checker = HealthChecker()
    checker.check_all()
    checker.print_report()

    # Fetch data
    fetcher = UnifiedDataFetcher()
    df = fetcher.fetch_all()

See PROCESSORS/api/README.md for full documentation.
"""

import logging
from typing import Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)

# Import from new API module
from PROCESSORS.api import UnifiedDataFetcher, HealthChecker
from PROCESSORS.api.clients import WiChartClient, SimplizeClient, VNStockClient


class MacroCommodityFetcher:
    """
    Unified fetcher for Commodity and Macro data.

    This is a thin wrapper around the new centralized API module.
    Provides backward compatibility for existing code.
    """

    def __init__(self):
        """Initialize with new API module."""
        self._fetcher = UnifiedDataFetcher()
        self._health_checker = HealthChecker()
        logger.info("MacroCommodityFetcher initialized (using centralized API module)")

    def health_check(self) -> Dict:
        """
        Check health of all APIs.

        Returns:
            Dictionary with status for each API:
            {
                'wichart': {'status': 'OK', 'latency_ms': 99, 'data_fresh': True},
                'simplize': {'status': 'OK', 'latency_ms': 150, ...},
                ...
            }
        """
        results = self._health_checker.check_all()
        return {
            name: {
                'status': result.status.value,
                'latency_ms': result.latency_ms,
                'data_fresh': result.data_fresh,
                'error': result.error_message,
            }
            for name, result in results.items()
        }

    def print_health_report(self):
        """Print formatted health report to console."""
        self._health_checker.check_all()
        self._health_checker.print_report()

    def is_api_healthy(self, api_name: str = None) -> bool:
        """
        Check if API(s) are healthy.

        Args:
            api_name: Specific API to check ('wichart', 'simplize', 'fireant', 'vnstock')
                     If None, checks all APIs.

        Returns:
            True if healthy, False otherwise
        """
        results = self._health_checker.check_all()

        if api_name:
            result = results.get(api_name)
            return result is not None and result.status.value == 'OK'

        # All APIs must be OK or WARN
        return all(r.status.value in ['OK', 'WARN'] for r in results.values())

    def fetch_commodities(self, start_date: str = "2015-01-01") -> pd.DataFrame:
        """
        Fetch all commodities.

        Args:
            start_date: Start date (YYYY-MM-DD)

        Returns:
            DataFrame with commodity data
        """
        return self._fetcher.fetch_commodities(start_date)

    def fetch_all_macro(self) -> pd.DataFrame:
        """
        Fetch all macro data (exchange rates, interest rates, bonds).

        Returns:
            DataFrame with macro data
        """
        return self._fetcher.fetch_macro()

    def fetch_exchange_rates(self) -> pd.DataFrame:
        """Fetch exchange rates from WiChart."""
        return self._fetcher.wichart.get_exchange_rates()

    def fetch_interest_rates(self) -> pd.DataFrame:
        """Fetch interest rates from WiChart."""
        return self._fetcher.wichart.get_interest_rates()

    def fetch_deposit_rates(self) -> pd.DataFrame:
        """Fetch deposit rates from WiChart."""
        return self._fetcher.wichart.get_deposit_rates()

    def fetch_gov_bonds(self) -> pd.DataFrame:
        """Fetch government bond yields from Simplize."""
        return self._fetcher.simplize.get_gov_bond_5y()

    def fetch_all(self, start_date: str = "2015-01-01") -> pd.DataFrame:
        """
        Fetch all data (commodity + macro).

        Args:
            start_date: Start date for historical data

        Returns:
            Combined DataFrame with all data
        """
        return self._fetcher.fetch_all(start_date)

    # Expose underlying clients for advanced usage
    @property
    def wichart(self) -> WiChartClient:
        """Get WiChart client for direct access."""
        return self._fetcher.wichart

    @property
    def simplize(self) -> SimplizeClient:
        """Get Simplize client for direct access."""
        return self._fetcher.simplize

    @property
    def vnstock(self) -> VNStockClient:
        """Get VNStock client for direct access."""
        return self._fetcher.vnstock


# For backward compatibility
LegacyMacroCommodityFetcher = MacroCommodityFetcher


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)

    fetcher = MacroCommodityFetcher()

    print("\n=== API Health Check ===")
    fetcher.print_health_report()

    print("\n=== Quick Data Test ===")
    df = fetcher.fetch_all_macro()
    print(f"Fetched {len(df)} macro records")
    print(f"Symbols: {df['symbol'].nunique()}")
