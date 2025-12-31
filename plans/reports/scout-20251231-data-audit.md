# Data Registry Audit Report
**Date:** 2025-12-31 | **Scope:** DATA directory structure vs data_mapping registry

---

## Executive Summary

**Critical Finding:** Registry is **26% complete** - only 14 of 54 actual data files are registered.

| Metric | Count | Status |
|--------|-------|--------|
| Total actual files | 54 | ✓ Inventory complete |
| Registered files | 14 | ⚠️ 26% coverage |
| Orphaned files | 40 | ⚠️ 74% unregistered |
| Empty directories | 1 | ✓ No legacy folders |
| Duplicate data patterns | 3 major sets | ⚠️ Requires review |

---

## PART 1: ORPHANED FILES (NOT IN REGISTRY)

40 files exist but are NOT registered in `config/data_mapping/configs/data_sources.yaml`

### Group A: Fundamental "Full" Files (4 files)
These appear to be complete/unfiltered versions of entity data.

```
DATA/processed/fundamental/bank_full.parquet
DATA/processed/fundamental/company_full.parquet
DATA/processed/fundamental/insurance_full.parquet
DATA/processed/fundamental/security_full.parquet
```

**Status:** Should be registered? Or redundant?
- Purpose: Unclear if these are working copies vs. filtered metrics versions
- Compare with: `bank_financial_metrics.parquet` (registered)
- **Recommendation:** Audit contents to determine if needed; consider consolidation

---

### Group B: Macro/Economic Data (4 files)
Detailed macro indicators not in main registry.

```
DATA/processed/fundamental/macro/deposit_interest_rates.parquet
DATA/processed/fundamental/macro/exchange_rates.parquet
DATA/processed/fundamental/macro/gov_bond_yields.parquet
DATA/processed/fundamental/macro/interest_rates.parquet
```

**Status:** ⚠️ Should be registered
- These are important economic indicators
- Only `macro_commodity_unified.parquet` is registered
- **Recommendation:** Register these 4 as separate sources OR consolidate into one

---

### Group C: Sector Fundamental Metrics (1 file)
```
DATA/processed/sector/sector_fundamental_metrics.parquet
```

**Status:** ⚠️ Should be registered
- Complements registered `sector_valuation_metrics.parquet`
- **Recommendation:** Register immediately

---

### Group D: Stock Valuation (Individual Multiples) (3 files)
Individual PE/PB/EV-EBITDA by ticker (not sector-level).

```
DATA/processed/stock_valuation/individual_pe.parquet
DATA/processed/stock_valuation/individual_pb.parquet
DATA/processed/stock_valuation/individual_ev_ebitda.parquet
```

**Status:** ⚠️ Potential duplicates vs. `historical_pe.parquet` etc.
- Compare with: `DATA/processed/valuation/pe/historical/`
- **Recommendation:** Clarify difference; consolidate if redundant

---

### Group E: Technical Alerts (10 files)
Stock scanner alerts for breakouts, patterns, volume spikes, MA crossovers.

```
DAILY snapshots:
  DATA/processed/technical/alerts/daily/breakout_latest.parquet
  DATA/processed/technical/alerts/daily/combined_latest.parquet
  DATA/processed/technical/alerts/daily/ma_crossover_latest.parquet
  DATA/processed/technical/alerts/daily/patterns_latest.parquet
  DATA/processed/technical/alerts/daily/volume_spike_latest.parquet

HISTORICAL records:
  DATA/processed/technical/alerts/historical/breakout_history.parquet
  DATA/processed/technical/alerts/historical/combined_history.parquet
  DATA/processed/technical/alerts/historical/ma_crossover_history.parquet
  DATA/processed/technical/alerts/historical/patterns_history.parquet
  DATA/processed/technical/alerts/historical/volume_spike_history.parquet
```

**Status:** ⚠️ Not registered - used by stock scanner
- Used in: `WEBAPP/pages/stock_scanner/` (likely)
- **Recommendation:** Register as group OR consolidate into 2 sources (daily/historical)

---

### Group F: Money Flow Analysis (5 files)
Individual & sector money flow metrics at different timeframes.

```
DATA/processed/technical/money_flow/individual_money_flow.parquet
DATA/processed/technical/money_flow/sector_money_flow.parquet
DATA/processed/technical/money_flow/sector_money_flow_1d.parquet
DATA/processed/technical/money_flow/sector_money_flow_1m.parquet
DATA/processed/technical/money_flow/sector_money_flow_1w.parquet
```

**Status:** ⚠️ Not registered
- Likely used by technical dashboard & money flow analyzers
- **Recommendation:** Register as `money_flow_individual`, `money_flow_sector_*`

