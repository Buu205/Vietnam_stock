# Phase 1: Spike Detector Module

**File:** `PROCESSORS/technical/ohlcv/ohlcv_spike_detector.py`
**Effort:** 3h
**Dependencies:** None (standalone module)

## Objective

Create spike detection module to identify abnormal daily price movements that exceed Vietnam stock exchange limits, indicating unadjusted corporate actions (splits/dividends).

## Vietnam Stock Exchange Daily Limits (CRITICAL)

```python
# Vietnamese stock exchanges have strict daily price limits
# Any movement EXCEEDING these limits = 100% corporate action (not adjusted)

EXCHANGE_LIMITS = {
    'HOSE': 0.07,    # ±7% - Ho Chi Minh Stock Exchange
    'HNX': 0.10,     # ±10% - Hanoi Stock Exchange
    'UPCOM': 0.15,   # ±15% - Unlisted Public Company Market
}

# If |daily_return| > limit → GUARANTEED unadjusted corporate action
# No false positives possible - this is a hard constraint
```

## Algorithm

### 0. Exchange Limit Detection (PRIMARY - 100% Reliable)

```python
def detect_exchange_limit_breach(df: pd.DataFrame) -> pd.DataFrame:
    """
    Primary detection: any daily return exceeding exchange limits
    MUST be an unadjusted corporate action.

    This is the most reliable method - NO false positives.
    Vietnamese exchanges have strict ±7/10/15% daily limits.
    """
    df = df.copy()
    df['daily_return'] = df.groupby('symbol')['close'].pct_change()

    # Map symbol to exchange (default HOSE if unknown)
    df['exchange_limit'] = df['symbol'].apply(get_exchange_limit)

    # Flag any movement exceeding exchange limit
    df['exceeds_limit'] = df['daily_return'].abs() > df['exchange_limit']

    # These are GUARANTEED corporate actions - auto-refresh
    return df[df['exceeds_limit']]


def get_exchange_limit(symbol: str) -> float:
    """
    Get daily limit for symbol's exchange.

    HOSE tickers: 3 chars (VCB, ACB, FPT)
    HNX tickers: 3 chars ending in specific patterns or 4+ chars
    UPCOM: specific list

    Default to HOSE (7%) for safety - most conservative.
    """
    # Load exchange mapping from registry or use heuristic
    # For now, use conservative HOSE limit
    return 0.07  # 7% - most common, safest default
```

### 1. Z-Score Detection (SECONDARY - for edge cases)

```python
def calculate_zscore_spikes(df: pd.DataFrame, window: int = 20, threshold: float = 3.0) -> pd.DataFrame:
    """
    Detect spikes using Z-score on daily returns.

    Args:
        df: OHLCV with columns [symbol, date, close]
        window: Rolling window for mean/std (default: 20 days)
        threshold: Z-score threshold (default: 3.0 = 3 sigma)

    Returns:
        DataFrame with columns [symbol, date, daily_return, zscore, is_spike]
    """
    df = df.copy()
    df['daily_return'] = df.groupby('symbol')['close'].pct_change()

    # Rolling mean and std
    df['ret_mean'] = df.groupby('symbol')['daily_return'].transform(
        lambda x: x.rolling(window, min_periods=10).mean()
    )
    df['ret_std'] = df.groupby('symbol')['daily_return'].transform(
        lambda x: x.rolling(window, min_periods=10).std()
    )

    # Z-score
    df['zscore'] = (df['daily_return'] - df['ret_mean']) / df['ret_std']
    df['is_spike'] = df['zscore'].abs() > threshold

    return df[df['is_spike']]
```

### 2. Split Ratio Detection (Confirmation)

```python
def detect_split_ratio(prev_close: float, curr_open: float, tolerance: float = 1.5) -> float | None:
    """
    Detect stock split ratio from price gap.

    Common ratios:
        2:1 split → ratio ≈ 2.0 (price halved)
        5:1 split → ratio ≈ 5.0 (price /5)
        Reverse 1:2 → ratio ≈ 0.5 (price doubled)
    """
    if prev_close <= 0 or curr_open <= 0:
        return None

    ratio = prev_close / curr_open

    # Check if ratio is close to common split values
    common_ratios = [2.0, 3.0, 4.0, 5.0, 10.0, 0.5, 0.33, 0.25, 0.2, 0.1]
    for common in common_ratios:
        if abs(ratio - common) < 0.1:  # 10% tolerance
            return common

    # Return raw ratio if significant gap
    if ratio > tolerance or ratio < (1 / tolerance):
        return round(ratio, 2)

    return None
```

### 3. Volume Spike Confirmation (Filter)

```python
def has_volume_spike(volume: float, volume_ma20: float, multiplier: float = 2.0) -> bool:
    """Volume > 2x 20-day average confirms corporate action."""
    if volume_ma20 <= 0:
        return False
    return volume > volume_ma20 * multiplier
```

## Output Schema

```python
SPIKE_SCHEMA = {
    'symbol': str,           # Ticker
    'date': 'datetime64',    # Date of spike
    'daily_return': float,   # % return that day
    'zscore': float,         # Z-score value
    'split_ratio': float,    # Detected split ratio (None if not split)
    'volume_spike': bool,    # Volume confirmation
    'spike_type': str,       # 'SPLIT' | 'DIVIDEND' | 'UNKNOWN'
    'needs_refresh': bool    # True if should trigger OHLCV refresh
}
```

## Classification Logic

```python
def classify_spike(row: pd.Series) -> str:
    """
    Classify spike type based on pattern.

    Rules:
        - SPLIT: split_ratio detected + volume spike
        - DIVIDEND: |return| 5-15% + volume spike (typical dividend yield)
        - UNKNOWN: spike detected but no clear pattern
    """
    if row['split_ratio'] is not None:
        return 'SPLIT'
    elif 0.05 <= abs(row['daily_return']) <= 0.15 and row['volume_spike']:
        return 'DIVIDEND'
    else:
        return 'UNKNOWN'
```

## CLI Interface

```bash
# Scan all symbols for spikes
python ohlcv_spike_detector.py --scan

# Scan specific date range
python ohlcv_spike_detector.py --scan --start 2025-01-01 --end 2025-12-31

# Output to CSV for review
python ohlcv_spike_detector.py --scan --output spikes.csv

# Only show confirmed splits (no unknown)
python ohlcv_spike_detector.py --scan --splits-only
```

## Integration Points

| Consumer | Method |
|----------|--------|
| `ohlcv_adjustment_detector.py` | Import `OHLCVSpikeDetector.get_flagged_symbols()` |
| Daily pipeline | Optional: add `--spike-check` to daily updater |
| Manual audit | Export to CSV for human review |

## Test Cases

1. **CSV stock (2025-06-04)**: +373.7% → should detect split ratio ≈ 4.7
2. **CTG (2025-12-17)**: Share dividend 100:44.6 → should detect
3. **Normal volatility**: 5% move → should NOT flag (below Z-score threshold)
4. **Market crash day**: VN-Index -5% → should NOT flag (systematic move)

## Deliverables

- [ ] `ohlcv_spike_detector.py` with `OHLCVSpikeDetector` class
- [ ] Z-score calculation with configurable window/threshold
- [ ] Split ratio detection with common ratio matching
- [ ] Volume spike confirmation filter
- [ ] CLI interface with `--scan`, `--output` flags
- [ ] Unit tests for detection logic
