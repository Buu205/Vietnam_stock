"""
BSC Forecast Dashboard - Senior UI Engineer Version
Clean, professional table display without filters
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Add project root to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
streamlit_app_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(streamlit_app_dir)

# Add both paths for compatibility
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if streamlit_app_dir not in sys.path:
    sys.path.insert(0, streamlit_app_dir)

# Try different import paths for compatibility
try:
    from WEBAPP.domains.forecast.data_loading_forecast_csv import (
        load_comprehensive_forecast_data_csv, 
        check_csv_data_freshness
    )
    from WEBAPP.core.formatters import format_currency, format_percentage, format_ratio
    from WEBAPP.layout.navigation import render_top_nav
    from WEBAPP.core.utils import load_custom_css
except (ImportError, KeyError):
    # Fallback for Streamlit Cloud
    try:
        from domains.forecast.data_loading_forecast_csv import (
            load_comprehensive_forecast_data_csv, 
            check_csv_data_freshness
        )
        from core.formatters import format_currency, format_percentage, format_ratio
        from layout.navigation import render_top_nav
        from core.utils import load_custom_css
    except (ImportError, KeyError):
        # Final fallback - define functions locally
        def load_comprehensive_forecast_data_csv():
            import pandas as pd
            st.error("❌ Không thể tải dữ liệu forecast. Vui lòng kiểm tra file CSV.")
            return pd.DataFrame()
        
        def check_csv_data_freshness():
            return {"is_fresh": False, "message": "Không thể kiểm tra dữ liệu"}
        
        def format_currency(value):
            return f"{value:,.0f}" if pd.notna(value) else "N/A"
        
        def format_percentage(value):
            return f"{value:.1f}%" if pd.notna(value) else "N/A"
        
        def format_ratio(value):
            return f"{value:.2f}" if pd.notna(value) else "N/A"
        
        # Fallback for navigation
        def render_top_nav():
            pass
        
        def load_custom_css():
            pass

# Load custom font CSS once at import time (align with other pages)
try:
    load_custom_css()
except Exception:
    pass

# ============================================================================
# UI STYLING
# ============================================================================

def inject_custom_css():
    """Inject enhanced CSS for professional table display - Cached"""
    # Only inject CSS once per session
    if 'css_injected' not in st.session_state:
        st.markdown("""
        <style>
        /* ===== GLOBAL TABLE STYLING ===== */
        [data-testid="stDataFrame"] {
            font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 14px;
        }
        
        /* ===== TABLE CONTAINER ===== */
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border: 1px solid #e1e4e8;
        }
        
        /* ===== STICKY HEADER ===== */
        [data-testid="stDataFrame"] thead {
            position: sticky;
            top: 0;
            z-index: 100;
            background-color: #f6f8fa;
        }
        
        [data-testid="stDataFrame"] th {
            font-size: 13px !important;
            font-weight: 600 !important;
            padding: 10px 12px !important;
            background-color: #f6f8fa !important;
            color: #24292f !important;
            text-align: center !important;
            border-bottom: 2px solid #d0d7de !important;
            white-space: nowrap;
        }
        
        /* ===== TABLE BODY - ZEBRA STRIPING ===== */
        [data-testid="stDataFrame"] tbody tr:nth-child(even) {
            background-color: #f9fafb;
        }
        
        [data-testid="stDataFrame"] tbody tr:nth-child(odd) {
            background-color: #ffffff;
        }
        
        [data-testid="stDataFrame"] tbody tr:hover {
            background-color: #f0f6ff !important;
            transition: background-color 0.15s ease;
        }
        
        [data-testid="stDataFrame"] td {
            font-size: 13px !important;
            padding: 8px 12px !important;
            line-height: 1.4 !important;
            color: #24292f;
            border-bottom: 1px solid #eaeef2;
        }
        
        /* ===== PINNED SYMBOL COLUMN ===== */
        [data-testid="stDataFrame"] th:first-child,
        [data-testid="stDataFrame"] td:first-child {
            position: sticky !important;
            left: 0 !important;
            background-color: #ffffff !important;
            z-index: 50 !important;
            border-right: 2px solid #d0d7de !important;
            font-weight: 600 !important;
        }
        
        [data-testid="stDataFrame"] thead th:first-child {
            background-color: #f6f8fa !important;
            z-index: 101 !important;
        }
        
        /* ===== NUMBER ALIGNMENT ===== */
        /* Symbol, Rating - left align */
        [data-testid="stDataFrame"] td:nth-child(1),
        [data-testid="stDataFrame"] td:nth-child(2) {
            text-align: left !important;
            font-weight: 500;
        }
        
        /* All other columns - right align */
        [data-testid="stDataFrame"] td:nth-child(n+3) {
            text-align: right !important;
            font-variant-numeric: tabular-nums;
        }
        
        /* ===== HYBRID COLOR GROUPS ===== */
        /* GROUP 1: IDENTITY & VALUATION (Blue) - Columns 1-6 */
        /* Symbol(1), Rating(2), Price(3), Target(4), Up%(5), MCap(6) */
        
        [data-testid="stDataFrame"] th:nth-child(-n+6),
        [data-testid="stDataFrame"] td:nth-child(-n+6) {
            background-color: #e3f2fd !important;
        }
        
        /* Thick separator after MCap (column 6) */
        [data-testid="stDataFrame"] th:nth-child(6),
        [data-testid="stDataFrame"] td:nth-child(6) {
            border-right: 3px solid #90caf9 !important;
        }
        
        /* GROUP 2: 2025 FORECAST (Green) - Columns 7-14 */
        /* Rev(7), RG%(8), NPAT(9), NG%(10), ROE(11), ROA(12), PE(13), PB(14) */
        
        [data-testid="stDataFrame"] th:nth-child(n+7):nth-child(-n+14),
        [data-testid="stDataFrame"] td:nth-child(n+7):nth-child(-n+14) {
            background-color: #e8f5e9 !important;
        }
        
        /* NPAT 2025 (column 9) - Highlighted */
        [data-testid="stDataFrame"] th:nth-child(9),
        [data-testid="stDataFrame"] td:nth-child(9) {
            background-color: #c8e6c9 !important;
            font-weight: 600 !important;
        }
        
        /* NG% 2025 (column 10) - Highlighted */
        [data-testid="stDataFrame"] th:nth-child(10),
        [data-testid="stDataFrame"] td:nth-child(10) {
            background-color: #c8e6c9 !important;
            font-weight: 600 !important;
        }
        
        /* Thick separator after PB (column 14) */
        [data-testid="stDataFrame"] th:nth-child(14),
        [data-testid="stDataFrame"] td:nth-child(14) {
            border-right: 3px solid #81c784 !important;
        }
        
        /* GROUP 3: 2026 FORECAST (Yellow) - Columns 15-22 */
        /* Rev(15), RG%(16), NPAT(17), NG%(18), ROE(19), ROA(20), PE(21), PB(22) */
        
        [data-testid="stDataFrame"] th:nth-child(n+15):nth-child(-n+22),
        [data-testid="stDataFrame"] td:nth-child(n+15):nth-child(-n+22) {
            background-color: #fff9c4 !important;
        }
        
        /* NPAT 2026 (column 17) - Highlighted */
        [data-testid="stDataFrame"] th:nth-child(17),
        [data-testid="stDataFrame"] td:nth-child(17) {
            background-color: #ffe0b2 !important;
            font-weight: 600 !important;
        }
        
        /* NG% 2026 (column 18) - Highlighted */
        [data-testid="stDataFrame"] th:nth-child(18),
        [data-testid="stDataFrame"] td:nth-child(18) {
            background-color: #ffe0b2 !important;
            font-weight: 600 !important;
        }
        
        /* ===== HOVER EFFECTS ===== */
        /* Blue group hover */
        [data-testid="stDataFrame"] tbody tr:hover td:nth-child(-n+6) {
            background-color: #bbdefb !important;
        }
        
        /* Green group hover */
        [data-testid="stDataFrame"] tbody tr:hover td:nth-child(n+7):nth-child(-n+14) {
            background-color: #c8e6c9 !important;
        }
        
        /* Green highlights hover (darker) */
        [data-testid="stDataFrame"] tbody tr:hover td:nth-child(9),
        [data-testid="stDataFrame"] tbody tr:hover td:nth-child(10) {
            background-color: #a5d6a7 !important;
        }
        
        /* Yellow group hover */
        [data-testid="stDataFrame"] tbody tr:hover td:nth-child(n+15):nth-child(-n+22) {
            background-color: #fff59d !important;
        }
        
        /* Yellow highlights hover (darker) */
        [data-testid="stDataFrame"] tbody tr:hover td:nth-child(17),
        [data-testid="stDataFrame"] tbody tr:hover td:nth-child(18) {
            background-color: #ffcc80 !important;
        }
        
        /* ===== SCROLLBAR STYLING ===== */
        [data-testid="stDataFrame"]::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        [data-testid="stDataFrame"]::-webkit-scrollbar-track {
            background: #f1f3f5;
            border-radius: 5px;
        }
        
        [data-testid="stDataFrame"]::-webkit-scrollbar-thumb {
            background: #adb5bd;
            border-radius: 5px;
        }
        
        [data-testid="stDataFrame"]::-webkit-scrollbar-thumb:hover {
            background: #868e96;
        }
        </style>
        """, unsafe_allow_html=True)
        st.session_state.css_injected = True


# ============================================================================
# DATA PREPARATION
# ============================================================================

# @st.cache_data(ttl=3600, max_entries=8)  # Cache disabled due to Series hash error
def prepare_display_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare dataframe for display with proper formatting
    Format numbers with comma separators using custom formatters
    Convert to strings for display (loses sorting capability but has comma)
    """
    display_df = df.copy()
    
    # Define column order - HYBRID DESIGN with 3 groups
    # GROUP 1: Identity & Valuation (Blue)
    # GROUP 2: 2025 Forecast (Green)  
    # GROUP 3: 2026 Forecast (Yellow)
    columns_order = [
        # GROUP 1: Identity & Valuation (6 columns)
        'symbol', 'recommendation', 'current_price', 'target_price', 'upside_pct', 'market_cap',
        
        # GROUP 2: 2025 Forecast (8 columns)
        '2025_rev', 'rev_gr_25', '2025_npat', 'npat_gr_25',
        'roe_2025', 'roa_2025', 'pe_fwd_2025', 'pb_fwd_2025',
        
        # GROUP 3: 2026 Forecast (8 columns)
        '2026_rev', 'rev_gr_26', '2026_npat', 'npat_gr_26',
        'roe_2026', 'roa_2026', 'pe_fwd_2026', 'pb_fwd_2026'
    ]
    
    # Keep only available columns
    available_columns = [col for col in columns_order if col in display_df.columns]
    display_df = display_df[available_columns]
    
    # Rename columns to English short names (HYBRID APPROACH)
    column_renames = {
        'symbol': 'symbol',
        'recommendation': 'rating',
        'current_price': 'price',
        'target_price': 'target',
        'upside_pct': 'up_pct',
        'market_cap': 'mcap',
        
        # 2025
        '2025_rev': 'rev_25',
        'rev_gr_25': 'rg_25',
        '2025_npat': 'npat_25',
        'npat_gr_25': 'ng_25',
        'roe_2025': 'roe_25',
        'roa_2025': 'roa_25',
        'pe_fwd_2025': 'pe_25',
        'pb_fwd_2025': 'pb_25',
        
        # 2026
        '2026_rev': 'rev_26',
        'rev_gr_26': 'rg_26',
        '2026_npat': 'npat_26',
        'npat_gr_26': 'ng_26',
        'roe_2026': 'roe_26',
        'roa_2026': 'roa_26',
        'pe_fwd_2026': 'pe_26',
        'pb_fwd_2026': 'pb_26'
    }
    
    # Apply renames only for existing columns
    renames_to_apply = {old: new for old, new in column_renames.items() if old in display_df.columns}
    display_df = display_df.rename(columns=renames_to_apply)
    
    # ===== RECALCULATE RATING BASED ON UPSIDE_PCT =====
    # Override rating column with fresh calculation based on upside_pct
    if 'up_pct' in display_df.columns:
        def calculate_rating(upside_pct):
            try:
                if pd.isna(upside_pct) or upside_pct is None:
                    return "N/A"
                # Ensure upside_pct is a scalar, not Series
                if hasattr(upside_pct, 'iloc'):
                    upside_pct = upside_pct.iloc[0] if len(upside_pct) > 0 else None
                if pd.isna(upside_pct) or upside_pct is None:
                    return "N/A"
                
                upside_pct = float(upside_pct)
                if upside_pct >= 20:
                    return "🔥 STRONG BUY"
                elif upside_pct >= 10:
                    return "🟢 BUY"
                elif upside_pct <= -20:
                    return "🔥 STRONG SELL"
                elif upside_pct <= -10:
                    return "🔴 SELL"
                else:  # -10% < upside_pct < 10%
                    return "🟡 HOLD"
            except Exception:
                return "N/A"
        
        display_df['rating'] = display_df['up_pct'].apply(calculate_rating)
    
    # Format columns with comma separators using custom formatters
    # Currency columns (prices, revenue, NPAT, MCap) - with comma separators
    currency_cols = ['price', 'target', 'mcap', 'rev_25', 'npat_25', 'rev_26', 'npat_26']
    for col in currency_cols:
        if col in display_df.columns:
            def format_currency_safe(x):
                try:
                    if pd.isna(x) or x is None:
                        return "N/A"
                    # Ensure x is a scalar, not Series
                    if hasattr(x, 'iloc'):
                        x = x.iloc[0] if len(x) > 0 else None
                    if pd.isna(x) or x is None:
                        return "N/A"
                    return format_currency(float(x))
                except Exception:
                    return "N/A"
            display_df[col] = display_df[col].apply(format_currency_safe)
    
    # Percentage columns (growth, upside) - 1 decimal
    percentage_cols = ['up_pct', 'rg_25', 'ng_25', 'rg_26', 'ng_26']
    for col in percentage_cols:
        if col in display_df.columns:
            def format_percentage_safe(x):
                try:
                    if pd.isna(x) or x is None:
                        return "N/A"
                    # Ensure x is a scalar, not Series
                    if hasattr(x, 'iloc'):
                        x = x.iloc[0] if len(x) > 0 else None
                    if pd.isna(x) or x is None:
                        return "N/A"
                    return f"{float(x):.1f}%"
                except Exception:
                    return "N/A"
            display_df[col] = display_df[col].apply(format_percentage_safe)
    
    # Ratio columns (PE, PB, ROE, ROA) - 2 decimals
    ratio_cols = ['roe_25', 'roa_25', 'pe_25', 'pb_25', 'roe_26', 'roa_26', 'pe_26', 'pb_26']
    for col in ratio_cols:
        if col in display_df.columns:
            def format_ratio_safe(x):
                try:
                    if pd.isna(x) or x is None:
                        return "N/A"
                    # Ensure x is a scalar, not Series
                    if hasattr(x, 'iloc'):
                        x = x.iloc[0] if len(x) > 0 else None
                    if pd.isna(x) or x is None:
                        return "N/A"
                    return f"{float(x):.2f}"
                except Exception:
                    return "N/A"
            display_df[col] = display_df[col].apply(format_ratio_safe)
    
    return display_df


