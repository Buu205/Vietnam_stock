"""
FA Scorer - Fundamental Analysis Scoring
=========================================

Tính điểm phân tích cơ bản cho các ngành.
Score fundamental analysis metrics for sectors.

This module scores fundamental metrics on a 0-100 scale based on
configurable thresholds and weights.

Scoring Components:
1. Growth Score (30%): Revenue YoY, Profit YoY
2. Profitability Score (40%): ROE, Net Margin, ROA
3. Efficiency Score (20%): Asset Turnover
4. Financial Health Score (10%): Debt to Equity

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


class FAScorer:
    """
    Fundamental Analysis Scorer.

    Chấm điểm các chỉ số tài chính cơ bản và tính điểm tổng hợp FA.

    Score fundamental metrics and calculate composite FA score.
    """

    def __init__(self, config_manager):
        """
        Initialize FA Scorer.

        Args:
            config_manager: ConfigManager instance for weights and preferences
        """
        self.config = config_manager

        # Load scoring thresholds
        self.thresholds = self._load_thresholds()

        # Get component weights from config (or use defaults)
        self.component_weights = self._get_component_weights()

        logger.info("FAScorer initialized")
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
            "growth": {
                "revenue_yoy": {
                    "excellent": 0.20,
                    "good": 0.10,
                    "neutral": 0.05,
                    "poor": 0.00,
                    "terrible": -0.05
                },
                "profit_yoy": {
                    "excellent": 0.25,
                    "good": 0.15,
                    "neutral": 0.05,
                    "poor": 0.00,
                    "terrible": -0.10
                }
            },
            "profitability": {
                "roe": {
                    "excellent": 0.20,
                    "good": 0.15,
                    "neutral": 0.10,
                    "poor": 0.05,
                    "terrible": 0.00
                },
                "net_margin": {
                    "excellent": 0.15,
                    "good": 0.10,
                    "neutral": 0.05,
                    "poor": 0.02,
                    "terrible": 0.00
                },
                "roa": {
                    "excellent": 0.10,
                    "good": 0.07,
                    "neutral": 0.05,
                    "poor": 0.02
                }
            },
            "efficiency": {
                "asset_turnover": {
                    "excellent": 1.5,
                    "good": 1.0,
                    "neutral": 0.7,
                    "poor": 0.5
                }
            },
            "financial_health": {
                "debt_to_equity": {
                    "excellent": 0.5,
                    "good": 1.0,
                    "neutral": 1.5,
                    "poor": 2.0,
                    "terrible": 3.0
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
            fa_config = config.get('fa_config', {})
            weights = fa_config.get('component_weights', {})

            # Return weights if valid, otherwise use defaults
            if weights:
                return weights
        except Exception as e:
            logger.warning(f"Could not load component weights from config: {e}")

        # Default weights
        return {
            'growth': 0.30,
            'profitability': 0.40,
            'efficiency': 0.20,
            'financial_health': 0.10
        }

    def score_sector_fundamentals(
        self,
        fundamental_df: pd.DataFrame,
        sector_code: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Score fundamental metrics for sectors.

        Tính điểm cho các chỉ số tài chính cơ bản.

        Args:
            fundamental_df: DataFrame from fa_aggregator.py output
            sector_code: Optional sector code to filter (if None, score all sectors)

        Returns:
            DataFrame with FA scores (0-100 scale)

        Output columns:
            - sector_code: str
            - report_date: date
            - growth_score: float (0-100)
            - profitability_score: float (0-100)
            - efficiency_score: float (0-100)
            - financial_health_score: float (0-100)
            - fa_score: float (0-100, weighted composite)
            - fa_rating: str (Excellent/Good/Neutral/Poor)
        """
        logger.info("=" * 80)
        logger.info("STARTING FA SCORING")
        logger.info("=" * 80)

        # Filter by sector if specified
        if sector_code:
            df = fundamental_df[fundamental_df['sector_code'] == sector_code].copy()
            logger.info(f"  Filtering for sector: {sector_code}")
        else:
            df = fundamental_df.copy()

        logger.info(f"  Processing {len(df)} sector-date records")

        # Score each component
        logger.info("\n[1/5] Scoring growth metrics...")
        df = self._score_growth(df)

        logger.info("[2/5] Scoring profitability metrics...")
        df = self._score_profitability(df)

        logger.info("[3/5] Scoring efficiency metrics...")
        df = self._score_efficiency(df)

        logger.info("[4/5] Scoring financial health metrics...")
        df = self._score_financial_health(df)

        logger.info("[5/5] Calculating composite FA score...")
        df = self._calculate_fa_score(df)

        # Add rating
        df['fa_rating'] = df['fa_score'].apply(self._get_rating)

        logger.info("=" * 80)
        logger.info(f"✅ FA SCORING COMPLETE: {len(df)} records scored")
        logger.info(f"   Average FA Score: {df['fa_score'].mean():.2f}")
        logger.info("=" * 80)

        return df

    def _score_growth(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score growth metrics (30% weight).

        Components:
        - Revenue YoY growth
        - Profit YoY growth

        Args:
            df: DataFrame with growth metrics

        Returns:
            DataFrame with growth_score column
        """
        # Score revenue growth
        df['revenue_growth_score'] = df['revenue_growth_yoy'].apply(
            lambda x: self._score_metric(x, self.thresholds['growth']['revenue_yoy'])
        )

        # Score profit growth
        df['profit_growth_score'] = df['profit_growth_yoy'].apply(
            lambda x: self._score_metric(x, self.thresholds['growth']['profit_yoy'])
        )

        # Composite growth score (equal weight for now)
        df['growth_score'] = (
            df['revenue_growth_score'] * 0.5 +
            df['profit_growth_score'] * 0.5
        )

        return df

    def _score_profitability(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score profitability metrics (40% weight).

        Components:
        - ROE (Return on Equity)
        - Net Margin
        - ROA (Return on Assets)

        Args:
            df: DataFrame with profitability metrics

        Returns:
            DataFrame with profitability_score column
        """
        # Score ROE
        df['roe_score'] = df['roe'].apply(
            lambda x: self._score_metric(x, self.thresholds['profitability']['roe'])
        )

        # Score net margin
        df['net_margin_score'] = df['net_margin'].apply(
            lambda x: self._score_metric(x, self.thresholds['profitability']['net_margin'])
        )

        # Score ROA
        df['roa_score'] = df['roa'].apply(
            lambda x: self._score_metric(x, self.thresholds['profitability']['roa'])
        )

        # Composite profitability score (weighted: ROE 50%, Margin 30%, ROA 20%)
        df['profitability_score'] = (
            df['roe_score'] * 0.5 +
            df['net_margin_score'] * 0.3 +
            df['roa_score'] * 0.2
        )

        return df

    def _score_efficiency(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score efficiency metrics (20% weight).

        Components:
        - Asset Turnover (calculated as total_revenue / total_assets)

        Args:
            df: DataFrame with efficiency metrics

        Returns:
            DataFrame with efficiency_score column
        """
        # Calculate asset turnover if not present
        if 'asset_turnover' not in df.columns:
            df['asset_turnover'] = np.where(
                df['total_assets'] > 0,
                df['total_revenue'] / df['total_assets'],
                np.nan
            )

        # Score asset turnover
        df['asset_turnover_score'] = df['asset_turnover'].apply(
            lambda x: self._score_metric(x, self.thresholds['efficiency']['asset_turnover'])
        )

        # Efficiency score (only asset turnover for now)
        df['efficiency_score'] = df['asset_turnover_score']

        return df

    def _score_financial_health(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score financial health metrics (10% weight).

        Components:
        - Debt to Equity (lower is better!)

        Args:
            df: DataFrame with financial health metrics

        Returns:
            DataFrame with financial_health_score column
        """
        # Score debt to equity (note: lower is better, so we invert the score)
        df['debt_to_equity_score'] = df['debt_to_equity'].apply(
            lambda x: self._score_metric_inverse(x, self.thresholds['financial_health']['debt_to_equity'])
        )

        # Financial health score
        df['financial_health_score'] = df['debt_to_equity_score']

        return df

    def _calculate_fa_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate composite FA score as weighted sum.

        FA Score = (growth * 30%) + (profitability * 40%) + (efficiency * 20%) + (health * 10%)

        Args:
            df: DataFrame with component scores

        Returns:
            DataFrame with fa_score column
        """
        df['fa_score'] = (
            df['growth_score'] * self.component_weights['growth'] +
            df['profitability_score'] * self.component_weights['profitability'] +
            df['efficiency_score'] * self.component_weights['efficiency'] +
            df['financial_health_score'] * self.component_weights['financial_health']
        )

        # Ensure score is in 0-100 range
        df['fa_score'] = df['fa_score'].clip(0, 100)

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

        # Extract threshold values
        excellent = thresholds.get('excellent', float('inf'))
        good = thresholds.get('good', 0)
        neutral = thresholds.get('neutral', 0)
        poor = thresholds.get('poor', 0)
        terrible = thresholds.get('terrible', float('-inf'))

        # Score based on thresholds
        if value >= excellent:
            return 100.0
        elif value >= good:
            # Linear interpolation between good (70) and excellent (100)
            return 70 + 30 * (value - good) / (excellent - good)
        elif value >= neutral:
            # Linear interpolation between neutral (50) and good (70)
            return 50 + 20 * (value - neutral) / (good - neutral)
        elif value >= poor:
            # Linear interpolation between poor (30) and neutral (50)
            return 30 + 20 * (value - poor) / (neutral - poor)
        elif value >= terrible:
            # Linear interpolation between terrible (0) and poor (30)
            return 0 + 30 * (value - terrible) / (poor - terrible)
        else:
            return 0.0

    def _score_metric_inverse(self, value: float, thresholds: Dict[str, float]) -> float:
        """
        Score a metric using thresholds (lower is better).

        For metrics where lower is better (e.g., debt_to_equity).

        Args:
            value: Metric value
            thresholds: Dictionary with threshold levels

        Returns:
            Score between 0 and 100
        """
        if pd.isna(value):
            return 50.0  # Neutral score for missing data

        # Extract threshold values (note: for inverse, excellent is lowest)
        excellent = thresholds.get('excellent', 0)
        good = thresholds.get('good', 0)
        neutral = thresholds.get('neutral', 0)
        poor = thresholds.get('poor', 0)
        terrible = thresholds.get('terrible', float('inf'))

        # Score based on thresholds (inverted)
        if value <= excellent:
            return 100.0
        elif value <= good:
            # Linear interpolation between excellent (100) and good (70)
            return 100 - 30 * (value - excellent) / (good - excellent)
        elif value <= neutral:
            # Linear interpolation between good (70) and neutral (50)
            return 70 - 20 * (value - good) / (neutral - good)
        elif value <= poor:
            # Linear interpolation between neutral (50) and poor (30)
            return 50 - 20 * (value - neutral) / (poor - neutral)
        elif value <= terrible:
            # Linear interpolation between poor (30) and terrible (0)
            return 30 - 30 * (value - poor) / (terrible - poor)
        else:
            return 0.0

    def _get_rating(self, score: float) -> str:
        """
        Convert numeric score to rating.

        Args:
            score: FA score (0-100)

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
        report_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get top N sectors by FA score.

        Args:
            scored_df: DataFrame with FA scores
            top_n: Number of top sectors to return
            report_date: Optional report date filter

        Returns:
            DataFrame with top sectors
        """
        df = scored_df.copy()

        # Filter by report date if specified
        if report_date:
            df = df[df['report_date'] == report_date]
        else:
            # Use most recent date
            latest_date = df['report_date'].max()
            df = df[df['report_date'] == latest_date]

        # Sort by FA score and return top N
        return df.nlargest(top_n, 'fa_score')


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
    scorer = FAScorer(config)

    # Load fundamental data
    fundamental_path = Path(__file__).resolve().parents[3] / "DATA" / "processed" / "sector" / "sector_fundamental_metrics.parquet"

    try:
        fundamental_df = pd.read_parquet(fundamental_path)
        logger.info(f"Loaded {len(fundamental_df)} fundamental records")

        # Score fundamentals
        scored_df = scorer.score_sector_fundamentals(fundamental_df)

        # Show top sectors
        print("\n" + "=" * 80)
        print("TOP 10 SECTORS BY FA SCORE (Latest Date)")
        print("=" * 80)
        top_sectors = scorer.get_top_sectors(scored_df, top_n=10)
        print(top_sectors[['sector_code', 'report_date', 'fa_score', 'fa_rating', 'growth_score', 'profitability_score']])

        print(f"\n{'=' * 80}")
        print(f"✅ SUCCESS: FA scoring complete")
        print(f"   Scored {len(scored_df)} records")
        print(f"   Average FA Score: {scored_df['fa_score'].mean():.2f}")
        print(f"{'=' * 80}")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
