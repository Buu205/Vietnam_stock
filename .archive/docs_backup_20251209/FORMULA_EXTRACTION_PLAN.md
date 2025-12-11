# 📐 FORMULA EXTRACTION PLAN (Week 2)
## Phase 0.2+ Formula Separation & Optimization

**Ngày tạo:** 2025-12-07
**Prerequisite:** Phase 0.2 complete (Base Calculators done)
**Timeline:** 3-5 days
**Status:** ⏳ Ready to start

---

## 🎯 MỤC TIÊU

### Tại sao extract formulas?

**Hiện tại (Phase 0.2):**
```python
# Trong calculator - formulas mixed với data loading
class CompanyFinancialCalculator(BaseFinancialCalculator):
    def calculate_all_metrics(self):
        # Load data
        df = self.load_data()

        # Formula trộn lẫn với logic
        df['roe'] = (df['net_income'] / df['equity']) * 100
        df['roa'] = (df['net_income'] / df['assets']) * 100
        df['gross_margin'] = (df['gross_profit'] / df['revenue']) * 100
        # ... 50+ formulas nữa
```

**Sau khi extract:**
```python
# formulas/company_formulas.py - Pure calculation functions
def calculate_roe(net_income: float, equity: float) -> float:
    """
    Return on Equity (ROE)
    Formula: (Net Income / Equity) × 100
    """
    if equity == 0:
        return None
    return (net_income / equity) * 100

# calculator - Chỉ orchestration
class CompanyFinancialCalculator(BaseFinancialCalculator):
    def calculate_all_metrics(self):
        df = self.load_data()

        # Apply formulas từ module
        df['roe'] = df.apply(
            lambda row: company_formulas.calculate_roe(
                row['net_income'], row['equity']
            ), axis=1
        )
```

### Lợi ích:

✅ **Maintainability:**
- Formulas tách riêng → dễ tìm, dễ sửa
- Không phải đọc 500+ lines calculator code để tìm 1 formula

✅ **Testability:**
- Unit test từng formula độc lập
- Test edge cases (division by zero, negative values, None)

✅ **Documentation:**
- Type hints + docstrings rõ ràng
- MCP có thể explain formulas cho user

✅ **Reusability:**
- Dùng lại formulas cho các entity khác
- Export formulas sang Excel/API

---

## 📋 FORMULA INVENTORY

### Phase 0.2 Calculators Overview:

```
PROCESSORS/fundamental/calculators/
├── base_financial_calculator.py    # Base class (no formulas)
├── company_calculator.py            # ~50 formulas
├── bank_calculator.py               # ~40 formulas
├── insurance_calculator.py          # ~30 formulas
└── security_calculator.py           # ~35 formulas

TOTAL: ~155 formulas to extract
```

### Formula Categories:

**1. Profitability Ratios (20-25 formulas)**
- ROE, ROA, ROIC, ROC
- Gross/Operating/Net profit margins
- EBIT, EBITDA margins

**2. Liquidity Ratios (10-15 formulas)**
- Current ratio, Quick ratio
- Cash ratio
- Working capital ratios

**3. Leverage Ratios (10-15 formulas)**
- Debt/Equity, Debt/Assets
- Interest coverage
- Financial leverage

**4. Efficiency Ratios (15-20 formulas)**
- Asset turnover, Inventory turnover
- Receivables/Payables turnover
- Days Sales Outstanding (DSO)

**5. Valuation Metrics (10-15 formulas)**
- EPS, P/E, P/B, P/S
- EV/EBITDA, EV/Sales
- PEG ratio

**6. Growth Metrics (15-20 formulas)**
- Revenue growth YoY/QoQ
- Earnings growth
- Asset growth

**7. Entity-Specific (35-45 formulas)**
- **Bank:** NIM, CIR, NPL ratio, CAR, LDR
- **Insurance:** Combined ratio, Loss ratio, Expense ratio
- **Security:** Proprietary trading ratio, Margin lending ratio

---

## 🏗️ FOLDER STRUCTURE

### Target Structure:

```
PROCESSORS/fundamental/
├── calculators/
│   ├── __init__.py
│   ├── base_financial_calculator.py
│   ├── company_calculator.py        # Simplified (orchestration only)
│   ├── bank_calculator.py
│   ├── insurance_calculator.py
│   └── security_calculator.py
│
├── formulas/                         # ✨ NEW
│   ├── __init__.py
│   ├── _base_formulas.py            # Common formulas (ROE, ROA, margins)
│   ├── company_formulas.py          # Company-specific
│   ├── bank_formulas.py             # Bank-specific (NIM, CIR, NPL)
│   ├── insurance_formulas.py        # Insurance-specific
│   ├── security_formulas.py         # Security-specific
│   └── utils.py                     # Helper functions (safe_divide, etc.)
│
└── pipelines/
    └── quarterly_pipeline.py
```

---

## 📝 IMPLEMENTATION GUIDE

### Step 1: Create Formula Modules (Day 1-2)

#### 1.1: Create utils.py (helper functions)

```python
# PROCESSORS/fundamental/formulas/utils.py
"""
Utility functions for formula calculations
"""
from typing import Optional, Union
import numpy as np

def safe_divide(
    numerator: Union[float, int, None],
    denominator: Union[float, int, None],
    default: Optional[float] = None
) -> Optional[float]:
    """
    Safely divide two numbers, handling None and zero division.

    Args:
        numerator: Top number
        denominator: Bottom number
        default: Value to return if division fails (default: None)

    Returns:
        Result of division or default value

    Examples:
        >>> safe_divide(100, 50)
        2.0
        >>> safe_divide(100, 0)
        None
        >>> safe_divide(None, 50)
        None
    """
    if numerator is None or denominator is None:
        return default
    if denominator == 0:
        return default
    return numerator / denominator


def safe_multiply(
    value: Union[float, int, None],
    multiplier: Union[float, int],
    default: Optional[float] = None
) -> Optional[float]:
    """
    Safely multiply, handling None values.
    """
    if value is None:
        return default
    return value * multiplier


def to_percentage(
    value: Optional[float],
    default: Optional[float] = None
) -> Optional[float]:
    """
    Convert decimal to percentage (multiply by 100).

    Examples:
        >>> to_percentage(0.25)
        25.0
        >>> to_percentage(None)
        None
    """
    if value is None:
        return default
    return value * 100


def yoy_growth(
    current: Union[float, int, None],
    previous: Union[float, int, None],
    as_percentage: bool = True
) -> Optional[float]:
    """
    Calculate Year-over-Year growth rate.

    Formula: ((Current - Previous) / Previous) × 100

    Args:
        current: Current period value
        previous: Previous period value
        as_percentage: Return as percentage (default: True)

    Returns:
        Growth rate (%) or None
    """
    if current is None or previous is None or previous == 0:
        return None

    growth = (current - previous) / previous
    return growth * 100 if as_percentage else growth
```

#### 1.2: Create _base_formulas.py (common formulas)

