# 🎯 MASTER PLAN: TA-LIB INTEGRATION WITH ARCHITECTURE UNIFICATION

**Date:** 2025-12-08
**Purpose:** Tích hợp TA-Lib vào architecture hiện tại, chuẩn hóa technical indicators, và tạo API endpoints cho AI analysis
**Status:** 🚧 IN PROGRESS

---

## 📋 EXECUTIVE SUMMARY

### Mục tiêu
1. **Tích hợp TA-Lib** vào technical indicators hiện tại
2. **Chuẩn hóa cấu trúc 3-layer** (Data → Formulas → Calculators)
3. **Tạo API endpoints** cho AI analysis
4. **Cập nhật Streamlit dashboard** để hiển thị MA statistics
5. **Tạo MCP integration** để AI truy cập dữ liệu

### Phạm vi
- Technical indicators module (`PROCESSORS/technical/indicators/`)
- WebApp services (`WEBAPP/services/`)
- MCP server (`mongodb/mcp_server/`)
- Streamlit dashboard (`WEBAPP/pages/`)

---

## 🏗️ ARCHITECTURE DESIGN

### 1. **Technical Indicators Module Refactor**

```
PROCESSORS/technical/indicators/
├── calculators/          ← NEW: Chuyên biệt calculation logic
│   ├── __init__.py
│   ├── base_technical_calculator.py  ← Base class
│   ├── ma_calculator.py           ← Moving Averages (TA-Lib)
│   ├── market_breadth_calculator.py ← Market Breadth (TA-Lib)
│   └── sector_rotation_calculator.py ← Sector Rotation (TA-Lib)
├── formulas/            ← NEW: Pure calculation functions
│   ├── __init__.py
│   ├── ta_formulas.py      ← TA-Lib wrappers
│   ├── vietnam_formulas.py ← Vietnam-specific indicators
│   └── signal_formulas.py   ← Signal generation logic
├── pipelines/           ← NEW: Orchestration logic
│   ├── __init__.py
│   ├── technical_pipeline.py  ← Main pipeline
│   └── ma_update_pipeline.py  ← MA-specific pipeline
└── processors/         ← Existing: Data processing
    ├── technical_processor.py
    └── ma_screening_processor.py
```

### 2. **TA-Lib Integration Strategy**

#### 2.1 Formulas Layer (Pure Functions)
```python
# PROCESSORS/technical/indicators/formulas/ta_formulas.py
import talib
import numpy as np
from typing import Tuple

# Moving Averages
def calculate_sma(data: np.array, period: int) -> np.array:
    """Simple Moving Average using TA-Lib."""
    return talib.SMA(data, timeperiod=period)

def calculate_ema(data: np.array, period: int) -> np.array:
    """Exponential Moving Average using TA-Lib."""
    return talib.EMA(data, timeperiod=period)

def calculate_wma(data: np.array, period: int) -> np.array:
    """Weighted Moving Average using TA-Lib."""
    return talib.WMA(data, timeperiod=period)

# Momentum Indicators
def calculate_rsi(data: np.array, period: int = 14) -> np.array:
    """Relative Strength Index using TA-Lib."""
    return talib.RSI(data, timeperiod=period)

def calculate_macd(
    data: np.array, 
    fast_period: int = 12, 
    slow_period: int = 26, 
    signal_period: int = 9
) -> Tuple[np.array, np.array, np.array]:
    """MACD using TA-Lib."""
    macd, signal, hist = talib.MACD(
        data, fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period
    )
    return macd, signal, hist

# Volatility Indicators
def calculate_bollinger_bands(
    data: np.array, 
    period: int = 20, 
    std_dev: float = 2.0
) -> Tuple[np.array, np.array, np.array]:
    """Bollinger Bands using TA-Lib."""
    upper, middle, lower = talib.BBANDS(data, timeperiod=period, nbdevup=std_dev)
    return upper, middle, lower

# Volume Indicators
def calculate_obv(close: np.array, volume: np.array) -> np.array:
    """On Balance Volume using TA-Lib."""
    return talib.OBV(close, volume)

def calculate_ad_line(
    high: np.array, 
    low: np.array, 
    close: np.array,
    volume: np.array
) -> np.array:
    """Accumulation/Distribution Line using TA-Lib."""
    return talib.AD(high, low, close, volume)
```

