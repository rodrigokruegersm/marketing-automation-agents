"""
Base Checkout Adapter
Abstract interface for checkout platform integrations
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class PaymentStatus(Enum):
    """Payment/transaction status"""
    APPROVED = "approved"
    PENDING = "pending"
    REFUNDED = "refunded"
    CHARGEBACK = "chargeback"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ProductType(Enum):
    """Type of digital product"""
    COURSE = "course"
    EBOOK = "ebook"
    MEMBERSHIP = "membership"
    SOFTWARE = "software"
    SERVICE = "service"
    PHYSICAL = "physical"
    OTHER = "other"


@dataclass
class Product:
    """
    Product definition from checkout platform.

    Contains pricing information essential for CPP analysis.
    """
    id: str
    name: str
    platform: str  # hotmart, kiwify, stripe, whop

    # Pricing
    price: float  # Main product price
    currency: str = "BRL"

    # Product details
    type: ProductType = ProductType.COURSE
    description: str = ""

    # Funnel association (maps to campaign {TAG})
    funnel_tag: Optional[str] = None

    # Commission/costs
    platform_fee_percent: float = 0.0  # Platform takes X%
    affiliate_commission_percent: float = 0.0

    # Metrics
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Raw data from platform
    raw_data: Dict = field(default_factory=dict)

    @property
    def net_revenue_per_sale(self) -> float:
        """Calculate net revenue after platform fees"""
        fees = self.price * (self.platform_fee_percent / 100)
        affiliate = self.price * (self.affiliate_commission_percent / 100)
        return self.price - fees - affiliate

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'platform': self.platform,
            'price': self.price,
            'currency': self.currency,
            'type': self.type.value,
            'funnel_tag': self.funnel_tag,
            'net_revenue_per_sale': self.net_revenue_per_sale,
            'platform_fee_percent': self.platform_fee_percent,
            'affiliate_commission_percent': self.affiliate_commission_percent
        }


@dataclass
class Offer:
    """
    Specific offer/checkout page for a product.

    A product can have multiple offers (different prices, bundles, etc.)
    """
    id: str
    name: str
    product_id: str
    platform: str

    # Pricing (can differ from main product price)
    price: float
    original_price: Optional[float] = None  # For discounts
    currency: str = "BRL"

    # Offer details
    checkout_url: Optional[str] = None
    is_bump: bool = False
    is_upsell: bool = False
    is_order_bump: bool = False

    # Funnel mapping
    funnel_tag: Optional[str] = None
    funnel_stage: str = "main"  # main, upsell_1, upsell_2, downsell, etc.

    # Tracking
    utm_source: Optional[str] = None
    utm_campaign: Optional[str] = None

    # Metrics
    total_sales: int = 0
    total_revenue: float = 0.0
    conversion_rate: float = 0.0

    raw_data: Dict = field(default_factory=dict)

    @property
    def discount_percent(self) -> float:
        """Calculate discount percentage if original price exists"""
        if self.original_price and self.original_price > 0:
            return ((self.original_price - self.price) / self.original_price) * 100
        return 0.0

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'product_id': self.product_id,
            'platform': self.platform,
            'price': self.price,
            'original_price': self.original_price,
            'discount_percent': self.discount_percent,
            'funnel_tag': self.funnel_tag,
            'funnel_stage': self.funnel_stage,
            'total_sales': self.total_sales,
            'total_revenue': self.total_revenue,
            'is_bump': self.is_bump,
            'is_upsell': self.is_upsell
        }


@dataclass
class Sale:
    """
    Individual sale/transaction from checkout platform.
    """
    id: str
    platform: str

    # Product/offer info
    product_id: str
    product_name: str
    offer_id: Optional[str] = None

    # Transaction details
    amount: float = 0.0
    currency: str = "BRL"
    status: PaymentStatus = PaymentStatus.APPROVED
    payment_method: str = ""

    # Customer
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None

    # Attribution
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None

    # Funnel mapping
    funnel_tag: Optional[str] = None

    # Timestamps
    created_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

    # Commission/fees
    platform_fee: float = 0.0
    affiliate_commission: float = 0.0
    net_amount: float = 0.0

    raw_data: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'platform': self.platform,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'amount': self.amount,
            'status': self.status.value,
            'customer_email': self.customer_email,
            'utm_source': self.utm_source,
            'utm_campaign': self.utm_campaign,
            'funnel_tag': self.funnel_tag,
            'net_amount': self.net_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class CheckoutMetrics:
    """
    Aggregated checkout metrics for analysis.
    """
    platform: str
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

    # Sales metrics
    total_sales: int = 0
    approved_sales: int = 0
    refunded_sales: int = 0
    chargeback_sales: int = 0

    # Revenue
    gross_revenue: float = 0.0
    net_revenue: float = 0.0
    refunded_amount: float = 0.0

    # Product breakdown
    products: Dict[str, Dict] = field(default_factory=dict)
    offers: Dict[str, Dict] = field(default_factory=dict)

    # Funnel breakdown (by {TAG})
    by_funnel: Dict[str, Dict] = field(default_factory=dict)

    # UTM breakdown
    by_utm_source: Dict[str, Dict] = field(default_factory=dict)
    by_utm_campaign: Dict[str, Dict] = field(default_factory=dict)

    # Averages
    average_ticket: float = 0.0
    approval_rate: float = 0.0
    refund_rate: float = 0.0

    def calculate_derived(self):
        """Calculate derived metrics"""
        if self.total_sales > 0:
            self.average_ticket = self.gross_revenue / self.total_sales
            self.approval_rate = (self.approved_sales / self.total_sales) * 100
            self.refund_rate = (self.refunded_sales / self.total_sales) * 100

    def to_dict(self) -> Dict:
        return {
            'platform': self.platform,
            'total_sales': self.total_sales,
            'approved_sales': self.approved_sales,
            'gross_revenue': self.gross_revenue,
            'net_revenue': self.net_revenue,
            'average_ticket': self.average_ticket,
            'approval_rate': self.approval_rate,
            'refund_rate': self.refund_rate,
            'by_funnel': self.by_funnel,
            'by_utm_source': self.by_utm_source
        }


class BaseCheckoutAdapter(ABC):
    """
    Abstract base class for checkout platform integrations.

    All checkout adapters must implement these methods to provide
    consistent data access across platforms.

    Usage:
        class MyPlatformAdapter(BaseCheckoutAdapter):
            def get_products(self):
                # Implementation
                pass
    """

    platform_name: str = "unknown"

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def test_connection(self) -> Dict:
        """Test API connection"""
        pass

    @abstractmethod
    def get_products(self) -> List[Product]:
        """
        Fetch all products from the platform.

        Returns:
            List of Product objects with pricing information
        """
        pass

    @abstractmethod
    def get_product(self, product_id: str) -> Optional[Product]:
        """
        Fetch a specific product by ID.

        Args:
            product_id: Platform-specific product ID

        Returns:
            Product object or None if not found
        """
        pass

    @abstractmethod
    def get_offers(self, product_id: Optional[str] = None) -> List[Offer]:
        """
        Fetch offers/checkout pages.

        Args:
            product_id: Optional filter by product

        Returns:
            List of Offer objects
        """
        pass

    @abstractmethod
    def get_sales(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        product_id: Optional[str] = None,
        status: Optional[PaymentStatus] = None
    ) -> List[Sale]:
        """
        Fetch sales/transactions.

        Args:
            start_date: Filter from this date
            end_date: Filter until this date
            product_id: Filter by product
            status: Filter by payment status

        Returns:
            List of Sale objects
        """
        pass

    @abstractmethod
    def get_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> CheckoutMetrics:
        """
        Get aggregated checkout metrics.

        Args:
            start_date: Start of period
            end_date: End of period

        Returns:
            CheckoutMetrics object with aggregated data
        """
        pass

    def get_revenue_by_funnel(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Get revenue breakdown by funnel tag.

        Returns:
            Dict mapping funnel_tag to total revenue
        """
        metrics = self.get_metrics(start_date, end_date)
        return {
            tag: data.get('revenue', 0)
            for tag, data in metrics.by_funnel.items()
        }

    def get_product_price(self, product_id: str) -> float:
        """
        Get main product price for CPP analysis.

        Args:
            product_id: Product ID

        Returns:
            Product price or 0 if not found
        """
        product = self.get_product(product_id)
        return product.price if product else 0.0

    def calculate_max_cpp(self, product_id: str, target_roas: float = 2.0) -> float:
        """
        Calculate maximum CPP for profitability.

        Args:
            product_id: Product ID
            target_roas: Target ROAS (default 2.0 = 100% profit)

        Returns:
            Maximum CPP to maintain target ROAS
        """
        product = self.get_product(product_id)
        if not product:
            return 0.0

        net_revenue = product.net_revenue_per_sale
        return net_revenue / target_roas

    def is_configured(self) -> bool:
        """Check if adapter is properly configured"""
        return bool(self.api_key)
