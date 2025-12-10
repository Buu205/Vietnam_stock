#!/usr/bin/env python3
"""
Check schema of fundamental data files
"""

import pandas as pd
from pathlib import Path

def check_schema():
    """Check column names in fundamental data files"""
    
    base_dir = Path("/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/fundamental")
    
    for entity_dir in base_dir.iterdir():
        if entity_dir.is_dir():
            print(f"\n=== {entity_dir.name} ===")
            for file_path in entity_dir.glob("*.parquet"):
                print(f"\nFile: {file_path.name}")
                try:
                    df = pd.read_parquet(file_path)
                    print(f"Columns: {list(df.columns)}")
                    print(f"Shape: {df.shape}")
                    print(f"Sample data:")
                    print(df.head(2))
                except Exception as e:
                    print(f"Error reading file: {e}")

if __name__ == "__main__":
    check_schema()