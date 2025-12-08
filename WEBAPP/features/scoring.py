"""Composite scoring (song ngữ)

Tạo điểm tổng hợp ngắn/trung/dài hạn từ nhiều chỉ số.
"""

from __future__ import annotations
import numpy as np


def weighted_score(values: dict[str, float], weights: dict[str, float]) -> float:
    """Compute weighted score from dict values and weights.

    VN: Tính điểm theo trọng số từ nhiều chỉ tiêu.
    """
    score = 0.0
    total_w = 0.0
    for k, v in values.items():
        w = weights.get(k, 0.0)
        if v is None or np.isnan(v):
            continue
        score += v * w
        total_w += w
    return score / total_w if total_w > 0 else float('nan')


