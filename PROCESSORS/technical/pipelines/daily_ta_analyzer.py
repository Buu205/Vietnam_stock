"""
Daily Technical Analyzer
=====================

Standalone module for daily technical analysis.
Focuses on price patterns, indicators, and trading signals for daily decisions.

Author: AI Assistant
Date: 2025-12-09
Version: 1.0.0
"""

import logging
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add project root to path
current_dir = Path(__file__).resolve().parent
# Calculate project root by going up from technical/ to Vietnam_dashboard/
project_root = current_dir.parent.parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config.registries import SectorRegistry
from PROCESSORS.core.shared.unified_mapper import UnifiedTickerMapper
from WEBAPP.core.utils import get_data_path

logger = logging.getLogger(__name__)


class DailyTAAnalyzer:
    """
    Standalone analyzer for daily technical analysis.
    
    Focuses on technical indicators and trading signals without fundamental data.
    Provides daily trading decisions based on price action and indicators.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize with optional configuration.
        
        Args:
            config: Configuration dictionary for analysis weights and options
        """
        self.sector_registry = SectorRegistry()
        self.ticker_mapper = UnifiedTickerMapper()
        self.config = config or self._get_default_config()
        
        # Pre-load technical data paths
        self._technical_paths = {
            "ohlcv": get_data_path("DATA/raw/ohlcv/OHLCV_mktcap.parquet"),
            "ma": get_data_path("DATA/processed/technical/moving_averages/ma_all_symbols.parquet"),
            "ema": get_data_path("DATA/processed/technical/exponential_moving_averages/ema_all_symbols.parquet"),
            "rsi": get_data_path("DATA/processed/technical/rsi/rsi_all_symbols.parquet"),
            "macd": get_data_path("DATA/processed/technical/macd/macd_all_symbols.parquet"),
            "bollinger": get_data_path("DATA/processed/technical/bollinger_bands/bb_all_symbols.parquet"),
            "atr": get_data_path("DATA/processed/technical/atr/atr_all_symbols.parquet"),
            "volume": get_data_path("DATA/processed/technical/volume/volume_analysis.parquet"),
            "market_breadth": get_data_path("DATA/processed/technical/market_breadth/market_breadth_daily.parquet")
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration for TA analysis.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "weights": {
                "trend": 0.3,
                "momentum": 0.3,
                "volume": 0.2,
                "volatility": 0.2
            },
            "indicators": {
                "enabled": {
                    "ma": True,
                    "ema": True,
                    "rsi": True,
                    "macd": True,
                    "bollinger": True,
                    "atr": True,
                    "volume": True
                }
            },
            "signals": {
                "trend_periods": [5, 10, 20],
                "rsi_period": 14,
                "rsi_oversold": 30,
                "rsi_overbought": 70,
                "volume_spike_multiplier": 1.5,
                "ma_crossover_periods": [20, 50],
                "atr_multiplier": 2.0,
                "price_change_threshold": 3.0  # Percentage
            },
            "display": {
                "chart_height": 500,
                "chart_colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
                "show_data_labels": True
            }
        }
    
    def analyze_ticker(self, ticker: str, days: int = 60) -> Dict[str, Any]:
        """
        Analyze technical indicators for a specific ticker.
        
        Args:
            ticker: Ticker symbol to analyze
            days: Number of recent days to analyze
            
        Returns:
            Dictionary with technical analysis and trading signals
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
            
        logger.info(f"Analyzing TA for ticker: {ticker}, days: {days}")
        
        # Get ticker info
        try:
            ticker_info = self.ticker_mapper.get_complete_info(ticker)
            if not ticker_info:
                raise ValueError(f"Ticker {ticker} not found")
        except Exception as e:
            logger.error(f"Error getting ticker info: {e}")
            raise ValueError(f"Invalid ticker: {ticker}")
        
        # Load data
        ohlcv_data = self._load_ohlcv_data(ticker, days)
        indicators_data = self._load_indicators_data(ticker, days)
        
        # Merge data
        merged_data = self._merge_technical_data(ohlcv_data, indicators_data)
        
        # Calculate signals
        signals = self._calculate_trading_signals(merged_data)
        
        # Calculate trend analysis
        trend_analysis = self._analyze_trends(merged_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(merged_data, signals, trend_analysis)
        
        # Create final structure
        analysis = {
            "metadata": {
                "ticker": ticker,
                "company_name": ticker_info.get("company_name", ""),
                "sector": ticker_info.get("sector", ""),
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "days_analyzed": days,
                "latest_date": merged_data["latest_date"] if merged_data else "",
                "data_sources": ["ohlcv", "technical_indicators"],
                "last_updated": datetime.now().isoformat()
            },
            "price_data": merged_data.get("price_data", {}),
            "indicators": merged_data.get("indicators", {}),
            "signals": signals,
            "trend_analysis": trend_analysis,
            "recommendations": recommendations
        }
        
        return analysis
    
    def analyze_sector(self, sector: str, days: int = 60) -> Dict[str, Any]:
        """
        Analyze technical indicators for all tickers in a sector.
        
        Args:
            sector: Sector name to analyze
            days: Number of recent days to analyze
            
        Returns:
            Dictionary with sector technical analysis
        """
        if not sector or not isinstance(sector, str):
            raise ValueError("Sector must be a non-empty string")
            
        logger.info(f"Analyzing TA for sector: {sector}, days: {days}")
        
        # Get all tickers in sector
        try:
            sector_tickers = self.sector_registry.get_tickers_by_sector(sector)
            if not sector_tickers:
                raise ValueError(f"No tickers found for sector: {sector}")
        except Exception as e:
            logger.error(f"Error getting sector tickers: {e}")
            raise ValueError(f"Invalid sector: {sector}")
        
        # Analyze each ticker
        ticker_analyses = []
        for ticker in sector_tickers:
            try:
                analysis = self.analyze_ticker(ticker, days)
                if "error" not in analysis:
                    ticker_analyses.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing ticker {ticker}: {e}")
                # Add placeholder with error
                ticker_analyses.append({
                    "metadata": {
                        "ticker": ticker,
                        "error": str(e)
                    }
                })
        
        # Calculate sector aggregates
        sector_aggregates = self._calculate_sector_ta_aggregates(ticker_analyses, sector)
        
        # Generate sector insights
        sector_insights = self._generate_sector_ta_insights(ticker_analyses, sector_aggregates, sector)
        
        # Create final structure
        sector_analysis = {
            "metadata": {
                "sector": sector,
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "ticker_count": len(ticker_analyses),
                "days_analyzed": days,
                "data_sources": ["ohlcv", "technical_indicators"],
                "last_updated": datetime.now().isoformat()
            },
            "ticker_analyses": ticker_analyses,
            "sector_aggregates": sector_aggregates,
            "insights": sector_insights
        }
        
        return sector_analysis
    
    def _load_ohlcv_data(self, ticker: str, days: int) -> Dict[str, Any]:
        """
        Load OHLCV data for a ticker.
        
        Args:
            ticker: Ticker symbol
            days: Number of recent days
            
        Returns:
            Dictionary with OHLCV data
        """
        try:
            # Load OHLCV data
            df = pd.read_parquet(self._technical_paths["ohlcv"])
            
            # Filter by ticker and date
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df['symbol'] == ticker]
            
            if 'date' in df.columns:
                df = df[pd.to_datetime(df['date']) >= cutoff_date]
            
            if df.empty:
                return {}
            
            # Get latest data
            latest = df.sort_values('date').iloc[-1]
            
            # Calculate basic metrics
            data = {
                "latest_date": latest['date'].strftime("%Y-%m-%d"),
                "open": latest.get('open', 0),
                "high": latest.get('high', 0),
                "low": latest.get('low', 0),
                "close": latest.get('close', 0),
                "volume": latest.get('volume', 0),
                "trading_value": latest.get('trading_value', 0),
                
                # Calculate daily changes
                "daily_change": 0,
                "daily_change_pct": 0,
                "volatility_20": 0  # 20-day volatility
            }
            
            # Calculate price changes if we have at least 2 days
            if len(df) >= 2:
                df_sorted = df.sort_values('date')
                prev = df_sorted.iloc[-2]
                cur = df_sorted.iloc[-1]
                
                data["daily_change"] = cur['close'] - prev['close']
                data["daily_change_pct"] = ((cur['close'] - prev['close']) / prev['close']) * 100
            
            # Calculate 20-day volatility
            if len(df) >= 20:
                df_20 = df_sorted.tail(20)
                df_20['daily_return'] = df_20['close'].pct_change()
                data["volatility_20"] = df_20['daily_return'].std() * np.sqrt(252) * 100  # Annualized
            
            return {
                "price_data": data,
                "historical_data": df.sort_values('date').to_dict('records')
            }
                
        except Exception as e:
            logger.error(f"Error loading OHLCV data: {e}")
            return {}
    
    def _load_indicators_data(self, ticker: str, days: int) -> Dict[str, Any]:
        """
        Load technical indicators data for a ticker.
        
        Args:
            ticker: Ticker symbol
            days: Number of recent days
            
        Returns:
            Dictionary with indicators data
        """
        indicators = {}
        
        # Load each indicator
        for indicator_type, path in self._technical_paths.items():
            if indicator_type == "ohlcv" or indicator_type == "volume" or indicator_type == "market_breadth":
                continue  # Skip these as they're handled elsewhere
                
            if not self.config.get("indicators", {}).get("enabled", {}).get(indicator_type.split("_")[0], False):
                continue
                
            try:
                df = pd.read_parquet(path)
                
                # Filter by ticker and date
                cutoff_date = datetime.now() - timedelta(days=days)
                df = df[df['symbol'] == ticker]
                
                if 'date' in df.columns:
                    df = df[pd.to_datetime(df['date']) >= cutoff_date]
                
                if df.empty:
                    continue
                
                # Get latest data
                latest = df.sort_values('date').iloc[-1]
                
                # Add to indicators dict
                indicator_data = {}
                for col in df.columns:
                    if col != 'symbol' and col != 'date':  # Skip symbol and date columns
                        indicator_data[col] = latest.get(col)
                
                indicators[indicator_type] = {
                    "latest_date": latest['date'].strftime("%Y-%m-%d") if 'date' in latest else "",
                    "data": indicator_data,
                    "historical_data": df.sort_values('date').to_dict('records')
                }
                
            except Exception as e:
                logger.error(f"Error loading {indicator_type} data: {e}")
        
        return {"indicators": indicators}
    
    def _merge_technical_data(self, ohlcv_data: Dict, indicators_data: Dict) -> Dict[str, Any]:
        """
        Merge OHLCV and indicators data.
        
        Args:
            ohlcv_data: OHLCV data dictionary
            indicators_data: Indicators data dictionary
            
        Returns:
            Merged technical data dictionary
        """
        merged = {
            "price_data": ohlcv_data.get("price_data", {}),
            "indicators": indicators_data.get("indicators", {}),
            "latest_date": max(
                ohlcv_data.get("price_data", {}).get("latest_date", ""),
                indicators_data.get("indicators", {}).get("ma", {}).get("latest_date", ""),
                indicators_data.get("indicators", {}).get("rsi", {}).get("latest_date", "")
            )
        }
        
        return merged
    
    def _calculate_trading_signals(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate trading signals from technical data.
        
        Args:
            data: Merged technical data
            
        Returns:
            Dictionary with trading signals
        """
        signals = {
            "trend_signals": {},
            "momentum_signals": {},
            "volume_signals": {},
            "volatility_signals": {},
            "overall_signal": {
                "action": "HOLD",
                "strength": 50,
                "confidence": 0.5
            }
        }
        
        price_data = data.get("price_data", {})
        indicators = data.get("indicators", {})
        
        # Get current price
        close = price_data.get("close", 0)
        volume = price_data.get("volume", 0)
        
        # Trend signals
        ma_data = indicators.get("ma", {})
        if ma_data and close:
            # MA crossover signals
            ma20 = ma_data.get("sma_20", 0)
            ma50 = ma_data.get("sma_50", 0)
            ma200 = ma_data.get("sma_200", 0)
            
            if ma20 and ma50 and ma200:
                signals["trend_signals"] = {
                    "ma20_above": close > ma20,
                    "ma50_above": close > ma50,
                    "ma200_above": close > ma200,
                    "ma20_ma50_bullish": ma20 > ma50,
                    "ma50_ma200_bullish": ma50 > ma200,
                    "golden_cross": ma50 > ma200 and close > ma50 and close > ma20,  # Bullish signal
                    "death_cross": ma50 < ma200 and close < ma50 and close < ma20  # Bearish signal
                }
        
        # Momentum signals
        rsi_data = indicators.get("rsi", {})
        if rsi_data:
            rsi = rsi_data.get("rsi_14", 50)
            signals["momentum_signals"] = {
                "rsi": rsi,
                "oversold": rsi < 30,
                "overbought": rsi > 70,
                "neutral": 30 <= rsi <= 70
            }
        
        # MACD signals
        macd_data = indicators.get("macd", {})
        if macd_data:
            macd = macd_data.get("macd", 0)
            macd_signal = macd_data.get("signal", 0)
            histogram = macd_data.get("histogram", 0)
            
            signals["momentum_signals"]["macd"] = {
                "macd": macd,
                "signal": macd_signal,
                "histogram": histogram,
                "bullish_crossover": macd > macd_signal and histogram > 0,
                "bearish_crossover": macd < macd_signal and histogram < 0,
                "divergence": False  # Simplified - would need more complex analysis
            }
        
        # Bollinger signals
        bollinger_data = indicators.get("bollinger", {})
        if bollinger_data and close:
            upper = bollinger_data.get("upper_band", 0)
            lower = bollinger_data.get("lower_band", 0)
            middle = bollinger_data.get("middle_band", 0)
            percent_b = bollinger_data.get("percent_b", 0.5)  # Middle by default
            
            signals["volatility_signals"]["bollinger"] = {
                "above_upper": close > upper,
                "below_lower": close < lower,
                "percent_b": percent_b,
                "squeeze": upper - lower < (middle * 0.1)  # Low volatility
            }
        
        # Volume signals
        avg_volume = self._calculate_avg_volume(data)
        if avg_volume and volume:
            volume_multiplier = self.config.get("signals", {}).get("volume_spike_multiplier", 1.5)
            
            signals["volume_signals"] = {
                "above_average": volume > (avg_volume * volume_multiplier),
                "volume_ratio": volume / avg_volume if avg_volume > 0 else 1,
                "accumulation": False,  # Would need volume analysis over multiple days
                "distribution": False    # Would need volume analysis over multiple days
            }
        
        # Calculate overall signal
        trend_score = 0
        momentum_score = 0
        volume_score = 0
        
        # Trend score
        if "trend_signals" in signals:
            trend_signals = signals["trend_signals"]
            if trend_signals:
                # Golden cross (very bullish)
                if trend_signals.get("golden_cross"):
                    trend_score = 90
                # Death cross (very bearish)
                elif trend_signals.get("death_cross"):
                    trend_score = 10
                # General trend
                else:
                    ma_above_score = 0
                    if trend_signals.get("ma20_above"):
                        ma_above_score += 30
                    if trend_signals.get("ma50_above"):
                        ma_above_score += 30
                    if trend_signals.get("ma200_above"):
                        ma_above_score += 40
                    
                    trend_score = ma_above_score
        
        # Momentum score
        if "momentum_signals" in signals:
            momentum_signals = signals["momentum_signals"]
            if momentum_signals:
                rsi = momentum_signals.get("rsi", 50)
                if 40 <= rsi <= 60:  # Neutral but not overbought/oversold
                    momentum_score = 70
                elif 60 < rsi <= 70:  # Slightly bullish
                    momentum_score = 85
                elif 30 <= rsi < 40:  # Slightly bearish
                    momentum_score = 30
                elif rsi > 70:  # Overbought
                    momentum_score = 20
                elif rsi < 30:  # Oversold
                    momentum_score = 80  # Potential reversal
        
        # Volume score
        if "volume_signals" in signals:
            volume_signals = signals["volume_signals"]
            if volume_signals:
                vol_ratio = volume_signals.get("volume_ratio", 1)
                if vol_ratio > 2:
                    volume_score = 90
                elif vol_ratio > 1.5:
                    volume_score = 75
                elif vol_ratio > 1.2:
                    volume_score = 60
                elif vol_ratio > 0.8:
                    volume_score = 40
                else:
                    volume_score = 20
        
        # Calculate weighted overall signal
        weights = self.config.get("weights", {})
        trend_weight = weights.get("trend", 0.3)
        momentum_weight = weights.get("momentum", 0.3)
        volume_weight = weights.get("volume", 0.2)
        volatility_weight = weights.get("volatility", 0.2)
        
        # Calculate weighted score
        weighted_score = (trend_score * trend_weight) + (momentum_score * momentum_weight) + (volume_score * volume_weight)
        
        # Convert to 0-100 scale
        normalized_score = max(0, min(100, weighted_score))
        
        # Determine action
        if normalized_score > 70:
            action = "BUY"
            strength = 90
        elif normalized_score > 60:
            action = "WEAK_BUY"
            strength = 70
        elif normalized_score > 40:
            action = "HOLD"
            strength = 50
        elif normalized_score > 30:
            action = "WEAK_SELL"
            strength = 30
        else:
            action = "SELL"
            strength = 10
        
        # Calculate confidence based on signal consistency
        confidence = 0.5  # Default
        if "trend_signals" in signals and "momentum_signals" in signals:
            trend_action = "BUY" if trend_score > 50 else "SELL"
            momentum_action = "BUY" if momentum_score > 50 else "SELL"
            
            if trend_action == momentum_action:
                confidence = 0.8  # High confidence when aligned
            else:
                confidence = 0.4  # Lower confidence when conflicting
        
        signals["overall_signal"] = {
            "action": action,
            "strength": strength,
            "confidence": confidence,
            "score": normalized_score,
            "components": {
                "trend_score": trend_score,
                "momentum_score": momentum_score,
                "volume_score": volume_score,
                "weighted_score": weighted_score
            }
        }
        
        return signals
    
    def _calculate_avg_volume(self, data: Dict[str, Any]) -> float:
        """
        Calculate average volume from historical data.
        
        Args:
            data: Technical data dictionary
            
        Returns:
            Average volume
        """
        # This is a simplified implementation
        # In a real system, this would use more historical data
        indicators = data.get("indicators", {})
        
        # Try to get volume from various sources
        if "volume" in indicators:
            vol_data = indicators["volume"].get("data", {})
            if vol_data and "historical_data" in vol_data:
                df = pd.DataFrame(vol_data["historical_data"])
                if "volume" in df.columns:
                    return df["volume"].mean()
        
        return 0  # Default if no data available
    
    def _analyze_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze price and indicator trends.
        
        Args:
            data: Merged technical data
            
        Returns:
            Dictionary with trend analysis
        """
        trends = {
            "short_term": {"direction": "NEUTRAL", "strength": 0},
            "medium_term": {"direction": "NEUTRAL", "strength": 0},
            "long_term": {"direction": "NEUTRAL", "strength": 0},
            "support_resistance": {}
        }
        
        # Get historical data if available
        historical = []
        price_data = data.get("price_data", {})
        if "historical_data" in price_data:
            historical = price_data["historical_data"][-20:]  # Last 20 days
        elif "historical_data" in data.get("indicators", {}).get("ma", {}):
            historical = data["indicators"]["ma"]["historical_data"][-20:]  # Last 20 days
        
        if len(historical) < 10:
            return trends
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(historical)
        
        # Short-term trend (5 days)
        if len(df) >= 5:
            df_5 = df.tail(5)
            close_5 = df_5["close"]
            if len(close_5) >= 3:
                # Simple linear regression to determine trend
                x = np.arange(len(close_5))
                slope, _ = np.polyfit(x, close_5, 1)
                
                if slope > 0.1:
                    trends["short_term"]["direction"] = "UP"
                    trends["short_term"]["strength"] = min(100, slope * 100)
                elif slope < -0.1:
                    trends["short_term"]["direction"] = "DOWN"
                    trends["short_term"]["strength"] = min(100, abs(slope * 100))
                else:
                    trends["short_term"]["direction"] = "SIDEWAYS"
                    trends["short_term"]["strength"] = 10
        
        # Medium-term trend (10 days)
        if len(df) >= 10:
            df_10 = df.tail(10)
            close_10 = df_10["close"]
            if len(close_10) >= 5:
                x = np.arange(len(close_10))
                slope, _ = np.polyfit(x, close_10, 1)
                
                if slope > 0.05:
                    trends["medium_term"]["direction"] = "UP"
                    trends["medium_term"]["strength"] = min(100, slope * 100)
                elif slope < -0.05:
                    trends["medium_term"]["direction"] = "DOWN"
                    trends["medium_term"]["strength"] = min(100, abs(slope * 100))
                else:
                    trends["medium_term"]["direction"] = "SIDEWAYS"
                    trends["medium_term"]["strength"] = 10
        
        # Long-term trend (20 days)
        if len(df) >= 20:
            df_20 = df.tail(20)
            close_20 = df_20["close"]
            if len(close_20) >= 10:
                x = np.arange(len(close_20))
                slope, _ = np.polyfit(x, close_20, 1)
                
                if slope > 0.02:
                    trends["long_term"]["direction"] = "UP"
                    trends["long_term"]["strength"] = min(100, slope * 100)
                elif slope < -0.02:
                    trends["long_term"]["direction"] = "DOWN"
                    trends["long_term"]["strength"] = min(100, abs(slope * 100))
                else:
                    trends["long_term"]["direction"] = "SIDEWAYS"
                    trends["long_term"]["strength"] = 10
        
        # Support and resistance levels
        if len(df) >= 20:
            highs = df["high"].max()
            lows = df["low"].min()
            
            # Find recent support and resistance
            recent = df.tail(10)
            recent_high = recent["high"].max()
            recent_low = recent["low"].min()
            
            trends["support_resistance"] = {
                "resistance": highs,
                "support": lows,
                "recent_resistance": recent_high,
                "recent_support": recent_low
            }
        
        return trends
    
    def _generate_recommendations(self, data: Dict[str, Any], signals: Dict[str, Any], trends: Dict[str, Any]) -> List[str]:
        """
        Generate trading recommendations based on analysis.
        
        Args:
            data: Merged technical data
            signals: Trading signals
            trends: Trend analysis
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Get overall signal
        if "overall_signal" in signals:
            overall = signals["overall_signal"]
            action = overall.get("action", "HOLD")
            confidence = overall.get("confidence", 0.5)
            score = overall.get("score", 50)
            
            if action == "BUY":
                if confidence > 0.7:
                    recommendations.append(f"Strong BUY signal with {score:.1f} score and {confidence:.1f} confidence")
                    recommendations.append("Consider entering a long position")
                else:
                    recommendations.append(f"BUY signal with {score:.1f} score and {confidence:.1f} confidence")
                    recommendations.append("Monitor for confirmation before entering")
            
            elif action == "SELL":
                if confidence > 0.7:
                    recommendations.append(f"Strong SELL signal with {score:.1f} score and {confidence:.1f} confidence")
                    recommendations.append("Consider closing long positions or entering short")
                else:
                    recommendations.append(f"SELL signal with {score:.1f} score and {confidence:.1f} confidence")
                    recommendations.append("Monitor for confirmation before acting")
            
            elif action == "WEAK_BUY":
                recommendations.append(f"Weak BUY signal with {score:.1f} score")
                recommendations.append("Wait for stronger confirmation")
            
            elif action == "WEAK_SELL":
                recommendations.append(f"Weak SELL signal with {score:.1f} score")
                recommendations.append("Consider taking partial profits")
            
            else:  # HOLD
                recommendations.append("HOLD signal - maintain current position")
                recommendations.append("Wait for clearer signals before making changes")
        
        # Trend-based recommendations
        if "short_term" in trends and "medium_term" in trends:
            st_trend = trends["short_term"]["direction"]
            mt_trend = trends["medium_term"]["direction"]
            
            if st_trend == "UP" and mt_trend == "UP":
                recommendations.append("Both short and medium term trends are UP - bullish outlook")
            elif st_trend == "DOWN" and mt_trend == "DOWN":
                recommendations.append("Both short and medium term trends are DOWN - bearish outlook")
            elif st_trend == "UP" and mt_trend == "SIDEWAYS":
                recommendations.append("Short term UP but medium term SIDEWAYS - wait for confirmation")
            elif st_trend == "SIDEWAYS" and mt_trend == "UP":
                recommendations.append("Short term SIDEWAYS but medium term UP - watch for breakout")
        
        # Indicator-specific recommendations
        indicators = data.get("indicators", {})
        
        # RSI recommendations
        if "momentum_signals" in signals:
            rsi = signals["momentum_signals"].get("rsi", 50)
            if rsi < 30:
                recommendations.append("RSI indicates oversold condition - potential bounce opportunity")
            elif rsi > 70:
                recommendations.append("RSI indicates overbought condition - potential correction")
        
        # MA crossover recommendations
        if "trend_signals" in signals:
            trend_signals = signals["trend_signals"]
            if trend_signals.get("golden_cross"):
                recommendations.append("Golden cross detected (50MA above 200MA) - bullish signal")
            elif trend_signals.get("death_cross"):
                recommendations.append("Death cross detected (50MA below 200MA) - bearish signal")
        
        # Bollinger Bands recommendations
        if "volatility_signals" in signals:
            bollinger = signals["volatility_signals"].get("bollinger", {})
            if bollinger:
                percent_b = bollinger.get("percent_b", 0.5)
                if percent_b > 0.9:
                    recommendations.append("Price near upper Bollinger Band - potential resistance")
                elif percent_b < 0.1:
                    recommendations.append("Price near lower Bollinger Band - potential support")
                elif bollinger.get("squeeze"):
                    recommendations.append("Bollinger Band squeeze detected - watch for breakout")
        
        return recommendations
    
    def _calculate_sector_ta_aggregates(self, ticker_analyses: List[Dict], sector: str) -> Dict[str, Any]:
        """
        Calculate sector-level technical aggregates.
        
        Args:
            ticker_analyses: List of ticker analyses
            sector: Sector name
            
        Returns:
            Dictionary with sector technical aggregates
        """
        if not ticker_analyses:
            return {}
        
        # Extract valid analyses
        valid_analyses = [a for a in ticker_analyses if "error" not in a]
        if not valid_analyses:
            return {}
        
        # Create DataFrame for analysis
        df = pd.DataFrame([{
            "ticker": a.get("metadata", {}).get("ticker", ""),
            "signal": a.get("signals", {}).get("overall_signal", {}),
            "trend_short": a.get("trend_analysis", {}).get("short_term", {}).get("direction", "NEUTRAL"),
            "trend_medium": a.get("trend_analysis", {}).get("medium_term", {}).get("direction", "NEUTRAL"),
            "trend_long": a.get("trend_analysis", {}).get("long_term", {}).get("direction", "NEUTRAL")
        } for a in valid_analyses])
        
        aggregates = {
            "sector_name": sector,
            "ticker_count": len(valid_analyses),
            "signal_distribution": {},
            "trend_distribution": {},
            "strength_distribution": {},
            "sector_ranking": {}
        }
        
        # Signal distribution
        signal_counts = df["signal"].apply(lambda x: x.get("action", "HOLD") if isinstance(x, dict) else "HOLD").value_counts()
        total = signal_counts.sum()
        
        if total > 0:
            aggregates["signal_distribution"] = {
                "buy": int(signal_counts.get("BUY", 0) + signal_counts.get("WEAK_BUY", 0)),
                "hold": int(signal_counts.get("HOLD", 0)),
                "sell": int(signal_counts.get("SELL", 0) + signal_counts.get("WEAK_SELL", 0)),
                "buy_pct": round((signal_counts.get("BUY", 0) + signal_counts.get("WEAK_BUY", 0)) / total * 100, 1),
                "sell_pct": round((signal_counts.get("SELL", 0) + signal_counts.get("WEAK_SELL", 0)) / total * 100, 1),
                "hold_pct": round(signal_counts.get("HOLD", 0) / total * 100, 1)
            }
        
        # Trend distribution
        trend_short = df["trend_short"].value_counts()
        trend_medium = df["trend_medium"].value_counts()
        trend_long = df["trend_long"].value_counts()
        
        aggregates["trend_distribution"] = {
            "short_term": {
                "up": int(trend_short.get("UP", 0)),
                "down": int(trend_short.get("DOWN", 0)),
                "sideways": int(trend_short.get("NEUTRAL", 0)),
                "up_pct": round(trend_short.get("UP", 0) / len(valid_analyses) * 100, 1),
                "down_pct": round(trend_short.get("DOWN", 0) / len(valid_analyses) * 100, 1)
            },
            "medium_term": {
                "up": int(trend_medium.get("UP", 0)),
                "down": int(trend_medium.get("DOWN", 0)),
                "sideways": int(trend_medium.get("NEUTRAL", 0)),
                "up_pct": round(trend_medium.get("UP", 0) / len(valid_analyses) * 100, 1),
                "down_pct": round(trend_medium.get("DOWN", 0) / len(valid_analyses) * 100, 1)
            },
            "long_term": {
                "up": int(trend_long.get("UP", 0)),
                "down": int(trend_long.get("DOWN", 0)),
                "sideways": int(trend_long.get("NEUTRAL", 0)),
                "up_pct": round(trend_long.get("UP", 0) / len(valid_analyses) * 100, 1),
                "down_pct": round(trend_long.get("DOWN", 0) / len(valid_analyses) * 100, 1)
            }
        }
        
        # Strength distribution
        if "signal" in df.columns:
            df["strength"] = df["signal"].apply(lambda x: x.get("strength", 50) if isinstance(x, dict) else 50)
            strength_stats = df["strength"].describe()
            
            aggregates["strength_distribution"] = {
                "mean": round(strength_stats["mean"], 1),
                "median": round(strength_stats["50%"], 1),
                "min": round(strength_stats["min"], 1),
                "max": round(strength_stats["max"], 1),
                "strong": int(df[df["strength"] > 70].shape[0]),
                "weak": int(df[df["strength"] < 30].shape[0])
            }
        
        # Sector ranking
        if "signal" in df.columns:
            df["score"] = df["signal"].apply(lambda x: x.get("score", 50) if isinstance(x, dict) else 50)
            sorted_df = df.sort_values("score", ascending=False)
            
            top_performers = []
            bottom_performers = []
            
            if not sorted_df.empty:
                top_performers = sorted_df.head(10)["ticker"].tolist()
                bottom_performers = sorted_df.tail(10)["ticker"].tolist()
            
            aggregates["sector_ranking"] = {
                "top_performers": top_performers,
                "bottom_performers": bottom_performers
            }
        
        return aggregates
    
    def _generate_sector_ta_insights(self, ticker_analyses: List[Dict], aggregates: Dict[str, Any], sector: str) -> Dict[str, Any]:
        """
        Generate technical insights for a sector.
        
        Args:
            ticker_analyses: List of ticker analyses
            aggregates: Sector aggregates
            sector: Sector name
            
        Returns:
            Dictionary with technical insights
        """
        insights = {
            "sector_overview": [],
            "signal_insights": [],
            "trend_insights": [],
            "momentum_insights": [],
            "recommendations": []
        }
        
        # Sector overview
        ticker_count = len(ticker_analyses)
        insights["sector_overview"].append(
            f"Sector {sector} contains {ticker_count} tickers with technical analysis"
        )
        
        # Signal distribution insights
        signal_dist = aggregates.get("signal_distribution", {})
        if signal_dist:
            buy_pct = signal_dist.get("buy_pct", 0)
            sell_pct = signal_dist.get("sell_pct", 0)
            hold_pct = signal_dist.get("hold_pct", 0)
            
            if buy_pct > 60:
                insights["signal_insights"].append(
                    f"Sector shows strong bullish momentum with {buy_pct:.1f}% BUY signals"
                )
            elif sell_pct > 60:
                insights["signal_insights"].append(
                    f"Sector shows strong bearish momentum with {sell_pct:.1f}% SELL signals"
                )
            elif hold_pct > 60:
                insights["signal_insights"].append(
                    f"Sector is mostly neutral with {hold_pct:.1f}% HOLD signals"
                )
            elif buy_pct > 40 and buy_pct < 60:
                insights["signal_insights"].append(
                    f"Sector shows moderate bullish sentiment with {buy_pct:.1f}% BUY signals"
                )
            elif sell_pct > 40 and sell_pct < 60:
                insights["signal_insights"].append(
                    f"Sector shows moderate bearish sentiment with {sell_pct:.1f}% SELL signals"
                )
        
        # Trend insights
        trend_dist = aggregates.get("trend_distribution", {})
        if trend_dist and "short_term" in trend_dist:
            short_up = trend_dist["short_term"].get("up_pct", 0)
            medium_up = trend_dist["medium_term"].get("up_pct", 0)
            long_up = trend_dist["long_term"].get("up_pct", 0)
            
            if short_up > 60 and medium_up > 60 and long_up > 60:
                insights["trend_insights"].append(
                    "Sector shows strong bullish trends across all timeframes"
                )
            elif short_up < 40 and medium_up < 40 and long_up < 40:
                insights["trend_insights"].append(
                    "Sector shows strong bearish trends across all timeframes"
                )
            elif 40 <= short_up <= 60:
                insights["trend_insights"].append(
                    "Sector shows mixed short-term trends"
                )
            else:
                insights["trend_insights"].append(
                    "Sector is mostly sideways in the short term"
                )
        
        # Strength distribution insights
        strength_dist = aggregates.get("strength_distribution", {})
        if strength_dist:
            strong_pct = (strength_dist.get("strong", 0) / ticker_count) * 100 if ticker_count > 0 else 0
            weak_pct = (strength_dist.get("weak", 0) / ticker_count) * 100 if ticker_count > 0 else 0
            
            if strong_pct > 60:
                insights["momentum_insights"].append(
                    f"Sector shows strong technical momentum with {strong_pct:.1f}% stocks scoring high"
                )
            elif weak_pct > 60:
                insights["momentum_insights"].append(
                    f"Sector shows weak technical momentum with {weak_pct:.1f}% stocks scoring low"
                )
            else:
                insights["momentum_insights"].append(
                    f"Sector shows moderate technical momentum"
                )
        
        # Generate recommendations
        ranking = aggregates.get("sector_ranking", {})
        top_performers = ranking.get("top_performers", [])
        
        if top_performers:
            # Focus on top 3 for recommendations
            top_3 = top_performers[:3]
            insights["recommendations"] = [
                f"Consider {top_3[0]} - highest technical score in sector"
            ]
            
            if len(top_3) >= 2:
                insights["recommendations"].append(
                    f"Consider {top_3[1]} - second highest technical score"
                )
            
            if len(top_3) >= 3:
                insights["recommendations"].append(
                    f"Consider {top_3[2]} - third highest technical score"
                )
            
            # Add sector-specific recommendations
            if "Ngân hàng" in sector:
                insights["recommendations"].append(
                    "Focus on banks with strong volume and bullish trends for best momentum"
                )
            elif "Bán lẻ" in sector:
                insights["recommendations"].append(
                    "Watch for volume spikes which may indicate institutional buying"
                )
            elif "Chứng khoán" in sector:
                insights["recommendations"].append(
                    "Prioritize stocks with consistent upward trends across multiple timeframes"
                )
        
        return insights
    
    def get_available_sectors(self) -> List[str]:
        """
        Get list of sectors with technical data.
        
        Returns:
            List of sector names
        """
        try:
            sectors = self.sector_registry.get_all_sectors()
            
            # Filter to only sectors with technical data
            sectors_with_data = []
            for sector in sectors:
                try:
                    tickers = self.sector_registry.get_tickers_by_sector(sector)
                    if tickers:  # Only include sectors with tickers
                        sectors_with_data.append(sector)
                except Exception:
                    continue
                    
            return sorted(sectors_with_data)
        except Exception as e:
            logger.error(f"Error getting available sectors: {e}")
            return []
    
    def get_sector_tickers(self, sector: str) -> List[str]:
        """
        Get all tickers in a sector.
        
        Args:
            sector: Sector name
            
        Returns:
            List of ticker symbols
        """
        if not sector:
            return []
            
        try:
            tickers = self.sector_registry.get_tickers_by_sector(sector)
            return tickers if tickers else []
        except Exception as e:
            logger.error(f"Error getting tickers for sector {sector}: {e}")
            return []


# Convenience function for quick ticker TA analysis
def analyze_ticker_ta(ticker: str, days: int = 60, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Quick function to analyze a ticker's technical indicators.
    
    Args:
        ticker: Ticker symbol to analyze
        days: Number of recent days to analyze
        config: Optional configuration
        
    Returns:
        Analysis result dictionary
    """
    analyzer = DailyTAAnalyzer(config)
    return analyzer.analyze_ticker(ticker, days)


# Convenience function for quick sector TA analysis
def analyze_sector_ta(sector: str, days: int = 60, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Quick function to analyze a sector's technical indicators.
    
    Args:
        sector: Sector name to analyze
        days: Number of recent days to analyze
        config: Optional configuration
        
    Returns:
        Analysis result dictionary
    """
    analyzer = DailyTAAnalyzer(config)
    return analyzer.analyze_sector(sector, days)