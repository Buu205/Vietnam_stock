# Phase 2: Sector Layer Implementation

**Goal:** Identify leading/lagging sectors for rotation strategy

---

## 1. Sector Relative Strength (RS)

### Concept
Compare each sector's performance against VN-Index benchmark using **market-cap weighted sector index**.

### Data Flow

```
INPUT DATA:
├── OHLCV_mktcap.parquet (458 symbols, 2015-2025)
│   ├── symbol, date, close, market_cap
│   └── Join with sector_registry → sector_code
│
├── vnindex_indicators.parquet (VN-Index OHLCV)
│   └── date, close (benchmark)
│
└── sector_industry_registry.json (457 tickers × 19 sectors)
    └── symbol → sector_code mapping

PROCESSING:
1. Calculate sector_index = Σ(stock_close × weight) / Σ(weight)
   where weight = market_cap
2. Calculate sector_return_20d = sector_index.pct_change(20)
3. Calculate RS = sector_return / vnindex_return
4. Calculate RS_momentum = RS.pct_change(5)

OUTPUT:
└── sector_rs_daily.parquet
    ├── date, sector_code
    ├── sector_index, sector_return_20d
    ├── rs_ratio, rs_momentum
    └── quadrant (LEADING/WEAKENING/LAGGING/IMPROVING)
```

### Formula

```python
# Step 1: Market-cap weighted sector index
sector_index = (stock_close * market_cap).groupby(['date', 'sector']).sum() / \
               market_cap.groupby(['date', 'sector']).sum()

# Step 2: RS Ratio (sector vs benchmark)
sector_return_20d = sector_index.pct_change(20)
vnindex_return_20d = vnindex_close.pct_change(20)
rs_ratio = sector_return_20d / vnindex_return_20d

# Step 3: RS Momentum (5-day change in RS)
rs_momentum = rs_ratio.pct_change(5) * 100

# Step 4: Normalize RS để so sánh (optional)
rs_normalized = (rs_ratio - rs_ratio.rolling(252).mean()) / rs_ratio.rolling(252).std()
```

### Implementation

```python
def build_sector_index(ohlcv_df: pd.DataFrame, sector_map: dict) -> pd.DataFrame:
    """
    Build market-cap weighted sector index from individual stocks

    Args:
        ohlcv_df: OHLCV with market_cap column
        sector_map: {symbol: sector_code} from sector_registry

    Returns:
        DataFrame with [date, sector_code, sector_index, total_mcap]
    """
    # Map symbol to sector
    df = ohlcv_df.copy()
    df['sector_code'] = df['symbol'].map(sector_map)
    df = df.dropna(subset=['sector_code', 'market_cap'])

    # Calculate weighted index per sector per day
    df['weighted_close'] = df['close'] * df['market_cap']

    sector_index = df.groupby(['date', 'sector_code']).agg({
        'weighted_close': 'sum',
        'market_cap': 'sum'
    }).reset_index()

    sector_index['sector_index'] = sector_index['weighted_close'] / sector_index['market_cap']
    sector_index = sector_index.rename(columns={'market_cap': 'total_mcap'})

    return sector_index[['date', 'sector_code', 'sector_index', 'total_mcap']]


def calculate_sector_rs(
    sector_index_df: pd.DataFrame,
    vnindex_df: pd.DataFrame,
    lookback: int = 20,
    momentum_period: int = 5
) -> pd.DataFrame:
    """
    Calculate RS ratio and momentum for each sector

    Args:
        sector_index_df: Output from build_sector_index()
        vnindex_df: VN-Index with [date, close]
        lookback: Period for return calculation (default 20 days)
        momentum_period: Period for RS momentum (default 5 days)

    Returns:
        DataFrame with [date, sector_code, rs_ratio, rs_momentum, quadrant]
    """
    # Merge VNIndex
    df = sector_index_df.merge(
        vnindex_df[['date', 'close']].rename(columns={'close': 'vnindex'}),
        on='date'
    )

    # Calculate returns per sector
    df = df.sort_values(['sector_code', 'date'])
    df['sector_return'] = df.groupby('sector_code')['sector_index'].pct_change(lookback)
    df['vnindex_return'] = df['vnindex'].pct_change(lookback)

    # RS Ratio
    df['rs_ratio'] = df['sector_return'] / df['vnindex_return']
    df['rs_ratio'] = df['rs_ratio'].replace([np.inf, -np.inf], np.nan)

    # RS Momentum
    df['rs_momentum'] = df.groupby('sector_code')['rs_ratio'].pct_change(momentum_period) * 100

    # Quadrant assignment
    def assign_quadrant(row):
        if pd.isna(row['rs_ratio']) or pd.isna(row['rs_momentum']):
            return 'UNKNOWN'
        if row['rs_ratio'] > 1 and row['rs_momentum'] > 0:
            return 'LEADING'
        elif row['rs_ratio'] > 1 and row['rs_momentum'] <= 0:
            return 'WEAKENING'
        elif row['rs_ratio'] <= 1 and row['rs_momentum'] <= 0:
            return 'LAGGING'
        else:
            return 'IMPROVING'

    df['quadrant'] = df.apply(assign_quadrant, axis=1)

    return df[['date', 'sector_code', 'sector_index', 'sector_return',
               'rs_ratio', 'rs_momentum', 'quadrant']]
```

