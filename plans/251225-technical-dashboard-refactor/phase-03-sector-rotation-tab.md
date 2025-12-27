# Phase 3: Sector Rotation Tab

**Goal:** Build Tab 2 with RRG chart, sector ranking, and Stock RS Rating Heatmap

---

## 1. Component Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                     SECTOR ROTATION                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    RRG SCATTER PLOT                        │  │
│  │                                                            │  │
│  │  Mode: [◉ Sector] [○ Stock (BSC Universe)]  [Watchlist ▼] │  │
│  │                                                            │  │
│  │          IMPROVING    │    LEADING                         │  │
│  │              ●CTG     │        ●VCB                        │  │
│  │         ●Securities   │    ●Banking                        │  │
│  │  ─────────────────────┼─────────────────────               │  │
│  │              ●Steel   │        ●Real Estate                │  │
│  │          LAGGING      │    WEAKENING                       │  │
│  │                       │                                    │  │
│  │  Trail: [5] days  Smooth: [SMA 3]                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              SECTOR RANKING TABLE (IBD-style)              │  │
│  │                                                            │  │
│  │ Rank │ Sector      │ Score │ 1W%  │ 1M%  │ 3M%  │ Action  │  │
│  │ 1    │ Ngân hàng   │ 12.5  │ +3%  │ +15% │ +22% │ OVERWEIGHT│ │
│  │ 2    │ Chứng khoán │ 10.2  │ +2%  │ +12% │ +18% │ OVERWEIGHT│ │
│  │ 3    │ Thép        │  8.5  │ +1%  │ +10% │ +8%  │ OVERWEIGHT│ │
│  │ ...                                                        │  │
│  │ 19   │ Bất động sản│ -2.3  │ -2%  │ -5%  │ -10% │ UNDERWEIGHT││
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                 MONEY FLOW HEATMAP                         │  │
│  │  Banking  ████████████████  +500B                          │  │
│  │  Securit  ████████         +200B                           │  │
│  │  Tech     ████             +100B                           │  │
│  │  ...                                                       │  │
│  │  Steel    ████████████     -300B                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              STOCK RS RATING HEATMAP (NEW)                 │  │
│  │                                                            │  │
│  │  Filters: [Top N ▼] [Sector ▼] [Search: ___________]      │  │
│  │                                                            │  │
│  │  Mã CP   │19/11│20/11│21/11│...│22/12│23/12│24/12│25/12│  │
│  │  [001]NNC│     │     │  95 │ 95│  94 │  93 │  90 │  92 │  │
│  │  [002]AAS│  20 │  17 │  20 │...│  69 │  90 │  96 │  98 │  │
│  │  [002]DHA│  35 │  89 │  85 │...│  96 │  96 │  96 │  98 │  │
│  │  [002]STB│   6 │  15 │  73 │...│  95 │  98 │  98 │  98 │  │
│  │  [002]VHM│  14 │  44 │  78 │...│  92 │  98 │  99 │  98 │  │
│  │  ...     │     │     │     │...│     │     │     │     │  │
│  │                                                            │  │
│  │  Color: ███ 80-99 (Strong) ██ 50-79 ██ 20-49 ██ 1-19 (Weak)│
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Implementation

