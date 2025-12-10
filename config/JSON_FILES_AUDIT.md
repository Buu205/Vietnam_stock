# JSON Files Audit Report
**Date:** 2025-12-10  
**Purpose:** Kiểm tra và đánh giá các file JSON trong config/

## 📊 Tổng Quan

- **Total JSON files:** 50 files
- **Files with actual data:** 45 files
- **Placeholder/Reference files:** 5 files

## 🔍 Phân Loại Files

### ✅ Files Được Sử Dụng (Active)

#### 1. Schema Registry Files (17 files)
**Location:** `config/schema_registry/`

**Core Schemas (3 files):**
- ✅ `core/entities.json` - Entity definitions (COMPANY, BANK, INSURANCE, SECURITY)
- ✅ `core/types.json` - Data type definitions
- ✅ `core/mappings.json` - Field mappings and relationships

**Domain Schemas (11 files):**
- ✅ `domain/fundamental/metrics.json` - Financial metrics definitions
- ✅ `domain/fundamental/reports.json` - Financial report structures
- ✅ `domain/fundamental/calculations.json` - Calculation formulas
- ✅ `domain/technical/indicators.json` - Technical indicator definitions
- ✅ `domain/technical/signals.json` - Trading signal schemas
- ✅ `domain/technical/trends.json` - Trend analysis schemas
- ✅ `domain/valuation/metrics.json` - Valuation metric definitions
- ✅ `domain/valuation/models.json` - Valuation model schemas
- ✅ `domain/unified/sector.json` - Unified sector schema
- ✅ `domain/unified/decisions.json` - Decision-making schemas
- ✅ `domain/unified/insights.json` - AI insights schemas

**Display Schemas (3 files):**
- ✅ `display/charts.json` - Chart visualization schemas
- ✅ `display/tables.json` - Table display schemas
- ✅ `display/dashboards.json` - Dashboard layout schemas

**Usage:** Loaded via `SchemaRegistry.get_schema()`, `get_domain_schema()`, `get_core_schema()`, `get_display_schema()`

---

#### 2. Master Schema (1 file)
**Location:** `config/schemas/`
- ✅ `master_schema.json` - Master schema with global settings (app_metadata, theme, formatting_rules, etc.)

**Usage:** Loaded automatically by `SchemaRegistry._load_all_schemas()`

---

#### 3. Business Logic Configs (9 files)
**Location:** `config/business_logic/`

**Analysis (4 files):**
- ✅ `analysis/fa_analysis.json` - Fundamental analysis settings
- ✅ `analysis/ta_analysis.json` - Technical analysis settings
- ✅ `analysis/valuation_analysis.json` - Valuation analysis settings
- ✅ `analysis/unified_analysis.json` - Unified analysis settings

**Decisions (3 files):**
- ✅ `decisions/rules.json` - Trading decision rules
- ✅ `decisions/weights.json` - Scoring weight configurations
- ✅ `decisions/thresholds.json` - Decision threshold settings

**Alerts (3 files):**
- ✅ `alerts/rules.json` - Alert triggering rules
- ✅ `alerts/channels.json` - Alert delivery channels
- ✅ `alerts/subscriptions.json` - Alert subscriptions

**Usage:** Loaded via `SchemaRegistry.get_business_logic(category, schema_name)`

---

### ⚠️ Files Chưa Được Sử Dụng (Placeholder/Reference)

#### 4. Metadata Registry - Placeholder Files (5 files)
**Location:** `config/metadata_registry/`

**Tickers (3 files):**
- ⚠️ `tickers/all_tickers.json` - **PLACEHOLDER** (chỉ có note, không có data thực)
- ⚠️ `tickers/sector_mappings.json` - **PLACEHOLDER** (chỉ có note)
- ⚠️ `tickers/exchange_mappings.json` - **PLACEHOLDER** (có structure nhưng chưa có data)

**Sectors (3 files):**
- ⚠️ `sectors/industry.json` - **PLACEHOLDER** (chỉ có structure, note reference đến DATA/metadata)
- ⚠️ `sectors/vn_industry.json` - **PLACEHOLDER** (chỉ có note)
- ⚠️ `sectors/mappings.json` - **PLACEHOLDER** (chỉ có structure, note reference)

