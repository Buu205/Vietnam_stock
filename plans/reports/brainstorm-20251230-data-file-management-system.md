# Brainstorm: Data File Management System

**Date:** 2025-12-30
**Status:** PROPOSED
**Author:** Claude (Brainstormer)

---

## Problem Statement

### Current Pain Points
1. **Manual gitignore maintenance** - Each new feature requires remembering to add files to exceptions
2. **No single source of truth** - 52 parquet files, scattered across directories, no clear categorization
3. **Deployment failures** - Streamlit Cloud missing files because they weren't tracked
4. **Cognitive overhead** - Developer must remember which files are needed where

### Current State
| Metric | Value |
|--------|-------|
| Total parquet files | 52 |
| Git tracked | 31 |
| Gitignore exceptions | 36 |
| Projected growth | +20-30 files |

### Root Cause
No systematic way to:
- Define which files Streamlit needs
- Auto-generate gitignore from source of truth
- Validate data completeness before deployment

---

## Requirements

1. **Full automation** - No manual gitignore updates
2. **Refactor-ready** - Can change imports across WEBAPP
3. **Scalable** - Support 70-100+ files in future
4. **Clear categorization**:
   - `STREAMLIT_REQUIRED` - Tracked in git, deployed to Streamlit Cloud
   - `PIPELINE_ONLY` - Large intermediate files, gitignored
   - `RAW_LOCAL` - Source data, never committed

---

## Evaluated Approaches

### Approach 1: Manifest File (KISS)
Simple text file listing required files.

| Pros | Cons |
|------|------|
| Easy to implement | Manual updates still required |
| Human readable | Can drift from actual code |
| Quick win | No type safety |

**Verdict:** ❌ Doesn't solve automation requirement

---

### Approach 2: Code Scanning (Auto-Discovery)
Script parses WEBAPP code to find all parquet references.

| Pros | Cons |
|------|------|
| Always in sync | Complex regex/AST parsing |
| Zero manual work | May miss dynamic paths |
| | Slow on each commit |
| | False positives from comments |

**Verdict:** ⚠️ Risky - dynamic paths in services are hard to detect

---

### Approach 3: Data Registry (DRY) ⭐ RECOMMENDED

Centralized Python module defining ALL data paths with metadata.

| Pros | Cons |
|------|------|
| Single source of truth | Refactor effort required |
| Type-safe, IDE support | All imports must change |
| Can generate gitignore | Initial setup time |
| Supports metadata | |
| Validation scripts | |

**Verdict:** ✅ Best for long-term scalability

---

## Recommended Solution: Data Registry + Auto-Validation

### Architecture Overview

```
config/
├── data_registry.py      # Single source of truth for ALL data paths
├── data_paths.py         # Generated constants (optional, for IDE autocomplete)
└── validate_data.py      # Pre-commit validation script

scripts/
└── generate_gitignore.py # Auto-generate gitignore from registry
```

### Data Registry Design

