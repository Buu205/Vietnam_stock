#!/usr/bin/env python3
"""
Input Data Validator
====================

Validates raw input data before processing to ensure data quality.

Features:
- CSV schema validation
- Required columns checking
- Data type validation
- Business logic validation
- Missing data detection

Usage:
    from PROCESSORS.core.validators.input_validator import InputValidator

    validator = InputValidator()
    result = validator.validate_csv(csv_path, "COMPANY")

    if not result.is_valid:
        print(f"Validation failed: {result.errors}")
        raise ValueError("Invalid input data")

Author: Claude Code
Date: 2025-12-08
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Import BSC CSV adapter
try:
    from .bsc_csv_adapter import BSCCSVAdapter
    BSC_ADAPTER_AVAILABLE = True
except ImportError:
    BSC_ADAPTER_AVAILABLE = False
    logger.warning("BSC CSV Adapter not available")


@dataclass
class ValidationResult:
    """Result of data validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

    def __str__(self) -> str:
        if self.is_valid:
            status = "✅ VALID"
        else:
            status = "❌ INVALID"

        msg = [f"{status}"]
        if self.errors:
            msg.append(f"Errors ({len(self.errors)}):")
            for err in self.errors[:5]:  # Show first 5
                msg.append(f"  - {err}")
            if len(self.errors) > 5:
                msg.append(f"  ... and {len(self.errors) - 5} more")

        if self.warnings:
            msg.append(f"Warnings ({len(self.warnings)}):")
            for warn in self.warnings[:3]:  # Show first 3
                msg.append(f"  - {warn}")
            if len(self.warnings) > 3:
                msg.append(f"  ... and {len(self.warnings) - 3} more")

        return "\n".join(msg)


