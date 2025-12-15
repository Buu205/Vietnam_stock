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

## 2. Đánh giá Hiện trạng

### 2.1. Hệ thống Registry Mới (`config/metadata/`)
*   **Metric Registry (`metric_registry.json`)**:
    *   [OK] Đã có **Income Statement** (`CIS`, `BIS`, `IIS`, `SIS`).
    *   [OK] Đã có **Balance Sheet** (`CBS`, `BBS`, `IBS`, `SBS`).
    *   **[OK]** Đã có **Cash Flow Statement** (`CCFI` cho Company, `BCFI/BCFD` cho Bank). (Updated: 2025-12-13)
*   **Formula Registry (`formula_registry.json`)**:
    *   [MISSING] Hiện tại chỉ chứa 5 công thức mẫu (`roe`, `roa`, `gross_margin`, `net_margin`, `eps`).
    *   **[ERROR]** Định nghĩa `roe` và `roa` đang bị sai mã tham chiếu:
        *   Hiện tại: `roe` dùng `CBS_270` (Tổng tài sản) => Sai (Phải là Vốn chủ sở hữu `CBS_400`).
        *   Hiện tại: `roa` dùng `CBS_100` (Tài sản ngắn hạn) => Sai (Phải là Tổng tài sản `CBS_270`).

### 2.2. Hệ thống Công thức Cũ (`formula_sample.py`)
*   **Company Formula** (`company_formula_sample.py`):
    *   **Logic gaps**:
        *   Phụ thuộc nặng vào **Cash Flow Metrics (`CCFI_xx`)** để tính EBITDA, Depreciation, Cash Flow Ratios -> Nhóm này **đã có** trong `metric_registry.json`.
        *   Sử dụng **Growth Rates (QoQ)** -> Logic này hiện tại phải hardcode trong Python, chưa có configuration trong `formula_registry.json`.
    *   **Metric chưa có**: `CCFI_2` (Khấu hao), `CCFI_20` (Operating CF), `CCFI_21` (Capex), `CCFI_50` (FCF) -> **Đã tìm thấy**.
*   **Bank Formula** (`bank_forumula_sample.py`):
    *   **Logic gaps**:
        *   NIM, Yield, Cost cần tính **Trung bình 2 quý (Average 2Q)** của tài sản/nguồn vốn -> Logic phức tạp cần custom calculator.
        *   Các chỉ số Nợ Xấu (NPL) phụ thuộc vào **Notes (Thuyết minh - `BNOT_xx`)** -> Nhóm `BNOT` chưa được kiểm tra kỹ trong registry mới.
    *   **Metric chưa có**: `BNOT_4_2` đến `BNOT_4_5` (Chi tiết nợ xấu), `BNOT_31_1` (Thu lãi tiền gửi).

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

#### c. Phân tích & Khuyến nghị (Analysis & Recommendation)
Trả lời câu hỏi: *Nên chia ở Engine hay chuẩn hóa từ File kết quả?*

**Khuyến nghị: Xử lý hiển thị tại Display Engine (UI Layer).**

**Lý do:**
1.  **Tính Nhất quán với Metadata**: File `metric_registry.json` đang định nghĩa unit là `VND`. Nếu lưu file parquet là `Tỷ VND`, hệ thống sẽ bị lệch pha (Metadata nói A, Data là B), gây lỗi cho các ứng dụng khác hoặc AI agent sau này.
2.  **Độ chính xác (Precision)**: Lưu `2.5 tỷ` có thể làm mất thông tin chi tiết (làm tròn). Lưu `2,500,123,000` giữ nguyên độ chính xác.
3.  **Linh hoạt**: Nếu sau này cần đổi sang đơn vị `Triệu USD` hay `Triệu VND`, dữ liệu gốc `VND` là chuẩn nhất để convert. Nếu lưu cứng là `Tỷ`, việc convert lại sẽ phức tạp hơn.
4.  **Ngoại lệ (EPS)**: Vì EPS vẫn giữ là VND, việc lưu lẫn lộn cột thì Tỷ, cột thì VND trong cùng một bảng Database sẽ rất dễ gây nhầm lẫn (cần tra cứu dictionary liên tục). Tốt nhất là "All VND" trong Database.

**Giải pháp cho Người dùng (User Experience):**
*   Trên Dashboard (Streamlit): Code sẽ tự động detect các cột `category="income/balance_sheet"` và chia `1e9` + thêm hậu tố " Tỷ" khi render bảng/biểu đồ.
*   Khi duyệt file thô (nếu cần): Có thể tạo script view riêng hoặc dùng tính năng format của tool xem parquet.

> **Note:** Quyết định này tuân thủ khuyến nghị đã đưa ra: dữ liệu thô sẽ được lưu trữ dưới dạng VND tuyệt đối để đảm bảo tính nhất quán và độ chính xác. Việc chuyển đổi sang "Tỷ VND" hoặc định dạng % sẽ được thực hiện ở lớp hiển thị (UI/Streamlit) để tối ưu trải nghiệm người dùng mà không ảnh hưởng đến tính toàn vẹn của dữ liệu gốc.

## 3. Kế hoạch Thực hiện (Action Plan)

