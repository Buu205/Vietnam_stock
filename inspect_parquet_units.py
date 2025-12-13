import pandas as pd
import os

files = [
    '/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/fundamental/company_full.parquet',
    '/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/fundamental/bank_full.parquet'
]

for f in files:
    print(f"\n--- {os.path.basename(f)} ---")
    if os.path.exists(f):
        try:
            df = pd.read_parquet(f)
            # Find a few likely large numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            # Filter for likely financial columns (containing 'revenue', 'asset', 'cbs', 'cis', etc.)
            fin_cols = [c for c in numeric_cols if any(x in c.lower() for x in ['revenue', 'asset', 'profit', 'equity', 'cbs', 'cis', 'bis', 'bbs'])]
            
            if not fin_cols:
                fin_cols = numeric_cols[:5]
                
            print(f"Sample data for columns: {fin_cols[:5]}")
            print(df[fin_cols[:5]].head(3).to_string())
            print(f"Max values:\n{df[fin_cols[:5]].max().to_string()}")
            
        except Exception as e:
            print(f"Error reading {f}: {e}")
    else:
        print("File not found.")
