# Brainstorm Report: OHLCV Adjustment Detection & Auto-Refresh

**Date:** 2025-12-23
**Status:** Agreed
**Topic:** Auto-detect dividend/split adjustments and refresh historical OHLCV data

---

## Problem Statement

- 450+ stocks in OHLCV data need monitoring for corporate actions (dividends, stock splits)
- When adjustment occurs, vnstock API returns adjusted prices but existing parquet has old prices
- Manual checking is impractical at scale
- Need automated detection and selective refresh

---

## Evaluated Approaches

### Approach A: Compare Old vs New Data (SELECTED)
**Logic:** Fetch recent 30 days from API, compare with stored data, flag symbols with significant diff

**Pros:**
- Detects ANY adjustment type (dividend, split, rights issue)
- Simple, reliable logic
- Fast check (~90s for 450 symbols)

**Cons:**
- Requires API calls for detection
- Minor false positives possible (mitigated by threshold)

### Approach B: Track Corporate Actions Events
**Logic:** Query corporate actions calendar from external source

**Pros:**
- Know in advance when adjustment happens
- More accurate

**Cons:**
- Need reliable corporate actions data source
- Vietnamese market data sources unreliable
- More complex implementation

---

## Final Agreed Solution

### Detection Algorithm

```python
FOR each symbol:
    1. Fetch 30 recent trading days from vnstock API
    2. Load same period from existing parquet
    3. Calculate: pct_diff = abs(new_close - old_close) / old_close * 100
    4. IF median(pct_diff) > 2.0% AND days_with_diff >= 10:
        → Add to refresh_list
```

### Refresh Process

```python
FOR each symbol in refresh_list:
    1. Delete symbol's history from parquet
    2. Fetch full history from API (2015 to present)
    3. Recalculate derived metrics (market_cap, trading_value)
    4. Append to parquet
```

### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Threshold** | 2.0% | Catches dividends (2-10%), avoids rounding noise |
| **Check window** | 30 days | Sufficient to confirm pattern |
| **Min days with diff** | 10 | Confirms systematic adjustment, not glitch |
| **History start** | 2015-01-01 | Match existing data range |

---

## Test Results (2024-12-23)

### Distribution Analysis (415 symbols scanned)

| Range | Count | Description |
|-------|-------|-------------|
| 0-0.1% | 276 | Perfect match - OK |
| 0.1-0.5% | 18 | Minor rounding |
| 0.5-1% | 7 | Small diff |
| 1-2% | 15 | Possible small dividend |
| **2-5%** | **42** | Likely dividend |
| **5-10%** | **27** | Significant adjustment |
| **10-20%** | **19** | Large adjustment |
| **20-50%** | **9** | Major corporate action |
| **>50%** | **1** | Stock split (VIC) |

### Symbols Needing Refresh (threshold 2.0%)

**99 symbols identified**, including:
- VIC (50%), BIC (43%), BSR (38%), CTG (31%), HDB (22%)
- POW (17%), SSI (11%), TPB (4.7%), VNM (4.6%)
- And 90 more...

### Estimated Runtime

- Detection phase: ~90 seconds (450 symbols × 0.2s)
- Refresh phase: ~5 minutes (99 symbols × 3s)
- Total: ~6-7 minutes

---

## Implementation Plan

### Script Location
`PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py`

### Features
1. **detect mode**: Scan all symbols, report which need refresh
2. **refresh mode**: Actually refresh flagged symbols
3. **dry-run mode**: Show what would be refreshed without doing it
4. **force mode**: Refresh specific symbols regardless of threshold

### CLI Interface
```bash
# Detect only (report)
python ohlcv_adjustment_detector.py --detect

# Detect and refresh
python ohlcv_adjustment_detector.py --detect --refresh

# Force refresh specific symbols
python ohlcv_adjustment_detector.py --refresh --symbols VIC,CTG,HDB

# Dry run
python ohlcv_adjustment_detector.py --detect --refresh --dry-run
```

### Integration with Existing Code
- Reuse `OHLCVDailyUpdater` for API calls and data handling
- Same output format to `DATA/raw/ohlcv/OHLCV_mktcap.parquet`
- Same derived metrics calculation (shares_outstanding, market_cap)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| API rate limit | 0.1s delay between calls, tested OK |
| False positives | 2% threshold + 10 days minimum |
| Data loss during refresh | Backup parquet before refresh |
| API downtime | Retry logic with exponential backoff |

---

## Success Metrics

1. Zero manual intervention needed for dividend adjustments
2. Detection accuracy >95% (validate against known corporate actions)
3. Full refresh completes in <10 minutes
4. No data gaps after refresh

---

## Next Steps

1. [ ] Implement `ohlcv_adjustment_detector.py` based on this spec
2. [ ] Run initial full refresh for 99 identified symbols
3. [ ] Set up weekly cron/manual trigger
4. [ ] Monitor and tune threshold if needed

---

## Appendix: Full Detection Results

See `/tmp/ohlcv_adjustment_check.csv` for complete symbol-by-symbol analysis.

Top 30 symbols by median_diff:
```
PMC (100%), VIC (50%), BIC (43%), BSR (38%), KLB (37%)
CTG (31%), STK (31%), ABI (28%), PGB (23%), ECO (23%)
HDB (22%), DSC (19%), SCL (18%), VEF (17%), IJC (17%)
POW (17%), MSB (16%), CDC (16%), CKA (13%), VTR (13%)
NHA (13%), TNH (13%), PC1 (13%), PTB (12%), BMI (11%)
VEA (11%), SSI (11%), HDC (10%), TLG (10%), SJD (10%)
```
