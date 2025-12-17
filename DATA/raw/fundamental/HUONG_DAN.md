# Hướng Dẫn Chuyển Đổi Dữ Liệu Fundamental

## Quy Trình Cập Nhật Dữ Liệu

### Bước 1: Chuẩn Bị File CSV

Đặt file CSV vào thư mục: `DATA/raw/fundamental/csv/Q3_2025/`

**File cần có:**
- COMPANY_BALANCE_SHEET.csv
- COMPANY_INCOME.csv
- COMPANY_CF_DIRECT.csv
- COMPANY_CF_INDIRECT.csv
- COMPANY_NOTE.csv
- (Tương tự cho BANK_, INSURANCE_, SECURITY_)

### Bước 2: Chuyển CSV → Full Parquet

```bash
python3 PROCESSORS/fundamental/csv_to_full_parquet.py
```

**Output:**
- `DATA/processed/fundamental/company_full.parquet`
- `DATA/processed/fundamental/bank_full.parquet`
- `DATA/processed/fundamental/insurance_full.parquet`
- `DATA/processed/fundamental/security_full.parquet`

### Bước 3: Tính Toán Chỉ Số Tài Chính

```bash
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py
```

**Output:**
- `DATA/processed/fundamental/company/company_financial_metrics.parquet`
- `DATA/processed/fundamental/bank/bank_financial_metrics.parquet`
- `DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet`
- `DATA/processed/fundamental/security/security_financial_metrics.parquet`

## Chạy Nhanh (2 Lệnh)

```bash
# Chuyển CSV → Parquet
python3 PROCESSORS/fundamental/csv_to_full_parquet.py

# Tính toán chỉ số
python3 PROCESSORS/fundamental/calculators/run_all_calculators.py
```

## Kiểm Tra Kết Quả

```python
import pandas as pd

# Kiểm tra company data
df = pd.read_parquet('DATA/processed/fundamental/company/company_financial_metrics.parquet')
print(f"Rows: {len(df):,}")
print(f"Tickers: {df['symbol'].nunique()}")
print(f"Date range: {df['report_date'].min()} to {df['report_date'].max()}")

# Xem VNM
vnm = df[df['symbol'] == 'VNM'].sort_values('report_date', ascending=False).head(1)
print(vnm[['symbol', 'report_date', 'net_revenue', 'roe', 'roa']])
```

## Cấu Trúc Metric Code

| Entity | Balance Sheet | Income | Cash Flow | Notes |
|--------|--------------|--------|-----------|-------|
| COMPANY | CBS_* | CIS_* | CCFI_*/CCFD_* | CNOT_* |
| BANK | BBS_* | BIS_* | BCFI_*/BCFD_* | BNOT_* |
| INSURANCE | IBS_* | IIS_* | ICFI_*/ICFD_* | INOT_* |
| SECURITY | SBS_* | SIS_* | SCFI_*/SCFD_* | SNOT_* |

## Chỉ Số Quan Trọng

| Chỉ Số | COMPANY | BANK |
|--------|---------|------|
| Doanh thu | CIS_10 | BIS_14A (TOI) |
| Lợi nhuận ròng | CIS_61 (NPATMI) | BIS_22A (NPATMI) |
| Tổng tài sản | CBS_270 | BBS_100 |
| Vốn chủ sở hữu | CBS_400 | BBS_400 |

## Lưu Ý

1. File CSV phải có cột `SECURITY_CODE`, `REPORT_DATE`, `FREQ_CODE`
2. Metric codes làm cột (wide format)
3. Script tự động chuyển sang long format (METRIC_CODE, METRIC_VALUE)
4. Chạy 2 lệnh theo thứ tự (csv → parquet → calculators)

---
Cập nhật: 2025-12-16
