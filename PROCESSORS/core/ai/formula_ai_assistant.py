#!/usr/bin/env python3
"""
Formula AI Assistant - Trợ lý AI tự động tạo công thức tài chính
================================================================

Orchestrator kết nối tất cả AI components để tạo công thức tự động:
1. NLPFormulaParser - Phân tích intent
2. MetricRegistryResolver - Tìm metric codes
3. FormulaCodeGenerator - Generate Python code

Author: AI Assistant
Date: 2025-12-12
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from .nlp_formula_parser import NLPFormulaParser, FormulaIntent, formula_parser
    from .metric_registry_resolver import MetricRegistryResolver, MetricInfo, metric_resolver
    from .formula_code_generator import FormulaCodeGenerator, GeneratedFormula, code_generator
except ImportError:
    from PROCESSORS.core.ai.nlp_formula_parser import NLPFormulaParser, FormulaIntent, formula_parser
    from PROCESSORS.core.ai.metric_registry_resolver import MetricRegistryResolver, MetricInfo, metric_resolver
    from PROCESSORS.core.ai.formula_code_generator import FormulaCodeGenerator, GeneratedFormula, code_generator


@dataclass
class FormulaGenerationResult:
    """
    Kết quả quá trình tạo công thức

    Attributes:
        success: Thành công hay không
        formula: GeneratedFormula object (nếu thành công)
        error_message: Thông báo lỗi (nếu thất bại)
        intent: FormulaIntent đã phân tích
        metrics: Danh sách MetricInfo đã tìm được
        suggestions: Gợi ý nếu không tìm được metric
    """
    success: bool
    formula: Optional[GeneratedFormula] = None
    error_message: Optional[str] = None
    intent: Optional[FormulaIntent] = None
    metrics: Optional[List[MetricInfo]] = None
    suggestions: Optional[List[str]] = None


class FormulaAIAssistant:
    """
    AI Assistant cho việc tạo công thức tài chính tự động

    Workflow:
    1. User nhập câu lệnh (Vietnamese/English)
    2. Parser phân tích intent
    3. Resolver tìm metric codes
    4. Generator tạo Python code
    5. Return complete formula code

    Examples:
        >>> assistant = FormulaAIAssistant()
        >>> result = assistant.generate_formula("tính SGA/Rev", "COMPANY")
        >>> if result.success:
        ...     print(result.formula.function_code)
    """

    def __init__(self):
        """Initialize AI Assistant với tất cả components."""
        self.parser = formula_parser
        self.resolver = metric_resolver
        self.generator = code_generator

    def generate_formula(
        self,
        user_input: str,
        entity_type: str,
        function_name: Optional[str] = None
    ) -> FormulaGenerationResult:
        """
        Tạo công thức từ câu lệnh user

        Args:
            user_input: Câu lệnh tiếng Việt/Anh (e.g., "tính SGA/Rev")
            entity_type: Loại thực thể (COMPANY, BANK, etc.)
            function_name: Tên hàm tùy chỉnh (optional)

        Returns:
            FormulaGenerationResult chứa formula code hoặc error

        Examples:
            >>> assistant = FormulaAIAssistant()
            >>> result = assistant.generate_formula("tính ROE", "COMPANY")
            >>> print(result.formula.function_code)
        """
        try:
            # Step 1: Parse intent
            intent = self.parser.parse(user_input)

            # Step 2: Resolve metrics
            metrics = self._resolve_metrics(intent, entity_type)

            if not metrics:
                return FormulaGenerationResult(
                    success=False,
                    error_message=f"Không tìm thấy metrics cho: {user_input}",
                    intent=intent,
                    metrics=[],
                    suggestions=self._get_suggestions(intent, entity_type)
                )

            # Step 3: Generate formula code
            formula = self.generator.generate_formula(
                intent,
                metrics,
                entity_type,
                function_name
            )

            return FormulaGenerationResult(
                success=True,
                formula=formula,
                intent=intent,
                metrics=metrics
            )

        except Exception as e:
            return FormulaGenerationResult(
                success=False,
                error_message=f"Error: {str(e)}",
                intent=None,
                metrics=None
            )

    def _resolve_metrics(
        self,
        intent: FormulaIntent,
        entity_type: str
    ) -> List[MetricInfo]:
        """
        Resolve metrics từ FormulaIntent

        Args:
            intent: FormulaIntent từ parser
            entity_type: Loại thực thể

        Returns:
            Danh sách MetricInfo
        """
        metrics = []

        # Case 1: Direct metric codes in components (e.g., "CIS_25 + CIS_26")
        if intent.components:
            for component in intent.components:
                metric = self.resolver.resolve_metric_code(component, entity_type)
                if metric:
                    metrics.append(metric)

        # Case 2: Numerator/Denominator (ratio calculation)
        elif intent.numerator and intent.denominator:
            # Try to resolve as metric codes first
            num_metric = self.resolver.resolve_metric_code(intent.numerator, entity_type)
            if not num_metric:
                # Try as metric name
                num_results = self.resolver.resolve_metric_name(
                    intent.numerator,
                    entity_type,
                    intent.language
                )
                if num_results:
                    num_metric = num_results[0]

            den_metric = self.resolver.resolve_metric_code(intent.denominator, entity_type)
            if not den_metric:
                # Try as metric name
                den_results = self.resolver.resolve_metric_name(
                    intent.denominator,
                    entity_type,
                    intent.language
                )
                if den_results:
                    den_metric = den_results[0]

            if num_metric and den_metric:
                metrics = [num_metric, den_metric]

        # Case 3: Single metric name
        elif intent.metric_name:
            results = self.resolver.resolve_metric_name(
                intent.metric_name,
                entity_type,
                intent.language
            )
            if results:
                metrics = results[:1]  # Take first match

        return metrics

    def _get_suggestions(
        self,
        intent: FormulaIntent,
        entity_type: str
    ) -> List[str]:
        """
        Đưa ra gợi ý khi không tìm được metric

        Args:
            intent: FormulaIntent
            entity_type: Loại thực thể

        Returns:
            Danh sách gợi ý
        """
        suggestions = []

        # Suggest based on operation
        if intent.operation == 'divide':
            suggestions.append("Thử sử dụng metric codes: 'CIS_25 / CIS_10'")
            suggestions.append("Hoặc tên đầy đủ: 'chi phí bán hàng / doanh thu thuần'")

        elif intent.operation == 'sum':
            suggestions.append("Thử sử dụng metric codes: 'CIS_25 + CIS_26'")

        # Search for similar metrics
        if intent.metric_name:
            keywords = intent.metric_name.split()
            if keywords:
                results = self.resolver.search_by_keywords(
                    keywords[:2],  # Use first 2 keywords
                    entity_type,
                    intent.language
                )
                if results:
                    suggestions.append("Có thể bạn đang tìm:")
                    for r in results[:5]:
                        suggestions.append(f"  - {r.code}: {r.name_vi}")

        return suggestions

    def generate_formula_from_codes(
        self,
        metric_codes: List[str],
        operation: str,
        entity_type: str,
        function_name: Optional[str] = None
    ) -> FormulaGenerationResult:
        """
        Tạo công thức trực tiếp từ metric codes

        Args:
            metric_codes: Danh sách metric codes (e.g., ['CIS_25', 'CIS_10'])
            operation: Operation type ('divide', 'sum', etc.)
            entity_type: Loại thực thể
            function_name: Tên hàm tùy chỉnh (optional)

        Returns:
            FormulaGenerationResult

        Examples:
            >>> assistant = FormulaAIAssistant()
            >>> result = assistant.generate_formula_from_codes(
            ...     ['CIS_25', 'CIS_10'],
            ...     'divide',
            ...     'COMPANY',
            ...     'calculate_sga_to_revenue'
            ... )
        """
        try:
            # Create intent
            intent = FormulaIntent(
                operation=operation,
                components=metric_codes
            )

            # Resolve metrics
            metrics = []
            for code in metric_codes:
                metric = self.resolver.resolve_metric_code(code, entity_type)
                if metric:
                    metrics.append(metric)

            if len(metrics) != len(metric_codes):
                missing = set(metric_codes) - set([m.code for m in metrics])
                return FormulaGenerationResult(
                    success=False,
                    error_message=f"Metric codes không tồn tại: {missing}",
                    intent=intent,
                    metrics=metrics
                )

            # Generate formula
            formula = self.generator.generate_formula(
                intent,
                metrics,
                entity_type,
                function_name
            )

            return FormulaGenerationResult(
                success=True,
                formula=formula,
                intent=intent,
                metrics=metrics
            )

        except Exception as e:
            return FormulaGenerationResult(
                success=False,
                error_message=f"Error: {str(e)}",
                intent=None,
                metrics=None
            )

    def validate_and_preview(
        self,
        user_input: str,
        entity_type: str
    ) -> Dict:
        """
        Validate và preview công thức trước khi generate

        Args:
            user_input: Câu lệnh user
            entity_type: Loại thực thể

        Returns:
            Dictionary với preview information
        """
        # Parse intent
        intent = self.parser.parse(user_input)

        # Resolve metrics
        metrics = self._resolve_metrics(intent, entity_type)

        return {
            'intent': {
                'operation': intent.operation,
                'language': intent.language,
                'raw_input': intent.raw_input
            },
            'metrics': [
                {
                    'code': m.code,
                    'name_vi': m.name_vi,
                    'name_en': m.name_en,
                    'category': m.category
                }
                for m in metrics
            ] if metrics else [],
            'can_generate': len(metrics) > 0,
            'suggestions': self._get_suggestions(intent, entity_type) if not metrics else []
        }


# Singleton instance
ai_assistant = FormulaAIAssistant()


if __name__ == "__main__":
    # Test cases
    print("Formula AI Assistant Test Cases:")
    print("=" * 80)

    assistant = FormulaAIAssistant()

    # Test 1: Simple ratio
    print("\n1. Test: 'tính SGA/Rev' for COMPANY")
    result = assistant.generate_formula("tính SGA/Rev", "COMPANY")
    if result.success:
        print(f"✅ Success!")
        print(f"Function: {result.formula.function_name}")
        print(f"Formula: {result.formula.formula_description}")
        print(f"Dependencies: {result.formula.dependencies}")
        print("\nGenerated Code (first 300 chars):")
        print(result.formula.function_code[:300] + "...")
    else:
        print(f"❌ Failed: {result.error_message}")
        if result.suggestions:
            print("Suggestions:")
            for s in result.suggestions:
                print(f"  {s}")

    # Test 2: Direct metric codes
    print("\n" + "=" * 80)
    print("\n2. Test: '(CIS_25 + CIS_26) / CIS_10' for COMPANY")
    result = assistant.generate_formula("(CIS_25 + CIS_26) / CIS_10", "COMPANY")
    if result.success:
        print(f"✅ Success!")
        print(f"Function: {result.formula.function_name}")
        print(f"Dependencies: {result.formula.dependencies}")
    else:
        print(f"❌ Failed: {result.error_message}")

    # Test 3: Validate and preview
    print("\n" + "=" * 80)
    print("\n3. Test: Validate và preview 'tính ROE'")
    preview = assistant.validate_and_preview("tính ROE", "COMPANY")
    print(f"Intent: {preview['intent']}")
    print(f"Can generate: {preview['can_generate']}")
    print(f"Metrics found: {len(preview['metrics'])}")
    if preview['metrics']:
        for m in preview['metrics']:
            print(f"  - {m['code']}: {m['name_vi']}")

    # Test 4: Generate from codes directly
    print("\n" + "=" * 80)
    print("\n4. Test: Generate from codes ['CIS_10', 'CIS_25']")
    result = assistant.generate_formula_from_codes(
        ['CIS_25', 'CIS_10'],
        'divide',
        'COMPANY',
        'calculate_sga_ratio'
    )
    if result.success:
        print(f"✅ Success!")
        print(f"Function: {result.formula.function_name}")
        print(f"Formula: {result.formula.formula_description}")
    else:
        print(f"❌ Failed: {result.error_message}")
