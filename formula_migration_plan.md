# Kế hoạch Di trú và Chuẩn hóa Công thức Tài chính (Formula Migration Plan)

## 1. Mục tiêu
Di chuyển toàn bộ các công thức tài chính tiêu chuẩn (Standard Formulas) từ hệ thống cũ (`company_formula_sample.py`, `bank_formula_sample.py`) sang kiến trúc mới sử dụng `FormulaRegistry`, đảm bảo dữ liệu đầu ra được lưu trữ chính xác tại `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/fundamental`.

### 1.1. Các File Liên Quan
*   **File nguồn (đã đọc)**:
    *   `formula_sample.py` (hoặc `company_formula_sample.py`, `bank_formula_sample.py`): Chứa định nghĩa các công thức tài chính hiện có.
    *   `metric_registry.json` (tại `config/metadata/`): Chứa định nghĩa các metric đã được chuẩn hóa.
    *   `formula_registry.json` (tại `config/metadata/`): Chứa định nghĩa các công thức mẫu và sẽ được cập nhật.
*   **File đích (cần xử lý)**:
    *   `metric_registry.json`: Cần bổ sung các metric còn thiếu (đặc biệt là cho Cash Flow Statement).
    *   `formula_registry.json`: Cần cập nhật và bổ sung các công thức từ hệ thống cũ, đồng thời sửa lỗi tham chiếu.
    *   Thư mục `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/fundamental`: Nơi lưu trữ dữ liệu đầu ra đã được xử lý.
# Bổ sung thêm các công thức và định dạng số liệu cho các chỉ số tài chính
## 2. Đánh giá Hiện trạng

### 2.1. Hệ thống Registry Mới (`config/metadata/`)
*   **Metric Registry (`metric_registry.json`)**:
    *   [OK] Đã có **Income Statement** (`CIS`, `BIS`, `IIS`, `SIS`).
    *   [OK] Đã có **Balance Sheet** (`CBS`, `BBS`, `IBS`, `SBS`).
    *   **[CRITICAL MISSING]** Chưa tìm thấy metric cho **Cash Flow Statement** (Lưu chuyển tiền tệ) - Các mã `CCFI`, `BBS` (Cash Flow parts) không tồn tại.
*   **Formula Registry (`formula_registry.json`)**:
    *   [MISSING] Hiện tại chỉ chứa 5 công thức mẫu (`roe`, `roa`, `gross_margin`, `net_margin`, `eps`).
    *   **[ERROR]** Định nghĩa `roe` và `roa` đang bị sai mã tham chiếu:
        *   Hiện tại: `roe` dùng `CBS_270` (Tổng tài sản) => Sai (Phải là Vốn chủ sở hữu `CBS_400`).
        *   Hiện tại: `roa` dùng `CBS_100` (Tài sản ngắn hạn) => Sai (Phải là Tổng tài sản `CBS_270`).

### 2.2. Hệ thống Công thức Cũ (`formula_sample.py`)
*   Chứa đầy đủ logic cho:
    *   **Company**: Growth (YoY, QoQ), Margins (EBIT, EBITDA), Solvency (Quick/Current Ratio), Liquidity.
    *   **Bank**: NIM, CASA, LDR, NPL, Cost/Income (CIR).
*   Sử dụng nhiều mã metric chưa có trong Registry mới.

### 2.3. Đơn vị Tính toán & Định dạng Số liệu (Units & Formatting)

#### a. Hiện trạng
*   **Dữ liệu Gốc (Raw Input via Parquet)**:
    *   File: `company_full.parquet`, `bank_full.parquet`.
    *   Đơn vị: **VND (Tuyệt đối)**.
    *   Ví dụ: `2,378,122,000,000` (2.378 nghìn tỷ).
*   **Hệ thống Cũ (`formula_sample.py`)**:
    *   Đơn vị Output (Absolute): **Tỷ VND** (Chia raw cho `1e9`).
    *   Đơn vị Output (Ratio): **%** (Nhân raw cho `100`).
*   **Vấn đề**: Sự không đồng nhất giữa Input (VND) và Legacy Output (Tỷ VND) có thể gây nhầm lẫn khi gộp chung dữ liệu.

#### b. Tiêu chuẩn Chuẩn hóa (Propose Standard)
Để đảm bảo tính nhất quán (Consistency) cho Data Lake, quy định chuẩn format cho toàn bộ hệ thống mới:

| Loại Chỉ số | Đơn vị Chuẩn (Standard) | Format Code | Ghi chú |
| :--- | :--- | :--- | :--- |
| **Giá trị Tuyệt đối** (Doanh thu, LN, Tài sản) | **VND** | `#,##0` | Giữ nguyên như Raw Data. Dashboard sẽ tự format hiển thị (ví dụ: chia 1e9 khi vẽ biểu đồ). |
| **Tỷ suất / Biên** (Margins, ROE, Growth) | **%** | `0.00%` | Scale 100 (Ví dụ: 0.15 -> 15%). |
| **Trên mỗi Cổ phần** (EPS, BVPS, DPS) | **VND / cp** | `#,##0` | Ví dụ: 15,000 VND. |
| **Hệ số** (P/E, P/B, Beta) | **Lần (x)** | `0.00x` | Số thập phân (Ví dụ: 15.2x). |