### Giai đoạn 1: Chuẩn hóa Dữ liệu Thô (Raw Data Standardization)
**Hành động:**
1.  **Verify & Map Cash Flow Metrics**:  Xác nhận lại mapping của các mã `CCFI` mới thêm vào với logic trong `formula_sample.py` để đảm bảo khớp nghĩa (Ví dụ: `CCFI_20` trong code = `CCFI_20` trong registry).
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
    *   **Logic TTM (Trailing Twelve Months)**:
        *   **CRITICAL RULE**: Dữ liệu đầu vào cho tính toán TTM **BẮT BUỘC** phải có tần suất là **Quarter (Q)**.
        *   **Công thức**: `TTM = Sum(Quarter_Current + 3 Quarters_Previous)`.
        *   **Quan trọng**: Tuyệt đối **KHÔNG** sử dụng dữ liệu Semi-annual (S) hoặc Year (Y) để tính TTM (để tránh lỗi số liệu bị nhân đôi hoặc thiếu sót như quá khứ). Engine phải có check: `if frequency != 'Q': raise Error`.
    *   **Logic Growth (YoY, QoQ)**:
        *   Sẽ được xử lý bởi `BaseCalculator` (hoặc module `Utils`) thông qua hàm `calculate_growth(series, period)`.
        *   Không hardcode công thức trong JSON.
        *   Mapping frequency tự động: QoQ cần data Q, YoY cần data Y hoặc cùng kỳ năm trước của Q.
    *   **Logic Data Sign Check (Kiểm tra Dấu Dữ liệu)**:
        *   **Problem**: Trong dữ liệu thô, chi phí (COGS, SG&A, Interest Exp) thường được lưu là số **Âm (-)**, nhưng đôi khi có thể bị lẫn số Dương do nhập liệu.
        *   **Solution**: Engine cần có cơ chế `Sanity Check` hoặc `Standardize Sign`.
        *   **Rule**: 
            *   Mặc định công thức là **Cộng Đại Số** (`Revenue + Expense`).
            *   Nếu phát hiện Chi phí là số Dương (>0) trong một tỷ lệ lớn records -> Cảnh báo (Warning Log).
            *   Tuỳ chọn: Thêm flag `force_negative_expense` trong config nếu cần ép kiểu dấu.
            
        *   **Signage Logic (Quy tắc Dấu)**:
            *   **Quy tắc**: Trong hệ thống, các khoản chi phí (Expenses) thường được lưu dưới dạng số **Âm (-)**.
            *   **Hệ quả**: Khi tính toán lợi nhuận, ta thực hiện phép **Cộng (+)** đại số.
            *   **Ví dụ**: `Profit = Revenue + Expense` (Vì `Expense` < 0, nên `+` sẽ làm giảm `Profit`).
            *   **Lưu ý**: Nếu người dùng muốn công thức hiển thị dạng `A - B`, cần lấy giá trị tuyệt đối: `Profit = Revenue - Abs(Expense)`. Quy ước hiện tại ưu tiên cộng đại số để đơn giản hóa logic code.

### Giai đoạn 4: Kiểm thử & Output
**Hành động:**
1.  Chạy tính toán thử nghiệm trên tập dữ liệu mẫu.
2.  Kiểm tra xem có sự tăng giảm bất thường tính toán vẹn của dữ liệu theo quý. 
3.  Đảm bảo output parquet được lưu đúng cấu trúc tại `/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/fundamental`.

## 4. Phụ lục: Chi tiết Logic Công thức Hệ thống Cũ (Reference)
*Dành cho việc kiểm tra và đối chiếu (Mapping)*

### A. Company Formulas (Chi tiết)

#### 1. Các chỉ số cơ bản (Direct Mappings)
*   **Income Statement**:
    *   Doanh thu thuần: `CIS_10`
    *   Giá vốn hàng bán: `CIS_11`
    *   Lợi nhuận trước thuế (EBT): `CIS_50`
    *   Lợi nhuận sau thuế (NPATMI): `CIS_61`
*   **Balance Sheet**:
    *   Tổng tài sản: `CBS_270`
    *   Tổng nợ phải trả: `CBS_300`
    *   Vốn chủ sở hữu: `CBS_400`
    *   Tiền & Tương đương tiền: `CBS_110`
    *   Hàng tồn kho: `CBS_140`
    *   Phải thu khách hàng (Các khoản phải thu ngắn hạn): `CBS_130`
    *   Tài sản cố định hữu hình: `CBS_221`
    *   Vay ngắn hạn: `CBS_320`
    *   Vay dài hạn: `CBS_338`
*   **Cash Flow**:
    *   Lưu chuyển tiền từ HĐKD (Operating CF): `CCFI_20`
    *   Lưu chuyển tiền từ HĐĐT (Investing CF): `CCFI_30`
    *   Lưu chuyển tiền từ HĐTC (Financing CF): `CCFI_40`
    *   Tiền chi mua sắm TSCĐ (Capex): `CCFI_21`
    *   Khấu hao tài sản cố định (depreciation cost- chi phí khấu hao): `CCFI_2`

#### 2. Các chỉ số Tài chính & Biên lợi nhuận (Ratios & Margins)
*   **Margins**:
    *   Biên lợi nhuận gộp (Gross Margin): `(Gross Profit / Net Revenue) * 100`
    *   Biên EBIT: `(EBIT / Net Revenue) * 100`
    *   Biên EBITDA: `(EBITDA / Net Revenue) * 100`
    *   Biên lợi nhuận ròng (Net Margin): `(NPATMI / Net Revenue) * 100`
*   **Efficiency**:
    *   Tỷ lệ chi phí hoạt động: `(SG&A / Net Revenue) * 100`
    *   *Ghi chú*: `SG&A` = Chi phí BH (`CIS_25`) + Chi phí QLDN (`CIS_26`)
 # Đầu tư :
    *   Tỷ lệ Khấu hao tích lũy (Accumulated Depreciation Rate): `(CBS_222 / CBS_221) * 100` (Giả định `CBS_222` là Giá trị hao mòn lũy kế và `CBS_221` là Nguyên giá TSCĐ)
    *   Tỷ lệ CIP (Capital Investment Profile): `(CBS_190 / CBS_270) * 100` (Giả định `CBS_190` là Chi phí xây dựng cơ bản dở dang và `CBS_270` là Tổng tài sản)
*   **Profitability**:
    *   ROE: `(NPATMI / Total Equity) * 100`
    *   ROA: `(NPATMI / Total Assets) * 100`
    *   EPS (TTM): `(NPATMI_TTM) / Common Shares (CBS_411A)`

#### 3. Các chỉ số Phức tạp & Công thức chi tiết (Complex Metrics):

