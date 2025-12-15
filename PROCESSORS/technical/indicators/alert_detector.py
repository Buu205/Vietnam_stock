#!/usr/bin/env python3
"""
Technical Alert Detector
========================

Detect trading alerts using TA-Lib:
- MA Crossover (price crosses MA20/50/100/200)
- Smart Volume Spike (volume + breakout + RSI + MACD + patterns)
- Breakout (price breaks resistance/support)
- Candlestick Patterns (61 patterns from TA-Lib)
- Combined Signals (MA + RSI + MACD scoring)

Author: Claude Code
Date: 2025-12-15
"""

import pandas as pd
import numpy as np
import talib
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalAlertDetector:
    """Detect technical alerts using TA-Lib."""

    def __init__(self, ohlcv_path: str = "DATA/raw/ohlcv/OHLCV_mktcap.parquet"):
        """
        Initialize alert detector.

        Args:
            ohlcv_path: Path to OHLCV data
        """
        self.ohlcv_path = Path(ohlcv_path)
        if not self.ohlcv_path.exists():
            raise FileNotFoundError(f"OHLCV file not found: {self.ohlcv_path}")

    def load_data(self, n_sessions: int = 200) -> pd.DataFrame:
        """Load last N sessions for all symbols."""
        logger.info(f"Loading OHLCV data (last {n_sessions} sessions)...")

        df = pd.read_parquet(self.ohlcv_path)

        # Get last N sessions for each symbol
        result = []
        for symbol in df['symbol'].unique():
            symbol_df = df[df['symbol'] == symbol].copy()
            symbol_df = symbol_df.sort_values('date').tail(n_sessions)
            result.append(symbol_df)

        combined = pd.concat(result, ignore_index=True)
        logger.info(f"✅ Loaded {len(combined):,} records for {combined['symbol'].nunique()} symbols")
        return combined

    def detect_ma_crossover(self, symbol: str, df: pd.DataFrame) -> List[Dict]:
        """
        Detect MA crossover events.

        Args:
            symbol: Stock symbol
            df: DataFrame with OHLCV for this symbol (sorted by date)

        Returns:
            List of crossover alerts
        """
        if len(df) < 2:
            return []

        alerts = []
        close = df['close'].values.astype(float)

        # Calculate MAs
        sma_20 = talib.SMA(close, timeperiod=20)
        sma_50 = talib.SMA(close, timeperiod=50)
        sma_100 = talib.SMA(close, timeperiod=100)
        sma_200 = talib.SMA(close, timeperiod=200)

        # Check last 2 days for crossover
        current_idx = -1
        prev_idx = -2

        for ma_period, ma_values in [
            (20, sma_20), (50, sma_50), (100, sma_100), (200, sma_200)
        ]:
            if np.isnan(ma_values[current_idx]) or np.isnan(ma_values[prev_idx]):
                continue

            prev_close = close[prev_idx]
            curr_close = close[current_idx]
            prev_ma = ma_values[prev_idx]
            curr_ma = ma_values[current_idx]

            # Cross above
            if prev_close < prev_ma and curr_close > curr_ma:
                alerts.append({
                    'symbol': symbol,
                    'date': df.iloc[current_idx]['date'],
                    'alert_type': 'MA_CROSS_ABOVE',
                    'ma_period': ma_period,
                    'price': float(curr_close),
                    'ma_value': float(curr_ma),
                    'signal': 'BULLISH'
                })

            # Cross below
            elif prev_close > prev_ma and curr_close < curr_ma:
                alerts.append({
                    'symbol': symbol,
                    'date': df.iloc[current_idx]['date'],
                    'alert_type': 'MA_CROSS_BELOW',
                    'ma_period': ma_period,
                    'price': float(curr_close),
                    'ma_value': float(curr_ma),
                    'signal': 'BEARISH'
                })

        return alerts

    def detect_smart_volume_spike(self, symbol: str, df: pd.DataFrame) -> Optional[Dict]:
        """
        Smart volume spike with 4-factor confirmation.

        Factors:
        1. Volume spike (>1.5x average)
        2. Breakout (price > 20-day high)
        3. RSI confirmation (not overbought)
        4. MACD bullish
        5. Candlestick pattern

        Args:
            symbol: Stock symbol
            df: DataFrame with OHLCV

        Returns:
            Alert dict or None
        """
        if len(df) < 21:
            return None

        # Convert to numpy
        close = df['close'].values.astype(float)
        high = df['high'].values.astype(float)
        low = df['low'].values.astype(float)
        open_price = df['open'].values.astype(float)
        volume = df['volume'].values.astype(float)

        # 1. Volume spike
        avg_volume_20 = np.mean(volume[-21:-1])  # Exclude current day
        current_volume = volume[-1]

        if avg_volume_20 == 0 or current_volume < avg_volume_20 * 1.5:
            return None

        volume_ratio = current_volume / avg_volume_20

        # 2. RSI
        rsi = talib.RSI(close, timeperiod=14)
        current_rsi = rsi[-1]

        # 3. MACD
        macd, macd_signal, _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        macd_bullish = macd[-1] > macd_signal[-1]

        # 4. Breakout
        resistance_20 = np.max(high[-21:-1])
        support_20 = np.min(low[-21:-1])
        is_breakout_up = close[-1] > resistance_20
        is_breakdown = close[-1] < support_20

        # 5. Candlestick pattern (top 10)
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

        active_pattern = None
        pattern_signal = None
        for name, values in patterns.items():
            if values[-1] != 0:
                active_pattern = name
                pattern_signal = 'BULLISH' if values[-1] > 0 else 'BEARISH'
                break

        # Calculate confirmations
        confirmations = 0
        confirmation_details = {}

        if is_breakout_up:
            confirmations += 1
            confirmation_details['breakout'] = 'UP'
        elif is_breakdown:
            confirmations += 1
            confirmation_details['breakout'] = 'DOWN'

        if 40 <= current_rsi <= 70:
            confirmations += 1
            confirmation_details['rsi'] = 'HEALTHY'
        elif current_rsi < 30:
            confirmations += 1
            confirmation_details['rsi'] = 'OVERSOLD_BOUNCE'

        if macd_bullish:
            confirmations += 1
            confirmation_details['macd'] = 'BULLISH'

        if active_pattern and pattern_signal == 'BULLISH':
            confirmations += 1
            confirmation_details['pattern'] = active_pattern.upper()

        # Determine signal
        price_change_pct = ((close[-1] - close[-2]) / close[-2]) * 100

        if confirmations >= 3:
            if is_breakout_up and macd_bullish:
                signal = 'STRONG_BUY'
                confidence = 0.85
            elif price_change_pct > 0:
                signal = 'BUY'
                confidence = 0.70
            else:
                signal = 'DISTRIBUTION'
                confidence = 0.65
        elif confirmations >= 2:
            signal = 'WATCH'
            confidence = 0.50
        else:
            signal = 'NOISE'
            confidence = 0.30

        return {
            'symbol': symbol,
            'date': df.iloc[-1]['date'],
            'alert_type': 'SMART_VOLUME_SPIKE',
            'volume': int(current_volume),
            'avg_volume_20d': int(avg_volume_20),
            'volume_ratio': round(volume_ratio, 2),
            'price': float(close[-1]),
            'price_change_pct': round(price_change_pct, 2),
            'is_breakout': bool(is_breakout_up),
            'rsi': round(float(current_rsi), 2) if not np.isnan(current_rsi) else None,
            'macd_bullish': bool(macd_bullish),
            'candlestick_pattern': active_pattern,
            'pattern_signal': pattern_signal,
            'signal': signal,
            'confidence': confidence,
            'confirmations': confirmations,
            'confirmation_details': confirmation_details
        }

    def detect_breakout(self, symbol: str, df: pd.DataFrame) -> Optional[Dict]:
        """
        Detect breakout/breakdown with volume confirmation.

        Args:
            symbol: Stock symbol
            df: DataFrame with OHLCV

        Returns:
            Breakout alert or None
        """
        if len(df) < 21:
            return None

        close = df['close'].values.astype(float)
        high = df['high'].values.astype(float)
        low = df['low'].values.astype(float)
        volume = df['volume'].values.astype(float)

        # 20-day high/low (exclude current)
        resistance = np.max(high[-21:-1])
        support = np.min(low[-21:-1])

        # Volume confirmation
        avg_volume = np.mean(volume[-21:-1])
        current_volume = volume[-1]
        volume_confirmed = current_volume > (avg_volume * 1.5)

        # Breakout up
        if close[-1] > resistance and volume_confirmed:
            return {
                'symbol': symbol,
                'date': df.iloc[-1]['date'],
                'alert_type': 'BREAKOUT_UP',
                'price': float(close[-1]),
                'resistance_level': float(resistance),
                'volume_confirmed': True,
                'volume_ratio': round(float(current_volume / avg_volume), 2),
                'signal': 'BULLISH_BREAKOUT'
            }

        # Breakdown
        elif close[-1] < support and volume_confirmed:
            return {
                'symbol': symbol,
                'date': df.iloc[-1]['date'],
                'alert_type': 'BREAKDOWN',
                'price': float(close[-1]),
                'support_level': float(support),
                'volume_confirmed': True,
                'volume_ratio': round(float(current_volume / avg_volume), 2),
                'signal': 'BEARISH_BREAKDOWN'
            }

        return None

    def detect_candlestick_patterns(self, symbol: str, df: pd.DataFrame) -> List[Dict]:
        """
        Detect candlestick patterns (top 10 most reliable).

        Args:
            symbol: Stock symbol
            df: DataFrame with OHLCV

        Returns:
            List of pattern alerts
        """
        if len(df) < 3:
            return []

        close = df['close'].values.astype(float)
        high = df['high'].values.astype(float)
        low = df['low'].values.astype(float)
        open_price = df['open'].values.astype(float)

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

        alerts = []
        for pattern_name, values in patterns.items():
            if values[-1] != 0:
                alerts.append({
                    'symbol': symbol,
                    'date': df.iloc[-1]['date'],
                    'alert_type': 'CANDLESTICK_PATTERN',
                    'pattern_name': pattern_name,
                    'signal': 'BULLISH' if values[-1] > 0 else 'BEARISH',
                    'strength': abs(int(values[-1])),
                    'price': float(close[-1])
                })

        return alerts

    def detect_combined_signal(self, symbol: str, df: pd.DataFrame) -> Optional[Dict]:
        """
        Combined MA + RSI + MACD signal with scoring.

        Scoring:
        - MA trend: 40 points
        - RSI: 30 points
        - MACD: 30 points

        Total >= 70: STRONG_BUY/SELL
        Total >= 40: BUY/SELL
        Otherwise: HOLD

        Args:
            symbol: Stock symbol
            df: DataFrame with OHLCV

        Returns:
            Combined signal or None
        """
        if len(df) < 50:
            return None

        close = df['close'].values.astype(float)

        # MAs
        sma_20 = talib.SMA(close, timeperiod=20)
        sma_50 = talib.SMA(close, timeperiod=50)

        if np.isnan(sma_20[-1]) or np.isnan(sma_50[-1]):
            return None

        # RSI
        rsi = talib.RSI(close, timeperiod=14)
        current_rsi = rsi[-1]

        # MACD
        macd, macd_signal, _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

        # Scoring
        score = 0

        # MA trend (40 points)
        if close[-1] > sma_20[-1] and sma_20[-1] > sma_50[-1]:
            score += 40
            ma_trend = 'BULLISH'
        elif close[-1] < sma_20[-1] and sma_20[-1] < sma_50[-1]:
            score -= 40
            ma_trend = 'BEARISH'
        else:
            ma_trend = 'NEUTRAL'

        # RSI (30 points)
        if 40 <= current_rsi <= 60:
            score += 30
        elif current_rsi < 30:
            score += 20  # Oversold bounce
        elif current_rsi > 70:
            score -= 20  # Overbought

        # MACD (30 points)
        if macd[-1] > macd_signal[-1]:
            score += 30
            macd_sig = 'BULLISH_CROSS'
        elif macd[-1] < macd_signal[-1]:
            score -= 30
            macd_sig = 'BEARISH_CROSS'
        else:
            macd_sig = 'NEUTRAL'

        # Classify
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
            'date': df.iloc[-1]['date'],
            'alert_type': 'COMBINED_SIGNAL',
            'price': float(close[-1]),
            'ma_trend': ma_trend,
            'rsi_14': round(float(current_rsi), 2),
            'macd_signal': macd_sig,
            'overall_signal': overall_signal,
            'confidence': confidence,
            'score': score
        }

    def detect_all_alerts(self, date: str = None, n_sessions: int = 200) -> Dict[str, pd.DataFrame]:
        """
        Detect all alerts for all symbols.

        Args:
            date: Target date (default: latest)
            n_sessions: Number of sessions to load

        Returns:
            Dict with alert DataFrames
        """
        logger.info(f"Detecting alerts (sessions: {n_sessions})...")

        # Load data
        ohlcv_df = self.load_data(n_sessions)

        if date is None:
            date = ohlcv_df['date'].max()

        # Detect alerts for each symbol
        ma_crossover_alerts = []
        volume_spike_alerts = []
        breakout_alerts = []
        pattern_alerts = []
        combined_signals = []

        symbols = ohlcv_df['symbol'].unique()

        for i, symbol in enumerate(symbols, 1):
            if i % 100 == 0:
                logger.info(f"  Processing {i}/{len(symbols)} symbols...")

            symbol_df = ohlcv_df[ohlcv_df['symbol'] == symbol].copy()
            symbol_df = symbol_df.sort_values('date')

            try:
                # MA crossover
                ma_alerts = self.detect_ma_crossover(symbol, symbol_df)
                ma_crossover_alerts.extend(ma_alerts)

                # Volume spike
                vol_alert = self.detect_smart_volume_spike(symbol, symbol_df)
                if vol_alert:
                    volume_spike_alerts.append(vol_alert)

                # Breakout
                breakout_alert = self.detect_breakout(symbol, symbol_df)
                if breakout_alert:
                    breakout_alerts.append(breakout_alert)

                # Patterns
                pattern_list = self.detect_candlestick_patterns(symbol, symbol_df)
                pattern_alerts.extend(pattern_list)

                # Combined
                combined = self.detect_combined_signal(symbol, symbol_df)
                if combined:
                    combined_signals.append(combined)

            except Exception as e:
                logger.error(f"  Error processing {symbol}: {e}")
                continue

        logger.info(f"✅ Alert detection complete")
        logger.info(f"  MA Crossover: {len(ma_crossover_alerts)}")
        logger.info(f"  Volume Spike: {len(volume_spike_alerts)}")
        logger.info(f"  Breakout: {len(breakout_alerts)}")
        logger.info(f"  Patterns: {len(pattern_alerts)}")
        logger.info(f"  Combined: {len(combined_signals)}")

        return {
            'ma_crossover': pd.DataFrame(ma_crossover_alerts),
            'volume_spike': pd.DataFrame(volume_spike_alerts),
            'breakout': pd.DataFrame(breakout_alerts),
            'patterns': pd.DataFrame(pattern_alerts),
            'combined': pd.DataFrame(combined_signals)
        }