```python
# File: WEBAPP/pages/technical/components/sector_rotation.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ..services.ta_dashboard_service import TADashboardService

QUADRANT_COLORS = {
    'LEADING': '#4CAF50',     # Green
    'WEAKENING': '#FF9800',   # Orange
    'LAGGING': '#F44336',     # Red
    'IMPROVING': '#2196F3'    # Blue
}

def render_sector_rotation():
    """Render Sector Rotation tab"""

    service = TADashboardService()

    # ============ RRG CHART WITH MODE SELECTOR ============
    st.markdown("### Relative Rotation Graph (RRG)")

    render_rrg_with_options(service)

    st.markdown("---")

    # ============ SECTOR RANKING TABLE ============
    st.markdown("### Sector Ranking (IBD-style Returns)")

    ranking = service.get_sector_ranking()
    if ranking is not None and not ranking.empty:
        render_sector_ranking_table(ranking)
    else:
        st.info("Sector ranking data not available.")

    st.markdown("---")

    # ============ MONEY FLOW HEATMAP ============
    st.markdown("### Sector Money Flow (1 Day)")

    money_flow = service.get_sector_money_flow()
    if money_flow is not None and not money_flow.empty:
        render_money_flow_heatmap(money_flow)
    else:
        st.info("Money flow data not available.")

    st.markdown("---")

    # ============ STOCK RS RATING HEATMAP (NEW) ============
    render_stock_rs_heatmap(service)


# ============ RRG WITH MODE SELECTOR ============

# BSC Universe - Expandable stock list for Stock RRG mode
BSC_UNIVERSE = [
    # Banks (Top picks)
    'VCB', 'ACB', 'TCB', 'MBB', 'CTG', 'BID', 'STB', 'HDB', 'VPB', 'TPB',
    # Securities
    'SSI', 'VCI', 'HCM', 'VND', 'SHS',
    # Real Estate
    'VHM', 'VIC', 'NVL', 'KDH', 'DXG', 'PDR',
    # Technology
    'FPT', 'CMG',
    # Consumer/Retail
    'VNM', 'MSN', 'MWG', 'PNJ', 'DGW',
    # Industrial
    'HPG', 'HSG', 'NKG', 'GVR', 'DPM', 'DCM',
    # Oil & Gas
    'GAS', 'PLX', 'PVD', 'PVS',
    # Utilities
    'POW', 'REE', 'PC1',
    # Aviation/Logistics
    'HVN', 'VJC', 'GMD',
]

# Predefined watchlists (expandable)
WATCHLISTS = {
    'BSC Universe': BSC_UNIVERSE,
    'VN30': ['VCB', 'VHM', 'VIC', 'VNM', 'HPG', 'FPT', 'GAS', 'MSN', 'MWG', 'TCB',
             'ACB', 'MBB', 'CTG', 'BID', 'VPB', 'STB', 'HDB', 'TPB', 'VJC', 'PLX',
             'POW', 'REE', 'SSI', 'VND', 'GVR', 'SAB', 'BCM', 'VRE', 'PDR', 'KDH'],
    'Banking': ['VCB', 'ACB', 'TCB', 'MBB', 'CTG', 'BID', 'STB', 'HDB', 'VPB', 'TPB', 'EIB', 'LPB', 'MSB', 'OCB', 'SHB'],
    'Securities': ['SSI', 'VCI', 'HCM', 'VND', 'SHS', 'MBS', 'VIX', 'BSI', 'CTS', 'FTS'],
    'Real Estate': ['VHM', 'VIC', 'NVL', 'KDH', 'DXG', 'PDR', 'NLG', 'CEO', 'HDG', 'DIG'],
    'Technology': ['FPT', 'CMG', 'VGI', 'FOX'],
    'Custom': [],  # User can add custom list
}


def render_rrg_with_options(service: 'TADashboardService'):
    """
    Render RRG chart with mode selector (Sector/Stock)

    Features:
    - Mode toggle: Sector vs Stock
    - Stock mode: BSC Universe or custom watchlist
    - Trail option: Show N-day movement trail
    - Smoothing: SMA period selector
    """
    # ============ MODE & OPTIONS ============
    col1, col2, col3, col4 = st.columns([1.5, 1.5, 1, 1])

    with col1:
        rrg_mode = st.radio(
            "Mode",
            ["Sector", "Stock"],
            horizontal=True,
            key="rrg_mode"
        )

    with col2:
        if rrg_mode == "Stock":
            watchlist_name = st.selectbox(
                "Watchlist",
                list(WATCHLISTS.keys()),
                key="rrg_watchlist"
            )
        else:
            watchlist_name = None

    with col3:
        trail_days = st.selectbox(
            "Trail",
            [0, 3, 5, 10],
            index=2,
            format_func=lambda x: f"{x} days" if x > 0 else "Off",
            key="rrg_trail"
        )

    with col4:
        smooth_period = st.selectbox(
            "Smooth",
            [1, 3, 5],
            index=1,
            format_func=lambda x: f"SMA {x}" if x > 1 else "None",
            key="rrg_smooth"
        )

    # ============ GET DATA ============
    if rrg_mode == "Sector":
        rrg_data = service.get_sector_rs_for_rrg(smooth=smooth_period, trail_days=trail_days)
        entity_col = 'sector_code'
    else:
        symbols = WATCHLISTS.get(watchlist_name, BSC_UNIVERSE)
        rrg_data = service.get_stock_rs_for_rrg(
            symbols=symbols,
            smooth=smooth_period,
            trail_days=trail_days
        )
        entity_col = 'symbol'

    # ============ RENDER CHART ============
    if rrg_data is not None and not rrg_data.empty:
        fig = create_rrg_chart(rrg_data, entity_col=entity_col, show_trail=(trail_days > 0))
        st.plotly_chart(fig, use_container_width=True)

        # Show quadrant summary
        render_rrg_summary(rrg_data, entity_col)
    else:
        st.info("RRG data not available. Run RS calculation pipeline first.")


def create_rrg_chart(
    rrg_df: pd.DataFrame,
    entity_col: str = 'sector_code',
    show_trail: bool = False
) -> go.Figure:
    """
    Create Relative Rotation Graph (RRG) scatter plot

    Args:
        rrg_df: DataFrame with rs_ratio_smooth, rs_momentum_smooth, quadrant
        entity_col: Column name for entity (sector_code or symbol)
        show_trail: Whether to show movement trail

    Axes:
    - X: rs_ratio_smooth (relative to median, 1.0 = average)
    - Y: rs_momentum_smooth (rate of change)
    """
    fig = go.Figure()

    # Get latest date for current positions
    latest_date = rrg_df['date'].max()
    latest_data = rrg_df[rrg_df['date'] == latest_date]

    # Add trail lines if enabled
    if show_trail and 'date' in rrg_df.columns:
        for entity in latest_data[entity_col].unique():
            entity_data = rrg_df[rrg_df[entity_col] == entity].sort_values('date')
            if len(entity_data) > 1:
                fig.add_trace(go.Scatter(
                    x=entity_data['rs_ratio_smooth'],
                    y=entity_data['rs_momentum_smooth'],
                    mode='lines',
                    line=dict(width=1, color='rgba(128,128,128,0.3)'),
                    showlegend=False,
                    hoverinfo='skip'
                ))

    # Add scatter points for current position
    for _, row in latest_data.iterrows():
        quadrant = row.get('quadrant', 'UNKNOWN')
        color = QUADRANT_COLORS.get(quadrant, 'gray')

        fig.add_trace(go.Scatter(
            x=[row['rs_ratio_smooth']],
            y=[row['rs_momentum_smooth']],
            mode='markers+text',
            marker=dict(
                size=15,
                color=color,
                line=dict(width=2, color='white')
            ),
            text=[row[entity_col]],
            textposition='top center',
            name=row[entity_col],
            hovertemplate=(
                f"<b>{row[entity_col]}</b><br>"
                f"RS Ratio: {row['rs_ratio_smooth']:.3f}<br>"
                f"Momentum: {row['rs_momentum_smooth']:.1f}<br>"
                f"Quadrant: {quadrant}"
                "<extra></extra>"
            )
        ))

    # Quadrant lines
    fig.add_hline(y=0, line=dict(color='gray', width=1, dash='dash'))
    fig.add_vline(x=1, line=dict(color='gray', width=1, dash='dash'))

    # Quadrant labels
    fig.add_annotation(x=0.85, y=5, text="IMPROVING", showarrow=False,
                       font=dict(size=12, color='#2196F3'))
    fig.add_annotation(x=1.15, y=5, text="LEADING", showarrow=False,
                       font=dict(size=12, color='#4CAF50'))
    fig.add_annotation(x=0.85, y=-5, text="LAGGING", showarrow=False,
                       font=dict(size=12, color='#F44336'))
    fig.add_annotation(x=1.15, y=-5, text="WEAKENING", showarrow=False,
                       font=dict(size=12, color='#FF9800'))

    # Layout
    fig.update_layout(
        height=450,
        showlegend=False,
        xaxis=dict(title='RS Ratio', range=[0.7, 1.3]),
        yaxis=dict(title='RS Momentum', range=[-10, 10]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def render_rrg_summary(rrg_df: pd.DataFrame, entity_col: str):
    """Show quadrant summary counts"""
    latest_date = rrg_df['date'].max()
    latest = rrg_df[rrg_df['date'] == latest_date]

    quadrant_counts = latest['quadrant'].value_counts()

    cols = st.columns(4)
    quadrants = ['LEADING', 'IMPROVING', 'WEAKENING', 'LAGGING']
    icons = ['🟢', '🔵', '🟠', '🔴']

    for i, (q, icon) in enumerate(zip(quadrants, icons)):
        with cols[i]:
            count = quadrant_counts.get(q, 0)
            entities = latest[latest['quadrant'] == q][entity_col].tolist()
            st.metric(
                f"{icon} {q}",
                count,
                help=", ".join(entities[:5]) + ("..." if len(entities) > 5 else "")
            )


def render_sector_ranking_table(ranking: pd.DataFrame):
    """Render sector ranking as styled table"""

    # Format columns
    display_df = ranking[[
        'rank', 'sector_code', 'score',
        'ret_1w', 'ret_1m', 'ret_3m',
        'quadrant', 'action', 'breadth_status', 'warning'
    ]].copy()

    # Rename for display
    display_df.columns = [
        'Rank', 'Sector', 'Score',
        '1W %', '1M %', '3M %',
        'Quadrant', 'Action', 'Breadth', 'Warning'
    ]

    # Format percentages
    for col in ['1W %', '1M %', '3M %']:
        display_df[col] = display_df[col].apply(lambda x: f"{x:+.1f}%")

    display_df['Score'] = display_df['Score'].apply(lambda x: f"{x:.1f}")

    # Style action column
    def style_action(val):
        if val == 'OVERWEIGHT':
            return '🟢 ' + val
        elif val == 'UNDERWEIGHT':
            return '🔴 ' + val
        return '⚪ ' + val

    display_df['Action'] = display_df['Action'].apply(style_action)

    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_money_flow_heatmap(money_flow: pd.DataFrame):
    """Render money flow as horizontal bar chart"""

    # Sort by net flow
    df = money_flow.sort_values('net_flow_1d', ascending=True)

    # Color based on positive/negative
    colors = ['#4CAF50' if x > 0 else '#F44336' for x in df['net_flow_1d']]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df['sector_code'],
        x=df['net_flow_1d'],
        orientation='h',
        marker_color=colors,
        text=df['net_flow_1d'].apply(lambda x: f"{x/1e9:+.0f}B"),
        textposition='outside',
        hovertemplate='<b>%{y}</b>: %{x:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        height=400,
        xaxis_title='Net Flow (VND)',
        yaxis_title='',
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig, use_container_width=True)


# ============ STOCK RS RATING HEATMAP (NEW) ============

def render_stock_rs_heatmap(service: 'TADashboardService'):
    """
    Render Stock RS Rating Heatmap - IBD-style price strength over time

    Features:
    - Rows: Stocks (sorted by latest RS rating)
    - Columns: Dates (last 30 trading days)
    - Color: RS Rating 1-99 (purple=weak → green=strong)
    - Filters: Top N, Sector, Search by symbol
    """
    st.markdown("### Bản đồ sức mạnh giá theo cổ phiếu (RS Rating)")

    # ============ FILTERS ============
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        top_n = st.selectbox(
            "Hiển thị",
            [20, 50, 100, 200, "All"],
            index=1,
            key="rs_heatmap_top_n"
        )

    with col2:
        sectors = ["All"] + service.get_sector_list()
        selected_sector = st.selectbox(
            "Sector",
            sectors,
            key="rs_heatmap_sector"
        )

    with col3:
        search_symbol = st.text_input(
            "Tìm mã (VD: VCB, ACB, FPT)",
            key="rs_heatmap_search",
            placeholder="Nhập mã cổ phiếu..."
        )

    # ============ GET DATA ============
    rs_data = service.get_stock_rs_rating_history(days=30)

    if rs_data is None or rs_data.empty:
        st.info("RS Rating data not available. Run RS calculation pipeline first.")
        return

    # ============ APPLY FILTERS ============
    filtered_df = rs_data.copy()

    # Filter by sector
    if selected_sector != "All":
        filtered_df = filtered_df[filtered_df['sector_code'] == selected_sector]

    # Filter by search
    if search_symbol:
        symbols = [s.strip().upper() for s in search_symbol.split(',')]
        filtered_df = filtered_df[filtered_df['symbol'].isin(symbols)]

    # Sort by latest RS rating and limit
    latest_date = filtered_df['date'].max()
    latest_rs = filtered_df[filtered_df['date'] == latest_date][['symbol', 'rs_rating']]
    latest_rs = latest_rs.sort_values('rs_rating', ascending=False)

    if top_n != "All":
        top_symbols = latest_rs.head(int(top_n))['symbol'].tolist()
        filtered_df = filtered_df[filtered_df['symbol'].isin(top_symbols)]

    if filtered_df.empty:
        st.warning("Không có dữ liệu phù hợp với bộ lọc.")
        return

    # ============ PIVOT FOR HEATMAP ============
    # Pivot: rows=symbol, columns=date, values=rs_rating
    pivot_df = filtered_df.pivot_table(
        index='symbol',
        columns='date',
        values='rs_rating',
        aggfunc='first'
    )

    # Sort by latest RS rating
    pivot_df = pivot_df.loc[latest_rs[latest_rs['symbol'].isin(pivot_df.index)]['symbol']]

    # Format date columns
    pivot_df.columns = [d.strftime('%d/%m') for d in pivot_df.columns]

    # ============ CREATE HEATMAP ============
    fig = create_rs_heatmap_figure(pivot_df)
    st.plotly_chart(fig, use_container_width=True)

    # ============ LEGEND ============
    st.markdown("""
    **Chú thích màu:**
    🟣 1-19 (Rất yếu) | 🟤 20-49 (Yếu) | 🟡 50-79 (Trung bình) | 🟢 80-99 (Mạnh)
    """)


def create_rs_heatmap_figure(pivot_df: pd.DataFrame) -> go.Figure:
    """
    Create Plotly heatmap for RS Rating

    Color scale: Purple (weak) → White (neutral) → Green (strong)
    """
    import numpy as np

    # Custom colorscale: purple → white → green
    colorscale = [
        [0.0, '#4A148C'],      # 1-19: Deep purple (very weak)
        [0.2, '#7B1FA2'],      # 20-39: Purple
        [0.4, '#9E9E9E'],      # 40-59: Gray (neutral)
        [0.6, '#81C784'],      # 60-79: Light green
        [0.8, '#4CAF50'],      # 80-89: Green
        [1.0, '#1B5E20']       # 90-99: Dark green (very strong)
    ]

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns.tolist(),
        y=pivot_df.index.tolist(),
        colorscale=colorscale,
        zmin=1,
        zmax=99,
        text=pivot_df.values.astype(int),
        texttemplate='%{text}',
        textfont=dict(size=10),
        hovertemplate=(
            '<b>%{y}</b><br>'
            'Ngày: %{x}<br>'
            'RS Rating: %{z}<extra></extra>'
        ),
        colorbar=dict(
            title='RS',
            tickvals=[1, 25, 50, 75, 99],
            ticktext=['1', '25', '50', '75', '99']
        )
    ))

    # Layout
    num_rows = len(pivot_df)
    height = max(400, min(800, num_rows * 25 + 100))

    fig.update_layout(
        height=height,
        xaxis=dict(
            title='Ngày',
            side='top',
            tickangle=45
        ),
        yaxis=dict(
            title='Mã CP',
            autorange='reversed'  # Top stocks at top
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig
```

