# 📊 TECHNICAL INDICATORS WITH TA-LIB INTEGRATION GUIDE

**Date:** 2025-12-08  
**Purpose:** Comprehensive guide for technical indicators using TA-Lib in Vietnam Dashboard

---

## 🎯 MỤC TIÊU

1. **Tích hợp TA-Lib** vào architecture hiện tại
2. **Tối ưu performance** với C implementation
3. **Tạo indicators chuyên biệt** cho thị trường Việt Nam
4. **Cung cấp API endpoints** cho AI analysis
5. **Cập nhật Streamlit dashboard** để hiển thị technical data

---

## 🏗️ ARCHITECTURE TỔNG TỤC

### Cấu trúc tổng thể

```
Vietnam_Dashboard/
├── DATA/                           ← DATA LAYER
│   ├── raw/ohlcv/                  ← OHLCV data
│   └── processed/technical/           ← Technical results
│       ├── ma_statistics/           ← MA statistics
│       ├── market_breadth/           ← Market breadth
│       └── sector_rotation/           ← Sector rotation
│
├── PROCESSORS/                      ← PROCESSOR LAYER
│   └── technical/indicators/       ← Technical indicators
│       ├── calculators/              ← Calculation logic
│       │   ├── ma_calculator.py      ← MA calculator
│       │   ├── rsi_calculator.py      ← RSI calculator
│       │   ├── macd_calculator.py      ← MACD calculator
│       │   └── bollinger_calculator.py ← Bollinger calculator
│       ├── formulas/                 ← Pure functions
│       │   ├── ta_formulas.py       ← TA-Lib wrappers
│       │   └── vietnam_formulas.py ← Vietnam-specific
│       └── pipelines/               ← Orchestration
│           └── technical_pipeline.py  ← Main pipeline
├── WEBAPP/                         ← APPLICATION LAYER
│   ├── services/technical_service.py ← Technical service
│   ├── api/technical_endpoints.py   ← REST API
│   └── pages/technical_dashboard.py  ← UI dashboard
└── mongodb/mcp_server/              ← MCP server
    └── handlers/technical_handler.py  ← Technical data handler
```

---

## 📚 THƯ VIỆN CÀI ĐỂT TRƯỚC

### 1. Cài đặt TA-Lib

```bash
# Cài đặt TA-Lib cho macOS
brew install ta-lib

# Cài đặt TA-Lib cho Ubuntu/Debian
sudo apt-get install -y python3-dev
pip3 install TA-Lib

# Cài đặt TA-Lib cho Windows
pip install TA-Lib
```

### 2. Import và sử dụng cơ bản

```python
import talib
import numpy as np

# Tính SMA
data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
sma = talib.SMA(data, timeperiod=5)

# Tính EMA
ema = talib.EMA(data, timeperiod=5)

# Tính RSI
rsi = talib.RSI(data, timeperiod=14)

# Tính MACD
macd, signal, hist = talib.MACD(data, fastperiod=12, slowperiod=26, signalperiod=9)
```

---

## 🎛 CÁC INDICATORS PHỔ BIỆT

### 1. Moving Averages (MA)

```python
# PROCESSORS/technical/indicators/calculators/ma_calculator.py
class MACalculator(BaseTechnicalCalculator):
    def calculate_all_ma(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tính tất cả MA types cho mỗi symbol."""
        for ticker in df['ticker'].unique():
            ticker_data = df[df['ticker'] == ticker].sort_values('date')
            close_prices = ticker_data['close'].values
            
            # Calculate MAs using TA-Lib
            sma_20 = talib.SMA(close_prices, timeperiod=20)
            sma_50 = talib.SMA(close_prices, timeperiod=50)
            sma_100 = talib.SMA(close_prices, timeperiod=100)
            sma_200 = talib.SMA(close_prices, timeperiod=200)
            
            # Calculate EMAs
            ema_12 = talib.EMA(close_prices, timeperiod=12)
            ema_26 = talib.EMA(close_prices, timeperiod=26)
            
            # Generate crossover signals
            signals = self._detect_crossovers(sma_20, sma_50)
```

