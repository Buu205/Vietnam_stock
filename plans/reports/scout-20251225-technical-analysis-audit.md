# Technical Analysis (TA) Codebase Audit

**Date:** 2025-12-25
**Scope:** Complete TA architecture review
**Status:** Production-ready with advanced features

---

## 1. PROCESSORS/technical/ - Core TA Engine

### 1.1 Structure & Organization

```
PROCESSORS/technical/
├── __init__.py
├── README.md                          # 426 lines - Comprehensive documentation
├── ohlcv/
│   ├── __init__.py
│   ├── ohlcv_daily_updater.py        # OHLCV data fetching (vnstock_data)
│   └── ohlcv_adjustment_detector.py  # Stock split/dividend detection
├── macro_commodity/
│   └── macro_commodity_fetcher.py    # Macro & commodity data
└── indicators/
    ├── technical_processor.py         # Main TA-Lib calculator
    ├── alert_detector.py              # 5 alert types + combined signals
    ├── money_flow.py                  # Individual stock money flow (CMF, MFI, OBV)
    ├── sector_money_flow.py           # Sector-level aggregation (1D/1W/1M)
    ├── sector_breadth.py              # Sector breadth metrics
    ├── market_regime.py               # Market condition detector
    └── vnindex_analyzer.py            # VN-Index indicator calculations
```

### 1.2 File Details & Capabilities

#### **technical_processor.py** (150+ lines)
**Purpose:** Calculate all TA indicators using TA-Lib
**Key Classes:**
- `TechnicalProcessor` - Main orchestrator
  - `load_ohlcv_data(n_sessions=200)` - Load last N sessions per symbol
  - `calculate_indicators_for_symbol(df)` - Batch indicator calculation

**Indicators (18 total):**
- Moving Averages: SMA 20/50/100/200, EMA 20/50
- Momentum: RSI 14, MACD, Stochastic K/D
- Volatility: Bollinger Bands (20/2), ATR 14
- Volume: OBV, AD Line, CMF 20, MFI 14
- Trend: ADX 14, CCI 20
- Position: price_vs_sma (% distance from MA)

**Performance:** ~15 seconds for 458 symbols × 200 sessions

---

#### **alert_detector.py** (280+ lines)
**Purpose:** Detect trading signals using TA-Lib
**Key Classes:**
- `TechnicalAlertDetector` - Alert detection engine

**Alert Types:**
1. **MA Crossover** - Price crosses MA (20/50/100/200)
   - Detects both above/below
   - Example: `MA_CROSS_ABOVE MA50 BULLISH`

2. **Smart Volume Spike** - Multi-factor confirmation
   - Volume > 1.5x average
   - Price breakout (20-day high)
   - RSI confirmation (not overbought)
   - MACD bullish signal
   - Candlestick pattern match
   - Result: WATCH with confidence score

3. **Breakout/Breakdown** - Price breaks resistance/support
   - 20-day high break + volume spike = BULLISH_BREAKOUT
   - 20-day low break + volume spike = BEARISH_BREAKDOWN

4. **Candlestick Patterns** - 61 patterns via TA-Lib
   - Top 10 most reliable patterns
   - Strength score (0-100)
   - Signal classification (BULLISH/BEARISH/NEUTRAL)

5. **Combined Signals** - MA+RSI+MACD scoring
   - Evaluates: trend (MA), momentum (RSI), trend strength (MACD)
   - Confidence 0-100
   - Signal: STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL

**Methods:**
- `detect_ma_crossover(symbol, df)` - Returns List[Dict]
- `detect_smart_volume_spike(symbol, df)` - Returns Optional[Dict]
- `detect_breakout(symbol, df)` - Returns List[Dict]
- `detect_candlestick_patterns(symbol, df)` - Returns List[Dict]
- `detect_combined_signals(symbol, df)` - Returns List[Dict]
- `detect_all_alerts(date, n_sessions)` - Returns Dict[str, List[Dict]]

