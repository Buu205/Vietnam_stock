# FX & Commodities Dashboard - Data Symbols Analysis

**Date:** 2025-12-21
**Analysis Scope:** Symbol mapping mismatch, dual-axis chart pairings, data availability
**Data Source:** `DATA/processed/macro_commodity/macro_commodity_unified.parquet` (22,526 records, 12 columns)

---

## Executive Summary

**Critical Issue:** Dashboard expects snake_case symbols but data contains **malformed symbols with mixed case, underscores, Vietnamese diacritics, and embedded labels**. Example: `13_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb` instead of `ls_huy_dong_13_thang`.

**Impact:** Dashboard `macro_labels` dict has ~30% mismatch with actual data symbols, causing chart failures for interest rate & bond visualizations.

**Commodities:** Clean symbol names (18 active), dual-axis pairings require VN vs Global comparisons not yet implemented.

---

## 1. Macro Symbols - Data vs Dashboard Mismatch

### Actual Data Symbols (12 Macro Symbols)

| Category | Symbol (As Stored) | Expected Symbol | Label Mapping | Data Range | Status |
|----------|-------------------|-----------------|----------------|------------|--------|
| **Interest Rates** | `13_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb` | `ls_huy_dong_13_thang` | ❌ MISSING | 2023-12-19 → 2025-12-19 | 504 recs |
| | `1_3_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb` | `ls_huy_dong_1_3_thang` | ❌ MISSING | 2023-12-19 → 2025-12-19 | 504 recs |
| | `6_9_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb` | `ls_huy_dong_6_9_thang` | ❌ MISSING | 2023-12-19 → 2025-12-19 | 504 recs |
| **Interbank Rates** | `ls_liên_ngân_hàng_kỳ_hạn_1_tuần` | ✓ Match | ✓ In dict | 2023-12-19 → 2025-12-19 | 504 recs |
| | `ls_liên_ngân_hàng_kỳ_hạn_2_tuần` | ✓ Match | ✓ In dict | 2023-12-19 → 2025-12-19 | 504 recs |
| | `ls_qua_dem_lien_ngan_hang` | ✓ Match | ✓ In dict | 2023-12-19 → 2025-12-19 | 504 recs |
| **Exchange Rates** | `ty_gia_san` | ✓ Match | ✓ In dict | Older data | N/A |
| | `ty_gia_tran` | ✓ Match | ✓ In dict | Older data | N/A |
| | `tỷ_giá_usd_nhtm_bán_ra` | `ty_gia_usd_nhtm_ban_ra` | ❌ MISMATCH (diacritics) | 2023-12-19 → 2025-12-19 | ~500 recs |
| | `tỷ_giá_usd_trung_tâm` | `ty_gia_usd_trung_tam` | ❌ MISMATCH (diacritics) | 2023-12-19 → 2025-12-19 | ~500 recs |
| | `tỷ_usd_tự_do_bán_ra` | `ty_gia_usd_tu_do_ban_ra` | ❌ MISMATCH (diacritics) | 2023-12-19 → 2025-12-19 | ~500 recs |
| **Bonds** | `vn_gov_bond_5y` | ✓ Match | ✓ In dict | Historical | N/A |

### Problem Pattern

**50% symbols fail matching:**

1. **Deposit Rates (3 symbols):** Data uses malformed names with Vietnamese text
   - Data: `13_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb`
   - Expected: `ls_huy_dong_13_thang`
   - Dashboard: `macro_labels.get('ls_huy_dong_13_thang')` → returns `None`

2. **Exchange Rates (3 symbols):** Diacritics not removed during data ingestion
   - Data: `tỷ_giá_usd_nhtm_bán_ra` (contains ế, ă diacritics)
   - Expected: `ty_gia_usd_nhtm_ban_ra`
   - Dashboard: Looks for symbol without diacritics → fails

---

## 2. Commodity Symbols - Data is Clean

### Actual Data Symbols (18 Commodities)

| Commodity | Symbol | Unit | Global Pair | VN Pair | Data Range | Status |
|-----------|--------|------|-------------|---------|------------|--------|
| **Metals** | `gold_global` | $/oz | ✓ (Global) | ❌ Missing | 1997 → 2025 | ✓ |
| | `iron_ore` | $/ton | ✓ (Global) | ❌ Missing | 2011 → 2025 | ✓ |
| | `steel_hrc`, `steel_d10`, `steel_coated` | $/ton | ✓ (3 types) | ❌ Missing | 2003 → 2025 | ✓ |
| **Energy** | `oil_wti`, `oil_crude` | $/bbl | ✓ (2 types) | ❌ Missing | 2003 → 2025 | ✓ |
| | `gas_natural` | $/mmbtu | ✓ (Global) | ❌ Missing | 1998 → 2025 | ✓ |
| **VN Agricultural** | `pork_vn_wichart` | ₫/kg | ❌ Global | ✓ (VN) | 2020 → 2025 | ✓ |
| | `pork_china` | ¥/kg | ✓ (Global) | ❌ VN Missing | 2010 → 2025 | ✓ |
| | `rubber` (cao_su) | $/kg | ✓ (Global) | ❌ VN Missing | 1997 → 2025 | ✓ |
| **Crops** | `corn`, `soybean`, `sugar` | $/ton | ✓ (Global) | ❌ Missing | 2003 → 2025 | ✓ |
| **VN-Specific** | `pvc`, `coke` | $/ton | ✓ (Global) | ❌ VN Missing | 2003 → 2025 | ✓ |
| | `sua_bot_wmp` | $/ton | ✓ (Global) | ❌ VN Missing | 2005 → 2025 | ✓ |
| | `fertilizer_ure` | $/ton | ✓ (Global) | ❌ VN Missing | 2005 → 2025 | ✓ |