> **Quyết định Quan trọng**: Calculator Engine mới sẽ **KHÔNG** chia cho `1e9` khi lưu trữ. Việc chuyển đổi sang "Tỷ VND" là trách nhiệm của lớp Hiển thị (UI/Streamlit), không phải của lớp Dữ liệu (Data Layer).

## 3. Kế hoạch Thực hiện (Action Plan)

### Giai đoạn 1: Chuẩn hóa Dữ liệu Thô (Raw Data Standardization)
**Hành động:**
1.  **Bổ sung Cash Flow Metrics**: Cần thêm definitions cho Cash Flow (Lưu chuyển tiền tệ) vào `metric_registry.json` cho cả 4 loại hình (Company, Bank, Insurance, Security).
2.  **Xác định và Chuẩn hóa Mã Metric**: Rà soát các công thức hiện có trong `formula_sample.py` để xác định các metric đang được sử dụng. Đối chiếu và đảm bảo các metric này có mã tương ứng trong `metric_registry.json`. Nếu chưa có, cần bổ sung định nghĩa cho các metric còn thiếu vào registry.

### Giai đoạn 2: Sửa lỗi & Cập nhật Formula Registry
**Hành động:**
1.  **Fix công thức ROE/ROA**:
    *   Sửa `roe` dependency: `CBS_400` (Vốn chủ).
    *   Sửa `roa` dependency: `CBS_270` (Tổng tài sản).
2.  **Porting công thức Company**: Thêm các mục sau vào `formula_registry.json`:
    *   *Profitability*: EBIT, EBITDA, Operating Margin.
    *   *Liquidity*: Current Ratio (`CBS_100` / `CBS_300`), Quick Ratio.
    *   *Solvency*: Debt/Equity, Debt/Asset.
3.  **Porting công thức Bank**:
    *   *Efficiency*: CIR (Cost to Income Ratio).
    *   *Asset Quality*: NPL Ratio (Nợ xấu / Tổng dư nợ), LDR (Loan to Deposit).
    *   *Profitability*: NIM (Net Interest Margin - cần logic tính trung bình tài sản sinh lời).

### Giai đoạn 3: Nâng cấp Calculator Engine (Python)
**Hành động:**
1.  **Cập nhật `company_calculator.py` & `bank_calculator.py`**:
    *   Cấu hình lại để đọc công thức từ `formula_registry.json`.
2.  **Xử lý Logic Phức tạp (Complex Logic Handling)**:
    *   Các chỉ số **Growth (YoY, QoQ)** và **TTM (Trailing Twelve Months)** cần được xử lý bằng code Python trong `BaseCalculator` (hoặc module `Utils`) chứ không định nghĩa cứng trong JSON.
    *   Engine sẽ tự động áp dụng logic Growth cho danh sách metric được cấu hình.

### Giai đoạn 4: Kiểm thử & Output
**Hành động:**
1.  Chạy tính toán thử nghiệm trên tập dữ liệu mẫu.
2.  So sánh kết quả với file excel/hệ thống cũ.
3.  Đảm bảo output parquet được lưu đúng cấu trúc tại `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/fundamental`.

## 4. Chi tiết Mapping Công thức (Ví dụ Đề xuất)

### Company
| Metric | Tên (VN) | Công thức (Mô phỏng) | Dependency (Dự kiến) |
| :--- | :--- | :--- | :--- |
| `ebit` | Lợi nhuận trước thuế và lãi vay | `net_profit_before_tax + interest_expense` | `CIS_50`, `CIS_23` |
| `ebitda` | EBITDA | `ebit + depreciation` | `ebit`, `CCFI_...` (Cần data CF) |
| `current_ratio` | Tỷ số thanh toán hiện hành | `current_assets / current_liabilities` | `CBS_100`, `CBS_310` |

### Bank
| Metric | Tên (VN) | Công thức (Mô phỏng) | Dependency (Dự kiến) |
| :--- | :--- | :--- | :--- |
| `cir` | Tỷ lệ chi phí trên thu nhập | `operating_expenses / operating_income` | `BIS_...` |
| `npl_ratio` | Tỷ lệ nợ xấu | `(bad_debt_group_3_5) / total_loans` | `BNOT_...` (Thuyết minh) |

---
**Khuyến nghị ngay lập tức:**
Vui lòng cập nhật `metric_registry.json` với dữ liệu **Cash Flow (Lưu chuyển tiền tệ)** trước khi tiến hành thêm công thức liên quan đến dòng tiền (như Free Cash Flow, EBITDA).
