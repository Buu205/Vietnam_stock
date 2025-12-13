"""
Company Financial Calculator
============================

Tính toán các chỉ số tài chính cơ bản cho công ty dựa trên dữ liệu fundamental.

Các chỉ số được tính toán:
1. Income Statement (đơn vị: tỷ VND):
   - Doanh thu thuần (Net Revenue) = CIS_10 / 1e9
   - Giá vốn hàng bán (COGS) = CIS_11 / 1e9
   - Lợi nhuận gộp (Gross Profit) = CIS_20 / 1e9
   - SG&A = (CIS_25 + CIS_26) / 1e9
   - Lợi nhuận hoạt động (EBIT) = (CIS_20 + CIS_25 + CIS_26) / 1e9
   - Doanh thu tài chính ròng (Net Finance Income) = (CIS_21 + CIS_22) / 1e9
   - EBT = CIS_50 / 1e9
   - NPATMI = CIS_61 / 1e9
   - Depreciation = CCFI_2 / 1e9
   - EBITDA = EBIT + Depreciation

2. Margins (đơn vị: %):
   - Gross profit margin = (CIS_20 / CIS_10) * 100
   - EBIT margin = (EBIT / CIS_10) * 100
   - EBITDA margin = (EBITDA / CIS_10) * 100
   - Net margin = (CIS_61 / CIS_10) * 100

3. Growth Rates (đơn vị: % - Quarter over Quarter):
   - Net Revenue Growth = (Net_Revenue(t) / Net_Revenue(t-1) - 1) * 100
   - Gross Profit Growth = (Gross_Profit(t) / Gross_Profit(t-1) - 1) * 100
   - EBIT Growth = (EBIT(t) / EBIT(t-1) - 1) * 100
   - EBITDA Growth = (EBITDA(t) / EBITDA(t-1) - 1) * 100
   - NPMI Growth = (NPMI(t) / NPMI(t-1) - 1) * 100

4. Ratios:
   - SG&A/DTT ratio = (SG&A / Net_Revenue) * 100

5. Balance Sheet Metrics (đơn vị: tỷ VND):
   - Total Assets = CBS_270 / 1e9
   - Total Liabilities = CBS_300 / 1e9
   - Cash = CBS_110 / 1e9
   - Cash Equivalent = CBS_110 / 1e9
   - Inventory = CBS_140 / 1e9
   - Account Receivable = CBS_130 / 1e9
   - Tangible Fixed Asset = CBS_221 / 1e9
   - Long-term Asset in Progress = CBS_240 / 1e9
   - Short-term Debt = CBS_320 / 1e9
   - Long-term Debt = CBS_338 / 1e9
   - Total Equity = CBS_400 / 1e9

6. Cash Flow Metrics (đơn vị: tỷ VND):
   - Operating Cash Flow = CCFI_20 / 1e9
   - Investment Cash Flow = CCFI_30 / 1e9
   - Capex = CCFI_21 / 1e9
   - Financing Cash Flow = CCFI_40 / 1e9
   - Free Cash Flow = CCFI_50 / 1e9

7. Profitability Ratios:
   - ROE = (CIS_61 / CBS_400) * 100 (đơn vị: %)
   - ROA = (CIS_61 / CBS_270) * 100 (đơn vị: %)
   - EPS = CIS_61 (TTM) * 1e9 / (CBS_411A / 10,000) (đơn vị: VND)

Author: AI Assistant
Date: 2025-01-27
"""

import pandas as pd
import numpy as np
import os
from typing import Dict, List, Optional, Tuple
import logging
import sys

