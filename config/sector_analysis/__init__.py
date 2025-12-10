"""
Sector Analysis Configuration Module
==================================

This module provides configuration management for FA+TA sector analysis.

Components:
- ConfigManager: Manages user preferences and configuration
"""

from .config_manager import ConfigManager, get_config, update_weights

__all__ = [
    "ConfigManager",
    "get_config",
    "update_weights"
]