---

## 3. Implementation Checklist

- [ ] Create `WEBAPP/pages/technical/components/sector_rotation.py`
- [ ] Implement `render_sector_rotation()`
- [ ] Implement `render_rrg_with_options()` - Mode selector (NEW)
- [ ] Implement `create_rrg_chart()` - With trail support
- [ ] Implement `render_rrg_summary()` - Quadrant counts (NEW)
- [ ] Implement `render_sector_ranking_table()`
- [ ] Implement `render_money_flow_heatmap()`
- [ ] Implement `render_stock_rs_heatmap()`
- [ ] Implement `create_rs_heatmap_figure()`
- [ ] Add service methods: `get_sector_ranking()`, `get_sector_rs_for_rrg()`, `get_sector_money_flow()`
- [ ] Add service method: `get_stock_rs_for_rrg()` (NEW - for Stock RRG mode)
- [ ] Add service method: `get_stock_rs_rating_history()`
- [ ] Create `config/watchlists.py` for BSC_UNIVERSE and WATCHLISTS
- [ ] Test with existing parquet files

---

## 4. Data Requirements

| Field | Source | Notes |
|-------|--------|-------|
| `sector_code` | sector_breadth_daily.parquet | Exists |
| `rs_ratio_smooth` | Calculated from returns | Phase 2 logic |
| `rs_momentum_smooth` | Calculated from returns | Phase 2 logic |
| `quadrant` | Calculated | LEADING/WEAKENING/LAGGING/IMPROVING |
| `net_flow_1d` | sector_money_flow_1d.parquet | Exists |
| `rs_rating` | **NEW** - stock_rs_rating_daily.parquet | 1-99 percentile rank |

