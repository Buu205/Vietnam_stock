#!/usr/bin/env python3
"""
Technical Indicators Processor with TA-Lib
==========================================

Fast technical analysis using TA-Lib (10-100x faster than pandas).

Author: Claude Code
Date: 2025-12-15
Version: 2.0.0
"""

import pandas as pd
import numpy as np
import talib
from pathlib import Path
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalProcessor:
    """
    Calculate technical indicators using TA-Lib for maximum performance.

    Features:
    - Moving Averages (SMA 20/50/100/200)
    - RSI (14 periods)
    - MACD (12/26/9)
    - Bollinger Bands (20/2)
    - ATR (14 periods)
    - Volume indicators (OBV, CMF, MFI)
    """

    def __init__(self, ohlcv_path: str = "DATA/raw/ohlcv/OHLCV_mktcap.parquet"):
        """
        Initialize processor.

        Args:
            ohlcv_path: Path to OHLCV data file
        """
        self.ohlcv_path = Path(ohlcv_path)
        if not self.ohlcv_path.exists():
            raise FileNotFoundError(f"OHLCV file not found: {self.ohlcv_path}")

        logger.info(f"✅ TechnicalProcessor initialized with OHLCV: {self.ohlcv_path}")

    def load_ohlcv_data(self, n_sessions: int = 200) -> pd.DataFrame:
        """
        Load last N trading sessions for all symbols.

        Args:
            n_sessions: Number of trading sessions to load (default: 200)

        Returns:
            DataFrame with OHLCV data
        """
        logger.info(f"Loading OHLCV data (last {n_sessions} sessions)...")

        df = pd.read_parquet(self.ohlcv_path)

        # Convert date to datetime if needed
        if df['date'].dtype == 'object':
            df['date'] = pd.to_datetime(df['date'])

        # Get last N sessions for each symbol
        result = []
        for symbol in df['symbol'].unique():
            symbol_df = df[df['symbol'] == symbol].copy()
            symbol_df = symbol_df.sort_values('date').tail(n_sessions)
            result.append(symbol_df)

        combined = pd.concat(result, ignore_index=True)

        logger.info(f"✅ Loaded {len(combined):,} records for {combined['symbol'].nunique()} symbols")
        return combined

    def calculate_indicators_for_symbol(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators for a single symbol using TA-Lib.

        Args:
            df: DataFrame with OHLCV data for ONE symbol

        Returns:
            DataFrame with indicators added
        """
        if len(df) < 200:
            logger.warning(f"Not enough data ({len(df)} rows) - need at least 200")
            return df

        df = df.copy()

        # Convert to numpy arrays for TA-Lib
        close = df['close'].values.astype(float)
        high = df['high'].values.astype(float)
        low = df['low'].values.astype(float)
        open_price = df['open'].values.astype(float)
        volume = df['volume'].values.astype(float)

        # === MOVING AVERAGES ===
        df['sma_20'] = talib.SMA(close, timeperiod=20)
        df['sma_50'] = talib.SMA(close, timeperiod=50)
        df['sma_100'] = talib.SMA(close, timeperiod=100)
        df['sma_200'] = talib.SMA(close, timeperiod=200)

        df['ema_20'] = talib.EMA(close, timeperiod=20)
        df['ema_50'] = talib.EMA(close, timeperiod=50)

        # === MOMENTUM INDICATORS ===
        df['rsi_14'] = talib.RSI(close, timeperiod=14)

        macd, macd_signal, macd_hist = talib.MACD(
            close, fastperiod=12, slowperiod=26, signalperiod=9
        )
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        df['macd_hist'] = macd_hist

        slowk, slowd = talib.STOCH(
            high, low, close,
            fastk_period=14, slowk_period=3, slowd_period=3
        )
        df['stoch_k'] = slowk
        df['stoch_d'] = slowd

        # === VOLATILITY INDICATORS ===
        upperband, middleband, lowerband = talib.BBANDS(
            close, timeperiod=20, nbdevup=2, nbdevdn=2
        )
        df['bb_upper'] = upperband
        df['bb_middle'] = middleband
        df['bb_lower'] = lowerband
        df['bb_width'] = (upperband - lowerband) / middleband * 100  # % width

        df['atr_14'] = talib.ATR(high, low, close, timeperiod=14)

        # === VOLUME INDICATORS ===
        df['obv'] = talib.OBV(close, volume)
        df['ad_line'] = talib.AD(high, low, close, volume)
        df['cmf_20'] = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)
        df['mfi_14'] = talib.MFI(high, low, close, volume, timeperiod=14)

        # === TREND INDICATORS ===
        df['adx_14'] = talib.ADX(high, low, close, timeperiod=14)
        df['cci_20'] = talib.CCI(high, low, close, timeperiod=20)

        # === PRICE POSITION RELATIVE TO MA ===
        df['price_vs_sma20'] = ((close - df['sma_20']) / df['sma_20'] * 100)
        df['price_vs_sma50'] = ((close - df['sma_50']) / df['sma_50'] * 100)
        df['price_vs_sma200'] = ((close - df['sma_200']) / df['sma_200'] * 100)

        return df

    def calculate_all_indicators(self, n_sessions: int = 200) -> pd.DataFrame:
        """
        Calculate technical indicators for all symbols.

        Args:
            n_sessions: Number of sessions to process

        Returns:
            DataFrame with all indicators
        """
        logger.info(f"Starting technical indicators calculation for {n_sessions} sessions...")

        # Load OHLCV data
        ohlcv_df = self.load_ohlcv_data(n_sessions)

        # Calculate indicators for each symbol
        results = []
        symbols = ohlcv_df['symbol'].unique()

        for i, symbol in enumerate(symbols, 1):
            if i % 50 == 0:
                logger.info(f"  Processing {i}/{len(symbols)} symbols...")

            symbol_df = ohlcv_df[ohlcv_df['symbol'] == symbol].copy()
            symbol_df = symbol_df.sort_values('date')

            try:
                symbol_df = self.calculate_indicators_for_symbol(symbol_df)
                results.append(symbol_df)
            except Exception as e:
                logger.error(f"  Error processing {symbol}: {e}")
                continue

        combined = pd.concat(results, ignore_index=True)

        logger.info(f"✅ Calculated indicators for {len(symbols)} symbols")
        return combined

    def save_basic_data(self, df: pd.DataFrame, output_path: str = "DATA/processed/technical/basic_data.parquet"):
        """
        Save technical indicators to parquet file.

        Args:
            df: DataFrame with indicators
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert date back to date (not datetime) for consistency
        df['date'] = pd.to_datetime(df['date']).dt.date

        # Sort by symbol and date
        df = df.sort_values(['symbol', 'date']).reset_index(drop=True)

        # Save
        df.to_parquet(output_path, index=False)

        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        logger.info(f"✅ Saved technical data to {output_path} ({file_size:.1f} MB)")

    def run_full_processing(self, n_sessions: int = 200):
        """
        Run full technical processing pipeline.

        Args:
            n_sessions: Number of sessions to process
        """
        logger.info("=" * 80)
        logger.info("TECHNICAL INDICATORS PROCESSING - TA-Lib Version")
        logger.info("=" * 80)

        # Calculate indicators
        df = self.calculate_all_indicators(n_sessions)

        # Save
        self.save_basic_data(df)

        logger.info("=" * 80)
        logger.info("✅ TECHNICAL PROCESSING COMPLETE")
        logger.info("=" * 80)

        return df


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Technical Indicators Processor (TA-Lib)')
    parser.add_argument('--sessions', type=int, default=200, help='Number of trading sessions to process')
    parser.add_argument('--ohlcv', type=str, default='DATA/raw/ohlcv/OHLCV_mktcap.parquet', help='OHLCV data path')

    args = parser.parse_args()

    try:
        processor = TechnicalProcessor(ohlcv_path=args.ohlcv)
        processor.run_full_processing(n_sessions=args.sessions)

    except Exception as e:
        logger.error(f"❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
