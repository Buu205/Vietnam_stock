"""
Valuation + Technical Decision Module
=====================================

Standalone module for combining valuation and technical analysis
to generate buy/sell trading decisions.

Author: AI Assistant
Date: 2025-12-09
Version: 1.0.0
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from ..core.registries.sector_lookup import SectorRegistry
from ..core.shared.unified_mapper import UnifiedTickerMapper
from WEBAPP.core.utils import get_data_path

logger = logging.getLogger(__name__)


class ValuationTAAnalyzer:
    """
    Analyzer combining valuation metrics with technical indicators
    to generate buy/sell/hold trading decisions.
    
    Focuses on using valuation (PE, PB, etc.) to determine fair value
    and technical indicators to determine optimal entry/exit points.
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
        
        # Pre-load valuation data paths
        self._valuation_paths = {
            "pe": get_data_path("DATA/processed/valuation/pe/pe_historical_all_symbols_final.parquet"),
            "pb": get_data_path("DATA/processed/valuation/pb/pb_historical_all_symbols_final.parquet"),
            "ev_ebitda": get_data_path("DATA/processed/valuation/ev_ebitda/ev_ebitda_historical_all_symbols_final.parquet")
        }
        
        # Pre-load technical data paths
        self._technical_paths = {
            "ohlcv": get_data_path("DATA/raw/ohlcv/OHLCV_mktcap.parquet"),
            "ma": get_data_path("DATA/processed/technical/moving_averages/ma_all_symbols.parquet"),
            "ema": get_data_path("DATA/processed/technical/exponential_moving_averages/ema_all_symbols.parquet"),
            "rsi": get_data_path("DATA/processed/technical/rsi/rsi_all_symbols.parquet"),
            "macd": get_data_path("DATA/processed/technical/macd/macd_all_symbols.parquet"),
            "bollinger": get_data_path("DATA/processed/technical/bollinger_bands/bb_all_symbols.parquet"),
            "atr": get_data_path("DATA/processed/technical/atr/atr_all_symbols.parquet"),
            "volume": get_data_path("DATA/processed/technical/volume/volume_analysis.parquet")
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration for Valuation+TA analysis.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "weights": {
                "valuation": 0.5,
                "technical": 0.5
            },
            "valuation_weights": {
                "pe_relative": 0.3,
                "pb_relative": 0.2,
                "ps_relative": 0.1,
                "ev_ebitda_relative": 0.2,
                "pe_absolute": 0.1,
                "pb_absolute": 0.05
            },
            "technical_weights": {
                "trend": 0.25,
                "momentum": 0.25,
                "oversold_overbought": 0.2,
                "volume_confirmation": 0.15,
                "volatility": 0.15
            },
            "decision_thresholds": {
                "strong_buy": 80,
                "buy": 65,
                "hold": 40,
                "sell": 35,
                "strong_sell": 20
            },
            "risk_adjustments": {
                "sector_pe_adjustment": True,
                "volatility_adjustment": True,
                "volume_weighting": True
            },
            "timeframes": {
                "short_term": 10,  # days
                "medium_term": 30,
                "long_term": 90
            }
        }
    
    def analyze_ticker(self, ticker: str, timeframe: str = "medium") -> Dict[str, Any]:
        """
        Analyze a ticker combining valuation and technical analysis.
        
        Args:
            ticker: Ticker symbol to analyze
            timeframe: Analysis timeframe ('short', 'medium', 'long')
            
        Returns:
            Dictionary with Valuation+TA analysis and decision
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
            
        logger.info(f"Analyzing Valuation+TA for ticker: {ticker}, timeframe: {timeframe}")
        
        # Get ticker info
        try:
            ticker_info = self.ticker_mapper.get_complete_info(ticker)
            if not ticker_info:
                raise ValueError(f"Ticker {ticker} not found")
        except Exception as e:
            logger.error(f"Error getting ticker info: {e}")
            raise ValueError(f"Invalid ticker: {ticker}")
        
        # Load valuation data
        valuation_data = self._load_valuation_data(ticker, timeframe)
        
        # Load technical data
        technical_data = self._load_technical_data(ticker, timeframe)
        
        # Merge data
        merged_data = {**valuation_data, **technical_data}
        
        # Calculate decision scores
        decision_scores = self._calculate_decision_scores(merged_data, ticker_info)
        
        # Generate final decision
        decision = self._generate_decision(decision_scores)
        
        # Create analysis summary
        analysis = self._generate_analysis(merged_data, decision_scores, decision)
        
        # Create final structure
        result = {
            "metadata": {
                "ticker": ticker,
                "company_name": ticker_info.get("company_name", ""),
                "sector": ticker_info.get("sector", ""),
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "timeframe": timeframe,
                "data_sources": ["valuation", "technical"],
                "last_updated": datetime.now().isoformat()
            },
            "valuation_data": valuation_data,
            "technical_data": technical_data,
            "decision_scores": decision_scores,
            "decision": decision,
            "analysis": analysis
        }
        
        return result
    
    def analyze_sector(self, sector: str, timeframe: str = "medium") -> Dict[str, Any]:
        """
        Analyze a sector combining valuation and technical analysis.
        
        Args:
            sector: Sector name to analyze
            timeframe: Analysis timeframe ('short', 'medium', 'long')
            
        Returns:
            Dictionary with sector Valuation+TA analysis
        """
        if not sector or not isinstance(sector, str):
            raise ValueError("Sector must be a non-empty string")
            
        logger.info(f"Analyzing Valuation+TA for sector: {sector}, timeframe: {timeframe}")
        
        # Get all tickers in sector
        try:
            sector_tickers = self.sector_registry.get_tickers_by_sector(sector)
            if not sector_tickers:
                raise ValueError(f"No tickers found for sector: {sector}")
        except Exception as e:
            logger.error(f"Error getting sector tickers: {e}")
            raise ValueError(f"Invalid sector: {sector}")
        
        # Analyze each ticker
        ticker_results = []
        for ticker in sector_tickers:
            try:
                ticker_result = self.analyze_ticker(ticker, timeframe)
                if "error" not in ticker_result:
                    ticker_results.append(ticker_result)
            except Exception as e:
                logger.error(f"Error analyzing ticker {ticker}: {e}")
                # Add placeholder with error
                ticker_results.append({
                    "metadata": {
                        "ticker": ticker,
                        "error": str(e)
                    }
                })
        
        # Calculate sector aggregates
        sector_aggregates = self._calculate_sector_decision_aggregates(ticker_results, sector)
        
        # Generate sector insights
        sector_insights = self._generate_sector_insights(ticker_results, sector_aggregates, sector)
        
        # Create final structure
        result = {
            "metadata": {
                "sector": sector,
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "timeframe": timeframe,
                "ticker_count": len(ticker_results),
                "data_sources": ["valuation", "technical"],
                "last_updated": datetime.now().isoformat()
            },
            "ticker_results": ticker_results,
            "sector_aggregates": sector_aggregates,
            "insights": sector_insights
        }
        
        return result
    
    def _load_valuation_data(self, ticker: str, timeframe: str) -> Dict[str, Any]:
        """
        Load valuation data for a ticker.
        
        Args:
            ticker: Ticker symbol
            timeframe: Analysis timeframe
            
        Returns:
            Dictionary with valuation data
        """
        valuation_data = {}
        
        # Load each valuation type
        for val_type, path in self._valuation_paths.items():
            try:
                df = pd.read_parquet(path)
                
                # Filter by ticker
                filtered_df = df[df['symbol'] == ticker]
                
                # Filter by timeframe
                if timeframe != "latest":
                    cutoff_date = self._get_cutoff_date(timeframe)
                    if 'date' in filtered_df.columns:
                        filtered_df = filtered_df[pd.to_datetime(filtered_df['date']) >= cutoff_date]
                
                if filtered_df.empty:
                    continue
                
                # Get latest data
                latest = filtered_df.sort_values('date').iloc[-1]
                
                # Add to valuation data
                val_data = {}
                for col in filtered_df.columns:
                    if col != 'symbol' and col != 'date':  # Skip symbol and date columns
                        val_data[col] = latest.get(col)
                
                valuation_data[val_type] = val_data
                        
            except Exception as e:
                logger.error(f"Error loading {val_type} valuation data: {e}")
        
        return valuation_data
    
    def _load_technical_data(self, ticker: str, timeframe: str) -> Dict[str, Any]:
        """
        Load technical data for a ticker.
        
        Args:
            ticker: Ticker symbol
            timeframe: Analysis timeframe
            
        Returns:
            Dictionary with technical data
        """
        technical_data = {}
        
        # Load OHLCV data
        try:
            df = pd.read_parquet(self._technical_paths["ohlcv"])
            
            # Filter by ticker
            filtered_df = df[df['symbol'] == ticker]
            
            # Filter by timeframe
            if timeframe != "latest":
                cutoff_date = self._get_cutoff_date(timeframe)
                filtered_df = filtered_df[pd.to_datetime(filtered_df['date']) >= cutoff_date]
            
            if filtered_df.empty:
                return {}
            
            # Get latest data
            latest = filtered_df.sort_values('date').iloc[-1]
            
            # Add price data
            price_data = {}
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in latest:
                    price_data[col] = latest.get(col)
            
            technical_data["price_data"] = price_data
            
            # Calculate basic metrics
            close = latest.get('close', 0)
            high = latest.get('high', 0)
            low = latest.get('low', 0)
            volume = latest.get('volume', 0)
            
            if close > 0:
                technical_data["basic_metrics"] = {
                    "daily_change": 0,
                    "daily_change_pct": 0,
                    "high_low_pct": ((high - low) / close) * 100 if close > 0 else 0,
                    "price_position": 0.5  # Middle of range by default
                }
                
                # Calculate daily changes if we have historical data
                if len(filtered_df) >= 2:
                    df_sorted = filtered_df.sort_values('date')
                    prev = df_sorted.iloc[-2]
                    cur = df_sorted.iloc[-1]
                    
                    technical_data["basic_metrics"]["daily_change"] = cur['close'] - prev['close']
                    technical_data["basic_metrics"]["daily_change_pct"] = ((cur['close'] - prev['close']) / prev['close']) * 100
                    
                    # Calculate position in recent range
                    recent_high = df_sorted.tail(10)['high'].max()
                    recent_low = df_sorted.tail(10)['low'].min()
                    
                    if recent_high > recent_low:
                        position = (cur['close'] - recent_low) / (recent_high - recent_low)
                        technical_data["basic_metrics"]["price_position"] = max(0, min(1, position))
                        
        except Exception as e:
            logger.error(f"Error loading OHLCV data: {e}")
        
        # Load technical indicators
        for indicator_type, path in self._technical_paths.items():
            if indicator_type == "ohlcv" or indicator_type == "volume" or indicator_type == "market_breadth":
                continue  # Already handled above
                
            if not self.config.get("indicators", {}).get("enabled", {}).get(indicator_type.split("_")[0], False):
                continue
                
            try:
                df = pd.read_parquet(path)
                
                # Filter by ticker
                filtered_df = df[df['symbol'] == ticker]
                
                # Filter by timeframe
                if timeframe != "latest":
                    cutoff_date = self._get_cutoff_date(timeframe)
                    if 'date' in filtered_df.columns:
                        filtered_df = filtered_df[pd.to_datetime(filtered_df['date']) >= cutoff_date]
                
                if filtered_df.empty:
                    continue
                
                # Get latest data
                latest = filtered_df.sort_values('date').iloc[-1]
                
                # Add to technical data
                indicator_data = {}
                for col in df.columns:
                    if col != 'symbol' and col != 'date':  # Skip symbol and date columns
                        indicator_data[col] = latest.get(col)
                
                technical_data[indicator_type] = {
                    "latest_date": latest['date'].strftime("%Y-%m-%d") if 'date' in latest else "",
                    "data": indicator_data
                }
                        
            except Exception as e:
                logger.error(f"Error loading {indicator_type} technical data: {e}")
        
        return technical_data
    
    def _get_cutoff_date(self, timeframe: str) -> datetime:
        """
        Get cutoff date for timeframe.
        
        Args:
            timeframe: Analysis timeframe
            
        Returns:
            Cutoff datetime
        """
        today = datetime.now()
        days = self.config.get("timeframes", {}).get(timeframe, 30)
        
        return today - timedelta(days=days)
    
    def _calculate_decision_scores(self, data: Dict[str, Any], ticker_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate decision scores combining valuation and technical data.
        
        Args:
            data: Merged valuation and technical data
            ticker_info: Ticker information
            
        Returns:
            Dictionary with decision scores
        """
        # Get weights
        weights = self.config.get("weights", {})
        val_weight = weights.get("valuation", 0.5)
        tech_weight = weights.get("technical", 0.5)
        
        val_weights = self.config.get("valuation_weights", {})
        tech_weights = self.config.get("technical_weights", {})
        thresholds = self.config.get("decision_thresholds", {})
        
        # Calculate valuation score
        valuation_score = self._calculate_valuation_score(data, val_weights)
        
        # Calculate technical score
        technical_score = self._calculate_technical_score(data, tech_weights)
        
        # Calculate combined score
        combined_score = (valuation_score * val_weight) + (technical_score * tech_weight)
        
        # Apply sector adjustments if enabled
        if self.config.get("risk_adjustments", {}).get("sector_pe_adjustment", False):
            combined_score = self._apply_sector_pe_adjustment(combined_score, data, ticker_info)
        
        if self.config.get("risk_adjustments", {}).get("volatility_adjustment", False):
            combined_score = self._apply_volatility_adjustment(combined_score, data)
        
        if self.config.get("risk_adjustments", {}).get("volume_weighting", False):
            combined_score = self._apply_volume_weighting(combined_score, data)
        
        # Final scores
        return {
            "valuation_score": round(valuation_score, 2),
            "technical_score": round(technical_score, 2),
            "combined_score": round(combined_score, 2),
            "valuation_raw": valuation_score,
            "technical_raw": technical_score,
            "combined_raw": combined_score,
            "components": {
                "pe_score": data.get("pe", {}).get("score", 0),
                "pb_score": data.get("pb", {}).get("score", 0),
                "trend_score": data.get("technical_data", {}).get("trend", {}).get("score", 0),
                "momentum_score": data.get("technical_data", {}).get("momentum", {}).get("score", 0)
            }
        }
    
    def _calculate_valuation_score(self, data: Dict[str, Any], weights: Dict[str, float]) -> float:
        """
        Calculate valuation score from multiple metrics.
        
        Args:
            data: Valuation data
            weights: Weights for different valuation metrics
            
        Returns:
            Valuation score (0-100)
        """
        score = 0
        total_weight = 0
        
        # PE score
        pe_data = data.get("pe", {})
        if pe_data and "pe_ttm" in pe_data:
            pe_ratio = pe_data["pe_ttm"]
            sector = data.get("technical_data", {}).get("price_data", {}).get("sector_avg_pe", 20)  # Default
            
            # Score based on relative valuation to sector
            if sector > 0:
                pe_score = max(0, 100 - (pe_ratio / sector) * 100)  # Lower PE than sector average is better
            else:
                # Absolute PE scoring
                pe_abs_weight = weights.get("pe_absolute", 0.05)
                pe_rel_weight = weights.get("pe_relative", 0.3)
                
                if pe_ratio < 10:
                    pe_abs_score = 90  # Very undervalued
                elif pe_ratio < 15:
                    pe_abs_score = 70  # Undervalued
                elif pe_ratio < 20:
                    pe_abs_score = 50  # Fair value
                elif pe_ratio < 30:
                    pe_abs_score = 30  # Overvalued
                else:
                    pe_abs_score = 10  # Very overvalued
                
                pe_score = (pe_abs_score * pe_abs_weight) + (pe_rel_score * pe_rel_weight)
            
            score += pe_score
            total_weight += weights.get("pe_relative", 0.3) + weights.get("pe_absolute", 0.05)
        
        # PB score
        pb_data = data.get("pb", {})
        if pb_data and "pb_ratio" in pb_data:
            pb_ratio = pb_data["pb_ratio"]
            sector = data.get("technical_data", {}).get("price_data", {}).get("sector_avg_pb", 2.0)  # Default
            
            # Score based on relative valuation to sector
            if sector > 0:
                pb_score = max(0, 100 - (pb_ratio / sector) * 100)  # Lower PB than sector average is better
            else:
                # Absolute PB scoring
                pb_abs_weight = weights.get("pb_absolute", 0.05)
                pb_rel_weight = weights.get("pb_relative", 0.2)
                
                if pb_ratio < 1.0:
                    pb_abs_score = 90  # Very undervalued
                elif pb_ratio < 1.5:
                    pb_abs_score = 70  # Undervalued
                elif pb_ratio < 2.5:
                    pb_abs_score = 50  # Fair value
                elif pb_ratio < 4.0:
                    pb_abs_score = 30  # Overvalued
                else:
                    pb_abs_score = 10  # Very overvalued
                
                pb_score = (pb_abs_score * pb_abs_weight) + (pb_rel_score * pb_rel_weight)
            
            score += pb_score
            total_weight += weights.get("pb_relative", 0.2) + weights.get("pb_absolute", 0.05)
        
        # EV/EBITDA score
        ev_data = data.get("ev_ebitda", {})
        if ev_data and "ev_ebitda" in ev_data:
            ev_ratio = ev_data["ev_ebitda"]
            sector = data.get("technical_data", {}).get("price_data", {}).get("sector_avg_ev_ebitda", 10)  # Default
            
            # Score based on relative valuation to sector
            if sector > 0:
                ev_score = max(0, 100 - (ev_ratio / sector) * 100)  # Lower EV/EBITDA than sector average is better
            else:
                # Absolute EV/EBITDA scoring
                ev_abs_weight = weights.get("ev_ebitda_relative", 0.2)
                
                if ev_ratio < 6:
                    ev_abs_score = 90  # Very undervalued
                elif ev_ratio < 8:
                    ev_abs_score = 70  # Undervalued
                elif ev_ratio < 12:
                    ev_abs_score = 50  # Fair value
                elif ev_ratio < 16:
                    ev_abs_score = 30  # Overvalued
                else:
                    ev_abs_score = 10  # Very overvalued
                
                ev_score = ev_abs_score * ev_abs_weight
            
            score += ev_score
            total_weight += weights.get("ev_ebitda_relative", 0.2)
        
        # Normalize to 100 if total_weight is not zero
        if total_weight > 0:
            return score / total_weight
        
        return 0  # Default if no data
    
    def _calculate_technical_score(self, data: Dict[str, Any], weights: Dict[str, float]) -> float:
        """
        Calculate technical score from multiple indicators.
        
        Args:
            data: Technical data
            weights: Weights for different technical indicators
            
        Returns:
            Technical score (0-100)
        """
        score = 0
        total_weight = 0
        
        tech_data = data.get("technical_data", {})
        
        # Trend score
        trend_data = tech_data.get("trend", {})
        if trend_data:
            trend_score = trend_data.get("score", 50)
            trend_weight = weights.get("trend", 0.25)
            
            score += trend_score * trend_weight
            total_weight += trend_weight
        
        # Momentum score
        momentum_data = tech_data.get("momentum", {})
        if momentum_data:
            momentum_score = momentum_data.get("score", 50)
            momentum_weight = weights.get("momentum", 0.25)
            
            score += momentum_score * momentum_weight
            total_weight += momentum_weight
        
        # Oversold/Overbought score
        rsi_data = tech_data.get("rsi", {})
        if rsi_data:
            rsi = rsi_data.get("rsi_14", 50)
            oo_weight = weights.get("oversold_overbought", 0.2)
            
            # Score based on RSI position
            if 20 <= rsi <= 35:  # Oversold - bullish
                oo_score = 80
            elif 35 < rsi <= 65:  # Slightly oversold - bullish
                oo_score = 60
            elif 65 < rsi <= 80:  # Neutral - hold
                oo_score = 40
            else:  # Overbought - bearish
                oo_score = 20
            
            score += oo_score * oo_weight
            total_weight += oo_weight
        
        # Volume confirmation score
        basic_metrics = tech_data.get("basic_metrics", {})
        if basic_metrics:
            volume_conf_weight = weights.get("volume_confirmation", 0.15)
            
            # Score based on volume confirmation of price movement
            if "daily_change_pct" in basic_metrics and "volume" in basic_metrics:
                change_pct = basic_metrics["daily_change_pct"]
                volume = basic_metrics.get("volume", 0)
                
                # High volume with positive change is bullish
                if volume > 0 and change_pct > 1:
                    vol_conf_score = 80
                elif volume > 0 and change_pct < -1:
                    vol_conf_score = 30  # High volume with negative change is bearish but not as strong
                elif volume < 0 and change_pct > 1:
                    vol_conf_score = 60  # Low volume with positive change might be unsustainable
                elif volume < 0 and change_pct < -1:
                    vol_conf_score = 20  # Low volume with negative change might indicate selling pressure easing
                else:
                    vol_conf_score = 50  # Neutral or conflicting signals
                
                score += vol_conf_score * volume_conf_weight
                total_weight += volume_conf_weight
        
        # Volatility score (adjusted - lower volatility gets higher score for value stocks)
        volatility_weight = weights.get("volatility", 0.15)
        
        # Score based on price position (in-the-money for options analogy)
        if "price_position" in basic_metrics:
            price_pos = basic_metrics["price_position"]
            
            # Middle of range is better for value investing
            if 0.4 <= price_pos <= 0.6:
                vol_score = 70  # Not at extremes
            elif 0.3 <= price_pos < 0.4 or 0.6 < price_pos <= 0.7:
                vol_score = 50  # Somewhat extended
            else:
                vol_score = 30  # At extremes
            
            score += vol_score * volatility_weight
            total_weight += volatility_weight
        
        # Normalize to 100 if total_weight is not zero
        if total_weight > 0:
            return score / total_weight
        
        return 0  # Default if no data
    
    def _apply_sector_pe_adjustment(self, score: float, data: Dict[str, Any], ticker_info: Dict[str, Any]) -> float:
        """
        Apply sector PE adjustment to the score.
        
        Args:
            score: Original combined score
            data: Merged data
            ticker_info: Ticker information
            
        Returns:
            Adjusted score
        """
        # Get sector PE comparison
        sector = ticker_info.get("sector", "")
        price_data = data.get("technical_data", {}).get("price_data", {})
        sector_avg_pe = price_data.get("sector_avg_pe", 20)
        current_pe = data.get("pe", {}).get("pe_ttm", 15)
        
        if sector_avg_pe > 0 and current_pe > 0:
            # Calculate adjustment factor
            pe_ratio = current_pe / sector_avg_pe
            
            # Apply adjustment based on PE relative to sector
            if pe_ratio < 0.8:  # Much cheaper than sector average
                adjustment = 1.2  # Boost score
            elif pe_ratio < 1.0:  # Somewhat cheaper than sector average
                adjustment = 1.1  # Slight boost
            elif pe_ratio > 1.5:  # More expensive than sector average
                adjustment = 0.9  # Reduce score
            elif pe_ratio > 2.0:  # Much more expensive than sector average
                adjustment = 0.8  # Reduce score more
            else:
                adjustment = 1.0  # No adjustment
            
            return min(100, score * adjustment)
        
        return score
    
    def _apply_volatility_adjustment(self, score: float, data: Dict[str, Any]) -> float:
        """
        Apply volatility adjustment to the score.
        
        Args:
            score: Original combined score
            data: Merged data
            
        Returns:
            Adjusted score
        """
        # Get volatility information
        tech_data = data.get("technical_data", {})
        
        # Calculate 20-day volatility if not available
        volatility = 0.25  # Default moderate volatility
        basic_metrics = tech_data.get("basic_metrics", {})
        
        if "volatility_20" in basic_metrics:
            volatility = basic_metrics["volatility_20"] / 100  # Convert from percentage
        
        # Apply adjustment based on volatility
        # Lower volatility is better for value investing, higher volatility is riskier
        if volatility < 0.15:
            adjustment = 1.1  # Low volatility - boost score
        elif volatility > 0.3:
            adjustment = 0.9  # High volatility - reduce score
        else:
            adjustment = 1.0  # Moderate volatility - no adjustment
        
        return min(100, score * adjustment)
    
    def _apply_volume_weighting(self, score: float, data: Dict[str, Any]) -> float:
        """
        Apply volume-based weighting to the score.
        
        Args:
            score: Original combined score
            data: Merged data
            
        Returns:
            Volume-weighted score
        """
        # Get volume information
        tech_data = data.get("technical_data", {})
        basic_metrics = tech_data.get("basic_metrics", {})
        
        # Calculate volume percentile if we have sector data
        if "volume_percentile" in basic_metrics:
            volume_pct = basic_metrics["volume_percentile"]
            
            # Higher volume stocks get more weight
            if volume_pct > 80:
                adjustment = 1.2  # High volume
            elif volume_pct > 60:
                adjustment = 1.1  # Above average volume
            elif volume_pct > 40:
                adjustment = 1.0  # Average volume
            else:
                adjustment = 0.9  # Low volume
            
            return min(100, score * adjustment)
        
        return score
    
    def _generate_decision(self, scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate final trading decision from scores.
        
        Args:
            scores: Decision scores
            
        Returns:
            Dictionary with final decision
        """
        combined_score = scores.get("combined_score", 50)
        thresholds = self.config.get("decision_thresholds", {})
        
        # Determine action
        if combined_score >= thresholds.get("strong_buy", 80):
            action = "STRONG_BUY"
            strength = 90
            timeframe = "short_term"  # Immediate entry
        elif combined_score >= thresholds.get("buy", 65):
            action = "BUY"
            strength = 70
            timeframe = "short_term"  # Entry soon
        elif combined_score >= thresholds.get("hold", 40):
            action = "HOLD"
            strength = 50
            timeframe = "medium_term"  # Wait and watch
        elif combined_score >= thresholds.get("sell", 35):
            action = "SELL"
            strength = 30
            timeframe = "short_term"  # Exit soon
        else:
            action = "STRONG_SELL"
            strength = 10
            timeframe = "short_term"  # Exit immediately
        
        # Determine confidence based on score consistency
        components = scores.get("components", {})
        val_score = components.get("valuation_score", 50)
        tech_score = components.get("technical_score", 50)
        
        # High confidence when both FA and TA agree
        confidence_diff = abs(val_score - tech_score)
        
        if confidence_diff < 20:  # High agreement
            confidence = 0.9
        elif confidence_diff < 40:  # Some agreement
            confidence = 0.7
        else:  # Low agreement
            confidence = 0.5
        
        return {
            "action": action,
            "strength": strength,
            "confidence": confidence,
            "timeframe": timeframe,
            "score_components": {
                "valuation": val_score,
                "technical": tech_score,
                "combined": combined_score,
                "agreement": 100 - confidence_diff  # Inverted for clarity
            }
        }
    
    def _generate_analysis(self, data: Dict[str, Any], scores: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate analysis summary.
        
        Args:
            data: Merged valuation and technical data
            scores: Decision scores
            decision: Final decision
            
        Returns:
            Dictionary with analysis
        """
        analysis = {
            "valuation_insights": [],
            "technical_insights": [],
            "combined_insights": [],
            "risk_factors": [],
            "recommendations": []
        }
        
        # Valuation insights
        pe_data = data.get("pe", {})
        if pe_data and "pe_ttm" in pe_data:
            pe_ratio = pe_data["pe_ttm"]
            
            if pe_ratio < 10:
                analysis["valuation_insights"].append(
                    "Stock appears significantly undervalued with low PE ratio"
                )
            elif pe_ratio > 25:
                analysis["valuation_insights"].append(
                    "Stock appears overvalued with high PE ratio"
                )
            else:
                analysis["valuation_insights"].append(
                    "Stock appears fairly valued based on PE ratio"
                )
        
        pb_data = data.get("pb", {})
        if pb_data and "pb_ratio" in pb_data:
            pb_ratio = pb_data["pb_ratio"]
            
            if pb_ratio < 1.0:
                analysis["valuation_insights"].append(
                    "Stock trading below book value indicates potential value"
                )
            elif pb_ratio > 3.0:
                analysis["valuation_insights"].append(
                    "Stock trading significantly above book value indicates risk"
                )
        
        # Technical insights
        tech_data = data.get("technical_data", {})
        trend_data = tech_data.get("trend", {})
        momentum_data = tech_data.get("momentum", {})
        
        if trend_data and momentum_data:
            trend_dir = trend_data.get("direction", "NEUTRAL")
            momentum_score = momentum_data.get("score", 50)
            
            if trend_dir == "UP" and momentum_score > 60:
                analysis["technical_insights"].append(
                    "Strong bullish trend with positive momentum"
                )
            elif trend_dir == "DOWN" and momentum_score < 40:
                analysis["technical_insights"].append(
                    "Strong bearish trend with negative momentum"
                )
            elif trend_dir == "UP" and momentum_score < 40:
                analysis["technical_insights"].append(
                    "Bullish trend but weakening momentum"
                )
            elif trend_dir == "DOWN" and momentum_score > 60:
                analysis["technical_insights"].append(
                    "Bearish trend but strengthening momentum"
                )
        
        # Combined insights
        val_score = scores.get("valuation_score", 50)
        tech_score = scores.get("technical_score", 50)
        
        if val_score > 70 and tech_score > 70:
            analysis["combined_insights"].append(
                "Both valuation and technical indicators suggest strong BUY"
            )
        elif val_score < 30 and tech_score < 30:
            analysis["combined_insights"].append(
                "Both valuation and technical indicators suggest strong SELL"
            )
        elif val_score > 70 and tech_score < 30:
            analysis["combined_insights"].append(
                "Valuation suggests BUY but technical indicators suggest caution"
            )
        elif val_score < 30 and tech_score > 70:
            analysis["combined_insights"].append(
                "Valuation suggests caution but technical indicators suggest BUY"
            )
        
        # Risk factors
        risk_factors = []
        
        # Volatility risk
        basic_metrics = tech_data.get("basic_metrics", {})
        if "volatility_20" in basic_metrics:
            volatility = basic_metrics["volatility_20"] / 100
            if volatility > 0.3:
                risk_factors.append("High volatility increases risk")
            elif volatility < 0.15:
                risk_factors.append("Low volatility indicates stability")
        
        # Liquidity risk
        if "volume_percentile" in basic_metrics:
            volume_pct = basic_metrics["volume_percentile"]
            if volume_pct < 20:
                risk_factors.append("Low trading volume indicates liquidity risk")
        
        analysis["risk_factors"] = risk_factors
        
        # Recommendations based on decision
        decision = decision.get("action", "HOLD")
        
        if decision in ["STRONG_BUY", "BUY"]:
            analysis["recommendations"] = [
                "Consider establishing position now",
                "Set stop-loss below recent support level",
                "Monitor for confirmation signals"
            ]
        elif decision in ["STRONG_SELL", "SELL"]:
            analysis["recommendations"] = [
                "Consider closing position immediately",
                "Take partial profits if available",
                "Wait for potential re-entry at better levels"
            ]
        else:  # HOLD
            analysis["recommendations"] = [
                "Maintain current position",
                "Monitor for signal changes",
                "Consider partial profit-taking at resistance levels"
            ]
        
        return analysis
    
    def _calculate_sector_decision_aggregates(self, ticker_results: List[Dict], sector: str) -> Dict[str, Any]:
        """
        Calculate sector-level aggregates for decision analysis.
        
        Args:
            ticker_results: List of ticker analysis results
            sector: Sector name
            
        Returns:
            Dictionary with sector aggregates
        """
        if not ticker_results:
            return {}
        
        # Filter out error results
        valid_results = [r for r in ticker_results if "error" not in r]
        if not valid_results:
            return {}
        
        # Create DataFrame for analysis
        df = pd.DataFrame([{
            "ticker": r.get("metadata", {}).get("ticker"),
            "decision": r.get("decision", {}).get("action", "HOLD"),
            "score": r.get("decision_scores", {}).get("combined_score", 50),
            "valuation_score": r.get("decision_scores", {}).get("valuation_score", 50),
            "technical_score": r.get("decision_scores", {}).get("technical_score", 50)
        } for r in valid_results])
        
        # Calculate distributions
        decision_counts = df["decision"].value_counts()
        score_stats = df["score"].describe()
        
        aggregates = {
            "sector_name": sector,
            "ticker_count": len(valid_results),
            "decision_distribution": {
                "strong_buy": int(decision_counts.get("STRONG_BUY", 0)),
                "buy": int(decision_counts.get("BUY", 0)),
                "hold": int(decision_counts.get("HOLD", 0)),
                "sell": int(decision_counts.get("SELL", 0)),
                "strong_sell": int(decision_counts.get("STRONG_SELL", 0))
            },
            "score_statistics": {
                "mean": round(score_stats["mean"], 2),
                "median": round(score_stats["50%"], 2),
                "min": round(score_stats["min"], 2),
                "max": round(score_stats["max"], 2),
                "std": round(score_stats["std"], 2)
            },
            "valuation_tech_correlation": {
                "correlation": round(df["valuation_score"].corr(df["technical_score"]), 2),
                "interpretation": ""
            }
        }
        
        # Interpret correlation
        corr = aggregates["valuation_tech_correlation"]["correlation"]
        if corr > 0.7:
            aggregates["valuation_tech_correlation"]["interpretation"] = "High correlation - FA and TA mostly aligned"
        elif corr > 0.3:
            aggregates["valuation_tech_correlation"]["interpretation"] = "Moderate correlation - FA and TA somewhat aligned"
        elif corr > -0.3:
            aggregates["valuation_tech_correlation"]["interpretation"] = "Low correlation - FA and TA often conflict"
        else:
            aggregates["valuation_tech_correlation"]["interpretation"] = "No correlation - FA and TA independent"
        
        # Get top/bottom performers
        if not df.empty:
            sorted_df = df.sort_values("score", ascending=False)
            
            aggregates["top_performers"] = sorted_df.head(10)[["ticker", "score", "decision"]].to_dict("records")
            aggregates["bottom_performers"] = sorted_df.tail(10)[["ticker", "score", "decision"]].to_dict("records")
        
        return aggregates
    
    def _generate_sector_insights(self, ticker_results: List[Dict], aggregates: Dict[str, Any], sector: str) -> Dict[str, Any]:
        """
        Generate insights for sector decision analysis.
        
        Args:
            ticker_results: List of ticker analysis results
            aggregates: Sector aggregates
            sector: Sector name
            
        Returns:
            Dictionary with sector insights
        """
        insights = {
            "sector_overview": [],
            "decision_insights": [],
            "risk_insights": [],
            "recommendations": []
        }
        
        # Sector overview
        decision_dist = aggregates.get("decision_distribution", {})
        if decision_dist:
            buy_signals = decision_dist.get("buy", 0) + decision_dist.get("strong_buy", 0)
            sell_signals = decision_dist.get("sell", 0) + decision_dist.get("strong_sell", 0)
            total = buy_signals + decision_dist.get("hold", 0) + sell_signals
            
            if total > 0:
                buy_pct = (buy_signals / total) * 100
                sell_pct = (sell_signals / total) * 100
                
                insights["sector_overview"].append(
                    f"Sector shows {buy_pct:.1f}% buy signals and {sell_pct:.1f}% sell signals"
                )
                
                if buy_pct > 60:
                    insights["decision_insights"].append(
                        f"Sector appears bullish with {buy_pct:.1f}% buy recommendations"
                    )
                elif sell_pct > 60:
                    insights["decision_insights"].append(
                        f"Sector appears bearish with {sell_pct:.1f}% sell recommendations"
                    )
        
        # Risk insights
        score_stats = aggregates.get("score_statistics", {})
        if score_stats:
            mean_score = score_stats.get("mean", 50)
            
            if mean_score > 70:
                insights["risk_insights"].append(
                    "Sector average score is high (>70), indicating potential overvaluation"
                )
            elif mean_score < 30:
                insights["risk_insights"].append(
                    "Sector average score is low (<30), indicating potential undervaluation"
                )
        
        # Correlation insights
        corr_data = aggregates.get("valuation_tech_correlation", {})
        if corr_data:
            corr = corr_data.get("correlation", 0)
            interp = corr_data.get("interpretation", "")
            
            if corr > 0.7:
                insights["decision_insights"].append(
                    f"High FA+TA correlation ({corr:.2f}) indicates consistent decision-making across metrics"
                )
            elif corr < -0.3:
                insights["decision_insights"].append(
                    f"Low FA+TA correlation ({corr:.2f}) indicates conflicting signals between metrics"
                )
        
        # Recommendations
        if decision_dist:
            buy_signals = decision_dist.get("buy", 0) + decision_dist.get("strong_buy", 0)
            
            if buy_signals > len(decision_dist.get("hold", 0)):
                insights["recommendations"].append(
                    "High number of buy recommendations - consider sector rotation risk"
                )
            elif buy_signals < len(decision_dist.get("hold", 0)) / 2:
                insights["recommendations"].append(
                    "Low number of buy recommendations - sector may be oversold"
                )
        
        return insights
    
    def get_available_sectors(self) -> List[str]:
        """
        Get list of sectors with valuation and technical data.
        
        Returns:
            List of sector names
        """
        try:
            sectors = self.sector_registry.get_all_sectors()
            
            # Filter to only sectors with data
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


# Convenience function for quick Valuation+TA analysis
def analyze_ticker_valuation_ta(ticker: str, timeframe: str = "medium", config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Quick function to analyze a ticker's valuation+technical indicators.
    
    Args:
        ticker: Ticker symbol to analyze
        timeframe: Analysis timeframe
        config: Optional configuration
        
    Returns:
        Analysis result dictionary
    """
    analyzer = ValuationTAAnalyzer(config)
    return analyzer.analyze_ticker(ticker, timeframe)


# Convenience function for quick sector Valuation+TA analysis
def analyze_sector_valuation_ta(sector: str, timeframe: str = "medium", config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Quick function to analyze a sector's valuation+technical indicators.
    
    Args:
        sector: Sector name to analyze
        timeframe: Analysis timeframe
        config: Optional configuration
        
    Returns:
        Analysis result dictionary
    """
    analyzer = ValuationTAAnalyzer(config)
    return analyzer.analyze_sector(sector, timeframe)