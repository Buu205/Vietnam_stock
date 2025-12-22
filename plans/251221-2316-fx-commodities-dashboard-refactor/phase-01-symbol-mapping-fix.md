# Phase 1: Symbol Mapping Fix

**Priority:** Critical (Blocking)
**Effort:** 2 hours
**Risk:** Low

---

## Context

Dashboard `macro_labels` dict (lines 73-86) expects cleaned snake_case symbols but parquet data contains Vietnamese diacritics and malformed names.

**Research Finding (researcher-01, lines 19-51):**
- 6 symbols mismatched out of 12 total (50% failure rate)
- Deposit rates: completely malformed (`13_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb`)
- Exchange rates: diacritics not stripped (`tỷ_giá_usd_trung_tâm`)

## Overview

Create bidirectional symbol mapping dict that maps actual parquet symbols → display labels.

## Requirements

1. Map all 12 macro symbols from actual data to Vietnamese display labels
2. Update symbol filtering logic to use actual data symbols
3. Add validation logging for unrecognized symbols
4. Backward compatible - don't break working charts

## Related Code Files

### `fx_commodities_dashboard.py` (lines 73-86)
```python
# CURRENT - expects clean symbols that don't exist in data
macro_labels = {
    'ls_huy_dong_13_thang': 'Lãi suất huy động 13 tháng',  # ❌ doesn't exist
    'ty_gia_usd_trung_tam': 'Tỷ giá USD trung tâm',       # ❌ diacritics mismatch
    ...
}
```

### `fx_commodities_dashboard.py` (lines 68-71)
```python
# Symbol filtering uses string matching that fails
interest_rate_symbols = [s for s in macro_symbols if 'ls_' in s]
exchange_rate_symbols = [s for s in macro_symbols if 'ty_gia' in s]
```

## Implementation Steps

### Step 1: Create Symbol Mapping Dict (NEW)
Add at line ~72, before `macro_labels`:

```python
# Map actual parquet symbols → canonical display symbols
MACRO_SYMBOL_MAP = {
    # Deposit Rates (malformed in data)
    '13_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb': 'ls_huy_dong_13_thang',
    '1_3_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb': 'ls_huy_dong_1_3_thang',
    '6_9_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb': 'ls_huy_dong_6_9_thang',

    # Interbank Rates (have diacritics)
    'ls_liên_ngân_hàng_kỳ_hạn_1_tuần': 'ls_lien_ngan_hang_ky_han_1_tuan',
    'ls_liên_ngân_hàng_kỳ_hạn_2_tuần': 'ls_lien_ngan_hang_ky_han_2_tuan',
    'ls_qua_dem_lien_ngan_hang': 'ls_qua_dem_lien_ngan_hang',  # clean

    # Exchange Rates (have diacritics)
    'tỷ_giá_usd_nhtm_bán_ra': 'ty_gia_usd_nhtm_ban_ra',
    'tỷ_giá_usd_trung_tâm': 'ty_gia_usd_trung_tam',
    'tỷ_usd_tự_do_bán_ra': 'ty_gia_usd_tu_do_ban_ra',
    'ty_gia_san': 'ty_gia_san',  # clean
    'ty_gia_tran': 'ty_gia_tran',  # clean

    # Bonds
    'vn_gov_bond_5y': 'vn_gov_bond_5y',  # clean
}

# Reverse map for lookup
CANONICAL_TO_ACTUAL = {v: k for k, v in MACRO_SYMBOL_MAP.items()}
```

