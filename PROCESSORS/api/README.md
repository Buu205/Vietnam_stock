# API Module - Centralized API Management

## Tổng Quan

Module này quản lý tập trung tất cả external API calls cho Vietnam Dashboard, bao gồm:
- **Retry logic** với exponential backoff
- **Error handling** chuẩn hóa
- **Health monitoring** và metrics
- **Secure credential management**

## Cấu Trúc

```
PROCESSORS/api/
├── __init__.py                 # Main exports
├── README.md                   # Tài liệu này
├── unified_fetcher.py          # Unified data fetcher
│
├── core/                       # Infrastructure
│   ├── base_client.py         # BaseAPIClient class
│   ├── exceptions.py          # Custom exceptions
│   └── retry_handler.py       # Retry logic
│
├── clients/                    # API Clients
│   ├── wichart_client.py      # WiChart API
│   ├── simplize_client.py     # Simplize API
│   ├── fireant_client.py      # Fireant API
│   └── vnstock_client.py      # vnstock_data wrapper
│
├── monitoring/                 # Health & Metrics
│   ├── health_checker.py      # Health checking
│   └── metrics_logger.py      # Request metrics
│
└── config/                     # Configuration
    └── api_config.py          # Config loader

config/api/                     # Config files
├── api_endpoints.json         # Endpoint definitions
├── api_credentials.json       # Tokens (GITIGNORED)
└── api_credentials.example.json
```

---

## Quick Start

### 1. Sử Dụng Unified Fetcher (Khuyến nghị)

```python
from PROCESSORS.api import UnifiedDataFetcher

# Khởi tạo fetcher
fetcher = UnifiedDataFetcher()

# Fetch tất cả data (commodity + macro)
df_all = fetcher.fetch_all(start_date="2020-01-01")

# Chỉ fetch commodity
df_commodity = fetcher.fetch_commodities()

# Chỉ fetch macro
df_macro = fetcher.fetch_macro()
```

### 2. Sử Dụng Client Riêng

```python
from PROCESSORS.api.clients import WiChartClient, SimplizeClient, VNStockClient

# WiChart - Tỷ giá, lãi suất
wichart = WiChartClient()
fx_rates = wichart.get_exchange_rates()
interest_rates = wichart.get_interest_rates()

# Simplize - Trái phiếu, cao su, sữa
simplize = SimplizeClient()
bonds = simplize.get_gov_bond_5y()
rubber = simplize.get_rubber()

# VNStock - Commodity từ vnstock_data
vnstock = VNStockClient()
gold = vnstock.get_commodity("gold_vn")
```

### 3. Health Check

```python
from PROCESSORS.api.monitoring import HealthChecker

checker = HealthChecker()
checker.check_all()
checker.print_report()
```

---

## CLI Commands

```bash
# Kiểm tra health tất cả APIs
python -m PROCESSORS.api.monitoring.health_checker

# Output JSON
python -m PROCESSORS.api.monitoring.health_checker --json

# Fetch data và save
python -m PROCESSORS.api.unified_fetcher --type all --output output.parquet

# Chỉ fetch macro
python -m PROCESSORS.api.unified_fetcher --type macro
```

---

## Cấu Hình Credentials

### File: `config/api/api_credentials.json`

```json
{
  "simplize": {
    "api_token": "eyJhbGciOiJIUzUxMiJ9...",
    "jsessionid": "YOUR_JSESSIONID"
  },
  "fireant": {
    "bearer_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
  }
}
```

### Environment Variables (Override)

```bash
export SIMPLIZE_API_TOKEN="your_token"
export SIMPLIZE_JSESSIONID="your_session"
export FIREANT_BEARER_TOKEN="your_token"
```

### Lấy Token Mới

| API | Cách lấy token |
|-----|----------------|
| **Simplize** | Đăng nhập https://simplize.vn → F12 → Network → Copy token từ header |
| **Fireant** | Đăng nhập https://fireant.vn → F12 → Network → Copy Bearer token |
| **WiChart** | Không cần token (public API) |
| **VNStock** | Không cần token (sử dụng library) |

---

## API Clients Chi Tiết

### WiChartClient

