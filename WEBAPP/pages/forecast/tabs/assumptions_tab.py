"""
Assumptions Tab
===============
Tab 4: Sector Assumptions from BSC Masterfiles.

Features:
- Sector selector (Banking, Brokerage, MWG, Utility)
- Summary cards with sector KPIs
- Detail table with full metrics
- Glassmorphism styling consistent with dashboard

Author: AI Assistant
Date: 2026-01-12
"""

import streamlit as st
import pandas as pd

from WEBAPP.services.assumptions_service import AssumptionsService
from WEBAPP.core.styles import render_styled_table


# ============================================================================
# FORMATTING HELPERS
# ============================================================================

def format_percent(val, decimals: int = 1) -> str:
    """Format value as percentage."""
    if pd.isna(val) or val is None:
        return '-'
    pct = val * 100 if abs(val) < 1 else val
    return f"{pct:.{decimals}f}%"


def format_number(val, decimals: int = 1, suffix: str = '') -> str:
    """Format number with decimals."""
    if pd.isna(val) or val is None or val == 0:
        return '-'
    return f"{val:,.{decimals}f}{suffix}"


def format_billions(val) -> str:
    """Format value in billions VND."""
    if pd.isna(val) or val is None or val == 0:
        return '-'
    if val >= 1000:
        return f"{val/1000:,.1f}T"
    return f"{val:,.0f}B"


def format_price(val) -> str:
    """Format price in thousands VND."""
    if pd.isna(val) or val is None or val == 0:
        return '-'
    return f"{val:,.0f}"


def format_upside(val) -> str:
    """Format upside with color."""
    if pd.isna(val) or val is None:
        return '-'
    pct = val * 100 if abs(val) < 1 else val
    color = '#22C55E' if pct >= 0 else '#EF4444'
    return f'<span style="color:{color};font-weight:600;">{pct:+.1f}%</span>'


# ============================================================================
# CARD RENDERERS
# ============================================================================

def render_kpi_card(label: str, value: str, color: str = "#8B5CF6") -> str:
    """Render a single KPI card with glassmorphism style."""
    return f'''
    <div style="
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(6, 182, 212, 0.05));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        text-align: center;
        transition: all 0.3s ease;
    ">
        <div style="
            color: #94A3B8;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.5rem;
        ">{label}</div>
        <div style="
            color: {color};
            font-size: 1.5rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
        ">{value}</div>
    </div>
    '''


def render_banking_cards(summary: dict):
    """Render banking sector summary cards."""
    cols = st.columns(4)

    with cols[0]:
        st.markdown(render_kpi_card(
            "Stocks Covered",
            str(summary.get('stock_count', 0)),
            "#A78BFA"
        ), unsafe_allow_html=True)

    with cols[1]:
        roe_val = summary.get('avg_roe')
        roe_str = f"{roe_val*100:.1f}%" if roe_val else "-"
        st.markdown(render_kpi_card(
            "Avg ROE 25F",
            roe_str,
            "#22C55E"
        ), unsafe_allow_html=True)

    with cols[2]:
        nim_val = summary.get('avg_nim')
        nim_str = f"{nim_val*100:.1f}%" if nim_val else "-"
        st.markdown(render_kpi_card(
            "Avg NIM 25F",
            nim_str,
            "#06B6D4"
        ), unsafe_allow_html=True)

    with cols[3]:
        npl_val = summary.get('avg_npl')
        npl_str = f"{npl_val*100:.1f}%" if npl_val else "-"
        st.markdown(render_kpi_card(
            "Avg NPL 25F",
            npl_str,
            "#F59E0B"
        ), unsafe_allow_html=True)


def render_brokerage_cards(summary: dict):
    """Render brokerage sector summary cards."""
    cols = st.columns(4)

    with cols[0]:
        st.markdown(render_kpi_card(
            "Brokers Tracked",
            str(summary.get('broker_count', 0)),
            "#A78BFA"
        ), unsafe_allow_html=True)

    with cols[1]:
        top3 = summary.get('top3_share')
        top3_str = f"{top3*100:.1f}%" if top3 else "-"
        st.markdown(render_kpi_card(
            "Top 3 Share",
            top3_str,
            "#22C55E"
        ), unsafe_allow_html=True)

    with cols[2]:
        top_broker = summary.get('top_broker', '-')
        st.markdown(render_kpi_card(
            "Top Broker",
            top_broker or "-",
            "#06B6D4"
        ), unsafe_allow_html=True)

    with cols[3]:
        top_share = summary.get('top_broker_share')
        top_str = f"{top_share*100:.1f}%" if top_share else "-"
        st.markdown(render_kpi_card(
            "Top Broker Share",
            top_str,
            "#F59E0B"
        ), unsafe_allow_html=True)