---

## 4.1 Stock RRG Data Requirements (NEW)

| Field | Source | Notes |
|-------|--------|-------|
| `symbol` | OHLCV data | Stock ticker |
| `rs_ratio_smooth` | Calculated | Stock price / VN-Index ratio, smoothed |
| `rs_momentum_smooth` | Calculated | Rate of change of RS ratio |
| `quadrant` | Calculated | Based on smoothed values |

### Stock RRG Calculation

```python
def calculate_stock_rs_for_rrg(
    ohlcv_df: pd.DataFrame,
    vnindex_df: pd.DataFrame,
    symbols: list,
    smooth_period: int = 3,
    trail_days: int = 5
) -> pd.DataFrame:
    """
    Calculate RS for individual stocks (vs VN-Index)

    Same logic as sector RRG but at stock level
    """
    # Filter to requested symbols
    df = ohlcv_df[ohlcv_df['symbol'].isin(symbols)].copy()

    # Merge VN-Index close
    df = df.merge(
        vnindex_df[['date', 'close']].rename(columns={'close': 'vnindex'}),
        on='date'
    )

    # RS Ratio = Stock Close / VN-Index Close (normalized)
    df['rs_ratio'] = df['close'] / df['vnindex']

    # Normalize to median = 1.0
    df['daily_median'] = df.groupby('date')['rs_ratio'].transform('median')
    df['rs_ratio_norm'] = df['rs_ratio'] / df['daily_median']

    # RS Momentum = 5-day change
    df['rs_momentum'] = df.groupby('symbol')['rs_ratio_norm'].diff(5) * 100

    # Smooth
    df['rs_ratio_smooth'] = df.groupby('symbol')['rs_ratio_norm'].transform(
        lambda x: x.rolling(smooth_period, min_periods=1).mean()
    )
    df['rs_momentum_smooth'] = df.groupby('symbol')['rs_momentum'].transform(
        lambda x: x.rolling(smooth_period, min_periods=1).mean()
    )

    # Quadrant
    conditions = [
        (df['rs_ratio_smooth'] > 1) & (df['rs_momentum_smooth'] > 0),
        (df['rs_ratio_smooth'] > 1) & (df['rs_momentum_smooth'] <= 0),
        (df['rs_ratio_smooth'] <= 1) & (df['rs_momentum_smooth'] <= 0),
        (df['rs_ratio_smooth'] <= 1) & (df['rs_momentum_smooth'] > 0)
    ]
    choices = ['LEADING', 'WEAKENING', 'LAGGING', 'IMPROVING']
    df['quadrant'] = np.select(conditions, choices, default='UNKNOWN')

    # Return trail_days of history
    cutoff = df['date'].max() - pd.Timedelta(days=trail_days)
    return df[df['date'] >= cutoff][
        ['symbol', 'date', 'rs_ratio_smooth', 'rs_momentum_smooth', 'quadrant']
    ]
```

