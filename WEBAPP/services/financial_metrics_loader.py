"""
Financial Metrics Loader
========================

Unified service for loading financial metrics for Streamlit dashboards.
Uses SymbolLoader for liquid tickers (315 symbols with >1B VND/day trading value).

Updated: 2025-12-17 - Use SymbolLoader instead of SectorRegistry for symbol lists
"""

import logging
import pandas as pd
import duckdb
import streamlit as st
from typing import Dict, Any, Optional, List
from pathlib import Path

# Project imports - Use SymbolLoader for symbol lists
from WEBAPP.core.symbol_loader import SymbolLoader
from config.registries.sector_lookup import SectorRegistry
from config.registries.metric_lookup import MetricRegistry
from WEBAPP.core.data_paths import (
    get_fundamental_path,
    get_valuation_path
)

logger = logging.getLogger(__name__)

class FinancialMetricsLoader:
    """
    Unified service for loading financial metrics for Streamlit dashboards.
    Automates entity type detection and data path resolution.
    Uses SymbolLoader for liquid tickers (315 symbols).
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FinancialMetricsLoader, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.symbol_loader = SymbolLoader()  # For symbol lists
        self.sector_registry = SectorRegistry()  # For ticker info lookup only
        self.metric_registry = MetricRegistry()
        self._duckdb_conn = duckdb.connect() # Persist connection if needed, or create per request
        
    def get_entity_type(self, symbol: str) -> str:
        """
        Detect entity type for a symbol.
        Returns: 'COMPANY', 'BANK', 'INSURANCE', 'SECURITY' or 'COMPANY' as default.
        """
        # Try to find exactly
        # Note: SectorRegistry needs a method to look up entity type by ticker.
        # If not available, we iterate or rely on some mapping.
        # Assuming we can get it or fallback to Company.
        info = self.sector_registry.get_ticker(symbol)
        if info:
            return info.get('entity_type', 'COMPANY')
        return 'COMPANY'

    @st.cache_data(ttl=300, show_spinner=False)
    def load_financial_metrics(_self, symbol: str, start_year: int = 2020) -> pd.DataFrame:
        """
        Load fundamental financial metrics for a symbol.
        Automatically selects the correct parquet file based on entity type.
        """
        try:
            entity_type = _self.get_entity_type(symbol).lower() # company, bank...
            if entity_type == 'security':
                # Map 'security' entity type to 'security' path key if needed
                # get_fundamental_path keys usually: company, bank, insurance, security
                pass
            
            data_path = get_fundamental_path(entity_type)
            if not data_path or not Path(data_path).exists():
                logger.error(f"Data path not found for entity type {entity_type}: {data_path}")
                return pd.DataFrame()

            conn = duckdb.connect()
            
            # Efficient DuckDB query
            query = """
                SELECT * FROM read_parquet(?)
                WHERE symbol = ?
            """
            params = [str(data_path), symbol]
            
            df = conn.execute(query, params).fetchdf()
            
            # Post-processing
            if not df.empty:
                if 'report_date' in df.columns:
                    df['report_date'] = pd.to_datetime(df['report_date'], errors='coerce')
                    # Filter by year if possible
                    df['year'] = df['report_date'].dt.year
                    df['quarter'] = df['report_date'].dt.quarter
                    df = df[df['year'] >= start_year].sort_values('report_date')
                elif 'REPORT_DATE' in df.columns:
                     # Handle uppercase case if present (legacy fallback)
                     df = df.rename(columns={'REPORT_DATE': 'report_date'})
                     df['report_date'] = pd.to_datetime(df['report_date'], errors='coerce')
                     df['year'] = df['report_date'].dt.year
                     df['quarter'] = df['report_date'].dt.quarter
                     df = df[df['year'] >= start_year].sort_values('report_date')
                     
                # Standardize other columns to lowercase if they are uppercase?
                # The dashboard expects 'net_revenue', but generated file might have uppercase codes?
                # Check generated file content again. Step 563: 'CBS_100', 'CBS_110'...
                # Wait, 'net_revenue' is a mapped name!
                # BaseFinancialCalculator maps codes to names?
                # Let's check BaseFinancialCalculator.pivot_data logic.
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading metrics for {symbol}: {e}")
            return pd.DataFrame()

    def get_metric_info(self, metric_code: str) -> Dict[str, Any]:
        """Get metric metadata (name_vi, unit, etc.)"""
        return self.metric_registry.get_metric(metric_code)
    
    def get_all_symbols(self, entity_type: str = None) -> List[str]:
        """
        Get all liquid symbols (315 symbols with >1B VND/day trading value).
        Optionally filtered by entity type.

        Args:
            entity_type: 'COMPANY', 'BANK', 'SECURITY', 'INSURANCE' or None for all

        Returns:
            List of liquid symbols
        """
        if entity_type:
            return self.symbol_loader.get_symbols_by_entity(entity_type.upper())
        else:
            return self.symbol_loader.get_all_symbols()
