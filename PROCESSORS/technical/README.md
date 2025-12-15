# Technical Analysis System
## Complete TA Pipeline with TA-Lib

**Version:** 2.0.0
**Date:** 2025-12-15
**Author:** Claude Code

---

## 🚀 Quick Start

### Daily Update (RECOMMENDED)

**Option 1: Master script (easiest)**
```bash
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

**Option 2: TA only**
```bash
python3 PROCESSORS/pipelines/daily_ta_complete.py
```

**Thời gian:** ~30-35 giây
**Input:** `DATA/raw/ohlcv/OHLCV_mktcap.parquet` (tự động load 200 sessions)
**Output:** Tất cả files dưới đây

---

## 📊 Features Implemented

### Phase 1-3: Alert System ✅

**File:** [PROCESSORS/technical/indicators/alert_detector.py](indicators/alert_detector.py)

**Alerts:**
- ✅ **MA Crossover** - Price crosses above/below MA20/50/100/200
- ✅ **Smart Volume Spike** - Volume spike with 4-factor confirmation:
  - Volume > 1.5x average
  - Breakout detection
  - RSI confirmation
  - MACD signal
  - Candlestick pattern
- ✅ **Breakout/Breakdown** - Price breaks 20-day high/low with volume
- ✅ **Candlestick Patterns** - 10 most reliable patterns using TA-Lib
- ✅ **Combined Signals** - MA + RSI + MACD scoring system

**Example Output (2025-12-15):**
```
MA Crossover Alerts: 78
  - ABB: CROSS_BELOW MA20 (BEARISH)
  - BCR: CROSS_ABOVE MA50 (BULLISH)
  - BMJ: CROSS_ABOVE MA100 (BULLISH)

Volume Spike Alerts: 49
  - BMP: WATCH (ratio: 2.99x, confirmations: 2, confidence: 50%)

Breakout Alerts: 9
Pattern Alerts: 161
Combined Signals: 457
```

### Phase 4: Money Flow & Advanced TA ✅

**File:** [PROCESSORS/technical/indicators/money_flow.py](indicators/money_flow.py)

**Indicators:**
- ✅ **Chaikin Money Flow (CMF)** - 20-period
- ✅ **Money Flow Index (MFI)** - 14-period (RSI của volume)
- ✅ **On-Balance Volume (OBV)** - Cumulative volume
- ✅ **AD Line** - Accumulation/Distribution
- ✅ **VPT** - Volume Price Trend

**Classification:**
- STRONG_ACCUMULATION
- ACCUMULATION
- NEUTRAL
- DISTRIBUTION
- STRONG_DISTRIBUTION

**File:** [PROCESSORS/technical/indicators/sector_money_flow.py](indicators/sector_money_flow.py)

**Features:**
- Aggregate money flow per sector
- **Multi-timeframe analysis (1D, 1W, 1M)** - Compare short vs long-term trends
- Inflow/Outflow % vs previous period
- Top 3 contributors per sector
- Identify sector rotation patterns

### Phase 5: Advanced Features ✅

**File:** [PROCESSORS/technical/indicators/sector_breadth.py](indicators/sector_breadth.py)

**Features:**
- % stocks above MA20/50/100/200 per sector
- Advancing vs Declining stocks per sector
- RSI breadth (bullish/bearish/overbought/oversold)
- Sector trend classification (STRONG_BULLISH to STRONG_BEARISH)
- Strength score (0-100)

**File:** [PROCESSORS/technical/indicators/market_regime.py](indicators/market_regime.py)

**Features:**
- Multi-factor regime detection (5 components)
  - Valuation (PE percentile)
  - Market breadth
  - Volume patterns
  - Volatility (ATR)
  - Momentum (MACD/RSI)
- Regime classification: BUBBLE, EUPHORIA, NEUTRAL, FEAR, BOTTOM
- Risk level: VERY_HIGH, HIGH, MEDIUM, LOW
- Market sentiment tracking

**File:** [PROCESSORS/technical/indicators/vnindex_analyzer.py](indicators/vnindex_analyzer.py)

**Features:**
- Fetch VN-Index OHLCV from vnstock
- Calculate all technical indicators for VN-Index
- Trend classification (STRONG_UPTREND to STRONG_DOWNTREND)
- Market-level view for comparison

---

## 📁 Output Files

```
DATA/processed/technical/
├── basic_data.parquet                      # 18.6 MB
│   └── 40 columns: OHLCV + MA + RSI + MACD + Bollinger + ATR + Volume indicators
│
├── alerts/
│   ├── daily/                              # Latest alerts (overwrite daily)
│   │   ├── ma_crossover_latest.parquet     # ~50 KB
│   │   ├── volume_spike_latest.parquet     # ~30 KB
│   │   ├── breakout_latest.parquet         # ~20 KB
│   │   ├── patterns_latest.parquet         # ~40 KB
│   │   └── combined_latest.parquet         # ~60 KB
│   │
│   └── historical/                         # Full history (append-only)
│       ├── ma_crossover_history.parquet
│       ├── volume_spike_history.parquet
│       ├── breakout_history.parquet
│       └── patterns_history.parquet
│
├── money_flow/
│   ├── individual_money_flow.parquet       # 6.6 MB - Per stock
│   ├── sector_money_flow.parquet           # Per sector (legacy)
│   ├── sector_money_flow_1d.parquet        # 1-day money flow
│   ├── sector_money_flow_1w.parquet        # 1-week money flow
│   └── sector_money_flow_1m.parquet        # 1-month money flow
│
├── market_breadth/
│   └── market_breadth_daily.parquet        # Market-wide metrics
│
├── sector_breadth/
│   └── sector_breadth_daily.parquet        # Per sector breadth metrics
│
├── market_regime/
│   └── market_regime_history.parquet       # Market regime classification
│
└── vnindex/
    └── vnindex_indicators.parquet          # VN-Index technical indicators
