"""
Daily Pipeline Scripts
=======================

Individual daily update scripts for each data domain.

Scripts:
    - daily_ohlcv_update.py: OHLCV market data
    - daily_ta_complete.py: Technical analysis indicators
    - daily_macro_commodity.py: Macro & commodity data
    - daily_valuation.py: Stock valuation (PE/PB/EV-EBITDA)
    - daily_sector_analysis.py: Sector analysis & scoring
    - daily_bsc_forecast.py: BSC forecast data

Usage:
    # Run all daily updates via master script
    python3 PROCESSORS/pipelines/run_all_daily_updates.py

    # Run individual scripts
    python3 PROCESSORS/pipelines/daily/daily_ohlcv_update.py
    python3 PROCESSORS/pipelines/daily/daily_valuation.py
"""
