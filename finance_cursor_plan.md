# FINANCE METRICS CALCULATION REFACTORING PLAN
## Vietnamese Stock Market Dashboard - Financial Calculation Engine Optimization

---

**Plan Created:** 2025-12-11  
**Author:** Claude Code (Senior Developer + Finance Analyst)  
**Priority:** HIGH - Core calculation engine for Streamlit dashboard display  
**Estimated Effort:** 6-10 days  
**Current Status:** Planning Phase - Awaiting Review & Approval

---

## EXECUTIVE SUMMARY

This plan addresses the need to refactor financial calculation formulas to ensure consistency between:
- **Formulas Layer** (`PROCESSORS/fundamental/formulas/`) - Pure calculation functions
- **Calculators Layer** (`PROCESSORS/fundamental/calculators/`) - Entity-specific calculation orchestrators
- **Dashboard Layer** (`WEBAPP/pages/`) - Streamlit UI that displays metrics

**Key Goals:**
1. Eliminate duplicate calculation logic between calculators and formulas
2. Ensure all dashboard-required metrics are calculated correctly
3. Standardize output column names for consistent dashboard consumption
4. Add missing formulas for growth rates and TTM calculations
5. Create comprehensive testing to validate end-to-end flow

**Problem Statement:**
- Dashboards (`bank_dashboard.py`, `company_dashboard_pyecharts.py`) need specific metrics like `net_margin`, `gross_margin`, `net_revenue_gr`
- Calculators may have duplicate logic instead of using formula functions
- Inconsistencies between what calculators output and what dashboards expect
- Missing formulas for growth rate calculations

---

## 1. CURRENT STATE ANALYSIS

### 1.1 Architecture Overview

```
PROCESSORS/fundamental/
├── formulas/                          (Pure calculation functions)
│   ├── _base_formulas.py             (Universal: ROE, ROA, margins, etc.)
│   ├── company_formulas.py           (Company-specific)
│   ├── bank_formulas.py              (Bank-specific)
│   └── utils.py                      (Helper: safe_divide, to_percentage)
│
├── calculators/                       (Entity-specific orchestrators)
│   ├── base_financial_calculator.py  (Abstract base class)
│   ├── company_calculator.py         (COMPANY entity)
│   ├── bank_calculator.py            (BANK entity)
│   ├── insurance_calculator.py        (INSURANCE entity)
│   └── security_calculator.py        (SECURITY entity)
│
└── sector_fa_analyzer.py             (Top-level orchestrator)

WEBAPP/pages/
├── bank_dashboard.py                 (Displays bank metrics)
├── company_dashboard_pyecharts.py    (Displays company metrics)
└── securities_dashboard.py           (Displays security metrics)
```

### 1.2 Data Flow (Current)

```
Raw Data (Parquet)
    ↓
Calculator.load_data() → Long format DataFrame
    ↓
Calculator.preprocess_data() → Filter by FREQ_CODE='Q', entity type
    ↓
Calculator.pivot_data() → Wide format (metrics as columns)
    ↓
Calculator.calculate_*() → Calculate metrics (may duplicate formula logic)
    ↓
Calculator.postprocess_results() → Format output
    ↓
Output: DATA/processed/fundamental/[entity]/[entity]_financial_metrics.parquet
    ↓
Dashboard reads parquet → Displays metrics
```

### 1.3 Key Issues Identified

| Issue | Location | Impact | Priority |
|-------|----------|--------|----------|
| **Duplicate calculation logic** | `company_calculator.py` line 128, `_base_formulas.py` line 175 | Code maintenance burden, potential inconsistencies | 🔴 HIGH |
| **Missing growth rate formulas** | `_base_formulas.py` | Dashboards need YoY/QoQ growth but formulas don't exist | 🔴 HIGH |
| **Inconsistent column names** | Calculator outputs vs Dashboard expectations | Dashboard may fail to find expected columns | 🟡 MEDIUM |
| **Missing TTM calculation formulas** | `_base_formulas.py` | Calculators calculate TTM but no reusable formula | 🟡 MEDIUM |
| **No validation of dashboard requirements** | Calculators | Output may not include all metrics dashboards need | 🟡 MEDIUM |

---

## 2. PROPOSED ARCHITECTURE