```python
from PROCESSORS.api.clients import WiChartClient

client = WiChartClient()

# Tỷ giá USD/VND
df = client.get_exchange_rates()
# Columns: date, symbol, value, unit, source

# Lãi suất liên ngân hàng
df = client.get_interest_rates()

# Lãi suất huy động
df = client.get_deposit_rates()

# Tất cả macro data
df = client.get_all_macro()

# Commodity
df = client.get_steel_coated()  # Tôn lạnh màu HSG
df = client.get_pvc()           # Nhựa PVC
```

**Endpoints:**
- `https://api.wichart.vn/vietnambiz/vi-mo?name=dhtg` - Tỷ giá
- `https://api.wichart.vn/vietnambiz/vi-mo?name=lslnh` - Lãi suất liên NH
- `https://api.wichart.vn/vietnambiz/vi-mo?name=lshd` - Lãi suất huy động

### SimplizeClient

```python
from PROCESSORS.api.clients import SimplizeClient

client = SimplizeClient()

# Trái phiếu chính phủ
df = client.get_gov_bond_5y()   # TPCP 5 năm
df = client.get_gov_bond_10y()  # TPCP 10 năm (nếu có)

# Commodity
df = client.get_rubber()        # Cao su TOCOM
df = client.get_wmp_milk()      # Sữa bột WMP
```

**Endpoints:**
- `/api/historical/prices/ohlcv?ticker=TVC:VN05Y` - Gov Bond 5Y
- `/api/historical/prices/chart?ticker=TOCOM:TRB1!` - Rubber
- `/api/historical/prices/chart?ticker=NZX:WMP1!` - WMP Milk

### VNStockClient

```python
from PROCESSORS.api.clients import VNStockClient

client = VNStockClient()

# Commodity đơn lẻ
df = client.get_commodity("gold_vn")
df = client.get_commodity("oil_crude")

# Tất cả commodity
df = client.get_all_commodities(start_date="2020-01-01")

# Danh sách commodity có sẵn
symbols = client.list_available_commodities()
# ['gold_vn', 'gold_global', 'oil_crude', 'oil_brent', 'gas_natural',
#  'coke', 'steel_d10', 'steel_hrc', 'iron_ore', 'fertilizer_ure',
#  'soybean', 'corn', 'sugar', 'pork_north_vn', 'pork_china']
```

### FireantClient

```python
from PROCESSORS.api.clients import FireantClient

client = FireantClient()

# Share outstanding
df = client.get_share_outstanding("VNM")

# Financial statements
df = client.get_income_statement("VNM", period="quarterly")
df = client.get_balance_sheet("VNM")
df = client.get_cash_flow("VNM")

# Company profile
profile = client.get_company_profile("VNM")
```

---

## Thêm API Mới

### 1. Tạo Client File

```python
# PROCESSORS/api/clients/new_client.py

from PROCESSORS.api.core.base_client import BaseAPIClient, APIResponse
from PROCESSORS.api.config.api_config import get_api_config

class NewAPIClient(BaseAPIClient):
    def __init__(self, config=None):
        self._config = config or get_api_config()
        endpoint_config = self._config.get_endpoint_config("new_api")
        credentials = self._config.get_credentials("new_api")

        self._api_key = credentials.get("api_key") if credentials else None

        super().__init__(
            name="new_api",
            base_url=endpoint_config.base_url if endpoint_config else "https://api.example.com",
            timeout=30,
            max_retries=3,
        )

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def validate_credentials(self):
        return self._api_key is not None

    def get_data(self):
        response = self.get("/endpoint")
        if response.success:
            return response.data
        return None
```

### 2. Thêm Config

**config/api/api_endpoints.json:**
```json
{
  "new_api": {
    "base_url": "https://api.example.com",
    "timeout_seconds": 30,
    "max_retries": 3,
    "rate_limit_per_minute": 60,
    "requires_auth": true
  }
}
```

**config/api/api_credentials.json:**
```json
{
  "new_api": {
    "api_key": "your_api_key"
  }
}
```

### 3. Export trong __init__.py

```python
# PROCESSORS/api/clients/__init__.py
from PROCESSORS.api.clients.new_client import NewAPIClient

__all__ = [..., "NewAPIClient"]
```

---

## Sửa Request / Thêm Endpoint

### Thêm method mới vào client có sẵn

