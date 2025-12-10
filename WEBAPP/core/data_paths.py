"""
Centralized Data Paths Configuration
=====================================

Single source of truth for all data paths in the project.
Giúp dễ dàng thay đổi đường dẫn mà không cần sửa nhiều file.

Author: AI Assistant
Date: 2025-12-09
Version: 2.0.0 - Updated to v4.0.0 Canonical Architecture

Usage:
    from WEBAPP.core.data_paths import DataPaths, get_fundamental_path
    
    # Method 1: Using static methods
    bank_path = DataPaths.fundamental('bank')
    
    # Method 2: Using convenience functions
    company_path = get_fundamental_path('company')
    
    # Method 3: Using constants (legacy support)
    pe_path = DataPaths.PE_DATA
"""

from pathlib import Path
from typing import Literal
import sys
import os

# Handle imports for both direct execution and module import
if __name__ == "__main__":
    # Direct execution - add project to path
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent.parent
    sys.path.insert(0, str(project_root))
    from WEBAPP.core.utils import get_data_path
else:
    # Module import - use relative import
    from .utils import get_data_path


class DataPaths:
    """
    Centralized configuration for all data paths.
    
    All paths are relative to project root and resolved using get_data_path().
    """
    
    # ============================================================================
    # FUNDAMENTAL DATA (Calculated Results)
    # ============================================================================
    
    @staticmethod
    def fundamental(
        entity_type: Literal['bank', 'company', 'insurance', 'security']
    ) -> Path:
        """
        Get fundamental data path by entity type.
        
        Args:
            entity_type: Type of financial entity
                - 'bank': Banking sector
                - 'company': Corporate sector (non-financial)
                - 'insurance': Insurance companies
                - 'security': Securities firms
                
        Returns:
            Path to fundamental metrics parquet file
            
        Raises:
            ValueError: If entity_type is not recognized
            
        Example:
            >>> DataPaths.fundamental('bank')
            Path('.../DATA/processed/fundamental/bank/bank_financial_metrics.parquet')
        
        Note:
            Files contain calculated metrics including:
            - Income statement metrics (Net Revenue, EBIT, EBITDA, etc.)
            - Balance sheet metrics (Assets, Liabilities, Equity)
            - Cash flow metrics (Operating CF, Free CF, Capex)
            - Profitability ratios (ROE, ROA, Margins)
            - Growth rates (YoY, QoQ)
        """
        entity_map = {
            'bank': 'fundamental/bank/bank_financial_metrics.parquet',
            'company': 'fundamental/company/company_financial_metrics.parquet',
            'insurance': 'fundamental/insurance/insurance_financial_metrics.parquet',
            'security': 'fundamental/security/security_financial_metrics.parquet'
        }
        
        if entity_type not in entity_map:
            raise ValueError(
                f"Unknown entity type: '{entity_type}'. "
                f"Valid options: {list(entity_map.keys())}"
            )
            
        return get_data_path(f"DATA/processed/{entity_map[entity_type]}")
    
    # Legacy constants for backward compatibility
    @property
    def BANK_FUNDAMENTAL(self) -> Path:
        """Legacy: Use DataPaths.fundamental('bank') instead"""
        return self.fundamental('bank')
    
    @property
    def COMPANY_FUNDAMENTAL(self) -> Path:
        """Legacy: Use DataPaths.fundamental('company') instead"""
        return self.fundamental('company')
    
    @property
    def INSURANCE_FUNDAMENTAL(self) -> Path:
        """Legacy: Use DataPaths.fundamental('insurance') instead"""
        return self.fundamental('insurance')
    
    @property
    def SECURITY_FUNDAMENTAL(self) -> Path:
        """Legacy: Use DataPaths.fundamental('security') instead"""
        return self.fundamental('security')
    
    # ============================================================================
    # VALUATION DATA
    # ============================================================================
    
    @staticmethod
    def valuation(
        metric: Literal['pe', 'pb', 'ev_ebitda', 'vnindex_pe', 'sector_pe']
    ) -> Path:
        """
        Get valuation data path by metric type.
        
        Args:
            metric: Valuation metric type
                - 'pe': Price-to-Earnings ratio (all symbols)
                - 'pb': Price-to-Book ratio (all symbols)
                - 'ev_ebitda': EV/EBITDA ratio (all symbols)
                - 'vnindex_pe': VN-Index historical PE
                - 'sector_pe': Sector-level PE analysis
                
        Returns:
            Path to valuation parquet file
            
        Raises:
            ValueError: If metric is not recognized
            
        Example:
            >>> DataPaths.valuation('pe')
            Path('.../DATA/processed/valuation/pe/pe_historical_all_symbols_final.parquet')
        """
        metric_map = {
            'pe': 'valuation/pe/pe_historical_all_symbols_final.parquet',
            'pb': 'valuation/pb/pb_historical_all_symbols_final.parquet',
            'ev_ebitda': 'valuation/ev_ebitda/ev_ebitda_historical_all_symbols_final.parquet',
            'vnindex_pe': 'valuation/vnindex_pe_historical_final.parquet',
            'sector_pe': 'valuation/sector_pe/sector_pe_historical_final.parquet'
        }
        
        if metric not in metric_map:
            raise ValueError(
                f"Unknown valuation metric: '{metric}'. "
                f"Valid options: {list(metric_map.keys())}"
            )
            
        return get_data_path(f"DATA/processed/{metric_map[metric]}")
    
    # Legacy constants
    @property
    def PE_DATA(self) -> Path:
        """Legacy: Use DataPaths.valuation('pe') instead"""
        return self.valuation('pe')
    
    @property
    def PB_DATA(self) -> Path:
        """Legacy: Use DataPaths.valuation('pb') instead"""
        return self.valuation('pb')
    
    @property
    def EV_EBITDA_DATA(self) -> Path:
        """Legacy: Use DataPaths.valuation('ev_ebitda') instead"""
        return self.valuation('ev_ebitda')
    
    # ============================================================================
    # TECHNICAL DATA
    # ============================================================================
    
    @staticmethod
    def technical(
        indicator: Literal['ma', 'ema', 'rsi', 'macd', 'bollinger', 'signals', 'market_breadth']
    ) -> Path:
        """
        Get technical indicator data path.
        
        Args:
            indicator: Technical indicator type
                - 'ma': Simple Moving Averages
                - 'ema': Exponential Moving Averages
                - 'rsi': Relative Strength Index
                - 'macd': MACD indicator
                - 'bollinger': Bollinger Bands
                - 'signals': Trading signals
                - 'market_breadth': Market breadth indicators
                
        Returns:
            Path to technical indicator parquet file
            
        Raises:
            ValueError: If indicator is not recognized
        """
        indicator_map = {
            'ma': 'technical/moving_averages/ma_all_symbols.parquet',
            'ema': 'technical/exponential_moving_averages/ema_all_symbols.parquet',
            'rsi': 'technical/rsi/rsi_all_symbols.parquet',
            'macd': 'technical/macd/macd_all_symbols.parquet',
            'bollinger': 'technical/bollinger_bands/bb_all_symbols.parquet',
            'signals': 'technical/signals/trading_signals.parquet',
            'market_breadth': 'technical/market_breadth/market_breadth_daily.parquet'
        }
        
        if indicator not in indicator_map:
            raise ValueError(
                f"Unknown technical indicator: '{indicator}'. "
                f"Valid options: {list(indicator_map.keys())}"
            )
            
        return get_data_path(f"DATA/processed/{indicator_map[indicator]}")
    
    # ============================================================================
    # RAW DATA (Data Warehouse)
    # ============================================================================
    
    @staticmethod
    def raw_fundamental(
        entity_type: Literal['bank', 'company', 'insurance', 'security']
    ) -> Path:
        """
        Get raw fundamental data from warehouse.
        
        Args:
            entity_type: Type of financial entity
            
        Returns:
            Path to raw fundamental data file (processed)
            
        Example:
            >>> DataPaths.raw_fundamental('company')
            Path('.../DATA/processed/fundamental/company_full.parquet')
        """
        valid_types = ['bank', 'company', 'insurance', 'security']
        if entity_type not in valid_types:
            raise ValueError(
                f"Unknown entity type: '{entity_type}'. "
                f"Valid options: {valid_types}"
            )

        return get_data_path(
            f"DATA/processed/fundamental/{entity_type}_full.parquet"
        )
    
    @staticmethod
    def raw_ohlcv() -> Path:
        """
        Get raw OHLCV data with market cap.
        
        Returns:
            Path to OHLCV parquet file
        """
        return get_data_path("DATA/raw/ohlcv/OHLCV_mktcap.parquet")
    
    # ============================================================================
    # MACRO DATA
    # ============================================================================
    
    @staticmethod
    def macro(
        indicator: Literal['deposit_interest', 'exchange_rates', 'gov_bond_yields', 'interest_rates']
    ) -> Path:
        """
        Get macro indicator data path.
        
        Args:
            indicator: Macro indicator type
                - 'deposit_interest': Deposit interest rates
                - 'exchange_rates': Exchange rates (USD/VND, etc.)
                - 'gov_bond_yields': Government bond yields
                - 'interest_rates': Interest rates
                
        Returns:
            Path to macro indicator parquet file
            
        Raises:
            ValueError: If indicator is not recognized
            
        Example:
            >>> DataPaths.macro('deposit_interest')
            Path('.../DATA/processed/macro/deposit_interest_rates.parquet')
        """
        indicator_map = {
            'deposit_interest': 'macro/deposit_interest_rates.parquet',
            'exchange_rates': 'macro/exchange_rates.parquet',
            'gov_bond_yields': 'macro/gov_bond_yields.parquet',
            'interest_rates': 'macro/interest_rates.parquet'
        }
        
        if indicator not in indicator_map:
            raise ValueError(
                f"Unknown macro indicator: '{indicator}'. "
                f"Valid options: {list(indicator_map.keys())}"
            )
            
        return get_data_path(f"DATA/processed/{indicator_map[indicator]}")
    
    # ============================================================================
    # FORECAST DATA
    # ============================================================================
    
    @staticmethod
    def forecast(source: Literal['bsc'] = 'bsc') -> Path:
        """
        Get forecast data path by source.
        
        Args:
            source: Forecast data source (currently only 'bsc')
            
        Returns:
            Path to forecast data file
            
        Raises:
            ValueError: If source is not recognized
        """
        if source == 'bsc':
            return get_data_path("DATA/processed/forecast/bsc/bsc_forecast_latest.json")
        else:
            raise ValueError(f"Unknown forecast source: '{source}'")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================
