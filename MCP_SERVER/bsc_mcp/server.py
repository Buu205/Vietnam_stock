#!/usr/bin/env python3
"""
MCP Server Entry Point
======================

Main entry point for the bsc_mcp MCP server.
This file initializes the FastMCP server and registers all tools.

Running the server:
------------------
The server is typically started by Claude/Cursor automatically based on .mcp.json config.
You can also run it manually for testing:

    $ cd MCP_SERVER
    $ python -m bsc_mcp.server

Usage with Claude Code:
-----------------------
1. Create .mcp.json in your project root
2. Start Claude Code in the project directory
3. Ask questions about Vietnamese stocks
4. Claude will automatically use the tools

Author: Buu Phan
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# Create FastMCP Server Instance
# =============================================================================

mcp = FastMCP(
    name="bsc_mcp",
)

# =============================================================================
# Register Tools
# =============================================================================

logger.info("Registering tools...")

from bsc_mcp.tools import discovery_tools
from bsc_mcp.tools import fundamental_tools
from bsc_mcp.tools import technical_tools
from bsc_mcp.tools import valuation_tools
from bsc_mcp.tools import forecast_tools
from bsc_mcp.tools import sector_tools
from bsc_mcp.tools import macro_tools

# Register all tools with the server
discovery_tools.register(mcp)
logger.info("Discovery tools registered (5 tools)")

fundamental_tools.register(mcp)
logger.info("Fundamental tools registered (5 tools)")

technical_tools.register(mcp)
logger.info("Technical tools registered (4 tools)")

valuation_tools.register(mcp)
logger.info("Valuation tools registered (5 tools)")

forecast_tools.register(mcp)
logger.info("Forecast tools registered (3 tools)")

sector_tools.register(mcp)
logger.info("Sector tools registered (3 tools)")

macro_tools.register(mcp)
logger.info("Macro tools registered (3 tools)")

logger.info("All 28 tools registered successfully!")

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    logger.info("Starting bsc_mcp server...")
    logger.info(f"Project root: {parent_dir}")
    mcp.run()
