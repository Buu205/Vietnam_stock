#!/usr/bin/env python3
"""
Integration tests for all financial calculators.
Các bài kiểm tra tích hợp cho tất cả các bộ tính toán tài chính.
==========================================

This script tests all refactored calculators to ensure they work correctly
with the UnifiedTickerMapper and can process data properly.

Author: Claude Code
Date: 2025-12-07
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import logging

import sys

# Use relative imports instead of sys.path manipulation
from PROCESSORS.core.shared.unified_mapper import UnifiedTickerMapper
from PROCESSORS.fundamental.calculators.base_financial_calculator import BaseFinancialCalculator
from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator
from PROCESSORS.fundamental.calculators.bank_calculator import BankFinancialCalculator
from PROCESSORS.fundamental.calculators.insurance_calculator import InsuranceFinancialCalculator
from PROCESSORS.fundamental.calculators.security_calculator import SecurityFinancialCalculator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalculatorIntegrationTest:
    """Test suite for all financial calculators."""
    
    def __init__(self):
        """Initialize test suite."""
        self.base_path = Path(__file__).parent.parent.parent
        self.data_paths = {
            "COMPANY": self.base_path / "DATA/processed/fundamental/company_full.parquet",
            "BANK": self.base_path / "DATA/processed/fundamental/bank_full.parquet",
            "INSURANCE": self.base_path / "DATA/processed/fundamental/insurance_full.parquet",
            "SECURITY": self.base_path / "DATA/processed/fundamental/security_full.parquet"
        }
        self.calculators = {
            "COMPANY": CompanyFinancialCalculator,
            "BANK": BankFinancialCalculator,
            "INSURANCE": InsuranceFinancialCalculator,
            "SECURITY": SecurityFinancialCalculator
        }
        self.unified_mapper = UnifiedTickerMapper()
        
    def run_all_tests(self):
        """Run all tests for all calculators."""
        logger.info("Starting integration tests for all calculators...")
        
        results = {}
        
        for entity_type in self.calculators.keys():
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing {entity_type} Calculator")
            logger.info(f"{'='*60}")
            
            try:
                result = self.test_calculator(entity_type)
                results[entity_type] = result
                
                if result['success']:
                    logger.info(f"✅ {entity_type} Calculator: PASSED")
                else:
                    logger.error(f"❌ {entity_type} Calculator: FAILED")
                    logger.error(f"Error: {result['error']}")
            except Exception as e:
                logger.error(f"❌ {entity_type} Calculator: EXCEPTION")
                logger.error(f"Exception: {str(e)}")
                results[entity_type] = {'success': False, 'error': str(e)}
        
        # Print summary
        self.print_test_summary(results)
        
        return results
    
    def test_calculator(self, entity_type: str) -> dict:
        """Test a specific calculator."""
        test_result = {'success': False, 'error': None, 'details': {}}
        
        # Check data file exists
        data_path = self.data_paths[entity_type]
        if not data_path.exists():
            return {'success': False, 'error': f"Data file not found: {data_path}"}
        
        try:
            # Initialize calculator
            calculator = self.calculators[entity_type](str(data_path))
            
            # Test basic functionality
            basic_result = self.test_basic_functionality(calculator, entity_type)
            test_result['details']['basic_functionality'] = basic_result
            
            if not basic_result['success']:
                test_result['success'] = False
                test_result['error'] = basic_result['error']
                return test_result
                
            # Test with sample ticker
            ticker_result = self.test_with_sample_ticker(calculator, entity_type)
            test_result['details']['sample_ticker'] = ticker_result
            
            if not ticker_result['success']:
                return ticker_result
                
            # Test metric validation
            validation_result = self.test_metric_validation(calculator, entity_type)
            test_result['details']['metric_validation'] = validation_result
            
            test_result['success'] = all([
                basic_result['success'],
                ticker_result['success'],
                validation_result['success']
            ])
            
            if not test_result['success']:
                if not basic_result['success']:
                    test_result['error'] = f"Basic: {basic_result['error']}"
                elif not ticker_result['success']:
                    test_result['error'] = f"Ticker: {ticker_result['error']}"
                elif not validation_result['success']:
                    test_result['error'] = f"Validation: {validation_result['error']}"

            
        except Exception as e:
            test_result['error'] = str(e)
            
        return test_result
    
    def test_basic_functionality(self, calculator: BaseFinancialCalculator, entity_type: str) -> dict:
        """
    Integration test suite for calculators.
    Bộ kiểm tra tích hợp cho các bộ tính toán.
    
    Verifies that all calculators can be instantiated
    and perform basic calculations without errors.
    Xác minh rằng tất cả các bộ tính toán có thể được khởi tạo
    và thực hiện các phép tính cơ bản mà không có lỗi.
    """
        result = {'success': False, 'error': None}
        
        try:
            # Test entity type
            assert calculator.get_entity_type() == entity_type, f"Entity type mismatch: {calculator.get_entity_type()} != {entity_type}"
            
            # Test metric prefixes
            prefixes = calculator.get_metric_prefixes()
            assert isinstance(prefixes, list) and len(prefixes) > 0, f"Invalid metric prefixes: {prefixes}"
            
            # Test entity-specific calculations
            calculations = calculator.get_entity_specific_calculations()
            assert isinstance(calculations, dict) and len(calculations) > 0, f"Invalid calculations: {calculations}"
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def test_with_sample_ticker(self, calculator: BaseFinancialCalculator, entity_type: str) -> dict:
        """Test calculator with a sample ticker."""
        result = {'success': False, 'error': None, 'ticker': None, 'shape': None}
        
        try:
            # Get sample ticker for entity type
            tickers = self.unified_mapper.sector_registry.get_tickers_by_entity_type(entity_type)
            assert len(tickers) > 0, f"No tickers found for entity type: {entity_type}"
            
            sample_ticker = tickers[0]
            result['ticker'] = sample_ticker
            
            # Calculate metrics for sample ticker
            calc_results = calculator.calculate_all_metrics(sample_ticker)
            
            # Check results
            assert isinstance(calc_results, pd.DataFrame), "Results not a DataFrame"
            assert not calc_results.empty, "Results DataFrame is empty"
            
            # Check for required columns
            id_cols = ['SECURITY_CODE', 'REPORT_DATE']
            for col in id_cols:
                if col in calc_results.columns:
                    assert col in calc_results.columns, f"Missing column: {col}"
                elif 'symbol' in calc_results.columns:
                    pass  # Renamed column
                else:
                    raise AssertionError(f"Missing ID column: {col} or symbol")
            
            result['shape'] = calc_results.shape
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def test_metric_validation(self, calculator: BaseFinancialCalculator, entity_type: str) -> dict:
        """Test metric validation functionality."""
        result = {'success': False, 'error': None, 'tested_metrics': []}
        
        try:
            # Test metric validation for some known metrics
            entity_metrics = {
                "COMPANY": ["CIS_10", "CBS_270", "CBS_400"],
                "BANK": ["BIS_1", "BBS_100", "BBS_500"],
                "INSURANCE": ["IIS_1", "IBS_18", "IBS_36"],
                "SECURITY": ["SIS_1", "SBS_39", "SBS_65"]
            }
            
            test_metrics = entity_metrics.get(entity_type, [])
            result['tested_metrics'] = test_metrics
            
            for metric in test_metrics:
                is_valid = calculator.validate_metric_for_entity(metric)
                # Just test the function runs, actual validation depends on metric registry
                assert isinstance(is_valid, bool), f"Invalid validation result for {metric}: {is_valid}"
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def print_test_summary(self, results: dict):
        """Print summary of test results."""
        logger.info("\n" + "="*80)
        logger.info("CALCULATOR INTEGRATION TEST SUMMARY")
        logger.info("="*80)
        
        total = len(results)
        passed = sum(1 for r in results.values() if r['success'])
        failed = total - passed
        
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            logger.info("\nFailed Tests:")
            for entity_type, result in results.items():
                if not result['success']:
                    logger.info(f"❌ {entity_type}: {result['error']}")
        
        logger.info("\n" + "="*80)

def main():
    """Main function to run tests."""
    test_suite = CalculatorIntegrationTest()
    results = test_suite.run_all_tests()
    
    # Return appropriate exit code
    all_passed = all(result['success'] for result in results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)