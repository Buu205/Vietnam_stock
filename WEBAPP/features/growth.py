"""Growth features (song ngữ)

Tính tốc độ tăng trưởng: Revenue, Gross Profit, EBIT, EBITDA, NPAT...
"""

from __future__ import annotations
import pandas as pd


def compute_growth(series: pd.Series, periods: int = 4) -> pd.Series:
    """YoY growth based on specified periods (default: quarterly YoY = 4).

    VN: Tăng trưởng YoY theo số kỳ (mặc định 4 cho dữ liệu quý).
    """
    s = pd.to_numeric(series, errors='coerce')
    return (s / s.shift(periods) - 1.0) * 100.0


