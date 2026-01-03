"""
FX & Commodities Dashboard
==========================
Macro economic indicators, exchange rates, and commodity prices.

Features:
- Interest rate groups (deposit, interbank) with multi-series charts
- Exchange rate pairs (official vs free market)
- Commodity VN vs Global dual-axis comparisons
- Performance tables with trend highlighting
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional
import logging

from WEBAPP.core.styles import (
    get_page_style, get_chart_layout, CHART_COLORS,
    render_styled_table, get_table_style
)
from WEBAPP.services.macro_commodity_loader import MacroCommodityLoader
from WEBAPP.components.tables.performance_table import (
    build_performance_table, calculate_period_changes, get_top_movers
)
from WEBAPP.core.session_state import init_page_state, render_persistent_tabs

logger = logging.getLogger(__name__)

# Apply global styles
st.markdown(get_page_style(), unsafe_allow_html=True)
st.markdown(get_table_style(), unsafe_allow_html=True)

# Initialize session state for this page
init_page_state('fx_commodities')

# Additional responsive CSS
st.markdown("""
<style>
.fx-chart-container {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
}
.stPlotlyChart > div > div {
    width: 100% !important;
}
.stPlotlyChart {
    margin-bottom: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SYMBOL MAPPING: Actual parquet symbols → canonical display symbols
# ============================================================================
MACRO_SYMBOL_MAP = {
    # Deposit Rates (malformed in data with Vietnamese text)
    '13_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb': 'ls_huy_dong_13_thang',
    '1_3_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb': 'ls_huy_dong_1_3_thang',
    '6_9_tháng___nhtm_lớn___mbb,_acb,_tcb,_vpb': 'ls_huy_dong_6_9_thang',

    # Interbank Rates (have Vietnamese diacritics)
    'ls_liên_ngân_hàng_kỳ_hạn_1_tuần': 'ls_lien_ngan_hang_ky_han_1_tuan',
    'ls_liên_ngân_hàng_kỳ_hạn_2_tuần': 'ls_lien_ngan_hang_ky_han_2_tuan',
    'ls_qua_dem_lien_ngan_hang': 'ls_qua_dem_lien_ngan_hang',  # clean

    # Exchange Rates (have Vietnamese diacritics)
    'tỷ_giá_usd_nhtm_bán_ra': 'ty_gia_usd_nhtm_ban_ra',
    'tỷ_giá_usd_trung_tâm': 'ty_gia_usd_trung_tam',
    'tỷ_usd_tự_do_bán_ra': 'ty_gia_usd_tu_do_ban_ra',
    'ty_gia_san': 'ty_gia_san',  # clean
    'ty_gia_tran': 'ty_gia_tran',  # clean

    # Bonds
    'vn_gov_bond_5y': 'vn_gov_bond_5y',  # clean
}

# Reverse map for data retrieval
CANONICAL_TO_ACTUAL = {v: k for k, v in MACRO_SYMBOL_MAP.items()}

# Vietnamese display labels
MACRO_LABELS = {
    'ls_huy_dong_13_thang': 'LS huy động 13 tháng',
    'ls_huy_dong_1_3_thang': 'LS huy động 1-3 tháng',
    'ls_huy_dong_6_9_thang': 'LS huy động 6-9 tháng',
    'ls_lien_ngan_hang_ky_han_1_tuan': 'LS liên NH kỳ hạn 1 tuần',
    'ls_lien_ngan_hang_ky_han_2_tuan': 'LS liên NH kỳ hạn 2 tuần',
    'ls_qua_dem_lien_ngan_hang': 'LS qua đêm liên NH',
    'ty_gia_san': 'Tỷ giá sàn',
    'ty_gia_tran': 'Tỷ giá trần',
    'ty_gia_usd_nhtm_ban_ra': 'USD NHTM bán ra',
    'ty_gia_usd_trung_tam': 'USD trung tâm (SBV)',
    'ty_gia_usd_tu_do_ban_ra': 'USD tự do bán ra',
    'vn_gov_bond_5y': 'Lợi suất TPCP 5 năm'
}

# Commodity labels (clean, no emojis)
COMMODITY_LABELS = {
    'gold_global': 'Vàng thế giới',
    'gold_vn': 'Vàng SJC VN',
    'gold_vn_buy': 'Vàng SJC mua vào',
    'oil_crude': 'Dầu Brent',
    'oil_wti': 'Dầu WTI',
    'gas_natural': 'Khí thiên nhiên',
    'coke': 'Than cốc',
    'steel_d10': 'Thép D10',
    'steel_hrc': 'Thép HRC',
    'steel_coated': 'Tôn mạ',
    'iron_ore': 'Quặng sắt',
    'fertilizer_ure': 'Ure Trung Đông',
    'ure_vn_dpm': 'Ure Phú Mỹ (DPM)',
    'ure_vn_dcm': 'Ure Cà Mau (DCM)',
    'soybean': 'Đậu tương',
    'corn': 'Ngô',
    'sugar': 'Đường',
    'pork_vn_wichart': 'Heo hơi VN',
    'pork_china': 'Heo hơi TQ',
    'pvc': 'PVC',
    'cao_su': 'Cao su',
    'sua_bot_wmp': 'Sữa bột WMP'
}

# Interest rate chart groups (shared Y-axis, % unit)
INTEREST_RATE_GROUPS = {
    "Lãi suất huy động": {
        'symbols': ['ls_huy_dong_1_3_thang', 'ls_huy_dong_6_9_thang', 'ls_huy_dong_13_thang'],
        'colors': [CHART_COLORS['primary'], CHART_COLORS['secondary'], CHART_COLORS['tertiary']],
        'unit': '%',
        'title': 'Lãi suất huy động theo kỳ hạn'
    },
    "Lãi suất liên ngân hàng": {
        'symbols': ['ls_qua_dem_lien_ngan_hang', 'ls_lien_ngan_hang_ky_han_1_tuan', 'ls_lien_ngan_hang_ky_han_2_tuan'],
        'colors': [CHART_COLORS['positive'], CHART_COLORS['primary'], CHART_COLORS['secondary']],
        'unit': '%',
        'title': 'Lãi suất liên ngân hàng'
    }
}

# Fill colors (10% opacity versions)
FILL_COLORS = {
    'primary': 'rgba(139, 92, 246, 0.1)',
    'secondary': 'rgba(6, 182, 212, 0.1)',
    'tertiary': 'rgba(245, 158, 11, 0.1)',
    'positive': 'rgba(16, 185, 129, 0.1)',
    'negative': 'rgba(239, 68, 68, 0.1)',
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def resolve_macro_symbol(actual_symbol: str) -> str:
    """Convert actual data symbol to canonical symbol."""
    return MACRO_SYMBOL_MAP.get(actual_symbol, actual_symbol)


def get_actual_symbol(canonical_symbol: str) -> str:
    """Convert canonical symbol to actual data symbol for loader."""
    return CANONICAL_TO_ACTUAL.get(canonical_symbol, canonical_symbol)


def get_label(canonical_symbol: str) -> str:
    """Get Vietnamese display label for canonical symbol."""
    return MACRO_LABELS.get(canonical_symbol, COMMODITY_LABELS.get(canonical_symbol, canonical_symbol))


def filter_series_by_days(series: pd.DataFrame, days: int) -> pd.DataFrame:
    """Filter series to last N days."""
    if series.empty or 'date' not in series.columns:
        return series
    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
    return series[series['date'] >= cutoff]


def create_multi_series_chart(
    loader: MacroCommodityLoader,
    symbols: list,
    colors: list,
    days: int,
    unit: str = '%',
    height: int = 450
) -> go.Figure:
    """
    Create multi-series chart with shared Y-axis.

    Args:
        loader: MacroCommodityLoader instance
        symbols: List of canonical symbol names
        colors: List of color hex codes
        days: Number of days to filter
        unit: Y-axis unit label
        height: Chart height
    """
    fig = go.Figure()

    for symbol, color in zip(symbols, colors):
        actual_symbol = get_actual_symbol(symbol)
        series = filter_series_by_days(loader.get_series(actual_symbol), days)

        if not series.empty and 'value' in series.columns:
            label = get_label(symbol)
            fig.add_trace(go.Scatter(
                x=series['date'],
                y=series['value'],
                name=label,
                mode='lines',
                line=dict(color=color, width=2.5),
                hovertemplate=f'<b>{label}</b><br>%{{x|%d/%m/%Y}}<br>%{{y:.2f}}{unit}<extra></extra>'
            ))

    # Apply layout
    layout = get_chart_layout(height=height)
    layout['showlegend'] = True
    layout['legend'] = dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.5,
        font=dict(size=11, color='#E8E8E8')
    )
    layout['yaxis']['title'] = unit
    layout['xaxis'] = dict(
        tickformat='%b %Y',
        tickmode='auto',
        nticks=8,
        tickangle=0,
        tickfont=dict(size=10, color='#CBD5E1'),
        showgrid=False,
        zeroline=False,
        showline=True,
        linecolor='rgba(255,255,255,0.2)'
    )
    fig.update_layout(**layout)

    return fig


# ============================================================================
# PAGE HEADER
# ============================================================================
st.title("FX & Commodities")
st.markdown("*Macro economic indicators, exchange rates, and commodity prices*")

# ============================================================================
# SIDEBAR: Time Range Filter
# ============================================================================
with st.sidebar:
    st.markdown("### Time Range")
    days = st.selectbox(
        "Select Period",
        options=[30, 90, 180, 365, 730],
        format_func=lambda x: {30: "1 Month", 90: "3 Months", 180: "6 Months", 365: "1 Year", 730: "2 Years"}[x],
        index=2
    )

# ============================================================================
# TABS: Macro & FX | Commodities (Session State Persisted)
# ============================================================================
active_tab = render_persistent_tabs(
    ["Macro & FX", "Commodities"],
    "fx_active_tab"
)

# ============================================================================
# TAB 1: MACRO DATA
# ============================================================================
if active_tab == 0:
    st.markdown("### Macro Economic Indicators")
    st.markdown("*Interest rates, exchange rates, and government bond yields*")

    # Initialize loader
    with st.spinner('Loading macro data...'):
        macro_loader = MacroCommodityLoader()
        macro_df = macro_loader.get_macro()

    if macro_df.empty:
        st.warning("No macro data available. Please run the daily update pipeline.")
    else:
        # Get canonical symbols from actual data
        macro_symbols_raw = macro_df['symbol'].unique().tolist()
        macro_symbols = [resolve_macro_symbol(s) for s in macro_symbols_raw]

        # Log unmapped symbols for debugging
        unmapped = [s for s in macro_symbols_raw if s not in MACRO_SYMBOL_MAP]
        if unmapped:
            logger.warning(f"FX Dashboard: Unmapped macro symbols: {unmapped}")

        # Selector for indicator type
        macro_type = st.radio(
            "Select Category",
            options=["Lãi suất huy động", "Lãi suất liên ngân hàng", "Tỷ giá USD", "Trái phiếu CP"],
            horizontal=True
        )

        # =============================================
        # INTEREST RATES: Grouped multi-series charts
        # =============================================
        if macro_type in INTEREST_RATE_GROUPS:
            group = INTEREST_RATE_GROUPS[macro_type]

            # Check if symbols have data
            available_symbols = [s for s in group['symbols'] if s in macro_symbols]

            if available_symbols:
                fig_macro = create_multi_series_chart(
                    loader=macro_loader,
                    symbols=available_symbols,
                    colors=group['colors'][:len(available_symbols)],
                    days=days,
                    unit=group['unit'],
                    height=500
                )
                st.plotly_chart(fig_macro, width='stretch')

                # Performance Table
                st.markdown("### Performance Summary")
                perf_data = []
                for symbol in available_symbols:
                    actual_symbol = get_actual_symbol(symbol)
                    series = macro_loader.get_series(actual_symbol)
                    if not series.empty:
                        changes = calculate_period_changes(series, 'value')
                        perf_data.append({
                            'symbol': symbol,
                            'label': get_label(symbol),
                            **changes
                        })

                if perf_data:
                    st.markdown(build_performance_table(perf_data, show_1y=True, unit='%'), unsafe_allow_html=True)
            else:
                st.info("No data available for selected category")

        # =============================================
        # EXCHANGE RATE: Dual pair comparisons
        # =============================================
        elif macro_type == "Tỷ giá USD":
            exchange_dual_axis_pairs = {
                "USD: Chính thức vs Tự do": (
                    'ty_gia_usd_trung_tam', 'ty_gia_usd_tu_do_ban_ra',
                    'Trung tâm (SBV)', 'Tự do (Thị trường)'
                ),
                "USD: Ngân hàng vs Tự do": (
                    'ty_gia_usd_nhtm_ban_ra', 'ty_gia_usd_tu_do_ban_ra',
                    'NHTM bán ra', 'Tự do bán ra'
                ),
                "Biên độ: Sàn vs Trần": (
                    'ty_gia_san', 'ty_gia_tran',
                    'Giá sàn', 'Giá trần'
                ),
            }

            exchange_individual = {
                "USD Trung tâm (SBV)": 'ty_gia_usd_trung_tam',
                "USD NHTM bán ra": 'ty_gia_usd_nhtm_ban_ra',
                "USD Tự do bán ra": 'ty_gia_usd_tu_do_ban_ra',
            }

            all_exchange_options = list(exchange_dual_axis_pairs.keys()) + list(exchange_individual.keys())

            selected_exchange = st.selectbox(
                "Select Exchange Rate View",
                options=all_exchange_options,
                index=0
            )

            if selected_exchange in exchange_dual_axis_pairs:
                symbol1, symbol2, label1_short, label2_short = exchange_dual_axis_pairs[selected_exchange]

                actual_symbol1 = get_actual_symbol(symbol1)
                actual_symbol2 = get_actual_symbol(symbol2)

                series1 = filter_series_by_days(macro_loader.get_series(actual_symbol1), days)
                series2 = filter_series_by_days(macro_loader.get_series(actual_symbol2), days)

                if not series1.empty and not series2.empty:
                    label1 = get_label(symbol1)
                    label2 = get_label(symbol2)

                    # Single-axis chart (same VND unit)
                    fig_exchange = go.Figure()

                    fig_exchange.add_trace(
                        go.Scatter(
                            x=series1['date'],
                            y=series1['value'],
                            name=label1,
                            mode='lines',
                            line=dict(color=CHART_COLORS['primary'], width=2.5),
                            hovertemplate=f'<b>{label1}</b><br>Date: %{{x|%d/%m/%Y}}<br>Value: %{{y:,.0f}} VND<extra></extra>'
                        )
                    )

                    fig_exchange.add_trace(
                        go.Scatter(
                            x=series2['date'],
                            y=series2['value'],
                            name=label2,
                            mode='lines',
                            line=dict(color=CHART_COLORS['tertiary'], width=2.5),
                            hovertemplate=f'<b>{label2}</b><br>Date: %{{x|%d/%m/%Y}}<br>Value: %{{y:,.0f}} VND<extra></extra>'
                        )
                    )

                    layout = get_chart_layout(height=500)
                    layout['showlegend'] = True
                    layout['legend'] = dict(
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='center',
                        x=0.5,
                        font=dict(size=11, color='#E8E8E8')
                    )
                    layout['xaxis'] = dict(
                        tickformat='%b %Y',
                        tickmode='auto',
                        nticks=8,
                        tickangle=0,
                        tickfont=dict(size=10, color='#CBD5E1'),
                        showgrid=False,
                        zeroline=False,
                        showline=True,
                        linecolor='rgba(255,255,255,0.2)'
                    )
                    layout['yaxis'] = dict(
                        title='VND',
                        title_font=dict(color='#E8E8E8'),
                        tickfont=dict(size=10, color='#CBD5E1'),
                        tickformat=',d',
                        showgrid=False,
                        zeroline=False,
                        showline=True,
                        linecolor='rgba(255,255,255,0.2)'
                    )
                    fig_exchange.update_layout(**layout)

                    st.plotly_chart(fig_exchange, width='stretch')

                    # Show spread metrics
                    st.markdown("### Latest Values & Spread")
                    latest1 = series1.iloc[-1]['value']
                    latest2 = series2.iloc[-1]['value']
                    spread = latest2 - latest1
                    spread_pct = (spread / latest1) * 100 if latest1 > 0 else 0

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label1_short, f"{latest1:,.0f} VND")
                    with col2:
                        st.metric(label2_short, f"{latest2:,.0f} VND")
                    with col3:
                        st.metric("Spread (Chênh lệch)", f"{spread:+,.0f} VND", f"{spread_pct:+.2f}%")

                    # Performance table
                    st.markdown("### Performance Summary")
                    perf_data = []
                    for sym in [symbol1, symbol2]:
                        actual_sym = get_actual_symbol(sym)
                        series = macro_loader.get_series(actual_sym)
                        if not series.empty:
                            changes = calculate_period_changes(series, 'value')
                            perf_data.append({
                                'symbol': sym,
                                'label': get_label(sym),
                                **changes
                            })
                    if perf_data:
                        st.markdown(build_performance_table(perf_data, value_format=',.0f'), unsafe_allow_html=True)
                else:
                    st.warning("Data not available for selected exchange rate pair")

            elif selected_exchange in exchange_individual:
                symbol = exchange_individual[selected_exchange]
                actual_symbol = get_actual_symbol(symbol)
                series = filter_series_by_days(macro_loader.get_series(actual_symbol), days)

                if not series.empty and 'value' in series.columns:
                    label = get_label(symbol)

                    fig_single = go.Figure()
                    fig_single.add_trace(go.Scatter(
                        x=series['date'],
                        y=series['value'],
                        name=label,
                        mode='lines',
                        line=dict(color=CHART_COLORS['primary'], width=2),
                        fill='tozeroy',
                        fillcolor=FILL_COLORS['primary'],
                        hovertemplate=f'<b>{label}</b><br>Date: %{{x}}<br>Value: %{{y:,.0f}} VND<extra></extra>'
                    ))

                    layout = get_chart_layout(height=500)
                    layout['yaxis']['title'] = 'VND'
                    layout['yaxis']['tickformat'] = ',d'
                    layout['xaxis'] = dict(
                        tickformat='%b %Y',
                        tickmode='auto',
                        nticks=8,
                        tickangle=0,
                        tickfont=dict(size=10, color='#CBD5E1'),
                        showgrid=True,
                        gridcolor='rgba(255,255,255,0.05)'
                    )
                    fig_single.update_layout(**layout)

                    st.plotly_chart(fig_single, width='stretch')

                    # Latest value
                    latest = series.iloc[-1]
                    st.markdown("### Latest Value")
                    st.metric(label, f"{latest['value']:,.0f} VND",
                             help=f"Last updated: {latest['date'].strftime('%Y-%m-%d') if pd.notna(latest['date']) else '-'}")
                else:
                    st.warning("Data not available for selected exchange rate")

        # =============================================
        # BONDS: Government bond yield
        # =============================================
        elif macro_type == "Trái phiếu CP":
            bond_symbol = 'vn_gov_bond_5y'
            actual_symbol = get_actual_symbol(bond_symbol)
            series = filter_series_by_days(macro_loader.get_series(actual_symbol), days)

            if not series.empty and 'value' in series.columns:
                label = get_label(bond_symbol)

                fig_bond = go.Figure()
                fig_bond.add_trace(go.Scatter(
                    x=series['date'],
                    y=series['value'],
                    name=label,
                    mode='lines',
                    line=dict(color=CHART_COLORS['secondary'], width=2.5),
                    fill='tozeroy',
                    fillcolor=FILL_COLORS['secondary'],
                    hovertemplate=f'<b>{label}</b><br>Date: %{{x|%d/%m/%Y}}<br>Yield: %{{y:.2f}}%<extra></extra>'
                ))

                layout = get_chart_layout(height=500)
                layout['yaxis']['title'] = 'Yield (%)'
                layout['xaxis'] = dict(
                    tickformat='%b %Y',
                    tickmode='auto',
                    nticks=8,
                    tickangle=0,
                    tickfont=dict(size=10, color='#CBD5E1'),
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.05)'
                )
                fig_bond.update_layout(**layout)

                st.plotly_chart(fig_bond, width='stretch')

                # Performance table
                st.markdown("### Performance Summary")
                changes = calculate_period_changes(series, 'value')
                perf_data = [{
                    'symbol': bond_symbol,
                    'label': label,
                    **changes
                }]
                st.markdown(build_performance_table(perf_data, unit='%'), unsafe_allow_html=True)
            else:
                st.info("No bond data available")

