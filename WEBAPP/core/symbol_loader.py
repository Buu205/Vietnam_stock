"""
Symbol Loader - Centralized symbol loading for WEBAPP
======================================================

Tải danh sách symbols từ metadata và fundamental data.
Hỗ trợ tải symbols theo sector và lấy thông tin symbol.

Author: AI Assistant
Date: 2025-12-10
"""

from __future__ import annotations
from typing import List, Dict, Optional
import pandas as pd
from pathlib import Path

def get_all_symbols() -> List[str]:
    """
    Lấy danh sách tất cả symbols có sẵn từ metadata
    
    Returns:
        List[str]: Danh sách tất cả symbols
    """
    try:
        # Try to load from all_tickers.json
        metadata_path = Path(__file__).parent.parent.parent / "DATA" / "metadata" / "all_tickers.json"
        if metadata_path.exists():
            import json
            with open(metadata_path, 'r') as f:
                data = json.load(f)
                return list(data.keys())
        
        # Fallback to fundamental data
        fundamental_path = Path(__file__).parent.parent.parent / "DATA" / "processed" / "fundamental"
        if fundamental_path.exists():
            company_df = pd.read_parquet(fundamental_path / "company_full.parquet")
            bank_df = pd.read_parquet(fundamental_path / "bank_full.parquet")
            
            symbols = set()
            if 'symbol' in company_df.columns:
                symbols.update(company_df['symbol'].unique().tolist())
            if 'symbol' in bank_df.columns:
                symbols.update(bank_df['symbol'].unique().tolist())
            
            return sorted(list(symbols))
        
        return []
        
    except Exception as e:
        print(f"Lỗi khi tải symbols: {e}")
        return []

def get_symbols_by_sector(sector: str) -> List[str]:
    """
    Lấy danh sách symbols theo sector
    
    Args:
        sector: Tên sector
        
    Returns:
        List[str]: Danh sách symbols trong sector đó
    """
    try:
        # Load sector mappings
        metadata_path = Path(__file__).parent.parent.parent / "config" / "metadata_registry" / "tickers" / "sector_mappings.json"
        if metadata_path.exists():
            import json
            with open(metadata_path, 'r') as f:
                mappings = json.load(f)
                return mappings.get(sector, [])
        
        return []
        
    except Exception as e:
        print(f"Lỗi khi tải sector mappings: {e}")
        return []

def get_symbol_info(symbol: str) -> Dict:
    """
    Lấy thông tin cơ bản về một symbol
    
    Args:
        symbol: Mã cổ phiếu
        
    Returns:
        Dict: Dictionary chứa thông tin symbol (symbol, exchange, sector)
    """
    try:
        # Load ticker mappings
        metadata_path = Path(__file__).parent.parent.parent / "config" / "metadata_registry" / "tickers" / "exchange_mappings.json"
        if metadata_path.exists():
            import json
            with open(metadata_path, 'r') as f:
                mappings = json.load(f)
                return mappings.get(symbol, {
                    'symbol': symbol,
                    'exchange': 'HOSE',
                    'sector': 'Unknown'
                })
        
        return {
            'symbol': symbol,
            'exchange': 'HOSE',
            'sector': 'Unknown'
        }
        
    except Exception as e:
        print(f"Lỗi khi tải symbol info cho {symbol}: {e}")
        return {
            'symbol': symbol,
            'exchange': 'HOSE',
            'sector': 'Unknown'
        }