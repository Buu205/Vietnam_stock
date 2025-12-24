# Phase 3: Stock Layer Implementation

**Goal:** Generate buy/sell signals with position sizing for individual stocks

---

## 1. EMA Cross Detection

### Validated Performance
- Win Rate: 33.4%
- Avg PnL: +2.47%
- Profit Factor: 1.87
- Avg Holding: 37 days

### Implementation
```python
def detect_ema_cross(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect EMA 9/21 crossovers for all stocks

    Input: OHLCV with ema9, ema21 columns
    Returns: [symbol, date, signal_type, ema9, ema21, price]
    """
    df = df.copy()

    # Cross detection
    df['ema_cross_up'] = (df['ema9'] > df['ema21']) & (df['ema9'].shift(1) <= df['ema21'].shift(1))
    df['ema_cross_down'] = (df['ema9'] < df['ema21']) & (df['ema9'].shift(1) >= df['ema21'].shift(1))

    # Filter signals
    signals = df[df['ema_cross_up'] | df['ema_cross_down']].copy()

    signals['signal_type'] = np.where(signals['ema_cross_up'], 'CROSS_UP', 'CROSS_DOWN')

    return signals[['symbol', 'date', 'signal_type', 'ema9', 'ema21', 'close']]
```

---

## 2. Relative Volume (RVOL)

### Purpose
Confirm signal strength with volume

### Thresholds
- RVOL >= 1.3 → Strong volume (breakout confirmation)
- RVOL >= 0.8 → Normal volume (EMA cross valid)
- RVOL < 0.8 → Weak volume (potential false signal)

### Implementation
```python
def calculate_rvol(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    Relative Volume = Current Volume / Average Volume

    Returns: Series with RVOL values
    """
    avg_volume = df.groupby('symbol')['volume'].rolling(period).mean()
    return df['volume'] / avg_volume.reset_index(level=0, drop=True)
```

---

## 3. VSA Pattern Detection

### Patterns Implemented

#### 3.1 Stopping Volume (Bullish)
- **Context:** Downtrend (close < MA20)
- **Volume:** High (RVOL > 1.3)
- **Spread:** Narrow (< avg spread)
- **Close:** Near high (close_position > 0.55)

```python
def detect_stopping_volume(df: pd.DataFrame) -> pd.Series:
    """Stopping Volume = Smart money absorbing selling"""
    in_downtrend = df['close'] < df['ma20']
    high_vol = df['rvol'] > 1.3
    close_near_high = (df['close'] - df['low']) / (df['high'] - df['low']) > 0.55
    narrow_spread = df['spread'] < df['spread'].rolling(20).mean()

    return in_downtrend & high_vol & close_near_high & narrow_spread
```

#### 3.2 No Demand (Bearish)
- **Context:** Uptrend (close > MA20)
- **Candle:** Up candle (close > open)
- **Volume:** Low (RVOL < 0.8)
- **Spread:** Narrow

```python
def detect_no_demand(df: pd.DataFrame) -> pd.Series:
    """No Demand = Lack of buying interest in uptrend"""
    in_uptrend = df['close'] > df['ma20']
    up_candle = df['close'] > df['open']
    low_vol = df['rvol'] < 0.8
    narrow_spread = df['spread'] < df['spread'].rolling(20).mean()

    return in_uptrend & up_candle & low_vol & narrow_spread
```

#### 3.3 Climax Volume (Reversal Warning)
- **Volume:** Very high (RVOL > 2.0)
- **Spread:** Wide
- **Close:** Near extreme (high for up climax, low for down climax)

```python
def detect_climax(df: pd.DataFrame) -> pd.DataFrame:
    """Climax = Exhaustion move, potential reversal"""
    very_high_vol = df['rvol'] > 2.0
    wide_spread = df['spread'] > df['spread'].rolling(20).mean() * 1.5

    # Up Climax
    close_near_high = (df['close'] - df['low']) / (df['high'] - df['low']) > 0.8
    up_climax = very_high_vol & wide_spread & close_near_high

    # Down Climax
    close_near_low = (df['close'] - df['low']) / (df['high'] - df['low']) < 0.2
    down_climax = very_high_vol & wide_spread & close_near_low

    df['up_climax'] = up_climax
    df['down_climax'] = down_climax

    return df
```

