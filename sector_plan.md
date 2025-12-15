# Sector Analysis Implementation Plan
# Kế Hoạch Triển Khai Phân Tích Ngành

> **Status**: Draft
> **Date**: 2025-12-14
> **Author**: Antigravity Agent

---

## 1. Tổng Quan / Overview

Mục tiêu là xây dựng hệ thống tính toán chỉ số tài chính (FA) và kỹ thuật/định giá (TA) ở cấp độ **Ngành (Sector)**.
The goal is to build a calculation system for Financial (FA) and Technical/Valuation (TA) metrics at the **Sector level**.

### Yêu Cầu Chính / Key Requirements

1.  **Phân Tích Cơ Bản (FA)**:
    -   Tổng hợp dữ liệu từ các công ty con trong ngành.
    -   Phương pháp: **Weighted Aggregation** (Cộng dồn tử số và mẫu số).
    -   Ví dụ: Sector Gross Margin = $\frac{\sum \text{Gross Profit}}{\sum \text{Net Revenue}}$ (thay vì trung bình cộng các margin).
2.  **Phân Tích Kỹ Thuật/Định Giá (TA)**:
    -   Tính toán chỉ số định giá ngành (Sector PE, PB, PS, EV/EBITDA).
    -   Hỗ trợ hiển thị dạng "Candlestick Distribution" (Box Plot/Historical Range) tương tự `bank_dashboard.py`.
3.  **Kiến Trúc**:
    -   Module tính toán riêng biệt (`PROCESSORS/sector/`).
    -   Lưu trữ kết quả dạng Parquet để UI (Streamlit) và AI Agent (MCP) sử dụng.

---

## 2. Kiến Trúc Hệ Thống / System Architecture

### 2.1 Luồng Dữ Liệu / Data Flow

```mermaid
graph LR
    A[Company/Bank/Security\nMetrics Parquet] --> B(Sector Calculator)
    C[Sector Registry\n(Mappings)] --> B
    D[Market Cap / Price Data] --> B
    B --> E[Sector FA Metrics\nParquet]
    B --> F[Sector Valuation\nParquet]
    E --> G[Streamlit Dashboard]
    F --> G
    E --> H[MCP Agent]
    F --> H
```

### 2.2 Cấu Trúc Thư Mục / Directory Structure

```
PROCESSORS/
└── sector/
    ├── __init__.py
    ├── calculators/
    │   ├── fa_aggregator.py       # Aggregate Income/Balance Sheet
    │   └── valuation_aggregator.py # Aggregate PE/PB/PS
    └── sector_processor.py        # Main orchestration
```

---

## 3. Phương Pháp Tính Toán / Calculation Methodology

### 3.1 Phân Tích Cơ Bản (Fundamental Analysis)

**Nguyên tắc**: Sử dụng **Sum-Aggregation** (Cộng gộp).
**Principle**: Use **Sum-Aggregation**.

| Metric Type | Aggregation Logic | Example Formula |
|-------------|-------------------|-----------------|
| **Absolute Values**<br>(Revenue, Profit, Assets) | Sum of all constituents | `Sector_Revenue = SUM(Company_A_Rev, Company_B_Rev, ...)` |
| **Ratios**<br>(Margin, ROE, ROA) | Derived from Aggregates | `Sector_ROE = Sector_NetProfit / Sector_TotalEquity` |
| **Growth Rates** | Derived from Aggregates | `Sector_Rev_Growth = (Sector_Rev_t / Sector_Rev_t-1) - 1` |

**Xử lý dữ liệu không đồng nhất (Heterogeneous Data)**:
-   Ngành Tài chính (Financials) bao gồm Bank, Security, Insurance.
-   **Giải pháp**:
    -   Tính riêng các chỉ số đặc thù (Bank: NIM, NPL; Security: Brokerage Rev).
    -   Chỉ tổng hợp các chỉ số chung (Net Profit, Total Equity, Total Assets) cho cấp độ "Financials".
    -   Ở cấp độ sub-sector (VD: Ngành Ngân hàng), tổng hợp đầy đủ các chỉ số chuyên ngành.

### 3.2 Định Giá Ngành (Sector Valuation - TA)

Để vẽ biểu đồ Candlestick/Boxplot phân phối định giá, cần 2 loại dữ liệu:

