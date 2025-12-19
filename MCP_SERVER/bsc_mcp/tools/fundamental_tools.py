"""
Fundamental Tools
=================

Tools for querying company financial metrics.

Tools:
------
1. bsc_get_company_financials - Get financial metrics for a company
2. bsc_get_bank_financials - Get bank-specific metrics
3. bsc_get_latest_fundamentals - Get latest quarter data
4. bsc_compare_fundamentals - Compare multiple tickers
5. bsc_screen_fundamentals - Screen stocks by criteria
"""

from typing import Optional, List
from mcp.server.fastmcp import FastMCP
import pandas as pd

from bsc_mcp.services.data_loader import get_data_loader
from bsc_mcp.utils.errors import handle_tool_error, TickerNotFoundError
from bsc_mcp.utils.formatters import (
    format_dataframe_markdown,
    format_number,
    format_percent,
    format_billions,
    format_ticker_header
)


def register(mcp: FastMCP):
    """Register all fundamental tools with the MCP server."""

    @mcp.tool()
    def bsc_get_company_financials(
        ticker: str,
        period: str = "Quarterly",
        limit: int = 8
    ) -> str:
        """
        Get financial metrics for a company/bank/insurance/security.

        Automatically detects entity type and returns appropriate metrics.

        Args:
            ticker: Stock symbol (e.g., "VNM", "VCB", "FPT")
            period: "Quarterly" or "Yearly" (default: Quarterly)
            limit: Number of periods to return (default: 8)

        Returns:
            Markdown table with key financial metrics by period

        Examples:
            - bsc_get_company_financials("VNM") - Vinamilk quarterly data
            - bsc_get_company_financials("VCB", period="Yearly") - VCB yearly data
        """
        try:
            loader = get_data_loader()
            ticker = ticker.upper().strip()

            # Determine entity type
            entity_type = loader.get_ticker_entity_type(ticker)

            if not entity_type:
                all_tickers = loader.get_available_tickers()
                suggestions = [t for t in all_tickers if t.startswith(ticker[:2])][:5]
                raise TickerNotFoundError(ticker, suggestions)

            # Load appropriate data
            if entity_type == 'BANK':
                df = loader.get_bank_fundamentals()
                key_metrics = ['symbol', 'year', 'quarter', 'nii', 'ppop', 'npatmi',
                              'roe', 'roa', 'nim', 'npl_ratio', 'casa_ratio', 'cir', 'car']
            elif entity_type == 'INSURANCE':
                df = loader.get_insurance_fundamentals()
                key_metrics = ['symbol', 'year', 'quarter', 'net_revenue', 'npatmi',
                              'roe', 'roa', 'combined_ratio', 'claims_ratio']
            elif entity_type == 'SECURITY':
                df = loader.get_security_fundamentals()
                key_metrics = ['symbol', 'year', 'quarter', 'net_revenue', 'npatmi',
                              'roe', 'roa', 'brokerage_revenue', 'trading_income']
            else:
                df = loader.get_company_fundamentals()
                key_metrics = ['symbol', 'year', 'quarter', 'net_revenue', 'gross_profit',
                              'npatmi', 'roe', 'roa', 'gross_margin', 'net_margin', 'eps', 'bvps']

            # Filter by ticker
            ticker_df = df[df['symbol'] == ticker].copy()

            if ticker_df.empty:
                raise TickerNotFoundError(ticker)

            # Filter by period type
            if period.lower() == "yearly":
                ticker_df = ticker_df[ticker_df['quarter'].isna() | (ticker_df['quarter'] == 0)]
            else:
                ticker_df = ticker_df[ticker_df['quarter'].notna() & (ticker_df['quarter'] > 0)]

            # Sort and limit
            ticker_df = ticker_df.sort_values(['year', 'quarter'], ascending=[False, False])
            ticker_df = ticker_df.head(limit)

            # Select available columns
            available_cols = [c for c in key_metrics if c in ticker_df.columns]
            result_df = ticker_df[available_cols].copy()

            # Create period label
            if period.lower() == "quarterly":
                result_df['Period'] = result_df.apply(
                    lambda x: f"Q{int(x['quarter'])}/{int(x['year'])}" if pd.notna(x.get('quarter')) else f"{int(x['year'])}",
                    axis=1
                )
            else:
                result_df['Period'] = result_df['year'].apply(lambda x: str(int(x)))

            # Reorder columns
            cols = ['Period'] + [c for c in available_cols if c not in ['symbol', 'year', 'quarter']]
            result_df = result_df[cols]

            # Get sector
            sector = ticker_df.iloc[0].get('sector', 'N/A') if 'sector' in ticker_df.columns else 'N/A'

            header = format_ticker_header(ticker, entity_type, sector)

            return header + format_dataframe_markdown(
                result_df,
                title=f"Financial Metrics ({period})"
            )

        except TickerNotFoundError as e:
            return str(e)
        except Exception as e:
            return handle_tool_error(e, "bsc_get_company_financials")

    @mcp.tool()
    def bsc_get_bank_financials(
        ticker: str,
        period: str = "Quarterly",
        limit: int = 8
    ) -> str:
        """
        Get bank-specific financial metrics (NIM, NPL, CASA, CAR, CIR).

        Args:
            ticker: Bank ticker (e.g., "VCB", "ACB", "TCB", "MBB")
            period: "Quarterly" or "Yearly" (default: Quarterly)
            limit: Number of periods to return (default: 8)

        Returns:
            Markdown table with bank-specific metrics

        Examples:
            - bsc_get_bank_financials("VCB") - Vietcombank metrics
            - bsc_get_bank_financials("ACB", limit=4) - ACB last 4 quarters
        """
        try:
            loader = get_data_loader()
            ticker = ticker.upper().strip()

            # Load bank data
            df = loader.get_bank_fundamentals()

            # Filter by ticker
            ticker_df = df[df['symbol'] == ticker].copy()

            if ticker_df.empty:
                # Check if it's a valid ticker but not a bank
                entity_type = loader.get_ticker_entity_type(ticker)
                if entity_type and entity_type != 'BANK':
                    return f"{ticker} is not a bank (type: {entity_type}). Use `bsc_get_company_financials` instead."
                raise TickerNotFoundError(ticker)

            # Bank-specific metrics
            bank_metrics = [
                'year', 'quarter', 'nii', 'ppop', 'npatmi',
                'roe', 'roa', 'nim', 'npl_ratio', 'casa_ratio',
                'ldr', 'cir', 'car'
            ]

            # Filter by period
            if period.lower() == "yearly":
                ticker_df = ticker_df[ticker_df['quarter'].isna() | (ticker_df['quarter'] == 0)]
            else:
                ticker_df = ticker_df[ticker_df['quarter'].notna() & (ticker_df['quarter'] > 0)]

            # Sort and limit
            ticker_df = ticker_df.sort_values(['year', 'quarter'], ascending=[False, False])
            ticker_df = ticker_df.head(limit)

            # Select available columns
            available_cols = [c for c in bank_metrics if c in ticker_df.columns]
            result_df = ticker_df[available_cols].copy()

            # Create period label
            if period.lower() == "quarterly":
                result_df['Period'] = result_df.apply(
                    lambda x: f"Q{int(x['quarter'])}/{int(x['year'])}" if pd.notna(x.get('quarter')) else f"{int(x['year'])}",
                    axis=1
                )
            else:
                result_df['Period'] = result_df['year'].apply(lambda x: str(int(x)))

            # Reorder columns
            cols = ['Period'] + [c for c in available_cols if c not in ['year', 'quarter']]
            result_df = result_df[cols]

            header = format_ticker_header(ticker, "BANK", "Ngân hàng")

            return header + format_dataframe_markdown(
                result_df,
                title=f"Bank Metrics ({period})"
            )

        except TickerNotFoundError as e:
            return str(e)
        except Exception as e:
            return handle_tool_error(e, "bsc_get_bank_financials")

    @mcp.tool()
    def bsc_get_latest_fundamentals(ticker: str) -> str:
        """
        Get the most recent fundamental data for a ticker.

        Returns a comprehensive snapshot of the latest available metrics.

        Args:
            ticker: Stock symbol (e.g., "VNM", "VCB")

        Returns:
            Markdown formatted latest metrics with key ratios

        Examples:
            - bsc_get_latest_fundamentals("VNM") - Latest Vinamilk data
            - bsc_get_latest_fundamentals("ACB") - Latest ACB bank data
        """
        try:
            loader = get_data_loader()
            ticker = ticker.upper().strip()

            # Determine entity type
            entity_type = loader.get_ticker_entity_type(ticker)

            if not entity_type:
                all_tickers = loader.get_available_tickers()
                suggestions = [t for t in all_tickers if t.startswith(ticker[:2])][:5]
                raise TickerNotFoundError(ticker, suggestions)

            # Load appropriate data
            if entity_type == 'BANK':
                df = loader.get_bank_fundamentals()
            elif entity_type == 'INSURANCE':
                df = loader.get_insurance_fundamentals()
            elif entity_type == 'SECURITY':
                df = loader.get_security_fundamentals()
            else:
                df = loader.get_company_fundamentals()

            # Get latest row
            ticker_df = df[df['symbol'] == ticker].copy()

            if ticker_df.empty:
                raise TickerNotFoundError(ticker)

            # Sort to get latest
            ticker_df = ticker_df.sort_values(['year', 'quarter'], ascending=[False, False])
            latest = ticker_df.iloc[0]

            # Build response
            sector = latest.get('sector', 'N/A')
            year = int(latest.get('year', 0))
            quarter = int(latest.get('quarter', 0)) if pd.notna(latest.get('quarter')) else None
            period_str = f"Q{quarter}/{year}" if quarter else str(year)

            header = format_ticker_header(ticker, entity_type, sector)

            response = header + f"### Latest Data: {period_str}\n\n"

            # Format key metrics based on entity type
            if entity_type == 'BANK':
                response += f"""| Metric | Value |
|--------|-------|
| **Net Interest Income** | {format_billions(latest.get('nii'))} |
| **PPOP** | {format_billions(latest.get('ppop'))} |
| **Net Profit (NPATMI)** | {format_billions(latest.get('npatmi'))} |
| **ROE** | {format_percent(latest.get('roe'))} |
| **ROA** | {format_percent(latest.get('roa'))} |
| **NIM** | {format_percent(latest.get('nim'))} |
| **NPL Ratio** | {format_percent(latest.get('npl_ratio'))} |
| **CASA Ratio** | {format_percent(latest.get('casa_ratio'))} |
| **CIR** | {format_percent(latest.get('cir'))} |
| **CAR** | {format_percent(latest.get('car'))} |
"""
            else:
                response += f"""| Metric | Value |
|--------|-------|
| **Net Revenue** | {format_billions(latest.get('net_revenue'))} |
| **Gross Profit** | {format_billions(latest.get('gross_profit'))} |
| **Net Profit (NPATMI)** | {format_billions(latest.get('npatmi'))} |
| **ROE** | {format_percent(latest.get('roe'))} |
| **ROA** | {format_percent(latest.get('roa'))} |
| **Gross Margin** | {format_percent(latest.get('gross_margin'))} |
| **Net Margin** | {format_percent(latest.get('net_margin'))} |
| **EPS** | {format_number(latest.get('eps'))} |
| **BVPS** | {format_number(latest.get('bvps'))} |
"""
            return response

        except TickerNotFoundError as e:
            return str(e)
        except Exception as e:
            return handle_tool_error(e, "bsc_get_latest_fundamentals")

    @mcp.tool()
    def bsc_compare_fundamentals(
        tickers: str,
        metrics: Optional[str] = None
    ) -> str:
        """
        Compare fundamental metrics across multiple tickers.

        Args:
            tickers: Comma-separated ticker symbols (e.g., "VCB,ACB,TCB,MBB")
            metrics: Comma-separated metrics to compare (default: auto-select based on entity type)
                     Options: roe, roa, net_margin, gross_margin, eps, bvps, nim, npl_ratio

        Returns:
            Markdown comparison table

        Examples:
            - bsc_compare_fundamentals("VCB,ACB,TCB,MBB") - Compare 4 banks
            - bsc_compare_fundamentals("VNM,MSN,SAB", metrics="roe,net_margin,eps")
        """
        try:
            loader = get_data_loader()

            # Parse tickers
            ticker_list = [t.strip().upper() for t in tickers.split(',')]

            if len(ticker_list) < 2:
                return "Please provide at least 2 tickers to compare."

            if len(ticker_list) > 10:
                return "Please limit comparison to 10 tickers or fewer."

            # Parse metrics
            if metrics:
                metric_list = [m.strip().lower() for m in metrics.split(',')]
            else:
                metric_list = None

            # Collect data for each ticker
            results = []

            for ticker in ticker_list:
                entity_type = loader.get_ticker_entity_type(ticker)

                if not entity_type:
                    results.append({'Ticker': ticker, 'Error': 'Not found'})
                    continue

                # Load appropriate data
                if entity_type == 'BANK':
                    df = loader.get_bank_fundamentals()
                    default_metrics = ['roe', 'roa', 'nim', 'npl_ratio', 'casa_ratio']
                elif entity_type == 'INSURANCE':
                    df = loader.get_insurance_fundamentals()
                    default_metrics = ['roe', 'roa', 'combined_ratio']
                elif entity_type == 'SECURITY':
                    df = loader.get_security_fundamentals()
                    default_metrics = ['roe', 'roa', 'net_margin']
                else:
                    df = loader.get_company_fundamentals()
                    default_metrics = ['roe', 'roa', 'gross_margin', 'net_margin', 'eps']

                # Get latest data
                ticker_df = df[df['symbol'] == ticker].sort_values(['year', 'quarter'], ascending=[False, False])

                if ticker_df.empty:
                    results.append({'Ticker': ticker, 'Error': 'No data'})
                    continue

                latest = ticker_df.iloc[0]

                # Use provided metrics or defaults
                use_metrics = metric_list if metric_list else default_metrics

                row = {'Ticker': ticker, 'Type': entity_type}
                for m in use_metrics:
                    if m in latest.index:
                        val = latest[m]
                        if 'ratio' in m or 'margin' in m or m in ['roe', 'roa', 'nim']:
                            row[m.upper()] = format_percent(val)
                        else:
                            row[m.upper()] = format_number(val)
                    else:
                        row[m.upper()] = 'N/A'

                results.append(row)

            df_results = pd.DataFrame(results)
            return format_dataframe_markdown(
                df_results,
                title=f"Fundamental Comparison ({len(ticker_list)} tickers)"
            )

        except Exception as e:
            return handle_tool_error(e, "bsc_compare_fundamentals")

    @mcp.tool()
    def bsc_screen_fundamentals(
        roe_min: Optional[float] = None,
        roe_max: Optional[float] = None,
        pe_max: Optional[float] = None,
        entity_type: Optional[str] = None,
        sector: Optional[str] = None,
        limit: int = 20
    ) -> str:
        """
        Screen stocks by fundamental criteria.

        Args:
            roe_min: Minimum ROE (e.g., 15 for 15%)
            roe_max: Maximum ROE
            pe_max: Maximum PE ratio
            entity_type: Filter by "BANK", "COMPANY", "INSURANCE", "SECURITY"
            sector: Filter by sector name
            limit: Maximum results (default: 20)

        Returns:
            Markdown table of stocks matching criteria

        Examples:
            - bsc_screen_fundamentals(roe_min=20) - Stocks with ROE > 20%
            - bsc_screen_fundamentals(roe_min=15, entity_type="BANK") - Banks with ROE > 15%
            - bsc_screen_fundamentals(pe_max=10, roe_min=15) - Value + quality stocks
        """
        try:
            loader = get_data_loader()

            results = []

            # Determine which data sources to search
            entity_types_to_check = []
            if entity_type:
                entity_types_to_check = [entity_type.upper()]
            else:
                entity_types_to_check = ['COMPANY', 'BANK', 'INSURANCE', 'SECURITY']

            for etype in entity_types_to_check:
                try:
                    if etype == 'BANK':
                        df = loader.get_bank_fundamentals()
                    elif etype == 'INSURANCE':
                        df = loader.get_insurance_fundamentals()
                    elif etype == 'SECURITY':
                        df = loader.get_security_fundamentals()
                    else:
                        df = loader.get_company_fundamentals()
                except FileNotFoundError:
                    continue

                # Get latest data for each ticker
                for ticker in df['symbol'].unique():
                    ticker_df = df[df['symbol'] == ticker].sort_values(
                        ['year', 'quarter'], ascending=[False, False]
                    )

                    if ticker_df.empty:
                        continue

                    latest = ticker_df.iloc[0]

                    # Apply filters
                    if sector and latest.get('sector') != sector:
                        continue

                    roe = latest.get('roe')
                    if roe_min is not None and (pd.isna(roe) or roe < roe_min):
                        continue
                    if roe_max is not None and (pd.isna(roe) or roe > roe_max):
                        continue

                    # Get PE if needed
                    pe = None
                    if pe_max is not None:
                        try:
                            pe_df = loader.get_pe_historical()
                            pe_ticker = pe_df[pe_df['symbol'] == ticker]
                            if not pe_ticker.empty:
                                pe = pe_ticker.sort_values('date', ascending=False).iloc[0]['pe_ratio']
                                if pd.isna(pe) or pe > pe_max:
                                    continue
                        except Exception:
                            pass

                    results.append({
                        'Ticker': ticker,
                        'Type': etype,
                        'Sector': latest.get('sector', 'N/A'),
                        'ROE': format_percent(roe),
                        'ROA': format_percent(latest.get('roa')),
                        'PE': format_number(pe) if pe else 'N/A'
                    })

                    if len(results) >= limit:
                        break

                if len(results) >= limit:
                    break

            if not results:
                return "No stocks found matching the specified criteria."

            df_results = pd.DataFrame(results)

            # Build filter description
            filters = []
            if roe_min:
                filters.append(f"ROE >= {roe_min}%")
            if roe_max:
                filters.append(f"ROE <= {roe_max}%")
            if pe_max:
                filters.append(f"PE <= {pe_max}")
            if entity_type:
                filters.append(f"Type = {entity_type}")
            if sector:
                filters.append(f"Sector = {sector}")

            filter_str = ", ".join(filters) if filters else "None"

            return format_dataframe_markdown(
                df_results,
                title=f"Stock Screening Results ({len(results)} found)\n\n**Filters:** {filter_str}"
            )

        except Exception as e:
            return handle_tool_error(e, "bsc_screen_fundamentals")
