"""
Công cụ tính toán P/B Lịch sử - Tính toán chỉ số P/B theo chuỗi thời gian hàng ngày
Đã được tái cấu trúc để sử dụng ValuationMetricMapper và ValuationFormulas
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime, timedelta
import logging
import sys
import warnings

# PROJECT_ROOT = thư mục stock_dashboard (3 cấp trên file hiện tại)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Import DateFormatter từ core theo absolute package path
try:
    from PROCESSORS.core.shared.date_formatter import DateFormatter
except ImportError:
    # Add project root to path for standalone execution
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.append(str(PROJECT_ROOT))
    from PROCESSORS.core.shared.date_formatter import DateFormatter

# Import standardized formulas and mapper
from PROCESSORS.valuation.formulas.valuation_formulas import calculate_pb_ratio, safe_divide
from PROCESSORS.valuation.formulas.metric_mapper import MetricRegistryLoader

from typing import Dict, List, Optional, Tuple

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class HistoricalPBCalculator:
    """
    Tính toán chỉ số P/B (Giá trị sổ sách) theo chuỗi thời gian hàng ngày.
    
    Class này chịu trách nhiệm:
    1. Tải dữ liệu cơ bản (Vốn chủ sở hữu) và dữ liệu thị trường.
    2. Chuẩn hóa và ghép nối dữ liệu bằng Metric Mapper.
    3. Tính toán BPS (Book Value Per Share) và P/B hàng ngày.
    """
    
    METADATA_PATH = PROJECT_ROOT / 'config' / 'metadata' / 'ticker_details.json' # Updated to JSON

    def __init__(self):
        # Dùng PROJECT_ROOT làm gốc: data_warehouse & calculated_results nằm ở root
        self.base_path = PROJECT_ROOT
        self.ohlcv_path = self.base_path / 'DATA' / 'raw' / 'ohlcv' / 'OHLCV_mktcap.parquet'
        self.output_path = self.base_path / 'DATA' / 'processed' / 'valuation' / 'pb' / 'historical'
        
        self.date_formatter = DateFormatter()
        
        # Initialize Smart Mapper
        self.mapper = MetricRegistryLoader()
        self.metadata = self.load_metadata() # Load metadata here
        
        self.symbol_entity_types = {}
        if self.metadata is not None and not self.metadata.empty:
            for _, row in self.metadata.iterrows():
                self.symbol_entity_types[row['symbol']] = str(row.get('entity_type', 'COMPANY')).upper()
        
        # Helper caches
        self.fundamental_data = None
        self.ohlcv_data = None
        
        # Vectorized data structures
        self.raw_equity_df = None
        self.daily_market_data = None
    
    def load_metadata(self):
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
        logger.info("⏳ Loading data for PB calculation...")
        
        # 1. Load Fundamental Data (Split files)
        fundamental_dfs = []
        entity_types = ['company', 'bank', 'insurance', 'security']
        
        for entity in entity_types:
            file_path = self.base_path / 'DATA' / 'processed' / 'fundamental' / f'{entity}_full.parquet'
            if file_path.exists():
                logger.info(f"   Loading {entity} data from {file_path.name}")
                try:
                    df = pd.read_parquet(file_path)
                    # Standardize columns if needed
                    if 'ENTITY_TYPE' not in df.columns:
                        df['ENTITY_TYPE'] = entity.upper()
                    
                    if 'REPORT_DATE' in df.columns:
                        df['REPORT_DATE'] = pd.to_datetime(df['REPORT_DATE'])
                        
                    fundamental_dfs.append(df)
                except Exception as e:
                    logger.error(f"   Error loading {file_path.name}: {e}")
            else:
                logger.warning(f"   ⚠️ File not found: {file_path}")

        if fundamental_dfs:
            self.fundamental_data = pd.concat(fundamental_dfs, ignore_index=True)
            # Standardize column name: SECURITY_CODE -> symbol
            if 'SECURITY_CODE' in self.fundamental_data.columns:
                self.fundamental_data.rename(columns={'SECURITY_CODE': 'symbol'}, inplace=True)
            logger.info(f"   Combined fundamental data: {len(self.fundamental_data):,} records")
        else:
            logger.error("❌ No fundamental data loaded!")
            raise FileNotFoundError("No fundamental data files found.")
            
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
            # Update symbol_entity_types from Metadata
            for _, row in self.metadata.iterrows():
                symbol = row['symbol']
                e_type = str(row.get('entity_type', 'COMPANY')).upper()
                if not self.mapper.validate_entity_type(e_type):
                    e_type = 'COMPANY'
                self.symbol_entity_types[symbol] = e_type
        
        # 4. Shares Outstanding calculation handled in preprocessing using OHLCV data
        
        # Pre-process và vectorize data
        self._preprocess_data()
    
    def _preprocess_data(self):
        """Tiền xử lý và chuẩn bị dữ liệu (Pivot, Vectorization) để tối ưu hóa tốc độ tính toán"""
        logger.info("⚡ Pre-processing data for optimization...")
        
        # 1. Get Equity Codes from Mapper
        # Returns dict: {'COMPANY': 'CBS_80', 'BANK': 'BBS_300', ...}
        # Assuming 'total_equity' is the metric name for Book Value
        equity_codes = self.mapper.get_all_codes_for_metric('total_equity')
        all_valid_codes = set(equity_codes.values())
        
        logger.info("   Creating quarterly equity pivot...")
        if 'FREQ_CODE' in self.fundamental_data.columns:
            logger.info("   Filtering for 'Q' frequency...")
            self.fundamental_data = self.fundamental_data[self.fundamental_data['FREQ_CODE'] == 'Q']

        # Initial filter by valid metric codes and Frequency 'Q'
        equity_data = self.fundamental_data[
            self.fundamental_data['METRIC_CODE'].isin(all_valid_codes)
        ].copy()
        
        if not equity_data.empty:
             # Add expected metric code based on ENTITY_TYPE already in data
            equity_data['expected_metric'] = equity_data['ENTITY_TYPE'].str.upper().map(equity_codes)
            
            # Filter rows where the metric code actually matches the expected one for that entity
            valid_mask = equity_data['METRIC_CODE'] == equity_data['expected_metric']
            equity_df = equity_data[valid_mask][['symbol', 'REPORT_DATE', 'METRIC_VALUE']].copy()
            
            if not equity_df.empty:
                # Remove duplicates
                equity_df = equity_df.groupby(['symbol', 'REPORT_DATE'], as_index=False)['METRIC_VALUE'].first()
                self.raw_equity_df = equity_df.sort_values(['symbol', 'REPORT_DATE'])
                logger.info(f"   Prepared equity data with {len(self.raw_equity_df):,} records")
            else:
                self.raw_equity_df = pd.DataFrame()
        else:
            self.raw_equity_df = pd.DataFrame()
        
        # 2. Pre-compute daily market data
        logger.info("   Pre-computing daily market data...")
        self.daily_market_data = self.ohlcv_data.copy()
        
        # Calculate shares outstanding (prefer market cap derivation)
        self.daily_market_data['shares_outstanding'] = np.where(
            self.daily_market_data['close'] > 0,
            self.daily_market_data['market_cap'] / self.daily_market_data['close'],
            np.nan
        )
        
        self.daily_market_data = self.daily_market_data.sort_values(['symbol', 'date'])
        logger.info("✅ Pre-processing completed!")
    
    def calculate_multiple_symbols_pb_timeseries(self, symbols: List[str], 
                                               start_date: datetime, 
                                               end_date: datetime) -> pd.DataFrame:
        """
        Tính chỉ số P/B cho danh sách nhiều mã chứng khoán (Vector hóa & Tối ưu hóa).
        Sử dụng kỹ thuật pandas merge_asof để ghép nối dữ liệu chuỗi thời gian.
        
        Args:
            symbols (List[str]): Danh sách các mã cổ phiếu cần tính.
            start_date (datetime): Ngày bắt đầu.
            end_date (datetime): Ngày kết thúc.
            
        Returns:
            pd.DataFrame: DataFrame chứa kết quả tính toán.
        """
        logger.info(f"🚀 Calculating PB timeseries for {len(symbols)} symbols...")
        
        # 1. Filter Market Data
        market_subset = self.daily_market_data[
            (self.daily_market_data['date'] >= start_date) &
            (self.daily_market_data['date'] <= end_date) &
            (self.daily_market_data['symbol'].isin(symbols))
        ].copy()
        
        if market_subset.empty:
            logger.warning("No market data found.")
            return pd.DataFrame()

        # 2. Prepare Equity Data
        if self.raw_equity_df is None or self.raw_equity_df.empty:
            return pd.DataFrame()

        equity_subset = self.raw_equity_df[self.raw_equity_df['symbol'].isin(symbols)].copy()
        equity_subset = equity_subset.rename(columns={'REPORT_DATE': 'report_date', 'METRIC_VALUE': 'total_equity_raw'})
        equity_subset = equity_subset.sort_values('report_date')
        
        # 3. Merge Market Data with Equity Data
        # merge_asof requires strict sorting by the 'on' key
        market_subset = market_subset.sort_values('date')
        equity_subset = equity_subset.sort_values('report_date')
        
        merged_data = pd.merge_asof(
            market_subset,
            equity_subset[['symbol', 'report_date', 'total_equity_raw']],
            left_on='date',
            right_on='report_date',
            by='symbol',
            direction='backward'
        )
        
        # 4. Compute Metrics
        # shares_outstanding calculated in preprocess
        
        # Calculate BPS: Total Equity (Raw VND) / Shares
        merged_data['bps'] = merged_data['total_equity_raw'] / merged_data['shares_outstanding']
        
        # Calculate PB: Close Price / BPS
        # Vectorized application
        merged_data['pb_ratio'] = np.where(
            (merged_data['bps'] > 0) & (merged_data['close'] > 0),
            merged_data['close'] / merged_data['bps'],
            np.nan
        )
        
        # Add metadata
        merged_data['equity_billion_vnd'] = merged_data['total_equity_raw'] / 1e9
        merged_data['sector'] = merged_data['symbol'].map(self.symbol_entity_types).fillna('COMPANY')
        
        # Final formatting
        result_cols = ['symbol', 'date', 'close', 'equity_billion_vnd', 
                       'shares_outstanding', 'bps', 'pb_ratio', 'sector']
        
        result_df = merged_data[result_cols].copy()
        result_df = result_df.rename(columns={'close': 'close_price'})
        
        logger.info(f"✅ Calculated PB for {result_df['symbol'].nunique()} symbols")
        return result_df
    
    def save_results(self, df: pd.DataFrame, filename: str = None):
        """Lưu kết quả tính toán vào file định dạng Parquet"""
        if df.empty:
            logger.warning("No data to save")
            return
        
        # Standardize dates
        df = self.date_formatter.standardize_all_date_columns(df.copy())
        
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            filename = f"pb_historical_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
        
        output_file = self.output_path / filename
        df.to_parquet(output_file, index=False)
        logger.info(f"Saved {len(df)} records to {output_file}")

def main():
    """Hàm chạy kiểm thử tính năng (Test function)"""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    calculator = HistoricalPBCalculator()
    try:
        calculator.load_data()
    except Exception as e:
        logger.error(str(e))
        return
    
    test_symbols = ['HPG', 'VCB', 'MWG', 'VIC', 'FPT']
    start_date = datetime(2018, 1, 1)
    end_date = datetime.now()
    
    results = calculator.calculate_multiple_symbols_pb_timeseries(test_symbols, start_date, end_date)
    if not results.empty:
        print(results.tail())
        calculator.save_results(results, "pb_historical_test.parquet")

if __name__ == "__main__":
    main()