def render_mwg_cards(summary: dict):
    """Render MWG sector summary cards."""
    cols = st.columns(4)

    with cols[0]:
        rev = summary.get('total_rev_2025')
        rev_str = f"{rev/1000:.0f}T" if rev else "-"
        st.markdown(render_kpi_card(
            "DTT 2025F",
            rev_str,
            "#A78BFA"
        ), unsafe_allow_html=True)

    with cols[1]:
        stores = summary.get('tgdd_stores')
        stores_str = f"{stores:,.0f}" if stores else "-"
        st.markdown(render_kpi_card(
            "TGDD+DMX Stores",
            stores_str,
            "#22C55E"
        ), unsafe_allow_html=True)

    with cols[2]:
        bhx = summary.get('bhx_stores')
        bhx_str = f"{bhx:,.0f}" if bhx else "-"
        st.markdown(render_kpi_card(
            "BHX Stores",
            bhx_str,
            "#06B6D4"
        ), unsafe_allow_html=True)

    with cols[3]:
        bhx_26 = summary.get('bhx_stores_2026')
        bhx_26_str = f"{bhx_26:,.0f}" if bhx_26 else "-"
        st.markdown(render_kpi_card(
            "BHX 2026F",
            bhx_26_str,
            "#F59E0B"
        ), unsafe_allow_html=True)


def render_utility_cards(summary: dict):
    """Render utility sector summary cards."""
    cols = st.columns(4)

    with cols[0]:
        projects = summary.get('total_projects', 0)
        st.markdown(render_kpi_card(
            "Total Projects",
            str(projects),
            "#A78BFA"
        ), unsafe_allow_html=True)

    with cols[1]:
        capacity = summary.get('total_capacity')
        cap_str = f"{capacity:,.0f} MW" if capacity else "-"
        st.markdown(render_kpi_card(
            "Total Capacity",
            cap_str,
            "#22C55E"
        ), unsafe_allow_html=True)

    with cols[2]:
        avg_val = summary.get('avg_val_per_mw')
        avg_str = f"{avg_val:.1f} tỷ/MW" if avg_val else "-"
        st.markdown(render_kpi_card(
            "Avg Val/MW",
            avg_str,
            "#06B6D4"
        ), unsafe_allow_html=True)

    with cols[3]:
        companies = summary.get('companies', 0)
        st.markdown(render_kpi_card(
            "Companies",
            str(companies),
            "#F59E0B"
        ), unsafe_allow_html=True)


# ============================================================================
# TABLE RENDERERS
# ============================================================================

def format_yoy(val) -> str:
    """Format YoY growth with color."""
    if pd.isna(val) or val is None:
        return '-'
    pct = val * 100 if abs(val) < 10 else val
    color = '#10B981' if pct >= 0 else '#EF4444'
    return f'<span style="color:{color};">{pct:+.1f}%</span>'


