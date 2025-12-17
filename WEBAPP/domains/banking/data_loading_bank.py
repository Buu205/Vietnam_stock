"""Banking domain data loading (bilingual / song ngữ)

Updated: 2025-11-11 - Using centralized DataPaths configuration
Updated: 2025-12-17 - Use SymbolLoader for liquid tickers
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
from WEBAPP.core.formatters import format_valuation_df, format_value
from WEBAPP.core.data_paths import get_fundamental_path
from WEBAPP.core.symbol_loader import SymbolLoader

# Use centralized DataPaths configuration
BANK_FUND_PATH = str(get_fundamental_path('bank'))


def get_bank_symbols() -> List[str]:
    """
    Get list of liquid bank symbols from master_symbols.json.
    Returns 22 banks with >1B VND/day trading value.
    """
    try:
        loader = SymbolLoader()
        return loader.get_symbols_by_entity('BANK')
    except Exception as e:
        print(f"Error loading bank symbols from SymbolLoader: {e}")
        # Fallback to parquet if SymbolLoader fails
        try:
            df = pd.read_parquet(BANK_FUND_PATH)
            if 'symbol' in df.columns:
                return sorted(df['symbol'].unique().tolist())
        except Exception:
            pass
        return []


def load_bank_valuation(symbol: str, years: int = 5) -> Dict[str, pd.DataFrame]:
    # Placeholder: implement banking valuation loader
    return {'pe': pd.DataFrame(), 'pb': pd.DataFrame(), 'ev_ebitda': pd.DataFrame()}