```

---

## 🎯 Usage Examples

### 1. Daily Complete Update

```bash
# Cập nhật tất cả (200 sessions)
python3 PROCESSORS/pipelines/daily_ta_complete.py

# Chỉ định số sessions
python3 PROCESSORS/pipelines/daily_ta_complete.py --sessions 250

# Chỉ định ngày cụ thể
python3 PROCESSORS/pipelines/daily_ta_complete.py --date 2025-12-15
```

### 2. Chỉ Tính Technical Indicators

```bash
python3 PROCESSORS/technical/indicators/technical_processor.py --sessions 200
```

### 3. Chỉ Detect Alerts

```bash
from PROCESSORS.technical.indicators.alert_detector import TechnicalAlertDetector

detector = TechnicalAlertDetector()
alerts = detector.detect_all_alerts(date='2025-12-15', n_sessions=200)

print(f"MA Crossover: {len(alerts['ma_crossover'])}")
print(f"Volume Spike: {len(alerts['volume_spike'])}")
```

### 4. Chỉ Money Flow Analysis

```bash
python3 PROCESSORS/technical/indicators/money_flow.py --sessions 200
```

### 5. Chỉ Sector Money Flow

```bash
# Single day (1D only)
python3 PROCESSORS/technical/indicators/sector_money_flow.py --date 2025-12-15

# Multi-timeframe (1D, 1W, 1M)
python3 PROCESSORS/technical/indicators/sector_money_flow.py --multi-timeframe
```

### 6. Chỉ Sector Breadth

```bash
python3 PROCESSORS/technical/indicators/sector_breadth.py --date 2025-12-15
```

### 7. Chỉ Market Regime

```bash
python3 PROCESSORS/technical/indicators/market_regime.py --date 2025-12-15
```

### 8. Chỉ VN-Index Analysis

```bash
python3 PROCESSORS/technical/indicators/vnindex_analyzer.py --sessions 500
```

### 9. View Streamlit Dashboard

```bash
streamlit run WEBAPP/main_app.py
# Then navigate to "Technical Analysis" page
```

---

## 📖 Data Schemas

### basic_data.parquet (40 columns)

| Column | Description |
|--------|-------------|
| date | Trading date |
| symbol | Stock symbol |
| open, high, low, close | OHLCV |
| volume | Volume |
| sma_20, sma_50, sma_100, sma_200 | Simple MA |
| ema_20, ema_50 | Exponential MA |
| rsi_14 | RSI 14-period |
| macd, macd_signal, macd_hist | MACD |
| stoch_k, stoch_d | Stochastic |
| bb_upper, bb_middle, bb_lower, bb_width | Bollinger Bands |
| atr_14 | Average True Range |
| obv | On-Balance Volume |
| ad_line | Accumulation/Distribution |
| cmf_20 | Chaikin Money Flow |
| mfi_14 | Money Flow Index |
| adx_14 | ADX (trend strength) |
| cci_20 | Commodity Channel Index |
| price_vs_sma20/50/200 | Price distance from MA (%) |

### Alerts Schema

**MA Crossover:**
```
symbol | date | alert_type | ma_period | price | ma_value | signal
ABB | 2025-12-15 | MA_CROSS_BELOW | 20 | 24500 | 24800 | BEARISH
```

**Smart Volume Spike:**
```
symbol | volume | volume_ratio | signal | confirmations | confidence
BMP | 5000000 | 2.99 | WATCH | 2 | 0.50
```

**Breakout:**
```
symbol | alert_type | price | resistance_level | volume_confirmed | signal
HPG | BREAKOUT_UP | 28500 | 28000 | True | BULLISH_BREAKOUT
```

**Candlestick Pattern:**
```
symbol | pattern_name | signal | strength | price
VNM | hammer | BULLISH | 100 | 85000
```

**Combined Signal:**
```
symbol | ma_trend | rsi_14 | macd_signal | overall_signal | confidence | score
VIC | BULLISH | 55 | BULLISH_CROSS | STRONG_BUY | 0.85 | 75
```

### Money Flow Schema

**Individual:**
```
symbol | date | cmf_20 | mfi_14 | obv | ad_line | vpt | money_flow_signal
ACB | 2025-12-15 | 0.12 | 58 | 125M | 350M | 120M | STRONG_ACCUMULATION
```

**Sector:**
```
sector_code | money_flow | inflow_pct | flow_signal | top_contributors
BANKING | 5.2T | +12.5% | STRONG_INFLOW | ACB, TCB, VCB
```

---

## ⚡ Performance

**Benchmarks (458 symbols × 200 sessions):**
- Complete pipeline: **~32 seconds**
- Technical indicators: **~15 seconds**
- Alert detection: **~8 seconds**
- Money flow: **~6 seconds**
- Sector analysis: **~2 seconds**

**Why so fast?**
- ✅ **TA-Lib** (C-based) - 10-100x faster than pandas
- ✅ **Vectorized operations** with numpy
- ✅ **Efficient parquet** compression
- ✅ **Only 200 sessions** loaded (not full history)

---

## 🔧 Dependencies

```bash
# Core libraries
pip install pandas numpy talib

