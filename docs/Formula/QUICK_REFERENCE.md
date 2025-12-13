# 🚀 Quick Reference: AI Formula Assistant

**1-Page Cheat Sheet cho việc thêm/sửa formulas**

---

## ⚡ Quick Start (30 seconds)

```python
from PROCESSORS.core.ai import ai_assistant

# Generate formula
result = ai_assistant.generate_formula("CIS_25 / CIS_10", "COMPANY")

if result.success:
    print(result.formula.function_code)
    # ✅ Copy & paste vào formula file!
```

---

## 📋 Complete Workflow (5 minutes)

### 1️⃣ Generate Formula
```python
from PROCESSORS.core.ai import ai_assistant

result = ai_assistant.generate_formula_from_codes(
    metric_codes=['CIS_25', 'CIS_10'],
    operation='divide',
    entity_type='COMPANY',
    function_name='calculate_sga_ratio'
)
```

### 2️⃣ Add to Formula File
**File:** `PROCESSORS/fundamental/formulas/company_formulas.py`
```python
class CompanyFormulas:
    @staticmethod
    def calculate_sga_ratio(df: pd.DataFrame) -> pd.Series:
        """Chi phí bán hàng / Doanh thu"""
        return safe_divide(df['CIS_25'], df['CIS_10']) * 100
```

### 3️⃣ Register in Registry
**File:** `PROCESSORS/fundamental/formulas/registry.py`
```python
self.register_formula(
    "calculate_sga_ratio",
    CompanyFormulas.calculate_sga_ratio,
    ["COMPANY"]
)
```

### 4️⃣ Use in Calculator
**File:** `PROCESSORS/fundamental/calculators/company_calculator.py`
```python
def _calculate_profitability(self, df: pd.DataFrame) -> pd.DataFrame:
    df['sga_ratio'] = CompanyFormulas.calculate_sga_ratio(df)
    return df
```

### 5️⃣ Test
```python
from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator

calc = CompanyFinancialCalculator("DATA/processed/fundamental/company_full.parquet")
result = calc.calculate_all_metrics("VNM")
print(result['sga_ratio'])
```

---

## 🔍 Search Metrics

```python
from PROCESSORS.core.ai import metric_resolver

# Search by Vietnamese name
results = metric_resolver.resolve_metric_name("doanh thu", "COMPANY")

# Search by code
metric = metric_resolver.resolve_metric_code("CIS_10", "COMPANY")

# Validate multiple codes
valid, invalid = metric_resolver.validate_metrics_for_entity(
    ['CIS_10', 'CIS_25'],
    'COMPANY'
)
```

---

## 📊 File Locations

| Component | File |
|-----------|------|
| **Formulas** | `PROCESSORS/fundamental/formulas/company_formulas.py` |
| **Registry** | `PROCESSORS/fundamental/formulas/registry.py` |
| **Calculator** | `PROCESSORS/fundamental/calculators/company_calculator.py` |
| **Tests** | `tests/fundamental/calculator_integration_test.py` |
| **AI Tools** | `PROCESSORS/core/ai/` |

---

## ⚠️ Common Issues

### Issue: "Không tìm thấy metrics"
```python
# ❌ Wrong
result = ai_assistant.generate_formula("SGA/Rev", "COMPANY")

# ✅ Correct
result = ai_assistant.generate_formula("CIS_25 / CIS_10", "COMPANY")
```

### Issue: "safe_divide not defined"
```python
# ✅ Add import
from PROCESSORS.fundamental.formulas.utils import safe_divide
```

### Issue: "Formula không xuất hiện"
Checklist:
- ✅ Add to formula file?
- ✅ Register in registry.py?
- ✅ Add to calculator method?
- ✅ Metric codes exist in data?

---

## 🎯 3 Methods to Generate

### Method 1: Direct Codes (Recommended)
```python
result = ai_assistant.generate_formula("CIS_25 / CIS_10", "COMPANY")
```

### Method 2: Explicit with Custom Name
```python
result = ai_assistant.generate_formula_from_codes(
    ['CIS_25', 'CIS_10'],
    'divide',
    'COMPANY',
    'my_function_name'
)
```

### Method 3: Natural Language (Experimental)
```python
result = ai_assistant.generate_formula(
    "chi phí bán hàng / doanh thu thuần",
    "COMPANY"
)
```

---

## 📝 Operations

| Operation | Code | Example |
|-----------|------|---------|
| **Ratio** | `'divide'` | `A / B * 100` |
| **Sum** | `'sum'` | `A + B + C` |
| **Subtract** | `'subtract'` | `A - B` |
| **Multiply** | `'multiply'` | `A * B` |
| **Growth** | `'growth'` | `pct_change()` |
| **TTM** | `'ttm'` | `rolling(4).sum()` |

---

## 🧪 Test Formula

```python
import pandas as pd
from PROCESSORS.fundamental.formulas.utils import safe_divide

# Sample data
df = pd.DataFrame({
    'CIS_25': [100, 200],
    'CIS_10': [1000, 2000]
})

# Test
result = safe_divide(df['CIS_25'], df['CIS_10']) * 100
print(result)  # Expected: [10.0, 10.0]
```

---

## 📚 Full Documentation

- **Complete Guide:** `docs/AI_FORMULA_GUIDE.md`
- **Example Script:** `scripts/example_add_formula.py`
- **Test Suite:** `tests/fundamental/test_ai_formula_generation.py`

---

## 💡 Pro Tips

1. **Always validate codes first**
   ```python
   metric = metric_resolver.resolve_metric_code("CIS_10", "COMPANY")
   ```

2. **Use preview before generating**
   ```python
   preview = ai_assistant.validate_and_preview("CIS_25 / CIS_10", "COMPANY")
   ```

3. **Test với sample data trước**
   ```python
   df = pd.DataFrame({'CIS_25': [100], 'CIS_10': [1000]})
   ```

4. **Check calculator integration**
   ```python
   calc = CompanyFinancialCalculator(data_path)
   calculations = calc.get_entity_specific_calculations()
   print(list(calculations.keys()))
   ```

---

## 🎓 Entity Types

| Entity | Prefix | Example Codes |
|--------|--------|---------------|
| **COMPANY** | CIS, CBS, CCS | CIS_10, CBS_270 |
| **BANK** | BIS, BBS, BCS | BIS_1, BBS_100 |
| **INSURANCE** | IIS, IBS, ICS | IIS_1, IBS_18 |
| **SECURITY** | SIS, SBS, SCS | SIS_1, SBS_39 |

---

**Last Updated:** 2025-12-12
**Need Help?** Read full guide: `docs/AI_FORMULA_GUIDE.md`
