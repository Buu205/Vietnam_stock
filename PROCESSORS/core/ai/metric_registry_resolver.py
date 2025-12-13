#!/usr/bin/env python3
"""
Metric Registry Resolver - Ánh xạ tên metric sang metric codes
==============================================================

Sử dụng metric_registry.json để:
1. Tìm metric code từ tên tiếng Việt
2. Validate metric tồn tại cho entity type
3. Lấy thông tin chi tiết về metric (data type, unit, etc.)

Author: AI Assistant
Date: 2025-12-12
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Try to import fuzzywuzzy for fuzzy matching (optional)
try:
    from fuzzywuzzy import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False

from config.registries import MetricRegistry


@dataclass
class MetricInfo:
    """
    Thông tin chi tiết về một metric

    Attributes:
        code: Metric code (e.g., CIS_25)
        name_vi: Tên tiếng Việt
        name_en: Tên tiếng Anh
        data_type: Loại dữ liệu (number, percent, currency)
        unit: Đơn vị (đ, %, etc.)
        entity_type: Loại thực thể (COMPANY, BANK, etc.)
        category: Danh mục (IS, BS, CF)
    """
    code: str
    name_vi: str
    name_en: str
    data_type: Optional[str] = None
    unit: Optional[str] = None
    entity_type: Optional[str] = None
    category: Optional[str] = None


class MetricRegistryResolver:
    """
    Resolver để tìm metric codes từ tên tiếng Việt/Anh

    Sử dụng MetricRegistry để tra cứu và validate metrics.
    """

    def __init__(self):
        """Khởi tạo resolver với metric registry."""
        self.metric_registry = MetricRegistry()

    def resolve_metric_name(
        self,
        metric_name: str,
        entity_type: Optional[str] = None,
        language: str = 'vi',
        fuzzy_threshold: int = 80
    ) -> List[MetricInfo]:
        """
        Tìm metric codes từ tên metric

        Args:
            metric_name: Tên metric (tiếng Việt hoặc Anh)
            entity_type: Loại thực thể (COMPANY, BANK, etc.) - optional
            language: Ngôn ngữ ('vi' hoặc 'en')
            fuzzy_threshold: Ngưỡng fuzzy matching (0-100)

        Returns:
            Danh sách MetricInfo objects matching

        Examples:
            >>> resolver = MetricRegistryResolver()
            >>> results = resolver.resolve_metric_name("doanh thu thuần", "COMPANY")
            >>> results[0].code
            'CIS_10'
        """
        metric_name = metric_name.lower().strip()
        results = []

        # Use MetricRegistry's search_by_name method
        lang_code = 'vi' if language == 'vi' else 'en'
        search_results = self.metric_registry.search_by_name(
            metric_name,
            lang=lang_code,
            entity_type=entity_type
        )

        for metric_data in search_results:
            code = metric_data.get('code', '')
            if code:
                results.append(self._create_metric_info(code, metric_data, entity_type))

        return results

    def resolve_metric_code(
        self,
        metric_code: str,
        entity_type: Optional[str] = None
    ) -> Optional[MetricInfo]:
        """
        Validate và lấy thông tin về một metric code

        Args:
            metric_code: Metric code (e.g., CIS_10)
            entity_type: Loại thực thể để validate

        Returns:
            MetricInfo object hoặc None nếu không tìm thấy
        """
        metric_code = metric_code.upper().strip()
        metric_data = self.metric_registry.get_metric(metric_code, entity_type)

        if metric_data:
            return self._create_metric_info(metric_code, metric_data, entity_type)

        return None

    def validate_metrics_for_entity(
        self,
        metric_codes: List[str],
        entity_type: str
    ) -> Tuple[List[str], List[str]]:
        """
        Validate danh sách metric codes cho một entity type

        Args:
            metric_codes: Danh sách metric codes
            entity_type: Loại thực thể (COMPANY, BANK, etc.)

        Returns:
            Tuple of (valid_codes, invalid_codes)
        """
        valid_codes = []
        invalid_codes = []

        for code in metric_codes:
            metric_data = self.metric_registry.get_metric(code, entity_type)
            if metric_data:
                valid_codes.append(code)
            else:
                invalid_codes.append(code)

        return valid_codes, invalid_codes

    def search_by_keywords(
        self,
        keywords: List[str],
        entity_type: Optional[str] = None,
        language: str = 'vi'
    ) -> List[MetricInfo]:
        """
        Tìm metrics bằng danh sách keywords

        Args:
            keywords: Danh sách keywords (e.g., ['doanh thu', 'thuần'])
            entity_type: Loại thực thể
            language: Ngôn ngữ

        Returns:
            Danh sách MetricInfo matching
        """
        results = []

        # Search for each keyword and find intersection
        all_results = []
        for keyword in keywords:
            search_results = self.metric_registry.search_by_name(
                keyword,
                lang='vi' if language == 'vi' else 'en',
                entity_type=entity_type
            )
            all_results.extend(search_results)

        # Convert to MetricInfo
        seen_codes = set()
        for metric_data in all_results:
            code = metric_data.get('code', '')
            if code and code not in seen_codes:
                results.append(self._create_metric_info(code, metric_data, entity_type))
                seen_codes.add(code)

        return results

    def get_metric_by_category(
        self,
        category: str,
        entity_type: str
    ) -> List[MetricInfo]:
        """
        Lấy tất cả metrics trong một category

        Args:
            category: Category code (IS, BS, CF)
            entity_type: Loại thực thể

        Returns:
            Danh sách MetricInfo
        """
        results = []

        # Use MetricRegistry to get all metrics for entity type
        # Then filter by category prefix
        prefix = f"{entity_type[0]}{category}"  # e.g., "CIS" for COMPANY Income Statement

        # Search with prefix to get all metrics in category
        search_results = self.metric_registry.search_by_name(
            "",  # Empty search to get all
            lang='vi',
            entity_type=entity_type
        )

        seen_codes = set()
        for metric_data in search_results:
            code = metric_data.get('code', '')
            if code and code.startswith(prefix) and code not in seen_codes:
                results.append(self._create_metric_info(code, metric_data, entity_type))
                seen_codes.add(code)

        return results

    def _create_metric_info(
        self,
        code: str,
        metric_data: Dict,
        entity_type: Optional[str]
    ) -> MetricInfo:
        """Create MetricInfo object from metric data."""
        return MetricInfo(
            code=code,
            name_vi=metric_data.get('name_vi', metric_data.get('metric_name_vie', '')),
            name_en=metric_data.get('name_en', metric_data.get('metric_name_eng', '')),
            data_type=metric_data.get('data_type', 'number'),
            unit=metric_data.get('unit', ''),
            entity_type=entity_type,
            category=code.split('_')[0][1:] if '_' in code else ''  # Extract category from code (e.g., "IS" from "CIS")
        )


# Singleton instance
metric_resolver = MetricRegistryResolver()


if __name__ == "__main__":
    # Test cases
    resolver = MetricRegistryResolver()

    print("Metric Registry Resolver Test Cases:")
    print("=" * 80)

    # Test 1: Resolve by Vietnamese name
    print("\n1. Resolve by Vietnamese name: 'doanh thu thuần'")
    results = resolver.resolve_metric_name("doanh thu thuần", "COMPANY", language='vi')
    if results:
        for r in results:
            print(f"   Code: {r.code}, Name VI: {r.name_vi}, Name EN: {r.name_en}")
    else:
        print("   No results found")

    # Test 2: Validate metric code
    print("\n2. Validate metric code: 'CIS_10' for COMPANY")
    metric_info = resolver.resolve_metric_code("CIS_10", "COMPANY")
    if metric_info:
        print(f"   Valid! Name: {metric_info.name_vi} ({metric_info.name_en})")
    else:
        print("   Invalid metric code")

    # Test 3: Validate multiple codes
    print("\n3. Validate multiple codes for COMPANY")
    codes = ["CIS_10", "CIS_25", "CBS_270", "INVALID_CODE"]
    valid, invalid = resolver.validate_metrics_for_entity(codes, "COMPANY")
    print(f"   Valid: {valid}")
    print(f"   Invalid: {invalid}")

    # Test 4: Search by keywords
    print("\n4. Search by keywords: ['lợi nhuận']")
    results = resolver.search_by_keywords(["lợi nhuận"], "COMPANY", language='vi')
    print(f"   Found {len(results)} metrics")
    for r in results[:3]:  # Show first 3
        print(f"   - {r.code}: {r.name_vi}")

    # Test 5: Get metrics by category
    print("\n5. Get Income Statement metrics for COMPANY")
    results = resolver.get_metric_by_category("IS", "COMPANY")
    print(f"   Found {len(results)} metrics in category IS")
    for r in results[:5]:  # Show first 5
        print(f"   - {r.code}: {r.name_vi}")