```python
# config/data_registry.py
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

class DataCategory(Enum):
    """Data file categories for gitignore management"""
    STREAMLIT_REQUIRED = "streamlit"  # Tracked in git, deployed
    PIPELINE_ONLY = "pipeline"        # Gitignored, intermediate results
    RAW_LOCAL = "raw"                 # Never committed, source data

@dataclass
class DataFile:
    """Metadata for a data file"""
    path: str                         # Relative path from project root
    category: DataCategory            # Determines git tracking
    description: str                  # What this file contains
    size_mb: Optional[float] = None   # Approximate size for planning
    update_frequency: str = "daily"   # daily, weekly, on-demand

    @property
    def full_path(self) -> Path:
        return Path(self.path)

    @property
    def is_tracked(self) -> bool:
        return self.category == DataCategory.STREAMLIT_REQUIRED

class DataRegistry:
    """Central registry for all data files"""

    # =========================================================================
    # TECHNICAL - Basic
    # =========================================================================
    BASIC_DATA = DataFile(
        path="DATA/processed/technical/basic_data.parquet",
        category=DataCategory.STREAMLIT_REQUIRED,
        description="Daily OHLCV with indicators for all tickers",
        size_mb=18.6,
        update_frequency="daily"
    )

    # =========================================================================
    # TECHNICAL - Alerts Daily
    # =========================================================================
    PATTERNS_LATEST = DataFile(
        path="DATA/processed/technical/alerts/daily/patterns_latest.parquet",
        category=DataCategory.STREAMLIT_REQUIRED,
        description="Today's candlestick patterns",
        size_mb=0.01
    )

    MA_CROSSOVER_LATEST = DataFile(
        path="DATA/processed/technical/alerts/daily/ma_crossover_latest.parquet",
        category=DataCategory.STREAMLIT_REQUIRED,
        description="Today's MA crossover signals",
        size_mb=0.01
    )

    # ... (continue for all files)

    # =========================================================================
    # FUNDAMENTAL - Full (Pipeline Only)
    # =========================================================================
    COMPANY_FULL = DataFile(
        path="DATA/processed/fundamental/company_full.parquet",
        category=DataCategory.PIPELINE_ONLY,
        description="Full company financials - used for calculations",
        size_mb=50.0
    )

    # =========================================================================
    # RAW DATA (Local Only)
    # =========================================================================
    OHLCV_RAW = DataFile(
        path="DATA/raw/ohlcv/OHLCV_mktcap.parquet",
        category=DataCategory.RAW_LOCAL,
        description="Raw OHLCV from vnstock API"
    )

    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    @classmethod
    def get_all(cls) -> list[DataFile]:
        """Return all registered data files"""
        return [v for k, v in vars(cls).items()
                if isinstance(v, DataFile)]

    @classmethod
    def get_streamlit_required(cls) -> list[DataFile]:
        """Return files needed by Streamlit"""
        return [f for f in cls.get_all()
                if f.category == DataCategory.STREAMLIT_REQUIRED]

    @classmethod
    def get_gitignore_exceptions(cls) -> list[str]:
        """Generate gitignore exception lines"""
        return [f"!{f.path}" for f in cls.get_streamlit_required()]

    @classmethod
    def validate_all_exist(cls) -> tuple[list[str], list[str]]:
        """Check which files exist/missing"""
        existing, missing = [], []
        for f in cls.get_streamlit_required():
            if f.full_path.exists():
                existing.append(f.path)
            else:
                missing.append(f.path)
        return existing, missing

    @classmethod
    def get_total_size_mb(cls) -> float:
        """Calculate total size of tracked files"""
        return sum(f.size_mb or 0 for f in cls.get_streamlit_required())
```

### Usage in WEBAPP

```python
# BEFORE (scattered paths)
basic_path = Path("DATA/processed/technical/basic_data.parquet")

# AFTER (centralized)
from config.data_registry import DataRegistry as DR

basic_path = DR.BASIC_DATA.full_path
```

### Auto-Generate Gitignore Script

```python
# scripts/generate_gitignore.py
"""
Generate gitignore DATA section from DataRegistry.
Run: python scripts/generate_gitignore.py
"""
from config.data_registry import DataRegistry

def generate_gitignore_section() -> str:
    lines = [
        "# ===========================================",
        "# DATA FILES (Auto-generated from DataRegistry)",
        "# ===========================================",
        "",
        "# Ignore all processed data by default",
        "DATA/processed/**/*.parquet",
        "DATA/processed/**/*.csv",
        "",
        "# EXCEPTIONS: Streamlit Required Files",
        f"# Total: {len(DataRegistry.get_streamlit_required())} files",
        f"# Size: ~{DataRegistry.get_total_size_mb():.1f} MB",
        "",
    ]

    # Group by category for readability
    files = DataRegistry.get_streamlit_required()
    current_category = None

    for f in sorted(files, key=lambda x: x.path):
        category = f.path.split('/')[2]  # e.g., "technical", "valuation"
        if category != current_category:
            lines.append(f"\n# {category.title()}")
            current_category = category
        lines.append(f"!{f.path}")

    return "\n".join(lines)

if __name__ == "__main__":
    print(generate_gitignore_section())
```

### Pre-Commit Validation Script

```python
# config/validate_data.py
"""
Validate all Streamlit-required files exist before commit.
Can be used as pre-commit hook.
"""
from config.data_registry import DataRegistry

def validate():
    existing, missing = DataRegistry.validate_all_exist()

    if missing:
        print("❌ MISSING STREAMLIT DATA FILES:")
        for path in missing:
            print(f"   - {path}")
        print(f"\nTotal: {len(missing)} missing, {len(existing)} OK")
        return False

    print(f"✅ All {len(existing)} Streamlit data files exist")
    return True

if __name__ == "__main__":
    import sys
    sys.exit(0 if validate() else 1)
```

