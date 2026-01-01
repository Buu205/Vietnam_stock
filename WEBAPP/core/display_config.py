"""
Centralized display configuration for all data formatting.
Cấu hình hiển thị tập trung cho tất cả định dạng dữ liệu.
"""

from typing import Dict, List, Any
import pandas as pd
import streamlit as st
from .formatters import format_value, format_valuation_df, format_summary_data

class DisplayConfigManager:
    """
    Manages display configuration for all data types.
    Quản lý cấu hình hiển thị cho tất cả các loại dữ liệu.
    """
    
    def __init__(self):
        self.column_formats = {
            # Financial data columns
            'financial_currency': [
                'net_revenue', 'gross_profit', 'ebit', 'ebitda', 'npatmi',
                'total_assets', 'total_equity', 'net_interest_income', 'net_income',
                'cash', 'inventory', 'receivables', 'fixed_assets',
                'operating_cf', 'investing_cf', 'financing_cf', 'capex', 'free_cash_flow'
            ],
            'financial_percentage': [
                'gross_margin', 'ebit_margin', 'ebitda_margin', 'net_margin',
                'roea_ttm', 'roaa_ttm', 'nim_q', 'nii_to_toi', 'cost_income_ratio', 'car_ratio',
                'revenue_growth', 'profit_growth', 'asset_growth', 'equity_growth'
            ],
            'financial_ratio': [
                'pe_ratio', 'pb_ratio', 'ev_ebitda_ratio', 'rsi_14', 'macd', 'bb_upper', 'bb_lower'
            ],
            'financial_decimal': [
                'rsi_14', 'macd_signal', 'macd_histogram', 'bb_middle'
            ]
        }
        
        self.date_columns = [
            'date', 'report_date', 'trading_date', 'created_at', 'updated_at'
        ]
    
    def format_dataframe_for_display(self, df: pd.DataFrame, 
                                   exclude_columns: List[str] = None) -> pd.DataFrame:
        """
        Format a DataFrame for display using the configuration.
        
        Args:
            df: DataFrame to format
            exclude_columns: Columns to exclude from formatting
        
        Returns:
            Formatted DataFrame
        """
        if df.empty:
            return df
        
        formatted_df = df.copy()
        exclude_columns = exclude_columns or []
        
        # Format each column based on its type
        for col in formatted_df.columns:
            if col in exclude_columns:
                continue
                
            # Determine format type
            format_type = self._get_column_format_type(col)
            
            if format_type:
                formatted_df[col] = formatted_df[col].apply(
                    lambda x: format_value(x, format_type) if pd.notna(x) else "N/A"
                )
            elif col in self.date_columns:
                # Format date columns
                formatted_df[col] = formatted_df[col].apply(
                    lambda x: self._format_date_column(x) if pd.notna(x) else "N/A"
                )
        
        return formatted_df
    
    def _get_column_format_type(self, column_name: str) -> str:
        """Get the format type for a column based on its name."""
        for format_type, columns in self.column_formats.items():
            if column_name in columns:
                return format_type.replace('financial_', '')
        return None
    
    def _format_date_column(self, date_value) -> str:
        """Format date column values."""
        if pd.isna(date_value):
            return "N/A"
        
        if isinstance(date_value, str):
            try:
                date_value = pd.to_datetime(date_value)
            except:
                return str(date_value)
        
        return date_value.strftime('%Y/%m/%d')
    
    def format_metrics_for_display(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Format metrics dictionary for display."""
        formatted_metrics = {}
        
        for key, value in metrics.items():
            if pd.isna(value) or value is None:
                formatted_metrics[key] = "N/A"
                continue
            
            # Determine format type based on key
            format_type = self._get_column_format_type(key)
            
            if format_type:
                formatted_metrics[key] = format_value(value, format_type)
            elif 'date' in key.lower():
                formatted_metrics[key] = self._format_date_column(value)
            else:
                formatted_metrics[key] = str(value)
        
        return formatted_metrics
    
    def get_chart_tooltip_config(self, data: pd.DataFrame, 
                                value_column: str, 
                                format_type: str = None) -> Dict[str, Any]:
        """Get tooltip configuration for charts."""
        if format_type is None:
            format_type = self._get_column_format_type(value_column) or 'decimal'
        
        # Format values for tooltip
        formatted_values = data[value_column].apply(
            lambda x: format_value(x, format_type) if pd.notna(x) else "N/A"
        )
        
        return {
            'hovertemplate': f"<b>{value_column.replace('_', ' ').title()}</b><br>" +
                           "Date: %{x}<br>" +
                           "Value: %{customdata}<br>" +
                           "<extra></extra>",
            'customdata': formatted_values
        }
    
    def get_table_display_config(self, table_type: str = 'default') -> Dict[str, Any]:
        """Get display configuration for different table types."""
        configs = {
            'financial_summary': {
                'height': 400,
                'width': 'stretch',
                'column_config': {
                    'report_date': st.column_config.DateColumn(
                        "Report Date",
                        help="Financial report date",
                        format="YYYY/MM/DD"
                    )
                }
            },
            'valuation': {
                'height': 500,
                'width': 'stretch',
                'column_config': {
                    'date': st.column_config.DateColumn(
                        "Date",
                        help="Trading date",
                        format="YYYY/MM/DD"
                    )
                }
            },
            'technical': {
                'height': 300,
                'width': 'stretch',
                'column_config': {
                    'date': st.column_config.DateColumn(
                        "Date",
                        help="Trading date",
                        format="YYYY/MM/DD"
                    )
                }
            },
            'default': {
                'height': 400,
                'width': 'stretch'
            }
        }
        
        return configs.get(table_type, configs['default'])

# Global instance
display_config_manager = DisplayConfigManager()

# Convenience functions
def format_df_for_display(df: pd.DataFrame, exclude_columns: List[str] = None) -> pd.DataFrame:
    """Quick format DataFrame for display."""
    return display_config_manager.format_dataframe_for_display(df, exclude_columns)

def format_metrics_for_display(metrics: Dict[str, Any]) -> Dict[str, str]:
    """Quick format metrics for display."""
    return display_config_manager.format_metrics_for_display(metrics)

def get_chart_tooltip_config(data: pd.DataFrame, value_column: str, format_type: str = None) -> Dict[str, Any]:
    """Quick get chart tooltip configuration."""
    return display_config_manager.get_chart_tooltip_config(data, value_column, format_type)

def get_table_display_config(table_type: str = 'default') -> Dict[str, Any]:
    """Quick get table display configuration."""
    return display_config_manager.get_table_display_config(table_type)
