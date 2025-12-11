# 🏭 SECTOR/INDUSTRY MAPPING SYSTEM - Data Standardization Foundation

**Priority:** 🔴 **CRITICAL - Must Complete Before Phase 2**
**Status:** 📝 **Planning Phase**
**Date:** 2025-12-05

---

## 📋 EXECUTIVE SUMMARY

Sector/Industry Mapping System là **nền tảng bắt buộc** để:
1. **Chuẩn hóa phân loại** ticker theo ngành và loại báo cáo tài chính
2. **Gọi đúng calculator** theo entity type (BANK/COMPANY/SECURITY/INSURANCE)
3. **So sánh peers** trong cùng ngành
4. **Apply công thức** phù hợp với từng loại báo cáo
5. **MCP Agent compatibility** - AI có thể query và hiểu data structure

---

## 🎯 BUSINESS REQUIREMENTS

### Vấn đề hiện tại

Hệ thống hiện có **400+ mã cổ phiếu** chia theo:

1. **4 Entity Types (Loại báo cáo tài chính):**
   - `COMPANY` - Các ngành sản xuất (390 tickers)
   - `BANK` - Ngân hàng (24 tickers)
   - `SECURITY` - Chứng khoán (37 tickers)
   - `INSURANCE` - Bảo hiểm (6 tickers)

2. **19 Sectors (Nhóm ngành chi tiết):**
   - Ngân hàng (24) → Entity: BANK
   - Dịch vụ tài chính (37) → Entity: SECURITY
   - Bảo hiểm (6) → Entity: INSURANCE
   - Xây dựng và Vật liệu (76) → Entity: COMPANY
   - Thực phẩm và đồ uống (39) → Entity: COMPANY
   - Tài nguyên Cơ bản (37) → Entity: COMPANY
   - Điện, nước & xăng dầu khí đốt (18) → Entity: COMPANY
   - Công nghệ Thông tin (8) → Entity: COMPANY
   - Hóa chất (27) → Entity: COMPANY
   - Hàng & Dịch vụ Công nghiệp (38) → Entity: COMPANY
   - Bán lẻ (9) → Entity: COMPANY
   - Bất động sản (75) → Entity: COMPANY
   - Truyền thông (6) → Entity: COMPANY
   - Du lịch và Giải trí (10) → Entity: COMPANY
   - Viễn thông (4) → Entity: COMPANY
   - Ô tô và phụ tùng (7) → Entity: COMPANY
   - Dầu khí (8) → Entity: COMPANY
   - Hàng cá nhân & Gia dụng (14) → Entity: COMPANY
   - Y tế (14) → Entity: COMPANY

### Yêu cầu

1. **Mapping chuẩn hóa** giữa:
   - Ticker → Entity Type
   - Ticker → Sector
   - Sector → Entity Type
   - Sector → Metric Codes (từ metric_registry.json)

2. **Dễ dàng extend** cho Phase 2:
   - Gọi calculator đúng theo entity type
   - Tính toán metrics khác nhau cho từng ngành
   - So sánh peers trong cùng sector

3. **MCP Agent compatibility:**
   - AI có thể query: "Các cổ phiếu ngành xây dựng"
   - AI hiểu được: "Ticker VCB thuộc entity type BANK"
   - AI tự động chọn metric codes phù hợp

---

## 📊 CURRENT DATA STRUCTURE

### File 1: `ticker_entity_mapping.json`

**Location:** `/Users/buuphan/Dev/stock_dashboard/data_warehouse/raw/metadata/ticker_entity_mapping.json`

**Structure:**
```json
{
  "TPB": "BANK",
  "VCB": "BANK",
  "VIC": "COMPANY",
  "EVF": "SECURITY",
  "PVI": "INSURANCE",
  ...
}
```

**Purpose:** Simple mapping ticker → entity type only
**Coverage:** 457 tickers
**Limitation:** ❌ Không có sector information

---

### File 2: `ticker_details.json`

**Location:** `/Users/buuphan/Dev/stock_dashboard/data_warehouse/raw/metadata/ticker_details.json`

**Structure:**
```json
{
  "TPB": {
    "entity": "BANK",
    "sector": "Ngân hàng"
  },
  "VIC": {
    "entity": "COMPANY",
    "sector": "Bất động sản"
  },
  "EVF": {
    "entity": "SECURITY",
    "sector": "Dịch vụ tài chính"
  },
  ...
}
```