def render_banking_wide_table(df: pd.DataFrame, summary_rows: pd.DataFrame):
    """Render banking detail as wide horizontal scrollable table like Excel."""
    if df.empty:
        st.warning("No banking data available.")
        return

    # View mode selector
    view_mode = st.radio(
        "View",
        ["Quick View", "Income", "Quality", "Valuation"],
        horizontal=True,
        key="banking_view_mode"
    )

    # Build display DataFrame based on view mode
    display_df = pd.DataFrame()
    display_df['Ticker'] = df['ticker']
    display_df['Type'] = df['bank_type']
    display_df['Rating'] = df['rating']
    display_df['Target'] = df['target_price'].apply(format_price)
    display_df['Price'] = df['closing_price'].apply(format_price)
    display_df['Upside'] = df['upside'].apply(format_upside)

    if view_mode == "Quick View":
        # Core metrics only
        if 'ytd' in df.columns:
            display_df['YTD'] = df['ytd'].apply(format_yoy)
        if 'npatmi_25f' in df.columns:
            display_df['NPATMI'] = df['npatmi_25f'].apply(format_billions)
        if 'npatmi_yoy_25f' in df.columns:
            display_df['%YoY'] = df['npatmi_yoy_25f'].apply(format_yoy)
        if 'roae_25f' in df.columns:
            display_df['ROE'] = df['roae_25f'].apply(format_percent)
        if 'nim_25f' in df.columns:
            display_df['NIM'] = df['nim_25f'].apply(format_percent)
        if 'npl_25f' in df.columns:
            display_df['NPL'] = df['npl_25f'].apply(format_percent)

    elif view_mode == "Income":
        # NII columns
        if 'nii_25f' in df.columns:
            display_df['NII 25F'] = df['nii_25f'].apply(format_billions)
        if 'nii_26f' in df.columns:
            display_df['NII 26F'] = df['nii_26f'].apply(format_billions)
        if 'nii_yoy_25f' in df.columns:
            display_df['NII %'] = df['nii_yoy_25f'].apply(format_yoy)
        # NoII columns
        if 'noii_25f' in df.columns:
            display_df['NoII 25F'] = df['noii_25f'].apply(format_billions)
        if 'noii_26f' in df.columns:
            display_df['NoII 26F'] = df['noii_26f'].apply(format_billions)
        if 'noii_yoy_25f' in df.columns:
            display_df['NoII %'] = df['noii_yoy_25f'].apply(format_yoy)
        # TOI columns
        if 'toi_25f' in df.columns:
            display_df['TOI 25F'] = df['toi_25f'].apply(format_billions)
        if 'toi_26f' in df.columns:
            display_df['TOI 26F'] = df['toi_26f'].apply(format_billions)
        if 'toi_yoy_25f' in df.columns:
            display_df['TOI %'] = df['toi_yoy_25f'].apply(format_yoy)
        # Provision
        if 'provision_25f' in df.columns:
            display_df['Prov 25F'] = df['provision_25f'].apply(format_billions)
        if 'provision_26f' in df.columns:
            display_df['Prov 26F'] = df['provision_26f'].apply(format_billions)
        # NPATMI
        if 'npatmi_25f' in df.columns:
            display_df['NPAT 25F'] = df['npatmi_25f'].apply(format_billions)
        if 'npatmi_26f' in df.columns:
            display_df['NPAT 26F'] = df['npatmi_26f'].apply(format_billions)
        if 'npatmi_yoy_25f' in df.columns:
            display_df['NPAT %'] = df['npatmi_yoy_25f'].apply(format_yoy)

    elif view_mode == "Quality":
        # Efficiency
        if 'nim_25f' in df.columns:
            display_df['NIM 25F'] = df['nim_25f'].apply(format_percent)
        if 'nim_26f' in df.columns:
            display_df['NIM 26F'] = df['nim_26f'].apply(format_percent)
        if 'cir_25f' in df.columns:
            display_df['CIR 25F'] = df['cir_25f'].apply(format_percent)
        if 'cir_26f' in df.columns:
            display_df['CIR 26F'] = df['cir_26f'].apply(format_percent)
        if 'roae_25f' in df.columns:
            display_df['ROE 25F'] = df['roae_25f'].apply(format_percent)
        if 'roae_26f' in df.columns:
            display_df['ROE 26F'] = df['roae_26f'].apply(format_percent)
        # Asset quality
        if 'credit_growth_25f' in df.columns:
            display_df['Cr.Gr 25F'] = df['credit_growth_25f'].apply(format_percent)
        if 'npl_25f' in df.columns:
            display_df['NPL 25F'] = df['npl_25f'].apply(format_percent)
        if 'npl_26f' in df.columns:
            display_df['NPL 26F'] = df['npl_26f'].apply(format_percent)
        if 'credit_cost_25f' in df.columns:
            display_df['Cr.Cost 25F'] = df['credit_cost_25f'].apply(format_percent)

    elif view_mode == "Valuation":
        if 'eps_25f' in df.columns:
            display_df['EPS 25F'] = df['eps_25f'].apply(lambda x: format_number(x, 0))
        if 'eps_26f' in df.columns:
            display_df['EPS 26F'] = df['eps_26f'].apply(lambda x: format_number(x, 0))
        if 'pe_25f' in df.columns:
            display_df['P/E 25F'] = df['pe_25f'].apply(lambda x: format_number(x, 1, 'x'))
        if 'pe_26f' in df.columns:
            display_df['P/E 26F'] = df['pe_26f'].apply(lambda x: format_number(x, 1, 'x'))
        if 'bvps_25f' in df.columns:
            display_df['BVPS 25F'] = df['bvps_25f'].apply(lambda x: format_number(x, 0))
        if 'pb_25f' in df.columns:
            display_df['P/B 25F'] = df['pb_25f'].apply(lambda x: format_number(x, 2, 'x'))
        if 'pb_26f' in df.columns:
            display_df['P/B 26F'] = df['pb_26f'].apply(lambda x: format_number(x, 2, 'x'))

    # Build summary display rows
    if not summary_rows.empty:
        summary_display = pd.DataFrame()
        summary_display['Ticker'] = summary_rows['ticker']
        summary_display['Type'] = ''
        summary_display['Rating'] = ''
        summary_display['Target'] = ''
        summary_display['Price'] = ''
        summary_display['Upside'] = ''

        if view_mode == "Quick View":
            summary_display['YTD'] = ''
            if 'npatmi_25f' in summary_rows.columns:
                summary_display['NPATMI'] = summary_rows['npatmi_25f'].apply(format_billions)
            summary_display['%YoY'] = ''
            if 'roae_25f' in summary_rows.columns:
                summary_display['ROE'] = summary_rows['roae_25f'].apply(format_percent)
            if 'nim_25f' in summary_rows.columns:
                summary_display['NIM'] = summary_rows['nim_25f'].apply(format_percent)
            if 'npl_25f' in summary_rows.columns:
                summary_display['NPL'] = summary_rows['npl_25f'].apply(format_percent)

        elif view_mode == "Income":
            if 'nii_25f' in summary_rows.columns:
                summary_display['NII 25F'] = summary_rows['nii_25f'].apply(format_billions)
            if 'nii_26f' in summary_rows.columns:
                summary_display['NII 26F'] = summary_rows['nii_26f'].apply(format_billions)
            summary_display['NII %'] = ''
            if 'noii_25f' in summary_rows.columns:
                summary_display['NoII 25F'] = summary_rows['noii_25f'].apply(format_billions)
            if 'noii_26f' in summary_rows.columns:
                summary_display['NoII 26F'] = summary_rows['noii_26f'].apply(format_billions)
            summary_display['NoII %'] = ''
            if 'toi_25f' in summary_rows.columns:
                summary_display['TOI 25F'] = summary_rows['toi_25f'].apply(format_billions)
            if 'toi_26f' in summary_rows.columns:
                summary_display['TOI 26F'] = summary_rows['toi_26f'].apply(format_billions)
            summary_display['TOI %'] = ''
            if 'provision_25f' in summary_rows.columns:
                summary_display['Prov 25F'] = summary_rows['provision_25f'].apply(format_billions)
            if 'provision_26f' in summary_rows.columns:
                summary_display['Prov 26F'] = summary_rows['provision_26f'].apply(format_billions)
            if 'npatmi_25f' in summary_rows.columns:
                summary_display['NPAT 25F'] = summary_rows['npatmi_25f'].apply(format_billions)
            if 'npatmi_26f' in summary_rows.columns:
                summary_display['NPAT 26F'] = summary_rows['npatmi_26f'].apply(format_billions)
            summary_display['NPAT %'] = ''

        # Combine data and summary
        combined_df = pd.concat([display_df, summary_display], ignore_index=True)
    else:
        combined_df = display_df

    # Render wide table with custom CSS
    st.markdown(f"**{len(df)} banks** | View: {view_mode}")
    st.markdown(render_wide_table_html(combined_df, len(df)), unsafe_allow_html=True)


