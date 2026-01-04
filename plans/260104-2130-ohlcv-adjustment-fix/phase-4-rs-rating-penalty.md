# Phase 4: Re-enable RS Rating Penalty

**File:** `PROCESSORS/technical/indicators/rs_rating.py`
**Effort:** 2h
**Dependencies:** Phase 1-3 (OHLCV data must be fixed first)

## Objective

Re-enable the downtrend penalty logic in RS Rating calculator after OHLCV data quality is verified.

## Current State (Disabled)

Lines 140-156 in `rs_rating.py`:

```python
# Step 4: Penalty is DISABLED temporarily (pending OHLCV data quality fix)
# TODO: Re-enable penalty after fixing stock splits/dividends in OHLCV data
# Penalty logic is preserved but not applied
df['penalty'] = 1.0  # No penalty applied

# DISABLED: Apply 1M penalty only if below tolerance threshold
# df.loc[df['ret_1m'] < THRESHOLD_1M, 'penalty'] *= PENALTY_1M

# DISABLED: Apply 3M penalty only if below tolerance threshold
# df.loc[df['ret_3m'] < THRESHOLD_3M, 'penalty'] *= PENALTY_3M

# DISABLED: Crash protection - "falling knife" detection
# df.loc[df['ret_1m'] < CRASH_THRESHOLD, 'penalty'] *= CRASH_PENALTY
```

## Target State (Re-enabled)

```python
# Step 4: Apply penalty for downtrend stocks
df['penalty'] = 1.0  # Start with no penalty

# Apply 1M penalty only if below tolerance threshold
df.loc[df['ret_1m'] < THRESHOLD_1M, 'penalty'] *= PENALTY_1M

# Apply 3M penalty only if below tolerance threshold
df.loc[df['ret_3m'] < THRESHOLD_3M, 'penalty'] *= PENALTY_3M

# Crash protection - "falling knife" detection
df.loc[df['ret_1m'] < CRASH_THRESHOLD, 'penalty'] *= CRASH_PENALTY

# Step 5: Final RS Rating = rs_rating_raw * penalty
df['rs_rating'] = (df['rs_rating_raw'] * df['penalty']).round().clip(1, 99).astype(int)
```

## Penalty Parameters (Reference)

```python
# Constants from lines 51-63
PENALTY_1M = 0.85  # 15% penalty if 1M return < threshold
PENALTY_3M = 0.70  # 30% penalty if 3M return < threshold (broken trend = more severe)
# Combined penalty: 0.85 × 0.70 = 0.595 if both conditions met

# Tolerance thresholds - distinguish noise from real drops
THRESHOLD_1M = -2.0   # 1M return must be < -2% to trigger penalty
THRESHOLD_3M = -2.0   # 3M return must be < -2% to trigger penalty

# Crash protection
CRASH_THRESHOLD = -15.0  # If 1M drops > 15%, apply additional penalty
CRASH_PENALTY = 0.85     # Additional 15% penalty for crash
```

## Pre-condition: Data Quality Check

Before re-enabling penalty, verify OHLCV data is clean:

```python
def verify_data_quality(ohlcv_df: pd.DataFrame) -> bool:
    """
    Check OHLCV data quality before enabling penalty logic.

    Returns True if data is clean (no unadjusted splits).
    """
    df = ohlcv_df.copy()
    df['daily_return'] = df.groupby('symbol')['close'].pct_change()

    # Check for extreme returns (likely unadjusted splits)
    extreme_returns = df[df['daily_return'].abs() > 0.50]  # |return| > 50%

    if not extreme_returns.empty:
        logger.warning(f"Found {len(extreme_returns)} extreme returns (>50%):")
        for _, row in extreme_returns.head(10).iterrows():
            logger.warning(f"  {row['symbol']} on {row['date']}: {row['daily_return']*100:.1f}%")
        return False

    logger.info("✅ Data quality check passed: no extreme returns detected")
    return True
```

## Implementation Steps

### Step 1: Add Data Quality Gate

