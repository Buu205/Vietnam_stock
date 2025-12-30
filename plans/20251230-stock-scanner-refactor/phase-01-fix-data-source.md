# Phase 1: Fix Data Source

**Priority:** P0 (Critical)
**Status:** Pending
**Estimated Changes:** ~30 lines

## Problem (P3)

Service loads `*_latest.parquet` (1 day only) instead of `*_history.parquet` (9 days).
- "2 ngày gần nhất" filter shows only 29/12
- Date filter UI is misleading

## Root Cause

In `ta_dashboard_service.py`, `_load_signals()` uses:
```python
patterns_path = alert_dir / "patterns_latest.parquet"  # Only 1 day!
```

## Solution

Load history files instead of latest files.

## Data Verification

```bash
# History files have 9 days of data
patterns_history.parquet: 2143 rows, 9 unique dates
volume_spike_history.parquet: 731 rows, 9 dates
ma_crossover_history.parquet: 1049 rows, 9 dates
breakout_history.parquet: 132 rows, 9 dates
```

## File Changes

### `WEBAPP/pages/technical/services/ta_dashboard_service.py`

**Location:** `_load_signals()` function (line ~286)

**Change:** Replace `*_latest.parquet` with `*_history.parquet`

```python
# BEFORE
patterns_path = alert_dir / "patterns_latest.parquet"
ma_path = alert_dir / "ma_crossover_latest.parquet"
vol_path = alert_dir / "volume_spike_latest.parquet"
breakout_path = alert_dir / "breakout_latest.parquet"

# AFTER
patterns_path = alert_dir / "patterns_history.parquet"
ma_path = alert_dir / "ma_crossover_history.parquet"
vol_path = alert_dir / "volume_spike_history.parquet"
breakout_path = alert_dir / "breakout_history.parquet"
```

## Implementation Steps

- [ ] Open `ta_dashboard_service.py`
- [ ] Find `_load_signals()` function
- [ ] Replace 4 file paths: `*_latest.parquet` → `*_history.parquet`
- [ ] Test: Verify multiple dates appear in table

## Success Criteria

- [ ] Date filter "2 ngày gần nhất" shows 2 different dates
- [ ] Date filter "5 ngày" shows up to 5 different dates
- [ ] No import errors or data loading failures

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| History file missing | Fallback to latest file if history not exists |
| Performance (more data) | Date filter applied first to reduce rows |

## Fallback Code (Optional)

```python
# Safe loading with fallback
patterns_path = alert_dir / "patterns_history.parquet"
if not patterns_path.exists():
    patterns_path = alert_dir / "patterns_latest.parquet"
```
