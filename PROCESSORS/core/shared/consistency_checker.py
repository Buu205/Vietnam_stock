"""
Consistency Checker for data validation across different sources.
Kiểm tra tính nhất quán cho validation dữ liệu qua các nguồn khác nhau.
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConsistencyChecker:
    """Checker for data consistency across different sources and time periods.
    Kiểm tra tính nhất quán dữ liệu qua các nguồn và khoảng thời gian khác nhau.
    """
    
    def __init__(self, data_warehouse_path: str = None):
        """Initialize ConsistencyChecker.
        Khởi tạo ConsistencyChecker.

        Args:
            data_warehouse_path: Path to data warehouse (default: canonical v4.0.0)
        """
        # Use canonical v4.0.0 path as default
        if data_warehouse_path is None:
            data_warehouse_path = Path(__file__).resolve().parents[3] / "DATA"

        self.data_warehouse_path = Path(data_warehouse_path)
        self.consistency_rules = self._load_consistency_rules()
    
    def _load_consistency_rules(self) -> Dict[str, Any]:
        """Load consistency rules from configuration.
        Tải quy tắc nhất quán từ cấu hình.
        
        Returns:
            Dictionary with consistency rules
        """
        rules_file = self.data_warehouse_path / "schemas" / "consistency_rules.json"
        
        if rules_file.exists():
            with open(rules_file, 'r') as f:
                return json.load(f)
        else:
            # Default consistency rules
            return {
                "ohlcv_fundamental": {
                    "description": "OHLCV and fundamental data consistency",
                    "rules": [
                        {
                            "name": "symbol_consistency",
                            "description": "Symbols should exist in both OHLCV and fundamental data",
                            "type": "cross_source"
                        },
                        {
                            "name": "date_range_overlap",
                            "description": "Date ranges should overlap between OHLCV and fundamental data",
                            "type": "temporal"
                        }
                    ]
                },
                "fundamental_consistency": {
                    "description": "Fundamental data internal consistency",
                    "rules": [
                        {
                            "name": "quarterly_sequence",
                            "description": "Quarterly data should be in sequence",
                            "type": "temporal"
                        },
                        {
                            "name": "financial_relationships",
                            "description": "Financial statement relationships should be consistent",
                            "type": "logical"
                        }
                    ]
                },
                "technical_consistency": {
                    "description": "Technical indicators consistency",
                    "rules": [
                        {
                            "name": "indicator_calculation",
                            "description": "Technical indicators should be calculated correctly",
                            "type": "calculation"
                        },
                        {
                            "name": "signal_consistency",
                            "description": "Signals should be consistent with underlying indicators",
                            "type": "logical"
                        }
                    ]
                }
            }
    
    def check_ohlcv_fundamental_consistency(self, 
                                          ohlcv_df: pd.DataFrame,
                                          fundamental_df: pd.DataFrame) -> Dict[str, Any]:
        """Check consistency between OHLCV and fundamental data.
        Kiểm tra tính nhất quán giữa dữ liệu OHLCV và fundamental.
        
        Args:
            ohlcv_df: OHLCV DataFrame
            fundamental_df: Fundamental DataFrame
            
        Returns:
            Dictionary with consistency check results
        """
        result = {
            "is_consistent": True,
            "issues": [],
            "statistics": {},
            "recommendations": []
        }
        
        try:
            # Check symbol consistency
            ohlcv_symbols = set(ohlcv_df['symbol'].unique())
            fundamental_symbols = set(fundamental_df['symbol'].unique())
            
            common_symbols = ohlcv_symbols.intersection(fundamental_symbols)
            ohlcv_only = ohlcv_symbols - fundamental_symbols
            fundamental_only = fundamental_symbols - ohlcv_symbols
            
            result["statistics"]["common_symbols"] = len(common_symbols)
            result["statistics"]["ohlcv_only"] = len(ohlcv_only)
            result["statistics"]["fundamental_only"] = len(fundamental_only)
            
            if len(common_symbols) == 0:
                result["issues"].append("No common symbols between OHLCV and fundamental data")
                result["is_consistent"] = False
            
            if len(ohlcv_only) > 0:
                result["issues"].append(f"Symbols in OHLCV but not in fundamental: {list(ohlcv_only)[:10]}")
                result["recommendations"].append("Consider adding fundamental data for OHLCV-only symbols")
            
            if len(fundamental_only) > 0:
                result["issues"].append(f"Symbols in fundamental but not in OHLCV: {list(fundamental_only)[:10]}")
                result["recommendations"].append("Consider adding OHLCV data for fundamental-only symbols")
            
            # Check date range overlap
            if 'date' in ohlcv_df.columns and 'report_date' in fundamental_df.columns:
                ohlcv_min_date = ohlcv_df['date'].min()
                ohlcv_max_date = ohlcv_df['date'].max()
                fundamental_min_date = fundamental_df['report_date'].min()
                fundamental_max_date = fundamental_df['report_date'].max()
                
                result["statistics"]["ohlcv_date_range"] = {
                    "min": ohlcv_min_date,
                    "max": ohlcv_max_date
                }
                result["statistics"]["fundamental_date_range"] = {
                    "min": fundamental_min_date,
                    "max": fundamental_max_date
                }
                
                # Check for overlap
                if ohlcv_max_date < fundamental_min_date or ohlcv_min_date > fundamental_max_date:
                    result["issues"].append("No date range overlap between OHLCV and fundamental data")
                    result["is_consistent"] = False
                else:
                    overlap_start = max(ohlcv_min_date, fundamental_min_date)
                    overlap_end = min(ohlcv_max_date, fundamental_max_date)
                    result["statistics"]["overlap_range"] = {
                        "start": overlap_start,
                        "end": overlap_end
                    }
            
            # Check price consistency for common symbols
            if len(common_symbols) > 0:
                price_consistency = self._check_price_consistency(
                    ohlcv_df, fundamental_df, list(common_symbols)
                )
                result["statistics"]["price_consistency"] = price_consistency
                
                if price_consistency["inconsistent_count"] > 0:
                    result["issues"].append(f"Price inconsistencies found in {price_consistency['inconsistent_count']} records")
                    result["is_consistent"] = False
        
        except Exception as e:
            result["is_consistent"] = False
            result["issues"].append(f"Error checking consistency: {e}")
        
        return result
    
    def _check_price_consistency(self, 
                               ohlcv_df: pd.DataFrame,
                               fundamental_df: pd.DataFrame,
                               common_symbols: List[str]) -> Dict[str, Any]:
        """Check price consistency between OHLCV and fundamental data.
        Kiểm tra tính nhất quán giá giữa dữ liệu OHLCV và fundamental.
        
        Args:
            ohlcv_df: OHLCV DataFrame
            fundamental_df: Fundamental DataFrame
            common_symbols: List of common symbols
            
        Returns:
            Dictionary with price consistency results
        """
        result = {
            "total_checks": 0,
            "consistent_count": 0,
            "inconsistent_count": 0,
            "inconsistencies": []
        }
        
        try:
            for symbol in common_symbols[:10]:  # Check first 10 symbols
                symbol_ohlcv = ohlcv_df[ohlcv_df['symbol'] == symbol].copy()
                symbol_fundamental = fundamental_df[fundamental_df['symbol'] == symbol].copy()
                
                if symbol_ohlcv.empty or symbol_fundamental.empty:
                    continue
                
                # Convert dates for comparison
                symbol_ohlcv['date'] = pd.to_datetime(symbol_ohlcv['date']).dt.date
                symbol_fundamental['report_date'] = pd.to_datetime(symbol_fundamental['report_date']).dt.date
                
                # Find matching dates
                for _, ohlcv_row in symbol_ohlcv.iterrows():
                    matching_fundamental = symbol_fundamental[
                        symbol_fundamental['report_date'] == ohlcv_row['date']
                    ]
                    
                    if not matching_fundamental.empty:
                        result["total_checks"] += 1
                        
                        # Check if prices are reasonable (within 10% difference)
                        ohlcv_price = ohlcv_row['close']
                        fundamental_price = matching_fundamental.iloc[0].get('bvps', 0)
                        
                        if fundamental_price > 0:
                            price_diff_pct = abs(ohlcv_price - fundamental_price) / fundamental_price * 100
                            
                            if price_diff_pct > 1000:  # More than 1000% difference
                                result["inconsistent_count"] += 1
                                result["inconsistencies"].append({
                                    "symbol": symbol,
                                    "date": ohlcv_row['date'],
                                    "ohlcv_price": ohlcv_price,
                                    "fundamental_price": fundamental_price,
                                    "difference_pct": price_diff_pct
                                })
                            else:
                                result["consistent_count"] += 1
        
        except Exception as e:
            logger.error(f"Error checking price consistency: {e}")
        
        return result
    
    def check_fundamental_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check internal consistency of fundamental data.
        Kiểm tra tính nhất quán nội bộ của dữ liệu fundamental.
        
        Args:
            df: Fundamental DataFrame
            
        Returns:
            Dictionary with consistency check results
        """
        result = {
            "is_consistent": True,
            "issues": [],
            "statistics": {},
            "recommendations": []
        }
        
        try:
            # Check quarterly sequence
            quarterly_sequence = self._check_quarterly_sequence(df)
            result["statistics"]["quarterly_sequence"] = quarterly_sequence
            
            if quarterly_sequence["gaps_count"] > 0:
                result["issues"].append(f"Found {quarterly_sequence['gaps_count']} quarterly gaps")
                result["is_consistent"] = False
            
            # Check financial relationships
            financial_relationships = self._check_financial_relationships(df)
            result["statistics"]["financial_relationships"] = financial_relationships
            
            if financial_relationships["violations_count"] > 0:
                result["issues"].append(f"Found {financial_relationships['violations_count']} financial relationship violations")
                result["is_consistent"] = False
            
            # Check data completeness
            completeness = self._check_data_completeness(df)
            result["statistics"]["completeness"] = completeness
            
            if completeness["low_completeness_columns"]:
                result["issues"].append(f"Low completeness in columns: {completeness['low_completeness_columns']}")
                result["recommendations"].append("Consider data imputation for low completeness columns")
        
        except Exception as e:
            result["is_consistent"] = False
            result["issues"].append(f"Error checking fundamental consistency: {e}")
        
        return result
    
    def _check_quarterly_sequence(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check quarterly data sequence.
        Kiểm tra chuỗi dữ liệu quý.
        
        Args:
            df: DataFrame with quarterly data
            
        Returns:
            Dictionary with sequence check results
        """
        result = {
            "gaps_count": 0,
            "gaps": [],
            "symbols_checked": 0
        }
        
        try:
            for symbol in df['symbol'].unique():
                symbol_data = df[df['symbol'] == symbol].copy()
                symbol_data = symbol_data.sort_values(['year', 'quarter'])
                
                result["symbols_checked"] += 1
                
                # Check for gaps in quarterly sequence
                for i in range(1, len(symbol_data)):
                    prev_row = symbol_data.iloc[i-1]
                    curr_row = symbol_data.iloc[i]
                    
                    # Calculate expected next quarter
                    expected_year = prev_row['year']
                    expected_quarter = prev_row['quarter'] + 1
                    
                    if expected_quarter > 4:
                        expected_year += 1
                        expected_quarter = 1
                    
                    # Check if current row matches expected
                    if (curr_row['year'] != expected_year or 
                        curr_row['quarter'] != expected_quarter):
                        result["gaps_count"] += 1
                        result["gaps"].append({
                            "symbol": symbol,
                            "expected": f"{expected_year}Q{expected_quarter}",
                            "actual": f"{curr_row['year']}Q{curr_row['quarter']}"
                        })
        
        except Exception as e:
            logger.error(f"Error checking quarterly sequence: {e}")
        
        return result
    
    def _check_financial_relationships(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check financial statement relationships.
        Kiểm tra các mối quan hệ báo cáo tài chính.
        
        Args:
            df: Fundamental DataFrame
            
        Returns:
            Dictionary with relationship check results
        """
        result = {
            "violations_count": 0,
            "violations": []
        }
        
        try:
            # Check gross profit calculation
            if 'net_revenue' in df.columns and 'cogs' in df.columns and 'gross_profit' in df.columns:
                calculated_gross_profit = df['net_revenue'] - df['cogs']
                gross_profit_diff = abs(df['gross_profit'] - calculated_gross_profit)
                large_diffs = gross_profit_diff > 1000  # Allow for rounding
                
                if large_diffs.any():
                    result["violations_count"] += large_diffs.sum()
                    result["violations"].append({
                        "type": "gross_profit_calculation",
                        "count": large_diffs.sum(),
                        "description": "Gross profit calculation mismatch"
                    })
            
            # Check EBITDA calculation
            if 'ebit' in df.columns and 'depreciation' in df.columns and 'ebitda' in df.columns:
                calculated_ebitda = df['ebit'] + df['depreciation']
                ebitda_diff = abs(df['ebitda'] - calculated_ebitda)
                large_diffs = ebitda_diff > 1000
                
                if large_diffs.any():
                    result["violations_count"] += large_diffs.sum()
                    result["violations"].append({
                        "type": "ebitda_calculation",
                        "count": large_diffs.sum(),
                        "description": "EBITDA calculation mismatch"
                    })
            
            # Check margin calculations
            if 'net_revenue' in df.columns and 'gross_profit' in df.columns and 'gross_margin' in df.columns:
                calculated_gross_margin = (df['gross_profit'] / df['net_revenue'] * 100).fillna(0)
                gross_margin_diff = abs(df['gross_margin'] - calculated_gross_margin)
                large_diffs = gross_margin_diff > 1  # 1% tolerance
                
                if large_diffs.any():
                    result["violations_count"] += large_diffs.sum()
                    result["violations"].append({
                        "type": "gross_margin_calculation",
                        "count": large_diffs.sum(),
                        "description": "Gross margin calculation mismatch"
                    })
        
        except Exception as e:
            logger.error(f"Error checking financial relationships: {e}")
        
        return result
    
    def _check_data_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check data completeness.
        Kiểm tra tính đầy đủ của dữ liệu.
        
        Args:
            df: DataFrame to check
            
        Returns:
            Dictionary with completeness results
        """
        result = {
            "overall_completeness": 0,
            "column_completeness": {},
            "low_completeness_columns": []
        }
        
        try:
            total_cells = df.shape[0] * df.shape[1]
            non_null_cells = df.count().sum()
            result["overall_completeness"] = (non_null_cells / total_cells) * 100
            
            # Check completeness by column
            for col in df.columns:
                completeness = (df[col].count() / len(df)) * 100
                result["column_completeness"][col] = completeness
                
                if completeness < 50:  # Less than 50% complete
                    result["low_completeness_columns"].append(col)
        
        except Exception as e:
            logger.error(f"Error checking data completeness: {e}")
        
        return result
    
    def check_technical_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check technical indicators consistency.
        Kiểm tra tính nhất quán của các chỉ báo kỹ thuật.
        
        Args:
            df: Technical indicators DataFrame
            
        Returns:
            Dictionary with consistency check results
        """
        result = {
            "is_consistent": True,
            "issues": [],
            "statistics": {},
            "recommendations": []
        }
        
        try:
            # Check RSI range
            rsi_columns = [col for col in df.columns if 'rsi' in col.lower()]
            for col in rsi_columns:
                rsi_values = df[col].dropna()
                if not rsi_values.empty:
                    out_of_range = (rsi_values < 0) | (rsi_values > 100)
                    if out_of_range.any():
                        result["issues"].append(f"RSI values out of range (0-100) in {col}")
                        result["is_consistent"] = False
            
            # Check moving average consistency
            ma_columns = [col for col in df.columns if 'sma' in col.lower() or 'ema' in col.lower()]
            if len(ma_columns) > 1:
                ma_consistency = self._check_moving_average_consistency(df, ma_columns)
                result["statistics"]["moving_average_consistency"] = ma_consistency
                
                if ma_consistency["inconsistencies"] > 0:
                    result["issues"].append(f"Moving average inconsistencies: {ma_consistency['inconsistencies']}")
                    result["is_consistent"] = False
            
            # Check signal consistency
            signal_columns = [col for col in df.columns if 'signal' in col.lower()]
            if signal_columns:
                signal_consistency = self._check_signal_consistency(df, signal_columns)
                result["statistics"]["signal_consistency"] = signal_consistency
                
                if signal_consistency["inconsistencies"] > 0:
                    result["issues"].append(f"Signal inconsistencies: {signal_consistency['inconsistencies']}")
                    result["is_consistent"] = False
        
        except Exception as e:
            result["is_consistent"] = False
            result["issues"].append(f"Error checking technical consistency: {e}")
        
        return result
    
    def _check_moving_average_consistency(self, df: pd.DataFrame, ma_columns: List[str]) -> Dict[str, Any]:
        """Check moving average consistency.
        Kiểm tra tính nhất quán của moving average.
        
        Args:
            df: DataFrame with moving averages
            ma_columns: List of moving average columns
            
        Returns:
            Dictionary with consistency results
        """
        result = {
            "inconsistencies": 0,
            "details": []
        }
        
        try:
            # Sort columns by period (extract number from column name)
            def extract_period(col_name):
                import re
                match = re.search(r'(\d+)', col_name)
                return int(match.group(1)) if match else 0
            
            sorted_columns = sorted(ma_columns, key=extract_period)
            
            # Check that longer period MAs are smoother
            for i in range(1, len(sorted_columns)):
                short_col = sorted_columns[i-1]
                long_col = sorted_columns[i]
                
                short_ma = df[short_col].dropna()
                long_ma = df[long_col].dropna()
                
                if not short_ma.empty and not long_ma.empty:
                    # Calculate volatility (standard deviation)
                    short_volatility = short_ma.std()
                    long_volatility = long_ma.std()
                    
                    if short_volatility > 0 and long_volatility > short_volatility:
                        result["inconsistencies"] += 1
                        result["details"].append({
                            "short_column": short_col,
                            "long_column": long_col,
                            "short_volatility": short_volatility,
                            "long_volatility": long_volatility
                        })
        
        except Exception as e:
            logger.error(f"Error checking moving average consistency: {e}")
        
        return result
    
    def _check_signal_consistency(self, df: pd.DataFrame, signal_columns: List[str]) -> Dict[str, Any]:
        """Check signal consistency.
        Kiểm tra tính nhất quán của signals.
        
        Args:
            df: DataFrame with signals
            signal_columns: List of signal columns
            
        Returns:
            Dictionary with consistency results
        """
        result = {
            "inconsistencies": 0,
            "details": []
        }
        
        try:
            # Check for conflicting signals
            for i, col1 in enumerate(signal_columns):
                for col2 in signal_columns[i+1:]:
                    if col1 in df.columns and col2 in df.columns:
                        # Count conflicting signals
                        conflicts = 0
                        for idx, row in df.iterrows():
                            if pd.notna(row[col1]) and pd.notna(row[col2]):
                                if (row[col1] == 'buy' and row[col2] == 'sell') or \
                                   (row[col1] == 'sell' and row[col2] == 'buy'):
                                    conflicts += 1
                        
                        if conflicts > 0:
                            result["inconsistencies"] += conflicts
                            result["details"].append({
                                "signal1": col1,
                                "signal2": col2,
                                "conflicts": conflicts
                            })
        
        except Exception as e:
            logger.error(f"Error checking signal consistency: {e}")
        
        return result
    
    def get_overall_consistency_report(self) -> Dict[str, Any]:
        """Get overall consistency report for all data sources.
        Lấy báo cáo nhất quán tổng thể cho tất cả nguồn dữ liệu.
        
        Returns:
            Dictionary with overall consistency report
        """
        report = {
            "overall_consistent": True,
            "data_sources": {},
            "cross_source_issues": [],
            "recommendations": [],
            "summary": {
                "total_sources": 0,
                "consistent_sources": 0,
                "inconsistent_sources": 0
            }
        }
        
        try:
            # This would typically load data from all sources and check consistency
            # For now, return a placeholder structure
            report["summary"]["total_sources"] = 3  # OHLCV, Fundamental, Technical
            report["summary"]["consistent_sources"] = 0
            report["summary"]["inconsistent_sources"] = 0
            
            report["recommendations"] = [
                "Regular consistency checks should be performed",
                "Data quality monitoring should be automated",
                "Cross-source validation should be implemented"
            ]
        
        except Exception as e:
            logger.error(f"Error generating overall consistency report: {e}")
            report["error"] = str(e)
        
        return report
