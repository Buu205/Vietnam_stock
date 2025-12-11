# FUNDAMENTAL CALCULATORS & FORMULAS OPTIMIZATION PLAN
## Vietnamese Stock Market Dashboard - Financial Calculation Engine

---

**Plan Created:** 2025-12-11
**Author:** Claude Code (Senior Developer + Senior Finance Analyst)
**Priority:** CRITICAL - Core calculation engine for all financial metrics
**Estimated Effort:** 7-10 days
**Current Status:** 70% Complete, needs bug fixes and consolidation

---

## EXECUTIVE SUMMARY

The fundamental calculator system uses clean inheritance patterns but has accumulated technical debt through code duplication, missing implementations, and inconsistent patterns. This plan fixes critical bugs, consolidates formula logic, completes missing entity-specific implementations, and establishes a clean, maintainable architecture.

**Key Goals:**
1. Fix critical bugs (missing logger, typos, broken tests)
2. Consolidate formula duplication (single source of truth)
3. Complete missing implementations (insurance/security formulas)
4. Standardize output schema integration
5. Add comprehensive error handling and validation
6. Create unified testing framework

---

## 1. CURRENT STATE ANALYSIS

### 1.1 Code Organization

```
PROCESSORS/fundamental/
├── calculators/                         (2,554 lines, 8 files)
│   ├── base_financial_calculator.py    (453 lines - Abstract base)
│   ├── company_calculator.py           (380 lines - COMPANY entity)
│   ├── bank_calculator.py              (472 lines - BANK entity)
│   ├── insurance_calculator.py         (303 lines - INSURANCE entity)
│   ├── security_calculator.py          (324 lines - SECURITY entity)
│   ├── __init__.py                     (58 lines - Package exports)
│   ├── calculator_integration_test.py  (253 lines - Tests)
│   └── calculator_usage_example.py     (311 lines - Examples)
│
├── formulas/                            (2,557 lines, 5 files)
│   ├── _base_formulas.py               (19 KB - 50+ universal formulas)
│   ├── company_formulas.py             (11 KB - Company-specific)
│   ├── bank_formulas.py                (9 KB - Bank-specific)
│   ├── utils.py                        (8 KB - Helper functions)
│   └── __init__.py
│
└── sector_fa_analyzer.py                (Top-level orchestrator)
```

### 1.2 Architecture Summary

**Design Pattern:** Template Method (well-implemented)
- Base class: `BaseFinancialCalculator` (abstract)
- Subclasses: 4 entity types (COMPANY, BANK, INSURANCE, SECURITY)
- Formula library: Pure functions for reusability

**Entity Types Supported:**
| Entity | Metric Prefixes | Calculators | Output Columns | Status |
|--------|----------------|-------------|----------------|--------|
| COMPANY | CIS_, CBS_, CCFI_ | ✅ Complete | 40+ | ✅ Working |
| BANK | BIS_, BBS_, BNOT_ | ✅ Complete | 35+ | ✅ Working |
| INSURANCE | IIS_, IBS_ | ⚠️ Has typos | 30+ | ⚠️ Needs fixes |
| SECURITY | SIS_, SBS_ | ✅ Complete | 28+ | ✅ Working |

### 1.3 Data Flow Pipeline

```
Raw Data (Parquet)
    ↓
load_data() → Long format DataFrame
    ↓
preprocess_data() → Filter by FREQ_CODE='Q', entity type
    ↓
pivot_data() → Wide format (metrics as columns)
    ↓
Entity-Specific Calculations
    ├── Income Statement metrics
    ├── Balance Sheet metrics
    ├── Cash Flow metrics
    ├── Profitability ratios
    ├── Growth rates
    └── TTM calculations
    ↓
postprocess_results() → Select columns, rename, format
    ↓
Output (Parquet) → DATA/processed/fundamental/[entity]/
```

---

## 2. CRITICAL ISSUES & BUGS

### 2.1 Priority 1: BLOCKER Bugs (Must Fix Immediately)

| Issue | File | Line | Severity | Impact |
|-------|------|------|----------|--------|
| **Missing logger import** | `company_calculator.py` | 288 | 🔴 CRITICAL | Runtime error if validation fails |
| **Method name typo** | `insurance_calculator.py` | 51, 158 | 🔴 CRITICAL | Method execution fails |
| **Broken test imports** | `calculator_integration_test.py` | Multiple | 🔴 CRITICAL | Tests cannot run |

#### Issue 2.1.1: Missing Logger in CompanyCalculator

**File:** `PROCESSORS/fundamental/calculators/company_calculator.py`

**Problem:**
```python
# Line 288 - logger is used but never imported/defined
def validate_data(self, df: pd.DataFrame) -> bool:
    if missing_metrics:
        logger.warning(f"Missing COMPANY metrics: {missing_metrics}")  # ❌ NameError
```

**Solution:**
```python
# Add at top of file (after other imports)
import logging
logger = logging.getLogger(__name__)
```

#### Issue 2.1.2: Typo in InsuranceCalculator

**File:** `PROCESSORS/fundamental/calculators/insurance_calculator.py`

**Problem:**
```python
# Line 51 - Missing underscore in method name
'investment': self.calculateinvestment_performance,  # ❌ Wrong

# Line 158 - Method definition also has typo
def calculateinvestment_performance(self, df):  # ❌ Wrong
```

