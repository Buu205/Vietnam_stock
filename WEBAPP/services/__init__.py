"""
Services Layer
==============

Data loading services using DataMappingRegistry for path resolution.

Services extend BaseService to get:
- Automatic path resolution via registry
- Schema validation on data load
- Cache TTL from config
- Consistent error handling

To keep the dashboard lightweight (e.g., when only commodity/macro modules are
needed), we avoid importing optional AI/chat helpers or pymongo-based utilities
at package import time. Import the specific helper you need directly, e.g.:

    from WEBAPP.services.chat_manager import ChatManager

Optional dependencies (openai, pymongo, etc.) are thus only required when the
corresponding submodule is explicitly used.

Usage:
    from WEBAPP.services import BaseService, BankService, CompanyService

    # Using registry-based services
    service = BankService()
    df = service.get_financial_data("ACB", "Quarterly")

    # Get path from registry
    path = service.get_data_path()

    # Check data source info
    info = service.get_data_source_info()
"""

from .base_service import BaseService
from .bank_service import BankService
from .company_service import CompanyService
from .security_service import SecurityService
from .forecast_service import ForecastService
from .sector_service import SectorService
from .technical_service import TechnicalService
from .valuation_service import ValuationService

__all__ = [
    'BaseService',
    'BankService',
    'CompanyService',
    'SecurityService',
    'ForecastService',
    'SectorService',
    'TechnicalService',
    'ValuationService',
]
