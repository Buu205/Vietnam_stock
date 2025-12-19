"""
Configuration Module
====================

Centralized configuration for the bsc_mcp server.
All paths, constants, and settings are defined here.

Environment Variables:
---------------------
- DATA_ROOT: Path to DATA directory (default: auto-detect)
- CACHE_TTL: Cache time-to-live in seconds (default: 300)
"""

import os
from pathlib import Path
from typing import Optional


def find_project_root() -> Path:
    """
    Find the project root directory by looking for known markers.

    Returns:
        Path: The project root directory path
    """
    # Check environment variable first
    env_root = os.environ.get("PROJECT_ROOT")
    if env_root:
        return Path(env_root)

    current = Path(__file__).resolve()

    # Walk up the directory tree
    while current.parent != current:
        if current.name in ['Vietnam_dashboard', 'stock_dashboard']:
            return current
        # Also check for DATA directory as marker
        if (current / "DATA").exists() and (current / "PROCESSORS").exists():
            return current
        current = current.parent

    # Fallback: assume MCP_SERVER is in project root
    return Path(__file__).resolve().parent.parent.parent


class Config:
    """
    Configuration class for bsc_mcp server.

    Attributes:
        PROJECT_ROOT (Path): Root directory of the Vietnam_dashboard project
        DATA_ROOT (Path): Path to DATA directory containing parquet files
        CACHE_TTL (int): Cache time-to-live in seconds
    """

    def __init__(self):
        """Initialize configuration with auto-detected or environment paths."""
        # Project root (auto-detect)
        self.PROJECT_ROOT = find_project_root()

        # Data root (from env or default)
        data_root_env = os.environ.get("DATA_ROOT")
        if data_root_env:
            self.DATA_ROOT = Path(data_root_env)
        else:
            self.DATA_ROOT = self.PROJECT_ROOT / "DATA"

        # MCP Server root
        self.MCP_SERVER_ROOT = self.PROJECT_ROOT / "MCP_SERVER"

        # Cache settings
        self.CACHE_TTL = int(os.environ.get("CACHE_TTL", 300))  # 5 minutes

        # Validate paths exist
        self._validate_paths()

    def _validate_paths(self):
        """Validate that required directories exist."""
        if not self.DATA_ROOT.exists():
            raise FileNotFoundError(
                f"DATA directory not found: {self.DATA_ROOT}\n"
                f"Please ensure the DATA directory exists with parquet files.\n"
                f"You can set DATA_ROOT environment variable to override."
            )

    # =========================================================================
    # Parquet File Paths (relative to DATA_ROOT)
    # =========================================================================

    # Fundamental Data Paths
    COMPANY_FUNDAMENTALS_PATH = "processed/fundamental/company/company_financial_metrics.parquet"
    COMPANY_FULL_PATH = "processed/fundamental/company_full.parquet"
    BANK_FUNDAMENTALS_PATH = "processed/fundamental/bank/bank_financial_metrics.parquet"
    INSURANCE_FUNDAMENTALS_PATH = "processed/fundamental/insurance/insurance_financial_metrics.parquet"
    SECURITY_FUNDAMENTALS_PATH = "processed/fundamental/security/security_financial_metrics.parquet"

    # Valuation Data Paths
    PE_HISTORICAL_PATH = "processed/valuation/pe/historical/historical_pe.parquet"
    PB_HISTORICAL_PATH = "processed/valuation/pb/historical/historical_pb.parquet"
    PS_HISTORICAL_PATH = "processed/valuation/ps/historical/historical_ps.parquet"
    EV_EBITDA_HISTORICAL_PATH = "processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet"
    VNINDEX_VALUATION_PATH = "processed/valuation/vnindex/vnindex_valuation_refined.parquet"

    # Technical Data Paths
    TECHNICAL_BASIC_PATH = "processed/technical/basic_data.parquet"
    MARKET_BREADTH_PATH = "processed/technical/market_breadth/market_breadth_daily.parquet"
    SECTOR_BREADTH_PATH = "processed/technical/sector_breadth/sector_breadth_daily.parquet"
    MONEY_FLOW_PATH = "processed/technical/money_flow/individual_money_flow.parquet"
    SECTOR_MONEY_FLOW_1D_PATH = "processed/technical/money_flow/sector_money_flow_1d.parquet"
    VNINDEX_INDICATORS_PATH = "processed/technical/vnindex/vnindex_indicators.parquet"

    # Technical Alerts
    BREAKOUT_LATEST_PATH = "processed/technical/alerts/daily/breakout_latest.parquet"
    MA_CROSSOVER_LATEST_PATH = "processed/technical/alerts/daily/ma_crossover_latest.parquet"
    VOLUME_SPIKE_LATEST_PATH = "processed/technical/alerts/daily/volume_spike_latest.parquet"
    PATTERNS_LATEST_PATH = "processed/technical/alerts/daily/patterns_latest.parquet"
    COMBINED_ALERTS_PATH = "processed/technical/alerts/daily/combined_latest.parquet"

    # Forecast Data Paths
    BSC_INDIVIDUAL_PATH = "processed/forecast/bsc/bsc_individual.parquet"
    BSC_SECTOR_PATH = "processed/forecast/bsc/bsc_sector_valuation.parquet"
    BSC_COMBINED_PATH = "processed/forecast/bsc/bsc_combined.parquet"

    # Sector Analysis Paths
    SECTOR_VALUATION_PATH = "processed/sector/sector_valuation_metrics.parquet"
    SECTOR_FUNDAMENTALS_PATH = "processed/sector/sector_fundamental_metrics.parquet"

    # Macro Data Paths
    MACRO_COMMODITY_PATH = "processed/macro_commodity/macro_commodity_unified.parquet"

    # Metadata Paths
    SECTOR_REGISTRY_PATH = "metadata/sector_industry_registry.json"

    def get_parquet_path(self, name: str) -> Path:
        """
        Get full path to a parquet file by name.

        Args:
            name: Name of the data file (e.g., "company_fundamentals")

        Returns:
            Path: Full path to the parquet file

        Raises:
            ValueError: If name is not recognized
        """
        path_mapping = {
            # Fundamental
            "company_fundamentals": self.COMPANY_FUNDAMENTALS_PATH,
            "company_full": self.COMPANY_FULL_PATH,
            "bank_fundamentals": self.BANK_FUNDAMENTALS_PATH,
            "insurance_fundamentals": self.INSURANCE_FUNDAMENTALS_PATH,
            "security_fundamentals": self.SECURITY_FUNDAMENTALS_PATH,
            # Valuation
            "pe_historical": self.PE_HISTORICAL_PATH,
            "pb_historical": self.PB_HISTORICAL_PATH,
            "ps_historical": self.PS_HISTORICAL_PATH,
            "ev_ebitda_historical": self.EV_EBITDA_HISTORICAL_PATH,
            "vnindex_valuation": self.VNINDEX_VALUATION_PATH,
            # Technical
            "technical_basic": self.TECHNICAL_BASIC_PATH,
            "market_breadth": self.MARKET_BREADTH_PATH,
            "sector_breadth": self.SECTOR_BREADTH_PATH,
            "money_flow": self.MONEY_FLOW_PATH,
            "sector_money_flow": self.SECTOR_MONEY_FLOW_1D_PATH,
            "vnindex_indicators": self.VNINDEX_INDICATORS_PATH,
            # Alerts
            "breakout_alerts": self.BREAKOUT_LATEST_PATH,
            "ma_crossover_alerts": self.MA_CROSSOVER_LATEST_PATH,
            "volume_spike_alerts": self.VOLUME_SPIKE_LATEST_PATH,
            "pattern_alerts": self.PATTERNS_LATEST_PATH,
            "combined_alerts": self.COMBINED_ALERTS_PATH,
            # Forecast
            "bsc_individual": self.BSC_INDIVIDUAL_PATH,
            "bsc_sector": self.BSC_SECTOR_PATH,
            "bsc_combined": self.BSC_COMBINED_PATH,
            # Sector
            "sector_valuation": self.SECTOR_VALUATION_PATH,
            "sector_fundamentals": self.SECTOR_FUNDAMENTALS_PATH,
            # Macro
            "macro_commodity": self.MACRO_COMMODITY_PATH,
        }

        if name not in path_mapping:
            raise ValueError(
                f"Unknown data file: '{name}'\n"
                f"Available options: {list(path_mapping.keys())}"
            )

        return self.DATA_ROOT / path_mapping[name]


# Global config instance (singleton pattern)
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        Config: The global configuration instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config
