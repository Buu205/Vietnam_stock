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
from WEBAPP.core.trading_constants import (
    MA20_HIGHER_LOW_WINDOW,
    MA50_HIGHER_LOW_WINDOW,
    CAPITULATION_THRESHOLD,
    ACCUMULATION_THRESHOLD,
    EARLY_REVERSAL_MA20_MIN,
)


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

    # ==========================================================================
    # SIGNAL PRIORITY CONFIGURATION
    # ==========================================================================
    # Priority 1: Breakout/Breakdown - Price structure change
    # Priority 2: Strong Reversal - Morning/Evening Star, Engulfing, Three Soldiers/Crows
    # Priority 3: Weak/Single Candle Reversal - Hammer, Shooting Star, Hanging Man
    # Priority 4: MA Crossover - Trend confirmation (lagging)
    # Priority 5: Generic/Indecision - Doji, Spinning Top

    PATTERN_PRIORITY = {
        # Priority 2: Strong Reversal
        'morning_star': 2, 'evening_star': 2,
        'engulfing': 2, 'bullish_engulfing': 2, 'bearish_engulfing': 2,
        'three_white_soldiers': 2, 'three_black_crows': 2,
        # Priority 3: Weak/Single Candle Reversal
        'hammer': 3, 'inverted_hammer': 3,
        'shooting_star': 3, 'hanging_man': 3,
        # Priority 5: Generic/Indecision
        'doji': 5, 'spinning_top': 5,
    }

    MA_STRENGTH = {20: 50, 50: 75, 100: 85, 200: 100}

    @staticmethod
    @st.cache_data(ttl=60)
    def _load_signals() -> pd.DataFrame:
        """Load all signal types and combine with proper labels.

        Returns ALL signals (no dedup) with:
        - is_primary: True for highest priority signal per symbol+date
        - secondary_signals: List of other signal names for same symbol+date
        - priority_group: For sorting (1=highest, 5=lowest)
        """
        history_dir = Path("DATA/processed/technical/alerts/historical")
        daily_dir = Path("DATA/processed/technical/alerts/daily")
        all_signals = []

        # ======================================================================
        # 1. CANDLESTICK PATTERNS
        # ======================================================================
        patterns_path = history_dir / "patterns_history.parquet"
        if not patterns_path.exists():
            patterns_path = daily_dir / "patterns_latest.parquet"
        if patterns_path.exists():
            df = pd.read_parquet(patterns_path)

            # Remove exact duplicates (data pipeline bug)
            df = df.drop_duplicates(subset=['symbol', 'date', 'pattern_name'])

            df['signal_type'] = 'patterns'
            df['type_label'] = df['pattern_name'].fillna('Pattern')

            # JOIN trend data
            basic_path = Path("DATA/processed/technical/basic_data.parquet")
            if basic_path.exists():
                basic_df = pd.read_parquet(basic_path, columns=[
                    'symbol', 'date', 'price_vs_sma20', 'price_vs_sma50',
                    'trading_value', 'volume', 'expected_trading_value', 'trading_value_diff'
                ])
                basic_df['date'] = pd.to_datetime(basic_df['date']).dt.date
                df['date'] = pd.to_datetime(df['date']).dt.date
                df = df.merge(basic_df, on=['symbol', 'date'], how='left')

            # Classify trend
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

            # Context-aware DOJI signal refinement
            def refine_doji_signal(row):
                if row.get('pattern_name') != 'doji':
                    return row['signal']
                trend = row.get('trend', 'SIDEWAYS')
                if trend in ['STRONG_UP', 'UPTREND']:
                    return 'BEARISH'  # Reversal warning at top
                elif trend in ['STRONG_DOWN', 'DOWNTREND']:
                    return 'BULLISH'  # Hope for reversal at bottom
                return 'NEUTRAL'

            df['signal'] = df.apply(refine_doji_signal, axis=1)

            # TREND → PATTERN → DIRECTION
            def get_strategy_signal(row):
                pattern_signal = row['signal']
                trend = row['trend']

                if trend in ['STRONG_UP', 'UPTREND']:
                    if pattern_signal == 'BULLISH':
                        return 'BUY'
                    elif pattern_signal == 'BEARISH':
                        return 'PULLBACK'
                elif trend in ['STRONG_DOWN', 'DOWNTREND']:
                    if pattern_signal == 'BEARISH':
                        return 'SELL'
                    elif pattern_signal == 'BULLISH':
                        return 'BOUNCE'
                else:  # SIDEWAYS
                    if pattern_signal == 'BULLISH':
                        return 'BUY'
                    elif pattern_signal == 'BEARISH':
                        return 'SELL'
                return 'NEUTRAL'

            df['direction'] = df.apply(get_strategy_signal, axis=1)

            # Assign priority group (default 4 for unknown patterns)
            df['priority_group'] = df['pattern_name'].map(
                TADashboardService.PATTERN_PRIORITY
            ).fillna(4).astype(int)

            cols = ['symbol', 'date', 'signal_type', 'type_label', 'direction',
                    'price', 'strength', 'priority_group', 'trend']
            optional = ['trading_value', 'volume', 'price_vs_sma20', 'price_vs_sma50']
            for c in optional:
                if c in df.columns:
                    cols.append(c)
            all_signals.append(df[cols])

        # ======================================================================
        # 2. MA CROSSOVER - Period-based strength
        # ======================================================================
        ma_path = history_dir / "ma_crossover_history.parquet"
        if not ma_path.exists():
            ma_path = daily_dir / "ma_crossover_latest.parquet"
        if ma_path.exists():
            df = pd.read_parquet(ma_path)
            df['signal_type'] = 'ma_crossover'

            # Label with MA period
            df['type_label'] = df.apply(
                lambda r: f"MA{r['ma_period']} Cross {'↑' if r['alert_type'] == 'MA_CROSS_ABOVE' else '↓'}",
                axis=1
            )
            df['direction'] = df['signal'].map({
                'BULLISH': 'BUY', 'BEARISH': 'SELL'
            }).fillna('NEUTRAL')

            # Period-based strength: MA20=50, MA50=75, MA100=85, MA200=100
            df['strength'] = df['ma_period'].map(TADashboardService.MA_STRENGTH).fillna(50)
            df['priority_group'] = 4  # MA Crossover = Priority 4

            all_signals.append(df[['symbol', 'date', 'signal_type', 'type_label',
                                   'direction', 'price', 'strength', 'priority_group']])

        # ======================================================================
        # 3. VOLUME SPIKE
        # ======================================================================
        vol_path = history_dir / "volume_spike_history.parquet"
        if not vol_path.exists():
            vol_path = daily_dir / "volume_spike_latest.parquet"
        if vol_path.exists():
            df = pd.read_parquet(vol_path)
            df['signal_type'] = 'volume_spike'
            df['type_label'] = 'Vol Spike ' + df['volume_ratio'].round(1).astype(str) + 'x'

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
            df['strength'] = (df['confidence'].fillna(0.5) * 100).clip(0, 100)
            df['priority_group'] = 4  # Volume = Priority 4

            all_signals.append(df[['symbol', 'date', 'signal_type', 'type_label',
                                   'direction', 'price', 'strength', 'priority_group']])

        # ======================================================================
        # 4. BREAKOUT - Dynamic strength based on volume
        # ======================================================================
        breakout_path = history_dir / "breakout_history.parquet"
        if not breakout_path.exists():
            breakout_path = daily_dir / "breakout_latest.parquet"
        if breakout_path.exists():
            df = pd.read_parquet(breakout_path)
            df['signal_type'] = 'breakout'
            df['type_label'] = df['alert_type'].replace({
                'BREAKOUT_UP': 'Breakout ↑',
                'BREAKDOWN': 'Breakdown ↓'
            })

            def map_breakout_signal(sig):
                if not isinstance(sig, str):
                    return 'NEUTRAL'
                sig = sig.upper()
                if 'BULLISH' in sig or 'UP' in sig:
                    return 'BUY'
                elif 'BEARISH' in sig or 'DOWN' in sig:
                    return 'SELL'
                return 'NEUTRAL'

            df['direction'] = df['signal'].apply(map_breakout_signal)

            # Dynamic strength: Base 70 + volume_confirmed(+15) + volume_ratio>1.5(+15)
            def calc_breakout_strength(row):
                base = 70
                if row.get('volume_confirmed', False):
                    base += 15
                vol_ratio = row.get('volume_ratio', 1.0) or 1.0
                if vol_ratio > 1.5:
                    base += 15
                return min(base, 100)

            df['strength'] = df.apply(calc_breakout_strength, axis=1)
            df['priority_group'] = 1  # Breakout = Priority 1 (highest)

            all_signals.append(df[['symbol', 'date', 'signal_type', 'type_label',
                                   'direction', 'price', 'strength', 'priority_group']])

        if not all_signals:
            return pd.DataFrame()

        # ======================================================================
        # COMBINE & ADD PRIMARY/SECONDARY FLAGS
        # ======================================================================
        combined = pd.concat(all_signals, ignore_index=True)

        # Sort: Date DESC → Priority ASC (1=best) → Strength DESC
        combined = combined.sort_values(
            ['date', 'priority_group', 'strength'],
            ascending=[False, True, False]
        )

        # Mark is_primary: first row per symbol+date (highest priority)
        combined['is_primary'] = ~combined.duplicated(subset=['symbol', 'date'], keep='first')

        # Build secondary_signals: collect non-primary type_labels per symbol+date
        secondary_df = (
            combined[~combined['is_primary']]
            .groupby(['symbol', 'date'], as_index=False)
            .agg(secondary_signals=('type_label', list))
        )

        # Merge secondary_signals back to combined
        combined = combined.merge(secondary_df, on=['symbol', 'date'], how='left')
        combined['secondary_signals'] = combined['secondary_signals'].apply(
            lambda x: x if isinstance(x, list) else []
        )

        return combined

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

        Logic (optimized from 3-year backtest 2023-2025):
        - MA20: Compare min of last 7 days with min of previous 7 days
        - MA50: Compare min of last 9 days with min of previous 9 days

        Window rationale:
        - MA20 median swing cycle: ~14.5 days → window = 7 days (half cycle)
        - MA50 median swing cycle: ~19.0 days → window = 9 days (half cycle)

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
        # Window sizes from trading_constants (based on 3-year backtest)
        MA20_WINDOW = MA20_HIGHER_LOW_WINDOW  # 7 days (~14.5 day cycle / 2)
        MA50_WINDOW = MA50_HIGHER_LOW_WINDOW  # 9 days (~19.0 day cycle / 2)

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

        # Need at least 2x window days of data
        min_required = MA50_WINDOW * 2
        if len(breadth_df) < min_required:
            return result

        # Get column names
        ma20_col = 'above_ma20_pct' if 'above_ma20_pct' in breadth_df.columns else 'pct_above_ma20'
        ma50_col = 'above_ma50_pct' if 'above_ma50_pct' in breadth_df.columns else 'pct_above_ma50'

        # Get last 18 rows for analysis
        recent_data = breadth_df.tail(min_required).copy()
        ma20_values = recent_data[ma20_col].tolist()
        ma50_values = recent_data[ma50_col].tolist()

        # MA20: Higher Lows detection (7-day windows)
        ma20_recent_window = ma20_values[-MA20_WINDOW:]  # Last 7 days
        ma20_prev_window = ma20_values[-(MA20_WINDOW * 2):-MA20_WINDOW]  # Previous 7 days

        ma20_recent_low = min(ma20_recent_window)
        ma20_prev_low = min(ma20_prev_window)
        ma20_current = ma20_values[-1]

        result['ma20_recent_low'] = ma20_recent_low
        result['ma20_prev_low'] = ma20_prev_low
        result['ma20_higher_low'] = ma20_recent_low > ma20_prev_low
        result['ma20_rising_from_low'] = ma20_current > ma20_recent_low

        # MA50: Higher Lows detection (9-day windows)
        ma50_recent_window = ma50_values[-MA50_WINDOW:]  # Last 9 days
        ma50_prev_window = ma50_values[-(MA50_WINDOW * 2):-MA50_WINDOW]  # Previous 9 days

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

        # Use constants from trading_constants
        all_oversold = (ma20 < ACCUMULATION_THRESHOLD and
                        ma50 < ACCUMULATION_THRESHOLD and
                        ma100 < ACCUMULATION_THRESHOLD)
        extreme_oversold = (ma20 < CAPITULATION_THRESHOLD and
                           ma50 < CAPITULATION_THRESHOLD and
                           ma100 < CAPITULATION_THRESHOLD)

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
        if ma20 >= EARLY_REVERSAL_MA20_MIN and ma20_higher_low and ma50_higher_low and ma50_rising:
            return 'EARLY_REVERSAL'

        return None
