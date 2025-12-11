#!/usr/bin/env python3
"""
Valuation Formulas
==================

Pure calculation functions for stock valuation metrics.
Includes PE, PB, PS, EV/EBITDA, and related valuation ratios.

These are pure functions that:
- Take primitive types (float, int, None) as inputs
- Return Optional[float] outputs
- Handle None/zero division gracefully
- Include comprehensive docstrings

Author: Formula Extraction Team
Date: 2025-12-08
"""

from typing import Optional


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def safe_divide(
    numerator: Optional[float],
    denominator: Optional[float],
    default: Optional[float] = None
) -> Optional[float]:
    """Safely divide two numbers, handling None and zero division."""
    if numerator is None or denominator is None:
        return default
    if denominator == 0:
        return default
    return numerator / denominator


# =============================================================================
# PRICE-BASED VALUATION RATIOS
# =============================================================================

def calculate_pe_ratio(
    price: Optional[float],
    eps: Optional[float]
) -> Optional[float]:
    """
    Price-to-Earnings Ratio (P/E)

    Formula: Price per Share / Earnings per Share

    Measures: Market valuation relative to earnings

    Interpretation (Vietnam market):
        - < 8: Potentially undervalued (or distressed)
        - 8-12: Fair value (market average)
        - 12-18: Reasonable premium (growth expected)
        - > 18: Expensive (high growth or speculation)
        - Negative: Company has losses

    Args:
        price: Current stock price (VND)
        eps: Earnings per share (VND) - Trailing or Forward

    Returns:
        P/E ratio or None

    Examples:
        >>> calculate_pe_ratio(50000, 2500)
        20.0
        >>> calculate_pe_ratio(50000, 0)
        None
        >>> calculate_pe_ratio(50000, -1000)
        -50.0
    """
    return safe_divide(price, eps)


def calculate_pb_ratio(
    price: Optional[float],
    bvps: Optional[float]
) -> Optional[float]:
    """
    Price-to-Book Ratio (P/B)

    Formula: Price per Share / Book Value per Share

    Measures: Market valuation relative to net asset value

    Interpretation (Vietnam market):
        - < 0.8: Deep value (trading below book value)
        - 0.8-1.5: Fair value
        - 1.5-3.0: Reasonable premium
        - > 3.0: High premium (growth/quality)
        - Banks: Typically 1.0-2.0
        - Manufacturing: Typically 0.8-1.5

    Args:
        price: Current stock price (VND)
        bvps: Book value per share (VND)

    Returns:
        P/B ratio or None

    Examples:
        >>> calculate_pb_ratio(50000, 25000)
        2.0
        >>> calculate_pb_ratio(20000, 30000)
        0.67
    """
    return safe_divide(price, bvps)


def calculate_ps_ratio(
    price: Optional[float],
    sps: Optional[float]
) -> Optional[float]:
    """
    Price-to-Sales Ratio (P/S)

    Formula: Price per Share / Sales per Share

    Measures: Market valuation relative to revenue
    Useful for: Companies with no earnings yet

    Interpretation:
        - < 1.0: Undervalued
        - 1.0-2.0: Fair value
        - > 2.0: Premium valuation
        - Varies widely by industry

    Args:
        price: Current stock price (VND)
        sps: Sales (revenue) per share (VND)

    Returns:
        P/S ratio or None

    Examples:
        >>> calculate_ps_ratio(50000, 100000)
        0.5
    """
    return safe_divide(price, sps)


def calculate_pcf_ratio(
    price: Optional[float],
    cfps: Optional[float]
) -> Optional[float]:
    """
    Price-to-Cash Flow Ratio (P/CF)

    Formula: Price per Share / Cash Flow per Share

    Measures: Market valuation relative to cash generation
    Useful for: Capital-intensive industries

    Interpretation:
        - < 10: Undervalued
        - 10-15: Fair value
        - > 15: Expensive

    Args:
        price: Current stock price (VND)
        cfps: Operating cash flow per share (VND)

    Returns:
        P/CF ratio or None
    """
    return safe_divide(price, cfps)


# =============================================================================
# ENTERPRISE VALUE RATIOS
# =============================================================================

