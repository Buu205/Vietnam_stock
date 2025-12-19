"""
Services Module
===============

Data access layer for bsc_mcp server.
"""

from bsc_mcp.services.data_loader import DataLoader, get_data_loader

__all__ = ["DataLoader", "get_data_loader"]