---

## Naming Convention (Optional Enhancement)

While DataRegistry is the source of truth, consistent naming helps visual scanning:

| Pattern | Category | Example |
|---------|----------|---------|
| `*_daily.parquet` | STREAMLIT_REQUIRED | `market_breadth_daily.parquet` |
| `*_latest.parquet` | STREAMLIT_REQUIRED | `patterns_latest.parquet` |
| `*_history.parquet` | STREAMLIT_REQUIRED | `patterns_history.parquet` |
| `*_full.parquet` | PIPELINE_ONLY | `company_full.parquet` |
| `*_raw.parquet` | RAW_LOCAL | `ohlcv_raw.parquet` |

**Note:** Naming convention is supplementary. DataRegistry remains authoritative.

---

## Implementation Plan

### Phase 1: Create Data Registry (Day 1)
1. Create `config/data_registry.py` with all 52 current files
2. Add metadata (category, description, size)
3. Implement helper methods

### Phase 2: Create Tooling (Day 1)
1. Create `scripts/generate_gitignore.py`
2. Create `config/validate_data.py`
3. Test both scripts

### Phase 3: Refactor WEBAPP Imports (Day 2-3)
1. Search all `.py` files for hardcoded paths
2. Replace with `DataRegistry.FILE_NAME.full_path`
3. Run tests to verify

### Phase 4: Refactor PROCESSORS Imports (Day 3-4)
1. Update calculators to use registry
2. Update pipelines to use registry
3. Run full pipeline to verify

### Phase 5: Documentation & CI (Day 5)
1. Update CLAUDE.md with new pattern
2. Add pre-commit hook for validation
3. Document in README

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Large refactor breaks code | High | Incremental migration, comprehensive testing |
| Missing files in registry | Medium | Validation script catches before deploy |
| Registry becomes outdated | Low | CI validation enforces completeness |
| Performance overhead | Low | Registry is simple dict lookup |

---

## Success Metrics

1. **Zero manual gitignore updates** - All changes via registry
2. **Zero missing file deployments** - Validation catches all
3. **< 5 min to add new file** - Just add to registry
4. **100% path coverage** - All WEBAPP paths use registry

---

## Next Steps

1. [ ] Review this plan
2. [ ] Approve approach
3. [ ] Create implementation plan with detailed tasks
4. [ ] Execute Phase 1-5

---

## Unresolved Questions

1. **Migration strategy:** Big bang refactor or incremental?
2. **Backward compatibility:** Keep old paths working during transition?
3. **CI integration:** GitHub Actions or local pre-commit only?
4. **Size limits:** Should we enforce max file size in registry?

---

## Appendix A: Complete Data File Inventory

**Generated:** 2025-12-30
**Total Files:** 57
**Git Tracked:** 35
**Gitignored:** 22

---

### 1. STREAMLIT_REQUIRED (Git Tracked, Deployed)

