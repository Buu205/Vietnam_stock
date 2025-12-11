#!/usr/bin/env python3
"""
Test script để kiểm tra CommodityPriceUpdater
"""

import sys
from pathlib import Path
from datetime import date, timedelta
import time

# Add paths
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from commodity_price_updater import CommodityPriceUpdater

def test_commodity_updater():
    """Test commodity updater với một số loại commodity."""
    print("=" * 60)
    print("TEST COMMODITY PRICE UPDATER")
    print("=" * 60)
    
    try:
        # Test với 3 loại commodity đầu tiên
        project_root = current_dir.parent.parent.parent.parent
        updater = CommodityPriceUpdater(
            output_path=str(project_root / "DATA/raw/commodity/commodity_prices_test.parquet"),
            years_back=1  # Test với 1 năm để nhanh hơn
        )
        
        # Test với một số loại commodity
        test_types = ['gold_vn', 'gold_global', 'oil_crude']
        
        start_date, end_date = updater.get_date_range()
        print(f"\nDate range: {start_date} to {end_date}")
        print(f"\nTesting {len(test_types)} commodity types...\n")
        
        start_time = time.time()
        
        for commodity_type in test_types:
            print(f"Testing {commodity_type}...")
            df = updater.get_commodity_data(commodity_type, start_date, end_date)
            
            if df is not None and not df.empty:
                print(f"  ✓ Success: {len(df)} records")
                print(f"    Columns: {list(df.columns)}")
                print(f"    Date range: {df['date'].min()} to {df['date'].max()}")
                print(f"    Sample data:")
                print(df.head(3).to_string())
            else:
                print(f"  ✗ Failed: No data")
            print()
        
        elapsed = time.time() - start_time
        print(f"Total time: {elapsed:.2f}s")
        print(f"Average per commodity: {elapsed/len(test_types):.2f}s")
        
        print("\n" + "=" * 60)
        print("✅ Test completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_commodity_updater()