# @st.cache_data(ttl=86400, max_entries=1)  # Cache disabled due to Series hash error
def create_column_config() -> dict:
    """
    Create column configuration - HYBRID DESIGN
    3 Groups: Identity (Blue) | 2025 Forecast (Green) | 2026 Forecast (Yellow)
    All English column names
    """
    return {
        # ===== GROUP 1: IDENTITY & VALUATION (Blue) =====
        "symbol": st.column_config.TextColumn(
            "Symbol",
            width="small",
            help="Stock ticker",
            pinned=True
        ),
        "rating": st.column_config.TextColumn(
            "Rating",
            width="small",
            help="Recommendation: 🔥STRONG BUY (Up≥20%) | 🟢BUY (10-20%) | 🟡HOLD (-10~10%) | 🔴SELL (-20~-10%) | 🔥STRONG SELL (Up≤-20%)"
        ),
        "price": st.column_config.TextColumn(
            "Price",
            width="small",
            help="Current price (VND)"
        ),
        "target": st.column_config.TextColumn(
            "Target",
            width="small",
            help="Target price (VND)"
        ),
        "up_pct": st.column_config.TextColumn(
            "Up%",
            width="small",
            help="Upside potential %"
        ),
        "mcap": st.column_config.TextColumn(
            "MCap",
            width="small",
            help="Market Cap (T VND)"
        ),
        
        # ===== GROUP 2: 2025 FORECAST (Green) =====
        "rev_25": st.column_config.TextColumn(
            "Rev",
            width="small",
            help="Revenue 2025 (T VND)"
        ),
        "rg_25": st.column_config.TextColumn(
            "RG%",
            width="small",
            help="Revenue Growth % vs 2024"
        ),
        "npat_25": st.column_config.TextColumn(
            "NPAT",
            width="small",
            help="Net Profit 2025 (T VND)"
        ),
        "ng_25": st.column_config.TextColumn(
            "NG%",
            width="small",
            help="NPAT Growth % vs 2024"
        ),
        "roe_25": st.column_config.TextColumn(
            "ROE",
            width="small",
            help="ROE 2025 (%)"
        ),
        "roa_25": st.column_config.TextColumn(
            "ROA",
            width="small",
            help="ROA 2025 (%)"
        ),
        "pe_25": st.column_config.TextColumn(
            "PE",
            width="small",
            help="PE Forward 2025"
        ),
        "pb_25": st.column_config.TextColumn(
            "PB",
            width="small",
            help="PB Forward 2025"
        ),
        
        # ===== GROUP 3: 2026 FORECAST (Yellow) =====
        "rev_26": st.column_config.TextColumn(
            "Rev",
            width="small",
            help="Revenue 2026 (T VND)"
        ),
        "rg_26": st.column_config.TextColumn(
            "RG%",
            width="small",
            help="Revenue Growth % vs 2025"
        ),
        "npat_26": st.column_config.TextColumn(
            "NPAT",
            width="small",
            help="Net Profit 2026 (T VND)"
        ),
        "ng_26": st.column_config.TextColumn(
            "NG%",
            width="small",
            help="NPAT Growth % vs 2025"
        ),
        "roe_26": st.column_config.TextColumn(
            "ROE",
            width="small",
            help="ROE 2026 (%)"
        ),
        "roa_26": st.column_config.TextColumn(
            "ROA",
            width="small",
            help="ROA 2026 (%)"
        ),
        "pe_26": st.column_config.TextColumn(
            "PE",
            width="small",
            help="PE Forward 2026"
        ),
        "pb_26": st.column_config.TextColumn(
            "PB",
            width="small",
            help="PB Forward 2026"
        ),
    }


