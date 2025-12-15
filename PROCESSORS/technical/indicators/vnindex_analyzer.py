#!/usr/bin/env python3
"""
VN-Index Technical Analyzer
============================

Fetch and analyze VN-Index using technical indicators.
Provides market-level view with all TA indicators.

Features:
- Fetch VN-Index OHLCV data from vnstock
- Calculate all technical indicators
- Track VN-Index trends
- Compare individual stocks with index

Author: Claude Code
Date: 2025-12-15
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import talib
import logging
from datetime import datetime, timedelta

# Add project root
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VNIndexAnalyzer:
    """Fetch and analyze VN-Index technical indicators."""

    def __init__(self):
        """Initialize analyzer."""
        pass

    def fetch_vnindex_data(self, n_sessions: int = 500) -> pd.DataFrame:
        """
        Fetch VN-Index OHLCV data from vnstock.

        Args:
            n_sessions: Number of sessions to fetch

        Returns:
            DataFrame with VN-Index OHLCV data
        """
        logger.info(f"Fetching VN-Index data (last {n_sessions} sessions)...")

        try:
            # Use vnstock_data with VND source (same as OHLCV updater)
            from vnstock_data import Quote

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=n_sessions * 2)  # Buffer for weekends

            # Fetch data using Quote class
            quote = Quote(symbol='VNINDEX', source='vnd')
            df = quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            if df is None or df.empty:
                logger.error("Failed to fetch VN-Index data")
                return pd.DataFrame()

            # Reset index and prepare data
            df = df.reset_index(drop=True)

            # Add symbol
            df['symbol'] = 'VNINDEX'

            # Rename time to date (vnstock_data returns 'time' column)
            if 'time' in df.columns:
                df = df.rename(columns={'time': 'date'})

            # Select and order columns
            df = df[['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']].copy()

            # Convert date to datetime.date
            df['date'] = pd.to_datetime(df['date']).dt.date

            # Sort and get last N sessions
            df = df.sort_values('date').tail(n_sessions).reset_index(drop=True)

            logger.info(f"✅ Fetched {len(df)} sessions for VN-Index")
            return df

        except Exception as e:
            logger.error(f"❌ Error fetching VN-Index data: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    def calculate_vnindex_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for VN-Index.

        Args:
            df: DataFrame with VN-Index OHLCV

        Returns:
            DataFrame with technical indicators
        """
        if len(df) < 200:
            logger.warning(f"Not enough data ({len(df)} rows) - need at least 200")
            return df

        logger.info(f"Calculating VN-Index technical indicators...")

        df = df.copy()

        # Convert to numpy arrays
        open_price = df['open'].values.astype(float)
        high = df['high'].values.astype(float)
        low = df['low'].values.astype(float)
        close = df['close'].values.astype(float)
        volume = df['volume'].values.astype(float)

        # === Moving Averages ===
        df['sma_20'] = talib.SMA(close, timeperiod=20)
        df['sma_50'] = talib.SMA(close, timeperiod=50)
        df['sma_100'] = talib.SMA(close, timeperiod=100)
        df['sma_200'] = talib.SMA(close, timeperiod=200)
        df['ema_20'] = talib.EMA(close, timeperiod=20)
        df['ema_50'] = talib.EMA(close, timeperiod=50)

        # === RSI ===
        df['rsi_14'] = talib.RSI(close, timeperiod=14)

        # === MACD ===
        macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        df['macd_hist'] = macd_hist

        # === Stochastic ===
        slowk, slowd = talib.STOCH(high, low, close, fastk_period=14, slowk_period=3, slowd_period=3)
        df['stoch_k'] = slowk
        df['stoch_d'] = slowd

        # === Bollinger Bands ===
        upperband, middleband, lowerband = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
        df['bb_upper'] = upperband
        df['bb_middle'] = middleband
        df['bb_lower'] = lowerband
        df['bb_width'] = (upperband - lowerband) / middleband * 100

        # === ATR ===
        df['atr_14'] = talib.ATR(high, low, close, timeperiod=14)

        # === Volume Indicators ===
        df['obv'] = talib.OBV(close, volume)
        df['ad_line'] = talib.AD(high, low, close, volume)
        df['cmf_20'] = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)
        df['mfi_14'] = talib.MFI(high, low, close, volume, timeperiod=14)

        # === Trend Indicators ===
        df['adx_14'] = talib.ADX(high, low, close, timeperiod=14)
        df['cci_20'] = talib.CCI(high, low, close, timeperiod=20)

        # === Price Distance from MAs ===
        df['price_vs_sma20'] = ((close - df['sma_20']) / df['sma_20'] * 100)
        df['price_vs_sma50'] = ((close - df['sma_50']) / df['sma_50'] * 100)
        df['price_vs_sma200'] = ((close - df['sma_200']) / df['sma_200'] * 100)

        logger.info(f"✅ Calculated indicators for VN-Index ({len(df)} rows, {len(df.columns)} columns)")
        return df

    def classify_vnindex_trend(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add trend classification to VN-Index data."""
        df = df.copy()

        # Trend based on MA alignment
        df['trend'] = 'UNKNOWN'

        # Check if required columns exist
        if 'sma_50' not in df.columns or 'sma_200' not in df.columns:
            logger.warning("Not enough data for trend classification (missing MA columns)")
            return df

        for idx in range(len(df)):
            row = df.iloc[idx]

            if pd.isna(row.get('sma_50')) or pd.isna(row.get('sma_200')):
                continue

            # Strong uptrend: Price > EMA20 > SMA50 > SMA200
            if (row['close'] > row['ema_20'] and
                row['ema_20'] > row['sma_50'] and
                row['sma_50'] > row['sma_200']):
                df.at[idx, 'trend'] = 'STRONG_UPTREND'

            # Uptrend: Price > SMA50 > SMA200
            elif row['close'] > row['sma_50'] > row['sma_200']:
                df.at[idx, 'trend'] = 'UPTREND'

            # Strong downtrend: Price < EMA20 < SMA50 < SMA200
            elif (row['close'] < row['ema_20'] and
                  row['ema_20'] < row['sma_50'] and
                  row['sma_50'] < row['sma_200']):
                df.at[idx, 'trend'] = 'STRONG_DOWNTREND'

            # Downtrend: Price < SMA50 < SMA200
            elif row['close'] < row['sma_50'] < row['sma_200']:
                df.at[idx, 'trend'] = 'DOWNTREND'

            # Sideways
            else:
                df.at[idx, 'trend'] = 'SIDEWAYS'

        return df

    def save_vnindex_data(self, df: pd.DataFrame, output_path: str = "DATA/processed/technical/vnindex/vnindex_indicators.parquet"):
        """Save VN-Index data with indicators."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert date
        df['date'] = pd.to_datetime(df['date']).dt.date

        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)

        # Save
        df.to_parquet(output_path, index=False)

        file_size = output_path.stat().st_size / 1024
        logger.info(f"✅ Saved VN-Index indicators to {output_path} ({file_size:.1f} KB)")

    def run_full_analysis(self, n_sessions: int = 500) -> pd.DataFrame:
        """
        Run complete VN-Index analysis.

        Args:
            n_sessions: Number of sessions

        Returns:
            DataFrame with VN-Index indicators
        """
        # Fetch data
        df = self.fetch_vnindex_data(n_sessions)

        if df.empty:
            logger.error("No VN-Index data available")
            return pd.DataFrame()

        # Calculate indicators
        df = self.calculate_vnindex_indicators(df)

        # Classify trend
        df = self.classify_vnindex_trend(df)

        # Save
        self.save_vnindex_data(df)

        return df


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='VN-Index Technical Analyzer')
    parser.add_argument('--sessions', type=int, default=500, help='Number of sessions')

    args = parser.parse_args()

    try:
        analyzer = VNIndexAnalyzer()
        df = analyzer.run_full_analysis(n_sessions=args.sessions)

        if not df.empty:
            # Print latest data
            latest = df.tail(1).iloc[0]
            print("\n" + "=" * 80)
            print(f"VN-INDEX TECHNICAL ANALYSIS - {latest['date']}")
            print("=" * 80)
            print(f"Close: {latest['close']:.2f}")
            print(f"Trend: {latest['trend']}")
            print(f"\nMoving Averages:")
            print(f"  SMA20: {latest['sma_20']:.2f} ({latest['price_vs_sma20']:.2f}%)")
            print(f"  SMA50: {latest['sma_50']:.2f} ({latest['price_vs_sma50']:.2f}%)")
            print(f"  SMA200: {latest['sma_200']:.2f} ({latest['price_vs_sma200']:.2f}%)")
            print(f"\nMomentum:")
            print(f"  RSI: {latest['rsi_14']:.2f}")
            print(f"  MACD: {latest['macd']:.2f} (Signal: {latest['macd_signal']:.2f})")
            print(f"  ADX: {latest['adx_14']:.2f}")
            print(f"\nVolume:")
            print(f"  MFI: {latest['mfi_14']:.2f}")
            print(f"  CMF: {latest['cmf_20']:.4f}")
            print("=" * 80)

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