### Alternative: Simple Average RS (No Market Cap)

Nếu không muốn dùng market-cap weighted:

```python
def calculate_simple_sector_rs(ohlcv_df: pd.DataFrame, sector_map: dict, vnindex_df: pd.DataFrame) -> pd.DataFrame:
    """
    Simple average return per sector (equal weight)

    Pros: Simpler, less bias toward large caps
    Cons: Small caps with high volatility can distort
    """
    df = ohlcv_df.copy()
    df['sector_code'] = df['symbol'].map(sector_map)

    # Calculate 20-day return per stock
    df = df.sort_values(['symbol', 'date'])
    df['return_20d'] = df.groupby('symbol')['close'].pct_change(20)

    # Average return per sector
    sector_returns = df.groupby(['date', 'sector_code'])['return_20d'].mean().reset_index()
    sector_returns = sector_returns.rename(columns={'return_20d': 'sector_return'})

    # Merge VNIndex and calculate RS
    sector_returns = sector_returns.merge(
        vnindex_df[['date', 'close']].assign(vnindex_return=vnindex_df['close'].pct_change(20)),
        on='date'
    )
    sector_returns['rs_ratio'] = sector_returns['sector_return'] / sector_returns['vnindex_return']

    return sector_returns
```

### Recommendation: Market-Cap Weighted

| Method | Pros | Cons | Use Case |
|--------|------|------|----------|
| **Market-Cap Weighted** | Phản ánh đúng dòng tiền thực | Bias toward large caps (VCB, VIC) | Institutional, thị trường VN |
| Simple Average | Equal representation | Small caps gây nhiễu | Research, backtesting |

**Recommend:** Market-Cap Weighted vì VN market dominated by large caps.

---

## 2. Sector Money Flow

### Input Data
- `DATA/processed/technical/money_flow/sector_money_flow_1d.parquet`

### Available Columns
- `sector`
- `net_value` - Net buy/sell value
- `foreign_net` - Foreign investor flow
- `institution_net` - Institution flow

### Logic
```python
def get_sector_money_flow(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate money flow by sector

    Returns: [sector, net_flow_1d, net_flow_5d, flow_signal]
    """
    latest = df.groupby('sector').agg({
        'net_value': 'sum',
    }).reset_index()

    # 5-day rolling sum
    flow_5d = df.groupby('sector')['net_value'].rolling(5).sum()

    # Signal based on flow direction
    def flow_signal(row):
        if row['net_flow_1d'] > 0 and row['net_flow_5d'] > 0:
            return 'STRONG_INFLOW'
        elif row['net_flow_1d'] > 0:
            return 'INFLOW'
        elif row['net_flow_1d'] < 0 and row['net_flow_5d'] < 0:
            return 'STRONG_OUTFLOW'
        else:
            return 'OUTFLOW'

    latest['flow_signal'] = latest.apply(flow_signal, axis=1)
    return latest
```

---

## 3. Sector Breadth

### Input Data
- `DATA/processed/technical/sector_breadth/sector_breadth_daily.parquet`

### Available Columns
- `sector`
- `pct_above_ma20` - % stocks in sector above MA20
- `pct_above_ma50` - % stocks in sector above MA50
- `strength_score` - Composite strength

### Logic
```python
def get_sector_breadth(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get latest breadth for each sector

    Returns: [sector, pct_above_ma20, pct_above_ma50, breadth_signal]
    """
    latest = df.groupby('sector').last().reset_index()

    def breadth_signal(row):
        if row['pct_above_ma20'] > 70:
            return 'STRONG'
        elif row['pct_above_ma20'] > 50:
            return 'HEALTHY'
        elif row['pct_above_ma20'] > 30:
            return 'WEAK'
        else:
            return 'VERY_WEAK'

    latest['breadth_signal'] = latest.apply(breadth_signal, axis=1)
    return latest
```

