# TA Systematic Trading System - Implementation Plan

**Date:** 2025-12-24
**Status:** Ready for Implementation
**Validated:** Backtest completed (see `251223-ta-backtest-experiments/`)

---

## Overview

Three-layer technical evaluation system for VN stock market:
1. **MARKET** → Macro trend & exposure control
2. **SECTOR** → Rotation & relative strength
3. **STOCK** → Entry/exit signals & position sizing

**Core Principle:** KISS - 8 indicators maximum, each validated by backtest.

---

## Validated Indicator Set (8 Total)

| # | Indicator | Layer | Backtest Result |
|---|-----------|-------|-----------------|
| 1 | EMA 9/21 | Market + Stock | PF 1.87, +2.47% avg |
| 2 | % > MA20 | Market | -58% DD reduction |
| 3 | RVOL | Stock | Volume confirmation |
| 4 | Sector RS | Sector | Rotation matrix |
| 5 | VSA Patterns | Stock | 54% WR (stopping vol) |
| 6 | ATR | Stock | Position sizing |
| 7 | Market Cap | Filter | >= 5,000 tỷ liquidity |
| 8 | Swing H/L | Stock | Breakout levels |

---

## Phase 1: Market Layer

**Goal:** Determine market regime & exposure level

### Functions to Implement

```python
# File: PROCESSORS/technical/market/market_analyzer.py

def get_market_regime(vnindex_df: pd.DataFrame) -> str:
    """
    Returns: 'BULLISH' | 'NEUTRAL' | 'BEARISH'
    Logic: EMA9 vs EMA21 on VN-Index
    """

def get_breadth_score(breadth_df: pd.DataFrame) -> float:
    """
    Returns: 0-100 (% stocks > MA20)
    Source: market_breadth_daily.parquet
    """

def calculate_exposure_level(regime: str, breadth: float) -> int:
    """
    Returns: 100 | 80 | 60 | 40 | 20 | 0 (% allocation)

    Logic:
    - EMA9 > EMA21 + Breadth >= 70% → 100%
    - EMA9 > EMA21 + Breadth 55-70% → 80%
    - EMA9 > EMA21 + Breadth 40-55% → 60%
    - EMA9 > EMA21 + Breadth 25-40% → 40%
    - EMA9 > EMA21 + Breadth < 25%  → 20%
    - EMA9 < EMA21 (any breadth)    → 0%
    """

def detect_breadth_divergence(vnindex_df: pd.DataFrame, breadth_df: pd.DataFrame) -> dict:
    """
    Returns: {'type': 'BULLISH'|'BEARISH'|None, 'strength': 1-3}

    BULLISH: VNIndex making lower lows, breadth making higher lows
    BEARISH: VNIndex making higher highs, breadth making lower highs
    """
```

### Output: Market Dashboard Data

```python
@dataclass
class MarketState:
    date: datetime
    vnindex_close: float
    regime: str  # BULLISH/NEUTRAL/BEARISH
    ema9: float
    ema21: float
    breadth_ma20_pct: float
    breadth_ma50_pct: float
    exposure_level: int  # 0-100
    divergence: Optional[dict]
    signal: str  # RISK_ON / RISK_OFF / CAUTION
```

---

## Phase 2: Sector Layer

**Goal:** Identify leading/lagging sectors for rotation

### Functions to Implement

```python
# File: PROCESSORS/technical/sector/sector_rotation.py

def calculate_sector_rs(sector_returns: pd.DataFrame, benchmark_return: float) -> pd.DataFrame:
    """
    Returns: DataFrame with columns [sector, rs_ratio, rs_momentum, quadrant]

    RS Ratio = Sector 20d Return / VNIndex 20d Return
    RS Momentum = 5-day change in RS Ratio

    Quadrants (RRG-style):
    - LEADING: RS > 1, Momentum > 0
    - WEAKENING: RS > 1, Momentum < 0
    - LAGGING: RS < 1, Momentum < 0
    - IMPROVING: RS < 1, Momentum > 0
    """

def get_sector_money_flow(money_flow_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns: DataFrame with [sector, net_flow_1d, net_flow_5d, flow_signal]
    Source: sector_money_flow_1d.parquet
    """

def get_sector_breadth(sector_breadth_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns: DataFrame with [sector, pct_above_ma20, pct_above_ma50, strength_score]
    Source: sector_breadth_daily.parquet
    """

def rank_sectors(rs_df: pd.DataFrame, flow_df: pd.DataFrame, breadth_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns: DataFrame with [sector, composite_score, rank, action]

    Composite = 0.4 * RS_score + 0.3 * Flow_score + 0.3 * Breadth_score
    Action: OVERWEIGHT | NEUTRAL | UNDERWEIGHT
    """
```

### Output: Sector Rotation Matrix

```python
@dataclass
class SectorState:
    date: datetime
    sector: str
    rs_ratio: float
    rs_momentum: float
    quadrant: str  # LEADING/WEAKENING/LAGGING/IMPROVING
    net_flow_1d: float
    breadth_score: float
    composite_rank: int
    action: str  # OVERWEIGHT/NEUTRAL/UNDERWEIGHT
```

---

## Phase 3: Stock Layer

**Goal:** Generate buy/sell signals with position sizing

### Functions to Implement

