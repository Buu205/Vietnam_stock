# Từ điển Công thức Ngân hàng (Formula Bank)

> Tài liệu này mô tả chi tiết các công thức tính toán chỉ số tài chính.

### YTD NII (`Ca.1`)
*   **Định nghĩa**: YTD NII - I. Thu nhập lãi thuần
*   **Mã chuẩn (Registry)**: `BIS_3`
*   **Thành phần**:
    *   Thu nhập lãi thuần (`Is.3`)
*   **Công thức**: `Tổng(Is.3)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 436.

### YTD Fees (`Ca.2`)
*   **Định nghĩa**: YTD Fees - VII. Thu nhập phí
*   **Mã chuẩn (Registry)**: `BIS_16`
*   **Thành phần**:
    *   Thu nhập lãi thuần từ hoạt động dịch vụ (`Is.6`)
*   **Công thức**: `Tổng(Is.6)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 437.

### YTD TOI (`Ca.3`)
*   **Định nghĩa**: YTD TOI - Tổng thu nhập hoạt động
*   **Mã chuẩn (Registry)**: `BIS_14A`
*   **Thành phần**:
    *   Tổng thu nhập hoạt động (`Is.14`): `BIS_14A`
*   **Công thức**: `Tổng(BIS_14A)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 438.

### YTD OPEX (`Ca.4`)
*   **Định nghĩa**: YTD OPEX - VIII. Chi phí hoạt động
*   **Mã chuẩn (Registry)**: `BIS_14`
*   **Thành phần**:
    *   Chi phí quản lý doanh nghiệp (`Is.15`)
*   **Công thức**: `Tổng(Is.15)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 439.

### YTD PPOP (`Ca.5`)
*   **Định nghĩa**: YTD PPOP - XII. Chi phí thuế TNDN
*   **Mã chuẩn (Registry)**: `BIS_20`
*   **Thành phần**:
    *   Lợi nhuận thuần từ hoạt động kinh doanh trước chi phí dự phòng rủi ro tín dụng (`Is.16`)
*   **Công thức**: `Tổng(Is.16)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 440.

### YTD PBT (`Ca.6`)
*   **Định nghĩa**: YTD PBT - XI. Tổng lợi nhuận trước thuế
*   **Mã chuẩn (Registry)**: `BIS_17`
*   **Thành phần**:
    *   Lợi nhuận trước thuế (`Is.18`)
*   **Công thức**: `Tổng(Is.18)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 441.

### YTD NPATMI (`Ca.7`)
*   **Định nghĩa**: YTD NPATMI - Cổ đông của Công ty mẹ
*   **Mã chuẩn (Registry)**: `BIS_22A`
*   **Thành phần**:
    *   Lợi nhuận sau thuế của cổ đông công ty mẹ (`Is.24`)
