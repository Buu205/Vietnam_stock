"""
TA Strategy Backtest Runner
===========================
Test các chiến lược kỹ thuật trên:
1. VNIndex (market level)
2. Top performers 2024-2025
3. VSA signals on individual stocks

Output: CSV results + summary report
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Paths
DATA_DIR = Path("DATA")
OUTPUT_DIR = Path("plans/251223-ta-backtest-experiments")

def load_ohlcv():
    """Load raw OHLCV data"""
    df = pd.read_parquet(DATA_DIR / "raw/ohlcv/OHLCV_mktcap.parquet")
    df['date'] = pd.to_datetime(df['date'])
    return df

def calc_technical_indicators(df):
    """Calculate technical indicators for a single stock"""
    df = df.sort_values('date').copy()

    # EMAs
    df['ema9'] = df['close'].ewm(span=9).mean()
    df['ema21'] = df['close'].ewm(span=21).mean()
    df['ma20'] = df['close'].rolling(20).mean()

    # Volume
    df['vol_sma20'] = df['volume'].rolling(20).mean()
    df['rvol'] = df['volume'] / df['vol_sma20']

    # ATR
    df['atr'] = (df['high'] - df['low']).rolling(14).mean()

    # Spread analysis for VSA
    df['spread'] = df['high'] - df['low']
    df['avg_spread'] = df['spread'].rolling(20).mean()
    df['close_position'] = np.where(
        df['spread'] > 0,
        (df['close'] - df['low']) / df['spread'],
        0.5
    )

    # Swing points
    df['swing_high_10'] = df['high'].rolling(10).max()
    df['swing_low_10'] = df['low'].rolling(10).min()

    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # Daily return
    df['daily_return'] = df['close'].pct_change()

    return df

def identify_vsa_signals(df):
    """Identify VSA patterns"""
    df = df.copy()

    # Stopping Volume: Downtrend + High Vol + Narrow Spread + Close near High
    in_downtrend = df['close'] < df['ma20']
    high_vol = df['rvol'] > 1.5
    narrow_spread = df['spread'] < df['avg_spread']
    close_near_high = df['close_position'] > 0.6
    df['stopping_vol'] = in_downtrend & high_vol & narrow_spread & close_near_high

    # No Demand: Up candle + Low Vol + Narrow Spread
    up_candle = df['close'] > df['open']
    low_vol = df['rvol'] < 0.8
    df['no_demand'] = up_candle & low_vol & narrow_spread

    # Breakout: Close > swing high + volume
    df['breakout'] = (df['close'] > df['swing_high_10'].shift(1)) & (df['rvol'] > 1.3)

    # EMA Cross
    df['ema_cross_up'] = (df['ema9'] > df['ema21']) & (df['ema9'].shift(1) <= df['ema21'].shift(1))
    df['ema_cross_down'] = (df['ema9'] < df['ema21']) & (df['ema9'].shift(1) >= df['ema21'].shift(1))

    return df

def get_top_performers_2024_2025(ohlcv, n=30):
    """Get top performing stocks in 2024-2025"""
    # Filter 2024-2025
    df = ohlcv[ohlcv['date'] >= '2024-01-01'].copy()

    # Calculate return per stock
    returns = df.groupby('symbol').apply(
        lambda x: (x.iloc[-1]['close'] / x.iloc[0]['close'] - 1) * 100
        if len(x) > 50 else np.nan,
        include_groups=False
    ).dropna()

    top_stocks = returns.nlargest(n).index.tolist()
    return top_stocks, returns

def backtest_ema_strategy(df, symbol='INDEX'):
    """Backtest EMA 9/21 cross strategy"""
    df = df.dropna().copy()

    position = 0
    entry_price = 0
    trades = []

    for i in range(len(df)):
        row = df.iloc[i]

        # Entry: EMA cross up + Volume > avg
        if position == 0 and row['ema_cross_up'] and row['rvol'] >= 1.0:
            position = 1
            entry_price = row['close']
            entry_date = row['date']

        # Exit: EMA cross down
        elif position == 1 and row['ema_cross_down']:
            position = 0
            pnl = (row['close'] - entry_price) / entry_price * 100
            trades.append({
                'symbol': symbol,
                'entry_date': entry_date,
                'exit_date': row['date'],
                'entry_price': entry_price,
                'exit_price': row['close'],
                'pnl_pct': pnl,
                'days_held': (row['date'] - entry_date).days
            })

    return pd.DataFrame(trades)

def backtest_vsa_stopping(df, symbol='STOCK', holding_days=5):
    """Backtest VSA Stopping Volume signal"""
    df = df.dropna().reset_index(drop=True)

    signals = df[df['stopping_vol']].copy()
    results = []

    for _, signal in signals.iterrows():
        signal_idx = df[df['date'] == signal['date']].index[0]
        entry_price = signal['close']

        # Get future prices
        future_idx = signal_idx + holding_days
        if future_idx >= len(df):
            continue

        exit_price = df.iloc[future_idx]['close']
        pnl = (exit_price - entry_price) / entry_price * 100

        results.append({
            'symbol': symbol,
            'signal_date': signal['date'],
            'entry_price': entry_price,
            'exit_price': exit_price,
            'pnl_pct': pnl,
            'holding_days': holding_days
        })

    return pd.DataFrame(results)

def calc_metrics(trades_df):
    """Calculate backtest metrics"""
    if len(trades_df) == 0:
        return {}

    winners = trades_df[trades_df['pnl_pct'] > 0]
    losers = trades_df[trades_df['pnl_pct'] <= 0]

    metrics = {
        'total_trades': len(trades_df),
        'win_rate': len(winners) / len(trades_df) * 100,
        'avg_pnl': trades_df['pnl_pct'].mean(),
        'total_return': trades_df['pnl_pct'].sum(),
        'max_win': trades_df['pnl_pct'].max(),
        'max_loss': trades_df['pnl_pct'].min(),
        'profit_factor': winners['pnl_pct'].sum() / abs(losers['pnl_pct'].sum()) if len(losers) > 0 and losers['pnl_pct'].sum() != 0 else np.inf
    }
    return metrics

def main():
    print("="*60)
    print("TA STRATEGY BACKTEST")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)

    # Load data
    print("\nLoading data...")
    ohlcv = load_ohlcv()
    print(f"Total records: {len(ohlcv):,}")
    print(f"Date range: {ohlcv['date'].min()} to {ohlcv['date'].max()}")

    # Get top performers
    print("\nIdentifying top performers 2024-2025...")
    top_stocks, returns = get_top_performers_2024_2025(ohlcv, n=30)
    print(f"Top 10 performers:")
    for symbol in top_stocks[:10]:
        print(f"  {symbol}: +{returns[symbol]:.1f}%")

    # ===== TEST 1: EMA Strategy on Top Stocks =====
    print("\n" + "="*60)
    print("TEST 1: EMA 9/21 Strategy on Top 30 Performers")
    print("="*60)

    all_ema_trades = []
    for symbol in top_stocks:
        stock_data = ohlcv[ohlcv['symbol'] == symbol].copy()
        stock_data = stock_data[stock_data['date'] >= '2023-01-01']  # Backtest from 2023
        if len(stock_data) < 100:
            continue

        stock_data = calc_technical_indicators(stock_data)
        stock_data = identify_vsa_signals(stock_data)

        trades = backtest_ema_strategy(stock_data, symbol)
        if len(trades) > 0:
            all_ema_trades.append(trades)

    if all_ema_trades:
        ema_results = pd.concat(all_ema_trades, ignore_index=True)
        ema_results.to_csv(OUTPUT_DIR / "ema_strategy_results.csv", index=False)

        metrics = calc_metrics(ema_results)
        print(f"\nEMA Strategy Results:")
        print(f"  Total trades: {metrics['total_trades']}")
        print(f"  Win rate: {metrics['win_rate']:.1f}%")
        print(f"  Avg PnL: {metrics['avg_pnl']:.2f}%")
        print(f"  Profit Factor: {metrics['profit_factor']:.2f}")

    # ===== TEST 2: VSA Stopping Volume =====
    print("\n" + "="*60)
    print("TEST 2: VSA Stopping Volume on Top 30 Performers")
    print("="*60)

    all_vsa_trades = []
    for symbol in top_stocks:
        stock_data = ohlcv[ohlcv['symbol'] == symbol].copy()
        stock_data = stock_data[stock_data['date'] >= '2023-01-01']
        if len(stock_data) < 100:
            continue

        stock_data = calc_technical_indicators(stock_data)
        stock_data = identify_vsa_signals(stock_data)

        trades = backtest_vsa_stopping(stock_data, symbol, holding_days=5)
        if len(trades) > 0:
            all_vsa_trades.append(trades)

    if all_vsa_trades:
        vsa_results = pd.concat(all_vsa_trades, ignore_index=True)
        vsa_results.to_csv(OUTPUT_DIR / "vsa_stopping_results.csv", index=False)

        metrics = calc_metrics(vsa_results)
        print(f"\nVSA Stopping Volume Results (5-day hold):")
        print(f"  Total signals: {metrics['total_trades']}")
        print(f"  Win rate: {metrics['win_rate']:.1f}%")
        print(f"  Avg PnL: {metrics['avg_pnl']:.2f}%")

    # ===== SAVE SUMMARY =====
    print("\n" + "="*60)
    print("SUMMARY SAVED")
    print("="*60)
    print(f"Results saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
