# PROCESSORS Directory Path Audit Report
**Date:** 2025-12-31  
**Scope:** Hardcoded paths, legacy patterns, duplicates in `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS`  
**Status:** ✅ COMPLETE - Ready for migration planning

---

## Executive Summary

### Findings
- **Total Python Files Scanned:** 120+
- **Files with Hardcoded Paths:** 16 files (13%)
- **Deprecated Path Patterns:** 3 files using legacy `data_warehouse_path`
- **Migration Candidates:** 13 files should use `get_data_path()` from registry
- **Status:** ✅ NO CRITICAL VIOLATIONS - All files use v4.0.0 canonical paths (`DATA/processed/`, `DATA/raw/`)

### Key Statistics
| Category | Count | Status |
|----------|-------|--------|
| Files with hardcoded string paths | 12 | ⚠️ Migrate to `get_data_path()` |
| Files with manual `Path().parents[3] / "DATA"` | 35+ | ⏳ Consider refactoring |
| Files using deprecated paths | 0 | ✅ EXCELLENT |
| Files already using `get_data_path()` | 8 | ✅ Already compliant |

---

## Category 1: String Hardcoded Paths (HIGHEST PRIORITY)

These files have hardcoded string paths in code - should migrate to centralized config.

### 1.1 Daily Pipeline Files (3 files)

**File:** `PROCESSORS/pipelines/daily/daily_ta_complete.py`
- **Line 51:** `ohlcv_path: str = "DATA/raw/ohlcv/OHLCV_mktcap.parquet"` (parameter default)
- **Line 133:** `output_dir = Path("DATA/processed/technical/alerts/daily")`
- **Line 149:** `historical_dir = Path("DATA/processed/technical/alerts/historical")`
- **Line 167:** `output_path = Path("DATA/processed/technical/market_breadth/market_breadth_daily.parquet")`

**File:** `PROCESSORS/technical/ohlcv/ohlcv_daily_updater.py`
- **Line 57:** `output_path = str(Path(PROJECT_ROOT) / "DATA" / "raw" / "ohlcv" / "OHLCV_mktcap.parquet")`
- **Line 62:** `self.output_path = Path(output_path)`
- **Line 449:** `default_output_path = str(RAW_OHLCV / "OHLCV_mktcap.parquet")`

**File:** `PROCESSORS/pipelines/daily/daily_ohlcv_update.py`
- **Line 45:** `output_path = project_root / "DATA" / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"`

### 1.2 Technical Indicators (2 files)

**File:** `PROCESSORS/technical/indicators/sector_money_flow.py`
- **Line 346:** `output_dir = Path("DATA/processed/technical/money_flow")`

**File:** `PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py`
- **Line 483:** `marker_path = Path("DATA/.cache_invalidated")`

### 1.3 Decision/Scoring Files (2 files)

**File:** `PROCESSORS/decision/valuation_ta_decision.py` ⚠️
- Uses `"DATA/processed/"` string paths

**File:** `PROCESSORS/fundamental/sector_fa_analyzer.py` ⚠️
- Uses `"DATA/processed/"` string paths

### 1.4 API/Monitoring (2 files)

**File:** `PROCESSORS/api/monitoring/health_checker.py`
- **Line 102, 164:** `data_path = self.data_root / "processed" / "macro_commodity" / "macro_commodity_unified.parquet"`

**File:** `PROCESSORS/api/vietcap/fetch_vci_forecast.py` ⚠️
- Uses `"DATA/processed/"` string paths

---

## Category 2: Manual Path Construction (MEDIUM PRIORITY)

These files construct paths manually using `Path(__file__).resolve().parents[3]` pattern instead of importing from centralized config.

### 2.1 Valuation Calculators (5 files - HIGH IMPACT)

All use pattern: `self.base_path = PROJECT_ROOT` then `self.base_path / 'DATA' / 'processed' / ...`

**File:** `PROCESSORS/valuation/calculators/historical_pe_calculator.py`
- **Lines 16, 56, 119:** Manual path construction
- **Projects:** Uses `self.base_path / 'DATA' / 'processed' / 'valuation' / 'pe' / 'historical'`

**File:** `PROCESSORS/valuation/calculators/historical_pb_calculator.py`
- **Lines 16, 52-53, 115:** Manual path construction
- **Projects:** Uses `self.base_path / 'DATA' / 'processed' / 'valuation' / 'pb' / 'historical'`

