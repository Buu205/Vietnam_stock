#!/usr/bin/env python3
"""
Market Regime Detector
======================

Detect market conditions: bubble, euphoria, neutral, fear, bottom.

Uses multi-factor scoring:
1. Valuation (PE percentile)
2. Market breadth (% above MA50/200)
3. Volume patterns (vs historical average)
4. Volatility (ATR percentile)
5. Momentum (% stocks in uptrend)

Author: Claude Code
Date: 2025-12-15
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging

# Add project root
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketRegimeDetector:
    """Detect market regime using multi-factor analysis."""

    def __init__(
        self,
        technical_data_path: str = "DATA/processed/technical/basic_data.parquet",
        market_breadth_path: str = "DATA/processed/technical/market_breadth/market_breadth_daily.parquet",
        vnindex_pe_path: str = "DATA/processed/valuation/vnindex_pe/vnindex_pe_historical.parquet"
    ):
        """
        Initialize detector.

        Args:
            technical_data_path: Path to technical indicators
            market_breadth_path: Path to market breadth data
            vnindex_pe_path: Path to VN-Index PE data
        """
        self.technical_data_path = Path(technical_data_path)
        self.market_breadth_path = Path(market_breadth_path)
        self.vnindex_pe_path = Path(vnindex_pe_path)

    def detect_regime(self, date: str = None) -> dict:
        """
        Detect current market regime.

        Args:
            date: Target date (default: latest)

        Returns:
            Dict with regime classification and scores
        """
        logger.info(f"Detecting market regime...")

        # Load data
        tech_df = pd.read_parquet(self.technical_data_path)

        if date is None:
            date = tech_df['date'].max()

        day_df = tech_df[tech_df['date'] == date].copy()

        if len(day_df) == 0:
            logger.warning(f"No data for date {date}")
            return None

        # Factor 1: Valuation (PE percentile)
        valuation_score = self._calculate_valuation_score(date)

        # Factor 2: Market Breadth
        breadth_score = self._calculate_breadth_score(day_df)

        # Factor 3: Volume Pattern
        volume_score = self._calculate_volume_score(tech_df, date)

        # Factor 4: Volatility
        volatility_score = self._calculate_volatility_score(day_df)

        # Factor 5: Momentum
        momentum_score = self._calculate_momentum_score(day_df)

        # Overall regime score (-100 to +100)
        # Negative = bearish, Positive = bullish
        regime_score = (
            valuation_score * 0.25 +
            breadth_score * 0.25 +
            volume_score * 0.15 +
            volatility_score * 0.15 +
            momentum_score * 0.20
        )

        # Classify regime
        regime = self._classify_regime(regime_score)

        # Risk level
        risk_level = self._calculate_risk_level(regime_score, volatility_score)

        result = {
            'date': date,
            'regime': regime,
            'regime_score': round(regime_score, 2),
            'risk_level': risk_level,
            'valuation_score': round(valuation_score, 2),
            'breadth_score': round(breadth_score, 2),
            'volume_score': round(volume_score, 2),
            'volatility_score': round(volatility_score, 2),
            'momentum_score': round(momentum_score, 2),
            'market_sentiment': self._get_sentiment(regime_score)
        }

        logger.info(f"✅ Market regime: {regime} (score: {regime_score:.2f})")
        return result

    def _calculate_valuation_score(self, date) -> float:
        """Calculate valuation score based on VN-Index PE percentile."""
        try:
            if not self.vnindex_pe_path.exists():
                logger.warning("VN-Index PE data not found, using neutral valuation score")
                return 0.0

            pe_df = pd.read_parquet(self.vnindex_pe_path)
            pe_df = pe_df.sort_values('date')

            # Get current PE
            current_pe_row = pe_df[pe_df['date'] == date]
            if current_pe_row.empty:
                current_pe_row = pe_df.tail(1)

            current_pe = current_pe_row['pe_ratio'].iloc[0]

            # Calculate percentile (last 252 sessions)
            recent_pe = pe_df.tail(252)['pe_ratio']
            percentile = (recent_pe < current_pe).sum() / len(recent_pe) * 100

            # Convert to score (-100 to +100)
            # Higher PE = more expensive = negative score
            if percentile >= 90:
                return -80  # Very expensive
            elif percentile >= 75:
                return -50  # Expensive
            elif percentile >= 60:
                return -20  # Slightly expensive
            elif percentile >= 40:
                return 0    # Fair value
            elif percentile >= 25:
                return 20   # Cheap
            elif percentile >= 10:
                return 50   # Very cheap
            else:
                return 80   # Extremely cheap

        except Exception as e:
            logger.warning(f"Error calculating valuation score: {e}")
            return 0.0

    def _calculate_breadth_score(self, day_df: pd.DataFrame) -> float:
        """Calculate breadth score."""
        total_stocks = len(day_df)

        # % above MA50 and MA200
        above_ma50 = (day_df['close'] > day_df['sma_50']).sum()
        above_ma200 = (day_df['close'] > day_df['sma_200']).sum()

        pct_above_ma50 = (above_ma50 / total_stocks) * 100
        pct_above_ma200 = (above_ma200 / total_stocks) * 100

        # Convert to score
        breadth_score = (
            (pct_above_ma50 - 50) * 1.5 +  # -75 to +75
            (pct_above_ma200 - 50) * 0.5   # -25 to +25
        )

        return max(-100, min(100, breadth_score))

    def _calculate_volume_score(self, tech_df: pd.DataFrame, date) -> float:
        """Calculate volume pattern score."""
        try:
            # Get last 20 sessions including current
            recent_df = tech_df.groupby('date').agg({
                'volume': 'sum'
            }).reset_index()
            recent_df = recent_df.sort_values('date').tail(20)

            if len(recent_df) < 20:
                return 0.0

            current_volume = recent_df[recent_df['date'] == date]['volume'].iloc[0]
            avg_volume = recent_df.head(19)['volume'].mean()

            volume_ratio = current_volume / avg_volume

            # Convert to score
            if volume_ratio >= 1.5:
                return 50  # High volume = interest
            elif volume_ratio >= 1.2:
                return 20
            elif volume_ratio >= 0.8:
                return 0
            elif volume_ratio >= 0.6:
                return -20
            else:
                return -50  # Very low volume = lack of interest

        except Exception as e:
            logger.warning(f"Error calculating volume score: {e}")
            return 0.0

    def _calculate_volatility_score(self, day_df: pd.DataFrame) -> float:
        """Calculate volatility score."""
        # Average ATR percentile
        atr_values = day_df['atr_14'].dropna()

        if len(atr_values) == 0:
            return 0.0

        # Higher ATR = higher volatility = more risk
        avg_atr = atr_values.mean()
        atr_std = atr_values.std()

        if atr_std == 0:
            return 0.0

        # Z-score
        z_score = (avg_atr - atr_values.mean()) / atr_std

        # Convert to score (-100 to +100)
        # High volatility = negative (risky)
        volatility_score = -z_score * 30

        return max(-100, min(100, volatility_score))

    def _calculate_momentum_score(self, day_df: pd.DataFrame) -> float:
        """Calculate momentum score."""
        total_stocks = len(day_df)

        # % with bullish MACD
        bullish_macd = (day_df['macd_hist'] > 0).sum()

        # % with RSI in bullish zone (50-70)
        bullish_rsi = ((day_df['rsi_14'] >= 50) & (day_df['rsi_14'] < 70)).sum()

        pct_bullish_macd = (bullish_macd / total_stocks) * 100
        pct_bullish_rsi = (bullish_rsi / total_stocks) * 100

        # Convert to score
        momentum_score = (
            (pct_bullish_macd - 50) * 1.2 +
            (pct_bullish_rsi - 50) * 0.8
        )

        return max(-100, min(100, momentum_score))

    def _classify_regime(self, score: float) -> str:
        """Classify market regime based on score."""
        if score >= 60:
            return 'BUBBLE'
        elif score >= 30:
            return 'EUPHORIA'
        elif score >= -30:
            return 'NEUTRAL'
        elif score >= -60:
            return 'FEAR'
        else:
            return 'BOTTOM'

    def _calculate_risk_level(self, regime_score: float, volatility_score: float) -> str:
        """Calculate risk level."""
        # Extreme bullish + high volatility = very high risk
        # Extreme bearish + low volatility = opportunity

        if regime_score > 50 and volatility_score < -30:
            return 'VERY_HIGH'
        elif regime_score > 30 or volatility_score < -30:
            return 'HIGH'
        elif -30 <= regime_score <= 30:
            return 'MEDIUM'
        elif regime_score < -50 and volatility_score > 20:
            return 'LOW'
        else:
            return 'MEDIUM'

    def _get_sentiment(self, score: float) -> str:
        """Get market sentiment description."""
        if score >= 60:
            return 'EXTREME_GREED'
        elif score >= 30:
            return 'GREED'
        elif score >= 10:
            return 'SLIGHTLY_BULLISH'
        elif score >= -10:
            return 'NEUTRAL'
        elif score >= -30:
            return 'SLIGHTLY_BEARISH'
        elif score >= -60:
            return 'FEAR'
        else:
            return 'EXTREME_FEAR'

    def save_regime_history(self, regime_data: dict, output_path: str = "DATA/processed/technical/market_regime/market_regime_history.parquet"):
        """Save regime data to history."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to DataFrame
        new_row = pd.DataFrame([regime_data])

        # Convert date
        new_row['date'] = pd.to_datetime(new_row['date']).dt.date

        # Append or create
        if output_path.exists():
            existing = pd.read_parquet(output_path)
            # Remove duplicate date
            existing = existing[existing['date'] != regime_data['date']]
            combined = pd.concat([existing, new_row], ignore_index=True)
            combined = combined.sort_values('date').reset_index(drop=True)
            combined.to_parquet(output_path, index=False)
            logger.info(f"✅ Updated market regime history (total: {len(combined)} records)")
        else:
            new_row.to_parquet(output_path, index=False)
            logger.info(f"✅ Created new market regime history file")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Market Regime Detector')
    parser.add_argument('--date', type=str, default=None, help='Target date (YYYY-MM-DD)')

    args = parser.parse_args()

    try:
        detector = MarketRegimeDetector()
        regime_data = detector.detect_regime(date=args.date)

        if regime_data:
            detector.save_regime_history(regime_data)

            # Print summary
            print("\n" + "=" * 80)
            print(f"MARKET REGIME ANALYSIS - {regime_data['date']}")
            print("=" * 80)
            print(f"Regime: {regime_data['regime']}")
            print(f"Regime Score: {regime_data['regime_score']}")
            print(f"Risk Level: {regime_data['risk_level']}")
            print(f"Market Sentiment: {regime_data['market_sentiment']}")
            print("\nComponent Scores:")
            print(f"  Valuation: {regime_data['valuation_score']}")
            print(f"  Breadth: {regime_data['breadth_score']}")
            print(f"  Volume: {regime_data['volume_score']}")
            print(f"  Volatility: {regime_data['volatility_score']}")
            print(f"  Momentum: {regime_data['momentum_score']}")
            print("=" * 80)

    except Exception as e:
        logger.error(f"❌ Detection failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
