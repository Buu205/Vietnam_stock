# Phân Tích Dữ Liệu Q2 2025 - Company Financial Metrics

## 📊 Tổng Quan

**Ngày phân tích:** 2025-01-XX  
**File:** `calculated_results/fundamental/company/company_financial_metrics.parquet`

## ⚠️ VẤN ĐỀ PHÁT HIỆN

### 1. Input Data Q2 2025 Bị Thiếu Nghiêm Trọng

| Metric Code | Q1 2025 | Q2 2025 | Q3 2025 | Ghi Chú |
|-------------|---------|---------|---------|---------|
| **CIS_10** (Net Revenue) | 379 records | **190 records** ⚠️ | 365 records | Q2 chỉ có ~50% so với Q1 |
| **CBS_338** (Long-term Debt) | 379 records | **149 records** ⚠️ | 292 records | Q2 chỉ có ~39% so với Q1 |
| **CCFI_20** (Operating CF) | 328 records | **155 records** ⚠️ | 318 records | Q2 chỉ có ~47% so với Q1 |

### 2. Null Values trong Output Calculated

| Metric | Q1 2025 | Q2 2025 | Q3 2025 |
|--------|---------|---------|---------|
| **lt_debt** | 10.1% null | **22.5% null** ⚠️ | 21.3% null |
| **st_debt** | 3.7% null | **6.6% null** | 9.3% null |
| **operating_cf** | 13.8% null | 13.5% null | 14.7% null |
| **net_revenue** | 0.5% null | 0.5% null | 1.9% null |

## 📈 Chi Tiết Null Values Q2 2025

### Income Statement Core Metrics ✅
- **net_revenue**: 376/378 có data (0.5% null) - **TỐT**
- **gross_profit**: 376/378 có data (0.5% null) - **TỐT**
- **ebit**: 378/378 có data (0.0% null) - **TỐT**
- **ebitda**: 378/378 có data (0.0% null) - **TỐT**
- **npatmi**: 378/378 có data (0.0% null) - **TỐT**

### Balance Sheet Metrics ⚠️
- **total_assets**: 378/378 có data (0.0% null) - **TỐT**
- **cash**: 378/378 có data (0.0% null) - **TỐT**
- **inventory**: 372/378 có data (1.6% null) - **TỐT**
- **st_debt**: 353/378 có data (6.6% null) - **CẢNH BÁO**
- **lt_debt**: 293/378 có data (22.5% null) - **VẤN ĐỀ**

### Cash Flow Metrics ⚠️
- **operating_cf**: 327/378 có data (13.5% null) - **VẤN ĐỀ**
- **inv_cf**: 326/378 có data (13.8% null) - **VẤN ĐỀ**
- **capex**: 326/378 có data (13.8% null) - **VẤN ĐỀ**
- **fin_cf**: 326/378 có data (13.8% null) - **VẤN ĐỀ**
- **fcf**: 327/378 có data (13.5% null) - **VẤN ĐỀ**

### Symbols Có Vấn Đề

**Symbols không có IS data:**
- `PV2`: Thiếu net_revenue, gross_profit
- `VHG`: Thiếu net_revenue, gross_profit

**Symbols thiếu nhiều metrics:**
- Nhiều symbols không có long-term debt (có thể bình thường)
- Nhiều symbols không có cash flow data (có thể do chưa công bố)

## 🔍 Nguyên Nhân

1. **Input data thiếu**: Source data trong `data_warehouse/raw/fundamental/processed/company_full.parquet` cho Q2 2025 không đầy đủ
   - Q2 chỉ có 375 symbols (Q1 có 380, Q3 có 372)
   - Nhiều metric codes không có đủ records trong Q2

2. **Logic tính toán đúng**: Code tính toán đúng, null values xuất hiện do input data thiếu

3. **Có thể do:**
   - Dữ liệu Q2 2025 chưa được cập nhật đầy đủ từ source
   - Nhiều công ty chưa công bố báo cáo Q2 2025
   - Lỗi trong quá trình import/process Q2 2025 data

## 💡 Đề Xuất Giải Pháp

1. **Kiểm tra source data:**
   - Xem lại quá trình import/update dữ liệu Q2 2025
   - Đảm bảo tất cả symbols đã được cập nhật

2. **So sánh với các quý khác:**
   - Q1 2025 có đầy đủ hơn → tham khảo cách xử lý Q1
   - Q3 2025 cũng tốt hơn → tham khảo cách xử lý Q3

3. **Cải thiện xử lý null:**
   - Xem xét fill forward từ quý trước nếu có thể
   - Hoặc đánh dấu rõ ràng data nào là thực tế thiếu

4. **Kiểm tra lại pipeline update:**
   - Xem lại script update fundamental data
   - Đảm bảo Q2 2025 được cập nhật đầy đủ

## 📝 Kết Luận

- **Income Statement metrics** hoạt động tốt (99%+ có data)
- **Balance Sheet và Cash Flow metrics** có nhiều null do input data thiếu
- **Vấn đề chính**: Input data Q2 2025 không đầy đủ, cần kiểm tra lại source data và pipeline update








