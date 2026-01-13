"""Bank Financial Formulas

Extracted pure calculation functions from bank_financial_calculator.py.

This module contains all financial formulas used for BANK entity calculations,
separated from data loading and orchestration logic.

Registry mapping:
- BIS_1: total_revenue (Tổng doanh thu)
- BIS_2: interest_income (Thu nhập lãi)
- BIS_3: interest_expense (Chi phí lãi vay)
- BIS_4: fee_and_commission_income (Thu nhập phí và hoa hồng)
- BIS_5: other_operating_income (Thu nhập hoạt động kinh doanh khác)
- BIS_6: other_operating_expense (Chi phí hoạt động kinh doanh khác)
- BIS_7: profit_before_provision_and_tax (Lợi nhuận trước trích lập dự phòng và thuế)
- BIS_8: provision_for_credit_losses (Trích lập dự phòng rủi ro)
- BIS_9: operating_profit (Lợi nhuận hoạt động)
- BIS_10: non_operating_income (Thu nhập ngoài hoạt động)
- BIS_11: non_operating_expense (Chi phí ngoài hoạt động)
- BIS_12: profit_before_tax (Lợi nhuận trước thuế)
- BIS_13: income_tax_expense (Chi phí thuế hiện hành)
- BIS_14: profit_after_tax (Lợi nhuận sau thuế)
- BIS_15: profit_from_discontinued (Lợi nhuận từ hoạt động kinh doanh đã ngừng)
- BIS_18: net_profit_from_continuing (Lợi nhuận từ hoạt động kinh doanh tiếp tục)
- BIS_20: net_profit (Lợi nhuận sau thuế)
- BBS_4: loans_and_advances_to_credit_institutions (Cho vay và tạm ứng các TCTD)
- BBS_7: investments_in_associates_and_joint_ventures (Đầu tư vào liên doanh và liên doanh)
- BBS_8: fixed_assets (Tài sản cố định)
- BBS_11: intangible_assets (Tài sản vô hình)
- BBS_12: goodwill (Lợi thế thương hiệu)
- BBS_14: other_assets (Tài sản khác)
- BBS_15: accumulated_depreciation (Hao mũ lũy kế tích lũy kế)
- BBS_16: provision_for_risks (Trích lập dự phòng rủi ro)
- BBS_18: non_current_assets (Tài sản dài hạn)
- BBS_19: inventories (Hàng tồn kho)
- BBS_20: current_assets (Tài sản ngắn hạn)
- BBS_21: other_current_assets (Tài sản ngắn hạn khác)
- BBS_22: assets_held_for_sale (Tài sản tài chính bán)
- BBS_23: total_assets (Tổng tài sản)
- BBS_24: short_term_borrowings (Vay và nợ thuê ngắn hạn)
- BBS_25: long_term_borrowings (Vay và nợ dài hạn)
- BBS_26: other_current_liabilities (Nợ ngắn hạn khác)
- BBS_27: total_current_liabilities (Tổng nợ ngắn hạn)
- BBS_30: long_term_liabilities (Nợ dài hạn)
- BBS_31: other_long_term_liabilities (Nợ dài hạn khác)
- BBS_32: total_long_term_liabilities (Tổng nợ dài hạn)
- BBS_33: total_liabilities (Tổng nợ phải trả)
- BBS_35: share_capital (Vốn cổ phần có ưu đãi)
- BBS_36: treasury_shares (Cổ phiếu thường)
- BBS_37: share_premium (Thặng dư vốn cổ phần)
- BBS_40: retained_earnings (Lợi nhuận giữ lại)
- BBS_41: other_comprehensive_income (Thu nhập TCDN khác)
- BBS_42: net_profit_before_tax (Lợi nhuận trước thuế)
- BBS_50: current_income_tax_expense (Chi phí thuế TNDN hiện hành)
- BBS_52: deferred_tax_expense (Chi phí thuế hoãn lại)
- BBS_53: net_profit_before_tax (Lợi nhuận trước thuế - Gộp)
- BBS_54: profit_before_tax (Lợi nhuận trước thuế - Gộp)
- BBS_55: income_tax_expense (Chi phí thuế)
- BBS_56: profit_before_tax (Lợi nhuận trước thuế)
- BBS_57: profit_before_tax (Lợi nhuận trước thuế)
- BBS_60: profit_after_tax (Lợi nhuận sau thuế)
- BBS_70: net_profit (Lợi nhuận sau thuế)
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any

try:
    from .utils import safe_divide, to_percentage
except ImportError:
    from utils import safe_divide, to_percentage


class BankFormulas:
    """Pure calculation functions for bank financial metrics."""
    
    # Profitability Ratios
    @staticmethod
    def calculate_nim(net_interest_income: float, total_earning_assets: float) -> Optional[float]:
        """
        Net Interest Margin (NIM).
        
        Formula: (Net Interest Income / Total Earning Assets) × 100
        Unit: Percentage (%)
        Good range: 2-5% (Vietnam banking sector)
        """
        if total_earning_assets == 0 or pd.isna(total_earning_assets):
            return None
        return round((net_interest_income / total_earning_assets) * 100, 2)
    
    @staticmethod
    def calculate_cir(operating_expense: float, operating_income: float) -> Optional[float]:
        """
        Cost to Income Ratio (CIR).
        
        Formula: (Operating Expenses / Operating Income) × 100
        Unit: Percentage (%)
        Good range: 30-60% (typical for Vietnam banks)
        """
        if operating_income == 0 or pd.isna(operating_income):
            return None
        return round((operating_expense / operating_income) * 100, 2)
    
    @staticmethod
    def calculate_plr(provision_for_credit_losses: float, total_loans: float) -> Optional[float]:
        """
        Provision to Loan Ratio (PLR).
        
        Formula: (Provision for Credit Losses / Total Loans) × 100
        Unit: Percentage (%)
        Good range: < 5% (healthy bank)
        """
        if total_loans == 0 or pd.isna(total_loans):
            return None
        return round((provision_for_credit_losses / total_loans) * 100, 2)
    
    @staticmethod
    def calculate_ldr(loan_loss_allowance: float, customer_loans: float, other_borrowings: float) -> Optional[float]:
        """
        Loans to Deposit Ratio (LDR).
        
        Formula: ((Customer Loans + Other Borrowings) - (Loan Loss Allowance)) / 
                 ((Customer Loans + Other Borrowings) - Loan Loss Allowance + Total Deposits)
        Unit: Percentage (%)
        Good range: 80-100% (regulated requirement)
        """
        total_funds = customer_loans + other_borrowings
        net_funds = total_funds - loan_loss_allowance
        
        # We need deposits data which might not be available in the current dataset
        # This is a simplified calculation
        if total_funds == 0 or pd.isna(total_funds):
            return None
            
        # Placeholder for deposits - would need actual deposits data
        deposits = 1.0  # Simplified - would need actual data
        
        ldr = (net_funds / (net_funds + deposits)) * 100
        return round(ldr, 2)
    
    @staticmethod
    def calculate_car(loan_loss_allowance: float, total_loans: float, risk_weighted_assets: float) -> Optional[float]:
        """
        Capital Adequacy Ratio (CAR).
        
        Formula: (Risk-Weighted Assets / (Loan Loss Allowance + Total Loans))
        Unit: Ratio (x:1)
        Good range: > 8% (minimum regulatory requirement)
        """
        if total_loans == 0 or pd.isna(total_loans):
            return None
        return round((risk_weighted_assets / (loan_loss_allowance + total_loans)), 2)
    
    # Asset Quality Metrics
    @staticmethod
    def calculate_npl_ratio(non_performing_loans: float, total_loans: float) -> Optional[float]:
        """
        Non-Performing Loan Ratio.
        
        Formula: (Non-Performing Loans / Total Loans) × 100
        Unit: Percentage (%)
        Good range: < 3% (healthy bank)
        """
        if total_loans == 0 or pd.isna(total_loans):
            return None
        return round((non_performing_loans / total_loans) * 100, 2)
    
    @staticmethod
    # Efficiency Metrics
    @staticmethod
    def calculate_efficiency_ratio(operating_income: float, operating_expense: float) -> Optional[float]:
        """
        Bank Efficiency Ratio.
        
        Formula: Operating Income / Operating Expenses
        Unit: Ratio (x:1)
        Good range: > 1.2 (efficient)
        """
        if operating_expense == 0 or pd.isna(operating_expense):
            return None
        return round(operating_income / operating_expense, 2)
    
    # Utility Functions
    # safe_divide is imported from utils and used directly in calculations where needed,
    # or provided by the base calculator if using object methods.
    # But since these are static methods, we rely on the import.


# ============================================================================
# Bank Group Metrics Calculator
# ============================================================================

# Metrics to aggregate by weighted average (by total_assets)
WEIGHTED_AVG_METRICS = [
    'nim_q', 'cir', 'npl_ratio', 'debt_group2_ratio', 'llcr', 'casa_ratio',
    'ldr_pure', 'ldr_regulated', 'roea_ttm', 'roaa_ttm', 'asset_yield_q',
    'funding_cost_q', 'loan_yield_q', 'provision_to_loan', 'credit_cost',
    'nii_toi', 'noii_toi',
    # Growth rates also weighted
    'nii_growth_yoy', 'toi_growth_yoy', 'ppop_growth_yoy', 'pbt_growth_yoy',
    'npatmi_growth_yoy', 'credit_growth_ytd', 'customer_deposit_growth_ytd',
]

# Metrics to aggregate by sum
SUM_METRICS = [
    'nii', 'noii', 'toi', 'opex', 'ppop', 'pbt', 'npatmi', 'npatmi_ttm',
    'total_assets', 'total_credit', 'total_customer_deposit', 'total_liabilities',
    'total_equity', 'npl_amount', 'debt_group2', 'loan_provision_balance',
    'interest_income', 'interest_expense', 'iea', 'ibl',
]


def calculate_bank_group_metrics(
    input_path: str = "DATA/processed/fundamental/bank/bank_financial_metrics.parquet",
    output_path: str = "DATA/processed/fundamental/bank/bank_group_metrics.parquet",
) -> pd.DataFrame:
    """
    Calculate aggregated bank metrics by tier group (SOCB, Tier-1, Tier-2, Tier-3).

    - Ratio metrics: Weighted average by total_assets
    - Absolute metrics: Sum

    Args:
        input_path: Path to individual bank metrics parquet
        output_path: Path to save group metrics parquet

    Returns:
        DataFrame with aggregated metrics per tier per period
    """
    from pathlib import Path
    from config.sector_analysis.bank_config import BANK_CLASSIFICATION, get_bank_tier

    # Load individual bank data
    df = pd.read_parquet(input_path)

    # Add tier column
    df['tier'] = df['symbol'].apply(get_bank_tier)

    # Filter only known tiers (exclude 'Unknown')
    df = df[df['tier'] != 'Unknown'].copy()

    # Group by tier and period
    group_cols = ['tier', 'year', 'quarter']

    results = []

    for (tier, year, quarter), group in df.groupby(group_cols):
        row = {
            'tier': tier,
            'year': year,
            'quarter': quarter,
            'period': f"{int(quarter)}Q{str(int(year))[-2:]}",
            'bank_count': len(group),
        }

        # Get total assets for weighting
        total_assets_sum = group['total_assets'].sum()

        # Calculate weighted averages for ratio metrics
        for col in WEIGHTED_AVG_METRICS:
            if col in group.columns:
                # Filter valid values
                valid = group[[col, 'total_assets']].dropna()
                if len(valid) > 0 and total_assets_sum > 0:
                    weighted_sum = (valid[col] * valid['total_assets']).sum()
                    row[f'{col}_wavg'] = round(weighted_sum / valid['total_assets'].sum(), 4)
                else:
                    row[f'{col}_wavg'] = None

        # Calculate sums for absolute metrics
        for col in SUM_METRICS:
            if col in group.columns:
                row[f'{col}_sum'] = group[col].sum()

        results.append(row)

    # Create result DataFrame
    result_df = pd.DataFrame(results)

    # Sort by tier order and period
    tier_order = {'SOCB': 0, 'Tier-1': 1, 'Tier-2': 2, 'Tier-3': 3}
    result_df['tier_order'] = result_df['tier'].map(tier_order)
    result_df = result_df.sort_values(['year', 'quarter', 'tier_order'])
    result_df = result_df.drop(columns=['tier_order'])

    # Save to parquet
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_parquet(output_file, index=False)

    print(f"✅ Bank group metrics saved: {output_path}")
    print(f"   Shape: {result_df.shape}")
    print(f"   Tiers: {result_df['tier'].unique().tolist()}")
    print(f"   Periods: {result_df['period'].nunique()}")

    return result_df


# ============================================================================
# Quarterly to Yearly Aggregation
# ============================================================================

# Flow metrics: Sum of 4 quarters
FLOW_METRICS = [
    'nii', 'noii', 'toi', 'opex', 'ppop', 'provision_expense', 'pbt', 'npatmi',
    'interest_income', 'interest_expense',
]

# Stock metrics: Use Q4 value (end of year) or latest available
STOCK_METRICS = [
    'total_assets', 'total_credit', 'total_customer_deposit', 'total_liabilities',
    'total_equity', 'charter_capital', 'npl_amount', 'debt_group2',
    'loan_provision_balance', 'iea', 'ibl', 'equity_avg_2q', 'assets_avg_2q',
    'casa_ratio', 'ldr_pure', 'ldr_regulated',
]

# TTM metrics: Already annualized, use Q4 value
TTM_METRICS = [
    'roea_ttm', 'roaa_ttm', 'eps_ttm', 'bvps', 'npatmi_ttm',
]


def calculate_yearly_metrics(
    input_path: str = "DATA/processed/fundamental/bank/bank_financial_metrics.parquet",
    output_path: str = "DATA/processed/fundamental/bank/bank_financial_metrics_yearly.parquet",
) -> pd.DataFrame:
    """
    Calculate yearly bank metrics from quarterly data.

    Aggregation logic:
    - Flow metrics (P&L): Sum of 4 quarters
    - Stock metrics (BS): Q4 value (or latest quarter for current year)
    - TTM metrics: Q4 value (already annualized)
    - Ratios: Recalculate from yearly aggregates

    For current year (incomplete), uses trailing sum/latest available.

    Args:
        input_path: Path to quarterly bank metrics parquet
        output_path: Path to save yearly metrics parquet

    Returns:
        DataFrame with yearly metrics per bank
    """
    from pathlib import Path

    # Load quarterly data
    df = pd.read_parquet(input_path)

    results = []

    for symbol in df['symbol'].unique():
        bank_df = df[df['symbol'] == symbol].copy()

        for year in bank_df['year'].unique():
            year_df = bank_df[bank_df['year'] == year].sort_values('quarter')
            quarters_available = year_df['quarter'].tolist()
            num_quarters = len(quarters_available)

            # Skip if no data
            if num_quarters == 0:
                continue

            row = {
                'symbol': symbol,
                'year': int(year),
                'quarter': 0,  # 0 indicates yearly
                'freq_code': 'Y',
                'quarters_aggregated': num_quarters,
                'report_date': year_df['report_date'].max(),
            }

            # Flow metrics: Sum of available quarters
            for col in FLOW_METRICS:
                if col in year_df.columns:
                    row[col] = year_df[col].sum()

            # Stock metrics: Use latest quarter value
            latest_q = year_df.iloc[-1]
            for col in STOCK_METRICS:
                if col in year_df.columns:
                    row[col] = latest_q[col]

            # TTM metrics: Use latest quarter value
            for col in TTM_METRICS:
                if col in year_df.columns:
                    row[col] = latest_q[col]

            # Recalculate ratios from yearly data
            # NIM = (interest_income - interest_expense) / avg(iea) * 100
            if row.get('interest_income') and row.get('interest_expense') and row.get('iea'):
                net_interest = row['interest_income'] - row['interest_expense']
                iea_avg = year_df['iea'].mean()
                if iea_avg > 0:
                    row['nim_q'] = round((net_interest / iea_avg) * 100 / num_quarters, 2)

            # CIR = abs(opex) / toi * 100 (opex is stored as negative)
            if row.get('toi') and row['toi'] > 0:
                row['cir'] = round((abs(row.get('opex', 0)) / row['toi']) * 100, 2)

            # NII/TOI ratio
            if row.get('toi') and row['toi'] > 0:
                row['nii_toi'] = round((row.get('nii', 0) / row['toi']) * 100, 2)
                row['noii_toi'] = round((row.get('noii', 0) / row['toi']) * 100, 2)

            # NPL ratio = npl_amount / total_credit * 100
            if row.get('total_credit') and row['total_credit'] > 0:
                row['npl_ratio'] = round((row.get('npl_amount', 0) / row['total_credit']) * 100, 2)
                row['debt_group2_ratio'] = round((row.get('debt_group2', 0) / row['total_credit']) * 100, 2)

            # LLCR = loan_provision_balance / npl_amount * 100
            if row.get('npl_amount') and row['npl_amount'] > 0:
                row['llcr'] = round((row.get('loan_provision_balance', 0) / row['npl_amount']) * 100, 2)

            # Provision to loan = loan_provision_balance / total_credit * 100
            if row.get('total_credit') and row['total_credit'] > 0:
                row['provision_to_loan'] = round((row.get('loan_provision_balance', 0) / row['total_credit']) * 100, 2)

            # Credit cost = provision_expense / total_credit * 100
            if row.get('total_credit') and row['total_credit'] > 0:
                row['credit_cost'] = round((row.get('provision_expense', 0) / row['total_credit']) * 100, 2)

            # Asset yield = interest_income / iea * 100
            if row.get('iea') and row['iea'] > 0:
                iea_avg = year_df['iea'].mean()
                row['asset_yield_q'] = round((row.get('interest_income', 0) / iea_avg) * 100 / num_quarters, 2)

            # Funding cost = interest_expense / ibl * 100
            if row.get('ibl') and row['ibl'] > 0:
                ibl_avg = year_df['ibl'].mean()
                row['funding_cost_q'] = round((row.get('interest_expense', 0) / ibl_avg) * 100 / num_quarters, 2)

            results.append(row)

    # Create result DataFrame
    result_df = pd.DataFrame(results)

    # Sort
    result_df = result_df.sort_values(['symbol', 'year']).reset_index(drop=True)

    # Calculate YoY growth metrics
    growth_metrics = {
        'nii': 'nii_growth_yoy',
        'toi': 'toi_growth_yoy',
        'ppop': 'ppop_growth_yoy',
        'pbt': 'pbt_growth_yoy',
        'npatmi': 'npatmi_growth_yoy',
        'total_credit': 'credit_growth_yoy',
        'total_customer_deposit': 'deposit_growth_yoy',
    }

    for base_col, growth_col in growth_metrics.items():
        if base_col in result_df.columns:
            result_df[growth_col] = result_df.groupby('symbol')[base_col].pct_change(fill_method=None) * 100
            result_df[growth_col] = result_df[growth_col].round(2)

    # Add aliases for dashboard compatibility (expects _ytd columns)
    result_df['credit_growth_ytd'] = result_df['credit_growth_yoy']
    result_df['customer_deposit_growth_ytd'] = result_df['deposit_growth_yoy']

    # Save to parquet
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_parquet(output_file, index=False)

    print(f"✅ Bank yearly metrics saved: {output_path}")
    print(f"   Shape: {result_df.shape}")
    print(f"   Symbols: {result_df['symbol'].nunique()}")
    print(f"   Years: {sorted(result_df['year'].unique())}")

    return result_df


# Main execution for standalone run
if __name__ == "__main__":
    print("Calculating bank group metrics...")
    df = calculate_bank_group_metrics()
    print("\nSample output:")
    print(df[['tier', 'period', 'bank_count', 'nim_q_wavg', 'npl_ratio_wavg', 'toi_sum']].tail(8))

    print("\n" + "="*60)
    print("Calculating bank yearly metrics...")
    df_yearly = calculate_yearly_metrics()
    print("\nSample yearly output:")
    print(df_yearly[['symbol', 'year', 'quarters_aggregated', 'toi', 'npatmi', 'nim_q', 'npl_ratio']].tail(10))