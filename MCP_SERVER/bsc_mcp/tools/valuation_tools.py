"""
Valuation Tools
===============

Tools for querying PE, PB, EV/EBITDA valuation data.

Tools:
------
1. bsc_get_ticker_valuation - Historical PE/PB for a ticker
2. bsc_get_valuation_stats - Valuation statistics (mean, percentile, z-score)
3. bsc_get_sector_valuation - Sector-level valuation comparison
4. bsc_compare_valuations - Compare valuations across tickers
5. bsc_get_vnindex_valuation - VN-Index PE/PB with bands
"""

from typing import Optional
from mcp.server.fastmcp import FastMCP
import pandas as pd
import numpy as np

from bsc_mcp.services.data_loader import get_data_loader
from bsc_mcp.utils.errors import handle_tool_error, TickerNotFoundError
from bsc_mcp.utils.formatters import (
    format_dataframe_markdown,
    format_number,
    format_percent,
    format_ticker_header
)


def register(mcp: FastMCP):
    """Register all valuation tools with the MCP server."""

    @mcp.tool()
    def bsc_get_ticker_valuation(
        ticker: str,
        metric: str = "PE",
        limit: int = 252
    ) -> str:
        """
        Get historical valuation data (PE/PB/PS/EV-EBITDA) for a ticker.

        Args:
            ticker: Stock symbol (e.g., "VNM", "VCB", "FPT")
            metric: Valuation metric - "PE", "PB", "PS", or "EV_EBITDA" (default: PE)
            limit: Number of days to return (default: 252 = ~1 year)

        Returns:
            Markdown table with historical valuation data

        Examples:
            - bsc_get_ticker_valuation("ACB") - ACB PE history
            - bsc_get_ticker_valuation("VNM", metric="PB") - VNM PB history
        """
        try:
            loader = get_data_loader()
            ticker = ticker.upper().strip()
            metric = metric.upper().strip()

            # Load appropriate valuation data
            if metric == "PE":
                df = loader.get_pe_historical()
                ratio_col = 'pe_ratio'
            elif metric == "PB":
                df = loader.get_pb_historical()
                ratio_col = 'pb_ratio'
            elif metric == "PS":
                df = loader.get_ps_historical()
                ratio_col = 'ps_ratio'
            elif metric == "EV_EBITDA":
                df = loader.get_ev_ebitda_historical()
                ratio_col = 'ev_ebitda'
            else:
                return f"Invalid metric '{metric}'. Use: PE, PB, PS, or EV_EBITDA"

            # Filter by ticker
            ticker_df = df[df['symbol'] == ticker].copy()

            if ticker_df.empty:
                all_tickers = df['symbol'].unique().tolist()
                suggestions = [t for t in all_tickers if t.startswith(ticker[:2])][:5]
                raise TickerNotFoundError(ticker, suggestions)

            # Sort and limit
            ticker_df = ticker_df.sort_values('date', ascending=False).head(limit)

            # Select columns
            cols = ['date', ratio_col]
            if 'close_price' in ticker_df.columns:
                cols.insert(1, 'close_price')

            result_df = ticker_df[cols].copy()

            # Format date
            result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')

            entity_type = loader.get_ticker_entity_type(ticker)
            header = format_ticker_header(ticker, entity_type)

            return header + format_dataframe_markdown(
                result_df,
                title=f"{metric} History (Last {len(result_df)} days)"
            )

        except TickerNotFoundError as e:
            return str(e)
        except Exception as e:
            return handle_tool_error(e, "bsc_get_ticker_valuation")

    @mcp.tool()
    def bsc_get_valuation_stats(
        ticker: str,
        metric: str = "PE",
        years: int = 5
    ) -> str:
        """
        Get valuation statistics for a ticker (current, mean, percentile, z-score).

        Calculates statistics over specified historical period to assess
        if current valuation is cheap or expensive vs history.

        Args:
            ticker: Stock symbol (e.g., "ACB", "VNM")
            metric: Valuation metric - "PE" or "PB" (default: PE)
            years: Historical period in years (default: 5)

        Returns:
            Markdown formatted valuation statistics with assessment

        Examples:
            - bsc_get_valuation_stats("ACB") - ACB PE statistics
            - bsc_get_valuation_stats("VNM", metric="PB", years=3)
        """
        try:
            loader = get_data_loader()
            ticker = ticker.upper().strip()
            metric = metric.upper().strip()

            # Load valuation data
            if metric == "PE":
                df = loader.get_pe_historical()
                ratio_col = 'pe_ratio'
            elif metric == "PB":
                df = loader.get_pb_historical()
                ratio_col = 'pb_ratio'
            else:
                return f"Invalid metric '{metric}'. Use: PE or PB"

            # Filter by ticker
            ticker_df = df[df['symbol'] == ticker].copy()

            if ticker_df.empty:
                raise TickerNotFoundError(ticker)

            # Sort by date
            ticker_df = ticker_df.sort_values('date', ascending=False)

            # Get current value
            current = ticker_df.iloc[0][ratio_col]
            current_date = pd.to_datetime(ticker_df.iloc[0]['date']).strftime('%Y-%m-%d')

            # Filter for historical period
            cutoff_date = pd.to_datetime(ticker_df.iloc[0]['date']) - pd.DateOffset(years=years)
            historical = ticker_df[pd.to_datetime(ticker_df['date']) >= cutoff_date][ratio_col].dropna()

            if len(historical) < 10:
                return f"Insufficient historical data for {ticker}. Need at least 10 data points."

            # Calculate statistics
            mean = historical.mean()
            std = historical.std()
            median = historical.median()
            min_val = historical.min()
            max_val = historical.max()

            # Calculate percentile
            percentile = (historical < current).sum() / len(historical) * 100

            # Calculate z-score
            z_score = (current - mean) / std if std > 0 else 0

            # Determine assessment
            if percentile <= 20:
                assessment = "**Significantly Undervalued** vs history"
            elif percentile <= 40:
                assessment = "**Undervalued** vs history"
            elif percentile <= 60:
                assessment = "**Fair Value** vs history"
            elif percentile <= 80:
                assessment = "**Overvalued** vs history"
            else:
                assessment = "**Significantly Overvalued** vs history"

            entity_type = loader.get_ticker_entity_type(ticker)
            header = format_ticker_header(ticker, entity_type)

            response = header + f"""### {metric} Valuation Statistics ({years}Y History)

| Metric | Value |
|--------|-------|
| **Current {metric}** | {format_number(current)} |
| **Date** | {current_date} |
| **{years}Y Mean** | {format_number(mean)} |
| **{years}Y Median** | {format_number(median)} |
| **{years}Y Std Dev** | {format_number(std)} |
| **{years}Y Min** | {format_number(min_val)} |
| **{years}Y Max** | {format_number(max_val)} |

### Valuation Position
| Metric | Value |
|--------|-------|
| **Percentile** | {format_number(percentile, 1)}th |
| **Z-Score** | {format_number(z_score)} |
| **Assessment** | {assessment} |

### Interpretation
- Percentile {format_number(percentile, 0)}th means current {metric} is higher than {format_number(percentile, 0)}% of historical values
- Z-Score {format_number(z_score)} means current {metric} is {abs(z_score):.1f} standard deviations {'above' if z_score > 0 else 'below'} the mean
"""
            return response

        except TickerNotFoundError as e:
            return str(e)
        except Exception as e:
            return handle_tool_error(e, "bsc_get_valuation_stats")

    @mcp.tool()
    def bsc_get_sector_valuation(
        sector: Optional[str] = None,
        metric: str = "PE"
    ) -> str:
        """
        Get sector-level valuation comparison.

        Args:
            sector: Optional sector name to filter. If None, shows all sectors
            metric: "PE" or "PB" (default: PE)

        Returns:
            Markdown table of sector valuations

        Examples:
            - bsc_get_sector_valuation() - All sectors PE
            - bsc_get_sector_valuation(sector="Ngân hàng") - Banking sector
        """
        try:
            loader = get_data_loader()

            # Load sector valuation data
            df = loader.get_sector_valuation()

            if df.empty:
                return "No sector valuation data available."

            # Filter by sector if provided
            if sector:
                df = df[df['sector'].str.contains(sector, case=False, na=False)]
                if df.empty:
                    return f"No data found for sector containing '{sector}'."

            # Get latest data for each sector
            if 'date' in df.columns:
                latest = df.sort_values('date', ascending=False).groupby('sector').first().reset_index()
            else:
                latest = df.groupby('sector').first().reset_index()

            # Select columns based on metric
            if metric.upper() == "PE":
                cols = ['sector', 'pe_ratio', 'pe_mean', 'pe_percentile']
            else:
                cols = ['sector', 'pb_ratio', 'pb_mean', 'pb_percentile']

            available_cols = [c for c in cols if c in latest.columns]
            result_df = latest[available_cols].copy()

            # Sort by PE/PB
            sort_col = 'pe_ratio' if 'pe_ratio' in result_df.columns else 'pb_ratio'
            if sort_col in result_df.columns:
                result_df = result_df.sort_values(sort_col)

            return format_dataframe_markdown(
                result_df,
                title=f"Sector {metric} Valuation ({len(result_df)} sectors)"
            )

        except Exception as e:
            return handle_tool_error(e, "bsc_get_sector_valuation")

    @mcp.tool()
    def bsc_compare_valuations(
        tickers: str,
        metric: str = "PE"
    ) -> str:
        """
        Compare valuations across multiple tickers.

        Args:
            tickers: Comma-separated ticker symbols (e.g., "VCB,ACB,TCB,MBB")
            metric: "PE" or "PB" (default: PE)

        Returns:
            Markdown comparison table with current vs historical stats

        Examples:
            - bsc_compare_valuations("VCB,ACB,TCB,MBB") - Compare bank PEs
            - bsc_compare_valuations("VNM,MSN,SAB", metric="PB")
        """
        try:
            loader = get_data_loader()

            # Parse tickers
            ticker_list = [t.strip().upper() for t in tickers.split(',')]

            if len(ticker_list) < 2:
                return "Please provide at least 2 tickers to compare."

            # Load valuation data
            if metric.upper() == "PE":
                df = loader.get_pe_historical()
                ratio_col = 'pe_ratio'
            else:
                df = loader.get_pb_historical()
                ratio_col = 'pb_ratio'

            results = []

            for ticker in ticker_list:
                ticker_df = df[df['symbol'] == ticker].sort_values('date', ascending=False)

                if ticker_df.empty:
                    results.append({
                        'Ticker': ticker,
                        f'Current {metric}': 'N/A',
                        '5Y Mean': 'N/A',
                        'Percentile': 'N/A'
                    })
                    continue

                current = ticker_df.iloc[0][ratio_col]

                # Calculate 5Y stats
                cutoff = pd.to_datetime(ticker_df.iloc[0]['date']) - pd.DateOffset(years=5)
                historical = ticker_df[pd.to_datetime(ticker_df['date']) >= cutoff][ratio_col].dropna()

                if len(historical) > 0:
                    mean = historical.mean()
                    percentile = (historical < current).sum() / len(historical) * 100
                else:
                    mean = None
                    percentile = None

                results.append({
                    'Ticker': ticker,
                    f'Current {metric}': format_number(current),
                    '5Y Mean': format_number(mean),
                    'Percentile': f"{format_number(percentile, 0)}th" if percentile else 'N/A'
                })

            df_results = pd.DataFrame(results)

            return format_dataframe_markdown(
                df_results,
                title=f"{metric} Valuation Comparison ({len(ticker_list)} tickers)"
            )

        except Exception as e:
            return handle_tool_error(e, "bsc_compare_valuations")

    @mcp.tool()
    def bsc_get_vnindex_valuation(limit: int = 60) -> str:
        """
        Get VN-Index valuation (PE/PB) with historical bands.

        Shows current VN-Index PE/PB vs historical mean +/- standard deviations.

        Args:
            limit: Number of days to show (default: 60)

        Returns:
            Markdown formatted VN-Index valuation overview

        Examples:
            - bsc_get_vnindex_valuation() - Latest 60 days
            - bsc_get_vnindex_valuation(limit=252) - Full year
        """
        try:
            loader = get_data_loader()

            df = loader.get_vnindex_valuation()

            if df.empty:
                return "No VN-Index valuation data available."

            # Sort and get recent data
            df = df.sort_values('date', ascending=False)
            recent = df.head(limit)
            latest = df.iloc[0]

            date_str = pd.to_datetime(latest['date']).strftime('%Y-%m-%d')

            # Get PE/PB values
            pe = latest.get('pe_ratio', latest.get('pe'))
            pb = latest.get('pb_ratio', latest.get('pb'))

            # Calculate statistics from full history
            pe_col = 'pe_ratio' if 'pe_ratio' in df.columns else 'pe'
            pb_col = 'pb_ratio' if 'pb_ratio' in df.columns else 'pb'

            pe_mean = df[pe_col].mean() if pe_col in df.columns else None
            pe_std = df[pe_col].std() if pe_col in df.columns else None
            pb_mean = df[pb_col].mean() if pb_col in df.columns else None
            pb_std = df[pb_col].std() if pb_col in df.columns else None

            # Calculate percentiles
            pe_percentile = (df[pe_col] < pe).sum() / len(df) * 100 if pe_col in df.columns and pd.notna(pe) else None
            pb_percentile = (df[pb_col] < pb).sum() / len(df) * 100 if pb_col in df.columns and pd.notna(pb) else None

            response = f"""## VN-Index Valuation ({date_str})

### Current Valuation
| Metric | Value | Mean | +1 Std | -1 Std | Percentile |
|--------|-------|------|--------|--------|------------|
| **PE** | {format_number(pe)} | {format_number(pe_mean)} | {format_number(pe_mean + pe_std if pe_mean and pe_std else None)} | {format_number(pe_mean - pe_std if pe_mean and pe_std else None)} | {format_number(pe_percentile, 0)}th |
| **PB** | {format_number(pb)} | {format_number(pb_mean)} | {format_number(pb_mean + pb_std if pb_mean and pb_std else None)} | {format_number(pb_mean - pb_std if pb_mean and pb_std else None)} | {format_number(pb_percentile, 0)}th |

### Interpretation
"""
            if pe_percentile:
                if pe_percentile <= 25:
                    response += "- VN-Index PE is in the **cheap zone** (bottom 25%)\n"
                elif pe_percentile >= 75:
                    response += "- VN-Index PE is in the **expensive zone** (top 25%)\n"
                else:
                    response += "- VN-Index PE is at **fair value** range\n"

            # Show recent trend
            cols = ['date', pe_col]
            if pb_col in recent.columns:
                cols.append(pb_col)
            trend_df = recent[cols].head(10).copy()
            trend_df['date'] = pd.to_datetime(trend_df['date']).dt.strftime('%Y-%m-%d')
            trend_df.columns = ['Date', 'PE', 'PB'] if 'PB' in trend_df.columns else ['Date', 'PE']

            response += f"\n### Recent Trend (Last 10 days)\n\n{format_dataframe_markdown(trend_df)}"

            return response

        except Exception as e:
            return handle_tool_error(e, "bsc_get_vnindex_valuation")
