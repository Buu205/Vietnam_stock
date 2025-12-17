#!/usr/bin/env python3
"""
OHLCV Daily Updater
Cập nhật dữ liệu OHLCV hàng ngày từ vnstock_data (source='vnd') và Fireant API
"""

import pandas as pd
import numpy as np
import requests
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import time
import json
import sys
import os

# Add project and core paths for date formatter
import sys
import os

# Import path configuration
from PROCESSORS.core.config.paths import PROJECT_ROOT, RAW_OHLCV

# Import DateFormatter
from PROCESSORS.core.shared.date_formatter import DateFormatter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ohlcv_daily_updater.log')
    ]
)
logger = logging.getLogger(__name__)

class OHLCVDailyUpdater:
    """Cập nhật dữ liệu OHLCV hàng ngày từ các API."""
    
    def __init__(self, 
                 output_path: str = None,
                 symbols_file: str = None,
                 fireant_token: str = None):
        """
        Khởi tạo OHLCV Daily Updater.
        
        Args:
            output_path: Đường dẫn file parquet để lưu dữ liệu (None = default path từ project root)
            symbols_file: File chứa danh sách mã chứng khoán (None = default path từ project root)
            fireant_token: Token cho Fireant API (nếu không có sẽ dùng token mặc định)
        """
        # Set default paths based on PROJECT_ROOT
        if output_path is None:
            output_path = str(Path(PROJECT_ROOT) / "DATA" / "raw" / "ohlcv" / "OHLCV_mktcap.parquet")
        if symbols_file is None:
            # Use master_symbols.json as primary source
            symbols_file = str(Path(PROJECT_ROOT) / "DATA" / "metadata" / "master_symbols.json")
        
        self.output_path = Path(output_path)
        self.symbols_file = Path(symbols_file)
        self.fireant_token = fireant_token or self._get_default_fireant_token()
        self.date_formatter = DateFormatter()
        
        # Tạo thư mục nếu chưa có
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load danh sách symbols
        self.symbols = self._load_symbols()
        logger.info(f"Loaded {len(self.symbols)} symbols for processing")
    
    def _get_default_fireant_token(self) -> str:
        """Lấy token Fireant mặc định."""
        return "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IkdYdExONzViZlZQakdvNERWdjV4QkRITHpnSSIsImtpZCI6IkdYdExONzViZlZQakdvNERWdjV4QkRITHpnSSJ9.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmZpcmVhbnQudm4iLCJhdWQiOiJodHRwczovL2FjY291bnRzLmZpcmVhbnQudm4vcmVzb3VyY2VzIiwiZXhwIjoyMDU1ODI4OTU5LCJuYmYiOjE3NTU4Mjg5NTksImNsaWVudF9pZCI6ImZpcmVhbnQudHJhZGVzdGF0aW9uIiwic2NvcGUiOlsib3BlbmlkIiwicHJvZmlsZSIsInJvbGVzIiwiZW1haWwiLCJhY2NvdW50cy1yZWFkIiwiYWNjb3VudHMtd3JpdGUiLCJvcmRlcnMtcmVhZCIsIm9yZGVycy13cml0ZSIsImNvbXBhbmllcy1yZWFkIiwiaW5kaXZpZHVhbHMtcmVhZCIsImZpbmFuY2UtcmVhZCIsInBvc3RzLXdyaXRlIiwicG9zdHMtcmVhZCIsInN5bWJvbHMtcmVhZCIsInVzZXItZGF0YS1yZWFkIiwidXNlci1kYXRhLXdyaXRlIiwidXNlcnMtcmVhZCIsInNlYXJjaCIsImFjYWRlbXktcmVhZCIsImFjYWRlbXktd3JpdGUiLCJibG9nLXJlYWQiLCJpbnZlc3RvcGVkaWEtcmVhZCJdLCJzdWIiOiJlMmE1OTFkNC04MmRlLTQ1MmYtYWMyNC0yNGIyZWE3OWZhOTIiLCJhdXRoX3RpbWUiOjE3NTU4Mjg5NTksImlkcCI6Imlkc3J2IiwibmFtZSI6ImJ1dXF1b2NwaGFuQGdtYWlsLmNvbSIsInNlY3VyaXR5X3N0YW1wIjoiYWZkZTBmNGEtMTY0ZS00ZDBmLWI4MjktOWM5MDgwODRhYzFiIiwianRpIjoiZWY1NWVlNmZkZGJkNWFjNmJkOTFjMGIwY2Q0OWVhZDMiLCJhbXIiOlsicGFzc3dvcmQiXX0.iLfhUQ-cVscclfz5loa7ly6svFTJlqVGaIabU4YdX_FmY9xReArIrRquTHMlXSRXvqRxkhRVCtktsWZjLuzS-X3JcepX-HS_pdcIpN779j7l-_6QMDZil1J6GjCvd1Q4vWz8Wc8IMzozKVeAMTdFe6LcFxFECDD4Bd2vlSexmdGke5zYgzJ4FaYm8DCNgcPg20_hbec1_mV592DKMQf2kOzrMIJza4JZEuKrTdL2Cns4negHcE3EYQzIjTEoqeY3yevsC3ieqyIEp2galb6Zb0I4hfjg0_32_JyOLhm0M3HFWu9TzIoGOOIoP608lbDadC28Fw7HDRdd9j6fBkOvKw"
    
    def _load_symbols(self) -> List[str]:
        """Load danh sách symbols từ master_symbols.json hoặc CSV."""
        try:
            if self.symbols_file.exists():
                # Check file extension
                if self.symbols_file.suffix.lower() == '.json':
                    try:
                        with open(self.symbols_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        # Support master_symbols.json format
                        if isinstance(data, dict):
                            if 'all_symbols' in data:
                                # New master_symbols.json format
                                symbols = data['all_symbols']
                                logger.info(f"Loaded master_symbols.json: {len(symbols)} symbols")
                            elif 'tickers' in data:
                                # liquid_tickers.json format
                                symbols = []
                                for entity_tickers in data['tickers'].values():
                                    symbols.extend(entity_tickers)
                            else:
                                # Legacy format: dict keys are symbols
                                symbols = list(data.keys())
                        else:
                            # JSON is a list
                            symbols = data

                        # Clean symbols
                        symbols = [str(s).upper().strip() for s in symbols]
                    except Exception as e:
                        logger.error(f"Error parsing JSON symbols file: {e}")
                        symbols = []
                else:
                    # CSV processing
                    df = pd.read_csv(self.symbols_file)
                    if 'symbol' in df.columns:
                        symbols = df['symbol'].str.upper().str.strip().tolist()
                    elif 'ticker' in df.columns:
                        symbols = df['ticker'].str.upper().str.strip().tolist()
                    else:
                        # Fallback: lấy cột đầu tiên
                        symbols = df.iloc[:, 0].str.upper().str.strip().tolist()
            else:
                # Danh sách symbols mặc định (top 30 liquid)
                symbols = [
                    'VCB', 'ACB', 'TCB', 'BID', 'CTG', 'MBB', 'VPB', 'HDB', 'STB', 'TPB',
                    'VIC', 'VHM', 'VRE', 'VGC', 'VNM', 'MSN', 'HPG', 'POW', 'GAS', 'PLX',
                    'FPT', 'CMG', 'VJC', 'SSI', 'HCM', 'VCI', 'SHS', 'VND', 'CTS', 'BSI'
                ]
                logger.warning(f"Symbols file not found ({self.symbols_file}), using default list: {len(symbols)} symbols")

            # Loại bỏ duplicates và sort
            symbols = sorted(list(set(symbols)))
            return symbols

        except Exception as e:
            logger.error(f"Error loading symbols: {e}")
            return ['VCB', 'ACB', 'TCB', 'BID', 'CTG']  # Fallback minimal list
    
    def get_ohlcv_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Lấy dữ liệu OHLCV từ vnstock_data (source='vnd').
        
        Args:
            symbol: Mã chứng khoán
            start_date: Ngày bắt đầu (YYYY-MM-DD)
            end_date: Ngày kết thúc (YYYY-MM-DD)
        
        Returns:
            DataFrame chứa dữ liệu OHLCV (giá đã chuyển đổi từ nghìn VND sang VND đầy đủ nếu cần)
            hoặc None nếu lỗi
        """
        try:
            # Use vnstock_data with VND source
            from vnstock_data import Quote
            
            quote = Quote(symbol=symbol, source='vnd')
            df = quote.history(start=start_date, end=end_date, interval='1D')
            
            if df.empty:
                logger.warning(f"No OHLCV data found for {symbol}")
                return None
            
            # Chuẩn hóa dữ liệu
            df = df.reset_index(drop=True)
            df['symbol'] = symbol.upper()
            
            # Convert time to date (vnstock_data returns datetime)
            df['date'] = pd.to_datetime(df['time']).dt.date  # Chỉ giữ ngày, không có giờ
            df['datetime'] = pd.to_datetime(df['time'])  # Giữ datetime cho schema
            
            # Chuyển đổi giá từ nghìn VND sang VND đầy đủ
            # vnstock_data từ VND source trả về giá dưới dạng nghìn VND (giống vnstock 3.3.0)
            # Để đảm bảo tương đồng với logic cũ, luôn nhân 1000
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in df.columns:
                    df[col] = df[col] * 1000
            
            logger.debug(f"Converted prices from thousands VND to full VND for {symbol}")
            
            # Chọn các cột cần thiết
            df = df[['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']].copy()
            
            logger.info(f"Retrieved {len(df)} OHLCV records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error getting OHLCV data for {symbol}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def get_shareoutstanding(self, symbol: str) -> Optional[float]:
        """
        Lấy share outstanding từ Fireant API.
        
        Args:
            symbol: Mã chứng khoán
        
        Returns:
            Share outstanding hoặc None nếu lỗi
        """
        try:
            url = f"https://restv2.fireant.vn/symbols/{symbol}/fundamental"
            
            headers = {
                'sec-ch-ua-platform': '"macOS"',
                'Authorization': f'Bearer {self.fireant_token}',
                'Referer': '',
                'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                'sec-ch-ua-mobile': '?0',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'DNT': '1'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Tìm share outstanding trong response
            # API trả về dữ liệu trực tiếp, không có wrapper 'data'
            possible_keys = [
                'sharesOutstanding', 'shares_outstanding', 'outstandingShares',
                'totalShares', 'total_shares', 'shares', 'outstanding'
            ]
            
            for key in possible_keys:
                if key in data and data[key] is not None:
                    shares = float(data[key])
                    logger.info(f"Retrieved share outstanding for {symbol}: {shares:,.0f}")
                    return shares
            
            # Nếu không tìm thấy, log toàn bộ response để debug
            logger.warning(f"Share outstanding not found for {symbol}")
            logger.debug(f"Available keys in response: {list(data.keys())}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting share outstanding for {symbol}: {e}")
            return None
    
    def calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính toán các chỉ số phái sinh.
        
        Args:
            df: DataFrame chứa dữ liệu OHLCV
        
        Returns:
            DataFrame với các chỉ số phái sinh đã được thêm
        """
        try:
            df = df.copy()
            
            # Tính trading value = volume * close
            df['trading_value'] = df['volume'] * df['close']
            
            # Lấy share outstanding cho mỗi symbol
            # Chuẩn hóa: dùng duy nhất cột 'shares_outstanding'
            if 'shares_outstanding' not in df.columns:
                df['shares_outstanding'] = pd.NA
            # Legacy cột 'shareoutstanding' (từ các lần chạy trước)
            if 'shareoutstanding' in df.columns:
                # Tạm thời giữ để fill, sẽ drop sau
                pass
            df['market_cap'] = df.get('market_cap', pd.NA)
            
            for symbol in df['symbol'].unique():
                shares = self.get_shareoutstanding(symbol)
                if shares is not None:
                    mask = df['symbol'] == symbol
                    df.loc[mask, 'shares_outstanding'] = float(shares)
                    # Tính market_cap nếu thiếu
                    if 'close' in df.columns:
                        df.loc[mask, 'market_cap'] = df.loc[mask, 'close'] * float(shares)
                    
                    # Thêm delay để tránh rate limit
                    time.sleep(0.1)
            
            # Hợp nhất cột legacy -> chuẩn
            if 'shareoutstanding' in df.columns:
                # Fill shares_outstanding từ legacy nếu còn thiếu
                legacy_series = pd.to_numeric(df['shareoutstanding'], errors='coerce')
                if 'shares_outstanding' in df.columns:
                    cur_series = pd.to_numeric(df['shares_outstanding'], errors='coerce')
                    df['shares_outstanding'] = cur_series.fillna(legacy_series)
                else:
                    df['shares_outstanding'] = legacy_series
                # Xóa cột legacy
                df = df.drop(columns=['shareoutstanding'])

            # Không fallback từ market_cap/close - chỉ dùng shares_outstanding từ API

            # Tính lại market_cap nếu còn thiếu và có shares_outstanding & close
            if 'market_cap' in df.columns and 'shares_outstanding' in df.columns and 'close' in df.columns:
                mc_series = pd.to_numeric(df['market_cap'], errors='coerce')
                so_series = pd.to_numeric(df['shares_outstanding'], errors='coerce')
                close_series = pd.to_numeric(df['close'], errors='coerce')
                need_mc = mc_series.isna() & so_series.notna() & close_series.notna()
                df.loc[need_mc, 'market_cap'] = (so_series[need_mc] * close_series[need_mc]).astype(float)

            logger.info("Calculated derived metrics successfully")
            return df
            
        except Exception as e:
            logger.error(f"Error calculating derived metrics: {e}")
            return df
    
    def load_existing_data(self) -> pd.DataFrame:
        """Load dữ liệu hiện có từ file parquet."""
        try:
            if self.output_path.exists():
                df = pd.read_parquet(self.output_path)
                logger.info(f"Loaded existing data: {len(df)} records")
                return df
            else:
                logger.info("No existing data found, starting fresh")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading existing data: {e}")
            return pd.DataFrame()
    
    def save_data(self, df: pd.DataFrame) -> None:
        """Lưu dữ liệu vào file parquet."""
        try:
            # Đảm bảo date column là date type
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            # Sort theo symbol và date
            df = df.sort_values(['symbol', 'date']).reset_index(drop=True)
            
            # Lưu file
            df.to_parquet(self.output_path, index=False)
            logger.info(f"Saved {len(df)} records to {self.output_path}")
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise
    
    def update_daily_data(self, target_date: Optional[date] = None) -> None:
        """
        Cập nhật dữ liệu hàng ngày.
        
        Args:
            target_date: Ngày cần cập nhật (mặc định là hôm nay)
        """
        try:
            if target_date is None:
                target_date = date.today()
            
            logger.info(f"Starting daily update for {target_date}")
            
            # Load dữ liệu hiện có
            existing_df = self.load_existing_data()
            
            # Lấy dữ liệu mới cho tất cả symbols
            new_data_list = []
            
            # Kiểm tra ngày gần nhất trong dữ liệu hiện có để tránh trùng lặp
            latest_date_in_existing = None
            if not existing_df.empty and 'date' in existing_df.columns:
                latest_date_in_existing = existing_df['date'].max()
                logger.info(f"Latest date in existing data: {latest_date_in_existing}")
            
            for i, symbol in enumerate(self.symbols, 1):
                logger.info(f"Processing {symbol} ({i}/{len(self.symbols)})")
                
                # Chỉ lấy dữ liệu cho ngày cần cập nhật
                # Nếu đã có dữ liệu cho ngày này, skip symbol này
                if latest_date_in_existing and not existing_df.empty:
                    existing_symbol_date = existing_df[
                        (existing_df['symbol'] == symbol) & 
                        (existing_df['date'] == target_date)
                    ]
                    if not existing_symbol_date.empty:
                        logger.info(f"Skipping {symbol} - data for {target_date} already exists")
                        continue
                
                # Chỉ lấy dữ liệu cho ngày cần cập nhật
                start_date = target_date.strftime('%Y-%m-%d')
                end_date = target_date.strftime('%Y-%m-%d')
                
                ohlcv_data = self.get_ohlcv_data(symbol, start_date, end_date)
                
                if ohlcv_data is not None and not ohlcv_data.empty:
                    # Chỉ giữ dữ liệu cho ngày cần cập nhật
                    ohlcv_data = ohlcv_data[ohlcv_data['date'] == target_date]
                    if not ohlcv_data.empty:
                        new_data_list.append(ohlcv_data)
                
                # Delay nhỏ để tránh quá tải
                time.sleep(0.1)
            
            if not new_data_list:
                logger.warning("No new data retrieved")
                return
            
            # Combine tất cả dữ liệu mới
            new_df = pd.concat(new_data_list, ignore_index=True)
            
            # Tính toán các chỉ số phái sinh
            new_df = self.calculate_derived_metrics(new_df)
            
            # Merge với dữ liệu hiện có
            if not existing_df.empty:
                # Loại bỏ dữ liệu trùng lặp chỉ cho ngày đang cập nhật
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                combined_df = combined_df.drop_duplicates(subset=['symbol', 'date'], keep='last')
            else:
                combined_df = new_df
            
            # Lưu dữ liệu
            self.save_data(combined_df)
            
            logger.info(f"Daily update completed successfully for {target_date}")
            
        except Exception as e:
            logger.error(f"Error in daily update: {e}")
            raise
    
    def update_specific_date(self, target_date: date) -> None:
        """Cập nhật dữ liệu cho một ngày cụ thể."""
        self.update_daily_data(target_date)
    
    def update_date_range(self, start_date: date, end_date: date) -> None:
        """Cập nhật dữ liệu cho một khoảng thời gian."""
        current_date = start_date
        while current_date <= end_date:
            try:
                logger.info(f"Updating data for {current_date}")
                self.update_daily_data(current_date)
                current_date += timedelta(days=1)
                time.sleep(1)  # Delay giữa các ngày
            except Exception as e:
                logger.error(f"Error updating {current_date}: {e}")
                current_date += timedelta(days=1)
                continue

def main():
    """Main function để chạy updater."""
    import argparse
    
    parser = argparse.ArgumentParser(description='OHLCV Daily Updater')
    parser.add_argument('--date', type=str, help='Target date (YYYY-MM-DD), default is today')
    parser.add_argument('--start-date', type=str, help='Start date for range update (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date for range update (YYYY-MM-DD)')
    # Default paths based on PROJECT_ROOT
    default_output_path = str(RAW_OHLCV / "OHLCV_mktcap.parquet")
    default_symbols_path = str(PROJECT_ROOT / "DATA" / "raw" / "metadata" / "all_tickers.csv")
    
    parser.add_argument('--output-path', type=str, 
                       default=default_output_path,
                       help='Output parquet file path')
    parser.add_argument('--symbols-file', type=str,
                       default=default_symbols_path,
                       help='Symbols CSV file path')
    
    args = parser.parse_args()
    
    # Khởi tạo updater
    updater = OHLCVDailyUpdater(
        output_path=args.output_path,
        symbols_file=args.symbols_file
    )
    
    try:
        if args.start_date and args.end_date:
            # Update range
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
            updater.update_date_range(start_date, end_date)
        elif args.date:
            # Update specific date
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
            updater.update_specific_date(target_date)
        else:
            # Update today
            updater.update_daily_data()
        
        logger.info("Update process completed successfully!")
        
    except Exception as e:
        logger.error(f"Update process failed: {e}")
        raise

if __name__ == "__main__":
    main()
