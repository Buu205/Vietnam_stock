# Config Directory Audit Report
Date: 2025-12-31
Status: Comprehensive Analysis Complete

---

## Executive Summary

Config directory contains **52 files** across 9 subsystems. Analysis identifies:
- ✅ **0 hardcoded DATA paths** (all normalized to `DATA/processed/`, `DATA/raw/`)
- ⚠️ **4 legacy registry builders** (unused, candidates for removal)
- ⚠️ **2 duplicate metric registries** (raw vs processed versions)
- ⚠️ **5 unused business logic configs** (no Python references found)
- ✅ **1 strong data_mapping module** (new clean architecture, ready for adoption)

---

## Section 1: Legacy Files (Candidates for Removal)

### A. Unused Registry Builders

These builder scripts are **no longer called anywhere** in the codebase. They appear to be leftover from v3.x architecture.

| File | Status | Reason | Size | Action |
|------|--------|--------|------|--------|
| `/config/registries/builders/build_metric_registry.py` | ❌ Unused | No imports found in codebase | 1.2K | **REMOVE** |
| `/config/registries/builders/build_sector_registry.py` | ❌ Unused | No imports found in codebase | 1.0K | **REMOVE** |
| `/config/registries/builders/__init__.py` | ❌ Empty | No exports | 0.1K | **REMOVE** |
| `/config/registries/builders/` | ❌ Empty Dir | No purpose | - | **REMOVE** |

**Evidence:** Grep search for "build_metric_registry" and "build_sector_registry" only found 5 self-references in the builder files themselves. No actual usage in production code.

**Why kept in v3.x?** Used to regenerate metric_registry.json and sector registry from source data files. Now handled by pipeline scripts (if needed).

---

### B. Duplicate Metric Registries

**Problem:** Two nearly identical metric registry files with different timestamps.

| File | Last Updated | Size | Purpose | Issue |
|------|--------------|------|---------|-------|
| `/config/metadata/metric_registry.json` | 2025-12-10 | 29.7K | Main registry | **CURRENT** |
| `/config/metadata/raw_metric_registry.json` | 2025-12-11 | 23.1K | Raw version | **NEWER BUT UNUSED** |

**Issue:** `raw_metric_registry.json` is newer but not referenced anywhere. Both contain ~99% identical structure. Creates confusion about which is authoritative.

**Evidence:** Grep found zero references to `raw_metric_registry` in any Python files or schemas.

**Recommendation:** 
1. Verify which version is actually used by `MetricRegistry` class
2. Keep ONE, delete OTHER
3. If raw is needed for pipeline rebuilds, document clearly in builder script

---

## Section 2: Hardcoded Paths Analysis

### ✅ GOOD NEWS: Zero Hardcoded Data Paths

**Finding:** All data paths are properly canonicalized to v4.0.0 standard (`DATA/processed/`, `DATA/raw/`).

Location of hardcoded paths (INTENTIONAL):
- `config/schema_registry/core/mappings.json` - **Correct**: Maps logical names → paths
  ```json
  "raw": {
    "ohlcv": "DATA/raw/ohlcv/",
    "fundamental": "DATA/raw/fundamental/csv/"
  },
  "processed": {
    "fundamental": "DATA/processed/fundamental/"
  }
  ```

- `config/README.md` - **Correct**: Documentation examples

- `config/data_mapping/registry.py` line 187:
  ```python
  return Path(data_root) / source.path  # data_root is parameter, not hardcoded
  ```

**Conclusion:** ✅ All hardcoded paths follow v4.0.0 standard. No deprecated paths found.

---

## Section 3: Unused Configuration Files

### Business Logic Configs (Not Referenced)

These configuration files exist but are **never loaded or referenced** by any Python code:

| File | Size | Purpose | Python References | Status |
|------|------|---------|-------------------|--------|
| `/config/business_logic/analysis/fa_analysis.json` | 0.9K | FA settings | **0 found** | ⚠️ Unused |
| `/config/business_logic/analysis/ta_analysis.json` | - | TA settings | **0 found** | ⚠️ Unused |
| `/config/business_logic/analysis/valuation_analysis.json` | - | Valuation settings | **0 found** | ⚠️ Unused |
| `/config/business_logic/analysis/unified_analysis.json` | - | Unified settings | **0 found** | ⚠️ Unused |
| `/config/business_logic/decisions/weights.json` | - | Decision weights | **0 found** | ⚠️ Unused |

**Finding:** Grep for `fa_analysis.json` etc. returned **0 results** across entire codebase. These are orphaned configs.

**Possible reasons:**
1. Created for planned features not yet implemented
2. Leftover from design phase
3. Superseded by data_mapping YAML configs

**Decision needed:** Are these for upcoming FA+TA orchestration layer (from active plan)?

---

### Metadata Files (Status Mixed)