### 2.1 Target Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. FORMULAS LAYER (Single Source of Truth)                 │
│    - _base_formulas.py: Universal formulas                  │
│      • calculate_net_margin(net_income, revenue)            │
│      • calculate_gross_margin(gross_profit, revenue)        │
│      • calculate_yoy_growth(current, previous_year)         │
│      • calculate_qoq_growth(current, previous_quarter)      │
│      • calculate_ttm_sum(quarterly_values)                  │
│    - company_formulas.py: Company-specific                  │
│    - bank_formulas.py: Bank-specific                        │
│    ✅ Pure functions, well-tested, no side effects            │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. CALCULATORS LAYER (Use Formulas - No Duplication)       │
│    - company_calculator.py:                                 │
│      • Import formulas from _base_formulas                  │
│      • calculate_margins() → Uses calculate_net_margin()    │
│      • calculate_growth_rates() → Uses calculate_yoy_growth()│
│      • calculate_profitability_ratios() → Uses calculate_roe()│
│    ✅ No duplicate logic, delegates to formulas              │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. OUTPUT SCHEMA (Standardized Columns)                    │
│    - All calculators output same column names:              │
│      • net_margin, gross_margin, ebit_margin, ebitda_margin │
│      • net_revenue_gr, gross_profit_gr, ebit_gr, etc.       │
│      • roe, roa, eps, total_assets, total_equity            │
│    ✅ Consistent naming for dashboard consumption            │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. DASHBOARD LAYER (Read & Display - No Calculation)       │
│    - bank_dashboard.py: Reads bank_financial_metrics.parquet │
│    - company_dashboard_pyecharts.py: Reads company_*.parquet │
│    ✅ No calculation logic, just display                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Design Principles

1. **Single Source of Truth:** All calculation logic in formulas layer
2. **Separation of Concerns:** Calculators orchestrate, formulas calculate
3. **Consistency:** Same column names across all entity types
4. **Testability:** Pure functions are easy to unit test
5. **Maintainability:** Change formula once, affects all calculators

---

## 3. DETAILED IMPLEMENTATION PLAN

### PHASE 1: AUDIT & ALIGN (1-2 days)

**Goal:** Identify exactly which metrics dashboards need and compare with current calculator output

#### Task 1.1: Extract Required Metrics from Dashboards

**Files to analyze:**
- `WEBAPP/pages/company_dashboard_pyecharts.py`
- `WEBAPP/pages/bank_dashboard.py`
- `WEBAPP/pages/securities_dashboard.py`

**Expected output:**

```python
# Company Dashboard Requirements
required_company_metrics = [
    # Income Statement
    'net_revenue', 'gross_profit', 'ebit', 'ebitda', 'npatmi',
    
    # Margins (percentages)
    'gross_margin', 'ebit_margin', 'ebitda_margin', 'net_margin',
    
    # Growth Rates (percentages)
    'net_revenue_gr', 'gross_profit_gr', 'ebit_gr', 'ebitda_gr', 'npatmi_gr',
    
    # Profitability Ratios
    'roe', 'roa', 'eps',
    
    # Balance Sheet
    'total_assets', 'total_equity', 'cash', 'total_debt',
    
    # Cash Flow
    'operating_cf', 'investment_cf', 'financing_cf', 'fcf'
]

# Bank Dashboard Requirements
required_bank_metrics = [
    'net_interest_income', 'net_profit', 'nim', 'roe', 'roa',
    'casa_ratio', 'ldr', 'npl_ratio', 'cir', 'total_assets', 'total_equity'
]
```

#### Task 1.2: Compare with Current Calculator Output

**Action:** Load actual output files and check columns

```python
# Check company calculator output
df_company = pd.read_parquet('DATA/processed/fundamental/company/company_financial_metrics.parquet')
current_company_cols = set(df_company.columns)
missing_company = set(required_company_metrics) - current_company_cols

# Check bank calculator output
df_bank = pd.read_parquet('DATA/processed/fundamental/bank/bank_financial_metrics.parquet')
current_bank_cols = set(df_bank.columns)
missing_bank = set(required_bank_metrics) - current_bank_cols
```

#### Task 1.3: Create Metrics Mapping Table

**Output:** Markdown table documenting:

| Dashboard Metric | Calculator Output | Formula Function | Status | Notes |
|-----------------|-------------------|------------------|--------|-------|
| `net_margin` | `net_margin` | `calculate_net_margin()` | ✅ Exists | Verify calculation matches |
| `gross_margin` | `gross_margin` | `calculate_gross_margin()` | ✅ Exists | Verify calculation matches |
| `net_revenue_gr` | `net_revenue_gr` | `calculate_yoy_growth()` | ❌ Missing | Need to add formula |
| `roe` | `roe` | `calculate_roe()` | ✅ Exists | Verify calculation matches |
| `npatmi_gr` | `npatmi_gr` | `calculate_yoy_growth()` | ❌ Missing | Need to add formula |

#### Task 1.4: Document Formula Gaps

**Identify missing formulas:**
- `calculate_yoy_growth()` - Year-over-year growth rate
- `calculate_qoq_growth()` - Quarter-over-quarter growth rate
- `calculate_ttm_sum()` - Trailing twelve months sum
- `calculate_ttm_avg()` - Trailing twelve months average

**Deliverable:** `PHASE1_AUDIT_REPORT.md` with:
- List of required metrics per dashboard
- Current calculator output columns
- Missing metrics
- Missing formulas
- Inconsistencies found

---

### PHASE 2: REFACTOR CALCULATORS (2-3 days)

**Goal:** Remove duplicate logic from calculators, make them use formula functions

#### Task 2.1: Update `company_calculator.py`

**Current state (example):**
```python
def calculate_margins(self, df):
    result_df = df.copy()
    # Duplicate logic - should use formula
    result_df['net_margin'] = (df['npatmi'] / df['net_revenue']) * 100
    result_df['gross_margin'] = (df['gross_profit'] / df['net_revenue']) * 100
```

**Target state:**
```python
from PROCESSORS.fundamental.formulas._base_formulas import (
    calculate_net_margin,
    calculate_gross_margin,
    calculate_ebit_margin,
    calculate_ebitda_margin
)

def calculate_margins(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all margin metrics using formula functions.
    
    Args:
        df: DataFrame with income statement metrics (in billions VND)
        
    Returns:
        DataFrame with margin columns added
    """
    result_df = df.copy()
    
    # Convert to VND for formula functions (formulas expect VND)
    npatmi_vnd = df['npatmi'] * 1e9 if 'npatmi' in df.columns else None
    net_revenue_vnd = df['net_revenue'] * 1e9 if 'net_revenue' in df.columns else None
    gross_profit_vnd = df['gross_profit'] * 1e9 if 'gross_profit' in df.columns else None
    ebit_vnd = df['ebit'] * 1e9 if 'ebit' in df.columns else None
    ebitda_vnd = df['ebitda'] * 1e9 if 'ebitda' in df.columns else None
    
    # Use formula functions
    result_df['net_margin'] = calculate_net_margin(npatmi_vnd, net_revenue_vnd)
    result_df['gross_margin'] = calculate_gross_margin(gross_profit_vnd, net_revenue_vnd)
    result_df['ebit_margin'] = calculate_ebit_margin(ebit_vnd, net_revenue_vnd)
    result_df['ebitda_margin'] = calculate_ebitda_margin(ebitda_vnd, net_revenue_vnd)
    
    return result_df
```

**Files to update:**
- `PROCESSORS/fundamental/calculators/company_calculator.py`
  - `calculate_margins()` - Use formula functions
  - `calculate_profitability_ratios()` - Use `calculate_roe()`, `calculate_roa()`
  - `calculate_growth_rates()` - Use `calculate_yoy_growth()`, `calculate_qoq_growth()`

#### Task 2.2: Update `bank_calculator.py`

**Similar refactoring:**
- `calculate_margins()` - Use `calculate_nim()` from `bank_formulas.py`
- `calculate_ratios()` - Use formula functions where applicable

#### Task 2.3: Update `insurance_calculator.py` and `security_calculator.py`

**Apply same pattern:**
- Import formulas
- Use formula functions instead of inline calculations
- Remove duplicate logic

#### Task 2.4: Ensure All Metrics Are Calculated

**Update `calculate_all_metrics()` in each calculator:**

