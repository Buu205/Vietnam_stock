"""
Sector Processor - Main Orchestrator for Sector Analysis
=========================================================

Bộ xử lý ngành - Điều phối toàn bộ quy trình phân tích ngành.
Main orchestrator for complete sector analysis pipeline.

This module orchestrates the entire sector analysis pipeline:
1. Load configurations and registries
2. Run FA aggregation → sector fundamental metrics
3. Run TA aggregation → sector valuation metrics
4. Run FA scoring → fundamental scores
5. Run TA scoring → technical/valuation scores
6. Run signal generation → combined scores + BUY/SELL/HOLD signals
7. Save all outputs to parquet files

Pipeline Flow:
    ConfigManager + Registries
            ↓
    FAAggregator → sector_fundamental_metrics.parquet
            ↓
    TAAggregator → sector_valuation_metrics.parquet
            ↓
    FAScorer → FA scores
            ↓
    TAScorer → TA scores
            ↓
    SignalGenerator → sector_combined_scores.parquet

Author: Claude Code
Date: 2025-12-15
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Any
import pandas as pd
from datetime import datetime, timedelta

# Import registries
from config.registries import MetricRegistry, SectorRegistry

# Import calculators/aggregators
from PROCESSORS.sector.calculators.fa_aggregator import FAAggregator
from PROCESSORS.sector.calculators.ta_aggregator import TAAggregator

# Import scorers
from PROCESSORS.sector.scoring.fa_scorer import FAScorer
from PROCESSORS.sector.scoring.ta_scorer import TAScorer
from PROCESSORS.sector.scoring.signal_generator import SignalGenerator

logger = logging.getLogger(__name__)


# Import ConfigManager
from config.sector_analysis.config_manager import ConfigManager


class SectorProcessor:
    """
    Sector Processor - Bộ Xử Lý Ngành.

    Main orchestrator that runs the complete sector analysis pipeline.
    Điều phối toàn bộ quy trình phân tích ngành.
    """

    def __init__(self):
        """
        Initialize Sector Processor.

        Loads all required registries and creates aggregator/scorer instances.
        """
        logger.info("=" * 80)
        logger.info("INITIALIZING SECTOR PROCESSOR")
        logger.info("=" * 80)

        # Step 1: Load registries
        logger.info("\n[1/6] Loading registries...")
        self.metric_reg = MetricRegistry()
        self.sector_reg = SectorRegistry()
        self.config = ConfigManager()
        logger.info("  ✅ Registries loaded")

        # Step 2: Initialize aggregators
        logger.info("\n[2/6] Initializing aggregators...")
        self.fa_aggregator = FAAggregator(
            config_manager=self.config,
            sector_registry=self.sector_reg,
            metric_registry=self.metric_reg
        )
        self.ta_aggregator = TAAggregator(
            config_manager=self.config,
            sector_registry=self.sector_reg
        )
        logger.info("  ✅ Aggregators initialized")

        # Step 3: Initialize scorers
        logger.info("\n[3/6] Initializing scorers...")
        self.fa_scorer = FAScorer(config_manager=self.config)
        self.ta_scorer = TAScorer(config_manager=self.config)
        self.signal_generator = SignalGenerator(config_manager=self.config)
        logger.info("  ✅ Scorers initialized")

        # Output path
        self.output_dir = Path.cwd() / "DATA" / "processed" / "sector"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("\n[4/6] Setting output directory...")
        logger.info(f"  Output: {self.output_dir}")

        logger.info("\n✅ SECTOR PROCESSOR READY")
        logger.info("=" * 80)

    def run_full_pipeline(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        report_date: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Run complete sector analysis pipeline.

        Chạy toàn bộ quy trình phân tích ngành.

        Args:
            start_date: Start date for analysis (YYYY-MM-DD)
            end_date: End date for analysis (YYYY-MM-DD)
            report_date: Specific report date for FA (overrides start/end)

        Returns:
            Dictionary containing all output DataFrames:
            {
                'fa_metrics': sector_fundamental_metrics DataFrame,
                'ta_metrics': sector_valuation_metrics DataFrame,
                'fa_scores': FA scores DataFrame,
                'ta_scores': TA scores DataFrame,
                'combined_scores': combined scores + signals DataFrame
            }

        Raises:
            Exception: If any step in the pipeline fails
        """
        logger.info("\n" + "=" * 80)
        logger.info("🚀 STARTING FULL SECTOR ANALYSIS PIPELINE")
        logger.info("=" * 80)

        start_time = datetime.now()
        results = {}

        try:
            # Step 1: Run FA Aggregation
            logger.info("\n" + "=" * 80)
            logger.info("[STEP 1/6] FUNDAMENTAL ANALYSIS AGGREGATION")
            logger.info("=" * 80)

            fa_metrics = self._run_fa_aggregation(report_date, start_date, end_date)
            results['fa_metrics'] = fa_metrics

            logger.info(f"\n✅ FA Aggregation complete: {len(fa_metrics)} records")
            logger.info(f"   Sectors: {fa_metrics['sector_code'].nunique()}")
            logger.info(f"   Date range: {fa_metrics['report_date'].min()} to {fa_metrics['report_date'].max()}")

            # Step 2: Run TA Aggregation
            logger.info("\n" + "=" * 80)
            logger.info("[STEP 2/6] TECHNICAL/VALUATION ANALYSIS AGGREGATION")
            logger.info("=" * 80)

            ta_metrics = self._run_ta_aggregation(start_date, end_date)
            results['ta_metrics'] = ta_metrics

            logger.info(f"\n✅ TA Aggregation complete: {len(ta_metrics)} records")
            logger.info(f"   Sectors: {ta_metrics['sector_code'].nunique()}")
            logger.info(f"   Date range: {ta_metrics['date'].min()} to {ta_metrics['date'].max()}")

            # Step 3: Run FA Scoring
            logger.info("\n" + "=" * 80)
            logger.info("[STEP 3/6] FUNDAMENTAL ANALYSIS SCORING")
            logger.info("=" * 80)

            fa_scores = self._run_fa_scoring(fa_metrics)
            results['fa_scores'] = fa_scores

            logger.info(f"\n✅ FA Scoring complete: {len(fa_scores)} records")
            logger.info(f"   Average FA score: {fa_scores['fa_score'].mean():.1f}")

            # Step 4: Run TA Scoring
            logger.info("\n" + "=" * 80)
            logger.info("[STEP 4/6] TECHNICAL/VALUATION SCORING")
            logger.info("=" * 80)

            ta_scores = self._run_ta_scoring(ta_metrics)
            results['ta_scores'] = ta_scores

            logger.info(f"\n✅ TA Scoring complete: {len(ta_scores)} records")
            logger.info(f"   Average TA score: {ta_scores['ta_score'].mean():.1f}")

            # Step 5: Run Signal Generation
            logger.info("\n" + "=" * 80)
            logger.info("[STEP 5/6] SIGNAL GENERATION (FA + TA COMBINATION)")
            logger.info("=" * 80)

            combined_scores = self._run_signal_generation(fa_scores, ta_scores)
            results['combined_scores'] = combined_scores

            logger.info(f"\n✅ Signal Generation complete: {len(combined_scores)} records")

            # Print signal distribution
            signal_dist = combined_scores['signal'].value_counts()
            logger.info("\n   Signal Distribution:")
            for signal, count in signal_dist.items():
                logger.info(f"     {signal}: {count} sectors")

            # Step 6: Save all outputs
            logger.info("\n" + "=" * 80)
            logger.info("[STEP 6/6] SAVING OUTPUTS")
            logger.info("=" * 80)

            output_files = self._save_outputs(results)

            logger.info("\n✅ All outputs saved:")
            for name, path in output_files.items():
                logger.info(f"   {name}: {path}")

            # Pipeline summary
            elapsed = (datetime.now() - start_time).total_seconds()

            logger.info("\n" + "=" * 80)
            logger.info("🎉 PIPELINE COMPLETE - SUCCESS")
            logger.info("=" * 80)
            logger.info(f"\n⏱️  Execution time: {elapsed:.1f} seconds")
            logger.info(f"\n📊 Results Summary:")
            logger.info(f"   FA Metrics: {len(fa_metrics)} records")
            logger.info(f"   TA Metrics: {len(ta_metrics)} records")
            logger.info(f"   Combined Scores: {len(combined_scores)} records")
            logger.info(f"   Sectors analyzed: {combined_scores['sector_code'].nunique()}")
            logger.info(f"\n📁 Output location: {self.output_dir}")
            logger.info("=" * 80)

            return results

        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.error("\n" + "=" * 80)
            logger.error("❌ PIPELINE FAILED")
            logger.error("=" * 80)
            logger.error(f"\n⏱️  Elapsed time: {elapsed:.1f} seconds")
            logger.error(f"\n💥 Error: {str(e)}")
            logger.error("=" * 80)
            raise

    def _run_fa_aggregation(
        self,
        report_date: Optional[str],
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> pd.DataFrame:
        """
        Run FA aggregation step.

        Args:
            report_date: Specific report date (overrides start/end)
            start_date: Start date for range
            end_date: End date for range

        Returns:
            FA metrics DataFrame
        """
        try:
            fa_metrics = self.fa_aggregator.aggregate_sector_fundamentals(
                report_date=report_date,
                start_date=start_date,
                end_date=end_date
            )

            if fa_metrics.empty:
                raise ValueError("FA aggregation returned no data!")

            return fa_metrics

        except Exception as e:
            logger.error(f"FA Aggregation failed: {e}")
            raise

    def _run_ta_aggregation(
        self,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> pd.DataFrame:
        """
        Run TA aggregation step.

        UPDATED (2025-12-15): Uses aggregate_sector_valuation() with full metrics
        (PE, PB, PS, EV/EBITDA) instead of v2 which only has PE/PB.

        Args:
            start_date: Start date for range
            end_date: End date for range

        Returns:
            TA metrics DataFrame with PE, PB, PS, EV/EBITDA
        """
        try:
            # Use full method with PE/PB/PS/EV_EBITDA
            ta_metrics = self.ta_aggregator.aggregate_sector_valuation(
                start_date=start_date,
                end_date=end_date
            )

            if ta_metrics.empty:
                raise ValueError("TA aggregation returned no data!")

            return ta_metrics

        except Exception as e:
            logger.error(f"TA Aggregation failed: {e}")
            raise

    def _run_fa_scoring(self, fa_metrics: pd.DataFrame) -> pd.DataFrame:
        """
        Run FA scoring step.

        Args:
            fa_metrics: FA metrics DataFrame

        Returns:
            FA scores DataFrame
        """
        try:
            fa_scores = self.fa_scorer.score_sector_fundamentals(fa_metrics)

            if fa_scores.empty:
                raise ValueError("FA scoring returned no data!")

            return fa_scores

        except Exception as e:
            logger.error(f"FA Scoring failed: {e}")
            raise

    def _run_ta_scoring(self, ta_metrics: pd.DataFrame) -> pd.DataFrame:
        """
        Run TA scoring step.

        Args:
            ta_metrics: TA metrics DataFrame

        Returns:
            TA scores DataFrame
        """
        try:
            ta_scores = self.ta_scorer.score_sector_valuation(ta_metrics)

            if ta_scores.empty:
                raise ValueError("TA scoring returned no data!")

            return ta_scores

        except Exception as e:
            logger.error(f"TA Scoring failed: {e}")
            raise

    def _run_signal_generation(
        self,
        fa_scores: pd.DataFrame,
        ta_scores: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Run signal generation step.

        Args:
            fa_scores: FA scores DataFrame
            ta_scores: TA scores DataFrame

        Returns:
            Combined scores + signals DataFrame
        """
        try:
            combined_scores = self.signal_generator.generate_signals(
                fa_scored_df=fa_scores,
                ta_scored_df=ta_scores
            )

            if combined_scores.empty:
                raise ValueError("Signal generation returned no data!")

            return combined_scores

        except Exception as e:
            logger.error(f"Signal Generation failed: {e}")
            raise

    def _save_outputs(self, results: Dict[str, pd.DataFrame]) -> Dict[str, Path]:
        """
        Save all output files.

        Args:
            results: Dictionary of DataFrames to save

        Returns:
            Dictionary of output file paths
        """
        output_files = {}

        try:
            # Save FA metrics
            if 'fa_metrics' in results:
                fa_path = self.output_dir / "sector_fundamental_metrics.parquet"
                results['fa_metrics'].to_parquet(fa_path, index=False)
                output_files['fa_metrics'] = fa_path
                logger.info(f"  ✅ Saved: sector_fundamental_metrics.parquet")

            # Save TA metrics
            if 'ta_metrics' in results:
                ta_path = self.output_dir / "sector_valuation_metrics.parquet"
                results['ta_metrics'].to_parquet(ta_path, index=False)
                output_files['ta_metrics'] = ta_path
                logger.info(f"  ✅ Saved: sector_valuation_metrics.parquet")

            # Save combined scores
            if 'combined_scores' in results:
                combined_path = self.output_dir / "sector_combined_scores.parquet"
                results['combined_scores'].to_parquet(combined_path, index=False)
                output_files['combined_scores'] = combined_path
                logger.info(f"  ✅ Saved: sector_combined_scores.parquet")

            return output_files

        except Exception as e:
            logger.error(f"Error saving outputs: {e}")
            raise


# Main execution for testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create processor
    processor = SectorProcessor()

    # Run pipeline (last 1 year for testing)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

    results = processor.run_full_pipeline(
        start_date=start_date,
        end_date=end_date
    )

    print("\n" + "=" * 80)
    print("✅ SUCCESS: Sector analysis pipeline complete")
    print("=" * 80)
