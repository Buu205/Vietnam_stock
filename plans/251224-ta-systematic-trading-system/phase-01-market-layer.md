# Phase 1: Market Layer Implementation

**Goal:** Determine market regime & exposure level from big picture

---

## 1. Market Regime Detection

### Input Data
- VN-Index OHLCV from `DATA/processed/technical/vnindex/vnindex_indicators.parquet`

### Logic
```python
def get_market_regime(df: pd.DataFrame) -> str:
    """
    EMA9 > EMA21 → BULLISH
    EMA9 < EMA21 → BEARISH
    EMA9 ≈ EMA21 (within 0.5%) → NEUTRAL
    """
    latest = df.iloc[-1]
    ema9, ema21 = latest['ema9'], latest['ema21']

    if ema9 > ema21 * 1.005:
        return 'BULLISH'
    elif ema9 < ema21 * 0.995:
        return 'BEARISH'
    return 'NEUTRAL'
```

---

## 2. Breadth Score

### Input Data
- `DATA/processed/technical/market_breadth/market_breadth_daily.parquet`

### Columns Available
- `above_ma20_pct` - % stocks above MA20
- `above_ma50_pct` - % stocks above MA50
- `above_ma100_pct` - % stocks above MA100
- `ad_ratio` - Advance/Decline ratio

### Logic
```python
def get_breadth_score(df: pd.DataFrame) -> float:
    """Primary: above_ma20_pct (faster, more sensitive)"""
    return df.iloc[-1]['above_ma20_pct']

def get_breadth_multi_ma(df: pd.DataFrame) -> dict:
    """Get breadth for MA20, MA50, MA100"""
    latest = df.iloc[-1]
    return {
        'ma20_pct': latest['above_ma20_pct'],
        'ma50_pct': latest['above_ma50_pct'],
        'ma100_pct': latest.get('above_ma100_pct', 0),
        'date': latest['date']
    }
```

### Breadth Interpretation Table

| MA Level | Overbought | Healthy | Oversold | Use Case |
|----------|------------|---------|----------|----------|
| MA20 | > 80% | 40-80% | < 20% | Short-term timing |
| MA50 | > 75% | 35-75% | < 20% | Medium-term trend |
| MA100 | > 70% | 30-70% | < 15% | Long-term health |

**Key Insight:**
- MA20 phản ứng nhanh nhất → dùng cho exposure control
- MA50 là tham chiếu chính cho market regime
- MA100 xác định long-term bull/bear market

---

## 3. Exposure Control (5 Levels)

### Validated by Backtest
- Sharpe: 0.82 vs 0.55 B&H
- DD: -14.5% vs -35.1% B&H (58% reduction)

### Logic Table

| Regime | Breadth % | Exposure | Risk Profile |
|--------|-----------|----------|--------------|
| BULLISH | >= 70% | 100% | Full risk-on |
| BULLISH | 55-70% | 80% | Moderate |
| BULLISH | 40-55% | 60% | Cautious |
| BULLISH | 25-40% | 40% | Defensive |
| BULLISH | < 25% | 20% | Minimal |
| BEARISH | Any | 0% | Cash |

### Implementation
```python
def calculate_exposure_level(regime: str, breadth: float) -> int:
    if regime == 'BEARISH':
        return 0

    if breadth >= 70:
        return 100
    elif breadth >= 55:
        return 80
    elif breadth >= 40:
        return 60
    elif breadth >= 25:
        return 40
    else:
        return 20
```

---

## 4. Breadth Divergence Detection

### Purpose
- Detect false breakouts (index up, breadth down)
- Detect accumulation (index down, breadth up)

### Logic
```python
def detect_breadth_divergence(vnindex_df: pd.DataFrame, breadth_df: pd.DataFrame, lookback: int = 20) -> dict:
    """
    Compare VN-Index price trend vs breadth trend

    BULLISH divergence: VNIndex lower lows + Breadth higher lows
    BEARISH divergence: VNIndex higher highs + Breadth lower highs
    """
    vn_close = vnindex_df['close'].tail(lookback)
    breadth = breadth_df['above_ma20_pct'].tail(lookback)

    # Find swing points
    vn_lows = vn_close.rolling(5, center=True).min()
    vn_highs = vn_close.rolling(5, center=True).max()
    br_lows = breadth.rolling(5, center=True).min()
    br_highs = breadth.rolling(5, center=True).max()

    # Check divergence
    vn_making_lower_lows = vn_lows.iloc[-1] < vn_lows.iloc[-10]
    br_making_higher_lows = br_lows.iloc[-1] > br_lows.iloc[-10]

    vn_making_higher_highs = vn_highs.iloc[-1] > vn_highs.iloc[-10]
    br_making_lower_highs = br_highs.iloc[-1] < br_highs.iloc[-10]

    if vn_making_lower_lows and br_making_higher_lows:
        return {'type': 'BULLISH', 'strength': 2}
    elif vn_making_higher_highs and br_making_lower_highs:
        return {'type': 'BEARISH', 'strength': 2}

    return {'type': None, 'strength': 0}
```

