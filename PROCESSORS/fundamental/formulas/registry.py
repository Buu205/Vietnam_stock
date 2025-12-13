#!/usr/bin/env python3
"""
Formula Registry
================

Central registry for all financial calculation formulas.
Provides a unified interface to access formulas by name and entity type.
"""

from typing import Dict, Any, Callable, List, Optional
import logging
import inspect

# Import all formulas
from ._base_formulas import (
    calculate_roe, calculate_roa, calculate_roic,
    calculate_gross_margin, calculate_operating_margin, calculate_net_margin,
    calculate_ebit_margin, calculate_ebitda_margin,
    calculate_current_ratio, calculate_quick_ratio, calculate_cash_ratio,
    calculate_debt_to_equity, calculate_debt_to_assets, calculate_equity_multiplier,
    calculate_interest_coverage,
    calculate_asset_turnover, calculate_inventory_turnover, calculate_receivables_turnover,
    calculate_days_sales_outstanding, calculate_days_inventory_outstanding,
    calculate_eps, calculate_book_value_per_share, calculate_ev_ebitda,
    calculate_yoy_growth, calculate_qoq_growth,
    calculate_ttm_sum
)

# Import entity specific formulas
# Note: These imports might be circular if not careful, but registry is usually imported by calculators
from .company_formulas import CompanyFormulas
from .bank_formulas import BankFormulas

logger = logging.getLogger(__name__)

class FormulaRegistry:
    """
    Registry trung tâm cho tất cả các công thức tính toán tài chính.
    Central registry for all financial calculation formulas.
    """
    
    _registry: Dict[str, Callable] = {}
    _entity_registry: Dict[str, Dict[str, Callable]] = {
        "COMPANY": {},
        "BANK": {},
        "INSURANCE": {},
        "SECURITY": {}
    }
    
    def __init__(self):
        """Khởi tạo và đăng ký các công thức mặc định."""
        self._register_base_formulas()
        self._register_entity_formulas()
        
    def _register_base_formulas(self):
        """Đăng ký các công thức chung cho tất cả các loại thực thể."""
        base_formulas = [
            calculate_roe, calculate_roa, calculate_roic,
            calculate_gross_margin, calculate_operating_margin, calculate_net_margin,
            calculate_ebit_margin, calculate_ebitda_margin,
            calculate_current_ratio, calculate_quick_ratio, calculate_cash_ratio,
            calculate_debt_to_equity, calculate_debt_to_assets, calculate_equity_multiplier,
            calculate_interest_coverage,
            calculate_asset_turnover, calculate_inventory_turnover, calculate_receivables_turnover,
            calculate_days_sales_outstanding, calculate_days_inventory_outstanding,
            calculate_eps, calculate_book_value_per_share, calculate_ev_ebitda,
            calculate_yoy_growth, calculate_qoq_growth,
            calculate_ttm_sum
        ]
        
        for formula in base_formulas:
            self.register_formula(formula.__name__, formula, ["ALL"])

    def _register_entity_formulas(self):
        """Đăng ký các công thức đặc thù cho từng loại thực thể."""
        # COMPANY
        self.register_formula("calculate_revenue_growth", CompanyFormulas.calculate_revenue_growth, ["COMPANY"])
        self.register_formula("calculate_profit_growth", CompanyFormulas.calculate_profit_growth, ["COMPANY"])
        self.register_formula("calculate_free_cash_flow", CompanyFormulas.calculate_free_cash_flow, ["COMPANY"])
        
        # BANK
        self.register_formula("calculate_nim", BankFormulas.calculate_nim, ["BANK"])
        self.register_formula("calculate_cir", BankFormulas.calculate_cir, ["BANK"])
        self.register_formula("calculate_plr", BankFormulas.calculate_plr, ["BANK"])
        self.register_formula("calculate_ldr", BankFormulas.calculate_ldr, ["BANK"])
        self.register_formula("calculate_car", BankFormulas.calculate_car, ["BANK"])
        self.register_formula("calculate_npl_ratio", BankFormulas.calculate_npl_ratio, ["BANK"])
        self.register_formula("calculate_efficiency_ratio", BankFormulas.calculate_efficiency_ratio, ["BANK"])

    def register_formula(self, name: str, formula: Callable, entity_types: List[str]):
        """
        Đăng ký một công thức mới vào registry.
        
        Args:
            name: Tên của công thức
            formula: Hàm tính toán
            entity_types: Danh sách các loại thực thể ("COMPANY", "BANK", "ALL", v.v.)
        """
        if "ALL" in entity_types:
            # Register in main registry and all entity registries
            self._registry[name] = formula
            for et in self._entity_registry:
                self._entity_registry[et][name] = formula
        else:
            for et in entity_types:
                if et in self._entity_registry:
                    self._entity_registry[et][name] = formula
                else:
                    logger.warning(f"Loại thực thể không xác định: {et}")

    def get_formula(self, name: str, entity_type: Optional[str] = None) -> Optional[Callable]:
        """
        Lấy công thức theo tên và loại thực thể (tùy chọn).
        
        Args:
            name: Tên của công thức
            entity_type: Ngữ cảnh loại thực thể
            
        Returns:
            Hàm tính toán hoặc None nếu không tìm thấy
        """
        if entity_type and entity_type in self._entity_registry:
            if name in self._entity_registry[entity_type]:
                return self._entity_registry[entity_type][name]
        
        # Fallback to general registry
        return self._registry.get(name)

    def list_formulas(self, entity_type: Optional[str] = None) -> List[str]:
        """Liệt kê các tên công thức có sẵn."""
        if entity_type and entity_type in self._entity_registry:
            return list(self._entity_registry[entity_type].keys())
        return list(self._registry.keys())

# Singleton instance
formula_registry = FormulaRegistry()
