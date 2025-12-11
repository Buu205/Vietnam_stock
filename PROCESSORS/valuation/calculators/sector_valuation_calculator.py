
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Import Parent Class
from PROCESSORS.valuation.calculators.vnindex_valuation_calculator import VNIndexValuationCalculator

logger = logging.getLogger(__name__)

class SectorValuationCalculator(VNIndexValuationCalculator):
    """
    Calculates PE & PB for each Sector (Market Cap Weighted).
    Inherits from VNIndexValuationCalculator to reuse efficient TTM Earnings/Equity & OHLCV processing logic.
    """
    
    def __init__(self):
        super().__init__()
        # Override output path for Sector Valuation
        self.output_path = self.base_path / 'DATA' / 'processed' / 'valuation' / 'sector_pe'
        
        # Sector Mapping: Symbol -> Sector
        self.sector_map = {}
        if self.metadata is not None and not self.metadata.empty:
            # Check if 'sector' column exists
            if 'sector' in self.metadata.columns:
                # Create map, filter out null sectors
                valid_sectors = self.metadata.dropna(subset=['sector'])
                self.sector_map = dict(zip(valid_sectors['symbol'], valid_sectors['sector']))
            else:
                logger.error("❌ Metadata does not contain 'sector' column!")

    def get_sectors(self) -> List[str]:
        """Get list of unique sectors."""
        if not self.sector_map:
            return []
        return sorted(list(set(self.sector_map.values())))

    def get_symbols_for_sector(self, sector_name: str) -> List[str]:
        """Get list of symbols for a specific sector."""
        return [sym for sym, sec in self.sector_map.items() if sec == sector_name]

    def process_all_sectors(self, start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
        """
        Calculate valuation for ALL keys in sector_map.
        Returns: concatenated DataFrame with 'scope' column = sector_name.
        """
        sectors = self.get_sectors()
        logger.info(f"🚀 Starting Sector Valuation for {len(sectors)} sectors...")
        
        all_results = []
        
        for i, sector in enumerate(sectors):
            # Get symbols
            symbols = self.get_symbols_for_sector(sector)
            if not symbols:
                continue
                
            logger.info(f"   ({i+1}/{len(sectors)}) Processing Sector: {sector} ({len(symbols)} symbols)")
            
            # Reuse Parent Logic: calculate_scope_valuation
            # This handles: Filtering OHLCV, Merging Financials, Aggregation (Sum MC / Sum Earnings)
            df_sector = self.calculate_scope_valuation(
                scope_name=sector, 
                subset_symbols=symbols, 
                start_date=start_date, 
                end_date=end_date
            )
            
            if not df_sector.empty:
                all_results.append(df_sector)
        
        # Combine
        if all_results:
            final_df = pd.concat(all_results, ignore_index=True)
            final_df = final_df.sort_values(['scope', 'date'])
        else:
            final_df = pd.DataFrame()

        # Save
        if not self.output_path.exists():
            self.output_path.mkdir(parents=True, exist_ok=True)
            
        final_file = self.output_path / 'sector_valuation.parquet'
        
        # If incremental (start_date provided), we might want to append?
        # Ideally, the caller handles appending (like in run_daily_valuation_update.py). 
        # But here valid_scope logic is simpler. 
        # I will let run_daily_update handle persistence if incremental.
        # But for full run/adhoc, I save here.
        
        if start_date is None: # Full run
            final_df.to_parquet(final_file)
            logger.info(f"✅ Saved Sector Valuation data to {final_file}")
            
        return final_df