```python
def calculate_all_metrics(self) -> pd.DataFrame:
    """
    Main orchestration method - ensures all dashboard metrics are calculated.
    
    Returns:
        DataFrame with all required metrics for dashboard display
    """
    # Load and preprocess
    df = self.load_data()
    df = self.preprocess_data(df)
    df = self.pivot_data(df)
    
    # Calculate in dependency order
    df = self.calculate_income_statement(df)
    df = self.calculate_balance_sheet(df)
    df = self.calculate_cash_flow(df)  # If applicable
    
    # Calculate derived metrics (using formulas)
    df = self.calculate_margins(df)  # ✅ Uses formulas
    df = self.calculate_growth_rates(df)  # ✅ Uses formulas
    df = self.calculate_profitability_ratios(df)  # ✅ Uses formulas
    df = self.calculate_ttm_metrics(df)  # ✅ Uses formulas
    
    # Postprocess and validate
    df = self.postprocess_results(df)
    
    return df
```

**Deliverable:** 
- Refactored calculator files
- All duplicate logic removed
- All calculators use formula functions

---

### PHASE 3: ADD MISSING FORMULAS (1-2 days)

**Goal:** Add formulas for growth rates and TTM calculations that dashboards need

#### Task 3.1: Add Growth Rate Formulas to `_base_formulas.py`

**New functions to add:**

```python
def calculate_yoy_growth(
    current_value: Optional[float],
    previous_year_value: Optional[float]
) -> Optional[float]:
    """
    Year-over-Year Growth Rate
    
    Formula: ((Current - Previous Year) / Previous Year) × 100
    
    Measures: Growth compared to same period previous year
    
    Interpretation:
        - > 20%: Strong growth
        - 10-20%: Good growth
        - 0-10%: Moderate growth
        - < 0%: Decline
    
    Args:
        current_value: Current period value
        previous_year_value: Same period previous year value
        
    Returns:
        Growth rate in percentage or None if invalid
        
    Examples:
        >>> calculate_yoy_growth(120, 100)
        20.0  # 20% growth
        >>> calculate_yoy_growth(80, 100)
        -20.0  # 20% decline
        >>> calculate_yoy_growth(100, 0)
        None  # Cannot divide by zero
    """
    if previous_year_value is None or previous_year_value == 0:
        return None
    
    if current_value is None:
        return None
        
    return to_percentage(
        safe_divide(current_value - previous_year_value, previous_year_value)
    )


def calculate_qoq_growth(
    current_value: Optional[float],
    previous_quarter_value: Optional[float]
) -> Optional[float]:
    """
    Quarter-over-Quarter Growth Rate
    
    Formula: ((Current - Previous Quarter) / Previous Quarter) × 100
    
    Measures: Sequential growth between quarters
    
    Args:
        current_value: Current quarter value
        previous_quarter_value: Previous quarter value
        
    Returns:
        Growth rate in percentage or None if invalid
    """
    if previous_quarter_value is None or previous_quarter_value == 0:
        return None
    
    if current_value is None:
        return None
        
    return to_percentage(
        safe_divide(current_value - previous_quarter_value, previous_quarter_value)
    )
```

#### Task 3.2: Add TTM Calculation Formulas

```python
def calculate_ttm_sum(
    quarterly_values: List[Optional[float]]
) -> Optional[float]:
    """
    Trailing Twelve Months (TTM) Sum
    
    Formula: Sum of last 4 quarters
    
    Measures: Annualized value from quarterly data
    
    Args:
        quarterly_values: List of 4 quarterly values (most recent first)
        
    Returns:
        TTM sum or None if insufficient data
        
    Examples:
        >>> calculate_ttm_sum([30, 25, 28, 32])
        115.0
        >>> calculate_ttm_sum([30, 25, None, 32])
        None  # Missing data
    """
    if len(quarterly_values) < 4:
        return None
    
    # Take last 4 quarters
    last_4 = quarterly_values[-4:]
    
    # Check for None values
    if any(v is None for v in last_4):
        return None
    
    return sum(last_4)


def calculate_ttm_avg(
    quarterly_values: List[Optional[float]]
) -> Optional[float]:
    """
    Trailing Twelve Months (TTM) Average
    
    Formula: Average of last 4 quarters
    
    Args:
        quarterly_values: List of quarterly values (most recent first)
        
    Returns:
        TTM average or None if insufficient data
    """
    ttm_sum = calculate_ttm_sum(quarterly_values)
    if ttm_sum is None:
        return None
    
    return ttm_sum / 4.0
```

#### Task 3.3: Update Formula Exports

**Update `PROCESSORS/fundamental/formulas/__init__.py`:**