---

### Group G: Other Technical Indicators (5 files)
Market regime, breadth, RS rating, and VN-Index indicators.

```
DATA/processed/technical/market_regime/market_regime_history.parquet
DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet
DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet
DATA/processed/technical/vnindex/vnindex_indicators.parquet
DATA/processed/forecast/VCI/vci_coverage_universe.parquet
```

**Status:** ⚠️ Not registered - potentially valuable signals
- **Recommendation:** Register these 5 sources

---

### Group H: Valuation Test & Variants (3 files)
```
DATA/processed/valuation/ev_ebitda/historical/ev_ebitda_historical_test.parquet
DATA/processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet
DATA/processed/valuation/ps/historical/historical_ps.parquet
```

**Status:** ⚠️ Test file should be removed; PS should be registered
- `ev_ebitda_historical_test.parquet` - **ORPHANED TEST DATA**
- `historical_ps.parquet` - P/S ratio (valuation metric) not registered
- **Recommendation:** Remove test file; register PS ratio

---

### Group I: BSC Forecast Variants (1 file)
```
DATA/processed/forecast/bsc/bsc_combined.parquet
```

**Status:** ⚠️ Should be registered OR removed
- Registered: `bsc_individual.parquet`, `bsc_sector_valuation.parquet`
- **Recommendation:** Clarify if `bsc_combined` is needed; if yes, register it

---

### Group J: News Raw Data (4 files)
Multiple snapshots of raw news data.

```
DATA/raw/news/news_raw_20251127_102844.parquet
DATA/raw/news/news_raw_20251127_103110.parquet
DATA/raw/news/news_raw_20251127_103804.parquet
DATA/raw/news/news_raw_20251128_074622.parquet
```

**Status:** ⚠️ Snapshot data - should consolidate
- 4 separate daily runs - indicates pipeline collecting historical snapshots
- **Recommendation:** Create versioned registry entry OR keep only latest

---

## PART 2: SUMMARY BY CATEGORY

| Category | Registered | Orphaned | Total | % Coverage |
|----------|-----------|----------|-------|-----------|
| **Fundamental** | 4 | 5 | 9 | 44% |
| **Valuation** | 4 | 4 | 8 | 50% |
| **Technical** | 2 | 22 | 24 | 8% |
| **Forecast** | 2 | 2 | 4 | 50% |
| **Macro** | 1 | 5 | 6 | 17% |
| **Sector** | 1 | 1 | 2 | 50% |
| **TOTAL** | **14** | **40** | **54** | **26%** |

**Key Insight:** Technical analysis is severely underregistered (8% coverage).

---

## PART 3: LEGACY/EMPTY DIRECTORIES

### Empty Directory Found:
```
DATA/processed/market_indices/
```

**Status:** ✓ No files - can be removed OR reserved for future use
- **Recommendation:** Remove if not planned for future data

---

## PART 4: POTENTIAL DUPLICATES & DATA CONSOLIDATION

### Duplicate Set #1: Individual PE Ratios
```
Registered:     DATA/processed/valuation/pe/historical/historical_pe.parquet
Orphaned:       DATA/processed/stock_valuation/individual_pe.parquet
```
- **Issue:** Both contain PE data by ticker - verify columns/differences
- **Size comparison:** Need to audit to determine if consolidation possible

---

### Duplicate Set #2: Individual PB Ratios
```
Registered:     DATA/processed/valuation/pb/historical/historical_pb.parquet
Orphaned:       DATA/processed/stock_valuation/individual_pb.parquet
```
- **Issue:** Both contain PB data - need clarification
- **Recommendation:** Audit schema & consolidate if identical

---

### Duplicate Set #3: "Full" vs. "Metrics" Entity Data
```
Registered:     DATA/processed/fundamental/company/company_financial_metrics.parquet
Orphaned:       DATA/processed/fundamental/company_full.parquet
```
Same pattern for bank, insurance, security. 
- **Question:** Are "*_full.parquet" unfiltered versions? Or legacy?
- **Recommendation:** Clarify intent; consolidate or remove

---

## PART 5: DIRECTORY STRUCTURE ANALYSIS

### Size Distribution (Ranked):
```
116M  fundamental/      ← Most data (entity metrics + full copies)
46M   valuation/        ← Historical PE/PB/PS multiples
32M   stock_valuation/  ← Individual stock multiples (orphaned)
27M   technical/        ← Mostly orphaned (alerts, money flow, etc.)
7.3M  sector/           ← Underutilized
400K  macro_commodity/  ← Small but growing
312K  forecast/         ← Small
0B    market_indices/   ← Empty (legacy?)
```