# ============================================================================
# RENDERING FUNCTIONS
# ============================================================================

def render_data_status(freshness_info: dict) -> bool:
    """Render data freshness status, return False if data missing"""
    if freshness_info['status'] == 'missing':
        st.error(f"❌ {freshness_info['message']}")
        st.code("python3 run_bsc_auto_update.py", language="bash")
        return False
    elif freshness_info['status'] == 'old':
        st.warning(f"⚠️ {freshness_info['message']}")
    elif freshness_info['status'] == 'stale':
        st.info(f"ℹ️ {freshness_info['message']}")
    
    # Status caption
    status_messages = {
        'fresh': "📅 Dữ liệu mới nhất",
        'stale': "📅 Dữ liệu hơi cũ - nên cập nhật",
        'old': "📅 Dữ liệu cũ - cần cập nhật"
    }
    st.caption(status_messages.get(freshness_info['status'], "📅 Trạng thái không xác định"))
    return True




def render_recommendation_breakdown(df: pd.DataFrame):
    """
    Render detailed breakdown of stocks by recommendation
    
    VN: Hiển thị chi tiết phân loại cổ phiếu theo khuyến nghị
    - Danh sách mã BUY với upside% cao nhất
    - Danh sách mã HOLD
    - Danh sách mã SELL
    """
    if 'recommendation' not in df.columns or 'upside_pct' not in df.columns:
        return
    
    st.markdown("### 📋 Phân Loại Theo Khuyến Nghị")
    st.caption("Dựa trên % chênh lệch giá mục tiêu so với giá hiện tại (Upside %)")
    
    # Kiểm tra phân loại dựa trên upside_pct
    if st.checkbox("🔍 Kiểm tra phân loại"):
        st.write("**Kiểm tra phân loại dựa trên upside_pct:**")
        
        # Tạo dataframe kiểm tra
        check_df = df[['symbol', 'upside_pct', 'recommendation']].copy()
        check_df = check_df.sort_values('upside_pct', ascending=False)
        
        # Kiểm tra từng nhóm
        strong_buy_check = check_df[check_df['upside_pct'] >= 20]
        buy_check = check_df[(check_df['upside_pct'] >= 10) & (check_df['upside_pct'] < 20)]
        hold_check = check_df[(check_df['upside_pct'] > -10) & (check_df['upside_pct'] < 10)]
        sell_check = check_df[(check_df['upside_pct'] > -20) & (check_df['upside_pct'] <= -10)]
        strong_sell_check = check_df[check_df['upside_pct'] <= -20]
        
        # Hiển thị kết quả
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"🔥 **STRONG BUY (≥20%):** {len(strong_buy_check)} mã")
            if not strong_buy_check.empty:
                st.dataframe(strong_buy_check.head(10), hide_index=True)
            
            st.write(f"🟢 **BUY (10-20%):** {len(buy_check)} mã")
            if not buy_check.empty:
                st.dataframe(buy_check.head(10), hide_index=True)
        
        with col2:
            st.write(f"🟡 **HOLD (-10% đến 10%):** {len(hold_check)} mã")
            if not hold_check.empty:
                st.dataframe(hold_check.head(10), hide_index=True)
            
            st.write(f"🔴 **SELL (-20% đến -10%):** {len(sell_check)} mã")
            if not sell_check.empty:
                st.dataframe(sell_check.head(10), hide_index=True)
            
            st.write(f"🔥 **STRONG SELL (≤-20%):** {len(strong_sell_check)} mã")
            if not strong_sell_check.empty:
                st.dataframe(strong_sell_check.head(10), hide_index=True)
        
        # Tổng kết
        total = len(check_df)
        st.write(f"**Tổng kết:** {total} mã")
        st.write(f"- Strong BUY: {len(strong_buy_check)} ({len(strong_buy_check)/total*100:.1f}%)")
        st.write(f"- BUY: {len(buy_check)} ({len(buy_check)/total*100:.1f}%)")
        st.write(f"- HOLD: {len(hold_check)} ({len(hold_check)/total*100:.1f}%)")
        st.write(f"- SELL: {len(sell_check)} ({len(sell_check)/total*100:.1f}%)")
        st.write(f"- Strong SELL: {len(strong_sell_check)} ({len(strong_sell_check)/total*100:.1f}%)")
    
    # Tạo 5 columns cho STRONG BUY, BUY, HOLD, SELL, STRONG SELL
    col_strong_buy, col_buy, col_hold, col_sell, col_strong_sell = st.columns(5)
    
    # ===== STRONG BUY STOCKS (upside >= 20%) =====
    with col_strong_buy:
        st.markdown("#### 🔥 STRONG BUY (Upside ≥ 20%)")
        # Phân loại dựa trên upside_pct trực tiếp, không dựa vào recommendation
        strong_buy_stocks = df[df['upside_pct'] >= 20].copy()
        
        if not strong_buy_stocks.empty:
            # Sắp xếp theo upside% giảm dần (cao nhất trước)
            strong_buy_stocks_sorted = strong_buy_stocks.sort_values('upside_pct', ascending=False)
            
            st.success(f"**{len(strong_buy_stocks)} mã** cơ hội lớn")
            
            # Hiển thị top stocks
            display_cols = ['symbol', 'upside_pct', 'current_price', 'target_price']
            available_cols = [col for col in display_cols if col in strong_buy_stocks_sorted.columns]
            
            if available_cols:
                strong_buy_display = strong_buy_stocks_sorted[available_cols].head(15).copy()
                
                # Format for display
                if 'upside_pct' in strong_buy_display.columns:
                    strong_buy_display['upside_pct'] = strong_buy_display['upside_pct'].apply(
                        lambda x: f"+{x:.1f}%" if pd.notna(x) else "N/A"
                    )
                if 'current_price' in strong_buy_display.columns:
                    strong_buy_display['current_price'] = strong_buy_display['current_price'].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
                    )
                if 'target_price' in strong_buy_display.columns:
                    strong_buy_display['target_price'] = strong_buy_display['target_price'].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
                    )
                
                # Rename columns
                strong_buy_display.columns = ['Mã', 'Up%', 'Giá HT', 'Giá MT'] if len(available_cols) == 4 else strong_buy_display.columns
                
                st.dataframe(strong_buy_display, hide_index=True, height=300)
                
                # Stats
                avg_upside = strong_buy_stocks['upside_pct'].mean()
                max_upside = strong_buy_stocks['upside_pct'].max()
                st.caption(f"📊 Upside TB: +{avg_upside:.1f}% | Max: +{max_upside:.1f}%")
        else:
            st.info("Không có mã nào")
    
    # ===== BUY STOCKS (10% <= upside < 20%) =====
    with col_buy:
        st.markdown("#### 🟢 BUY (10% ≤ Up% < 20%)")
        # Phân loại dựa trên upside_pct trực tiếp
        buy_stocks = df[(df['upside_pct'] >= 10) & (df['upside_pct'] < 20)].copy()
        
        if not buy_stocks.empty:
            # Sắp xếp theo upside% giảm dần (cao nhất trước)
            buy_stocks_sorted = buy_stocks.sort_values('upside_pct', ascending=False)
            
            st.success(f"**{len(buy_stocks)} mã** đáng mua")
            
            # Hiển thị top stocks
            display_cols = ['symbol', 'upside_pct', 'current_price', 'target_price']
            available_cols = [col for col in display_cols if col in buy_stocks_sorted.columns]
            
            if available_cols:
                buy_display = buy_stocks_sorted[available_cols].head(15).copy()
                
                # Format for display
                if 'upside_pct' in buy_display.columns:
                    buy_display['upside_pct'] = buy_display['upside_pct'].apply(
                        lambda x: f"+{x:.1f}%" if pd.notna(x) else "N/A"
                    )
                if 'current_price' in buy_display.columns:
                    buy_display['current_price'] = buy_display['current_price'].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
                    )
                if 'target_price' in buy_display.columns:
                    buy_display['target_price'] = buy_display['target_price'].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
                    )
                
                # Rename columns
                buy_display.columns = ['Mã', 'Up%', 'Giá HT', 'Giá MT'] if len(available_cols) == 4 else buy_display.columns
                
                st.dataframe(buy_display, hide_index=True, height=300)
                
                # Stats
                avg_upside = buy_stocks['upside_pct'].mean()
                max_upside = buy_stocks['upside_pct'].max()
                st.caption(f"📊 Upside TB: +{avg_upside:.1f}% | Max: +{max_upside:.1f}%")
        else:
            st.info("Không có mã nào")
    
    # ===== HOLD STOCKS (-10% < upside < 10%) =====
    with col_hold:
        st.markdown("#### 🟡 HOLD (-10% < Up% < 10%)")
        # Phân loại dựa trên upside_pct trực tiếp
        hold_stocks = df[(df['upside_pct'] > -10) & (df['upside_pct'] < 10)].copy()
        
        if not hold_stocks.empty:
            # Sắp xếp theo upside% giảm dần
            hold_stocks_sorted = hold_stocks.sort_values('upside_pct', ascending=False)
            
            st.warning(f"**{len(hold_stocks)} mã** nên giữ")
            
            # Hiển thị stocks
            display_cols = ['symbol', 'upside_pct', 'current_price', 'target_price']
            available_cols = [col for col in display_cols if col in hold_stocks_sorted.columns]
            
            if available_cols:
                hold_display = hold_stocks_sorted[available_cols].head(15).copy()
                
                # Format for display
                if 'upside_pct' in hold_display.columns:
                    hold_display['upside_pct'] = hold_display['upside_pct'].apply(
                        lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A"
                    )
                if 'current_price' in hold_display.columns:
                    hold_display['current_price'] = hold_display['current_price'].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
                    )
                if 'target_price' in hold_display.columns:
                    hold_display['target_price'] = hold_display['target_price'].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
                    )
                
                # Rename columns
                hold_display.columns = ['Mã', 'Up%', 'Giá HT', 'Giá MT'] if len(available_cols) == 4 else hold_display.columns
                
                st.dataframe(hold_display, hide_index=True, height=300)
                
                # Stats
                avg_upside = hold_stocks['upside_pct'].mean()
                st.caption(f"📊 Upside TB: {avg_upside:+.1f}%")
        else:
            st.info("Không có mã nào")
    
    # ===== SELL STOCKS (-20% < upside <= -10%) =====
    with col_sell:
        st.markdown("#### 🔴 SELL (-20% < Up% ≤ -10%)")
        # Phân loại dựa trên upside_pct trực tiếp
        sell_stocks = df[(df['upside_pct'] > -20) & (df['upside_pct'] <= -10)].copy()
        
        if not sell_stocks.empty:
            # Sắp xếp theo upside% tăng dần (âm nhất trước - overvalued nhất)
            sell_stocks_sorted = sell_stocks.sort_values('upside_pct', ascending=True)
            
            st.error(f"**{len(sell_stocks)} mã** nên bán")
            
            # Hiển thị stocks
            display_cols = ['symbol', 'upside_pct', 'current_price', 'target_price']
            available_cols = [col for col in display_cols if col in sell_stocks_sorted.columns]
            
            if available_cols:
                sell_display = sell_stocks_sorted[available_cols].head(15).copy()
                
                # Format for display
                if 'upside_pct' in sell_display.columns:
                    sell_display['upside_pct'] = sell_display['upside_pct'].apply(
                        lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
                    )
                if 'current_price' in sell_display.columns:
                    sell_display['current_price'] = sell_display['current_price'].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
                    )
                if 'target_price' in sell_display.columns:
                    sell_display['target_price'] = sell_display['target_price'].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
                    )
                
                # Rename columns
                sell_display.columns = ['Mã', 'Up%', 'Giá HT', 'Giá MT'] if len(available_cols) == 4 else sell_display.columns
                
                st.dataframe(sell_display, hide_index=True, height=300)
                
                # Stats
                avg_upside = sell_stocks['upside_pct'].mean()
                min_upside = sell_stocks['upside_pct'].min()
                st.caption(f"📊 Upside TB: {avg_upside:.1f}% | Min: {min_upside:.1f}%")
        else:
            st.info("Không có mã nào")
    
    # ===== STRONG SELL STOCKS (upside <= -20%) =====
    with col_strong_sell:
        st.markdown("#### 🔥 STRONG SELL (Up% ≤ -20%)")
        # Phân loại dựa trên upside_pct trực tiếp
        strong_sell_stocks = df[df['upside_pct'] <= -20].copy()
        
        if not strong_sell_stocks.empty:
            # Sắp xếp theo upside% tăng dần (âm nhất trước - overvalued nhất)
            strong_sell_stocks_sorted = strong_sell_stocks.sort_values('upside_pct', ascending=True)
            
            st.error(f"**{len(strong_sell_stocks)} mã** rủi ro lớn")
            
            # Hiển thị stocks
            display_cols = ['symbol', 'upside_pct', 'current_price', 'target_price']
            available_cols = [col for col in display_cols if col in strong_sell_stocks_sorted.columns]
            
            if available_cols:
                strong_sell_display = strong_sell_stocks_sorted[available_cols].head(15).copy()
                
                # Format for display
                if 'upside_pct' in strong_sell_display.columns:
                    strong_sell_display['upside_pct'] = strong_sell_display['upside_pct'].apply(
                        lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
                    )
                if 'current_price' in strong_sell_display.columns:
                    strong_sell_display['current_price'] = strong_sell_display['current_price'].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
                    )
                if 'target_price' in strong_sell_display.columns:
                    strong_sell_display['target_price'] = strong_sell_display['target_price'].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
                    )
                
                # Rename columns
                strong_sell_display.columns = ['Mã', 'Up%', 'Giá HT', 'Giá MT'] if len(available_cols) == 4 else strong_sell_display.columns
                
                st.dataframe(strong_sell_display, hide_index=True, height=300)
                
                # Stats
                avg_upside = strong_sell_stocks['upside_pct'].mean()
                min_upside = strong_sell_stocks['upside_pct'].min()
                st.caption(f"📊 Upside TB: {avg_upside:.1f}% | Min: {min_upside:.1f}%")
        else:
            st.info("Không có mã nào")