**Performance:** ~8 seconds for all 458 symbols

---

#### **money_flow.py** (150+ lines)
**Purpose:** Calculate volume-based money flow indicators
**Key Classes:**
- `MoneyFlowAnalyzer` - Individual stock analysis

**Indicators:**
- **Chaikin Money Flow (CMF)** - 20-period, measures accumulation
- **Money Flow Index (MFI)** - 14-period RSI of volume
- **On-Balance Volume (OBV)** - Cumulative volume indicator
- **Accumulation/Distribution Line** - High-Low distance × volume
- **Volume Price Trend (VPT)** - Custom calculation

**Classification:**
- STRONG_ACCUMULATION (CMF > 0.1)
- ACCUMULATION (0 < CMF < 0.1)
- NEUTRAL (-0.1 < CMF < 0)
- DISTRIBUTION (-0.1 > CMF > -0.2)
- STRONG_DISTRIBUTION (CMF < -0.2)

**Output:** `individual_money_flow.parquet` (6.6 MB)

---

#### **sector_money_flow.py** (180+ lines)
**Purpose:** Aggregate money flow by sector with multi-timeframe analysis
**Key Classes:**
- `SectorMoneyFlowAnalyzer` - Sector-level aggregation

**Features:**
- Aggregates (Price × Volume) per sector per date
- **Multi-timeframe comparison:**
  - 1D vs previous day
  - 1W vs previous week
  - 1M vs previous month
- Inflow/Outflow % calculation
- Top 3 contributors per sector
- Sector rotation pattern identification

**Outputs:**
- `sector_money_flow_1d.parquet` (daily)
- `sector_money_flow_1w.parquet` (weekly)
- `sector_money_flow_1m.parquet` (monthly)

---

#### **sector_breadth.py** (160+ lines)
**Purpose:** Calculate breadth metrics per sector
**Key Classes:**
- `SectorBreadthAnalyzer` - Breadth calculations

**Metrics Per Sector:**
- % stocks above MA20/50/100/200
- Advancing vs Declining count
- RSI breadth (bullish/bearish/overbought/oversold)
- New highs vs New lows
- Strength score (0-100)

**Trend Classification:**
- STRONG_BULLISH (+80 to +100)
- BULLISH (+50 to +80)
- NEUTRAL (-50 to +50)
- BEARISH (-80 to -50)
- STRONG_BEARISH (-100 to -80)

**Output:** `sector_breadth_daily.parquet`

---

#### **market_regime.py** (200+ lines)
**Purpose:** Detect market conditions using multi-factor analysis
**Key Classes:**
- `MarketRegimeDetector` - Regime classification engine

**5-Factor Scoring:**
1. **Valuation Score** (25% weight) - PE percentile ranking
2. **Breadth Score** (25% weight) - % stocks in uptrend
3. **Volume Score** (15% weight) - Volume vs historical average
4. **Volatility Score** (15% weight) - ATR percentile
5. **Momentum Score** (20% weight) - MACD/RSI % bullish

**Regime Classification:**
- BUBBLE (regime_score > +70) - Risk: VERY_HIGH
- EUPHORIA (+40 to +70) - Risk: HIGH
- NEUTRAL (-40 to +40) - Risk: MEDIUM
- FEAR (-70 to -40) - Risk: HIGH
- BOTTOM (< -70) - Risk: VERY_HIGH

**Output:** `market_regime_history.parquet` (historical tracking)

---

#### **vnindex_analyzer.py** (180+ lines)
**Purpose:** Calculate TA indicators for VN-Index market overview
**Key Classes:**
- `VNIndexAnalyzer` - Market-level analysis

**Features:**
- Fetch VN-Index OHLCV from vnstock (source='vnd')
- Calculate all 18 TA indicators (same as individual stocks)
- Trend classification (STRONG_UPTREND to STRONG_DOWNTREND)
- Compare individual stocks with market

