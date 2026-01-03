"""
Checkout Platform Adapters
Connectors for payment/checkout platforms to get real product and sales data
"""

from .base import BaseCheckoutAdapter, Product, Offer, Sale, CheckoutMetrics, PaymentStatus, ProductType
from .hotmart import HotmartAdapter
from .kiwify import KiwifyAdapter
from .stripe import StripeAdapter
from .whop import WhopAdapter
from .clickfunnels import ClickFunnelsAdapter

__all__ = [
    # Base
    'BaseCheckoutAdapter',
    'Product',
    'Offer',
    'Sale',
    'CheckoutMetrics',
    'PaymentStatus',
    'ProductType',
    # Adapters
    'HotmartAdapter',
    'KiwifyAdapter',
    'StripeAdapter',
    'WhopAdapter',
    'ClickFunnelsAdapter',
]