# Install TA-Lib (macOS)
brew install ta-lib
pip install TA-Lib

# Install TA-Lib (Ubuntu)
sudo apt-get install ta-lib
pip install TA-Lib
```

---

## 📅 Daily Workflow (Recommended)

**Every day at 17:00 (after market close):**

**Option 1: Master script (easiest)**
```bash
python3 PROCESSORS/pipelines/run_all_daily_updates.py
```

**Option 2: Individual scripts**
```bash
# 1. Update OHLCV first
python3 PROCESSORS/pipelines/daily_ohlcv_update.py

# 2. Run complete TA update
python3 PROCESSORS/pipelines/daily_ta_complete.py
```

**Total time:** ~2-3 minutes

**Cron job setup:**
```bash
# Add to crontab -e (Option 1: Master script)
30 17 * * 1-5 cd /Users/buuphan/Dev/Vietnam_dashboard && python3 PROCESSORS/pipelines/run_all_daily_updates.py

# OR (Option 2: Individual)
30 17 * * 1-5 cd /Users/buuphan/Dev/Vietnam_dashboard && python3 PROCESSORS/pipelines/daily_ohlcv_update.py
35 17 * * 1-5 cd /Users/buuphan/Dev/Vietnam_dashboard && python3 PROCESSORS/pipelines/daily_ta_complete.py
```

---

## 🐛 Troubleshooting

### "No module named 'talib'"
```bash
brew install ta-lib  # macOS
pip install TA-Lib
```

### "OHLCV file not found"
Đảm bảo chạy OHLCV update trước:
```bash
python3 PROCESSORS/technical/pipelines/daily_ohlcv_update.py
```

### "Not enough data (X rows) - need at least 200"
Bình thường cho các mã mới. Indicators sẽ skip mã này.

---

## 🎨 Dashboard Features

**Streamlit Dashboard:** [WEBAPP/pages/technical_analysis.py](../../WEBAPP/pages/technical_analysis.py)

**7 Tabs:**
1. **📈 Market Overview** - Market breadth trends, A/D ratio
2. **🚨 Trading Alerts** - MA crossover, volume spike, breakout, patterns
3. **💰 Money Flow** - Sector and individual money flow analysis
4. **📊 Market Breadth** - Historical breadth metrics
5. **🏢 Sector Analysis** - Sector strength ranking and breadth
6. **📉 VN-Index** - VN-Index price chart with indicators
7. **🌡️ Market Regime** - Current regime and component scores

**How to Run:**
```bash
streamlit run WEBAPP/main_app.py
# Navigate to "Technical Analysis" page
```

---

## 📞 Support

Issues: Report to project maintainer

Documentation: See [technical_alerts_enhancement_plan.md](../../technical_alerts_enhancement_plan.md)