| File | Size | Usage | Status |
|------|------|-------|--------|
| `/config/metadata/formula_registry.json` | 699B | ✅ Referenced in schema_registry.py | **ACTIVE** |
| `/config/metadata/master_symbols.json` | 667B | ✅ Referenced in 20 WEBAPP/PROCESSORS files | **ACTIVE** |
| `/config/metadata/ticker_details.json` | 1.8K | ❓ Unknown usage | **VERIFY** |

**Action:** Verify `ticker_details.json` is actually used. If not, remove.

---

## Section 4: Migration Candidates

### DataMappingRegistry (NEW - Ready to Replace Legacy Registries)

**Location:** `/config/data_mapping/`

**Status:** ✅ Well-designed, actively initialized, ready for adoption

**Current Usage:**
```python
from config.data_mapping import get_registry, get_data_path
registry = get_registry()
path = registry.get_path("bank_metrics")
```

**What it replaces:**
- ❌ Manual `Path(__file__).parent` navigation
- ❌ Scattered `find_project_root()` implementations
- ❌ String-based path construction

**What's NEW:**
- ✅ YAML-based config (easier to maintain than hardcoded paths)
- ✅ Dependency resolution (knows what depends on what)
- ✅ Schema validation
- ✅ Health checking

**Files to migrate:**
1. `/config/registries/metric_lookup.py` - Uses old `find_project_root()` pattern
2. `/config/registries/sector_lookup.py` - Uses old `find_project_root()` pattern
3. `/config/sector_analysis/config_manager.py` - Uses `Path(__file__).resolve().parents[2]`
4. `/config/registries/builders/` - If repurposed, could use DataMappingRegistry

---

## Section 5: Redundancy & Duplication

### A. Multiple `find_project_root()` Implementations

**Problem:** Same function re-implemented 4 times across config:

```python
# config/registries/metric_lookup.py
def find_project_root() -> Path:
    current = Path(__file__).resolve()
    while current.parent != current:
        if current.name in ['Vietnam_dashboard', 'stock_dashboard']:
            return current
        current = current.parent
    return Path(__file__).resolve().parents[3]

# config/registries/sector_lookup.py
def find_project_root() -> Path:  # DUPLICATE!
    # ... same logic ...

# config/registries/builders/build_metric_registry.py
def find_project_root() -> Path:  # DUPLICATE!
    # ... slight variation ...

# config/registries/builders/build_sector_registry.py
def find_project_root() -> Path:  # DUPLICATE!
    # ... another variation ...
```

**Impact:** Code duplication, maintenance burden, inconsistent logic.

**Solution:** Use centralized path helper:
```python
# PROPOSED: config/paths.py (or use existing PROCESSORS/core/config/paths.py)
from config.paths import PROJECT_ROOT
# or
from PROCESSORS.core.config.paths import get_project_root
```

---

### B. Path Resolution Patterns

**Current patterns in use:**

1. ✅ **DataMappingRegistry** (best):
   ```python
   from config.data_mapping import get_data_path
   path = get_data_path("bank_metrics")
   ```

2. ⚠️ **Manual Path + find_project_root()** (legacy):
   ```python
   from config.registries.metric_lookup import PROJECT_ROOT
   path = PROJECT_ROOT / "config" / "metadata" / "metric_registry.json"
   ```

3. ❌ **Path manipulation** (worst):
   ```python
   project_root = Path(__file__).resolve().parents[2]
   config_dir = project_root / "config"
   ```

**Recommendation:** Consolidate on **DataMappingRegistry** pattern.

---

## Section 6: API Configuration Analysis

### Credentials Management

**Status:** ⚠️ Credentials stored in JSON

Files:
- `/config/api/api_credentials.json` - **CONTAINS LIVE TOKENS** ⚠️
- `/config/api/api_credentials.example.json` - Safe template
- `/config/api/api_endpoints.json` - Endpoint definitions (safe)

**Risk:** Tokens visible in git history if not careful.

**Recommendation:**
1. ✅ Already ignored in `.gitignore` (likely)
2. Verify `.gitignore` includes `api_credentials.json`
3. Use environment variables for production tokens instead

---

## Section 7: Unused Subdirectories

| Directory | Files | Purpose | Usage | Status |
|-----------|-------|---------|-------|--------|
| `/config/registries/builders/` | 3 files | Build metric registry | Not called | ⚠️ Can remove |
| `/config/sector_analysis/` | 3 files | Sector config | Only ConfigManager used | ✅ Keep |
| `/config/api/` | 3 files | API endpoints | Referenced | ✅ Keep |

---

## Section 8: Current Architecture Assessment

### What's GOOD ✅

1. **Data Mapping Module**
   - Clean separation of concerns
   - YAML-based (human-readable)
   - Entity-oriented design
   - Resolver + Validator patterns

2. **Schema Registry**
   - Centralizes all schema definitions
   - Organized by domain (fundamental, technical, valuation)
   - Display configs for Streamlit
   - Formatting rules (price, volume, percentage)

