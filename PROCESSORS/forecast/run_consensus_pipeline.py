#!/usr/bin/env python3
"""
Consensus Forecast Pipeline Orchestrator.

This script orchestrates the full consensus data pipeline:
1. Extract: PDF/Screenshot → JSON (staging)
2. Normalize: JSON → Parquet (processed)
3. Validate: Check coverage and data quality

Usage:
    python run_consensus_pipeline.py                    # Full pipeline (normalize only)
    python run_consensus_pipeline.py --extract-pdf      # Extract from PDFs first
    python run_consensus_pipeline.py --extract-screenshots  # Extract from screenshots
    python run_consensus_pipeline.py --validate         # Validate only

Environment:
    GEMINI_API_KEY: Required for extraction steps.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path("/Users/buuphan/Dev/Vietnam_dashboard")
PROCESSORS_DIR = PROJECT_ROOT / "PROCESSORS" / "forecast"
RAW_FORECAST_DIR = PROJECT_ROOT / "DATA" / "raw" / "forecast"
OUTPUT_DIR = PROJECT_ROOT / "DATA" / "processed" / "forecast" / "consensus"
SOURCES_DIR = PROJECT_ROOT / "DATA" / "processed" / "forecast" / "sources"

# Source-specific paths (HCM and SSI separated)
HCM_DIR = RAW_FORECAST_DIR / "hcm"
SSI_DIR = RAW_FORECAST_DIR / "ssi"


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"[STEP] {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"[OK] {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        return False


def extract_pdfs():
    """Extract data from all PDFs in the pdf folder."""
    pdf_files = list(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"[WARNING] No PDF files found in {PDF_DIR}")
        return False

    print(f"[INFO] Found {len(pdf_files)} PDF files")

    # Source mapping based on filename
    source_mapping = {
        'hcm': ['hcm', 'strategy'],
        'ssi': ['ssi'],
        'vci': ['vci', 'chienluoc'],
        'shs': ['shs'],
    }

    for pdf_path in pdf_files:
        # Infer source from filename
        filename_lower = pdf_path.stem.lower()
        source = None
        for src, keywords in source_mapping.items():
            if any(kw in filename_lower for kw in keywords):
                source = src
                break

        if not source:
            print(f"[SKIP] Cannot infer source for: {pdf_path.name}")
            continue

        cmd = [
            sys.executable,
            str(PROCESSORS_DIR / "hcm_ssi_extraction" / "pdf_extractor.py"),
            "--pdf", str(pdf_path),
            "--source", source
        ]
        run_command(cmd, f"Extract {source.upper()} from {pdf_path.name}")

    return True


def extract_screenshots():
    """Extract data from screenshots in the screenshots folder."""
    cmd = [
        sys.executable,
        str(PROCESSORS_DIR / "hcm_ssi_extraction" / "screenshot_extractor.py")
    ]
    return run_command(cmd, "Extract from screenshots")


def normalize():
    """Run normalization to convert staging JSON to processed parquet."""
    cmd = [
        sys.executable,
        str(PROCESSORS_DIR / "hcm_ssi_extraction" / "hcm_ssi_update_script.py")
    ]
    return run_command(cmd, "Normalize consensus data")


def validate():
    """Validate the output data quality."""
    import pandas as pd

    print(f"\n{'='*60}")
    print("[STEP] Validate Output Data")
    print(f"{'='*60}")

    # Check output files exist
    required_files = [
        'consensus_combined.parquet',
        'consensus_summary.parquet',
        'hcm_forecast.parquet',
        'ssi_forecast.parquet',
        'vci_forecast.parquet',
    ]

    missing = []
    for f in required_files:
        if not (OUTPUT_DIR / f).exists():
            missing.append(f)

    if missing:
        print(f"[ERROR] Missing files: {missing}")
        return False

    # Load and check data quality
    combined = pd.read_parquet(OUTPUT_DIR / "consensus_combined.parquet")

    print(f"\n[DATA QUALITY CHECK]")
    print(f"Total records: {len(combined)}")
    print(f"Unique tickers: {combined['symbol'].nunique()}")
    print(f"Sources: {combined['source'].unique().tolist()}")

    # Coverage check (schema migrated to 2026F/2027F in Jan 2026)
    npatmi_2026_coverage = combined['npatmi_2026f'].notna().sum() / len(combined) * 100
    npatmi_2027_coverage = combined['npatmi_2027f'].notna().sum() / len(combined) * 100
    tp_coverage = combined['target_price'].notna().sum() / len(combined) * 100

    print(f"\n[COVERAGE]")
    print(f"NPATMI 2026F: {npatmi_2026_coverage:.1f}%")
    print(f"NPATMI 2027F: {npatmi_2027_coverage:.1f}%")
    print(f"Target Price: {tp_coverage:.1f}%")

    # Multi-source coverage
    coverage = combined.groupby('symbol')['source'].count()
    print(f"\n[MULTI-SOURCE COVERAGE]")
    print(f"  1 source: {(coverage == 1).sum()} stocks")
    print(f"  2 sources: {(coverage == 2).sum()} stocks")
    print(f"  3+ sources: {(coverage >= 3).sum()} stocks")

    # Success criteria
    success = npatmi_2026_coverage >= 80
    if success:
        print(f"\n[OK] Data quality check PASSED")
    else:
        print(f"\n[WARNING] NPATMI 2026F coverage below 80%")

    return success


def main():
    parser = argparse.ArgumentParser(
        description="Consensus Forecast Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full normalization (default)
  python run_consensus_pipeline.py

  # Extract from PDFs first, then normalize
  python run_consensus_pipeline.py --extract-pdf

  # Extract from screenshots, then normalize
  python run_consensus_pipeline.py --extract-screenshots

  # Validate only (no processing)
  python run_consensus_pipeline.py --validate
        """
    )
    parser.add_argument('--extract-pdf', action='store_true',
                        help='Extract data from PDFs before normalizing')
    parser.add_argument('--extract-screenshots', action='store_true',
                        help='Extract data from screenshots before normalizing')
    parser.add_argument('--validate', action='store_true',
                        help='Only validate output data')
    parser.add_argument('--skip-normalize', action='store_true',
                        help='Skip normalization step')

    args = parser.parse_args()

    print("="*60)
    print("CONSENSUS FORECAST PIPELINE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Validate only mode
    if args.validate:
        validate()
        return

    # Extraction steps
    if args.extract_pdf:
        extract_pdfs()

    if args.extract_screenshots:
        extract_screenshots()

    # Normalization
    if not args.skip_normalize:
        normalize()

    # Always validate at the end
    validate()

    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)


if __name__ == "__main__":
    main()
