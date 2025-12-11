#!/usr/bin/env python3
"""
Script để merge Q2 & Q3/2025 từ /copy/input vào processed files
"""
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def merge_entity(entity_name, input_file, processed_file):
    """Merge Q2 & Q3/2025 từ input vào processed file"""
    logger.info(f"\n{'='*80}")
    logger.info(f"🔄 Đang xử lý {entity_name}")
    logger.info(f"{'='*80}")
    
    try:
        # 1. Đọc input file
        logger.info(f"📖 Đang đọc input: {input_file.name}")
        input_df = pd.read_parquet(input_file)
        input_df['REPORT_DATE'] = pd.to_datetime(input_df['REPORT_DATE'])
        
        # Lấy Q2 & Q3/2025
        q2_q3_input = input_df[
            (input_df['REPORT_DATE'].dt.year == 2025) &
            (input_df['REPORT_DATE'].dt.quarter.isin([2, 3]))
        ].copy()
        
        logger.info(f"   Input Q2/2025: {len(input_df[(input_df['REPORT_DATE'].dt.year == 2025) & (input_df['REPORT_DATE'].dt.quarter == 2)]):,} records ({input_df[(input_df['REPORT_DATE'].dt.year == 2025) & (input_df['REPORT_DATE'].dt.quarter == 2)]['SECURITY_CODE'].nunique()} symbols)")
        logger.info(f"   Input Q3/2025: {len(input_df[(input_df['REPORT_DATE'].dt.year == 2025) & (input_df['REPORT_DATE'].dt.quarter == 3)]):,} records ({input_df[(input_df['REPORT_DATE'].dt.year == 2025) & (input_df['REPORT_DATE'].dt.quarter == 3)]['SECURITY_CODE'].nunique()} symbols)")
        
        # 2. Đọc processed file
        logger.info(f"📖 Đang đọc processed: {processed_file.name}")
        proc_df = pd.read_parquet(processed_file)
        proc_df['REPORT_DATE'] = pd.to_datetime(proc_df['REPORT_DATE'])
        
        before_total = len(proc_df)
        proc_q2_before = len(proc_df[(proc_df['REPORT_DATE'].dt.year == 2025) & (proc_df['REPORT_DATE'].dt.quarter == 2)])
        proc_q3_before = len(proc_df[(proc_df['REPORT_DATE'].dt.year == 2025) & (proc_df['REPORT_DATE'].dt.quarter == 3)])
        
        logger.info(f"   Processed trước merge:")
        logger.info(f"      Total: {before_total:,} records")
        logger.info(f"      Q2/2025: {proc_q2_before:,} records ({proc_df[(proc_df['REPORT_DATE'].dt.year == 2025) & (proc_df['REPORT_DATE'].dt.quarter == 2)]['SECURITY_CODE'].nunique()} symbols)")
        logger.info(f"      Q3/2025: {proc_q3_before:,} records ({proc_df[(proc_df['REPORT_DATE'].dt.year == 2025) & (proc_df['REPORT_DATE'].dt.quarter == 3)]['SECURITY_CODE'].nunique()} symbols)")
        
        # 3. Lấy existing codes trong processed
        existing_codes = set(proc_df['SECURITY_CODE'].unique())
        logger.info(f"   Existing codes in processed: {len(existing_codes)}")
        
        # 4. Filter input để chỉ lấy existing codes
        q2_q3_input = q2_q3_input[q2_q3_input['SECURITY_CODE'].isin(existing_codes)].copy()
        logger.info(f"   Filtered input (existing codes only): {len(q2_q3_input):,} records")
        
        # 5. Remove Q2 & Q3/2025 cũ từ processed
        proc_df = proc_df[
            ~((proc_df['REPORT_DATE'].dt.year == 2025) & 
              (proc_df['REPORT_DATE'].dt.quarter.isin([2, 3])))
        ].copy()
        
        logger.info(f"   Removed old Q2 & Q3/2025: {before_total - len(proc_df):,} records")
        
        # 6. Merge với data mới
        merged_df = pd.concat([proc_df, q2_q3_input], ignore_index=True)
        
        # 7. Remove duplicates
        before_dedup = len(merged_df)
        merged_df = merged_df.drop_duplicates(
            subset=['SECURITY_CODE', 'REPORT_DATE', 'METRIC_CODE'],
            keep='last'
        )
        after_dedup = len(merged_df)
        
        if before_dedup != after_dedup:
            logger.info(f"   Removed {before_dedup - after_dedup:,} duplicates")
        
        # 8. Validation
        merged_q2 = merged_df[(merged_df['REPORT_DATE'].dt.year == 2025) & (merged_df['REPORT_DATE'].dt.quarter == 2)]
        merged_q3 = merged_df[(merged_df['REPORT_DATE'].dt.year == 2025) & (merged_df['REPORT_DATE'].dt.quarter == 3)]
        
        logger.info(f"\n   ✅ Sau merge:")
        logger.info(f"      Total: {len(merged_df):,} records (trước: {before_total:,}, +{len(merged_df) - before_total:,})")
        logger.info(f"      Q2/2025: {len(merged_q2):,} records ({merged_q2['SECURITY_CODE'].nunique()} symbols)")
        logger.info(f"      Q3/2025: {len(merged_q3):,} records ({merged_q3['SECURITY_CODE'].nunique()} symbols)")
        
        # 9. Fix data types before saving
        # Convert REPORTED_DATE to datetime (có thể có string values)
        if 'REPORTED_DATE' in merged_df.columns:
            merged_df['REPORTED_DATE'] = pd.to_datetime(merged_df['REPORTED_DATE'], errors='coerce')
        
        # Convert YEAR, QUARTER to Int64 (nullable integer)
        if 'YEAR' in merged_df.columns:
            merged_df['YEAR'] = merged_df['YEAR'].astype('Int64')
        if 'QUARTER' in merged_df.columns:
            merged_df['QUARTER'] = merged_df['QUARTER'].astype('Int64')
        
        # 10. Lưu file
        merged_df.to_parquet(processed_file, index=False)
        logger.info(f"   💾 Đã lưu: {processed_file}")
        logger.info(f"   ✅ Hoàn thành {entity_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Lỗi: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    base_path = Path(__file__).parent.parent.parent
    
    entities = {
        'COMPANY': {
            'input': base_path / 'copy/input/COMPANY_Q3_2025_FILTERED_448.parquet',
            'processed': base_path / 'data_warehouse/raw/fundamental/processed/company_full.parquet'
        },
        'BANK': {
            'input': base_path / 'copy/input/BANK_Q3_2025_FILTERED_448.parquet',
            'processed': base_path / 'data_warehouse/raw/fundamental/processed/bank_full.parquet'
        },
        'SECURITY': {
            'input': base_path / 'copy/input/SECURITY_Q3_2025_FILTERED_448.parquet',
            'processed': base_path / 'data_warehouse/raw/fundamental/processed/security_full.parquet'
        },
        'INSURANCE': {
            'input': base_path / 'copy/input/INSURANCE_Q3_2025_FILTERED_448.parquet',
            'processed': base_path / 'data_warehouse/raw/fundamental/processed/insurance_full.parquet'
        }
    }
    
    logger.info("🚀 BẮT ĐẦU MERGE Q2 & Q3/2025 TỪ /COPY/INPUT")
    logger.info("="*80)
    
    results = {}
    
    for entity_name, paths in entities.items():
        if not paths['input'].exists():
            logger.warning(f"\n⚠️  Input file không tồn tại: {paths['input']}")
            results[entity_name] = False
            continue
        
        if not paths['processed'].exists():
            logger.warning(f"\n⚠️  Processed file không tồn tại: {paths['processed']}")
            results[entity_name] = False
            continue
        
        results[entity_name] = merge_entity(entity_name, paths['input'], paths['processed'])
    
    # Summary
    logger.info(f"\n{'='*80}")
    logger.info("📊 TÓM TẮT KẾT QUẢ")
    logger.info("="*80)
    
    for entity_name, success in results.items():
        status = "✅ Thành công" if success else "❌ Thất bại"
        logger.info(f"   {entity_name}: {status}")
    
    if all(results.values()):
        logger.info("\n🎉 HOÀN THÀNH TẤT CẢ!")
    else:
        logger.warning(f"\n⚠️  Có {sum(1 for v in results.values() if not v)} entity thất bại")

if __name__ == "__main__":
    main()

