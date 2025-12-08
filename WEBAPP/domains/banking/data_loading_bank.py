"""Banking domain data loading (bilingual / song ngữ)

Updated: 2025-11-11 - Using centralized DataPaths configuration
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
from streamlit_app.core.formatters import format_valuation_df, format_value
from streamlit_app.core.data_paths import get_fundamental_path

# Use centralized DataPaths configuration
BANK_FUND_PATH = str(get_fundamental_path('bank'))


def get_bank_symbols() -> List[str]:
    """Get list of bank symbols from the bank financial metrics file"""
    try:
        import pandas as pd
        df = pd.read_parquet(BANK_FUND_PATH)
        if 'symbol' in df.columns:
            symbols = df['symbol'].unique().tolist()
            # Filter for major banks
            major_banks = [
                'VCB', 'TCB', 'BID', 'CTG', 'MBB', 'ACB', 'VPB', 'HDB', 'TPB', 'STB',
                'SHB', 'MSB', 'LPB', 'VIB', 'OCB', 'NAB', 'SSB', 'EIB', 'VBB', 'PGB'
            ]
            return [symbol for symbol in major_banks if symbol in symbols]
        return []
    except Exception as e:
        print(f"Error loading bank symbols: {e}")
        return []


def load_bank_valuation(symbol: str, years: int = 5) -> Dict[str, pd.DataFrame]:
    # Placeholder: implement banking valuation loader
    return {'pe': pd.DataFrame(), 'pb': pd.DataFrame(), 'ev_ebitda': pd.DataFrame()}


