#!/usr/bin/env python3
"""
Output Data Validator
=====================

Validates calculated metrics after processing to ensure data quality.

Features:
- Financial ratios sanity checks
- Range validation for metrics
- Infinite/NaN detection
- Business logic validation
- Statistical outlier detection

Usage:
    from PROCESSORS.core.validators.output_validator import OutputValidator

    validator = OutputValidator()
    result = validator.validate_metrics(df, "COMPANY")

    if not result.is_valid:
        print(f"Validation failed: {result.errors}")
        raise ValueError("Invalid calculated metrics")

Author: Claude Code
Date: 2025-12-08
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of metrics validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    stats: Dict[str, any] = None

    def __str__(self) -> str:
        if self.is_valid:
            status = "✅ VALID"
        else:
            status = "❌ INVALID"

        msg = [f"{status}"]

        if self.stats:
            msg.append(f"Stats:")
            msg.append(f"  - Total rows: {self.stats.get('total_rows', 'N/A')}")
            msg.append(f"  - Total columns: {self.stats.get('total_cols', 'N/A')}")
            msg.append(f"  - Metrics checked: {self.stats.get('metrics_checked', 'N/A')}")

        if self.errors:
            msg.append(f"\nErrors ({len(self.errors)}):")
            for err in self.errors[:5]:
                msg.append(f"  - {err}")
            if len(self.errors) > 5:
                msg.append(f"  ... and {len(self.errors) - 5} more")

        if self.warnings:
            msg.append(f"\nWarnings ({len(self.warnings)}):")
            for warn in self.warnings[:5]:
                msg.append(f"  - {warn}")
            if len(self.warnings) > 5:
                msg.append(f"  ... and {len(self.warnings) - 5} more")

        return "\n".join(msg)


class OutputValidator:
    """
    Validates calculated financial metrics.

    This validator checks:
    1. Infinite values detection
    2. NaN values in critical metrics
    3. Financial ratios within reasonable ranges
    4. Business logic constraints
    5. Statistical outliers
    """

    # Ratio validation ranges (min, max)
    RATIO_RANGES = {
        # Profitability ratios
        "roe": (-2.0, 2.0),  # ROE: -200% to 200%
        "roa": (-1.0, 1.0),  # ROA: -100% to 100%
        "gross_margin": (-1.0, 1.0),  # Gross margin: -100% to 100%
        "operating_margin": (-2.0, 2.0),  # Operating margin
        "net_margin": (-2.0, 2.0),  # Net margin

        # Bank-specific ratios
        "nim": (-0.2, 0.3),  # NIM: -20% to 30%
        "cir": (0.0, 3.0),  # CIR: 0% to 300%
        "npl_ratio": (0.0, 1.0),  # NPL ratio: 0% to 100%
        "loan_to_deposit": (0.0, 2.0),  # L/D ratio: 0% to 200%

        # Leverage ratios
        "debt_to_equity": (0.0, 20.0),  # D/E: 0 to 2000%
        "debt_to_assets": (0.0, 1.0),  # D/A: 0% to 100%

        # Liquidity ratios
        "current_ratio": (0.0, 20.0),  # Current ratio: 0 to 20
        "quick_ratio": (0.0, 20.0),  # Quick ratio: 0 to 20

        # Valuation ratios
        "pe_ratio": (-100.0, 1000.0),  # P/E: -100 to 1000
        "pb_ratio": (0.0, 100.0),  # P/B: 0 to 100
    }

    # Critical metrics that should not have NaN
    CRITICAL_METRICS = {
        "COMPANY": ["ticker", "year", "quarter", "revenue", "net_income"],
        "BANK": ["ticker", "year", "quarter", "net_interest_income", "net_income"],
        "INSURANCE": ["ticker", "year", "quarter", "gross_premium", "net_income"],
        "SECURITY": ["ticker", "year", "quarter", "revenue", "net_income"],
    }

    def __init__(self, strict_mode: bool = False):
        """
        Initialize output validator.

        Args:
            strict_mode: If True, warnings are treated as errors
        """
        self.strict_mode = strict_mode
        logger.info(f"OutputValidator initialized (strict_mode={strict_mode})")

    def validate_metrics(
        self,
        df: pd.DataFrame,
        entity_type: str,
        check_outliers: bool = True
    ) -> ValidationResult:
        """
        Validate calculated financial metrics.

        Args:
            df: DataFrame with calculated metrics
            entity_type: Entity type (COMPANY, BANK, INSURANCE, SECURITY)
            check_outliers: Whether to check for statistical outliers

        Returns:
            ValidationResult with validation status

        Example:
            >>> validator = OutputValidator()
            >>> result = validator.validate_metrics(metrics_df, "COMPANY")
            >>> if result.is_valid:
            ...     print("Metrics are valid!")
        """
        errors = []
        warnings = []
        stats = {
            "total_rows": len(df),
            "total_cols": len(df.columns),
            "metrics_checked": 0
        }

        # 1. Empty dataframe check
        if len(df) == 0:
            errors.append("DataFrame is empty (0 rows)")
            return ValidationResult(False, errors, warnings, stats)

        # 2. Entity type check
        if entity_type not in self.CRITICAL_METRICS:
            errors.append(f"Unknown entity type: {entity_type}")
            return ValidationResult(False, errors, warnings, stats)

        # 3. Infinite values check
        inf_errors = self._check_infinite_values(df)
        errors.extend(inf_errors)

        # 4. Critical metrics NaN check
        nan_errors = self._check_critical_nan(df, entity_type)
        errors.extend(nan_errors)

        # 5. Ratio ranges validation
        range_errors, range_warnings = self._validate_ratio_ranges(df)
        errors.extend(range_errors)
        warnings.extend(range_warnings)
        stats["metrics_checked"] = len(range_errors) + len(range_warnings)

        # 6. Business logic validation
        logic_errors, logic_warnings = self._validate_business_logic(df, entity_type)
        errors.extend(logic_errors)
        warnings.extend(logic_warnings)

        # 7. Statistical outliers
        if check_outliers:
            outlier_warnings = self._check_outliers(df)
            warnings.extend(outlier_warnings)

        # 8. Duplicate check
        dup_warnings = self._check_duplicates(df)
        warnings.extend(dup_warnings)

        # Strict mode: treat warnings as errors
        if self.strict_mode and warnings:
            errors.extend(warnings)
            warnings = []

        is_valid = len(errors) == 0

        if is_valid:
            logger.info(f"✅ Metrics validation passed ({len(df)} rows, {entity_type})")
        else:
            logger.error(f"❌ Metrics validation failed ({len(errors)} errors)")
            for err in errors[:3]:
                logger.error(f"  - {err}")

        return ValidationResult(is_valid, errors, warnings, stats)

    def _check_infinite_values(self, df: pd.DataFrame) -> List[str]:
        """Check for infinite values in numeric columns"""
        errors = []

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            inf_count = np.isinf(df[col]).sum()
            if inf_count > 0:
                errors.append(
                    f"Column '{col}' has {inf_count} infinite values"
                )

        return errors

    def _check_critical_nan(self, df: pd.DataFrame, entity_type: str) -> List[str]:
        """Check for NaN in critical metrics"""
        errors = []

        critical_metrics = self.CRITICAL_METRICS.get(entity_type, [])

        for metric in critical_metrics:
            if metric in df.columns:
                nan_count = df[metric].isna().sum()
                if nan_count > 0:
                    nan_pct = (nan_count / len(df)) * 100
                    errors.append(
                        f"Critical metric '{metric}' has {nan_count} NaN values "
                        f"({nan_pct:.1f}%)"
                    )

        return errors

    def _validate_ratio_ranges(
        self,
        df: pd.DataFrame
    ) -> Tuple[List[str], List[str]]:
        """Validate financial ratios are within reasonable ranges"""
        errors = []
        warnings = []

        for ratio_name, (min_val, max_val) in self.RATIO_RANGES.items():
            if ratio_name in df.columns:
                # Get non-NaN values
                values = df[ratio_name].dropna()

                if len(values) == 0:
                    continue

                # Check min/max
                out_of_range = (values < min_val) | (values > max_val)
                if out_of_range.any():
                    count = out_of_range.sum()
                    pct = (count / len(values)) * 100
                    min_found = values.min()
                    max_found = values.max()

                    msg = (
                        f"Ratio '{ratio_name}' has {count} values ({pct:.1f}%) "
                        f"out of range [{min_val}, {max_val}]. "
                        f"Found range: [{min_found:.2f}, {max_found:.2f}]"
                    )

                    # High percentage out of range = error
                    if pct > 10:
                        errors.append(msg)
                    else:
                        warnings.append(msg)

        return errors, warnings

    def _validate_business_logic(
        self,
        df: pd.DataFrame,
        entity_type: str
    ) -> Tuple[List[str], List[str]]:
        """Validate business logic constraints"""
        errors = []
        warnings = []

        # 1. Revenue should be >= 0 for most companies
        if 'revenue' in df.columns:
            negative_revenue = (df['revenue'] < 0).sum()
            if negative_revenue > 0:
                pct = (negative_revenue / len(df)) * 100
                if pct > 5:  # >5% is concerning
                    warnings.append(
                        f"{negative_revenue} rows ({pct:.1f}%) have negative revenue"
                    )

        # 2. Total assets should be > 0
        if 'total_assets' in df.columns:
            zero_or_neg_assets = (df['total_assets'] <= 0).sum()
            if zero_or_neg_assets > 0:
                errors.append(
                    f"{zero_or_neg_assets} rows have zero or negative total assets"
                )

        # 3. Equity should not be too negative
        if 'total_equity' in df.columns:
            very_negative_equity = (df['total_equity'] < -df['total_assets']).sum()
            if very_negative_equity > 0:
                warnings.append(
                    f"{very_negative_equity} rows have equity more negative than assets"
                )

        # 4. Bank-specific: NPL ratio validation
        if entity_type == "BANK" and 'npl_ratio' in df.columns:
            high_npl = (df['npl_ratio'] > 0.1).sum()  # >10% NPL
            if high_npl > 0:
                warnings.append(
                    f"{high_npl} banks have NPL ratio > 10%"
                )

        # 5. Year/quarter validation
        if 'year' in df.columns:
            current_year = 2025
            future_years = (df['year'] > current_year).sum()
            if future_years > 0:
                warnings.append(
                    f"{future_years} rows have year > {current_year}"
                )

        return errors, warnings

    def _check_outliers(self, df: pd.DataFrame) -> List[str]:
        """Check for statistical outliers using IQR method"""
        warnings = []

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            # Skip ID columns
            if col in ['year', 'quarter', 'ticker']:
                continue

            values = df[col].dropna()
            if len(values) < 10:  # Need enough data
                continue

            # IQR method
            Q1 = values.quantile(0.25)
            Q3 = values.quantile(0.75)
            IQR = Q3 - Q1

            if IQR == 0:  # Avoid division by zero
                continue

            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR

            outliers = ((values < lower_bound) | (values > upper_bound)).sum()
            if outliers > 0:
                pct = (outliers / len(values)) * 100
                if pct > 5:  # >5% outliers
                    warnings.append(
                        f"Column '{col}' has {outliers} outliers ({pct:.1f}%) "
                        f"[IQR bounds: {lower_bound:.2f}, {upper_bound:.2f}]"
                    )

        return warnings

    def _check_duplicates(self, df: pd.DataFrame) -> List[str]:
        """Check for duplicate records"""
        warnings = []

        if {'ticker', 'year', 'quarter'}.issubset(df.columns):
            duplicates = df.duplicated(subset=['ticker', 'year', 'quarter'], keep=False)
            if duplicates.any():
                dup_count = duplicates.sum()
                warnings.append(
                    f"Found {dup_count} duplicate rows (ticker, year, quarter)"
                )

        return warnings

    def generate_report(self, result: ValidationResult) -> str:
        """Generate detailed validation report"""
        return str(result)


# Convenience function
def validate_metrics(df: pd.DataFrame, entity_type: str) -> ValidationResult:
    """Convenience function to validate metrics"""
    validator = OutputValidator()
    return validator.validate_metrics(df, entity_type)


if __name__ == "__main__":
    # Demo usage
    import sys
    from pathlib import Path

    # Add project to path
    project_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(project_root))

    from PROCESSORS.core.config.paths import PROCESSED_FUNDAMENTAL

    print("=" * 60)
    print("OUTPUT VALIDATOR DEMO")
    print("=" * 60)

    # Test with actual parquet
    parquet_dir = project_root / "DATA" / "refined" / "fundamental" / "current"

    if parquet_dir.exists():
        parquet_files = list(parquet_dir.glob("company_full.parquet"))
        if parquet_files:
            test_file = parquet_files[0]
            print(f"\nTesting: {test_file.name}")
            print("-" * 60)

            df = pd.read_parquet(test_file)
            print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

            validator = OutputValidator()
            result = validator.validate_metrics(df, "COMPANY", check_outliers=False)

            print("\n" + validator.generate_report(result))
        else:
            print("No parquet files found for testing")
    else:
        print(f"Parquet directory not found: {parquet_dir}")
