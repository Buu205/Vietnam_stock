"""Bank Financial Formulas

Extracted pure calculation functions from bank_financial_calculator.py.

This module contains all financial formulas used for BANK entity calculations,
separated from data loading and orchestration logic.

Registry mapping:
- BIS_1: total_revenue (Tổng doanh thu)
- BIS_2: interest_income (Thu nhập lãi)
- BIS_3: interest_expense (Chi phí lãi vay)
- BIS_4: fee_and_commission_income (Thu nhập phí và hoa hồng)
- BIS_5: other_operating_income (Thu nhập hoạt động kinh doanh khác)
- BIS_6: other_operating_expense (Chi phí hoạt động kinh doanh khác)
- BIS_7: profit_before_provision_and_tax (Lợi nhuận trước trích lập dự phòng và thuế)
- BIS_8: provision_for_credit_losses (Trích lập dự phòng rủi ro)
- BIS_9: operating_profit (Lợi nhuận hoạt động)
- BIS_10: non_operating_income (Thu nhập ngoài hoạt động)
- BIS_11: non_operating_expense (Chi phí ngoài hoạt động)
- BIS_12: profit_before_tax (Lợi nhuận trước thuế)
- BIS_13: income_tax_expense (Chi phí thuế hiện hành)
- BIS_14: profit_after_tax (Lợi nhuận sau thuế)
- BIS_15: profit_from_discontinued (Lợi nhuận từ hoạt động kinh doanh đã ngừng)
- BIS_18: net_profit_from_continuing (Lợi nhuận từ hoạt động kinh doanh tiếp tục)
- BIS_20: net_profit (Lợi nhuận sau thuế)
- BBS_4: loans_and_advances_to_credit_institutions (Cho vay và tạm ứng các TCTD)
- BBS_7: investments_in_associates_and_joint_ventures (Đầu tư vào liên doanh và liên doanh)
- BBS_8: fixed_assets (Tài sản cố định)
- BBS_11: intangible_assets (Tài sản vô hình)
- BBS_12: goodwill (Lợi thế thương hiệu)
- BBS_14: other_assets (Tài sản khác)
- BBS_15: accumulated_depreciation (Hao mũ lũy kế tích lũy kế)
- BBS_16: provision_for_risks (Trích lập dự phòng rủi ro)
- BBS_18: non_current_assets (Tài sản dài hạn)
- BBS_19: inventories (Hàng tồn kho)
- BBS_20: current_assets (Tài sản ngắn hạn)
- BBS_21: other_current_assets (Tài sản ngắn hạn khác)
- BBS_22: assets_held_for_sale (Tài sản tài chính bán)
- BBS_23: total_assets (Tổng tài sản)
- BBS_24: short_term_borrowings (Vay và nợ thuê ngắn hạn)
- BBS_25: long_term_borrowings (Vay và nợ dài hạn)
- BBS_26: other_current_liabilities (Nợ ngắn hạn khác)
- BBS_27: total_current_liabilities (Tổng nợ ngắn hạn)
- BBS_30: long_term_liabilities (Nợ dài hạn)
- BBS_31: other_long_term_liabilities (Nợ dài hạn khác)
- BBS_32: total_long_term_liabilities (Tổng nợ dài hạn)
- BBS_33: total_liabilities (Tổng nợ phải trả)
- BBS_35: share_capital (Vốn cổ phần có ưu đãi)
- BBS_36: treasury_shares (Cổ phiếu thường)
- BBS_37: share_premium (Thặng dư vốn cổ phần)
- BBS_40: retained_earnings (Lợi nhuận giữ lại)
- BBS_41: other_comprehensive_income (Thu nhập TCDN khác)
- BBS_42: net_profit_before_tax (Lợi nhuận trước thuế)
- BBS_50: current_income_tax_expense (Chi phí thuế TNDN hiện hành)
- BBS_52: deferred_tax_expense (Chi phí thuế hoãn lại)
- BBS_53: net_profit_before_tax (Lợi nhuận trước thuế - Gộp)
- BBS_54: profit_before_tax (Lợi nhuận trước thuế - Gộp)
- BBS_55: income_tax_expense (Chi phí thuế)
- BBS_56: profit_before_tax (Lợi nhuận trước thuế)
- BBS_57: profit_before_tax (Lợi nhuận trước thuế)
- BBS_60: profit_after_tax (Lợi nhuận sau thuế)
- BBS_70: net_profit (Lợi nhuận sau thuế)
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any


class BankFormulas:
    """Pure calculation functions for bank financial metrics."""
    
    # Profitability Ratios
    @staticmethod
    def calculate_nim(net_interest_income: float, total_earning_assets: float) -> Optional[float]:
        """
        Net Interest Margin (NIM).
        
        Formula: (Net Interest Income / Total Earning Assets) × 100
        Unit: Percentage (%)
        Good range: 2-5% (Vietnam banking sector)
        """
        if total_earning_assets == 0 or pd.isna(total_earning_assets):
            return None
        return round((net_interest_income / total_earning_assets) * 100, 2)
    
    @staticmethod
    def calculate_cir(operating_expense: float, operating_income: float) -> Optional[float]:
        """
        Cost to Income Ratio (CIR).
        
        Formula: (Operating Expenses / Operating Income) × 100
        Unit: Percentage (%)
        Good range: 30-60% (typical for Vietnam banks)
        """
        if operating_income == 0 or pd.isna(operating_income):
            return None
        return round((operating_expense / operating_income) * 100, 2)
    
    @staticmethod
    def calculate_plr(provision_for_credit_losses: float, total_loans: float) -> Optional[float]:
        """
        Provision to Loan Ratio (PLR).
        
        Formula: (Provision for Credit Losses / Total Loans) × 100
        Unit: Percentage (%)
        Good range: < 5% (healthy bank)
        """
        if total_loans == 0 or pd.isna(total_loans):
            return None
        return round((provision_for_credit_losses / total_loans) * 100, 2)
    
    @staticmethod
    def calculate_ldr(loan_loss_allowance: float, customer_loans: float, other_borrowings: float) -> Optional[float]:
        """
        Loans to Deposit Ratio (LDR).
        
        Formula: ((Customer Loans + Other Borrowings) - (Loan Loss Allowance)) / 
                 ((Customer Loans + Other Borrowings) - Loan Loss Allowance + Total Deposits)
        Unit: Percentage (%)
        Good range: 80-100% (regulated requirement)
        """
        total_funds = customer_loans + other_borrowings
        net_funds = total_funds - loan_loss_allowance
        
        # We need deposits data which might not be available in the current dataset
        # This is a simplified calculation
        if total_funds == 0 or pd.isna(total_funds):
            return None
            
        # Placeholder for deposits - would need actual deposits data
        deposits = 1.0  # Simplified - would need actual data
        
        ldr = (net_funds / (net_funds + deposits)) * 100
        return round(ldr, 2)
    
    @staticmethod
    def calculate_car(loan_loss_allowance: float, total_loans: float, risk_weighted_assets: float) -> Optional[float]:
        """
        Capital Adequacy Ratio (CAR).
        
        Formula: (Risk-Weighted Assets / (Loan Loss Allowance + Total Loans))
        Unit: Ratio (x:1)
        Good range: > 8% (minimum regulatory requirement)
        """
        if total_loans == 0 or pd.isna(total_loans):
            return None
        return round((risk_weighted_assets / (loan_loss_allowance + total_loans)), 2)
    
    # Asset Quality Metrics
    @staticmethod
    def calculate_npl_ratio(non_performing_loans: float, total_loans: float) -> Optional[float]:
        """
        Non-Performing Loan Ratio.
        
        Formula: (Non-Performing Loans / Total Loans) × 100
        Unit: Percentage (%)
        Good range: < 3% (healthy bank)
        """
        if total_loans == 0 or pd.isna(total_loans):
            return None
        return round((non_performing_loans / total_loans) * 100, 2)
    
    @staticmethod
    # Efficiency Metrics
    @staticmethod
    def calculate_efficiency_ratio(operating_income: float, operating_expense: float) -> Optional[float]:
        """
        Bank Efficiency Ratio.
        
        Formula: Operating Income / Operating Expenses
        Unit: Ratio (x:1)
        Good range: > 1.2 (efficient)
        """
        if operating_expense == 0 or pd.isna(operating_expense):
            return None
        return round(operating_income / operating_expense, 2)
    
    # Utility Functions
    @staticmethod
    def safe_divide(numerator: float, denominator: float, result_nan: bool = True) -> Optional[float]:
        """
        Safely divide two values, handling division by zero and NaN.
        
        Args:
            numerator: Value to divide
            denominator: Value to divide by
            result_nan: Whether to return NaN if denominator is zero
            
        Returns:
            Division result or None/NaN
        """
        if denominator == 0 or pd.isna(denominator):
            return np.nan if result_nan else None
        return numerator / denominator