---

## 4. Breakout Detection

### Validated Performance
- Win Rate: 50.9% (10-day hold)
- Avg PnL: +1.21%

### Implementation
```python
def detect_breakout(df: pd.DataFrame, swing_period: int = 10) -> pd.DataFrame:
    """
    Detect price breakouts above swing high with volume confirmation

    Returns: [symbol, date, breakout_type, swing_level, rvol, volume_confirm]
    """
    df = df.copy()

    # Calculate swing points
    df['swing_high'] = df.groupby('symbol')['high'].rolling(swing_period).max().shift(1)
    df['swing_low'] = df.groupby('symbol')['low'].rolling(swing_period).min().shift(1)

    # Breakout conditions
    df['break_high'] = df['close'] > df['swing_high']
    df['break_low'] = df['close'] < df['swing_low']

    # Volume confirmation
    df['volume_confirm'] = df['rvol'] > 1.3

    # Filter breakouts
    breakouts = df[df['break_high'] | df['break_low']].copy()
    breakouts['breakout_type'] = np.where(breakouts['break_high'], 'SWING_HIGH_BREAK', 'SWING_LOW_BREAK')

    return breakouts[['symbol', 'date', 'breakout_type', 'swing_high', 'swing_low', 'rvol', 'volume_confirm', 'close']]
```

---

## 5. Position Sizing

### Formula
```
Stop Loss = Entry Price - (ATR × 1.5)
Risk per Share = Entry Price - Stop Loss
Max Risk Amount = Capital × Risk% × (Exposure Level / 100)
Position Size = Max Risk Amount / Risk per Share
```

### Implementation
```python
def calculate_position_size(
    capital: float,
    risk_pct: float,  # e.g., 0.01 for 1%
    entry_price: float,
    atr: float,
    exposure_level: int  # 0-100
) -> dict:
    """
    Calculate position size based on ATR-based stop loss

    Returns: {
        'shares': int,
        'position_value': float,
        'stop_loss': float,
        'target': float,
        'risk_amount': float,
        'risk_reward': float
    }
    """
    # Stop loss calculation
    stop_distance = atr * 1.5
    stop_loss = entry_price - stop_distance

    # Risk per share
    risk_per_share = stop_distance

    # Adjusted capital based on exposure
    adjusted_capital = capital * (exposure_level / 100)

    # Max risk amount
    max_risk = adjusted_capital * risk_pct

    # Position size
    shares = int(max_risk / risk_per_share)

    # Position value
    position_value = shares * entry_price

    # Target (2:1 reward/risk)
    target = entry_price + (stop_distance * 2)

    return {
        'shares': shares,
        'position_value': round(position_value, 0),
        'stop_loss': round(stop_loss, 0),
        'target': round(target, 0),
        'risk_amount': round(max_risk, 0),
        'risk_reward': 2.0
    }
```

### Example
```python
# Capital: 1,000,000,000 VND (1 tỷ)
# Risk: 1% per trade
# Exposure: 80%
# Entry: 25,000 VND
# ATR: 500 VND

result = calculate_position_size(
    capital=1_000_000_000,
    risk_pct=0.01,
    entry_price=25000,
    atr=500,
    exposure_level=80
)

# Result:
# shares: 10,666
# position_value: 266,650,000 VND
# stop_loss: 24,250 VND
# target: 26,500 VND
# risk_amount: 8,000,000 VND
```

---

## 6. Buy/Sell List Generator

