"""
Product Registry
Central registry for products, offers, and their funnel associations
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from .adapters.checkout.base import Product, Offer, BaseCheckoutAdapter


@dataclass
class FunnelProduct:
    """
    Product configuration with funnel association.

    Maps products from checkout platforms to campaign funnels.
    """
    id: str
    name: str
    platform: str  # hotmart, kiwify, stripe, whop
    platform_product_id: str

    # Pricing
    price: float
    currency: str = "BRL"

    # Funnel mapping
    funnel_tag: str = ""  # Maps to {TAG} in campaign names

    # Funnel position
    funnel_position: str = "main"  # main, upsell_1, downsell, order_bump

    # Product economics
    cost_of_goods: float = 0.0  # For physical products
    fulfillment_cost: float = 0.0
    platform_fee_percent: float = 0.0
    affiliate_commission_percent: float = 0.0

    # LTV data for optimization
    average_ltv: float = 0.0  # Customer lifetime value
    ltv_months: int = 12  # LTV calculation period

    # Thresholds for optimization
    target_cpp: Optional[float] = None  # Maximum acceptable CPP
    target_roas: float = 2.0  # Minimum acceptable ROAS
    breakeven_cpp: Optional[float] = None  # Calculated breakeven

    # Offers/variations
    offers: List[Dict] = field(default_factory=list)

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Calculate derived values"""
        self._calculate_breakeven()

    def _calculate_breakeven(self):
        """Calculate breakeven CPP based on product economics"""
        net_revenue = self.price * (1 - self.platform_fee_percent / 100)
        net_revenue -= self.price * (self.affiliate_commission_percent / 100)
        net_revenue -= self.cost_of_goods
        net_revenue -= self.fulfillment_cost

        self.breakeven_cpp = net_revenue

        # Set target CPP if not specified (50% of breakeven for 2x ROAS)
        if self.target_cpp is None:
            self.target_cpp = net_revenue / self.target_roas

    @property
    def net_revenue_per_sale(self) -> float:
        """Calculate net revenue per sale"""
        net = self.price * (1 - self.platform_fee_percent / 100)
        net -= self.price * (self.affiliate_commission_percent / 100)
        net -= self.cost_of_goods
        net -= self.fulfillment_cost
        return net

    def get_max_cpp_for_roas(self, target_roas: float) -> float:
        """Calculate maximum CPP for a given ROAS target"""
        return self.net_revenue_per_sale / target_roas

    def evaluate_cpp(self, current_cpp: float) -> str:
        """Evaluate current CPP against thresholds"""
        if current_cpp <= 0:
            return "no_data"

        if self.target_cpp and current_cpp <= self.target_cpp:
            return "excellent"
        elif self.breakeven_cpp and current_cpp <= self.breakeven_cpp:
            return "good"
        elif self.breakeven_cpp and current_cpp <= self.breakeven_cpp * 1.2:
            return "warning"
        else:
            return "critical"

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'platform': self.platform,
            'platform_product_id': self.platform_product_id,
            'price': self.price,
            'currency': self.currency,
            'funnel_tag': self.funnel_tag,
            'funnel_position': self.funnel_position,
            'net_revenue_per_sale': self.net_revenue_per_sale,
            'target_cpp': self.target_cpp,
            'target_roas': self.target_roas,
            'breakeven_cpp': self.breakeven_cpp,
            'average_ltv': self.average_ltv,
            'offers': self.offers
        }


