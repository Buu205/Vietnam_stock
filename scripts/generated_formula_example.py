#!/usr/bin/env python3
"""
AI-Generated Formula
"""

import pandas as pd
from PROCESSORS.fundamental.formulas.utils import safe_divide

def calculate_operating_expenses_to_revenue(df: pd.DataFrame) -> pd.Series:
    """
    Tính tỷ lệ 9. Chi phí bán hàng
    trên 10. Chi phí quản lý doanh nghiệp
    
    Áp dụng cho: COMPANY

    Args:
        df: DataFrame chứa dữ liệu pivot với các metric codes làm columns

    Returns:
        Series chứa kết quả tính toán

    Dependencies:
        CIS_25, CIS_26, CIS_10

    Entity Types:
        COMPANY
    """
        return safe_divide(
        df['CIS_25'],
        df['CIS_26']
    ) * 100  # Convert to percentage
