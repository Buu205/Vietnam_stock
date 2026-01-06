#!/usr/bin/env python3
"""
Consensus Update Pipeline
=========================

One-click pipeline to update consensus data from Excel to Streamlit:
1. Parse Excel (HSC_AI, SSI_AI sheets) -> JSON sources
2. Build unified.parquet for Streamlit

Usage:
    python3 PROCESSORS/forecast/update_consensus_pipeline.py

Input:
    DATA/raw/forecast/Consensus.xlsx

Output:
    DATA/processed/forecast/sources/ssi.json
    DATA/processed/forecast/sources/hcm.json
    DATA/processed/forecast/unified.parquet
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def step_1_parse_excel():
    """Step 1: Parse Excel -> JSON sources."""
    print("\n" + "=" * 60)
    print("STEP 1: Parse Excel -> JSON")
    print("=" * 60)

    from PROCESSORS.forecast.parsers.excel_consensus_parser import main as parse_excel
    parse_excel()


def step_2_build_unified():
    """Step 2: Build unified.parquet from all JSON sources."""
    print("\n" + "=" * 60)
    print("STEP 2: Build unified.parquet")
    print("=" * 60)

    from PROCESSORS.forecast.unified.build_unified import build_unified
    build_unified()


def main():
    """Run full consensus update pipeline."""
    print("=" * 60)
    print("CONSENSUS UPDATE PIPELINE")
    print("=" * 60)
    print("""
Pipeline steps:
  1. Parse Excel (HSC_AI, SSI_AI) -> JSON
  2. Build unified.parquet -> Streamlit
    """)

    # Step 1: Parse Excel
    step_1_parse_excel()

    # Step 2: Build unified.parquet
    step_2_build_unified()

    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print("""
✅ Updated files:
   - DATA/processed/forecast/sources/ssi.json
   - DATA/processed/forecast/sources/hcm.json
   - DATA/processed/forecast/unified.parquet

📌 Next: Refresh Streamlit browser to see new data
    """)


if __name__ == "__main__":
    main()
