#!/usr/bin/env python3
"""
Unified Ticker Mapper - Complete Integration Layer
===================================================

Combines sector_industry_registry.json + metric_registry.json
to provide unified access for AI agents and calculators.

This is the MAIN integration component that Phase 2 calculators
and MCP agents should use.

Usage:
    from PROCESSORS.core.shared.unified_mapper import UnifiedTickerMapper

    mapper = UnifiedTickerMapper()
    info = mapper.get_complete_info("ACB")
    # Returns: entity, sector, metrics, calculator, all definitions

Author: Claude Code
Date: 2025-12-05
"""

from pathlib import Path
import json
from typing import Dict, List, Optional, Set
from config.registries import SectorRegistry, MetricRegistry
import logging

logger = logging.getLogger(__name__)


class UnifiedTickerMapper:
    """
    Unified mapping interface combining sector and metric registries

    Provides complete ticker information including:
    - Entity type and sector classification
    - Available metric codes and definitions
    - Calculator class selection
    - Peer ticker identification

    This is the PRIMARY interface that should be used by:
    - Phase 2 calculators (auto-select calculator)
    - MCP servers (understand data structure)
    - AI agents (query and analyze)
    """

    def __init__(
        self,
        sector_registry_path: Optional[str] = None,
        metric_registry_path: Optional[str] = None
    ):
        """
        Initialize unified mapper with both registries

        Args:
            sector_registry_path: Path to sector_industry_registry.json
            metric_registry_path: Path to metric_registry.json
        """
        self.sector_registry = SectorRegistry(sector_registry_path)
        self.metric_registry = MetricRegistry(metric_registry_path)

        # Calculator class mapping
        self.calculator_map = {
            "COMPANY": "CompanyFinancialCalculator",
            "BANK": "BankFinancialCalculator",
            "SECURITY": "SecurityFinancialCalculator",
            "INSURANCE": "InsuranceFinancialCalculator"
        }

        logger.info("UnifiedTickerMapper initialized")
        logger.info(f"  Sector registry: {self.sector_registry.get_statistics()['total_tickers']} tickers")
        logger.info(f"  Metric registry: {sum(self.metric_registry.get_metric_count().values())} metrics")

    def get_complete_info(self, ticker: str) -> Dict:
        """
        Get complete information for a ticker

        This is the MAIN METHOD that AI agents and calculators should use.

        Args:
            ticker: Stock ticker (e.g., "ACB", "VCB")

        Returns:
            Complete ticker information dictionary:
            {
                "ticker": str,
                "entity_type": str,
                "sector": str,
                "calculator_class": str,
                "available_metrics": Dict[code, name],
                "calculated_metrics": List[str],
                "peer_tickers": List[str],
                "metric_prefixes": List[str]
            }

        Example:
            >>> mapper = UnifiedTickerMapper()
            >>> info = mapper.get_complete_info("ACB")
            >>> print(info["entity_type"])
            'BANK'
            >>> print(info["available_metrics"]["BIS_22A"])
            'Lợi nhuận sau thuế'
        """
        # Get sector info
        ticker_info = self.sector_registry.get_ticker(ticker)
        if not ticker_info:
            raise ValueError(f"Ticker {ticker} not found in sector registry")

        entity_type = ticker_info["entity_type"]
        sector = ticker_info["sector"]

        # Get available metrics for this entity type
        available_metrics = self._get_available_metrics(entity_type)

        # Get calculated metrics that are valid for this entity
        calculated_metrics = self._get_calculated_metrics(entity_type)

        # Get peer tickers (same sector)
        peer_tickers = self.sector_registry.get_peers(ticker)

        # Get metric prefixes
        metric_prefixes = self.sector_registry.get_metric_prefixes(sector)

        return {
            "ticker": ticker,
            "entity_type": entity_type,
            "sector": sector,
            "name": ticker_info.get("name", ""),
            "exchange": ticker_info.get("exchange", ""),
            "calculator_class": self.calculator_map.get(entity_type),
            "available_metrics": available_metrics,
            "calculated_metrics": calculated_metrics,
            "peer_tickers": peer_tickers,
            "metric_prefixes": metric_prefixes
        }

    def _get_available_metrics(self, entity_type: str) -> Dict[str, str]:
        """
        Get all available metric codes and names for entity type

        Args:
            entity_type: "COMPANY", "BANK", "INSURANCE", "SECURITY"

        Returns:
            Dictionary mapping metric codes to Vietnamese names:
            {
                "BIS_1": "Tổng doanh thu hoạt động",
                "BIS_22A": "Lợi nhuận sau thuế",
                ...
            }
        """
        metrics = {}

        # Get all metrics for this entity type from metric registry
        entity_metrics = self.metric_registry.registry["entity_types"].get(entity_type, {})

        for category_name, category_metrics in entity_metrics.items():
            for code, metric_info in category_metrics.items():
                metrics[code] = metric_info["name_vi"]

        return metrics

    def _get_calculated_metrics(self, entity_type: str) -> List[str]:
        """
        Get list of calculated metrics applicable to this entity type

        Args:
            entity_type: "COMPANY", "BANK", "INSURANCE", "SECURITY"

        Returns:
            List of calculated metric names: ["roe", "roa", "eps", ...]
        """
        calculated = []

        calc_metrics = self.metric_registry.registry.get("calculated_metrics", {})

        for metric_name, metric_info in calc_metrics.items():
            if entity_type in metric_info.get("entity_types", []):
                calculated.append(metric_name)

        return calculated

    def get_metric_definition(self, ticker: str, metric_code: str) -> Optional[Dict]:
        """
        Get full metric definition for a specific ticker and metric code

        Args:
            ticker: Stock ticker
            metric_code: Metric code (e.g., "BIS_22A")

        Returns:
            Metric definition dictionary or None if not found

        Example:
            >>> mapper.get_metric_definition("ACB", "BIS_22A")
            {
                "code": "BIS_22A",
                "name_vi": "Lợi nhuận sau thuế",
                "name_en": "Net profit after tax",
                "unit": "VND",
                "data_type": "NUMBER(23,2)",
                "category": "income"
            }
        """
        ticker_info = self.sector_registry.get_ticker(ticker)
        if not ticker_info:
            return None

        entity_type = ticker_info["entity_type"]
        return self.metric_registry.get_metric(metric_code, entity_type)

    def validate_metric_for_ticker(self, ticker: str, metric_code: str) -> bool:
        """
        Check if a metric code is valid for a ticker's entity type

        Args:
            ticker: Stock ticker
            metric_code: Metric code to validate

        Returns:
            True if metric is valid for this ticker's entity type

        Example:
            >>> mapper.validate_metric_for_ticker("ACB", "BIS_22A")
            True
            >>> mapper.validate_metric_for_ticker("ACB", "CIS_62")
            False  # CIS_62 is for COMPANY, not BANK
        """
        ticker_info = self.sector_registry.get_ticker(ticker)
        if not ticker_info:
            return False

        entity_type = ticker_info["entity_type"]
        metric = self.metric_registry.get_metric(metric_code, entity_type)

        return metric is not None

    def get_calculator_class(self, ticker: str) -> str:
        """
        Get calculator class name for a ticker

        Args:
            ticker: Stock ticker

        Returns:
            Calculator class name (e.g., "BankFinancialCalculator")

        Example:
            >>> mapper.get_calculator_class("ACB")
            'BankFinancialCalculator'
        """
        ticker_info = self.sector_registry.get_ticker(ticker)
        if not ticker_info:
            raise ValueError(f"Ticker {ticker} not found")

        return self.calculator_map.get(ticker_info["entity_type"])

    def search_tickers_with_metric(
        self,
        metric_code: str,
        sector: Optional[str] = None
    ) -> List[str]:
        """
        Find all tickers that have a specific metric available

        Args:
            metric_code: Metric code (e.g., "BIS_22A")
            sector: Optional sector filter

        Returns:
            List of tickers that have this metric

        Example:
            >>> mapper.search_tickers_with_metric("BIS_22A")
            ['ACB', 'VCB', 'TCB', ...]  # All banks

            >>> mapper.search_tickers_with_metric("BIS_22A", "Ngân hàng")
            ['ACB', 'VCB', 'TCB', ...]  # Banks in banking sector
        """
        # Determine which entity type has this metric
        entity_type = None
        for etype in ["COMPANY", "BANK", "INSURANCE", "SECURITY"]:
            if self.metric_registry.get_metric(metric_code, etype):
                entity_type = etype
                break

        if not entity_type:
            return []

        # Get all tickers for this entity type
        if sector:
            # Filter by sector
            tickers = self.sector_registry.get_tickers_by_sector(sector)
        else:
            # Get all tickers for entity type
            tickers = []
            for sec in self.sector_registry.get_sectors_by_entity(entity_type):
                tickers.extend(self.sector_registry.get_tickers_by_sector(sec))

        return tickers

    def get_peer_comparison_info(self, ticker: str) -> Dict:
        """
        Get complete information for peer comparison

        Args:
            ticker: Stock ticker

        Returns:
            Dictionary with ticker info, peers, and comparison metrics

        Example:
            >>> mapper.get_peer_comparison_info("ACB")
            {
                "ticker": "ACB",
                "sector": "Ngân hàng",
                "peers": ["VCB", "TCB", "MBB", ...],
                "comparison_metrics": ["roe", "roa", "nim", "car"],
                "metric_codes": {
                    "roe": {"dependencies": ["BIS_22A", "BBS_400"]},
                    ...
                }
            }
        """
        ticker_info = self.sector_registry.get_ticker(ticker)
        if not ticker_info:
            raise ValueError(f"Ticker {ticker} not found")

        entity_type = ticker_info["entity_type"]
        sector = ticker_info["sector"]

        # Get peers
        peers = self.sector_registry.get_peers(ticker)

        # Get comparison metrics (calculated metrics for this entity)
        comparison_metrics = self._get_calculated_metrics(entity_type)

        # Get metric dependencies
        metric_codes = {}
        calc_metrics = self.metric_registry.registry.get("calculated_metrics", {})
        for metric_name in comparison_metrics:
            if metric_name in calc_metrics:
                metric_info = calc_metrics[metric_name]
                metric_codes[metric_name] = {
                    "dependencies": metric_info["dependencies"].get(entity_type, []),
                    "formula": metric_info.get("formula", ""),
                    "unit": metric_info.get("unit", "")
                }

        return {
            "ticker": ticker,
            "sector": sector,
            "entity_type": entity_type,
            "peers": peers,
            "comparison_metrics": comparison_metrics,
            "metric_codes": metric_codes
        }

    def query_by_natural_language(self, query: str) -> Dict:
        """
        Query system using natural language (AI agent interface)

        Args:
            query: Natural language query

        Returns:
            Query results based on intent

        Example:
            >>> mapper.query_by_natural_language("What sector is ACB?")
            {"ticker": "ACB", "sector": "Ngân hàng", "entity_type": "BANK"}

            >>> mapper.query_by_natural_language("Get all construction stocks")
            {"sector": "Xây dựng và Vật liệu", "tickers": [...]}

            >>> mapper.query_by_natural_language("What calculator for BANK entity?")
            {"entity_type": "BANK", "calculator": "BankFinancialCalculator"}
        """
        query_lower = query.lower()

        # Pattern matching for common queries
        if "what sector" in query_lower or "thuộc ngành" in query_lower:
            # Extract ticker (simple: uppercase words)
            import re
            ticker_match = re.search(r'\b([A-Z]{3})\b', query)
            if ticker_match:
                ticker = ticker_match.group(1)
                ticker_info = self.sector_registry.get_ticker(ticker)
                return {
                    "query_type": "ticker_sector",
                    "ticker": ticker,
                    "sector": ticker_info.get("sector") if ticker_info else None,
                    "entity_type": ticker_info.get("entity_type") if ticker_info else None
                }

        elif "get all" in query_lower or "tất cả cổ phiếu" in query_lower:
            # Search for sector name
            sectors = self.sector_registry.get_all_sectors()
            for sector in sectors:
                if sector.lower() in query_lower:
                    tickers = self.sector_registry.get_tickers_by_sector(sector)
                    return {
                        "query_type": "sector_tickers",
                        "sector": sector,
                        "tickers": tickers,
                        "count": len(tickers)
                    }

        elif "calculator" in query_lower or "calculator class" in query_lower:
            # Extract entity type
            for entity in ["COMPANY", "BANK", "INSURANCE", "SECURITY"]:
                if entity.lower() in query_lower:
                    return {
                        "query_type": "calculator_class",
                        "entity_type": entity,
                        "calculator": self.calculator_map.get(entity)
                    }

        return {"query_type": "unknown", "message": "Could not parse query"}

    def __repr__(self) -> str:
        """String representation"""
        sector_stats = self.sector_registry.get_statistics()
        metric_counts = self.metric_registry.get_metric_count()
        total_metrics = sum(metric_counts.values())

        return (
            f"UnifiedTickerMapper(\n"
            f"  tickers={sector_stats['total_tickers']},\n"
            f"  sectors={sector_stats['total_sectors']},\n"
            f"  entity_types={sector_stats['total_entity_types']},\n"
            f"  total_metrics={total_metrics},\n"
            f"  sector_registry={self.sector_registry.get_version()},\n"
            f"  metric_registry={self.metric_registry.get_version()}\n"
            f")"
        )