**Solution:**
```python
# Line 51
'investment': self.calculate_investment_performance,  # ✅ Correct

# Line 158
def calculate_investment_performance(self, df):  # ✅ Correct
```

#### Issue 2.1.3: Broken Test Imports

**File:** `PROCESSORS/fundamental/calculators/calculator_integration_test.py`

**Problem:**
```python
# Imports reference old class names
from PROCESSORS.fundamental.calculators.company_financial_calculator import CompanyFinancialCalculator
# ❌ File is named company_calculator.py, not company_financial_calculator.py
```

**Solution:**
```python
# Update all imports
from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator
from PROCESSORS.fundamental.calculators.bank_calculator import BankFinancialCalculator
from PROCESSORS.fundamental.calculators.insurance_calculator import InsuranceFinancialCalculator
from PROCESSORS.fundamental.calculators.security_calculator import SecurityFinancialCalculator
```

### 2.2 Priority 2: Code Quality Issues

| Issue | Files | Impact | Priority |
|-------|-------|--------|----------|
| **Formula duplication** | `_base_formulas.py`, `company_formulas.py`, `bank_formulas.py` | Code maintenance burden | 🟡 HIGH |
| **Missing formula files** | `insurance_formulas.py`, `security_formulas.py` | Inconsistent pattern | 🟡 MEDIUM |
| **Unused sys import** | `base_financial_calculator.py` line 21 | Code cleanliness | 🟢 LOW |
| **Deprecated paths in examples** | `calculator_usage_example.py` | Misleading docs | 🟡 MEDIUM |

---

## 3. OPTIMIZATION PHASES

### PHASE 1: BUG FIXES & CRITICAL PATCHES (1 day)

**Goal:** Fix all blocker bugs to make system stable

#### Phase 1.1: Fix CompanyCalculator Logger

**File:** `company_calculator.py`

**Changes:**
```python
# Add after line 22 (after other imports)
import logging

logger = logging.getLogger(__name__)
```

**Test:**
```python
# Trigger validation to test logger
calc = CompanyFinancialCalculator()
df = pd.DataFrame()  # Empty dataframe
result = calc.validate_data(df)  # Should log warning without error
```

#### Phase 1.2: Fix InsuranceCalculator Typo

**File:** `insurance_calculator.py`

**Changes:**
```python
# Line 51 - Fix dictionary entry
def get_entity_specific_calculations(self) -> Dict[str, callable]:
    return {
        'income_statement': self.calculate_income_statement,
        'balance_sheet': self.calculate_balance_sheet,
        'underwriting': self.calculate_underwriting_metrics,
        'investment': self.calculate_investment_performance,  # ✅ Fixed
        'ratios': self.calculate_insurance_ratios,
    }

# Line 158 - Fix method name
def calculate_investment_performance(self, df: pd.DataFrame) -> pd.DataFrame:  # ✅ Fixed
    """Calculate investment performance metrics for INSURANCE entities."""
    # ... existing implementation
```

#### Phase 1.3: Fix Test File Imports

**File:** `calculator_integration_test.py`

**Changes:**
```python
# Update imports (lines 10-15)
from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator
from PROCESSORS.fundamental.calculators.bank_calculator import BankFinancialCalculator
from PROCESSORS.fundamental.calculators.insurance_calculator import InsuranceFinancialCalculator
from PROCESSORS.fundamental.calculators.security_calculator import SecurityFinancialCalculator
from PROCESSORS.fundamental.calculators.base_financial_calculator import BaseFinancialCalculator
```

**Run tests:**
```bash
cd /Users/buuphan/Dev/Vietnam_dashboard
python -m pytest PROCESSORS/fundamental/calculators/calculator_integration_test.py -v
```

#### Phase 1.4: Remove Unused Imports

**File:** `base_financial_calculator.py`

**Changes:**
```python
# Line 21 - Remove unused sys import
# import sys  # ❌ Remove this line
```

---

### PHASE 2: FORMULA CONSOLIDATION (2 days)

**Goal:** Create single source of truth for all financial formulas

#### Phase 2.1: Audit Formula Duplication

**Current State:**

| Formula | _base_formulas.py | company_formulas.py | bank_formulas.py | Status |
|---------|-------------------|---------------------|------------------|--------|
| `calculate_roe()` | ✅ Yes | ✅ Yes (duplicate) | ❌ No | 🔴 Duplicate |
| `calculate_roa()` | ✅ Yes | ✅ Yes (duplicate) | ❌ No | 🔴 Duplicate |
| `calculate_gross_margin()` | ✅ Yes | ✅ Yes (duplicate) | ❌ No | 🔴 Duplicate |
| `calculate_nim()` | ❌ No | ❌ No | ✅ Yes (unique) | ✅ Unique |
| `calculate_casa_ratio()` | ❌ No | ❌ No | ✅ Yes (unique) | ✅ Unique |

**Total Functions:**
- `_base_formulas.py`: 24 universal functions
- `company_formulas.py`: 9 functions (5 duplicates, 4 unique)
- `bank_formulas.py`: 8 functions (all unique)
- **Duplication:** ~20% (5 out of 24 base functions duplicated)

#### Phase 2.2: Consolidation Strategy

**Decision:** Keep `_base_formulas.py` as single source of truth

**Actions:**

1. **Move unique formulas TO _base_formulas.py**
   - Company-specific: Asset turnover, inventory turnover (if universal)
   - Bank-specific: Keep in bank_formulas.py (too specialized)

