"""
Macro Tools
===========

Tools for querying macro economic and commodity data.

Tools:
------
1. bsc_get_macro_data - Interest rates, FX, bond yields
2. bsc_get_commodity_prices - Gold, oil, steel prices
3. bsc_get_macro_overview - Summary of current macro indicators
"""

from typing import Optional
from mcp.server.fastmcp import FastMCP
import pandas as pd

from bsc_mcp.services.data_loader import get_data_loader
from bsc_mcp.utils.errors import handle_tool_error
from bsc_mcp.utils.formatters import format_dataframe_markdown, format_number, format_percent


def register(mcp: FastMCP):
    """Register all macro tools with the MCP server."""

    @mcp.tool()
    def bsc_get_macro_data(
        indicator: Optional[str] = None,
        limit: int = 30
    ) -> str:
        """
        Get macro economic data (interest rates, FX, bond yields).

        Args:
            indicator: Specific indicator to query. Options:
                      - "deposit_rate" - Bank deposit rates
                      - "lending_rate" - Lending rates
                      - "usd_vnd" - USD/VND exchange rate
                      - "gov_bond_10y" - 10Y government bond yield
                      - None - All indicators (default)
            limit: Number of data points (default: 30)

        Returns:
            Markdown table of macro data

        Examples:
            - bsc_get_macro_data() - All macro data
            - bsc_get_macro_data(indicator="usd_vnd") - Just FX rate
        """
        try:
            loader = get_data_loader()

            df = loader.get_macro_commodity()

            if df.empty:
                return "No macro data available."

            # Filter by indicator type if specified
            if indicator:
                indicator_lower = indicator.lower()
                # Look for matching columns or filter by type column if exists
                if 'indicator' in df.columns:
                    df = df[df['indicator'].str.lower().str.contains(indicator_lower)]
                elif 'type' in df.columns:
                    df = df[df['type'].str.lower().str.contains(indicator_lower)]

            if df.empty:
                return f"No data found for indicator '{indicator}'."

            # Sort by date and limit
            if 'date' in df.columns:
                df = df.sort_values('date', ascending=False).head(limit)

            # Format date
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

            return format_dataframe_markdown(
                df,
                title=f"Macro Economic Data (Last {len(df)} records)"
            )

        except Exception as e:
            return handle_tool_error(e, "bsc_get_macro_data")

    @mcp.tool()
    def bsc_get_commodity_prices(
        commodity: Optional[str] = None,
        limit: int = 30
    ) -> str:
        """
        Get commodity prices (gold, oil, steel, rubber).

        Args:
            commodity: Specific commodity. Options:
                      - "gold" - Gold prices
                      - "oil" or "oil_brent" - Brent oil
                      - "steel" - Steel prices
                      - "rubber" - Rubber prices
                      - None - All commodities (default)
            limit: Number of data points (default: 30)

        Returns:
            Markdown table of commodity prices

        Examples:
            - bsc_get_commodity_prices() - All commodities
            - bsc_get_commodity_prices(commodity="gold") - Just gold
        """
        try:
            loader = get_data_loader()

            df = loader.get_macro_commodity()

            if df.empty:
                return "No commodity data available."

            # Filter by commodity type
            if commodity:
                commodity_lower = commodity.lower()
                if 'commodity' in df.columns:
                    df = df[df['commodity'].str.lower().str.contains(commodity_lower)]
                elif 'indicator' in df.columns:
                    df = df[df['indicator'].str.lower().str.contains(commodity_lower)]
                elif 'type' in df.columns:
                    df = df[df['type'].str.lower().str.contains(commodity_lower)]

            if df.empty:
                return f"No data found for commodity '{commodity}'."

            # Sort by date and limit
            if 'date' in df.columns:
                df = df.sort_values('date', ascending=False).head(limit)

            # Format date
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

            title = f"Commodity Prices"
            if commodity:
                title = f"{commodity.title()} Prices"
            title += f" (Last {len(df)} records)"

            return format_dataframe_markdown(df, title=title)

        except Exception as e:
            return handle_tool_error(e, "bsc_get_commodity_prices")

    @mcp.tool()
    def bsc_get_macro_overview() -> str:
        """
        Get a summary overview of current macro indicators.

        Returns current values for key macro metrics including
        interest rates, FX, bond yields, and commodity prices.

        Returns:
            Markdown formatted macro overview

        Examples:
            - bsc_get_macro_overview() - Current macro snapshot
        """
        try:
            loader = get_data_loader()

            df = loader.get_macro_commodity()

            if df.empty:
                return "No macro data available."

            # Get latest data
            if 'date' in df.columns:
                df = df.sort_values('date', ascending=False)

            latest_date = None
            if 'date' in df.columns:
                latest_date = pd.to_datetime(df.iloc[0]['date']).strftime('%Y-%m-%d')

            # Try to extract key metrics
            metrics = {}

            # Common column patterns
            value_cols = ['value', 'close', 'price', 'rate']
            type_cols = ['indicator', 'type', 'commodity', 'name']

            # Find the type and value columns
            type_col = None
            value_col = None

            for col in type_cols:
                if col in df.columns:
                    type_col = col
                    break

            for col in value_cols:
                if col in df.columns:
                    value_col = col
                    break

            if type_col and value_col:
                # Get latest value for each indicator
                for indicator in df[type_col].unique():
                    ind_data = df[df[type_col] == indicator].iloc[0]
                    metrics[indicator] = ind_data[value_col]

            response = f"""## Macro Economic Overview

**Latest Data:** {latest_date or 'N/A'}

### Key Indicators
| Indicator | Value |
|-----------|-------|
"""
            for name, value in list(metrics.items())[:15]:
                response += f"| {name} | {format_number(value)} |\n"

            if not metrics:
                # Fallback: show raw data
                response += "\n### Raw Data\n\n"
                response += format_dataframe_markdown(df.head(20))

            response += """
### Market Impact Notes
- Rising interest rates → Negative for growth stocks, positive for banks
- USD/VND depreciation → Positive for exporters, negative for importers
- Rising oil prices → Negative for airlines, positive for PVN stocks
"""
            return response

        except Exception as e:
            return handle_tool_error(e, "bsc_get_macro_overview")