def render_wide_table_html(df: pd.DataFrame, data_row_count: int) -> str:
    """Generate HTML for wide scrollable table with sticky first column."""
    # Build header
    headers = ''.join([f'<th>{col}</th>' for col in df.columns])

    # Build rows
    rows_html = []
    for i, row in df.iterrows():
        is_summary = i >= data_row_count
        row_class = 'summary-row' if is_summary else ''
        ticker = str(row.iloc[0])

        # Color code summary rows
        if ticker == 'SOCBs':
            row_class += ' socb-row'
        elif 'Tier-1' in ticker:
            row_class += ' tier1-row'
        elif 'Tier-2' in ticker:
            row_class += ' tier2-row'
        elif 'Tier-3' in ticker:
            row_class += ' tier3-row'

        cells = []
        for j, val in enumerate(row):
            cell_class = 'sticky-col' if j == 0 else ''
            cells.append(f'<td class="{cell_class}">{val}</td>')

        rows_html.append(f'<tr class="{row_class}">{"".join(cells)}</tr>')

    return f'''
    <style>
    .wide-table-container {{
        overflow-x: auto;
        margin: 1rem 0;
        border-radius: 12px;
        border: 1px solid rgba(139, 92, 246, 0.2);
    }}
    .wide-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8rem;
        white-space: nowrap;
    }}
    .wide-table th {{
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(6, 182, 212, 0.1));
        padding: 0.6rem 0.8rem;
        text-align: right;
        font-weight: 600;
        color: #E2E8F0;
        border-bottom: 2px solid rgba(139, 92, 246, 0.3);
        position: sticky;
        top: 0;
    }}
    .wide-table th:first-child,
    .wide-table th:nth-child(2),
    .wide-table th:nth-child(3) {{
        text-align: left;
    }}
    .wide-table td {{
        padding: 0.5rem 0.8rem;
        text-align: right;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        color: #CBD5E1;
    }}
    .wide-table td:first-child,
    .wide-table td:nth-child(2),
    .wide-table td:nth-child(3) {{
        text-align: left;
    }}
    .wide-table .sticky-col {{
        position: sticky;
        left: 0;
        background: rgba(26, 22, 37, 0.98);
        color: #00C9AD;
        font-weight: 600;
        z-index: 1;
    }}
    .wide-table tr:hover td {{
        background: rgba(139, 92, 246, 0.08);
    }}
    .wide-table .summary-row td {{
        background: rgba(139, 92, 246, 0.1);
        font-weight: 600;
        border-top: 2px solid rgba(139, 92, 246, 0.3);
    }}
    .wide-table .socb-row td:first-child {{
        color: #06B6D4;
    }}
    .wide-table .tier1-row td:first-child {{
        color: #A78BFA;
    }}
    .wide-table .tier2-row td:first-child {{
        color: #F59E0B;
    }}
    .wide-table .tier3-row td:first-child {{
        color: #64748B;
    }}
    </style>
    <div class="wide-table-container">
        <table class="wide-table">
            <thead><tr>{headers}</tr></thead>
            <tbody>{"".join(rows_html)}</tbody>
        </table>
    </div>
    '''


