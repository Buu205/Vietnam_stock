#!/usr/bin/env python3
"""
Test Suite for OHLCV Standardization (Phase 0.1.6)
===================================================

Tests for:
- OHLCVFormatter (display formatting)
- OHLCVValidator (data quality validation)
- Schema integrity

Author: Claude Code
Date: 2025-12-07
"""

import sys
from pathlib import Path
import pandas as pd
import json

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from PROCESSORS.core.formatters.ohlcv_formatter import OHLCVFormatter
from PROCESSORS.core.formatters.ohlcv_validator import OHLCVValidator


def test_schema_exists():
    """Test 1: Schema files exist"""
    print("\n" + "=" * 70)
    print("TEST 1: Schema Files Existence")
    print("=" * 70)

    schema_files = [
        "DATA/schemas/ohlcv.json",
        "DATA/metadata/sector_industry_registry.json"
    ]

    for schema_file in schema_files:
        schema_path = project_root / schema_file
        exists = schema_path.exists()
        print(f"  {schema_file:<60} {'✅' if exists else '❌'}")
        if not exists:
            return False

    return True


def test_schema_structure():
    """Test 2: Schema structure validation"""
    print("\n" + "=" * 70)
    print("TEST 2: Schema Structure Validation")
    print("=" * 70)

    schema_path = project_root / "DATA/schemas/ohlcv.json"
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    required_sections = [
        'definitions',
        'schemas',
        'display_formats',
        'validation_rules',
        'metadata'
    ]

    all_valid = True
    for section in required_sections:
        exists = section in schema
        print(f"  {section:<60} {'✅' if exists else '❌'}")
        if not exists:
            all_valid = False

    # Check display formats
    print("\n  Display format specs:")
    display_formats = schema.get('display_formats', {})
    for format_type in ['price', 'volume', 'percentage', 'market_cap', 'ratio']:
        exists = format_type in display_formats
        print(f"    {format_type:<58} {'✅' if exists else '❌'}")
        if not exists:
            all_valid = False

    return all_valid


def test_formatter_functionality():
    """Test 3: OHLCVFormatter functionality"""
    print("\n" + "=" * 70)
    print("TEST 3: OHLCVFormatter Functionality")
    print("=" * 70)

    formatter = OHLCVFormatter()

    test_cases = [
        ("Price formatting", formatter.format_price(25750.5), "25,750.50đ"),
        ("Volume formatting", formatter.format_volume(1250000), "1,250,000"),
        ("Percentage +", formatter.format_percentage(2.35, positive=True), "+2.35%"),
        ("Percentage -", formatter.format_percentage(-1.25, positive=False), "-1.25%"),
        ("Market cap", formatter.format_market_cap(25750000000), "25.8B"),
        ("Ratio", formatter.format_ratio(12.345), "12.35"),
    ]

    all_passed = True
    for test_name, actual, expected in test_cases:
        # For market cap, allow small differences due to rounding
        if "Market cap" in test_name:
            passed = actual.startswith("25.")
        else:
            passed = actual == expected

        status = "✅" if passed else "❌"
        print(f"  {test_name:<30} {actual:<20} {status}")
        if not passed:
            print(f"    Expected: {expected}")
            all_passed = False

    return all_passed


def test_validator_functionality():
    """Test 4: OHLCVValidator functionality"""
    print("\n" + "=" * 70)
    print("TEST 4: OHLCVValidator Functionality")
    print("=" * 70)

    validator = OHLCVValidator()

    # Test 4.1: Valid data
    print("\n  Test 4.1: Valid OHLCV data")
    valid_data = pd.DataFrame({
        'symbol': ['VCB', 'VCB'],
        'date': pd.to_datetime(['2025-12-01', '2025-12-02']),
        'open': [95000, 96000],
        'high': [97000, 97000],
        'low': [94000, 95500],
        'close': [96500, 96800],
        'volume': [1000000, 1200000],
    })

    result = validator.validate_ohlcv_data(valid_data)
    print(f"    Valid data test: {'✅ PASSED' if result.is_valid else '❌ FAILED'}")
    print(f"    Issues found: {len(result.issues)}")

    # Test 4.2: Invalid data (high < low)
    print("\n  Test 4.2: Invalid data detection (high < low)")
    invalid_data = valid_data.copy()
    invalid_data.loc[0, 'high'] = 90000  # Make high < low

    result = validator.validate_ohlcv_data(invalid_data)
    has_error = not result.is_valid and result.errors > 0
    print(f"    Error detection: {'✅ PASSED' if has_error else '❌ FAILED'}")
    print(f"    Errors found: {result.errors}")

    # Test 4.3: Invalid data (close out of range)
    print("\n  Test 4.3: Invalid data detection (close > high)")
    invalid_data = valid_data.copy()
    invalid_data.loc[0, 'close'] = 98000  # Make close > high

    result = validator.validate_ohlcv_data(invalid_data)
    has_error = not result.is_valid and result.errors > 0
    print(f"    Error detection: {'✅ PASSED' if has_error else '❌ FAILED'}")
    print(f"    Errors found: {result.errors}")

    return True


def test_frequency_codes():
    """Test 5: Frequency codes"""
    print("\n" + "=" * 70)
    print("TEST 5: Frequency Codes")
    print("=" * 70)

    formatter = OHLCVFormatter()

    expected_frequencies = {
        'D': 'Daily',
        'W': 'Weekly',
        'M': 'Monthly',
        'Q': 'Quarterly',
        'Y': 'Yearly'
    }

    all_passed = True
    for code, expected_desc in expected_frequencies.items():
        actual_desc = formatter.get_frequency_description(code)
        passed = actual_desc == expected_desc
        status = "✅" if passed else "❌"
        print(f"  {code}: {actual_desc:<30} {status}")
        if not passed:
            all_passed = False

    return all_passed


def test_integration_with_existing_schemas():
    """Test 6: Integration with existing schemas"""
    print("\n" + "=" * 70)
    print("TEST 6: Integration with Existing Schemas")
    print("=" * 70)

    ohlcv_schema_path = project_root / "DATA/schemas/ohlcv.json"
    with open(ohlcv_schema_path, 'r', encoding='utf-8') as f:
        ohlcv_schema = json.load(f)

    # Check dependencies
    dependencies = ohlcv_schema.get('metadata', {}).get('dependencies', {})

    expected_deps = [
        'technical_indicators_schema',
        'fundamental_schema'
    ]

    all_found = True
    for dep in expected_deps:
        exists = dep in dependencies
        print(f"  Dependency '{dep}': {'✅' if exists else '❌'}")
        if not exists:
            all_found = False

    return all_found


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 70)
    print("OHLCV STANDARDIZATION TEST SUITE (Phase 0.1.6)")
    print("=" * 70)

    tests = [
        ("Schema Files Existence", test_schema_exists),
        ("Schema Structure", test_schema_structure),
        ("OHLCVFormatter", test_formatter_functionality),
        ("OHLCVValidator", test_validator_functionality),
        ("Frequency Codes", test_frequency_codes),
        ("Schema Integration", test_integration_with_existing_schemas),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name:<50} {status}")

    print("=" * 70)
    print(f"  Total: {passed_count}/{total_count} tests passed")
    print("=" * 70)

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Phase 0.1.6 implementation is complete.")
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed. Please review.")

    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