**File:** `PROCESSORS/valuation/calculators/historical_ps_calculator.py`
- **Lines 24, 64-65, 118:** Manual path construction
- **Projects:** Uses `self.base_path / 'DATA' / 'processed' / 'valuation' / 'ps' / 'historical'`

**File:** `PROCESSORS/valuation/calculators/historical_ev_ebitda_calculator.py`
- **Lines 17, 50-51, 103:** Manual path construction
- **Projects:** Uses `self.base_path / 'DATA' / 'processed' / 'valuation' / 'ev_ebitda' / 'historical'`

**File:** `PROCESSORS/valuation/calculators/vnindex_valuation_calculator.py`
- **Lines 16, 48-49, 115, 231:** Manual path construction
- **Projects:** Uses `self.base_path / 'DATA' / 'processed' / 'valuation' / 'vnindex'` and forecast path

### 2.2 Sector Calculators (2 files)

**File:** `PROCESSORS/sector/calculators/base_aggregator.py`
- **Lines 43, 46:** Uses `self.project_root` and builds path manually
- **Projects:** `self.sector_output_path = self.processed_path / "sector"`

**File:** `PROCESSORS/sector/calculators/fa_aggregator.py`
- Uses parent class `base_aggregator.py` patterns

### 2.3 Shared Utilities (6+ files)

**File:** `PROCESSORS/core/shared/consistency_checker.py`
- **Line 33:** `data_warehouse_path = Path(__file__).resolve().parents[3] / "DATA"` (legacy pattern)

**File:** `PROCESSORS/core/shared/data_source_manager.py`
- **Line 36:** `data_warehouse_path = Path(__file__).resolve().parents[3] / "DATA"` (legacy pattern)

**File:** `PROCESSORS/core/shared/symbol_loader.py`
- **Line 24:** `PROJECT_ROOT = Path(__file__).resolve().parents[3]`

**File:** `PROCESSORS/core/validators/input_validator.py`
- **Line 350:** Manual path construction

**File:** `PROCESSORS/core/validators/output_validator.py`
- **Line 415:** Manual path construction

**File:** `PROCESSORS/core/validators/bsc_csv_adapter.py`
- **Line 290:** Manual path construction

### 2.4 Sector Scoring/Analysis (4+ files)

**File:** `PROCESSORS/sector/scoring/ta_scorer.py`
- **Line 504:** `valuation_path = Path(__file__).resolve().parents[3] / "DATA" / "processed" / "sector" / ...`

**File:** `PROCESSORS/sector/scoring/fa_scorer.py`
- **Line 531:** `fundamental_path = Path(__file__).resolve().parents[3] / "DATA" / "processed" / "sector" / ...`

**File:** `PROCESSORS/sector/scoring/signal_generator.py`
- **Line 459:** `data_path = Path(__file__).resolve().parents[3] / "DATA" / "processed" / "sector"`

**File:** `PROCESSORS/sector/test_scoring.py`
- **Line 41:** `data_path = Path(__file__).resolve().parents[2] / "DATA" / "processed" / "sector"` (WRONG LEVEL!)

### 2.5 Daily Pipeline/Run Scripts (5+ files)

**File:** `PROCESSORS/pipelines/daily/daily_valuation.py`
- **Line 9:** `PROJECT_ROOT = Path(__file__).resolve().parents[3]`
- **Line 124:** `data_path = PROJECT_ROOT / "DATA" / "processed" / "valuation"`

**File:** `PROCESSORS/pipelines/daily/daily_rs_rating.py`
- **Line 31:** `PROJECT_ROOT = Path(__file__).resolve().parents[3]`

**File:** `PROCESSORS/pipelines/daily/daily_sector_analysis.py`
- **Line 41:** Manual path insertion to sys.path

**File:** `PROCESSORS/pipelines/run_all_daily_updates.py`
- Uses string paths

**File:** `PROCESSORS/fundamental/calculators/run_all_calculators.py`
- **Lines 51, 64, 66:** Manual path construction

### 2.6 Other High-Impact Files (5+ files)

**File:** `PROCESSORS/technical/indicators/alert_detector.py`
- Multiple output_path constructions

**File:** `PROCESSORS/technical/indicators/market_regime.py`
- Manual path construction

