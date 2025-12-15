"""
FA Aggregator - Fundamental Analysis Sector Aggregation
========================================================

Tổng hợp dữ liệu fundamental metrics theo ngành.
Aggregate fundamental metrics by sector.

This module loads raw financial data in metric_code format from *_full.parquet files,
pivots them to business metrics, and aggregates by sector.

Key Features:
- Load raw data from *_full.parquet files (long format: SECURITY_CODE, REPORT_DATE, METRIC_CODE, METRIC_VALUE)
- Pivot metric codes to business metric columns using metric_mappings.py
- Filter by entity type (COMPANY, BANK, SECURITY, INSURANCE)
- Map tickers to sectors using SectorRegistry
- Aggregate absolute metrics (sum by sector)
- Calculate sector-level ratios from aggregated sums (not averages!)
- Calculate YoY and QoQ growth rates
- Handle entity-specific metrics (bank NIM, NPL, LDR; security margin loans, etc.)

Data Flow:
1. Load *_full.parquet → Filter by ENTITY_TYPE → Filter mapped METRIC_CODEs
2. Pivot: METRIC_CODE columns → Business metric columns (via mappings)
3. Map tickers to sectors → Aggregate by sector + report_date
4. Calculate ratios (from sums, not averages!)
5. Calculate growth rates (YoY, QoQ)

Output: DATA/processed/sector/sector_fundamental_metrics.parquet

Author: Claude Code
Date: 2025-12-15
Version: 2.0.0 - Rewritten to use *_full.parquet with metric_code pivot
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime

from PROCESSORS.sector.calculators.base_aggregator import BaseAggregator

logger = logging.getLogger(__name__)


class FAAggregator(BaseAggregator):
    """
    Fundamental Analysis Aggregator.

    Tổng hợp dữ liệu tài chính từ 4 loại hình doanh nghiệp và tính toán
    các chỉ số tài chính cấp ngành.

    Aggregates financial data from 4 entity types and calculates
    sector-level financial metrics.
    """

    def __init__(self, config_manager, sector_registry, metric_registry):
        """
        Initialize FA Aggregator.

        Args:
            config_manager: ConfigManager instance (for FA weights/preferences)
            sector_registry: SectorRegistry instance (for ticker-sector mapping)
            metric_registry: MetricRegistry instance (for metric definitions)
        """
        super().__init__(config_manager, sector_registry, metric_registry)

        # Set input paths - USE *_full.parquet files for sector aggregation
        self.fundamental_path = self.processed_path / "fundamental"

        # All entity types are in these files (filtered by ENTITY_TYPE column)
        self.company_path = self.fundamental_path / "company_full.parquet"
        self.bank_path = self.fundamental_path / "bank_full.parquet"
        self.security_path = self.fundamental_path / "security_full.parquet"
        self.insurance_path = self.fundamental_path / "insurance_full.parquet"

        # Import metric mappings
        from PROCESSORS.sector.calculators.metric_mappings import (
            COMPANY_MAPPINGS,
            BANK_MAPPINGS,
            SECURITY_MAPPINGS,
            INSURANCE_MAPPINGS
        )

        self.company_mappings = COMPANY_MAPPINGS
        self.bank_mappings = BANK_MAPPINGS
        self.security_mappings = SECURITY_MAPPINGS
        self.insurance_mappings = INSURANCE_MAPPINGS

        logger.info("FAAggregator initialized")
        logger.info(f"  Company data: {self.company_path}")
        logger.info(f"  Bank data: {self.bank_path}")
        logger.info(f"  Security data: {self.security_path}")
        logger.info(f"  Insurance data: {self.insurance_path}")
        logger.info(f"  Company mappings: {len(self.company_mappings)} metrics")
        logger.info(f"  Bank mappings: {len(self.bank_mappings)} metrics")
        logger.info(f"  Security mappings: {len(self.security_mappings)} metrics")
        logger.info(f"  Insurance mappings: {len(self.insurance_mappings)} metrics")

    def aggregate_sector_fundamentals(
        self,
        report_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Main aggregation function - Hàm tổng hợp chính.

        Aggregate fundamental metrics by sector from all entity types.

        Args:
            report_date: Specific report date (YYYY-MM-DD) - if provided, only this date
            start_date: Start date for range (YYYY-MM-DD)
            end_date: End date for range (YYYY-MM-DD)

        Returns:
            DataFrame with sector fundamental metrics

        Schema:
            - sector_code: str
            - sector_name_vi: str
            - report_date: date
            - entity_types: list[str]
            - ticker_count: int
            - total_revenue: float (VND)
            - net_profit: float (VND)
            - total_assets: float (VND)
            - total_equity: float (VND)
            - total_liabilities: float (VND)
            - gross_margin: float (decimal)
            - operating_margin: float (decimal)
            - net_margin: float (decimal)
            - roe: float (decimal)
            - roa: float (decimal)
            - debt_to_equity: float (decimal)
            - revenue_growth_yoy: float (decimal)
            - profit_growth_yoy: float (decimal)
            - revenue_growth_qoq: float (decimal)
            - profit_growth_qoq: float (decimal)
            - [Bank-specific metrics if applicable]
            - [Security-specific metrics if applicable]
            - calculation_date: timestamp
            - data_quality_score: float
        """
        logger.info("=" * 80)
        logger.info("STARTING FA SECTOR AGGREGATION")
        logger.info("=" * 80)

        # Step 1: Load all entity data
        logger.info("\n[1/5] Loading fundamental data...")
        company_df = self._load_company_data()
        bank_df = self._load_bank_data()
        security_df = self._load_security_data()
        insurance_df = self._load_insurance_data()

        # Step 2: Filter by date if specified
        if report_date:
            logger.info(f"\n[2/5] Filtering for report_date: {report_date}")
            company_df = self._filter_by_date(company_df, start_date=report_date, end_date=report_date)
            bank_df = self._filter_by_date(bank_df, start_date=report_date, end_date=report_date)
            security_df = self._filter_by_date(security_df, start_date=report_date, end_date=report_date)
            insurance_df = self._filter_by_date(insurance_df, start_date=report_date, end_date=report_date)
        elif start_date or end_date:
            logger.info(f"\n[2/5] Filtering date range: {start_date} to {end_date}")
            company_df = self._filter_by_date(company_df, start_date=start_date, end_date=end_date)
            bank_df = self._filter_by_date(bank_df, start_date=start_date, end_date=end_date)
            security_df = self._filter_by_date(security_df, start_date=start_date, end_date=end_date)
            insurance_df = self._filter_by_date(insurance_df, start_date=start_date, end_date=end_date)
        else:
            logger.info("\n[2/5] No date filter applied - using all available data")

        # Step 3: Add sector mapping
        logger.info("\n[3/5] Mapping tickers to sectors...")
        company_df = self._add_sector_mapping(company_df) if company_df is not None else None
        bank_df = self._add_sector_mapping(bank_df) if bank_df is not None else None
        security_df = self._add_sector_mapping(security_df) if security_df is not None else None
        insurance_df = self._add_sector_mapping(insurance_df) if insurance_df is not None else None

        # Step 4: Aggregate by sector
        logger.info("\n[4/5] Aggregating by sector...")
        results = self._aggregate_all_sectors(company_df, bank_df, security_df, insurance_df)

        if not results:
            logger.warning("No aggregation results generated!")
            return pd.DataFrame()

        # Step 5: Calculate ratios and growth
        logger.info("\n[5/5] Calculating ratios and growth rates...")
        sector_df = pd.DataFrame(results)
        sector_df = self._calculate_ratios(sector_df)
        sector_df = self._calculate_growth(sector_df)

        # Add metadata
        sector_df['calculation_date'] = pd.Timestamp.now()

        logger.info("=" * 80)
        logger.info(f"✅ FA AGGREGATION COMPLETE: {len(sector_df)} records generated")
        logger.info(f"   Sectors: {sector_df['sector_code'].nunique()}")
        logger.info(f"   Date range: {sector_df['report_date'].min()} to {sector_df['report_date'].max()}")
        logger.info("=" * 80)

        return sector_df

    def _log_unmapped_codes(
        self,
        df_raw: pd.DataFrame,
        mapped_codes: List[str],
        entity_type: str
    ) -> None:
        """
        Log unmapped metric codes for debugging.

        Args:
            df_raw: Raw DataFrame with METRIC_CODE column
            mapped_codes: List of mapped metric codes
            entity_type: Entity type name (for logging)
        """
        if df_raw is None or df_raw.empty:
            return

        all_codes = set(df_raw['METRIC_CODE'].unique())
        unmapped = all_codes - set(mapped_codes)

        if unmapped:
            unmapped_sorted = sorted(list(unmapped))
            logger.info(
                f"  📋 {entity_type}: {len(unmapped)} unmapped metric codes "
                f"(showing first 15): {unmapped_sorted[:15]}"
            )

    def _load_company_data(self) -> Optional[pd.DataFrame]:
        """
        Load and pivot company fundamental data.

        Process:
        1. Load raw data (SECURITY_CODE, REPORT_DATE, METRIC_CODE, METRIC_VALUE)
        2. Filter by ENTITY_TYPE = 'COMPANY'
        3. Filter metric codes to only those in COMPANY_MAPPINGS
        4. Pivot METRIC_CODE to columns
        5. Rename columns using mappings

        Returns:
            DataFrame with columns: symbol, report_date, net_revenue, gross_profit, ...
        """
        df_raw = self._load_parquet(self.company_path)
        if df_raw is None:
            return None

        # Filter by entity type
        df_filtered = df_raw[df_raw['ENTITY_TYPE'] == 'COMPANY'].copy()

        # Log unmapped codes before filtering
        mapped_codes = list(self.company_mappings.keys())
        self._log_unmapped_codes(df_filtered, mapped_codes, 'COMPANY')

        # Filter to only mapped metric codes
        df_filtered = df_filtered[df_filtered['METRIC_CODE'].isin(mapped_codes)]

        if len(df_filtered) == 0:
            logger.warning("  ⚠️  No company data after filtering")
            return None

        # Pivot: metric_code → columns
        df_wide = df_filtered.pivot_table(
            index=['SECURITY_CODE', 'REPORT_DATE'],
            columns='METRIC_CODE',
            values='METRIC_VALUE',
            aggfunc='first'  # Take first value if duplicates
        ).reset_index()

        # Rename columns using mappings
        rename_dict = {'SECURITY_CODE': 'symbol', 'REPORT_DATE': 'report_date'}
        rename_dict.update(self.company_mappings)
        df_wide.rename(columns=rename_dict, inplace=True)

        logger.info(f"  ✅ Company: {len(df_wide)} rows, {df_wide['symbol'].nunique()} tickers, {len(df_wide.columns)-2} metrics")

        return df_wide

    def _load_bank_data(self) -> Optional[pd.DataFrame]:
        """
        Load and pivot bank fundamental data.

        Process:
        1. Load raw data
        2. Filter by ENTITY_TYPE = 'BANK'
        3. Filter metric codes to only those in BANK_MAPPINGS
        4. Pivot METRIC_CODE to columns
        5. Rename columns using mappings

        Returns:
            DataFrame with columns: symbol, report_date, total_assets, customer_loans, nii, ...
        """
        df_raw = self._load_parquet(self.bank_path)
        if df_raw is None:
            return None

        # Filter by entity type
        df_filtered = df_raw[df_raw['ENTITY_TYPE'] == 'BANK'].copy()

        # Log unmapped codes before filtering
        mapped_codes = list(self.bank_mappings.keys())
        self._log_unmapped_codes(df_filtered, mapped_codes, 'BANK')

        # Filter to only mapped metric codes
        df_filtered = df_filtered[df_filtered['METRIC_CODE'].isin(mapped_codes)]

        if len(df_filtered) == 0:
            logger.warning("  ⚠️  No bank data after filtering")
            return None

        # Pivot: metric_code → columns
        df_wide = df_filtered.pivot_table(
            index=['SECURITY_CODE', 'REPORT_DATE'],
            columns='METRIC_CODE',
            values='METRIC_VALUE',
            aggfunc='first'
        ).reset_index()

        # Rename columns using mappings
        rename_dict = {'SECURITY_CODE': 'symbol', 'REPORT_DATE': 'report_date'}
        rename_dict.update(self.bank_mappings)
        df_wide.rename(columns=rename_dict, inplace=True)

        # Calculate derived metrics
        # NPL = sum of groups 3, 4, 5
        if all(col in df_wide.columns for col in ['npl_group3', 'npl_group4', 'npl_group5']):
            df_wide['npl_amount'] = (
                df_wide['npl_group3'].fillna(0) +
                df_wide['npl_group4'].fillna(0) +
                df_wide['npl_group5'].fillna(0)
            )

        # CASA = sum of CASA components
        if all(col in df_wide.columns for col in ['casa_current_deposits', 'casa_demand_deposits', 'casa_savings_no_term']):
            df_wide['casa'] = (
                df_wide['casa_current_deposits'].fillna(0) +
                df_wide['casa_demand_deposits'].fillna(0) +
                df_wide['casa_savings_no_term'].fillna(0)
            )

        # Interest Earning Assets (IEA) = Total Assets - non-earning assets
        # For now, use total_assets as proxy if not available
        if 'iea' not in df_wide.columns and 'total_assets' in df_wide.columns:
            # Rough estimate: IEA ≈ 90% of total assets
            df_wide['iea'] = df_wide['total_assets'] * 0.9
            logger.warning("  ⚠️  IEA not available, using 90% of total assets as estimate")

        logger.info(f"  ✅ Bank: {len(df_wide)} rows, {df_wide['symbol'].nunique()} tickers, {len(df_wide.columns)-2} metrics")

        return df_wide

    def _load_security_data(self) -> Optional[pd.DataFrame]:
        """
        Load and pivot security/brokerage fundamental data.

        Process:
        1. Load raw data
        2. Filter by ENTITY_TYPE = 'SECURITY'
        3. Filter metric codes to only those in SECURITY_MAPPINGS
        4. Pivot METRIC_CODE to columns
        5. Rename columns using mappings

        Returns:
            DataFrame with columns: symbol, report_date, total_assets, margin_loans, fvtpl_securities, ...
        """
        df_raw = self._load_parquet(self.security_path)
        if df_raw is None:
            return None

        # Filter by entity type
        df_filtered = df_raw[df_raw['ENTITY_TYPE'] == 'SECURITY'].copy()

        # Log unmapped codes before filtering
        mapped_codes = list(self.security_mappings.keys())
        self._log_unmapped_codes(df_filtered, mapped_codes, 'SECURITY')

        # Filter to only mapped metric codes
        df_filtered = df_filtered[df_filtered['METRIC_CODE'].isin(mapped_codes)]

        if len(df_filtered) == 0:
            logger.warning("  ⚠️  No security data after filtering")
            return None

        # Pivot: metric_code → columns
        df_wide = df_filtered.pivot_table(
            index=['SECURITY_CODE', 'REPORT_DATE'],
            columns='METRIC_CODE',
            values='METRIC_VALUE',
            aggfunc='first'
        ).reset_index()

        # Rename columns using mappings
        rename_dict = {'SECURITY_CODE': 'symbol', 'REPORT_DATE': 'report_date'}
        rename_dict.update(self.security_mappings)
        df_wide.rename(columns=rename_dict, inplace=True)

        # Calculate total investment = FVTPL + HTM + AFS
        if all(col in df_wide.columns for col in ['fvtpl_securities', 'htm_securities', 'afs_securities']):
            df_wide['total_investment'] = (
                df_wide['fvtpl_securities'].fillna(0) +
                df_wide['htm_securities'].fillna(0) +
                df_wide['afs_securities'].fillna(0)
            )

        # Calculate total liabilities if needed
        if 'total_liabilities' not in df_wide.columns:
            if all(col in df_wide.columns for col in ['short_term_debt', 'long_term_debt']):
                df_wide['total_liabilities'] = (
                    df_wide['short_term_debt'].fillna(0) +
                    df_wide['long_term_debt'].fillna(0)
                )

        logger.info(f"  ✅ Security: {len(df_wide)} rows, {df_wide['symbol'].nunique()} tickers, {len(df_wide.columns)-2} metrics")

        return df_wide

    def _load_insurance_data(self) -> Optional[pd.DataFrame]:
        """
        Load and pivot insurance fundamental data.

        Process:
        1. Load raw data
        2. Filter by ENTITY_TYPE = 'INSURANCE'
        3. Filter metric codes to only those in INSURANCE_MAPPINGS
        4. Pivot METRIC_CODE to columns
        5. Rename columns using mappings

        Returns:
            DataFrame with columns: symbol, report_date, total_assets, total_equity, total_revenue, npatmi
        """
        df_raw = self._load_parquet(self.insurance_path)
        if df_raw is None:
            return None

        # Filter by entity type
        df_filtered = df_raw[df_raw['ENTITY_TYPE'] == 'INSURANCE'].copy()

        # Log unmapped codes before filtering
        mapped_codes = list(self.insurance_mappings.keys())
        self._log_unmapped_codes(df_filtered, mapped_codes, 'INSURANCE')

        # Filter to only mapped metric codes
        df_filtered = df_filtered[df_filtered['METRIC_CODE'].isin(mapped_codes)]

        if len(df_filtered) == 0:
            logger.warning("  ⚠️  No insurance data after filtering")
            return None

        # Pivot: metric_code → columns
        df_wide = df_filtered.pivot_table(
            index=['SECURITY_CODE', 'REPORT_DATE'],
            columns='METRIC_CODE',
            values='METRIC_VALUE',
            aggfunc='first'
        ).reset_index()

        # Rename columns using mappings
        rename_dict = {'SECURITY_CODE': 'symbol', 'REPORT_DATE': 'report_date'}
        rename_dict.update(self.insurance_mappings)
        df_wide.rename(columns=rename_dict, inplace=True)

        logger.info(f"  ✅ Insurance: {len(df_wide)} rows, {df_wide['symbol'].nunique()} tickers, {len(df_wide.columns)-2} metrics")

        return df_wide

    def _aggregate_all_sectors(
        self,
        company_df: Optional[pd.DataFrame],
        bank_df: Optional[pd.DataFrame],
        security_df: Optional[pd.DataFrame],
        insurance_df: Optional[pd.DataFrame]
    ) -> List[Dict[str, Any]]:
        """
        Aggregate all sectors across all report dates.

        Returns:
            List of sector aggregation dictionaries
        """
        results = []

        # Get all unique sectors
        sectors = self.sector_reg.get_all_sectors()
        logger.info(f"  Processing {len(sectors)} sectors")

        # Get all unique report dates across all entities
        all_dates = set()
        for df in [company_df, bank_df, security_df, insurance_df]:
            if df is not None and 'report_date' in df.columns:
                all_dates.update(df['report_date'].unique())

        all_dates = sorted(list(all_dates))
        logger.info(f"  Found {len(all_dates)} unique report dates")

        # Aggregate each sector for each report date
        for sector in sectors:
            for report_date in all_dates:
                sector_data = self._aggregate_sector_single_date(
                    sector=sector,
                    report_date=report_date,
                    company_df=company_df,
                    bank_df=bank_df,
                    security_df=security_df,
                    insurance_df=insurance_df
                )

                if sector_data is not None:
                    results.append(sector_data)

        logger.info(f"  ✅ Generated {len(results)} sector-date records")
        return results

    def _aggregate_sector_single_date(
        self,
        sector: str,
        report_date,
        company_df: Optional[pd.DataFrame],
        bank_df: Optional[pd.DataFrame],
        security_df: Optional[pd.DataFrame],
        insurance_df: Optional[pd.DataFrame]
    ) -> Optional[Dict[str, Any]]:
        """
        Aggregate one sector for one specific report date.

        Args:
            sector: Sector code
            report_date: Report date to aggregate
            company_df, bank_df, security_df, insurance_df: Entity DataFrames

        Returns:
            Dictionary with aggregated sector metrics or None if no data
        """
        # Get tickers in this sector
        tickers = self.sector_reg.get_tickers_by_sector(sector)
        if not tickers:
            return None

        # Filter each DataFrame for this sector + this date
        sector_company = self._filter_sector_date(company_df, tickers, report_date)
        sector_bank = self._filter_sector_date(bank_df, tickers, report_date)
        sector_security = self._filter_sector_date(security_df, tickers, report_date)
        sector_insurance = self._filter_sector_date(insurance_df, tickers, report_date)

        # Check if we have any data for this sector-date
        total_tickers = (
            (len(sector_company) if sector_company is not None else 0) +
            (len(sector_bank) if sector_bank is not None else 0) +
            (len(sector_security) if sector_security is not None else 0) +
            (len(sector_insurance) if sector_insurance is not None else 0)
        )

        if total_tickers == 0:
            return None

        # Aggregate metrics
        result = {
            'sector_code': sector,
            'sector_name_vi': sector,  # Vietnamese name (same as code for now)
            'report_date': pd.to_datetime(report_date),
            'ticker_count': total_tickers,
            'entity_types': self._get_entity_types(sector_company, sector_bank, sector_security, sector_insurance),
        }

        # Aggregate absolute metrics (sum across all entities)
        result.update(self._aggregate_absolute_metrics(
            sector_company, sector_bank, sector_security, sector_insurance
        ))

        # Aggregate bank-specific metrics
        if sector_bank is not None and len(sector_bank) > 0:
            result.update(self._aggregate_bank_metrics(sector_bank))

        # Aggregate security-specific metrics
        if sector_security is not None and len(sector_security) > 0:
            result.update(self._aggregate_security_metrics(sector_security))

        # Calculate data quality score
        result['data_quality_score'] = self._calculate_data_quality(result)

        return result

    def _filter_sector_date(
        self,
        df: Optional[pd.DataFrame],
        tickers: List[str],
        report_date
    ) -> Optional[pd.DataFrame]:
        """
        Filter DataFrame for specific tickers and report date.

        NOTE: This returns data for SINGLE quarter only.
        TTM calculation is done separately in _calculate_ttm_metrics()

        Args:
            df: Entity DataFrame
            tickers: List of ticker symbols
            report_date: Report date to filter

        Returns:
            Filtered DataFrame or None
        """
        if df is None or df.empty:
            return None

        # Filter by tickers
        filtered = df[df['symbol'].isin(tickers)]

        # Filter by report date
        if 'report_date' in filtered.columns:
            filtered = filtered[filtered['report_date'] == report_date]

        return filtered if len(filtered) > 0 else None

    def _get_entity_types(
        self,
        sector_company: Optional[pd.DataFrame],
        sector_bank: Optional[pd.DataFrame],
        sector_security: Optional[pd.DataFrame],
        sector_insurance: Optional[pd.DataFrame]
    ) -> List[str]:
        """Get list of entity types present in this sector."""
        entity_types = []

        if sector_company is not None and len(sector_company) > 0:
            entity_types.append('COMPANY')
        if sector_bank is not None and len(sector_bank) > 0:
            entity_types.append('BANK')
        if sector_security is not None and len(sector_security) > 0:
            entity_types.append('SECURITY')
        if sector_insurance is not None and len(sector_insurance) > 0:
            entity_types.append('INSURANCE')

        return entity_types

    def _aggregate_absolute_metrics(
        self,
        sector_company: Optional[pd.DataFrame],
        sector_bank: Optional[pd.DataFrame],
        sector_security: Optional[pd.DataFrame],
        sector_insurance: Optional[pd.DataFrame]
    ) -> Dict[str, float]:
        """
        Aggregate absolute metrics (sum) across all entity types.

        IMPORTANT: Column names now match metric_mappings.py output after pivot.

        Common metrics:
        - total_revenue (company: net_revenue, bank: toi, security: total_revenue)
        - net_profit (company: npatmi, bank: npatmi, security: npatmi)
        - total_assets
        - total_equity
        - total_liabilities
        - gross_profit
        - operating_profit

        Returns:
            Dictionary of aggregated absolute metrics
        """
        # Initialize result
        metrics = {
            'total_revenue': 0.0,
            'net_profit': 0.0,
            'total_assets': 0.0,
            'total_equity': 0.0,
            'total_liabilities': 0.0,
            'gross_profit': 0.0,
            'operating_profit': 0.0,
            'general_admin_expenses': 0.0,
        }

        # Company metrics (column names from COMPANY_MAPPINGS)
        if sector_company is not None and len(sector_company) > 0:
            # Revenue: 'net_revenue' (CIS_10)
            if 'net_revenue' in sector_company.columns:
                metrics['total_revenue'] += sector_company['net_revenue'].fillna(0).sum()

            # Profit: 'npatmi' (CIS_62)
            if 'npatmi' in sector_company.columns:
                metrics['net_profit'] += sector_company['npatmi'].fillna(0).sum()

            # Balance sheet
            if 'total_assets' in sector_company.columns:
                metrics['total_assets'] += sector_company['total_assets'].fillna(0).sum()
            if 'total_equity' in sector_company.columns:
                metrics['total_equity'] += sector_company['total_equity'].fillna(0).sum()
            if 'total_liabilities' in sector_company.columns:
                metrics['total_liabilities'] += sector_company['total_liabilities'].fillna(0).sum()

            # Profitability metrics
            if 'gross_profit' in sector_company.columns:
                metrics['gross_profit'] += sector_company['gross_profit'].fillna(0).sum()
            if 'operating_profit' in sector_company.columns:
                metrics['operating_profit'] += sector_company['operating_profit'].fillna(0).sum()

        # Bank metrics (column names from BANK_MAPPINGS)
        if sector_bank is not None and len(sector_bank) > 0:
            # Revenue: 'toi' (BIS_14A) - Total Operating Income
            if 'toi' in sector_bank.columns:
                metrics['total_revenue'] += sector_bank['toi'].fillna(0).sum()

            # Profit: 'npatmi' (BIS_22A)
            if 'npatmi' in sector_bank.columns:
                metrics['net_profit'] += sector_bank['npatmi'].fillna(0).sum()

            # Balance sheet
            if 'total_assets' in sector_bank.columns:
                metrics['total_assets'] += sector_bank['total_assets'].fillna(0).sum()
            if 'total_equity' in sector_bank.columns:
                metrics['total_equity'] += sector_bank['total_equity'].fillna(0).sum()

            # Operating expenses (opex is NEGATIVE in raw data, so abs())
            if 'opex' in sector_bank.columns:
                metrics['general_admin_expenses'] += sector_bank['opex'].fillna(0).abs().sum()

        # Security metrics (column names from SECURITY_MAPPINGS)
        if sector_security is not None and len(sector_security) > 0:
            # Revenue: 'total_revenue' (SIS_20)
            if 'total_revenue' in sector_security.columns:
                metrics['total_revenue'] += sector_security['total_revenue'].fillna(0).sum()

            # Profit: 'npatmi' (SIS_201)
            if 'npatmi' in sector_security.columns:
                metrics['net_profit'] += sector_security['npatmi'].fillna(0).sum()
            elif 'net_profit' in sector_security.columns:  # Fallback to SIS_200
                metrics['net_profit'] += sector_security['net_profit'].fillna(0).sum()

            # Balance sheet
            if 'total_assets' in sector_security.columns:
                metrics['total_assets'] += sector_security['total_assets'].fillna(0).sum()
            if 'total_equity' in sector_security.columns:
                metrics['total_equity'] += sector_security['total_equity'].fillna(0).sum()

            # Profitability
            if 'gross_profit' in sector_security.columns:
                metrics['gross_profit'] += sector_security['gross_profit'].fillna(0).sum()

        # Insurance metrics (column names from INSURANCE_MAPPINGS)
        if sector_insurance is not None and len(sector_insurance) > 0:
            # Revenue: 'total_revenue' (IIS_10)
            if 'total_revenue' in sector_insurance.columns:
                metrics['total_revenue'] += sector_insurance['total_revenue'].fillna(0).sum()

            # Profit: 'npatmi' (IIS_50)
            if 'npatmi' in sector_insurance.columns:
                metrics['net_profit'] += sector_insurance['npatmi'].fillna(0).sum()

            # Balance sheet
            if 'total_assets' in sector_insurance.columns:
                metrics['total_assets'] += sector_insurance['total_assets'].fillna(0).sum()
            if 'total_equity' in sector_insurance.columns:
                metrics['total_equity'] += sector_insurance['total_equity'].fillna(0).sum()

        return metrics

    def _aggregate_bank_metrics(self, sector_bank: pd.DataFrame) -> Dict[str, float]:
        """
        Aggregate bank-specific metrics.

        IMPORTANT: Column names from BANK_MAPPINGS after pivot:
        - customer_loans (BBS_161)
        - customer_deposits (BBS_330)
        - casa (calculated from CASA components)
        - nii (BIS_3) - Net Interest Income
        - interest_income (BIS_1)
        - interest_expense (BIS_2)
        - provision_expenses (BIS_16)
        - npl_amount (calculated from NPL groups 3+4+5)
        - iea (calculated or estimated from total_assets)

        Returns:
            Dictionary of bank-specific aggregated metrics
        """
        metrics = {}

        # Loan & Deposit (from BANK_SIZE mappings)
        if 'customer_loans' in sector_bank.columns:
            metrics['customer_loans'] = sector_bank['customer_loans'].fillna(0).sum()

        if 'customer_deposits' in sector_bank.columns:
            metrics['customer_deposits'] = sector_bank['customer_deposits'].fillna(0).sum()

        # CASA (calculated in _load_bank_data)
        if 'casa' in sector_bank.columns:
            metrics['casa_deposits'] = sector_bank['casa'].fillna(0).sum()

        # Income Statement (from BANK_INCOME mappings)
        if 'nii' in sector_bank.columns:
            metrics['total_nii'] = sector_bank['nii'].fillna(0).sum()

        if 'interest_income' in sector_bank.columns:
            metrics['interest_income'] = sector_bank['interest_income'].fillna(0).sum()

        if 'interest_expense' in sector_bank.columns:
            metrics['interest_expense'] = sector_bank['interest_expense'].fillna(0).sum()

        if 'provision_expenses' in sector_bank.columns:
            metrics['provision_expenses'] = sector_bank['provision_expenses'].fillna(0).sum()

        # Asset Quality (NPL calculated in _load_bank_data)
        if 'npl_amount' in sector_bank.columns:
            metrics['npl_amount'] = sector_bank['npl_amount'].fillna(0).sum()

        # Interest Earning Assets (IEA)
        if 'iea' in sector_bank.columns:
            metrics['interest_earning_assets'] = sector_bank['iea'].fillna(0).sum()

        return metrics

    def _aggregate_security_metrics(self, sector_security: pd.DataFrame) -> Dict[str, float]:
        """
        Aggregate security/brokerage-specific metrics.

        IMPORTANT: Column names from SECURITY_MAPPINGS after pivot:
        - margin_loans (SBS_114)
        - fvtpl_securities (SBS_112)
        - htm_securities (SBS_113)
        - afs_securities (SBS_115)
        - total_investment (calculated in _load_security_data)

        Returns:
            Dictionary of security-specific aggregated metrics
        """
        metrics = {}

        # Asset scale (from SECURITY_SCALE mappings)
        if 'margin_loans' in sector_security.columns:
            metrics['margin_loans'] = sector_security['margin_loans'].fillna(0).sum()

        # Investment Portfolio
        if 'fvtpl_securities' in sector_security.columns:
            metrics['fvtpl_assets'] = sector_security['fvtpl_securities'].fillna(0).sum()

        if 'htm_securities' in sector_security.columns:
            metrics['htm_assets'] = sector_security['htm_securities'].fillna(0).sum()

        if 'afs_securities' in sector_security.columns:
            metrics['afs_assets'] = sector_security['afs_securities'].fillna(0).sum()

        # Total investment (calculated in _load_security_data)
        if 'total_investment' in sector_security.columns:
            metrics['total_investment'] = sector_security['total_investment'].fillna(0).sum()

        # Income sources
        if 'income_from_fvtpl' in sector_security.columns:
            metrics['income_from_fvtpl'] = sector_security['income_from_fvtpl'].fillna(0).sum()

        if 'income_from_loans' in sector_security.columns:
            metrics['margin_income'] = sector_security['income_from_loans'].fillna(0).sum()

        return metrics

    def _calculate_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate financial ratios from aggregated sums.

        IMPORTANT: Calculate ratios from SECTOR SUMS, not averages!
        Example: sector_roe = total_net_profit / total_equity

        Ratios to calculate:
        - gross_margin = gross_profit / total_revenue
        - operating_margin = operating_profit / total_revenue
        - net_margin = net_profit / total_revenue
        - sga_ratio = (selling + admin) / total_revenue
        - roe = net_profit / total_equity
        - roa = net_profit / total_assets
        - debt_to_equity = total_liabilities / total_equity
        
        Bank-specific:
        - nim_q = total_nii / interest_earning_assets (quarterly)
        - npl_ratio = npl_amount / customer_loans
        - ldr = customer_loans / customer_deposits
        - casa_ratio = casa_deposits / customer_deposits
        - cir = general_admin_expenses / total_revenue (TOI)

        Security-specific:
        - margin_revenue_ratio
        - brokerage_revenue_ratio

        Company-specific:
        - cip_ratio = construction_in_progress / total_assets

        Args:
            df: DataFrame with aggregated absolute metrics

        Returns:
            DataFrame with added ratio columns
        """
        # Core profitability ratios
        df['gross_margin'] = np.where(
            df['total_revenue'] > 0,
            df['gross_profit'] / df['total_revenue'],
            np.nan
        )

        df['operating_margin'] = np.where(
            df['total_revenue'] > 0,
            df['operating_profit'] / df['total_revenue'],
            np.nan
        )
        
        df['ebit_margin'] = df['operating_margin'] # Alias

        df['net_margin'] = np.where(
            df['total_revenue'] > 0,
            df['net_profit'] / df['total_revenue'],
            np.nan
        )
        
        # SG&A Ratio
        if 'selling_expenses' in df.columns and 'general_admin_expenses' in df.columns:
            df['total_sga'] = df['selling_expenses'].fillna(0) + df['general_admin_expenses'].fillna(0)
            df['sga_ratio'] = np.where(
                df['total_revenue'] > 0,
                df['total_sga'] / df['total_revenue'],
                np.nan
            )

        # Return ratios
        df['roe'] = np.where(
            df['total_equity'] > 0,
            df['net_profit'] / df['total_equity'],
            np.nan
        )

        df['roa'] = np.where(
            df['total_assets'] > 0,
            df['net_profit'] / df['total_assets'],
            np.nan
        )

        # Leverage ratio
        df['debt_to_equity'] = np.where(
            df['total_equity'] > 0,
            df['total_liabilities'] / df['total_equity'],
            np.nan
        )
        
        # CIP Ratio (Company)
        if 'construction_in_progress' in df.columns:
            df['cip_ratio'] = np.where(
                df['total_assets'] > 0,
                df['construction_in_progress'] / df['total_assets'],
                np.nan
            )

        # Bank-specific ratios
        if 'total_nii' in df.columns and 'interest_earning_assets' in df.columns:
            df['nim_q'] = np.where(
                df['interest_earning_assets'] > 0,
                df['total_nii'] / df['interest_earning_assets'],
                np.nan
            )
            # Annualized NIM (approximate)
            df['nim_ttm'] = df['nim_q'] * 4 

        if 'npl_amount' in df.columns and 'customer_loans' in df.columns:
            df['npl_ratio'] = np.where(
                df['customer_loans'] > 0,
                df['npl_amount'] / df['customer_loans'],
                np.nan
            )

        if 'customer_loans' in df.columns and 'customer_deposits' in df.columns:
            df['ldr'] = np.where(
                df['customer_deposits'] > 0,
                df['customer_loans'] / df['customer_deposits'],
                np.nan
            )
            
        if 'casa_deposits' in df.columns and 'customer_deposits' in df.columns:
            df['casa_ratio'] = np.where(
                df['customer_deposits'] > 0,
                df['casa_deposits'] / df['customer_deposits'],
                np.nan
            )
            
        if 'general_admin_expenses' in df.columns and 'total_revenue' in df.columns:
            # For banks, CIR = OPEX (admin expenses) / TOI (total_revenue)
            df['cir'] = np.where(
                df['total_revenue'] > 0,
                df['general_admin_expenses'] / df['total_revenue'],
                np.nan
            )

        # Securities-specific
        if 'brokerage_revenue' in df.columns and 'total_revenue' in df.columns:
             df['brokerage_revenue_ratio'] = np.where(
                df['total_revenue'] > 0,
                df['brokerage_revenue'] / df['total_revenue'],
                np.nan
            )

        return df

    def _calculate_growth(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate YoY and QoQ growth rates.

        Growth metrics:
        - revenue_growth_yoy: YoY revenue growth (vs 4 quarters ago)
        - profit_growth_yoy: YoY profit growth (vs 4 quarters ago)
        - revenue_growth_qoq: QoQ revenue growth (vs 1 quarter ago)
        - profit_growth_qoq: QoQ profit growth (vs 1 quarter ago)

        Logic:
        1. Sort by sector_code + report_date
        2. Use .shift() to get previous periods within each sector group
        3. Calculate percentage change

        Args:
            df: DataFrame with aggregated metrics

        Returns:
            DataFrame with added growth columns
        """
        # Ensure sorted by sector and date
        df = df.sort_values(['sector_code', 'report_date'])

        # YoY growth (4 quarters ago)
        df['revenue_growth_yoy'] = (
            df.groupby('sector_code')['total_revenue']
            .pct_change(periods=4)
        )

        df['profit_growth_yoy'] = (
            df.groupby('sector_code')['net_profit']
            .pct_change(periods=4)
        )

        # QoQ growth (1 quarter ago)
        df['revenue_growth_qoq'] = (
            df.groupby('sector_code')['total_revenue']
            .pct_change(periods=1)
        )

        df['profit_growth_qoq'] = (
            df.groupby('sector_code')['net_profit']
            .pct_change(periods=1)
        )

        return df

    def _calculate_data_quality(self, sector_data: Dict[str, Any]) -> float:
        """
        Calculate data quality score (0-1).

        Based on percentage of non-null core metrics:
        - total_revenue
        - net_profit
        - total_assets
        - total_equity

        Args:
            sector_data: Dictionary of sector metrics

        Returns:
            Quality score between 0 and 1
        """
        core_metrics = ['total_revenue', 'net_profit', 'total_assets', 'total_equity']

        non_null_count = sum(
            1 for metric in core_metrics
            if metric in sector_data and sector_data[metric] is not None and not pd.isna(sector_data[metric])
        )

        return non_null_count / len(core_metrics)

    def run(self, report_date: Optional[str] = None) -> Path:
        """
        Convenience method to run aggregation and save output.

        Args:
            report_date: Optional specific report date (YYYY-MM-DD)

        Returns:
            Path to saved output file
        """
        logger.info("Running FA aggregation...")

        # Run aggregation
        sector_df = self.aggregate_sector_fundamentals(report_date=report_date)

        # Save output
        output_path = self._save_output(
            sector_df,
            filename="sector_fundamental_metrics.parquet",
            index=False
        )

        logger.info(f"✅ FA aggregation complete: {output_path}")
        return output_path


# Main execution for testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Import registries
    from config.registries import MetricRegistry, SectorRegistry

    # Mock ConfigManager (will be replaced with real one later)
    class MockConfigManager:
        def __init__(self):
            self.fa_weights = {}

    # Initialize
    metric_reg = MetricRegistry()
    sector_reg = SectorRegistry()
    config = MockConfigManager()

    # Create aggregator
    agg = FAAggregator(config, sector_reg, metric_reg)

    # Run aggregation
    output_path = agg.run()

    print(f"\n{'=' * 80}")
    print(f"✅ SUCCESS: FA aggregation complete")
    print(f"   Output: {output_path}")
    print(f"{'=' * 80}")
