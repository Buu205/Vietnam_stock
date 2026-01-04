---
title: "Fix OHLCV Data Quality for Corporate Actions"
description: "Detect and fix stock splits/dividends causing >7% daily price spikes, re-enable RS Rating penalty"
status: pending
priority: P1
effort: 8h
branch: main
tags: [ohlcv, data-quality, corporate-actions, rs-rating]
created: 2026-01-04
---

# Fix OHLCV Data Quality for Corporate Actions

## Context

CSV stock showed +373.7% daily return on 2025-06-04 due to unadjusted stock split. This distorts RS Rating calculations, forcing penalty logic to be disabled (lines 140-156 in `rs_rating.py`).

## Problem Analysis

| Issue | Root Cause | Impact |
|-------|------------|--------|
| Extreme returns (>50%) | Unadjusted stock splits | RS Rating distortion |
| False downtrend signals | Unadjusted dividends | Penalty logic disabled |
| API vs stored mismatch | vnstock returns adjusted prices, stored data stale | 2%+ median diff detection |

## Solution Overview

**Two-pronged approach:**
1. **Exchange Limit Detection (PRIMARY)**: Any |daily_return| > 7% (HOSE) / 10% (HNX) / 15% (UPCOM) = 100% guaranteed corporate action → auto-refresh
2. **Z-score Detection (SECONDARY)**: For edge cases near limits (5-7%) + split ratio classification
3. **Reactive Fix**: Extend `ohlcv_adjustment_detector.py` with spike-based refresh trigger

## Vietnam Exchange Limits (KEY INSIGHT)

```python
EXCHANGE_LIMITS = {
    'HOSE': 0.07,    # ±7% - Most stocks
    'HNX': 0.10,     # ±10%
    'UPCOM': 0.15,   # ±15%
}
# If |daily_return| > limit → GUARANTEED unadjusted corporate action
# Zero false positives - this is a hard market constraint
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ OHLCV Spike Detector (NEW)                                  │
│ - Exchange Limit: |return| > 7% = 100% corporate action     │
│ - Z-score (edge cases): |Z| > 3.0, 20-day window            │
│ - Split Ratio: prev_close/curr_open > 1.5                   │
└────────────────────────┬────────────────────────────────────┘
                         │ Flagged symbols
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ OHLCV Adjustment Detector (EXISTING)                        │
│ - Compare stored vs API (already implemented)               │
│ - Cascade selective refresh (already implemented)           │
└────────────────────────┬────────────────────────────────────┘
                         │ Refreshed symbols
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ RS Rating Calculator                                         │
│ - Re-enable penalty logic after data fix                    │
└─────────────────────────────────────────────────────────────┘
```

## Key Insights from Research

1. **vnstock_data already provides adjusted prices** - API returns adjusted OHLCV, just need full refresh
2. **Z-score method preferred** for spike detection (|Z| > 3.0, handles volatility)
3. **Split ratio patterns**: 2:1 (-50%), 5:1 (-80%), 10:1 (-90%)
4. **No corporate actions API** - must detect algorithmically or maintain manual CSV

## Implementation Phases

### Phase 1: Spike Detector Module (3h)
**File:** `PROCESSORS/technical/ohlcv/ohlcv_spike_detector.py`
- **Exchange Limit Detection (PRIMARY)**: |return| > 7%/10%/15% = auto-flag for refresh
- Z-score calculation (SECONDARY for edge cases 5-7%)
- Split ratio detection (prev_close/curr_open > 1.5)
- Output: List of (symbol, date, spike_type, ratio) + auto-refresh for limit breaches

### Phase 2: Integration with Adjustment Detector (2h)
**File:** `PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py`
- Add `--spike-detect` flag to run spike detection first
- Pass spike-flagged symbols to existing `detect_adjustment()` logic
- Combine spike-triggered + median-diff-triggered symbols for refresh

### Phase 3: Corporate Actions Registry (1h)
**File:** `DATA/processed/metadata/corporate_actions.csv`
- Schema: `ticker,date,action_type,ratio,verified`
- Populate with known splits (CSV, CTG, etc.)
- Allow detector to skip manual review for verified actions

### Phase 4: Re-enable RS Rating Penalty (2h)
**File:** `PROCESSORS/technical/indicators/rs_rating.py`
- Uncomment penalty logic (lines 146-152)
- Add data quality check before applying penalty
- Test with cleaned OHLCV data

## Related Files

| File | Role |
|------|------|
| `PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py` | Existing detector (extend) |
| `PROCESSORS/technical/ohlcv/ohlcv_daily_updater.py` | API fetch logic (reuse) |
| `PROCESSORS/technical/indicators/rs_rating.py` | Penalty logic (re-enable) |
| `DATA/raw/ohlcv/OHLCV_mktcap.parquet` | OHLCV data (fix target) |

## Success Criteria

- [ ] CSV stock +373.7% spike detected and corrected
- [ ] **No stocks with |daily_return| > 7%** (HOSE limit - guaranteed corporate action)
- [ ] RS Rating penalty logic re-enabled
- [ ] Detection runs in <5 min for 458 symbols

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| False positives (real 15% drops flagged) | Volume spike confirmation required |
| vnstock API rate limit | Existing 0.05s delay, increase if needed |
| Cascade refresh too slow | Use `--cascade-selective` (10x faster) |

## Unresolved Questions

1. Should spike detector run daily as part of pipeline or on-demand only?
2. Tolerance for corporate_actions.csv maintenance burden?
3. Historical lookback period for initial spike scan (1 year vs all history)?