def render_banking_table(df: pd.DataFrame, summary_rows: pd.DataFrame = None):
    """Render banking detail table - delegates to wide table renderer."""
    if summary_rows is None:
        summary_rows = pd.DataFrame()
    render_banking_wide_table(df, summary_rows)


def render_brokerage_table(data: dict):
    """Render brokerage detail table (latest quarter market share)."""
    latest_df = data.get('latest', pd.DataFrame())

    if latest_df.empty:
        st.warning("No brokerage data available.")
        return

    display_df = pd.DataFrame()
    display_df['Broker'] = latest_df['broker']
    display_df['Market Share'] = latest_df['market_share'].apply(
        lambda x: f"{x*100:.2f}%" if pd.notna(x) else '-'
    )

    quarter = data.get('summary', {}).get('latest_quarter', 'Latest')
    st.markdown(f"**Market Share - {quarter}** ({len(latest_df)} brokers)")
    st.markdown(
        render_styled_table(display_df, highlight_first_col=True),
        unsafe_allow_html=True
    )


def render_mwg_table(data: dict):
    """Render MWG quarterly table."""
    quarterly_df = data.get('quarterly', pd.DataFrame())
    forecast = data.get('forecast', {})

    if quarterly_df.empty:
        st.warning("No MWG data available.")
        return

    # Display forecast summary
    st.markdown("**Yearly Forecast**")

    summary_data = {
        'Metric': ['TGDD+DMX Revenue', 'TGDD Stores', 'BHX Revenue', 'BHX Stores'],
        '2025F': [
            format_billions(forecast.get('tgdd_rev_2025')),
            format_number(forecast.get('tgdd_stores_2025'), 0),
            format_billions(forecast.get('bhx_rev_2025')),
            format_number(forecast.get('bhx_stores_2025'), 0),
        ],
        '2026F': [
            format_billions(forecast.get('tgdd_rev_2026')),
            format_number(forecast.get('tgdd_stores_2026'), 0),
            format_billions(forecast.get('bhx_rev_2026')),
            format_number(forecast.get('bhx_stores_2026'), 0),
        ],
    }
    summary_df = pd.DataFrame(summary_data)
    st.markdown(
        render_styled_table(summary_df, highlight_first_col=True),
        unsafe_allow_html=True
    )

    # Quarterly breakdown
    st.markdown("**Quarterly Breakdown**")

    display_df = pd.DataFrame()
    display_df['Quarter'] = quarterly_df['quarter']
    display_df['TGDD Rev'] = quarterly_df['tgdd_rev'].apply(format_billions)
    display_df['TGDD Stores'] = quarterly_df['tgdd_stores'].apply(
        lambda x: format_number(x, 0)
    )
    display_df['BHX Rev'] = quarterly_df['bhx_rev'].apply(format_billions)
    display_df['BHX Stores'] = quarterly_df['bhx_stores'].apply(
        lambda x: format_number(x, 0)
    )

    st.markdown(
        render_styled_table(display_df, highlight_first_col=True),
        unsafe_allow_html=True
    )


