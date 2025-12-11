#!/usr/bin/env python3
"""
Historical Technical Analysis Processor - Optimized Version
===========================================================

Tạo database lịch sử cho tất cả technical indicators từ 2018 đến nay
với tối ưu hóa performance và memory management.

Dựa trên phương pháp từ historical_pb_calculator.py:
- Batch processing
- Memory optimization  
- Vectorized calculations
- Progressive data loading
- Efficient data structures

Author: AI Assistant
Date: 2025-01-27
"""

import pandas as pd
import numpy as np
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
import gc
import shutil

# Optional imports
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    def tqdm(iterable, **kwargs):
        return iterable

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

warnings.filterwarnings('ignore')

# Add core module to path for date formatter (tương tự các module khác trong dự án)
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", ".."))
CORE_DIR_DP = os.path.join(PROJECT_ROOT, "data_processor", "core")
if CORE_DIR_DP not in sys.path:

from PROCESSORS.core.shared.date_formatter import DateFormatter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HistoricalTechnicalProcessor:
    """
    Historical Technical Analysis Processor với optimization
    tương tự historical_pb_calculator.py
    """
    
    def __init__(self):
        """Initialize processor với paths và configurations."""
        # Dùng PROJECT_ROOT đã resolve ở trên làm gốc thay vì dừng ở data_processor
        # để tránh path kiểu .../data_processor/data_warehouse/...
        self.base_path = Path(PROJECT_ROOT)
        self.ohlcv_path = self.base_path / 'DATA' / 'raw' / 'ohlcv' / 'OHLCV_mktcap.parquet'
        self.output_base = self.base_path / 'DATA' / 'processed' / 'technical'
        
        # Date formatter
        self.date_formatter = DateFormatter()
        
        # Data containers for optimization
        self.ohlcv_data = None
        self.symbol_list = None
        self.date_range = None
        
        # Performance tracking
        self.start_time = None
        self.memory_usage = {}
        
        # Processing configuration
        self.batch_size = 50  # symbols per batch
        self.chunk_size = 10000  # rows per chunk
        
        # Indicators to process
        self.indicators = {
            'basic_data': {
                'description': 'OHLCV + Volume analysis',
                'columns': ['open', 'high', 'low', 'close', 'volume', 'market_cap', 'shares_outstanding',
                          'volume_ma20', 'volume_ratio', 'trading_value']
            },
            'moving_averages': {
                'description': 'MA 5,10,20,50,100,200 + crossovers',
                'columns': ['ma5', 'ma10', 'ma20', 'ma50', 'ma100', 'ma200',
                          'ma5_signal', 'ma10_signal', 'ma20_signal', 'ma50_signal', 'ma100_signal', 'ma200_signal',
                          'ma_golden_cross', 'ma_death_cross', 'ma_crossover_signal', 'ma_crossover_strength', 'days_since_ma_cross']
            },
            'exponential_moving_averages': {
                'description': 'EMA 9,21,50 + crossovers',
                'columns': ['ema9', 'ema21', 'ema50',
                          'ema9_signal', 'ema21_signal', 'ema50_signal',
                          'ema_golden_cross', 'ema_death_cross', 'ema_crossover_signal', 'ema_crossover_strength', 'days_since_ema_cross']
            },
            'rsi': {
                'description': 'RSI 14-period với Wilder smoothing',
                'columns': ['rsi', 'rsi_signal']
            },
            'macd': {
                'description': 'MACD 12-26-9',
                'columns': ['macd', 'macd_signal', 'macd_histogram']
            },
            'bollinger_bands': {
                'description': 'Bollinger Bands 20-period, 2 std',
                'columns': ['bb_middle', 'bb_upper', 'bb_lower', 'bb_width', 'bb_position']
            },
            'volatility': {
                'description': 'Volatility analysis',
                'columns': ['volatility', 'volatility_ma']
            },
            'trading_values': {
                'description': 'Trading value analysis',
                'columns': ['trading_value', 'trading_value_ma5', 'trading_value_ma20']
            }
        }
        
    def _log_memory_usage(self, stage: str):
        """Log memory usage for optimization tracking."""
        if HAS_PSUTIL:
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.memory_usage[stage] = memory_mb
            logger.info(f"Memory usage at {stage}: {memory_mb:.1f} MB")
        
    def load_and_preprocess_data(self, start_date: str = '2018-01-01', end_date: str = None):
        """
        Load và preprocess OHLCV data với optimization.
        Tương tự _preprocess_data() trong historical_pb_calculator.py
        """
        logger.info("🚀 Loading and preprocessing OHLCV data...")
        self._log_memory_usage("start")
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # Load OHLCV data
        logger.info(f"   Loading OHLCV from {self.ohlcv_path}")
        self.ohlcv_data = pd.read_parquet(self.ohlcv_path)
        self._log_memory_usage("after_load")
        
        # Filter date range
        logger.info(f"   Filtering date range: {start_date} to {end_date}")
        
        # Convert date strings to datetime for comparison
        start_dt = pd.to_datetime(start_date).date() if isinstance(start_date, str) else start_date
        end_dt = pd.to_datetime(end_date).date() if isinstance(end_date, str) else end_date
        
        # Convert date column to datetime.date if it's string
        if self.ohlcv_data['date'].dtype == 'object':
            self.ohlcv_data['date'] = pd.to_datetime(self.ohlcv_data['date']).dt.date
        
        date_mask = (
            (self.ohlcv_data['date'] >= start_dt) & 
            (self.ohlcv_data['date'] <= end_dt)
        )
        self.ohlcv_data = self.ohlcv_data[date_mask].copy()
        
        # Basic data quality filters
        logger.info("   Applying data quality filters...")
        quality_mask = (
            (self.ohlcv_data['close'] > 0) &
            (self.ohlcv_data['volume'] >= 0) &
            (self.ohlcv_data['high'] >= self.ohlcv_data['low']) &
            (self.ohlcv_data['high'] >= self.ohlcv_data['close']) &
            (self.ohlcv_data['low'] <= self.ohlcv_data['close'])
        )
        self.ohlcv_data = self.ohlcv_data[quality_mask].copy()
        
        # Sort for optimal processing
        logger.info("   Sorting data for optimal processing...")
        self.ohlcv_data = self.ohlcv_data.sort_values(['symbol', 'date']).reset_index(drop=True)
        
        # Extract symbol list and date range
        self.symbol_list = sorted(self.ohlcv_data['symbol'].unique())
        self.date_range = (
            self.ohlcv_data['date'].min(),
            self.ohlcv_data['date'].max()
        )
        
        logger.info(f"✅ Data preprocessing completed!")
        logger.info(f"   Symbols: {len(self.symbol_list):,}")
        logger.info(f"   Records: {len(self.ohlcv_data):,}")
        logger.info(f"   Date range: {self.date_range[0]} to {self.date_range[1]}")
        
        self._log_memory_usage("after_preprocess")
        
    def _calculate_basic_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate basic technical indicators với vectorized operations."""
        result = df.copy()
        
        # Basic volume analysis
        result['volume_ma20'] = result.groupby('symbol')['volume'].rolling(window=20, min_periods=1).mean().reset_index(0, drop=True)
        result['volume_ratio'] = result['volume'] / result['volume_ma20'].replace(0, np.nan)
        result['trading_value'] = result['close'] * result['volume']
        
        return result
        
    def _calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages với crossover detection."""
        result = df.copy()
        
        # Calculate MAs
        periods = [5, 10, 20, 50, 100, 200]
        for period in periods:
            result[f'ma{period}'] = result.groupby('symbol')['close'].rolling(window=period, min_periods=1).mean().reset_index(0, drop=True)
            result[f'ma{period}_signal'] = np.where(result['close'] > result[f'ma{period}'], 1, 0)
        
        # MA 20 x MA 50 Crossover Detection
        def calculate_ma_crossover(group):
            group = group.copy()
            
            # Current and previous positions
            group['ma20_above_ma50'] = group['ma20'] > group['ma50']
            group['ma20_above_ma50_prev'] = group['ma20_above_ma50'].shift(1)
            
            # Crossover events
            group['ma_golden_cross'] = (
                (group['ma20_above_ma50'] == True) & 
                (group['ma20_above_ma50_prev'] == False)
            )
            group['ma_death_cross'] = (
                (group['ma20_above_ma50'] == False) & 
                (group['ma20_above_ma50_prev'] == True)
            )
            
            # Crossover signals
            group['ma_crossover_signal'] = 0
            group.loc[group['ma_golden_cross'], 'ma_crossover_signal'] = 2
            group.loc[group['ma_death_cross'], 'ma_crossover_signal'] = -2
            group.loc[(group['ma20_above_ma50']) & (~group['ma_golden_cross']), 'ma_crossover_signal'] = 1
            group.loc[(~group['ma20_above_ma50']) & (~group['ma_death_cross']), 'ma_crossover_signal'] = -1
            
            # Crossover strength
            group['ma_crossover_strength'] = np.abs(
                (group['ma20'] - group['ma50']) / group['ma50'] * 100
            )
            
            # Days since crossover
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
        
        # Apply crossover calculation
        result = result.groupby('symbol', group_keys=False).apply(calculate_ma_crossover).reset_index(drop=True)
        
        return result
    
    def _calculate_exponential_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate EMAs với crossover detection."""
        result = df.copy()
        
        # Calculate EMAs
        periods = [9, 21, 50]
        for period in periods:
            result[f'ema{period}'] = result.groupby('symbol')['close'].ewm(span=period, min_periods=1).mean().reset_index(0, drop=True)
            result[f'ema{period}_signal'] = np.where(result['close'] > result[f'ema{period}'], 1, 0)
        
        # EMA 9 x EMA 21 Crossover Detection
        def calculate_ema_crossover(group):
            group = group.copy()
            
            # Current and previous positions
            group['ema9_above_ema21'] = group['ema9'] > group['ema21']
            group['ema9_above_ema21_prev'] = group['ema9_above_ema21'].shift(1)
            
            # Crossover events
            group['ema_golden_cross'] = (
                (group['ema9_above_ema21'] == True) & 
                (group['ema9_above_ema21_prev'] == False)
            )
            group['ema_death_cross'] = (
                (group['ema9_above_ema21'] == False) & 
                (group['ema9_above_ema21_prev'] == True)
            )
            
            # Crossover signals
            group['ema_crossover_signal'] = 0
            group.loc[group['ema_golden_cross'], 'ema_crossover_signal'] = 2
            group.loc[group['ema_death_cross'], 'ema_crossover_signal'] = -2
            group.loc[(group['ema9_above_ema21']) & (~group['ema_golden_cross']), 'ema_crossover_signal'] = 1
            group.loc[(~group['ema9_above_ema21']) & (~group['ema_death_cross']), 'ema_crossover_signal'] = -1
            
            # Crossover strength
            group['ema_crossover_strength'] = np.abs(
                (group['ema9'] - group['ema21']) / group['ema21'] * 100
            )
            
            # Days since crossover
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
        
        # Apply crossover calculation
        result = result.groupby('symbol', group_keys=False).apply(calculate_ema_crossover).reset_index(drop=True)
        
        return result
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate RSI using Wilder's smoothing method."""
        result = df.copy()
        
        def calculate_rsi_group(group):
            delta = group['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            # Wilder's smoothing
            avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
            avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        result['rsi'] = result.groupby('symbol').apply(calculate_rsi_group).reset_index(0, drop=True)
        result['rsi_signal'] = np.where(result['rsi'] > 70, -1, np.where(result['rsi'] < 30, 1, 0))
        
        return result
    
    def _calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Calculate MACD."""
        result = df.copy()
        
        def calculate_macd_group(group):
            ema_fast = group['close'].ewm(span=fast).mean()
            ema_slow = group['close'].ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            
            return pd.DataFrame({
                'macd': macd_line,
                'macd_signal': signal_line,
                'macd_histogram': histogram
            }, index=group.index)
        
        # Calculate MACD for each symbol
        macd_results = []
        for symbol in result['symbol'].unique():
            symbol_data = result[result['symbol'] == symbol].copy()
            if len(symbol_data) > 0:
                macd_result = calculate_macd_group(symbol_data)
                macd_results.append(macd_result)
        
        if macd_results:
            macd_df = pd.concat(macd_results)
            result = result.join(macd_df, how='left')
        
        # Normalize MACD for Vietnam market
        result['macd'] = result['macd'] / 1000
        result['macd_signal'] = result['macd_signal'] / 1000
        result['macd_histogram'] = result['macd_histogram'] / 1000
        
        return result
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2) -> pd.DataFrame:
        """Calculate Bollinger Bands."""
        result = df.copy()
        
        result['bb_middle'] = result.groupby('symbol')['close'].rolling(window=period, min_periods=1).mean().reset_index(0, drop=True)
        bb_std = result.groupby('symbol')['close'].rolling(window=period, min_periods=1).std().reset_index(0, drop=True)
        result['bb_upper'] = result['bb_middle'] + (bb_std * std_dev)
        result['bb_lower'] = result['bb_middle'] - (bb_std * std_dev)
        result['bb_width'] = (result['bb_upper'] - result['bb_lower']) / result['bb_middle'] * 100
        result['bb_position'] = (result['close'] - result['bb_lower']) / (result['bb_upper'] - result['bb_lower']) * 100
        
        return result
    
    def _calculate_volatility(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate volatility."""
        result = df.copy()
        
        result['volatility'] = result.groupby('symbol')['close'].pct_change().rolling(window=period, min_periods=1).std().reset_index(0, drop=True) * 100
        result['volatility_ma'] = result.groupby('symbol')['volatility'].rolling(window=period, min_periods=1).mean().reset_index(0, drop=True)
        
        return result
    
    def _calculate_trading_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate trading values."""
        result = df.copy()
        
        result['trading_value'] = result['close'] * result['volume']
        result['trading_value_ma5'] = result.groupby('symbol')['trading_value'].rolling(window=5, min_periods=1).mean().reset_index(0, drop=True)
        result['trading_value_ma20'] = result.groupby('symbol')['trading_value'].rolling(window=20, min_periods=1).mean().reset_index(0, drop=True)
        
        return result
    
    def _clean_output_directories(self):
        """Xóa các file cũ trong thư mục output."""
        logger.info("🗑️ Cleaning old output files...")
        
        for indicator_name in self.indicators.keys():
            indicator_dir = self.output_base / indicator_name
            if indicator_dir.exists():
                logger.info(f"   Removing old files in {indicator_name}/")
                shutil.rmtree(indicator_dir)
            
            # Recreate directory
            indicator_dir.mkdir(parents=True, exist_ok=True)
        
        # Note: No combined file needed anymore
            
        logger.info("✅ Output directories cleaned!")
    
    def _save_indicator_data(self, data: pd.DataFrame, indicator_name: str):
        """Save indicator data với date formatting (chỉ full data)."""
        try:
            # Standardize date format
            logger.info(f"   Standardizing date format for {indicator_name}...")
            data = self.date_formatter.standardize_all_date_columns(data.copy())
            
            # Create output directory
            output_dir = self.output_base / indicator_name
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save full data only
            full_path = output_dir / f"{indicator_name}_full.parquet"
            data.to_parquet(full_path, index=False)
            
            # Get file size for logging
            file_size_mb = full_path.stat().st_size / (1024 * 1024)
            
            logger.info(f"✅ Saved {indicator_name}: {len(data):,} records, {file_size_mb:.1f}MB")
            
        except Exception as e:
            logger.error(f"❌ Error saving {indicator_name}: {e}")
            raise
    
    def process_indicator_batch(self, symbol_batch: List[str], indicator_name: str) -> pd.DataFrame:
        """Process một batch symbols cho một indicator."""
        
        # Filter data for this batch
        batch_data = self.ohlcv_data[
            self.ohlcv_data['symbol'].isin(symbol_batch)
        ].copy()
        
        if batch_data.empty:
            return pd.DataFrame()
        
        # Calculate indicator based on type
        if indicator_name == 'basic_data':
            result = self._calculate_basic_indicators(batch_data)
        elif indicator_name == 'moving_averages':
            result = self._calculate_moving_averages(batch_data)
        elif indicator_name == 'exponential_moving_averages':
            result = self._calculate_exponential_moving_averages(batch_data)
        elif indicator_name == 'rsi':
            result = self._calculate_rsi(batch_data)
        elif indicator_name == 'macd':
            result = self._calculate_macd(batch_data)
        elif indicator_name == 'bollinger_bands':
            result = self._calculate_bollinger_bands(batch_data)
        elif indicator_name == 'volatility':
            result = self._calculate_volatility(batch_data)
        elif indicator_name == 'trading_values':
            result = self._calculate_trading_values(batch_data)
        else:
            logger.warning(f"Unknown indicator: {indicator_name}")
            return pd.DataFrame()
        
        # Select only relevant columns for this indicator
        base_columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
        indicator_columns = self.indicators[indicator_name]['columns']
        
        # Keep base columns + indicator specific columns (avoid duplicates)
        all_columns = base_columns + [col for col in indicator_columns if col not in base_columns]
        available_columns = [col for col in all_columns if col in result.columns]
        
        # Remove any duplicate columns that might exist
        result = result.loc[:, ~result.columns.duplicated()]
        result = result[available_columns].copy()
        
        return result
    
    def process_all_indicators(self, start_date: str = '2018-01-01', end_date: str = None):
        """
        Process tất cả indicators với batch processing optimization.
        Tương tự logic trong historical_pb_calculator.py
        """
        logger.info("🚀 Starting Historical Technical Analysis Processing...")
        logger.info("=" * 70)
        
        self.start_time = datetime.now()
        
        # Step 1: Load and preprocess data
        self.load_and_preprocess_data(start_date, end_date)
        
        # Step 2: Clean output directories
        self._clean_output_directories()
        
        # Step 3: Create symbol batches for processing
        symbol_batches = [
            self.symbol_list[i:i + self.batch_size] 
            for i in range(0, len(self.symbol_list), self.batch_size)
        ]
        
        logger.info(f"📊 Processing Configuration:")
        logger.info(f"   Total symbols: {len(self.symbol_list):,}")
        logger.info(f"   Symbol batches: {len(symbol_batches)}")
        logger.info(f"   Batch size: {self.batch_size}")
        logger.info(f"   Date range: {self.date_range[0]} to {self.date_range[1]}")
        
        # Step 4: Process each indicator
        for indicator_name, indicator_info in self.indicators.items():
            logger.info(f"\n📈 Processing {indicator_name}...")
            logger.info(f"   Description: {indicator_info['description']}")
            
            all_results = []
            
            # Process each batch
            for batch_idx, symbol_batch in enumerate(tqdm(symbol_batches, desc=f"Processing {indicator_name}")):
                try:
                    batch_result = self.process_indicator_batch(symbol_batch, indicator_name)
                    
                    if not batch_result.empty:
                        all_results.append(batch_result)
                    
                    # Memory management
                    if (batch_idx + 1) % 10 == 0:  # Every 10 batches
                        gc.collect()
                        self._log_memory_usage(f"{indicator_name}_batch_{batch_idx}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing batch {batch_idx} for {indicator_name}: {e}")
                    continue
            
            # Combine all results
            if all_results:
                logger.info(f"   Combining {len(all_results)} batches...")
                combined_result = pd.concat(all_results, ignore_index=True)
                combined_result = combined_result.sort_values(['symbol', 'date']).reset_index(drop=True)
                
                # Save results
                self._save_indicator_data(combined_result, indicator_name)
                
                # Clear memory
                del combined_result, all_results
                gc.collect()
                
            else:
                logger.warning(f"⚠️ No data generated for {indicator_name}")
        
        # Step 5: Final summary
        self._print_final_summary()
        
    
    def _print_final_summary(self):
        """Print final processing summary."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ HISTORICAL TECHNICAL ANALYSIS COMPLETED!")
        logger.info("=" * 70)
        
        logger.info(f"📊 Processing Summary:")
        logger.info(f"   Total symbols processed: {len(self.symbol_list):,}")
        logger.info(f"   Date range: {self.date_range[0]} to {self.date_range[1]}")
        logger.info(f"   Processing duration: {duration}")
        logger.info(f"   Records per symbol (avg): {len(self.ohlcv_data) / len(self.symbol_list):.0f}")
        
        logger.info(f"\n📁 Output Files:")
        total_size = 0
        for indicator_name in self.indicators.keys():
            indicator_dir = self.output_base / indicator_name
            if indicator_dir.exists():
                full_file = indicator_dir / f"{indicator_name}_full.parquet"
                
                if full_file.exists():
                    full_size = full_file.stat().st_size / (1024*1024)
                    total_size += full_size
                    
                    logger.info(f"   {indicator_name}: {full_size:.1f} MB")
        
        logger.info(f"\n💾 Total output size: {total_size:.1f} MB")
        
        if self.memory_usage:
            logger.info(f"\n🧠 Peak memory usage: {max(self.memory_usage.values()):.1f} MB")
        
        logger.info("\n🎯 Next steps:")
        logger.info("   - Use stock_screener.py for daily filtering")
        logger.info("   - Data available in DATA/processed/technical/")
        logger.info("   - Each indicator has full historical data only")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Historical Technical Analysis Processor')
    parser.add_argument('--start-date', type=str, default='2018-01-01',
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default=None,
                       help='End date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--batch-size', type=int, default=50,
                       help='Number of symbols per batch')
    
    args = parser.parse_args()
    
    # Create and run processor
    processor = HistoricalTechnicalProcessor()
    processor.batch_size = args.batch_size
    
    processor.process_all_indicators(
        start_date=args.start_date,
        end_date=args.end_date
    )

if __name__ == '__main__':
    main()
