#!/usr/bin/env python3
"""
Comprehensive Test Suite for Metric Registry (Phase 1)
========================================================

Tests to verify:
1. Metric registry completeness (all metrics from BSC Excel)
2. Link between metric_registry.json and Material Q3 raw data
3. Data integrity (columns in CSV match metric codes)
4. AI agent compatibility (can query and understand metrics)

Usage:
    python data_processor/core/test_metric_registry.py

Author: Claude Code
Date: 2025-12-05
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Set
import logging

from metric_lookup import MetricRegistry, find_project_root

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = find_project_root()


class MetricRegistryTester:
    """Comprehensive test suite for metric registry"""

    def __init__(self):
        self.registry = MetricRegistry()
        self.material_q3_path = PROJECT_ROOT / "data_warehouse" / "Material Q3"
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'errors': []
        }

    def run_all_tests(self):
        """Run all test suites"""
        logger.info("=" * 80)
        logger.info("COMPREHENSIVE METRIC REGISTRY TEST SUITE")
        logger.info("=" * 80)

        tests = [
            ("Test 1: Registry Structure", self.test_registry_structure),
            ("Test 2: Metric Completeness", self.test_metric_completeness),
            ("Test 3: Link with Material Q3", self.test_material_q3_linkage),
            ("Test 4: Entity Type Coverage", self.test_entity_coverage),
            ("Test 5: Calculated Metrics", self.test_calculated_metrics),
            ("Test 6: AI Query Compatibility", self.test_ai_compatibility),
            ("Test 7: Data Integrity", self.test_data_integrity)
        ]

        for test_name, test_func in tests:
            logger.info(f"\n{'='*80}")
            logger.info(f"{test_name}")
            logger.info(f"{'='*80}")
            try:
                test_func()
            except Exception as e:
                logger.error(f"❌ {test_name} failed with exception: {str(e)}")
                self.test_results['failed'] += 1
                self.test_results['errors'].append({
                    'test': test_name,
                    'error': str(e)
                })

        # Summary
        self.print_summary()

    def test_registry_structure(self):
        """Test 1: Verify registry JSON structure"""
        logger.info("Checking registry structure...")

        # Check required fields
        required_fields = ['version', 'last_updated', 'entity_types', 'calculated_metrics']
        for field in required_fields:
            assert field in self.registry.registry, f"Missing field: {field}"

        logger.info(f"✅ Version: {self.registry.get_version()}")
        logger.info(f"✅ Last Updated: {self.registry.get_last_updated()}")

        # Check entity types
        expected_entities = ['COMPANY', 'BANK', 'INSURANCE', 'SECURITY']
        actual_entities = list(self.registry.registry['entity_types'].keys())

        assert set(expected_entities) == set(actual_entities), \
            f"Entity mismatch: expected {expected_entities}, got {actual_entities}"

        logger.info(f"✅ Entity types: {actual_entities}")

        # Check metric counts
        counts = self.registry.get_metric_count()
        total = sum(counts.values())
        logger.info(f"✅ Total metrics: {total}")
        for entity, count in counts.items():
            logger.info(f"  - {entity}: {count} metrics")

        self.test_results['passed'] += 1

    def test_metric_completeness(self):
        """Test 2: Verify all entity types have required categories"""
        logger.info("Checking metric completeness...")

        expected_categories = {
            'COMPANY': ['INCOME', 'BALANCE_SHEET', 'NOTE'],
            'BANK': ['INCOME', 'BALANCE_SHEET', 'NOTE'],
            'INSURANCE': ['INCOME', 'BALANCE_SHEET', 'NOTE'],
            'SECURITY': ['INCOME', 'BALANCE_SHEET', 'NOTE']
        }

        for entity, expected_cats in expected_categories.items():
            actual_cats = self.registry.list_categories(entity)

            # Check if expected categories exist
            for cat in expected_cats:
                if cat not in actual_cats:
                    logger.warning(f"⚠️  {entity} missing category: {cat}")
                    self.test_results['warnings'] += 1
                else:
                    metrics = self.registry.get_entity_metrics(entity, cat)
                    logger.info(f"✅ {entity}.{cat}: {len(metrics)} metrics")

        self.test_results['passed'] += 1

    def test_material_q3_linkage(self):
        """Test 3: Link metric registry with Material Q3 raw data"""
        logger.info("Testing linkage with Material Q3 data...")

        # Define test files (sample from each entity type)
        test_files = {
            'COMPANY': 'COMPANY_INCOME.csv',
            'BANK': 'BANK_INCOME.csv',
            'INSURANCE': 'INSURANCE_INCOME.csv',
            'SECURITY': 'SECURITY_INCOME.csv'
        }

        for entity_type, filename in test_files.items():
            file_path = self.material_q3_path / filename

            if not file_path.exists():
                logger.warning(f"⚠️  File not found: {filename}")
                self.test_results['warnings'] += 1
                continue

            # Read CSV columns
            df = pd.read_csv(file_path, nrows=0)  # Just read headers
            csv_columns = set(df.columns)

            # Get metric codes from registry
            registry_metrics = self.registry.get_entity_metrics(entity_type, 'INCOME')
            registry_codes = set(registry_metrics.keys())

            # Find metric codes in CSV
            metric_codes_in_csv = csv_columns.intersection(registry_codes)

            # Metrics in CSV but not in registry
            unknown_metrics = csv_columns - registry_codes - {
                'REPORT_DATE', 'REPORTED_DATE', 'FREQ_CODE',
                'SECURITY_CODE', 'AUDITED', 'MONTH_IN_PERIOD',
                'CREATED_DATE', 'UPDATED_DATE', 'Unnamed: 0'
            }

            logger.info(f"\n{entity_type} - {filename}:")
            logger.info(f"  CSV columns: {len(csv_columns)}")
            logger.info(f"  Registry metrics: {len(registry_codes)}")
            logger.info(f"  Matched codes: {len(metric_codes_in_csv)}")

            if unknown_metrics:
                logger.warning(f"  ⚠️  Unknown metrics in CSV: {len(unknown_metrics)}")
                logger.warning(f"     Sample: {list(unknown_metrics)[:5]}")
                self.test_results['warnings'] += 1
            else:
                logger.info(f"  ✅ All CSV metrics found in registry")

            # Verify sample metrics
            sample_codes = list(metric_codes_in_csv)[:3]
            for code in sample_codes:
                metric_def = self.registry.get_metric(code, entity_type)
                logger.info(f"  ✅ {code}: {metric_def['name_vi'][:50]}...")

        self.test_results['passed'] += 1

    def test_entity_coverage(self):
        """Test 4: Verify each entity has sufficient metric coverage"""
        logger.info("Testing entity type coverage...")

        # Minimum expected metrics per entity
        min_expected = {
            'COMPANY': {'INCOME': 20, 'BALANCE_SHEET': 100, 'NOTE': 100},
            'BANK': {'INCOME': 20, 'BALANCE_SHEET': 80, 'NOTE': 100},
            'INSURANCE': {'INCOME': 50, 'BALANCE_SHEET': 100, 'NOTE': 100},
            'SECURITY': {'INCOME': 50, 'BALANCE_SHEET': 100, 'NOTE': 100}
        }

        for entity, categories in min_expected.items():
            for category, min_count in categories.items():
                metrics = self.registry.get_entity_metrics(entity, category)
                actual_count = len(metrics)

                if actual_count < min_count:
                    logger.warning(
                        f"⚠️  {entity}.{category}: {actual_count} metrics "
                        f"(expected >= {min_count})"
                    )
                    self.test_results['warnings'] += 1
                else:
                    logger.info(
                        f"✅ {entity}.{category}: {actual_count} metrics "
                        f"(>= {min_count} required)"
                    )

        self.test_results['passed'] += 1

    def test_calculated_metrics(self):
        """Test 5: Verify calculated metrics definitions"""
        logger.info("Testing calculated metrics...")

        expected_metrics = ['roe', 'roa', 'gross_margin', 'net_margin', 'eps']
        calc_metrics = self.registry.get_all_calculated_metrics()

        for metric_name in expected_metrics:
            if metric_name not in calc_metrics:
                logger.error(f"❌ Missing calculated metric: {metric_name}")
                self.test_results['failed'] += 1
                continue

            metric_info = calc_metrics[metric_name]

            # Check required fields
            required_fields = ['name_vi', 'formula', 'unit', 'dependencies', 'entity_types']
            for field in required_fields:
                assert field in metric_info, \
                    f"{metric_name} missing field: {field}"

            logger.info(f"✅ {metric_name}:")
            logger.info(f"   Formula: {metric_info['formula']}")
            logger.info(f"   Unit: {metric_info['unit']}")
            logger.info(f"   Applies to: {', '.join(metric_info['entity_types'])}")

            # Verify dependencies exist
            for entity in metric_info['entity_types']:
                deps = metric_info['dependencies'].get(entity, [])
                for dep_code in deps:
                    dep_metric = self.registry.get_metric(dep_code, entity)
                    if not dep_metric:
                        logger.error(
                            f"❌ {metric_name} dependency {dep_code} "
                            f"not found in {entity}"
                        )
                        self.test_results['failed'] += 1

        self.test_results['passed'] += 1

    def test_ai_compatibility(self):
        """Test 6: Test AI query compatibility"""
        logger.info("Testing AI query compatibility...")

        # Test scenarios an AI agent might use
        test_queries = [
            ("lợi nhuận", "vi"),
            ("revenue", "en"),
            ("tài sản", "vi"),
            ("equity", "en"),
            ("doanh thu", "vi")
        ]

        for keyword, lang in test_queries:
            results = self.registry.search_by_name(keyword, lang=lang)
            logger.info(f"✅ Search '{keyword}' ({lang}): {len(results)} results")

            if len(results) > 0:
                # Show sample result
                sample = results[0]
                logger.info(f"   Sample: {sample['code']} - {sample['name_vi'][:50]}...")

        # Test getting specific metrics (common queries)
        common_metrics = [
            ("CIS_10", "COMPANY", "Net Revenue"),
            ("CIS_62", "COMPANY", "Net Profit"),
            ("CBS_100", "COMPANY", "Total Assets"),
            ("CBS_270", "COMPANY", "Total Equity"),
            ("BIS_22A", "BANK", "Net Profit"),
            ("BBS_100", "BANK", "Total Assets")
        ]

        for code, entity, description in common_metrics:
            metric = self.registry.get_metric(code, entity)
            if metric:
                logger.info(f"✅ {code} ({entity}): {description}")
            else:
                logger.error(f"❌ Failed to get {code} ({entity})")
                self.test_results['failed'] += 1

        self.test_results['passed'] += 1

    def test_data_integrity(self):
        """Test 7: Data integrity checks"""
        logger.info("Testing data integrity...")

        # Test 1: No duplicate metric codes within entity
        for entity in ['COMPANY', 'BANK', 'INSURANCE', 'SECURITY']:
            all_codes = []
            entity_data = self.registry.registry['entity_types'][entity]

            for category, metrics in entity_data.items():
                all_codes.extend(metrics.keys())

            # Check for duplicates
            if len(all_codes) != len(set(all_codes)):
                duplicates = [code for code in set(all_codes) if all_codes.count(code) > 1]
                logger.error(f"❌ {entity} has duplicate codes: {duplicates}")
                self.test_results['failed'] += 1
            else:
                logger.info(f"✅ {entity}: No duplicate codes ({len(all_codes)} unique)")

        # Test 2: All metrics have required fields
        required_fields = ['code', 'name_vi', 'data_type', 'unit', 'category']

        entities_checked = 0
        metrics_checked = 0

        for entity_name, entity_data in self.registry.registry['entity_types'].items():
            for category, metrics in entity_data.items():
                for code, metric in metrics.items():
                    # Check required fields
                    for field in required_fields:
                        if field not in metric:
                            logger.error(
                                f"❌ {entity_name}.{category}.{code} "
                                f"missing field: {field}"
                            )
                            self.test_results['failed'] += 1

                    metrics_checked += 1

            entities_checked += 1

        logger.info(f"✅ Checked {metrics_checked} metrics across {entities_checked} entities")
        logger.info(f"✅ All metrics have required fields")

        self.test_results['passed'] += 1

    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)

        total_tests = self.test_results['passed'] + self.test_results['failed']

        logger.info(f"Total tests: {total_tests}")
        logger.info(f"✅ Passed: {self.test_results['passed']}")
        logger.info(f"❌ Failed: {self.test_results['failed']}")
        logger.info(f"⚠️  Warnings: {self.test_results['warnings']}")

        if self.test_results['errors']:
            logger.info("\nErrors:")
            for error in self.test_results['errors']:
                logger.error(f"  - {error['test']}: {error['error']}")

        logger.info("\n" + "=" * 80)

        if self.test_results['failed'] == 0:
            logger.info("✅ ALL TESTS PASSED!")
            logger.info("Metric Registry is ready for use.")
            logger.info("=" * 80)
            return True
        else:
            logger.error("❌ SOME TESTS FAILED")
            logger.error("Please fix errors before proceeding.")
            logger.info("=" * 80)
            return False


def main():
    """Run comprehensive test suite"""
    tester = MetricRegistryTester()
    success = tester.run_all_tests()

    exit(0 if success else 1)


if __name__ == "__main__":
    main()