# @st.cache_data(ttl=1800, max_entries=4)  # Cache disabled due to Series hash error
def get_display_dataframe_and_config(df: pd.DataFrame) -> tuple:
    """
    Get display dataframe and column config - Cached for performance
    Returns: (display_df, available_config)
    """
    # Prepare display dataframe
    display_df = prepare_display_dataframe(df)
    
    # Get column configuration
    column_config = create_column_config()
    
    # Filter out non-existent columns from config
    available_config = {
        col: config 
        for col, config in column_config.items() 
        if col in display_df.columns
    }
    
    return display_df, available_config


def get_styled_dataframe(df: pd.DataFrame) -> tuple:
    """
    Get styled dataframe with column coloring - Not cached (Styler can't be pickled)
    Returns: (styler, available_config)
    """
    # Get cached display dataframe and config
    display_df, available_config = get_display_dataframe_and_config(df)
    
    # ===== Apply column coloring using pandas Styler (reliable in Streamlit) =====
    # Define groups (only keep existing columns to avoid Styler errors)
    def existing(cols: list[str]) -> list[str]:
        return [c for c in cols if c in display_df.columns]

    group1 = existing(['symbol', 'rating', 'price', 'target', 'up_pct', 'mcap'])
    group2 = existing(['rev_25', 'rg_25', 'npat_25', 'ng_25', 'roe_25', 'roa_25', 'pe_25', 'pb_25'])
    group3 = existing(['rev_26', 'rg_26', 'npat_26', 'ng_26', 'roe_26', 'roa_26', 'pe_26', 'pb_26'])

    styler = display_df.style
    if group1:
        styler = styler.set_properties(subset=group1, **{"background-color": "#e3f2fd"})
        # Alignments
        left_cols = existing(['symbol', 'rating'])
        if left_cols:
            styler = styler.set_properties(subset=left_cols, **{"text-align": "left", "font-weight": "500"})
        right_cols = [c for c in group1 if c not in left_cols]
        if right_cols:
            styler = styler.set_properties(subset=right_cols, **{"text-align": "right"})

    if group2:
        styler = styler.set_properties(subset=group2, **{"background-color": "#e8f5e9"})
        # Highlights for 2025
        hl_25 = existing(['npat_25', 'ng_25'])
        if hl_25:
            styler = styler.set_properties(subset=hl_25, **{"background-color": "#c8e6c9", "font-weight": "600"})
        styler = styler.set_properties(subset=group2, **{"text-align": "right"})

    if group3:
        styler = styler.set_properties(subset=group3, **{"background-color": "#fff9c4"})
        # Highlights for 2026
        hl_26 = existing(['npat_26', 'ng_26'])
        if hl_26:
            styler = styler.set_properties(subset=hl_26, **{"background-color": "#ffe0b2", "font-weight": "600"})
        styler = styler.set_properties(subset=group3, **{"text-align": "right"})

    return styler, available_config