#### 2.2 Calculators Layer (Business Logic)
```python
# PROCESSORS/technical/indicators/calculators/ma_calculator.py
import pandas as pd
import numpy as np
import talib
from typing import Dict, List, Optional, Tuple
from PROCESSORS.technical.indicators.calculators.base_technical_calculator import BaseTechnicalCalculator
from PROCESSORS.technical.indicators.formulas.ta_formulas import (
    calculate_sma, calculate_ema, generate_ma_crossover_signals
)

class MACalculator(BaseTechnicalCalculator):
    """Moving Average calculator using TA-Lib."""
    
    def __init__(self, symbols_file: Optional[str] = None):
        super().__init__(symbols_file)
        self.ma_periods = [20, 50, 100, 200]  # Default MA periods
        
    def calculate_ma_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MA statistics for all symbols."""
        if not self.validate_data(df):
            raise ValueError("Invalid OHLCV data format")
            
        results = []
        
        for ticker in df['ticker'].unique():
            ticker_data = df[df['ticker'] == ticker].sort_values('date')
            close_prices = ticker_data['close'].values
            
            # Calculate MAs using TA-Lib
            sma_20 = calculate_sma(close_prices, 20)
            sma_50 = calculate_sma(close_prices, 50)
            sma_100 = calculate_sma(close_prices, 100)
            sma_200 = calculate_sma(close_prices, 200)
            
            # Count stocks above each MA
            above_ma20 = np.sum(close_prices > sma_20)
            above_ma50 = np.sum(close_prices > sma_50)
            above_ma100 = np.sum(close_prices > sma_100)
            
            # Calculate percentages
            total_stocks = len(close_prices)
            pct_above_ma20 = (above_ma20 / total_stocks) * 100
            pct_above_ma50 = (above_ma50 / total_stocks) * 100
            pct_above_ma100 = (above_ma100 / total_stocks) * 100
            
            # Combine results
            ticker_results = pd.DataFrame({
                'ticker': ticker,
                'date': ticker_data['date'].iloc[-1],  # Latest date
                'close': ticker_data['close'].iloc[-1],  # Latest price
                'total_stocks': total_stocks,
                'above_ma20': above_ma20,
                'above_ma50': above_ma50,
                'above_ma100': above_ma100,
                'pct_above_ma20': pct_above_ma20,
                'pct_above_ma50': pct_above_ma50,
                'pct_above_ma100': pct_above_ma100
            })
            
            results.append(ticker_results)
            
        return pd.concat(results, ignore_index=True)
    
    def calculate_ma_by_sector(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MA statistics grouped by sector."""
        # Load sector mapping
        from PROCESSORS.core.shared.unified_mapper import UnifiedTickerMapper
        mapper = UnifiedTickerMapper()
        
        # Add sector info to dataframe
        df_with_sector = df.copy()
        df_with_sector['sector'] = df_with_sector['ticker'].apply(
            lambda x: mapper.get_complete_info(x)['sector']
        )
        
        # Calculate MA stats by sector
        sector_results = []
        
        for sector in df_with_sector['sector'].unique():
            if pd.isna(sector):
                continue
                
            sector_data = df_with_sector[df_with_sector['sector'] == sector]
            
            # Calculate MAs for all stocks in sector
            sector_ma_stats = []
            for ticker in sector_data['ticker'].unique():
                ticker_data = sector_data[sector_data['ticker'] == ticker].sort_values('date')
                close_prices = ticker_data['close'].values
                
                # Calculate MAs using TA-Lib
                sma_20 = calculate_sma(close_prices, 20)
                sma_50 = calculate_sma(close_prices, 50)
                sma_100 = calculate_sma(close_prices, 100)
                
                # Count stocks above each MA
                above_ma20 = np.sum(close_prices > sma_20)
                above_ma50 = np.sum(close_prices > sma_50)
                above_ma100 = np.sum(close_prices > sma_100)
                
                sector_ma_stats.append({
                    'ticker': ticker,
                    'above_ma20': above_ma20,
                    'above_ma50': above_ma50,
                    'above_ma100': above_ma100
                })
            
            # Convert to DataFrame
            sector_stats_df = pd.DataFrame(sector_ma_stats)
            
            # Calculate sector totals
            total_stocks = len(sector_stats_df)
            total_above_ma20 = sector_stats_df['above_ma20'].sum()
            total_above_ma50 = sector_stats_df['above_ma50'].sum()
            total_above_ma100 = sector_stats_df['above_ma100'].sum()
            
            # Calculate percentages
            pct_above_ma20 = (total_above_ma20 / total_stocks) * 100
            pct_above_ma50 = (total_above_ma50 / total_stocks) * 100
            pct_above_ma100 = (total_above_ma100 / total_stocks) * 100
            
            # Combine sector results
            sector_result = pd.DataFrame({
                'sector': sector,
                'date': df['date'].max(),  # Latest date in data
                'total_stocks': total_stocks,
                'above_ma20': total_above_ma20,
                'above_ma50': total_above_ma50,
                'above_ma100': total_above_ma100,
                'pct_above_ma20': pct_above_ma20,
                'pct_above_ma50': pct_above_ma50,
                'pct_above_ma100': pct_above_ma100
            }, index=[0])
            
            sector_results.append(sector_result)
            
        return pd.concat(sector_results, ignore_index=True)
    
    def run_calculation(self, symbols: List[str] = None) -> pd.DataFrame:
        """Main calculation method."""
        # Load data
        ohlcv_data = self.load_ohlcv_data(symbols)
        
        # Calculate MA statistics
        ma_stats = self.calculate_ma_stats(ohlcv_data)
        
        # Calculate MA by sector
        ma_by_sector = self.calculate_ma_by_sector(ohlcv_data)
        
        # Save results
        self.save_results(ma_stats, "ma_statistics.parquet")
        self.save_results(ma_by_sector, "ma_by_sector.parquet")
        
        return ma_stats, ma_by_sector
```

