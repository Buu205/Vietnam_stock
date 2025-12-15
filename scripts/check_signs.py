
import pandas as pd
import os

COMPANY_PATH = 'DATA/processed/fundamental/company_full.parquet'
BANK_PATH = 'DATA/processed/fundamental/bank/bank_financial_metrics.parquet'

def check_company():
    if not os.path.exists(COMPANY_PATH):
        print(f"File not found: {COMPANY_PATH}")
        return

    print(f"--- Checking Company Metrics ({COMPANY_PATH}) ---")
    df = pd.read_parquet(COMPANY_PATH)
    print("Columns sample:", df.columns[:10])
    
    # specific expense columns to check
    # Company: CIS_11 (COGS), CIS_22 (Fin Exp), CIS_25 (Selling), CIS_26 (Admin)
    target_cols = ['CIS_11', 'CIS_22', 'CIS_25', 'CIS_26', 'cis_11', 'cis_22', 'cis_25', 'cis_26']
    
    # Check if we have wide format with these columns
    found_cols = [c for c in df.columns if c in target_cols]
    if found_cols:
        print("Company Expense Values:")
        print(df[['symbol'] + found_cols].dropna().head(5))
    
    # If long format (METRIC_CODE column), filter rows
    if 'METRIC_CODE' in df.columns:
        print("Checking Company Long Format:")
        subset = df[df['METRIC_CODE'].isin(['CIS_11', 'CIS_22', 'CIS_25', 'CIS_26'])]
        if not subset.empty:
            print(subset[['SECURITY_CODE', 'METRIC_CODE', 'METRIC_VALUE']].head(10))

def check_bank():
    if not os.path.exists(BANK_PATH):
        print(f"File not found: {BANK_PATH}")
        return

    print(f"\n--- Checking Bank Metrics ({BANK_PATH}) ---")
    df = pd.read_parquet(BANK_PATH)
    
    # Bank: BIS_2 (Interest Exp), BIS_14 (OPEX), BIS_16 (Provision)
    # Note: parquet might have normalized names like 'opex', 'provision'
    print("Bank Columns:", df.columns.tolist())
    
    target_cols = ['opex', 'provision', 'interest_expenses', 'bis_2', 'bis_14', 'bis_16']
    found_cols = [c for c in df.columns if c.lower() in target_cols] 
    
    if found_cols:
        print("Bank Expense Values:")
        print(df[['symbol'] + found_cols].dropna().head(5))

def check_security():
    SECURITY_PATH = 'DATA/processed/fundamental/security/security_financial_metrics.parquet'
    if not os.path.exists(SECURITY_PATH):
        print(f"File not found: {SECURITY_PATH}")
        return

    print(f"\n--- Checking Security Metrics ({SECURITY_PATH}) ---")
    df = pd.read_parquet(SECURITY_PATH)
    print("Security Cols:", df.columns.tolist())
    
    # Check for SIS_40 (Op Exp), SIS_27 (Brokerage Exp), SIS_62 (G&A)
    # or columns with 'expense'
    target_cols = ['SIS_40', 'SIS_27', 'SIS_62', 'sis_40', 'sis_27', 'sis_62', 'operating_expenses', 'brokerage_expenses', 'ga_expenses']
    found = [c for c in df.columns if c in target_cols]
    
    if found:
         print("Security Expense Values:")
         print(df[['symbol'] + found].dropna().head(5))

if __name__ == "__main__":
    check_company()
    check_bank()
