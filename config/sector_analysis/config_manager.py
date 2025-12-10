"""
Configuration Manager for Sector Analysis
=====================================

Manages user preferences and configuration for FA+TA sector analysis.
Handles loading, saving, and merging of default and user configs.

Author: AI Assistant
Date: 2025-12-09
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import os

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manage user preferences and configuration for sector analysis.
    
    Handles loading and saving of configuration files,
    merging defaults with user overrides, and providing
    the active configuration for use by other components.
    """
    
    def __init__(self, user_config_file: Optional[str] = None):
        """
        Initialize with optional user config file path.
        
        Args:
            user_config_file: Path to user's configuration file
        """
        # Set paths
        project_root = Path(__file__).resolve().parents[2]
        self.config_dir = project_root / "CONFIG" / "sector_analysis"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.default_config_file = self.config_dir / "default_weights.json"
        self.indicators_config_file = self.config_dir / "indicators_config.json"
        
        if user_config_file:
            self.user_config_file = Path(user_config_file)
        else:
            self.user_config_file = self.config_dir / "user_preferences.json"
        
        # Initialize configuration
        self.default_config = self._load_default_config()
        self.indicators_config = self._load_indicators_config()
        self.user_config = self._load_user_config()
        self.active_config = self._merge_configs()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """
        Load default configuration.
        
        Returns:
            Dictionary with default configuration
        """
        # Create default config if it doesn't exist
        if not self.default_config_file.exists():
            self._create_default_config()
        
        try:
            with open(self.default_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading default config: {e}")
            return {}
    
    def _load_indicators_config(self) -> Dict[str, Any]:
        """
        Load indicators configuration.
        
        Returns:
            Dictionary with indicators configuration
        """
        # Create indicators config if it doesn't exist
        if not self.indicators_config_file.exists():
            self._create_indicators_config()
        
        try:
            with open(self.indicators_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading indicators config: {e}")
            return {}
    
    def _load_user_config(self) -> Dict[str, Any]:
        """
        Load user configuration.
        
        Returns:
            Dictionary with user configuration
        """
        # Return empty dict if user config doesn't exist
        if not self.user_config_file.exists():
            return {}
        
        try:
            with open(self.user_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading user config: {e}")
            return {}
    
    def _merge_configs(self) -> Dict[str, Any]:
        """
        Merge default configuration with user overrides.
        
        Returns:
            Merged configuration dictionary
        """
        # Start with default config
        merged = {}
        
        # Deep copy default config sections
        for section, values in self.default_config.items():
            if isinstance(values, dict):
                merged[section] = values.copy()
            else:
                merged[section] = values
        
        # Merge indicators config
        if not merged.get("indicators"):
            merged["indicators"] = {}
        merged["indicators"].update(self.indicators_config)
        
        # Merge user config (deep merge for nested dicts)
        for section, values in self.user_config.items():
            if section in merged and isinstance(merged[section], dict) and isinstance(values, dict):
                # Deep merge for nested dictionaries
                for key, value in values.items():
                    merged[section][key] = value
            else:
                merged[section] = values
        
        return merged
    
    def _create_default_config(self) -> None:
        """
        Create default configuration file with sensible defaults.
        """
        default_config = {
            "fa_weights": {
                "revenue_growth": 0.2,
                "gross_margin": 0.15,
                "operating_margin": 0.15,
                "roe": 0.2,
                "roa": 0.1,
                "debt_to_equity": 0.1,
                "other": 0.1
            },
            "ta_weights": {
                "ma_alignment": 0.2,
                "rsi_momentum": 0.15,
                "volume_trend": 0.15,
                "macd_signal": 0.1,
                "bollinger_position": 0.1,
                "sector_strength": 0.2,
                "other": 0.1
            },
            "composite_weights": {
                "fundamental": 0.6,
                "technical": 0.4
            },
            "display": {
                "default_timeframe": "latest",
                "chart_height": 500,
                "chart_colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
                "show_data_labels": True,
                "animation_duration": 1000
            },
            "analysis": {
                "top_performers_count": 5,
                "risk_threshold": 50,
                "min_companies_per_sector": 3
            }
        }
        
        try:
            with open(self.default_config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default config at {self.default_config_file}")
        except Exception as e:
            logger.error(f"Error creating default config: {e}")
    
    def _create_indicators_config(self) -> None:
        """
        Create indicators configuration file.
        """
        indicators_config = {
            "enabled": {
                "fundamental": {
                    "revenue_growth": True,
                    "gross_margin": True,
                    "operating_margin": True,
                    "roe": True,
                    "roa": True,
                    "debt_to_equity": True
                },
                "technical": {
                    "ma_20": True,
                    "ma_50": True,
                    "ma_100": True,
                    "ma_200": True,
                    "rsi_14": True,
                    "macd": True,
                    "bollinger": True,
                    "atr": True,
                    "momentum": True,
                    "volume_trend": True
                },
                "valuation": {
                    "pe_ratio": True,
                    "pb_ratio": True,
                    "ps_ratio": True,
                    "ev_ebitda": True
                }
            },
            "alerts": {
                "price_movement": True,
                "volume_spike": True,
                "rsi_divergence": True,
                "ma_crossover": True,
                "sector_momentum_change": True,
                "valuation_extreme": True
            },
            "thresholds": {
                "rsi_oversold": 30,
                "rsi_overbought": 70,
                "volume_spike_multiplier": 2.0,
                "price_spike_percent": 5.0,
                "ma_signal_period": 10,
                "low_pe_threshold": 10,
                "high_pe_threshold": 25
            },
            "sector_specific": {
                "banking": {
                    "focus_metrics": ["nim", "cir", "npl_ratio"],
                    "benchmark_metrics": ["roe", "roa"]
                },
                "insurance": {
                    "focus_metrics": ["combined_ratio", "loss_ratio"],
                    "benchmark_metrics": ["roe", "premium_growth"]
                },
                "securities": {
                    "focus_metrics": ["brokerage_revenue", "assets_under_management"],
                    "benchmark_metrics": ["roe", "market_cap_growth"]
                }
            }
        }
        
        try:
            with open(self.indicators_config_file, 'w', encoding='utf-8') as f:
                json.dump(indicators_config, f, indent=2)
            logger.info(f"Created indicators config at {self.indicators_config_file}")
        except Exception as e:
            logger.error(f"Error creating indicators config: {e}")
    
    def get_active_config(self) -> Dict[str, Any]:
        """
        Get the currently active configuration.
        
        Returns:
            Merged configuration dictionary
        """
        return self.active_config
    
    def save_user_config(self, config: Dict[str, Any]) -> bool:
        """
        Save user configuration.
        
        Args:
            config: Configuration dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            # Update internal state
            self.user_config = config
            self.active_config = self._merge_configs()
            
            logger.info(f"Saved user config to {self.user_config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving user config: {e}")
            return False
    
    def update_user_config(self, updates: Dict[str, Any]) -> bool:
        """
        Update user configuration with new values.
        
        Args:
            updates: Dictionary with configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        # Deep merge with existing user config
        new_config = self._deep_merge(self.user_config.copy(), updates)
        
        return self.save_user_config(new_config)
    
    def reset_user_config(self) -> bool:
        """
        Reset user configuration to defaults.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.user_config_file.exists():
                self.user_config_file.unlink()
            
            # Update internal state
            self.user_config = {}
            self.active_config = self._merge_configs()
            
            logger.info("Reset user config to defaults")
            return True
        except Exception as e:
            logger.error(f"Error resetting user config: {e}")
            return False
    
    def get_weights(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get weight configuration.
        
        Args:
            category: Optional category filter ('fa', 'ta', 'composite')
            
        Returns:
            Dictionary with weight configuration
        """
        weights = self.active_config.get("weights", {})
        
        if category:
            return weights.get(category, {})
        
        return weights
    
    def update_weights(self, fa_weights: Optional[Dict[str, float]] = None,
                    ta_weights: Optional[Dict[str, float]] = None,
                    composite_weights: Optional[Dict[str, float]] = None) -> bool:
        """
        Update weight configuration.
        
        Args:
            fa_weights: Fundamental weights updates
            ta_weights: Technical weights updates
            composite_weights: Composite weights updates
            
        Returns:
            True if successful, False otherwise
        """
        updates = {}
        
        if fa_weights:
            updates["fa_weights"] = fa_weights
        
        if ta_weights:
            updates["ta_weights"] = ta_weights
        
        if composite_weights:
            updates["composite_weights"] = composite_weights
        
        if not updates:
            return True  # Nothing to update
        
        return self.update_user_config({"weights": updates})
    
    def get_enabled_indicators(self) -> Dict[str, Any]:
        """
        Get enabled indicators configuration.
        
        Returns:
            Dictionary with enabled indicators
        """
        return self.active_config.get("indicators", {}).get("enabled", {})
    
    def update_enabled_indicators(self, fundamental: Optional[Dict[str, bool]] = None,
                               technical: Optional[Dict[str, bool]] = None,
                               valuation: Optional[Dict[str, bool]] = None) -> bool:
        """
        Update enabled indicators configuration.
        
        Args:
            fundamental: Fundamental indicators updates
            technical: Technical indicators updates
            valuation: Valuation indicators updates
            
        Returns:
            True if successful, False otherwise
        """
        updates = {}
        
        if fundamental:
            updates["fundamental"] = fundamental
        
        if technical:
            updates["technical"] = technical
        
        if valuation:
            updates["valuation"] = valuation
        
        if not updates:
            return True  # Nothing to update
        
        # Get current enabled indicators
        current_enabled = self.get_enabled_indicators()
        new_enabled = current_enabled.copy()
        
        # Update with new values
        for category, indicators in updates.items():
            if category in new_enabled:
                new_enabled[category].update(indicators)
            else:
                new_enabled[category] = indicators
        
        return self.update_user_config({"indicators": {"enabled": new_enabled}})
    
    def get_display_config(self) -> Dict[str, Any]:
        """
        Get display configuration.
        
        Returns:
            Dictionary with display configuration
        """
        return self.active_config.get("display", {})
    
    def update_display_config(self, updates: Dict[str, Any]) -> bool:
        """
        Update display configuration.
        
        Args:
            updates: Display configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        if not updates:
            return True  # Nothing to update
        
        return self.update_user_config({"display": updates})
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """
        Get analysis configuration.
        
        Returns:
            Dictionary with analysis configuration
        """
        return self.active_config.get("analysis", {})
    
    def update_analysis_config(self, updates: Dict[str, Any]) -> bool:
        """
        Update analysis configuration.
        
        Args:
            updates: Analysis configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        if not updates:
            return True  # Nothing to update
        
        return self.update_user_config({"analysis": updates})
    
    def get_alert_config(self) -> Dict[str, Any]:
        """
        Get alert configuration.
        
        Returns:
            Dictionary with alert configuration
        """
        return self.active_config.get("indicators", {}).get("alerts", {})
    
    def update_alert_config(self, updates: Dict[str, Any]) -> bool:
        """
        Update alert configuration.
        
        Args:
            updates: Alert configuration updates
            
        Returns:
            True if successful, False otherwise
        """
        if not updates:
            return True  # Nothing to update
        
        # Get current alerts
        current_alerts = self.get_alert_config()
        new_alerts = current_alerts.copy()
        new_alerts.update(updates)
        
        return self.update_user_config({"indicators": {"alerts": new_alerts}})
    
    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            updates: Updates dictionary
            
        Returns:
            Deep merged dictionary
        """
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def export_config(self, file_path: str) -> bool:
        """
        Export active configuration to a file.
        
        Args:
            file_path: Path to export configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.active_config, f, indent=2)
            logger.info(f"Exported configuration to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting config: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """
        Import configuration from a file.
        
        Args:
            file_path: Path to import configuration from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            return self.save_user_config(imported_config)
        except Exception as e:
            logger.error(f"Error importing config: {e}")
            return False


# Convenience function for quick config access
def get_config(user_config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick function to get active configuration.
    
    Args:
        user_config_file: Optional path to user config file
        
    Returns:
        Active configuration dictionary
    """
    config_manager = ConfigManager(user_config_file)
    return config_manager.get_active_config()


# Convenience function for quick weights update
def update_weights(fa_weights: Optional[Dict[str, float]] = None,
                ta_weights: Optional[Dict[str, float]] = None,
                composite_weights: Optional[Dict[str, float]] = None,
                user_config_file: Optional[str] = None) -> bool:
    """
    Quick function to update weights.
    
    Args:
        fa_weights: Fundamental weights updates
        ta_weights: Technical weights updates
        composite_weights: Composite weights updates
        user_config_file: Optional path to user config file
        
    Returns:
        True if successful, False otherwise
    """
    config_manager = ConfigManager(user_config_file)
    return config_manager.update_weights(fa_weights, ta_weights, composite_weights)