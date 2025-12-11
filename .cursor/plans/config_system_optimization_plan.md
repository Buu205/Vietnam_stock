# CONFIG SYSTEM OPTIMIZATION PLAN
## Vietnamese Stock Market Dashboard - Configuration Architecture

---

**Plan Created:** 2025-12-11
**Author:** Claude Code (Senior Developer + Senior Finance Analyst)
**Priority:** HIGH - Foundation for all display and calculation features
**Estimated Effort:** 3-5 days
**Current Status:** 85% Complete, needs cleanup and consolidation

---

## EXECUTIVE SUMMARY

The config system currently works but has accumulated technical debt through multiple iterations. This plan optimizes the schema registry architecture, removes duplication, completes missing schemas, and establishes a single source of truth for all configurations.

**Key Goals:**
1. Remove unused/duplicate files (11 files identified)
2. Complete missing schemas (fundamental benchmarks, display schemas)
3. Clarify data sources and precedence
4. Improve schema loading performance
5. Document schema dependencies clearly

---

## 1. CURRENT STATE ANALYSIS

### 1.1 Directory Structure Overview

```
config/
├── registries/                          ✅ CANONICAL (8 files, ~1,900 lines)
│   ├── __init__.py
│   ├── metric_lookup.py                (MetricRegistry - 2,099 metrics)
│   ├── sector_lookup.py                (SectorRegistry - 457 tickers × 19 sectors)
│   └── builders/
│       ├── build_metric_registry.py    (Excel → JSON builder)
│       └── build_sector_registry.py    (Metadata → JSON builder)
│
├── schema_registry.py                   ✅ SINGLETON (584 lines)
│
├── schema_registry/                     ✅ NEW ORGANIZED (19 JSON files)
│   ├── core/                           (3 files - types, entities, mappings)
│   ├── domain/                         (11 files - fundamental, technical, valuation, unified)
│   └── display/                        (3 files - charts, tables, dashboards)
│
├── metadata/                            ✅ PRIMARY DATA (2 files, 771 KB)
│   ├── metric_registry.json            (770 KB - 2,099 metrics)
│   └── ticker_details.json             (36 KB)
│
├── business_logic/                      ✅ COMPLETE (9 files)
│   ├── analysis/                       (FA, TA, valuation, unified configs)
│   ├── decisions/                      (Rules, weights, thresholds)
│   └── alerts/                         (Rules, channels, subscriptions)
│
├── sector_analysis/                     ✅ NEW (2 files)
│   ├── __init__.py
│   └── config_manager.py               (ConfigManager for FA/TA weights)
│
├── schemas/                             ⚠️ LEGACY (10 files - backward compat)
│   ├── master_schema.json              (✅ CẦN THIẾT - vẫn sử dụng cho định dạng, màu sắc, validation; lưu ý: kế hoạch dọn dẹp này phục vụ cho tối ưu hóa hệ thống config cho Streamlit, sau sẽ tối ưu bổ sung/sửa lại tùy giao diện app cần gì)
│   └── data/                           (Các schemas OHLCV, fundamental, technical - PHẦN LỚN ĐÃ ĐƯỢC THAY bởi schemas mới; CHUẨN BỊ XOÁ/ARCHIVE. CHỈ GIỮ LẠI file còn được service sử dụng, còn lại XOÁ để giảm nhiễu cho config system.)
│        ↑ Đánh giá: Folder này giữ cho backward compatibility. Nếu toàn bộ code đã chuyển sang `config/schema_registry/` thì CLAUDE XOÁ TẤT CẢ các schema trong này ngoại trừ `master_schema.json`. Mục đích: dọn kho, giảm duplication và technical debt.

├── data_sources.json                    ❌ KHÔNG CẦN THIẾT - không còn sử dụng, paths lỗi thời (nên xoá)
└── frequency_filtering_rules.json       ❌ KHÔNG CẦN THIẾT - không còn sử dụng (nên xoá)
```

### 1.2 Key Statistics

| Category | Count | Lines | Status |
|----------|-------|-------|--------|
| Registry Classes | 3 | ~1,900 | ✅ Complete |
| Core Schemas | 3 | ~250 | ✅ Complete |
| Domain Schemas | 11 | ~450 | ⚠️ 80% complete |
| Display Schemas | 3 | ~100 | ⚠️ Incomplete |
| Business Logic | 9 | ~400 | ✅ Complete |
| Master Schema | 1 | 233 | ✅ Complete |
| **TOTAL** | **30** | **~3,300** | **✅ 85%** |

**Problems Identified:**
- 11 unused/placeholder files
- 2 minor duplications (ohlcv variants, master_schema)
- Missing fundamental benchmarks schema
- Incomplete display schemas (tables, dashboards)
- No reconciliation schema for financial statements

