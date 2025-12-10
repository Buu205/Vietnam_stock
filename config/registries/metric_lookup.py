#!/usr/bin/env python3
"""
Metric Registry Lookup Utility
================================

Fast lookup utility for metric definitions from metric_registry.json

Features:
- Get metric by code (CIS_62, BBS_100, etc.)
- Search metrics by Vietnamese/English name
- Get calculated metric formulas
- Validate metric dependencies

Usage:
    from PROCESSORS.core.registries.metric_lookup import MetricRegistry

    registry = MetricRegistry()

    # Get specific metric
    metric = registry.get_metric("CIS_62", "COMPANY")
    # {'code': 'CIS_62', 'name_vi': 'Lợi nhuận sau thuế...', ...}

    # Search by name
    results = registry.search_by_name("lợi nhuận")
    # [{'code': 'CIS_20', ...}, {'code': 'CIS_62', ...}]

    # Get calculated metric formula
    roe_formula = registry.get_calculated_metric_formula("roe")
    # {'formula': '(net_profit / total_equity) * 100', ...}

Author: Claude Code
Date: 2025-12-05
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


def find_project_root() -> Path:
    """Find project root (Vietnam_dashboard directory)"""
    current = Path(__file__).resolve()
    while current.parent != current:
        if current.name in ['Vietnam_dashboard', 'stock_dashboard']:
            return current
        current = current.parent
    return Path(__file__).resolve().parents[3]  # From registries/ -> core/ -> PROCESSORS/ -> project root


PROJECT_ROOT = find_project_root()


class MetricRegistry:
    """
    Fast lookup for metric definitions from metric_registry.json

    This class provides efficient access to:
    - Raw metric codes from BSC database (CIS_*, BBS_*, etc.)
    - Calculated metric formulas (ROE, gross_margin, etc.)
    - Metric dependencies and validation
    """

    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize metric registry

        Args:
            registry_path: Path to metric_registry.json (default: auto-detect)
        """
        if registry_path is None:
            registry_path = PROJECT_ROOT / "DATA" / "metadata" / "metric_registry.json"
        else:
            registry_path = Path(registry_path)

        if not registry_path.exists():
            raise FileNotFoundError(
                f"Metric registry not found: {registry_path}\n"
                f"Please run: python data_processor/core/build_metric_registry.py"
            )

        # Load registry
        with open(registry_path, 'r', encoding='utf-8') as f:
            self.registry = json.load(f)

        logger.info(f"Loaded metric registry v{self.registry['version']}")
        logger.info(f"  Total entity types: {len(self.registry['entity_types'])}")
        logger.info(f"  Calculated metrics: {len(self.registry['calculated_metrics'])}")

    def get_metric(self, code: str, entity_type: Optional[str] = None) -> Optional[Dict]:
        """
        Get metric definition by code

        Args:
            code: Metric code (e.g., CIS_62, BBS_100)
            entity_type: Entity type to search in (COMPANY, BANK, etc.)
                        If None, searches all entity types

        Returns:
            Metric definition dictionary, or None if not found

        Example:
            >>> registry = MetricRegistry()
            >>> metric = registry.get_metric("CIS_62", "COMPANY")
            >>> print(metric['name_vi'])
            'Lợi nhuận sau thuế công ty mẹ'
        """
        if entity_type:
            # Search in specific entity type
            entity_data = self.registry["entity_types"].get(entity_type)
            if not entity_data:
                return None

            for category_name, metrics in entity_data.items():
                if code in metrics:
                    return metrics[code]
        else:
            # Search all entity types
            for entity_name, entity_data in self.registry["entity_types"].items():
                for category_name, metrics in entity_data.items():
                    if code in metrics:
                        return metrics[code]

        return None

    def search_by_name(self, keyword: str, lang: str = "vi", entity_type: Optional[str] = None) -> List[Dict]:
        """
        Search metrics by Vietnamese or English name

        Args:
            keyword: Search keyword (case-insensitive)
            lang: Language to search ('vi' or 'en')
            entity_type: Filter by entity type (optional)

        Returns:
            List of matching metric definitions

        Example:
            >>> registry = MetricRegistry()
            >>> results = registry.search_by_name("lợi nhuận")
            >>> for metric in results:
            ...     print(f"{metric['code']}: {metric['name_vi']}")
            CIS_20: Lợi nhuận gộp...
            CIS_62: Lợi nhuận sau thuế...
        """
        results = []
        name_field = f"name_{lang}"
        keyword_lower = keyword.lower()

        # Determine which entities to search
        if entity_type:
            entities_to_search = {entity_type: self.registry["entity_types"][entity_type]}
        else:
            entities_to_search = self.registry["entity_types"]

        # Search through metrics
        for entity_name, entity_data in entities_to_search.items():
            for category_name, metrics in entity_data.items():
                for code, metric in metrics.items():
                    metric_name = metric.get(name_field, "").lower()
                    if keyword_lower in metric_name:
                        results.append(metric)

        return results

    def get_calculated_metric_formula(self, metric_name: str) -> Optional[Dict]:
        """
        Get formula for calculated metrics (ROE, gross_margin, etc.)

        Args:
            metric_name: Calculated metric name (roe, roa, gross_margin, etc.)

        Returns:
            Formula information dictionary, or None if not found

        Example:
            >>> registry = MetricRegistry()
            >>> roe_info = registry.get_calculated_metric_formula("roe")
            >>> print(roe_info['formula'])
            '(net_profit / total_equity) * 100'
            >>> print(roe_info['dependencies']['COMPANY'])
            ['CIS_62', 'CBS_270']
        """
        return self.registry["calculated_metrics"].get(metric_name)

    def get_all_calculated_metrics(self) -> Dict[str, Dict]:
        """
        Get all calculated metric definitions

        Returns:
            Dictionary of all calculated metrics

        Example:
            >>> registry = MetricRegistry()
            >>> calc_metrics = registry.get_all_calculated_metrics()
            >>> for name, info in calc_metrics.items():
            ...     print(f"{name}: {info['name_vi']}")
        """
        return self.registry["calculated_metrics"]

    def validate_dependencies(self, metric_name: str, available_codes: Set[str],
                            entity_type: str) -> Dict[str, any]:
        """
        Check if all dependencies are available for calculated metric

        Args:
            metric_name: Calculated metric name (roe, roa, etc.)
            available_codes: Set of available metric codes in dataset
            entity_type: Entity type (COMPANY, BANK, etc.)

        Returns:
            {
                'is_valid': bool,
                'missing': List[str],  # Missing dependencies
                'available': List[str]  # Available dependencies
            }

        Example:
            >>> registry = MetricRegistry()
            >>> available = {'CIS_62', 'CBS_270', 'CIS_10'}
            >>> result = registry.validate_dependencies("roe", available, "COMPANY")
            >>> if result['is_valid']:
            ...     print("All dependencies available!")
            >>> else:
            ...     print(f"Missing: {result['missing']}")
        """
        formula_info = self.get_calculated_metric_formula(metric_name)
        if not formula_info:
            return {
                'is_valid': False,
                'error': f'Calculated metric "{metric_name}" not found',
                'missing': [],
                'available': []
            }

        # Get dependencies for this entity type
        if entity_type not in formula_info.get('entity_types', []):
            return {
                'is_valid': False,
                'error': f'Metric "{metric_name}" not applicable to {entity_type}',
                'missing': [],
                'available': []
            }

        deps = set(formula_info["dependencies"].get(entity_type, []))

        # Check availability
        available = deps.intersection(available_codes)
        missing = deps - available_codes

        return {
            'is_valid': len(missing) == 0,
            'missing': list(missing),
            'available': list(available),
            'total_required': len(deps)
        }

    def get_entity_metrics(self, entity_type: str, category: Optional[str] = None) -> Dict[str, Dict]:
        """
        Get all metrics for an entity type

        Args:
            entity_type: Entity type (COMPANY, BANK, INSURANCE, SECURITY)
            category: Filter by category (INCOME, BALANCE_SHEET, etc.)

        Returns:
            Dictionary of metrics for the entity/category

        Example:
            >>> registry = MetricRegistry()
            >>> income_metrics = registry.get_entity_metrics("COMPANY", "INCOME")
            >>> print(f"COMPANY has {len(income_metrics)} income statement metrics")
        """
        entity_data = self.registry["entity_types"].get(entity_type)
        if not entity_data:
            return {}

        if category:
            return entity_data.get(category, {})
        else:
            # Return all metrics across categories
            all_metrics = {}
            for cat_metrics in entity_data.values():
                all_metrics.update(cat_metrics)
            return all_metrics

    def get_metric_count(self, entity_type: Optional[str] = None) -> Dict[str, int]:
        """
        Get count of metrics by entity type

        Args:
            entity_type: Entity type to count (or None for all)

        Returns:
            Dictionary of metric counts

        Example:
            >>> registry = MetricRegistry()
            >>> counts = registry.get_metric_count()
            >>> for entity, count in counts.items():
            ...     print(f"{entity}: {count} metrics")
        """
        if entity_type:
            entities = {entity_type: self.registry["entity_types"][entity_type]}
        else:
            entities = self.registry["entity_types"]

        counts = {}
        for entity_name, entity_data in entities.items():
            total = sum(len(metrics) for metrics in entity_data.values())
            counts[entity_name] = total

        return counts

    def list_categories(self, entity_type: str) -> List[str]:
        """
        List all categories for an entity type

        Args:
            entity_type: Entity type (COMPANY, BANK, etc.)

        Returns:
            List of category names

        Example:
            >>> registry = MetricRegistry()
            >>> categories = registry.list_categories("COMPANY")
            >>> print(categories)
            ['INCOME', 'BALANCE_SHEET', 'NOTE']
        """
        entity_data = self.registry["entity_types"].get(entity_type, {})
        return list(entity_data.keys())

    def get_version(self) -> str:
        """Get registry version"""
        return self.registry.get("version", "unknown")

    def get_last_updated(self) -> str:
        """Get last update timestamp"""
        return self.registry.get("last_updated", "unknown")

    def __repr__(self) -> str:
        """String representation"""
        total_metrics = sum(self.get_metric_count().values())
        calc_metrics = len(self.registry["calculated_metrics"])
        return (
            f"MetricRegistry(version={self.get_version()}, "
            f"raw_metrics={total_metrics}, "
            f"calculated_metrics={calc_metrics})"
        )


