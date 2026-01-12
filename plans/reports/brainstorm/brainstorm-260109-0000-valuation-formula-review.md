# Brainstorm Report: Valuation Formula Review

**Date:** 2026-01-09
**Topic:** PE/PB Forward và PE Trailing Formulas
**Status:** ✅ Verified

---

## 1. Summary

Đã kiểm tra và xác nhận công thức tính PE/PB FWD 2025/2026 và PE Trailing trong codebase. Các công thức đều **ĐÚNG** và tuân theo logic tài chính chuẩn.

---

## 2. PE Forward 2025 & 2026

### Nguồn Code
**File:** `PROCESSORS/forecast/bsc/bsc_forecast_processor.py:521-523`

### Công thức

```
PE FWD 2025 = Market Cap (current) / NPATMI Forecast 2025
PE FWD 2026 = Market Cap (current) / NPATMI Forecast 2026
```

### Code Implementation

```python
# Individual Stock Level (line 522-523)
df['pe_fwd_2025'] = df['market_cap'] / df['npatmi_2025f']
df['pe_fwd_2026'] = df['market_cap'] / df['npatmi_2026f']

# Sector Aggregate Level (line 626-627)
sector_agg['pe_fwd_2025'] = sector_agg['total_market_cap'] / sector_agg['total_npatmi_2025f']
sector_agg['pe_fwd_2026'] = sector_agg['total_market_cap'] / sector_agg['total_npatmi_2026f']
```

### Data Sources
- `market_cap`: Từ `DATA/raw/ohlcv/OHLCV_mktcap.parquet` (latest date, đơn vị: tỷ VND)
- `npatmi_2025f`, `npatmi_2026f`: Từ BSC Forecast Excel (đơn vị: tỷ VND)

### Giải thích
- **PE Forward** dùng lợi nhuận **dự báo trong tương lai** chia cho **vốn hóa hiện tại**
- Sector PE FWD tính theo phương pháp **weighted aggregation**: Sum(MC) / Sum(NPATMI)
- Đây là cách tính **đúng** theo chuẩn ngành tài chính

---

## 3. PB Forward 2025 & 2026 (UPDATED 2026-01-09)

### Nguồn Code
**File:** `PROCESSORS/forecast/bsc/bsc_forecast_processor.py:608-616`

### Công thức (Corrected)

```
Parent Equity 2024 = Total Equity 2024 (Q4/2024) - Minority Interest
                   = Total Equity - Lợi ích cổ đông thiểu số

Equity FWD 2025 = Parent Equity 2024 + NPATMI Forecast 2025
Equity FWD 2026 = Equity FWD 2025 + NPATMI Forecast 2026

PB FWD 2025 = Market Cap (current) / Equity FWD 2025
PB FWD 2026 = Market Cap (current) / Equity FWD 2026
```

### Minority Interest Codes by Entity Type

| Entity | Metric Code | Vietnamese Name |
|--------|-------------|-----------------|
| Company | CBS_429 | Lợi ích cổ đông không kiểm soát |
| Bank | BBS_700 | Lợi ích của cổ đông thiểu số |
| Security | SBS_418 | Lợi ích cổ đông không kiểm soát |
| Insurance | IBS_4214 | Lợi ích cổ đông không kiểm soát |

### Code Implementation

```python
# Calculate Parent Equity (excluding minority interest)
df['parent_equity_2024'] = df['total_equity'] - df['minority_interest']

# Calculate forward equity (retained earnings growth model)
df['equity_2025f'] = df['parent_equity_2024'] + df['npatmi_2025f']
df['equity_2026f'] = df['equity_2025f'] + df['npatmi_2026f']

# Calculate PB Forward
df['pb_fwd_2025'] = df['market_cap'] / df['equity_2025f']
df['pb_fwd_2026'] = df['market_cap'] / df['equity_2026f']
```

### Sector Level (line 708-716)

```python
# Use Parent Equity for sector aggregate
sector_agg['total_equity_2025f'] = sector_agg['total_parent_equity_2024'] + sector_agg['total_npatmi_2025f']
sector_agg['total_equity_2026f'] = sector_agg['total_equity_2025f'] + sector_agg['total_npatmi_2026f']

sector_agg['pb_fwd_2025'] = sector_agg['total_market_cap'] / sector_agg['total_equity_2025f']
sector_agg['pb_fwd_2026'] = sector_agg['total_market_cap'] / sector_agg['total_equity_2026f']
```

### Data Sources
- `market_cap`: Từ OHLCV (latest date)
- `total_equity`: Từ fundamental metrics (latest quarter)
- `minority_interest`: Từ raw balance sheet CSV (CBS_429, BBS_700, SBS_418, IBS_4214)
- `npatmi_2025f`, `npatmi_2026f`: Từ BSC Forecast Excel