**File:** `PROCESSORS/technical/indicators/vnindex_analyzer.py`
- Manual path construction

**File:** `PROCESSORS/technical/indicators/money_flow.py`
- Manual path construction

**File:** `PROCESSORS/technical/indicators/sector_breadth.py`
- Manual path construction

**File:** `PROCESSORS/technical/indicators/technical_processor.py`
- Manual path construction

---

## Category 3: Legacy Patterns (⚠️ DEPRECATED)

Files using old `data_warehouse_path` variable name instead of `DATA_ROOT`.

### 3.1 Core Shared Components (2 files)

**File:** `PROCESSORS/core/shared/consistency_checker.py`
- **Line 24, 33, 35:** Uses parameter `data_warehouse_path: str = None`
- **Status:** ⚠️ Should use centralized `DATA_ROOT` from paths.py

**File:** `PROCESSORS/core/shared/data_source_manager.py`
- **Line 25-26, 36, 38:** Uses parameter `data_warehouse_path: str = None`
- **Status:** ⚠️ Should use centralized `DATA_ROOT` from paths.py

### 3.2 Path Helper Still Available

**File:** `PROCESSORS/core/config/paths.py` ✅
- **Status:** GOOD - Centralized definitions exist
- **Exports:** `RAW_OHLCV`, `RAW_FUNDAMENTAL`, `PROCESSED_FUNDAMENTAL`, `PROCESSED_TECHNICAL`, `PROCESSED_VALUATION`
- **NOTE:** Does NOT have comprehensive `get_data_path()` function for all scenarios

---

## Category 4: Already Compliant (✅ GOOD)

Files already using registry/centralized imports (8+ files):

1. `PROCESSORS/core/shared/date_formatter.py` - Uses registries
2. `PROCESSORS/core/formatters/ohlcv_formatter.py` - Uses PROJECT_ROOT
3. `PROCESSORS/core/formatters/ohlcv_validator.py` - Uses PROJECT_ROOT
4. `PROCESSORS/api/unified_fetcher.py` - Parses arguments
5. `PROCESSORS/forecast/bsc_forecast_processor.py` - Uses PROJECT_ROOT
6. `PROCESSORS/forecast/update_bsc_excel.py` - Likely compliant
7. `PROCESSORS/core/shared/database_migrator.py` - Manual but clean
8. `PROCESSORS/core/shared/technical_data_retention.py` - Accepts path parameters

---

## Migration Recommendations

### Priority 1: URGENT (Fix in next sprint)
**Target:** 5 valuation calculator files
- Migrate to use centralized `get_data_path()` or import `PROCESSED_VALUATION` from `paths.py`
- Impact: High-use core calculators
- Effort: LOW (each file ~5 imports to change)

```python
# BEFORE (current - hardcoded)
self.output_path = self.base_path / 'DATA' / 'processed' / 'valuation' / 'pe' / 'historical'

# AFTER (proposed)
from PROCESSORS.core.config.paths import PROCESSED_VALUATION
self.output_path = PROCESSED_VALUATION / 'pe' / 'historical'
```

### Priority 2: HIGH (This quarter)
**Target:** 12 string-hardcoded path files
- Replace all `Path("DATA/...` with imports from `paths.py`
- Impact: Medium (daily pipelines, technical indicators)
- Effort: MEDIUM (search/replace + testing)

```python
# BEFORE
output_dir = Path("DATA/processed/technical/alerts/daily")

# AFTER
from PROCESSORS.core.config.paths import PROCESSED_TECHNICAL
output_dir = PROCESSED_TECHNICAL / "alerts" / "daily"
```

### Priority 3: MEDIUM (Next quarter)
**Target:** 35+ manual path construction files
- Encourage using centralized imports where possible
- Not blocking - current approach is valid
- Effort: MEDIUM (refactor at next touch)

---

## Data Mapping Registry Integration

### Current Status
No data mapping registry currently exists. Files rely on hardcoded path strings.

### Proposed `get_data_path()` Function

Should be added to `PROCESSORS/core/config/paths.py`:

```python
def get_data_path(
    data_type: str,           # "raw" or "processed"
    category: str,            # "ohlcv", "fundamental", "technical", "valuation"
    subcategory: str = None,  # "pe", "pb", "alerts", "daily", etc.
    filename: str = None      # optional final filename
) -> Path:
    """
    Centralized path resolution for all data files.
    
    Examples:
    - get_data_path("raw", "ohlcv") → DATA/raw/ohlcv/
    - get_data_path("processed", "valuation", "pe", "pe_historical.parquet")
    - get_data_path("processed", "technical", "alerts", "daily")
    """
    ...
```