**Output:** `vnindex_indicators.parquet` (single row per date)

---

### 1.3 Data Flow Architecture

```
Raw Data (OHLCV_mktcap.parquet)
    ↓
technical_processor.py
    ├─→ SMA 20/50/100/200
    ├─→ RSI 14, MACD, Stochastic
    ├─→ Bollinger Bands, ATR
    ├─→ Volume indicators (OBV, CMF, MFI)
    └─→ Output: basic_data.parquet (40 columns)
    
basic_data.parquet + OHLCV
    ↓
alert_detector.py → alerts/daily/*.parquet + alerts/historical/*.parquet
money_flow.py → individual_money_flow.parquet
sector_breadth.py → sector_breadth_daily.parquet
sector_money_flow.py → sector_money_flow_1d/1w/1m.parquet
market_regime.py → market_regime_history.parquet
vnindex_analyzer.py → vnindex_indicators.parquet
```

---

## 2. WEBAPP/pages/technical/ - Frontend Dashboard

### 2.1 File Structure

```
WEBAPP/pages/technical/
├── __init__.py
└── technical_dashboard.py (567 lines - Production dashboard)
```

### 2.2 technical_dashboard.py - Comprehensive Overview

**Architecture:**
- Streamlit-based interactive dashboard
- 5 user inputs (ticker, days, chart options)
- 3 main tabs for visualization
- Real-time metric cards
- Full data export

**User Inputs:**
```python
st.sidebar.markdown("## Filters")
- ticker selectbox (315 liquid symbols)
- limit slider (30-500 days, default 180)
- show_volume checkbox
- show_bb checkbox (Bollinger Bands)
- Refresh Data button
```

**Content Structure:**

1. **Metric Cards** (5 KPI cards)
   - Close Price with delta %
   - RSI (14) with overbought/oversold status
   - Price vs SMA50 (% distance)
   - ADX (14) with trend strength
   - MACD with bullish/bearish indicator

2. **Tab 1: Price & Volume**
   - Candlestick chart with volume subplot
   - 3 Moving Averages (SMA 20/50/200)
   - Optional Bollinger Bands (upper/middle/lower)
   - Volume bars (green/red by close direction)
   - MA Signal Summary table (price distance)
   - Trend Analysis (SMA direction + Golden/Death cross)

3. **Tab 2: Oscillators**
   - RSI 14 with overbought/oversold zones
   - MACD with histogram + signal line
   - Stochastic K/D with zones
   - CCI 20 with bands

4. **Tab 3: Data Tables**
   - Price & Moving Averages table
   - Volatility indicators (ATR, BB width)
   - Momentum indicators (RSI, MACD, Stochastic, CCI, MFI)
   - Volume indicators (Volume, OBV, CMF)
   - CSV download button

**Caching Strategy:**
- Uses `@st.cache_data(ttl=3600)` for 1-hour caching
- Refresh button clears cache on demand

**Data Source:**
- Calls `TechnicalService.get_technical_data(ticker, limit=limit)`
- Returns DataFrame with 40 columns from `basic_data.parquet`

**Design Theme:**
- Financial Editorial Theme
- Dark terminal with vibrant accents
- Plotly charts with custom colors

---

## 3. WEBAPP/services/technical_service.py - Data Access Layer

### 3.1 Service Overview

**Purpose:** Bridge between frontend dashboard and parquet data files

**Key Class:**
- `TechnicalService` - Data loading with caching support

**Constructor:**
```python
def __init__(self, data_root: Optional[Path] = None)
    # Initializes: data_path = PROJECT_ROOT/DATA/processed/technical
    # Validates path existence
    # Lazy-loads SymbolLoader
```

**Methods:**

1. **get_technical_data(ticker, limit, start_date, end_date)** → DataFrame
   - Loads from `basic_data.parquet`
   - Filters by symbol
   - Applies date filters (optional)
   - Returns sorted by date, limited to N most recent rows

