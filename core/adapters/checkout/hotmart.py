"""
Hotmart Adapter
Integration with Hotmart checkout platform
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime

from .base import (
    BaseCheckoutAdapter, Product, Offer, Sale, CheckoutMetrics,
    PaymentStatus, ProductType
)


class HotmartAdapter(BaseCheckoutAdapter):
    """
    Adapter for Hotmart platform.

    Hotmart API Documentation: https://developers.hotmart.com/

    Usage:
        adapter = HotmartAdapter(
            api_key="your_api_key",
            client_id="your_client_id",
            client_secret="your_client_secret"
        )
        products = adapter.get_products()
        sales = adapter.get_sales(start_date=datetime(2024, 1, 1))
    """

    platform_name = "hotmart"
    base_url = "https://developers.hotmart.com/payments/api/v1"

    def __init__(
        self,
        api_key: str,
        client_id: str = "",
        client_secret: str = "",
        **kwargs
    ):
        super().__init__(api_key, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None

    def _get_access_token(self) -> str:
        """Get OAuth access token"""
        if self._access_token:
            return self._access_token

        # TODO: Implement OAuth flow with Hotmart
        # For now, use API key directly
        return self.api_key

    def _request(self, endpoint: str, params: Optional[Dict] = None, method: str = "GET") -> Dict:
        """Make API request to Hotmart"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self._get_access_token()}',
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

        result = self._request('/sales/summary')
        return {
            'success': 'error' not in result,
            'platform': self.platform_name,
            'response': result
        }

    def get_products(self) -> List[Product]:
        """Fetch all products from Hotmart"""
        result = self._request('/products')

        if 'error' in result:
            return []

        products = []
        for item in result.get('items', []):
            products.append(self._parse_product(item))

        return products

    def get_product(self, product_id: str) -> Optional[Product]:
        """Fetch a specific product"""
        result = self._request(f'/products/{product_id}')

        if 'error' in result:
            return None

        return self._parse_product(result)

    def _parse_product(self, data: Dict) -> Product:
        """Parse Hotmart product data"""
        return Product(
            id=str(data.get('id', '')),
            name=data.get('name', ''),
            platform=self.platform_name,
            price=float(data.get('price', 0)),
            currency=data.get('currency', 'BRL'),
            type=ProductType.COURSE,  # Default for Hotmart
            description=data.get('description', ''),
            platform_fee_percent=9.9,  # Hotmart standard fee
            raw_data=data
        )

    def get_offers(self, product_id: Optional[str] = None) -> List[Offer]:
        """Fetch offers/checkout pages"""
        params = {}
        if product_id:
            params['product_id'] = product_id

        result = self._request('/offers', params)

        if 'error' in result:
            return []

        offers = []
        for item in result.get('items', []):
            offers.append(self._parse_offer(item))

        return offers

    def _parse_offer(self, data: Dict) -> Offer:
        """Parse Hotmart offer data"""
        return Offer(
            id=str(data.get('id', '')),
            name=data.get('name', ''),
            product_id=str(data.get('product_id', '')),
            platform=self.platform_name,
            price=float(data.get('price', 0)),
            original_price=float(data.get('original_price', 0)) or None,
            checkout_url=data.get('checkout_url', ''),
            is_bump=data.get('is_bump', False),
            is_upsell=data.get('is_upsell', False),
            raw_data=data
        )

    def get_sales(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        product_id: Optional[str] = None,
        status: Optional[PaymentStatus] = None
    ) -> List[Sale]:
        """Fetch sales/transactions from Hotmart"""
        params = {}

        if start_date:
            params['start_date'] = int(start_date.timestamp() * 1000)  # Hotmart uses milliseconds

        if end_date:
            params['end_date'] = int(end_date.timestamp() * 1000)

        if product_id:
            params['product_id'] = product_id

        if status:
            status_map = {
                PaymentStatus.APPROVED: 'APPROVED',
                PaymentStatus.PENDING: 'WAITING_PAYMENT',
                PaymentStatus.REFUNDED: 'REFUNDED',
                PaymentStatus.CHARGEBACK: 'CHARGEBACK',
                PaymentStatus.CANCELLED: 'CANCELLED'
            }
            params['transaction_status'] = status_map.get(status, 'APPROVED')

        result = self._request('/sales/history', params)

        if 'error' in result:
            return []

        sales = []
        for item in result.get('items', []):
            sales.append(self._parse_sale(item))

        return sales

    def _parse_sale(self, data: Dict) -> Sale:
        """Parse Hotmart sale data"""
        # Map Hotmart status to PaymentStatus
        status_map = {
            'APPROVED': PaymentStatus.APPROVED,
            'COMPLETE': PaymentStatus.APPROVED,
            'WAITING_PAYMENT': PaymentStatus.PENDING,
            'REFUNDED': PaymentStatus.REFUNDED,
            'CHARGEBACK': PaymentStatus.CHARGEBACK,
            'CANCELLED': PaymentStatus.CANCELLED,
            'EXPIRED': PaymentStatus.EXPIRED
        }

        hotmart_status = data.get('purchase', {}).get('status', 'APPROVED')
        payment_status = status_map.get(hotmart_status, PaymentStatus.PENDING)

        # Extract UTM from tracking
        tracking = data.get('purchase', {}).get('tracking', {})

        # Calculate net amount
        price = float(data.get('purchase', {}).get('price', {}).get('value', 0))
        commission = float(data.get('purchase', {}).get('commission', {}).get('value', 0))

        # Parse dates
        created_ts = data.get('purchase', {}).get('order_date')
        created_at = datetime.fromtimestamp(created_ts / 1000) if created_ts else None

        return Sale(
            id=str(data.get('purchase', {}).get('transaction', '')),
            platform=self.platform_name,
            product_id=str(data.get('product', {}).get('id', '')),
            product_name=data.get('product', {}).get('name', ''),
            amount=price,
            currency='BRL',
            status=payment_status,
            payment_method=data.get('purchase', {}).get('payment', {}).get('type', ''),
            customer_email=data.get('buyer', {}).get('email', ''),
            customer_name=data.get('buyer', {}).get('name', ''),
            utm_source=tracking.get('source', ''),
            utm_medium=tracking.get('medium', ''),
            utm_campaign=tracking.get('campaign', ''),
            utm_content=tracking.get('content', ''),
            created_at=created_at,
            platform_fee=price * 0.099,  # 9.9% Hotmart fee
            affiliate_commission=commission,
            net_amount=price - (price * 0.099) - commission,
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

            # Group by UTM source
            if sale.utm_source:
                if sale.utm_source not in metrics.by_utm_source:
                    metrics.by_utm_source[sale.utm_source] = {'sales': 0, 'revenue': 0}
                metrics.by_utm_source[sale.utm_source]['sales'] += 1
                metrics.by_utm_source[sale.utm_source]['revenue'] += sale.amount

            # Group by funnel tag
            if sale.funnel_tag:
                if sale.funnel_tag not in metrics.by_funnel:
                    metrics.by_funnel[sale.funnel_tag] = {'sales': 0, 'revenue': 0}
                metrics.by_funnel[sale.funnel_tag]['sales'] += 1
                metrics.by_funnel[sale.funnel_tag]['revenue'] += sale.amount

        metrics.calculate_derived()
        return metrics
