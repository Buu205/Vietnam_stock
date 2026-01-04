# Research: Stock Split & Dividend Adjustment for Vietnamese Stock Data

**Date:** 2025-01-04
**Context:** OHLCV data exhibits extreme returns (e.g., CSV +373.7% on 2025-06-04) due to unadjusted stock splits
**Goal:** Identify technical methods for detecting & correcting stock split adjustments

---

## 1. vnstock_data API Capabilities

### Current Status
- **Package:** `vnstock_data` (latest v3.2.0 on PyPI as of Jan 2025)
- **OHLCV Data:** Includes `Adj Close` (adjusted close) column in output
- **Price Method:** Returns raw + adjusted prices via `price()` method
- **Limitation:** API documentation does NOT detail split/dividend adjustment methodology

### Implications for Vietnam Dashboard
- vnstock_data returns **both raw & adjusted prices**
- Current codebase uses raw prices (causing 373%+ returns)
- **Action:** Switch to `Adj Close` column OR implement custom adjustment layer

---

## 2. Stock Split Detection Algorithm

### Ratio-Based Detection (RECOMMENDED)

```
Split Ratio = Previous Close / Current Open
```

**Common Vietnamese Ratios:**
- 2:1 split (ratio ≈ 2.0)
- 3:1 split (ratio ≈ 3.0)
- 5:1 split (ratio ≈ 5.0)
- 100:44.63658403 (CTG bank dividend - non-integer split)

**Detection Threshold:** Flag anomalies where price ratio > 1.5 (indicating gap down likely from split)

**Implementation:**
```python
def detect_split(prev_close: float, curr_open: float, threshold: float = 1.5) -> float | None:
    if prev_close <= 0 or curr_open <= 0:
        return None
    ratio = prev_close / curr_open
    if ratio > threshold or ratio < (1 / threshold):
        return round(ratio, 2)  # Return detected split ratio
    return None
```

### Detection Accuracy
- **Limitation:** Cannot distinguish between stock split vs. dividend payment
- **Time Cost:** O(n) single pass through chronological price data
- **Vietnamese Market:** Daily price limit (±7-10%) makes jumps > 15% likely splits

---

## 3. Vietnamese Corporate Actions Sources

### Official Channels
1. **Vietnam National Seed Group (HOSE: NSC)** - Official dividend history
2. **Vietstock** - Daily announcements for all HOSE/HNX corporate actions
3. **HOSE/HNX Direct** - Exchange-published official records
4. **Vietnam.vn Official** - Government announcements (ex-dividend dates)

### Recent Examples (Dec 2025)
- **CTG (Industry Bank):** 100:44.63658403 share dividend ratio
- **TTA (Construction):** 100:5 share bonus ratio
- **HDB (Sacombank):** 100:4.69 share bonus ratio

### Data Availability Issue
- **No single free API** consolidates all corporate actions
- **Manual extraction required** from Vietstock HTML or exchange PDFs
- **Recommendation:** Create `corporate_actions.csv` with manual entries

---

## 4. Historical Price Adjustment Best Practices

### Adjustment Formula
```
Adjusted Price = Raw Price ÷ Cumulative Split Factor
```

### Split Factor Calculation
- **2:1 split:** Multiply pre-split prices by 0.5
- **4:1 split:** Multiply pre-split prices by 0.25
- **1:5 reverse split:** Multiply pre-split prices by 5
- **Compounding:** Multiple splits multiply factors (e.g., 2×2 = 4, not 3)

### Volume Adjustment
- Multiply pre-split volume by split ratio
- Ensures technical indicators (OBV, CMF) remain consistent

### Reference Date Approach
- Choose anchor date (e.g., today)
- All historical data before split date gets adjustment factor applied
- Prevents need to recalculate on each data update

---

## 5. Implementation Strategy for Vietnam Dashboard

### Phase 1: Detect Splits (Automated)
```python
# OHLCV_mktcap.parquet processing
for ticker in all_tickers:
    for date in price_history[ticker]:
        split_ratio = detect_split(prev_close, curr_open)
        if split_ratio:
            log_to_corporate_actions(ticker, date, ratio)
            flag_for_review()  # Manual verification needed
```

### Phase 2: Manual Corporate Actions Registry
Create `DATA/processed/metadata/corporate_actions.csv`:
```
ticker,date,action_type,ratio,verified
CSV,2025-06-04,STOCK_SPLIT,2.0,YES
CTG,2025-12-17,SHARE_DIVIDEND,1.4463658403,YES
```

### Phase 3: Apply Adjustments
```python
# Load corporate actions
actions = pd.read_csv("corporate_actions.csv")

# Apply cumulative factors
for ticker in ohlcv_df['ticker'].unique():
    ticker_actions = actions[actions['ticker'] == ticker].sort_values('date')
    cumulative_factor = 1.0

    for _, row in ticker_actions.iterrows():
        if row['action_type'] == 'STOCK_SPLIT':
            cumulative_factor /= row['ratio']
        # Apply factor to all prices before this date
```

---

## 6. Data Source Hierarchy

| Priority | Source | Type | Coverage | Update |
|----------|--------|------|----------|--------|
| **1** | vnstock_data `Adj Close` | API | All OHLCV | Daily |
| **2** | Manual corporate_actions.csv | Registry | Key splits/dividends | Manual/quarterly |
| **3** | Vietstock announcements | Web | All corporate actions | Real-time |
| **4** | HOSE/HNX official records | PDF | Official history | Quarterly |

---

## 7. Unresolved Questions

1. **Does vnstock_data handle bonus shares (100:5 ratios)?** Need to test actual output
2. **What adjustment method does vnstock use?** (forward-adjusted vs backward-adjusted?)
3. **How often do Vietnamese stocks experience reverse splits?** (rare vs common)
4. **Is Vietstock scraping feasible** given rate limits and CAPTCHA?
5. **Should we use vnstock `Adj Close` directly** or build custom adjustment layer for transparency?

---

## Sources

- [VNStock Data Documentation](https://vnstock-data-python.readthedocs.io/en/latest/)
- [Stock Split Detection - Stock Titan](https://www.stocktitan.net/articles/split-adjusted-price-vs-raw-price)
- [Price Adjustment Methods - StockCharts](https://support.stockcharts.com/doku.php?id=policies:adjusted_data)
- [Vietnam Corporate Actions - Vietstock](https://en.vietstock.vn/vietnam-companies/dividend-963.htm)
- [CRSP Split Calculations Reference](https://leiq.bus.umich.edu/docs/crsp_calculations_splits.pdf)
