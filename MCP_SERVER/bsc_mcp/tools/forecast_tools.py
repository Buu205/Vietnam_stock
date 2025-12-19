"""
Forecast Tools
==============

Tools for querying BSC analyst forecasts and ratings.

Tools:
------
1. bsc_get_bsc_forecast - Get forecast for a specific ticker
2. bsc_list_bsc_forecasts - List all stocks with forecasts
3. bsc_get_top_upside_stocks - Get stocks with highest upside potential
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
    """Register all forecast tools with the MCP server."""

    @mcp.tool()
    def bsc_get_bsc_forecast(ticker: str) -> str:
        """
        Get BSC analyst forecast for a specific ticker.

        Returns target price, rating, EPS forecasts, and growth estimates.

        Args:
            ticker: Stock symbol (e.g., "ACB", "VCB", "FPT")

        Returns:
            Markdown formatted forecast details

        Examples:
            - bsc_get_bsc_forecast("ACB") - ACB forecast
            - bsc_get_bsc_forecast("FPT") - FPT forecast
        """
        try:
            loader = get_data_loader()
            ticker = ticker.upper().strip()

            df = loader.get_bsc_individual()

            # Find ticker
            ticker_df = df[df['symbol'] == ticker]

            if ticker_df.empty:
                # List available tickers
                available = df['symbol'].unique().tolist()
                suggestions = [t for t in available if t.startswith(ticker[:1])][:5]

                if suggestions:
                    return f"No BSC forecast for {ticker}. Similar tickers with forecasts: {', '.join(suggestions)}"
                else:
                    return f"No BSC forecast available for {ticker}. Use `bsc_list_bsc_forecasts()` to see all covered stocks."

            forecast = ticker_df.iloc[0]

            # Get values
            target_price = forecast.get('target_price')
            current_price = forecast.get('current_price', forecast.get('close'))
            upside = forecast.get('upside_pct', forecast.get('upside'))
            rating = forecast.get('rating', forecast.get('recommendation'))

            entity_type = loader.get_ticker_entity_type(ticker)
            sector = forecast.get('sector', 'N/A')

            header = format_ticker_header(ticker, entity_type, sector)

            response = header + f"""### BSC Analyst Forecast

| Metric | Value |
|--------|-------|
| **Rating** | **{rating or 'N/A'}** |
| **Target Price** | {format_price(target_price)} |
| **Current Price** | {format_price(current_price)} |
| **Upside Potential** | {format_percent(upside/100 if upside and upside > 1 else upside)} |

### EPS Forecasts
| Year | EPS | YoY Growth |
|------|-----|------------|
| **2025F** | {format_number(forecast.get('eps_2025f', forecast.get('eps_2025')))} | {format_percent(forecast.get('eps_growth_2025'))} |
| **2026F** | {format_number(forecast.get('eps_2026f', forecast.get('eps_2026')))} | {format_percent(forecast.get('eps_growth_2026'))} |

### Forward Valuations
| Metric | 2025F | 2026F |
|--------|-------|-------|
| **PE Forward** | {format_number(forecast.get('pe_fwd_2025', forecast.get('pe_2025f')))} | {format_number(forecast.get('pe_fwd_2026', forecast.get('pe_2026f')))} |
| **PB Forward** | {format_number(forecast.get('pb_fwd_2025', forecast.get('pb_2025f')))} | {format_number(forecast.get('pb_fwd_2026', forecast.get('pb_2026f')))} |