**Finding:** Largest directories (fundamental, valuation, technical) have most orphaned data.

---

## PART 6: ACTION ITEMS

### CRITICAL (Must Register/Remove):
- [ ] **PS Ratio:** Register `historical_ps.parquet` as `ps_historical`
- [ ] **Sector Fundamentals:** Register `sector_fundamental_metrics.parquet`
- [ ] **Macro Data:** Register 4 macro indicators OR consolidate them
- [ ] **Remove Test File:** Delete `ev_ebitda_historical_test.parquet`

### HIGH PRIORITY (Complete Registry):
- [ ] **Technical Alerts:** Register 10 alert files (or consolidate)
- [ ] **Money Flow:** Register 5 money flow files
- [ ] **Market Regime/Breadth:** Register 3 market indicator files
- [ ] **VCI Coverage:** Register forecast VCI data

### MEDIUM PRIORITY (Audit Duplicates):
- [ ] **Individual Multiples:** Compare `stock_valuation/individual_*` vs `valuation/*/historical/`
- [ ] **"Full" Copies:** Clarify purpose of `*_full.parquet` files
- [ ] **BSC Variants:** Clarify need for `bsc_combined.parquet`

### LOW PRIORITY (Cleanup):
- [ ] **News Snapshots:** Consolidate 4 dated news files
- [ ] **Empty Directory:** Remove `market_indices/` if not planned
- [ ] **Documentation:** Add comments to data directory READMEs

---

## PART 7: RECOMMENDATIONS

### Immediate Actions (Today):
1. **Add 10 missing registrations** to `data_sources.yaml`:
   - PS ratio, Sector fundamentals, 4 macro, 3 technical, 1 VCI = 11 sources
   
2. **Delete orphaned test file**:
   - `DATA/processed/valuation/ev_ebitda/historical/ev_ebitda_historical_test.parquet`

3. **Clarify duplicates** via code review:
   - Investigate `*_full.parquet` vs `*_metrics.parquet` 
   - Compare `stock_valuation/` vs `valuation/` directories

### Short-term (Next sprint):
1. **Complete technical registry** - register all 22 orphaned technical files
2. **Consolidate news data** - implement versioning or rolling window
3. **Update dashboards.yaml** - link new technical sources to scanner page
4. **Create DATA/README.md** - document directory structure & orphaned files

### Long-term (Architecture):
1. **Establish data governance policy** - when to create vs. consolidate files
2. **Audit all *_full.parquet** - determine if working copies or legacy
3. **Schema validation** - ensure orphaned files pass registry validation
4. **Pipeline documentation** - map which scripts output each orphaned file

---

## Appendix: Complete File Inventory

### Registered Files (14/54 - 26%):
```
✓ bank_metrics → processed/fundamental/bank/bank_financial_metrics.parquet
✓ company_metrics → processed/fundamental/company/company_financial_metrics.parquet
✓ insurance_metrics → processed/fundamental/insurance/insurance_financial_metrics.parquet
✓ security_metrics → processed/fundamental/security/security_financial_metrics.parquet
✓ pe_historical → processed/valuation/pe/historical/historical_pe.parquet
✓ pb_historical → processed/valuation/pb/historical/historical_pb.parquet
✓ vnindex_valuation → processed/valuation/vnindex/vnindex_valuation_refined.parquet
✓ sector_valuation → processed/sector/sector_valuation_metrics.parquet
✓ ohlcv_raw → raw/ohlcv/OHLCV_mktcap.parquet
✓ technical_basic → processed/technical/basic_data.parquet
✓ market_breadth → processed/technical/market_breadth/market_breadth_daily.parquet
✓ macro_commodity → processed/macro_commodity/macro_commodity_unified.parquet
✓ bsc_individual → processed/forecast/bsc/bsc_individual.parquet
✓ bsc_sector_valuation → processed/forecast/bsc/bsc_sector_valuation.parquet
```

### Orphaned Files (40/54 - 74%):
See PART 1 above for detailed breakdown by category.

---

## Questions for Stakeholder Review

1. **Purpose of "*_full.parquet" files:** Are these working copies, backup versions, or can they be removed?
2. **"individual_*" vs "historical_*" multiples:** Are `stock_valuation/individual_*` truly different from `valuation/*/historical/`?
3. **Technical alerts & money flow:** Which dashboards/services use these orphaned files?
4. **Macro indicators:** Should these 4 macro files be 1 unified source or separate registrations?
5. **VCI coverage data:** Is forecast/VCI actively used? Should it be registered?
6. **BSC combined forecast:** Is this file actively maintained or legacy?

---

**Report Generated:** 2025-12-31 | **Next Review:** After registrations complete
