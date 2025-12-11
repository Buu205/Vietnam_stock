#!/usr/bin/env python3
"""
CSV Data Loader
===============

Centralized CSV loading with BSC format support.

Features:
- Auto-detection of BSC CSV format
- Column standardization
- Error handling
- Caching support

Usage:
    from PROCESSORS.extractors.csv_loader import CSVLoader

    loader = CSVLoader()
    df = loader.load_fundamental_csv("COMPANY", quarter=3, year=2025)

Author: Claude Code
Date: 2025-12-08
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Import from validators
try:
    import sys
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))
    from PROCESSORS.core.validators.bsc_csv_adapter import BSCCSVAdapter
    from PROCESSORS.core.config.paths import PROJECT_ROOT
    BSC_ADAPTER_AVAILABLE = True
except ImportError:
    BSC_ADAPTER_AVAILABLE = False
    logger.warning("BSC CSV Adapter not available")


class CSVLoader:
    """
    Centralized CSV data loader with BSC format support.

    This loader:
    1. Locates CSV files in DATA/raw/
    2. Auto-detects and adapts BSC CSV format
    3. Returns standardized DataFrames
    4. Handles errors gracefully
    """

    # CSV file name mappings
    CSV_FILES = {
        "COMPANY": {
            "balance_sheet": "COMPANY_BALANCE_SHEET.csv",
            "income": "COMPANY_INCOME.csv",
            "cashflow": "COMPANY_CF_DIRECT.csv",
        },
        "BANK": {
            "balance_sheet": "BANK_BALANCE_SHEET.csv",
            "income": "BANK_INCOME.csv",
            "cashflow": "BANK_CF_DIRECT.csv",
        },
        "INSURANCE": {
            "balance_sheet": "INSURANCE_BALANCE_SHEET.csv",
            "income": "INSURANCE_INCOME.csv",
            "cashflow": "INSURANCE_CF_DIRECT.csv",
        },
        "SECURITY": {
            "balance_sheet": "SECURITY_BALANCE_SHEET.csv",
            "income": "SECURITY_INCOME.csv",
            "cashflow": "SECURITY_CF_DIRECT.csv",
        }
    }

    def __init__(self, data_root: Optional[Path] = None):
        """
        Initialize CSV loader.

        Args:
            data_root: Root data directory (default: PROJECT_ROOT/DATA)
        """
        if data_root is None:
            data_root = PROJECT_ROOT / "DATA"

        self.data_root = Path(data_root)
        self.raw_dir = self.data_root / "raw" / "fundamental" / "csv"

        if BSC_ADAPTER_AVAILABLE:
            self.bsc_adapter = BSCCSVAdapter()
        else:
            self.bsc_adapter = None

        logger.info(f"CSVLoader initialized (data_root={self.data_root})")

    def load_fundamental_csv(
        self,
        entity_type: str,
        statement_type: str = "balance_sheet",
        quarter: int = 3,
        year: int = 2025,
        auto_adapt: bool = True
    ) -> pd.DataFrame:
        """
        Load fundamental CSV file.

        Args:
            entity_type: Entity type (COMPANY, BANK, INSURANCE, SECURITY)
            statement_type: Statement type (balance_sheet, income, cashflow)
            quarter: Quarter number (1-4)
            year: Year
            auto_adapt: Whether to auto-adapt BSC CSV format

        Returns:
            DataFrame with standardized columns

        Example:
            >>> loader = CSVLoader()
            >>> df = loader.load_fundamental_csv("COMPANY", "balance_sheet", 3, 2025)
            >>> print(df[['ticker', 'year', 'quarter']].head())
        """
        # Get CSV file name
        if entity_type not in self.CSV_FILES:
            raise ValueError(f"Unknown entity type: {entity_type}")

        if statement_type not in self.CSV_FILES[entity_type]:
            raise ValueError(f"Unknown statement type: {statement_type}")

        csv_filename = self.CSV_FILES[entity_type][statement_type]

        # Construct path
        csv_dir = self.raw_dir / f"Q{quarter}_{year}"
        csv_path = csv_dir / csv_filename

        # Check file exists
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        # Load CSV
        logger.info(f"Loading: {csv_path}")
        df = pd.read_csv(csv_path, low_memory=False)

        # Auto-adapt BSC format
        if auto_adapt and self.bsc_adapter and 'SECURITY_CODE' in df.columns:
            logger.info("Detected BSC CSV format, adapting...")
            df = self.bsc_adapter.adapt(df)

        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")

        return df

    def load_all_statements(
        self,
        entity_type: str,
        quarter: int = 3,
        year: int = 2025
    ) -> Dict[str, pd.DataFrame]:
        """
        Load all statement types for an entity.

        Args:
            entity_type: Entity type
            quarter: Quarter number
            year: Year

        Returns:
            Dictionary with statement_type → DataFrame

        Example:
            >>> loader = CSVLoader()
            >>> statements = loader.load_all_statements("COMPANY", 3, 2025)
            >>> print(statements.keys())
            dict_keys(['balance_sheet', 'income', 'cashflow'])
        """
        statements = {}

        for statement_type in self.CSV_FILES[entity_type].keys():
            try:
                df = self.load_fundamental_csv(
                    entity_type,
                    statement_type,
                    quarter,
                    year
                )
                statements[statement_type] = df
            except FileNotFoundError:
                logger.warning(f"Skipping missing file: {statement_type}")

        return statements


# Convenience functions
def load_csv(entity_type: str, statement_type: str = "balance_sheet", quarter: int = 3, year: int = 2025) -> pd.DataFrame:
    """Convenience function to load CSV"""
    loader = CSVLoader()
    return loader.load_fundamental_csv(entity_type, statement_type, quarter, year)


if __name__ == "__main__":
    # Demo
    print("=" * 60)
    print("CSV LOADER DEMO")
    print("=" * 60)

    loader = CSVLoader()

    try:
        df = loader.load_fundamental_csv("COMPANY", "balance_sheet", 3, 2025)
        print(f"\n✅ Loaded {len(df)} rows")
        print(f"Columns: {list(df.columns[:10])}...")
        print(f"\nSample data:")
        print(df[['ticker', 'year', 'quarter', 'lengthReport']].head())
    except Exception as e:
        print(f"❌ Error: {e}")
