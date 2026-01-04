"""Data loading layer – dùng chung (bilingual / song ngữ)

Cung cấp API load dữ liệu chuẩn (DuckDB/Parquet), có cache và lọc outlier
mặc định. Domain có thể kế thừa/ghi đè ở thư mục `domains/`.

Updated: 2025-12-17 - Added get_all_symbols() using SymbolLoader
Updated: 2026-01-04 - Added caching with TTL constants
"""

from __future__ import annotations
import duckdb
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional
from WEBAPP.core.constants import OUTLIERS_DEFAULT, CACHE_TTL_COLD, CACHE_TTL_STATIC
from WEBAPP.core.utils import clip_outliers
from WEBAPP.core.formatters import format_valuation_df, format_value
from WEBAPP.core.symbol_loader import SymbolLoader


def get_connection() -> duckdb.DuckDBPyConnection:
    """Return a DuckDB connection (no persistence).

    VN: Trả về kết nối DuckDB, dùng để đọc Parquet nhanh.
    """
    return duckdb.connect()


def get_all_symbols(entity_type: Optional[str] = None) -> List[str]:
    """
    Get list of liquid symbols from master_symbols.json.
    Returns 315 symbols with >1B VND/day trading value.

    Args:
        entity_type: 'COMPANY', 'BANK', 'SECURITY', 'INSURANCE' or None for all

    Returns:
        List of liquid symbols
    """
    loader = SymbolLoader()
    if entity_type:
        return loader.get_symbols_by_entity(entity_type.upper())
    return loader.get_all_symbols()


@st.cache_data(ttl=CACHE_TTL_STATIC, show_spinner=False)
def load_symbol_list(path: str) -> List[str]:
    """Load danh sách symbol duy nhất từ file parquet (cached 24h).
    NOTE: Consider using get_all_symbols() instead for liquid tickers only.

    Args:
        path: absolute path đến parquet symbols nguồn.
    """
    conn = get_connection()
    df = conn.execute(f"SELECT DISTINCT symbol FROM read_parquet('{path}') ORDER BY symbol").fetchdf()
    return df['symbol'].tolist()


@st.cache_data(ttl=CACHE_TTL_COLD, show_spinner=False)
def load_valuation_generic(symbol: str, start_date: str,
                           pe_path: str, pb_path: str, ev_path: str) -> Dict[str, pd.DataFrame]:
    """Load valuation (PE/PB/EVEBITDA) cho 1 symbol từ 3 parquet (cached 1h).

    VN: Trả về dict {'pe','pb','ev_ebitda'} – đã lọc outliers mặc định.
    """
    conn = get_connection()
    pe = conn.execute(
        f"""
        SELECT symbol, date, close_price, ttm_earning_billion_vnd, shares_outstanding,
               eps, pe_ratio, sector
        FROM read_parquet('{pe_path}')
        WHERE symbol = ? AND TRY_CAST(date AS DATE) >= ? AND TRY_CAST(date AS DATE) >= '1900-01-01'
        ORDER BY TRY_CAST(date AS DATE)
        """ , [symbol, start_date]).fetchdf()

    pb = conn.execute(
        f"""
        SELECT symbol, date, close_price, equity_billion_vnd, shares_outstanding,
               bps, pb_ratio, sector
        FROM read_parquet('{pb_path}')
        WHERE symbol = ? AND TRY_CAST(date AS DATE) >= ? AND TRY_CAST(date AS DATE) >= '1900-01-01'
        ORDER BY TRY_CAST(date AS DATE)
        """ , [symbol, start_date]).fetchdf()

    ev = conn.execute(
        f"""
        SELECT symbol, date, close_price, market_cap, total_debt_long, total_debt_short,
               total_debt, cash_equivalent, ev, ebitda_ttm, ebitda_vnd, ev_ebitda_ratio
        FROM read_parquet('{ev_path}')
        WHERE symbol = ? AND TRY_CAST(date AS DATE) >= ? AND TRY_CAST(date AS DATE) >= '1900-01-01'
        ORDER BY TRY_CAST(date AS DATE)
        """ , [symbol, start_date]).fetchdf()

    # Outlier filters (mặc định)
    if not pe.empty:
        pe = clip_outliers(pe, 'pe_ratio', OUTLIERS_DEFAULT['pe_ratio'])
    if not pb.empty:
        pb = clip_outliers(pb, 'pb_ratio', OUTLIERS_DEFAULT['pb_ratio'])
    if not ev.empty:
        ev = clip_outliers(ev, 'ev_ebitda_ratio', OUTLIERS_DEFAULT['ev_ebitda_ratio'])

    # Ensure datetime
    for df in (pe, pb, ev):
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])

    return {'pe': pe, 'pb': pb, 'ev_ebitda': ev}


