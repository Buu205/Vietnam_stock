#!/usr/bin/env python3
"""
Technical Indicators Update Script
==================================

Script tiện ích để cập nhật technical indicators hàng ngày.

Usage:
    python3 run_technical_update.py [--mode daily|full] [--indicators LIST]

Author: AI Assistant
Date: 2025-10-09
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add technical indicators path
current_dir = Path(__file__).parent
TECH_INDICATORS_PATH = current_dir / "technical" / "technical_indicators"
sys.path.append(str(TECH_INDICATORS_PATH))

try:
    from technical_processor import TechnicalProcessor
    from daily_updater import DailyTechnicalUpdater
except ImportError as e:
    print(f"❌ Error importing technical modules: {e}")
    print(f"💡 Looking in: {TECH_INDICATORS_PATH}")
    print("💡 Make sure you're running from the project root directory")
    sys.exit(1)

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('technical_update.log')
        ]
    )

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Technical Indicators Update')
    parser.add_argument('--mode', choices=['daily', 'full', 'historical'], 
                       default='daily', help='Update mode')
    parser.add_argument('--indicators', nargs='+', 
                       help='Specific indicators to update')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose logging')
    parser.add_argument('--force', action='store_true',
                       help='Force update even if data exists')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    print("🚀 TECHNICAL INDICATORS UPDATE")
    print("=" * 40)
    print(f"📅 Mode: {args.mode}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        if args.mode == 'daily':
            # Daily update mode
            logger.info("Starting daily technical indicators update...")
            
            updater = DailyTechnicalUpdater()
            
            if args.indicators:
                logger.info(f"Updating specific indicators: {args.indicators}")
                # Update specific indicators
                for indicator in args.indicators:
                    logger.info(f"Updating {indicator}...")
                    updater.update_all_indicators()
                print("\n✅ Daily update completed successfully!")
            else:
                logger.info("Updating all indicators...")
                updater.update_all_indicators()
                print("\n✅ Daily update completed successfully!")
                
        elif args.mode == 'full':
            # Full reprocessing mode
            logger.info("Starting full technical indicators reprocessing...")
            
            updater = DailyTechnicalUpdater()
            updater.run_full_reprocess()
            
            print("\n✅ Full reprocessing completed!")
            
        elif args.mode == 'historical':
            # Historical processing mode (full from scratch)
            logger.info("Starting historical technical indicators processing...")
            
            processor = TechnicalProcessor()
            processor.process_all_indicators()
            
            print("\n✅ Historical processing completed!")
        
        # Show summary
        print(f"\n📊 SUMMARY")
        print("-" * 20)
        print(f"Mode: {args.mode}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Log: technical_update.log")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error in technical update: {e}")
        print(f"\n❌ Error: {e}")
        print("🔍 Check technical_update.log for details")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
