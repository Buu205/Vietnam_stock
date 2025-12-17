"""Company domain data loading (bilingual / song ngữ)

Wrapper cho core.data_loading với đường dẫn cố định cho Company.
Updated: 2025-11-11 - Using centralized DataPaths configuration
Updated: 2025-12-17 - Use SymbolLoader for liquid tickers
"""

from __future__ import annotations
import os
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
from WEBAPP.core.data_loading import load_symbol_list, load_valuation_generic
from WEBAPP.core.data_paths import DataPaths, get_fundamental_path, get_valuation_path
from WEBAPP.core.symbol_loader import SymbolLoader
from pathlib import Path
import streamlit as st
from WEBAPP.core.formatters import format_valuation_df, format_value


# Use centralized DataPaths configuration
PE_PATH = str(get_valuation_path('pe'))
PB_PATH = str(get_valuation_path('pb'))
EV_PATH = str(get_valuation_path('ev_ebitda'))
FUND_PATH = str(get_fundamental_path('company'))


def get_company_symbols() -> List[str]:
    """
    Get list of liquid company symbols from master_symbols.json.
    Returns 261 companies with >1B VND/day trading value.
    """
    try:
        loader = SymbolLoader()
        return loader.get_symbols_by_entity('COMPANY')
    except Exception as e:
        print(f"Error loading company symbols from SymbolLoader: {e}")
        # Fallback to parquet if SymbolLoader fails
        fund_file = Path(FUND_PATH)
        if not fund_file.exists():
            st.warning("Company fundamentals file is missing. Please ensure it exists at DATA/processed/fundamental/company/company_financial_metrics.parquet")
            return []
        return load_symbol_list(FUND_PATH)


def load_company_valuation(symbol: str, start_year: int = None) -> Dict[str, pd.DataFrame]:
    """
    Load company valuation data (PE, PB, EV/EBITDA)
    
    Args:
        symbol: Stock symbol
        start_year: Starting year (e.g., 2020). If None, defaults to 5 years ago
        
    Returns:
        Dict with keys 'pe', 'pb', 'ev_ebitda'
        
    VN: Load dữ liệu định giá công ty từ năm bắt đầu được chọn
    """
    # Convert start_year to cutoff date string
    # VN: Chuyển đổi năm bắt đầu thành ngày cutoff
    if start_year is not None:
        # Use Jan 1 of start_year as cutoff
        cutoff_str = f"{start_year}-01-01"
    else:
        # Default: 5 years ago from today
        cutoff_date = datetime.now() - timedelta(days=5 * 365)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
    
    return load_valuation_generic(symbol, cutoff_str, PE_PATH, PB_PATH, EV_PATH)


