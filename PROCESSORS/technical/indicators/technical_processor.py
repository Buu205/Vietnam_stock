import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Optional
import warnings
import sys
import os

# Import TA-Lib for optimized technical indicators (REQUIRED)
try:
    import talib
except ImportError:
    raise ImportError(
        "TA-Lib is required for technical indicators. "
        "Install with: brew install ta-lib && pip install TA-Lib"
    )

# Robust path setup to import DateFormatter from PROCESSORS/core or WEBAPP/core
# Find project root by checking for DATA and DATA/processed directories
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT_PATH = None

# Try to find project root by checking for markers (data_warehouse and calculated_results)
for parent in [CURRENT_DIR] + list(CURRENT_DIR.parents):
    if (parent / "DATA").exists() and (parent / "DATA/processed").exists():
        PROJECT_ROOT_PATH = parent
        break

# Fallback: if not found, calculate from current dir (5 levels up)
if PROJECT_ROOT_PATH is None:
    PROJECT_ROOT_PATH = CURRENT_DIR.parent.parent.parent.parent.parent

# Debug: print PROJECT_ROOT_PATH to verify it's correct
import logging
_logger = logging.getLogger(__name__)
_logger.info(f"technical_processor.py: PROJECT_ROOT_PATH = {PROJECT_ROOT_PATH}")

PROJECT_ROOT = str(PROJECT_ROOT_PATH)
CORE_DIR_DP = str(CURRENT_DIR.parent.parent.parent / "core")  # data_processor/core
if PROJECT_ROOT not in sys.path:
if CORE_DIR_DP not in sys.path:

from PROCESSORS.core.shared.date_formatter import DateFormatter
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TechnicalProcessor:
    def __init__(self, ohlcv_path: str = None, output_dir: str = None):
        # Calculate default paths if not provided
        if ohlcv_path is None:
            ohlcv_path = str(PROJECT_ROOT_PATH / "DATA" / "raw" / "ohlcv" / "OHLCV_mktcap.parquet")
        if output_dir is None:
            output_dir = str(PROJECT_ROOT_PATH / "DATA" / "processed" / "technical")
        
        self.ohlcv_path = ohlcv_path
        self.output_dir = Path(output_dir)
        
        # Debug: Print to stderr to see what's happening
        import sys
        print(f"DEBUG TechnicalProcessor.__init__:", file=sys.stderr)
        print(f"  PROJECT_ROOT_PATH: {PROJECT_ROOT_PATH}", file=sys.stderr)
        print(f"  OHLCV path: {self.ohlcv_path}", file=sys.stderr)
        print(f"  Output dir: {self.output_dir}", file=sys.stderr)
        
        # Validate paths don't contain old hardcoded path
        if '/Users/buu_os' in self.ohlcv_path or '/Users/buu_os' in str(self.output_dir):
            error_msg = (
                f"Found old hardcoded path '/Users/buu_os' in paths! "
                f"OHLCV: {self.ohlcv_path}, Output: {self.output_dir}. "
                f"PROJECT_ROOT_PATH was: {PROJECT_ROOT_PATH}"
            )
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise ValueError(error_msg)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.date_formatter = DateFormatter()
        
        # List of indicators to process
        self.indicators = [
            'basic_data', 'moving_averages', 'exponential_moving_averages', 
            'rsi', 'macd', 'bollinger_bands', 'volatility', 'trading_values', 
            'signals', 'sector_trading', 'market_breadth', 'sector_rotation'
        ]
        
        # Methods mapping
        self.indicators_methods = {
            'basic_data': self.calculate_basic_data,
            'moving_averages': self.calculate_moving_averages,
            'exponential_moving_averages': self.calculate_exponential_moving_averages,
            'rsi': self.calculate_rsi,
            'macd': self.calculate_macd,
            'bollinger_bands': self.calculate_bollinger_bands,
            'volatility': self.calculate_volatility,
            'trading_values': self.calculate_trading_values,
            'signals': self.calculate_signals,
            'sector_trading': self.calculate_sector_trading,
            'market_breadth': self.calculate_market_breadth,
            'sector_rotation': self.calculate_sector_rotation
        }
    
    def load_ohlcv_data(self) -> pd.DataFrame:
        """Load OHLCV data from parquet file."""
        try:
            df = pd.read_parquet(self.ohlcv_path)
            
            # Chuẩn hóa dữ liệu - đảm bảo date chỉ là date object
            df['date'] = pd.to_datetime(df['date']).dt.date  # Chỉ giữ ngày tháng năm
            df['symbol'] = df['symbol'].str.upper().str.strip()
            
            logger.info(f"Loaded {len(df)} records for {df['symbol'].nunique()} symbols")
            return df
        except Exception as e:
            logger.error(f"Error loading OHLCV data: {e}")
            raise
    
    def calculate_basic_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate basic technical data."""
        logger.info("Calculating Basic Data...")
        result = df.copy()
        
        # Price changes
        result['price_change'] = result['close'] - result['open']
        result['price_change_pct'] = (result['close'] - result['open']) / result['open'] * 100
        
        # High-Low range
        result['hl_range'] = result['high'] - result['low']
        result['hl_range_pct'] = result['hl_range'] / result['low'] * 100
        
        # Volume analysis
        result['volume_ma5'] = result.groupby('symbol')['volume'].rolling(window=5, min_periods=1).mean().reset_index(0, drop=True)
        result['volume_ma20'] = result.groupby('symbol')['volume'].rolling(window=20, min_periods=1).mean().reset_index(0, drop=True)
        result['volume_ratio'] = result['volume'] / result['volume_ma20']
        
        return result
    
    def calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages with MA20 x MA50 crossover detection - OPTIMIZED with TA-Lib."""
        logger.info("Calculating Moving Averages with MA20 x MA50 crossover signals...")
        result = df.copy()
        
        ma_periods = [5, 10, 20, 50, 100, 200]
        
        def calculate_ma_group(group):
            """Calculate all MAs for one symbol using TA-Lib."""
            close_values = group['close'].values.astype(np.float64)
            
            for period in ma_periods:
                # TA-Lib SMA - faster and more accurate
                ma_values = talib.SMA(close_values, timeperiod=period)
                group[f'ma{period}'] = ma_values
                group[f'ma{period}_signal'] = np.where(
                    group['close'] > group[f'ma{period}'], 1, 0
                )
            
            return group
        
        # Apply TA-Lib calculation per symbol
        result = result.groupby('symbol', group_keys=False).apply(
            calculate_ma_group
        ).reset_index(drop=True)
        
        # MA 20 x MA 50 Crossover Detection (Mid-term signals)
        logger.info("Calculating MA 20 x MA 50 crossover signals...")
        
        def calculate_ma_crossover(group):
            """Calculate MA crossover signals for each symbol group."""
            group = group.copy()
            
            # Current position: MA20 vs MA50
            group['ma20_above_ma50'] = group['ma20'] > group['ma50']
            
            # Previous position (shifted by 1 period)
            group['ma20_above_ma50_prev'] = group['ma20_above_ma50'].shift(1)
            
            # Golden Cross: MA20 crosses ABOVE MA50 (Mid-term bullish)
            group['ma_golden_cross'] = (
                (group['ma20_above_ma50'] == True) & 
                (group['ma20_above_ma50_prev'] == False)
            )
            
            # Death Cross: MA20 crosses BELOW MA50 (Mid-term bearish)
            group['ma_death_cross'] = (
                (group['ma20_above_ma50'] == False) & 
                (group['ma20_above_ma50_prev'] == True)
            )
            
            # Mid-term trend signal
            # +2: Strong bullish (Golden cross)
            # +1: Bullish (MA20 > MA50, no cross)
            # 0: Neutral or insufficient data
            # -1: Bearish (MA20 < MA50, no cross)
            # -2: Strong bearish (Death cross)
            group['ma_crossover_signal'] = 0
            
            # Set signals
            group.loc[group['ma_golden_cross'], 'ma_crossover_signal'] = 2
            group.loc[group['ma_death_cross'], 'ma_crossover_signal'] = -2
            group.loc[(group['ma20_above_ma50']) & (~group['ma_golden_cross']), 'ma_crossover_signal'] = 1
            group.loc[(~group['ma20_above_ma50']) & (~group['ma_death_cross']), 'ma_crossover_signal'] = -1
            
            # Calculate crossover strength (distance between MAs as %)
            group['ma_crossover_strength'] = np.abs(
                (group['ma20'] - group['ma50']) / group['ma50'] * 100
            )
            
            # Days since last crossover
            cross_points = group['ma_golden_cross'] | group['ma_death_cross']
            group['days_since_ma_cross'] = 0
            
            if cross_points.any():
                last_cross_idx = group[cross_points].index[-1] if cross_points.any() else None
                if last_cross_idx is not None:
                    for i, idx in enumerate(group.index):
                        if idx >= last_cross_idx:
                            group.loc[idx, 'days_since_ma_cross'] = i - group.index.get_loc(last_cross_idx)
                        else:
                            group.loc[idx, 'days_since_ma_cross'] = np.nan
            
            # Clean up temporary columns
            group = group.drop(['ma20_above_ma50', 'ma20_above_ma50_prev'], axis=1)
            
            return group
        
        # Apply crossover calculation to each symbol
        result = result.groupby('symbol', group_keys=False).apply(calculate_ma_crossover).reset_index(drop=True)
        
        # Add summary statistics
        golden_crosses = result['ma_golden_cross'].sum()
        death_crosses = result['ma_death_cross'].sum()
        
        logger.info(f"MA Crossover Analysis Complete:")
        logger.info(f"- Golden Crosses (MA20 > MA50): {golden_crosses}")
        logger.info(f"- Death Crosses (MA20 < MA50): {death_crosses}")
        logger.info(f"- Average crossover strength: {result['ma_crossover_strength'].mean():.2f}%")
        
        return result
    
    def calculate_exponential_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate exponential moving averages with crossover detection."""
        logger.info("Calculating Exponential Moving Averages (EMA 9, 21, 50) with crossover signals...")
        result = df.copy()
        
        for period in [9, 21, 50]:
            result[f'ema{period}'] = result.groupby('symbol')['close'].ewm(span=period, min_periods=1).mean().reset_index(0, drop=True)
            result[f'ema{period}_signal'] = np.where(result['close'] > result[f'ema{period}'], 1, 0)
        
        # EMA 9 x EMA 21 Crossover Detection
        logger.info("Calculating EMA 9 x EMA 21 crossover signals...")
        
        def calculate_ema_crossover(group):
            """Calculate EMA crossover signals for each symbol group."""
            group = group.copy()
            
            # Current position: EMA9 vs EMA21
            group['ema9_above_ema21'] = group['ema9'] > group['ema21']
            
            # Previous position (shifted by 1 period)
            group['ema9_above_ema21_prev'] = group['ema9_above_ema21'].shift(1)
            
            # Golden Cross: EMA9 crosses ABOVE EMA21
            group['ema_golden_cross'] = (
                (group['ema9_above_ema21'] == True) & 
                (group['ema9_above_ema21_prev'] == False)
            )
            
            # Death Cross: EMA9 crosses BELOW EMA21  
            group['ema_death_cross'] = (
                (group['ema9_above_ema21'] == False) & 
                (group['ema9_above_ema21_prev'] == True)
            )
            
            # Combined crossover signal
            # +2: Strong bullish (Golden cross)
            # +1: Bullish (EMA9 > EMA21, no cross)
            # 0: Neutral or insufficient data
            # -1: Bearish (EMA9 < EMA21, no cross) 
            # -2: Strong bearish (Death cross)
            group['ema_crossover_signal'] = 0
            
            # Set signals
            group.loc[group['ema_golden_cross'], 'ema_crossover_signal'] = 2
            group.loc[group['ema_death_cross'], 'ema_crossover_signal'] = -2
            group.loc[(group['ema9_above_ema21']) & (~group['ema_golden_cross']), 'ema_crossover_signal'] = 1
            group.loc[(~group['ema9_above_ema21']) & (~group['ema_death_cross']), 'ema_crossover_signal'] = -1
            
            # Calculate crossover strength (distance between EMAs as %)
            group['ema_crossover_strength'] = np.abs(
                (group['ema9'] - group['ema21']) / group['ema21'] * 100
            )
            
            # Days since last crossover
            cross_points = group['ema_golden_cross'] | group['ema_death_cross']
            group['days_since_ema_cross'] = 0
            
            if cross_points.any():
                last_cross_idx = group[cross_points].index[-1] if cross_points.any() else None
                if last_cross_idx is not None:
                    for i, idx in enumerate(group.index):
                        if idx >= last_cross_idx:
                            group.loc[idx, 'days_since_ema_cross'] = i - group.index.get_loc(last_cross_idx)
                        else:
                            group.loc[idx, 'days_since_ema_cross'] = np.nan
            
            # Clean up temporary columns
            group = group.drop(['ema9_above_ema21', 'ema9_above_ema21_prev'], axis=1)
            
            return group
        
        # Apply crossover calculation to each symbol
        result = result.groupby('symbol', group_keys=False).apply(calculate_ema_crossover).reset_index(drop=True)
        
        # Add summary statistics
        golden_crosses = result['ema_golden_cross'].sum()
        death_crosses = result['ema_death_cross'].sum()
        
        logger.info(f"EMA Crossover Analysis Complete:")
        logger.info(f"- Golden Crosses (EMA9 > EMA21): {golden_crosses}")
        logger.info(f"- Death Crosses (EMA9 < EMA21): {death_crosses}")
        logger.info(f"- Average crossover strength: {result['ema_crossover_strength'].mean():.2f}%")
        
        return result
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate RSI - OPTIMIZED with TA-Lib."""
        logger.info(f"Calculating RSI with period {period}...")
        result = df.copy()
        
        rsi_results = []
        for symbol in result['symbol'].unique():
            symbol_data = result[result['symbol'] == symbol].copy().sort_values('date')
            close_values = symbol_data['close'].values.astype(np.float64)
            rsi_values = talib.RSI(close_values, timeperiod=period)
            symbol_data['rsi'] = rsi_values
            rsi_results.append(symbol_data)
        
        result = pd.concat(rsi_results, ignore_index=True)
        result['rsi_signal'] = np.where(result['rsi'] > 70, -1, np.where(result['rsi'] < 30, 1, 0))
        return result
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Calculate MACD - OPTIMIZED with TA-Lib."""
        logger.info(f"Calculating MACD with fast={fast}, slow={slow}, signal={signal}...")
        result = df.copy()
        
        macd_results = []
        for symbol in result['symbol'].unique():
            symbol_data = result[result['symbol'] == symbol].copy().sort_values('date')
            close_values = symbol_data['close'].values.astype(np.float64)
            
            # TA-Lib MACD trả về 3 arrays: macd, signal, histogram
            macd_line, signal_line, histogram = talib.MACD(
                close_values,
                fastperiod=fast,
                slowperiod=slow,
                signalperiod=signal
            )
            
            symbol_data['macd'] = macd_line / 1000  # Normalize for Vietnam market
            symbol_data['macd_signal'] = signal_line / 1000
            symbol_data['macd_histogram'] = histogram / 1000
            
            macd_results.append(symbol_data)
        
        result = pd.concat(macd_results, ignore_index=True)
        return result
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2) -> pd.DataFrame:
        """Calculate Bollinger Bands - OPTIMIZED with TA-Lib."""
        logger.info(f"Calculating Bollinger Bands with period={period}, std_dev={std_dev}...")
        result = df.copy()
        
        def calculate_bb_group(group):
            """Calculate Bollinger Bands for one symbol using TA-Lib."""
            close_values = group['close'].values.astype(np.float64)
            
            # TA-Lib BBANDS trả về 3 arrays: upper, middle, lower
            upper, middle, lower = talib.BBANDS(
                close_values,
                timeperiod=period,
                nbdevup=std_dev,
                nbdevdn=std_dev,
                matype=0  # SMA
            )
            
            group['bb_upper'] = upper
            group['bb_middle'] = middle
            group['bb_lower'] = lower
            group['bb_width'] = (upper - lower) / middle * 100
            group['bb_position'] = (group['close'] - lower) / (upper - lower) * 100
            
            return group
        
        # Apply TA-Lib calculation per symbol
        result = result.groupby('symbol', group_keys=False).apply(
            calculate_bb_group
        ).reset_index(drop=True)
        
        return result
    
    def calculate_volatility(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate volatility using TA-Lib ATR - OPTIMIZED."""
        logger.info(f"Calculating Volatility with period={period}...")
        result = df.copy()
        
        def calculate_volatility_group(group):
            """Calculate volatility using TA-Lib ATR."""
            high_values = group['high'].values.astype(np.float64)
            low_values = group['low'].values.astype(np.float64)
            close_values = group['close'].values.astype(np.float64)
            
            # ATR (Average True Range) - better volatility measure than std
            atr_values = talib.ATR(
                high_values, low_values, close_values,
                timeperiod=period
            )
            
            # Convert to percentage volatility
            volatility_pct = (atr_values / close_values) * 100
            
            group['volatility'] = volatility_pct
            # Calculate MA of volatility using TA-Lib
            group['volatility_ma'] = talib.SMA(volatility_pct, timeperiod=period)
            
            return group
        
        # Apply TA-Lib calculation per symbol
        result = result.groupby('symbol', group_keys=False).apply(
            calculate_volatility_group
        ).reset_index(drop=True)
        
        return result

    def calculate_trading_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate trading values."""
        logger.info("Calculating Trading Values...")
        result = df.copy()
        
        result['trading_value'] = result['close'] * result['volume']
        result['trading_value_ma5'] = result.groupby('symbol')['trading_value'].rolling(window=5, min_periods=1).mean().reset_index(0, drop=True)
        result['trading_value_ma20'] = result.groupby('symbol')['trading_value'].rolling(window=20, min_periods=1).mean().reset_index(0, drop=True)
        
        return result
    
    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate combined signals including EMA crossover."""
        logger.info("Calculating Combined Signals with EMA crossover...")
        result = df.copy()
        
        # Calculate individual indicators
        result = self.calculate_moving_averages(result)
        result = self.calculate_exponential_moving_averages(result)  # Include EMA with crossover
        result = self.calculate_rsi(result)
        result = self.calculate_macd(result)
        result = self.calculate_bollinger_bands(result)
        
        # Enhanced Combined signal with EMA crossover
        result['combined_signal'] = (
            result['ma20_signal'] +                                                    # MA trend component
            result['rsi_signal'] +                                                     # RSI momentum component
            np.where(result['macd'] > result['macd_signal'], 1, -1) +                # MACD momentum component
            np.where(result['close'] > result['bb_upper'], -1,                       # Bollinger Bands mean reversion
                    np.where(result['close'] < result['bb_lower'], 1, 0)) +
            result['ema_crossover_signal']                                             # EMA crossover component (±2)
        )
        
        # EMA-focused signal (for EMA crossover strategies)
        result['ema_focused_signal'] = (
            result['ema_crossover_signal'] * 2 +                                      # EMA crossover (double weight)
            result['rsi_signal'] +                                                    # RSI confirmation
            np.where(result['macd'] > result['macd_signal'], 1, -1)                  # MACD confirmation
        )
        
        # Trading signals based on EMA crossover
        result['ema_trade_signal'] = 'HOLD'
        
        # Strong Buy: Golden cross + bullish momentum
        result.loc[
            (result['ema_golden_cross']) & 
            (result['rsi'] < 70) & 
            (result['macd'] > result['macd_signal']), 
            'ema_trade_signal'
        ] = 'STRONG_BUY'
        
        # Buy: EMA9 > EMA21 + momentum
        result.loc[
            (result['ema_crossover_signal'] > 0) & 
            (result['rsi'] < 70) & 
            (~result['ema_golden_cross']), 
            'ema_trade_signal'
        ] = 'BUY'
        
        # Strong Sell: Death cross + bearish momentum  
        result.loc[
            (result['ema_death_cross']) & 
            (result['rsi'] > 30) & 
            (result['macd'] < result['macd_signal']), 
            'ema_trade_signal'
        ] = 'STRONG_SELL'
        
        # Sell: EMA9 < EMA21 + momentum
        result.loc[
            (result['ema_crossover_signal'] < 0) & 
            (result['rsi'] > 30) & 
            (~result['ema_death_cross']), 
            'ema_trade_signal'
        ] = 'SELL'
        
        # Log signal statistics
        signal_counts = result['ema_trade_signal'].value_counts()
        logger.info("EMA Trading Signals Distribution:")
        for signal, count in signal_counts.items():
            logger.info(f"- {signal}: {count} instances")
        
        return result

    def calculate_sector_trading(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate sector trading data."""
        logger.info("Calculating Sector Trading...")
        result = df.copy()
        
        # Add sector mapping
        sector_mapping = {
            'VCB': 'Ngân hàng', 'TCB': 'Ngân hàng', 'BID': 'Ngân hàng', 'CTG': 'Ngân hàng', 'MBB': 'Ngân hàng',
            'VIC': 'Bất động sản', 'VHM': 'Bất động sản', 'KDH': 'Bất động sản', 'NVL': 'Bất động sản',
            'VNM': 'Tiêu dùng', 'MSN': 'Tiêu dùng', 'MWG': 'Tiêu dùng', 'PNJ': 'Tiêu dùng',
            'GAS': 'Năng lượng', 'PLX': 'Năng lượng', 'POW': 'Năng lượng', 'GEG': 'Năng lượng',
            'HPG': 'Thép', 'HSG': 'Thép', 'NKG': 'Thép', 'SMC': 'Thép',
            'FPT': 'Công nghệ', 'CMG': 'Công nghệ', 'ELC': 'Công nghệ', 'ITD': 'Công nghệ'
        }
        
        result['sector'] = result['symbol'].map(sector_mapping).fillna('Khác')
        result['trading_value'] = result['close'] * result['volume']
        
        return result

    def calculate_market_breadth(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate market breadth."""
        logger.info("Calculating Market Breadth...")
        
        # Calculate MA20 and MA50 for all stocks
        df_with_ma = df.copy()
        df_with_ma['ma20'] = df_with_ma.groupby('symbol')['close'].rolling(window=20, min_periods=1).mean().reset_index(0, drop=True)
        df_with_ma['ma50'] = df_with_ma.groupby('symbol')['close'].rolling(window=50, min_periods=1).mean().reset_index(0, drop=True)
        df_with_ma['ma100'] = df_with_ma.groupby('symbol')['close'].rolling(window=100, min_periods=1).mean().reset_index(0, drop=True)
        
        # Calculate breadth by date
        breadth_data = []
        for date in sorted(df_with_ma['date'].unique()):
            date_data = df_with_ma[df_with_ma['date'] == date]
            
            total_stocks = len(date_data)
            above_ma20 = len(date_data[date_data['close'] > date_data['ma20']])
            above_ma50 = len(date_data[date_data['close'] > date_data['ma50']])
            above_ma100 = len(date_data[date_data['close'] > date_data['ma100']])
            
            breadth_data.append({
                'date': date,
                'total_stocks': total_stocks,
                'above_ma20': above_ma20,
                'above_ma50': above_ma50,
                'above_ma100': above_ma100,
                'ma20_breadth_ratio': above_ma20 / total_stocks if total_stocks > 0 else 0,
                'ma50_breadth_ratio': above_ma50 / total_stocks if total_stocks > 0 else 0,
                'ma100_breadth_ratio': above_ma100 / total_stocks if total_stocks > 0 else 0
            })
        
        result = pd.DataFrame(breadth_data)
        
        # Calculate moving averages
        result['ma20_breadth_ma5'] = result['ma20_breadth_ratio'].rolling(window=5).mean()
        result['ma20_breadth_ma20'] = result['ma20_breadth_ratio'].rolling(window=20).mean()
        result['ma50_breadth_ma5'] = result['ma50_breadth_ratio'].rolling(window=5).mean()
        result['ma50_breadth_ma20'] = result['ma50_breadth_ratio'].rolling(window=20).mean()
        result['ma100_breadth_ma5'] = result['ma100_breadth_ratio'].rolling(window=5).mean()
        result['ma100_breadth_ma20'] = result['ma100_breadth_ratio'].rolling(window=20).mean()
        
        # Breadth signal
        result['breadth_signal'] = 'NEUTRAL'
        result.loc[result['ma20_breadth_ratio'] >= 0.8, 'breadth_signal'] = 'STRONG_BULL'
        result.loc[(result['ma20_breadth_ratio'] >= 0.6) & (result['ma20_breadth_ratio'] < 0.8), 'breadth_signal'] = 'BULL'
        result.loc[(result['ma20_breadth_ratio'] <= 0.2) & (result['ma20_breadth_ratio'] > 0), 'breadth_signal'] = 'BEAR'
        result.loc[result['ma20_breadth_ratio'] <= 0.2, 'breadth_signal'] = 'STRONG_BEAR'
        
        # Add symbol column for compatibility
        result['symbol'] = 'MARKET'
        result['ticker'] = 'MARKET'
        
        return result

    def calculate_sector_rotation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate sector rotation with T+2.5 and Market Cap analysis."""
        logger.info("Calculating Sector Rotation Analysis...")
        
        # Load sector mapping
        try:
            tickers_path = Path(PROJECT_ROOT) / "DATA" / "raw" / "metadata" / "all_tickers.csv"
            tickers_df = pd.read_csv(tickers_path)
            sector_mapping = dict(zip(tickers_df['symbol'], tickers_df['sector']))
        except:
            sector_mapping = {
                'VCB': 'Ngân hàng', 'TCB': 'Ngân hàng', 'BID': 'Ngân hàng', 'CTG': 'Ngân hàng', 'MBB': 'Ngân hàng',
                'VIC': 'Bất động sản', 'VHM': 'Bất động sản', 'KDH': 'Bất động sản', 'NVL': 'Bất động sản',
                'VNM': 'Tiêu dùng', 'MSN': 'Tiêu dùng', 'MWG': 'Tiêu dùng', 'PNJ': 'Tiêu dùng',
                'GAS': 'Năng lượng', 'PLX': 'Năng lượng', 'POW': 'Năng lượng', 'GEG': 'Năng lượng',
                'HPG': 'Thép', 'HSG': 'Thép', 'NKG': 'Thép', 'SMC': 'Thép',
                'FPT': 'Công nghệ', 'CMG': 'Công nghệ', 'ELC': 'Công nghệ', 'ITD': 'Công nghệ'
            }
        
        # Add sector column
        df_with_sector = df.copy()
        df_with_sector['sector'] = df_with_sector['symbol'].map(sector_mapping).fillna('Khác')
        df_with_sector['trading_value'] = df_with_sector['close'] * df_with_sector['volume']
        
        # Calculate sector rotation by date
        sector_rotation = []
        for date in sorted(df_with_sector['date'].unique()):
            date_data = df_with_sector[df_with_sector['date'] == date].copy()
            
            # Calculate trading value and market cap by sector
            sector_trading = date_data.groupby('sector').agg({
                'trading_value': 'sum',
                'volume': 'sum',
                'market_cap': 'sum',
                'symbol': 'count'
            }).reset_index()
            
            sector_trading.columns = ['sector', 'total_trading_value', 'total_volume', 'total_market_cap', 'stock_count']
            sector_trading['date'] = date
            
            # Calculate percentages
            total_market_value = sector_trading['total_trading_value'].sum()
            sector_trading['pct_trading_value'] = (sector_trading['total_trading_value'] / total_market_value * 100) if total_market_value > 0 else 0
            
            total_market_cap = sector_trading['total_market_cap'].sum()
            sector_trading['pct_market_cap'] = (sector_trading['total_market_cap'] / total_market_cap * 100) if total_market_cap > 0 else 0
            
            sector_rotation.append(sector_trading)
        
        result = pd.concat(sector_rotation, ignore_index=True)
        
        # Calculate performance metrics (T+2.5 adjusted)
        if not result.empty:
            result = result.sort_values(['sector', 'date']).reset_index(drop=True)
            
            for sector in result['sector'].unique():
                sector_mask = result['sector'] == sector
                sector_data = result[sector_mask].copy()
                
                # Trading Value Performance - Period over Period (PoP) comparison
                result.loc[sector_mask, 'trading_value_3d_pct'] = sector_data['total_trading_value'].pct_change(periods=3) * 100
                result.loc[sector_mask, 'trading_value_1_5w_pct'] = sector_data['total_trading_value'].pct_change(periods=7) * 100
                result.loc[sector_mask, 'trading_value_3w_pct'] = sector_data['total_trading_value'].pct_change(periods=15) * 100
                result.loc[sector_mask, 'trading_value_1m_pct'] = sector_data['total_trading_value'].pct_change(periods=20) * 100
                result.loc[sector_mask, 'trading_value_1_5m_pct'] = sector_data['total_trading_value'].pct_change(periods=30) * 100
                
                # Market Cap Performance - Period over Period (PoP) comparison
                result.loc[sector_mask, 'market_cap_3d_pct'] = sector_data['total_market_cap'].pct_change(periods=3) * 100
                result.loc[sector_mask, 'market_cap_1_5w_pct'] = sector_data['total_market_cap'].pct_change(periods=7) * 100
                result.loc[sector_mask, 'market_cap_3w_pct'] = sector_data['total_market_cap'].pct_change(periods=15) * 100
                result.loc[sector_mask, 'market_cap_1m_pct'] = sector_data['total_market_cap'].pct_change(periods=20) * 100
                result.loc[sector_mask, 'market_cap_1_5m_pct'] = sector_data['total_market_cap'].pct_change(periods=30) * 100
                
                # Note: Using Period-over-Period comparison, no rolling averages needed
                
            
            # Ranking
            for period in ['3d', '1_5w', '3w', '1m', '1_5m']:
                col_name = f'trading_value_{period}_pct'
                result[f'{period}_rank'] = result.groupby('date')[col_name].rank(ascending=False, method='dense')
            
            # Rotation Divergence Analysis (after all performance metrics are calculated)
            result['rotation_divergence_3d'] = (
                (result['trading_value_3d_pct'] > 5) & (result['market_cap_3d_pct'] < 0)
            )
            result['rotation_divergence_1_5w'] = (
                (result['trading_value_1_5w_pct'] > 10) & (result['market_cap_1_5w_pct'] < 0)
            )
            result['rotation_divergence_3w'] = (
                (result['trading_value_3w_pct'] > 15) & (result['market_cap_3w_pct'] < 0)
            )
            
            # Rotation Quality Score
            def calculate_rotation_quality(row):
                score = 0
                if not pd.isna(row['trading_value_3d_pct']) and not pd.isna(row['market_cap_3d_pct']):
                    if row['trading_value_3d_pct'] > 0 and row['market_cap_3d_pct'] > 0:
                        score += 25
                    elif row['trading_value_3d_pct'] > 0 and row['market_cap_3d_pct'] < 0:
                        score += 5
                    elif row['trading_value_3d_pct'] < 0 and row['market_cap_3d_pct'] > 0:
                        score += 15
                
                if not pd.isna(row['trading_value_1_5w_pct']) and not pd.isna(row['market_cap_1_5w_pct']):
                    if row['trading_value_1_5w_pct'] > 0 and row['market_cap_1_5w_pct'] > 0:
                        score += 35
                    elif row['trading_value_1_5w_pct'] > 0 and row['market_cap_1_5w_pct'] < 0:
                        score += 10
                    elif row['trading_value_1_5w_pct'] < 0 and row['market_cap_1_5w_pct'] > 0:
                        score += 20
                
                if not pd.isna(row['trading_value_1m_pct']) and not pd.isna(row['market_cap_1m_pct']):
                    if row['trading_value_1m_pct'] > 0 and row['market_cap_1m_pct'] > 0:
                        score += 40
                    elif row['trading_value_1m_pct'] > 0 and row['market_cap_1m_pct'] < 0:
                        score += 15
                    elif row['trading_value_1m_pct'] < 0 and row['market_cap_1m_pct'] > 0:
                        score += 25
                
                return min(score, 100)
            
            result['rotation_quality_score'] = result.apply(calculate_rotation_quality, axis=1)
            
            # Small cap rotation analysis
            result['small_cap_rotation'] = (
                (result['pct_trading_value'] < 5) & 
                (result['trading_value_1_5w_pct'] > 10) & 
                (result['trading_value_1m_pct'] > 10)
            )
            
            # Rotation Pattern Classification
            def classify_rotation(row):
                if pd.isna(row['trading_value_3d_pct']) or pd.isna(row['trading_value_1_5w_pct']) or pd.isna(row['trading_value_1m_pct']):
                    return 'UNKNOWN'
                
                quality_score = row.get('rotation_quality_score', 0)
                
                if (row['trading_value_3d_pct'] > 0 and 
                    row['trading_value_1_5w_pct'] > 0 and 
                    row['trading_value_1m_pct'] > 0 and
                    quality_score >= 70):
                    return 'LEADER_ROTATION'
                elif (row['trading_value_3d_pct'] > 5 and 
                      row['trading_value_1_5w_pct'] > 0 and 
                      quality_score < 40):
                    return 'FAKE_ROTATION'
                elif (row['trading_value_3d_pct'] > 8 and 
                      row['trading_value_1_5w_pct'] < 0 and 
                      row['trading_value_1m_pct'] < 0):
                    return 'SHORT_TERM_SPIKE'
                elif (row['trading_value_3d_pct'] < 0 and 
                      row['trading_value_1_5w_pct'] < 0 and 
                      row['trading_value_1m_pct'] < 0):
                    return 'LAGGING_OUTFLOW'
                else:
                    return 'MIXED_SIGNALS'
            
            result['rotation_pattern'] = result.apply(classify_rotation, axis=1)
            
            # Percentile Label
            def calculate_percentile_label(group):
                p80 = group['trading_value_1_5w_pct'].quantile(0.8)
                p20 = group['trading_value_1_5w_pct'].quantile(0.2)
                
                def label_percentile(row):
                    if pd.isna(row['trading_value_1_5w_pct']):
                        return 'UNKNOWN'
                    elif row['trading_value_1_5w_pct'] >= p80:
                        return 'HOT'
                    elif row['trading_value_1_5w_pct'] <= p20:
                        return 'COLD'
                    else:
                        return 'NEUTRAL'
                
                return group.apply(label_percentile, axis=1)
            
            result['percentile_label'] = result.groupby('date').apply(calculate_percentile_label).reset_index(level=0, drop=True)
            
            # Rotation Strength Score
            def calculate_rotation_strength(row):
                score = 0
                if not pd.isna(row['trading_value_3d_pct']):
                    score += min(abs(row['trading_value_3d_pct']) * 0.35, 35)
                if not pd.isna(row['trading_value_1_5w_pct']):
                    score += min(abs(row['trading_value_1_5w_pct']) * 0.4, 40)
                if not pd.isna(row['trading_value_1m_pct']):
                    score += min(abs(row['trading_value_1m_pct']) * 0.25, 25)
                return min(score, 100)
            
            result['rotation_strength'] = result.apply(calculate_rotation_strength, axis=1)
            
            # Market Cap Weighted Performance
            result['weighted_3d'] = result['trading_value_3d_pct'] * (result['pct_trading_value'] / 100)
            result['weighted_1_5w'] = result['trading_value_1_5w_pct'] * (result['pct_trading_value'] / 100)
            result['weighted_3w'] = result['trading_value_3w_pct'] * (result['pct_trading_value'] / 100)
            result['weighted_1m'] = result['trading_value_1m_pct'] * (result['pct_trading_value'] / 100)
            
            # Rotation Momentum
            result['rotation_momentum'] = (
                result['trading_value_3d_pct'] * 0.3 + 
                result['trading_value_1_5w_pct'] * 0.4 + 
                result['trading_value_3w_pct'] * 0.2 +
                result['trading_value_1m_pct'] * 0.1
            )
            
            # Sector Health Score
            def calculate_health_score(row):
                consistency = 0
                if not pd.isna(row['trading_value_3d_pct']) and not pd.isna(row['trading_value_1_5w_pct']):
                    if (row['trading_value_3d_pct'] > 0) == (row['trading_value_1_5w_pct'] > 0):
                        consistency += 25
                if not pd.isna(row['trading_value_1_5w_pct']) and not pd.isna(row['trading_value_1m_pct']):
                    if (row['trading_value_1_5w_pct'] > 0) == (row['trading_value_1m_pct'] > 0):
                        consistency += 25
                if row['pct_trading_value'] > 5:
                    consistency += 25
                elif row['pct_trading_value'] > 1:
                    consistency += 15
                else:
                    consistency += 5
                if row['rotation_strength'] > 50:
                    consistency += 25
                elif row['rotation_strength'] > 25:
                    consistency += 15
                else:
                    consistency += 5
                return min(consistency, 100)
            
            result['sector_health_score'] = result.apply(calculate_health_score, axis=1)
        
        # Add symbol column for compatibility
        result['symbol'] = 'SECTOR_ROTATION'
        result['ticker'] = 'SECTOR_ROTATION'
        
        return result
    
    def save_indicator_data(self, data: pd.DataFrame, indicator_name: str) -> None:
        """Save indicator data to parquet files."""
        try:
            # Chuẩn hóa date format trước khi lưu
            logger.info(f"Standardizing date format for {indicator_name}...")
            data = self.date_formatter.standardize_all_date_columns(data.copy())
            
            # Save full data
            full_path = self.output_dir / indicator_name / f"{indicator_name}_full.parquet"
            full_path.parent.mkdir(parents=True, exist_ok=True)
            data.to_parquet(full_path, index=False)
            
            # Create summary data
            if 'symbol' in data.columns:
                summary_data = data.groupby('symbol').last().reset_index()
            else:
                summary_data = data.tail(1)
            
            summary_path = self.output_dir / indicator_name / f"{indicator_name}_summary.parquet"
            summary_data.to_parquet(summary_path, index=False)
            
            logger.info(f"Saved {indicator_name}: {len(data)} records (full), {len(summary_data)} records (summary)")
            logger.info(f"Date format sample: {data.columns[data.columns.str.contains('date', case=False)].tolist()}")
            
        except Exception as e:
            logger.error(f"Error saving {indicator_name}: {e}")
            raise
    
    def process_all_indicators(self) -> None:
        """Process all technical indicators."""
        logger.info("Starting technical indicators processing...")
        
        # Load OHLCV data
        ohlcv_data = self.load_ohlcv_data()
        
        # Process each indicator
        for indicator_name in self.indicators:
            try:
                logger.info(f"Processing {indicator_name}...")
                method = self.indicators_methods[indicator_name]
                result = method(ohlcv_data)
                self.save_indicator_data(result, indicator_name)
            except Exception as e:
                logger.error(f"Error processing {indicator_name}: {e}")
                continue
        
        # Create combined technical indicators file
        try:
            logger.info("Creating combined technical indicators file...")
            combined_data = ohlcv_data.copy()
            combined_data.to_parquet(self.output_dir / "technical_indicators_full.parquet", index=False)
            logger.info(f"Saved combined technical indicators: {len(combined_data)} records")
        except Exception as e:
            logger.error(f"Error creating combined file: {e}")
        
        logger.info("Technical indicators processing completed!")
    
if __name__ == "__main__":
    processor = TechnicalProcessor()
    processor.process_all_indicators()