```python
from ._base_formulas import (
    # Existing
    calculate_roe, calculate_roa, calculate_roic,
    calculate_gross_margin, calculate_operating_margin,
    calculate_ebit_margin, calculate_ebitda_margin, calculate_net_margin,
    
    # New
    calculate_yoy_growth, calculate_qoq_growth,
    calculate_ttm_sum, calculate_ttm_avg
)
```

**Deliverable:**
- Updated `_base_formulas.py` with new functions
- Unit tests for new formulas
- Updated `__init__.py` exports

---

### PHASE 4: STANDARDIZE OUTPUT SCHEMA (1 day)

**Goal:** Ensure all calculators output consistent column names that dashboards expect

#### Task 4.1: Create Output Schema Definitions

**File:** `config/schema_registry/domain/fundamental/company_output.json`

```json
{
  "schema_version": "1.0.0",
  "description": "Output schema for company financial calculator",
  "last_updated": "2025-12-11",
  "entity_type": "COMPANY",
  
  "required_columns": [
    "symbol", "report_date", "year", "quarter", "freq_code",
    "net_revenue", "gross_profit", "ebit", "ebitda", "npatmi",
    "gross_margin", "ebit_margin", "ebitda_margin", "net_margin",
    "net_revenue_gr", "gross_profit_gr", "ebit_gr", "ebitda_gr", "npatmi_gr",
    "roe", "roa", "eps",
    "total_assets", "total_equity", "cash", "total_debt",
    "operating_cf", "investment_cf", "financing_cf", "fcf"
  ],
  
  "recommended_columns": [
    "net_revenue_ttm", "npatmi_ttm", "operating_cf_ttm"
  ],
  
  "column_units": {
    "net_revenue": "billions_vnd",
    "gross_profit": "billions_vnd",
    "ebit": "billions_vnd",
    "ebitda": "billions_vnd",
    "npatmi": "billions_vnd",
    "gross_margin": "percentage",
    "ebit_margin": "percentage",
    "ebitda_margin": "percentage",
    "net_margin": "percentage",
    "net_revenue_gr": "percentage",
    "roe": "percentage",
    "roa": "percentage",
    "eps": "vnd_per_share"
  },
  
  "display_formatting": {
    "net_revenue": "format_market_cap",
    "npatmi": "format_market_cap",
    "gross_margin": "format_percentage",
    "net_margin": "format_percentage",
    "roe": "format_percentage",
    "roa": "format_percentage"
  }
}
```

**Similar files for:**
- `bank_output.json`
- `insurance_output.json`
- `security_output.json`

#### Task 4.2: Add Schema Validation to Calculators

**Update `base_financial_calculator.py`:**

```python
from config.schema_registry import SchemaRegistry

class BaseFinancialCalculator:
    def __init__(self, data_path: Optional[str] = None):
        # ... existing initialization
        self.schema_registry = SchemaRegistry()
    
    def validate_output_schema(self, df: pd.DataFrame) -> bool:
        """
        Validate output DataFrame against schema.
        
        Args:
            df: Calculated results DataFrame
            
        Returns:
            True if validation passes
        """
        entity_type = self.get_entity_type()
        
        # Get expected schema from registry
        try:
            expected_schema = self.schema_registry.get_domain_schema(
                'fundamental',
                f'{entity_type.lower()}_output'
            )
        except FileNotFoundError:
            logger.warning(f"No output schema found for {entity_type}, skipping validation")
            return True
        
        # Check required columns
        required_cols = expected_schema.get('required_columns', [])
        missing_cols = set(required_cols) - set(df.columns)
        
        if missing_cols:
            logger.warning(f"Missing required columns: {missing_cols}")
            # Don't fail, just warn
        
        return True
    
    def postprocess_results(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Format and validate output.
        
        Args:
            df: Calculated DataFrame
            
        Returns:
            Formatted DataFrame with standard column names
        """
        result_df = df.copy()
        
        # Rename columns to standard names
        column_mapping = {
            'SECURITY_CODE': 'symbol',
            'REPORT_DATE': 'report_date',
            # Add other mappings as needed
        }
        result_df = result_df.rename(columns=column_mapping)
        
        # Validate schema
        self.validate_output_schema(result_df)
        
        return result_df
```

**Deliverable:**
- Output schema JSON files for all entity types
- Schema validation in calculators
- Consistent column naming

---

### PHASE 5: TESTING & VALIDATION (1-2 days)