### Buy List Filters
```python
def generate_buy_list(
    ema_signals: pd.DataFrame,
    vsa_signals: pd.DataFrame,
    breakout_signals: pd.DataFrame,
    market_state: MarketState,
    sector_ranks: pd.DataFrame,
    ticker_info: pd.DataFrame,  # With market cap
    capital: float = 1_000_000_000,
    risk_pct: float = 0.01,
    min_mcap: float = 5000  # tỷ VND
) -> pd.DataFrame:
    """
    Generate ranked buy list with position sizing

    Filters applied:
    1. Market exposure > 0
    2. Sector in top 50% (rank <= 10)
    3. Market cap >= 5,000 tỷ
    4. Valid signal (EMA cross up OR VSA stopping OR Breakout with volume)
    5. RVOL >= 0.8

    Returns top 10 candidates with position sizing
    """
    # Check market exposure
    if market_state.exposure_level == 0:
        return pd.DataFrame()  # No buys in bearish regime

    # Combine signals
    buy_signals = pd.concat([
        ema_signals[ema_signals['signal_type'] == 'CROSS_UP'],
        vsa_signals[vsa_signals['pattern'] == 'STOPPING_VOLUME'],
        breakout_signals[breakout_signals['volume_confirm']]
    ])

    # Apply filters
    buy_signals = buy_signals.merge(ticker_info[['symbol', 'market_cap', 'sector']], on='symbol')
    buy_signals = buy_signals.merge(sector_ranks[['sector', 'rank']], on='sector')

    # Filter conditions
    buy_signals = buy_signals[
        (buy_signals['market_cap'] >= min_mcap) &
        (buy_signals['rank'] <= 10) &  # Top 50% sectors
        (buy_signals['rvol'] >= 0.8)
    ]

    # Calculate position size for each
    buy_signals['position'] = buy_signals.apply(
        lambda row: calculate_position_size(
            capital=capital,
            risk_pct=risk_pct,
            entry_price=row['close'],
            atr=row['atr'],
            exposure_level=market_state.exposure_level
        ),
        axis=1
    )

    # Unpack position dict
    buy_signals['shares'] = buy_signals['position'].apply(lambda x: x['shares'])
    buy_signals['stop_loss'] = buy_signals['position'].apply(lambda x: x['stop_loss'])
    buy_signals['target'] = buy_signals['position'].apply(lambda x: x['target'])

    # Rank by signal quality
    buy_signals['score'] = (
        buy_signals['rvol'] * 0.4 +
        (11 - buy_signals['rank']) * 0.3 +
        buy_signals['market_cap'].rank(pct=True) * 0.3
    )

    return buy_signals.nlargest(10, 'score')[
        ['symbol', 'sector', 'close', 'signal_type', 'rvol',
         'shares', 'stop_loss', 'target', 'score']
    ]
```

### Sell List Generator
```python
def generate_sell_list(
    holdings: pd.DataFrame,  # Current positions
    ema_signals: pd.DataFrame,
    vsa_signals: pd.DataFrame,
    current_prices: pd.DataFrame,
    market_state: MarketState
) -> pd.DataFrame:
    """
    Generate sell list with exit reasons

    Exit conditions:
    1. EMA cross down
    2. VSA No Demand pattern
    3. Stop loss hit
    4. Market exposure = 0 (emergency exit)

    Returns: [symbol, entry_price, current_price, pnl_pct, exit_reason, urgency]
    """
    sell_list = []

    for _, holding in holdings.iterrows():
        symbol = holding['symbol']
        entry_price = holding['entry_price']
        stop_loss = holding['stop_loss']

        current = current_prices[current_prices['symbol'] == symbol].iloc[0]
        current_price = current['close']

        pnl_pct = (current_price - entry_price) / entry_price * 100

        exit_reason = None
        urgency = 'LOW'

        # Check conditions
        if market_state.exposure_level == 0:
            exit_reason = 'MARKET_BEARISH'
            urgency = 'HIGH'

        elif current_price <= stop_loss:
            exit_reason = 'STOP_LOSS_HIT'
            urgency = 'HIGH'

        elif symbol in ema_signals[ema_signals['signal_type'] == 'CROSS_DOWN']['symbol'].values:
            exit_reason = 'EMA_CROSS_DOWN'
            urgency = 'MEDIUM'

        elif symbol in vsa_signals[vsa_signals['pattern'] == 'NO_DEMAND']['symbol'].values:
            exit_reason = 'VSA_NO_DEMAND'
            urgency = 'LOW'

        if exit_reason:
            sell_list.append({
                'symbol': symbol,
                'entry_price': entry_price,
                'current_price': current_price,
                'pnl_pct': round(pnl_pct, 2),
                'exit_reason': exit_reason,
                'urgency': urgency
            })

    return pd.DataFrame(sell_list).sort_values('urgency', ascending=False)
```

---

## 7. Output Schema

### Signal Output
```python
@dataclass
class StockSignal:
    date: datetime
    symbol: str
    sector: str
    signal_type: str  # EMA_CROSS_UP, BREAKOUT, STOPPING_VOL, etc.
    price: float
    ema9: float
    ema21: float
    rvol: float
    atr: float
    market_cap: float
    sector_rank: int
    signal_strength: str  # STRONG/MODERATE/WEAK
```