**Purpose:** Full mapping ticker → entity + sector
**Coverage:** 457 tickers
**Advantage:** ✅ Có đầy đủ thông tin entity + sector

---

### File 3: `entity_statistics.json`

**Location:** `/Users/buuphan/Dev/stock_dashboard/data_warehouse/raw/metadata/entity_statistics.json`

**Structure:**
```json
{
  "total_tickers": 457,
  "by_entity": {
    "BANK": 24,
    "SECURITY": 37,
    "INSURANCE": 6,
    "COMPANY": 390
  },
  "by_sector": {
    "Ngân hàng": {
      "count": 24,
      "entity": "BANK",
      "sample_tickers": ["TPB", "NVB", "VPB", "STB", "VCB"]
    },
    "Bất động sản": {
      "count": 75,
      "entity": "COMPANY",
      "sample_tickers": ["TLD", "SGR", "VRG", "CKG", "NVL"]
    },
    ...
  }
}
```

**Purpose:** Statistics and sector grouping
**Coverage:** 19 sectors
**Advantage:** ✅ Có thống kê và sample tickers

---

## 🎯 PROPOSED STANDARDIZED MAPPING SYSTEM

### Phase 0.1.5: Sector/Industry Mapping Registry

**Timeline:** 1-2 ngày (trước Phase 2)

**Goal:** Tạo unified mapping system với structure chuẩn, dễ query và extend

---

### 1. Unified Mapping File Structure

**New File:** `data_warehouse/metadata/sector_industry_registry.json`

```json
{
  "version": "1.0",
  "last_updated": "2025-12-05T00:00:00Z",
  "metadata": {
    "total_tickers": 457,
    "total_sectors": 19,
    "total_entity_types": 4
  },
  
  "entity_types": {
    "COMPANY": {
      "description": "Các ngành sản xuất và dịch vụ",
      "count": 390,
      "metric_registry_key": "COMPANY",
      "calculator_class": "CompanyFinancialCalculator",
      "sectors": [
        "Xây dựng và Vật liệu",
        "Thực phẩm và đồ uống",
        "Tài nguyên Cơ bản",
        ...
      ]
    },
    "BANK": {
      "description": "Ngân hàng thương mại",
      "count": 24,
      "metric_registry_key": "BANK",
      "calculator_class": "BankFinancialCalculator",
      "sectors": [
        "Ngân hàng"
      ]
    },
    "SECURITY": {
      "description": "Công ty chứng khoán",
      "count": 37,
      "metric_registry_key": "SECURITY",
      "calculator_class": "SecurityFinancialCalculator",
      "sectors": [
        "Dịch vụ tài chính"
      ]
    },
    "INSURANCE": {
      "description": "Công ty bảo hiểm",
      "count": 6,
      "metric_registry_key": "INSURANCE",
      "calculator_class": "InsuranceFinancialCalculator",
      "sectors": [
        "Bảo hiểm"
      ]
    }
  },
  
  "sectors": {
    "Ngân hàng": {
      "entity_type": "BANK",
      "count": 24,
      "description": "Ngân hàng thương mại Việt Nam",
      "tickers": ["TPB", "NVB", "VPB", "STB", "VCB", ...],
      "metric_prefixes": ["BIS_", "BBS_", "BCF_"],
      "key_metrics": ["ROE", "ROA", "NIM", "CAR"]
    },
    "Xây dựng và Vật liệu": {
      "entity_type": "COMPANY",
      "count": 76,
      "description": "Công ty xây dựng và vật liệu xây dựng",
      "tickers": ["VLB", "VC2", "C4G", "THG", "DFF", ...],
      "metric_prefixes": ["CIS_", "CBS_", "CCF_"],
      "key_metrics": ["ROE", "ROA", "gross_margin", "net_margin"]
    },
    "Bất động sản": {
      "entity_type": "COMPANY",
      "count": 75,
      "description": "Công ty bất động sản và phát triển",
      "tickers": ["TLD", "SGR", "VRG", "CKG", "NVL", ...],
      "metric_prefixes": ["CIS_", "CBS_", "CCF_"],
      "key_metrics": ["ROE", "ROA", "gross_margin", "inventory_turnover"]
    },
    ...
  },
  
  "ticker_mapping": {
    "TPB": {
      "entity_type": "BANK",
      "sector": "Ngân hàng",
      "name": "Ngân hàng Tiên Phong",
      "exchange": "HOSE",
      "industry_code": "BANK"
    },
    "VIC": {
      "entity_type": "COMPANY",
      "sector": "Bất động sản",
      "name": "Tập đoàn Vingroup",
      "exchange": "HOSE",
      "industry_code": "REAL_ESTATE"
    },
    ...
  },
  
  "sector_to_entity_mapping": {
    "Ngân hàng": "BANK",
    "Dịch vụ tài chính": "SECURITY",
    "Bảo hiểm": "INSURANCE",
    "Xây dựng và Vật liệu": "COMPANY",
    "Thực phẩm và đồ uống": "COMPANY",
    ...
  }
}
```

