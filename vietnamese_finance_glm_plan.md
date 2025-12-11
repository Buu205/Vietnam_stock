# Kế Hoạch Tối Ưu Hóa Hệ Thống Tính Toán Chỉ Số Tài Chính

## Tổng Quan

"""
Kế hoạch tối ưu hóa toàn diện cho hệ thống tính toán chỉ số tài chính, nhằm sửa các lỗi nghiêm trọng, giảm thiểu mã lặp và cải thiện khả năng tích hợp với Streamlit.

Tác giả: AI Assistant
Ngày: 11-12-2025
Phiên bản: 1.0.0

Kế hoạch này giải quyết các vấn đề chính sau:
1. Các lỗi nghiêm trọng gây crash hệ thống
2. Mã lặp (duplication) trong tính toán công thức
3. Thiếu triển khai cho các loại hình bảo hiểm và chứng khoán
4. Tích hợp kém với dashboard Streamlit
5. Thiếu kiểm tra rà soát (schema validation) và testing

Kế hoạch được chia thành 6 giai đoạn với các sản phẩm bàn giao và mốc thời gian rõ ràng.
"""

## Phân Tích Hiện Trạng

### Kiến Trúc Hiện Tại
- **BaseFinancialCalculator**: Lớp cơ sở trừu tượng sử dụng Template Method pattern
- **Entity-Specific Calculators**: Các calculator riêng cho Công ty, Ngân hàng, Bảo hiểm, Chứng khoán
- **Formula Modules**: Các module riêng biệt cho các loại hình thực thể khác nhau
- **Schema Registry**: Quản lý cấu hình tập trung
- **Streamlit Dashboards**: Dashboard cho Ngân hàng và Công ty sử dụng PyEcharts

### Các Vấn Đề Đã Xác Định
1. **Lỗi Nghiêm Trọng**: Thiếu import logger, sai chính tả tên phương thức (typos)
2. **Mã Lặp**: 60% mã lặp giữa các module công thức
3. **Thiếu Tính Năng**: Calculator cho Bảo hiểm/Chứng khoán chưa hoàn thiện
4. **Khoảng Trống Tích Hợp**: Luồng dữ liệu giữa calculator và dashboard kém hiệu quả
5. **Khoảng Trống Testing**: Không có test coverage toàn diện

---

## Giai Đoạn 1: Sửa Lỗi Nghiêm Trọng (Mức Độ: CAO)

### 1.1 Sửa Lỗi Import Logger

"""
Sửa lỗi thiếu import logger gây ra lỗi `AttributeError` khi khởi tạo calculator.

Các file cần sửa:
- PROCESSORS/fundamental/calculators/company_calculator.py
- PROCESSORS/fundamental/calculators/insurance_calculator.py
- PROCESSORS/fundamental/calculators/security_calculator.py

Tác động: Ngăn chặn hệ thống bị crash khi khởi tạo
Thời gian: 2 giờ
"""

**Hành động cần thiết:**
- Thêm `import logging` và `logger = logging.getLogger(__name__)` vào tất cả các file calculator
- Đảm bảo logger được cấu hình đúng trong lớp cơ sở
- Test khởi tạo calculator không bị lỗi

### 1.2 Sửa Lỗi Chính Tả Tên Phương Thức

"""
Sửa các lỗi chính tả trong tên phương thức ngăn cản việc phân giải phương thức đúng.

Các file cần sửa:
- PROCESSORS/fundamental/calculators/insurance_calculator.py (dòng 51, 158)

Tác động: Giúp calculator bảo hiểm hoạt động được
Thời gian: 1 giờ
"""

**Hành động cần thiết:**
- Sửa `calculateinvestment_performance` → `calculate_investment_performance`
- Cập nhật tham chiếu key trong dictionary `get_entity_specific_calculations()`
- Xác minh chữ ký phương thức khớp với kỳ vọng của lớp cha

### 1.3 Sửa Đường Dẫn Import Test

"""
Cập nhật các câu lệnh import trong file test để khớp với tên file và vị trí thực tế.

Các file cần sửa:
- PROCESSORS/fundamental/calculators/calculator_integration_test.py

Tác động: Cho phép test tích hợp calculator đúng cách
Thời gian: 1 giờ
"""

