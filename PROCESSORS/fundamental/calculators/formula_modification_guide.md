# Hướng dẫn Chỉnh sửa và Thêm mới Công thức (Formula Modification Guide)

Tài liệu này hướng dẫn quy trình tiêu chuẩn để chỉnh sửa hoặc thêm mới các công thức tính toán tài chính và định nghĩa chỉ số trong hệ thống Vietnam Dashboard.

## 1. Tổng quan Kiến trúc Công thức

Hệ thống hiện tại (Phase 4 Refactor) đã tách biệt định nghĩa dữ liệu thô và công thức tính toán để tăng tính linh hoạt và khả năng tự động hóa.

*   **Raw Metrics (Dữ liệu thô):** `config/metadata/raw_metric_registry.json`
    *   Định nghĩa các item lấy trực tiếp từ Báo cáo tài chính (Doanh thu `CIS_10`, Tài sản `CBS_100`...).
    *   Ít thay đổi.
*   **Formula Registry (Công thức):** `config/metadata/formula_registry.json`
    *   Định nghĩa các chỉ số tính toán (ROE, Margin, Growth...).
    *   Chứa logic công thức dạng khai báo.
    *   **Automation:** Thay đổi file này sẽ **TỰ ĐỘNG** cập nhật cách tính mà không cần sửa code Python (nhờ `Dynamic Formula Engine`).
*   **Bộ tính toán:** `PROCESSORS/fundamental/calculators/*.py`
    *   Base Calculator có phương thức `calculate_from_registry(metric_name)` để thực thi công thức động.

## 2. Quy trình Workflow (Step-by-Step)

Để sửa đổi hoặc thêm mới, hãy tuân theo quy trình sau:

### Bước 1: Xác định loại chỉ số
*   **Raw Metric:** Cần thêm item mới từ BCTC? -> Sửa `raw_metric_registry.json`.
*   **Calculated Metric:** Cần sửa công thức ROE hay thêm chỉ số tỷ lệ mới? -> Sửa `formula_registry.json`.

### Bước 2: Cập nhật Registry

#### Trường hợp A: Sửa công thức tính toán (Calculated Metrics)
Mở file `config/metadata/formula_registry.json`. Tìm và sửa section `"calculated_metrics"`.

```json
"roe": {
  "name_vi": "Lợi nhuận trên vốn chủ sở hữu",
  "name_en": "Return on Equity",
  "formula": "(net_profit_npatmi / total_equity) * 100",
  "unit": "%",
  "dependencies": {
    "COMPANY": ["CIS_62", "CBS_400"],
    "BANK": ["BIS_22", "BBS_400"]
  }
}
```
*   **Lưu ý quan trọng:** `dependencies` phải chứa **đúng 2 thành phần** (Tử số, Mẫu số) để `Dynamic Engine` tự động tính phép chia (Calculate Ratio).
*   Nếu `dependencies` có nhiều hơn 2 hoặc logic phức tạp hơn phép chia, bạn vẫn có thể cần custom code (xem Bước 3).

#### Trường hợp B: Thêm chỉ số mới (New Metric)
Thêm entry mới vào `formula_registry.json`:

```json
"new_ratio": {
    "name_vi": "Tỷ số mới",
    "formula": "Doanh thu / Tài sản",
    "unit": "%",
    "dependencies": {
        "COMPANY": ["CIS_10", "CBS_100"]
    }
}
```

### Bước 3: Cập nhật Code Python (Chỉ khi cần thiết)

**Tin vui:** Với `Dynamic Formula Engine`, nếu chỉ số của bạn là phép chia đơn giản `(A / B)` hoặc `(A / B) * 100`, bạn **KHÔNG CẦN** viết thêm dòng code Python nào! Hệ thống sẽ tự động tính toán dựa trên `dependencies`.

Bạn chỉ cần cập nhật code Python trong các trường hợp sau:
1.  Công thức phức tạp (không phải A/B).
2.  Logic đặc thù (If/Else, điều kiện biên).

Nếu cần sửa logic đặc thù:
*   Mở `PROCESSORS/fundamental/calculators/company_calculator.py` (hoặc Bank/Insurance).
*   Override phương thức tính toán.


#### File cần sửa:
*   **Công thức chung (đơn giản):** `PROCESSORS/fundamental/formulas/_base_formulas.py`
*   **Logic tính toán (Calculator):**
    *   Công ty: `PROCESSORS/fundamental/calculators/company_calculator.py`
    *   Ngân hàng: `PROCESSORS/fundamental/calculators/bank_calculator.py`
    *   Bảo hiểm: `PROCESSORS/fundamental/calculators/insurance_calculator.py`
    *   Chứng khoán: `PROCESSORS/fundamental/calculators/security_calculator.py`

**Ví dụ:** Nếu bạn sửa cách tính ROE trong `metric_registry.json`, hãy kiểm tra phương thức `calculate_profitability_ratios` trong `company_calculator.py` để đảm bảo code Python thực hiện đúng phép tính mới.

```python
# PROCESSORS/fundamental/calculators/company_calculator.py

def calculate_profitability_ratios(self, df):
    # logic cũ
    # result_df['roe'] = ...
    
    # Cập nhật logic mới (nếu cần)
    calc_roe = formula_registry.get_formula('calculate_roe') # Lấy từ registry formulas/
    # Hoặc viết trực tiếp nếu là logic đặc thù mới
```

### Bước 4: Chạy Kiểm thử (Verification)
Luôn chạy bộ test tích hợp để đảm bảo không phá vỡ tính năng hiện có.

```bash
python3 tests/fundamental/calculator_integration_test.py
```

## 3. Bản đồ File (Map)

1.  **Định nghĩa (Definitions):** `config/metadata/metric_registry.json`
2.  **Tra cứu (Lookup):** `config/registries/metric_lookup.py`
3.  **Hàm tính toán nhỏ (Formula Functions):** `PROCESSORS/fundamental/formulas/_base_formulas.py`
4.  **Luồng tính toán chính (Calculators):** `PROCESSORS/fundamental/calculators/*_calculator.py`
5.  **Test:** `tests/fundamental/calculator_integration_test.py`

---
**Tóm tắt:** Bắt đầu từ `metric_registry.json` để định nghĩa -> Cập nhật Code Calculator để thực thi -> Chạy Test để xác nhận.