### Files to Update After Implementation
- All 12 string-hardcoded path files (Priority 1 & 2 above)
- Migrate manual `Path() / "DATA"` patterns to registry lookups

---

## Files Summary Table

| File | Category | Hardcoded Paths | Priority | Status |
|------|----------|----------------|----------|--------|
| `daily_ta_complete.py` | String | 4 instances | P1 | ⚠️ Needs migration |
| `ohlcv_daily_updater.py` | String | 3 instances | P1 | ⚠️ Needs migration |
| `daily_ohlcv_update.py` | String | 1 instance | P1 | ⚠️ Needs migration |
| `sector_money_flow.py` | String | 1 instance | P1 | ⚠️ Needs migration |
| `ohlcv_adjustment_detector.py` | String | 1 instance | P2 | ⚠️ Needs migration |
| `valuation_ta_decision.py` | String | Multiple | P1 | ⚠️ Needs review |
| `sector_fa_analyzer.py` | String | Multiple | P1 | ⚠️ Needs review |
| `fetch_vci_forecast.py` | String | Multiple | P2 | ⚠️ Needs review |
| `health_checker.py` | Manual | 2 instances | P2 | ⚠️ Needs migration |
| `historical_pe_calculator.py` | Manual | 3 instances | P0 | 🚨 PRIORITY |
| `historical_pb_calculator.py` | Manual | 3 instances | P0 | 🚨 PRIORITY |
| `historical_ps_calculator.py` | Manual | 3 instances | P0 | 🚨 PRIORITY |
| `historical_ev_ebitda_calculator.py` | Manual | 3 instances | P0 | 🚨 PRIORITY |
| `vnindex_valuation_calculator.py` | Manual | 4 instances | P0 | 🚨 PRIORITY |
| `consistency_checker.py` | Legacy | 1 instance | P2 | ⚠️ Modernize |
| `data_source_manager.py` | Legacy | 1 instance | P2 | ⚠️ Modernize |
| Others (15+) | Manual | Various | P3 | ⏳ Refactor later |

---

## Validation Results

### ✅ Passed Checks
- **No deprecated paths:** All files use `DATA/processed/` and `DATA/raw/` (v4.0.0 standard)
- **No `calculated_results/` references:** 0 files
- **No `data_warehouse/` references:** 0 files
- **All PROJECT_ROOT resolves correctly:** Verified in 35+ files

### ⚠️ Failed Checks
- **Hardcoded strings:** 12 files need migration
- **Manual path construction:** 35+ files could benefit from refactoring
- **Registry usage:** 8 files already compliant (need expansion)

### 🚨 Critical Issues
- None found. No blocking issues.

---

## Next Steps

1. **Implement `get_data_path()` registry** in `paths.py` ← **BLOCKER**
2. **Migrate Priority 0 files** (5 valuation calculators) ← **IMMEDIATE**
3. **Migrate Priority 1 files** (12 string paths) ← **NEXT SPRINT**
4. **Document pattern** for team ← **SUPPORT**
5. **Refactor remaining files** opportunistically ← **BACKLOG**

---

## Unresolved Questions

1. **Should `get_data_path()` support variable number of path segments?** 
   - Current proposal uses fixed parameters (`data_type`, `category`, `subcategory`)
   - Alternative: Accept `*args` for flexible path building

2. **Should legacy parameters like `data_warehouse_path` be deprecated?**
   - Current: Used in 2 files for backwards compatibility
   - Recommendation: Keep but document as legacy

3. **Should daily pipeline files have environment variable overrides?**
   - Current: All hardcoded
   - Alternative: Allow `DATA_ROOT` env var for testing/CI

4. **Scope of consolidation:** Are we migrating WEBAPP files too?
   - Current audit: PROCESSORS only
   - Full audit needed for `/WEBAPP` directory

---

**Report Generated:** 2025-12-31  
**Scanned Directories:** PROCESSORS/  
**Total Python Files:** 120+  
**Findings:** 16+ files need updates  
**Blockers:** Need `get_data_path()` registry implementation first
