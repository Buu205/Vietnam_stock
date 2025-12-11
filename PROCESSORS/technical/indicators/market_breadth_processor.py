#!/usr/bin/env python3
"""
Market Breadth Processor
========================

Xử lý riêng market breadth indicators với khắc phục lỗi ngày 6/4/2025.

Author: AI Assistant
Date: 2025-10-21
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Dict, Any
import warnings

# Import TA-Lib for optimized technical indicators (REQUIRED)
try:
    import talib
except ImportError:
    raise ImportError(
        "TA-Lib is required for market breadth calculations. "
        "Install with: brew install ta-lib && pip install TA-Lib"
    )

warnings.filterwarnings('ignore')

# Setup logging
logger = logging.getLogger(__name__)

class MarketBreadthProcessor:
    """Xử lý market breadth indicators riêng biệt."""
    
    def __init__(self, data_dir: str = None):
        """
        Khởi tạo Market Breadth Processor
        
        Args:
            data_dir: Đường dẫn đến thư mục dữ liệu (project root). None = tự động tìm
        """
        if data_dir is None:
            # Get project root from current file - find actual project root
            current_file = Path(__file__).resolve()
            # Try to find project root by checking for data_warehouse and calculated_results
            # Also check for streamlit_app to ensure it's the real project root
            # File location: data_processor/technical/technical/technical_indicators/market_breadth_processor.py
            data_dir = None
            for parent in [current_file.parent] + list(current_file.parents):
                # Check for both data_warehouse/calculated_results AND streamlit_app to ensure it's project root
                if (parent / "DATA").exists() and (parent / "DATA/processed").exists() and (parent / "WEBAPP").exists():
                    data_dir = str(parent)
                    break
            
            # Fallback: calculate from current dir (5 levels up: technical_indicators -> technical -> technical -> data_processor -> project_root)
            if data_dir is None:
                data_dir = str(current_file.parent.parent.parent.parent.parent)     
        
        self.data_dir = Path(data_dir)
        self.ohlcv_path = self.data_dir / "DATA/raw/ohlcv/OHLCV_mktcap.parquet"
        # ✅ TẤT CẢ FILE PARQUET LƯU VÀO 1 FOLDER DUY NHẤT
        self.output_dir = self.data_dir / "DATA/processed/technical/market_breadth"
        
        # Tạo thư mục output nếu chưa có
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Đường dẫn các file output
        self.global_breadth_path = self.output_dir / "market_breadth_global.parquet"
        self.sector_breadth_path = self.output_dir / "market_breadth_sector.parquet"
        
        # Load sector mapping từ all_tickers.csv
        tickers_file = self.data_dir / "DATA/raw/metadata/all_tickers.csv"
        try:
            if tickers_file.exists():
                df_tickers = pd.read_csv(tickers_file)
                if 'symbol' in df_tickers.columns and 'sector' in df_tickers.columns:
                    self.sector_mapping = dict(zip(df_tickers['symbol'], df_tickers['sector']))
                    logger.info(f"Loaded {len(self.sector_mapping)} symbols with sector mapping")
                else:
                    logger.warning(f"Sector columns not found in {tickers_file}. Sector statistics will be skipped.")
                    self.sector_mapping = {}
            else:
                logger.warning(f"Sector mapping file not found: {tickers_file}. Sector statistics will be skipped.")
                self.sector_mapping = {}
        except Exception as e:
            logger.warning(f"Could not load sector mapping: {e}. Sector statistics will be skipped.")
            self.sector_mapping = {}
        
        logger.info(f"Market Breadth Processor initialized")
        logger.info(f"Data dir: {self.data_dir}")
        logger.info(f"OHLCV path: {self.ohlcv_path}")
        logger.info(f"Output dir: {self.output_dir}")
    
    def load_ohlcv_data(self) -> pd.DataFrame:
        """Load OHLCV data."""
        try:
            logger.info("Loading OHLCV data...")
            df = pd.read_parquet(self.ohlcv_path)
            
            # Convert date column
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            logger.info(f"Loaded {len(df):,} OHLCV records")
            logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading OHLCV data: {e}")
            raise
    
    # (đã xoá vì dư thừa – không còn xử lý gì cho ngày lỗi cũ)
    
    def load_ma_from_file(self, start_date: date, end_date: date) -> pd.DataFrame:
        """Load MA data từ file moving_averages_full.parquet (nhanh hơn tính lại từ OHLCV).
        
        Args:
            start_date: Ngày bắt đầu
            end_date: Ngày kết thúc
            
        Returns:
            DataFrame với columns: symbol, date, close, ma20, ma50, ma100, ma200
            Nếu file không tồn tại hoặc lỗi, trả về empty DataFrame
        """
        ma_path = self.data_dir / "DATA/processed/technical/moving_averages/moving_averages_full.parquet"
        
        if not ma_path.exists():
            logger.debug(f"MA file not found: {ma_path}, will calculate from OHLCV")
            return pd.DataFrame()
        
        try:
            logger.info(f"Loading MA data from file (faster) for date range: {start_date} to {end_date}")
            
            # Chỉ đọc columns cần thiết (giảm memory và tăng tốc độ)
            # Thử đọc ma200, nếu không có thì chỉ đọc ma20, ma50, ma100
            try:
                df_ma = pd.read_parquet(
                    ma_path,
                    columns=['symbol', 'date', 'close', 'ma20', 'ma50', 'ma100', 'ma200']
                )
            except (KeyError, ValueError):
                # Nếu file chưa có ma200, chỉ đọc các MA cũ
                df_ma = pd.read_parquet(
                    ma_path,
                    columns=['symbol', 'date', 'close', 'ma20', 'ma50', 'ma100']
                )
                df_ma['ma200'] = np.nan  # Thêm column ma200 với giá trị NaN
            
            # Convert date
            df_ma['date'] = pd.to_datetime(df_ma['date']).dt.date
            
            # Filter theo date range
            df_ma = df_ma[
                (df_ma['date'] >= start_date) & 
                (df_ma['date'] <= end_date)
            ].copy()
            
            if df_ma.empty:
                logger.debug(f"No MA data found in file for date range: {start_date} to {end_date}")
                return pd.DataFrame()
            
            logger.info(f"Loaded {len(df_ma):,} MA records from file "
                      f"(date range: {df_ma['date'].min()} to {df_ma['date'].max()})")
            
            return df_ma
            
        except Exception as e:
            logger.warning(f"Error loading MA from file: {e}, will calculate from OHLCV")
            return pd.DataFrame()
    
    def calculate_market_breadth(self, df: pd.DataFrame, use_ma_file: bool = True):
        """Tính market breadth - ưu tiên dùng MA file nếu có (nhanh hơn).
        
        Args:
            df: OHLCV DataFrame với columns: symbol, date, close
            use_ma_file: Nếu True, sẽ thử load MA từ file trước, nếu không có mới tính từ OHLCV
            
        Returns:
            DataFrame với market breadth metrics
        """
        try:
            logger.info("Calculating Market Breadth...")
            
            # Kiểm tra dữ liệu đầu vào
            if df.empty:
                logger.warning("Empty DataFrame provided for market breadth calculation")
                return pd.DataFrame()
            
            # Đảm bảo có đủ dữ liệu
            if len(df) < 20:
                logger.warning(f"Insufficient data for market breadth: {len(df)} rows")
                return pd.DataFrame()
            
            # Chuẩn hóa date
            df = df.copy()
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            # Thử dùng MA file trước (nhanh hơn)
            df_with_ma = None
            use_ma_file_success = False
            
            if use_ma_file:
                start_date = df['date'].min()
                end_date = df['date'].max()
                df_ma_from_file = self.load_ma_from_file(start_date, end_date)
                
                if not df_ma_from_file.empty:
                    # Merge với OHLCV để đảm bảo đúng symbols và dates
                    df_ohlcv = df[['symbol', 'date', 'close']].copy()
                    ma_columns = ['symbol', 'date', 'ma20', 'ma50', 'ma100']
                    if 'ma200' in df_ma_from_file.columns:
                        ma_columns.append('ma200')
                    
                    df_merged = pd.merge(
                        df_ohlcv,
                        df_ma_from_file[ma_columns],
                        on=['symbol', 'date'],
                        how='left'
                    )
                    
                    # Kiểm tra xem có đủ MA data không
                    ma_check_cols = ['ma20', 'ma50', 'ma100']
                    if 'ma200' in df_merged.columns:
                        ma_check_cols.append('ma200')
                    missing_ma = df_merged[df_merged[ma_check_cols].isna().any(axis=1)]
                    missing_ratio = len(missing_ma) / len(df_merged) if len(df_merged) > 0 else 1.0
                    
                    if missing_ratio < 0.2:  # Nếu < 20% thiếu MA, có thể dùng
                        logger.info(f"Using MA data from file (faster) - {len(df_merged):,} records, "
                                  f"missing MA: {len(missing_ma):,} ({missing_ratio:.1%})")
                        df_with_ma = df_merged.sort_values(['symbol', 'date']).reset_index(drop=True)
                        
                        # Fill NaN MA values bằng cách tính từ close với TA-Lib (cho các records thiếu)
                        if len(missing_ma) > 0:
                            logger.debug(f"Filling {len(missing_ma)} missing MA values using TA-Lib")
                            for symbol in missing_ma['symbol'].unique():
                                symbol_data = df_with_ma[df_with_ma['symbol'] == symbol].copy()
                                if len(symbol_data) >= 20:
                                    symbol_data = symbol_data.sort_values('date')
                                    close_values = symbol_data['close'].values.astype(np.float64)
                                    
                                    # Tính lại với TA-Lib nếu thiếu
                                    if symbol_data['ma20'].isna().any():
                                        symbol_data['ma20'] = talib.SMA(close_values, timeperiod=20)
                                    if symbol_data['ma50'].isna().any():
                                        symbol_data['ma50'] = talib.SMA(close_values, timeperiod=50)
                                    if symbol_data['ma100'].isna().any():
                                        symbol_data['ma100'] = talib.SMA(close_values, timeperiod=100)
                                    if 'ma200' in symbol_data.columns and symbol_data['ma200'].isna().any():
                                        symbol_data['ma200'] = talib.SMA(close_values, timeperiod=200)
                                    
                                    update_cols = ['ma20', 'ma50', 'ma100']
                                    if 'ma200' in symbol_data.columns:
                                        update_cols.append('ma200')
                                    df_with_ma.loc[df_with_ma['symbol'] == symbol, update_cols] = \
                                        symbol_data[update_cols].values
                        
                        use_ma_file_success = True
                    else:
                        logger.warning(f"Too many missing MA values ({missing_ratio:.1%}), calculating from OHLCV")
            
            # Nếu không dùng được MA file, tính lại từ OHLCV với TA-Lib (nhanh và chính xác)
            if not use_ma_file_success:
                logger.info("Calculating MA from OHLCV using TA-Lib (optimized)")
                df_with_ma = df.copy()
                df_with_ma = df_with_ma.sort_values(['symbol', 'date']).reset_index(drop=True)
                
                # Tính các đường MA với TA-Lib
                try:
                    ma_results = []
                    for symbol in df_with_ma['symbol'].unique():
                        symbol_data = df_with_ma[df_with_ma['symbol'] == symbol].copy().sort_values('date')
                        close_values = symbol_data['close'].values.astype(np.float64)
                        
                        # TA-Lib SMA - faster and more accurate
                        symbol_data['ma20'] = talib.SMA(close_values, timeperiod=20)
                        symbol_data['ma50'] = talib.SMA(close_values, timeperiod=50)
                        symbol_data['ma100'] = talib.SMA(close_values, timeperiod=100)
                        symbol_data['ma200'] = talib.SMA(close_values, timeperiod=200)
                        
                        ma_results.append(symbol_data)
                    
                    df_with_ma = pd.concat(ma_results, ignore_index=True)
                    
                except Exception as e:
                    logger.error(f"Error calculating moving averages with TA-Lib: {e}")
                    return pd.DataFrame()
            
            # Tính breadth theo ngày (toàn thị trường + theo sector)
            breadth_data = []
            breadth_by_sector_data = []  # Thêm data theo sector
            unique_dates = sorted(df_with_ma['date'].unique())
            
            logger.info(f"Processing {len(unique_dates)} dates for market breadth...")
            
            for i, date_val in enumerate(unique_dates):
                if i % 100 == 0:  # Log progress
                    logger.info(f"Processing date {i+1}/{len(unique_dates)}: {date_val}")
                
                try:
                    date_data = df_with_ma[df_with_ma['date'] == date_val].copy()
                    
                    if date_data.empty:
                        continue
                    
                    # Thêm sector vào date_data
                    date_data['sector'] = date_data['symbol'].map(self.sector_mapping).fillna('Khác')
                    
                    total_stocks = len(date_data)
                    
                    # Tính số cổ phiếu trên các đường MA (toàn thị trường)
                    above_ma20 = len(date_data[date_data['close'] > date_data['ma20']])
                    above_ma50 = len(date_data[date_data['close'] > date_data['ma50']])
                    above_ma100 = len(date_data[date_data['close'] > date_data['ma100']])
                    above_ma200 = len(date_data[date_data['close'] > date_data['ma200']]) if 'ma200' in date_data.columns else 0
                    
                    # Tính ratios (toàn thị trường)
                    ma20_ratio = above_ma20 / total_stocks if total_stocks > 0 else 0
                    ma50_ratio = above_ma50 / total_stocks if total_stocks > 0 else 0
                    ma100_ratio = above_ma100 / total_stocks if total_stocks > 0 else 0
                    ma200_ratio = above_ma200 / total_stocks if total_stocks > 0 else 0
                    
                    # Breadth data toàn thị trường
                    breadth_data.append({
                        'date': date_val,
                        'total_stocks': total_stocks,
                        'above_ma20': above_ma20,
                        'above_ma50': above_ma50,
                        'above_ma100': above_ma100,
                        'above_ma200': above_ma200,
                        'ma20_breadth_ratio': ma20_ratio,      # 0-1 (giữ lại cho compatibility)
                        'ma50_breadth_ratio': ma50_ratio,      # 0-1
                        'ma100_breadth_ratio': ma100_ratio,    # 0-1
                        'ma200_breadth_ratio': ma200_ratio,     # 0-1
                        # ✅ THÊM: Percentage (0-100) - Streamlit chỉ cần đọc
                        'pct_ma20': ma20_ratio * 100,
                        'pct_ma50': ma50_ratio * 100,
                        'pct_ma100': ma100_ratio * 100,
                        'pct_ma200': ma200_ratio * 100,
                    })
                    
                    # Tính breadth theo từng sector
                    if self.sector_mapping:
                        sectors_for_date = date_data['sector'].unique()
                        if i == 0:  # Log chỉ ngày đầu tiên
                            logger.info(f"DEBUG: Processing sectors for date {date_val}: {len(sectors_for_date)} unique sectors")
                        for sector in sectors_for_date:
                            sector_data = date_data[date_data['sector'] == sector]
                            sector_total = len(sector_data)
                            
                            if sector_total == 0:
                                continue
                            
                            # Đếm số cổ phiếu > MA trong sector
                            sector_above_ma20 = len(sector_data[sector_data['close'] > sector_data['ma20']])
                            sector_above_ma50 = len(sector_data[sector_data['close'] > sector_data['ma50']])
                            sector_above_ma100 = len(sector_data[sector_data['close'] > sector_data['ma100']])
                            sector_above_ma200 = len(sector_data[sector_data['close'] > sector_data['ma200']]) if 'ma200' in sector_data.columns else 0
                            
                            # Tính ratios
                            sector_ma20_ratio = sector_above_ma20 / sector_total if sector_total > 0 else 0
                            sector_ma50_ratio = sector_above_ma50 / sector_total if sector_total > 0 else 0
                            sector_ma100_ratio = sector_above_ma100 / sector_total if sector_total > 0 else 0
                            sector_ma200_ratio = sector_above_ma200 / sector_total if sector_total > 0 else 0
                            
                            # Tính strength score (weighted average)
                            # MA20 (ngắn hạn) weight 0.4, MA50 (0.3), MA100 (0.2), MA200 (0.1)
                            strength_score = (
                                sector_ma20_ratio * 0.4 + 
                                sector_ma50_ratio * 0.3 + 
                                sector_ma100_ratio * 0.2 + 
                                sector_ma200_ratio * 0.1
                            )
                            
                            # ✅ Tính trading value cho sector (volume * price)
                            if 'volume' in sector_data.columns and 'close' in sector_data.columns:
                                sector_trading_value = (sector_data['volume'] * sector_data['close']).sum()
                            else:
                                sector_trading_value = 0
                            
                            # Append sector breadth data
                            if i == 0 and sector == sectors_for_date[0]:  # Log chỉ sector đầu tiên của ngày đầu
                                logger.info(f"DEBUG: Appending sector data for {sector} on {date_val}")
                            breadth_by_sector_data.append({
                                'date': date_val,
                                'sector': sector,
                                'total_stocks': sector_total,
                                'above_ma20': sector_above_ma20,
                                'above_ma50': sector_above_ma50,
                                'above_ma100': sector_above_ma100,
                                'above_ma200': sector_above_ma200,
                                'ma20_breadth_ratio': sector_ma20_ratio,
                                'ma50_breadth_ratio': sector_ma50_ratio,
                                'ma100_breadth_ratio': sector_ma100_ratio,
                                'ma200_breadth_ratio': sector_ma200_ratio,
                                # ✅ THÊM: Percentage (0-100)
                                'pct_ma20': sector_ma20_ratio * 100,
                                'pct_ma50': sector_ma50_ratio * 100,
                                'pct_ma100': sector_ma100_ratio * 100,
                                'pct_ma200': sector_ma200_ratio * 100,
                                'strength_score': strength_score,
                                # ✅ THÊM: Trading value
                                'trading_value': sector_trading_value,
                    })
                    
                except Exception as e:
                    logger.warning(f"Error processing date {date_val}: {e}")
                    continue
            
            if not breadth_data:
                logger.warning("No breadth data calculated")
                return pd.DataFrame()
            
            # Tạo DataFrame kết quả toàn thị trường
            result = pd.DataFrame(breadth_data)
            result = result.sort_values('date').reset_index(drop=True)
            
            # Tính moving averages của breadth ratios
            try:
                result['ma20_breadth_ma5'] = result['ma20_breadth_ratio'].rolling(window=5, min_periods=1).mean()
                result['ma20_breadth_ma20'] = result['ma20_breadth_ratio'].rolling(window=20, min_periods=1).mean()
                result['ma50_breadth_ma5'] = result['ma50_breadth_ratio'].rolling(window=5, min_periods=1).mean()
                result['ma50_breadth_ma20'] = result['ma50_breadth_ratio'].rolling(window=20, min_periods=1).mean()
                result['ma100_breadth_ma5'] = result['ma100_breadth_ratio'].rolling(window=5, min_periods=1).mean()
                result['ma100_breadth_ma20'] = result['ma100_breadth_ratio'].rolling(window=20, min_periods=1).mean()
                if 'ma200_breadth_ratio' in result.columns:
                    result['ma200_breadth_ma5'] = result['ma200_breadth_ratio'].rolling(window=5, min_periods=1).mean()
                    result['ma200_breadth_ma20'] = result['ma200_breadth_ratio'].rolling(window=20, min_periods=1).mean()
            except Exception as e:
                logger.warning(f"Error calculating breadth moving averages: {e}")
            
            # Xử lý breadth theo sector
            result_by_sector = pd.DataFrame()  # Khởi tạo empty DataFrame
            if breadth_by_sector_data:
                logger.info(f"✅ Found {len(breadth_by_sector_data)} sector breadth records")
                result_by_sector = pd.DataFrame(breadth_by_sector_data)
                result_by_sector = result_by_sector.sort_values(['sector', 'date']).reset_index(drop=True)
                logger.info(f"✅ Created result_by_sector DataFrame: {len(result_by_sector)} records, {len(result_by_sector.columns)} columns")
                
                # ✅ TÍNH TRADING VALUE PERCENTAGE VÀ CHANGE (backend)
                if 'trading_value' in result_by_sector.columns:
                    logger.info("Calculating trading value metrics for sectors...")
                    # Tính % trading value cho từng ngày
                    for date_val in result_by_sector['date'].unique():
                        date_mask = result_by_sector['date'] == date_val
                        total_tv = result_by_sector.loc[date_mask, 'trading_value'].sum()
                        if total_tv > 0:
                            result_by_sector.loc[date_mask, 'trading_value_pct'] = (
                                result_by_sector.loc[date_mask, 'trading_value'] / total_tv * 100
                            )
                        else:
                            result_by_sector.loc[date_mask, 'trading_value_pct'] = 0
                    
                    # Tính change 5D, 20D cho từng sector
                    for sector in result_by_sector['sector'].unique():
                        sector_mask = result_by_sector['sector'] == sector
                        sector_df = result_by_sector.loc[sector_mask].copy().sort_values('date')
                        
                        sector_df['tv_5d_ago'] = sector_df['trading_value'].shift(5)
                        sector_df['tv_20d_ago'] = sector_df['trading_value'].shift(20)
                        
                        result_by_sector.loc[sector_mask, 'trading_value_change_5d'] = (
                            ((sector_df['trading_value'] / sector_df['tv_5d_ago'] - 1) * 100)
                            .fillna(0)
                        )
                        result_by_sector.loc[sector_mask, 'trading_value_change_20d'] = (
                            ((sector_df['trading_value'] / sector_df['tv_20d_ago'] - 1) * 100)
                            .fillna(0)
                        )
                
                # Tính trend indicators cho từng sector
                logger.info("Calculating trend indicators for sectors...")
                for sector in result_by_sector['sector'].unique():
                    sector_df = result_by_sector[result_by_sector['sector'] == sector].copy()
                    sector_df = sector_df.sort_values('date')
                    
                    # Change vs 5 days ago
                    sector_df['strength_5d_ago'] = sector_df['strength_score'].shift(5)
                    sector_df['trend_5d'] = sector_df['strength_score'] - sector_df['strength_5d_ago']
                    
                    # Change vs 20 days ago
                    sector_df['strength_20d_ago'] = sector_df['strength_score'].shift(20)
                    sector_df['trend_20d'] = sector_df['strength_score'] - sector_df['strength_20d_ago']
                    
                    # Moving averages của strength score
                    sector_df['strength_ma5'] = sector_df['strength_score'].rolling(window=5, min_periods=1).mean()
                    sector_df['strength_ma20'] = sector_df['strength_score'].rolling(window=20, min_periods=1).mean()
                    
                    # Momentum: Tốc độ thay đổi strength
                    sector_df['momentum'] = sector_df['strength_score'].diff()
                    
                    # Acceleration: Tốc độ thay đổi momentum
                    sector_df['acceleration'] = sector_df['momentum'].diff()
                    
                    # Update lại vào result_by_sector
                    update_cols = ['trend_5d', 'trend_20d', 'strength_ma5', 'strength_ma20', 'momentum', 'acceleration']
                    result_by_sector.loc[result_by_sector['sector'] == sector, update_cols] = \
                        sector_df[update_cols].values
                
                # Tính rank và rank change cho từng ngày
                result_by_sector['rank'] = result_by_sector.groupby('date')['strength_score'].rank(
                    ascending=False, method='dense'
                )
                result_by_sector['rank_change'] = result_by_sector.groupby('sector')['rank'].diff()
                
                # Sector rotation signal
                result_by_sector['rotation_signal'] = 'NEUTRAL'
                result_by_sector.loc[
                    (result_by_sector['momentum'] > 0.05) & (result_by_sector['rank_change'] < 0),
                    'rotation_signal'
                ] = 'ROTATION_IN'
                result_by_sector.loc[
                    (result_by_sector['momentum'] < -0.05) & (result_by_sector['rank_change'] > 0),
                    'rotation_signal'
                ] = 'ROTATION_OUT'
            else:
                logger.warning(f"⚠️ No breadth_by_sector_data found (length: {len(breadth_by_sector_data) if breadth_by_sector_data else 0})")
            
            # Tính breadth signals cho global
            try:
                result['breadth_signal'] = 'NEUTRAL'
                result.loc[result['ma20_breadth_ratio'] >= 0.8, 'breadth_signal'] = 'STRONG_BULL'
                result.loc[(result['ma20_breadth_ratio'] >= 0.6) & (result['ma20_breadth_ratio'] < 0.8), 'breadth_signal'] = 'BULL'
                result.loc[(result['ma20_breadth_ratio'] <= 0.2) & (result['ma20_breadth_ratio'] > 0), 'breadth_signal'] = 'BEAR'
                result.loc[result['ma20_breadth_ratio'] <= 0.2, 'breadth_signal'] = 'STRONG_BEAR'
            except Exception as e:
                logger.warning(f"Error calculating breadth signals: {e}")
            
            # ✅ TÁCH THÀNH 2 FILE RIÊNG: Global và Sector
            # Thêm columns cho compatibility
            result['symbol'] = 'MARKET'
            result['ticker'] = 'MARKET'
            
            # Lưu global và sector data riêng biệt
            logger.info(f"Market breadth calculation completed:")
            logger.info(f"  - Global: {len(result)} records")
            if breadth_by_sector_data and not result_by_sector.empty:
                logger.info(f"  - Sector: {len(result_by_sector)} records")
            else:
                logger.info(f"  - Sector: 0 records (no sector data)")
            
            # Return cả 2 để lưu riêng
            return {
                'global': result,
                'sector': result_by_sector if breadth_by_sector_data and not result_by_sector.empty else pd.DataFrame()
            }
            
        except Exception as e:
            logger.error(f"Error calculating market breadth: {e}")
            return pd.DataFrame()
    
    def save_market_breadth_data(self, data) -> None:
        """
        Lưu market breadth data vào 2 file riêng:
        1. market_breadth_global.parquet - Global market breadth (đếm số cổ phiếu >MA)
        2. market_breadth_sector.parquet - Sector breadth analysis + trading_value
        
        Tất cả lưu vào: DATA/processed/technical/market_breadth/
        """
        try:
            # Kiểm tra data type: dict (global + sector) hoặc DataFrame (chỉ global)
            if isinstance(data, dict):
                global_data = data.get('global', pd.DataFrame())
                sector_data = data.get('sector', pd.DataFrame())
            else:
                # Backward compatibility: nếu là DataFrame thì chỉ có global
                global_data = data
                sector_data = pd.DataFrame()
            
            # ✅ LƯU FILE GLOBAL: Đếm số lượng cổ phiếu >MA
            if not global_data.empty:
                global_data = global_data.copy()
                if 'date' in global_data.columns:
                    global_data['date'] = pd.to_datetime(global_data['date']).dt.date
                
                MIN_CALC_DATE = pd.Timestamp('2024-06-01').date()
                global_from_june = global_data[global_data['date'] >= MIN_CALC_DATE].copy()
                
                if not global_from_june.empty:
                    global_from_june = global_from_june.sort_values('date').reset_index(drop=True)
                    global_from_june.to_parquet(self.global_breadth_path, index=False)
                    logger.info(f"✅ Saved global market breadth: {len(global_from_june)} records -> {self.global_breadth_path}")
                    logger.info(f"   Date range: {global_from_june['date'].min()} to {global_from_june['date'].max()}")
                else:
                    logger.warning(f"  No global data from {MIN_CALC_DATE} to save")
            else:
                logger.warning("No global data to save")
            
            # ✅ LƯU FILE SECTOR: Sector breadth analysis + trading_value
            if not sector_data.empty:
                sector_data = sector_data.copy()
                if 'date' in sector_data.columns:
                    sector_data['date'] = pd.to_datetime(sector_data['date']).dt.date
                
                MIN_CALC_DATE = pd.Timestamp('2024-06-01').date()
                sector_from_june = sector_data[sector_data['date'] >= MIN_CALC_DATE].copy()
                
                if not sector_from_june.empty:
                    sector_from_june = sector_from_june.sort_values(['date', 'sector']).reset_index(drop=True)
                    sector_from_june.to_parquet(self.sector_breadth_path, index=False)
                    logger.info(f"✅ Saved sector breadth: {len(sector_from_june)} records -> {self.sector_breadth_path}")
                    logger.info(f"   Date range: {sector_from_june['date'].min()} to {sector_from_june['date'].max()}")
                    logger.info(f"   Unique sectors: {sector_from_june['sector'].nunique()}")
                else:
                    logger.warning(f"  No sector data from {MIN_CALC_DATE} to save")
            else:
                logger.warning("No sector data to save")
            
        except Exception as e:
            logger.error(f"Error saving market breadth data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def process_market_breadth(self) -> None:
        """Xử lý market breadth hoàn chỉnh."""
        try:
            logger.info("Starting market breadth processing...")
            
            # Load dữ liệu
            ohlcv_data = self.load_ohlcv_data()
            
            if ohlcv_data.empty:
                logger.error("No OHLCV data available")
                return
            
            # Tính market breadth (trả về dict với 'global' và 'sector')
            breadth_result = self.calculate_market_breadth(ohlcv_data)
            
            if isinstance(breadth_result, dict):
                if breadth_result.get('global', pd.DataFrame()).empty and breadth_result.get('sector', pd.DataFrame()).empty:
                    logger.error("No market breadth data calculated")
                    return
            elif breadth_result.empty:
                logger.error("No market breadth data calculated")
                return
            
            # Lưu dữ liệu (2 file riêng)
            self.save_market_breadth_data(breadth_result)
            
            logger.info("Market breadth processing completed successfully!")
            
        except Exception as e:
            logger.error(f"Error in market breadth processing: {e}")
            raise
    
    def get_latest_date(self) -> Optional[date]:
        """Lấy ngày mới nhất của market breadth data (từ file global)."""
        try:
            if not self.global_breadth_path.exists():
                return None
            
            df = pd.read_parquet(self.global_breadth_path)
            if df.empty:
                return None
            
            latest_date = pd.to_datetime(df['date']).max().date()
            return latest_date
            
        except Exception as e:
            logger.error(f"Error getting latest date: {e}")
            return None
    
    def update_incremental(self, new_data: pd.DataFrame) -> None:
        """Cập nhật market breadth incremental - append data mới vào file duy nhất.
        
        Để tính MA20/MA50/MA100 chính xác, cần load thêm OHLCV lịch sử (ít nhất 100 ngày)
        trước ngày mới nhất để có đủ dữ liệu tính MA.
        """
        try:
            logger.info("Updating market breadth incrementally...")
            
            # Load dữ liệu hiện tại từ file global & sector (chỉ từ 2025)
            if self.global_breadth_path.exists():
                current_global = pd.read_parquet(self.global_breadth_path)
                current_global['date'] = pd.to_datetime(current_global['date']).dt.date
                # Đảm bảo chỉ giữ data từ 2025-01-01
                current_global = current_global[current_global['date'] >= pd.Timestamp('2025-01-01').date()].copy()
            else:
                current_global = pd.DataFrame()

            if self.sector_breadth_path.exists():
                current_sector = pd.read_parquet(self.sector_breadth_path)
                current_sector['date'] = pd.to_datetime(current_sector['date']).dt.date
                current_sector = current_sector[current_sector['date'] >= pd.Timestamp('2025-01-01').date()].copy()
            else:
                current_sector = pd.DataFrame()
            
            # QUAN TRỌNG: Load thêm OHLCV lịch sử để tính MA đúng
            # Cần ít nhất 100 ngày trước ngày mới nhất để tính MA100
            if new_data.empty:
                logger.warning("No new data provided for incremental update")
                return
            
            # Convert date để xử lý
            new_data = new_data.copy()
            new_data['date'] = pd.to_datetime(new_data['date']).dt.date
            latest_new_date = new_data['date'].max()
            new_dates_set = set(new_data['date'])
            
            # Load OHLCV lịch sử (ít nhất 100 ngày trước ngày mới nhất)
            # Để đảm bảo có đủ dữ liệu tính MA20/MA50/MA100
            history_days = 120  # Load thêm 20 ngày buffer để đảm bảo
            history_start_date = latest_new_date - pd.Timedelta(days=history_days)
            
            logger.info(f"Loading OHLCV history from {history_start_date} to {latest_new_date} for MA calculation...")
            ohlcv_all = self.load_ohlcv_data()
            ohlcv_all['date'] = pd.to_datetime(ohlcv_all['date']).dt.date
            
            # Filter OHLCV từ history_start_date đến latest_new_date
            # Bao gồm cả dữ liệu mới và lịch sử cần thiết để tính MA
            ohlcv_with_history = ohlcv_all[
                (ohlcv_all['date'] >= history_start_date) & 
                (ohlcv_all['date'] <= latest_new_date)
            ].copy()
            
            logger.info(f"Loaded {len(ohlcv_with_history):,} OHLCV records for MA calculation "
                      f"(date range: {ohlcv_with_history['date'].min()} to {ohlcv_with_history['date'].max()})")
            
            # Tính market breadth với dữ liệu đầy đủ (bao gồm lịch sử để tính MA đúng)
            # Sau đó chỉ giữ lại kết quả cho các ngày trong new_data
            new_breadth = self.calculate_market_breadth(ohlcv_with_history)

            # Tách kết quả global / sector (API mới trả về dict)
            if isinstance(new_breadth, dict):
                new_global = new_breadth.get('global', pd.DataFrame())
                new_sector = new_breadth.get('sector', pd.DataFrame())
            else:
                # Backward compatibility: chỉ có global
                new_global = new_breadth
                new_sector = pd.DataFrame()

            if (new_global is None or new_global.empty) and (new_sector is None or new_sector.empty):
                logger.warning("No new market breadth data calculated")
                return

            # Đảm bảo chỉ giữ data từ 2025-01-01 và chỉ các ngày trong new_dates_set
            if new_global is not None and not new_global.empty:
                new_global = new_global.copy()
                new_global['date'] = pd.to_datetime(new_global['date']).dt.date
                new_global = new_global[new_global['date'] >= pd.Timestamp('2025-01-01').date()].copy()
                new_global = new_global[new_global['date'].isin(new_dates_set)].copy()
                logger.info(f"Filtered GLOBAL breadth data to {len(new_global)} records for new dates only")

            if new_sector is not None and not new_sector.empty:
                new_sector = new_sector.copy()
                if 'date' in new_sector.columns:
                    new_sector['date'] = pd.to_datetime(new_sector['date']).dt.date
                    new_sector = new_sector[new_sector['date'] >= pd.Timestamp('2025-01-01').date()].copy()
                    new_sector = new_sector[new_sector['date'].isin(new_dates_set)].copy()
                logger.info(f"Filtered SECTOR breadth data to {len(new_sector)} records for new dates only")

            # Kết hợp dữ liệu GLOBAL (append data mới)
            if new_global is not None and not new_global.empty:
                if not current_global.empty:
                    new_dates_global = set(new_global['date'])
                    current_global = current_global[~current_global['date'].isin(new_dates_global)]
                    updated_global = pd.concat([current_global, new_global], ignore_index=True)
                else:
                    updated_global = new_global

                updated_global = updated_global.sort_values('date').reset_index(drop=True)
            else:
                updated_global = current_global

            # Kết hợp dữ liệu SECTOR (append data mới)
            if new_sector is not None and not new_sector.empty:
                if not current_sector.empty:
                    new_dates_sector = set(new_sector['date'])
                    current_sector = current_sector[~current_sector['date'].isin(new_dates_sector)]
                    updated_sector = pd.concat([current_sector, new_sector], ignore_index=True)
                else:
                    updated_sector = new_sector

                updated_sector = updated_sector.sort_values(['date', 'sector']).reset_index(drop=True)
            else:
                updated_sector = current_sector

            # Lưu lại bằng API chung (dict)
            data_to_save = {
                'global': updated_global if updated_global is not None else pd.DataFrame(),
                'sector': updated_sector if updated_sector is not None else pd.DataFrame(),
            }
            self.save_market_breadth_data(data_to_save)
            
            logger.info("Market breadth incremental update completed!")
            
        except Exception as e:
            logger.error(f"Error in incremental update: {e}")
            raise


def main():
    """Main function để chạy market breadth processor."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Market Breadth Processor')
    parser.add_argument('--mode', choices=['full', 'incremental'], default='full',
                       help='Processing mode')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('market_breadth_processor.log')
        ]
    )
    
    try:
        processor = MarketBreadthProcessor()
        
        if args.mode == 'full':
            processor.process_market_breadth()
        elif args.mode == 'incremental':
            # Load new data since latest date
            latest_date = processor.get_latest_date()
            if latest_date:
                # Load OHLCV data since latest date
                ohlcv_data = processor.load_ohlcv_data()
                new_data = ohlcv_data[ohlcv_data['date'] > latest_date]
                if not new_data.empty:
                    processor.update_incremental(new_data)
                else:
                    logger.info("No new data to process")
            else:
                logger.info("No existing data found, running full processing...")
                processor.process_market_breadth()
        
        print("✅ Market breadth processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