---

## 4. Composite Sector Ranking

### Weighting
- RS Score: 40%
- Money Flow: 30%
- Breadth: 30%

### Implementation
```python
def rank_sectors(
    rs_df: pd.DataFrame,
    flow_df: pd.DataFrame,
    breadth_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Create composite ranking for sector rotation

    Returns: [sector, rs_score, flow_score, breadth_score, composite, rank, action]
    """
    # Merge all data
    merged = rs_df.merge(flow_df, on='sector').merge(breadth_df, on='sector')

    # Normalize scores to 0-100
    merged['rs_score'] = (merged['rs_ratio'] - merged['rs_ratio'].min()) / \
                         (merged['rs_ratio'].max() - merged['rs_ratio'].min()) * 100

    merged['flow_score'] = (merged['net_flow_1d'] - merged['net_flow_1d'].min()) / \
                           (merged['net_flow_1d'].max() - merged['net_flow_1d'].min()) * 100

    merged['breadth_score'] = merged['pct_above_ma20']  # Already 0-100

    # Composite score
    merged['composite'] = (
        0.4 * merged['rs_score'] +
        0.3 * merged['flow_score'] +
        0.3 * merged['breadth_score']
    )

    # Rank and action
    merged['rank'] = merged['composite'].rank(ascending=False).astype(int)

    def action(row):
        if row['rank'] <= 5:  # Top 5 sectors
            return 'OVERWEIGHT'
        elif row['rank'] <= 12:  # Middle
            return 'NEUTRAL'
        else:  # Bottom 7
            return 'UNDERWEIGHT'

    merged['action'] = merged.apply(action, axis=1)

    return merged.sort_values('rank')
```

---

## 5. RRG Quadrant Logic

### Relative Rotation Graph (RRG)
Visual representation of sector rotation cycle:

```
        RS Momentum (+)
              ↑
              │
   IMPROVING  │  LEADING
      ↗       │       ↘
              │
←─────────────┼─────────────→ RS Ratio
              │              1.0
      ↖       │       ↙
   LAGGING    │  WEAKENING
              │
              ↓
        RS Momentum (-)
```

### Rotation Cycle
```
LAGGING → IMPROVING → LEADING → WEAKENING → LAGGING
   ↑_______________________________________________|
```

### Trading Implications
| Quadrant | Position | Action |
|----------|----------|--------|
| LEADING | Full | Hold/Add |
| WEAKENING | Reduce | Take profit |
| LAGGING | Avoid | Stay out |
| IMPROVING | Build | Accumulate |

---

## 6. Output Schema

### SectorState Dataclass
```python
@dataclass
class SectorState:
    date: datetime
    sector: str
    sector_return_20d: float
    rs_ratio: float
    rs_momentum: float
    quadrant: str  # LEADING/WEAKENING/LAGGING/IMPROVING
    net_flow_1d: float
    net_flow_5d: float
    flow_signal: str
    pct_above_ma20: float
    pct_above_ma50: float
    breadth_signal: str
    composite_score: float
    rank: int
    action: str  # OVERWEIGHT/NEUTRAL/UNDERWEIGHT
```

### Output File
```
DATA/processed/technical/sector_rotation/sector_rotation_daily.parquet
```

---

## 7. File Structure

```
PROCESSORS/technical/sector/
├── __init__.py
├── sector_rotation.py       # Main module
│   ├── calculate_sector_rs()
│   ├── get_sector_money_flow()
│   ├── get_sector_breadth()
│   ├── rank_sectors()
│   └── generate_sector_state()
└── sector_dashboard_data.py # Dashboard data prep
```

---

## 8. Dashboard Components

### 12_sector_rotation.py

