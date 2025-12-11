"""
Valuation domain data loading (bilingual / song ngữ)
Updated: 2025-12-10 - Using centralized DataPaths configuration
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path
from WEBAPP.core.data_paths import DataPaths

# Use centralized DataPaths configuration
PE_FUND_PATH = str(DataPaths.valuation('pe'))
PB_FUND_PATH = str(DataPaths.valuation('pb'))
EV_EBITDA_FUND_PATH = str(DataPaths.valuation('ev_ebitda'))
SECTOR_PE_PATH = str(DataPaths.valuation('sector_pe'))
VNINDEX_PE_PATH = str(DataPaths.valuation('vnindex_pe'))

def get_valuation_symbols() -> List[str]:
    """Get list of symbols from valuation metrics files"""
    try:
        # Load PE data to get symbols
        pe_df = pd.read_parquet(PE_FUND_PATH)
        symbols = pe_df['symbol'].unique().tolist()
        return sorted(symbols)
    except Exception as e:
        print(f"Lỗi khi tải symbols từ PE data: {e}")
        return []

def load_pe_data(symbol: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Load PE ratio data
    
    Args:
        symbol: Specific symbol to load (None = all symbols)
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
    
    Returns:
        DataFrame with PE data
    """
    try:
        df = pd.read_parquet(PE_FUND_PATH)
        
        # Filter by symbol if specified
        if symbol:
            df = df[df['symbol'] == symbol]
        
        # Filter by date range if specified
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]
            
        return df
    except Exception as e:
        print(f"Lỗi khi tải PE data: {e}")
        return pd.DataFrame()

def load_pb_data(symbol: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Load P/B ratio data
    
    Args:
        symbol: Specific symbol to load (None = all symbols)
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
    
    Returns:
        DataFrame with P/B data
    """
    try:
        df = pd.read_parquet(PB_FUND_PATH)
        
        # Filter by symbol if specified
        if symbol:
            df = df[df['symbol'] == symbol]
        
        # Filter by date range if specified
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]
            
        return df
    except Exception as e:
        print(f"Lỗi khi tải P/B data: {e}")
        return pd.DataFrame()

def load_ev_ebitda_data(symbol: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Load EV/EBITDA data
    
    Args:
        symbol: Specific symbol to load (None = all symbols)
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
    
    Returns:
        DataFrame with EV/EBITDA data
    """
    try:
        df = pd.read_parquet(EV_EBITDA_FUND_PATH)
        
        # Filter by symbol if specified
        if symbol:
            df = df[df['symbol'] == symbol]
        
        # Filter by date range if specified
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]
            
        return df
    except Exception as e:
        print(f"Lỗi khi tải EV/EBITDA data: {e}")
        return pd.DataFrame()

def load_sector_pe_data(start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Load sector PE data
    
    Args:
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
    
    Returns:
        DataFrame with sector PE data
    """
    try:
        df = pd.read_parquet(SECTOR_PE_PATH)
        
        # Filter by date range if specified
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]
            
        return df
    except Exception as e:
        print(f"Lỗi khi tải sector PE data: {e}")
        return pd.DataFrame()

def load_vnindex_pe_data(start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Load VN-Index PE data
    
    Args:
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
    
    Returns:
        DataFrame with VN-Index PE data
    """
    try:
        df = pd.read_parquet(VNINDEX_PE_PATH)
        
        # Filter by date range if specified
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]
            
        return df
    except Exception as e:
        print(f"Lỗi khi tải VN-Index PE data: {e}")
        return pd.DataFrame()

def get_latest_valuation_date() -> Optional[datetime]:
    """
    Lấy ngày cập nhật mới nhất của dữ liệu valuation
    
    Returns:
        Latest date from valuation data or None if no data available
    """
    try:
        # Try PE data first
        pe_df = pd.read_parquet(PE_FUND_PATH)
        if not pe_df.empty and 'date' in pe_df.columns:
            latest_date = pe_df['date'].max()
            if pd.isna(latest_date):
                return None
            return pd.to_datetime(latest_date)
    except Exception as e:
        print(f"Lỗi khi lấy latest valuation date từ PE: {e}")
    
    try:
        # Fallback to PB data
        pb_df = pd.read_parquet(PB_FUND_PATH)
        if not pb_df.empty and 'date' in pb_df.columns:
            latest_date = pb_df['date'].max()
            if pd.isna(latest_date):
                return None
            return pd.to_datetime(latest_date)
    except Exception as e:
        print(f"Lỗi khi lấy latest valuation date từ PB: {e}")
    
    return None

def get_latest_valuation_summary(symbol: str) -> Dict:
    """
    Get latest valuation summary for a specific symbol
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Dictionary with latest valuation metrics
    """
    try:
        # Get latest PE
        pe_df = load_pe_data(symbol)
        if not pe_df.empty:
            latest_pe = pe_df.iloc[-1]
            pe_value = latest_pe.get('pe_ratio', None)
            pe_date = latest_pe.get('date', None)
        else:
            pe_value = None
            pe_date = None
            
        # Get latest P/B
        pb_df = load_pb_data(symbol)
        if not pb_df.empty:
            latest_pb = pb_df.iloc[-1]
            pb_value = latest_pb.get('pb_ratio', None)
            pb_date = latest_pb.get('date', None)
        else:
            pb_value = None
            pb_date = None
            
        # Get latest EV/EBITDA
        ev_ebitda_df = load_ev_ebitda_data(symbol)
        if not ev_ebitda_df.empty:
            latest_ev_ebitda = ev_ebitda_df.iloc[-1]
            ev_ebitda_value = latest_ev_ebitda.get('ev_ebitda', None)
            ev_ebitda_date = latest_ev_ebitda.get('date', None)
        else:
            ev_ebitda_value = None
            ev_ebitda_date = None
            
        return {
            'symbol': symbol,
            'pe_ratio': pe_value,
            'pe_date': pe_date,
            'pb_ratio': pb_value,
            'pb_date': pb_date,
            'ev_ebitda': ev_ebitda_value,
            'ev_ebitda_date': ev_ebitda_date
        }
        
    except Exception as e:
        print(f"Lỗi khi lấy valuation summary cho {symbol}: {e}")
        return {
            'symbol': symbol,
            'pe_ratio': None,
            'pe_date': None,
            'pb_ratio': None,
            'pb_date': None,
            'ev_ebitda': None,
            'ev_ebitda_date': None
        }

def get_latest_valuation_date() -> Optional[datetime]:
    """
    Lấy ngày cập nhật mới nhất của dữ liệu valuation
    
    Returns:
        Latest date from valuation data or None if no data available
    """
    try:
        # Try PE data first
        pe_df = pd.read_parquet(PE_FUND_PATH)
        if not pe_df.empty and 'date' in pe_df.columns:
            latest_date = pe_df['date'].max()
            if pd.isna(latest_date):
                return None
            return pd.to_datetime(latest_date)
    except Exception as e:
        print(f"Lỗi khi lấy latest valuation date từ PE: {e}")
    
    try:
        # Fallback to PB data
        pb_df = pd.read_parquet(PB_FUND_PATH)
        if not pb_df.empty and 'date' in pb_df.columns:
            latest_date = pb_df['date'].max()
            if pd.isna(latest_date):
                return None
            return pd.to_datetime(latest_date)
    except Exception as e:
        print(f"Lỗi khi lấy latest valuation date từ PB: {e}")
    
    return None