"""
API Clients
===========

Centralized API clients for external data sources.

Clients:
- WiChartClient: Exchange rates, interest rates, deposit rates, commodities
- SimplizeClient: Government bonds, rubber, WMP milk
- FireantClient: Share outstanding, fundamentals, financial statements
- VNStockClient: Wrapper for vnstock_data library commodities

Usage:
    from PROCESSORS.api.clients import WiChartClient, SimplizeClient, FireantClient, VNStockClient

    # WiChart - no auth needed
    wichart = WiChartClient()
    fx_rates = wichart.get_exchange_rates()

    # Simplize - needs token from config
    simplize = SimplizeClient()
    bonds = simplize.get_gov_bond_5y()

    # Fireant - needs token from config
    fireant = FireantClient()
    shares = fireant.get_share_outstanding("VNM")

    # VNStock - wrapper for vnstock_data library
    vnstock = VNStockClient()
    gold = vnstock.get_commodity("gold_vn")
"""

from PROCESSORS.api.clients.wichart_client import WiChartClient
from PROCESSORS.api.clients.simplize_client import SimplizeClient
from PROCESSORS.api.clients.fireant_client import FireantClient
from PROCESSORS.api.clients.vnstock_client import VNStockClient

__all__ = [
    "WiChartClient",
    "SimplizeClient",
    "FireantClient",
    "VNStockClient",
]
