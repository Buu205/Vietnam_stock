"""
Công cụ tính toán EV/EBITDA Lịch sử - Tính toán chỉ số EV/EBITDA theo chuỗi thời gian hàng ngày
Đã được tái cấu trúc để sử dụng ValuationMetricMapper và ValuationFormulas
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import logging
import sys
import warnings

# PROJECT_ROOT = thư mục stock_dashboard (3 cấp trên file hiện tại)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Import DateFormatter từ core theo absolute package path
try:
    from PROCESSORS.core.shared.date_formatter import DateFormatter
except ImportError:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.append(str(PROJECT_ROOT))
    from PROCESSORS.core.shared.date_formatter import DateFormatter

# Import standardized formulas and mapper
from PROCESSORS.valuation.formulas.valuation_formulas import calculate_ev_ebitda, calculate_enterprise_value, safe_divide
from PROCESSORS.valuation.formulas.metric_mapper import MetricRegistryLoader

from typing import Dict, List, Optional, Tuple

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class HistoricalEVEBITDACalculator:
    """
    Tính toán chỉ số EV/EBITDA theo chuỗi thời gian hàng ngày.
    
    Class này chịu trách nhiệm:
    1. Tải dữ liệu cơ bản (Nợ, Tiền mặt, EBITDA) và dữ liệu thị trường.
    2. Chuẩn hóa và ghép nối dữ liệu bằng Metric Registry Loader.
    3. Tính toán Enterprise Value (EV) và EV/EBITDA hàng ngày.
    """
    
    METADATA_PATH = PROJECT_ROOT / 'config' / 'metadata' / 'ticker_details.json' # Updated to JSON

    def __init__(self):
        self.base_path = PROJECT_ROOT
        self.ohlcv_path = self.base_path / 'DATA' / 'raw' / 'ohlcv' / 'OHLCV_mktcap.parquet'
        self.output_path = self.base_path / 'DATA' / 'processed' / 'valuation' / 'ev_ebitda' / 'historical'
        
        # Initialize Smart Mapper
        self.mapper = MetricRegistryLoader()
        self.metadata = self.load_metadata() # Load metadata during initialization
        
        # Helper caches
        self.fundamental_data = None
        self.ohlcv_data = None
        self.daily_market_data = None
        
        # self.symbol_entity_types will be populated from self.metadata in load_data
        self.symbol_entity_types = {} 
    
    def load_metadata(self) -> pd.DataFrame:
        """
        Load ticker metadata from ticker_details.json
        Returns: DataFrame with ['symbol', 'entity_type']
        """
        if not self.METADATA_PATH.exists():
            raise FileNotFoundError(f"Metadata file not found: {self.METADATA_PATH}")
            
        try:
            with open(self.METADATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert nested dict to DataFrame
            df = pd.DataFrame.from_dict(data, orient='index').reset_index()
            # Rename columns
            df.rename(columns={'index': 'symbol', 'entity': 'entity_type'}, inplace=True)
            
            # Normalize
            df['symbol'] = df['symbol'].str.upper().str.strip()
            
            if 'entity_type' in df.columns:
                df['entity_type'] = df['entity_type'].str.upper().str.strip()
            else:
                logger.warning("Entity type missing in metadata, defaulting to COMPANY")
                df['entity_type'] = 'COMPANY'
                
            return df[['symbol', 'entity_type']]
            
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return pd.DataFrame(columns=['symbol', 'entity_type'])

    def load_data(self):
        """Tải toàn bộ dữ liệu cần thiết từ hệ thống file (Fundamental, OHLCV, Metadata)"""
        logger.info("⏳ Loading data for EV/EBITDA calculation...")
        
        # 1. Load Fundamental Data (COMPANY ONLY for EV/EBITDA)
        entity = 'company'
        file_path = self.base_path / 'DATA' / 'processed' / 'fundamental' / f'{entity}_full.parquet'
        
        if file_path.exists():
            logger.info(f"   Loading {entity} data from {file_path.name}")
            try:
                self.fundamental_data = pd.read_parquet(file_path)
                if 'ENTITY_TYPE' not in self.fundamental_data.columns:
                    self.fundamental_data['ENTITY_TYPE'] = entity.upper()
                if 'REPORT_DATE' in self.fundamental_data.columns:
                    self.fundamental_data['REPORT_DATE'] = pd.to_datetime(self.fundamental_data['REPORT_DATE'])
                
                if 'SECURITY_CODE' in self.fundamental_data.columns:
                    self.fundamental_data.rename(columns={'SECURITY_CODE': 'symbol'}, inplace=True)
                logger.info(f"   Loaded fundamental data: {len(self.fundamental_data):,} records")
            except Exception as e:
                logger.error(f"   Error loading {file_path.name}: {e}")
                raise
        else:
            logger.error(f"❌ File not found: {file_path}")
            raise FileNotFoundError("Company fundamental data file not found.")
            
        # 2. Load OHLCV Data
        if self.ohlcv_path.exists():
            logger.info(f"   Loading OHLCV data from {self.ohlcv_path}")
            self.ohlcv_data = pd.read_parquet(self.ohlcv_path)
            if 'date' in self.ohlcv_data.columns:
                self.ohlcv_data['date'] = pd.to_datetime(self.ohlcv_data['date'])
            logger.info(f"   Loaded {len(self.ohlcv_data):,} OHLCV records")
        else:
            raise FileNotFoundError(f"OHLCV data not found at {self.ohlcv_path}")

        # 3. Load Metadata from Config
        logger.info("🏷️ Loading metadata...")
        metadata_path = self.base_path / 'config' / 'metadata' / 'all_tickers.csv'
        if metadata_path.exists():
            self.metadata = pd.read_csv(metadata_path)
            for _, row in self.metadata.iterrows():
                symbol = row['symbol']
                self.symbol_entity_types[symbol] = str(row.get('entity_type', 'COMPANY')).upper()
        
        # Pre-process và vectorize data
        self._preprocess_data()
    
    def _preprocess_data(self):
        """Tiền xử lý dữ liệu: lọc Debt, Cash, EBITDA components, Minority Interest và Pivot (Sum)"""
        logger.info("⚡ Pre-processing data for optimization...")
        
        # 1. Build Global Code Map using Registry Loader
        code_map = {} # (entity_type, metric_code) -> metric_type
        all_relevant_codes = set()
        
        # Only process COMPANY
        entity = 'COMPANY'
        
        # A. Total Debt (Components)
        debt_comps = self.mapper.get_component_codes('total_debt', entity)
        for code in debt_comps:
            code_map[(entity, code)] = 'total_debt'
            all_relevant_codes.add(code)
        
        # B. EBITDA (Components)
        ebitda_comps = self.mapper.get_component_codes('ebitda', entity)
        for code in ebitda_comps:
            code_map[(entity, code)] = 'ebitda'
            all_relevant_codes.add(code)
            
        # C. Cash
        cash_code = self.mapper.get_metric_code('cash', entity)
        if cash_code:
            code_map[(entity, cash_code)] = 'cash'
            all_relevant_codes.add(cash_code)

        # D. Minority Interest
        min_int_code = self.mapper.get_metric_code('minority_interest', entity)
        if min_int_code:
            code_map[(entity, min_int_code)] = 'minority_interest'
            all_relevant_codes.add(min_int_code)
        
        if 'FREQ_CODE' in self.fundamental_data.columns:
            logger.info("   Filtering for 'Q' frequency...")
            self.fundamental_data = self.fundamental_data[self.fundamental_data['FREQ_CODE'] == 'Q']

        logger.info(f"   Filtering financial data for {len(all_relevant_codes)} distinct metric codes...")
        
        # Filter Data
        fin_data = self.fundamental_data[
            self.fundamental_data['METRIC_CODE'].isin(all_relevant_codes)
        ].copy()
        
        if not fin_data.empty:
            # Apply Mapping
            fin_data['entity_code_pair'] = list(zip(fin_data['ENTITY_TYPE'], fin_data['METRIC_CODE']))
            fin_data['metric_type'] = fin_data['entity_code_pair'].map(code_map)
            
            valid_fin = fin_data.dropna(subset=['metric_type']).copy()
                
            if not valid_fin.empty:
                # Pivot with Sum aggregation
                pivot_df = valid_fin.pivot_table(
                    index=['symbol', 'REPORT_DATE'],
                    columns='metric_type',
                    values='METRIC_VALUE',
                    aggfunc='sum',
                    fill_value=0
                ).reset_index()
                
                # Ensure columns exist
                for col in ['total_debt', 'cash', 'ebitda', 'minority_interest']:
                    if col not in pivot_df.columns:
                        pivot_df[col] = 0.0
                        
                self.raw_financials_df = pivot_df.sort_values(['symbol', 'REPORT_DATE'])
                logger.info(f"   Prepared financial table with {len(self.raw_financials_df):,} records")
            else:
                self.raw_financials_df = pd.DataFrame()
        else:
             self.raw_financials_df = pd.DataFrame()

        # 2. Pre-compute daily market data
        logger.info("   Pre-computing daily market data...")
        self.daily_market_data = self.ohlcv_data.copy()
        self.daily_market_data = self.daily_market_data.sort_values(['symbol', 'date'])
        
        logger.info("✅ Pre-processing completed!")
    
    def calculate_multiple_symbols_ev_ebitda_timeseries(self, symbols: List[str], 
                                                      start_date: datetime, 
                                                      end_date: datetime) -> pd.DataFrame:
        """
        Tính chỉ số EV/EBITDA cho danh sách nhiều mã chứng khoán.
        """
        logger.info(f"🚀 Calculating EV/EBITDA timeseries for {len(symbols)} symbols...")
        
        # Filter only COMPANY symbols
        symbols = [s for s in symbols if self.symbol_entity_types.get(s, 'COMPANY') == 'COMPANY']
        if not symbols:
            logger.warning("No COMPANY symbols found in the list.")
            return pd.DataFrame()

        # 1. Filter Market Data
        market_subset = self.daily_market_data[
            (self.daily_market_data['date'] >= start_date) &
            (self.daily_market_data['date'] <= end_date) &
            (self.daily_market_data['symbol'].isin(symbols))
        ].copy()
        
        if market_subset.empty:
            return pd.DataFrame()
        
        # 2. Prepare Financial Data (TTM for EBITDA, Latest for Debt/Cash)
        if self.raw_financials_df is None or self.raw_financials_df.empty:
            return pd.DataFrame()
        
        fin_subset = self.raw_financials_df[self.raw_financials_df['symbol'].isin(symbols)].copy()
        fin_subset = fin_subset.sort_values(['symbol', 'REPORT_DATE'])
        
        # Calculate TTM for EBITDA
        fin_subset['ebitda_ttm'] = fin_subset.groupby('symbol')['ebitda'].transform(
            lambda x: x.rolling(window=4, min_periods=4).sum()
        )
        
        # Rename for merge
        fin_subset = fin_subset.rename(columns={'REPORT_DATE': 'report_date'})
        
        # 3. Merge Market Data with Financial Data
        # merge_asof requires strict sorting by the 'on' key (date/report_date)
        market_subset = market_subset.sort_values('date')
        fin_subset = fin_subset.sort_values('report_date')
        
        # We need mapping columns: ebitda_ttm, total_debt, cash, minority_interest
        merged_data = pd.merge_asof(
            market_subset,
            fin_subset[['symbol', 'report_date', 'ebitda_ttm', 'total_debt', 'cash', 'minority_interest']],
            left_on='date',
            right_on='report_date',
            by='symbol',
            direction='backward'
        )
        
        # 4. Compute Checks and Metrics
        # EV = Market Cap + Debt + Minority Interest - Cash
        merged_data['ev'] = (merged_data['market_cap'] + 
                             merged_data['total_debt'] + 
                             merged_data['minority_interest'] - 
                             merged_data['cash'])
        
        # EV/EBITDA
        merged_data['ev_ebitda'] = np.where(
            (merged_data['ev'] > 0) & (merged_data['ebitda_ttm'] > 0),
            merged_data['ev'] / merged_data['ebitda_ttm'],
            np.nan
        )
        
        # Add metadata
        merged_data['ev_billion_vnd'] = merged_data['ev'] / 1e9
        merged_data['ebitda_ttm_billion_vnd'] = merged_data['ebitda_ttm'] / 1e9
        merged_data['sector'] = merged_data['symbol'].map(self.symbol_entity_types).fillna('COMPANY')
        
        # Select columns
        result_cols = ['symbol', 'date', 'close', 'ev_billion_vnd', 
                       'ebitda_ttm_billion_vnd', 'ev_ebitda', 'sector']
        
        result_df = merged_data[result_cols].copy()
        result_df = result_df.rename(columns={'close': 'close_price'})
        
        logger.info(f"✅ Calculated EV/EBITDA for {result_df['symbol'].nunique()} symbols")
        return result_df
    
    def save_results(self, df: pd.DataFrame, filename: str = None):
        """Lưu kết quả tính toán vào file định dạng Parquet"""
        if df.empty:
            logger.warning("No data to save")
            return
        
        df = self.date_formatter.standardize_all_date_columns(df.copy())
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            filename = f"ev_ebitda_historical_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
        
        output_file = self.output_path / filename
        df.to_parquet(output_file, index=False)
        logger.info(f"Saved {len(df)} records to {output_file}")

def main():
    """Hàm chạy kiểm thử tính năng (Test function)"""
    logging.basicConfig(level=logging.INFO)
    
    calculator = HistoricalEVEBITDACalculator()
    try:
        calculator.load_data()
    except Exception as e:
        logger.error(str(e))
        return
    
    test_symbols = ['HPG', 'VCB', 'MWG', 'VIC', 'FPT']
    start_date = datetime(2018, 1, 1)
    end_date = datetime.now()
    
    results = calculator.calculate_multiple_symbols_ev_ebitda_timeseries(test_symbols, start_date, end_date)
    if not results.empty:
        print(results.tail())
        calculator.save_results(results, "ev_ebitda_historical_test.parquet")

if __name__ == "__main__":
    main()
