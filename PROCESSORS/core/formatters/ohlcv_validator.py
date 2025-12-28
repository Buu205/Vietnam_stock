#!/usr/bin/env python3
"""
OHLCV Data Validator - Data Quality Validation
===============================================

Implements validation rules from ohlcv_data_schema.json.
Use this to validate OHLCV data quality before processing.

Author: Claude Code
Date: 2025-12-07
"""

from pathlib import Path
import json
import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    row_index: Optional[int]
    symbol: Optional[str]
    field: str
    rule: str
    message: str
    severity: str = "WARNING"  # WARNING, ERROR, CRITICAL


@dataclass
class ValidationResult:
    """Result of validation"""
    is_valid: bool
    total_records: int
    errors: int = 0
    warnings: int = 0
    critical: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    def add_issue(self, issue: ValidationIssue):
        """Add an issue to the result"""
        self.issues.append(issue)
        if issue.severity == "ERROR":
            self.errors += 1
        elif issue.severity == "WARNING":
            self.warnings += 1
        elif issue.severity == "CRITICAL":
            self.critical += 1

    def summary(self) -> str:
        """Get summary string"""
        return (
            f"Total: {self.total_records} | "
            f"Errors: {self.errors} | "
            f"Warnings: {self.warnings} | "
            f"Critical: {self.critical}"
        )