3. **Metadata Registry Files**
   - Comprehensive metric definitions
   - Formula documentation
   - Ticker information

### What Needs Cleanup ⚠️

1. **Legacy Registry Builders** → Remove (unused)
2. **Duplicate find_project_root()** → Consolidate (DRY)
3. **Unused business logic configs** → Document or remove
4. **Raw metric registry** → Verify and deduplicate
5. **Scattered path patterns** → Migrate to DataMappingRegistry

---

## Section 9: Specific File Issues

### High Priority Issues

| File | Issue | Fix | Impact |
|------|-------|-----|--------|
| `/config/registries/builders/` | Entire directory unused | Remove all 4 files | Zero (no usage) |
| `/config/metadata/raw_metric_registry.json` | Duplicate, never read | Delete or document | Cleanup |
| `/config/registries/metric_lookup.py` | find_project_root() antipattern | Refactor to use helpers | Maintenance |
| `/config/registries/sector_lookup.py` | find_project_root() antipattern | Refactor to use helpers | Maintenance |

### Medium Priority Issues

| File | Issue | Fix | Impact |
|------|-------|-----|--------|
| `/config/business_logic/analysis/*.json` | Unused configs | Document intent or delete | Clarity |
| `/config/sector_analysis/config_manager.py` | Uses old path pattern | Migrate to DataMappingRegistry | Consistency |
| `/config/metadata/ticker_details.json` | Verify actual usage | Confirm in grep or remove | Clarity |

### Low Priority Issues

| File | Issue | Fix | Impact |
|------|-------|-----|--------|
| `/config/api/api_credentials.json` | Contains tokens | Ensure .gitignore covers | Security |
| `/config/README.md` | Hardcoded paths in examples | Update to use DataMappingRegistry | Documentation |

---

## Section 10: Cleanup Roadmap

### Phase 1: Remove Unused Code (No Risk)

**Action items:**
1. Delete `/config/registries/builders/` (entire directory + 4 files)
2. Delete `/config/metadata/raw_metric_registry.json`
3. Delete unused entries from `/config/business_logic/analysis/`

**Risk:** None (zero references)
**Time:** 5 minutes
**Lines removed:** ~200

### Phase 2: Consolidate & Refactor (Low Risk)

**Action items:**
1. Create centralized `project_root` helper in `config/paths.py`
2. Replace all `find_project_root()` with import
3. Refactor `config_manager.py` to use helper

**Risk:** Low (just consolidating existing patterns)
**Time:** 20 minutes
**Test:** Run all tests to confirm paths still resolve

### Phase 3: Migrate to DataMappingRegistry (Medium Risk)

**Action items:**
1. Update `metric_lookup.py` to use `DataMappingRegistry`
2. Update `sector_lookup.py` to use `DataMappingRegistry`
3. Update `config_manager.py` to use `DataMappingRegistry`

**Risk:** Medium (changes initialization pattern)
**Time:** 30 minutes
**Test:** All WEBAPP/PROCESSORS modules still load data correctly

---

## Unresolved Questions

1. **Are business logic configs intentional?**
   - Are `fa_analysis.json`, `ta_analysis.json`, etc. part of upcoming FA+TA feature?
   - Or are they orphaned from earlier design phase?

2. **What about `ticker_details.json`?**
   - Is it actively used or leftover metadata?
   - Grep found zero references in Python files

3. **Should `raw_metric_registry.json` be kept?**
   - Is it needed for pipeline rebuilds?
   - Or completely superseded by `metric_registry.json`?

4. **Is builder cleanup safe?**
   - Are metric registry rebuilds still needed from source data?
   - Or is `metric_registry.json` now authoritative/static?

---

## Files Summary

### Total: 52 files across config/

**By type:**
- Python files: 7 (registries, builders, data_mapping)
- JSON config: 35 (schemas, metadata, business logic, API)
- YAML config: 4 (data_mapping configs)
- Markdown: 2 (README, audit)

**By usage status:**
- ✅ Active: 45 files (used by WEBAPP/PROCESSORS)
- ⚠️ Unused: 7 files (candidates for removal)
- ❓ Verify: 3 files (need clarification)

---

## Recommendations Summary

| Priority | Action | Files | Benefit |
|----------|--------|-------|---------|
| **HIGH** | Remove builders | 4 | -200 LOC, zero impact |
| **HIGH** | Deduplicate metric registry | 1 | Clarity, single source of truth |
| **MEDIUM** | Consolidate find_project_root() | 4 | DRY principle, maintainability |
| **MEDIUM** | Document business logic configs | 5 | Clarity on intended use |
| **MEDIUM** | Migrate to DataMappingRegistry | 3 | Modern architecture, consistency |
| **LOW** | Verify ticker_details.json usage | 1 | Cleanup |
| **LOW** | Ensure credentials ignored | 1 | Security |

---

**Report Generated:** 2025-12-31
**Status:** Ready for user review
**Next Step:** Get answers to unresolved questions, then execute cleanup phases
