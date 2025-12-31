#!/usr/bin/env python3
"""
Sector Ranking Calculator
==========================

Calculate composite sector ranking based on multiple factors:
- RS Score (relative strength)
- Money Flow Score
- Breadth Score (% above MAs)
- Momentum Score

Used by Technical Dashboard Tab 2: Sector Rotation.

Output: DATA/processed/technical/sector/ranking_latest.parquet

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


class SectorRankingCalculator:
    """Calculate sector rankings with composite scoring."""

    # Scoring weights
    WEIGHTS = {
        'rs_score': 0.30,
        'money_flow_score': 0.25,
        'breadth_score': 0.25,
        'momentum_score': 0.20
    }

    def __init__(self):
        """Initialize calculator."""
        self.project_root = project_root

        # Input paths
        self.rs_rating_path = self.project_root / "DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet"
        self.money_flow_path = self.project_root / "DATA/processed/technical/money_flow/sector_money_flow_1d.parquet"
        self.breadth_path = self.project_root / "DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet"
        self.technical_path = self.project_root / "DATA/processed/technical/basic_data.parquet"

        # Output
        self.output_dir = self.project_root / "DATA/processed/technical/sector"
        self.output_path = self.output_dir / "ranking_latest.parquet"

    def calculate(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate sector ranking.

        Args:
            date: Target date (YYYY-MM-DD), defaults to latest

        Returns:
            DataFrame with sector rankings
        """
        logger.info("Calculating sector rankings...")

        # Get RS score by sector
        rs_scores = self._calculate_rs_scores(date)

        # Get money flow scores
        money_flow_scores = self._calculate_money_flow_scores(date)

        # Get breadth scores
        breadth_scores = self._calculate_breadth_scores(date)

        # Get momentum scores
        momentum_scores = self._calculate_momentum_scores(date)

        # Merge all scores
        all_sectors = set(rs_scores.keys()) | set(money_flow_scores.keys()) | \
                      set(breadth_scores.keys()) | set(momentum_scores.keys())

        if not all_sectors:
            logger.error("No sector data available")
            return pd.DataFrame()

        results = []
        for sector in all_sectors:
            rs = rs_scores.get(sector, 50)
            mf = money_flow_scores.get(sector, 50)
            br = breadth_scores.get(sector, 50)
            mo = momentum_scores.get(sector, 50)

            # Calculate composite score
            composite = (
                rs * self.WEIGHTS['rs_score'] +
                mf * self.WEIGHTS['money_flow_score'] +
                br * self.WEIGHTS['breadth_score'] +
                mo * self.WEIGHTS['momentum_score']
            )

            # Determine trend
            trend = self._determine_trend(composite, rs, mf)

            results.append({
                'sector_code': sector,
                'date': date or pd.Timestamp.now().strftime('%Y-%m-%d'),
                'score': round(composite, 1),
                'rs_score': round(rs, 1),
                'money_flow_score': round(mf, 1),
                'breadth_score': round(br, 1),
                'momentum_score': round(mo, 1),
                'trend': trend
            })

        df = pd.DataFrame(results)

        # Handle NaN scores
        df['score'] = df['score'].fillna(0)

        # Add rank
        df['rank'] = df['score'].rank(ascending=False, na_option='bottom').astype(int)
        df = df.sort_values('rank')

        logger.info(f"Calculated rankings for {len(df)} sectors")
        return df

    def _calculate_rs_scores(self, date: Optional[str]) -> dict:
        """Calculate RS scores by sector (average of top stocks)."""
        if not self.rs_rating_path.exists():
            logger.warning("RS rating file not found")
            return {}

        df = pd.read_parquet(self.rs_rating_path)
        df['date'] = pd.to_datetime(df['date'])

        if date:
            df = df[df['date'] == pd.to_datetime(date)]
        else:
            df = df[df['date'] == df['date'].max()]

        if df.empty:
            return {}

        # Group by sector, take average RS rating
        sector_rs = df.groupby('sector_code')['rs_rating'].mean()

        # Normalize to 0-100 scale
        min_rs = sector_rs.min()
        max_rs = sector_rs.max()
        if max_rs > min_rs:
            sector_rs = (sector_rs - min_rs) / (max_rs - min_rs) * 100
        else:
            sector_rs = pd.Series(50, index=sector_rs.index)

        return sector_rs.to_dict()

    def _calculate_money_flow_scores(self, date: Optional[str]) -> dict:
        """Calculate money flow scores by sector."""
        if not self.money_flow_path.exists():
            logger.warning("Money flow file not found")
            return {}

        df = pd.read_parquet(self.money_flow_path)
        df['date'] = pd.to_datetime(df['date'])

        if date:
            df = df[df['date'] == pd.to_datetime(date)]
        else:
            df = df[df['date'] == df['date'].max()]

        if df.empty:
            return {}

        # Use inflow_pct as score
        if 'inflow_pct' in df.columns:
            # Normalize inflow_pct (-100 to 100) to (0 to 100)
            df['score'] = (df['inflow_pct'] + 100) / 2
            return df.set_index('sector_code')['score'].to_dict()

        return {}

    def _calculate_breadth_scores(self, date: Optional[str]) -> dict:
        """Calculate breadth scores by sector."""
        if not self.breadth_path.exists():
            logger.warning("Breadth file not found")
            return {}

        df = pd.read_parquet(self.breadth_path)
        df['date'] = pd.to_datetime(df['date'])

        if date:
            df = df[df['date'] == pd.to_datetime(date)]
        else:
            df = df[df['date'] == df['date'].max()]

        if df.empty:
            return {}

        # Use above_ma50_pct as breadth score
        if 'above_ma50_pct' in df.columns:
            return df.set_index('sector_code')['above_ma50_pct'].to_dict()
        elif 'above_ma20_pct' in df.columns:
            return df.set_index('sector_code')['above_ma20_pct'].to_dict()

        return {}

    def _calculate_momentum_scores(self, date: Optional[str]) -> dict:
        """Calculate momentum scores by sector."""
        if not self.technical_path.exists():
            return {}

        df = pd.read_parquet(self.technical_path)
        df['date'] = pd.to_datetime(df['date'])

        # Get last 20 days
        latest_date = df['date'].max()
        df = df[df['date'] >= latest_date - pd.Timedelta(days=30)]

        if df.empty:
            return {}

        # Calculate 20-day return by symbol
        symbol_returns = df.groupby('symbol').apply(
            lambda x: x.sort_values('date')['close'].iloc[-1] / x.sort_values('date')['close'].iloc[0] - 1
            if len(x) > 1 else 0
        )

        # Map symbols to sectors
        try:
            from config.registries import SectorRegistry
            sector_reg = SectorRegistry()
        except Exception:
            return {}

        sector_returns = {}
        for symbol, ret in symbol_returns.items():
            try:
                info = sector_reg.get_ticker(symbol)
                sector = info.get('sector', 'Unknown')
                if sector not in sector_returns:
                    sector_returns[sector] = []
                sector_returns[sector].append(ret)
            except Exception:
                continue

        # Average returns per sector, normalize to 0-100
        scores = {}
        for sector, returns in sector_returns.items():
            avg_return = np.mean(returns)
            # Normalize: -20% to +20% -> 0 to 100
            score = (avg_return + 0.20) / 0.40 * 100
            scores[sector] = max(0, min(100, score))

        return scores

    def _determine_trend(self, composite: float, rs: float, mf: float) -> str:
        """Determine sector trend."""
        if composite >= 70 and rs >= 60:
            return 'LEADING'
        elif composite >= 50 and mf >= 60:
            return 'IMPROVING'
        elif composite < 30:
            return 'LAGGING'
        elif composite < 50 and mf < 40:
            return 'WEAKENING'
        return 'NEUTRAL'

    def save(self, df: pd.DataFrame) -> Path:
        """Save rankings to parquet."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self.output_path, index=False)
        logger.info(f"Saved sector rankings to {self.output_path}")
        return self.output_path

    def run(self, date: Optional[str] = None) -> pd.DataFrame:
        """Calculate and save sector rankings."""
        df = self.calculate(date)
        if not df.empty:
            self.save(df)
        return df


if __name__ == "__main__":
    calculator = SectorRankingCalculator()
    result = calculator.run()
    if not result.empty:
        print("\nTop 10 Sectors:")
        print(result.head(10)[['rank', 'sector_code', 'score', 'trend']])