2. **get_latest_indicators(ticker)** → Dict
   - Returns latest row as dictionary
   - Convenience method for KPI cards

3. **get_available_tickers(entity_type)** → List[str]
   - Returns 315 liquid symbols from SymbolLoader
   - Fallback to parquet if SymbolLoader unavailable
   - Supports entity type filtering (COMPANY, BANK, INSURANCE, SECURITY)

4. **get_market_breadth()** → DataFrame
   - Loads from `market_breadth/` directory
   - Returns latest file by modification time

5. **get_sector_breadth(sector)** → DataFrame
   - Loads from `sector_breadth/` directory
   - Optional sector filtering

**Error Handling:**
- FileNotFoundError for missing data paths
- Returns empty DataFrame on missing data
- Fallback mechanisms for SymbolLoader

---

## 4. DATA/processed/technical/ - Output File Organization

### 4.1 Data Structure

```
DATA/processed/technical/
├── basic_data.parquet                      (18.6 MB, 40 columns)
│   └── Core TA data: OHLCV + 18 indicators
│
├── alerts/                                  (Latest + Historical)
│   ├── daily/
│   │   ├── ma_crossover_latest.parquet     (~50 KB)
│   │   ├── volume_spike_latest.parquet     (~30 KB)
│   │   ├── breakout_latest.parquet         (~20 KB)
│   │   ├── patterns_latest.parquet         (~40 KB)
│   │   └── combined_latest.parquet         (~60 KB)
│   │
│   └── historical/
│       ├── ma_crossover_history.parquet
│       ├── volume_spike_history.parquet
│       ├── breakout_history.parquet
│       ├── patterns_history.parquet
│       └── combined_history.parquet
│
├── money_flow/
│   ├── individual_money_flow.parquet       (6.6 MB)
│   ├── sector_money_flow.parquet           (Legacy)
│   ├── sector_money_flow_1d.parquet        (1-day window)
│   ├── sector_money_flow_1w.parquet        (1-week window)
│   └── sector_money_flow_1m.parquet        (1-month window)
│
├── market_breadth/
│   └── market_breadth_daily.parquet        (Market-wide metrics)
│
├── sector_breadth/
│   └── sector_breadth_daily.parquet        (Per-sector breadth)
│
├── market_regime/
│   └── market_regime_history.parquet       (Historical regimes)
│
└── vnindex/
    └── vnindex_indicators.parquet          (VN-Index TA)
```

### 4.2 Schema Details

**basic_data.parquet (40 columns)**
- date, symbol (2)
- OHLCV (5): open, high, low, close, volume
- SMA (4): sma_20, sma_50, sma_100, sma_200
- EMA (2): ema_20, ema_50
- Momentum (6): rsi_14, macd, macd_signal, macd_hist, stoch_k, stoch_d
- Volatility (5): bb_upper, bb_middle, bb_lower, bb_width, atr_14
- Volume (4): obv, ad_line, cmf_20, mfi_14
- Trend (2): adx_14, cci_20
- Position (3): price_vs_sma20, price_vs_sma50, price_vs_sma200
- Total: 40 columns

**Alerts Schema Variations:**
- MA Crossover: symbol, date, alert_type, ma_period, price, ma_value, signal
- Volume Spike: symbol, volume, volume_ratio, signal, confirmations, confidence
- Breakout: symbol, alert_type, price, resistance_level, volume_confirmed, signal
- Pattern: symbol, pattern_name, signal, strength, price
- Combined: symbol, ma_trend, rsi_14, macd_signal, overall_signal, confidence, score

**Money Flow Schema:**
- Individual: symbol, date, cmf_20, mfi_14, obv, ad_line, vpt, money_flow_signal
- Sector: sector_code, money_flow, inflow_pct, flow_signal, top_contributors

**Sector Breadth Schema:**
- sector_code, date, ma20_count, ma50_count, ma100_count, ma200_count, advancing, declining, strength_score, trend_class

