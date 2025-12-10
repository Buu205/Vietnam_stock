#!/usr/bin/env python3
"""
Sector/Industry Registry Builder
=================================

Builds unified sector/industry mapping registry by consolidating:
- ticker_details.json (ticker → entity + sector mapping)
- entity_statistics.json (sector statistics)
- metric_registry.json (entity → metric codes mapping)

Output: sector_industry_registry.json

Usage:
    python data_processor/core/build_sector_registry.py

Author: Claude Code
Date: 2025-12-05
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_project_root() -> Path:
    """Find project root (stock_dashboard directory)"""
    current = Path(__file__).resolve()
    while current.parent != current:
        if current.name == 'stock_dashboard':
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent


PROJECT_ROOT = find_project_root()


class SectorRegistryBuilder:
    """
    Build unified sector/industry registry

    Consolidates multiple data sources into single source of truth
    for sector, industry, and entity type mappings.
    """

    def __init__(self):
        """Initialize paths to source files"""
        self.ticker_details_path = PROJECT_ROOT / "data_warehouse" / "raw" / "metadata" / "ticker_details.json"
        self.entity_stats_path = PROJECT_ROOT / "data_warehouse" / "raw" / "metadata" / "entity_statistics.json"
        self.metric_registry_path = PROJECT_ROOT / "data_warehouse" / "metadata" / "metric_registry.json"
        self.output_path = PROJECT_ROOT / "data_warehouse" / "metadata" / "sector_industry_registry.json"

        # Data containers
        self.ticker_details = {}
        self.entity_stats = {}
        self.metric_registry = {}

        # Mapping for metric prefixes per entity type
        self.metric_prefixes_map = {
            "COMPANY": ["CIS_", "CBS_", "CCF_", "CNOT_"],
            "BANK": ["BIS_", "BBS_", "BCF_", "BNOT_"],
            "SECURITY": ["SIS_", "SBS_", "SCF_", "SNOT_"],
            "INSURANCE": ["IIS_", "IBS_", "ICF_", "INOT_"]
        }

        # Key metrics per entity type
        self.key_metrics_map = {
            "COMPANY": ["roe", "roa", "gross_margin", "net_margin", "eps"],
            "BANK": ["roe", "roa", "nim", "car", "npl_ratio"],
            "SECURITY": ["roe", "roa", "commission_ratio", "leverage_ratio"],
            "INSURANCE": ["roe", "roa", "combined_ratio", "loss_ratio"]
        }

    def load_source_files(self):
        """Load all source JSON files"""
        logger.info("Loading source files...")

        # Load ticker details
        if not self.ticker_details_path.exists():
            raise FileNotFoundError(f"Ticker details not found: {self.ticker_details_path}")
        with open(self.ticker_details_path, 'r', encoding='utf-8') as f:
            self.ticker_details = json.load(f)
        logger.info(f"  Loaded {len(self.ticker_details)} tickers from ticker_details.json")

        # Load entity statistics
        if not self.entity_stats_path.exists():
            raise FileNotFoundError(f"Entity statistics not found: {self.entity_stats_path}")
        with open(self.entity_stats_path, 'r', encoding='utf-8') as f:
            self.entity_stats = json.load(f)
        logger.info(f"  Loaded entity statistics for {len(self.entity_stats['by_sector'])} sectors")

        # Load metric registry (for linking)
        if not self.metric_registry_path.exists():
            raise FileNotFoundError(f"Metric registry not found: {self.metric_registry_path}")
        with open(self.metric_registry_path, 'r', encoding='utf-8') as f:
            self.metric_registry = json.load(f)
        logger.info(f"  Loaded metric registry v{self.metric_registry['version']}")

    def build_entity_types_section(self) -> Dict:
        """Build entity_types section with metadata"""
        logger.info("Building entity_types section...")

        entity_types = {}

        for entity_type, count in self.entity_stats['by_entity'].items():
            # Get sectors for this entity type
            sectors = [
                sector_name
                for sector_name, sector_info in self.entity_stats['by_sector'].items()
                if sector_info['entity'] == entity_type
            ]

            entity_types[entity_type] = {
                "description": self._get_entity_description(entity_type),
                "count": count,
                "metric_registry_key": entity_type,
                "calculator_class": f"{entity_type.capitalize()}FinancialCalculator",
                "sectors": sectors
            }

        logger.info(f"  Built {len(entity_types)} entity types")
        return entity_types

    def build_sectors_section(self) -> Dict:
        """Build sectors section with full details"""
        logger.info("Building sectors section...")

        sectors = {}

        for sector_name, sector_info in self.entity_stats['by_sector'].items():
            entity_type = sector_info['entity']

            # Get all tickers for this sector
            sector_tickers = [
                ticker
                for ticker, details in self.ticker_details.items()
                if details['sector'] == sector_name
            ]

            sectors[sector_name] = {
                "entity_type": entity_type,
                "count": sector_info['count'],
                "description": self._get_sector_description(sector_name),
                "tickers": sorted(sector_tickers),
                "metric_prefixes": self.metric_prefixes_map.get(entity_type, []),
                "key_metrics": self.key_metrics_map.get(entity_type, [])
            }

        logger.info(f"  Built {len(sectors)} sectors")
        return sectors

    def build_ticker_mapping_section(self) -> Dict:
        """Build ticker_mapping section"""
        logger.info("Building ticker_mapping section...")

        ticker_mapping = {}

        for ticker, details in self.ticker_details.items():
            ticker_mapping[ticker] = {
                "entity_type": details['entity'],
                "sector": details['sector'],
                "name": self._get_ticker_name(ticker),
                "exchange": self._get_exchange(ticker),
                "industry_code": self._get_industry_code(details['sector'])
            }

        logger.info(f"  Built ticker mapping for {len(ticker_mapping)} tickers")
        return ticker_mapping

    def build_sector_to_entity_mapping(self) -> Dict:
        """Build simple sector → entity type mapping"""
        logger.info("Building sector_to_entity_mapping...")

        mapping = {}
        for sector_name, sector_info in self.entity_stats['by_sector'].items():
            mapping[sector_name] = sector_info['entity']

        logger.info(f"  Built mapping for {len(mapping)} sectors")
        return mapping

    def validate_registry(self, registry: Dict) -> bool:
        """Validate registry for completeness and consistency"""
        logger.info("Validating registry...")

        issues = []

        # Check 1: All tickers have entity_type
        for ticker, info in registry['ticker_mapping'].items():
            if not info.get('entity_type'):
                issues.append(f"Ticker {ticker} missing entity_type")

        # Check 2: All tickers have sector
        for ticker, info in registry['ticker_mapping'].items():
            if not info.get('sector'):
                issues.append(f"Ticker {ticker} missing sector")

        # Check 3: Sector → Entity mapping is consistent
        for ticker, info in registry['ticker_mapping'].items():
            sector = info['sector']
            entity_type = info['entity_type']
            expected_entity = registry['sector_to_entity_mapping'].get(sector)
            if expected_entity != entity_type:
                issues.append(
                    f"Ticker {ticker}: sector '{sector}' should map to {expected_entity}, got {entity_type}"
                )

        # Check 4: All entity types have calculators
        for entity_type in registry['entity_types'].keys():
            calculator = registry['entity_types'][entity_type]['calculator_class']
            if not calculator:
                issues.append(f"Entity type {entity_type} missing calculator_class")

        # Check 5: All entity types have metric prefixes
        for entity_type in registry['entity_types'].keys():
            sectors = registry['entity_types'][entity_type]['sectors']
            for sector in sectors:
                prefixes = registry['sectors'][sector]['metric_prefixes']
                if not prefixes:
                    issues.append(f"Sector {sector} missing metric_prefixes")

        if issues:
            logger.error(f"Validation failed with {len(issues)} issues:")
            for issue in issues[:10]:  # Show first 10 issues
                logger.error(f"  - {issue}")
            return False

        logger.info("  ✓ All validation checks passed")
        return True

    def build_registry(self) -> Dict:
        """Build complete registry"""
        logger.info("=" * 60)
        logger.info("Building Sector/Industry Registry")
        logger.info("=" * 60)

        # Load source files
        self.load_source_files()

        # Build sections
        entity_types = self.build_entity_types_section()
        sectors = self.build_sectors_section()
        ticker_mapping = self.build_ticker_mapping_section()
        sector_to_entity = self.build_sector_to_entity_mapping()

        # Assemble registry
        registry = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "metadata": {
                "total_tickers": len(ticker_mapping),
                "total_sectors": len(sectors),
                "total_entity_types": len(entity_types)
            },
            "entity_types": entity_types,
            "sectors": sectors,
            "ticker_mapping": ticker_mapping,
            "sector_to_entity_mapping": sector_to_entity
        }

        # Validate
        if not self.validate_registry(registry):
            raise ValueError("Registry validation failed")

        return registry

    def save_registry(self, registry: Dict):
        """Save registry to JSON file"""
        logger.info(f"Saving registry to {self.output_path}...")

        # Create directory if needed
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save with pretty formatting
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)

        file_size_kb = self.output_path.stat().st_size / 1024
        logger.info(f"  ✓ Registry saved ({file_size_kb:.1f} KB)")

    def print_summary(self, registry: Dict):
        """Print summary of registry"""
        logger.info("")
        logger.info("=" * 60)
        logger.info("REGISTRY SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Version: {registry['version']}")
        logger.info(f"Total Tickers: {registry['metadata']['total_tickers']}")
        logger.info(f"Total Sectors: {registry['metadata']['total_sectors']}")
        logger.info(f"Total Entity Types: {registry['metadata']['total_entity_types']}")
        logger.info("")
        logger.info("Entity Types:")
        for entity_type, info in registry['entity_types'].items():
            logger.info(f"  {entity_type}: {info['count']} tickers, {len(info['sectors'])} sectors")
        logger.info("")
        logger.info("Top 5 Sectors by Count:")
        sorted_sectors = sorted(
            registry['sectors'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        for sector_name, sector_info in sorted_sectors[:5]:
            logger.info(f"  {sector_name}: {sector_info['count']} tickers ({sector_info['entity_type']})")
        logger.info("=" * 60)

    # Helper methods

    def _get_entity_description(self, entity_type: str) -> str:
        """Get description for entity type"""
        descriptions = {
            "COMPANY": "Các ngành sản xuất và dịch vụ",
            "BANK": "Ngân hàng thương mại",
            "SECURITY": "Công ty chứng khoán",
            "INSURANCE": "Công ty bảo hiểm"
        }
        return descriptions.get(entity_type, "")

    def _get_sector_description(self, sector_name: str) -> str:
        """Get description for sector"""
        # Simple descriptions, can be expanded
        return f"Ngành {sector_name}"

    def _get_ticker_name(self, ticker: str) -> str:
        """Get full name for ticker (placeholder, can be enhanced with real data)"""
        # TODO: Load from actual ticker names database if available
        return ""

    def _get_exchange(self, ticker: str) -> str:
        """Get exchange for ticker (placeholder)"""
        # TODO: Determine from ticker or load from database
        # Most common is HOSE for large caps
        return "HOSE"

    def _get_industry_code(self, sector_name: str) -> str:
        """Get industry code from sector name"""
        # Map sector names to industry codes
        industry_codes = {
            "Ngân hàng": "BANK",
            "Dịch vụ tài chính": "SECURITY",
            "Bảo hiểm": "INSURANCE",
            "Xây dựng và Vật liệu": "CONSTRUCTION",
            "Thực phẩm và đồ uống": "FOOD_BEVERAGE",
            "Tài nguyên Cơ bản": "BASIC_RESOURCES",
            "Điện, nước & xăng dầu khí đốt": "UTILITIES",
            "Công nghệ Thông tin": "IT",
            "Hóa chất": "CHEMICALS",
            "Hàng & Dịch vụ Công nghiệp": "INDUSTRIAL",
            "Bán lẻ": "RETAIL",
            "Bất động sản": "REAL_ESTATE",
            "Truyền thông": "MEDIA",
            "Du lịch và Giải trí": "TRAVEL_LEISURE",
            "Viễn thông": "TELECOM",
            "Ô tô và phụ tùng": "AUTOMOBILE",
            "Dầu khí": "OIL_GAS",
            "Hàng cá nhân & Gia dụng": "PERSONAL_GOODS",
            "Y tế": "HEALTHCARE"
        }
        return industry_codes.get(sector_name, "OTHER")


def main():
    """Main entry point"""
    try:
        builder = SectorRegistryBuilder()
        registry = builder.build_registry()
        builder.save_registry(registry)
        builder.print_summary(registry)

        logger.info("")
        logger.info("✓ Sector/Industry Registry built successfully!")
        logger.info(f"Output: {builder.output_path}")

    except Exception as e:
        logger.error(f"Failed to build registry: {e}")
        raise


if __name__ == "__main__":
    main()
