#!/usr/bin/env python3
"""
BSC Forecast Auto Update System
===============================

Quy trình tự động hóa hoàn chỉnh để cập nhật dữ liệu BSC Forecast:
1. Đọc file Excel BSC mới nhất
2. Xử lý và chuẩn hóa dữ liệu  
3. Tạo file CSV chuẩn cho Streamlit
4. Backup và validation
5. Thông báo kết quả

Usage:
    python3 run_bsc_auto_update.py [--source SOURCE_FILE] [--force]

Author: AI Assistant
Date: 2025-10-08
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import logging
import argparse
import json
from typing import Dict, List, Optional, Tuple

# Find project root (stock_dashboard directory)
def find_project_root() -> Path:
    """Tìm project root bằng cách tìm thư mục chứa stock_dashboard"""
    current = Path(__file__).resolve()
    while current.parent != current:
        if current.name == 'stock_dashboard':
            return current
        current = current.parent
    # Fallback: giả sử script chạy từ project root
    return Path(__file__).resolve().parent.parent.parent

PROJECT_ROOT = find_project_root()

# Setup logging với absolute path
log_dir = PROJECT_ROOT / 'calculated_results' / 'forecast' / 'bsc'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / 'processing_log.txt'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(log_file), mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BSCAutoProcessor:
    """
    BSC Forecast Auto Processing System
    Tự động hóa quy trình cập nhật dữ liệu BSC
    """
    
    def __init__(self, config_path: str = "data_processor/forecast/bsc_config.json"):
        """
        Initialize BSC Auto Processor
        
        Args:
            config_path: Đường dẫn đến file cấu hình
        """
        # Find project root
        self.project_root = find_project_root()
        
        # Resolve config path relative to project root
        if not os.path.isabs(config_path):
            self.config_path = self.project_root / config_path
        else:
            self.config_path = Path(config_path)
        
        self.config = self.load_config()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.date_str = datetime.now().strftime("%Y%m%d")
        
        # Đường dẫn các file (resolve relative to project root)
        input_file_rel = self.config['input']['excel_file']
        if not os.path.isabs(input_file_rel):
            self.input_file = self.project_root / input_file_rel
        else:
            self.input_file = Path(input_file_rel)
        
        output_dir_rel = self.config['output']['csv_dir']
        if not os.path.isabs(output_dir_rel):
            self.output_dir = self.project_root / output_dir_rel
        else:
            self.output_dir = Path(output_dir_rel)
        
        backup_dir_rel = self.config['output']['backup_dir']
        if not os.path.isabs(backup_dir_rel):
            self.backup_dir = self.project_root / backup_dir_rel
        else:
            self.backup_dir = Path(backup_dir_rel)
        
        # Tạo thư mục nếu chưa tồn tại
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # File output chính
        self.latest_csv = self.output_dir / "bsc_forecast_latest.csv"
        self.backup_csv = self.backup_dir / f"bsc_forecast_{self.date_str}.csv"
        
    def load_config(self) -> Dict:
        """Load cấu hình từ file JSON"""
        default_config = {
            "input": {
                "excel_file": "data_processor/Bsc_forecast/BSC Master File Equity Pro.xlsm",
                "sheet_name": "Codedata",
                "fallback_file": "data_processor/Bsc_forecast/Database Forecast BSC.xlsx"
            },
            "output": {
                "csv_dir": "calculated_results/forecast/bsc",
                "backup_dir": "calculated_results/forecast/bsc/backup"
            },
            "columns": {
                "ticker": "symbol",
                "Rating": "rating", 
                "target_price": "target_price",
                "2025_rev": "rev_fy",
                "2026_rev": "rev_fy_1",
                "2025_npat": "npatmi_fy",
                "2026_npat": "npatmi_fy_1",
                "2025_roe": "roe_fy",
                "2026_roe": "roe_fy_1",
                "2025_roa": "roa_fy",
                "2026_roa": "roa_fy_1"
            },
            "validation": {
                "min_symbols": 50,
                "required_columns": ["symbol", "rating", "target_price", "rev_fy", "npatmi_fy"],
                "max_change_pct": 50
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge với default config
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                    elif isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey not in config[key]:
                                config[key][subkey] = subvalue
                return config
            except Exception as e:
                logger.warning(f"Lỗi đọc config, sử dụng default: {e}")
        
        # Tạo file config mặc định
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        return default_config
    
    def backup_existing_csv(self) -> bool:
        """Backup file CSV hiện tại nếu có"""
        try:
            if self.latest_csv.exists():
                # Copy file hiện tại sang backup
                shutil.copy2(self.latest_csv, self.backup_csv)
                logger.info(f"✅ Đã backup file cũ: {self.backup_csv}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Lỗi backup file: {e}")
            return False
    
    def read_excel_data(self, source_file: Optional[str] = None) -> pd.DataFrame:
        """
        Đọc dữ liệu từ file Excel BSC
        
        Args:
            source_file: Đường dẫn file Excel (nếu không dùng default)
            
        Returns:
            DataFrame chứa dữ liệu BSC
        """
        try:
            # Xác định file input
            if source_file:
                excel_file = Path(source_file) if not os.path.isabs(source_file) else Path(source_file)
                if not excel_file.is_absolute():
                    excel_file = self.project_root / excel_file
            else:
                excel_file = self.input_file
            
            if not excel_file.exists():
                # Thử file fallback
                fallback_file_rel = self.config['input']['fallback_file']
                if not os.path.isabs(fallback_file_rel):
                    fallback_file = self.project_root / fallback_file_rel
                else:
                    fallback_file = Path(fallback_file_rel)
                
                if fallback_file.exists():
                    logger.warning(f"File chính không tồn tại, sử dụng fallback: {fallback_file}")
                    excel_file = fallback_file
                else:
                    raise FileNotFoundError(f"Không tìm thấy file Excel: {excel_file}")
            
            logger.info(f"📖 Đọc dữ liệu từ: {excel_file}")
            
            # Đọc sheet với header từ dòng 7 (cho BSC Master File)
            sheet_name = self.config['input']['sheet_name']
            if 'BSC Forecast' in sheet_name:
                df = pd.read_excel(excel_file, sheet_name=sheet_name, header=7)
            else:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            logger.info(f"✅ Đã đọc {df.shape[0]} dòng, {df.shape[1]} cột từ sheet '{sheet_name}'")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Lỗi đọc file Excel: {e}")
            raise
    
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Xử lý và chuẩn hóa dữ liệu BSC
        
        Args:
            df: DataFrame gốc từ Excel
            
        Returns:
            DataFrame đã được chuẩn hóa
        """
        try:
            logger.info("🔄 Bắt đầu xử lý dữ liệu...")
            
            # Copy để không thay đổi dữ liệu gốc
            processed_df = df.copy()
            
            # Chuẩn hóa tên cột
            processed_df.columns = processed_df.columns.str.strip()
            
            # Mapping cột theo cấu hình
            column_mapping = self.config['columns']
            available_columns = [col for col in column_mapping.keys() if col in processed_df.columns]
            
            if not available_columns:
                raise ValueError("Không tìm thấy cột nào phù hợp trong dữ liệu")
            
            # Lấy chỉ các cột cần thiết và đổi tên
            processed_df = processed_df[available_columns].copy()
            rename_mapping = {col: column_mapping[col] for col in available_columns}
            processed_df = processed_df.rename(columns=rename_mapping)
            
            # Chuẩn hóa symbol [[memory:8512150]]
            if 'symbol' in processed_df.columns:
                processed_df['symbol'] = processed_df['symbol'].str.upper().str.strip()
                # Loại bỏ các dòng có symbol rỗng
                processed_df = processed_df.dropna(subset=['symbol'])
                processed_df = processed_df[processed_df['symbol'] != '']
            
            # Chuẩn hóa rating
            if 'rating' in processed_df.columns:
                processed_df['rating'] = processed_df['rating'].str.upper().str.strip()
            
            # Chuyển đổi ROE, ROA từ decimal sang percentage
            # Note: After config mapping, columns are already renamed to roe_2025, roe_2026, etc.
            for col in ['roe_2025', 'roe_2026', 'roa_2025', 'roa_2026']:
                if col in processed_df.columns:
                    processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce') * 100
            
            # Thêm metadata
            processed_df['source'] = 'BSC'
            processed_df['update_date'] = datetime.now().strftime('%Y-%m-%d')
            processed_df['data_type'] = 'forecast'
            processed_df['processing_timestamp'] = self.timestamp
            
            # Sắp xếp theo symbol
            processed_df = processed_df.sort_values('symbol').reset_index(drop=True)
            
            logger.info(f"✅ Đã xử lý {len(processed_df)} records với {len(processed_df.columns)} cột")
            
            return processed_df
            
        except Exception as e:
            logger.error(f"❌ Lỗi xử lý dữ liệu: {e}")
            raise
    
    def validate_data(self, df: pd.DataFrame, previous_df: Optional[pd.DataFrame] = None) -> Tuple[bool, List[str]]:
        """
        Validate chất lượng dữ liệu
        
        Args:
            df: DataFrame mới
            previous_df: DataFrame từ lần cập nhật trước (nếu có)
            
        Returns:
            Tuple (is_valid, warnings)
        """
        warnings = []
        is_valid = True
        
        try:
            logger.info("🔍 Kiểm tra chất lượng dữ liệu...")
            
            validation_config = self.config['validation']
            
            # 1. Kiểm tra số lượng symbols
            min_symbols = validation_config['min_symbols']
            if len(df) < min_symbols:
                warnings.append(f"⚠️ Chỉ có {len(df)} symbols, ít hơn mức tối thiểu {min_symbols}")
                is_valid = False
            
            # 2. Kiểm tra các cột bắt buộc
            required_columns = validation_config['required_columns']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                warnings.append(f"❌ Thiếu các cột bắt buộc: {missing_columns}")
                is_valid = False
            
            # 3. Kiểm tra dữ liệu null trong các cột quan trọng
            for col in required_columns:
                if col in df.columns:
                    null_count = df[col].isnull().sum()
                    null_pct = (null_count / len(df)) * 100
                    if null_pct > 20:  # Hơn 20% null
                        warnings.append(f"⚠️ Cột '{col}' có {null_pct:.1f}% giá trị null")
            
            # 4. So sánh với dữ liệu trước (nếu có)
            if previous_df is not None and not previous_df.empty:
                # Kiểm tra thay đổi số lượng symbols
                prev_count = len(previous_df)
                curr_count = len(df)
                change_pct = abs((curr_count - prev_count) / prev_count) * 100
                
                max_change = validation_config['max_change_pct']
                if change_pct > max_change:
                    warnings.append(f"⚠️ Số lượng symbols thay đổi {change_pct:.1f}% (từ {prev_count} → {curr_count})")
                
                # Kiểm tra symbols mới và mất
                if 'symbol' in df.columns and 'symbol' in previous_df.columns:
                    prev_symbols = set(previous_df['symbol'])
                    curr_symbols = set(df['symbol'])
                    
                    new_symbols = curr_symbols - prev_symbols
                    removed_symbols = prev_symbols - curr_symbols
                    
                    if new_symbols:
                        warnings.append(f"➕ Symbols mới: {sorted(list(new_symbols))}")
                    if removed_symbols:
                        warnings.append(f"➖ Symbols bị loại: {sorted(list(removed_symbols))}")
            
            # 5. Kiểm tra giá trị bất thường
            if 'target_price' in df.columns:
                target_prices = pd.to_numeric(df['target_price'], errors='coerce')
                if target_prices.max() > 1000000:  # Hơn 1 triệu VND
                    warnings.append("⚠️ Có giá mục tiêu bất thường (> 1M VND)")
                if target_prices.min() < 1000:  # Dưới 1000 VND
                    warnings.append("⚠️ Có giá mục tiêu bất thường (< 1K VND)")
            
            if warnings:
                logger.warning(f"Phát hiện {len(warnings)} cảnh báo trong quá trình validation")
                for warning in warnings:
                    logger.warning(warning)
            else:
                logger.info("✅ Dữ liệu đã pass tất cả kiểm tra validation")
            
            return is_valid, warnings
            
        except Exception as e:
            logger.error(f"❌ Lỗi trong quá trình validation: {e}")
            return False, [f"❌ Lỗi validation: {e}"]
    
    def save_csv(self, df: pd.DataFrame) -> bool:
        """
        Lưu DataFrame thành file CSV
        
        Args:
            df: DataFrame cần lưu
            
        Returns:
            True nếu thành công
        """
        try:
            # Lưu file chính
            df.to_csv(self.latest_csv, index=False, encoding='utf-8')
            logger.info(f"✅ Đã lưu file chính: {self.latest_csv}")
            
            # Lưu file backup với timestamp
            df.to_csv(self.backup_csv, index=False, encoding='utf-8')
            logger.info(f"✅ Đã lưu file backup: {self.backup_csv}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi lưu file CSV: {e}")
            return False
    
    def load_previous_data(self) -> Optional[pd.DataFrame]:
        """Load dữ liệu từ lần cập nhật trước để so sánh"""
        try:
            if self.latest_csv.exists():
                return pd.read_csv(self.latest_csv)
            return None
        except Exception as e:
            logger.warning(f"Không thể load dữ liệu trước: {e}")
            return None
    
    def create_processing_report(self, df: pd.DataFrame, warnings: List[str], processing_time: float) -> Dict:
        """Tạo báo cáo quá trình xử lý"""
        report = {
            "timestamp": self.timestamp,
            "processing_time_seconds": round(processing_time, 2),
            "input_file": str(self.input_file),
            "output_file": str(self.latest_csv),
            "records_processed": len(df),
            "columns_count": len(df.columns),
            "symbols_count": df['symbol'].nunique() if 'symbol' in df.columns else 0,
            "warnings": warnings,
            "success": len(warnings) == 0 or all('❌' not in w for w in warnings)
        }
        
        # Lưu report
        report_file = self.output_dir / f"processing_report_{self.date_str}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def run(self, source_file: Optional[str] = None, force: bool = False) -> bool:
        """
        Chạy toàn bộ quy trình auto update
        
        Args:
            source_file: File Excel nguồn (nếu không dùng default)
            force: Bỏ qua validation errors
            
        Returns:
            True nếu thành công
        """
        start_time = datetime.now()
        
        try:
            logger.info("🚀 BẮT ĐẦU QUY TRÌNH BSC AUTO UPDATE")
            logger.info("="*60)
            
            # 1. Backup file hiện tại
            self.backup_existing_csv()
            
            # 2. Load dữ liệu trước để so sánh
            previous_df = self.load_previous_data()
            
            # 3. Đọc dữ liệu Excel mới
            raw_df = self.read_excel_data(source_file)
            
            # 4. Xử lý dữ liệu
            processed_df = self.process_data(raw_df)
            
            # 5. Validation
            is_valid, warnings = self.validate_data(processed_df, previous_df)
            
            if not is_valid and not force:
                logger.error("❌ Dữ liệu không pass validation. Sử dụng --force để bỏ qua.")
                return False
            
            # 6. Lưu file CSV
            if not self.save_csv(processed_df):
                return False
            
            # Note: PE Forward calculation is now integrated into daily valuation update
            # Run: python3 data_processor/valuation/run_optimized_daily_update.py
            
            # 7. Tạo báo cáo
            processing_time = (datetime.now() - start_time).total_seconds()
            report = self.create_processing_report(processed_df, warnings, processing_time)
            
            # 8. Thông báo kết quả
            logger.info("="*60)
            logger.info("🎉 HOÀN THÀNH BSC AUTO UPDATE!")
            logger.info("="*60)
            logger.info(f"📊 Đã xử lý: {report['records_processed']} records")
            logger.info(f"🏢 Số symbols: {report['symbols_count']}")
            logger.info(f"⏱️ Thời gian xử lý: {report['processing_time_seconds']}s")
            logger.info(f"📁 File output: {self.latest_csv}")
            
            if warnings:
                logger.info(f"⚠️ Có {len(warnings)} cảnh báo - xem log để biết chi tiết")
            
            logger.info("✅ Streamlit dashboard sẽ tự động load dữ liệu mới!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi trong quá trình auto update: {e}")
            return False


def main():
    """Main function với command line arguments"""
    parser = argparse.ArgumentParser(description='BSC Forecast Auto Update System')
    parser.add_argument('--source', '-s', help='Đường dẫn file Excel nguồn')
    parser.add_argument('--force', '-f', action='store_true', help='Bỏ qua validation errors')
    parser.add_argument('--config', '-c', default='data_processor/forecast/bsc_config.json', 
                       help='Đường dẫn file cấu hình')
    
    args = parser.parse_args()
    
    try:
        # Khởi tạo processor
        processor = BSCAutoProcessor(config_path=args.config)
        
        # Chạy quy trình
        success = processor.run(source_file=args.source, force=args.force)
        
        if success:
            print("\n🎉 BSC Auto Update hoàn thành thành công!")
            print(f"📁 File CSV mới: {processor.latest_csv}")
            print("💡 Có thể sử dụng ngay trong Streamlit dashboard.")
            sys.exit(0)
        else:
            print("\n❌ BSC Auto Update thất bại!")
            print("🔍 Kiểm tra log để biết chi tiết lỗi.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Đã dừng quá trình theo yêu cầu người dùng.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Lỗi không mong muốn: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