class ProductRegistry:
    """
    Central registry for products across all checkout platforms.

    Usage:
        registry = ProductRegistry()

        # Load client products
        registry.load_client_products("brez-scales")

        # Get product for funnel
        product = registry.get_product_for_funnel("VSL_CHALLENGE")

        # Calculate max CPP
        max_cpp = product.get_max_cpp_for_roas(2.5)

        # Sync from checkout platform
        registry.sync_from_platform(hotmart_adapter)
    """

    def __init__(self, base_path: str = "clients"):
        self.base_path = Path(base_path)
        self.products: Dict[str, FunnelProduct] = {}
        self.by_funnel: Dict[str, List[FunnelProduct]] = {}
        self.by_platform: Dict[str, List[FunnelProduct]] = {}

    def load_client_products(self, client_slug: str) -> List[FunnelProduct]:
        """
        Load products configuration for a client.

        Args:
            client_slug: Client directory name (e.g., "brez-scales")

        Returns:
            List of FunnelProduct objects
        """
        products_path = self.base_path / client_slug / "products"

        if not products_path.exists():
            products_path.mkdir(parents=True, exist_ok=True)
            return []

        products = []

        for yaml_file in products_path.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                if data:
                    product = self._parse_product_config(data)
                    products.append(product)
                    self._index_product(product)

            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")

        return products

    def _parse_product_config(self, data: Dict) -> FunnelProduct:
        """Parse product configuration from YAML"""
        product_data = data.get('product', data)

        return FunnelProduct(
            id=product_data.get('id', ''),
            name=product_data.get('name', ''),
            platform=product_data.get('platform', ''),
            platform_product_id=product_data.get('platform_product_id', ''),
            price=float(product_data.get('price', 0)),
            currency=product_data.get('currency', 'BRL'),
            funnel_tag=product_data.get('funnel_tag', ''),
            funnel_position=product_data.get('funnel_position', 'main'),
            cost_of_goods=float(product_data.get('cost_of_goods', 0)),
            fulfillment_cost=float(product_data.get('fulfillment_cost', 0)),
            platform_fee_percent=float(product_data.get('platform_fee_percent', 0)),
            affiliate_commission_percent=float(product_data.get('affiliate_commission_percent', 0)),
            average_ltv=float(product_data.get('average_ltv', 0)),
            ltv_months=int(product_data.get('ltv_months', 12)),
            target_cpp=product_data.get('target_cpp'),
            target_roas=float(product_data.get('target_roas', 2.0)),
            offers=product_data.get('offers', [])
        )

    def _index_product(self, product: FunnelProduct):
        """Index product for quick lookup"""
        self.products[product.id] = product

        # Index by funnel
        if product.funnel_tag:
            if product.funnel_tag not in self.by_funnel:
                self.by_funnel[product.funnel_tag] = []
            self.by_funnel[product.funnel_tag].append(product)

        # Index by platform
        if product.platform:
            if product.platform not in self.by_platform:
                self.by_platform[product.platform] = []
            self.by_platform[product.platform].append(product)

    def get_product(self, product_id: str) -> Optional[FunnelProduct]:
        """Get product by ID"""
        return self.products.get(product_id)

    def get_product_for_funnel(self, funnel_tag: str, position: str = "main") -> Optional[FunnelProduct]:
        """
        Get main product for a funnel.

        Args:
            funnel_tag: Funnel tag (e.g., "VSL_CHALLENGE")
            position: Funnel position (main, upsell_1, etc.)

        Returns:
            FunnelProduct or None
        """
        funnel_products = self.by_funnel.get(funnel_tag, [])

        for product in funnel_products:
            if product.funnel_position == position:
                return product

        # Return first product if position not found
        return funnel_products[0] if funnel_products else None

    def get_products_for_funnel(self, funnel_tag: str) -> List[FunnelProduct]:
        """Get all products in a funnel"""
        return self.by_funnel.get(funnel_tag, [])

    def get_funnel_total_value(self, funnel_tag: str) -> float:
        """Calculate total potential value of funnel"""
        products = self.get_products_for_funnel(funnel_tag)
        return sum(p.price for p in products)

    def get_max_cpp_for_funnel(self, funnel_tag: str, target_roas: float = 2.0) -> float:
        """
        Calculate maximum CPP for a funnel considering all products.

        Args:
            funnel_tag: Funnel tag
            target_roas: Target ROAS

        Returns:
            Maximum CPP for profitability
        """
        products = self.get_products_for_funnel(funnel_tag)

        if not products:
            return 0.0

        # Use main product for base calculation
        main_product = self.get_product_for_funnel(funnel_tag, "main")

        if main_product:
            return main_product.get_max_cpp_for_roas(target_roas)

        # Fallback: average of all products
        total_net_revenue = sum(p.net_revenue_per_sale for p in products)
        return total_net_revenue / len(products) / target_roas

    def sync_from_platform(
        self,
        adapter: BaseCheckoutAdapter,
        funnel_mapping: Optional[Dict[str, str]] = None
    ) -> List[FunnelProduct]:
        """
        Sync products from a checkout platform.

        Args:
            adapter: Checkout platform adapter
            funnel_mapping: Optional dict mapping product_id to funnel_tag

        Returns:
            List of synced FunnelProduct objects
        """
        funnel_mapping = funnel_mapping or {}
        synced = []

        try:
            platform_products = adapter.get_products()

            for product in platform_products:
                funnel_product = FunnelProduct(
                    id=f"{adapter.platform_name}_{product.id}",
                    name=product.name,
                    platform=adapter.platform_name,
                    platform_product_id=product.id,
                    price=product.price,
                    currency=product.currency,
                    funnel_tag=funnel_mapping.get(product.id, product.funnel_tag or ''),
                    platform_fee_percent=product.platform_fee_percent,
                    affiliate_commission_percent=product.affiliate_commission_percent
                )

                self._index_product(funnel_product)
                synced.append(funnel_product)

        except Exception as e:
            print(f"Error syncing from {adapter.platform_name}: {e}")

        return synced

    def save_product(self, client_slug: str, product: FunnelProduct):
        """Save product configuration to YAML"""
        products_path = self.base_path / client_slug / "products"
        products_path.mkdir(parents=True, exist_ok=True)

        filepath = products_path / f"{product.id}.yaml"

        config = {
            'product': {
                'id': product.id,
                'name': product.name,
                'platform': product.platform,
                'platform_product_id': product.platform_product_id,
                'price': product.price,
                'currency': product.currency,
                'funnel_tag': product.funnel_tag,
                'funnel_position': product.funnel_position,
                'cost_of_goods': product.cost_of_goods,
                'fulfillment_cost': product.fulfillment_cost,
                'platform_fee_percent': product.platform_fee_percent,
                'affiliate_commission_percent': product.affiliate_commission_percent,
                'average_ltv': product.average_ltv,
                'ltv_months': product.ltv_months,
                'target_cpp': product.target_cpp,
                'target_roas': product.target_roas,
                'offers': product.offers
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    def get_optimization_thresholds(self, funnel_tag: str) -> Dict[str, Any]:
        """
        Get optimization thresholds for a funnel based on products.

        Returns dict with cpp, roas, and other thresholds.
        """
        main_product = self.get_product_for_funnel(funnel_tag)

        if not main_product:
            return {
                'cpp': {'excellent': 12, 'good': 18, 'warning': 25, 'critical': 35},
                'roas': {'excellent': 3.0, 'good': 2.0, 'warning': 1.5, 'critical': 1.0}
            }

        return {
            'cpp': {
                'excellent': main_product.target_cpp * 0.7 if main_product.target_cpp else 12,
                'good': main_product.target_cpp if main_product.target_cpp else 18,
                'warning': main_product.breakeven_cpp * 0.8 if main_product.breakeven_cpp else 25,
                'critical': main_product.breakeven_cpp if main_product.breakeven_cpp else 35
            },
            'roas': {
                'excellent': main_product.target_roas * 1.5,
                'good': main_product.target_roas,
                'warning': main_product.target_roas * 0.75,
                'critical': 1.0
            },
            'product_price': main_product.price,
            'breakeven_cpp': main_product.breakeven_cpp,
            'target_cpp': main_product.target_cpp,
            'net_revenue': main_product.net_revenue_per_sale
        }
