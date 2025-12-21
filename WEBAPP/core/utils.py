"""Shared utilities for Streamlit dashboards."""

from __future__ import annotations
from typing import Iterable
import pandas as pd
from pathlib import Path
import os
import streamlit as st


def ensure_datetime(series: pd.Series) -> pd.Series:
    """Convert a Series to pandas datetime (errors='coerce')."""
    return pd.to_datetime(series, errors='coerce')


def percentile_rank(series: pd.Series, value: float) -> float:
    """Return percentile rank (0..100) of `value` within `series`.

    NaNs are ignored. If series empty or value is NaN, returns NaN.
    """
    s = series.dropna()
    if len(s) == 0 or pd.isna(value):
        return float('nan')
    return float(((s <= value).mean()) * 100.0)


def clip_outliers(df: pd.DataFrame, column: str, max_value: float) -> pd.DataFrame:
    """Filter out rows where df[column] > max_value. Returns a copy."""
    if column not in df.columns:
        return df.copy()
    m = df[column] <= max_value
    return df.loc[m].copy()


def get_data_path(relative_path: str = "") -> Path:
    """Get the full path for a file/directory relative to project root.
    
    Args:
        relative_path: Optional relative path from project root
        
    Returns:
        Full Path object
    """
    # Try to find the project root
    current = Path(__file__).resolve()
    # Go up from streamlit_app/core/utils.py to project root
    project_root = current.parent.parent.parent
    
    if relative_path:
        return project_root / relative_path
    return project_root


def load_custom_css():
    """DEPRECATED: Custom CSS is now handled by core/styles.py.

    This function is kept for backward compatibility but does nothing.
    Use get_page_style() from WEBAPP.core.styles instead.
    """
    # No-op - styling is now centralized in styles.py
    pass


def get_plotly_font_config():
    """Get Plotly font configuration for Inter font (dark theme).

    Returns:
        dict: Font configuration to be used in fig.update_layout()

    Usage:
        fig.update_layout(**get_plotly_font_config())
    """
    return {
        'font': {
            'family': 'JetBrains Mono, monospace',
            'size': 11,
            'color': '#CBD5E1'
        },
        'title_font': {
            'family': 'Inter, sans-serif',
            'size': 15,
            'color': '#CBD5E1'
        },
        'hoverlabel': {
            'font': {
                'family': 'JetBrains Mono, monospace',
                'size': 12,
                'color': '#F0F4F8'
            },
            'bgcolor': '#101820',
            'bordercolor': '#009B87'
        },
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)'
    }


def get_pyecharts_font_config():
    """Get PyEcharts text style configuration for Inter font.

    Returns:
        dict: Text style configuration for PyEcharts charts

    Usage:
        textstyle_opts = opts.TextStyleOpts(**get_pyecharts_font_config())
    """
    return {
        'font_family': 'Inter, sans-serif',
        'font_size': 12
    }


def get_pyecharts_global_opts_with_font(title=None, xaxis_name=None, yaxis_name=None, 
                                        show_legend=True, **kwargs):
    """Get PyEcharts global opts with Nunito font pre-configured.
    
    Args:
        title: Chart title
        xaxis_name: X-axis label
        yaxis_name: Y-axis label  
        show_legend: Show/hide legend
        **kwargs: Additional opts to override
    
    Returns:
        dict: Complete global opts with Nunito font
    
    Usage:
        chart.set_global_opts(**get_pyecharts_global_opts_with_font(
            title="My Chart",
            xaxis_name="Quarter",
            yaxis_name="Value"
        ))
    """
    from pyecharts import options as opts
    
    opts_dict = {}
    
    # Title with Nunito font
    if title:
        opts_dict['title_opts'] = opts.TitleOpts(
            title=title,
            pos_left="center",
            title_textstyle_opts=opts.TextStyleOpts(
                font_family='Nunito, sans-serif',
                font_size=18,
                font_weight='bold',
                color='#295CA9'
            )
        )
    
    # X-axis with Nunito font
    if xaxis_name or 'xaxis_opts' not in kwargs:
        opts_dict['xaxis_opts'] = opts.AxisOpts(
            name=xaxis_name or "",
            axislabel_opts=opts.LabelOpts(
                font_family='Nunito, sans-serif',
                font_size=12
            ),
            name_textstyle_opts=opts.TextStyleOpts(
                font_family='Nunito, sans-serif',
                font_size=13
            )
        )
    
    # Y-axis with Nunito font
    if yaxis_name or 'yaxis_opts' not in kwargs:
        opts_dict['yaxis_opts'] = opts.AxisOpts(
            name=yaxis_name or "",
            axislabel_opts=opts.LabelOpts(
                font_family='Nunito, sans-serif',
                font_size=12
            ),
            name_textstyle_opts=opts.TextStyleOpts(
                font_family='Nunito, sans-serif',
                font_size=13
            )
        )
    
    # Tooltip with Nunito font
    if 'tooltip_opts' not in kwargs:
        opts_dict['tooltip_opts'] = opts.TooltipOpts(
            trigger="axis",
            textstyle_opts=opts.TextStyleOpts(
                font_family='Nunito, sans-serif',
                font_size=13
            )
        )
    
    # Legend with Nunito font
    if 'legend_opts' not in kwargs:
        opts_dict['legend_opts'] = opts.LegendOpts(
            is_show=show_legend,
            pos_bottom="2%",
            pos_left="center",
            textstyle_opts=opts.TextStyleOpts(
                font_family='Nunito, sans-serif',
                font_size=12
            )
        )
    
    # Merge with custom kwargs (kwargs override defaults)
    opts_dict.update(kwargs)
    
    return opts_dict
