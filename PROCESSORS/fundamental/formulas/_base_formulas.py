#!/usr/bin/env python3
"""
Base Financial Formulas

Common financial formulas used across all entity types (COMPANY, BANK, INSURANCE, SECURITY).

These are pure calculation functions that:
- Take primitive types (float, int, None) as inputs
- Return Optional[float] outputs
- Handle None/zero division gracefully
- Include comprehensive docstrings with formula, interpretation, and examples

Author: Formula Extraction Team
Date: 2025-12-08
"""

from typing import Optional

# Handle imports for both module usage and standalone testing
try:
    from .utils import safe_divide, to_percentage
except ImportError:
    from utils import safe_divide, to_percentage


# =============================================================================
# PROFITABILITY RATIOS
# =============================================================================

def calculate_roe(
    net_income: Optional[float],
    equity: Optional[float]
) -> Optional[float]:
    """
    Return on Equity (ROE)

    Formula: (Net Income / Total Equity) × 100

    Measures: How efficiently company uses shareholder equity to generate profit

    Interpretation:
        - > 20%: Excellent
        - 15-20%: Good
        - 10-15%: Acceptable
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
        - > 10%: Excellent
        - 5-10%: Good
        - 2-5%: Acceptable
        - < 2%: Poor
        - Varies by industry (capital-intensive industries have lower ROA)

    Args:
        net_income: Net income after tax
        total_assets: Total assets (Tổng tài sản)

    Returns:
        ROA in percentage or None
    """
    return to_percentage(safe_divide(net_income, total_assets))


def calculate_roic(
    nopat: Optional[float],
    invested_capital: Optional[float]
) -> Optional[float]:
    """
    Return on Invested Capital (ROIC)

    Formula: (NOPAT / Invested Capital) × 100

    Where:
    - NOPAT = Net Operating Profit After Tax
    - Invested Capital = Debt + Equity - Cash

    Measures: Return generated on all capital invested (debt + equity)

    Interpretation:
        - > 15%: Excellent
        - 10-15%: Good
        - 5-10%: Acceptable
        - < 5%: Poor

    Args:
        nopat: Net operating profit after tax
        invested_capital: Total capital invested (debt + equity - cash)

    Returns:
        ROIC in percentage or None
    """
    return to_percentage(safe_divide(nopat, invested_capital))


def calculate_gross_margin(
    gross_profit: Optional[float],
    revenue: Optional[float]
) -> Optional[float]:
    """
    Gross Profit Margin

    Formula: (Gross Profit / Revenue) × 100

    Measures: Profitability after direct costs (COGS)

    Interpretation:
        - > 40%: High margin (software, services)
        - 20-40%: Moderate margin (retail, manufacturing)
        - < 20%: Low margin (commodities, low-value retail)

    Args:
        gross_profit: Revenue - Cost of Goods Sold (Lợi nhuận gộp)
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

    Measures: Profitability from core operations (before interest & tax)

    Interpretation:
        - > 20%: Excellent
        - 10-20%: Good
        - 5-10%: Acceptable
        - < 5%: Poor

    Args:
        operating_profit: Profit before interest and tax / EBIT
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

    Interpretation:
        - > 15%: Excellent
        - 10-15%: Good
        - 5-10%: Acceptable
        - < 5%: Poor

    Args:
        net_income: Net income after tax
        revenue: Total revenue

    Returns:
        Net margin in percentage or None
    """
    return to_percentage(safe_divide(net_income, revenue))


def calculate_ebit_margin(
    ebit: Optional[float],
    revenue: Optional[float]
) -> Optional[float]:
    """
    EBIT Margin (Earnings Before Interest & Tax)

    Formula: (EBIT / Revenue) × 100

    Measures: Operating profitability before financing costs

    Args:
        ebit: Earnings before interest and tax
        revenue: Total revenue

    Returns:
        EBIT margin in percentage or None
    """
    return to_percentage(safe_divide(ebit, revenue))


def calculate_ebitda_margin(
    ebitda: Optional[float],
    revenue: Optional[float]
) -> Optional[float]:
    """
    EBITDA Margin (Earnings Before Interest, Tax, Depreciation, Amortization)

    Formula: (EBITDA / Revenue) × 100

    Measures: Cash profitability before financing and non-cash expenses

    Args:
        ebitda: Earnings before interest, tax, depreciation, amortization
        revenue: Total revenue

    Returns:
        EBITDA margin in percentage or None
    """
    return to_percentage(safe_divide(ebitda, revenue))


# =============================================================================
# LIQUIDITY RATIOS
# =============================================================================

