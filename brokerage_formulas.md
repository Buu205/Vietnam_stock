
# Công Thức Tính Các Chỉ Số Tài Chính Công Ty Chứng Khoán (Brokerage Formulas)

Tài liệu này mô tả cách tính toán các chỉ số tài chính (Mã MT) được tìm thấy trong file `Brokerage Masterfile.xlsx`.

> **Lưu ý**: Các công thức dưới đây sử dụng mã số từ hệ thống `metric_registry` (ví dụ `SIS_1`, `SBS_112`) để đảm bảo tính nhất quán khi cài đặt.

---

## 1. Quy Mô & Lợi Nhuận (Scale & Profit)

Nhóm chỉ số phản ánh quy mô tài sản, nguồn vốn và kết quả kinh doanh tuyệt đối.

- **Total Assets** (Tổng tài sản): `SBS_270` (Tổng cộng tài sản.)
- **Total Equity** (Vốn chủ sở hữu): `SBS_400` (Vốn chủ sở hữu.)
- **Investment Portfolio** (Danh mục đầu tư): `SBS_112 + SBS_113 + SBS_115` (FVTPL + HTM + AFS.)
- **Loan Portfolio** (Danh mục cho vay): `SBS_114` (Các khoản cho vay và phải thu margin.)
- **Total Revenue** (Tổng doanh thu): `SIS_20` (Doanh thu hoạt động.)
- **Gross Profit** (Lợi nhuận gộp): `SIS_20 - SIS_40` (Doanh thu hoạt động - Chi phí hoạt động.)
    - **Investment GP** (Lợi nhuận gộp Tự doanh): `(SIS_1 - SIS_21) + (SIS_2 - SIS_22) + (SIS_4 - SIS_24)` (Lãi - Lỗ từ FVTPL, HTM, AFS.)
    - **Lending GP** (Lợi nhuận gộp Cho vay): `SIS_3 - SIS_22_1` (Lãi cho vay - Chi phí/Lỗ từ cho vay.)
    - **Brokerage GP** (Lợi nhuận gộp Môi giới): `SIS_6 - SIS_27` (Doanh thu môi giới - Chi phí môi giới.)
    - **IB GP** (Lợi nhuận gộp IB): `(SIS_7_1 + SIS_7_2 + SIS_8 + SIS_10) - (SIS_28 + SIS_29)` (Doanh thu Bảo lãnh, Đại lý, Tư vấn - Chi phí Bảo lãnh, Tư vấn.)
- **PBT** (Lợi nhuận trước thuế): `SIS_90` (Tổng lợi nhuận kế toán trước thuế.)
- **Leverage** (Tỷ lệ đòn bẩy): `SBS_270 / SBS_400` (Tổng tài sản / Vốn chủ sở hữu.)
- **Loans/Equity** (Tỷ lệ Cho vay/VCSH): `SBS_114 / SBS_400` (Dư nợ cho vay / Vốn chủ sở hữu.)

## 2. Chi Tiết Kết Quả Kinh Doanh (Income Statement Breakdown)

Phân tích cấu trúc lợi nhuận từ Doanh thu hoạt động đến Lợi nhuận sau thuế (mô phỏng bảng KQKD chi tiết).

- **Operating Revenue** (Doanh thu hoạt động): `SIS_20`
- **Operating Expenses** (Chi phí hoạt động): `SIS_40`
- **Gross Operating Profit** (Lợi nhuận gộp HĐKD): `SIS_20 - SIS_40`
    - *Lưu ý*: Đây là lợi nhuận từ các hoạt động kinh doanh chính (Môi giới, Tự doanh, Cho vay) trước khi trừ chi phí tài chính và quản lý.
- **Financial Income** (Doanh thu tài chính): `SIS_1 - SIS_1` (Thường nằm trong Doanh thu hoạt động `SIS_20`, nhưng nếu tách riêng theo khoản mục kế toán thì là các khoản lãi tiền gửi, chênh lệch tỷ giá lãi...).
    - *Mapping*: `SIS_11` (Thu nhập khác) hoặc phần lãi tiền gửi trong `SIS_20`.
- **Financial Expenses** (Chi phí tài chính): `SIS_60` (Bao gồm `SIS_52` Chi phí lãi vay).
    - **Interest Expense** (Chi phí nợ vay): `SIS_52`