---

## 2. ISSUES & TECHNICAL DEBT

### 2.1 Critical Issues

| Issue | Severity | Impact | Files Affected |
|-------|----------|--------|----------------|
| **Unused config files** | MEDIUM | Clutter, confusion | `data_sources.json`, `frequency_filtering_rules.json` |
| **Duplicate schemas** | LOW | Inconsistency risk | `ohlcv.json` vs `ohlcv_schema.json`, `master_schema.json` (2 locations) |
| **Placeholder files** | LOW | Misleading docs | 9 files in `metadata_registry/` |
| **Incomplete display schemas** | MEDIUM | Display logic hardcoded | `tables.json`, `dashboards.json` |
| **Missing validation schemas** | HIGH | No metric requirements per entity | None - needs creation |
| **Schema search chain too long** | LOW | Slow startup | `schema_registry.py` lines 264-360 |

### 2.2 Duplication Analysis

1. **OHLCV Schemas**
   - `config/schemas/data/ohlcv_schema.json` (older)
   - `config/schemas/data/ohlcv.json` (newer)
   - **Action:** Keep `ohlcv_schema.json`, delete `ohlcv.json`

2. **Master Schema**
   - `config/schemas/master_schema.json` (primary, 233 lines)
   - `config/schemas/data/master_schema.json` (duplicate)
   - **Action:** Delete duplicate in `data/` subdirectory

3. **Kiểm tra và chuyển hướng sử dụng Metric Registry**

   - **Yêu cầu:** Kiểm tra lại tất cả các file Python trong thư mục `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS` đang import hoặc thao tác với `metric_registry.json`/`metric_registry`/`metric_registor` hoặc các biến liên quan đến metric registry.
   - **Hướng dẫn:** Tất cả các file/processors chỉ được sử dụng `metric_registry.json` từ folder `config/metadata/` để đảm bảo dễ quản lý và tập trung – KHÔNG được truy cập trực tiếp file trong `DATA/metadata/` hết, toàn bộ logic registry/lookup sẽ thông qua API/lớp đọc từ `config`.
   - **Ghi chú cập nhật:** Sửa lại các file có truy cập cũ (`DATA/metadata/metric_registry.json`) thành import/lấy từ `config/metadata/metric_registry.json` hoặc class tương ứng trong `config/registries/metric_lookup.py`.
   - **Cần thực hiện:** 
     1. Rà soát (search: 'metric_registry', 'metric_registor') toàn bộ code dưới PROCESSORS. 
     2. Sửa các đường dẫn hardcode hoặc load file registry về canonical path (`config/metadata/metric_registry.json`).
     3. Đảm bảo tất cả registry đều access qua config registry layer, không trực tiếp đọc file ngoài.
   - **Lưu ý:** Nếu `config/metadata/metric_registry.json` chỉ là placeholder, cần copy bản mới nhất từ `DATA/metadata/` vào `config/metadata/` và cập nhật README chú thích rõ: "Đây là bản duy nhất được phép dùng cho toàn bộ hệ thống."

   - **Action:** Thực hiện di chuyển, cập nhật và thống nhất lại source của metric registry về duy nhất folder `config/metadata/`, đồng thời update lại codebase để sử dụng path này cho tất cả các nơi import/lookup liên quan (thay cho mọi path cũ như `DATA/metadata/`). Ngoài ra kiểm tra và cập nhật lại path nếu cần để đảm bảo mọi đoạn code truy cập metric registry đều thống nhất qua layer của `config/registries/` hoặc file `config/metadata/metric_registry.json`, không đọc file trực tiếp ở vị trí khác.

### 2.3 Missing Schemas

| Missing Schema | Purpose | Priority | Target Location |
|----------------|---------|----------|-----------------|
| **Fundamental Benchmarks** | Industry benchmarks by entity type | HIGH | `schema_registry/domain/fundamental/benchmarks.json` |
| **Metric Requirements** | Required metrics per entity type | HIGH | `schema_registry/domain/fundamental/requirements.json` |
| **Financial Reconciliation** | How statements relate to each other | MEDIUM | `schema_registry/domain/fundamental/reconciliation.json` |
| **Display Tables (Complete)** | Full table display configuration | MEDIUM | `schema_registry/display/tables.json` |
| **Display Dashboards (Complete)** | Full dashboard layout schemas | MEDIUM | `schema_registry/display/dashboards.json` |

---

## 3. OPTIMIZATION PHASES

### PHASE 1: CLEANUP & REMOVAL (1 day)

**Goal:** Remove unused files and duplicates

