"""
Financial Calculators Package
=============================

Unified calculator system for all entity types (Company, Bank, Insurance, Security).

Main Entry Point:
    python3 PROCESSORS/fundamental/calculators/run_all_calculators.py

Usage:
    # Run all calculators
    python3 PROCESSORS/fundamental/calculators/run_all_calculators.py

    # Run specific entity
    python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity bank
    python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity company
    python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity insurance
    python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity security

Output Files:
    - DATA/processed/fundamental/company/company_financial_metrics.parquet
    - DATA/processed/fundamental/bank/bank_financial_metrics.parquet
    - DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet
    - DATA/processed/fundamental/security/security_financial_metrics.parquet

Key Formulas (Bank):
    - LDR Pure = BBS_161 / BBS_330 * 100
    - LDR Regulated = (BBS_160 + BNOT_13_1_1_3) / (BBS_330 + BBS_360) * 100
    - CASA Ratio = (BNOT_26_1 + BNOT_26_3 + BNOT_26_5) / BNOT_26 * 100
    - NPL = BNOT_4_3 + BNOT_4_4 + BNOT_4_5
    - LLCR = abs(BBS_169) / NPL * 100
"""

# Import from unified calculator
from .run_all_calculators import (
    EntityCalculator,
    CompanyCalculator,
    BankCalculator,
    InsuranceCalculator,
    SecurityCalculator,
)

__all__ = [
    'EntityCalculator',
    'CompanyCalculator',
    'BankCalculator',
    'InsuranceCalculator',
    'SecurityCalculator',
]
