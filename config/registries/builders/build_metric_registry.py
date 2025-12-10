#!/usr/bin/env python3
"""
Metric Registry Builder
========================

Convert BSC - Mô tả CSDL.xlsx to structured JSON registry for:
- AI/Human readable metric definitions
- Fast lookups by code or name
- Validation of available metrics

Usage:
    python PROCESSORS/core/registries/build_metric_registry.py

Output:
    config/metadata_registry/metrics/metric_registry.json (primary)
    config/metric_registry.json (backward compatibility)

Author: Claude Code
Date: 2025-12-05
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_project_root() -> Path:
    """Find project root (stock_dashboard directory)"""
    current = Path(__file__).resolve()
    while current.parent != current:
        if current.name == 'Vietnam_dashboard':
            return current
        current = current.parent
    # Fallback
    return Path(__file__).resolve().parent.parent.parent


PROJECT_ROOT = find_project_root()


def get_metric_prefix(sheet_name: str) -> str:
    """
    Get metric code prefix from sheet name

    Examples:
        COMPANY_INCOME → CIS_
        BANK_BALANCE_SHEET → BBS_
        INSURANCE_CF_DIRECT → ICD_
    """
    parts = sheet_name.split('_')

    # Entity prefix (first letter)
    entity_map = {
        'COMPANY': 'C',
        'BANK': 'B',
        'INSURANCE': 'I',
        'SECURITY': 'S'
    }
    entity_prefix = entity_map.get(parts[0], parts[0][0])

    # Statement type prefix
    type_map = {
        'INCOME': 'IS',
        'BALANCE': 'BS',
        'SHEET': '',  # Already included in BALANCE_SHEET
        'CF': 'CF',
        'DIRECT': 'D',
        'INDIRECT': 'I',
        'NOTE': 'NOT'
    }

    # Build prefix
    if 'INCOME' in sheet_name:
        return f'{entity_prefix}IS_'
    elif 'BALANCE_SHEET' in sheet_name or 'BALANCE' in sheet_name:
        return f'{entity_prefix}BS_'
    elif 'CF_DIRECT' in sheet_name:
        return f'{entity_prefix}CD_'
    elif 'CF_INDIRECT' in sheet_name:
        return f'{entity_prefix}CI_'
    elif 'NOTE' in sheet_name:
        return f'{entity_prefix}NOT_'
    else:
        # Fallback: use all parts
        return f"{entity_prefix}{''.join(p[0] for p in parts[1:])}_"


def get_category(sheet_name: str) -> str:
    """
    Get category name from sheet name

    Examples:
        COMPANY_INCOME → INCOME
        BANK_BALANCE_SHEET → BALANCE_SHEET
        INSURANCE_CF_DIRECT → CASH_FLOW_DIRECT
    """
    if 'INCOME' in sheet_name:
        return 'INCOME'
    elif 'BALANCE' in sheet_name:
        return 'BALANCE_SHEET'
    elif 'CF_DIRECT' in sheet_name:
        return 'CASH_FLOW_DIRECT'
    elif 'CF_INDIRECT' in sheet_name:
        return 'CASH_FLOW_INDIRECT'
    elif 'NOTE' in sheet_name:
        return 'NOTE'
    else:
        return 'OTHER'


def convert_bsc_excel_to_registry() -> Dict:
    """
    Convert BSC - Mô tả CSDL.xlsx to metric_registry.json

    Returns:
        Dictionary containing complete metric registry
    """
    logger.info("=" * 60)
    logger.info("Starting BSC Excel to Metric Registry Conversion")
    logger.info("=" * 60)

    excel_file = PROJECT_ROOT / "DATA" / "raw" / "Metric_code" / "BSC - Mô tả CSDL.xlsx"

    if not excel_file.exists():
        raise FileNotFoundError(f"BSC Excel file not found: {excel_file}")

    logger.info(f"Reading Excel file: {excel_file.name}")

    # Entity types and their relevant sheets
    entity_sheets = {
        "COMPANY": [
            "COMPANY_INCOME",
            "COMPANY_BALANCE_SHEET",
            "COMPANY_CF_DIRECT",
            "COMPANY_CF_INDIRECT",
            "COMPANY_NOTE"
        ],
        "BANK": [
            "BANK_INCOME",
            "BANK_BALANCE_SHEET",
            "BANK_CF_DIRECT",
            "BANK_CF_INDIRECT",
            "BANK_NOTE"
        ],
        "INSURANCE": [
            "INSURANCE_INCOME",
            "INSURANCE_BALANCE_SHEET",
            "INSURANCE_CF_DIRECT",
            "INSURANCE_CF_INDIRECT",
            "INSURANCE_NOTE"
        ],
        "SECURITY": [
            "SECURITY_INCOME",
            "SECURITY_BALANCE_SHEET",
            "SECURITY_CF_DIRECT",
            "SECURITY_CF_INDIRECT",
            "SECURITY_NOTE"
        ]
    }

    # Initialize registry
    registry = {
        "version": "1.0",
        "last_updated": datetime.now().isoformat(),
        "description": "Metric registry converted from BSC - Mô tả CSDL.xlsx",
        "entity_types": {}
    }

    total_metrics = 0

    # Process each entity type
    for entity, sheets in entity_sheets.items():
        logger.info(f"\nProcessing {entity} entity type...")
        registry["entity_types"][entity] = {}
        entity_metric_count = 0

        for sheet_name in sheets:
            try:
                # Read sheet
                df = pd.read_excel(excel_file, sheet_name=sheet_name)

                # Get prefix for this sheet
                prefix = get_metric_prefix(sheet_name)

                # Filter rows that are actual metrics (have the prefix)
                metrics = df[df['COLUMN_NAME'].str.startswith(prefix, na=False)].copy()

                if len(metrics) == 0:
                    logger.warning(f"  No metrics found in {sheet_name} with prefix {prefix}")
                    continue

                # Get category
                category = get_category(sheet_name)

                # Initialize category if not exists
                if category not in registry["entity_types"][entity]:
                    registry["entity_types"][entity][category] = {}

                # Process each metric
                for _, row in metrics.iterrows():
                    code = row['COLUMN_NAME']

                    # Build metric definition
                    metric_def = {
                        "code": code,
                        "name_vi": str(row['Mô tả']) if pd.notna(row['Mô tả']) else "",
                        "name_en": "",  # TODO: Add English translation if available
                        "data_type": str(row['DATA_TYPE']) if pd.notna(row['DATA_TYPE']) else "NUMBER",
                        "unit": "VND",  # Default to VND for financial data
                        "category": category.lower(),
                        "is_calculated": False,
                        "sheet_name": sheet_name,
                        "entity_type": entity
                    }

                    registry["entity_types"][entity][category][code] = metric_def
                    entity_metric_count += 1
                    total_metrics += 1

                logger.info(f"  {sheet_name}: {len(metrics)} metrics")

            except Exception as e:
                logger.error(f"  Error processing {sheet_name}: {str(e)}")
                continue

        logger.info(f"  Total {entity} metrics: {entity_metric_count}")

    # Add calculated metrics definitions
    logger.info("\nAdding calculated metrics definitions...")
    registry["calculated_metrics"] = {
        "roe": {
            "name_vi": "Tỷ suất sinh lời trên vốn chủ sở hữu",
            "name_en": "Return on Equity",
            "formula": "(net_profit / total_equity) * 100",
            "formula_description": "Net Profit / Total Equity * 100",
            "unit": "%",
            "dependencies": {
                "COMPANY": ["CIS_62", "CBS_270"],
                "BANK": ["BIS_22A", "BBS_400"],
                "INSURANCE": ["IIS_60", "IBS_270"],
                "SECURITY": ["SIS_60", "SBS_270"]
            },
            "entity_types": ["COMPANY", "BANK", "INSURANCE", "SECURITY"]
        },
        "roa": {
            "name_vi": "Tỷ suất sinh lời trên tổng tài sản",
            "name_en": "Return on Assets",
            "formula": "(net_profit / total_assets) * 100",
            "formula_description": "Net Profit / Total Assets * 100",
            "unit": "%",
            "dependencies": {
                "COMPANY": ["CIS_62", "CBS_100"],
                "BANK": ["BIS_22A", "BBS_100"],
                "INSURANCE": ["IIS_60", "IBS_100"],
                "SECURITY": ["SIS_60", "SBS_100"]
            },
            "entity_types": ["COMPANY", "BANK", "INSURANCE", "SECURITY"]
        },
        "gross_margin": {
            "name_vi": "Biên lợi nhuận gộp",
            "name_en": "Gross Profit Margin",
            "formula": "(gross_profit / net_revenue) * 100",
            "formula_description": "Gross Profit / Net Revenue * 100",
            "unit": "%",
            "dependencies": {
                "COMPANY": ["CIS_20", "CIS_10"]
            },
            "entity_types": ["COMPANY"]
        },
        "net_margin": {
            "name_vi": "Biên lợi nhuận ròng",
            "name_en": "Net Profit Margin",
            "formula": "(net_profit / net_revenue) * 100",
            "formula_description": "Net Profit / Net Revenue * 100",
            "unit": "%",
            "dependencies": {
                "COMPANY": ["CIS_62", "CIS_10"],
                "BANK": ["BIS_22A", "BIS_1"],
                "INSURANCE": ["IIS_60", "IIS_01"],  # Fixed: IIS_1 -> IIS_01
                "SECURITY": ["SIS_60", "SIS_10"]
            },
            "entity_types": ["COMPANY", "BANK", "INSURANCE", "SECURITY"]
        },
        "eps": {
            "name_vi": "Lãi cơ bản trên cổ phiếu",
            "name_en": "Earnings Per Share",
            "formula": "(net_profit * 1e9) / (common_shares / 10000)",
            "formula_description": "Net Profit / Common Shares Outstanding",
            "unit": "VND",
            "dependencies": {
                "COMPANY": ["CIS_62", "CBS_411A"],
                "BANK": ["BIS_22A", "BBS_411"],  # Fixed: BBS_411A -> BBS_411
                "INSURANCE": ["IIS_60", "IBS_411"],  # Fixed: IBS_411A -> IBS_411
                "SECURITY": ["SIS_60", "SBS_411"]  # Fixed: SBS_411A -> SBS_411
            },
            "entity_types": ["COMPANY", "BANK", "INSURANCE", "SECURITY"]
        }
    }

    logger.info(f"Added {len(registry['calculated_metrics'])} calculated metric definitions")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("CONVERSION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total raw metrics: {total_metrics}")
    logger.info(f"Total calculated metrics: {len(registry['calculated_metrics'])}")
    logger.info(f"Entity types: {len(registry['entity_types'])}")

    for entity, categories in registry["entity_types"].items():
        entity_total = sum(len(metrics) for metrics in categories.values())
        logger.info(f"  {entity}: {entity_total} metrics across {len(categories)} categories")

    return registry


def save_registry(registry: Dict, output_path: Optional[Path] = None):
    """
    Save registry to JSON file
    
    Saves to both:
    1. New location: config/metadata_registry/metrics/metric_registry.json (primary)
    2. Old location: config/metric_registry.json (backward compatibility)

    Args:
        registry: Registry dictionary
        output_path: Output file path (optional, defaults to new location)
    """
    if output_path is None:
        # Primary location: new structure
        output_path = PROJECT_ROOT / "config" / "metadata_registry" / "metrics" / "metric_registry.json"
    
    # Create directory if not exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to JSON with pretty formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    logger.info(f"\n✅ Metric registry saved to: {output_path}")
    logger.info(f"   File size: {output_path.stat().st_size / 1024:.2f} KB")
    
    # Also save to old location for backward compatibility
    old_path = PROJECT_ROOT / "config" / "metric_registry.json"
    if output_path != old_path:
        with open(old_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        logger.info(f"   Also saved to (backward compatibility): {old_path}")


def main():
    """Main execution"""
    try:
        # Convert Excel to registry
        registry = convert_bsc_excel_to_registry()

        # Save to JSON
        save_registry(registry)

        logger.info("\n" + "=" * 60)
        logger.info("✅ Conversion completed successfully!")
        logger.info("=" * 60)

        # Print sample usage
        logger.info("\nSample usage:")
        logger.info("  from PROCESSORS.core.registries.metric_lookup import MetricRegistry")
        logger.info("  registry = MetricRegistry()")
        logger.info('  metric = registry.get_metric("CIS_62", "COMPANY")')
        logger.info('  results = registry.search_by_name("lợi nhuận")')

    except Exception as e:
        logger.error(f"\n❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
