#!/usr/bin/env python3
"""
Test Suite for Unified Ticker Mapper
=====================================

Comprehensive tests for the integrated mapping system:
- SectorRegistry
- MetricRegistry
- UnifiedTickerMapper

Author: Claude Code
Date: 2025-12-05
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PROCESSORS.core.shared.unified_mapper import UnifiedTickerMapper
from config.registries import SectorRegistry, MetricRegistry


def test_sector_registry():
    """Test SectorRegistry functionality"""
    print("=" * 70)
    print("TEST 1: Sector Registry")
    print("=" * 70)

    registry = SectorRegistry()

    # Test 1.1: Get ticker info
    print("\n1.1 Get ticker info for ACB (BANK)")
    acb_info = registry.get_ticker("ACB")
    assert acb_info is not None, "ACB should exist"
    assert acb_info['entity_type'] == "BANK", "ACB should be BANK"
    assert acb_info['sector'] == "Ngân hàng", "ACB should be in Ngân hàng sector"
    print(f"  ✓ ACB: {acb_info['entity_type']} - {acb_info['sector']}")

    # Test 1.2: Get sector info
    print("\n1.2 Get sector info for Ngân hàng")
    bank_sector = registry.get_sector("Ngân hàng")
    assert bank_sector is not None, "Ngân hàng sector should exist"
    assert bank_sector['entity_type'] == "BANK"
    assert bank_sector['count'] == 24, "Should have 24 banks"
    print(f"  ✓ Ngân hàng: {bank_sector['count']} tickers")

    # Test 1.3: Get peers
    print("\n1.3 Get peers for ACB")
    peers = registry.get_peers("ACB")
    assert len(peers) == 23, "ACB should have 23 peers (24 banks - 1 itself)"
    assert "VCB" in peers, "VCB should be a peer"
    assert "ACB" not in peers, "ACB should not be in its own peers"
    print(f"  ✓ Found {len(peers)} peers for ACB")

    # Test 1.4: Get calculator class
    print("\n1.4 Get calculator class for ACB")
    calc_class = registry.get_calculator_class("ACB")
    assert calc_class == "BankFinancialCalculator"
    print(f"  ✓ Calculator: {calc_class}")

    # Test 1.5: Get metric prefixes
    print("\n1.5 Get metric prefixes for Ngân hàng sector")
    prefixes = registry.get_metric_prefixes("Ngân hàng")
    assert "BIS_" in prefixes, "Should have BIS_ prefix"
    assert "BBS_" in prefixes, "Should have BBS_ prefix"
    print(f"  ✓ Prefixes: {prefixes}")

    print("\n✅ TEST 1 PASSED: Sector Registry")
    return True


def test_metric_registry():
    """Test MetricRegistry functionality"""
    print("\n" + "=" * 70)
    print("TEST 2: Metric Registry")
    print("=" * 70)

    registry = MetricRegistry()

    # Test 2.1: Get metric by code
    print("\n2.1 Get metric BIS_22A for BANK")
    metric = registry.get_metric("BIS_22A", "BANK")
    assert metric is not None, "BIS_22A should exist for BANK"
    assert metric['code'] == "BIS_22A"
    assert 'name_vi' in metric
    print(f"  ✓ BIS_22A: {metric['name_vi']}")

    # Test 2.2: Search by name
    print("\n2.2 Search for 'lợi nhuận'")
    results = registry.search_by_name("lợi nhuận", entity_type="COMPANY")
    assert len(results) > 0, "Should find metrics containing 'lợi nhuận'"
    print(f"  ✓ Found {len(results)} metrics")

    # Test 2.3: Get calculated metric formula
    print("\n2.3 Get ROE formula")
    roe_formula = registry.get_calculated_metric_formula("roe")
    assert roe_formula is not None, "ROE formula should exist"
    assert "BANK" in roe_formula['dependencies'], "ROE should have BANK dependencies"
    assert "COMPANY" in roe_formula['dependencies'], "ROE should have COMPANY dependencies"
    print(f"  ✓ ROE formula: {roe_formula['formula']}")

    # Test 2.4: Validate dependencies
    print("\n2.4 Validate ROE dependencies for BANK")
    available_codes = {'BIS_22A', 'BBS_400', 'BBS_100'}
    validation = registry.validate_dependencies("roe", available_codes, "BANK")
    assert validation['is_valid'], "ROE dependencies should be valid"
    print(f"  ✓ ROE dependencies valid: {validation['available']}")

    # Test 2.5: Get entity metrics count
    print("\n2.5 Get metric counts by entity")
    counts = registry.get_metric_count()
    assert counts['BANK'] > 0, "BANK should have metrics"
    assert counts['COMPANY'] > 0, "COMPANY should have metrics"
    print(f"  ✓ BANK: {counts['BANK']} metrics")
    print(f"  ✓ COMPANY: {counts['COMPANY']} metrics")

    print("\n✅ TEST 2 PASSED: Metric Registry")
    return True


def test_unified_mapper_basic():
    """Test UnifiedTickerMapper basic functionality"""
    print("\n" + "=" * 70)
    print("TEST 3: Unified Mapper - Basic Functions")
    print("=" * 70)

    mapper = UnifiedTickerMapper()

    # Test 3.1: Get complete info for BANK ticker
    print("\n3.1 Get complete info for ACB (BANK)")
    info = mapper.get_complete_info("ACB")
    assert info['ticker'] == "ACB"
    assert info['entity_type'] == "BANK"
    assert info['sector'] == "Ngân hàng"
    assert info['calculator_class'] == "BankFinancialCalculator"
    assert len(info['available_metrics']) > 0
    assert len(info['calculated_metrics']) > 0
    assert len(info['peer_tickers']) > 0
    print(f"  ✓ ACB info complete")
    print(f"    - {len(info['available_metrics'])} available metrics")
    print(f"    - {len(info['calculated_metrics'])} calculated metrics")
    print(f"    - {len(info['peer_tickers'])} peers")

    # Test 3.2: Get complete info for COMPANY ticker
    print("\n3.2 Get complete info for HPG (COMPANY)")
    hpg_info = mapper.get_complete_info("HPG")
    assert hpg_info['entity_type'] == "COMPANY"
    assert hpg_info['calculator_class'] == "CompanyFinancialCalculator"
    print(f"  ✓ HPG: {hpg_info['entity_type']} - {hpg_info['sector']}")

    # Test 3.3: Validate metric for ticker
    print("\n3.3 Validate metrics for ACB")
    is_valid_bis = mapper.validate_metric_for_ticker("ACB", "BIS_22A")
    is_valid_cis = mapper.validate_metric_for_ticker("ACB", "CIS_62")
    assert is_valid_bis == True, "BIS_22A should be valid for BANK"
    assert is_valid_cis == False, "CIS_62 should NOT be valid for BANK"
    print(f"  ✓ BIS_22A valid: {is_valid_bis}")
    print(f"  ✓ CIS_62 valid: {is_valid_cis}")

    # Test 3.4: Get metric definition
    print("\n3.4 Get metric definition for BIS_22A")
    metric_def = mapper.get_metric_definition("ACB", "BIS_22A")
    assert metric_def is not None
    assert metric_def['code'] == "BIS_22A"
    print(f"  ✓ BIS_22A: {metric_def['name_vi']}")

    print("\n✅ TEST 3 PASSED: Unified Mapper Basic")
    return True


def test_unified_mapper_advanced():
    """Test UnifiedTickerMapper advanced functionality"""
    print("\n" + "=" * 70)
    print("TEST 4: Unified Mapper - Advanced Functions")
    print("=" * 70)

    mapper = UnifiedTickerMapper()

    # Test 4.1: Search tickers with metric
    print("\n4.1 Search tickers with BIS_22A metric")
    tickers = mapper.search_tickers_with_metric("BIS_22A")
    assert len(tickers) == 24, "Should find all 24 banks"
    assert "ACB" in tickers
    assert "VCB" in tickers
    print(f"  ✓ Found {len(tickers)} tickers with BIS_22A")

    # Test 4.2: Search tickers with metric in specific sector
    print("\n4.2 Search banks with BIS_22A in Ngân hàng sector")
    bank_tickers = mapper.search_tickers_with_metric("BIS_22A", "Ngân hàng")
    assert len(bank_tickers) == 24
    print(f"  ✓ Found {len(bank_tickers)} banks")

    # Test 4.3: Get peer comparison info
    print("\n4.3 Get peer comparison info for ACB")
    peer_info = mapper.get_peer_comparison_info("ACB")
    assert peer_info['ticker'] == "ACB"
    assert peer_info['sector'] == "Ngân hàng"
    assert len(peer_info['peers']) > 0
    assert len(peer_info['comparison_metrics']) > 0
    assert 'roe' in peer_info['metric_codes']
    print(f"  ✓ Peer comparison info complete")
    print(f"    - {len(peer_info['peers'])} peers")
    print(f"    - {len(peer_info['comparison_metrics'])} comparison metrics")

    print("\n✅ TEST 4 PASSED: Unified Mapper Advanced")
    return True


def test_integration():
    """Test integration between registries"""
    print("\n" + "=" * 70)
    print("TEST 5: Integration Tests")
    print("=" * 70)

    mapper = UnifiedTickerMapper()

    # Test 5.1: All entity types have calculators
    print("\n5.1 Verify all entity types have calculators")
    for entity in ["COMPANY", "BANK", "INSURANCE", "SECURITY"]:
        sectors = mapper.sector_registry.get_sectors_by_entity(entity)
        assert len(sectors) > 0, f"{entity} should have at least one sector"

        # Get a sample ticker
        sample_ticker = mapper.sector_registry.get_tickers_by_sector(sectors[0])[0]
        calculator = mapper.get_calculator_class(sample_ticker)
        assert calculator is not None, f"{entity} should have calculator"
        print(f"  ✓ {entity}: {len(sectors)} sectors, calculator: {calculator}")

    # Test 5.2: All entity types have metrics
    print("\n5.2 Verify all entity types have metrics")
    for entity in ["COMPANY", "BANK", "INSURANCE", "SECURITY"]:
        metrics = mapper.metric_registry.get_entity_metrics(entity)
        assert len(metrics) > 0, f"{entity} should have metrics"
        print(f"  ✓ {entity}: {len(metrics)} metrics")

    # Test 5.3: Metric prefixes match entity types
    print("\n5.3 Verify metric prefixes match entity types")
    prefix_map = {
        "COMPANY": "CIS_",
        "BANK": "BIS_",
        "SECURITY": "SIS_",
        "INSURANCE": "IIS_"
    }
    for entity, expected_prefix in prefix_map.items():
        sectors = mapper.sector_registry.get_sectors_by_entity(entity)
        sector_prefixes = mapper.sector_registry.get_metric_prefixes(sectors[0])
        assert expected_prefix in sector_prefixes, f"{entity} should have {expected_prefix} prefix"
        print(f"  ✓ {entity}: {sector_prefixes}")

    print("\n✅ TEST 5 PASSED: Integration")
    return True


def test_natural_language():
    """Test natural language query interface"""
    print("\n" + "=" * 70)
    print("TEST 6: Natural Language Queries")
    print("=" * 70)

    mapper = UnifiedTickerMapper()

    # Test 6.1: Sector query
    print("\n6.1 Query: 'What sector is VCB?'")
    result = mapper.query_by_natural_language("What sector is VCB?")
    assert result['query_type'] == "ticker_sector"
    assert result['ticker'] == "VCB"
    assert result['sector'] == "Ngân hàng"
    print(f"  ✓ Result: {result['ticker']} - {result['sector']}")

    # Test 6.2: Calculator query
    print("\n6.2 Query: 'What calculator for BANK entity?'")
    result = mapper.query_by_natural_language("What calculator for BANK entity?")
    assert result['query_type'] == "calculator_class"
    assert result['entity_type'] == "BANK"
    assert result['calculator'] == "BankFinancialCalculator"
    print(f"  ✓ Result: {result['entity_type']} → {result['calculator']}")

    print("\n✅ TEST 6 PASSED: Natural Language")
    return True


def run_all_tests():
    """Run all test suites"""
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "UNIFIED MAPPER TEST SUITE" + " " * 28 + "║")
    print("╚" + "=" * 68 + "╝")

    tests = [
        ("Sector Registry", test_sector_registry),
        ("Metric Registry", test_metric_registry),
        ("Unified Mapper Basic", test_unified_mapper_basic),
        ("Unified Mapper Advanced", test_unified_mapper_advanced),
        ("Integration", test_integration),
        ("Natural Language", test_natural_language)
    ]

    passed = 0
    failed = 0
    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            if success:
                passed += 1
                results.append(f"✅ {test_name}")
            else:
                failed += 1
                results.append(f"❌ {test_name}")
        except Exception as e:
            failed += 1
            results.append(f"❌ {test_name}: {str(e)}")
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {e}")

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for result in results:
        print(result)
    print("=" * 70)
    print(f"Total: {passed + failed} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 70)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n✓ Phase 0.1.5 (Sector/Industry Mapping) COMPLETE")
        print("✓ UnifiedTickerMapper ready for Phase 2 integration")
        return True
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
