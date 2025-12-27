#!/usr/bin/env python3
"""
Master Daily Update Script
===========================

Chạy toàn bộ daily updates theo đúng thứ tự.
Runs all daily updates in correct order.

Pipeline Order:
1. OHLCV (raw market data)
2. Technical Analysis (TA indicators, alerts, breadth)
3. Macro & Commodity (economic data)
4. Stock Valuation (PE/PB/EV-EBITDA)
5. Sector Analysis (sector metrics & scoring)

Usage:
    # Run all daily updates
    python3 PROCESSORS/pipelines/run_all_daily_updates.py

    # Skip specific updates
    python3 PROCESSORS/pipelines/run_all_daily_updates.py --skip-ohlcv

    # Run only one update
    python3 PROCESSORS/pipelines/run_all_daily_updates.py --only ta

Author: Claude Code
Date: 2025-12-15
Version: 2.0.0 (Enhanced with progress tracking & file verification)
"""

import sys
import subprocess
from pathlib import Path
import argparse
import logging
from datetime import datetime
from typing import Dict, Tuple, Optional
import pandas as pd

PIPELINES_DIR = Path(__file__).parent
DAILY_DIR = PIPELINES_DIR / "daily"  # Daily scripts subfolder
PROJECT_ROOT = PIPELINES_DIR.parent.parent
LOG_DIR = PROJECT_ROOT / "logs"

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging - both console and file
log_filename = LOG_DIR / f"daily_update_{datetime.now().strftime('%Y%m%d')}.log"

