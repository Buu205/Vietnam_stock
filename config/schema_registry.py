#!/usr/bin/env python3
"""
Schema Registry - Central Schema Management System
===================================================

Single source of truth for ALL schemas in the stock dashboard system.

Usage:
    from config.schema_registry import SchemaRegistry

    # Singleton - initialized once
    registry = SchemaRegistry()

    # Get formatting
    price = registry.format_price(25750.5)  # "25,750.50đ"

    # Get colors
    color = registry.get_color('positive_change')  # "#00C853"

    # Get schema
    ohlcv_schema = registry.get_schema('ohlcv')

Author: Claude Code
Date: 2025-12-07
"""

from pathlib import Path
import json
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class SchemaRegistry:
    """
    Central registry for all schemas

    Singleton pattern - loads schemas once and caches them
    """
    _instance = None
    _schemas_loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SchemaRegistry, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not SchemaRegistry._schemas_loaded:
            self._load_all_schemas()
            SchemaRegistry._schemas_loaded = True

    def _load_all_schemas(self):
        """Load all schemas from config/schemas/"""
        self.config_dir = Path(__file__).parent
        self.schema_dir = self.config_dir / "schemas"

        # Load master schema
        master_path = self.schema_dir / "master_schema.json"
        with open(master_path, 'r', encoding='utf-8') as f:
            self.master_schema = json.load(f)

        # Extract commonly used settings
        self.app_metadata = self.master_schema['app_metadata']
        self.global_settings = self.master_schema['global_settings']
        self.theme = self.master_schema['theme']
        self.formatting_rules = self.master_schema['formatting_rules']
        self.frequency_codes = self.master_schema['frequency_codes']
        self.validation_thresholds = self.master_schema['validation_thresholds']
        self.entity_types = self.master_schema['entity_types']
        self.chart_defaults = self.master_schema['chart_defaults']

        # Cache for loaded schemas
        self._schema_cache = {}

        logger.info("SchemaRegistry initialized successfully")

    # ============================================================================
    # FORMATTING METHODS
    # ============================================================================

    def format_price(self, value: Union[float, int], include_currency: bool = True) -> str:
        """
        Format price using master schema rules

        Args:
            value: Price value
            include_currency: Whether to include currency symbol

        Returns:
            Formatted string (e.g., "25,750.50đ")
        """
        if value is None or (isinstance(value, float) and value != value):  # NaN
            return "-"

        rules = self.formatting_rules['price']
        decimal_places = rules['decimal_places']

        formatted = f"{value:,.{decimal_places}f}"

        if include_currency and rules['show_currency']:
            currency = self.global_settings['display']['currency_symbol']
            position = self.global_settings['display']['currency_position']

            if position == 'suffix':
                formatted += currency
            else:
                formatted = currency + formatted

        return formatted

    def format_volume(self, value: Union[int, float]) -> str:
        """Format volume using master schema rules"""
        if value is None or (isinstance(value, float) and value != value):
            return "-"

        rules = self.formatting_rules['volume']

        if rules.get('abbreviate_millions') and value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        else:
            return f"{int(value):,}"

    def format_percentage(
        self,
        value: Union[float, int],
        show_sign: Optional[bool] = None,
        color: bool = False
    ) -> str:
        """
        Format percentage using master schema rules

        Args:
            value: Percentage value
            show_sign: Override default sign showing
            color: If True, return color code based on positive/negative

        Returns:
            Formatted string or tuple (formatted, color) if color=True
        """
        if value is None or (isinstance(value, float) and value != value):
            return "-"

        rules = self.formatting_rules['percentage']
        decimal_places = rules['decimal_places']

        formatted = f"{value:.{decimal_places}f}"

        # Add sign
        if show_sign is None:
            show_sign = rules.get('show_sign', False)

        if show_sign and value > 0:
            formatted = "+" + formatted

        formatted += rules['suffix']

        if color:
            if value > 0:
                color_code = self.get_color('positive_change')
            elif value < 0:
                color_code = self.get_color('negative_change')
            else:
                color_code = self.get_color('neutral')
            return formatted, color_code

        return formatted

    def format_market_cap(self, value: Union[float, int], abbreviate: Optional[bool] = None) -> str:
        """Format market cap using master schema rules"""
        if value is None or (isinstance(value, float) and value != value):
            return "-"

        rules = self.formatting_rules['market_cap']

        if abbreviate is None:
            abbreviate = rules.get('abbreviate', True)

        if abbreviate:
            billions = value / 1_000_000_000
            decimal_places = rules['decimal_places']
            unit = rules.get('unit', 'B')
            return f"{billions:.{decimal_places}f}{unit}"
        else:
            return f"{int(value):,}"

    def format_ratio(self, value: Union[float, int]) -> str:
        """Format ratio (PE, PB) using master schema rules"""
        if value is None or (isinstance(value, float) and value != value):
            return "-"

        rules = self.formatting_rules['ratio']
        decimal_places = rules['decimal_places']
        return f"{value:.{decimal_places}f}"

    # ============================================================================
    # COLOR METHODS
    # ============================================================================

    def get_color(self, color_name: str) -> str:
        """
        Get color code from theme

        Args:
            color_name: Color name (e.g., 'positive_change', 'primary', 'success')

        Returns:
            Hex color code (e.g., "#00C853")
        """
        # Check semantic colors first
        if color_name in self.theme['semantic_colors']:
            return self.theme['semantic_colors'][color_name]['color']

        # Check base colors
        if color_name in self.theme['colors']:
            return self.theme['colors'][color_name]

        # Default
        logger.warning(f"Color '{color_name}' not found, returning default")
        return self.theme['colors']['primary']

    def get_entity_color(self, entity_type: str) -> str:
        """Get color for entity type"""
        if entity_type in self.entity_types:
            return self.entity_types[entity_type]['color']
        return self.theme['colors']['primary']

    def get_entity_icon(self, entity_type: str) -> str:
        """Get icon for entity type"""
        if entity_type in self.entity_types:
            return self.entity_types[entity_type]['icon']
        return "📊"

    # ============================================================================
    # SCHEMA LOADING
    # ============================================================================

    def get_schema(self, schema_name: str) -> Dict[str, Any]:
        """
        Load a specific schema

        Args:
            schema_name: Schema name (e.g., 'ohlcv', 'fundamental')

        Returns:
            Schema dictionary
        """
        if schema_name in self._schema_cache:
            return self._schema_cache[schema_name]

        # Find schema file
        schema_file = None

        # Check data schemas
        data_path = self.schema_dir / "data" / f"{schema_name}.json"
        if data_path.exists():
            schema_file = data_path

        # Check display schemas
        if not schema_file:
            display_path = self.schema_dir / "display" / f"{schema_name}.json"
            if display_path.exists():
                schema_file = display_path

        # Check metadata schemas
        if not schema_file:
            metadata_path = self.schema_dir / "metadata" / f"{schema_name}.json"
            if metadata_path.exists():
                schema_file = metadata_path

        # Fallback to old locations (backward compatibility)
        if not schema_file:
            # Check calculated_results/schemas/
            old_path = Path(__file__).parent.parent / "calculated_results" / "schemas" / f"{schema_name}_data_schema.json"
            if old_path.exists():
                schema_file = old_path
                logger.warning(f"Using old schema location: {old_path}")

        if not schema_file:
            raise FileNotFoundError(f"Schema '{schema_name}' not found")

        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)

        self._schema_cache[schema_name] = schema
        return schema

    # ============================================================================
    # VALIDATION
    # ============================================================================

    def get_validation_threshold(self, metric: str, threshold_type: str = 'typical_range') -> Any:
        """
        Get validation threshold for a metric

        Args:
            metric: Metric name (e.g., 'price', 'pe_ratio')
            threshold_type: Type of threshold ('min', 'max', 'typical_range')

        Returns:
            Threshold value
        """
        if metric in self.validation_thresholds:
            return self.validation_thresholds[metric].get(threshold_type)
        return None

    # ============================================================================
    # FREQUENCY
    # ============================================================================

    def get_frequency_info(self, freq_code: str) -> Dict[str, Any]:
        """Get frequency information"""
        return self.frequency_codes.get(freq_code, {})

    # ============================================================================
    # APP METADATA
    # ============================================================================

    @property
    def app_name(self) -> str:
        """Get application name"""
        return self.app_metadata['app_name']

    @property
    def app_version(self) -> str:
        """Get application version"""
        return self.app_metadata['version']

    @property
    def default_language(self) -> str:
        """Get default language"""
        return self.app_metadata['default_language']

    # ============================================================================
    # CHART DEFAULTS
    # ============================================================================

    def get_chart_defaults(self) -> Dict[str, Any]:
        """Get default chart configuration"""
        return self.chart_defaults.copy()

    # ============================================================================
    # STREAMLIT HELPERS
    # ============================================================================

    def get_streamlit_theme_css(self) -> str:
        """
        Generate CSS for Streamlit based on theme

        Returns:
            CSS string to inject into Streamlit
        """
        colors = self.theme['colors']

        css = f"""
        <style>
        :root {{
            --primary-color: {colors['primary']};
            --secondary-color: {colors['secondary']};
            --success-color: {colors['success']};
            --danger-color: {colors['danger']};
            --warning-color: {colors['warning']};
            --info-color: {colors['info']};
        }}

        .positive {{
            color: {self.get_color('positive_change')};
            font-weight: bold;
        }}

        .negative {{
            color: {self.get_color('negative_change')};
            font-weight: bold;
        }}

        .neutral {{
            color: {self.get_color('neutral')};
        }}
        </style>
        """
        return css


