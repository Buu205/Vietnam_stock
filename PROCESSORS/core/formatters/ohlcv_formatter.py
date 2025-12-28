#!/usr/bin/env python3
"""
OHLCV Data Formatter - Display Formatting Utilities
====================================================

Implements display formatting rules from ohlcv_data_schema.json.
Use this for all OHLCV data display in Streamlit app and reports.

Author: Claude Code
Date: 2025-12-07
"""

from pathlib import Path
import json
from typing import Union, Optional


class OHLCVFormatter:
    """
    Formatter for OHLCV data based on ohlcv_data_schema.json

    Usage:
        formatter = OHLCVFormatter()
        price_str = formatter.format_price(25750.5)
        # Returns: "25,750.50đ"

        pct_str = formatter.format_percentage(2.35, positive=True)
        # Returns: "+2.35%"
    """

    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize formatter with schema

        Args:
            schema_path: Path to ohlcv_data_schema.json (auto-detects if None)
        """
        # Default display formats (used when schema not found)
        self.default_formats = {
            'price': {'decimal_places': 2, 'currency_symbol': 'đ'},
            'percentage': {'decimal_places': 2, 'suffix': '%'},
            'ratio': {'decimal_places': 2},
            'volume': {'format': 'integer'},
            'market_cap': {'abbreviate': True}
        }

        if schema_path is None:
            # Auto-detect schema path (canonical v4.0.0)
            root = Path(__file__).resolve().parents[3]
            schema_path = root / "config" / "schemas" / "data" / "ohlcv_data_schema.json"

        # Try to load schema, use defaults if not found
        if schema_path.exists():
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    self.schema = json.load(f)
                self.display_formats = self.schema.get('display_formats', {})
            except Exception as e:
                import logging
                logging.warning(f"Failed to load schema from {schema_path}: {e}. Using defaults.")
                self.display_formats = {}
                self.schema = {'definitions': {'frequency_codes': {}}}
        else:
            # Schema not found, use defaults
            self.display_formats = {}
            self.schema = {'definitions': {'frequency_codes': {}}}

    def format_price(self, value: Union[float, int], include_currency: bool = True) -> str:
        """
        Format price value according to schema

        Args:
            value: Price value in VND
            include_currency: Whether to include currency symbol

        Returns:
            Formatted price string (e.g., "25,750.50đ")
        """
        if value is None or (isinstance(value, float) and not value == value):  # NaN check
            return "-"

        format_spec = self.display_formats.get('price', {})
        decimal_places = format_spec.get('decimal_places', 2)

        # Format with thousand separators and decimal places
        formatted = f"{value:,.{decimal_places}f}"

        if include_currency:
            currency = format_spec.get('currency_symbol', 'đ')
            formatted += currency

        return formatted

    def format_volume(self, value: Union[int, float]) -> str:
        """
        Format volume value according to schema

        Args:
            value: Volume value

        Returns:
            Formatted volume string (e.g., "1,250,000")
        """
        if value is None or (isinstance(value, float) and not value == value):  # NaN check
            return "-"

        # Volume is integer with thousand separators
        return f"{int(value):,}"

    def format_percentage(
        self,
        value: Union[float, int],
        positive: Optional[bool] = None,
        include_sign: bool = True
    ) -> str:
        """
        Format percentage value according to schema

        Args:
            value: Percentage value (e.g., 2.35 for 2.35%)
            positive: Whether value is positive (for color coding in UI)
            include_sign: Whether to include +/- sign

        Returns:
            Formatted percentage string (e.g., "+2.35%")
        """
        if value is None or (isinstance(value, float) and not value == value):  # NaN check
            return "-"

        format_spec = self.display_formats.get('percentage', {})
        decimal_places = format_spec.get('decimal_places', 2)

        formatted = f"{value:.{decimal_places}f}"

        if include_sign and value > 0:
            formatted = "+" + formatted

        suffix = format_spec.get('suffix', '%')
        formatted += suffix

        return formatted

    def format_market_cap(self, value: Union[float, int], abbreviate: bool = True) -> str:
        """
        Format market cap value according to schema

        Args:
            value: Market cap value in VND
            abbreviate: Whether to abbreviate billions (25.7B)

        Returns:
            Formatted market cap string
        """
        if value is None or (isinstance(value, float) and not value == value):  # NaN check
            return "-"

        if abbreviate:
            # Convert to billions
            billions = value / 1_000_000_000
            return f"{billions:.1f}B"
        else:
            # Full format with thousand separators
            return f"{int(value):,}"

    def format_ratio(self, value: Union[float, int]) -> str:
        """
        Format ratio value (PE, PB) according to schema

        Args:
            value: Ratio value

        Returns:
            Formatted ratio string (e.g., "12.35")
        """
        if value is None or (isinstance(value, float) and not value == value):  # NaN check
            return "-"

        format_spec = self.display_formats.get('ratio', {})
        decimal_places = format_spec.get('decimal_places', 2)

        return f"{value:.{decimal_places}f}"

    def get_frequency_description(self, freq_code: str) -> str:
        """
        Get description for frequency code

        Args:
            freq_code: Frequency code (D/W/M/Q/Y)

        Returns:
            Description string (e.g., "Daily")
        """
        freq_codes = self.schema.get('definitions', {}).get('frequency_codes', {})
        freq_info = freq_codes.get(freq_code, {})
        return freq_info.get('description', freq_code)


# Example usage and demo
if __name__ == "__main__":
    print("=== OHLCV Formatter Demo ===\n")

    formatter = OHLCVFormatter()

    # Price formatting
    print("1. Price Formatting:")
    print(f"   Input: 25750.5")
    print(f"   Output: {formatter.format_price(25750.5)}")
    print(f"   No currency: {formatter.format_price(25750.5, include_currency=False)}")
    print()

    # Volume formatting
    print("2. Volume Formatting:")
    print(f"   Input: 1250000")
    print(f"   Output: {formatter.format_volume(1250000)}")
    print()

    # Percentage formatting
    print("3. Percentage Formatting:")
    print(f"   Positive: {formatter.format_percentage(2.35, positive=True)}")
    print(f"   Negative: {formatter.format_percentage(-1.25, positive=False)}")
    print(f"   No sign: {formatter.format_percentage(2.35, include_sign=False)}")
    print()

    # Market cap formatting
    print("4. Market Cap Formatting:")
    print(f"   Input: 25750000000")
    print(f"   Abbreviated: {formatter.format_market_cap(25750000000)}")
    print(f"   Full: {formatter.format_market_cap(25750000000, abbreviate=False)}")
    print()

    # Ratio formatting
    print("5. Ratio Formatting:")
    print(f"   PE Ratio: {formatter.format_ratio(12.345)}")
    print(f"   PB Ratio: {formatter.format_ratio(1.89)}")
    print()

    # Frequency description
    print("6. Frequency Descriptions:")
    for freq in ['D', 'W', 'M', 'Q', 'Y']:
        print(f"   {freq}: {formatter.get_frequency_description(freq)}")
    print()

    print("✅ All formatting examples completed!")
