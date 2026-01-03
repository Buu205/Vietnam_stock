#!/usr/bin/env python3
"""
Extract stock forecast data from Vietnamese securities strategy reports using Gemini API.

Usage:
    python extract_forecast_from_pdf.py --pdf <path_to_pdf> --source <source_name>
    python extract_forecast_from_pdf.py --pdf report.pdf --source hsc --model gemini-3-pro-preview
    python extract_forecast_from_pdf.py --pdf report.pdf --source vci --output custom_output.json

Environment:
    GEMINI_API_KEY: Required. Your Google Gemini API key.

Output:
    JSON file with extracted stock forecasts saved to raw_extracts/<source>_raw.json
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


# Default extraction prompt for Vietnamese strategy reports
DEFAULT_PROMPT = """
Analyze this Vietnamese stock market strategy report comprehensively.

IMPORTANT: Extract ALL stocks mentioned with ANY forecast data.
Do NOT limit to any specific list - extract EVERY stock with forecasts.

For EACH stock found, extract these fields (use null for missing values):
- ticker: Stock symbol (uppercase, e.g., VCB, ACB, FPT)
- company_name: Company name in Vietnamese (if available)
- sector: Sector/Industry classification (if mentioned)
- npatmi_2024a: Actual NPATMI 2024 (billion VND)
- npatmi_2025f: Forecast NPATMI 2025 (billion VND)
- npatmi_2026f: Forecast NPATMI 2026 (billion VND)
- revenue_2025f: Revenue forecast 2025 (billion VND)
- revenue_2026f: Revenue forecast 2026 (billion VND)
- pe_fwd_2025: Forward PE ratio 2025
- pe_fwd_2026: Forward PE ratio 2026
- pb_fwd_2025: Forward PB ratio 2025
- pb_fwd_2026: Forward PB ratio 2026
- eps_2025f: EPS forecast 2025 (VND)
- eps_2026f: EPS forecast 2026 (VND)
- npatmi_growth_2025: YoY growth 2025 (decimal, e.g., 0.15 for 15%)
- npatmi_growth_2026: YoY growth 2026 (decimal)
- target_price: Target price (VND)
- upside: Upside potential (decimal)
- rating: Rating (Buy/Add/Hold/Reduce/Sell)

Return ONLY a valid JSON array. Example:
[
  {"ticker": "VCB", "npatmi_2025f": 45000, "pe_fwd_2025": 12.5, "target_price": 72900, "rating": "Buy", ...},
  ...
]

Extract from ALL pages, ALL tables, ALL stock recommendations.
Include stocks from sector analysis, top picks, coverage universe, valuation tables.
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


def extract_forecast(pdf_path: str, model_name: str = "gemini-3-pro-preview",
                     custom_prompt: str = None) -> list:
    """
    Extract forecast data from PDF using Gemini API.

    Args:
        pdf_path: Path to PDF file
        model_name: Gemini model to use
        custom_prompt: Custom extraction prompt (optional)

    Returns:
        List of stock forecast dictionaries
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print(f"[INFO] Uploading PDF: {pdf_path} ({pdf_path.stat().st_size / 1024 / 1024:.1f}MB)")

    # Upload PDF to Gemini
    uploaded_file = genai.upload_file(str(pdf_path), mime_type="application/pdf")
    print(f"[INFO] Uploaded: {uploaded_file.name}")

    # Initialize model
    model = genai.GenerativeModel(model_name)
    prompt = custom_prompt or DEFAULT_PROMPT

    print(f"[INFO] Extracting with model: {model_name}")
    response = model.generate_content([uploaded_file, prompt])

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
        print(f"[WARNING] Raw response saved for manual review")
        return {"error": str(e), "raw_response": response.text}


def save_result(data: list | dict, output_path: str, source: str) -> str:
    """
    Save extraction result to JSON file.

    Args:
        data: Extracted data
        output_path: Output file path
        source: Source identifier for metadata

    Returns:
        Path to saved file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Add metadata
    result = {
        "metadata": {
            "source": source,
            "extracted_at": datetime.now().isoformat(),
            "total_stocks": len(data) if isinstance(data, list) else 0
        },
        "data": data
    }

    # If data is a list, save directly (backward compatible)
    if isinstance(data, list):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        # Save error result
        error_path = str(output_path).replace('.json', '_error.json')
        with open(error_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return error_path

    return str(output_path)


def list_models():
    """List available Gemini models."""
    print("\nAvailable Gemini models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name.replace('models/', '')}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract stock forecast data from PDF using Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic extraction
  python extract_forecast_from_pdf.py --pdf report.pdf --source hsc

  # Use specific model
  python extract_forecast_from_pdf.py --pdf report.pdf --source vci --model gemini-2.5-pro

  # Custom output path
  python extract_forecast_from_pdf.py --pdf report.pdf --source ssi --output my_output.json

  # List available models
  python extract_forecast_from_pdf.py --list-models
        """
    )

    parser.add_argument('--pdf', type=str, help='Path to PDF file')
    parser.add_argument('--source', type=str, help='Source identifier (e.g., hsc, vci, ssi, shs, bsc)')
    parser.add_argument('--model', type=str, default='gemini-3-pro-preview',
                        help='Gemini model to use (default: gemini-3-pro-preview)')
    parser.add_argument('--output', type=str, help='Custom output path (default: <source>_raw.json)')
    parser.add_argument('--prompt', type=str, help='Custom extraction prompt')
    parser.add_argument('--prompt-file', type=str, help='File containing custom prompt')
    parser.add_argument('--list-models', action='store_true', help='List available Gemini models')

    args = parser.parse_args()

    # Setup API
    setup_api()

    # List models if requested
    if args.list_models:
        list_models()
        return

    # Validate required args
    if not args.pdf or not args.source:
        parser.print_help()
        print("\nError: --pdf and --source are required")
        sys.exit(1)

    # Get custom prompt if provided
    custom_prompt = None
    if args.prompt:
        custom_prompt = args.prompt
    elif args.prompt_file:
        with open(args.prompt_file, 'r') as f:
            custom_prompt = f.read()

    # Set output path - save to staging folder
    staging_dir = Path("/Users/buuphan/Dev/Vietnam_dashboard/DATA/raw/concensus_report/staging")
    output_path = args.output or str(staging_dir / f"{args.source}_raw.json")

    try:
        # Extract data
        print(f"\n{'='*60}")
        print(f"Extracting forecast data from: {args.pdf}")
        print(f"Source: {args.source}")
        print(f"Model: {args.model}")
        print(f"{'='*60}\n")

        data = extract_forecast(args.pdf, args.model, custom_prompt)

        # Save result
        saved_path = save_result(data, output_path, args.source)

        # Summary
        if isinstance(data, list):
            tickers = sorted(set(d.get('ticker', '') for d in data if d.get('ticker')))
            print(f"\n{'='*60}")
            print(f"EXTRACTION COMPLETE")
            print(f"{'='*60}")
            print(f"Total stocks: {len(data)}")
            print(f"Unique tickers: {len(tickers)}")
            print(f"Output: {saved_path}")
            print(f"\nTickers: {', '.join(tickers)}")
        else:
            print(f"\n[ERROR] Extraction failed. Check: {saved_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during extraction: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
