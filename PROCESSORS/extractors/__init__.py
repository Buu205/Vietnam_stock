"""
Data Extractors
===============

Centralized data loading for Vietnam Dashboard.
"""

from .csv_loader import CSVLoader, load_csv

__all__ = [
    "CSVLoader",
    "load_csv",
]
