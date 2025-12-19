"""
Technical Tools
===============

Tools for querying technical indicators and trading alerts.

Tools:
------
1. bsc_get_technical_indicators - Get OHLCV + indicators
2. bsc_get_latest_technicals - Snapshot of latest indicators
3. bsc_get_technical_alerts - Trading alerts (breakout, MA crossover, etc.)
4. bsc_get_market_breadth - Market breadth indicators
5. bsc_get_candlestick_patterns - Candlestick pattern detection
6. bsc_get_ohlcv_raw - Raw OHLCV data for external analysis
"""

from typing import Optional
from mcp.server.fastmcp import FastMCP
import pandas as pd

from bsc_mcp.services.data_loader import get_data_loader
from bsc_mcp.utils.errors import handle_tool_error, TickerNotFoundError
from bsc_mcp.utils.formatters import (
    format_dataframe_markdown,
    format_number,
    format_percent,
    format_price,
    format_ticker_header
)


def register(mcp: FastMCP):
    """Register all technical tools with the MCP server."""

    @mcp.tool()
    def bsc_get_technical_indicators(
        ticker: str,
        limit: int = 30,
        indicators: Optional[str] = None
    ) -> str:
        """
        Get OHLCV data with technical indicators for a ticker.

        Args:
            ticker: Stock symbol (e.g., "VNM", "VCB", "FPT")
            limit: Number of days to return (default: 30)
            indicators: Comma-separated indicators to include. Options:
                       - sma (SMA 20/50/200)
                       - ema (EMA 20/50)
                       - rsi (RSI 14)
                       - macd (MACD, signal, histogram)
                       - bb (Bollinger Bands)
                       - volume (OBV, CMF, MFI)
                       Default: all indicators

        Returns:
            Markdown table with OHLCV and selected indicators

        Examples:
            - bsc_get_technical_indicators("FPT") - All indicators
            - bsc_get_technical_indicators("VNM", limit=10, indicators="rsi,macd")
        """
        try:
            loader = get_data_loader()
            ticker = ticker.upper().strip()

            # Load technical data
            df = loader.get_technical_basic()

            # Filter by ticker
            ticker_df = df[df['symbol'] == ticker].copy()

            if ticker_df.empty:
                all_tickers = loader.get_available_tickers()
                suggestions = [t for t in all_tickers if t.startswith(ticker[:2])][:5]
                raise TickerNotFoundError(ticker, suggestions)

            # Sort by date and limit
            ticker_df = ticker_df.sort_values('date', ascending=False).head(limit)

            # Select columns based on requested indicators
            base_cols = ['date', 'open', 'high', 'low', 'close', 'volume']

            indicator_cols = {
                'sma': ['sma_20', 'sma_50', 'sma_200'],
                'ema': ['ema_20', 'ema_50'],
                'rsi': ['rsi_14'],
                'macd': ['macd', 'macd_signal', 'macd_hist'],
                'bb': ['bb_upper', 'bb_middle', 'bb_lower', 'bb_width'],
                'volume': ['obv', 'cmf_20', 'mfi_14'],
                'adx': ['adx_14'],
                'atr': ['atr_14'],
            }

            # Determine which indicators to include
            if indicators:
                selected = [i.strip().lower() for i in indicators.split(',')]
                cols_to_include = base_cols.copy()
                for ind in selected:
                    if ind in indicator_cols:
                        cols_to_include.extend(indicator_cols[ind])
            else:
                # Include key indicators by default
                cols_to_include = base_cols + ['rsi_14', 'macd', 'sma_20', 'sma_50']

            # Filter available columns
            available_cols = [c for c in cols_to_include if c in ticker_df.columns]
            result_df = ticker_df[available_cols].copy()

            # Format date
            if 'date' in result_df.columns:
                result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')

            entity_type = loader.get_ticker_entity_type(ticker)
            header = format_ticker_header(ticker, entity_type)

            return header + format_dataframe_markdown(
                result_df,
                title=f"Technical Indicators (Last {len(result_df)} days)"
            )

        except TickerNotFoundError as e:
            return str(e)
        except Exception as e:
            return handle_tool_error(e, "bsc_get_technical_indicators")

    @mcp.tool()
    def bsc_get_latest_technicals(ticker: str) -> str:
        """
        Get a snapshot of the latest technical indicators for a ticker.

        Returns current values with signal interpretation.

        Args:
            ticker: Stock symbol (e.g., "FPT", "VNM", "VCB")

        Returns:
            Markdown formatted technical snapshot with signals

        Examples:
            - bsc_get_latest_technicals("FPT") - Latest FPT technicals
        """
        try:
            loader = get_data_loader()
            ticker = ticker.upper().strip()

            # Load technical data
            df = loader.get_technical_basic()

            # Get latest for ticker
            ticker_df = df[df['symbol'] == ticker].sort_values('date', ascending=False)

            if ticker_df.empty:
                all_tickers = loader.get_available_tickers()
                suggestions = [t for t in all_tickers if t.startswith(ticker[:2])][:5]
                raise TickerNotFoundError(ticker, suggestions)

            latest = ticker_df.iloc[0]
            date_str = pd.to_datetime(latest['date']).strftime('%Y-%m-%d')

            # Calculate signals
            close = latest.get('close', 0)
            rsi = latest.get('rsi_14')
            macd = latest.get('macd')
            macd_signal = latest.get('macd_signal')
            sma_20 = latest.get('sma_20')
            sma_50 = latest.get('sma_50')
            sma_200 = latest.get('sma_200')

            # RSI signal
            rsi_signal = "N/A"
            if pd.notna(rsi):
                if rsi > 70:
                    rsi_signal = "Overbought"
                elif rsi < 30:
                    rsi_signal = "Oversold"
                else:
                    rsi_signal = "Neutral"

            # MACD signal
            macd_trend = "N/A"
            if pd.notna(macd) and pd.notna(macd_signal):
                if macd > macd_signal:
                    macd_trend = "Bullish"
                else:
                    macd_trend = "Bearish"

            # Price vs SMA
            trend = "N/A"
            if pd.notna(sma_50) and pd.notna(sma_200):
                if close > sma_50 > sma_200:
                    trend = "Uptrend"
                elif close < sma_50 < sma_200:
                    trend = "Downtrend"
                else:
                    trend = "Sideways"

            entity_type = loader.get_ticker_entity_type(ticker)
            header = format_ticker_header(ticker, entity_type)

            response = header + f"""### Technical Snapshot ({date_str})

#### Price & Volume
| Metric | Value |
|--------|-------|
| **Close** | {format_price(close)} |
| **Volume** | {format_number(latest.get('volume'), 0)} |
| **Change** | {format_percent(latest.get('change_pct', 0))} |

#### Trend Indicators
| Indicator | Value | Signal |
|-----------|-------|--------|
| **SMA 20** | {format_number(sma_20)} | {'Above' if close > sma_20 else 'Below'} |
| **SMA 50** | {format_number(sma_50)} | {'Above' if close > sma_50 else 'Below'} |
| **SMA 200** | {format_number(sma_200)} | {'Above' if close > sma_200 else 'Below'} |
| **Trend** | - | **{trend}** |

#### Momentum Indicators
| Indicator | Value | Signal |
|-----------|-------|--------|
| **RSI (14)** | {format_number(rsi)} | **{rsi_signal}** |
| **MACD** | {format_number(macd)} | **{macd_trend}** |
| **MACD Signal** | {format_number(macd_signal)} | - |

#### Volatility
| Indicator | Value |
|-----------|-------|
| **BB Upper** | {format_number(latest.get('bb_upper'))} |
| **BB Lower** | {format_number(latest.get('bb_lower'))} |
| **ATR (14)** | {format_number(latest.get('atr_14'))} |
"""
            return response

        except TickerNotFoundError as e:
            return str(e)
        except Exception as e:
            return handle_tool_error(e, "bsc_get_latest_technicals")

    @mcp.tool()
    def bsc_get_technical_alerts(
        ticker: Optional[str] = None,
        alert_type: str = "all",
        limit: int = 20
    ) -> str:
        """
        Get technical trading alerts (breakouts, MA crossovers, volume spikes).

        Args:
            ticker: Optional ticker filter. If None, returns alerts for all stocks
            alert_type: Type of alert to filter:
                       - "breakout" - Price breakout above resistance
                       - "ma_crossover" - Golden cross / Death cross
                       - "volume_spike" - Unusual volume
                       - "patterns" - Candlestick patterns
                       - "all" - All alert types (default)
            limit: Maximum alerts to return (default: 20)

        Returns:
            Markdown table of trading alerts

        Examples:
            - bsc_get_technical_alerts() - All latest alerts
            - bsc_get_technical_alerts(alert_type="breakout") - Only breakouts
            - bsc_get_technical_alerts(ticker="FPT") - Alerts for FPT only
        """
        try:
            loader = get_data_loader()

            all_alerts = []

            # Load relevant alert files
            alert_loaders = {
                'breakout': ('breakout_alerts', loader.get_breakout_alerts),
                'ma_crossover': ('ma_crossover_alerts', loader.get_ma_crossover_alerts),
                'volume_spike': ('volume_spike_alerts', loader.get_volume_spike_alerts),
            }

            for atype, (name, loader_func) in alert_loaders.items():
                if alert_type != 'all' and alert_type != atype:
                    continue

                try:
                    df = loader_func()

                    # Filter by ticker if provided
                    if ticker:
                        df = df[df['symbol'] == ticker.upper()]

                    # Add alert type column
                    df = df.copy()
                    df['alert_type'] = atype

                    all_alerts.append(df)
                except FileNotFoundError:
                    continue
                except Exception:
                    continue

            if not all_alerts:
                return f"No alerts found for filter: ticker={ticker}, alert_type={alert_type}"

            # Combine all alerts
            combined = pd.concat(all_alerts, ignore_index=True)

            # Sort by date if available
            if 'date' in combined.columns:
                combined = combined.sort_values('date', ascending=False)

            # Select key columns
            display_cols = ['symbol', 'alert_type', 'date']
            if 'signal' in combined.columns:
                display_cols.append('signal')
            if 'close' in combined.columns:
                display_cols.append('close')

            available_cols = [c for c in display_cols if c in combined.columns]
            result_df = combined[available_cols].head(limit)

            # Format date
            if 'date' in result_df.columns:
                result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')

            title = f"Technical Alerts ({len(result_df)} found)"
            if ticker:
                title = f"Technical Alerts for {ticker.upper()} ({len(result_df)} found)"

            return format_dataframe_markdown(result_df, title=title)

        except Exception as e:
            return handle_tool_error(e, "bsc_get_technical_alerts")

    @mcp.tool()
    def bsc_get_market_breadth(date: Optional[str] = None) -> str:
        """
        Get market breadth indicators (Advance/Decline, McClellan, etc.).

        Args:
            date: Optional date (YYYY-MM-DD). If None, returns latest data

        Returns:
            Markdown formatted market breadth overview

        Examples:
            - bsc_get_market_breadth() - Latest breadth data
            - bsc_get_market_breadth("2024-12-18") - Specific date
        """
        try:
            loader = get_data_loader()

            # Load market breadth data
            df = loader.get_market_breadth()

            if df.empty:
                return "No market breadth data available."

            # Filter by date if provided
            if date:
                df = df[df['date'] == date]
                if df.empty:
                    return f"No market breadth data for {date}."
            else:
                # Get latest
                df = df.sort_values('date', ascending=False)

            latest = df.iloc[0]
            date_str = pd.to_datetime(latest['date']).strftime('%Y-%m-%d')

            # Build response
            response = f"""## Market Breadth Overview ({date_str})

### Advance / Decline
| Metric | Value |
|--------|-------|
| **Advancing** | {format_number(latest.get('advancing', 'N/A'), 0)} |
| **Declining** | {format_number(latest.get('declining', 'N/A'), 0)} |
| **Unchanged** | {format_number(latest.get('unchanged', 'N/A'), 0)} |
| **A/D Ratio** | {format_number(latest.get('ad_ratio', 'N/A'))} |

### Breadth Indicators
| Indicator | Value | Signal |
|-----------|-------|--------|
| **McClellan Oscillator** | {format_number(latest.get('mcclellan_oscillator', 'N/A'))} | {'Bullish' if latest.get('mcclellan_oscillator', 0) > 0 else 'Bearish'} |
| **McClellan Sum Index** | {format_number(latest.get('mcclellan_sum_index', 'N/A'))} | - |
| **% Above SMA 20** | {format_percent(latest.get('pct_above_sma20', 'N/A'))} | - |
| **% Above SMA 50** | {format_percent(latest.get('pct_above_sma50', 'N/A'))} | - |
| **% Above SMA 200** | {format_percent(latest.get('pct_above_sma200', 'N/A'))} | - |

### New Highs / New Lows
| Metric | Value |
|--------|-------|
| **New 52W Highs** | {format_number(latest.get('new_highs', 'N/A'), 0)} |
| **New 52W Lows** | {format_number(latest.get('new_lows', 'N/A'), 0)} |
| **High-Low Index** | {format_number(latest.get('high_low_index', 'N/A'))} |
"""
            return response

        except Exception as e:
            return handle_tool_error(e, "bsc_get_market_breadth")

    @mcp.tool()
    def bsc_get_candlestick_patterns(
        ticker: Optional[str] = None,
        pattern: Optional[str] = None,
        signal: Optional[str] = None,
        limit: int = 30
    ) -> str:
        """
        Get candlestick pattern alerts detected by ta-lib.

        Available patterns: doji, hammer, hanging_man, engulfing,
        three_white_soldiers, evening_star, inverted_hammer, shooting_star

        Args:
            ticker: Optional ticker to filter (e.g., "FPT"). If None, returns all.
            pattern: Optional pattern name to filter. Options:
                    - "doji" - Doji pattern (indecision)
                    - "hammer" - Hammer (bullish reversal)
                    - "hanging_man" - Hanging man (bearish reversal)
                    - "engulfing" - Engulfing pattern
                    - "three_white_soldiers" - Three white soldiers (strong bullish)
                    - "evening_star" - Evening star (bearish reversal)
                    - "inverted_hammer" - Inverted hammer
                    - "shooting_star" - Shooting star (bearish)
            signal: Filter by signal type: "BULLISH" or "BEARISH"
            limit: Maximum patterns to return (default: 30)

        Returns:
            Markdown table of detected candlestick patterns

        Examples:
            - bsc_get_candlestick_patterns() - All patterns today
            - bsc_get_candlestick_patterns(ticker="FPT") - FPT patterns only
            - bsc_get_candlestick_patterns(pattern="hammer") - All hammer patterns
            - bsc_get_candlestick_patterns(signal="BULLISH") - All bullish patterns
        """
        try:
            loader = get_data_loader()

            # Load pattern alerts
            df = loader.get_pattern_alerts()

            if df.empty:
                return "No candlestick pattern data available."

            # Filter by ticker
            if ticker:
                df = df[df['symbol'] == ticker.upper()]
                if df.empty:
                    return f"No patterns found for ticker: {ticker.upper()}"

            # Filter by pattern name
            if pattern:
                pattern = pattern.lower().strip()
                df = df[df['pattern_name'].str.lower() == pattern]
                if df.empty:
                    return f"No '{pattern}' patterns found."

            # Filter by signal
            if signal:
                signal = signal.upper().strip()
                df = df[df['signal'] == signal]
                if df.empty:
                    return f"No {signal} patterns found."

            # Sort by date descending and limit
            if 'date' in df.columns:
                df = df.sort_values('date', ascending=False)

            result_df = df.head(limit).copy()

            # Format output
            display_cols = ['symbol', 'pattern_name', 'signal', 'strength', 'price', 'date']
            available_cols = [c for c in display_cols if c in result_df.columns]
            result_df = result_df[available_cols]

            # Format date
            if 'date' in result_df.columns:
                result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')

            # Format price
            if 'price' in result_df.columns:
                result_df['price'] = result_df['price'].apply(lambda x: format_price(x) if pd.notna(x) else 'N/A')

            # Build title
            title = f"Candlestick Patterns ({len(result_df)} found)"
            if ticker:
                title = f"Candlestick Patterns for {ticker.upper()} ({len(result_df)} found)"

            # Add summary
            bullish_count = len(df[df['signal'] == 'BULLISH']) if 'signal' in df.columns else 0
            bearish_count = len(df[df['signal'] == 'BEARISH']) if 'signal' in df.columns else 0

            summary = f"""### Pattern Summary
- **Bullish patterns**: {bullish_count}
- **Bearish patterns**: {bearish_count}
- **Total detected**: {len(df)}

"""
            return summary + format_dataframe_markdown(result_df, title=title)

        except Exception as e:
            return handle_tool_error(e, "bsc_get_candlestick_patterns")

    @mcp.tool()
    def bsc_get_ohlcv_raw(
        ticker: str,
        limit: int = 60,
        include_value: bool = True
    ) -> str:
        """
        Get raw OHLCV (Open, High, Low, Close, Volume) data with trading value.

        This tool returns price data with trading value for:
        - External technical analysis with ta-lib
        - Money flow analysis
        - Custom indicator calculations
        - Charting and visualization

        Args:
            ticker: Stock symbol (e.g., "FPT", "VNM", "VCB")
            limit: Number of trading days to return (default: 60)
            include_value: Include trading value columns (default: True)

        Returns:
            Markdown table with OHLCV and trading value data

        Examples:
            - bsc_get_ohlcv_raw("FPT") - Last 60 days with trading value
            - bsc_get_ohlcv_raw("VNM", limit=100) - Last 100 days
            - bsc_get_ohlcv_raw("ACB", include_value=False) - OHLCV only
        """
        try:
            loader = get_data_loader()
            ticker = ticker.upper().strip()

            # Load technical data (contains OHLCV)
            df = loader.get_technical_basic()

            # Filter by ticker
            ticker_df = df[df['symbol'] == ticker].copy()

            if ticker_df.empty:
                all_tickers = loader.get_available_tickers()
                suggestions = [t for t in all_tickers if t.startswith(ticker[:2])][:5]
                raise TickerNotFoundError(ticker, suggestions)

            # Sort by date descending and limit
            ticker_df = ticker_df.sort_values('date', ascending=False).head(limit)

            # Select columns based on include_value
            if include_value:
                ohlcv_cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'trading_value']
            else:
                ohlcv_cols = ['date', 'open', 'high', 'low', 'close', 'volume']

            available_cols = [c for c in ohlcv_cols if c in ticker_df.columns]
            result_df = ticker_df[available_cols].copy()

            # Format date
            if 'date' in result_df.columns:
                result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')

            entity_type = loader.get_ticker_entity_type(ticker)
            header = format_ticker_header(ticker, entity_type)

            # Calculate basic stats
            if len(ticker_df) > 0:
                latest_close = ticker_df.iloc[0]['close'] if 'close' in ticker_df.columns else 0
                avg_volume = ticker_df['volume'].mean() if 'volume' in ticker_df.columns else 0
                high_period = ticker_df['high'].max() if 'high' in ticker_df.columns else 0
                low_period = ticker_df['low'].min() if 'low' in ticker_df.columns else 0

                # Trading value stats (in billions VND)
                avg_trading_value = ticker_df['trading_value'].mean() / 1e9 if 'trading_value' in ticker_df.columns else 0
                latest_trading_value = ticker_df.iloc[0]['trading_value'] / 1e9 if 'trading_value' in ticker_df.columns else 0
                max_trading_value = ticker_df['trading_value'].max() / 1e9 if 'trading_value' in ticker_df.columns else 0

                stats = f"""### OHLCV Summary
| Metric | Value |
|--------|-------|
| **Latest Close** | {format_price(latest_close)} |
| **Avg Volume ({limit}d)** | {format_number(avg_volume, 0)} |
| **High ({limit}d)** | {format_price(high_period)} |
| **Low ({limit}d)** | {format_price(low_period)} |

"""
                if include_value:
                    stats += f"""### Trading Value Analysis (tỷ VND)
| Metric | Value |
|--------|-------|
| **Latest Trading Value** | {format_number(latest_trading_value, 2)} tỷ |
| **Avg Trading Value ({limit}d)** | {format_number(avg_trading_value, 2)} tỷ |
| **Max Trading Value ({limit}d)** | {format_number(max_trading_value, 2)} tỷ |
| **Value vs Avg** | {format_percent((latest_trading_value / avg_trading_value - 1) if avg_trading_value > 0 else 0)} |

"""
            else:
                stats = ""

            # Format trading value columns for display (convert to billions VND)
            if 'trading_value' in result_df.columns:
                result_df['trading_value'] = (result_df['trading_value'] / 1e9).round(2)
                result_df = result_df.rename(columns={'trading_value': 'value_bn'})

            return header + stats + format_dataframe_markdown(
                result_df,
                title=f"OHLCV + Trading Value (Last {len(result_df)} days)"
            )

        except TickerNotFoundError as e:
            return str(e)
        except Exception as e:
            return handle_tool_error(e, "bsc_get_ohlcv_raw")