2. **Delete duplicates FROM entity-specific files**
   - Remove ROE, ROA, gross_margin from company_formulas.py
   - Update imports to use _base_formulas instead

3. **Keep entity-specific formulas**
   - `bank_formulas.py`: NIM, CASA ratio, LDR, NPL ratio (banking only)
   - `insurance_formulas.py` (NEW): Combined ratio, loss ratio, solvency
   - `security_formulas.py` (NEW): Revenue composition, CAD ratio

**Implementation:**

**Step 1:** Update `company_formulas.py` - Remove duplicates

```python
# BEFORE (9 functions)
def calculate_roe(net_profit, total_equity):  # Duplicate
def calculate_roa(net_income, total_assets):  # Duplicate
def calculate_gross_margin(...):  # Duplicate
def calculate_asset_turnover(...):  # Unique - KEEP
def calculate_inventory_turnover(...):  # Unique - KEEP

# AFTER (4 functions only)
# Import universals from base
from PROCESSORS.fundamental.formulas._base_formulas import (
    calculate_roe,
    calculate_roa,
    calculate_gross_margin,
    calculate_operating_margin,
    calculate_net_margin
)

# Keep only company-specific
def calculate_asset_turnover(revenue, total_assets):
    """Company-specific: Asset turnover ratio"""
    # Implementation

def calculate_inventory_turnover(cogs, avg_inventory):
    """Company-specific: Inventory turnover"""
    # Implementation

def calculate_receivables_turnover(revenue, avg_receivables):
    """Company-specific: Receivables turnover"""
    # Implementation

def calculate_working_capital_turnover(revenue, working_capital):
    """Company-specific: Working capital efficiency"""
    # Implementation
```

**Step 2:** Update calculators to import from correct location

```python
# In company_calculator.py
from PROCESSORS.fundamental.formulas._base_formulas import (
    calculate_roe, calculate_roa, calculate_gross_margin
)
from PROCESSORS.fundamental.formulas.company_formulas import (
    calculate_asset_turnover, calculate_inventory_turnover
)
```

#### Phase 2.3: Create Missing Formula Files

**File:** `PROCESSORS/fundamental/formulas/insurance_formulas.py`

**Content:**
```python
#!/usr/bin/env python3
"""
Insurance-Specific Financial Formulas
======================================

Pure functions for insurance company metrics:
- Combined ratio (loss ratio + expense ratio)
- Loss ratio
- Expense ratio
- Claims ratio
- Solvency margin ratio
- Investment yield

Author: Claude Code
Date: 2025-12-11
"""

from typing import Optional
import pandas as pd
from PROCESSORS.fundamental.formulas.utils import safe_divide


def calculate_loss_ratio(
    claims_paid: float,
    earned_premiums: float
) -> Optional[float]:
    """
    Calculate loss ratio for insurance companies

    Loss Ratio = Claims Paid / Earned Premiums × 100

    Lower is better. Typical range: 50-70%

    Args:
        claims_paid: Total claims paid in period (VND)
        earned_premiums: Total earned premiums (VND)

    Returns:
        Loss ratio as percentage, or None if invalid

    Example:
        >>> calculate_loss_ratio(150_000_000_000, 250_000_000_000)
        60.0
    """
    result = safe_divide(claims_paid, earned_premiums)
    return round(result * 100, 2) if result is not None else None


def calculate_expense_ratio(
    operating_expenses: float,
    earned_premiums: float
) -> Optional[float]:
    """
    Calculate expense ratio for insurance companies

    Expense Ratio = Operating Expenses / Earned Premiums × 100

    Lower is better. Typical range: 20-30%

    Args:
        operating_expenses: Total operating expenses (VND)
        earned_premiums: Total earned premiums (VND)

    Returns:
        Expense ratio as percentage, or None if invalid
    """
    result = safe_divide(operating_expenses, earned_premiums)
    return round(result * 100, 2) if result is not None else None


def calculate_combined_ratio(
    loss_ratio: float,
    expense_ratio: float
) -> Optional[float]:
    """
    Calculate combined ratio for insurance companies

    Combined Ratio = Loss Ratio + Expense Ratio

    < 100% = Underwriting profit
    > 100% = Underwriting loss

    Args:
        loss_ratio: Loss ratio (percentage)
        expense_ratio: Expense ratio (percentage)

    Returns:
        Combined ratio as percentage

    Example:
        >>> calculate_combined_ratio(60.0, 25.0)
        85.0  # Underwriting profit
    """
    if pd.isna(loss_ratio) or pd.isna(expense_ratio):
        return None

    return round(loss_ratio + expense_ratio, 2)


def calculate_claims_ratio(
    total_claims: float,
    total_premiums: float
) -> Optional[float]:
    """
    Calculate claims ratio (similar to loss ratio)

    Claims Ratio = Total Claims / Total Premiums × 100

    Args:
        total_claims: Total claims in period (VND)
        total_premiums: Total premiums collected (VND)

    Returns:
        Claims ratio as percentage
    """
    result = safe_divide(total_claims, total_premiums)
    return round(result * 100, 2) if result is not None else None


def calculate_solvency_margin_ratio(
    available_capital: float,
    required_capital: float
) -> Optional[float]:
    """
    Calculate solvency margin ratio for insurance regulatory compliance

    Solvency Margin Ratio = Available Capital / Required Capital × 100

    Regulatory minimum in Vietnam: 100%
    Healthy range: > 150%

    Args:
        available_capital: Total available capital (VND)
        required_capital: Regulatory required capital (VND)

    Returns:
        Solvency margin ratio as percentage

    Example:
        >>> calculate_solvency_margin_ratio(500_000_000_000, 300_000_000_000)
        166.67  # Healthy solvency
    """
    result = safe_divide(available_capital, required_capital)
    return round(result * 100, 2) if result is not None else None


def calculate_investment_yield(
    investment_income: float,
    average_invested_assets: float
) -> Optional[float]:
    """
    Calculate investment yield for insurance investment portfolio

    Investment Yield = Investment Income / Average Invested Assets × 100

    Args:
        investment_income: Total investment income (interest, dividends, gains)
        average_invested_assets: Average value of invested assets

    Returns:
        Investment yield as percentage
    """
    result = safe_divide(investment_income, average_invested_assets)
    return round(result * 100, 2) if result is not None else None


def calculate_retention_ratio(
    premiums_retained: float,
    gross_premiums: float
) -> Optional[float]:
    """
    Calculate premium retention ratio (how much risk is retained vs reinsured)

    Retention Ratio = Premiums Retained / Gross Premiums × 100

    Higher = More risk retained

    Args:
        premiums_retained: Premiums retained after reinsurance (VND)
        gross_premiums: Total gross premiums before reinsurance (VND)

    Returns:
        Retention ratio as percentage
    """
    result = safe_divide(premiums_retained, gross_premiums)
    return round(result * 100, 2) if result is not None else None
```

