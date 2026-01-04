"""
BSC Forecast Processing Module
==============================

Processes BSC Research Forecast Excel data into structured parquet files.

Usage:
    from PROCESSORS.forecast.bsc.bsc_forecast_processor import BSCForecastProcessor

    processor = BSCForecastProcessor()
    result = processor.run()
"""

from .bsc.bsc_forecast_processor import BSCForecastProcessor

__all__ = ['BSCForecastProcessor']
