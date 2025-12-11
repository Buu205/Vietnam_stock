"""
Financial Formulas Module

Module này cung cấp tất cả financial formulas cho các entity types khác nhau.

Structure:
- _base_formulas.py: Universal formulas cho tất cả entities
- company_formulas.py: Company-specific formulas
- bank_formulas.py: Bank-specific formulas  
- insurance_formulas.py: Insurance-specific formulas
- security_formulas.py: Security-specific formulas
- utils.py: Utility functions (safe_divide, to_percentage)

Usage:
    from PROCESSORS.fundamental.formulas import (
        calculate_roe, calculate_roa,  # Universal formulas
        calculate_revenue_growth,      # Company-specific
        calculate_nim, calculate_cir     # Bank-specific
    )
"""

# Universal formulas - available for all entities
from ._base_formulas import (
    # Profitability Ratios
    calculate_roe,
    calculate_roa,
    calculate_gross_margin,
    calculate_net_margin,
    calculate_operating_margin,
    
    # Financial Health Ratios
    calculate_current_ratio,
    calculate_debt_to_equity,
    
    # Efficiency Ratios
    calculate_asset_turnover,
    calculate_inventory_turnover,
    
    # Market Metrics
    calculate_eps,
    
    # Growth Rates
    calculate_yoy_growth,
    calculate_qoq_growth,
    
    # TTM Formulas
    calculate_ttm_sum,
    calculate_ttm_avg,
    
    # Enhanced Efficiency Ratios
    calculate_receivables_turnover,
    calculate_payables_turnover,
    
    # Utilities
    safe_divide,
    to_percentage
)

# Valuation formulas - PE, PB, PS, EV/EBITDA
try:
    from PROCESSORS.valuation.formulas.valuation_formulas import (
        calculate_pe_ratio,
        calculate_pb_ratio,
        calculate_ps_ratio,
        calculate_ev_ebitda
    )
except ImportError:
    # Valuation formulas not available
    calculate_pe_ratio = None
    calculate_pb_ratio = None
    calculate_ps_ratio = None
    calculate_ev_ebitda = None

# Entity-specific formulas
try:
    from .company_formulas import CompanyFormulas
    
    # Company-specific formulas
    calculate_revenue_growth = CompanyFormulas.calculate_revenue_growth
    calculate_profit_growth = CompanyFormulas.calculate_profit_growth
    calculate_free_cash_flow = CompanyFormulas.calculate_free_cash_flow
    
except ImportError:
    # Company formulas not available
    CompanyFormulas = None
    calculate_revenue_growth = None
    calculate_profit_growth = None
    calculate_free_cash_flow = None

try:
    from .bank_formulas import BankFormulas
    
    # Bank-specific formulas would be imported here
    # (to be implemented when bank_formulas.py is created)
    
except ImportError:
    # Bank formulas not available
    BankFormulas = None

# Insurance and Security formulas not implemented yet
InsuranceFormulas = None
SecurityFormulas = None

# Export all formulas for easy access
__all__ = [
    # Universal formulas
    'calculate_roe', 'calculate_roa', 'calculate_gross_margin', 'calculate_net_margin',
    'calculate_operating_margin', 'calculate_current_ratio', 'calculate_debt_to_equity',
    'calculate_asset_turnover', 'calculate_inventory_turnover', 'calculate_eps',
    'safe_divide', 'to_percentage',
    
    # Growth Rates
    'calculate_yoy_growth', 'calculate_qoq_growth',
    
    # TTM Formulas
    'calculate_ttm_sum', 'calculate_ttm_avg',
    
    # Enhanced Efficiency Ratios
    'calculate_receivables_turnover', 'calculate_payables_turnover',
    
    # Entity-specific formulas
    'calculate_revenue_growth', 'calculate_profit_growth', 'calculate_free_cash_flow',
    
    # Valuation formulas (from valuation module)
    'calculate_pe_ratio', 'calculate_pb_ratio', 'calculate_ps_ratio', 'calculate_ev_ebitda',
    
    # Classes
    'CompanyFormulas', 'BankFormulas', 'InsuranceFormulas', 'SecurityFormulas'
]