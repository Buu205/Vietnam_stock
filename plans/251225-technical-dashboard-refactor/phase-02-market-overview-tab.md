# Phase 2: Market Overview Tab

**Goal:** Build Tab 1 with regime, breadth line chart, exposure gauge

---

## 1. Component Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                   MARKET OVERVIEW                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────┐   │
│  │ VN-Index │  │  Regime  │  │      Exposure Level          │   │
│  │  1,245   │  │    🟢    │  │  ████████████░░░░  80%       │   │
│  │  +1.2%   │  │ BULLISH  │  │                              │   │
│  └──────────┘  └──────────┘  └──────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │            BREADTH LINE CHART (6 months)                 │    │
│  │                                                          │    │
│  │  VN-Index ─────────────────────────── (Right Y-Axis)    │    │
│  │                                                          │    │
│  │  100% ┬ ░░░░░░░░░░░░░░░░░░░░░░░░░░ (Overbought Zone)    │    │
│  │   80% ┼────────────────────────────                      │    │
│  │       │    ╭──╮  ╭───╮                                   │    │
│  │   60% ┼───╯    ╰─╯   ╰───  ← % > MA20 (Blue)            │    │
│  │       │                                                  │    │
│  │   40% ┼───────────────────  ← % > MA50 (Orange)         │    │
│  │       │                                                  │    │
│  │   20% ┼───────────────────  ← % > MA100 (Green)         │    │
│  │    0% ┴ ░░░░░░░░░░░░░░░░░░░░░░░░░░ (Oversold Zone)      │    │
│  │       └──────┬──────┬──────┬──────┬──────┬──────┬────── │    │
│  │            Jul    Aug    Sep    Oct    Nov    Dec        │    │
│  │                                                          │    │
│  │  Legend:                                                 │    │
│  │  ━━━ % > MA20 (Short-term)                              │    │
│  │  ━━━ % > MA50 (Medium-term)                             │    │
│  │  ━━━ % > MA100 (Long-term)                              │    │
│  │  ─── VN-Index (Overlay)                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌───────────────────────┐ ┌───────────────────────────────┐    │
│  │   Breadth Gauges      │ │   Divergence Alert            │    │
│  │   MA20: ████████ 62%  │ │   ⚠️ BEARISH DIVERGENCE       │    │
│  │   MA50: ██████░░ 48%  │ │   VNIndex: Higher Highs       │    │
│  │   MA100: ████░░░ 38%  │ │   Breadth: Lower Highs        │    │
│  └───────────────────────┘ └───────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Implementation