#### Phase 1.1: Delete Unused Files
```bash
# Files to delete (3 files)
rm config/data_sources.json
rm config/frequency_filtering_rules.json
rm config/schemas/data/ohlcv.json
```

**Files:**
- `data_sources.json` - Uses deprecated paths, not imported anywhere
- `frequency_filtering_rules.json` - Standalone, not integrated
- `ohlcv.json` - Duplicate of `ohlcv_schema.json`

#### Phase 1.2: Remove Duplicate Master Schema
```bash
# Remove duplicate
rm config/schemas/data/master_schema.json

# Keep: config/schemas/master_schema.json (primary)
```

#### Phase 1.3: Clean Up Metadata Registry Placeholders

**Decision Point:** Keep or delete `config/metadata_registry/` placeholders?

**Option A (Recommended):** Keep as documentation
- Add `README.md` explaining they are references
- Clarify that actual data is in `DATA/metadata/`

**Option B:** Delete all placeholders
- Remove entire `config/metadata_registry/` directory
- Update `SchemaRegistry` to skip searching this location

**Recommendation:** Option A - Keep as documentation with clear README

**Actions:**
```bash
# Create README
cat > config/metadata_registry/README.md << 'EOF'
# Metadata Registry Reference

This directory contains reference/documentation files only.

**PRIMARY DATA SOURCES:**
- Metric Registry: `DATA/metadata/metric_registry.json` (770 KB, 2,099 metrics)
- Sector Registry: `DATA/metadata/sector_industry_registry.json`
- Ticker Details: `config/metadata/ticker_details.json` (36 KB)

**DO NOT** place actual data files here. Use `DATA/metadata/` for all registry data.
EOF
```

#### Phase 1.4: Update CLAUDE.md

**Update configuration section with cleanup status:**
```markdown
## Configuration & Registry System (config/)

**CANONICAL STRUCTURE (Updated 2025-12-11):**

config/
├── registries/                    # ✅ Registry lookup classes
├── schema_registry.py            # ✅ SchemaRegistry singleton
├── schema_registry/              # ✅ Organized schemas (19 files)
├── metadata/                     # ✅ Small metadata (ticker_details.json)
├── business_logic/               # ✅ Business rules
├── sector_analysis/              # ✅ Sector analysis config
└── schemas/                      # ⚠️ LEGACY (backward compatibility)

**PRIMARY DATA SOURCES:**
- Metric Registry: `DATA/metadata/metric_registry.json` (770 KB)
- Sector Registry: `DATA/metadata/sector_industry_registry.json`
```

---

### PHASE 2: COMPLETE MISSING SCHEMAS (2 days)

**Goal:** Create missing schemas for fundamental metrics and display

#### Phase 2.1: Fundamental Benchmarks Schema

**File:** `config/schema_registry/domain/fundamental/benchmarks.json`

**Content Structure:**
```json
{
  "schema_version": "1.0.0",
  "description": "Industry benchmark ranges for financial metrics",
  "last_updated": "2025-12-11",

  "benchmarks_by_entity": {
    "COMPANY": {
      "profitability": {
        "roe": {
          "excellent": {"min": 20, "max": null},
          "good": {"min": 15, "max": 20},
          "average": {"min": 10, "max": 15},
          "poor": {"min": 0, "max": 10},
          "unit": "percentage"
        },
        "roa": {
          "excellent": {"min": 15, "max": null},
          "good": {"min": 10, "max": 15},
          "average": {"min": 5, "max": 10},
          "poor": {"min": 0, "max": 5},
          "unit": "percentage"
        },
        "net_margin": {
          "excellent": {"min": 20, "max": null},
          "good": {"min": 10, "max": 20},
          "average": {"min": 5, "max": 10},
          "poor": {"min": 0, "max": 5},
          "unit": "percentage"
        }
      },
      "growth": {
        "revenue_growth_yoy": {
          "excellent": {"min": 30, "max": null},
          "good": {"min": 15, "max": 30},
          "average": {"min": 5, "max": 15},
          "poor": {"min": null, "max": 5},
          "unit": "percentage"
        }
      },
      "leverage": {
        "debt_to_equity": {
          "excellent": {"min": 0, "max": 0.5},
          "good": {"min": 0.5, "max": 1.0},
          "average": {"min": 1.0, "max": 2.0},
          "poor": {"min": 2.0, "max": null},
          "unit": "ratio"
        }
      }
    },

    "BANK": {
      "profitability": {
        "roea": {
          "excellent": {"min": 18, "max": null},
          "good": {"min": 15, "max": 18},
          "average": {"min": 10, "max": 15},
          "poor": {"min": 0, "max": 10},
          "unit": "percentage"
        },
        "nim": {
          "excellent": {"min": 4, "max": null},
          "good": {"min": 3, "max": 4},
          "average": {"min": 2, "max": 3},
          "poor": {"min": 0, "max": 2},
          "unit": "percentage"
        }
      },
      "asset_quality": {
        "npl_ratio": {
          "excellent": {"min": 0, "max": 1},
          "good": {"min": 1, "max": 2},
          "average": {"min": 2, "max": 3},
          "poor": {"min": 3, "max": null},
          "unit": "percentage"
        }
      }
    }
  },

  "sector_adjustments": {
    "description": "Sector-specific benchmark adjustments",
    "banking": {"profitability_multiplier": 0.9},
    "technology": {"growth_multiplier": 1.5},
    "utilities": {"leverage_multiplier": 1.2}
  }
}
```