---

### 2. Sector Registry Builder Script

**New File:** `data_processor/core/build_sector_registry.py`

**Purpose:**
- Consolidate data từ `ticker_details.json` + `entity_statistics.json`
- Generate unified `sector_industry_registry.json`
- Validate consistency
- Link với `metric_registry.json`

**Features:**
```python
class SectorRegistryBuilder:
    def __init__(self):
        self.ticker_details_path = "data_warehouse/raw/metadata/ticker_details.json"
        self.entity_stats_path = "data_warehouse/raw/metadata/entity_statistics.json"
        self.metric_registry_path = "data_warehouse/metadata/metric_registry.json"
        self.output_path = "data_warehouse/metadata/sector_industry_registry.json"
    
    def build_registry(self):
        """Build unified sector/industry registry"""
        # 1. Load ticker details
        # 2. Load entity statistics
        # 3. Load metric registry (for linking)
        # 4. Build entity_types section
        # 5. Build sectors section
        # 6. Build ticker_mapping section
        # 7. Build sector_to_entity_mapping
        # 8. Validate consistency
        # 9. Save to JSON
        pass
    
    def validate(self):
        """Validate registry consistency"""
        # - All tickers have entity_type
        # - All tickers have sector
        # - Sector → Entity mapping is consistent
        # - No orphaned sectors
        pass
```

---

### 3. Sector Lookup Utility

**New File:** `data_processor/core/sector_lookup.py`

**Purpose:** Fast lookup utility (similar to MetricRegistry)

**Usage Examples:**

```python
from data_processor.core.sector_lookup import SectorRegistry

registry = SectorRegistry()

# Get ticker info
vcb_info = registry.get_ticker("VCB")
# → {"entity_type": "BANK", "sector": "Ngân hàng", ...}

# Get all tickers in sector
construction_tickers = registry.get_tickers_by_sector("Xây dựng và Vật liệu")
# → ["VLB", "VC2", "C4G", ...]

# Get all sectors for entity type
company_sectors = registry.get_sectors_by_entity("COMPANY")
# → ["Xây dựng và Vật liệu", "Thực phẩm và đồ uống", ...]

# Get calculator class for ticker
calculator_class = registry.get_calculator_class("VCB")
# → "BankFinancialCalculator"

# Get metric prefixes for sector
metric_prefixes = registry.get_metric_prefixes("Ngân hàng")
# → ["BIS_", "BBS_", "BCF_"]

# Search sectors
results = registry.search_sectors("xây dựng")
# → [{"sector": "Xây dựng và Vật liệu", ...}]

# Get peers (same sector)
vcb_peers = registry.get_peers("VCB")
# → ["TPB", "NVB", "VPB", ...] (all banks)
```

---

## 🔗 INTEGRATION WITH METRIC REGISTRY

### Link Sector → Metric Codes

**Concept:** Mỗi sector có thể map đến metric prefixes từ `metric_registry.json`

```python
# Sector "Ngân hàng" → Entity "BANK" → Metrics với prefix "BIS_", "BBS_", "BCF_"
# Sector "Xây dựng và Vật liệu" → Entity "COMPANY" → Metrics với prefix "CIS_", "CBS_", "CCF_"

from data_processor.core.sector_lookup import SectorRegistry
from data_processor.core.metric_lookup import MetricRegistry

sector_reg = SectorRegistry()
metric_reg = MetricRegistry()

# Get available metrics for a ticker's sector
ticker = "VCB"
ticker_info = sector_reg.get_ticker(ticker)
entity_type = ticker_info["entity_type"]

# Get all metrics for this entity type
bank_metrics = metric_reg.get_metrics_by_entity(entity_type)
# → [{"code": "BIS_1", "name": "Tổng doanh thu", ...}, ...]

# Get specific metric for this entity
revenue_metric = metric_reg.get_metric("BIS_1", entity_type)
# → {"code": "BIS_1", "name": "Tổng doanh thu", "unit": "VND", ...}
```