**File:** `PROCESSORS/fundamental/formulas/security_formulas.py`

**Content:**
```python
#!/usr/bin/env python3
"""
Security/Brokerage-Specific Financial Formulas
===============================================

Pure functions for securities firm metrics:
- Revenue composition (brokerage, proprietary trading, etc.)
- Capital adequacy ratio (CAD)
- Trading leverage
- Client asset ratio

Author: Claude Code
Date: 2025-12-11
"""

from typing import Optional
import pandas as pd
from PROCESSORS.fundamental.formulas.utils import safe_divide


def calculate_brokerage_revenue_ratio(
    brokerage_revenue: float,
    total_revenue: float
) -> Optional[float]:
    """
    Calculate percentage of revenue from brokerage commissions

    Brokerage Revenue Ratio = Brokerage Revenue / Total Revenue × 100

    Args:
        brokerage_revenue: Revenue from brokerage commissions (VND)
        total_revenue: Total operating revenue (VND)

    Returns:
        Ratio as percentage
    """
    result = safe_divide(brokerage_revenue, total_revenue)
    return round(result * 100, 2) if result is not None else None


def calculate_proprietary_trading_ratio(
    prop_trading_revenue: float,
    total_revenue: float
) -> Optional[float]:
    """
    Calculate percentage of revenue from proprietary trading

    Prop Trading Ratio = Proprietary Trading Revenue / Total Revenue × 100

    Higher = More reliant on market performance

    Args:
        prop_trading_revenue: Revenue from proprietary trading (VND)
        total_revenue: Total operating revenue (VND)

    Returns:
        Ratio as percentage
    """
    result = safe_divide(prop_trading_revenue, total_revenue)
    return round(result * 100, 2) if result is not None else None


def calculate_capital_adequacy_ratio(
    net_capital: float,
    total_risk_requirement: float
) -> Optional[float]:
    """
    Calculate Capital Adequacy Ratio (CAD) for securities firms

    CAD = Net Capital / Total Risk Requirement × 100

    Regulatory minimum in Vietnam: 140%

    Args:
        net_capital: Net regulatory capital (VND)
        total_risk_requirement: Total risk capital requirement (VND)

    Returns:
        CAD as percentage

    Example:
        >>> calculate_capital_adequacy_ratio(500_000_000_000, 300_000_000_000)
        166.67  # Above regulatory minimum
    """
    result = safe_divide(net_capital, total_risk_requirement)
    return round(result * 100, 2) if result is not None else None


def calculate_trading_leverage(
    margin_loan: float,
    equity: float
) -> Optional[float]:
    """
    Calculate trading leverage for securities firms

    Trading Leverage = Margin Loan / Equity

    Higher = More leverage risk

    Args:
        margin_loan: Total margin lending to clients (VND)
        equity: Total equity (VND)

    Returns:
        Leverage ratio
    """
    result = safe_divide(margin_loan, equity)
    return round(result, 2) if result is not None else None


def calculate_client_asset_ratio(
    client_assets_under_management: float,
    total_assets: float
) -> Optional[float]:
    """
    Calculate ratio of client assets under management

    Client Asset Ratio = Client AUM / Total Assets × 100

    Args:
        client_assets_under_management: Total client assets managed (VND)
        total_assets: Total firm assets (VND)

    Returns:
        Ratio as percentage
    """
    result = safe_divide(client_assets_under_management, total_assets)
    return round(result * 100, 2) if result is not None else None


def calculate_margin_loan_quality(
    performing_margin_loans: float,
    total_margin_loans: float
) -> Optional[float]:
    """
    Calculate quality of margin loan portfolio

    Margin Loan Quality = Performing Loans / Total Margin Loans × 100

    Args:
        performing_margin_loans: Non-overdue margin loans (VND)
        total_margin_loans: Total margin loans outstanding (VND)

    Returns:
        Quality ratio as percentage (higher is better)
    """
    result = safe_divide(performing_margin_loans, total_margin_loans)
    return round(result * 100, 2) if result is not None else None
```

