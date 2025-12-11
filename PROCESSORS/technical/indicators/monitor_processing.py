#!/usr/bin/env python3
"""
Monitor Historical Technical Processing
======================================

Script để theo dõi tiến trình xử lý historical technical analysis
và kiểm tra kết quả.

Usage:
    python monitor_processing.py [--check-results]

Author: AI Assistant
Date: 2025-01-27
"""

import os
import sys
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
import argparse
import subprocess

def check_process_running():
    """Check if historical processing is still running."""
    try:
        result = subprocess.run(['pgrep', '-f', 'historical_technical_processor.py'], 
                              capture_output=True, text=True)
        return bool(result.stdout.strip())
    except:
        return False

def monitor_log_file():
    """Monitor the processing log file."""
    project_root = Path(__file__).resolve().parents[4]
    log_file = project_root / "historical_technical_processing.log"
    
    if not log_file.exists():
        print("❌ Log file not found")
        return
    
    print("📋 Latest log entries:")
    print("=" * 60)
    
    # Get last 20 lines
    with open(log_file, 'r') as f:
        lines = f.readlines()
        for line in lines[-20:]:
            print(line.strip())

def check_results():
    """Check processing results."""
    project_root = Path(__file__).resolve().parents[4]
    base_path = project_root / "DATA/processed/technical"
    
    print("\n📊 PROCESSING RESULTS SUMMARY")
    print("=" * 60)
    
    indicators = [
        'basic_data', 'moving_averages', 'exponential_moving_averages', 
        'rsi', 'macd', 'bollinger_bands', 'volatility', 'trading_values'
    ]
    
    total_size = 0
    completed_indicators = 0
    
    for indicator in indicators:
        indicator_dir = base_path / indicator
        if indicator_dir.exists():
            full_file = indicator_dir / f"{indicator}_full.parquet"
            
            if full_file.exists():
                completed_indicators += 1
                
                # Get file size
                full_size = full_file.stat().st_size / (1024*1024)
                total_size += full_size
                
                # Get record counts
                try:
                    full_df = pd.read_parquet(full_file)
                    
                    # Get date range
                    date_range = f"{full_df['date'].min()} to {full_df['date'].max()}"
                    symbols_count = full_df['symbol'].nunique()
                    
                    print(f"✅ {indicator:25} | {full_size:6.1f}MB | {len(full_df):>8,} records | {symbols_count:>3} symbols | {date_range}")
                    
                    del full_df  # Free memory
                    
                except Exception as e:
                    print(f"❌ {indicator:25} | {full_size:6.1f}MB | Error reading: {e}")
            else:
                print(f"⏳ {indicator:25} | Processing...")
        else:
            print(f"❌ {indicator:25} | Not found")
    
    # Note: No combined file anymore
    
    print("=" * 60)
    print(f"📈 Progress: {completed_indicators}/{len(indicators)} indicators completed")
    print(f"💾 Total size: {total_size:.1f} MB")
    
    return completed_indicators == len(indicators)

def show_sample_data():
    """Show sample data from completed indicators."""
    project_root = Path(__file__).resolve().parents[4]
    base_path = project_root / "DATA/processed/technical"
    
    # Show sample from moving averages (latest data from full file)
    ma_file = base_path / "moving_averages" / "moving_averages_full.parquet"
    if ma_file.exists():
        print("\n📊 SAMPLE: Moving Averages (Latest data)")
        print("=" * 80)
        
        df = pd.read_parquet(ma_file)
        # Get latest data for sample symbols
        latest_df = df.groupby('symbol').tail(1).reset_index(drop=True)
        sample_df = latest_df[latest_df['symbol'].isin(['VCB', 'HPG', 'VIC', 'VNM', 'FPT'])].copy()
        
        display_cols = ['symbol', 'date', 'close', 'ma20', 'ma50', 'ma_crossover_signal', 'ma_golden_cross', 'ma_death_cross']
        available_cols = [col for col in display_cols if col in sample_df.columns]
        
        if available_cols:
            print(sample_df[available_cols].to_string(index=False))
        else:
            print("No suitable columns found")
    
    # Show sample from EMA (latest data from full file)
    ema_file = base_path / "exponential_moving_averages" / "exponential_moving_averages_full.parquet"
    if ema_file.exists():
        print("\n📊 SAMPLE: EMA Crossovers (Latest data)")
        print("=" * 80)
        
        df = pd.read_parquet(ema_file)
        # Get latest data for sample symbols
        latest_df = df.groupby('symbol').tail(1).reset_index(drop=True)
        sample_df = latest_df[latest_df['symbol'].isin(['VCB', 'HPG', 'VIC', 'VNM', 'FPT'])].copy()
        
        display_cols = ['symbol', 'date', 'close', 'ema9', 'ema21', 'ema_crossover_signal', 'ema_golden_cross', 'ema_death_cross']
        available_cols = [col for col in display_cols if col in sample_df.columns]
        
        if available_cols:
            print(sample_df[available_cols].to_string(index=False))
        else:
            print("No suitable columns found")

def main():
    parser = argparse.ArgumentParser(description='Monitor Historical Technical Processing')
    parser.add_argument('--check-results', action='store_true',
                       help='Check processing results')
    parser.add_argument('--show-sample', action='store_true',
                       help='Show sample data')
    parser.add_argument('--watch', action='store_true',
                       help='Watch processing in real-time')
    
    args = parser.parse_args()
    
    if args.watch:
        print("👀 Watching historical technical processing...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                os.system('clear')  # Clear screen
                print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                if check_process_running():
                    print("🟢 Process is running")
                else:
                    print("🔴 Process not running")
                
                check_results()
                monitor_log_file()
                
                time.sleep(30)  # Update every 30 seconds
                
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
    
    elif args.check_results:
        is_complete = check_results()
        
        if args.show_sample:
            show_sample_data()
        
        if is_complete:
            print("\n🎉 All indicators processing completed!")
        else:
            print("\n⏳ Processing still in progress...")
    
    else:
        # Default: quick status check
        print("🔍 Quick Status Check")
        print("=" * 40)
        
        if check_process_running():
            print("🟢 Process is running")
        else:
            print("🔴 Process not running")
        
        check_results()
        
        print("\nUse --watch to monitor in real-time")
        print("Use --check-results --show-sample to see detailed results")

if __name__ == '__main__':
    main()
