#!/usr/bin/env python3
"""
Complete Daily TA Update Pipeline
==================================

Full technical analysis update workflow:
1. Load OHLCV data (last 200 sessions)
2. Calculate technical indicators (MA, RSI, MACD, etc.)
3. Detect alerts (MA crossover, volume spike, breakout, patterns)
4. Calculate money flow (individual + sector)
5. Calculate market breadth
6. Save all outputs

Usage:
    python3 PROCESSORS/technical/pipelines/daily_complete_ta_update.py
    python3 PROCESSORS/technical/pipelines/daily_complete_ta_update.py --sessions 200

Author: Claude Code
Date: 2025-12-15
"""

import sys
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime

# Add project root
project_root = Path(__file__).resolve().parents[2]  # pipelines is 2 levels deep
sys.path.insert(0, str(project_root))

from PROCESSORS.technical.indicators.technical_processor import TechnicalProcessor
from PROCESSORS.technical.indicators.alert_detector import TechnicalAlertDetector
from PROCESSORS.technical.indicators.money_flow import MoneyFlowAnalyzer
from PROCESSORS.technical.indicators.sector_money_flow import SectorMoneyFlowAnalyzer
from PROCESSORS.technical.indicators.sector_breadth import SectorBreadthAnalyzer
from PROCESSORS.technical.indicators.market_regime import MarketRegimeDetector
from PROCESSORS.technical.indicators.vnindex_analyzer import VNIndexAnalyzer

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

    def calculate_market_breadth(self, df: pd.DataFrame, date=None) -> dict:
        """Calculate market breadth."""
        if date is None:
            date = df['date'].max()

        day_df = df[df['date'] == date].copy()

        if len(day_df) == 0:
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

    def save_market_breadth(self, breadth: dict):
        """Save market breadth."""
        output_path = Path("DATA/processed/technical/market_breadth/market_breadth_daily.parquet")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        new_row = pd.DataFrame([breadth])

        if output_path.exists():
            existing = pd.read_parquet(output_path)
            existing = existing[existing['date'] != breadth['date']]
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
            logger.info("\n[1/8] Analyzing VN-Index...")
            vnindex_df = self.vnindex_analyzer.run_full_analysis(n_sessions=500)

            # Step 2: Technical Indicators
            logger.info("\n[2/8] Calculating technical indicators...")
            tech_df = self.tech_processor.run_full_processing(n_sessions=n_sessions)

            if date is None:
                date = tech_df['date'].max()

            # Step 3: Alerts
            logger.info("\n[3/8] Detecting alerts...")
            alerts = self.alert_detector.detect_all_alerts(date=date, n_sessions=n_sessions)
            self.save_alerts(alerts, date)

            # Step 4: Money Flow
            logger.info("\n[4/8] Calculating money flow...")
            money_flow_df = self.money_flow_analyzer.calculate_all_money_flow(n_sessions=n_sessions)
            self.money_flow_analyzer.save_money_flow(money_flow_df)

            # Step 5: Sector Money Flow (Multi-Timeframe)
            logger.info("\n[5/8] Calculating sector money flow (1D, 1W, 1M)...")
            sector_mf_results = self.sector_money_flow.calculate_multi_timeframe_flow(date=date)
            self.sector_money_flow.save_multi_timeframe_flow(sector_mf_results)

            # Step 6: Market Breadth
            logger.info("\n[6/8] Calculating market breadth...")
            breadth = self.calculate_market_breadth(tech_df, date)
            if breadth:
                self.save_market_breadth(breadth)

            # Step 7: Sector Breadth
            logger.info("\n[7/8] Calculating sector breadth...")
            sector_breadth_df = self.sector_breadth.calculate_sector_breadth(date=date)
            if not sector_breadth_df.empty:
                self.sector_breadth.save_sector_breadth(sector_breadth_df)

            # Step 8: Market Regime
            logger.info("\n[8/8] Detecting market regime...")
            regime_data = self.market_regime.detect_regime(date=date)
            if regime_data:
                self.market_regime.save_regime_history(regime_data)

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