- **Assoc/Divestment Gain** (Lãi từ công ty liên kết/thoái vốn): `SIS_56` (Lãi/lỗ từ công ty liên doanh, liên kết) + `SIS_43` (Lãi bán, thanh lý đầu tư).
- **G&A Expenses** (Chi phí QLDN): `SIS_62`
- **Net Other Income** (Thu nhập ròng khác): `SIS_80` (Kết quả hoạt động khác = Thu nhập khác - Chi phí khác).
- **PBT** (Lợi nhuận trước thuế): `SIS_90` (`Gross Op Profit` - `Fin Exp` - `G&A` + `Other Income`...).
- **Net Income** (Lợi nhuận sau thuế): `SIS_200`

## 3. Tốc Độ Tăng Trưởng (Growth)

Đo lường mức tăng trưởng %YTD cho Bảng Cân Đối Kế Toán và %YoY cho Kết Quả Kinh Doanh.

- **Investment Portfolio (%YTD)**: `Sum(Inv_End) / Sum(Inv_Start) - 1` (Tăng trưởng danh mục đầu tư.)
- **Loan Portfolio (%YTD)**: `SBS_114_End / SBS_114_Start - 1` (Tăng trưởng dư nợ cho vay.)
- **Total Revenue (%YoY)**: `SIS_20_Q / SIS_20_YoY - 1` (Tăng trưởng doanh thu hoạt động.)
- **Gross Profit (%YoY)**: `GP_Q / GP_YoY - 1` (Tăng trưởng lợi nhuận gộp.)
    - **Investment GP (%YoY)**: `Inv_GP_Q / Inv_GP_YoY - 1`
    - **Lending GP (%YoY)**: `Lending_GP_Q / Lending_GP_YoY - 1`
    - **Brokerage GP (%YoY)**: `Brokerage_GP_Q / Brokerage_GP_YoY - 1`
    - **IB GP (%YoY)**: `IB_GP_Q / IB_GP_YoY - 1`
- **PBT (%YoY)**: `SIS_90_Q / SIS_90_YoY - 1` (Tăng trưởng lợi nhuận trước thuế.)

## 4. Khả Năng Sinh Lời (Profitability)

Các chỉ số hiệu quả hoạt động (dùng số liệu TTM - Trailing 12 Months cho Tử số và Bình quân 5 quý cho Mẫu số nếu là tỷ suất).

- **ROAA (TTM)**: `Sum(SIS_200, 4Q) / Avg(SBS_270, 5Q)` (Lợi nhuận sau thuế / Tổng tài sản bình quân.)
- **ROAE (TTM)**: `Sum(SIS_200, 4Q) / Avg(SBS_400, 5Q)` (Lợi nhuận sau thuế / Vốn chủ sở hữu bình quân.)
- **Investment Yield (TTM)**: `Sum(Inv_GP, 4Q) / Avg(Sum(SBS_112,SBS_113,SBS_115), 5Q)` (Hiệu suất đầu tư: Lãi thuần đầu tư / Tài sản đầu tư bình quân.)
- **Loan Yield (TTM)**: `Sum(Lending_GP, 4Q) / Avg(SBS_114, 5Q)` (Hiệu suất cho vay: Lãi thuần cho vay / Dư nợ bình quân.)
- **Brokerage Gross Margin (TTM)**: `Sum(Brokerage_GP, 4Q) / Sum(SIS_6, 4Q)` (Biên lợi nhuận gộp mảng môi giới: Lãi môi giới / Doanh thu môi giới.)
- **Gross Profit Margin** (Biên Lợi Nhuận Gộp): `GP / Revenue`
    - **Investment Margin**: `Inv_GP / (SIS_1 + SIS_2 + SIS_4)` (Lãi thuần đầu tư / Tổng doanh thu đầu tư.)
    - **Lending Margin**: `Lending_GP / SIS_3` (Lãi thuần cho vay / Doanh thu lãi vay.)
    - **Brokerage Margin**: `Brokerage_GP / SIS_6` (Lãi thuần môi giới / Doanh thu môi giới.)
    - **IB Margin**: `IB_GP / (SIS_7_1 + SIS_7_2 + SIS_8 + SIS_10)` (Lãi thuần IB / Doanh thu IB.)
- **CIR (Cost to Income Ratio)**: `(SIS_40 + SIS_62) / SIS_20` (Chi phí hoạt động + QLDN / Tổng doanh thu. *Lưu ý: SIS_40 trong báo cáo thường bao gồm cả chi phí trực tiếp, cần tách nếu muốn tính CIR chuẩn bank, nhưng với CTCK thường dùng Tổng CP / Tổng Doanh Thu*.)