---

## 🎯 PHASE 2 INTEGRATION

### How Sector Registry Enables Phase 2

**1. Auto-select Calculator:**

```python
from data_processor.core.sector_lookup import SectorRegistry

sector_reg = SectorRegistry()

def get_calculator_for_ticker(ticker: str):
    """Auto-select calculator based on ticker's entity type"""
    ticker_info = sector_reg.get_ticker(ticker)
    entity_type = ticker_info["entity_type"]
    
    calculator_map = {
        "COMPANY": CompanyFinancialCalculator,
        "BANK": BankFinancialCalculator,
        "SECURITY": SecurityFinancialCalculator,
        "INSURANCE": InsuranceFinancialCalculator
    }
    
    return calculator_map[entity_type]()

# Usage
ticker = "VCB"
calculator = get_calculator_for_ticker(ticker)
# → BankFinancialCalculator instance
```

**2. Sector-specific Calculations:**

```python
def calculate_sector_metrics(ticker: str, metrics_df: pd.DataFrame):
    """Calculate metrics with sector-specific formulas"""
    ticker_info = sector_reg.get_ticker(ticker)
    sector = ticker_info["sector"]
    entity_type = ticker_info["entity_type"]
    
    # Get sector-specific key metrics
    key_metrics = sector_reg.get_sector(sector)["key_metrics"]
    
    # Calculate with sector-specific logic
    if sector == "Bất động sản":
        # Real estate specific calculations
        metrics_df["inventory_turnover"] = calculate_inventory_turnover(...)
    elif sector == "Ngân hàng":
        # Banking specific calculations
        metrics_df["nim"] = calculate_net_interest_margin(...)
    
    return metrics_df
```

**3. Peer Comparison:**

```python
def get_peer_comparison(ticker: str, metric: str):
    """Compare ticker with peers in same sector"""
    peers = sector_reg.get_peers(ticker)
    
    # Get metric values for all peers
    peer_data = []
    for peer_ticker in peers:
        peer_metric_value = get_metric_value(peer_ticker, metric)
        peer_data.append({
            "ticker": peer_ticker,
            "value": peer_metric_value
        })
    
    # Calculate statistics
    return {
        "ticker": ticker,
        "sector": sector_reg.get_ticker(ticker)["sector"],
        "peers": peer_data,
        "mean": np.mean([p["value"] for p in peer_data]),
        "median": np.median([p["value"] for p in peer_data]),
        "percentile": calculate_percentile(ticker_value, peer_data)
    }
```

---

## 📁 FILE STRUCTURE

```
stock_dashboard/
├── data_warehouse/
│   └── metadata/
│       ├── sector_industry_registry.json      ✅ NEW (unified mapping)
│       ├── metric_registry.json               ✅ EXISTS (link with this)
│       └── ...
│
├── data_warehouse/raw/metadata/
│   ├── ticker_entity_mapping.json             📍 SOURCE (simple mapping)
│   ├── ticker_details.json                    📍 SOURCE (full mapping)
│   ├── entity_statistics.json                 📍 SOURCE (statistics)
│   └── all_tickers.csv                        📍 SOURCE (CSV format)
│
└── data_processor/core/
    ├── build_sector_registry.py               ✅ NEW (builder script)
    ├── sector_lookup.py                       ✅ NEW (lookup utility)
    ├── build_metric_registry.py               ✅ EXISTS
    └── metric_lookup.py                       ✅ EXISTS
```

---

## ✅ VALIDATION REQUIREMENTS

### 1. Completeness Checks

- ✅ All 457 tickers have entity_type
- ✅ All 457 tickers have sector
- ✅ All sectors have entity_type mapping
- ✅ All entity types have at least 1 sector

### 2. Consistency Checks

- ✅ Ticker → Entity mapping matches ticker_details.json
- ✅ Ticker → Sector mapping matches ticker_details.json
- ✅ Sector → Entity mapping is consistent across all tickers
- ✅ No ticker has conflicting entity_type and sector

### 3. Integration Checks

- ✅ All entity types have corresponding calculator classes
- ✅ All entity types have metric prefixes in metric_registry.json
- ✅ Sector key_metrics exist in metric_registry.json

