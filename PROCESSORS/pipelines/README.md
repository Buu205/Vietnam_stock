# Daily Update Pipelines

Tất cả scripts để update data hàng ngày nằm ở đây.
All daily data update scripts are consolidated in this folder.

## 🚀 Quick Start

### Chạy Toàn Bộ (Recommended)

```bash
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

This runs all daily updates in the correct order:
1. **OHLCV** → Raw market data
2. **Technical Analysis** → TA indicators, alerts, breadth
3. **Macro & Commodity** → Economic data
4. **Stock Valuation** → PE/PB/EV-EBITDA
5. **Sector Analysis** → Sector metrics & scoring

### Chạy Từng Script Riêng Lẻ

```bash
# 1. OHLCV (chạy đầu tiên)
python3 PROCESSORS/pipelines/daily_ohlcv_update.py

# 2. Technical Analysis (Full TA Pipeline)
python3 PROCESSORS/pipelines/daily_ta_complete.py

# 3. Macro & Commodity
python3 PROCESSORS/pipelines/daily_macro_commodity.py

# 4. Stock Valuation
python3 PROCESSORS/pipelines/daily_valuation.py

# 5. Sector Analysis
python3 PROCESSORS/pipelines/daily_sector_analysis.py
```

---

## 📋 Scripts Overview

| Script | Purpose | Output Location | Est. Runtime |
|--------|---------|----------------|--------------|
| `daily_ohlcv_update.py` | Fetch OHLCV data via vnstock | `DATA/raw/ohlcv/` | ~10s |
| `daily_ta_complete.py` | Full TA pipeline (8 steps) | `DATA/processed/technical/` | ~30s |
| `daily_macro_commodity.py` | Macro & commodity data | `DATA/processed/macro_commodity/` | ~15s |
| `daily_valuation.py` | Individual stock PE/PB/EV-EBITDA + VNINDEX | `DATA/processed/valuation/` | ~8s |
| `daily_sector_analysis.py` | Sector FA+TA metrics & scores | `DATA/processed/sector/` | ~16s |

**Total Runtime:** ~80 seconds (~1.3 minutes)

---

## 🎯 Master Script Options

### Skip Specific Updates

```bash
# Skip OHLCV and TA
python3 PROCESSORS/pipelines/run_all_daily_updates.py --skip-ohlcv --skip-ta

# Skip only sector analysis
python3 PROCESSORS/pipelines/run_all_daily_updates.py --skip-sector
```

### Run Only One Update

```bash
# Run only valuation
python3 PROCESSORS/pipelines/run_all_daily_updates.py --only valuation

# Run only TA
python3 PROCESSORS/pipelines/run_all_daily_updates.py --only ta
```

---

## 📊 Script Details

### 1. daily_ohlcv_update.py

**Purpose:** Fetch OHLCV (Open, High, Low, Close, Volume) data for all stocks.

**Data Source:** vnstock_data API

**Output:**
- `DATA/raw/ohlcv/OHLCV_mktcap.parquet`

**Options:**
```bash
# Fetch for specific date
python3 PROCESSORS/pipelines/daily_ohlcv_update.py --date 2024-12-15

# Force update (overwrite existing)
python3 PROCESSORS/pipelines/daily_ohlcv_update.py --force
```

---

### 2. daily_ta_complete.py

**Purpose:** Full technical analysis pipeline (8 steps).

**Steps:**
1. VN-Index analysis (trend, RSI, MACD)
2. Technical indicators (MA, RSI, MACD, Bollinger, ATR)
3. Alert detection (crossover, volume spike, breakout, patterns)
4. Money flow analysis (individual stocks)
5. Sector money flow (1D, 1W, 1M)
6. Market breadth (MA breadth, advancing/declining)
7. Sector breadth (strength scores)
8. Market regime detection (bullish/bearish/neutral)

**Output:**
- `DATA/processed/technical/basic_data.parquet`
- `DATA/processed/technical/alerts/`
- `DATA/processed/technical/money_flow/`
- `DATA/processed/technical/market_breadth/`
- `DATA/processed/technical/sector_breadth/`
- `DATA/processed/technical/market_regime/`
- `DATA/processed/technical/vnindex/`

**Options:**
```bash
# Process more sessions (default: 200)
python3 PROCESSORS/pipelines/daily_ta_complete.py --sessions 500