#### A. Sector Time-Series (Chỉ số Ngành theo thời gian)
Tính PE/PB đại diện cho cả ngành theo thời gian.

$$ \text{Sector P/E}_t = \frac{\sum (\text{Market Cap}_i)_t}{\sum (\text{Earnings TTM}_i)_t} $$

-   **Input**: Market Cap hàng ngày, Earnings TTM hàng quý (fill-forward).
-   **Output**: Chuỗi thời gian PE ngành.
-   **Usage**: Vẽ đường xu hướng PE ngành, hoặc Candlestick lịch sử (Open/High/Low/Close của PE ngành trong 1 khoảng thời gian).

#### B. Cross-Sectional Distribution (Phân phối chéo)
Tính phân vị (percentiles) của các công ty trong ngành tại một thời điểm.

-   **Metrics**: Min, 25%, Median, 75%, Max của PE các cổ phiếu trong ngành.
-   **Output**: Dữ liệu thống kê mô tả.
-   **Usage**: Vẽ Boxplot so sánh sự phân hóa trong ngành.

**Note**: Yêu cầu "Candlestick like bank dashboard" trong `bank_dashboard.py` là dạng hiển thị **Historical Range** của từng mã hoặc của ngành (Candlestick biểu diễn vùng dao động giá trị lịch sử P25-P75). Plan này sẽ hỗ trợ tính toán Historical Percentiles cho Sector PE.

---

## 4. Đặc Tả Đầu Ra / Output Specification

### 4.1 File: `sector_fundamental_metrics.parquet`

| Column | Type | Description |
|--------|------|-------------|
| `sector_code` | string | Standardized sector name (e.g., "Banking") |
| `report_date` | date | Quarter end date |
| `net_revenue` | float | Sum of revenue (VND) |
| `net_profit` | float | Sum of profit (VND) |
| `total_assets` | float | Sum of assets (VND) |
| `gross_margin` | float | Calculated ratio |
| `roe` | float | Calculated ratio |
| ... | ... | Other aggregated metrics |

### 4.2 File: `sector_valuation_metrics.parquet`

| Column | Type | Description |
|--------|------|-------------|
| `sector_code` | string | Standardized sector name |
| `date` | date | Trading date |
| `sector_market_cap`| float | Sum of market caps |
| `sector_pe` | float | Market Cap / Earnings TTM |
| `sector_pb` | float | Market Cap / Book Value |
| `pe_median` | float | Median PE of constituents (optional) |
| `pb_median` | float | Median PB of constituents (optional) |

---

## 5. Kế Hoạch Thực Hiện / Implementation Steps

### Phase 1: Core Framework & Data Loading
1.  **Refactor Aggregators**:
    -   Update `fa_aggregator.py` to support specific modular logic for Bank, Securities, and Insurance.
    -   Implement `_load_metric_map()` using `metric_registry.json` for precise code mapping.
2.  **Ticker Verification**:
    -   Ensure explicit tickers (e.g., SSI, VCI -> Securities) are correctly routed to their respective logic.

### Phase 2: Fundamental Calculation (FA)
1.  **Bank Aggregation**:
    -   Implement "Super Bank" logic: Sum(Assets, Credit, Deposits).
    -   Calculate specialized ratios: NIM, NPL, LDR, CASA (from aggregated sums).
2.  **Securities Aggregation**:
    -   Implement Sum(Margin Loans, FVTPL, Revenue).
    -   Calculate Yields and Leverage.
3.  **Company Aggregation**:
    -   Loop through sub-sectors (Retail, Real Estate, etc.).
    -   Calculate Margins (Gross, Operating, Net) and SG&A ratios.

### Phase 3: Valuation Enhancements (TA)
1.  **Upgrade `vnindex_valuation_calculator.py`**:
    -   Load `net_revenue` metric.
    -   Implement **Sector PS** (Market Cap / TTM Revenue).
    -   Calculate **Sector PE, PB, PS** time series.
2.  **Historical Distribution**:
    -   Calculate 5-year Percentiles (5, 25, 50, 75, 95) for Sector PE/PB/PS.

### Phase 4: Visualization & Delivery
1.  **Streamlit Dashboard**:
    -   Build `pages/sector_dashboard.py`.
    -   Implement "Candlestick Valuation" chart (Historical Range).
    -   Implement Cross-Sectional Boxplots.
2.  **MCP Agent Tool**:
    -   Expose `get_sector_report(sector_name)` to provide AI summary.

