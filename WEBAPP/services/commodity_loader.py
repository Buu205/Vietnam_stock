#!/usr/bin/env python3
"""
Commodity Data Loader for Streamlit
Service để load dữ liệu commodity từ parquet file
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

import pandas as pd
import streamlit as st

from streamlit_app.core.utils import get_data_path

logger = logging.getLogger(__name__)

DEFAULT_COMMODITY_REL_PATH = "calculated_results/commodity/commodity_prices.parquet"


def _resolve_data_path(explicit_path: Optional[str] = None) -> Path:
    """Resolve commodity parquet path using env overrides with project fallback."""
    if explicit_path:
        return Path(explicit_path).expanduser()

    env_override = os.getenv("COMMODITY_DATA_PATH")
    if env_override:
        return Path(env_override).expanduser()

    # Ưu tiên path cụ thể mà user chỉ định
    default_absolute_path = Path("/Users/buuphan/Dev/Vietnam_dashboard/DATA/refined/commodity/commodity_prices.parquet")
    if default_absolute_path.exists():
        return default_absolute_path

    data_dir = os.getenv("DATA_DIR")
    if data_dir:
        # Try calculated_results first, then fallback to old location
        candidate = Path(data_dir).expanduser() / "calculated_results" / "commodity" / "commodity_prices.parquet"
        if candidate.exists():
            return candidate
        # Fallback to old location for backward compatibility
        candidate = Path(data_dir).expanduser() / "data_warehouse" / "raw" / "commodity" / "commodity_prices.parquet"
        if candidate.exists():
            return candidate

    # Try new location first, then fallback to old
    new_path = get_data_path(DEFAULT_COMMODITY_REL_PATH)
    if new_path.exists():
        return new_path
    
    # Fallback to old location for backward compatibility
    old_path = get_data_path("data_warehouse/raw/commodity/commodity_prices.parquet")
    return old_path


@st.cache_data(ttl=300, show_spinner=False)  # Cache 5 phút, dùng latest_date làm key
def _load_commodity_data_cached(file_path: str, latest_date_key: str) -> pd.DataFrame:
    """
    Load commodity data với Streamlit cache.
    Sử dụng latest_date trong data làm cache key để tự động reload khi có data mới.
    
    Args:
        file_path: Đường dẫn đến file parquet
        latest_date_key: Latest date trong data (YYYY-MM-DD) - dùng làm cache key
    
    Returns:
        DataFrame chứa dữ liệu commodity
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Commodity data file not found: {path}")
            return pd.DataFrame()
        
        df = pd.read_parquet(path)
        
        # Đảm bảo date column là datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
        
        logger.info(f"Loaded {len(df)} commodity records from {path}, latest date: {latest_date_key}")
        return df
        
    except Exception as e:
        logger.error(f"Error loading commodity data: {e}")
        return pd.DataFrame()


