# Phase 2: Integration with Adjustment Detector

**File:** `PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py`
**Effort:** 2h
**Dependencies:** Phase 1 (spike detector)

## Objective

Extend existing `ohlcv_adjustment_detector.py` to use spike detection as an additional trigger for OHLCV refresh, alongside the existing median-diff method.

## Current Detection Method (Preserve)

```python
# Line 76-78: Existing parameters
THRESHOLD_PCT = 2.0          # Median diff threshold (%)
MIN_DAYS_WITH_DIFF = 10      # Minimum days with significant diff
CHECK_WINDOW_DAYS = 35       # Days to fetch for comparison
```

The existing detector compares stored OHLCV vs fresh API data over 30 days. If median diff > 2%, it flags for refresh. **This works well for recent adjustments but misses historical issues.**

## New Detection Method (Add)

Add spike-based detection to catch historical issues that median-diff misses:

```python
class OHLCVAdjustmentDetector:
    # NEW: Add spike detection integration

    def detect_spikes(self, lookback_days: int = 365) -> List[Dict]:
        """
        Detect historical spikes in stored OHLCV data.

        Returns list of {symbol, date, spike_type, needs_refresh}
        """
        from PROCESSORS.technical.ohlcv.ohlcv_spike_detector import OHLCVSpikeDetector

        detector = OHLCVSpikeDetector(self.existing_df)
        spikes = detector.scan_all_symbols(lookback_days=lookback_days)

        return spikes

    def get_symbols_needing_refresh(
        self,
        use_spike_detection: bool = True,
        use_median_diff: bool = True
    ) -> List[str]:
        """
        Combine both detection methods to get full list of symbols needing refresh.
        """
        symbols = set()

        if use_spike_detection:
            spikes = self.detect_spikes()
            symbols.update([s['symbol'] for s in spikes if s['needs_refresh']])

        if use_median_diff:
            diff_results = self.detect_all()
            symbols.update(diff_results[diff_results['needs_refresh']]['symbol'].tolist())

        return sorted(list(symbols))
```

## CLI Extension

```python
# Add new arguments to argparse
parser.add_argument('--spike-detect', action='store_true',
    help='Run spike detection in addition to median-diff detection')
parser.add_argument('--spike-only', action='store_true',
    help='Only use spike detection (skip median-diff)')
parser.add_argument('--lookback', type=int, default=365,
    help='Lookback days for spike detection (default: 365)')
```

**Usage Examples:**

```bash
# Original behavior (unchanged)
python ohlcv_adjustment_detector.py --detect --refresh --cascade-selective

# NEW: With spike detection
python ohlcv_adjustment_detector.py --detect --spike-detect --refresh --cascade-selective

# NEW: Spike-only mode (for historical audit)
python ohlcv_adjustment_detector.py --spike-only --lookback 730 --output spikes.csv
```

## Integration Flow

```
┌──────────────────────────────────────────────────────────────┐
│ CLI: python ohlcv_adjustment_detector.py                     │
│        --detect --spike-detect --refresh --cascade-selective │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 1: Spike Detection (if --spike-detect)                  │
│ - Load stored OHLCV                                          │
│ - Calculate Z-score for all symbols                          │
│ - Identify spikes with |Z| > 3.0                             │
│ - Classify as SPLIT/DIVIDEND/UNKNOWN                         │
│ - Output: spike_flagged_symbols[]                            │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 2: Median-Diff Detection (existing)                     │
│ - For each symbol, fetch 35 days from API                    │
│ - Compare with stored data                                   │
│ - Flag if median_diff > 2%                                   │
│ - Output: diff_flagged_symbols[]                             │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 3: Combine & Deduplicate                                │
│ refresh_symbols = spike_flagged ∪ diff_flagged               │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 4: Refresh (existing)                                   │
│ - Backup parquet                                             │
│ - For each symbol: delete old → fetch full history           │
│ - Save updated parquet                                       │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 5: Cascade Selective (existing)                         │
│ - Recalc technical indicators for refreshed symbols only     │
│ - Recalc alerts, money flow                                  │
│ - Recalc market breadth (full)                               │
│ - Create cache invalidation marker                           │
└──────────────────────────────────────────────────────────────┘
```

## Modified `run()` Method

```python
def run(
    self,
    detect: bool = True,
    refresh: bool = False,
    symbols: Optional[List[str]] = None,
    dry_run: bool = False,
    threshold: Optional[float] = None,
    cascade: bool = False,
    cascade_selective: bool = False,
    # NEW parameters
    spike_detect: bool = False,
    spike_only: bool = False,
    lookback: int = 365
) -> Dict:
    """
    Run detection and/or refresh.

    Args:
        ...existing args...
        spike_detect: Also run spike detection (combines with median-diff)
        spike_only: Only use spike detection (skips median-diff)
        lookback: Days to look back for spike detection
    """
```

## Test Scenarios

| Scenario | Expected Behavior |
|----------|-------------------|
| `--detect` only | Unchanged (median-diff only) |
| `--detect --spike-detect` | Both methods, union of results |
| `--spike-only` | Only spike detection, no API calls |
| `--symbols CSV --refresh` | Force refresh specific symbol |

## Deliverables

- [ ] Import `OHLCVSpikeDetector` in adjustment detector
- [ ] Add `detect_spikes()` method
- [ ] Add `get_symbols_needing_refresh()` combining methods
- [ ] Add CLI flags: `--spike-detect`, `--spike-only`, `--lookback`
- [ ] Update `run()` method signature
- [ ] Preserve all existing functionality (backward compatible)