**Implementation:**
```python
# Add to SchemaRegistry
def get_benchmark(self, entity_type: str, metric: str, value: float) -> str:
    """Get benchmark rating (excellent/good/average/poor) for a metric value"""
    benchmarks = self.get_domain_schema('fundamental', 'benchmarks')
    # Implementation details...
    return rating  # "excellent", "good", "average", "poor"
```

#### Phase 2.2: Metric Requirements Schema

**File:** `config/schema_registry/domain/fundamental/requirements.json`

**Content Structure:**
```json
{
  "schema_version": "1.0.0",
  "description": "Required metrics and validation rules per entity type",
  "last_updated": "2025-12-11",

  "entity_requirements": {
    "COMPANY": {
      "income_statement": {
        "required": ["CIS_10", "CIS_61", "CIS_20"],
        "recommended": ["CIS_50", "CIS_11"],
        "optional": ["CIS_21", "CIS_22"]
      },
      "balance_sheet": {
        "required": ["CBS_270", "CBS_400", "CBS_300"],
        "recommended": ["CBS_110", "CBS_140"],
        "optional": ["CBS_221"]
      },
      "cash_flow": {
        "required": ["CCFI_20"],
        "recommended": ["CCFI_30", "CCFI_40"],
        "optional": ["CCFI_2", "CCFI_50"]
      },
      "calculated_metrics": {
        "required": ["roe", "roa", "eps"],
        "recommended": ["gross_margin", "net_margin", "debt_to_equity"],
        "optional": ["asset_turnover", "inventory_turnover"]
      }
    },

    "BANK": {
      "income_statement": {
        "required": ["BIS_3", "BIS_22A", "BIS_1", "BIS_2"],
        "recommended": ["BIS_14", "BIS_16"],
        "optional": []
      },
      "balance_sheet": {
        "required": ["BBS_100", "BBS_500", "BBS_120", "BBS_330"],
        "recommended": ["BBS_321"],
        "optional": []
      },
      "notes": {
        "required": ["BNOT_4", "BNOT_26"],
        "recommended": ["BNOT_4_2", "BNOT_4_3"],
        "optional": []
      },
      "calculated_metrics": {
        "required": ["roea", "roaa", "nim", "npl_ratio"],
        "recommended": ["casa_ratio", "cir", "ldr"],
        "optional": ["asset_yield", "funding_cost"]
      }
    }
  },

  "validation_rules": {
    "completeness_threshold": 0.95,
    "description": "Minimum completeness required for valid analysis",
    "missing_data_handling": {
      "required": "error",
      "recommended": "warning",
      "optional": "info"
    }
  }
}
```

#### Phase 2.3: Financial Reconciliation Schema

**File:** `config/schema_registry/domain/fundamental/reconciliation.json`

**Content Structure:**
```json
{
  "schema_version": "1.0.0",
  "description": "How financial statements reconcile with each other",
  "last_updated": "2025-12-11",

  "statement_relationships": {
    "income_to_cashflow": {
      "description": "Net Profit reconciles to Operating Cash Flow",
      "formula": "Operating CF = Net Profit + Non-cash expenses - Working Capital changes",
      "key_adjustments": [
        {"name": "depreciation", "metric_code": "CCFI_2", "add_back": true},
        {"name": "working_capital_change", "calculation": "delta(inventory + receivables - payables)"}
      ]
    },

    "income_to_balance": {
      "description": "Net Profit affects Retained Earnings",
      "formula": "Ending Equity = Beginning Equity + Net Profit - Dividends + Capital Raises",
      "key_metrics": {
        "net_profit": "CIS_61",
        "total_equity": "CBS_400"
      }
    },

    "balance_to_cashflow": {
      "description": "Balance Sheet changes explain Cash Flow movements",
      "formula": "Ending Cash = Beginning Cash + Operating CF + Investing CF + Financing CF",
      "key_metrics": {
        "cash": "CBS_110",
        "operating_cf": "CCFI_20",
        "investing_cf": "CCFI_30",
        "financing_cf": "CCFI_40"
      }
    }
  },

  "validation_checks": {
    "balance_sheet_equation": {
      "formula": "Assets = Liabilities + Equity",
      "tolerance": 0.01,
      "metrics": {
        "assets": "CBS_270",
        "liabilities": "CBS_300",
        "equity": "CBS_400"
      }
    }
  }
}
```

