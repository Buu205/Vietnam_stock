"""
TADashboardService - Unified service for Technical Dashboard
============================================================

Singleton service with caching for all TA Dashboard data needs.

Author: Claude Code
Date: 2025-12-25
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from WEBAPP.core.models.market_state import MarketState, BreadthHistory


# ==================== SINGLETON PATTERN ====================

@st.cache_resource
def get_ta_service() -> 'TADashboardService':
    """
    Get singleton TADashboardService instance.
    Call from main dashboard, pass to all components.
    """
    return TADashboardService()


class TADashboardService:
    """Unified service for Technical Dashboard"""

    DATA_ROOT = Path("DATA/processed/technical")

    def __init__(self):
        # Lazy loading - no preload
        pass

    # ==================== MARKET LAYER ====================

    def get_market_state(self) -> MarketState:
        """Get current market state with regime and breadth"""
        vnindex = self._load_vnindex()
        breadth = self._load_market_breadth()

        latest_vn = vnindex.iloc[-1]
        latest_br = breadth.iloc[-1]

        # Regime detection
        ema9 = latest_vn.get('ema9', latest_vn.get('ema_9', 0))
        ema21 = latest_vn.get('ema21', latest_vn.get('ema_21', 0))
        regime = self._get_regime(ema9, ema21)

        # Breadth values
        ma20_pct = latest_br.get('above_ma20_pct', latest_br.get('pct_above_ma20', 0))
        ma50_pct = latest_br.get('above_ma50_pct', latest_br.get('pct_above_ma50', 0))
        ma100_pct = latest_br.get('above_ma100_pct', latest_br.get('pct_above_ma100', 0))

        # Exposure level
        exposure = self._calculate_exposure(regime, ma20_pct)

        # Signal
        signal = "RISK_ON" if exposure >= 60 else ("RISK_OFF" if exposure == 0 else "CAUTION")

        return MarketState(
            date=latest_vn['date'],
            vnindex_close=latest_vn['close'],
            vnindex_change_pct=latest_vn.get('change_pct', 0),
            regime=regime,
            ema9=ema9,
            ema21=ema21,
            breadth_ma20_pct=ma20_pct,
            breadth_ma50_pct=ma50_pct,
            breadth_ma100_pct=ma100_pct,
            ad_ratio=latest_br.get('ad_ratio', 1.0),
            exposure_level=exposure,
            divergence_type=None,
            divergence_strength=0,
            signal=signal
        )

    def get_breadth_history(self, days: int = 180) -> BreadthHistory:
        """Get historical breadth for line chart"""
        breadth = self._load_market_breadth().tail(days)
        vnindex = self._load_vnindex().tail(days)

        # Merge on date
        merged = breadth.merge(
            vnindex[['date', 'close']].rename(columns={'close': 'vnindex_close'}),
            on='date',
            how='left'
        )

        return BreadthHistory(
            date=merged['date'].tolist(),
            ma20_pct=merged.get('above_ma20_pct', merged.get('pct_above_ma20', pd.Series([0]))).tolist(),
            ma50_pct=merged.get('above_ma50_pct', merged.get('pct_above_ma50', pd.Series([0]))).tolist(),
            ma100_pct=merged.get('above_ma100_pct', merged.get('pct_above_ma100', pd.Series([0]))).tolist(),
            vnindex_close=merged['vnindex_close'].tolist()
        )

    # ==================== SECTOR LAYER ====================

    def get_sector_ranking(self) -> Optional[pd.DataFrame]:
        """Get sector ranking with strength scores"""
        try:
            df = self._load_sector_breadth()
            if df.empty:
                return None

            # Get latest date
            latest_date = df['date'].max()
            latest = df[df['date'] == latest_date].copy()

            # Sort by strength score
            if 'strength_score' in latest.columns:
                latest = latest.sort_values('strength_score', ascending=False)
                latest['rank'] = range(1, len(latest) + 1)

            return latest
        except Exception:
            return None

    def get_sector_money_flow(self, timeframe: str = '1D') -> Optional[pd.DataFrame]:
        """Get sector money flow data"""
        try:
            path = self.DATA_ROOT / f"money_flow/sector_money_flow_{timeframe.lower()}.parquet"
            if not path.exists():
                return None
            return pd.read_parquet(path)
        except Exception:
            return None

    def get_sector_rs_for_rrg(self, smooth: int = 3, trail_days: int = 5) -> Optional[pd.DataFrame]:
        """Get sector RS data for RRG chart"""
        try:
            df = self._load_sector_breadth()
            if df.empty:
                return None

            # Calculate RS ratio and momentum per sector
            result = []
            for sector in df['sector_code'].unique():
                sector_df = df[df['sector_code'] == sector].sort_values('date').tail(trail_days + 10)

                if len(sector_df) < 5:
                    continue

                # RS Ratio = sector strength relative to market average
                sector_df['rs_ratio'] = sector_df['strength_score'] / sector_df['strength_score'].mean()

                # RS Momentum = rate of change
                sector_df['rs_momentum'] = sector_df['rs_ratio'].diff(5) * 100

                # Smooth
                sector_df['rs_ratio_smooth'] = sector_df['rs_ratio'].rolling(smooth, min_periods=1).mean()
                sector_df['rs_momentum_smooth'] = sector_df['rs_momentum'].rolling(smooth, min_periods=1).mean()

                # Quadrant
                sector_df['quadrant'] = sector_df.apply(
                    lambda r: self._determine_quadrant(r['rs_ratio_smooth'], r['rs_momentum_smooth']),
                    axis=1
                )

                result.append(sector_df.tail(trail_days))

            if not result:
                return None

            return pd.concat(result, ignore_index=True)
        except Exception:
            return None

    # ==================== STOCK LAYER ====================

    def get_signals(self, signal_type: str = None) -> Optional[pd.DataFrame]:
        """Get trading signals from alerts"""
        try:
            df = self._load_signals()
            if df is None or df.empty:
                return None

            if signal_type:
                df = df[df['signal_type'] == signal_type]

            return df
        except Exception:
            return None

    def get_stock_rs_rating_history(self, days: int = 30) -> Optional[pd.DataFrame]:
        """Get RS Rating history for heatmap"""
        try:
            path = self.DATA_ROOT / "rs_rating/stock_rs_rating_daily.parquet"
            if not path.exists():
                return None

            df = pd.read_parquet(path)
            df['date'] = pd.to_datetime(df['date'])

            # Filter to last N days
            cutoff = df['date'].max() - pd.Timedelta(days=days)
            return df[df['date'] >= cutoff]
        except Exception:
            return None

    def get_sector_list(self) -> List[str]:
        """Get list of all sectors"""
        return self._load_sector_list()

    # ==================== PRIVATE METHODS (with Caching) ====================

    @staticmethod
    @st.cache_data(ttl=300)
    def _load_market_breadth() -> pd.DataFrame:
        """Load market breadth with 5-min cache"""
        path = Path("DATA/processed/technical/market_breadth/market_breadth_daily.parquet")
        if not path.exists():
            return pd.DataFrame()
        df = pd.read_parquet(path)
        df['date'] = pd.to_datetime(df['date'])
        return df

    @staticmethod
    @st.cache_data(ttl=300)
    def _load_vnindex() -> pd.DataFrame:
        """Load VN-Index indicators with 5-min cache"""
        path = Path("DATA/processed/technical/vnindex/vnindex_indicators.parquet")
        if not path.exists():
            return pd.DataFrame()
        df = pd.read_parquet(path)
        df['date'] = pd.to_datetime(df['date'])
        return df

    @staticmethod
    @st.cache_data(ttl=300)
    def _load_sector_breadth() -> pd.DataFrame:
        """Load sector breadth with 5-min cache"""
        path = Path("DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet")
        if not path.exists():
            return pd.DataFrame()
        df = pd.read_parquet(path)
        df['date'] = pd.to_datetime(df['date'])
        return df

    @staticmethod
    @st.cache_data(ttl=60)
    def _load_signals() -> pd.DataFrame:
        """Load all signal types and combine with proper labels"""
        alert_dir = Path("DATA/processed/technical/alerts/daily")
        all_signals = []

        # 1. Candlestick Patterns - most useful signal type
        patterns_path = alert_dir / "patterns_latest.parquet"
        if patterns_path.exists():
            df = pd.read_parquet(patterns_path)
            df['signal_type'] = 'patterns'
            df['type_label'] = df['pattern_name'].fillna('Pattern')
            df['direction'] = df['signal'].map({
                'BULLISH': 'BUY', 'BEARISH': 'SELL'
            }).fillna('NEUTRAL')
            all_signals.append(df[['symbol', 'date', 'signal_type', 'type_label', 'direction', 'price', 'strength']])

        # 2. MA Crossover
        ma_path = alert_dir / "ma_crossover_latest.parquet"
        if ma_path.exists():
            df = pd.read_parquet(ma_path)
            df['signal_type'] = 'ma_crossover'
            df['type_label'] = df['alert_type'].replace({
                'MA_CROSS_ABOVE': 'MA Cross Up',
                'MA_CROSS_BELOW': 'MA Cross Down'
            })
            df['direction'] = df['signal'].map({
                'BULLISH': 'BUY', 'BUY': 'BUY',
                'BEARISH': 'SELL', 'SELL': 'SELL'
            }).fillna('NEUTRAL')
            df['strength'] = 0.7  # Default strength
            all_signals.append(df[['symbol', 'date', 'signal_type', 'type_label', 'direction', 'price', 'strength']])

        # 3. Volume Spike
        vol_path = alert_dir / "volume_spike_latest.parquet"
        if vol_path.exists():
            df = pd.read_parquet(vol_path)
            df['signal_type'] = 'volume_spike'
            df['type_label'] = 'Vol Spike ' + df['volume_ratio'].round(1).astype(str) + 'x'
            # Handle various signal formats: BULLISH, BEARISH, NOISE, WATCH, etc.
            def map_vol_signal(sig):
                if not isinstance(sig, str):
                    return 'NEUTRAL'
                sig = sig.upper()
                if 'BULLISH' in sig or sig == 'BUY':
                    return 'BUY'
                elif 'BEARISH' in sig or sig == 'SELL':
                    return 'SELL'
                return 'NEUTRAL'
            df['direction'] = df['signal'].apply(map_vol_signal)
            df['strength'] = df['confidence'].fillna(0.5)
            all_signals.append(df[['symbol', 'date', 'signal_type', 'type_label', 'direction', 'price', 'strength']])

        # 4. Breakout
        breakout_path = alert_dir / "breakout_latest.parquet"
        if breakout_path.exists():
            df = pd.read_parquet(breakout_path)
            df['signal_type'] = 'breakout'
            df['type_label'] = df['alert_type'].replace({
                'BREAKOUT_UP': 'Breakout ↑',
                'BREAKDOWN': 'Breakdown ↓'
            })
            # Handle various signal formats: BULLISH_BREAKOUT, BEARISH_BREAKDOWN, etc.
            def map_breakout_signal(sig):
                if not isinstance(sig, str):
                    return 'NEUTRAL'
                sig = sig.upper()
                if 'BULLISH' in sig or 'UP' in sig or sig == 'BUY':
                    return 'BUY'
                elif 'BEARISH' in sig or 'DOWN' in sig or sig == 'SELL':
                    return 'SELL'
                return 'NEUTRAL'
            df['direction'] = df['signal'].apply(map_breakout_signal)
            df['strength'] = 0.8  # Default strength
            all_signals.append(df[['symbol', 'date', 'signal_type', 'type_label', 'direction', 'price', 'strength']])

        if not all_signals:
            return pd.DataFrame()

        # Combine all signals
        combined = pd.concat(all_signals, ignore_index=True)
        return combined.sort_values(['direction', 'symbol'], ascending=[True, True])

    @staticmethod
    @st.cache_data(ttl=300)
    def _load_sector_list() -> List[str]:
        """Load sector list ONCE, shared across all tabs"""
        path = Path("DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet")
        if not path.exists():
            return []
        df = pd.read_parquet(path)
        return sorted(df['sector_code'].unique().tolist())

    def _get_regime(self, ema9: float, ema21: float) -> str:
        if ema9 > ema21 * 1.005:
            return 'BULLISH'
        elif ema9 < ema21 * 0.995:
            return 'BEARISH'
        return 'NEUTRAL'

    def _calculate_exposure(self, regime: str, breadth: float) -> int:
        if regime == 'BEARISH':
            return 0
        if breadth >= 70:
            return 100
        elif breadth >= 55:
            return 80
        elif breadth >= 40:
            return 60
        elif breadth >= 25:
            return 40
        return 20

    def _determine_quadrant(self, rs_ratio: float, rs_momentum: float) -> str:
        """Determine RRG quadrant"""
        if pd.isna(rs_ratio) or pd.isna(rs_momentum):
            return 'UNKNOWN'
        if rs_ratio > 1 and rs_momentum > 0:
            return 'LEADING'
        elif rs_ratio > 1 and rs_momentum <= 0:
            return 'WEAKENING'
        elif rs_ratio <= 1 and rs_momentum <= 0:
            return 'LAGGING'
        else:
            return 'IMPROVING'
