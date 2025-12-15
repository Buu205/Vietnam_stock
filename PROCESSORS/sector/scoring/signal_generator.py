"""
Signal Generator - FA+TA Combined Signal Generation
====================================================

Tạo tín hiệu mua/bán/giữ từ điểm FA và TA.
Generate BUY/HOLD/SELL signals from FA and TA scores.

This module combines FA and TA scores using configurable weights
and generates actionable trading signals.

Signal Logic:
- BUY: combined_score >= 70
- SELL: combined_score <= 30
- HOLD: 30 < combined_score < 70

Signal Strength: 1-5 stars based on score range

Author: Claude Code
Date: 2025-12-15
Version: 1.0.0
"""

import logging
import json
from pathlib import Path
from typing import Dict, Optional, Any, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class SignalGenerator:
    """
    Signal Generator for FA+TA Combined Analysis.

    Kết hợp điểm FA và TA để tạo tín hiệu giao dịch.

    Combine FA and TA scores to generate trading signals.
    """

    def __init__(self, config_manager):
        """
        Initialize Signal Generator.

        Args:
            config_manager: ConfigManager instance for weights and preferences
        """
        self.config = config_manager

        # Load sector-specific configs
        self.sector_configs = self._load_sector_configs()

        # Get default FA/TA weights
        self.default_weights = self._get_default_weights()

        logger.info("SignalGenerator initialized")
        logger.info(f"  Default FA/TA weights: {self.default_weights}")

    def _load_sector_configs(self) -> Dict[str, Any]:
        """
        Load sector-specific configuration.

        Returns:
            Dictionary with sector-specific configs
        """
        config_file = Path(__file__).resolve().parents[3] / "config" / "sector_analysis" / "sector_specific_config.json"

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                configs = json.load(f)
            logger.info(f"  ✅ Loaded sector configs from {config_file}")
            return configs
        except Exception as e:
            logger.warning(f"  ⚠️  Could not load sector configs: {e}")
            return {}

    def _get_default_weights(self) -> Dict[str, float]:
        """
        Get default FA/TA weights from config.

        Returns:
            Dictionary with fa_weight and ta_weight
        """
        try:
            config = self.config.get_active_config()
            composite_weights = config.get('composite_weights', {})

            if composite_weights:
                return {
                    'fa_weight': composite_weights.get('fundamental', 0.6),
                    'ta_weight': composite_weights.get('technical', 0.4)
                }
        except Exception as e:
            logger.warning(f"Could not load weights from config: {e}")

        # Default weights
        return {
            'fa_weight': 0.6,
            'ta_weight': 0.4
        }

    def generate_signals(
        self,
        fa_scored_df: pd.DataFrame,
        ta_scored_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Generate trading signals by combining FA and TA scores.

        Tạo tín hiệu giao dịch từ điểm FA và TA.

        Args:
            fa_scored_df: DataFrame with FA scores (from fa_scorer.py)
            ta_scored_df: DataFrame with TA scores (from ta_scorer.py)

        Returns:
            DataFrame with combined scores and signals

        Output columns:
            - sector_code: str
            - date: date
            - fa_score: float (0-100)
            - ta_score: float (0-100)
            - combined_score: float (0-100)
            - signal: str (BUY/HOLD/SELL)
            - signal_strength: int (1-5 stars)
            - signal_explanation: str (bilingual)
            - fa_weight: float (used for this sector)
            - ta_weight: float (used for this sector)
        """
        logger.info("=" * 80)
        logger.info("STARTING SIGNAL GENERATION")
        logger.info("=" * 80)

        # Step 1: Merge FA and TA scores
        logger.info("\n[1/4] Merging FA and TA scores...")
        merged_df = self._merge_scores(fa_scored_df, ta_scored_df)

        if merged_df.empty:
            logger.warning("No matching records between FA and TA data!")
            return pd.DataFrame()

        logger.info(f"  → {len(merged_df)} matching records found")

        # Step 2: Get sector-specific weights
        logger.info("\n[2/4] Applying sector-specific weights...")
        merged_df = self._apply_sector_weights(merged_df)

        # Step 3: Calculate combined score
        logger.info("\n[3/4] Calculating combined scores...")
        merged_df = self._calculate_combined_score(merged_df)

        # Step 4: Generate signals
        logger.info("\n[4/4] Generating signals...")
        merged_df = self._generate_signal(merged_df)
        merged_df = self._calculate_signal_strength(merged_df)
        merged_df = self._generate_explanation(merged_df)

        logger.info("=" * 80)
        logger.info(f"✅ SIGNAL GENERATION COMPLETE: {len(merged_df)} signals")
        logger.info(f"   BUY signals: {(merged_df['signal'] == 'BUY').sum()}")
        logger.info(f"   HOLD signals: {(merged_df['signal'] == 'HOLD').sum()}")
        logger.info(f"   SELL signals: {(merged_df['signal'] == 'SELL').sum()}")
        logger.info("=" * 80)

        return merged_df

    def _merge_scores(
        self,
        fa_df: pd.DataFrame,
        ta_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Merge FA and TA DataFrames.

        Match on sector_code and date (FA uses report_date, TA uses date).

        Args:
            fa_df: FA scores DataFrame
            ta_df: TA scores DataFrame

        Returns:
            Merged DataFrame
        """
        # Prepare FA data (select relevant columns)
        fa_cols = ['sector_code', 'report_date', 'fa_score', 'fa_rating',
                   'growth_score', 'profitability_score', 'efficiency_score', 'financial_health_score']
        fa_available = [col for col in fa_cols if col in fa_df.columns]
        fa_clean = fa_df[fa_available].copy()

        # Rename report_date to date for merging
        fa_clean = fa_clean.rename(columns={'report_date': 'date'})

        # Prepare TA data (select relevant columns)
        ta_cols = ['sector_code', 'date', 'ta_score', 'ta_rating',
                   'valuation_score', 'momentum_score', 'breadth_score',
                   'sector_pe', 'sector_pb', 'pe_percentile_5y', 'pb_percentile_5y']
        ta_available = [col for col in ta_cols if col in ta_df.columns]
        ta_clean = ta_df[ta_available].copy()

        # Convert dates to same type
        fa_clean['date'] = pd.to_datetime(fa_clean['date'])
        ta_clean['date'] = pd.to_datetime(ta_clean['date'])

        # Merge on sector_code and date
        merged = fa_clean.merge(
            ta_clean,
            on=['sector_code', 'date'],
            how='inner',
            suffixes=('_fa', '_ta')
        )

        return merged

    def _apply_sector_weights(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply sector-specific FA/TA weights.

        Args:
            df: Merged DataFrame

        Returns:
            DataFrame with fa_weight and ta_weight columns
        """
        def get_sector_weights(sector_code: str) -> Tuple[float, float]:
            """Get FA/TA weights for a sector."""
            # Check if sector has specific config
            if sector_code in self.sector_configs:
                sector_config = self.sector_configs[sector_code]
                weights = sector_config.get('fa_ta_weights', {})

                if weights:
                    return (
                        weights.get('fa_weight', self.default_weights['fa_weight']),
                        weights.get('ta_weight', self.default_weights['ta_weight'])
                    )

            # Use defaults
            return (
                self.default_weights['fa_weight'],
                self.default_weights['ta_weight']
            )

        # Apply weights for each sector
        df[['fa_weight', 'ta_weight']] = df['sector_code'].apply(
            lambda x: pd.Series(get_sector_weights(x))
        )

        return df

    def _calculate_combined_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate combined score from FA and TA.

        Formula: combined_score = (fa_score * fa_weight) + (ta_score * ta_weight)

        Args:
            df: DataFrame with FA and TA scores and weights

        Returns:
            DataFrame with combined_score column
        """
        df['combined_score'] = (
            df['fa_score'] * df['fa_weight'] +
            df['ta_score'] * df['ta_weight']
        )

        # Ensure in 0-100 range
        df['combined_score'] = df['combined_score'].clip(0, 100)

        return df

    def _generate_signal(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate BUY/HOLD/SELL signal based on combined score.

        Thresholds:
        - BUY: score >= 70
        - SELL: score <= 30
        - HOLD: 30 < score < 70

        Args:
            df: DataFrame with combined_score

        Returns:
            DataFrame with signal column
        """
        df['signal'] = df['combined_score'].apply(
            lambda x: 'BUY' if x >= 70 else ('SELL' if x <= 30 else 'HOLD')
        )

        return df

    def _calculate_signal_strength(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate signal strength (1-5 stars).

        Score ranges:
        - 90-100: 5 stars (Strong BUY)
        - 70-90: 4 stars (BUY)
        - 50-70: 3 stars (HOLD)
        - 30-50: 2 stars (SELL)
        - 0-30: 1 star (Strong SELL)

        Args:
            df: DataFrame with combined_score

        Returns:
            DataFrame with signal_strength column
        """
        def get_strength(score: float) -> int:
            if pd.isna(score):
                return 3  # Neutral
            elif score >= 90:
                return 5
            elif score >= 70:
                return 4
            elif score >= 50:
                return 3
            elif score >= 30:
                return 2
            else:
                return 1

        df['signal_strength'] = df['combined_score'].apply(get_strength)

        return df

    def _generate_explanation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate bilingual explanation for each signal.

        Args:
            df: DataFrame with signal and scores

        Returns:
            DataFrame with signal_explanation column
        """
        def create_explanation(row: pd.Series) -> str:
            signal = row['signal']
            strength = row['signal_strength']
            fa_score = row['fa_score']
            ta_score = row['ta_score']
            combined = row['combined_score']

            # Create explanation
            if signal == 'BUY':
                if strength == 5:
                    vi = f"MUA MẠNH: Điểm kết hợp {combined:.1f} (FA: {fa_score:.1f}, TA: {ta_score:.1f})"
                    en = f"STRONG BUY: Combined score {combined:.1f} (FA: {fa_score:.1f}, TA: {ta_score:.1f})"
                else:
                    vi = f"MUA: Điểm kết hợp {combined:.1f} (FA: {fa_score:.1f}, TA: {ta_score:.1f})"
                    en = f"BUY: Combined score {combined:.1f} (FA: {fa_score:.1f}, TA: {ta_score:.1f})"
            elif signal == 'SELL':
                if strength == 1:
                    vi = f"BÁN MẠNH: Điểm kết hợp {combined:.1f} (FA: {fa_score:.1f}, TA: {ta_score:.1f})"
                    en = f"STRONG SELL: Combined score {combined:.1f} (FA: {fa_score:.1f}, TA: {ta_score:.1f})"
                else:
                    vi = f"BÁN: Điểm kết hợp {combined:.1f} (FA: {fa_score:.1f}, TA: {ta_score:.1f})"
                    en = f"SELL: Combined score {combined:.1f} (FA: {fa_score:.1f}, TA: {ta_score:.1f})"
            else:  # HOLD
                vi = f"GIỮ: Điểm kết hợp {combined:.1f} (FA: {fa_score:.1f}, TA: {ta_score:.1f})"
                en = f"HOLD: Combined score {combined:.1f} (FA: {fa_score:.1f}, TA: {ta_score:.1f})"

            return f"{vi} | {en}"

        df['signal_explanation'] = df.apply(create_explanation, axis=1)

        return df

    def get_buy_signals(
        self,
        signals_df: pd.DataFrame,
        date: Optional[str] = None,
        min_strength: int = 3
    ) -> pd.DataFrame:
        """
        Get BUY signals filtered by date and strength.

        Args:
            signals_df: DataFrame with signals
            date: Optional date filter (if None, use latest)
            min_strength: Minimum signal strength (1-5)

        Returns:
            Filtered DataFrame with BUY signals
        """
        df = signals_df.copy()

        # Filter by date
        if date:
            df = df[df['date'] == date]
        else:
            latest_date = df['date'].max()
            df = df[df['date'] == latest_date]

        # Filter BUY signals with minimum strength
        df = df[
            (df['signal'] == 'BUY') &
            (df['signal_strength'] >= min_strength)
        ]

        # Sort by combined score descending
        return df.sort_values('combined_score', ascending=False)

    def get_sell_signals(
        self,
        signals_df: pd.DataFrame,
        date: Optional[str] = None,
        min_strength: int = 2
    ) -> pd.DataFrame:
        """
        Get SELL signals filtered by date and strength.

        Args:
            signals_df: DataFrame with signals
            date: Optional date filter
            min_strength: Minimum signal strength (1-5, but inverted for SELL)

        Returns:
            Filtered DataFrame with SELL signals
        """
        df = signals_df.copy()

        # Filter by date
        if date:
            df = df[df['date'] == date]
        else:
            latest_date = df['date'].max()
            df = df[df['date'] == latest_date]

        # Filter SELL signals with maximum strength (lower is stronger for SELL)
        df = df[
            (df['signal'] == 'SELL') &
            (df['signal_strength'] <= min_strength)
        ]

        # Sort by combined score ascending (lowest first)
        return df.sort_values('combined_score', ascending=True)


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
    generator = SignalGenerator(config)

    # Load FA and TA scored data
    data_path = Path(__file__).resolve().parents[3] / "DATA" / "processed" / "sector"

    try:
        # For testing, we need to score FA and TA first
        from PROCESSORS.sector.scoring.fa_scorer import FAScorer
        from PROCESSORS.sector.scoring.ta_scorer import TAScorer

        # Load raw data
        fundamental_df = pd.read_parquet(data_path / "sector_fundamental_metrics.parquet")
        valuation_df = pd.read_parquet(data_path / "sector_valuation_metrics.parquet")

        # Score FA and TA
        fa_scorer = FAScorer(config)
        ta_scorer = TAScorer(config)

        fa_scored = fa_scorer.score_sector_fundamentals(fundamental_df)
        ta_scored = ta_scorer.score_sector_valuation(valuation_df)

        # Generate signals
        signals_df = generator.generate_signals(fa_scored, ta_scored)

        # Show BUY signals
        print("\n" + "=" * 80)
        print("BUY SIGNALS (Latest Date, Strength >= 3)")
        print("=" * 80)
        buy_signals = generator.get_buy_signals(signals_df, min_strength=3)
        if len(buy_signals) > 0:
            print(buy_signals[['sector_code', 'date', 'signal', 'signal_strength', 'combined_score', 'fa_score', 'ta_score']])
        else:
            print("No BUY signals found")

        # Show SELL signals
        print("\n" + "=" * 80)
        print("SELL SIGNALS (Latest Date, Strength <= 2)")
        print("=" * 80)
        sell_signals = generator.get_sell_signals(signals_df, min_strength=2)
        if len(sell_signals) > 0:
            print(sell_signals[['sector_code', 'date', 'signal', 'signal_strength', 'combined_score', 'fa_score', 'ta_score']])
        else:
            print("No SELL signals found")

        print(f"\n{'=' * 80}")
        print(f"✅ SUCCESS: Signal generation complete")
        print(f"   Total signals: {len(signals_df)}")
        print(f"   BUY: {(signals_df['signal'] == 'BUY').sum()}")
        print(f"   HOLD: {(signals_df['signal'] == 'HOLD').sum()}")
        print(f"   SELL: {(signals_df['signal'] == 'SELL').sum()}")
        print(f"{'=' * 80}")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
