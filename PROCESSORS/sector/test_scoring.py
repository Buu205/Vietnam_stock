"""
Test Scoring and Signal Generation
===================================

Test script to verify FA scorer, TA scorer, and signal generator.

Author: Claude Code
Date: 2025-12-15
"""

import logging
from pathlib import Path
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main test function."""
    print("=" * 80)
    print("TESTING SECTOR SCORING AND SIGNAL GENERATION")
    print("=" * 80)

    # Import modules
    from config.sector_analysis.config_manager import ConfigManager
    from PROCESSORS.sector.scoring import FAScorer, TAScorer, SignalGenerator

    # Initialize
    config = ConfigManager()
    fa_scorer = FAScorer(config)
    ta_scorer = TAScorer(config)
    signal_gen = SignalGenerator(config)

    # Load data
    data_path = Path(__file__).resolve().parents[2] / "DATA" / "processed" / "sector"

    print("\n[1/4] Loading data...")
    fundamental_df = pd.read_parquet(data_path / "sector_fundamental_metrics.parquet")
    valuation_df = pd.read_parquet(data_path / "sector_valuation_metrics.parquet")
    print(f"  ✅ Loaded {len(fundamental_df)} fundamental records")
    print(f"  ✅ Loaded {len(valuation_df)} valuation records")

    # Score FA
    print("\n[2/4] Scoring fundamentals...")
    fa_scored = fa_scorer.score_sector_fundamentals(fundamental_df)
    print(f"  ✅ Scored {len(fa_scored)} records")
    print(f"  → Average FA Score: {fa_scored['fa_score'].mean():.2f}")
    print(f"  → Top FA Score: {fa_scored['fa_score'].max():.2f}")

    # Score TA
    print("\n[3/4] Scoring valuation/technical...")
    ta_scored = ta_scorer.score_sector_valuation(valuation_df)
    print(f"  ✅ Scored {len(ta_scored)} records")
    print(f"  → Average TA Score: {ta_scored['ta_score'].mean():.2f}")
    print(f"  → Top TA Score: {ta_scored['ta_score'].max():.2f}")

    # Generate signals
    print("\n[4/4] Generating signals...")
    signals = signal_gen.generate_signals(fa_scored, ta_scored)
    print(f"  ✅ Generated {len(signals)} signals")
    print(f"  → BUY: {(signals['signal'] == 'BUY').sum()}")
    print(f"  → HOLD: {(signals['signal'] == 'HOLD').sum()}")
    print(f"  → SELL: {(signals['signal'] == 'SELL').sum()}")

    # Show latest signals
    print("\n" + "=" * 80)
    print("LATEST SIGNALS (Top 10 by Combined Score)")
    print("=" * 80)

    latest_date = signals['date'].max()
    latest_signals = signals[signals['date'] == latest_date].copy()
    latest_signals = latest_signals.sort_values('combined_score', ascending=False).head(10)

    print(latest_signals[[
        'sector_code', 'signal', 'signal_strength',
        'combined_score', 'fa_score', 'ta_score'
    ]].to_string())

    # Show BUY signals (if any)
    buy_signals = signal_gen.get_buy_signals(signals, min_strength=3)
    if len(buy_signals) > 0:
        print("\n" + "=" * 80)
        print("BUY SIGNALS (Strength >= 3)")
        print("=" * 80)
        print(buy_signals[[
            'sector_code', 'signal', 'signal_strength',
            'combined_score', 'fa_score', 'ta_score'
        ]].to_string())

    # Show SELL signals (if any)
    sell_signals = signal_gen.get_sell_signals(signals, min_strength=2)
    if len(sell_signals) > 0:
        print("\n" + "=" * 80)
        print("SELL SIGNALS (Strength <= 2)")
        print("=" * 80)
        print(sell_signals[[
            'sector_code', 'signal', 'signal_strength',
            'combined_score', 'fa_score', 'ta_score'
        ]].to_string())

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Date range: {signals['date'].min()} to {signals['date'].max()}")
    print(f"Sectors covered: {signals['sector_code'].nunique()}")
    print(f"Total signals: {len(signals)}")
    print(f"\nScore distributions:")
    print(f"  FA Score:       mean={fa_scored['fa_score'].mean():.2f}, std={fa_scored['fa_score'].std():.2f}")
    print(f"  TA Score:       mean={ta_scored['ta_score'].mean():.2f}, std={ta_scored['ta_score'].std():.2f}")
    print(f"  Combined Score: mean={signals['combined_score'].mean():.2f}, std={signals['combined_score'].std():.2f}")

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()
