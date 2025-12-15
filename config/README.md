# Configuration & Registry System - Vietnam Dashboard
# Hệ thống Cấu hình & Registry - Bảng điều khiển Thị trường Chứng khoán Việt Nam

**Version:** 4.0.0
**Last Updated:** 2025-12-15
**Status:** ✅ READY FOR STREAMLIT REBUILD

---

## 📋 Mục Lục / Table of Contents

1. [🚀 STREAMLIT DEVELOPMENT GUIDE](#-streamlit-development-guide) **← START HERE**
2. [Tổng Quan / Overview](#-tổng-quan--overview)
3. [Cấu Trúc Thư Mục / Directory Structure](#-cấu-trúc-thư-mục--directory-structure)
4. [Hệ Thống Registry / Registry System](#-hệ-thống-registry--registry-system)
5. [Tiêu Chuẩn Đơn Vị / Unit Standards](#-tiêu-chuẩn-đơn-vị--unit-standards-v400)
6. [Quy Tắc Docstring / Docstring Rules](#-quy-tắc-docstring--docstring-rules)
7. [Cách Sử Dụng / Usage Examples](#-cách-sử-dụng--usage-examples)
8. [Công Cụ Xây Dựng / Builder Tools](#-công-cụ-xây-dựng--builder-tools)
9. [Tài Liệu Tham Khảo / References](#-tài-liệu-tham-khảo--references)

---

## 🚀 STREAMLIT DEVELOPMENT GUIDE
## Hướng Dẫn Phát Triển Streamlit

**Status:** Config cleaned, ready for Streamlit rebuild (2025-12-14)

### 🎯 Quick Start / Bắt Đầu Nhanh

```python
# 1. Import registries
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry

# 2. Initialize
metric_reg = MetricRegistry()
sector_reg = SectorRegistry()
schema_reg = SchemaRegistry()

# 3. Load display configs
charts_config = schema_reg.get_display_schema('charts')
tables_config = schema_reg.get_display_schema('tables')
dashboards_config = schema_reg.get_display_schema('dashboards')

# 4. Load processed data
import pandas as pd

company_data = pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")
bank_data = pd.read_parquet("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")
technical_data = pd.read_parquet("DATA/processed/technical/basic_data.parquet")
valuation_data = pd.read_parquet("DATA/processed/valuation/pe/pe_historical.parquet")
```

### 📂 Files Cần Sử Dụng / Files to Use

#### 1. **Display Schemas** (Chart/Table/Dashboard Configs)
```
config/schema_registry/display/
├── charts.json       → Thêm configs cho Plotly charts
├── tables.json       → Thêm configs cho Streamlit tables
└── dashboards.json   → Thêm configs cho dashboard layouts
```

**Ví dụ sử dụng:**
```python
from config.schema_registry import SchemaRegistry

registry = SchemaRegistry()

# Load chart config
chart_config = registry.get_display_schema('charts')
# Customize for your Streamlit chart
pe_chart_config = chart_config.get('pe_ratio_chart', {})

# Load table config
table_config = registry.get_display_schema('tables')
financial_table = table_config.get('financial_summary_table', {})
```

#### 2. **Unit Standards** (Data Formatting)
```
config/unit_standards.json → v4.0.0 formatting rules
```

**Quy tắc quan trọng:**
- **Absolute values**: Stored in VND (not billions) → Display as "X.X Tỷ VND"
- **Ratios**: Stored as decimal (0.15) → Display as "15%"
- **Multiples**: Stored as float (15.2) → Display as "15.2x"
- **Per-share**: Stored in VND/share → Display as "X,XXX VND/cp"

**Ví dụ formatting:**
```python
from config.schema_registry import SchemaRegistry

registry = SchemaRegistry()

# Format price
price_str = registry.format_price(25750.5)  # "25,750.50đ"

# Format percentage
pct_str = registry.format_percentage(0.1523, show_sign=True)  # "+15.23%"

# Format market cap
mcap_str = registry.format_market_cap(12_241_737_677_888)  # "12,241.7B"

# Format ratio
pe_str = registry.format_ratio(15.234)  # "15.23"
```

#### 3. **Registries** (Data Lookups)
```python
from config.registries import MetricRegistry, SectorRegistry

# Metric lookup (2,099 metrics)
metric_reg = MetricRegistry()
metric = metric_reg.get_metric("CIS_62", "COMPANY")
# Returns: {'description': 'Chi phí quản lý doanh nghiệp', 'unit': 'VND', ...}

roe_formula = metric_reg.get_calculated_metric_formula("roe")
# Returns formula function for ROE calculation

# Sector lookup (457 tickers × 19 sectors)
sector_reg = SectorRegistry()
ticker_info = sector_reg.get_ticker("ACB")
# Returns: {'sector': 'Banking', 'entity_type': 'BANK', ...}

peers = sector_reg.get_peers("ACB")
# Returns: ['VCB', 'CTG', 'BID', 'TCB', ...]
```

#### 4. **Processed Data** (Ready to Use)
```python
import pandas as pd

# Company financials
company_df = pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")
# Columns: total_revenue, net_profit, roe, roa, debt_to_equity, etc.
# Units: VND for absolute values, decimals for ratios (per v4.0.0)

# Bank financials
bank_df = pd.read_parquet("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")
# Columns: nii, toi, nim_q, roea_ttm, npl_ratio, casa_ratio, etc.

# Technical indicators
technical_df = pd.read_parquet("DATA/processed/technical/basic_data.parquet")
# Columns: ma_20, ma_50, rsi, macd, bollinger_upper, atr, etc.

# Valuation metrics
pe_df = pd.read_parquet("DATA/processed/valuation/pe/pe_historical.parquet")
pb_df = pd.read_parquet("DATA/processed/valuation/pb/pb_historical.parquet")
```

### 📊 Streamlit Page Structure / Cấu Trúc Page Streamlit

**Recommended pattern:**

```python
# WEBAPP/pages/my_dashboard.py

import streamlit as st
import pandas as pd
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry

# Initialize
metric_reg = MetricRegistry()
sector_reg = SectorRegistry()
schema_reg = SchemaRegistry()

# Page config
st.set_page_config(page_title="My Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    return pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")

df = load_data()

# Sidebar filters
with st.sidebar:
    st.title("Filters")
    sectors = st.multiselect("Sectors", sector_reg.get_all_sectors())

# Main content
st.title("My Dashboard")

# Chart (using schema config)
chart_config = schema_reg.get_display_schema('charts')
fig = create_chart(df, chart_config)
st.plotly_chart(fig)

# Table (using schema config + formatting)
table_config = schema_reg.get_display_schema('tables')
formatted_df = format_dataframe(df, schema_reg)
st.dataframe(formatted_df)
```

### 🎨 Display Schema Examples / Ví Dụ Display Schemas

**config/schema_registry/display/charts.json:**
```json
{
  "pe_ratio_chart": {
    "title": "PE Ratio Over Time",
    "chart_type": "line",
    "x_axis": "report_date",
    "y_axis": "pe_ratio",
    "color_field": "sector",
    "height": 400,
    "show_legend": true,
    "plotly_config": {
      "displayModeBar": true,
      "responsive": true
    }
  },
  "revenue_bar_chart": {
    "title": "Quarterly Revenue",
    "chart_type": "bar",
    "x_axis": "quarter",
    "y_axis": "total_revenue",
    "format_y": "billions_vnd",
    "height": 350
  }
}
```

**config/schema_registry/display/tables.json:**
```json
{
  "financial_summary_table": {
    "title": "Financial Summary",
    "columns": [
      {"field": "ticker", "header": "Mã CK", "width": 80},
      {"field": "total_revenue", "header": "Doanh thu", "format": "billions_vnd"},
      {"field": "net_profit", "header": "Lợi nhuận", "format": "billions_vnd"},
      {"field": "roe", "header": "ROE", "format": "percentage"},
      {"field": "pe_ratio", "header": "P/E", "format": "ratio"}
    ],
    "default_sort": {"field": "total_revenue", "order": "desc"},
    "page_size": 25
  }
}
```

### 📝 Checklist for Streamlit Development

- [ ] **Config Setup**
  - [ ] Đọc display schemas từ `config/schema_registry/display/`
  - [ ] Load unit standards từ `config/unit_standards.json`
  - [ ] Initialize registries (MetricRegistry, SectorRegistry)

- [ ] **Data Loading**
  - [ ] Load processed data từ `DATA/processed/`
  - [ ] Verify units (VND, decimals) theo v4.0.0
  - [ ] Cache data với `@st.cache_data`

- [ ] **Formatting**
  - [ ] Sử dụng `schema_reg.format_price()` cho giá
  - [ ] Sử dụng `schema_reg.format_percentage()` cho tỷ lệ
  - [ ] Sử dụng `schema_reg.format_market_cap()` cho vốn hóa
  - [ ] Verify không hardcode formatting

- [ ] **Charts & Tables**
  - [ ] Load configs từ charts.json/tables.json
  - [ ] Customize configs cho specific use cases
  - [ ] Add interactivity (filters, date pickers)

- [ ] **Testing**
  - [ ] Test với multiple tickers
  - [ ] Test với different sectors
  - [ ] Test date range filtering
  - [ ] Verify formatting consistency

### 🔄 Development Workflow / Quy Trình Phát Triển

1. **Plan your page/dashboard**
   - Xác định data sources (company/bank/technical/valuation)
   - Thiết kế layout (charts, tables, metrics)
   - Define filters (sector, date range, tickers)

2. **Add display configs**
   - Update `config/schema_registry/display/charts.json`
   - Update `config/schema_registry/display/tables.json`
   - Update `config/schema_registry/display/dashboards.json`

3. **Build Streamlit page**
   - Create `WEBAPP/pages/your_page.py`
   - Import registries và schemas
   - Load data from `DATA/processed/`
   - Apply formatting theo v4.0.0

4. **Test & iterate**
   - Run: `streamlit run WEBAPP/main_app.py`
   - Test filters và interactivity
   - Verify formatting consistency
   - Optimize performance (caching)

### ⚡ Performance Tips

```python
# Use caching for data loading
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_company_data():
    return pd.read_parquet("DATA/processed/fundamental/company/company_financial_metrics.parquet")

# Use caching for expensive computations
@st.cache_data
def calculate_sector_averages(df, sector):
    return df[df['sector'] == sector].mean()

# Load only required columns
df = pd.read_parquet("DATA/processed/...", columns=['ticker', 'report_date', 'roe', 'pe_ratio'])

# Filter data early
df = df[df['report_date'] >= start_date]
```

---

## 🎯 Tổng Quan / Overview

Thư mục `config/` chứa toàn bộ cấu hình, metadata, registry, và business logic cho Vietnam Dashboard. Đây là "single source of truth" cho:

- **Metric Definitions**: 2,099+ financial metrics từ BSC database
- **Sector Mappings**: 457 tickers × 19 sectors × 4 entity types
- **Schema Definitions**: Data schemas cho fundamental, technical, valuation
- **Unit Standards**: Quy chuẩn v4.0.0 cho việc lưu trữ và hiển thị dữ liệu
- **Business Logic**: Quy tắc phân tích, cảnh báo, ra quyết định

---

## 📁 Cấu Trúc Thư Mục / Directory Structure

**✅ CLEANED (2025-12-14):**
- Removed legacy schemas & backward compatibility code
- **Removed DATA/metadata/** (duplicates of config/metadata/)
- **Single Source of Truth:** All metadata now in `config/metadata/`

```
config/
│
├── 📚 REGISTRIES - Python Lookup Classes
│   ├── registries/
│   │   ├── __init__.py                      # Exports: MetricRegistry, SectorRegistry
│   │   ├── metric_lookup.py                 # 🔍 MetricRegistry - 2,099 metrics lookup
│   │   ├── sector_lookup.py                 # 🏢 SectorRegistry - Ticker/sector mapping
│   │   └── builders/                        # Registry builder scripts
│   │       ├── build_metric_registry.py     # BSC Excel → metric_registry.json
│   │       └── build_sector_registry.py     # Metadata → sector_registry.json
│   │
│   ├── schema_registry.py                   # 🎨 SchemaRegistry - Formatting utilities
│   └── sector_analysis/                     # Sector analysis configuration
│       └── config_manager.py                # FA/TA weights management
│
├── 📊 METADATA - Core Data Assets
│   └── metadata/
│       ├── metric_registry.json             # 770 KB - 2,099 metrics (CANONICAL)
│       ├── formula_registry.json            # Calculated metric formulas
│       ├── raw_metric_registry.json         # Raw BSC metric codes
│       └── ticker_details.json              # Ticker metadata
│
├── 🎨 SCHEMAS - Data Structure Definitions
│   └── schema_registry/                     # ⭐ ACTIVE - All schemas here
│       ├── core/                           # Core types & entities
│       │   ├── types.json                  # Base data types
│       │   ├── entities.json               # Entity definitions
│       │   └── mappings.json               # Field mappings
│       │
│       ├── domain/                         # Domain-specific schemas
│       │   ├── fundamental/                # Fundamental analysis
│       │   ├── technical/                  # Technical indicators
│       │   ├── valuation/                  # Valuation models
│       │   └── unified/                    # Sector analysis
│       │
│       └── display/                        # 🎨 UI/UX configs for Streamlit
│           ├── charts.json                 # Chart configurations
│           ├── tables.json                 # Table layouts
│           └── dashboards.json             # Dashboard specs
│
├── 🧠 BUSINESS LOGIC - Analysis & Decision Rules
│   └── business_logic/
│       ├── analysis/                       # Analysis configurations
│       ├── decisions/                      # Decision engine rules
│       └── alerts/                         # Alert system
│
├── 📏 STANDARDS & CONFIG
│   ├── unit_standards.json                 # v4.0.0 formatting rules
│   ├── __init__.py                         # Package initialization
│   └── README.md                           # This file
│
└── 📖 DOCUMENTATION
    ├── README.md                            # This file
    └── JSON_FILES_AUDIT.md                 # JSON file audit log
```

---

## 🔧 Hệ Thống Registry / Registry System

### 1. MetricRegistry - Financial Metrics Lookup

**File:** `config/registries/metric_lookup.py`
**Data:** `config/metadata/metric_registry.json` (770 KB, 2,099 metrics)

**Chức năng / Features:**
- Tra cứu metric theo code (VD: `CIS_62`, `BBS_400`)
- Tìm kiếm theo tên Tiếng Việt (VD: "lợi nhuận", "tài sản")
- Lấy công thức cho calculated metrics (VD: ROE, ROIC)
- Hỗ trợ 4 entity types: COMPANY, BANK, INSURANCE, SECURITY

**Sử dụng / Usage:**
```python
from config.registries import MetricRegistry

registry = MetricRegistry()

# Tra cứu metric theo code
metric = registry.get_metric("CIS_62", "COMPANY")
print(metric['description'])  # "Chi phí quản lý doanh nghiệp"

# Tìm kiếm theo tên Tiếng Việt
results = registry.search_by_name("lợi nhuận")

# Lấy công thức calculated metric
roe_formula = registry.get_calculated_metric_formula("roe")
```

**Cấu trúc dữ liệu / Data Structure:**
```json
{
  "version": "1.0",
  "last_updated": "2025-12-10",
  "entity_types": {
    "COMPANY": {
      "income_statement": {"CIS_10": {...}, "CIS_62": {...}},
      "balance_sheet": {"CBS_270": {...}, "CBS_400": {...}},
      "cash_flow": {"CCFI_20": {...}}
    }
  },
  "calculated_metrics": {
    "roe": {
      "formula": "net_income / avg_equity * 100",
      "unit": "%"
    }
  }
}
```

---

### 2. SectorRegistry - Ticker/Sector Mapping

**File:** `config/registries/sector_lookup.py`
**Data:** `config/metadata/sector_industry_registry.json`

**Chức năng / Features:**
- Map ticker → entity type (COMPANY/BANK/SECURITY)
- Map ticker → sector (19 sectors)
- Tìm peer companies (same sector)
- Validation ticker có tồn tại

**Sử dụng / Usage:**
```python
from config.registries import SectorRegistry

registry = SectorRegistry()

# Lấy thông tin ticker
info = registry.get_ticker("ACB")
print(info['entity_type'])  # "BANK"
print(info['sector'])        # "Banking"

# Tìm peer companies
peers = registry.get_peers("ACB")  # Returns: ['VCB', 'CTG', 'BID', ...]

# Validate ticker
is_valid = registry.validate_ticker("ACB")  # True
```

**Dữ liệu / Data:**
- **457 tickers** (390 companies, 24 banks, 37 securities, 6 insurance)
- **19 sectors** (Banking, Real Estate, Technology, ...)
- **4 entity types** (COMPANY, BANK, INSURANCE, SECURITY)

---

### 3. SchemaRegistry - Schema & Formatting Utilities

**File:** `config/schema_registry.py`

**Chức năng / Features:**
- Central schema management
- Formatting utilities (price, volume, percentages)
- Color schemes
- Chart configurations

**Sử dụng / Usage:**
```python
from config.schema_registry import SchemaRegistry

registry = SchemaRegistry()  # Singleton pattern

# Formatting
price_str = registry.format_price(25750.5)       # "25,750.50đ"
volume_str = registry.format_volume(1_500_000)   # "1.5M"
pct_str = registry.format_percentage(0.0523)     # "5.23%"

# Get schema
ohlcv_schema = registry.get_schema('ohlcv')

# Colors
green = registry.get_color('positive_change')
red = registry.get_color('negative_change')
```

---

## 🎯 Tiêu Chuẩn Đơn Vị / Unit Standards (v4.0.0)

**File:** `config/unit_standards.json`

### Nguyên Tắc Chính / Key Principles

1. **Storage Layer (Lớp Lưu Trữ):** Lưu giá trị RAW (VND, decimal ratios)
2. **Display Layer (Lớp Hiển Thị):** UI/Streamlit xử lý formatting
3. **Precision (Độ Chính Xác):** Tối đa hóa bằng cách lưu giá trị đầy đủ
4. **Consistency (Nhất Quán):** Tất cả entity types tuân theo cùng chuẩn

### Bảng Chuẩn Hóa / Standardization Table

| Loại Chỉ Số | Đơn Vị Lưu Trữ | Ví Dụ Lưu | Hiển Thị | Ví Dụ Hiển Thị |
|-------------|----------------|-----------|----------|----------------|
| **Giá Trị Tuyệt Đối**<br>(Revenue, Assets, Equity) | **VND** | `2,500,123,000` | `value/1e9` + " Tỷ" | `2.5 Tỷ VND` |
| **Tỷ Suất / Biên**<br>(ROE, NIM, Margins) | **Decimal (0-1)** | `0.1523` | `value*100` + "%" | `15.23%` |
| **Trên Mỗi Cổ Phần**<br>(EPS, BVPS, DPS) | **VND/share** | `15,234` | `#,##0` + " VND/cp" | `15,234 VND/cp` |
| **Hệ Số**<br>(P/E, Leverage, Debt/Equity) | **Times (x)** | `15.23` | `0.00x` | `15.23x` |

### Ví Dụ Sử Dụng / Usage Example

```python
# ✅ CORRECT: Storage in VND, ratios as decimals
data = {
    'total_assets': 12_241_737_677_888,    # VND (not billions)
    'total_equity': 6_017_883_172_138,     # VND
    'roe': 0.1523,                         # Decimal (15.23%)
    'nim': 0.0337,                         # Decimal (3.37%)
    'debt_to_equity': 0.4766,              # Ratio
    'eps': 15_234                          # VND per share
}

# Display layer formatting
from config.unit_standards import format_metric

# Absolute values → Billions
st.metric("Total Assets", format_metric(data['total_assets'], "total_assets"))
# Output: "12,241.7 Tỷ VND"

# Ratios → Percentage
st.metric("ROE", format_metric(data['roe'], "roe"))
# Output: "15.23%"

# Per share → VND/share
st.metric("EPS", format_metric(data['eps'], "eps"))
# Output: "15,234 VND/cp"
```

**Tài liệu đầy đủ:** Xem `config/unit_standards.json` để biết chi tiết implementation.

---

## 📝 Quy Tắc Docstring / Docstring Rules

### Tiêu Chuẩn Bắt Buộc / Mandatory Standards

Tất cả file Python trong dự án **BẮT BUỘC** phải có docstring **SONG NGỮ** (Tiếng Việt + English):

#### 1. Module Docstring (Đầu File)

```python
#!/usr/bin/env python3
"""
Module Name - Mô Tả Ngắn Gọn (Tiếng Việt)
=====================================

English Brief Description.

Tính năng chính (Main Features):
---------------------------------
- Tính năng 1 (Feature 1)
- Tính năng 2 (Feature 2)
- Tính năng 3 (Feature 3)

Sử dụng (Usage):
---------------
    from module_name import ClassName

    obj = ClassName()
    result = obj.method()

Tác giả (Author): Your Name
Ngày tạo (Created): 2025-12-14
Phiên bản (Version): 1.0.0
"""
```

#### 2. Class Docstring

```python
class MetricRegistry:
    """
    Registry tra cứu financial metrics từ BSC database.
    Financial metrics lookup registry from BSC database.

    Chức năng (Features):
    - Tra cứu metric theo code (VD: CIS_62, BBS_400)
    - Tìm kiếm theo tên Tiếng Việt
    - Lấy công thức calculated metrics

    Features:
    - Lookup metrics by code (e.g., CIS_62, BBS_400)
    - Search by Vietnamese name
    - Get calculated metric formulas

    Thuộc tính (Attributes):
        metrics (dict): Dictionary chứa toàn bộ metrics
        metrics (dict): Dictionary containing all metrics

    Ví dụ (Example):
        >>> registry = MetricRegistry()
        >>> metric = registry.get_metric("CIS_62", "COMPANY")
        >>> print(metric['description'])
        'Chi phí quản lý doanh nghiệp'
    """
```

#### 3. Function/Method Docstring

```python
def get_metric(self, code: str, entity_type: str) -> dict:
    """
    Tra cứu metric theo code và entity type.
    Lookup metric by code and entity type.

    Args:
        code (str): Mã metric (VD: "CIS_62", "BBS_400")
                   Metric code (e.g., "CIS_62", "BBS_400")
        entity_type (str): Loại entity ("COMPANY", "BANK", "SECURITY")
                          Entity type ("COMPANY", "BANK", "SECURITY")

    Returns:
        dict: Thông tin metric bao gồm description, unit, category
             Metric information including description, unit, category

    Raises:
        KeyError: Nếu code không tồn tại
                 If code does not exist
        ValueError: Nếu entity_type không hợp lệ
                   If entity_type is invalid

    Ví dụ (Example):
        >>> metric = self.get_metric("CIS_62", "COMPANY")
        >>> print(metric['description'])
        'Chi phí quản lý doanh nghiệp'
    """
```

#### 4. Quy Tắc Bổ Sung / Additional Rules

1. **Constants & Variables:**
   ```python
   # Đơn vị chuẩn cho lưu trữ (VND)
   # Standard storage unit (VND)
   STORAGE_UNIT_VND = "VND"

   # Tỷ lệ chuyển đổi sang tỷ
   # Conversion ratio to billions
   BILLION_CONVERSION = 1e9
   ```

2. **Complex Logic Comments:**
   ```python
   # Tính ROAE (TTM) = Net Profit TTM / Equity Avg 2Q
   # Calculate ROAE (TTM) = Net Profit TTM / Equity Avg 2Q
   result_df['roae_ttm'] = self.safe_divide(
       numerator=result_df['net_profit_ttm'],
       denominator=result_df['equity_avg_2q']
   )
   ```

3. **TODO & FIXME:**
   ```python
   # TODO: Thêm validation cho metric code format
   # TODO: Add validation for metric code format

   # FIXME: Xử lý edge case khi denominator = 0
   # FIXME: Handle edge case when denominator = 0
   ```

### Công Cụ Kiểm Tra / Validation Tools

**Kiểm tra docstring:**
```bash
# Check if all Python files have bilingual docstrings
python3 scripts/validate_docstrings.py config/
```

---

## 💡 Cách Sử Dụng / Usage Examples

### Example 1: Tra Cứu Metric và Format Hiển Thị

```python
from config.registries import MetricRegistry
from config.unit_standards import format_metric
import pandas as pd

# Load data
df = pd.read_parquet("DATA/processed/fundamental/company_financial_metrics.parquet")

# Get metric info
registry = MetricRegistry()
metric_info = registry.get_metric("CIS_62", "COMPANY")

# Extract value
latest = df.iloc[-1]
total_assets = latest['total_assets']  # 12,241,737,677,888 VND

# Format for display
formatted = format_metric(total_assets, "total_assets")
print(formatted)  # "12,241.7 Tỷ VND"
```

### Example 2: Phân Tích Sector với Peer Comparison

```python
from config.registries import SectorRegistry

registry = SectorRegistry()

# Get ticker info
ticker = "ACB"
info = registry.get_ticker(ticker)

print(f"Ticker: {info['ticker']}")
print(f"Entity Type: {info['entity_type']}")
print(f"Sector: {info['sector']}")

# Find peers
peers = registry.get_peers(ticker)
print(f"\nPeer Banks: {', '.join(peers[:5])}")

# Output:
# Ticker: ACB
# Entity Type: BANK
# Sector: Banking
#
# Peer Banks: VCB, CTG, BID, TCB, MBB
```

### Example 3: Tạo Dashboard với Unit Standards

```python
import streamlit as st
from config.unit_standards import format_metric
from config.schema_registry import SchemaRegistry

schema_reg = SchemaRegistry()

# Sample data (stored in canonical units)
data = {
    'total_assets': 12_241_737_677_888,  # VND
    'roe': 0.1523,                       # Decimal
    'nim': 0.0337,                       # Decimal
    'eps': 15_234                        # VND/share
}

# Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Assets",
        format_metric(data['total_assets'], 'total_assets'),
        delta=None
    )

with col2:
    st.metric(
        "ROE",
        format_metric(data['roe'], 'roe'),
        delta="+2.3%"
    )

with col3:
    st.metric(
        "NIM",
        format_metric(data['nim'], 'nim'),
        delta="-0.1%"
    )

with col4:
    st.metric(
        "EPS (TTM)",
        format_metric(data['eps'], 'eps'),
        delta="+1,200"
    )
```

---

## 🔨 Công Cụ Xây Dựng / Builder Tools

### 1. Build Metric Registry

**Mục đích:** Chuyển đổi BSC Excel templates → `metric_registry.json`

```bash
python3 config/registries/builders/build_metric_registry.py
```

**Input:**
- Excel files from BSC database
- Company, Bank, Insurance, Security entity templates

**Output:**
- `config/metadata/metric_registry.json` (770 KB)
- 2,099 metrics mapped

---

### 2. Build Sector Registry

**Mục đích:** Xây dựng sector/industry registry từ ticker metadata

```bash
python3 config/registries/builders/build_sector_registry.py
```

**Input:**
- `config/metadata/ticker_details.json`
- `config/metadata/all_tickers.csv`

**Output:**
- `config/metadata/sector_industry_registry.json`
- 457 tickers × 19 sectors × 4 entity types

---

## 📚 Tài Liệu Tham Khảo / References

### Internal Documentation

- **Project Overview:** [CLAUDE.md](../CLAUDE.md)
- **Formula Migration Plan:** [formula_migration_plan.md](../formula_migration_plan.md)
- **Data Management Plan:** [config/metadata/data_management_plan.md](metadata/data_management_plan.md)
- **JSON Files Audit:** [config/JSON_FILES_AUDIT.md](JSON_FILES_AUDIT.md)

### Key Configuration Files

| File | Purpose | Size | Records |
|------|---------|------|---------|
| `unit_standards.json` | v4.0.0 Unit standardization | 8.5 KB | Canonical |
| `metric_registry.json` | Financial metrics lookup | 770 KB | 2,099 metrics |
| `sector_industry_registry.json` | Sector/ticker mapping | ~50 KB | 457 tickers |

### External Resources

- **BSC Financial Database:** Source of metric definitions
- **Vnstock API:** Market data provider
- **Streamlit Documentation:** Dashboard framework

---

## 🔄 Migration History

### 2025-12-15: Config Cleanup & Daily Pipeline Consolidation

**Changes:**
1. ✅ Deleted `config/data_sources.json` (old paths, unused)
2. ✅ Deleted `config/frequency_filtering_rules.json` (unused)
3. ✅ Fixed `config/sector_analysis/config_manager.py` path casing ("CONFIG" → "config")
4. ✅ Consolidated all daily scripts to `PROCESSORS/pipelines/`
5. ✅ Created master orchestrator `run_all_daily_updates.py` with progress tracking

**Impact:** Cleaner config structure, easier daily updates

### 2025-12-14: Unit Standardization v4.0.0

**Changes:**
1. ✅ Created `unit_standards.json` with complete specification
2. ✅ Updated all calculators to store in VND (not billions)
3. ✅ Changed ratios to decimals (not percentages)
4. ✅ Added bilingual docstring requirements

**Impact:** All fundamental calculators now follow v4.0.0 standard

### 2025-12-10: Registry & Schema Cleanup

**Changes:**
1. ✅ Moved `PROCESSORS/core/registries/` → `config/registries/`
2. ✅ Removed 3 duplicate schema files
3. ✅ Removed 2 duplicate `metric_registry.json` copies
4. ✅ Deleted legacy `SchemaRegistry` from PROCESSORS

**Storage Saved:** ~2.4 MB

**Import Pattern Changed:**
```python
# ✅ NEW (canonical)
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry

# ❌ OLD (deprecated)
from PROCESSORS.core.registries.metric_lookup import MetricRegistry
```

---

## ⚠️ Important Notes / Lưu Ý Quan Trọng

### 1. Single Source of Truth

`config/metadata/metric_registry.json` là **CANONICAL** source:
- **KHÔNG** tạo copies
- **KHÔNG** edit manually
- **CHỈ** sử dụng builder scripts để update

### 2. Backward Compatibility

Các file trong `config/schemas/` là **LEGACY**:
- Giữ lại cho backward compatibility
- **KHÔNG** sử dụng cho code mới
- Sử dụng `config/schema_registry/` thay thế

### 3. Unit Standards Enforcement

Tất cả calculators **BẮT BUỘC** tuân theo v4.0.0:
- Storage in VND (not billions)
- Ratios as decimals (not percentages)
- No conversion at calculator layer

### 4. Docstring Requirement

Tất cả Python files **BẮT BUỘC** có bilingual docstrings:
- Module-level docstring
- Class docstring
- Function/method docstrings
- Tiếng Việt + English

---

## 🆘 Troubleshooting

### Issue: Import Error

```python
ImportError: cannot import name 'MetricRegistry' from 'config.registries'
```

**Solution:**
```bash
# Check if __init__.py exists
ls config/registries/__init__.py

# Re-import with correct path
from config.registries import MetricRegistry
```

### Issue: Wrong Unit Values

```python
# Asset value shows 12.24 instead of 12,241.7 billion
```

**Solution:** Check calculator is using v4.0.0 standard:
```python
# ✅ CORRECT
result_df['total_assets'] = df.get('CBS_270', np.nan)  # Raw VND

# ❌ WRONG
result_df['total_assets'] = df.get('CBS_270', np.nan) / 1e9  # Billions
```

---

## 📞 Contact / Liên Hệ

**Maintainer:** Vietnam Dashboard Team
**Documentation:** This file (`config/README.md`)
**Issues:** [GitHub Issues](https://github.com/your-repo/issues)

---

**Last Updated:** 2025-12-15
**Version:** 4.0.0
**Status:** ✅ Production Ready