1.  **Gross Profit (Lợi nhuận gộp)**:
    *   **Định nghĩa**: Lợi nhuận từ hoạt động kinh doanh chính sau khi trừ giá vốn hàng bán.
    *   **Thành phần**:
        *   Doanh thu thuần (`CIS_10`)
        *   Giá vốn hàng bán (`CIS_11`)
    *   **Công thức**: `Gross Profit = CIS_10 + CIS_11` (Do `CIS_11` là chi phí nên thường được lưu dưới dạng số âm, thực hiện phép cộng đại số).

2.  **EBIT (Earnings Before Interest & Tax - Lợi nhuận Trước Lãi và Thuế)**:
    *   **Định nghĩa**: Lợi nhuận từ hoạt động kinh doanh trước khi tính lãi vay và thuế.
    *   **Thành phần**:
        *   `Gross Profit`: Lợi nhuận gộp (`CIS_20`).
        *   `SG&A`: Chi phí Bán hàng (`CIS_25`) + Chi phí Quản lý Doanh nghiệp (`CIS_26`).
    *   **Công thức**: `EBIT = Gross Profit + CIS_25 + CIS_26` (Do `CIS_25`, `CIS_26` là số âm/negative).

3.  **EBITDA (Earnings Before Interest, Tax, Depreciation & Amortization)**:
    *   **Định nghĩa**: Lợi nhuận trước lãi, thuế và khấu hao. Thước đo dòng tiền từ hoạt động kinh doanh cốt lõi.
    *   **Thành phần**:
        *   `EBIT`: Lợi nhuận trước lãi và thuế.
        *   `Depreciation`: Khấu hao tài sản cố định (`CCFI_2`).
    *   **Công thức**: `EBITDA = EBIT + Depreciation`.

4.  **Net Financial Income (Thu nhập Tài chính Ròng)**:
    *   **Định nghĩa**: Chênh lệch giữa doanh thu tài chính và chi phí tài chính.
    *   **Thành phần**:
        *   Doanh thu hoạt động tài chính (`CIS_21`)
        *   Chi phí tài chính (`CIS_22` - *Lưu ý: Check kỹ dấu của dữ liệu*)
    *   **Công thức**: `Net Fin Income = CIS_21 + CIS_22` (Algebraic Addition).

5.  **Net Debt (Nợ Ròng)**:
    *   **Định nghĩa**: Tổng nợ vay chịu lãi trừ đi tiền mặt và các khoản đầu tư ngắn hạn tương đương tiền.
    *   **Thành phần**:
        *   Vay ngắn hạn (`CBS_320`)
        *   Vay dài hạn (`CBS_338`)
        *   Tiền và tương đương tiền (`CBS_110`)
    *   **Công thức**: `Net Debt = (CBS_320 + CBS_338) - CBS_110`.

6.  **Working Capital (Vốn Lưu động)**:
    *   **Định nghĩa**: Vốn lưu động ròng, đo lường khả năng thanh khoản ngắn hạn.
    *   **Thành phần**:
        *   Tài sản ngắn hạn (`CBS_100`)
        *   Nợ ngắn hạn (`CBS_300` hoặc `CBS_310` - *Check logic cũ*)
    *   **Công thức**: `Working Capital = CBS_100 - CBS_310`.

8.  **Signage Logic (Quy tắc Dấu)**:
    *   **Quy tắc**: Trong hệ thống, các khoản chi phí (Expenses) thường được lưu dưới dạng số **Âm (-)**.
    *   **Hệ quả**: Khi tính toán lợi nhuận, ta thực hiện phép **Cộng (+)** đại số.
    *   **Ví dụ**: `Profit = Revenue + Expense` (Vì `Expense` < 0, nên `+` sẽ làm giảm `Profit`).
    *   **Lưu ý**: Nếu người dùng muốn công thức hiển thị dạng `A - B`, cần lấy giá trị tuyệt đối: `Profit = Revenue - Abs(Expense)`. Quy ước hiện tại ưu tiên cộng đại số để đơn giản hóa logic code.

7.  **Free Cash Flow (FCF - Dòng tiền Tự do)**:
    *   **Định nghĩa**: Dòng tiền thuần doanh nghiệp tạo ra sau khi trừ chi phí đầu tư (Capex).
    *   **Thành phần**:
        *   Lưu chuyển tiền từ HĐKD (Operating CF): `CCFI_20`
        *   Tiền chi mua sắm TSCĐ (Capex): `CCFI_21`
    *   **Công thức**: `FCF = CCFI_20 - CCFI_21`.

8.  **Free Cash Flow to Equity (FCFE - Dòng tiền Tự do cho Chủ sở hữu)**:
    *   **Định nghĩa**: Dòng tiền còn lại cho các cổ đông sau khi đã thanh toán tất cả các chi phí, thuế, nợ và tái đầu tư cần thiết.
    *   **Thành phần**:
        *   Lợi nhuận sau thuế (NPATMI): `CIS_61`
        *   Khấu hao tài sản cố định (Depreciation): `CCFI_2`
        *   Tiền chi mua sắm TSCĐ (Capex): `CCFI_21`
        *   Thay đổi Vốn lưu động (Delta Working Capital): `(CBS_100 - CBS_310)_t - (CBS_100 - CBS_310)_{t-1}`
        *   Thay đổi Vay nợ ròng (Delta Net Borrowing): `((CBS_320 + CBS_338) - CBS_110)_t - ((CBS_320 + CBS_338) - CBS_110)_{t-1}`
    *   **Công thức**: `FCFE = NPATMI + Depreciation - Capex - Delta Working Capital + Delta Net Borrowing`.

### B. Bank Formulas (Chi tiết)

#### 1. Các chỉ số cơ bản (Direct Mappings)
*   **Income Statement**:
    *   Thu nhập lãi thuần (NII): `BIS_3`
    *   Tổng thu nhập hoạt động (TOI): `BIS_14A`
    *   Chi phí hoạt động (OPEX): `BIS_14`
    *   Chi phí dự phòng (Provision): `BIS_16`
    *   Lợi nhuận trước thuế (PBT): `BIS_17`
    *   Lợi nhuận sau thuế (NPATMI): `BIS_22A`
