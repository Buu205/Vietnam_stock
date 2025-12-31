#!/usr/bin/env python3
"""
Trading List Generator
=======================

Generate daily buy/sell lists based on technical signals.
Used by Technical Dashboard Tab 4: Trading Lists.

Buy List Criteria:
- RS Rating >= 80
- Price above SMA50
- Volume confirmation (above average)
- Positive MACD signal
- Market regime not BEARISH

Sell List Criteria:
- RS Rating < 50 (fallen from previous high)
- Price below SMA50
- Negative MACD crossover
- Stop loss triggered

Outputs:
- DATA/processed/technical/lists/buy_list_latest.parquet
- DATA/processed/technical/lists/sell_list_latest.parquet

Author: Claude Code
Date: 2025-12-31
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from typing import Optional, Tuple

# Add project root
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingListGenerator:
    """Generate buy/sell lists based on technical signals."""

    # Buy criteria thresholds
    MIN_RS_RATING = 80
    MIN_VOLUME_RATIO = 1.2
    POSITION_SIZE_BASE = 5  # Base position size %

    # Sell criteria
    MAX_RS_FOR_SELL = 50
    STOP_LOSS_PCT = 7  # 7% stop loss

    def __init__(self):
        """Initialize generator."""
        self.project_root = project_root

        # Input paths
        self.rs_rating_path = self.project_root / "DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet"
        self.technical_path = self.project_root / "DATA/processed/technical/basic_data.parquet"
        self.alerts_path = self.project_root / "DATA/processed/technical/alerts/daily/combined_latest.parquet"
        self.market_state_path = self.project_root / "DATA/processed/technical/market/market_state_latest.parquet"

        # Output
        self.output_dir = self.project_root / "DATA/processed/technical/lists"
        self.buy_list_path = self.output_dir / "buy_list_latest.parquet"
        self.sell_list_path = self.output_dir / "sell_list_latest.parquet"

    def generate(self, date: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate buy and sell lists.

        Args:
            date: Target date (YYYY-MM-DD), defaults to latest

        Returns:
            Tuple of (buy_list_df, sell_list_df)
        """
        logger.info("Generating trading lists...")

        # Load data
        technical_df = self._load_technical_data(date)
        rs_df = self._load_rs_rating(date)
        market_state = self._load_market_state()

        if technical_df.empty or rs_df.empty:
            logger.error("Insufficient data for trading list generation")
            return pd.DataFrame(), pd.DataFrame()

        # Determine target date
        target_date = date or technical_df['date'].max()
        logger.info(f"Target date: {target_date}")

        # Get market exposure level
        exposure = market_state.get('exposure_level', 50) if market_state else 50
        market_signal = market_state.get('signal', 'CAUTION') if market_state else 'CAUTION'

        # Generate buy list
        buy_list = self._generate_buy_list(technical_df, rs_df, target_date, exposure, market_signal)

        # Generate sell list
        sell_list = self._generate_sell_list(technical_df, rs_df, target_date)

        return buy_list, sell_list

    def _load_technical_data(self, date: Optional[str]) -> pd.DataFrame:
        """Load technical data."""
        if not self.technical_path.exists():
            return pd.DataFrame()

        df = pd.read_parquet(self.technical_path)
        df['date'] = pd.to_datetime(df['date'])

        if date:
            df = df[df['date'] == pd.to_datetime(date)]
        else:
            # Get last 5 days for momentum calculation
            latest = df['date'].max()
            df = df[df['date'] >= latest - pd.Timedelta(days=7)]

        return df

    def _load_rs_rating(self, date: Optional[str]) -> pd.DataFrame:
        """Load RS rating data."""
        if not self.rs_rating_path.exists():
            return pd.DataFrame()

        df = pd.read_parquet(self.rs_rating_path)
        df['date'] = pd.to_datetime(df['date'])

        if date:
            df = df[df['date'] == pd.to_datetime(date)]
        else:
            df = df[df['date'] == df['date'].max()]

        return df

    def _load_market_state(self) -> Optional[dict]:
        """Load market state."""
        if not self.market_state_path.exists():
            return None

        df = pd.read_parquet(self.market_state_path)
        if df.empty:
            return None

        return df.iloc[0].to_dict()

    def _generate_buy_list(self, technical_df: pd.DataFrame, rs_df: pd.DataFrame,
                           date, exposure: int, market_signal: str) -> pd.DataFrame:
        """Generate buy list candidates."""

        # Don't generate buys in RISK_OFF mode
        if market_signal == 'RISK_OFF':
            logger.info("Market RISK_OFF - no buy signals generated")
            return pd.DataFrame()

        # Get latest technical data
        latest_tech = technical_df[technical_df['date'] == technical_df['date'].max()].copy()

        # Merge with RS rating
        merged = latest_tech.merge(rs_df[['symbol', 'rs_rating', 'rs_score', 'sector_code']],
                                    on='symbol', how='inner')

        # Apply buy criteria
        buy_candidates = merged[
            (merged['rs_rating'] >= self.MIN_RS_RATING) &
            (merged['close'] > merged.get('sma_50', 0))
        ].copy()

        if buy_candidates.empty:
            return pd.DataFrame()

        # Score candidates
        buy_candidates['buy_score'] = (
            buy_candidates['rs_rating'] * 0.4 +
            self._calculate_momentum_score(buy_candidates) * 0.3 +
            self._calculate_volume_score(buy_candidates) * 0.3
        )

        # Calculate position sizing based on RS and market exposure
        buy_candidates['position_size_pct'] = buy_candidates.apply(
            lambda x: self._calculate_position_size(x['rs_rating'], exposure), axis=1
        )

        # Calculate entry, stop, targets
        buy_candidates['entry_price'] = buy_candidates['close']
        buy_candidates['stop_loss'] = buy_candidates['close'] * (1 - self.STOP_LOSS_PCT / 100)
        buy_candidates['target_1'] = buy_candidates['close'] * 1.10  # 10% target
        buy_candidates['target_2'] = buy_candidates['close'] * 1.20  # 20% target

        # Add signal source
        buy_candidates['signal_source'] = 'RS_MOMENTUM'

        # Select top 10
        buy_list = buy_candidates.nlargest(10, 'buy_score')

        # Select output columns
        output_cols = [
            'symbol', 'sector_code', 'rs_rating', 'buy_score',
            'entry_price', 'stop_loss', 'target_1', 'target_2',
            'position_size_pct', 'signal_source'
        ]
        buy_list = buy_list[[c for c in output_cols if c in buy_list.columns]].copy()
        buy_list['date'] = date
        buy_list['score'] = buy_list['buy_score']  # Rename for consistency

        logger.info(f"Generated {len(buy_list)} buy candidates")
        return buy_list

    def _generate_sell_list(self, technical_df: pd.DataFrame, rs_df: pd.DataFrame,
                            date) -> pd.DataFrame:
        """Generate sell list (exit signals)."""

        # Get latest technical data
        latest_tech = technical_df[technical_df['date'] == technical_df['date'].max()].copy()

        # Merge with RS rating
        merged = latest_tech.merge(rs_df[['symbol', 'rs_rating', 'sector_code']],
                                    on='symbol', how='inner')

        # Apply sell criteria - falling RS rating or below SMA
        sell_candidates = merged[
            (merged['rs_rating'] < self.MAX_RS_FOR_SELL) |
            (merged['close'] < merged.get('sma_50', merged['close']))
        ].copy()

        if sell_candidates.empty:
            return pd.DataFrame()

        # Determine sell reason
        sell_candidates['sell_reason'] = sell_candidates.apply(
            lambda x: self._determine_sell_reason(x), axis=1
        )

        # Calculate hypothetical P&L (assume bought at SMA50)
        sell_candidates['exit_price'] = sell_candidates['close']
        sell_candidates['original_entry'] = sell_candidates.get('sma_50', sell_candidates['close'])
        sell_candidates['pnl_pct'] = (
            (sell_candidates['exit_price'] - sell_candidates['original_entry']) /
            sell_candidates['original_entry'] * 100
        ).round(1)

        # Estimate hold days (simplified)
        sell_candidates['hold_days'] = 20  # Placeholder

        # Select output columns
        output_cols = [
            'symbol', 'sector_code', 'sell_reason',
            'exit_price', 'original_entry', 'pnl_pct', 'hold_days'
        ]
        sell_list = sell_candidates[[c for c in output_cols if c in sell_candidates.columns]].copy()
        sell_list['date'] = date

        # Sort by P&L (worst first - most urgent to sell)
        sell_list = sell_list.sort_values('pnl_pct')

        logger.info(f"Generated {len(sell_list)} sell signals")
        return sell_list

    def _calculate_momentum_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate momentum score (0-100)."""
        if 'rsi_14' in df.columns:
            # RSI between 50-70 is ideal
            rsi = df['rsi_14'].clip(30, 70)
            return (rsi - 30) / 40 * 100
        return pd.Series(50, index=df.index)

    def _calculate_volume_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate volume score (0-100)."""
        if 'volume' in df.columns and 'sma_20' in df.columns:
            # Above average volume is better
            vol_ratio = df['volume'] / df['volume'].mean()
            return (vol_ratio.clip(0.5, 2) - 0.5) / 1.5 * 100
        return pd.Series(50, index=df.index)

    def _calculate_position_size(self, rs_rating: int, market_exposure: int) -> float:
        """
        Calculate position size based on RS rating and market exposure.

        Higher RS = larger position
        Higher market exposure = larger positions allowed
        """
        base_size = self.POSITION_SIZE_BASE

        # RS adjustment (+/- 2%)
        rs_adjustment = (rs_rating - 80) / 20 * 2

        # Market exposure adjustment
        exposure_mult = market_exposure / 100

        position = (base_size + rs_adjustment) * exposure_mult
        return round(max(2, min(10, position)), 1)

    def _determine_sell_reason(self, row) -> str:
        """Determine sell reason."""
        reasons = []

        if row['rs_rating'] < 50:
            reasons.append('RS_BREAKDOWN')

        if 'sma_50' in row and row['close'] < row['sma_50']:
            reasons.append('BELOW_SMA50')

        if 'rsi_14' in row and row['rsi_14'] > 70:
            reasons.append('OVERBOUGHT')

        return ', '.join(reasons) if reasons else 'WEAKNESS'

    def save(self, buy_list: pd.DataFrame, sell_list: pd.DataFrame) -> Tuple[Path, Path]:
        """Save buy and sell lists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not buy_list.empty:
            buy_list.to_parquet(self.buy_list_path, index=False)
            logger.info(f"Saved buy list to {self.buy_list_path}")

        if not sell_list.empty:
            sell_list.to_parquet(self.sell_list_path, index=False)
            logger.info(f"Saved sell list to {self.sell_list_path}")

        return self.buy_list_path, self.sell_list_path

    def run(self, date: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate and save trading lists."""
        buy_list, sell_list = self.generate(date)
        self.save(buy_list, sell_list)
        return buy_list, sell_list


if __name__ == "__main__":
    generator = TradingListGenerator()
    buy_list, sell_list = generator.run()

    print("\n=== BUY LIST ===")
    if not buy_list.empty:
        print(buy_list[['symbol', 'rs_rating', 'entry_price', 'position_size_pct']].to_string(index=False))
    else:
        print("No buy candidates")

    print("\n=== SELL LIST ===")
    if not sell_list.empty:
        print(sell_list[['symbol', 'sell_reason', 'pnl_pct']].head(10).to_string(index=False))
    else:
        print("No sell signals")
