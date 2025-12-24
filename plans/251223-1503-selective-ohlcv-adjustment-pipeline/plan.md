# Selective OHLCV Adjustment Pipeline

**Date:** 2025-12-23
**Status:** Completed
**Priority:** High

---

## Problem Statement

Khi cổ phiếu chia cổ tức/split:
1. vnstock API trả về giá đã điều chỉnh (adjusted prices)
2. Stored OHLCV có giá cũ → sai lệch với API
3. Cần refresh OHLCV + recalc tất cả TA indicators liên quan
4. BSC MCP cần đọc được data mới nhất

**Current Issue:** `--cascade` flag chạy FULL pipeline (458 symbols) dù chỉ 10-20 symbols cần update.

---

## Solution: Unified Selective Pipeline

Tích hợp vào `ohlcv_adjustment_detector.py` với selective mode:

```bash
# Full pipeline (detect → refresh OHLCV → selective TA update)
python ohlcv_adjustment_detector.py --detect --refresh --cascade-selective

# Force specific symbols
python ohlcv_adjustment_detector.py --symbols CTG,HDB --refresh --cascade-selective
```

---

## Pipeline Flow

```
ohlcv_adjustment_detector.py --detect --refresh --cascade-selective
        │
        ├── [Step 1] Detect: Compare stored vs API prices
        │   └── Output: List of affected symbols (e.g., CTG, HDB, POW)
        │
        ├── [Step 2] Refresh OHLCV: Fetch full history for affected symbols
        │   └── Update OHLCV_mktcap.parquet (atomic write)
        │
        ├── [Step 3] Selective TA Update:
        │   ├── TechnicalProcessor: Recalc indicators for affected symbols only
        │   ├── AlertDetector: Recalc alerts for affected symbols only
        │   ├── MoneyFlowAnalyzer: Recalc money flow for affected symbols only
        │   └── MarketBreadth: Always FULL recalc (% calculations need all)
        │
        ├── [Step 4] Atomic Merge: Update parquet files preserving other symbols
        │
        └── [Step 5] Verify: Confirm data consistency
```

---

## Phases

| Phase | Description | File |
|-------|-------------|------|
| 01 | TechnicalProcessor selective mode | [phase-01](phase-01-technical-processor-selective.md) |
| 02 | AlertDetector + MoneyFlow selective | [phase-02](phase-02-alert-moneyflow-selective.md) |
| 03 | Orchestrator integration | [phase-03](phase-03-orchestrator.md) |
| 04 | BSC MCP data source update | [phase-04](phase-04-bsc-mcp-data-source.md) |

---

## Files Changed

| File | Change | Purpose |
|------|--------|---------|
| `technical_processor.py` | Add `symbols` param + atomic merge | Selective TA calc |
| `alert_detector.py` | Add `symbols` param | Selective alerts |
| `money_flow.py` | Add `symbols` param | Selective money flow |
| `ohlcv_adjustment_detector.py` | Add `--cascade-selective` | Orchestration |
| `bsc_mcp/services/data_loader.py` | Add raw OHLCV reader | BSC MCP direct access |

---

## Performance Gains

| Metric | Full Cascade | Selective | Improvement |
|--------|--------------|-----------|-------------|
| Symbols processed | 458 | 20 (typical) | 95% fewer |
| Runtime | ~180s | ~15s | 91% faster |
| Memory | ~880 MB | ~18 MB | 98% less |

---

## BSC MCP Data Source

**Current:** BSC MCP reads `basic_data.parquet` (processed)
**Issue:** After OHLCV refresh, need to regenerate basic_data.parquet

**Solution (Phase 04):**
1. Add `get_ohlcv_raw()` method to DataLoader for direct OHLCV access
2. After selective update, basic_data.parquet is auto-updated
3. BSC MCP always reads latest data

---

## Success Criteria

- [x] Single command runs full pipeline
- [x] Only affected symbols processed (91% speedup)
- [x] basic_data.parquet preserves non-affected data
- [x] BSC MCP reads correct updated data
- [x] Zero data corruption (atomic writes)
- [x] Validation confirms data consistency

## Usage Guide

See [usage-guide.md](usage-guide.md) for complete documentation.

---

## Related Documents

- [Research: Selective Patterns](reports/researcher-01-selective-refresh-patterns.md)
- [Research: TA Recalculation](research/researcher-02-ta-recalculation.md)
