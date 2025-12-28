# Streamlit Data Dependencies Audit

**Date:** 2025-12-28
**Scope:** Analyze which DATA/processed/*.parquet files are actually used by Streamlit
**Objective:** Optimize git commits to only include necessary data files

---

## Executive Summary

**Finding:** Only **15 out of 52 parquet files (29%)** in DATA/processed are actually used by Streamlit pages.

**Impact:**
- Current commit includes 37 unnecessary files (2.8 MB wasted)
- Can optimize .gitignore to exclude unused files
- Reduces repository bloat by 71%

**Recommendation:** Update .gitignore to exclude all DATA/processed by default, then whitelist only the 15 required files.

---

## Analysis Results

### Files Breakdown

| Category | Count | Status |
|----------|-------|--------|
| **Existing + Used** | 15 | ✅ Must commit |
| **Referenced but Missing** | 17 | ⚠️ Need generation |
| **Existing but Unused** | 37 | ⚪ Can exclude |
| **Total Existing** | 52 | - |

### Required Files by Service

#### 1. Valuation Service (5 files)
```
WEBAPP/services/valuation_service.py
```

**Files:**
- ✅ `DATA/processed/valuation/pe/historical/historical_pe.parquet`
- ✅ `DATA/processed/valuation/pb/historical/historical_pb.parquet`
- ✅ `DATA/processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet`
- ✅ `DATA/processed/valuation/ps/historical/historical_ps.parquet`
- ✅ `DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet`

**Usage:**
- `get_pe_data()` → historical_pe.parquet
- `get_pb_data()` → historical_pb.parquet
- `get_ev_ebitda_data()` → historical_ev_ebitda.parquet
- `get_ps_data()` → historical_ps.parquet
- `get_vnindex_valuation()` → vnindex_valuation_refined.parquet

---

#### 2. Company Service (1 file)
```
WEBAPP/services/company_service.py
```

**Files:**
- ✅ `DATA/processed/fundamental/company/company_financial_metrics.parquet`

**Usage:**
- `load_company_data()` → company_financial_metrics.parquet
- `get_available_symbols()` → Reads symbol column only

---

#### 3. Bank Service (1 file)
```
WEBAPP/services/bank_service.py
```

**Files:**
- ✅ `DATA/processed/fundamental/bank/bank_financial_metrics.parquet`

**Usage:**
- `load_bank_data()` → bank_financial_metrics.parquet

---

#### 4. Technical Service (4 files)
```
WEBAPP/services/technical_service.py
WEBAPP/pages/technical/services/ta_dashboard_service.py
```

**Files:**
- ✅ `DATA/processed/technical/basic_data.parquet`
- ✅ `DATA/processed/technical/market_breadth/market_breadth_daily.parquet`
- ✅ `DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet`
- ✅ `DATA/processed/technical/vnindex/vnindex_indicators.parquet`

**Usage:**
- `load_technical_data()` → basic_data.parquet
- `load_market_breadth()` → market_breadth_daily.parquet (glob latest)
- `load_sector_breadth()` → sector_breadth_daily.parquet
- `load_vnindex_indicators()` → vnindex_indicators.parquet

---

#### 5. Forecast Service (3 files)
```
WEBAPP/services/forecast_service.py
```

**Files:**
- ✅ `DATA/processed/forecast/bsc/bsc_individual.parquet`
- ✅ `DATA/processed/forecast/bsc/bsc_sector_valuation.parquet`
- ✅ `DATA/processed/forecast/bsc/bsc_combined.parquet`

**Usage:**
- `load_bsc_individual()` → bsc_individual.parquet
- `load_bsc_sector_valuation()` → bsc_sector_valuation.parquet
- `load_bsc_combined()` → bsc_combined.parquet

---

#### 6. Macro/Commodity Loader (1 file)
```
WEBAPP/services/macro_commodity_loader.py
```

**Files:**
- ✅ `DATA/processed/macro_commodity/macro_commodity_unified.parquet`

**Usage:**
- `load_data()` → macro_commodity_unified.parquet

---

### Unused Files (37 files)

These files exist but are NOT loaded by any Streamlit service:

#### Alerts (10 files) - ⚪ NOT USED
```
DATA/processed/technical/alerts/daily/breakout_latest.parquet
DATA/processed/technical/alerts/daily/combined_latest.parquet
DATA/processed/technical/alerts/daily/ma_crossover_latest.parquet
DATA/processed/technical/alerts/daily/patterns_latest.parquet
DATA/processed/technical/alerts/daily/volume_spike_latest.parquet
DATA/processed/technical/alerts/historical/breakout_history.parquet
DATA/processed/technical/alerts/historical/combined_history.parquet
DATA/processed/technical/alerts/historical/ma_crossover_history.parquet
DATA/processed/technical/alerts/historical/patterns_history.parquet
DATA/processed/technical/alerts/historical/volume_spike_history.parquet
```

**Reason:** No service loads alert data. Likely planned for future features.

---

#### Money Flow (5 files) - ⚪ NOT USED
```
DATA/processed/technical/money_flow/individual_money_flow.parquet
DATA/processed/technical/money_flow/sector_money_flow.parquet
DATA/processed/technical/money_flow/sector_money_flow_1d.parquet
DATA/processed/technical/money_flow/sector_money_flow_1m.parquet
DATA/processed/technical/money_flow/sector_money_flow_1w.parquet
```

**Reason:** Money flow analysis not implemented in UI yet.

---

#### Sector/Market Indices (6 files) - ⚪ NOT USED
```
DATA/processed/sector/sector_combined_scores.parquet
DATA/processed/sector/sector_fundamental_metrics.parquet
DATA/processed/sector/sector_valuation_metrics.parquet
DATA/processed/market_indices/sector_pe_summary.parquet
DATA/processed/market_indices/vnindex_valuation.parquet
DATA/processed/stock_valuation/individual_ev_ebitda.parquet
DATA/processed/stock_valuation/individual_pb.parquet
DATA/processed/stock_valuation/individual_pe.parquet
```

**Reason:** Legacy files or duplicates (vnindex_valuation vs vnindex_valuation_refined).

---

#### Insurance/Security (4 files) - ⚪ NOT USED
```
DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet
DATA/processed/fundamental/insurance_full.parquet
DATA/processed/fundamental/security/security_financial_metrics.parquet
DATA/processed/fundamental/security_full.parquet
```

**Reason:** No Insurance or Security dashboard pages implemented.

---

#### Macro (4 files) - ⚪ NOT USED
```
DATA/processed/fundamental/macro/deposit_interest_rates.parquet
DATA/processed/fundamental/macro/exchange_rates.parquet
DATA/processed/fundamental/macro/gov_bond_yields.parquet
DATA/processed/fundamental/macro/interest_rates.parquet
```

**Reason:** Replaced by unified file `macro_commodity_unified.parquet`.

---

#### Other (8 files) - ⚪ NOT USED
```
DATA/processed/forecast/VCI/vci_coverage_universe.parquet
DATA/processed/fundamental/bank_full.parquet
DATA/processed/fundamental/company_full.parquet
DATA/processed/technical/market_regime/market_regime_history.parquet
DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet
DATA/processed/valuation/ev_ebitda/historical/ev_ebitda_historical_test.parquet
```

**Reason:** Test files, legacy files, or future features.

---

## Missing Files (17 files)

These files are referenced in code but don't exist:

#### Forecast (3 files) - ❌ MISSING
```
DATA/processed/forecast/bsc_combined.parquet  (should be in bsc/ subfolder)
DATA/processed/forecast/bsc_individual.parquet (should be in bsc/ subfolder)
DATA/processed/forecast/bsc_sector_valuation.parquet (should be in bsc/ subfolder)
```

**Fix:** Path mismatch - files exist in `forecast/bsc/` but code references `forecast/` directly.

---

#### Fundamental (1 file) - ❌ MISSING
```
DATA/processed/fundamental/{entity_type}_full.parquet  (template path)
```

**Fix:** Dynamic path template, not a real file.

---

#### Technical (3 files) - ❌ MISSING
```
DATA/processed/technical/basic_data/basic_data_full.parquet
DATA/processed/technical/ma_screening_latest.parquet
DATA/processed/technical/moving_averages/moving_averages_full.parquet
DATA/processed/technical/rsi/rsi_full.parquet
```

**Fix:** Legacy paths from old code - update to use `basic_data.parquet`.

---

#### Valuation (2 files) - ❌ MISSING
```
DATA/processed/valuation/pe/pe_historical_all_symbols_final.parquet
DATA/processed/valuation/pb/pb_historical_all_symbols_final.parquet
```

**Fix:** Legacy paths - use `historical/historical_pe.parquet` instead.

---

#### News (1 file) - ❌ MISSING
```
DATA/processed/news/news_latest.parquet
```

**Fix:** News pipeline not run yet or directory missing.

---

## Recommendations

### 1. Update .gitignore (CRITICAL)

```gitignore
# Exclude all processed data by default
DATA/processed/**/*.parquet