*   **Công thức**: `Tổng(Is.24)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 442.

### Customer LDR (`Ca.8`)
*   **Định nghĩa**: Customer LDR
*   **Mã chuẩn (Registry)**: `BIS_10`
*   **Thành phần**:
    *   Tiền gửi của khách hàng (`Bs.56`)
    *   Cho vay khách hàng (`Bs.13`): `BNOT_45_6`
*   **Công thức**: `BNOT_45_6/Bs.56`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 443.

### CASA (`Ca.9`)   
*   **Định nghĩa**: CASA
*   **Thành phần**:
    *   Tiền gửi không kỳ hạn (`Nt.121`): `BNOT_25_1_1`
    *   Tiền gửi theo loại hình (`Nt.120`)
    *   Tiền gửi vốn chuyên dùng (`Nt.125`): `BNOT_26_3`
    *   Tiền gửi ký quỹ (`Nt.124`): `BNOT_26_5`
*   **Công thức**: `(BNOT_25_1_1+BNOT_26_5+BNOT_26_3)/Nt.120`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 444.

### Cate 2 loan % (`Ca.10`)
*   **Định nghĩa**: Cate 2 loan %
*   **Thành phần**:
    *   Dư nợ cho vay theo nhóm nợ (`Nt.65`)
    *   Nợ cần chú ý (Nhóm 2) (`Nt.67`)
*   **Công thức**: `Nt.67/Nt.65`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 445.

### NPL (3-5) (`Ca.11`)
*   **Định nghĩa**: NPL (3-5)
*   **Thành phần**:
    *   Nợ có khả năng mất vốn (Nhóm 5) (`Nt.70`)
    *   Nợ nghi ngờ (Nhóm 4) (`Nt.69`)
    *   Cho vay khách hàng (`Bs.13`): `BNOT_45_6`
    *   Nợ dưới tiêu chuẩn (Nhóm 3) (`Nt.68`)
*   **Công thức**: `(Nt.68+Nt.69+Nt.70)/BNOT_45_6`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 446.

### VAMC % of loan (`Ca.12`)
*   **Định nghĩa**: VAMC % of loan
*   **Thành phần**:
    *   Dư nợ cho vay theo nhóm nợ (`Nt.65`)
    *   Trái phiếu đặc biệt do VAMC phát hành (`Nt.114`): `BNOT_13_3`
*   **Công thức**: `BNOT_13_3/Nt.65`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 447.

### CIR (`Ca.13`)
*   **Định nghĩa**: CIR
*   **Thành phần**:
    *   Chi phí quản lý doanh nghiệp (`Is.15`)
    *   Tổng thu nhập hoạt động (`Is.14`): `BIS_14A`
*   **Công thức**: `-Is.15/BIS_14A`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 448.

### LLR (`Ca.14`)
*   **Định nghĩa**: LLR
*   **Thành phần**:
    *   Nợ có khả năng mất vốn (Nhóm 5) (`Nt.70`)
    *   Nợ nghi ngờ (Nhóm 4) (`Nt.69`)
    *   Less: Provision for losses on loans and advances to customers (`Bs.14`)
    *   Nợ dưới tiêu chuẩn (Nhóm 3) (`Nt.68`)
*   **Công thức**: `-Bs.14/(Nt.68+Nt.69+Nt.70)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 449.

### Total Credit * (`Ca.15`)
*   **Định nghĩa**: Total Credit *
*   **Thành phần**:
    *   Chứng khoán nợ do các tổ chức kinh tế trong nước phát hành (`Nt.112`)
    *   Mua nợ (`Bs.16`)
    *   Cho vay khách hàng (`Bs.13`): `BNOT_45_6`
    *   Chứng khoán do các tổ chức kinh tế trong nước phát hành (`Nt.97`)
*   **Công thức**: `BNOT_45_6+Nt.97+Nt.112+Bs.16`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 450.

### Provision / Total loan (`Ca.16`)
*   **Định nghĩa**: Provision / Total loan
*   **Thành phần**:
    *   Less: Provision for losses on loans and advances to customers (`Bs.14`)
    *   Cho vay khách hàng (`Bs.13`): `BNOT_45_6`
*   **Công thức**: `-Bs.14/BNOT_45_6`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 451.

### Receivable/ Total loan (`Ca.17`)
*   **Định nghĩa**: Receivable/ Total loan
*   **Thành phần**:
    *   Lãi và phí phải thu (`Bs.44`)
    *   Trái phiếu bình quân (`Ca.39`)
    *   Cho vay khách hàng (`Ca.35`): `BNOT_45_6`
