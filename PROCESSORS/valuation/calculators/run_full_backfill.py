
import sys
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime

# Setup Project Root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from PROCESSORS.valuation.calculators.historical_pe_calculator import HistoricalPECalculator
from PROCESSORS.valuation.calculators.historical_pb_calculator import HistoricalPBCalculator
from PROCESSORS.valuation.calculators.historical_ev_ebitda_calculator import HistoricalEVEBITDACalculator
from PROCESSORS.valuation.calculators.vnindex_valuation_calculator import VNIndexValuationCalculator
from PROCESSORS.valuation.calculators.sector_valuation_calculator import SectorValuationCalculator

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('BACKFILL')

def run_full_backfill():
    start_time = datetime.now()
    logger.info("🚀 STARTING FULL BACKFILL FOR ALL VALUATION CALCULATORS")
    
    # Common Dates
    START_DATE = datetime(2018, 1, 1) # User requested 2018+
    END_DATE = datetime.now()
    
    # 1. Historical PE
    try:
        logger.info("\n--- 1. Running Historical PE Calculator ---")
        pe_calc = HistoricalPECalculator()
        pe_calc.load_data()
        symbols = list(pe_calc.symbol_entity_types.keys())
        df_pe = pe_calc.calculate_multiple_symbols_pe_timeseries(symbols, START_DATE, END_DATE)
        
        # Save
        output_pe = pe_calc.output_path / 'historical_pe.parquet'
        df_pe.to_parquet(output_pe)
        logger.info(f"✅ Saved PE data to {output_pe} ({len(df_pe)} rows)")
    except Exception as e:
        logger.error(f"❌ Failed PE Backfill: {e}")

    # 2. Historical PB
    try:
        logger.info("\n--- 2. Running Historical PB Calculator ---")
        pb_calc = HistoricalPBCalculator()
        pb_calc.load_data()
        symbols = list(pb_calc.symbol_entity_types.keys())
        df_pb = pb_calc.calculate_multiple_symbols_pb_timeseries(symbols, START_DATE, END_DATE)
        
        # Save
        output_pb = pb_calc.output_path / 'historical_pb.parquet'
        df_pb.to_parquet(output_pb)
        logger.info(f"✅ Saved PB data to {output_pb} ({len(df_pb)} rows)")
    except Exception as e:
        logger.error(f"❌ Failed PB Backfill: {e}")

    # 3. Historical EV/EBITDA
    try:
        logger.info("\n--- 3. Running Historical EV/EBITDA Calculator ---")
        ev_calc = HistoricalEVEBITDACalculator()
        ev_calc.load_data()
        symbols = list(ev_calc.symbol_entity_types.keys())
        # Filter for COMPANY only
        comp_symbols = [s for s in symbols if ev_calc.symbol_entity_types.get(s, 'COMPANY') == 'COMPANY']
        df_ev = ev_calc.calculate_multiple_symbols_ev_ebitda_timeseries(comp_symbols, START_DATE, END_DATE)
        
        # Save
        output_ev = ev_calc.output_path / 'historical_ev_ebitda.parquet'
        df_ev.to_parquet(output_ev)
        logger.info(f"✅ Saved EV/EBITDA data to {output_ev} ({len(df_ev)} rows)")
    except Exception as e:
        logger.error(f"❌ Failed EV/EBITDA Backfill: {e}")

    # 4. VNINDEX Valuation (Refined)
    try:
        logger.info("\n--- 4. Running VNINDEX Valuation (Refined) ---")
        vn_calc = VNIndexValuationCalculator()
        vn_calc.load_data()
        # Pass Start/End date to respect user request (2018+)
        df_vn = vn_calc.process_all_scopes(start_date=START_DATE, end_date=END_DATE)
        
        # Save (Already handled inside process_all_scopes but ensuring explicit save here if I changed return logic)
        # Wait, I removed the save logic from inside process_all_scopes? 
        # Checking my previous diff... 
        # I removed: "final_df.to_parquet(final_file)" from inside process_all_scopes
        # SO I MUST SAVE IT HERE.
        
        output_vn = vn_calc.output_path / 'vnindex_valuation_refined.parquet'
        if not output_vn.parent.exists(): output_vn.parent.mkdir(parents=True, exist_ok=True)
        df_vn.to_parquet(output_vn)
        logger.info(f"✅ Saved VNINDEX data to {output_vn} ({len(df_vn)} rows)")
        
    except Exception as e:
        logger.error(f"❌ Failed VNINDEX Backfill: {e}")

    # 5. Sector Valuation
    try:
        logger.info("\n--- 5. Running Sector Valuation ---")
        sector_calc = SectorValuationCalculator()
        sector_calc.load_data()
        df_sector = sector_calc.process_all_sectors(start_date=START_DATE, end_date=END_DATE)
        
        output_sector = sector_calc.output_path / 'sector_valuation.parquet'
        if not output_sector.parent.exists(): output_sector.parent.mkdir(parents=True, exist_ok=True)
        df_sector.to_parquet(output_sector)
        logger.info(f"✅ Saved Sector Valuation data to {output_sector} ({len(df_sector)} rows)")
    except Exception as e:
        logger.error(f"❌ Failed Sector Backfill: {e}")

    logger.info(f"\n🎉 ALL BACKFILLS COMPLETED in {datetime.now() - start_time}")

if __name__ == "__main__":
    run_full_backfill()
