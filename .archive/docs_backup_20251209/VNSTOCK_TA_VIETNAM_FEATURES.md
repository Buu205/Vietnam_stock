# vnstock_ta - Vietnamese Market Specific Features Analysis

**Date:** 2025-12-05  
**Source:** Context7 Documentation + Codebase Analysis

---

## 📋 Executive Summary

Sau khi tìm hiểu documentation từ `vnstock_ta` và `vnstock-agent-guide`, **không có nhiều features riêng biệt cho thị trường Việt Nam** trong `vnstock_ta` library. Library này chủ yếu cung cấp các technical indicators chuẩn (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, OBV) tương tự như các library technical analysis khác.

**Tuy nhiên**, có một số điểm đáng chú ý:

1. **Tích hợp với vnstock_data**: `vnstock_ta` được thiết kế để làm việc với data từ `vnstock_data` (Vietnamese stock data sources: VCI, VND, MAS)
2. **Vietnamese Market Context**: Library được optimize cho Vietnamese stock symbols và data format
3. **Normalization cho Vietnamese Market**: Trong codebase hiện tại có normalization step (MACD / 1000) có thể liên quan đến đặc thù thị trường VN

---

## 🔍 Features của vnstock_ta

### 1. Standard Technical Indicators

`vnstock_ta` cung cấp các indicators chuẩn:

```python
from vnstock_ta import Indicator
from vnstock_data import Quote
import pandas as pd

# Get Vietnamese stock data
quote = Quote(source="vnd", symbol="VCB")
df = quote.history(start="2024-01-01", end="2024-12-31", interval="1D")
df = df.set_index('time')  # IMPORTANT: Set time as index

# Initialize indicator calculator
indicator = Indicator(data=df)

# Trend Indicators
sma_20 = indicator.sma(length=20)
sma_50 = indicator.sma(length=50)
ema_12 = indicator.ema(length=12)

# Momentum Indicators
rsi = indicator.rsi(length=14)
macd_data = indicator.macd(fast=12, slow=26, signal=9)

# Volatility Indicators
bbands = indicator.bbands(length=20, std=2)
atr = indicator.atr(length=14)

# Volume Indicators
obv = indicator.obv()
```

### 2. Available Indicators

| Indicator Type | Functions | Description |
|---------------|------------|-------------|
| **Trend** | `sma()`, `ema()` | Moving Averages |
| **Momentum** | `rsi()`, `macd()` | Relative Strength Index, MACD |
| **Volatility** | `bbands()`, `atr()` | Bollinger Bands, Average True Range |
| **Volume** | `obv()` | On-Balance Volume |

### 3. Plotting Support

`vnstock_ta` có `Plotter` class để visualize:

```python
from vnstock_ta import Plotter

plotter = Plotter(data=df, theme='light')  # or 'dark'

# Plot candlestick with SMA
fig1 = plotter.sma(length=[20, 50], title='VCB Price with SMA 20/50', show_volume=True)
fig1.show()

# Plot RSI
fig2 = plotter.rsi(length=14, title='VCB RSI(14)', overbought=70, oversold=30)
fig2.show()

# Plot MACD
fig3 = plotter.macd(fast=12, slow=26, signal=9, title='VCB MACD')
fig3.show()

# Plot Bollinger Bands
fig4 = plotter.bbands(length=20, std=2, title='VCB Bollinger Bands')
fig4.show()
```

---

## 🇻🇳 Vietnamese Market Context

### 1. Data Source Integration

`vnstock_ta` được thiết kế để làm việc với Vietnamese data sources:

- **VCI**: Most complete data (recommended)
- **VND**: Faster performance
- **MAS**: Alternative source

```python
# Vietnamese stock symbols
quote = Quote(source="vci", symbol="VCB")  # Vietcombank
quote = Quote(source="vnd", symbol="HPG")   # Hoa Phat Group
quote = Quote(source="vci", symbol="VNM")   # Vinamilk
```

### 2. Vietnamese Market Symbols

Library hỗ trợ:
- **Stocks**: VCB, HPG, VNM, POW, etc.
- **Indices**: VN30, VNMidCap, etc.
- **Warrants**: CW symbols
- **ETFs**: ETF symbols

### 3. Market-Specific Considerations

#### A. Price Normalization

Trong codebase hiện tại (`technical_processor.py`), có normalization step cho MACD:

```python
# From technical_processor.py line 370
symbol_data['macd'] = macd_line / 1000  # Normalize for Vietnam market
symbol_data['macd_signal'] = signal_line / 1000
symbol_data['macd_histogram'] = histogram / 1000
```

**Lý do có thể:**
- Vietnamese stock prices thường có giá trị lớn (hàng nghìn VND)
- Normalization giúp indicators dễ đọc và so sánh
- Tránh overflow trong calculations

#### B. Trading Hours

Vietnamese stock market trading hours:
- **Morning session**: 9:00 AM - 11:30 AM
- **Afternoon session**: 1:00 PM - 3:00 PM
- **Daily pipeline**: Scheduled at 16:30 (after market close)

```python
# From vnstock-agent-guide documentation
# Daily pipeline runs at 16:30 after market close
schedule.every().day.at("16:30").do(daily_pipeline)
```

#### C. Market Indices

Library hỗ trợ Vietnamese market indices:

```python
from vnstock_data import Listing

listing = Listing(source="vci")
vn30_stocks = listing.symbols_by_group("VN30")
# Returns: ['VCB', 'VHM', 'HPG', ...]
```

---

## 🔄 Comparison với TA-Lib

### Current Codebase Usage

Codebase hiện tại **KHÔNG sử dụng `vnstock_ta`**, mà sử dụng:

1. **TA-Lib** (C-based, optimized performance)
2. **Custom Pandas implementations**

### Why Not vnstock_ta?

**Advantages của TA-Lib:**
- ✅ Faster performance (C-based)
- ✅ More indicators (100+)
- ✅ Industry standard
- ✅ Well-tested

**Advantages của vnstock_ta:**
- ✅ Native integration với `vnstock_data`
- ✅ Vietnamese market context
- ✅ Plotting support built-in
- ✅ Easier setup (no C dependencies)

### Recommendation

**Hybrid Approach** (như đã đề xuất trong `TA_LIB_VS_VNSTOCK_TA_COMPARISON.md`):

1. **Keep TA-Lib** cho performance-critical indicators (MA, RSI, MACD, BB)
2. **Use vnstock_ta** cho:
   - Quick prototyping
   - Plotting/visualization
   - New indicators not in TA-Lib
   - Integration với vnstock_data pipeline

---

## 📊 Vietnamese Market Specific Features (Missing)

### Features KHÔNG có trong vnstock_ta:

1. **Circuit Breaker Detection**
   - Vietnamese market có circuit breaker rules (7%, 10%, 20%)
   - Không có built-in function để detect circuit breaker events

2. **Price Limit Detection**
   - Daily price limits: ±7% (normal), ±10% (special), ±20% (new listings)
   - Không có function để check price limit hits

3. **Trading Session Analysis**
   - Morning session (9:00-11:30) vs Afternoon session (13:00-15:00)
   - Không có session-specific indicators

4. **Vietnamese Market Calendar**
   - Trading holidays (Tet, National Day, etc.)
   - Không có built-in calendar support

5. **Foreign Ownership Limits**
   - FOL (Foreign Ownership Limit) tracking
   - Không có function để check FOL status

6. **Market-Specific Patterns**
   - Vietnamese market patterns (e.g., pre-Tet rally, post-earnings behavior)
   - Không có pattern recognition

---

## 💡 Recommendations

### 1. Current Implementation (TA-Lib)

**Keep using TA-Lib** cho:
- ✅ Performance-critical calculations
- ✅ Standard indicators (MA, RSI, MACD, BB)
- ✅ Production systems

### 2. Potential vnstock_ta Usage

**Consider vnstock_ta** cho:
- 📊 Quick prototyping và testing
- 📈 Plotting/visualization needs
- 🔄 Integration với vnstock_data pipelines
- 🆕 New indicators not in TA-Lib

### 3. Custom Vietnamese Market Features

**Build custom functions** cho:
- 🚨 Circuit breaker detection
- 📅 Trading calendar (holidays)
- 💱 Price limit checking
- 📊 Session-specific analysis
- 🌏 Foreign ownership tracking

### 4. Example: Custom Circuit Breaker Detection

```python
def detect_circuit_breaker(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect circuit breaker events in Vietnamese market.
    
    Circuit breaker rules:
    - ±7%: Normal stocks
    - ±10%: Special stocks
    - ±20%: New listings (first 5 days)
    """
    df = df.copy()
    
    # Calculate price change %
    df['price_change_pct'] = df['close'].pct_change() * 100
    
    # Detect circuit breaker hits
    df['circuit_breaker_7'] = df['price_change_pct'].abs() >= 7.0
    df['circuit_breaker_10'] = df['price_change_pct'].abs() >= 10.0
    df['circuit_breaker_20'] = df['price_change_pct'].abs() >= 20.0
    
    return df
```

---

## 📚 Documentation References

1. **vnstock-agent-guide**: `/vnstock-hq/vnstock-agent-guide`
   - Comprehensive documentation
   - Code examples
   - Best practices

2. **vnstock (main library)**: `/thinh-vu/vnstock`
   - Main vnstock library
   - Data fetching capabilities

3. **Current Codebase**:
   - `data_processor/technical/technical_indicators/technical_processor.py`
   - Uses TA-Lib, not vnstock_ta

---

## ✅ Conclusion

**vnstock_ta không có nhiều features riêng cho thị trường Việt Nam**, nhưng:

1. ✅ **Tích hợp tốt** với `vnstock_data` (Vietnamese data sources)
2. ✅ **Plotting support** built-in
3. ✅ **Easy to use** (no C dependencies)
4. ❌ **Không có** circuit breaker, price limits, trading calendar
5. ❌ **Performance** không bằng TA-Lib

**Recommendation:**
- Keep TA-Lib cho production
- Use vnstock_ta cho prototyping/plotting
- Build custom functions cho Vietnamese market-specific features

---

## 🔗 Related Documents

- `docs/TA_LIB_VS_VNSTOCK_TA_COMPARISON.md` - Detailed comparison
- `docs/VNSTOCK_LIBRARIES_AUDIT.md` - Current usage audit
- `docs/VNSTOCK_PIPELINE_GUIDE.md` - Pipeline framework guide

---

*Last Updated: 2025-12-05*