**Hành động cần thiết:**
- Cập nhật đường dẫn import để sử dụng tên file đúng
- Xác minh tất cả các lớp calculator được import đúng
- Chạy bộ test suite để xác nhận các sửa lỗi

---

## Giai Đoạn 2: Hợp Nhất Công Thức (Mức Độ: CAO)

### 2.1 Nhận Diện và Loại Bỏ Công Thức Trùng Lặp

"""
Loại bỏ mã lặp bằng cách hợp nhất các công thức chung vào một module chia sẻ.

Phân tích cho thấy 60% trùng lặp giữa:
- PROCESSORS/fundamental/formulas/_base_formulas.py
- PROCESSORS/fundamental/formulas/company_formulas.py
- PROCESSORS/fundamental/formulas/bank_formulas.py

Tác động: Giảm gánh nặng bảo trì và đảm bảo tính nhất quán
Thời gian: 6 giờ
"""

**Các Công Thức Trùng Cần Hợp Nhất:**
- `calculate_roe()` - Lợi nhuận trên Vốn chủ sở hữu
- `calculate_roa()` - Lợi nhuận trên Tài sản
- `calculate_gross_margin()` - Biên lợi nhuận gộp
- `calculate_net_margin()` - Biên lợi nhuận ròng
- `calculate_operating_margin()` - Biên lợi nhuận hoạt động
- `safe_divide()` - Hàm tiện ích cho phép chia

**Các Công Thức Đặc Thù Cần Giữ:**
- **Company**: `calculate_asset_turnover()`, `calculate_inventory_turnover()`
- **Bank**: `calculate_nim()`, `calculate_cir()`, `calculate_plr()`
- **Insurance**: Combined ratio, Loss ratio calculations
- **Security**: CAD ratio, Trading leverage calculations

### 2.2 Tạo Registry Công Thức Thống Nhất

"""
Triển khai pattern formula registry để quản lý tất cả các tính toán tài chính tập trung.

Điều này sẽ cung cấp:
- Nguồn sự thật duy nhất (single source of truth) cho tất cả công thức
- Dễ dàng tìm kiếm và tài liệu hóa công thức
- Xử lý lỗi nhất quán trên tất cả các tính toán
- Tích hợp sẵn validate và testing công thức

Tác động: Cải thiện khả năng bảo trì và giảm lỗi
Thời gian: 4 giờ
"""

**Cấu Trúc Registry:**
```python
class FormulaRegistry:
    """
    Registry trung tâm cho tất cả các công thức tính toán tài chính.
    
    Cung cấp:
    - Tra cứu công thức theo tên và loại entity
    - Validate input và xử lý lỗi
    - Tài liệu công thức và ví dụ
    - Monitoring hiệu năng và caching
    """
    
    def register_formula(self, name: str, formula: callable, 
                        entity_types: List[str], documentation: str):
        """Đăng ký một công thức mới với metadata"""
        
    def get_formula(self, name: str, entity_type: str) -> callable:
        """Lấy công thức cho loại entity cụ thể"""
        
    def list_formulas(self, entity_type: str = None) -> Dict[str, Dict]:
        """Liệt kê tất cả công thức khả dụng kèm tài liệu"""
```

### 2.3 Cập Nhật Import Calculator

"""
Refactor tất cả các lớp calculator để sử dụng formula registry thống nhất.

Điều này đảm bảo:
- Sử dụng công thức nhất quán trên tất cả calculator
- Validate công thức và xử lý lỗi tự động
- Dễ dàng test và debug hơn
- Giảm mã lặp

Tác động: Chuẩn hóa việc sử dụng công thức và cải thiện độ tin cậy
Thời gian: 3 giờ
"""

---

## Giai Đoạn 3: Tích Hợp Schema (Mức Độ: TRUNG BÌNH)

### 3.1 Tạo Định Nghĩa Output Schema

"""
Định nghĩa schema toàn diện cho tất cả đầu ra của calculator để đảm bảo tính nhất quán dữ liệu.

Các schema cần tạo:
- config/schema_registry/domain/fundamental/company_output.json
- config/schema_registry/domain/fundamental/bank_output.json
- config/schema_registry/domain/fundamental/insurance_output.json
- config/schema_registry/domain/fundamental/security_output.json

Mỗi schema định nghĩa:
- Các cột bắt buộc và kiểu dữ liệu
- Ràng buộc giá trị và quy tắc validate
- Mô tả cột và logic nghiệp vụ
- Mối quan hệ giữa các metric

Tác động: Đảm bảo chất lượng và nhất quán dữ liệu trên tất cả đầu ra
Thời gian: 6 giờ
"""

