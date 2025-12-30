# Phase 3: Add Filters & Sort

**Priority:** P1 (High)
**Status:** Pending
**Estimated Changes:** ~80 lines

## Problems

### P4: No Action Priority Sort
- Current: Sort by score DESC only
- Issue: Buy opportunities buried among sell signals

### P5: No Liquidity Filter
- Missing: Filter by avg trading value
- Issue: Penny stocks appear in results

### P6: Score Default = 0
- Current: Shows all signals including weak ones
- Issue: Too much noise, low-quality signals

## Solution

### 3.1 Add Action Priority Sort

Sort order: MUA first → BÁN → TRUNG LẬP, then by score DESC

```python
# In _apply_filters() or after loading
df['action_priority'] = df['direction'].map({
    'BUY': 1,      # MUA first
    'SELL': 2,     # BÁN second
    'NEUTRAL': 3   # TRUNG LẬP last
}).fillna(3)

df = df.sort_values(
    ['action_priority', 'strength'],
    ascending=[True, False]
)
```

### 3.2 Add Liquidity Filter

JOIN with `basic_data.parquet` to get `trading_value`.

**In `ta_dashboard_service.py`:**

```python
def _load_signals() -> pd.DataFrame:
    # ... existing loading code ...

    # Add trading_value from basic_data
    basic_path = Path("DATA/processed/technical/basic_data.parquet")
    if basic_path.exists():
        basic_df = pd.read_parquet(basic_path, columns=['symbol', 'date', 'trading_value'])
        basic_df['date'] = pd.to_datetime(basic_df['date']).dt.date
        combined = combined.merge(
            basic_df,
            on=['symbol', 'date'],
            how='left'
        )

    return combined
```

**In `stock_scanner.py` UI:**

```python
# Add liquidity filter slider
min_value_bn = st.slider(
    "GTGD tối thiểu (tỷ)",
    min_value=0,
    max_value=10,
    value=2,  # Default: 2 billion VND
    key="scanner_min_value"
)

# Apply filter
if min_value_bn > 0 and 'trading_value' in filtered.columns:
    min_value = min_value_bn * 1e9
    filtered = filtered[filtered['trading_value'] >= min_value]
```

### 3.3 Update Score Default

```python
# In stock_scanner.py, change slider default
min_strength = st.slider(
    "Điểm tối thiểu",
    min_value=0,
    max_value=100,
    value=50,  # CHANGED: 0 → 50
    key="scanner_min_strength"
)
```

## File Changes

### `WEBAPP/pages/technical/services/ta_dashboard_service.py`

**Location:** End of `_load_signals()` function

**Add trading_value JOIN:**

```python
# After deduplication, before return:

# Add trading_value from basic_data for liquidity filter
basic_path = Path("DATA/processed/technical/basic_data.parquet")
if basic_path.exists():
    basic_df = pd.read_parquet(basic_path, columns=['symbol', 'date', 'trading_value'])
    # Normalize date for join
    basic_df['date'] = pd.to_datetime(basic_df['date']).dt.date
    combined['date'] = pd.to_datetime(combined['date']).dt.date
    combined = combined.merge(basic_df, on=['symbol', 'date'], how='left')

return combined
```

### `WEBAPP/pages/technical/components/stock_scanner.py`

**Location 1:** Advanced Filters section (~line 235-263)

**Add liquidity filter to expander:**

```python
with st.expander("Bộ lọc nâng cao", expanded=False):
    fcol1, fcol2, fcol3, fcol4 = st.columns(4)  # Add 4th column

    with fcol1:
        # ... existing type filter ...

    with fcol2:
        # ... existing direction filter ...

    with fcol3:
        min_strength = st.slider(
            "Điểm tối thiểu",
            min_value=0,
            max_value=100,
            value=50,  # CHANGED: default 50
            key="scanner_min_strength"
        )

    with fcol4:
        min_value_bn = st.slider(
            "GTGD (tỷ)",
            min_value=0,
            max_value=10,
            value=2,  # Default: 2 billion
            key="scanner_min_value",
            help="Giá trị giao dịch tối thiểu (tỷ VND)"
        )
```

**Location 2:** `_apply_filters()` function (~line 300-351)

**Add liquidity filter and action sort:**

```python
def _apply_filters(
    df: pd.DataFrame,
    symbols_str: Optional[str],
    sector: Optional[str],
    signal_type: Optional[str],
    direction: Optional[str],
    min_strength: int,
    days: int = 2,
    min_value_bn: float = 0  # NEW PARAMETER
) -> pd.DataFrame:
    """Apply all filters to signals dataframe."""

    filtered = df.copy()

    # ... existing filters (date, symbol, sector, signal_type, direction, strength) ...

    # NEW: Liquidity filter
    if min_value_bn > 0 and 'trading_value' in filtered.columns:
        min_value = min_value_bn * 1e9
        filtered = filtered[filtered['trading_value'] >= min_value]

    # NEW: Sort by action priority, then strength
    filtered['action_priority'] = filtered['direction'].map({
        'BUY': 1, 'SELL': 2, 'NEUTRAL': 3
    }).fillna(3)

    filtered = filtered.sort_values(
        ['date', 'action_priority', 'strength'],
        ascending=[False, True, False]
    )

    # Clean up temp column
    filtered = filtered.drop(columns=['action_priority'], errors='ignore')

    return filtered
```

**Location 3:** Function call (~line 266-274)

**Update `_apply_filters()` call:**

```python
filtered = _apply_filters(
    signals,
    search_symbols,
    selected_sector if selected_sector != "Tất cả ngành" else None,
    selected_type if selected_type != 'Tất cả' else None,
    selected_direction if selected_direction != 'Tất cả' else None,
    min_strength,
    selected_days,
    min_value_bn  # NEW: Pass liquidity filter
)
```

## Implementation Steps

### Service Changes
- [ ] Open `ta_dashboard_service.py`
- [ ] Add `trading_value` JOIN at end of `_load_signals()`
- [ ] Test: Verify `trading_value` column in output

### UI Changes
- [ ] Open `stock_scanner.py`
- [ ] Change `min_strength` default from 0 to 50
- [ ] Add `min_value_bn` slider in advanced filters
- [ ] Update `_apply_filters()` signature with new parameter
- [ ] Add liquidity filter logic
- [ ] Add action priority sort logic
- [ ] Update function call with new parameter
- [ ] Test: Verify filters work correctly

## Success Criteria

- [ ] Score filter default = 50 (not 0)
- [ ] Liquidity filter slider appears in UI
- [ ] Liquidity filter works (removes penny stocks)
- [ ] MUA signals appear first in table
- [ ] Within MUA, sorted by score DESC
- [ ] BÁN signals appear after all MUA

## Test Cases

### Sort Order Expected
```
1. VCB | 29/12 | morning_star | 85 | MUA  (MUA, high score)
2. FPT | 29/12 | hammer       | 72 | MUA  (MUA, medium score)
3. HPG | 29/12 | engulfing    | 68 | MUA  (MUA, lower score)
4. VIC | 29/12 | hanging_man  | 75 | BÁN  (BÁN, high score)
5. MWG | 29/12 | shooting_star| 62 | BÁN  (BÁN, lower score)
```

### Liquidity Filter Expected
- Min 2 tỷ: ~200 stocks remain
- Min 5 tỷ: ~100 stocks remain
- Min 10 tỷ: ~50 stocks remain

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing trading_value | Filter won't work | Show warning, skip filter |
| Date join mismatch | Missing values | Use left join, handle NaN |
| Performance (JOIN) | Slow loading | JOIN is one-time, acceptable |