---

## 5. RS Rating Calculation (New Pipeline Required)

### Formula (IBD-style RS Rating)

```python
def calculate_rs_rating(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate IBD-style RS Rating for all stocks

    RS Rating = Percentile rank of weighted price performance
    Score = 0.4×ret_3m + 0.2×ret_6m + 0.2×ret_9m + 0.2×ret_12m

    Returns: 1-99 rating (99 = top 1%, 1 = bottom 1%)
    """
    df = df.copy()

    # Calculate returns for different periods
    df['ret_3m'] = df.groupby('symbol')['close'].pct_change(63) * 100   # ~3 months
    df['ret_6m'] = df.groupby('symbol')['close'].pct_change(126) * 100  # ~6 months
    df['ret_9m'] = df.groupby('symbol')['close'].pct_change(189) * 100  # ~9 months
    df['ret_12m'] = df.groupby('symbol')['close'].pct_change(252) * 100 # ~12 months

    # IBD-style weighted score (recent performance weighted more)
    df['rs_score'] = (
        0.4 * df['ret_3m'] +
        0.2 * df['ret_6m'] +
        0.2 * df['ret_9m'] +
        0.2 * df['ret_12m']
    )

    # Percentile rank within each date (1-99)
    df['rs_rating'] = df.groupby('date')['rs_score'].transform(
        lambda x: x.rank(pct=True) * 98 + 1  # Scale to 1-99
    ).round().astype(int)

    return df[['symbol', 'date', 'sector_code', 'rs_rating', 'rs_score']]
```

