#!/usr/bin/env python3
"""
Complete Daily TA Update Pipeline
==================================

Full technical analysis update workflow (14 steps):

Core Indicators (Steps 1-9):
1. VN-Index Analysis (trend, RSI, support/resistance)
2. Technical Indicators (MA, RSI, MACD, Bollinger)
3. Alerts (MA crossover, volume spike, breakout, patterns)
4. Money Flow (individual stocks)
5. Sector Money Flow (1D, 1W, 1M)
6. Market Breadth (% above MA)
7. Sector Breadth (per sector MA stats)
8. Market Regime (BULLISH/NEUTRAL/BEARISH)
9. RS Rating (IBD-style 1-99)

Dashboard Outputs (Steps 10-14):
10. RS Rating 30d History (heatmap data)
11. Market State (combined regime + breadth + vnindex)
12. Sector Ranking (composite scoring)
13. RRG Coordinates (Relative Rotation Graph)
14. Trading Lists (Buy/Sell signals)

Usage:
    python3 PROCESSORS/pipelines/daily/daily_ta_complete.py
    python3 PROCESSORS/pipelines/daily/daily_ta_complete.py --sessions 200

Author: Claude Code
Date: 2025-12-31 (v2.1.0 - added dashboard calculators)
"""

import sys
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime

# Add project root
project_root = Path(__file__).resolve().parents[3]  # daily/pipelines/PROCESSORS is 3 levels deep
sys.path.insert(0, str(project_root))