---

### Ghi chú về dữ liệu nguồn (Source Data Mapping)
Để tính toán các công thức trên từ dữ liệu thô (Raw Data), bạn cần ánh xạ các khoản mục từ Báo cáo tài chính (Entity Type: **SECURITY**):

**Tài Sản (Balance Sheet / SBS):**
- **FVTPL**: `SBS_112`
- **HTM**: `SBS_113`
- **AFS**: `SBS_115`
- **Loans (Cho vay)**: `SBS_114`
- **Total Assets**: `SBS_270`
- **Total Equity**: `SBS_400`

**Kết Quả Kinh Doanh (Income Statement / SIS):**
- **Revenue (Doanh thu)**: `SIS_20`
- **Investment Rev**: `SIS_1` (FVTPL) + `SIS_2` (HTM) + `SIS_4` (AFS)
- **Lending Rev**: `SIS_3` (HTKD khác - thường là lãi vay margin)
- **Brokerage Rev**: `SIS_6`
- **IB Rev**: `SIS_7_1` + `SIS_7_2` (Bảo lãnh/Đại lý) + `SIS_8` (Tư vấn ĐT) + `SIS_10` (Tư vấn TC)
- **Expenses (Chi phí)**: `SIS_40`
    - **Inv Exp**: `SIS_21` (FVTPL) + `SIS_22` (HTM) + `SIS_24` (Dự phòng)
    - **Lending Exp**: `SIS_22_1` (Chi phí lãi vay/Lỗ cho vay)
    - **Brokerage Exp**: `SIS_27`
    - **IB Exp**: `SIS_28` + `SIS_29`
    - **Financial Exp (CP Tài chính)**: `SIS_60`
    - **G&A Exp (CP Quản lý)**: `SIS_62`
    - **Other Net Income (KQ Khác)**: `SIS_80`

---

### 5. Tổng Hợp Công Thức Quan Trọng (Summary & Conclusion)

Bảng tổng hợp nhanh các công thức quan trọng theo yêu cầu.

#### Capital & Structure
- **Leverage**: `SBS_270 / SBS_400`
- **Total loans/Total equity**: `SBS_114 / SBS_400`
- **Investment portfolio/Total assets**: `(SBS_112 + SBS_113 + SBS_115) / SBS_270`
- **Total loan/Total asset**: `SBS_114 / SBS_270`

#### Profitability (TTM)
- **ROAE**: `Sum(SIS_200, 4Q) / Avg(SBS_400, 5Q)`
- **ROAA**: `Sum(SIS_200, 4Q) / Avg(SBS_270, 5Q)`
- **Investment Yield**: `Sum(SIS_1+SIS_2+SIS_4, 4Q) / Avg(SBS_112+SBS_113+SBS_115, 5Q)`
- **Net Investment Yield**: `Sum((SIS_1-SIS_21)+(SIS_2-SIS_22)+(SIS_4-SIS_24), 4Q) / Avg(...)`
- **Loan Yield**: `Sum(SIS_3, 4Q) / Avg(SBS_114, 5Q)`
- **Net Loan Yield**: `Sum(SIS_3 - SIS_22_1, 4Q) / Avg(SBS_114, 5Q)`
- **Net Broker Yield**: `Sum(SIS_6 - SIS_27, 4Q) / Sum(SIS_6, 4Q)`
- **Funding Cost**: `Sum(SIS_52, 4Q) / Avg(SBS_311 + SBS_341, 5Q)`

#### Scale
- **Total Investment**: `SBS_112 + SBS_113 + SBS_115`
- **FVTPL**: `SBS_112`
- **HTM**: `SBS_113`
- **AFS**: `SBS_115`
- **Total Loan**: `SBS_114`
- **Total Debt**: `SBS_311 + SBS_341`
- **Total Asset**: `SBS_270`

#### Income Statement Breakdown
- **Rev** (Doanh thu): `SIS_20`
- **Gross Profit**: `SIS_50_1` (hoặc `SIS_20 - SIS_40`)
- **Income from FVTPL**: `SIS_1`
- **Income from HTM**: `SIS_2`
- **Income from Loan**: `SIS_3`
- **CIR (CP HĐ, QLDN)/ Rev**: `(SIS_40 + SIS_62) / SIS_20`
- **NPATMI**: `SIS_201`