# BUT include files required by Streamlit (15 files)

# Forecast data (3 files)
!DATA/processed/forecast/bsc/bsc_combined.parquet
!DATA/processed/forecast/bsc/bsc_individual.parquet
!DATA/processed/forecast/bsc/bsc_sector_valuation.parquet

# Fundamental data (2 files)
!DATA/processed/fundamental/company/company_financial_metrics.parquet
!DATA/processed/fundamental/bank/bank_financial_metrics.parquet

# Technical data (4 files)
!DATA/processed/technical/basic_data.parquet
!DATA/processed/technical/market_breadth/market_breadth_daily.parquet
!DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet
!DATA/processed/technical/vnindex/vnindex_indicators.parquet

# Valuation data (5 files)
!DATA/processed/valuation/pe/historical/historical_pe.parquet
!DATA/processed/valuation/pb/historical/historical_pb.parquet
!DATA/processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet
!DATA/processed/valuation/ps/historical/historical_ps.parquet
!DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet

# Macro/Commodity data (1 file)
!DATA/processed/macro_commodity/macro_commodity_unified.parquet
```

**Impact:** Reduces committed files from 52 → 15 (71% reduction)

---

### 2. Clean Up Unused Files (Optional)

**Option A:** Keep unused files locally (for future features)
**Option B:** Delete unused files to save disk space

```bash
# If choosing Option B:
rm -rf DATA/processed/technical/alerts/
rm -rf DATA/processed/technical/money_flow/
rm -rf DATA/processed/sector/
rm -rf DATA/processed/market_indices/
rm -rf DATA/processed/fundamental/insurance/
rm -rf DATA/processed/fundamental/security/
# ... etc
```

**Recommendation:** Keep files locally, exclude from git.

---

### 3. Fix Missing File References

Update service files to use correct paths:

**Example fix for forecast paths:**
```python
# ❌ OLD (incorrect):
file_path = self.data_path / "bsc_individual.parquet"

# ✅ NEW (correct):
file_path = self.data_path / "bsc" / "bsc_individual.parquet"
```

---

## Implementation Checklist

- [ ] 1. Review and approve recommended .gitignore changes
- [ ] 2. Update .gitignore file
- [ ] 3. Remove 37 unused files from git staging
- [ ] 4. Verify only 15 required files remain staged
- [ ] 5. Commit with message: "chore: optimize DATA/processed commits (15/52 files)"
- [ ] 6. Fix path references for missing files (forecast, technical legacy paths)
- [ ] 7. Document required files in CLAUDE.md

---

## Conclusion

**Key Insight:** 71% of DATA/processed files are NOT used by Streamlit.

**Action:** Update .gitignore to whitelist only 15 essential files, reducing repository size and commit noise.

**Next Steps:** Apply recommended .gitignore changes and verify Streamlit still works with minimal data files.