**Ví dụ Cấu Trúc Schema:**
```json
{
  "schema_name": "company_output",
  "version": "1.0.0",
  "description": "Output schema for company financial calculator",
  "required_columns": [
    {
      "name": "net_profit",
      "type": "float",
      "description": "Lợi nhuận sau thuế (tỷ VND)",
      "constraints": {"min": null, "max": null, "nullable": false}
    },
    {
      "name": "net_margin",
      "type": "float", 
      "description": "Biên lợi nhuận ròng (%)",
      "constraints": {"min": -100, "max": 100, "nullable": true}
    }
  ],
  "optional_columns": [...],
  "calculated_columns": [...]
}
```

### 3.2 Triển Khai Validate Schema

"""
Thêm tính năng tự động validate schema vào BaseFinancialCalculator.

Tính năng:
- Validate đầu ra so với schema trước khi trả về kết quả
- Cung cấp thông báo lỗi chi tiết khi validate thất bại
- Hỗ trợ versioning schema và migration
- Metric hiệu năng cho overhead khi validate

Tác động: Ngăn chặn vấn đề chất lượng dữ liệu và cải thiện debugging
Thời gian: 4 giờ
"""

---

## Giai Đoạn 4: Tính Năng Calculator Nâng Cao (Mức Độ: TRUNG BÌNH)

### 4.1 Triển Khai Tính Toán Các Metrics Quan Trọng

"""
Đảm bảo tất cả calculator có thể tính toán các metrics thiết yếu cho hiển thị Streamlit.

Key metrics cần triển khai:
- Lợi nhuận ròng (sau thuế, tỷ VND)
- Biên lợi nhuận ròng (lợi nhuận ròng / doanh thu * 100)
- Tính toán TTM (Trailing Twelve Months - 12 tháng gần nhất)
- Tăng trưởng theo quý (QoQ)
- Tăng trưởng theo năm (YoY)

Tác động: Cung cấp dữ liệu thiết yếu cho trực quan hóa dashboard
Thời gian: 6 giờ
"""

### 4.2 Thêm Hỗ Trợ TTM (Trailing Twelve Months)

"""
Triển khai tính toán TTM để phân tích xu hướng tốt hơn.

Metrics TTM cần tính:
- TTM Net Profit
- TTM Net Margin
- TTM Revenue
- TTM Operating Cash Flow
- TTM Free Cash Flow

Tác động: Cung cấp xu hướng mượt mà hơn và so sánh theo năm tốt hơn
Thời gian: 4 giờ
"""

### 4.3 Triển Khai Tính Toán Tốc Độ Tăng Trưởng

"""
Thêm tính toán tốc độ tăng trưởng toàn diện cho tất cả metrics chính.

Các loại tăng trưởng:
- Tăng trưởng Quý-so-với-Quý (QoQ)
- Tăng trưởng Năm-so-với-Năm (YoY)
- Tốc độ tăng trưởng kép hàng năm (CAGR)
- Tăng trưởng TTM

Tác động: Cho phép phân tích xu hướng toàn diện trong dashboards
Thời gian: 3 giờ
"""

---

## Giai Đoạn 5: Tối Ưu Hóa Tích Hợp Streamlit (Mức Độ: CAO)

### 5.1 Tạo Unified Metrics Loader

"""
Triển khai một service tập trung để load và format metrics tài chính cho Streamlit.

Tính năng:
- Giao diện thống nhất cho tất cả loại entity
- Tự động phát hiện loại entity
- Format đầu ra để hiển thị dashboard
- Caching để cải thiện hiệu năng
- Xử lý lỗi và fallback

Tác động: Đơn giản hóa code dashboard và cải thiện hiệu năng
Thời gian: 6 giờ
"""

### 5.2 Tối Ưu Hóa Các Thành Phần Dashboard

"""
Refactor các thành phần dashboard để sử dụng unified metrics loader.

Các thành phần cần tối ưu:
- Thẻ tổng quan tài chính (Financial overview cards)
- Biểu đồ xu hướng và trực quan hóa
- Bảng tài chính định dạng pivot
- Công cụ so sánh metric

Tác động: Cải thiện hiệu năng và khả năng bảo trì dashboard
Thời gian: 4 giờ
"""