# ============================================================================
# TAB 2: COMMODITY DATA
# ============================================================================
elif active_tab == 1:
    st.markdown("### Commodity Prices")
    st.markdown("*Individual commodities with dual-axis charts for comparison pairs*")

    # Initialize loader
    with st.spinner('Loading commodity data...'):
        commodity_loader = MacroCommodityLoader()
        commodity_df = commodity_loader.get_commodities()

    if commodity_df.empty:
        st.warning("No commodity data available. Please run the daily update pipeline.")
    else:
        commodity_symbols = commodity_df['symbol'].unique().tolist()

        # Dual-axis pairs (VN vs Global comparison)
        dual_axis_pairs = {
            "Vàng: VN vs Thế giới": ('gold_vn', 'gold_global', 'VND/lượng', '$/oz'),
            "Heo hơi: VN vs Trung Quốc": ('pork_vn_wichart', 'pork_china', 'VND/kg', 'CNY/kg'),
            "Dầu: WTI vs Brent": ('oil_wti', 'oil_crude', '$/bbl', '$/bbl'),
            "Ure: DPM vs Trung Đông": ('ure_vn_dpm', 'fertilizer_ure', 'VND/kg', '$/ton'),
            "Ure: DCM vs Trung Đông": ('ure_vn_dcm', 'fertilizer_ure', 'VND/kg', '$/ton'),
            "Thép: HRC vs D10": ('steel_hrc', 'steel_d10', '$/ton', '$/ton'),
        }

        # Individual commodities (no emojis, clean labels)
        individual_commodities = [
            ('gold_global', 'Vàng thế giới'),
            ('gas_natural', 'Khí thiên nhiên'),
            ('coke', 'Than cốc'),
            ('steel_d10', 'Thép D10'),
            ('steel_hrc', 'Thép HRC'),
            ('steel_coated', 'Tôn mạ'),
            ('iron_ore', 'Quặng sắt'),
            ('fertilizer_ure', 'Ure (Trung Đông)'),
            ('soybean', 'Đậu tương'),
            ('corn', 'Ngô'),
            ('sugar', 'Đường'),
            ('cao_su', 'Cao su'),
            ('pvc', 'PVC'),
            ('sua_bot_wmp', 'Sữa bột WMP'),
        ]

        # Filter to available symbols
        available_pairs = {k: v for k, v in dual_axis_pairs.items()
                         if v[0] in commodity_symbols and v[1] in commodity_symbols}
        available_individual = [(sym, label) for sym, label in individual_commodities
                               if sym in commodity_symbols]

        all_options = list(available_pairs.keys()) + [label for _, label in available_individual]

        if not all_options:
            st.warning("No commodity data available")
        else:
            selected_commodity = st.selectbox(
                "Select Commodity",
                options=all_options,
                index=0
            )

            # Check if selected is a dual-axis pair
            if selected_commodity in available_pairs:
                symbol1, symbol2, unit1, unit2 = available_pairs[selected_commodity]

                series1 = filter_series_by_days(commodity_loader.get_series(symbol1), days)
                series2 = filter_series_by_days(commodity_loader.get_series(symbol2), days)

                if not series1.empty or not series2.empty:
                    # Detect if same unit (single axis) or different (dual axis)
                    use_dual_axis = unit1 != unit2

                    if use_dual_axis:
                        fig = make_subplots(specs=[[{"secondary_y": True}]])
                    else:
                        fig = go.Figure()

                    # First series
                    if not series1.empty:
                        value_col1 = 'close' if 'close' in series1.columns and series1['close'].notna().any() else 'value'
                        label1 = COMMODITY_LABELS.get(symbol1, symbol1)
                        trace1 = go.Scatter(
                            x=series1['date'],
                            y=series1[value_col1],
                            name=label1,
                            mode='lines',
                            line=dict(color=CHART_COLORS['primary'], width=2.5),
                            hovertemplate=f'<b>{label1}</b><br>%{{x|%d/%m/%Y}}<br>%{{y:,.0f}} {unit1}<extra></extra>'
                        )
                        if use_dual_axis:
                            fig.add_trace(trace1, secondary_y=False)
                        else:
                            fig.add_trace(trace1)

                    # Second series
                    if not series2.empty:
                        value_col2 = 'close' if 'close' in series2.columns and series2['close'].notna().any() else 'value'
                        label2 = COMMODITY_LABELS.get(symbol2, symbol2)
                        trace2 = go.Scatter(
                            x=series2['date'],
                            y=series2[value_col2],
                            name=label2,
                            mode='lines',
                            line=dict(color=CHART_COLORS['tertiary'], width=2.5),
                            hovertemplate=f'<b>{label2}</b><br>%{{x|%d/%m/%Y}}<br>%{{y:,.0f}} {unit2}<extra></extra>'
                        )
                        if use_dual_axis:
                            fig.add_trace(trace2, secondary_y=True)
                        else:
                            fig.add_trace(trace2)

                    # Layout
                    layout = get_chart_layout(height=500)
                    layout['showlegend'] = True
                    layout['legend'] = dict(
                        orientation='h', yanchor='bottom', y=1.02,
                        xanchor='center', x=0.5, font=dict(size=11, color='#E8E8E8')
                    )
                    layout['xaxis'] = dict(
                        tickformat='%b %Y', tickmode='auto', nticks=8, tickangle=0,
                        tickfont=dict(size=10, color='#CBD5E1'),
                        showgrid=True, gridcolor='rgba(255,255,255,0.05)'
                    )
                    fig.update_layout(**layout)

                    if use_dual_axis:
                        fig.update_yaxes(title_text=f"{COMMODITY_LABELS.get(symbol1, symbol1)} ({unit1})",
                                        secondary_y=False, title_font=dict(color=CHART_COLORS['primary']))
                        fig.update_yaxes(title_text=f"{COMMODITY_LABELS.get(symbol2, symbol2)} ({unit2})",
                                        secondary_y=True, title_font=dict(color=CHART_COLORS['tertiary']))

                    st.plotly_chart(fig, width='stretch')

                    # Performance table
                    st.markdown("### Performance Summary")
                    perf_data = []
                    for sym, unit in [(symbol1, unit1), (symbol2, unit2)]:
                        series = commodity_loader.get_series(sym)
                        if not series.empty:
                            value_col = 'close' if 'close' in series.columns and series['close'].notna().any() else 'value'
                            changes = calculate_period_changes(series, value_col)
                            perf_data.append({
                                'symbol': sym,
                                'label': COMMODITY_LABELS.get(sym, sym),
                                **changes
                            })
                    if perf_data:
                        st.markdown(build_performance_table(perf_data, value_format=',.2f'), unsafe_allow_html=True)
                else:
                    st.warning("No data available for this pair")

            else:
                # Individual commodity
                symbol = None
                for sym, label in available_individual:
                    if label == selected_commodity:
                        symbol = sym
                        break

                if symbol:
                    series = filter_series_by_days(commodity_loader.get_series(symbol), days)

                    if not series.empty:
                        value_col = 'close' if 'close' in series.columns and series['close'].notna().any() else 'value'
                        label = COMMODITY_LABELS.get(symbol, symbol)

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=series['date'],
                            y=series[value_col],
                            name=label,
                            mode='lines',
                            line=dict(color=CHART_COLORS['primary'], width=2.5),
                            fill='tozeroy',
                            fillcolor=FILL_COLORS['primary'],
                            hovertemplate=f'<b>{label}</b><br>%{{x|%d/%m/%Y}}<br>Price: %{{y:,.2f}}<extra></extra>'
                        ))

                        layout = get_chart_layout(height=500)
                        layout['showlegend'] = False
                        layout['yaxis']['title'] = 'Price'
                        layout['xaxis'] = dict(
                            tickformat='%b %Y', tickmode='auto', nticks=8, tickangle=0,
                            tickfont=dict(size=10, color='#CBD5E1'),
                            showgrid=True, gridcolor='rgba(255,255,255,0.05)'
                        )
                        fig.update_layout(**layout)

                        st.plotly_chart(fig, width='stretch')

                        # Latest value metrics
                        latest = series.iloc[-1]
                        value = latest.get(value_col, 0)
                        change_pct = None
                        if len(series) > 1:
                            prev = series[value_col].iloc[-2]
                            if prev and prev != 0:
                                change_pct = ((value - prev) / prev) * 100

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Latest Price", f"{value:,.2f}")
                        with col2:
                            st.metric("Change (1D)", f"{change_pct:+.2f}%" if change_pct else "-")
                        with col3:
                            st.metric("Date", latest['date'].strftime('%Y-%m-%d') if pd.notna(latest['date']) else '-')

                        # Performance table
                        st.markdown("### Performance Summary")
                        changes = calculate_period_changes(series, value_col)
                        perf_data = [{
                            'symbol': symbol,
                            'label': label,
                            **changes
                        }]
                        st.markdown(build_performance_table(perf_data), unsafe_allow_html=True)
                    else:
                        st.warning(f"No data available for {selected_commodity}")
                else:
                    st.warning("Commodity not found")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption(f"Data: Macro & Commodities | Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