# Add core module to path for date formatter
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
from date_formatter import DateFormatter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompanyFinancialCalculator:
    """Tính toán các chỉ số tài chính cơ bản cho công ty."""
    
    def __init__(self, data_path: str):
        """
        Khởi tạo calculator.
        
        Args:
            data_path: Đường dẫn đến file parquet chứa dữ liệu fundamental
        """
        self.data_path = data_path
        self.df = None
        self.date_formatter = DateFormatter()
        self.results = None
        
        # Mapping các metric codes
        self.metric_mapping = {
            # Income Statement
            'net_revenue': 'CIS_10',               # Doanh thu thuần
            'cogs': 'CIS_11',                      # Giá vống hàng bán
            'gross_profit': 'CIS_20',              # Lợi nhuận gộp
            'sga': ['CIS_25', 'CIS_26'],           # SG&A (Chi phí bán hàng + Chi phí quản lý)
            'finance_income': 'CIS_21',            # Doanh thu hoạt động tài chính
            'finance_cost': 'CIS_22',              # Chi phí tài chính
            'ebt': 'CIS_50',                       # Lợi nhuận trước thuế
            'npatmi': 'CIS_61',                    # Lợi nhuận sau thuế công ty mẹ
            'depreciation': 'CCFI_2',              # Khấu hao TSCĐ và BĐSĐT
            
            # Cash Flow Statement
            'operating_cf': 'CCFI_20',             # Dòng tiền từ hoạt động kinh doanh
            'inv_cf': 'CCFI_30',                   # Dòng tiền từ hoạt động đầu tư
            'capex': 'CCFI_21',                    # Vốn đầu tư (Capex)
            'fin_cf': 'CCFI_40',                   # Dòng tiền từ hoạt động tài chính
            'fcf': 'CCFI_50',                      # Dòng tiền tự do (Free Cash Flow)
            
            # Balance Sheet
            'equity': 'CBS_400',                   # Vốn chủ sở hữu
            'total_assets': 'CBS_270',             # Tổng tài sản
            'total_liabilities': 'CBS_300',        # Tổng nợ phải trả
            'cash': 'CBS_110',                     # Tiền mặt
            'cash_equivalent': 'CBS_110',          # Tiền và các khoản tương đương tiền (cùng CBS_110)
            'inventory': 'CBS_140',                # Hàng tồn kho
            'account_receivable': 'CBS_130',       # Phải thu khách hàng
            'tangible_fixed_asset': 'CBS_221',     # Tài sản cố định hữu hình
            'long_term_asset_in_progress': 'CBS_240', # Tài sản dài hạn khác đang trong quá trình đầu tư
            'st_debt': 'CBS_320',                  # Nợ vay ngắn hạn ròng
            'lt_debt': 'CBS_338',                  # Nợ vay dài hạn ròng
            'common_shares': 'CBS_411A',           # Cổ phiếu phổ thông có quyền biểu quyết
        }
    
    def load_data(self) -> pd.DataFrame:
        """Đọc dữ liệu từ file parquet."""
        try:
            logger.info(f"Đang đọc dữ liệu từ {self.data_path}")
            self.df = pd.read_parquet(self.data_path)
            logger.info(f"Đã đọc {len(self.df)} records")
            return self.df
        except Exception as e:
            logger.error(f"Lỗi khi đọc dữ liệu: {e}")
            raise
    
    def pivot_data(self) -> pd.DataFrame:
        """
        Chuyển đổi dữ liệu từ long format sang wide format.
        
        Returns:
            DataFrame với columns là các metric codes và values là metric values
        """
        if self.df is None:
            self.load_data()
        
        # Chỉ sử dụng dữ liệu theo quý để tránh trộn với yearly/semi
        quarterly_df = self.df[self.df['FREQ_CODE'] == 'Q'].copy()

        # Pivot data để có các metric codes làm columns
        pivot_df = quarterly_df.pivot_table(
            index=['SECURITY_CODE', 'REPORT_DATE', 'YEAR', 'QUARTER', 'FREQ_CODE'],
            columns='METRIC_CODE',
            values='METRIC_VALUE',
            aggfunc='first'
        ).reset_index()
        
        # Flatten column names
        pivot_df.columns.name = None
        
        logger.info(f"Đã pivot dữ liệu: {pivot_df.shape}")
        return pivot_df
    
    def calculate_income_statement(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính toán các chỉ số Income Statement.
        
        Args:
            df: DataFrame đã được pivot
            
        Returns:
            DataFrame với các chỉ số Income Statement
        """
        result_df = df.copy()
        
        # Doanh thu thuần (chuyển từ VND sang tỷ VND)
        result_df['net_revenue'] = df.get('CIS_10', np.nan) / 1e9
        
        # Giá vốn hàng bán (chuyển từ VND sang tỷ VND)
        result_df['cogs'] = df.get('CIS_11', np.nan) / 1e9
        
        # Lợi nhuận gộp (chuyển từ VND sang tỷ VND)
        result_df['gross_profit'] = df.get('CIS_20', np.nan) / 1e9
        
        # SG&A (Chi phí bán hàng + Chi phí quản lý) (chuyển từ VND sang tỷ VND)
        # Handle NaN values properly
        sga_sales = df.get('CIS_25', np.nan)
        sga_admin = df.get('CIS_26', np.nan)

        # Normalize expense signs: ensure expenses are negative (some quarters stored as positive)
        if sga_sales is not None:
            sga_sales = np.where(pd.isna(sga_sales), np.nan, np.where(sga_sales > 0, -sga_sales, sga_sales))
        if sga_admin is not None:
            sga_admin = np.where(pd.isna(sga_admin), np.nan, np.where(sga_admin > 0, -sga_admin, sga_admin))
        
        # If both are NaN, result is NaN. If one is NaN, use the other. If both exist, sum them.
        result_df['sga'] = np.where(
            pd.isna(sga_sales) & pd.isna(sga_admin), np.nan,
            np.where(pd.isna(sga_sales), sga_admin,
                    np.where(pd.isna(sga_admin), sga_sales, sga_sales + sga_admin))
        ) / 1e9
        
        # Lợi nhuận hoạt động (EBIT) (chuyển từ VND sang tỷ VND)
        # EBIT = Gross Profit - SG&A
        gross_profit_raw = df.get('CIS_20', np.nan)
        sga_raw = np.where(
            pd.isna(sga_sales) & pd.isna(sga_admin), np.nan,
            np.where(pd.isna(sga_sales), sga_admin,
                    np.where(pd.isna(sga_admin), sga_sales, sga_sales + sga_admin))
        )
        
        # Calculate EBIT with proper NaN handling
        # SGA values are stored as negative in raw data, so we add them (subtract negative = add)
        result_df['ebit'] = (
            np.where(pd.isna(gross_profit_raw), 0, gross_profit_raw) +
            np.where(pd.isna(sga_raw), 0, sga_raw)  # SGA is already negative, so adding = subtracting
        ) / 1e9
        
        # Doanh thu tài chính ròng (chuyển từ VND sang tỷ VND)
        finance_income = df.get('CIS_21', np.nan)
        finance_cost = df.get('CIS_22', np.nan)
        result_df['net_finance_income'] = (
            np.where(pd.isna(finance_income), 0, finance_income) +
            np.where(pd.isna(finance_cost), 0, finance_cost)
        ) / 1e9
        
        # EBT (Lợi nhuận trước thuế) (chuyển từ VND sang tỷ VND)
        result_df['ebt'] = df.get('CIS_50', np.nan) / 1e9
        
        # NPATMI (Lợi nhuận sau thuế công ty mẹ) (chuyển từ VND sang tỷ VND)
        result_df['npatmi'] = df.get('CIS_61', np.nan) / 1e9
        
        # Depreciation (chuyển từ VND sang tỷ VND) - if missing, assume 0
        depreciation_raw = df.get('CCFI_2', np.nan)
        result_df['depreciation'] = np.where(pd.isna(depreciation_raw), 0, depreciation_raw) / 1e9
        
        # EBITDA = EBIT + Depreciation
        result_df['ebitda'] = result_df['ebit'] + result_df['depreciation']
        
        return result_df
    
    def calculate_margins(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính toán các chỉ số Margin.
        
        Args:
            df: DataFrame đã có các chỉ số Income Statement
            
        Returns:
            DataFrame với các chỉ số Margin
        """
        result_df = df.copy()
        
        # Tránh chia cho 0
        net_revenue = df['net_revenue'].replace(0, np.nan)
        
        # Gross profit margin (nhân 100 để hiển thị %)
        result_df['gross_profit_margin'] = np.where(
            net_revenue != 0,
            (df['gross_profit'] / net_revenue) * 100,
            np.nan
        )
        
        # EBIT margin (nhân 100 để hiển thị %)
        result_df['ebit_margin'] = np.where(
            net_revenue != 0,
            (df['ebit'] / net_revenue) * 100,
            np.nan
        )
        
        # EBITDA margin (nhân 100 để hiển thị %)
        result_df['ebitda_margin'] = np.where(
            net_revenue != 0,
            (df['ebitda'] / net_revenue) * 100,
            np.nan
        )
        
        # Net margin (nhân 100 để hiển thị %)
        result_df['net_margin'] = np.where(
            net_revenue != 0,
            (df['npatmi'] / net_revenue) * 100,
            np.nan
        )
        
        return result_df
    
    def calculate_growth_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính toán các chỉ số Growth Rate theo quý (Quarter over Quarter).
        
        Args:
            df: DataFrame đã có các chỉ số cơ bản
            
        Returns:
            DataFrame với các chỉ số Growth Rate
        """
        result_df = df.copy()
        
        # Sắp xếp theo symbol và date để tính growth rate đúng
        df_sorted = result_df.sort_values(['SECURITY_CODE', 'REPORT_DATE'])
        
        # Tính growth rate cho từng symbol riêng biệt
        for symbol in df_sorted['SECURITY_CODE'].unique():
            symbol_mask = df_sorted['SECURITY_CODE'] == symbol
            
            # Net Revenue Growth Rate (QoQ)
            df_sorted.loc[symbol_mask, 'net_revenue_gr'] = df_sorted.loc[symbol_mask, 'net_revenue'].pct_change(fill_method=None) * 100
            
            # Gross Profit Growth Rate (QoQ)
            df_sorted.loc[symbol_mask, 'gross_profit_gr'] = df_sorted.loc[symbol_mask, 'gross_profit'].pct_change(fill_method=None) * 100
            
            # EBIT Growth Rate (QoQ)
            df_sorted.loc[symbol_mask, 'ebit_gr'] = df_sorted.loc[symbol_mask, 'ebit'].pct_change(fill_method=None) * 100
            
            # EBITDA Growth Rate (QoQ)
            df_sorted.loc[symbol_mask, 'ebitda_gr'] = df_sorted.loc[symbol_mask, 'ebitda'].pct_change(fill_method=None) * 100
            
            # NPMI Growth Rate (QoQ)
            df_sorted.loc[symbol_mask, 'npatmi_gr'] = df_sorted.loc[symbol_mask, 'npatmi'].pct_change(fill_method=None) * 100
        
        # Tính SG&A/DTT ratio (SG&A / Doanh thu thuần)
        # Tránh chia cho 0
        net_revenue = df_sorted['net_revenue'].replace(0, np.nan)
        result_df['sga_dtt_ratio'] = np.where(
            net_revenue != 0,
            (df_sorted['sga'] / net_revenue) * 100,  # Chuyển thành phần trăm
            np.nan
        )
        
        # Copy growth rates từ df_sorted về result_df
        result_df['net_revenue_gr'] = df_sorted['net_revenue_gr']
        result_df['gross_profit_gr'] = df_sorted['gross_profit_gr']
        result_df['ebit_gr'] = df_sorted['ebit_gr']
        result_df['ebitda_gr'] = df_sorted['ebitda_gr']
        result_df['npatmi_gr'] = df_sorted['npatmi_gr']
        
        return result_df
    
    def calculate_balance_sheet_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính toán các chỉ số Balance Sheet.
        
        Args:
            df: DataFrame đã có các chỉ số cơ bản
            
        Returns:
            DataFrame với các chỉ số Balance Sheet
        """
        result_df = df.copy()
        
        # Lấy dữ liệu Balance Sheet (chuyển từ VND sang tỷ VND)
        result_df['total_assets'] = result_df.get('CBS_270', 0) / 1e9
        result_df['total_liabilities'] = result_df.get('CBS_300', 0) / 1e9
        result_df['cash'] = result_df.get('CBS_110', 0) / 1e9
        result_df['cash_equivalent'] = result_df.get('CBS_110', 0) / 1e9
        result_df['inventory'] = result_df.get('CBS_140', 0) / 1e9
        result_df['account_receivable'] = result_df.get('CBS_130', 0) / 1e9
        result_df['tangible_fixed_asset'] = result_df.get('CBS_221', 0) / 1e9
        result_df['long_term_asset_in_progress'] = result_df.get('CBS_240', 0) / 1e9
        result_df['st_debt'] = result_df.get('CBS_320', 0) / 1e9
        result_df['lt_debt'] = result_df.get('CBS_338', 0) / 1e9
        
        return result_df
    
    def calculate_cash_flow_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính toán các chỉ số Cash Flow.
        
        Args:
            df: DataFrame đã có các chỉ số cơ bản
            
        Returns:
            DataFrame với các chỉ số Cash Flow
        """
        result_df = df.copy()
        
        # Lấy dữ liệu Cash Flow (chuyển từ VND sang tỷ VND)
        result_df['operating_cf'] = result_df.get('CCFI_20', 0) / 1e9
        result_df['inv_cf'] = result_df.get('CCFI_30', 0) / 1e9
        result_df['capex'] = result_df.get('CCFI_21', 0) / 1e9
        result_df['fin_cf'] = result_df.get('CCFI_40', 0) / 1e9
        result_df['fcf'] = result_df.get('CCFI_50', 0) / 1e9
        
        return result_df
    
    def calculate_profitability_ratios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính toán các chỉ số Profitability.
        
        Args:
            df: DataFrame đã có các chỉ số cơ bản
            
        Returns:
            DataFrame với các chỉ số Profitability
        """
        result_df = df.copy()
        
        # Lấy dữ liệu Balance Sheet (chuyển từ VND sang tỷ VND)
        equity = df.get('CBS_400', 0) / 1e9
        total_assets = df.get('CBS_270', 0) / 1e9
        # Sửa: common_shares phải chia cho 10,000 để ra số cổ phiếu thực tế
        common_shares = df.get('CBS_411A', 0) / 10000
        
        # ROE (Return on Equity) (nhân 100 để hiển thị %)
        result_df['roe'] = np.where(
            equity != 0,
            (df['npatmi'] / equity) * 100,
            np.nan
        )
        
        # ROA (Return on Assets) (nhân 100 để hiển thị %)
        result_df['roa'] = np.where(
            total_assets != 0,
            (df['npatmi'] / total_assets) * 100,
            np.nan
        )
        
        # EPS (Earnings Per Share) - chuyển đổi từ tỷ VND sang VND
        # Sửa lại logic: npatmi đang là tỷ VND, cần nhân lại 1e9 để ra VND, và common_shares phải chia cho 10,000
        result_df['eps'] = np.where(
            common_shares != 0,
            (df['npatmi'] * 1e9) / common_shares,  # NPATMI từ tỷ VND, chia cho số cổ phiếu thực tế, ra VND/cp
            np.nan
        )
        
        return result_df
    
    def calculate_ttm_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính toán các chỉ số TTM (Trailing Twelve Months) với 4 quý liên tục.
        
        Args:
            df: DataFrame với dữ liệu theo quý
            
        Returns:
            DataFrame với các chỉ số TTM
        """
        result_df = df.copy()
        
        # Sắp xếp theo symbol và date
        df_sorted = df.sort_values(['SECURITY_CODE', 'REPORT_DATE'])
        
        # Tính TTM cho các chỉ số quan trọng
        ttm_metrics = ['net_revenue', 'cogs', 'gross_profit', 'sga', 'ebit', 
                      'net_finance_income', 'ebt', 'npatmi', 'depreciation', 'ebitda']
        
        # Initialize TTM columns
        for metric in ttm_metrics:
            if metric in df_sorted.columns:
                df_sorted[f'{metric}_ttm'] = np.nan
        
        # Process each symbol separately to get best available 4 quarters
        for symbol in df_sorted['SECURITY_CODE'].unique():
            symbol_data = df_sorted[df_sorted['SECURITY_CODE'] == symbol].copy()
            
            # Filter for quarterly data only (Q4 có 2 dạng Y và Q, ưu tiên Q)
            quarterly_data = symbol_data[symbol_data['FREQ_CODE'] == 'Q'].copy()
            
            if len(quarterly_data) < 4:
                continue  # Skip if less than 4 quarters
            
            # Get unique quarters sorted by date
            unique_quarters = quarterly_data[['YEAR', 'QUARTER', 'REPORT_DATE']].drop_duplicates().sort_values('REPORT_DATE')
            
            if len(unique_quarters) < 4:
                continue  # Skip if less than 4 quarters
            
            # Calculate TTM for each quarter that has at least 4 quarters of data available
            for i in range(3, len(unique_quarters)):  # Start from 4th quarter
                current_quarter = unique_quarters.iloc[i]
                current_date = current_quarter['REPORT_DATE']
                current_mask = (df_sorted['SECURITY_CODE'] == symbol) & (df_sorted['REPORT_DATE'] == current_date)
                
                # Find 4 most recent quarters with complete data for this date
                available_quarters = unique_quarters[unique_quarters['REPORT_DATE'] <= current_date]
                
                if len(available_quarters) < 4:
                    continue  # Not enough historical data
                
                # Get latest 4 quarters (not necessarily consecutive)
                latest_4_quarters = available_quarters.tail(4)
                
                # Calculate TTM for this point
                for metric in ttm_metrics:
                    if metric in df_sorted.columns:
                        ttm_value = 0
                        quarters_with_data = 0
                        
                        for _, quarter_row in latest_4_quarters.iterrows():
                            quarter_mask = (quarterly_data['SECURITY_CODE'] == symbol) & (quarterly_data['REPORT_DATE'] == quarter_row['REPORT_DATE'])
                            
                            if not quarterly_data[quarter_mask].empty:
                                quarter_value = quarterly_data[quarter_mask][metric].iloc[0]
                                
                                # Handle NaN values - treat as 0 for summation
                                if pd.isna(quarter_value):
                                    quarter_value = 0
                                
                                ttm_value += quarter_value
                                quarters_with_data += 1
                        
                        # Only set TTM if we have data from at least 3 quarters (75% coverage)
                        if quarters_with_data >= 3:
                            df_sorted.loc[current_mask, f'{metric}_ttm'] = ttm_value
        
        # Tính TTM margins
        net_revenue_ttm = df_sorted['net_revenue_ttm'].replace(0, np.nan)
        
        df_sorted['gross_profit_margin_ttm'] = np.where(
            net_revenue_ttm != 0,
            (df_sorted['gross_profit_ttm'] / net_revenue_ttm) * 100,
            np.nan
        )
        
        df_sorted['ebit_margin_ttm'] = np.where(
            net_revenue_ttm != 0,
            (df_sorted['ebit_ttm'] / net_revenue_ttm) * 100,
            np.nan
        )
        
        df_sorted['ebitda_margin_ttm'] = np.where(
            net_revenue_ttm != 0,
            (df_sorted['ebitda_ttm'] / net_revenue_ttm) * 100,
            np.nan
        )
        
        df_sorted['net_margin_ttm'] = np.where(
            net_revenue_ttm != 0,
            (df_sorted['npatmi_ttm'] / net_revenue_ttm) * 100,
            np.nan
        )
        
        # Tính TTM ROE, ROA, EPS (chuyển từ VND sang tỷ VND)
        equity = df_sorted.get('CBS_400', 0) / 1e9
        total_assets = df_sorted.get('CBS_270', 0) / 1e9
        # Sửa: common_shares phải chia cho 10,000 để ra số cổ phiếu thực tế
        common_shares = df_sorted.get('CBS_411A', 0) / 10000
        
        df_sorted['roe_ttm'] = np.where(
            equity != 0,
            (df_sorted['npatmi_ttm'] / equity) * 100,
            np.nan
        )
        
        df_sorted['roa_ttm'] = np.where(
            total_assets != 0,
            (df_sorted['npatmi_ttm'] / total_assets) * 100,
            np.nan
        )
        
        # EPS TTM: npatmi_ttm đang là tỷ VND, cần nhân lại 1e9 để ra VND, và common_shares phải chia cho 10,000
        df_sorted['eps_ttm'] = np.where(
            common_shares != 0,
            (df_sorted['npatmi_ttm'] * 1e9) / common_shares,  # NPATMI_TTM từ tỷ VND, chia cho số cổ phiếu thực tế, ra VND/cp
            np.nan
        )
        
        return df_sorted
    
    def optimize_output(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tối ưu hóa kết quả - chỉ giữ lại các cột cần thiết với tên dễ đọc.
        
        Args:
            df: DataFrame với tất cả các chỉ số đã tính toán
            
        Returns:
            DataFrame đã được tối ưu hóa
        """
        # Định nghĩa mapping tên cột cũ -> tên cột mới (mở rộng để bao gồm tất cả cột mới)
        column_mapping = {
            # Thông tin cơ bản
            'SECURITY_CODE': 'symbol',
            'REPORT_DATE': 'report_date',
            'YEAR': 'year',
            'QUARTER': 'quarter',
            'FREQ_CODE': 'freq_code',
            
            # Income Statement
            'net_revenue': 'net_revenue',
            'cogs': 'cogs',
            'gross_profit': 'gross_profit',
            'sga': 'sga',
            'ebit': 'ebit',
            'net_finance_income': 'net_finance_income',
            'ebt': 'ebt',
            'npatmi': 'npatmi',
            'depreciation': 'depreciation',
            'ebitda': 'ebitda',
            
            # Margins
            'gross_profit_margin': 'gross_margin',
            'ebit_margin': 'ebit_margin',
            'ebitda_margin': 'ebitda_margin',
            'net_margin': 'net_margin',
            
            # Growth Rates
            'net_revenue_gr': 'net_revenue_gr',
            'gross_profit_gr': 'gross_profit_gr',
            'ebit_gr': 'ebit_gr',
            'ebitda_gr': 'ebitda_gr',
            'npatmi_gr': 'npatmi_gr',
            
            # Ratios
            'sga_dtt_ratio': 'sga_dtt_ratio',
            
            # Balance Sheet (giữ nguyên tên cột vì đã đúng)
            'total_liabilities': 'total_liabilities',
            'cash': 'cash',
            'cash_equivalent': 'cash_equivalent',
            'inventory': 'inventory',
            'account_receivable': 'account_receivable',
            'tangible_fixed_asset': 'tangible_fixed_asset',
            'long_term_asset_in_progress': 'long_term_asset_in_progress',
            'st_debt': 'st_debt',
            'lt_debt': 'lt_debt',
            
            # Cash Flow (giữ nguyên tên cột vì đã đúng)
            'operating_cf': 'operating_cf',
            'inv_cf': 'inv_cf',
            'capex': 'capex',
            'fin_cf': 'fin_cf',
            'fcf': 'fcf',
            
            # Profitability Ratios
            'roe': 'roe',
            'roa': 'roa',
            'eps': 'eps',
            
            # TTM Metrics
            'net_revenue_ttm': 'net_revenue_ttm',
            'gross_profit_ttm': 'gross_profit_ttm',
            'ebit_ttm': 'ebit_ttm',
            'ebitda_ttm': 'ebitda_ttm',
            'npatmi_ttm': 'npatmi_ttm',
            'gross_profit_margin_ttm': 'gross_margin_ttm',
            'ebit_margin_ttm': 'ebit_margin_ttm',
            'ebitda_margin_ttm': 'ebitda_margin_ttm',
            'net_margin_ttm': 'net_margin_ttm',
            'roe_ttm': 'roe_ttm',
            'roa_ttm': 'roa_ttm',
            'eps_ttm': 'eps_ttm'
        }
        
        # Chọn chỉ các cột cần thiết
        required_columns = list(column_mapping.keys())
        available_columns = [col for col in required_columns if col in df.columns]
        
        # Tạo DataFrame mới chỉ với các cột cần thiết
        optimized_df = df[available_columns].copy()
        
        # Đổi tên cột
        optimized_df = optimized_df.rename(columns=column_mapping)
        
        # Sắp xếp lại thứ tự cột (mở rộng để bao gồm tất cả cột mới)
        column_order = [
            'symbol', 'report_date', 'year', 'quarter', 'freq_code',
            'net_revenue', 'cogs', 'gross_profit', 'sga',
            'ebit', 'net_finance_income', 'ebt', 'npatmi', 'depreciation', 'ebitda',
            'gross_margin', 'ebit_margin', 'ebitda_margin', 'net_margin',
            'net_revenue_gr', 'gross_profit_gr', 'ebit_gr', 'ebitda_gr', 'npatmi_gr',
            'sga_dtt_ratio',
            'total_assets', 'total_liabilities', 'cash', 'cash_equivalent', 'inventory', 'account_receivable',
            'tangible_fixed_asset', 'long_term_asset_in_progress', 'st_debt', 'lt_debt',
            'operating_cf', 'inv_cf', 'capex', 'fin_cf', 'fcf',
            'roe', 'roa', 'eps',
            'net_revenue_ttm', 'gross_profit_ttm', 'ebit_ttm', 'ebitda_ttm', 'npatmi_ttm',
            'gross_margin_ttm', 'ebit_margin_ttm', 'ebitda_margin_ttm', 'net_margin_ttm',
            'roe_ttm', 'roa_ttm', 'eps_ttm'
        ]
        
        # Chỉ giữ lại các cột có trong DataFrame
        final_columns = [col for col in column_order if col in optimized_df.columns]
        optimized_df = optimized_df[final_columns]
        
        # Chuẩn hóa date format trước khi return
        logger.info("Standardizing date format to YYYY-MM-DD...")
        optimized_df = self.date_formatter.standardize_all_date_columns(optimized_df, inplace=True)
        
        logger.info(f"Đã tối ưu hóa từ {len(df.columns)} cột xuống {len(optimized_df.columns)} cột")
        logger.info(f"Date format sample: {optimized_df['report_date'].head(3).tolist() if 'report_date' in optimized_df.columns else 'No report_date column'}")
        
        return optimized_df
    
    def calculate_all_metrics(self) -> pd.DataFrame:
        """
        Tính toán tất cả các chỉ số tài chính.
        
        Returns:
            DataFrame với tất cả các chỉ số đã tính toán
        """
        logger.info("Bắt đầu tính toán các chỉ số tài chính...")
        
        # Đọc và pivot dữ liệu
        pivot_df = self.pivot_data()
        
        # Tính toán Income Statement
        logger.info("Tính toán Income Statement...")
        income_df = self.calculate_income_statement(pivot_df)
        
        # Tính toán Margins
        logger.info("Tính toán Margins...")
        margin_df = self.calculate_margins(income_df)
        
        # Tính toán Growth Rates
        logger.info("Tính toán Growth Rates...")
        growth_df = self.calculate_growth_rates(margin_df)
        
        # Tính toán Balance Sheet Metrics
        logger.info("Tính toán Balance Sheet Metrics...")
        balance_sheet_df = self.calculate_balance_sheet_metrics(growth_df)
        
        # Tính toán Cash Flow Metrics
        logger.info("Tính toán Cash Flow Metrics...")
        cash_flow_df = self.calculate_cash_flow_metrics(balance_sheet_df)
        
        # Tính toán Profitability Ratios
        logger.info("Tính toán Profitability Ratios...")
        profitability_df = self.calculate_profitability_ratios(cash_flow_df)
        
        # Tính toán TTM metrics
        logger.info("Tính toán TTM metrics...")
        ttm_df = self.calculate_ttm_metrics(profitability_df)
        
        # Tối ưu hóa kết quả - chỉ giữ lại các cột cần thiết
        logger.info("Tối ưu hóa kết quả...")
        optimized_df = self.optimize_output(ttm_df)
        
        self.results = optimized_df
        logger.info(f"Hoàn thành tính toán: {optimized_df.shape}")
        
        return optimized_df
    
    def save_results(self, output_path: str) -> None:
        """
        Lưu kết quả ra file parquet.
        
        Args:
            output_path: Đường dẫn file output
        """
        if self.results is None:
            raise ValueError("Chưa có kết quả để lưu. Hãy chạy calculate_all_metrics() trước.")
        
        # Tạo thư mục nếu chưa có
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Lưu file
        self.results.to_parquet(output_path, index=False)
        logger.info(f"Đã lưu kết quả vào {output_path}")
    
    def get_summary_stats(self) -> pd.DataFrame:
        """
        Lấy thống kê tóm tắt của các chỉ số đã tính toán.
        
        Returns:
            DataFrame với thống kê tóm tắt
        """
        if self.results is None:
            raise ValueError("Chưa có kết quả. Hãy chạy calculate_all_metrics() trước.")
        
        # Các chỉ số cần thống kê (sử dụng tên cột mới)
        metrics = [
            'gross_margin', 'ebit_margin', 'ebitda_margin', 'net_margin',
            'net_revenue_gr', 'gross_profit_gr', 'ebit_gr', 'ebitda_gr', 'npatmi_gr',
            'sga_dtt_ratio',
            'roe', 'roa', 'eps',
            'gross_margin_ttm', 'ebit_margin_ttm', 'ebitda_margin_ttm', 'net_margin_ttm',
            'roe_ttm', 'roa_ttm', 'eps_ttm'
        ]
        
        summary_stats = []
        for metric in metrics:
            if metric in self.results.columns:
                stats = self.results[metric].describe()
                stats['metric'] = metric
                summary_stats.append(stats)
        
        return pd.DataFrame(summary_stats)


def main():
    """Hàm main để chạy calculator."""
    # Xác định PROJECT_ROOT
    from pathlib import Path
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    
    # Đường dẫn dữ liệu
    data_path = f"{project_root}/data_warehouse/raw/fundamental/processed/company_full.parquet"
    output_path = f"{project_root}/calculated_results/fundamental/company/company_financial_metrics.parquet"
    
    # Khởi tạo calculator
    calculator = CompanyFinancialCalculator(data_path)
    
    # Tính toán các chỉ số
    results = calculator.calculate_all_metrics()
    
    # Lưu kết quả
    calculator.save_results(output_path)
    
    # In thống kê tóm tắt
    print("\n=== THỐNG KÊ TÓM TẮT ===")
    summary = calculator.get_summary_stats()
    print(summary[['metric', 'count', 'mean', 'std', 'min', 'max']].round(4))
    
    print(f"\nĐã hoàn thành tính toán và lưu kết quả vào {output_path}")


if __name__ == "__main__":
    main()