### Step 2: Update macro_labels Dict (MODIFY)
Use canonical symbols as keys (no change needed, they're already correct):

```python
macro_labels = {
    'ls_huy_dong_13_thang': 'Lãi suất huy động 13 tháng',
    'ls_huy_dong_1_3_thang': 'Lãi suất huy động 1-3 tháng',
    'ls_huy_dong_6_9_thang': 'Lãi suất huy động 6-9 tháng',
    'ls_lien_ngan_hang_ky_han_1_tuan': 'LS liên NH kỳ hạn 1 tuần',
    'ls_lien_ngan_hang_ky_han_2_tuan': 'LS liên NH kỳ hạn 2 tuần',
    'ls_qua_dem_lien_ngan_hang': 'LS qua đêm liên NH',
    'ty_gia_san': 'Tỷ giá sàn',
    'ty_gia_tran': 'Tỷ giá trần',
    'ty_gia_usd_nhtm_ban_ra': 'Tỷ giá USD NHTM bán ra',
    'ty_gia_usd_trung_tam': 'Tỷ giá USD trung tâm',
    'ty_gia_usd_tu_do_ban_ra': 'Tỷ giá USD tự do bán ra',
    'vn_gov_bond_5y': 'Lợi suất TPCP 5 năm'
}
```

### Step 3: Create Helper Function for Symbol Resolution
Add after mappings:

```python
def resolve_macro_symbol(actual_symbol: str) -> str:
    """Convert actual data symbol to canonical symbol."""
    return MACRO_SYMBOL_MAP.get(actual_symbol, actual_symbol)

def get_actual_symbol(canonical_symbol: str) -> str:
    """Convert canonical symbol to actual data symbol for loader."""
    return CANONICAL_TO_ACTUAL.get(canonical_symbol, canonical_symbol)

def get_label(canonical_symbol: str) -> str:
    """Get Vietnamese display label for canonical symbol."""
    return macro_labels.get(canonical_symbol, canonical_symbol)
```

### Step 4: Update Symbol Filtering Logic (line ~68)
Replace string matching with mapping-based approach:

```python
# Get canonical symbols from actual data
macro_symbols_raw = macro_df['symbol'].unique().tolist()
macro_symbols = [resolve_macro_symbol(s) for s in macro_symbols_raw]

# Group by category using canonical names
deposit_rate_symbols = [s for s in macro_symbols if s.startswith('ls_huy_dong')]
interbank_rate_symbols = [s for s in macro_symbols if s.startswith('ls_lien') or s.startswith('ls_qua')]
exchange_rate_symbols = [s for s in macro_symbols if s.startswith('ty_gia')]
bond_symbols = [s for s in macro_symbols if 'bond' in s]
```

### Step 5: Update Data Retrieval (throughout file)
Modify `macro_loader.get_series()` calls to use actual symbols:

```python
# Before
series1 = filter_series_by_days(macro_loader.get_series(symbol1), days)

# After
actual_symbol1 = get_actual_symbol(symbol1)
series1 = filter_series_by_days(macro_loader.get_series(actual_symbol1), days)
```

### Step 6: Add Validation Logging
Add after loading macro data (line ~63):

```python
# Validate symbol mapping
unmapped_symbols = [s for s in macro_symbols_raw if s not in MACRO_SYMBOL_MAP]
if unmapped_symbols:
    import logging
    logging.warning(f"FX Dashboard: Unmapped macro symbols: {unmapped_symbols}")
```

## Success Criteria

1. [ ] All 12 macro symbols resolve correctly from data to display
2. [ ] Interest rate charts render for all 6 symbols
3. [ ] Exchange rate charts render for all 5 symbols
4. [ ] Bond chart renders for 1 symbol
5. [ ] No Python errors or empty charts
6. [ ] Validation logs capture any new unmapped symbols

## Testing Steps

1. Run dashboard: `streamlit run WEBAPP/main_app.py`
2. Navigate to FX & Commodities page
3. Select "Lãi suất huy động" - verify 3 interest rate lines appear
4. Select "Lãi suất liên ngân hàng" - verify 3 interbank lines appear
5. Select "Tỷ giá USD" - verify USD pairs chart works
6. Check terminal for any validation warnings

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| More unmapped symbols appear | Low | Medium | Validation logging catches early |
| Data format changes upstream | Medium | High | Pin data version, add tests |
| Performance overhead | Low | Low | Dict lookup is O(1) |

## Rollback Plan

Revert to original `macro_labels` dict if issues arise. No data changes made.