### 3. **API Endpoints for Technical Data**

#### 3.1 MCP Server Extensions
```python
# mongodb/mcp_server/handlers/technical_handler.py
from PROCESSORS.technical.indicators.calculators.ma_calculator import MACalculator

class TechnicalHandler:
    """Handle technical data requests via MCP."""
    
    def __init__(self):
        self.ma_calculator = MACalculator()
    
    def get_ma_statistics(self, tickers: List[str]) -> dict:
        """Get MA statistics for tickers."""
        try:
            ma_stats, ma_by_sector = self.ma_calculator.run_calculation(tickers)
            
            return {
                'ma_stats': ma_stats.to_dict('records'),
                'ma_by_sector': ma_by_sector.to_dict('records'),
                'total_tickers': len(ma_stats['ticker'].unique()),
                'last_updated': ma_stats['date'].max()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_ma_by_ticker(self, ticker: str) -> dict:
        """Get MA statistics for a specific ticker."""
        try:
            ma_stats, _ = self.ma_calculator.run_calculation([ticker])
            
            if len(ma_stats) > 0:
                ticker_data = ma_stats[ma_stats['ticker'] == ticker].iloc[0]
                
                return {
                    'ticker': ticker,
                    'current_price': ticker_data['close'],
                    'sma_20': ticker_data['sma_20'],
                    'sma_50': ticker_data['sma_50'],
                    'sma_100': ticker_data['sma_100'],
                    'above_ma20': ticker_data['above_ma20'],
                    'above_ma50': ticker_data['above_ma50'],
                    'above_ma100': ticker_data['above_ma100'],
                    'pct_above_ma20': ticker_data['pct_above_ma20'],
                    'pct_above_ma50': ticker_data['pct_above_ma50'],
                    'pct_above_ma100': ticker_data['pct_above_ma100']
                }
            else:
                return {'error': f'No data found for {ticker}'}
        except Exception as e:
            return {'error': str(e)}
```

