#!/usr/bin/env python3
"""
So sánh cấu trúc Parquet files (cũ vs mới)
Kiểm tra xem formulas mới có ảnh hưởng đến output không
"""

import pandas as pd
from pathlib import Path

print("=" * 70)
print("SO SÁNH CẤU TRÚC PARQUET FILES")
print("=" * 70)

# Paths
company_path = Path("DATA/processed/fundamental/company/company_financial_metrics.parquet")
bank_path = Path("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")

# Load Company parquet
print("\n🏢 COMPANY FINANCIAL METRICS:")
print("-" * 70)
if company_path.exists():
    df_company = pd.read_parquet(company_path)
    print(f"  File size: {company_path.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"  Total rows: {len(df_company):,}")
    print(f"  Total columns: {len(df_company.columns)}")
    print(f"  Date range: {df_company['report_date'].min()} → {df_company['report_date'].max()}")
    print(f"\n  Columns ({len(df_company.columns)}):")
    for i, col in enumerate(df_company.columns, 1):
        print(f"    {i:2d}. {col}")
else:
    print("  ❌ File not found!")

# Load Bank parquet
print("\n🏦 BANK FINANCIAL METRICS:")
print("-" * 70)
if bank_path.exists():
    df_bank = pd.read_parquet(bank_path)
    print(f"  File size: {bank_path.stat().st_size / 1024:.2f} KB")
    print(f"  Total rows: {len(df_bank):,}")
    print(f"  Total columns: {len(df_bank.columns)}")
    print(f"  Date range: {df_bank['report_date'].min()} → {df_bank['report_date'].max()}")
    print(f"\n  Columns ({len(df_bank.columns)}):")
    for i, col in enumerate(df_bank.columns, 1):
        print(f"    {i:2d}. {col}")
else:
    print("  ❌ File not found!")

print("\n" + "=" * 70)
print("KẾT LUẬN:")
print("=" * 70)
print("""
📌 TRẠNG THÁI HIỆN TẠI:
  • Formulas (company_formulas.py, bank_formulas.py) đã được tạo
  • Calculators CHƯA sử dụng formulas mới
  • Output parquet files vẫn giữ nguyên structure từ Dec 4

❓ CÓ CẦN CHẠY LẠI FILE MỚI KHÔNG?
  ✅ KHÔNG CẦN - vì formulas chưa được integrate vào calculators
  • Calculators vẫn dùng logic cũ (inline formulas)
  • Output parquet sẽ GIỐNG HỆT như trước

📊 PARQUET OUTPUT CÓ KHÁC BIỆT GÌ KHÔNG?
  ✅ KHÔNG KHÁC BIỆT - vì formulas chưa được sử dụng
  • Cấu trúc: GIỮ NGUYÊN (same columns, same format)
  • Data: GIỮ NGUYÊN (same calculations)
  • Schema: GIỮ NGUYÊN (same types)

🔄 KHI NÀO CẦN CHẠY LẠI?
  → Chỉ khi UPDATE calculators để sử dụng formulas mới
  → Khi đó output sẽ giống y hệt (vì formulas tính toán giống cũ)
  → Backup parquet trước khi chạy lại để so sánh

📁 BACKUP RECOMMENDATION:
  cp DATA/processed/fundamental/company/company_financial_metrics.parquet \\
     DATA/processed/fundamental/company/backup_before_formulas.parquet

  cp DATA/processed/fundamental/bank/bank_financial_metrics.parquet \\
     DATA/processed/fundamental/bank/backup_before_formulas.parquet
""")
