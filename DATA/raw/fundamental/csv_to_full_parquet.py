#!/usr/bin/env python3
"""
CSV to Full Parquet Converter
=============================

Converts raw CSV files (wide format) to long-format parquet files (like legacy full_database.parquet).

Input: DATA/raw/fundamental/csv/Q3_2025/*.csv (wide format with metric codes as columns)
Output: DATA/processed/fundamental/{entity}_full.parquet (long format with METRIC_CODE column)

Usage:
    python3 PROCESSORS/fundamental/csv_to_full_parquet.py

Author: Claude Code
Date: 2025-12-16
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "DATA" / "raw" / "fundamental" / "csv" / "Q3_2025"
OUTPUT_PATH = PROJECT_ROOT / "DATA" / "processed" / "fundamental"

# Entity configurations
ENTITY_CONFIGS = {
    'bank': {
        'prefix': 'BANK',
        'files': ['BALANCE_SHEET', 'INCOME', 'CF_DIRECT', 'CF_INDIRECT', 'NOTE'],
        'metric_prefixes': ['BBS', 'BIS', 'BCFD', 'BCFI', 'BNOT'],
    },
    'company': {
        'prefix': 'COMPANY',
        'files': ['BALANCE_SHEET', 'INCOME', 'CF_DIRECT', 'CF_INDIRECT', 'NOTE'],
        'metric_prefixes': ['CBS', 'CIS', 'CCFD', 'CCFI', 'CNOT'],
    },
    'insurance': {
        'prefix': 'INSURANCE',
        'files': ['BALANCE_SHEET', 'INCOME', 'CF_DIRECT', 'CF_INDIRECT', 'NOTE'],
        'metric_prefixes': ['IBS', 'IIS', 'ICFD', 'ICFI', 'INOT'],
    },
    'security': {
        'prefix': 'SECURITY',
        'files': ['BALANCE_SHEET', 'INCOME', 'CF_DIRECT', 'CF_INDIRECT', 'NOTE'],
        'metric_prefixes': ['SBS', 'SIS', 'SCFD', 'SCFI', 'SNOT'],
    },
}

# ID columns (columns that are NOT metric codes)
ID_COLUMNS = [
    'SECURITY_CODE', 'REPORT_DATE', 'YEAR', 'QUARTER',
    'REPORTED_DATE', 'FREQ_CODE', 'AUDITED', 'Unnamed: 0',
    'ICB_L2', 'ENTITY_TYPE', 'MONTH_IN_PERIOD'
]


def load_csv_file(filepath: Path) -> pd.DataFrame:
    """Load a CSV file with proper dtype handling."""
    try:
        df = pd.read_csv(filepath, low_memory=False)

        # Drop unnamed columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        return df
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return pd.DataFrame()


def wide_to_long(df: pd.DataFrame, metric_prefixes: List[str]) -> pd.DataFrame:
    """
    Convert wide-format DataFrame to long-format.

    Wide format: Each metric is a column (CBS_100, CBS_110, etc.)
    Long format: METRIC_CODE column with values in METRIC_VALUE column
    """
    if df.empty:
        return df

    # Identify ID columns (present in dataframe)
    id_cols = [c for c in ID_COLUMNS if c in df.columns]

    # Identify metric columns (those starting with metric prefixes)
    metric_cols = []
    for col in df.columns:
        if col not in id_cols:
            # Check if it starts with any of the metric prefixes
            for prefix in metric_prefixes:
                if col.startswith(prefix):
                    metric_cols.append(col)
                    break

    if not metric_cols:
        logger.warning(f"No metric columns found for prefixes: {metric_prefixes}")
        return pd.DataFrame()

    logger.info(f"Found {len(metric_cols)} metric columns, {len(id_cols)} ID columns")

    # Melt wide to long
    df_long = df.melt(
        id_vars=id_cols,
        value_vars=metric_cols,
        var_name='METRIC_CODE',
        value_name='METRIC_VALUE'
    )

    # Drop null values
    df_long = df_long.dropna(subset=['METRIC_VALUE'])

    # Ensure proper types
    df_long['METRIC_VALUE'] = pd.to_numeric(df_long['METRIC_VALUE'], errors='coerce')

    return df_long


def process_entity(entity_type: str, config: Dict) -> pd.DataFrame:
    """Process all files for a single entity type."""
    logger.info(f"{'='*60}")
    logger.info(f"Processing {entity_type.upper()}")
    logger.info(f"{'='*60}")

    all_data = []
    prefix = config['prefix']
    metric_prefixes = config['metric_prefixes']

    for file_type in config['files']:
        filename = f"{prefix}_{file_type}.csv"
        filepath = CSV_PATH / filename

        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            continue

        logger.info(f"Loading {filename}...")
        df = load_csv_file(filepath)

        if df.empty:
            continue

        logger.info(f"  Loaded {len(df):,} rows, {len(df.columns)} columns")

        # Convert to long format
        df_long = wide_to_long(df, metric_prefixes)

        if not df_long.empty:
            # Add metadata
            df_long['ENTITY_TYPE'] = entity_type.upper()
            all_data.append(df_long)
            logger.info(f"  Converted to {len(df_long):,} long-format rows")

    if not all_data:
        logger.warning(f"No data processed for {entity_type}")
        return pd.DataFrame()

    # Combine all files
    combined = pd.concat(all_data, ignore_index=True)

    # Remove duplicates (same ticker/date/metric_code)
    key_cols = ['SECURITY_CODE', 'REPORT_DATE', 'FREQ_CODE', 'METRIC_CODE']
    available_keys = [c for c in key_cols if c in combined.columns]

    before_dedup = len(combined)
    combined = combined.drop_duplicates(subset=available_keys, keep='first')
    after_dedup = len(combined)

    if before_dedup != after_dedup:
        logger.info(f"Removed {before_dedup - after_dedup:,} duplicates")

    logger.info(f"Total {entity_type}: {len(combined):,} rows")

    return combined


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns like YEAR, QUARTER from REPORT_DATE."""
    if 'REPORT_DATE' in df.columns:
        df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])

        if 'YEAR' not in df.columns:
            df['YEAR'] = df['REPORT_DATE'].dt.year

        if 'QUARTER' not in df.columns:
            df['QUARTER'] = df['REPORT_DATE'].dt.quarter

    # Clean ticker codes (remove leading/trailing spaces and tabs)
    if 'SECURITY_CODE' in df.columns:
        df['SECURITY_CODE'] = df['SECURITY_CODE'].str.strip()

    return df


