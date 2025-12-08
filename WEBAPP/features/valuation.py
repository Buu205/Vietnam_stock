"""Valuation features (bilingual / song ngữ)

Functions to compute percentiles, percentile ranks, and overall valuation label
for ratios such as P/E, P/B, EV/EBITDA.

VN: Các hàm tính toán phân vị (Q1/Q3/Median), percentile rank, và xếp hạng
Overall Valuation dựa trên 3 chỉ số PE/PB/EVEBITDA.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Tuple, Dict
from streamlit_app.core.constants import classify_overall_label
from streamlit_app.core.utils import percentile_rank


def compute_percentiles(series: pd.Series) -> Tuple[float, float, float]:
    """Return (q25, median, q75) ignoring NaNs.

    VN: Tính (Q1, Median, Q3) bỏ qua NaN.
    """
    s = series.dropna()
    if len(s) == 0:
        return float('nan'), float('nan'), float('nan')
    return float(s.quantile(0.25)), float(s.median()), float(s.quantile(0.75))


def compute_percentile_rank(series: pd.Series, current_value: float) -> float:
    """Percentile rank (0..100) of current_value vs series.

    VN: Tính percentile rank (0..100) của giá trị hiện tại so với lịch sử.
    """
    return percentile_rank(series, current_value)


def classify_overall(pe_pct: float, pb_pct: float, ev_pct: float) -> Dict[str, float | str]:
    """Return overall percentile and label from three percentiles.

    VN: Tính percentile tổng hợp và nhãn (Cheap/Below/Above/Expensive) từ 3 chỉ số.
    """
    vals = [v for v in [pe_pct, pb_pct, ev_pct] if not pd.isna(v)]
    overall_pct = float(np.mean(vals)) if vals else float('nan')
    label = classify_overall_label(overall_pct)
    return {"overall_pct": overall_pct, "label": label}