**Metrics (3 files):**
- ⚠️ `metrics/fundamental_metrics.json` - **REFERENCE FILE** (reference đến metric_registry.json)
- ⚠️ `metrics/technical_metrics.json` - **REFERENCE FILE** (reference đến schema_registry)
- ⚠️ `metrics/valuation_metrics.json` - **REFERENCE FILE** (reference đến schema_registry)

**Config (3 files):**
- ✅ `config/sources.json` - Data source configurations (có data thực)
- ✅ `config/updates.json` - Update schedules and versions (có data thực)
- ✅ `config/quality.json` - Data quality standards (có data thực)

**Note:** Các placeholder files này được tạo để làm reference, nhưng actual data nằm ở:
- `DATA/metadata/metric_registry.json` (753KB, 2,099+ metrics)
- `DATA/metadata/sector_industry_registry.json`
- `PROCESSORS/core/registries/sector_lookup.py` (UnifiedTickerMapper)

---

### ❓ Files Cần Kiểm Tra (Potentially Unused)

#### 5. Root Config Files (2 files)
**Location:** `config/`

- ❓ `data_sources.json` - **CẦN KIỂM TRA**
  - Có 344 lines, chứa data source configurations
  - Paths trong file này vẫn dùng **OLD paths** (`data_warehouse/`, `calculated_results/`)
  - **VẤN ĐỀ:** Không thấy được sử dụng trong codebase
  - **ĐỀ XUẤT:** 
    - Option 1: Xóa nếu không dùng
    - Option 2: Cập nhật paths → v4.0.0 canonical paths và tích hợp vào `metadata_registry/config/sources.json`

- ❓ `frequency_filtering_rules.json` - **CẦN KIỂM TRA**
  - Có 36 lines, chứa frequency filtering rules
  - **VẤN ĐỀ:** Không thấy được sử dụng trong codebase
  - **ĐỀ XUẤT:**
    - Option 1: Xóa nếu không dùng
    - Option 2: Tích hợp vào `business_logic/decisions/rules.json` hoặc tạo file mới trong `business_logic/`

---

## 🎯 Đề Xuất Hành Động

### Priority 1: Files Cần Xử Lý Ngay

1. **`config/data_sources.json`**
   - ❌ **Không được sử dụng** trong codebase
   - ❌ **Paths đã lỗi thời** (data_warehouse, calculated_results)
   - ✅ **Đã có thay thế:** `config/metadata_registry/config/sources.json`
   - **Hành động:** Xóa hoặc archive

2. **`config/frequency_filtering_rules.json`**
   - ❌ **Không được sử dụng** trong codebase
   - ✅ **Có thể tích hợp** vào business_logic
   - **Hành động:** Di chuyển vào `business_logic/decisions/rules.json` hoặc xóa

### Priority 2: Files Cần Cải Thiện

3. **Placeholder Files trong `metadata_registry/`**
   - ⚠️ 5 files chỉ có notes, không có data thực
   - **Hành động:** 
     - Option A: Giữ lại làm documentation/reference
     - Option B: Xóa và chỉ giữ README.md

4. **Reference Files trong `metadata_registry/metrics/`**
   - ⚠️ 3 files chỉ reference đến files khác
   - **Hành động:** Giữ lại vì có giá trị documentation

---

## 📋 Checklist

- [ ] Xóa `config/data_sources.json` (đã có thay thế)
- [ ] Xóa hoặc di chuyển `config/frequency_filtering_rules.json`
- [ ] Quyết định về placeholder files (giữ/xóa)
- [ ] Cập nhật documentation nếu cần

---

## 📊 Summary

| Category | Total | Active | Placeholder | Unused |
|----------|-------|--------|-------------|--------|
| Schema Registry | 17 | 17 | 0 | 0 |
| Master Schema | 1 | 1 | 0 | 0 |
| Business Logic | 9 | 9 | 0 | 0 |
| Metadata Registry | 12 | 3 | 9 | 0 |
| Root Config | 2 | 0 | 0 | 2 |
| **TOTAL** | **41** | **30** | **9** | **2** |

**Note:** Có thêm `config/metric_registry.json` (753KB) nhưng đã được copy vào `config/metadata_registry/metrics/metric_registry.json`