---

### PHASE 3: SCHEMA INTEGRATION (2 days)

**Goal:** Integrate SchemaRegistry for output validation and formatting

#### Phase 3.1: Add Schema Validation to BaseFinancialCalculator

**File:** `base_financial_calculator.py`

**Add import:**
```python
from config.schema_registry import SchemaRegistry
```

**Add to __init__:**
```python
def __init__(self, data_path: Optional[str] = None):
    # ... existing initialization
    self.schema_registry = SchemaRegistry()
```

**Add validation method:**
```python
def validate_output_schema(self, df: pd.DataFrame) -> bool:
    """
    Validate output DataFrame against schema

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
        logger.error(f"Missing required columns: {missing_cols}")
        return False

    # Check data types
    for col, expected_type in expected_schema.get('column_types', {}).items():
        if col in df.columns:
            actual_type = df[col].dtype
            # Type validation logic here

    return True
```

#### Phase 3.2: Create Output Schemas

**Create 4 new schema files:**

**File:** `config/schema_registry/domain/fundamental/company_output.json`

```json
{
  "schema_version": "1.0.0",
  "description": "Output schema for company financial calculator",
  "last_updated": "2025-12-11",

  "entity_type": "COMPANY",

  "required_columns": [
    "symbol", "report_date", "year", "quarter", "freq_code",
    "net_revenue", "npatmi", "total_assets", "total_equity",
    "roe", "roa", "eps"
  ],

  "recommended_columns": [
    "gross_profit", "ebit", "ebitda",
    "gross_profit_margin", "net_margin",
    "net_revenue_growth", "npatmi_growth",
    "cash", "debt_to_equity"
  ],

  "column_types": {
    "symbol": "string",
    "report_date": "date",
    "year": "integer",
    "quarter": "integer",
    "freq_code": "string",
    "net_revenue": "float",
    "npatmi": "float",
    "roe": "float",
    "roa": "float",
    "eps": "float"
  },

  "units": {
    "net_revenue": "billions_vnd",
    "npatmi": "billions_vnd",
    "total_assets": "billions_vnd",
    "roe": "percentage",
    "roa": "percentage",
    "eps": "vnd_per_share"
  },

  "display_formatting": {
    "net_revenue": "format_market_cap",
    "npatmi": "format_market_cap",
    "roe": "format_percentage",
    "roa": "format_percentage",
    "eps": "format_price"
  }
}
```

**Similar files for:**
- `bank_output.json`
- `insurance_output.json`
- `security_output.json`

---

### PHASE 4: ERROR HANDLING & LOGGING (1 day)

**Goal:** Add comprehensive error handling and structured logging

#### Phase 4.1: Add Error Handling to Calculation Methods

**Pattern to follow:**

```python
def calculate_income_statement(self, df: pd.DataFrame) -> pd.DataFrame:
    """Calculate income statement metrics with error handling"""
    try:
        result_df = df.copy()

        # Calculation logic with validation
        if 'CIS_10' not in df.columns:
            logger.warning("CIS_10 (net_revenue) missing, setting to NaN")
            result_df['net_revenue'] = np.nan
        else:
            result_df['net_revenue'] = self.convert_to_billions(df['CIS_10'])

        # Continue with other metrics...

        return result_df

    except Exception as e:
        logger.error(f"Error in calculate_income_statement: {str(e)}", exc_info=True)
        # Return DataFrame with NaN values rather than failing
        return self._create_empty_result_df(df)

def _create_empty_result_df(self, df: pd.DataFrame) -> pd.DataFrame:
    """Create result DataFrame with NaN values if calculation fails"""
    result_df = df[['SECURITY_CODE', 'REPORT_DATE']].copy()
    # Add NaN columns for all expected metrics
    return result_df
```

#### Phase 4.2: Add Structured Logging

**Create logging configuration:**

**File:** `PROCESSORS/fundamental/calculators/logging_config.py`

```python
import logging
import sys
from pathlib import Path

def setup_calculator_logging(log_level=logging.INFO):
    """Setup structured logging for calculators"""

    # Create logs directory
    log_dir = Path(__file__).parent.parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(levelname)s | %(message)s'
    )

    # File handler (detailed logs)
    file_handler = logging.FileHandler(
        log_dir / "fundamental_calculators.log",
        mode='a',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    # Console handler (simple logs)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)

    # Configure root logger for PROCESSORS.fundamental
    root_logger = logging.getLogger('PROCESSORS.fundamental')
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger
```

**Use in calculators:**

```python
# In base_financial_calculator.py
from PROCESSORS.fundamental.calculators.logging_config import setup_calculator_logging

# At module level
setup_calculator_logging()
logger = logging.getLogger(__name__)
```

---

### PHASE 5: COMPREHENSIVE TESTING (2 days)

**Goal:** Create complete test suite for all calculators and formulas

#### Phase 5.1: Unit Tests for Formula Functions

**File:** `PROCESSORS/fundamental/formulas/tests/test_base_formulas.py`