@st.cache_data(ttl=3600, max_entries=8)
def load_npat_3q_2025(forecast_symbols: list) -> pd.DataFrame:
    """
    Load LNST luỹ kế 3 quý 2025 và LNST Q4/2024 cho các mã forecast
    - Company: từ company_financial_metrics.parquet (cột npatmi)
    - Bank: từ bank_financial_metrics.parquet (cột npatmi)
    - Security: từ security_full.parquet (METRIC_CODE = 'SIS_201')
    
    Args:
        forecast_symbols: List of symbols from forecast data
        
    Returns:
        DataFrame với các cột: symbol, npat_3q_2025, q4_2024_npat
    """
    try:
        from WEBAPP.core.data_paths import DataPaths
        from WEBAPP.core.utils import get_data_path
        
        # Normalize symbols to uppercase
        forecast_symbols_upper = [s.upper() for s in forecast_symbols]
        
        # Load company and bank fundamental data
        company_path = DataPaths.fundamental('company')
        bank_path = DataPaths.fundamental('bank')
        security_path = get_data_path('DATA/refined/fundamental/current/security_full.parquet')
        
        all_npat_data = []
        
        # Load company data
        if company_path.exists():
            company_df = pd.read_parquet(company_path)
            company_df['symbol'] = company_df['symbol'].str.upper()
            
            company_filtered = company_df[
                (company_df['symbol'].isin(forecast_symbols_upper)) &
                (company_df['year'] == 2025) &
                (company_df['quarter'].isin([1, 2, 3])) &
                (company_df['freq_code'] == 'Q')
            ].copy()
            
            company_q4_filtered = company_df[
                (company_df['symbol'].isin(forecast_symbols_upper)) &
                (company_df['year'] == 2024) &
                (company_df['quarter'] == 4) &
                (company_df['freq_code'] == 'Q')
            ].copy()
            
            company_npat = None
            if not company_filtered.empty:
                company_npat = company_filtered.groupby('symbol')['npatmi'].sum().reset_index()
                company_npat.columns = ['symbol', 'npat_3q_2025']
            
            company_q4 = None
            if not company_q4_filtered.empty:
                company_q4 = company_q4_filtered.groupby('symbol')['npatmi'].sum().reset_index()
                company_q4.columns = ['symbol', 'q4_2024_npat']
            
            if company_npat is not None or company_q4 is not None:
                company_data = pd.merge(
                    company_npat if company_npat is not None else pd.DataFrame(columns=['symbol', 'npat_3q_2025']),
                    company_q4 if company_q4 is not None else pd.DataFrame(columns=['symbol', 'q4_2024_npat']),
                    on='symbol',
                    how='outer'
                )
                all_npat_data.append(company_data)
        
        # Load bank data
        if bank_path.exists():
            bank_df = pd.read_parquet(bank_path)
            bank_df['symbol'] = bank_df['symbol'].str.upper()
            
            bank_filtered = bank_df[
                (bank_df['symbol'].isin(forecast_symbols_upper)) &
                (bank_df['year'] == 2025) &
                (bank_df['quarter'].isin([1, 2, 3])) &
                (bank_df['freq_code'] == 'Q')
            ].copy()
            
            bank_q4_filtered = bank_df[
                (bank_df['symbol'].isin(forecast_symbols_upper)) &
                (bank_df['year'] == 2024) &
                (bank_df['quarter'] == 4) &
                (bank_df['freq_code'] == 'Q')
            ].copy()
            
            bank_npat = None
            if not bank_filtered.empty:
                bank_npat = bank_filtered.groupby('symbol')['npatmi'].sum().reset_index()
                bank_npat.columns = ['symbol', 'npat_3q_2025']
            
            bank_q4 = None
            if not bank_q4_filtered.empty:
                bank_q4 = bank_q4_filtered.groupby('symbol')['npatmi'].sum().reset_index()
                bank_q4.columns = ['symbol', 'q4_2024_npat']
            
            if bank_npat is not None or bank_q4 is not None:
                bank_data = pd.merge(
                    bank_npat if bank_npat is not None else pd.DataFrame(columns=['symbol', 'npat_3q_2025']),
                    bank_q4 if bank_q4 is not None else pd.DataFrame(columns=['symbol', 'q4_2024_npat']),
                    on='symbol',
                    how='outer'
                )
                all_npat_data.append(bank_data)
        
        # Load security data (HCM, SSI, VCI, etc.)
        if security_path.exists():
            security_df = pd.read_parquet(security_path)
            security_df['SECURITY_CODE'] = security_df['SECURITY_CODE'].str.upper()
            security_divisor = 1_000_000_000  # convert VND -> tỷ VND
            
            sec_filtered = security_df[
                (security_df['SECURITY_CODE'].isin(forecast_symbols_upper)) &
                (security_df['METRIC_CODE'] == 'SIS_201') &
                (security_df['YEAR'] == 2025) &
                (security_df['QUARTER'].isin([1, 2, 3])) &
                (security_df['FREQ_CODE'] == 'Q')
            ].copy()
            if not sec_filtered.empty:
                sec_filtered['METRIC_VALUE'] = sec_filtered['METRIC_VALUE'] / security_divisor
            
            sec_q4_filtered = security_df[
                (security_df['SECURITY_CODE'].isin(forecast_symbols_upper)) &
                (security_df['METRIC_CODE'] == 'SIS_201') &
                (security_df['YEAR'] == 2024) &
                (security_df['QUARTER'] == 4) &
                (security_df['FREQ_CODE'] == 'Q')
            ].copy()
            if not sec_q4_filtered.empty:
                sec_q4_filtered['METRIC_VALUE'] = sec_q4_filtered['METRIC_VALUE'] / security_divisor
            
            sec_npat = None
            if not sec_filtered.empty:
                sec_npat = sec_filtered.groupby('SECURITY_CODE')['METRIC_VALUE'].sum().reset_index()
                sec_npat.columns = ['symbol', 'npat_3q_2025']
            
            sec_q4 = None
            if not sec_q4_filtered.empty:
                sec_q4 = sec_q4_filtered.groupby('SECURITY_CODE')['METRIC_VALUE'].sum().reset_index()
                sec_q4.columns = ['symbol', 'q4_2024_npat']
            
            if sec_npat is not None or sec_q4 is not None:
                sec_data = pd.merge(
                    sec_npat if sec_npat is not None else pd.DataFrame(columns=['symbol', 'npat_3q_2025']),
                    sec_q4 if sec_q4 is not None else pd.DataFrame(columns=['symbol', 'q4_2024_npat']),
                    on='symbol',
                    how='outer'
                )
                all_npat_data.append(sec_data)
        
        # Combine all data (company, bank, security)
        if all_npat_data:
            result_df = pd.concat(all_npat_data, ignore_index=True)
            result_df = result_df.groupby('symbol').agg({
                'npat_3q_2025': lambda x: x.sum(min_count=1),
                'q4_2024_npat': lambda x: x.sum(min_count=1)
            }).reset_index()
            return result_df
        else:
            return pd.DataFrame(columns=['symbol', 'npat_3q_2025', 'q4_2024_npat'])
            
    except Exception as e:
        st.error(f"Error loading LNST 3Q 2025 data: {e}")
        return pd.DataFrame(columns=['symbol', 'npat_3q_2025', 'q4_2024_npat'])