**Goal:** Ensure formulas are correct, calculators output expected metrics, and dashboards can display them

#### Task 5.1: Unit Tests for Formulas

**File:** `PROCESSORS/fundamental/formulas/tests/test_base_formulas.py`

```python
import pytest
import numpy as np
from PROCESSORS.fundamental.formulas._base_formulas import (
    calculate_net_margin,
    calculate_gross_margin,
    calculate_yoy_growth,
    calculate_qoq_growth,
    calculate_ttm_sum
)

class TestMarginFormulas:
    """Test margin calculation formulas"""
    
    def test_calculate_net_margin_normal(self):
        """Net margin calculates correctly with positive values"""
        result = calculate_net_margin(100_000_000_000, 1_000_000_000_000)
        assert result == 10.0  # 10%
    
    def test_calculate_net_margin_zero_revenue(self):
        """Net margin returns None for zero revenue"""
        result = calculate_net_margin(100_000_000_000, 0)
        assert result is None
    
    def test_calculate_net_margin_nan_input(self):
        """Net margin handles NaN inputs gracefully"""
        result = calculate_net_margin(np.nan, 1_000_000_000_000)
        assert result is None

class TestGrowthFormulas:
    """Test growth rate calculation formulas"""
    
    def test_calculate_yoy_growth_positive(self):
        """YoY growth calculates correctly for positive growth"""
        result = calculate_yoy_growth(120, 100)
        assert result == 20.0  # 20% growth
    
    def test_calculate_yoy_growth_negative(self):
        """YoY growth calculates correctly for decline"""
        result = calculate_yoy_growth(80, 100)
        assert result == -20.0  # 20% decline
    
    def test_calculate_yoy_growth_zero_previous(self):
        """YoY growth returns None for zero previous value"""
        result = calculate_yoy_growth(100, 0)
        assert result is None

class TestTTMFormulas:
    """Test TTM calculation formulas"""
    
    def test_calculate_ttm_sum_normal(self):
        """TTM sum calculates correctly"""
        result = calculate_ttm_sum([30, 25, 28, 32])
        assert result == 115.0
    
    def test_calculate_ttm_sum_insufficient_data(self):
        """TTM sum returns None for insufficient data"""
        result = calculate_ttm_sum([30, 25])
        assert result is None
```

#### Task 5.2: Integration Tests for Calculators

**File:** `PROCESSORS/fundamental/calculators/tests/test_company_calculator_integration.py`

```python
import pytest
import pandas as pd
from pathlib import Path
from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator

class TestCompanyCalculatorIntegration:
    """Integration tests for CompanyFinancialCalculator"""
    
    def test_calculator_output_has_all_required_metrics(self):
        """Calculator output includes all metrics dashboards need"""
        calc = CompanyFinancialCalculator()
        result = calc.calculate_all_metrics()
        
        required = [
            'net_margin', 'gross_margin', 'ebit_margin', 'ebitda_margin',
            'net_revenue_gr', 'gross_profit_gr', 'roe', 'roa', 'eps'
        ]
        
        for col in required:
            assert col in result.columns, f"Missing required column: {col}"
    
    def test_margins_calculated_correctly(self):
        """Margins are calculated using formula functions"""
        # Create test data
        test_data = pd.DataFrame({
            'SECURITY_CODE': ['VNM'],
            'REPORT_DATE': ['2024-12-31'],
            'CIS_10': [1_000_000_000_000],  # net_revenue
            'CIS_20': [400_000_000_000],    # gross_profit
            'CIS_61': [100_000_000_000],    # npatmi
        })
        
        calc = CompanyFinancialCalculator()
        # ... test calculation logic
```

#### Task 5.3: End-to-End Dashboard Test

**File:** `tests/test_dashboard_metrics_availability.py`

```python
import pytest
import pandas as pd
from pathlib import Path

class TestDashboardMetricsAvailability:
    """Test that dashboard-required metrics are available in output files"""
    
    def test_company_dashboard_metrics_available(self):
        """Company dashboard can find all required metrics"""
        df = pd.read_parquet(
            'DATA/processed/fundamental/company/company_financial_metrics.parquet'
        )
        
        required = [
            'net_margin', 'gross_margin', 'npatmi', 'net_revenue',
            'net_revenue_gr', 'roe', 'roa'
        ]
        
        for col in required:
            assert col in df.columns, f"Missing column for dashboard: {col}"
            # Check that column has some non-null values
            assert df[col].notna().any(), f"Column {col} has no data"
    
    def test_bank_dashboard_metrics_available(self):
        """Bank dashboard can find all required metrics"""
        df = pd.read_parquet(
            'DATA/processed/fundamental/bank/bank_financial_metrics.parquet'
        )
        
        required = ['nim', 'roe', 'roa', 'casa_ratio', 'ldr']
        
        for col in required:
            assert col in df.columns, f"Missing column for dashboard: {col}"
            assert df[col].notna().any(), f"Column {col} has no data"
```

