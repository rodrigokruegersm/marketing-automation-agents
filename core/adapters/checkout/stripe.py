"""
Stripe Adapter
Integration with Stripe payment platform
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime

from .base import (
    BaseCheckoutAdapter, Product, Offer, Sale, CheckoutMetrics,
    PaymentStatus, ProductType
)


class StripeAdapter(BaseCheckoutAdapter):
    """
    Adapter for Stripe platform.

    Stripe API Documentation: https://stripe.com/docs/api

    Usage:
        adapter = StripeAdapter(api_key="sk_live_xxx")
        products = adapter.get_products()
        sales = adapter.get_sales(start_date=datetime(2024, 1, 1))
    """

    platform_name = "stripe"
    base_url = "https://api.stripe.com/v1"

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)

    def _request(self, endpoint: str, params: Optional[Dict] = None, method: str = "GET") -> Dict:
        """Make API request to Stripe"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, auth=(self.api_key, ''), params=params)
            else:
                response = requests.post(url, auth=(self.api_key, ''), data=params)

            return response.json()
        except Exception as e:
            return {'error': str(e)}

    def test_connection(self) -> Dict:
        """Test API connection"""
        if not self.is_configured():
            return {'success': False, 'error': 'Not configured'}

        result = self._request('/balance')
        return {
            'success': 'error' not in result,
            'platform': self.platform_name,
            'response': result
        }

    def get_products(self) -> List[Product]:
        """Fetch all products from Stripe"""
        result = self._request('/products', {'active': 'true', 'limit': 100})

        if 'error' in result:
            return []

        products = []
        for item in result.get('data', []):
            # Get price for this product
            prices = self._request('/prices', {'product': item['id'], 'active': 'true'})
            default_price = prices.get('data', [{}])[0] if prices.get('data') else {}

            products.append(self._parse_product(item, default_price))

        return products

    def get_product(self, product_id: str) -> Optional[Product]:
        """Fetch a specific product"""
        result = self._request(f'/products/{product_id}')

        if 'error' in result:
            return None

        # Get price
        prices = self._request('/prices', {'product': product_id, 'active': 'true'})
        default_price = prices.get('data', [{}])[0] if prices.get('data') else {}

        return self._parse_product(result, default_price)

    def _parse_product(self, data: Dict, price_data: Dict) -> Product:
        """Parse Stripe product data"""
        # Get price in main currency
        price = float(price_data.get('unit_amount', 0)) / 100
        currency = price_data.get('currency', 'usd').upper()

        return Product(
            id=str(data.get('id', '')),
            name=data.get('name', ''),
            platform=self.platform_name,
            price=price,
            currency=currency,
            type=ProductType.OTHER,
            description=data.get('description', ''),
            platform_fee_percent=2.9,  # Stripe standard (2.9% + $0.30)
            raw_data={**data, 'price_data': price_data}
        )

    def get_offers(self, product_id: Optional[str] = None) -> List[Offer]:
        """Fetch prices (offers) from Stripe"""
        params = {'active': 'true', 'limit': 100}
        if product_id:
            params['product'] = product_id

        result = self._request('/prices', params)

        if 'error' in result:
            return []

        offers = []
        for item in result.get('data', []):
            offers.append(self._parse_offer(item))

        return offers

    def _parse_offer(self, data: Dict) -> Offer:
        """Parse Stripe price as offer"""
        price = float(data.get('unit_amount', 0)) / 100

        return Offer(
            id=str(data.get('id', '')),
            name=data.get('nickname', '') or f"Price {data.get('id', '')[:8]}",
            product_id=str(data.get('product', '')),
            platform=self.platform_name,
            price=price,
            currency=data.get('currency', 'usd').upper(),
            raw_data=data
        )

    def get_sales(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        product_id: Optional[str] = None,
        status: Optional[PaymentStatus] = None
    ) -> List[Sale]:
        """Fetch charges/payments from Stripe"""
        params = {'limit': 100}

        if start_date:
            params['created[gte]'] = int(start_date.timestamp())

        if end_date:
            params['created[lte]'] = int(end_date.timestamp())

        result = self._request('/charges', params)

        if 'error' in result:
            return []

        sales = []
        for item in result.get('data', []):
            sale = self._parse_sale(item)

            # Filter by status if specified
            if status and sale.status != status:
                continue

            sales.append(sale)

        return sales

    def _parse_sale(self, data: Dict) -> Sale:
        """Parse Stripe charge data"""
        # Map Stripe status
        if data.get('refunded'):
            payment_status = PaymentStatus.REFUNDED
        elif data.get('status') == 'succeeded':
            payment_status = PaymentStatus.APPROVED
        elif data.get('status') == 'pending':
            payment_status = PaymentStatus.PENDING
        else:
            payment_status = PaymentStatus.CANCELLED

        amount = float(data.get('amount', 0)) / 100
        currency = data.get('currency', 'usd').upper()

        # Extract metadata for UTM
        metadata = data.get('metadata', {})

        # Stripe fee calculation (2.9% + $0.30 for US cards)
        stripe_fee = (amount * 0.029) + 0.30

        created_at = datetime.fromtimestamp(data.get('created', 0))

        return Sale(
            id=str(data.get('id', '')),
            platform=self.platform_name,
            product_id=metadata.get('product_id', ''),
            product_name=data.get('description', ''),
            amount=amount,
            currency=currency,
            status=payment_status,
            payment_method=data.get('payment_method_details', {}).get('type', ''),
            customer_email=data.get('billing_details', {}).get('email', ''),
            customer_name=data.get('billing_details', {}).get('name', ''),
            utm_source=metadata.get('utm_source', ''),
            utm_medium=metadata.get('utm_medium', ''),
            utm_campaign=metadata.get('utm_campaign', ''),
            created_at=created_at,
            platform_fee=stripe_fee,
            net_amount=amount - stripe_fee,
            raw_data=data
        )

    def get_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> CheckoutMetrics:
        """Get aggregated checkout metrics"""
        sales = self.get_sales(start_date, end_date)

        metrics = CheckoutMetrics(
            platform=self.platform_name,
            period_start=start_date,
            period_end=end_date
        )

        for sale in sales:
            metrics.total_sales += 1

            if sale.status == PaymentStatus.APPROVED:
                metrics.approved_sales += 1
                metrics.gross_revenue += sale.amount
                metrics.net_revenue += sale.net_amount
            elif sale.status == PaymentStatus.REFUNDED:
                metrics.refunded_sales += 1
                metrics.refunded_amount += sale.amount
            elif sale.status == PaymentStatus.CHARGEBACK:
                metrics.chargeback_sales += 1

            # Group by product
            if sale.product_id:
                if sale.product_id not in metrics.products:
                    metrics.products[sale.product_id] = {
                        'name': sale.product_name,
                        'sales': 0,
                        'revenue': 0
                    }
                metrics.products[sale.product_id]['sales'] += 1
                metrics.products[sale.product_id]['revenue'] += sale.amount

            # Group by UTM
            if sale.utm_source:
                if sale.utm_source not in metrics.by_utm_source:
                    metrics.by_utm_source[sale.utm_source] = {'sales': 0, 'revenue': 0}
                metrics.by_utm_source[sale.utm_source]['sales'] += 1
                metrics.by_utm_source[sale.utm_source]['revenue'] += sale.amount

        metrics.calculate_derived()
        return metrics