class OHLCVValidator:
    """
    Validator for OHLCV data based on ohlcv_data_schema.json

    Usage:
        validator = OHLCVValidator()
        result = validator.validate_ohlcv_data(df)

        if not result.is_valid:
            for issue in result.issues[:10]:  # Show first 10 issues
                print(f"{issue.severity}: {issue.message}")
    """

    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize validator with schema

        Args:
            schema_path: Path to ohlcv_data_schema.json (auto-detects if None)
        """
        if schema_path is None:
            # Auto-detect schema path (canonical v4.0.0)
            root = Path(__file__).resolve().parents[3]
            schema_path = root / "config" / "schemas" / "data" / "ohlcv_data_schema.json"

        # Try to load schema, use defaults if not found
        if schema_path.exists():
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    self.schema = json.load(f)
                self.validation_rules = self.schema.get('validation_rules', {})
            except Exception as e:
                import logging
                logging.warning(f"Failed to load schema from {schema_path}: {e}. Using defaults.")
                self.schema = {}
                self.validation_rules = {}
        else:
            # Schema not found, use defaults
            self.schema = {}
            self.validation_rules = {}

    def validate_ohlcv_data(self, df: pd.DataFrame, strict: bool = False) -> ValidationResult:
        """
        Validate OHLCV DataFrame against all rules

        Args:
            df: DataFrame with OHLCV data
            strict: If True, warnings become errors

        Returns:
            ValidationResult with all issues found
        """
        result = ValidationResult(is_valid=True, total_records=len(df))

        # Run all validation rules
        self._validate_data_quality(df, result, strict)
        self._validate_business_rules(df, result, strict)
        self._validate_required_fields(df, result)

        # Set overall validity
        result.is_valid = (result.errors == 0 and result.critical == 0)

        return result

    def _validate_required_fields(self, df: pd.DataFrame, result: ValidationResult):
        """Check if required fields exist"""
        required = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']

        for field in required:
            if field not in df.columns:
                result.add_issue(ValidationIssue(
                    row_index=None,
                    symbol=None,
                    field=field,
                    rule="required_fields",
                    message=f"Required field '{field}' is missing",
                    severity="CRITICAL"
                ))

    def _validate_data_quality(self, df: pd.DataFrame, result: ValidationResult, strict: bool):
        """Validate data quality rules"""

        # Rule 1: High >= Low
        invalid_high_low = df[df['high'] < df['low']]
        for idx, row in invalid_high_low.iterrows():
            result.add_issue(ValidationIssue(
                row_index=idx,
                symbol=row.get('symbol'),
                field='high/low',
                rule='high_low_consistency',
                message=f"High ({row['high']}) < Low ({row['low']})",
                severity="ERROR"
            ))

        # Rule 2: Close between Low and High
        invalid_close = df[(df['close'] < df['low']) | (df['close'] > df['high'])]
        for idx, row in invalid_close.iterrows():
            result.add_issue(ValidationIssue(
                row_index=idx,
                symbol=row.get('symbol'),
                field='close',
                rule='close_range',
                message=f"Close ({row['close']}) not in range [{row['low']}, {row['high']}]",
                severity="ERROR"
            ))

        # Rule 3: Open between Low and High
        invalid_open = df[(df['open'] < df['low']) | (df['open'] > df['high'])]
        for idx, row in invalid_open.iterrows():
            severity = "ERROR" if strict else "WARNING"
            result.add_issue(ValidationIssue(
                row_index=idx,
                symbol=row.get('symbol'),
                field='open',
                rule='open_range',
                message=f"Open ({row['open']}) not in range [{row['low']}, {row['high']}]",
                severity=severity
            ))

        # Rule 4: Volume should be positive
        invalid_volume = df[df['volume'] < 0]
        for idx, row in invalid_volume.iterrows():
            result.add_issue(ValidationIssue(
                row_index=idx,
                symbol=row.get('symbol'),
                field='volume',
                rule='positive_volume',
                message=f"Volume is negative: {row['volume']}",
                severity="ERROR"
            ))

        # Rule 5: Prices should be positive
        for price_col in ['open', 'high', 'low', 'close']:
            if price_col in df.columns:
                negative_prices = df[df[price_col] <= 0]
                for idx, row in negative_prices.iterrows():
                    result.add_issue(ValidationIssue(
                        row_index=idx,
                        symbol=row.get('symbol'),
                        field=price_col,
                        rule='positive_price',
                        message=f"{price_col.title()} price is <= 0: {row[price_col]}",
                        severity="ERROR"
                    ))

    def _validate_business_rules(self, df: pd.DataFrame, result: ValidationResult, strict: bool):
        """Validate business logic rules"""

        # Rule: Price change % consistency (if price_change_pct exists)
        if 'price_change_pct' in df.columns and 'price_change' in df.columns and 'close' in df.columns:
            # Calculate expected percentage
            df_sorted = df.sort_values(['symbol', 'date'])
            df_sorted['prev_close'] = df_sorted.groupby('symbol')['close'].shift(1)

            # Where we have prev_close, check consistency
            has_prev = df_sorted[df_sorted['prev_close'].notna()].copy()
            if len(has_prev) > 0:
                has_prev['expected_pct'] = (has_prev['price_change'] / has_prev['prev_close']) * 100
                has_prev['pct_diff'] = abs(has_prev['price_change_pct'] - has_prev['expected_pct'])

                # Allow 0.1% tolerance
                inconsistent = has_prev[has_prev['pct_diff'] > 0.1]
                for idx, row in inconsistent.iterrows():
                    severity = "ERROR" if strict else "WARNING"
                    result.add_issue(ValidationIssue(
                        row_index=idx,
                        symbol=row.get('symbol'),
                        field='price_change_pct',
                        rule='pct_consistency',
                        message=f"Price change % mismatch: {row['price_change_pct']:.2f}% vs expected {row['expected_pct']:.2f}%",
                        severity=severity
                    ))

        # Rule: Turnover consistency (if exists)
        if 'turnover' in df.columns:
            df['expected_turnover'] = df['close'] * df['volume']
            df['turnover_diff_pct'] = abs((df['turnover'] - df['expected_turnover']) / df['expected_turnover']) * 100

            # Allow 1% tolerance
            inconsistent = df[df['turnover_diff_pct'] > 1.0]
            for idx, row in inconsistent.iterrows():
                severity = "ERROR" if strict else "WARNING"
                result.add_issue(ValidationIssue(
                    row_index=idx,
                    symbol=row.get('symbol'),
                    field='turnover',
                    rule='turnover_consistency',
                    message=f"Turnover mismatch: {row['turnover']:.0f} vs expected {row['expected_turnover']:.0f}",
                    severity=severity
                ))

    def generate_report(self, result: ValidationResult, max_issues: int = 50) -> str:
        """
        Generate text report of validation results

        Args:
            result: ValidationResult to report
            max_issues: Maximum number of issues to show

        Returns:
            Text report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("OHLCV DATA VALIDATION REPORT")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Total Records:     {result.total_records}")
        lines.append(f"Validation Status: {'✅ PASSED' if result.is_valid else '❌ FAILED'}")
        lines.append(f"Errors:           {result.errors}")
        lines.append(f"Warnings:         {result.warnings}")
        lines.append(f"Critical:         {result.critical}")
        lines.append("")

        if result.issues:
            lines.append(f"Issues Found (showing first {min(max_issues, len(result.issues))}):")
            lines.append("-" * 70)
            lines.append(f"{'Severity':<10} {'Symbol':<8} {'Field':<15} {'Message':<35}")
            lines.append("-" * 70)

            for issue in result.issues[:max_issues]:
                symbol = issue.symbol or "N/A"
                lines.append(f"{issue.severity:<10} {symbol:<8} {issue.field:<15} {issue.message[:35]}")

        lines.append("=" * 70)
        return "\n".join(lines)


# Example usage and demo
if __name__ == "__main__":
    print("=== OHLCV Validator Demo ===\n")

    validator = OHLCVValidator()

    # Create sample data with some issues
    sample_data = pd.DataFrame({
        'symbol': ['VCB', 'VCB', 'ACB', 'ACB'],
        'date': pd.to_datetime(['2025-12-01', '2025-12-02', '2025-12-01', '2025-12-02']),
        'open': [95000, 96000, 25000, 26000],
        'high': [97000, 97000, 26000, 27000],
        'low': [94000, 95500, 24500, 25500],
        'close': [96500, 96800, 25800, 26500],
        'volume': [1000000, 1200000, 500000, 600000],
    })

    # Add intentional errors for demo
    sample_data.loc[1, 'high'] = 94000  # High < Low error
    sample_data.loc[3, 'close'] = 28000  # Close > High error

    print("Sample data:")
    print(sample_data)
    print()

    # Validate
    result = validator.validate_ohlcv_data(sample_data)

    # Print report
    print(validator.generate_report(result))
    print()

    print(f"Validation summary: {result.summary()}")
    print(f"Is valid: {result.is_valid}")
