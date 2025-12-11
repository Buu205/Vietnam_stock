"""
Technical Dashboard (orchestrator mỏng)

VN: Trang phân tích kỹ thuật sử dụng loaders trong domains/technical.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os
import time
from pathlib import Path
from pyecharts import options as opts
from pyecharts.charts import Line, Bar
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
from streamlit_echarts import st_pyecharts

# Add project root to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ensure Streamlit package namespace is registered (Streamlit Cloud can evict it during reload)
import importlib
streamlit_app = importlib.import_module("streamlit_app")

from WEBAPP.core.utils import get_data_path, load_custom_css, get_plotly_font_config
from WEBAPP.layout.navigation import render_top_nav
from config.schema_registry import SchemaRegistry

# Initialize SchemaRegistry singleton
schema_registry = SchemaRegistry()

# Load custom CSS (Nunito font)
load_custom_css()

# Plotly configuration to avoid deprecation warnings
PLOTLY_CONFIG = {
    "displayModeBar": False,
    "staticPlot": False,
    "responsive": True,
    "autosizable": True,
    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"]
}

# Import formatting utilities
from WEBAPP.core.formatters import formatter, format_value, format_df_column, format_summary_data
from WEBAPP.core.display_config import format_df_for_display, format_metrics_for_display

from WEBAPP.domains.technical.data_loading_technical import (
    get_technical_symbols,
    load_rsi,
    load_ma_screening,
    get_ma_screening_metadata,
)
    get_ma_screening_metadata,
)
from WEBAPP.services.commodity_loader import COMMODITY_DESCRIPTIONS
from WEBAPP.services.macro_commodity_loader import MacroCommodityLoader


@st.cache_data(ttl=3600)
def load_macro_dataset(relative_path: str) -> tuple[pd.DataFrame, str]:
    """Load macro dataset from calculated_results (returns df + resolved path)."""
    path = get_data_path(relative_path)
    path_str = str(path)
    try:
        if not os.path.exists(path_str):
            return pd.DataFrame(), path_str
        df = pd.read_parquet(path_str)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df, path_str
    except Exception:
        return pd.DataFrame(), path_str


def render_ma_screening_table():
    """Render MA screening table with filters
    
    VN: Hiển thị bảng lọc MA với các bộ lọc
    """
    # Load data
    with st.spinner("Đang tải dữ liệu MA screening..."):
        ma_df = load_ma_screening()
    
    # Debug info
    if ma_df.empty:
        from WEBAPP.domains.technical.data_loading_technical import MA_SCREENING_PATH
        st.error(f"⚠️ MA screening data is empty!")
        st.info(f"📁 Path: `{MA_SCREENING_PATH}`")
        st.info(f"📁 Exists: {MA_SCREENING_PATH.exists()}")
        st.warning("Không có dữ liệu MA screening. Vui lòng nhấn nút 'Update MA Screening' để cập nhật dữ liệu.")
        return
    
    # Metadata (ngắn gọn) và cấu hình mặc định
    latest_date = ma_df['date'].max()
    st.caption(f"Dữ liệu mới nhất: {latest_date.strftime('%Y-%m-%d')} | Volume tối thiểu: 200,000")
    
    # Filter chỉ lấy data ngày mới nhất (không hiển thị các ngày cũ)
    ma_df_latest = ma_df[ma_df['date'] == latest_date].copy()
    
    if ma_df_latest.empty:
        st.warning(f"Không có dữ liệu MA screening cho ngày {latest_date.strftime('%Y-%m-%d')}")
        return
    
    # Áp dụng volume mặc định 200K và sắp xếp theo volume
    base_df = ma_df_latest[ma_df_latest['volume'] >= 200_000].copy()
    if base_df.empty:
        st.info("Không có mã nào đạt điều kiện volume ≥ 200,000")
        return
    base_df = base_df.sort_values('volume', ascending=False)
    
    # Chuẩn bị các section và hiển thị dạng lưới 2 cột
    # 1) Cắt xuống MA20 (>0.5%)
    cut_down = base_df[(base_df['close'] < base_df['sma_20']) & (((base_df['close'] - base_df['sma_20']) / base_df['sma_20'] * 100) < -0.5)].copy()
    cut_down['diff_pct'] = (cut_down['close'] - cut_down['sma_20']) / cut_down['sma_20'] * 100
    
    # 2) Cắt lên MA20 (>0.5%)
    cut_up = base_df[(base_df['close'] > base_df['sma_20']) & (((base_df['close'] - base_df['sma_20']) / base_df['sma_20'] * 100) > 0.5)].copy()
    cut_up['diff_pct'] = (cut_up['close'] - cut_up['sma_20']) / cut_up['sma_20'] * 100
    
    # 3) Giá > MA50 và gần MA50 (<2%)
    near_below = base_df[(base_df['close'] > base_df['sma_50']) & ((((base_df['close'] - base_df['sma_50']) / base_df['sma_50'] * 100)) < 2) & ((((base_df['close'] - base_df['sma_50']) / base_df['sma_50'] * 100)) > 0)].copy()
    near_below['diff_pct'] = (near_below['close'] - near_below['sma_50']) / near_below['sma_50'] * 100
    
    # 4) Giá < MA50 và gần MA50 (<2%)
    near_above = base_df[(base_df['close'] < base_df['sma_50']) & ((((base_df['close'] - base_df['sma_50']) / base_df['sma_50'] * 100)) > -2) & ((((base_df['close'] - base_df['sma_50']) / base_df['sma_50'] * 100)) < 0)].copy()
    near_above['diff_pct'] = (near_above['close'] - near_above['sma_50']) / near_above['sma_50'] * 100
    
    # 5) Bullish alignment
    bull = base_df[(base_df['sma_20'] > base_df['sma_50']) & (base_df['sma_50'] > base_df['sma_100']) & (base_df['sma_100'] > base_df['sma_200'])].copy()
    
    # 6) Bearish alignment
    bear = base_df[(base_df['sma_20'] < base_df['sma_50']) & (base_df['sma_50'] < base_df['sma_100']) & (base_df['sma_100'] < base_df['sma_200'])].copy()
    
    sections = [
        ("🔴 CẮT XUỐNG SMA20 (>0.5%)", cut_down, ['symbol', 'close', 'sma_20', 'diff_pct']),
        ("🟢 CẮT LÊN SMA20 (>0.5%)", cut_up, ['symbol', 'close', 'sma_20', 'diff_pct']),
        ("⚠️ SẮP CHẠM XUỐNG SMA50", near_below, ['symbol', 'close', 'sma_50', 'diff_pct']),
        ("📈 SẮP CẮT LÊN SMA50", near_above, ['symbol', 'close', 'sma_50', 'diff_pct']),
        ("🚀 BULLISH ALIGNMENT", bull, ['symbol', 'close', 'sma_20', 'sma_50', 'sma_100', 'sma_200']),
        ("📉 BEARISH ALIGNMENT", bear, ['symbol', 'close', 'sma_20', 'sma_50', 'sma_100', 'sma_200'])
    ]
    
    def _format_display(df):
        df = df.head(10).copy()
        if 'close' in df.columns:
            df['close'] = df['close'].apply(lambda x: f"{x:,.0f}")
        for c in ['sma_20', 'sma_50', 'sma_100', 'sma_200']:
            if c in df.columns:
                df[c] = df[c].apply(lambda x: f"{x:,.0f}")
        if 'diff_pct' in df.columns:
            df['diff_pct'] = df['diff_pct'].apply(lambda x: f"{x:+.2f}%")
        return df
    
    # Render dạng lưới 2 cột
    total = 0
    n_cols = 2
    for i in range(0, len(sections), n_cols):
        cols = st.columns(n_cols)
        for j in range(n_cols):
            idx = i + j
            if idx >= len(sections):
                continue
            title, df_sec, cols_sec = sections[idx]
            if df_sec.empty:
                continue
            with cols[j]:
                st.markdown(f"**{title}**  ")
                show_df = _format_display(df_sec)
                st.dataframe(show_df[cols_sec], hide_index=True)
                total += len(df_sec)
    
    st.success(f"📊 Tổng cộng: {total} mã thuộc các nhóm tín hiệu trên")


def render_market_breadth_chart():
    """Render Market Breadth chart with MA20/MA50/MA100 and historical zones

    VN: Hiển thị biểu đồ Market Breadth với % cổ phiếu > MA20/MA50/MA100 và vùng median
    """
    st.subheader("Market Breadth")

    # Resolve file path tương đối từ project root (không dùng iCloud absolute path)
    local_path = get_data_path("DATA/processed/technical/market_breadth_global.parquet")
    file_exists = local_path.exists()

    if not file_exists:
        st.error(f"⚠️ File không tồn tại tại: `{local_path}`")
        st.info("💡 Vui lòng kiểm tra lại file `DATA/processed/technical/market_breadth_global.parquet` dưới project root.")
        st.info("💡 Bạn cần chạy script tổng hợp dữ liệu market breadth và đảm bảo quyền truy cập file.")
        return

    try:
        import duckdb
        import plotly.graph_objects as go
        import pandas as pd

        conn = duckdb.connect()
        # Đọc dữ liệu từ file market breadth dưới project root
        df_all = conn.execute(
            "SELECT * FROM read_parquet(?)", [str(local_path)]
        ).fetchdf()

        # Nếu cột date chưa chuẩn, cố gắng chuyển đổi
        if "date" in df_all.columns:
            df_all['date'] = pd.to_datetime(df_all['date'])
        else:
            st.error("❌ File thiếu cột 'date'. Vui lòng kiểm tra lại dữ liệu.")
            return

        # Nếu thiếu các field %MA, tính lại nếu chỉ có số mã
        for need_col, num_col in [
            ('pct_ma20', 'above_ma20'), ('pct_ma50', 'above_ma50'), ('pct_ma100', 'above_ma100')
        ]:
            if need_col not in df_all.columns and num_col in df_all.columns and "total_stocks" in df_all.columns:
                df_all[need_col] = df_all[num_col] / df_all['total_stocks'] * 100

        # Đảm bảo các cột pct_ma20, pct_ma50, pct_ma100 có tồn tại để vẽ chart
        missing_pct_cols = [c for c in ['pct_ma20', 'pct_ma50', 'pct_ma100'] if c not in df_all.columns]
        if missing_pct_cols:
            st.error(f"❌ File thiếu các cột {missing_pct_cols}. Vui lòng kiểm tra lại dữ liệu.")
            return

        latest_date = df_all['date'].max()
        total_stocks = int(df_all[df_all['date'] == latest_date]['total_stocks'].values[-1])
        st.caption(f"Dữ liệu mới nhất: {latest_date.strftime('%Y-%m-%d')} | Tổng số mã: {total_stocks}")

        if len(df_all) < 5:
            st.warning(f"⚠️ Chỉ có {len(df_all)} ngày dữ liệu Market Breadth. Cần ít nhất 5 ngày để hiển thị biểu đồ có ý nghĩa.")
            st.info("💡 Dữ liệu Market Breadth sẽ được cập nhật khi có đủ dữ liệu lịch sử.")
            return

        # Calculate historical zones for MA50 (last 2 years)
        max_d = df_all['date'].max()
        window_start_2y = (max_d - pd.Timedelta(days=730)).normalize()
        series50_2y = df_all.loc[df_all['date'] >= window_start_2y, 'pct_ma50'].dropna()

        if not series50_2y.empty:
            median_50 = float(series50_2y.median())
            p20_50 = float(series50_2y.quantile(0.2))  # Bottom zone
            p80_50 = float(series50_2y.quantile(0.8))  # Top zone
        else:
            median_50 = p20_50 = p80_50 = None

        # Fixed YTD display (Year to Date)
        start_display = pd.Timestamp(str(max_d.year) + "-01-01")

        # Filter data for display (YTD only)
        df = df_all[df_all['date'] >= start_display].copy()

        if df.empty:
            st.warning("Không có dữ liệu YTD")
            return

        y20 = [None if pd.isna(v) else round(float(v), 1) for v in df['pct_ma20']]
        y50 = [None if pd.isna(v) else round(float(v), 1) for v in df['pct_ma50']]
        y100 = [None if pd.isna(v) else round(float(v), 1) for v in df['pct_ma100']]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=y20,
            mode='lines',
            name='% > MA20',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='%{y:.1f}%<extra></extra>'
        ))
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=y50,
            mode='lines',
            name='% > MA50',
            line=dict(color='#ff7f0e', width=2),
            hovertemplate='%{y:.1f}%<extra></extra>'
        ))
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=y100,
            mode='lines',
            name='% > MA100',
            line=dict(color='#9467bd', width=2),
            hovertemplate='%{y:.1f}%<extra></extra>'
        ))

        if p20_50 is not None:
            fig.add_hline(
                y=p20_50,
                line_dash="dash",
                line_color="#2E7D32",
                line_width=1.5,
                annotation_text=f"Bottom Zone (P20): {p20_50:.1f}%",
                annotation_position="bottom right"
            )
        if p80_50 is not None:
            fig.add_hline(
                y=p80_50,
                line_dash="dash",
                line_color="#C62828",
                line_width=1.5,
                annotation_text=f"Top Zone (P80): {p80_50:.1f}%",
                annotation_position="top right"
            )

        fig.update_layout(
            **get_plotly_font_config(),
            title="Market Breadth (YTD)",
            xaxis_title="Date",
            yaxis_title="%",
            yaxis=dict(range=[0, 100]),
            height=500,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                rangeslider=dict(visible=True),
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(step="all", label="All")
                    ])
                )
            )
        )

        st.plotly_chart(fig, config=PLOTLY_CONFIG, key="plotly_chart_325")

        # ✅ Hiển thị Market Breadth chart và Trading Value chart cùng hàng (tỷ lệ 3:2)
        col_chart1, col_chart2 = st.columns([3, 2])
        
        with col_chart1:
            st.plotly_chart(fig, config=PLOTLY_CONFIG, use_container_width=True, key="market_breadth_chart")
            
            # Display zone metrics and current values
            if p20_50 is not None and p80_50 is not None:
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                col1.metric("Bottom Zone (P20)", f"{p20_50:.1f}%")
                col2.metric("Median", f"{median_50:.1f}%")
                col3.metric("Top Zone (P80)", f"{p80_50:.1f}%")
                # Current values
                latest_data = df.iloc[-1]
                col4.metric("MA20 (Current)", f"{latest_data['pct_ma20']:.1f}%")
                col5.metric("MA50 (Current)", f"{latest_data['pct_ma50']:.1f}%")
                col6.metric("MA100 (Current)", f"{latest_data['pct_ma100']:.1f}%")
        
        with col_chart2:
            render_trading_value_chart()

    except Exception as e:
        st.error(f"Lỗi tải Market Breadth: {e}")




def render_trading_value_chart():
    """Render compact Trading Value chart for side-by-side display with Market Breadth
    
    VN: Hiển thị biểu đồ Trading Value (volume x price) theo sector - compact version
    """
    st.subheader("Trading Value by Sector")
    
    try:
        import duckdb
        import plotly.graph_objects as go
        
        sector_path = get_data_path("DATA/processed/technical/market_breadth/market_breadth_sector.parquet")
        sector_path_str = str(sector_path)
        
        if not Path(sector_path).exists():
            st.warning("⚠️ File sector breadth không tồn tại")
            return
        
        conn = duckdb.connect()
        
        # Get latest date data
        df_latest = conn.execute(
            """
            WITH latest_date AS (
                SELECT MAX(date) as max_date
                FROM read_parquet(?)
            )
            SELECT 
                sector,
                trading_value,
                trading_value_pct,
                trading_value_change_5d,
                trading_value_change_20d
            FROM read_parquet(?)
            WHERE date = (SELECT max_date FROM latest_date)
            ORDER BY trading_value DESC
            LIMIT 10
            """,
            [sector_path_str, sector_path_str]
        ).fetchdf()
        
        if df_latest.empty:
            st.info("Chưa có dữ liệu trading value")
            return
        
        # Create compact bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_latest['sector'],
            y=df_latest['trading_value'] / 1e9,  # Convert to billions
            text=[f"{tv/1e9:.1f}B" for tv in df_latest['trading_value']],
            textposition='auto',
            marker=dict(
                color=df_latest['trading_value_change_5d'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Change 5D (%)", len=0.5, y=0.5, yanchor='middle')
            ),
            hovertemplate='<b>%{x}</b><br>Trading Value: %{text}<br>Change 5D: %{customdata:.1f}%<extra></extra>',
            customdata=df_latest['trading_value_change_5d']
        ))
        
        fig.update_layout(
            title="Trading Value by Sector (Latest)",
            xaxis_title="Sector",
            yaxis_title="Trading Value (Billion VND)",
            height=500,
            xaxis=dict(tickangle=-45),
            hovermode='x unified',
            showlegend=False
        )
        
        # Key riêng cho chart VN-Index PE để tránh trùng với Trading Value chart
        st.plotly_chart(fig, config=PLOTLY_CONFIG, use_container_width=True, key="vnindex_pe_chart_main")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total TV", f"{df_latest['trading_value'].sum()/1e9:.2f}B")
        with col2:
            st.metric("Top Sector", df_latest.iloc[0]['sector'])
        with col3:
            st.metric("Avg Change 5D", f"{df_latest['trading_value_change_5d'].mean():+.1f}%")
        
    except Exception as e:
        st.error(f"❌ Lỗi tải Trading Value: {e}")

def render_sector_breadth_table():
    """Render Sector Breadth table with strength score, rank, and trend indicators

    VN: Hiển thị bảng Market Breadth theo từng ngành với strength score, rank, và các chỉ báo trend
    """
    st.subheader("Sector Breadth Analysis")
    st.markdown("---")

    # Resolve file path tương đối từ project root (không dùng iCloud absolute path)
    local_sector_path = get_data_path("DATA/processed/technical/market_breadth/market_breadth_sector.parquet")

    if not local_sector_path.exists():
        st.warning(f"⚠️ File sector breadth không tồn tại tại: `{local_sector_path}`")
        st.info("💡 Vui lòng chạy script tổng hợp dữ liệu sector breadth và kiểm tra lại đường dẫn dưới project root.")
        return

    try:
        import duckdb
        import pandas as pd

        # Load data using DuckDB - chỉ lấy dữ liệu ngày mới nhất
        conn = duckdb.connect()
        df_sector = conn.execute(
            """
            WITH latest_date AS (
                SELECT MAX(TRY_CAST(date AS DATE)) as max_date
                FROM read_parquet(?)
            )
            SELECT 
                s.sector,
                s.total_stocks,
                s.above_ma20,
                s.above_ma50,
                s.above_ma100,
                s.above_ma200,
                s.ma20_breadth_ratio,
                s.ma50_breadth_ratio,
                s.ma100_breadth_ratio,
                s.ma200_breadth_ratio,
                s.pct_ma20,
                s.pct_ma50,
                s.pct_ma100,
                s.pct_ma200,
                s.strength_score,
                s.trend_5d,
                s.trend_20d,
                s.momentum,
                s.acceleration,
                s.rank,
                s.rank_change,
                s.rotation_signal,
                s.date
            FROM read_parquet(?) s
            CROSS JOIN latest_date ld
            WHERE TRY_CAST(s.date AS DATE) = ld.max_date
            ORDER BY s.strength_score DESC
            """,
            [str(local_sector_path), str(local_sector_path)]
        ).fetchdf()

        if df_sector.empty:
            st.warning("⚠️ Không có dữ liệu sector breadth.")
            return

        latest_date = df_sector['date'].max() if 'date' in df_sector.columns else None
        if latest_date:
            st.caption(f"📅 Dữ liệu mới nhất: {pd.to_datetime(latest_date).strftime('%Y-%m-%d')} | Tổng số ngành: {len(df_sector)}")

        # Prepare display columns
        display_cols = {
            'sector': 'Ngành',
            'total_stocks': 'Tổng mã',
            'above_ma20': '>MA20',
            'above_ma50': '>MA50',
            'above_ma100': '>MA100',
            'above_ma200': '>MA200',
            'ma20_breadth_ratio': '%MA20',
            'ma50_breadth_ratio': '%MA50',
            'strength_score': 'Strength',
            'rank': 'Rank',
            'rank_change': 'ΔRank',
            'trend_5d': 'Trend 5D',
            'trend_20d': 'Trend 20D',
            'momentum': 'Momentum',
            'rotation_signal': 'Signal'
        }

        # Create display dataframe
        df_display = df_sector.copy()

        # Format percentages
        for col in ['ma20_breadth_ratio', 'ma50_breadth_ratio', 'ma100_breadth_ratio', 'ma200_breadth_ratio', 'strength_score']:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "N/A")

        # Format integers
        for col in ['total_stocks', 'above_ma20', 'above_ma50', 'above_ma100', 'above_ma200']:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: f"{int(x)}" if pd.notna(x) else "N/A")

        # Format rank
        if 'rank' in df_display.columns:
            df_display['rank'] = df_display['rank'].apply(lambda x: f"{int(x)}" if pd.notna(x) else "N/A")

        # Format rank_change
        if 'rank_change' in df_display.columns:
            def format_rank_change(x):
                if pd.isna(x):
                    return "N/A"
                val = float(x)
                if val > 0:
                    return f"+{int(val)}"
                return f"{int(val)}"
            df_display['rank_change'] = df_display['rank_change'].apply(format_rank_change)

        # Format trend
        for col in ['trend_5d', 'trend_20d']:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: f"{x:+.2f}" if pd.notna(x) else "N/A")

        # Format momentum
        if 'momentum' in df_display.columns:
            df_display['momentum'] = df_display['momentum'].apply(lambda x: f"{x:+.2f}" if pd.notna(x) else "N/A")

        # Format rotation signal
        if 'rotation_signal' in df_display.columns:
            def format_signal(x):
                if pd.isna(x):
                    return "N/A"
                signals = {
                    'Strong Buy': '🟢 Strong Buy',
                    'Buy': '🟡 Buy',
                    'Neutral': '⚪ Neutral',
                    'Sell': '🟠 Sell',
                    'Strong Sell': '🔴 Strong Sell'
                }
                return signals.get(str(x), str(x))
            df_display['rotation_signal'] = df_display['rotation_signal'].apply(format_signal)

        # Select and rename columns for display
        cols_to_show = ['sector', 'total_stocks', 'above_ma20', 'above_ma50', 'ma20_breadth_ratio',
                        'ma50_breadth_ratio', 'strength_score', 'rank', 'rank_change',
                        'trend_5d', 'trend_20d', 'momentum', 'rotation_signal']
        cols_to_show = [c for c in cols_to_show if c in df_display.columns]

        df_display = df_display[cols_to_show].copy()
        df_display = df_display.rename(columns=display_cols)

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )

        with st.expander("ℹ️ Giải thích các chỉ số"):
            st.markdown("""
            **Strength Score**: Điểm tổng hợp dựa trên % cổ phiếu > MA20 và > MA50 (0-1, càng cao càng mạnh)

            **Rank**: Xếp hạng theo Strength Score (1 = mạnh nhất)

            **ΔRank**: Thay đổi rank so với kỳ trước (+ = tăng hạng, - = giảm hạng)

            **Trend 5D / 20D**: Xu hướng strength score trong 5/20 ngày gần nhất (+ = tăng, - = giảm)

            **Momentum**: Tốc độ thay đổi strength score (+ = tăng tốc, - = giảm tốc)

            **Signal**: Tín hiệu rotation (🟢 Strong Buy = ngành đang mạnh và tăng tốc, 🔴 Strong Sell = ngành đang yếu và giảm tốc)

            **%MA20 / %MA50**: Tỷ lệ % cổ phiếu trong ngành vượt MA20/MA50
            """)

    except Exception as e:
        st.error(f"❌ Lỗi tải dữ liệu sector breadth: {e}")
        import traceback
        st.exception(e)


def render_vnindex_pe_chart():
    """Render VN-Index PE ratio chart using pyecharts
    
    VN: Hiển thị biểu đồ tỷ lệ PE của VN-Index
    """
    st.subheader("VN-Index PE Ratio Analysis")
    range_option = st.selectbox("Khung thời gian", ["YTD", "1Y", "2Y", "3Y", "All"], index=0)
    
    try:
        # Load VN-Index PE data (single file with all data including BSC Universal PE)
        pe_data_path = get_data_path("DATA/processed/valuation/vnindex_pe_historical_final.parquet")
        
        if not os.path.exists(pe_data_path):
            st.warning("⚠️ Chưa có dữ liệu VN-Index PE. Vui lòng chạy script tính toán PE trước.")
            return
        
        # Load main PE data
        with st.spinner("Đang tải dữ liệu VN-Index PE..."):
            df = pd.read_parquet(pe_data_path)
        
        if df.empty:
            st.warning("Không có dữ liệu VN-Index PE")
            return
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Get date range for display and apply time filter
        latest_date = df['date'].max()
        earliest_date = df['date'].min()
        if range_option == "YTD":
            start_display = pd.Timestamp(str(latest_date.year) + "-01-01")
        elif range_option == "1Y":
            start_display = latest_date - pd.Timedelta(days=365)
        elif range_option == "2Y":
            start_display = latest_date - pd.Timedelta(days=730)
        elif range_option == "3Y":
            start_display = latest_date - pd.Timedelta(days=1095)
        else:
            start_display = earliest_date
        df_filtered = df[df['date'] >= start_display].copy()
        
        if df_filtered.empty:
            st.warning("Không có dữ liệu PE")
            return
        
        
        # Show data info
        st.caption(f"Dữ liệu mới nhất: {df_filtered['date'].max().strftime('%Y-%m-%d')} | Tổng số records: {len(df_filtered):,}")
        
        # Prepare data for chart
        dates = [d.strftime('%Y-%m-%d') for d in df_filtered['date']]
        pe_ratios = df_filtered['pe_ratio'].tolist()
        
        # Check if excluded PE data exists
        has_excluded_data = 'pe_ratio_excluded' in df_filtered.columns
        if has_excluded_data:
            # Keep None values to preserve alignment with x-axis
            pe_ratios_excluded = df_filtered['pe_ratio_excluded'].tolist()
        else:
            pe_ratios_excluded = []
        
        # Check if BSC Universal PE data exists
        has_bsc_universal_data = 'pe_ratio_bsc_universal' in df_filtered.columns
        if has_bsc_universal_data:
            # Keep None values to preserve alignment with x-axis
            pe_ratios_bsc_universal = df_filtered['pe_ratio_bsc_universal'].tolist()
        else:
            pe_ratios_bsc_universal = []
        
        # Calculate statistics
        current_pe = pe_ratios[-1] if pe_ratios else None
        avg_pe = np.mean(pe_ratios)
        min_pe = np.min(pe_ratios)
        max_pe = np.max(pe_ratios)
        
        # Calculate statistics for excluded data
        if has_excluded_data and pe_ratios_excluded:
            current_pe_excluded = pe_ratios_excluded[-1] if pe_ratios_excluded else None
            avg_pe_excluded = np.mean(pe_ratios_excluded)
            min_pe_excluded = np.min(pe_ratios_excluded)
            max_pe_excluded = np.max(pe_ratios_excluded)
        else:
            current_pe_excluded = None
            avg_pe_excluded = None
            min_pe_excluded = None
            max_pe_excluded = None
        
        # Calculate statistics for BSC Universal data
        if has_bsc_universal_data and pe_ratios_bsc_universal:
            current_pe_bsc_universal = pe_ratios_bsc_universal[-1] if pe_ratios_bsc_universal else None
            avg_pe_bsc_universal = np.mean(pe_ratios_bsc_universal)
            min_pe_bsc_universal = np.min(pe_ratios_bsc_universal)
            max_pe_bsc_universal = np.max(pe_ratios_bsc_universal)
        else:
            current_pe_bsc_universal = None
            avg_pe_bsc_universal = None
            min_pe_bsc_universal = None
            max_pe_bsc_universal = None
        
        # Compute 1Y median and std bands (fallback to full history if < 30 points)
        one_year_ago = latest_date - pd.Timedelta(days=365)
        df_last_year = df[(df['date'] >= one_year_ago)].copy()
        if len(df_last_year) < 30:
            df_last_year = df.copy()
        median_1y = float(np.nanmedian(df_last_year['pe_ratio'].values))
        std_1y = float(np.nanstd(df_last_year['pe_ratio'].values))
        median_line = [round(median_1y, 2) for _ in dates]
        plus1_line = [round(median_1y + std_1y, 2) for _ in dates]
        minus1_line = [round(median_1y - std_1y, 2) for _ in dates]

        # Dynamic y-axis min (not below 6)
        try:
            visible_min = float(np.nanmin(pe_ratios)) if pe_ratios else 6.0
        except Exception:
            visible_min = 6.0
        y_min_value = max(6.0, round(visible_min - 1.0, 1))

        # Build Plotly chart instead (fallback/stable)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_filtered['date'],
            y=pe_ratios,
            mode='lines',
            name='VN-Index PE (All)',
            line=dict(color='#1f77b4', width=2.5),
            hovertemplate='Date: %{x}<br>PE: %{y:.2f}<extra></extra>'
        ))

        if has_excluded_data and len(pe_ratios_excluded) == len(pe_ratios):
            fig.add_trace(go.Scatter(
                x=df_filtered['date'],
                y=pe_ratios_excluded,
                mode='lines',
                name='VN-Index PE (Excluded)',
                line=dict(color='#ff7f0e', width=2.5),
                hovertemplate='Date: %{x}<br>PE Excluded: %{y:.2f}<extra></extra>'
            ))

        if has_bsc_universal_data and len(pe_ratios_bsc_universal) == len(pe_ratios):
            fig.add_trace(go.Scatter(
                x=df_filtered['date'],
                y=pe_ratios_bsc_universal,
                mode='lines',
                name='BSC Universal PE',
                line=dict(color='#2ca02c', width=2.5),
                hovertemplate='Date: %{x}<br>BSC Universal PE: %{y:.2f}<extra></extra>'
            ))

        # Median and bands
        fig.add_trace(go.Scatter(
            x=df_filtered['date'],
            y=median_line,
            mode='lines',
            name='Median (1Y)',
            line=dict(color='#616161', width=1.2, dash='dot'),
            hovertemplate='Date: %{x}<br>Median: %{y:.2f}<extra></extra>'
        ))
        fig.add_trace(go.Scatter(
            x=df_filtered['date'],
            y=plus1_line,
            mode='lines',
            name='+1σ (1Y)',
            line=dict(color='#9e9e9e', width=1.2, dash='dash'),
            hovertemplate='Date: %{x}<br>+1σ: %{y:.2f}<extra></extra>'
        ))
        fig.add_trace(go.Scatter(
            x=df_filtered['date'],
            y=minus1_line,
            mode='lines',
            name='-1σ (1Y)',
            line=dict(color='#9e9e9e', width=1.2, dash='dash'),
            hovertemplate='Date: %{x}<br>-1σ: %{y:.2f}<extra></extra>'
        ))

        subtitle_text = f"Current PE: {current_pe:.2f} | Average: {avg_pe:.2f}"
        if has_excluded_data and current_pe_excluded is not None:
            subtitle_text += f" | Excluded PE: {current_pe_excluded:.2f}"
        if has_bsc_universal_data and current_pe_bsc_universal is not None:
            subtitle_text += f" | BSC Universal PE: {current_pe_bsc_universal:.2f}"

        fig.update_layout(
            **get_plotly_font_config(),
            title=dict(text='VN-Index PE Ratio Analysis', x=0.5),
            xaxis_title='Date',
            yaxis_title='PE Ratio',
            height=600,
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis=dict(
                rangeslider=dict(visible=True, thickness=0.1),
                rangeselector=dict(buttons=list([
                    dict(count=1, label='1M', step='month', stepmode='backward'),
                    dict(count=3, label='3M', step='month', stepmode='backward'),
                    dict(count=6, label='6M', step='month', stepmode='backward'),
                    dict(count=1, label='1Y', step='year', stepmode='backward'),
                    dict(step='all', label='All')
                ]))
            ),
            yaxis=dict(range=[y_min_value, None], gridcolor='rgba(128,128,128,0.2)')
        )

        # Key riêng cho chart commodity để tránh trùng với Trading Value / VNIndex PE
        st.plotly_chart(fig, config=PLOTLY_CONFIG, use_container_width=True, key="commodity_prices_chart")
        
        # Display metrics
        if has_excluded_data and current_pe_excluded is not None or has_bsc_universal_data and current_pe_bsc_universal is not None:
            # Show metrics comparison including BSC Universal if available
            st.subheader("📊 PE Metrics Comparison")
            
            # Determine number of columns based on available data
            metrics_count = 1  # Always show All PE
            if has_excluded_data and current_pe_excluded is not None:
                metrics_count += 1
            if has_bsc_universal_data and current_pe_bsc_universal is not None:
                metrics_count += 1
            
            # Create columns dynamically
            cols = st.columns(metrics_count)
            col_idx = 0
            
            # Current PE metrics
            with cols[col_idx]:
                st.metric(
                    "Current PE (All)",
                    f"{current_pe:.2f}" if current_pe else "N/A",
                    delta=None
                )
            col_idx += 1
            
            if has_excluded_data and current_pe_excluded is not None:
                with cols[col_idx]:
                    st.metric(
                        "Current PE (Excluded)",
                        f"{current_pe_excluded:.2f}" if current_pe_excluded else "N/A",
                        delta=f"{current_pe_excluded - current_pe:+.2f}" if current_pe and current_pe_excluded else None
                    )
                col_idx += 1
            
            if has_bsc_universal_data and current_pe_bsc_universal is not None:
                with cols[col_idx]:
                    st.metric(
                        "BSC Universal PE",
                        f"{current_pe_bsc_universal:.2f}" if current_pe_bsc_universal else "N/A",
                        delta=f"{current_pe_bsc_universal - current_pe:+.2f}" if current_pe and current_pe_bsc_universal else None
                    )
                col_idx += 1
            
            # Average PE metrics
            cols = st.columns(metrics_count)
            col_idx = 0
            
            with cols[col_idx]:
                st.metric(
                    "Average PE (All)",
                    f"{avg_pe:.2f}",
                    delta=None
                )
            col_idx += 1
            
            if has_excluded_data and avg_pe_excluded is not None:
                with cols[col_idx]:
                    st.metric(
                        "Average PE (Excluded)",
                        f"{avg_pe_excluded:.2f}" if avg_pe_excluded else "N/A",
                        delta=f"{avg_pe_excluded - avg_pe:+.2f}" if avg_pe and avg_pe_excluded else None
                    )
                col_idx += 1
            
            if has_bsc_universal_data and avg_pe_bsc_universal is not None:
                with cols[col_idx]:
                    st.metric(
                        "Average BSC Universal PE",
                        f"{avg_pe_bsc_universal:.2f}" if avg_pe_bsc_universal else "N/A",
                        delta=f"{avg_pe_bsc_universal - avg_pe:+.2f}" if avg_pe and avg_pe_bsc_universal else None
                    )
                col_idx += 1
            
            # Min/Max comparison
            cols = st.columns(metrics_count)
            col_idx = 0
            
            with cols[col_idx]:
                st.metric("Min PE (All)", f"{min_pe:.2f}")
            col_idx += 1
            
            if has_excluded_data and min_pe_excluded is not None:
                with cols[col_idx]:
                    st.metric("Min PE (Excluded)", f"{min_pe_excluded:.2f}" if min_pe_excluded else "N/A")
                col_idx += 1
            
            if has_bsc_universal_data and min_pe_bsc_universal is not None:
                with cols[col_idx]:
                    st.metric("Min BSC Universal PE", f"{min_pe_bsc_universal:.2f}" if min_pe_bsc_universal else "N/A")
                col_idx += 1
            
            cols = st.columns(metrics_count)
            col_idx = 0
            
            with cols[col_idx]:
                st.metric("Max PE (All)", f"{max_pe:.2f}")
            col_idx += 1
            
            if has_excluded_data and max_pe_excluded is not None:
                with cols[col_idx]:
                    st.metric("Max PE (Excluded)", f"{max_pe_excluded:.2f}" if max_pe_excluded else "N/A")
                col_idx += 1
            
            if has_bsc_universal_data and max_pe_bsc_universal is not None:
                with cols[col_idx]:
                    st.metric("Max BSC Universal PE", f"{max_pe_bsc_universal:.2f}" if max_pe_bsc_universal else "N/A")
                col_idx += 1
        else:
            # Show original metrics if no excluded data
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Current PE",
                    f"{current_pe:.2f}" if current_pe else "N/A",
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Average PE",
                    f"{avg_pe:.2f}",
                    delta=None
                )
            
            with col3:
                st.metric(
                    "Min PE",
                    f"{min_pe:.2f}",
                    delta=None
                )
            
            with col4:
                st.metric(
                    "Max PE",
                    f"{max_pe:.2f}",
                    delta=None
                )
        
        # PE Analysis
        st.subheader("📈 PE Analysis")
        
        # Calculate percentiles
        pe_25 = np.percentile(pe_ratios, 25)
        pe_50 = np.percentile(pe_ratios, 50)
        pe_75 = np.percentile(pe_ratios, 75)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("25th Percentile", f"{pe_25:.2f}")
        
        with col2:
            st.metric("50th Percentile (Median)", f"{pe_50:.2f}")
        
        with col3:
            st.metric("75th Percentile", f"{pe_75:.2f}")
        
        # PE Valuation zones
        if current_pe:
            if current_pe < pe_25:
                valuation = "🟢 Undervalued"
                color = "green"
            elif current_pe < pe_50:
                valuation = "🟡 Fair Value (Low)"
                color = "orange"
            elif current_pe < pe_75:
                valuation = "🟡 Fair Value (High)"
                color = "orange"
            else:
                valuation = "🔴 Overvalued"
                color = "red"
            
            st.markdown(f"### Current Valuation: <span style='color:{color}'>{valuation}</span>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Lỗi tải VN-Index PE data: {e}")
        st.exception(e)


def render_commodity_chart():
    """Render Commodity Price chart using Plotly
    
    VN: Hiển thị biểu đồ giá hàng hoá với Plotly
    """
    st.subheader("Commodity Prices")
    
    # Add reload button để force reload data khi file được update
    col_reload, _ = st.columns([1, 10])
    with col_reload:
        if st.button("🔄 Reload Data", help="Force reload commodity data từ file (dùng khi file vừa được update)"):
            MacroCommodityLoader.clear_cache()
            st.success("✅ Cache cleared! Data sẽ được reload.")
            st.rerun()
    
    try:
        # Initialize loader
        loader = MacroCommodityLoader()
        
        # Get available commodity types
        commodity_types = loader.get_available_symbols(category='commodity')
        
        if not commodity_types:
            st.warning("⚠️ Chưa có dữ liệu commodity. Vui lòng chạy script cập nhật dữ liệu trước.")
            return
        
        
        # Prepare options: remove gold_vn, gold_global, pork_north_vn, pork_china, fertilizer_ure_vn, fertilizer_ure_global
        # Add "Giá vàng", "Giá heo hơi", and "Giá phân bón" as special options
        regular_commodities = [c for c in commodity_types if c not in [
            'gold_vn', 'gold_global', 
            'pork_north_vn', 'pork_china',
            'fertilizer_ure_vn', 'fertilizer_ure_global'
        ]]
        
        # Create options list with special options first
        options_list = []
        has_gold = 'gold_vn' in commodity_types and 'gold_global' in commodity_types
        has_pork = 'pork_north_vn' in commodity_types and 'pork_china' in commodity_types
        has_fertilizer = 'fertilizer_ure_vn' in commodity_types and 'fertilizer_ure_global' in commodity_types
        
        if has_gold:
            options_list.append('__GOLD__')
        if has_pork:
            options_list.append('__PORK__')
        if has_fertilizer:
            options_list.append('__FERTILIZER__')
        
        options_list.extend(regular_commodities)
        
        if not options_list:
            options_list = regular_commodities
        
        # Create two columns for filters
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Selectbox for single commodity selection
            selected_option = st.selectbox(
                "Chọn loại hàng hoá",
                options=options_list,
                index=0 if options_list else None,
                format_func=lambda x: (
                    "Giá vàng" if x == '__GOLD__' 
                    else "Giá heo hơi" if x == '__PORK__'
                    else "Giá phân bón" if x == '__FERTILIZER__'
                    else COMMODITY_DESCRIPTIONS.get(x, x)
                )
            )
        
        with col2:
            # Time range selector
            time_range = st.selectbox(
                "Khung thời gian",
                options=["3Y", "2Y", "1Y", "YTD"],
                index=2  # Default to 1Y
            )
        
        if not selected_option:
            st.info("Vui lòng chọn một loại hàng hoá để hiển thị")
            return
        
        # Special handling for gold, pork, and fertilizer: show both types together with dual y-axis
        if selected_option == '__GOLD__':
            commodities_to_load = ['gold_vn', 'gold_global']
            use_dual_axis = True
            dual_axis_type = 'gold'
        elif selected_option == '__PORK__':
            commodities_to_load = ['pork_north_vn', 'pork_china']
            use_dual_axis = True
            dual_axis_type = 'pork'
        elif selected_option == '__FERTILIZER__':
            commodities_to_load = ['fertilizer_ure_vn', 'fertilizer_ure_global']
            use_dual_axis = True
            dual_axis_type = 'fertilizer'
        else:
            commodities_to_load = [selected_option]
            use_dual_axis = False
            dual_axis_type = None
        
        # Calculate date range
        end_date = pd.Timestamp.now()
        if time_range == "YTD":
            start_date = pd.Timestamp(f"{end_date.year}-01-01")
        elif time_range == "1Y":
            start_date = end_date - pd.Timedelta(days=365)
        elif time_range == "2Y":
            start_date = end_date - pd.Timedelta(days=730)
        elif time_range == "3Y":
            start_date = end_date - pd.Timedelta(days=1095)
        else:
            start_date = end_date - pd.Timedelta(days=365)
        
        # Load data for selected commodities
        # Load data for selected commodities
        with st.spinner("Đang tải dữ liệu commodity..."):
            # Load unified data and filter
            df_unified = loader.load_data()
            if df_unified.empty:
                df = pd.DataFrame()
            else:
                # Filter by category and date
                mask = (
                    (df_unified['category'] == 'commodity') & 
                    (df_unified['symbol'].isin(commodities_to_load)) &
                    (df_unified['date'] >= pd.to_datetime(start_date)) &
                    (df_unified['date'] <= pd.to_datetime(end_date))
                )
                df = df_unified[mask].copy()
                # Rename 'symbol' to 'commodity_type' for compatibility with existing chart logic
                df = df.rename(columns={'symbol': 'commodity_type'})
        
        if df.empty:
            st.warning("Không có dữ liệu cho khoảng thời gian đã chọn")
            return
        
        # Show data info
        latest_date = df['date'].max()
        num_commodities = df['commodity_type'].nunique()
        st.caption(f"Dữ liệu mới nhất: {latest_date.strftime('%Y-%m-%d')} | Số loại hàng hóa: {num_commodities}")
        
        # Prepare data for chart
        chart_data = {}
        
        for commodity_type in commodities_to_load:
            commodity_df = df[df['commodity_type'] == commodity_type].copy()
            if commodity_df.empty:
                continue
            
            # Sort by date
            commodity_df = commodity_df.sort_values('date')
            
            # Determine which column to use for price
            # Priority: close > sell > buy > first numeric column
            if 'close' in commodity_df.columns and commodity_df['close'].notna().any():
                # Use close price for OHLCV data (oil_crude, gold_global, pork, etc.)
                price_col = 'close'
            elif commodity_type == 'gold_vn':
                # Use sell price for gold_vn if close not available
                if 'sell' in commodity_df.columns and commodity_df['sell'].notna().any():
                    price_col = 'sell'
                elif 'buy' in commodity_df.columns and commodity_df['buy'].notna().any():
                    price_col = 'buy'
                else:
                    continue
            elif 'sell' in commodity_df.columns and commodity_df['sell'].notna().any():
                # Fallback to sell price
                price_col = 'sell'
            elif 'buy' in commodity_df.columns and commodity_df['buy'].notna().any():
                # Fallback to buy price
                price_col = 'buy'
            else:
                # Try to find any numeric column
                numeric_cols = commodity_df.select_dtypes(include=[np.number]).columns
                numeric_cols = [c for c in numeric_cols if c not in ['commodity_type', 'volume', 'time']]
                if numeric_cols:
                    price_col = numeric_cols[0]
                else:
                    continue
            
            # Extract dates and prices
            dates = [d.strftime('%Y-%m-%d') for d in commodity_df['date']]
            prices = commodity_df[price_col].fillna(0).tolist()
            
            # Remove None values and corresponding dates
            valid_data = [(d, p) for d, p in zip(dates, prices) if p is not None and not pd.isna(p) and p > 0]
            if valid_data:
                chart_data[commodity_type] = {
                    'dates': [d for d, p in valid_data],
                    'prices': [round(float(p), 2) for d, p in valid_data],
                    'description': COMMODITY_DESCRIPTIONS.get(commodity_type, commodity_type),
                    'price_col': price_col
                }
        
        if not chart_data:
            st.warning("Không có dữ liệu hợp lệ để hiển thị")
            return
        
        # Create Plotly chart with dual y-axis for gold and pork
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        if use_dual_axis and len(chart_data) == 2:
            # Create subplot with secondary y-axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            if dual_axis_type == 'gold':
                # Add gold_vn on primary y-axis
                if 'gold_vn' in chart_data:
                    data_vn = chart_data['gold_vn']
                    dates_dt_vn = pd.to_datetime(data_vn['dates'])
                    fig.add_trace(
                        go.Scatter(
                            x=dates_dt_vn,
                            y=data_vn['prices'],
                            mode='lines',
                            name='Giá vàng Việt Nam (VND)',
                            line=dict(color='#1f77b4', width=2.5),
                            hovertemplate='<b>Giá vàng Việt Nam</b><br>' +
                                        'Date: %{x|%Y-%m-%d}<br>' +
                                        'Price: %{y:,.0f} VND<br>' +
                                        '<extra></extra>'
                        ),
                        secondary_y=False
                    )
                
                # Add gold_global on secondary y-axis
                if 'gold_global' in chart_data:
                    data_global = chart_data['gold_global']
                    dates_dt_global = pd.to_datetime(data_global['dates'])
                    fig.add_trace(
                        go.Scatter(
                            x=dates_dt_global,
                            y=data_global['prices'],
                            mode='lines',
                            name='Giá vàng thế giới (USD/oz)',
                            line=dict(color='#ff7f0e', width=2.5),
                            hovertemplate='<b>Giá vàng thế giới</b><br>' +
                                        'Date: %{x|%Y-%m-%d}<br>' +
                                        'Price: %{y:,.2f} USD/oz<br>' +
                                        '<extra></extra>'
                        ),
                        secondary_y=True
                    )
                
                # Update layout for dual y-axis
                fig.update_yaxes(title_text="Giá vàng Việt Nam (VND)", secondary_y=False)
                fig.update_yaxes(title_text="Giá vàng thế giới (USD/oz)", secondary_y=True)
                chart_title = f"Giá Vàng - Việt Nam vs Thế Giới ({time_range})"
                
            elif dual_axis_type == 'pork':
                # Add pork_north_vn on primary y-axis
                if 'pork_north_vn' in chart_data:
                    data_north = chart_data['pork_north_vn']
                    dates_dt_north = pd.to_datetime(data_north['dates'])
                    fig.add_trace(
                        go.Scatter(
                            x=dates_dt_north,
                            y=data_north['prices'],
                            mode='lines',
                            name='Giá heo hơi miền Bắc (VND/kg)',
                            line=dict(color='#1f77b4', width=2.5),
                            hovertemplate='<b>Giá heo hơi miền Bắc</b><br>' +
                                        'Date: %{x|%Y-%m-%d}<br>' +
                                        'Price: %{y:,.0f} VND/kg<br>' +
                                        '<extra></extra>'
                        ),
                        secondary_y=False
                    )
                
                # Add pork_china on secondary y-axis
                if 'pork_china' in chart_data:
                    data_china = chart_data['pork_china']
                    dates_dt_china = pd.to_datetime(data_china['dates'])
                    fig.add_trace(
                        go.Scatter(
                            x=dates_dt_china,
                            y=data_china['prices'],
                            mode='lines',
                            name='Giá heo hơi Trung Quốc (CNY/kg)',
                            line=dict(color='#ff7f0e', width=2.5),
                            hovertemplate='<b>Giá heo hơi Trung Quốc</b><br>' +
                                        'Date: %{x|%Y-%m-%d}<br>' +
                                        'Price: %{y:,.2f} CNY/kg<br>' +
                                        '<extra></extra>'
                        ),
                        secondary_y=True
                    )
                
                # Update layout for dual y-axis
                fig.update_yaxes(title_text="Giá heo hơi miền Bắc (VND/kg)", secondary_y=False)
                fig.update_yaxes(title_text="Giá heo hơi Trung Quốc (CNY/kg)", secondary_y=True)
                chart_title = f"Giá Heo Hơi - Miền Bắc vs Trung Quốc ({time_range})"
            
            elif dual_axis_type == 'fertilizer':
                # Add fertilizer_ure_vn (DPM trong nước) on primary y-axis
                if 'fertilizer_ure_vn' in chart_data:
                    data_vn = chart_data['fertilizer_ure_vn']
                    dates_dt_vn = pd.to_datetime(data_vn['dates'])
                    fig.add_trace(
                        go.Scatter(
                            x=dates_dt_vn,
                            y=data_vn['prices'],
                            mode='lines',
                            name='Giá phân bón DPM trong nước (VND/kg)',
                            line=dict(color='#1f77b4', width=2.5),
                            hovertemplate='<b>Giá phân bón DPM trong nước</b><br>' +
                                        'Date: %{x|%Y-%m-%d}<br>' +
                                        'Price: %{y:,.0f} VND/kg<br>' +
                                        '<extra></extra>'
                        ),
                        secondary_y=False
                    )
                
                # Add fertilizer_ure_global on secondary y-axis
                if 'fertilizer_ure_global' in chart_data:
                    data_global = chart_data['fertilizer_ure_global']
                    dates_dt_global = pd.to_datetime(data_global['dates'])
                    fig.add_trace(
                        go.Scatter(
                            x=dates_dt_global,
                            y=data_global['prices'],
                            mode='lines',
                            name='Giá ure thế giới (USD/tấn)',
                            line=dict(color='#ff7f0e', width=2.5),
                            hovertemplate='<b>Giá ure thế giới</b><br>' +
                                        'Date: %{x|%Y-%m-%d}<br>' +
                                        'Price: %{y:,.2f} USD/tấn<br>' +
                                        '<extra></extra>'
                        ),
                        secondary_y=True
                    )
                
                # Update layout for dual y-axis
                fig.update_yaxes(title_text="Giá phân bón DPM trong nước (VND/kg)", secondary_y=False)
                fig.update_yaxes(title_text="Giá ure thế giới (USD/tấn)", secondary_y=True)
                chart_title = f"Giá Phân Bón - DPM trong nước vs Ure thế giới ({time_range})"
            
            # Common layout updates for dual y-axis charts
            fig.update_xaxes(title_text="Date")
            
            fig.update_layout(
                **get_plotly_font_config(),
                title=dict(
                    text=chart_title,
                    x=0.5,
                    font=dict(size=18)
                ),
                height=600,
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                xaxis=dict(
                    rangeslider=dict(visible=True, thickness=0.1),
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1M", step="month", stepmode="backward"),
                            dict(count=3, label="3M", step="month", stepmode="backward"),
                            dict(count=6, label="6M", step="month", stepmode="backward"),
                            dict(count=1, label="1Y", step="year", stepmode="backward"),
                            dict(step="all", label="All")
                        ])
                    )
                )
            )
        else:
            # Single y-axis chart for other commodities
            fig = go.Figure()
            
            # Colors for different commodities
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            
            # Add trace for each commodity
            for idx, (commodity_type, data) in enumerate(chart_data.items()):
                # Convert dates to datetime for Plotly
                dates_dt = pd.to_datetime(data['dates'])
                
                fig.add_trace(go.Scatter(
                    x=dates_dt,
                    y=data['prices'],
                    mode='lines',
                    name=data['description'],
                    line=dict(color=colors[idx % len(colors)], width=2.5),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                'Date: %{x|%Y-%m-%d}<br>' +
                                'Price: %{y:,.2f}<br>' +
                                '<extra></extra>'
                ))
            
            # Update layout
            fig.update_layout(
                **get_plotly_font_config(),  # Apply Nunito font
                title=dict(
                    text=f"Commodity Prices - {time_range}",
                    x=0.5,
                    font=dict(size=18)
                ),
                xaxis_title="Date",
                yaxis_title="Price",
                height=600,
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                xaxis=dict(
                    rangeslider=dict(visible=True, thickness=0.1),
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1M", step="month", stepmode="backward"),
                            dict(count=3, label="3M", step="month", stepmode="backward"),
                            dict(count=6, label="6M", step="month", stepmode="backward"),
                            dict(count=1, label="1Y", step="year", stepmode="backward"),
                            dict(step="all", label="All")
                        ])
                    )
                )
            )
        
        # Display chart
        st.plotly_chart(fig, config=PLOTLY_CONFIG, use_container_width=True, key="trading_value_chart")
        
        st.markdown("---")
        
        # Performance Summary Table AFTER chart
        st.subheader("📊 Performance Summary - Tất cả Commodity")
        
        # Calculate date range for performance table (use 3Y to get all data)
        end_date = pd.Timestamp.now()
        start_date_perf = end_date - pd.Timedelta(days=1095)  # 3 years for performance calculation
        
        # Load ALL commodities data for performance table
        # Load ALL commodities data for performance table
        with st.spinner("Đang tải dữ liệu commodity cho bảng performance..."):
            df_all_unified = loader.load_data()
            if not df_all_unified.empty:
                df_all = df_all_unified[df_all_unified['category'] == 'commodity'].copy()
                df_all = df_all.rename(columns={'symbol': 'commodity_type'})
                if 'date' in df_all.columns:
                    df_all['date'] = pd.to_datetime(df_all['date'])
                    df_all = df_all[df_all['date'] >= start_date_perf].copy()
        
        if not df_all.empty:
            # Calculate performance for ALL commodities
            performance_data = []
            
            for commodity_type in commodity_types:
                commodity_df = df_all[df_all['commodity_type'] == commodity_type].copy()
                if commodity_df.empty:
                    continue
                
                commodity_df = commodity_df.sort_values('date')
                
                # Determine price column - Priority: close > sell > buy
                if 'close' in commodity_df.columns and commodity_df['close'].notna().any():
                    price_col = 'close'
                elif commodity_type == 'gold_vn':
                    price_col = 'sell' if 'sell' in commodity_df.columns and commodity_df['sell'].notna().any() else 'buy'
                elif 'sell' in commodity_df.columns and commodity_df['sell'].notna().any():
                    price_col = 'sell'
                elif 'buy' in commodity_df.columns and commodity_df['buy'].notna().any():
                    price_col = 'buy'
                else:
                    numeric_cols = commodity_df.select_dtypes(include=[np.number]).columns
                    numeric_cols = [c for c in numeric_cols if c not in ['commodity_type', 'volume', 'time']]
                    if numeric_cols:
                        price_col = numeric_cols[0]
                    else:
                        continue
                
                # Get valid data
                valid_df = commodity_df[commodity_df[price_col].notna() & (commodity_df[price_col] > 0)].copy()
                if valid_df.empty:
                    continue
                
                latest_price = valid_df[price_col].iloc[-1]
                latest_date = valid_df['date'].iloc[-1]
                
                # Calculate performance metrics
                performance = {
                    'Commodity': COMMODITY_DESCRIPTIONS.get(commodity_type, commodity_type),
                    'Latest Price': latest_price,
                    'Latest Date': latest_date.strftime('%Y-%m-%d')
                }
                
                # 1D: Find closest date to 1 day ago
                one_day_ago = latest_date - pd.Timedelta(days=1)
                oned_candidates = valid_df[valid_df['date'] <= one_day_ago].copy()
                if len(oned_candidates) > 0:
                    oned_candidates = oned_candidates.copy()
                    oned_candidates['days_diff'] = abs((oned_candidates['date'] - one_day_ago).dt.days)
                    closest_idx = oned_candidates['days_diff'].idxmin()
                    closest_oned = oned_candidates.loc[closest_idx]
                    oned_price = closest_oned[price_col]
                    if pd.notna(oned_price) and oned_price > 0:
                        performance['% 1D'] = ((latest_price / oned_price) - 1) * 100
                    else:
                        performance['% 1D'] = None
                else:
                    performance['% 1D'] = None
                
                # 1W: Find closest date to 1 week ago
                one_week_ago = latest_date - pd.Timedelta(days=7)
                onew_candidates = valid_df[valid_df['date'] <= one_week_ago].copy()
                if len(onew_candidates) > 0:
                    onew_candidates = onew_candidates.copy()
                    onew_candidates['days_diff'] = abs((onew_candidates['date'] - one_week_ago).dt.days)
                    closest_idx = onew_candidates['days_diff'].idxmin()
                    closest_onew = onew_candidates.loc[closest_idx]
                    onew_price = closest_onew[price_col]
                    if pd.notna(onew_price) and onew_price > 0:
                        performance['% 1W'] = ((latest_price / onew_price) - 1) * 100
                    else:
                        performance['% 1W'] = None
                else:
                    performance['% 1W'] = None
                
                # 1M: Find closest date to 1 month ago
                one_month_ago = latest_date - pd.Timedelta(days=30)
                onem_candidates = valid_df[valid_df['date'] <= one_month_ago].copy()
                if len(onem_candidates) > 0:
                    onem_candidates = onem_candidates.copy()
                    onem_candidates['days_diff'] = abs((onem_candidates['date'] - one_month_ago).dt.days)
                    closest_idx = onem_candidates['days_diff'].idxmin()
                    closest_onem = onem_candidates.loc[closest_idx]
                    onem_price = closest_onem[price_col]
                    if pd.notna(onem_price) and onem_price > 0:
                        performance['% 1M'] = ((latest_price / onem_price) - 1) * 100
                    else:
                        performance['% 1M'] = None
                else:
                    performance['% 1M'] = None
                
                # 3M: Find closest date to 3 months ago
                three_months_ago = latest_date - pd.Timedelta(days=90)
                threem_candidates = valid_df[valid_df['date'] <= three_months_ago].copy()
                if len(threem_candidates) > 0:
                    threem_candidates = threem_candidates.copy()
                    threem_candidates['days_diff'] = abs((threem_candidates['date'] - three_months_ago).dt.days)
                    closest_idx = threem_candidates['days_diff'].idxmin()
                    closest_threem = threem_candidates.loc[closest_idx]
                    threem_price = closest_threem[price_col]
                    if pd.notna(threem_price) and threem_price > 0:
                        performance['% 3M'] = ((latest_price / threem_price) - 1) * 100
                    else:
                        performance['% 3M'] = None
                else:
                    performance['% 3M'] = None
                
                # 1Y: Find closest date to 1 year ago
                one_year_ago = latest_date - pd.Timedelta(days=365)
                oney_candidates = valid_df[valid_df['date'] <= one_year_ago].copy()
                if len(oney_candidates) > 0:
                    oney_candidates = oney_candidates.copy()
                    oney_candidates['days_diff'] = abs((oney_candidates['date'] - one_year_ago).dt.days)
                    closest_idx = oney_candidates['days_diff'].idxmin()
                    closest_oney = oney_candidates.loc[closest_idx]
                    oney_price = closest_oney[price_col]
                    if pd.notna(oney_price) and oney_price > 0:
                        performance['% 1Y'] = ((latest_price / oney_price) - 1) * 100
                    else:
                        performance['% 1Y'] = None
                else:
                    performance['% 1Y'] = None
                
                # 2Y: Find closest date to 2 years ago
                two_years_ago = latest_date - pd.Timedelta(days=730)
                twoy_candidates = valid_df[valid_df['date'] <= two_years_ago].copy()
                if len(twoy_candidates) > 0:
                    twoy_candidates = twoy_candidates.copy()
                    twoy_candidates['days_diff'] = abs((twoy_candidates['date'] - two_years_ago).dt.days)
                    closest_idx = twoy_candidates['days_diff'].idxmin()
                    closest_twoy = twoy_candidates.loc[closest_idx]
                    twoy_price = closest_twoy[price_col]
                    if pd.notna(twoy_price) and twoy_price > 0:
                        performance['% 2Y'] = ((latest_price / twoy_price) - 1) * 100
                    else:
                        performance['% 2Y'] = None
                else:
                    performance['% 2Y'] = None
                
                performance_data.append(performance)
            
            if performance_data:
                perf_df = pd.DataFrame(performance_data)
                column_order = ['Commodity', 'Latest Price', 'Latest Date', '% 1D', '% 1W', '% 1M', '% 3M', '% 1Y', '% 2Y']
                perf_df = perf_df[[c for c in column_order if c in perf_df.columns]].copy()
                
                # Format columns via Styler to keep numeric values for conditional coloring
                # Use SchemaRegistry for formatting
                def format_price(val: float) -> str:
                    if pd.isna(val):
                        return "N/A"
                    return schema_registry.format_price(float(val), include_currency=False)

                def format_date(val: str) -> str:
                    return val if val else "N/A"
                    
                def format_pct(val: float) -> str:
                    if pd.isna(val):
                        return "N/A"
                    formatted, _ = schema_registry.format_percentage(val, show_sign=True, color=False)
                    return formatted

                def pct_color(val: float) -> str:
                    if pd.isna(val):
                        return ""
                    if val > 0:
                        return "color:#1B5E20;font-weight:600;"
                    if val < 0:
                        return "color:#B71C1C;font-weight:600;"
                    return "color:#424242;font-weight:600;"

                pct_cols = [c for c in ['% 1D', '% 1W', '% 1M', '% 3M', '% 1Y', '% 2Y'] if c in perf_df.columns]
                
                # Apply formatting + coloring (English number format, Vietnamese color hint in caption)
                styler = (
                    perf_df.style
                    .format({col: format_price for col in ['Latest Price'] if col in perf_df.columns})
                    .format({col: format_date for col in ['Latest Date'] if col in perf_df.columns})
                    .format({col: format_pct for col in pct_cols})
                    .applymap(pct_color, subset=pct_cols)
                )
                
                st.dataframe(
                    styler,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Show note
                st.caption("📝 Performance % = (Latest Price / Previous Price) - 1. Màu xanh = tăng, màu đỏ = giảm.")
        
        
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu commodity: {e}")
        import traceback
        st.exception(e)


def _build_macro_latest_table(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Chuẩn hóa bảng latest value + delta cho macro datasets."""
    if df.empty or value_col not in df.columns:
        return pd.DataFrame()
    
    df_sorted = df.sort_values('date').copy()
    df_sorted['prev_value'] = df_sorted.groupby('rate_name')[value_col].shift(1)
    df_sorted['prev_date'] = df_sorted.groupby('rate_name')['date'].shift(1)
    
    idx = df_sorted.groupby('rate_name')['date'].idxmax()
    latest = df_sorted.loc[idx].copy()
    latest = latest.rename(columns={value_col: 'latest_value'})
    latest['delta'] = latest['latest_value'] - latest['prev_value']
    latest['delta_pct'] = np.where(
        (latest['prev_value'].notna()) & (latest['prev_value'] != 0),
        latest['delta'] / latest['prev_value'] * 100,
        np.nan
    )
    
    return latest[['rate_name', 'unit', 'date', 'latest_value', 'delta', 'delta_pct']].sort_values('rate_name')


