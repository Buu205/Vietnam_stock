"""Technical domain data loading (bilingual / song ngữ)

Đọc các file parquet technical: moving averages, RSI, MACD, Bollinger, breadth,
rotation, signals…
"""

from __future__ import annotations
from typing import Dict, List
from pathlib import Path
import duckdb
import pandas as pd
from streamlit_app.core.formatters import format_value, format_df_column
from streamlit_app.core.utils import get_data_path

# Import streamlit for caching (optional, only if available)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    # Dummy decorator if streamlit not available
    def st_cache_data(**kwargs):
        def decorator(func):
            return func
        return decorator

# Example paths (có thể hiệu chỉnh sau)
OHLCV_BASIC = \
    get_data_path("calculated_results/technical/basic_data/basic_data_full.parquet")
RSI_PATH = \
    get_data_path("calculated_results/technical/rsi/rsi_full.parquet")
MA_PATH = \
    get_data_path("calculated_results/technical/moving_averages/moving_averages_full.parquet")

# MA Screening hiện đang được script daily ghi ra thư mục technical riêng:
# calculated_results/technical/ma_screening_latest.parquet
# Sử dụng get_data_path() để nhất quán với các path khác
MA_SCREENING_PATH = get_data_path("calculated_results/technical/ma_screening_latest.parquet")


def get_connection() -> duckdb.DuckDBPyConnection:
    return duckdb.connect()


def get_technical_symbols() -> List[str]:
    conn = get_connection()
    df = conn.execute(f"SELECT DISTINCT symbol FROM read_parquet('{str(OHLCV_BASIC)}') ORDER BY symbol").fetchdf()
    return df['symbol'].tolist()


def load_rsi(symbol: str) -> pd.DataFrame:
    conn = get_connection()
    df = conn.execute(
        f"SELECT * FROM read_parquet('{str(RSI_PATH)}') WHERE symbol = ? AND TRY_CAST(date AS DATE) >= '1900-01-01' ORDER BY TRY_CAST(date AS DATE)", [symbol]
    ).fetchdf()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df


def _load_ma_screening_impl() -> pd.DataFrame:
    """Internal implementation to load MA screening data"""
    if not MA_SCREENING_PATH.exists():
        return pd.DataFrame()
    
    try:
        df = pd.read_parquet(MA_SCREENING_PATH)
        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        import logging
        logging.error(f"Error loading MA screening from {MA_SCREENING_PATH}: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return pd.DataFrame()


# Cache with short TTL to allow fresh data while avoiding repeated file reads
if HAS_STREAMLIT:
    @st.cache_data(ttl=60, show_spinner=False)  # Cache for 1 minute
    def load_ma_screening() -> pd.DataFrame:
        """Load MA screening data from latest parquet file (cached for 1 minute)"""
        return _load_ma_screening_impl()
else:
    def load_ma_screening() -> pd.DataFrame:
        """Load MA screening data from latest parquet file"""
        return _load_ma_screening_impl()


def get_ma_screening_metadata() -> Dict:
    """Get metadata about MA screening data"""
    df = load_ma_screening()
    
    if df.empty:
        return {
            'status': 'empty',
            'message': 'No MA screening data available',
            'last_update': None,
            'symbol_count': 0
        }
    
    latest_date = df['date'].max() if 'date' in df.columns else None
    symbol_count = df['symbol'].nunique() if 'symbol' in df.columns else 0
    
    return {
        'status': 'ok',
        'message': 'MA screening data loaded successfully',
        'last_update': latest_date,
        'symbol_count': symbol_count,
        'total_records': len(df)
    }


