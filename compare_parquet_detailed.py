#!/usr/bin/env python3
"""
So sánh chi tiết Parquet files (OLD vs NEW)
Kiểm tra xem calculator có thay đổi gì không
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 80)
print("SO SÁNH CHI TIẾT PARQUET FILES (OLD vs NEW)")
print("=" * 80)

# Paths
company_old = Path("backup_parquet_before_test/company_OLD.parquet")
company_new = Path("DATA/processed/fundamental/company/company_financial_metrics.parquet")
bank_old = Path("backup_parquet_before_test/bank_OLD.parquet")
bank_new = Path("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")

def compare_parquet(old_path, new_path, entity_type):
    """So sánh 2 parquet files"""
    print(f"\n{'=' * 80}")
    print(f"{entity_type.upper()} COMPARISON")
    print("=" * 80)

    if not old_path.exists():
        print(f"❌ OLD file not found: {old_path}")
        return

    if not new_path.exists():
        print(f"❌ NEW file not found: {new_path}")
        return

    # Load files
    df_old = pd.read_parquet(old_path)
    df_new = pd.read_parquet(new_path)

    # Basic info
    print(f"\n📊 BASIC INFO:")
    print(f"  OLD: {len(df_old):,} rows × {len(df_old.columns)} cols | {old_path.stat().st_size / 1024:.1f} KB")
    print(f"  NEW: {len(df_new):,} rows × {len(df_new.columns)} cols | {new_path.stat().st_size / 1024:.1f} KB")

    # Row comparison
    print(f"\n📈 ROWS:")
    if len(df_old) == len(df_new):
        print(f"  ✅ IDENTICAL row count: {len(df_old):,}")
    else:
        print(f"  ⚠️  DIFFERENT: {len(df_old):,} → {len(df_new):,} ({len(df_new) - len(df_old):+,})")

    # Column comparison
    print(f"\n📋 COLUMNS:")
    old_cols = set(df_old.columns)
    new_cols = set(df_new.columns)

    if old_cols == new_cols:
        print(f"  ✅ IDENTICAL columns: {len(df_old.columns)}")
    else:
        removed = old_cols - new_cols
        added = new_cols - old_cols

        if removed:
            print(f"  ❌ REMOVED ({len(removed)}): {sorted(removed)}")
        if added:
            print(f"  ✅ ADDED ({len(added)}): {sorted(added)}")

    # Data comparison (first 5 rows, common columns)
    common_cols = sorted(old_cols & new_cols)

    if len(common_cols) > 0 and len(df_old) > 0 and len(df_new) > 0:
        print(f"\n🔬 DATA COMPARISON (first 5 rows, sample columns):")

        # Sample columns to check (avoid too many)
        check_cols = ['symbol', 'report_date', 'year', 'quarter']
        metric_cols = [c for c in common_cols if c not in check_cols][:5]
        check_cols += metric_cols
        check_cols = [c for c in check_cols if c in common_cols]

        # Compare first 5 rows
        df_old_sample = df_old[check_cols].head(5).reset_index(drop=True)
        df_new_sample = df_new[check_cols].head(5).reset_index(drop=True)

        # Check if identical
        try:
            if df_old_sample.equals(df_new_sample):
                print(f"  ✅ FIRST 5 ROWS IDENTICAL")
            else:
                print(f"  ⚠️  DIFFERENCES FOUND:")
                # Find differences
                for col in check_cols:
                    if col in df_old_sample.columns and col in df_new_sample.columns:
                        diff = (df_old_sample[col] != df_new_sample[col])
                        if diff.any():
                            print(f"\n    Column '{col}' has differences:")
                            print(f"      OLD: {df_old_sample[col][diff].tolist()}")
                            print(f"      NEW: {df_new_sample[col][diff].tolist()}")
        except Exception as e:
            print(f"  ⚠️  Cannot compare: {e}")

    # Dtypes comparison
    print(f"\n🔤 DATA TYPES:")
    dtype_changes = []
    for col in common_cols:
        if str(df_old[col].dtype) != str(df_new[col].dtype):
            dtype_changes.append((col, df_old[col].dtype, df_new[col].dtype))

    if len(dtype_changes) == 0:
        print(f"  ✅ All data types IDENTICAL")
    else:
        print(f"  ⚠️  CHANGES ({len(dtype_changes)}):")
        for col, old_dtype, new_dtype in dtype_changes[:10]:
            print(f"    {col}: {old_dtype} → {new_dtype}")

    # Summary statistics for numeric columns
    print(f"\n📊 SUMMARY STATS (sample numeric columns):")
    numeric_cols = df_old.select_dtypes(include=[np.number]).columns
    sample_numeric = [c for c in numeric_cols if c in common_cols][:3]

    if sample_numeric:
        for col in sample_numeric:
            old_mean = df_old[col].mean()
            new_mean = df_new[col].mean()
            old_std = df_old[col].std()
            new_std = df_new[col].std()

            mean_diff = abs(old_mean - new_mean) if pd.notna(old_mean) and pd.notna(new_mean) else None

            print(f"\n  {col}:")
            if mean_diff is not None:
                print(f"    Mean: {old_mean:.2f} → {new_mean:.2f} (Δ={mean_diff:.4f})")
            else:
                print(f"    Mean: {old_mean:.2f} → {new_mean:.2f} (Δ=N/A)")
            print(f"    Std:  {old_std:.2f} → {new_std:.2f}")

            if mean_diff is not None and mean_diff < 0.01:
                print(f"    ✅ VIRTUALLY IDENTICAL")
            elif mean_diff is not None:
                print(f"    ⚠️  SIGNIFICANT CHANGE")

# Compare Company
compare_parquet(company_old, company_new, "company")

# Compare Bank
compare_parquet(bank_old, bank_new, "bank")

print("\n" + "=" * 80)
print("OVERALL CONCLUSION")
print("=" * 80)
print("""
⚠️  IMPORTANT NOTES:

1. Formulas (company_formulas.py, bank_formulas.py) đã được tạo NHƯNG:
   → Calculators CHƯA sử dụng chúng
   → Calculators vẫn dùng logic cũ (inline calculations)

2. Nếu files OLD và NEW GIỐNG NHAU:
   → ✅ Đúng như dự kiến (vì formulas chưa được integrate)
   → Output không thay đổi

3. Nếu files OLD và NEW KHÁC NHAU:
   → ⚠️  Có thể do:
      - Calculator được chạy với data mới hơn
      - Logic calculation thay đổi (không nên xảy ra)
      - Data source thay đổi

4. ĐỂ SỬ DỤNG FORMULAS MỚI:
   → Cần update calculators để import và dùng formulas
   → Sau đó chạy lại sẽ cho kết quả GIỐNG HỆT (vì logic giống)

5. VALUATION FORMULAS:
   → Đã được tạo hoàn chỉnh (PE, PB, EV/EBITDA, ...)
   → Sẵn sàng để integrate vào valuation calculators
""")