class CommodityLoader:
    """Loader cho dữ liệu commodity."""
    
    def __init__(self, 
                 data_path: Optional[str] = None):
        """
        Khởi tạo CommodityLoader.
        
        Args:
            data_path: Đường dẫn đến file parquet chứa dữ liệu commodity
        """
        self.data_path = _resolve_data_path(data_path)
    
    def load_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load dữ liệu commodity từ parquet file với Streamlit cache.
        Sử dụng latest_date trong data làm cache key để tự động reload khi có data mới.
        
        Args:
            force_reload: Nếu True, clear cache và reload (chỉ dùng khi debug)
        
        Returns:
            DataFrame chứa dữ liệu commodity
        """
        if force_reload:
            # Clear cache nếu cần force reload
            _load_commodity_data_cached.clear()
        
        if not self.data_path.exists():
            logger.warning(f"Commodity data file not found: {self.data_path}")
            return pd.DataFrame()
        
        # Đọc file để lấy latest_date (file nhỏ ~287KB, load nhanh ~30ms)
        # Dùng latest_date làm cache key - khi có data mới, latest_date thay đổi -> cache invalidate
        try:
            # Load file để lấy latest_date
            df_temp = pd.read_parquet(self.data_path)
            if not df_temp.empty and 'date' in df_temp.columns:
                df_temp['date'] = pd.to_datetime(df_temp['date'])
                latest_date = df_temp['date'].max()
                latest_date_key = latest_date.strftime('%Y-%m-%d')
                logger.info(f"Latest date in commodity data: {latest_date_key}")
            else:
                # Fallback nếu không có date column
                logger.warning(f"No date column found in {self.data_path.name}, using mtime fallback")
                try:
                    latest_date_key = str(self.data_path.stat().st_mtime)
                except Exception:
                    latest_date_key = "unknown"
        except Exception as e:
            logger.warning(f"Error getting latest date from {self.data_path}: {e}")
            try:
                latest_date_key = str(self.data_path.stat().st_mtime)
            except Exception:
                latest_date_key = "unknown"
        
        # Load data với cache, dùng latest_date làm key
        # Streamlit cache sẽ tự động invalidate khi latest_date_key thay đổi
        return _load_commodity_data_cached(str(self.data_path), latest_date_key)
    
    def get_commodity_types(self) -> List[str]:
        """
        Lấy danh sách tất cả các loại commodity.
        
        Returns:
            List các loại commodity
        """
        df = self.load_data()
        if df.empty:
            return []
        return sorted(df['commodity_type'].unique().tolist())
    
    def get_commodity_data(self, 
                          commodity_type: str,
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Lấy dữ liệu cho một loại commodity cụ thể.
        
        Args:
            commodity_type: Loại commodity (ví dụ: 'gold_vn', 'oil_crude')
            start_date: Ngày bắt đầu (YYYY-MM-DD), optional
            end_date: Ngày kết thúc (YYYY-MM-DD), optional
        
        Returns:
            DataFrame chứa dữ liệu commodity đã filter
        """
        df = self.load_data()
        
        if df.empty:
            return pd.DataFrame()
        
        # Filter theo commodity_type
        result = df[df['commodity_type'] == commodity_type].copy()
        
        # Filter theo date range nếu có
        if 'date' in result.columns:
            if start_date:
                result = result[result['date'] >= pd.to_datetime(start_date)]
            if end_date:
                result = result[result['date'] <= pd.to_datetime(end_date)]
        
        # Sort theo date
        if 'date' in result.columns:
            result = result.sort_values('date').reset_index(drop=True)
        
        return result
    
    def get_available_commodities_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin về các commodity có sẵn.
        
        Returns:
            Dict chứa thông tin về các commodity
        """
        df = self.load_data()
        
        if df.empty:
            return {}
        
        info = {}
        for commodity_type in df['commodity_type'].unique():
            commodity_df = df[df['commodity_type'] == commodity_type]
            info[commodity_type] = {
                'count': len(commodity_df),
                'date_range': {
                    'start': commodity_df['date'].min().strftime('%Y-%m-%d') if 'date' in commodity_df.columns else None,
                    'end': commodity_df['date'].max().strftime('%Y-%m-%d') if 'date' in commodity_df.columns else None,
                },
                'columns': [col for col in commodity_df.columns if col not in ['commodity_type', 'date', 'datetime', 'time']]
            }
        
        return info
    
    def get_multiple_commodities(self, 
                                 commodity_types: List[str],
                                 start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Lấy dữ liệu cho nhiều loại commodity.
        
        Args:
            commodity_types: List các loại commodity
            start_date: Ngày bắt đầu (YYYY-MM-DD), optional
            end_date: Ngày kết thúc (YYYY-MM-DD), optional
        
        Returns:
            DataFrame chứa dữ liệu của tất cả commodity types đã filter
        """
        df = self.load_data()
        
        if df.empty:
            return pd.DataFrame()
        
        # Filter theo commodity_types
        result = df[df['commodity_type'].isin(commodity_types)].copy()
        
        # Filter theo date range nếu có
        if 'date' in result.columns:
            if start_date:
                result = result[result['date'] >= pd.to_datetime(start_date)]
            if end_date:
                result = result[result['date'] <= pd.to_datetime(end_date)]
        
        # Sort theo commodity_type và date
        sort_cols = ['commodity_type']
        if 'date' in result.columns:
            sort_cols.append('date')
        result = result.sort_values(sort_cols).reset_index(drop=True)
        
        return result
    
    @staticmethod
    def clear_cache():
        """Clear Streamlit cache cho commodity data."""
        _load_commodity_data_cached.clear()

# Commodity type descriptions for UI
COMMODITY_DESCRIPTIONS = {
    'gold_vn': 'Giá vàng Việt Nam',
    'gold_global': 'Giá vàng thế giới',
    'oil_crude': 'Giá dầu thô',
    'gas_natural': 'Giá khí thiên nhiên',
    'coke': 'Giá than cốc',
    'steel_d10': 'Giá thép thanh HPG (D10)',
    'steel_hrc': 'Giá thép HRC',
    'steel_coated': 'Giá tôn mạ HSG',
    'iron_ore': 'Giá quặng sắt',
    'fertilizer_ure_vn': 'Giá phân bón DPM trong nước',
    'fertilizer_ure_global': 'Giá ure thế giới',
    'soybean': 'Giá đậu tương',
    'corn': 'Giá ngô (bắp)',
    'sugar': 'Giá đường',
    'pork_north_vn': 'Giá heo hơi miền Bắc',
    'pork_china': 'Giá heo hơi Trung Quốc',
    'pvc_china': 'Giá PVC China',
    'fertilizer_ure_global': 'Giá Ure Trung Đông',
    'fertilizer_ure_vn': 'Giá Ure Phú Mỹ',
    'milk_wmp': 'Giá sữa bột nguyên kem (WMP)',
}