```python
# Trong wichart_client.py

def get_new_data(self) -> pd.DataFrame:
    """Fetch new data type."""
    endpoint = "/vietnambiz/vi-mo?name=new_param"

    response = self.get(endpoint)

    if not response.success:
        return pd.DataFrame()

    # Parse response
    data = response.data.get("chart", {}).get("series", [])
    # ... xử lý data

    return df
```

### Thay đổi request parameters

```python
# Thêm query params
response = self.get("/endpoint", params={
    "start_date": "2020-01-01",
    "limit": 1000,
})

# POST request với data
response = self.post("/endpoint", data={
    "field": "value"
})
```

---

## Error Handling

```python
from PROCESSORS.api import (
    APIError,
    APITimeoutError,
    APIConnectionError,
    APIAuthenticationError,
    APIRateLimitError,
)

try:
    data = client.get_data()
except APITimeoutError:
    print("Request timed out")
except APIAuthenticationError:
    print("Invalid credentials")
except APIRateLimitError:
    print("Rate limit exceeded")
except APIError as e:
    print(f"API error: {e}")
```

---

## Metrics & Monitoring

### Xem metrics

```python
from PROCESSORS.api.monitoring import MetricsLogger, get_metrics_registry

# Metrics cho 1 API
logger = MetricsLogger("simplize")
logger.log_request("/api/data", 200, 150.5)
print(logger.get_summary())

# Tất cả metrics
registry = get_metrics_registry()
print(registry.get_health_overview())
```

### Health check output

```
======================================================================
API HEALTH REPORT - 2025-12-19 12:40:20
======================================================================
API          | Status | Latency  | Last Success   | Data Fresh
----------------------------------------------------------------------
wichart      | OK     | 99ms     | Just now       | Yes
simplize     | OK     | 696ms    | Just now       | Yes
fireant      | OK     | 173ms    | Just now       | Yes
vnstock      | OK     | 3319ms   | Just now       | Yes
======================================================================
```

---

## Migration từ macro_commodity_fetcher.py

File cũ `PROCESSORS/technical/macro_commodity/macro_commodity_fetcher.py` vẫn hoạt động nhưng:
- ❌ Hardcoded tokens trong source code
- ❌ Không có retry logic
- ❌ Không có health monitoring

### Cách migrate:

```python
# CŨ (không khuyến khích)
from PROCESSORS.technical.macro_commodity.macro_commodity_fetcher import MacroCommodityFetcher
fetcher = MacroCommodityFetcher()
df = fetcher.fetch_all()

# MỚI (khuyến khích)
from PROCESSORS.api import UnifiedDataFetcher
fetcher = UnifiedDataFetcher()
df = fetcher.fetch_all()
```

### Backward compatibility wrapper

```python
# Nếu cần giữ interface cũ
from PROCESSORS.api import UnifiedDataFetcher

class MacroCommodityFetcher:
    """Backward compatible wrapper."""

    def __init__(self):
        self._fetcher = UnifiedDataFetcher()

    def fetch_all(self, start_date="2015-01-01"):
        return self._fetcher.fetch_all(start_date)

    def fetch_commodities(self, start_date="2015-01-01"):
        return self._fetcher.fetch_commodities(start_date)

    def fetch_all_macro(self):
        return self._fetcher.fetch_macro()
```

---

## Troubleshooting

### Token hết hạn

```
[simplize] Health check failed (token may be expired)
```

**Fix:** Lấy token mới từ browser và update `config/api/api_credentials.json`

### Rate limit

```
APIRateLimitError: Rate limit exceeded
```

**Fix:** Giảm `rate_limit_per_minute` trong config hoặc thêm delay giữa requests

### Connection timeout

```
APITimeoutError: Request timed out
```

**Fix:** Tăng `timeout_seconds` trong config hoặc kiểm tra network

---

## Data Sources Summary

| Source | Data Types | Auth Required |
|--------|------------|---------------|
| **WiChart** | Tỷ giá, lãi suất, tôn, PVC | ❌ |
| **Simplize** | TPCP, cao su, sữa WMP | ✅ |
| **Fireant** | Share outstanding, financials | ✅ |
| **VNStock** | Vàng, dầu, thép, nông sản | ❌ |

---

## ✅ API Health Report (2025-12-19) - UPDATED

### ✅ TẤT CẢ API ĐANG HOẠT ĐỘNG TỐT