```python
import pytest
import pandas as pd
import numpy as np
from PROCESSORS.fundamental.formulas._base_formulas import (
    calculate_roe, calculate_roa, calculate_gross_margin,
    calculate_debt_to_equity, calculate_current_ratio
)

class TestProfitabilityRatios:
    """Test profitability ratio calculations"""

    def test_roe_normal_case(self):
        """ROE calculates correctly with positive values"""
        result = calculate_roe(net_income=100_000_000_000, equity=500_000_000_000)
        assert result == 20.0  # 20%

    def test_roe_negative_equity(self):
        """ROE returns None for negative equity"""
        result = calculate_roe(net_income=100_000_000_000, equity=-50_000_000_000)
        assert result is None

    def test_roe_zero_equity(self):
        """ROE returns None for zero equity"""
        result = calculate_roe(net_income=100_000_000_000, equity=0)
        assert result is None

    def test_roe_nan_input(self):
        """ROE handles NaN inputs gracefully"""
        result = calculate_roe(net_income=np.nan, equity=500_000_000_000)
        assert result is None

class TestLeverageRatios:
    """Test leverage ratio calculations"""

    def test_debt_to_equity_normal(self):
        """Debt-to-equity calculates correctly"""
        result = calculate_debt_to_equity(total_debt=300_000_000_000, equity=200_000_000_000)
        assert result == 1.5

    def test_debt_to_equity_zero_equity(self):
        """Returns None for zero equity"""
        result = calculate_debt_to_equity(total_debt=100_000_000_000, equity=0)
        assert result is None

# Run with: pytest test_base_formulas.py -v
```

#### Phase 5.2: Integration Tests for Calculators

**File:** `PROCESSORS/fundamental/calculators/tests/test_company_calculator_integration.py`

```python
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from PROCESSORS.fundamental.calculators.company_calculator import CompanyFinancialCalculator

@pytest.fixture
def sample_company_data():
    """Create sample company financial data"""
    return pd.DataFrame({
        'SECURITY_CODE': ['VNM'] * 4,
        'REPORT_DATE': ['2024-03-31', '2024-06-30', '2024-09-30', '2024-12-31'],
        'METRIC_CODE': ['CIS_10'] * 4,
        'METRIC_VALUE': [5_000_000_000_000, 5_500_000_000_000, 6_000_000_000_000, 6_500_000_000_000],
        'FREQ_CODE': ['Q'] * 4,
        'YEAR': [2024] * 4,
        'QUARTER': [1, 2, 3, 4]
    })

class TestCompanyCalculatorIntegration:
    """Integration tests for CompanyFinancialCalculator"""

    def test_calculator_initialization(self):
        """Calculator initializes without errors"""
        calc = CompanyFinancialCalculator()
        assert calc.get_entity_type() == "COMPANY"
        assert 'CIS_' in calc.get_metric_prefixes()

    def test_data_loading_and_preprocessing(self, sample_company_data, tmp_path):
        """Data loads and preprocesses correctly"""
        # Save sample data
        data_file = tmp_path / "company_test.parquet"
        sample_company_data.to_parquet(data_file)

        # Initialize calculator with test data
        calc = CompanyFinancialCalculator(data_path=str(data_file))
        raw_data = calc.load_data()

        assert not raw_data.empty
        assert 'SECURITY_CODE' in raw_data.columns
        assert 'METRIC_CODE' in raw_data.columns

    def test_pivot_operation(self, sample_company_data):
        """Data pivots correctly to wide format"""
        calc = CompanyFinancialCalculator()

        # Mock load_data to return sample data
        calc._raw_data = sample_company_data

        pivoted = calc.pivot_data(sample_company_data)

        assert 'CIS_10' in pivoted.columns
        assert len(pivoted) == 4  # 4 quarters

    def test_full_calculation_pipeline(self, sample_company_data, tmp_path):
        """Full pipeline runs without errors"""
        data_file = tmp_path / "company_test.parquet"
        sample_company_data.to_parquet(data_file)

        calc = CompanyFinancialCalculator(data_path=str(data_file))

        # This should run full pipeline
        result = calc.calculate_all_metrics()

        assert not result.empty
        assert 'symbol' in result.columns  # Renamed from SECURITY_CODE
        assert 'report_date' in result.columns

# Run with: pytest test_company_calculator_integration.py -v
```

#### Phase 5.3: End-to-End Tests

**File:** `PROCESSORS/fundamental/calculators/tests/test_e2e_calculation_flow.py`

```python
import pytest
from pathlib import Path
from PROCESSORS.fundamental.calculators import (
    CompanyFinancialCalculator,
    BankFinancialCalculator,
    InsuranceFinancialCalculator,
    SecurityFinancialCalculator
)

class TestEndToEndFlow:
    """End-to-end tests for all entity types"""

    @pytest.mark.parametrize("calc_class,entity_type,metric_prefix", [
        (CompanyFinancialCalculator, "COMPANY", "CIS_"),
        (BankFinancialCalculator, "BANK", "BIS_"),
        (InsuranceFinancialCalculator, "INSURANCE", "IIS_"),
        (SecurityFinancialCalculator, "SECURITY", "SIS_"),
    ])
    def test_all_calculators_initialize(self, calc_class, entity_type, metric_prefix):
        """All calculators initialize correctly"""
        calc = calc_class()
        assert calc.get_entity_type() == entity_type
        assert metric_prefix in calc.get_metric_prefixes()

    def test_output_files_created(self):
        """Verify output parquet files exist"""
        output_dir = Path("/Users/buuphan/Dev/Vietnam_dashboard/DATA/processed/fundamental")

        expected_files = [
            "company/company_financial_metrics.parquet",
            "bank/bank_financial_metrics.parquet",
            "insurance/insurance_financial_metrics.parquet",
            "security/security_financial_metrics.parquet"
        ]

        for file_path in expected_files:
            full_path = output_dir / file_path
            assert full_path.exists(), f"Output file not found: {full_path}"
```

