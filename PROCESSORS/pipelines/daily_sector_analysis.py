#!/usr/bin/env python3
"""
Run Sector Analysis - CLI Script
=================================

Chạy phân tích ngành qua dòng lệnh.
Command-line interface for running sector analysis pipeline.

This script provides a command-line interface to run the complete
sector analysis pipeline with configurable date ranges and options.

Usage:
    # Run with default settings (all available data)
    python3 run_sector_analysis.py

    # Run for specific date range
    python3 run_sector_analysis.py --start-date 2024-01-01 --end-date 2024-12-31

    # Run for specific report date (FA only)
    python3 run_sector_analysis.py --report-date 2024-09-30

    # Run with verbose logging
    python3 run_sector_analysis.py --verbose

    # Run with custom output directory
    python3 run_sector_analysis.py --output-dir /custom/path

Author: Claude Code
Date: 2025-12-15
Version: 1.0.0
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PROCESSORS.sector.sector_processor import SectorProcessor


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration.

    Thiết lập cấu hình logging.

    Args:
        verbose: Enable verbose (DEBUG) logging
    """
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def validate_date(date_str: Optional[str], date_name: str) -> Optional[str]:
    """
    Validate date format.

    Kiểm tra định dạng ngày tháng.

    Args:
        date_str: Date string (YYYY-MM-DD)
        date_name: Name of the date field (for error messages)

    Returns:
        Validated date string or None

    Raises:
        ValueError: If date format is invalid
    """
    if date_str is None:
        return None

    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        raise ValueError(
            f"Invalid {date_name} format: {date_str}. "
            f"Expected format: YYYY-MM-DD (e.g., 2024-01-01)"
        )


def print_summary(results: dict, execution_time: float, output_dir: Path) -> None:
    """
    Print execution summary.

    In tóm tắt kết quả thực thi.

    Args:
        results: Results dictionary from pipeline
        execution_time: Execution time in seconds
        output_dir: Output directory path
    """
    print("\n" + "=" * 80)
    print("📊 EXECUTION SUMMARY - TÓM TẮT THỰC THI")
    print("=" * 80)

    # Execution time
    print(f"\n⏱️  Execution time: {execution_time:.1f} seconds")

    # Results summary
    if 'fa_metrics' in results:
        fa_metrics = results['fa_metrics']
        print(f"\n📈 Fundamental Analysis:")
        print(f"   Records: {len(fa_metrics):,}")
        print(f"   Sectors: {fa_metrics['sector_code'].nunique()}")
        print(f"   Date range: {fa_metrics['report_date'].min()} to {fa_metrics['report_date'].max()}")

    if 'ta_metrics' in results:
        ta_metrics = results['ta_metrics']
        print(f"\n📉 Technical/Valuation Analysis:")
        print(f"   Records: {len(ta_metrics):,}")
        print(f"   Sectors: {ta_metrics['sector_code'].nunique()}")
        print(f"   Date range: {ta_metrics['date'].min()} to {ta_metrics['date'].max()}")

    if 'combined_scores' in results:
        combined = results['combined_scores']
        print(f"\n🎯 Combined Scores & Signals:")
        print(f"   Total records: {len(combined):,}")

        # Signal distribution
        signal_dist = combined['signal'].value_counts()
        print(f"\n   Signal Distribution:")
        for signal in ['BUY', 'HOLD', 'SELL']:
            count = signal_dist.get(signal, 0)
            pct = (count / len(combined) * 100) if len(combined) > 0 else 0
            print(f"     {signal:5s}: {count:3d} sectors ({pct:5.1f}%)")

        # Top 5 sectors by combined score
        if not combined.empty:
            top5 = combined.nlargest(5, 'combined_score')
            print(f"\n   🏆 Top 5 Sectors by Combined Score:")
            for idx, row in top5.iterrows():
                print(f"     {row['sector_code']:20s}: {row['combined_score']:5.1f} ({row['signal']})")

    # Output files
    print(f"\n📁 Output Files:")
    output_files = [
        'sector_fundamental_metrics.parquet',
        'sector_valuation_metrics.parquet',
        'sector_combined_scores.parquet'
    ]

    for filename in output_files:
        filepath = output_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"   ✅ {filename:35s} ({size_mb:6.2f} MB)")
        else:
            print(f"   ❌ {filename:35s} (not found)")

    print(f"\n📂 Output directory: {output_dir}")
    print("=" * 80)


