"""
Kiwify Adapter
Integration with Kiwify checkout platform
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime

from .base import (
    BaseCheckoutAdapter, Product, Offer, Sale, CheckoutMetrics,
    PaymentStatus, ProductType
)


class KiwifyAdapter(BaseCheckoutAdapter):
    """
    Adapter for Kiwify platform.

    Kiwify API Documentation: https://api.kiwify.com.br/docs

    Usage:
        adapter = KiwifyAdapter(api_key="your_api_key")
        products = adapter.get_products()
        sales = adapter.get_sales(start_date=datetime(2024, 1, 1))
    """

    platform_name = "kiwify"
    base_url = "https://api.kiwify.com.br/v1"

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)

    def _request(self, endpoint: str, params: Optional[Dict] = None, method: str = "GET") -> Dict:
        """Make API request to Kiwify"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            else:
                response = requests.post(url, headers=headers, json=params)

            return response.json()
        except Exception as e:
            return {'error': str(e)}

    def test_connection(self) -> Dict:
        """Test API connection"""
        if not self.is_configured():
            return {'success': False, 'error': 'Not configured'}

        result = self._request('/account')
        return {
            'success': 'error' not in result,
            'platform': self.platform_name,
            'response': result
        }

    def get_products(self) -> List[Product]:
        """Fetch all products from Kiwify"""
        result = self._request('/products')

        if 'error' in result:
            return []

        products = []
        for item in result.get('data', []):
            products.append(self._parse_product(item))

        return products

    def get_product(self, product_id: str) -> Optional[Product]:
        """Fetch a specific product"""
        result = self._request(f'/products/{product_id}')

        if 'error' in result:
            return None

        return self._parse_product(result.get('data', {}))

    def _parse_product(self, data: Dict) -> Product:
        """Parse Kiwify product data"""
        return Product(
            id=str(data.get('id', '')),
            name=data.get('name', ''),
            platform=self.platform_name,
            price=float(data.get('price', 0)) / 100,  # Kiwify uses cents
            currency='BRL',
            type=ProductType.COURSE,
            description=data.get('description', ''),
            platform_fee_percent=8.99,  # Kiwify standard fee
            raw_data=data
        )

    def get_offers(self, product_id: Optional[str] = None) -> List[Offer]:
        """Fetch offers from Kiwify"""
        endpoint = '/offers'
        if product_id:
            endpoint = f'/products/{product_id}/offers'

        result = self._request(endpoint)

        if 'error' in result:
            return []

        offers = []
        for item in result.get('data', []):
            offers.append(self._parse_offer(item))

        return offers

    def _parse_offer(self, data: Dict) -> Offer:
        """Parse Kiwify offer data"""
        return Offer(
            id=str(data.get('id', '')),
            name=data.get('name', ''),
            product_id=str(data.get('product_id', '')),
            platform=self.platform_name,
            price=float(data.get('price', 0)) / 100,
            original_price=float(data.get('original_price', 0)) / 100 or None,
            checkout_url=data.get('checkout_url', ''),
            is_bump=data.get('type') == 'bump',
            is_upsell=data.get('type') == 'upsell',
            raw_data=data
        )

    def get_sales(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        product_id: Optional[str] = None,
        status: Optional[PaymentStatus] = None
    ) -> List[Sale]:
        """Fetch sales from Kiwify"""
        params = {}

        if start_date:
            params['start_date'] = start_date.strftime('%Y-%m-%d')

        if end_date:
            params['end_date'] = end_date.strftime('%Y-%m-%d')

        if product_id:
            params['product_id'] = product_id

        if status:
            status_map = {
                PaymentStatus.APPROVED: 'paid',
                PaymentStatus.PENDING: 'waiting_payment',
                PaymentStatus.REFUNDED: 'refunded',
                PaymentStatus.CHARGEBACK: 'chargedback',
                PaymentStatus.CANCELLED: 'cancelled'
            }
            params['status'] = status_map.get(status, 'paid')

        result = self._request('/orders', params)

        if 'error' in result:
            return []

        sales = []
        for item in result.get('data', []):
            sales.append(self._parse_sale(item))

        return sales

    def _parse_sale(self, data: Dict) -> Sale:
        """Parse Kiwify sale data"""
        status_map = {
            'paid': PaymentStatus.APPROVED,
            'waiting_payment': PaymentStatus.PENDING,
            'refunded': PaymentStatus.REFUNDED,
            'chargedback': PaymentStatus.CHARGEBACK,
            'cancelled': PaymentStatus.CANCELLED,
            'expired': PaymentStatus.EXPIRED
        }

        kiwify_status = data.get('status', 'paid')
        payment_status = status_map.get(kiwify_status, PaymentStatus.PENDING)

        # Extract UTM
        tracking = data.get('tracking', {})

        # Amount in cents
        amount = float(data.get('amount', 0)) / 100

        # Parse date
        created_str = data.get('created_at', '')
        created_at = datetime.fromisoformat(created_str.replace('Z', '+00:00')) if created_str else None

        return Sale(
            id=str(data.get('id', '')),
            platform=self.platform_name,
            product_id=str(data.get('product', {}).get('id', '')),
            product_name=data.get('product', {}).get('name', ''),
            amount=amount,
            currency='BRL',
            status=payment_status,
            payment_method=data.get('payment_method', ''),
            customer_email=data.get('customer', {}).get('email', ''),
            customer_name=data.get('customer', {}).get('name', ''),
            utm_source=tracking.get('utm_source', ''),
            utm_medium=tracking.get('utm_medium', ''),
            utm_campaign=tracking.get('utm_campaign', ''),
            utm_content=tracking.get('utm_content', ''),
            created_at=created_at,
            platform_fee=amount * 0.0899,
            net_amount=amount * 0.9101,
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