# Create formatter
formatter = logging.Formatter('%(asctime)s - MASTER - %(levelname)s - %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# File handler (append mode so multiple runs on same day are captured)
file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Root logger
logger = logging.getLogger('MASTER')
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    else:
        return f"{seconds/60:.1f}m ({seconds:.0f}s)"


def show_data_integrity_report():
    """Show final data integrity report - can be called independently."""
    logger.info("\n" + "=" * 80)
    logger.info("📋 FINAL DATA INTEGRITY REPORT")
    logger.info("=" * 80)
    logger.info(f"{'Data Source':<22} | {'Latest':<12} | {'Tickers':<8} | {'Records':<12} | Status")
    logger.info("-" * 80)

    today_str = datetime.now().strftime('%Y-%m-%d')
    data_checks = [
        ("OHLCV (Source)", "DATA/raw/ohlcv/OHLCV_mktcap.parquet", "date", "symbol"),
        ("Technical (TA)", "DATA/processed/technical/basic_data.parquet", "date", "symbol"),
        ("RS Rating", "DATA/processed/technical/rs_rating/stock_rs_rating_daily.parquet", "date", "symbol"),
        ("Market Breadth", "DATA/processed/technical/market_breadth/market_breadth_daily.parquet", "date", None),
        ("PE Ratio", "DATA/processed/valuation/pe/historical/historical_pe.parquet", "date", "symbol"),
        ("PB Ratio", "DATA/processed/valuation/pb/historical/historical_pb.parquet", "date", "symbol"),
        ("P/S Ratio", "DATA/processed/valuation/ps/historical/historical_ps.parquet", "date", "symbol"),
        ("EV/EBITDA", "DATA/processed/valuation/ev_ebitda/historical/historical_ev_ebitda.parquet", "date", "symbol"),
        ("VN-Index Val", "DATA/processed/valuation/vnindex/vnindex_valuation_refined.parquet", "date", None),
        ("Macro/Commodity", "DATA/processed/macro_commodity/macro_commodity_unified.parquet", "date", None),
        ("Sector Valuation", "DATA/processed/sector/sector_valuation_metrics.parquet", "date", "sector"),
    ]

    all_data_ok = True
    for name, rel_path, date_col, group_col in data_checks:
        file_path = PROJECT_ROOT / rel_path
        try:
            if file_path.exists():
                df = pd.read_parquet(file_path)
                latest = pd.to_datetime(df[date_col]).max().strftime('%Y-%m-%d')

                if group_col and group_col in df.columns:
                    tickers = str(df[group_col].nunique())
                else:
                    tickers = "-"

                records = f"{len(df):,}"
                status = "✅" if latest == today_str else "⚠️"
                if latest != today_str:
                    all_data_ok = False

                logger.info(f"{name:<22} | {latest:<12} | {tickers:<8} | {records:<12} | {status}")
            else:
                logger.info(f"{name:<22} | {'NOT FOUND':<12} | {'-':<8} | {'-':<12} | ❌")
                all_data_ok = False
        except Exception as e:
            logger.info(f"{name:<22} | {'ERROR':<12} | {'-':<8} | {'-':<12} | ❌")
            all_data_ok = False

    logger.info("-" * 80)

    if all_data_ok:
        logger.info("🎯 DATA STATUS: ✅ ALL DATA UP TO DATE")
    else:
        logger.info("🎯 DATA STATUS: ⚠️ SOME DATA MAY BE OUTDATED")

    logger.info("=" * 80)
    logger.info(f"📝 Log file: {log_filename}")
    logger.info("=" * 80)

    return all_data_ok


def check_output_files(step_key: str) -> Dict[str, any]:
    """
    Check output files for each step and return summary.

    Args:
        step_key: Key identifying the pipeline step (ohlcv, ta, macro, valuation, sector)

    Returns:
        Dictionary with file info (path, size, records, latest_date, etc.)
    """
    data_dir = PROJECT_ROOT / "DATA"
    info = {"files": [], "total_size_mb": 0, "status": "unknown"}

    try:
        if step_key == "ohlcv":
            # Check OHLCV file
            file_path = data_dir / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"
            if file_path.exists():
                df = pd.read_parquet(file_path)
                size_mb = file_path.stat().st_size / (1024 * 1024)
                latest_date = pd.to_datetime(df['date']).max()
                # Handle both 'symbol' and 'ticker' column names
                symbol_col = 'symbol' if 'symbol' in df.columns else 'ticker'
                symbols = df[symbol_col].nunique() if symbol_col in df.columns else 0

                info["files"].append({
                    "path": str(file_path.relative_to(PROJECT_ROOT)),
                    "size_mb": size_mb,
                    "records": len(df),
                    "symbols": symbols,
                    "latest_date": latest_date.strftime('%Y-%m-%d') if pd.notna(latest_date) else "N/A"
                })
                info["total_size_mb"] = size_mb
                info["status"] = "ok"

        elif step_key == "ta":
            # Check main TA files (including RS Rating for TA Dashboard)
            files_to_check = [
                data_dir / "processed" / "technical" / "basic_data.parquet",
                data_dir / "processed" / "technical" / "vnindex" / "vnindex_analysis.parquet",
                data_dir / "processed" / "technical" / "market_breadth" / "market_breadth_daily.parquet",
                data_dir / "processed" / "technical" / "rs_rating" / "stock_rs_rating_daily.parquet",
                data_dir / "processed" / "technical" / "sector_breadth" / "sector_breadth_daily.parquet",
            ]

            for file_path in files_to_check:
                if file_path.exists():
                    df = pd.read_parquet(file_path)
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    latest_date = pd.to_datetime(df['date']).max() if 'date' in df.columns else None

                    info["files"].append({
                        "path": str(file_path.relative_to(PROJECT_ROOT)),
                        "size_mb": size_mb,
                        "records": len(df),
                        "latest_date": latest_date.strftime('%Y-%m-%d') if pd.notna(latest_date) else "N/A"
                    })
                    info["total_size_mb"] += size_mb

            info["status"] = "ok" if info["files"] else "no_files"

        elif step_key == "macro":
            # Check macro/commodity file
            file_path = data_dir / "processed" / "macro_commodity" / "macro_commodity_unified.parquet"
            if file_path.exists():
                df = pd.read_parquet(file_path)
                size_mb = file_path.stat().st_size / (1024 * 1024)
                latest_date = pd.to_datetime(df['date']).max()
                categories = df['category'].nunique()

                info["files"].append({
                    "path": str(file_path.relative_to(PROJECT_ROOT)),
                    "size_mb": size_mb,
                    "records": len(df),
                    "categories": categories,
                    "latest_date": latest_date.strftime('%Y-%m-%d') if pd.notna(latest_date) else "N/A"
                })
                info["total_size_mb"] = size_mb
                info["status"] = "ok"

        elif step_key == "valuation":
            # Check valuation files
            files_to_check = [
                data_dir / "processed" / "valuation" / "pe" / "historical" / "historical_pe.parquet",
                data_dir / "processed" / "valuation" / "pb" / "historical" / "historical_pb.parquet",
                data_dir / "processed" / "valuation" / "ps" / "historical" / "historical_ps.parquet",
                data_dir / "processed" / "valuation" / "ev_ebitda" / "historical" / "historical_ev_ebitda.parquet",
                data_dir / "processed" / "valuation" / "vnindex" / "vnindex_valuation_refined.parquet",
            ]

            for file_path in files_to_check:
                if file_path.exists():
                    df = pd.read_parquet(file_path)
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    latest_date = pd.to_datetime(df['date']).max()

                    info["files"].append({
                        "path": str(file_path.relative_to(PROJECT_ROOT)),
                        "size_mb": size_mb,
                        "records": len(df),
                        "latest_date": latest_date.strftime('%Y-%m-%d') if pd.notna(latest_date) else "N/A"
                    })
                    info["total_size_mb"] += size_mb

            info["status"] = "ok" if info["files"] else "no_files"

        elif step_key == "sector":
            # Check sector files
            files_to_check = [
                data_dir / "processed" / "sector" / "sector_fundamental_metrics.parquet",
                data_dir / "processed" / "sector" / "sector_valuation_metrics.parquet",
                data_dir / "processed" / "sector" / "sector_combined_scores.parquet",
            ]

            for file_path in files_to_check:
                if file_path.exists():
                    df = pd.read_parquet(file_path)
                    size_mb = file_path.stat().st_size / (1024 * 1024)

                    # Get latest date (different column names for different files)
                    latest_date = None
                    if 'report_date' in df.columns:
                        latest_date = pd.to_datetime(df['report_date']).max()
                    elif 'date' in df.columns:
                        latest_date = pd.to_datetime(df['date']).max()

                    file_info = {
                        "path": str(file_path.relative_to(PROJECT_ROOT)),
                        "size_mb": size_mb,
                        "records": len(df),
                        "sectors": df['sector_code'].nunique() if 'sector_code' in df.columns else 0,
                        "latest_date": latest_date.strftime('%Y-%m-%d') if pd.notna(latest_date) else "N/A"
                    }

                    # Add signal distribution for combined scores
                    if 'signal' in df.columns:
                        signals = df['signal'].value_counts().to_dict()
                        file_info['signals'] = signals

                    info["files"].append(file_info)
                    info["total_size_mb"] += size_mb

            info["status"] = "ok" if info["files"] else "no_files"

        elif step_key == "bscforecast":
            # Check BSC forecast files
            files_to_check = [
                data_dir / "processed" / "forecast" / "bsc" / "bsc_individual.parquet",
                data_dir / "processed" / "forecast" / "bsc" / "bsc_sector_valuation.parquet",
                data_dir / "processed" / "forecast" / "bsc" / "bsc_combined.parquet",
            ]

            for file_path in files_to_check:
                if file_path.exists():
                    df = pd.read_parquet(file_path)
                    size_mb = file_path.stat().st_size / (1024 * 1024)

                    # Get updated_at timestamp
                    latest_date = None
                    if 'updated_at' in df.columns:
                        latest_date = pd.to_datetime(df['updated_at']).max()

                    file_info = {
                        "path": str(file_path.relative_to(PROJECT_ROOT)),
                        "size_mb": size_mb,
                        "records": len(df),
                        "latest_date": latest_date.strftime('%Y-%m-%d') if pd.notna(latest_date) else "N/A"
                    }

                    # Add rating distribution for individual file
                    if 'rating' in df.columns:
                        ratings = df['rating'].value_counts().to_dict()
                        file_info['ratings'] = ratings

                    info["files"].append(file_info)
                    info["total_size_mb"] += size_mb

            info["status"] = "ok" if info["files"] else "no_files"

    except Exception as e:
        logger.warning(f"Could not check output files for {step_key}: {e}")
        info["status"] = "error"
        info["error"] = str(e)

    return info


def display_file_info(step_key: str, file_info: Dict):
    """Display file information in a nice format."""
    if file_info["status"] != "ok":
        logger.warning(f"   ⚠️  Output verification: {file_info['status']}")
        return

    logger.info(f"\n   📁 Output Files ({file_info['total_size_mb']:.1f} MB total):")

    for file_data in file_info["files"]:
        path_short = file_data["path"].split("/")[-1]  # Just filename
        logger.info(f"      • {path_short}")
        logger.info(f"        └─ {file_data['records']:,} records | {file_data['size_mb']:.2f} MB | Latest: {file_data['latest_date']}")

        # Additional info per step
        if step_key == "ohlcv" and "symbols" in file_data:
            logger.info(f"        └─ {file_data['symbols']} symbols")

        if step_key == "macro" and "categories" in file_data:
            logger.info(f"        └─ {file_data['categories']} categories")

        if step_key == "sector" and "sectors" in file_data:
            logger.info(f"        └─ {file_data['sectors']} sectors")
            if "signals" in file_data:
                signals_str = ", ".join([f"{k}: {v}" for k, v in file_data["signals"].items()])
                logger.info(f"        └─ Signals: {signals_str}")

        if step_key == "bscforecast" and "ratings" in file_data:
            ratings_str = ", ".join([f"{k}: {v}" for k, v in file_data["ratings"].items()])
            logger.info(f"        └─ Ratings: {ratings_str}")


def run_script(
    script_name: str,
    description: str,
    step_num: int,
    total_steps: int,
    step_key: str
) -> Tuple[bool, float, Optional[Dict]]:
    """
    Run a daily script and return success status, duration, and file info.

    Args:
        script_name: Name of the script file
        description: Human-readable description
        step_num: Current step number
        total_steps: Total number of steps
        step_key: Step key for file verification

    Returns:
        Tuple of (success, duration_seconds, file_info)
    """
    script_path = DAILY_DIR / script_name

    logger.info("\n" + "=" * 80)
    logger.info(f"🚀 STEP {step_num}/{total_steps}: {description}")
    logger.info(f"   Script: {script_name}")
    logger.info("=" * 80)

    start_time = datetime.now()

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        duration = (datetime.now() - start_time).total_seconds()

        if result.returncode == 0:
            logger.info(f"\n✅ SUCCESS: {description}")
            logger.info(f"   Duration: {format_duration(duration)}")

            # Check output files
            file_info = check_output_files(step_key)
            display_file_info(step_key, file_info)

            logger.info("")
            return True, duration, file_info
        else:
            logger.error(f"\n❌ FAILED: {description}")
            logger.error(f"   Exit code: {result.returncode}")
            logger.error(f"   Duration: {format_duration(duration)}")
            if result.stderr:
                # Show last 20 lines of error
                stderr_lines = result.stderr.strip().split('\n')
                logger.error(f"   Error output (last 20 lines):")
                for line in stderr_lines[-20:]:
                    logger.error(f"     {line}")
            logger.info("")
            return False, duration, None

    except subprocess.TimeoutExpired:
        duration = 600.0
        logger.error(f"\n❌ TIMEOUT: {description} exceeded 10 minutes")
        logger.info("")
        return False, duration, None
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"\n❌ ERROR: {description} - {str(e)}")
        logger.info("")
        return False, duration, None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run all daily updates in correct order',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Pipeline Order:
  1. OHLCV → 2. TA → 3. Macro → 4. Stock Valuation → 5. Sector Analysis

