# Brainstorm: Market Regime - Sector Confirmation Logic

**Date:** 2026-01-15
**Status:** Analysis Complete
**Decision:** Pending - Need more historical data

---

## Problem Statement

Thị trường tăng mạnh (VN-Index +15% từ đáy Dec 15), breadth cải thiện rõ rệt (MA20: 61%, MA50: 52%), nhưng hệ thống vẫn hiển thị "EARLY BUY" thay vì chuyển sang trạng thái mua mạnh hơn.

**Screenshot context:**
- MA20: 61% | MA50: 52% | MA100: 41%
- Score: 53 | Trend: DOWNTREND
- Signal: EARLY BUY (Early Reversal)
- Higher Lows: Đã xác nhận cho cả MA20 và MA50

---

## Root Cause Analysis

### Current Logic (trading_rules.py)

```python
def is_uptrend(ma50_pct, ma100_pct):
    return ma50_pct >= 50 AND ma100_pct >= 50

def determine_signal(...):
    if is_uptrend(ma50, ma100):
        # UPTREND signals: STRONG_BUY, BUY, HOLD, WARNING
    else:
        # DOWNTREND signals: SELL, DANGER, EARLY_BUY, WAIT
        if bottom_stage == 'EARLY_REVERSAL':
            return 'EARLY_BUY'
```

### Bottleneck Identified

| Condition | Required | Actual | Status |
|-----------|----------|--------|--------|
| MA50 >= 50% | ✅ | 52% | PASS |
| MA100 >= 50% | ✅ | 41% | **FAIL** |

**=> MA100 = 41% là nút thắt khiến hệ thống không chuyển sang UPTREND**

---

## Backtest Results

### Period: Dec 2024 - Jan 2026 (262 trading days)

| Strategy | Return | Exposure | Max DD | Alpha vs B&H |
|----------|--------|----------|--------|--------------|
| **Buy & Hold VN-Index** | +48.7% | 100% | -18.1% | — |
| MA100 >= 50% (current) | +23.2% | 35% | -4.4% | -25.5% |
| MA100 >= 45% | +23.4% | 41% | -4.4% | -25.3% |
| MA100 >= 40% | +26.8% | 44% | -4.4% | -21.9% |
| EARLY_BUY (MA20>=25%) | +10.4% | 51% | -12.9% | -38.3% |

### Key Insights

1. **All threshold strategies underperform B&H** trong bull market
2. **MA100>=40% tốt nhất** trong các threshold (+26.8%)
3. **Max DD rất thấp** (−4.4% vs −18.1%) → Trade-off hợp lý
4. **EARLY_BUY signal kém hiệu quả** (+10.4% với exposure 51%)

---

## Dec 2025 - Jan 2026 Rally Analysis

### VN-Index Performance

| Date | VNI | Cum Ret | MA20 | MA50 | MA100 | Signal |
|------|-----|---------|------|------|-------|--------|
| Dec 15 | 1,646 | +0.0% | 16% | 23% | 16% | WAIT |
| Dec 19 | 1,704 | +3.5% | 28% | 30% | 21% | EARLY_BUY |
| Dec 22 | 1,751 | +6.4% | 38% | 35% | 24% | EARLY_BUY |
| Jan 07 | 1,862 | +13.1% | 47% | 39% | 30% | EARLY_BUY |
| Jan 12 | 1,877 | +14.1% | 56% | 48% | 37% | EARLY_BUY |
| **Jan 14** | **1,894** | **+15.1%** | **61%** | **52%** | **41%** | **EARLY_BUY** |

**=> Miss toàn bộ rally 15% vì chờ MA100 >= 50%**

---

## Proposed Solution: Sector-Based Confirmation

### Sector Breadth Data (Jan 14, 2026)

| Sector | MA50>=50% | MA100>=50% |
|--------|-----------|------------|
| TELECOM | 100% | 100% |
| OIL_GAS | 100% | 100% |
| INSURANCE | 100% | 50% |
| BANK | 78% | 43% |
| UTILITIES | 78% | 56% |
| ... | ... | ... |