### Phase 5: Verification / Kiểm Thử
1.  **Automated Script**: Chạy `run_sector_analysis.py` và kiểm tra log.
2.  **Metric Spot Check**:
    -   **Bank**: Verify Sector NPL calculation = Sum(Bad Debt)/Sum(Loans).
    -   **Securities**: Verify Sector Margin Loans total.
    -   **Valuation**: Verify Sector PS calculation.

---

## 6. Chi Tiết Công Thức / Detailed Formulas Request

### 6.1 Tổng Hợp Cơ Bản (Fundamental Aggregation)

Nguyên tắc chung: **Sum-Aggregation First, Ratio-Calculation Second**.
Tất cả các chỉ số ngành đều được tính từ tổng số liệu của các công ty thành phần.

#### A. Chỉ Số Tuyệt Đối (Absolute Metrics)
Hệ thống sẽ tổng hợp (Sum) các chỉ số sau từ báo cáo tài chính của từng công ty:

| Group | Method |
|-------|--------|
| **Absolute** | $$ \text{Sector Metric}_t = \sum_{i=1}^{N} \text{Company Metric}_{i,t} $$ |
| **Growth** | $$ \text{Growth}_t = \frac{\text{Sector Metric}_t - \text{Sector Metric}_{t-1}}{\text{Sector Metric}_{t-1}} $$ |

### 6.2 Định Giá Ngành (Sector Valuation)

Sử dụng phương pháp **Market Cap Weighted** (Tỷ trọng theo vốn hóa):

1.  **Sector P/E**: $\frac{\sum \text{Market Cap}}{\sum \text{Earnings (TTM)}}$
2.  **Sector P/B**: $\frac{\sum \text{Market Cap}}{\sum \text{Book Value}}$
3.  **Sector P/S**: $\frac{\sum \text{Market Cap}}{\sum \text{Revenue (TTM)}}$ (New)

### 6.3 Chi Tiết Công Thức Ngành Ngân Hàng (Banking Sector Specifics)
Áp dụng logic "Sector = Aggregated Super Bank".

*   **Size**: Total Assets, Total Credit (Loan+Bond), Customer Deposits.
*   **Asset Quality**: 
    *   Sector NPL = $\sum \text{Bad Debt} / \sum \text{Loans}$
    *   Sector LLCR = $\sum \text{Provisions} / \sum \text{Bad Debt}$
    *   Sector Credit Cost = $\sum \text{Prov Exp} / \sum \text{Avg Loans}$
*   **Capital/Liquidity**: 
    *   Sector LDR = $\sum \text{Loans} / \sum \text{Deposits}$
    *   Sector CASA = $\sum \text{CASA} / \sum \text{Deposits}$
*   **Efficiency**: 
    *   Sector NIM = $\sum \text{NII} / \sum \text{IEA}$
    *   Sector CIR = $\sum \text{OPEX} / \sum \text{TOI}$

### 6.4 Chi Tiết Công Thức Ngành Doanh Nghiệp (Company Sector Specifics)
Áp dụng cho từng sub-sector phi tài chính (Bất động sản, Bán lẻ, Xây dựng, v.v.).

*   **Margins**: Gross Margin, EBITDA Margin, EBIT Margin, Net Margin (All calculated from Aggregates).
*   **Efficiency**: SG&A / Revenue.
*   **Growth**: Revenue Growth, Profit Growth.

### 6.5 Chi Tiết Công Thức Ngành Chứng Khoán (Securities Sector Specifics)
Áp dụng cho ngành "Dịch vụ tài chính". *(Verified Tickers: SSI, VCI, HCM, VND...)*

*   **Scale**: Assets, Equity, Margin Loans, Prop Trading Assets (FVTPL).
*   **Income**: Total Revenue, Gross Profit, Prop Trading Income, Margin Income.
*   **Ratios**:
    *   Sector Leverage = Sum Assets / Sum Equity.
    *   Loan Yield = Margin Income / Avg Margin Loans.
    *   Inv Yield = Prop Trading Income / Avg Prop Trading Assets.

---

## 7. Yêu Cầu Visualization & Agent (Specs)

### 7.1 Dashboard Design (Streamlit)
**Page**: `pages/sector_dashboard.py`