| # | File Path | Size (MB) | Notes |
|---|-----------|-----------|-------|
| 1 | `DATA/processed/forecast/bsc/bsc_combined.parquet` | 0.04 | BSC forecasts |
| 2 | `DATA/processed/forecast/bsc/bsc_individual.parquet` | 0.04 | BSC forecasts |
| 3 | `DATA/processed/forecast/bsc/bsc_sector_valuation.parquet` | 0.02 | Valuation charts |
| 4 | `DATA/processed/fundamental/bank/bank_financial_metrics.parquet` | 0.44 | Financial metrics |
| 5 | `DATA/processed/fundamental/company/company_financial_metrics.parquet` | 16.72 | Financial metrics |
| 6 | `DATA/processed/fundamental/security/security_financial_metrics.parquet` | 0.43 | Financial metrics |
| 7 | `DATA/processed/macro_commodity/macro_commodity_unified.parquet` | 0.39 | Macro/Commodity data |
| 8 | `DATA/processed/sector/sector_combined_scores.parquet` | 0.05 | Sector analysis |
| 9 | `DATA/processed/sector/sector_fundamental_metrics.parquet` | 0.13 | Financial metrics |
| 10 | `DATA/processed/sector/sector_valuation_metrics.parquet` | 7.21 | Valuation charts |
| 11 | `DATA/processed/technical/alerts/daily/breakout_latest.parquet` | 0.01 | Stock scanner signals |
| 12 | `DATA/processed/technical/alerts/daily/ma_crossover_latest.parquet` | 0.01 | Stock scanner signals |
| 13 | `DATA/processed/technical/alerts/daily/patterns_latest.parquet` | 0.01 | Stock scanner signals |
| 14 | `DATA/processed/technical/alerts/daily/volume_spike_latest.parquet` | 0.01 | Stock scanner signals |
| 15 | `DATA/processed/technical/alerts/historical/breakout_history.parquet` | 0.01 | Stock scanner signals |
| 16 | `DATA/processed/technical/alerts/historical/ma_crossover_history.parquet` | 0.02 | Stock scanner signals |
| 17 | `DATA/processed/technical/alerts/historical/patterns_history.parquet` | 0.04 | Stock scanner signals |
| 18 | `DATA/processed/technical/alerts/historical/volume_spike_history.parquet` | 0.04 | Stock scanner signals |
| 19 | `DATA/processed/technical/basic_data.parquet` | 18.62 | Main technical data |
| 20 | `DATA/processed/technical/market_breadth/market_breadth_daily.parquet` | 0.02 | Market breadth |
| 21 | `DATA/processed/technical/money_flow/sector_money_flow_1d.parquet` | 0.01 | Sector analysis |
| 22 | `DATA/processed/technical/money_flow/sector_money_flow_1m.parquet` | 0.01 | Sector analysis |
| 23 | `DATA/processed/technical/money_flow/sector_money_flow_1w.parquet` | 0.01 | Sector analysis |
| 24 | `DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet` | 1.33 | RS Rating heatmap |
| 25 | `DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet` | 0.06 | Sector analysis |
| 26 | `DATA/processed/technical/vnindex/vnindex_indicators.parquet` | 0.14 | VN-Index indicators |
| 27 | `DATA/processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet` | 12.14 | Valuation charts |
| 28 | `DATA/processed/valuation/pb/historical/historical_pb.parquet` | 10.77 | Valuation charts |
| 29 | `DATA/processed/valuation/pe/historical/historical_pe.parquet` | 10.08 | Valuation charts |
| 30 | `DATA/processed/valuation/ps/historical/historical_ps.parquet` | 12.28 | Valuation charts |
| 31 | `DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet` | 0.19 | Valuation charts |

**Subtotal:** 91.25 MB (31 files)

---

### 2. PIPELINE_ONLY (Gitignored, Local Processing)

| # | File Path | Size (MB) | Notes |
|---|-----------|-----------|-------|
| 1 | `DATA/processed/forecast/VCI/vci_coverage_universe.parquet` | 0.03 | VCI coverage data |
| 2 | `DATA/processed/fundamental/bank_full.parquet` | 3.31 | Full financial data for calculations |
| 3 | `DATA/processed/fundamental/company_full.parquet` | 85.73 | Full financial data for calculations |
| 4 | `DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet` | 0.09 | ⚠️ **NEED TO ADD** |
| 5 | `DATA/processed/fundamental/insurance_full.parquet` | 1.19 | Full financial data for calculations |
| 6 | `DATA/processed/fundamental/macro/deposit_interest_rates.parquet` | 0.02 | ⚠️ **NEED TO ADD** |
| 7 | `DATA/processed/fundamental/macro/exchange_rates.parquet` | 0.03 | ⚠️ **NEED TO ADD** |
| 8 | `DATA/processed/fundamental/macro/gov_bond_yields.parquet` | 0.02 | ⚠️ **NEED TO ADD** |
| 9 | `DATA/processed/fundamental/macro/interest_rates.parquet` | 0.02 | ⚠️ **NEED TO ADD** |
| 10 | `DATA/processed/fundamental/security_full.parquet` | 7.82 | Full financial data for calculations |
| 11 | `DATA/processed/market_indices/sector_pe_summary.parquet` | 0.90 | Deprecated |
| 12 | `DATA/processed/market_indices/vnindex_valuation.parquet` | 0.19 | Deprecated |
| 13 | `DATA/processed/stock_valuation/individual_ev_ebitda.parquet` | 12.08 | Per-stock valuation (generated) |
| 14 | `DATA/processed/stock_valuation/individual_pb.parquet` | 10.48 | Per-stock valuation (generated) |
| 15 | `DATA/processed/stock_valuation/individual_pe.parquet` | 9.78 | Per-stock valuation (generated) |
| 16 | `DATA/processed/technical/alerts/daily/combined_latest.parquet` | 0.01 | Combined alerts (generated) |
| 17 | `DATA/processed/technical/alerts/historical/combined_history.parquet` | 0.05 | Combined alerts (generated) |
| 18 | `DATA/processed/technical/market_regime/market_regime_history.parquet` | 0.01 | Market regime detection |
| 19 | `DATA/processed/technical/money_flow/individual_money_flow.parquet` | 6.59 | Per-stock money flow |
| 20 | `DATA/processed/technical/money_flow/sector_money_flow.parquet` | 0.01 | Deprecated - use 1d/1w/1m |
| 21 | `DATA/processed/valuation/ev_ebitda/historical/ev_ebitda_historical_test.parquet` | 0.16 | Test file |