def main():
    """Main execution function."""
    logger.info("="*60)
    logger.info("CSV to Full Parquet Converter")
    logger.info("="*60)

    if not CSV_PATH.exists():
        logger.error(f"CSV path not found: {CSV_PATH}")
        return

    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    total_rows = 0
    results = {}

    for entity_type, config in ENTITY_CONFIGS.items():
        df = process_entity(entity_type, config)

        if df.empty:
            continue

        # Add derived columns
        df = add_derived_columns(df)

        # Save to parquet
        output_file = OUTPUT_PATH / f"{entity_type}_full.parquet"
        df.to_parquet(output_file, index=False)

        logger.info(f"Saved: {output_file}")
        logger.info(f"  Rows: {len(df):,}")
        logger.info(f"  Tickers: {df['SECURITY_CODE'].nunique()}")
        logger.info(f"  Metrics: {df['METRIC_CODE'].nunique()}")

        total_rows += len(df)
        results[entity_type] = len(df)

    # Summary
    logger.info("")
    logger.info("="*60)
    logger.info("SUMMARY")
    logger.info("="*60)
    for entity, rows in results.items():
        logger.info(f"  {entity.upper()}: {rows:,} rows")
    logger.info(f"  TOTAL: {total_rows:,} rows")
    logger.info("="*60)


if __name__ == "__main__":
    main()