---

### PHASE 6: DOCUMENTATION & EXAMPLES (1 day)

**Goal:** Create comprehensive documentation and usage examples

#### Phase 6.1: Update Calculator Usage Examples

**File:** `calculator_usage_example.py`

**Fix paths and add complete examples:**

```python
#!/usr/bin/env python3
"""
Financial Calculator Usage Examples
====================================

Complete examples of using financial calculators for all entity types.

Updated: 2025-12-11
"""

from pathlib import Path
from PROCESSORS.fundamental.calculators import (
    CompanyFinancialCalculator,
    BankFinancialCalculator,
    InsuranceFinancialCalculator,
    SecurityFinancialCalculator
)

# ============================================================================
# EXAMPLE 1: Company Calculator
# ============================================================================

def example_company_calculator():
    """Calculate financial metrics for a standard company"""
    print("=" * 70)
    print("EXAMPLE 1: Company Financial Calculator")
    print("=" * 70)

    # Initialize calculator with correct path
    data_path = "DATA/raw/fundamental/company/company_full.parquet"
    calc = CompanyFinancialCalculator(data_path=data_path)

    # Run full calculation
    result = calc.calculate_all_metrics()

    # Display results for one ticker
    vnm_data = result[result['symbol'] == 'VNM'].sort_values('report_date')

    print("\nVNM Financial Metrics (Latest 4 Quarters):")
    print(vnm_data[['report_date', 'net_revenue', 'npatmi', 'roe', 'roa']].tail(4))

    # Save to output
    output_path = "DATA/processed/fundamental/company/company_financial_metrics.parquet"
    result.to_parquet(output_path, index=False)
    print(f"\n✅ Saved {len(result)} records to {output_path}")

# ... similar examples for bank, insurance, security

# ============================================================================
# EXAMPLE 5: Using Formulas Directly
# ============================================================================

def example_direct_formula_usage():
    """Use formula functions directly without calculator"""
    print("=" * 70)
    print("EXAMPLE 5: Direct Formula Usage")
    print("=" * 70)

    from PROCESSORS.fundamental.formulas._base_formulas import (
        calculate_roe, calculate_roa, calculate_gross_margin
    )

    # Example data
    net_income = 100_000_000_000  # 100 billion VND
    total_equity = 500_000_000_000  # 500 billion VND
    total_assets = 800_000_000_000  # 800 billion VND
    revenue = 1_200_000_000_000  # 1.2 trillion VND
    cogs = 800_000_000_000  # 800 billion VND

    # Calculate metrics
    roe = calculate_roe(net_income, total_equity)
    roa = calculate_roa(net_income, total_assets)
    gross_margin = calculate_gross_margin(revenue, cogs)

    print(f"\nCalculated Metrics:")
    print(f"  ROE: {roe}%")
    print(f"  ROA: {roa}%")
    print(f"  Gross Margin: {gross_margin}%")

if __name__ == "__main__":
    # Run all examples
    example_company_calculator()
    # ... call other examples
```

#### Phase 6.2: Create API Documentation

**File:** `PROCESSORS/fundamental/API_REFERENCE.md`

```markdown
# Fundamental Calculators API Reference

## Overview

The fundamental calculator system provides a clean, inheritance-based architecture for calculating financial metrics across different entity types.

## Architecture

### Base Class: BaseFinancialCalculator

**Abstract class** that defines the template method pattern.

#### Required Implementations (Subclasses)

All subclasses must implement:

1. `get_entity_type()` → str
2. `get_metric_prefixes()` → List[str]
3. `get_entity_specific_calculations()` → Dict[str, callable]

#### Provided Methods (Inherited)

- `load_data()` - Load parquet files
- `preprocess_data()` - Filter and clean
- `pivot_data()` - Convert long to wide format
- `calculate_all_metrics()` - Main orchestration
- `validate_data()` - Data validation
- `postprocess_results()` - Format output

### Entity-Specific Calculators

#### CompanyFinancialCalculator

**Entity Type:** COMPANY
**Metric Prefixes:** CIS_, CBS_, CCFI_
**Output Metrics:** 40+

**Key Methods:**
- `calculate_income_statement()` - Revenue, margins, profitability
- `calculate_margins()` - Gross, EBIT, EBITDA, net margins
- `calculate_growth_rates()` - QoQ and YoY growth
- `calculate_balance_sheet()` - Assets, liabilities, equity
- `calculate_cash_flow()` - Operating, investing, financing CF
- `calculate_profitability_ratios()` - ROE, ROA, EPS
- `calculate_ttm_metrics()` - Trailing twelve months values

**Usage:**
```python
from PROCESSORS.fundamental.calculators import CompanyFinancialCalculator