*   **Balance Sheet**:
    *   Tổng tài sản: `BBS_300`
    *   Vốn chủ sở hữu: `BBS_500`
    *   Tổng Dư nợ (Loans): `BBS_161` (Cho vay khách hàng)
    *   Tổng Huy động (Deposits): `BBS_330` (Tiền gửi khách hàng)

#### 2. Các chỉ số Hiệu quả & An toàn (Ratios & Safety)
*   **Profitability**:
    *   NIM (Net Interest Margin): `(NII / IEA_Avg_2Q) * 100`
    *   COF (Cost of Fund): `(Interest Exp / IBL_Avg_2Q) * 100`
    *   YOA (Yield on Asset): `(Interest Inc / IEA_Avg_2Q) * 100`
    *   ROE: `(NPATMI / Equity_Avg_2Q) * 100`
    *   ROA: `(NPATMI / Assets_Avg_2Q) * 100`
*   **Efficiency**:
    *   CIR (Cost to Income): `(OPEX / TOI) * 100`
    *   Orb (Operating Efficiency): *Cần định nghĩa nếu dùng check lại logic*
*   **Liquidity & Safety**:
    *   CASA Ratio: `(Tiền gửi không kỳ hạn / Tổng tiền gửi)` (Chi tiết bên dưới)
    *   LDR (Pure): `Total Loans / (Deposits + Giấy tờ có giá)`
    *   NPL Ratio: `NPL Amount / Total Loans`
    *   LLCR (Bao phủ nợ xấu): `Dự phòng cụ thể / NPL Amount`

#### 3. Các chỉ số Phức tạp & Công thức chi tiết (Complex Metrics):

1.  **Avg_2Q (Trung bình 2 Quý)**:
    *   **Định nghĩa**: Là trung bình cộng giá trị của chỉ số tại cuối quý hiện tại và cuối quý liền trước.
    *   **Công thức**: `(Value_Current_Quarter + Value_Previous_Quarter) / 2`.
    *   **Mục đích**: Phản ánh chính xác hơn quy mô tài sản/nguồn vốn trong kỳ tính toán thu nhập/chi phí lãi (tránh bias do biến động cuối kỳ).

2.  **IEA (Interest Earning Assets - Tài sản Sinh lời)**:
    *   **Định nghĩa**: Các tài sản mang lại thu nhập lãi cho ngân hàng.
    *   **Thành phần**:
        *   Tiền gửi tại NHNN (`BBS_120`)
        *   Tiền gửi & cho vay TCTD khác (`BBS_131`)
        *   Tiền gửi & cho vay TCTD khác (`BBS_132`)
        *   Chứng khoán kinh doanh (`BBS_141`)
        *   Cho vay khách hàng (`BBS_161`)
        *   Chứng khoán đầu tư (`BBS_171`)
        *   Chứng khoán đầu tư (`BBS_172`)
    *   **Công thức**: `IEA = BBS_120 + BBS_131+ BBS_132 + BBS_141+ BBS_161 + BBS_171 + BBS_172`.

3.  **IBL (Interest Bearing Liabilities - Nợ Chịu lãi)**:
    *   **Định nghĩa**: Các khoản nợ mà ngân hàng phải trả lãi.
    *   **Thành phần**:
        *   Các khoản nợ khác (`BBS_310`)
        *   Vay các TCTD khác (`BBS_320`)
        *   Tiền gửi của khách hàng (`BBS_330`)
        *   Các khoản phải trả khác (`BBS_350`)
        *   Phát hành giấy tờ có giá (`BBS_360`)
    *   **Công thức**: `IBL = BBS_320 + BBS_310 + BBS_330 + BBS_360 + BBS_350`.

4.  **NPL Amount (Non-Performing Loans - Tổng Nợ xấu)**:
    *   **Định nghĩa**: Tổng dư nợ của các nhóm nợ từ 3 đến 5 (dưới tiêu chuẩn, nghi ngờ, có khả năng mất vốn).
    *   **Thành phần**:
        *   Nợ dưới tiêu chuẩn (Nhóm 3) (`BNOT_4_3`)
        *   Nợ nghi ngờ (Nhóm 4) (`BNOT_4_4`)
        *   Nợ có khả năng mất vốn (Nhóm 5) (`BNOT_4_5`)
    *   **Công thức**: `NPL Amount = BNOT_4_3 + BNOT_4_4 + BNOT_4_5`.

5.  **NII (Net Interest Income - Thu nhập Lãi thuần)**:
    *   **Định nghĩa**: Chênh lệch giữa thu nhập lãi và chi phí lãi.
    *   **Thành phần**:
        *   Thu nhập lãi và các khoản thu nhập tương tự (`BIS_1`)
        *   Chi phí lãi và các chi phí tương tự (`BIS_2`)
        *   *Lưu ý*: `BIS_3` thường đã là Net Interest Income trong báo cáo.
    *   **Công thức**: `NII = BIS_3` (hoặc `BIS_1 - BIS_2` nếu cần kiểm tra lại).

6.  **TOI (Total Operating Income - Tổng Thu nhập Hoạt động)**:
    *   **Định nghĩa**: Tổng các nguồn thu nhập từ hoạt động kinh doanh của ngân hàng (Lãi, Dịch vụ, Ngoại hối, Chứng khoán...).
    *   **Thành phần**:
        *   Thu nhập lãi thuần (`BIS_3`)
        *   Lãi/lỗ thuần từ hoạt động dịch vụ (`BIS_6`)
        *   Lãi/lỗ thuần từ hoạt động KD ngoại hối (`BIS_7`)
        *   Lãi/lỗ thuần từ mua bán chứng khoán KD (`BIS_8`)
        *   Lãi/lỗ thuần từ mua bán chứng khoán đầu tư (`BIS_9`)
        *   Lãi/lỗ thuần từ hoạt động khác (`BIS_12`)
        *   Thu nhập từ góp vốn, mua cổ phần (`BIS_13`)
    *   **Công thức**: `TOI = BIS_14A`.