**Subtotal:** 138.53 MB (21 files)

---

### 3. RAW_LOCAL (Source Data, Never Deploy)

| # | File Path | Size (MB) | Notes |
|---|-----------|-----------|-------|
| 1 | `DATA/raw/news/news_raw_20251127_102844.parquet` | 0.01 | ⚠️ Should NOT be tracked |
| 2 | `DATA/raw/news/news_raw_20251127_103110.parquet` | 0.07 | ⚠️ Should NOT be tracked |
| 3 | `DATA/raw/news/news_raw_20251127_103804.parquet` | 0.18 | ⚠️ Should NOT be tracked |
| 4 | `DATA/raw/news/news_raw_20251128_074622.parquet` | 0.17 | ⚠️ Should NOT be tracked |
| 5 | `DATA/raw/ohlcv/OHLCV_mktcap.parquet` | 28.19 | Raw OHLCV from vnstock API |

**Subtotal:** 28.61 MB (5 files)

---

## Appendix B: Issues Detected

### B.1 WEBAPP References but GITIGNORED (Deployment Risk)

| File | Issue | Recommendation |
|------|-------|----------------|
| `insurance/insurance_financial_metrics.parquet` | Used by Insurance Analysis page | **ADD to tracked** |
| `fundamental/macro/deposit_interest_rates.parquet` | Used by FX & Commodities page | **ADD to tracked** |
| `fundamental/macro/exchange_rates.parquet` | Used by FX & Commodities page | **ADD to tracked** |
| `fundamental/macro/gov_bond_yields.parquet` | Used by FX & Commodities page | **ADD to tracked** |
| `fundamental/macro/interest_rates.parquet` | Used by FX & Commodities page | **ADD to tracked** |
| `company_full.parquet` | Too large (86MB) | Keep gitignored, use metrics file |

### B.2 Tracked but UNUSED? (Cleanup Candidates)

| File | Status | Recommendation |
|------|--------|----------------|
| `DATA/raw/news/*.parquet` | Tracked but no WEBAPP usage | **REMOVE from git** |
| `money_flow_1d/1w/1m.parquet` | No direct references found | Verify Sector Rotation usage |

---

## Appendix C: Summary Statistics

| Category | Files | Size (MB) | Status |
|----------|-------|-----------|--------|
| STREAMLIT_REQUIRED | 31 | 91.25 | ✅ Deployed |
| PIPELINE_ONLY | 21 | 138.53 | ✅ Gitignored |
| RAW_LOCAL | 5 | 28.61 | ⚠️ Some tracked incorrectly |
| **TOTAL** | **57** | **258.39** | |

---

## Appendix D: Immediate Action Items

### D.1 ADD to gitignore exceptions (5 files, ~0.18 MB)
```
!DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet
!DATA/processed/fundamental/macro/deposit_interest_rates.parquet
!DATA/processed/fundamental/macro/exchange_rates.parquet
!DATA/processed/fundamental/macro/gov_bond_yields.parquet
!DATA/processed/fundamental/macro/interest_rates.parquet
```

### D.2 REMOVE from git tracking (4 files)
```bash
git rm --cached DATA/raw/news/*.parquet
```

### D.3 VERIFY usage before removing
- `sector_money_flow_1d.parquet`
- `sector_money_flow_1w.parquet`
- `sector_money_flow_1m.parquet`
