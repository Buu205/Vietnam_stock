
import sys
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime, timedelta

# Setup Project Root
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # daily/pipelines/PROCESSORS is 3 levels deep
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Import Calculators
from PROCESSORS.valuation.calculators.historical_pe_calculator import HistoricalPECalculator
from PROCESSORS.valuation.calculators.historical_pb_calculator import HistoricalPBCalculator
from PROCESSORS.valuation.calculators.historical_ev_ebitda_calculator import HistoricalEVEBITDACalculator
from PROCESSORS.valuation.calculators.vnindex_valuation_calculator import VNIndexValuationCalculator
# Note: Sector valuation is now handled by PROCESSORS/sector/run_sector_analysis.py --ta-only

# Logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - DAILY_UPDATE - %(levelname)s - %(message)s')
logger = logging.getLogger('DAILY_UPDATE')

def get_next_date(parquet_path):
    """
    Check existing parquet file for the latest date.
    Returns: (next_start_date, is_new_file)
    """
    if not parquet_path.exists():
        return datetime(2018, 1, 1), True
    
    try:
        # Read only the 'date' column to be fast
        df = pd.read_parquet(parquet_path, columns=['date'])
        if df.empty:
            return datetime(2018, 1, 1), True
            
        max_date = pd.to_datetime(df['date']).max()
        return max_date + timedelta(days=1), False
    except Exception as e:
        logger.warning(f"Error reading date from {parquet_path}: {e}. Starting from scratch.")
        return datetime(2015, 1, 1), True

def update_calculator(calc_class, output_name, calc_method_name, scope_logic=None):
    """
    Generic update function for symbol-based calculators.
    """
    try:
        # Initialize
        calc = calc_class()
        # Output Path
        output_path = calc.output_path / output_name
        
        # Determine Date Range
        start_date, is_new_file = get_next_date(output_path)
        end_date = datetime.now()
        
        # Check if update needed
        if start_date > end_date:
            logger.info(f"✅ {output_name} is up to date (Latest: {start_date - timedelta(days=1)}). Skipping.")
            return

        logger.info(f"🔄 Updating {output_name} from {start_date.date()} to {end_date.date()}...")
        
        # Load Data
        calc.load_data()
        
        # Logic specific to calculator type
        if scope_logic == 'VNINDEX':
            # VNIndex Calculator uses a different method signature (process_all_scopes)
            # which I modified to accept start_date, end_date
            new_data = calc.process_all_scopes(start_date=start_date, end_date=end_date)
            
        elif scope_logic == 'SECTOR':
            new_data = calc.process_all_sectors(start_date=start_date, end_date=end_date)
        
        else:
            # Symbol-based calculators
            symbols = list(calc.symbol_entity_types.keys())
            
            # Filter for EV/EBITDA (Company only)
            if 'EVEBITDA' in str(calc_class):
                symbols = [s for s in symbols if calc.symbol_entity_types.get(s, 'COMPANY') == 'COMPANY']
            
            # Call method dynamically
            method = getattr(calc, calc_method_name)
            new_data = method(symbols, start_date, end_date)

        # Save Result
        if new_data is not None and not new_data.empty:
            if is_new_file:
                # Create parent dir if needed
                if not output_path.parent.exists(): output_path.parent.mkdir(parents=True, exist_ok=True)
                new_data.to_parquet(output_path)
                logger.info(f"📝 Created new file {output_path} with {len(new_data)} rows.")
            else:
                # Append
                existing_df = pd.read_parquet(output_path)
                combined_df = pd.concat([existing_df, new_data], ignore_index=True)
                # Deduplicate by sorting and keeping last (just in case of overlap)
                if 'scope' in combined_df.columns:
                     combined_df = combined_df.drop_duplicates(subset=['date', 'scope'], keep='last')
                     combined_df = combined_df.sort_values(['scope', 'date'])
                else:
                     if 'symbol' in combined_df.columns:
                        combined_df = combined_df.drop_duplicates(subset=['date', 'symbol'], keep='last')
                        combined_df = combined_df.sort_values(['symbol', 'date'])
                     else:
                        combined_df = combined_df.sort_values('date')
                        
                combined_df.to_parquet(output_path)
                logger.info(f"📝 Appended {len(new_data)} rows to {output_path}. Total: {len(combined_df)}")
        else:
            logger.warning(f"⚠️ No new data found for {output_name} in range.")

    except Exception as e:
        logger.error(f"❌ Failed to update {output_name}: {e}")
        import traceback
        traceback.print_exc()

def print_summary():
    """Print summary of all valuation data files."""
    data_path = PROJECT_ROOT / "DATA" / "processed" / "valuation"
    logger.info("\n" + "=" * 70)
    logger.info("📊 VALUATION DATA SUMMARY")
    logger.info("=" * 70)

    files_to_check = [
        ("PE", data_path / "pe" / "historical" / "historical_pe.parquet"),
        ("PB", data_path / "pb" / "historical" / "historical_pb.parquet"),
        ("EV/EBITDA", data_path / "ev_ebitda" / "historical" / "historical_ev_ebitda.parquet"),
        ("VNINDEX", data_path / "vnindex" / "vnindex_valuation_refined.parquet"),
    ]

    for name, path in files_to_check:
        if path.exists():
            try:
                df = pd.read_parquet(path)
                latest = pd.to_datetime(df['date']).max()
                symbols = df['symbol'].nunique() if 'symbol' in df.columns else '-'
                logger.info(f"  {name:12} | {len(df):>10,} rows | {symbols:>5} tickers | Latest: {latest.strftime('%Y-%m-%d')}")
            except Exception as e:
                logger.warning(f"  {name:12} | Error reading: {e}")
        else:
            logger.warning(f"  {name:12} | File not found")

    logger.info("=" * 70)

def run_daily_update():
    start_time = datetime.now()
    logger.info("🚀 STARTING DAILY VALUATION UPDATE script")
    logger.info(f"   Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("   Updating: Individual stock PE/PB/EV_EBITDA + VNINDEX valuation")
    logger.info("")

    # 1. Historical PE
    logger.info("\n--- 1/4 Historical PE ---")
    update_calculator(HistoricalPECalculator, 'historical_pe.parquet', 'calculate_multiple_symbols_pe_timeseries')

    # 2. Historical PB
    logger.info("\n--- 2/4 Historical PB ---")
    update_calculator(HistoricalPBCalculator, 'historical_pb.parquet', 'calculate_multiple_symbols_pb_timeseries')

    # 3. Historical EV/EBITDA
    logger.info("\n--- 3/4 Historical EV/EBITDA ---")
    update_calculator(HistoricalEVEBITDACalculator, 'historical_ev_ebitda.parquet', 'calculate_multiple_symbols_ev_ebitda_timeseries')

    # 4. VNINDEX Valuation
    logger.info("\n--- 4/4 VNINDEX Valuation ---")
    update_calculator(VNIndexValuationCalculator, 'vnindex_valuation_refined.parquet', 'process_all_scopes', scope_logic='VNINDEX')

    # Print summary
    print_summary()

    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"\n🎉 DAILY VALUATION UPDATE COMPLETED in {elapsed:.1f}s")
    logger.info("ℹ️  For sector valuation (PE/PB/PS/EV_EBITDA), run: python3 PROCESSORS/sector/run_sector_analysis.py --ta-only")

if __name__ == "__main__":
    run_daily_update()
