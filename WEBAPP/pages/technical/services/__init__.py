"""
Technical Dashboard Services
============================

Data services for the TA Dashboard.

Services:
- TADashboardService: Unified singleton service with caching
- get_ta_service: Factory function for singleton access
"""

from .ta_dashboard_service import TADashboardService, get_ta_service

__all__ = [
    'TADashboardService',
    'get_ta_service',
]