### Insight

Commodity data is well-named. **Gap: No VN vs Global dual-axis pairs available** except pork (VN vs China).

---

## 3. Dual-Axis Chart Pairings

### Current Implementation (Dashboard)

#### Macro - Exchange Rates (All work)
- USD Trung tâm vs Tự do
- USD NHTM vs Tự do
- Tỷ giá Sàn vs Trần

#### Commodities - Implemented Pairs

```python
dual_axis_pairs = {
    "Gold (Global)": ('gold_global', 'gold_global', '$/oz', '$/oz'),  # Same source
    "Pork": ('pork_vn_wichart', 'pork_china', '₫/kg', '¥/kg'),       # VN vs China ✓
    "Steel": ('steel_hrc', 'steel_d10', '$/ton', '$/ton'),           # 2 variants ✓
    # ... more
}
```

### Missing Opportunities

**VN vs Global pairs (Not implemented):**
1. Pork VN (₫/kg) vs Global ($/kg) - Market influence analysis
2. Oil prices VN retail vs WTI global - Price gap tracking
3. Gold retail VN vs global spot - Local markup analysis
4. Rubber VN production vs global price - Supply correlation
5. Fertilizer VN retail vs global futures - Import cost pass-through

---

## 4. Root Cause Analysis

### Why Macro Symbols Broke

**Source Data Pipeline Issue:**

1. **Data Ingestion:** Raw symbols come with Vietnamese text, diacritics
2. **Transformation:** Incomplete diacritic removal (only some symbols cleaned)
3. **Storage:** Mixed cleaned/uncleaned symbols in same parquet file
4. **Result:** Dashboard's hardcoded `macro_labels` dict references symbols that don't exist

### Example Flow:
```
Raw source: "Lãi suất huy động 13 tháng - NHTM lớn (MBB, ACB, TCB, VPB)"
  ↓ (Bad transform)
Stored as: "13_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb"
  ↓ (Dashboard lookup)
macro_labels.get("ls_huy_dong_13_thang") → None (symbol doesn't exist)
  ✗ Chart fails to render
```

---

## 5. Recommendations

### Immediate Fixes (High Priority)

1. **Sanitize Macro Symbols** (PROCESSORS layer)
   - Standardize all macro symbols to snake_case, remove diacritics
   - Maintain mapping table: original → canonical
   - Test: All 12 macro symbols must match dashboard `macro_labels` keys

2. **Update Dashboard Macros Labels** (Interim fix)
   - Add actual stored symbol names to `macro_labels` dict
   - Map both cleaned & uncleaned variants for backward compatibility

3. **Add Data Validation** (Data pipeline)
   - Pre-flight check: symbols in parquet must exist in dashboard dict
   - Log mismatches before cache update

### Medium-term (Refactor)

4. **Centralize Symbol Registry**
   - Move `macro_labels`, `commodity_labels` to `config/metadata_registry/macro_commodity_symbols.json`
   - Single source of truth, not embedded in dashboard

5. **Implement VN vs Global Pairs** (Commodities)
   - Add VN retail prices data source (WiChart, VNStock)
   - Build dual-axis pairs: VN vs global for pork, gold, oil, fertilizer
   - Useful for inflation analysis, import pass-through tracking

6. **Data Quality Gates**
   - Unit consistency validation (all steel prices in $/ton, not mixed)
   - Data freshness checks (warn if no updates >7 days)
   - Missing value alerting (>20% NaN in recent data)

---

## Appendix: Full Symbol Inventory

### Macro (12 symbols)
```
Interest Rates (Deposit): 13_tháng..., 1_3_tháng..., 6_9_tháng...
Interbank Rates: ls_liên_ngân_hàng_kỳ_hạn_1_tuần, ls_liên_ngân_hàng_kỳ_hạn_2_tuần, ls_qua_dem_lien_ngan_hang
Exchange: tỷ_giá_usd_nhtm_bán_ra, tỷ_giá_usd_trung_tâm, tỷ_usd_tự_do_bán_ra, ty_gia_san, ty_gia_tran
Bonds: vn_gov_bond_5y
```

### Commodities (18 symbols)
```
Metals: gold_global, iron_ore, steel_hrc, steel_d10, steel_coated
Energy: oil_wti, oil_crude, gas_natural
Agriculture: pork_vn_wichart, pork_china, cao_su, corn, soybean, sugar, pvc, coke
Food: sua_bot_wmp, fertilizer_ure
```

---

## Unresolved Questions

1. **Source of malformed deposit rate symbols?** Which upstream system produces `13_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb`?
2. **VN retail prices availability?** Where to source live pork/fertilizer/gold retail prices for dual-axis pairs?
3. **Data ingestion sanitization:** Is diacritic removal performed in PROCESSORS pipeline or at dashboard level?
4. **Bond data currency:** Is `vn_gov_bond_5y` in % yield or basis points? Check recent values.