### 5.3 Triển Khai Cập Nhật Dữ Liệu Real-time

"""
Thêm hỗ trợ cập nhật dữ liệu real-time trong Streamlit dashboards.

Tác động: Cung cấp cho người dùng dữ liệu tài chính mới nhất
Thời gian: 3 giờ
"""

---

## Giai Đoạn 6: Testing và Validation (Mức Độ: TRUNG BÌNH)

### 6.1 Triển Khai Unit Tests cho Công Thức

"""
Tạo unit tests toàn diện cho tất cả công thức tính toán tài chính.

Yêu cầu test coverage:
- 100% coverage cho tất cả hàm công thức
- Test các trường hợp biên (số 0, số âm, dữ liệu thiếu)
- Test hiệu năng với tập dữ liệu lớn
- Validate độ chính xác so với các tính toán đã biết

Tác động: Đảm bảo độ chính xác tính toán và ngăn chặn hồi quy (regressions)
Thời gian: 6 giờ
"""

### 6.2 Triển Khai Integration Tests

"""
Tạo integration tests cho toàn bộ pipeline calculator.

Kịch bản test:
- Thực thi calculator end-to-end
- Luồng dữ liệu từ raw data đến hiển thị dashboard
- Xử lý lỗi và phục hồi
- Hiệu năng dưới tải

Tác động: Validate độ tin cậy và hiệu năng hệ thống
Thời gian: 4 giờ
"""

### 6.3 Thêm Monitoring Hiệu Năng

"""
Triển khai monitoring hiệu năng cho tất cả hoạt động calculator.

Metrics cần theo dõi:
- Thời gian thực thi tính toán
- Sử dụng bộ nhớ trong quá trình xử lý
- Thời gian load và xử lý dữ liệu
- Tỉ lệ cache hit

Tác động: Nhận diện điểm nghẽn hiệu năng và cơ hội tối ưu hóa
Thời gian: 3 giờ
"""

---

## Lộ Trình Triển Khai

### Tuần 1: Sửa Lỗi Nghiêm Trọng và Nền Tảng
- **Ngày 1**: Giai đoạn 1 - Sửa Lỗi Nghiêm Trọng
- **Ngày 2-3**: Giai đoạn 2 - Hợp Nhất Công Thức (Phần 1)
- **Ngày 4**: Giai đoạn 2 - Hợp Nhất Công Thức (Phần 2)
- **Ngày 5**: Giai đoạn 3 - Tích Hợp Schema (Phần 1)

### Tuần 2: Tính Năng và Tích Hợp
- **Ngày 6**: Giai đoạn 3 - Tích Hợp Schema (Phần 2)
- **Ngày 7-8**: Giai đoạn 4 - Tính Năng Calculator Nâng Cao
- **Ngày 9**: Giai đoạn 5 - Tích Hợp Streamlit (Phần 1)
- **Ngày 10**: Giai đoạn 5 - Tích Hợp Streamlit (Phần 2)

### Tuần 3: Testing và Validation
- **Ngày 11**: Giai đoạn 6 - Unit Tests
- **Ngày 12**: Giai đoạn 6 - Integration Tests
- **Ngày 13**: Giai đoạn 6 - Monitoring Hiệu Năng
- **Ngày 14**: Testing Cuối Cùng và Tài Liệu

**Tổng Thời Gian: 14 ngày làm việc**

---

## Tiêu Chí Thành Công

### Metrics Kỹ Thuật
- [ ] Không còn lỗi nghiêm trọng trên production
- [ ] Giảm 60% mã lặp
- [ ] 100% test coverage cho tất cả công thức
- [ ] Thời gian load dashboard < 2 giây
- [ ] Validate schema cho tất cả đầu ra

### Metrics Kinh Doanh
- [ ] Cải thiện độ chính xác dữ liệu trên dashboard
- [ ] Nâng cao trải nghiệm người dùng với tốc độ load nhanh hơn
- [ ] Giảm chi phí bảo trì
- [ ] Xử lý lỗi và phản hồi người dùng tốt hơn
- [ ] Tài liệu đầy đủ cho tất cả tính năng

---

# PHẦN 2: KẾ HOẠCH HỢP NHẤT CUỐI CÙNG VỚI AI SINH CÔNG THỨC