### Giải thích
- **Parent Equity** = Total Equity - Minority Interest (Lợi ích cổ đông thiểu số)
- **NPATMI** = Net Profit After Tax to **Mother** company (lợi nhuận công ty mẹ)
- PB FWD tính trên **vốn chủ sở hữu của công ty mẹ**, loại trừ phần của cổ đông thiểu số
- 100% NPATMI được giữ lại (retained earnings, không chia cổ tức)

### Lý do cập nhật (2026-01-09)
- Công thức cũ dùng `total_equity` bao gồm cả minority interest → PB bị **understated**
- NPATMI là lợi nhuận của cổ đông mẹ, nên phải dùng equity của cổ đông mẹ để tính PB
- Công thức mới **consistent** với logic tài chính chuẩn

---

## 4. PE Trailing (TTM)

### Nguồn Code

**Individual Stock:** `PROCESSORS/valuation/calculators/historical_pe_calculator.py:301-309`

**Index/Sector Level:** `PROCESSORS/valuation/calculators/vnindex_valuation_calculator.py:321-325`

### Công thức

```
# Individual Stock Level
EPS = TTM Earnings / Shares Outstanding
PE Ratio = Close Price / EPS
(Chỉ tính khi EPS > 0)

# Index/Sector Aggregate Level
PE TTM = Sum(Market Cap) / Sum(TTM Earnings)
```

### Code Implementation

```python
# Individual Stock (historical_pe_calculator.py)
merged_data['eps'] = merged_data['ttm_earnings_raw'] / merged_data['shares_outstanding']
merged_data['pe_ratio'] = np.where(
    (merged_data['eps'] > 0) & (merged_data['close'] > 0),
    merged_data['close'] / merged_data['eps'],
    np.nan
)

# Index Aggregate (vnindex_valuation_calculator.py)
pe_agg = pe_valid.groupby('date').agg(
    total_mc_pe=('market_cap', 'sum'),
    total_earnings=('earnings_ttm', 'sum')
)
pe_agg['pe_ttm'] = pe_agg['total_mc_pe'] / pe_agg['total_earnings']
```

### Data Sources
- `close`: Giá đóng cửa từ OHLCV
- `ttm_earnings_raw`: TTM earnings từ fundamental data (4 quý gần nhất)
- `shares_outstanding`: Số cổ phiếu lưu hành từ OHLCV/fundamental

### Giải thích
- **TTM (Trailing Twelve Months)** = Tổng lợi nhuận 4 quý gần nhất
- PE TTM sử dụng **lợi nhuận thực tế trong quá khứ**, không phải dự báo
- Negative earnings → PE = NaN (không tính)
- Index PE dùng **weighted aggregation** như FWD PE

---

## 4.5 PB Trailing (TTM) - UPDATED 2026-01-09

### Nguồn Code

**File:** `PROCESSORS/valuation/calculators/historical_pb_calculator.py:181-232, 312-322`

### Công thức (Corrected)

```
# Parent Equity calculation
Parent Equity = Total Equity (TTM) - Minority Interest
              = Total Equity - Lợi ích cổ đông thiểu số

# Individual Stock Level
BPS = Parent Equity / Shares Outstanding
PB Ratio = Close Price / BPS
(Chỉ tính khi BPS > 0)
```

### Minority Interest Codes by Entity Type

| Entity | Metric Code | Vietnamese Name |
|--------|-------------|-----------------|
| Company | CBS_429 | Lợi ích cổ đông không kiểm soát |
| Bank | BBS_700 | Lợi ích của cổ đông thiểu số |
| Security | SBS_418 | Lợi ích cổ đông không kiểm soát |
| Insurance | IBS_4214 | Lợi ích cổ đông không kiểm soát |

### Code Implementation

```python
# Minority interest codes (line 181-188)
minority_interest_codes = {
    'COMPANY': 'CBS_429',
    'BANK': 'BBS_700',
    'SECURITY': 'SBS_418',
    'INSURANCE': 'IBS_4214'
}

# Calculate Parent Equity (line 231-232)
equity_df['parent_equity_raw'] = equity_df['total_equity_raw'] - equity_df['minority_interest']

# Calculate BPS using Parent Equity (line 313-314)
merged_data['bps'] = merged_data['parent_equity_raw'] / merged_data['shares_outstanding']

# Calculate PB Ratio (line 318-322)
merged_data['pb_ratio'] = np.where(
    (merged_data['bps'] > 0) & (merged_data['close'] > 0),
    merged_data['close'] / merged_data['bps'],
    np.nan
)
```