def _format_macro_value(val: float, decimals: int = 2) -> str:
    if pd.isna(val):
        return "N/A"
    return f"{val:,.{decimals}f}"


def _format_macro_delta(val: float, suffix: str = "") -> str:
    if pd.isna(val):
        return "N/A"
    return f"{val:+,.4f}{suffix}" if abs(val) < 1 else f"{val:+,.2f}{suffix}"


def _render_macro_section(
    df: pd.DataFrame,
    dataset_label: str,
    value_col: str,
    multiselect_key: str,
    decimals: int = 3,
) -> None:
    if df.empty:
        st.warning(f"⚠️ Chưa có dữ liệu cho nhóm '{dataset_label}'. Vui lòng chạy macro update.")
        return
    
    df = df.copy()
    df = df.sort_values('date')
    available_series = sorted(df['rate_name'].dropna().unique().tolist())
    default_selection = available_series[: min(3, len(available_series))]
    
    # Automatically select all available indicators
    selected = available_series
    
    if not selected:
        st.info("Không có dữ liệu để hiển thị.")
        return
    
    # Time range selector for chart view
    range_options = {
        "1M": 30,
        "3M": 90,
        "6M": 180,
        "1Y": 365,
        "3Y": 365 * 3,
        "All": None,
    }
    range_label = st.selectbox(
        "Khoảng thời gian biểu đồ",
        list(range_options.keys()),
        index=2,
        key=f"{multiselect_key}_range",
    )
    days = range_options[range_label]
    if days:
        cutoff = df['date'].max() - pd.Timedelta(days=days)
        plot_df = df[df['date'] >= cutoff].copy()
    else:
        plot_df = df.copy()
    if plot_df.empty:
        st.warning("Không có dữ liệu trong khoảng thời gian đã chọn. Đang hiển thị toàn bộ lịch sử.")
        plot_df = df.copy()
    
    latest_table = _build_macro_latest_table(df, value_col)
    
    fig = go.Figure()
    for name in selected:
        series = plot_df[plot_df['rate_name'] == name].sort_values('date')
        if series.empty:
            continue
        fig.add_trace(go.Scatter(
            x=series['date'],
            y=series[value_col],
            mode='lines',
            name=name,
            line=dict(shape='spline', smoothing=0.8, width=2),
            hovertemplate='%{x|%Y-%m-%d}: %{y:,.4f}<extra></extra>',
        ))
    
    fig.update_layout(
        **get_plotly_font_config(),
        height=420,
        hovermode='x unified',
        margin=dict(l=0, r=0, t=40, b=40),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        xaxis=dict(title="Date"),
        yaxis=dict(title="Value"),
        title=f"{dataset_label} — Historical Trend",
    )
    
    st.plotly_chart(fig, config=PLOTLY_CONFIG, use_container_width=True, key="plotly_chart_1716")
    
    if not latest_table.empty:
        display_table = latest_table.copy()
        display_table['latest_value'] = display_table['latest_value'].apply(lambda v: _format_macro_value(v, decimals))
        display_table['delta'] = display_table['delta'].apply(lambda v: _format_macro_delta(v))
        display_table['delta_pct'] = display_table['delta_pct'].apply(lambda v: _format_macro_delta(v, suffix="%"))
        display_table['date'] = display_table['date'].dt.strftime('%Y-%m-%d')
        st.dataframe(
            display_table.rename(columns={
                'rate_name': 'Indicator',
                'unit': 'Unit',
                'date': 'Latest Date',
                'latest_value': 'Latest',
                'delta': 'Δ (vs prev)',
                'delta_pct': 'Δ %',
            }),
            hide_index=True,
            use_container_width=True,
        )


