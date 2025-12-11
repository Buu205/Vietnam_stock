"""News data pipeline package."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_NEWS_DIR = PROJECT_ROOT / "data_warehouse" / "raw" / "news"
PROCESSED_NEWS_DIR = PROJECT_ROOT / "calculated_results" / "news"

__all__ = ["PROJECT_ROOT", "RAW_NEWS_DIR", "PROCESSED_NEWS_DIR"]