# These provide shorter syntax for common operations

def get_fundamental_path(entity_type: str) -> Path:
    """
    Shortcut function for fundamental data.
    
    Args:
        entity_type: 'bank', 'company', 'insurance', or 'security'
        
    Returns:
        Path to fundamental metrics file
        
    Example:
        >>> get_fundamental_path('company')
        Path('.../DATA/processed/fundamental/company/company_financial_metrics.parquet')
    """
    return DataPaths.fundamental(entity_type)


def get_valuation_path(metric: str) -> Path:
    """
    Shortcut function for valuation data.
    
    Args:
        metric: 'pe', 'pb', 'ev_ebitda', 'vnindex_pe', or 'sector_pe'
        
    Returns:
        Path to valuation file
    """
    return DataPaths.valuation(metric)


def get_technical_path(indicator: str) -> Path:
    """
    Shortcut function for technical data.
    
    Args:
        indicator: Technical indicator name
        
    Returns:
        Path to technical indicator file
    """
    return DataPaths.technical(indicator)


def get_macro_path(indicator: str) -> Path:
    """
    Shortcut function for macro data.
    
    Args:
        indicator: Macro indicator name ('deposit_interest', 'exchange_rates', 
                  'gov_bond_yields', 'interest_rates')
        
    Returns:
        Path to macro indicator file
    """
    return DataPaths.macro(indicator)


