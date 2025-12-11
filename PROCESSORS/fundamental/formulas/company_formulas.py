"""
Company Financial Formulas

Extracted pure calculation functions from company_financial_calculator.py.

This module contains all financial formulas used for COMPANY entity calculations,
separated from data loading and orchestration logic.

Registry mapping:
- CIS_10: total_revenue (Doanh thu thuần)
- CIS_11: gross_profit (Lợi nhuận gộp)
- CIS_12: selling_expenses (Chi phí bán hàng)
- CIS_18: other_expenses (Chi phí quản lý doanh nghiệp)
- CIS_20: financial_expenses (Chi phí tài chính)
- CIS_22: net_profit_before_tax (Lợi nhuận trước thuế)
- CIS_25: corporate_income_tax (Thuế TNDN)
- CIS_30: other_profit (Lợi nhuận khác)
- CIS_31: net_profit_after_tax (Lợi nhuận sau thuế)
- CIS_34: net_profit_from_continuing (Lợi nhuận từ HĐKD kinh doanh)
- CIS_35: net_profit_from_discontinued (Lợi nhuận từ HĐKD ngừng hoạt động)
- CIS_36: net_profit (Lợi nhuận sau thuế - Hợp nhất)
- CIS_40: other_comprehensive_income (Thu nhập khác TCDN)
- CIS_42: depreciation (Khấu hao)
- CIS_50: operating_profit (Lợi nhuận từ HĐKD)
- CIS_52: financial_income (Thu nhập tài chính)
- CIS_54: profit_before_tax (Lợi nhuận trước thuế - Lợi nhuận gộp)
- CIS_55: income_tax (Thuế TNDN phải nộp)
- CIS_60: net_profit (Lợi nhuận sau thuế)
- CIS_61: retained_earnings (Lợi nhuận giữ lại)
- CIS_62: net_profit (Lợi nhuận sau thuế công ty mẹ)
- CIS_64: profit_before_tax (Lợi nhuận trước thuế - Gộp)
- CIS_65: income_tax_expense (Chi phí thuế)
- CIS_70: profit_before_tax (Lợi nhuận trước thuế - Gộp)
- CIS_71: current_income_tax_expense (Chi phí thuế TNDN hiện hành)
- CIS_72: net_profit (Lợi nhuận sau thuế)
- CIS_80: other_income (Thu nhập khác)
- CIS_81: interest_income (Thu nhập lãi)
- CIS_82: interest_expense (Chi phí lãi vay)
- CIS_90: profit_before_tax (Lợi nhuận trước thuế)
- CIS_92: net_cash_flow (Dòng tiền thuần từ hoạt động kinh doanh)
- CBS_100: total_assets (Tổng tài sản)
- CBS_110: intangible_assets (Tài sản vô hình)
- CBS_120: ppe (TSCĐH)
- CBS_130: current_assets (Tài sản ngắn hạn)
- CBS_135: inventories (Hàng tồn kho)
- CBS_140: non_current_assets (Tài sản dài hạn)
- CBS_150: total_assets (Tổng tài sản)
- CBS_210: current_liabilities (Nợ ngắn hạn)
- CBS_220: st_borrowings (Vay và nợ thuê ngắn hạn)
- CBS_225: non_current_liabilities (Nợ dài hạn)
- CBS_235: total_liabilities (Tổng nợ phải trả)
- CBS_250: total_equity (Vốn chủ sở hữu)
- CBS_260: treasury_shares (Cổ phiếu quỹ)
- CBS_262: capital_reserve (Quỹ dự trữ vốn)
- CBS_270: total_equity (Tổng vốn chủ sở hữu)
- CBS_280: minority_interests (Lợi ích của cổ đông thiểu số)
- CBS_290: net_profit (Lợi nhuận sau thuế)
- CBS_310: retained_earnings (Lợi nhuận giữ lại)
- CBS_320: comprehensive_income (Tổng thu nhập)
- CBS_340: total_assets (Tổng tài sản)
- CBS_400: common_shares (Số cổ phiếu thường)
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any


class CompanyFormulas:
    """Pure calculation functions for company financial metrics."""
    
    # Profitability Ratios
    @staticmethod
    def calculate_roe(net_profit: float, total_equity: float) -> Optional[float]:
        """
        Return on Equity (ROE).
        
        Formula: (Net Profit / Total Equity) × 100
        Unit: Percentage (%)
        Good range: 15-25% (Vietnam market)
        """
        if total_equity == 0 or pd.isna(total_equity):
            return None
        return round((net_profit / total_equity) * 100, 2)
    
    @staticmethod
    def calculate_roa(net_profit: float, total_assets: float) -> Optional[float]:
        """
        Return on Assets (ROA).
        
        Formula: (Net Profit / Total Assets) × 100
        Unit: Percentage (%)
        Good range: 5-15% (Vietnam market)
        """
        if total_assets == 0 or pd.isna(total_assets):
            return None
        return round((net_profit / total_assets) * 100, 2)
    
    @staticmethod
    def calculate_gross_margin(gross_profit: float, revenue: float) -> Optional[float]:
        """
        Gross Profit Margin.
        
        Formula: (Gross Profit / Revenue) × 100
        Unit: Percentage (%)
        Good range: 20-40% (manufacturing), 15-30% (services)
        """
        if revenue == 0 or pd.isna(revenue):
            return None
        return round((gross_profit / revenue) * 100, 2)
    
    @staticmethod
    def calculate_net_margin(net_profit: float, revenue: float) -> Optional[float]:
        """
        Net Profit Margin.
        
        Formula: (Net Profit / Revenue) × 100
        Unit: Percentage (%)
        Good range: 5-15% (Vietnam market)
        """
        if revenue == 0 or pd.isna(revenue):
            return None
        return round((net_profit / revenue) * 100, 2)
    
    @staticmethod
    def calculate_operating_margin(operating_profit: float, revenue: float) -> Optional[float]:
        """
        Operating Profit Margin.
        
        Formula: (Operating Profit / Revenue) × 100
        Unit: Percentage (%)
        Good range: 10-20% (Vietnam market)
        """
        if revenue == 0 or pd.isna(revenue):
            return None
        return round((operating_profit / revenue) * 100, 2)
    
    # Growth Rates
    @staticmethod
    def calculate_revenue_growth(current_revenue: float, previous_revenue: float) -> Optional[float]:
        """
        Revenue Growth Rate.
        
        Formula: ((Current Revenue - Previous Revenue) / Previous Revenue) × 100
        Unit: Percentage (%)
        Good range: 10-20% (growth companies)
        """
        if previous_revenue == 0 or pd.isna(previous_revenue):
            return None
        return round(((current_revenue - previous_revenue) / previous_revenue) * 100, 2)
    
    @staticmethod
    def calculate_profit_growth(current_profit: float, previous_profit: float) -> Optional[float]:
        """
        Profit Growth Rate.
        
        Formula: ((Current Profit - Previous Profit) / Previous Profit) × 100
        Unit: Percentage (%)
        """
        if previous_profit == 0 or pd.isna(previous_profit):
            return None
        return round(((current_profit - previous_profit) / previous_profit) * 100, 2)
    
    # Financial Health Ratios
    @staticmethod
    def calculate_debt_to_equity(total_liabilities: float, total_equity: float) -> Optional[float]:
        """
        Debt to Equity Ratio.
        
        Formula: (Total Liabilities / Total Equity)
        Unit: Ratio (x:1)
        Good range: < 2.0 (healthy)
        """
        if total_equity == 0 or pd.isna(total_equity):
            return None
        return round(total_liabilities / total_equity, 2)
    
    @staticmethod
    def calculate_current_ratio(current_assets: float, current_liabilities: float) -> Optional[float]:
        """
        Current Ratio.
        
        Formula: (Current Assets / Current Liabilities)
        Unit: Ratio (x:1)
        Good range: > 1.5 (healthy)
        """
        if current_liabilities == 0 or pd.isna(current_liabilities):
            return None
        return round(current_assets / current_liabilities, 2)
    
    # Efficiency Ratios
    @staticmethod
    def calculate_asset_turnover(revenue: float, total_assets: float) -> Optional[float]:
        """
        Asset Turnover Ratio.
        
        Formula: (Revenue / Total Assets)
        Unit: Times per year
        Good range: > 1.0 (efficient)
        """
        if total_assets == 0 or pd.isna(total_assets):
            return None
        return round(revenue / total_assets, 2)
    
    @staticmethod
    def calculate_inventory_turnover(cogs: float, inventory: float) -> Optional[float]:
        """
        Inventory Turnover Ratio.
        
        Formula: (Cost of Goods Sold / Inventory)
        Unit: Times per year
        Good range: > 6.0 (efficient)
        """
        if inventory == 0 or pd.isna(inventory):
            return None
        return round(cogs / inventory, 2)
    
    # Market Metrics
    @staticmethod
    def calculate_eps(net_profit: float, common_shares: float) -> Optional[float]:
        """
        Earnings Per Share.
        
        Formula: (Net Profit / Common Shares) × 10,000
        Unit: VND per share
        """
        if common_shares == 0 or pd.isna(common_shares):
            return None
        return round((net_profit * 1e9) / (common_shares * 10000), 0)
    
    @staticmethod
    def calculate_pe_ratio(price_per_share: float, eps: float) -> Optional[float]:
        """
        Price to Earnings Ratio.
        
        Formula: (Price per Share / Earnings Per Share)
        Unit: Times (years)
        Good range: 5-25 (reasonable valuation)
        """
        if eps == 0 or pd.isna(eps) or eps < 0:
            return None
        return round(price_per_share / eps, 2)
    
    @staticmethod
    def calculate_pb_ratio(price_per_share: float, book_value_per_share: float) -> Optional[float]:
        """
        Price to Book Value Ratio.
        
        Formula: (Price per Share / Book Value per Share)
        Unit: Times
        Good range: 1-5 (reasonable valuation)
        """
        if book_value_per_share == 0 or pd.isna(book_value_per_share):
            return None
        return round(price_per_share / book_value_per_share, 2)
    
    # Cash Flow Metrics
    @staticmethod
    def calculate_operating_cash_flow_ratio(operating_cash_flow: float, net_profit: float) -> Optional[float]:
        """
        Operating Cash Flow to Net Profit Ratio.
        
        Formula: (Operating Cash Flow / Net Profit)
        Unit: Ratio (x:1)
        Good range: > 1.0 (healthy)
        """
        if net_profit == 0 or pd.isna(net_profit) or net_profit < 0:
            return None
        return round(operating_cash_flow / net_profit, 2)
    
    @staticmethod
    def calculate_free_cash_flow(operating_cash_flow: float, capital_expenditure: float) -> Optional[float]:
        """
        Free Cash Flow.
        
        Formula: (Operating Cash Flow - Capital Expenditure)
        Unit: Amount in VND
        """
        if operating_cash_flow is None or capital_expenditure is None:
            return None
        return operating_cash_flow - capital_expenditure
    
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