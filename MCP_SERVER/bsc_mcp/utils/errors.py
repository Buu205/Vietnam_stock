"""
Error Handling
==============

Custom exceptions and error handling utilities.
"""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class TickerNotFoundError(Exception):
    """Raised when a ticker doesn't exist in the data."""

    def __init__(self, ticker: str, suggestions: Optional[List[str]] = None):
        self.ticker = ticker
        self.suggestions = suggestions or []
        msg = f"Ticker '{ticker}' not found."
        if suggestions:
            msg += f" Did you mean: {', '.join(suggestions[:5])}?"
        super().__init__(msg)


class DataNotFoundError(Exception):
    """Raised when requested data is not available."""

    def __init__(self, data_type: str, details: Optional[str] = None):
        self.data_type = data_type
        msg = f"Data not found: {data_type}"
        if details:
            msg += f". {details}"
        super().__init__(msg)


class InvalidParameterError(Exception):
    """Raised when an invalid parameter is provided."""

    def __init__(self, param_name: str, value: str, valid_options: Optional[List[str]] = None):
        self.param_name = param_name
        self.value = value
        msg = f"Invalid value '{value}' for parameter '{param_name}'."
        if valid_options:
            msg += f" Valid options: {', '.join(valid_options)}"
        super().__init__(msg)


def handle_tool_error(error: Exception, tool_name: str) -> str:
    """
    Format error for MCP response.

    Args:
        error: The exception that occurred
        tool_name: Name of the tool that failed

    Returns:
        User-friendly error message
    """
    logger.error(f"Error in {tool_name}: {error}", exc_info=True)

    if isinstance(error, TickerNotFoundError):
        return str(error)

    if isinstance(error, DataNotFoundError):
        return str(error)

    if isinstance(error, InvalidParameterError):
        return str(error)

    if isinstance(error, FileNotFoundError):
        return (
            f"**Data file not found**\n\n"
            f"The required data file is missing. Please run the data pipeline:\n"
            f"```bash\n"
            f"python3 PROCESSORS/daily_sector_complete_update.py\n"
            f"```"
        )

    if isinstance(error, PermissionError):
        return f"**Permission denied** when accessing data files."

    # Generic error
    return (
        f"**Error in {tool_name}**\n\n"
        f"An unexpected error occurred: {str(error)}\n\n"
        f"Please try again or check the data files."
    )


def find_similar_tickers(ticker: str, all_tickers: List[str], max_suggestions: int = 5) -> List[str]:
    """
    Find similar tickers for suggestions.

    Args:
        ticker: The ticker that wasn't found
        all_tickers: List of all valid tickers
        max_suggestions: Maximum number of suggestions

    Returns:
        List of similar ticker symbols
    """
    ticker = ticker.upper()
    suggestions = []

    # Exact prefix match
    prefix_matches = [t for t in all_tickers if t.startswith(ticker[:2])]
    suggestions.extend(prefix_matches[:max_suggestions])

    # Contains match
    if len(suggestions) < max_suggestions:
        contains_matches = [
            t for t in all_tickers
            if ticker in t and t not in suggestions
        ]
        suggestions.extend(contains_matches[:max_suggestions - len(suggestions)])

    return suggestions[:max_suggestions]


def validate_ticker(ticker: str, all_tickers: List[str]) -> str:
    """
    Validate and normalize a ticker symbol.

    Args:
        ticker: Ticker to validate
        all_tickers: List of valid tickers

    Returns:
        Normalized ticker (uppercase)

    Raises:
        TickerNotFoundError: If ticker is not valid
    """
    normalized = ticker.upper().strip()

    if normalized in all_tickers:
        return normalized

    # Try to find suggestions
    suggestions = find_similar_tickers(normalized, all_tickers)
    raise TickerNotFoundError(normalized, suggestions)


def validate_date_format(date_str: Optional[str], param_name: str = "date") -> Optional[str]:
    """
    Validate date string format (YYYY-MM-DD).

    Args:
        date_str: Date string to validate (or None)
        param_name: Parameter name for error message

    Returns:
        Validated date string, or None if input was None

    Raises:
        InvalidParameterError: If date format is invalid
    """
    if date_str is None:
        return None

    from datetime import datetime

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise InvalidParameterError(
            param_name,
            date_str,
            ["YYYY-MM-DD format (e.g., 2024-12-31)"]
        )


def validate_limit(limit: int, min_val: int = 1, max_val: int = 1000) -> int:
    """
    Validate limit parameter is within bounds.

    Args:
        limit: Limit value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Validated limit value

    Raises:
        InvalidParameterError: If limit is out of bounds
    """
    if limit < min_val or limit > max_val:
        raise InvalidParameterError(
            "limit",
            str(limit),
            [f"Integer between {min_val} and {max_val}"]
        )
    return limit


def validate_dataframe_schema(
    df,
    expected_columns: List[str],
    source_name: str = "data"
) -> None:
    """
    Validate DataFrame has expected columns.

    Args:
        df: DataFrame to validate
        expected_columns: List of required column names
        source_name: Name of data source for error message

    Raises:
        DataNotFoundError: If required columns are missing
    """
    if df is None or df.empty:
        return

    missing = set(expected_columns) - set(df.columns)
    if missing:
        logger.warning(
            f"Schema validation: {source_name} missing columns: {missing}"
        )