### 2. Momentum Indicators

```python
# PROCESSORS/technical/indicators/calculators/rsi_calculator.py
class RSICalculator(BaseTechnicalCalculator):
    def calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tính RSI cho mỗi symbol."""
        for ticker in df['ticker'].unique():
            ticker_data = df[df['ticker'] == ticker].sort_values('date')
            close_prices = ticker_data['close'].values
            
            # Calculate RSI using TA-Lib
            rsi = talib.RSI(close_prices, timeperiod=14)
            
            # Generate signals
            overbought = rsi > 70
            oversold = rsi < 30
```

### 3. Volatility Indicators

```python
# PROCESSORS/technical/indicators/calculators/bollinger_calculator.py
class BollingerCalculator(BaseTechnicalCalculator):
    def calculate_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tính Bollinger Bands cho mỗi symbol."""
        for ticker in df['ticker'].unique():
            ticker_data = df[df['ticker'] == ticker].sort_values('date')
            close_prices = ticker_data['close'].values
            
            # Calculate Bollinger Bands using TA-Lib
            upper, middle, lower = talib.BBANDS(close_prices, timeperiod=20, nbdevup=2)
```

### 4. Volume Indicators

```python
# PROCESSORS/technical/indicators/formulas/ta_formulas.py
def calculate_obv(close: np.array, volume: np.array) -> np.array:
    """On Balance Volume using TA-Lib."""
    return talib.OBV(close, volume)

def calculate_ad_line(high: np.array, low: np.array, close: np.array, volume: np.array) -> np.array:
    """Accumulation/Distribution Line using TA-Lib."""
    return talib.AD(high, low, close, volume)
```

---

## 🎯 TÍNH HIỆU SỐ DỮNG LIỆU

### 1. Pipeline Execution

```bash
# Chạy pipeline technical hàng ngày
python3 PROCESSORS/technical/pipelines/technical_pipeline.py

# Chạy pipeline MA riêng biệt
python3 PROCESSORS/technical/pipelines/ma_update_pipeline.py
```

### 2. API Access

```python
# Lấy MA statistics qua API
import requests

response = requests.get('http://localhost:8501/api/technical/ma-stats/VCB')
data = response.json()

# Lấy MA theo sector
response = requests.get('http://localhost:8501/api/technical/ma-by-sector/Ngân hàng')
data = response.json()
```

### 3. Streamlit Dashboard

```python
# Trong technical_dashboard.py
import streamlit as st
from WEBAPP.services.technical_service import TechnicalAnalysisService

# Hiển thị MA statistics
st.header("📊 Technical Analysis")
ticker = st.text_input("Ticker", value="VCB").upper()

if ticker:
    ma_data = technical_service.get_ma_statistics([ticker])
    
    if 'ma_stats' in ma_data:
        st.dataframe(ma_data['ma_stats'])
        
        # Hiển thị số lượng cổ phiếu > MA
        total_stocks = len(ma_data['ma_stats'])
        above_ma20 = ma_data['ma_stats']['above_ma20'].sum()
        above_ma50 = ma_data['ma_stats']['above_ma50'].sum()
        above_ma100 = ma_data['ma_stats']['above_ma100'].sum()
        
        st.metric("Số lượng > MA20", above_ma20)
        st.metric("Số lượng > MA50", above_ma50)
        st.metric("Số lượng > MA100", above_ma100)
        
        # Hiển thị phần trăm
        st.metric("% > MA20", f"{above_ma20/total_stocks*100:.1f}%")
        st.metric("% > MA50", f"{above_ma50/total_stocks*100:.1f}%")
        st.metric("% > MA100", f"{above_ma100/total_stocks*100:.1f}%")
```

---

## 🚀 LỢI ÍCH TỐI TƯỞNG

