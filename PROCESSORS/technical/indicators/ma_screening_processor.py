"""
MA Screening Data Processor

VN: Xử lý dữ liệu để tạo bảng lọc MA và lưu vào 1 file parquet duy nhất
Chỉ lưu dữ liệu ngày gần nhất, không lưu lịch sử
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import os
import sys
from pathlib import Path

# Add project root to path
# ma_screening_processor.py is at: data_processor/technical/technical/technical_indicators/
# Need to go up 4 levels to reach project root
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
project_root = str(project_root)

# Import duckdb directly - lightweight, no streamlit dependency
try:
    import duckdb
except ImportError:
    raise ImportError("duckdb is required. Install with: pip install duckdb")

# Define get_connection locally - lightweight version without streamlit
def get_connection():
    """Get DuckDB connection - lightweight local version"""
    return duckdb.connect()

# Import daily updater for auto-update
try:
    from daily_updater import DailyTechnicalUpdater
except ImportError:
    print("Warning: Could not import DailyTechnicalUpdater. Manual update may be required.")
    DailyTechnicalUpdater = None

# Data paths (resolve từ project root, không dùng iCloud absolute path)
OHLCV_BASIC = os.path.join(project_root, "DATA", "raw", "ohlcv", "OHLCV_mktcap.parquet")
MA_PATH = os.path.join(project_root, "DATA", "processed", "technical", "moving_averages", "moving_averages_full.parquet")

# Output path - chỉ 1 file duy nhất
OUTPUT_FILE = os.path.join(project_root, "DATA", "processed", "technical", "ma_screening_latest.parquet")


def load_latest_ma_and_ohlcv_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load latest MA and OHLCV data for all symbols
    
    VN: Tải dữ liệu MA và OHLCV mới nhất cho tất cả mã cổ phiếu
    """
    conn = get_connection()
    
    # Load latest MA data
    ma_query = """
    WITH latest_ma AS (
        SELECT symbol, MAX(TRY_CAST(date AS DATE)) as latest_date
        FROM read_parquet(?)
        WHERE TRY_CAST(date AS DATE) >= '1900-01-01'
        GROUP BY symbol
    )
    SELECT ma.symbol, ma.date, ma.ma20 as sma_20, ma.ma50 as sma_50, ma.ma100 as sma_100, ma.ma200 as sma_200
    FROM read_parquet(?) ma
    INNER JOIN latest_ma ld ON ma.symbol = ld.symbol 
        AND TRY_CAST(ma.date AS DATE) = ld.latest_date
    WHERE TRY_CAST(ma.date AS DATE) >= '1900-01-01'
    ORDER BY ma.symbol
    """
    
    ma_data = conn.execute(ma_query, [MA_PATH, MA_PATH]).fetchdf()
    
    # Load latest OHLCV data
    ohlcv_query = """
    WITH latest_ohlcv AS (
        SELECT symbol, MAX(TRY_CAST(date AS DATE)) as latest_date
        FROM read_parquet(?)
        WHERE TRY_CAST(date AS DATE) >= '1900-01-01'
        GROUP BY symbol
    )
    SELECT ohlcv.*
    FROM read_parquet(?) ohlcv
    INNER JOIN latest_ohlcv ld ON ohlcv.symbol = ld.symbol 
        AND TRY_CAST(ohlcv.date AS DATE) = ld.latest_date
    WHERE TRY_CAST(ohlcv.date AS DATE) >= '1900-01-01'
    ORDER BY ohlcv.symbol
    """
    
    ohlcv_data = conn.execute(ohlcv_query, [OHLCV_BASIC, OHLCV_BASIC]).fetchdf()
    
    # Convert dates
    if not ma_data.empty:
        ma_data['date'] = pd.to_datetime(ma_data['date'])
    if not ohlcv_data.empty:
        ohlcv_data['date'] = pd.to_datetime(ohlcv_data['date'])
    
    return ma_data, ohlcv_data


