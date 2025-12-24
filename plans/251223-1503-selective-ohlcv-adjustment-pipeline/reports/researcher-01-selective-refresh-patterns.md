# Research Report: Selective Data Refresh Patterns for Time-Series Financial Data

**Date:** 2025-12-23
**Research Period:** July 2025 – December 2025
**Status:** Comprehensive findings with actionable recommendations

---

## Executive Summary

Parquet files cannot be selectively updated in-place; **append-only is the only safe pattern**. For financial time-series with selective symbol refreshes, adopt one of two architectures:

1. **Partition by symbol** (recommended for <1000 symbols): Rewrite only affected symbol partitions, leaving others untouched
2. **Delta Lake migration** (recommended for production systems): Provides ACID upserts, change tracking, and incremental recalculation without file rewrites

Rolling indicators (SMA, RSI, MACD) **require historical context** and cannot be computed independently; recalculate affected symbol with full historical lookback (minimum 200 days for MA200), then merge selectively back into parquet.

---

## Key Findings

### 1. Parquet File Update Limitation

**Critical constraint:** PyArrow and fastparquet cannot modify existing rows in parquet files. The standard approach is rewrite-entire-file.

**Safe patterns:**
- Fastparquet supports append-mode (adds new rows to file structure)
- PyArrow requires manual merge: read → filter → update → write
- No in-place row modification possible

**For 458 symbols:** Full rewrites cost ~5-10s per run. Selective rewrites cost ~100-500ms per symbol.

### 2. Partitioning Strategy for Selective Updates

**Recommend: Partition by symbol column**

```
DATA/processed/technical/ohlcv_by_symbol/
├── symbol=ACB/
│   ├── part-0.parquet (2025-01-01 → 2025-12-23)
│   └── .parquet.crc
├── symbol=VCB/
│   ├── part-0.parquet
│   └── .parquet.crc
└── ... (458 symbols)
```

**Benefits:**
- Read single symbol partition (99% I/O reduction for selective updates)
- Rewrite only affected symbol directory, leave others untouched
- Compression improves: same symbol = higher entropy reduction (~33% smaller files per research)
- Partition pruning at read-time (arrow automatically filters partitions)

**Cardinality consideration:** 458 symbols is high-cardinality but manageable. Each symbol file ~5-20MB (depending on date range), resulting in balanced I/O.

**File sizing:** Target 128MB–1GB per partition. With ~5 years of daily OHLCV data per symbol (~250KB per day × 1250 days = 312MB), single-file-per-symbol works well.

### 3. Selective Recalculation Pattern

**Problem:** Rolling indicators (SMA20, RSI14, MACD) depend on 20-200 historical bars.

**Solution:** Recalculate with full context, then merge selectively

```python
# Step 1: Load affected symbol with full history (minimum 200 bars)
symbol = 'VCB'
full_data = pd.read_parquet(
    f"DATA/processed/technical/ohlcv_by_symbol/symbol={symbol}/",
    columns=['date', 'close', 'volume']
)

# Step 2: Recalculate ALL rolling indicators (can't do partial)
full_data['sma20'] = full_data['close'].rolling(20).mean()
full_data['rsi14'] = calc_rsi(full_data['close'], 14)

# Step 3: Merge only updated rows back
updated_rows = full_data[full_data['date'] >= adjustment_date]
existing = read_existing_file(symbol)
merged = pd.concat([existing, updated_rows]).drop_duplicates('date', keep='last')

# Step 4: Write back to symbol partition
merged.to_parquet(f"DATA/processed/technical/ohlcv_by_symbol/symbol={symbol}/")
```

**Key insight:** Lookback requirement = max(window_size across all indicators). For your indicators:
- SMA200 requires 200 bars
- RSI14 requires 14 bars (typically safe after 50)
- MACD requires 26 bars (typically safe after 100)
- **Minimum lookback: 200 days** to be conservative

### 4. Update Safety & Consistency

**Race condition risk:** If reads happen during write, readers get partial data.

**Mitigations:**
1. **Atomic rename** (preferred): Write to `symbol=VCB.tmp/`, then atomic rename to `symbol=VCB/`
2. **Write-ahead log:** Store transaction metadata in JSON, replay on failure
3. **Version metadata:** Store update timestamp in parquet footer statistics

