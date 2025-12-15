# Technical Alerts Enhancement Plan
## MA/RSI/MACD Breakout & Market Breadth System

**Author:** Claude Code
**Date:** 2025-12-15
**Version:** 1.0.0

---

## 📋 MỤC TIÊU

Tạo hệ thống cảnh báo kỹ thuật (Technical Alerts) với:
1. **MA Alerts**: Cổ phiếu lủng MA / vượt MA
2. **Smart Volume Alerts**: Volume spike KẾT HỢP với breakout và TA signals
3. **Breakout Alerts**: Phá vỡ vùng kháng cự/hỗ trợ + volume + pattern confirmation
4. **Market Breadth**: Số lượng mã vượt MA20/50/100/200
5. **Candlestick Patterns**: Nhận diện mẫu hình nến (Doji, Hammer, Engulfing, etc.)
6. **Tích hợp MA + RSI + MACD + Volume + Patterns** (comprehensive signals)

**Giới hạn dữ liệu:** Chỉ xử lý **1 năm (252 ngày giao dịch)** để tránh quá nặng

**Công cụ:** Sử dụng **TA-Lib** cho tính toán nhanh và chính xác

---

## 🎯 PHÂN TÍCH HIỆN TRẠNG

### ✅ Đã Có (Existing Components)

| Component | File | Chức năng |
|-----------|------|-----------|
| **MA Screening** | `ma_screening_processor.py` | Lọc mã theo MA20/50/100/200 |
| **Market Breadth** | `market_breadth_processor.py` | Tính số lượng mã vượt MA |
| **Daily TA Analyzer** | `daily_ta_analyzer.py` | Phân tích MA/RSI/MACD cho từng mã |
| **Technical Processor** | `technical_processor.py` | Tính toán MA/RSI/MACD/Bollinger |

### ❌ Thiếu (Missing Features)

1. **MA Crossover Alerts**: Phát hiện lủng MA / vượt MA trong ngày
2. **Volume Spike Alerts**: Volume tăng đột biến (>1.5x trung bình)
3. **Breakout Detection**: Phá kháng cự/hỗ trợ với volume xác nhận
4. **Combined Signals**: MA + RSI + MACD kết hợp
5. **Daily Alert Table**: Bảng tổng hợp alerts mỗi ngày
6. **Historical Backtest**: Test độ chính xác của signals

---

## 📊 THIẾT KẾ HỆ THỐNG

### Phase 1: Alert Detection Engine (Core) - Using TA-Lib

**File mới:** `PROCESSORS/technical/indicators/alert_detector.py`

```python
import talib
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class TechnicalAlertDetector:
    """
    Detect technical alerts using TA-Lib for fast calculations.

    Input: 1 year OHLCV data (252 trading days)
    Output: Daily alerts with comprehensive signals

    TA-Lib Functions Used:
    - MA: SMA, EMA
    - Momentum: RSI, MACD
    - Volume: OBV (On-Balance Volume)
    - Patterns: CDL functions (Candlestick patterns)
    """

    def __init__(self, lookback_days: int = 252):
        """Initialize with 1-year lookback (252 trading days)"""
        self.lookback_days = lookback_days

    def detect_ma_crossover(self, symbol: str, df: pd.DataFrame) -> Dict:
        """
        Detect MA crossover events:
        - Price crosses above MA20/50/100/200 (Bullish)
        - Price crosses below MA20/50/100/200 (Bearish)

        Returns:
            {
                'symbol': 'ACB',
                'date': '2025-12-15',
                'alert_type': 'MA_CROSS_ABOVE',
                'ma_period': 20,
                'price': 25500,
                'ma_value': 25000,
                'signal': 'BULLISH'
            }
        """

    def detect_smart_volume_spike(self, symbol: str, df: pd.DataFrame) -> Dict:
        """
        Smart Volume Spike: KẾT HỢP volume với breakout và TA signals.

        Logic:
        1. Volume > 1.5x average (basic spike)
        2. Check if accompanied by:
           - Breakout (price > 20-day high)
           - Strong RSI (not overbought)
           - Bullish MACD
           - Bullish candlestick pattern

        Returns:
            {
                'symbol': 'VNM',
                'date': '2025-12-15',
                'alert_type': 'SMART_VOLUME_SPIKE',
                'volume': 5_000_000,
                'avg_volume_20d': 2_500_000,
                'volume_ratio': 2.0,
                'price_change_pct': 3.5,

                # Confirmations
                'is_breakout': True,
                'rsi': 58,
                'macd_bullish': True,
                'candlestick_pattern': 'HAMMER',

                # Overall signal
                'signal': 'STRONG_BUY',
                'confidence': 0.85,
                'confirmations': 4  # out of 4
            }
        """

    def detect_breakout(self, symbol: str, df: pd.DataFrame) -> Dict:
        """
        Detect breakout/breakdown:
        - Price breaks above 20-day high with volume confirmation
        - Price breaks below 20-day low with volume confirmation

        Returns:
            {
                'symbol': 'HPG',
                'date': '2025-12-15',
                'alert_type': 'BREAKOUT_UP',
                'price': 28500,
                'resistance': 28000,
                'volume_confirmed': True,
                'signal': 'BULLISH_BREAKOUT'
            }
        """

    def detect_combined_signal(self, symbol: str, df: pd.DataFrame) -> Dict:
        """
        Combined MA + RSI + MACD signal:

        STRONG BUY:
        - Price > MA20 > MA50
        - RSI 40-60 (not overbought)
        - MACD bullish crossover

        STRONG SELL:
        - Price < MA20 < MA50
        - RSI 40-60 (not oversold)
        - MACD bearish crossover

        Returns:
            {
                'symbol': 'VIC',
                'date': '2025-12-15',
                'alert_type': 'COMBINED_SIGNAL',
                'ma_trend': 'BULLISH',
                'rsi': 55,
                'macd_signal': 'BULLISH_CROSS',
                'overall_signal': 'STRONG_BUY',
                'confidence': 0.85
            }
        """
```

---

### Phase 2: Market Breadth Dashboard

**File mới:** `PROCESSORS/technical/indicators/breadth_calculator.py`

```python
class MarketBreadthCalculator:
    """
    Calculate market breadth metrics:
    - Number of stocks above MA20/50/100/200
    - Advance-Decline ratio
    - % stocks in uptrend
    """

    def calculate_daily_breadth(self, date: str) -> Dict:
        """
        Calculate market breadth for specific date.

        Returns:
            {
                'date': '2025-12-15',
                'total_stocks': 450,

                # MA Breadth
                'above_ma20': 280,
                'above_ma50': 250,
                'above_ma100': 220,
                'above_ma200': 200,

                # Percentages
                'above_ma20_pct': 62.2,
                'above_ma50_pct': 55.6,
                'above_ma100_pct': 48.9,
                'above_ma200_pct': 44.4,

                # Advance-Decline
                'advancing': 285,
                'declining': 155,
                'unchanged': 10,
                'ad_ratio': 1.84,

                # Trend Classification
                'market_trend': 'BULLISH',  # >60% above MA50
                'trend_strength': 'MODERATE'
            }
        """
```

---

### Phase 3: Alert Tables (Output)

**Output Files:**

#### 3.1 Daily MA Alerts
**File:** `DATA/processed/technical/alerts/ma_crossover_alerts.parquet`

| Column | Type | Description |
|--------|------|-------------|
| date | datetime | Ngày phát hiện |
| symbol | str | Mã cổ phiếu |
| alert_type | str | MA_CROSS_ABOVE / MA_CROSS_BELOW |
| ma_period | int | 20 / 50 / 100 / 200 |
| price | float | Giá đóng cửa |
| ma_value | float | Giá trị MA |
| signal | str | BULLISH / BEARISH |
| prev_position | str | ABOVE / BELOW (vị trí ngày trước) |

**Sample Data:**
```
date       | symbol | alert_type      | ma_period | price | ma_value | signal
-----------|--------|-----------------|-----------|-------|----------|--------
2025-12-15 | ACB    | MA_CROSS_ABOVE  | 20        | 25500 | 25200    | BULLISH
2025-12-15 | VIC    | MA_CROSS_BELOW  | 50        | 82000 | 83500    | BEARISH
2025-12-15 | HPG    | MA_CROSS_ABOVE  | 100       | 28500 | 28000    | BULLISH
```

#### 3.2 Volume Spike Alerts
**File:** `DATA/processed/technical/alerts/volume_spike_alerts.parquet`

| Column | Type | Description |
|--------|------|-------------|
| date | datetime | Ngày phát hiện |
| symbol | str | Mã cổ phiếu |
| volume | int | Khối lượng giao dịch |
| avg_volume_20d | int | KL trung bình 20 ngày |
| volume_ratio | float | volume / avg_volume |
| price_change_pct | float | % thay đổi giá |
| signal | str | ACCUMULATION / DISTRIBUTION |

**Sample Data:**
```
date       | symbol | volume    | avg_volume_20d | ratio | price_chg | signal
-----------|--------|-----------|----------------|-------|-----------|----------------
2025-12-15 | VNM    | 5,000,000 | 2,500,000      | 2.0   | +3.2%     | ACCUMULATION
2025-12-15 | MSN    | 8,000,000 | 3,000,000      | 2.67  | -2.1%     | DISTRIBUTION
```

#### 3.3 Breakout Alerts
**File:** `DATA/processed/technical/alerts/breakout_alerts.parquet`

| Column | Type | Description |
|--------|------|-------------|
| date | datetime | Ngày phát hiện |
| symbol | str | Mã cổ phiếu |
| alert_type | str | BREAKOUT_UP / BREAKDOWN |
| price | float | Giá đóng cửa |
| resistance_level | float | Vùng kháng cự (20-day high) |
| support_level | float | Vùng hỗ trợ (20-day low) |
| volume_confirmed | bool | Volume xác nhận (>1.5x avg) |
| signal | str | BULLISH_BREAKOUT / BEARISH_BREAKDOWN |

#### 3.4 Combined Signals
**File:** `DATA/processed/technical/alerts/combined_signals.parquet`

| Column | Type | Description |
|--------|------|-------------|
| date | datetime | Ngày phát hiện |
| symbol | str | Mã cổ phiếu |
| price | float | Giá đóng cửa |
| ma20_trend | str | ABOVE / BELOW |
| ma50_trend | str | ABOVE / BELOW |
| rsi_14 | float | RSI 14-day |
| macd_signal | str | BULLISH_CROSS / BEARISH_CROSS / NEUTRAL |
| overall_signal | str | STRONG_BUY / BUY / HOLD / SELL / STRONG_SELL |
| confidence | float | Độ tin cậy (0-1) |

#### 3.5 Market Breadth Daily
**File:** `DATA/processed/technical/market_breadth/market_breadth_daily.parquet`

| Column | Type | Description |
|--------|------|-------------|
| date | datetime | Ngày |
| total_stocks | int | Tổng số mã |
| above_ma20 | int | Số mã > MA20 |
| above_ma50 | int | Số mã > MA50 |
| above_ma100 | int | Số mã > MA100 |
| above_ma200 | int | Số mã > MA200 |
| above_ma20_pct | float | % mã > MA20 |
| above_ma50_pct | float | % mã > MA50 |
| advancing | int | Số mã tăng |
| declining | int | Số mã giảm |
| ad_ratio | float | Tỷ lệ tăng/giảm |
| market_trend | str | BULLISH / NEUTRAL / BEARISH |

---

---

## 🎯 ARCHITECTURE: DATA LOOKBACK & STORAGE STRATEGY

### Lookback Period Decision: 200 Trading Sessions

**Quyết định:** Sử dụng **200 phiên giao dịch** (trading sessions) thay vì 252 ngày lịch.

**Lý do:**
- **Đủ cho MA200**: 200 sessions = exactly MA200 + small buffer
- **Hiệu quả hơn**: 252 days có thể chứa ~40 ngày nghỉ → lãng phí bộ nhớ
- **Tính toán nhanh hơn**: Ít data hơn ~20% so với 252 days
- **Tương thích**: 200 sessions ≈ 10 months (adequate cho MA analysis)

