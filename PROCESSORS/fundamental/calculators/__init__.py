"""
Financial Calculators Base Package / Gói Cơ Bản Các Bộ Tính Toán Tài Chính
======================================================================

This package contains all refactored financial calculators that inherit
from BaseFinancialCalculator to reduce code duplication.
Gói này chứa tất cả các bộ tính toán tài chính đã được tái cấu trúc,
kế thừa từ BaseFinancialCalculator để giảm thiểu lặp lại mã nguồn.

Calculators / Các Bộ Tính Toán:
- BaseFinancialCalculator: Base class with shared functionality (Lớp cơ sở với chức năng chia sẻ)
- CompanyFinancialCalculator: Calculator for COMPANY entities (Bộ tính toán cho DOANH NGHIỆP)
- BankFinancialCalculator: Calculator for BANK entities (Bộ tính toán cho NGÂN HÀNG)
- InsuranceFinancialCalculator: Calculator for INSURANCE entities (Bộ tính toán cho BẢO HIỂM)
- SecurityFinancialCalculator: Calculator for SECURITY entities (Bộ tính toán cho CHỨNG KHOÁN)

Usage / Hướng Dẫn Sử Dụng:
    from PROCESSORS.fundamental.calculators import (
        BaseFinancialCalculator,
        CompanyFinancialCalculator,
        BankFinancialCalculator,
        InsuranceFinancialCalculator,
        SecurityFinancialCalculator,
        UnifiedTickerMapper
    )
    
    # Auto-select calculator by ticker
    mapper = UnifiedTickerMapper()
    ticker = "ACB"
    entity_type = mapper.get_entity_type(ticker)  # "BANK"
    
    # Select calculator
    calculators = {
        "COMPANY": CompanyFinancialCalculator,
        "BANK": BankFinancialCalculator,
        "INSURANCE": InsuranceFinancialCalculator,
        "SECURITY": SecurityFinancialCalculator
    }
    
    calculator_class = calculators[entity_type]
    calculator = calculator_class(data_path)
    
    # Calculate metrics
    results = calculator.calculate_all_metrics(ticker)
"""

from .base_financial_calculator import BaseFinancialCalculator
from .company_calculator import CompanyFinancialCalculator
from .bank_calculator import BankFinancialCalculator
from .insurance_calculator import InsuranceFinancialCalculator
from .security_calculator import SecurityFinancialCalculator

__all__ = [
    'BaseFinancialCalculator',
    'CompanyFinancialCalculator',
    'BankFinancialCalculator',
    'InsuranceFinancialCalculator',
    'SecurityFinancialCalculator'
]