def calculate_ma_screening_conditions(ma_data: pd.DataFrame, ohlcv_data: pd.DataFrame, 
                                    min_volume: int = 100_000) -> pd.DataFrame:
    """Calculate MA screening conditions
    
    VN: Tính toán các điều kiện lọc MA
    """
    # Merge data
    merged_data = pd.merge(
        ma_data, 
        ohlcv_data[['symbol', 'close', 'volume']], 
        on='symbol', 
        how='inner'
    )
    
    # Filter by volume
    merged_data = merged_data[merged_data['volume'] >= min_volume]
    
    results = []
    
    for _, row in merged_data.iterrows():
        symbol = row['symbol']
        close = row['close']
        volume = row['volume']
        date = row['date']
        
        # Get MA values
        sma_20 = row.get('sma_20', None)
        sma_50 = row.get('sma_50', None)
        sma_100 = row.get('sma_100', None)
        sma_200 = row.get('sma_200', None)
        
        # Skip if missing critical MA data
        if pd.isna(sma_20) or pd.isna(sma_50):
            continue
        
        # Calculate differences
        diff_ma20 = ((close - sma_20) / sma_20 * 100) if sma_20 else None
        diff_ma50 = ((close - sma_50) / sma_50 * 100) if sma_50 else None
        diff_ma100 = ((close - sma_100) / sma_100 * 100) if sma_100 else None
        diff_ma200 = ((close - sma_200) / sma_200 * 100) if sma_200 else None
        
        # Determine conditions
        above_ma20 = close > sma_20 if sma_20 else False
        above_ma50 = close > sma_50 if sma_50 else False
        above_ma100 = close > sma_100 if sma_100 else False
        above_ma200 = close > sma_200 if sma_200 else False
        
        # MA alignment conditions (dùng MA20/50/100, không bắt buộc MA200 vì nhiều mã thiếu MA200)
        has_20_50_100 = pd.notna(sma_20) and pd.notna(sma_50) and pd.notna(sma_100)
        ma20_above_ma50 = sma_20 > sma_50 if has_20_50_100 else False
        ma50_above_ma100 = sma_50 > sma_100 if has_20_50_100 else False
        
        # Bullish alignment (MA20>MA50>MA100)
        bullish_alignment = ma20_above_ma50 and ma50_above_ma100
        
        # Bearish alignment (MA20<MA50<MA100)
        bearish_alignment = (sma_20 < sma_50 if has_20_50_100 else False) and \
                           (sma_50 < sma_100 if has_20_50_100 else False)
        
        # Near MA conditions (within 2%)
        near_ma20 = abs(diff_ma20) <= 2.0 if diff_ma20 else False
        near_ma50 = abs(diff_ma50) <= 2.0 if diff_ma50 else False
        near_ma100 = abs(diff_ma100) <= 2.0 if diff_ma100 else False
        near_ma200 = abs(diff_ma200) <= 2.0 if diff_ma200 else False
        
        # Signal conditions
        cut_up_ma20 = near_ma20 and above_ma20 and (diff_ma20 > 0.5) if diff_ma20 else False
        cut_down_ma20 = near_ma20 and not above_ma20 and (diff_ma20 < -0.5) if diff_ma20 else False
        near_ma50_above = near_ma50 and above_ma50
        near_ma50_below = near_ma50 and not above_ma50
        
        results.append({
            'date': date,
            'symbol': symbol,
            'close': close,
            'volume': volume,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'sma_100': sma_100,
            'sma_200': sma_200,
            'diff_ma20_pct': diff_ma20,
            'diff_ma50_pct': diff_ma50,
            'diff_ma100_pct': diff_ma100,
            'diff_ma200_pct': diff_ma200,
            'above_ma20': above_ma20,
            'above_ma50': above_ma50,
            'above_ma100': above_ma100,
            'above_ma200': above_ma200,
            'bullish_alignment': bullish_alignment,
            'bearish_alignment': bearish_alignment,
            'near_ma20': near_ma20,
            'near_ma50': near_ma50,
            'near_ma100': near_ma100,
            'near_ma200': near_ma200,
            'cut_up_ma20': cut_up_ma20,
            'cut_down_ma20': cut_down_ma20,
            'near_ma50_above': near_ma50_above,
            'near_ma50_below': near_ma50_below
        })
    
    return pd.DataFrame(results)


def save_ma_screening_data(screening_df: pd.DataFrame):
    """Save MA screening data to single parquet file
    
    VN: Lưu dữ liệu MA screening vào 1 file parquet duy nhất
    """
    # Ensure output directory exists
    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Save to single file (overwrite each time)
    screening_df.to_parquet(OUTPUT_FILE, index=False)
    print(f"Saved MA screening data: {OUTPUT_FILE}")
    print(f"Total records: {len(screening_df)}")