---

## 🚀 IMPLEMENTATION PLAN

### Step 1: Create Builder Script (Day 1 - Morning)

**File:** `data_processor/core/build_sector_registry.py`

**Tasks:**
1. Load ticker_details.json
2. Load entity_statistics.json
3. Load metric_registry.json (for linking)
4. Build entity_types section
5. Build sectors section (with statistics)
6. Build ticker_mapping section
7. Build sector_to_entity_mapping
8. Validate all checks
9. Save to JSON

**Output:** `sector_industry_registry.json` (unified format)

---

### Step 2: Create Lookup Utility (Day 1 - Afternoon)

**File:** `data_processor/core/sector_lookup.py`

**Tasks:**
1. Create SectorRegistry class
2. Implement get_ticker() method
3. Implement get_sector() method
4. Implement get_tickers_by_sector() method
5. Implement get_sectors_by_entity() method
6. Implement get_peers() method
7. Implement get_calculator_class() method
8. Implement search_sectors() method
9. Add integration with MetricRegistry

**Output:** Full-featured lookup utility

---

### Step 3: Create Test Suite (Day 2 - Morning)

**File:** `data_processor/core/test_sector_registry.py`

**Test Cases:**
1. Registry structure validation
2. Completeness (all tickers covered)
3. Consistency (no conflicts)
4. Integration with metric_registry
5. Lookup utility functionality
6. Performance (query speed)
7. MCP agent compatibility

**Output:** 7/7 tests passing

---

### Step 4: Integration with Existing Code (Day 2 - Afternoon)

**Update Existing Files:**

1. `data_processor/technical/technical/technical_indicators/technical_processor.py`
   - Replace hardcoded sector mapping
   - Use SectorRegistry instead

2. `data_processor/valuation/sector_pe_calculator.py`
   - Use SectorRegistry for sector mapping
   - Ensure consistency

3. `data_processor/fundamental/base/base_financial_calculator.py` (Phase 2)
   - Use SectorRegistry to auto-select calculator
   - Use sector info for metric selection

**Output:** All code uses unified SectorRegistry

---

### Step 5: Documentation (Day 2 - End)

**Update Documentation:**

1. Add to `DATA_STANDARDIZATION.md`
2. Add usage examples
3. Add MCP agent query examples
4. Update architecture summary

**Output:** Complete documentation

---

## 📊 SUCCESS CRITERIA

✅ **Registry Completeness:**
- All 457 tickers mapped
- All 19 sectors defined
- All 4 entity types configured

✅ **Integration:**
- Links with metric_registry.json
- Works with existing calculators
- Ready for Phase 2 refactoring

✅ **Performance:**
- Lookup < 1ms per query
- Load time < 100ms

✅ **MCP Compatibility:**
- AI can query: "What sector is VCB?"
- AI can query: "Get all construction stocks"
- AI can query: "What calculator for BANK entity?"

✅ **Code Quality:**
- All tests passing (7/7)
- Documentation complete
- Usage examples provided

---

## 🔄 NEXT STEPS AFTER COMPLETION

1. **Phase 2: Unified Calculator**
   - Use SectorRegistry to auto-select calculators
   - Implement sector-specific calculation logic
   - Reduce code duplication

2. **MCP Agent Integration**
   - Add sector queries to MCP tools
   - Enable AI to understand sector structure
   - Query raw data by sector

3. **Dashboard Enhancement**
   - Sector comparison views
   - Peer analysis
   - Sector rotation indicators

---

## 📝 NOTES

- **File Naming:** Keep existing files as source, create new unified registry
- **Backward Compatibility:** Existing code continues to work, gradually migrate
- **Performance:** Registry loaded once, cached in memory
- **Extensibility:** Easy to add new sectors or entity types

---

## 🎯 TIMELINE

**Total Duration:** 2 days

- **Day 1:** Builder script + Lookup utility (6-8 hours)
- **Day 2:** Tests + Integration + Documentation (6-8 hours)

**Dependencies:**
- ✅ Phase 1 (Metric Registry) - COMPLETED
- ✅ Source files (ticker_details.json, etc.) - EXISTS

**Blockers:** None

---

**Status:** 📝 **Ready to Implement**

**Next Action:** Start with Step 1 - Create Builder Script

---

*Last Updated: 2025-12-05*
*Author: Data Standardization Team*