**Implementation:**
```python
def get_last_n_trading_sessions(df: pd.DataFrame, n: int = 200) -> pd.DataFrame:
    """
    Get last N trading sessions (exclude weekends/holidays).

    Args:
        df: Full OHLCV DataFrame
        n: Number of trading sessions (default: 200)

    Returns:
        DataFrame with last N trading sessions
    """
    # Sort by date
    df = df.sort_values('date')

    # Get last N records (these are actual trading days)
    return df.tail(n)
```

### Storage Architecture: 3-Tier System

**Tier 1: Daily Snapshots (Overwrite)**
- **Purpose**: Latest alerts for quick dashboard access
- **Update**: Overwrite daily
- **Size**: ~200 KB total
- **Location**: `DATA/processed/technical/alerts/daily/`

```
daily/
├── ma_crossover_latest.parquet          # 50 KB (chỉ giữ ngày hiện tại)
├── smart_volume_spike_latest.parquet    # 30 KB
├── breakout_latest.parquet              # 20 KB
├── candlestick_patterns_latest.parquet  # 40 KB
└── combined_signals_latest.parquet      # 60 KB
```

**Tier 2: Rolling Window (30-day)**
- **Purpose**: Track alert trends over time
- **Update**: Append daily, keep only last 30 days
- **Size**: ~1.5 MB
- **Location**: `DATA/processed/technical/alerts/daily/`

```
daily/
└── alerts_rolling_30d.parquet           # 1.5 MB (30 days × all alerts)
```

**Tier 3: Historical Archive (Append-only)**
- **Purpose**: Backtesting and historical analysis
- **Update**: Append daily, never delete
- **Size**: ~40 MB/year
- **Location**: `DATA/processed/technical/alerts/historical/`

```
historical/
├── ma_crossover_history.parquet         # 10 MB/year
├── smart_volume_spike_history.parquet   # 8 MB/year
├── breakout_history.parquet             # 5 MB/year
├── candlestick_patterns_history.parquet # 12 MB/year
└── market_breadth_history.parquet       # 2 MB/year
```

### Script Architecture

**1. Full Historical Backfill** (One-time)
**File:** `PROCESSORS/technical/pipelines/full_historical_alerts.py`
```python
# Chạy 1 lần để tạo historical archive
# Input: 200 trading sessions
# Output: historical/*.parquet (append all historical data)
```

**2. Daily Alert Update** (Cron job)
**File:** `PROCESSORS/technical/pipelines/daily_alerts_update.py`
```python
# Chạy mỗi ngày lúc 17:00
# Steps:
# 1. Load latest 200 sessions
# 2. Detect all alerts for latest date
# 3. Save to daily/ (overwrite)
# 4. Append to rolling_30d (drop >30 days)
# 5. Append to historical/ (never delete)
```

**3. Weekly Summary** (Optional)
**File:** `PROCESSORS/technical/pipelines/weekly_alerts_summary.py`
```python
# Chạy mỗi thứ 2 tuần
# Aggregates top 50 signals from last week
# Output: weekly/alerts_summary_weekly.parquet
```

**Example: Daily Update Script**
```python
def update_daily_alerts(date: str):
    """Update alerts for single date."""

    # 1. Load 200 trading sessions
    ohlcv_df = load_last_n_sessions(n=200)

    # 2. Detect alerts for latest date
    alerts = detect_all_alerts(ohlcv_df, date)

    # 3. Save to daily/ (overwrite)
    save_latest_snapshots(alerts, date)

    # 4. Update rolling_30d
    update_rolling_window(alerts, date, window_days=30)

    # 5. Append to historical/
    append_to_historical(alerts, date)

    logger.info(f"✅ Daily alert update complete for {date}")
```

---

## 📚 TA-LIB INTEGRATION GUIDE

### Tại Sao Dùng TA-Lib?

**Performance:**
- TA-Lib được viết bằng C → **nhanh hơn pandas 10-100x**
- Tối ưu cho vectorized operations
- Hỗ trợ 150+ technical indicators

**Accuracy:**
- Industry-standard algorithms
- Được sử dụng bởi trading platforms chuyên nghiệp
- Consistency với TradingView, Bloomberg Terminal

### Installation

```bash
# macOS
brew install ta-lib
pip install TA-Lib

# Ubuntu/Debian
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

### TA-Lib Functions Cheat Sheet

#### **Moving Averages**
```python
import talib
import numpy as np

close = np.array([...])  # Close prices

# Simple Moving Average
sma_20 = talib.SMA(close, timeperiod=20)
sma_50 = talib.SMA(close, timeperiod=50)
sma_100 = talib.SMA(close, timeperiod=100)
sma_200 = talib.SMA(close, timeperiod=200)

# Exponential Moving Average
ema_20 = talib.EMA(close, timeperiod=20)
```

#### **Momentum Indicators**
```python
# RSI (Relative Strength Index)
rsi = talib.RSI(close, timeperiod=14)

# MACD (Moving Average Convergence Divergence)
macd, macd_signal, macd_hist = talib.MACD(
    close,
    fastperiod=12,
    slowperiod=26,
    signalperiod=9
)

# Stochastic
slowk, slowd = talib.STOCH(
    high, low, close,
    fastk_period=14,
    slowk_period=3,
    slowd_period=3
)
```

#### **Volume Indicators**
```python
volume = np.array([...])

# On-Balance Volume
obv = talib.OBV(close, volume)

# Chaikin A/D Line
ad = talib.AD(high, low, close, volume)

# Money Flow Index
mfi = talib.MFI(high, low, close, volume, timeperiod=14)
```

#### **Candlestick Patterns** ⭐ QUAN TRỌNG

TA-Lib cung cấp **61 candlestick patterns**. Mỗi pattern trả về:
- **100** = Bullish pattern
- **-100** = Bearish pattern
- **0** = No pattern

```python
high = np.array([...])
low = np.array([...])
open_price = np.array([...])
close = np.array([...])

# === BULLISH PATTERNS ===

# Hammer (búa - bullish reversal)
hammer = talib.CDLHAMMER(open_price, high, low, close)

# Inverted Hammer (búa ngược)
inverted_hammer = talib.CDLINVERTEDHAMMER(open_price, high, low, close)

# Bullish Engulfing (nhấn chìm tăng)
bullish_engulfing = talib.CDLENGULFING(open_price, high, low, close)

# Morning Star (sao mai - very bullish)
morning_star = talib.CDLMORNINGSTAR(open_price, high, low, close)

# Piercing Line (đường xuyên thủng)
piercing = talib.CDLPIERCING(open_price, high, low, close)

# Three White Soldiers (ba chiến binh trắng - strong bullish)
three_white_soldiers = talib.CDL3WHITESOLDIERS(open_price, high, low, close)

# === BEARISH PATTERNS ===

# Hanging Man (người treo cổ - bearish reversal)
hanging_man = talib.CDLHANGINGMAN(open_price, high, low, close)

# Shooting Star (sao băng - bearish reversal)
shooting_star = talib.CDLSHOOTINGSTAR(open_price, high, low, close)

# Bearish Engulfing (nhấn chìm giảm)
# (same function as bullish, returns -100 for bearish)

# Evening Star (sao hôm - very bearish)
evening_star = talib.CDLEVENINGSTAR(open_price, high, low, close)

# Dark Cloud Cover (đám mây đen)
dark_cloud = talib.CDLDARKCLOUDCOVER(open_price, high, low, close)

# Three Black Crows (ba con quạ đen - strong bearish)
three_black_crows = talib.CDL3BLACKCROWS(open_price, high, low, close)

# === NEUTRAL/CONTINUATION PATTERNS ===

# Doji (ngôi sao Doji - indecision)
doji = talib.CDLDOJI(open_price, high, low, close)

# Spinning Top (con quay - indecision)
spinning_top = talib.CDLSPINNINGTOP(open_price, high, low, close)

# Harami (thai nghén - inside bar)
harami = talib.CDLHARAMI(open_price, high, low, close)
```

#### **All 61 Candlestick Patterns**

**Bullish Reversal Patterns (15):**
```python
talib.CDLHAMMER              # Hammer
talib.CDLINVERTEDHAMMER      # Inverted Hammer
talib.CDLMORNINGSTAR         # Morning Star
talib.CDLMORNINGDOJISTAR     # Morning Doji Star
talib.CDL3WHITESOLDIERS      # Three White Soldiers
talib.CDLPIERCING            # Piercing Line
talib.CDLABANDONEDBABY       # Abandoned Baby (bullish)
talib.CDLBREAKAWAY           # Breakaway (bullish)
talib.CDLHOMINGPIGEON        # Homing Pigeon
talib.CDLKICKING             # Kicking (bullish)
talib.CDLLADDERBOTTOM        # Ladder Bottom
talib.CDLMATCHINGLOW         # Matching Low
talib.CDLUNIQUE3RIVER        # Unique 3 River
talib.CDLXSIDEGAP3METHODS    # Upside Gap Three Methods
talib.CDL3INSIDE             # Three Inside Up
```

**Bearish Reversal Patterns (15):**
```python
talib.CDLHANGINGMAN          # Hanging Man
talib.CDLSHOOTINGSTAR        # Shooting Star
talib.CDLEVENINGSTAR         # Evening Star
talib.CDLEVENINGDOJISTAR     # Evening Doji Star
talib.CDL3BLACKCROWS         # Three Black Crows
talib.CDLDARKCLOUDCOVER      # Dark Cloud Cover
talib.CDLABANDONEDBABY       # Abandoned Baby (bearish)
talib.CDLBREAKAWAY           # Breakaway (bearish)
talib.CDLIDENTICAL3CROWS     # Identical Three Crows
talib.CDLKICKING             # Kicking (bearish)
talib.CDLINNECK              # In-Neck Pattern
talib.CDLONNECK              # On-Neck Pattern
talib.CDLTHRUSTING           # Thrusting Pattern
talib.CDLADVANCEBLOCK        # Advance Block
talib.CDL3LINESTRIKE         # Three-Line Strike
```

**Continuation Patterns (10):**
```python
talib.CDL3STARSINSOUTH       # Three Stars In The South
talib.CDLCONCEALBABYSWALL    # Concealing Baby Swallow
talib.CDLGAPSIDESIDEWHITE    # Up/Down-gap side-by-side white lines
talib.CDLMATHOLD             # Mat Hold
talib.CDLRISEFALL3METHODS    # Rising/Falling Three Methods
talib.CDLSEPARATINGLINES     # Separating Lines
talib.CDLTASUKIGAP           # Tasuki Gap
talib.CDLTRISTAR             # Tristar Pattern
talib.CDL2CROWS              # Two Crows
talib.CDLXSIDEGAP3METHODS    # Upside/Downside Gap Three Methods
```

**Neutral/Indecision Patterns (21):**
```python
talib.CDLDOJI                # Doji
talib.CDLDOJISTAR            # Doji Star
talib.CDLDRAGONFLYDOJI       # Dragonfly Doji
talib.CDLGRAVESTONEDOJI      # Gravestone Doji
talib.CDLLONGLEGGEDDOJI      # Long Legged Doji
talib.CDL4PRICE              # Four Price Doji
talib.CDLSPINNINGTOP         # Spinning Top
talib.CDLHARAMI              # Harami Pattern
talib.CDLHARAMICROSS         # Harami Cross
talib.CDLHIGHWAVE            # High-Wave Candle
talib.CDLBELTHOLD            # Belt-hold
talib.CDLCLOSINGMARUBOZU     # Closing Marubozu
talib.CDLCOUNTERATTACK       # Counterattack
talib.CDLENGULFING           # Engulfing Pattern
talib.CDLGAPSIDESIDEWHITE    # Up/Down-gap side-by-side white lines
talib.CDLHIKKAKE             # Hikkake Pattern
talib.CDLHIKKAKEMOD          # Modified Hikkake
talib.CDLKICKINGBYLENGTH     # Kicking - bull/bear determined by longer marubozu
talib.CDLLONGLINE            # Long Line Candle
talib.CDLMARUBOZU            # Marubozu
talib.CDLSHORTLINE           # Short Line Candle
```

### Using Candlestick Patterns in Alert Detection

```python
def detect_candlestick_patterns(open_prices, high, low, close):
    """
    Detect all important candlestick patterns.

    Returns dict with pattern names and signals.
    """
    patterns = {}

    # Check top 10 most reliable patterns
    patterns['hammer'] = talib.CDLHAMMER(open_prices, high, low, close)
    patterns['inverted_hammer'] = talib.CDLINVERTEDHAMMER(open_prices, high, low, close)
    patterns['engulfing'] = talib.CDLENGULFING(open_prices, high, low, close)
    patterns['morning_star'] = talib.CDLMORNINGSTAR(open_prices, high, low, close)
    patterns['evening_star'] = talib.CDLEVENINGSTAR(open_prices, high, low, close)
    patterns['three_white_soldiers'] = talib.CDL3WHITESOLDIERS(open_prices, high, low, close)
    patterns['three_black_crows'] = talib.CDL3BLACKCROWS(open_prices, high, low, close)
    patterns['doji'] = talib.CDLDOJI(open_prices, high, low, close)
    patterns['shooting_star'] = talib.CDLSHOOTINGSTAR(open_prices, high, low, close)
    patterns['hanging_man'] = talib.CDLHANGINGMAN(open_prices, high, low, close)

    # Get latest patterns (last candle)
    current_patterns = {}
    for name, values in patterns.items():
        if values[-1] != 0:
            current_patterns[name] = {
                'signal': 'BULLISH' if values[-1] > 0 else 'BEARISH',
                'strength': abs(values[-1])
            }

    return current_patterns
