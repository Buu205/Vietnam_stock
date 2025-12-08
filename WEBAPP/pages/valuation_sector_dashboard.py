"""
Valuation Sector Dashboard

VN: Trang phân tích định giá sector theo PE với thống kê và so sánh
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from streamlit_app.core.utils import get_data_path, load_custom_css
from streamlit_app.layout.navigation import render_top_nav

# Load custom CSS
load_custom_css()

# Defaults for data loading / caching
LATEST_COLUMNS = [
    'date', 'sector', 'sector_pe', 'pe_min', 'pe_max', 'pe_median',
    'pe_mean', 'pe_std', 'pe_q25', 'pe_q75', 'pe_percentile',
    'observation_days'
]
HISTORICAL_COLUMNS = ['date', 'sector', 'sector_pe']
MAX_HISTORY_YEARS = 3
SESSION_PAYLOAD_KEY = "sector_pe_payload"

# Page config
st.set_page_config(
    page_title="Valuation Sector Analysis",
    page_icon="📊",
    layout="wide"
)

# Plotly config
PLOTLY_CONFIG = {
    "displayModeBar": True,
    "staticPlot": False,
    "responsive": True,
    "autosizable": True
}


@st.cache_data(ttl=900)
def load_sector_pe_data(
    latest_columns: list[str] | None = None,
    historical_columns: list[str] | None = None,
    max_years: int = MAX_HISTORY_YEARS,
):
    """Load sector PE data with column selection + history window"""
    data_dir = get_data_path("calculated_results/valuation/sector_pe")
    
    latest_cols = latest_columns or LATEST_COLUMNS
    hist_cols = historical_columns or HISTORICAL_COLUMNS

    latest_path = data_dir / "sector_pe_latest.parquet"
    historical_path = data_dir / "sector_pe_historical.parquet"

    latest_df = (
        pd.read_parquet(latest_path, columns=latest_cols)
        if latest_path.exists()
        else pd.DataFrame(columns=latest_cols)
    )
    historical_df = (
        pd.read_parquet(historical_path, columns=hist_cols)
        if historical_path.exists()
        else pd.DataFrame(columns=hist_cols)
    )

    if not latest_df.empty:
        latest_df['date'] = pd.to_datetime(latest_df['date'], utc=True).dt.tz_localize(None)
    if not historical_df.empty:
        historical_df['date'] = pd.to_datetime(historical_df['date'], utc=True).dt.tz_localize(None)
        if max_years:
            now_utc = pd.Timestamp.utcnow()
            if now_utc.tzinfo is not None:
                now_naive = now_utc.tz_convert(None)
            else:
                now_naive = now_utc.tz_localize(None)
            cutoff = now_naive.normalize() - pd.DateOffset(years=max_years)
            historical_df = historical_df[historical_df['date'] >= cutoff]
    
    return latest_df, historical_df


def get_sector_pe_payload():
    """Load data once per session to avoid re-reading parquet files."""
    if SESSION_PAYLOAD_KEY not in st.session_state:
        latest_df, historical_df = load_sector_pe_data()
        st.session_state[SESSION_PAYLOAD_KEY] = {
            "latest": latest_df,
            "historical": historical_df,
        }
    return st.session_state[SESSION_PAYLOAD_KEY]


@st.cache_data(ttl=300)
def filter_sector_data(latest_df: pd.DataFrame, historical_df: pd.DataFrame, sectors_key: tuple[str, ...]):
    """Filter cached datasets for the selected sectors."""
    if not sectors_key:
        return latest_df.iloc[0:0].copy(), historical_df.iloc[0:0].copy()
    selected = list(sectors_key)
    filtered_latest = latest_df[latest_df['sector'].isin(selected)].copy()
    filtered_historical = historical_df[historical_df['sector'].isin(selected)].copy()
    return filtered_latest, filtered_historical


def format_number(num, suffix=''):
    """Format number with appropriate suffix"""
    if pd.isna(num):
        return '-'
    if abs(num) >= 1e9:
        return f"{num/1e9:.2f}B{suffix}"
    elif abs(num) >= 1e6:
        return f"{num/1e6:.2f}M{suffix}"
    else:
        return f"{num:.2f}{suffix}"


def main():
    # Render Top Navigation
    render_top_nav()
    
    
    # Load data (preload once per session)
    with st.spinner("Đang tải dữ liệu..."):
        payload = get_sector_pe_payload()
        latest_df = payload["latest"]
        historical_df = payload["historical"]
    
    if latest_df.empty:
        st.error("Không tìm thấy dữ liệu valuation sector. Vui lòng chạy script tính toán trước.")
        return
    
    # Sidebar filters
    st.sidebar.header("🔧 Filters")
    
    # Date info
    latest_date = latest_df['date'].max()
    st.sidebar.markdown(f"**📅 Latest Update:** {latest_date.strftime('%Y-%m-%d')}")
    
    # Sector filter - show all by default
    sectors = sorted(latest_df['sector'].unique().tolist())
    selected_sectors = st.sidebar.multiselect(
        "Select Sectors",
        sectors,
        default=sectors  # Default: ALL sectors
    )
    
    if not selected_sectors:
        st.warning("Vui lòng chọn ít nhất một sector")
        return
    
    sectors_key = tuple(sorted(selected_sectors))
    filtered_latest, filtered_historical = filter_sector_data(
        latest_df, historical_df, sectors_key
    )
    
    # Main content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Sectors",
            len(filtered_latest),
            help="Số lượng sectors được chọn"
        )
    
    with col2:
        avg_pe = filtered_latest['sector_pe'].mean()
        st.metric(
            "Average PE",
            f"{avg_pe:.2f}",
            help="PE trung bình của các sectors được chọn"
        )
    
    with col3:
        date_range = (filtered_historical['date'].max() - filtered_historical['date'].min()).days if not filtered_historical.empty else 0
        st.metric(
            "Observation Period",
            f"{date_range} days",
            help="Số ngày quan sát"
        )
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Overview", 
        "📊 PE Comparison", 
        "📉 Historical Trends",
        "📋 Detailed Statistics"
    ])
    
    with tab1:
        render_overview_tab(filtered_latest, filtered_historical)
    
    with tab2:
        render_comparison_tab(filtered_latest)
    
    with tab3:
        render_trends_tab(filtered_historical)
    
    with tab4:
        render_statistics_tab(filtered_latest)


def render_overview_tab(latest_df, historical_df):
    """Render overview tab"""
    st.subheader("📈 PE Overview")
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    with col1:
        # Current PE bar chart
        sorted_df = latest_df.sort_values('sector_pe')
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=sorted_df['sector_pe'],
            y=sorted_df['sector'],
            orientation='h',
            marker=dict(
                color=sorted_df['sector_pe'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="PE")
            ),
            text=[f"{pe:.2f}" for pe in sorted_df['sector_pe']],
            textposition='auto',
            name='Current PE'
        ))
        
        fig.update_layout(
            title="Current PE by Sector",
            xaxis_title="PE Ratio",
            yaxis_title="Sector",
            height=500,
            showlegend=False,
            font=dict(size=10)
        )
        
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    
    with col2:
        # PE vs Percentile scatter
        fig = go.Figure()
        
        # Add percentile reference lines
        for percentile in [25, 50, 75, 90]:
            fig.add_hline(
                y=percentile,
                line_dash="dash",
                line_color="gray",
                opacity=0.3,
                annotation_text=f"{percentile}th percentile"
            )
        
        # Simple, clean scatter plot with larger markers
        fig.add_trace(go.Scatter(
            x=latest_df['sector_pe'],
            y=latest_df['pe_percentile'],
            mode='markers',
            marker=dict(
                size=18,
                color=latest_df['sector_pe'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="PE", len=0.6),
                line=dict(width=2, color='white'),
                opacity=0.8
            ),
            name='Sector',
            text=latest_df['sector'],
            hovertemplate='<b>%{text}</b><br>PE: %{x:.2f}<br>Percentile: %{y:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title="PE vs Percentile Rank",
            xaxis_title="Current PE",
            yaxis_title="Percentile (%)",
            height=550,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    
    st.markdown("#### 📊 PE Comparison Table")
    simple_df = latest_df[[
        'sector', 'sector_pe', 'pe_min', 'pe_max', 'pe_median'
    ]].copy()
    
    simple_df.columns = [
        'Sector', 'Current PE', 'Min PE', 'Max PE', 'Median PE'
    ]
    
    simple_df['vs Median'] = simple_df['Current PE'] - simple_df['Median PE']
    simple_df['vs Median (%)'] = (
        (simple_df['Current PE'] - simple_df['Median PE']) / simple_df['Median PE'] * 100
    ).round(1)
    
    simple_df = simple_df.sort_values('Current PE', ascending=False).round(2)
    
    st.dataframe(
        simple_df,
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("#### 📋 Detailed Summary Table")
    summary_df = latest_df[[
        'sector', 'sector_pe', 'pe_min', 'pe_max', 'pe_median',
        'pe_mean', 'pe_std', 'pe_percentile'
    ]].copy()
    
    summary_df.columns = [
        'Sector', 'Current PE', 'Min', 'Max', 'Median', 'Mean', 'Std Dev', 'Percentile'
    ]
    
    summary_df = summary_df.sort_values('Current PE', ascending=False).round(2)
    
    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True
    )


def render_comparison_tab(latest_df):
    """Render comparison tab"""
    st.subheader("📊 PE Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### PE Range: Min vs Current vs Max")
        fig = go.Figure()
        for sector in latest_df['sector']:
            row = latest_df[latest_df['sector'] == sector].iloc[0]
            fig.add_trace(go.Scatter(
                x=[sector, sector, sector],
                y=[row['pe_min'], row['sector_pe'], row['pe_max']],
                mode='lines+markers',
                name=sector,
                line=dict(width=2),
                marker=dict(size=10)
            ))
        fig.update_layout(
            title="PE Range: Min, Current, Max",
            xaxis_title="Sector",
            yaxis_title="PE Ratio",
            height=500,
            xaxis_tickangle=-45,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    
    with col2:
        st.markdown("#### PE Distribution (Box + Current)")
        fig = go.Figure()
        for _, row in latest_df.iterrows():
            fig.add_trace(go.Box(
                y=[row['pe_q25'], row['pe_median'], row['pe_q75'], row['pe_min'], row['pe_max']],
                name=row['sector'],
                boxmean='sd'
            ))
        fig.add_trace(go.Scatter(
            x=list(range(len(latest_df))),
            y=latest_df['sector_pe'],
            mode='markers',
            marker=dict(size=12, color='red', symbol='diamond'),
            name='Current PE'
        ))
        fig.update_layout(
            title="PE Distribution with Current Value",
            xaxis_title="Sector",
            yaxis_title="PE Ratio",
            height=500,
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(len(latest_df))),
                ticktext=latest_df['sector'],
                tickangle=-45
            ),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    
    st.markdown("#### 📊 Volatility Analysis Table")
    volatility_df = latest_df[[
        'sector', 'sector_pe', 'pe_std', 'pe_min', 'pe_max'
    ]].copy()
    volatility_df['Range'] = volatility_df['pe_max'] - volatility_df['pe_min']
    volatility_df['Coeff_Var'] = (volatility_df['pe_std'] / volatility_df['sector_pe'] * 100).round(2)
    volatility_df.columns = [
        'Sector', 'Current PE', 'Std Dev', 'Min', 'Max', 'Range', 'Coeff of Var (%)'
    ]
    volatility_df = volatility_df.sort_values('Coeff of Var (%)', ascending=False)
    st.dataframe(
        volatility_df,
        use_container_width=True,
        hide_index=True
    )


def render_trends_tab(historical_df):
    """Render historical trends tab"""
    st.subheader("📉 Historical Trends")
    
    if historical_df.empty:
        st.warning("Không có dữ liệu lịch sử")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### PE Trends for Selected Sectors")
        fig = go.Figure()
        sectors = historical_df['sector'].unique()
        colors = px.colors.qualitative.Set3
        for i, sector in enumerate(sectors):
            sector_data = historical_df[historical_df['sector'] == sector].sort_values('date')
            fig.add_trace(go.Scatter(
                x=sector_data['date'],
                y=sector_data['sector_pe'],
                mode='lines',
                name=sector,
                line=dict(color=colors[i % len(colors)], width=2)
            ))
        fig.update_layout(
            title="PE Trends Over Time",
            xaxis_title="Date",
            yaxis_title="PE Ratio",
            height=500,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    
    with col2:
        st.markdown("#### Single Sector Snapshot")
        selected_sector = st.selectbox(
            "Select Sector for Detail",
            sectors
        )
        if selected_sector:
            sector_data = historical_df[historical_df['sector'] == selected_sector].sort_values('date')
            st.metric("Current PE", f"{sector_data['sector_pe'].iloc[-1]:.2f}")
            st.metric("Min PE", f"{sector_data['sector_pe'].min():.2f}")
            st.metric("Max PE", f"{sector_data['sector_pe'].max():.2f}")
            st.metric("Average PE", f"{sector_data['sector_pe'].mean():.2f}")


def render_statistics_tab(latest_df):
    """Render detailed statistics tab"""
    st.subheader("📋 Detailed Statistics")
    
    st.markdown("#### Full Statistics Table")
    stats_df = latest_df[[
        'sector', 'sector_pe', 'pe_min', 'pe_max', 'pe_median', 
        'pe_mean', 'pe_std', 'pe_q25', 'pe_q75', 
        'pe_percentile', 'observation_days'
    ]].copy()
    stats_df.columns = [
        'Sector', 'Current PE', 'Min', 'Max', 'Median', 
        'Mean', 'Std Dev', 'Q25', 'Q75', 
        'Percentile (%)', 'Obs Days'
    ]
    stats_df = stats_df.sort_values('Current PE', ascending=False).round(2)
    st.dataframe(
        stats_df,
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("#### 💡 Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🔴 Sectors at High Valuation:**")
        high_pct = latest_df[latest_df['pe_percentile'] > 90].sort_values('pe_percentile', ascending=False)
        if not high_pct.empty:
            for _, row in high_pct.iterrows():
                st.write(f"- **{row['sector']}**: PE {row['sector_pe']:.2f} (Percentile: {row['pe_percentile']:.1f}%)")
        else:
            st.write("None")
    with col2:
        st.markdown("**🟢 Sectors at Low Valuation:**")
        low_pct = latest_df[latest_df['pe_percentile'] < 20].sort_values('pe_percentile')
        if not low_pct.empty:
            for _, row in low_pct.iterrows():
                st.write(f"- **{row['sector']}**: PE {row['sector_pe']:.2f} (Percentile: {row['pe_percentile']:.1f}%)")
        else:
            st.write("None")


if __name__ == "__main__":
    main()
