#!/usr/bin/env python3
"""
Test All Calculators - Company, Bank, Security
===============================================

Test script to run all three financial calculators and validate output.

Usage:
    python3 test_all_calculators.py

Author: Claude Code
Date: 2025-12-14
"""

import sys
from pathlib import Path
import pandas as pd
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import calculators
from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator
from PROCESSORS.fundamental.calculators.bank_calculator import BankFinancialCalculator
from PROCESSORS.fundamental.calculators.security_calculator import SecurityFinancialCalculator


def test_company_calculator():
    """Test Company Calculator."""
    logger.info("=" * 80)
    logger.info("TESTING COMPANY CALCULATOR")
    logger.info("=" * 80)

    try:
        # Initialize calculator
        data_path = Path("DATA/processed/fundamental/company_full.parquet")

        if not data_path.exists():
            logger.warning(f"Data file not found: {data_path}")
            logger.info("Skipping Company Calculator test")
            return None

        calc = CompanyFinancialCalculator(str(data_path))

        # Load and check data
        logger.info(f"Loading data from: {data_path}")
        df = calc.load_data()
        logger.info(f"✓ Loaded {len(df):,} rows")
        logger.info(f"✓ Columns: {df.columns.tolist()[:10]}... (showing first 10)")
        logger.info(f"✓ Unique tickers: {df['SECURITY_CODE'].nunique()}")
        logger.info(f"✓ Date range: {df['REPORT_DATE'].min()} to {df['REPORT_DATE'].max()}")

        # Calculate metrics for a sample ticker
        sample_ticker = df['SECURITY_CODE'].iloc[0]
        logger.info(f"\nCalculating metrics for sample ticker: {sample_ticker}")

        result = calc.calculate_all_metrics(ticker=sample_ticker)

        if result.empty:
            logger.error("❌ Calculator returned empty DataFrame!")
            return None

        logger.info(f"✓ Calculated {len(result)} rows")
        logger.info(f"✓ Output columns ({len(result.columns)}): {result.columns.tolist()}")

        # Display sample results
        logger.info("\n📊 Sample Results (Latest Quarter):")
        latest = result.iloc[-1]

        metrics_to_show = [
            'symbol', 'report_date', 'year', 'quarter',
            'net_revenue', 'gross_profit', 'ebit', 'ebitda', 'npatmi',
            'gross_profit_margin', 'ebit_margin', 'net_margin',
            'roe', 'roa', 'eps',
            'total_assets', 'total_equity', 'debt_to_equity',
            'current_ratio', 'fcf', 'fcfe'
        ]

        for metric in metrics_to_show:
            if metric in latest.index:
                value = latest[metric]
                if pd.notna(value):
                    if isinstance(value, (int, float)):
                        logger.info(f"  {metric:30s}: {value:,.2f}")
                    else:
                        logger.info(f"  {metric:30s}: {value}")

        logger.info("\n✅ COMPANY CALCULATOR TEST PASSED")
        return result

    except Exception as e:
        logger.error(f"❌ COMPANY CALCULATOR TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_bank_calculator():
    """Test Bank Calculator."""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING BANK CALCULATOR")
    logger.info("=" * 80)

    try:
        # Initialize calculator
        data_path = Path("DATA/processed/fundamental/bank_full.parquet")

        if not data_path.exists():
            logger.warning(f"Data file not found: {data_path}")
            logger.info("Skipping Bank Calculator test")
            return None

        calc = BankFinancialCalculator(str(data_path))

        # Load and check data
        logger.info(f"Loading data from: {data_path}")
        df = calc.load_data()
        logger.info(f"✓ Loaded {len(df):,} rows")
        logger.info(f"✓ Unique tickers: {df['SECURITY_CODE'].nunique()}")
        logger.info(f"✓ Date range: {df['REPORT_DATE'].min()} to {df['REPORT_DATE'].max()}")

        # Calculate metrics for a sample ticker
        sample_ticker = df['SECURITY_CODE'].iloc[0]
        logger.info(f"\nCalculating metrics for sample ticker: {sample_ticker}")

        result = calc.calculate_all_metrics(ticker=sample_ticker)

        if result.empty:
            logger.error("❌ Calculator returned empty DataFrame!")
            return None

        logger.info(f"✓ Calculated {len(result)} rows")
        logger.info(f"✓ Output columns ({len(result.columns)}): {result.columns.tolist()}")

        # Display sample results
        logger.info("\n📊 Sample Results (Latest Quarter):")
        latest = result.iloc[-1]

        metrics_to_show = [
            'symbol', 'report_date', 'year', 'quarter',
            'nii', 'toi', 'noii', 'opex', 'pbt', 'npatmi',
            'roea_ttm', 'roaa_ttm', 'nim_q',
            'casa_ratio', 'cir', 'ldr_pure',
            'npl_ratio', 'debt_group2_ratio', 'llcr'
        ]

        for metric in metrics_to_show:
            if metric in latest.index:
                value = latest[metric]
                if pd.notna(value):
                    if isinstance(value, (int, float)):
                        logger.info(f"  {metric:30s}: {value:,.2f}")
                    else:
                        logger.info(f"  {metric:30s}: {value}")

        logger.info("\n✅ BANK CALCULATOR TEST PASSED")
        return result

    except Exception as e:
        logger.error(f"❌ BANK CALCULATOR TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_security_calculator():
    """Test Security Calculator."""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING SECURITY CALCULATOR")
    logger.info("=" * 80)

    try:
        # Initialize calculator
        data_path = Path("DATA/processed/fundamental/security_full.parquet")

        if not data_path.exists():
            logger.warning(f"Data file not found: {data_path}")
            logger.info("Skipping Security Calculator test")
            return None

        calc = SecurityFinancialCalculator(str(data_path))

        # Load and check data
        logger.info(f"Loading data from: {data_path}")
        df = calc.load_data()
        logger.info(f"✓ Loaded {len(df):,} rows")
        logger.info(f"✓ Unique tickers: {df['SECURITY_CODE'].nunique()}")
        logger.info(f"✓ Date range: {df['REPORT_DATE'].min()} to {df['REPORT_DATE'].max()}")

        # Calculate metrics for a sample ticker
        sample_ticker = df['SECURITY_CODE'].iloc[0]
        logger.info(f"\nCalculating metrics for sample ticker: {sample_ticker}")

        result = calc.calculate_all_metrics(ticker=sample_ticker)

        if result.empty:
            logger.error("❌ Calculator returned empty DataFrame!")
            return None

        logger.info(f"✓ Calculated {len(result)} rows")
        logger.info(f"✓ Output columns ({len(result.columns)}): {result.columns.tolist()}")

        # Display sample results
        logger.info("\n📊 Sample Results (Latest Quarter):")
        latest = result.iloc[-1]

        metrics_to_show = [
            'symbol', 'report_date', 'year', 'quarter',
            'total_revenue', 'net_profit', 'gross_profit',
            'total_assets', 'equity', 'leverage',
            'roae_ttm', 'roaa_ttm', 'profit_margin',
            'total_investment', 'margin_loans',
            'investment_ratio', 'lending_ratio', 'brokerage_ratio',
            'cir', 'opex_ratio'
        ]

        for metric in metrics_to_show:
            if metric in latest.index:
                value = latest[metric]
                if pd.notna(value):
                    if isinstance(value, (int, float)):
                        logger.info(f"  {metric:30s}: {value:,.2f}")
                    else:
                        logger.info(f"  {metric:30s}: {value}")

        logger.info("\n✅ SECURITY CALCULATOR TEST PASSED")
        return result

    except Exception as e:
        logger.error(f"❌ SECURITY CALCULATOR TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def save_results(company_result, bank_result, security_result):
    """Save calculator results to parquet files."""
    logger.info("\n" + "=" * 80)
    logger.info("SAVING RESULTS")
    logger.info("=" * 80)

    output_dir = Path("DATA/processed/fundamental")
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []

    # Save Company results
    if company_result is not None and not company_result.empty:
        company_path = output_dir / "company" / "company_financial_metrics.parquet"
        company_path.parent.mkdir(parents=True, exist_ok=True)
        company_result.to_parquet(company_path, index=False)
        logger.info(f"✓ Saved Company results: {company_path}")
        logger.info(f"  Rows: {len(company_result):,} | Columns: {len(company_result.columns)}")
        saved_files.append(str(company_path))

    # Save Bank results
    if bank_result is not None and not bank_result.empty:
        bank_path = output_dir / "bank" / "bank_financial_metrics.parquet"
        bank_path.parent.mkdir(parents=True, exist_ok=True)
        bank_result.to_parquet(bank_path, index=False)
        logger.info(f"✓ Saved Bank results: {bank_path}")
        logger.info(f"  Rows: {len(bank_result):,} | Columns: {len(bank_result.columns)}")
        saved_files.append(str(bank_path))

    # Save Security results
    if security_result is not None and not security_result.empty:
        security_path = output_dir / "security" / "security_financial_metrics.parquet"
        security_path.parent.mkdir(parents=True, exist_ok=True)
        security_result.to_parquet(security_path, index=False)
        logger.info(f"✓ Saved Security results: {security_path}")
        logger.info(f"  Rows: {len(security_result):,} | Columns: {len(security_result.columns)}")
        saved_files.append(str(security_path))

    return saved_files


def main():
    """Main test function."""
    logger.info("=" * 80)
    logger.info("FINANCIAL CALCULATORS TEST SUITE")
    logger.info("=" * 80)
    logger.info("")

    # Run tests
    company_result = test_company_calculator()
    bank_result = test_bank_calculator()
    security_result = test_security_calculator()

    # Save results
    saved_files = save_results(company_result, bank_result, security_result)

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)

    total_tests = 3
    passed_tests = sum([
        company_result is not None,
        bank_result is not None,
        security_result is not None
    ])

    logger.info(f"Tests Passed: {passed_tests}/{total_tests}")
    logger.info(f"Files Saved: {len(saved_files)}")

    if saved_files:
        logger.info("\nSaved files:")
        for file in saved_files:
            logger.info(f"  - {file}")

    if passed_tests == total_tests:
        logger.info("\n🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        logger.warning(f"\n⚠️  {total_tests - passed_tests} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
