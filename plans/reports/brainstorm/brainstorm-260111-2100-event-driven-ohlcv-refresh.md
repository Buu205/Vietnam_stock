# Brainstorm: Event-Driven OHLCV Refresh Strategy

**Date:** 2026-01-11
**Topic:** Pre-OHLCV event check để refresh full data khi có corporate events

---

## Problem Statement

Cần thêm bước kiểm tra TRƯỚC khi chạy OHLCV update:
1. **Primary**: Check ngày GDKHQ (giao dịch không hưởng quyền) từ Vietstock API
2. **Fallback 1**: Shares Outstanding thay đổi so với 5 phiên liền kề
3. **Fallback 2**: Giá thay đổi >8% so với phiên trước

**Khi trigger**: Chạy full OHLCV history refresh cho các mã affected

---

## Evaluated Approaches

### Option 1: Live API Check (Real-time)

```
Pipeline run → Call Vietstock API → Filter tickers → Refresh affected
```

| Pros | Cons |
|------|------|
| Dữ liệu luôn mới nhất | Chậm (~5-10s API call) |
| Không cần maintain cache | API có thể fail/rate limit |
| Đơn giản implement | Cookie/token có thể expire |

**Verdict**: ❌ Không khuyến khích - dependency vào external API mỗi lần chạy

---

### Option 2: Event Parquet Cache (Pre-fetched)

```
Weekly job: Fetch events → Save parquet
Pipeline run: Read parquet → Filter → Refresh affected
```

| Pros | Cons |
|------|------|
| Rất nhanh (~50ms đọc file) | Cần job riêng update |
| Offline-capable | Có thể miss events mới |
| Stable, không API failures | Thêm 1 file cần maintain |

**Schema đề xuất:**
```python
# vietstock_events.parquet
{
    "ticker": str,           # VNM, VCB, ...
    "event_type": str,       # DIVIDEND_CASH, DIVIDEND_STOCK, RIGHTS_ISSUE
    "ex_date": date,         # Ngày GDKHQ (GDKHQDate)
    "record_date": date,     # Ngày đăng ký cuối cùng (NDKCCDate)
    "payment_date": date,    # Ngày thanh toán (Time)
    "note": str,             # "Trả cổ tức năm 2024 bằng tiền, 1000đ/CP"
    "fetched_at": timestamp  # Timestamp lấy dữ liệu
}
```

**Verdict**: ⚠️ OK nhưng thiếu real-time cho events đột xuất

---

### Option 3: Hybrid Strategy (Recommended) ⭐

```
1. Event parquet (refresh weekly/daily) → Primary lookup
2. Price/Shares anomaly detection từ OHLCV data → Fallback
3. Optional: Live API check nếu cần
```

**Flow:**
```
OHLCV Update Pipeline
│
├─ Step 0 (NEW): Pre-check Module
│   ├─ 0.1 Read events parquet → Filter GDKHQ = today
│   ├─ 0.2 Read existing OHLCV → Detect anomalies
│   │       └─ Shares changed vs last 5 days
│   │       └─ Price moved >8%
│   └─ 0.3 Combine triggers → List of tickers to refresh
│
├─ Step 1: OHLCV Update
│   ├─ Normal update for non-affected tickers
│   └─ Full history refresh for affected tickers
│
└─ Step 2+: TA, Valuation, etc.
```

| Pros | Cons |
|------|------|
| Fast (file-based primary) | Thêm 1 module mới |
| Robust (multiple fallbacks) | Complexity tăng nhẹ |
| Offline-capable | Cần 2 data sources |
| Self-healing via anomaly detection | - |

**Verdict**: ✅ RECOMMENDED

---

## Recommended Solution: Hybrid Strategy

### 1. New Module: `event_trigger_check.py`

**Location:** `PROCESSORS/pipelines/utils/event_trigger_check.py`

```python
def get_tickers_needing_full_refresh() -> list[str]:
    """
    Check multiple trigger conditions and return tickers needing full OHLCV refresh.

    Priority:
    1. Event calendar (GDKHQ = today)
    2. Shares outstanding anomaly (changed vs 5 days)
    3. Price anomaly (>8% move)
    """
    affected = set()

    # 1. Event-based (primary)
    events_df = load_events_cache()
    if events_df is not None:
        today_events = events_df[events_df['ex_date'] == today]
        affected.update(today_events['ticker'].tolist())

    # 2. Shares anomaly (fallback)
    shares_anomalies = detect_shares_changes()
    affected.update(shares_anomalies)

    # 3. Price anomaly (fallback)
    price_anomalies = detect_price_moves(threshold=0.08)
    affected.update(price_anomalies)

    return list(affected)
```

### 2. Event Cache Update Job

**Location:** `PROCESSORS/pipelines/utils/update_event_cache.py`

```python
# Chạy riêng: daily hoặc weekly
# Output: DATA/processed/events/vietstock_events.parquet
```

**Khi nào chạy:**
- Cron: Daily lúc 7:00 AM (trước market open)
- Manual: Khi cần refresh