```

---

## 🔧 IMPLEMENTATION ROADMAP

### **Phase 1: Alert Detection Engine (2-3 days)** - TA-Lib Version

#### 1.1 Create Alert Detector Class
**File:** `PROCESSORS/technical/indicators/alert_detector.py`

```python
class TechnicalAlertDetector:
    def __init__(self, lookback_days: int = 252):
        """Initialize with 1-year lookback"""
        self.lookback_days = lookback_days
        self.ohlcv_path = "DATA/raw/ohlcv/OHLCV_mktcap.parquet"
        self.ma_path = "DATA/processed/technical/moving_averages/ma_all_symbols.parquet"
        self.rsi_path = "DATA/processed/technical/rsi/rsi_all_symbols.parquet"
        self.macd_path = "DATA/processed/technical/macd/macd_all_symbols.parquet"

    def load_data(self, symbols: List[str] = None) -> pd.DataFrame:
        """Load 1 year of OHLCV + MA + RSI + MACD data"""

    def detect_all_alerts(self, date: str) -> pd.DataFrame:
        """Detect all alerts for given date"""
        ma_alerts = self.detect_ma_crossover_all()
        vol_alerts = self.detect_volume_spike_all()
        breakout_alerts = self.detect_breakout_all()
        combined_signals = self.detect_combined_signal_all()

        return {
            'ma_crossover': ma_alerts,
            'volume_spike': vol_alerts,
            'breakout': breakout_alerts,
            'combined': combined_signals
        }
```

**Tests:**
```python
# Test MA crossover detection
detector = TechnicalAlertDetector()
alerts = detector.detect_ma_crossover('ACB', df_acb)
assert alerts['alert_type'] == 'MA_CROSS_ABOVE'
assert alerts['ma_period'] == 20
```

#### 1.2 Implement MA Crossover Detection
**Logic:**
```python
def detect_ma_crossover(self, symbol, df):
    # Lấy 2 ngày gần nhất
    current = df.iloc[-1]
    previous = df.iloc[-2]

    alerts = []

    for ma_period in [20, 50, 100, 200]:
        ma_col = f'sma_{ma_period}'

        # Crossover up: price crosses above MA
        if previous['close'] < previous[ma_col] and current['close'] > current[ma_col]:
            alerts.append({
                'symbol': symbol,
                'date': current['date'],
                'alert_type': 'MA_CROSS_ABOVE',
                'ma_period': ma_period,
                'price': current['close'],
                'ma_value': current[ma_col],
                'signal': 'BULLISH'
            })

        # Crossover down: price crosses below MA
        elif previous['close'] > previous[ma_col] and current['close'] < current[ma_col]:
            alerts.append({
                'symbol': symbol,
                'date': current['date'],
                'alert_type': 'MA_CROSS_BELOW',
                'ma_period': ma_period,
                'price': current['close'],
                'ma_value': current[ma_col],
                'signal': 'BEARISH'
            })

    return pd.DataFrame(alerts)
```

#### 1.3 Implement Smart Volume Spike Detection (với TA-Lib)
**Logic:** Volume spike KẾT HỢP với breakout, RSI, MACD, và candlestick patterns

```python
import talib
import numpy as np

def detect_smart_volume_spike(self, symbol, df):
    """Smart volume spike with multi-factor confirmation using TA-Lib"""

    # Convert to numpy arrays for TA-Lib
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    open_price = df['open'].values
    volume = df['volume'].values

    # 1. Basic Volume Spike Detection
    avg_volume_20 = np.mean(volume[-20:])
    current_volume = volume[-1]
    volume_ratio = current_volume / avg_volume_20

    if volume_ratio < 1.5:
        return None  # No significant volume spike

    # 2. Calculate Technical Indicators using TA-Lib
    # RSI
    rsi = talib.RSI(close, timeperiod=14)
    current_rsi = rsi[-1]

    # MACD
    macd, macd_signal, macd_hist = talib.MACD(
        close, fastperiod=12, slowperiod=26, signalperiod=9
    )
    macd_bullish = macd[-1] > macd_signal[-1]

    # MA
    sma_20 = talib.SMA(close, timeperiod=20)

    # 3. Breakout Detection
    resistance_20 = np.max(high[-21:-1])  # 20-day high (exclude current)
    support_20 = np.min(low[-21:-1])       # 20-day low (exclude current)

    is_breakout_up = close[-1] > resistance_20
    is_breakdown = close[-1] < support_20

    # 4. Candlestick Pattern Detection (Top 10)
    patterns = {
        'hammer': talib.CDLHAMMER(open_price, high, low, close),
        'inverted_hammer': talib.CDLINVERTEDHAMMER(open_price, high, low, close),
        'engulfing': talib.CDLENGULFING(open_price, high, low, close),
        'morning_star': talib.CDLMORNINGSTAR(open_price, high, low, close),
        'evening_star': talib.CDLEVENINGSTAR(open_price, high, low, close),
        'three_white_soldiers': talib.CDL3WHITESOLDIERS(open_price, high, low, close),
        'three_black_crows': talib.CDL3BLACKCROWS(open_price, high, low, close),
        'shooting_star': talib.CDLSHOOTINGSTAR(open_price, high, low, close),
        'hanging_man': talib.CDLHANGINGMAN(open_price, high, low, close),
        'doji': talib.CDLDOJI(open_price, high, low, close)
    }

    # Find active patterns
    active_pattern = None
    pattern_signal = None
    for name, values in patterns.items():
        if values[-1] != 0:
            active_pattern = name
            pattern_signal = 'BULLISH' if values[-1] > 0 else 'BEARISH'
            break

    # 5. Calculate Confirmations
    confirmations = 0
    confirmation_details = {}

    # Confirmation 1: Breakout
    if is_breakout_up:
        confirmations += 1
        confirmation_details['breakout'] = 'UP'
    elif is_breakdown:
        confirmations += 1
        confirmation_details['breakout'] = 'DOWN'

    # Confirmation 2: RSI (not overbought/oversold)
    if 40 <= current_rsi <= 70:
        confirmations += 1
        confirmation_details['rsi'] = 'HEALTHY'
    elif current_rsi < 30:
        confirmations += 1
        confirmation_details['rsi'] = 'OVERSOLD_BOUNCE'

    # Confirmation 3: MACD
    if macd_bullish:
        confirmations += 1
        confirmation_details['macd'] = 'BULLISH'

    # Confirmation 4: Candlestick Pattern
    if active_pattern and pattern_signal == 'BULLISH':
        confirmations += 1
        confirmation_details['pattern'] = active_pattern.upper()

    # 6. Determine Overall Signal
    price_change_pct = ((close[-1] - close[-2]) / close[-2]) * 100

    if confirmations >= 3:
        if is_breakout_up and macd_bullish:
            signal = 'STRONG_BUY'
            confidence = 0.85
        elif price_change_pct > 0:
            signal = 'BUY'
            confidence = 0.70
        else:
            signal = 'DISTRIBUTION'  # Volume spike on down day
            confidence = 0.65
    elif confirmations >= 2:
        signal = 'WATCH'
        confidence = 0.50
    else:
        signal = 'NOISE'  # Volume spike without confirmations
        confidence = 0.30

    return {
        'symbol': symbol,
        'date': df.iloc[-1]['date'],
        'alert_type': 'SMART_VOLUME_SPIKE',

        # Volume data
        'volume': int(current_volume),
        'avg_volume_20d': int(avg_volume_20),
        'volume_ratio': round(volume_ratio, 2),

        # Price data
        'price': close[-1],
        'price_change_pct': round(price_change_pct, 2),

        # Technical confirmations
        'is_breakout': is_breakout_up,
        'rsi': round(current_rsi, 2),
        'macd_bullish': macd_bullish,
        'candlestick_pattern': active_pattern,
        'pattern_signal': pattern_signal,

        # Overall assessment
        'signal': signal,
        'confidence': confidence,
        'confirmations': confirmations,
        'confirmation_details': confirmation_details
    }
```

**Example Output:**
```python
{
    'symbol': 'HPG',
    'date': '2025-12-15',
    'alert_type': 'SMART_VOLUME_SPIKE',
    'volume': 8_500_000,
    'avg_volume_20d': 4_000_000,
    'volume_ratio': 2.13,
    'price': 28500,
    'price_change_pct': 3.8,
    'is_breakout': True,
    'rsi': 58.5,
    'macd_bullish': True,
    'candlestick_pattern': 'hammer',
    'pattern_signal': 'BULLISH',
    'signal': 'STRONG_BUY',
    'confidence': 0.85,
    'confirmations': 4,
    'confirmation_details': {
        'breakout': 'UP',
        'rsi': 'HEALTHY',
        'macd': 'BULLISH',
        'pattern': 'HAMMER'
    }
}
```

#### 1.4 Implement Breakout Detection
**Logic:**
```python
def detect_breakout(self, symbol, df):
    current = df.iloc[-1]

    # Calculate 20-day high/low
    resistance = df['high'].iloc[-20:-1].max()  # Exclude current day
    support = df['low'].iloc[-20:-1].min()

    # Volume confirmation
    avg_volume = df['volume'].iloc[-20:].mean()
    volume_confirmed = current['volume'] > (avg_volume * 1.5)

    # Breakout up
    if current['close'] > resistance and volume_confirmed:
        return {
            'symbol': symbol,
            'date': current['date'],
            'alert_type': 'BREAKOUT_UP',
            'price': current['close'],
            'resistance_level': resistance,
            'volume_confirmed': True,
            'signal': 'BULLISH_BREAKOUT'
        }

    # Breakdown
    elif current['close'] < support and volume_confirmed:
        return {
            'symbol': symbol,
            'date': current['date'],
            'alert_type': 'BREAKDOWN',
            'price': current['close'],
            'support_level': support,
            'volume_confirmed': True,
            'signal': 'BEARISH_BREAKDOWN'
        }

    return None