#### Phase 2.4: Complete Display Schemas

**File:** `config/schema_registry/display/tables.json` (expand existing)

**Add sections:**
```json
{
  "fundamental_tables": {
    "income_statement_table": {
      "columns": ["metric_name", "q1", "q2", "q3", "q4", "yoy_growth"],
      "formatting": {
        "revenue": "currency_billions",
        "margins": "percentage",
        "growth": "percentage_with_sign"
      }
    },
    "balance_sheet_table": {
      "columns": ["metric_name", "current_quarter", "previous_quarter", "change"],
      "formatting": {
        "assets": "currency_billions",
        "ratios": "decimal_2"
      }
    }
  },

  "sector_comparison_table": {
    "columns": ["ticker", "roe", "roa", "debt_to_equity", "revenue_growth", "rating"],
    "sorting": {"default": "roe", "direction": "desc"},
    "conditional_formatting": {
      "roe": {"threshold": 15, "above": "success", "below": "warning"}
    }
  }
}
```

**File:** `config/schema_registry/display/dashboards.json` (expand existing)

**Add sections:**
```json
{
  "company_dashboard": {
    "layout": "tabs",
    "tabs": [
      {
        "id": "overview",
        "title": "Tổng quan",
        "components": [
          {"type": "metric_cards", "metrics": ["roe", "revenue_growth", "debt_to_equity"]},
          {"type": "chart", "chart_id": "revenue_trend"},
          {"type": "table", "table_id": "quarterly_summary"}
        ]
      },
      {
        "id": "fundamental",
        "title": "Phân tích cơ bản",
        "components": [
          {"type": "income_statement_chart"},
          {"type": "margin_analysis"},
          {"type": "peer_comparison_table"}
        ]
      }
    ]
  },

  "sector_dashboard": {
    "layout": "rows",
    "sections": [
      {
        "id": "sector_overview",
        "height": "300px",
        "components": [
          {"type": "sector_heatmap"},
          {"type": "top_performers_cards"}
        ]
      },
      {
        "id": "fa_ta_combined",
        "height": "600px",
        "components": [
          {"type": "scatter_plot", "x": "roe", "y": "rsi"},
          {"type": "ranking_table"}
        ]
      }
    ]
  }
}
```

---

### PHASE 3: CLARIFY DATA SOURCES (0.5 days)

**Goal:** Document single source of truth for all registry data

#### Phase 3.1: Update SchemaRegistry Search Priority

**File:** `config/schema_registry.py`

**Change:** Prioritize `DATA/metadata/` FIRST before searching other locations

**Current order:**
1. schema_registry/ (core, domain, display)
2. metadata_registry/ (placeholders)
3. business_logic/
4. Old schemas/