7.  **OPEX (Operating Expenses - Chi phí Hoạt động)**:
    *   **Định nghĩa**: Chi phí vận hành ngân hàng (nhân viên, tài sản, quản lý...).
    *   **Thành phần**: Chi phí hoạt động (`BIS_14`).
    *   **Công thức**: `OPEX = BIS_14`.

8.  **PPOP (Pre-Provision Operating Profit - Lợi nhuận Thuần trước Dự phòng)**:
    *   **Định nghĩa**: Lợi nhuận từ hoạt động kinh doanh trước khi trừ chi phí dự phòng rủi ro tín dụng.
    *   **Thành phần**:
        *   Tổng thu nhập hoạt động (`TOI`)
        *   Chi phí hoạt động (`OPEX` - số âm)
    *   **Công thức**: `PPOP = TOI + OPEX` (Cộng đại số).

9.  **Provision Expenses (Chi phí Dự phòng)**:
    *   **Định nghĩa**: Chi phí trích lập dự phòng rủi ro tín dụng trong kỳ.
    *   **Thành phần**: Chi phí dự phòng rủi ro tín dụng (`BIS_16`).
    *   **Công thức**: `Provision = BIS_16`.

10. **PBT (Profit Before Tax - Lợi nhuận Trước thuế)**:
    *   **Định nghĩa**: Tổng lợi nhuận kế toán trước khi trừ thuế thu nhập doanh nghiệp.
    *   **Thành phần**: Tổng lợi nhuận trước thuế (`BIS_17`).
    *   **Công thức**: `PBT = BIS_17`.

11. **NPATMI (Net Profit After Tax Minority Interest - Lợi nhuận Sau thuế của CĐ Mẹ)**:
    *   **Định nghĩa**: Lợi nhuận sau thuế thuộc về cổ đông của ngân hàng mẹ (sau khi trừ lợi ích cổ đông thiểu số).
    *   **Thành phần**: Lợi nhuận sau thuế của cổ đông công ty mẹ (`BIS_22A`).
    *   **Công thức**: `NPATMI = BIS_22A`.

12. **CASA Ratio (Current Account Savings Account Ratio - Tỷ lệ Tiền gửi Không kỳ hạn)**:
    *   **Định nghĩa**: Tỷ lệ tiền gửi không kỳ hạn trên tổng tiền gửi của khách hàng. Phản ánh khả năng huy động vốn giá rẻ.
    *   **Thành phần**:
        *   Tiền gửi không kỳ hạn bằng VND (`BNOT_26_1`)
        *   Tiền gửi không kỳ hạn bằng ngoại tệ (`BNOT_26_3`)
        *   Tiền gửi vốn chuyên dùng (`BNOT_26_5` - *Tùy ngân hàng, cần check kỹ*)
        *   Tổng tiền gửi của khách hàng (`BNOT_26`)
    *   **Công thức**: `CASA Ratio = (BNOT_26_1 + BNOT_26_3 + BNOT_26_5) / BNOT_26`.

13. **CIR (Cost to Income Ratio - Tỷ lệ Chi phí trên Thu nhập)**:
    *   **Định nghĩa**: Tỷ lệ chi phí hoạt động trên tổng thu nhập hoạt động. Đo lường hiệu quả vận hành.
    *   **Thành phần**: `OPEX`, `TOI`.
    *   **Công thức**: `CIR = (Abs(OPEX) / TOI) * 100`.

14. **LDR Pure (Loan to Deposit Ratio - Tỷ lệ Dư nợ trên Huy động)**:
    *   **Định nghĩa**: Tỷ lệ cho vay khách hàng trên tổng tiền gửi và giấy tờ có giá.
    *   **Thành phần**:
        *   Cho vay khách hàng (`BBS_161`)
        *   Tiền gửi của khách hàng (`BBS_330`)
        *   Phát hành giấy tờ có giá (`BBS_360`)
        *   Vốn tài trợ, ủy thác (`BBS_370`)
    *   **Công thức**: `LDR = BBS_161 / (BBS_330 + BBS_360 + BBS_370)`.

15. **NPL Ratio (Tỷ lệ Nợ xấu)**:
    *   **Định nghĩa**: Tỷ lệ nợ xấu trên tổng dư nợ cho vay.
    *   **Thành phần**: `NPL Amount` (đã định nghĩa trên), Tổng dư nợ (`BNOT_4` hoặc `BBS_161`).
    *   **Công thức**: `NPL Ratio = NPL Amount / Total Loans`.

16. **LLCR (Loan Loss Coverage Ratio - Tỷ lệ Bao phủ Nợ xấu)**:
    *   **Định nghĩa**: Khả năng dùng dự phòng để bù đắp nợ xấu.
    *   **Thành phần**:
        *   Dự phòng rủi ro cho vay khách hàng (`BBS_169` - *Lấy giá trị tuyệt đối*)
        *   `NPL Amount`
    *   **Công thức**: `LLCR = Abs(BBS_169) / NPL Amount`.

17. **BVPS (Book Value Per Share - Giá trị Sổ sách mỗi Cổ phiếu)**:
    *   **Định nghĩa**: Giá trị vốn chủ sở hữu trên mỗi cổ phiếu lưu hành.
    *   **Thành phần**:
        *   Vốn chủ sở hữu (`BBS_400` hoặc `BBS_410`)
        *   Lợi ích cổ đông thiểu số (`BBS_700` hoặc `7001` - *Trừ ra nếu dùng Total Equity*)
        *   Số lượng cổ phiếu lưu hành (`BBS_411`)
    *   **Công thức**: `BVPS = (BBS_410 - Minority_Interest) / BBS_411`.

18. **EPS (Earnings Per Share - Lợi nhuận trên mỗi Cổ phiếu)**:
    *   **Định nghĩa**: Lợi nhuận sau thuế phân bổ cho mỗi cổ phiếu thường.
    *   **Thành phần**: `NPATMI`, `Shares` (`BBS_411`).
    *   **Công thức**: `EPS = NPATMI / BBS_411`.
