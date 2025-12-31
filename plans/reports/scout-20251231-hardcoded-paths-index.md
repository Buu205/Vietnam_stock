# PROCESSORS Hardcoded Paths - Quick Reference Index

**Last Updated:** 2025-12-31  
**Scope:** All hardcoded path files in PROCESSORS directory  
**Total Files:** 40+ requiring attention

---

## Files Requiring Immediate Action (PRIORITY P0-P1)

### ⚠️ CRITICAL: Valuation Calculators (5 files)
All use pattern: `self.base_path / 'DATA' / 'processed' / ...`

1. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/valuation/calculators/historical_pe_calculator.py`
   - Lines: 16, 56, 119
   - Pattern: `self.base_path / 'DATA' / 'processed' / 'valuation' / 'pe' / 'historical'`

2. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/valuation/calculators/historical_pb_calculator.py`
   - Lines: 16, 52-53, 115
   - Pattern: `self.base_path / 'DATA' / 'processed' / 'valuation' / 'pb' / 'historical'`

3. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/valuation/calculators/historical_ps_calculator.py`
   - Lines: 24, 64-65, 118
   - Pattern: `self.base_path / 'DATA' / 'processed' / 'valuation' / 'ps' / 'historical'`

4. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/valuation/calculators/historical_ev_ebitda_calculator.py`
   - Lines: 17, 50-51, 103
   - Pattern: `self.base_path / 'DATA' / 'processed' / 'valuation' / 'ev_ebitda' / 'historical'`

5. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/valuation/calculators/vnindex_valuation_calculator.py`
   - Lines: 16, 48-49, 115, 231
   - Pattern: `self.base_path / 'DATA' / 'processed' / 'valuation' / 'vnindex'`

---

### 🔴 HIGH: String Hardcoded Paths (12 files)

#### Daily Pipeline Files
6. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/pipelines/daily/daily_ta_complete.py`
   - Line 51: `ohlcv_path: str = "DATA/raw/ohlcv/OHLCV_mktcap.parquet"`
   - Line 133: `output_dir = Path("DATA/processed/technical/alerts/daily")`
   - Line 149: `historical_dir = Path("DATA/processed/technical/alerts/historical")`
   - Line 167: `output_path = Path("DATA/processed/technical/market_breadth/market_breadth_daily.parquet")`

7. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/ohlcv/ohlcv_daily_updater.py`
   - Line 57: `output_path = str(Path(PROJECT_ROOT) / "DATA" / "raw" / "ohlcv" / "OHLCV_mktcap.parquet")`
   - Line 449: `default_output_path = str(RAW_OHLCV / "OHLCV_mktcap.parquet")`

8. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/pipelines/daily/daily_ohlcv_update.py`
   - Line 45: `output_path = project_root / "DATA" / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"`

#### Technical Indicators
9. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/sector_money_flow.py`
   - Line 346: `output_dir = Path("DATA/processed/technical/money_flow")`

10. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py`
    - Line 483: `marker_path = Path("DATA/.cache_invalidated")`

#### Decision/Scoring
11. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/decision/valuation_ta_decision.py`
    - Multiple `"DATA/processed/"` references - needs detailed review

12. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/fundamental/sector_fa_analyzer.py`
    - Multiple `"DATA/processed/"` references - needs detailed review

#### API/Monitoring
13. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/api/monitoring/health_checker.py`
    - Line 102, 164: `data_path = self.data_root / "processed" / "macro_commodity" / ...`

14. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/api/vietcap/fetch_vci_forecast.py`
    - Multiple `"DATA/processed/"` references - needs detailed review

---

## Files with Manual Path Construction (PRIORITY P2-P3)

### Sector Calculators
15. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/sector/calculators/base_aggregator.py`
    - Lines: 43, 46

16. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/sector/calculators/fa_aggregator.py`
    - Inherits from base_aggregator.py

### Shared Utilities
17. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/core/shared/consistency_checker.py`
    - Line 33: Legacy pattern - `data_warehouse_path`

18. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/core/shared/data_source_manager.py`
    - Line 36: Legacy pattern - `data_warehouse_path`

19. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/core/shared/symbol_loader.py`
    - Line 24: `PROJECT_ROOT = Path(__file__).resolve().parents[3]`

### Validators
20. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/core/validators/input_validator.py`
    - Line 350: Manual construction

21. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/core/validators/output_validator.py`
    - Line 415: Manual construction

22. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/core/validators/bsc_csv_adapter.py`
    - Line 290: Manual construction

### Sector Scoring
23. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/sector/scoring/ta_scorer.py`
    - Line 504: Manual construction

24. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/sector/scoring/fa_scorer.py`
    - Line 531: Manual construction

25. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/sector/scoring/signal_generator.py`
    - Line 459: Manual construction

26. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/sector/test_scoring.py`
    - Line 41: ⚠️ WRONG LEVEL - `parents[2]` instead of `parents[3]`

### Daily Pipeline/Run Scripts
27. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/pipelines/daily/daily_valuation.py`
    - Line 9: `PROJECT_ROOT = Path(__file__).resolve().parents[3]`
    - Line 124: `data_path = PROJECT_ROOT / "DATA" / "processed" / "valuation"`

28. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/pipelines/daily/daily_rs_rating.py`
    - Line 31: `PROJECT_ROOT = Path(__file__).resolve().parents[3]`

29. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/pipelines/daily/daily_sector_analysis.py`
    - Line 41: sys.path insertion

30. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/pipelines/run_all_daily_updates.py`
    - Uses string paths

31. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/fundamental/calculators/run_all_calculators.py`
    - Lines: 51, 64, 66

### Technical Indicators
32. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/alert_detector.py`
    - Multiple output_path constructions

33. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/market_regime.py`
    - Manual path construction

34. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/vnindex_analyzer.py`
    - Manual path construction

35. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/money_flow.py`
    - Manual path construction

36. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/sector_breadth.py`
    - Manual path construction

37. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/technical_processor.py`
    - Manual path construction

---

## Migration Patterns

### Pattern 1: String Path → Import
```python
# BEFORE
output_dir = Path("DATA/processed/technical/alerts/daily")

# AFTER
from PROCESSORS.core.config.paths import PROCESSED_TECHNICAL
output_dir = PROCESSED_TECHNICAL / "alerts" / "daily"
```

### Pattern 2: Manual Construction → Direct Import
```python
# BEFORE
self.base_path = PROJECT_ROOT
self.output_path = self.base_path / 'DATA' / 'processed' / 'valuation' / 'pe' / 'historical'

# AFTER
from PROCESSORS.core.config.paths import PROCESSED_VALUATION
self.output_path = PROCESSED_VALUATION / 'pe' / 'historical'
```

### Pattern 3: Legacy Parameter → Centralized Import
```python
# BEFORE
def __init__(self, data_warehouse_path: str = None):
    if data_warehouse_path is None:
        data_warehouse_path = Path(__file__).resolve().parents[3] / "DATA"

# AFTER
from PROCESSORS.core.config.paths import DATA_ROOT
def __init__(self):
    self.data_root = DATA_ROOT
```

---

## Available Constants in `PROCESSORS/core/config/paths.py`

```python
# Root paths
PROJECT_ROOT          # /Users/buuphan/Dev/Vietnam_dashboard
DATA_ROOT            # /Users/buuphan/Dev/Vietnam_dashboard/DATA

# Raw data paths
RAW_DATA             # /Users/buuphan/Dev/Vietnam_dashboard/DATA/raw
RAW_OHLCV            # /Users/buuphan/Dev/Vietnam_dashboard/DATA/raw/ohlcv
RAW_FUNDAMENTAL      # /Users/buuphan/Dev/Vietnam_dashboard/DATA/raw/fundamental/csv
RAW_COMMODITY        # /Users/buuphan/Dev/Vietnam_dashboard/DATA/raw/commodity
RAW_MACRO            # /Users/buuphan/Dev/Vietnam_dashboard/DATA/raw/macro

# Processed data paths
PROCESSED_DATA       # /Users/buuphan/Dev/Vietnam_dashboard/DATA/processed
PROCESSED_FUNDAMENTAL # /Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/fundamental
PROCESSED_TECHNICAL  # /Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/technical
PROCESSED_VALUATION  # /Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/valuation

# Metadata paths
METADATA             # /Users/buuphan/Dev/Vietnam_dashboard/DATA/metadata
METRIC_REGISTRY      # /Users/buuphan/Dev/Vietnam_dashboard/DATA/metadata/metric_registry.json
SECTOR_REGISTRY      # /Users/buuphan/Dev/Vietnam_dashboard/DATA/metadata/sector_industry_registry.json

# Helper function
get_fundamental_path(entity_type: str) -> Path
```

---

## Proposed `get_data_path()` Function

Add to `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/core/config/paths.py`:

```python
def get_data_path(
    data_type: str,        # "raw" or "processed"
    category: str,         # "ohlcv", "fundamental", "technical", "valuation", "commodity", "macro", "forecast"
    subcategory: str = None,  # "pe", "pb", "ps", "ev_ebitda", "alerts", "daily", "sector", etc.
    filename: str = None   # optional final filename
) -> Path:
    """
    Centralized path resolution for all data files.
    
    Args:
        data_type: "raw" or "processed"
        category: Major data category
        subcategory: Optional subcategory for more specific paths
        filename: Optional filename at the end
    
    Returns:
        Path object to the requested location
    
    Examples:
        >>> get_data_path("raw", "ohlcv")
        Path(...)/DATA/raw/ohlcv
        
        >>> get_data_path("processed", "valuation", "pe")
        Path(...)/DATA/processed/valuation/pe
        
        >>> get_data_path("processed", "technical", "alerts", "daily")
        Path(...)/DATA/processed/technical/alerts/daily
        
        >>> get_data_path("processed", "valuation", "pe", "historical", "pe_historical.parquet")
        Path(...)/DATA/processed/valuation/pe/historical/pe_historical.parquet
    """
    # Implementation to follow
    ...
```

---

## Validation Checklist

When migrating files, verify:

- [ ] All imports use absolute paths from `PROCESSORS.core.config.paths`
- [ ] No remaining `Path("DATA/...")` strings
- [ ] No remaining `Path(__file__).resolve().parents[n]` patterns
- [ ] All tests pass
- [ ] No regression in existing functionality
- [ ] Paths resolve to correct location (verify with print debug)

---

## File Status Summary

| Priority | Count | Examples |
|----------|-------|----------|
| P0 (Critical) | 5 | Valuation calculators |
| P1 (High) | 12 | Daily pipelines, Technical |
| P2 (Medium) | 15 | Sector analysis, Shared utils |
| P3 (Low) | 8+ | Other indicators, validators |
| ✅ Compliant | 8+ | Already use imports |

---

## Quick Navigation

**Centralized Path Config:**
- File: `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/core/config/paths.py`
- Status: ✅ Exists and well-organized
- Needs: `get_data_path()` function implementation

**Full Audit Report:**
- File: `/Users/buuphan/Dev/Vietnam_dashboard/plans/reports/scout-20251231-hardcoded-paths-audit.md`
- Status: ✅ Complete
- Contains: Detailed findings, recommendations, next steps

---

**Generated:** 2025-12-31  
**Status:** Ready for implementation sprint
