# BSC Forecast Data Structure

## Overview
Dữ liệu dự báo BSC Research đã xử lý, bao gồm PE/PB forward và các metrics tính toán.

**Last Updated:** 2026-01-04 14:54:39
**Source:** BSC Research Forecast Excel
**Symbols:** 92 mã | **Sectors:** 15 ngành

---

## Files

### 1. bsc_individual.parquet (92 rows)
Individual stock forecast với calculated metrics.

| Column | Type | Description |
|--------|------|-------------|
| symbol | str | Mã cổ phiếu |
| target_price | float | Giá mục tiêu BSC (VND) |
| current_price | float | Giá hiện tại (VND) |
| upside_pct | float | % tăng giá kỳ vọng |
| rating | str | Khuyến nghị (STRONG BUY/BUY/HOLD/SELL/STRONG SELL) |
| rev_2025f | float | Doanh thu forecast 2025 (tỷ VND) |
| rev_2026f | float | Doanh thu forecast 2026 (tỷ VND) |
| npatmi_2025f | float | LNST forecast 2025 (tỷ VND) |
| npatmi_2026f | float | LNST forecast 2026 (tỷ VND) |
| eps_2025f | float | EPS forecast 2025 (VND) |
| eps_2026f | float | EPS forecast 2026 (VND) |
| roe_2025f | float | ROE forecast 2025 (%) |
| roe_2026f | float | ROE forecast 2026 (%) |
| roa_2025f | float | ROA forecast 2025 (%) |
| roa_2026f | float | ROA forecast 2026 (%) |
| rev_growth_yoy_2025 | float | Tăng trưởng DT 2024→2025 (%) |
| rev_growth_yoy_2026 | float | Tăng trưởng DT 2025→2026 (%) |
| npatmi_growth_yoy_2025 | float | Tăng trưởng LN 2024→2025 (%) |
| npatmi_growth_yoy_2026 | float | Tăng trưởng LN 2025→2026 (%) |
| rev_ytd_2025 | float | Doanh thu YTD 2025 (tỷ VND) |
| npatmi_ytd_2025 | float | LNST YTD 2025 (tỷ VND) |
| rev_achievement_pct | float | % hoàn thành DT forecast |
| npatmi_achievement_pct | float | % hoàn thành LN forecast |
| market_cap | float | Vốn hóa hiện tại (tỷ VND) |
| total_equity | float | Vốn chủ sở hữu TTM (tỷ VND) |
| pe_fwd_2025 | float | PE forward 2025 |
| pe_fwd_2026 | float | PE forward 2026 |
| pb_fwd_2025 | float | PB forward 2025 |
| pb_fwd_2026 | float | PB forward 2026 |
| sector | str | Ngành ICB L2 (ticker_details.json) |
| entity_type | str | Loại DN: BANK/COMPANY/SECURITY/INSURANCE |
| updated_at | datetime | Thời gian cập nhật |

### 2. bsc_sector_valuation.parquet (15 rows)
Sector aggregation với PE/PB forward 2025-2026.

| Column | Type | Description |
|--------|------|-------------|
| sector | str | Ngành ICB L2 |
| symbol_count | int | Số mã trong ngành |
| total_market_cap | float | Tổng vốn hóa (tỷ VND) |
| total_npatmi_2025f | float | Tổng LNST forecast 2025 (tỷ VND) |
| total_npatmi_2026f | float | Tổng LNST forecast 2026 (tỷ VND) |
| total_equity_2025f | float | Tổng VCSH forecast 2025 (tỷ VND) |
| total_equity_2026f | float | Tổng VCSH forecast 2026 (tỷ VND) |
| pe_fwd_2025 | float | Sector PE forward 2025 |
| pe_fwd_2026 | float | Sector PE forward 2026 |
| pb_fwd_2025 | float | Sector PB forward 2025 |
| pb_fwd_2026 | float | Sector PB forward 2026 |
| avg_upside_pct | float | Upside trung bình ngành (%) |
| avg_roe_2025f | float | ROE trung bình 2025 (%) |
| avg_roe_2026f | float | ROE trung bình 2026 (%) |
| updated_at | datetime | Thời gian cập nhật |

### 3. bsc_combined.parquet (92 rows)
Individual + sector metrics merged.

Bao gồm tất cả columns từ bsc_individual.parquet + thêm:
| Column | Type | Description |
|--------|------|-------------|
| sector_pe_fwd_2025 | float | PE FWD 2025 của ngành |
| sector_pe_fwd_2026 | float | PE FWD 2026 của ngành |
| sector_pb_fwd_2025 | float | PB FWD 2025 của ngành |
| sector_pb_fwd_2026 | float | PB FWD 2026 của ngành |
| pe_premium_2025 | float | PE stock / PE sector - 1 (premium/discount) |
| pe_premium_2026 | float | PE stock / PE sector - 1 |

---

## Formulas

### PE Forward
```
PE FWD 2025 = market_cap / npatmi_2025f
PE FWD 2026 = market_cap / npatmi_2026f
```

### PB Forward
```
equity_2025f = total_equity_ttm + npatmi_2025f
equity_2026f = equity_2025f + npatmi_2026f

PB FWD 2025 = market_cap / equity_2025f
PB FWD 2026 = market_cap / equity_2026f
```

### Upside & Rating
```
upside_pct = (target_price / current_price) - 1

Rating Logic:
- STRONG BUY:  upside > 25%
- BUY:         upside > 10% & <= 25%
- HOLD:        upside >= -10% & <= 10%
- SELL:        upside > -20% & < -10%
- STRONG SELL: upside <= -20%
```

### YTD Achievement
```
rev_achievement_pct = rev_ytd_2025 / rev_2025f
npatmi_achievement_pct = npatmi_ytd_2025 / npatmi_2025f
```

### Growth YoY
```
rev_growth_yoy_2025 = (rev_2025f / rev_2024_actual) - 1
npatmi_growth_yoy_2025 = (npatmi_2025f / npatmi_2024_actual) - 1
```

---

## Data Refresh

### Daily Auto-Update (via daily pipeline)
Cập nhật market_cap, current_price, PE/PB FWD từ OHLCV data.

```bash
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

### Manual Excel Re-read
Khi BSC cập nhật forecast mới trong Excel:

```bash
python3 PROCESSORS/forecast/update_bsc_excel.py
```

---

## Usage Example

```python
import pandas as pd

# Load individual stocks
df = pd.read_parquet("DATA/processed/forecast/bsc/bsc_individual.parquet")

# Filter by rating
strong_buys = df[df['rating'] == 'STRONG BUY']

# Load sector valuation
sectors = pd.read_parquet("DATA/processed/forecast/bsc/bsc_sector_valuation.parquet")

# Compare PE FWD by sector
print(sectors[['sector', 'pe_fwd_2025', 'pe_fwd_2026']].sort_values('pe_fwd_2025'))
```