from PROCESSORS.technical.indicators.technical_processor import TechnicalProcessor
from PROCESSORS.technical.indicators.alert_detector import TechnicalAlertDetector
from PROCESSORS.technical.indicators.money_flow import MoneyFlowAnalyzer
from PROCESSORS.technical.indicators.sector_money_flow import SectorMoneyFlowAnalyzer
from PROCESSORS.technical.indicators.sector_breadth import SectorBreadthAnalyzer
from PROCESSORS.technical.indicators.market_regime import MarketRegimeDetector
from PROCESSORS.technical.indicators.vnindex_analyzer import VNIndexAnalyzer
from PROCESSORS.technical.indicators.rs_rating import RSRatingCalculator
# Dashboard-specific calculators (v2.1.0)
from PROCESSORS.technical.indicators.market_state_calculator import MarketStateCalculator
from PROCESSORS.technical.indicators.sector_ranking_calculator import SectorRankingCalculator
from PROCESSORS.technical.indicators.rrg_calculator import RRGCalculator
from PROCESSORS.technical.indicators.trading_list_generator import TradingListGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CompleteTAUpdatePipeline:
    """Complete TA update pipeline."""

    def __init__(self, ohlcv_path: str = "DATA/raw/ohlcv/OHLCV_mktcap.parquet"):
        """Initialize pipeline."""
        self.ohlcv_path = ohlcv_path
        self.tech_processor = TechnicalProcessor(ohlcv_path)
        self.alert_detector = TechnicalAlertDetector(ohlcv_path)
        self.money_flow_analyzer = MoneyFlowAnalyzer(ohlcv_path)
        self.sector_money_flow = SectorMoneyFlowAnalyzer(ohlcv_path)
        self.sector_breadth = SectorBreadthAnalyzer()
        self.market_regime = MarketRegimeDetector()
        self.vnindex_analyzer = VNIndexAnalyzer()
        self.rs_rating_calc = RSRatingCalculator()
        # Dashboard-specific calculators
        self.market_state_calc = MarketStateCalculator()
        self.sector_ranking_calc = SectorRankingCalculator()
        self.rrg_calc = RRGCalculator()
        self.trading_list_gen = TradingListGenerator()

    def calculate_market_breadth(self, df: pd.DataFrame, date=None) -> dict:
        """Calculate market breadth."""
        # Normalize date column to date type
        if df['date'].dtype != 'object':
            df['date'] = pd.to_datetime(df['date']).dt.date
        else:
            df['date'] = pd.to_datetime(df['date']).dt.date
        
        if date is None:
            date = df['date'].max()
        else:
            # Normalize input date to date object
            if isinstance(date, str):
                date = pd.to_datetime(date).date()
            elif isinstance(date, pd.Timestamp):
                date = date.date()
            # If already date object, keep as is

        # Filter by date (ensure both are date objects)
        day_df = df[df['date'] == date].copy()

        if len(day_df) == 0:
            logger.warning(f"⚠️  No data found for date {date} in tech_df. Available dates: {df['date'].min()} to {df['date'].max()}")
            return None

        total_stocks = len(day_df)

        # MA breadth
        above_ma20 = (day_df['close'] > day_df['sma_20']).sum()
        above_ma50 = (day_df['close'] > day_df['sma_50']).sum()
        above_ma100 = (day_df['close'] > day_df['sma_100']).sum()
        above_ma200 = (day_df['close'] > day_df['sma_200']).sum()

        # AD
        advancing = (day_df['close'] > day_df['open']).sum()
        declining = (day_df['close'] < day_df['open']).sum()
        unchanged = (day_df['close'] == day_df['open']).sum()

        ad_ratio = advancing / declining if declining > 0 else 0

        # Trend
        ma50_pct = (above_ma50 / total_stocks) * 100

        if ma50_pct > 60:
            market_trend = 'BULLISH'
        elif ma50_pct < 40:
            market_trend = 'BEARISH'
        else:
            market_trend = 'NEUTRAL'

        return {
            'date': date,
            'total_stocks': total_stocks,
            'above_ma20': int(above_ma20),
            'above_ma50': int(above_ma50),
            'above_ma100': int(above_ma100),
            'above_ma200': int(above_ma200),
            'above_ma20_pct': round((above_ma20 / total_stocks) * 100, 2),
            'above_ma50_pct': round(ma50_pct, 2),
            'above_ma100_pct': round((above_ma100 / total_stocks) * 100, 2),
            'above_ma200_pct': round((above_ma200 / total_stocks) * 100, 2),
            'advancing': int(advancing),
            'declining': int(declining),
            'unchanged': int(unchanged),
            'ad_ratio': round(ad_ratio, 2),
            'market_trend': market_trend
        }

    def save_alerts(self, alerts: dict, date):
        """Save alerts to daily snapshots."""
        output_dir = Path("DATA/processed/technical/alerts/daily")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save each alert type (overwrite)
        for alert_type, alert_df in alerts.items():
            if not alert_df.empty:
                # Convert date
                alert_df['date'] = pd.to_datetime(alert_df['date']).dt.date

                # Save
                output_path = output_dir / f"{alert_type}_latest.parquet"
                alert_df.to_parquet(output_path, index=False)

                logger.info(f"  ✅ Saved {len(alert_df)} {alert_type} alerts")

        # Save to historical (append)
        historical_dir = Path("DATA/processed/technical/alerts/historical")
        historical_dir.mkdir(parents=True, exist_ok=True)

        for alert_type, alert_df in alerts.items():
            if not alert_df.empty:
                hist_path = historical_dir / f"{alert_type}_history.parquet"

                if hist_path.exists():
                    existing = pd.read_parquet(hist_path)
                    # Remove duplicates for this date
                    existing = existing[existing['date'] != date]
                    combined = pd.concat([existing, alert_df], ignore_index=True)
                    combined.to_parquet(hist_path, index=False)
                else:
                    alert_df.to_parquet(hist_path, index=False)

    def generate_optimized_basic_data(self, tech_df: pd.DataFrame):
        """Generate optimized basic_data files for Streamlit (Option B).

        Creates:
        - basic_data_latest.parquet (146KB) - latest row per symbol for lookups
        - basic_data_30d.parquet (2.2MB) - last 30 days for S/R calculations
        """
        output_dir = Path("DATA/processed/technical")

        # Ensure date is datetime
        tech_df['date'] = pd.to_datetime(tech_df['date'])

        # 1. basic_data_latest.parquet (458 rows, 146KB)
        latest = tech_df.sort_values('date', ascending=False).groupby('symbol', as_index=False).first()
        latest_path = output_dir / "basic_data_latest.parquet"
        latest.to_parquet(latest_path, index=False)
        logger.info(f"  ✅ basic_data_latest.parquet: {len(latest)} rows")

        # 2. basic_data_30d.parquet (~10K rows, 2.2MB)
        latest_date = tech_df['date'].max()
        cutoff = latest_date - pd.Timedelta(days=30)
        recent = tech_df[tech_df['date'] >= cutoff].copy()
        recent_path = output_dir / "basic_data_30d.parquet"
        recent.to_parquet(recent_path, index=False)
        logger.info(f"  ✅ basic_data_30d.parquet: {len(recent)} rows")

    def precalculate_composite_scores(self) -> pd.DataFrame:
        """Pre-calculate FULL 100-point composite scores for all signals.

        Uses full VSA spec with vol_ratio, spread_ratio, close_position.
        Saves to signals_with_scores.parquet for instant Streamlit loading.
        """
        try:
            # Import full spec scoring service
            sys.path.insert(0, str(Path(__file__).parents[3]))
            from WEBAPP.pages.technical.services.full_spec_scoring_service import (
                calculate_candlestick_score,
                calculate_vsa_score,
                calculate_trend_score,
                calculate_sr_score,
                calculate_rs_score,
                calculate_liquidity_score,
                classify_trend,
                BULLISH_REVERSAL_PATTERNS,
                BEARISH_REVERSAL_PATTERNS,
            )

            # Load pattern signals
            patterns_path = Path("DATA/processed/technical/alerts/daily/patterns_latest.parquet")
            if not patterns_path.exists():
                logger.warning("  ⚠️ No patterns_latest.parquet found")
                return None

            signals_df = pd.read_parquet(patterns_path)
            if signals_df.empty:
                logger.warning("  ⚠️ No pattern signals to score")
                return None

            # Drop existing score columns to avoid duplicates
            cols_to_drop = [c for c in ['composite_score', 'context_score', 'direction', 'trend', 'trading_value',
                                        'pattern_score', 'vsa_score', 'trend_score', 'sr_score', 'rs_score',
                                        'liquidity_score', 'vol_ratio', 'vsa_signal', 'vsa_bias', 'price', 'is_aligned', 'rs_rating'] if c in signals_df.columns]
            if cols_to_drop:
                signals_df = signals_df.drop(columns=cols_to_drop)

            # Load supporting data
            basic_latest_path = Path("DATA/processed/technical/basic_data_latest.parquet")
            basic_30d_path = Path("DATA/processed/technical/basic_data_30d.parquet")
            rs_path = Path("DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet")

            # Build basic lookup (latest OHLCV + indicators)
            basic_lookup = {}
            if basic_latest_path.exists():
                basic_df = pd.read_parquet(basic_latest_path)
                for _, row in basic_df.iterrows():
                    basic_lookup[row['symbol']] = row.to_dict()

            # Build volume average lookup from 30d data
            vol_avg_lookup = {}
            if basic_30d_path.exists():
                basic_30d = pd.read_parquet(basic_30d_path, columns=['symbol', 'date', 'volume'])
                basic_30d = basic_30d.sort_values('date', ascending=False)
                for symbol in basic_30d['symbol'].unique():
                    sym_data = basic_30d[basic_30d['symbol'] == symbol].head(20)
                    if len(sym_data) >= 5:
                        vol_avg_lookup[symbol] = sym_data['volume'].mean()

            # Build RS lookup with momentum
            rs_lookup = {}
            if rs_path.exists():
                rs_df = pd.read_parquet(rs_path)
                rs_df = rs_df.sort_values('date', ascending=False)
                for symbol in rs_df['symbol'].unique():
                    sym_data = rs_df[rs_df['symbol'] == symbol]
                    if len(sym_data) >= 1:
                        rs_rating = sym_data.iloc[0].get('rs_rating', 0) or 0
                        rs_momentum = 0
                        if len(sym_data) >= 5:
                            rs_5d_ago = sym_data.iloc[4].get('rs_rating', rs_rating) or rs_rating
                            rs_momentum = rs_rating - rs_5d_ago
                        rs_lookup[symbol] = {'rs_rating': rs_rating, 'rs_momentum': rs_momentum}

            # Calculate FULL spec scores
            scores = []
            for _, row in signals_df.iterrows():
                symbol = row.get('symbol', '')
                pattern = row.get('pattern_name', '')
                signal_type = row.get('signal', 'BULLISH')

                # Get basic data
                basic_data = basic_lookup.get(symbol, {})
                if not basic_data:
                    continue

                # Extract values
                price = basic_data.get('close', 0) or 0
                high = basic_data.get('high', price) or price
                low = basic_data.get('low', price) or price
                volume = basic_data.get('volume', 0) or 0
                trading_value = basic_data.get('trading_value', 0) or 0
                atr_14 = basic_data.get('atr_14', 1) or 1
                price_vs_sma20 = basic_data.get('price_vs_sma20', 0) or 0
                price_vs_sma50 = basic_data.get('price_vs_sma50', 0) or 0

                # Calculate VSA metrics (FULL SPEC)
                vol_avg_20d = vol_avg_lookup.get(symbol, volume) or volume
                vol_ratio = volume / vol_avg_20d if vol_avg_20d > 0 else 1.0
                spread = high - low
                spread_ratio = spread / atr_14 if atr_14 > 0 else 1.0
                close_position = (price - low) / spread if spread > 0 else 0.5

                # Classify trend
                trend = classify_trend(price_vs_sma20, price_vs_sma50)

                # Derive direction from signal type
                pattern_lower = pattern.lower().replace(' ', '_') if pattern else ''
                if signal_type == 'BULLISH' or pattern_lower in BULLISH_REVERSAL_PATTERNS:
                    direction = 'BUY'
                elif signal_type == 'BEARISH' or pattern_lower in BEARISH_REVERSAL_PATTERNS:
                    direction = 'SELL'
                else:
                    direction = 'NEUTRAL'

                # === CALCULATE ALL 6 FACTORS (FULL SPEC) ===

                # 1. Candlestick Score (15 pts)
                candlestick_score = calculate_candlestick_score(pattern, trend)

                # 2. VSA Score (25 pts) - FULL SPEC with vol_ratio, spread_ratio, close_position
                vsa_result = calculate_vsa_score(vol_ratio, spread_ratio, close_position, direction, trend)
                vsa_score = vsa_result['vsa_score']
                vsa_signal = vsa_result.get('vsa_signal', '')
                vsa_bias = vsa_result.get('vsa_bias', '')

                # 3. Trend Score (20 pts)
                trend_score = calculate_trend_score(direction, trend, pattern)

                # 4. S/R Score (15 pts)
                sr_result = calculate_sr_score(price, low, high, direction)
                sr_score = sr_result['sr_score']

                # 5. RS Score (15 pts)
                rs_data = rs_lookup.get(symbol, {'rs_rating': 50, 'rs_momentum': 0})
                rs_rating = rs_data.get('rs_rating', 50)
                rs_momentum = rs_data.get('rs_momentum', 0)
                rs_result = calculate_rs_score(rs_rating, rs_momentum, direction)
                rs_score = rs_result['rs_score']

                # 6. Liquidity Score (10 pts)
                liq_result = calculate_liquidity_score(trading_value, vol_ratio)
                liquidity_score = liq_result['liquidity_score']

                # TOTAL (max 100)
                total_score = candlestick_score + vsa_score + trend_score + sr_score + rs_score + liquidity_score
                total_score = max(0, min(100, total_score))

                # Alignment check
                is_aligned = (
                    (trend in ['STRONG_UP', 'UPTREND'] and direction in ['BUY', 'PULLBACK']) or
                    (trend in ['STRONG_DOWN', 'DOWNTREND'] and direction in ['SELL', 'BOUNCE'])
                )

                scores.append({
                    'composite_score': round(total_score, 1),
                    'pattern_score': round(candlestick_score, 1),
                    'vsa_score': round(vsa_score, 1),
                    'trend_score': round(trend_score, 1),
                    'sr_score': round(sr_score, 1),
                    'rs_score': round(rs_score, 1),
                    'liquidity_score': round(liquidity_score, 1),
                    'is_aligned': is_aligned,
                    'rs_rating': rs_rating,
                    'direction': direction,
                    'trend': trend,
                    'trading_value': trading_value,
                    'vol_ratio': round(vol_ratio, 2),
                    'vsa_signal': vsa_signal or '',
                    'vsa_bias': vsa_bias or '',
                    'price': price,
                })

            # Merge scores with signals
            scores_df = pd.DataFrame(scores)
            result = pd.concat([signals_df.reset_index(drop=True), scores_df], axis=1)

            # Remove duplicate columns (keep last occurrence which is from scores_df)
            result = result.loc[:, ~result.columns.duplicated(keep='last')]

            # Save
            output_path = Path("DATA/processed/technical/alerts/signals_with_scores.parquet")
            result.to_parquet(output_path, index=False)

            logger.info(f"  ✅ signals_with_scores.parquet: {len(result)} signals with FULL 100-pt scores")
            return result

        except Exception as e:
            logger.error(f"  ❌ Failed to pre-calculate scores: {e}")
            import traceback
            traceback.print_exc()
            return None

    def save_market_breadth(self, breadth: dict):
        """Save market breadth."""
        output_path = Path("DATA/processed/technical/market_breadth/market_breadth_daily.parquet")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        new_row = pd.DataFrame([breadth])
        # Normalize date to pd.Timestamp
        new_row['date'] = pd.to_datetime(new_row['date'])

        if output_path.exists():
            existing = pd.read_parquet(output_path)
            # Normalize existing dates
            existing['date'] = pd.to_datetime(existing['date'])
            target_date = pd.to_datetime(breadth['date'])
            existing = existing[existing['date'] != target_date]
            combined = pd.concat([existing, new_row], ignore_index=True)
            combined = combined.sort_values('date').reset_index(drop=True)
            combined.to_parquet(output_path, index=False)
        else:
            new_row.to_parquet(output_path, index=False)

    def run(self, n_sessions: int = 200, date: str = None):
        """
        Run complete TA update pipeline.

        Args:
            n_sessions: Number of sessions to process
            date: Target date (default: latest)
        """
        logger.info("=" * 80)
        logger.info("COMPLETE DAILY TA UPDATE PIPELINE")
        logger.info("=" * 80)

        start_time = datetime.now()

        try:
            # Step 1: VN-Index Analysis
            logger.info("\n[1/14] Analyzing VN-Index...")
            vnindex_df = self.vnindex_analyzer.run_full_analysis(n_sessions=500)

            # Step 2: Technical Indicators
            logger.info("\n[2/14] Calculating technical indicators...")
            tech_df = self.tech_processor.run_full_processing(n_sessions=n_sessions)
            
            # Normalize tech_df date column
            if tech_df['date'].dtype != 'object':
                tech_df['date'] = pd.to_datetime(tech_df['date']).dt.date
            else:
                tech_df['date'] = pd.to_datetime(tech_df['date']).dt.date

            # Generate optimized basic_data files (Option B - fast Streamlit loading)
            logger.info("  Generating optimized basic_data files...")
            self.generate_optimized_basic_data(tech_df.copy())

            # Set target date
            if date is None:
                date = tech_df['date'].max()
            else:
                # Normalize date parameter
                if isinstance(date, str):
                    date = pd.to_datetime(date).date()
                elif isinstance(date, pd.Timestamp):
                    date = date.date()
                
                # Check if date exists in tech_df
                if date not in tech_df['date'].values:
                    logger.warning(f"⚠️  Date {date} not found in tech_df. Latest available: {tech_df['date'].max()}")
                    # Use latest available date that is <= target date
                    available_dates = tech_df[tech_df['date'] <= date]['date']
                    if len(available_dates) > 0:
                        date = available_dates.max()
                        logger.info(f"   Using latest available date: {date}")
                    else:
                        date = tech_df['date'].max()
                        logger.warning(f"   No data before target date. Using latest: {date}")

            # Step 3: Alerts
            logger.info("\n[3/14] Detecting alerts...")
            alerts = self.alert_detector.detect_all_alerts(date=date, n_sessions=n_sessions)
            self.save_alerts(alerts, date)

            # Step 4: Money Flow
            logger.info("\n[4/14] Calculating money flow...")
            money_flow_df = self.money_flow_analyzer.calculate_all_money_flow(n_sessions=n_sessions)
            self.money_flow_analyzer.save_money_flow(money_flow_df)

            # Step 5: Sector Money Flow (Multi-Timeframe)
            logger.info("\n[5/14] Calculating sector money flow (1D, 1W, 1M)...")
            sector_mf_results = self.sector_money_flow.calculate_multi_timeframe_flow(date=date)
            self.sector_money_flow.save_multi_timeframe_flow(sector_mf_results)

            # Step 6: Market Breadth
            logger.info("\n[6/14] Calculating market breadth...")
            breadth = self.calculate_market_breadth(tech_df, date)
            if breadth:
                self.save_market_breadth(breadth)

            # Step 7: Sector Breadth
            logger.info("\n[7/14] Calculating sector breadth...")
            sector_breadth_df = self.sector_breadth.calculate_sector_breadth(date=date)
            if not sector_breadth_df.empty:
                self.sector_breadth.save_sector_breadth(sector_breadth_df)

            # Step 8: Market Regime
            logger.info("\n[8/14] Detecting market regime...")
            regime_data = self.market_regime.detect_regime(date=date)
            if regime_data:
                self.market_regime.save_regime_history(regime_data)

            # Step 9: RS Rating (IBD-style)
            logger.info("\n[9/14] Calculating RS Rating...")
            rs_rating_path = self.rs_rating_calc.run_and_save()
            rs_latest = self.rs_rating_calc.get_latest()
            rs_count = len(rs_latest) if rs_latest is not None else 0

            # Step 10: RS Rating 30d History (for dashboard heatmap)
            logger.info("\n[10/14] Generating RS Rating 30d history...")
            rs_history_path = self.rs_rating_calc.save_history_30d()
            logger.info(f"  ✅ RS Rating history saved")

            # Step 11: Market State (combines regime + breadth + vnindex)
            logger.info("\n[11/14] Calculating market state...")
            market_state_df = self.market_state_calc.run(date=str(date) if date else None)
            if not market_state_df.empty:
                logger.info(f"  ✅ Market state: {market_state_df['signal'].iloc[0]}, exposure: {market_state_df['exposure_level'].iloc[0]}%")

            # Step 12: Sector Ranking
            logger.info("\n[12/14] Calculating sector ranking...")
            sector_ranking_df = self.sector_ranking_calc.run(date=str(date) if date else None)
            if not sector_ranking_df.empty:
                top_sector = sector_ranking_df.iloc[0]
                logger.info(f"  ✅ Top sector: {top_sector['sector_code']} (score: {top_sector['score']:.1f})")

            # Step 13: RRG (Relative Rotation Graph)
            logger.info("\n[13/14] Calculating RRG coordinates...")
            rrg_df = self.rrg_calc.run(date=str(date) if date else None)
            if not rrg_df.empty:
                leading = rrg_df[rrg_df['quadrant'] == 'LEADING']['sector_code'].tolist()
                logger.info(f"  ✅ LEADING sectors: {', '.join(leading[:3]) if leading else 'None'}")

            # Step 14: Trading Lists (Buy/Sell)
            logger.info("\n[14/15] Generating trading lists...")
            buy_list, sell_list = self.trading_list_gen.run(date=str(date) if date else None)
            logger.info(f"  ✅ Buy list: {len(buy_list)} candidates")
            logger.info(f"  ✅ Sell list: {len(sell_list)} signals")

            # Step 15: Pre-calculate Composite Scores (Option B optimization)
            logger.info("\n[15/15] Pre-calculating composite scores...")
            scored_signals = self.precalculate_composite_scores()
            if scored_signals is not None:
                logger.info(f"  ✅ Saved {len(scored_signals)} signals with scores")

            # Summary
            elapsed = (datetime.now() - start_time).total_seconds()

            logger.info("\n" + "=" * 80)
            logger.info(f"SUMMARY - {date}")
            logger.info("=" * 80)

            if not vnindex_df.empty:
                latest_vni = vnindex_df.tail(1).iloc[0]
                logger.info(f"\nVN-Index:")
                logger.info(f"  Close: {latest_vni['close']:.2f}")
                logger.info(f"  Trend: {latest_vni['trend']}")
                logger.info(f"  RSI: {latest_vni['rsi_14']:.2f}")

            logger.info(f"\nTechnical Indicators: {len(tech_df):,} records")
            logger.info(f"MA Crossover Alerts: {len(alerts['ma_crossover'])}")
            logger.info(f"Volume Spike Alerts: {len(alerts['volume_spike'])}")
            logger.info(f"Breakout Alerts: {len(alerts['breakout'])}")
            logger.info(f"Pattern Alerts: {len(alerts['patterns'])}")
            logger.info(f"Combined Signals: {len(alerts['combined'])}")

            if breadth:
                logger.info(f"\nMarket Breadth:")
                logger.info(f"  Above MA20: {breadth['above_ma20']} ({breadth['above_ma20_pct']}%)")
                logger.info(f"  Above MA50: {breadth['above_ma50']} ({breadth['above_ma50_pct']}%)")
                logger.info(f"  Market Trend: {breadth['market_trend']}")

            # Display multi-timeframe money flow
            logger.info(f"\nSector Money Flow (Multi-Timeframe):")
            for timeframe in ['1D', '1W', '1M']:
                df = sector_mf_results.get(timeframe)
                if df is not None and not df.empty:
                    logger.info(f"\n  {timeframe} Top 5:")
                    top5 = df.head(5)
                    for _, row in top5.iterrows():
                        logger.info(f"    {row['sector_code']}: {row['inflow_pct']:+.1f}% ({row['flow_signal']})")

            if not sector_breadth_df.empty:
                logger.info(f"\nTop 3 Strongest Sectors:")
                top3 = sector_breadth_df.head(3)
                for _, row in top3.iterrows():
                    logger.info(f"  {row['sector_code']}: {row['strength_score']:.1f} ({row['sector_trend']})")

            if regime_data:
                logger.info(f"\nMarket Regime:")
                logger.info(f"  Regime: {regime_data['regime']}")
                logger.info(f"  Score: {regime_data['regime_score']:.2f}")
                logger.info(f"  Risk Level: {regime_data['risk_level']}")

            logger.info(f"\nRS Rating (IBD-style):")
            logger.info(f"  Stocks: {rs_count}")
            if rs_latest is not None and len(rs_latest) > 0:
                top5_rs = rs_latest.head(5)
                logger.info(f"  Top 5:")
                for _, row in top5_rs.iterrows():
                    logger.info(f"    {row['symbol']}: RS {row['rs_rating']}")

            # Dashboard Outputs Summary
            logger.info(f"\n--- Dashboard Outputs ---")
            if not market_state_df.empty:
                logger.info(f"  Market State: {market_state_df['signal'].iloc[0]} (exposure: {market_state_df['exposure_level'].iloc[0]}%)")
            if not sector_ranking_df.empty:
                logger.info(f"  Sector Ranking: {len(sector_ranking_df)} sectors ranked")
            if not rrg_df.empty:
                logger.info(f"  RRG: {len(rrg_df)} sectors positioned")
            logger.info(f"  Trading Lists: {len(buy_list)} buys, {len(sell_list)} sells")

            logger.info(f"\nProcessing time: {elapsed:.1f}s")
            logger.info("=" * 80)
            logger.info("\n✅ COMPLETE TA UPDATE FINISHED")

        except Exception as e:
            logger.error(f"\n❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            exit(1)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Complete Daily TA Update')
    parser.add_argument('--sessions', type=int, default=200, help='Number of sessions')
    parser.add_argument('--date', type=str, default=None, help='Target date (YYYY-MM-DD)')

    args = parser.parse_args()

    pipeline = CompleteTAUpdatePipeline()
    pipeline.run(n_sessions=args.sessions, date=args.date)


if __name__ == "__main__":
    main()