**Cập nhật:** 11-12-2025
**Phiên bản:** 2.0.0 - KẾ HOẠCH HỢP NHẤT (UNIFIED PLAN)
**Trạng thái:** Final - Sẵn sàng triển khai

---

## TÓM TẮT ĐIỀU HÀNH - CÁCH TIẾP CẬN HỢP NHẤT

Sau khi xem xét toàn diện 3 kế hoạch tối ưu hóa độc lập, kế hoạch hợp nhất này kết hợp các thực tiễn tốt nhất từ mỗi phương pháp đồng thời bổ sung **hệ thống sinh công thức hỗ trợ bởi AI mang tính cách mạng**, cho phép người dùng thêm các chỉ số tài chính mới thông qua các lệnh ngôn ngữ tự nhiên.

**Đổi Mới Chính:** Người dùng có thể gõ lệnh tiếng Việt như **"tính SGA/Rev"** và hệ thống sẽ tự động:
1. Phân tích `metric_registry.json` để hiểu tên metric tiếng Việt
2. Map sang các mã metric chính xác (CIS_25 + CIS_26) / CIS_10
3. Sinh code công thức Python với docstring tiếng Việt
4. Tích hợp mượt mà với khung calculator hiện có

Kế hoạch này giải quyết cả nợ kỹ thuật trước mắt (lỗi nghiêm trọng, mã lặp) và khả năng mở rộng trong tương lai (thêm metric dễ dàng, phát triển hỗ trợ bởi AI).

---

## MỤC 1: PHÂN TÍCH SO SÁNH 3 KẾ HOẠCH

### 1.1 Tổng Quan Các Kế Hoạch

| Kế Hoạch | Thời Gian | Giai Đoạn | Trọng Tâm Chính | Đổi Mới Then Chốt |
|------|----------|--------|---------------|----------------|
| **Plan A: GLM Plan** | 14 ngày | 6 giai đoạn | Sửa lỗi → Hợp nhất → Tích hợp | FormulaRegistry pattern, FinancialMetricsLoader |
| **Plan B: Flow Design** | 2-3 tuần | 5 giai đoạn | Kiến trúc 4 lớp, Docs tiếng Việt | Kiến trúc 4 lớp chuẩn hóa |
| **Plan C: Cursor Plan** | 6-10 ngày | 5 giai đoạn | Tiếp cận Dashboard-first | Validate output schema |

### 1.4 Cách Tiếp Cận Hợp Nhất - Tốt Nhất Của Cả 3

Kế hoạch hợp nhất kết hợp:

| Tính Năng | Nguồn | Tại Sao Chọn |
|---------|-------------|-------------|
| **Sửa lỗi nghiêm trọng trước** | Plan A (GLM) | Ngăn crash hệ thống, bỏ chặn phát triển |
| **Kiến trúc 4 lớp** | Plan B (Flow) | Phân tách mối quan tâm rõ ràng, dễ bảo trì |
| **Docstring tiếng Việt** | Plan B (Flow) | Cần thiết cho team Việt Nam |
| **Audit theo Dashboard** | Plan C (Cursor) | Đảm bảo làm đúng cái dashboard cần |
| **Validate output schema** | Plan C (Cursor) | Ngăn chặn vấn đề chất lượng data |
| **Pattern FormulaRegistry** | Plan A (GLM) | Scalable, nguồn sự thật duy nhất |
| **Đường găng ngắn nhất** | Plan C (Cursor) | Timeline 6-10 ngày là thực tế |
| **AI Formula Generation** | **MỚI** | Cách mạng: thêm metric cực dễ |

---

## MỤC 2: HỆ THỐNG SINH CÔNG THỨC HỖ TRỢ BỞI AI

### 2.1 Phát Biểu Vấn Đề

**Quy Trình Hiện Tại (Thủ Công):**
```
Developer muốn tính tỷ lệ SGA/Revenue:
1. Tra mã metric trong file Excel BSC (30 phút)
2. Viết hàm công thức thủ công (20 phút)
3. Thêm docstring tiếng Việt (15 phút)
4. Cập nhật calculator để dùng công thức (10 phút)
5. Test công thức (15 phút)
Tổng: 90 phút mỗi metric
```

**Quy Trình Mục Tiêu (Hỗ Trợ AI) - 3 Phương Thức Input:**