#### 3.2 REST API Endpoints
```python
# WEBAPP/api/technical_endpoints.py
from flask import Flask, request, jsonify
from WEBAPP.services.technical_service import TechnicalAnalysisService

app = Flask(__name__)
technical_service = TechnicalAnalysisService()

@app.route('/api/technical/ma-stats/<ticker>', methods=['GET'])
def get_ma_stats(ticker: str):
    """Get MA statistics for a ticker."""
    try:
        result = technical_service.get_ma_statistics([ticker])
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/technical/ma-by-sector/<sector>', methods=['GET'])
def get_ma_by_sector(sector: str):
    """Get MA statistics by sector."""
    try:
        result = technical_service.get_ma_by_sector(sector)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/technical/ma-crossover/<ticker>', methods=['GET'])
def get_ma_crossover_signals(ticker: str):
    """Get MA crossover signals for a ticker."""
    try:
        result = technical_service.get_ma_crossover_signals([ticker])
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
```

### 4. **Streamlit Dashboard Integration**

#### 4.1 Technical Dashboard Page
```python
# WEBAPP/pages/technical_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from WEBAPP.services.technical_service import TechnicalAnalysisService
from WEBAPP.components.charts import create_ma_chart, create_sector_comparison_chart

def render_ma_statistics():
    """Render MA statistics section."""
    st.header("📊 Moving Average Statistics")
    
    # Get user input
    ticker = st.text_input("Enter ticker:", value="VCB").upper()
    period = st.selectbox("Select MA period:", options=[20, 50, 100, 200], index=1)
    
    if ticker:
        # Get MA data
        ma_stats = technical_service.get_ma_statistics([ticker])
        
        if 'error' not in ma_stats:
            # Display current stats
            st.write(f"**Current Price:** {ma_stats['current_price']:,.2f}")
            st.write(f"**MA {period}:** {ma_stats[f'sma_{period}']:,.2f}")
            
            # Display MA chart
            ma_data = technical_service.get_ma_history([ticker], period)
            if ma_data is not None:
                fig = create_ma_chart(ma_data, period)
                st.plotly_chart(fig, use_container_width=True)
                
                # Display crossover signals
                signals = technical_service.get_ma_crossover_signals([ticker])
                if 'error' not in signals:
                    latest_signal = signals['current_signal']
                    st.write(f"**Latest Signal:** {latest_signal}")
                    
                    # Signal history
                    signal_history = signals.get('signal_history', [])
                    if signal_history:
                        st.write("**Signal History:**")
                        for signal in signal_history[-5:]:  # Last 5 signals
                            st.write(f"- {signal['date']}: {signal['signal_type']}")

def render_ma_by_sector():
    """Render MA statistics by sector."""
    st.header("📈 MA Analysis by Sector")
    
    # Get sector selection
    from PROCESSORS.core.shared.unified_mapper import UnifiedTickerMapper
    mapper = UnifiedTickerMapper()
    sectors = mapper.get_all_sectors()
    
    selected_sector = st.selectbox("Select sector:", options=sectors)
    
    if selected_sector:
        # Get MA data by sector
        ma_by_sector = technical_service.get_ma_by_sector(selected_sector)
        
        if 'error' not in ma_by_sector:
            # Display sector stats
            sector_data = ma_by_sector['ma_by_sector']
            
            # Create sector comparison chart
            fig = create_sector_comparison_chart(sector_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display sector table
            st.dataframe(sector_data)

def main():
    """Main function for technical dashboard."""
    st.set_page_config(page_title="Technical Analysis", page_icon="📊")
    
    # Navigation
    page = st.sidebar.selectbox("Select Analysis:", options=[
        "MA Statistics", "MA by Sector", "MA Crossovers"
    ])
    
    if page == "MA Statistics":
        render_ma_statistics()
    elif page == "MA by Sector":
        render_ma_by_sector()
    elif page == "MA Crossovers":
        render_ma_crossovers()
```