**Market Regime Schema:**
- date, regime_score, regime_class, risk_level, valuation_score, breadth_score, volume_score, volatility_score, momentum_score

---

## 5. Code Patterns & Conventions

### 5.1 Class Design Pattern

**Analyzer Pattern (Consistent across all calculators):**
```python
class TechnicalProcessor:
    def __init__(self, ohlcv_path: str):
        self.ohlcv_path = Path(ohlcv_path)
        # Validate path exists
        
    def load_data(self, n_sessions: int = 200) -> pd.DataFrame:
        # Load and prepare OHLCV data
        
    def calculate_indicators_for_symbol(self, df: pd.DataFrame) -> pd.DataFrame:
        # Single symbol calculation
        # Uses TA-Lib for performance
```

**Common Methods:**
- `load_data()` - Prepare raw data
- `calculate_*()` - Main calculation
- `_get_sector()` - Internal helper for SectorRegistry
- `_detect_*()` - Alert detection helpers

### 5.2 Data Processing Patterns

**TA-Lib Usage:**
```python
# All indicators use TA-Lib (not pandas)
import talib

# Convert to numpy first
close = df['close'].values.astype(float)
high, low, volume = df['high'].values.astype(float), ...

# Calculate using TA-Lib (10-100x faster)
df['sma_20'] = talib.SMA(close, timeperiod=20)
df['rsi_14'] = talib.RSI(close, timeperiod=14)
macd, signal, hist = talib.MACD(close, ...)
```

**Vectorized Operations:**
```python
# Vectorized calculations for efficiency
df['price_vs_sma50'] = (df['close'] - df['sma_50']) / df['sma_50'] * 100
df['money_flow'] = df['close'] * df['volume']
```

**Registry Pattern:**
```python
# Use SectorRegistry for symbol→sector mapping
from config.registries import SectorRegistry

sector_reg = SectorRegistry()
sector = sector_reg.get_sector(ticker)  # Returns sector_code
```

### 5.3 File I/O Pattern

**Input:**
```python
# Read from raw data
df = pd.read_parquet("DATA/raw/ohlcv/OHLCV_mktcap.parquet")
```

**Output:**
```python
# Write to processed data
output_path = Path("DATA/processed/technical/basic_data.parquet")
df.to_parquet(output_path, index=False)
```

**Path Resolution:**
```python
# Always use pathlib.Path
from pathlib import Path

path = Path("DATA/raw/ohlcv/OHLCV_mktcap.parquet")
if not path.exists():
    raise FileNotFoundError(f"File not found: {path}")
```

---

## 6. Data Flow & Integration Points

### 6.1 Daily Update Pipeline

**Master Script:** `PROCESSORS/pipelines/run_all_daily_updates.py`

**Pipeline Order:**
```
1. OHLCV Update (ohlcv_daily_updater.py)
   └─→ DATA/raw/ohlcv/OHLCV_mktcap.parquet

2. Technical Analysis Complete
   ├─→ technical_processor.py
   │   └─→ DATA/processed/technical/basic_data.parquet
   ├─→ alert_detector.py
   │   └─→ DATA/processed/technical/alerts/{daily,historical}/*
   ├─→ money_flow.py
   │   └─→ DATA/processed/technical/money_flow/individual_money_flow.parquet
   ├─→ sector_money_flow.py
   │   └─→ DATA/processed/technical/money_flow/sector_money_flow_1d/1w/1m.parquet
   ├─→ sector_breadth.py
   │   └─→ DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet
   ├─→ market_regime.py
   │   └─→ DATA/processed/technical/market_regime/market_regime_history.parquet
   └─→ vnindex_analyzer.py
       └─→ DATA/processed/technical/vnindex/vnindex_indicators.parquet

3. Valuation Update (separate pipeline)

4. Sector Analysis Update (separate pipeline)
```

**Execution Time:** ~32 seconds total (458 symbols × 200 sessions)

### 6.2 Dashboard Integration Flow