### 1. Performance Optimization

- **Vectorized Operations**: Dùng numpy arrays thay vì loop
- **Batch Processing**: Xử lý nhiều symbols cùng lúc
- **Caching**: Lưu kết quả trung gian để tránh tính lại
- **Parallel Processing**: Dùng multiprocessing cho large datasets

### 2. Custom Indicators cho Việt Nam

```python
# Vietnam Market Sentiment Score
def calculate_vietnam_sentiment(price_change: np.array, volume: np.array) -> np.array:
    """Tính market sentiment score cho thị trường Việt Nam."""
    # Vietnam market characteristics
    volume_weight = np.log1p(volume / np.mean(volume) + 1)
    
    # Combine price change and volume
    sentiment = price_change * volume_weight
    
    # Normalize
    max_sentiment = np.max(np.abs(sentiment))
    if max_sentiment > 0:
        return sentiment / max_sentiment
    else:
        return np.zeros_like(sentiment)

# State-owned stocks adjustment
def adjust_breadth_for_vietnam(basic_breadth: dict, state_owned_ratio: float = 0.15) -> dict:
    """Điều chỉnh market breadth cho Việt Nam."""
    adjusted_ratio = basic_breadth['ratio'] * (1 + state_owned_ratio)
    
    return {
        **basic_breadth,
        'adjusted_ratio': adjusted_ratio,
        'market_state': 'Bullish' if adjusted_ratio > 1.5 else 'Bearish' if adjusted_ratio < 0.7 else 'Neutral'
    }
```

---

## 📚 TÀI LIỆU THAM KHẢO

### 1. Testing

```python
# Test TA-Lib integration
import unittest
import numpy as np
import talib

class TestTAIndicators(unittest.TestCase):
    def test_sma_calculation(self):
        """Test SMA calculation."""
        data = np.array([1, 2, 3, 4, 5])
        expected = np.array([np.nan, np.nan, 3.0, 3.5, 4.0])
        
        result = talib.SMA(data, timeperiod=3)
        np.testing.assert_array_almost_equal(result, expected)
```

### 2. Troubleshooting

```python
# Kiểm tra TA-Lib installation
import talib
print(f"TA-Lib version: {talib.__version__}")
print(f"Supported functions: {len(talib.get_functions())}")

# Kiểm tra dữ liệu đầu vào
def validate_ohlcv_data(df: pd.DataFrame) -> bool:
    """Kiểm tra dữ liệu OHLCV."""
    required_columns = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']
    
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        raise ValueError(f"Missing columns: {missing}")
    
    if df.empty:
        raise ValueError("Empty DataFrame")
    
    return True
```

---

## 🔗 TÀI LIÊN KẾT NỐI

### 1. TA-Lib Documentation
- [Official Documentation](https://mrjbq7.github.io/ta-lib/)
- [Function Reference](https://github.com/mrjbq7/ta-lib/blob/master/docs/func.md)
- [Examples Repository](https://github.com/mrjbq7/ta-lib/tree/master/examples)

### 2. Python Technical Analysis Libraries
- [TA-Lib](https://github.com/mrjbq7/ta-lib) - Recommended
- [Pandas-TA](https://github.com/twopir/pandas-ta) - Alternative
- [TA](https://github.com/bukosabino/ta) - Pure Python implementation

---

## 🎯 KẾT LUẬN

1. **Bắt đầu với MA Calculator** vì đã có code mẫu
2. **Sử dụng TA-Lib** cho performance tốt hơn
3. **Tích hợp với MCP server** để AI truy cập dữ liệu
4. **Cập nhật Streamlit dashboard** để hiển thị kết quả
5. **Test kỹ lưỡng** trước khi deploy production

---

*Hướng dẫn này sẽ giúp bạn tích hợp TA-Lib một cách hiệu quả vào architecture hiện tại, đồng thời cung cấp tài liệu tham khảo toàn diện.*

