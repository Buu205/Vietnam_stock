"""
Discovery Tools
===============

Tools for discovering and searching tickers, sectors, and metadata.

Tools:
------
1. bsc_list_tickers - List all available tickers
2. bsc_get_ticker_info - Get detailed info for a ticker
3. bsc_list_sectors - List all sectors
4. bsc_search_tickers - Search tickers by keyword
5. bsc_get_peers - Get peer companies in same sector
"""

from typing import Optional
from mcp.server.fastmcp import FastMCP

from bsc_mcp.services.data_loader import get_data_loader
from bsc_mcp.utils.errors import handle_tool_error, TickerNotFoundError
from bsc_mcp.utils.formatters import format_dataframe_markdown
import pandas as pd


def register(mcp: FastMCP):
    """Register all discovery tools with the MCP server."""

    @mcp.tool()
    def bsc_list_tickers(
        entity_type: Optional[str] = None,
        sector: Optional[str] = None,
        limit: int = 50
    ) -> str:
        """
        List all available stock tickers with optional filtering.

        Args:
            entity_type: Filter by type - "BANK", "COMPANY", "INSURANCE", "SECURITY", or None for all
            sector: Filter by sector name (Vietnamese), e.g., "Ngân hàng", "Bất động sản"
            limit: Maximum number of tickers to return (default: 50)

        Returns:
            Markdown table of tickers with entity type and sector

        Examples:
            - bsc_list_tickers() - List all tickers
            - bsc_list_tickers(entity_type="BANK") - List all banks
            - bsc_list_tickers(sector="Ngân hàng") - List banking sector
        """
        try:
            loader = get_data_loader()

            # Get tickers from technical data (most comprehensive)
            tech_df = loader.get_technical_basic()
            tickers = tech_df['symbol'].unique().tolist()

            # Build ticker info
            results = []
            for ticker in sorted(tickers):
                etype = loader.get_ticker_entity_type(ticker)

                # Apply entity_type filter
                if entity_type and etype != entity_type.upper():
                    continue

                # Get sector from fundamental data
                ticker_sector = None
                try:
                    if etype == 'BANK':
                        df = loader.get_bank_fundamentals()
                    elif etype == 'INSURANCE':
                        df = loader.get_insurance_fundamentals()
                    elif etype == 'SECURITY':
                        df = loader.get_security_fundamentals()
                    else:
                        df = loader.get_company_fundamentals()

                    ticker_data = df[df['symbol'] == ticker]
                    if not ticker_data.empty and 'sector' in ticker_data.columns:
                        ticker_sector = ticker_data.iloc[0].get('sector')
                except Exception:
                    pass

                # Apply sector filter
                if sector and ticker_sector != sector:
                    continue

                results.append({
                    'Ticker': ticker,
                    'Type': etype or 'N/A',
                    'Sector': ticker_sector or 'N/A'
                })

                if len(results) >= limit:
                    break

            if not results:
                return f"No tickers found matching filters: entity_type={entity_type}, sector={sector}"

            df = pd.DataFrame(results)
            response = format_dataframe_markdown(
                df,
                title=f"Available Tickers ({len(results)} found)"
            )

            if len(results) == limit:
                response += f"\n\n*Showing first {limit} results. Use `limit` parameter for more.*"

            return response

        except Exception as e:
            return handle_tool_error(e, "bsc_list_tickers")

    @mcp.tool()
    def bsc_get_ticker_info(ticker: str) -> str:
        """
        Get detailed information about a specific ticker.

        Args:
            ticker: Stock symbol (e.g., "VCB", "VNM", "FPT") - case-insensitive

        Returns:
            Detailed ticker information including entity type, sector, and data availability

        Examples:
            - bsc_get_ticker_info("VCB") - Get Vietcombank info
            - bsc_get_ticker_info("vnm") - Get Vinamilk info (lowercase works)
        """
        try:
            loader = get_data_loader()
            ticker = ticker.upper().strip()

            # Check if ticker exists
            all_tickers = loader.get_available_tickers()
            if ticker not in all_tickers:
                # Find suggestions
                suggestions = [t for t in all_tickers if t.startswith(ticker[:2])][:5]
                raise TickerNotFoundError(ticker, suggestions)

            # Get entity type
            entity_type = loader.get_ticker_entity_type(ticker) or "UNKNOWN"

            # Get sector and other info
            sector = None
            exchange = None
            latest_date = None

            try:
                if entity_type == 'BANK':
                    df = loader.get_bank_fundamentals()
                elif entity_type == 'INSURANCE':
                    df = loader.get_insurance_fundamentals()
                elif entity_type == 'SECURITY':
                    df = loader.get_security_fundamentals()
                else:
                    df = loader.get_company_fundamentals()

                ticker_data = df[df['symbol'] == ticker]
                if not ticker_data.empty:
                    if 'sector' in ticker_data.columns:
                        sector = ticker_data.iloc[-1].get('sector')
                    if 'exchange' in ticker_data.columns:
                        exchange = ticker_data.iloc[-1].get('exchange')
            except Exception:
                pass

            # Get latest technical data date
            try:
                tech_df = loader.get_technical_basic()
                ticker_tech = tech_df[tech_df['symbol'] == ticker]
                if not ticker_tech.empty and 'date' in ticker_tech.columns:
                    latest_date = ticker_tech['date'].max()
            except Exception:
                pass

            # Check BSC forecast coverage
            has_bsc = False
            try:
                bsc_df = loader.get_bsc_individual()
                has_bsc = ticker in bsc_df['symbol'].values
            except Exception:
                pass

            # Build response
            response = f"""## {ticker} - Ticker Information

| Field | Value |
|-------|-------|
| **Symbol** | {ticker} |
| **Entity Type** | {entity_type} |
| **Sector** | {sector or 'N/A'} |
| **Exchange** | {exchange or 'N/A'} |
| **Latest Data** | {latest_date or 'N/A'} |

### Data Availability
- **Fundamental Metrics**: Yes
- **Valuation History**: Yes
- **Technical Indicators**: Yes
- **BSC Forecast**: {'Yes' if has_bsc else 'No'}

### Quick Actions
- Use `bsc_get_company_financials("{ticker}")` for financials
- Use `bsc_get_ticker_valuation("{ticker}")` for PE/PB history
- Use `bsc_get_technical_indicators("{ticker}")` for technical data
"""
            if has_bsc:
                response += f'- Use `bsc_get_bsc_forecast("{ticker}")` for analyst forecast\n'

            return response

        except TickerNotFoundError as e:
            return str(e)
        except Exception as e:
            return handle_tool_error(e, "bsc_get_ticker_info")

    @mcp.tool()
    def bsc_list_sectors(entity_type: Optional[str] = None) -> str:
        """
        List all industry sectors with ticker counts.

        Args:
            entity_type: Optional filter - "BANK", "COMPANY", "INSURANCE", "SECURITY"

        Returns:
            Markdown table of sectors with ticker counts

        Examples:
            - bsc_list_sectors() - List all sectors
            - bsc_list_sectors(entity_type="COMPANY") - Only company sectors
        """
        try:
            loader = get_data_loader()

            # Collect sectors from all fundamental data
            sector_counts = {}

            def add_sectors(df, etype):
                if 'sector' in df.columns:
                    for sector in df['sector'].dropna().unique():
                        if sector not in sector_counts:
                            sector_counts[sector] = {'count': 0, 'entity_type': etype}
                        sector_counts[sector]['count'] += df[df['sector'] == sector]['symbol'].nunique()

            # Load each entity type
            if not entity_type or entity_type.upper() == 'COMPANY':
                try:
                    add_sectors(loader.get_company_fundamentals(), 'COMPANY')
                except FileNotFoundError:
                    pass

            if not entity_type or entity_type.upper() == 'BANK':
                try:
                    add_sectors(loader.get_bank_fundamentals(), 'BANK')
                except FileNotFoundError:
                    pass

            if not entity_type or entity_type.upper() == 'INSURANCE':
                try:
                    add_sectors(loader.get_insurance_fundamentals(), 'INSURANCE')
                except FileNotFoundError:
                    pass

            if not entity_type or entity_type.upper() == 'SECURITY':
                try:
                    add_sectors(loader.get_security_fundamentals(), 'SECURITY')
                except FileNotFoundError:
                    pass

            if not sector_counts:
                return "No sectors found in the data."

            # Build results
            results = []
            for sector, info in sorted(sector_counts.items()):
                results.append({
                    'Sector': sector,
                    'Entity Type': info['entity_type'],
                    'Tickers': info['count']
                })

            df = pd.DataFrame(results)
            return format_dataframe_markdown(
                df,
                title=f"Vietnamese Stock Market Sectors ({len(results)} sectors)"
            )

        except Exception as e:
            return handle_tool_error(e, "bsc_list_sectors")

    @mcp.tool()
    def bsc_search_tickers(query: str, limit: int = 20) -> str:
        """
        Search for tickers by keyword or name pattern.

        Args:
            query: Search keyword (case-insensitive) - searches ticker symbols and sectors
            limit: Maximum results to return (default: 20)

        Returns:
            Markdown table of matching tickers

        Examples:
            - bsc_search_tickers("bank") - Find banking-related stocks
            - bsc_search_tickers("VN") - Find tickers starting with VN
            - bsc_search_tickers("thực phẩm") - Find food sector stocks
        """
        try:
            loader = get_data_loader()
            query_lower = query.lower().strip()

            # Get all tickers
            all_tickers = loader.get_available_tickers()

            results = []
            for ticker in all_tickers:
                entity_type = loader.get_ticker_entity_type(ticker)

                # Get sector
                sector = None
                try:
                    if entity_type == 'BANK':
                        df = loader.get_bank_fundamentals()
                    elif entity_type == 'INSURANCE':
                        df = loader.get_insurance_fundamentals()
                    elif entity_type == 'SECURITY':
                        df = loader.get_security_fundamentals()
                    else:
                        df = loader.get_company_fundamentals()

                    ticker_data = df[df['symbol'] == ticker]
                    if not ticker_data.empty and 'sector' in ticker_data.columns:
                        sector = ticker_data.iloc[0].get('sector', '')
                except Exception:
                    sector = ''

                # Check for matches
                match_type = None
                if query_lower in ticker.lower():
                    match_type = "ticker"
                elif sector and query_lower in sector.lower():
                    match_type = "sector"

                if match_type:
                    results.append({
                        'Ticker': ticker,
                        'Type': entity_type or 'N/A',
                        'Sector': sector or 'N/A',
                        'Match': match_type
                    })

                if len(results) >= limit:
                    break

            if not results:
                return (
                    f"## No Results Found\n\n"
                    f"No tickers found matching '{query}'.\n\n"
                    f"**Tips:**\n"
                    f"- Try different spelling\n"
                    f"- Use Vietnamese sector names (e.g., 'Ngân hàng')\n"
                    f"- Use `bsc_list_sectors()` to see all sectors"
                )

            df = pd.DataFrame(results)
            return format_dataframe_markdown(
                df,
                title=f"Search Results for '{query}' ({len(results)} found)"
            )

        except Exception as e:
            return handle_tool_error(e, "bsc_search_tickers")

    @mcp.tool()
    def bsc_get_peers(
        ticker: str,
        limit: int = 10,
        exclude_self: bool = True
    ) -> str:
        """
        Get peer companies in the same sector.

        Args:
            ticker: Stock symbol to find peers for
            limit: Maximum number of peers to return (default: 10)
            exclude_self: Whether to exclude the input ticker (default: True)

        Returns:
            Markdown list of peer tickers with basic info

        Examples:
            - bsc_get_peers("VCB") - Find other banks
            - bsc_get_peers("VNM") - Find other F&B companies
        """
        try:
            loader = get_data_loader()
            ticker = ticker.upper().strip()

            # Validate ticker
            all_tickers = loader.get_available_tickers()
            if ticker not in all_tickers:
                suggestions = [t for t in all_tickers if t.startswith(ticker[:2])][:5]
                raise TickerNotFoundError(ticker, suggestions)

            # Get entity type and sector
            entity_type = loader.get_ticker_entity_type(ticker)

            # Get sector
            sector = None
            try:
                if entity_type == 'BANK':
                    df = loader.get_bank_fundamentals()
                elif entity_type == 'INSURANCE':
                    df = loader.get_insurance_fundamentals()
                elif entity_type == 'SECURITY':
                    df = loader.get_security_fundamentals()
                else:
                    df = loader.get_company_fundamentals()

                ticker_data = df[df['symbol'] == ticker]
                if not ticker_data.empty and 'sector' in ticker_data.columns:
                    sector = ticker_data.iloc[0].get('sector')
            except Exception:
                pass

            if not sector:
                return f"Cannot find sector for {ticker}. Unable to determine peers."

            # Find peers in same sector
            peers = []
            sector_df = df[df['sector'] == sector]

            for peer in sector_df['symbol'].unique():
                if exclude_self and peer == ticker:
                    continue

                peers.append({
                    'Ticker': peer,
                    'Type': entity_type or 'N/A'
                })

                if len(peers) >= limit:
                    break

            if not peers:
                return f"No peers found for {ticker} in sector '{sector}'."

            df_peers = pd.DataFrame(peers)
            response = f"""## Peers for {ticker}

**Sector:** {sector}
**Total Peers:** {len(sector_df['symbol'].unique()) - (1 if exclude_self else 0)}
**Showing:** {len(peers)}

{format_dataframe_markdown(df_peers)}

### Compare with Peers
- Use `bsc_compare_fundamentals` to compare financial metrics
- Use `bsc_compare_valuations` to compare PE/PB ratios
"""
            return response

        except TickerNotFoundError as e:
            return str(e)
        except Exception as e:
            return handle_tool_error(e, "bsc_get_peers")