**Data consistency:** Partitioned structure guarantees symbol-level consistency. Cross-symbol queries unaffected if single-symbol updates fail.

### 5. Delta Lake Alternative (Production Path)

If moving beyond pandas-only scripts:

**Delta Lake advantages:**
- ACID upsert: `MERGE INTO target USING source ON condition WHEN MATCHED THEN UPDATE`
- Change Data Feed: Track exact rows changed (enables incremental downstream recalculation)
- No small-file problem (automatic compaction)
- Time travel (rollback corrupt data to yesterday's version)

**Example upsert:**
```sql
MERGE INTO delta_ohlcv t
USING updated_symbols s
ON t.symbol = s.symbol AND t.date = s.date
WHEN MATCHED THEN UPDATE SET t.close = s.close, t.sma20 = s.sma20
WHEN NOT MATCHED THEN INSERT *
```

---

## Implementation Roadmap

### Phase 1: Partition Existing Data (No Logic Change)
1. Read full technical parquet
2. Repartition by symbol using `groupby().apply()`
3. Write to `DATA/processed/technical/ohlcv_by_symbol/symbol=X/` structure
4. Run read-validation tests (verify sums match original)

### Phase 2: Adjust OHLCV Detector Pipeline
1. Detect adjustments (current logic unchanged)
2. For each adjusted symbol:
   - Read partition with 200-day lookback
   - Recalculate all rolling indicators (rescan full history)
   - Write merged result back to partition
3. Skip full cascade refresh

### Phase 3: Incremental Recalculation Service
1. Expose symbol update list as dependency
2. Valuation calculator: only process adjusted symbols
3. Macro/commodity: remain unchanged (no per-symbol recalculation)

### Phase 4: Delta Lake Migration (Optional, 6+ months out)
- Only if concurrent updates or audit trail required
- Backward compatible with existing parquet pipelines

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|-----------|
| **Stale data in concurrent reads** | Medium | Write to `.tmp`, atomic rename before releasing locks |
| **Lookback insufficient for rolling calcs** | Low | Use 200-day minimum; validate first 20 rows = NaN |
| **Partition explosion** | Low | Monitor file count; consolidate symbols quarterly if needed |
| **Cross-symbol joins fail** | Low | Partitioning transparent to pandas; no code change needed |
| **Merge conflicts on overlapping dates** | Medium | Use `keep='last'` in concat; validate no duplicates after merge |

---

## Unresolved Questions

1. **How many symbols get adjustments per month?** (impacts cost-benefit of selective vs. full refresh)
2. **Are there cross-symbol dependencies** in valuation calcs (sector PE, market breadth)?
3. **Read-only or read-write concurrent access?** (affects atomic rename strategy)
4. **Budget for Delta Lake migration?** (requires PySpark cluster vs. pandas-only)

---

## Sources

- [Incremental Data Load into Parquet Files from Python – Curated SQL](https://curatedsql.com/2025/07/18/incremental-data-load-into-parquet-files-from-python/)
- [Incremental Data Loading with Apache Spark - Medium](https://joydipnath.medium.com/incremental-data-loading-with-apache-spark-concept-with-special-parquet-file-feature-of-increment-ebaa89897cff)
- [Efficient Data Management with Partitioned Parquet Files - Medium](https://medium.com/@sandeeparikarevula/efficient-data-management-with-partitioned-parquet-files-a-daily-data-append-and-cleanup-strategy-3aabe6e5df13)
- [All About Parquet Part 10 — Performance Tuning and Best Practices - Medium](https://medium.com/data-engineering-with-dremio/all-about-parquet-part-10-performance-tuning-and-best-practices-with-parquet-d697ba4e8a57)
- [Delta Lake vs. Parquet Comparison - Delta Lake](https://delta.io/blog/delta-lake-vs-parquet-comparison/)
- [Delta Lake Change Data Feed (CDF) - Delta Lake](https://delta.io/blog/2023-07-14-delta-lake-change-data-feed-cdf/)
- [Delta Lake Upsert - Delta Lake](https://delta.io/blog/delta-lake-upsert/)
- [Understanding Pandas Rolling - Medium](https://medium.com/@whyamit101/understanding-pandas-rolling-f8f6d6796c07/)
- [Pandas DataFrame.rolling Documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html)
- [Parquet Partitioning Best Practices - CLIMB](https://climbtheladder.com/10-parquet-partitioning-best-practices/)
