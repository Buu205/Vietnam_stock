#!/usr/bin/env python3
"""
NLP Formula Parser - Phân tích yêu cầu tính toán tài chính
===========================================================

Phân tích câu lệnh tiếng Việt/Anh để hiểu intent và trích xuất các thành phần công thức.

Ví dụ:
    - "tính SGA/Rev" → {operation: 'divide', numerator: 'SGA', denominator: 'Rev'}
    - "calculate ROE" → {operation: 'calculate', metric: 'ROE'}
    - "tính tổng lợi nhuận 4 quý gần nhất" → {operation: 'ttm_sum', metric: 'lợi nhuận'}

Author: AI Assistant
Date: 2025-12-12
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class FormulaIntent:
    """
    Cấu trúc intent sau khi phân tích câu lệnh

    Attributes:
        operation: Loại phép tính (divide, multiply, sum, ratio, growth, ttm, etc.)
        numerator: Tử số (cho phép chia/nhân)
        denominator: Mẫu số (cho phép chia)
        metric_name: Tên metric cần tính
        components: Danh sách components cần tính
        language: Ngôn ngữ input (vi/en)
        raw_input: Câu lệnh gốc từ user
    """
    operation: str
    numerator: Optional[str] = None
    denominator: Optional[str] = None
    metric_name: Optional[str] = None
    components: Optional[List[str]] = field(default_factory=list)
    language: str = 'vi'
    raw_input: str = ''


class NLPFormulaParser:
    """
    Parser cho câu lệnh tính toán tài chính bằng tiếng Việt/Anh

    Hỗ trợ các pattern:
    - "tính X/Y" → Ratio calculation
    - "calculate X" → Single metric
    - "tính tổng X" → Summation
    - "tính X + Y" → Addition
    - "tính tăng trưởng X" → Growth rate
    """

    # Từ khóa operation
    OPERATION_KEYWORDS = {
        'divide': ['/', 'chia', 'trên', 'to', 'ratio', 'tỷ lệ'],
        'sum': ['tổng', 'sum', 'total', 'cộng', '+'],
        'subtract': ['trừ', 'subtract', '-', 'hiệu'],
        'multiply': ['nhân', 'multiply', '*', 'x'],
        'growth': ['tăng trưởng', 'growth', 'gr', 'yoy', 'qoq'],
        'ttm': ['ttm', '4 quý', 'trailing twelve months', '12 tháng', 'trailing'],
        'margin': ['biên', 'margin', 'tỷ suất'],
        'ratio': ['ratio', 'tỷ số', 'hệ số']
    }

    # Synonyms cho các metrics phổ biến
    METRIC_SYNONYMS = {
        'revenue': ['doanh thu', 'revenue', 'rev', 'dt', 'doanh thu thuần'],
        'profit': ['lợi nhuận', 'profit', 'lợi nhuận sau thuế', 'npatmi', 'lnst'],
        'sga': ['sga', 'chi phí bán hàng', 'chi phí quản lý', 'selling and admin'],
        'cogs': ['giá vốn', 'cogs', 'cost of goods sold', 'gv'],
        'equity': ['vốn chủ sở hữu', 'equity', 'vcsh'],
        'assets': ['tài sản', 'assets', 'total assets', 'tổng tài sản'],
        'fcf': ['fcf', 'free cash flow', 'dòng tiền tự do'],
        'roe': ['roe', 'return on equity', 'tỷ suất sinh lời trên vốn'],
        'roa': ['roa', 'return on assets', 'tỷ suất sinh lời trên tài sản'],
        'nim': ['nim', 'net interest margin', 'biên lãi thuần'],
        'cir': ['cir', 'cost to income ratio', 'tỷ lệ chi phí'],
        'npl': ['npl', 'non performing loan', 'nợ xấu']
    }

    def parse(self, input_text: str) -> FormulaIntent:
        """
        Phân tích câu lệnh input để trích xuất intent

        Args:
            input_text: Câu lệnh tiếng Việt/Anh (e.g., "tính SGA/Rev")

        Returns:
            FormulaIntent object chứa parsed information

        Examples:
            >>> parser = NLPFormulaParser()
            >>> intent = parser.parse("tính SGA/Rev")
            >>> intent.operation
            'divide'
            >>> intent.numerator
            'SGA'
            >>> intent.denominator
            'Rev'
        """
        original_input = input_text
        input_text = input_text.lower().strip()

        # Detect language
        language = self._detect_language(input_text)

        # Try different parsing strategies
        intent = None

        # Strategy 1: Ratio/Division pattern (X/Y, X trên Y)
        intent = self._parse_ratio(input_text, language)
        if intent:
            intent.raw_input = original_input
            return intent

        # Strategy 2: Addition pattern (X + Y)
        intent = self._parse_addition(input_text, language)
        if intent:
            intent.raw_input = original_input
            return intent

        # Strategy 3: Direct formula pattern (CIS_10 + CIS_25)
        intent = self._parse_direct_formula(input_text, language)
        if intent:
            intent.raw_input = original_input
            return intent

        # Strategy 4: Growth rate
        intent = self._parse_growth(input_text, language)
        if intent:
            intent.raw_input = original_input
            return intent

        # Strategy 5: TTM calculation
        intent = self._parse_ttm(input_text, language)
        if intent:
            intent.raw_input = original_input
            return intent

        # Strategy 6: Single metric calculation
        intent = self._parse_single_metric(input_text, language)
        if intent:
            intent.raw_input = original_input
            return intent

        # Fallback: Return generic calculate intent
        return FormulaIntent(
            operation='calculate',
            metric_name=input_text,
            language=language,
            raw_input=original_input
        )

    def _detect_language(self, text: str) -> str:
        """Detect if input is Vietnamese or English"""
        vietnamese_chars = re.findall(
            r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]',
            text
        )
        return 'vi' if vietnamese_chars else 'en'

    def _parse_ratio(self, text: str, language: str) -> Optional[FormulaIntent]:
        """
        Parse ratio/division patterns

        Patterns:
        - "tính SGA/Rev"
        - "SGA trên doanh thu"
        - "calculate SGA to Revenue"
        """
        # Pattern 1: X/Y
        match = re.search(r'(\w+)\s*/\s*(\w+)', text)
        if match:
            return FormulaIntent(
                operation='divide',
                numerator=match.group(1).upper(),
                denominator=match.group(2).upper(),
                language=language
            )

        # Pattern 2: X trên Y
        match = re.search(r'(\w+)\s+(trên|to|over)\s+(\w+)', text)
        if match:
            return FormulaIntent(
                operation='divide',
                numerator=match.group(1).upper(),
                denominator=match.group(3).upper(),
                language=language
            )

        return None

    def _parse_addition(self, text: str, language: str) -> Optional[FormulaIntent]:
        """
        Parse addition patterns

        Patterns:
        - "tính X + Y"
        - "calculate sum of X and Y"
        """
        # Pattern: X + Y (can have multiple terms)
        match = re.findall(r'(\w+)\s*\+', text)
        if match:
            # Get the last term after the last +
            last_match = re.search(r'\+\s*(\w+)', text)
            if last_match:
                components = [m.upper() for m in match] + [last_match.group(1).upper()]
                return FormulaIntent(
                    operation='sum',
                    components=components,
                    language=language
                )

        return None

    def _parse_direct_formula(self, text: str, language: str) -> Optional[FormulaIntent]:
        """
        Parse direct formula with metric codes

        Patterns:
        - "(CIS_25 + CIS_26) / CIS_10"
        - "CIS_10 * 100"
        """
        # Check if text contains metric codes (e.g., CIS_10, BIS_22A)
        metric_codes = re.findall(r'[A-Z]{3}_\w+', text.upper())
        if not metric_codes or len(metric_codes) < 2:
            return None

        # Check for division
        if '/' in text:
            parts = text.split('/')
            numerator_codes = re.findall(r'[A-Z]{3}_\w+', parts[0].upper())
            denominator_codes = re.findall(r'[A-Z]{3}_\w+', parts[1].upper())

            if numerator_codes and denominator_codes:
                return FormulaIntent(
                    operation='divide',
                    components=metric_codes,
                    language=language
                )

        # Check for addition
        if '+' in text:
            return FormulaIntent(
                operation='sum',
                components=metric_codes,
                language=language
            )

        # Check for subtraction
        if '-' in text:
            return FormulaIntent(
                operation='subtract',
                components=metric_codes,
                language=language
            )

        # Check for multiplication
        if '*' in text or 'x' in text.lower():
            return FormulaIntent(
                operation='multiply',
                components=metric_codes,
                language=language
            )

        return None

    def _parse_single_metric(self, text: str, language: str) -> Optional[FormulaIntent]:
        """
        Parse single metric calculation

        Patterns:
        - "tính ROE"
        - "calculate net margin"
        """
        # Remove common prefixes
        text = re.sub(r'^(tính|calculate|compute)\s+', '', text)

        # Check if remaining text is a known metric
        for standard_name, synonyms in self.METRIC_SYNONYMS.items():
            if any(syn in text for syn in synonyms):
                return FormulaIntent(
                    operation='calculate',
                    metric_name=standard_name,
                    language=language
                )

        # Generic metric name
        if text:
            return FormulaIntent(
                operation='calculate',
                metric_name=text,
                language=language
            )

        return None

    def _parse_growth(self, text: str, language: str) -> Optional[FormulaIntent]:
        """Parse growth rate patterns"""
        growth_keywords = ['tăng trưởng', 'growth', 'gr', 'yoy', 'qoq']

        if any(kw in text for kw in growth_keywords):
            # Extract metric name
            for kw in growth_keywords:
                text = text.replace(kw, '').strip()

            # Remove common prefixes
            text = re.sub(r'^(tính|calculate|compute)\s+', '', text)

            return FormulaIntent(
                operation='growth',
                metric_name=text if text else 'value',
                language=language
            )

        return None

    def _parse_ttm(self, text: str, language: str) -> Optional[FormulaIntent]:
        """Parse TTM calculation patterns"""
        ttm_keywords = ['ttm', '4 quý', 'trailing', '12 tháng']

        if any(kw in text for kw in ttm_keywords):
            # Extract metric name
            for kw in ttm_keywords:
                text = text.replace(kw, '').strip()

            # Remove common prefixes
            text = re.sub(r'^(tính|calculate|compute)\s+', '', text)

            return FormulaIntent(
                operation='ttm',
                metric_name=text if text else 'value',
                language=language
            )

        return None


# Singleton instance for easy import
formula_parser = NLPFormulaParser()


if __name__ == "__main__":
    # Test cases
    parser = NLPFormulaParser()

    test_cases = [
        "tính SGA/Rev",
        "calculate ROE",
        "tính tổng lợi nhuận 4 quý",
        "CIS_25 + CIS_26",
        "(CIS_25 + CIS_26) / CIS_10",
        "tính tăng trưởng doanh thu",
        "calculate net margin"
    ]

    print("NLP Formula Parser Test Cases:")
    print("=" * 80)

    for test in test_cases:
        intent = parser.parse(test)
        print(f"\nInput: {test}")
        print(f"  Operation: {intent.operation}")
        print(f"  Language: {intent.language}")
        if intent.numerator:
            print(f"  Numerator: {intent.numerator}")
        if intent.denominator:
            print(f"  Denominator: {intent.denominator}")
        if intent.metric_name:
            print(f"  Metric: {intent.metric_name}")
        if intent.components:
            print(f"  Components: {intent.components}")
