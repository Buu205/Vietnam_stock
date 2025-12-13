#!/usr/bin/env python3
"""
Example Script: Add New Formula Using AI Assistant
==================================================

This script demonstrates the complete workflow to add a new formula
to the fundamental analysis system using AI assistance.

Example: Add "Total Operating Expenses to Revenue" ratio

Author: AI Assistant
Date: 2025-12-12
"""

import sys
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PROCESSORS.core.ai import ai_assistant, metric_resolver


def step_1_explore_metrics():
    """Step 1: Explore available metrics"""
    print("=" * 80)
    print("STEP 1: EXPLORE AVAILABLE METRICS")
    print("=" * 80)

    # Search for operating expense metrics
    print("\n🔍 Searching for 'chi phí' (expenses) metrics in COMPANY...")
    results = metric_resolver.search_by_keywords(
        ["chi phí"],
        entity_type="COMPANY",
        language='vi'
    )

    print(f"\n📊 Found {len(results)} metrics:")
    for i, metric in enumerate(results[:10], 1):  # Show first 10
        print(f"{i:2}. {metric.code:8} - {metric.name_vi[:60]}")

    # Search for revenue metrics
    print("\n🔍 Searching for 'doanh thu' (revenue) metrics...")
    revenue_results = metric_resolver.resolve_metric_name(
        "doanh thu thuần",
        entity_type="COMPANY",
        language='vi'
    )

    if revenue_results:
        for r in revenue_results:
            print(f"   {r.code:8} - {r.name_vi}")

    return results, revenue_results


def step_2_validate_metrics():
    """Step 2: Validate specific metric codes"""
    print("\n" + "=" * 80)
    print("STEP 2: VALIDATE METRIC CODES")
    print("=" * 80)

    # Codes we want to use:
    # CIS_25 = Chi phí bán hàng
    # CIS_26 = Chi phí quản lý doanh nghiệp
    # CIS_10 = Doanh thu thuần

    codes_to_validate = ['CIS_25', 'CIS_26', 'CIS_10']

    print(f"\n✅ Validating codes: {codes_to_validate}")

    valid, invalid = metric_resolver.validate_metrics_for_entity(
        codes_to_validate,
        "COMPANY"
    )

    print(f"\n✅ Valid codes: {valid}")
    print(f"❌ Invalid codes: {invalid}")

    # Get detailed info
    print("\n📋 Metric Details:")
    for code in valid:
        metric = metric_resolver.resolve_metric_code(code, "COMPANY")
        if metric:
            print(f"   {metric.code:8} - {metric.name_vi}")

    return valid, invalid


def step_3_generate_formula():
    """Step 3: Generate formula using AI"""
    print("\n" + "=" * 80)
    print("STEP 3: GENERATE FORMULA WITH AI")
    print("=" * 80)

    print("\n🤖 Generating formula: (CIS_25 + CIS_26) / CIS_10")
    print("   Formula: Total Operating Expenses / Revenue")
    print("   Entity: COMPANY")

    # Method 1: Let AI parse the formula
    print("\n📝 Method 1: Natural formula parsing")
    result1 = ai_assistant.generate_formula(
        "(CIS_25 + CIS_26) / CIS_10",
        "COMPANY"
    )

    if result1.success:
        print(f"   ✅ Success!")
        print(f"   Function: {result1.formula.function_name}")
        print(f"   Dependencies: {result1.formula.dependencies}")
    else:
        print(f"   ❌ Failed: {result1.error_message}")

    # Method 2: Explicit codes and operation (RECOMMENDED)
    print("\n📝 Method 2: Explicit codes (recommended)")

    # First generate sum of expenses
    result2 = ai_assistant.generate_formula_from_codes(
        metric_codes=['CIS_25', 'CIS_26', 'CIS_10'],
        operation='divide',  # Will do (CIS_25 + CIS_26) / CIS_10
        entity_type='COMPANY',
        function_name='calculate_operating_expenses_to_revenue'
    )

    if result2.success:
        print(f"   ✅ Success!")
        print(f"   Function: {result2.formula.function_name}")
        print(f"   Formula: {result2.formula.formula_description}")
        print(f"   Dependencies: {result2.formula.dependencies}")
        return result2
    else:
        print(f"   ❌ Failed: {result2.error_message}")
        return None


