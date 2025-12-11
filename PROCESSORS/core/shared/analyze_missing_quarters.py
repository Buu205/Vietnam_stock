"""
Script phân tích các quý bị thiếu trong calculated results
So sánh file hiện tại với backup và input data để tìm nguyên nhân
"""

import pandas as pd
from pathlib import Path
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_missing_quarters():
    """Phân tích các quý bị thiếu"""
    
    calc_path = Path('calculated_results/fundamental')
    processed_path = Path('data_warehouse/raw/fundamental/processed')
    
    # Đọc files
    company_input = processed_path / 'company_full.parquet'
    company_current = calc_path / 'company/company_financial_metrics.parquet'
    company_backup = calc_path / 'company/company_financial_metrics_backup.parquet'
    
    if not all(f.exists() for f in [company_input, company_current, company_backup]):
        logger.error("Một số files không tồn tại")
        return
    
    logger.info("Đang đọc files...")
    df_input = pd.read_parquet(company_input)
    df_current = pd.read_parquet(company_current)
    df_backup = pd.read_parquet(company_backup)
    
    # Chuẩn hóa dates
    df_input['REPORT_DATE'] = pd.to_datetime(df_input['REPORT_DATE'], errors='coerce')
    df_input = df_input[df_input['REPORT_DATE'].notna()]
    df_input['year'] = df_input['REPORT_DATE'].dt.year
    df_input['quarter'] = df_input['REPORT_DATE'].dt.quarter
    
    df_current['report_date'] = pd.to_datetime(df_current['report_date'], errors='coerce')
    df_current = df_current[df_current['report_date'].notna()]
    df_current['year'] = df_current['report_date'].dt.year
    df_current['quarter'] = df_current['report_date'].dt.quarter
    
    df_backup['report_date'] = pd.to_datetime(df_backup['report_date'], errors='coerce')
    df_backup = df_backup[df_backup['report_date'].notna()]
    df_backup['year'] = df_backup['report_date'].dt.year
    df_backup['quarter'] = df_backup['report_date'].dt.quarter
    
    # Lọc chỉ COMPANY symbols
    company_symbols = set(df_input['SECURITY_CODE'].unique())
    df_backup_company = df_backup[df_backup['symbol'].isin(company_symbols)].copy()
    
    # Tạo sets để so sánh
    input_quarters = set()
    for _, row in df_input[df_input['FREQ_CODE'] == 'Q'].iterrows():
        input_quarters.add((row['SECURITY_CODE'], row['year'], row['quarter']))
    
    backup_quarters = set()
    for _, row in df_backup_company.iterrows():
        backup_quarters.add((row['symbol'], row['year'], row['quarter']))
    
    current_quarters = set()
    for _, row in df_current.iterrows():
        current_quarters.add((row['symbol'], row['year'], row['quarter']))
    
    # Tìm missing
    missing_from_current = backup_quarters - current_quarters
    missing_from_input = backup_quarters - input_quarters
    
    logger.info(f"\n{'='*80}")
    logger.info("KẾT QUẢ PHÂN TÍCH")
    logger.info(f"{'='*80}")
    logger.info(f"Input có: {len(input_quarters)} unique quarters (FREQ_CODE='Q')")
    logger.info(f"Backup có: {len(backup_quarters)} unique quarters (chỉ COMPANY)")
    logger.info(f"Current có: {len(current_quarters)} unique quarters")
    logger.info(f"\nThiếu trong current: {len(missing_from_current)} quý")
    logger.info(f"Thiếu trong input: {len(missing_from_input)} quý")
    
    if len(missing_from_input) > 0:
        logger.warning(f"\n⚠️  Có {len(missing_from_input)} quý trong backup KHÔNG CÓ trong input")
        logger.warning("   → Có thể backup được tính toán từ version khác của input data")
    
    # Phân tích missing từ current
    if len(missing_from_current) > 0:
        logger.info(f"\n📋 Phân tích {len(missing_from_current)} quý thiếu trong current:")
        
        missing_by_symbol = {}
        missing_by_year = {}
        
        for symbol, year, quarter in missing_from_current:
            if symbol not in missing_by_symbol:
                missing_by_symbol[symbol] = []
            missing_by_symbol[symbol].append((year, quarter))
            
            if year not in missing_by_year:
                missing_by_year[year] = 0
            missing_by_year[year] += 1
        
        logger.info(f"\n   Top 20 symbols bị thiếu nhiều nhất:")
        sorted_symbols = sorted(missing_by_symbol.items(), key=lambda x: len(x[1]), reverse=True)
        for symbol, quarters in sorted_symbols[:20]:
            logger.info(f"      - {symbol}: {len(quarters)} quý - {sorted(quarters)[:5]}")
        
        logger.info(f"\n   Missing theo năm:")
        for year in sorted(missing_by_year.keys()):
            logger.info(f"      - {year}: {missing_by_year[year]} quý")
        
        # Kiểm tra xem các quý này có trong input không
        logger.info(f"\n   Kiểm tra xem các quý thiếu có trong input không:")
        found_in_input = 0
        not_in_input = 0
        
        for symbol, year, quarter in list(missing_from_current)[:100]:  # Kiểm tra 100 quý đầu
            if (symbol, year, quarter) in input_quarters:
                found_in_input += 1
            else:
                not_in_input += 1
        
        logger.info(f"      - Có trong input: {found_in_input}/{min(100, len(missing_from_current))}")
        logger.info(f"      - Không có trong input: {not_in_input}/{min(100, len(missing_from_current))}")
    
    return {
        'input_quarters': input_quarters,
        'backup_quarters': backup_quarters,
        'current_quarters': current_quarters,
        'missing_from_current': missing_from_current,
        'missing_from_input': missing_from_input
    }

if __name__ == "__main__":
    analyze_missing_quarters()

