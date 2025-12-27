# Pipeline Files Audit Report

**Date:** 2025-12-25
**Purpose:** Map existing Python files to TA Dashboard Plan requirements

---

## 1. PROCESSORS/technical Structure

```
PROCESSORS/technical/
├── indicators/                    # TA indicator calculators
│   ├── technical_processor.py     # ✅ Core - SMA, RSI, MACD, BB, ATR
│   ├── alert_detector.py          # ✅ Core - MA crossover, volume spike, breakout
│   ├── money_flow.py              # ✅ Core - Individual stock money flow
│   ├── sector_money_flow.py       # ✅ Core - Sector-level money flow
│   ├── sector_breadth.py          # ✅ Core - Sector % above MA
│   ├── market_regime.py           # ✅ Core - BULLISH/BEARISH/NEUTRAL
│   ├── vnindex_analyzer.py        # ✅ Core - VN-Index indicators
│   └── rs_rating.py               # ✅ NEW - IBD-style RS Rating (1-99)
│
├── ohlcv/                         # OHLCV data management
│   ├── __init__.py
│   ├── ohlcv_daily_updater.py     # ✅ Core - Fetch/update OHLCV data
│   └── ohlcv_adjustment_detector.py # ✅ Core - Detect price adjustments
│
└── macro_commodity/               # Macro economic data
    └── macro_commodity_fetcher.py # ✅ Core - Fetch macro/commodity data
```

---

## 2. File to Plan Mapping

| Python File | Plan Phase | Purpose | Status |
|-------------|------------|---------|--------|
| `technical_processor.py` | Phase 1-3 | SMA/EMA, RSI, MACD, Bollinger | ✅ Used |
| `alert_detector.py` | Phase 4 | Buy/Sell signals detection | ✅ Used |
| `money_flow.py` | Phase 3 | Individual stock money flow | ✅ Used |
| `sector_money_flow.py` | Phase 3 | Sector money flow heatmap | ✅ Used |
| `sector_breadth.py` | Phase 2 | Sector % above MA20/50/100 | ✅ Used |
| `market_regime.py` | Phase 2 | Market state detection | ✅ Used |
| `vnindex_analyzer.py` | Phase 2 | VN-Index trend analysis | ✅ Used |
| `rs_rating.py` | Phase 3 | RS Rating Heatmap (NEW) | ✅ Created |
| `ohlcv_daily_updater.py` | Daily Pipeline | OHLCV data source | ✅ Used |
| `ohlcv_adjustment_detector.py` | Daily Pipeline | Handle price adjustments | ✅ Used |
| `macro_commodity_fetcher.py` | Dashboard-wide | Macro data overlay | ✅ Used |

---

## 3. Data Outputs Required by Plan

| Data File | Generator | Plan Phase |
|-----------|-----------|------------|
| `basic_data.parquet` | technical_processor.py | All phases |
| `market_breadth_daily.parquet` | daily_ta_complete.py | Phase 2 |
| `vnindex_indicators.parquet` | vnindex_analyzer.py | Phase 2 |
| `sector_breadth_daily.parquet` | sector_breadth.py | Phase 2, 3 |
| `sector_money_flow_1d.parquet` | sector_money_flow.py | Phase 3 |
| `combined_latest.parquet` | alert_detector.py | Phase 4 |
| **`stock_rs_rating_daily.parquet`** | **rs_rating.py** | **Phase 3 (NEW)** |

---

## 4. Missing Files Check

### Required by Plan but Not Yet Created:

| File | Purpose | Plan Section | Status |
|------|---------|--------------|--------|
| `base.py` | TAIndicator abstract class | Phase 1 Section 0 | ❌ TODO |
| `quadrant.py` | RRG quadrant logic | Phase 1 Section 0 | ❌ TODO |
| `relative_strength.py` | RS Ratio calculator | Phase 1 Section 0 | ❌ TODO |
| `confidence.py` | Confidence score | Phase 1 Section 0 | ❌ TODO |

> **Note:** These are optional refactoring for cleaner code. Current functionality works without them.

---

## 5. Daily Pipeline Integration

### PROCESSORS/pipelines/daily/

| File | Steps | Updated |
|------|-------|---------|
| `daily_ta_complete.py` | 9 steps (1-8 + RS Rating) | ✅ 2025-12-25 |
| `daily_rs_rating.py` | Standalone RS Rating | ✅ Created |
| `daily_ohlcv_update.py` | OHLCV sync | Existing |
| `daily_valuation.py` | PE/PB/EV-EBITDA | Existing |
| `daily_sector_analysis.py` | Sector metrics | Existing |
| `daily_macro_commodity.py` | Macro data | Existing |
| `daily_bsc_forecast.py` | BSC forecast | Existing |

### run_all_daily_updates.py

```python
# Updated 2025-12-25: Added RS Rating and Market Breadth to data checks

data_checks = [
    ("OHLCV (Source)", "DATA/raw/ohlcv/OHLCV_mktcap.parquet", ...),
    ("Technical (TA)", "DATA/processed/technical/basic_data.parquet", ...),
    ("RS Rating", "DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet", ...),  # NEW
    ("Market Breadth", "DATA/processed/technical/market_breadth/market_breadth_daily.parquet", ...),  # NEW
    ...
]
```

---

## 6. Summary

**Total Python files in PROCESSORS/technical:** 12 files

**Status:**
- ✅ 11 files are existing and required
- ✅ 1 file created today (rs_rating.py)
- ❌ 4 optional refactoring files (base classes) - TODO for cleaner architecture

**Conclusion:** Không có file thừa. Tất cả các file đều có mục đích rõ ràng và được sử dụng trong pipeline.

---

## 7. Run Commands

```bash
# Full TA update (includes RS Rating)
python3 PROCESSORS/pipelines/daily/daily_ta_complete.py

# Master daily runner
python3 PROCESSORS/pipelines/run_all_daily_updates.py

# Standalone RS Rating (for testing)
python3 PROCESSORS/pipelines/daily/daily_rs_rating.py --verify
```
