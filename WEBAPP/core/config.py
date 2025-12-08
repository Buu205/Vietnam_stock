"""
Configuration module for display formats and settings.
Cấu hình định dạng hiển thị và các thiết lập chung.
"""

from typing import Dict, Any
import locale

# Set Vietnamese locale for number formatting
try:
    locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        pass

class DisplayConfig:
    """Configuration for data display formatting."""
    
    # Date formats
    DATE_FORMATS = {
        'display': '%Y/%m/%d',  # YYYY/MM/DD for display
        'storage': '%Y-%m-%d',  # YYYY-MM-DD for storage
        'axis': '%m/%Y',        # MM/YYYY for chart axes
        'tooltip': '%d/%m/%Y'   # DD/MM/YYYY for tooltips
    }
    
    # Number formatting
    NUMBER_FORMATS = {
        'currency': {
            'symbol': 'VND',
            'decimal_places': 0,
            'thousands_separator': ',',
            'decimal_separator': '.',
            'suffix': ''  # Remove VND suffix
        },
        'percentage': {
            'decimal_places': 1,
            'suffix': '%',
            'multiply': False  # Don't multiply by 100 for display (data already in %)
        },
        'decimal': {
            'decimal_places': 1,
            'thousands_separator': ',',
            'decimal_separator': '.'
        },
        'integer': {
            'decimal_places': 0,
            'thousands_separator': ','
        },
        'ratio': {
            'decimal_places': 2,
            'suffix': '×'
        }
    }
    
    # Chart formatting
    CHART_CONFIG = {
        'colors': {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#8c564b',
            'dark': '#e377c2'
        },
        'font_sizes': {
            'title': 16,
            'subtitle': 14,
            'axis_label': 12,
            'tick': 10,
            'annotation': 10
        },
        'margins': {
            'l': 60,
            'r': 60,
            't': 100,
            'b': 60
        }
    }
    
    # Data validation rules
    VALIDATION_RULES = {
        'outliers': {
            'pe_max': 100,
            'pb_max': 10,
            'ev_ebitda_max': 100,
            'rsi_min': 0,
            'rsi_max': 100
        },
        'ranges': {
            'pe_reasonable': (5, 50),
            'pb_reasonable': (0.5, 5),
            'ev_ebitda_reasonable': (5, 30)
        }
    }

def format_currency(value: float, config: Dict[str, Any] = None) -> str:
    """Format currency values with proper separators."""
    if config is None:
        config = DisplayConfig.NUMBER_FORMATS['currency']
    
    if pd.isna(value) or value is None:
        return "N/A"
    
    # Format with thousands separator
    formatted = f"{value:,.{config['decimal_places']}f}"
    
    # Replace decimal separator if needed
    if config['decimal_separator'] != '.':
        formatted = formatted.replace('.', config['decimal_separator'])
    
    return f"{formatted}{config['suffix']}"

def format_percentage(value: float, config: Dict[str, Any] = None) -> str:
    """Format percentage values."""
    if config is None:
        config = DisplayConfig.NUMBER_FORMATS['percentage']
    
    if pd.isna(value) or value is None:
        return "N/A"
    
    # Multiply by 100 if needed
    if config.get('multiply', False):
        value = value * 100
    
    formatted = f"{value:.{config['decimal_places']}f}"
    return f"{formatted}{config['suffix']}"

def format_ratio(value: float, config: Dict[str, Any] = None) -> str:
    """Format ratio values (PE, PB, EV/EBITDA)."""
    if config is None:
        config = DisplayConfig.NUMBER_FORMATS['ratio']
    
    if pd.isna(value) or value is None:
        return "N/A"
    
    formatted = f"{value:.{config['decimal_places']}f}"
    return f"{formatted}{config['suffix']}"

def format_decimal(value: float, config: Dict[str, Any] = None) -> str:
    """Format decimal numbers with proper separators."""
    if config is None:
        config = DisplayConfig.NUMBER_FORMATS['decimal']
    
    if pd.isna(value) or value is None:
        return "N/A"
    
    formatted = f"{value:,.{config['decimal_places']}f}"
    
    # Replace separators if needed
    if config['thousands_separator'] != ',':
        formatted = formatted.replace(',', config['thousands_separator'])
    if config['decimal_separator'] != '.':
        formatted = formatted.replace('.', config['decimal_separator'])
    
    return formatted

def format_date(date_value, format_type: str = 'display') -> str:
    """Format date values according to specified format type."""
    if pd.isna(date_value) or date_value is None:
        return "N/A"
    
    if isinstance(date_value, str):
        try:
            date_value = pd.to_datetime(date_value)
        except:
            return str(date_value)
    
    format_str = DisplayConfig.DATE_FORMATS.get(format_type, '%Y/%m/%d')
    return date_value.strftime(format_str)

# Import pandas for type checking
import pandas as pd