#### A. Sector Historical Range (The "Candlestick" Chart)
Biểu đồ này trả lời câu hỏi: *"Ngành này đang đắt hay rẻ so với lịch sử của chính nó?"*
*   **X-Axis**: Metric Name (PE, PB, PS) hoặc Sector Name.
*   **Display**:
    *   **Candle Body**: P25 - P75 (Vùng định giá phổ biến lịch sử).
    *   **Wicks**: P5 - P95 (Vùng cực đại/cực tiểu lịch sử).
    *   **Dot/Line**: Giá trị hiện tại (Current Value).
    *   **Color**: Xanh (Rẻ - Dưới Median), Đỏ (Đắt - Trên Median).

#### B. Cross-Sectional Distribution
Biểu đồ này trả lời câu hỏi: *"Sự phân hóa trong ngành hiện tại ra sao?"*
*   **Data Source**: `processing/valuation/pe/*.parquet` (Snapshot).
*   **Display**: Boxplot/Dotplot of constituents.

---

## 8. MCP Agent Integration & Examples (Final Layer)

Agent (thông qua MCP) sẽ là lớp cuối cùng, tổng hợp dữ liệu từ tất cả các nguồn để trả lời câu hỏi phức tạp của người dùng.

### 8.1 Data Access Architecture
Agent cần khả năng "Read All Data" từ thư mục `DATA/processed/`:
1.  **Sector Data**: Tổng hợp vĩ mô ngành (`sector_*.parquet`).
2.  **Fundamental Data**: Chi tiết báo cáo tài chính từng mã (`fundamental/*.parquet`).
3.  **Valuation Data**: Định giá lịch sử từng mã và ngành (`valuation/*.parquet`).

### 8.2 Supported Analysis Types & Prompt Examples

Dưới đây là các ví dụ cụ thể về Capabilities mà Agent cần hỗ trợ:

#### A. Phân Tích Cơ Bản (FA - Financial Analysis)
*   **Goal**: Hiểu sức khỏe tài chính và xu hướng tăng trưởng.
*   **Prompt Example**:
    > *"Hãy phân tích biên lợi nhuận (Net Margin) của ngành Thép trong 3 năm qua. Có sự cải thiện nào không? So sánh HPG với trung bình ngành."*
*   **Agent Logic**:
    1.  Query `get_sector_metrics(sector="Steel", metric="net_margin", period="3y")`.
    2.  Query `get_financial_trend(tickers=["HPG"], metric="net_margin")`.
    3.  Compare and Summarize.

#### B. Phân Tích Động Lượng & Kỹ Thuật (TA - Technical/Momentum)
*   **Goal**: Đọc mẫu hình nến và động lượng dòng tiền (dựa trên Price/Volume data).
*   **Prompt Example**:
    > *"Ngành Chứng khoán hiện tại đang ở trạng thái tích lũy hay bùng nổ? Dựa trên Volume tuần này so với trung bình 20 tuần, dòng tiền có vào không?"*
*   **Agent Logic**:
    1.  Query `get_sector_ohlcv(sector="Financial Services")`.
    2.  Analyze Price Action (Trend) & Volume Anomaly (Volume > Avg).
    3.  Return assessment (e.g., "Bullish Momentum with high volume").

#### C. Định Giá (Valuation - Relative & Historical)
*   **Goal**: Xác định Đắt/Rẻ (Relative Value).
*   **Prompt Example 1 (Historical)**:
    > *"Ngành Ngân hàng hiện tại PE là 10.5. Mức này là đắt hay rẻ so với lịch sử 5 năm qua? Nó nằm ở percentile bao nhiêu?"*
    *   *Result*: "PE 10.5 tương đương Percentile 30% (Rẻ). Vùng trung bình lịch sử là 12.0 - 14.0."
*   **Prompt Example 2 (Cross-Sector)**:
    > *"Trong các ngành sản xuất, ngành nào đang có định giá P/B thấp nhất hiện tại?"*
    *   *Result*: Scan all manufacturing sectors -> Sort by PB -> "Ngành Hóa chất đang có PB thấp nhất (1.1x)."

### 8.3 Recommended Tools Implementation
1.  `get_sector_summary(sector, period)`: General health check.
2.  `compare_ticker_vs_sector(ticker, metric)`: Benchmarking.
3.  `scan_valuation(metric, condition)`: Screener.
4.  `detect_sector_momentum()`: TA Logic scan.