# Process specific date
python3 PROCESSORS/pipelines/daily_ta_complete.py --date 2024-12-15
```

---

### 3. daily_macro_commodity.py

**Purpose:** Update macro-economic and commodity data.

**Data:** Gold, USD/VND, interest rates, inflation, etc.

**Output:**
- `DATA/processed/macro_commodity/macro_commodity_unified.parquet`

**Options:**
```bash
# Run full migration (2015-present)
python3 PROCESSORS/pipelines/daily_macro_commodity.py --migrate
```

---

### 4. daily_valuation.py

**Purpose:** Update individual stock valuation metrics + VNINDEX valuation.

**Metrics:**
- PE Ratio (Price-to-Earnings)
- PB Ratio (Price-to-Book)
- EV/EBITDA Ratio
- VNINDEX PE (multiple scopes)

**Output:**
- `DATA/processed/valuation/pe/historical/historical_pe.parquet`
- `DATA/processed/valuation/pb/historical/historical_pb.parquet`
- `DATA/processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet`
- `DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet`

**Note:** Sector valuation is now handled by `daily_sector_analysis.py`.

---

### 5. daily_sector_analysis.py

**Purpose:** Complete sector analysis pipeline (FA + TA + Scoring).

**Steps:**
1. Aggregate fundamental metrics by sector
2. Aggregate valuation metrics by sector (PE/PB/PS/EV-EBITDA)
3. Calculate FA scores
4. Calculate TA scores
5. Combine FA+TA scores
6. Generate Buy/Hold/Sell signals

**Output:**
- `DATA/processed/sector/sector_fundamental_metrics.parquet`
- `DATA/processed/sector/sector_valuation_metrics.parquet`
- `DATA/processed/sector/sector_combined_scores.parquet`

**Options:**
```bash
# Run only FA aggregation
python3 PROCESSORS/pipelines/daily_sector_analysis.py --fa-only

# Run only TA aggregation
python3 PROCESSORS/pipelines/daily_sector_analysis.py --ta-only

# Specific date range
python3 PROCESSORS/pipelines/daily_sector_analysis.py --start-date 2024-01-01 --end-date 2024-12-31

# Verbose logging
python3 PROCESSORS/pipelines/daily_sector_analysis.py --verbose
```

---

## 🔍 Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`, ensure you're running from project root:

```bash
cd /Users/buuphan/Dev/Vietnam_dashboard
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

### Data Not Found

If scripts fail with "file not found", ensure previous steps have run:
- OHLCV must run first (provides raw data)
- TA depends on OHLCV
- Valuation depends on OHLCV
- Sector analysis depends on fundamental + valuation data

### Timeout Errors

Master script has 10-minute timeout per script. If a script exceeds this:
- Run it separately with more time
- Check for data issues (corrupted files, missing dependencies)

---

## 📁 Directory Structure

```
PROCESSORS/
└── pipelines/                    # Daily update scripts
    ├── run_all_daily_updates.py  # Master orchestrator
    ├── daily_ohlcv_update.py     # OHLCV fetch
    ├── daily_ta_complete.py      # Full TA pipeline
    ├── daily_macro_commodity.py  # Macro/commodity
    ├── daily_valuation.py        # Stock valuation
    ├── daily_sector_analysis.py  # Sector analysis
    └── README.md                 # This file
```

---

## 🔄 Update Frequency

**Daily Updates (recommended):**
- Run every trading day after market close (5 PM Vietnam time)
- OHLCV data available ~30 minutes after close
- Full pipeline takes ~1-2 minutes

**Weekly/Monthly:**
- Macro/commodity: Can run weekly (data doesn't change daily)
- Sector analysis: Can run weekly for longer-term analysis

---

**Author:** Claude Code
**Last Updated:** 2025-12-15
**Version:** 1.0.0
