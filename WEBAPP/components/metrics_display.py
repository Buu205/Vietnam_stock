"""
Metrics display components with consistent formatting.
Các component hiển thị metrics với định dạng nhất quán.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from core.formatters import format_value, format_summary_data
from core.display_settings import display_settings

def render_valuation_metrics(pe_ratio: float, pb_ratio: float, ev_ebitda_ratio: float, 
                           pe_rank: str, pb_rank: str, ev_ebitda_rank: str,
                           overall_valuation: str) -> None:
    """
    Render valuation metrics in a summary row.
    
    Args:
        pe_ratio: Current P/E ratio
        pb_ratio: Current P/B ratio  
        ev_ebitda_ratio: Current EV/EBITDA ratio
        pe_rank: P/E percentile rank
        pb_rank: P/B percentile rank
        ev_ebitda_rank: EV/EBITDA percentile rank
        overall_valuation: Overall valuation classification
    """
    st.markdown("### 📊 Tóm tắt định giá hiện tại")
    
    # Create columns for metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        display_settings.show_metric_card(
            label="P/E Ratio",
            value=format_value(pe_ratio, 'ratio'),
            delta=pe_rank
        )
    
    with col2:
        display_settings.show_metric_card(
            label="P/B Ratio", 
            value=format_value(pb_ratio, 'ratio'),
            delta=pb_rank
        )
    
    with col3:
        display_settings.show_metric_card(
            label="EV/EBITDA",
            value=format_value(ev_ebitda_ratio, 'ratio'),
            delta=ev_ebitda_rank
        )
    
    with col4:
        # Color coding for overall valuation
        color_map = {
            'Cheap': 'inverse',
            'Below Avg': 'normal', 
            'Above Avg': 'normal',
            'Expensive': 'off'
        }
        delta_color = color_map.get(overall_valuation, 'normal')
        
        display_settings.show_metric_card(
            label="Overall Valuation",
            value=overall_valuation,
            delta_color=delta_color
        )
    
    with col5:
        st.markdown("**Percentile vs 5-year history**")
        st.markdown("*Outliers removed: P/E>100, P/B>10, EV/EBITDA>100*")

def render_financial_summary(financial_data: Dict[str, Any]) -> None:
    """
    Render financial summary with proper formatting.
    
    Args:
        financial_data: Dictionary containing financial metrics
    """
    if not financial_data:
        st.warning("Không có dữ liệu tài chính")
        return
    
    # Format the data
    formatted_data = format_summary_data(financial_data)
    
    st.markdown("### 💰 Tóm tắt tài chính")
    
    # Group metrics by category
    revenue_metrics = {k: v for k, v in formatted_data.items() 
                      if any(term in k.lower() for term in ['revenue', 'doanh thu'])}
    
    profit_metrics = {k: v for k, v in formatted_data.items() 
                     if any(term in k.lower() for term in ['profit', 'lợi nhuận', 'net income'])}
    
    margin_metrics = {k: v for k, v in formatted_data.items() 
                     if any(term in k.lower() for term in ['margin', 'biên'])}
    
    # Display in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Doanh thu**")
        for key, value in revenue_metrics.items():
            st.markdown(f"- {key}: {value}")
    
    with col2:
        st.markdown("**Lợi nhuận**")
        for key, value in profit_metrics.items():
            st.markdown(f"- {key}: {value}")
    
    with col3:
        st.markdown("**Biên lợi nhuận**")
        for key, value in margin_metrics.items():
            st.markdown(f"- {key}: {value}")

def render_data_table(df: pd.DataFrame, title: str = "", 
                     value_columns: List[str] = None,
                     value_types: Dict[str, str] = None) -> None:
    """
    Render a data table with proper formatting.
    
    Args:
        df: DataFrame to display
        title: Table title
        value_columns: List of columns to format as values
        value_types: Dictionary mapping columns to format types
    """
    if df.empty:
        st.warning("Không có dữ liệu để hiển thị")
        return
    
    if title:
        st.markdown(f"### {title}")
    
    # Format value columns if specified
    if value_columns and value_types:
        df_display = df.copy()
        for col in value_columns:
            if col in df_display.columns and col in value_types:
                df_display[col] = df_display[col].apply(
                    lambda x: format_value(x, value_types[col]) if pd.notna(x) else "N/A"
                )
    else:
        df_display = df
    
    # Display the table
    st.dataframe(
        df_display,
        height=400
    )

def render_percentile_annotations(percentiles: Dict[str, float], 
                                chart_height: int = 500) -> Dict[str, Any]:
    """
    Create percentile annotations for charts.
    
    Args:
        percentiles: Dictionary with percentile values
        chart_height: Height of the chart for positioning
    
    Returns:
        Dictionary with annotation configuration
    """
    annotations = []
    
    # Position annotations on the right side
    x_pos = 0.95
    y_spacing = 0.15
    start_y = 0.85
    
    for i, (label, value) in enumerate(percentiles.items()):
        if pd.notna(value):
            y_pos = start_y - (i * y_spacing)
            
            annotation = {
                'x': x_pos,
                'y': y_pos,
                'xref': 'paper',
                'yref': 'paper',
                'text': f"<b>{label} = {format_value(value, 'ratio')}</b>",
                'showarrow': False,
                'font': {
                    'size': 10,
                    'color': '#666666'
                },
                'bgcolor': 'rgba(255,255,255,0.8)',
                'bordercolor': '#cccccc',
                'borderwidth': 1,
                'borderpad': 4,
                'xanchor': 'right',
                'yanchor': 'middle'
            }
            annotations.append(annotation)
    
    return annotations
