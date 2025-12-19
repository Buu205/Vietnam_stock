"""
Sector Tools
============

Tools for querying sector analysis data (FA/TA scores, signals).

Tools:
------
1. bsc_get_sector_scores - Get FA/TA scores and signals
2. bsc_get_sector_history - Historical sector scores
3. bsc_compare_sectors - Compare multiple sectors
"""

from typing import Optional
from mcp.server.fastmcp import FastMCP
import pandas as pd

from bsc_mcp.services.data_loader import get_data_loader
from bsc_mcp.utils.errors import handle_tool_error
from bsc_mcp.utils.formatters import format_dataframe_markdown, format_number, format_percent


def register(mcp: FastMCP):
    """Register all sector tools with the MCP server."""

    @mcp.tool()
    def bsc_get_sector_scores(
        sector: Optional[str] = None,
        signal: Optional[str] = None
    ) -> str:
        """
        Get sector FA/TA scores and trading signals.

        Args:
            sector: Optional sector name filter
            signal: Filter by signal - "MUA" (BUY), "BÁN" (SELL), "GIỮ" (HOLD)

        Returns:
            Markdown table of sector scores with signals

        Examples:
            - bsc_get_sector_scores() - All sectors latest scores
            - bsc_get_sector_scores(signal="MUA") - Only BUY signals
            - bsc_get_sector_scores(sector="Ngân hàng") - Banking sector
        """
        try:
            loader = get_data_loader()

            # Try sector valuation data first
            try:
                df = loader.get_sector_valuation()
            except FileNotFoundError:
                try:
                    df = loader.get_sector_fundamentals()
                except FileNotFoundError:
                    return "No sector analysis data available."

            if df.empty:
                return "No sector data available."

            # Get latest data for each sector
            if 'date' in df.columns:
                df = df.sort_values('date', ascending=False)
                latest = df.groupby('sector').first().reset_index()
            else:
                latest = df.copy()

            # Apply filters
            if sector:
                latest = latest[latest['sector'].str.contains(sector, case=False, na=False)]

            if signal and 'signal' in latest.columns:
                latest = latest[latest['signal'].str.upper() == signal.upper()]

            if latest.empty:
                return f"No sectors found matching: sector={sector}, signal={signal}"

            # Build result
            result_cols = ['sector']

            # Add score columns if available
            score_cols = ['fa_score', 'ta_score', 'combined_score', 'signal', 'signal_strength']
            for col in score_cols:
                if col in latest.columns:
                    result_cols.append(col)

            # Add valuation columns if available
            val_cols = ['pe_ratio', 'pb_ratio', 'pe_percentile']
            for col in val_cols:
                if col in latest.columns:
                    result_cols.append(col)

            result_df = latest[result_cols].copy()

            # Sort by combined score or FA score
            if 'combined_score' in result_df.columns:
                result_df = result_df.sort_values('combined_score', ascending=False)
            elif 'fa_score' in result_df.columns:
                result_df = result_df.sort_values('fa_score', ascending=False)

            return format_dataframe_markdown(
                result_df,
                title=f"Sector Analysis ({len(result_df)} sectors)"
            )

        except Exception as e:
            return handle_tool_error(e, "bsc_get_sector_scores")

    @mcp.tool()
    def bsc_get_sector_history(
        sector: str,
        limit: int = 30
    ) -> str:
        """
        Get historical FA/TA scores for a specific sector.

        Args:
            sector: Sector name (e.g., "Ngân hàng", "Bất động sản")
            limit: Number of days to return (default: 30)

        Returns:
            Markdown table of historical sector scores

        Examples:
            - bsc_get_sector_history("Ngân hàng") - Banking sector history
            - bsc_get_sector_history("Bất động sản", limit=60) - Real estate 60 days
        """
        try:
            loader = get_data_loader()

            # Try multiple data sources
            df = None
            try:
                df = loader.get_sector_valuation()
            except FileNotFoundError:
                pass

            if df is None or df.empty:
                try:
                    df = loader.get_sector_fundamentals()
                except FileNotFoundError:
                    return "No sector historical data available."

            if df.empty:
                return "No sector data available."

            # Filter by sector
            sector_df = df[df['sector'].str.contains(sector, case=False, na=False)]

            if sector_df.empty:
                # Show available sectors
                available = df['sector'].unique().tolist()
                return f"Sector '{sector}' not found. Available sectors: {', '.join(available[:10])}"

            # Sort by date and limit
            if 'date' in sector_df.columns:
                sector_df = sector_df.sort_values('date', ascending=False).head(limit)

            # Select columns
            result_cols = ['date']
            optional_cols = ['fa_score', 'ta_score', 'combined_score', 'signal',
                          'pe_ratio', 'pb_ratio']

            for col in optional_cols:
                if col in sector_df.columns:
                    result_cols.append(col)

            result_df = sector_df[result_cols].copy()

            # Format date
            if 'date' in result_df.columns:
                result_df['date'] = pd.to_datetime(result_df['date']).dt.strftime('%Y-%m-%d')

            sector_name = sector_df.iloc[0]['sector']

            return format_dataframe_markdown(
                result_df,
                title=f"Sector History: {sector_name} (Last {len(result_df)} days)"
            )

        except Exception as e:
            return handle_tool_error(e, "bsc_get_sector_history")

    @mcp.tool()
    def bsc_compare_sectors(
        sectors: Optional[str] = None,
        metrics: Optional[str] = None
    ) -> str:
        """
        Compare multiple sectors on key metrics.

        Args:
            sectors: Comma-separated sector names. If None, compares all sectors
            metrics: Comma-separated metrics to compare:
                    - fa_score, ta_score, combined_score
                    - pe_ratio, pb_ratio
                    - Default: fa_score, ta_score, pe_ratio

        Returns:
            Markdown comparison table

        Examples:
            - bsc_compare_sectors() - Compare all sectors
            - bsc_compare_sectors(sectors="Ngân hàng,Bất động sản,Công nghệ")
        """
        try:
            loader = get_data_loader()

            # Load sector data
            try:
                df = loader.get_sector_valuation()
            except FileNotFoundError:
                try:
                    df = loader.get_sector_fundamentals()
                except FileNotFoundError:
                    return "No sector data available."

            if df.empty:
                return "No sector data available."

            # Get latest data
            if 'date' in df.columns:
                df = df.sort_values('date', ascending=False)
                latest = df.groupby('sector').first().reset_index()
            else:
                latest = df.copy()

            # Filter sectors if specified
            if sectors:
                sector_list = [s.strip() for s in sectors.split(',')]
                mask = latest['sector'].apply(
                    lambda x: any(s.lower() in x.lower() for s in sector_list)
                )
                latest = latest[mask]

            if latest.empty:
                return f"No sectors found matching: {sectors}"

            # Select metrics
            if metrics:
                metric_list = [m.strip() for m in metrics.split(',')]
            else:
                metric_list = ['fa_score', 'ta_score', 'pe_ratio', 'signal']

            result_cols = ['sector'] + [m for m in metric_list if m in latest.columns]
            result_df = latest[result_cols].copy()

            # Sort by first score column
            for col in ['combined_score', 'fa_score', 'ta_score']:
                if col in result_df.columns:
                    result_df = result_df.sort_values(col, ascending=False)
                    break

            return format_dataframe_markdown(
                result_df,
                title=f"Sector Comparison ({len(result_df)} sectors)"
            )

        except Exception as e:
            return handle_tool_error(e, "bsc_compare_sectors")