```
WEBAPP/main_app.py
    └─→ /pages/technical_dashboard.py
        └─→ TechnicalService.get_technical_data()
            ├─→ DATA/processed/technical/basic_data.parquet
            ├─→ Cached for 1 hour (ttl=3600)
            └─→ Display in 5-tab layout

User Interactions:
├─→ Ticker selector → Filter DataFrame
├─→ Days slider → Limit rows
├─→ Volume/BB toggles → Conditional rendering
└─→ Refresh button → Clear cache
```

### 6.3 Registry Integration

**SymbolLoader Access:**
```python
from WEBAPP.core.symbol_loader import SymbolLoader

loader = SymbolLoader()
symbols = loader.get_all_symbols()  # 315 liquid symbols
symbols = loader.get_symbols_by_entity('COMPANY')  # By entity type
```

**SectorRegistry Access:**
```python
from config.registries import SectorRegistry

sector_reg = SectorRegistry()
sector = sector_reg.get_sector('ACB')  # Returns 'BANKING'
peers = sector_reg.get_peers('ACB')  # All banking tickers
```

---

## 7. Naming Conventions & Standards

### 7.1 File & Module Naming
- **Files:** `snake_case.py` (e.g., `technical_processor.py`)
- **Classes:** `CamelCase` (e.g., `TechnicalProcessor`)
- **Functions/Variables:** `snake_case` (e.g., `calculate_indicators`)
- **DataFrames:** `snake_case_df` suffix (e.g., `price_df`, `alert_df`)

### 7.2 Column Naming
- OHLCV: open, high, low, close, volume
- Moving Averages: sma_20, sma_50, sma_100, sma_200, ema_20, ema_50
- Indicators: rsi_14, macd, macd_signal, macd_hist, stoch_k, stoch_d
- Volatility: bb_upper, bb_middle, bb_lower, bb_width, atr_14
- Volume: obv, ad_line, cmf_20, mfi_14, vpt
- Trend: adx_14, cci_20
- Position: price_vs_sma20, price_vs_sma50, price_vs_sma200

### 7.3 Enumerations & Constants
- Signal classification: 'BULLISH', 'BEARISH', 'NEUTRAL'
- Alert types: 'MA_CROSS_ABOVE', 'MA_CROSS_BELOW', 'BREAKOUT_UP', 'BREAKOUT_DOWN'
- Regime classes: 'BUBBLE', 'EUPHORIA', 'NEUTRAL', 'FEAR', 'BOTTOM'
- Money flow signals: 'STRONG_ACCUMULATION', 'ACCUMULATION', 'NEUTRAL', 'DISTRIBUTION', 'STRONG_DISTRIBUTION'

---

## 8. Performance Characteristics

### 8.1 Execution Benchmarks

**Complete TA Pipeline (458 symbols × 200 sessions):**
| Component | Time | Notes |
|-----------|------|-------|
| Technical Indicators | ~15s | TA-Lib vectorized |
| Alert Detection | ~8s | 5 alert types |
| Money Flow | ~6s | Individual + sector |
| Sector Analysis | ~2s | Breadth + regime |
| **Total** | **~32s** | Production-ready |

### 8.2 Data Size Characteristics

| File | Size | Rows | Cols | Update |
|------|------|------|------|--------|
| basic_data.parquet | 18.6 MB | ~91,600 | 40 | Daily |
| individual_money_flow | 6.6 MB | ~91,600 | 8 | Daily |
| Alerts (combined) | ~200 KB | Varies | 7 | Daily |
| sector_money_flow_1d | ~500 KB | ~19 sectors | 6 | Daily |
| sector_breadth_daily | ~300 KB | ~19 sectors | 12 | Daily |
| market_regime_history | ~100 KB | Appended | 10 | Daily |

### 8.3 Optimization Techniques