#### Task 5.4: Manual Dashboard Verification

**Action:** Run dashboards and verify metrics display correctly

1. Start Streamlit app: `streamlit run WEBAPP/main_app.py`
2. Navigate to Company Dashboard
3. Select a symbol (e.g., VNM)
4. Verify all metrics display:
   - Margins chart shows `net_margin`, `gross_margin`
   - Growth chart shows `net_revenue_gr`, `npatmi_gr`
   - Profitability shows `roe`, `roa`
5. Repeat for Bank Dashboard

**Deliverable:**
- Unit test suite for formulas
- Integration test suite for calculators
- End-to-end test for dashboard metrics
- Manual verification checklist

---

## 4. IMPLEMENTATION TIMELINE

| Phase | Tasks | Duration | Priority | Dependencies |
|-------|-------|----------|----------|--------------|
| **Phase 1** | Audit & Align | 1-2 days | 🔴 HIGH | None |
| **Phase 2** | Refactor Calculators | 2-3 days | 🔴 HIGH | Phase 1 |
| **Phase 3** | Add Missing Formulas | 1-2 days | 🟡 MEDIUM | Phase 1 |
| **Phase 4** | Standardize Schema | 1 day | 🟡 MEDIUM | Phase 2 |
| **Phase 5** | Testing & Validation | 1-2 days | 🔴 HIGH | Phase 2, 3, 4 |
| **TOTAL** | | **6-10 days** | | |

### Recommended Sequence

**Week 1:**
- **Day 1-2:** Phase 1 (Audit) - Understand current state
- **Day 3-5:** Phase 2 (Refactor) - Update calculators to use formulas

**Week 2:**
- **Day 6-7:** Phase 3 (Add Formulas) - Add growth rate and TTM formulas
- **Day 8:** Phase 4 (Schema) - Standardize output schema
- **Day 9-10:** Phase 5 (Testing) - Comprehensive testing

---

## 5. SUCCESS CRITERIA

### Quantitative Metrics

- ✅ **Zero duplicate calculation logic** - All calculators use formula functions
- ✅ **100% formula coverage** - All dashboard-required metrics have formulas
- ✅ **100% test coverage** - All formulas have unit tests
- ✅ **Consistent column names** - All calculators output same column names
- ✅ **All dashboards functional** - No missing metrics errors

### Qualitative Metrics

- ✅ **Code maintainability** - Single source of truth for calculations
- ✅ **Consistency** - Same calculation logic across all entity types
- ✅ **Reliability** - Formulas handle edge cases (None, zero, NaN)
- ✅ **Documentation** - All formulas have clear docstrings
- ✅ **Performance** - No performance regression from refactoring

---

## 6. RISKS & MITIGATION

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Breaking existing dashboards** | HIGH | MEDIUM | Comprehensive testing before deployment, keep backup of current output files |
| **Performance regression** | MEDIUM | LOW | Benchmark before/after, optimize formula functions if needed |
| **Missing edge cases in formulas** | MEDIUM | MEDIUM | Extensive unit tests, test with real data |
| **Inconsistent data types** | MEDIUM | MEDIUM | Schema validation, type checking in formulas |
| **Dashboard expects different format** | HIGH | LOW | Phase 1 audit will catch this early |

---

## 7. ROLLBACK PLAN

If issues are discovered after deployment:

1. **Immediate:** Revert calculator changes to previous version
2. **Short-term:** Keep both old and new calculation methods, use feature flag
3. **Long-term:** Fix issues and redeploy

**Backup Strategy:**
- Git commit before starting each phase
- Keep backup of current output parquet files
- Document all changes in commit messages

---

## 8. DOCUMENTATION REQUIREMENTS

### Code Documentation

- All formula functions must have docstrings with:
  - Formula definition
  - Interpretation guidelines
  - Example usage
  - Edge case handling

