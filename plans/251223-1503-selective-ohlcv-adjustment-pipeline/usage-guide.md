# OHLCV Adjustment Pipeline - Usage Guide

## Quick Start

```bash
# RECOMMENDED: Detect, refresh, and selective cascade (10x faster)
python PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py \
  --detect --refresh --cascade-selective

# Force specific symbols with selective cascade
python PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py \
  --symbols CTG,HDB,POW --refresh --cascade-selective
```

---

## Commands Overview

### Detection Only

```bash
# Detect which symbols need OHLCV refresh
python PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py --detect

# Save detection results to CSV
python PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py \
  --detect --output detection_results.csv
```

### Detection + Refresh

```bash
# Detect and refresh (no TA cascade)
python PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py --detect --refresh

# Dry run (show what would be done)
python PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py \
  --detect --refresh --dry-run
```

### Full Pipeline (Recommended)

```bash
# RECOMMENDED: Selective cascade (only affected symbols)
python PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py \
  --detect --refresh --cascade-selective

# Legacy: Full cascade (all 458 symbols - slow)
python PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py \
  --detect --refresh --cascade
```

### Force Specific Symbols

```bash
# Force refresh specific symbols
python PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py \
  --symbols CTG,HDB,POW --refresh --cascade-selective

# No detection, just refresh + cascade
python PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py \
  --symbols CTG --refresh --cascade-selective
```

---

## Parameters

| Flag | Description |
|------|-------------|
| `--detect` | Run detection phase (compare stored vs API prices) |
| `--refresh` | Run refresh phase (fetch full history for flagged symbols) |
| `--cascade-selective` | **RECOMMENDED** - Selective TA cascade for affected symbols only |
| `--cascade` | Full TA cascade for ALL 458 symbols (legacy, slow) |
| `--symbols <list>` | Comma-separated symbols to force refresh |
| `--dry-run` | Show what would be done without doing it |
| `--threshold <pct>` | Detection threshold % (default: 2.0) |
| `--output <file>` | Save detection results to CSV |

---

## Pipeline Flow

```
--detect --refresh --cascade-selective
     │
     ├─► [Step 1] Detection
     │   └── Compare stored OHLCV vs API prices
     │   └── Flag symbols with median diff > 2%
     │
     ├─► [Step 2] OHLCV Refresh
     │   └── Fetch full history from vnstock API
     │   └── Atomic update to OHLCV_mktcap.parquet
     │
     └─► [Step 3] Selective Cascade (only affected symbols)
         ├── [3.1] Technical indicators → basic_data.parquet
         ├── [3.2] Alerts → alerts/daily/*.parquet
         ├── [3.3] Money flow → money_flow/individual_money_flow.parquet
         ├── [3.4] Market breadth (full recalc - needs all symbols)
         └── [3.5] BSC MCP cache invalidation marker
```

---

## Performance Comparison

| Metric | `--cascade` (Full) | `--cascade-selective` |
|--------|-------------------|----------------------|
| Symbols processed | 458 | ~20 (typical) |
| Runtime | ~180s | ~15s |
| Memory | ~880 MB | ~18 MB |
| Improvement | - | **91% faster** |

---

## Verification Commands

### Check Detection Results

```bash
# View symbols flagged for refresh
python PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py --detect
```

### Verify Data After Refresh

```python
import pandas as pd

# Check OHLCV
df = pd.read_parquet('DATA/raw/ohlcv/OHLCV_mktcap.parquet')
print(f"Total symbols: {df.symbol.nunique()}")
print(df[df.symbol == 'CTG'].tail(5))

# Check technical indicators
df = pd.read_parquet('DATA/processed/technical/basic_data.parquet')
print(f"Total rows: {len(df)}")
print(df[df.symbol.isin(['CTG','HDB'])].groupby('symbol').size())
```

### BSC MCP Verification

```bash
# Check cache invalidation marker
ls -la DATA/.cache_invalidated

# Query via BSC MCP (in Claude Code with BSC MCP connected)
# bsc_get_ohlcv_raw("CTG")
# bsc_get_technical_indicators("CTG")
```

---

## Troubleshooting

### "No API data" Error

- Check internet connection
- vnstock API might be rate limited - wait and retry
- Symbol might be delisted

### "Insufficient stored data" Warning

- Symbol has < 10 days of historical data
- Normal for newly listed stocks

### Cache Not Invalidating

- Check `DATA/.cache_invalidated` marker exists
- Restart BSC MCP server if needed

---

## Files Modified

| File | Changes |
|------|---------|
| `PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py` | Added `--cascade-selective` flag, selective cascade method |
| `PROCESSORS/technical/indicators/technical_processor.py` | Added `calculate_selective_indicators()`, `atomic_merge_basic_data()` |
| `PROCESSORS/technical/indicators/alert_detector.py` | Added `symbols` param, `merge_alerts_selective()` |
| `PROCESSORS/technical/indicators/money_flow.py` | Added `symbols` param, `atomic_merge_money_flow()` |
| `MCP_SERVER/bsc_mcp/services/data_loader.py` | Added `get_ohlcv_raw()`, cache invalidation marker support |
| `MCP_SERVER/bsc_mcp/tools/technical_tools.py` | Updated `bsc_get_ohlcv_raw()` to use raw OHLCV |

---

## Integration with Daily Pipeline

Add to your daily cron/scheduler:

```bash
# Morning run: detect and fix dividend/split adjustments
python PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py \
  --detect --refresh --cascade-selective

# Or as part of full daily update
python PROCESSORS/daily_sector_complete_update.py
```

---

## Related Documentation

- [Plan Overview](plan.md)
- [Phase 01: TechnicalProcessor](phase-01-technical-processor-selective.md)
- [Phase 02: Alert + MoneyFlow](phase-02-alert-moneyflow-selective.md)
- [Phase 03: Orchestrator](phase-03-orchestrator.md)
- [Phase 04: BSC MCP](phase-04-bsc-mcp-data-source.md)