```python
def calculate_rs_rating(
    ohlcv_df: pd.DataFrame,
    sector_map: Optional[dict] = None,
    apply_penalty: bool = True,    # NEW parameter
    skip_quality_check: bool = False  # NEW parameter
) -> pd.DataFrame:
    """
    Calculate multi-period RS Rating for all stocks.

    Args:
        ...existing args...
        apply_penalty: If True, apply downtrend penalty (default: True)
        skip_quality_check: If True, skip data quality verification
    """
    # Data quality gate (can be skipped for performance)
    if apply_penalty and not skip_quality_check:
        if not verify_data_quality(ohlcv_df):
            logger.warning("Data quality check failed, disabling penalty")
            apply_penalty = False
```

### Step 2: Conditional Penalty Application

```python
# Step 4: Apply penalty for downtrend stocks (if enabled)
df['penalty'] = 1.0  # Start with no penalty

if apply_penalty:
    # Apply 1M penalty only if below tolerance threshold
    df.loc[df['ret_1m'] < THRESHOLD_1M, 'penalty'] *= PENALTY_1M

    # Apply 3M penalty only if below tolerance threshold
    df.loc[df['ret_3m'] < THRESHOLD_3M, 'penalty'] *= PENALTY_3M

    # Crash protection - "falling knife" detection
    df.loc[df['ret_1m'] < CRASH_THRESHOLD, 'penalty'] *= CRASH_PENALTY

    # Final RS Rating = rs_rating_raw * penalty
    df['rs_rating'] = (df['rs_rating_raw'] * df['penalty']).round().clip(1, 99).astype(int)
else:
    # No penalty
    df['rs_rating'] = df['rs_rating_raw'].clip(1, 99)
```

### Step 3: Update Logging

```python
# Log penalty statistics (only if penalty applied)
if apply_penalty:
    penalized_count = (df['penalty'] < 1.0).sum()
    crash_count = (df['ret_1m'] < CRASH_THRESHOLD).sum()
    logger.info(f"  Penalty applied: {penalized_count} stocks penalized, {crash_count} crash warnings")
else:
    logger.info("  Penalty DISABLED (data quality check failed or manually disabled)")
```

## Verification Script

Create verification script to run after OHLCV fix:

```python
# scripts/verify_rs_rating_penalty.py
"""
Verify RS Rating penalty logic works correctly after OHLCV fix.
"""
from PROCESSORS.technical.indicators.rs_rating import RSRatingCalculator, get_top_rs_stocks

def main():
    # Calculate RS Rating with penalty enabled
    calc = RSRatingCalculator()
    df = calc.calculate(apply_penalty=True)

    # Check penalty distribution
    penalty_applied = (df['penalty'] < 1.0).sum()
    total = len(df)

    print(f"Total stocks: {total}")
    print(f"Penalized: {penalty_applied} ({penalty_applied/total*100:.1f}%)")

    # Show top 10 with penalty applied
    print("\nTop 10 stocks (with penalty):")
    top10 = df.nlargest(10, 'rs_rating')[
        ['symbol', 'rs_1m', 'rs_3m', 'rs_rating', 'penalty', 'ret_1m', 'ret_3m']
    ]
    print(top10.to_string(index=False))

    # Show stocks most affected by penalty
    print("\nMost penalized stocks:")
    most_penalized = df.nsmallest(10, 'penalty')[
        ['symbol', 'rs_rating_raw', 'rs_rating', 'penalty', 'ret_1m', 'ret_3m']
    ]
    print(most_penalized.to_string(index=False))

if __name__ == "__main__":
    main()
```

## Success Criteria

- [ ] Data quality check passes (no |return| > 50%)
- [ ] Penalty logic re-enabled in production
- [ ] ~20-30% of stocks receive some penalty (normal market)
- [ ] CSV stock no longer shows +373.7% return
- [ ] Top RS stocks are genuinely in uptrends (visual verification)

## Rollback Plan

If issues found after re-enabling:
1. Set `apply_penalty=False` in daily pipeline
2. Run spike detector to find new problematic symbols
3. Fix OHLCV data
4. Re-enable penalty

## Deliverables

- [ ] Add `verify_data_quality()` function
- [ ] Add `apply_penalty` and `skip_quality_check` parameters
- [ ] Uncomment penalty logic (lines 146-152)
- [ ] Update penalty application to use new parameter
- [ ] Update logging to show penalty status
- [ ] Create verification script
- [ ] Run verification and confirm success
