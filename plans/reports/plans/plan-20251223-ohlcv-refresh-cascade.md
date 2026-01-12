# Plan: OHLCV Refresh Cascade - BSC MCP Data Consistency

**Date:** 2025-12-23
**Status:** Planning
**Topic:** How to handle dividend/split-adjusted OHLCV and cascade to all derived data

---

## Problem Statement

Khi cổ phiếu chia cổ tức/split:
1. ✅ vnstock API trả về giá đã điều chỉnh
2. ✅ `ohlcv_adjustment_detector.py` detect và refresh OHLCV raw data
3. ❌ **Vấn đề:** Các chỉ số kỹ thuật (MA, RSI, MACD...) được tính từ data cũ vẫn lưu trong parquet
4. ❌ **Vấn đề:** BSC MCP đọc từ `basic_data.parquet` (processed) - không cập nhật

---

## Data Flow Analysis

```
OHLCV_mktcap.parquet (RAW - adjusted prices)
        │
        ▼
TechnicalProcessor.run_full_processing()
        │
        ├── basic_data.parquet ◀── BSC MCP reads here
        │
        ├── Alerts (MA crossover, breakout, patterns)
        │
        ├── Money Flow (individual + sector)
        │
        └── Market/Sector Breadth

Valuation Pipeline:
OHLCV_mktcap.parquet
        │
        ├── PE/PB/PS/EV-EBITDA calculators
        │
        └── Sector valuation parquets
```

---

## Impact of Dividend Adjustment

Khi cổ phiếu CTG chia cổ tức (ví dụ 10%):
- Giá close cũ: 25,000
- Giá close mới (adjusted): 22,500

**Ảnh hưởng:**
1. **SMA/EMA**: Giá trị MA cũ (từ data cũ) sai so với giá mới
2. **RSI**: Momentum calculation bị lệch
3. **MACD**: Signal line sai
4. **Bollinger Bands**: Bands bị lệch
5. **Market cap**: Vẫn đúng (shares * price được điều chỉnh đồng bộ)
6. **PE/PB ratios**: Không ảnh hưởng (earnings/book value không đổi)

---

## Solution Options

### Option A: Full Cascade Refresh (RECOMMENDED)

**Logic:** Khi refresh OHLCV → cascade refresh tất cả derived data

```python
# After ohlcv_adjustment_detector.py runs:
1. Refresh OHLCV for flagged symbols
2. Run TechnicalProcessor.run_full_processing(n_sessions=500)
3. Run all alert detectors
4. Run money flow analyzers
5. (Optional) Run valuation recalculation
```

**Pros:**
- Data consistency 100%
- Simple to implement (chạy lại existing pipelines)

**Cons:**
- Chậm (~5-10 phút cho full cascade)
- Overhead nếu chỉ 1-2 symbols cần refresh

### Option B: Selective Symbol Refresh

**Logic:** Chỉ recalculate cho symbols đã bị refresh

```python
def refresh_technical_for_symbols(symbols: List[str]):
    """Only recalculate technical indicators for specific symbols."""
    ohlcv_df = load_ohlcv(symbols_filter=symbols)
    tech_df = calculate_indicators(ohlcv_df)

    # Update basic_data.parquet (merge/replace for symbols)
    existing = pd.read_parquet("basic_data.parquet")
    existing = existing[~existing['symbol'].isin(symbols)]
    combined = pd.concat([existing, tech_df])
    combined.to_parquet("basic_data.parquet")
```

**Pros:**
- Nhanh hơn (chỉ process symbols bị ảnh hưởng)
- Resource efficient

**Cons:**
- Complex merge logic
- Risk of data inconsistency

### Option C: BSC MCP Read from Raw OHLCV

**Logic:** Add option cho BSC MCP tools đọc trực tiếp từ OHLCV raw

```python
# In bsc_mcp/services/data_loader.py
def get_ohlcv_raw(self, ticker: str, limit: int = 30) -> pd.DataFrame:
    """Read directly from raw OHLCV parquet."""
    df = pd.read_parquet(self.raw_ohlcv_path)
    df = df[df['symbol'] == ticker].tail(limit)
    return df
```

**Pros:**
- Luôn có data mới nhất
- Không cần chờ pipeline chạy

**Cons:**
- Mất các chỉ số technical (MA, RSI, MACD...)
- User phải tự tính indicators

---

## Recommended Solution: Hybrid Approach

### Phase 1: Immediate (Option A)
```bash
# After running adjustment detector with --refresh:
python3 PROCESSORS/pipelines/daily/daily_ta_complete.py --sessions 500
```

### Phase 2: Integration (Add to detector)
```python
# In ohlcv_adjustment_detector.py
def run(self, ..., cascade_refresh: bool = True):
    ...
    if refresh_results['success'] > 0 and cascade_refresh:
        logger.info("Triggering cascade refresh...")
        self._cascade_refresh_technical()

def _cascade_refresh_technical(self):
    """Refresh all technical indicators after OHLCV update."""
    from PROCESSORS.pipelines.daily.daily_ta_complete import CompleteTAUpdatePipeline
    pipeline = CompleteTAUpdatePipeline()
    pipeline.run(n_sessions=500)
```

### Phase 3: Optional (Option C for BSC MCP)
Add `get_ohlcv_raw()` method to BSC MCP DataLoader cho trường hợp cần data real-time.

---

## Implementation Steps

### Step 1: Run Cascade Now (Manual)
```bash
cd /Users/buuphan/Dev/Vietnam_dashboard
python3 PROCESSORS/pipelines/daily/daily_ta_complete.py --sessions 500
```

### Step 2: Verify BSC MCP Data
```python
# Check if basic_data.parquet has updated indicators for CTG, HDB
```

### Step 3: Add --cascade Flag to Detector
```python
parser.add_argument('--cascade', action='store_true',
                    help='Run cascade refresh after OHLCV update')
```

---

## Timeline

| Step | Action | Time |
|------|--------|------|
| 1 | Run daily_ta_complete.py now | ~5 min |
| 2 | Verify data consistency | ~2 min |
| 3 | Add cascade flag to detector | ~15 min |
| 4 | Test end-to-end | ~10 min |

---

## Completed Actions

1. [x] Run `python3 PROCESSORS/pipelines/daily/daily_ta_complete.py --sessions 500` ✅
2. [x] Verify CTG, HDB indicators in basic_data.parquet ✅ (all close prices match 100%)
3. [x] Add `--cascade` flag to adjustment detector ✅

## New Workflow

```bash
# Full workflow: detect, refresh OHLCV, AND update all technical indicators
python3 PROCESSORS/technical/ohlcv/ohlcv_adjustment_detector.py --detect --refresh --cascade
```

This ensures:
- OHLCV prices are adjusted for dividends/splits
- All technical indicators (MA, RSI, MACD, etc.) are recalculated
- BSC MCP reads correct data from basic_data.parquet

---

## Notes

- Valuation data (PE/PB) không cần recalculate vì formula dùng market_cap / earnings
- Market cap được tính từ shares_outstanding * close - cả hai được điều chỉnh đồng bộ
- Chỉ technical indicators cần recalculate vì dùng historical prices
