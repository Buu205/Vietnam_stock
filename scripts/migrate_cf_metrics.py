import pandas as pd
import json
import os

EXCEL_PATH = '/Users/buuphan/Dev/Vietnam_dashboard/DATA/raw/Metric_code/BSC - Mô tả CSDL.xlsx'
JSON_PATH = '/Users/buuphan/Dev/Vietnam_dashboard/config/metadata/metric_registry.json'

MISSING_SHEETS = [
    'COMPANY_CF_INDIRECT',
    'COMPANY_CF_DIRECT',
    'BANK_CF_INDIRECT',
    'BANK_CF_DIRECT',
    'SECURITY_CF_INDIRECT',
    'SECURITY_CF_DIRECT',
    'INSURANCE_CF_INDIRECT',
    'INSURANCE_CF_DIRECT'
]

ENTITY_MAP = {
    'COMPANY': 'COMPANY',
    'BANK': 'BANK',
    'SECURITY': 'SECURITY',
    'INSURANCE': 'INSURANCE'
}

def get_entity_type(sheet_name):
    if sheet_name.startswith('COMPANY_'): return 'COMPANY'
    if sheet_name.startswith('BANK_'): return 'BANK'
    if sheet_name.startswith('SECURITY_'): return 'SECURITY'
    if sheet_name.startswith('INSURANCE_'): return 'INSURANCE'
    return None

def get_category(sheet_name):
    if 'CF_INDIRECT' in sheet_name: return 'CASH_FLOW_INDIRECT'
    if 'CF_DIRECT' in sheet_name: return 'CASH_FLOW_DIRECT'
    return None

def run():
    print(f"Reading existing registry from {JSON_PATH}...")
    with open(JSON_PATH, 'r') as f:
        registry = json.load(f)

    print(f"Processing Excel file {EXCEL_PATH}...")
    # Read all sheets at once is cleaner but might be slow, let's read one by one to be safe and debuggable
    
    for sheet in MISSING_SHEETS:
        print(f"Processing sheet: {sheet}")
        try:
            df = pd.read_excel(EXCEL_PATH, sheet_name=sheet)
        except Exception as e:
            print(f"Error reading sheet {sheet}: {e}")
            continue

        # Standardize columns: 'COLUMN_NAME', 'DATA_TYPE', 'Mô tả'
        # Sometimes case might vary or whitespace
        df.columns = [c.strip() for c in df.columns]
        
        # Check if required columns exist
        required_cols = ['COLUMN_NAME', 'DATA_TYPE', 'Mô tả']
        if not all(col in df.columns for col in required_cols):
             print(f"Skipping {sheet}, missing columns. Found: {df.columns.tolist()}")
             continue

        entity_type = get_entity_type(sheet)
        category_key = get_category(sheet) # CASH_FLOW_INDIRECT or CASH_FLOW_DIRECT
        
        if not entity_type or not category_key:
            print(f"Could not determine entity or category for {sheet}")
            continue

        # Ensure entity exists in registry
        if entity_type not in registry['entity_types']:
            registry['entity_types'][entity_type] = {}
            print(f"Created new entity type: {entity_type}")

        # Ensure category exists under entity
        if category_key not in registry['entity_types'][entity_type]:
            registry['entity_types'][entity_type][category_key] = {}
            print(f"Created new category: {category_key} under {entity_type}")

        count = 0
        for _, row in df.iterrows():
            code = str(row['COLUMN_NAME']).strip()
            if pd.isna(code) or code == 'nan': continue
            
            # Basic validation: Code should be somewhat alphanumeric
            
            metric_def = {
                "code": code,
                "name_vi": str(row['Mô tả']).strip() if not pd.isna(row['Mô tả']) else "",
                "name_en": "",
                "data_type": str(row['DATA_TYPE']).strip() if not pd.isna(row['DATA_TYPE']) else "NUMBER(23,2)",
                "unit": "VND",
                "category": category_key.lower(), # internal category tag often lower snake_case
                "is_calculated": False,
                "sheet_name": sheet,
                "entity_type": entity_type
            }
            
            registry['entity_types'][entity_type][category_key][code] = metric_def
            count += 1
        
        print(f"Added {count} metrics from {sheet}")

    print("Saving updated registry...")
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print("Done.")

if __name__ == "__main__":
    run()
