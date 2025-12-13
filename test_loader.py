
import sys
import os
import pandas as pd

# Add project root to path
sys.path.append('/Users/buuphan/Dev/Vietnam_dashboard')

from WEBAPP.services.financial_metrics_loader import FinancialMetricsLoader

def test_loader():
    loader = FinancialMetricsLoader()
    
    # Test 1: Get Entity Type
    symbol = "VNM"
    entity_type = loader.get_entity_type(symbol)
    print(f"Symbol: {symbol}, Entity Type: {entity_type}")
    
    # Test 2: Load Data
    print(f"Loading data for {symbol}...")
    df = loader.load_financial_metrics(symbol, start_year=2023)
    
    if not df.empty:
        print(f"Loaded {len(df)} rows.")
        print("Columns:", df.columns[:5])
        print("Latest Date:", df['report_date'].max())
    else:
        print("No data loaded.")

    # Test 3: Get All Symbols
    all_syms = loader.get_all_symbols()
    print(f"Total symbols: {len(all_syms)}")

if __name__ == "__main__":
    test_loader()