**Why Fast?**
- ✅ **TA-Lib** - C-based library (10-100x faster than pandas)
- ✅ **Vectorized Operations** - NumPy arrays instead of loops
- ✅ **Efficient Parquet** - Columnar compression
- ✅ **Lazy Loading** - Only 200 sessions per symbol (not full history)
- ✅ **Streamlit Caching** - 1-hour TTL for dashboard

---

## 9. Key Strengths & Architecture Quality

### 9.1 Design Excellence

**Strengths:**
1. **Modular Architecture**
   - Each analyzer is independent and reusable
   - Clear separation of concerns
   - Easy to extend with new indicators

2. **Performance-First Design**
   - Uses TA-Lib instead of pandas (10-100x faster)
   - Vectorized NumPy operations
   - Efficient parquet format

3. **Comprehensive Alert System**
   - 5 distinct alert types
   - Multi-factor confirmation (volume spike)
   - Candlestick pattern detection (61 patterns)
   - Combined scoring (MA+RSI+MACD)

4. **Production-Ready Dashboard**
   - 567 lines of well-structured Streamlit
   - 5 KPI metrics
   - 3-tab layout with comprehensive data
   - Caching for performance
   - CSV export

5. **Registry Pattern**
   - Uses SectorRegistry for consistency
   - Supports entity-type filtering
   - Fallback mechanisms

6. **Comprehensive Documentation**
   - README.md (426 lines) with examples
   - Inline comments and docstrings
   - Schema documentation in README

### 9.2 Code Quality Metrics

- **Consistency:** Uniform class structure across all analyzers
- **Error Handling:** Path validation, FileNotFoundError, fallback mechanisms
- **Type Hints:** Optional type hints in service layer
- **Logging:** Consistent logging with INFO/WARNING/ERROR levels
- **Testing:** No unit tests found (potential gap)

---

## 10. Integration Checklist

### 10.1 External Dependencies

**Required Packages:**
- pandas (≥1.0.0) - Data manipulation
- numpy (≥1.19.0) - Vectorized operations
- talib - Technical indicators (C-based)
- vnstock_data - OHLCV data source

**Optional:**
- plotly - Streamlit charting
- streamlit - Frontend framework

### 10.2 Data Dependencies

**Input Files:**
- `DATA/raw/ohlcv/OHLCV_mktcap.parquet` - Must exist before TA update
- `config/registries/sector_registry.json` - For sector mapping

**Output Files:**
- All written to `DATA/processed/technical/`
- Append-only: historical files grow daily
- Overwrite daily: latest alert files

### 10.3 Service Dependencies

**Frontend Services Consumed By:**
- `TechnicalService` ← Used by technical_dashboard.py
- Can be extended to other dashboards (analysis pages, etc.)

**Backend Services Produced For:**
- Valuation calculators (use basic_data.parquet for PE calculations)
- Sector analysis (uses alerts, breadth, regime)
- Market regime detection (uses technical data)

---

## 11. Known Limitations & Gaps

### 11.1 Code Coverage

**Missing Components:**
- ❌ No unit tests for indicator calculations
- ❌ No integration tests for pipeline
- ❌ No performance benchmarks (manual timing only)

### 11.2 Feature Limitations

**Alerts:**
- ✅ 5 alert types implemented
- ⚠️ No alert severity/priority system
- ⚠️ No alert notification system (email/SMS)

**Money Flow:**
- ✅ Individual and sector aggregation
- ⚠️ No multi-symbol comparison
- ⚠️ Limited historical depth tracking

**Dashboard:**
- ✅ 3-tab comprehensive layout
- ⚠️ No alerts tab (should exist)
- ⚠️ No money flow tab visualization
- ⚠️ No regime visualization

### 11.3 Documentation Gaps

**Missing:**
- API documentation for TechnicalService
- Architecture diagram
- Deployment guide
- Troubleshooting guide (partially in README)

---

## 12. Recommendations for Enhancement

### 12.1 Short-Term (1-2 weeks)