# Convenience function for quick access
def get_unified_mapper(
    sector_registry_path: Optional[str] = None,
    metric_registry_path: Optional[str] = None
) -> UnifiedTickerMapper:
    """
    Get unified mapper instance

    Args:
        sector_registry_path: Path to sector registry (optional)
        metric_registry_path: Path to metric registry (optional)

    Returns:
        UnifiedTickerMapper instance
    """
    return UnifiedTickerMapper(sector_registry_path, metric_registry_path)


if __name__ == "__main__":
    # Demo usage
    print("=" * 70)
    print("Unified Ticker Mapper Demo")
    print("=" * 70)

    mapper = UnifiedTickerMapper()
    print(f"\n{mapper}\n")

    # Demo 1: Get complete info for ACB
    print("Demo 1: Get complete info for ACB")
    print("-" * 70)
    acb_info = mapper.get_complete_info("ACB")
    print(f"Ticker: {acb_info['ticker']}")
    print(f"Entity Type: {acb_info['entity_type']}")
    print(f"Sector: {acb_info['sector']}")
    print(f"Calculator: {acb_info['calculator_class']}")
    print(f"\nAvailable Metrics: {len(acb_info['available_metrics'])} metrics")
    print(f"Sample metrics:")
    for code, name in list(acb_info['available_metrics'].items())[:5]:
        print(f"  {code}: {name}")
    print(f"\nCalculated Metrics: {acb_info['calculated_metrics']}")
    print(f"Peer Tickers ({len(acb_info['peer_tickers'])}): {acb_info['peer_tickers'][:10]}")

    # Demo 2: Validate metric for ticker
    print("\n\nDemo 2: Validate metrics for ACB")
    print("-" * 70)
    is_valid_bis = mapper.validate_metric_for_ticker("ACB", "BIS_22A")
    is_valid_cis = mapper.validate_metric_for_ticker("ACB", "CIS_62")
    print(f"BIS_22A valid for ACB: {is_valid_bis}")
    print(f"CIS_62 valid for ACB: {is_valid_cis}")

    # Demo 3: Get metric definition
    print("\n\nDemo 3: Get metric definition for BIS_22A")
    print("-" * 70)
    metric_def = mapper.get_metric_definition("ACB", "BIS_22A")
    if metric_def:
        print(f"Code: {metric_def['code']}")
        print(f"Name (VI): {metric_def['name_vi']}")
        print(f"Unit: {metric_def['unit']}")
        print(f"Data Type: {metric_def['data_type']}")

    # Demo 4: Find tickers with specific metric
    print("\n\nDemo 4: Find all tickers with BIS_22A metric")
    print("-" * 70)
    tickers_with_bis = mapper.search_tickers_with_metric("BIS_22A")
    print(f"Found {len(tickers_with_bis)} tickers with BIS_22A")
    print(f"Sample: {tickers_with_bis[:10]}")

    # Demo 5: Get peer comparison info
    print("\n\nDemo 5: Get peer comparison info for ACB")
    print("-" * 70)
    peer_info = mapper.get_peer_comparison_info("ACB")
    print(f"Ticker: {peer_info['ticker']}")
    print(f"Sector: {peer_info['sector']}")
    print(f"Peers ({len(peer_info['peers'])}): {peer_info['peers'][:10]}")
    print(f"Comparison Metrics: {peer_info['comparison_metrics']}")
    print(f"\nMetric Dependencies:")
    for metric, info in list(peer_info['metric_codes'].items())[:3]:
        print(f"  {metric}: {info['dependencies']}")

    # Demo 6: Natural language queries
    print("\n\nDemo 6: Natural language queries")
    print("-" * 70)

    query1 = mapper.query_by_natural_language("What sector is VCB?")
    print(f"Query: 'What sector is VCB?'")
    print(f"Result: {query1}")

    query2 = mapper.query_by_natural_language("Get all construction stocks")
    print(f"\nQuery: 'Get all construction stocks'")
    if 'sector' in query2:
        print(f"Result: {query2['sector']} has {query2.get('count', 0)} tickers")
    else:
        print(f"Result: {query2}")

    query3 = mapper.query_by_natural_language("What calculator for BANK entity?")
    print(f"\nQuery: 'What calculator for BANK entity?'")
    print(f"Result: {query3}")

    print("\n" + "=" * 70)