Examples:
  # Run all updates
  python3 PROCESSORS/pipelines/run_all_daily_updates.py

  # Skip OHLCV and TA
  python3 PROCESSORS/pipelines/run_all_daily_updates.py --skip-ohlcv --skip-ta

  # Run only valuation
  python3 PROCESSORS/pipelines/run_all_daily_updates.py --only valuation
        """
    )

    parser.add_argument('--skip-ohlcv', action='store_true', help='Skip OHLCV update')
    parser.add_argument('--skip-ta', action='store_true', help='Skip TA update')
    parser.add_argument('--skip-macro', action='store_true', help='Skip macro/commodity')
    parser.add_argument('--skip-valuation', action='store_true', help='Skip stock valuation')
    parser.add_argument('--skip-sector', action='store_true', help='Skip sector analysis')
    parser.add_argument('--skip-bscforecast', action='store_true', help='Skip BSC forecast update')
    parser.add_argument('--only', choices=['ohlcv', 'ta', 'macro', 'valuation', 'sector', 'bscforecast'],
                       help='Run only specified update')

    args = parser.parse_args()

    pipeline_start = datetime.now()
    results = {}
    durations = {}
    file_infos = {}

    logger.info("\n" + "=" * 80)
    logger.info("🚀 MASTER DAILY UPDATE PIPELINE - STARTED")
    logger.info(f"   Time: {pipeline_start.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    # Define pipeline (order matters!)
    pipeline = [
        ('daily_ohlcv_update.py', 'OHLCV Data Update', 'ohlcv', args.skip_ohlcv),
        ('daily_ta_complete.py', 'Technical Analysis (Full)', 'ta', args.skip_ta),
        ('daily_macro_commodity.py', 'Macro & Commodity Data', 'macro', args.skip_macro),
        ('daily_valuation.py', 'Stock Valuation (PE/PB/EV-EBITDA)', 'valuation', args.skip_valuation),
        ('daily_sector_analysis.py', 'Sector Analysis', 'sector', args.skip_sector),
        ('daily_bsc_forecast.py', 'BSC Forecast Update', 'bscforecast', args.skip_bscforecast),
    ]

    # Filter pipeline based on args
    active_pipeline = []
    for script, desc, key, skip in pipeline:
        if args.only and args.only != key:
            continue
        if skip:
            logger.info(f"\n⏭️  SKIPPED: {desc} (--skip-{key} specified)")
            continue
        active_pipeline.append((script, desc, key))

    total_steps = len(active_pipeline)

    if total_steps == 0:
        logger.warning("\n⚠️  No steps to run (all skipped)")
        # Still show data integrity report
        show_data_integrity_report()
        sys.exit(0)

    logger.info(f"\n📋 Pipeline: {total_steps} steps to run")
    logger.info("")

    # Run pipeline
    for step_num, (script, description, key) in enumerate(active_pipeline, start=1):
        success, duration, file_info = run_script(script, description, step_num, total_steps, key)
        results[key] = success
        durations[key] = duration
        if file_info:
            file_infos[key] = file_info

        if not success:
            logger.warning(f"⚠️  Continuing despite failure in: {description}")

    # Summary
    total_elapsed = (datetime.now() - pipeline_start).total_seconds()

    logger.info("\n" + "=" * 80)
    logger.info("📊 MASTER DAILY UPDATE PIPELINE - SUMMARY")
    logger.info("=" * 80)
    logger.info(f"\n⏱️  Total execution time: {format_duration(total_elapsed)}")
    logger.info("")

    # Step-by-step results
    logger.info("📋 Results by Step:")
    for step_num, (script, desc, key) in enumerate(active_pipeline, start=1):
        success = results.get(key, False)
        duration = durations.get(key, 0)
        status_icon = "✅" if success else "❌"

        logger.info(f"   {step_num}. {status_icon} {desc}")
        logger.info(f"      └─ Duration: {format_duration(duration)}")

        # Show file count
        if key in file_infos and file_infos[key]["status"] == "ok":
            file_count = len(file_infos[key]["files"])
            total_mb = file_infos[key]["total_size_mb"]
            logger.info(f"      └─ Output: {file_count} files ({total_mb:.1f} MB)")

    # Overall stats
    success_count = sum(1 for v in results.values() if v)
    failed_count = len(results) - success_count

    logger.info(f"\n📈 Overall Statistics:")
    logger.info(f"   Total steps: {len(results)}")
    logger.info(f"   Successful: {success_count}")
    logger.info(f"   Failed: {failed_count}")
    logger.info(f"   Success rate: {success_count/len(results)*100:.0f}%")

    # Total data size
    total_data_mb = sum(info.get("total_size_mb", 0) for info in file_infos.values())
    if total_data_mb > 0:
        logger.info(f"   Total output size: {total_data_mb:.1f} MB")

    logger.info("=" * 80)

    # Critical data check - OHLCV
    logger.info("\n" + "=" * 80)
    logger.info("🔍 CRITICAL DATA CHECK - OHLCV")
    logger.info("=" * 80)

    ohlcv_path = PROJECT_ROOT / "DATA" / "raw" / "ohlcv" / "OHLCV_mktcap.parquet"
    if ohlcv_path.exists():
        try:
            df = pd.read_parquet(ohlcv_path)
            latest = pd.to_datetime(df['date']).max()
            today = datetime.now().date()
            symbol_col = 'symbol' if 'symbol' in df.columns else 'ticker'
            symbols = df[symbol_col].nunique()

            logger.info(f"   OHLCV Latest Date: {latest.strftime('%Y-%m-%d')}")
            logger.info(f"   Today's Date: {today}")
            logger.info(f"   Total Symbols: {symbols}")
            logger.info(f"   Total Records: {len(df):,}")

            # Check if up to date (within 1 trading day)
            days_diff = (today - latest.date()).days
            if days_diff <= 1:
                logger.info(f"   Status: ✅ UP TO DATE")
            elif days_diff <= 3:
                logger.info(f"   Status: ⚠️ {days_diff} DAYS BEHIND (may be weekend)")
            else:
                logger.warning(f"   Status: ❌ {days_diff} DAYS BEHIND - CHECK DATA SOURCE!")

        except Exception as e:
            logger.error(f"   Error checking OHLCV: {e}")
    else:
        logger.error(f"   ❌ OHLCV file not found!")

    logger.info("=" * 80)

    # ========== FINAL DATA INTEGRITY REPORT ==========
    all_data_ok = show_data_integrity_report()

    # Exit code
    all_success = all(results.values())
    if all_success and all_data_ok:
        logger.info("\n🎉 ALL UPDATES COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    elif all_success:
        logger.info("\n✅ Pipeline completed but some data may not be up to today")
        sys.exit(0)
    else:
        logger.error(f"\n⚠️  {failed_count}/{len(results)} UPDATES FAILED - CHECK LOGS ABOVE")
        sys.exit(1)


if __name__ == '__main__':
    main()
