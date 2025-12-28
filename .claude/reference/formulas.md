# Valuation Formulas Reference

Complete reference for all financial and valuation formulas used in the Vietnam Dashboard project.

---

## Valuation Ratios

### PE Ratio (Price-to-Earnings)

**Formula:**
```
PE Ratio = Market Capitalization / TTM Earnings
PE Ratio = Price per Share / EPS (Earnings per Share)
```

**Implementation:**
```python
# File: PROCESSORS/valuation/calculators/vnindex_pe_calculator_optimized.py

def calculate_pe_ratio(market_cap: float, ttm_earnings: float) -> float:
    """Calculate PE ratio.

    Args:
        market_cap: Market capitalization (billions VND)
        ttm_earnings: Trailing twelve month earnings (billions VND)

    Returns:
        PE ratio (times)
    """
    if ttm_earnings <= 0:
        return np.nan
    return market_cap / ttm_earnings
```

**VN-Index PE Calculation:**
```python
# Aggregate all tickers
total_market_cap = sum(market_cap) / 1e9  # Convert to billions
total_ttm_earnings = sum(ttm_earning_billion_vnd)

# Calculate VN-Index PE
vnindex_pe = total_market_cap / total_ttm_earnings

# Validation
valid_data = data[
    (data['market_cap'] > 0) &
    (data['ttm_earning_billion_vnd'].notna()) &
    (data['ttm_earning_billion_vnd'] > 0)
]
```

**Symbol Filtering:**
```python
# Exclude certain tickers from VN-Index calculation
exclude_symbols = ['VIC', 'VHM', 'VPB']
filtered_symbols = [s for s in all_symbols if s not in exclude_symbols]
```

---

### PB Ratio (Price-to-Book)

**Formula:**
```
PB Ratio = Market Capitalization / Book Value of Equity
PB Ratio = Price per Share / BVPS (Book Value per Share)
```

**Implementation:**
```python
# File: PROCESSORS/valuation/calculators/vnindex_pb_calculator_optimized.py

def calculate_pb_ratio(market_cap: float, equity: float) -> float:
    """Calculate PB ratio.

    Args:
        market_cap: Market capitalization (billions VND)
        equity: Book value of equity (billions VND)

    Returns:
        PB ratio (times)
    """
    if equity <= 0:
        return np.nan
    return market_cap / equity
```

**VN-Index PB Calculation:**
```python
# Aggregate all tickers
total_market_cap = sum(market_cap) / 1e9  # Convert to billions
total_equity = sum(equity_billion_vnd)

# Calculate VN-Index PB
vnindex_pb = total_market_cap / total_equity

# Validation
valid_data = data[
    (data['market_cap'] > 0) &
    (data['equity_billion_vnd'].notna()) &
    (data['equity_billion_vnd'] > 0)
]
```

---

### PS Ratio (Price-to-Sales)

**Formula:**
```
PS Ratio = Market Capitalization / TTM Revenue
PS Ratio = Price per Share / Revenue per Share
```

**Implementation:**
```python
def calculate_ps_ratio(market_cap: float, ttm_revenue: float) -> float:
    """Calculate PS ratio.

    Args:
        market_cap: Market capitalization (billions VND)
        ttm_revenue: Trailing twelve month revenue (billions VND)

    Returns:
        PS ratio (times)
    """
    if ttm_revenue <= 0:
        return np.nan
    return market_cap / ttm_revenue
```

---

### EV/EBITDA Ratio

**Formula:**
```
EV/EBITDA = Enterprise Value / EBITDA

Where:
Enterprise Value (EV) = Market Cap + Total Debt - Cash & Cash Equivalents
EBITDA = Earnings Before Interest, Tax, Depreciation, and Amortization
```

**Implementation:**
```python
# File: PROCESSORS/valuation/calculators/ev_ebitda_calculator_optimized.py

def calculate_ev_ebitda(
    market_cap: float,
    total_debt: float,
    cash: float,
    ebitda: float
) -> float:
    """Calculate EV/EBITDA ratio.

    Args:
        market_cap: Market capitalization (billions VND)
        total_debt: Total debt (billions VND)
        cash: Cash and cash equivalents (billions VND)
        ebitda: EBITDA (billions VND)

    Returns:
        EV/EBITDA ratio (times)
    """
    # Calculate Enterprise Value
    ev = market_cap + total_debt - cash

    if ebitda <= 0:
        return np.nan

    return ev / ebitda
```

---

## Fundamental Metrics

### ROE (Return on Equity)

**Formula:**
```
ROE = Net Income / Shareholders' Equity
```

**Implementation:**
```python
# File: PROCESSORS/transformers/financial/formulas.py

def roe(net_income: float, equity: float) -> float:
    """Calculate Return on Equity.

    Args:
        net_income: Net income (VND)
        equity: Shareholders' equity (VND)

    Returns:
        ROE as decimal (e.g., 0.15 for 15%)
    """
    if equity <= 0:
        return np.nan
    return net_income / equity
```

---

### ROA (Return on Assets)