---

## 5. Output Schema

### MarketState Dataclass
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class MarketState:
    date: datetime
    vnindex_close: float
    vnindex_change_pct: float
    regime: str  # BULLISH/NEUTRAL/BEARISH
    ema9: float
    ema21: float
    breadth_ma20_pct: float
    breadth_ma50_pct: float
    ad_ratio: float
    exposure_level: int  # 0, 20, 40, 60, 80, 100
    divergence_type: Optional[str]  # BULLISH/BEARISH/None
    divergence_strength: int  # 0-3
    signal: str  # RISK_ON / RISK_OFF / CAUTION
```

### Output File
```
DATA/processed/technical/market_state/market_state_daily.parquet
```

---

## 6. File Structure

```
PROCESSORS/technical/market/
├── __init__.py
├── market_analyzer.py       # Main module
│   ├── get_market_regime()
│   ├── get_breadth_score()
│   ├── calculate_exposure_level()
│   ├── detect_breadth_divergence()
│   └── generate_market_state()
└── market_dashboard_data.py # Dashboard data prep
```

---

## 7. Dashboard Components

### 11_market_overview.py

```
┌─────────────────────────────────────────────────────────┐
│                   MARKET OVERVIEW                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │ VN-Index │  │  Regime  │  │    Exposure Level    │   │
│  │  1,245   │  │    🟢    │  │  ████████░░  80%     │   │
│  │  +1.2%   │  │ BULLISH  │  │                      │   │
│  └──────────┘  └──────────┘  └──────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Breadth Gauge                       │    │
│  │  ┌─────────────────────────────────────────┐    │    │
│  │  │ % > MA20:  ████████████░░░░  62%        │    │    │
│  │  │ % > MA50:  ██████████░░░░░░  48%        │    │    │
│  │  │ % > MA100: ████████░░░░░░░░  38%        │    │    │
│  │  └─────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │           Divergence Alert                       │    │
│  │  ⚠️ BEARISH DIVERGENCE DETECTED                 │    │
│  │  VNIndex: Higher Highs | Breadth: Lower Highs   │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Market Breadth Multi-MA Line Chart