calc = CompanyFinancialCalculator(data_path="DATA/raw/fundamental/company/company_full.parquet")
result = calc.calculate_all_metrics()
```

#### BankFinancialCalculator

**Entity Type:** BANK
**Metric Prefixes:** BIS_, BBS_, BNOT_, CCFI_
**Output Metrics:** 35+

**Key Metrics:**
- NIM (Net Interest Margin)
- ROEA / ROAA (Return on Equity/Assets)
- CASA Ratio
- LDR (Loan-to-Deposit Ratio)
- NPL Ratio (Non-Performing Loan)
- CIR (Cost-to-Income Ratio)

[Similar sections for Insurance and Security calculators]

## Formula Library

### Universal Formulas (_base_formulas.py)

24 functions covering:
- Profitability: ROE, ROA, ROIC, margins
- Liquidity: Current ratio, quick ratio, cash ratio
- Leverage: Debt-to-equity, interest coverage
- Efficiency: Asset turnover, inventory turnover
- Valuation: EPS, BVPS, PE ratio, PB ratio

### Entity-Specific Formulas

- **bank_formulas.py**: NIM, CASA ratio, LDR, NPL
- **insurance_formulas.py**: Combined ratio, loss ratio, solvency
- **security_formulas.py**: CAD ratio, revenue composition

## Data Flow

```
Input: DATA/raw/fundamental/[entity]/[entity]_full.parquet
  ↓
Calculator: Entity-specific calculation logic
  ↓
Output: DATA/processed/fundamental/[entity]/[entity]_financial_metrics.parquet
```

## Error Handling

All calculators include:
- Graceful handling of missing metrics (NaN rather than errors)
- Validation of required columns
- Logging of warnings and errors
- Safe arithmetic operations (division by zero protection)

## Testing

Run tests:
```bash
pytest PROCESSORS/fundamental/calculators/tests/ -v
pytest PROCESSORS/fundamental/formulas/tests/ -v
```
```

---

## 4. MIGRATION & ROLLOUT

### Week 1: Critical Fixes
- **Day 1:** Phase 1 (Bug fixes) - Fix logger, typos, test imports
- **Day 2:** Phase 1 (Validation) - Run tests, verify all calculators work

### Week 2: Consolidation
- **Day 3-4:** Phase 2 (Formula consolidation) - Remove duplicates, create missing files
- **Day 5:** Phase 2 (Testing) - Unit tests for all formulas

### Week 3: Integration
- **Day 6-7:** Phase 3 (Schema integration) - Add SchemaRegistry validation
- **Day 8:** Phase 4 (Error handling) - Add comprehensive logging

### Week 4: Testing & Documentation
- **Day 9:** Phase 5 (Testing) - Complete test suite
- **Day 10:** Phase 6 (Documentation) - Update examples and API docs

---

## 5. SUCCESS METRICS

### Quantitative
- **Bugs fixed:** 3 critical bugs eliminated
- **Code duplication reduced:** 20% (5 duplicate functions removed)
- **Test coverage:** 90%+ for calculators, 95%+ for formulas
- **Missing implementations:** 2 formula files created (insurance, security)
- **Documentation:** 100% API coverage

### Qualitative
- ✅ All calculators run without errors
- ✅ Formula logic consolidated in single source
- ✅ Schema validation integrated
- ✅ Comprehensive error handling
- ✅ Clean, maintainable codebase

---

## 6. RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Breaking existing pipelines** | HIGH | Extensive testing before merge |
| **Performance regression** | MEDIUM | Benchmark before/after |
| **Schema integration complexity** | MEDIUM | Phased rollout, validation optional initially |
| **Formula consolidation errors** | HIGH | Unit test every formula after consolidation |

---

## APPENDIX A: METRIC CODE REFERENCE

### COMPANY Metrics (CIS_, CBS_, CCFI_)

**Income Statement (CIS_):**
- CIS_10: Net Revenue
- CIS_11: Cost of Goods Sold
- CIS_20: Gross Profit
- CIS_61: Net Profit After Tax (NPATMI)

**Balance Sheet (CBS_):**
- CBS_270: Total Assets
- CBS_300: Total Liabilities
- CBS_400: Total Equity
- CBS_110: Cash and equivalents

**Cash Flow (CCFI_):**
- CCFI_20: Operating Cash Flow
- CCFI_30: Investing Cash Flow
- CCFI_40: Financing Cash Flow

### BANK Metrics (BIS_, BBS_, BNOT_)

**Income (BIS_):**
- BIS_1: Interest Income
- BIS_2: Interest Expense
- BIS_3: Net Interest Income
- BIS_22A: Net Profit After Tax

**Balance Sheet (BBS_):**
- BBS_100: Total Assets
- BBS_120: Interest-Earning Assets
- BBS_330: Customer Deposits
- BBS_500: Total Equity

**Notes (BNOT_):**
- BNOT_4: Total Loans
- BNOT_4_2: Group 2 Loans (substandard)
- BNOT_26: Total Deposits

[Similar sections for INSURANCE and SECURITY]

---

## CONCLUSION

This plan transforms the fundamental calculator system from "working but has bugs" to "production-ready, maintainable, and extensible." The phased approach ensures stability while systematically improving code quality.

**Total Effort:** 10 days
**Priority:** CRITICAL - Core calculation engine
**Dependencies:** None - can start immediately after config optimization

---

**Plan Status:** READY FOR REVIEW & APPROVAL
**Next Steps:** Review plan → Fix critical bugs (Phase 1) → Consolidate formulas (Phase 2)