19. **Total bond (Tổng trái phiếu đầu tư)**:
    *   **Định nghĩa**: Tổng trái phiếu đầu tư.
    *   **Thành phần**: `BBS_141`, `BBS_171`, `BBS_172`.
    *   **Công thức**: `Total bond = BBS_141 + BBS_171 + BBS_172`.
20. **Total Average Cash & Placements (Tiền gửi & Tiền gửi TCTD khác bình quân)**:
    *   **Định nghĩa**: Tổng tiền gửi & Tiền gửi TCTD khác bình quân.
    *   **Thành phần**: `BBS_120`, `BBS_131`, `BBS_132`.
    *   **Công thức**: `Total deposit = BBS_120 + BBS_131 + BBS_132`.
21. **Total Average Customer Loan (Tiền gửi & Tiền gửi TCTD khác bình quân)**:
    *   **Định nghĩa**: Tổng tiền gửi & Tiền gửi TCTD khác bình quân.
    *   **Thành phần**: `BBS_160`, `BBS_181`
    *   **Công thức**: `Total customer loan = BBS_160 + BBS_181`.
22. **Total Deposit from customer  (Tiền gửi & Tiền gửi từ khách hàng và các tổ chức tín dụng)**:
    *   **Định nghĩa**: Tiền gửi từ khách hàng và các tổ chức tín dụng.
    *   **Thành phần**: `BBS_321`, `BBS_330`
    *   **Công thức**: `Total customer loan = BBS_321 + BBS_330`.
23  **Total Loan from SBV and credit instit (Tiền vay từ SBV và các tổ chức tín dụng khác)**:
    *   **Định nghĩa**: Tổng tiền vay từ SBV và các tổ chức tín dụng khác.
    *   **Thành phần**: `BBS_310`, `BBS_322`, `BBS_350`  
    *   **Công thức**: `Total customer loan = BBS_310 + BBS_322 + BBS_350`.
24  **Total Loan from value paper (Tiền vay từ giấy tờ có giá & trái phiếu)**:
    *   **Định nghĩa**: Tổng tiền vay từ giấy tờ có giá & trái phiếu.
    *   **Thành phần**: `BBS_360`
    *   **Công thức**: `Total customer loan = BBS_360`.


### Bank Sheet 
#### Size (Quy mô)
    1. Total asset (Tổng tài sản): `BBS_300`
    2. Total credit (Tổng tín dụng): `BBS_161` (Tổng dư nợ cho vay) + `BBS_181` (Mua nợ ) + `BNOT_5_1_3` (Trái phiếu do các TCKT trong nước phát hành - Chứng khoán nợ) + `BNOT_13_1_1_3` (Trái phiếu do các TCKT trong nước phát hành) + `BNOT_13_2_3` (Trái phiếu do các TCKT trong nước phát hành)
       2.1 Total loan (Tổng dư nợ cho vay): `BBS_161`
       2.2 Total corp bond (Tổng trái phiếu doanh nghiệp): `BNOT_13_1_1_3`
    3. Total customer deposit (Tổng tiền gửi khách hàng): `BBS_330`

#### Income Statement (Kết quả kinh doanh)
    1. NII (Thu nhập lãi thuần): `BIS_3`
    2. TOI (Tổng thu nhập hoạt động): `BIS_14A`
    3. NOII (Thu Nhập phi lãi) = TOI- NII = `BIS_14A - BIS_3`
    3. OPEX (Chi phí hoạt động): `BIS_14`
    4. PPOP (Lợi nhuận trước dự phòng): `BIS_14A + BIS_14` / Hoặc `BIS_15`
        4.1 Provision expenses (Chi phí dự phòng): `BIS_16`
    5. PBT (Lợi nhuận trước thuế): `BIS_17`
    6. NPATMI (Lợi nhuận sau thuế của cổ đông công ty mẹ): `BIS_22A`

#### Growth (Tăng trưởng)
> **Note**: Các chỉ số Tăng trưởng (Growth) có thể được tính theo YoY (Year-over-Year) hoặc QoQ (Quarter-over-Quarter) tùy theo yêu cầu phân tích cụ thể. Công thức bên dưới đang mô tả mặc định.
    1. Credit growth (Tăng trưởng tín dụng): `(Total_Credit - Total_Credit_PrevYearEnd) / Total_Credit_PrevYearEnd`
    2. Asset growth (Tăng trưởng tài sản): `(BBS_300 - BBS_300_PrevYearEnd) / BBS_300_PrevYearEnd`
    3. Customer loan growth (ytd) (Tăng trưởng cho vay khách hàng (YTD)): `(BBS_161 - BBS_161_PrevYearEnd) / BBS_161_PrevYearEnd`
    4. Customer deposit growth (ytd) (Tăng trưởng tiền gửi khách hàng (YTD)): `(BBS_330 - BBS_330_PrevYearEnd) / BBS_330_PrevYearEnd`
    5. NII growth (yoy) (Tăng trưởng thu nhập lãi thuần (YoY)): `(BIS_3 - BIS_3_SamePeriodLastYear) / BIS_3_SamePeriodLastYear`
    6. TOI growth (yoy) (Tăng trưởng tổng thu nhập hoạt động (YoY)): `(BIS_14A - BIS_14A_SamePeriodLastYear) / BIS_14A_SamePeriodLastYear`
    7. PPOP growth (yoy) (Tăng trưởng lợi nhuận trước dự phòng (YoY)): `(BIS_15 - BIS_15_SamePeriodLastYear) / BIS_15_SamePeriodLastYear`
    8. PBT growth (yoy) (Tăng trưởng lợi nhuận trước thuế (YoY)): `(BIS_17 - BIS_17_SamePeriodLastYear) / BIS_17_SamePeriodLastYear`
    9. NPATMI growth (yoy) (Tăng trưởng lợi nhuận sau thuế của CĐ mẹ (YoY)): `(BIS_22A - BIS_22A_SamePeriodLastYear) / BIS_22A_SamePeriodLastYear`