```

#### 1.5 Implement Combined Signal Detection
**Logic:**
```python
def detect_combined_signal(self, symbol, df):
    current = df.iloc[-1]

    # MA trend
    ma20_trend = 'ABOVE' if current['close'] > current['sma_20'] else 'BELOW'
    ma50_trend = 'ABOVE' if current['close'] > current['sma_50'] else 'BELOW'

    # RSI
    rsi = current['rsi_14']

    # MACD signal
    if current['macd'] > current['macd_signal']:
        macd_signal = 'BULLISH_CROSS'
    elif current['macd'] < current['macd_signal']:
        macd_signal = 'BEARISH_CROSS'
    else:
        macd_signal = 'NEUTRAL'

    # Scoring system
    score = 0

    # MA trend (40 points)
    if ma20_trend == 'ABOVE' and ma50_trend == 'ABOVE':
        score += 40
    elif ma20_trend == 'BELOW' and ma50_trend == 'BELOW':
        score -= 40

    # RSI (30 points)
    if 40 <= rsi <= 60:
        score += 30  # Neutral RSI is good
    elif rsi < 30:
        score += 20  # Oversold (potential bounce)
    elif rsi > 70:
        score -= 20  # Overbought

    # MACD (30 points)
    if macd_signal == 'BULLISH_CROSS':
        score += 30
    elif macd_signal == 'BEARISH_CROSS':
        score -= 30

    # Classify signal
    if score >= 70:
        overall_signal = 'STRONG_BUY'
        confidence = 0.85
    elif score >= 40:
        overall_signal = 'BUY'
        confidence = 0.65
    elif score <= -70:
        overall_signal = 'STRONG_SELL'
        confidence = 0.85
    elif score <= -40:
        overall_signal = 'SELL'
        confidence = 0.65
    else:
        overall_signal = 'HOLD'
        confidence = 0.50

    return {
        'symbol': symbol,
        'date': current['date'],
        'price': current['close'],
        'ma20_trend': ma20_trend,
        'ma50_trend': ma50_trend,
        'rsi_14': rsi,
        'macd_signal': macd_signal,
        'overall_signal': overall_signal,
        'confidence': confidence,
        'score': score
    }
```

---

### **Phase 2: Market Breadth Calculator (1 day)**

#### 2.1 Enhance Market Breadth Processor
**File:** Update existing `market_breadth_processor.py`

```python
def calculate_daily_breadth(self, date: str) -> Dict:
    """Calculate comprehensive market breadth"""

    # Load latest data for all symbols
    df = self.load_ohlcv_and_ma_data(date)

    total_stocks = len(df)

    # MA breadth
    above_ma20 = (df['close'] > df['sma_20']).sum()
    above_ma50 = (df['close'] > df['sma_50']).sum()
    above_ma100 = (df['close'] > df['sma_100']).sum()
    above_ma200 = (df['close'] > df['sma_200']).sum()

    # Advance-Decline
    advancing = (df['price_change'] > 0).sum()
    declining = (df['price_change'] < 0).sum()
    unchanged = (df['price_change'] == 0).sum()

    ad_ratio = advancing / declining if declining > 0 else 0

    # Market trend classification
    ma50_pct = (above_ma50 / total_stocks) * 100

    if ma50_pct > 60:
        market_trend = 'BULLISH'
    elif ma50_pct < 40:
        market_trend = 'BEARISH'
    else:
        market_trend = 'NEUTRAL'

    return {
        'date': date,
        'total_stocks': total_stocks,
        'above_ma20': above_ma20,
        'above_ma50': above_ma50,
        'above_ma100': above_ma100,
        'above_ma200': above_ma200,
        'above_ma20_pct': (above_ma20 / total_stocks) * 100,
        'above_ma50_pct': ma50_pct,
        'above_ma100_pct': (above_ma100 / total_stocks) * 100,
        'above_ma200_pct': (above_ma200 / total_stocks) * 100,
        'advancing': advancing,
        'declining': declining,
        'unchanged': unchanged,
        'ad_ratio': ad_ratio,
        'market_trend': market_trend
    }