```python
# PROCESSORS/fundamental/formulas/_base_formulas.py
"""
Base financial formulas used across all entity types.

These formulas apply to COMPANY, BANK, INSURANCE, and SECURITY entities.
"""
from typing import Optional
from .utils import safe_divide, to_percentage


# ============================================================================
# PROFITABILITY RATIOS
# ============================================================================

def calculate_roe(
    net_income: Optional[float],
    equity: Optional[float]
) -> Optional[float]:
    """
    Return on Equity (ROE)

    Formula: (Net Income / Total Equity) × 100

    Measures: How efficiently company uses shareholder equity to generate profit

    Interpretation:
        - Higher is better
        - > 15%: Good
        - > 20%: Excellent
        - < 10%: Poor

    Args:
        net_income: Net income after tax (Lợi nhuận sau thuế)
        equity: Total shareholder equity (Vốn chủ sở hữu)

    Returns:
        ROE in percentage or None

    Examples:
        >>> calculate_roe(100_000, 500_000)
        20.0  # 20% ROE
        >>> calculate_roe(100_000, 0)
        None  # Cannot divide by zero
    """
    return to_percentage(safe_divide(net_income, equity))


def calculate_roa(
    net_income: Optional[float],
    total_assets: Optional[float]
) -> Optional[float]:
    """
    Return on Assets (ROA)

    Formula: (Net Income / Total Assets) × 100

    Measures: How efficiently company uses assets to generate profit

    Interpretation:
        - Higher is better
        - > 5%: Good
        - > 10%: Excellent
        - Varies by industry

    Args:
        net_income: Net income after tax
        total_assets: Total assets (Tổng tài sản)

    Returns:
        ROA in percentage or None
    """
    return to_percentage(safe_divide(net_income, total_assets))


def calculate_gross_margin(
    gross_profit: Optional[float],
    revenue: Optional[float]
) -> Optional[float]:
    """
    Gross Profit Margin

    Formula: (Gross Profit / Revenue) × 100

    Measures: Profitability after direct costs

    Args:
        gross_profit: Revenue - Cost of Goods Sold
        revenue: Total revenue (Doanh thu)

    Returns:
        Gross margin in percentage or None
    """
    return to_percentage(safe_divide(gross_profit, revenue))


def calculate_operating_margin(
    operating_profit: Optional[float],
    revenue: Optional[float]
) -> Optional[float]:
    """
    Operating Profit Margin

    Formula: (Operating Profit / Revenue) × 100

    Measures: Profitability from core operations

    Args:
        operating_profit: Profit before interest and tax (EBIT)
        revenue: Total revenue

    Returns:
        Operating margin in percentage or None
    """
    return to_percentage(safe_divide(operating_profit, revenue))


def calculate_net_margin(
    net_income: Optional[float],
    revenue: Optional[float]
) -> Optional[float]:
    """
    Net Profit Margin

    Formula: (Net Income / Revenue) × 100

    Measures: Overall profitability after all expenses

    Args:
        net_income: Net income after tax
        revenue: Total revenue

    Returns:
        Net margin in percentage or None
    """
    return to_percentage(safe_divide(net_income, revenue))


# ============================================================================
# LIQUIDITY RATIOS
# ============================================================================

def calculate_current_ratio(
    current_assets: Optional[float],
    current_liabilities: Optional[float]
) -> Optional[float]:
    """
    Current Ratio

    Formula: Current Assets / Current Liabilities

    Measures: Ability to pay short-term obligations

    Interpretation:
        - > 2.0: Strong liquidity
        - 1.0-2.0: Acceptable
        - < 1.0: Liquidity concerns

    Args:
        current_assets: Short-term assets (Tài sản ngắn hạn)
        current_liabilities: Short-term liabilities (Nợ ngắn hạn)

    Returns:
        Current ratio or None
    """
    return safe_divide(current_assets, current_liabilities)


def calculate_quick_ratio(
    current_assets: Optional[float],
    inventory: Optional[float],
    current_liabilities: Optional[float]
) -> Optional[float]:
    """
    Quick Ratio (Acid-Test Ratio)

    Formula: (Current Assets - Inventory) / Current Liabilities

    Measures: Ability to pay short-term obligations without selling inventory

    Interpretation:
        - > 1.0: Good liquidity
        - 0.5-1.0: Acceptable
        - < 0.5: Liquidity concerns

    Args:
        current_assets: Short-term assets
        inventory: Inventory (Hàng tồn kho)
        current_liabilities: Short-term liabilities

    Returns:
        Quick ratio or None
    """
    if current_assets is None or inventory is None:
        return None

    liquid_assets = current_assets - inventory
    return safe_divide(liquid_assets, current_liabilities)


# ============================================================================
# LEVERAGE RATIOS
# ============================================================================

def calculate_debt_to_equity(
    total_debt: Optional[float],
    equity: Optional[float]
) -> Optional[float]:
    """
    Debt-to-Equity Ratio

    Formula: Total Debt / Total Equity

    Measures: Financial leverage

    Interpretation:
        - < 1.0: Conservative (more equity than debt)
        - 1.0-2.0: Moderate leverage
        - > 2.0: High leverage (risky)

    Args:
        total_debt: Short-term + Long-term debt
        equity: Total shareholder equity

    Returns:
        Debt-to-equity ratio or None
    """
    return safe_divide(total_debt, equity)


def calculate_debt_to_assets(
    total_debt: Optional[float],
    total_assets: Optional[float]
) -> Optional[float]:
    """
    Debt-to-Assets Ratio

    Formula: Total Debt / Total Assets

    Measures: Proportion of assets financed by debt

    Interpretation:
        - < 0.3: Low debt
        - 0.3-0.6: Moderate debt
        - > 0.6: High debt

    Args:
        total_debt: Short-term + Long-term debt
        total_assets: Total assets

    Returns:
        Debt-to-assets ratio or None
    """
    return safe_divide(total_debt, total_assets)


# ... Add more base formulas
```

