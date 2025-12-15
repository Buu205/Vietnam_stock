#!/usr/bin/env python3
"""
Money Flow Analyzer
===================

Track fund flows using volume-based indicators:
- Chaikin Money Flow (CMF)
- Money Flow Index (MFI)
- On-Balance Volume (OBV)
- Accumulation/Distribution Line
- Volume Price Trend (VPT)

Author: Claude Code
Date: 2025-12-15
"""

import pandas as pd
import numpy as np
import talib
from pathlib import Path
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MoneyFlowAnalyzer:
    """Calculate money flow indicators for stocks."""

    def __init__(self, ohlcv_path: str = "DATA/raw/ohlcv/OHLCV_mktcap.parquet"):
        """
        Initialize analyzer.

        Args:
            ohlcv_path: Path to OHLCV data
        """
        self.ohlcv_path = Path(ohlcv_path)
        if not self.ohlcv_path.exists():
            raise FileNotFoundError(f"OHLCV file not found: {self.ohlcv_path}")

    def load_data(self, n_sessions: int = 200) -> pd.DataFrame:
        """Load last N sessions."""
        logger.info(f"Loading OHLCV data for money flow analysis...")

        df = pd.read_parquet(self.ohlcv_path)

        # Get last N sessions per symbol
        result = []
        for symbol in df['symbol'].unique():
            symbol_df = df[df['symbol'] == symbol].copy()
            symbol_df = symbol_df.sort_values('date').tail(n_sessions)
            result.append(symbol_df)

        combined = pd.concat(result, ignore_index=True)
        logger.info(f"✅ Loaded {len(combined):,} records for {combined['symbol'].nunique()} symbols")
        return combined

    def calculate_money_flow_for_symbol(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate money flow indicators for one symbol.

        Args:
            df: DataFrame with OHLCV for one symbol

        Returns:
            DataFrame with money flow indicators
        """
        if len(df) < 20:
            return df

        df = df.copy()

        # Convert to numpy
        high = df['high'].values.astype(float)
        low = df['low'].values.astype(float)
        close = df['close'].values.astype(float)
        volume = df['volume'].values.astype(float)

        # Chaikin Money Flow
        df['cmf_20'] = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)

        # Money Flow Index
        df['mfi_14'] = talib.MFI(high, low, close, volume, timeperiod=14)

        # On-Balance Volume
        df['obv'] = talib.OBV(close, volume)

        # AD Line
        df['ad_line'] = talib.AD(high, low, close, volume)

        # Volume Price Trend (custom)
        df['vpt'] = self._calculate_vpt(close, volume)

        # Money flow signal
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
        Classify money flow based on indicators.

        Returns:
            Series with classification
        """
        signals = []

        for idx, row in df.iterrows():
            score = 0

            # CMF contribution
            if not pd.isna(row['cmf_20']):
                if row['cmf_20'] > 0.10:
                    score += 2
                elif row['cmf_20'] > 0.05:
                    score += 1
                elif row['cmf_20'] < -0.10:
                    score -= 2
                elif row['cmf_20'] < -0.05:
                    score -= 1

            # MFI contribution
            if not pd.isna(row['mfi_14']):
                if row['mfi_14'] > 70:
                    score -= 1  # Overbought
                elif row['mfi_14'] < 30:
                    score += 1  # Oversold

            # OBV trend (compare with 20-period MA)
            if idx >= 20:
                obv_ma = df['obv'].iloc[idx-20:idx].mean()
                if not pd.isna(obv_ma) and not pd.isna(row['obv']):
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

    def calculate_all_money_flow(self, n_sessions: int = 200) -> pd.DataFrame:
        """
        Calculate money flow for all symbols.

        Args:
            n_sessions: Number of sessions

        Returns:
            DataFrame with money flow indicators
        """
        logger.info(f"Calculating money flow indicators...")

        # Load data
        ohlcv_df = self.load_data(n_sessions)

        # Calculate for each symbol
        results = []
        symbols = ohlcv_df['symbol'].unique()

        for i, symbol in enumerate(symbols, 1):
            if i % 100 == 0:
                logger.info(f"  Processing {i}/{len(symbols)} symbols...")

            symbol_df = ohlcv_df[ohlcv_df['symbol'] == symbol].copy()
            symbol_df = symbol_df.sort_values('date')

            try:
                symbol_df = self.calculate_money_flow_for_symbol(symbol_df)
                results.append(symbol_df)
            except Exception as e:
                logger.error(f"  Error processing {symbol}: {e}")
                continue

        combined = pd.concat(results, ignore_index=True)

        logger.info(f"✅ Money flow calculated for {len(symbols)} symbols")
        return combined

    def save_money_flow(self, df: pd.DataFrame, output_path: str = "DATA/processed/technical/money_flow/individual_money_flow.parquet"):
        """Save money flow data."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert date
        df['date'] = pd.to_datetime(df['date']).dt.date

        # Sort
        df = df.sort_values(['symbol', 'date']).reset_index(drop=True)

        # Save
        df.to_parquet(output_path, index=False)

        file_size = output_path.stat().st_size / (1024 * 1024)
        logger.info(f"✅ Saved money flow data to {output_path} ({file_size:.1f} MB)")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Money Flow Analyzer')
    parser.add_argument('--sessions', type=int, default=200, help='Number of sessions')

    args = parser.parse_args()

    try:
        analyzer = MoneyFlowAnalyzer()
        df = analyzer.calculate_all_money_flow(n_sessions=args.sessions)
        analyzer.save_money_flow(df)

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
