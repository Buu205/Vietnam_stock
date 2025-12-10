"""
Data formatting utilities for consistent display across the application.
Tiện ích định dạng dữ liệu để hiển thị nhất quán trong ứng dụng.
"""

import pandas as pd
import streamlit as st
from typing import Any, Dict, List, Optional, Union
from .config import DisplayConfig, format_currency, format_percentage, format_ratio, format_decimal, format_date
from config.schema_registry import SchemaRegistry

class DataFormatter:
    """
    Centralized data formatting class.
    Lớp định dạng dữ liệu tập trung.
    """
    
    def __init__(self):
        self.config = DisplayConfig()
    
    def format_financial_value(self, value: float, value_type: str = 'currency') -> str:
        """
        Format financial values based on type.
        
        Args:
            value: The value to format
            value_type: Type of value ('currency', 'percentage', 'ratio', 'decimal')
        
        Returns:
            Formatted string
        """
        if pd.isna(value) or value is None:
            return "N/A"
        
        if value_type == 'currency':
            return format_currency(value)
        elif value_type == 'percentage':
            return format_percentage(value)
        elif value_type == 'ratio':
            return format_ratio(value)
        elif value_type == 'decimal':
            return format_decimal(value)
        else:
            return str(value)
    
    def format_dataframe_column(self, df: pd.DataFrame, column: str, value_type: str = 'currency') -> pd.DataFrame:
        """
        Format a specific column in a DataFrame.
        
        Args:
            df: DataFrame to format
            column: Column name to format
            value_type: Type of formatting to apply
        
        Returns:
            DataFrame with formatted column
        """
        if column not in df.columns:
            return df
        
        df_copy = df.copy()
        df_copy[column] = df_copy[column].apply(
            lambda x: self.format_financial_value(x, value_type)
        )
        return df_copy
    
    def format_valuation_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Format valuation data (PE, PB, EV/EBITDA) for display.
        
        Args:
            df: DataFrame containing valuation data
        
        Returns:
            Formatted DataFrame
        """
        df_copy = df.copy()
        
        # Format ratio columns
        ratio_columns = ['pe_ratio', 'pb_ratio', 'ev_ebitda_ratio']
        for col in ratio_columns:
            if col in df_copy.columns:
                df_copy[col] = df_copy[col].apply(
                    lambda x: format_ratio(x) if pd.notna(x) else "N/A"
                )
        
        # Format date columns
        date_columns = ['date', 'report_date', 'trading_date']
        for col in date_columns:
            if col in df_copy.columns:
                df_copy[col] = df_copy[col].apply(
                    lambda x: format_date(x, 'display') if pd.notna(x) else "N/A"
                )
        
        return df_copy
    
    def format_financial_summary(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Format financial summary data for display.
        
        Args:
            data: Dictionary containing financial metrics
        
        Returns:
            Dictionary with formatted values
        """
        formatted = {}
        
        for key, value in data.items():
            if pd.isna(value) or value is None:
                formatted[key] = "N/A"
                continue
            
            # Determine format type based on key
            if any(term in key.lower() for term in ['revenue', 'profit', 'equity', 'assets', 'liabilities']):
                formatted[key] = format_currency(value)
            elif any(term in key.lower() for term in ['margin', 'growth', 'return', 'ratio']):
                if 'ratio' in key.lower() and not any(term in key.lower() for term in ['margin', 'growth', 'return']):
                    formatted[key] = format_ratio(value)
                else:
                    formatted[key] = format_percentage(value)
            elif 'date' in key.lower():
                formatted[key] = format_date(value, 'display')
            else:
                formatted[key] = format_decimal(value)
        
        return formatted
    
    def create_tooltip_text(self, data: Dict[str, Any], title: str = "") -> str:
        """
        Create tooltip text for charts.
        
        Args:
            data: Dictionary containing data for tooltip
            title: Optional title for tooltip
        
        Returns:
            Formatted tooltip text
        """
        if not data:
            return ""
        
        lines = []
        if title:
            lines.append(f"<b>{title}</b>")
        
        for key, value in data.items():
            if pd.isna(value) or value is None:
                continue
            
            # Format based on key type
            if any(term in key.lower() for term in ['revenue', 'profit', 'equity']):
                formatted_value = format_currency(value)
            elif any(term in key.lower() for term in ['margin', 'growth']):
                formatted_value = format_percentage(value)
            elif any(term in key.lower() for term in ['pe', 'pb', 'ev_ebitda']):
                formatted_value = format_ratio(value)
            elif 'date' in key.lower():
                formatted_value = format_date(value, 'tooltip')
            else:
                formatted_value = format_decimal(value)
            
            lines.append(f"{key}: {formatted_value}")
        
        return "<br>".join(lines)

# Global formatter instance
formatter = DataFormatter()

# Convenience functions for direct use
def format_value(value: float, value_type: str = 'currency') -> str:
    """
    Format a single value based on type.
    Định dạng một giá trị đơn lẻ theo loại.
    
    Args:
        value: Giá trị cần định dạng
        value_type: Loại giá trị ('currency', 'percentage', 'ratio', 'decimal')
    
    Returns:
        Chuỗi đã được định dạng
    """
    return formatter.format_financial_value(value, value_type)

def format_df_column(df: pd.DataFrame, column: str, value_type: str = 'currency') -> pd.DataFrame:
    """
    Format a column in DataFrame.
    Định dạng một cột trong DataFrame.
    
    Args:
        df: DataFrame cần định dạng
        column: Tên cột
        value_type: Loại giá trị
    
    Returns:
        DataFrame đã được định dạng
    """
    """Quick format a DataFrame column."""
    return formatter.format_dataframe_column(df, column, value_type)

def format_valuation_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format valuation DataFrame.
    Định dạng DataFrame định giá.
    
    Args:
        df: DataFrame định giá
    
    Returns:
        DataFrame đã được định dạng
    """
    """Quick format valuation DataFrame."""
    return formatter.format_valuation_data(df)

def format_summary_data(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Format summary data dictionary.
    Định dạng dictionary dữ liệu tóm tắt.
    
    Args:
        data: Dictionary dữ liệu
    
    Returns:
        Dictionary đã được định dạng
    """
    """Quick format summary data."""
    return formatter.format_financial_summary(data)
