# Gói Cơ Bản Các Bộ Tính Toán Tài Chính (Financial Calculators Base Package)

## Tổng Quan (Overview)

Gói này chứa các bộ tính toán tài chính đã được tái cấu trúc, kế thừa từ `BaseFinancialCalculator` để giảm thiểu việc lặp lại mã nguồn lên đến 60%, tuân theo kiến trúc được định nghĩa trong:
- `/docs/MASTER_PLAN.md` - Thực hiện Giai đoạn 0.2
- `/docs/architecture/DATA_STANDARDIZATION.md` - Tái cấu trúc Bộ tính toán Thống nhất
- `/docs/ARCHITECTURE_SUMMARY.md` - Tổng quan kiến trúc hệ thống

### Tuân Thủ Kiến Trúc (Architecture Compliance)

✅ **Không thao tác sys.path** - Sử dụng imports tương đối như khuyến nghị trong kiến trúc tổng quan
✅ **Mẫu Template Method** - BaseFinancialCalculator triển khai các chức năng chung
✅ **Tính Toán Đặc Thù Theo Thực Thể** - Mỗi bộ tính toán triển khai các chỉ số chuyên biệt
✅ **Tích Hợp Metric Registry** - Kiểm tra hợp lệ với metric_registry.json
✅ **Tích Hợp UnifiedTickerMapper** - Tự động chọn bộ tính toán theo mã chứng khoán
✅ **Đầu Ra Chuẩn Hóa** - Đặt tên cột và định dạng ngày tháng nhất quán

## Kiến Trúc (Architecture)

```
BaseFinancialCalculator (Lớp Cơ Sở Trừu Tượng)
├── CompanyFinancialCalculator (390 doanh nghiệp)
├── BankFinancialCalculator (24 ngân hàng)
├── InsuranceFinancialCalculator (6 công ty bảo hiểm)
└── SecurityFinancialCalculator (37 công ty chứng khoán)
```

## Tính Năng Chính (Key Features)

1. **Lớp Cơ Sở Chia Sẻ**: Các chức năng chung như tải dữ liệu, xoay trục (pivoting), tính toán tăng trưởng
2. **Logic Đặc Thù Thực Thể**: Mỗi bộ tính toán triển khai các phép tính chuyên biệt
3. **Tích Hợp Metric Registry**: Xác thực các chỉ số với `metric_registry.json`
4. **Unified Ticker Mapper**: Tự động chọn bộ tính toán theo mã chứng khoán
5. **Đầu Ra Chuẩn Hóa**: Tên cột và định dạng dữ liệu nhất quán

## Cài Đặt (Installation)

```python
# Cài đặt gói (nếu cần)
pip install -e /path/to/stock_dashboard
```

## Ví Dụ Sử Dụng (Usage Examples)

### 1. Tính toán chỉ số cho một mã cụ thể

```python
from data_processor.fundamental.base import (
    UnifiedTickerMapper,
    CompanyFinancialCalculator,
    BankFinancialCalculator,
    InsuranceFinancialCalculator,
    SecurityFinancialCalculator
)
# ... imports khác ...

# Khởi tạo mapper
mapper = UnifiedTickerMapper()

# Lấy loại thực thể cho mã
ticker = "ACB"
entity_type = mapper.get_entity_type(ticker)  # Trả về "BANK"

# Chọn bộ tính toán phù hợp
calculators = {
    "COMPANY": CompanyFinancialCalculator,
    "BANK": BankFinancialCalculator,
    "INSURANCE": InsuranceFinancialCalculator,
    "SECURITY": SecurityFinancialCalculator
}

calculator_class = calculators[entity_type]
calculator = calculator_class(data_path)

# Tính toán chỉ số
results = calculator.calculate_all_metrics(ticker)
print(results)
```

### 2. Tính toán chỉ số toàn ngành

```python
# Lấy tất cả mã cho một loại thực thể
entity_type = "BANK"
tickers = mapper.sector_registry.get_tickers_by_entity_type(entity_type)

# Tính toán cho tất cả ngân hàng
calculator = BankFinancialCalculator(bank_data_path)
all_results = calculator.calculate_all_metrics()  # Tính cho tất cả mã

# Lấy NIM cho toàn ngành
nim_data = all_results[['symbol', 'report_date', 'nim_q']]
print(nim_data)
```