### Giải thích
- **Parent Equity** = Total Equity - Minority Interest
- PB TTM tính trên **vốn chủ sở hữu của công ty mẹ**, loại trừ phần của cổ đông thiểu số
- Đây là cách tính **consistent** với PB FWD (cũng dùng parent equity)

### Lý do cập nhật (2026-01-09)
- Công thức cũ dùng `total_equity` bao gồm cả minority interest → PB bị **understated**
- PB TTM và PB FWD cần **consistent** trong việc sử dụng parent equity
- Công thức mới đảm bảo so sánh PB TTM vs PB FWD là meaningful

---

## 5. So Sánh PE TTM vs PE FWD

| Metric | PE TTM | PE FWD 2025 | PE FWD 2026 |
|--------|--------|-------------|-------------|
| **Earnings Used** | TTM (4Q gần nhất) | NPATMI Forecast 2025 | NPATMI Forecast 2026 |
| **Market Cap** | Current | Current | Current |
| **Calculation** | MC / TTM Earnings | MC / NPATMI 2025F | MC / NPATMI 2026F |
| **Meaning** | Backward-looking | Forward-looking | Forward-looking |
| **Risk** | Actual data | Forecast uncertainty | Higher uncertainty |

### Expected Relationship
- Nếu EPS growth dương: `PE FWD < PE TTM` (re-rating opportunity)
- Nếu EPS growth âm: `PE FWD > PE TTM` (de-rating risk)

---

## 6. Data Flow Summary

```
BSC Forecast Excel
    │
    ├─► npatmi_2025f, npatmi_2026f (forecast earnings)
    │
OHLCV_mktcap.parquet
    │
    ├─► market_cap, close (current prices)
    │
Fundamental Metrics
    │
    ├─► total_equity (TTM book value)
    ├─► minority_interest (CBS_429/BBS_700/SBS_418/IBS_4214)
    ├─► ttm_earnings (actual TTM profits)
    │
    ▼
BSC Forecast Processor
    │
    ├─► parent_equity = total_equity - minority_interest
    ├─► PE FWD 2025 = market_cap / npatmi_2025f
    ├─► PE FWD 2026 = market_cap / npatmi_2026f
    ├─► PB FWD 2025 = market_cap / (parent_equity + npatmi_2025f)
    └─► PB FWD 2026 = market_cap / (equity_2025f + npatmi_2026f)

Historical PB Calculator
    │
    ├─► parent_equity = total_equity - minority_interest
    ├─► BPS = parent_equity / shares_outstanding
    └─► PB TTM = close_price / BPS
```

---

## 7. Conclusion

| Formula | Status | Notes |
|---------|--------|-------|
| PE FWD 2025 | ✅ **Correct** | MC / NPATMI 2025F |
| PE FWD 2026 | ✅ **Correct** | MC / NPATMI 2026F |
| PB FWD 2025 | ✅ **Corrected** | MC / (Parent Equity + NPATMI 2025F) |
| PB FWD 2026 | ✅ **Corrected** | MC / (Equity 2025F + NPATMI 2026F) |
| PE TTM | ✅ **Correct** | Price / EPS (or MC / TTM Earnings) |
| PB TTM | ✅ **Corrected** | Price / BPS (BPS = Parent Equity / Shares) |

**Parent Equity** = Total Equity - Minority Interest (Lợi ích cổ đông thiểu số)

Tất cả công thức PB đã được cập nhật để sử dụng **Parent Equity** (vốn chủ sở hữu công ty mẹ) thay vì Total Equity, đảm bảo **consistent** với NPATMI (lợi nhuận công ty mẹ).

---

## 8. Unresolved Questions

1. **Dividend Payout Adjustment:** Nên thêm payout ratio vào PB FWD calculation không? (Low priority)
2. **Negative Earnings Handling:** Hiện tại PE = NaN khi earnings < 0. Có nên hiển thị "N/A" trên UI?

---

## Files Referenced

| File | Purpose |
|------|---------|
| `PROCESSORS/forecast/bsc/bsc_forecast_processor.py` | PE/PB FWD calculation |
| `PROCESSORS/valuation/calculators/historical_pe_calculator.py` | Individual PE TTM |
| `PROCESSORS/valuation/calculators/historical_pb_calculator.py` | Individual PB TTM (updated 2026-01-09) |
| `PROCESSORS/valuation/calculators/vnindex_valuation_calculator.py` | Index/Sector PE TTM |
| `PROCESSORS/valuation/formulas/valuation_formulas.py` | Pure formula functions |
| `config/metadata/metric_registry.json` | Minority interest metric codes |
| `docs/logic/forecast.md` | Business logic documentation |
| `docs/logic/sector.md` | Sector valuation logic |
