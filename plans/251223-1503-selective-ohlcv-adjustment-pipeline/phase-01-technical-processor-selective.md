# Phase 01: TechnicalProcessor Selective Mode

## Objective

Add `symbols` parameter to TechnicalProcessor for processing only specified symbols and atomic merge back to parquet.

## Current State

```python
# technical_processor.py - lines 157-193
def calculate_all_indicators(self, n_sessions: int = 200) -> pd.DataFrame:
    ohlcv_df = self.load_ohlcv_data(n_sessions)
    for symbol in ohlcv_df['symbol'].unique():  # Processes ALL symbols
        symbol_df = ohlcv_df[ohlcv_df['symbol'] == symbol].copy()
        ...
```

## Changes Required

### 1. Add `calculate_selective_indicators()` method

```python
def calculate_selective_indicators(
    self,
    symbols: List[str],
    n_sessions: int = 200
) -> pd.DataFrame:
    """
    Calculate indicators for specified symbols only.

    Args:
        symbols: List of symbols to process
        n_sessions: Historical lookback (min 200 for SMA200)

    Returns:
        DataFrame with indicators for specified symbols
    """
    logger.info(f"Selective processing: {len(symbols)} symbols")

    # Load OHLCV for affected symbols only
    ohlcv_df = self.load_ohlcv_data(n_sessions)
    ohlcv_df = ohlcv_df[ohlcv_df['symbol'].isin(symbols)]

    results = []
    for symbol in symbols:
        symbol_df = ohlcv_df[ohlcv_df['symbol'] == symbol].copy()
        if len(symbol_df) >= 200:
            symbol_df = symbol_df.sort_values('date')
            symbol_df = self.calculate_indicators_for_symbol(symbol_df)
            results.append(symbol_df)
        else:
            logger.warning(f"Skipping {symbol}: only {len(symbol_df)} rows")

    return pd.concat(results, ignore_index=True) if results else pd.DataFrame()
```

### 2. Add `atomic_merge_basic_data()` method

```python
def atomic_merge_basic_data(
    self,
    new_data: pd.DataFrame,
    affected_symbols: List[str],
    output_path: str = "DATA/processed/technical/basic_data.parquet"
) -> bool:
    """
    Atomically merge new indicator data for affected symbols.

    Pattern:
    1. Load existing parquet
    2. Remove rows for affected symbols
    3. Append new data
    4. Write to .tmp, atomic rename

    Returns:
        True if successful
    """
    output_path = Path(output_path)
    temp_path = output_path.with_suffix('.parquet.tmp')

    try:
        # Load existing
        if output_path.exists():
            existing = pd.read_parquet(output_path)
        else:
            existing = pd.DataFrame()

        # Remove affected symbols
        if not existing.empty:
            mask = ~existing['symbol'].isin(affected_symbols)
            filtered = existing[mask].copy()
        else:
            filtered = pd.DataFrame()

        # Append new data
        if not new_data.empty:
            new_data['date'] = pd.to_datetime(new_data['date']).dt.date
            combined = pd.concat([filtered, new_data], ignore_index=True)
        else:
            combined = filtered

        # Sort and save
        combined = combined.sort_values(['symbol', 'date']).reset_index(drop=True)
        combined.to_parquet(temp_path, index=False)

        # Atomic rename
        temp_path.replace(output_path)

        logger.info(f"Merged {len(affected_symbols)} symbols into {output_path}")
        return True

    except Exception as e:
        logger.error(f"Merge failed: {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False
```

### 3. Update CLI

Add to `main()`:

```python
parser.add_argument(
    '--symbols',
    type=str,
    help='Comma-separated symbols for selective processing'
)
parser.add_argument(
    '--merge',
    action='store_true',
    help='Merge results into existing basic_data.parquet'
)

# In execution:
if args.symbols:
    symbols = [s.strip().upper() for s in args.symbols.split(',')]
    df = processor.calculate_selective_indicators(symbols, n_sessions=args.sessions)
    if args.merge:
        processor.atomic_merge_basic_data(df, symbols)
    else:
        processor.save_basic_data(df)
```

## Validation Checklist

- [ ] `calculate_selective_indicators(['ACB', 'VCB'])` returns only 2 symbols
- [ ] `atomic_merge_basic_data()` preserves all other symbols
- [ ] Row count before merge == row count after merge (for 458 symbols)
- [ ] No duplicate (symbol, date) pairs after merge
- [ ] .tmp file cleaned up on failure

## Test Commands

```bash
# Selective calc only
python technical_processor.py --symbols ACB,VCB,TCB --sessions 200

# Selective calc + merge
python technical_processor.py --symbols ACB,VCB,TCB --sessions 200 --merge

# Verify
python -c "
import pandas as pd
df = pd.read_parquet('DATA/processed/technical/basic_data.parquet')
print(f'Symbols: {df.symbol.nunique()}')
print(f'Rows: {len(df)}')
print(df[df.symbol.isin(['ACB','VCB','TCB'])].groupby('symbol').size())
"
```

## Edge Cases

1. **Symbol not in OHLCV:** Log warning, skip
2. **< 200 rows for symbol:** Log warning, skip (indicators incomplete)
3. **Empty new_data:** Skip merge, return success
4. **Concurrent writes:** Atomic rename handles this

## Dependencies

None - self-contained changes to `technical_processor.py`.
