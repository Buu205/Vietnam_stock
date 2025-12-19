"""
API Configuration
=================

Load and manage API configuration from JSON files and environment variables.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


def find_project_root() -> Path:
    """Find project root directory."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if current.name in ["Vietnam_dashboard", "stock_dashboard"]:
            return current
        if (current / "DATA").exists() and (current / "PROCESSORS").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent.parent


@dataclass
class EndpointConfig:
    """Configuration for a single API endpoint."""

    base_url: str
    endpoints: Dict[str, str]
    timeout_seconds: int = 30
    rate_limit_per_minute: int = 60
    max_retries: int = 3


class APIConfig:
    """
    API Configuration Manager.

    Loads configuration from:
    1. config/api/api_endpoints.json - Endpoint definitions
    2. config/api/api_credentials.json - Credentials (gitignored)
    3. Environment variables (override)

    Usage:
        config = APIConfig()
        simplize_token = config.get_credential("simplize", "api_token")
        endpoints = config.get_endpoint_config("simplize")
    """

    def __init__(self, project_root: Path = None):
        """
        Initialize API configuration.

        Args:
            project_root: Project root directory. Auto-detected if not provided.
        """
        self.project_root = project_root or find_project_root()
        self.config_dir = self.project_root / "config" / "api"

        self._endpoints: Dict[str, Any] = {}
        self._credentials: Dict[str, Any] = {}

        self._load_endpoints()
        self._load_credentials()

        logger.info(f"API config loaded from {self.config_dir}")

    def _load_endpoints(self):
        """Load endpoint configuration from JSON file."""
        endpoints_file = self.config_dir / "api_endpoints.json"

        if endpoints_file.exists():
            try:
                with open(endpoints_file, "r", encoding="utf-8") as f:
                    self._endpoints = json.load(f)
                logger.info(f"Loaded {len(self._endpoints)} API endpoint configs")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse endpoints JSON: {e}")
        else:
            logger.warning(f"Endpoints file not found: {endpoints_file}")

    def _load_credentials(self):
        """Load credentials from JSON file or environment."""
        credentials_file = self.config_dir / "api_credentials.json"

        # Load from file if exists
        if credentials_file.exists():
            try:
                with open(credentials_file, "r", encoding="utf-8") as f:
                    self._credentials = json.load(f)
                logger.info("Loaded API credentials from file")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse credentials JSON: {e}")

        # Environment variables override file values
        self._load_credentials_from_env()

    def _load_credentials_from_env(self):
        """Load credentials from environment variables."""
        env_mappings = {
            "SIMPLIZE_API_TOKEN": ("simplize", "api_token"),
            "SIMPLIZE_JSESSIONID": ("simplize", "jsessionid"),
            "FIREANT_BEARER_TOKEN": ("fireant", "bearer_token"),
            "WICHART_API_KEY": ("wichart", "api_key"),
        }

        for env_var, (api_name, key) in env_mappings.items():
            value = os.environ.get(env_var)
            if value:
                if api_name not in self._credentials:
                    self._credentials[api_name] = {}
                self._credentials[api_name][key] = value
                logger.debug(f"Loaded {api_name}.{key} from environment")

    def get_credential(self, api_name: str, key: str) -> Optional[str]:
        """
        Get credential value.

        Args:
            api_name: API name (e.g., "simplize", "fireant")
            key: Credential key (e.g., "api_token", "bearer_token")

        Returns:
            Credential value or None if not found
        """
        api_creds = self._credentials.get(api_name, {})
        return api_creds.get(key)

    def get_credentials(self, api_name: str) -> Optional[Dict[str, str]]:
        """
        Get all credentials for an API.

        Args:
            api_name: API name (e.g., "simplize", "fireant")

        Returns:
            Dictionary of credentials or None if not found
        """
        return self._credentials.get(api_name)

    def get_endpoint_config(self, api_name: str) -> Optional[EndpointConfig]:
        """
        Get endpoint configuration for an API.

        Args:
            api_name: API name

        Returns:
            EndpointConfig or None if not found
        """
        config = self._endpoints.get(api_name)
        if not config:
            return None

        return EndpointConfig(
            base_url=config.get("base_url", ""),
            endpoints=config.get("endpoints", {}),
            timeout_seconds=config.get("timeout_seconds", 30),
            rate_limit_per_minute=config.get("rate_limit_per_minute", 60),
            max_retries=config.get("max_retries", 3),
        )

    def get_all_api_names(self) -> list:
        """Get list of all configured API names."""
        return list(self._endpoints.keys())

    def is_configured(self, api_name: str) -> bool:
        """
        Check if API is fully configured (endpoints + credentials if required).

        Args:
            api_name: API name

        Returns:
            True if configured, False otherwise
        """
        if api_name not in self._endpoints:
            return False

        # Check if credentials are required and present
        api_config = self._endpoints[api_name]
        requires_auth = api_config.get("requires_auth", False)

        if requires_auth and api_name not in self._credentials:
            return False

        return True

    def reload(self):
        """Reload configuration from files."""
        self._endpoints = {}
        self._credentials = {}
        self._load_endpoints()
        self._load_credentials()
        logger.info("API configuration reloaded")


# Singleton instance
_api_config: Optional[APIConfig] = None


def get_api_config() -> APIConfig:
    """
    Get global APIConfig singleton instance.

    Returns:
        APIConfig instance
    """
    global _api_config
    if _api_config is None:
        _api_config = APIConfig()
    return _api_config
