#!/usr/bin/env python3
"""
Macro Commodity Loader
======================
Service to load Unified Macro & Commodity data for Streamlit.
Replaces old CommodityLoader.
"""

import pandas as pd
import streamlit as st
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from WEBAPP.core.data_paths import DataPaths
from WEBAPP.core.constants import CACHE_TTL_WARM

logger = logging.getLogger(__name__)

@st.cache_data(ttl=CACHE_TTL_WARM, show_spinner=False)
def _load_unified_data_cached(file_path: str, latest_date_key: str) -> pd.DataFrame:
    try:
        df = pd.read_parquet(file_path)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        logger.error(f"Error loading unified data: {e}")
        return pd.DataFrame()

class MacroCommodityLoader:
    def __init__(self):
        self.data_path = DataPaths.unified_macro_commodity()
        
    def load_data(self, force_reload: bool = False) -> pd.DataFrame:
        if force_reload:
            _load_unified_data_cached.clear()
            
        if not self.data_path.exists():
            return pd.DataFrame()
            
        # Get cache key (modification time or latest date if quick)
        try:
            mtime = str(self.data_path.stat().st_mtime)
        except:
            mtime = "unknown"
            
        return _load_unified_data_cached(str(self.data_path), mtime)

    def get_commodities(self) -> pd.DataFrame:
        """Get only Commodity data."""
        df = self.load_data()
        if df.empty: return df
        return df[df['category'] == 'commodity'].copy()

    def get_macro(self) -> pd.DataFrame:
        """Get only Macro data."""
        df = self.load_data()
        if df.empty: return df
        return df[df['category'] == 'macro'].copy()

    def get_series(self, symbol: str) -> pd.DataFrame:
        """Get data for a specific symbol."""
        df = self.load_data()
        if df.empty: return df
        df_res = df[df['symbol'] == symbol].copy()
        return df_res.sort_values('date').reset_index(drop=True)
        
    def get_available_symbols(self, category: str = None) -> List[str]:
        df = self.load_data()
        if df.empty: return []
        if category:
            df = df[df['category'] == category]
        return sorted(df['symbol'].unique().tolist())

    @staticmethod
    def clear_cache():
        _load_unified_data_cached.clear()