def auto_update_technical_indicators():
    """Auto-update technical indicators if needed
    
    VN: Tự động cập nhật technical indicators nếu cần
    """
    if DailyTechnicalUpdater is None:
        print("⚠️  DailyTechnicalUpdater không khả dụng. Bỏ qua auto-update.")
        return False
    
    try:
        print("🔄 Kiểm tra và cập nhật technical indicators...")
        updater = DailyTechnicalUpdater()
        
        # Get latest date from OHLCV data
        ohlcv_df = pd.read_parquet(updater.ohlcv_path)
        ohlcv_df['date'] = pd.to_datetime(ohlcv_df['date']).dt.date
        latest_ohlcv_date = ohlcv_df['date'].max()
        
        # Get latest processed date from moving_averages (key indicator)
        latest_processed_date = updater.get_latest_date('moving_averages')
        
        if latest_processed_date is None or latest_ohlcv_date > latest_processed_date:
            print(f"📊 Phát hiện dữ liệu mới: {latest_ohlcv_date}")
            print(f"📅 Dữ liệu đã xử lý: {latest_processed_date}")
            print("⏳ Đang cập nhật technical indicators...")
            
            # Run incremental update using the main method
            updater.update_all_indicators(target_date=latest_processed_date)
            print("✅ Cập nhật technical indicators thành công!")
            return True
        else:
            print(f"✅ Technical indicators đã cập nhật (latest: {latest_processed_date})")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi auto-update technical indicators: {e}")
        print("⚠️  Tiếp tục với dữ liệu hiện có...")
        return False


def process_ma_screening(min_volume: int = 100_000, auto_update: bool = True):
    """Main processing function
    
    VN: Hàm xử lý chính
    
    Args:
        min_volume: Volume tối thiểu để lọc
        auto_update: Tự động cập nhật technical indicators trước khi xử lý
    """
    print("=== MA SCREENING DATA PROCESSOR ===")
    print(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Volume tối thiểu: {min_volume:,}")
    print(f"Auto-update: {'Bật' if auto_update else 'Tắt'}")
    print()
    
    try:
        # Auto-update technical indicators if enabled
        if auto_update:
            auto_update_technical_indicators()
            print()
        
        # Load data
        print("Đang tải dữ liệu...")
        ma_data, ohlcv_data = load_latest_ma_and_ohlcv_data()
        
        if ma_data.empty or ohlcv_data.empty:
            print("Không có dữ liệu để xử lý.")
            return
        
        latest_date = ma_data['date'].max()
        print(f"Dữ liệu mới nhất đến: {latest_date}")
        print(f"Tổng số mã cổ phiếu: {len(ma_data)}")
        
        # Calculate conditions
        print("Đang tính toán điều kiện MA...")
        screening_df = calculate_ma_screening_conditions(ma_data, ohlcv_data, min_volume)
        
        if screening_df.empty:
            print("Không có mã cổ phiếu nào thỏa mãn điều kiện.")
            return
        
        print(f"Số mã có volume ≥ {min_volume:,}: {len(screening_df)}")
        
        # Count signals
        signal_types = ['cut_up_ma20', 'cut_down_ma20', 'near_ma50_above', 
                       'near_ma50_below', 'bullish_alignment', 'bearish_alignment']
        
        print("\n=== THỐNG KÊ TÍN HIỆU ===")
        for signal_type in signal_types:
            if signal_type in screening_df.columns:
                count = screening_df[signal_type].sum()
                print(f"{signal_type}: {count} mã")
        
        # Save data
        print("\nĐang lưu dữ liệu...")
        save_ma_screening_data(screening_df)
        
        print("\n=== HOÀN THÀNH ===")
        print("Dữ liệu đã được xử lý và lưu vào file parquet.")
        
    except Exception as e:
        print(f"Lỗi: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='MA Screening Data Processor with Auto-Update')
    parser.add_argument('--min-volume', type=int, default=100_000, 
                       help='Minimum volume threshold (default: 100,000)')
    parser.add_argument('--no-auto-update', action='store_true',
                       help='Disable automatic technical indicators update')
    
    args = parser.parse_args()
    
    # Auto-update is enabled by default, disabled only if --no-auto-update is specified
    auto_update = not args.no_auto_update
    
    process_ma_screening(args.min_volume, auto_update)