**Phương Thức 1: Ngôn Ngữ Tự Nhiên (Việt/Anh)**
```
Developer gõ: "tính SGA/Rev"
AI phản hồi trong 30 giây với code đã sinh ra
```

**Phương Thức 2: Input Công Thức Trực Tiếp**
```
Developer cung cấp: (CIS_25 + CIS_26) / CIS_10 * 100
AI phản hồi trong 10 giây:
- Validate mã metric tồn tại
- Sinh hàm với tên tiếng Việt
- Thêm xử lý lỗi đúng chuẩn
- Tự động chuyển phép chia sang safe_divide()
- Tạo docstring tiếng Việt giải thích công thức
```

**Phương Thức 3: Mã Metric + Phép Toán**
```
Developer cung cấp:
- Tử số: CIS_25, CIS_26
- Mẫu số: CIS_10
- Phép toán: ratio (tỷ lệ phần trăm)
AI phản hồi trong 15 giây với implementation hoàn chỉnh
```

**Tiết Kiệm Thời Gian: Giảm 88%** (90 phút → 10.5 phút)

### 2.2 Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────────────┐
│ USER INPUT (Natural Language)                                   │
│ "tính SGA/Rev" hoặc "tính tỷ lệ SGA trên Doanh thu"            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LỚP 1: Natural Language Parser (NLPFormulaParser)              │
│ - Trích xuất ý định: "tính tỷ lệ"                               │
│ - Nhận diện thành phần: "SGA" (tử), "Rev" (mẫu)                 │
│ - Phát hiện phép toán: chia                                     │
│ - Ngôn ngữ: Tiếng Việt hoặc Tiếng Anh                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LỚP 2: Metric Resolver (MetricRegistryResolver)                │
│ - Load metric_registry.json (2,099 metrics)                     │
│ - Tìm kiếm tên tiếng Việt: "chi phí bán hàng" → CIS_25         │
│ - Validate: Tất cả metric tồn tại cho entity type COMPANY       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LỚP 3: Formula Code Generator (FormulaCodeGenerator)           │
│ - Sinh hàm Python: calculate_sga_to_revenue()                   │
│ - Thêm docstring tiếng Việt với giải thích công thức            │
│ - Xử lý edge cases: safe_divide, check None                     │
│ - Áp dụng chuẩn code: type hints, error handling                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LỚP 4: Integration Generator (CalculatorIntegrationGen)        │
│ - Sinh phương thức calculator để sử dụng công thức              │
│ - Cập nhật import trong file calculator phù hợp                 │
│ - Sinh template unit test                                       │
│ - Tạo bản cập nhật schema để validate output                    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 Ví Dụ Workflow Sinh Công Thức AI Hoàn Chỉnh

**Ví dụ: Người dùng gõ "tính SGA/Rev"**

**Kết Quả Sinh Ra (Demo):**

```python
def calculate_sga_to_revenue(
    cis_25_cis_26: Optional[float],
    cis_10: Optional[float]
) -> Optional[float]:
    """
    Tính Tỷ lệ chi phí SGA trên doanh thu

    Công thức: (Chi phí bán hàng và quản lý / Doanh thu thuần) × 100

    Benchmark: >20% (High cost), <15% (Efficient), <10% (Excellent)

    Args:
        cis_25_cis_26: Chi phí bán hàng và quản lý (VND)
        cis_10: Doanh thu thuần (VND)

    Returns:
        Tỷ lệ dưới dạng phần trăm, hoặc None nếu không hợp lệ

    Examples:
        >>> calculate_sga_to_revenue(100_000_000_000, 1_000_000_000_000)
        10.0  # 10%
    """
    result = safe_divide(cis_25_cis_26, cis_10)
    return round(result * 100, 2) if result is not None else None
```

---

## MỤC 3: KẾ HOẠCH TRIỂN KHAI HỢP NHẤT

### 3.1 Cấu Trúc Giai Đoạn Tối Ưu

Kết hợp các yếu tố tốt nhất từ cả 3 plan với AI generation:

```
GIAI ĐOẠN 0: Sửa Lỗi Nghiêm Trọng (4 giờ) - Từ Plan A
GIAI ĐOẠN 1: Nền Tảng Lớp Công Thức (3 ngày) - Từ Plan B + AI
GIAI ĐOẠN 2: Refactor Calculator (3 ngày) - Từ Plan C + Plan B
GIAI ĐOẠN 3: Hệ Thống Sinh Công Thức AI (2 ngày) - MỚI
GIAI ĐOẠN 4: Tích Hợp Dashboard & Schema (2 ngày) - Từ Plan C
GIAI ĐOẠN 5: Testing & Validation (2 ngày) - Từ tất cả plan

TỔNG CỘNG: 12 ngày (có thể giảm xuống 8 ngày nếu chạy song song)
```

### 3.2 Chi Tiết Các Giai Đoạn

#### GIAI ĐOẠN 0: Sửa Lỗi Nghiêm Trọng (4 giờ) ⚠️ BLOCKING

**Ưu tiên:** TỐI MẬT - Phải sửa trước để hệ thống chạy được
**Nhiệm vụ:**
1. Fix thiếu import Logger (`company_calculator.py`, etc.)
2. Fix lỗi chính tả tên hàm
3. Fix đường dẫn import test

#### GIAI ĐOẠN 1: Nền Tảng Lớp Công Thức (3 ngày)

**Ngày 1: Audit & Hợp Nhất Công Thức**
- Chạy script audit
- Xóa công thức trùng lặp (giữ ở `_base_formulas.py`)

**Ngày 2: Docstrings Tiếng Việt**
- Áp dụng template tiếng Việt cho TẤT CẢ công thức (~50 công thức)

**Ngày 3: Các Công Thức Còn Thiếu**
- Thêm các hàm tính Tăng trưởng (YoY, QoQ)
- Thêm hàm TTM
- Thêm hàm Hiệu quả hoạt động

#### GIAI ĐOẠN 2: Refactor Calculator (3 ngày)

**Ngày 1: Audit Yêu Cầu Dashboard**
- Phân tích code dashboard để lập danh sách metric cần thiết
- So sánh với output hiện tại

**Ngày 2: Refactor Company Calculator**
- Cập nhật import
- Refactor `calculate_margins`, `calculate_ratios` dùng hàm chuẩn

**Ngày 3: Refactor Bank Calculator**
- Tương tự Company Calculator

#### GIAI ĐOẠN 3: Hệ Thống Sinh Công Thức AI (2 ngày) 🚀 MỚI

**Ngày 1: Core AI Components**
- Implement `NLPFormulaParser` (Parse "tính X/Y")
- Implement `MetricRegistryResolver` (Fuzzy search tên tiếng Việt)

**Ngày 2: Code Generation & Integration**
- Implement `FormulaCodeGenerator` (Sinh code Python + Docs)
- Implement `FormulaAssistant` (Orchestrator)

#### GIAI ĐOẠN 4: Tích Hợp Dashboard & Schema (2 ngày)

**Ngày 1: Định Nghĩa Output Schema**
- Tạo file JSON schema cho Company, Bank
- Thêm `validate_output_schema()` vào Calculator

**Ngày 2: Test Tích Hợp Dashboard**
- Test hiển thị trên Streamlit
- Fix lỗi thiếu cột

#### GIAI ĐOẠN 5: Testing & Validation (2 ngày)

**Ngày 1: Unit & Integration Tests**
- Unit tests cho formulas (coverage 95%+)
- Test end-to-end cho calculator

**Ngày 2: End-to-End & Performance**
- Benchmark hiệu năng
- Update tài liệu

---

## KẾT LUẬN

Kế hoạch hợp nhất này kết hợp sức mạnh của cả 3 plan độc lập đồng thời bổ sung hệ thống sinh công thức hỗ trợ bởi AI mang tính cách mạng. Kết quả là:

1. **Giá Trị Tức Thời:** Sửa lỗi nghiêm trọng, loại bỏ mã lặp (Giai đoạn 0-2)
2. **Khả Năng Mở Rộng Tương Lai:** AI sinh công thức giúp thêm metric cực nhanh (Giai đoạn 3)
3. **Chất Lượng Production:** Testing và validation toàn diện (Giai đoạn 4-5)
4. **Timeline Thực Tế:** 12 ngày tuần tự, hoặc 8 ngày song song

**Bước Tiếp Theo:**
1. Duyệt kế hoạch hợp nhất này
2. Bắt đầu Giai đoạn 0 (Sửa lỗi nghiêm trọng) ngay lập tức

**Trạng thái Kế Hoạch:** FINAL - SẴN SÀNG TRIỂN KHAI