### Revenue Growth
| Metric | Value |
|--------|-------|
| **2025F Rev Growth** | {format_percent(forecast.get('rev_growth_yoy_2025', forecast.get('revenue_growth_2025')))} |
| **NPATMI Achievement** | {format_percent(forecast.get('npatmi_achievement_pct'))} |
"""
            return response

        except Exception as e:
            return handle_tool_error(e, "bsc_get_bsc_forecast")

    @mcp.tool()
    def bsc_list_bsc_forecasts(
        rating: Optional[str] = None,
        sector: Optional[str] = None,
        sort_by: str = "upside",
        limit: int = 30
    ) -> str:
        """
        List all stocks with BSC analyst forecasts.

        Args:
            rating: Filter by rating - "BUY", "HOLD", "SELL", or None for all
            sector: Filter by sector name
            sort_by: Sort results - "upside" (default), "pe", "ticker"
            limit: Maximum results (default: 30)

        Returns:
            Markdown table of stocks with forecasts

        Examples:
            - bsc_list_bsc_forecasts() - All forecasts sorted by upside
            - bsc_list_bsc_forecasts(rating="BUY") - Only BUY ratings
            - bsc_list_bsc_forecasts(sector="Ngân hàng") - Banking sector
        """
        try:
            loader = get_data_loader()

            df = loader.get_bsc_individual()

            if df.empty:
                return "No BSC forecast data available."

            # Apply filters
            if rating:
                rating_col = 'rating' if 'rating' in df.columns else 'recommendation'
                df = df[df[rating_col].str.upper() == rating.upper()]

            if sector:
                if 'sector' in df.columns:
                    df = df[df['sector'].str.contains(sector, case=False, na=False)]

            if df.empty:
                return f"No forecasts found matching filters: rating={rating}, sector={sector}"

            # Sort
            upside_col = 'upside_pct' if 'upside_pct' in df.columns else 'upside'
            pe_col = 'pe_fwd_2025' if 'pe_fwd_2025' in df.columns else 'pe_2025f'

            if sort_by == "upside" and upside_col in df.columns:
                df = df.sort_values(upside_col, ascending=False)
            elif sort_by == "pe" and pe_col in df.columns:
                df = df.sort_values(pe_col, ascending=True)
            else:
                df = df.sort_values('symbol')

            df = df.head(limit)

            # Build result
            rating_col = 'rating' if 'rating' in df.columns else 'recommendation'
            result_cols = ['symbol', rating_col, 'target_price', upside_col]
            if pe_col in df.columns:
                result_cols.append(pe_col)

            available_cols = [c for c in result_cols if c in df.columns]
            result_df = df[available_cols].copy()

            # Rename columns
            result_df.columns = ['Ticker', 'Rating', 'Target', 'Upside%'] + (['PE 2025F'] if pe_col in available_cols else [])

            # Format upside
            if 'Upside%' in result_df.columns:
                result_df['Upside%'] = result_df['Upside%'].apply(lambda x: format_percent(x/100 if x > 1 else x))

            return format_dataframe_markdown(
                result_df,
                title=f"BSC Forecasts ({len(result_df)} stocks)"
            )

        except Exception as e:
            return handle_tool_error(e, "bsc_list_bsc_forecasts")

    @mcp.tool()
    def bsc_get_top_upside_stocks(
        n: int = 10,
        sector: Optional[str] = None,
        min_upside: float = 0
    ) -> str:
        """
        Get top stocks with highest upside potential according to BSC.

        Args:
            n: Number of stocks to return (default: 10)
            sector: Optional sector filter
            min_upside: Minimum upside % to include (default: 0)

        Returns:
            Markdown table of top upside stocks

        Examples:
            - bsc_get_top_upside_stocks() - Top 10 upside stocks
            - bsc_get_top_upside_stocks(n=5, sector="Ngân hàng") - Top 5 banks
            - bsc_get_top_upside_stocks(min_upside=20) - Stocks with >20% upside
        """
        try:
            loader = get_data_loader()

            df = loader.get_bsc_individual()

            if df.empty:
                return "No BSC forecast data available."

            # Get upside column
            upside_col = 'upside_pct' if 'upside_pct' in df.columns else 'upside'

            # Apply sector filter
            if sector and 'sector' in df.columns:
                df = df[df['sector'].str.contains(sector, case=False, na=False)]

            # Apply minimum upside filter
            if upside_col in df.columns:
                df = df[df[upside_col] >= min_upside]

            if df.empty:
                return f"No stocks found with upside >= {min_upside}% in sector '{sector or 'All'}'"

            # Sort by upside and get top n
            df = df.sort_values(upside_col, ascending=False).head(n)

            # Build result
            rating_col = 'rating' if 'rating' in df.columns else 'recommendation'
            result = []

            for _, row in df.iterrows():
                result.append({
                    'Rank': len(result) + 1,
                    'Ticker': row['symbol'],
                    'Rating': row.get(rating_col, 'N/A'),
                    'Target': format_price(row.get('target_price')),
                    'Current': format_price(row.get('current_price', row.get('close'))),
                    'Upside': format_percent(row.get(upside_col, 0) / 100 if row.get(upside_col, 0) > 1 else row.get(upside_col, 0)),
                    'Sector': row.get('sector', 'N/A')
                })

            result_df = pd.DataFrame(result)

            title = f"Top {n} Upside Stocks (BSC Forecast)"
            if sector:
                title += f" - {sector}"

            return format_dataframe_markdown(result_df, title=title)

        except Exception as e:
            return handle_tool_error(e, "bsc_get_top_upside_stocks")
