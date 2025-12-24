# Vietcap IQ API - Hướng dẫn sử dụng

## Tổng quan

API này fetch dữ liệu **Coverage Universe** từ Vietcap IQ - bao gồm:
- Target price, rating (BUY/O-PF/U-PF/M-PF)
- PE, PB, ROE dự báo 2025F, 2026F
- Lợi nhuận dự báo, analyst phụ trách

**Output:** `DATA/processed/forecast/VCI/vci_coverage_universe.parquet`

---

## Quick Start

```bash
# Fetch data mới
cd /Users/buuphan/Dev/Vietnam_dashboard
python3 PROCESSORS/api/vietcap/fetch_vci_forecast.py
```

---

## Lịch update khuyến nghị

| Tần suất | Khi nào | Lý do |
|----------|---------|-------|
| **Tuần 1 lần** | Thứ 2 sáng | Vietcap thường update target price cuối tuần |
| **2 tuần/lần** | Đầu tháng + giữa tháng | Đủ để bắt các thay đổi rating |

---

## Các bước update data

### 1. Check token còn hạn không

```bash
cat PROCESSORS/api/vietcap/vietcap_token.json | grep expires_at
```

Token hết hạn sau **7 ngày**. Nếu cần refresh:

```bash
python3 PROCESSORS/api/vietcap/vietcap_auth.py --refresh
```

### 2. Fetch data mới

```bash
python3 PROCESSORS/api/vietcap/fetch_vci_forecast.py
```

Output:
```
✅ Got 83 tickers
💾 Saved parquet: DATA/processed/forecast/VCI/vci_coverage_universe.parquet
```

### 3. Verify data

```bash
python3 -c "
import pandas as pd
df = pd.read_parquet('DATA/processed/forecast/VCI/vci_coverage_universe.parquet')
print(f'Rows: {len(df)}, Date: {df.fetch_date.iloc[0]}')
print(df[['ticker','rating','targetPrice']].head(10))
"
```

---

## Tự động hóa với Cron (Optional)

### Chạy mỗi thứ 2 lúc 8:00 sáng

```bash
crontab -e
```

Thêm dòng:
```cron
0 8 * * 1 cd /Users/buuphan/Dev/Vietnam_dashboard && python3 PROCESSORS/api/vietcap/fetch_vci_forecast.py >> logs/vci_update.log 2>&1
```

### Chạy 2 tuần/lần (ngày 1 và 15 hàng tháng)

```cron
0 8 1,15 * * cd /Users/buuphan/Dev/Vietnam_dashboard && python3 PROCESSORS/api/vietcap/fetch_vci_forecast.py >> logs/vci_update.log 2>&1
```

---

## Xử lý lỗi

### Token hết hạn (Error 401/100)

```bash
# Refresh token
python3 PROCESSORS/api/vietcap/vietcap_auth.py --refresh
```

### Connection error / Timeout

- Kiểm tra mạng
- Thử lại sau 5 phút
- Vietcap có thể maintenance

### Password sai

Edit `.env`:
```bash
nano .env
# Sửa VIETCAP_PASS=<password_mới>
```

---

## Cấu trúc files

```
PROCESSORS/api/vietcap/
├── vietcap_auth.py          # Auto login (Playwright)
├── vietcap_client.py        # API client
├── vietcap_token.json       # Token cache (7 ngày)
└── fetch_vci_forecast.py    # Main script

DATA/processed/forecast/VCI/
├── vci_coverage_universe.parquet   # Data chính
└── vci_coverage_universe.json      # Backup JSON

.env                         # Credentials (KHÔNG commit!)
```

---

## Data Schema

| Column | Type | Mô tả |
|--------|------|-------|
| ticker | str | Mã CK (VCB, ACB, FPT...) |
| sector | str | Ngành (Banks, Consumer...) |
| rating | str | BUY, O-PF, U-PF, M-PF |
| targetPrice | float | Giá mục tiêu (VND) |
| projectedTsrPercentage | float | TSR dự kiến (%) |
| pe_2025F, pe_2026F | float | PE dự báo |
| pb_2025F, pb_2026F | float | PB dự báo |
| roe_2025F, roe_2026F | float | ROE dự báo |
| npatmi_2025F, npatmi_2026F | float | Lợi nhuận dự báo |
| analyst | str | Analyst phụ trách |
| tpUpdatedTime | str | Ngày update target price |
| fetch_date | str | Ngày fetch data |

---

## Sử dụng trong code

```python
import pandas as pd

# Load data
df = pd.read_parquet("DATA/processed/forecast/VCI/vci_coverage_universe.parquet")

# Filter BUY rating
buy_stocks = df[df['rating'] == 'BUY']

# Top upside
top_upside = df.nlargest(10, 'projectedTsrPercentage')[['ticker', 'targetPrice', 'projectedTsrPercentage']]

# Banks sector
banks = df[df['sector'] == 'Banks']
```

---

## Checklist update hàng tuần

- [ ] Check token expiry
- [ ] Run fetch script
- [ ] Verify row count (~83 tickers)
- [ ] Check fetch_date = today
- [ ] Commit nếu có thay đổi đáng kể