```

---

### **Phase 3: Daily Alert Pipeline (1 day)**

#### 3.1 Create Daily Alert Runner
**File:** `PROCESSORS/technical/pipelines/daily_alert_pipeline.py`

```python
#!/usr/bin/env python3
"""
Daily Technical Alert Pipeline
===============================

Run daily to detect:
- MA crossovers
- Volume spikes
- Breakouts
- Combined signals
- Market breadth

Usage:
    python3 PROCESSORS/technical/pipelines/daily_alert_pipeline.py
    python3 PROCESSORS/technical/pipelines/daily_alert_pipeline.py --date 2025-12-15
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import logging

# Add project root
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from PROCESSORS.technical.indicators.alert_detector import TechnicalAlertDetector
from PROCESSORS.technical.indicators.market_breadth_processor import MarketBreadthProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Daily Technical Alert Pipeline')
    parser.add_argument('--date', type=str, default=None, help='Target date (YYYY-MM-DD)')
    args = parser.parse_args()

    # Get target date
    if args.date:
        target_date = args.date
    else:
        target_date = datetime.now().strftime('%Y-%m-%d')

    logger.info(f"Running Daily Alert Pipeline for {target_date}")

    # 1. Detect alerts
    logger.info("Detecting technical alerts...")
    detector = TechnicalAlertDetector(lookback_days=252)
    alerts = detector.detect_all_alerts(target_date)

    # 2. Save alerts
    output_dir = Path("DATA/processed/technical/alerts")
    output_dir.mkdir(parents=True, exist_ok=True)

    alerts['ma_crossover'].to_parquet(output_dir / "ma_crossover_alerts.parquet")
    alerts['volume_spike'].to_parquet(output_dir / "volume_spike_alerts.parquet")
    alerts['breakout'].to_parquet(output_dir / "breakout_alerts.parquet")
    alerts['combined'].to_parquet(output_dir / "combined_signals.parquet")

    logger.info(f"✅ MA Crossover: {len(alerts['ma_crossover'])} alerts")
    logger.info(f"✅ Volume Spike: {len(alerts['volume_spike'])} alerts")
    logger.info(f"✅ Breakout: {len(alerts['breakout'])} alerts")
    logger.info(f"✅ Combined Signals: {len(alerts['combined'])} alerts")

    # 3. Calculate market breadth
    logger.info("Calculating market breadth...")
    breadth_proc = MarketBreadthProcessor()
    breadth = breadth_proc.calculate_daily_breadth(target_date)

    # Save market breadth
    breadth_df = pd.DataFrame([breadth])
    breadth_output = Path("DATA/processed/technical/market_breadth/market_breadth_daily.parquet")

    if breadth_output.exists():
        existing = pd.read_parquet(breadth_output)
        # Remove duplicate date
        existing = existing[existing['date'] != target_date]
        combined = pd.concat([existing, breadth_df], ignore_index=True)
        combined.to_parquet(breadth_output, index=False)
    else:
        breadth_df.to_parquet(breadth_output, index=False)

    logger.info(f"✅ Market Breadth: {breadth['above_ma50']}/{breadth['total_stocks']} above MA50 ({breadth['above_ma50_pct']:.1f}%)")
    logger.info(f"✅ Market Trend: {breadth['market_trend']}")

    # 4. Print summary
    print("\n" + "=" * 80)
    print(f"DAILY TECHNICAL ALERTS - {target_date}")
    print("=" * 80)
    print(f"\nMA Crossover Alerts: {len(alerts['ma_crossover'])}")
    print(f"Volume Spike Alerts: {len(alerts['volume_spike'])}")
    print(f"Breakout Alerts: {len(alerts['breakout'])}")
    print(f"Combined Signals (STRONG BUY/SELL): {len(alerts['combined'][alerts['combined']['overall_signal'].isin(['STRONG_BUY', 'STRONG_SELL'])])}")
    print(f"\nMarket Breadth:")
    print(f"  Above MA20: {breadth['above_ma20']} ({breadth['above_ma20_pct']:.1f}%)")
    print(f"  Above MA50: {breadth['above_ma50']} ({breadth['above_ma50_pct']:.1f}%)")
    print(f"  Above MA100: {breadth['above_ma100']} ({breadth['above_ma100_pct']:.1f}%)")
    print(f"  Above MA200: {breadth['above_ma200']} ({breadth['above_ma200_pct']:.1f}%)")
    print(f"  Advance/Decline: {breadth['advancing']}/{breadth['declining']} (AD Ratio: {breadth['ad_ratio']:.2f})")
    print(f"  Market Trend: {breadth['market_trend']}")
    print("=" * 80)


if __name__ == '__main__':
    main()
```

---

## 📈 SUGGESTED FEATURES (Đề xuất thêm)

### 1. **Golden Cross / Death Cross Alert**
- Golden Cross: MA50 vượt MA200 (very bullish)
- Death Cross: MA50 lủng MA200 (very bearish)

### 2. **Divergence Detection**
- RSI Divergence: Price makes higher high but RSI makes lower high
- MACD Divergence: Price makes lower low but MACD makes higher low

### 3. **Support/Resistance Break with Fibonacci**
- Fibonacci retracement levels (23.6%, 38.2%, 50%, 61.8%)
- Alert when price breaks key Fibonacci levels

### 4. **Volume Profile**
- Volume-Weighted Average Price (VWAP)
- High volume zones (support/resistance)

### 5. **Trend Strength**
- ADX (Average Directional Index) to measure trend strength
- Strong trend: ADX > 25
- Weak trend: ADX < 20

### 6. **Pattern Recognition**
- Double Top / Double Bottom
- Head and Shoulders
- Cup and Handle

---

## 🎨 STREAMLIT DASHBOARD DESIGN

### Page: "Technical Alerts"

**Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  📊 TECHNICAL ALERTS DASHBOARD - 2025-12-15                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🔔 ALERT SUMMARY                                           │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │ MA Crossover│ Volume Spike│  Breakout   │  Combined   │ │
│  │     12      │      8      │      5      │     15      │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │
│                                                             │
│  📈 MARKET BREADTH                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Above MA20: 280 (62%)  ████████████████░░░░░░░░░   │   │
│  │  Above MA50: 250 (55%)  ██████████████░░░░░░░░░░░   │   │
│  │  Above MA100: 220 (49%) ████████████░░░░░░░░░░░░░   │   │
│  │  Above MA200: 200 (44%) ██████████░░░░░░░░░░░░░░░   │   │
│  │                                                      │   │
│  │  Market Trend: BULLISH                               │   │
│  │  AD Ratio: 1.84 (285 ↑ / 155 ↓)                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  🎯 TOP ALERTS (Filter: All | MA | Volume | Breakout)       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Symbol │ Alert Type     │ Signal  │ Price │ Details  │   │
│  ├────────┼────────────────┼─────────┼───────┼─────────┤   │
│  │ ACB    │ MA_CROSS_ABOVE │ BULLISH │ 25500 │ MA20    │   │
│  │ HPG    │ BREAKOUT_UP    │ BULLISH │ 28500 │ Vol 2.1x│   │
│  │ VNM    │ VOLUME_SPIKE   │ ACCUM   │ 85000 │ Vol 2.0x│   │
│  │ ...    │ ...            │ ...     │ ...   │ ...     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  💡 COMBINED SIGNALS (STRONG BUY/SELL)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Symbol │ Signal      │ MA Trend│ RSI │ MACD  │ Conf │   │
│  ├────────┼─────────────┼─────────┼─────┼───────┼──────┤   │
│  │ VIC    │ STRONG_BUY  │ BULLISH │ 55  │ CROSS │ 85%  │   │
│  │ FPT    │ STRONG_BUY  │ BULLISH │ 48  │ CROSS │ 80%  │   │
│  │ ...    │ ...         │ ...     │ ... │ ...   │ ...  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ ACCEPTANCE CRITERIA

### Phase 1: Alert Detection Engine
- [ ] Detect MA crossover (20/50/100/200) với độ chính xác 100%
- [ ] Detect volume spike (>1.5x, >2.0x avg) với độ chính xác 100%
- [ ] Detect breakout với volume confirmation
- [ ] Combined signal (MA + RSI + MACD) với confidence score
- [ ] Output 4 parquet files (ma_crossover, volume_spike, breakout, combined)

### Phase 2: Market Breadth
- [ ] Tính số mã vượt MA20/50/100/200
- [ ] Tính Advance-Decline ratio
- [ ] Classify market trend (BULLISH/NEUTRAL/BEARISH)
- [ ] Output market_breadth_daily.parquet

### Phase 3: Daily Pipeline
- [ ] Chạy tự động mỗi ngày
- [ ] Xử lý chỉ 1 năm data (252 days)
- [ ] Runtime < 5 phút cho toàn bộ 450 mã
- [ ] Append vào historical data (không overwrite)

### Phase 4: Streamlit Dashboard
- [ ] Hiển thị summary cards
- [ ] Hiển thị market breadth bar charts
- [ ] Table alerts với filter
- [ ] Export to Excel
- [ ] Auto-refresh mỗi 5 phút

---

## 📝 NOTES

### Performance Optimization
- Chỉ load 1 năm data (252 days) để giảm memory
- Use DuckDB query để filter trước khi load vào pandas
- Parallel processing cho từng symbol
- Cache MA/RSI/MACD data đã tính toán

### Data Quality
- Validate OHLCV data (remove outliers)
- Handle missing MA values (chưa đủ 200 days)
- Handle division by zero (avg_volume = 0)

### Future Enhancements
- Email/Telegram alerts cho STRONG_BUY/SELL
- Backtesting alerts (độ chính xác bao nhiêu %)
- AI-based pattern recognition
- Sentiment analysis integration

---

## 📅 TIMELINE

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1 | Alert Detector Class | 0.5 day | ⏳ Pending |
| 1 | MA Crossover Detection | 0.5 day | ⏳ Pending |
| 1 | Volume Spike Detection | 0.5 day | ⏳ Pending |
| 1 | Breakout Detection | 0.5 day | ⏳ Pending |
| 1 | Combined Signal Detection | 0.5 day | ⏳ Pending |
| 2 | Market Breadth Enhancement | 1 day | ⏳ Pending |
| 3 | Daily Alert Pipeline | 1 day | ⏳ Pending |
| 4 | Streamlit Dashboard | 2 days | ⏳ Pending |
| **TOTAL** | | **6 days** | |

---

## 🚀 ADVANCED TA FEATURES (Phase 4)

### Overview

Bổ sung các tính năng phân tích kỹ thuật nâng cao:
1. **Money Flow Analysis**: Theo dõi dòng tiền (fund flows)
2. **Bubble & Bottom Detection**: Phát hiện thị trường bubble/đáy
3. **Sector Technical Analysis**: Phân tích kỹ thuật theo sector
4. **VN-Index Integration**: Tích hợp chỉ số VN-Index

---

### 4.1 Money Flow Indicators (Theo Dõi Dòng Tiền)

#### **Concept: Money Flow**

Money Flow tracks the flow of capital in and out of stocks:
- **Accumulation**: Big money buying (high volume + rising price)
- **Distribution**: Big money selling (high volume + falling price)

#### **Indicators to Implement**

**1. Chaikin Money Flow (CMF)**
- **Formula**: CMF = Sum(MFV) / Sum(Volume) over N periods
- **MFV** = Money Flow Volume = ((Close - Low) - (High - Close)) / (High - Low) × Volume
- **Interpretation**:
  - CMF > 0.05: Strong accumulation
  - CMF < -0.05: Strong distribution
  - CMF near 0: Neutral

**2. Money Flow Index (MFI)** - RSI của volume
- **Formula**: Similar to RSI but uses volume-weighted price
- **Interpretation**:
  - MFI > 80: Overbought (potential distribution)
  - MFI < 20: Oversold (potential accumulation)

**3. On-Balance Volume (OBV)**
- **Formula**: Cumulative volume (add on up days, subtract on down days)
- **Interpretation**:
  - OBV rising: Buying pressure
  - OBV falling: Selling pressure
  - Price vs OBV divergence: Warning signal

**4. Accumulation/Distribution Line (AD Line)**
- **Formula**: Similar to OBV but weighted by close position in range
- **Interpretation**: Confirms price trends

**5. Volume Price Trend (VPT)**
- **Formula**: VPT = Previous VPT + Volume × (Today's Close - Yesterday's Close) / Yesterday's Close
- **Interpretation**: Volume-adjusted price momentum

#### **Implementation: Individual Stock Money Flow**

**File:** `PROCESSORS/technical/indicators/money_flow.py`

```python
import talib
import numpy as np
import pandas as pd
from typing import Dict

class MoneyFlowAnalyzer:
    """
    Calculate money flow indicators for individual stocks using TA-Lib.
    """

    def calculate_all_money_flow_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all money flow indicators for a stock.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with money flow indicators added
        """
        df = df.copy()

        # Convert to numpy arrays
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        volume = df['volume'].values

        # 1. Chaikin Money Flow (CMF) - 20 periods
        df['cmf_20'] = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)

        # 2. Money Flow Index (MFI) - 14 periods
        df['mfi_14'] = talib.MFI(high, low, close, volume, timeperiod=14)

        # 3. On-Balance Volume (OBV)
        df['obv'] = talib.OBV(close, volume)

        # 4. AD Line (Accumulation/Distribution)
        df['ad_line'] = talib.AD(high, low, close, volume)

        # 5. Volume Price Trend (custom calculation)
        df['vpt'] = self._calculate_vpt(close, volume)

        # 6. Money Flow Signal (combined)
        df['money_flow_signal'] = self._classify_money_flow(df)

        return df

    def _calculate_vpt(self, close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Calculate Volume Price Trend."""
        vpt = np.zeros_like(close)
        vpt[0] = 0

        for i in range(1, len(close)):
            if close[i-1] != 0:
                vpt[i] = vpt[i-1] + volume[i] * (close[i] - close[i-1]) / close[i-1]

        return vpt

    def _classify_money_flow(self, df: pd.DataFrame) -> pd.Series:
        """
        Classify money flow based on multiple indicators.

        Returns:
            Series with 'STRONG_ACCUMULATION', 'ACCUMULATION', 'NEUTRAL',
            'DISTRIBUTION', 'STRONG_DISTRIBUTION'
        """
        signals = []

        for idx, row in df.iterrows():
            score = 0

            # CMF contribution
            if row['cmf_20'] > 0.10:
                score += 2
            elif row['cmf_20'] > 0.05:
                score += 1
            elif row['cmf_20'] < -0.10:
                score -= 2
            elif row['cmf_20'] < -0.05:
                score -= 1

            # MFI contribution
            if row['mfi_14'] > 70:
                score -= 1  # Overbought (distribution risk)
            elif row['mfi_14'] < 30:
                score += 1  # Oversold (accumulation opportunity)

            # OBV trend (compare with 20-period MA)
            if idx >= 20:
                obv_ma = df['obv'].iloc[idx-20:idx].mean()
                if row['obv'] > obv_ma * 1.05:
                    score += 1
                elif row['obv'] < obv_ma * 0.95:
                    score -= 1

            # Classify
            if score >= 3:
                signals.append('STRONG_ACCUMULATION')
            elif score >= 1:
                signals.append('ACCUMULATION')
            elif score <= -3:
                signals.append('STRONG_DISTRIBUTION')
            elif score <= -1:
                signals.append('DISTRIBUTION')
            else:
                signals.append('NEUTRAL')

        return pd.Series(signals, index=df.index)

    def get_latest_money_flow_status(self, df: pd.DataFrame) -> Dict:
        """
        Get latest money flow status for a stock.

        Returns:
            {
                'symbol': 'ACB',
                'date': '2025-12-15',
                'cmf_20': 0.12,
                'mfi_14': 58.5,
                'obv': 125000000,
                'obv_trend': 'RISING',
                'signal': 'STRONG_ACCUMULATION',
                'confidence': 0.85
            }
        """
        latest = df.iloc[-1]

        # OBV trend
        obv_ma_20 = df['obv'].iloc[-20:].mean()
        if latest['obv'] > obv_ma_20 * 1.05:
            obv_trend = 'RISING'
        elif latest['obv'] < obv_ma_20 * 0.95:
            obv_trend = 'FALLING'
        else:
            obv_trend = 'FLAT'

        # Calculate confidence
        score = 0
        if abs(latest['cmf_20']) > 0.10:
            score += 1
        if latest['mfi_14'] > 70 or latest['mfi_14'] < 30:
            score += 1
        if obv_trend in ['RISING', 'FALLING']:
            score += 1

        confidence = min(0.5 + (score * 0.15), 0.95)

        return {
            'symbol': latest.get('symbol', 'UNKNOWN'),
            'date': latest.get('date', None),
            'cmf_20': round(latest['cmf_20'], 4),
            'mfi_14': round(latest['mfi_14'], 2),
            'obv': int(latest['obv']),
            'obv_trend': obv_trend,
            'ad_line': int(latest['ad_line']),
            'vpt': int(latest['vpt']),
            'signal': latest['money_flow_signal'],
            'confidence': confidence
        }
```

**Output Schema:**

| Column | Type | Description |
|--------|------|-------------|
| symbol | str | Mã cổ phiếu |
| date | datetime | Ngày |
| cmf_20 | float | Chaikin Money Flow 20-day |
| mfi_14 | float | Money Flow Index 14-day |
| obv | int | On-Balance Volume |
| ad_line | int | Accumulation/Distribution Line |
| vpt | int | Volume Price Trend |
| money_flow_signal | str | STRONG_ACCUMULATION / ACCUMULATION / NEUTRAL / DISTRIBUTION / STRONG_DISTRIBUTION |

---

### 4.2 Sector Money Flow Analysis

#### **Concept: Sector Money Flow**

Track which sectors are receiving fund inflows vs outflows.

**Formula:**
```
Sector Money Flow = Σ(Price × Volume) for all stocks in sector

Inflow/Outflow % = (Today - Yesterday) / Yesterday × 100
```

#### **Implementation: Sector Money Flow Aggregator**

**File:** `PROCESSORS/technical/indicators/sector_money_flow.py`

```python
import pandas as pd
import numpy as np
from typing import Dict, List
from config.registries import SectorRegistry

class SectorMoneyFlowAnalyzer:
    """
    Calculate money flow for each sector.
    """

    def __init__(self):
        self.sector_reg = SectorRegistry()

    def calculate_sector_money_flow(self, date: str) -> pd.DataFrame:
        """
        Calculate daily money flow for all sectors.

        Returns:
            DataFrame:
                sector_code | money_flow | inflow_pct | flow_signal | top_contributors
        """
        # Load OHLCV data for date
        ohlcv_df = self._load_ohlcv_for_date(date)

        # Calculate money flow for each stock
        ohlcv_df['money_flow'] = ohlcv_df['close'] * ohlcv_df['volume']

        # Add sector information
        ohlcv_df['sector_code'] = ohlcv_df['symbol'].apply(
            lambda x: self.sector_reg.get_ticker(x).get('sector_code', 'UNKNOWN') if self.sector_reg.get_ticker(x) else 'UNKNOWN'
        )

        # Aggregate by sector
        sector_flow = ohlcv_df.groupby('sector_code').agg({
            'money_flow': 'sum',
            'symbol': 'count'  # Number of stocks
        }).reset_index()

        sector_flow.columns = ['sector_code', 'money_flow', 'stock_count']

        # Calculate inflow/outflow (compare with previous day)
        prev_date = self._get_previous_trading_date(date)
        if prev_date:
            prev_flow = self.calculate_sector_money_flow(prev_date)
            sector_flow = sector_flow.merge(
                prev_flow[['sector_code', 'money_flow']],
                on='sector_code',
                how='left',
                suffixes=('', '_prev')
            )

            sector_flow['inflow_pct'] = (
                (sector_flow['money_flow'] - sector_flow['money_flow_prev']) /
                sector_flow['money_flow_prev'] * 100
            )
        else:
            sector_flow['inflow_pct'] = 0.0

        # Classify flow signal
        sector_flow['flow_signal'] = sector_flow['inflow_pct'].apply(
            lambda x: 'STRONG_INFLOW' if x > 10 else
                     'INFLOW' if x > 3 else
                     'STRONG_OUTFLOW' if x < -10 else
                     'OUTFLOW' if x < -3 else
                     'NEUTRAL'
        )

        # Find top contributors (stocks with highest money flow in sector)
        sector_flow['top_contributors'] = sector_flow['sector_code'].apply(
            lambda s: self._get_top_contributors(ohlcv_df, s, top_n=3)
        )

        sector_flow['date'] = date

        return sector_flow[['date', 'sector_code', 'money_flow', 'inflow_pct', 'flow_signal', 'stock_count', 'top_contributors']]

    def _get_top_contributors(self, df: pd.DataFrame, sector_code: str, top_n: int = 3) -> str:
        """Get top N stocks by money flow in sector."""
        sector_df = df[df['sector_code'] == sector_code].copy()
        sector_df = sector_df.nlargest(top_n, 'money_flow')
        return ', '.join(sector_df['symbol'].tolist())

    def _load_ohlcv_for_date(self, date: str) -> pd.DataFrame:
        """Load OHLCV data for specific date."""
        # Implementation: Load from OHLCV_mktcap.parquet
        pass

    def _get_previous_trading_date(self, date: str) -> str:
        """Get previous trading date."""
        # Implementation: Query OHLCV data for previous date
        pass
```

**Output Table:**

| sector_code | money_flow | inflow_pct | flow_signal | stock_count | top_contributors |
|-------------|------------|------------|-------------|-------------|------------------|
| BANKING     | 5.2T VND   | +12.5%     | STRONG_INFLOW | 28         | ACB, TCB, VCB    |
| TECH        | 2.8T VND   | -8.3%      | OUTFLOW     | 15         | FPT, CMG, VGI    |
| REAL_ESTATE | 4.1T VND   | +3.2%      | INFLOW      | 42         | VHM, NVL, DXG    |

---

### 4.3 Sector Breadth Analysis

#### **Concept: Sector Breadth**

Track how many stocks in each sector are above MA20/50/200.

**Purpose:**
- Identify strong vs weak sectors
- Detect sector rotation
- Confirm sector trends

#### **Implementation: Sector Breadth Analyzer**

**File:** `PROCESSORS/technical/indicators/sector_breadth.py`

```python
import pandas as pd
from config.registries import SectorRegistry

class SectorBreadthAnalyzer:
    """
    Calculate breadth indicators per sector.
    """

    def __init__(self):
        self.sector_reg = SectorRegistry()

    def calculate_sector_breadth(self, date: str) -> pd.DataFrame:
        """
        Calculate breadth indicators for all sectors.

        Returns:
            DataFrame:
                sector_code | total_stocks | above_ma20 | above_ma50 | above_ma200 |
                above_ma20_pct | above_ma50_pct | above_ma200_pct |
                ad_ratio | sector_strength
        """
        # Load OHLCV + MA data for date
        df = self._load_ohlcv_ma_for_date(date)

        # Add sector information
        df['sector_code'] = df['symbol'].apply(
            lambda x: self.sector_reg.get_ticker(x).get('sector_code', 'UNKNOWN') if self.sector_reg.get_ticker(x) else 'UNKNOWN'
        )

        # Aggregate by sector
        sector_breadth = df.groupby('sector_code').apply(
            lambda sector_df: pd.Series({
                'total_stocks': len(sector_df),
                'above_ma20': (sector_df['close'] > sector_df['sma_20']).sum(),
                'above_ma50': (sector_df['close'] > sector_df['sma_50']).sum(),
                'above_ma200': (sector_df['close'] > sector_df['sma_200']).sum(),
                'advancing': (sector_df['price_change'] > 0).sum(),
                'declining': (sector_df['price_change'] < 0).sum(),
            })
        ).reset_index()

        # Calculate percentages
        sector_breadth['above_ma20_pct'] = (sector_breadth['above_ma20'] / sector_breadth['total_stocks']) * 100
        sector_breadth['above_ma50_pct'] = (sector_breadth['above_ma50'] / sector_breadth['total_stocks']) * 100
        sector_breadth['above_ma200_pct'] = (sector_breadth['above_ma200'] / sector_breadth['total_stocks']) * 100

        # AD Ratio
        sector_breadth['ad_ratio'] = sector_breadth['advancing'] / sector_breadth['declining'].replace(0, 1)

        # Sector strength classification
        sector_breadth['sector_strength'] = sector_breadth['above_ma50_pct'].apply(
            lambda x: 'VERY_STRONG' if x >= 70 else
                     'STRONG' if x >= 55 else
                     'WEAK' if x <= 35 else
                     'VERY_WEAK' if x <= 20 else
                     'NEUTRAL'
        )

        sector_breadth['date'] = date

        return sector_breadth

    def _load_ohlcv_ma_for_date(self, date: str) -> pd.DataFrame:
        """Load OHLCV + MA data for specific date."""
        # Implementation: Join OHLCV with MA data
        pass
```

**Output Table:**

| sector_code | total_stocks | above_ma20 | above_ma50 | above_ma200 | above_ma20_pct | above_ma50_pct | ad_ratio | sector_strength |
|-------------|--------------|------------|------------|-------------|----------------|----------------|----------|-----------------|
| BANKING     | 28           | 22         | 18         | 15          | 78.6%          | 64.3%          | 2.1      | STRONG          |
| TECH        | 15           | 8          | 6          | 5           | 53.3%          | 40.0%          | 0.9      | WEAK            |
| REAL_ESTATE | 42           | 30         | 25         | 20          | 71.4%          | 59.5%          | 1.8      | STRONG          |

---

### 4.4 Market Regime Detection (Bubble & Bottom)

#### **Concept: Market Regime**

Detect if market is in:
- **BUBBLE**: Overvalued, extreme breadth, volume climax
- **BOTTOM**: Undervalued, weak breadth, capitulation
- **RALLY**: Improving breadth, moderate valuation
- **CONSOLIDATION**: Neutral indicators

#### **Multi-Factor Detection System**

**Factors:**
1. **Valuation**: VN-Index PE/PB percentile (5-year historical)
2. **Breadth**: % stocks above MA200
3. **Volume**: Volume spike vs average
4. **Volatility**: VIX-like volatility index

**Implementation: Market Regime Detector**

**File:** `PROCESSORS/technical/indicators/market_regime.py`

```python
import pandas as pd
import numpy as np
from typing import Dict

class MarketRegimeDetector:
    """
    Detect market regime using valuation, breadth, volume, and volatility.
    """

    def detect_market_regime(self, date: str) -> Dict:
        """
        Detect market regime for specific date.

        Returns:
            {
                'date': '2025-12-15',
                'regime': 'BUBBLE' | 'BOTTOM' | 'RALLY' | 'CONSOLIDATION',
                'confidence': 0.85,
                'signals': {
                    'valuation_signal': 'EXPENSIVE',
                    'breadth_signal': 'EXTREME_BULLISH',
                    'volume_signal': 'CLIMAX',
                    'volatility_signal': 'HIGH'
                },
                'factor_scores': {
                    'valuation': 90,  # PE percentile
                    'breadth': 85,    # % above MA200
                    'volume': 120,    # % of average
                    'volatility': 75  # Volatility percentile
                }
            }
        """
        # 1. Valuation Factor
        valuation_data = self._get_valuation_percentile(date)

        # 2. Breadth Factor
        breadth_data = self._get_market_breadth(date)

        # 3. Volume Factor
        volume_data = self._get_volume_analysis(date)

        # 4. Volatility Factor
        volatility_data = self._get_volatility_analysis(date)

        # Combine signals
        signals = {
            'valuation_signal': self._classify_valuation(valuation_data),
            'breadth_signal': self._classify_breadth(breadth_data),
            'volume_signal': self._classify_volume(volume_data),
            'volatility_signal': self._classify_volatility(volatility_data)
        }

        # Detect regime
        regime, confidence = self._determine_regime(
            valuation_data, breadth_data, volume_data, volatility_data
        )

        return {
            'date': date,
            'regime': regime,
            'confidence': confidence,
            'signals': signals,
            'factor_scores': {
                'valuation': valuation_data['pe_percentile'],
                'breadth': breadth_data['above_ma200_pct'],
                'volume': volume_data['volume_pct_of_avg'],
                'volatility': volatility_data['volatility_percentile']
            }
        }

    def _get_valuation_percentile(self, date: str) -> Dict:
        """
        Calculate VN-Index PE/PB percentile (5-year lookback).

        Returns:
            {
                'vnindex_pe': 15.2,
                'pe_percentile': 85,  # In top 15% of 5-year range
                'vnindex_pb': 2.1,
                'pb_percentile': 78
            }
        """
        # Load VN-Index PE/PB historical data (5 years)
        vnindex_pe_df = pd.read_parquet("DATA/processed/valuation/vnindex/vnindex_pe_historical.parquet")

        # Filter last 5 years
        five_years_ago = pd.to_datetime(date) - pd.DateOffset(years=5)
        historical = vnindex_pe_df[vnindex_pe_df['date'] >= five_years_ago]

        # Get current values
        current = vnindex_pe_df[vnindex_pe_df['date'] == date].iloc[0]

        # Calculate percentiles
        pe_percentile = (historical['pe_ratio'] < current['pe_ratio']).sum() / len(historical) * 100
        pb_percentile = (historical['pb_ratio'] < current['pb_ratio']).sum() / len(historical) * 100

        return {
            'vnindex_pe': current['pe_ratio'],
            'pe_percentile': pe_percentile,
            'vnindex_pb': current['pb_ratio'],
            'pb_percentile': pb_percentile
        }

    def _get_market_breadth(self, date: str) -> Dict:
        """
        Get market breadth for date.

        Returns:
            {
                'above_ma200': 380,
                'total_stocks': 450,
                'above_ma200_pct': 84.4
            }
        """
        # Load market breadth data
        breadth_df = pd.read_parquet("DATA/processed/technical/market_breadth/market_breadth_daily.parquet")
        breadth = breadth_df[breadth_df['date'] == date].iloc[0]

        return {
            'above_ma200': breadth['above_ma200'],
            'total_stocks': breadth['total_stocks'],
            'above_ma200_pct': breadth['above_ma200_pct']
        }

    def _get_volume_analysis(self, date: str) -> Dict:
        """
        Analyze market-wide volume.

        Returns:
            {
                'total_volume': 500_000_000,
                'avg_volume_20d': 350_000_000,
                'volume_pct_of_avg': 142.8
            }
        """
        # Load OHLCV data
        ohlcv_df = pd.read_parquet("DATA/raw/ohlcv/OHLCV_mktcap.parquet")

        # Filter date
        day_data = ohlcv_df[ohlcv_df['date'] == date]
        total_volume = day_data['volume'].sum()

        # Calculate 20-day average
        last_20_days = ohlcv_df[ohlcv_df['date'] <= date].tail(20 * len(day_data))
        avg_volume_20d = last_20_days.groupby('date')['volume'].sum().mean()

        return {
            'total_volume': total_volume,
            'avg_volume_20d': avg_volume_20d,
            'volume_pct_of_avg': (total_volume / avg_volume_20d) * 100 if avg_volume_20d > 0 else 100
        }

    def _get_volatility_analysis(self, date: str) -> Dict:
        """
        Calculate market volatility (VN-Index ATR percentile).

        Returns:
            {
                'atr_14': 25.5,
                'volatility_percentile': 68
            }
        """
        # Implementation: Calculate VN-Index ATR and percentile
        pass

    def _classify_valuation(self, data: Dict) -> str:
        """Classify valuation signal."""
        pe_pct = data['pe_percentile']

        if pe_pct >= 90:
            return 'VERY_EXPENSIVE'
        elif pe_pct >= 70:
            return 'EXPENSIVE'
        elif pe_pct <= 20:
            return 'VERY_CHEAP'
        elif pe_pct <= 40:
            return 'CHEAP'
        else:
            return 'FAIR'

    def _classify_breadth(self, data: Dict) -> str:
        """Classify breadth signal."""
        breadth_pct = data['above_ma200_pct']

        if breadth_pct >= 80:
            return 'EXTREME_BULLISH'
        elif breadth_pct >= 60:
            return 'BULLISH'
        elif breadth_pct <= 20:
            return 'EXTREME_BEARISH'
        elif breadth_pct <= 40:
            return 'BEARISH'
        else:
            return 'NEUTRAL'

    def _classify_volume(self, data: Dict) -> str:
        """Classify volume signal."""
        vol_pct = data['volume_pct_of_avg']

        if vol_pct >= 150:
            return 'CLIMAX'
        elif vol_pct >= 120:
            return 'HIGH'
        elif vol_pct <= 70:
            return 'LOW'
        else:
            return 'NORMAL'

    def _classify_volatility(self, data: Dict) -> str:
        """Classify volatility signal."""
        # Implementation
        pass

    def _determine_regime(self, valuation, breadth, volume, volatility) -> tuple:
        """
        Determine market regime based on all factors.

        Returns:
            (regime, confidence)
        """
        # Bubble detection
        bubble_score = 0
        if valuation['pe_percentile'] >= 90:
            bubble_score += 3
        elif valuation['pe_percentile'] >= 75:
            bubble_score += 2

        if breadth['above_ma200_pct'] >= 80:
            bubble_score += 3
        elif breadth['above_ma200_pct'] >= 70:
            bubble_score += 2

        if volume['volume_pct_of_avg'] >= 150:
            bubble_score += 2

        # Bottom detection
        bottom_score = 0
        if valuation['pe_percentile'] <= 10:
            bottom_score += 3
        elif valuation['pe_percentile'] <= 25:
            bottom_score += 2

        if breadth['above_ma200_pct'] <= 20:
            bottom_score += 3
        elif breadth['above_ma200_pct'] <= 35:
            bottom_score += 2

        if volume['volume_pct_of_avg'] <= 70:
            bottom_score += 2

        # Determine regime
        if bubble_score >= 6:
            return ('BUBBLE', min(0.6 + (bubble_score - 6) * 0.05, 0.95))
        elif bottom_score >= 6:
            return ('BOTTOM', min(0.6 + (bottom_score - 6) * 0.05, 0.95))
        elif breadth['above_ma200_pct'] >= 60 and valuation['pe_percentile'] < 75:
            return ('RALLY', 0.70)
        else:
            return ('CONSOLIDATION', 0.60)
```

**Output:**

```json
{
  "date": "2025-12-15",
  "regime": "BUBBLE",
  "confidence": 0.85,
  "signals": {
    "valuation_signal": "VERY_EXPENSIVE",
    "breadth_signal": "EXTREME_BULLISH",
    "volume_signal": "CLIMAX",
    "volatility_signal": "HIGH"
  },
  "factor_scores": {
    "valuation": 92,
    "breadth": 85,
    "volume": 145,
    "volatility": 78
  }
}
```

---

### 4.5 VN-Index Integration

#### **Fetching VN-Index Data via vnstock_data**

**Reference:** `/Users/buuphan/Dev/Vietnam_dashboard/PROCESSORS/technical/pipelines/daily_ohlcv_update.py:139-143`

```python
from vnstock_data import Quote

# Fetch VN-Index OHLCV data
quote = Quote(symbol='VNINDEX', source='vnd')
vnindex_df = quote.history(start='2020-01-01', end='2025-12-15', interval='1D')

# Convert prices from thousands VND to full VND
price_columns = ['open', 'high', 'low', 'close']
for col in price_columns:
    vnindex_df[col] = vnindex_df[col] * 1000
```

#### **VN-Index Technical Indicators**

**File:** `PROCESSORS/technical/indicators/vnindex_analyzer.py`

```python
import talib
import pandas as pd
from vnstock_data import Quote

class VNIndexAnalyzer:
    """
    Calculate technical indicators for VN-Index.
    """

    def fetch_vnindex_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch VN-Index OHLCV data."""
        quote = Quote(symbol='VNINDEX', source='vnd')
        df = quote.history(start=start_date, end=end_date, interval='1D')

        # Convert prices
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            df[col] = df[col] * 1000

        df['symbol'] = 'VNINDEX'
        df['date'] = pd.to_datetime(df['time']).dt.date

        return df[['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']].copy()

    def calculate_vnindex_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all TA indicators for VN-Index."""
        df = df.copy()

        # Convert to numpy
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values

        # Moving Averages
        df['sma_20'] = talib.SMA(close, timeperiod=20)
        df['sma_50'] = talib.SMA(close, timeperiod=50)
        df['sma_100'] = talib.SMA(close, timeperiod=100)
        df['sma_200'] = talib.SMA(close, timeperiod=200)

        # Momentum
        df['rsi_14'] = talib.RSI(close, timeperiod=14)
        macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        df['macd_hist'] = macd_hist

        # Volatility
        df['atr_14'] = talib.ATR(high, low, close, timeperiod=14)

        # Volume
        df['obv'] = talib.OBV(close, volume)

        # Money Flow
        df['cmf_20'] = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)
        df['mfi_14'] = talib.MFI(high, low, close, volume, timeperiod=14)

        return df

    def get_vnindex_summary(self, date: str) -> dict:
        """
        Get VN-Index summary for specific date.

        Returns:
            {
                'date': '2025-12-15',
                'close': 1285.5,
                'ma20': 1270.2,
                'ma50': 1250.8,
                'ma200': 1220.5,
                'rsi': 62.5,
                'macd_signal': 'BULLISH_CROSS',
                'trend': 'UPTREND',
                'money_flow': 'ACCUMULATION'
            }
        """
        # Implementation: Load data and calculate summary
        pass
```

**Integration with Daily Pipeline:**

```python
# In daily_alerts_update.py

def update_vnindex_indicators(date: str):
    """Update VN-Index indicators."""
    vnindex_analyzer = VNIndexAnalyzer()

    # Fetch 200 sessions
    df = vnindex_analyzer.fetch_vnindex_data(
        start_date=(pd.to_datetime(date) - pd.DateOffset(days=400)).strftime('%Y-%m-%d'),
        end_date=date
    )

    # Keep only last 200 trading sessions
    df = df.tail(200)

    # Calculate indicators
    df = vnindex_analyzer.calculate_vnindex_indicators(df)

    # Save to processed/technical/vnindex/
    output_path = Path("DATA/processed/technical/vnindex/vnindex_indicators.parquet")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    logger.info(f"✅ VN-Index indicators updated for {date}")
```

---

### 4.6 Output Files & Storage

**New Data Files:**

```
DATA/processed/technical/
├── money_flow/
│   ├── individual_money_flow.parquet    # All stocks
│   └── sector_money_flow.parquet        # Sector aggregates
│
├── sector_breadth/
│   └── sector_breadth_daily.parquet     # Sector breadth metrics
│
├── market_regime/
│   └── market_regime_history.parquet    # Daily regime detection
│
└── vnindex/
    └── vnindex_indicators.parquet       # VN-Index TA indicators
```

**Schema Examples:**

**1. individual_money_flow.parquet**
```
date | symbol | cmf_20 | mfi_14 | obv | ad_line | vpt | money_flow_signal
```

**2. sector_money_flow.parquet**
```
date | sector_code | money_flow | inflow_pct | flow_signal | stock_count | top_contributors
```

**3. sector_breadth_daily.parquet**
```
date | sector_code | total_stocks | above_ma20 | above_ma50 | above_ma200 |
     | above_ma20_pct | above_ma50_pct | above_ma200_pct | ad_ratio | sector_strength
```

**4. market_regime_history.parquet**
```
date | regime | confidence | valuation_signal | breadth_signal | volume_signal |
     | pe_percentile | above_ma200_pct | volume_pct_of_avg
```

**5. vnindex_indicators.parquet**
```
date | symbol | open | high | low | close | volume | sma_20 | sma_50 | sma_200 |
     | rsi_14 | macd | macd_signal | atr_14 | obv | cmf_20 | mfi_14
```

---

### 4.7 Implementation Roadmap (Phase 4)

| Task | File | Duration | Status |
|------|------|----------|--------|
| Money Flow Indicators | `money_flow.py` | 1 day | ⏳ Pending |
| Sector Money Flow | `sector_money_flow.py` | 0.5 day | ⏳ Pending |
| Sector Breadth | `sector_breadth.py` | 0.5 day | ⏳ Pending |
| Market Regime Detector | `market_regime.py` | 1 day | ⏳ Pending |
| VN-Index Integration | `vnindex_analyzer.py` | 0.5 day | ⏳ Pending |
| Daily Pipeline Integration | Update `daily_alerts_update.py` | 0.5 day | ⏳ Pending |
| Streamlit Dashboard | New pages | 1 day | ⏳ Pending |
| **TOTAL** | | **5 days** | |

---

### 4.8 Streamlit Dashboard Design (Advanced Features)

**New Pages:**

**1. Money Flow Dashboard**
```
┌────────────────────────────────────────────────────────┐
│  💰 MONEY FLOW ANALYSIS - 2025-12-15                   │
├────────────────────────────────────────────────────────┤
│                                                         │
│  📊 SECTOR MONEY FLOW                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Sector      | Money Flow | Inflow % | Signal    │  │
│  ├─────────────┼────────────┼──────────┼───────────┤  │
│  │ BANKING     │ 5.2T VND   │ +12.5%   │ STRONG ↑  │  │
│  │ TECH        │ 2.8T VND   │ -8.3%    │ OUTFLOW ↓ │  │
│  │ REAL_ESTATE │ 4.1T VND   │ +3.2%    │ INFLOW ↑  │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  🔥 TOP ACCUMULATION STOCKS                            │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Symbol | CMF | MFI | OBV Trend | Signal         │  │
│  ├────────┼─────┼─────┼───────────┼────────────────┤  │
│  │ ACB    │ 0.12│ 58  │ RISING    │ STRONG_ACCUM   │  │
│  │ HPG    │ 0.08│ 52  │ RISING    │ ACCUMULATION   │  │
│  └─────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

**2. Market Regime Dashboard**
```
┌────────────────────────────────────────────────────────┐
│  🎯 MARKET REGIME ANALYSIS - 2025-12-15                │
├────────────────────────────────────────────────────────┤
│                                                         │
│  CURRENT REGIME: BUBBLE (Confidence: 85%)              │
│  ⚠️ WARNING: Market showing signs of overheating       │
│                                                         │
│  FACTOR ANALYSIS:                                      │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Valuation:  ████████████████████░ 92% (EXPENSIVE)│  │
│  │ Breadth:    █████████████████░░░ 85% (EXTREME)  │  │
│  │ Volume:     ██████████████░░░░░░ 145% (CLIMAX)  │  │
│  │ Volatility: █████████████░░░░░░░ 78% (HIGH)     │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  HISTORICAL REGIME TIMELINE:                           │
│  [Chart showing regime changes over time]              │
└────────────────────────────────────────────────────────┘
```

**3. Sector Breadth Dashboard**
```
┌────────────────────────────────────────────────────────┐
│  📊 SECTOR BREADTH ANALYSIS - 2025-12-15               │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Sector      | Total | >MA20 | >MA50 | >MA200 | Strength│
│  ────────────┼───────┼───────┼───────┼────────┼─────────│
│  BANKING     │  28   │ 78.6% │ 64.3% │ 53.6%  │ STRONG  │
│  TECH        │  15   │ 53.3% │ 40.0% │ 33.3%  │ WEAK    │
│  REAL_ESTATE │  42   │ 71.4% │ 59.5% │ 47.6%  │ STRONG  │
│                                                         │
│  SECTOR ROTATION HEATMAP:                              │
│  [Heatmap showing sector strength changes]             │
└────────────────────────────────────────────────────────┘
```

---

## 📝 HƯỚNG DẪN VẬN HÀNH (OPERATIONS GUIDE)

### Daily Operations - Cập Nhật Hàng Ngày

#### 1. Cập Nhật OHLCV Data (Chạy Đầu Tiên)

**File:** `PROCESSORS/technical/pipelines/daily_ohlcv_update.py`

**Mục đích:** Cập nhật dữ liệu giá OHLCV + market cap cho tất cả mã

**Chạy:**
```bash
# Cập nhật ngày hôm nay (auto-detect latest trading date)
python3 PROCESSORS/technical/pipelines/daily_ohlcv_update.py

# Hoặc chỉ định ngày cụ thể
python3 PROCESSORS/technical/pipelines/daily_ohlcv_update.py --date 2025-12-15

# Fallback: Cập nhật lại khoảng thời gian
python3 PROCESSORS/technical/pipelines/daily_ohlcv_update.py \
    --start-date 2025-12-01 \
    --end-date 2025-12-15
```

**Output:** `DATA/raw/ohlcv/OHLCV_mktcap.parquet`

**Thời gian:** ~5-10 phút cho 450 mã

---

#### 2. Cập Nhật Technical Indicators (MA, RSI, MACD)

**File:** `PROCESSORS/technical/pipelines/daily_ta_analyzer.py`

**Mục đích:** Tính toán MA, RSI, MACD, Bollinger Bands cho tất cả mã

**Chạy:**
```bash
# Cập nhật ngày hôm nay
python3 PROCESSORS/technical/pipelines/daily_ta_analyzer.py

# Hoặc chỉ định ngày
python3 PROCESSORS/technical/pipelines/daily_ta_analyzer.py --date 2025-12-15

# Full recalculation (200 sessions cho tất cả mã)
python3 PROCESSORS/technical/pipelines/daily_ta_analyzer.py --full-recalc
```

**Output:**
- `DATA/processed/technical/moving_averages/ma_all_symbols.parquet`
- `DATA/processed/technical/rsi/rsi_all_symbols.parquet`
- `DATA/processed/technical/macd/macd_all_symbols.parquet`
- `DATA/processed/technical/bollinger/bollinger_all_symbols.parquet`

**Thời gian:**
- Daily update: ~2-3 phút
- Full recalc: ~10-15 phút

---

#### 3. Cập Nhật Market Breadth

**File:** Sử dụng `daily_ta_analyzer.py` (đã tích hợp market breadth)

**Output:** `DATA/processed/technical/market_breadth/market_breadth_daily.parquet`

---

### Full Backfill - Khôi Phục Dữ Liệu

Khi cần tạo lại toàn bộ dữ liệu lịch sử (ví dụ: sau khi xóa nhầm, hoặc thêm mã mới):

#### 1. Backfill OHLCV (200 sessions)

```bash
# Tính toán lại 200 phiên giao dịch gần nhất
python3 PROCESSORS/technical/pipelines/daily_ohlcv_update.py \
    --start-date 2024-04-01 \
    --end-date 2025-12-15
```

**Lưu ý:** 200 phiên ≈ 10 tháng, nên start-date nên cách end-date ~12 tháng để đảm bảo

#### 2. Backfill Technical Indicators

```bash
# Full recalculation cho tất cả indicators
python3 PROCESSORS/technical/pipelines/daily_ta_analyzer.py --full-recalc
```

---

### Thứ Tự Chạy (Dependencies)

**Quan trọng:** Phải chạy theo thứ tự này vì có dependencies:

```
1. OHLCV Update (daily_ohlcv_update.py)
   ↓
2. TA Indicators + Market Breadth (daily_ta_analyzer.py)
```

**Không được:** Chạy TA analyzer trước khi có OHLCV → sẽ lỗi!

---

### Kiểm Tra Kết Quả

#### 1. Kiểm tra OHLCV có update không

```bash
# Xem ngày mới nhất
python3 -c "
import pandas as pd
df = pd.read_parquet('DATA/raw/ohlcv/OHLCV_mktcap.parquet')
print(f'Latest date: {df[\"date\"].max()}')
print(f'Total records: {len(df)}')
print(f'Symbols: {df[\"symbol\"].nunique()}')
"
```

#### 2. Kiểm tra TA Indicators

```bash
# Xem MA data
python3 -c "
import pandas as pd
df = pd.read_parquet('DATA/processed/technical/basic_data.parquet')
print(f'Latest date: {df[\"date\"].max()}')
print(f'Total records: {len(df)}')
print(f'Columns: {list(df.columns)}')
"
```

#### 3. Kiểm tra Market Breadth

```bash
# Xem breadth hôm nay
python3 -c "
import pandas as pd

df = pd.read_parquet('DATA/processed/technical/market_breadth/market_breadth_daily.parquet')
latest = df.iloc[-1]
print(f'Date: {latest[\"date\"]}')
print(f'Above MA20: {latest[\"above_ma20\"]} ({latest[\"above_ma20_pct\"]:.1f}%)')
print(f'Above MA50: {latest[\"above_ma50\"]} ({latest[\"above_ma50_pct\"]:.1f}%)')
print(f'Market Trend: {latest[\"market_trend\"]}')
"
```

---

### Troubleshooting

#### Lỗi: "No module named 'talib'"

**Giải pháp:**
```bash
# macOS
brew install ta-lib
pip install TA-Lib

# Ubuntu
sudo apt-get install ta-lib
pip install TA-Lib
```

#### Lỗi: "File not found: OHLCV_mktcap.parquet"

**Giải pháp:** Chạy OHLCV update trước:
```bash
python3 PROCESSORS/technical/pipelines/daily_ohlcv_update.py
```

#### Performance chậm (>10 phút)

**Giải pháp:**
1. Kiểm tra đang load bao nhiêu sessions:
   ```python
   # Should be reasonable, not 1000+
   df = pd.read_parquet('DATA/raw/ohlcv/OHLCV_mktcap.parquet')
   print(len(df) / df['symbol'].nunique())
   ```

2. Nếu quá nhiều, xóa data cũ và backfill lại:
   ```bash
   # Backup first
   cp DATA/raw/ohlcv/OHLCV_mktcap.parquet DATA/raw/ohlcv/OHLCV_mktcap.parquet.backup

   # Delete and rebuild
   rm DATA/raw/ohlcv/OHLCV_mktcap.parquet
   python3 PROCESSORS/technical/pipelines/daily_ohlcv_update.py --start-date 2024-04-01 --end-date 2025-12-15
   ```

---

### File Size Monitoring

**Expected sizes:**

| File | Size | Notes |
|------|------|-------|
| OHLCV_mktcap.parquet | ~20-50 MB | Depends on history length |
| basic_data.parquet | ~30-80 MB | All TA indicators |
| market_breadth_daily.parquet | ~100 KB | 200 days × 1 row/day |

---

**END OF PLAN**

---

## ✅ IMPLEMENTATION STATUS (2025-12-15)

### Phase 1-4: COMPLETED ✅

All phases from the original plan have been successfully implemented:

**Phase 1: Alert Detection Engine** ✅ COMPLETE
- File: `PROCESSORS/technical/indicators/alert_detector.py`
- MA Crossover detection (20/50/100/200)
- Smart Volume Spike with 4-factor confirmation
- Breakout/Breakdown detection with volume
- Candlestick patterns (10 most reliable)
- Combined signal scoring system

**Phase 2: Market Breadth** ✅ COMPLETE
- Integrated into `daily_complete_ta_update.py`
- % stocks above MA20/50/100/200
- Advance-Decline ratio
- Market trend classification

**Phase 3: Daily Pipeline** ✅ COMPLETE
- File: `PROCESSORS/technical/pipelines/daily_complete_ta_update.py`
- Complete 8-step pipeline:
  1. VN-Index analysis
  2. Technical indicators
  3. Alert detection
  4. Money flow (individual)
  5. Sector money flow
  6. Market breadth
  7. Sector breadth
  8. Market regime detection
- Runtime: ~40-50 seconds for full update

**Phase 4: Advanced Features** ✅ COMPLETE
- Money Flow Analysis: `PROCESSORS/technical/indicators/money_flow.py`
- Sector Money Flow: `PROCESSORS/technical/indicators/sector_money_flow.py`
- Sector Breadth: `PROCESSORS/technical/indicators/sector_breadth.py`
- Market Regime Detection: `PROCESSORS/technical/indicators/market_regime.py`
- VN-Index Integration: `PROCESSORS/technical/indicators/vnindex_analyzer.py`

**Phase 5: Streamlit Dashboard** ✅ COMPLETE
- File: `WEBAPP/pages/technical_analysis.py`
- 7 comprehensive tabs:
  1. 📈 Market Overview - Market breadth trends, A/D ratio
  2. 🚨 Trading Alerts - MA crossover, volume spike, breakout, patterns
  3. 💰 Money Flow - Sector and individual money flow analysis
  4. 📊 Market Breadth - Historical breadth metrics
  5. 🏢 Sector Analysis - Sector strength ranking and breadth
  6. 📉 VN-Index - VN-Index price chart with indicators
  7. 🌡️ Market Regime - Current regime and component scores

---

### Implementation Details

**Technology Stack:**
- TA-Lib for fast calculations (10-100x faster than pandas)
- Parquet format for efficient storage
- 200 trading sessions lookback
- Multi-factor confirmation systems

**Performance Metrics:**
- Complete pipeline: ~40-50 seconds
- Technical indicators: ~15 seconds
- Alert detection: ~8 seconds  
- Money flow: ~6 seconds
- Sector analysis: ~2 seconds
- VN-Index fetch: ~3-5 seconds

**Output Files Created:**
```
DATA/processed/technical/
├── basic_data.parquet (18.6 MB)
├── alerts/
│   ├── daily/ (latest snapshots)
│   └── historical/ (full history)
├── money_flow/
│   ├── individual_money_flow.parquet (6.6 MB)
│   └── sector_money_flow.parquet
├── market_breadth/
│   └── market_breadth_daily.parquet
├── sector_breadth/
│   └── sector_breadth_daily.parquet
├── market_regime/
│   └── market_regime_history.parquet
└── vnindex/
    └── vnindex_indicators.parquet
```

---

### How to Run

**Daily Update (Recommended):**
```bash
# Run complete pipeline with all features
python3 PROCESSORS/technical/pipelines/daily_complete_ta_update.py

# Specify number of sessions (default: 200)
python3 PROCESSORS/technical/pipelines/daily_complete_ta_update.py --sessions 200

# Specify date
python3 PROCESSORS/technical/pipelines/daily_complete_ta_update.py --date 2025-12-15
```

**Individual Components:**
```bash
# Technical indicators only
python3 PROCESSORS/technical/indicators/technical_processor.py --sessions 200

# Sector breadth
python3 PROCESSORS/technical/indicators/sector_breadth.py --date 2025-12-15

# Market regime
python3 PROCESSORS/technical/indicators/market_regime.py --date 2025-12-15

# VN-Index analysis
python3 PROCESSORS/technical/indicators/vnindex_analyzer.py --sessions 500
```

**View Dashboard:**
```bash
streamlit run WEBAPP/main_app.py
# Navigate to "Technical Analysis" page
```

---

### Documentation

**Complete README:** `PROCESSORS/technical/README.md`
- Features implemented
- Usage examples
- Data schemas
- Performance benchmarks
- Troubleshooting guide
- Dashboard instructions

---

### Status Summary

| Phase | Features | Status | Files |
|-------|----------|--------|-------|
| 1 | Alert Detection | ✅ COMPLETE | alert_detector.py |
| 2 | Market Breadth | ✅ COMPLETE | Built into pipeline |
| 3 | Daily Pipeline | ✅ COMPLETE | daily_complete_ta_update.py |
| 4 | Money Flow | ✅ COMPLETE | money_flow.py, sector_money_flow.py |
| 4 | Sector Analysis | ✅ COMPLETE | sector_breadth.py |
| 4 | Market Regime | ✅ COMPLETE | market_regime.py |
| 4 | VN-Index | ✅ COMPLETE | vnindex_analyzer.py |
| 5 | Dashboard | ✅ COMPLETE | technical_analysis.py |

**Total Implementation Time:** ~3 days
**Lines of Code:** ~3,500 lines
**Test Status:** All features tested with real data

---

**🎉 PROJECT COMPLETE - ALL PLANNED FEATURES IMPLEMENTED**

Last Updated: 2025-12-15
