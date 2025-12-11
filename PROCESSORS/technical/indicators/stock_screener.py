#!/usr/bin/env python3
"""
Daily Stock Screener for Vietnamese Market
==========================================

Hệ thống lọc cổ phiếu hàng ngày cho 400+ mã chứng khoán Việt Nam
dựa trên các tín hiệu kỹ thuật và crossover patterns.

Features:
- EMA 9 x EMA 21 crossover (Short-term signals)
- MA 20 x MA 50 crossover (Mid-term signals) 
- Multi-factor scoring system
- Daily screening reports
- Sector analysis
- Risk assessment

Usage:
    python stock_screener.py [--output-dir results] [--top-n 20]

Author: AI Assistant
Date: 2025-01-27
"""

import pandas as pd
import numpy as np
import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

# Add technical processor to path
sys.path.append(os.path.dirname(__file__))
from technical_processor import TechnicalProcessor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockScreener:
    """Daily Stock Screener với multiple filtering strategies."""
    
    def __init__(self, 
                 ohlcv_path: str = None,
                 output_dir: str = None):
        """
        Initialize Stock Screener.
        
        Args:
            ohlcv_path: Path to OHLCV data file
            output_dir: Output directory for screening results
        """
        project_root = Path(__file__).resolve().parents[4]
        self.ohlcv_path = ohlcv_path or str(project_root / "DATA/raw/ohlcv/OHLCV_mktcap.parquet")
        self.output_dir = Path(output_dir) if output_dir else project_root / "DATA/processed/technical/screening"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize technical processor
        self.tech_processor = TechnicalProcessor()
        
        # Sector mapping for analysis
        self.sector_mapping = {
            'VCB': 'Ngân hàng', 'TCB': 'Ngân hàng', 'BID': 'Ngân hàng', 'CTG': 'Ngân hàng', 'MBB': 'Ngân hàng',
            'VIC': 'Bất động sản', 'VHM': 'Bất động sản', 'KDH': 'Bất động sản', 'NVL': 'Bất động sản',
            'VNM': 'Tiêu dùng', 'MSN': 'Tiêu dùng', 'MWG': 'Tiêu dùng', 'PNJ': 'Tiêu dùng',
            'GAS': 'Năng lượng', 'PLX': 'Năng lượng', 'POW': 'Năng lượng', 'GEG': 'Năng lượng',
            'HPG': 'Thép', 'HSG': 'Thép', 'NKG': 'Thép', 'SMC': 'Thép',
            'FPT': 'Công nghệ', 'CMG': 'Công nghệ', 'ELC': 'Công nghệ', 'ITD': 'Công nghệ'
        }
        
    def load_latest_data(self, days_back: int = 60) -> pd.DataFrame:
        """Load latest OHLCV data for screening."""
        logger.info(f"Loading latest {days_back} days of OHLCV data...")
        
        df = pd.read_parquet(self.ohlcv_path)
        
        # Get latest N days for each symbol
        df_latest = df.groupby('symbol').tail(days_back).reset_index(drop=True)
        
        logger.info(f"Loaded data: {len(df_latest)} records, {df_latest['symbol'].nunique()} symbols")
        logger.info(f"Date range: {df_latest['date'].min()} to {df_latest['date'].max()}")
        
        return df_latest
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators needed for screening."""
        logger.info("Calculating all technical indicators...")
        
        # Calculate basic indicators
        result = self.tech_processor.calculate_basic_data(df)
        result = self.tech_processor.calculate_moving_averages(result)  # Now includes MA crossover
        result = self.tech_processor.calculate_exponential_moving_averages(result)  # Includes EMA crossover
        result = self.tech_processor.calculate_rsi(result)
        result = self.tech_processor.calculate_macd(result)
        result = self.tech_processor.calculate_bollinger_bands(result)
        result = self.tech_processor.calculate_volatility(result)
        result = self.tech_processor.calculate_trading_values(result)
        
        # Add sector information
        result['sector'] = result['symbol'].map(self.sector_mapping).fillna('Khác')
        
        logger.info("All indicators calculated successfully!")
        return result
    
    def create_screening_filters(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Create multiple screening filters for different strategies."""
        
        # Get latest data only (most recent date for each symbol)
        latest_df = df.groupby('symbol').tail(1).reset_index(drop=True)
        
        filters = {}
        
        # 1. SHORT-TERM MOMENTUM (EMA 9 x EMA 21 based)
        filters['short_term_bullish'] = latest_df[
            (latest_df['ema_golden_cross'] == True) |  # Fresh golden cross
            ((latest_df['ema_crossover_signal'] > 0) & (latest_df['days_since_ema_cross'] <= 5))  # Recent golden cross
        ].copy()
        
        filters['short_term_bearish'] = latest_df[
            (latest_df['ema_death_cross'] == True) |  # Fresh death cross
            ((latest_df['ema_crossover_signal'] < 0) & (latest_df['days_since_ema_cross'] <= 5))  # Recent death cross
        ].copy()
        
        # 2. MID-TERM TREND (MA 20 x MA 50 based)
        filters['mid_term_bullish'] = latest_df[
            (latest_df['ma_golden_cross'] == True) |  # Fresh golden cross
            ((latest_df['ma_crossover_signal'] > 0) & (latest_df['days_since_ma_cross'] <= 10))  # Recent golden cross
        ].copy()
        
        filters['mid_term_bearish'] = latest_df[
            (latest_df['ma_death_cross'] == True) |  # Fresh death cross
            ((latest_df['ma_crossover_signal'] < 0) & (latest_df['days_since_ma_cross'] <= 10))  # Recent death cross
        ].copy()
        
        # 3. MOMENTUM BREAKOUT (Multiple confirmations)
        filters['momentum_breakout'] = latest_df[
            (latest_df['ema_crossover_signal'] > 0) &  # EMA bullish
            (latest_df['ma_crossover_signal'] > 0) &   # MA bullish
            (latest_df['rsi'] > 50) & (latest_df['rsi'] < 70) &  # RSI healthy
            (latest_df['macd'] > latest_df['macd_signal']) &  # MACD bullish
            (latest_df['volume_ratio'] > 1.2)  # Volume above average
        ].copy()
        
        # 4. OVERSOLD BOUNCE (Potential reversal)
        filters['oversold_bounce'] = latest_df[
            (latest_df['rsi'] < 35) &  # Oversold
            (latest_df['bb_position'] < 20) &  # Near lower Bollinger Band
            (latest_df['ema_crossover_signal'] >= 0) &  # EMA not bearish
            (latest_df['volume_ratio'] > 1.1)  # Some volume interest
        ].copy()
        
        # 5. OVERBOUGHT WARNING (Potential reversal)
        filters['overbought_warning'] = latest_df[
            (latest_df['rsi'] > 75) &  # Overbought
            (latest_df['bb_position'] > 80) &  # Near upper Bollinger Band
            (latest_df['volatility'] > latest_df['volatility_ma'] * 1.5)  # High volatility
        ].copy()
        
        # 6. HIGH VOLUME BREAKOUT
        filters['volume_breakout'] = latest_df[
            (latest_df['volume_ratio'] > 2.0) &  # Volume spike
            (latest_df['ema_crossover_signal'] > 0) &  # Bullish EMA
            (latest_df['close'] > latest_df['ma20'])  # Above MA20
        ].copy()
        
        # 7. SECTOR ROTATION PLAYS
        filters['sector_leaders'] = latest_df[
            (latest_df['ema_crossover_signal'] > 0) &  # Bullish EMA
            (latest_df['ma_crossover_signal'] > 0) &   # Bullish MA
            (latest_df['volume_ratio'] > 1.3)  # Above average volume
        ].copy()
        
        # 8. SAFE DIVIDEND PLAYS (Conservative)
        filters['dividend_safe'] = latest_df[
            (latest_df['symbol'].isin(['VCB', 'TCB', 'VNM', 'VIC', 'GAS', 'POW'])) &  # Blue chips
            (latest_df['ma_crossover_signal'] >= 0) &  # Not bearish MA
            (latest_df['volatility'] < latest_df['volatility_ma'])  # Low volatility
        ].copy()
        
        return filters
    
    def score_stocks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive scoring system for stocks."""
        
        df = df.copy()
        
        # Initialize scores
        df['technical_score'] = 0.0
        df['momentum_score'] = 0.0
        df['trend_score'] = 0.0
        df['volume_score'] = 0.0
        df['risk_score'] = 0.0
        
        # Technical Score (0-100)
        # EMA signals (20 points max)
        df.loc[df['ema_crossover_signal'] == 2, 'technical_score'] += 20  # Golden cross
        df.loc[df['ema_crossover_signal'] == 1, 'technical_score'] += 10  # Bullish
        df.loc[df['ema_crossover_signal'] == -1, 'technical_score'] -= 10  # Bearish
        df.loc[df['ema_crossover_signal'] == -2, 'technical_score'] -= 20  # Death cross
        
        # MA signals (15 points max)
        df.loc[df['ma_crossover_signal'] == 2, 'technical_score'] += 15
        df.loc[df['ma_crossover_signal'] == 1, 'technical_score'] += 8
        df.loc[df['ma_crossover_signal'] == -1, 'technical_score'] -= 8
        df.loc[df['ma_crossover_signal'] == -2, 'technical_score'] -= 15
        
        # RSI (15 points max)
        df.loc[(df['rsi'] > 40) & (df['rsi'] < 60), 'technical_score'] += 15  # Healthy
        df.loc[(df['rsi'] > 30) & (df['rsi'] <= 40), 'technical_score'] += 8   # Recovering
        df.loc[(df['rsi'] > 60) & (df['rsi'] <= 70), 'technical_score'] += 8   # Strong
        df.loc[df['rsi'] > 75, 'technical_score'] -= 10  # Overbought
        df.loc[df['rsi'] < 25, 'technical_score'] -= 10  # Oversold
        
        # MACD (10 points max)
        df.loc[df['macd'] > df['macd_signal'], 'technical_score'] += 10
        df.loc[df['macd'] < df['macd_signal'], 'technical_score'] -= 10
        
        # Momentum Score (0-100)
        df['momentum_score'] = (
            (df['ema_crossover_strength'] * 2).clip(0, 30) +  # EMA momentum
            (df['ma_crossover_strength'] * 1.5).clip(0, 25) +  # MA momentum
            ((df['rsi'] - 50).abs() * -0.5 + 25).clip(0, 25) +  # RSI momentum
            (df['macd_histogram'].abs() * 10000).clip(0, 20)  # MACD momentum
        )
        
        # Trend Score (0-100)
        trend_components = 0
        trend_components += np.where(df['close'] > df['ma20'], 20, -20)
        trend_components += np.where(df['ma20'] > df['ma50'], 25, -25)
        trend_components += np.where(df['ema9'] > df['ema21'], 15, -15)
        trend_components += np.where(df['macd'] > 0, 10, -10)
        df['trend_score'] = (trend_components + 70).clip(0, 100)
        
        # Volume Score (0-100)
        df['volume_score'] = (
            (df['volume_ratio'] * 25).clip(0, 50) +  # Volume ratio
            np.where(df['volume_ratio'] > 1.5, 25, 0) +  # Volume spike bonus
            np.where(df['volume_ratio'] > 2.0, 25, 0)   # High volume bonus
        ).clip(0, 100)
        
        # Risk Score (0-100, lower is better)
        df['risk_score'] = (
            (df['volatility'] * 2).clip(0, 40) +  # Volatility risk
            np.where(df['rsi'] > 80, 30, 0) +  # Overbought risk
            np.where(df['rsi'] < 20, 30, 0) +  # Oversold risk
            (df['bb_position'].apply(lambda x: abs(x - 50) * 0.6)).clip(0, 30)  # BB position risk
        ).clip(0, 100)
        
        # Overall Score (0-100)
        df['overall_score'] = (
            df['technical_score'] * 0.3 +
            df['momentum_score'] * 0.25 +
            df['trend_score'] * 0.25 +
            df['volume_score'] * 0.1 +
            (100 - df['risk_score']) * 0.1
        ).clip(0, 100)
        
        return df
    
    def generate_daily_report(self, 
                            filters: Dict[str, pd.DataFrame], 
                            scored_df: pd.DataFrame,
                            top_n: int = 20) -> Dict:
        """Generate comprehensive daily screening report."""
        
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_stocks_analyzed': len(scored_df),
            'filters': {},
            'top_performers': {},
            'sector_analysis': {},
            'market_summary': {}
        }
        
        # Filter summaries
        for filter_name, filter_df in filters.items():
            if len(filter_df) > 0:
                # Score and sort
                filter_scored = self.score_stocks(filter_df)
                top_stocks = filter_scored.nlargest(min(top_n, len(filter_scored)), 'overall_score')
                
                report['filters'][filter_name] = {
                    'count': len(filter_df),
                    'top_stocks': top_stocks[['symbol', 'sector', 'close', 'overall_score', 
                                            'ema_crossover_signal', 'ma_crossover_signal', 
                                            'rsi', 'volume_ratio']].to_dict('records')
                }
        
        # Top performers overall
        top_performers = scored_df.nlargest(top_n, 'overall_score')
        report['top_performers'] = {
            'by_overall_score': top_performers[['symbol', 'sector', 'close', 'overall_score',
                                             'technical_score', 'momentum_score', 'trend_score']].to_dict('records'),
            'by_technical_score': scored_df.nlargest(top_n, 'technical_score')[['symbol', 'sector', 'close', 'technical_score']].to_dict('records'),
            'by_momentum_score': scored_df.nlargest(top_n, 'momentum_score')[['symbol', 'sector', 'close', 'momentum_score']].to_dict('records')
        }
        
        # Sector analysis
        sector_summary = scored_df.groupby('sector').agg({
            'overall_score': ['mean', 'max', 'count'],
            'ema_crossover_signal': 'mean',
            'ma_crossover_signal': 'mean',
            'volume_ratio': 'mean'
        }).round(2)
        
        sector_summary.columns = ['avg_score', 'max_score', 'stock_count', 'avg_ema_signal', 'avg_ma_signal', 'avg_volume_ratio']
        report['sector_analysis'] = sector_summary.to_dict('index')
        
        # Market summary
        report['market_summary'] = {
            'avg_overall_score': float(scored_df['overall_score'].mean()),
            'bullish_ema_count': int((scored_df['ema_crossover_signal'] > 0).sum()),
            'bearish_ema_count': int((scored_df['ema_crossover_signal'] < 0).sum()),
            'bullish_ma_count': int((scored_df['ma_crossover_signal'] > 0).sum()),
            'bearish_ma_count': int((scored_df['ma_crossover_signal'] < 0).sum()),
            'high_volume_count': int((scored_df['volume_ratio'] > 1.5).sum()),
            'overbought_count': int((scored_df['rsi'] > 70).sum()),
            'oversold_count': int((scored_df['rsi'] < 30).sum())
        }
        
        return report
    
    def save_report(self, report: Dict, format: str = 'json') -> str:
        """Save screening report to file."""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            filename = f"daily_screening_report_{timestamp}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
                
        elif format == 'excel':
            filename = f"daily_screening_report_{timestamp}.xlsx"
            filepath = self.output_dir / filename
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    'Metric': ['Total Stocks', 'Avg Score', 'Bullish EMA', 'Bearish EMA', 
                              'Bullish MA', 'Bearish MA', 'High Volume', 'Overbought', 'Oversold'],
                    'Value': [
                        report['total_stocks_analyzed'],
                        round(report['market_summary']['avg_overall_score'], 2),
                        report['market_summary']['bullish_ema_count'],
                        report['market_summary']['bearish_ema_count'],
                        report['market_summary']['bullish_ma_count'],
                        report['market_summary']['bearish_ma_count'],
                        report['market_summary']['high_volume_count'],
                        report['market_summary']['overbought_count'],
                        report['market_summary']['oversold_count']
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Top performers
                if 'top_performers' in report:
                    pd.DataFrame(report['top_performers']['by_overall_score']).to_excel(
                        writer, sheet_name='Top Overall', index=False)
                
                # Each filter
                for filter_name, filter_data in report['filters'].items():
                    if filter_data['count'] > 0:
                        pd.DataFrame(filter_data['top_stocks']).to_excel(
                            writer, sheet_name=filter_name[:31], index=False)  # Excel sheet name limit
        
        logger.info(f"Report saved: {filepath}")
        return str(filepath)
    
    def run_daily_screening(self, 
                          top_n: int = 20, 
                          save_format: str = 'both') -> Dict:
        """Run complete daily screening process."""
        
        logger.info("🚀 Starting Daily Stock Screening...")
        logger.info("=" * 60)
        
        # Load data
        df = self.load_latest_data()
        
        # Calculate indicators
        df_with_indicators = self.calculate_all_indicators(df)
        
        # Create filters
        logger.info("Creating screening filters...")
        filters = self.create_screening_filters(df_with_indicators)
        
        # Score all stocks
        logger.info("Scoring all stocks...")
        latest_df = df_with_indicators.groupby('symbol').tail(1).reset_index(drop=True)
        scored_df = self.score_stocks(latest_df)
        
        # Generate report
        logger.info("Generating daily report...")
        report = self.generate_daily_report(filters, scored_df, top_n)
        
        # Save reports
        saved_files = []
        if save_format in ['json', 'both']:
            saved_files.append(self.save_report(report, 'json'))
        if save_format in ['excel', 'both']:
            saved_files.append(self.save_report(report, 'excel'))
        
        # Print summary
        logger.info("📊 Screening Summary:")
        logger.info(f"- Total stocks analyzed: {report['total_stocks_analyzed']}")
        logger.info(f"- Average market score: {report['market_summary']['avg_overall_score']:.1f}/100")
        logger.info(f"- Bullish signals (EMA): {report['market_summary']['bullish_ema_count']}")
        logger.info(f"- Bullish signals (MA): {report['market_summary']['bullish_ma_count']}")
        logger.info(f"- High volume stocks: {report['market_summary']['high_volume_count']}")
        
        logger.info("\n📋 Filter Results:")
        for filter_name, filter_data in report['filters'].items():
            if filter_data['count'] > 0:
                logger.info(f"- {filter_name}: {filter_data['count']} stocks")
        
        logger.info(f"\n💾 Reports saved: {saved_files}")
        logger.info("✅ Daily screening complete!")
        
        return report

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Daily Stock Screener')
    parser.add_argument('--output-dir', type=str, 
                       help='Output directory for reports (mặc định: DATA/processed/technical/screening dưới project root)')
    parser.add_argument('--top-n', type=int, default=20,
                       help='Number of top stocks to show in each filter')
    parser.add_argument('--format', type=str, choices=['json', 'excel', 'both'], 
                       default='both', help='Output format')
    
    args = parser.parse_args()
    
    # Run screening
    screener = StockScreener(output_dir=args.output_dir)
    report = screener.run_daily_screening(top_n=args.top_n, save_format=args.format)
    
    return report

if __name__ == '__main__':
    main()