#### 1.3: Create company_formulas.py

```python
# PROCESSORS/fundamental/formulas/company_formulas.py
"""
Company-specific financial formulas.

For COMPANY entity type (standard corporations).
Inherits common formulas from _base_formulas.py
"""
from typing import Optional
from .utils import safe_divide, to_percentage, yoy_growth
from . import _base_formulas as base


# ============================================================================
# EFFICIENCY RATIOS
# ============================================================================

def calculate_asset_turnover(
    revenue: Optional[float],
    total_assets: Optional[float]
) -> Optional[float]:
    """
    Asset Turnover Ratio

    Formula: Revenue / Total Assets

    Measures: How efficiently company uses assets to generate revenue

    Interpretation:
        - Higher is better
        - Varies by industry
        - Manufacturing: 0.5-1.0
        - Retail: 2.0-3.0

    Args:
        revenue: Total revenue
        total_assets: Total assets

    Returns:
        Asset turnover ratio or None
    """
    return safe_divide(revenue, total_assets)


def calculate_inventory_turnover(
    cogs: Optional[float],
    avg_inventory: Optional[float]
) -> Optional[float]:
    """
    Inventory Turnover Ratio

    Formula: Cost of Goods Sold / Average Inventory

    Measures: How many times inventory is sold and replaced

    Interpretation:
        - Higher is better (faster inventory movement)
        - Varies by industry

    Args:
        cogs: Cost of goods sold
        avg_inventory: Average inventory during period

    Returns:
        Inventory turnover ratio or None
    """
    return safe_divide(cogs, avg_inventory)


def calculate_receivables_turnover(
    revenue: Optional[float],
    avg_receivables: Optional[float]
) -> Optional[float]:
    """
    Receivables Turnover Ratio

    Formula: Revenue / Average Receivables

    Measures: How efficiently company collects receivables

    Args:
        revenue: Total revenue
        avg_receivables: Average accounts receivable

    Returns:
        Receivables turnover ratio or None
    """
    return safe_divide(revenue, avg_receivables)


def calculate_days_sales_outstanding(
    avg_receivables: Optional[float],
    revenue: Optional[float],
    days: int = 365
) -> Optional[float]:
    """
    Days Sales Outstanding (DSO)

    Formula: (Average Receivables / Revenue) × Days

    Measures: Average days to collect payment from customers

    Interpretation:
        - Lower is better
        - < 30 days: Excellent
        - 30-60 days: Good
        - > 90 days: Concern

    Args:
        avg_receivables: Average accounts receivable
        revenue: Total revenue
        days: Number of days in period (365 for annual, 90 for quarterly)

    Returns:
        DSO in days or None
    """
    if avg_receivables is None or revenue is None or revenue == 0:
        return None

    return (avg_receivables / revenue) * days


# ============================================================================
# VALUATION METRICS
# ============================================================================

def calculate_eps(
    net_income: Optional[float],
    shares_outstanding: Optional[float]
) -> Optional[float]:
    """
    Earnings Per Share (EPS)

    Formula: Net Income / Shares Outstanding

    Measures: Profit per share

    Args:
        net_income: Net income after tax
        shares_outstanding: Number of shares outstanding

    Returns:
        EPS or None
    """
    return safe_divide(net_income, shares_outstanding)


def calculate_book_value_per_share(
    equity: Optional[float],
    shares_outstanding: Optional[float]
) -> Optional[float]:
    """
    Book Value Per Share (BVPS)

    Formula: Total Equity / Shares Outstanding

    Measures: Net asset value per share

    Args:
        equity: Total shareholder equity
        shares_outstanding: Number of shares outstanding

    Returns:
        BVPS or None
    """
    return safe_divide(equity, shares_outstanding)


# ============================================================================
# GROWTH METRICS
# ============================================================================

def calculate_revenue_growth_yoy(
    current_revenue: Optional[float],
    previous_revenue: Optional[float]
) -> Optional[float]:
    """
    Revenue Growth Year-over-Year

    Formula: ((Current Revenue - Previous Revenue) / Previous Revenue) × 100

    Measures: Revenue growth compared to same period last year

    Args:
        current_revenue: Revenue in current period
        previous_revenue: Revenue in same period last year

    Returns:
        Growth rate in percentage or None
    """
    return yoy_growth(current_revenue, previous_revenue)


def calculate_earnings_growth_yoy(
    current_earnings: Optional[float],
    previous_earnings: Optional[float]
) -> Optional[float]:
    """
    Earnings Growth Year-over-Year

    Formula: ((Current Earnings - Previous Earnings) / Previous Earnings) × 100

    Measures: Earnings growth compared to same period last year

    Args:
        current_earnings: Net income in current period
        previous_earnings: Net income in same period last year

    Returns:
        Growth rate in percentage or None
    """
    return yoy_growth(current_earnings, previous_earnings)


# Re-export base formulas for convenience
calculate_roe = base.calculate_roe
calculate_roa = base.calculate_roa
calculate_gross_margin = base.calculate_gross_margin
calculate_operating_margin = base.calculate_operating_margin
calculate_net_margin = base.calculate_net_margin
calculate_current_ratio = base.calculate_current_ratio
calculate_quick_ratio = base.calculate_quick_ratio
calculate_debt_to_equity = base.calculate_debt_to_equity
calculate_debt_to_assets = base.calculate_debt_to_assets
```

