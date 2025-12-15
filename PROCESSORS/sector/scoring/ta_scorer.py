"""
TA Scorer - Technical Analysis & Valuation Scoring
==================================================

Tính điểm phân tích kỹ thuật và định giá cho các ngành.
Score technical analysis and valuation metrics for sectors.

This module scores valuation and momentum metrics on a 0-100 scale
based on configurable thresholds and weights.

Scoring Components:
1. Valuation Score (50%): PE Percentile, PB Percentile (lower is better!)
2. Momentum Score (30%): Price changes, sector strength
3. Breadth Score (20%): Ticker participation

Author: Claude Code
Date: 2025-12-15
Version: 1.0.0
"""

import logging
import json
from pathlib import Path
from typing import Dict, Optional, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class TAScorer:
    """
    Technical Analysis & Valuation Scorer.

    Chấm điểm các chỉ số định giá và kỹ thuật.

    Score valuation and technical metrics.
    """

    def __init__(self, config_manager):
        """
        Initialize TA Scorer.

        Args:
            config_manager: ConfigManager instance for weights and preferences
        """
        self.config = config_manager

        # Load scoring thresholds
        self.thresholds = self._load_thresholds()

        # Get component weights from config (or use defaults)
        self.component_weights = self._get_component_weights()

        logger.info("TAScorer initialized")
        logger.info(f"  Component weights: {self.component_weights}")

    def _load_thresholds(self) -> Dict[str, Any]:
        """
        Load scoring thresholds from JSON file.

        Returns:
            Dictionary with scoring thresholds
        """
        threshold_file = Path(__file__).resolve().parents[3] / "config" / "sector_analysis" / "scoring_thresholds.json"

        try:
            with open(threshold_file, 'r', encoding='utf-8') as f:
                thresholds = json.load(f)
            logger.info(f"  ✅ Loaded thresholds from {threshold_file}")
            return thresholds
        except Exception as e:
            logger.error(f"  ❌ Error loading thresholds: {e}")
            return self._get_default_thresholds()

    def _get_default_thresholds(self) -> Dict[str, Any]:
        """
        Get default scoring thresholds if file not found.

        Returns:
            Dictionary with default thresholds
        """
        return {
            "valuation": {
                "pe_percentile": {
                    "very_cheap": 10,
                    "cheap": 25,
                    "fair": 50,
                    "expensive": 75,
                    "very_expensive": 90
                },
                "pb_percentile": {
                    "very_cheap": 10,
                    "cheap": 25,
                    "fair": 50,
                    "expensive": 75,
                    "very_expensive": 90
                }
            },
            "momentum": {
                "price_change_20d": {
                    "strong_up": 0.10,
                    "up": 0.05,
                    "neutral": 0.00,
                    "down": -0.05,
                    "strong_down": -0.10
                }
            }
        }

    def _get_component_weights(self) -> Dict[str, float]:
        """
        Get component weights from config.

        Returns:
            Dictionary with component weights
        """
        try:
            config = self.config.get_active_config()
            ta_config = config.get('ta_config', {})
            weights = ta_config.get('component_weights', {})

            # Return weights if valid, otherwise use defaults
            if weights:
                return weights
        except Exception as e:
            logger.warning(f"Could not load component weights from config: {e}")

        # Default weights
        return {
            'valuation': 0.50,
            'momentum': 0.30,
            'breadth': 0.20
        }

    def score_sector_valuation(
        self,
        valuation_df: pd.DataFrame,
        sector_code: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Score valuation metrics for sectors.

        Tính điểm cho các chỉ số định giá.

        Args:
            valuation_df: DataFrame from ta_aggregator.py output
            sector_code: Optional sector code to filter

        Returns:
            DataFrame with TA scores (0-100 scale)

        Output columns:
            - sector_code: str
            - date: date
            - valuation_score: float (0-100, lower percentile = higher score!)
            - momentum_score: float (0-100)
            - breadth_score: float (0-100)
            - ta_score: float (0-100, weighted composite)
            - ta_rating: str (Excellent/Good/Neutral/Poor)
        """
        logger.info("=" * 80)
        logger.info("STARTING TA SCORING")
        logger.info("=" * 80)

        # Filter by sector if specified
        if sector_code:
            df = valuation_df[valuation_df['sector_code'] == sector_code].copy()
            logger.info(f"  Filtering for sector: {sector_code}")
        else:
            df = valuation_df.copy()

        logger.info(f"  Processing {len(df)} sector-date records")

        # Score each component
        logger.info("\n[1/4] Scoring valuation metrics...")
        df = self._score_valuation(df)

        logger.info("[2/4] Scoring momentum metrics...")
        df = self._score_momentum(df)

        logger.info("[3/4] Scoring breadth metrics...")
        df = self._score_breadth(df)

        logger.info("[4/4] Calculating composite TA score...")
        df = self._calculate_ta_score(df)

        # Add rating
        df['ta_rating'] = df['ta_score'].apply(self._get_rating)

        logger.info("=" * 80)
        logger.info(f"✅ TA SCORING COMPLETE: {len(df)} records scored")
        logger.info(f"   Average TA Score: {df['ta_score'].mean():.2f}")
        logger.info("=" * 80)

        return df

    def _score_valuation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score valuation metrics (50% weight).

        IMPORTANT: Lower percentile = cheaper = higher score!

        Components:
        - PE Percentile (5-year)
        - PB Percentile (5-year)

        Args:
            df: DataFrame with valuation metrics

        Returns:
            DataFrame with valuation_score column
        """
        # Score PE percentile (lower is better, so invert)
        df['pe_percentile_score'] = df['pe_percentile_5y'].apply(
            lambda x: self._score_percentile_inverse(x, self.thresholds['valuation']['pe_percentile'])
        )

        # Score PB percentile (lower is better, so invert)
        df['pb_percentile_score'] = df['pb_percentile_5y'].apply(
            lambda x: self._score_percentile_inverse(x, self.thresholds['valuation']['pb_percentile'])
        )

        # Composite valuation score (equal weight for PE and PB)
        df['valuation_score'] = (
            df['pe_percentile_score'] * 0.5 +
            df['pb_percentile_score'] * 0.5
        )

        return df

    def _score_momentum(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score momentum metrics (30% weight).

        Components:
        - 20-day price change
        - Sector strength (avg_price vs moving average)

        Args:
            df: DataFrame with momentum metrics

        Returns:
            DataFrame with momentum_score column
        """
        # Calculate 20-day price change
        df = df.sort_values(['sector_code', 'date'])
        df['price_change_20d'] = (
            df.groupby('sector_code')['avg_price']
            .pct_change(periods=20)
        )

        # Score price change
        df['price_change_score'] = df['price_change_20d'].apply(
            lambda x: self._score_metric(x, self.thresholds['momentum']['price_change_20d'])
        )

        # Calculate sector strength (price vs 50-day MA)
        df['ma_50'] = (
            df.groupby('sector_code')['avg_price']
            .transform(lambda x: x.rolling(window=50, min_periods=1).mean())
        )

        df['sector_strength'] = np.where(
            df['ma_50'] > 0,
            (df['avg_price'] - df['ma_50']) / df['ma_50'],
            0
        )

        # Score sector strength (same thresholds as price change)
        df['sector_strength_score'] = df['sector_strength'].apply(
            lambda x: self._score_metric(x, self.thresholds['momentum']['price_change_20d'])
        )

        # Composite momentum score (price change 60%, strength 40%)
        df['momentum_score'] = (
            df['price_change_score'] * 0.6 +
            df['sector_strength_score'] * 0.4
        )

        return df

    def _score_breadth(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score breadth metrics (20% weight).

        Components:
        - Ticker participation (ticker_count relative to max)
        - Volume trend

        Args:
            df: DataFrame with breadth metrics

        Returns:
            DataFrame with breadth_score column
        """
        # Calculate ticker participation (% of max tickers in sector)
        max_tickers = df.groupby('sector_code')['ticker_count'].transform('max')
        df['ticker_participation'] = np.where(
            max_tickers > 0,
            df['ticker_count'] / max_tickers,
            0
        )

        # Score ticker participation (0-100 scale, direct mapping)
        df['ticker_participation_score'] = df['ticker_participation'] * 100

        # Calculate volume trend (20-day change)
        df['volume_change_20d'] = (
            df.groupby('sector_code')['total_volume']
            .pct_change(periods=20)
        )

        # Score volume trend (using momentum thresholds)
        df['volume_trend_score'] = df['volume_change_20d'].apply(
            lambda x: self._score_metric(x, self.thresholds['momentum']['price_change_20d'])
        )

        # Composite breadth score (participation 70%, volume 30%)
        df['breadth_score'] = (
            df['ticker_participation_score'] * 0.7 +
            df['volume_trend_score'] * 0.3
        )

        return df

    def _calculate_ta_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate composite TA score as weighted sum.

        TA Score = (valuation * 50%) + (momentum * 30%) + (breadth * 20%)

        Args:
            df: DataFrame with component scores

        Returns:
            DataFrame with ta_score column
        """
        df['ta_score'] = (
            df['valuation_score'] * self.component_weights['valuation'] +
            df['momentum_score'] * self.component_weights['momentum'] +
            df['breadth_score'] * self.component_weights['breadth']
        )

        # Ensure score is in 0-100 range
        df['ta_score'] = df['ta_score'].clip(0, 100)

        return df

    def _score_metric(self, value: float, thresholds: Dict[str, float]) -> float:
        """
        Score a metric using thresholds (higher is better).

        Args:
            value: Metric value
            thresholds: Dictionary with threshold levels

        Returns:
            Score between 0 and 100
        """
        if pd.isna(value):
            return 50.0  # Neutral score for missing data

        # Get threshold keys and values (sorted descending)
        levels = sorted(thresholds.items(), key=lambda x: x[1], reverse=True)

        if not levels:
            return 50.0

        # If value exceeds highest threshold, return 100
        if value >= levels[0][1]:
            return 100.0

        # If value below lowest threshold, return 0
        if value <= levels[-1][1]:
            return 0.0

        # Find the two thresholds that bracket the value
        for i in range(len(levels) - 1):
            upper_val = levels[i][1]
            lower_val = levels[i + 1][1]

            if value <= upper_val and value >= lower_val:
                # Linear interpolation
                # Map thresholds to score range
                upper_score = 100 - (i * 100 / (len(levels) - 1))
                lower_score = 100 - ((i + 1) * 100 / (len(levels) - 1))

                # Interpolate
                score = lower_score + (upper_score - lower_score) * (value - lower_val) / (upper_val - lower_val)
                return score

        return 50.0

    def _score_percentile_inverse(self, value: float, thresholds: Dict[str, float]) -> float:
        """
        Score percentile (lower percentile = higher score).

        For valuation metrics where lower percentile means cheaper/better.

        Args:
            value: Percentile value (0-100)
            thresholds: Dictionary with threshold levels

        Returns:
            Score between 0 and 100
        """
        if pd.isna(value):
            return 50.0  # Neutral score for missing data

        # Extract threshold values
        very_cheap = thresholds.get('very_cheap', 10)
        cheap = thresholds.get('cheap', 25)
        fair = thresholds.get('fair', 50)
        expensive = thresholds.get('expensive', 75)
        very_expensive = thresholds.get('very_expensive', 90)

        # Score based on percentile (inverted: low percentile = high score)
        if value <= very_cheap:
            return 100.0  # Very cheap = excellent
        elif value <= cheap:
            # Linear interpolation between very cheap (100) and cheap (80)
            return 100 - 20 * (value - very_cheap) / (cheap - very_cheap)
        elif value <= fair:
            # Linear interpolation between cheap (80) and fair (50)
            return 80 - 30 * (value - cheap) / (fair - cheap)
        elif value <= expensive:
            # Linear interpolation between fair (50) and expensive (30)
            return 50 - 20 * (value - fair) / (expensive - fair)
        elif value <= very_expensive:
            # Linear interpolation between expensive (30) and very expensive (0)
            return 30 - 30 * (value - expensive) / (very_expensive - expensive)
        else:
            return 0.0  # Very expensive = poor

    def _get_rating(self, score: float) -> str:
        """
        Convert numeric score to rating.

        Args:
            score: TA score (0-100)

        Returns:
            Rating string
        """
        if pd.isna(score):
            return "N/A"
        elif score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Neutral"
        else:
            return "Poor"

    def get_top_sectors(
        self,
        scored_df: pd.DataFrame,
        top_n: int = 5,
        date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get top N sectors by TA score.

        Args:
            scored_df: DataFrame with TA scores
            top_n: Number of top sectors to return
            date: Optional date filter

        Returns:
            DataFrame with top sectors
        """
        df = scored_df.copy()

        # Filter by date if specified
        if date:
            df = df[df['date'] == date]
        else:
            # Use most recent date
            latest_date = df['date'].max()
            df = df[df['date'] == latest_date]

        # Sort by TA score and return top N
        return df.nlargest(top_n, 'ta_score')


# Main execution for testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Import dependencies
    from config.sector_analysis.config_manager import ConfigManager

    # Initialize
    config = ConfigManager()
    scorer = TAScorer(config)

    # Load valuation data
    valuation_path = Path(__file__).resolve().parents[3] / "DATA" / "processed" / "sector" / "sector_valuation_metrics.parquet"

    try:
        valuation_df = pd.read_parquet(valuation_path)
        logger.info(f"Loaded {len(valuation_df)} valuation records")

        # Score valuation
        scored_df = scorer.score_sector_valuation(valuation_df)

        # Show top sectors
        print("\n" + "=" * 80)
        print("TOP 10 SECTORS BY TA SCORE (Latest Date)")
        print("=" * 80)
        top_sectors = scorer.get_top_sectors(scored_df, top_n=10)
        print(top_sectors[['sector_code', 'date', 'ta_score', 'ta_rating', 'valuation_score', 'momentum_score']])

        print(f"\n{'=' * 80}")
        print(f"✅ SUCCESS: TA scoring complete")
        print(f"   Scored {len(scored_df)} records")
        print(f"   Average TA Score: {scored_df['ta_score'].mean():.2f}")
        print(f"{'=' * 80}")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