### User Documentation

- Update `CLAUDE.md` with new formula locations
- Document calculator usage patterns
- Add examples of using formulas directly

### API Documentation

- Document all available formulas in `PROCESSORS/fundamental/formulas/README.md`
- Document calculator output schema
- Create dashboard metrics reference guide

---

## 9. APPENDIX

### A. Formula Function Signatures

```python
# Profitability Ratios
calculate_roe(net_income: Optional[float], equity: Optional[float]) -> Optional[float]
calculate_roa(net_income: Optional[float], total_assets: Optional[float]) -> Optional[float]
calculate_roic(nopat: Optional[float], invested_capital: Optional[float]) -> Optional[float]

# Margins
calculate_gross_margin(gross_profit: Optional[float], revenue: Optional[float]) -> Optional[float]
calculate_operating_margin(operating_profit: Optional[float], revenue: Optional[float]) -> Optional[float]
calculate_ebit_margin(ebit: Optional[float], revenue: Optional[float]) -> Optional[float]
calculate_ebitda_margin(ebitda: Optional[float], revenue: Optional[float]) -> Optional[float]
calculate_net_margin(net_income: Optional[float], revenue: Optional[float]) -> Optional[float]

# Growth Rates (NEW)
calculate_yoy_growth(current_value: Optional[float], previous_year_value: Optional[float]) -> Optional[float]
calculate_qoq_growth(current_value: Optional[float], previous_quarter_value: Optional[float]) -> Optional[float]

# TTM Calculations (NEW)
calculate_ttm_sum(quarterly_values: List[Optional[float]]) -> Optional[float]
calculate_ttm_avg(quarterly_values: List[Optional[float]]) -> Optional[float]
```

### B. Calculator Output Column Reference

**Company Calculator Output:**
- `symbol`, `report_date`, `year`, `quarter`
- `net_revenue`, `gross_profit`, `ebit`, `ebitda`, `npatmi`
- `gross_margin`, `ebit_margin`, `ebitda_margin`, `net_margin`
- `net_revenue_gr`, `gross_profit_gr`, `ebit_gr`, `ebitda_gr`, `npatmi_gr`
- `roe`, `roa`, `eps`
- `total_assets`, `total_equity`, `cash`, `total_debt`
- `operating_cf`, `investment_cf`, `financing_cf`, `fcf`

**Bank Calculator Output:**
- `symbol`, `report_date`, `year`, `quarter`
- `net_interest_income`, `net_profit`
- `nim`, `roe`, `roa`
- `casa_ratio`, `ldr`, `npl_ratio`, `cir`
- `total_assets`, `total_equity`

### C. Dashboard Metrics Mapping

**Company Dashboard (`company_dashboard_pyecharts.py`):**
- Margins Tab: `gross_margin`, `ebit_margin`, `ebitda_margin`, `net_margin`
- Growth Tab: `net_revenue_gr`, `gross_profit_gr`, `ebit_gr`, `ebitda_gr`, `npatmi_gr`
- Profitability Tab: `roe`, `roa`, `eps`
- Financial Tables Tab: All income statement and balance sheet metrics

**Bank Dashboard (`bank_dashboard.py`):**
- Overview: `nim`, `roe`, `roa`, `net_profit`
- Margins: `nim`, `net_margin`
- Asset Quality: `npl_ratio`, `ldr`
- Growth: `net_interest_income_gr`, `net_profit_gr`

---

## 10. CONCLUSION

This plan provides a systematic approach to refactoring financial calculation formulas to ensure consistency between the formulas layer, calculators layer, and dashboard layer. By following this plan:

1. **Eliminates duplication** - Single source of truth for all calculations
2. **Ensures consistency** - Same formulas used everywhere
3. **Improves maintainability** - Change formula once, affects all calculators
4. **Enables testing** - Pure functions are easy to test
5. **Guarantees dashboard compatibility** - All required metrics are calculated

**Next Steps:**
1. Review and approve this plan
2. Start with Phase 1 (Audit) to understand current state
3. Proceed with implementation following the phased approach
4. Test thoroughly before deploying to production

---

**Plan Status:** READY FOR REVIEW  
**Approval Required:** Yes  
**Estimated Start Date:** TBD  
**Estimated Completion Date:** TBD

---

*This plan is a living document and will be updated as implementation progresses.*