# Convenience functions for direct import
_registry = None

def get_registry() -> SchemaRegistry:
    """Get singleton SchemaRegistry instance"""
    global _registry
    if _registry is None:
        _registry = SchemaRegistry()
    return _registry


# Direct access functions
def format_price(value: Union[float, int], include_currency: bool = True) -> str:
    """Format price using global registry"""
    return get_registry().format_price(value, include_currency)


def format_volume(value: Union[int, float]) -> str:
    """Format volume using global registry"""
    return get_registry().format_volume(value)


def format_percentage(value: Union[float, int], show_sign: Optional[bool] = None, color: bool = False):
    """Format percentage using global registry"""
    return get_registry().format_percentage(value, show_sign, color)


def get_color(color_name: str) -> str:
    """Get color from global registry"""
    return get_registry().get_color(color_name)


# Demo and testing
if __name__ == "__main__":
    print("=" * 70)
    print("SCHEMA REGISTRY DEMO")
    print("=" * 70)

    registry = SchemaRegistry()

    print("\n1. App Metadata:")
    print(f"   App Name: {registry.app_name}")
    print(f"   Version: {registry.app_version}")
    print(f"   Language: {registry.default_language}")

    print("\n2. Formatting:")
    print(f"   Price: {registry.format_price(25750.5)}")
    print(f"   Volume: {registry.format_volume(1250000)}")
    print(f"   Percentage: {registry.format_percentage(2.35, show_sign=True)}")
    print(f"   Market Cap: {registry.format_market_cap(25750000000)}")
    print(f"   Ratio: {registry.format_ratio(12.345)}")

    print("\n3. Colors:")
    print(f"   Positive: {registry.get_color('positive_change')}")
    print(f"   Negative: {registry.get_color('negative_change')}")
    print(f"   Primary: {registry.get_color('primary')}")
    print(f"   Success: {registry.get_color('success')}")

    print("\n4. Entity Types:")
    for entity, info in registry.entity_types.items():
        color = info['color']
        icon = info['icon']
        desc = info['description']
        print(f"   {entity}: {icon} {desc} ({color})")

    print("\n5. Frequency Codes:")
    for freq, info in registry.frequency_codes.items():
        print(f"   {freq}: {info['description']} - {info['typical_use']}")

    print("\n6. Validation Thresholds:")
    print(f"   PE Ratio range: {registry.get_validation_threshold('pe_ratio', 'typical_range')}")
    print(f"   ROE range: {registry.get_validation_threshold('roe', 'typical_range')}")

    print("\n" + "=" * 70)
    print("✅ Schema Registry initialized successfully!")
    print("=" * 70)
