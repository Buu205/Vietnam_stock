#!/usr/bin/env python3
"""
Sector/Industry Registry Lookup Utility
========================================

Fast lookup utility for sector/industry classifications from sector_industry_registry.json

Features:
- Get ticker entity type and sector
- Get all tickers in a sector
- Get all sectors for entity type
- Get calculator class for ticker
- Get peers (same sector tickers)
- Search sectors

Usage:
    from PROCESSORS.core.registries.sector_lookup import SectorRegistry

    registry = SectorRegistry()

    # Get ticker info
    info = registry.get_ticker("VCB")
    # {'entity_type': 'BANK', 'sector': 'Ngân hàng', ...}

    # Get peers
    peers = registry.get_peers("VCB")
    # ['ACB', 'TPB', 'MBB', ...]

Author: Claude Code
Date: 2025-12-05
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def find_project_root() -> Path:
    """Find project root (stock_dashboard directory)"""
    current = Path(__file__).resolve()
    while current.parent != current:
        if current.name in ['Vietnam_dashboard', 'stock_dashboard']:
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent


PROJECT_ROOT = find_project_root()


class SectorRegistry:
    """
    Fast lookup for sector/industry classifications

    This class provides efficient access to:
    - Ticker → Entity Type + Sector mapping
    - Sector → Tickers list
    - Entity Type → Sectors list
    - Calculator class selection
    - Peer ticker identification
    """

    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize sector registry

        Args:
            registry_path: Path to sector_industry_registry.json (default: auto-detect)
        """
        if registry_path is None:
            registry_path = PROJECT_ROOT / "DATA" / "metadata" / "sector_industry_registry.json"
        else:
            registry_path = Path(registry_path)

        if not registry_path.exists():
            raise FileNotFoundError(
                f"Sector registry not found: {registry_path}\n"
            f"Please run: python config/registries/builders/build_sector_registry.py"
            )

        # Load registry
        with open(registry_path, 'r', encoding='utf-8') as f:
            self.registry = json.load(f)

        logger.info(f"Loaded sector registry v{self.registry['version']}")
        logger.info(f"  Total tickers: {self.registry['metadata']['total_tickers']}")
        logger.info(f"  Total sectors: {self.registry['metadata']['total_sectors']}")

    def get_ticker(self, ticker: str) -> Optional[Dict]:
        """
        Get complete information for a ticker

        Args:
            ticker: Stock ticker (e.g., "VCB", "ACB")

        Returns:
            Ticker information dictionary, or None if not found

        Example:
            >>> registry = SectorRegistry()
            >>> info = registry.get_ticker("VCB")
            >>> print(info['entity_type'])
            'BANK'
            >>> print(info['sector'])
            'Ngân hàng'
        """
        return self.registry["ticker_mapping"].get(ticker)

    def get_sector(self, sector_name: str) -> Optional[Dict]:
        """
        Get complete information for a sector

        Args:
            sector_name: Sector name (e.g., "Ngân hàng")

        Returns:
            Sector information dictionary, or None if not found

        Example:
            >>> registry = SectorRegistry()
            >>> info = registry.get_sector("Ngân hàng")
            >>> print(info['count'])
            24
            >>> print(info['tickers'][:5])
            ['ACB', 'MBB', 'TCB', 'VCB', 'VPB']
        """
        return self.registry["sectors"].get(sector_name)

    def get_entity_type_info(self, entity_type: str) -> Optional[Dict]:
        """
        Get complete information for an entity type
        
        Args:
            entity_type: Entity type (COMPANY, BANK, INSURANCE, SECURITY)
            
        Returns:
            Entity type information dictionary, or None if not found
            
        Example:
            >>> registry = SectorRegistry()
            >>> info = registry.get_entity_type_info("BANK")
            >>> print(info['calculator_class'])
            'BankFinancialCalculator'
            >>> print(info['sectors'])
            ['Ngân hàng']
        """
        return self.registry["entity_types"].get(entity_type)

    def get_all_tickers(self) -> List[str]:
        """
        Get list of all tickers in the registry
        
        Returns:
            List of all ticker symbols
        """
        return sorted(list(self.registry["ticker_mapping"].keys()))

    def get_tickers_by_entity_type(self, entity_type: str) -> List[str]:
        """
        Get all tickers for a specific entity type
        
        Args:
            entity_type: Entity type (COMPANY, BANK, INSURANCE, SECURITY)
            
        Returns:
            List of tickers belonging to this entity type
            
        Example:
            >>> registry = SectorRegistry()
            >>> bank_tickers = registry.get_tickers_by_entity_type("BANK")
        """
        sectors = self.get_sectors_by_entity(entity_type)
        all_tickers = []
        for sector in sectors:
            all_tickers.extend(self.get_tickers_by_sector(sector))
        return sorted(list(set(all_tickers)))

    def get_tickers_by_sector(self, sector_name: str) -> List[str]:
        """
        Get all tickers in a sector

        Args:
            sector_name: Sector name

        Returns:
            List of tickers in the sector

        Example:
            >>> registry = SectorRegistry()
            >>> banks = registry.get_tickers_by_sector("Ngân hàng")
            >>> print(len(banks))
            24
        """
        sector_info = self.get_sector(sector_name)
        if sector_info:
            return sector_info.get("tickers", [])
        return []

    def get_sectors_by_entity(self, entity_type: str) -> List[str]:
        """
        Get all sectors for an entity type

        Args:
            entity_type: Entity type (COMPANY, BANK, etc.)

        Returns:
            List of sector names

        Example:
            >>> registry = SectorRegistry()
            >>> company_sectors = registry.get_sectors_by_entity("COMPANY")
            >>> print(len(company_sectors))
            16  # COMPANY has 16 sectors
        """
        entity_info = self.get_entity_type_info(entity_type)
        if entity_info:
            return entity_info.get("sectors", [])
        return []

    def get_calculator_class(self, ticker: str) -> Optional[str]:
        """
        Get calculator class name for a ticker

        Args:
            ticker: Stock ticker

        Returns:
            Calculator class name (e.g., "BankFinancialCalculator")

        Example:
            >>> registry = SectorRegistry()
            >>> calc_class = registry.get_calculator_class("VCB")
            >>> print(calc_class)
            'BankFinancialCalculator'
        """
        ticker_info = self.get_ticker(ticker)
        if not ticker_info:
            return None

        entity_type = ticker_info["entity_type"]
        entity_info = self.get_entity_type_info(entity_type)

        if entity_info:
            return entity_info.get("calculator_class")
        return None

    def get_metric_prefixes(self, sector_name: str) -> List[str]:
        """
        Get metric prefixes for a sector

        Args:
            sector_name: Sector name

        Returns:
            List of metric code prefixes (e.g., ["BIS_", "BBS_", "BCF_"])

        Example:
            >>> registry = SectorRegistry()
            >>> prefixes = registry.get_metric_prefixes("Ngân hàng")
            >>> print(prefixes)
            ['BIS_', 'BBS_', 'BCF_', 'BNOT_']
        """
        sector_info = self.get_sector(sector_name)
        if sector_info:
            return sector_info.get("metric_prefixes", [])
        return []

    def get_key_metrics(self, sector_name: str) -> List[str]:
        """
        Get key calculated metrics for a sector

        Args:
            sector_name: Sector name

        Returns:
            List of key metric names

        Example:
            >>> registry = SectorRegistry()
            >>> metrics = registry.get_key_metrics("Ngân hàng")
            >>> print(metrics)
            ['roe', 'roa', 'nim', 'car', 'npl_ratio']
        """
        sector_info = self.get_sector(sector_name)
        if sector_info:
            return sector_info.get("key_metrics", [])
        return []

    def get_peers(self, ticker: str, exclude_self: bool = True) -> List[str]:
        """
        Get peer tickers (same sector)

        Args:
            ticker: Stock ticker
            exclude_self: Exclude the ticker itself from results

        Returns:
            List of peer tickers

        Example:
            >>> registry = SectorRegistry()
            >>> peers = registry.get_peers("VCB")
            >>> print(peers[:5])
            ['ACB', 'MBB', 'TCB', 'VPB', ...]  # Other banks
        """
        ticker_info = self.get_ticker(ticker)
        if not ticker_info:
            return []

        sector = ticker_info["sector"]
        all_tickers = self.get_tickers_by_sector(sector)

        if exclude_self and ticker in all_tickers:
            all_tickers = [t for t in all_tickers if t != ticker]

        return all_tickers

    def search_sectors(self, keyword: str) -> List[Dict]:
        """
        Search sectors by name

        Args:
            keyword: Search keyword (case-insensitive)

        Returns:
            List of matching sector information dictionaries

        Example:
            >>> registry = SectorRegistry()
            >>> results = registry.search_sectors("xây dựng")
            >>> for sector in results:
            ...     print(f"{sector['name']}: {sector['count']} tickers")
            Xây dựng và Vật liệu: 76 tickers
        """
        results = []
        keyword_lower = keyword.lower()

        for sector_name, sector_info in self.registry["sectors"].items():
            if keyword_lower in sector_name.lower():
                results.append({
                    "name": sector_name,
                    **sector_info
                })

        return results

    def get_all_sectors(self) -> List[str]:
        """
        Get list of all sector names

        Returns:
            List of all sector names

        Example:
            >>> registry = SectorRegistry()
            >>> sectors = registry.get_all_sectors()
            >>> print(len(sectors))
            19
        """
        return list(self.registry["sectors"].keys())

    def get_all_entity_types(self) -> List[str]:
        """
        Get list of all entity types

        Returns:
            List of all entity types

        Example:
            >>> registry = SectorRegistry()
            >>> entities = registry.get_all_entity_types()
            >>> print(entities)
            ['BANK', 'COMPANY', 'INSURANCE', 'SECURITY']
        """
        return list(self.registry["entity_types"].keys())

    def get_statistics(self) -> Dict:
        """
        Get registry statistics

        Returns:
            Statistics dictionary

        Example:
            >>> registry = SectorRegistry()
            >>> stats = registry.get_statistics()
            >>> print(stats['total_tickers'])
            457
        """
        return self.registry["metadata"]

    def get_version(self) -> str:
        """Get registry version"""
        return self.registry.get("version", "unknown")

    def get_last_updated(self) -> str:
        """Get last update timestamp"""
        return self.registry.get("last_updated", "unknown")

    def __repr__(self) -> str:
        """String representation"""
        stats = self.get_statistics()
        return (
            f"SectorRegistry(version={self.get_version()}, "
            f"tickers={stats['total_tickers']}, "
            f"sectors={stats['total_sectors']}, "
            f"entity_types={stats['total_entity_types']})"
        )


