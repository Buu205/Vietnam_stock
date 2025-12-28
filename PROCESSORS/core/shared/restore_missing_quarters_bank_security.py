"""
Script khôi phục các quý bị thiếu từ backup cho BANK và SECURITY
- Chỉ lấy đúng entity type từ backup
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

def restore_bank():
    """Khôi phục dữ liệu BANK"""

    # Canonical v4.0.0 paths
    base_path = Path(__file__).resolve().parents[3]
    calc_path = base_path / 'DATA' / 'processed' / 'fundamental'
    processed_path = base_path / 'DATA' / 'processed' / 'fundamental'
    
    # Đường dẫn files
    bank_input = processed_path / 'bank_full.parquet'
    bank_current = calc_path / 'bank/bank_financial_metrics.parquet'
    
    # Tìm backup file mới nhất
    bank_backups = sorted([f for f in (calc_path / 'bank').glob('*backup*.parquet')], reverse=True)
    if not bank_backups:
        logger.error("Không tìm thấy backup file cho BANK")
        return
    
    bank_backup = bank_backups[0]
    
    # Backup file hiện tại
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_current = calc_path / 'bank' / f'bank_financial_metrics_before_restore_{timestamp}.parquet'
    
    if not bank_current.exists():
        logger.error(f"File hiện tại không tồn tại: {bank_current}")
        return
    
    logger.info("="*80)
    logger.info("KHÔI PHỤC DỮ LIỆU BANK TỪ BACKUP")
    logger.info("="*80)
    
    # Backup file hiện tại
    logger.info(f"\n1. Backup file hiện tại...")
    shutil.copy2(bank_current, backup_current)
    logger.info(f"   ✅ Đã backup: {backup_current}")
    
    # Đọc files
    logger.info(f"\n2. Đang đọc files...")
    df_current = pd.read_parquet(bank_current)
    df_backup = pd.read_parquet(bank_backup)
    
    # Lấy danh sách BANK symbols từ input
    logger.info(f"   Đang đọc input để lấy BANK symbols...")
    df_input = pd.read_parquet(bank_input)
    bank_symbols = set(df_input['SECURITY_CODE'].unique())
    logger.info(f"   ✅ Có {len(bank_symbols)} BANK symbols")
    
    # Lọc chỉ BANK symbols từ backup
    logger.info(f"\n3. Lọc BANK symbols từ backup...")
    df_backup_bank = df_backup[df_backup['symbol'].isin(bank_symbols)].copy()
    logger.info(f"   - Backup tổng: {len(df_backup)} records")
    logger.info(f"   - Backup BANK: {len(df_backup_bank)} records")
    
    # Chuẩn hóa dates
    logger.info(f"\n4. Chuẩn hóa dates...")
    df_current['report_date'] = pd.to_datetime(df_current['report_date'], errors='coerce')
    df_current = df_current[df_current['report_date'].notna()]
    df_current['year'] = df_current['report_date'].dt.year
    df_current['quarter'] = df_current['report_date'].dt.quarter
    
    df_backup_bank['report_date'] = pd.to_datetime(df_backup_bank['report_date'], errors='coerce')
    df_backup_bank = df_backup_bank[df_backup_bank['report_date'].notna()]
    df_backup_bank['year'] = df_backup_bank['report_date'].dt.year
    df_backup_bank['quarter'] = df_backup_bank['report_date'].dt.quarter
    
    # Tạo keys để so sánh
    logger.info(f"\n5. So sánh và tìm quý bị thiếu...")
    current_keys = set()
    for _, row in df_current.iterrows():
        current_keys.add((row['symbol'], row['year'], row['quarter']))
    
    backup_keys = set()
    for _, row in df_backup_bank.iterrows():
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
    for _, row in df_backup_bank.iterrows():
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
        keep='first'
    )
    after_dedup = len(df_merged)
    
    if before_dedup != after_dedup:
        logger.info(f"   ✅ Đã loại bỏ {before_dedup - after_dedup} duplicates")
    
    # Xóa các columns tạm thời
    if 'year' in df_merged.columns:
        df_merged = df_merged.drop(columns=['year', 'quarter'])
    
    # Lưu file
    logger.info(f"\n10. Lưu file mới...")
    df_merged.to_parquet(bank_current, index=False)
    logger.info(f"   ✅ Đã lưu: {bank_current}")
    
    # Kiểm tra kết quả
    logger.info(f"\n11. Kiểm tra kết quả...")
    df_final = pd.read_parquet(bank_current)
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
    logger.info("✅ HOÀN TẤT KHÔI PHỤC BANK")
    logger.info(f"{'='*80}")

def restore_security():
    """Khôi phục dữ liệu SECURITY - kiểm tra từ company backup"""

    # Canonical v4.0.0 paths
    base_path = Path(__file__).resolve().parents[3]
    calc_path = base_path / 'DATA' / 'processed' / 'fundamental'
    processed_path = base_path / 'DATA' / 'processed' / 'fundamental'
    
    # Đường dẫn files
    security_input = processed_path / 'security_full.parquet'
    security_current = calc_path / 'security/security_financial_metrics.parquet'
    
    # Kiểm tra xem có backup trong company backup không
    company_backup = calc_path / 'company/company_financial_metrics_backup.parquet'
    
    if not company_backup.exists():
        logger.warning("Không tìm thấy company backup để lấy SECURITY data")
        return
    
    # Backup file hiện tại
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_current = calc_path / 'security' / f'security_financial_metrics_before_restore_{timestamp}.parquet'
    
    if not security_current.exists():
        logger.error(f"File hiện tại không tồn tại: {security_current}")
        return
    
    logger.info("="*80)
    logger.info("KHÔI PHỤC DỮ LIỆU SECURITY TỪ BACKUP")
    logger.info("="*80)
    
    # Backup file hiện tại
    logger.info(f"\n1. Backup file hiện tại...")
    shutil.copy2(security_current, backup_current)
    logger.info(f"   ✅ Đã backup: {backup_current}")
    
    # Đọc files
    logger.info(f"\n2. Đang đọc files...")
    df_current = pd.read_parquet(security_current)
    df_backup = pd.read_parquet(company_backup)  # Company backup có thể chứa SECURITY
    
    # Lấy danh sách SECURITY symbols từ input
    logger.info(f"   Đang đọc input để lấy SECURITY symbols...")
    df_input = pd.read_parquet(security_input)
    security_symbols = set(df_input['SECURITY_CODE'].unique())
    logger.info(f"   ✅ Có {len(security_symbols)} SECURITY symbols")
    
    # Lọc chỉ SECURITY symbols từ backup
    logger.info(f"\n3. Lọc SECURITY symbols từ backup...")
    df_backup_security = df_backup[df_backup['symbol'].isin(security_symbols)].copy()
    logger.info(f"   - Backup tổng: {len(df_backup)} records")
    logger.info(f"   - Backup SECURITY: {len(df_backup_security)} records")
    
    if len(df_backup_security) == 0:
        logger.warning("   ⚠️  Không tìm thấy SECURITY data trong backup")
        return
    
    # Chuẩn hóa dates
    logger.info(f"\n4. Chuẩn hóa dates...")
    df_current['report_date'] = pd.to_datetime(df_current['report_date'], errors='coerce')
    df_current = df_current[df_current['report_date'].notna()]
    df_current['year'] = df_current['report_date'].dt.year
    df_current['quarter'] = df_current['report_date'].dt.quarter
    
    df_backup_security['report_date'] = pd.to_datetime(df_backup_security['report_date'], errors='coerce')
    df_backup_security = df_backup_security[df_backup_security['report_date'].notna()]
    df_backup_security['year'] = df_backup_security['report_date'].dt.year
    df_backup_security['quarter'] = df_backup_security['report_date'].dt.quarter
    
    # Tạo keys để so sánh
    logger.info(f"\n5. So sánh và tìm quý bị thiếu...")
    current_keys = set()
    for _, row in df_current.iterrows():
        current_keys.add((row['symbol'], row['year'], row['quarter']))
    
    backup_keys = set()
    for _, row in df_backup_security.iterrows():
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
    for _, row in df_backup_security.iterrows():
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
        keep='first'
    )
    after_dedup = len(df_merged)
    
    if before_dedup != after_dedup:
        logger.info(f"   ✅ Đã loại bỏ {before_dedup - after_dedup} duplicates")
    
    # Xóa các columns tạm thời
    if 'year' in df_merged.columns:
        df_merged = df_merged.drop(columns=['year', 'quarter'])
    
    # Lưu file
    logger.info(f"\n10. Lưu file mới...")
    df_merged.to_parquet(security_current, index=False)
    logger.info(f"   ✅ Đã lưu: {security_current}")
    
    # Kiểm tra kết quả
    logger.info(f"\n11. Kiểm tra kết quả...")
    df_final = pd.read_parquet(security_current)
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
    logger.info("✅ HOÀN TẤT KHÔI PHỤC SECURITY")
    logger.info(f"{'='*80}")

if __name__ == "__main__":
    logger.info("="*80)
    logger.info("KHÔI PHỤC DỮ LIỆU BANK VÀ SECURITY")
    logger.info("="*80)
    
    logger.info("\n" + "="*80)
    logger.info("PHẦN 1: BANK")
    logger.info("="*80)
    restore_bank()
    
    logger.info("\n\n" + "="*80)
    logger.info("PHẦN 2: SECURITY")
    logger.info("="*80)
    restore_security()
    
    logger.info("\n" + "="*80)
    logger.info("✅ HOÀN TẤT TẤT CẢ")
    logger.info("="*80)

