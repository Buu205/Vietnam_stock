#!/usr/bin/env python3
"""
Market State Calculator
========================

Combines market regime, breadth, and VN-Index data into a single market state snapshot.
Used by Technical Dashboard Tab 1: Market Overview.

Output: DATA/processed/technical/market/market_state_latest.parquet

Columns:
    - date: Trading date
    - vnindex_close: VN-Index closing price
    - vnindex_change_pct: Daily change %
    - regime: BULLISH/NEUTRAL/BEARISH
    - ema9, ema21: VN-Index EMAs
    - breadth_ma20_pct, breadth_ma50_pct, breadth_ma100_pct: Market breadth
    - ad_ratio: Advance/Decline ratio
    - exposure_level: Recommended exposure (0-100)
    - divergence_type: BULLISH_DIV/BEARISH_DIV/None
    - divergence_strength: 0-100
    - signal: RISK_ON/RISK_OFF/CAUTION

Author: Claude Code
Date: 2025-12-31
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from typing import Optional

# Add project root
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketStateCalculator:
    """Calculate consolidated market state for dashboard."""

    def __init__(self):
        """Initialize calculator with data paths from registry."""
        self.project_root = project_root

        # Input paths
        self.vnindex_path = self.project_root / "DATA/processed/technical/vnindex/vnindex_indicators.parquet"
        self.breadth_path = self.project_root / "DATA/processed/technical/market_breadth/market_breadth_daily.parquet"
        self.regime_path = self.project_root / "DATA/processed/technical/market_regime/market_regime_history.parquet"
        self.technical_path = self.project_root / "DATA/processed/technical/basic_data.parquet"

        # Output path
        self.output_dir = self.project_root / "DATA/processed/technical/market"
        self.output_path = self.output_dir / "market_state_latest.parquet"

    def calculate(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate market state for a given date.

        Args:
            date: Target date (YYYY-MM-DD), defaults to latest

        Returns:
            DataFrame with single row of market state
        """
        logger.info("Calculating market state...")

        # Load VN-Index data
        vnindex_df = self._load_vnindex(date)
        if vnindex_df.empty:
            logger.error("No VN-Index data available")
            return pd.DataFrame()

        target_date = vnindex_df['date'].iloc[0]
        logger.info(f"Target date: {target_date}")

        # Load breadth data
        breadth = self._load_breadth(target_date)

        # Load regime data
        regime = self._load_regime(target_date)

        # Calculate AD ratio
        ad_ratio = self._calculate_ad_ratio(target_date)

        # Calculate divergence
        divergence = self._detect_divergence(target_date)

        # Calculate exposure level
        exposure = self._calculate_exposure(regime, breadth)

        # Determine signal
        signal = self._determine_signal(regime, breadth, divergence)

        # Build result
        result = pd.DataFrame([{
            'date': target_date,
            'vnindex_close': vnindex_df['close'].iloc[0],
            'vnindex_change_pct': vnindex_df.get('change_pct', pd.Series([0])).iloc[0],
            'regime': regime.get('regime', 'NEUTRAL'),
            'regime_score': regime.get('regime_score', 0),
            'ema9': vnindex_df.get('ema_9', pd.Series([0])).iloc[0],
            'ema21': vnindex_df.get('ema_21', pd.Series([0])).iloc[0],
            'breadth_ma20_pct': breadth.get('above_ma20_pct', 0),
            'breadth_ma50_pct': breadth.get('above_ma50_pct', 0),
            'breadth_ma100_pct': breadth.get('above_ma100_pct', 0),
            'ad_ratio': ad_ratio,
            'exposure_level': exposure,
            'divergence_type': divergence.get('type'),
            'divergence_strength': divergence.get('strength', 0),
            'signal': signal
        }])

        return result

    def _load_vnindex(self, date: Optional[str] = None) -> pd.DataFrame:
        """Load VN-Index indicators."""
        if not self.vnindex_path.exists():
            logger.warning(f"VN-Index file not found: {self.vnindex_path}")
            return pd.DataFrame()

        df = pd.read_parquet(self.vnindex_path)
        df['date'] = pd.to_datetime(df['date'])

        if date:
            df = df[df['date'] == pd.to_datetime(date)]
        else:
            df = df.sort_values('date').tail(1)

        return df

    def _load_breadth(self, date) -> dict:
        """Load market breadth data."""
        if not self.breadth_path.exists():
            return {}

        df = pd.read_parquet(self.breadth_path)
        df['date'] = pd.to_datetime(df['date'])

        day_df = df[df['date'] == pd.to_datetime(date)]
        if day_df.empty:
            # Get latest available
            day_df = df.sort_values('date').tail(1)

        if day_df.empty:
            return {}

        return day_df.iloc[0].to_dict()

    def _load_regime(self, date) -> dict:
        """Load market regime data."""
        if not self.regime_path.exists():
            return {'regime': 'NEUTRAL', 'regime_score': 0}

        df = pd.read_parquet(self.regime_path)
        df['date'] = pd.to_datetime(df['date'])

        day_df = df[df['date'] == pd.to_datetime(date)]
        if day_df.empty:
            day_df = df.sort_values('date').tail(1)

        if day_df.empty:
            return {'regime': 'NEUTRAL', 'regime_score': 0}

        return day_df.iloc[0].to_dict()

    def _calculate_ad_ratio(self, date) -> float:
        """Calculate Advance/Decline ratio."""
        if not self.technical_path.exists():
            return 1.0

        df = pd.read_parquet(self.technical_path)
        df['date'] = pd.to_datetime(df['date'])

        day_df = df[df['date'] == pd.to_datetime(date)]
        if day_df.empty:
            return 1.0

        # Calculate based on daily change
        if 'close' in day_df.columns and 'open' in day_df.columns:
            advances = (day_df['close'] > day_df['open']).sum()
            declines = (day_df['close'] < day_df['open']).sum()
            if declines > 0:
                return round(advances / declines, 2)

        return 1.0

    def _detect_divergence(self, date) -> dict:
        """Detect price-breadth divergence."""
        # Load last 20 days of data
        if not self.vnindex_path.exists() or not self.breadth_path.exists():
            return {'type': None, 'strength': 0}

        vnindex = pd.read_parquet(self.vnindex_path)
        breadth = pd.read_parquet(self.breadth_path)

        vnindex['date'] = pd.to_datetime(vnindex['date'])
        breadth['date'] = pd.to_datetime(breadth['date'])

        target_date = pd.to_datetime(date)
        vnindex = vnindex[vnindex['date'] <= target_date].sort_values('date').tail(20)
        breadth = breadth[breadth['date'] <= target_date].sort_values('date').tail(20)

        if len(vnindex) < 10 or len(breadth) < 10:
            return {'type': None, 'strength': 0}

        # Compare trends
        price_trend = vnindex['close'].iloc[-1] / vnindex['close'].iloc[0] - 1
        breadth_trend = breadth['above_ma50_pct'].iloc[-1] - breadth['above_ma50_pct'].iloc[0]

        # Bearish divergence: price up, breadth down
        if price_trend > 0.02 and breadth_trend < -10:
            strength = min(100, int(abs(breadth_trend) * 2))
            return {'type': 'BEARISH_DIV', 'strength': strength}

        # Bullish divergence: price down, breadth up
        if price_trend < -0.02 and breadth_trend > 10:
            strength = min(100, int(breadth_trend * 2))
            return {'type': 'BULLISH_DIV', 'strength': strength}

        return {'type': None, 'strength': 0}

    def _calculate_exposure(self, regime: dict, breadth: dict) -> int:
        """Calculate recommended exposure level (0-100)."""
        base_exposure = 50

        # Adjust based on regime
        regime_score = regime.get('regime_score', 0)
        regime_adjustment = regime_score * 0.3  # -30 to +30

        # Adjust based on breadth
        ma50_pct = breadth.get('above_ma50_pct', 50)
        if ma50_pct > 70:
            breadth_adjustment = 15
        elif ma50_pct > 50:
            breadth_adjustment = 10
        elif ma50_pct < 30:
            breadth_adjustment = -15
        elif ma50_pct < 50:
            breadth_adjustment = -10
        else:
            breadth_adjustment = 0

        exposure = int(base_exposure + regime_adjustment + breadth_adjustment)
        return max(0, min(100, exposure))

    def _determine_signal(self, regime: dict, breadth: dict, divergence: dict) -> str:
        """Determine trading signal."""
        regime_name = regime.get('regime', 'NEUTRAL')
        ma50_pct = breadth.get('above_ma50_pct', 50)
        div_type = divergence.get('type')

        # Bearish conditions
        if regime_name == 'BEARISH' or ma50_pct < 30:
            return 'RISK_OFF'

        # Bullish conditions
        if regime_name == 'BULLISH' and ma50_pct > 60 and div_type != 'BEARISH_DIV':
            return 'RISK_ON'

        # Divergence warning
        if div_type == 'BEARISH_DIV':
            return 'CAUTION'

        return 'CAUTION'

    def save(self, df: pd.DataFrame) -> Path:
        """Save market state to parquet."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self.output_path, index=False)
        logger.info(f"Saved market state to {self.output_path}")
        return self.output_path

    def run(self, date: Optional[str] = None) -> pd.DataFrame:
        """Calculate and save market state."""
        df = self.calculate(date)
        if not df.empty:
            self.save(df)
        return df


if __name__ == "__main__":
    calculator = MarketStateCalculator()
    result = calculator.run()
    if not result.empty:
        print("\nMarket State:")
        print(result.T)