#### Asset Quality (Chất lượng tài sản)
    1. Group 2 (%) (Tỷ lệ nợ nhóm 2) = (BNOT_4_2/BNOT_4) * 100
    2. NPL (%) (Tỷ lệ nợ xấu): ((BNOT_4_3 + BNOT_4_4 + BNOT_4_5) / BNOT_4) * 100
    3. Provision/ Total loan (Tỷ lệ dự phòng/Tổng dư nợ): (BBS_169/BBS_161) * 100
    4. LLCRs (Tỷ lệ bao phủ nợ xấu): ((BBS_169) / (BNOT_4_3 + BNOT_4_4 + BNOT_4_5)) * 100
    5. Accrued/ Total loan (Tỷ lệ lãi dự thu/Tổng dư nợ): `(BBS_252 / ( (BBS_160 + BBS_181) + (BBS_141 + BBS_171 + BBS_172) )) * 100`
    6. Credit cost (Chi phí tín dụng) = BIS_16 / BBS_160_Avg_2Q (BBS_160 lấy trung bình 2 quý gần nhất)
    7. NPL formation (%) (Tỷ lệ hình thành nợ xấu) = (NPL Amount / BBS_160_Avg_2Q) * 100 (NPL Amount là tổng nợ nhóm 3, 4, 5; BBS_160 lấy trung bình 2 quý gần nhất)
    8. G2 formation (%) (Tỷ lệ hình thành nợ nhóm 2) = (Group 2 Amount / BBS_160_Avg_2Q) * 100 (Group 2 Amount BNOT_4_2/BNOT_4; BBS_160 lấy trung bình 2 quý gần nhất)

   