**Total: 13/19 sectors có MA50>=50%**

### Proposed Stage Logic

| Stage | Condition | Exposure |
|-------|-----------|----------|
| CAPITULATION | All sectors oversold | 0% |
| ACCUMULATING | <5 sectors MA50>=50%, Higher Lows | 10-20% |
| EARLY BUY | 5-9 sectors MA50>=50% | 20-40% |
| **CONFIRMED** | **>=10 sectors MA50>=50%** | **40-60%** |
| FULL UPTREND | >=10 sectors MA100>=50% | 80-100% |

### Backtest Results (Feb 2025 - Jan 2026)

| Strategy | Return | Exposure | Max DD |
|----------|--------|----------|--------|
| Buy & Hold | +49.2% | 100% | -18.1% |
| Current (MA100>=50%) | +22.8% | 37% | -4.4% |
| Sector>=10 MA50>=50% | +0.9% | 1% | -0.4% |
| Combined (Sector OR Current) | +23.9% | 38% | -4.4% |

### Timeline Comparison

| Date | Current Logic | Proposed Logic | Sectors MA50>=50% |
|------|---------------|----------------|-------------------|
| Dec 25 | - | EARLY BUY | 5/19 |
| Jan 07 | - | EARLY BUY | 6/19 |
| Jan 12 | - | **CONFIRMED** | 11/19 |
| Jan 14 | - | **CONFIRMED** | 13/19 |

---

## Limitations & Issues

### 1. Data Availability
- Sector breadth data: Feb 2025 - present (11 months)
- Sector confirmation >=10 chỉ mới trigger lần đầu: **Jan 12, 2026**
- **Không đủ historical data để validate**

### 2. Backtest Bias
- Sector-based logic chưa từng trigger trong downtrend/sideways 2025
- Chỉ có 2-3 ngày data với sector confirmation
- Statistical significance rất thấp

---

## Recommendations

### Option A: Implement & Collect Data
- Thêm `sector_confirmation_count` vào market state
- Hiển thị trên UI nhưng không thay đổi signal logic
- Thu thập data 6-12 tháng rồi re-evaluate

### Option B: Lower MA100 Threshold
- Giảm MA100 từ 50% xuống 40-45%
- Simple change, backtest cho thấy +3-4% return improvement
- Risk: Có thể trigger sớm trong false breakout

### Option C: Keep Current + Better UI
- Giữ nguyên logic conservative
- Cải thiện UI hiển thị exposure recommendation rõ hơn
- EARLY_BUY = "Test buy 10-20%", không phải "Đứng ngoài"

---

## Unresolved Questions

1. **Data collection**: Có thể backfill sector breadth data từ 2023-2024 không?
2. **Leading sectors**: Banking, Securities, Real Estate có nên weight cao hơn?
3. **Rate of change**: Sector count tăng nhanh có nên là signal mạnh hơn?
4. **Individual sector signals**: Khi nào một sector "confirmed" riêng lẻ?

---

## References

### Files Analyzed
- `WEBAPP/core/trading_rules.py` - Signal matrix, determine_signal()
- `WEBAPP/core/trading_constants.py` - Thresholds
- `WEBAPP/pages/technical/services/ta_dashboard_service.py` - _detect_bottom_stage()
- `DATA/processed/technical/market_breadth/market_breadth_daily.parquet`
- `DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet`

### Key Functions
```python
# Current uptrend check
is_uptrend(ma50_pct, ma100_pct) -> bool

# Bottom stage detection
_detect_bottom_stage(ma20, ma50, ma100, higher_lows) -> str|None

# Signal determination
determine_signal(ma20, ma50, ma100, higher_lows, bottom_stage) -> str
```

---

## Action Items

- [ ] Decide on implementation approach (A, B, or C)
- [ ] If Option A: Add sector_confirmation_count to MarketState model
- [ ] If Option B: Update TREND_CONFIRMATION_THRESHOLD in trading_constants.py
- [ ] If Option C: Update UI to show exposure recommendations clearly
- [ ] Consider backfilling sector breadth data for better validation
