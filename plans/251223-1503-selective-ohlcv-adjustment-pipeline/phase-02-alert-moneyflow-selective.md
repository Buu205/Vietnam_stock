# Phase 02: AlertDetector + MoneyFlowAnalyzer Selective Mode

## Objective

Add `symbols` parameter to AlertDetector and MoneyFlowAnalyzer for processing only specified symbols with atomic merge.

---

## Part A: AlertDetector Changes

### File: `PROCESSORS/technical/indicators/alert_detector.py`

### 1. Update `detect_all_alerts()` signature

Current (line 465):
```python
def detect_all_alerts(self, date: str = None, n_sessions: int = 200) -> Dict[str, pd.DataFrame]:
```

Updated:
```python
def detect_all_alerts(
    self,
    date: str = None,
    n_sessions: int = 200,
    symbols: List[str] = None
) -> Dict[str, pd.DataFrame]:
    """
    Detect all alerts.

    Args:
        date: Target date (default: latest)
        n_sessions: Lookback sessions
        symbols: Optional list of symbols to process (selective mode)

    Returns:
        Dict with alert DataFrames
    """
```

### 2. Add symbol filtering after load

Insert after line 479 (`ohlcv_df = self.load_data(n_sessions)`):

```python
# Selective mode: filter to specified symbols
if symbols is not None:
    ohlcv_df = ohlcv_df[ohlcv_df['symbol'].isin(symbols)]
    logger.info(f"Selective mode: processing {len(symbols)} symbols")
```

### 3. Add atomic merge for alerts

New method:

```python
def merge_alerts_selective(
    self,
    new_alerts: Dict[str, pd.DataFrame],
    affected_symbols: List[str],
    output_dir: str = "DATA/processed/technical/alerts/daily"
) -> bool:
    """
    Merge new alerts for affected symbols only.

    Preserves existing alerts for non-affected symbols.
    """
    output_dir = Path(output_dir)

    for alert_type, new_df in new_alerts.items():
        if new_df.empty:
            continue

        output_path = output_dir / f"{alert_type}_latest.parquet"

        if output_path.exists():
            existing = pd.read_parquet(output_path)
            # Remove affected symbols
            filtered = existing[~existing['symbol'].isin(affected_symbols)]
            # Append new
            combined = pd.concat([filtered, new_df], ignore_index=True)
        else:
            combined = new_df

        combined.to_parquet(output_path, index=False)

    return True
```

---

## Part B: MoneyFlowAnalyzer Changes

### File: `PROCESSORS/technical/indicators/money_flow.py`

### 1. Update `calculate_all_money_flow()` signature

Current (line 164):
```python
def calculate_all_money_flow(self, n_sessions: int = 200) -> pd.DataFrame:
```

Updated:
```python
def calculate_all_money_flow(
    self,
    n_sessions: int = 200,
    symbols: List[str] = None
) -> pd.DataFrame:
    """
    Calculate money flow.

    Args:
        n_sessions: Lookback sessions
        symbols: Optional list of symbols (selective mode)
    """
```

### 2. Add symbol filtering

Insert after line 177 (`ohlcv_df = self.load_data(n_sessions)`):

```python
# Selective mode
if symbols is not None:
    ohlcv_df = ohlcv_df[ohlcv_df['symbol'].isin(symbols)]
    logger.info(f"Selective mode: {len(symbols)} symbols")
```

### 3. Add atomic merge for money flow

New method:

```python
def atomic_merge_money_flow(
    self,
    new_data: pd.DataFrame,
    affected_symbols: List[str],
    output_path: str = "DATA/processed/technical/money_flow/individual_money_flow.parquet"
) -> bool:
    """
    Atomically merge money flow data for affected symbols.
    """
    output_path = Path(output_path)
    temp_path = output_path.with_suffix('.parquet.tmp')

    try:
        if output_path.exists():
            existing = pd.read_parquet(output_path)
            filtered = existing[~existing['symbol'].isin(affected_symbols)]
        else:
            filtered = pd.DataFrame()

        new_data['date'] = pd.to_datetime(new_data['date']).dt.date
        combined = pd.concat([filtered, new_data], ignore_index=True)
        combined = combined.sort_values(['symbol', 'date']).reset_index(drop=True)

        combined.to_parquet(temp_path, index=False)
        temp_path.replace(output_path)

        logger.info(f"Merged money flow for {len(affected_symbols)} symbols")
        return True

    except Exception as e:
        logger.error(f"Money flow merge failed: {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False
```

---

## Validation Checklist

### AlertDetector
- [ ] `detect_all_alerts(symbols=['ACB','VCB'])` returns alerts only for ACB, VCB
- [ ] `merge_alerts_selective()` preserves other symbol alerts
- [ ] Historical append still works with selective mode

### MoneyFlowAnalyzer
- [ ] `calculate_all_money_flow(symbols=['ACB'])` returns only ACB
- [ ] `atomic_merge_money_flow()` preserves non-affected symbols
- [ ] Symbol count unchanged after merge

## Test Commands

```bash
# Alert selective test
python -c "
from PROCESSORS.technical.indicators.alert_detector import TechnicalAlertDetector
detector = TechnicalAlertDetector()
alerts = detector.detect_all_alerts(symbols=['ACB', 'VCB', 'TCB'])
for k, v in alerts.items():
    print(f'{k}: {len(v)} alerts, symbols: {v.symbol.unique().tolist() if not v.empty else []}')
"

# Money flow selective test
python -c "
from PROCESSORS.technical.indicators.money_flow import MoneyFlowAnalyzer
analyzer = MoneyFlowAnalyzer()
df = analyzer.calculate_all_money_flow(symbols=['ACB', 'VCB'])
print(f'Symbols: {df.symbol.unique().tolist()}')
print(f'Rows: {len(df)}')
"
```

## Edge Cases

1. **No alerts for affected symbols:** Return empty DataFrame, skip merge
2. **New symbol not in existing parquet:** Append works normally
3. **Symbol removed from universe:** Filtered out naturally

## Dependencies

- Phase 01 completed (atomic merge pattern established)