#### 1.4: Create bank_formulas.py

```python
# PROCESSORS/fundamental/formulas/bank_formulas.py
"""
Bank-specific financial formulas.

For BANK entity type.
"""
from typing import Optional
from .utils import safe_divide, to_percentage
from . import _base_formulas as base


# ============================================================================
# BANK-SPECIFIC PROFITABILITY
# ============================================================================

def calculate_nim(
    net_interest_income: Optional[float],
    avg_earning_assets: Optional[float]
) -> Optional[float]:
    """
    Net Interest Margin (NIM)

    Formula: (Net Interest Income / Average Earning Assets) × 100

    Measures: Profitability from lending activities

    Interpretation:
        - > 3%: Good
        - 2-3%: Acceptable
        - < 2%: Low profitability

    Args:
        net_interest_income: Interest income - Interest expense
        avg_earning_assets: Average earning assets

    Returns:
        NIM in percentage or None
    """
    return to_percentage(safe_divide(net_interest_income, avg_earning_assets))


def calculate_cir(
    operating_expenses: Optional[float],
    operating_income: Optional[float]
) -> Optional[float]:
    """
    Cost-to-Income Ratio (CIR)

    Formula: (Operating Expenses / Operating Income) × 100

    Measures: Operating efficiency

    Interpretation:
        - < 40%: Excellent efficiency
        - 40-50%: Good
        - 50-60%: Acceptable
        - > 60%: Poor efficiency

    Args:
        operating_expenses: Total operating expenses
        operating_income: Total operating income

    Returns:
        CIR in percentage or None
    """
    return to_percentage(safe_divide(operating_expenses, operating_income))


# ============================================================================
# ASSET QUALITY
# ============================================================================

def calculate_npl_ratio(
    npl: Optional[float],
    total_loans: Optional[float]
) -> Optional[float]:
    """
    Non-Performing Loan (NPL) Ratio

    Formula: (Non-Performing Loans / Total Loans) × 100

    Measures: Asset quality / Credit risk

    Interpretation:
        - < 2%: Excellent asset quality
        - 2-5%: Acceptable
        - 5-10%: Concern
        - > 10%: High risk

    Args:
        npl: Non-performing loans (Nợ xấu)
        total_loans: Total loan portfolio

    Returns:
        NPL ratio in percentage or None
    """
    return to_percentage(safe_divide(npl, total_loans))


def calculate_loan_loss_reserve_ratio(
    loan_loss_reserve: Optional[float],
    total_loans: Optional[float]
) -> Optional[float]:
    """
    Loan Loss Reserve Ratio

    Formula: (Loan Loss Reserve / Total Loans) × 100

    Measures: Provision for bad debts

    Args:
        loan_loss_reserve: Reserve for loan losses
        total_loans: Total loan portfolio

    Returns:
        Reserve ratio in percentage or None
    """
    return to_percentage(safe_divide(loan_loss_reserve, total_loans))


# ============================================================================
# CAPITAL ADEQUACY
# ============================================================================

def calculate_car(
    tier1_capital: Optional[float],
    tier2_capital: Optional[float],
    risk_weighted_assets: Optional[float]
) -> Optional[float]:
    """
    Capital Adequacy Ratio (CAR)

    Formula: ((Tier 1 + Tier 2 Capital) / Risk-Weighted Assets) × 100

    Measures: Bank's capital strength

    Interpretation:
        - Basel III minimum: 8%
        - SBV requirement: 9% (Vietnam)
        - > 12%: Strong capital
        - < 9%: Undercapitalized

    Args:
        tier1_capital: Core capital (equity + retained earnings)
        tier2_capital: Supplementary capital
        risk_weighted_assets: Total risk-weighted assets

    Returns:
        CAR in percentage or None
    """
    if tier1_capital is None or tier2_capital is None:
        return None

    total_capital = tier1_capital + tier2_capital
    return to_percentage(safe_divide(total_capital, risk_weighted_assets))


# ============================================================================
# LIQUIDITY
# ============================================================================

def calculate_ldr(
    total_loans: Optional[float],
    total_deposits: Optional[float]
) -> Optional[float]:
    """
    Loan-to-Deposit Ratio (LDR)

    Formula: (Total Loans / Total Deposits) × 100

    Measures: Liquidity / Lending aggressiveness

    Interpretation:
        - < 70%: Conservative (low lending)
        - 70-85%: Optimal
        - 85-100%: Aggressive
        - > 100%: High liquidity risk

    Args:
        total_loans: Total loan portfolio
        total_deposits: Total customer deposits

    Returns:
        LDR in percentage or None
    """
    return to_percentage(safe_divide(total_loans, total_deposits))


def calculate_casa_ratio(
    casa_deposits: Optional[float],
    total_deposits: Optional[float]
) -> Optional[float]:
    """
    CASA Ratio (Current Account + Savings Account)

    Formula: (CASA Deposits / Total Deposits) × 100

    Measures: Low-cost funding base

    Interpretation:
        - > 40%: Excellent (low funding cost)
        - 30-40%: Good
        - 20-30%: Acceptable
        - < 20%: High funding cost

    Args:
        casa_deposits: Current + Savings account deposits
        total_deposits: Total deposits

    Returns:
        CASA ratio in percentage or None
    """
    return to_percentage(safe_divide(casa_deposits, total_deposits))


# Re-export base formulas
calculate_roe = base.calculate_roe
calculate_roa = base.calculate_roa
```