*   **Công thức**: `Bs.44/(BNOT_45_6+Ca.39)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 452.

### Interbank deposit/ Customer deposit (`Ca.18`)
*   **Định nghĩa**: Interbank deposit/ Customer deposit
*   **Thành phần**:
    *   Tiền gửi tại các TCTD khác (`Bs.5`): `BNOT_3_1`
    *   Tiền gửi của khách hàng (`Bs.56`)
    *   Tiền gửi và vay các tổ chức tín dụng khác (`Bs.54`)
*   **Công thức**: `(BNOT_3_14-BNOT_3_1)/BNOT_3_16`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 453.

### Leverage (`Ca.19`)
*   **Định nghĩa**: Leverage
*   **Thành phần**:
    *   Vốn chủ sở hữu (`Bs.65`)
    *   Tổng tài sản (`Bs.1`)
*   **Công thức**: `Bs.1/Bs.65`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 454.

### Interest earning asset (`Ca.20`)
*   **Định nghĩa**: Interest earning asset
*   **Thành phần**:
    *   Chứng khoán sẵn sàng để bán (`Bs.19`)
    *   Tiền gửi tại các TCTD khác (`Bs.5`): `BNOT_3_1`
    *   Tiền gửi tại NHNN (`Bs.3`): `BCFD_9A`
    *   Mua nợ (`Bs.16`)
    *   Chứng khoán giữ đến ngày đáo hạn (`Bs.20`): `BNOT_13_2`
    *   Cho vay khách hàng (`Bs.13`): `BNOT_45_6`
    *   Cho vay các TCTD khác (`Bs.6`): `BNOT_3_2`
    *   Chứng khoán kinh doanh (`Bs.9`)
*   **Công thức**: `BCFD_9A+BNOT_3_1+Bs.9+BNOT_45_6+Bs.19+Bs.16+BNOT_13_2+BNOT_3_2`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 455.

### Interest bearing liability (`Ca.21`)
*   **Định nghĩa**: Interest bearing liability
*   **Thành phần**:
    *   Phát hành giấy tờ có giá (`Bs.59`)
    *   Deposits and Loans from other credit institutions (`Bs.53`)
    *   Tiền gửi của khách hàng (`Bs.56`)
    *   Vay chính phủ và NHNN (`Bs.52`)
    *   Vốn tài trợ, ủy thác đầu tư (`Bs.58`)
*   **Công thức**: `Bs.52+Bs.53+Bs.56+Bs.59+Bs.58`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 456.

### Avg. IEA (`Ca.22`)
*   **Định nghĩa**: Avg. IEA
*   **Công thức**: `AVERAGE(C455,IF(C$8=1,INDEX($A455:$XDQ455,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A455:$XDQ455,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A455:$XDQ455,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 457.

### Avg. IBL (`Ca.23`)
*   **Định nghĩa**: Avg. IBL
*   **Công thức**: `AVERAGE(C456,IF(C$8=1,INDEX($A456:$XDQ456,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A456:$XDQ456,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A456:$XDQ456,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 458.

### Avg. Asset Yield (`Ca.24`)
*   **Định nghĩa**: Avg. Asset Yield
*   **Công thức**: `IF(C8=5,C120/C457,C120*4/C457)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 459.

### Avg. Funding Cost (`Ca.25`)
*   **Định nghĩa**: Avg. Funding Cost
*   **Công thức**: `IF(C8=5,-C121/C458,-C121*4/C458)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 460.

### NIM (`Ca.26`)
*   **Định nghĩa**: NIM
*   **Công thức**: `IF(C8=5,C122/C457,C122/C457*4)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 461.

### NII/TOI (`Ca.27`)
*   **Định nghĩa**: NII/TOI
*   **Công thức**: `C436/C438`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 462.

### Provision/PPOP (`Ca.28`)
*   **Định nghĩa**: Provision/PPOP
*   **Thành phần**:
    *   Lợi nhuận thuần từ hoạt động kinh doanh trước chi phí dự phòng rủi ro tín dụng (`Is.16`)
    *   Provision for credit losses (`Is.17`)
*   **Công thức**: `-Is.17/Is.16`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 463.

### Avg.Total Asset (`Ca.29`)
*   **Định nghĩa**: Avg.Total Asset
*   **Công thức**: `AVERAGE(C14,IF(C$8=1,INDEX($A14:$XDQ14,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A14:$XDQ14,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A14:$XDQ14,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 464.

### Avg. Total Equity (`Ca.30`)
*   **Định nghĩa**: Avg. Total Equity
*   **Công thức**: `AVERAGE(C78,IF(C$8=1,INDEX($A78:$XDQ78,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A78:$XDQ78,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A78:$XDQ78,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 465.

### ROAA (`Ca.31`)
*   **Định nghĩa**: ROAA
*   **Công thức**: `IF(C8=5,C141/C464,C141*4/C464)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 466.

### ROAE (`Ca.32`)
*   **Định nghĩa**: ROAE
*   **Công thức**: `IF(C8=5,C143/C465,C143*4/C465)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 467.

### YTD Debt interest Income (`Ca.33`)
*   **Định nghĩa**: YTD Debt interest Income
*   **Thành phần**:
    *   Interest income from debt securities (`Nt.145`)
*   **Công thức**: `Tổng(Nt.145)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 468.

### Adj NIM (for bond book) (`Ca.34`)
*   **Định nghĩa**: Adj NIM (for bond book)
*   **Công thức**: `IF(C8=5,(C436-C468)/C457,(C436-C468)/C457*4/C8)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 469.

### Customer loan (`Ca.35`)
*   **Định nghĩa**: Customer loan
*   **Thành phần**:
    *   Mua nợ (`Bs.16`)
    *   Cho vay khách hàng (`Bs.13`): `BNOT_45_6`
*   **Công thức**: `BNOT_45_6+Bs.16`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 470.

### Avg Customer loan (`Ca.36`)
*   **Định nghĩa**: ="Avg " &B470
*   **Công thức**: `AVERAGE(C470,IF(C$8=1,INDEX($A470:$XDQ470,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A470:$XDQ470,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A470:$XDQ470,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 471.

### Loan yield (`Ca.37`)
*   **Định nghĩa**: Loan yield
*   **Công thức**: `IF(C8=5,C357/C471,C357/C471*4)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 472.

### Total bond (`Ca.38`)
*   **Định nghĩa**: Total bond
*   **Thành phần**:
    *   Chứng khoán sẵn sàng để bán (`Bs.19`)
    *   Chứng khoán giữ đến ngày đáo hạn (`Bs.20`): `BNOT_13_2`
    *   Chứng khoán kinh doanh (`Bs.9`)
*   **Công thức**: `Bs.9+Bs.19+BNOT_13_2`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 473.

### Avg Total bond (`Ca.39`)
*   **Định nghĩa**: ="Avg " &B473
*   **Công thức**: `AVERAGE(C473,IF(C$8=1,INDEX($A473:$XDQ473,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A473:$XDQ473,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A473:$XDQ473,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 474.

### Bond yield (`Ca.40`)
*   **Định nghĩa**: Bond yield
*   **Công thức**: `IF(C8=5,C359/C474,C359/C474*4)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 475.

### Total deposit on asset (`Ca.41`)
*   **Định nghĩa**: Total deposit on asset
*   **Thành phần**:
    *   Tiền gửi tại các TCTD khác (`Bs.5`): `BNOT_3_1`
    *   Tiền gửi tại NHNN (`Bs.3`): `BCFD_9A`
    *   Cho vay các TCTD khác (`Bs.6`): `BNOT_3_2`
*   **Công thức**: `BNOT_3_1+BCFD_9A+BNOT_3_2`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 476.

### Avg Total deposit on asset (`Ca.42`)
*   **Định nghĩa**: ="Avg " &B476
*   **Công thức**: `AVERAGE(C476,IF(C$8=1,INDEX($A476:$XDQ476,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A476:$XDQ476,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A476:$XDQ476,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 477.

### Deposit yield (`Ca.43`)
*   **Định nghĩa**: Deposit yield
*   **Công thức**: `IF(C8=5,C358/C477,C358/C477*4)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 478.

### Total deposit (`Ca.44`)
*   **Định nghĩa**: Total deposit
*   **Thành phần**:
    *   Tiền gửi của khách hàng (`Bs.56`)
    *   Tiền gửi và vay các tổ chức tín dụng khác (`Bs.54`)
*   **Công thức**: `Bs.54+Bs.56`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 479.

### Avg Total deposit (`Ca.45`)
*   **Định nghĩa**: ="Avg " &B479
*   **Công thức**: `AVERAGE(C479,IF(C$8=1,INDEX($A479:$XDQ479,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A479:$XDQ479,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A479:$XDQ479,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 480.

### COF from deposit (`Ca.46`)
*   **Định nghĩa**: COF from deposit
*   **Công thức**: `IF(C$8=5,C365/C480,C365/C480*4)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 481.

### Total loan on liabilities (`Ca.47`)
*   **Định nghĩa**: Total loan on liabilities
*   **Thành phần**:
    *   Vay chính phủ và NHNN (`Bs.52`)
    *   Vốn tài trợ, ủy thác đầu tư (`Bs.58`)
    *   Loans from other credit institutions (`Bs.55`)
*   **Công thức**: `Bs.52+Bs.58+Bs.55`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 482.

### Avg Total loan on liabilities (`Ca.48`)
*   **Định nghĩa**: ="Avg " &B482
*   **Công thức**: `AVERAGE(C482,IF(C$8=1,INDEX($A482:$XDQ482,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A482:$XDQ482,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A482:$XDQ482,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 483.

### COF from loan (`Ca.49`)
*   **Định nghĩa**: COF from loan
*   **Công thức**: `IF(C8=5,(C366+C368)/C483,(C366+C368)/C483*4)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 484.

### Total valuable paper (`Ca.50`)
*   **Định nghĩa**: Total valuable paper
*   **Thành phần**:
    *   Phát hành giấy tờ có giá (`Bs.59`)
*   **Công thức**: `Bs.59`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 485.

### Avg Total valuable paper (`Ca.51`)
*   **Định nghĩa**: ="Avg " &B485
*   **Công thức**: `AVERAGE(C485,IF(C$8=1,INDEX($A485:$XDQ485,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A485:$XDQ485,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A485:$XDQ485,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 486.

### COF from valuable paper (`Ca.52`)
*   **Định nghĩa**: COF from valuable paper
*   **Công thức**: `IF(C8=5,(C367)/C485,(C367)/C485*4)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 487.

### Credit cost (`Ca.53`)
*   **Định nghĩa**: Credit cost
*   **Thành phần**:
    *   Provision for credit losses (`Is.17`)
*   **Công thức**: `IF(C8=5,-Is.17/AVERAGE(C26,IF(C$8=1,INDEX($A26:$XDQ26,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A26:$XDQ26,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A26:$XDQ26,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0))))),-Is.17/AVERAGE(C26,IF(C$8=1,INDEX($A26:$XDQ26,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A26:$XDQ26,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A26:$XDQ26,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))*4)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 488.

### Fees Income/ Total asset (`Ca.54`)
*   **Định nghĩa**: Fees Income/ Total asset
*   **Công thức**: `IF(C8=5,C125/C464,C125/C464*4)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 489.

### LDR (`Ca.55`)
*   **Định nghĩa**: LDR
*   **Công thức**: `(C26+C32+C33+C22)/(C69+C72)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 490.

### Fees Income/ Total loan (`Ca.56`)
*   **Định nghĩa**: Fees Income/ Total loan
*   **Công thức**: `IF(C8=5,C125/C471,C125/C464*4)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 491.

### NPL formation (`Ca.57`)
*   **Định nghĩa**: NPL formation
*   **Công thức**: `IF(C$8=5,C$446*C$26-C$526-INDEX($26:$26,MATCH(C$9&"Q"&C$8&C$7-1,$1:$1,0))*INDEX($446:$446,MATCH(C$9&"Q"&C$8&C$7-1,$1:$1,0)),C$446*C$26-C$526-IF(C8=1,INDEX($26:$26,MATCH(C$9&"Q5"&C$7-1,$1:$1,0))*INDEX($446:$446,MATCH(C$9&"Q5"&C$7-1,$1:$1,0)),INDEX($26:$26,MATCH(C$9&"Q"&C$8-1&C$7,$1:$1,0))*INDEX($446:$446,MATCH(C$9&"Q"&C$8-1&C$7,$1:$1,0))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 492.

### NPL formation (%) (`Ca.58`)
*   **Định nghĩa**: NPL formation (%)
*   **Công thức**: `C492/IF(C$8=5,INDEX($26:$26,MATCH(C$9&"Q"&C$8&C$7-1,$1:$1,0)),IF(C$8=1,INDEX($26:$26,MATCH(C$9&"Q"&4&C$7-1,$1:$1,0)),INDEX($26:$26,MATCH(C$9&"Q"&C$8-1&C$7,$1:$1,0))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 493.

###  (`Ca.59`)
*   **Công thức**: `C26+C32+C33+C22`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 494.

###  (`Ca.60`)
*   **Công thức**: `C69+C72`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 495.

### Fair LDR (`Ca.61`)
*   **Định nghĩa**: Fair LDR
*   **Thành phần**:
    *   Phát hành giấy tờ có giá (`Bs.59`)
    *   Tiền gửi của khách hàng (`Bs.56`)
    *   Loans and advances to customers, net (`Bs.12`)
    *   Chứng khoán do các tổ chức kinh tế trong nước phát hành (`Nt.97`)
*   **Công thức**: `(Nt.97+Bs.12)/(Bs.56+Bs.59)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 496.

### Liquidity Reserve (`Ca.62`)
*   **Định nghĩa**: Liquidity Reserve
*   **Thành phần**:
    *   Tiền gửi tại NHNN (`Bs.3`): `BCFD_9A`
    *   Tiền mặt, vàng bạc, đá quý (`Bs.2`): `BNOT_1`
    *   Trái phiếu chính phủ (`Nt.109`)
    *   Trái phiếu chính phủ (`Nt.3`)
    *   Trái phiếu chính phủ (`Nt.94`)
    *   Trái phiếu được chính phủ bảo lãnh (`Nt.110`)
    *   Trái phiếu được chính phủ bảo lãnh (`Nt.4`)
    *   Trái phiếu được chính phủ bảo lãnh (`Nt.95`)
    *   Tổng nợ phải trả (`Bs.51`)
*   **Công thức**: `(BNOT_1+BCFD_9A+Nt.94+Nt.3+Nt.4+Nt.95+Nt.109+Nt.110)/Bs.51`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 497.

### NIM Diff (`Ca.63`)
*   **Định nghĩa**: NIM Diff
*   **Công thức**: `C461-IF(C$8=1,INDEX($A461:$XDQ461,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A461:$XDQ461,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A461:$XDQ461,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 498.

### IAE Diff (`Ca.64`)
*   **Định nghĩa**: IAE Diff
*   **Công thức**: `C455-IF(C$8=1,INDEX($A455:$XDQ455,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A455:$XDQ455,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A455:$XDQ455,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 499.

###  (`ca.65`)
*   **Công thức**: `(-LN(C499)/C498)/4`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 500.

### Total GB (`Ca.66`)
*   **Định nghĩa**: Total GB
*   **Công thức**: `C218+C217+C308+C309+C323+C324`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 501.

### Average GB (`ca.67`)
*   **Định nghĩa**: Average GB
*   **Công thức**: `AVERAGE(C501,IF(C$8=1,INDEX($A501:$XDQ501,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A501:$XDQ501,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A501:$XDQ501,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 502.

### Total BB (`ca.68`)
*   **Định nghĩa**: Total BB
*   **Công thức**: `C219+C310+C325`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 503.

### Average BB (`ca.69`)
*   **Định nghĩa**: Average BB
*   **Công thức**: `AVERAGE(C503,IF(C$8=1,INDEX($A503:$XDQ503,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A503:$XDQ503,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A503:$XDQ503,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 504.

### Total CB (`ca.70`)
*   **Định nghĩa**: Total CB
*   **Công thức**: `C220+C326+C311`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 505.

### Average CB (`ca.71`)
*   **Định nghĩa**: Average CB
*   **Công thức**: `AVERAGE(C505,IF(C$8=1,INDEX($A505:$XDQ505,MATCH(C$9&"Q4"&(C$7-1),$1:$1,0)),IF(C$8=5,INDEX($A505:$XDQ505,MATCH(C$9&"Q5"&(C$7-1),$1:$1,0)),INDEX($A505:$XDQ505,MATCH(C$9&"Q"&(C$8-1)&(C$7),$1:$1,0)))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 506.

### Liquidity Coverage Ratio (`Ca.72`)
*   **Định nghĩa**: Liquidity Coverage Ratio
*   **Thành phần**:
    *   Tiền gửi tại NHNN (`Bs.3`): `BCFD_9A`
    *   Tiền mặt, vàng bạc, đá quý (`Bs.2`): `BNOT_1`
    *   Trái phiếu chính phủ (`Nt.109`)
    *   Trái phiếu chính phủ (`Nt.3`)
    *   Trái phiếu chính phủ (`Nt.94`)
    *   Trái phiếu được chính phủ bảo lãnh (`Nt.110`)
    *   Trái phiếu được chính phủ bảo lãnh (`Nt.4`)
    *   Trái phiếu được chính phủ bảo lãnh (`Nt.95`)
*   **Công thức**: `(BNOT_1+BCFD_9A+Nt.94+Nt.3+Nt.4+Nt.95+Nt.109+Nt.110)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 507.

### G2 formation (`Ca.73`)
*   **Định nghĩa**: G2 formation
*   **Công thức**: `IF(C$8=5,C$445*C$26+C$492-INDEX($26:$26,MATCH(C$9&"Q"&C$8&C$7-1,$1:$1,0))*INDEX($445:$445,MATCH(C$9&"Q"&C$8&C$7-1,$1:$1,0)),C$445*C$26+C$492-IF(C8=1,INDEX($26:$26,MATCH(C$9&"Q5"&C$7-1,$1:$1,0))*INDEX($445:$445,MATCH(C$9&"Q5"&C$7-1,$1:$1,0)),INDEX($26:$26,MATCH(C$9&"Q"&C$8-1&C$7,$1:$1,0))*INDEX($445:$445,MATCH(C$9&"Q"&C$8-1&C$7,$1:$1,0))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 508.

### G2 formation (%) (`Ca.74`)
*   **Định nghĩa**: G2 formation (%)
*   **Công thức**: `C508/IF(C$8=5,INDEX($26:$26,MATCH(C$9&"Q"&C$8&C$7-1,$1:$1,0)),IF(C$8=1,INDEX($26:$26,MATCH(C$9&"Q"&5&C$7-1,$1:$1,0)),INDEX($26:$26,MATCH(C$9&"Q"&C$8-1&C$7,$1:$1,0))))`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 509.

### Banca income (`Ca.75`)
*   **Định nghĩa**: Banca income
*   **Thành phần**:
    *   Chi phí hoạt động kinh doanh bảo hiểm (`Nt.167`)
    *   Thu nhập từ hoạt động kinh doanh bảo hiểm (`Nt.160`)
*   **Công thức**: `(Nt.160+Nt.167)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 510.

### Credit card income (`Ca.76`)
*   **Định nghĩa**: Credit card income
*   **Thành phần**:
    *   Chi phí hoạt động thanh toán (`Nt.163`)
    *   Thu nhập từ hoạt động thanh toán (`Nt.156`)
*   **Công thức**: `(Nt.156+Nt.163)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 511.

### Treasury income (`Ca.77`)
*   **Định nghĩa**: Treasury income
*   **Thành phần**:
    *   Chi phí hoạt động kinh doanh vốn (`Nt.164`)
    *   Thu nhập từ hoạt động kinh doanh vốn (`Nt.157`)
*   **Công thức**: `(Nt.157+Nt.164)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 512.

### Guarantee services (`Ca.78`)
*   **Định nghĩa**: Guarantee services
*   **Thành phần**:
    *   Chi phí hoạt động bảo lãnh (`Nt.165`)
    *   Thu nhập từ hoạt động bảo lãnh (`Nt.158`)
*   **Công thức**: `(Nt.158+Nt.165)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 513.

### Agency services (`Ca.79`)
*   **Định nghĩa**: Agency services
*   **Thành phần**:
    *   Chi phí hoạt động đại lý (`Nt.166`)
    *   Thu nhập từ hoạt động đại lý (`Nt.159`)
*   **Công thức**: `(Nt.159+Nt.166)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 514.

### Others (`Ca.80`)
*   **Định nghĩa**: Others
*   **Thành phần**:
    *   Chi phí môi giới (`Nt.168`)
    *   Expenses on Other services (`Nt.169`)
    *   Thu nhập môi giới (`Nt.161`)
    *   Income from Other services (`Nt.162`)
*   **Công thức**: `(Nt.162+Nt.169)+(Nt.161+Nt.168)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 515.

### NoII (`Ca.81`)
*   **Định nghĩa**: NoII
*   **Thành phần**:
    *   Thu nhập lãi thuần (`Is.3`)
    *   Tổng thu nhập hoạt động (`Is.14`): `BIS_14A`
*   **Công thức**: `BIS_14A-Is.3`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 516.

### Net VAMC (`Ca.82`)
*   **Định nghĩa**: Net VAMC
*   **Thành phần**:
    *   Dự phòng trái phiếu đặc biệt (`Nt.119`): `BNOT_13_3_2`
    *   Trái phiếu đặc biệt do VAMC phát hành (`Nt.114`): `BNOT_13_3`
*   **Công thức**: `BNOT_13_3+BNOT_13_3_2`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 517.

### Abs NPL (`Ca.83`)
*   **Định nghĩa**: Abs NPL
*   **Thành phần**:
    *   Nợ có khả năng mất vốn (Nhóm 5) (`Nt.70`)
    *   Nợ nghi ngờ (Nhóm 4) (`Nt.69`)
    *   Nợ dưới tiêu chuẩn (Nhóm 3) (`Nt.68`)
*   **Công thức**: `(Nt.68+Nt.69+Nt.70)`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 518.

### Group 5 % (`Ca.84`)
*   **Định nghĩa**: Group 5 %
*   **Thành phần**:
    *   Nợ có khả năng mất vốn (Nhóm 5) (`Nt.70`)
    *   Dư nợ cho vay theo nhóm nợ (`Nt.65`)
*   **Công thức**: `Nt.70/Nt.65`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 519.

### Short loan/ Total loan (`Ca.85`)
*   **Định nghĩa**: Short loan/ Total loan
*   **Công thức**: `C286/C285`
*   *Ghi chú*: Dữ liệu nguồn từ `DATA1` Row 520.
