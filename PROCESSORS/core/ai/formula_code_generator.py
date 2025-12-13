#!/usr/bin/env python3
"""
Formula Code Generator - Tự động tạo code công thức tài chính
============================================================

Tự động generate Python code cho công thức tính toán tài chính dựa trên:
1. FormulaIntent từ NLPFormulaParser
2. MetricInfo từ MetricRegistryResolver
3. Code templates và coding standards

Author: AI Assistant
Date: 2025-12-12
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re

try:
    from .nlp_formula_parser import FormulaIntent
    from .metric_registry_resolver import MetricInfo
except ImportError:
    from PROCESSORS.core.ai.nlp_formula_parser import FormulaIntent
    from PROCESSORS.core.ai.metric_registry_resolver import MetricInfo


@dataclass
class GeneratedFormula:
    """
    Kết quả generate code công thức

    Attributes:
        function_name: Tên hàm (e.g., calculate_sga_to_revenue)
        function_code: Code Python đầy đủ của hàm
        docstring: Vietnamese docstring
        dependencies: Danh sách metric codes cần thiết
        entity_types: Danh sách entity types áp dụng
        formula_description: Mô tả công thức bằng tiếng Việt
    """
    function_name: str
    function_code: str
    docstring: str
    dependencies: List[str]
    entity_types: List[str]
    formula_description: str


class FormulaCodeGenerator:
    """
    Generator để tự động tạo Python code cho công thức tài chính

    Sử dụng templates và coding standards để generate code
    theo chuẩn của project.
    """

    # Template for basic formula function
    FUNCTION_TEMPLATE = '''def {function_name}(df: pd.DataFrame) -> pd.Series:
    """
    {docstring}

    Args:
        df: DataFrame chứa dữ liệu pivot với các metric codes làm columns

    Returns:
        Series chứa kết quả tính toán

    Dependencies:
        {dependencies}

    Entity Types:
        {entity_types}
    """
    {body}
'''

    # Safe divide template
    SAFE_DIVIDE_TEMPLATE = '''safe_divide(
        {numerator},
        {denominator}
    )'''

    def __init__(self):
        """Initialize code generator."""
        pass

    def generate_formula(
        self,
        intent: FormulaIntent,
        metrics: List[MetricInfo],
        entity_type: str,
        function_name: Optional[str] = None
    ) -> GeneratedFormula:
        """
        Generate Python code cho một công thức

        Args:
            intent: FormulaIntent từ NLPFormulaParser
            metrics: Danh sách MetricInfo từ MetricRegistryResolver
            entity_type: Loại thực thể (COMPANY, BANK, etc.)
            function_name: Tên hàm tùy chỉnh (optional)

        Returns:
            GeneratedFormula object chứa code đã generate

        Examples:
            >>> generator = FormulaCodeGenerator()
            >>> intent = FormulaIntent(operation='divide', numerator='SGA', denominator='Rev')
            >>> metrics = [metric1, metric2]
            >>> result = generator.generate_formula(intent, metrics, 'COMPANY')
            >>> print(result.function_code)
        """
        # Generate function name if not provided
        if not function_name:
            function_name = self._generate_function_name(intent, metrics)

        # Generate docstring
        docstring = self._generate_docstring(intent, metrics, entity_type)

        # Generate function body
        body = self._generate_body(intent, metrics)

        # Extract dependencies
        dependencies = [m.code for m in metrics]

        # Build formula description
        formula_desc = self._generate_formula_description(intent, metrics)

        # Format complete function code
        function_code = self.FUNCTION_TEMPLATE.format(
            function_name=function_name,
            docstring=docstring,
            dependencies=', '.join(dependencies),
            entity_types=entity_type,
            body=body
        )

        return GeneratedFormula(
            function_name=function_name,
            function_code=function_code,
            docstring=docstring,
            dependencies=dependencies,
            entity_types=[entity_type],
            formula_description=formula_desc
        )

    def _generate_function_name(
        self,
        intent: FormulaIntent,
        metrics: List[MetricInfo]
    ) -> str:
        """Generate function name based on intent and metrics."""
        if intent.metric_name:
            # Use metric name
            name = intent.metric_name.lower().replace(' ', '_')
            return f"calculate_{name}"

        if intent.operation == 'divide' and len(metrics) >= 2:
            # Create ratio name from numerator and denominator
            num_name = metrics[0].name_en.lower().replace(' ', '_')[:15]
            den_name = metrics[1].name_en.lower().replace(' ', '_')[:15]
            return f"calculate_{num_name}_to_{den_name}_ratio"

        if intent.operation == 'sum':
            # Sum operation
            return f"calculate_sum_{len(metrics)}_metrics"

        if intent.operation == 'growth':
            metric_name = metrics[0].name_en.lower().replace(' ', '_')[:20] if metrics else 'metric'
            return f"calculate_{metric_name}_growth"

        if intent.operation == 'ttm':
            metric_name = metrics[0].name_en.lower().replace(' ', '_')[:20] if metrics else 'metric'
            return f"calculate_{metric_name}_ttm"

        # Default
        return f"calculate_custom_metric"

    def _generate_docstring(
        self,
        intent: FormulaIntent,
        metrics: List[MetricInfo],
        entity_type: str
    ) -> str:
        """Generate Vietnamese docstring."""
        lines = []

        # Title based on operation
        if intent.operation == 'divide':
            lines.append(f"Tính tỷ lệ {metrics[0].name_vi if metrics else 'tử số'}")
            lines.append(f"trên {metrics[1].name_vi if len(metrics) > 1 else 'mẫu số'}")
        elif intent.operation == 'sum':
            lines.append("Tính tổng các chỉ tiêu:")
            for m in metrics:
                lines.append(f"  - {m.name_vi}")
        elif intent.operation == 'growth':
            lines.append(f"Tính tăng trưởng {metrics[0].name_vi if metrics else 'chỉ tiêu'}")
        elif intent.operation == 'ttm':
            lines.append(f"Tính TTM (4 quý) của {metrics[0].name_vi if metrics else 'chỉ tiêu'}")
        else:
            lines.append(f"Tính toán chỉ tiêu tùy chỉnh")

        lines.append("")
        lines.append(f"Áp dụng cho: {entity_type}")

        return "\n    ".join(lines)

    def _generate_body(
        self,
        intent: FormulaIntent,
        metrics: List[MetricInfo]
    ) -> str:
        """Generate function body code."""
        lines = []

        if intent.operation == 'divide':
            # Division with safe_divide
            if len(metrics) >= 2:
                numerator_code = self._get_metric_access_code(metrics[0].code)
                denominator_code = self._get_metric_access_code(metrics[1].code)

                safe_div = self.SAFE_DIVIDE_TEMPLATE.format(
                    numerator=numerator_code,
                    denominator=denominator_code
                )
                lines.append(f"    return {safe_div} * 100  # Convert to percentage")
            else:
                lines.append("    # Missing metrics for division")
                lines.append("    return pd.Series(dtype=float)")

        elif intent.operation == 'sum':
            # Addition
            if metrics:
                metric_codes = ' + '.join([self._get_metric_access_code(m.code) for m in metrics])
                lines.append(f"    return {metric_codes}")
            else:
                lines.append("    return pd.Series(dtype=float)")

        elif intent.operation == 'subtract':
            # Subtraction
            if len(metrics) >= 2:
                metric_codes = ' - '.join([self._get_metric_access_code(m.code) for m in metrics])
                lines.append(f"    return {metric_codes}")
            else:
                lines.append("    return pd.Series(dtype=float)")

        elif intent.operation == 'multiply':
            # Multiplication
            if metrics:
                metric_codes = ' * '.join([self._get_metric_access_code(m.code) for m in metrics])
                lines.append(f"    return {metric_codes}")
            else:
                lines.append("    return pd.Series(dtype=float)")

        elif intent.operation == 'growth':
            # YoY or QoQ growth
            if metrics:
                metric_code = self._get_metric_access_code(metrics[0].code)
                lines.append(f"    # Calculate YoY growth (this is a placeholder)")
                lines.append(f"    # Actual implementation needs period-over-period logic")
                lines.append(f"    return {metric_code}.pct_change(periods=4) * 100")
            else:
                lines.append("    return pd.Series(dtype=float)")

        elif intent.operation == 'ttm':
            # TTM sum
            if metrics:
                metric_code = self._get_metric_access_code(metrics[0].code)
                lines.append(f"    # Calculate TTM (4 quarters)")
                lines.append(f"    return {metric_code}.rolling(window=4).sum()")
            else:
                lines.append("    return pd.Series(dtype=float)")

        else:
            # Default
            lines.append("    # Custom calculation logic here")
            lines.append("    return pd.Series(dtype=float)")

        return '\n'.join(lines)

    def _get_metric_access_code(self, metric_code: str) -> str:
        """Generate code to access a metric from DataFrame."""
        return f"df['{metric_code}']"

    def _generate_formula_description(
        self,
        intent: FormulaIntent,
        metrics: List[MetricInfo]
    ) -> str:
        """Generate human-readable formula description."""
        if intent.operation == 'divide' and len(metrics) >= 2:
            return f"({metrics[0].code}) / ({metrics[1].code}) * 100"
        elif intent.operation == 'sum':
            codes = ' + '.join([m.code for m in metrics])
            return codes
        elif intent.operation == 'subtract' and len(metrics) >= 2:
            codes = ' - '.join([m.code for m in metrics])
            return codes
        elif intent.operation == 'multiply':
            codes = ' * '.join([m.code for m in metrics])
            return codes
        else:
            return f"{intent.operation}({', '.join([m.code for m in metrics])})"

    def generate_calculator_integration(
        self,
        formula: GeneratedFormula,
        entity_type: str
    ) -> str:
        """
        Generate code để integrate formula vào calculator

        Returns:
            Python code để add vào calculator's get_entity_specific_calculations()
        """
        code = f'''        # Auto-generated formula: {formula.formula_description}
        '{formula.function_name}': lambda df: {formula.function_name}(df),'''

        return code

    def generate_unit_test(
        self,
        formula: GeneratedFormula,
        entity_type: str
    ) -> str:
        """
        Generate unit test template cho formula

        Returns:
            Python test code
        """
        test_code = f'''def test_{formula.function_name}():
    """Test {formula.function_name}"""
    # Create sample data
    df = pd.DataFrame({{
        {', '.join([f"'{dep}': [100, 200, 300]" for dep in formula.dependencies])}
    }})

    # Calculate
    result = {formula.function_name}(df)

    # Assertions
    assert result is not None
    assert len(result) == 3
    # Add more specific assertions based on formula logic
'''
        return test_code


# Singleton instance
code_generator = FormulaCodeGenerator()


if __name__ == "__main__":
    # Test cases
    from nlp_formula_parser import NLPFormulaParser
    from metric_registry_resolver import MetricRegistryResolver

    generator = FormulaCodeGenerator()
    parser = NLPFormulaParser()
    resolver = MetricRegistryResolver()

    print("Formula Code Generator Test Cases:")
    print("=" * 80)

    # Test 1: Generate SGA/Revenue ratio
    print("\n1. Generate SGA/Revenue ratio formula:")
    intent = parser.parse("tính SGA/Rev")

    # Resolve metrics
    sga_metrics = resolver.resolve_metric_name("chi phí bán hàng", "COMPANY")
    rev_metrics = resolver.resolve_metric_name("doanh thu thuần", "COMPANY")

    if sga_metrics and rev_metrics:
        metrics = [sga_metrics[0], rev_metrics[0]]
        formula = generator.generate_formula(intent, metrics, "COMPANY")
        print(f"Function Name: {formula.function_name}")
        print(f"Formula: {formula.formula_description}")
        print(f"Dependencies: {formula.dependencies}")
        print("\nGenerated Code:")
        print(formula.function_code)
    else:
        print("Could not resolve metrics")

    # Test 2: Generate sum formula
    print("\n" + "=" * 80)
    print("\n2. Generate sum formula:")
    intent = parser.parse("CIS_25 + CIS_26")

    # Resolve specific codes
    metric1 = resolver.resolve_metric_code("CIS_25", "COMPANY")
    metric2 = resolver.resolve_metric_code("CIS_26", "COMPANY")

    if metric1 and metric2:
        metrics = [metric1, metric2]
        formula = generator.generate_formula(intent, metrics, "COMPANY", "calculate_total_sga")
        print(f"Function Name: {formula.function_name}")
        print(f"Formula: {formula.formula_description}")
        print("\nGenerated Code:")
        print(formula.function_code)