#### Capital Adequacy (An toàn vốn)
    1. LDR (Tỷ lệ dư nợ/huy động vốn): `((BBS_161 + BBS_170)`/ (BBS_330 + BBS_360)) * 100`
    2. Fair LDR (CB+CL/CD + VP) (LDR thực chất / điều chỉnh): `((BBS_161 + BNOT_5_1_3)`/ (BBS_330 + BBS_360)) * 100`
    3. Net Interbank deposit/ Customer deposit (Tỷ lệ tiền gửi LNH ròng/Tiền gửi KH): `((BBS_321- BBS_131)/BBS_330) * 100`
    4. Leverage (Đòn bẩy tài chính): `(BBS_100/BBS_500) * 100`
    5. CASA (Tỷ lệ tiền gửi không kỳ hạn): `((BNOT_26_1 + BNOT_26_3 + BNOT_26_5)/BNOT_26) * 100`
    6. Short term loan/ total loan (Tỷ lệ cho vay ngắn hạn/Tổng dư nợ): `(BNOT_9_1/BNOT_9) * 100`
    7. Required Liquid Reserve (Tỷ lệ dự trữ thanh khoản bắt buộc): `((BNOT_5_1_1+BNOT_5_1_2+BNOT_13_1_1_1+BNOT_13_1_1_2+BNOT_13_2_2+BNOT_13_2_3+BBS_110+BBS_120)/BBS_400) * 100`

#### Earning quality (Chất lượng lợi nhuận) Toàn bộ sử dụng %, * 100 
    1. Average gross yield (Lợi suất sinh lời bình quân): `(BIS_1/IEA_Avg_2Q) * 100`
        1.1 Loan yield (Lợi suất cho vay): `(BNOT_31_2/Total customer loan_Avg_2Q) * 100`, trong đó  total customer loan_avg_2Q = BBS_160 + BBS_181
        1.2 Bond yield (Lợi suất trái phiếu): `(BNOT_31_3/Totalbond_Avg_2Q) * 100`, trong đó totalbond_Avg_2Q = BBS_141+BBS_171+BBS_172
        1.3 Deposit yield (Lợi suất tiền gửi): `(BNOT_31_1/Total Average Cash & Placements(Tiền gửi & Tiền gửi TCTD khác bình quân)_Avg_2Q) * 100` trong đó Total Average Cash & Placements(Tiền gửi & Tiền gửi TCTD khác bình quân)_Avg_2Q = BBS_120+BBS_131+BBS_132
    2. Average funding cost (Chi phí vốn bình quân): `(BIS_2/IBL_Avg_2Q) * 100`
        2.1 COF deposit (Chi phí vốn tiền gửi): `(BNOT_32_1/Total Average Cash & Placements(Tiền gửi & Tiền gửi TCTD khác bình quân)_Avg_2Q) * 100`
        2.2 COF loan (Chi phí vốn vay): `(BNOT_32_2/Total customer loan_Avg_2Q) * 100`
        2.3 COF valuable paper (Chi phí vốn giấy tờ có giá): `(BNOT_32_3/Totalbond_Avg_2Q) * 100`
    3. NIM (%) (Biên lãi ròng): `(BIS_3 / IEA_Avg_2Q) * 100`
    4. NII/ TOI (Tỷ lệ Thu nhập lãi thuần/Tổng thu nhập HĐ): `(BIS_3 / BIS_14A) * 100`
    5. Provisioning/PPOP (Tỷ lệ trích lập dự phòng/PPOP): `(BIS_16 / (BIS_14A + BIS_14)) * 100`
    6. CIR (Tỷ lệ chi phí/Thu nhập): `((BIS_14) / BIS_14A) * 100`
    7. Fees Income/ Total Loan (Thu nhập phí/Tổng dư nợ)
    8. ROEA (Lợi nhuận/Tài sản BQ - ROAA): `(BIS_22A / Assets_Avg_2Q) * 100`
    9. ROEE (Lợi nhuận/Vốn chủ sở hữu BQ - ROAE): `(BIS_22A / Equity_Avg_2Q) * 100`
    

### C. Securities Formulas (Detailed)

#### 1. Các chỉ số cơ bản (Direct Mappings)
*   **Scale (Quy Mô)**:
    *   Total Assets: `SBS_270`
    *   Total Equity: `SBS_400`
    *   Total Investment: `SBS_112 + SBS_113 + SBS_115`
    *   Total Loans (Margin): `SBS_114`
    *   Total Debt: `SBS_311 + SBS_341`
*   **Income Statement (Kết Quả Kinh Doanh)**:
    *   Total Revenue (Doanh thu): `SIS_20`
    *   Gross Profit: `SIS_50_1` (hoặc `SIS_20 - SIS_40`)
    *   Income from FVTPL: `SIS_1`
    *   Income from HTM: `SIS_2`
    *   Income from Loans: `SIS_3`
    *   NPATMI: `SIS_201`

#### 2. Các chỉ số Hiệu quả (Ratios & Safety)
*   **Capital & Structure**:
    *   Leverage: `SBS_270 / SBS_400`
    *   Loans/Equity: `SBS_114 / SBS_400`
    *   Inv/Assets: `Total Investment / SBS_270`
    *   Loans/Assets: `SBS_114 / SBS_270`
*   **Profitability (TTM)**:
    *   ROAE: `Sum(SIS_200, 4Q) / Avg(SBS_400, 5Q)`
    *   ROAA: `Sum(SIS_200, 4Q) / Avg(SBS_270, 5Q)`
    *   Investment Yield: `Sum(SIS_1+SIS_2+SIS_4, 4Q) / Avg(Total Investment, 5Q)`
    *   Loan Yield: `Sum(SIS_3, 4Q) / Avg(SBS_114, 5Q)`
    *   Funding Cost: `Sum(SIS_52, 4Q) / Avg(Total Debt, 5Q)`

#### 3. Các chỉ số Phức tạp & Công thức chi tiết (Complex Metrics):

1.  **Total Investment (Tổng danh mục đầu tư)**:
    *   **Định nghĩa**: Tổng giá trị các khoản đầu tư tài chính.
    *   **Thành phần**: `FVTPL (SBS_112) + HTM (SBS_113) + AFS (SBS_115)`.

2.  **Net Investment Yield (Hiệu suất đầu tư ròng)**:
    *   **Định nghĩa**: Lợi nhuận thuần từ đầu tư trên quy mô danh mục bình quân.
    *   **Thành phần**:
        *   Tử số: `Sum((SIS_1+SIS_21) + (SIS_2+SIS_22) + (SIS_4+SIS_24), 4Q)` (Lãi + C.Phí).
        *   Mẫu số: `Avg(Total Investment, 5Q)`.
    *   **Công thức**: `Net Inv Yield = Net Inv Income / Avg Inv Assets`.

3.  **Net Loan Yield (Hiệu suất cho vay ròng)**:
    *   **Định nghĩa**: Lãi suất cho vay thực tế sau khi trừ chi phí vốn/lỗ liên quan.
    *   **Thành phần**:
        *   Tử số: `Sum(SIS_3 + SIS_22_1, 4Q)` (Thu lãi vay + Chi phí/Lỗ cho vay).
        *   Mẫu số: `Avg(SBS_114, 5Q)` (Dư nợ Margin bình quân).
    *   **Công thức**: `Net Loan Yield = Net Loan Income / Avg Loan Assets`.

4.  **Net Broker Yield (Hiệu suất môi giới ròng)**:
    *   **Định nghĩa**: Tỷ suất lợi nhuận gộp mảng môi giới.
    *   **Thành phần**:
        *   Tử số: `Sum(SIS_6 + SIS_27, 4Q)` (Doanh thu môi giới + Chi phí môi giới).
        *   Mẫu số: `Sum(SIS_6, 4Q)` (Tổng doanh thu môi giới).
    *   **Công thức**: `Net Broker Yield = Gross Broker Profit / Broker Revenue`.

5.  **Funding Cost (Chi phí vốn COF)**:
    *   **Định nghĩa**: Chi phí nợ vay bình quân.
    *   **Thành phần**:
        *   Tử số: `Sum(SIS_52, 4Q)` (Chi phí lãi vay).
        *   Mẫu số: `Avg(SBS_311 + SBS_341, 5Q)` (Tổng nợ vay bình quân).
    *   **Công thức**: `Funding Cost = Interest Expense / Avg Total Debt`.

6.  **Leverage (Tỷ lệ Đòn bẩy)**:
    *   **Định nghĩa**: Mức độ sử dụng nợ vay so với vốn chủ sở hữu (hoặc Tổng tài sản / VCSH).
    *   **Thành phần**: `Tổng Tài sản (SBS_270)`, `Vốn Chủ sở hữu (SBS_400)`.
    *   **Công thức**: `Leverage = SBS_270 / SBS_400`.

7.  **Loans to Equity Ratio (Dư nợ / VCSH)**:
    *   **Định nghĩa**: Tỷ lệ dư nợ cho vay margin trên vốn chủ sở hữu.
    *   **Thành phần**: `Dư nợ Margin (SBS_114)`, `Vốn Chủ sở hữu (SBS_400)`.
    *   **Công thức**: `Loans/Equity = SBS_114 / SBS_400`.

8.  **Investment Portfolio Ratio (Tỷ trọng Danh mục đầu tư)**:
    *   **Định nghĩa**: Tỷ trọng tài sản phân bổ vào hoạt động tự doanh.
    *   **Thành phần**: `Total Investment (SBS_112 + 113 + 115)`, `Total Assets (SBS_270)`.
    *   **Công thức**: `Inv Ratio = Total Investment / Total Assets`.

9.  **CIR (Cost to Income Ratio)**:
    *   **Định nghĩa**: Tỷ lệ chi phí hoạt động và quản lý trên tổng doanh thu.
    *   **Thành phần**: `Chi phí (SIS_40 + SIS_62)`, `Doanh thu (SIS_20)`.
    *   **Công thức**: `CIR = Abs(SIS_40 + SIS_62) / SIS_20`.

10. **Gross Profit (Lợi nhuận gộp)**:
    *   **Định nghĩa**: Lợi nhuận gộp từ hoạt động kinh doanh (hoặc lấy trực tiếp từ báo cáo nếu có).
    *   **Thành phần**: `Doanh thu (SIS_20)`, `Chi phí HĐ (SIS_40)`.
    *   **Công thức**: `Gross Profit = SIS_50_1` (hoặc `SIS_20 + SIS_40`).