```python
# File: WEBAPP/pages/technical/components/market_overview.py

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from ..services.ta_dashboard_service import TADashboardService

def render_market_overview():
    """Render Market Overview tab"""

    service = TADashboardService()
    state = service.get_market_state()
    history = service.get_breadth_history(days=180)

    # ============ METRIC CARDS ============
    st.markdown("### Current Market State")

    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

    with col1:
        delta = f"{state.vnindex_change_pct:+.2f}%"
        st.metric("VN-Index", f"{state.vnindex_close:,.0f}", delta)

    with col2:
        regime_icon = {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "🟡"}
        st.metric("Regime", state.regime, regime_icon.get(state.regime, "⚪"))

    with col3:
        st.metric("Signal", state.signal)

    with col4:
        # Exposure gauge as progress bar
        st.markdown("**Exposure Level**")
        st.progress(state.exposure_level / 100)
        st.caption(f"{state.exposure_level}% allocation recommended")

    st.markdown("---")

    # ============ BREADTH LINE CHART ============
    st.markdown("### Market Breadth (% Stocks Above MA)")

    fig = create_breadth_chart(history)
    st.plotly_chart(fig, use_container_width=True)

    # ============ BREADTH GAUGES + DIVERGENCE ============
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Breadth Gauges")
        render_breadth_gauges(state)

    with col2:
        st.markdown("### Divergence Alert")
        render_divergence_alert(state)


def create_breadth_chart(history) -> go.Figure:
    """Create multi-MA breadth line chart with VN-Index overlay"""

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.35, 0.65],
        specs=[[{"secondary_y": False}],
               [{"secondary_y": True}]]
    )

    # Row 1: VN-Index
    fig.add_trace(
        go.Scatter(
            x=history.date,
            y=history.vnindex_close,
            name='VN-Index',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ),
        row=1, col=1
    )

    # Row 2: Breadth Lines (Left Y-axis)
    # MA20 - Blue (fastest)
    fig.add_trace(
        go.Scatter(
            x=history.date,
            y=history.ma20_pct,
            name='% > MA20',
            line=dict(color='#2196F3', width=2),
            hovertemplate='<b>MA20</b>: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1, secondary_y=False
    )

    # MA50 - Orange (medium)
    fig.add_trace(
        go.Scatter(
            x=history.date,
            y=history.ma50_pct,
            name='% > MA50',
            line=dict(color='#FF9800', width=2),
            hovertemplate='<b>MA50</b>: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1, secondary_y=False
    )

    # MA100 - Green (slowest)
    fig.add_trace(
        go.Scatter(
            x=history.date,
            y=history.ma100_pct,
            name='% > MA100',
            line=dict(color='#4CAF50', width=2),
            hovertemplate='<b>MA100</b>: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1, secondary_y=False
    )

    # Overbought zone (80-100%)
    fig.add_hrect(
        y0=80, y1=100,
        fillcolor="rgba(255, 0, 0, 0.1)",
        line_width=0,
        row=2, col=1
    )

    # Oversold zone (0-20%)
    fig.add_hrect(
        y0=0, y1=20,
        fillcolor="rgba(0, 255, 0, 0.1)",
        line_width=0,
        row=2, col=1
    )

    # Threshold lines
    fig.add_hline(y=80, line=dict(color='red', width=1, dash='dash'),
                  row=2, col=1)
    fig.add_hline(y=20, line=dict(color='green', width=1, dash='dash'),
                  row=2, col=1)
    fig.add_hline(y=50, line=dict(color='gray', width=1, dash='dot'),
                  row=2, col=1)

    # Layout
    fig.update_layout(
        height=500,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_yaxes(title_text="VN-Index", row=1, col=1)
    fig.update_yaxes(title_text="% Stocks Above MA", range=[0, 100], row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)

    return fig


def render_breadth_gauges(state):
    """Render individual breadth gauges"""

    gauges = [
        ("MA20 (Short-term)", state.breadth_ma20_pct, "#2196F3"),
        ("MA50 (Medium-term)", state.breadth_ma50_pct, "#FF9800"),
        ("MA100 (Long-term)", state.breadth_ma100_pct, "#4CAF50"),
    ]

    for label, value, color in gauges:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(value / 100)
        with col2:
            status = "🔴" if value > 80 else ("🟢" if value < 20 else "⚪")
            st.write(f"{status} {value:.0f}%")
        st.caption(label)


def render_divergence_alert(state):
    """Render divergence detection alert"""

    if state.divergence_type:
        icon = "🐂" if state.divergence_type == "BULLISH" else "🐻"
        color = "green" if state.divergence_type == "BULLISH" else "red"
        st.warning(f"{icon} **{state.divergence_type} DIVERGENCE** detected (Strength: {state.divergence_strength}/3)")

        if state.divergence_type == "BULLISH":
            st.caption("VNIndex: Lower Lows | Breadth: Higher Lows → Potential reversal up")
        else:
            st.caption("VNIndex: Higher Highs | Breadth: Lower Highs → Potential reversal down")
    else:
        st.info("No divergence detected")
```

---

## 3. Implementation Checklist

- [ ] Create `WEBAPP/pages/technical/components/__init__.py`
- [ ] Create `WEBAPP/pages/technical/components/market_overview.py`
- [ ] Implement `render_market_overview()`
- [ ] Implement `create_breadth_chart()`
- [ ] Implement `render_breadth_gauges()`
- [ ] Implement `render_divergence_alert()`
- [ ] Test chart rendering with real data
- [ ] Verify responsive layout

---

## 4. Data Requirements

| Field | Source | Notes |
|-------|--------|-------|
| `above_ma20_pct` | market_breadth_daily.parquet | Exists |
| `above_ma50_pct` | market_breadth_daily.parquet | Exists |
| `above_ma100_pct` | market_breadth_daily.parquet | **VERIFY** |
| `ema9`, `ema21` | vnindex_indicators.parquet | Exists |
| `close` | vnindex_indicators.parquet | Exists |
