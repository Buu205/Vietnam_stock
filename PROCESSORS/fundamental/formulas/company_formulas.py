"""
Company Financial Formulas

Entity-specific formulas for COMPANY entities that are NOT in _base_formulas.py.

These formulas are specific to companies and should not be duplicated in other entity files.

Registry mapping for company-specific metrics:
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

Author: Formula Extraction Team
Date: 2025-12-11
"""

import pandas as pd
import numpy as np
from typing import Optional

# Handle imports for both module usage and standalone testing
try:
    from .utils import safe_divide, to_percentage
except ImportError:
    from utils import safe_divide, to_percentage


class CompanyFormulas:
    """Entity-specific calculation functions for COMPANY entities."""
    
    # Growth Rates - Company Specific
    @staticmethod
    def calculate_revenue_growth(current_revenue: float, previous_revenue: float) -> Optional[float]:
        """
        Tốc độ tăng trưởng doanh thu (Revenue Growth Rate)

        Công thức: ((Doanh thu hiện tại - Doanh thu kỳ trước) / Doanh thu kỳ trước) × 100

        Đo lường khả năng tăng trưởng doanh thu của công ty.

        Diễn giải:
            - > 20%: Tăng trưởng vượt trội
            - 10-20%: Tăng trưởng tốt
            - 5-10%: Tăng trưởng vừa phải
            - 0-5%: Tăng trưởng chậm
            - < 0%: Sụt giảm doanh thu

        Args:
            current_revenue: Doanh thu kỳ hiện tại (VND)
            previous_revenue: Doanh thu kỳ trước (VND)

        Returns:
            Tốc độ tăng trưởng (%), hoặc None nếu không hợp lệ

        Examples:
            >>> calculate_revenue_growth(120_000_000_000, 100_000_000_000)
            20.0  # 20% growth
        """
        if previous_revenue == 0 or pd.isna(previous_revenue):
            return None
        return round(((current_revenue - previous_revenue) / previous_revenue) * 100, 2)
    
    @staticmethod
    def calculate_profit_growth(current_profit: float, previous_profit: float) -> Optional[float]:
        """
        Tốc độ tăng trưởng lợi nhuận (Profit Growth Rate)

        Công thức: ((Lợi nhuận hiện tại - Lợi nhuận kỳ trước) / Lợi nhuận kỳ trước) × 100

        Đo lường khả năng tăng trưởng lợi nhuận của công ty.

        Diễn giải:
            - > 25%: Tăng trưởng lợi nhuận vượt trội
            - 15-25%: Tăng trưởng lợi nhuận tốt
            - 5-15%: Tăng trưởng lợi nhuận vừa phải
            - 0-5%: Tăng trưởng lợi nhuận chậm
            - < 0%: Sụt giảm lợi nhuận

        Args:
            current_profit: Lợi nhuận kỳ hiện tại (VND)
            previous_profit: Lợi nhuận kỳ trước (VND)

        Returns:
            Tốc độ tăng trưởng (%), hoặc None nếu không hợp lệ

        Examples:
            >>> calculate_profit_growth(24_000_000_000, 20_000_000_000)
            20.0  # 20% growth
        """
        if previous_profit == 0 or pd.isna(previous_profit):
            return None
        return round(((current_profit - previous_profit) / previous_profit) * 100, 2)
    
    # Free Cash Flow - Company Specific
    @staticmethod
    def calculate_free_cash_flow(operating_cash_flow: float, capital_expenditure: float) -> Optional[float]:
        """
        Dòng tiền tự do (Free Cash Flow)

        Công thức: Dòng tiền từ hoạt động kinh doanh - Chi tiêu vốn đầu tư

        Đo lường lượng tiền mặt thực tế công ty tạo ra sau khi đầu tư vào 
        tài sản cố định và vốn lưu động cần thiết để duy trì hoạt động.

        Diễn giải:
            - > 0: FCF dương - công ty tạo ra tiền mặt
            - = 0: FCF bằng không - công ty hòa vốn
            - < 0: FCF âm - công ty tiêu dùng nhiều tiền hơn tạo ra

        Args:
            operating_cash_flow: Dòng tiền từ hoạt động kinh doanh (VND)
            capital_expenditure: Chi tiêu vốn đầu tư (VND)

        Returns:
            Dòng tiền tự do (VND), hoặc None nếu không hợp lệ

        Examples:
            >>> calculate_free_cash_flow(50_000_000_000, 30_000_000_000)
            20_000_000_000  # 20 tỷ VND FCF
        """
        if operating_cash_flow is None or capital_expenditure is None:
            return None
        return operating_cash_flow - capital_expenditure