# ============================================================================
# PATH VALIDATION (Optional - for debugging)
# ============================================================================

def validate_all_paths() -> dict:
    """
    Validate that all configured paths exist.
    Useful for debugging and monitoring.
    
    Returns:
        Dictionary with validation results
    """
    results = {
        'fundamental': {},
        'valuation': {},
        'technical': {},
        'macro': {},
        'raw': {}
    }
    
    # Check fundamental paths
    for entity in ['bank', 'company', 'insurance', 'security']:
        path = DataPaths.fundamental(entity)
        results['fundamental'][entity] = path.exists()
    
    # Check valuation paths
    for metric in ['pe', 'pb', 'ev_ebitda']:
        path = DataPaths.valuation(metric)
        results['valuation'][metric] = path.exists()
    
    # Check technical paths (sample)
    for indicator in ['ma', 'rsi']:
        try:
            path = DataPaths.technical(indicator)
            results['technical'][indicator] = path.exists()
        except ValueError:
            results['technical'][indicator] = False
    
    # Check macro paths
    for indicator in ['deposit_interest', 'exchange_rates', 'gov_bond_yields', 'interest_rates']:
        try:
            path = DataPaths.macro(indicator)
            results['macro'][indicator] = path.exists()
        except ValueError:
            results['macro'][indicator] = False
    
    # Check raw data
    for entity in ['bank', 'company']:
        path = DataPaths.raw_fundamental(entity)
        results['raw'][entity] = path.exists()
    
    return results


if __name__ == "__main__":
    # Test module when run directly (for testing only)
    print("🧪 Testing DataPaths configuration...\n")
    
    print("📁 Fundamental paths:")
    for entity in ['bank', 'company', 'insurance', 'security']:
        try:
            path = DataPaths.fundamental(entity)
            exists = "✅" if path.exists() else "❌"
            print(f"  {exists} {entity}: {path}")
        except Exception as e:
            print(f"  ❌ {entity}: Error - {e}")
    
    print("\n💰 Valuation paths:")
    for metric in ['pe', 'pb', 'ev_ebitda']:
        try:
            path = DataPaths.valuation(metric)
            exists = "✅" if path.exists() else "❌"
            print(f"  {exists} {metric}: {path}")
        except Exception as e:
            print(f"  ❌ {metric}: Error - {e}")
    
    print("\n📊 Macro paths:")
    for indicator in ['deposit_interest', 'exchange_rates', 'gov_bond_yields', 'interest_rates']:
        try:
            path = DataPaths.macro(indicator)
            exists = "✅" if path.exists() else "❌"
            print(f"  {exists} {indicator}: {path}")
        except Exception as e:
            print(f"  ❌ {indicator}: Error - {e}")
    
    print("\n✅ DataPaths module test completed!")