---

### Step 2: Update Calculators to Use Formulas (Day 2-3)

#### Before (Mixed logic):
```python
# PROCESSORS/fundamental/calculators/company_calculator.py
class CompanyFinancialCalculator(BaseFinancialCalculator):
    def calculate_all_metrics(self):
        df = self.load_data()

        # Formulas mixed with logic
        df['roe'] = (df['net_income'] / df['equity']) * 100
        df['roa'] = (df['net_income'] / df['assets']) * 100
        # ... 50 more lines
```

#### After (Clean separation):
```python
# PROCESSORS/fundamental/calculators/company_calculator.py
from PROCESSORS.fundamental.formulas import company_formulas

class CompanyFinancialCalculator(BaseFinancialCalculator):
    def calculate_all_metrics(self):
        """Calculate all company financial metrics using formula module."""
        df = self.load_data()

        # Apply formulas
        df['roe'] = df.apply(
            lambda row: company_formulas.calculate_roe(
                row['net_income'], row['equity']
            ), axis=1
        )

        df['roa'] = df.apply(
            lambda row: company_formulas.calculate_roa(
                row['net_income'], row['assets']
            ), axis=1
        )

        df['gross_margin'] = df.apply(
            lambda row: company_formulas.calculate_gross_margin(
                row['gross_profit'], row['revenue']
            ), axis=1
        )

        # ... cleaner, testable, documented
```

