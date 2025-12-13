#!/usr/bin/env python3
"""
Calculator Usage Example - How to Use Refactored Calculators
========================================================

This script demonstrates how to use the refactored financial calculators
for different entity types (Company, Bank, Insurance, Security).
Script này minh họa cách sử dụng các bộ tính toán tài chính đã tái cấu trúc
cho các loại hình thực thể khác nhau (Doanh nghiệp, Ngân hàng, Bảo hiểm, Chứng khoán).

Examples:
1. Calculate metrics for a specific ticker
2. Calculate sector-wide metrics
3. Compare peer companies
4. Calculate industry-specific metrics (e.g., NIM for banks)

Author: Claude Code
Date: 2025-12-07
"""

import os
import pandas as pd
from pathlib import Path
import logging

# Use relative imports instead of sys.path manipulation
from PROCESSORS.core.shared.unified_mapper import UnifiedTickerMapper
from PROCESSORS.fundamental.calculators import (
    CompanyFinancialCalculator,
    BankFinancialCalculator,
    InsuranceFinancialCalculator,
    SecurityFinancialCalculator
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalculatorUsageExample:
    """
    Example class demonstrating calculator usage patterns.
    Lớp ví dụ minh họa các mẫu sử dụng bộ tính toán.
    """
    
    def __init__(self):
        """
        Initialize example with data paths and mapper.
        Khởi tạo ví dụ với đường dẫn dữ liệu và bộ ánh xạ.
        """
        self.base_path = Path(__file__).parent.parent.parent.parent.parent
        self.data_paths = {
            "COMPANY": self.base_path / "DATA/raw/fundamental/processed/company_full.parquet",
            "BANK": self.base_path / "DATA/raw/fundamental/processed/bank_full.parquet",
            "INSURANCE": self.base_path / "DATA/raw/fundamental/processed/insurance_full.parquet",
            "SECURITY": self.base_path / "DATA/raw/fundamental/processed/security_full.parquet"
        }
        self.calculators = {
            "COMPANY": CompanyFinancialCalculator,
            "BANK": BankFinancialCalculator,
            "INSURANCE": InsuranceFinancialCalculator,
            "SECURITY": SecurityFinancialCalculator
        }
        self.unified_mapper = UnifiedTickerMapper()
    
    def example_1_calculate_single_ticker(self, ticker: str):
        """
        Example 1: Calculate metrics for a single ticker.
        
        Demonstrates:
        - Auto entity detection
        - Calculator selection
        - Metric calculation
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"EXAMPLE 1: Calculate metrics for {ticker}")
        logger.info(f"{'='*60}")
        
        # Get entity type for ticker
        entity_type = self.unified_mapper.get_entity_type(ticker)
        logger.info(f"Entity type: {entity_type}")
        
        # Select appropriate calculator
        calculator_class = self.calculators[entity_type]
        calculator = calculator_class(str(self.data_paths[entity_type]))
        
        # Calculate metrics
        results = calculator.calculate_all_metrics(ticker)
        
        logger.info(f"Results shape: {results.shape}")
        logger.info(f"Metrics calculated: {len(results.columns)}")
        
        # Print sample results
        if not results.empty:
            logger.info(f"\nSample results for {ticker}:")
            sample_cols = ['symbol', 'report_date', 'year', 'quarter']
            if entity_type == "COMPANY":
                sample_cols.extend(['net_revenue', 'npatmi', 'roe', 'eps'])
            elif entity_type == "BANK":
                sample_cols.extend(['nim_q', 'roea_ttm', 'ldr_pure', 'npl_ratio'])
            elif entity_type == "INSURANCE":
                sample_cols.extend(['combined_ratio', 'loss_ratio', 'solvency_ratio'])
            elif entity_type == "SECURITY":
                sample_cols.extend(['brokerage_ratio', 'prop_trading_ratio', 'leverage_ratio'])
            
            available_cols = [col for col in sample_cols if col in results.columns]
            logger.info(results[available_cols].head(3).to_string())
        
        return results
    
    def example_2_calculate_sector_metrics(self, entity_type: str, metric: str):
        """
        Example 2: Calculate metrics for all entities of a type.
        
        Demonstrates:
        - Multiple ticker processing
        - Aggregation
        - Sector-wide analysis
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"EXAMPLE 2: Calculate {metric} for all {entity_type}s")
        logger.info(f"{'='*60}")
        
        # Get all tickers for entity type
        tickers = self.unified_mapper.sector_registry.get_tickers_by_entity_type(entity_type)
        logger.info(f"Found {len(tickers)} tickers for {entity_type}")
        
        # Select calculator
        calculator_class = self.calculators[entity_type]
        calculator = calculator_class(str(self.data_paths[entity_type]))
        
        # Calculate metrics for all tickers
        all_results = []
        
        # Process in batches to avoid memory issues
        batch_size = 50
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(tickers)-1)//batch_size + 1}: {len(batch)} tickers")
            
            # Calculate for batch
            batch_results = calculator.calculate_all_metrics()  # Calculate for all
            if metric in batch_results.columns:
                all_results.append(batch_results)
        
        # Combine results
        if all_results:
            combined = pd.concat(all_results, ignore_index=True)
            
            # Get latest quarter
            latest_date = combined['report_date'].max()
            latest_data = combined[combined['report_date'] == latest_date]
            
            # Calculate statistics
            metric_stats = latest_data[metric].describe()
            
            logger.info(f"\n{metric} statistics for {entity_type} sector (latest quarter {latest_date}):")
            logger.info(metric_stats.to_string())
            
            # Show top 10 and bottom 10 by metric
            if metric in latest_data.columns:
                top_10 = latest_data.nlargest(10, metric)
                bottom_10 = latest_data.nsmallest(10, metric)
                
                logger.info(f"\nTop 10 by {metric}:")
                logger.info(top_10[['symbol', metric]].to_string())
                
                logger.info(f"\nBottom 10 by {metric}:")
                logger.info(bottom_10[['symbol', metric]].to_string())
            
            return combined
        else:
            logger.warning(f"No results found for {entity_type} sector")
            return pd.DataFrame()
    
    def example_3_compare_peers(self, ticker: str, metric: str):
        """
        Example 3: Compare a ticker with its peers.
        
        Demonstrates:
        - Peer identification
        - Comparative analysis
        - Benchmarking
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"EXAMPLE 3: Compare {ticker} with peers on {metric}")
        logger.info(f"{'='*60}")
        
        # Get peer information
        peer_info = self.unified_mapper.get_peer_comparison_info(ticker)
        entity_type = peer_info['entity_type']
        sector = peer_info['sector']
        peers = peer_info['peer_tickers']
        
        logger.info(f"Ticker: {ticker}")
        logger.info(f"Entity Type: {entity_type}")
        logger.info(f"Sector: {sector}")
        logger.info(f"Peers: {len(peers)} tickers")
        
        # Select calculator
        calculator_class = self.calculators[entity_type]
        calculator = calculator_class(str(self.data_paths[entity_type]))
        
        # Calculate for all peers
        all_results = calculator.calculate_all_metrics()
        
        # Filter for ticker and peers
        comparison_symbols = [ticker] + peers
        comparison_data = all_results[all_results['symbol'].isin(comparison_symbols)]
        
        # Get latest quarter
        latest_date = comparison_data['report_date'].max()
        latest_data = comparison_data[comparison_data['report_date'] == latest_date]
        
        if metric in latest_data.columns:
            # Create comparison table
            comparison_table = latest_data[['symbol', metric]].copy()
            comparison_table = comparison_table.sort_values(metric, ascending=False)
            
            # Find target ticker rank
            target_row = comparison_table[comparison_table['symbol'] == ticker]
            target_value = target_row[metric].iloc[0] if not target_row.empty else None
            target_rank = (comparison_table[metric] > target_value).sum() + 1 if target_value is not None else None
            
            logger.info(f"\n{metric} comparison for {sector} sector (as of {latest_date}):")
            logger.info(comparison_table.to_string())
            
            if target_value is not None and target_rank is not None:
                total_peers = len(comparison_table)
                percentile = (total_peers - target_rank) / total_peers * 100
                logger.info(f"\n{ticker} performance:")
                logger.info(f"  {metric}: {target_value:.2f}")
                logger.info(f"  Rank: {target_rank}/{total_peers}")
                logger.info(f"  Percentile: {percentile:.1f}%")
            
            return comparison_table
        else:
            logger.warning(f"Metric {metric} not found in results")
            return pd.DataFrame()
    
    def example_4_industry_specific_metric(self, ticker: str, metric: str):
        """
        Example 4: Calculate industry-specific metrics.
        
        Demonstrates:
        - Industry-specific calculations
        - Specialized metrics (e.g., NIM for banks)
        - Entity-specific insights
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"EXAMPLE 4: Calculate {metric} (industry-specific) for {ticker}")
        logger.info(f"{'='*60}")
        
        # Get entity type
        entity_type = self.unified_mapper.get_entity_type(ticker)
        
        # Select calculator
        calculator_class = self.calculators[entity_type]
        calculator = calculator_class(str(self.data_paths[entity_type]))
        
        # Calculate metrics for ticker
        results = calculator.calculate_all_metrics(ticker)
        
        # Get ticker's historical data for analysis
        if not results.empty and metric in results.columns:
            # Create analysis table
            analysis_table = results[['symbol', 'report_date', 'year', 'quarter', metric]].copy()
            analysis_table = analysis_table.sort_values('report_date')
            
            # Calculate trend
            if len(analysis_table) >= 2:
                latest_value = analysis_table[metric].iloc[-1]
                previous_value = analysis_table[metric].iloc[-2]
                
                if pd.notna(latest_value) and pd.notna(previous_value) and previous_value != 0:
                    change = latest_value - previous_value
                    change_pct = (change / abs(previous_value)) * 100
                    
                    trend = "↑ Improving" if change > 0 else "↓ Declining" if change < 0 else "→ Stable"
                    
                    logger.info(f"\n{metric} analysis for {ticker}:")
                    logger.info(f"  Latest: {latest_value:.2f}")
                    logger.info(f"  Previous: {previous_value:.2f}")
                    logger.info(f"  Change: {change:.2f} ({change_pct:.1f}%)")
                    logger.info(f"  Trend: {trend}")
                
            # Show full history
            logger.info(f"\nHistorical {metric} for {ticker}:")
            logger.info(analysis_table.to_string())
            
            return analysis_table
        else:
            logger.warning(f"Metric {metric} not found for {ticker}")
            return pd.DataFrame()

def main():
    """Main function to run all examples."""
    example = CalculatorUsageExample()
    
    # Example 1: Single ticker analysis
    example.example_1_calculate_single_ticker("ACB")  # Bank
    
    # Example 2: Sector-wide analysis
    example.example_2_calculate_sector_metrics("BANK", "roea_ttm")
    
    # Example 3: Peer comparison
    example.example_3_compare_peers("ACB", "nim_q")
    
    # Example 4: Industry-specific metrics
    example.example_4_industry_specific_metric("ACB", "nim_q")

if __name__ == "__main__":
    main()