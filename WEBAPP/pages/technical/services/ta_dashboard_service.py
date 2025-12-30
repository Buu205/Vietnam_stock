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

    def get_market_state(self) -> Optional[MarketState]:
        """Get current market state with regime and breadth"""
        vnindex = self._load_vnindex()
        breadth = self._load_market_breadth()

        # Handle empty data - return None if no data available
        if vnindex.empty or breadth.empty:
            return None

        latest_vn = vnindex.iloc[-1]
        latest_br = breadth.iloc[-1]

        # Previous day breadth for recovery detection
        prev_ma20_pct = None
        prev_ma50_pct = None
        if len(breadth) >= 2:
            prev_br = breadth.iloc[-2]
            prev_ma20_pct = prev_br.get('above_ma20_pct', prev_br.get('pct_above_ma20', None))
            prev_ma50_pct = prev_br.get('above_ma50_pct', prev_br.get('pct_above_ma50', None))

        # Regime detection
        ema9 = latest_vn.get('ema9', latest_vn.get('ema_9', 0))
        ema21 = latest_vn.get('ema21', latest_vn.get('ema_21', 0))
        regime = self._get_regime(ema9, ema21)

        # Breadth values
        ma20_pct = latest_br.get('above_ma20_pct', latest_br.get('pct_above_ma20', 0))
        ma50_pct = latest_br.get('above_ma50_pct', latest_br.get('pct_above_ma50', 0))
        ma100_pct = latest_br.get('above_ma100_pct', latest_br.get('pct_above_ma100', 0))

        # Bottom Detection: Calculate higher lows pattern
        higher_lows = self._calculate_higher_lows(breadth)

        # Bottom Formation Stage detection
        bottom_stage = self._detect_bottom_stage(
            ma20_pct, ma50_pct, ma100_pct,
            higher_lows
        )

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
            prev_breadth_ma20_pct=prev_ma20_pct,
            prev_breadth_ma50_pct=prev_ma50_pct,
            ma20_higher_low=higher_lows['ma20_higher_low'],
            ma20_recent_low=higher_lows['ma20_recent_low'],
            ma20_prev_low=higher_lows['ma20_prev_low'],
            ma20_rising_from_low=higher_lows['ma20_rising_from_low'],
            ma50_higher_low=higher_lows['ma50_higher_low'],
            ma50_recent_low=higher_lows['ma50_recent_low'],
            ma50_prev_low=higher_lows['ma50_prev_low'],
            ma50_rising_from_low=higher_lows['ma50_rising_from_low'],
            bottom_stage=bottom_stage,
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
        """Get sector money flow data (latest date only)"""
        try:
            path = self.DATA_ROOT / f"money_flow/sector_money_flow_{timeframe.lower()}.parquet"
            if not path.exists():
                return None
            df = pd.read_parquet(path)
            # Filter to latest date only
            if 'date' in df.columns and not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                latest_date = df['date'].max()
                df = df[df['date'] == latest_date]
            return df
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
        """Load all signal types and combine with proper labels.

        Uses history files (9 days) instead of latest files (1 day)
        to enable proper date filtering in Stock Scanner.
        """
        # Use historical directory for multi-day data
        history_dir = Path("DATA/processed/technical/alerts/historical")
        daily_dir = Path("DATA/processed/technical/alerts/daily")
        all_signals = []

        # 1. Candlestick Patterns - most useful signal type
        patterns_path = history_dir / "patterns_history.parquet"
        if not patterns_path.exists():
            patterns_path = daily_dir / "patterns_latest.parquet"  # Fallback
        if patterns_path.exists():
            df = pd.read_parquet(patterns_path)
            df['signal_type'] = 'patterns'
            df['type_label'] = df['pattern_name'].fillna('Pattern')

            # JOIN trend data from basic_data for trend-aware signals
            basic_path = Path("DATA/processed/technical/basic_data.parquet")
            if basic_path.exists():
                basic_df = pd.read_parquet(basic_path, columns=[
                    'symbol', 'date', 'price_vs_sma20', 'price_vs_sma50',
                    'trading_value', 'volume', 'expected_trading_value', 'trading_value_diff'
                ])
                # Normalize dates for join
                basic_df['date'] = pd.to_datetime(basic_df['date']).dt.date
                df['date'] = pd.to_datetime(df['date']).dt.date
                df = df.merge(basic_df, on=['symbol', 'date'], how='left')

            # Classify trend based on SMA20/SMA50 position
            # Threshold: ±5% for clear trend, otherwise SIDEWAYS
            def classify_trend(row):
                sma20 = row.get('price_vs_sma20', 0) or 0
                sma50 = row.get('price_vs_sma50', 0) or 0
                if sma20 > 5 and sma50 > 5:
                    return 'STRONG_UP'
                elif sma20 > 2 and sma50 > 2:
                    return 'UPTREND'
                elif sma20 < -5 and sma50 < -5:
                    return 'STRONG_DOWN'
                elif sma20 < -2 and sma50 < -2:
                    return 'DOWNTREND'
                return 'SIDEWAYS'

            df['trend'] = df.apply(classify_trend, axis=1)

            # Pullback Strategy: TREND → PATTERN → SIGNAL
            def get_strategy_signal(row):
                pattern_signal = row['signal']
                trend = row['trend']
                pattern_name = row.get('pattern_name', '')

                # Doji is always NEUTRAL (indecision)
                if pattern_name == 'doji':
                    return 'NEUTRAL'

                # UPTREND patterns
                if trend in ['STRONG_UP', 'UPTREND']:
                    if pattern_signal == 'BULLISH':
                        return 'BUY'  # Trend continuation
                    elif pattern_signal == 'BEARISH':
                        return 'PULLBACK'  # Counter-trend, wait for support

                # DOWNTREND patterns
                elif trend in ['STRONG_DOWN', 'DOWNTREND']:
                    if pattern_signal == 'BEARISH':
                        return 'SELL'  # Trend continuation
                    elif pattern_signal == 'BULLISH':
                        return 'BOUNCE'  # Counter-trend, wait for resistance

                # SIDEWAYS: follow pattern with lighter conviction
                else:
                    if pattern_signal == 'BULLISH':
                        return 'BUY'
                    elif pattern_signal == 'BEARISH':
                        return 'SELL'

                return 'NEUTRAL'

            df['direction'] = df.apply(get_strategy_signal, axis=1)

            # Select columns (include trend, volume data for Phase 3+)
            cols = ['symbol', 'date', 'signal_type', 'type_label', 'direction', 'price', 'strength']
            optional_cols = ['trend', 'trading_value', 'volume', 'expected_trading_value', 'trading_value_diff',
                            'price_vs_sma20', 'price_vs_sma50']
            for col in optional_cols:
                if col in df.columns:
                    cols.append(col)
            all_signals.append(df[cols])

        # 2. MA Crossover
        ma_path = history_dir / "ma_crossover_history.parquet"
        if not ma_path.exists():
            ma_path = daily_dir / "ma_crossover_latest.parquet"  # Fallback
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
        vol_path = history_dir / "volume_spike_history.parquet"
        if not vol_path.exists():
            vol_path = daily_dir / "volume_spike_latest.parquet"  # Fallback
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
        breakout_path = history_dir / "breakout_history.parquet"
        if not breakout_path.exists():
            breakout_path = daily_dir / "breakout_latest.parquet"  # Fallback
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

        # Dedup: Keep highest strength signal per ticker+date
        # This prevents same stock showing both MUA and BÁN from different patterns
        combined = combined.sort_values('strength', ascending=False)
        combined = combined.drop_duplicates(subset=['symbol', 'date'], keep='first')

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

    def _calculate_higher_lows(self, breadth_df: pd.DataFrame) -> dict:
        """
        Detect "Higher Lows" pattern for MA20 and MA50 breadth.
        Higher lows = recent low > previous low → confirms uptrend forming.

        Logic:
        - MA20: Compare min of last 3 days with min of previous 3 days
        - MA50: Compare min of last 5 days with min of previous 5 days

        Returns:
            dict: {
                'ma20_higher_low': bool,      # True if MA20 forming higher lows
                'ma20_recent_low': float,     # Recent low value
                'ma20_prev_low': float,       # Previous low value
                'ma20_rising_from_low': bool, # Current > recent low
                'ma50_higher_low': bool,
                'ma50_recent_low': float,
                'ma50_prev_low': float,
                'ma50_rising_from_low': bool,
            }
        """
        result = {
            'ma20_higher_low': False,
            'ma20_recent_low': 0,
            'ma20_prev_low': 0,
            'ma20_rising_from_low': False,
            'ma50_higher_low': False,
            'ma50_recent_low': 0,
            'ma50_prev_low': 0,
            'ma50_rising_from_low': False,
        }

        if len(breadth_df) < 10:
            return result

        # Get column names
        ma20_col = 'above_ma20_pct' if 'above_ma20_pct' in breadth_df.columns else 'pct_above_ma20'
        ma50_col = 'above_ma50_pct' if 'above_ma50_pct' in breadth_df.columns else 'pct_above_ma50'

        # Get last 10 rows for MA50 analysis (need 10 = 5 recent + 5 previous)
        recent_10 = breadth_df.tail(10).copy()
        ma20_values = recent_10[ma20_col].tolist()
        ma50_values = recent_10[ma50_col].tolist()

        # MA20: Higher Lows detection (3-day windows)
        # Recent 3 days: [-3:-1] (indices 7,8,9 in 10-day array)
        # Previous 3 days: [-6:-3] (indices 4,5,6)
        ma20_recent_window = ma20_values[-3:]  # Last 3 days
        ma20_prev_window = ma20_values[-6:-3]  # Previous 3 days

        ma20_recent_low = min(ma20_recent_window)
        ma20_prev_low = min(ma20_prev_window)
        ma20_current = ma20_values[-1]

        result['ma20_recent_low'] = ma20_recent_low
        result['ma20_prev_low'] = ma20_prev_low
        result['ma20_higher_low'] = ma20_recent_low > ma20_prev_low
        result['ma20_rising_from_low'] = ma20_current > ma20_recent_low

        # MA50: Higher Lows detection (5-day windows)
        # Recent 5 days: [-5:] (indices 5,6,7,8,9)
        # Previous 5 days: [-10:-5] (indices 0,1,2,3,4)
        ma50_recent_window = ma50_values[-5:]  # Last 5 days
        ma50_prev_window = ma50_values[-10:-5]  # Previous 5 days

        ma50_recent_low = min(ma50_recent_window)
        ma50_prev_low = min(ma50_prev_window)
        ma50_current = ma50_values[-1]

        result['ma50_recent_low'] = ma50_recent_low
        result['ma50_prev_low'] = ma50_prev_low
        result['ma50_higher_low'] = ma50_recent_low > ma50_prev_low
        result['ma50_rising_from_low'] = ma50_current > ma50_recent_low

        return result

    def _detect_bottom_stage(
        self,
        ma20: float,
        ma50: float,
        ma100: float,
        higher_lows: dict
    ) -> Optional[str]:
        """
        Detect bottom formation stage based on breadth conditions and higher lows.

        Stages:
        - CAPITULATION: Extreme oversold (all MAs < 25), no higher low yet
        - ACCUMULATING: All oversold (< 30), MA20 forming higher lows
        - EARLY_REVERSAL: MA20 higher low confirmed + MA50 starting to form higher low

        Returns:
            str or None: Bottom stage name or None if not in bottom formation
        """
        # Check if already in uptrend (no bottom detection needed)
        if ma50 >= 50 and ma100 >= 50:
            return None

        all_oversold = ma20 < 30 and ma50 < 30 and ma100 < 30
        extreme_oversold = ma20 < 25 and ma50 < 25 and ma100 < 25

        ma20_higher_low = higher_lows.get('ma20_higher_low', False)
        ma20_rising = higher_lows.get('ma20_rising_from_low', False)
        ma50_higher_low = higher_lows.get('ma50_higher_low', False)
        ma50_rising = higher_lows.get('ma50_rising_from_low', False)

        # Stage 1: CAPITULATION - Extreme fear, no recovery signs yet
        if extreme_oversold and not ma20_higher_low:
            return 'CAPITULATION'

        # Stage 2: ACCUMULATING - Oversold but MA20 forming higher lows (bottom forming)
        if all_oversold and ma20_higher_low and ma20_rising:
            return 'ACCUMULATING'

        # Stage 3: EARLY_REVERSAL - MA20 escaped oversold + both MAs forming higher lows
        if ma20 >= 25 and ma20_higher_low and ma50_higher_low and ma50_rising:
            return 'EARLY_REVERSAL'

        return None
