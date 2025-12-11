"""
Sector Fundamental Analyzer
=========================

Standalone module for fundamental analysis by sector.
Focuses on quarterly financial metrics analysis without technical indicators.

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


class SectorFAAnalyzer:
    """
    Standalone analyzer for fundamental analysis by sector.
    
    Focuses on financial metrics analysis by sector with quarterly data.
    Provides comparison between sectors and identifies top performers.
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
        
        # Pre-load fundamental data paths
        self._fundamental_paths = {
            "bank": get_data_path("DATA/processed/fundamental/bank/bank_financial_metrics.parquet"),
            "company": get_data_path("DATA/processed/fundamental/company/company_financial_metrics.parquet"),
            "insurance": get_data_path("DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet"),
            "security": get_data_path("DATA/processed/fundamental/security/security_financial_metrics.parquet")
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration for FA analysis.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "weights": {
                "profitability": 0.3,
                "growth": 0.3,
                "efficiency": 0.2,
                "leverage": 0.2
            },
            "indicators": {
                "enabled": {
                    "roe": True,
                    "roa": True,
                    "gross_margin": True,
                    "operating_margin": True,
                    "ebitda_margin": True,
                    "revenue_growth": True,
                    "profit_growth": True,
                    "debt_to_equity": True,
                    "current_ratio": True
                }
            },
            "display": {
                "chart_height": 500,
                "chart_colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
                "show_data_labels": True
            }
        }
    
    def analyze_sector(self, sector: str, quarters: int = 4) -> Dict[str, Any]:
        """
        Analyze sector fundamentals over multiple quarters.
        
        Args:
            sector: Sector name to analyze
            quarters: Number of recent quarters to analyze (default: 4)
            
        Returns:
            Dictionary with sector fundamental analysis
        """
        if not sector or not isinstance(sector, str):
            raise ValueError("Sector must be a non-empty string")
            
        logger.info(f"Analyzing FA for sector: {sector}, quarters: {quarters}")
        
        # 1. Get all tickers in sector
        try:
            sector_tickers = self.sector_registry.get_tickers_by_sector(sector)
            if not sector_tickers:
                raise ValueError(f"No tickers found for sector: {sector}")
        except Exception as e:
            logger.error(f"Error getting sector tickers: {e}")
            raise ValueError(f"Invalid sector: {sector}")
        
        # 2. Load fundamental data for sector
        fundamental_data = self._load_fundamental_data(sector_tickers, quarters)
        
        # 3. Calculate sector metrics and aggregates
        sector_metrics = self._calculate_sector_metrics(fundamental_data, sector)
        
        # 4. Generate insights
        insights = self._generate_insights(fundamental_data, sector_metrics, sector)
        
        # 5. Create final structure
        sector_analysis = {
            "metadata": {
                "sector": sector,
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "ticker_count": len(fundamental_data),
                "quarters_analyzed": quarters,
                "data_sources": ["fundamental"],
                "last_updated": datetime.now().isoformat()
            },
            "entities": fundamental_data,
            "sector_metrics": sector_metrics,
            "insights": insights
        }
        
        return sector_analysis
    
    def _load_fundamental_data(self, tickers: List[str], quarters: int) -> List[Dict[str, Any]]:
        """
        Load fundamental data for specified tickers over multiple quarters.
        
        Args:
            tickers: List of ticker symbols
            quarters: Number of recent quarters to analyze
            
        Returns:
            List of dictionaries with fundamental data
        """
        fundamental_data = []
        
        # Determine entity types from tickers
        entity_types = set()
        for ticker in tickers:
            try:
                info = self.ticker_mapper.get_complete_info(ticker)
                if info and "entity_type" in info:
                    entity_types.add(info["entity_type"])
            except Exception:
                continue
        
        # Load data for each entity type
        for entity_type in entity_types:
            if entity_type not in self._fundamental_paths:
                continue
                
            path = self._fundamental_paths[entity_type]
            try:
                df = pd.read_parquet(path)
                
                # Filter by tickers
                filtered_df = df[df['symbol'].isin(tickers)]
                
                # Filter by recent quarters
                if 'year' in filtered_df.columns and 'quarter' in filtered_df.columns:
                    # Create period identifier for sorting
                    filtered_df['period'] = filtered_df['year'].astype(str) + 'Q' + filtered_df['quarter'].astype(str)
                    
                    # Sort by period and get most recent periods
                    filtered_df = filtered_df.sort_values(['year', 'quarter'], ascending=False)
                    
                    # Group by symbol and get N most recent quarters
                    filtered_df = filtered_df.groupby('symbol').head(quarters)
                
                # Convert to dictionary
                for _, row in filtered_df.iterrows():
                    ticker = row['symbol']
                    
                    # Create entity dictionary
                    entity = {"symbol": ticker}
                    
                    # Add entity type
                    entity["entity_type"] = entity_type
                    
                    # Add sector info
                    try:
                        info = self.ticker_mapper.get_complete_info(ticker)
                        if info:
                            entity["sector"] = info.get("sector")
                            entity["industry"] = info.get("industry")
                    except Exception:
                        pass
                    
                    # Add fundamental metrics
                    for col in filtered_df.columns:
                        if col != 'symbol' and col != 'period':  # Skip symbol and period columns
                            entity[col] = row[col]
                    
                    fundamental_data.append(entity)
                            
            except Exception as e:
                logger.error(f"Error loading fundamental data for {entity_type}: {e}")
        
        return fundamental_data
    
    def _calculate_sector_metrics(self, entities: List[Dict], sector: str) -> Dict[str, Any]:
        """
        Calculate sector-level metrics and aggregates.
        
        Args:
            entities: List of entity dictionaries
            sector: Sector name
            
        Returns:
            Dictionary with sector metrics
        """
        if not entities:
            return {}
        
        # Extract data for easier analysis
        df = pd.DataFrame(entities)
        
        # Initialize metrics dictionary
        metrics = {
            "sector_name": sector,
            "sector_ticker_count": len(entities),
            "profitability_metrics": {},
            "growth_metrics": {},
            "efficiency_metrics": {},
            "leverage_metrics": {},
            "quarterly_trends": {},
            "distribution_metrics": {},
            "sector_ranking": {}
        }
        
        # Calculate profitability metrics
        profitability = {}
        
        # ROE distribution
        roe_values = df["roe"].dropna()
        if not roe_values.empty:
            profitability["roe"] = {
                "median": np.percentile(roe_values, 50),
                "mean": roe_values.mean(),
                "min": roe_values.min(),
                "max": roe_values.max(),
                "q1": np.percentile(roe_values, 25),
                "q3": np.percentile(roe_values, 75),
                "std_dev": roe_values.std()
            }
        
        # ROA distribution
        roa_values = df["roa"].dropna()
        if not roa_values.empty:
            profitability["roa"] = {
                "median": np.percentile(roa_values, 50),
                "mean": roa_values.mean(),
                "min": roa_values.min(),
                "max": roa_values.max(),
                "q1": np.percentile(roa_values, 25),
                "q3": np.percentile(roa_values, 75),
                "std_dev": roa_values.std()
            }
        
        # Margin distributions
        margin_types = ["gross_margin", "operating_margin", "ebitda_margin", "net_margin"]
        for margin in margin_types:
            if margin in df.columns:
                margin_values = df[margin].dropna()
                if not margin_values.empty:
                    profitability[margin] = {
                        "median": np.percentile(margin_values, 50),
                        "mean": margin_values.mean(),
                        "min": margin_values.min(),
                        "max": margin_values.max(),
                        "q1": np.percentile(margin_values, 25),
                        "q3": np.percentile(margin_values, 75),
                        "std_dev": margin_values.std()
                    }
        
        metrics["profitability_metrics"] = profitability
        
        # Calculate growth metrics
        growth = {}
        
        # Revenue growth distribution
        rev_growth = df["revenue_growth_yoy"].dropna()
        if not rev_growth.empty:
            growth["revenue_growth"] = {
                "median": np.percentile(rev_growth, 50),
                "mean": rev_growth.mean(),
                "min": rev_growth.min(),
                "max": rev_growth.max(),
                "q1": np.percentile(rev_growth, 25),
                "q3": np.percentile(rev_growth, 75),
                "std_dev": rev_growth.std()
            }
        
        # Profit growth distribution
        profit_growth = df["profit_growth_yoy"].dropna()
        if not profit_growth.empty:
            growth["profit_growth"] = {
                "median": np.percentile(profit_growth, 50),
                "mean": profit_growth.mean(),
                "min": profit_growth.min(),
                "max": profit_growth.max(),
                "q1": np.percentile(profit_growth, 25),
                "q3": np.percentile(profit_growth, 75),
                "std_dev": profit_growth.std()
            }
        
        metrics["growth_metrics"] = growth
        
        # Calculate efficiency metrics
        efficiency = {}
        
        # Asset turnover
        if "total_assets" in df.columns and "revenue" in df.columns:
            asset_turnover = (df["revenue"] / df["total_assets"]).dropna()
            if not asset_turnover.empty:
                efficiency["asset_turnover"] = {
                    "median": np.percentile(asset_turnover, 50),
                    "mean": asset_turnover.mean(),
                    "min": asset_turnover.min(),
                    "max": asset_turnover.max(),
                    "q1": np.percentile(asset_turnover, 25),
                    "q3": np.percentile(asset_turnover, 75),
                    "std_dev": asset_turnover.std()
                }
        
        # Equity turnover
        if "total_equity" in df.columns and "revenue" in df.columns:
            equity_turnover = (df["revenue"] / df["total_equity"]).dropna()
            if not equity_turnover.empty:
                efficiency["equity_turnover"] = {
                    "median": np.percentile(equity_turnover, 50),
                    "mean": equity_turnover.mean(),
                    "min": equity_turnover.min(),
                    "max": equity_turnover.max(),
                    "q1": np.percentile(equity_turnover, 25),
                    "q3": np.percentile(equity_turnover, 75),
                    "std_dev": equity_turnover.std()
                }
        
        metrics["efficiency_metrics"] = efficiency
        
        # Calculate leverage metrics
        leverage = {}
        
        # Debt to equity
        debt_to_equity = df["debt_to_equity"].dropna()
        if not debt_to_equity.empty:
            leverage["debt_to_equity"] = {
                "median": np.percentile(debt_to_equity, 50),
                "mean": debt_to_equity.mean(),
                "min": debt_to_equity.min(),
                "max": debt_to_equity.max(),
                "q1": np.percentile(debt_to_equity, 25),
                "q3": np.percentile(debt_to_equity, 75),
                "std_dev": debt_to_equity.std()
            }
        
        # Current ratio
        current_ratio = df["current_ratio"].dropna()
        if not current_ratio.empty:
            leverage["current_ratio"] = {
                "median": np.percentile(current_ratio, 50),
                "mean": current_ratio.mean(),
                "min": current_ratio.min(),
                "max": current_ratio.max(),
                "q1": np.percentile(current_ratio, 25),
                "q3": np.percentile(current_ratio, 25),
                "std_dev": current_ratio.std()
            }
        
        # Sector-specific metrics
        if "entity_type" in df.columns:
            # Banking sector metrics
            banks = df[df["entity_type"] == "BANK"]
            if not banks.empty:
                bank_metrics = {}
                
                # NIM
                nim = banks["nim"].dropna()
                if not nim.empty:
                    bank_metrics["nim"] = {
                        "median": np.percentile(nim, 50),
                        "mean": nim.mean(),
                        "min": nim.min(),
                        "max": nim.max(),
                        "q1": np.percentile(nim, 25),
                        "q3": np.percentile(nim, 75),
                        "std_dev": nim.std()
                    }
                
                # CIR
                cir = banks["cir"].dropna()
                if not cir.empty:
                    bank_metrics["cir"] = {
                        "median": np.percentile(cir, 50),
                        "mean": cir.mean(),
                        "min": cir.min(),
                        "max": cir.max(),
                        "q1": np.percentile(cir, 25),
                        "q3": np.percentile(cir, 75),
                        "std_dev": cir.std()
                    }
                
                # NPL ratio
                npl = banks["npl_ratio"].dropna()
                if not npl.empty:
                    bank_metrics["npl_ratio"] = {
                        "median": np.percentile(npl, 50),
                        "mean": npl.mean(),
                        "min": npl.min(),
                        "max": npl.max(),
                        "q1": np.percentile(npl, 25),
                        "q3": np.percentile(npl, 75),
                        "std_dev": npl.std()
                    }
                
                leverage["banking_metrics"] = bank_metrics
        
        metrics["leverage_metrics"] = leverage
        
        # Calculate quarterly trends
        quarterly_trends = {}
        
        if 'year' in df.columns and 'quarter' in df.columns:
            # Get all unique periods
            df['period'] = df['year'].astype(str) + 'Q' + df['quarter'].astype(str)
            periods = sorted(df['period'].unique(), reverse=True)  # Most recent first
            
            # Calculate metrics for each period
            for period in periods[:8]:  # Last 8 quarters
                period_data = df[df['period'] == period]
                if period_data.empty:
                    continue
                
                period_metrics = {}
                
                # Calculate median key metrics for this period
                if 'roe' in period_data.columns:
                    period_metrics['median_roe'] = period_data['roe'].median()
                
                if 'revenue_growth_yoy' in period_data.columns:
                    period_metrics['median_revenue_growth'] = period_data['revenue_growth_yoy'].median()
                
                if 'gross_margin' in period_data.columns:
                    period_metrics['median_gross_margin'] = period_data['gross_margin'].median()
                
                if 'debt_to_equity' in period_data.columns:
                    period_metrics['median_debt_to_equity'] = period_data['debt_to_equity'].median()
                
                quarterly_trends[period] = period_metrics
        
        metrics["quarterly_trends"] = quarterly_trends
        
        # Calculate distribution metrics
        distribution = {}
        
        # Market cap distribution
        market_cap = df["market_cap"].dropna()
        if not market_cap.empty:
            total_market_cap = market_cap.sum()
            
            # Calculate market cap percentiles
            distribution["market_cap"] = {
                "total": total_market_cap,
                "q1": np.percentile(market_cap, 25),
                "q2_median": np.percentile(market_cap, 50),
                "q3": np.percentile(market_cap, 75),
                "min": market_cap.min(),
                "max": market_cap.max(),
                "top_10_concentration": (market_cap.nlargest(10).sum() / total_market_cap) * 100
            }
        
        metrics["distribution_metrics"] = distribution
        
        # Calculate sector ranking
        ranking = {}
        
        # Create scoring based on multiple metrics
        scores = []
        for _, entity in df.iterrows():
            score = 0
            count = 0
            
            # Profitability score
            if "roe" in entity and not pd.isna(entity["roe"]):
                roe_score = min(100, entity["roe"] * 5)  # Scale ROE to 0-100
                score += roe_score
                count += 1
            
            # Growth score
            if "revenue_growth_yoy" in entity and not pd.isna(entity["revenue_growth_yoy"]):
                growth_score = max(0, 50 + entity["revenue_growth_yoy"] * 2)  # Scale growth to 0-100
                score += growth_score
                count += 1
            
            # Margin score
            if "gross_margin" in entity and not pd.isna(entity["gross_margin"]):
                margin_score = min(100, entity["gross_margin"] * 2)  # Scale margin to 0-100
                score += margin_score
                count += 1
            
            # Leverage score (inverse - lower is better)
            if "debt_to_equity" in entity and not pd.isna(entity["debt_to_equity"]):
                leverage_score = max(0, 100 - entity["debt_to_equity"] * 20)  # Scale leverage to 0-100
                score += leverage_score
                count += 1
            
            # Average score
            if count > 0:
                avg_score = score / count
                scores.append((entity["symbol"], avg_score))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Create ranking
        ranking = {
            "top_performers": [{"symbol": s, "score": round(score, 2)} for s, score in scores[:10]],
            "bottom_performers": [{"symbol": s, "score": round(score, 2)} for s, score in scores[-10:]],
            "full_ranking": [{"symbol": s, "score": round(score, 2), "rank": i+1} for i, (s, score) in enumerate(scores)]
        }
        
        metrics["sector_ranking"] = ranking
        
        return metrics
    
    def _generate_insights(self, entities: List[Dict], metrics: Dict[str, Any], sector: str) -> Dict[str, Any]:
        """
        Generate insights from fundamental analysis.
        
        Args:
            entities: List of entity dictionaries
            metrics: Sector metrics dictionary
            sector: Sector name
            
        Returns:
            Dictionary with insights
        """
        insights = {
            "sector_overview": [],
            "profitability_insights": [],
            "growth_insights": [],
            "risk_insights": [],
            "recommendations": []
        }
        
        # Sector overview insights
        ticker_count = len(entities)
        insights["sector_overview"].append(
            f"Sector {sector} contains {ticker_count} companies with available fundamental data"
        )
        
        # Profitability insights
        profitability = metrics.get("profitability_metrics", {})
        
        # ROE analysis
        roe_data = profitability.get("roe", {})
        if roe_data:
            median_roe = roe_data.get("median", 0)
            if median_roe > 15:
                insights["profitability_insights"].append(
                    f"Sector shows excellent profitability with median ROE of {median_roe:.1f}%"
                )
            elif median_roe > 10:
                insights["profitability_insights"].append(
                    f"Sector shows good profitability with median ROE of {median_roe:.1f}%"
                )
            elif median_roe > 5:
                insights["profitability_insights"].append(
                    f"Sector shows moderate profitability with median ROE of {median_roe:.1f}%"
                )
            else:
                insights["profitability_insights"].append(
                    f"Sector shows weak profitability with median ROE of {median_roe:.1f}%"
                )
        
        # Margin analysis
        gross_margin = profitability.get("gross_margin", {})
        if gross_margin:
            median_margin = gross_margin.get("median", 0)
            if median_margin > 40:
                insights["profitability_insights"].append(
                    f"Sector has high margins with median gross margin of {median_margin:.1f}%"
                )
            elif median_margin > 25:
                insights["profitability_insights"].append(
                    f"Sector has moderate margins with median gross margin of {median_margin:.1f}%"
                )
            elif median_margin > 15:
                insights["profitability_insights"].append(
                    f"Sector has low margins with median gross margin of {median_margin:.1f}%"
                )
            else:
                insights["profitability_insights"].append(
                    f"Sector has very low margins with median gross margin of {median_margin:.1f}%"
                )
        
        # Growth insights
        growth = metrics.get("growth_metrics", {})
        
        # Revenue growth analysis
        revenue_growth = growth.get("revenue_growth", {})
        if revenue_growth:
            median_growth = revenue_growth.get("median", 0)
            if median_growth > 15:
                insights["growth_insights"].append(
                    f"Sector shows strong revenue growth with median of {median_growth:.1f}%"
                )
            elif median_growth > 8:
                insights["growth_insights"].append(
                    f"Sector shows moderate revenue growth with median of {median_growth:.1f}%"
                )
            elif median_growth > 0:
                insights["growth_insights"].append(
                    f"Sector shows slow revenue growth with median of {median_growth:.1f}%"
                )
            else:
                insights["growth_insights"].append(
                    f"Sector shows declining revenue with median of {median_growth:.1f}%"
                )
        
        # Risk insights
        leverage = metrics.get("leverage_metrics", {})
        
        # Debt to equity analysis
        debt_to_equity = leverage.get("debt_to_equity", {})
        if debt_to_equity:
            median_dte = debt_to_equity.get("median", 0)
            if median_dte > 3:
                insights["risk_insights"].append(
                    f"Sector has high leverage with median debt-to-equity of {median_dte:.1f}"
                )
            elif median_dte > 1.5:
                insights["risk_insights"].append(
                    f"Sector has moderate leverage with median debt-to-equity of {median_dte:.1f}"
                )
            elif median_dte > 0.5:
                insights["risk_insights"].append(
                    f"Sector has low leverage with median debt-to-equity of {median_dte:.1f}"
                )
            else:
                insights["risk_insights"].append(
                    f"Sector has very low leverage with median debt-to-equity of {median_dte:.1f}"
                )
        
        # Banking-specific insights
        banking_metrics = leverage.get("banking_metrics", {})
        if banking_metrics and "Ngân hàng" in sector:
            # NIM analysis
            nim = banking_metrics.get("nim", {})
            if nim:
                median_nim = nim.get("median", 0)
                if median_nim > 4:
                    insights["profitability_insights"].append(
                        f"Banking sector shows strong NIM with median of {median_nim:.2f}%"
                    )
                elif median_nim > 2.5:
                    insights["profitability_insights"].append(
                        f"Banking sector shows moderate NIM with median of {median_nim:.2f}%"
                    )
                else:
                    insights["profitability_insights"].append(
                        f"Banking sector shows weak NIM with median of {median_nim:.2f}%"
                    )
            
            # CIR analysis
            cir = banking_metrics.get("cir", {})
            if cir:
                median_cir = cir.get("median", 0)
                if median_cir < 40:
                    insights["efficiency_insights"] = []  # Create if not exists
                    insights["efficiency_insights"].append(
                        f"Banking sector shows good efficiency with median CIR of {median_cir:.1f}%"
                    )
                elif median_cir < 60:
                    insights["efficiency_insights"] = []  # Create if not exists
                    insights["efficiency_insights"].append(
                        f"Banking sector shows moderate efficiency with median CIR of {median_cir:.1f}%"
                    )
                else:
                    insights["efficiency_insights"] = []  # Create if not exists
                    insights["efficiency_insights"].append(
                        f"Banking sector shows poor efficiency with median CIR of {median_cir:.1f}%"
                    )
            
            # NPL analysis
            npl = banking_metrics.get("npl_ratio", {})
            if npl:
                median_npl = npl.get("median", 0)
                if median_npl < 1:
                    insights["risk_insights"].append(
                        f"Banking sector shows good asset quality with median NPL ratio of {median_npl:.2f}%"
                    )
                elif median_npl < 2:
                    insights["risk_insights"].append(
                        f"Banking sector shows moderate asset quality with median NPL ratio of {median_npl:.2f}%"
                    )
                elif median_npl < 4:
                    insights["risk_insights"].append(
                        f"Banking sector shows poor asset quality with median NPL ratio of {median_npl:.2f}%"
                    )
        
        # Generate recommendations
        ranking = metrics.get("sector_ranking", {})
        top_performers = ranking.get("top_performers", [])
        
        if top_performers:
            # Focus on top 3 for recommendations
            top_3 = top_performers[:3]
            insights["recommendations"] = [
                f"Consider {top_3[0]['symbol']} - highest fundamental score in sector"
            ]
            
            if len(top_3) >= 2:
                insights["recommendations"].append(
                    f"Consider {top_3[1]['symbol']} - second highest fundamental score"
                )
            
            if len(top_3) >= 3:
                insights["recommendations"].append(
                    f"Consider {top_3[2]['symbol']} - third highest fundamental score"
                )
            
            # Add qualitative insights
            if "Ngân hàng" in sector:
                insights["recommendations"].append(
                    "Focus on banks with high NIM and low CIR for best profitability"
                )
            elif "Bất động sản" in sector or "Xây dựng" in sector:
                insights["recommendations"].append(
                    "Monitor interest rate trends as they significantly impact real estate sector"
                )
            elif "Bán lẻ" in sector:
                insights["recommendations"].append(
                    "Focus on companies with strong revenue growth and efficient operations"
                )
        
        return insights
    
    def compare_sectors(self, sectors: List[str], quarters: int = 4) -> Dict[str, Any]:
        """
        Compare multiple sectors on fundamental metrics.
        
        Args:
            sectors: List of sector names to compare
            quarters: Number of recent quarters to analyze
            
        Returns:
            Dictionary with sector comparison data
        """
        if not sectors or not isinstance(sectors, list):
            raise ValueError("Sectors must be a non-empty list")
            
        if len(sectors) < 2:
            raise ValueError("Need at least 2 sectors for comparison")
        
        # Analyze each sector
        sector_results = {}
        for sector in sectors:
            try:
                sector_results[sector] = self.analyze_sector(sector, quarters)
            except Exception as e:
                sector_results[sector] = {
                    "error": True,
                    "message": str(e)
                }
        
        # Create comparison tables
        comparison = {
            "sectors": sectors,
            "quarters_analyzed": quarters,
            "results": sector_results,
            "comparison_tables": self._create_comparison_tables(sector_results)
        }
        
        return comparison
    
    def _create_comparison_tables(self, sector_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comparison tables from sector results.
        
        Args:
            sector_results: Dictionary of sector analysis results
            
        Returns:
            Dictionary with comparison tables
        """
        tables = {
            "profitability_comparison": [],
            "growth_comparison": [],
            "leverage_comparison": [],
            "overall_ranking": []
        }
        
        # Extract key metrics for comparison
        for sector, result in sector_results.items():
            if "error" in result:
                continue
                
            # Get sector metrics
            if "sector_metrics" not in result:
                continue
                
            metrics = result["sector_metrics"]
            
            # Profitability comparison
            profitability = metrics.get("profitability_metrics", {})
            tables["profitability_comparison"].append({
                "sector": sector,
                "median_roe": profitability.get("roe", {}).get("median", 0),
                "median_roa": profitability.get("roa", {}).get("median", 0),
                "median_gross_margin": profitability.get("gross_margin", {}).get("median", 0),
                "median_operating_margin": profitability.get("operating_margin", {}).get("median", 0)
            })
            
            # Growth comparison
            growth = metrics.get("growth_metrics", {})
            tables["growth_comparison"].append({
                "sector": sector,
                "median_revenue_growth": growth.get("revenue_growth", {}).get("median", 0),
                "median_profit_growth": growth.get("profit_growth", {}).get("median", 0)
            })
            
            # Leverage comparison
            leverage = metrics.get("leverage_metrics", {})
            tables["leverage_comparison"].append({
                "sector": sector,
                "median_debt_to_equity": leverage.get("debt_to_equity", {}).get("median", 0),
                "median_current_ratio": leverage.get("current_ratio", {}).get("median", 0)
            })
            
            # Overall ranking (top performers)
            ranking = metrics.get("sector_ranking", {})
            top_performers = ranking.get("top_performers", [])
            if top_performers:
                # Get top 3 average score
                top_scores = [p.get("score", 0) for p in top_performers[:3]]
                avg_top_score = sum(top_scores) / len(top_scores) if top_scores else 0
                
                tables["overall_ranking"].append({
                    "sector": sector,
                    "top_3_avg_score": round(avg_top_score, 2),
                    "top_performer": top_performers[0]["symbol"] if top_performers else None,
                    "top_score": top_performers[0]["score"] if top_performers else 0
                })
        
        # Sort tables by relevant metrics
        tables["profitability_comparison"] = sorted(
            tables["profitability_comparison"],
            key=lambda x: x.get("median_roe", 0),
            reverse=True
        )
        
        tables["growth_comparison"] = sorted(
            tables["growth_comparison"],
            key=lambda x: x.get("median_revenue_growth", 0),
            reverse=True
        )
        
        tables["overall_ranking"] = sorted(
            tables["overall_ranking"],
            key=lambda x: x.get("top_3_avg_score", 0),
            reverse=True
        )
        
        return tables
    
    def get_available_sectors(self) -> List[str]:
        """
        Get list of sectors with fundamental data.
        
        Returns:
            List of sector names
        """
        try:
            sectors = self.sector_registry.get_all_sectors()
            
            # Filter to only sectors with fundamental data
            sectors_with_data = []
            for sector in sectors:
                try:
                    tickers = self.sector_registry.get_tickers_by_sector(sector)
                    if tickers:  # Only include sectors with tickers
                        sectors_with_data.append(sector)
                except Exception:
                    # Skip sectors with errors
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


# Convenience function for quick sector FA analysis
def analyze_sector_fa(sector: str, quarters: int = 4, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Quick function to analyze a sector's fundamentals.
    
    Args:
        sector: Sector name to analyze
        quarters: Number of recent quarters to analyze
        config: Optional configuration
        
    Returns:
        Analysis result dictionary
    """
    analyzer = SectorFAAnalyzer(config)
    return analyzer.analyze_sector(sector, quarters)