**Formula:**
```
ROA = Net Income / Total Assets
```

**Implementation:**
```python
def roa(net_income: float, assets: float) -> float:
    """Calculate Return on Assets.

    Args:
        net_income: Net income (VND)
        assets: Total assets (VND)

    Returns:
        ROA as decimal (e.g., 0.08 for 8%)
    """
    if assets <= 0:
        return np.nan
    return net_income / assets
```

---

### Gross Margin

**Formula:**
```
Gross Margin = (Revenue - COGS) / Revenue
Gross Margin = Gross Profit / Revenue
```

**Implementation:**
```python
def gross_margin(gross_profit: float, revenue: float) -> float:
    """Calculate Gross Margin.

    Args:
        gross_profit: Gross profit (VND)
        revenue: Total revenue (VND)

    Returns:
        Gross margin as decimal (e.g., 0.35 for 35%)
    """
    if revenue <= 0:
        return np.nan
    return gross_profit / revenue
```

---

### Net Margin

**Formula:**
```
Net Margin = Net Income / Revenue
```

**Implementation:**
```python
def net_margin(net_income: float, revenue: float) -> float:
    """Calculate Net Margin.

    Args:
        net_income: Net income (VND)
        revenue: Total revenue (VND)

    Returns:
        Net margin as decimal (e.g., 0.12 for 12%)
    """
    if revenue <= 0:
        return np.nan
    return net_income / revenue
```

---

### Debt-to-Equity Ratio

**Formula:**
```
Debt-to-Equity = Total Debt / Shareholders' Equity
```

**Implementation:**
```python
def debt_to_equity(total_debt: float, equity: float) -> float:
    """Calculate Debt-to-Equity ratio.

    Args:
        total_debt: Total debt (VND)
        equity: Shareholders' equity (VND)

    Returns:
        D/E ratio (times)
    """
    if equity <= 0:
        return np.nan
    return total_debt / equity
```

---

## Growth Metrics

### YoY Growth (Year-over-Year)

**Formula:**
```
YoY Growth = (Current Value - Previous Value) / Previous Value
```

**Implementation:**
```python
def yoy_growth(current: float, previous: float) -> float:
    """Calculate Year-over-Year growth.

    Args:
        current: Current period value
        previous: Previous period value (same quarter, previous year)

    Returns:
        Growth rate as decimal (e.g., 0.25 for 25% growth)
    """
    if previous <= 0:
        return np.nan
    return (current - previous) / previous
```

---

### QoQ Growth (Quarter-over-Quarter)

**Formula:**
```
QoQ Growth = (Current Quarter - Previous Quarter) / Previous Quarter
```

**Implementation:**
```python
def qoq_growth(current: float, previous: float) -> float:
    """Calculate Quarter-over-Quarter growth.

    Args:
        current: Current quarter value
        previous: Previous quarter value

    Returns:
        Growth rate as decimal (e.g., 0.10 for 10% growth)
    """
    if previous <= 0:
        return np.nan
    return (current - previous) / previous
```

---

## Bank-Specific Metrics

### NIM (Net Interest Margin)

**Formula:**
```
NIM = (Interest Income - Interest Expense) / Average Earning Assets
```

**Implementation:**
```python
def nim(interest_income: float, interest_expense: float, avg_earning_assets: float) -> float:
    """Calculate Net Interest Margin.

    Args:
        interest_income: Interest income (VND)
        interest_expense: Interest expense (VND)
        avg_earning_assets: Average earning assets (VND)

    Returns:
        NIM as decimal (e.g., 0.03 for 3%)
    """
    if avg_earning_assets <= 0:
        return np.nan
    return (interest_income - interest_expense) / avg_earning_assets
```

---

### NPL Ratio (Non-Performing Loan Ratio)

**Formula:**
```
NPL Ratio = Non-Performing Loans / Total Loans
```

**Implementation:**
```python
def npl_ratio(npl: float, total_loans: float) -> float:
    """Calculate NPL Ratio.

    Args:
        npl: Non-performing loans (VND)
        total_loans: Total loan portfolio (VND)

    Returns:
        NPL ratio as decimal (e.g., 0.02 for 2%)
    """
    if total_loans <= 0:
        return np.nan
    return npl / total_loans
```

---

### CAR (Capital Adequacy Ratio)

**Formula:**
```
CAR = (Tier 1 Capital + Tier 2 Capital) / Risk-Weighted Assets
```

**Implementation:**
```python
def car(tier1_capital: float, tier2_capital: float, rwa: float) -> float:
    """Calculate Capital Adequacy Ratio.

    Args:
        tier1_capital: Tier 1 capital (VND)
        tier2_capital: Tier 2 capital (VND)
        rwa: Risk-weighted assets (VND)

    Returns:
        CAR as decimal (e.g., 0.12 for 12%)
    """
    if rwa <= 0:
        return np.nan
    return (tier1_capital + tier2_capital) / rwa
```

---

### CASA Ratio (Current Account & Savings Account)

