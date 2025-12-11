"""
Daily Technical Indicators Updater
Cập nhật hàng ngày các chỉ số kỹ thuật từ dữ liệu OHLCV mới nhất.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, date, timedelta
import argparse
import sys

# Add current directory to path để import technical_processor
from technical_processor import TechnicalProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DailyTechnicalUpdater:
    """Cập nhật hàng ngày các technical indicators."""
    
    def __init__(self, 
                 ohlcv_path: str = None,
                 output_dir: str = None,
                 backup_dir: str = None):
        """
        Khởi tạo DailyTechnicalUpdater.
        
        Args:
            ohlcv_path: Đường dẫn đến file OHLCV parquet
            output_dir: Thư mục lưu kết quả
            backup_dir: Thư mục backup dữ liệu cũ
        """
        project_root = Path(__file__).resolve().parents[4]
        self.ohlcv_path = ohlcv_path or str(project_root / "DATA/raw/ohlcv/OHLCV_mktcap.parquet")
        self.output_dir = Path(output_dir) if output_dir else project_root / "DATA/processed/technical"
        self.backup_dir = Path(backup_dir) if backup_dir else project_root / "DATA/processed/technical/backup"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Khởi tạo processor
        self.processor = TechnicalProcessor(self.ohlcv_path, str(self.output_dir))
        
        # Danh sách indicators cần cập nhật
        self.indicators = [
            'basic_data', 'moving_averages', 'exponential_moving_averages', 
            'rsi', 'macd', 'bollinger_bands', 'volatility', 'signals',
            'trading_values', 'sector_trading', 'market_breadth'
        ]
    
    def get_latest_date(self, indicator_name: str) -> Optional[date]:
        """Lấy ngày mới nhất trong dữ liệu indicator hiện tại."""
        try:
            file_path = self.output_dir / indicator_name / f"{indicator_name}_full.parquet"
            if not file_path.exists():
                return None
            
            df = pd.read_parquet(file_path)
            if df.empty:
                return None
            
            # Đảm bảo cột date là date object
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.date
            
            latest_date = df['date'].max()
            
            # Đảm bảo trả về date object
            if isinstance(latest_date, date):
                return latest_date
            else:
                return pd.to_datetime(latest_date).date()
            
        except Exception as e:
            logger.warning(f"Could not get latest date for {indicator_name}: {e}")
            return None
    
    def get_new_data_since(self, target_date: date = None, full_data: bool = False) -> pd.DataFrame:
        """Lấy dữ liệu OHLCV mới từ target_date hoặc toàn bộ dữ liệu."""
        try:
            if full_data:
                logger.info("Loading all OHLCV data")
            else:
                logger.info(f"Loading OHLCV data since {target_date}")
            
            df = pd.read_parquet(self.ohlcv_path)
            
            # Chuẩn hóa dữ liệu - đảm bảo date chỉ là date object
            df['date'] = pd.to_datetime(df['date']).dt.date  # Chỉ giữ ngày tháng năm
            df['symbol'] = df['symbol'].str.upper().str.strip()
            
            # Hiển thị thông tin về dữ liệu có sẵn
            available_dates = sorted(df['date'].unique())
            logger.info(f"Available data range: {available_dates[0]} to {available_dates[-1]}")
            
            if not full_data and target_date is not None:
                # Lọc dữ liệu mới - so sánh date với date (đảm bảo cùng kiểu)
                if isinstance(target_date, date):
                    new_data = df[df['date'] > target_date].copy()
                else:
                    # Chuyển đổi target_date thành date object nếu cần
                    target_date_obj = pd.to_datetime(target_date).date() if target_date else None
                    new_data = df[df['date'] > target_date_obj].copy()
                
                if new_data.empty:
                    logger.info(f"No new data found after {target_date}")
                    logger.info(f"Latest available data: {available_dates[-1]}")
                    return pd.DataFrame()
            else:
                # Lấy toàn bộ dữ liệu
                new_data = df.copy()
            
            # Sắp xếp theo symbol và date
            new_data = new_data.sort_values(['symbol', 'date']).reset_index(drop=True)
            
            logger.info(f"Found {len(new_data)} records for {new_data['symbol'].nunique()} symbols")
            return new_data
            
        except Exception as e:
            logger.error(f"Error loading OHLCV data: {e}")
            raise
    
    def backup_existing_data(self, indicator_name: str) -> None:
        """Backup dữ liệu hiện tại trước khi cập nhật."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for file_type in ['full', 'summary']:
                source_file = self.output_dir / indicator_name / f"{indicator_name}_{file_type}.parquet"
                if source_file.exists():
                    backup_file = self.backup_dir / f"{indicator_name}_{file_type}_{timestamp}.parquet"
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    import shutil
                    shutil.copy2(source_file, backup_file)
                    logger.info(f"Backed up {source_file} to {backup_file}")
                    
        except Exception as e:
            logger.warning(f"Could not backup {indicator_name}: {e}")
    
    def update_indicator_incremental(self, indicator_name: str, new_data: pd.DataFrame) -> None:
        """Cập nhật indicator theo cách incremental (chỉ tính cho dữ liệu mới)."""
        try:
            logger.info(f"Updating {indicator_name} incrementally...")
            
            # Backup dữ liệu cũ
            self.backup_existing_data(indicator_name)
            
            # Load dữ liệu hiện tại
            current_file = self.output_dir / indicator_name / f"{indicator_name}_full.parquet"
            if current_file.exists():
                current_data = pd.read_parquet(current_file)
            else:
                current_data = pd.DataFrame()
            
            # Xác định nhu cầu lookback để tính đúng các chỉ báo dựa trên MA/EMA
            indicators_require_lookback = {
                'moving_averages': 220,
                'exponential_moving_averages': 220,
                'bollinger_bands': 50,
                'macd': 50,
                'rsi': 14,
            }

            use_lookback_days = indicators_require_lookback.get(indicator_name, 0)

            # Nếu cần lookback, nạp thêm dữ liệu cửa sổ trước ngày cuối cùng của new_data
            effective_data = new_data
            if use_lookback_days > 0 and not new_data.empty:
                try:
                    end_date = pd.to_datetime(new_data['date']).max()
                    start_date = (pd.to_datetime(end_date) - pd.Timedelta(days=use_lookback_days)).date()
                    all_df = pd.read_parquet(self.ohlcv_path)
                    all_df['date'] = pd.to_datetime(all_df['date']).dt.date
                    # Chỉ lấy các symbol liên quan để giảm dữ liệu
                    symbols_to_update = new_data['symbol'].unique().tolist()
                    window_df = all_df[(all_df['date'] >= start_date) & (all_df['symbol'].isin(symbols_to_update))].copy()
                    window_df = window_df.sort_values(['symbol', 'date']).reset_index(drop=True)
                    if not window_df.empty:
                        effective_data = window_df
                        logger.info(f"Using lookback window {use_lookback_days}d for {indicator_name}: {start_date} → {end_date.date()} ({len(window_df)} rows)")
                except Exception as e:
                    logger.warning(f"Failed to load lookback window for {indicator_name}, fallback to new_data only: {e}")

            # Tính toán cho dữ liệu (dùng effective_data đã có lookback nếu cần)
            if indicator_name == 'basic_data':
                new_indicator_data = self.processor.calculate_basic_data(effective_data)
            elif indicator_name == 'moving_averages':
                new_indicator_data = self.processor.calculate_moving_averages(effective_data)
            elif indicator_name == 'exponential_moving_averages':
                new_indicator_data = self.processor.calculate_exponential_moving_averages(effective_data)
            elif indicator_name == 'rsi':
                new_indicator_data = self.processor.calculate_rsi(effective_data)
            elif indicator_name == 'macd':
                new_indicator_data = self.processor.calculate_macd(effective_data)
            elif indicator_name == 'bollinger_bands':
                new_indicator_data = self.processor.calculate_bollinger_bands(effective_data)
            elif indicator_name == 'volatility':
                new_indicator_data = self.processor.calculate_volatility(effective_data)
            elif indicator_name == 'trading_values':
                new_indicator_data = self.processor.calculate_trading_values(effective_data)
            elif indicator_name == 'signals':
                new_indicator_data = self.processor.calculate_signals(effective_data)
            elif indicator_name == 'sector_trading':
                new_indicator_data = self.processor.calculate_sector_trading(effective_data)
            elif indicator_name == 'market_breadth':
                new_indicator_data = self.processor.calculate_market_breadth(effective_data)
            else:
                logger.warning(f"Unknown indicator: {indicator_name}")
                return
            
            # Merge với dữ liệu cũ
            if not current_data.empty:
                # Loại bỏ dữ liệu cũ cho các symbol có trong new_data
                symbols_to_update = new_indicator_data['symbol'].unique()
                current_data = current_data[~current_data['symbol'].isin(symbols_to_update)]
                
                # Kết hợp dữ liệu
                updated_data = pd.concat([current_data, new_indicator_data], ignore_index=True)
            else:
                updated_data = new_indicator_data
            
            # Sắp xếp lại
            updated_data = updated_data.sort_values(['symbol', 'date']).reset_index(drop=True)
            
            # Lưu dữ liệu
            self.processor.save_indicator_data(updated_data, indicator_name)
            
            logger.info(f"Successfully updated {indicator_name}")
            
        except Exception as e:
            logger.error(f"Error updating {indicator_name}: {e}")
            raise
    
    def update_all_indicators(self, target_date: Optional[date] = None) -> None:
        """Cập nhật tất cả indicators."""
        try:
            if target_date is None:
                # Tìm ngày mới nhất trong tất cả indicators
                latest_dates = []
                for indicator in self.indicators:
                    latest_date = self.get_latest_date(indicator)
                    if latest_date:
                        latest_dates.append(latest_date)
                
                if not latest_dates:
                    logger.info("No existing data found, running full processing...")
                    self.processor.process_all_indicators()
                    return
                
                target_date = max(latest_dates)
                logger.info(f"Latest data date: {target_date}")
            
            # Lấy dữ liệu mới
            new_data = self.get_new_data_since(target_date)
            if new_data.empty:
                logger.info("No new data to process")
                return
            
            # Cập nhật từng indicator
            for indicator in self.indicators:
                try:
                    self.update_indicator_incremental(indicator, new_data)
                except Exception as e:
                    logger.error(f"Failed to update {indicator}: {e}")
                    continue
            
            # Cập nhật file tổng hợp
            self.update_combined_file()
            
            logger.info("Daily update completed successfully!")
            
        except Exception as e:
            logger.error(f"Error in daily update: {e}")
            raise
    
    def update_combined_file(self) -> None:
        """Cập nhật file tổng hợp technical indicators."""
        try:
            logger.info("Updating combined technical indicators file...")
            
            # Load OHLCV data
            ohlcv_data = self.processor.load_ohlcv_data()
            
            # Tạo file tổng hợp mới
            self.processor.create_combined_technical_file(ohlcv_data)
            
            logger.info("Combined file updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating combined file: {e}")
    
    def run_full_reprocess(self) -> None:
        """Chạy lại toàn bộ quá trình xử lý (khi cần thiết)."""
        logger.info("Running full reprocessing...")
        self.processor.process_all_indicators()
        logger.info("Full reprocessing completed!")
    
    def cleanup_old_backups(self, days_to_keep: int = 30) -> None:
        """Dọn dẹp các file backup cũ."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for backup_file in self.backup_dir.rglob("*.parquet"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    logger.info(f"Removed old backup: {backup_file}")
            
            logger.info("Backup cleanup completed")
            
        except Exception as e:
            logger.warning(f"Error during backup cleanup: {e}")


def main():
    """Main function để chạy daily updater."""
    parser = argparse.ArgumentParser(description='Daily Technical Indicators Updater')
    parser.add_argument('--mode', choices=['incremental', 'full'], default='incremental',
                       help='Update mode: incremental (default) or full reprocess')
    parser.add_argument('--target-date', type=str, default=None,
                       help='Target date to update from (YYYY-MM-DD format)')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up old backup files')
    
    args = parser.parse_args()
    
    # Khởi tạo updater
    updater = DailyTechnicalUpdater()
    
    try:
        if args.mode == 'full':
            updater.run_full_reprocess()
        else:
            # Incremental update
            target_date = None
            if args.target_date:
                target_date = pd.to_datetime(args.target_date).date()
            
            updater.update_all_indicators(target_date)
        
        if args.cleanup:
            updater.cleanup_old_backups()
        
        logger.info("Daily update process completed successfully!")
        
    except Exception as e:
        logger.error(f"Daily update failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
