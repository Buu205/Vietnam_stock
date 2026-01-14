"""
Assumptions Service - BSC Sector Assumptions Data Loading
==========================================================
Service for loading sector assumptions from BSC masterfiles.

Supports 4 sectors:
- Banking: Financial metrics (NIM, NPL, CIR, ROE, etc.)
- Brokerage: Market share time series
- MWG: Business segments (TGDĐ, BHX) with store counts
- Utility: Project-level valuation (Hydro, Wind, Solar)

Usage:
    from WEBAPP.services.assumptions_service import AssumptionsService

    service = AssumptionsService()
    banking = service.load_banking_assumptions()
    brokerage = service.load_brokerage_assumptions()

Author: AI Assistant
Date: 2026-01-12
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, List, Optional, Any


class AssumptionsService:
    """Service for loading BSC sector assumptions from Excel masterfiles."""

    # Import bank classification from centralized config
    from config.sector_analysis.bank_config import BANK_CLASSIFICATION
    SOCBS = BANK_CLASSIFICATION['SOCB']
    TIER1_PCBS = BANK_CLASSIFICATION['Tier-1']
    TIER2_PCBS = BANK_CLASSIFICATION['Tier-2']
    TIER3_PCBS = BANK_CLASSIFICATION['Tier-3']

    # Column index mapping for Banking Masterfile (0-indexed)
    # NOTE: Historical data (2023A, 2024A) comes from parquet, NOT Excel
    # Only FORECAST columns (25F, 26F) are loaded from Excel
    BANKING_COLS = {
        # Stock info
        'ticker': 1, 'rating': 2, 'target_price': 3,
        'closing_price': 4, 'upside': 5, 'prev_price': 6, 'ytd': 7,
        # Income metrics - FORECAST ONLY (25F, 26F) + %YoY from Excel
        'nii_25f': 12, 'nii_26f': 13,
        'nii_yoy_25f': 16, 'nii_yoy_26f': 17,
        'noii_25f': 22, 'noii_26f': 23,
        'noii_yoy_25f': 26, 'noii_yoy_26f': 27,
        'toi_25f': 32, 'toi_26f': 33,
        'toi_yoy_25f': 36, 'toi_yoy_26f': 37,
        'provision_25f': 42, 'provision_26f': 43,
        'provision_yoy_25f': 46, 'provision_yoy_26f': 47,
        'pbt_25f': 52, 'pbt_26f': 53,
        'pbt_yoy_25f': 56, 'pbt_yoy_26f': 57,
        'npatmi_25f': 62, 'npatmi_26f': 63,
        'npatmi_yoy_25f': 66, 'npatmi_yoy_26f': 67,
        # Quality metrics
        'credit_growth_25f': 72, 'credit_growth_26f': 73,
        'npl_25f': 78, 'npl_26f': 79,
        'npl_formation_25f': 84, 'npl_formation_26f': 85,
        'credit_cost_25f': 90, 'credit_cost_26f': 91,
        # Efficiency metrics
        'nim_25f': 96, 'nim_26f': 97,
        'cir_25f': 102, 'cir_26f': 103,
        'roaa_25f': 108, 'roaa_26f': 109,
        'roae_25f': 114, 'roae_26f': 115,
        # Valuation metrics
        'eps_25f': 120, 'eps_26f': 121,
        'pe_25f': 124, 'pe_26f': 125,
        'bvps_25f': 130, 'bvps_26f': 131,
        'pb_25f': 134, 'pb_26f': 135,
        # Size metrics
        'total_assets_25f': 138, 'total_assets_26f': 139,
        'equity_25f': 142, 'equity_26f': 143,
    }

    # Historical parquet path for bank metrics
    BANK_PARQUET_PATH = Path("DATA/processed/fundamental/bank/bank_financial_metrics.parquet")
    # OHLCV path for latest prices
    OHLCV_PATH = Path("DATA/raw/ohlcv/OHLCV_mktcap.parquet")

    def __init__(self, masterfile_root: Optional[Path] = None):
        """
        Initialize AssumptionsService.

        Args:
            masterfile_root: Root directory for BSC masterfiles (default: BSC_masterfile/)
        """
        self.masterfile_root = masterfile_root or Path("BSC_masterfile")

    # =========================================================================
    # Price Data Helper
    # =========================================================================

    def _load_latest_prices(self, tickers: list) -> pd.DataFrame:
        """
        Load latest closing prices from OHLCV parquet.

        Args:
            tickers: List of ticker symbols

        Returns:
            DataFrame with columns: ticker, latest_price, price_date
        """
        if not self.OHLCV_PATH.exists():
            return pd.DataFrame()

        try:
            df = pd.read_parquet(self.OHLCV_PATH)
            # OHLCV uses 'symbol' column, not 'ticker'
            df = df[df['symbol'].isin(tickers)].copy()

            if df.empty:
                return pd.DataFrame()

            # Get latest date for each ticker
            latest_idx = df.groupby('symbol')['date'].idxmax()
            latest_df = df.loc[latest_idx, ['symbol', 'date', 'close']].copy()
            latest_df.columns = ['ticker', 'price_date', 'latest_price']

            return latest_df.reset_index(drop=True)

        except Exception as e:
            print(f"Error loading latest prices: {e}")
            return pd.DataFrame()

    # =========================================================================
    # Banking Sector
    # =========================================================================

    def _load_bank_historical(self) -> pd.DataFrame:
        """
        Load historical bank metrics (2023A, 2024A) from parquet.

        Returns:
            DataFrame with columns: ticker, npatmi_23a, npatmi_24a, nii_23a, nii_24a, etc.
            - Income metrics: Sum of 4 quarters, in billion VND (tỉ VND)
            - Ratio metrics: Q4 value as proxy for full year
        """
        if not self.BANK_PARQUET_PATH.exists():
            return pd.DataFrame()

        try:
            df = pd.read_parquet(self.BANK_PARQUET_PATH)

            # Filter for 2023 and 2024 full year data
            df_2023 = df[df['year'] == 2023].copy()
            df_2024 = df[df['year'] == 2024].copy()

            # Income metrics: Sum of 4 quarters
            income_cols = ['npatmi', 'nii', 'noii', 'toi', 'provision_expense', 'pbt']
            # Ratio metrics: Use Q4 as proxy for full year
            ratio_cols = ['nim_q', 'cir', 'npl_ratio', 'roea_ttm', 'roaa_ttm']

            def agg_year(year_df: pd.DataFrame) -> pd.DataFrame:
                """Aggregate annual data from quarterly."""
                agg_dict = {}
                # Sum for income metrics
                for col in income_cols:
                    if col in year_df.columns:
                        agg_dict[col] = 'sum'
                result = year_df.groupby('symbol').agg(agg_dict).reset_index()
                # Convert from VND to billion VND (tỉ VND) to match Excel format
                for col in income_cols:
                    if col in result.columns:
                        result[col] = result[col] / 1e9

                # Get Q4 data for ratio metrics
                q4_df = year_df[year_df['quarter'] == 4].copy()
                if not q4_df.empty:
                    q4_ratios = q4_df[['symbol'] + [c for c in ratio_cols if c in q4_df.columns]]
                    result = result.merge(q4_ratios, on='symbol', how='left')

                return result

            hist_2023 = agg_year(df_2023)
            hist_2024 = agg_year(df_2024)

            # Rename columns with year suffix
            hist_2023.columns = ['ticker'] + [f'{c}_23a' for c in hist_2023.columns[1:]]
            hist_2024.columns = ['ticker'] + [f'{c}_24a' for c in hist_2024.columns[1:]]

            # Rename provision_expense to provision, nim_q to nim, etc.
            rename_map_23 = {
                'provision_expense_23a': 'provision_23a',
                'nim_q_23a': 'nim_23a',
                'npl_ratio_23a': 'npl_23a',
                'roea_ttm_23a': 'roe_23a',
                'roaa_ttm_23a': 'roa_23a',
            }
            rename_map_24 = {
                'provision_expense_24a': 'provision_24a',
                'nim_q_24a': 'nim_24a',
                'npl_ratio_24a': 'npl_24a',
                'roea_ttm_24a': 'roe_24a',
                'roaa_ttm_24a': 'roa_24a',
            }
            hist_2023.rename(columns=rename_map_23, inplace=True)
            hist_2024.rename(columns=rename_map_24, inplace=True)

            # Merge 2023 and 2024
            historical = hist_2023.merge(hist_2024, on='ticker', how='outer')

            return historical

        except Exception as e:
            print(f"Error loading bank historical: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=3600, show_spinner=False)
    def load_banking_assumptions(_self) -> Dict[str, Any]:
        """
        Load banking assumptions from Excel masterfile.

        Returns:
            Dict with 'summary', 'detail', 'summary_rows' DataFrames
        """
        file_path = _self.masterfile_root / "Banking Masterfile.xlsx"

        if not file_path.exists():
            return {'summary': {}, 'detail': pd.DataFrame(), 'error': 'File not found'}

        try:
            # Read raw data without header
            df = pd.read_excel(file_path, sheet_name='read_python', header=None)

            # Data starts at row 4 (0-indexed), filter valid tickers
            # Exclude summary rows from Excel (Sum/Average, SOCBs, PCBs)
            data_df = df.iloc[4:].copy()
            data_df = data_df[data_df.iloc[:, 1].notna() & (data_df.iloc[:, 1] != 'x')]
            # Filter out Excel summary rows
            summary_labels = ['Sum/Average', 'SOCBs', 'PCBs', 'Sum', 'Average', 'Total']
            data_df = data_df[~data_df.iloc[:, 1].isin(summary_labels)]

            # Extract all columns using mapping
            clean_df = pd.DataFrame()
            cols = _self.BANKING_COLS

            for col_name, col_idx in cols.items():
                if col_idx < data_df.shape[1]:
                    clean_df[col_name] = pd.to_numeric(
                        data_df.iloc[:, col_idx], errors='coerce'
                    ) if col_name not in ['ticker', 'rating'] else data_df.iloc[:, col_idx]

            # Clean ticker and rating
            clean_df['ticker'] = clean_df['ticker'].astype(str).str.strip()
            clean_df['rating'] = clean_df['rating'].fillna('N/A')

            # Merge historical data from parquet (2023A, 2024A)
            historical_df = _self._load_bank_historical()
            if not historical_df.empty:
                clean_df = clean_df.merge(historical_df, on='ticker', how='left')

            # Update prices from OHLCV and recalculate upside
            tickers = clean_df['ticker'].tolist()
            latest_prices = _self._load_latest_prices(tickers)
            if not latest_prices.empty:
                # Merge latest prices
                clean_df = clean_df.merge(latest_prices, on='ticker', how='left')
                # Update closing_price with latest_price where available
                mask = clean_df['latest_price'].notna()
                clean_df.loc[mask, 'closing_price'] = clean_df.loc[mask, 'latest_price']
                # Recalculate upside = (target - current) / current
                clean_df['upside'] = (clean_df['target_price'] - clean_df['closing_price']) / clean_df['closing_price']
                # Drop helper columns
                clean_df.drop(columns=['latest_price', 'price_date'], inplace=True, errors='ignore')

            # Add bank classification (SOCB, Tier-1, Tier-2, Tier-3)
            def classify_bank(ticker):
                if ticker in _self.SOCBS:
                    return 'SOCB'
                elif ticker in _self.TIER1_PCBS:
                    return 'Tier-1'
                elif ticker in _self.TIER2_PCBS:
                    return 'Tier-2'
                elif ticker in _self.TIER3_PCBS:
                    return 'Tier-3'
                else:
                    return 'Other'

            clean_df['bank_type'] = clean_df['ticker'].apply(classify_bank)

            # Calculate summary rows
            def calc_summary_row(subset_df: pd.DataFrame, label: str) -> dict:
                """Calculate aggregated row for a subset of banks."""
                row = {'ticker': label, 'rating': '', 'bank_type': 'summary'}
                # Sum for income metrics (historical + forecast)
                sum_cols = [
                    # Historical from parquet
                    'nii_23a', 'nii_24a', 'noii_23a', 'noii_24a', 'toi_23a', 'toi_24a',
                    'provision_23a', 'provision_24a', 'pbt_23a', 'pbt_24a',
                    'npatmi_23a', 'npatmi_24a',
                    # Forecast from Excel
                    'nii_25f', 'nii_26f', 'noii_25f', 'noii_26f', 'toi_25f', 'toi_26f',
                    'provision_25f', 'provision_26f', 'pbt_25f', 'pbt_26f',
                    'npatmi_25f', 'npatmi_26f', 'total_assets_25f', 'equity_25f'
                ]
                for col in sum_cols:
                    if col in subset_df.columns:
                        row[col] = subset_df[col].sum()
                # Average for ratio metrics
                avg_cols = ['roae_25f', 'roae_26f', 'nim_25f', 'nim_26f', 'npl_25f', 'npl_26f',
                           'cir_25f', 'cir_26f', 'credit_growth_25f', 'credit_growth_26f',
                           'pe_25f', 'pb_25f']
                for col in avg_cols:
                    if col in subset_df.columns:
                        row[col] = subset_df[col].mean()
                return row

            summary_rows = []
            # All banks
            summary_rows.append(calc_summary_row(clean_df, 'Sum/Average'))
            # SOCBs
            socb_df = clean_df[clean_df['ticker'].isin(_self.SOCBS)]
            if not socb_df.empty:
                summary_rows.append(calc_summary_row(socb_df, 'SOCBs'))
            # Tier-1 PCBs
            tier1_df = clean_df[clean_df['ticker'].isin(_self.TIER1_PCBS)]
            if not tier1_df.empty:
                summary_rows.append(calc_summary_row(tier1_df, 'Tier-1 PCBs'))
            # Tier-2 PCBs
            tier2_df = clean_df[clean_df['ticker'].isin(_self.TIER2_PCBS)]
            if not tier2_df.empty:
                summary_rows.append(calc_summary_row(tier2_df, 'Tier-2 PCBs'))
            # Tier-3 PCBs (small banks)
            tier3_df = clean_df[clean_df['ticker'].isin(_self.TIER3_PCBS)]
            if not tier3_df.empty:
                summary_rows.append(calc_summary_row(tier3_df, 'Tier-3 PCBs'))

            summary_df = pd.DataFrame(summary_rows)

            # Calculate summary stats for cards
            summary = {
                'stock_count': len(clean_df),
                'avg_roe': clean_df['roae_25f'].mean() if 'roae_25f' in clean_df.columns else None,
                'avg_nim': clean_df['nim_25f'].mean() if 'nim_25f' in clean_df.columns else None,
                'avg_npl': clean_df['npl_25f'].mean() if 'npl_25f' in clean_df.columns else None,
                'avg_upside': clean_df['upside'].mean(),
            }

            return {
                'summary': summary,
                'detail': clean_df.reset_index(drop=True),
                'summary_rows': summary_df,
            }

        except Exception as e:
            return {'summary': {}, 'detail': pd.DataFrame(), 'error': str(e)}

    # =========================================================================
    # Brokerage Sector
    # =========================================================================

    @st.cache_data(ttl=3600, show_spinner=False)
    def load_brokerage_assumptions(_self) -> Dict[str, Any]:
        """
        Load brokerage market share data from Excel masterfile.

        Returns:
            Dict with 'summary', 'detail' (time series), and 'latest' data
        """
        file_path = _self.masterfile_root / "Brokerage Masterfile.xlsx"

        if not file_path.exists():
            return {'summary': {}, 'detail': pd.DataFrame(), 'error': 'File not found'}

        try:
            # Read market share sheet
            df = pd.read_excel(file_path, sheet_name='read_python', header=None)

            # Structure: Row 3 has quarters (1Q16, 2Q16, ..., 3Q25)
            # Column 2: Broker ticker, Column 3+: quarterly values
            header_row = 3
            quarters = df.iloc[header_row, 3:].dropna().tolist()

            # Get broker data (rows 4+)
            brokers_data = []
            for i in range(header_row + 1, len(df)):
                row = df.iloc[i]
                if pd.isna(row[2]):
                    continue
                broker = str(row[2]).strip()
                if not broker:
                    continue

                values = row[3:3+len(quarters)].tolist()
                for j, val in enumerate(values):
                    if j < len(quarters) and pd.notna(val):
                        brokers_data.append({
                            'broker': broker,
                            'quarter': quarters[j],
                            'market_share': float(val) if pd.notna(val) else None
                        })

            detail_df = pd.DataFrame(brokers_data)

            if detail_df.empty:
                return {'summary': {}, 'detail': pd.DataFrame(), 'error': 'No data parsed'}

            # Get latest quarter (last in list)
            latest_quarter = quarters[-1] if quarters else None
            latest_df = detail_df[detail_df['quarter'] == latest_quarter].copy() if latest_quarter else pd.DataFrame()
            latest_df = latest_df.sort_values('market_share', ascending=False)

            # Calculate summary
            top3_share = latest_df['market_share'].head(3).sum() if not latest_df.empty else 0

            summary = {
                'broker_count': detail_df['broker'].nunique(),
                'latest_quarter': latest_quarter,
                'top3_share': top3_share,
                'top_broker': latest_df['broker'].iloc[0] if not latest_df.empty else None,
                'top_broker_share': latest_df['market_share'].iloc[0] if not latest_df.empty else None,
            }

            return {
                'summary': summary,
                'detail': detail_df,
                'latest': latest_df,
            }

        except Exception as e:
            return {'summary': {}, 'detail': pd.DataFrame(), 'error': str(e)}

    # =========================================================================
    # MWG Sector
    # =========================================================================

    @st.cache_data(ttl=3600, show_spinner=False)
    def load_mwg_assumptions(_self) -> Dict[str, Any]:
        """
        Load MWG business segment data from Excel masterfile.

        Returns:
            Dict with 'summary', 'forecast', 'bhx_tracking' data
        """
        file_path = _self.masterfile_root / "MWG 29.12.2025.xlsx"

        if not file_path.exists():
            return {'summary': {}, 'forecast': pd.DataFrame(), 'error': 'File not found'}

        try:
            # Read main forecast sheet
            df = pd.read_excel(file_path, sheet_name='Read_python', header=None)

            # Structure based on exploration:
            # Row 1: Headers (Quan điểm BSC, 2025e, 2026F, ...)
            # Row 3: TGDĐ + ĐMX revenue
            # Row 4: SLCH (store count)
            # Row 5: DT/CH/Tháng (revenue per store/month)
            # Row 6: BHX revenue
            # Row 7: SLCH (BHX stores)
            # Row 8: DT/CH/Tháng (BHX)

            # Extract key metrics
            forecast_data = {
                'tgdd_rev_2025': df.iloc[3, 1] if df.shape[0] > 3 else None,
                'tgdd_rev_2026': df.iloc[3, 2] if df.shape[0] > 3 else None,
                'tgdd_stores_2025': df.iloc[4, 1] if df.shape[0] > 4 else None,
                'tgdd_stores_2026': df.iloc[4, 2] if df.shape[0] > 4 else None,
                'tgdd_rev_per_store_2025': df.iloc[5, 1] if df.shape[0] > 5 else None,
                'bhx_rev_2025': df.iloc[6, 1] if df.shape[0] > 6 else None,
                'bhx_rev_2026': df.iloc[6, 2] if df.shape[0] > 6 else None,
                'bhx_stores_2025': df.iloc[7, 1] if df.shape[0] > 7 else None,
                'bhx_stores_2026': df.iloc[7, 2] if df.shape[0] > 7 else None,
                'bhx_rev_per_store_2025': df.iloc[8, 1] if df.shape[0] > 8 else None,
            }

            # Convert to numeric
            for key in forecast_data:
                if forecast_data[key] is not None:
                    try:
                        forecast_data[key] = float(forecast_data[key])
                    except (ValueError, TypeError):
                        forecast_data[key] = None

            # Create quarterly detail DataFrame
            quarters = ['Q1/2024', 'Q2/2024', 'Q3/2024', 'Q4/2024',
                       'Q1/2025', 'Q2/2025', 'Q3/2025', 'Q4/2025',
                       'Q1/2026', 'Q2/2026', 'Q3/2026', 'Q4/2026']

            quarterly_data = []
            for i, q in enumerate(quarters):
                col_idx = i + 5  # Quarterly data starts from column 5
                if col_idx < df.shape[1]:
                    quarterly_data.append({
                        'quarter': q,
                        'tgdd_rev': df.iloc[3, col_idx] if df.shape[0] > 3 else None,
                        'tgdd_stores': df.iloc[4, col_idx] if df.shape[0] > 4 else None,
                        'bhx_rev': df.iloc[6, col_idx] if df.shape[0] > 6 else None,
                        'bhx_stores': df.iloc[7, col_idx] if df.shape[0] > 7 else None,
                    })

            quarterly_df = pd.DataFrame(quarterly_data)

            # Calculate summary
            summary = {
                'total_rev_2025': (forecast_data.get('tgdd_rev_2025') or 0) + (forecast_data.get('bhx_rev_2025') or 0),
                'total_rev_2026': (forecast_data.get('tgdd_rev_2026') or 0) + (forecast_data.get('bhx_rev_2026') or 0),
                'tgdd_stores': forecast_data.get('tgdd_stores_2025'),
                'bhx_stores': forecast_data.get('bhx_stores_2025'),
                'bhx_stores_2026': forecast_data.get('bhx_stores_2026'),
            }

            # Calculate YoY growth
            if summary['total_rev_2025'] and summary['total_rev_2026']:
                summary['rev_growth_yoy'] = (summary['total_rev_2026'] - summary['total_rev_2025']) / summary['total_rev_2025']

            return {
                'summary': summary,
                'forecast': forecast_data,
                'quarterly': quarterly_df,
            }

        except Exception as e:
            return {'summary': {}, 'forecast': {}, 'error': str(e)}

    # =========================================================================
    # Utility Sector
    # =========================================================================

    @st.cache_data(ttl=3600, show_spinner=False)
    def load_utility_assumptions(_self) -> Dict[str, Any]:
        """
        Load utility sector project-level valuation data.

        Returns:
            Dict with 'summary', 'detail', 'by_type' data
        """
        file_path = _self.masterfile_root / "Masterfile_Utitlities.xlsx"

        if not file_path.exists():
            return {'summary': {}, 'detail': pd.DataFrame(), 'error': 'File not found'}

        try:
            # Read valuation summary sheet
            df = pd.read_excel(file_path, sheet_name='Tổng hợp định giá', header=2)

            # Clean column names based on structure
            # Columns: [NaN, Dự án, Công ty liên quan, Loại hình, Công suất (MW), ...]
            df = df.iloc[:, 1:]  # Skip first empty column

            # Rename columns
            expected_cols = [
                'project', 'company', 'type', 'capacity_mw',
                'total_investment', 'investment_per_mw',
                'valuation', 'valuation_per_mw', 'efficiency', 'notes'
            ]
            if len(df.columns) >= len(expected_cols):
                df.columns = expected_cols + list(df.columns[len(expected_cols):])

            # Filter valid rows (non-null project)
            df = df[df['project'].notna()].copy()

            # Skip header/summary rows
            df = df[~df['project'].str.contains('Dự án|Tổng|Total|Sum', case=False, na=False)]

            # Convert numeric columns
            for col in ['capacity_mw', 'total_investment', 'investment_per_mw',
                       'valuation', 'valuation_per_mw']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Standardize type names
            type_mapping = {
                'Thủy điện': 'Hydro',
                'Điện gió': 'Wind',
                'Điện mặt trời': 'Solar',
            }
            if 'type' in df.columns:
                df['type_en'] = df['type'].map(type_mapping).fillna(df['type'])

            # Group by type
            by_type = df.groupby('type').agg({
                'capacity_mw': 'sum',
                'valuation': 'sum',
                'valuation_per_mw': 'mean',
                'project': 'count'
            }).reset_index()
            by_type.columns = ['type', 'total_capacity', 'total_valuation', 'avg_val_per_mw', 'project_count']

            # Calculate summary
            summary = {
                'total_projects': len(df),
                'total_capacity': df['capacity_mw'].sum() if 'capacity_mw' in df.columns else 0,
                'avg_val_per_mw': df['valuation_per_mw'].mean() if 'valuation_per_mw' in df.columns else 0,
                'companies': df['company'].nunique() if 'company' in df.columns else 0,
            }

            return {
                'summary': summary,
                'detail': df,
                'by_type': by_type,
            }

        except Exception as e:
            return {'summary': {}, 'detail': pd.DataFrame(), 'error': str(e)}

    # =========================================================================
    # Unified Loader
    # =========================================================================

    def load_sector(self, sector: str) -> Dict[str, Any]:
        """
        Load assumptions for a specific sector.

        Args:
            sector: One of 'banking', 'brokerage', 'mwg', 'utility'

        Returns:
            Dict with sector-specific data
        """
        loaders = {
            'banking': self.load_banking_assumptions,
            'brokerage': self.load_brokerage_assumptions,
            'mwg': self.load_mwg_assumptions,
            'utility': self.load_utility_assumptions,
        }

        loader = loaders.get(sector.lower())
        if loader:
            return loader()
        return {'error': f'Unknown sector: {sector}'}

    def get_available_sectors(self) -> List[str]:
        """Get list of available sectors."""
        return ['Banking', 'Brokerage', 'MWG', 'Utility']
