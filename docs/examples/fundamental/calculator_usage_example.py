#!/usr/bin/env python3
"""
Calculator Usage Example - How to Use Unified Calculator
=========================================================

This script demonstrates how to use the unified financial calculator
for different entity types (Company, Bank, Insurance, Security).

The calculator system has been consolidated into a single file:
    PROCESSORS/fundamental/calculators/run_all_calculators.py

Usage:
    # Run all calculators (command line)
    python3 PROCESSORS/fundamental/calculators/run_all_calculators.py

    # Run specific entity
    python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity bank
    python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity company

Author: Claude Code
Date: 2025-12-17 (Updated)
"""

import pandas as pd
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_load_calculated_data():
    """
    Example: Load pre-calculated metrics from parquet files.

    The recommended approach is to run the calculator once via command line,
    then load the results from parquet files for analysis.
    """
    base_path = Path(__file__).parent.parent.parent.parent

    # Output paths
    output_paths = {
        "company": base_path / "DATA/processed/fundamental/company/company_financial_metrics.parquet",
        "bank": base_path / "DATA/processed/fundamental/bank/bank_financial_metrics.parquet",
        "insurance": base_path / "DATA/processed/fundamental/insurance/insurance_financial_metrics.parquet",
        "security": base_path / "DATA/processed/fundamental/security/security_financial_metrics.parquet",
    }

    logger.info("Loading pre-calculated metrics...")

    for entity, path in output_paths.items():
        if path.exists():
            df = pd.read_parquet(path)
            logger.info(f"{entity.upper()}: {len(df)} rows, {len(df.columns)} columns")

            # Show sample metrics
            if entity == "bank":
                cols = ['symbol', 'year', 'quarter', 'nim_q', 'npl_ratio', 'casa_ratio', 'ldr_pure', 'ldr_regulated']
            elif entity == "company":
                cols = ['symbol', 'year', 'quarter', 'roe', 'roa', 'gross_margin', 'net_margin']
            else:
                cols = ['symbol', 'year', 'quarter']

            available_cols = [c for c in cols if c in df.columns]
            latest = df[df['quarter'] == df['quarter'].max()].head(5)
            logger.info(f"\nLatest {entity} data:\n{latest[available_cols].to_string()}\n")
        else:
            logger.warning(f"{entity.upper()}: File not found at {path}")


def example_run_calculator_programmatically():
    """
    Example: Run calculator programmatically (not recommended for production).

    For production use, prefer running via command line:
        python3 PROCESSORS/fundamental/calculators/run_all_calculators.py --entity bank
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

    from PROCESSORS.fundamental.calculators import BankCalculator

    logger.info("Running BankCalculator programmatically...")

    calc = BankCalculator()
    result = calc.run()

    logger.info(f"Calculated {len(result)} rows for BANK entity")

    # Show key metrics for top banks
    top_banks = ['ACB', 'VCB', 'TCB', 'MBB', 'VPB']
    latest = result[(result['year'] == result['year'].max()) &
                    (result['quarter'] == result['quarter'].max()) &
                    (result['symbol'].isin(top_banks))]

    cols = ['symbol', 'nim_q', 'npl_ratio', 'llcr', 'casa_ratio', 'ldr_pure', 'ldr_regulated']
    available_cols = [c for c in cols if c in latest.columns]

    logger.info(f"\nTop banks latest metrics:\n{latest[available_cols].to_string()}")


def main():
    """Main function to run examples."""
    logger.info("=" * 60)
    logger.info("EXAMPLE 1: Load pre-calculated metrics")
    logger.info("=" * 60)
    example_load_calculated_data()

    # Uncomment to run calculator programmatically
    # logger.info("=" * 60)
    # logger.info("EXAMPLE 2: Run calculator programmatically")
    # logger.info("=" * 60)
    # example_run_calculator_programmatically()


if __name__ == "__main__":
    main()