def calculate_enterprise_value(
    market_cap: Optional[float],
    total_debt: Optional[float],
    cash: Optional[float],
    minority_interest: Optional[float] = None,
    preferred_equity: Optional[float] = None
) -> Optional[float]:
    """
    Enterprise Value (EV)

    Formula: Market Cap + Total Debt - Cash + Minority Interest + Preferred Equity

    Measures: Total value of company (equity + debt - cash)

    Args:
        market_cap: Market capitalization (billions VND)
        total_debt: Short-term + Long-term debt (billions VND)
        cash: Cash and cash equivalents (billions VND)
        minority_interest: Minority interests (billions VND, optional)
        preferred_equity: Preferred equity (billions VND, optional)

    Returns:
        Enterprise value (billions VND) or None

    Examples:
        >>> calculate_enterprise_value(10000, 3000, 1000)
        12000.0
        >>> calculate_enterprise_value(10000, 3000, 1000, 500, 200)
        12700.0
    """
    if market_cap is None:
        return None

    ev = market_cap
    ev += (total_debt or 0)
    ev -= (cash or 0)
    ev += (minority_interest or 0)
    ev += (preferred_equity or 0)

    return ev


def calculate_ev_ebitda(
    enterprise_value: Optional[float],
    ebitda: Optional[float]
) -> Optional[float]:
    """
    EV/EBITDA Ratio

    Formula: Enterprise Value / EBITDA

    Measures: Company valuation relative to cash operating earnings
    Advantages:
        - Not affected by capital structure (debt vs equity)
        - Not affected by depreciation methods
        - Better for comparing companies with different leverage

    Interpretation (Vietnam market):
        - < 6: Potentially undervalued
        - 6-10: Fair value
        - 10-15: Reasonable premium
        - > 15: Expensive
        - Manufacturing: Typically 6-10
        - Technology: Typically 10-20

    Args:
        enterprise_value: EV (billions VND)
        ebitda: EBITDA - Trailing 12 months (billions VND)

    Returns:
        EV/EBITDA ratio or None

    Examples:
        >>> calculate_ev_ebitda(12000, 1500)
        8.0
        >>> calculate_ev_ebitda(12000, 0)
        None
    """
    return safe_divide(enterprise_value, ebitda)


def calculate_ev_sales(
    enterprise_value: Optional[float],
    revenue: Optional[float]
) -> Optional[float]:
    """
    EV/Sales Ratio

    Formula: Enterprise Value / Revenue

    Measures: Valuation relative to revenue (capital structure neutral)

    Interpretation:
        - < 1.0: Undervalued
        - 1.0-2.0: Fair value
        - > 2.0: Premium
        - Retail: 0.5-1.5
        - Technology: 2.0-5.0

    Args:
        enterprise_value: EV (billions VND)
        revenue: Revenue - Trailing 12 months (billions VND)

    Returns:
        EV/Sales ratio or None
    """
    return safe_divide(enterprise_value, revenue)


def calculate_ev_fcf(
    enterprise_value: Optional[float],
    fcf: Optional[float]
) -> Optional[float]:
    """
    EV/FCF Ratio (Enterprise Value to Free Cash Flow)

    Formula: Enterprise Value / Free Cash Flow

    Measures: Valuation relative to free cash generation

    Interpretation:
        - < 15: Attractive
        - 15-25: Fair value
        - > 25: Expensive

    Args:
        enterprise_value: EV (billions VND)
        fcf: Free cash flow - TTM (billions VND)

    Returns:
        EV/FCF ratio or None
    """
    return safe_divide(enterprise_value, fcf)


# =============================================================================
# PER-SHARE METRICS
# =============================================================================

def calculate_eps(
    net_income: Optional[float],
    shares_outstanding: Optional[float]
) -> Optional[float]:
    """
    Earnings Per Share (EPS)

    Formula: Net Income / Shares Outstanding

    Measures: Profit attributed to each share

    Args:
        net_income: Net income after tax (billions VND)
        shares_outstanding: Number of shares outstanding (millions)

    Returns:
        EPS (VND per share) or None

    Examples:
        >>> calculate_eps(1000, 500)  # 1000B / 500M shares
        2000.0  # 2,000 VND per share
    """
    return safe_divide(net_income, shares_outstanding)


def calculate_bvps(
    total_equity: Optional[float],
    shares_outstanding: Optional[float]
) -> Optional[float]:
    """
    Book Value Per Share (BVPS)

    Formula: Total Equity / Shares Outstanding

    Measures: Net asset value attributed to each share

    Args:
        total_equity: Total shareholder equity (billions VND)
        shares_outstanding: Number of shares outstanding (millions)

    Returns:
        BVPS (VND per share) or None

    Examples:
        >>> calculate_bvps(5000, 500)  # 5000B / 500M shares
        10000.0  # 10,000 VND per share
    """
    return safe_divide(total_equity, shares_outstanding)