def render_macro_dashboard():
    """Hiển thị tab chỉ số vĩ mô (FX, rates, bonds)."""
    st.subheader("Macro Indicators Reference")
    
    # Define groups of symbols
    macro_groups = {
        "💱 Tỷ giá ngoại hối": [
            'ty_gia_usd_trung_tam', 'ty_gia_tran', 'ty_gia_san', 
            'ty_gia_usd_nhtm_ban_ra', 'ty_gia_usd_tu_do_ban_ra'
        ],
        "🏦 Lãi suất liên ngân hàng": [
            'ls_qua_dem_lien_ngan_hang', 'ls_lien_ngan_hang_ky_han_1_tuan', 
            'ls_lien_ngan_hang_ky_han_2_tuan'
        ],
        "💰 Lãi suất huy động NHTM lớn": [
            'ls_huy_dong_1_3_thang', 'ls_huy_dong_6_9_thang', 'ls_huy_dong_13_thang'
        ],
        "📉 Trái phiếu Chính phủ VN 5Y": [
            'vn_gov_bond_5y'
        ],
    }
    
    dataset_label = st.selectbox("Chọn nhóm dữ liệu vĩ mô", list(macro_groups.keys()))
    selected_symbols = macro_groups[dataset_label]
    
    # Load data using MacroCommodityLoader
    loader = MacroCommodityLoader()
    df_unified = loader.load_data()
    
    if df_unified.empty:
        st.warning("Chưa có dữ liệu macro.")
        return
        
    # Filter for selected symbols
    df = df_unified[df_unified['symbol'].isin(selected_symbols)].copy()
    
    if df.empty:
        st.warning("Chưa có dữ liệu cho nhóm này.")
        return
        
    # Rename columns to match expected format for _render_macro_section
    # Expected: rate_name, value, date, unit
    df = df.rename(columns={'name': 'rate_name', 'symbol': 'symbol_id'})
    
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    title_col, info_col = st.columns([1, 0.35])
    with title_col:
        st.markdown(f"**{dataset_label}**")
    with info_col:
        if isinstance(min_date, pd.Timestamp):
            min_d_str = min_date.strftime('%Y-%m-%d')
            max_d_str = max_date.strftime('%Y-%m-%d')
        else:
            min_d_str = str(min_date)
            max_d_str = str(max_date)
            
        info_col.markdown(
            f"<div style='text-align:right;color:#6c757d;font-size:0.85rem;'>"
            f"{min_d_str} → {max_d_str}"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Determine decimals based on group
    decimals = 3 if "Trái phiếu" in dataset_label else 2

    _render_macro_section(
        df=df,
        dataset_label=dataset_label,
        value_col="value",
        multiselect_key=dataset_label, # Use label as key since path is not unique anymore
        decimals=decimals,
    )


def render_technical_dashboard():
    # Render Top Navigation
    render_top_nav()

    st.set_page_config(layout="wide", page_title="Technical Dashboard", page_icon="📉")

    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 MA Screening",
        "📈 Market Breadth",
        "💰 VN-Index PE",
        "📦 Commodity Prices",
        "🌐 Macro Indicators",
    ])
    
    with tab1:
        render_ma_screening_table()
    
    with tab2:
        render_market_breadth_chart()
        render_sector_breadth_table()
    
    with tab3:
        render_vnindex_pe_chart()
    
    with tab4:
        render_commodity_chart()
    
    with tab5:
        render_macro_dashboard()

if __name__ == "__main__":
    render_technical_dashboard()