```
┌─────────────────────────────────────────────────────────────────┐
│                     SECTOR ROTATION                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    RRG SCATTER PLOT                        │  │
│  │                                                            │  │
│  │          IMPROVING    │    LEADING                         │  │
│  │              ●CTG     │        ●VCB                        │  │
│  │         ●Securities   │    ●Banking                        │  │
│  │  ─────────────────────┼─────────────────────               │  │
│  │              ●Steel   │        ●Real Estate                │  │
│  │          LAGGING      │    WEAKENING                       │  │
│  │                       │                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                 SECTOR RANKING TABLE                       │  │
│  │ Rank │ Sector      │ RS   │ Flow  │ Breadth │ Action      │  │
│  │ 1    │ Ngân hàng   │ 1.15 │ +500B │ 72%     │ OVERWEIGHT  │  │
│  │ 2    │ Chứng khoán │ 1.08 │ +200B │ 65%     │ OVERWEIGHT  │  │
│  │ 3    │ Công nghệ   │ 1.02 │ +100B │ 58%     │ OVERWEIGHT  │  │
│  │ ...                                                        │  │
│  │ 19   │ Thép        │ 0.75 │ -300B │ 25%     │ UNDERWEIGHT │  │
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
└─────────────────────────────────────────────────────────────────┘
```

### RRG Chart Implementation (Plotly)

```python
import plotly.graph_objects as go

def create_rrg_chart(sector_rs_df: pd.DataFrame) -> go.Figure:
    """
    Create Relative Rotation Graph (RRG) scatter plot

    Args:
        sector_rs_df: DataFrame with [sector_code, rs_ratio, rs_momentum, quadrant]

    Returns:
        Plotly figure with RRG chart
    """
    # Color mapping for quadrants
    quadrant_colors = {
        'LEADING': '#4CAF50',     # Green
        'WEAKENING': '#FF9800',   # Orange
        'LAGGING': '#F44336',     # Red
        'IMPROVING': '#2196F3'    # Blue
    }

    fig = go.Figure()

    # Add scatter points for each sector
    for _, row in sector_rs_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['rs_ratio']],
            y=[row['rs_momentum']],
            mode='markers+text',
            marker=dict(
                size=15,
                color=quadrant_colors.get(row['quadrant'], 'gray'),
                line=dict(width=2, color='white')
            ),
            text=[row['sector_code']],
            textposition='top center',
            name=row['sector_code'],
            hovertemplate=(
                f"<b>{row['sector_code']}</b><br>"
                f"RS Ratio: {row['rs_ratio']:.3f}<br>"
                f"RS Momentum: {row['rs_momentum']:.1f}%<br>"
                f"Quadrant: {row['quadrant']}"
                "<extra></extra>"
            )
        ))

    # Add quadrant lines
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=1, line_dash="dash", line_color="gray", opacity=0.5)

    # Add quadrant labels
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
        title='Sector Relative Rotation Graph (RRG)',
        xaxis_title='RS Ratio (Relative Strength)',
        yaxis_title='RS Momentum (%)',
        height=500,
        showlegend=False,
        xaxis=dict(range=[0.7, 1.3]),
        yaxis=dict(range=[-10, 10])
    )

    return fig


def create_rrg_trail_chart(sector_rs_history: pd.DataFrame, trail_days: int = 5) -> go.Figure:
    """
    Create RRG with trailing path showing sector movement over time

    Args:
        sector_rs_history: Historical RS data with [date, sector_code, rs_ratio, rs_momentum]
        trail_days: Number of days to show trail

    Returns:
        Plotly figure with RRG trail chart
    """
    fig = go.Figure()

    # Get unique sectors
    sectors = sector_rs_history['sector_code'].unique()

    quadrant_colors = {
        'LEADING': '#4CAF50',
        'WEAKENING': '#FF9800',
        'LAGGING': '#F44336',
        'IMPROVING': '#2196F3'
    }

    for sector in sectors:
        sector_data = sector_rs_history[
            sector_rs_history['sector_code'] == sector
        ].tail(trail_days).sort_values('date')

        if len(sector_data) < 2:
            continue

        latest = sector_data.iloc[-1]

        # Trail line (fading opacity)
        fig.add_trace(go.Scatter(
            x=sector_data['rs_ratio'],
            y=sector_data['rs_momentum'],
            mode='lines',
            line=dict(
                color=quadrant_colors.get(latest['quadrant'], 'gray'),
                width=2
            ),
            opacity=0.5,
            showlegend=False,
            hoverinfo='skip'
        ))

        # Current position marker
        fig.add_trace(go.Scatter(
            x=[latest['rs_ratio']],
            y=[latest['rs_momentum']],
            mode='markers+text',
            marker=dict(
                size=12,
                color=quadrant_colors.get(latest['quadrant'], 'gray'),
                line=dict(width=2, color='white')
            ),
            text=[sector],
            textposition='top center',
            name=sector,
            hovertemplate=(
                f"<b>{sector}</b><br>"
                f"RS: {latest['rs_ratio']:.3f}<br>"
                f"Mom: {latest['rs_momentum']:.1f}%<br>"
                f"{latest['quadrant']}"
                "<extra></extra>"
            )
        ))

    # Quadrant lines and labels (same as above)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=1, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        title=f'Sector RRG with {trail_days}-Day Trail',
        xaxis_title='RS Ratio',
        yaxis_title='RS Momentum (%)',
        height=500,
        showlegend=False,
        xaxis=dict(range=[0.7, 1.3]),
        yaxis=dict(range=[-10, 10])
    )

    return fig
```