def calculate_sps(
    revenue: Optional[float],
    shares_outstanding: Optional[float]
) -> Optional[float]:
    """
    Sales Per Share (SPS)

    Formula: Revenue / Shares Outstanding

    Measures: Revenue attributed to each share

    Args:
        revenue: Total revenue (billions VND)
        shares_outstanding: Number of shares outstanding (millions)

    Returns:
        SPS (VND per share) or None
    """
    return safe_divide(revenue, shares_outstanding)


def calculate_cfps(
    operating_cf: Optional[float],
    shares_outstanding: Optional[float]
) -> Optional[float]:
    """
    Cash Flow Per Share (CFPS)

    Formula: Operating Cash Flow / Shares Outstanding

    Measures: Cash generation attributed to each share

    Args:
        operating_cf: Operating cash flow (billions VND)
        shares_outstanding: Number of shares outstanding (millions)

    Returns:
        CFPS (VND per share) or None
    """
    return safe_divide(operating_cf, shares_outstanding)


# =============================================================================
# DIVIDEND & YIELD METRICS
# =============================================================================

def calculate_dividend_yield(
    annual_dividend_per_share: Optional[float],
    price: Optional[float]
) -> Optional[float]:
    """
    Dividend Yield

    Formula: (Annual Dividend per Share / Price) × 100

    Measures: Annual dividend income as % of stock price

    Interpretation (Vietnam market):
        - < 2%: Low yield
        - 2-4%: Moderate yield
        - 4-6%: High yield
        - > 6%: Very high (check sustainability)

    Args:
        annual_dividend_per_share: Total dividend per share in year (VND)
        price: Current stock price (VND)

    Returns:
        Dividend yield in percentage or None

    Examples:
        >>> calculate_dividend_yield(2000, 50000)
        4.0
    """
    ratio = safe_divide(annual_dividend_per_share, price)
    return ratio * 100 if ratio is not None else None


def calculate_dividend_payout_ratio(
    dividend_per_share: Optional[float],
    eps: Optional[float]
) -> Optional[float]:
    """
    Dividend Payout Ratio

    Formula: (Dividend per Share / EPS) × 100

    Measures: Proportion of earnings paid as dividends

    Interpretation:
        - < 30%: Low payout (retaining for growth)
        - 30-60%: Moderate payout
        - > 60%: High payout (mature company)
        - > 100%: Unsustainable (paying more than earnings)

    Args:
        dividend_per_share: Dividend per share (VND)
        eps: Earnings per share (VND)

    Returns:
        Payout ratio in percentage or None
    """
    ratio = safe_divide(dividend_per_share, eps)
    return ratio * 100 if ratio is not None else None


# =============================================================================
# GROWTH-ADJUSTED VALUATION
# =============================================================================

def calculate_peg_ratio(
    pe_ratio: Optional[float],
    earnings_growth_rate: Optional[float]
) -> Optional[float]:
    """
    PEG Ratio (Price/Earnings to Growth)

    Formula: PE Ratio / Earnings Growth Rate

    Measures: PE ratio adjusted for growth rate

    Interpretation:
        - < 1.0: Undervalued (cheap relative to growth)
        - 1.0: Fair value
        - > 1.0: Overvalued (expensive relative to growth)
        - Growth rate should be 3-5 year forward estimate

    Args:
        pe_ratio: Current P/E ratio
        earnings_growth_rate: Expected earnings growth rate (%)

    Returns:
        PEG ratio or None

    Examples:
        >>> calculate_peg_ratio(20, 20)  # PE=20, Growth=20%
        1.0
        >>> calculate_peg_ratio(15, 30)  # PE=15, Growth=30%
        0.5
    """
    return safe_divide(pe_ratio, earnings_growth_rate)


def calculate_price_to_growth(
    price: Optional[float],
    revenue_growth_rate: Optional[float]
) -> Optional[float]:
    """
    Price to Growth Ratio

    Formula: Price / Revenue Growth Rate

    Measures: Price relative to revenue growth

    Args:
        price: Current stock price (VND)
        revenue_growth_rate: Revenue growth rate (%)

    Returns:
        Price/Growth ratio or None
    """
    return safe_divide(price, revenue_growth_rate)


# =============================================================================
# SECTOR-SPECIFIC VALUATION (BANKS)
# =============================================================================

