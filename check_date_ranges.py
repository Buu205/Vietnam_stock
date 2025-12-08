#!/usr/bin/env python3
"""
Script to check date ranges in parquet files
"""
import pandas as pd
from pathlib import Path

def check_date_range(file_path):
    """Check min and max dates in a parquet file"""
    try:
        # Read the file to get columns
        df = pd.read_parquet(file_path)
        print(f"\nColumns in {file_path.name}:")
        print(df.columns.tolist())
        
        # Try to find date/datetime columns
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        
        if date_columns:
            print(f"Date columns found: {date_columns}")
            
            # Get min/max for date columns
            for col in date_columns:
                min_date = df[col].min()
                max_date = df[col].max()
                print(f"Column '{col}': {min_date} to {max_date}")
        else:
            # If no obvious date columns, try to find period or report_date columns
            other_date_cols = [col for col in df.columns if any(x in col.lower() for x in ['period', 'report', 'quarter', 'year', 'month'])]
            if other_date_cols:
                print(f"Possible date columns: {other_date_cols}")
                for col in other_date_cols:
                    min_val = df[col].min()
                    max_val = df[col].max()
                    print(f"Column '{col}': {min_val} to {max_val}")
            else:
                print("No obvious date columns found. Showing first 5 rows to help identify date fields:")
                print(df.head())
        
        print(f"Total rows: {len(df)}")
        
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")

def main():
    data_dir = Path("/Users/buuphan/Dev/Vietnam_dashboard/DATA/refined/fundamental/current/")
    
    files = [
        "bank_full.parquet",
        "company_full.parquet",
        "insurance_full.parquet",
        "security_full.parquet"
    ]
    
    for file_name in files:
        file_path = data_dir / file_name
        if file_path.exists():
            print(f"\n{'='*60}")
            print(f"Checking: {file_name}")
            print(f"{'='*60}")
            check_date_range(file_path)
        else:
            print(f"\nFile not found: {file_path}")

if __name__ == "__main__":
    main()