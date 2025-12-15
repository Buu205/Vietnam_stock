#!/usr/bin/env python3
"""
Daily Macro & Commodity Update Pipeline
=======================================
Updates Unified Macro & Commodity Data.
Supports incremental updates and full migration.

Usage:
    python daily_macro_commodity_update.py [--migrate]
"""

import sys
import logging
import argparse
import shutil
from pathlib import Path
from datetime import datetime, date
import pandas as pd

# Path Setup
PROCESSORS_DIR = Path(__file__).resolve().parent.parent  # pipelines is 2 levels deep (pipelines -> PROCESSORS)
PROJECT_ROOT = PROCESSORS_DIR.parent  # PROCESSORS -> Vietnam_dashboard
sys.path.insert(0, str(PROJECT_ROOT))

from PROCESSORS.technical.macro_commodity.macro_commodity_fetcher import MacroCommodityFetcher

# Paths
DATA_DIR = PROJECT_ROOT / "DATA"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
TARGET_DIR = PROCESSED_DIR / "macro_commodity"
TARGET_FILE = TARGET_DIR / "macro_commodity_unified.parquet"

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("UnifiedUpdate")

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def cleanup_old_folders():
    """Delete old separate macro/commodity folders."""
    paths_to_remove = [
        PROCESSED_DIR / "commodity",
        PROCESSED_DIR / "macro",
        RAW_DIR / "commodity",
        RAW_DIR / "macro",
        PROCESSORS_DIR / "technical" / "commodity",
        PROCESSORS_DIR / "technical" / "macro"
    ]
    
    logger.info("🧹 Starting cleanup of old folders...")
    for p in paths_to_remove:
        if p.exists():
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
                logger.info(f"✅ Removed: {p}")
            except Exception as e:
                logger.error(f"❌ Failed to remove {p}: {e}")
        else:
            logger.info(f"skipped (not found): {p}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--migrate", action="store_true", help="Run full migration from 2015 and cleanup old folders")
    args = parser.parse_args()
    
    ensure_dir(TARGET_DIR)
    
    fetcher = MacroCommodityFetcher()
    
    if args.migrate:
        logger.info("🚀 STARTING FULL MIGRATION (Start Date: 2015-01-01)")
        start_date = '2015-01-01'
        
        # 1. Fetch All
        df_new = fetcher.fetch_all(start_date)
        if df_new.empty:
            logger.error("❌ Migration failed: No data fetched.")
            return
            
        # 2. Save
        # Ensure date is datetime for parquet
        df_new['date'] = pd.to_datetime(df_new['date'])
        df_new.to_parquet(TARGET_FILE, index=False)
        logger.info(f"✅ Migration Saved: {len(df_new)} records to {TARGET_FILE}")
        
        # 3. Cleanup
        cleanup_old_folders()
        logger.info("🎉 MIGRATION COMPLETED SUCCESSFULLY")
        
    else:
        logger.info("🔄 STARTING DAILY UPDATE")
        # Incremental logic: Fetch last 30 days to ensure coverage
        start_date = (date.today() - pd.Timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 1. Fetch New Data
        df_new = fetcher.fetch_all(start_date)
        if df_new.empty:
            logger.warning("⚠️ No new data fetched.")
            return

        # 2. Load Existing
        if TARGET_FILE.exists():
            df_old = pd.read_parquet(TARGET_FILE)
            logger.info(f"Loaded existing: {len(df_old)} records")
        else:
            df_old = pd.DataFrame()
            
        # 3. Merge
        if not df_old.empty:
            # Normalize date column types
            df_new['date'] = pd.to_datetime(df_new['date'])
            df_old['date'] = pd.to_datetime(df_old['date'])
            
            combined = pd.concat([df_old, df_new], ignore_index=True)
            # Dedup based on date + symbol + category, keep last (newest)
            combined = combined.drop_duplicates(subset=['date', 'symbol', 'category'], keep='last')
        else:
            combined = df_new
            
        combined = combined.sort_values(['category', 'symbol', 'date']).reset_index(drop=True)
        
        # 4. Save
        combined.to_parquet(TARGET_FILE, index=False)
        logger.info(f"✅ Update Completed. Total records: {len(combined)}")

if __name__ == "__main__":
    main()