def calculate_current_ratio(
    current_assets: Optional[float],
    current_liabilities: Optional[float]
) -> Optional[float]:
    """
    Current Ratio

    Formula: Current Assets / Current Liabilities

    Measures: Ability to pay short-term obligations

    Interpretation:
        - > 2.0: Strong liquidity (may indicate inefficient use of assets)
        - 1.5-2.0: Good liquidity
        - 1.0-1.5: Acceptable
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


def calculate_cash_ratio(
    cash: Optional[float],
    current_liabilities: Optional[float]
) -> Optional[float]:
    """
    Cash Ratio

    Formula: Cash / Current Liabilities

    Measures: Ability to pay short-term obligations with cash only

    Interpretation:
        - > 0.5: Very strong liquidity
        - 0.2-0.5: Good liquidity
        - < 0.2: Rely on receivables/inventory

    Args:
        cash: Cash and cash equivalents
        current_liabilities: Short-term liabilities

    Returns:
        Cash ratio or None
    """
    return safe_divide(cash, current_liabilities)


# =============================================================================
# LEVERAGE RATIOS
# =============================================================================

def calculate_debt_to_equity(
    total_debt: Optional[float],
    equity: Optional[float]
) -> Optional[float]:
    """
    Debt-to-Equity Ratio

    Formula: Total Debt / Total Equity

    Measures: Financial leverage

    Interpretation:
        - < 0.5: Conservative (low leverage)
        - 0.5-1.0: Moderate leverage
        - 1.0-2.0: Aggressive leverage
        - > 2.0: High leverage (risky)

    Args:
        total_debt: Short-term + Long-term debt (Tổng nợ vay)
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
        - < 0.3: Low debt (conservative)
        - 0.3-0.6: Moderate debt
        - > 0.6: High debt (aggressive)

    Args:
        total_debt: Short-term + Long-term debt
        total_assets: Total assets

    Returns:
        Debt-to-assets ratio or None
    """
    return safe_divide(total_debt, total_assets)


def calculate_equity_multiplier(
    total_assets: Optional[float],
    equity: Optional[float]
) -> Optional[float]:
    """
    Equity Multiplier

    Formula: Total Assets / Total Equity

    Measures: Financial leverage (DuPont analysis component)

    Interpretation:
        - 1.0: No debt (100% equity financed)
        - 2.0: 50% equity, 50% debt
        - > 3.0: High leverage

    Args:
        total_assets: Total assets
        equity: Total shareholder equity

    Returns:
        Equity multiplier or None
    """
    return safe_divide(total_assets, equity)


def calculate_interest_coverage(
    ebit: Optional[float],
    interest_expense: Optional[float]
) -> Optional[float]:
    """
    Interest Coverage Ratio

    Formula: EBIT / Interest Expense

    Measures: Ability to pay interest on debt

    Interpretation:
        - > 5: Very safe
        - 2.5-5: Acceptable
        - 1.5-2.5: Caution
        - < 1.5: High risk (cannot cover interest)

    Args:
        ebit: Earnings before interest and tax
        interest_expense: Interest expense (Chi phí lãi vay)

    Returns:
        Interest coverage ratio or None
    """
    return safe_divide(ebit, interest_expense)


# =============================================================================
# EFFICIENCY RATIOS
# =============================================================================

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
        - Varies by industry:
          - Retail: 2-3
          - Manufacturing: 0.5-1.0
          - Services: 1-2

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
        - Varies by industry:
          - Grocery: 10-20
          - Retail: 4-8
          - Manufacturing: 6-12

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

    Interpretation:
        - Higher is better (faster collection)
        - 6-12: Good
        - < 6: Slow collection

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
        - < 30 days: Excellent
        - 30-60 days: Good
        - 60-90 days: Acceptable
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


def calculate_days_inventory_outstanding(
    avg_inventory: Optional[float],
    cogs: Optional[float],
    days: int = 365
) -> Optional[float]:
    """
    Days Inventory Outstanding (DIO)

    Formula: (Average Inventory / COGS) × Days

    Measures: Average days inventory held before sale

    Interpretation:
        - Lower is better (faster inventory turnover)
        - Varies by industry

    Args:
        avg_inventory: Average inventory
        cogs: Cost of goods sold
        days: Number of days in period

    Returns:
        DIO in days or None
    """
    if avg_inventory is None or cogs is None or cogs == 0:
        return None

    return (avg_inventory / cogs) * days


# =============================================================================
# VALUATION METRICS
# =============================================================================

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
        shares_outstanding: Number of shares outstanding (Số cổ phiếu lưu hành)

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


# NOTE: PE and PB ratios moved to valuation module
# Use: from PROCESSORS.valuation.formulas.valuation_formulas import calculate_pe_ratio, calculate_pb_ratio


def calculate_ev_ebitda(
    enterprise_value: Optional[float],
    ebitda: Optional[float]
) -> Optional[float]:
    """
    EV/EBITDA Ratio

    Formula: Enterprise Value / EBITDA

    Where:
    - Enterprise Value = Market Cap + Debt - Cash

    Measures: Company valuation relative to cash earnings

    Interpretation:
        - < 10: Potentially undervalued
        - 10-15: Fair value
        - > 15: Potentially overvalued

    Args:
        enterprise_value: Market cap + debt - cash
        ebitda: Earnings before interest, tax, depreciation, amortization

    Returns:
        EV/EBITDA ratio or None
    """
    return safe_divide(enterprise_value, ebitda)


# =============================================================================
# DEMO / TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("BASE FINANCIAL FORMULAS DEMO")
    print("=" * 60)

    print("\n📊 PROFITABILITY RATIOS:")
    print(f"  ROE: {calculate_roe(100_000, 500_000):.2f}%")
    print(f"  ROA: {calculate_roa(100_000, 2_000_000):.2f}%")
    print(f"  Gross Margin: {calculate_gross_margin(300_000, 1_000_000):.2f}%")
    print(f"  Net Margin: {calculate_net_margin(100_000, 1_000_000):.2f}%")

    print("\n💧 LIQUIDITY RATIOS:")
    print(f"  Current Ratio: {calculate_current_ratio(500_000, 300_000):.2f}")
    print(f"  Quick Ratio: {calculate_quick_ratio(500_000, 100_000, 300_000):.2f}")
    print(f"  Cash Ratio: {calculate_cash_ratio(100_000, 300_000):.2f}")

    print("\n⚖️  LEVERAGE RATIOS:")
    print(f"  Debt/Equity: {calculate_debt_to_equity(400_000, 500_000):.2f}")
    print(f"  Debt/Assets: {calculate_debt_to_assets(400_000, 2_000_000):.2f}")
    print(f"  Interest Coverage: {calculate_interest_coverage(150_000, 30_000):.2f}")

    print("\n🔄 EFFICIENCY RATIOS:")
    print(f"  Asset Turnover: {calculate_asset_turnover(1_000_000, 2_000_000):.2f}")
    print(f"  DSO: {calculate_days_sales_outstanding(100_000, 1_000_000, 365):.1f} days")

    print("\n💰 VALUATION METRICS:")
    print(f"  EPS: {calculate_eps(100_000, 50_000):.2f}")
    print(f"  P/E Ratio: Moved to valuation module")
    print(f"  P/B Ratio: Moved to valuation module")

# =============================================================================
# GROWTH RATES
# =============================================================================

def calculate_yoy_growth(
    current_value: Optional[float],
    previous_value: Optional[float]
) -> Optional[float]:
    """
    Tốc độ tăng trưởng năm so với năm (Year-over-Year Growth)

    Công thức: ((Giá trị hiện tại - Giá trị năm trước) / Giá trị năm trước) × 100

    Đo lường tốc độ tăng trưởng của chỉ số tài chính giữa các năm.

    Diễn giải:
        - > 20%: Tăng trưởng vượt trội
        - 10-20%: Tăng trưởng rất tốt
        - 5-10%: Tăng trưởng tốt
        - 0-5%: Tăng trưởng vừa phải
        - < 0%: Sụt giảm

    Args:
        current_value: Giá trị năm hiện tại
        previous_value: Giá trị năm trước

    Returns:
        Tốc độ tăng trưởng YoY (%), hoặc None nếu không hợp lệ

    Examples:
        >>> calculate_yoy_growth(120_000, 100_000)
        20.0  # 20% growth
    """
    if previous_value is None or previous_value == 0 or current_value is None:
        return None
    return round(((current_value - previous_value) / previous_value) * 100, 2)

def calculate_qoq_growth(
    current_value: Optional[float],
    previous_value: Optional[float]
) -> Optional[float]:
    """
    Tốc độ tăng trưởng quý so với quý (Quarter-over-Quarter Growth)

    Công thức: ((Giá trị quý hiện tại - Giá trị quý trước) / Giá trị quý trước) × 100

    Đo lường tốc độ tăng trưởng của chỉ số tài chính giữa các quý.

    Diễn giải:
        - > 15%: Tăng trưởng quý vượt trội
        - 8-15%: Tăng trưởng quý tốt
        - 3-8%: Tăng trưởng quý vừa phải
        - 0-3%: Tăng trưởng quý chậm
        - < 0%: Sụt giảm quý

    Args:
        current_value: Giá trị quý hiện tại
        previous_value: Giá trị quý trước

    Returns:
        Tốc độ tăng trưởng QoQ (%), hoặc None nếu không hợp lệ

    Examples:
        >>> calculate_qoq_growth(115_000, 100_000)
        15.0  # 15% growth
    """
    if previous_value is None or previous_value == 0 or current_value is None:
        return None
    return round(((current_value - previous_value) / previous_value) * 100, 2)

# =============================================================================
# TTM (TRAILING TWELVE MONTHS) FORMULAS
# =============================================================================

def calculate_ttm_sum(
    q1: Optional[float],
    q2: Optional[float],
    q3: Optional[float],
    q4: Optional[float]
) -> Optional[float]:
    """
    TTM Sum (Trailing Twelve Months - Tổng 12 tháng gần nhất)

    Công thức: Q1 + Q2 + Q3 + Q4

    Tính tổng giá trị của 4 quý gần nhất để có cái nhìn toàn diện 
    về hiệu suất hoạt động trong 12 tháng.

    Args:
        q1: Giá trị quý 1
        q2: Giá trị quý 2
        q3: Giá trị quý 3
        q4: Giá trị quý 4

    Returns:
        TTM sum, hoặc None nếu tất cả đều None

    Examples:
        >>> calculate_ttm_sum(100_000, 120_000, 110_000, 130_000)
        460_000  # TTM total
    """
    values = [q1, q2, q3, q4]
    valid_values = [v for v in values if v is not None]
    
    if not valid_values:
        return None
    
    return sum(valid_values)

def calculate_ttm_avg(
    q1: Optional[float],
    q2: Optional[float],
    q3: Optional[float],
    q4: Optional[float]
) -> Optional[float]:
    """
    TTM Average (Trailing Twelve Months - Trung bình 12 tháng gần nhất)

    Công thức: (Q1 + Q2 + Q3 + Q4) / 4

    Tính trung bình giá trị của 4 quý gần nhất để smooth out 
    biến động theo mùa và có cái nhìn ổn định hơn.

    Args:
        q1: Giá trị quý 1
        q2: Giá trị quý 2
        q3: Giá trị quý 3
        q4: Giá trị quý 4

    Returns:
        TTM average, hoặc None nếu tất cả đều None

    Examples:
        >>> calculate_ttm_avg(100_000, 120_000, 110_000, 130_000)
        115_000  # TTM average
    """
    values = [q1, q2, q3, q4]
    valid_values = [v for v in values if v is not None]
    
    if not valid_values:
        return None
    
    return round(sum(valid_values) / len(valid_values), 2)

# =============================================================================
# ENHANCED EFFICIENCY RATIOS
# =============================================================================

def calculate_receivables_turnover(
    revenue: Optional[float],
    accounts_receivable: Optional[float]
) -> Optional[float]:
    """
    Tỷ lệ quay vòng các khoản phải thu (Receivables Turnover)

    Công thức: Doanh thu / Các khoản phải thu trung bình

    Đo lường hiệu quả thu hồi công nợ từ khách hàng.
    Tỷ lệ cao hơn = thu hồi nhanh hơn.

    Diễn giải:
        - > 12: Thu hồi rất nhanh
        - 8-12: Thu hồi tốt
        - 4-8: Thu hồi vừa phải
        - < 4: Thu hồi chậm

    Args:
        revenue: Doanh thu năm
        accounts_receivable: Các khoản phải thu trung bình

    Returns:
        Tỷ lệ quay vòng, hoặc None nếu không hợp lệ

    Examples:
        >>> calculate_receivables_turnover(1_000_000, 100_000)
        10.0  # 10 lần quay vòng/năm
    """
    return safe_divide(revenue, accounts_receivable)

def calculate_payables_turnover(
    cost_of_goods_sold: Optional[float],
    accounts_payable: Optional[float]
) -> Optional[float]:
    """
    Tỷ lệ quay vòng các khoản phải trả (Payables Turnover)

    Công thức: Giá vốn hàng bán / Các khoản phải trả trung bình

    Đo lường tốc độ trả nợ cho nhà cung cấp.
    Tỷ lệ cao hơn = trả nhanh hơn.

    Diễn giải:
        - > 12: Trả rất nhanh
        - 8-12: Trả tốt
        - 4-8: Trả vừa phải
        - < 4: Trả chậm

    Args:
        cost_of_goods_sold: Giá vốn hàng bán
        accounts_payable: Các khoản phải trả trung bình

    Returns:
        Tỷ lệ quay vòng, hoặc None nếu không hợp lệ

    Examples:
        >>> calculate_payables_turnover(600_000, 50_000)
        12.0  # 12 lần quay vòng/năm
    """
    return safe_divide(cost_of_goods_sold, accounts_payable)

    print("\n✅ All base formulas working!")
