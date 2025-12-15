#!/usr/bin/env python3
"""
Script để chạy OHLCV Daily Updater
Sử dụng vnstock_data (source='vnd') để lấy dữ liệu OHLCV
"""

import sys
import logging
from pathlib import Path
from datetime import date, datetime

# Resolve project paths once to avoid hard-coded absolute strings
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent  # Vietnam_dashboard root (pipelines is 2 levels deep)

# Add project root to Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Ensure technical modules are importable when script runs directly
sys.path.append(str(current_dir))
sys.path.append(str(current_dir / "technical" / "ohlcv"))

# Use absolute import
from PROCESSORS.technical.ohlcv.ohlcv_daily_updater import OHLCVDailyUpdater

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='OHLCV Daily Updater')
    parser.add_argument('--date', type=str, default=None,
                       help='Target date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--force', action='store_true',
                       help='Force update even if data exists (not implemented yet)')
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Khởi tạo updater với file symbols và output path đầy đủ
        symbols_path = project_root / "config" / "metadata" / "ticker_details.json"
        output_path = project_root / "DATA" / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"
        updater = OHLCVDailyUpdater(
            output_path=str(output_path),
            symbols_file=str(symbols_path)
        )
        
        # Parse target date
        if args.date:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        else:
            target_date = date.today()
        
        # Chạy full update với tất cả symbols
        logger.info(f"Starting update with {len(updater.symbols)} symbols for date: {target_date}")
        
        if args.force:
            logger.info("⚠️  Force mode enabled (will overwrite existing data)")
        
        # Lấy dữ liệu cho ngày chỉ định
        updater.update_daily_data(target_date=target_date)
        
        logger.info(f"✅ OHLCV update completed successfully for {target_date}!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