### 3. Pipeline Integration

**Modify:** `run_all_daily_updates.py`

```python
# Before OHLCV step
from PROCESSORS.pipelines.utils.event_trigger_check import get_tickers_needing_full_refresh

# Get tickers needing full refresh
full_refresh_tickers = get_tickers_needing_full_refresh()
if full_refresh_tickers:
    logger.info(f"🔄 {len(full_refresh_tickers)} tickers need full OHLCV refresh:")
    logger.info(f"   {full_refresh_tickers[:10]}...")  # Show first 10

    # Run full refresh for these tickers
    run_ohlcv_full_refresh(full_refresh_tickers)

# Then run normal daily update
run_script('daily_ohlcv_update.py', ...)
```

---

## Detection Logic Details

### 1. Event Detection (Primary)

```python
def filter_today_events(events_df: pd.DataFrame) -> list[str]:
    """Filter tickers with GDKHQ (ex-date) = today."""
    today = date.today()
    return events_df[events_df['ex_date'] == today]['ticker'].unique().tolist()
```

### 2. Shares Outstanding Anomaly

```python
def detect_shares_changes(ohlcv_df: pd.DataFrame, lookback: int = 5) -> list[str]:
    """Detect tickers where shares outstanding changed vs last 5 sessions."""
    anomalies = []

    for ticker in ohlcv_df['symbol'].unique():
        ticker_data = ohlcv_df[ohlcv_df['symbol'] == ticker].tail(lookback + 1)

        if len(ticker_data) < 2:
            continue

        # Compare latest vs previous sessions
        latest_shares = ticker_data.iloc[-1]['shareOutstanding']
        prev_shares = ticker_data.iloc[:-1]['shareOutstanding'].mode()[0]  # Most common

        if latest_shares != prev_shares:
            anomalies.append(ticker)

    return anomalies
```

### 3. Price Anomaly Detection

```python
def detect_price_moves(ohlcv_df: pd.DataFrame, threshold: float = 0.08) -> list[str]:
    """Detect tickers with >8% price move vs previous day."""
    anomalies = []

    for ticker in ohlcv_df['symbol'].unique():
        ticker_data = ohlcv_df[ohlcv_df['symbol'] == ticker].tail(2)

        if len(ticker_data) < 2:
            continue

        prev_close = ticker_data.iloc[-2]['close']
        curr_close = ticker_data.iloc[-1]['close']

        pct_change = abs(curr_close - prev_close) / prev_close

        if pct_change > threshold:
            anomalies.append(ticker)

    return anomalies
```

---

## Data File Structure

```
DATA/
├── processed/
│   └── events/
│       └── vietstock_events.parquet    # Event cache (NEW)
│           Schema:
│           - ticker: str
│           - event_type: str
│           - ex_date: date
│           - record_date: date
│           - payment_date: date
│           - note: str
│           - fetched_at: timestamp
│
└── raw/
    └── ohlcv/
        └── OHLCV_mktcap.parquet        # Existing OHLCV data
```

---

## Priority Order

| Priority | Trigger | Why |
|----------|---------|-----|
| 1 | Event calendar (GDKHQ) | Most reliable, known in advance |
| 2 | Shares changed | Corporate action indicator |
| 3 | Price >8% | Likely event, but could be market-driven |

---

## Performance Comparison

| Approach | Lookup Time | API Calls | Reliability |
|----------|-------------|-----------|-------------|
| Live API only | ~5-10s | Yes | Medium (API dependent) |
| Parquet only | ~50ms | No | High (local file) |
| **Hybrid** | ~100ms | Optional | Highest (fallbacks) |

---

## Implementation Considerations

### Risks
1. **Stale event cache**: Mitigate via daily refresh job
2. **False positives (price moves)**: Accept, better safe than miss event
3. **API token expiry**: Refresh mechanism needed

### Success Metrics
- Zero missed corporate events causing data gaps
- Pipeline runtime increase <30s
- Event cache freshness <24h

### Next Steps
1. Create `event_trigger_check.py` module
2. Create `update_event_cache.py` job
3. Integrate into `run_all_daily_updates.py`
4. Add cron for event cache refresh

---

## Recommended Answer to Original Question

> **"Nên tạo file parquet sự kiện hay như thế nào?"**

✅ **Nên dùng Hybrid approach:**
1. **Parquet event cache** - Primary, fast lookup
2. **Anomaly detection từ OHLCV** - Fallback, self-healing
3. **Ưu tiên event calendar** - Vì đã biết trước, chính xác nhất

**Lý do:**
- Event parquet: Tra cứu nhanh (~50ms vs ~5s API)
- Anomaly detection: Bắt được cases event cache miss
- Không phụ thuộc 100% vào external API khi chạy pipeline

---

## Unresolved Questions

1. **Event cache refresh frequency?** Daily 7AM recommended
2. **Full refresh scope?** All history or just affected dates?
3. **Include other event types?** AGM, phát hành mới, etc.?