# Convenience function for quick access
def get_registry(registry_path: Optional[str] = None) -> MetricRegistry:
    """
    Get global metric registry instance

    Args:
        registry_path: Path to registry JSON (default: auto-detect)

    Returns:
        MetricRegistry instance
    """
    return MetricRegistry(registry_path)


if __name__ == "__main__":
    # Demo usage
    print("=" * 60)
    print("Metric Registry Demo")
    print("=" * 60)

    registry = MetricRegistry()
    print(f"\n{registry}\n")

    # Demo 1: Get specific metric
    print("Demo 1: Get CIS_62 (Net Profit)")
    print("-" * 60)
    cis_62 = registry.get_metric("CIS_62", "COMPANY")
    if cis_62:
        print(f"Code: {cis_62['code']}")
        print(f"Name (VI): {cis_62['name_vi']}")
        print(f"Data Type: {cis_62['data_type']}")
        print(f"Unit: {cis_62['unit']}")

    # Demo 2: Search by name
    print("\n\nDemo 2: Search for 'lợi nhuận'")
    print("-" * 60)
    results = registry.search_by_name("lợi nhuận", entity_type="COMPANY")
    print(f"Found {len(results)} metrics:")
    for metric in results[:5]:  # Show first 5
        print(f"  {metric['code']}: {metric['name_vi']}")

    # Demo 3: Get calculated metric
    print("\n\nDemo 3: Get ROE formula")
    print("-" * 60)
    roe = registry.get_calculated_metric_formula("roe")
    if roe:
        print(f"Name: {roe['name_vi']}")
        print(f"Formula: {roe['formula']}")
        print(f"Unit: {roe['unit']}")
        print(f"Dependencies (COMPANY): {roe['dependencies']['COMPANY']}")

    # Demo 4: Validate dependencies
    print("\n\nDemo 4: Validate ROE dependencies")
    print("-" * 60)
    available_codes = {'CIS_62', 'CBS_270', 'CBS_100', 'CIS_10'}
    validation = registry.validate_dependencies("roe", available_codes, "COMPANY")
    print(f"Is valid: {validation['is_valid']}")
    print(f"Available: {validation['available']}")
    print(f"Missing: {validation['missing']}")

    # Demo 5: Metric counts
    print("\n\nDemo 5: Metric counts by entity")
    print("-" * 60)
    counts = registry.get_metric_count()
    for entity, count in counts.items():
        print(f"{entity}: {count} metrics")

    print("\n" + "=" * 60)