def main():
    """
    Main function - Hàm chính.

    Parse arguments, run pipeline, and display results.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Run sector analysis pipeline - Chạy phân tích ngành',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (all data)
  python3 run_sector_analysis.py

  # Run for specific date range
  python3 run_sector_analysis.py --start-date 2024-01-01 --end-date 2024-12-31

  # Run for last 6 months with verbose logging
  python3 run_sector_analysis.py --start-date 2024-06-01 --verbose

  # Run for specific quarter (FA only)
  python3 run_sector_analysis.py --report-date 2024-09-30
        """
    )

    parser.add_argument(
        '--start-date',
        type=str,
        default=None,
        help='Start date for analysis (YYYY-MM-DD), e.g., 2024-01-01'
    )

    parser.add_argument(
        '--end-date',
        type=str,
        default=None,
        help='End date for analysis (YYYY-MM-DD), e.g., 2024-12-31'
    )

    parser.add_argument(
        '--report-date',
        type=str,
        default=None,
        help='Specific report date for FA analysis (YYYY-MM-DD), e.g., 2024-09-30'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose (DEBUG) logging'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Custom output directory (default: DATA/processed/sector/)'
    )

    parser.add_argument(
        '--ta-only',
        action='store_true',
        help='Run TA aggregation only (skip FA processing)'
    )

    parser.add_argument(
        '--fa-only',
        action='store_true',
        help='Run FA aggregation only (skip TA processing)'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    logger = logging.getLogger(__name__)

    # Print header
    print("\n" + "=" * 80)
    print("🚀 SECTOR ANALYSIS PIPELINE - QUY TRÌNH PHÂN TÍCH NGÀNH")
    print("=" * 80)

    # Validate dates
    try:
        start_date = validate_date(args.start_date, 'start-date')
        end_date = validate_date(args.end_date, 'end-date')
        report_date = validate_date(args.report_date, 'report-date')
    except ValueError as e:
        logger.error(f"❌ Date validation error: {e}")
        sys.exit(1)

    # Check date logic
    if start_date and end_date:
        if start_date > end_date:
            logger.error("❌ Error: start-date cannot be after end-date")
            sys.exit(1)

    # Print configuration
    print("\n📋 Configuration:")
    print(f"   Start date: {start_date or 'Not specified (all data)'}")
    print(f"   End date: {end_date or 'Not specified (all data)'}")
    print(f"   Report date: {report_date or 'Not specified'}")
    print(f"   Verbose logging: {args.verbose}")

    # Initialize processor
    try:
        logger.info("Initializing sector processor...")
        processor = SectorProcessor()

        # Override output directory if specified
        if args.output_dir:
            processor.output_dir = Path(args.output_dir)
            processor.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using custom output directory: {processor.output_dir}")

        print(f"   Output directory: {processor.output_dir}")

    except Exception as e:
        logger.error(f"❌ Failed to initialize processor: {e}")
        sys.exit(2)

    # Run pipeline
    try:
        logger.info("Starting sector analysis pipeline...")
        start_time = datetime.now()

        results = processor.run_full_pipeline(
            start_date=start_date,
            end_date=end_date,
            report_date=report_date
        )

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # Print summary
        print_summary(results, execution_time, processor.output_dir)

        print("\n✅ SUCCESS - Pipeline completed successfully!")
        print("=" * 80)

        sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Pipeline interrupted by user (Ctrl+C)")
        sys.exit(130)

    except Exception as e:
        logger.error(f"\n❌ Pipeline failed with error: {e}", exc_info=args.verbose)
        print("\n" + "=" * 80)
        print("❌ FAILURE - Pipeline failed")
        print("=" * 80)
        sys.exit(3)


if __name__ == "__main__":
    main()
