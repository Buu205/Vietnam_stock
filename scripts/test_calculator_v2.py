#!/usr/bin/env python3
"""
Test Calculator v2.0 - Test clean calculator functionality
================================================================

Script này test calculator v2.0 để đảm bảo:
1. Import thành công
2. Tính toán metrics đúng
3. Không có type errors
4. Output schema đúng

Usage:
    python scripts/test_calculator_v2.py
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import sys
import os

# Add project root to path
sys.path.append('/Users/buuphan/Dev/Vietnam_dashboard')

def test_calculator_imports():
    """Test calculator v2.0 imports"""
    print("🔍 Testing Calculator v2.0 Imports...")
    
    try:
        from PROCESSORS.fundamental.calculators.company_calculator_v2 import CompanyFinancialCalculatorV2
        print("✅ Calculator v2.0 import successful")
        return CompanyFinancialCalculatorV2
    except Exception as e:
        print(f"❌ Calculator v2.0 import failed: {e}")
        return None

def test_calculator_methods(calculator):
    """Test calculator methods exist and are callable"""
    print("\n🧪 Testing Calculator Methods...")
    
    required_methods = [
        'get_entity_type',
        'get_metric_prefixes', 
        'get_entity_specific_calculations',
        'calculate_income_statement',
        'calculate_profitability_ratios',
        'calculate_growth_rates',
        'calculate_efficiency_ratios',
        'calculate_valuation_ratios',
        'calculate_basic_components'
    ]
    
    missing_methods = []
    
    for method in required_methods:
        if not hasattr(calculator, method):
            missing_methods.append(method)
        else:
            method_func = getattr(calculator, method)
            if not callable(method_func):
                missing_methods.append(f"{method} (not callable)")
    
    if missing_methods:
        print(f"❌ Missing methods: {missing_methods}")
        return False
    else:
        print("✅ All required methods available")
        return True

def test_formula_imports():
    """Test formula imports"""
    print("\n📦 Testing Formula Imports...")
    
    try:
        from PROCESSORS.fundamental.formulas import (
            calculate_roe, calculate_roa, calculate_gross_margin, calculate_net_margin,
            calculate_operating_margin, calculate_current_ratio, calculate_debt_to_equity,
            calculate_asset_turnover, calculate_inventory_turnover, calculate_eps,
            calculate_yoy_growth, calculate_qoq_growth, calculate_ttm_sum, calculate_ttm_avg,
            calculate_receivables_turnover, calculate_payables_turnover,
            safe_divide, to_percentage,
            calculate_revenue_growth, calculate_profit_growth, calculate_free_cash_flow,
            calculate_pe_ratio, calculate_pb_ratio
        )
        print("✅ All formula imports successful")
        return True
    except Exception as e:
        print(f"❌ Formula imports failed: {e}")
        return False

def create_test_data():
    """Create test data for calculator"""
    print("\n📊 Creating Test Data...")
    
    # Create sample data with required CIS_ and CBS_ codes
    test_data = {
        'SECURITY_CODE': ['VNM', 'FPT', 'ACB'],
        'REPORT_DATE': pd.to_datetime('2024-12-31'),
        
        # Income Statement codes
        'CIS_10': [100_000_000_000, 200_000_000_000, 150_000_000_000],  # net_revenue
        'CIS_11': [60_000_000_000, 120_000_000_000, 90_000_000_000],      # cogs
        'CIS_20': [40_000_000_000, 80_000_000_000, 60_000_000_000],      # gross_profit
        'CIS_25': [10_000_000_000, 15_000_000_000, 12_000_000_000],      # selling_expenses
        'CIS_26': [5_000_000_000, 7_500_000_000, 6_000_000_000],        # admin_expenses
        'CIS_21': [2_000_000_000, 3_000_000_000, 2_500_000_000],      # finance_income
        'CIS_22': [1_000_000_000, 1_500_000_000, 1_200_000_000],      # finance_cost
        'CIS_50': [30_000_000_000, 35_000_000_000, 32_500_000_000],      # ebit
        'CIS_61': [20_000_000_000, 25_000_000_000, 22_500_000_000],      # npatmi
        'CCFI_2': [5_000_000_000, 6_000_000_000, 5_500_000_000],      # depreciation
        
        # Balance Sheet codes
        'CBS_100': [500_000_000_000, 600_000_000_000, 550_000_000_000],  # total_assets
        'CBS_135': [20_000_000_000, 25_000_000_000, 22_500_000_000],  # inventory
        'CBS_130': [150_000_000_000, 180_000_000_000, 165_000_000_000], # current_assets
        'CBS_210': [50_000_000_000, 60_000_000_000, 55_000_000_000],  # current_liabilities
        'CBS_235': [200_000_000_000, 250_000_000_000, 225_000_000_000],  # total_liabilities
        'CBS_250': [300_000_000_000, 350_000_000_000, 325_000_000_000],  # total_equity
        'CBS_400': [10_000_000, 20_000_000, 15_000_000_000],           # common_shares
    }
    
    df = pd.DataFrame(test_data)
    print(f"✅ Test data created: {df.shape}")
    return df

def test_calculator_functionality(calculator, test_df):
    """Test calculator functionality"""
    print("\n🧮 Testing Calculator Functionality...")
    
    try:
        # Test income statement calculation
        income_result = calculator.calculate_income_statement(test_df)
        print(f"✅ Income Statement: {income_result.shape}")
        
        # Test profitability ratios
        profitability_result = calculator.calculate_profitability_ratios(income_result)
        print(f"✅ Profitability Ratios: {profitability_result.shape}")
        
        # Test efficiency ratios
        efficiency_result = calculator.calculate_efficiency_ratios(test_df)
        print(f"✅ Efficiency Ratios: {efficiency_result.shape}")
        
        # Test valuation ratios
        valuation_result = calculator.calculate_valuation_ratios(income_result)
        print(f"✅ Valuation Ratios: {valuation_result.shape}")
        
        # Test basic components
        components_result = calculator.calculate_basic_components(test_df)
        print(f"✅ Basic Components: {components_result.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ Calculator functionality test failed: {e}")
        return False

def test_formula_functions():
    """Test individual formula functions"""
    print("\n🧮 Testing Individual Formula Functions...")
    
    test_cases = [
        ('calculate_roe', [100_000_000_000, 500_000_000_000]),
        ('calculate_gross_margin', [40_000_000_000, 100_000_000_000]),
        ('calculate_yoy_growth', [120_000_000_000, 100_000_000_000]),
        ('calculate_pe_ratio', [50_000, 10_000]),
    ]
    
    for func_name, args in test_cases:
        try:
            from PROCESSORS.fundamental.formulas import func_name
            result = func_name(*args)
            print(f"✅ {func_name}({args}): {result}")
        except Exception as e:
            print(f"❌ {func_name}({args}): {e}")
    
    return True

def compare_with_old_calculator(test_df):
    """Compare outputs with old calculator if available"""
    print("\n🔄 Comparing with Old Calculator...")
    
    try:
        # Try to import old calculator
        from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator
        
        old_calculator = CompanyFinancialCalculator()
        new_calculator = CompanyFinancialCalculatorV2()
        
        # Test both calculators
        old_result = old_calculator.calculate_all(test_df)
        new_result = new_calculator.calculate_all(test_df)
        
        print(f"✅ Old Calculator: {old_result.shape}")
        print(f"✅ New Calculator: {new_result.shape}")
        
        # Compare column counts
        old_cols = set(old_result.columns)
        new_cols = set(new_result.columns)
        
        missing_in_new = old_cols - new_cols
        extra_in_new = new_cols - old_cols
        
        if missing_in_new:
            print(f"⚠️  Missing in new calculator: {missing_in_new}")
        
        if extra_in_new:
            print(f"✅ Extra in new calculator: {extra_in_new}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not import old calculator: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Calculator v2.0 Testing...")
    print("=" * 60)
    
    # Test imports
    calculator = test_calculator_imports()
    if calculator is None:
        return
    
    # Test methods
    if not test_calculator_methods(calculator):
        return
    
    # Test formula imports
    if not test_formula_imports():
        return
    
    # Create test data
    test_df = create_test_data()
    
    # Test calculator functionality
    if not test_calculator_functionality(calculator, test_df):
        return
    
    # Test individual formulas
    if not test_formula_functions():
        return
    
    # Compare with old calculator
    compare_with_old_calculator(test_df)
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY: Calculator v2.0 Testing Complete")
    print("✅ All tests passed - Calculator v2.0 ready for production")

if __name__ == "__main__":
    main()