---

### Step 3: Create Unit Tests (Day 3-4)

```python
# PROCESSORS/fundamental/formulas/tests/test_company_formulas.py
"""
Unit tests for company formulas
"""
import pytest
from PROCESSORS.fundamental.formulas import company_formulas


class TestProfitabilityRatios:
    """Test profitability ratio calculations"""

    def test_roe_normal_case(self):
        """Test ROE with normal values"""
        result = company_formulas.calculate_roe(
            net_income=100_000,
            equity=500_000
        )
        assert result == 20.0  # 20% ROE

    def test_roe_zero_equity(self):
        """Test ROE with zero equity (division by zero)"""
        result = company_formulas.calculate_roe(
            net_income=100_000,
            equity=0
        )
        assert result is None

    def test_roe_none_values(self):
        """Test ROE with None values"""
        assert company_formulas.calculate_roe(None, 500_000) is None
        assert company_formulas.calculate_roe(100_000, None) is None

    def test_roa_normal_case(self):
        """Test ROA with normal values"""
        result = company_formulas.calculate_roa(
            net_income=100_000,
            total_assets=2_000_000
        )
        assert result == 5.0  # 5% ROA


class TestEfficiencyRatios:
    """Test efficiency ratio calculations"""

    def test_asset_turnover(self):
        """Test asset turnover ratio"""
        result = company_formulas.calculate_asset_turnover(
            revenue=1_000_000,
            total_assets=500_000
        )
        assert result == 2.0

    def test_dso_annual(self):
        """Test Days Sales Outstanding (annual)"""
        result = company_formulas.calculate_days_sales_outstanding(
            avg_receivables=100_000,
            revenue=1_000_000,
            days=365
        )
        assert result == 36.5  # 36.5 days


# Run tests:
# pytest PROCESSORS/fundamental/formulas/tests/ -v
```

---

### Step 4: Documentation & Examples (Day 4-5)

Create `PROCESSORS/fundamental/formulas/README.md`:

```markdown
# Financial Formulas Module

Pure calculation functions for financial metrics.

## Usage

### Import formulas:
```python
from PROCESSORS.fundamental.formulas import company_formulas, bank_formulas

# Calculate ROE
roe = company_formulas.calculate_roe(
    net_income=100_000,
    equity=500_000
)
print(f"ROE: {roe}%")  # ROE: 20.0%
```

### Use in calculators:
```python
# Apply to DataFrame
df['roe'] = df.apply(
    lambda row: company_formulas.calculate_roe(
        row['net_income'], row['equity']
    ), axis=1
)
```

## Formula Catalog

### Common Formulas (_base_formulas.py)
- Profitability: ROE, ROA, margins
- Liquidity: Current ratio, Quick ratio
- Leverage: Debt ratios

### Company Formulas (company_formulas.py)
- Efficiency: Turnover ratios, DSO
- Valuation: EPS, BVPS
- Growth: Revenue/Earnings growth

### Bank Formulas (bank_formulas.py)
- Profitability: NIM, CIR
- Asset Quality: NPL ratio
- Capital: CAR
- Liquidity: LDR, CASA ratio

### Insurance Formulas (insurance_formulas.py)
- Combined ratio
- Loss ratio
- Expense ratio

### Security Formulas (security_formulas.py)
- Proprietary trading ratio
- Margin lending ratio
```

---

## ✅ CHECKLIST

### Day 1-2: Create Formula Modules
- [ ] Create `PROCESSORS/fundamental/formulas/` folder
- [ ] Create `__init__.py`
- [ ] Create `utils.py` (safe_divide, to_percentage, yoy_growth)
- [ ] Create `_base_formulas.py` (20-25 common formulas)
- [ ] Create `company_formulas.py` (~50 formulas)
- [ ] Create `bank_formulas.py` (~40 formulas)
- [ ] Create `insurance_formulas.py` (~30 formulas)
- [ ] Create `security_formulas.py` (~35 formulas)

