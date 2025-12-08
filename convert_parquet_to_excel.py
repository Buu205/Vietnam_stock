#!/usr/bin/env python3
"""
Convert Parquet file to Excel file
Usage: python convert_parquet_to_excel.py <input_parquet> <output_excel>
"""

import sys
import pandas as pd
from pathlib import Path

def convert_parquet_to_excel(input_file: str, output_file: str):
    """Convert parquet file to Excel file"""
    try:
        # Read parquet file
        print(f"📖 Reading parquet file: {input_file}")
        df = pd.read_parquet(input_file)
        print(f"✅ Loaded {len(df)} rows and {len(df.columns)} columns")
        
        # Create output directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to Excel
        print(f"💾 Writing to Excel file: {output_file}")
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✅ Successfully converted to Excel!")
        
        # Show file info
        input_size = Path(input_file).stat().st_size / (1024 * 1024)  # MB
        output_size = Path(output_file).stat().st_size / (1024 * 1024)  # MB
        
        print(f"\n📊 File Information:")
        print(f"   Input (Parquet): {input_size:.2f} MB")
        print(f"   Output (Excel):  {output_size:.2f} MB")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {len(df.columns)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    if len(sys.argv) != 3:
        print("Usage: python convert_parquet_to_excel.py <input_parquet> <output_excel>")
        print("Example: python convert_parquet_to_excel.py data.parquet data.xlsx")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)
    
    # Convert
    success = convert_parquet_to_excel(input_file, output_file)
    
    if success:
        print(f"\n🎉 Conversion completed successfully!")
        print(f"   📁 Output file: {output_file}")
    else:
        print(f"\n💥 Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
