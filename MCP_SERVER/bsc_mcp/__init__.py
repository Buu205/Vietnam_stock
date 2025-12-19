"""
bsc_mcp - MCP Server for Vietnamese Stock Market Data
=========================================================

This package provides an MCP (Model Context Protocol) server that enables
AI agents like Claude to query Vietnamese stock market data.

Features:
---------
- Query company/bank/insurance/security financial metrics
- Get historical PE/PB/EV-EBITDA valuation data
- Access technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Search BSC analyst forecasts and ratings
- Analyze sector FA/TA scores and signals
- Read macro/commodity data (gold, oil, FX, interest rates)

Quick Start:
-----------
1. Configure .mcp.json in your project root
2. Start Claude Code in the project directory
3. Ask questions like "ROE của VCB là bao nhiêu?"

Author: Buu Phan
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Buu Phan"

__all__ = ["__version__"]
