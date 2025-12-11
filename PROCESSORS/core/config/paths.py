"""
Centralized Path Configuration
===============================

All data paths for the stock dashboard system.
"""

from pathlib import Path

# ROOT PATHS
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = PROJECT_ROOT / "DATA"
PROCESSORS_ROOT = PROJECT_ROOT / "PROCESSORS"
CONFIG_ROOT = PROJECT_ROOT / "CONFIG"
WEBAPP_ROOT = PROJECT_ROOT / "WEBAPP"

# Raw data paths
RAW_DATA = DATA_ROOT / "raw"
RAW_OHLCV = RAW_DATA / "ohlcv"
RAW_FUNDAMENTAL = RAW_DATA / "fundamental" / "csv"
RAW_COMMODITY = RAW_DATA / "commodity"
RAW_MACRO = RAW_DATA / "macro"

# Processed data paths
PROCESSED_DATA = DATA_ROOT / "processed"
PROCESSED_FUNDAMENTAL = PROCESSED_DATA / "fundamental"
PROCESSED_TECHNICAL = PROCESSED_DATA / "technical"
PROCESSED_VALUATION = PROCESSED_DATA / "valuation"

# Metadata paths
METADATA = DATA_ROOT / "metadata"
METRIC_REGISTRY = METADATA / "metric_registry.json"
SECTOR_REGISTRY = METADATA / "sector_industry_registry.json"

# Schemas
SCHEMAS = DATA_ROOT / "schemas"
SCHEMA_FUNDAMENTAL = SCHEMAS / "fundamental.json"
SCHEMA_TECHNICAL = SCHEMAS / "technical.json"
SCHEMA_OHLCV = SCHEMAS / "ohlcv.json"

# Helper functions
def get_fundamental_path(entity_type: str) -> Path:
    """Get fundamental data path for entity type."""
    entity_map = {
        "company": PROCESSED_FUNDAMENTAL / "company",
        "bank": PROCESSED_FUNDAMENTAL / "bank",
        "insurance": PROCESSED_FUNDAMENTAL / "insurance",
        "security": PROCESSED_FUNDAMENTAL / "security",
    }
    return entity_map[entity_type.lower()]