```
┌─────────────────────────────────────────────────────────────────────┐
│         MARKET BREADTH vs VN-INDEX (% Stocks Above MA)              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  VN-Index (Right Axis)                                              │
│  1300 ┤                                    ╭──╮                      │
│  1250 ┤                              ╭────╯  ╰────╮                  │
│  1200 ┤                     ╭───────╯             ╰────              │
│  1150 ┤            ╭───────╯                                         │
│  1100 ┤   ╭───────╯                                                  │
│  1050 ┼───╯                                                          │
│       └──────┬──────┬──────┬──────┬──────┬──────┬──────┬────────    │
│            Jan    Feb    Mar    Apr    May    Jun    Jul             │
│                                                                      │
│  100%┤ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ (Overbought)      │
│   80%┤         ╭╮   ╭──╮      ╭╮                                     │
│   60%┤   ╭────╯ ╰──╯  ╰─────╮│╰──╮   ╭──╮  ← % > MA20 (Blue)       │
│   40%┤──╯                   ╰╯   ╰──╯  ╰───  ← % > MA50 (Orange)   │
│   20%┤─────────────────────────────────────  ← % > MA100 (Green)   │
│    0%┤ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ (Oversold)        │
│       └──────┬──────┬──────┬──────┬──────┬──────┬──────┬────────    │
│            Jan    Feb    Mar    Apr    May    Jun    Jul             │
│                                                                      │
│  Legend:                                                             │
│  ━━━ % > MA20 (Short-term) - Fastest, most sensitive                │
│  ━━━ % > MA50 (Medium-term) - Main trend reference                  │
│  ━━━ % > MA100 (Long-term) - Market health indicator                │
│  ─── VN-Index (Overlay)                                             │
│                                                                      │
│  Zones:                                                              │
│  ░░░ 80-100%: Overbought → Caution, potential correction            │
│  ░░░ 40-60%: Healthy → Normal trading conditions                    │
│  ░░░ 0-20%: Oversold → Potential bounce opportunity                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Chart Implementation (Streamlit + Plotly)

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_breadth_chart(breadth_df: pd.DataFrame, vnindex_df: pd.DataFrame) -> go.Figure:
    """
    Create dual-axis chart: VN-Index + Market Breadth (MA20/50/100)

    Features:
    - VN-Index as area chart (right axis)
    - 3 breadth lines: MA20, MA50, MA100 (left axis)
    - Overbought/Oversold zones as horizontal bands
    - Divergence highlighting
    """
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.4, 0.6],
        shared_xaxes=True,
        vertical_spacing=0.05,
        specs=[[{"secondary_y": False}],
               [{"secondary_y": True}]]
    )

    # Row 1: VN-Index
    fig.add_trace(
        go.Scatter(
            x=vnindex_df['date'],
            y=vnindex_df['close'],
            name='VN-Index',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ),
        row=1, col=1
    )

    # Row 2: Market Breadth Lines
    # MA20 - Blue (fastest)
    fig.add_trace(
        go.Scatter(
            x=breadth_df['date'],
            y=breadth_df['above_ma20_pct'],
            name='% > MA20',
            line=dict(color='#2196F3', width=2)
        ),
        row=2, col=1
    )

    # MA50 - Orange (medium)
    fig.add_trace(
        go.Scatter(
            x=breadth_df['date'],
            y=breadth_df['above_ma50_pct'],
            name='% > MA50',
            line=dict(color='#FF9800', width=2)
        ),
        row=2, col=1
    )

    # MA100 - Green (slowest)
    fig.add_trace(
        go.Scatter(
            x=breadth_df['date'],
            y=breadth_df['above_ma100_pct'],
            name='% > MA100',
            line=dict(color='#4CAF50', width=2)
        ),
        row=2, col=1
    )

    # Add horizontal zones
    # Overbought zone (80-100%)
    fig.add_hrect(
        y0=80, y1=100,
        fillcolor="rgba(255, 0, 0, 0.1)",
        line_width=0,
        annotation_text="Overbought",
        annotation_position="top right",
        row=2, col=1
    )

    # Oversold zone (0-20%)
    fig.add_hrect(
        y0=0, y1=20,
        fillcolor="rgba(0, 255, 0, 0.1)",
        line_width=0,
        annotation_text="Oversold",
        annotation_position="bottom right",
        row=2, col=1
    )

    # Layout
    fig.update_layout(
        title='Market Breadth vs VN-Index',
        height=600,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode='x unified'
    )

    fig.update_yaxes(title_text="VN-Index", row=1, col=1)
    fig.update_yaxes(title_text="% Stocks Above MA", range=[0, 100], row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)

    return fig
```

### Divergence Detection on Chart

```python
def highlight_divergences(fig: go.Figure, divergences: list) -> go.Figure:
    """
    Add divergence markers to breadth chart

    divergences: list of {'date', 'type', 'strength'}
    """
    for div in divergences:
        color = 'green' if div['type'] == 'BULLISH' else 'red'
        symbol = '▲' if div['type'] == 'BULLISH' else '▼'

        fig.add_annotation(
            x=div['date'],
            y=50,  # Middle of breadth chart
            text=f"{symbol} {div['type']} DIV",
            showarrow=True,
            arrowhead=2,
            arrowcolor=color,
            font=dict(color=color, size=10),
            row=2, col=1
        )

    return fig
```

---

## 8. Implementation Checklist

- [ ] Create `PROCESSORS/technical/market/market_analyzer.py`
- [ ] Implement `get_market_regime()`
- [ ] Implement `get_breadth_multi_ma()` for MA20/50/100
- [ ] Implement `calculate_exposure_level()`
- [ ] Implement `detect_breadth_divergence()`
- [ ] Add `above_ma100_pct` column to market_breadth processor
- [ ] Create output parquet schema
- [ ] Add to daily pipeline
- [ ] Build Streamlit dashboard page with Multi-MA Line Chart
- [ ] Implement `create_breadth_chart()` with Plotly
- [ ] Add divergence highlighting
- [ ] Test with historical data