### Output File

```
DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet
```

### Service Method

```python
def get_stock_rs_rating_history(self, days: int = 30) -> pd.DataFrame:
    """
    Get RS Rating history for heatmap

    Returns: [symbol, date, sector_code, rs_rating]
    """
    path = self.DATA_ROOT / "rs_rating/stock_rs_rating_daily.parquet"
    if not path.exists():
        return None

    df = pd.read_parquet(path)

    # Filter to last N days
    cutoff = df['date'].max() - pd.Timedelta(days=days)
    df = df[df['date'] >= cutoff]

    return df
```

---

## 6. Pipeline Integration

Add to daily update pipeline:

```python
# In PROCESSORS/technical/daily_updates.py

from .rs_rating.rs_rating_calculator import calculate_rs_rating

def run_daily_rs_rating_update():
    """Calculate RS Rating for all stocks"""

    # Load OHLCV data
    ohlcv = pd.read_parquet("DATA/processed/technical/basic_data.parquet")

    # Get sector mapping
    sector_map = get_sector_mapping()  # symbol -> sector_code
    ohlcv['sector_code'] = ohlcv['symbol'].map(sector_map)

    # Calculate RS Rating
    rs_df = calculate_rs_rating(ohlcv)

    # Save
    output_path = Path("DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rs_df.to_parquet(output_path, index=False)

    print(f"✅ RS Rating updated: {len(rs_df)} records")
```