def render_utility_table(data: dict):
    """Render utility project table."""
    detail_df = data.get('detail', pd.DataFrame())
    by_type_df = data.get('by_type', pd.DataFrame())

    if detail_df.empty:
        st.warning("No utility data available.")
        return

    # Type summary
    if not by_type_df.empty:
        st.markdown("**By Project Type**")
        type_display = pd.DataFrame()
        type_display['Type'] = by_type_df['type']
        type_display['Projects'] = by_type_df['project_count'].astype(int)
        type_display['Capacity (MW)'] = by_type_df['total_capacity'].apply(
            lambda x: format_number(x, 0)
        )
        type_display['Avg Val/MW'] = by_type_df['avg_val_per_mw'].apply(
            lambda x: f"{x:.1f}" if pd.notna(x) else '-'
        )

        st.markdown(
            render_styled_table(type_display, highlight_first_col=True),
            unsafe_allow_html=True
        )

    # Project detail
    st.markdown("**Project Detail**")

    display_df = pd.DataFrame()
    if 'project' in detail_df.columns:
        display_df['Project'] = detail_df['project']
    if 'company' in detail_df.columns:
        display_df['Company'] = detail_df['company']
    if 'type' in detail_df.columns:
        display_df['Type'] = detail_df['type']
    if 'capacity_mw' in detail_df.columns:
        display_df['MW'] = detail_df['capacity_mw'].apply(
            lambda x: format_number(x, 0)
        )
    if 'valuation_per_mw' in detail_df.columns:
        display_df['Val/MW'] = detail_df['valuation_per_mw'].apply(
            lambda x: f"{x:.1f}" if pd.notna(x) else '-'
        )
    if 'efficiency' in detail_df.columns:
        display_df['Efficiency'] = detail_df['efficiency']

    # Limit to first 50 rows for display
    if len(display_df) > 50:
        st.caption(f"Showing first 50 of {len(display_df)} projects")
        display_df = display_df.head(50)

    st.markdown(
        render_styled_table(display_df, highlight_first_col=True),
        unsafe_allow_html=True
    )


# ============================================================================
# MAIN TAB RENDERER
# ============================================================================

def render_assumptions_tab():
    """
    Render the Assumptions tab with sector selector and content.
    """
    st.markdown("### Sector Assumptions")
    st.markdown("**BSC Research assumptions from masterfiles**")

    # Initialize service
    service = AssumptionsService()
    sectors = service.get_available_sectors()

    # Sector selector - Pill style buttons
    st.markdown("""
    <style>
    .sector-selector {
        display: flex;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    selected_sector = st.radio(
        "Select Sector",
        sectors,
        horizontal=True,
        key="assumptions_sector_selector",
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Load and render based on selected sector
    if selected_sector == "Banking":
        with st.spinner("Loading banking data..."):
            data = service.load_banking_assumptions()

        if 'error' in data and data['error']:
            st.error(f"Error loading data: {data['error']}")
        else:
            render_banking_cards(data.get('summary', {}))
            st.markdown("---")
            render_banking_table(
                data.get('detail', pd.DataFrame()),
                data.get('summary_rows', pd.DataFrame())
            )

    elif selected_sector == "Brokerage":
        with st.spinner("Loading brokerage data..."):
            data = service.load_brokerage_assumptions()

        if 'error' in data and data['error']:
            st.error(f"Error loading data: {data['error']}")
        else:
            render_brokerage_cards(data.get('summary', {}))
            st.markdown("---")
            render_brokerage_table(data)

    elif selected_sector == "MWG":
        with st.spinner("Loading MWG data..."):
            data = service.load_mwg_assumptions()

        if 'error' in data and data['error']:
            st.error(f"Error loading data: {data['error']}")
        else:
            render_mwg_cards(data.get('summary', {}))
            st.markdown("---")
            render_mwg_table(data)

    elif selected_sector == "Utility":
        with st.spinner("Loading utility data..."):
            data = service.load_utility_assumptions()

        if 'error' in data and data['error']:
            st.error(f"Error loading data: {data['error']}")
        else:
            render_utility_cards(data.get('summary', {}))
            st.markdown("---")
            render_utility_table(data)