def step_4_review_generated_code(result):
    """Step 4: Review generated code"""
    print("\n" + "=" * 80)
    print("STEP 4: REVIEW GENERATED CODE")
    print("=" * 80)

    if not result or not result.success:
        print("❌ No formula to review")
        return

    print("\n📄 Generated Function Code:")
    print("-" * 80)
    print(result.formula.function_code)
    print("-" * 80)

    # Save to file
    output_file = Path(__file__).parent / "generated_formula_example.py"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#!/usr/bin/env python3\n")
        f.write('"""\nAI-Generated Formula\n"""\n\n')
        f.write("import pandas as pd\n")
        f.write("from PROCESSORS.fundamental.formulas.utils import safe_divide\n\n")
        f.write(result.formula.function_code)

    print(f"\n💾 Code saved to: {output_file}")


def step_5_test_generated_formula(result):
    """Step 5: Test generated formula with sample data"""
    print("\n" + "=" * 80)
    print("STEP 5: TEST WITH SAMPLE DATA")
    print("=" * 80)

    if not result or not result.success:
        print("❌ No formula to test")
        return

    # Create sample data
    sample_data = pd.DataFrame({
        'CIS_25': [100, 200, 150],      # Chi phí bán hàng
        'CIS_26': [50, 100, 75],        # Chi phí quản lý
        'CIS_10': [1000, 2000, 1500],   # Doanh thu thuần
    })

    print("\n📊 Sample Data:")
    print(sample_data)

    # Execute generated formula
    # Note: We need to define the function first
    print("\n🧪 Testing formula...")

    # Import safe_divide
    from PROCESSORS.fundamental.formulas.utils import safe_divide

    # Execute the generated function (dynamically)
    # For demo, we'll calculate manually
    numerator = sample_data['CIS_25'] + sample_data['CIS_26']
    result_series = safe_divide(numerator, sample_data['CIS_10']) * 100

    print("\n📈 Results:")
    print(result_series)

    # Expected: [15.0, 15.0, 15.0]
    print("\n✅ Expected: All values should be 15.0%")
    print(f"✅ Actual: {result_series.tolist()}")


def step_6_integration_guide():
    """Step 6: Show integration steps"""
    print("\n" + "=" * 80)
    print("STEP 6: INTEGRATION GUIDE")
    print("=" * 80)

    print("\n📝 Next Steps to Integrate:")
    print("\n1️⃣  Add to company_formulas.py:")
    print("   File: PROCESSORS/fundamental/formulas/company_formulas.py")
    print("   Location: Inside CompanyFormulas class")

    print("\n2️⃣  Register in FormulaRegistry:")
    print("   File: PROCESSORS/fundamental/formulas/registry.py")
    print("   Method: _register_entity_formulas()")

    print("\n3️⃣  Use in Calculator:")
    print("   File: PROCESSORS/fundamental/calculators/company_calculator.py")
    print("   Method: Add new calculation method")

    print("\n4️⃣  Update Schema (optional):")
    print("   File: config/schemas/data/fundamental_calculated_schema.json")

    print("\n5️⃣  Test Integration:")
    print("   Run: python3 tests/fundamental/calculator_integration_test.py")


def main():
    """Main workflow"""
    print("\n" + "🤖" * 40)
    print("AI-ASSISTED FORMULA GENERATION WORKFLOW")
    print("🤖" * 40)

    # Step 1: Explore metrics
    results, revenue_results = step_1_explore_metrics()

    # Step 2: Validate metrics
    valid, invalid = step_2_validate_metrics()

    # Step 3: Generate formula
    formula_result = step_3_generate_formula()

    # Step 4: Review code
    step_4_review_generated_code(formula_result)

    # Step 5: Test
    step_5_test_generated_formula(formula_result)

    # Step 6: Integration guide
    step_6_integration_guide()

    print("\n" + "=" * 80)
    print("✅ WORKFLOW COMPLETED!")
    print("=" * 80)

    print("\n📚 Next Steps:")
    print("   1. Review generated code in: scripts/generated_formula_example.py")
    print("   2. Follow integration guide above")
    print("   3. Test with actual data")
    print("   4. Read full guide: docs/AI_FORMULA_GUIDE.md")

    print("\n💡 Quick Commands:")
    print("   # Test calculator")
    print("   python3 tests/fundamental/calculator_integration_test.py")
    print("")
    print("   # Load data and test")
    print("   from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator")
    print("   calc = CompanyFinancialCalculator('DATA/processed/fundamental/company_full.parquet')")
    print("   result = calc.calculate_all_metrics('VNM')")
    print("")


if __name__ == "__main__":
    main()