**Formula:**
```
CASA Ratio = (Current Account Deposits + Savings Account Deposits) / Total Deposits
```

**Implementation:**
```python
def casa_ratio(casa_deposits: float, total_deposits: float) -> float:
    """Calculate CASA Ratio.

    Args:
        casa_deposits: Current + Savings account deposits (VND)
        total_deposits: Total deposits (VND)

    Returns:
        CASA ratio as decimal (e.g., 0.35 for 35%)
    """
    if total_deposits <= 0:
        return np.nan
    return casa_deposits / total_deposits
```

---

### CIR (Cost-to-Income Ratio)

**Formula:**
```
CIR = Operating Expenses / Operating Income
```

**Implementation:**
```python
def cir(operating_expenses: float, operating_income: float) -> float:
    """Calculate Cost-to-Income Ratio.

    Args:
        operating_expenses: Operating expenses (VND)
        operating_income: Operating income (VND)

    Returns:
        CIR as decimal (e.g., 0.45 for 45%)
    """
    if operating_income <= 0:
        return np.nan
    return operating_expenses / operating_income
```

---

## Sector Aggregation

### Sector PE Calculation

**Formula:**
```
Sector PE = Total Sector Market Cap / Total Sector TTM Earnings

Where:
Total Sector Market Cap = sum(market_cap for all tickers in sector)
Total Sector TTM Earnings = sum(ttm_earnings for all tickers in sector)
```

**Implementation:**
```python
from config.registries import SectorRegistry

def calculate_sector_pe(sector: str, ohlcv_df: pd.DataFrame, fundamental_df: pd.DataFrame) -> float:
    """Calculate sector PE ratio.

    Args:
        sector: Sector name (e.g., "Ngân hàng")
        ohlcv_df: OHLCV data with market cap
        fundamental_df: Fundamental data with TTM earnings

    Returns:
        Sector PE ratio
    """
    # Get tickers in sector
    sector_reg = SectorRegistry()
    tickers = sector_reg.get_tickers_by_sector(sector)

    # Filter data for sector
    sector_ohlcv = ohlcv_df[ohlcv_df['ticker'].isin(tickers)]
    sector_fundamental = fundamental_df[fundamental_df['ticker'].isin(tickers)]

    # Aggregate
    total_market_cap = sector_ohlcv['market_cap'].sum() / 1e9  # billions
    total_ttm_earnings = sector_fundamental['ttm_earnings'].sum()

    # Calculate PE
    if total_ttm_earnings <= 0:
        return np.nan
    return total_market_cap / total_ttm_earnings
```

---

## Validation Rules

### Data Validation

```python
# PE Ratio validation
assert pe_ratio > 0, "PE ratio must be positive"
assert pe_ratio < 100, "PE ratio unusually high (> 100)"

# PB Ratio validation
assert pb_ratio > 0, "PB ratio must be positive"
assert pb_ratio < 20, "PB ratio unusually high (> 20)"

# ROE validation
assert -1 < roe < 2, "ROE out of reasonable range (-100% to 200%)"

# Growth validation
assert -0.9 < yoy_growth < 5, "YoY growth out of reasonable range"
```

---

## Common Issues & Solutions

### Division by Zero

```python
# Always check denominator before division
def safe_divide(numerator: float, denominator: float) -> float:
    """Safe division with NaN handling."""
    if denominator == 0 or pd.isna(denominator):
        return np.nan
    return numerator / denominator
```

### Negative Earnings/Equity

```python
# Return NaN for negative denominators in ratio calculations
if ttm_earnings <= 0:
    return np.nan  # PE ratio undefined for negative earnings

if equity <= 0:
    return np.nan  # PB ratio undefined for negative equity
```

### Missing Data

```python
# Handle missing data gracefully
df['pe_ratio'] = df.apply(
    lambda row: calculate_pe_ratio(row['market_cap'], row['ttm_earnings'])
    if pd.notna(row['ttm_earnings']) else np.nan,
    axis=1
)
```

---

## Quick Reference

| Metric | Formula | Output Type |
|--------|---------|-------------|
| **PE Ratio** | Market Cap / TTM Earnings | Times (x) |
| **PB Ratio** | Market Cap / Equity | Times (x) |
| **PS Ratio** | Market Cap / TTM Revenue | Times (x) |
| **EV/EBITDA** | (Market Cap + Debt - Cash) / EBITDA | Times (x) |
| **ROE** | Net Income / Equity | Decimal (%) |
| **ROA** | Net Income / Assets | Decimal (%) |
| **Gross Margin** | Gross Profit / Revenue | Decimal (%) |
| **Net Margin** | Net Income / Revenue | Decimal (%) |
| **YoY Growth** | (Current - Previous) / Previous | Decimal (%) |
| **NIM** | (Int. Income - Int. Expense) / Assets | Decimal (%) |
| **NPL Ratio** | NPL / Total Loans | Decimal (%) |
| **CAR** | Total Capital / RWA | Decimal (%) |
| **CASA Ratio** | CASA / Total Deposits | Decimal (%) |