```python
# File: PROCESSORS/technical/stock/signal_generator.py

def detect_ema_cross(ohlcv_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns: DataFrame with [symbol, date, signal_type, ema9, ema21]
    signal_type: 'CROSS_UP' | 'CROSS_DOWN' | None
    """

def calculate_rvol(ohlcv_df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    Returns: Series of relative volume (volume / avg_volume)
    """

def detect_vsa_patterns(ohlcv_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns: DataFrame with [symbol, date, pattern, signal]

    Patterns:
    - STOPPING_VOLUME: Downtrend + High vol + Close near high
    - NO_DEMAND: Up candle + Low vol + Narrow spread
    - CLIMAX_UP: Uptrend + Very high vol + Wide spread + Close near high
    - CLIMAX_DOWN: Downtrend + Very high vol + Wide spread + Close near low
    """

def detect_breakout(ohlcv_df: pd.DataFrame, swing_period: int = 10) -> pd.DataFrame:
    """
    Returns: DataFrame with [symbol, date, breakout_type, volume_confirm]
    breakout_type: 'SWING_HIGH_BREAK' | 'SWING_LOW_BREAK'
    volume_confirm: True if RVOL > 1.3
    """

def calculate_position_size(
    capital: float,
    risk_pct: float,
    entry_price: float,
    atr: float,
    exposure_level: int
) -> dict:
    """
    Returns: {
        'shares': int,
        'position_value': float,
        'stop_loss': float,
        'risk_amount': float
    }

    Formula:
    - Stop = Entry - (ATR × 1.5)
    - Risk per share = Entry - Stop
    - Max risk = Capital × risk_pct × (exposure_level / 100)
    - Shares = Max risk / Risk per share
    """
```

### Buy/Sell List Generator

```python
# File: PROCESSORS/technical/stock/list_generator.py

def generate_buy_list(
    signals_df: pd.DataFrame,
    market_state: MarketState,
    sector_ranks: pd.DataFrame,
    min_mcap: float = 5000  # tỷ VND
) -> pd.DataFrame:
    """
    Returns top 10 buy candidates

    Filters:
    1. Market exposure > 0
    2. Sector in top 50% by rank
    3. Market cap >= 5,000 tỷ
    4. EMA cross up OR VSA stopping volume
    5. RVOL >= 0.8

    Columns: [symbol, sector, signal, entry_price, stop_loss, target, position_size]
    """

def generate_sell_list(
    holdings_df: pd.DataFrame,
    signals_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Returns stocks to exit

    Exit conditions:
    1. EMA cross down
    2. VSA No Demand pattern
    3. Stop loss hit (Entry - 1.5 × ATR)
    4. Market exposure = 0

    Columns: [symbol, entry_price, current_price, pnl_pct, exit_reason]
    """
```

---

## Data Pipeline

### Daily Update Flow

```
1. OHLCV Update (6:30 PM)
   └── technical_processor.py
       ├── Calculate EMA9, EMA21, RSI, MACD, ATR
       ├── Calculate RVOL
       └── Detect patterns (candlestick, VSA)

2. Market Analysis (6:35 PM)
   └── market_analyzer.py
       ├── Get VN-Index regime
       ├── Calculate breadth
       └── Set exposure level

3. Sector Analysis (6:40 PM)
   └── sector_rotation.py
       ├── Calculate sector RS
       ├── Get money flow
       └── Rank sectors

4. Signal Generation (6:45 PM)
   └── signal_generator.py
       ├── Detect EMA crosses
       ├── Detect breakouts
       └── Detect VSA patterns

5. List Generation (6:50 PM)
   └── list_generator.py
       ├── Generate buy list
       └── Generate sell list
```

### Output Files

```
DATA/processed/technical/
├── market_state/
│   └── market_state_daily.parquet
├── sector_rotation/
│   └── sector_rotation_daily.parquet
├── signals/
│   ├── ema_signals_daily.parquet
│   ├── breakout_signals_daily.parquet
│   └── vsa_signals_daily.parquet
└── lists/
    ├── buy_list_daily.parquet
    └── sell_list_daily.parquet
```

---

## Dashboard Integration

### Streamlit Pages

```
WEBAPP/pages/
├── 11_market_overview.py      # Market regime, breadth, exposure
├── 12_sector_rotation.py      # RRG chart, sector ranks
├── 13_stock_scanner.py        # Signal scanner, filters
└── 14_trading_lists.py        # Buy/Sell lists with sizing
```

### Key Visualizations

1. **Market Layer**
   - Breadth gauge (0-100%)
   - Regime traffic light (🟢🟡🔴)
   - Exposure recommendation bar

2. **Sector Layer**
   - RRG scatter plot (RS vs Momentum)
   - Money flow heatmap
   - Sector ranking table

3. **Stock Layer**
   - Signal scanner with filters
   - Buy list with position sizes
   - Sell list with exit reasons

---

## Implementation Order

### Week 1: Market Layer
- [ ] Implement `market_analyzer.py`
- [ ] Add breadth divergence detection
- [ ] Create market state output
- [ ] Build `11_market_overview.py` dashboard

### Week 2: Sector Layer
- [ ] Implement `sector_rotation.py`
- [ ] Calculate RS and momentum
- [ ] Integrate money flow data
- [ ] Build `12_sector_rotation.py` dashboard

### Week 3: Stock Layer
- [ ] Implement `signal_generator.py`
- [ ] Add VSA pattern detection
- [ ] Implement position sizing
- [ ] Build `13_stock_scanner.py` dashboard

### Week 4: Integration
- [ ] Implement `list_generator.py`
- [ ] Create daily pipeline orchestrator
- [ ] Build `14_trading_lists.py` dashboard
- [ ] End-to-end testing

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Signal accuracy | > 50% WR | Backtest validation |
| Drawdown reduction | > 50% vs B&H | Variable exposure |
| Dashboard load time | < 3 sec | Performance testing |
| Daily update time | < 5 min | Pipeline timing |

---

## Files Reference

- Backtest results: `plans/251223-ta-backtest-experiments/BACKTEST_RESULTS.md`
- Indicator specs: `TA_indicator.md`
- Existing breadth: `DATA/processed/technical/market_breadth/`
- Existing signals: `DATA/processed/technical/alerts/`
