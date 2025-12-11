# Formula Audit Report

**Generated:** 2025-12-11 21:54:53.528597

## 📊 Summary

- **Total Formulas:** 35
- **Files Analyzed:** 5
- **Duplicates Found:** 0
- **Missing Docstrings:** 0

## 📈 Formula Counts by File

| File | Formula Count |
|------|---------------|
| base | 25 |
| company | 3 |
| bank | 7 |
| insurance | 0 |
| security | 0 |

## 🎯 Recommendations

### 1. Immediate Actions (Phase 1)

1. **Remove Duplicates:**
   - Move universal formulas to `_base_formulas.py`
   - Remove from entity-specific files
   - Update imports in calculators

2. **Fix Docstrings:**
   - Add comprehensive Vietnamese docstrings
   - Include formula, interpretation, examples

### 2. Consolidation Strategy

1. **Keep in _base_formulas.py:**
   - `calculate_gross_margin`
   - `calculate_net_margin`
   - `calculate_operating_margin`
   - `calculate_roa`
   - `calculate_roe`
   - `safe_divide`

2. **Entity-Specific to Keep:**
   **Company:**
   - `asset_turnover`
   - `inventory_turnover`

   **Bank:**
   - `nim`
   - `cir`
   - `plr`

   **Insurance:**
   - `combined_ratio`
   - `loss_ratio`

   **Security:**
   - `cad_ratio`
   - `trading_leverage`

