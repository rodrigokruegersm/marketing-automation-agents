"""
Whop Adapter
Integration with Whop membership/payments platform
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime

from .base import (
    BaseCheckoutAdapter, Product, Offer, Sale, CheckoutMetrics,
    PaymentStatus, ProductType
)


class WhopAdapter(BaseCheckoutAdapter):
    """
    Adapter for Whop platform.

    Whop API Documentation: https://dev.whop.com/

    Usage:
        adapter = WhopAdapter(api_key="your_api_key", company_id="biz_xxx")
        products = adapter.get_products()
        sales = adapter.get_sales(start_date=datetime(2024, 1, 1))
    """

    platform_name = "whop"
    base_url = "https://api.whop.com/api/v5"  # Updated to v5 API

    def __init__(self, api_key: str, company_id: str = "", **kwargs):
        super().__init__(api_key, **kwargs)
        self.company_id = company_id

    def _request(self, endpoint: str, params: Optional[Dict] = None, method: str = "GET") -> Dict:
        """Make API request to Whop"""
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

            if response.status_code == 401:
                return {'error': 'Unauthorized - check API key permissions'}
            elif response.status_code == 404:
                return {'error': f'Endpoint not found: {endpoint}'}

            return response.json()
        except Exception as e:
            return {'error': str(e)}

    def test_connection(self) -> Dict:
        """Test API connection using v5 company products endpoint"""
        if not self.is_configured():
            return {'success': False, 'error': 'Not configured'}

        result = self._request('/company/products', {'per': 1})
        success = 'error' not in result and 'data' in result
        return {
            'success': success,
            'platform': self.platform_name,
            'total_products': result.get('pagination', {}).get('total_count', 0) if success else 0,
            'response': result if not success else 'Connected successfully'
        }

    def get_products(self, per_page: int = 100) -> List[Product]:
        """Fetch all products from Whop using v5 API"""
        all_products = []
        page = 1

        while True:
            result = self._request('/company/products', {'per': per_page, 'page': page})

            if 'error' in result:
                break

            data = result.get('data', [])
            if not data:
                break

            for item in data:
                all_products.append(self._parse_product(item))

            # Check pagination
            pagination = result.get('pagination', {})
            if page >= pagination.get('total_pages', 1):
                break
            page += 1

        return all_products

    def get_product(self, product_id: str) -> Optional[Product]:
        """Fetch a specific product"""
        # In v5, we need to search through products
        products = self.get_products()
        for product in products:
            if product.id == product_id:
                return product
        return None

    def _parse_product(self, data: Dict) -> Product:
        """Parse Whop product data (v5 format)"""
        return Product(
            id=str(data.get('id', '')),
            name=data.get('name', '') or data.get('title', '') or data.get('id', ''),
            platform=self.platform_name,
            price=0.0,  # Price comes from plans/payments
            currency='USD',
            type=ProductType.MEMBERSHIP,
            description=data.get('description', '') or '',
            platform_fee_percent=3.0,  # Whop fee varies
            raw_data=data
        )

    def get_offers(self, product_id: Optional[str] = None) -> List[Offer]:
        """Fetch checkout links as offers from Whop"""
        result = self._request('/checkout_links')

        if 'error' in result:
            return []

        offers = []
        for item in result.get('data', []):
            if product_id and item.get('plan') != product_id:
                continue
            offers.append(self._parse_offer(item))

        return offers

    def _parse_offer(self, data: Dict) -> Offer:
        """Parse Whop checkout link as offer"""
        return Offer(
            id=str(data.get('id', '')),
            name=data.get('name', ''),
            product_id=str(data.get('plan', '')),
            platform=self.platform_name,
            price=float(data.get('amount_override', 0)) / 100 if data.get('amount_override') else 0,
            checkout_url=data.get('direct_link', ''),
            raw_data=data
        )

    def get_sales(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        product_id: Optional[str] = None,
        status: Optional[PaymentStatus] = None,
        per_page: int = 100,
        max_pages: int = 10
    ) -> List[Sale]:
        """Fetch payments from Whop using v5 API"""
        all_sales = []
        page = 1

        while page <= max_pages:
            params = {'per': per_page, 'page': page}
            result = self._request('/company/payments', params)

            if 'error' in result:
                break

            data = result.get('data', [])
            if not data:
                break

            for item in data:
                sale = self._parse_sale(item)

                # Filter by date
                if start_date and sale.created_at and sale.created_at < start_date:
                    continue
                if end_date and sale.created_at and sale.created_at > end_date:
                    continue

                # Filter by product
                if product_id and sale.product_id != product_id:
                    continue

                # Filter by status
                if status and sale.status != status:
                    continue

                all_sales.append(sale)

            # Check pagination
            pagination = result.get('pagination', {})
            if page >= pagination.get('total_pages', 1):
                break
            page += 1

        return all_sales

    def _parse_sale(self, data: Dict) -> Sale:
        """Parse Whop payment data (v5 format)"""
        # Map Whop status - v5 uses 'paid', 'open', 'refunded', etc.
        status_str = data.get('status', '')
        if status_str == 'paid':
            payment_status = PaymentStatus.APPROVED
        elif status_str == 'refunded':
            payment_status = PaymentStatus.REFUNDED
        elif status_str in ['pending', 'open']:
            payment_status = PaymentStatus.PENDING
        else:
            payment_status = PaymentStatus.CANCELLED

        # v5 API returns amounts directly (not in cents for some fields)
        amount = float(data.get('final_amount', 0) or 0)
        subtotal = float(data.get('subtotal', 0) or 0)

        # Use subtotal if final_amount is 0 (installment payments)
        if amount == 0 and subtotal > 0:
            amount = subtotal

        # Parse date - v5 uses Unix timestamp
        created_ts = data.get('created_at')
        created_at = None
        if created_ts:
            try:
                if isinstance(created_ts, (int, float)):
                    created_at = datetime.fromtimestamp(created_ts)
                else:
                    created_at = datetime.fromisoformat(str(created_ts).replace('Z', '+00:00'))
            except:
                pass

        # Extract UTM from membership metadata
        metadata = data.get('membership_metadata', {}) or {}

        return Sale(
            id=str(data.get('id', '')),
            platform=self.platform_name,
            product_id=str(data.get('product_id', '')),
            product_name='',  # Product name not in v5 payment response
            amount=amount,
            currency=data.get('currency', 'usd').upper(),
            status=payment_status,
            payment_method=data.get('payment_method_type', '') or data.get('wallet_type', ''),
            customer_email=data.get('user_email', ''),
            customer_name=data.get('user_username', ''),
            utm_source=metadata.get('utm_source', ''),
            utm_medium=metadata.get('utm_medium', ''),
            utm_campaign=metadata.get('utm_campaign', ''),
            created_at=created_at,
            platform_fee=amount * 0.03,
            net_amount=amount * 0.97,
            raw_data=data
        )

    def get_memberships(self) -> List[Dict]:
        """Fetch active memberships"""
        result = self._request('/memberships')

        if 'error' in result:
            return []

        return result.get('data', [])

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
