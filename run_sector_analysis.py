
#!/usr/bin/env python3
"""
Run Sector Analysis Pipeline
============================
This script triggers the sector-level aggregation for both 
Fundamental (FA) and Valuation (TA) metrics.

Outputs:
- DATA/processed/sector/sector_fundamental_metrics.parquet
- DATA/processed/sector/sector_valuation_metrics.parquet
"""

import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from PROCESSORS.sector.sector_processor import SectorProcessor

def main():
    print("Starting Sector Analysis Job...")
    try:
        processor = SectorProcessor()
        processor.process_all_sectors()
        print("Job Completed Successfully.")
    except Exception as e:
        print(f"Job Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