**New order:**
1. **DATA/metadata/** (PRIMARY for metric_registry.json, sector_industry_registry.json)
2. schema_registry/ (core, domain, display)
3. business_logic/
4. Old schemas/ (backward compat)
5. metadata_registry/ (documentation only)

**Implementation:**
```python
def get_schema(self, schema_name: str, schema_type: Optional[str] = None) -> Dict[str, Any]:
    """Load a specific schema with DATA/metadata/ priority"""
    cache_key = f"{schema_type}:{schema_name}" if schema_type else schema_name
    if cache_key in self._schema_cache:
        return self._schema_cache[cache_key]

    schema_file = None

    # PRIORITY 1: Check DATA/metadata/ for large registry files
    if schema_name in ['metric_registry', 'sector_industry_registry']:
        data_metadata_path = Path(__file__).parent.parent / "DATA" / "metadata" / f"{schema_name}.json"
        if data_metadata_path.exists():
            schema_file = data_metadata_path
            logger.info(f"Loaded {schema_name} from DATA/metadata/ (PRIMARY source)")

    # PRIORITY 2: New structure: schema_registry/
    if not schema_file and self.schema_registry_dir.exists():
        # ... existing logic

    # Rest of search chain...
```

#### Phase 3.2: Create Data Source Documentation

**File:** `config/DATA_SOURCES.md`

```markdown
# Config Data Sources - Single Source of Truth

## PRIMARY DATA LOCATIONS

### Large Registry Files (> 100 KB)
**Location:** `DATA/metadata/`

| File | Size | Purpose | Built By |
|------|------|---------|----------|
| `metric_registry.json` | 770 KB | 2,099 financial metrics (Vietnamese → English) | `config/registries/builders/build_metric_registry.py` |
| `sector_industry_registry.json` | ~50 KB | 457 tickers × 19 sectors × 4 entity types | `config/registries/builders/build_sector_registry.py` |

### Small Metadata Files (< 100 KB)
**Location:** `config/metadata/`

| File | Size | Purpose |
|------|------|---------|
| `ticker_details.json` | 36 KB | Detailed ticker information |

### Schema Definitions (JSON schemas)
**Location:** `config/schema_registry/`

- **Core schemas**: types, entities, mappings
- **Domain schemas**: fundamental, technical, valuation, unified
- **Display schemas**: charts, tables, dashboards

### Business Logic Configs
**Location:** `config/business_logic/`

- **Analysis configs**: FA, TA, valuation, unified analysis
- **Decision configs**: Rules, weights, thresholds
- **Alert configs**: Rules, channels, subscriptions

### Legacy Schemas (Backward Compatibility)
**Location:** `config/schemas/`

- `master_schema.json` - Formatting rules, colors, validation thresholds
- `data/` - Old schema files (still loaded by SchemaRegistry)

## REBUILDING REGISTRIES

### Metric Registry
```bash
python config/registries/builders/build_metric_registry.py
# Output: DATA/metadata/metric_registry.json
```

### Sector Registry
```bash
python config/registries/builders/build_sector_registry.py
# Output: DATA/metadata/sector_industry_registry.json
```

## IMPORT PATTERNS

### ✅ CORRECT (Canonical as of 2025-12-11)
```python
from config.registries import MetricRegistry, SectorRegistry
from config.schema_registry import SchemaRegistry
```

### ❌ DEPRECATED (Do not use)
```python
from PROCESSORS.core.registries.metric_lookup import MetricRegistry
from PROCESSORS.core.registries.sector_lookup import SectorRegistry
```
```

---

### PHASE 4: PERFORMANCE OPTIMIZATION (1 day)

**Goal:** Improve schema loading speed and memory efficiency

#### Phase 4.1: Add Schema Validation on Load

**File:** `config/schema_registry.py`

**Add method:**
```python
def _validate_schema(self, schema: Dict, schema_name: str) -> bool:
    """Validate schema has required fields"""
    required_fields = ['schema_version', 'description']

    for field in required_fields:
        if field not in schema:
            logger.warning(f"Schema '{schema_name}' missing required field: {field}")
            return False

    return True
```

#### Phase 4.2: Add Schema Version Checking

**Add to SchemaRegistry:**
```python
def check_schema_versions(self) -> Dict[str, str]:
    """Check all loaded schemas for version compatibility"""
    versions = {}

    for cache_key, schema in self._schema_cache.items():
        version = schema.get('schema_version', 'unknown')
        versions[cache_key] = version

        if version == 'unknown':
            logger.warning(f"Schema '{cache_key}' has no version")

    return versions
```

#### Phase 4.3: Optimize Search Chain

**Current:** 5 locations searched sequentially
**Optimized:** Early exit + logging

```python
def get_schema(self, schema_name: str, schema_type: Optional[str] = None) -> Dict[str, Any]:
    # ... existing cache check

    search_locations = [
        ("DATA/metadata", self._search_data_metadata),
        ("schema_registry", self._search_schema_registry),
        ("business_logic", self._search_business_logic),
        ("legacy schemas", self._search_legacy)
    ]

    for location_name, search_func in search_locations:
        schema_file = search_func(schema_name, schema_type)
        if schema_file:
            logger.debug(f"Found '{schema_name}' in {location_name}")
            break

    # ... rest of loading logic
```

---

### PHASE 5: DOCUMENTATION UPDATES (0.5 days)

**Goal:** Complete documentation for all schemas and registries

#### Phase 5.1: Create README Files

**Files to create:**
- `config/schema_registry/core/README.md` - Core schema docs
- `config/schema_registry/domain/fundamental/README.md` - Fundamental schema docs
- `config/schema_registry/domain/technical/README.md` - Technical schema docs
- `config/schema_registry/domain/valuation/README.md` - Valuation schema docs
- `config/schema_registry/display/README.md` - Display schema docs

**Template:**
```markdown
# [Domain] Schemas

## Overview
[Purpose and scope of these schemas]

## Schema Files

### [schema_name].json
- **Purpose:** [What this schema defines]
- **Used by:** [Which modules/files use this]
- **Key sections:** [Main structure]
- **Example usage:** [Code example]

## Usage Patterns

```python
from config.schema_registry import SchemaRegistry

registry = SchemaRegistry()
schema = registry.get_domain_schema('[domain]', '[schema_name]')
```

## Schema Versioning

Current version: 1.0.0
Last updated: 2025-12-11

## Maintenance

To update these schemas:
1. Edit the JSON file
2. Increment schema_version
3. Update last_updated timestamp
4. Test with SchemaRegistry.check_schema_versions()
```

#### Phase 5.2: Update CLAUDE.md

**Add new sections:**
```markdown
## Configuration System Documentation

### Schema Registry Architecture

**Three-tier system:**
1. **Registries** (Python classes) - Fast lookup, validation
2. **Schemas** (JSON files) - Structure definitions, formatting rules
3. **Business Logic** (JSON configs) - Weights, thresholds, rules

### Loading Precedence

1. DATA/metadata/ - Large registry files (metric, sector registries)
2. schema_registry/ - Organized schemas (core, domain, display)
3. business_logic/ - Analysis configs, decision rules
4. schemas/ - Legacy (backward compatibility)

### Creating New Schemas

**Step 1:** Determine category
- Core: Data types, entities, mappings
- Domain: Business logic (fundamental, technical, valuation)
- Display: UI configs (charts, tables, dashboards)

**Step 2:** Create JSON file in appropriate directory
```json
{
  "schema_version": "1.0.0",
  "description": "Clear description of schema purpose",
  "last_updated": "2025-12-11",
  "data": { ... }
}
```

**Step 3:** Add to SchemaRegistry if custom loading needed

**Step 4:** Document in domain README.md
```

#### Phase 5.3: Create Schema Dependency Graph

**File:** `config/SCHEMA_DEPENDENCIES.md`

**Content:**
```markdown
# Schema Dependency Graph

## Core Dependencies (Foundation)

```
types.json
├── Used by: metrics.json, indicators.json, charts.json
└── Defines: price, volume, percentage, ratio, market_cap, date formats

entities.json
├── Used by: all calculators, sector_lookup.py
└── Defines: COMPANY, BANK, INSURANCE, SECURITY

mappings.json
├── Used by: data pipelines, path resolution
└── Defines: field mappings, v4.0.0 paths, calculator routing
```

## Domain Dependencies

### Fundamental
```
metrics.json
├── Requires: types.json, entities.json
├── Used by: calculators, WEBAPP formatters
└── Defines: ROE, ROA, margins, growth metrics

calculations.json
├── Requires: metrics.json, types.json
├── Used by: formula validation
└── Defines: Formula dependencies, TTM calculations

benchmarks.json (NEW)
├── Requires: metrics.json, entities.json
├── Used by: rating systems, peer comparison
└── Defines: Industry benchmarks by entity type
```

### Technical
```
indicators.json
├── Requires: types.json
├── Used by: technical analyzers, chart components
└── Defines: MA, RSI, MACD, Bollinger, ATR configs
```

### Display
```
charts.json
├── Requires: types.json, indicators.json, metrics.json
├── Used by: WEBAPP chart components
└── Defines: Plotly configs, chart defaults

tables.json (UPDATED)
├── Requires: types.json, metrics.json
├── Used by: WEBAPP table displays
└── Defines: Table layouts, formatting rules, conditional styling
```
```

---

## 4. TESTING & VALIDATION

### Phase 4.1: Schema Validation Tests

**File:** `config/tests/test_schema_validation.py`

```python
import pytest
from pathlib import Path
import json
from config.schema_registry import SchemaRegistry

def test_all_schemas_have_version():
    """All schemas must have schema_version field"""
    schema_dir = Path(__file__).parent.parent / "schema_registry"

    for schema_file in schema_dir.rglob("*.json"):
        with open(schema_file, 'r') as f:
            schema = json.load(f)

        assert 'schema_version' in schema, f"{schema_file.name} missing schema_version"

def test_all_schemas_have_description():
    """All schemas must have description field"""
    schema_dir = Path(__file__).parent.parent / "schema_registry"

    for schema_file in schema_dir.rglob("*.json"):
        with open(schema_file, 'r') as f:
            schema = json.load(f)

        assert 'description' in schema, f"{schema_file.name} missing description"

def test_schema_registry_loads_all():
    """SchemaRegistry can load all schemas without errors"""
    registry = SchemaRegistry()

    # Test core schemas
    assert registry.get_core_schema('types') is not None
    assert registry.get_core_schema('entities') is not None

    # Test domain schemas
    assert registry.get_domain_schema('fundamental', 'metrics') is not None
    assert registry.get_domain_schema('technical', 'indicators') is not None

    # Test display schemas
    assert registry.get_display_schema('charts') is not None

def test_metric_registry_accessible():
    """Metric registry loads from DATA/metadata/"""
    registry = SchemaRegistry()
    metric_reg = registry.get_metric_registry()

    assert 'entity_types' in metric_reg
    assert len(metric_reg['entity_types']) == 4  # COMPANY, BANK, INSURANCE, SECURITY
```

### Phase 4.2: Performance Benchmarks

**File:** `config/tests/benchmark_schema_loading.py`

```python
import time
from config.schema_registry import SchemaRegistry

def benchmark_first_load():
    """Time first schema registry initialization"""
    start = time.time()
    registry = SchemaRegistry()
    end = time.time()

    print(f"First load: {(end - start) * 1000:.2f}ms")
    return registry

def benchmark_schema_access(registry):
    """Time schema retrieval (should be cached)"""
    schemas_to_test = [
        ('core', 'types'),
        ('domain/fundamental', 'metrics'),
        ('display', 'charts')
    ]

    for location, name in schemas_to_test:
        start = time.time()
        if '/' in location:
            domain = location.split('/')[1]
            registry.get_domain_schema(domain, name)
        else:
            registry.get_core_schema(name)
        end = time.time()

        print(f"{location}/{name}: {(end - start) * 1000:.2f}ms")

if __name__ == "__main__":
    print("Schema Loading Benchmarks")
    print("=" * 60)

    registry = benchmark_first_load()
    print("\nCached schema access:")
    benchmark_schema_access(registry)
```

---

## 5. ROLLOUT PLAN

### Week 1: Cleanup & Foundation
- **Day 1:** Phase 1 (Cleanup) - Delete unused files, remove duplicates
- **Day 2:** Phase 2.1-2.2 (New Schemas) - Create benchmarks & requirements schemas
- **Day 3:** Phase 2.3-2.4 (Complete Schemas) - Reconciliation & display schemas

### Week 2: Optimization & Documentation
- **Day 4:** Phase 3 (Data Sources) - Clarify precedence, update search order
- **Day 5:** Phase 4 (Performance) - Validation, version checking, optimization
- **Day 6:** Phase 5 (Documentation) - README files, update CLAUDE.md
- **Day 7:** Testing & validation, benchmark performance

---

## 6. SUCCESS METRICS

### Quantitative Metrics
- **Files removed:** 11 (unused/duplicate files)
- **Schemas completed:** 5 (benchmarks, requirements, reconciliation, tables, dashboards)
- **Documentation pages:** 6 (domain READMEs + DATA_SOURCES.md)
- **Test coverage:** 95%+ for schema loading
- **Load time:** < 50ms for schema registry initialization

### Qualitative Metrics
- ✅ Clear single source of truth documented
- ✅ No ambiguity about schema locations
- ✅ Complete fundamental metric schemas
- ✅ Comprehensive documentation
- ✅ All schemas versioned and validated

---

## 7. RISKS & MITIGATION

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Breaking existing imports** | HIGH | LOW | Thorough testing, keep legacy paths working |
| **Schema validation too strict** | MEDIUM | MEDIUM | Make validation warnings, not errors |
| **Performance regression** | MEDIUM | LOW | Benchmark before/after, optimize search |
| **Documentation drift** | LOW | MEDIUM | Automated doc generation from schemas |

---

## 8. APPENDIX

### A. Schema File Sizes

| File | Size | Lines | Complexity |
|------|------|-------|------------|
| master_schema.json | 8 KB | 233 | Medium |
| metric_registry.json | 770 KB | ~50,000 | High |
| fundamental/metrics.json | 5 KB | 126 | Low |
| fundamental/benchmarks.json | 6 KB | 150 | Medium |
| technical/indicators.json | 4 KB | 123 | Low |
| display/charts.json | 3 KB | 63 | Low |

### B. Import Audit Results

**Files using correct imports:** 15
**Files using deprecated imports:** 4
**Files to update after Phase 3:** 4

---

## 9. CONCLUSION

This plan transforms the config system from "working but cluttered" to "clean, documented, and optimized." The 5-phase approach ensures backward compatibility while establishing clear patterns for future schema additions.

**Key Benefits:**
1. **Clarity:** Single source of truth documented
2. **Performance:** Faster schema loading, better caching
3. **Completeness:** All missing schemas created
4. **Maintainability:** Clear documentation, validation, versioning
5. **Scalability:** Easy to add new schemas following established patterns

**Total Effort:** 5-7 days
**Priority:** HIGH - Blocks effective financial metric display
**Dependencies:** None - can start immediately

---

**Plan Status:** READY FOR REVIEW & APPROVAL
**Next Steps:** Review plan → Get approval → Begin Phase 1 cleanup