# Convenience function for quick access
def get_registry(registry_path: Optional[str] = None) -> SectorRegistry:
    """
    Get global sector registry instance

    Args:
        registry_path: Path to registry JSON (default: auto-detect)

    Returns:
        SectorRegistry instance
    """
    return SectorRegistry(registry_path)


if __name__ == "__main__":
    # Demo usage
    print("=" * 60)
    print("Sector Registry Demo")
    print("=" * 60)

    registry = SectorRegistry()
    print(f"\n{registry}\n")

    # Demo 1: Get ticker info
    print("Demo 1: Get VCB ticker info")
    print("-" * 60)
    vcb_info = registry.get_ticker("VCB")
    if vcb_info:
        print(f"Ticker: VCB")
        print(f"Entity Type: {vcb_info['entity_type']}")
        print(f"Sector: {vcb_info['sector']}")
        print(f"Exchange: {vcb_info['exchange']}")
        print(f"Industry Code: {vcb_info['industry_code']}")

    # Demo 2: Get calculator class
    print("\n\nDemo 2: Get calculator class for VCB")
    print("-" * 60)
    calc_class = registry.get_calculator_class("VCB")
    print(f"Calculator Class: {calc_class}")

    # Demo 3: Get peers
    print("\n\nDemo 3: Get peers for VCB")
    print("-" * 60)
    peers = registry.get_peers("VCB")
    print(f"VCB has {len(peers)} peers in banking sector:")
    print(f"Sample peers: {peers[:10]}")

    # Demo 4: Get sector info
    print("\n\nDemo 4: Get sector info for 'Ngân hàng'")
    print("-" * 60)
    sector_info = registry.get_sector("Ngân hàng")
    if sector_info:
        print(f"Sector: Ngân hàng")
        print(f"Entity Type: {sector_info['entity_type']}")
        print(f"Count: {sector_info['count']} tickers")
        print(f"Metric Prefixes: {sector_info['metric_prefixes']}")
        print(f"Key Metrics: {sector_info['key_metrics']}")

    # Demo 5: Search sectors
    print("\n\nDemo 5: Search sectors for 'xây dựng'")
    print("-" * 60)
    results = registry.search_sectors("xây dựng")
    for sector in results:
        print(f"{sector['name']}: {sector['count']} tickers")

    # Demo 6: Get all tickers in a sector
    print("\n\nDemo 6: Get all construction tickers")
    print("-" * 60)
    construction_tickers = registry.get_tickers_by_sector("Xây dựng và Vật liệu")
    print(f"Found {len(construction_tickers)} construction tickers:")
    print(f"Sample: {construction_tickers[:10]}")

    print("\n" + "=" * 60)
