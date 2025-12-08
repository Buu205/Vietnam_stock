"""Valuation charts (bilingual / song ngữ)

Build PE/PB/EVEBITDA line charts with percentile bands.

VN: Vẽ biểu đồ đường cho PE/PB/EVEBITDA kèm các đường phân vị (Q1/Median/Q3).
"""

from __future__ import annotations
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict
from streamlit_app.core.constants import COLORS


def build_val_trends_subplots(pe_df: pd.DataFrame | None,
                              pb_df: pd.DataFrame | None,
                              ev_df: pd.DataFrame | None) -> go.Figure:
    """Return a 3-row subplot figure for PE, PB, EV/EBITDA.

    VN: Trả về figure 3 hàng cho PE, PB, EV/EBITDA. DataFrames đã được lọc outliers từ loader.
    """
    fig = make_subplots(rows=3, cols=1, subplot_titles=("P/E", "P/B", "EV/EBITDA"), vertical_spacing=0.12)

    if pe_df is not None and not pe_df.empty:
        fig.add_trace(go.Scatter(x=pe_df['date'], y=pe_df['pe_ratio'], mode='lines',
                                 line=dict(color=COLORS['pe'], width=2, shape='spline', smoothing=0.3),
                                 name='P/E'), row=1, col=1)

    if pb_df is not None and not pb_df.empty:
        fig.add_trace(go.Scatter(x=pb_df['date'], y=pb_df['pb_ratio'], mode='lines',
                                 line=dict(color=COLORS['pb'], width=2, shape='spline', smoothing=0.3),
                                 name='P/B'), row=2, col=1)

    if ev_df is not None and not ev_df.empty:
        fig.add_trace(go.Scatter(x=ev_df['date'], y=ev_df['ev_ebitda_ratio'], mode='lines',
                                 line=dict(color=COLORS['ev_ebitda'], width=2, shape='spline', smoothing=0.3),
                                 name='EV/EBITDA'), row=3, col=1)

    fig.update_layout(height=900, showlegend=False, margin=dict(l=60, r=60, t=40, b=60))
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="P/E", row=1, col=1)
    fig.update_yaxes(title_text="P/B", row=2, col=1)
    fig.update_yaxes(title_text="EV/EBITDA", row=3, col=1)
    return fig


