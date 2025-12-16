"""
Financial Tables - Pivot Table Renderers
========================================
Creates pivot tables with KEYCODE as rows and periods as columns.
Follows the reference design from the Income Statement screenshot.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from WEBAPP.core.styles import render_styled_table

# ============================================================================
# CONSTANTS
# ============================================================================

# Brand colors
HEADER_BG = "#295CA9"
HEADER_TEXT = "#FFFFFF"
ROW_ALT_BG = "#F8FAFC"

# Metric configurations for each table type
INCOME_STATEMENT_METRICS = [
    {"keycode": "NET_REVENUE", "source": "net_revenue", "format": "billions", "label": "Net Revenue"},
    {"keycode": "NET_REVENUE_GR", "source": "net_revenue", "format": "growth", "label": "Net Revenue Growth"},
    {"keycode": "GROSS_PROFIT", "source": "gross_profit", "format": "billions", "label": "Gross Profit"},
    {"keycode": "GROSS_PROFIT_GR", "source": "gross_profit", "format": "growth", "label": "Gross Profit Growth"},
    {"keycode": "GROSS_MARGIN", "source": "gross_profit_margin", "format": "percent", "label": "Gross Margin"},
    {"keycode": "SGA", "source": "sga", "format": "billions", "label": "SG&A"},
    {"keycode": "SGA_DTT_RATIO", "source": "sga_ratio", "format": "percent", "label": "SG&A/Revenue"},
    {"keycode": "EBIT", "source": "ebit", "format": "billions", "label": "EBIT"},
    {"keycode": "EBIT_GR", "source": "ebit", "format": "growth", "label": "EBIT Growth"},
    {"keycode": "EBIT_MARGIN", "source": "ebit_margin", "format": "percent", "label": "EBIT Margin"},
    {"keycode": "EBITDA", "source": "ebitda", "format": "billions", "label": "EBITDA"},
    {"keycode": "EBITDA_GR", "source": "ebitda", "format": "growth", "label": "EBITDA Growth"},
    {"keycode": "EBITDA_MARGIN", "source": "ebitda_margin", "format": "percent", "label": "EBITDA Margin"},
    {"keycode": "NET_FINANCE_INCOME", "source": "net_finance_income", "format": "billions", "label": "Net Finance Income"},
    {"keycode": "NPATMI", "source": "npatmi", "format": "billions", "label": "NPATMI"},
    {"keycode": "NPATMI_GR", "source": "npatmi", "format": "growth", "label": "NPATMI Growth"},
    {"keycode": "NET_MARGIN", "source": "net_margin", "format": "percent", "label": "Net Margin"},
]

BALANCE_SHEET_METRICS = [
    {"keycode": "TOTAL_ASSETS", "source": "total_assets", "format": "billions", "label": "Total Assets"},
    {"keycode": "TOTAL_ASSETS_GR", "source": "total_assets", "format": "growth", "label": "Total Assets Growth"},
    {"keycode": "CURRENT_ASSETS", "source": "current_assets", "format": "billions", "label": "Current Assets"},
    {"keycode": "CASH", "source": "cash", "format": "billions", "label": "Cash & Equivalents"},
    {"keycode": "INVENTORY", "source": "inventory", "format": "billions", "label": "Inventory"},
    {"keycode": "ACCOUNT_RECEIVABLE", "source": "account_receivable", "format": "billions", "label": "Account Receivable"},
    {"keycode": "TANGIBLE_FIXED_ASSET", "source": "tangible_fixed_asset", "format": "billions", "label": "Tangible Fixed Assets"},
    {"keycode": "TOTAL_LIABILITIES", "source": "total_liabilities", "format": "billions", "label": "Total Liabilities"},
    {"keycode": "CURRENT_LIABILITIES", "source": "current_liabilities", "format": "billions", "label": "Current Liabilities"},
    {"keycode": "ST_DEBT", "source": "st_debt", "format": "billions", "label": "Short-term Debt"},
    {"keycode": "LT_DEBT", "source": "lt_debt", "format": "billions", "label": "Long-term Debt"},
    {"keycode": "NET_DEBT", "source": "net_debt", "format": "billions", "label": "Net Debt"},
    {"keycode": "TOTAL_EQUITY", "source": "total_equity", "format": "billions", "label": "Total Equity"},
    {"keycode": "TOTAL_EQUITY_GR", "source": "total_equity", "format": "growth", "label": "Total Equity Growth"},
    {"keycode": "WORKING_CAPITAL", "source": "working_capital", "format": "billions", "label": "Working Capital"},
    {"keycode": "CURRENT_RATIO", "source": "current_ratio", "format": "ratio", "label": "Current Ratio"},
    {"keycode": "QUICK_RATIO", "source": "quick_ratio", "format": "ratio", "label": "Quick Ratio"},
    {"keycode": "CASH_RATIO", "source": "cash_ratio", "format": "ratio", "label": "Cash Ratio"},
    {"keycode": "DEBT_TO_EQUITY", "source": "debt_to_equity", "format": "ratio", "label": "Debt/Equity"},
    {"keycode": "DEBT_TO_ASSETS", "source": "debt_to_assets", "format": "percent", "label": "Debt/Assets"},
    {"keycode": "DEPRECIATION_RATE", "source": "depreciation_rate", "format": "percent", "label": "Depreciation Rate"},
    {"keycode": "CIP_RATE", "source": "cip_rate", "format": "percent", "label": "CIP Rate"},
]

CASH_FLOW_METRICS = [
    {"keycode": "OPERATING_CF", "source": "operating_cf", "format": "billions", "label": "Operating CF"},
    {"keycode": "OPERATING_CF_GR", "source": "operating_cf", "format": "growth", "label": "Operating CF Growth"},
    {"keycode": "INVESTMENT_CF", "source": "investment_cf", "format": "billions", "label": "Investment CF"},
    {"keycode": "FINANCING_CF", "source": "financing_cf", "format": "billions", "label": "Financing CF"},
    {"keycode": "CAPEX", "source": "capex", "format": "billions", "label": "Capex"},
    {"keycode": "DEPRECIATION", "source": "depreciation", "format": "billions", "label": "Depreciation"},
    {"keycode": "FCF", "source": "fcf", "format": "billions", "label": "Free Cash Flow"},
    {"keycode": "FCF_GR", "source": "fcf", "format": "growth", "label": "FCF Growth"},
    {"keycode": "FCFE", "source": "fcfe", "format": "billions", "label": "FCFE"},
    {"keycode": "FCFE_GR", "source": "fcfe", "format": "growth", "label": "FCFE Growth"},
    {"keycode": "DELTA_WORKING_CAPITAL", "source": "delta_working_capital", "format": "billions", "label": "Δ Working Capital"},
    {"keycode": "DELTA_NET_BORROWING", "source": "delta_net_borrowing", "format": "billions", "label": "Δ Net Borrowing"},
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_yoy_growth(df: pd.DataFrame, metric: str) -> pd.Series:
    """
    Calculate Year-over-Year growth rate for a metric.

    For quarterly data: compares to same quarter last year (4 periods back)
    For yearly data: compares to previous year (1 period back)

    Returns growth as percentage (e.g., 10.5 for 10.5%)
    """
    if metric not in df.columns:
        return pd.Series([np.nan] * len(df), index=df.index)

    # Determine period offset based on data frequency
    has_quarter = 'quarter' in df.columns and df['quarter'].notna().any()
    offset = 4 if has_quarter else 1

    current = df[metric]
    previous = df[metric].shift(offset)

    # Calculate growth: (current - previous) / abs(previous) * 100
    growth = np.where(
        (previous != 0) & previous.notna() & current.notna(),
        (current - previous) / np.abs(previous) * 100,
        np.nan
    )

    return pd.Series(growth, index=df.index)


def calculate_sga_ratio(df: pd.DataFrame) -> pd.Series:
    """Calculate SGA/Net Revenue ratio as percentage."""
    if 'sga' not in df.columns or 'net_revenue' not in df.columns:
        return pd.Series([np.nan] * len(df), index=df.index)

    return np.where(
        df['net_revenue'] != 0,
        np.abs(df['sga']) / df['net_revenue'] * 100,
        np.nan
    )


def format_value(value: float, format_type: str) -> str:
    """Format a value based on its type."""
    if pd.isna(value):
        return "-"

    if format_type == "billions":
        # Convert VND to billions VND
        value_in_billions = value / 1e9
        return f"{value_in_billions:,.1f}"
    elif format_type == "percent":
        return f"{value:.1f}%"
    elif format_type == "growth":
        if value > 0:
            return f"+{value:.1f}%"
        else:
            return f"{value:.1f}%"
    elif format_type == "ratio":
        return f"{value:.2f}x"
    else:
        return f"{value:,.2f}"


def get_period_label(row: pd.Series, period_type: str) -> str:
    """Generate period label like '1Q24' or '2024'."""
    year = row.get('year', '')
    if period_type == 'Quarterly':
        quarter = row.get('quarter', '')
        year_short = str(int(year))[-2:] if year else ''
        return f"{int(quarter)}Q{year_short}" if quarter else str(year)
    return str(int(year)) if year else ''


def prepare_data_with_calculations(df: pd.DataFrame, period_type: str) -> pd.DataFrame:
    """
    Prepare dataframe with all calculated fields.
    """
    result = df.copy()

    # Sort by date
    if 'report_date' in result.columns:
        result = result.sort_values('report_date')

    # Add period labels
    result['period_label'] = result.apply(lambda r: get_period_label(r, period_type), axis=1)

    # Calculate SGA ratio
    result['sga_ratio'] = calculate_sga_ratio(result)

    return result


def create_pivot_dataframe(
    df: pd.DataFrame,
    metrics_config: List[Dict],
    period_type: str
) -> Tuple[pd.DataFrame, int, int]:
    """
    Create a pivot table DataFrame with KEYCODE as rows and periods as columns.

    Returns:
        Tuple of (pivot_df, num_metrics, num_periods)
    """
    # Prepare data
    data = prepare_data_with_calculations(df, period_type)
    periods = data['period_label'].tolist()

    # Build pivot data
    rows = []
    for metric in metrics_config:
        keycode = metric['keycode']
        source = metric['source']
        fmt = metric['format']

        row_data = {'KEYCODE': keycode}

        for idx, period in enumerate(periods):
            period_row = data[data['period_label'] == period]
            if period_row.empty:
                row_data[period] = "-"
                continue

            if fmt == 'growth':
                # Calculate growth for this metric
                growth_values = calculate_yoy_growth(data, source)
                value = growth_values.iloc[idx] if idx < len(growth_values) else np.nan
            elif source in data.columns:
                value = period_row[source].iloc[0]
            else:
                value = np.nan

            row_data[period] = format_value(value, fmt)

        rows.append(row_data)

    pivot_df = pd.DataFrame(rows)

    # Count actual metrics (excluding those with all missing data)
    num_metrics = len([r for r in rows if any(v != "-" for k, v in r.items() if k != 'KEYCODE')])
    num_periods = len(periods)

    return pivot_df, num_metrics, num_periods


def style_pivot_table(pivot_df: pd.DataFrame):
    """Apply styling to the pivot table."""

    def highlight_negative(val):
        """Highlight negative values in red."""
        if isinstance(val, str) and val != "-":
            # Check if it's a negative number
            try:
                num = float(val.replace('%', '').replace(',', ''))
                if num < 0:
                    return 'color: #DC2626'
            except (ValueError, AttributeError):
                pass
        return ''

    def alternate_rows(row):
        """Alternate row background colors."""
        idx = row.name
        if idx % 2 == 1:
            return [f'background-color: {ROW_ALT_BG}'] * len(row)
        return [''] * len(row)

    styled = pivot_df.style.applymap(highlight_negative).apply(alternate_rows, axis=1)

    return styled


# ============================================================================
# MAIN RENDER FUNCTIONS
# ============================================================================

def render_income_statement_table(df: pd.DataFrame, period_type: str = 'Quarterly') -> None:
    """
    Render Income Statement pivot table.

    Args:
        df: DataFrame with financial data
        period_type: 'Quarterly' or 'Yearly'
    """
    if df.empty:
        st.warning("No data available for Income Statement")
        return

    st.markdown("#### Income Statement")

    pivot_df, num_metrics, num_periods = create_pivot_dataframe(
        df, INCOME_STATEMENT_METRICS, period_type
    )

    st.caption(f"📊 Showing {num_metrics} metrics across {num_periods} {period_type.lower()} periods")

    # Use styled HTML table instead of st.dataframe for better dark theme support
    html_table = render_styled_table(pivot_df, highlight_first_col=True)
    st.markdown(html_table, unsafe_allow_html=True)


def render_balance_sheet_table(df: pd.DataFrame, period_type: str = 'Quarterly') -> None:
    """
    Render Balance Sheet pivot table.

    Args:
        df: DataFrame with financial data
        period_type: 'Quarterly' or 'Yearly'
    """
    if df.empty:
        st.warning("No data available for Balance Sheet")
        return

    st.markdown("#### Balance Sheet")

    # Filter out metrics that don't exist in data
    available_metrics = [
        m for m in BALANCE_SHEET_METRICS
        if m['source'] in df.columns or m['format'] == 'growth'
    ]

    pivot_df, num_metrics, num_periods = create_pivot_dataframe(
        df, available_metrics, period_type
    )

    st.caption(f"📊 Showing {num_metrics} metrics across {num_periods} {period_type.lower()} periods")

    # Use styled HTML table instead of st.dataframe for better dark theme support
    html_table = render_styled_table(pivot_df, highlight_first_col=True)
    st.markdown(html_table, unsafe_allow_html=True)


def render_cash_flow_table(df: pd.DataFrame, period_type: str = 'Quarterly') -> None:
    """
    Render Cash Flow pivot table.

    Args:
        df: DataFrame with financial data
        period_type: 'Quarterly' or 'Yearly'
    """
    if df.empty:
        st.warning("No data available for Cash Flow")
        return

    st.markdown("#### Cash Flow")

    # Filter out metrics that don't exist in data
    available_metrics = [
        m for m in CASH_FLOW_METRICS
        if m['source'] in df.columns or m['format'] == 'growth'
    ]

    pivot_df, num_metrics, num_periods = create_pivot_dataframe(
        df, available_metrics, period_type
    )

    st.caption(f"📊 Showing {num_metrics} metrics across {num_periods} {period_type.lower()} periods")

    # Use styled HTML table instead of st.dataframe for better dark theme support
    html_table = render_styled_table(pivot_df, highlight_first_col=True)
    st.markdown(html_table, unsafe_allow_html=True)