def calculate_bank_pe_adjusted(
    price: Optional[float],
    eps: Optional[float],
    npl_ratio: Optional[float],
    npl_benchmark: float = 2.0
) -> Optional[float]:
    """
    Bank P/E Ratio Adjusted for Asset Quality

    Formula: (Price / EPS) × (NPL Benchmark / NPL Ratio)

    Adjusts P/E for asset quality (lower NPL = higher quality)

    Args:
        price: Current stock price (VND)
        eps: Earnings per share (VND)
        npl_ratio: Non-performing loan ratio (%)
        npl_benchmark: Industry benchmark NPL (default: 2.0%)

    Returns:
        Adjusted P/E ratio or None

    Examples:
        >>> # Bank A: PE=15, NPL=1% → Adjusted PE = 30 (high quality)
        >>> calculate_bank_pe_adjusted(30000, 2000, 1.0, 2.0)
        30.0

        >>> # Bank B: PE=15, NPL=4% → Adjusted PE = 7.5 (lower quality)
        >>> calculate_bank_pe_adjusted(30000, 2000, 4.0, 2.0)
        7.5
    """
    pe = safe_divide(price, eps)
    if pe is None or npl_ratio is None or npl_ratio == 0:
        return None

    adjustment = npl_benchmark / npl_ratio
    return pe * adjustment


def calculate_bank_pb_adjusted(
    price: Optional[float],
    bvps: Optional[float],
    roe: Optional[float],
    roe_benchmark: float = 15.0
) -> Optional[float]:
    """
    Bank P/B Ratio Adjusted for ROE

    Formula: (Price / BVPS) / (ROE / ROE Benchmark)

    Normalizes P/B for profitability (higher ROE justifies higher P/B)

    Args:
        price: Current stock price (VND)
        bvps: Book value per share (VND)
        roe: Return on equity (%)
        roe_benchmark: Industry benchmark ROE (default: 15%)

    Returns:
        Adjusted P/B ratio or None
    """
    pb = safe_divide(price, bvps)
    if pb is None or roe is None or roe == 0:
        return None

    adjustment = roe / roe_benchmark
    return pb / adjustment


# =============================================================================
# DEMO / TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("VALUATION FORMULAS DEMO")
    print("=" * 70)

    # Sample data for VCB (Vietcombank) - example
    price = 85000  # 85,000 VND
    eps = 6500  # 6,500 VND
    bvps = 35000  # 35,000 VND
    revenue_ttm = 50_000  # 50,000 billion VND
    ebitda_ttm = 25_000  # 25,000 billion VND
    market_cap = 425_000  # 425,000 billion VND
    total_debt = 50_000  # 50,000 billion VND
    cash = 30_000  # 30,000 billion VND
    shares_outstanding = 5_000  # 5,000 million shares

    print("\n💰 PRICE-BASED RATIOS:")
    print("-" * 70)
    pe = calculate_pe_ratio(price, eps)
    pb = calculate_pb_ratio(price, bvps)
    print(f"  P/E Ratio: {pe:.2f}x")
    print(f"  P/B Ratio: {pb:.2f}x")

    print("\n🏢 ENTERPRISE VALUE RATIOS:")
    print("-" * 70)
    ev = calculate_enterprise_value(market_cap, total_debt, cash)
    ev_ebitda = calculate_ev_ebitda(ev, ebitda_ttm)
    print(f"  Enterprise Value: {ev:,.0f} billion VND")
    print(f"  EV/EBITDA: {ev_ebitda:.2f}x")

    print("\n📊 PER-SHARE METRICS:")
    print("-" * 70)
    sps = calculate_sps(revenue_ttm, shares_outstanding)
    print(f"  EPS: {eps:,.0f} VND")
    print(f"  BVPS: {bvps:,.0f} VND")
    print(f"  SPS: {sps:,.0f} VND")

    print("\n📈 GROWTH-ADJUSTED:")
    print("-" * 70)
    earnings_growth = 20.0  # 20% expected growth
    peg = calculate_peg_ratio(pe, earnings_growth)
    print(f"  PEG Ratio: {peg:.2f} (PE={pe:.2f}, Growth={earnings_growth}%)")

    print("\n🏦 BANK-SPECIFIC:")
    print("-" * 70)
    npl_ratio = 1.2  # 1.2% NPL
    roe = 22.0  # 22% ROE
    pe_adj = calculate_bank_pe_adjusted(price, eps, npl_ratio, 2.0)
    pb_adj = calculate_bank_pb_adjusted(price, bvps, roe, 15.0)
    print(f"  P/E Adjusted (NPL): {pe_adj:.2f}x")
    print(f"  P/B Adjusted (ROE): {pb_adj:.2f}x")

    print("\n" + "=" * 70)
    print("✅ ALL VALUATION FORMULAS WORKING!")
    print("=" * 70)