### Buy List Output
```python
@dataclass
class BuyCandidate:
    date: datetime
    symbol: str
    sector: str
    signal_type: str
    entry_price: float
    stop_loss: float
    target: float
    shares: int
    position_value: float
    risk_amount: float
    rvol: float
    score: float
```

### Output Files
```
DATA/processed/technical/signals/
├── ema_signals_daily.parquet
├── breakout_signals_daily.parquet
├── vsa_signals_daily.parquet
└── combined_signals_daily.parquet

DATA/processed/technical/lists/
├── buy_list_daily.parquet
└── sell_list_daily.parquet
```

---

## 8. File Structure

```
PROCESSORS/technical/stock/
├── __init__.py
├── signal_generator.py      # Main signal module
│   ├── detect_ema_cross()
│   ├── calculate_rvol()
│   ├── detect_vsa_patterns()
│   └── detect_breakout()
├── position_sizer.py        # Position sizing
│   └── calculate_position_size()
├── list_generator.py        # Buy/Sell lists
│   ├── generate_buy_list()
│   └── generate_sell_list()
└── stock_dashboard_data.py  # Dashboard prep
```

---

## 9. Dashboard Components

### 13_stock_scanner.py

```
┌─────────────────────────────────────────────────────────────────┐
│                     STOCK SCANNER                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Filters:                                                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │
│  │ Signal ▼ │ │ Sector ▼ │ │ RVOL >=  │ │ Market Cap >=    │    │
│  │ All      │ │ All      │ │   0.8    │ │   5,000 tỷ       │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘    │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    SIGNAL TABLE                            │  │
│  │ Symbol │ Sector    │ Signal      │ Price  │ RVOL │ Score  │  │
│  │ ACB    │ Ngân hàng │ EMA_CROSS   │ 25,500 │ 1.45 │ 85     │  │
│  │ FPT    │ Công nghệ │ BREAKOUT    │ 95,000 │ 1.82 │ 82     │  │
│  │ VNM    │ Thực phẩm │ STOPPING_VOL│ 72,000 │ 1.55 │ 78     │  │
│  │ ...                                                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 14_trading_lists.py

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRADING LISTS                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    BUY LIST (Top 10)                     │    │
│  │ # │ Symbol │ Sector    │ Entry  │ Stop   │ Target │ Size │    │
│  │ 1 │ ACB    │ Ngân hàng │ 25,500 │ 24,250 │ 27,500 │ 10K  │    │
│  │ 2 │ FPT    │ Công nghệ │ 95,000 │ 92,000 │ 101K   │ 2.5K │    │
│  │ 3 │ VNM    │ Thực phẩm │ 72,000 │ 70,500 │ 75,000 │ 3.5K │    │
│  │ ...                                                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    SELL LIST                             │    │
│  │ Symbol │ Entry  │ Current │ PnL%   │ Reason      │ Urgency│   │
│  │ VIC    │ 45,000 │ 42,500  │ -5.6%  │ STOP_LOSS   │ 🔴 HIGH│   │
│  │ HPG    │ 28,000 │ 26,500  │ -5.4%  │ EMA_CROSS   │ 🟡 MED │   │
│  │ NVL    │ 12,000 │ 11,800  │ -1.7%  │ NO_DEMAND   │ 🟢 LOW │   │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Implementation Checklist

- [ ] Create `PROCESSORS/technical/stock/signal_generator.py`
- [ ] Implement `detect_ema_cross()`
- [ ] Implement `calculate_rvol()`
- [ ] Implement `detect_vsa_patterns()` (stopping vol, no demand, climax)
- [ ] Implement `detect_breakout()`
- [ ] Create `PROCESSORS/technical/stock/position_sizer.py`
- [ ] Implement `calculate_position_size()`
- [ ] Create `PROCESSORS/technical/stock/list_generator.py`
- [ ] Implement `generate_buy_list()`
- [ ] Implement `generate_sell_list()`
- [ ] Create output parquet schemas
- [ ] Add to daily pipeline
- [ ] Build Streamlit scanner page
- [ ] Build trading lists page
- [ ] Test with historical data