### Daily Pipeline

```python
# File: PROCESSORS/technical/sector/daily_sector_rs_update.py

def run_daily_sector_rs_pipeline():
    """
    Daily update pipeline for Sector RS calculation

    Run time: 6:40 PM (after OHLCV update)
    """
    import pandas as pd
    import json
    from pathlib import Path

    # 1. Load inputs
    ohlcv = pd.read_parquet('DATA/raw/ohlcv/OHLCV_mktcap.parquet')
    vnindex = pd.read_parquet('DATA/processed/technical/vnindex/vnindex_indicators.parquet')

    with open('config/metadata_registry/sectors/sector_industry_registry.json') as f:
        registry = json.load(f)

    # Create symbol → sector mapping
    sector_map = {}
    for sector, data in registry['sectors'].items():
        for ticker in data.get('tickers', []):
            sector_map[ticker] = sector

    # 2. Build sector index
    sector_index = build_sector_index(ohlcv, sector_map)

    # 3. Calculate RS
    sector_rs = calculate_sector_rs(sector_index, vnindex)

    # 4. Save output
    output_path = Path('DATA/processed/technical/sector_rotation/sector_rs_daily.parquet')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sector_rs.to_parquet(output_path, index=False)

    print(f"✅ Sector RS updated: {len(sector_rs)} records")
    return sector_rs
```

---

## 9. VN Market Sector Mapping

### 19 Sectors
| # | Sector (VN) | Sector (EN) | Key Tickers |
|---|-------------|-------------|-------------|
| 1 | Ngân hàng | Banking | VCB, ACB, TCB, MBB |
| 2 | Bất động sản | Real Estate | VIC, VHM, NVL |
| 3 | Chứng khoán | Securities | SSI, VND, HCM |
| 4 | Thực phẩm | Food & Beverage | VNM, MSN, SAB |
| 5 | Xây dựng | Construction | CTD, HBC, VCG |
| 6 | Công nghệ | Technology | FPT, CMG |
| 7 | Bảo hiểm | Insurance | BVH, MIG, PVI |
| 8 | Điện | Utilities | POW, GEG, PC1 |
| 9 | Dầu khí | Oil & Gas | GAS, PVD, PVS |
| 10 | Thép | Steel | HPG, HSG, NKG |
| 11 | Hóa chất | Chemicals | DPM, DCM, DGC |
| 12 | Dệt may | Textiles | TCM, MSH, TNG |
| 13 | Cao su | Rubber | GVR, PHR, DPR |
| 14 | Hàng không | Aviation | VJC, HVN |
| 15 | Cảng biển | Ports | GMD, VSC |
| 16 | Bán lẻ | Retail | MWG, PNJ, DGW |
| 17 | Thuỷ sản | Seafood | VHC, ANV, IDI |
| 18 | Dược phẩm | Pharmaceuticals | DHG, IMP, DMC |
| 19 | Vật liệu XD | Building Materials | HT1, BCC, VGC |

---

## 10. Implementation Checklist

- [ ] Create `PROCESSORS/technical/sector/sector_rotation.py`
- [ ] Implement `build_sector_index()` (market-cap weighted)
- [ ] Implement `calculate_sector_rs()` with quadrant assignment
- [ ] Implement `get_sector_money_flow()`
- [ ] Implement `get_sector_breadth()`
- [ ] Implement `rank_sectors()` with composite scoring
- [ ] Create `daily_sector_rs_update.py` pipeline
- [ ] Create output: `sector_rs_daily.parquet`
- [ ] Build RRG scatter plot with `create_rrg_chart()`
- [ ] Build RRG trail chart with `create_rrg_trail_chart()`
- [ ] Build sector ranking table in Streamlit
- [ ] Build money flow heatmap
- [ ] Test RS calculation with historical data
- [ ] Validate quadrant rotation cycle