---

## 🚀 IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 1-2)
- [ ] Create `PROCESSORS/technical/indicators/formulas/ta_formulas.py`
- [ ] Create `PROCESSORS/technical/indicators/calculators/ma_calculator.py`
- [ ] Update `PROCESSORS/technical/indicators/calculators/base_technical_calculator.py`
- [ ] Create `PROCESSORS/technical/indicators/pipelines/technical_pipeline.py`
- [ ] Test TA-Lib integration with sample data

### Phase 2: API Integration (Week 3-4)
- [ ] Create `WEBAPP/services/technical_service.py`
- [ ] Create `mongodb/mcp_server/handlers/technical_handler.py`
- [ ] Create `WEBAPP/api/technical_endpoints.py`
- [ ] Update MCP server with technical handlers
- [ ] Test API endpoints with curl

### Phase 3: Dashboard Integration (Week 5-6)
- [ ] Create `WEBAPP/pages/technical_dashboard.py`
- [ ] Create `WEBAPP/components/charts.py` (technical charts)
- [ ] Update main navigation to include Technical Analysis
- [ ] Test complete workflow with sample data

### Phase 4: Documentation (Week 7-8)
- [ ] Update `QUICK_REFERENCE.md` with technical commands
- [ ] Update `ARCHITECTURE_STANDARDS.md` with technical indicators
- [ ] Create technical analysis guide in `docs/`
- [ ] Record video tutorial for technical analysis workflow

---

## 📝 SUCCESS CRITERIA

### Phase 1 Completion
- [ ] All TA-Lib functions tested with sample data
- [ ] MA calculator produces correct output format
- [ ] Base technical calculator works with inheritance
- [ ] Pipeline executes without errors

### Phase 2 Completion
- [ ] MCP server returns technical data correctly
- [ ] API endpoints respond with proper JSON format
- [ ] Technical service integrates with calculators

### Phase 3 Completion
- [ ] Streamlit dashboard displays MA statistics
- [ ] Charts render correctly with Plotly
- [ ] Sector analysis works with UnifiedTickerMapper

### Phase 4 Completion
- [ ] Documentation is complete and accurate
- [ ] Quick reference includes all technical commands
- [ ] Architecture standards updated with technical indicators

---

## 🔧 TECHNICAL CONSIDERATIONS

### TA-Lib Installation
```bash
# Install TA-Lib for technical indicators
pip install TA-Lib
```

### Performance Optimization
- Use TA-Lib (C implementation) for performance-critical calculations
- Cache results for frequently accessed data
- Implement batch processing for multiple symbols

### Vietnam Market Specifics
- Custom indicators for Vietnam market characteristics
- Sector rotation analysis for Vietnam market
- Volume spike detection for illiquid stocks

---

## 📚 REFERENCE MATERIALS

### TA-Lib Documentation
- [TA-Lib Documentation](https://mrjbq7.github.io/ta-lib/)
- [TA-Lib Function Reference](https://github.com/mrjbq7/ta-lib/blob/master/docs/func.md)

### Existing Code References
- `PROCESSORS/technical/indicators/technical_processor.py` (current implementation)
- `WEBAPP/services/llm_service.py` (AI integration)
- `PROCESSORS/core/shared/unified_mapper.py` (sector mapping)

---

## 🎯 NEXT STEPS

1. **Review and approve** this master plan
2. **Begin Phase 1** implementation with TA-Lib formulas
3. **Create sample data** for testing
4. **Set up development environment** with required dependencies
5. **Test incrementally** with each phase completion

---

*This master plan provides a comprehensive roadmap for integrating TA-Lib with the existing architecture while maintaining consistency and enabling powerful technical analysis capabilities.*

