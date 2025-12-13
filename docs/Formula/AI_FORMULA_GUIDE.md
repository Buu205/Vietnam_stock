# 🤖 Hướng Dẫn Sử Dụng AI Formula Assistant

**Version:** 1.0
**Date:** 2025-12-12
**Author:** AI Assistant

---

## 📋 Mục Lục

1. [Import và Sử Dụng AI Assistant](#1-import-và-sử-dụng-ai-assistant)
2. [3 Phương Pháp Generate Formula](#2-3-phương-pháp-generate-formula)
3. [Flow Thêm Formula Mới](#3-flow-thêm-formula-mới)
4. [Flow Sửa Formula Hiện Có](#4-flow-sửa-formula-hiện-có)
5. [Integration với Calculator System](#5-integration-với-calculator-system)
6. [Troubleshooting](#6-troubleshooting)

🚀 SỬ DỤNG NGAY
Cách 1: Import và sử dụng (30 giây)
from PROCESSORS.core.ai import ai_assistant

result = ai_assistant.generate_formula("CIS_25 / CIS_10", "COMPANY")
print(result.formula.function_code)
# ✅ Copy code này vào company_formulas.py!
Cách 2: Run demo script
python3 scripts/example_add_formula.py
Cách 3: Đọc hướng dẫn đầy đủ
cat docs/AI_FORMULA_GUIDE.md
cat docs/QUICK_REFERENCE.md

🎯 NEXT STEPS (Tùy bạn)
Bạn có thể:
✅ Sử dụng ngay - Import ai_assistant và generate formulas
📚 Đọc docs - docs/AI_FORMULA_GUIDE.md (hướng dẫn đầy đủ)
🧪 Run tests - tests/fundamental/test_ai_formula_generation.py
💡 Run demo - scripts/example_add_formula.py
🚀 Build Section 3 - Streamlit UI cho AI assistant (nếu muốn)

📊 INTEGRATION FLOW
USER INPUT
    ↓
[AI Assistant]
    ↓
Generated Python Code
    ↓
company_formulas.py → registry.py → calculator.py
    ↓
Calculator Output
---

## 1. Import và Sử Dụng AI Assistant

### 1.1 Basic Import

```python
# Method 1: Import singleton instance (RECOMMENDED)
from PROCESSORS.core.ai import ai_assistant

# Method 2: Import class
from PROCESSORS.core.ai import FormulaAIAssistant
assistant = FormulaAIAssistant()

# Method 3: Import tất cả components
from PROCESSORS.core.ai import (
    ai_assistant,           # Main orchestrator
    formula_parser,         # NLP parser
    metric_resolver,        # Metric lookup
    code_generator          # Code generator
)
```

### 1.2 Quick Start Example

```python
from PROCESSORS.core.ai import ai_assistant

# Generate formula từ metric codes
result = ai_assistant.generate_formula("CIS_25 / CIS_10", "COMPANY")

if result.success:
    print("✅ Success!")
    print(f"Function name: {result.formula.function_name}")
    print(f"Dependencies: {result.formula.dependencies}")
    print(f"\nGenerated code:\n{result.formula.function_code}")
else:
    print(f"❌ Failed: {result.error_message}")
    if result.suggestions:
        print("\nSuggestions:")
        for s in result.suggestions:
            print(f"  - {s}")
```

---

## 2. 3 Phương Pháp Generate Formula

### Method 1: Direct Metric Codes (✅ RECOMMENDED)

**Dùng khi:** Bạn biết chính xác metric codes cần dùng

```python
from PROCESSORS.core.ai import ai_assistant

# Ví dụ 1: Ratio formula
result = ai_assistant.generate_formula("CIS_25 / CIS_10", "COMPANY")

# Ví dụ 2: Sum formula
result = ai_assistant.generate_formula("CIS_25 + CIS_26", "COMPANY")

# Ví dụ 3: Complex formula
result = ai_assistant.generate_formula("(CIS_25 + CIS_26) / CIS_10", "COMPANY")
```

**Output:**
```python
def calculate_sga_ratio(df: pd.DataFrame) -> pd.Series:
    """
    Tính tỷ lệ Chi phí bán hàng
    trên Doanh thu thuần

    Áp dụng cho: COMPANY

    Args:
        df: DataFrame chứa dữ liệu pivot với các metric codes làm columns

    Returns:
        Series chứa kết quả tính toán

    Dependencies:
        CIS_25, CIS_10

    Entity Types:
        COMPANY
    """
    return safe_divide(
        df['CIS_25'],
        df['CIS_10']
    ) * 100  # Convert to percentage
```

---

### Method 2: Generate from Codes with Custom Function Name

**Dùng khi:** Bạn muốn control tên hàm và operation cụ thể

```python
from PROCESSORS.core.ai import ai_assistant

result = ai_assistant.generate_formula_from_codes(
    metric_codes=['CIS_25', 'CIS_10'],      # Danh sách metric codes
    operation='divide',                      # Operation: divide, sum, subtract, multiply
    entity_type='COMPANY',                   # COMPANY, BANK, INSURANCE, SECURITY
    function_name='calculate_sga_to_revenue_ratio'  # Custom function name
)

if result.success:
    print(result.formula.function_code)
```

**Supported operations:**
- `'divide'` - Chia (A / B * 100)
- `'sum'` - Cộng (A + B + C)
- `'subtract'` - Trừ (A - B)
- `'multiply'` - Nhân (A * B)
- `'growth'` - Tăng trưởng (YoY/QoQ)
- `'ttm'` - Trailing 12 months

---

### Method 3: Natural Language (⚠️ EXPERIMENTAL)

**Dùng khi:** Testing hoặc exploration

```python
from PROCESSORS.core.ai import ai_assistant

# Tiếng Việt (cần tên chính xác)
result = ai_assistant.generate_formula(
    "tính chi phí bán hàng / doanh thu thuần",
    "COMPANY"
)

# Tiếng Anh
result = ai_assistant.generate_formula(
    "calculate gross margin",
    "COMPANY"
)
```

**⚠️ Lưu ý:** Method này cần tên metric chính xác trong registry. Recommend dùng Method 1 hoặc 2.

---

## 3. Flow Thêm Formula Mới

### 📊 Complete Flow Diagram

```
[1] AI Generate → [2] Test Code → [3] Add to Formula Module → [4] Register → [5] Use in Calculator
```

### Step 1️⃣: Generate Formula với AI

```python
# File: scripts/generate_new_formula.py
from PROCESSORS.core.ai import ai_assistant

# Generate formula
result = ai_assistant.generate_formula_from_codes(
    metric_codes=['CIS_25', 'CIS_26', 'CIS_10'],
    operation='divide',
    entity_type='COMPANY',
    function_name='calculate_total_sga_to_revenue'
)

if result.success:
    # Save to file for review
    with open('generated_formula.py', 'w') as f:
        f.write(result.formula.function_code)

    print(f"✅ Formula generated!")
    print(f"Dependencies: {result.formula.dependencies}")
    print(f"Function name: {result.formula.function_name}")
else:
    print(f"❌ Error: {result.error_message}")
```

---

### Step 2️⃣: Review và Test Generated Code

```python
# Copy generated code và test
import pandas as pd
from PROCESSORS.fundamental.formulas.utils import safe_divide

# Paste generated function here
def calculate_total_sga_to_revenue(df: pd.DataFrame) -> pd.Series:
    """Generated function..."""
    numerator = df['CIS_25'] + df['CIS_26']
    return safe_divide(numerator, df['CIS_10']) * 100

# Test với sample data
test_df = pd.DataFrame({
    'CIS_25': [100, 200, 300],
    'CIS_26': [50, 75, 100],
    'CIS_10': [1000, 2000, 3000]
})

result = calculate_total_sga_to_revenue(test_df)
print(result)
# Expected: [15.0, 13.75, 13.33]
```

---

### Step 3️⃣: Add Formula to Appropriate Module

**File structure:**
```
PROCESSORS/fundamental/formulas/
├── _base_formulas.py      # Common formulas (ROE, ROA, margins, etc.)
├── company_formulas.py    # COMPANY-specific formulas
├── bank_formulas.py       # BANK-specific formulas
├── insurance_formulas.py  # INSURANCE-specific (TODO)
└── security_formulas.py   # SECURITY-specific (TODO)
```

**Add to company_formulas.py:**

```python
# File: PROCESSORS/fundamental/formulas/company_formulas.py

from typing import Optional
import pandas as pd
from .utils import safe_divide

class CompanyFormulas:
    """Company-specific financial formulas"""

    # ... existing formulas ...

    @staticmethod
    def calculate_total_sga_to_revenue(df: pd.DataFrame) -> pd.Series:
        """
        Tính tỷ lệ Tổng chi phí SGA (Sales + Admin)
        trên Doanh thu thuần

        Áp dụng cho: COMPANY

        Args:
            df: DataFrame chứa dữ liệu pivot với các metric codes làm columns

        Returns:
            Series chứa kết quả tính toán (%)

        Dependencies:
            CIS_25 (Chi phí bán hàng)
            CIS_26 (Chi phí quản lý)
            CIS_10 (Doanh thu thuần)

        Formula:
            (CIS_25 + CIS_26) / CIS_10 * 100
        """
        numerator = df['CIS_25'] + df['CIS_26']
        return safe_divide(numerator, df['CIS_10']) * 100
```

---

### Step 4️⃣: Register Formula in FormulaRegistry

**File: `PROCESSORS/fundamental/formulas/registry.py`**

```python
# Add import
from .company_formulas import CompanyFormulas

class FormulaRegistry:
    # ... existing code ...

    def _register_entity_formulas(self):
        """Đăng ký các công thức đặc thù cho từng loại thực thể."""

        # COMPANY formulas
        self.register_formula("calculate_revenue_growth", CompanyFormulas.calculate_revenue_growth, ["COMPANY"])
        self.register_formula("calculate_profit_growth", CompanyFormulas.calculate_profit_growth, ["COMPANY"])

        # ✨ ADD YOUR NEW FORMULA HERE
        self.register_formula(
            "calculate_total_sga_to_revenue",
            CompanyFormulas.calculate_total_sga_to_revenue,
            ["COMPANY"]
        )

        # BANK formulas
        # ... existing bank formulas ...
```

---

### Step 5️⃣: Use in Calculator

**File: `PROCESSORS/fundamental/calculators/company_calculator.py`**

```python
from PROCESSORS.fundamental.formulas.company_formulas import CompanyFormulas

class CompanyFinancialCalculator(BaseFinancialCalculator):

    def get_entity_specific_calculations(self) -> Dict[str, callable]:
        """
        Get company-specific calculation methods.
        """
        return {
            # Existing calculations
            'income_statement': self._calculate_income_statement,
            'profitability': self._calculate_profitability,

            # ✨ ADD YOUR NEW CALCULATION HERE
            'sga_analysis': self._calculate_sga_analysis,
        }

    def _calculate_sga_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate SGA-related metrics"""
        # Add individual SGA components
        df['sga_selling'] = df.get('CIS_25', 0)
        df['sga_admin'] = df.get('CIS_26', 0)

        # ✨ USE YOUR NEW FORMULA
        df['total_sga_to_revenue'] = CompanyFormulas.calculate_total_sga_to_revenue(df)

        return df
```

---

### Step 6️⃣: Update Schema (Optional)

**File: `config/schemas/data/fundamental_calculated_schema.json`**

```json
{
  "COMPANY": {
    "calculated_metrics": {
      "total_sga_to_revenue": {
        "name_vi": "Tỷ lệ Tổng SGA / Doanh thu",
        "name_en": "Total SGA to Revenue Ratio",
        "data_type": "number",
        "unit": "%",
        "format": ",.2f",
        "category": "profitability",
        "description": "Tỷ lệ tổng chi phí bán hàng và quản lý trên doanh thu thuần"
      }
    }
  }
}
```

---

### Step 7️⃣: Test Integration

```python
# Test script
from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator

# Initialize calculator
calc = CompanyFinancialCalculator("DATA/processed/fundamental/company_full.parquet")

# Calculate for a specific ticker
result = calc.calculate_all_metrics("VNM")

# Check if new metric exists
if 'total_sga_to_revenue' in result.columns:
    print("✅ New formula integrated successfully!")
    print(result[['REPORT_DATE', 'total_sga_to_revenue']].head())
else:
    print("❌ Formula not found in results")
```

---

## 4. Flow Sửa Formula Hiện Có

### Step 1️⃣: Locate Existing Formula

```bash
# Search for formula in codebase
grep -r "calculate_gross_margin" PROCESSORS/fundamental/formulas/

# Output:
# PROCESSORS/fundamental/formulas/_base_formulas.py:def calculate_gross_margin(...)
```

### Step 2️⃣: Review Current Implementation

```python
# File: PROCESSORS/fundamental/formulas/_base_formulas.py

def calculate_gross_margin(gross_profit: pd.Series, revenue: pd.Series) -> pd.Series:
    """
    Current implementation
    """
    return safe_divide(gross_profit, revenue) * 100
```

### Step 3️⃣: Generate New Version with AI

```python
from PROCESSORS.core.ai import ai_assistant

# Generate improved version
result = ai_assistant.generate_formula_from_codes(
    metric_codes=['CIS_20', 'CIS_10'],  # Updated metric codes
    operation='divide',
    entity_type='COMPANY',
    function_name='calculate_gross_margin_v2'
)

print(result.formula.function_code)
```

### Step 4️⃣: Compare and Update

```python
# NEW VERSION (AI-generated)
def calculate_gross_margin(df: pd.DataFrame) -> pd.Series:
    """
    Tính biên lợi nhuận gộp

    Updated: 2025-12-12
    Uses direct metric codes instead of derived values

    Dependencies:
        CIS_20 (Lợi nhuận gộp)
        CIS_10 (Doanh thu thuần)
    """
    return safe_divide(df['CIS_20'], df['CIS_10']) * 100
```

### Step 5️⃣: Update Tests

```python
# File: tests/fundamental/test_formulas.py

def test_calculate_gross_margin():
    """Test updated gross margin calculation"""
    df = pd.DataFrame({
        'CIS_20': [200, 400, 600],  # Gross profit
        'CIS_10': [1000, 2000, 3000]  # Revenue
    })

    result = calculate_gross_margin(df)

    expected = pd.Series([20.0, 20.0, 20.0])
    pd.testing.assert_series_equal(result, expected)
```

### Step 6️⃣: Run Tests and Deploy

```bash
# Run tests
python3 tests/fundamental/test_formulas.py

# If tests pass, commit changes
git add PROCESSORS/fundamental/formulas/_base_formulas.py
git commit -m "feat: update calculate_gross_margin to use direct metric codes"
```

---

## 5. Integration với Calculator System

### 5.1 Calculator Architecture

```
BaseFinancialCalculator (Abstract)
├── CompanyFinancialCalculator
├── BankFinancialCalculator
├── InsuranceFinancialCalculator
└── SecurityFinancialCalculator
```

### 5.2 Template Method Pattern

Mỗi calculator implement 3 abstract methods:

```python
class CompanyFinancialCalculator(BaseFinancialCalculator):

    def get_entity_type(self) -> str:
        """Return entity type"""
        return "COMPANY"

    def get_metric_prefixes(self) -> List[str]:
        """Return metric code prefixes for this entity"""
        return ["CIS", "CBS", "CCS"]

    def get_entity_specific_calculations(self) -> Dict[str, callable]:
        """
        Return dictionary of calculation methods

        ✨ ADD YOUR FORMULAS HERE
        """
        return {
            'income_statement': self._calculate_income_statement,
            'balance_sheet': self._calculate_balance_sheet,
            'profitability': self._calculate_profitability,
            'liquidity': self._calculate_liquidity,
            'leverage': self._calculate_leverage,
            'activity': self._calculate_activity,
            'margins': self._calculate_margins,

            # Add custom calculations
            'custom_analysis': self._calculate_custom_analysis,
        }
```

### 5.3 Adding Calculation Method

```python
def _calculate_custom_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate custom metrics

    This method is called by calculate_all_metrics() automatically
    """
    # Import your formulas
    from PROCESSORS.fundamental.formulas.company_formulas import CompanyFormulas

    # Use AI-generated formulas
    df['sga_ratio'] = CompanyFormulas.calculate_total_sga_to_revenue(df)
    df['operating_leverage'] = CompanyFormulas.calculate_operating_leverage(df)

    return df
```

### 5.4 Complete Flow Example

```python
# 1. Generate formula with AI
from PROCESSORS.core.ai import ai_assistant

result = ai_assistant.generate_formula_from_codes(
    ['CIS_30', 'CIS_10'],
    'divide',
    'COMPANY',
    'calculate_operating_margin'
)

# 2. Add to company_formulas.py
# (Copy generated code)

# 3. Register in registry.py
self.register_formula(
    "calculate_operating_margin",
    CompanyFormulas.calculate_operating_margin,
    ["COMPANY"]
)

# 4. Use in calculator
def _calculate_profitability(self, df: pd.DataFrame) -> pd.DataFrame:
    df['operating_margin'] = CompanyFormulas.calculate_operating_margin(df)
    return df

# 5. Test
calc = CompanyFinancialCalculator("DATA/processed/fundamental/company_full.parquet")
result = calc.calculate_all_metrics("VNM")
print(result['operating_margin'])
```

---

## 6. Troubleshooting

### Issue 1: "Không tìm thấy metrics"

**Problem:**
```python
result = ai_assistant.generate_formula("tính SGA/Rev", "COMPANY")
# Error: Không tìm thấy metrics cho: tính SGA/Rev
```

**Solution:**
```python
# ✅ Dùng metric codes trực tiếp
result = ai_assistant.generate_formula("CIS_25 / CIS_10", "COMPANY")

# ✅ Hoặc dùng tên tiếng Việt chính xác
result = ai_assistant.generate_formula(
    "chi phí bán hàng / doanh thu thuần",
    "COMPANY"
)
```

---

### Issue 2: "safe_divide not defined"

**Problem:**
```python
NameError: name 'safe_divide' is not defined
```

**Solution:**
```python
# Add import ở đầu file
from PROCESSORS.fundamental.formulas.utils import safe_divide

# Hoặc use inline
def calculate_ratio(df: pd.DataFrame) -> pd.Series:
    from PROCESSORS.fundamental.formulas.utils import safe_divide
    return safe_divide(df['A'], df['B']) * 100
```

---

### Issue 3: "Metric code không tồn tại"

**Problem:**
```python
result = ai_assistant.generate_formula_from_codes(
    ['CIS_999'],  # Invalid code
    'sum',
    'COMPANY'
)
# Error: Metric codes không tồn tại: {'CIS_999'}
```

**Solution:**
```python
# Validate codes trước
from PROCESSORS.core.ai import metric_resolver

# Check if code exists
metric = metric_resolver.resolve_metric_code('CIS_999', 'COMPANY')
if metric:
    print(f"✅ Valid: {metric.name_vi}")
else:
    print("❌ Invalid code")

# Search for correct code
results = metric_resolver.resolve_metric_name("doanh thu", "COMPANY")
for r in results:
    print(f"{r.code}: {r.name_vi}")
```

---

### Issue 4: Formula không xuất hiện trong calculator output

**Problem:**
```python
result = calc.calculate_all_metrics("VNM")
# 'my_new_metric' not in result.columns
```

**Checklist:**

1. ✅ Formula đã add vào formula module?
2. ✅ Formula đã register trong `registry.py`?
3. ✅ Calculator method đã được add vào `get_entity_specific_calculations()`?
4. ✅ Metric codes tồn tại trong data?
5. ✅ DataFrame có đúng metric columns?

**Debug:**
```python
# Check what calculations are registered
calc = CompanyFinancialCalculator(data_path)
calculations = calc.get_entity_specific_calculations()
print("Available calculations:", list(calculations.keys()))

# Check if metrics exist in data
calc.load_data()
calc.pivot_data()
print("Available columns:", calc.pivot_df.columns.tolist())
```

---

## 📚 Reference Files

### Core AI Components
- `PROCESSORS/core/ai/nlp_formula_parser.py` - NLP parser
- `PROCESSORS/core/ai/metric_registry_resolver.py` - Metric resolver
- `PROCESSORS/core/ai/formula_code_generator.py` - Code generator
- `PROCESSORS/core/ai/formula_ai_assistant.py` - Main orchestrator

### Formula Modules
- `PROCESSORS/fundamental/formulas/_base_formulas.py` - Common formulas
- `PROCESSORS/fundamental/formulas/company_formulas.py` - COMPANY formulas
- `PROCESSORS/fundamental/formulas/bank_formulas.py` - BANK formulas
- `PROCESSORS/fundamental/formulas/registry.py` - Formula registry

### Calculators
- `PROCESSORS/fundamental/calculators/base_financial_calculator.py` - Base class
- `PROCESSORS/fundamental/calculators/company_calculator.py` - COMPANY calculator
- `PROCESSORS/fundamental/calculators/bank_calculator.py` - BANK calculator

### Tests
- `tests/fundamental/test_ai_formula_generation.py` - AI integration tests
- `tests/fundamental/calculator_integration_test.py` - Calculator tests

---

## 🎯 Quick Reference Commands

```python
# Import AI assistant
from PROCESSORS.core.ai import ai_assistant

# Generate formula
result = ai_assistant.generate_formula("CIS_25 / CIS_10", "COMPANY")

# Generate with custom name
result = ai_assistant.generate_formula_from_codes(
    ['CIS_25', 'CIS_10'],
    'divide',
    'COMPANY',
    'my_custom_function'
)

# Preview before generating
preview = ai_assistant.validate_and_preview("CIS_25 / CIS_10", "COMPANY")

# Search for metrics
from PROCESSORS.core.ai import metric_resolver
results = metric_resolver.resolve_metric_name("doanh thu", "COMPANY")

# Test calculator
from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator
calc = CompanyFinancialCalculator("DATA/processed/fundamental/company_full.parquet")
result = calc.calculate_all_metrics("VNM")
```

---

**End of Guide** 🎉
