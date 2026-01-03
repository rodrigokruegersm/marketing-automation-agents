"""
Marketing Command Center - Core Module

Multi-client, multi-funnel marketing automation platform.
"""

from .campaign_parser import CampaignParser, ParsedCampaign
from .client_registry import ClientRegistry, Client
from .funnel_registry import FunnelRegistry, Funnel, FunnelType
from .data_aggregator import DataAggregator, AggregatedMetrics, FunnelData, ClientData
from .product_registry import ProductRegistry, FunnelProduct

# Adapters for external platforms
from .adapters.meta_ads import MetaAdsAdapter
from .adapters.hyros import HyrosAdapter

# Checkout platform adapters
from .adapters.checkout import (
    BaseCheckoutAdapter,
    Product,
    Offer,
    Sale,
    CheckoutMetrics,
    PaymentStatus,
    ProductType,
    HotmartAdapter,
    KiwifyAdapter,
    StripeAdapter,
    WhopAdapter,
    ClickFunnelsAdapter,
)

__all__ = [
    # Core modules
    'CampaignParser',
    'ParsedCampaign',
    'ClientRegistry',
    'Client',
    'FunnelRegistry',
    'Funnel',
    'FunnelType',
    'DataAggregator',
    'AggregatedMetrics',
    'FunnelData',
    'ClientData',
    'ProductRegistry',
    'FunnelProduct',
    # Ads Adapters
    'MetaAdsAdapter',
    'HyrosAdapter',
    # Checkout Adapters
    'BaseCheckoutAdapter',
    'Product',
    'Offer',
    'Sale',
    'CheckoutMetrics',
    'PaymentStatus',
    'ProductType',
    'HotmartAdapter',
    'KiwifyAdapter',
    'StripeAdapter',
    'WhopAdapter',
    'ClickFunnelsAdapter',
]

__version__ = '1.0.0'
