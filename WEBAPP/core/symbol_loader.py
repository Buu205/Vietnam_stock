"""
Symbol Loader - Centralized symbol loading for WEBAPP
======================================================

Tải danh sách symbols từ master_symbols.json.
Single source of truth cho tất cả symbol loading trong project.

Usage:
    from WEBAPP.core.symbol_loader import SymbolLoader, get_all_symbols

    loader = SymbolLoader()
    all_symbols = loader.get_all_symbols()  # 315 liquid symbols
    bank_symbols = loader.get_symbols_by_entity('BANK')  # 22 banks
"""

from __future__ import annotations
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Default paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MASTER_SYMBOLS = PROJECT_ROOT / "DATA" / "metadata" / "master_symbols.json"
FALLBACK_LIQUID_TICKERS = PROJECT_ROOT / "DATA" / "metadata" / "liquid_tickers.json"


class SymbolLoader:
    """Centralized symbol loader for WEBAPP and all pipelines."""

    _instance = None
    _symbols_data = None

    def __new__(cls):
        """Singleton pattern for efficiency."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize SymbolLoader.

        Args:
            config_path: Path to master_symbols.json (optional)
        """
        if SymbolLoader._symbols_data is None:
            self.config_path = config_path or DEFAULT_MASTER_SYMBOLS
            self._load_data()

    def _load_data(self):
        """Load symbol data from JSON file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    SymbolLoader._symbols_data = json.load(f)
                logger.info(f"Loaded symbols from {self.config_path}")
            elif FALLBACK_LIQUID_TICKERS.exists():
                with open(FALLBACK_LIQUID_TICKERS, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Convert liquid_tickers format to master_symbols format
                all_symbols = []
                for tickers in data.get('tickers', {}).values():
                    all_symbols.extend(tickers)
                SymbolLoader._symbols_data = {
                    'all_symbols': sorted(set(all_symbols)),
                    'symbols_by_entity': data.get('tickers', {})
                }
                logger.warning(f"Using fallback liquid_tickers.json")
            else:
                logger.error(f"No symbol config found at {self.config_path}")
                SymbolLoader._symbols_data = {'all_symbols': [], 'symbols_by_entity': {}}
        except Exception as e:
            logger.error(f"Error loading symbols: {e}")
            SymbolLoader._symbols_data = {'all_symbols': [], 'symbols_by_entity': {}}

    def get_all_symbols(self) -> List[str]:
        """Get all liquid symbols."""
        return SymbolLoader._symbols_data.get('all_symbols', [])

    def get_symbols_by_entity(self, entity_type: str) -> List[str]:
        """
        Get symbols for a specific entity type.

        Args:
            entity_type: One of 'BANK', 'COMPANY', 'SECURITY', 'INSURANCE'

        Returns:
            List of symbols for that entity type
        """
        entity_type = entity_type.upper()
        return SymbolLoader._symbols_data.get('symbols_by_entity', {}).get(entity_type, [])

    def get_statistics(self) -> Dict:
        """Get statistics about the symbol list."""
        return SymbolLoader._symbols_data.get('statistics', {})

    def get_criteria(self) -> Dict:
        """Get the criteria used for filtering symbols."""
        return SymbolLoader._symbols_data.get('criteria', {})

    def is_liquid(self, symbol: str) -> bool:
        """Check if a symbol is in the liquid list."""
        return symbol.upper() in self.get_all_symbols()

    def filter_liquid(self, symbols: List[str]) -> List[str]:
        """Filter a list of symbols to only include liquid ones."""
        liquid_set = set(self.get_all_symbols())
        return [s for s in symbols if s.upper() in liquid_set]

    def get_symbol_info(self, symbol: str) -> Dict:
        """
        Get basic info about a symbol.

        Args:
            symbol: Stock ticker

        Returns:
            Dict with symbol, entity_type
        """
        symbol = symbol.upper()
        for entity_type, symbols in SymbolLoader._symbols_data.get('symbols_by_entity', {}).items():
            if symbol in symbols:
                return {
                    'symbol': symbol,
                    'entity_type': entity_type,
                    'is_liquid': True
                }
        return {
            'symbol': symbol,
            'entity_type': 'UNKNOWN',
            'is_liquid': False
        }

    @staticmethod
    def clear_cache():
        """Clear cached data (useful for testing or after updating config)."""
        SymbolLoader._symbols_data = None
        SymbolLoader._instance = None


# Convenience functions for backward compatibility
def get_all_symbols() -> List[str]:
    """Get all liquid symbols."""
    return SymbolLoader().get_all_symbols()


def get_symbols_by_entity(entity_type: str) -> List[str]:
    """Get symbols for a specific entity type."""
    return SymbolLoader().get_symbols_by_entity(entity_type)


def get_symbols_by_sector(sector: str) -> List[str]:
    """
    Get symbols by sector name.
    Note: This requires SectorRegistry for sector->ticker mapping.
    """
    try:
        from config.registries import SectorRegistry
        registry = SectorRegistry()
        return registry.get_tickers_by_sector(sector)
    except Exception:
        return []


def get_symbol_info(symbol: str) -> Dict:
    """Get basic info about a symbol."""
    return SymbolLoader().get_symbol_info(symbol)


def is_liquid(symbol: str) -> bool:
    """Check if a symbol is liquid."""
    return SymbolLoader().is_liquid(symbol)


if __name__ == "__main__":
    # Test
    loader = SymbolLoader()
    print(f"Total symbols: {len(loader.get_all_symbols())}")
    print(f"Banks: {len(loader.get_symbols_by_entity('BANK'))}")
    print(f"Companies: {len(loader.get_symbols_by_entity('COMPANY'))}")
    print(f"Securities: {len(loader.get_symbols_by_entity('SECURITY'))}")
    print(f"Insurance: {len(loader.get_symbols_by_entity('INSURANCE'))}")
    print()
    print(f"VCB info: {loader.get_symbol_info('VCB')}")
    print(f"Is VCB liquid? {loader.is_liquid('VCB')}")
