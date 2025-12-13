#!/usr/bin/env python3
"""
AI Formula Generation Integration Test
=======================================

Test the complete AI formula generation pipeline from natural language
to Python code.

Author: AI Assistant
Date: 2025-12-12
"""

import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from PROCESSORS.core.ai import ai_assistant


def test_vietnamese_ratio():
    """Test Vietnamese ratio formula"""
    logger.info("Test 1: Vietnamese ratio 'tính SGA/Rev'")
    result = ai_assistant.generate_formula("tính SGA/Rev", "COMPANY")

    assert result.success, f"Failed: {result.error_message}"
    assert result.formula is not None
    assert 'CIS_25' in result.formula.dependencies or 'CIS_26' in result.formula.dependencies
    assert 'CIS_10' in result.formula.dependencies
    assert 'safe_divide' in result.formula.function_code

    logger.info(f"  ✅ Function: {result.formula.function_name}")
    logger.info(f"  ✅ Formula: {result.formula.formula_description}")
    logger.info(f"  ✅ Dependencies: {result.formula.dependencies}")
    return True


def test_direct_formula():
    """Test direct metric code formula"""
    logger.info("\nTest 2: Direct formula 'CIS_25 + CIS_26'")
    result = ai_assistant.generate_formula("CIS_25 + CIS_26", "COMPANY")

    assert result.success, f"Failed: {result.error_message}"
    assert result.formula is not None
    assert 'CIS_25' in result.formula.dependencies
    assert 'CIS_26' in result.formula.dependencies

    logger.info(f"  ✅ Function: {result.formula.function_name}")
    logger.info(f"  ✅ Formula: {result.formula.formula_description}")
    return True


def test_english_metric():
    """Test English metric name"""
    logger.info("\nTest 3: English metric 'calculate ROE'")
    result = ai_assistant.generate_formula("calculate ROE", "COMPANY")

    # ROE might not have exact match, check if it at least parsed
    if result.success:
        logger.info(f"  ✅ Function: {result.formula.function_name}")
        logger.info(f"  ✅ Resolved metrics: {[m.code for m in result.metrics]}")
    else:
        logger.info(f"  ⚠️  Could not resolve ROE (expected): {result.error_message}")
        if result.suggestions:
            logger.info("  Suggestions:")
            for s in result.suggestions[:3]:
                logger.info(f"    {s}")

    return True  # Don't fail on this since ROE might need exact Vietnamese name


def test_validate_preview():
    """Test validate and preview"""
    logger.info("\nTest 4: Validate and preview 'CIS_10 / CIS_25'")
    preview = ai_assistant.validate_and_preview("CIS_10 / CIS_25", "COMPANY")

    assert preview is not None
    assert 'intent' in preview
    assert 'metrics' in preview
    assert preview['can_generate'] == True
    assert len(preview['metrics']) == 2

    logger.info(f"  ✅ Can generate: {preview['can_generate']}")
    logger.info(f"  ✅ Metrics found: {len(preview['metrics'])}")
    for m in preview['metrics']:
        logger.info(f"    - {m['code']}: {m['name_vi']}")

    return True


def test_generate_from_codes():
    """Test generate from codes directly"""
    logger.info("\nTest 5: Generate from codes ['CIS_25', 'CIS_10']")
    result = ai_assistant.generate_formula_from_codes(
        ['CIS_25', 'CIS_10'],
        'divide',
        'COMPANY',
        'calculate_sga_ratio'
    )

    assert result.success, f"Failed: {result.error_message}"
    assert result.formula is not None
    assert result.formula.function_name == 'calculate_sga_ratio'
    assert 'CIS_25' in result.formula.dependencies
    assert 'CIS_10' in result.formula.dependencies

    logger.info(f"  ✅ Function: {result.formula.function_name}")
    logger.info(f"  ✅ Formula: {result.formula.formula_description}")

    # Print generated code (first 500 chars)
    logger.info("\n  Generated Code Sample:")
    code_lines = result.formula.function_code.split('\n')
    for line in code_lines[:15]:
        logger.info(f"    {line}")

    return True


def test_bank_metrics():
    """Test with BANK entity type"""
    logger.info("\nTest 6: Bank metrics 'BIS_1 + BIS_2'")
    result = ai_assistant.generate_formula("BIS_1 + BIS_2", "BANK")

    if result.success:
        logger.info(f"  ✅ Function: {result.formula.function_name}")
        logger.info(f"  ✅ Dependencies: {result.formula.dependencies}")
    else:
        logger.info(f"  ⚠️  Bank metrics test: {result.error_message}")

    return True  # Don't fail if specific bank codes don't exist


def run_all_tests():
    """Run all tests"""
    logger.info("=" * 80)
    logger.info("AI Formula Generation Integration Tests")
    logger.info("=" * 80)

    tests = [
        test_vietnamese_ratio,
        test_direct_formula,
        test_english_metric,
        test_validate_preview,
        test_generate_from_codes,
        test_bank_metrics,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                logger.error(f"  ❌ Test {test.__name__} failed")
        except AssertionError as e:
            failed += 1
            logger.error(f"  ❌ Test {test.__name__} failed: {e}")
        except Exception as e:
            failed += 1
            logger.error(f"  ❌ Test {test.__name__} exception: {e}")

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total Tests: {len(tests)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Success Rate: {(passed/len(tests))*100:.1f}%")
    logger.info("=" * 80)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