### 3. So sánh với đối thủ (Compare peers)

```python
# Lấy thông tin đối thủ cho một mã
ticker = "VCB"
peer_info = mapper.get_peer_comparison_info(ticker)

# Lấy danh sách mã đối thủ
peer_tickers = peer_info['peer_tickers']

# Tính toán chỉ số để so sánh
calculator = BankFinancialCalculator(bank_data_path)
results = calculator.calculate_all_metrics()

# Lọc VCB và các đối thủ
comparison_symbols = [ticker] + peer_tickers
comparison_data = results[results['symbol'].isin(comparison_symbols)]

# Lấy quý mới nhất
latest_date = comparison_data['report_date'].max()
latest_data = comparison_data[comparison_data['report_date'] == latest_date]

# So sánh ROE
vcb_roe = latest_data[latest_data['symbol'] == "VCB"]["roea_ttm"].values[0]
peer_avg_roe = latest_data[latest_data['symbol'] != "VCB"]["roea_ttm"].mean()

print(f"VCB ROE: {vcb_roe:.2f}%")
print(f"Peer Average ROE: {peer_avg_roe:.2f}%")
```

## Kiểm Thử (Testing)

Chạy bài kiểm tra tích hợp để xác minh tất cả bộ tính toán hoạt động chính xác:

```bash
python data_processor/fundamental/base/calculator_integration_test.py
```

## Các Bộ Tính Toán Có Sẵn (Available Calculators)

| Bộ Tính Toán | Loại Thực Thể | Số Lượng | Chỉ Số Chính |
|------------|--------------|--------|--------------|
| CompanyFinancialCalculator | COMPANY | 390 | Doanh thu, Biên lợi nhuận, ROE, EPS |
| BankFinancialCalculator | BANK | 24 | NIM, LDR, ROEA, CAR |
| InsuranceFinancialCalculator | INSURANCE | 6 | Combined Ratio, Loss Ratio, Solvency |
| SecurityFinancialCalculator | SECURITY | 37 | Tỷ lệ Môi giới, Tự doanh |

## Luồng Dữ Liệu (Data Flow)

1. **Dữ Liệu Thô**: File Parquet với dữ liệu cơ bản dạng dài (long-format)
2. **Tải Dữ Liệu**: `BaseFinancialCalculator.load_data()`
3. **Xoay Trục**: `BaseFinancialCalculator.pivot_data()` chuyển đổi sang dạng rộng (wide format)
4. **Tính Toán Đặc Thù**: `get_entity_specific_calculations()` của từng bộ tính toán
5. **Hậu Xử Lý**: Chuẩn hóa tên cột và định dạng ngày tháng
6. **Đầu Ra**: DataFrame sạch sẵn sàng cho phân tích hoặc sử dụng bởi MCP

## Tích Hợp với MCP (Integration with MCP)

Các bộ tính toán đã tái cấu trúc được thiết kế để hoạt động liền mạch với máy chủ Model Context Protocol (MCP).

## Phát Triển (Development)

Để mở rộng hoặc sửa đổi các bộ tính toán:

1. **Thêm Chỉ Số Mới**: Cập nhật `get_entity_specific_calculations()`
2. **Thêm Phép Tính Mới**: Triển khai các phương thức mới theo mẫu
3. **Đăng Ký Chỉ Số**: Thêm vào metric_registry.json nếu cần
4. **Cập Nhật Kiểm Thử**: Thêm bài kiểm tra cho chức năng mới

## Tuân Thủ Kiến Trúc (Architecture Compliance)

Các bộ tính toán này tuân theo kiến trúc được đề ra trong:
- `/docs/MASTER_PLAN.md`
- `/docs/architecture/DATA_STANDARDIZATION.md`
- `/docs/ARCHITECTURE_SUMMARY.md`

Chúng triển khai Giai đoạn 0.2 của lộ trình chuẩn hóa dữ liệu.