class InputValidator:
    """
    Validates raw input data before processing.

    This validator checks:
    1. File existence and accessibility
    2. Required columns presence
    3. Data types correctness
    4. Business logic constraints
    5. Missing/null values in critical columns
    """

    # Required columns for each entity type
    REQUIRED_COLUMNS = {
        "COMPANY": ["ticker", "year", "quarter", "lengthReport"],
        "BANK": ["ticker", "year", "quarter", "lengthReport"],
        "INSURANCE": ["ticker", "year", "quarter", "lengthReport"],
        "SECURITY": ["ticker", "year", "quarter", "lengthReport"],
    }

    # Critical columns that cannot have NaN
    CRITICAL_COLUMNS = {
        "COMPANY": ["ticker", "year", "quarter"],
        "BANK": ["ticker", "year", "quarter"],
        "INSURANCE": ["ticker", "year", "quarter"],
        "SECURITY": ["ticker", "year", "quarter"],
    }

    def __init__(self):
        """Initialize input validator"""
        logger.info("InputValidator initialized")

    def validate_csv(
        self,
        csv_path: Path,
        entity_type: str,
        check_business_logic: bool = True,
        auto_adapt_bsc: bool = True
    ) -> ValidationResult:
        """
        Validate CSV file for fundamental data.

        Args:
            csv_path: Path to CSV file
            entity_type: Entity type (COMPANY, BANK, INSURANCE, SECURITY)
            check_business_logic: Whether to check business logic constraints
            auto_adapt_bsc: Whether to automatically adapt BSC CSV format (default: True)

        Returns:
            ValidationResult with validation status

        Example:
            >>> validator = InputValidator()
            >>> result = validator.validate_csv(Path("company.csv"), "COMPANY")
            >>> if result.is_valid:
            ...     print("Data is valid!")
        """
        errors = []
        warnings = []

        # 1. File existence check
        if not csv_path.exists():
            errors.append(f"File not found: {csv_path}")
            return ValidationResult(False, errors, warnings)

        # 2. File accessibility check
        try:
            df = pd.read_csv(csv_path, low_memory=False)
        except Exception as e:
            errors.append(f"Cannot read CSV: {e}")
            return ValidationResult(False, errors, warnings)

        # 2.5. Auto-adapt BSC CSV format if needed
        if auto_adapt_bsc and BSC_ADAPTER_AVAILABLE:
            # Check if this looks like BSC CSV (has SECURITY_CODE instead of ticker)
            if 'SECURITY_CODE' in df.columns and 'ticker' not in df.columns:
                logger.info(f"Detected BSC CSV format, adapting...")
                adapter = BSCCSVAdapter()
                df = adapter.adapt(df)
                warnings.append("Auto-adapted from BSC CSV format")

        # 3. Empty file check
        if len(df) == 0:
            errors.append("CSV file is empty (0 rows)")
            return ValidationResult(False, errors, warnings)

        # 4. Entity type check
        if entity_type not in self.REQUIRED_COLUMNS:
            errors.append(f"Unknown entity type: {entity_type}")
            return ValidationResult(False, errors, warnings)

        # 5. Required columns check
        required_cols = self.REQUIRED_COLUMNS[entity_type]
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # 6. Critical columns NaN check
        critical_cols = self.CRITICAL_COLUMNS[entity_type]
        for col in critical_cols:
            if col in df.columns:
                nan_count = df[col].isna().sum()
                if nan_count > 0:
                    errors.append(
                        f"Critical column '{col}' has {nan_count} NaN values"
                    )

        # 7. Data type validation
        type_errors = self._validate_data_types(df, entity_type)
        errors.extend(type_errors)

        # 8. Business logic validation
        if check_business_logic:
            logic_errors, logic_warnings = self._validate_business_logic(df, entity_type)
            errors.extend(logic_errors)
            warnings.extend(logic_warnings)

        # 9. Duplicate check
        if 'ticker' in df.columns and 'year' in df.columns and 'quarter' in df.columns:
            duplicates = df.duplicated(subset=['ticker', 'year', 'quarter'], keep=False)
            if duplicates.any():
                dup_count = duplicates.sum()
                warnings.append(f"Found {dup_count} duplicate rows (ticker, year, quarter)")

        is_valid = len(errors) == 0

        if is_valid:
            logger.info(f"✅ CSV validation passed: {csv_path.name}")
        else:
            logger.error(f"❌ CSV validation failed: {csv_path.name}")
            for err in errors[:3]:
                logger.error(f"  - {err}")

        return ValidationResult(is_valid, errors, warnings)

    def _validate_data_types(self, df: pd.DataFrame, entity_type: str) -> List[str]:
        """Validate data types of key columns"""
        errors = []

        # Year should be numeric
        if 'year' in df.columns:
            try:
                pd.to_numeric(df['year'], errors='raise')
            except (ValueError, TypeError) as e:
                errors.append(f"Column 'year' contains non-numeric values: {e}")

        # Quarter should be 1, 2, 3, or 4
        if 'quarter' in df.columns:
            try:
                quarters = pd.to_numeric(df['quarter'], errors='coerce')
                invalid = ~quarters.isin([1, 2, 3, 4])
                if invalid.any():
                    errors.append(
                        f"Column 'quarter' has {invalid.sum()} invalid values "
                        "(must be 1, 2, 3, or 4)"
                    )
            except (ValueError, TypeError) as e:
                errors.append(f"Column 'quarter' contains non-numeric values: {e}")

        # Ticker should be string
        if 'ticker' in df.columns:
            if not df['ticker'].dtype == 'object':
                errors.append("Column 'ticker' should be string type")

        return errors

    def _validate_business_logic(
        self,
        df: pd.DataFrame,
        entity_type: str
    ) -> tuple[List[str], List[str]]:
        """Validate business logic constraints"""
        errors = []
        warnings = []

        # Year range validation
        if 'year' in df.columns:
            years = pd.to_numeric(df['year'], errors='coerce')
            min_year = years.min()
            max_year = years.max()

            if min_year < 2000:
                warnings.append(f"Data contains years before 2000 (min: {min_year})")

            if max_year > 2030:
                warnings.append(f"Data contains future years (max: {max_year})")

        # lengthReport validation (should be Q1, Q2, Q3, or YEAR)
        if 'lengthReport' in df.columns:
            valid_values = {'Q1', 'Q2', 'Q3', 'YEAR'}
            invalid = ~df['lengthReport'].isin(valid_values)
            if invalid.any():
                invalid_count = invalid.sum()
                warnings.append(
                    f"lengthReport has {invalid_count} invalid values "
                    f"(valid: {valid_values})"
                )

        # Ticker format validation (should be 3-4 uppercase letters)
        if 'ticker' in df.columns:
            invalid_tickers = df['ticker'].str.match(r'^[A-Z]{3,4}$', na=False) == False
            if invalid_tickers.any():
                invalid_count = invalid_tickers.sum()
                warnings.append(
                    f"Found {invalid_count} tickers with invalid format "
                    "(should be 3-4 uppercase letters)"
                )

        return errors, warnings

    def validate_parquet(
        self,
        parquet_path: Path,
        check_schema: bool = True
    ) -> ValidationResult:
        """
        Validate parquet file.

        Args:
            parquet_path: Path to parquet file
            check_schema: Whether to validate schema

        Returns:
            ValidationResult
        """
        errors = []
        warnings = []

        # 1. File existence
        if not parquet_path.exists():
            errors.append(f"File not found: {parquet_path}")
            return ValidationResult(False, errors, warnings)

        # 2. Read parquet
        try:
            df = pd.read_parquet(parquet_path)
        except Exception as e:
            errors.append(f"Cannot read parquet: {e}")
            return ValidationResult(False, errors, warnings)

        # 3. Empty check
        if len(df) == 0:
            warnings.append("Parquet file is empty (0 rows)")

        # 4. Schema validation
        if check_schema:
            # Check for basic columns
            expected_cols = ['ticker', 'year', 'quarter']
            missing = set(expected_cols) - set(df.columns)
            if missing:
                warnings.append(f"Missing expected columns: {missing}")

        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)

    def generate_report(self, result: ValidationResult) -> str:
        """Generate detailed validation report"""
        return str(result)


# Convenience function
def validate_csv(csv_path: Path, entity_type: str) -> ValidationResult:
    """Convenience function to validate CSV"""
    validator = InputValidator()
    return validator.validate_csv(csv_path, entity_type)


if __name__ == "__main__":
    # Demo usage
    import sys
    from pathlib import Path

    # Add project to path
    project_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(project_root))

    from PROCESSORS.core.config.paths import RAW_FUNDAMENTAL, PROJECT_ROOT

    print("=" * 60)
    print("INPUT VALIDATOR DEMO")
    print("=" * 60)

    # Test with actual CSV
    csv_dir = PROJECT_ROOT / "DATA" / "raw" / "fundamental" / "csv" / "Q3_2025"

    if csv_dir.exists():
        csv_files = list(csv_dir.glob("COMPANY_*.csv"))
        if csv_files:
            test_file = csv_files[0]
            print(f"\nTesting: {test_file.name}")
            print("-" * 60)

            validator = InputValidator()
            result = validator.validate_csv(test_file, "COMPANY")

            print(validator.generate_report(result))
        else:
            print("No CSV files found for testing")
    else:
        print(f"CSV directory not found: {csv_dir}")