| API | Data Types | Endpoint | Status |
|-----|------------|----------|--------|
| **WiChart** | Tỷ giá USD | `vi-mo?name=dhtg` | ✅ OK |
| **WiChart** | Lãi suất liên NH | `vi-mo?name=lslnh` | ✅ OK |
| **WiChart** | Lãi suất huy động | `vi-mo?name=lshd` | ✅ OK |
| **WiChart** | Thép tôn HSG | `vi-mo?key=hang_hoa&name=ton_lanh_mau_hoa_sen_045mm` | ✅ OK |
| **WiChart** | Nhựa PVC | `vi-mo?key=hang_hoa&name=nhua_pvc_trung_quoc` | ✅ OK |
| **WiChart** | Heo hơi VN | `vi-mo?key=hang_hoa&name=heo_hoi` | ✅ OK |
| **Simplize** | Gov Bond 5Y, Cao su, Sữa WMP | `/api/historical/prices/*` | ✅ OK |
| **VNStock** | Gold, Oil, Steel, Corn, Soybean, etc. | vnstock_data library | ✅ OK |
| **Fireant** | Share outstanding, Financials | `/symbols/{ticker}/*` | ✅ OK |

**Base URL:** `https://api.wichart.vn/vietnambiz/`

---

## Version History

- **v1.0.2** (2025-12-19): All APIs restored
  - WiChart API hoạt động trở lại
  - Thêm endpoint giá heo hơi VN

- **v1.0.1** (2025-12-19): API Health Report
  - Phát hiện WiChart API DEAD (data dừng 2023-12-19)
  - Cần tìm nguồn thay thế cho macro data

- **v1.0.0** (2025-12-19): Initial release
  - 4 API clients (WiChart, Simplize, Fireant, VNStock)
  - Health monitoring
  - Unified fetcher
  - Secure credential management

---

## API Examples (Raw Request Reference)

### 1. Tỷ giá USD (WiChart)

```python
import requests

url = "https://api.wichart.vn/vietnambiz/vi-mo?name=dhtg"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://data.vietnambiz.vn',
    'Referer': 'https://data.vietnambiz.vn/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
print(response.json())
```

### 2. Lãi suất liên ngân hàng (WiChart)

```python
import requests

url = "https://api.wichart.vn/vietnambiz/vi-mo?name=lslnh"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://data.vietnambiz.vn',
    'Referer': 'https://data.vietnambiz.vn/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
print(response.json())
```

### 3. Lãi suất huy động (WiChart)

```python
import requests

url = "https://api.wichart.vn/vietnambiz/vi-mo?name=lshd"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://data.vietnambiz.vn',
    'Referer': 'https://data.vietnambiz.vn/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
print(response.json())
```

### 4. Thép tôn HSG (WiChart)

```python
import requests

url = "https://api.wichart.vn/vietnambiz/vi-mo?key=hang_hoa&name=ton_lanh_mau_hoa_sen_045mm"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://data.vietnambiz.vn',
    'Referer': 'https://data.vietnambiz.vn/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
print(response.json())
```

### 5. Nhựa PVC Trung Quốc (WiChart)

```python
import requests

url = "https://api.wichart.vn/vietnambiz/vi-mo?key=hang_hoa&name=nhua_pvc_trung_quoc"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://data.vietnambiz.vn',
    'Referer': 'https://data.vietnambiz.vn/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
print(response.json())
```

### 6. Giá heo hơi Việt Nam (WiChart)

```python
import requests

url = "https://api.wichart.vn/vietnambiz/vi-mo?key=hang_hoa&name=heo_hoi"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://data.vietnambiz.vn',
    'Referer': 'https://data.vietnambiz.vn/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
print(response.json())
```

### 7. Giá sữa WMP (Simplize)

```python
import requests

url = "https://api2.simplize.vn/api/historical/prices/chart?ticker=NZX%3AWMP1!&period=1y"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Authorization': 'Bearer YOUR_TOKEN_HERE',  # Lấy từ config/api/api_credentials.json
    'Origin': 'https://simplize.vn',
    'Referer': 'https://simplize.vn/',
    'Cookie': 'JSESSIONID=YOUR_SESSION_ID'
}

response = requests.get(url, headers=headers)
print(response.json())
```

