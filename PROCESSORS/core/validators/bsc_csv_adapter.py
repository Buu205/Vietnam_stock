#!/usr/bin/env python3
"""
BSC CSV Format Adapter
======================

Adapter to convert BSC CSV format to standardized format for validation.

BSC CSV uses different column names:
- SECURITY_CODE → ticker
- REPORT_DATE → year, quarter (parsed)
- FREQ_CODE → lengthReport

Features:
- Column name mapping
- Date parsing (YYYY-MM-DD → year, quarter)
- Frequency code conversion (Q/Y → Q1/Q2/Q3/YEAR)
- Preserve original data

Usage:
    from PROCESSORS.core.validators.bsc_csv_adapter import BSCCSVAdapter

    adapter = BSCCSVAdapter()
    standardized_df = adapter.adapt(bsc_df)

    # Now can validate with InputValidator
    validator = InputValidator()
    result = validator.validate_csv_dataframe(standardized_df, "COMPANY")

Author: Claude Code
Date: 2025-12-08
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BSCCSVAdapter:
    """
    Adapter to convert BSC CSV format to standardized format.

    BSC CSV Structure:
    ------------------
    - SECURITY_CODE: Stock ticker (e.g., "ACB", "VCB")
    - REPORT_DATE: Report date (e.g., "2024-06-30")
    - FREQ_CODE: Frequency code ("Q" for quarterly, "Y" for yearly)
    - AUDITED: Audit status ("Y" or "N")
    - MONTH_IN_PERIOD: Number of months (3, 6, 9, 12)
    - CBS_*/CIS_*/BBS_*/etc.: Metric codes

    Standard Format:
    ---------------
    - ticker: Stock ticker
    - year: Year (int)
    - quarter: Quarter (int, 1-4)
    - lengthReport: Report type ("Q1", "Q2", "Q3", "YEAR")
    - ... (rest of columns unchanged)
    """

    # Column name mappings
    COLUMN_MAPPING = {
        "SECURITY_CODE": "ticker",
        "REPORT_DATE": "report_date",  # Will be parsed
        "FREQ_CODE": "freq_code",      # Will be converted
        "AUDITED": "audited",
        "MONTH_IN_PERIOD": "month_in_period"
    }

    # Frequency code to lengthReport mapping
    FREQ_CODE_MAPPING = {
        "Q": None,  # Depends on month_in_period
        "Y": "YEAR",
        "M": "Q1",  # Monthly treated as Q1
        "S": "Q2",  # Semi-annual (6 months)
    }

    def __init__(self):
        """Initialize BSC CSV adapter"""
        logger.info("BSCCSVAdapter initialized")

    def adapt(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adapt BSC CSV format to standardized format.

        Args:
            df: DataFrame in BSC CSV format

        Returns:
            DataFrame in standardized format

        Example:
            >>> adapter = BSCCSVAdapter()
            >>> bsc_df = pd.read_csv("COMPANY_BALANCE_SHEET.csv")
            >>> std_df = adapter.adapt(bsc_df)
            >>> print(std_df[['ticker', 'year', 'quarter', 'lengthReport']].head())
        """
        # Make a copy to avoid modifying original
        adapted_df = df.copy()

        # 1. Rename basic columns
        for bsc_col, std_col in self.COLUMN_MAPPING.items():
            if bsc_col in adapted_df.columns:
                adapted_df.rename(columns={bsc_col: std_col}, inplace=True)

        # 2. Parse report_date to year, quarter
        if 'report_date' in adapted_df.columns:
            year_quarter = adapted_df['report_date'].apply(self._parse_report_date)
            adapted_df['year'] = year_quarter.apply(lambda x: x[0] if x else None)
            adapted_df['quarter'] = year_quarter.apply(lambda x: x[1] if x else None)

        # 3. Convert freq_code to lengthReport
        if 'freq_code' in adapted_df.columns:
            adapted_df['lengthReport'] = adapted_df.apply(
                lambda row: self._convert_freq_code(
                    row.get('freq_code'),
                    row.get('month_in_period')
                ),
                axis=1
            )

        logger.info(f"Adapted {len(adapted_df)} rows from BSC CSV format")

        return adapted_df

    def _parse_report_date(self, date_str: str) -> Optional[Tuple[int, int]]:
        """
        Parse report date to (year, quarter).

        Args:
            date_str: Date string (e.g., "2024-06-30")

        Returns:
            (year, quarter) tuple or None if invalid

        Examples:
            "2024-03-31" → (2024, 1)
            "2024-06-30" → (2024, 2)
            "2024-09-30" → (2024, 3)
            "2024-12-31" → (2024, 4)
        """
        if pd.isna(date_str):
            return None

        try:
            date_obj = pd.to_datetime(date_str)
            year = date_obj.year
            month = date_obj.month

            # Determine quarter from month
            if month <= 3:
                quarter = 1
            elif month <= 6:
                quarter = 2
            elif month <= 9:
                quarter = 3
            else:
                quarter = 4

            return (year, quarter)

        except Exception as e:
            logger.warning(f"Could not parse date: {date_str} - {e}")
            return None

    def _convert_freq_code(
        self,
        freq_code: str,
        month_in_period: Optional[int]
    ) -> Optional[str]:
        """
        Convert BSC frequency code to lengthReport.

        Args:
            freq_code: Frequency code ("Q", "Y", "M")
            month_in_period: Number of months (3, 6, 9, 12)

        Returns:
            lengthReport value ("Q1", "Q2", "Q3", "YEAR")

        Logic:
            - Y → YEAR
            - Q + 3 months → Q1
            - Q + 6 months → Q2
            - Q + 9 months → Q3
            - Q + 12 months → YEAR (actually yearly)
            - M → Q1
        """
        if pd.isna(freq_code):
            return None

        freq_code = str(freq_code).upper().strip()

        # Direct mapping for Y, M, S
        if freq_code == "Y":
            return "YEAR"

        if freq_code == "M":
            return "Q1"

        if freq_code == "S":
            return "Q2"  # Semi-annual

        # Q requires month_in_period
        if freq_code == "Q":
            if pd.isna(month_in_period):
                return None

            month_in_period = int(month_in_period)

            if month_in_period == 0:
                # month_in_period = 0 might mean yearly
                return "YEAR"
            elif month_in_period == 3:
                return "Q1"
            elif month_in_period == 6:
                return "Q2"
            elif month_in_period == 9:
                return "Q3"
            elif month_in_period == 12:
                return "YEAR"
            else:
                logger.debug(f"Unusual month_in_period: {month_in_period}, defaulting to Q1")
                return "Q1"

        logger.debug(f"Unknown freq_code: {freq_code}, defaulting to None")
        return None

    def validate_adaptation(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Validate that adaptation was successful.

        Args:
            df: Adapted DataFrame

        Returns:
            Dictionary with validation statistics
        """
        stats = {
            "total_rows": len(df),
            "has_ticker": "ticker" in df.columns,
            "has_year": "year" in df.columns,
            "has_quarter": "quarter" in df.columns,
            "has_lengthReport": "lengthReport" in df.columns,
            "ticker_null_count": df["ticker"].isna().sum() if "ticker" in df.columns else None,
            "year_null_count": df["year"].isna().sum() if "year" in df.columns else None,
            "quarter_null_count": df["quarter"].isna().sum() if "quarter" in df.columns else None,
            "lengthReport_null_count": df["lengthReport"].isna().sum() if "lengthReport" in df.columns else None,
        }

        return stats

    def adapt_csv_file(self, csv_path: Path) -> pd.DataFrame:
        """
        Adapt BSC CSV file directly.

        Args:
            csv_path: Path to BSC CSV file

        Returns:
            Adapted DataFrame
        """
        df = pd.read_csv(csv_path, low_memory=False)
        adapted_df = self.adapt(df)

        # Validate
        stats = self.validate_adaptation(adapted_df)
        logger.info(f"Adaptation stats: {stats}")

        return adapted_df


# Convenience function
def adapt_bsc_csv(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience function to adapt BSC CSV"""
    adapter = BSCCSVAdapter()
    return adapter.adapt(df)


if __name__ == "__main__":
    # Demo usage
    import sys
    from pathlib import Path

    # Add project to path
    project_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(project_root))

    print("=" * 60)
    print("BSC CSV ADAPTER DEMO")
    print("=" * 60)

    # Test with actual CSV
    csv_dir = project_root / "DATA" / "raw" / "fundamental" / "csv" / "Q3_2025"

    if csv_dir.exists():
        csv_files = list(csv_dir.glob("COMPANY_BALANCE_SHEET.csv"))
        if csv_files:
            test_file = csv_files[0]
            print(f"\nTesting: {test_file.name}")
            print("-" * 60)

            adapter = BSCCSVAdapter()
            adapted_df = adapter.adapt_csv_file(test_file)

            print(f"\nAdapted columns:")
            print(adapted_df[['ticker', 'year', 'quarter', 'lengthReport']].head(10))

            print(f"\nValidation stats:")
            stats = adapter.validate_adaptation(adapted_df)
            for key, value in stats.items():
                print(f"  {key}: {value}")
        else:
            print("No CSV files found for testing")
    else:
        print(f"CSV directory not found: {csv_dir}")