### Day 2-3: Update Calculators
- [ ] Update `company_calculator.py` to use formulas
- [ ] Update `bank_calculator.py` to use formulas
- [ ] Update `insurance_calculator.py` to use formulas
- [ ] Update `security_calculator.py` to use formulas
- [ ] Test all calculators still work
- [ ] Compare output before/after (should be identical)

### Day 3-4: Testing
- [ ] Create `tests/` folder in formulas/
- [ ] Write unit tests for utils.py
- [ ] Write unit tests for _base_formulas.py
- [ ] Write unit tests for company_formulas.py
- [ ] Write unit tests for bank_formulas.py
- [ ] Write unit tests for insurance_formulas.py
- [ ] Write unit tests for security_formulas.py
- [ ] Run all tests: `pytest PROCESSORS/fundamental/formulas/tests/ -v`
- [ ] Achieve >90% code coverage

### Day 4-5: Documentation
- [ ] Add docstrings to all formulas (formula, interpretation, examples)
- [ ] Create `formulas/README.md` with usage guide
- [ ] Create formula catalog (list all 155 formulas)
- [ ] Add examples for each category
- [ ] Update `CURRENT_STATUS.md` with Week 2 completion

---

## 📊 EXPECTED OUTCOMES

### Before Formula Extraction:
```
PROCESSORS/fundamental/calculators/
├── company_calculator.py    500 lines (logic + formulas mixed)
├── bank_calculator.py       450 lines
├── insurance_calculator.py  400 lines
└── security_calculator.py   400 lines

Output:
DATA/processed/fundamental/
├── company/company_financial_metrics.parquet
├── bank/bank_financial_metrics.parquet
├── insurance/insurance_financial_metrics.parquet
└── security/security_financial_metrics.parquet
```

### After Formula Extraction:
```
PROCESSORS/fundamental/
├── calculators/
│   ├── company_calculator.py     250 lines (orchestration only)
│   ├── bank_calculator.py        200 lines
│   ├── insurance_calculator.py   180 lines
│   └── security_calculator.py    180 lines
│
└── formulas/
    ├── utils.py                  100 lines
    ├── _base_formulas.py         300 lines
    ├── company_formulas.py       500 lines
    ├── bank_formulas.py          400 lines
    ├── insurance_formulas.py     300 lines
    ├── security_formulas.py      350 lines
    └── tests/                    1000+ lines

Output (same location - v3.0 structure):
DATA/processed/fundamental/
├── company/company_financial_metrics.parquet
├── bank/bank_financial_metrics.parquet
├── insurance/insurance_financial_metrics.parquet
└── security/security_financial_metrics.parquet
```

**Benefits:**
- ✅ 50% reduction in calculator complexity
- ✅ 155 formulas documented with type hints + docstrings
- ✅ 100% testable (unit tests for each formula)
- ✅ Reusable across different contexts
- ✅ MCP can explain formulas to users

---

## 🚀 NEXT STEPS AFTER WEEK 2

### Week 3: Quarterly Pipeline (Optional)
- Create `quarterly_pipeline.py` to run all calculators
- Add validation + backup logic

### Week 4: MCP Integration (When Ready)
- MCP can query formulas by Vietnamese name
- MCP can explain formula meanings
- MCP can show example calculations

---

## 💡 TIPS

### When extracting formulas:
1. **Start small:** Extract 5-10 formulas first, test, then continue
2. **Test immediately:** Don't extract all formulas then test - test as you go
3. **Compare outputs:** Ensure calculator output identical before/after
4. **Use type hints:** Helps catch errors early
5. **Write good docstrings:** Future you will thank you

### Common pitfalls:
- ❌ Forgetting to handle None/zero division
- ❌ Not testing edge cases
- ❌ Missing docstrings
- ❌ Not comparing before/after outputs

---

**Last Updated:** 2025-12-07
**Status:** ⏳ Ready to implement after schema standardization complete
