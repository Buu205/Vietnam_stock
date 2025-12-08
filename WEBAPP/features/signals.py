"""Technical signals (song ngữ)

Các hàm tín hiệu đơn giản như MA/EMA crossover, RSI levels, MACD cross.
"""

from __future__ import annotations
import pandas as pd


def moving_average(series: pd.Series, window: int) -> pd.Series:
    return pd.to_numeric(series, errors='coerce').rolling(window=window, min_periods=1).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    return pd.to_numeric(series, errors='coerce').ewm(span=span, adjust=False).mean()


def crossover(short: pd.Series, long: pd.Series) -> pd.Series:
    """Return 1 when short crosses above long, -1 when crosses below, else 0."""
    prev = (short.shift(1) > long.shift(1))
    curr = (short > long)
    up = (~prev) & curr
    down = prev & (~curr)
    return up.astype(int) - down.astype(int)


