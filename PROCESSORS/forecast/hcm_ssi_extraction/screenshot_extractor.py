#!/usr/bin/env python3
"""
Batch extract stock forecast data from screenshots using Gemini API.

This script processes images in the screenshots folder and extracts
tabular forecast data (NPATMI, PE, Target Price).

Usage:
    python screenshot_extractor.py
    python screenshot_extractor.py --source hcm
    python screenshot_extractor.py --file specific_image.png --source ssi

Environment:
    GEMINI_API_KEY: Required. Your Google Gemini API key.

Input:
    Images in DATA/raw/forecast/{source}/screenshots/

Output:
    JSON files in DATA/raw/forecast/{source}/extracted/
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai not installed. Run: pip install google-generativeai")
    sys.exit(1)

# Paths
PROJECT_ROOT = Path("/Users/buuphan/Dev/Vietnam_dashboard")
RAW_FORECAST_DIR = PROJECT_ROOT / "DATA" / "raw" / "forecast"

def get_source_paths(source: str):
    """Get screenshots and extracted dirs for a source."""
    source_dir = RAW_FORECAST_DIR / source
    return source_dir / "screenshots", source_dir / "extracted"

# Extraction prompt for table images
TABLE_EXTRACTION_PROMPT = """
Extract stock forecast data from this table image.

For EACH row/stock in the table, extract:
- ticker: Stock symbol (uppercase, e.g., VCB, ACB, FPT)
- target_price: Target price in VND (null if not shown)
- npatmi_2025f: Forecast NPATMI 2025 in billion VND (null if not shown)
- npatmi_2026f: Forecast NPATMI 2026 in billion VND (null if not shown)
- npatmi_growth_2025: YoY growth 2025 as decimal (0.15 = 15%)
- npatmi_growth_2026: YoY growth 2026 as decimal
- pe_fwd_2025: Forward PE 2025 (null if not shown)
- pe_fwd_2026: Forward PE 2026 (null if not shown)
- rating: Buy/Add/Hold/Reduce/Sell (null if not shown)

IMPORTANT:
- Convert percentages to decimals (15% → 0.15)
- Keep prices in VND (not thousands)
- Keep NPATMI in billion VND
- Return ONLY a valid JSON array

Example output:
[
  {"ticker": "VCB", "target_price": 72900, "npatmi_2025f": 45000, "npatmi_growth_2025": 0.18, "pe_fwd_2025": 12.5},
  {"ticker": "ACB", "target_price": 35000, "npatmi_2025f": 22000, "npatmi_growth_2025": 0.22, "pe_fwd_2025": 8.2}
]
"""


def setup_api():
    """Configure Gemini API with environment key."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Set it with: export GEMINI_API_KEY=your_api_key")
        sys.exit(1)

    genai.configure(api_key=api_key)
    return api_key


def extract_from_image(image_path: Path, model_name: str = "gemini-2.5-flash") -> list:
    """
    Extract forecast data from image using Gemini API.

    Args:
        image_path: Path to image file
        model_name: Gemini model to use

    Returns:
        List of stock forecast dictionaries
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    print(f"[INFO] Processing: {image_path.name} ({image_path.stat().st_size / 1024:.1f}KB)")

    # Upload image
    uploaded_file = genai.upload_file(str(image_path))
    print(f"[INFO] Uploaded: {uploaded_file.name}")

    # Extract with vision model
    model = genai.GenerativeModel(model_name)
    response = model.generate_content([uploaded_file, TABLE_EXTRACTION_PROMPT])

    # Parse JSON from response
    text = response.text

    # Handle markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    try:
        data = json.loads(text.strip())
        if not isinstance(data, list):
            data = [data]
        return data
    except json.JSONDecodeError as e:
        print(f"[WARNING] JSON parsing failed: {e}")
        return {"error": str(e), "raw_response": response.text}


def process_screenshots_folder(source: str = None, model_name: str = "gemini-2.5-flash") -> dict:
    """
    Process all images in screenshots folder.

    Args:
        source: Optional source filter (e.g., "hcm" to process only hcm_*.png)
        model_name: Gemini model to use

    Returns:
        Dictionary with source -> extracted data
    """
    results = {}

    # Find image files
    image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
    images = [f for f in SCREENSHOTS_DIR.iterdir()
              if f.suffix.lower() in image_extensions]

    if source:
        images = [f for f in images if f.stem.lower().startswith(source.lower())]

    if not images:
        print(f"[WARNING] No images found in {SCREENSHOTS_DIR}")
        return results

    print(f"[INFO] Found {len(images)} images to process")

    for image_path in sorted(images):
        # Infer source from filename (e.g., hcm_table_01.png -> hcm)
        img_source = image_path.stem.split('_')[0].lower()

        try:
            data = extract_from_image(image_path, model_name)

            if isinstance(data, list):
                if img_source not in results:
                    results[img_source] = []
                results[img_source].extend(data)
                print(f"[OK] Extracted {len(data)} stocks from {image_path.name}")
            else:
                print(f"[ERROR] Failed to extract from {image_path.name}")

        except Exception as e:
            print(f"[ERROR] {image_path.name}: {e}")

    return results


def save_results(results: dict) -> list:
    """
    Save extraction results to staging folder.

    Args:
        results: Dictionary with source -> list of stocks

    Returns:
        List of saved file paths
    """
    saved_files = []
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    for source, data in results.items():
        if not data:
            continue

        # Merge with existing data if file exists
        output_path = STAGING_DIR / f"{source}_raw.json"

        existing_data = []
        if output_path.exists():
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

        # Merge: existing + new (dedup by ticker)
        existing_tickers = {d.get('ticker') for d in existing_data}
        merged_data = existing_data + [d for d in data if d.get('ticker') not in existing_tickers]

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)

        print(f"[SAVED] {output_path} ({len(merged_data)} stocks)")
        saved_files.append(str(output_path))

    return saved_files


def main():
    parser = argparse.ArgumentParser(
        description="Extract stock forecast data from screenshots using Gemini API"
    )
    parser.add_argument('--source', type=str, help='Filter by source (e.g., hcm, ssi)')
    parser.add_argument('--file', type=str, help='Process specific image file')
    parser.add_argument('--model', type=str, default='gemini-2.5-flash',
                        help='Gemini model (default: gemini-2.5-flash)')

    args = parser.parse_args()

    # Setup API
    setup_api()

    print(f"\n{'='*60}")
    print("SCREENSHOT FORECAST EXTRACTION")
    print(f"{'='*60}")
    print(f"Screenshots folder: {SCREENSHOTS_DIR}")
    print(f"Model: {args.model}")

    if args.file:
        # Process single file
        image_path = Path(args.file)
        if not image_path.is_absolute():
            image_path = SCREENSHOTS_DIR / args.file

        data = extract_from_image(image_path, args.model)

        if isinstance(data, list):
            source = args.source or image_path.stem.split('_')[0].lower()
            results = {source: data}
            save_results(results)
        else:
            print(f"[ERROR] Extraction failed")
    else:
        # Process folder
        results = process_screenshots_folder(args.source, args.model)
        if results:
            save_results(results)

    print(f"\n{'='*60}")
    print("DONE!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