def render_npat_achievement_table(forecast_df: pd.DataFrame):
    """
    Render bảng so sánh LNST dự phóng 2025 vs LNST luỹ kế 3 quý 2025
    
    Args:
        forecast_df: DataFrame từ forecast data với cột symbol và 2025_npat (hoặc npat_25)
    """
    if forecast_df.empty:
        return
    
    # Get forecast symbols
    forecast_symbols = forecast_df['symbol'].str.upper().unique().tolist()
    
    # Load LNST 3Q 2025
    with st.spinner("Đang tải dữ liệu LNST 3 quý 2025..."):
        npat_3q_df = load_npat_3q_2025(forecast_symbols)
    
    if npat_3q_df.empty:
        st.warning("⚠️ Không có dữ liệu LNST 3 quý 2025")
        return
    
    # Prepare forecast data - get NPAT 2025 column
    forecast_cols = forecast_df.columns.tolist()
    npat_2025_col = None
    
    # Try different column names
    for col in ['2025_npat', 'npat_25', 'NPAT_2025', 'npat_2025']:
        if col in forecast_cols:
            npat_2025_col = col
            break
    
    if npat_2025_col is None:
        st.warning("⚠️ Không tìm thấy cột LNST dự phóng 2025 trong forecast data")
        return
    
    # Create comparison table
    comparison_data = []
    
    for _, row in forecast_df.iterrows():
        symbol = str(row['symbol']).upper()
        npat_2025_forecast = row.get(npat_2025_col)
        
        # Get actual data
        npat_3q_row = npat_3q_df[npat_3q_df['symbol'] == symbol]
        npat_3q_2025 = npat_3q_row['npat_3q_2025'].iloc[0] if not npat_3q_row.empty else None
        q4_2024_actual = npat_3q_row['q4_2024_npat'].iloc[0] if not npat_3q_row.empty and 'q4_2024_npat' in npat_3q_row.columns else None
        
        # Calculate metrics
        achievement_pct = None
        q4_needed = None
        q4_vs_last_year = None
        
        if pd.notna(npat_2025_forecast) and npat_2025_forecast != 0:
            if pd.notna(npat_3q_2025):
                achievement_pct = (npat_3q_2025 / npat_2025_forecast) * 100
                q4_needed = npat_2025_forecast - npat_3q_2025
                if q4_needed < 0:
                    q4_needed = 0
            else:
                q4_needed = npat_2025_forecast
            
            if pd.notna(q4_needed) and pd.notna(q4_2024_actual) and q4_2024_actual != 0:
                q4_vs_last_year = (q4_needed / q4_2024_actual - 1) * 100
        
        comparison_data.append({
            'Mã': symbol,
            'LNST Luỹ Kế 3Q 2025': npat_3q_2025 if pd.notna(npat_3q_2025) else None,
            'LNST Dự Phóng 2025': npat_2025_forecast if pd.notna(npat_2025_forecast) else None,
            '% Hoàn Thành': achievement_pct if pd.notna(achievement_pct) else None,
            'LNST Q4 Cần Đạt': q4_needed if pd.notna(q4_needed) else None,
            '% So với Q4/2024': q4_vs_last_year if pd.notna(q4_vs_last_year) else None
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Format numbers
    if not comparison_df.empty:
        # Format currency columns
        for col in ['LNST Luỹ Kế 3Q 2025', 'LNST Dự Phóng 2025', 'LNST Q4 Cần Đạt']:
            comparison_df[col] = comparison_df[col].apply(
                lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
            )
        
        # Format percentage column
        comparison_df['% Hoàn Thành'] = comparison_df['% Hoàn Thành'].apply(
            lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
        )
        comparison_df['% So với Q4/2024'] = comparison_df['% So với Q4/2024'].apply(
            lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
        )
        
        # Sort by % Hoàn Thành descending
        comparison_df = comparison_df.sort_values(
            '% Hoàn Thành', 
            key=lambda x: pd.to_numeric(x.str.rstrip('%'), errors='coerce'),
            ascending=False,
            na_position='last'
        )
        
        # Display table
        st.markdown("### 📊 So Sánh LNST: Dự Phóng 2025 vs Luỹ Kế 3 Quý 2025")
        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Summary stats
        valid_achievement = comparison_df[comparison_df['% Hoàn Thành'] != 'N/A'].copy()
        if not valid_achievement.empty:
            valid_achievement['% Hoàn Thành_num'] = valid_achievement['% Hoàn Thành'].str.rstrip('%').astype(float)
            avg_achievement = valid_achievement['% Hoàn Thành_num'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tổng Số Mã", len(comparison_df))
            with col2:
                st.metric("Mã Có Dữ Liệu", len(valid_achievement))
            with col3:
                st.metric("% Hoàn Thành TB", f"{avg_achievement:.1f}%")


def render_forecast_table(df: pd.DataFrame):
    """
    Render main forecast table - HYBRID DESIGN
    - 3 color groups: Blue (Identity) | Green (2025) | Yellow (2026)
    - Fixed height 560px with vertical scroll
    - Sticky header + Pinned symbol column
    - Thick vertical separators between groups
    - Rating column calculated fresh from upside_pct
    """
    if df.empty:
        st.warning("⚠️ No data to display")
        return
    
    # Color legend above table
    st.markdown("""
    <div style="display: flex; gap: 20px; margin-bottom: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; background-color: #e3f2fd; border: 1px solid #90caf9; border-radius: 3px;"></div>
            <span style="font-weight: 600; color: #1976d2;">Identity & Valuation</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; background-color: #e8f5e9; border: 1px solid #81c784; border-radius: 3px;"></div>
            <span style="font-weight: 600; color: #388e3c;">2025 Forecast</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; background-color: #fff9c4; border: 1px solid #ffd54f; border-radius: 3px;"></div>
            <span style="font-weight: 600; color: #f57c00;">2026 Forecast</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get cached styled dataframe
    styler, available_config = get_styled_dataframe(df)
    
    # Render styled dataframe
    st.dataframe(
        styler,
        height=560,
        column_config=available_config,
        hide_index=True,
    )


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def render_forecast_dashboard():
    """Main forecast dashboard with enhanced UI - NO FILTERS"""
    
    # Render Top Navigation
    if render_top_nav is not None:
        render_top_nav()
    
    # Inject custom CSS for tables
    inject_custom_css()
    
    # Initialize session state
    if 'forecast_data_loaded' not in st.session_state:
        st.session_state.forecast_data_loaded = False
        st.session_state.forecast_data = pd.DataFrame()
    
    # Lazy load data with simplified approach
    if not st.session_state.forecast_data_loaded:
        # Show loading message
        with st.spinner("🔄 Đang tải dữ liệu forecast..."):
            try:
                # Load data with error handling
                forecast_data = load_comprehensive_forecast_data_csv()
                
                # Validate data
                if forecast_data.empty:
                    st.error("❌ Không có dữ liệu forecast. Vui lòng kiểm tra file CSV.")
                    st.info("💡 Chạy lệnh sau để tạo dữ liệu:")
                    st.code("python3 data_processor/forecast/run_bsc_auto_update.py", language="bash")
                    return
                
                # Store in session state
                st.session_state.forecast_data = forecast_data
                st.session_state.forecast_data_loaded = True
                
            except Exception as e:
                st.error(f"❌ Lỗi tải dữ liệu: {str(e)}")
                st.info("💡 Thử refresh trang hoặc kiểm tra kết nối mạng.")
                
                # Show fallback data
                st.warning("⚠️ Hiển thị dữ liệu mẫu...")
                forecast_data = pd.DataFrame({
                    'symbol': ['VCB', 'VIC', 'HPG'],
                    'rating': ['🟢 BUY', '🟡 HOLD', '🔴 SELL'],
                    'current_price': [95000, 50000, 30000],
                    'target_price': [100000, 48000, 25000],
                    'upside_pct': [5.3, -4.0, -16.7]
                })
                st.session_state.forecast_data = forecast_data
                st.session_state.forecast_data_loaded = True
                return
    else:
        forecast_data = st.session_state.forecast_data
    
    # Validate data
    if forecast_data.empty:
        st.error("❌ Không có dữ liệu forecast. Chạy lệnh sau:")
        st.code("python3 run_bsc_auto_update.py", language="bash")
        if st.button("🔄 Thử lại"):
            st.session_state.forecast_data_loaded = False
            st.rerun()
        return
    
    # Main table
    st.markdown("### 📊 Bảng Dự Báo Chi Tiết")
    render_forecast_table(forecast_data)
    
    # LNST Achievement Table
    st.markdown("---")
    render_npat_achievement_table(forecast_data)
    
    # Legend table - Quy Tắc Khuyến Nghị
    st.markdown("---")
    st.markdown("### 📋 Quy Tắc Khuyến Nghị")
    
    legend_data = {
        'Khuyến Nghị': ['🔥 STRONG BUY', '🟢 BUY', '🟡 HOLD', '🔴 SELL', '🔥 STRONG SELL'],
        'Điều Kiện': [
            'upside ≥ 20%',
            '10% ≤ upside < 20%',
            '-10% < upside < 10%',
            '-20% < upside ≤ -10%',
            'upside ≤ -20%'
        ]
    }
    legend_df = pd.DataFrame(legend_data)
    st.dataframe(legend_df, use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("---")
    st.caption("💡 Nguồn: BSC Research | Cập nhật tự động hàng ngày")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    render_forecast_dashboard()