1. **Add Unit Tests**
   - Test TechnicalProcessor indicators
   - Test AlertDetector for edge cases
   - Test service layer data loading

2. **Expand Dashboard Tabs**
   - Add "🚨 Trading Alerts" tab
   - Add "💰 Money Flow" tab
   - Add "🌡️ Market Regime" tab

3. **Enhance Documentation**
   - Create API reference for TechnicalService
   - Add deployment guide
   - Create troubleshooting FAQ

### 12.2 Medium-Term (1-2 months)

1. **Alert System Enhancement**
   - Add alert severity levels (CRITICAL, WARNING, INFO)
   - Implement alert notification system
   - Add alert history/filtering in UI

2. **Money Flow Enhancement**
   - Add money flow heatmap visualization
   - Add sector rotation analysis
   - Compare individual stocks with sector flows

3. **Performance Optimization**
   - Profile and optimize alert detection
   - Consider Polars for faster parquet operations
   - Cache intermediate calculations

### 12.3 Long-Term (3+ months)

1. **Machine Learning Integration**
   - Train ML models on historical alerts
   - Predict alert reliability
   - Pattern recognition for similar market conditions

2. **Advanced Analytics**
   - Add correlation analysis (sector vs index)
   - Add volatility surface analysis
   - Add sentiment scoring

3. **Real-Time Features**
   - Stream price updates during market hours
   - Real-time alert generation
   - WebSocket support for live data

---

## 13. Summary & File Listing

### 13.1 Complete File Inventory

**PROCESSORS/technical/ (7 files)**
1. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/technical_processor.py` (150+ lines)
2. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/alert_detector.py` (280+ lines)
3. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/money_flow.py` (150+ lines)
4. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/sector_money_flow.py` (180+ lines)
5. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/sector_breadth.py` (160+ lines)
6. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/market_regime.py` (200+ lines)
7. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/indicators/vnindex_analyzer.py` (180+ lines)
8. `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/ohlcv/ohlcv_daily_updater.py` (200+ lines)

**WEBAPP/pages/technical/ (2 files)**
1. `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/technical/technical_dashboard.py` (567 lines - Core dashboard)
2. `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/pages/technical/__init__.py` (Empty)

**WEBAPP/services/ (1 file)**
1. `/Users/buuphan/Dev/Vietnam_dashboard/WEBAPP/services/technical_service.py` (165 lines - Data service)

**DATA/processed/technical/ (25+ output files)**
- basic_data.parquet (18.6 MB)
- alerts/{daily,historical}/* (5 daily + 5 historical)
- money_flow/* (4 timeframe files)
- market_breadth/, sector_breadth/, market_regime/, vnindex/ (1 each)

### 13.2 Key Statistics

- **Total TA Code:** ~1,500 lines (processors)
- **Dashboard Code:** 567 lines (Streamlit)
- **Service Code:** 165 lines (data access)
- **Output Files:** 25+ parquet files daily
- **Data Volume:** ~25 MB processed daily
- **Execution Time:** ~32 seconds
- **Coverage:** 458 stocks × 19 sectors × 200 sessions

### 13.3 Architecture Maturity

- **Status:** Production-Ready ✅
- **Completeness:** 95% feature-complete
- **Code Quality:** High (consistent patterns, good documentation)
- **Performance:** Excellent (TA-Lib + vectorization)
- **Maintainability:** Good (modular, clear separation)
- **Test Coverage:** Low (no unit tests yet)

---

## Unresolved Questions

1. **Alert Notifications:** Should alerts trigger email/SMS notifications? Currently silent.
2. **Alert Severity:** Should alerts have severity levels (CRITICAL/WARNING/INFO)?
3. **Dashboard Missing Tabs:** Why no alerts/money flow visualization in dashboard?
4. **Historical Alerts:** Should older alerts be available for filtering/analysis?
5. **Real-Time Updates:** Is real-time streaming needed during market hours?
6. **Performance Target:** Is 32 seconds acceptable or should we optimize further?

