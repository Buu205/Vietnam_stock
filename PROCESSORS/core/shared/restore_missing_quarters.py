"""
Script khôi phục các quý bị thiếu từ backup vào file hiện tại
- Chỉ lấy COMPANY symbols từ backup
- Giữ Q3/2025 từ file hiện tại (không ghi đè)
- Merge và lưu file mới
"""

import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
import shutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def restore_missing_quarters():
    """Khôi phục các quý bị thiếu từ backup"""
    
    calc_path = Path('calculated_results/fundamental')
    processed_path = Path('data_warehouse/raw/fundamental/processed')
    
    # Đường dẫn files
    company_input = processed_path / 'company_full.parquet'
    company_current = calc_path / 'company/company_financial_metrics.parquet'
    company_backup = calc_path / 'company/company_financial_metrics_backup.parquet'
    
    # Backup file hiện tại trước khi sửa
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_current = calc_path / 'company' / f'company_financial_metrics_before_restore_{timestamp}.parquet'
    
    if not company_current.exists():
        logger.error(f"File hiện tại không tồn tại: {company_current}")
        return
    
    if not company_backup.exists():
        logger.error(f"File backup không tồn tại: {company_backup}")
        return
    
    logger.info("="*80)
    logger.info("KHÔI PHỤC DỮ LIỆU TỪ BACKUP")
    logger.info("="*80)
    
    # Backup file hiện tại
    logger.info(f"\n1. Backup file hiện tại...")
    shutil.copy2(company_current, backup_current)
    logger.info(f"   ✅ Đã backup: {backup_current}")
    
    # Đọc files
    logger.info(f"\n2. Đang đọc files...")
    df_current = pd.read_parquet(company_current)
    df_backup = pd.read_parquet(company_backup)
    
    # Lấy danh sách COMPANY symbols từ input
    logger.info(f"   Đang đọc input để lấy COMPANY symbols...")
    df_input = pd.read_parquet(company_input)
    company_symbols = set(df_input['SECURITY_CODE'].unique())
    logger.info(f"   ✅ Có {len(company_symbols)} COMPANY symbols")
    
    # Lọc chỉ COMPANY symbols từ backup
    logger.info(f"\n3. Lọc COMPANY symbols từ backup...")
    df_backup_company = df_backup[df_backup['symbol'].isin(company_symbols)].copy()
    logger.info(f"   - Backup tổng: {len(df_backup)} records")
    logger.info(f"   - Backup COMPANY: {len(df_backup_company)} records")
    
    # Chuẩn hóa dates
    logger.info(f"\n4. Chuẩn hóa dates...")
    df_current['report_date'] = pd.to_datetime(df_current['report_date'], errors='coerce')
    df_current = df_current[df_current['report_date'].notna()]
    df_current['year'] = df_current['report_date'].dt.year
    df_current['quarter'] = df_current['report_date'].dt.quarter
    
    df_backup_company['report_date'] = pd.to_datetime(df_backup_company['report_date'], errors='coerce')
    df_backup_company = df_backup_company[df_backup_company['report_date'].notna()]
    df_backup_company['year'] = df_backup_company['report_date'].dt.year
    df_backup_company['quarter'] = df_backup_company['report_date'].dt.quarter
    
    # Tạo keys để so sánh
    logger.info(f"\n5. So sánh và tìm quý bị thiếu...")
    current_keys = set()
    for _, row in df_current.iterrows():
        current_keys.add((row['symbol'], row['year'], row['quarter']))
    
    backup_keys = set()
    for _, row in df_backup_company.iterrows():
        backup_keys.add((row['symbol'], row['year'], row['quarter']))
    
    missing_keys = backup_keys - current_keys
    logger.info(f"   - Current có: {len(current_keys)} unique quarters")
    logger.info(f"   - Backup có: {len(backup_keys)} unique quarters")
    logger.info(f"   - Thiếu trong current: {len(missing_keys)} quarters")
    
    if len(missing_keys) == 0:
        logger.info("   ✅ Không có quý nào bị thiếu!")
        return
    
    # Lấy các records bị thiếu từ backup
    logger.info(f"\n6. Lấy các records bị thiếu từ backup...")
    missing_records = []
    for _, row in df_backup_company.iterrows():
        key = (row['symbol'], row['year'], row['quarter'])
        if key in missing_keys:
            missing_records.append(row)
    
    df_missing = pd.DataFrame(missing_records)
    logger.info(f"   ✅ Đã lấy {len(df_missing)} records bị thiếu")
    
    # Loại bỏ Q3/2025 từ missing nếu có (giữ từ current)
    logger.info(f"\n7. Loại bỏ Q3/2025 từ missing (giữ từ current)...")
    before_remove = len(df_missing)
    df_missing = df_missing[
        ~((df_missing['year'] == 2025) & (df_missing['quarter'] == 3))
    ].copy()
    after_remove = len(df_missing)
    
    if before_remove != after_remove:
        logger.info(f"   ✅ Đã loại bỏ {before_remove - after_remove} records Q3/2025 (giữ từ current)")
    
    # Merge với current
    logger.info(f"\n8. Merge với file hiện tại...")
    df_merged = pd.concat([df_current, df_missing], ignore_index=True)
    
    # Sắp xếp
    df_merged = df_merged.sort_values(['symbol', 'year', 'quarter', 'report_date'])
    
    # Loại bỏ duplicates (nếu có) - ưu tiên current
    logger.info(f"\n9. Loại bỏ duplicates...")
    before_dedup = len(df_merged)
    df_merged = df_merged.drop_duplicates(
        subset=['symbol', 'year', 'quarter'],
        keep='first'  # Giữ record đầu tiên (từ current nếu có)
    )
    after_dedup = len(df_merged)
    
    if before_dedup != after_dedup:
        logger.info(f"   ✅ Đã loại bỏ {before_dedup - after_dedup} duplicates")
    
    # Xóa các columns tạm thời
    if 'year' in df_merged.columns:
        df_merged = df_merged.drop(columns=['year', 'quarter'])
    
    # Lưu file
    logger.info(f"\n10. Lưu file mới...")
    df_merged.to_parquet(company_current, index=False)
    logger.info(f"   ✅ Đã lưu: {company_current}")
    
    # Kiểm tra kết quả
    logger.info(f"\n11. Kiểm tra kết quả...")
    df_final = pd.read_parquet(company_current)
    df_final['report_date'] = pd.to_datetime(df_final['report_date'], errors='coerce')
    df_final = df_final[df_final['report_date'].notna()]
    df_final['year'] = df_final['report_date'].dt.year
    df_final['quarter'] = df_final['report_date'].dt.quarter
    
    final_keys = set()
    for _, row in df_final.iterrows():
        final_keys.add((row['symbol'], row['year'], row['quarter']))
    
    logger.info(f"   - Records trước: {len(df_current):,}")
    logger.info(f"   - Records sau: {len(df_final):,}")
    logger.info(f"   - Thêm mới: {len(df_final) - len(df_current):,} records")
    logger.info(f"   - Unique quarters: {len(final_keys)}")
    
    # Kiểm tra Q3/2025
    q3_2025 = df_final[(df_final['year'] == 2025) & (df_final['quarter'] == 3)]
    logger.info(f"   - Q3/2025: {len(q3_2025)} records (phải giữ nguyên)")
    
    logger.info(f"\n{'='*80}")
    logger.info("✅ HOÀN TẤT KHÔI PHỤC")
    logger.info(f"{'='*80}")
    logger.info(f"   - File backup: {backup_current}")
    logger.info(f"   - File đã khôi phục: {company_current}")
    logger.info(f"   - Đã thêm {len(df_missing):,} records từ backup")
    logger.info(f"{'='*80}")

if __name__ == "__main__":
    restore_missing_quarters()

